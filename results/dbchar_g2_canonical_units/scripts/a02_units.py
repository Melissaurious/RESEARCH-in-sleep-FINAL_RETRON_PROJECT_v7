#!/usr/bin/env python3
"""a02 - the canonical unit ladder, coordinate/RT integrity QC and eligibility denominators.

Reads only the derived tables e01 wrote. Every table states its unit and the population its
denominator equals. Nothing here filters the corpus: eligibility flags decide which records
can support which measurement, and every rule reports how many records it removes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g2lib as G  # noqa: E402

ELIG = ["elig_exact_rt", "elig_rt_coords", "elig_geometry", "elig_rt_length", "elig_rt_completeness"]


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    D, T = W / "derived", W / "tables"
    T.mkdir(parents=True, exist_ok=True)

    r = pd.read_parquet(D / "rt_records_v1.parquet")
    lo = pd.read_parquet(D / "rt_loci_v1.parquet")
    ph = pd.read_parquet(D / "rt_physical_loci_v1.parquet")
    ex = pd.read_parquet(D / "rt_exact_v1.parquet",
                         columns=["rt_seq_hash", "rt_aa_len", "n_records", "n_loci", "n_genomes",
                                  "n_source_databases", "family_label_set", "any_multilabel",
                                  "n_verified_records", "wellformed"])
    f = r[r.is_first_copy]                      # distinct raw records (byte-identical extras dropped)
    pop = r.file_label.eq("MULTI").map({True: "POP-RT-MULTI", False: "POP-RT-FAM"})
    r["population"] = pop
    f = r[r.is_first_copy]

    # ---- 1 · the unit ladder ---------------------------------------------------------
    rows = [
        ["raw_record", "one line of an RT-anchored corpus file", len(r),
         "the 42 RT-anchored files at their g1 sha256"],
        ["distinct_raw_record", "raw records after byte-identical duplicate lines collapse", len(f),
         "raw_record"],
        ["rt_system_id", "distinct rt_system_id string (NOT a key: it encodes contig+RT start)",
         r.rt_system_id.nunique(), "raw_record"],
        ["attribution", "distinct (rt_system_id, source_database, genome_id)",
         len(f.drop_duplicates(["rt_system_id", "source_database", "genome_id"])), "distinct_raw_record"],
        ["locus", "distinct (contig, RT start, RT end, RT strand)", f.locus_key.nunique(),
         "distinct_raw_record"],
        ["physical_locus", "locus after NZ_ contig-prefix normalisation", f.physical_locus_key.nunique(),
         "locus"],
        ["physical_locus_collapse_supported",
         "physical loci whose collapse the window-DNA + RT + coordinate evidence supports",
         int(ph.collapse_supported.sum()), "physical_locus"],
        ["exact_rt", "distinct sha256 of the RT amino-acid sequence (one trailing * removed)",
         f.rt_seq_hash.nunique(), "distinct_raw_record"],
        ["exact_rt_wellformed", "exact RT sequences that are well-formed protein",
         int(ex.wellformed.sum()), "exact_rt"],
        ["exact_rt_coord_verified", "exact RTs with at least one back-translation-verified record",
         int((ex.n_verified_records > 0).sum()), "exact_rt"],
        ["genome", "distinct genome_id after the GTDB RS_/GB_ prefix is removed",
         f.genome_id_norm.nunique(), "distinct_raw_record"],
        ["contig", "distinct contig accession after NZ_ normalisation", f.contig_norm.nunique(),
         "distinct_raw_record"],
        ["rt_taxonomic_occurrence", "distinct (exact RT, genome)",
         len(f.drop_duplicates(["rt_seq_hash", "genome_id_norm"])), "distinct_raw_record"],
        ["rt_species_occurrence", "distinct (exact RT, taxonomy_system, species)",
         len(f.drop_duplicates(["rt_seq_hash", "taxonomy_system", "tax_species"])), "distinct_raw_record"],
        ["window_dna", "distinct sha256 of the extracted window DNA (empty excluded)",
         f.loc[f.window_dna_sha256 != "", "window_dna_sha256"].nunique(), "distinct_raw_record"],
    ]
    w(T / "g2_unit_ladder.tsv", pd.DataFrame(rows, columns=["unit", "definition", "n", "denominator"]))

    # ---- 2 · the ladder per stratum: the factors are NOT constant ---------------------
    def ladder(df, by):
        g = df.groupby(by)
        out = g.agg(n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
                    n_physical_loci=("physical_locus_key", "nunique"),
                    n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique"),
                    n_contigs=("contig_norm", "nunique")).reset_index()
        out["records_per_locus"] = (out.n_records / out.n_loci).round(4)
        out["loci_per_exact_rt"] = (out.n_loci / out.n_exact_rt).round(4)
        out["records_per_exact_rt"] = (out.n_records / out.n_exact_rt).round(4)
        return out

    w(T / "g2_ladder_by_source_database.tsv", ladder(f, "source_database"))
    w(T / "g2_ladder_by_family_label.tsv", ladder(f, "file_label"))
    w(T / "g2_ladder_by_population.tsv", ladder(f, "population"))

    # ---- 3 · multiplicity distributions ----------------------------------------------
    def dist(s, name, unit, denom):
        v = s.value_counts().sort_index()
        return pd.DataFrame({"measure": name, "value": v.index, "n": v.values,
                             "unit": unit, "denominator": denom})
    md = pd.concat([
        dist(lo.n_records.clip(upper=10), "records_per_locus(capped_10)", "loci", "locus"),
        dist(lo.n_source_databases, "source_databases_per_locus", "loci", "locus"),
        dist(lo.n_files, "source_files_per_locus", "loci", "locus"),
        dist(lo.n_rt_hashes, "exact_rts_per_locus", "loci", "locus"),
        dist(ex.n_loci.clip(upper=20), "loci_per_exact_rt(capped_20)", "exact RTs", "exact_rt"),
        dist(ex.n_genomes.clip(upper=20), "genomes_per_exact_rt(capped_20)", "exact RTs", "exact_rt"),
        dist(ph.n_contig_spellings, "contig_spellings_per_physical_locus", "physical loci", "physical_locus"),
    ])
    w(T / "g2_multiplicity.tsv", md)

    # ---- 4 · RT coordinate integrity: back-translation --------------------------------
    bt = (r.groupby(["population", "bt_status"]).size().rename("n_records").reset_index())
    bt["n_in_population"] = bt.population.map(r.population.value_counts())
    bt["verified"] = bt.bt_status.isin(G.BT_VERIFIED)
    d = r[r.frame_disambiguating]
    bt2 = (d.groupby(["population", "bt_status"]).size().rename("n_records_frame_disambiguating")
           .reset_index())
    bt = bt.merge(bt2, how="left", on=["population", "bt_status"]).fillna({"n_records_frame_disambiguating": 0})
    bt["n_in_population_frame_disambiguating"] = bt.population.map(d.population.value_counts())
    w(T / "g2_bt_status.tsv", bt)
    w(T / "g2_bt_status_by_family.tsv",
      r.groupby(["file_label", "bt_status"]).size().rename("n_records").reset_index())

    # ---- 5 · the RT-CDS question -----------------------------------------------------
    cl = r.groupby(["population", "no_rt_cds_class"]).agg(
        n_records=("record_key", "size"), n_bt_verified=("elig_rt_coords", "sum"),
        n_elig_exact_rt=("elig_exact_rt", "sum"), n_elig_geometry=("elig_geometry", "sum"),
        n_elig_completeness=("elig_rt_completeness", "sum")).reset_index()
    cl["n_in_population"] = cl.population.map(r.population.value_counts())
    w(T / "g2_rt_cds_classes.tsv", cl)
    w(T / "g2_rt_cds_concordance.tsv", r.groupby(
        ["n_rt_cds", "rtcds_coords_eq_rt", "rtcds_seq_eq_rt", "seqcds_all_are_rt"],
        dropna=False).size().rename("n_records").reset_index())
    w(T / "g2_cds_sequence_carrier.tsv", r.groupby(
        ["n_cds_with_sequence", "seqcds_all_are_rt"], dropna=False).size().rename("n_records").reset_index())

    # ---- 6 · eligibility denominators ------------------------------------------------
    er = []
    for flag in ELIG:
        reason = flag + "_reason"
        for p, sub in r.groupby("population"):
            n = len(sub)
            ok = int(sub[flag].sum())
            er.append([p, flag, "ELIGIBLE", "", ok, n, round(100 * ok / n, 4)])
            for rs, cnt in sub.loc[~sub[flag], reason].value_counts().items():
                er.append([p, flag, "INELIGIBLE", rs, int(cnt), n, round(100 * cnt / n, 4)])
    w(T / "g2_eligibility.tsv", pd.DataFrame(er, columns=[
        "population", "eligibility_flag", "state", "reason", "n_records",
        "n_records_in_population", "pct_of_population"]))
    eu = []
    for flag in ELIG:
        sub = f[f[flag]]
        eu.append([flag, len(sub), sub.locus_key.nunique(), sub.physical_locus_key.nunique(),
                   sub.rt_seq_hash.nunique(), sub.genome_id_norm.nunique()])
    w(T / "g2_eligible_unit_counts.tsv", pd.DataFrame(eu, columns=[
        "eligibility_flag", "n_distinct_raw_records", "n_loci", "n_physical_loci",
        "n_exact_rt", "n_genomes"]))

    # ---- 7 · window / coordinate-frame QC --------------------------------------------
    wq = [
        ["window_inverted", int(r.window_inverted.sum())],
        ["window_length_inconsistent", int((~r.window_len_consistent).sum())],
        ["fullseq_empty", int((r.fullseq_len == 0).sum())],
        ["rt_inside_window", int(r.rt_in_window.sum())],
        ["rt_outside_window", int((~r.rt_in_window).sum())],
        ["rt_at_window_edge", int(r.rt_at_window_edge.sum())],
        ["window_starts_at_1", int((r.win_start == 1).sum())],
        ["frame_disambiguating(window_start>1)", int(r.frame_disambiguating.sum())],
        ["clipped_at_contig_end_flag_true", int(r.clipped_end_flag.sum())],
        ["clipped_at_contig_start_flag_true(raw, known dead)", int(r.clipped_start_flag_raw.sum())],
        ["true_start_clipped(anchor_center-10000<1)", int(r.true_start_clipped.sum())],
        ["extended_for_cds", int(r.extended_for_cds.sum())],
        ["anchor_interval_equals_rt_gene", int(r.anchor_eq_rt.sum())],
        ["rt_len_nt_equals_3x_aa", int(r.rt_len_nt_eq_3aa.sum())],
        ["rt_interval_invalid", int((~r.rt_interval_valid).sum())],
    ]
    w(T / "g2_window_qc.tsv", pd.DataFrame(wq, columns=["measure", "n_records"]).assign(
        n_records_total=len(r), unit="records", denominator="raw_record (RT-anchored)"))
    w(T / "g2_inverted_window_profile.tsv", r[r.window_inverted].groupby(
        ["population", "source_database", "clipped_end_flag"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_with_cds=("n_cds", lambda s: int((s > 0).sum())),
        n_fullseq_empty=("fullseq_len", lambda s: int((s == 0).sum())),
        n_rt_beyond_win_end=("rt_start", "size")).reset_index())
    w(T / "g2_rt_outside_window_profile.tsv", r[~r.rt_in_window].groupby(
        ["population", "source_database", "window_inverted"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_elig_exact_rt=("elig_exact_rt", "sum")).reset_index())

    # ---- 8 · the canonical ncRNA count source ----------------------------------------
    nc = r.groupby(["population", "ncrna_count_qc"]).agg(
        n_records=("record_key", "size"),
        n_array_gt_0=("n_ncrna", lambda s: int((s > 0).sum())),
        n_ids_missing_from_array=("n_ncrna_ids_missing_from_array", lambda s: int((s > 0).sum())),
        sum_array=("n_ncrna", "sum"), sum_metadata=("meta_total_ncrnas", "sum")).reset_index()
    w(T / "g2_ncrna_count_source.tsv", nc)
    w(T / "g2_ncrna_flag_reconciliation.tsv", r.groupby(
        [(r.n_ncrna > 0).rename("array_nonempty"),
         (r.n_igr_has_ncrna_true > 0).rename("any_intergenic_has_ncrna"),
         (r.n_ncrna_ids_referenced > 0).rename("any_ncrna_ids_referenced")]).size()
        .rename("n_records").reset_index())

    # ---- 9 · MULTI and the cross-file multi-label records ------------------------------
    m = r[r.population.eq("POP-RT-MULTI")]
    w(T / "g2_multi_stratum.tsv", m.groupby(["type_set_norm", "n_type_tokens"]).agg(
        n_records=("record_key", "size"), n_raw_spellings=("system_types_raw", "nunique"),
        n_loci=("locus_key", "nunique"), n_exact_rt=("rt_seq_hash", "nunique"),
        n_source_databases=("source_database", "nunique"),
        n_elig_rt_coords=("elig_rt_coords", "sum")).reset_index()
        .sort_values("n_records", ascending=False))
    fam_multi = r[r.multilabel & r.population.eq("POP-RT-FAM")]
    w(T / "g2_multilabel_in_family_files.tsv", fam_multi.groupby(
        ["type_set_norm", "source_file"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"),
        n_first_copy=("is_first_copy", "sum")).reset_index())
    # Cross-family loci must be counted over ALL records, not first copies: the cross-file
    # duplicates are byte-identical lines, so the first-copy filter hides the second file.
    fl = (r.groupby("locus_key").file_label.agg(["nunique", "first"])
          .rename(columns={"nunique": "n_labels", "first": "label"}))
    multi_lab = fl.index[fl.n_labels > 1]
    cross = r[r.locus_key.isin(multi_lab)]
    w(T / "g2_cross_family_loci.tsv", cross.groupby(["type_set_norm"]).agg(
        n_loci=("locus_key", "nunique"), n_records=("record_key", "size"),
        n_files=("source_file", "nunique"), n_exact_rt=("rt_seq_hash", "nunique"),
        n_first_copy_records=("is_first_copy", "sum")).reset_index())

    # ---- 10 · twins and duplicate lines ------------------------------------------------
    w(T / "g2_twin_evidence.tsv", ph.groupby("twin_evidence_class").agg(
        n_physical_loci=("physical_locus_key", "size"), n_loci=("n_loci", "sum"),
        n_records=("n_records", "sum"), n_collapse_supported=("collapse_supported", "sum")).reset_index())
    dup = r[r.n_copies_of_line > 1]
    w(T / "g2_duplicate_lines.tsv", pd.DataFrame([
        ["records_on_duplicated_lines", len(dup)],
        ["duplicate_line_groups", dup.record_sha256.nunique()],
        ["extra_copies_beyond_first", len(dup) - dup.record_sha256.nunique()],
        ["loci_touched_by_duplicates", dup.locus_key.nunique()],
        ["duplicate_groups_spanning_two_files", int(dup.groupby("record_sha256").source_file.nunique().gt(1).sum())],
        ["exact_rts_touched", dup.rt_seq_hash.nunique()],
    ], columns=["measure", "n"]).assign(unit="records/groups/loci", denominator="raw_record (RT-anchored)"))
    w(T / "g2_locus_conflicts.tsv", pd.DataFrame([
        ["loci_with_more_than_one_exact_rt", int((lo.n_rt_hashes > 1).sum())],
        ["loci_in_more_than_one_source_file", int((lo.n_files > 1).sum())],
        ["loci_in_more_than_one_source_database", int((lo.n_source_databases > 1).sum())],
        ["loci_with_more_than_one_genome_id", int((lo.n_genomes > 1).sum())],
        ["loci_with_more_than_one_rt_system_id", int((lo.n_rt_system_ids > 1).sum())],
        ["loci_spanning_more_than_one_source_file_INCLUDING_duplicate_copies",
         int(r.groupby("locus_key").source_file.nunique().gt(1).sum())],
        ["loci_with_more_than_one_family_label_INCLUDING_duplicate_copies", int((fl.n_labels > 1).sum())],
    ], columns=["measure", "n_loci"]).assign(n_loci_total=len(lo), unit="loci", denominator="locus"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
