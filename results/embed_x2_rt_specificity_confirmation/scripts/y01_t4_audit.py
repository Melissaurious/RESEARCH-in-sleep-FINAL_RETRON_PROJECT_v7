#!/usr/bin/env python
"""embed_x2/y01 - audit exactly what T4 is, BEFORE any X2 computation.

T4 is the caveat that motivates X2, so what it contains must be documented before any X2
number exists. Nothing here is changed afterwards.
"""
from __future__ import annotations
import gzip, json, sys
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[1]
OUT = TASK / "tables"
SPLIT = ROOT / "results" / "embed_g2b_frozen_split"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
KEY = ["rt_seq_hash", "nc_seq_hash"]


def neff(s):
    s = np.asarray(s, float)
    return float((s.sum() ** 2) / (s ** 2).sum()) if len(s) else 0.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    asg = pd.read_csv(gzip.open(SPLIT / "tables" / "split_assignment.tsv.gz"), sep="\t")
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet").to_pandas()
    rec = pq.read_table(CANON / "rt_ncrna_exact_pair_recurrence_v1.parquet",
                        columns=KEY + ["recurrence_class"]).to_pandas()
    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet",
                      columns=KEY + ["geometry_eligible", "detection_model",
                                     "physical_locus_key"]).to_pandas()
    e = p[p.geometry_eligible]
    pm = e.groupby(KEY).detection_model.agg(lambda s: s.mode().iat[0]).rename("retron_type")
    d = (asg.merge(reg, on=KEY, how="left").merge(rec, on=KEY, how="left")
            .merge(pm, on=KEY, how="left"))
    te = d[d.fold == "test"]
    t4 = te[te.T4 == 1]

    print("[1] tier definitions (from dbchar_g3, restated; not redefined here)")
    defs = [
        ("T1", "observed", "canonical, non-redundant, Retron file label", 30287),
        ("T2", "architecture",
         "T1 + same strand + not downstream + no intervening CDS + |gap| <= 200 bp", 25673),
        ("T3", "high-confidence", "T2 + covariance-model hit E <= 1e-5", 23680),
        ("T4", "independently recurrent",
         "T3 + recurrence_class in {multiple_species, one_species_multiple_genomes}", 7476),
    ]
    for t, n, r, c in defs:
        print(f"    {t} {n:<24} {r}   (universe-wide {c:,} pairs)")
    print("""
    WHY T4 IS THE MOST INDEPENDENT EVIDENCE. T1-T3 tighten ARCHITECTURAL and DETECTION
    criteria but say nothing about whether a pair was observed more than once as a genuine
    event. A pair can recur in T3 simply because one physical locus was deposited under
    several accessions - repeated DEPOSITION, not repeated observation. T4 additionally
    requires recurrence across genomes or species, so a repeat is a repeated EVENT. It is the
    tier least inflated by database redundancy, which is why an unresolved T4 result is the
    binding caveat on X1.""")

    print("[2] T4 inside the frozen TEST fold")
    comps = t4.component_id.value_counts()
    rows = dict(
        test_pairs=len(t4),
        independent_components=int(t4.component_id.nunique()),
        n_eff=round(neff(comps.values), 2),
        unique_rt=int(t4.rt_seq_hash.nunique()),
        unique_ncrna=int(t4.nc_seq_hash.nunique()),
        rt_clusters=int(t4.rt_cluster.nunique()),
        ncrna_clusters=int(t4.nc_cluster.nunique()),
        retron_types=int(t4.retron_type.nunique()),
        largest_component_pairs=int(comps.max()),
        largest_component_share=round(float(comps.max() / comps.sum()), 4),
        median_component_pairs=int(comps.median()),
        singleton_components=int((comps == 1).sum()),
    )
    for k, v in rows.items():
        print(f"    {k:<28} {v}")

    print("\n[3] deposition multiplicity inside T4 (what T4 is meant to control)")
    dep = dict(
        median_placements_per_pair=float(t4.n_placements.median()),
        mean_placements_per_pair=round(float(t4.n_placements.mean()), 2),
        max_placements_per_pair=int(t4.n_placements.max()),
        median_physical_loci=float(t4.n_physical_loci.median()),
        median_genomes=float(t4.n_genomes.median()),
        pairs_with_1_physical_locus=int((t4.n_physical_loci == 1).sum()),
        pairs_multiple_species=int((t4.recurrence_class == "multiple_species").sum()),
        pairs_one_species_multi_genome=int(
            (t4.recurrence_class == "one_species_multiple_genomes").sum()),
    )
    for k, v in dep.items():
        print(f"    {k:<34} {v}")

    print("\n[4] repeated exact sequences / loci WITHIN a component")
    rep_rt = t4.groupby("component_id").rt_seq_hash.apply(lambda s: s.duplicated().any())
    rep_nc = t4.groupby("component_id").nc_seq_hash.apply(lambda s: s.duplicated().any())
    loc = e.groupby(KEY).physical_locus_key.nunique().rename("n_distinct_loci")
    t4l = t4.merge(loc, on=KEY, how="left")
    rep = dict(
        components_with_repeated_exact_RT=int(rep_rt.sum()),
        components_with_repeated_exact_ncRNA=int(rep_nc.sum()),
        components_with_either=int((rep_rt | rep_nc).sum()),
        pairs_spanning_multiple_physical_loci=int((t4l.n_distinct_loci > 1).sum()),
    )
    for k, v in rep.items():
        den = f"{len(comps)} components" if k.startswith("components") else f"{len(t4)} pairs"
        print(f"    {k:<42} {v} / {den}")

    print("\n[5] retron-type composition of T4 in test")
    tc = t4.retron_type.value_counts()
    tcomp = t4.groupby("retron_type").component_id.nunique()
    comp_tbl = (pd.DataFrame({"pairs": tc, "components": tcomp})
                .fillna(0).astype(int).sort_values("pairs", ascending=False))
    print(comp_tbl.head(10).to_string())
    print(f"    ... {len(comp_tbl)} types total")

    print("\n[6] is 83 the correct inferential denominator for the X1 T4 comparison?")
    n_comp = int(t4.component_id.nunique())
    ok = n_comp == 83
    print(f"    components carrying >=1 T4 test pair : {n_comp}")
    print(f"    X1 reported n_components for T4      : 83")
    print(f"    {'CONFIRMED' if ok else 'MISMATCH'} - the denominator is components, "
          f"not the {len(t4):,} pairs")
    print(f"    n_eff over those components: {rows['n_eff']}; the largest holds "
          f"{100*rows['largest_component_share']:.1f}% of T4 test pairs")

    audit = {"tier_definitions": {t: r for t, _, r, _ in defs}, **rows, **dep, **rep,
             "denominator_confirmed_83": bool(ok),
             "note": ("T4 is a STRATUM of the frozen test fold, not a separate split; its "
                      "components are a subset of the 357 test components.")}
    (OUT / "T4_AUDIT.json").write_text(json.dumps(audit, indent=2, default=str) + "\n")
    flat = {k: (json.dumps(v) if isinstance(v, dict) else v) for k, v in audit.items()}
    pd.Series(flat, name="value").rename_axis("field").to_csv(OUT / "T4_AUDIT.tsv", sep="\t")
    comp_tbl.to_csv(OUT / "T4_type_composition.tsv", sep="\t")
    print("\nwrote T4_AUDIT.tsv, T4_AUDIT.json, T4_type_composition.tsv")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
