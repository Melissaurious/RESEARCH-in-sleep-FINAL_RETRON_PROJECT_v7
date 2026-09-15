#!/usr/bin/env python3
"""c03 - positive controls and internal-consistency checks over the landed tables.

Every control states what it expects BEFORE it runs, and `--seed-bad` corrupts one expectation so
the suite can be watched failing (a control suite that has never failed is untested).
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

import common as C

SCRIPT = "c03_controls.py"


def modes_rule(v: np.ndarray) -> int:
    """The declared mode-count rule, re-implemented here so the control tests the RULE, not the
    function it was copied from (a01 owns the production copy)."""
    lo, hi = np.percentile(v, [1, 99])
    if hi - lo < 20:
        return 1
    b = np.arange(lo, hi + 10, 10)
    h, _ = np.histogram(v, bins=b)
    if len(h) < 5:
        return 1
    k = np.convolve(h, np.ones(3) / 3, mode="same")
    peaks = [i for i in range(1, len(k) - 1)
             if k[i] > k[i - 1] and k[i] >= k[i + 1] and k[i] >= 0.1 * k.max()]
    kept = []
    for i in peaks:
        if all(k[min(i, j):max(i, j) + 1].min() <= 0.6 * min(k[i], k[j]) for j in kept):
            kept.append(i)
    return max(1, len(kept))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-bad", action="store_true",
                    help="corrupt one expectation; the suite MUST then fail")
    a = ap.parse_args()
    C.log("== c03 positive controls")
    rows = []

    def check(name, expected, observed, tol=0.0):
        try:
            ok = abs(float(expected) - float(observed)) <= tol
        except (TypeError, ValueError):
            ok = expected == observed
        rows.append(dict(control=name, expected=expected, observed=observed, tolerance=tol,
                         verdict="PASS" if ok else "FAIL"))

    # ---- 1. the estimator: Wilson interval on values with a known answer ---------------------
    lo, hi = C.wilson(50, 100)
    check("Wilson 95% lower bound for 50/100 (Newcombe 1998: 0.4038)", 0.4038, float(lo), 0.0002)
    check("Wilson 95% upper bound for 50/100 (Newcombe 1998: 0.5962)", 0.5962, float(hi), 0.0002)
    lo0, hi0 = C.wilson(0, 100)
    check("Wilson interval for 0/100 starts at 0", 0.0, float(lo0), 1e-12)
    check("Wilson 95% upper bound for 0/100 (Newcombe 1998: 0.0370)", 0.0370, float(hi0), 0.0002)
    lo1, hi1 = C.wilson(1, 10**6)
    check("Wilson interval narrows with n: width at 1/1,000,000 < 0.0001",
          True, bool((hi1 - lo1) < 1e-4))

    # ---- 2. the declared mode rule fires on a known bimodal sample --------------------------
    rng = np.random.default_rng(C.SEED)
    bimodal = np.concatenate([rng.normal(250, 15, 4000), rng.normal(600, 20, 4000)])
    unimodal = rng.normal(400, 30, 8000)
    check("mode rule returns 2 on a constructed bimodal length sample", 2, modes_rule(bimodal))
    check("mode rule returns 1 on a constructed unimodal length sample", 1, modes_rule(unimodal))

    # ---- 3. partitions: every classification covers its population exactly ------------------
    cc = C.read_table("t12_configuration_classes")
    check("configuration classes partition the CANONICAL placements",
          int(cc.n_placements_total.iloc[0]), int(cc.n_placements.sum()))
    ups = C.read_table("t02_exact_rt_database_upset")
    lad = C.landed("dbchar_g2_canonical_units", "g2_unit_ladder.tsv").set_index("unit")
    check("database-membership classes partition the exact RTs",
          int(lad.loc["exact_rt", "n"]), int(ups.n_exact_rt.sum()))
    t18 = C.read_table("t18_tool_combination_carriage")
    rec_rows = t18[t18.view_unit == "distinct record"]
    g6 = C.landed("dbchar_g6_tool_calls", "g6_tool_matrix_retron.tsv")
    check("tool combinations partition the Retron records",
          int(g6.n_records.sum()), int(rec_rows.n.sum()))
    pl_rows = t18[t18.view_unit.str.startswith("physical locus")]
    check("tool combinations partition the Retron physical loci", 563701, int(pl_rows.n.sum()))
    t40 = C.read_table("t40_inspectability")
    check("inspectability tiers partition the distinct records",
          int(lad.loc["distinct_raw_record", "n"]), int(t40.n_records.sum()))
    t23 = C.read_table("t23_zero_call_by_database")
    check("zero/1/2/>2 classes partition the Retron physical loci",
          563701, int((t23.n_0 + t23.n_1 + t23.n_2 + t23.n_gt2).sum()))

    # ---- 4. the funnel is monotone and its removals reconcile -------------------------------
    fun = C.read_table("t01_unit_funnel")
    check("the unit funnel is monotone non-increasing", True,
          bool((fun.n.diff().dropna() <= 0).all()))
    removed_ok = True
    for i in range(1, len(fun)):
        if int(fun.n.iloc[i - 1]) - int(fun.n.iloc[i]) != int(fun.n_removed.iloc[i]):
            removed_ok = False
    check("each funnel step's n_removed equals the difference between its two levels",
          True, removed_ok)

    # ---- 5. every landed rate has a Wilson interval that contains it, inside [0,100] --------
    bad_ci = []
    for p in sorted(C.T.glob("*.tsv")):
        df = pd.read_csv(p, sep="\t")
        for col in [c for c in df.columns if c.endswith("_ci_lo")]:
            base = col[:-6]
            hi_col = f"{base}_ci_hi"
            if base not in df.columns or hi_col not in df.columns:
                continue
            sub = df[[base, col, hi_col]].dropna()
            inside = (sub[col] <= sub[base] + 1e-9) & (sub[base] <= sub[hi_col] + 1e-9)
            bounded = sub[col].between(-1e-9, 100 + 1e-9) & sub[hi_col].between(-1e-9, 100 + 1e-9)
            if not bool(inside.all() and bounded.all()):
                bad_ci.append(f"{p.name}:{base}")
    check("every landed Wilson interval contains its point estimate and lies in [0,100]",
          0, len(bad_ci))

    # ---- 6. prevalence denominators add up ---------------------------------------------------
    t34 = C.read_table("t34_gtdb_prevalence_by_rank")
    ph = t34[t34["rank"] == "phylum"]
    check("GTDB phylum rows sum to the catalogue's genome count", 715230,
          int(ph.n_sampled_genomes.sum()))
    check("GTDB phylum RT-positive rows sum to the corpus's gtdb_bacteria genome count",
          299306, int(ph.n_rt_positive_genomes.sum()))

    # ---- 7. a rate can move: the carriage gradient is not flat by construction ---------------
    t24 = C.read_table("t24_carriage_by_upstream_context")
    check("carriage against upstream context spans more than 20 percentage points", True,
          bool((t24.pct_with_ncrna.max() - t24.pct_with_ncrna.min()) > 20))

    # ---- 8. the zero-ncRNA class is not an artefact of the canonical filter ------------------
    t42 = C.read_table("t42_definition_differences")
    check("the three coverage rules differ by less than 1% of Retron loci", True,
          bool(abs(int(t42.n_a.iloc[0]) - int(t42.n_c.iloc[0])) / int(t42.n_loci.iloc[0]) < 0.01))

    if a.seed_bad:
        rows.append(dict(control="SEEDED-BAD: an expectation that must fail", expected=1,
                         observed=2, tolerance=0.0, verdict="FAIL"))

    t = pd.DataFrame(rows)
    C.write_table("t44_controls", t, "controls",
                  "each row is one declared expectation checked against the landed tables",
                  SCRIPT, estimate="n/a - controls, not measurements")
    n_fail = int((t.verdict == "FAIL").sum())
    C.log(f"   {len(t)} controls, {n_fail} failed")
    if n_fail:
        print(t[t.verdict == "FAIL"].to_string(index=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
