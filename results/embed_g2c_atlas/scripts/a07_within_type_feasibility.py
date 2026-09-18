#!/usr/bin/env python
"""embed_g2/a07 - FEASIBILITY AUDIT for a future within-retron-type compatibility experiment.

AUDIT ONLY. Nothing is trained, no model output is inspected, no candidate set is scored. This
script answers one question per retron type: *could* a partner-specific test be run inside that
type with enough independent data to support component-level inference?

It exists because embed_g2 separated two levels of signal and established only the first:
  level 1  shared RT-ncRNA organization at retron-type / system-class level  -- SUPPORTED
  level 2  individual RT-ncRNA partner specificity within that organization  -- NOT ESTABLISHED
A within-type experiment is the design that could address level 2, because restricting
candidates to one retron type removes type-associated structure by construction rather than
relying on it being controlled away.

FEASIBILITY CRITERIA, declared here and applied uniformly (not tuned to any outcome):
  C1  candidate pool      >= 50 unique ncRNAs of that type, so a 50-way retrieval task exists
  C2  independent units   >= 30 relatedness components carrying that type's pairs
  C3  effective units     n_eff >= 10 over those components
  C4  confirmatory depth  >= 100 T3 pairs of that type
All four must hold. A type failing any one is reported as infeasible with the reason named.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
MIN_POOL, MIN_COMPS, MIN_NEFF, MIN_T3 = 50, 30, 10.0, 100


def neff(s):
    s = np.asarray(s, float)
    return float((s.sum() ** 2) / (s ** 2).sum()) if len(s) else 0.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(W / "analysis_pairs.parquet")
    rows = []
    for t, g in df.groupby("detection_model"):
        comps = g.component_id.value_counts()
        pool = g.nc_seq_hash.nunique()
        # a within-type query is usable only if the pool can supply 49 decoys that are NOT
        # observed partners of that RT; the binding constraint is the pool size minus the
        # query RT's own observed partners
        max_partners = g.groupby("rt_seq_hash").nc_seq_hash.nunique().max()
        rows.append(dict(
            retron_type=t,
            pairs=len(g), unique_rt=g.rt_seq_hash.nunique(), unique_ncrna=pool,
            components=len(comps), n_eff=round(neff(comps.values), 1),
            largest_comp_frac=round(float(comps.max() / comps.sum()), 3),
            test_pairs=int((g.fold == "test").sum()),
            test_components=int(g[g.fold == "test"].component_id.nunique()),
            test_n_eff=round(neff(g[g.fold == "test"].component_id.value_counts().values), 1),
            T3=int(g.T3.sum()), T4=int(g.T4.sum()),
            T3_test=int(g[(g.fold == "test")].T3.sum()),
            within_type_pool=pool, max_observed_partners_per_rt=int(max_partners),
            usable_pool_worst_case=int(pool - max_partners),
            rt_clusters=g.rt_cluster.nunique(), nc_clusters=g.nc_cluster.nunique(),
            species=int(g.tax_species_ncbi.nunique()),
            species_coverage=round(float(g.tax_species_ncbi.notna().mean()), 3),
        ))
    f = pd.DataFrame(rows).sort_values("pairs", ascending=False)

    f["C1_pool>=50"] = f.usable_pool_worst_case >= MIN_POOL
    f["C2_components>=30"] = f.components >= MIN_COMPS
    f["C3_neff>=10"] = f.n_eff >= MIN_NEFF
    f["C4_T3>=100"] = f.T3 >= MIN_T3
    f["FEASIBLE"] = f[["C1_pool>=50", "C2_components>=30", "C3_neff>=10", "C4_T3>=100"]].all(axis=1)
    f["blocking"] = [", ".join(c.split("_")[0] for c in
                               ("C1_pool>=50", "C2_components>=30", "C3_neff>=10", "C4_T3>=100")
                               if not r[c]) or "-"
                     for _, r in f.iterrows()]
    f.to_csv(OUT / "g2a_within_type_feasibility.tsv", sep="\t", index=False)

    cols = ["retron_type", "pairs", "unique_rt", "unique_ncrna", "components", "n_eff",
            "test_components", "test_n_eff", "T3", "T4", "usable_pool_worst_case",
            "rt_clusters", "nc_clusters", "species", "FEASIBLE", "blocking"]
    print(f.to_string(index=False, columns=cols))
    ok = f[f.FEASIBLE]
    print(f"\nfeasible retron types: {len(ok)} of {len(f)}")
    if len(ok):
        print(f"  {', '.join(ok.retron_type)}")
        print(f"  combined: {int(ok.pairs.sum()):,} pairs, {int(ok.components.sum()):,} components, "
              f"{int(ok.T3.sum()):,} T3, {int(ok.T4.sum()):,} T4")
    else:
        print("  NONE - no retron type has enough independent data for a partner-specific test")
    print(f"\ncriteria: pool>={MIN_POOL}, components>={MIN_COMPS}, n_eff>={MIN_NEFF}, "
          f"T3>={MIN_T3}; all four required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
