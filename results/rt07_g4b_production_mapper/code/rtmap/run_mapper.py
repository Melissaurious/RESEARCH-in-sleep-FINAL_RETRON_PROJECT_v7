#!/usr/bin/env python3
"""Production runner for the frozen RT state->residue mapper.

    run_mapper.py --in <fasta> --out <dir> --shard <name> [--work <dir>]
                  [--metadata <tsv>] [--batch-size N] [--force]

The SCIENCE is the frozen mapper, imported byte-identically and called exactly as the UG25
confirmatory gate called it:

    state_to_residue(HMM, seqs, work, tag, pp_hi=PP_HI, pp_lo=PP_LO)
    domain_scores(HMM, faa, work, tag)
    classify_sequence(states, ANCHORS, LENG, S_MIN, K_MIN, dom)

Everything else in this file is engineering: input validation, deduplication, batching,
deterministic ordering, atomic writes, resume, failure logging and provenance. No threshold,
no rule and no criterion is introduced. `scripts/test_production_freeze.py` proves the
per-state calls are identical to the frozen bundle's own mapper on the same input.

Determinism guarantees:

  * work is ordered by (rt_hash, sequence_id) - input file order is irrelevant;
  * batch boundaries are a function of that order and --batch-size only;
  * per-sequence calls are independent of batch composition (hmmalign scores each sequence
    against the profile separately); the smoke test asserts this against two batch sizes;
  * output rows are emitted in the same total order, so a rerun is byte-identical.

Failure isolation: a batch that raises is retried one sequence at a time, so one bad record
costs one TOOL_FAILURE row rather than a whole batch of them.
"""
import argparse
import collections
import datetime
import hashlib
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from rtmap import params as P
from rtmap import schema as S
from rtmap import version as V
from rtmap.mapper import state_to_residue, domain_scores, classify_sequence, hmm_leng

DYAD = re.compile(P.DYAD_PATTERN)

# Inherited eligibility rule - NOT invented here. These are the values the registered loader
# (FINAL_PRE_UG25_VALIDATION_BUNDLE/code/loader.py) applied to every sequence the instrument
# was ever calibrated or validated on. A record failing them is outside the population the
# instrument has been exercised on, so it is logged as INPUT_INVALID rather than mapped.
MIN_AA = 250
NON_STANDARD = re.compile(r"[^ACDEFGHIKLMNPQRSTVWY]")

DEFAULT_BATCH_SIZE = 500


def clean(x):
    """The registered loader's cleaning, verbatim."""
    return x.replace("-", "").replace(".", "").upper().rstrip("*").replace("*", "")


def rt_hash(seq):
    return hashlib.sha256(seq.encode()).hexdigest()


def read_fasta(path):
    """Yield (sequence_id, raw_residues). Malformed records are yielded with None so the
    caller can log them rather than dropping them silently."""
    hdr, buf = None, []
    with open(path, errors="replace") as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.startswith(">"):
                if hdr is not None:
                    yield hdr, "".join(buf)
                parts = ln[1:].split()
                hdr = parts[0] if parts else None
                buf = []
            elif hdr is not None:
                buf.append(ln.strip())
            elif ln.strip():
                yield None, ln.strip()
    if hdr is not None:
        yield hdr, "".join(buf)


def load_metadata(path):
    """Optional Stage-1 stratum labels: TSV with a `sequence_id` column and a
    `family_metadata` column. METADATA, NOT TRUTH - see docs/STAGE1_METADATA_ROLE.md."""
    if not path:
        return {}
    out = {}
    with open(path) as f:
        cols = f.readline().rstrip("\n").split("\t")
        if "sequence_id" not in cols or "family_metadata" not in cols:
            raise SystemExit("FAIL CLOSED: --metadata needs `sequence_id` and "
                             "`family_metadata` columns")
        i, j = cols.index("sequence_id"), cols.index("family_metadata")
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) > max(i, j):
                out[p[i]] = p[j]
    return out


