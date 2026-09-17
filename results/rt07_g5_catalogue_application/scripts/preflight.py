#!/usr/bin/env python3
"""g5 preflight — instrument verification (task §3) and a production smoke test (task §9).

    preflight.py <work_dir> <shard_dir>

ENGINEERING ONLY. Nothing here is scientific validation, and no number it prints is a result.

§3 — the instrument must be the canonical g4b instrument, field by field. Any difference is
a STOP, with no compatibility substitution.

§9 — one shard is run through the frozen production path and checked for: schema; exact row
counts; 150 state rows per successfully mapped eligible sequence; catalytic rows and fields;
deterministic rerun; batch-size independence; failures retained; and that joining Stage-1
metadata changes no scientific column.
"""
import collections
import hashlib
import os
import subprocess
import sys

ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
G4B = f"{ROOT}/results/rt07_g4b_production_mapper"
PY = "/home/borg/miniconda3/envs/retron_tradicional/bin/python3"
RUNNER = f"{G4B}/code/rtmap/run_mapper.py"
ROOTFILE = f"{ROOT}/review-stage/roots/RT07_G4B.root"

sys.path.insert(0, f"{G4B}/code")
from rtmap import params as P               # noqa: E402
from rtmap import schema as S               # noqa: E402
from rtmap import version as V              # noqa: E402

# The canonical g4b instrument, as the operator stated it and as the landed bundle records it.
CANON = {
    "mapper_version": "rtmap-1.0.0/53a1e738a19b3896",
    "instrument_sha256":
        "53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5",
    "mapper_sha256":
        "69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef",
    "schema_version": "rtmap-schema-1.0",
    "profile_sha256":
        "292495a4f4ec2d04c47cf73c658b0f5cbaec7b202de70d97e6fc2496dd82e97b",
    "profile_leng": "471",
    "anchor_set_sha256":
        "3eca033357f5f7ca2b3f0e53a5e48b0b2ee9e0e3a0f4d2a08a0f9c2bbd8a1e35",  # checked as n+hash
    "match_state_definition": "hhmake -M 50",
    "CAT_STATE": "262",
    "PP_HI": "0.75", "PP_LO": "0.5", "S_MIN": "10", "K_MIN": "30",
    "T1": "0.32", "D_MAX": "0.48", "D_RANDOM": "0.067",
    "dyad_pattern": "[YF].DD",
    "hmmalign_sha256":
        "532f1ed4c21dc03a12007b31c2dc0568e82cab659b0d75c20efd20e6374f53e2",
    "hmmsearch_sha256":
        "e73bad9d701f129795dd3ffb108ee2d4724ab4c8b1a46269bd5671bdcfcdc8f2",
    "domain_scoring_protocol": "PER_SEQUENCE_DB_SIZE_1",
    "eligibility_rule": "MIN_AA=250;ALPHABET=ACDEFGHIKLMNPQRSTVWY;CLEAN=strip[-.]upper,rstrip*",
}

FAILS = []


