#!/usr/bin/env python3
"""REPAIR 6 - executable C6 / empty-control / di-shuffle-failure policy.

Implements control/C6_CONTROL_POLICY.md verbatim. Imported by the UG25 gate when it is
authorised; exercised now by control_policy_tests.py on synthetic inputs so the empty branch is
demonstrated before it can ever matter.
"""
CLASSES = ("MONO", "DI", "REV")
MIN_REPLICATE_FRACTION = 0.90
ABSOLUTE_MIN_REPLICATES = 20
REPLICATES_PER_SEQUENCE = 3


def pctl(vals, q):
    v = sorted(vals)
    return v[min(int(q * len(v)), len(v) - 1)] if v else None


def evaluate_c6(neg_by_class, real_mapped_non_abstaining, n_eligible,
                failed_ids_by_class=None):
    """Return (verdict, reasons, report_rows).

    `neg_by_class`: {class: [MAPPED-anchor count per valid replicate]}
    `real_mapped_non_abstaining`: [MAPPED-anchor count per non-abstaining real sequence]
    `n_eligible`: number of eligible holdout sequences (sets the expected replicate count)

    Fails closed on: a missing class, an empty class, a class below the replicate minimum, or
    any class whose maximum reaches the minimum real value. Pooled statistics are reported and
    are never a pass condition.
    """
    failed_ids_by_class = failed_ids_by_class or {}
    expected = REPLICATES_PER_SEQUENCE * n_eligible
    required = max(ABSOLUTE_MIN_REPLICATES, int(MIN_REPLICATE_FRACTION * expected + 0.5))
    reasons, rows = [], []

    min_real = min(real_mapped_non_abstaining) if real_mapped_non_abstaining else None
    if min_real is None:
        # C6 is undefined with no non-abstaining real sequence. Undefined is a FAIL, not a pass.
        reasons.append("NO_NON_ABSTAINING_REAL_SEQUENCES: C6 undefined -> FAIL CLOSED")

    pooled = []
    for cls in CLASSES:
        vals = list(neg_by_class.get(cls, []))
        pooled += vals
        n_failed = len(failed_ids_by_class.get(cls, []))
        rows.append(dict(control_class=cls, n_attempted=expected, n_valid=len(vals),
                         n_failed=n_failed,
                         max=max(vals) if vals else None,
                         mean=(sum(vals) / len(vals)) if vals else None,
                         p95=pctl(vals, 0.95),
                         n_with_any_mapped=sum(1 for v in vals if v > 0)))
        if cls not in neg_by_class:
            reasons.append(f"MISSING_CONTROL_CLASS:{cls} -> FAIL CLOSED")
            continue
        if not vals:
            reasons.append(f"EMPTY_CONTROL_CLASS:{cls} (0 valid replicates) -> FAIL CLOSED")
            continue
        if len(vals) < required:
            reasons.append(f"INSUFFICIENT_REPLICATES:{cls} {len(vals)} < {required} "
                           f"(expected {expected}, {n_failed} generation failure(s)) "
                           f"-> FAIL CLOSED")
        if min_real is not None and max(vals) >= min_real:
            reasons.append(f"SEPARATION_VIOLATED:{cls} max {max(vals)} >= min real {min_real}")

    rows.append(dict(control_class="POOLED", n_attempted=expected * len(CLASSES),
                     n_valid=len(pooled), n_failed=sum(len(v) for v in
                                                       failed_ids_by_class.values()),
                     max=max(pooled) if pooled else None,
                     mean=(sum(pooled) / len(pooled)) if pooled else None,
                     p95=pctl(pooled, 0.95),
                     n_with_any_mapped=sum(1 for v in pooled if v > 0)))

    return ("PASS" if not reasons else "FAIL"), reasons, rows


def write_control_report(path, rows, verdict, reasons, failed_ids_by_class=None):
    failed_ids_by_class = failed_ids_by_class or {}
    with open(path, "w") as f:
        f.write(f"# C6 verdict: {verdict}\n")
        for r in reasons:
            f.write(f"# reason: {r}\n")
        for cls, ids in sorted(failed_ids_by_class.items()):
            if ids:
                f.write(f"# {cls} generation failures ({len(ids)}), NOT replaced: "
                        f"{','.join(sorted(ids))}\n")
        f.write("# p95 is REPORTED, never a pass condition (C6_CONTROL_POLICY.md s3)\n")
        f.write("control_class\tn_attempted\tn_valid\tn_failed\tmax\tmean\tp95\t"
                "n_with_any_mapped\n")
        for r in rows:
            f.write(f"{r['control_class']}\t{r['n_attempted']}\t{r['n_valid']}\t"
                    f"{r['n_failed']}\t{r['max']}\t"
                    f"{'' if r['mean'] is None else format(r['mean'], '.3f')}\t"
                    f"{r['p95']}\t{r['n_with_any_mapped']}\n")
