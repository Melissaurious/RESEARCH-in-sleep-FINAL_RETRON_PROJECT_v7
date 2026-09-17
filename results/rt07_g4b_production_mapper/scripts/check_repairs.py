#!/usr/bin/env python3
"""Checks for the five repairs the independent packaging review required. ENGINEERING ONLY.

    check_repairs.py <work_dir>

Each check reproduces the reviewer's own demonstration and asserts it no longer holds.

  R1  the instrument identifier binds the production wrapper, the eligibility rule and the
      domain-scoring protocol - so a wrapper that silently reverted to batched hmmsearch
      cannot keep the same identifier; and the bundle root is verified and recorded.
  R2  duplicate identifiers are deterministic and order-independent.
  R3  every valid input identifier reconciles to exactly one outcome, aliases included.
  R4  a DONE sidecar is validated, not merely present.
  R5  the inspectability status introduces no predicate of its own.
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G4B = os.path.dirname(HERE)
PY = "/home/borg/miniconda3/envs/retron_tradicional/bin/python3"
RUNNER = f"{G4B}/code/rtmap/run_mapper.py"

sys.path.insert(0, f"{G4B}/code")
from rtmap import params as P          # noqa: E402
from rtmap import schema as S          # noqa: E402
from rtmap import version as V         # noqa: E402
from rtmap import run_mapper as R      # noqa: E402

FAILS = []
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def check(ok, label, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)


def run(args, **kw):
    return subprocess.run([PY, "-B", RUNNER] + args, capture_output=True, text=True,
                          env=ENV, **kw)


def write_fasta(path, records):
    with open(path, "w") as f:
        for sid, seq in records:
            f.write(f">{sid}\n{seq}\n")


def real_sequence():
    """One real construction sequence, so the runner does real work."""
    sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
                       "FINAL_PRE_UG25_VALIDATION_BUNDLE/code")
    from loader import load_families
    e = load_families(("GII",))
    k = sorted(e["GII"])[0]
    return k, e["GII"][k]


def r1_identifier_binds_the_wrapper(w):
    print("\n== R1  the identifier binds the production wrapper ==")
    c = V.check_instrument()
    base = V.mapper_version(c)
    for field in ("instrument_tree_sha256", "eligibility_rule", "domain_scoring_protocol"):
        check(field in c, f"R1 {field} is an instrument component")
        check(V.mapper_version(dict(c, **{field: "CHANGED"})) != base,
              f"R1 changing {field} changes the identifier")
    # the tree digest must actually move when the wrapper changes
    import shutil
    td = f"{w}/r1_tree"
    shutil.rmtree(td, ignore_errors=True)
    os.makedirs(td)
    subprocess.run(["cp", "-r", "--no-preserve=mode", f"{G4B}/code", f"{G4B}/control", td],
                   check=True)
    with open(f"{td}/code/rtmap/run_mapper.py", "a") as f:
        f.write("\n# a silent wrapper change\n")
    r = subprocess.run([PY, "-B", "-c",
                        "import sys; sys.path.insert(0,'code');"
                        " from rtmap import version as V; print(V.instrument_tree_sha256())"],
                       capture_output=True, text=True, cwd=td, env=ENV)
    check(r.returncode == 0 and r.stdout.strip() != c["instrument_tree_sha256"],
          "R1 editing run_mapper.py changes the instrument tree digest",
          r.stdout.strip()[:16] or r.stderr.strip()[:60])
    # tables/ must NOT be in the tree - landing an output cannot change the instrument
    check("tables" not in V.INSTRUMENT_TREES,
          "R1 tables/ is excluded, so landing an output does not change the instrument")

    # bundle-root verification
    sid, seq = real_sequence()
    fa = f"{w}/r1.faa"
    write_fasta(fa, [(sid, seq)])
    good_root = R.bundle_root_now()
    ok = run(["--in", fa, "--out", f"{w}/r1_out", "--shard", "r1",
              "--pinned-root", good_root, "--work", f"{w}/r1_work"])
    check(ok.returncode == 0, "R1 a correct pinned root is accepted", ok.stderr[-120:])
    bad = run(["--in", fa, "--out", f"{w}/r1_bad", "--shard", "r1b",
               "--pinned-root", "f" * 64, "--work", f"{w}/r1_workb"])
    check(bad.returncode != 0 and "pinned root" in (bad.stdout + bad.stderr),
          "R1 a wrong pinned root FAILS CLOSED before any record is emitted")
    check(not os.path.exists(f"{w}/r1_bad/r1b.sequences.tsv"),
          "R1 nothing was written by the refused run")
    prov = dict(ln.rstrip("\n").split("\t", 1)
                for ln in open(f"{w}/r1_out/r1.provenance.tsv"))
    check(prov.get("bundle_root_sha256") == good_root
          and prov.get("bundle_root_status") == "VERIFIED",
          "R1 provenance records the verified bundle root",
          prov.get("bundle_root_status"))
    check(prov.get("domain_scoring_protocol") == "PER_SEQUENCE_DB_SIZE_1"
          and prov.get("eligibility_rule", "").startswith("MIN_AA=250"),
          "R1 provenance records the protocol and eligibility rule")


def r2_duplicate_ids_are_deterministic(w):
    print("\n== R2  duplicate identifiers are order-independent ==")
    a, c = "A" * 300, "C" * 300
    fwd, _ = R.validate([("x", a), ("x", c)])
    rev, _ = R.validate([("x", c), ("x", a)])
    check(fwd == rev == {}, "R2 an identifier with two DIFFERENT sequences retains neither",
          f"forward {list(fwd)} reverse {list(rev)}")
    _, inv_f = R.validate([("x", a), ("x", c)])
    codes = sorted(code for _, _, code, _ in inv_f)
    check(codes == ["DUPLICATE_SEQUENCE_ID_CONFLICT"] * 2,
          "R2 both occurrences are rejected as a conflict", str(codes))
    same_f, inv_s = R.validate([("y", a), ("y", a)])
    check(list(same_f) == ["y"] and same_f["y"] == a,
          "R2 an identifier repeated with an IDENTICAL sequence is kept once")
    check([code for _, _, code, _ in inv_s] == ["DUPLICATE_SEQUENCE_ID"],
          "R2 the redundant copy is still logged")
    g, inv_r = R.validate([("z", a)], reject_ids={"z"})
    check(g == {} and [code for _, _, code, _ in inv_r]
          == ["DUPLICATE_SEQUENCE_ID_CONFLICT"],
          "R2 the global census reject list is honoured")
    check("DUPLICATE_SEQUENCE_ID_CONFLICT" in S.INPUT_INVALID_REASONS,
          "R2 the conflict reason is in the schema")


def r3_every_input_reconciles(w):
    print("\n== R3  every valid input identifier reconciles to exactly one outcome ==")
    sid, seq = real_sequence()
    fa = f"{w}/r3.faa"
    write_fasta(fa, [("alias_a", seq), ("alias_b", seq)])
    ok = run(["--in", fa, "--out", f"{w}/r3_out", "--shard", "r3", "--work", f"{w}/r3_work"])
    check(ok.returncode == 0, "R3 the two-alias shard runs", ok.stderr[-150:])
    rows = open(f"{w}/r3_out/r3.sequences.tsv").read().splitlines()[1:]
    got = sorted(r.split("\t")[1] for r in rows)
    check(got == ["alias_a", "alias_b"], "R3 both aliases get a row", str(got))

    # now force the mapper to fail, and check BOTH aliases are accounted for
    broken = f"{w}/broken"
    os.makedirs(broken, exist_ok=True)
    subprocess.run(["cp", "-r", "--no-preserve=mode", f"{G4B}/code", f"{G4B}/control",
                    broken], check=True)
    mp = f"{broken}/code/rtmap/run_mapper.py"
    src = open(mp).read().replace(
        "    m, ins, leng = state_to_residue(",
        "    raise RuntimeError('planted failure')\n    m, ins, leng = state_to_residue(", 1)
    open(mp, "w").write(src)
    r = subprocess.run([PY, "-B", f"{broken}/code/rtmap/run_mapper.py", "--in", fa,
                        "--out", f"{w}/r3_fail", "--shard", "r3f",
                        "--work", f"{w}/r3_failwork"], capture_output=True, text=True,
                       env=ENV)
    frows = open(f"{w}/r3_fail/r3f.failures.tsv").read().splitlines()[1:] \
        if os.path.exists(f"{w}/r3_fail/r3f.failures.tsv") else []
    fids = sorted(x.split("\t")[1] for x in frows)
    check(r.returncode == 0 and fids == ["alias_a", "alias_b"],
          "R3 a planted mapper failure produces a TOOL_FAILURE row for BOTH aliases",
          f"rc={r.returncode} ids={fids}")

    # and the reconciliation assertion itself fires when an outcome is dropped
    mp2 = f"{broken}/code/rtmap/run_mapper.py"
    src2 = open(mp2).read().replace(
        "                        for sid in sorted(by_hash[rt_hash(rseq)]):",
        "                        for sid in sorted(by_hash[rt_hash(rseq)])[:1]:", 1)
    open(mp2, "w").write(src2)
    r2 = subprocess.run([PY, "-B", mp2, "--in", fa, "--out", f"{w}/r3_drop",
                         "--shard", "r3d", "--work", f"{w}/r3_dropwork"],
                        capture_output=True, text=True, env=ENV)
    check(r2.returncode != 0 and "does not reconcile" in (r2.stdout + r2.stderr),
          "R3 dropping one alias's outcome FAILS CLOSED", (r2.stdout + r2.stderr)[-90:])


def r4_done_is_validated(w):
    print("\n== R4  a DONE sidecar is validated, not merely present ==")
    sid, seq = real_sequence()
    fa = f"{w}/r4.faa"
    write_fasta(fa, [(sid, seq)])
    out = f"{w}/r4_out"
    os.makedirs(out, exist_ok=True)
    open(f"{out}/probe.DONE", "w").write("")
    r = run(["--in", fa, "--out", out, "--shard", "probe", "--work", f"{w}/r4_work"])
    produced = os.path.exists(f"{out}/probe.sequences.tsv")
    check(r.returncode == 0 and produced and "SKIP" not in r.stdout,
          "R4 an EMPTY DONE does not skip the shard", r.stdout.strip()[:80])
    r2 = run(["--in", fa, "--out", out, "--shard", "probe", "--work", f"{w}/r4_work"])
    check("SKIP" in r2.stdout, "R4 a genuine, verified DONE does skip", r2.stdout.strip())
    # corrupt an output: the shard must be redone, not skipped
    with open(f"{out}/probe.states.tsv", "a") as f:
        f.write("tampered\n")
    r3 = run(["--in", fa, "--out", out, "--shard", "probe", "--work", f"{w}/r4_work"])
    check("SKIP" not in r3.stdout and "REDO" in r3.stderr,
          "R4 a tampered output forces a redo", r3.stderr.strip()[:90])
    # change the input: the shard must be redone
    write_fasta(fa, [(sid, seq), ("second_" + sid, seq)])
    r4 = run(["--in", fa, "--out", out, "--shard", "probe", "--work", f"{w}/r4_work"])
    check("SKIP" not in r4.stdout and "input changed" in r4.stderr,
          "R4 a changed input forces a redo", r4.stderr.strip()[:90])


def r5_status_introduces_no_predicate(w):
    print("\n== R5  the inspectability status introduces no predicate of its own ==")
    check(R.inspectability("MAPPED", "OK", 0.67) == "MAPPABLE", "R5 MAPPABLE")
    check(R.inspectability("MAPPED", "OK", 0.30) == "PARTIAL_MAPPING",
          "R5 PARTIAL_MAPPING below the frozen T1")
    for (v, rsn), want in sorted(S.STATUS_FROM_FROZEN_REASON.items()):
        check(R.inspectability(v, rsn, 0.0) == want,
              f"R5 ({v}, {rsn}) -> {want} by relabelling alone")
    check(R.inspectability("ABSTAIN", "INSUFFICIENT_SUPPORTED_ANCHORS", 0.0)
          == "AMBIGUOUS_MAPPING",
          "R5 AMBIGUOUS_MAPPING no longer depends on any count comparison")
    # the removed predicate: with zero AMBIGUOUS calls the status must still follow the
    # frozen reason, not an invented magnitude test
    # Inspect the function's CODE, not its docstring - the docstring names the removed
    # predicate on purpose, so that the history is not quietly erased.
    import inspect
    src = inspect.getsource(R.inspectability)
    body = src.split('"""')[2] if src.count('"""') >= 2 else src
    check("n_amb" not in body and "n_uns" not in body and "n_map" not in body,
          "R5 no anchor-count comparison remains in the function body")
    check("n_ambiguous + n_unsupported > n_mapped" in " ".join(src.split()),
          "R5 the removed predicate is still named in the docstring, not erased")
    check(set(S.STATUS_FROM_FROZEN_REASON.values())
          | {"MAPPABLE", "PARTIAL_MAPPING"} | set(S.NON_SCIENTIFIC_STATUS)
          == set(S.INSPECTABILITY_STATUS),
          "R5 every documented status is reachable and none is undocumented")
    try:
        R.inspectability("ABSTAIN", "A_REASON_THE_MAPPER_NEVER_EMITS", 0.0)
        check(False, "R5 an unmapped frozen reason fails closed")
    except SystemExit:
        check(True, "R5 an unmapped frozen reason fails closed")


def main():
    w = sys.argv[1]
    os.makedirs(w, exist_ok=True)
    for t in (r1_identifier_binds_the_wrapper, r2_duplicate_ids_are_deterministic,
              r3_every_input_reconciles, r4_done_is_validated,
              r5_status_introduces_no_predicate):
        t(w)
    print()
    if FAILS:
        print(f"REPAIR CHECKS FAILED: {len(FAILS)}")
        for f in FAILS:
            print(f"  {f}")
        return 1
    print("REPAIR CHECKS OK - all five review repairs hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