def validate(records, reject_ids=frozenset()):
    """Split input into (mappable, invalid). Deterministic and ORDER-INDEPENDENT.

    `records` is the raw [(sequence_id, residues)] stream.

    Duplicate-identifier policy, repaired after the independent packaging review found the
    first version order-dependent:

      * an identifier carrying **different** sequences is a CONFLICT. **Every** occurrence
        is rejected - none is retained. Keeping "the first" made the retained science a
        function of input order, which a production instrument may not be.
      * an identifier repeated with the **same** sequence is a harmless restatement. One
        copy is kept (they are identical, so which one is not a choice) and each extra
        occurrence is logged.
      * `reject_ids` is the globally censused conflict set, supplied from outside. Shard-
        local detection cannot see a conflict whose two records landed in different shards,
        so g5's eligibility census computes the set once over the whole catalogue and every
        shard is given it. See docs/G5_EXECUTION_PLAN.md section 4.

    Identical SEQUENCES under different identifiers are NOT an error - they share an
    rt_hash and are mapped once.
    """
    # Pass 1: group by identifier, in input order, without deciding anything.
    by_id, invalid = collections.OrderedDict(), []
    for sid, raw in records:
        if sid is None:
            invalid.append(("", 0, "UNPARSEABLE_RECORD",
                            "residue line outside any FASTA record"))
            continue
        by_id.setdefault(sid, []).append(clean(raw))

    # Pass 2: decide per identifier. Every branch is a function of the identifier's own
    # records as a SET, so re-ordering the input cannot change any outcome.
    good = {}
    for sid, seqs in by_id.items():
        distinct = sorted(set(seqs))
        if sid in reject_ids:
            for s in seqs:
                invalid.append((sid, len(s), "DUPLICATE_SEQUENCE_ID_CONFLICT",
                                "identifier conflicts across the catalogue "
                                "(global census)"))
            continue
        if len(distinct) > 1:
            for s in seqs:
                invalid.append((sid, len(s), "DUPLICATE_SEQUENCE_ID_CONFLICT",
                                f"identifier carries {len(distinct)} different sequences; "
                                f"all occurrences rejected"))
            continue
        seq = distinct[0]
        for _ in seqs[1:]:
            invalid.append((sid, len(seq), "DUPLICATE_SEQUENCE_ID",
                            "identifier repeated with an identical sequence"))
        if not seq:
            invalid.append((sid, 0, "EMPTY_SEQUENCE", "no residues"))
        elif len(seq) < MIN_AA:
            invalid.append((sid, len(seq), "BELOW_MIN_LENGTH",
                            f"{len(seq)} aa < registered minimum {MIN_AA}"))
        elif NON_STANDARD.search(seq):
            bad = sorted(set(NON_STANDARD.findall(seq)))
            invalid.append((sid, len(seq), "NON_STANDARD_RESIDUE",
                            f"non-standard residue(s): {''.join(bad)}"))
        else:
            good[sid] = seq
    return good, invalid


def read_reject_ids(path):
    """Identifiers the global duplicate census rejected. One per line; '#' comments."""
    if not path:
        return frozenset()
    out = set()
    for ln in open(path):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.add(ln.split("\t")[0])
    return frozenset(out)


