#!/usr/bin/env python3
"""Failure-injection suite for the programme's gates.

Every test deliberately breaks one rule and asserts the machinery REFUSES, except the one
test that asserts it ALLOWS a valid negative result through. Non-scientific; touches no
project data. Writes programme/PREFLIGHT_TESTS.tsv.

Run:  python3 programme/test_gates.py
"""
from __future__ import annotations
import csv, hashlib, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import preflight as pf  # noqa: E402

PROGRAMME = Path(__file__).parent
RESULTS: list[dict] = []


def record(test_id: str, rule: str, injected: str, expected: str, ok: bool, detail: str) -> None:
    RESULTS.append({
        "test_id": test_id, "rule": rule, "fault_injected": injected,
        "expected_behaviour": expected, "result": "PASS" if ok else "FAIL",
        "detail": detail,
    })


# --------------------------------------------------------------------------- tests

def t01_unauthorized_task() -> None:
    board = {"T-FAKE": {"task_id": "T-FAKE", "state": "HELD"}}
    p = pf.preflight("T-FAKE", board, base="deadbee")
    ok = not p.launchable
    record("FI-01", "only AUTHORIZED tasks may launch", "task state=HELD",
           "refuse", ok, f"launchable={p.launchable}")


def t02_stale_governance_base() -> None:
    board = pf.read_board()
    real = next((t for t in board if (pf.TASKS / t / "TASK_LAUNCHER.md").exists()), None)
    p = pf.preflight(real, board, base="0000000")  # pretend governance moved on
    failed = [c.name for c in p.checks if not c.ok]
    ok = (not p.launchable) and "governance_base_current" in failed
    record("FI-02", "worktree and launcher must match the governance base",
           "governance base advanced to 0000000", "refuse", ok,
           f"failed checks: {failed}")


def t03_input_hash_mismatch() -> None:
    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".tsv") as fh:
        fh.write(b"col\n1\n"); path = fh.name
    good = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    ok_good, _ = pf.hash_guard(path, good)
    ok_bad, detail = pf.hash_guard(path, "0" * 64)
    ok = ok_good and not ok_bad
    record("FI-03", "inputs must match their preregistered hash",
           "input hash altered", "refuse", ok, detail)


def t04_write_outside_output_dir() -> None:
    wt = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A0-lineage-variance"
    out = "analysis/t_a0_lineage_variance/"
    ok_in, _ = pf.write_guard(f"{wt}/{out}tables/x.tsv", out, wt)
    ok_out, detail = pf.write_guard(f"{wt}/results/frozen_bundle/x.tsv", out, wt)
    ok_esc, _ = pf.write_guard("/home/borg/elsewhere/x.tsv", out, wt)
    ok = ok_in and not ok_out and not ok_esc
    record("FI-04", "a task writes only under its declared output_directory",
           "write to results/ and to an unrelated absolute path", "refuse both", ok, detail)


def t05_criterion_changed() -> None:
    ok_same, _ = pf.criterion_guard("R-G CI excludes zero", "R-G CI excludes zero")
    ok_diff, detail = pf.criterion_guard("R-G CI excludes zero", "R-G point estimate is negative")
    ok = ok_same and not ok_diff
    record("FI-05", "a criterion may not change after preregistration",
           "criterion rewritten post hoc", "refuse", ok, detail)


def t06_population_collision() -> None:
    ok_clear, _ = pf.population_guard({"NEW-POP-A"}, {"PAIR-ELIG"})
    ok_clash, detail = pf.population_guard({"PAIR-ELIG"}, {"PAIR-ELIG"})
    ok = ok_clear and not ok_clash
    record("FI-06", "a confirmatory population is consumed once",
           "two tasks claim the same population", "refuse the second", ok, detail)


def t07_consume_from_void() -> None:
    allowed, detail = pf.consumption_gate("VOID", "DESCRIPTIVE", "tables/x.tsv", ["tables/x.tsv"])
    record("FI-07", "no downstream consumption from an invalid task",
           "producer TASK_STATE=VOID", "refuse", not allowed, detail)


def t08_consume_from_valid_negative() -> None:
    """The one test that must ALLOW. A refuted hypothesis is a successful task."""
    allowed, detail = pf.consumption_gate("PASS", "FALSIFIED", "tables/x.tsv", ["tables/x.tsv"])
    record("FI-08", "a valid negative result is consumable",
           "producer PASS + FALSIFIED", "ALLOW", allowed, detail)


def t08b_consume_unlisted_artifact() -> None:
    allowed, detail = pf.consumption_gate("PASS", "FALSIFIED", "tables/debug.tsv", ["tables/x.tsv"])
    record("FI-08b", "only declared CONSUMABLE_OUTPUTS may be read",
           "artifact absent from the consumable list", "refuse", not allowed, detail)


def t09_prereg_after_job() -> None:
    t = time.time()
    ok_good, _ = pf.ordering_guard(t, t + 60)
    ok_bad, detail = pf.ordering_guard(t + 60, t)
    ok = ok_good and not ok_bad
    record("FI-09", "preregistration must precede job submission",
           "prereg timestamp set after the job started", "refuse", ok, detail)


SUITE = [t01_unauthorized_task, t02_stale_governance_base, t03_input_hash_mismatch,
         t04_write_outside_output_dir, t05_criterion_changed, t06_population_collision,
         t07_consume_from_void, t08_consume_from_valid_negative,
         t08b_consume_unlisted_artifact, t09_prereg_after_job]


def run_suite() -> int:
    for fn in SUITE:
        try:
            fn()
        except Exception as exc:  # a crashing gate is a failing gate
            record(fn.__name__, "gate must not crash", "n/a", "no exception", False, repr(exc))
    out = PROGRAMME / "PREFLIGHT_TESTS.tsv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(RESULTS[0].keys()), delimiter="\t")
        w.writeheader(); w.writerows(RESULTS)
    npass = sum(r["result"] == "PASS" for r in RESULTS)
    for r in RESULTS:
        print(f"  [{r['result']}] {r['test_id']:<8} {r['rule']}")
    print(f"\n{npass}/{len(RESULTS)} gate tests pass -> {out}")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(run_suite())
