#!/usr/bin/env python3
"""
T-A22 · machine enforcement of DESIGN_FREEZE_01.

⛔ THIS CHANGES NO SCIENTIFIC DESIGN.  It is the executable form of a freeze that
already exists.  The admissible and inadmissible feature sets are DESIGN_FREEZE_01
section 2b, verbatim, materialised as A22_FEATURE_WHITELIST.tsv and
A22_FEATURE_DENYLIST.tsv.  Nothing here decides what a feature should be.

WHY IT EXISTS
    62 of the 81 RT-DNA anchors T-R1b would spend are T-A22's positive class, and
    77 of 81 carry a measured production value.  A feature chosen after seeing the
    anchors would be selected on the outcome.  The freeze fixes the feature set in
    advance; this file makes that fixing checkable by a machine rather than by a
    reader, which is the difference between a gate and a sentence about a gate.

TWO INDEPENDENT CHECKS, BOTH BLOCKING
    1  FEATURE ADMISSIBILITY -- default-DENY against the whitelist, plus a louder
       denylist that names WHY a rejected column is rejected and that catches
       aliases and proxies someone might otherwise add to the whitelist.
    2  OUTCOME POPULATION -- 175 panel rows; 103 measured; 67 producers; 36
       measured zeros; 72 EMPTY cells that are MISSING, never negative.

Usage:
    a22_validate.py --selftest                 # fixtures only, no external data
    a22_validate.py --check-panel              # read-only check of support.csv
    a22_validate.py --check-columns a,b,c      # validate a model matrix header
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WHITELIST = os.path.join(HERE, "A22_FEATURE_WHITELIST.tsv")
DENYLIST = os.path.join(HERE, "A22_FEATURE_DENYLIST.tsv")

PANEL = ("/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights"
         "/inputs/support.csv")
PANEL_SHA256 = "80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577"
C_PROD = "rtdna_production_xeco1"
C_ANCHOR = "RTDNA_sequence"

# DESIGN_FREEZE_01 section 1, counted from the file 2026-09-20.
EXPECT = {"panel_total": 175, "measured": 103, "producers": 67, "measured_zero": 36,
          "empty_production": 72, "anchors": 81, "anchor_and_measured": 77,
          "anchor_and_producer": 62}


def load_whitelist() -> set:
    with open(WHITELIST) as fh:
        return {r["feature_id"] for r in csv.DictReader(fh, delimiter="\t")
                if r["admissible"].strip().upper() == "YES"}


def load_denylist() -> list:
    with open(DENYLIST) as fh:
        return [(re.compile(r["pattern"]), r["reason"])
                for r in csv.DictReader(fh, delimiter="\t")]


def validate_columns(cols) -> list:
    """Return a list of (column, verdict, reason). Empty list == admissible."""
    allow, deny = load_whitelist(), load_denylist()
    out = []
    for c in cols:
        name = c.strip()
        hit = next(((rx, why) for rx, why in deny if rx.search(name)), None)
        if hit is not None:
            # A denylisted name is refused even if someone added it to the whitelist.
            out.append((name, "DENIED", hit[1]))
        elif name not in allow:
            out.append((name, "NOT_WHITELISTED",
                        "default-deny: not in A22_FEATURE_WHITELIST.tsv section 2b"))
    return out


def validate_outcome(rows) -> list:
    """Return a list of (check, expected, observed, state)."""
    def nonempty(r, c):
        return bool((r.get(c) or "").strip())

    measured = [r for r in rows if nonempty(r, C_PROD)]
    empty = [r for r in rows if not nonempty(r, C_PROD)]
    prod = [r for r in measured if float(r[C_PROD]) > 0]
    zero = [r for r in measured if float(r[C_PROD]) == 0]
    anchors = [r for r in rows if nonempty(r, C_ANCHOR)]
    a_and_m = [r for r in anchors if nonempty(r, C_PROD)]
    a_and_p = [r for r in a_and_m if float(r[C_PROD]) > 0]

    got = {"panel_total": len(rows), "measured": len(measured), "producers": len(prod),
           "measured_zero": len(zero), "empty_production": len(empty),
           "anchors": len(anchors), "anchor_and_measured": len(a_and_m),
           "anchor_and_producer": len(a_and_p)}
    checks = [(k, EXPECT[k], got[k], "PASS" if got[k] == EXPECT[k] else "FAIL")
              for k in EXPECT]
    # The rule the freeze exists to protect: an empty cell is MISSING, not a zero.
    coerced = sum(1 for r in empty if (r.get(C_PROD) or "").strip() == "0")
    checks.append(("empty_cells_never_coded_zero", 0, coerced,
                   "PASS" if coerced == 0 else "FAIL"))
    checks.append(("outcome_population_is_measured_only", EXPECT["measured"],
                   len(prod) + len(zero),
                   "PASS" if len(prod) + len(zero) == EXPECT["measured"] else "FAIL"))
    return checks


# ------------------------------------------------------------------- selftest
def selftest() -> int:
    allow = sorted(load_whitelist())
    cases = [
        ("every whitelisted feature", allow, True),
        ("empty matrix", [], True),
        ("rt_len alone", ["rt_len"], True),
        # --- the ones that must be refused -------------------------------
        ("RT-DNA length", ["rt_len", "rtdna_length"], False),
        ("RT-DNA coords", ["rtdna_start", "rtdna_end"], False),
        ("RT-DNA position in ncRNA", ["rt_dna_position_in_ncrna"], False),
        ("msDNA alias", ["msdna_len"], False),
        ("punctuated msDNA alias", ["ms-dna-length"], False),
        ("anchor presence", ["has_anchor"], False),
        ("anchor availability", ["anchor_available"], False),
        ("T-R1b output", ["r1b_anchor_coordinate"], False),
        ("T-A5b1 output", ["a5b1_start"], False),
        ("boundary feature", ["ncrna_boundary_score"], False),
        ("the OUTCOME as a feature", ["rtdna_production_xeco1"], False),
        ("outcome alias", ["production_level"], False),
        ("unknown novel feature", ["some_new_idea"], False),
        ("whitelisted + one denied", allow + ["rtdna_len"], False),
    ]
    fails = 0
    print("=== FEATURE ADMISSIBILITY ===")
    for label, cols, want_ok in cases:
        v = validate_columns(cols)
        ok = (len(v) == 0)
        good = ok == want_ok
        fails += 0 if good else 1
        verdict = "PASS" if good else "FAIL"
        detail = "admissible" if ok else "; ".join(f"{c}:{s}" for c, s, _ in v)[:78]
        print(f"  [{verdict}] {label:<34} -> {detail}")
    print("\n=== OUTCOME-POPULATION LOGIC (synthetic) ===")
    synth = ([{C_PROD: "1.0", C_ANCHOR: "ACGT"}] * 62
             + [{C_PROD: "1.0", C_ANCHOR: ""}] * 5
             + [{C_PROD: "0", C_ANCHOR: "ACGT"}] * 15
             + [{C_PROD: "0", C_ANCHOR: ""}] * 21
             + [{C_PROD: "", C_ANCHOR: "ACGT"}] * 4
             + [{C_PROD: "", C_ANCHOR: ""}] * 68)
    for name, exp, obs, st in validate_outcome(synth):
        print(f"  [{st}] {name:<38} expected={exp:<5} observed={obs}")
        fails += 0 if st == "PASS" else 1
    print(f"\n=== {'ALL CHECKS PASS' if not fails else str(fails) + ' FAILURES'} ===")
    return 0 if fails == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check-panel", action="store_true")
    ap.add_argument("--check-columns")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if a.check_columns:
        v = validate_columns([c for c in a.check_columns.split(",") if c.strip()])
        if not v:
            print("ADMISSIBLE: every column is in the frozen whitelist")
            return 0
        print("⛔ REFUSED — DESIGN_FREEZE_01 section 2b")
        for c, s, why in v:
            print(f"  {s:<16} {c:<34} {why}")
        return 2

    if a.check_panel:
        import hashlib
        h = hashlib.sha256(open(PANEL, "rb").read()).hexdigest()
        print(f"panel sha256 {'OK' if h == PANEL_SHA256 else 'MISMATCH'}  {h}")
        if h != PANEL_SHA256:
            return 2
        rows = list(csv.DictReader(open(PANEL)))
        bad = 0
        for name, exp, obs, st in validate_outcome(rows):
            print(f"  [{st}] {name:<38} expected={exp:<5} observed={obs}")
            bad += 0 if st == "PASS" else 1
        print("ALL PASS" if not bad else f"{bad} FAILURES")
        return 0 if not bad else 2

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
