#!/usr/bin/env python3
"""a02 - RT<->ncRNA geometry priors on explicitly named populations.

Populations (declared in g3lib / PLAN.md):
  ALL          every placement in rt_ncrna_pairs_v1
  ELIGIBLE     geometry-eligible placements (record verified, ncRNA inside the window, strand present)
  CANONICAL    eligible, not touching a window edge, not a duplicate call
  ATYPICAL     eligible but not canonical

These are empirical priors and QC information. They are NOT converted into filters here, and
no threshold in this file removes a record from the canonical representation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g3lib as G  # noqa: E402


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    D, W = Path(a.derived), Path(a.work)
    T = W / "tables"
    T.mkdir(parents=True, exist_ok=True)
    p = pd.read_parquet(W / "derived" / "rt_ncrna_pairs_v1.parquet")
    ex = pd.read_parquet(W / "derived" / "rt_ncrna_exact_pairs_v1.parquet")
    rec = pd.read_parquet(D / "rt_records_v1.parquet",
                          columns=["record_key", "locus_key", "file_label", "source_database",
                                   "n_ncrna", "is_first_copy", "elig_geometry", "rt_seq_hash"])

    pops = {"ALL": p, "ELIGIBLE": p[p.geometry_eligible], "CANONICAL": p[p.canonical],
            "ATYPICAL": p[p.geometry_eligible & ~p.canonical]}

    def by_pop(fn, name):
        out = []
        for k, sub in pops.items():
            d = fn(sub).reset_index()
            d.insert(0, "population", k)
            d["n_in_population"] = len(sub)
            out.append(d)
        w(T / name, pd.concat(out, ignore_index=True))

    # ---- 1 · populations and why placements fall out --------------------------------
    rows = [[k, len(v), round(100 * len(v) / len(p), 4)] for k, v in pops.items()]
    w(T / "g3_populations.tsv", pd.DataFrame(rows, columns=["population", "n_placements", "pct_of_ALL"])
      .assign(unit="placements", denominator="all placements in rt_ncrna_pairs_v1"))
    w(T / "g3_ineligible_reasons.tsv", p[~p.geometry_eligible].geometry_ineligible_reason
      .value_counts().rename("n_placements").reset_index().assign(
          n_placements_total=len(p), unit="placements", denominator="all placements"))

    # ---- 2 · the zero-ncRNA class, per family (detector scope is NOT uniform) --------
    f = rec[rec.is_first_copy]
    loci = f.groupby(["file_label", "locus_key"]).n_ncrna.max().reset_index()
    z = loci.groupby("file_label").agg(n_loci=("locus_key", "size"),
                                       n_loci_with_call=("n_ncrna", lambda s: int((s > 0).sum()))).reset_index()
    z["n_loci_zero_ncrna"] = z.n_loci - z.n_loci_with_call
    z["pct_zero"] = (100 * z.n_loci_zero_ncrna / z.n_loci).round(4)
    w(T / "g3_zero_class_by_family.tsv", z.sort_values("n_loci", ascending=False).assign(
        unit="loci", denominator="loci of that family label (distinct raw records)"))
    ret = f[f.file_label.eq("Retron")].groupby(["source_database", "locus_key"]).n_ncrna.max().reset_index()
    zr = ret.groupby("source_database").agg(n_loci=("locus_key", "size"),
                                            n_loci_with_call=("n_ncrna", lambda s: int((s > 0).sum()))).reset_index()
    zr["n_loci_zero_ncrna"] = zr.n_loci - zr.n_loci_with_call
    zr["pct_zero"] = (100 * zr.n_loci_zero_ncrna / zr.n_loci).round(4)
    w(T / "g3_zero_class_retron_by_database.tsv", zr.assign(
        unit="loci", denominator="Retron loci of that source_database"))

    # ---- 3 · direction, distance, strand, CDS between, overlap ----------------------
    by_pop(lambda s: s.groupby("direction").size().rename("n_placements"), "g3_direction.tsv")
    by_pop(lambda s: s.groupby(["direction", "distance_bin"]).size().rename("n_placements"),
           "g3_distance_bins.tsv")
    by_pop(lambda s: s.groupby("direction").signed_distance_bp.agg(
        n="size", median="median", q25=lambda x: x.quantile(.25), q75=lambda x: x.quantile(.75),
        min="min", max="max"), "g3_distance_stats.tsv")
    by_pop(lambda s: s.groupby(["direction", s.same_strand.astype("string").fillna("missing")]).size()
           .rename("n_placements"), "g3_same_strand.tsv")
    by_pop(lambda s: s.groupby(["direction", "cds_between_bin"]).size().rename("n_placements"),
           "g3_cds_between.tsv")
    by_pop(lambda s: s.groupby([(s.overlap_bp > 0).rename("overlaps_rt"),
                                (s.n_cds_overlapping_ncrna_recomputed > 0).rename("overlaps_any_cds")])
           .size().rename("n_placements"), "g3_overlap.tsv")

    # ---- 3b · the two distributions the report plots, as landed tables ---------------
    # bp spacing: a histogram with explicit edges, so the figure script reads numbers and
    # never touches the pair table.
    edges = [-10000, -5000, -2000, -1000, -500, -200, -100, -50, -20, -5, 0,
             5, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    hrows = []
    for k, sub in pops.items():
        v = sub.signed_distance_bp.dropna()
        cut = pd.cut(v, bins=edges, include_lowest=True)
        cnt = cut.value_counts().sort_index()
        for iv, n in cnt.items():
            hrows.append([k, iv.left, iv.right, int(n), len(v),
                          round(100 * n / len(v), 4) if len(v) else 0])
        hrows.append([k, "below", edges[0], int((v < edges[0]).sum()), len(v),
                      round(100 * (v < edges[0]).mean(), 4) if len(v) else 0])
        hrows.append([k, edges[-1], "above", int((v > edges[-1]).sum()), len(v),
                      round(100 * (v > edges[-1]).mean(), 4) if len(v) else 0])
    w(T / "g3_distance_histogram.tsv", pd.DataFrame(hrows, columns=[
        "population", "bin_left_bp", "bin_right_bp", "n_placements", "n_in_population",
        "pct_of_population"]).assign(unit="placements",
                                     denominator="placements of that population with a defined signed distance"))

    # intervening CDS: 0, 1, 2, 3, >3 explicitly - not a mean
    def cds_explicit(df, label, extra=None):
        v = df.n_cds_between
        rows = []
        for lab, mask in (("0", v == 0), ("1", v == 1), ("2", v == 2), ("3", v == 3), (">3", v > 3)):
            rows.append([label, extra or "", lab, int(mask.sum()), len(v),
                         round(100 * mask.mean(), 4) if len(v) else 0])
        return rows
    rows = []
    for k, sub in pops.items():
        rows += cds_explicit(sub, k)
    fam = p[p.canonical].groupby("file_label")
    for name, sub in fam:
        if len(sub) >= 30:
            rows += cds_explicit(sub, "CANONICAL_by_family", name)
    w(T / "g3_cds_between_explicit.tsv", pd.DataFrame(rows, columns=[
        "population", "stratum", "n_cds_between", "n_placements", "n_in_population",
        "pct_of_population"]).assign(unit="placements",
                                     denominator="placements of that population/stratum"))

    # ---- 4 · multiplicity, and duplicate call vs biological multiplicity -------------
    by_pop(lambda s: s.groupby("multiplicity_class").size().rename("n_placements"),
           "g3_multiplicity_class.tsv")
    lo = p[p.geometry_eligible].groupby("locus_key").agg(
        n_calls=("ncrna_id", "size"), n_seqs=("nc_seq_hash", "nunique"),
        n_models=("detection_model", "nunique")).reset_index()
    w(T / "g3_calls_per_locus.tsv", pd.concat([
        lo.n_calls.clip(upper=10).value_counts().sort_index().rename("n_loci").reset_index()
        .assign(measure="calls_per_locus(capped_10)"),
        lo.n_seqs.clip(upper=10).value_counts().sort_index().rename("n_loci").reset_index()
        .assign(measure="distinct_ncrna_sequences_per_locus(capped_10)"),
        lo.n_models.clip(upper=5).value_counts().sort_index().rename("n_loci").reset_index()
        .assign(measure="distinct_detection_models_per_locus(capped_5)")], ignore_index=True)
      .assign(unit="loci", denominator="loci carrying >=1 geometry-eligible call"))

    # one ncRNA sequence across many RTs, and one RT across many ncRNA sequences
    deg_nc = ex.groupby("nc_seq_hash").rt_seq_hash.nunique()
    deg_rt = ex.groupby("rt_seq_hash").nc_seq_hash.nunique()
    w(T / "g3_pair_degree.tsv", pd.concat([
        deg_nc.clip(upper=20).value_counts().sort_index().rename("n").reset_index()
        .assign(measure="distinct_exact_RTs_per_exact_ncRNA(capped_20)", unit="exact ncRNA sequences",
                denominator="exact ncRNA sequences in the exact-pair view"),
        deg_rt.clip(upper=20).value_counts().sort_index().rename("n").reset_index()
        .assign(measure="distinct_exact_ncRNAs_per_exact_RT(capped_20)", unit="exact RT sequences",
                denominator="exact RT sequences in the exact-pair view")], ignore_index=True))
    w(T / "g3_pair_view_sizes.tsv", pd.DataFrame([
        ["placements_geometry_eligible", int(p.geometry_eligible.sum())],
        ["distinct_exact_pairs", len(ex)],
        ["distinct_exact_rt_in_pairs", int(ex.rt_seq_hash.nunique())],
        ["distinct_exact_ncrna_in_pairs", int(ex.nc_seq_hash.nunique())],
        ["loci_with_a_geometry_eligible_call", int(p[p.geometry_eligible].locus_key.nunique())],
        ["exact_pairs_seen_at_more_than_one_locus", int((ex.n_loci > 1).sum())],
        ["exact_pairs_in_more_than_one_species", int((ex.n_species > 1).sum())],
        ["exact_pairs_with_more_than_one_direction", int((ex.n_directions > 1).sum())],
    ], columns=["measure", "n"]).assign(unit="named per row", denominator="named per row"))

    # ---- 5 · model identity, family and database strata ------------------------------
    w(T / "g3_model_composition.tsv", p[p.canonical].groupby(
        ["detection_model", "file_label"]).agg(
        n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
        n_exact_ncrna=("nc_seq_hash", "nunique"),
        median_signed_distance_bp=("signed_distance_bp", "median")).reset_index()
      .sort_values("n_placements", ascending=False).assign(
          unit="placements", denominator="CANONICAL placements of that model and family"))
    w(T / "g3_geometry_by_family.tsv", p[p.canonical].groupby("file_label").agg(
        n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
        pct_upstream=("direction", lambda s: round(100 * (s == "upstream").mean(), 4)),
        pct_downstream=("direction", lambda s: round(100 * (s == "downstream").mean(), 4)),
        pct_overlapping=("direction", lambda s: round(100 * (s == "overlapping").mean(), 4)),
        median_abs_distance_bp=("signed_distance_bp", lambda s: s.abs().median()),
        pct_same_strand=("same_strand", lambda s: round(100 * s.mean(), 4)),
        median_cds_between=("n_cds_between", "median")).reset_index().assign(
            unit="placements", denominator="CANONICAL placements of that family label"))
    w(T / "g3_geometry_by_database.tsv", p[p.canonical].groupby("source_database").agg(
        n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
        pct_upstream=("direction", lambda s: round(100 * (s == "upstream").mean(), 4)),
        median_abs_distance_bp=("signed_distance_bp", lambda s: s.abs().median()),
        pct_same_strand=("same_strand", lambda s: round(100 * s.mean(), 4))).reset_index().assign(
            unit="placements", denominator="CANONICAL placements of that source_database"))

    # ---- 6 · QC of the shipped fields this gate refused to trust ---------------------
    qc = []
    shipped = p.position_relative_to_rt
    qc.append(["position_relative_to_rt_null", int(shipped.isna().sum()), len(p)])
    qc.append(["position_relative_to_rt_present", int(shipped.notna().sum()), len(p)])
    ok = p[shipped.notna() & p.geometry_eligible]
    qc.append(["shipped_value_equals_computed_signed_distance",
               int((ok.position_relative_to_rt == ok.signed_distance_bp).sum()), len(ok)])
    qc.append(["shipped_value_equals_nc_start_minus_rt_start",
               int((ok.position_relative_to_rt == (ok.nc_start - ok.rt_start)).sum()), len(ok)])
    qc.append(["shipped_value_equals_nc_start_minus_rt_end",
               int((ok.position_relative_to_rt == (ok.nc_start - ok.rt_end)).sum()), len(ok)])
    qc.append(["cds_overlap_shipped_agrees_with_recomputed",
               int(p.cds_overlap_agrees_with_shipped.sum()), len(p)])
    qc.append(["nc_length_field_equals_end_minus_start_plus_1",
               int((p.nc_len_field == (p.nc_end - p.nc_start + 1)).sum()), len(p)])
    qc.append(["orientation_corrected_true", int(p.orientation_corrected.sum()), len(p)])
    qc.append(["ncrna_outside_its_window", int((~p.nc_in_window).sum()), len(p)])
    qc.append(["ncrna_touching_a_window_edge", int(p.nc_at_window_edge.sum()), len(p)])
    w(T / "g3_shipped_field_qc.tsv", pd.DataFrame(qc, columns=["measure", "n", "denominator_n"])
      .assign(unit="placements", denominator="all placements, or the subset named in the measure"))

    # ---- 7 · the atypical catalogue --------------------------------------------------
    e = p[p.geometry_eligible]
    at = [
        ["overlapping_the_RT", int((e.overlap_bp > 0).sum())],
        ["distance_gt_5kb", int((e.signed_distance_bp.abs() > 5000).sum())],
        ["opposite_strand_to_RT", int((e.same_strand == False).sum())],  # noqa: E712
        ["more_than_2_CDS_between", int((e.n_cds_between > 2).sum())],
        ["duplicate_call_within_one_record",
         int((e.multiplicity_class == "duplicate_call_within_one_record").sum())],
        ["same_call_from_another_record_of_the_same_locus",
         int((e.multiplicity_class == "same_call_from_another_record_of_the_same_locus").sum())],
        ["locus_carrying_more_than_one_distinct_ncRNA_sequence",
         int((e.n_distinct_ncrna_seq_at_locus > 1).sum())],
        ["ncRNA_touching_a_window_edge", int(e.nc_at_window_edge.sum())],
        ["RT_touching_a_window_edge", int(e.rt_at_window_edge.sum())],
        ["window_clipped_at_contig_end", int(e.clipped_end_flag.sum())],
        ["true_start_clipped", int(e.true_start_clipped.sum())],
    ]
    w(T / "g3_atypical_catalogue.tsv", pd.DataFrame(at, columns=["atypical_class", "n_placements"])
      .assign(n_eligible=len(e), unit="placements", denominator="ELIGIBLE placements"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
