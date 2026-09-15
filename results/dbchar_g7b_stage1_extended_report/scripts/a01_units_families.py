#!/usr/bin/env python3
"""a01 - sections 1-3: the unit funnel and redundancy structure, family composition, RT length.

Reads the registered Stage-1 derived datasets and landed g1-g6 tables. Writes tables only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

SCRIPT = "a01_units_families.py"


def major_families(fb: pd.DataFrame) -> list[str]:
    s = fb[fb.view == "V-RT-SINGLE"].family_label.value_counts()
    return list(s.head(C.N_MAJOR_FAMILIES).index)


def fam_bucket(labels: pd.Series, major: list[str]) -> pd.Series:
    out = labels.where(labels.isin(major), "other")
    return out.mask(labels == "MULTI", "MULTI")


def main() -> None:
    C.log("== a01 sections 1-3")
    rec = C.records()
    fb = C.derived("rt_family_baseline_v1", ["rt_seq_hash", "rt_aa_len", "family_label", "view",
                                             "completeness_class", "n_loci", "n_genomes",
                                             "n_species", "n_databases"])
    ex = C.derived("rt_exact_v1", ["rt_seq_hash", "rt_aa_len", "n_records", "n_loci",
                                   "n_physical_loci", "n_genomes", "n_source_databases"])
    major = major_families(fb)
    C.log(f"   major families: {', '.join(major)}")

    # ---------------------------------------------------------------- T01 the unit funnel
    ladder = C.landed("dbchar_g2_canonical_units", "g2_unit_ladder.tsv")
    ladder = ladder.set_index("unit")

    def lv(u):
        return int(ladder.loc[u, "n"])

    dup = C.landed("dbchar_g2_canonical_units", "g2_duplicate_lines.tsv").set_index("measure")
    steps = [
        ("raw record", "one line of an RT-anchored file", lv("raw_record"), "", ""),
        ("distinct record", "byte-identical duplicate lines collapsed", lv("distinct_raw_record"),
         "duplicate lines", int(dup.loc["extra_copies_beyond_first", "n"])),
        ("locus", "distinct (contig, RT start, RT end, RT strand)", lv("locus"),
         "records of the same locus re-mined (usually a second database)",
         lv("distinct_raw_record") - lv("locus")),
        ("physical locus", "locus after NZ_ contig-prefix normalisation", lv("physical_locus"),
         "RefSeq/GenBank twin loci collapsed", lv("locus") - lv("physical_locus")),
        ("exact RT", "sha256 of the RT protein", lv("exact_rt"),
         "physical loci carrying an RT protein seen elsewhere",
         lv("physical_locus") - lv("exact_rt")),
    ]
    fun = pd.DataFrame(steps, columns=["step", "definition", "n", "removed_by", "n_removed"])
    fun["pct_of_raw_records"] = 100 * fun.n / lv("raw_record")
    fun["cumulative_collapse_factor"] = lv("raw_record") / fun.n
    C.write_table("t01_unit_funnel", fun, "the unit named in the row",
                  "raw RT-anchored records (3,059,700) for the percentage column", SCRIPT)

    # other unit counts worth stating beside the funnel
    other = pd.DataFrame([
        ("genome", lv("genome")), ("contig", lv("contig")),
        ("RT taxonomic occurrence", lv("rt_taxonomic_occurrence")),
        ("RT species occurrence", lv("rt_species_occurrence")),
        ("window DNA", lv("window_dna")),
        ("exact RT, coordinate-verified", lv("exact_rt_coord_verified")),
    ], columns=["unit_name", "n"])
    C.write_table("t01_other_units", other, "the unit named in the row",
                  "n/a - counts of distinct units, no rate", SCRIPT)

    # ---------------------------------------------------------------- T02 per-database structure
    db = rec.groupby("source_database").agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_physical_loci=("physical_locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique"))
    db["loci_per_exact_rt"] = db.n_loci / db.n_exact_rt
    db["records_per_exact_rt"] = db.n_records / db.n_exact_rt
    db = db.reindex([d for d in C.DB_ORDER if d in db.index]).reset_index()
    C.write_table("t02_ladder_by_database", db, "records / loci / physical loci / exact RTs",
                  "distinct RT-anchored records of that source database", SCRIPT)

    # exact RTs shared across databases (which database contributes what)
    pair = rec[["rt_seq_hash", "source_database"]].drop_duplicates()
    sets = pair.groupby("rt_seq_hash").source_database.agg(
        lambda v: "|".join(d for d in C.DB_ORDER if d in set(v)))
    share = sets.value_counts().rename("n_exact_rt").reset_index()
    share.columns = ["source_database_set", "n_exact_rt"]
    share["n_databases"] = share.source_database_set.str.count(r"\|") + 1
    share["pct_of_exact_rt"] = 100 * share.n_exact_rt / share.n_exact_rt.sum()
    share = share.sort_values(["n_exact_rt"], ascending=False)
    C.write_table("t02_exact_rt_database_sets", share, "exact RT sequences",
                  "all 501,561 exact RT sequences", SCRIPT)

    # the same, folded to the UpSet the figure draws: the three big databases + "other database"
    def membership(s: str) -> str:
        parts = set(s.split("|"))
        keep = [d for d in C.BIG_DBS if d in parts]
        if parts - set(C.BIG_DBS):
            keep.append("other database")
        return "|".join(keep)
    ups = sets.map(membership).value_counts().rename("n_exact_rt").reset_index()
    ups.columns = ["membership", "n_exact_rt"]
    ups["n_sets"] = ups.membership.str.count(r"\|") + 1
    ups = ups.sort_values("n_exact_rt", ascending=False)
    C.write_table("t02_exact_rt_database_upset", ups, "exact RT sequences",
                  "all 501,561 exact RT sequences", SCRIPT)

    # twin effect per database (loci -> physical loci)
    lo = C.derived("rt_loci_v1", ["locus_key", "physical_locus_key", "is_refseq_genbank_twin",
                                  "family_label_set", "source_database_set"])
    tw = lo.groupby("source_database_set").agg(
        n_loci=("locus_key", "size"), n_physical_loci=("physical_locus_key", "nunique"),
        n_twin_loci=("is_refseq_genbank_twin", "sum")).reset_index()
    tw["pct_twin_loci"] = 100 * tw.n_twin_loci / tw.n_loci
    tw = tw.sort_values("n_loci", ascending=False)
    C.write_table("t02_twin_effect_by_database_set", tw, "loci",
                  "loci whose records carry that set of source databases", SCRIPT)

    # ---------------------------------------------------------------- T03 recurrence structure
    ex2 = ex.merge(fb[["rt_seq_hash", "family_label", "view"]], on="rt_seq_hash", how="left")
    ex2["family"] = fam_bucket(ex2.family_label, major)
    rows = []
    for metric, col in (("physical loci per exact RT", "n_physical_loci"),
                        ("genomes per exact RT", "n_genomes"),
                        ("databases per exact RT", "n_source_databases")):
        for fam, g in ex2.groupby("family"):
            v = np.sort(g[col].to_numpy())
            n = len(v)
            for x in (1, 2, 3, 5, 10, 20, 50, 100, 1000, 10000):
                rows.append(dict(metric=metric, family=fam, at_least=x,
                                 n_exact_rt=int((v >= x).sum()), n_exact_rt_total=n,
                                 pct=100 * float((v >= x).mean())))
    C.write_table("t03_recurrence_ccdf", pd.DataFrame(rows), "exact RT sequences",
                  "exact RT sequences of that family bucket", SCRIPT)

    conc = []
    for fam, g in ex2.groupby("family"):
        v = np.sort(g.n_physical_loci.to_numpy())[::-1]
        tot = v.sum()
        n = len(v)
        for q in (0.001, 0.01, 0.1):
            k = max(1, int(round(q * n)))
            conc.append(dict(family=fam, top_fraction_of_exact_rt=q, n_exact_rt=n,
                             n_top=k, pct_of_physical_loci=100 * v[:k].sum() / tot,
                             n_physical_loci_total=int(tot)))
    C.write_table("t03_recurrence_concentration", pd.DataFrame(conc), "physical loci",
                  "physical loci of that family bucket", SCRIPT)

    # ---------------------------------------------------------------- T04 abundance vs unit
    rec2 = rec.copy()
    rec2["family"] = fam_bucket(rec2.file_label, major)
    per_unit = rec2.groupby("family").agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_physical_loci=("physical_locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique"))
    for c in ("n_records", "n_loci", "n_physical_loci", "n_exact_rt"):
        per_unit["pct_" + c[2:]] = 100 * per_unit[c] / per_unit[c].sum()
    per_unit["shift_records_to_exact_rt"] = per_unit.pct_exact_rt / per_unit.pct_records
    per_unit = per_unit.sort_values("n_exact_rt", ascending=False).reset_index()
    C.write_table("t04_family_share_by_unit", per_unit,
                  "records / loci / physical loci / exact RTs",
                  "all RT-anchored units of that level (MULTI included as its own row)", SCRIPT)

    # ---------------------------------------------------------------- T05 database x family
    hm = (rec2.groupby(["source_database", "family"]).rt_seq_hash.nunique()
          .rename("n_exact_rt").reset_index())
    tot = hm.groupby("source_database").n_exact_rt.transform("sum")
    hm["pct_of_database_exact_rt"] = 100 * hm.n_exact_rt / tot
    C.write_table("t05_database_family_composition", hm, "exact RT sequences (distinct within a database)",
                  "exact RT sequences seen in that source database", SCRIPT)

    # ---------------------------------------------------------------- T06 ranked family table
    fam_tab = per_unit.copy()
    single = fb[fb.view == "V-RT-SINGLE"].groupby("family_label").rt_aa_len.median().rename(
        "median_rt_aa_len")
    fam_tab = fam_tab.merge(single, left_on="family", right_index=True, how="left")
    C.write_table("t06_family_ranked", fam_tab, "exact RTs (bar) with loci/records beside",
                  "all RT-anchored units of that level", SCRIPT)

    # ---------------------------------------------------------------- T07/T08 RT length
    single_fb = fb[fb.view == "V-RT-SINGLE"].copy()
    multi_fb = fb[fb.view == "V-RT-MULTI"].copy()
    both = pd.concat([single_fb, multi_fb])
    both["family"] = both.family_label.where(
        both.family_label.isin(major) | (both.view == "V-RT-MULTI"), "other")
    qs = []
    for (fam, comp), g in both.groupby(["family", "completeness_class"]):
        v = g.rt_aa_len.to_numpy()
        if len(v) == 0:
            continue
        qs.append(dict(family=fam, completeness_class=comp, n_exact_rt=len(v),
                       q05=float(np.percentile(v, 5)), q25=float(np.percentile(v, 25)),
                       median=float(np.median(v)), q75=float(np.percentile(v, 75)),
                       q95=float(np.percentile(v, 95)), min=int(v.min()), max=int(v.max()),
                       mean=float(v.mean())))
    for fam, g in both.groupby("family"):
        v = g.rt_aa_len.to_numpy()
        qs.append(dict(family=fam, completeness_class="ALL", n_exact_rt=len(v),
                       q05=float(np.percentile(v, 5)), q25=float(np.percentile(v, 25)),
                       median=float(np.median(v)), q75=float(np.percentile(v, 75)),
                       q95=float(np.percentile(v, 95)), min=int(v.min()), max=int(v.max()),
                       mean=float(v.mean())))
    C.write_table("t07_rt_length_quantiles", pd.DataFrame(qs).sort_values(
        ["family", "completeness_class"]), "exact RT sequences",
        "exact RTs of that family and completeness class (V-RT-SINGLE; MULTI is its own family row)",
        SCRIPT)

    # histogram the violins are drawn from (10-aa bins, 0-1200 aa plus an overflow bin)
    edges = np.arange(0, 1210, 10)
    hrows = []
    for (fam, comp), g in both.groupby(["family", "completeness_class"]):
        cnt, _ = np.histogram(np.clip(g.rt_aa_len.to_numpy(), 0, 1205), bins=list(edges) + [10**9])
        for lo, c in zip(list(edges) + [1210], cnt):
            if c:
                hrows.append(dict(family=fam, completeness_class=comp, bin_start_aa=int(lo),
                                  n_exact_rt=int(c)))
    C.write_table("t07_rt_length_histogram", pd.DataFrame(hrows), "exact RT sequences",
                  "exact RTs of that family and completeness class, binned at 10 aa "
                  "(bin_start_aa 1210 = 1,205 aa and above)", SCRIPT)

    # ECDF at 1-aa resolution for the major families (plotted as a step)
    erows = []
    for fam, g in both.groupby("family"):
        v = np.sort(g.rt_aa_len.to_numpy())
        grid = np.unique(np.clip(np.percentile(v, np.arange(0, 100.5, 0.5)), 0, None)).astype(int)
        for x in grid:
            erows.append(dict(family=fam, rt_aa_len=int(x),
                              cumulative_pct=100 * float((v <= x).mean()), n_exact_rt=len(v)))
    C.write_table("t08_rt_length_ecdf", pd.DataFrame(erows), "exact RT sequences",
                  "exact RTs of that family (V-RT-SINGLE; MULTI separate)", SCRIPT)

    # shape: dispersion and a declared mode count
    def modes(v: np.ndarray) -> int:
        """Declared rule: histogram at 10 aa over the 1st-99th percentile, smoothed with a
        3-bin moving average; a local maximum counts as a mode when it is >= 10% of the global
        maximum and separated from a higher peak by a valley <= 60% of the lower of the two."""
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
            ok = True
            for j in kept:
                a, b2 = sorted((i, j))
                valley = k[a:b2 + 1].min()
                if valley > 0.6 * min(k[i], k[j]):
                    ok = False
                    break
            if ok:
                kept.append(i)
        return max(1, len(kept))

    srows = []
    for fam, g in both.groupby("family"):
        v = g.rt_aa_len.to_numpy().astype(float)
        q25, med, q75 = np.percentile(v, [25, 50, 75])
        q05, q95 = np.percentile(v, [5, 95])
        iqr = q75 - q25
        fl, fh = q25 - 1.5 * iqr, q75 + 1.5 * iqr
        srows.append(dict(family=fam, n_exact_rt=len(v), median=med, iqr=iqr,
                          iqr_over_median=iqr / med if med else np.nan,
                          q95_over_q05=q95 / q05 if q05 else np.nan,
                          pct_outside_tukey_fences=100 * float(((v < fl) | (v > fh)).mean()),
                          n_modes_declared_rule=modes(v)))
    C.write_table("t08_rt_length_shape", pd.DataFrame(srows).sort_values(
        "n_exact_rt", ascending=False), "exact RT sequences",
        "exact RTs of that family (V-RT-SINGLE; MULTI separate)", SCRIPT)


if __name__ == "__main__":
    main()
