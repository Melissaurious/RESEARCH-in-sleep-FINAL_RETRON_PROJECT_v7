#!/usr/bin/env python3
"""a05 - sections 11-13: taxonomic prevalence vs representation, data quality, recurrence breadth.

PREVALENCE needs a sampled-genome denominator. No landed Stage-1 table carries one, so this
script reads TWO columns of the GTDB bacterial catalogue that g5 already joined and hashed
(`accession`, `gtdb_taxonomy`) plus CheckM2 completeness. That is the declared data gap in
FIGURE_AND_ANALYSIS_PLAN.md §B. Everything else comes from landed/derived Stage-1 data.

⛔ Prevalence is computed ONLY inside the `gtdb_bacteria` source database, where the corpus's
taxonomy schema and the catalogue's are the same (GTDB). The NCBI block has no phylum by
construction (g5), so NCBI is reported as REPRESENTATION, never prevalence, and the two schemas
are never pooled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

SCRIPT = "a05_taxonomy_quality.py"
RANKS = ("phylum", "class", "order", "genus")
MIN_SAMPLED = {"phylum": 1000, "class": 1000, "order": 500, "genus": 500}


def gtdb_catalogue() -> pd.DataFrame:
    def build():
        cat = pd.read_csv(C.GTDB_CATALOGUE, sep="\t", compression="gzip", low_memory=False,
                          usecols=["accession", "gtdb_taxonomy", "checkm2_completeness"])
        cat["genome_id_norm"] = cat.accession.str.replace(r"^(RS_|GB_)", "", regex=True)
        parts = cat.gtdb_taxonomy.str.split(";", expand=True)
        for i, r in enumerate(["domain", "phylum", "class", "order", "family", "genus", "species"]):
            cat[f"cat_{r}"] = parts[i].str.slice(3) if i < parts.shape[1] else ""
        return cat.drop(columns=["gtdb_taxonomy"])
    return C.cached("gtdb_catalogue", build)


def main() -> None:
    C.log("== a05 sections 11-13")
    rec = C.records()
    cat = gtdb_catalogue()
    fb = C.derived("rt_family_baseline_v1", ["rt_seq_hash", "family_label", "view"])
    major = list(fb[fb.view == "V-RT-SINGLE"].family_label.value_counts()
                 .head(C.N_MAJOR_FAMILIES).index)

    g = rec[rec.source_database == "gtdb_bacteria"].copy()
    # the corpus's own lineage for these records IS GTDB (g5: taxonomy_system == 'gtdb')
    assert set(g.taxonomy_system.unique()) <= {"gtdb"}, "gtdb_bacteria records are not GTDB-schema"
    pos = g.groupby("genome_id_norm").agg(n_loci=("physical_locus_key", "nunique"),
                                          n_exact_rt=("rt_seq_hash", "nunique"))
    joined = cat.merge(pos, left_on="genome_id_norm", right_index=True, how="left")
    joined["rt_positive"] = joined.n_loci.notna()
    C.log(f"   GTDB catalogue genomes {len(joined):,d}; RT-positive {int(joined.rt_positive.sum()):,d}")

    # ---------------------------------------------------------------- t34 prevalence per rank
    out = []
    for rank in RANKS:
        col = f"cat_{rank}"
        grp = joined.groupby(col)
        t = grp.agg(n_sampled_genomes=("genome_id_norm", "size"),
                    n_rt_positive_genomes=("rt_positive", "sum")).reset_index()
        t = t.rename(columns={col: "taxon"})
        t["rank"] = rank
        ex = (g.merge(cat[["genome_id_norm", col]], on="genome_id_norm", how="left")
              .groupby(col).agg(n_exact_rt=("rt_seq_hash", "nunique"),
                                n_physical_loci=("physical_locus_key", "nunique")).reset_index()
              .rename(columns={col: "taxon"}))
        t = t.merge(ex, on="taxon", how="left")
        t[["n_exact_rt", "n_physical_loci"]] = t[["n_exact_rt", "n_physical_loci"]].fillna(0).astype(int)
        t = C.add_rate(t, "n_rt_positive_genomes", "n_sampled_genomes", "prevalence_pct")
        t["loci_per_positive_genome"] = t.n_physical_loci / t.n_rt_positive_genomes.replace(0, np.nan)
        t["exact_rt_per_positive_genome"] = t.n_exact_rt / t.n_rt_positive_genomes.replace(0, np.nan)
        t["meets_min_sampled"] = t.n_sampled_genomes >= MIN_SAMPLED[rank]
        out.append(t.sort_values("n_sampled_genomes", ascending=False))
    t34 = pd.concat(out, ignore_index=True)
    C.write_table("t34_gtdb_prevalence_by_rank", t34, "genomes",
                  "genomes of that taxon in the GTDB bacterial catalogue (the sampled set; an "
                  "upper bound on what the pipeline attempted - pipeline failures are not "
                  "recorded in any Stage-1 input). Only gtdb_bacteria corpus records contribute "
                  "the numerator", SCRIPT, estimate="census; Wilson 95% interval on the prevalence")

    # ---------------------------------------------------------------- t35 family x phylum
    gg = g.merge(cat[["genome_id_norm", "cat_phylum"]], on="genome_id_norm", how="left")
    gg["family"] = gg.file_label.where(gg.file_label.isin(major) | gg.file_label.eq("MULTI"), "other")
    fam_gen = (gg.groupby(["cat_phylum", "family"]).genome_id_norm.nunique()
               .rename("n_positive_genomes").reset_index())
    samp = joined.groupby("cat_phylum").genome_id_norm.size().rename("n_sampled_genomes")
    fam_gen = fam_gen.merge(samp, left_on="cat_phylum", right_index=True, how="left")
    fam_gen = C.add_rate(fam_gen, "n_positive_genomes", "n_sampled_genomes", "prevalence_pct")
    fam_gen = fam_gen[fam_gen.n_sampled_genomes >= MIN_SAMPLED["phylum"]]
    C.write_table("t35_family_by_phylum_prevalence", fam_gen.sort_values(
        ["n_sampled_genomes", "n_positive_genomes"], ascending=False), "genomes",
        "genomes of that phylum in the GTDB bacterial catalogue (phyla with >=1,000 sampled "
        "genomes); numerator = genomes carrying >=1 locus of that family label",
        SCRIPT, estimate="census; Wilson 95% interval on the prevalence")

    # ---------------------------------------------------------------- t36 NCBI representation
    rep = C.landed("dbchar_g5_metadata_sampling", "g5_overrepresentation_genus.tsv")
    rep = rep[rep.taxonomy_system == "ncbi"].copy()
    C.write_table("t36_ncbi_genus_representation", rep.drop(columns=[
        c for c in ("unit", "denominator") if c in rep.columns]).head(20),
        "records / loci / exact RTs",
        "all NCBI-schema records carrying a genus (carried from the landed g5 table, re-emitted "
        "unchanged, top 20 by records). This is REPRESENTATION: no sampled-genome denominator "
        "exists for the NCBI block, so no prevalence is computed", SCRIPT)

    # ---------------------------------------------------------------- t37 carriage vs host quality
    q = joined[joined.rt_positive].copy()
    rpl = C.physical_retron_loci()
    rec_g = rec[["record_key", "genome_id_norm", "source_database"]]
    rl = rpl.merge(rec_g, left_on="representative_record_key", right_on="record_key", how="left")
    rl = rl[rl.source_database_y.eq("gtdb_bacteria") if "source_database_y" in rl.columns
            else rl.source_database.eq("gtdb_bacteria")]
    rl = rl.merge(cat[["genome_id_norm", "checkm2_completeness"]], on="genome_id_norm", how="left")
    rl = rl.dropna(subset=["checkm2_completeness"])
    bins = [0, 50, 70, 90, 95, 99, 100.0001]
    labs = ["<50", "50-69", "70-89", "90-94", "95-98", ">=99"]
    rl["completeness_bin"] = pd.cut(rl.checkm2_completeness, bins=bins, labels=labs, right=False)
    rows = []
    for b, h in rl.groupby("completeness_bin", observed=True):
        rows.append(dict(checkm2_completeness_bin=b, n_loci=len(h),
                         n_with_ncrna=int((h.n_canonical > 0).sum())))
    t37 = C.add_rate(pd.DataFrame(rows), "n_with_ncrna", "n_loci", "pct_with_ncrna")
    C.write_table("t37_carriage_by_host_completeness", t37, "physical loci",
                  "Retron physical loci in gtdb_bacteria genomes with a CheckM2 completeness "
                  "value in the catalogue (the only databases carrying one are GTDB/GEM/MGnify; "
                  "NCBI carries no CheckM column at all - g5)", SCRIPT,
                  estimate="census; Wilson 95% interval on the rate")

    # ---------------------------------------------------------------- t38 recurrence breadth
    ex = C.derived("rt_exact_v1", ["rt_seq_hash", "n_genomes", "n_physical_loci",
                                   "n_source_databases", "n_records"])
    sp = rec.groupby("rt_seq_hash").agg(n_species=("tax_species", "nunique"),
                                        n_genera=("tax_genus", "nunique"),
                                        n_tax_systems=("taxonomy_system", "nunique"))
    ex = ex.merge(sp, left_on="rt_seq_hash", right_index=True, how="left")
    ex = ex.merge(fb[["rt_seq_hash", "family_label", "view"]], on="rt_seq_hash", how="left")
    ex["family"] = ex.family_label.where(ex.family_label.isin(major) | ex.family_label.eq("MULTI"),
                                         "other")
    big = ex[ex.n_genomes >= 20].copy()
    big["breadth_class"] = np.where(big.n_species <= 1, "one species (database duplication or clonal)",
                                    np.where(big.n_species <= 5, "2-5 species", ">5 species"))
    t38 = big.groupby(["family", "breadth_class"]).agg(
        n_exact_rt=("rt_seq_hash", "size"), median_genomes=("n_genomes", "median"),
        median_species=("n_species", "median"), median_databases=("n_source_databases", "median")
    ).reset_index()
    tot = t38.groupby("family").n_exact_rt.transform("sum")
    t38["pct_of_family_high_recurrence"] = 100 * t38.n_exact_rt / tot
    C.write_table("t38_recurrence_breadth", t38.sort_values(["n_exact_rt"], ascending=False),
                  "exact RT sequences", "exact RTs occurring in >=20 genomes, of that family",
                  SCRIPT)

    C.write_table("t38_recurrence_scatter", big[["rt_seq_hash", "family", "n_genomes", "n_species",
                                                 "n_genera", "n_source_databases",
                                                 "n_physical_loci"]].sort_values(
        "n_genomes", ascending=False), "exact RT sequences",
        "each exact RT occurring in >=20 genomes, one per row", SCRIPT)

    # ---------------------------------------------------------------- section 12: data quality
    bt = (rec.groupby(["source_database", "bt_status"]).size().rename("n_records").reset_index())
    tot = bt.groupby("source_database").n_records.transform("sum")
    bt["pct_of_database_records"] = 100 * bt.n_records / tot
    C.write_table("t39_bt_status_by_database", bt.sort_values(["source_database", "n_records"],
                                                              ascending=[True, False]),
                  "distinct records",
                  "distinct RT-anchored records of that source database", SCRIPT)

    rc = C.derived("rt_cds_recovery_v1", ["record_key", "source_database", "recovery_state",
                                          "representation_class", "file_label"])
    rr = (rc.groupby(["source_database", "recovery_state"]).size().rename("n_records")
          .reset_index())
    rr = rr.merge(rec.groupby("source_database").size().rename("n_records_in_database"),
                  left_on="source_database", right_index=True, how="left")
    rr["pct_of_database_records"] = 100 * rr.n_records / rr.n_records_in_database
    C.write_table("t39_no_rt_cds_recovery_by_database", rr.sort_values(
        ["n_records"], ascending=False), "distinct records",
        "records without a marked RT CDS, of that source database; the percentage is out of all "
        "distinct RT-anchored records of the database", SCRIPT)

    trunc = []
    for db, h in rec.groupby("source_database"):
        trunc.append(dict(source_database=db, n_records=len(h),
                          pct_window_inverted=100 * float(h.window_inverted.mean()),
                          pct_rt_outside_window=100 * float((~h.rt_in_window).mean()),
                          pct_rt_at_window_edge=100 * float(h.rt_at_window_edge.mean()),
                          pct_true_start_clipped=100 * float(h.true_start_clipped.mean()),
                          pct_clipped_at_contig_end=100 * float(h.clipped_end_flag.mean()),
                          pct_geometry_eligible=100 * float(h.elig_geometry.mean())))
    C.write_table("t39_context_truncation_by_database", pd.DataFrame(trunc).sort_values(
        "n_records", ascending=False), "distinct records",
        "distinct RT-anchored records of that source database", SCRIPT)

    qa = C.landed("dbchar_g5_metadata_sampling", "g5_quality_availability.tsv")
    C.write_table("t39_checkm_availability", qa.drop(columns=[
        c for c in ("unit", "denominator") if c in qa.columns]), "genome entries",
        "genome entries per source database (carried from the landed g5 table, re-emitted "
        "unchanged)", SCRIPT)

    # the inspectability tier: what a reader can look at directly, and what is retained with caveats
    r = rec
    tier = pd.Series("retained with a caveat", index=r.index, dtype=object)
    fully = (r.bt_status.eq("exact") & r.elig_geometry & r.n_rt_cds.gt(0)
             & ~r.rt_at_window_edge & ~r.true_start_clipped & ~r.clipped_end_flag)
    recoded = r.bt_status.isin(["alt_start", "code4_tga_trp", "internal_stop_masked"])
    tier = tier.mask(fully, "fully inspectable (exact back-translation, RT CDS present, "
                            "window not clipped or edge-touching)")
    tier = tier.mask(~fully & r.elig_geometry & recoded,
                     "geometry-eligible, translation recoded (alt start / table 4 / masked stop)")
    tier = tier.mask(~fully & r.elig_geometry & r.bt_status.eq("exact"),
                     "geometry-eligible, context clipped or RT at a window edge")
    tier = tier.mask(~r.elig_geometry & r.bt_status.ne("mismatch"),
                     "sequence only - no defensible genomic context")
    tier = tier.mask(r.bt_status.eq("mismatch"), "ill-posed - back-translation mismatch")
    t40 = tier.value_counts().rename("n_records").reset_index()
    t40.columns = ["inspectability_tier", "n_records"]
    t40["pct_of_distinct_records"] = 100 * t40.n_records / len(r)
    C.write_table("t40_inspectability", t40, "distinct records",
                  "all 3,051,238 distinct RT-anchored records", SCRIPT)


if __name__ == "__main__":
    main()
