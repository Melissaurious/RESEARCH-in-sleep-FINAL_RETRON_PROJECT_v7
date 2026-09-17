#!/usr/bin/env python3
"""REPAIR 6 tests - the C6 policy, including the EMPTY-CONTROL branch, on synthetic inputs.

Each case is constructed so the expected verdict is known exactly. The empty branch is
exercised here so it is demonstrated before it can ever matter on a real holdout.

    control_policy_tests.py <tables_dir>
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from control_policy import evaluate_c6, CLASSES, REPLICATES_PER_SEQUENCE

TABLES = sys.argv[1]
rows = []
N = 28                                   # UG25 eligible count (feasibility only)
FULL = REPLICATES_PER_SEQUENCE * N       # 84 expected replicates per class


def rec(name, ok, detail, passes_when, fails_when):
    rows.append([name, "FALSIFIABLE_EMPIRICAL_TEST", "PASS" if ok else "FAIL", detail,
                 passes_when, fails_when])


def classes(mono, di, rev):
    return {"MONO": mono, "DI": di, "REV": rev}


real_ok = [140] * 40 + [31]              # min real = 31, just above the construction max of 25

# C1 - the good case must PASS, or every other case below proves nothing
v, why, _ = evaluate_c6(classes([0] * FULL, [0] * FULL, [10] * FULL), real_ok, N)
rec("C1_clean_separation_passes", v == "PASS", f"verdict={v} reasons={why}",
    "all three classes full and separated from the real minimum",
    "a clean, well-separated control set is rejected")

# C2 - EMPTY control class must FAIL CLOSED (the branch the operator asked for)
v, why, _ = evaluate_c6(classes([0] * FULL, [], [0] * FULL), real_ok, N)
rec("C2_empty_control_class_fails_closed",
    v == "FAIL" and any("EMPTY_CONTROL_CLASS:DI" in r for r in why),
    f"verdict={v} reasons={why}",
    "a class with zero valid replicates fails closed",
    "the gate proceeds on the two surviving classes and calls it separation")

# C3 - a class BELOW the replicate minimum must FAIL (di-shuffle depletion)
short = [0] * 60                          # 60 < required 76
v, why, _ = evaluate_c6(classes([0] * FULL, short, [0] * FULL), real_ok, N,
                        failed_ids_by_class={"DI": [f"s{i}" for i in range(24)]})
rec("C3_depleted_class_fails_closed",
    v == "FAIL" and any("INSUFFICIENT_REPLICATES:DI" in r for r in why),
    f"verdict={v} reasons={why}",
    "di-shuffle failures pushing a class below 90% of expected fail closed",
    "the gate proceeds with a silently thinner control class")

# C4 - ONE class violating separation must FAIL even though POOLED looks clean.
# This is the operator's explicit question. REV reaches 31 == min real; pooled p95 stays 0.
v, why, rep = evaluate_c6(classes([0] * FULL, [0] * FULL, [0] * (FULL - 1) + [31]),
                          real_ok, N)
pooled_p95 = [r for r in rep if r["control_class"] == "POOLED"][0]["p95"]
rec("C4_single_class_violation_fails_despite_clean_pooled",
    v == "FAIL" and any("SEPARATION_VIOLATED:REV" in r for r in why) and pooled_p95 == 0,
    f"verdict={v} pooled_p95={pooled_p95} reasons={why}",
    "one class touching the real minimum fails C6 even when the pooled statistic is clean",
    "pooling hides a single-class violation - the exact defect the reviewer identified")

# C5 - no non-abstaining real sequence: C6 is UNDEFINED, and undefined is a FAIL
v, why, _ = evaluate_c6(classes([0] * FULL, [0] * FULL, [0] * FULL), [], N)
rec("C5_no_real_sequences_fails_closed",
    v == "FAIL" and any("NO_NON_ABSTAINING_REAL_SEQUENCES" in r for r in why),
    f"verdict={v} reasons={why}",
    "an empty real set makes C6 undefined, which fails closed",
    "an undefined criterion is reported as satisfied")

# C6t - a MISSING class (not merely empty) must also fail
v, why, _ = evaluate_c6({"MONO": [0] * FULL, "REV": [0] * FULL}, real_ok, N)
rec("C6t_missing_class_fails_closed",
    v == "FAIL" and any("MISSING_CONTROL_CLASS:DI" in r for r in why),
    f"verdict={v} reasons={why}",
    "a control class absent from the results dict fails closed",
    "an omitted class is treated as vacuously satisfied")

# C7t - high per-class p95 alone must NOT fail: REV p95=10 is expected on construction data
v, why, rep = evaluate_c6(classes([0] * FULL, [0] * FULL, [10] * FULL), real_ok, N)
rev_p95 = [r for r in rep if r["control_class"] == "REV"][0]["p95"]
rec("C7t_high_p95_is_reported_not_failed",
    v == "PASS" and rev_p95 == 10,
    f"verdict={v} REV_p95={rev_p95} (reported, not a pass condition)",
    "a class with p95>0 still passes when separation holds, and its p95 is reported",
    "p95 is silently promoted to a pass condition, making C6 unpassable on real data")

with open(f"{TABLES}/control_policy_tests.tsv", "w") as f:
    f.write("test\tclassification\tresult\tdetail\tpasses_when\tfails_when\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[2]:4s} {r[0]:52s} {r[3]}")
bad = [r for r in rows if r[2] != "PASS"]
print(f"\n{len(rows)-len(bad)}/{len(rows)} passed")
sys.exit(1 if bad else 0)