def map_batch(seqs, work, tag):
    """One frozen mapping call over a batch, plus PER-SEQUENCE domain scoring.

    ALIGNMENT is batched. `hmmalign` scores each sequence against the profile
    independently, so the match-column residues and their posteriors do not depend on which
    other sequences share the call. This is asserted empirically by smoke check S2/S4:
    batch size 1 and batch size 500 give byte-identical states.tsv.

    DOMAIN SCORING IS NOT BATCHED, and this is a deliberate production repair.

    `hmmsearch` computes E-values against the size of the database it was handed, and its
    default reporting threshold is an E-value. So in a batched call:

      * the reported E-value of a sequence is a function of how many OTHER sequences were
        in its shard; and, worse,
      * whether a marginal domain is REPORTED AT ALL moves with the shard size. Measured on
        560 construction sequences: `YP_217686.1_Retrons` is reported with bitscore -0.6
        at shard size 100 and is absent at shard size 1000.

    `classify_sequence` treats "no domain reported" and "bitscore < S_MIN" identically, so
    that particular sequence's verdict does not move. But the hazard generalises the wrong
    way: at Stage-1 shard sizes a sequence whose bitscore is at or just above S_MIN = 10
    could fall below the E-value reporting threshold purely because its shard was large,
    and ABSTAIN where a smaller shard would have returned MAPPED. A verdict must not be a
    function of shard geometry.

    Scoring one sequence at a time makes the database size 1 for every call, so the
    bitscore and the E-value are properties of the sequence alone. It is also strictly more
    inclusive: no sequence loses a reported domain because of its neighbours.

    This changes NO frozen code, NO threshold and NO rule - `domain_scores` is the frozen
    function, called with a one-sequence FASTA. Bit scores are database-size independent;
    measured over 120 construction sequences, per-sequence and batched scoring agree on
    every reported bitscore to the printed precision (0 differences).

    Cost, measured: 11.9 ms/sequence against 2.2 ms/sequence batched. See
    `docs/G5_EXECUTION_PLAN.md` - it is not the binding cost.

    Returns (states, insertions, leng, domains).
    """
    m, ins, leng = state_to_residue(P.PROFILE_HMM, seqs, work, tag,
                                    pp_hi=P.PP_HI, pp_lo=P.PP_LO)
    dom = {}
    for i, sid in enumerate(sorted(seqs)):
        fa = f"{work}/{tag}_d{i:05d}.faa"
        with open(fa, "w") as f:
            f.write(f">{sid}\n{seqs[sid]}\n")
        dom.update(domain_scores(P.PROFILE_HMM, fa, work, f"{tag}_d{i:05d}"))
    return m, ins, leng, dom


def state_reason(call, posterior):
    if call == "DELETED_STATE":
        return "MATCH_COLUMN_GAPPED"
    if posterior is None:
        return "POSTERIOR_UNAVAILABLE"
    if call == "MAPPED":
        return "OK_POSTERIOR_AT_OR_ABOVE_PP_HI"
    if call == "AMBIGUOUS":
        return "POSTERIOR_BETWEEN_PP_LO_AND_PP_HI"
    return "POSTERIOR_BELOW_PP_LO"


def inspectability(verdict, reason, frac):
    """Production status: a RELABELLING of the frozen (verdict, reason) pair, split by the
    frozen T1. It introduces no predicate of its own.

    An earlier version used an invented comparison, `n_ambiguous + n_unsupported >
    n_mapped`, to pick out AMBIGUOUS_MAPPING. The independent packaging review correctly
    identified that as a new classification rule - and one that could fire with zero
    AMBIGUOUS calls. It was removed rather than defended. See
    schema.STATUS_FROM_FROZEN_REASON, which the freeze tests check this function against.
    """
    if verdict != "ABSTAIN":
        return "MAPPABLE" if frac >= P.T1 else "PARTIAL_MAPPING"
    status = S.STATUS_FROM_FROZEN_REASON.get((verdict, reason))
    if status is None:
        raise SystemExit(f"FAIL CLOSED: unmapped frozen verdict/reason pair "
                         f"({verdict!r}, {reason!r}) - the relabelling must stay a "
                         f"bijection onto the frozen reason codes")
    return status


