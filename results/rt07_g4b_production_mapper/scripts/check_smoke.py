#!/usr/bin/env python3
"""Smoke-test assertions. ENGINEERING ONLY - no scientific claim is made or tested here.

    check_smoke.py <smoke_dir>

Seven checks. Every one is about packaging; none is about biology.

  S1  EQUIVALENCE TO THE FROZEN BUNDLE. The production run's per-sequence anchor counts,
      verdict, reason and catalytic class equal the values LANDED in
      FINAL_PRE_UG25_VALIDATION_BUNDLE/tables/construction_validation_sequence.tsv for the
      same identifiers. This is the load-bearing check: if packaging had altered any
      threshold, rule or call, these would move.

  S2  PER-STATE EQUIVALENCE TO A DIRECT FROZEN-MAPPER CALL. The production states.tsv is
      compared, state by state, against `state_to_residue` imported straight from the frozen
      bundle and called with the frozen thresholds. 150 states x every smoke sequence.

  S3  DETERMINISM. A second run with --force is byte-identical.

  S4  BATCH INVARIANCE. --batch-size 1 gives the same scientific columns as --batch-size 500,
      so shard and batch geometry in g5 cannot move a result.

  S5  CALL-STATE COMPLETENESS. All four per-state call states are reachable in the emitted
      data, and no fifth value appears. The states are not collapsed to present/absent.

  S6  FAILURE STATES. The three planted invalid records land in failures.tsv with the right
      reason codes, and the planted duplicate identifier is rejected exactly once.

  S7  DEDUPLICATION. The planted identical-sequence pair shares one rt_hash, is mapped once
      (provenance records the collapse) and still yields two sequence rows with identical
      calls.
"""
import collections
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G4B = os.path.dirname(HERE)
ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
BUNDLE = f"{ROOT}/results/FINAL_PRE_UG25_VALIDATION_BUNDLE"
EXPECTED = f"{BUNDLE}/tables/construction_validation_sequence.tsv"

sys.path.insert(0, f"{G4B}/code")
from rtmap import params as P          # noqa: E402
from rtmap import schema as S          # noqa: E402

FAILS = []


def check(ok, label, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)
    return ok