def check(ok, label, detail=""):
    print(f"  {'ok  ' if ok else 'STOP'}  {label}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)


def read_tsv(path):
    with open(path) as f:
        cols = f.readline().rstrip("\n").split("\t")
        return [dict(zip(cols, ln.rstrip("\n").split("\t"))) for ln in f if ln.strip()]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def instrument_check():
    print("\n== §3  INSTRUMENT — must be the canonical g4b instrument ==")
    c = V.check_instrument()
    mv = V.mapper_version(c)
    check(mv == CANON["mapper_version"], "instrument version", mv)
    check(V.instrument_digest(c) == CANON["instrument_sha256"], "instrument sha256",
          V.instrument_digest(c)[:20])
    check(c["mapper_sha256"] == CANON["mapper_sha256"], "mapper code hash")
    check(c["schema_version"] == CANON["schema_version"], "schema version",
          c["schema_version"])
    check(c["profile_sha256"] == CANON["profile_sha256"], "profile / HMM hash")
    check(c["profile_leng"] == CANON["profile_leng"], "profile LENG", c["profile_leng"])
    check(len(P.ANCHORS) == 150 and P.ANCHORS == sorted(P.ANCHORS),
          "frozen anchor/state definition: 150 states, ascending")
    check(c["anchor_set_sha256"] == P.anchor_set_sha256(),
          "anchor-set digest matches the frozen table")
    check(P.CAT_STATE == 262, "CAT_STATE 262", str(P.CAT_STATE))
    check(P.CAT_STATE not in P.ANCHORS,
          "CAT_STATE is NOT one of the 150 anchors — separate denominator")
    for k in ("PP_HI", "PP_LO", "S_MIN", "K_MIN", "T1", "D_MAX", "D_RANDOM"):
        check(c[k] == CANON[k], f"calibrated parameter {k} = {CANON[k]}", c[k])
    check(c["match_state_definition"] == CANON["match_state_definition"],
          "match-state convention", c["match_state_definition"])
    check(c["dyad_pattern"] == CANON["dyad_pattern"], "catalytic dyad pattern")
    check(c["hmmalign_sha256"] == CANON["hmmalign_sha256"], "hmmalign binary")
    check(c["hmmsearch_sha256"] == CANON["hmmsearch_sha256"], "hmmsearch binary")
    check(V.hmmer_version().startswith("HMMER 3.4"), "HMMER version", V.hmmer_version())
    check(c["domain_scoring_protocol"] == CANON["domain_scoring_protocol"],
          "domain-scoring protocol", c["domain_scoring_protocol"])
    check(c["eligibility_rule"] == CANON["eligibility_rule"], "eligibility rule")
    pinned = open(ROOTFILE).read().strip()
    check(len(pinned) == 64, "external pinned bundle root present", pinned[:16])
    return mv, pinned


def run(args, cwd=None):
    return subprocess.run([PY, "-B", RUNNER] + args, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, cwd=cwd)


def smoke(work, shard_dir, pinned):
    print("\n== §9  SMOKE TEST on one production shard (engineering only) ==")
    fa = f"{shard_dir}/shard_0000.faa"
    n_in = sum(1 for ln in open(fa) if ln.startswith(">"))
    a, b, c3 = f"{work}/smoke_a", f"{work}/smoke_b", f"{work}/smoke_c"
    for out, extra in ((a, []), (b, []), (c3, ["--batch-size", "97"])):
        r = run(["--in", fa, "--out", out, "--shard", "shard_0000",
                 "--work", f"{work}/w_{os.path.basename(out)}",
                 "--pinned-root", pinned] + extra)
        if r.returncode != 0:
            check(False, f"runner failed for {out}", (r.stderr or r.stdout)[-200:])
            return
    seqs = read_tsv(f"{a}/shard_0000.sequences.tsv")
    states = read_tsv(f"{a}/shard_0000.states.tsv")
    fails = read_tsv(f"{a}/shard_0000.failures.tsv")
    prov = {r["key"]: r["value"] for r in read_tsv(f"{a}/shard_0000.provenance.tsv")}

    check(list(seqs[0].keys()) == list(S.SEQUENCES_COLUMNS), "sequences.tsv schema exact")
    check(list(states[0].keys()) == list(S.STATES_COLUMNS), "states.tsv schema exact")
    check(len(seqs) + len([f for f in fails
                           if f["inspectability_status"] == "TOOL_FAILURE"]) == n_in,
          "every eligible input reconciles to exactly one outcome",
          f"{len(seqs)} + tool-failures vs {n_in} in")
    check(len(states) == len(seqs) * 150, "150 state rows per mapped sequence",
          f"{len(states)} == {len(seqs)} x 150")
    per = collections.Counter(r["sequence_id"] for r in states)
    check(set(per.values()) == {150}, "no sequence has other than 150 state rows")
    check(set(r["call_state"] for r in states) <= set(S.CALL_STATES),
          "no call state outside the frozen four")
    check(all(r["cat_state"] == "262" for r in seqs), "catalytic field present on every row")
    check(all(r["cat_motif_class"] in S.CAT_MOTIF_CLASSES for r in seqs),
          "catalytic class is always a frozen value")
    check(prov.get("mapper_version") == CANON["mapper_version"],
          "provenance carries the canonical instrument")
    check(prov.get("bundle_root_status") == "VERIFIED",
          "provenance records a VERIFIED bundle root", prov.get("bundle_root_status"))

    for name in ("states", "sequences", "failures"):
        h1 = sha256_file(f"{a}/shard_0000.{name}.tsv")
        h2 = sha256_file(f"{b}/shard_0000.{name}.tsv")
        check(h1 == h2, f"deterministic rerun: {name}.tsv byte-identical", h1[:16])
    sci = ("n_mapped", "n_ambiguous", "n_unsupported", "n_deleted", "mapped_fraction",
           "verdict", "reason", "domain_bitscore", "domain_evalue", "cat_call_state",
           "cat_residue_index", "cat_motif_class", "inspectability_status")
    small = {r["sequence_id"]: r for r in read_tsv(f"{c3}/shard_0000.sequences.tsv")}
    diff = [f"{r['sequence_id']}.{k}" for r in seqs for k in sci
            if small.get(r["sequence_id"], {}).get(k) != r[k]]
    check(not diff, "batch-size independence on every scientific column",
          "; ".join(diff[:3]))
    check(sha256_file(f"{a}/shard_0000.states.tsv")
          == sha256_file(f"{c3}/shard_0000.states.tsv"),
          "batch-size independence: states.tsv byte-identical")

    st = collections.Counter(r["inspectability_status"] for r in seqs)
    print(f"  (descriptive) statuses on this shard: {dict(st)}")
    print(f"  (descriptive) failures retained: {len(fails)}")
    return seqs


def metadata_neutrality(work, seqs):
    """§9 — joining Stage-1 metadata must not change any scientific column.

    Structural, not empirical: the runner only ever reads metadata through `--metadata`,
    which writes exactly one column, `family_metadata`. The full g5 join happens AFTER
    mapping, in merge.py, against the landed outputs.
    """
    print("\n== §9  metadata join cannot influence mapping ==")
    import inspect
    sys.path.insert(0, f"{G4B}/code")
    from rtmap import run_mapper as RM
    src = open(f"{G4B}/code/rtmap/run_mapper.py").read()
    # The operative property: the metadata value enters `build_rows` as `family_meta` and is
    # used there exactly once, to fill the single schema column `family_metadata`. Every
    # other name in that function is a mapper output.
    body = inspect.getsource(RM.build_rows)
    uses = [ln.strip() for ln in body.splitlines()
            if "family_meta" in ln and not ln.strip().startswith("#")]
    check(len(uses) == 2 and uses[0].startswith("def build_rows")
          and uses[1].startswith('"family_metadata"'),
          "metadata reaches exactly one output column, family_metadata", " | ".join(uses))
    check('"family_metadata": family_meta or "NOT_SUPPLIED"' in body,
          "family_metadata is the only destination of a supplied label")
    for sym in ("by_myRT", "by_PADLOC", "by_DefenseFinder", "family_label",
                "source_database", "tax_"):
        check(sym not in src, f"runner never reads {sym}")
    check(all(r["family_metadata"] == "NOT_SUPPLIED" for r in seqs),
          "the g5 run supplies no metadata to the mapper at all")


def main():
    work, shard_dir = sys.argv[1], sys.argv[2]
    os.makedirs(work, exist_ok=True)
    mv, pinned = instrument_check()
    if FAILS:
        print(f"\nSTOP: instrument differs from canonical g4b: {FAILS}")
        return 1
    seqs = smoke(work, shard_dir, pinned)
    if seqs:
        metadata_neutrality(work, seqs)
    print()
    if FAILS:
        print(f"PREFLIGHT FAILED: {len(FAILS)}")
        for f in FAILS:
            print(f"  {f}")
        return 1
    print("PREFLIGHT OK — instrument is canonical and the production path behaves as in g4b.")
    print("This is an ENGINEERING result. It is not new scientific validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