def build_rows(sid, seq, st, ins_runs, leng, dom, mapper_version, family_meta):
    anchors = [a for a in P.ANCHORS if a <= leng]
    state_rows = []
    for ai, a in enumerate(anchors, start=1):
        c = st[a]
        post = c["posterior"]
        state_rows.append({
            "rt_hash": rt_hash(seq),
            "sequence_id": sid,
            "mapper_version": mapper_version,
            "state_id": a,
            "anchor_index": ai,
            "call_state": c["call"],
            "sequence_residue_index": c["residue_index"],
            "amino_acid": c["aa"],
            "posterior": "" if post is None else f"{post:.2f}",
            "support": f"{(post if post is not None else 0.0):.2f}",
            "reason_code": state_reason(c["call"], post),
        })

    n = collections.Counter(r["call_state"] for r in state_rows)
    n_map, n_amb = n["MAPPED"], n["AMBIGUOUS"]
    n_uns, n_del = n["UNSUPPORTED"], n["DELETED_STATE"]
    verdict, reason, *_ = classify_sequence(st, P.ANCHORS, leng, P.S_MIN, P.K_MIN, dom)
    frac = n_map / len(anchors)

    cs = st[P.CAT_STATE]
    if cs["call"] == "DELETED_STATE":
        cls = "CATALYTIC_STATE_DELETED"
    elif cs["call"] == "AMBIGUOUS":
        cls = "CATALYTIC_AMBIGUOUS"
    elif cs["call"] == "UNSUPPORTED":
        cls = "CATALYTIC_UNSUPPORTED"
    else:
        ri = cs["residue_index"]
        cls = ("CATALYTIC_CONFIRMED"
               if ri and DYAD.match(seq[ri - 1:ri + 3]) else "CATALYTIC_SUBSTITUTED")
    ri = cs["residue_index"]
    cat_post = cs["posterior"]

    seq_row = {
        "rt_hash": rt_hash(seq),
        "sequence_id": sid,
        "sequence_length": len(seq),
        "mapper_version": mapper_version,
        "profile_version": P.PROFILE_SHA256[:16],
        "match_state_definition": P.MATCH_STATE_DEFINITION,
        "family_metadata": family_meta or "NOT_SUPPLIED",
        "n_states_total": len(anchors),
        "n_mapped": n_map,
        "n_ambiguous": n_amb,
        "n_unsupported": n_uns,
        "n_deleted": n_del,
        "mapped_fraction": f"{frac:.4f}",
        "verdict": verdict,
        "reason": reason,
        "domain_bitscore": "" if dom is None else f"{dom[0]:.1f}",
        "domain_evalue": "" if dom is None else f"{dom[1]:.3g}",
        "inspectability_status": inspectability(verdict, reason, frac),
        "cat_state": P.CAT_STATE,
        "cat_call_state": cs["call"],
        "cat_residue_index": ri,
        "cat_residue": cs["aa"],
        "cat_motif_class": cls,
        "cat_support": f"{(cat_post if cat_post is not None else 0.0):.2f}",
        "cat_motif_window": seq[ri - 1:ri + 3] if ri else "",
        "n_dyad_motifs_in_sequence": len(DYAD.findall(seq)),
        "n_insertion_runs": len(ins_runs),
        "total_inserted_residues": sum(l for _, l in ins_runs),
        "max_insertion_run": max((l for _, l in ins_runs), default=0),
    }
    return state_rows, seq_row


DONE_HEADER = "# rtmap shard completion sidecar"

def bundle_root_now():
    """The observed manifest root of this bundle, computed the same way freeze.py does."""
    import hashlib as _h
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from freeze import scan, sha256_file
    regular, symlinks, irregular, _ = scan(V.BUNDLE_DIR)
    if symlinks or irregular:
        raise SystemExit(f"FAIL CLOSED: bundle contains symlink(s)/non-regular file(s): "
                         f"{symlinks + irregular}")
    rows = sorted((rel, sha256_file(p), os.path.getsize(p)) for rel, p in regular)
    body = "".join(f"{h}  {n}  {rel}\n" for rel, h, n in rows)
    return _h.sha256(body.encode()).hexdigest()


def verify_bundle_root(pinned):
    """Verify the whole production bundle against an EXTERNAL pinned root.

    The instrument digest binds `code/` and `control/`, which is what can change behaviour.
    This is the complementary binding the independent packaging review asked for: it ties a
    production record to THIS bundle on disk, tables and documentation included.

    `pinned` is a 64-hex root, or `@<path>` to read one from a file outside the bundle - a
    bundle cannot authenticate itself. Not supplied, the run proceeds and records
    `UNVERIFIED_NOT_REQUESTED`, which is honest rather than silent; **g5 requires it**
    (docs/G5_EXECUTION_PLAN.md section 1).

    Returns (root_value, status). A mismatch is fatal: a production record is never emitted
    by a bundle that failed its own freeze.
    """
    if not pinned:
        return "NONE", "UNVERIFIED_NOT_REQUESTED"
    if pinned.startswith("@"):
        pinned = open(pinned[1:]).read().strip()
    pinned = pinned.strip().lower()
    if len(pinned) != 64 or any(c not in "0123456789abcdef" for c in pinned) \
            or set(pinned) == {"0"}:
        raise SystemExit(f"FAIL CLOSED: --pinned-root malformed or all-zero: {pinned!r}")
    observed = bundle_root_now()
    if observed != pinned:
        raise SystemExit(
            f"FAIL CLOSED: production bundle does not match its external pinned root.\n"
            f"  pinned   {pinned}\n  observed {observed}\n"
            f"  Refusing to emit production records from an unverified instrument.")
    return observed, "VERIFIED"