def read_tsv(path):
    with open(path) as f:
        cols = f.readline().rstrip("\n").split("\t")
        return [dict(zip(cols, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]


def main():
    smoke = sys.argv[1]
    seqs = read_tsv(f"{smoke}/main/smoke.sequences.tsv")
    states = read_tsv(f"{smoke}/main/smoke.states.tsv")
    fails = read_tsv(f"{smoke}/main/smoke.failures.tsv")
    prov = {r["key"]: r["value"] for r in read_tsv(f"{smoke}/main/smoke.provenance.tsv")}

    print("\n== S1  equivalence to the landed frozen construction results ==")
    landed = {r["sequence_id"]: r for r in read_tsv(EXPECTED)}
    compared = 0
    for r in seqs:
        e = landed.get(r["sequence_id"])
        if not e:
            continue
        compared += 1
        same = (r["n_mapped"] == e["n_mapped"] and r["n_ambiguous"] == e["n_ambiguous"]
                and r["n_unsupported"] == e["n_unsupported"]
                and r["n_deleted"] == e["n_deleted"]
                and r["verdict"] == e["verdict"] and r["reason"] == e["reason"]
                and r["cat_motif_class"] == e["catalytic_verdict"]
                and f"{100 * float(r['mapped_fraction']):.1f}" == e["pct_mapped"]
                and r["domain_bitscore"] == e["domain_bitscore"])
        if not same:
            check(False, f"S1 {r['sequence_id']}",
                  f"production {r['n_mapped']}/{r['n_ambiguous']}/{r['n_unsupported']}/"
                  f"{r['n_deleted']} {r['verdict']} {r['cat_motif_class']} vs landed "
                  f"{e['n_mapped']}/{e['n_ambiguous']}/{e['n_unsupported']}/{e['n_deleted']}"
                  f" {e['verdict']} {e['catalytic_verdict']}")
    check(compared > 0, "S1 at least one sequence compared against landed values",
          f"{compared} compared")
    check(not [f for f in FAILS if f.startswith("S1 ")],
          f"S1 all {compared} sequences match the landed frozen values exactly")

    print("\n== S2  per-state equivalence to a direct frozen-mapper call ==")
    sys.path.insert(0, f"{BUNDLE}/code")
    import importlib
    frozen = importlib.import_module("mapper")
    check(frozen.__file__ == f"{BUNDLE}/code/mapper.py", "S2 imported the frozen mapper",
          frozen.__file__)
    # Independent FASTA read. The planted duplicate identifier is dropped exactly as
    # production drops it - keeping it would silently concatenate two copies of one protein
    # and make this check compare against a sequence that was never mapped.
    inp = {}
    hdr = None
    for ln in open(f"{smoke}/smoke_input.faa"):
        ln = ln.rstrip()
        if ln.startswith(">"):
            h = ln[1:].split()[0]
            hdr = None if h in inp else h
            if hdr:
                inp[hdr] = ""
        elif hdr:
            inp[hdr] += ln
    valid = {k: v for k, v in inp.items()
             if len(v) >= 250 and not any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in v)}
    work = f"{smoke}/s2_work"
    os.makedirs(work, exist_ok=True)
    m, _, leng = frozen.state_to_residue(P.PROFILE_HMM, valid, work, "s2",
                                         pp_hi=P.PP_HI, pp_lo=P.PP_LO)
    by_seq = collections.defaultdict(dict)
    for r in states:
        by_seq[r["sequence_id"]][int(r["state_id"])] = r
    n_states_checked, mismatched = 0, []
    for sid, ref in m.items():
        got = by_seq.get(sid)
        if not got:
            mismatched.append(f"{sid}: no production state rows")
            continue
        for st in [a for a in P.ANCHORS if a <= leng]:
            n_states_checked += 1
            r, c = got[st], ref[st]
            want_idx = "" if c["residue_index"] is None else str(c["residue_index"])
            if (r["call_state"] != c["call"] or r["sequence_residue_index"] != want_idx
                    or r["amino_acid"] != c["aa"]):
                mismatched.append(f"{sid} state {st}: {r['call_state']}/"
                                  f"{r['sequence_residue_index']}/{r['amino_acid']} vs "
                                  f"{c['call']}/{want_idx}/{c['aa']}")
    check(not mismatched, f"S2 {n_states_checked} state calls identical to the frozen "
                          f"mapper", "; ".join(mismatched[:3]))

    print("\n== S3  determinism (byte-identical rerun) ==")
    for name in ("states", "sequences", "failures"):
        a = P.sha256_file(f"{smoke}/main/smoke.{name}.tsv")
        b = P.sha256_file(f"{smoke}/rerun/smoke.{name}.tsv")
        check(a == b, f"S3 smoke.{name}.tsv identical across runs", a[:16])

    print("\n== S4  batch-composition invariance ==")
    small = {r["sequence_id"]: r for r in read_tsv(f"{smoke}/batch1/smoke.sequences.tsv")}
    # domain_bitscore AND domain_evalue are included deliberately. hmmsearch E-values scale
    # with database size, so batched domain scoring would make both - and, at the margin,
    # whether a domain is reported at all - a function of shard geometry. Production scores
    # one sequence at a time; this check is what holds that in place.
    sci = ("n_mapped", "n_ambiguous", "n_unsupported", "n_deleted", "mapped_fraction",
           "verdict", "reason", "domain_bitscore", "domain_evalue", "cat_call_state",
           "cat_residue_index", "cat_motif_class", "inspectability_status")
    diff = [f"{r['sequence_id']}.{c}" for r in seqs for c in sci
            if small.get(r["sequence_id"], {}).get(c) != r[c]]
    check(len(small) == len(seqs) and not diff,
          "S4 batch-size 1 and default batching agree on every scientific column, domain scores included",
          "; ".join(diff[:3]))

    print("\n== S5  call-state completeness ==")
    seen = collections.Counter(r["call_state"] for r in states)
    check(set(seen) <= set(S.CALL_STATES), "S5 no call state outside the frozen four",
          str(sorted(set(seen) - set(S.CALL_STATES))))
    check(set(seen) == set(S.CALL_STATES), "S5 all four call states reachable in the output",
          " ".join(f"{k}={seen[k]}" for k in S.CALL_STATES))
    check(all(int(r["n_states_total"]) == len(P.ANCHORS) for r in seqs),
          f"S5 every sequence carries all {len(P.ANCHORS)} frozen anchor rows")
    check(len(states) == len(seqs) * len(P.ANCHORS),
          "S5 state row count = sequences x anchors",
          f"{len(states)} == {len(seqs)} x {len(P.ANCHORS)}")

    print("\n== S6  failure states ==")
    byreason = collections.Counter(r["reason_code"] for r in fails)
    for want in ("BELOW_MIN_LENGTH", "NON_STANDARD_RESIDUE", "EMPTY_SEQUENCE",
                 "DUPLICATE_SEQUENCE_ID"):
        check(byreason[want] == 1, f"S6 exactly one {want}", str(byreason[want]))
    check(all(r["inspectability_status"] in S.NON_SCIENTIFIC_STATUS for r in fails),
          "S6 every failure row is INPUT_INVALID or TOOL_FAILURE")
    check(all(r["inspectability_status"] not in S.NON_SCIENTIFIC_STATUS for r in seqs),
          "S6 no engineering-failure status leaks into sequences.tsv")

    print("\n== S7  deduplication ==")
    dup = [r for r in seqs if r["sequence_id"].startswith("SMOKE_DUPLICATE_OF_")]
    check(len(dup) == 1, "S7 the planted duplicate sequence produced its own row")
    if dup:
        orig_id = dup[0]["sequence_id"][len("SMOKE_DUPLICATE_OF_"):]
        orig = [r for r in seqs if r["sequence_id"] == orig_id]
        check(bool(orig) and orig[0]["rt_hash"] == dup[0]["rt_hash"],
              "S7 duplicate and original share one rt_hash", dup[0]["rt_hash"][:16])
        check(bool(orig) and all(orig[0][c] == dup[0][c] for c in sci),
              "S7 duplicate and original carry identical calls")
    check(prov.get("duplicate_ids_collapsed") == "1",
          "S7 provenance records exactly one collapsed duplicate",
          prov.get("duplicate_ids_collapsed"))
    check(int(prov["distinct_rt_hash"]) == int(prov["input_valid"]) - 1,
          "S7 distinct rt_hash = valid inputs - 1")

    print()
    if FAILS:
        print(f"SMOKE FAILED: {len(FAILS)} check(s): {FAILS}")
        return 1
    print("SMOKE OK - production packaging reproduces the frozen mapper exactly.")
    print("This is an ENGINEERING result. It is not new scientific validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
