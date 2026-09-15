#!/usr/bin/env python3
"""a04 - sections 8, 9, 10: exact-pair topology, the atypical non-Retron candidates, MULTI."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

SCRIPT = "a04_pairs_candidates_multi.py"


def main() -> None:
    C.log("== a04 sections 8-10")
    ep = C.derived("rt_ncrna_exact_pairs_v1")
    rc = C.derived("rt_ncrna_exact_pair_recurrence_v1")
    pairs = C.derived("rt_ncrna_pairs_v1", ["physical_locus_key", "rt_seq_hash", "nc_seq_hash",
                                            "detection_model", "canonical", "direction",
                                            "signed_distance_bp", "same_strand", "n_cds_between",
                                            "tax_species", "source_database", "file_label",
                                            "genome_id_norm", "gap_bp", "nc_seq_len", "score",
                                            "geometry_eligible"])
    can = pairs[pairs.canonical]

    # ================================================================ section 8: topology
    comp = C.landed("dbchar_g3_pair_geometry", "g3_topology_components.tsv")
    C.write_table("t28_topology_components", comp.drop(columns=[c for c in ("unit", "denominator")
                                                                if c in comp.columns]),
                  "connected components of the exact RT-ncRNA bipartite graph",
                  "the 14,918 components over 30,924 exact pairs (carried from the landed g3 "
                  "table, re-emitted unchanged)", SCRIPT)

    deg_rt = ep.groupby("rt_seq_hash").nc_seq_hash.nunique()
    deg_nc = ep.groupby("nc_seq_hash").rt_seq_hash.nunique()
    rows = []
    for side, s in (("exact RT -> distinct exact ncRNAs", deg_rt),
                    ("exact ncRNA -> distinct exact RTs", deg_nc)):
        vc = s.clip(upper=5).value_counts().sort_index()
        for k, v in vc.items():
            rows.append(dict(side=side, degree=">4" if k == 5 else str(int(k)), n=int(v),
                             n_total=len(s), pct=100 * v / len(s), max_degree=int(s.max())))
    C.write_table("t28_degree_distribution", pd.DataFrame(rows), "exact sequences",
                  "exact RT (or exact ncRNA) sequences present in the exact-pair view", SCRIPT)

    # recurrence: class shares at pair and placement units
    r = rc.copy()
    cls = r.groupby("recurrence_class").agg(n_exact_pairs=("rt_seq_hash", "size"),
                                            n_placements=("n_placements", "sum"),
                                            median_placements=("n_placements", "median"),
                                            max_placements=("n_placements", "max"),
                                            median_species=("n_species", "median")).reset_index()
    cls["pct_of_exact_pairs"] = 100 * cls.n_exact_pairs / cls.n_exact_pairs.sum()
    cls["pct_of_placements"] = 100 * cls.n_placements / cls.n_placements.sum()
    C.write_table("t29_recurrence_classes", cls.sort_values("n_exact_pairs", ascending=False),
                  "exact pairs (placements beside)",
                  "the 30,924 distinct (exact RT, exact ncRNA) pairs", SCRIPT)

    rows = []
    for metric, col in (("placements per pair", "n_placements"), ("genomes per pair", "n_genomes"),
                        ("species per pair", "n_species"), ("databases per pair", "n_databases")):
        for cl, g in rc.groupby("recurrence_class"):
            v = g[col].to_numpy()
            for x in (1, 2, 5, 10, 100, 1000, 10000):
                rows.append(dict(metric=metric, recurrence_class=cl, at_least=x,
                                 n_pairs=int((v >= x).sum()), n_pairs_total=len(v),
                                 pct=100 * float((v >= x).mean())))
    C.write_table("t29_recurrence_ccdf", pd.DataFrame(rows), "exact pairs",
                  "exact pairs of that recurrence class", SCRIPT)

    # ---- do recurrent exact RTs keep the same partner? -------------------------------------
    per = can.groupby(["rt_seq_hash", "nc_seq_hash"]).physical_locus_key.nunique().rename("n_loci")
    per = per.reset_index()
    tot = per.groupby("rt_seq_hash").n_loci.sum().rename("n_loci_total")
    top = per.groupby("rt_seq_hash").n_loci.max().rename("n_loci_dominant")
    npart = per.groupby("rt_seq_hash").nc_seq_hash.nunique().rename("n_partners")
    mods = can.groupby("rt_seq_hash").detection_model.nunique().rename("n_models")
    d = pd.concat([tot, top, npart, mods], axis=1).reset_index()
    d["dominant_partner_pct"] = 100 * d.n_loci_dominant / d.n_loci_total
    multi = d[d.n_loci_total >= 2]
    bins = [1, 2, 5, 20, 100, 10**9]
    labs = ["2-4", "5-19", "20-99", ">=100", ""]
    multi = multi.assign(recurrence_bin=pd.cut(multi.n_loci_total, bins=[1, 4, 19, 99, 10**9],
                                               labels=["2-4", "5-19", "20-99", ">=100"]))
    rows = []
    for b, g in multi.groupby("recurrence_bin", observed=True):
        rows.append(dict(recurrence_bin=b, n_exact_rt=len(g),
                         median_dominant_partner_pct=float(g.dominant_partner_pct.median()),
                         pct_single_partner=100 * float(g.n_partners.eq(1).mean()),
                         pct_dominant_ge_90=100 * float(g.dominant_partner_pct.ge(90).mean()),
                         pct_single_model=100 * float(g.n_models.eq(1).mean()),
                         median_partners=float(g.n_partners.median())))
    C.write_table("t30_partner_consistency", pd.DataFrame(rows), "exact RT sequences",
                  "exact RTs carrying CANONICAL placements at >=2 physical loci, binned by how "
                  "many loci they occur at", SCRIPT)

    hist = multi.dominant_partner_pct.round(0).value_counts().sort_index().rename("n_exact_rt")
    C.write_table("t30_dominant_partner_histogram", hist.reset_index().rename(
        columns={"index": "dominant_partner_pct"}), "exact RT sequences",
        "exact RTs carrying CANONICAL placements at >=2 physical loci (n = "
        f"{len(multi):,d})", SCRIPT)

    # exact-sequence difference vs ncRNA-family difference
    nb = C.derived("ncrna_family_baseline_v1", ["nc_seq_hash", "detection_model", "nc_seq_len"])
    j = per.merge(nb, on="nc_seq_hash", how="left")
    multi_rt = j[j.rt_seq_hash.isin(set(d[d.n_partners > 1].rt_seq_hash))]
    gg = multi_rt.groupby("rt_seq_hash").agg(n_partners=("nc_seq_hash", "nunique"),
                                             n_models=("detection_model", "nunique"),
                                             len_span=("nc_seq_len", lambda v: v.max() - v.min()))
    rows = [dict(measure="exact RTs paired with more than one exact ncRNA sequence", n=len(gg)),
            dict(measure="of those, all partners called by ONE covariance model",
                 n=int(gg.n_models.eq(1).sum())),
            dict(measure="of those, partner lengths span <= 10 nt",
                 n=int(gg.len_span.le(10).sum())),
            dict(measure="of those, partner lengths span > 50 nt",
                 n=int(gg.len_span.gt(50).sum()))]
    t = pd.DataFrame(rows)
    t["pct"] = 100 * t.n / len(gg)
    C.write_table("t30_partner_sequence_vs_family", t, "exact RT sequences",
                  "exact RTs paired with more than one exact ncRNA sequence in the CANONICAL view",
                  SCRIPT)

    # ================================================================ section 9: candidates
    nr = C.derived("rt_ncrna_nonretron_candidates_v1")
    fam = nr.groupby(["file_label", "detection_model"]).agg(
        n_placements=("record_key", "size"), n_loci=("physical_locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_exact_ncrna=("nc_seq_hash", "nunique"),
        n_species=("tax_species", "nunique"), n_databases=("source_database", "nunique"),
        n_canonical=("canonical", "sum")).reset_index()
    C.write_table("t31_candidates_family_model", fam.sort_values("n_placements", ascending=False),
                  "placements", "the 266 retained retron-CM placements beside non-Retron-labelled "
                  "RTs (geometry-eligible)", SCRIPT)

    canr = can[can.file_label == "Retron"]
    env_lo, env_hi = -1100, 0      # declared Retron envelope, from the canonical distribution
    def envelope(df):
        return (df.direction.eq("upstream") & df.same_strand & df.n_cds_between.eq(0)
                & df.signed_distance_bp.between(env_lo, env_hi))
    rows = []
    for name, df in (("CANONICAL Retron placements", canr),
                     ("non-Retron retron-CM candidates (single-family)", nr[~nr.is_multi]),
                     ("non-Retron retron-CM candidates (MULTI stratum)", nr[nr.is_multi])):
        rows.append(dict(population=name, n_placements=len(df),
                         pct_upstream=100 * float(df.direction.eq("upstream").mean()),
                         pct_downstream=100 * float(df.direction.eq("downstream").mean()),
                         pct_overlapping=100 * float(df.direction.eq("overlapping").mean()),
                         pct_same_strand=100 * float(df.same_strand.mean()),
                         pct_0_cds_between=100 * float(df.n_cds_between.eq(0).mean()),
                         median_abs_distance_bp=float(df.signed_distance_bp.abs().median()),
                         pct_in_retron_envelope=100 * float(envelope(df).mean()),
                         n_exact_rt=int(df.rt_seq_hash.nunique()),
                         n_species=int(df.tax_species.nunique())))
    t31 = C.add_rate(pd.DataFrame(rows).assign(
        n_in_envelope=lambda x: (x.pct_in_retron_envelope / 100 * x.n_placements).round().astype(int)),
        "n_in_envelope", "n_placements", "pct_envelope")
    C.write_table("t31_candidates_vs_retron", t31, "placements",
                  "placements of the population named in the row; the 'Retron envelope' is "
                  f"declared as upstream, same strand, 0 intervening CDS and a gap of "
                  f"{-env_hi}-{-env_lo} bp", SCRIPT,
                  estimate="census; Wilson 95% interval on the envelope rate")

    nrl = nr.groupby("rt_seq_hash").agg(n_placements=("record_key", "size"),
                                        n_loci=("physical_locus_key", "nunique"),
                                        n_species=("tax_species", "nunique"),
                                        n_databases=("source_database", "nunique"),
                                        family=("file_label", "first"),
                                        model=("detection_model", "first"),
                                        median_distance=("signed_distance_bp", "median"),
                                        n_ncrna_seqs=("nc_seq_hash", "nunique")).reset_index()
    C.write_table("t31_candidate_exact_rts", nrl.sort_values("n_placements", ascending=False),
                  "exact RT sequences",
                  "exact RTs carrying at least one of the 266 candidate placements", SCRIPT)

    dist = nr[["file_label", "detection_model", "signed_distance_bp", "direction", "same_strand",
               "n_cds_between", "canonical", "source_database", "tax_species"]].copy()
    C.write_table("t31_candidate_placements", dist.sort_values(
        ["file_label", "detection_model", "signed_distance_bp"]), "placements",
        "each of the 266 candidate placements, one per row", SCRIPT)

    # ================================================================ section 10: MULTI
    mh = C.derived("multi_hmm_evidence_v1")
    prof = C.landed("dbchar_g4_family_baseline", "g4_multi_hmm_profile.tsv")
    ctrl = C.landed("dbchar_g4_family_baseline", "g4_multi_hmm_positive_control.tsv")
    C.write_table("t32_multi_profile", prof.drop(columns=[c for c in ("unit", "denominator")
                                                          if c in prof.columns]),
                  "MULTI exact RT sequences", "the 7,593 V-RT-MULTI exact RTs (carried from the "
                  "landed g4 table, re-emitted unchanged)", SCRIPT)

    grid = np.array([0, 1, 2, 3, 5, 7.5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 400], dtype=float)
    ctrl_margin = None
    for c in ctrl.columns:
        if "margin" in c.lower() and ctrl[c].dtype != object:
            ctrl_margin = c
    rows = []
    v = mh.margin_bits.to_numpy(float)
    for x in grid:
        rows.append(dict(series="MULTI exact RTs", margin_bits=float(x),
                         cumulative_pct=100 * float((v <= x).mean()), n_total=len(v)))
    cmp_tab = C.landed("dbchar_g4_family_baseline", "g4_multi_hmm_margin_comparison.tsv")
    C.write_table("t32_margin_ecdf", pd.DataFrame(rows), "MULTI exact RT sequences",
                  "the 7,593 V-RT-MULTI exact RTs; the landed control (single-family sample) "
                  "median is in t32_margin_comparison", SCRIPT)
    C.write_table("t32_margin_comparison", cmp_tab.drop(columns=[
        c for c in ("unit", "denominator") if c in cmp_tab.columns]),
        "exact RT sequences", "MULTI exact RTs vs the landed seeded control of 2,000 "
        "single-family exact RTs (carried from g4, re-emitted unchanged)", SCRIPT)

    # margin vs length, binned (the figure draws a hexbin from the raw pairs it also lands)
    mh2 = mh[["rt_seq_hash", "rt_aa_len", "margin_bits", "best_family", "second_family",
              "labels", "best_in_labels", "n_families_hit", "n_loci", "n_species"]].copy()
    C.write_table("t32_multi_margin_length", mh2, "MULTI exact RT sequences",
                  "each of the 7,593 V-RT-MULTI exact RTs, one per row", SCRIPT)

    lb = mh.assign(len_bin=pd.cut(mh.rt_aa_len, bins=[0, 150, 200, 250, 300, 350, 400, 500, 10**9],
                                  labels=["<150", "150-199", "200-249", "250-299", "300-349",
                                          "350-399", "400-499", ">=500"]))
    agg = lb.groupby("len_bin", observed=True).agg(
        n_exact_rt=("margin_bits", "size"), median_margin_bits=("margin_bits", "median"),
        q25=("margin_bits", lambda v: v.quantile(.25)),
        q75=("margin_bits", lambda v: v.quantile(.75)),
        pct_margin_below_10=("margin_bits", lambda v: 100 * float(v.lt(10).mean()))).reset_index()
    C.write_table("t32_margin_by_length", agg, "MULTI exact RT sequences",
                  "V-RT-MULTI exact RTs of that RT length bin", SCRIPT)

    pairs_lab = []
    for labels, g in mh.groupby("labels"):
        fams = sorted(set(str(labels).split("/")))
        for i in range(len(fams)):
            for j in range(i + 1, len(fams)):
                pairs_lab.append(dict(family_a=fams[i], family_b=fams[j], n_exact_rt=len(g),
                                      median_margin_bits=float(g.margin_bits.median())))
    pl = pd.DataFrame(pairs_lab).groupby(["family_a", "family_b"]).agg(
        n_exact_rt=("n_exact_rt", "sum"),
        median_margin_bits=("median_margin_bits", "median")).reset_index()
    C.write_table("t33_multi_family_pairs", pl.sort_values("n_exact_rt", ascending=False),
                  "MULTI exact RT sequences",
                  "V-RT-MULTI exact RTs whose label set contains both families (a 3-label set "
                  "contributes to all three pairs)", SCRIPT)

    # does MULTI co-occur with unusual architecture?
    rec = C.records()
    rec_multi = rec[rec.file_label == "MULTI"]
    rec_single = rec[rec.file_label != "MULTI"]
    rows = []
    for name, df in (("MULTI records", rec_multi), ("single-family records", rec_single)):
        rows.append(dict(population=name, n_records=len(df),
                         pct_geometry_eligible=100 * float(df.elig_geometry.mean()),
                         pct_no_rt_cds=100 * float(df.n_rt_cds.eq(0).mean()),
                         pct_rt_at_window_edge=100 * float(df.rt_at_window_edge.mean()),
                         pct_window_inverted=100 * float(df.window_inverted.mean()),
                         pct_with_ncrna_call=100 * float(df.n_ncrna.gt(0).mean()),
                         median_rt_aa_len=float(df.rt_aa_len.median()),
                         pct_bt_exact=100 * float(df.bt_status.eq("exact").mean())))
    C.write_table("t33_multi_architecture", pd.DataFrame(rows), "distinct records",
                  "distinct RT-anchored records of that population (MULTI 9,012 vs the "
                  "single-family files)", SCRIPT)


if __name__ == "__main__":
    main()