def done_is_valid(done, out_dir, shard, input_sha, instrument_sha):
    """A shard is complete only if its DONE sidecar VERIFIES. Repaired after the independent
    packaging review showed an empty `probe.DONE` was enough to skip a shard with no
    outputs at all.

    Every one of these must hold, or the shard is redone:
      * the sidecar parses and declares an input sha256 and an instrument digest;
      * both match THIS run - so a changed input or a changed instrument forces a redo
        rather than silently inheriting a stale result;
      * every output file it names exists and still hashes to the recorded value.

    Returns (ok, reason).
    """
    try:
        rows, meta = {}, {}
        for ln in open(done):
            ln = ln.rstrip("\n")
            if ln.startswith("# ") and "=" in ln:
                k, v = ln[2:].split("=", 1)
                meta[k] = v
            elif ln.startswith("#") or not ln:
                continue
            else:
                h, name = ln.split("  ", 1)
                rows[name] = h
    except Exception as e:
        return False, f"sidecar unparseable ({e})"
    if not rows:
        return False, "sidecar names no output files"
    if meta.get("input_sha256") != input_sha:
        return False, (f"input changed (sidecar {str(meta.get('input_sha256'))[:16]} != "
                       f"{input_sha[:16]})")
    if meta.get("instrument_sha256") != instrument_sha:
        return False, (f"instrument changed (sidecar "
                       f"{str(meta.get('instrument_sha256'))[:16]} != "
                       f"{instrument_sha[:16]})")
    expected = {f"{shard}.{n}.tsv" for n in ("states", "sequences", "failures",
                                             "provenance")}
    if set(rows) != expected:
        return False, f"sidecar lists {sorted(rows)}, expected {sorted(expected)}"
    for name, want in sorted(rows.items()):
        p = os.path.join(out_dir, name)
        if not os.path.isfile(p):
            return False, f"output missing: {name}"
        if P.sha256_file(p) != want:
            return False, f"output changed since it was written: {name}"
    return True, "verified"


