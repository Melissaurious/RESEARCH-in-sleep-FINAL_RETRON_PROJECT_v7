#!/usr/bin/env python3
"""a02 - sections 4-5: ncRNA length / CM composition, and RT<->ncRNA genomic geometry.

Geometry conventions are g3's, unchanged (gap_bp = bases strictly between; direction and signed
distance transcription-relative to the RT strand; intervening CDS = CDS wholly in the gap). This
script adds only VIEWS: the same placements counted at three units, and the configuration classes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

SCRIPT = "a02_geometry.py"

PAIR_COLS = ["physical_locus_key", "locus_key", "rt_seq_hash", "nc_seq_hash", "detection_model",
             "file_label", "source_database", "tax_species", "genome_id_norm", "direction",
             "signed_distance_bp", "gap_bp", "overlap_bp", "same_strand", "n_cds_between",
             "cds_between_bin", "overlaps_rt_cds", "overlaps_any_cds", "overlaps_non_rt_cds",
             "canonical", "geometry_eligible", "nc_seq_len", "nc_at_window_edge",
             "true_start_clipped", "clipped_end_flag", "has_structure_annotation", "score",
             "multiplicity_class"]


def classify(p: pd.DataFrame, tech_lo: float, tech_hi: float) -> pd.Series:
    """Exclusive configuration classes, in this declared order."""
    d, gap, ncds = p.direction, p.gap_bp, p.n_cds_between
    sd = p.signed_distance_bp
    cls = pd.Series("unclassified", index=p.index, dtype=object)
    tech = d.eq("downstream") & sd.between(tech_lo, tech_hi)
    cls = cls.mask(d.eq("overlapping") & p.overlaps_rt_cds, "overlapping the RT CDS")
    cls = cls.mask(cls.eq("unclassified") & d.eq("overlapping"), "overlapping the RT interval only")
    cls = cls.mask(cls.eq("unclassified") & tech, "downstream: technical clipped mode")
    cls = cls.mask(cls.eq("unclassified") & d.eq("downstream"), "downstream: other")
    cls = cls.mask(cls.eq("unclassified") & d.eq("upstream") & ncds.eq(0) & gap.le(C.ADJACENT_MAX_GAP),
                   "upstream, adjacent (0 CDS, \u2264500 bp)")
    cls = cls.mask(cls.eq("unclassified") & d.eq("upstream") & ncds.eq(0),
                   "upstream, long intergenic gap (0 CDS, >500 bp)")
    cls = cls.mask(cls.eq("unclassified") & d.eq("upstream") & ncds.eq(1),
                   "upstream, one intervening CDS")
    cls = cls.mask(cls.eq("unclassified") & d.eq("upstream") & ncds.ge(2),
                   "upstream, two or more intervening CDS")
    return cls


def hist_rows(v: np.ndarray, edges: np.ndarray, **keys) -> list[dict]:
    cnt, _ = np.histogram(v, bins=edges)
    return [dict(bin_lo=float(a), bin_hi=float(b), n=int(c), **keys)
            for a, b, c in zip(edges[:-1], edges[1:], cnt) if c]


def main() -> None:
    C.log("== a02 sections 4-5")
    p = C.derived("rt_ncrna_pairs_v1", PAIR_COLS)
    can = p[p.canonical].copy()
    ep = C.derived("rt_ncrna_exact_pairs_v1")
    nb = C.derived("ncrna_family_baseline_v1")

    # g3's own technical-mode rule, re-read from the landed profile rather than re-chosen here
    prof = C.landed("dbchar_g3_pair_geometry", "g3_downstream_mode_profile.tsv")
    med_dn = float(prof.loc[prof.measure == "median_signed_distance_bp", "value"].iloc[0])
    tech_lo, tech_hi = med_dn - C.TECH_MODE_HALF_WIDTH, med_dn + C.TECH_MODE_HALF_WIDTH
    can["tech_mode"] = can.direction.eq("downstream") & can.signed_distance_bp.between(tech_lo, tech_hi)
    C.log(f"   technical downstream mode: {tech_lo:.0f}..{tech_hi:.0f} bp "
          f"({int(can.tech_mode.sum()):,d} canonical placements)")

    # ================================================================ section 4: ncRNA and CM
    q = []
    for m, g in nb.groupby("detection_model"):
        v = g.nc_seq_len.to_numpy()
        q.append(dict(detection_model=m, n_exact_ncrna=len(v), n_placements=int(g.n_placements.sum()),
                      min=int(v.min()), q05=float(np.percentile(v, 5)), q25=float(np.percentile(v, 25)),
                      median=float(np.median(v)), q75=float(np.percentile(v, 75)),
                      q95=float(np.percentile(v, 95)), max=int(v.max()),
                      iqr=float(np.percentile(v, 75) - np.percentile(v, 25)),
                      pct_with_structure_annotation=100 * float(g.any_structure.mean()),
                      median_infernal_score=float(g.median_score.median())))
    q = pd.DataFrame(q).sort_values("median")
    C.write_table("t09_ncrna_length_by_model", q, "exact ncRNA sequences",
                  "exact ncRNA sequences called by that covariance model", SCRIPT)

    edges = np.arange(0, 420, 5)
    rows = []
    for m, g in nb.groupby("detection_model"):
        rows += hist_rows(np.clip(g.nc_seq_len.to_numpy(), 0, 415), edges, detection_model=m)
    rows += hist_rows(np.clip(nb.nc_seq_len.to_numpy(), 0, 415), edges, detection_model="ALL MODELS")
    C.write_table("t09_ncrna_length_histogram", pd.DataFrame(rows), "exact ncRNA sequences",
                  "exact ncRNA sequences of that model, binned at 5 nt", SCRIPT)

    # CM composition at four units
    units = []
    for m, g in can.groupby("detection_model"):
        units.append(dict(detection_model=m, n_placements=len(g),
                          n_physical_loci=g.physical_locus_key.nunique(),
                          n_exact_ncrna=g.nc_seq_hash.nunique(),
                          n_exact_rt=g.rt_seq_hash.nunique(),
                          n_species=g.tax_species.nunique()))
    u = pd.DataFrame(units)
    for c in ("n_placements", "n_physical_loci", "n_exact_ncrna", "n_exact_rt"):
        u["pct_" + c[2:]] = 100 * u[c] / u[c].sum()
    u = u.sort_values("n_placements", ascending=False)
    C.write_table("t10_model_composition_by_unit", u,
                  "placements / physical loci / exact ncRNAs / exact RTs",
                  "all CANONICAL placements counted at that unit", SCRIPT)

    # ================================================================ section 5: geometry
    can["config_class"] = classify(can, tech_lo, tech_hi)
    rows = []
    tot_p, tot_l, tot_e = len(can), can.physical_locus_key.nunique(), None
    ep_keys = set(zip(ep.rt_seq_hash, ep.nc_seq_hash))
    can["pair_key"] = list(zip(can.rt_seq_hash, can.nc_seq_hash))
    tot_e = can.pair_key.nunique()
    for cls, g in can.groupby("config_class"):
        rows.append(dict(config_class=cls, n_placements=len(g),
                         pct_placements=100 * len(g) / tot_p,
                         n_physical_loci=g.physical_locus_key.nunique(),
                         n_exact_pairs=g.pair_key.nunique(),
                         n_exact_rt=g.rt_seq_hash.nunique(),
                         n_exact_ncrna=g.nc_seq_hash.nunique(),
                         n_species=g.tax_species.nunique(),
                         pct_same_strand=100 * float(g.same_strand.mean()),
                         median_abs_distance_bp=float(g.signed_distance_bp.abs().median())))
    cc = pd.DataFrame(rows).sort_values("n_placements", ascending=False)
    cc["n_placements_total"] = tot_p
    cc["n_physical_loci_total"] = tot_l
    cc["n_exact_pairs_total"] = tot_e
    C.write_table("t12_configuration_classes", cc, "placements (loci/pairs beside)",
                  "all CANONICAL placements (344,154); a physical locus with two placements of "
                  "different classes is counted in both locus columns", SCRIPT)

    flags = pd.DataFrame([
        dict(flag="opposite strand to the RT", n_placements=int((~can.same_strand).sum())),
        dict(flag="ncRNA overlaps a non-RT CDS", n_placements=int(can.overlaps_non_rt_cds.sum())),
        dict(flag="placement in a contig-start-clipped window",
             n_placements=int(can.true_start_clipped.sum())),
        dict(flag="placement in a window clipped at the contig end",
             n_placements=int(can.clipped_end_flag.sum())),
        dict(flag="same call arriving from another record of the same locus",
             n_placements=int(can.multiplicity_class.eq(
                 "same_call_from_another_record_of_the_same_locus").sum())),
    ])
    flags["pct_of_canonical"] = 100 * flags.n_placements / tot_p
    C.write_table("t12_configuration_flags", flags, "placements",
                  "all CANONICAL placements (344,154); the flags are not exclusive", SCRIPT)

    # ---- signed distance at three units --------------------------------------------------
    per_locus = can.groupby("physical_locus_key").signed_distance_bp.median()
    per_pair = ep.set_index(["rt_seq_hash", "nc_seq_hash"]).median_signed_distance_bp

    fine = np.arange(-300, 305, 5)
    rows = []
    for name, v in (("placement", can.signed_distance_bp.to_numpy()),
                    ("physical locus", per_locus.to_numpy()),
                    ("exact pair", per_pair.to_numpy())):
        v = np.asarray(v, dtype=float)
        v = v[~np.isnan(v)]
        rows += hist_rows(v, fine, view_unit=name, n_total=len(v))
    C.write_table("t13_signed_distance_zoom", pd.DataFrame(rows), "the unit named in view_unit",
                  "units with a defined signed distance (CANONICAL placements; their median per "
                  "physical locus; the landed median per exact pair), 5-bp bins over -300..300 bp",
                  SCRIPT)

    wide = np.array([-10000, -5000, -2000, -1000, -500, -200, -100, -50, -20, -5, 5, 20, 50, 100,
                     200, 500, 1000, 2000, 5000, 10000], dtype=float)
    rows = []
    for name, v in (("placement", can.signed_distance_bp.to_numpy()),
                    ("physical locus", per_locus.to_numpy()),
                    ("exact pair", per_pair.to_numpy())):
        v = np.asarray(v, dtype=float)
        v = v[~np.isnan(v)]
        rows += hist_rows(v, wide, view_unit=name, n_total=len(v))
    # the technical mode's own contribution, so the figure can shade it
    tm = can[can.tech_mode].signed_distance_bp.to_numpy()
    rows += hist_rows(tm, wide, view_unit="placement: technical clipped mode only", n_total=len(tm))
    C.write_table("t13_signed_distance_wide", pd.DataFrame(rows), "the unit named in view_unit",
                  "units with a defined signed distance, asymmetric bins over -10..+10 kb", SCRIPT)

    # ---- absolute distance ECDF ----------------------------------------------------------
    grid = np.array([0, 5, 10, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1100, 1500,
                     2000, 2700, 3000, 5000, 10000], dtype=float)
    rows = []
    for name, v in (("placement", can.signed_distance_bp.abs().to_numpy()),
                    ("placement, technical mode excluded",
                     can[~can.tech_mode].signed_distance_bp.abs().to_numpy()),
                    ("physical locus", per_locus.abs().to_numpy()),
                    ("exact pair", per_pair.abs().to_numpy())):
        v = np.asarray(v, dtype=float)
        v = v[~np.isnan(v)]
        for x in grid:
            rows.append(dict(view_unit=name, abs_distance_bp=float(x),
                             cumulative_pct=100 * float((v <= x).mean()), n_total=len(v)))
    C.write_table("t14_abs_distance_ecdf", pd.DataFrame(rows), "the unit named in view_unit",
                  "units with a defined signed distance", SCRIPT)

    # ---- what the ~1 kb upstream mode is made of -----------------------------------------
    band = can[(can.direction == "upstream") & can.gap_bp.between(900, 1100)]
    top_rt = band.rt_seq_hash.value_counts()
    top_sp = band.tax_species.value_counts()
    comp = pd.DataFrame([
        dict(measure="canonical placements in the 900-1,100 bp upstream band", value=len(band)),
        dict(measure="of those, with 0 intervening CDS", value=int(band.n_cds_between.eq(0).sum())),
        dict(measure="distinct exact RTs in the band", value=int(band.rt_seq_hash.nunique())),
        dict(measure="distinct exact ncRNAs in the band", value=int(band.nc_seq_hash.nunique())),
        dict(measure="distinct physical loci in the band",
             value=int(band.physical_locus_key.nunique())),
        dict(measure="distinct species in the band", value=int(band.tax_species.nunique())),
        dict(measure="placements contributed by the single most recurrent exact RT",
             value=int(top_rt.iloc[0])),
        dict(measure="placements contributed by the most frequent species", value=int(top_sp.iloc[0])),
    ])
    comp["pct_of_band"] = 100 * comp.value / len(band)
    comp = pd.concat([comp, pd.DataFrame([dict(
        measure="all CANONICAL upstream placements (context, not part of the band)",
        value=int(can.direction.eq("upstream").sum()), pct_of_band=np.nan)])], ignore_index=True)
    comp["top_exact_rt_sha256"] = top_rt.index[0]
    comp["top_species"] = top_sp.index[0]
    C.write_table("t14_gap_mode_composition", comp, "placements",
                  "CANONICAL upstream placements with a 900-1,100 bp gap (the second upstream mode)",
                  SCRIPT)

    # upstream gap distribution with and without that one exact RT, at placement and pair units
    gb = np.array([0, 20, 50, 100, 200, 500, 900, 1100, 2000, 5000, 10000], dtype=float)
    up = can[can.direction == "upstream"]
    rows = []
    rows += hist_rows(up.gap_bp.to_numpy(float), gb, series="all CANONICAL upstream placements",
                      n_total=len(up))
    excl = up[up.rt_seq_hash != top_rt.index[0]]
    rows += hist_rows(excl.gap_bp.to_numpy(float), gb,
                      series="placements, most recurrent exact RT removed", n_total=len(excl))
    upl = up.groupby("physical_locus_key").gap_bp.median().to_numpy(float)
    rows += hist_rows(upl, gb, series="physical loci (median gap)", n_total=len(upl))
    upp = up.groupby(["rt_seq_hash", "nc_seq_hash"]).gap_bp.median().to_numpy(float)
    rows += hist_rows(upp, gb, series="exact pairs (median gap)", n_total=len(upp))
    C.write_table("t14_upstream_gap_by_unit", pd.DataFrame(rows), "the unit named in series",
                  "CANONICAL upstream placements, counted at that unit", SCRIPT)

    # ---- intervening CDS, strand, overlap at two units -----------------------------------
    rows = []
    for unit, frame in (("placement", can), ("physical locus", None)):
        if unit == "placement":
            vc = frame.n_cds_between.clip(upper=4).value_counts().sort_index()
            tot = len(frame)
        else:
            s = can.groupby("physical_locus_key").n_cds_between.min().clip(upper=4)
            vc = s.value_counts().sort_index()
            tot = len(s)
        for k, v in vc.items():
            lab = ">3" if k == 4 else str(int(k))
            rows.append(dict(view_unit=unit, n_cds_between=lab, n=int(v), n_total=int(tot),
                             pct=100 * v / tot))
    C.write_table("t15_cds_between_by_unit", pd.DataFrame(rows), "the unit named in view_unit",
                  "CANONICAL placements (or physical loci, taking the minimum CDS count of the "
                  "locus's placements)", SCRIPT)

    rows = []
    for d, g in can.groupby("direction"):
        rows.append(dict(direction=d, n_placements=len(g),
                         n_same_strand=int(g.same_strand.sum()),
                         n_opposite_strand=int((~g.same_strand).sum()),
                         n_overlaps_rt_cds=int(g.overlaps_rt_cds.sum()),
                         n_overlaps_non_rt_cds=int(g.overlaps_non_rt_cds.sum()),
                         n_overlaps_any_cds=int(g.overlaps_any_cds.sum())))
    ov = pd.DataFrame(rows)
    ov = C.add_rate(ov, "n_same_strand", "n_placements", "pct_same_strand")
    ov = C.add_rate(ov, "n_overlaps_any_cds", "n_placements", "pct_overlaps_any_cds")
    C.write_table("t15_strand_and_overlap", ov, "placements",
                  "CANONICAL placements of that direction", SCRIPT)

    # ---- geometry by CM model -------------------------------------------------------------
    rows = []
    for m, g in can.groupby("detection_model"):
        loci = g.groupby("physical_locus_key").agg(
            signed=("signed_distance_bp", "median"), cds=("n_cds_between", "min"),
            direction=("direction", "first"), same=("same_strand", "max"))
        if len(loci) < 1:
            continue
        rows.append(dict(detection_model=m, n_physical_loci=len(loci),
                         pct_upstream=100 * float(loci.direction.eq("upstream").mean()),
                         pct_downstream=100 * float(loci.direction.eq("downstream").mean()),
                         pct_overlapping=100 * float(loci.direction.eq("overlapping").mean()),
                         pct_same_strand=100 * float(loci.same.mean()),
                         pct_0_cds_between=100 * float(loci.cds.eq(0).mean()),
                         pct_1_cds_between=100 * float(loci.cds.eq(1).mean()),
                         median_signed_distance_bp=float(loci.signed.median()),
                         q25_signed=float(loci.signed.quantile(.25)),
                         q75_signed=float(loci.signed.quantile(.75)),
                         pct_in_technical_mode=100 * float(
                             g.groupby("physical_locus_key").tech_mode.max().mean())))
    gm = pd.DataFrame(rows).sort_values("n_physical_loci", ascending=False)
    C.write_table("t16_geometry_by_model", gm, "physical loci",
                  "CANONICAL physical loci carrying a call by that covariance model", SCRIPT)

    rows = []
    for m, g in can.groupby("detection_model"):
        loci = g.groupby("physical_locus_key").signed_distance_bp.median().to_numpy(float)
        if len(loci) < 200:
            continue
        rows += hist_rows(loci, wide, detection_model=m, n_total=len(loci))
    C.write_table("t16_distance_histogram_by_model", pd.DataFrame(rows), "physical loci",
                  "CANONICAL physical loci of that model (models with >=200 loci), asymmetric bins "
                  "over -10..+10 kb", SCRIPT)

    # ---- ncRNA call multiplicity per locus -------------------------------------------------
    per = can.groupby("physical_locus_key").agg(n_calls=("nc_seq_hash", "size"),
                                                n_seqs=("nc_seq_hash", "nunique"),
                                                n_models=("detection_model", "nunique"))
    rows = []
    for col, lab in (("n_calls", "canonical calls per physical locus"),
                     ("n_seqs", "distinct exact ncRNA sequences per physical locus"),
                     ("n_models", "distinct covariance models per physical locus")):
        vc = per[col].clip(upper=4).value_counts().sort_index()
        for k, v in vc.items():
            rows.append(dict(measure=lab, value=">3" if k == 4 else str(int(k)), n_loci=int(v),
                             n_loci_total=len(per), pct=100 * v / len(per)))
    C.write_table("t17_calls_per_locus", pd.DataFrame(rows), "physical loci",
                  "physical loci carrying at least one CANONICAL placement", SCRIPT)

    # structure annotation, reported separately from biological absence
    st = nb.groupby("detection_model").agg(n_exact_ncrna=("nc_seq_hash", "size"),
                                           n_with_structure=("any_structure", "sum")).reset_index()
    st = C.add_rate(st, "n_with_structure", "n_exact_ncrna", "pct_with_structure")
    st = st.sort_values("n_exact_ncrna", ascending=False)
    C.write_table("t11_structure_annotation_by_model", st, "exact ncRNA sequences",
                  "exact ncRNA sequences called by that model", SCRIPT)


if __name__ == "__main__":
    main()
