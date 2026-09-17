#!/usr/bin/env python3
"""C6 tests: semantic cases, value validation, and TYPED IDENTITY accounting.

Lands:
  c6_policy_tests.tsv          - semantic + canonical-order cases
  c6_negative_test_matrix.tsv  - one row per invalid state, each asserting a reason code

Every invalid state must return an explicit FAIL with a reason code and must NOT raise.
Positive cases must still PASS, or the matrix proves nothing.

    tests_c6.py <tables_dir>
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c6_policy import evaluate_c6, CLASSES
from canonical_order import (CANONICAL_FAMILY_ORDER, CANONICAL_SEED,
                             CANONICAL_ORDER_HASH, assert_canonical)

TABLES = sys.argv[1]
N = 28                     # UG25 eligible count (feasibility only; no mapping performance)
REPS = 3
FULL = REPS * N            # 84 attempted replicates per class
NAN, INF = float("nan"), float("inf")
sem, neg = [], []

real_ok = [140] * 27 + [31]          # 28 real observations, min 31


def att(c, n=FULL):
    return [f"{c}#r{i}" for i in range(n)]


def baseline(n_valid=FULL):
    """A fully reconciled, separated, type-correct control set. Must PASS."""
    vals = {c: [0] * n_valid for c in CLASSES}
    a = {c: att(c) for c in CLASSES}
    v = {c: a[c][:n_valid] for c in CLASSES}
    f = {c: a[c][n_valid:] for c in CLASSES}
    return vals, a, v, f


def run(vals, a, v, f, real=None, n_elig=N, reps=REPS):
    try:
        return evaluate_c6(vals, real_ok if real is None else real, n_elig,
                           attempted_ids_by_class=a, valid_ids_by_class=v,
                           failed_ids_by_class=f, replicates_per_sequence=reps)
    except Exception as e:          # a raise is itself a failure of the contract
        return (f"RAISED:{type(e).__name__}", [f"UNCAUGHT_EXCEPTION: {e}"], [])


def sem_rec(name, ok, detail, passes_when, fails_when):
    sem.append([name, "FALSIFIABLE_EMPIRICAL_TEST", "PASS" if ok else "FAIL", detail,
                passes_when, fails_when])


def neg_rec(name, category, verdict, reasons, token):
    ok = verdict == "FAIL" and any(token in r for r in reasons)
    hit = next((r for r in reasons if token in r), "")
    neg.append([name, category, "PASS" if ok else "FAIL", str(verdict), token,
                hit[:120] or "(expected reason code ABSENT)"])


# =====================================================================================
# Positive cases
# =====================================================================================
vals, a, v, f = baseline()
vals["REV"] = [10] * FULL
vr, why, _ = run(vals, a, v, f)
sem_rec("S1_complete_identity_accounting_passes", vr == "PASS", f"{vr} {why[:1]}",
        "attempted == valid U failed, disjoint, typed, separated -> PASS",
        "a fully correct control set is rejected, making every negative case meaningless")

vals, a, v, f = baseline(n_valid=80)
vr, why, _ = run(vals, a, v, f)
sem_rec("S2_partial_failures_reconcile", vr == "PASS", f"{vr} {why[:1]}",
        "80 valid + 4 failed = 84 attempted, disjoint, all ids known -> PASS",
        "correct partial-failure accounting is rejected")

vals, a, v, f = baseline()
vals["DI"] = []
v["DI"], f["DI"] = [], a["DI"]
vr, why, _ = run(vals, a, v, f)
sem_rec("S3_empty_class_fails", vr == "FAIL" and any("EMPTY_CONTROL_CLASS:DI" in r for r in why),
        f"{vr} {why[:1]}", "a class with zero valid replicates fails closed",
        "the gate proceeds on the surviving classes")

vals, a, v, f = baseline()
vals["REV"] = [0] * (FULL - 1) + [31]
vr, why, rep = run(vals, a, v, f)
pooled_p95 = [r for r in rep if r["control_class"] == "POOLED"][0]["p95"]
sem_rec("S4_single_class_violation_fails_despite_clean_pooled",
        vr == "FAIL" and any("SEPARATION_VIOLATED:REV" in r for r in why) and pooled_p95 == 0,
        f"{vr} pooled_p95={pooled_p95}",
        "one class touching the real minimum fails even when pooled is clean",
        "pooling hides a single-class violation")

vals, a, v, f = baseline()
vals["REV"] = [10] * FULL
vr, why, rep = run(vals, a, v, f)
rev_p95 = [r for r in rep if r["control_class"] == "REV"][0]["p95"]
sem_rec("S5_high_p95_reported_not_failed", vr == "PASS" and rev_p95 == 10,
        f"{vr} REV_p95={rev_p95}",
        "a class with p95>0 passes when separation holds; its p95 is reported",
        "p95 becomes a pass condition, making C6 unpassable on real data")

ok_canon = assert_canonical(CANONICAL_FAMILY_ORDER, CANONICAL_SEED) == CANONICAL_ORDER_HASH
sem_rec("S6_canonical_order_accepted", ok_canon,
        f"order={'|'.join(CANONICAL_FAMILY_ORDER)} seed={CANONICAL_SEED}",
        "the historical family order and seed are accepted",
        "the canonical pair is rejected, blocking every run")

caught = False
try:
    assert_canonical(tuple(sorted(CANONICAL_FAMILY_ORDER)), CANONICAL_SEED)
except SystemExit:
    caught = True
sem_rec("S7_reordered_family_list_fails_closed", caught, f"sorted order rejected={caught}",
        "an accidental sort of the family list fails closed",
        "a reorder passes silently, changing which di-shuffles fail")

caught_seed = False
try:
    assert_canonical(CANONICAL_FAMILY_ORDER, CANONICAL_SEED + 1)
except SystemExit:
    caught_seed = True
sem_rec("S8_seed_drift_fails_closed", caught_seed, f"seed drift rejected={caught_seed}",
        "a changed RNG seed fails closed", "a seed change passes silently")

# =====================================================================================
# Negative matrix - the 17 required container/identity cases, plus value cases
# =====================================================================================
def mutate(field, cls, value):
    vals, a, v, f = baseline()
    {"a": a, "v": v, "f": f}[field][cls] = value
    return run(vals, a, v, f)


CONTAINER_CASES = [
    ("T1_set_valued_valid_ids", "v", {f"MONO#r{i}" for i in range(FULL)},
     "INVALID_VALID_IDS"),
    ("T2_set_valued_failed_ids", "f", {"MONO#r0"}, "INVALID_FAILED_IDS"),
    ("T3_dict_valued_ids", "v", {f"MONO#r{i}": 1 for i in range(FULL)},
     "INVALID_VALID_IDS"),
    ("T4_generator_valued_ids", "v", (x for x in att("MONO")), "INVALID_VALID_IDS"),
    ("T5_none_ids", "v", None, "INVALID_VALID_IDS"),
    ("T6_integer_ids", "v", 84, "INVALID_VALID_IDS"),
    ("T7_scalar_string_ids", "v", "MONO#r0", "INVALID_VALID_IDS"),
    ("T8_bytes_ids", "v", b"MONO#r0", "INVALID_VALID_IDS"),
    ("T9_non_string_list_element", "v", ["MONO#r0", 7] + att("MONO")[2:],
     "INVALID_VALID_IDS"),
    ("T10_nested_container_element", "v", [["MONO#r0"]] + att("MONO")[1:],
     "INVALID_VALID_IDS"),
    ("T11_tuple_valued_ids", "v", tuple(att("MONO")), "INVALID_VALID_IDS"),
    ("T12_blank_id", "v", [" "] + att("MONO")[1:], "INVALID_VALID_IDS"),
]
for name, field, value, token in CONTAINER_CASES:
    vr, why, _ = mutate(field, "MONO", value)
    neg_rec(name, "container-type", vr, why, token)

# duplicate / overlap / membership
vr, why, _ = mutate("v", "MONO", [att("MONO")[0]] * FULL)
neg_rec("T13_duplicate_valid_id", "identity", vr, why, "INVALID_VALID_IDS")

vals, a, v, f = baseline(n_valid=80)
f["MONO"] = [a["MONO"][80]] * 4
vr, why, _ = run(vals, a, v, f)
neg_rec("T14_duplicate_failed_id", "identity", vr, why, "INVALID_FAILED_IDS")

vals, a, v, f = baseline(n_valid=80)
f["MONO"] = [a["MONO"][0]] + a["MONO"][81:]
vr, why, _ = run(vals, a, v, f)
neg_rec("T15_valid_failed_overlap", "identity", vr, why, "REPLICATE_IN_BOTH_SETS:MONO")

vals, a, v, f = baseline(n_valid=80)
f["MONO"] = a["MONO"][81:]           # one attempted id in neither set
vr, why, _ = run(vals, a, v, f)
neg_rec("T16_missing_attempted_id", "identity", vr, why, "UNACCOUNTED_ATTEMPTED_ID:MONO")

vals, a, v, f = baseline(n_valid=80)
v["MONO"] = v["MONO"][:-1] + ["MONO#UNKNOWN"]
vr, why, _ = run(vals, a, v, f)
neg_rec("T17_unknown_extra_id", "identity", vr, why, "UNKNOWN_VALID_ID:MONO")

vals, a, v, f = baseline(n_valid=80)
vals["MONO"] = [0] * 70              # values disagree with the valid-id list length
vr, why, _ = run(vals, a, v, f)
neg_rec("T18_count_list_mismatch", "identity", vr, why, "VALID_ID_COUNT_MISMATCH:MONO")

vals, a, v, f = baseline()
del v["MONO"]
vr, why, _ = run(vals, a, v, f)
neg_rec("T19_no_valid_id_list_supplied", "identity", vr, why, "INVALID_VALID_IDS")

vals, a, v, f = baseline(n_valid=80)
del f["MONO"]
vr, why, _ = run(vals, a, v, f)
neg_rec("T20_no_failed_id_list_supplied", "identity", vr, why, "INVALID_FAILED_IDS")

vals, a, v, f = baseline()
del a["MONO"]
vr, why, _ = run(vals, a, v, f)
neg_rec("T21_no_attempted_id_list_supplied", "identity", vr, why, "INVALID_ATTEMPTED_IDS")

vals, a, v, f = baseline()
a["MONO"] = att("MONO", FULL - 1)
vr, why, _ = run(vals, a, v, f)
neg_rec("T22_attempted_count_vs_design", "identity", vr, why,
        "ATTEMPTED_ID_COUNT_MISMATCH:MONO")

# whole-argument omission: the map itself is never supplied (not merely a missing class key)
def run_omitting(which):
    vals, a, v, f = baseline()
    kw = {"attempted_ids_by_class": a, "valid_ids_by_class": v, "failed_ids_by_class": f}
    kw.pop(which)
    try:
        return evaluate_c6(vals, real_ok, N, replicates_per_sequence=REPS, **kw)
    except Exception as e:
        return (f"RAISED:{type(e).__name__}", [f"UNCAUGHT_EXCEPTION: {e}"], [])


for nm, which in [("T24_whole_attempted_map_omitted", "attempted_ids_by_class"),
                  ("T25_whole_valid_map_omitted", "valid_ids_by_class"),
                  ("T26_whole_failed_map_omitted", "failed_ids_by_class")]:
    vr_, why_, _ = run_omitting(which)
    neg_rec(nm, "identity", vr_, why_, "IDENTITY_MAP_NOT_SUPPLIED")


class _ExplodingRepr:
    """An element whose __repr__ raises. The validator must still return a controlled FAIL."""
    def __repr__(self):
        raise RuntimeError("repr deliberately raises")


vals, a, v, f = baseline()
v["MONO"] = [_ExplodingRepr()] + a["MONO"][1:]
vr, why, _ = run(vals, a, v, f)
neg_rec("T27_element_with_raising_repr", "container-type", vr, why, "INVALID_VALID_IDS")

vals, a, v, f = baseline()
a["BOGUS"] = att("BOGUS", 1)
vr, why, _ = run(vals, a, v, f)
neg_rec("T23_undeclared_class_in_attempted", "identity", vr, why, "UNDECLARED_CONTROL_CLASS")

# value cases
VALUE_CASES = [
    ("V1_nan_in_controls", "MONO", [NAN] * FULL, real_ok, N, "INVALID_INPUT"),
    ("V2_inf_in_controls", "MONO", [INF] * FULL, real_ok, N, "INVALID_INPUT"),
    ("V3_negative_control_count", "MONO", [-5] * FULL, real_ok, N, "INVALID_INPUT"),
    ("V4_non_integer_count", "MONO", [0.5] * FULL, real_ok, N, "INVALID_INPUT"),
    ("V5_non_numeric_count", "MONO", ["x"] * FULL, real_ok, N, "INVALID_INPUT"),
]
for name, cls, values, real, ne, token in VALUE_CASES:
    vals, a, v, f = baseline()
    vals[cls] = values
    vr, why, _ = run(vals, a, v, f, real=real, n_elig=ne)
    neg_rec(name, "value", vr, why, token)

for name, real, ne, token in [
    ("V6_nan_in_real", [NAN] * 28, N, "INVALID_INPUT"),
    ("V7_negative_real", [-3] * 28, N, "INVALID_INPUT"),
    ("V8_n_real_exceeds_eligible", [140] * 9999, N, "IMPOSSIBLE_REAL_CARDINALITY"),
    ("V9_no_real_observations", [], N, "NO_NON_ABSTAINING_REAL"),
    ("V10_zero_denominator", real_ok, 0, "INVALID_DENOMINATOR"),
    ("V11_negative_denominator", real_ok, -28, "INVALID_DENOMINATOR"),
    ("V12_non_int_denominator", real_ok, 28.5, "INVALID_DENOMINATOR"),
    ("V13_nan_denominator", real_ok, NAN, "INVALID_DENOMINATOR"),
]:
    vals, a, v, f = baseline()
    vr, why, _ = run(vals, a, v, f, real=real, n_elig=ne)
    neg_rec(name, "value", vr, why, token)

vals, a, v, f = baseline()
vr, why, _ = run(vals, a, v, f, reps=0)
neg_rec("V14_invalid_design_parameter", "value", vr, why, "INVALID_DESIGN")

vr, why, _ = run("not a dict", a, v, f)
neg_rec("V15_controls_not_a_dict", "value", vr, why, "INVALID_CONTAINER")

vals, a, v, f = baseline()
vr, why, _ = run(vals, "nope", v, f)
neg_rec("V16_attempted_not_a_dict", "value", vr, why, "INVALID_CONTAINER")

with open(f"{TABLES}/c6_policy_tests.tsv", "w") as fh:
    fh.write("test\tclassification\tresult\tdetail\tpasses_when\tfails_when\n")
    for r in sem:
        fh.write("\t".join(r) + "\n")

with open(f"{TABLES}/c6_negative_test_matrix.tsv", "w") as fh:
    fh.write("# Every row is an invalid C6 state that MUST return an explicit FAIL with the\n")
    fh.write("# named reason code, and MUST NOT raise. A raise is recorded as RAISED:<type>.\n")
    fh.write("test\tcategory\tresult\tverdict_returned\texpected_reason_code\t"
             "reason_reported\n")
    for r in neg:
        fh.write("\t".join(r) + "\n")

for r in sem:
    print(f"  {r[2]:4s} {r[0]:48s} {r[3][:66]}")
for r in neg:
    print(f"  {r[2]:4s} {r[0]:48s} {r[3]:6s} {r[4]}")
bad = [r for r in sem if r[2] != "PASS"] + [r for r in neg if r[2] != "PASS"]
print(f"\n{len(sem)+len(neg)-len(bad)}/{len(sem)+len(neg)} passed "
      f"({len(sem)} semantic, {len(neg)} negative)")
sys.exit(1 if bad else 0)