def run_shard(args):
    comps = V.check_instrument()
    mv = V.mapper_version(comps)
    instrument_sha = V.instrument_digest(comps)
    bundle_root, bundle_root_status = verify_bundle_root(args.pinned_root)
    input_sha = P.sha256_file(args.input)

    os.makedirs(args.out, exist_ok=True)
    done = os.path.join(args.out, f"{args.shard}.DONE")
    if os.path.exists(done) and not args.force:
        ok, why = done_is_valid(done, args.out, args.shard, input_sha, instrument_sha)
        if ok:
            print(f"SKIP {args.shard}: already complete and verified ({done}).")
            return 0
        print(f"REDO {args.shard}: DONE present but NOT valid - {why}", file=sys.stderr)

    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = list(read_fasta(args.input))
    good, invalid = validate(records, read_reject_ids(args.reject_ids))
    meta = load_metadata(args.metadata)

    # deduplicate by exact residue string; every identifier still gets its own output row.
    by_hash = collections.defaultdict(list)
    for sid, seq in good.items():
        by_hash[rt_hash(seq)].append(sid)
    order = sorted(by_hash)                       # deterministic: sorted rt_hash
    n_dup_ids = sum(len(v) - 1 for v in by_hash.values())

    work = args.work or tempfile.mkdtemp(prefix=f"rtmap_{args.shard}_")
    os.makedirs(work, exist_ok=True)
    owns_work = args.work is None

    state_rows, seq_rows, fail_rows = [], [], []
    for sid, ln, code, detail in invalid:
        fail_rows.append({"rt_hash": "", "sequence_id": sid, "sequence_length": ln,
                          "mapper_version": mv, "inspectability_status": "INPUT_INVALID",
                          "reason_code": code, "detail": detail})

    n_batches = 0
    try:
        for start in range(0, len(order), args.batch_size):
            chunk = order[start:start + args.batch_size]
            n_batches += 1
            tag = f"{args.shard}_b{n_batches:05d}"
            # representative id per hash: the lexicographically first, for a stable FASTA
            reps = {min(by_hash[h]): good[min(by_hash[h])] for h in chunk}
            try:
                m, ins, leng, dom = map_batch(reps, work, tag)
            except Exception:
                # isolate: one failing record must not fail its neighbours
                print(f"  batch {tag} failed; retrying {len(reps)} sequences singly",
                      file=sys.stderr)
                m, ins, dom, leng = {}, {}, {}, hmm_leng(P.PROFILE_HMM)
                for i, (rid, rseq) in enumerate(sorted(reps.items())):
                    try:
                        mm, ii, leng, dd = map_batch({rid: rseq}, work, f"{tag}_s{i:05d}")
                        m.update(mm)
                        ins.update(ii)
                        dom.update(dd)
                    except Exception:
                        detail = traceback.format_exc(limit=1).strip().replace("\n", " | ")
                        # EVERY identifier sharing this sequence gets a failure row, not
                        # just the representative. The independent packaging review found
                        # an alias receiving neither a scientific row nor a failure row;
                        # the reconciliation assertion below now makes that impossible.
                        for sid in sorted(by_hash[rt_hash(rseq)]):
                            fail_rows.append({
                                "rt_hash": rt_hash(rseq), "sequence_id": sid,
                                "sequence_length": len(rseq), "mapper_version": mv,
                                "inspectability_status": "TOOL_FAILURE",
                                "reason_code": "MAPPER_RAISED", "detail": detail})
            for h in chunk:
                rep = min(by_hash[h])
                if rep not in m:
                    continue    # already accounted for as TOOL_FAILURE, for every alias
                for sid in sorted(by_hash[h]):
                    sr, qr = build_rows(sid, good[sid], m[rep], ins.get(rep, []), leng,
                                        dom.get(rep), mv, meta.get(sid))
                    state_rows += sr
                    seq_rows.append(qr)
    finally:
        if owns_work:
            shutil.rmtree(work, ignore_errors=True)

    # ---- RECONCILIATION: every valid input identifier has exactly one outcome ----------
    # Repaired after the independent packaging review found an alias of a failed sequence
    # receiving neither a scientific row nor a failure row. A production run that cannot
    # account for one of its inputs fails closed rather than shipping a silent gap.
    accounted = collections.Counter(r["sequence_id"] for r in seq_rows)
    accounted.update(r["sequence_id"] for r in fail_rows
                     if r["inspectability_status"] == "TOOL_FAILURE")
    missing = sorted(set(good) - set(accounted))
    doubled = sorted(k for k in good if accounted[k] > 1)
    if missing or doubled:
        raise SystemExit(
            f"FAIL CLOSED: shard {args.shard} does not reconcile. "
            f"{len(missing)} valid input(s) produced no row: {missing[:5]}; "
            f"{len(doubled)} produced more than one: {doubled[:5]}. "
            f"Every valid input identifier must appear exactly once across "
            f"sequences.tsv and the TOOL_FAILURE rows of failures.tsv.")

    key = lambda r: (r["rt_hash"], r["sequence_id"])
    seq_rows.sort(key=key)
    state_rows.sort(key=lambda r: (r["rt_hash"], r["sequence_id"], r["anchor_index"]))
    fail_rows.sort(key=lambda r: (r["reason_code"], r["sequence_id"]))

    finished = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    written = {}
    for name, cols, rows in (("states", S.STATES_COLUMNS, state_rows),
                             ("sequences", S.SEQUENCES_COLUMNS, seq_rows),
                             ("failures", S.FAILURES_COLUMNS, fail_rows)):
        path = os.path.join(args.out, f"{args.shard}.{name}.tsv")
        tmp = path + ".part"
        with open(tmp, "w") as f:
            f.write(S.header(cols))
            for r in rows:
                f.write(S.row(cols, r))
        os.replace(tmp, path)                       # atomic: no half-written shard
        written[f"{args.shard}.{name}.tsv"] = P.sha256_file(path)

    prov = [
        ("schema_version", S.SCHEMA_VERSION),
        ("mapper_version", mv),
        ("instrument_sha256", instrument_sha),
        ("bundle_root_sha256", bundle_root),
        ("bundle_root_status", bundle_root_status),
        ("shard", args.shard),
        ("input_path", os.path.abspath(args.input)),
        ("input_sha256", input_sha),
        ("reject_ids_path", os.path.abspath(args.reject_ids) if args.reject_ids else "NONE"),
        ("reject_ids_sha256",
         P.sha256_file(args.reject_ids) if args.reject_ids else "NONE"),
        ("input_records_read", len(records)),
        ("input_valid", len(good)),
        ("input_invalid", len(invalid)),
        ("distinct_rt_hash", len(order)),
        ("duplicate_ids_collapsed", n_dup_ids),
        ("batch_size", args.batch_size),
        ("n_batches", n_batches),
        ("sequences_emitted", len(seq_rows)),
        ("state_rows_emitted", len(state_rows)),
        ("failures_emitted", len(fail_rows)),
        ("metadata_path", os.path.abspath(args.metadata) if args.metadata else "NONE"),
        ("metadata_sha256", P.sha256_file(args.metadata) if args.metadata else "NONE"),
        ("min_aa_eligibility", MIN_AA),
        ("eligibility_rule", V.ELIGIBILITY_RULE),
        ("domain_scoring_protocol", V.DOMAIN_SCORING_PROTOCOL),
        ("hmmer_version", V.hmmer_version()),
        ("python_version", sys.version.split()[0]),
        ("host", socket.gethostname()),
        ("started_utc", started),
        ("finished_utc", finished),
    ] + [(f"instrument.{k}", comps[k]) for k in sorted(comps)] \
      + [(f"output.{k}", v) for k, v in sorted(written.items())]

    ppath = os.path.join(args.out, f"{args.shard}.provenance.tsv")
    with open(ppath + ".part", "w") as f:
        f.write(S.header(S.PROVENANCE_COLUMNS))
        for k, v in prov:
            f.write(f"{k}\t{v}\n")
    os.replace(ppath + ".part", ppath)

    # The DONE sidecar carries what `done_is_valid` needs to decide, on a later run,
    # whether this shard may be skipped: the input identity, the instrument identity, and
    # the hash of every output. Presence alone is not completion.
    with open(done + ".part", "w") as f:
        f.write(DONE_HEADER + "\n")
        f.write(f"# shard={args.shard}\n")
        f.write(f"# input_sha256={input_sha}\n")
        f.write(f"# instrument_sha256={instrument_sha}\n")
        f.write(f"# mapper_version={mv}\n")
        f.write(f"# finished_utc={finished}\n")
        for k in sorted(written):
            f.write(f"{written[k]}  {k}\n")
        f.write(f"{P.sha256_file(ppath)}  {args.shard}.provenance.tsv\n")
    os.replace(done + ".part", done)

    print(f"{args.shard}: {len(seq_rows)} sequences, {len(state_rows)} state rows, "
          f"{len(fail_rows)} failures, {n_batches} batch(es) -> {args.out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="input", required=True, help="input FASTA shard")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--shard", required=True, help="shard name; output file prefix")
    ap.add_argument("--work", default=None, help="scratch dir (default: a temp dir)")
    ap.add_argument("--metadata", default=None,
                    help="optional TSV of Stage-1 strata (metadata, not truth)")
    ap.add_argument("--reject-ids", default=None,
                    help="identifiers rejected by the GLOBAL duplicate census; one per "
                         "line. Required in g5 - shard-local detection cannot see a "
                         "conflict split across shards")
    ap.add_argument("--pinned-root", default=None,
                    help="external pinned bundle root (64 hex, or @<path>). Verifies the "
                         "whole bundle before emitting any record. Required in g5")
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    ap.add_argument("--force", action="store_true", help="redo a shard marked DONE")
    args = ap.parse_args(argv)
    if args.batch_size < 1:
        raise SystemExit("FAIL CLOSED: --batch-size must be >= 1")
    return run_shard(args)


if __name__ == "__main__":
    sys.exit(main())
