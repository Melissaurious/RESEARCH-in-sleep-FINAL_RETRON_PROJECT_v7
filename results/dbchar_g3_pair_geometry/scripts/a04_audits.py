#!/usr/bin/env python3
"""a04 - three audits g3 owes before its geometry can be read as a prior.

(A) `position_relative_to_rt`: what the shipped field actually contains. Before calling it
    wrong, every plausible reference frame is tested - genomic vs transcription-relative, from
    either RT end, to either ncRNA end, signed or unsigned, and against the anchor. A field
    that disagrees because of a frame convention is a semantic mismatch, not an error.

(B) retron-CM placements beside NON-Retron-labelled RTs. The covariance models are retron
    ncRNA models, so the near-total absence of calls outside Retron-labelled files is DETECTOR
    SCOPE, not biological absence. The rare placements that do occur there are preserved as an
    explicit candidate population and compared with the canonical Retron geometry. Stage 1 does
    not call them novel or divergent retrons.

(C) the downstream distance mode. A tight cluster of downstream placements is audited against
    window geometry, database, family, model, contig-edge state and a fixed-offset signature
    before it is allowed to be read as biology.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    p = pd.read_parquet(W / "derived" / "rt_ncrna_pairs_v1.parquet")
    e = p[p.geometry_eligible].copy()
    can = p[p.canonical].copy()

    # ================= (A) the shipped position_relative_to_rt =======================
    s = e[e.position_relative_to_rt.notna()].copy()
    plus = s.rt_strand.eq("+")
    cand = {
        "computed_signed_distance_transcription_relative": s.signed_distance_bp,
        "gap_bp_unsigned": s.gap_bp,
        "nc_start_minus_rt_start": s.nc_start - s.rt_start,
        "nc_start_minus_rt_end": s.nc_start - s.rt_end,
        "nc_end_minus_rt_start": s.nc_end - s.rt_start,
        "nc_end_minus_rt_end": s.nc_end - s.rt_end,
        "rt_start_minus_nc_end": s.rt_start - s.nc_end,
        "rt_start_minus_nc_start": s.rt_start - s.nc_start,
        "nc_start_minus_anchor_center": s.nc_start - ((s.rt_start + s.rt_end) // 2),
        "nc_start_minus_window_start": s.nc_start - s.win_start,
        "genomic_signed_gap_not_strand_corrected": np.where(
            s.nc_end < s.rt_start, -s.gap_bp, np.where(s.rt_end < s.nc_start, s.gap_bp, 0)),
        "strand_corrected_gap_negated_on_minus": np.where(
            plus, s.signed_distance_bp, -s.signed_distance_bp),
    }
    rows = []
    for name, v in cand.items():
        v = pd.Series(v, index=s.index)
        eq = (v == s.position_relative_to_rt)
        rows.append([name, int(eq.sum()), len(s), round(100 * eq.mean(), 4),
                     int(eq[plus].sum()), int(plus.sum()),
                     int(eq[~plus].sum()), int((~plus).sum())])
    w(T / "g3_shipped_field_semantics.tsv", pd.DataFrame(rows, columns=[
        "candidate_reference_frame", "n_equal", "n_compared", "pct_equal",
        "n_equal_plus_strand", "n_plus_strand", "n_equal_minus_strand", "n_minus_strand"])
      .sort_values("n_equal", ascending=False).assign(
          unit="placements", denominator="geometry-eligible placements where the field is non-null"))
    # What the field looks like in itself, and where it is present at all.
    w(T / "g3_shipped_field_profile.tsv", pd.DataFrame([
        ["placements_total", len(p), ""],
        ["field_null", int(p.position_relative_to_rt.isna().sum()),
         round(100 * p.position_relative_to_rt.isna().mean(), 4)],
        ["field_present", int(p.position_relative_to_rt.notna().sum()),
         round(100 * p.position_relative_to_rt.notna().mean(), 4)],
        ["field_present_and_geometry_eligible", len(s), ""],
        ["field_value_min", float(s.position_relative_to_rt.min()), ""],
        ["field_value_median", float(s.position_relative_to_rt.median()), ""],
        ["field_value_max", float(s.position_relative_to_rt.max()), ""],
        ["field_value_negative", int((s.position_relative_to_rt < 0).sum()), ""],
        ["field_value_zero", int((s.position_relative_to_rt == 0).sum()), ""],
        ["field_present_on_minus_strand_RTs", int((~plus).sum()), ""],
    ], columns=["measure", "value", "pct"]).assign(
        unit="placements", denominator="all placements, or the non-null subset where stated"))
    # What the field IS, once no coordinate frame explains it: its variation is dominated by
    # the negative of the RT's offset into its own window, plus a small additive term that
    # tracks the ncRNA's intergenic-region INDEX. That is an index mixed with a coordinate,
    # which is why no bp reference frame reproduces it.
    rt_off = s.rt_start - s.win_start
    k = s.position_relative_to_rt + rt_off
    ir_idx = s.intergenic_region_id.str.extract(r"_intergenic_(\d+)$")[0].astype(float)
    nc_idx = s.ncrna_id.str.extract(r"(\d+)$")[0].astype(float)
    w(T / "g3_shipped_field_structure.tsv", pd.DataFrame([
        ["pearson_r(field, -(rt_start - win_start))",
         round(float(np.corrcoef(s.position_relative_to_rt, -rt_off)[0, 1]), 6), "", ""],
        ["residual k = field + (rt_start - win_start): min", float(k.min()), "", ""],
        ["residual k: median", float(k.median()), "", ""],
        ["residual k: max", float(k.max()), "", ""],
        ["residual k: distinct values", int(k.nunique()), "",
         "a bp distance would not be confined to a handful of small integers"],
        ["k == intergenic_region_index - 1", int((k == ir_idx - 1).sum()),
         round(100 * (k == ir_idx - 1).mean(), 4), "the single best explanation of the residual"],
        ["k == intergenic_region_index", int((k == ir_idx).sum()),
         round(100 * (k == ir_idx).mean(), 4), ""],
        ["k == ncrna_index", int((k == nc_idx).sum()), round(100 * (k == nc_idx).mean(), 4), ""],
        ["field == (intergenic_region_index - 1) - (rt_start - win_start)",
         int((s.position_relative_to_rt == (ir_idx - 1) - rt_off).sum()),
         round(100 * (s.position_relative_to_rt == (ir_idx - 1) - rt_off).mean(), 4),
         "an INDEX minus a COORDINATE - not a distance in any frame"],
    ], columns=["measure", "value", "pct", "note"]).assign(
        n_compared=len(s), unit="placements",
        denominator="geometry-eligible placements where the field is non-null"))
    w(T / "g3_shipped_field_presence_by_stratum.tsv", p.assign(
        present=p.position_relative_to_rt.notna()).groupby(
        ["file_label", "source_database"]).agg(
        n_placements=("ncrna_id", "size"), n_field_present=("present", "sum")).reset_index()
      .query("n_field_present > 0").assign(
          unit="placements", denominator="placements of that family and database"))

    # ================= (B) retron CMs beside non-Retron RTs ==========================
    nr = e[~e.file_label.isin(["Retron"])].copy()
    nr["is_multi"] = nr.file_label.eq("MULTI")
    w(T / "g3_nonretron_cm_placements.tsv", nr.groupby(
        ["file_label", "detection_model"]).agg(
        n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_exact_ncrna=("nc_seq_hash", "nunique"),
        n_genomes=("genome_id_norm", "nunique"), n_species=("tax_species", "nunique"),
        n_databases=("source_database", "nunique"),
        n_canonical=("canonical", "sum"),
        median_signed_distance_bp=("signed_distance_bp", "median"),
        pct_upstream=("direction", lambda x: round(100 * (x == "upstream").mean(), 2)),
        pct_same_strand=("same_strand", lambda x: round(100 * x.mean(), 2)),
        median_cds_between=("n_cds_between", "median")).reset_index().sort_values(
            "n_placements", ascending=False).assign(
                n_nonretron_placements=len(nr), unit="placements",
                denominator="geometry-eligible placements at non-Retron-labelled RTs"))
    # side-by-side with the canonical Retron geometry, same columns, same rules
    def geom(df, label):
        return pd.DataFrame([[label, len(df), df.locus_key.nunique(),
                              round(100 * df.direction.eq("upstream").mean(), 3),
                              round(100 * df.direction.eq("downstream").mean(), 3),
                              round(100 * df.direction.eq("overlapping").mean(), 3),
                              float(df.signed_distance_bp.abs().median()),
                              float(df.signed_distance_bp.abs().quantile(.25)),
                              float(df.signed_distance_bp.abs().quantile(.75)),
                              round(100 * df.same_strand.mean(), 3),
                              float(df.n_cds_between.median()),
                              round(100 * df.n_cds_between.eq(0).mean(), 3)]],
                            columns=["population", "n_placements", "n_loci", "pct_upstream",
                                     "pct_downstream", "pct_overlapping", "median_abs_distance_bp",
                                     "q25_abs_distance_bp", "q75_abs_distance_bp",
                                     "pct_same_strand", "median_cds_between", "pct_zero_cds_between"])
    comp = pd.concat([
        geom(can[can.file_label.eq("Retron")], "CANONICAL_Retron"),
        geom(e[e.file_label.eq("Retron")], "ELIGIBLE_Retron"),
        geom(nr[~nr.is_multi], "ELIGIBLE_non_Retron_single_family"),
        geom(nr[nr.is_multi], "ELIGIBLE_MULTI_stratum"),
    ], ignore_index=True)
    w(T / "g3_nonretron_vs_retron_geometry.tsv", comp.assign(
        unit="placements", denominator="the population named in the row"))
    nr.to_parquet(W / "derived" / "rt_ncrna_nonretron_candidates_v1.parquet", index=False,
                  compression="zstd")
    print(f"  rt_ncrna_nonretron_candidates_v1: {len(nr):,d} placements", flush=True)

    # ================= (C) the downstream distance mode ==============================
    d = can[can.direction.eq("downstream")].copy()
    if len(d):
        med = float(d.signed_distance_bp.median())
        lo, hi = med - 150, med + 150
        d["in_mode"] = d.signed_distance_bp.between(lo, hi)
        w(T / "g3_downstream_mode_profile.tsv", pd.DataFrame([
            ["canonical_downstream_placements", len(d), ""],
            ["median_signed_distance_bp", med, ""],
            ["placements_within_150bp_of_the_median", int(d.in_mode.sum()),
             round(100 * d.in_mode.mean(), 3)],
            ["iqr_bp", float(d.signed_distance_bp.quantile(.75) - d.signed_distance_bp.quantile(.25)), ""],
            ["distinct_exact_ncrna_in_the_mode", int(d[d.in_mode].nc_seq_hash.nunique()), ""],
            ["distinct_exact_rt_in_the_mode", int(d[d.in_mode].rt_seq_hash.nunique()), ""],
            ["distinct_loci_in_the_mode", int(d[d.in_mode].locus_key.nunique()), ""],
            ["distinct_species_in_the_mode", int(d[d.in_mode].tax_species.nunique()), ""],
            ["distinct_detection_models_in_the_mode", int(d[d.in_mode].detection_model.nunique()), ""],
            ["distinct_source_databases_in_the_mode", int(d[d.in_mode].source_database.nunique()), ""],
        ], columns=["measure", "value", "pct"]).assign(
            unit="placements", denominator="CANONICAL downstream placements"))
        # a fixed offset from a WINDOW boundary would be an extraction signature, not biology
        d["nc_start_minus_win_start"] = d.nc_start - d.win_start
        d["win_end_minus_nc_end"] = d.win_end - d.nc_end
        d["rt_start_minus_win_start"] = d.rt_start - d.win_start
        w(T / "g3_downstream_mode_window_signature.tsv", pd.DataFrame([
            ["nc_start - win_start", d.nc_start_minus_win_start.median(),
             d.nc_start_minus_win_start.std(), int(d.nc_start_minus_win_start.nunique())],
            ["win_end - nc_end", d.win_end_minus_nc_end.median(),
             d.win_end_minus_nc_end.std(), int(d.win_end_minus_nc_end.nunique())],
            ["rt_start - win_start", d.rt_start_minus_win_start.median(),
             d.rt_start_minus_win_start.std(), int(d.rt_start_minus_win_start.nunique())],
            ["signed_distance_bp", d.signed_distance_bp.median(),
             d.signed_distance_bp.std(), int(d.signed_distance_bp.nunique())],
        ], columns=["offset", "median", "std", "n_distinct_values"]).assign(
            n_placements=len(d), unit="placements", denominator="CANONICAL downstream placements",
            note="a near-zero spread on a window-relative offset would mark an extraction artefact"))
        w(T / "g3_downstream_mode_strata.tsv", d.groupby(
            ["in_mode", "source_database", "file_label", "detection_model"]).agg(
            n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
            n_species=("tax_species", "nunique"),
            pct_clipped_end=("clipped_end_flag", lambda x: round(100 * x.mean(), 2)),
            pct_true_start_clipped=("true_start_clipped", lambda x: round(100 * x.mean(), 2)),
            pct_nc_at_window_edge=("nc_at_window_edge", lambda x: round(100 * x.mean(), 2)),
            median_cds_between=("n_cds_between", "median")).reset_index().sort_values(
                "n_placements", ascending=False).assign(
                    unit="placements", denominator="CANONICAL downstream placements in that stratum"))
        # is the mode one ncRNA sequence repeated, or many?
        top = d[d.in_mode].groupby("nc_seq_hash").agg(
            n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
            n_species=("tax_species", "nunique"), detection_model=("detection_model", "first"),
            median_signed_distance_bp=("signed_distance_bp", "median")).reset_index().sort_values(
                "n_placements", ascending=False).head(30)
        w(T / "g3_downstream_mode_top_sequences.tsv", top.assign(
            n_in_mode=int(d.in_mode.sum()), unit="placements",
            denominator="CANONICAL downstream placements within 150 bp of the median (top 30 sequences)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
