#!/usr/bin/env python
"""embed-g0/a01 - Phase-0 audit of the proposed RT-ncRNA embedding universe.

Reads ONLY the read-only canonical derived layer. Writes TSV tables. No GPU, no writes
outside ARIS_OUTPUT. Every number the Phase-0 report quotes is produced here.

Proposed universe: the registered eligible exact-pair resource
`data/derived/rt_ncrna_exact_pairs_v1.parquet` (PAIR-ELIG). T1/T2/T3/T4 are attached as
pair-level views, never as the embedding population.

Env: /home/borg/miniconda3/envs/retron_tradicional/bin/python  (pyarrow + pandas; no duckdb)
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

D = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
OUT = Path(__file__).resolve().parents[1] / "tables"
KEY = ["rt_seq_hash", "nc_seq_hash"]
# Declared from the workbench handover; asserted, never trusted.
EXPECT = {"placements_all": 346_722, "placements_canonical": 344_154, "pair_elig": 30_924,
          "pair_canon": 30_427, "T1": 30_287, "T2": 25_673, "T3": 23_680,
          "u_rt": 29_192, "u_nc": 16_458}


def check(name, got, want):
    if got != want:
        raise AssertionError(f"FAIL {name}: got {got!r}, expected {want!r}")
    print(f"  ok  {name}: {got:,}")


def w(name, df):
    p = OUT / name
    df.to_csv(p, sep="\t", index=False)
    print(f"  wrote {p.name}  ({len(df)} rows)")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["rt_seq_hash", "nc_seq_hash", "nc_seq_len", "detection_model", "file_label",
            "canonical", "geometry_eligible", "same_strand", "direction", "n_cds_between",
            "signed_distance_bp", "evalue", "source_file", "line_no", "ncrna_idx",
            "source_database", "genome_id_norm", "taxonomy_system", "tax_species",
            "physical_locus_key", "locus_key", "nc_strand", "orientation_corrected",
            "rt_at_window_edge", "rt_in_window", "bt_status"]
    p = pq.read_table(D / "rt_ncrna_pairs_v1.parquet", columns=cols).to_pandas()
    reg = pq.read_table(D / "rt_ncrna_exact_pairs_v1.parquet").to_pandas()
    e = p[p.geometry_eligible]

    print("[1] population reproduction")
    check("placements_all", len(p), EXPECT["placements_all"])
    check("placements_canonical", int(p.canonical.sum()), EXPECT["placements_canonical"])
    check("pair_elig (registered resource)", len(reg), EXPECT["pair_elig"])
    check("pair_elig == distinct pairs over geometry_eligible placements",
          e.groupby(KEY).ngroups, EXPECT["pair_elig"])
    check("u_rt", reg.rt_seq_hash.nunique(), EXPECT["u_rt"])
    check("u_nc", reg.nc_seq_hash.nunique(), EXPECT["u_nc"])

    c = p[p.canonical]
    cr = c[c.file_label == "Retron"]
    T1 = cr.drop_duplicates(KEY)
    T2 = cr[cr.same_strand & (cr.direction != "downstream") & (cr.n_cds_between == 0)
            & (cr.signed_distance_bp.abs() <= 200)].drop_duplicates(KEY)
    T3 = cr[cr.same_strand & (cr.direction != "downstream") & (cr.n_cds_between == 0)
            & (cr.signed_distance_bp.abs() <= 200) & (cr.evalue <= 1e-5)].drop_duplicates(KEY)
    check("pair_canon", c.groupby(KEY).ngroups, EXPECT["pair_canon"])
    check("T1", len(T1), EXPECT["T1"])
    check("T2", len(T2), EXPECT["T2"])
    check("T3", len(T3), EXPECT["T3"])

    rec = pq.read_table(D / "rt_ncrna_exact_pair_recurrence_v1.parquet").to_pandas()
    T4 = T3.merge(rec[rec.recurrence_class.isin(
        ["multiple_species", "one_species_multiple_genomes"])][KEY], on=KEY)
    print(f"  note T4 (T3 & recurrent) = {len(T4):,}")

    # the universe is a strict superset of every view
    t1s = set(map(tuple, T1[KEY].values))
    regs = set(map(tuple, reg[KEY].values))
    check("T1 \\ PAIR-ELIG (must be empty)", len(t1s - regs), 0)
    print(f"  note PAIR-ELIG \\ T1 = {len(regs - t1s):,} "
          f"({len(regs) - c.groupby(KEY).ngroups} dedup-removed + "
          f"{c.groupby(KEY).ngroups - len(T1)} non-Retron canonical)")

    views = pd.DataFrame([
        ["PAIR-ELIG (proposed embedding universe)", len(reg), reg.rt_seq_hash.nunique(), reg.nc_seq_hash.nunique()],
        ["PAIR-CANON", c.groupby(KEY).ngroups, c.rt_seq_hash.nunique(), c.nc_seq_hash.nunique()],
        ["T1 observed", len(T1), T1.rt_seq_hash.nunique(), T1.nc_seq_hash.nunique()],
        ["T2 architecture", len(T2), T2.rt_seq_hash.nunique(), T2.nc_seq_hash.nunique()],
        ["T3 high-confidence", len(T3), T3.rt_seq_hash.nunique(), T3.nc_seq_hash.nunique()],
        ["T4 independently recurrent", len(T4), T4.rt_seq_hash.nunique(), T4.nc_seq_hash.nunique()],
    ], columns=["view", "pairs", "unique_rt", "unique_ncrna"])
    w("g0_views.tsv", views)

    print("\n[2] sequence grain")
    RT = sorted(reg.rt_seq_hash.unique())
    NC = sorted(reg.nc_seq_hash.unique())
    rx = pq.read_table(D / "rt_exact_v1.parquet",
                       columns=["rt_seq_hash", "rt_aa_len", "wellformed"]).to_pandas()
    m = rx.set_index("rt_seq_hash").reindex(RT)
    check("RT hashes resolvable in rt_exact_v1", int(m.rt_aa_len.notna().sum()), len(RT))
    check("RT wellformed", int(m.wellformed.fillna(False).sum()), len(RT))
    L = m.rt_aa_len.astype(int)

    nl = e.groupby("nc_seq_hash").nc_seq_len.agg(["max", "nunique"]).reindex(NC)
    check("nc hashes with a single length (hash-length consistency)",
          int((nl["nunique"] == 1).sum()), len(NC))
    N = nl["max"].astype(int)
    check("empty nc hash absent", int("" in set(NC)), 0)
    check("all eligible placements orientation_corrected",
          int(e.orientation_corrected.all()), 1)
    check("nc hashes with conflicting orientation state",
          int((e.groupby("nc_seq_hash").orientation_corrected.nunique() > 1).sum()), 0)

    def dist(tag, v, unit):
        return dict(population=tag, unit=unit, n=len(v), total=int(v.sum()), min=int(v.min()),
                    p25=int(v.quantile(.25)), median=int(v.median()), mean=round(float(v.mean()), 1),
                    p75=int(v.quantile(.75)), p99=int(v.quantile(.99)), max=int(v.max()))
    w("g0_length_distributions.tsv", pd.DataFrame([
        dist("unique exact RT", L, "aa"), dist("unique exact oriented ncRNA", N, "nt")]))

    strata = pd.DataFrame([
        ["RT < 250 aa (excluded by the g5a Stage-2 eligibility rule)", int((L < 250).sum()), len(RT)],
        ["RT > 1024 aa", int((L > 1024).sum()), len(RT)],
        ["RT > 2048 aa", int((L > 2048).sum()), len(RT)],
        ["ncRNA > 512 nt", int((N > 512).sum()), len(NC)],
    ], columns=["stratum", "numerator", "denominator"])
    w("g0_length_strata.tsv", strata)

    print("\n[3] multiplicity")
    dr = reg.groupby("rt_seq_hash").nc_seq_hash.nunique()
    dn = reg.groupby("nc_seq_hash").rt_seq_hash.nunique()
    w("g0_multiplicity.tsv", pd.DataFrame([
        ["placements per pair", reg.n_placements.median(), round(reg.n_placements.mean(), 2), reg.n_placements.max()],
        ["ncRNA partners per RT", dr.median(), round(dr.mean(), 3), dr.max()],
        ["RT partners per ncRNA", dn.median(), round(dn.mean(), 3), dn.max()],
    ], columns=["quantity", "median", "mean", "max"]))
    print(f"  RT degree==1: {int((dr==1).sum()):,} ({100*(dr==1).mean():.2f}%)   "
          f"ncRNA degree==1: {int((dn==1).sum()):,} ({100*(dn==1).mean():.2f}%)")
    w("g0_recurrence_class.tsv",
      rec.recurrence_class.value_counts().rename_axis("recurrence_class").reset_index(name="pairs"))

    print("\n[4] nuisance structure")
    pm = e.groupby(KEY).detection_model.agg(lambda s: s.mode().iat[0]).rename("model")
    fam = pq.read_table(D / "rt_family_baseline_v1.parquet",
                        columns=["rt_seq_hash", "family_label", "completeness_class"]).to_pandas()
    P = reg.merge(pm, on=KEY).merge(fam, on="rt_seq_hash", how="left")
    w("g0_detection_model.tsv",
      P.model.value_counts().rename_axis("detection_model").reset_index(name="pairs"))
    w("g0_rt_family.tsv",
      P.family_label.value_counts().rename_axis("family_label").reset_index(name="pairs"))
    w("g0_completeness.tsv",
      P.completeness_class.value_counts().rename_axis("completeness_class").reset_index(name="pairs"))

    print("\n[5] split keys over the universe")
    w("g0_split_keys.tsv", pd.DataFrame([
        ["source_database", e.source_database.nunique()],
        ["taxonomy_system", e.taxonomy_system.nunique()],
        ["tax_species (NOT poolable across systems)", e.tax_species.nunique()],
        ["genome_id_norm", e.genome_id_norm.nunique()],
        ["locus_key", e.locus_key.nunique()],
        ["physical_locus_key", e.physical_locus_key.nunique()],
        ["rt_seq_hash (leakiest - see handover 5)", len(RT)],
        ["nc_seq_hash", len(NC)],
    ], columns=["grouping_key", "distinct"]))

    print("\n[6] ncRNA sequence recoverability")
    # nc sequences are NOT in the derived layer; they must come from the raw corpus.
    # every eligible placement carries (source_file, line_no, ncrna_idx) -> exact provenance.
    src = e.groupby("source_file").nc_seq_hash.nunique().sort_values(ascending=False)
    first = e.sort_values(["source_file", "line_no", "ncrna_idx"]).drop_duplicates("nc_seq_hash")
    check("every nc hash has a raw-corpus address", len(first), len(NC))
    w("g0_ncrna_source_files.tsv", src.rename_axis("source_file").reset_index(name="unique_nc_hashes"))
    w("g0_ncrna_fetch_plan.tsv",
      first[["nc_seq_hash", "source_file", "line_no", "ncrna_idx", "nc_seq_len"]])

    print("\n[7] storage, at fp16")
    def gb(n, d): return round(n * d * 2 / 1e9, 4)
    w("g0_storage.tsv", pd.DataFrame([
        ["ESM-C 300M", "pooled", len(RT), 960, gb(len(RT), 960)],
        ["ESM-C 300M", "per-residue", int(L.sum()), 960, gb(int(L.sum()), 960)],
        ["RiNALMo giga-v1", "pooled", len(NC), 1280, gb(len(NC), 1280)],
        ["RiNALMo giga-v1", "per-nucleotide", int(N.sum()), 1280, gb(int(N.sum()), 1280)],
    ], columns=["model", "level", "rows", "dim", "gb_fp16"]))

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
