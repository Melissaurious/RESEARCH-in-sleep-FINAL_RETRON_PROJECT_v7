#!/usr/bin/env python3
"""p01 - build the RT<->ncRNA association (placement) table and the exact-pair view.

Inputs are the g2 derived datasets only; the raw corpus is not re-read. Every geometry column
is computed from coordinates by the conventions declared in g3lib (bases strictly between,
transcription-relative direction), never from the shipped `position_relative_to_rt`, which g1
measured as null for the large majority and which disagrees with the coordinates.

Outputs (to <work>/derived):
  rt_ncrna_pairs_v1.parquet        one row per (record, ncRNA call) placement
  rt_ncrna_exact_pairs_v1.parquet  one row per distinct (exact RT, exact ncRNA) pair
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g3lib as G  # noqa: E402

REC_COLS = ["source_file", "line_no", "record_key", "rt_system_id", "locus_key", "physical_locus_key",
            "rt_seq_hash", "rt_start", "rt_end", "rt_strand", "win_start", "win_end",
            "file_label", "source_database", "genome_id_norm", "taxonomy_system", "tax_species",
            "elig_geometry", "elig_geometry_reason", "is_first_copy", "n_ncrna", "n_cds",
            "rt_at_window_edge", "clipped_end_flag", "true_start_clipped", "window_inverted",
            "window_len_consistent", "rt_in_window", "bt_status", "n_rt_cds",
            "rtcds_start", "rtcds_end"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True, help="g2 derived datasets")
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    D, W = Path(a.derived), Path(a.work)
    out = W / "derived"
    out.mkdir(parents=True, exist_ok=True)

    nc = pd.read_parquet(D / "rt_ncrna_calls_v1.parquet")
    rec = pd.read_parquet(D / "rt_records_v1.parquet", columns=REC_COLS)
    p = nc.merge(rec, on=["source_file", "line_no"], how="left", validate="many_to_one")
    print(f"  placements={len(p):,d} records_with_calls={p.record_key.nunique():,d}", flush=True)

    rs, re_, ns, ne = (p.rt_start.to_numpy(), p.rt_end.to_numpy(),
                       p.nc_start.to_numpy(), p.nc_end.to_numpy())
    ok = ~(pd.isna(p.rt_start) | pd.isna(p.nc_start) | pd.isna(p.rt_end) | pd.isna(p.nc_end)).to_numpy()
    ov = np.maximum(0, np.minimum(re_, ne) - np.maximum(rs, ns) + 1)
    before = ne < rs
    after = re_ < ns
    gap = np.where(before, rs - ne - 1, np.where(after, ns - re_ - 1, 0))
    plus = (p.rt_strand == "+").to_numpy()
    upstream = (before == plus) & (ov <= 0)
    dirn = np.where(ov > 0, "overlapping",
                    np.where(~np.isin(p.rt_strand.to_numpy(), ["+", "-"]), "undetermined",
                             np.where(upstream, "upstream", "downstream")))
    signed = np.where(ov > 0, 0, np.where(upstream, -gap, gap)).astype("float64")
    signed[dirn == "undetermined"] = np.nan
    p["overlap_bp"] = np.where(ok, ov, np.nan)
    p["gap_bp"] = np.where(ok, gap, np.nan)
    p["direction"] = np.where(ok, dirn, "undetermined")
    p["signed_distance_bp"] = np.where(ok, signed, np.nan)
    # nullable boolean: a missing strand must stay missing, never read as False
    ss = pd.Series(pd.NA, index=p.index, dtype="boolean")
    both = p.nc_strand.isin(["+", "-"]) & p.rt_strand.isin(["+", "-"])
    ss[both] = (p.nc_strand == p.rt_strand)[both]
    p["same_strand"] = ss
    p["nc_in_window"] = (p.win_start <= p.nc_start) & (p.nc_end <= p.win_end)
    p["nc_at_window_edge"] = (p.nc_start == p.win_start) | (p.nc_end == p.win_end)
    p["distance_bin"] = [G.bin_label(v if pd.notna(v) else None, G.DIST_BINS)
                         for v in p.signed_distance_bp]

    # ---- CDS strictly between the RT and the ncRNA, and CDS overlapping the ncRNA ----
    keys = pa.array(p.record_key.unique())
    cds = pq.read_table(D / "rt_window_cds_v1.parquet",
                        columns=["source_file", "line_no", "cds_start", "cds_end", "is_rt_gene"])
    ck = pc.binary_join_element_wise(cds["source_file"].cast(pa.string()),
                                     pc.cast(cds["line_no"], pa.string()), ":")
    cds = cds.append_column("record_key", ck)
    cds = cds.filter(pc.is_in(cds["record_key"], value_set=keys)).to_pandas()
    print(f"  cds rows for records carrying calls={len(cds):,d}", flush=True)
    m = p[["record_key", "rt_start", "rt_end", "nc_start", "nc_end", "ncrna_id"]].merge(
        cds[["record_key", "cds_start", "cds_end", "is_rt_gene"]], on="record_key", how="left")
    lo = np.where(m.nc_end < m.rt_start, m.nc_end + 1, m.rt_end + 1)
    hi = np.where(m.nc_end < m.rt_start, m.rt_start - 1, m.nc_start - 1)
    m["between"] = (~m.is_rt_gene.fillna(False)) & (m.cds_start >= lo) & (m.cds_end <= hi)
    m["ov_nc"] = (m.cds_start <= m.nc_end) & (m.cds_end >= m.nc_start)
    g = m.groupby(["record_key", "ncrna_id"], sort=False)[["between", "ov_nc"]].sum()
    p = p.merge(g.rename(columns={"between": "n_cds_between", "ov_nc": "n_cds_overlapping_ncrna_recomputed"}),
                left_on=["record_key", "ncrna_id"], right_index=True, how="left")
    p["n_cds_between"] = p.n_cds_between.fillna(0).astype("int32")
    p["n_cds_overlapping_ncrna_recomputed"] = p.n_cds_overlapping_ncrna_recomputed.fillna(0).astype("int32")
    p["cds_overlap_agrees_with_shipped"] = (
        (p.n_cds_overlapping_ncrna_recomputed > 0) == p.has_cds_overlap)
    p["cds_between_bin"] = [G.bin_label(v, G.CDS_BINS) for v in p.n_cds_between]
    # Overlapping ANY CDS and overlapping the RT's own CDS are different questions: the second
    # is the one that bears on whether the ncRNA sits inside the RT gene model.
    has_rtcds = p.rtcds_start.notna() & p.rtcds_end.notna()
    ov_rt = np.maximum(0, np.minimum(p.rtcds_end, p.nc_end) - np.maximum(p.rtcds_start, p.nc_start) + 1)
    p["overlap_bp_rt_cds"] = np.where(has_rtcds, ov_rt, np.nan)
    p["overlaps_rt_cds"] = pd.array(np.where(has_rtcds, ov_rt > 0, None), dtype="boolean")
    p["overlaps_any_cds"] = p.n_cds_overlapping_ncrna_recomputed > 0
    p["overlaps_non_rt_cds"] = p.overlaps_any_cds & ~p.overlaps_rt_cds.fillna(False)

    # ---- multiplicity at the locus, and the duplicate-call class ---------------------
    gl = p.groupby("locus_key", sort=False)
    p["n_calls_at_locus"] = gl.ncrna_id.transform("size").astype("int32")
    p["n_distinct_ncrna_seq_at_locus"] = gl.nc_seq_hash.transform("nunique").astype("int32")
    # Two very different things would otherwise share the name "duplicate call": the SAME
    # record carrying the call twice (a detector duplicate) and one locus mined from two
    # databases, each record carrying its own copy (a re-mining duplicate). They are separated.
    p["n_calls_at_record"] = p.groupby("record_key", sort=False).ncrna_id.transform("size").astype("int32")
    in_rec = p.groupby(["record_key", "nc_seq_hash", "nc_start", "nc_end"], sort=False).ncrna_id.transform("size")
    at_locus = p.groupby(["locus_key", "nc_seq_hash", "nc_start", "nc_end"], sort=False).ncrna_id.transform("size")
    same_seq = p.groupby(["locus_key", "nc_seq_hash"], sort=False).ncrna_id.transform("size")
    p["multiplicity_class"] = np.where(
        p.n_calls_at_locus == 1, "single_call",
        np.where(in_rec > 1, "duplicate_call_within_one_record",
                 np.where(at_locus > 1, "same_call_from_another_record_of_the_same_locus",
                          np.where(same_seq > 1, "same_sequence_other_coordinates",
                                   "distinct_sequences"))))

    # ---- eligibility: geometry is only honest where the record and the call allow ----
    p["geometry_eligible"] = (p.elig_geometry & p.nc_in_window & p.nc_strand.isin(["+", "-"])
                              & p.is_first_copy)
    p["geometry_ineligible_reason"] = np.where(
        p.geometry_eligible, "",
        np.where(~p.is_first_copy, "byte_identical_duplicate_line",
                 np.where(~p.elig_geometry, "record:" + p.elig_geometry_reason.astype(str),
                          np.where(~p.nc_in_window, "ncrna_outside_window", "ncrna_strand_missing"))))
    p["canonical"] = (p.geometry_eligible & ~p.nc_at_window_edge
                      & (p.multiplicity_class != "duplicate_call_within_one_record"))
    p.to_parquet(out / "rt_ncrna_pairs_v1.parquet", index=False, compression="zstd")
    print(f"  rt_ncrna_pairs_v1: {len(p):,d} placements, geometry-eligible "
          f"{int(p.geometry_eligible.sum()):,d}, canonical {int(p.canonical.sum()):,d}", flush=True)

    # ---- the exact-pair view --------------------------------------------------------
    e = p[p.geometry_eligible].groupby(["rt_seq_hash", "nc_seq_hash"], sort=True)
    ex = pd.DataFrame({
        "n_placements": e.size(), "n_loci": e.locus_key.nunique(),
        "n_physical_loci": e.physical_locus_key.nunique(), "n_genomes": e.genome_id_norm.nunique(),
        "n_species": e.tax_species.nunique(), "n_source_databases": e.source_database.nunique(),
        "n_detection_models": e.detection_model.nunique(),
        "median_signed_distance_bp": e.signed_distance_bp.median(),
        "min_signed_distance_bp": e.signed_distance_bp.min(),
        "max_signed_distance_bp": e.signed_distance_bp.max(),
        "n_directions": e.direction.nunique(),
        "n_same_strand_true": e.same_strand.sum().astype("Int64"),
        "median_cds_between": e.n_cds_between.median()}).reset_index()
    ex.to_parquet(out / "rt_ncrna_exact_pairs_v1.parquet", index=False, compression="zstd")
    print(f"  rt_ncrna_exact_pairs_v1: {len(ex):,d} distinct (exact RT, exact ncRNA) pairs", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
