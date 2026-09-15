#!/usr/bin/env python3
"""b01 - the non-redundant per-family RT/ncRNA descriptive baseline.

Declared views (PLAN.md), fixed before any data is read:

  V-RT-SINGLE   one observation per EXACT RT sequence whose occurrences all carry one family
                label. This is the per-family population; a protein is counted once however
                many loci carry it.
  V-RT-CROSS    exact RTs whose occurrences span more than one family label - their own
                stratum, never folded into a single family (the prior project's
                <MULTI_FAMILY_KEY> bucket, kept explicit here).
  V-RT-MULTI    exact RTs occurring in the MULTI file - the unresolved multi-label stratum.
  V-NCRNA       one observation per exact ncRNA sequence, from the g3 placement table.

Completeness is three-state and NEVER reads a missing Prodigal flag as "partial": that
conflation is a known defect of the prior gate (c18 counted NULL as partial while c04 declared
it neither). Outlier fences are computed WITHIN a family, never pooled.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --- DECLARED before any data is read -------------------------------------------------
IQR_K = 1.5              # Tukey fence multiplier
MIN_GROUP = 30           # a family smaller than this gets no fences, and says so
TOP_OUTLIERS = 20        # named outliers listed per family


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    D, W = Path(a.derived), Path(a.work)
    T, DV = W / "tables", W / "derived"
    T.mkdir(parents=True, exist_ok=True)
    DV.mkdir(parents=True, exist_ok=True)

    r = pd.read_parquet(D / "rt_records_v1.parquet", columns=[
        "record_key", "is_first_copy", "rt_seq_hash", "rt_aa_len", "file_label", "multilabel",
        "type_set_norm", "source_database", "genome_id_norm", "tax_species", "locus_key",
        "elig_rt_coords", "elig_rt_length", "elig_rt_completeness", "rtcds_partial",
        "orf_start_codon_ok", "orf_stop_ok", "rt_at_window_edge", "true_start_clipped",
        "clipped_end_flag", "rt_internal_stops", "rt_nonstd_residues", "bt_status",
        "bt_internal_stops_dna"])
    f = r[r.is_first_copy]

    # ---- build the exact-RT view ------------------------------------------------------
    g = f.groupby("rt_seq_hash", sort=True)
    ex = pd.DataFrame({
        "rt_aa_len": g.rt_aa_len.first(),
        "n_records": g.size(), "n_loci": g.locus_key.nunique(),
        "n_genomes": g.genome_id_norm.nunique(), "n_species": g.tax_species.nunique(),
        "n_databases": g.source_database.nunique(),
        "n_family_labels": g.file_label.nunique(),
        "family_label": g.file_label.first(),
        "any_multilabel": g.multilabel.any(),
        "n_verified": g.elig_rt_coords.sum(),
        "n_internal_stops_reported": g.rt_internal_stops.max(),
        "n_nonstd_residues": g.rt_nonstd_residues.max(),
        "any_internal_stop_in_dna": g.bt_internal_stops_dna.max(),
        "n_edge": g.rt_at_window_edge.sum(),
        "n_true_start_clipped": g.true_start_clipped.sum(),
        "n_clipped_end": g.clipped_end_flag.sum(),
    }).reset_index()

    # completeness, three-state, aggregated over the RT's records
    comp = f.assign(
        complete=lambda d: np.where(
            d.rtcds_partial.eq("00"), "complete_prodigal",
            np.where(d.rtcds_partial.isin(["01", "10", "11"]), "partial_prodigal",
                     np.where(d.orf_start_codon_ok.fillna(False) & d.orf_stop_ok.fillna(False)
                              & d.elig_rt_coords, "complete_by_codons_no_prodigal_call",
                              "no_completeness_evidence"))))
    cg = comp.groupby("rt_seq_hash").complete
    ex["completeness_states"] = cg.agg(lambda s: "|".join(sorted(set(s)))).values
    ex["completeness_class"] = np.where(
        ex.completeness_states.eq("complete_prodigal"), "all_complete",
        np.where(ex.completeness_states.str.contains("complete"), "mixed_or_codon_evidence",
                 np.where(ex.completeness_states.eq("no_completeness_evidence"),
                          "no_evidence", "all_partial")))
    ex["view"] = np.where(ex.family_label.eq("MULTI"), "V-RT-MULTI",
                          np.where(ex.n_family_labels > 1, "V-RT-CROSS", "V-RT-SINGLE"))
    # an exact RT seen in MULTI *and* a family file is cross-labelled, not single
    ex.loc[(ex.n_family_labels > 1) & ex.family_label.eq("MULTI"), "view"] = "V-RT-CROSS"
    ex.to_parquet(DV / "rt_family_baseline_v1.parquet", index=False, compression="zstd")
    print(f"  rt_family_baseline_v1: {len(ex):,d} exact RTs", flush=True)

    w(T / "g4_views.tsv", ex.groupby("view").agg(
        n_exact_rt=("rt_seq_hash", "size"), n_records=("n_records", "sum"),
        n_loci=("n_loci", "sum"), median_aa_len=("rt_aa_len", "median")).reset_index().assign(
            n_exact_rt_total=len(ex), unit="exact RT sequences",
            denominator="exact RT sequences in the corpus (501,561)"))

    # Distinct exact RTs per FILE LABEL with no view filter - the quantity the independent
    # awk route can recount directly (a protein in two family files counts in both).
    # Computed over ALL records, not first copies: a byte-identical line filed in two family
    # files is a first copy in only one of them, and the other label would silently lose the
    # sequence. The g2 unit ladder deduplicates; this comparison table deliberately does not.
    w(T / "g4_exact_rt_per_family_label.tsv", r.groupby("file_label").agg(
        n_exact_rt=("rt_seq_hash", "nunique"), n_records=("record_key", "size"),
        min_aa_len=("rt_aa_len", "min"), max_aa_len=("rt_aa_len", "max")).reset_index()
      .sort_values("n_exact_rt", ascending=False).assign(
          unit="exact RT sequences", denominator="distinct RT sequences in that source file"))

    single = ex[ex.view.eq("V-RT-SINGLE")]

    # ---- 1 · RT length per family ------------------------------------------------------
    q = single.groupby("family_label").rt_aa_len
    stats = pd.DataFrame({
        "n_exact_rt": q.size(), "min": q.min(), "q25": q.quantile(.25), "median": q.median(),
        "q75": q.quantile(.75), "max": q.max(), "mean": q.mean().round(2),
        "std": q.std().round(2)}).reset_index()
    stats["iqr"] = stats.q75 - stats.q25
    stats["fence_low"] = (stats.q25 - IQR_K * stats.iqr).round(2)
    stats["fence_high"] = (stats.q75 + IQR_K * stats.iqr).round(2)
    stats["fences_declared"] = stats.n_exact_rt >= MIN_GROUP
    stats.loc[~stats.fences_declared, ["fence_low", "fence_high"]] = np.nan
    w(T / "g4_rt_length_by_family.tsv", stats.sort_values("n_exact_rt", ascending=False).assign(
        unit="exact RT sequences", denominator="V-RT-SINGLE exact RTs of that family label",
        rule=f"Tukey k={IQR_K} within family; no fences below n={MIN_GROUP}"))

    # named outliers, with their own values landed
    m = single.merge(stats[["family_label", "fence_low", "fence_high", "fences_declared"]],
                     on="family_label", how="left")
    out = m[m.fences_declared & ((m.rt_aa_len < m.fence_low) | (m.rt_aa_len > m.fence_high))].copy()
    out["side"] = np.where(out.rt_aa_len < out.fence_low, "below", "above")
    w(T / "g4_rt_length_outlier_rates.tsv", out.groupby(["family_label", "side"]).agg(
        n_outliers=("rt_seq_hash", "size"), median_aa_len=("rt_aa_len", "median"),
        min_aa_len=("rt_aa_len", "min"), max_aa_len=("rt_aa_len", "max")).reset_index().merge(
        stats[["family_label", "n_exact_rt"]], on="family_label").assign(
            unit="exact RT sequences", denominator="V-RT-SINGLE exact RTs of that family label"))
    named = (out.sort_values(["family_label", "rt_aa_len"])
             .groupby("family_label").head(TOP_OUTLIERS)
             [["family_label", "side", "rt_seq_hash", "rt_aa_len", "n_loci", "n_species",
               "completeness_class", "n_internal_stops_reported", "n_edge", "bt" if False else "n_verified"]])
    w(T / "g4_rt_length_named_outliers.tsv", named.assign(
        unit="exact RT sequences", denominator=f"the {TOP_OUTLIERS} smallest outliers per family"))

    # ---- 2 · completeness per family ---------------------------------------------------
    w(T / "g4_completeness_by_family.tsv", single.groupby(
        ["family_label", "completeness_class"]).agg(
        n_exact_rt=("rt_seq_hash", "size"), median_aa_len=("rt_aa_len", "median")).reset_index()
      .merge(stats[["family_label", "n_exact_rt"]].rename(
          columns={"n_exact_rt": "n_exact_rt_in_family"}), on="family_label").assign(
              unit="exact RT sequences", denominator="V-RT-SINGLE exact RTs of that family label",
              note="a missing Prodigal partial flag is 'no_completeness_evidence', never 'partial'"))
    w(T / "g4_completeness_states_raw.tsv", single.groupby("completeness_states").agg(
        n_exact_rt=("rt_seq_hash", "size")).reset_index().assign(
            n_single=len(single), unit="exact RT sequences", denominator="V-RT-SINGLE exact RTs"))

    # ---- 3 · redundancy and sequence anomalies per family ------------------------------
    w(T / "g4_family_composition.tsv", single.groupby("family_label").agg(
        n_exact_rt=("rt_seq_hash", "size"), n_records=("n_records", "sum"),
        n_loci=("n_loci", "sum"), median_loci_per_exact_rt=("n_loci", "median"),
        max_loci_per_exact_rt=("n_loci", "max"),
        n_exact_rt_in_one_locus_only=("n_loci", lambda s: int((s == 1).sum())),
        n_with_internal_stops=("n_internal_stops_reported", lambda s: int((s > 0).sum())),
        n_with_nonstandard_residues=("n_nonstd_residues", lambda s: int((s > 0).sum())),
        n_with_dna_internal_stops=("any_internal_stop_in_dna", lambda s: int((s > 0).sum())),
        n_edge_touching=("n_edge", lambda s: int((s > 0).sum()))).reset_index().sort_values(
            "n_exact_rt", ascending=False).assign(
                unit="exact RT sequences", denominator="V-RT-SINGLE exact RTs of that family label"))

    # ---- 4 · the ncRNA baseline --------------------------------------------------------
    p = pd.read_parquet(D / "rt_ncrna_pairs_v1.parquet", columns=[
        "nc_seq_hash", "nc_seq_len", "detection_model", "file_label", "geometry_eligible",
        "canonical", "locus_key", "tax_species", "evalue", "score", "has_structure_annotation"])
    pe = p[p.geometry_eligible] if len(p) else p
    if not len(pe):
        # A corpus slice can legitimately carry no ncRNA call (the controls' fixture does).
        # Emit the ncRNA tables empty rather than failing: an absent population is a value.
        for name, cols in (("g4_ncrna_length_by_model.tsv",
                            ["detection_model", "n_exact_ncrna", "min", "q25", "median", "q75", "max"]),
                           ("g4_ncrna_model_by_family.tsv",
                            ["family_label", "detection_model", "n_exact_ncrna", "median_len", "median_score"]),
                           ("g4_ncrna_structure_coverage.tsv", ["measure", "n", "pct"])):
            w(T / name, pd.DataFrame(columns=cols + ["unit", "denominator"]))
        pd.DataFrame(columns=["nc_seq_hash"]).to_parquet(
            DV / "ncrna_family_baseline_v1.parquet", index=False, compression="zstd")
        return 0
    nc = pe.groupby("nc_seq_hash").agg(
        nc_seq_len=("nc_seq_len", "first"), n_placements=("locus_key", "size"),
        n_loci=("locus_key", "nunique"), n_species=("tax_species", "nunique"),
        n_models=("detection_model", "nunique"), detection_model=("detection_model", "first"),
        n_families=("file_label", "nunique"), family_label=("file_label", "first"),
        median_score=("score", "median"), median_evalue=("evalue", "median"),
        any_structure=("has_structure_annotation", "any")).reset_index()
    nc.to_parquet(DV / "ncrna_family_baseline_v1.parquet", index=False, compression="zstd")
    lq = nc.groupby("detection_model").nc_seq_len
    w(T / "g4_ncrna_length_by_model.tsv", pd.DataFrame({
        "n_exact_ncrna": lq.size(), "min": lq.min(), "q25": lq.quantile(.25),
        "median": lq.median(), "q75": lq.quantile(.75), "max": lq.max()}).reset_index()
      .sort_values("n_exact_ncrna", ascending=False).assign(
          unit="exact ncRNA sequences", denominator="exact ncRNA sequences called by that model"))
    w(T / "g4_ncrna_model_by_family.tsv", nc.groupby(["family_label", "detection_model"]).agg(
        n_exact_ncrna=("nc_seq_hash", "size"), median_len=("nc_seq_len", "median"),
        median_score=("median_score", "median")).reset_index().sort_values(
            "n_exact_ncrna", ascending=False).assign(
                unit="exact ncRNA sequences",
                denominator="exact ncRNA sequences of that family label and model"))
    w(T / "g4_ncrna_structure_coverage.tsv", pd.DataFrame([
        ["exact_ncRNA_sequences", len(nc), ""],
        ["with_a_structure_annotation", int(nc.any_structure.sum()),
         round(100 * nc.any_structure.mean(), 4)],
        ["called_by_more_than_one_model", int((nc.n_models > 1).sum()),
         round(100 * (nc.n_models > 1).mean(), 4)],
        ["seen_in_more_than_one_family_label", int((nc.n_families > 1).sum()),
         round(100 * (nc.n_families > 1).mean(), 4)],
    ], columns=["measure", "n", "pct"]).assign(
        unit="exact ncRNA sequences", denominator="exact ncRNA sequences with an eligible placement"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
