#!/usr/bin/env python3
"""c01 - reconcile every re-derived quantity against the landed g1-g6 value.

This bundle is a reporting layer: it may not change a Stage-1 number. Every quantity it
re-derives that a landed table also carries is compared here, EXACTLY. A disagreement is a
finding, not a rounding error: the build stops, the row is landed in t41_reconciliation.tsv, and
nothing in g1-g7 is touched (the launcher's rule, and BS-6).

Re-derivation is from the derived parquet datasets, not from the landed TSV being compared
against - otherwise the check would be a tautology.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

import common as C

SCRIPT = "c01_reconcile.py"
TOL = 0.005   # percentage points, for values the landed table rounds to 2-4 dp


def main() -> int:
    C.log("== c01 reconcile against the landed g1-g6 values")
    rows = []

    def cmp(quantity, landed_value, rederived_value, bundle, table, tol=0.0):
        try:
            a, b = float(landed_value), float(rederived_value)
            agree = abs(a - b) <= tol
        except (TypeError, ValueError):
            a, b = str(landed_value), str(rederived_value)
            agree = a == b
        rows.append(dict(quantity=quantity, landed_value=landed_value,
                         rederived_value=rederived_value, landed_bundle=bundle,
                         landed_table=table, tolerance=tol,
                         verdict="AGREE" if agree else "DISAGREE"))

    rec = C.records()
    # ---------------------------------------------------------------- g2 unit ladder
    lad = C.landed("dbchar_g2_canonical_units", "g2_unit_ladder.tsv").set_index("unit")
    cmp("distinct RT-anchored records", lad.loc["distinct_raw_record", "n"], len(rec),
        "dbchar_g2_canonical_units", "g2_unit_ladder.tsv")
    cmp("loci", lad.loc["locus", "n"], rec.locus_key.nunique(),
        "dbchar_g2_canonical_units", "g2_unit_ladder.tsv")
    cmp("physical loci", lad.loc["physical_locus", "n"], rec.physical_locus_key.nunique(),
        "dbchar_g2_canonical_units", "g2_unit_ladder.tsv")
    cmp("exact RTs", lad.loc["exact_rt", "n"], rec.rt_seq_hash.nunique(),
        "dbchar_g2_canonical_units", "g2_unit_ladder.tsv")
    cmp("genomes", lad.loc["genome", "n"], rec.genome_id_norm.nunique(),
        "dbchar_g2_canonical_units", "g2_unit_ladder.tsv")

    # ---------------------------------------------------------------- g2 per-database ladder
    dbl = C.landed("dbchar_g2_canonical_units", "g2_ladder_by_source_database.tsv")
    mine = rec.groupby("source_database").agg(n_records=("record_key", "size"),
                                              n_loci=("locus_key", "nunique"),
                                              n_exact_rt=("rt_seq_hash", "nunique"),
                                              n_genomes=("genome_id_norm", "nunique"))
    for _, r in dbl.iterrows():
        db = r.source_database
        for col in ("n_records", "n_loci", "n_exact_rt", "n_genomes"):
            cmp(f"{col} in {db}", r[col], mine.loc[db, col],
                "dbchar_g2_canonical_units", "g2_ladder_by_source_database.tsv")

    # ---------------------------------------------------------------- g2 per-family ladder
    fam = C.landed("dbchar_g2_canonical_units", "g2_ladder_by_family_label.tsv")
    minef = rec.groupby("file_label").agg(n_records=("record_key", "size"),
                                          n_loci=("locus_key", "nunique"),
                                          n_exact_rt=("rt_seq_hash", "nunique"))
    for _, r in fam.iterrows():
        for col in ("n_records", "n_loci", "n_exact_rt"):
            cmp(f"{col} in {r.file_label}", r[col], minef.loc[r.file_label, col],
                "dbchar_g2_canonical_units", "g2_ladder_by_family_label.tsv")

    # ---------------------------------------------------------------- g3 geometry
    pairs = C.derived("rt_ncrna_pairs_v1", ["canonical", "geometry_eligible", "direction",
                                            "same_strand", "n_cds_between", "locus_key",
                                            "file_label", "physical_locus_key", "rt_seq_hash",
                                            "nc_seq_hash", "detection_model"])
    can = pairs[pairs.canonical]
    pop = C.landed("dbchar_g3_pair_geometry", "g3_populations.tsv")
    n_can = int(pop.loc[pop.population == "CANONICAL", "n_placements"].iloc[0])
    cmp("CANONICAL placements", n_can, len(can), "dbchar_g3_pair_geometry", "g3_populations.tsv")
    cmp("ALL placements", int(pop.loc[pop.population == "ALL", "n_placements"].iloc[0]), len(pairs),
        "dbchar_g3_pair_geometry", "g3_populations.tsv")

    d = C.landed("dbchar_g3_pair_geometry", "g3_direction.tsv")
    d = d[d.population == "CANONICAL"]
    for _, r in d.iterrows():
        cmp(f"CANONICAL placements, direction={r.direction}", r.n_placements,
            int((can.direction == r.direction).sum()), "dbchar_g3_pair_geometry",
            "g3_direction.tsv")

    cb = C.landed("dbchar_g3_pair_geometry", "g3_cds_between_explicit.tsv")
    cb = cb[(cb.population == "CANONICAL") & (cb.stratum.isna() | cb.stratum.eq(""))]
    for _, r in cb.iterrows():
        k = str(r.n_cds_between)
        mine_n = int((can.n_cds_between > 3).sum()) if k == ">3" else int(
            (can.n_cds_between == int(k)).sum())
        cmp(f"CANONICAL placements, {k} CDS between", r.n_placements, mine_n,
            "dbchar_g3_pair_geometry", "g3_cds_between_explicit.tsv")

    ss = C.landed("dbchar_g3_pair_geometry", "g3_same_strand.tsv")
    ss = ss[ss.population == "CANONICAL"]
    for _, r in ss.iterrows():
        mine_n = int(((can.direction == r.direction) & (can.same_strand == (r.same_strand in
                                                                           (True, "True")))).sum())
        cmp(f"CANONICAL {r.direction}, same_strand={r.same_strand}", r.n_placements, mine_n,
            "dbchar_g3_pair_geometry", "g3_same_strand.tsv")

    # Zero class. g3's rule is RECORD-level: a locus is covered when any of its first-copy
    # records carries >=1 ncRNA call (len(ncrnas[]) > 0), whatever that call's geometry. The
    # placement-level rule (>=1 geometry-eligible placement) is a DIFFERENT, stricter question
    # and gives a smaller number; both are compared, and the difference is landed as a row of
    # t42_definition_differences rather than presented as a disagreement.
    zc = C.landed("dbchar_g3_pair_geometry", "g3_zero_class_by_family.tsv")
    lo = C.derived("rt_loci_v1", ["locus_key", "family_label_set"])
    with_call_rec = set(rec.loc[rec.n_ncrna > 0, "locus_key"])
    with_call_elig = set(pairs.loc[pairs.geometry_eligible, "locus_key"])
    with_call_can = set(can.locus_key)
    defs = []
    for lab in ("Retron", "RVT-GII"):
        sub = lo[lo.family_label_set == lab]
        row = zc[zc.file_label == lab]
        if row.empty:
            continue
        row = row.iloc[0]
        cmp(f"{lab} loci", row.n_loci, len(sub), "dbchar_g3_pair_geometry",
            "g3_zero_class_by_family.tsv")
        cmp(f"{lab} loci with >=1 ncRNA call in a record (g3's rule)", row.n_loci_with_call,
            int(sub.locus_key.isin(with_call_rec).sum()), "dbchar_g3_pair_geometry",
            "g3_zero_class_by_family.tsv")
        defs.append(dict(
            quantity=f"{lab} loci counted as carrying an ncRNA",
            rule_a="g3: >=1 ncRNA call in any first-copy record of the locus",
            n_a=int(sub.locus_key.isin(with_call_rec).sum()),
            rule_b="this bundle, where stated: >=1 geometry-ELIGIBLE placement",
            n_b=int(sub.locus_key.isin(with_call_elig).sum()),
            rule_c="this bundle, where stated: >=1 CANONICAL placement",
            n_c=int(sub.locus_key.isin(with_call_can).sum()),
            n_loci=len(sub),
            note="not a disagreement: a call whose geometry is ineligible or non-canonical still "
                 "exists as a call. Every rate in this bundle names which rule it used"))

    ep = C.derived("rt_ncrna_exact_pairs_v1", ["rt_seq_hash", "nc_seq_hash"])
    sizes = C.landed("dbchar_g3_pair_geometry", "g3_pair_view_sizes.tsv").set_index("measure")
    cmp("distinct exact (RT, ncRNA) pairs", sizes.loc["distinct_exact_pairs", "n"], len(ep),
        "dbchar_g3_pair_geometry", "g3_pair_view_sizes.tsv")
    deg = C.landed("dbchar_g3_pair_geometry", "g3_topology_degrees.tsv").set_index("measure")
    cmp("exact RTs in the pair view", deg.loc["exact_RTs_in_the_pair_view", "n"],
        ep.rt_seq_hash.nunique(), "dbchar_g3_pair_geometry", "g3_topology_degrees.tsv")
    cmp("exact ncRNAs in the pair view", deg.loc["exact_ncRNA_sequences_in_the_pair_view", "n"],
        ep.nc_seq_hash.nunique(), "dbchar_g3_pair_geometry", "g3_topology_degrees.tsv")

    nr = C.derived("rt_ncrna_nonretron_candidates_v1", ["record_key"])
    nrl = C.landed("dbchar_g3_pair_geometry", "g3_nonretron_cm_placements.tsv")
    cmp("non-Retron retron-CM candidate placements", int(nrl.n_nonretron_placements.iloc[0]),
        len(nr), "dbchar_g3_pair_geometry", "g3_nonretron_cm_placements.tsv")

    # ---------------------------------------------------------------- g4 family baseline
    g4 = C.landed("dbchar_g4_family_baseline", "g4_rt_length_by_family.tsv")
    fb = C.derived("rt_family_baseline_v1", ["rt_seq_hash", "rt_aa_len", "family_label", "view"])
    single = fb[fb.view == "V-RT-SINGLE"]
    for _, r in g4.head(15).iterrows():
        sub = single[single.family_label == r.family_label]
        if sub.empty:
            continue
        cmp(f"exact RTs of {r.family_label} (V-RT-SINGLE)", r.n_exact_rt, len(sub),
            "dbchar_g4_family_baseline", "g4_rt_length_by_family.tsv")
        cmp(f"median RT aa length of {r.family_label}", r["median"],
            float(sub.rt_aa_len.median()), "dbchar_g4_family_baseline",
            "g4_rt_length_by_family.tsv")

    nb = C.derived("ncrna_family_baseline_v1", ["nc_seq_hash", "detection_model", "nc_seq_len"])
    g4n = C.landed("dbchar_g4_family_baseline", "g4_ncrna_length_by_model.tsv")
    for _, r in g4n.iterrows():
        sub = nb[nb.detection_model == r.detection_model]
        cmp(f"exact ncRNAs called by {r.detection_model}", r.n_exact_ncrna, len(sub),
            "dbchar_g4_family_baseline", "g4_ncrna_length_by_model.tsv")
        cmp(f"median ncRNA length, {r.detection_model}", r["median"],
            float(sub.nc_seq_len.median()), "dbchar_g4_family_baseline",
            "g4_ncrna_length_by_model.tsv")

    mh = C.derived("multi_hmm_evidence_v1", ["margin_bits", "best_in_labels"])
    prof = C.landed("dbchar_g4_family_baseline", "g4_multi_hmm_profile.tsv").set_index("measure")
    cmp("MULTI exact RTs scored", prof.loc["MULTI exact RTs scored", "value"], len(mh),
        "dbchar_g4_family_baseline", "g4_multi_hmm_profile.tsv")
    cmp("MULTI median best-vs-second margin (bits)",
        prof.loc["median best-vs-second margin (bits)", "value"],
        float(mh.margin_bits.median()), "dbchar_g4_family_baseline", "g4_multi_hmm_profile.tsv")
    cmp("MULTI with best family among its labels",
        prof.loc["best-scoring family is among the record's labels", "value"],
        int(mh.best_in_labels.sum()), "dbchar_g4_family_baseline", "g4_multi_hmm_profile.tsv")

    # ---------------------------------------------------------------- g6 tool calls
    tc = C.derived("rt_tool_calls_v1", ["record_key", "file_label", "by_myRT", "by_PADLOC",
                                        "by_DefenseFinder", "n_ncrna", "locus_key", "rt_seq_hash"])
    tcr = tc[tc.file_label == "Retron"].copy()
    tcr["combo"] = C.combo_name(tcr)
    g6 = C.landed("dbchar_g6_tool_calls", "g6_tool_matrix_retron.tsv")
    for _, r in g6.iterrows():
        sub = tcr[tcr.combo == r.detected_by_set]
        cmp(f"Retron records detected by {r.detected_by_set}", r.n_records, len(sub),
            "dbchar_g6_tool_calls", "g6_tool_matrix_retron.tsv")
        cmp(f"Retron loci detected by {r.detected_by_set}", r.n_loci, sub.locus_key.nunique(),
            "dbchar_g6_tool_calls", "g6_tool_matrix_retron.tsv")
        cmp(f"ncRNA carriage %, Retron records, {r.detected_by_set}", r.pct_with_ncrna,
            100 * float((sub.n_ncrna > 0).mean()), "dbchar_g6_tool_calls",
            "g6_tool_matrix_retron.tsv", tol=TOL)

    # ---------------------------------------------------------------- g2b recovery
    rc = C.derived("rt_cds_recovery_v1", ["record_key", "recovery_state"])
    g2b = C.landed("dbchar_g2b_rt_cds_recovery", "g2b_recovery_classes.tsv")
    for state, n in g2b.groupby("recovery_state").n_records.sum().items():
        cmp(f"records with no RT CDS, {state}", n, int((rc.recovery_state == state).sum()),
            "dbchar_g2b_rt_cds_recovery", "g2b_recovery_classes.tsv")

    # ---------------------------------------------------------------- g5 join coverage
    g5 = C.landed("dbchar_g5_metadata_sampling", "g5_join_coverage.tsv")
    for _, r in g5.iterrows():
        sub = rec[rec.source_database == r.source_database]
        cmp(f"genomes in {r.source_database}", r["n_genomes"], sub.genome_id_norm.nunique(),
            "dbchar_g5_metadata_sampling", "g5_join_coverage.tsv")

    C.write_table("t42_definition_differences", pd.DataFrame(defs), "loci",
                  "loci of that family label; the three columns are three declared coverage rules "
                  "over the same loci, not three estimates of one number", SCRIPT)

    t = pd.DataFrame(rows)
    C.write_table("t41_reconciliation", t, "landed values compared",
                  "every quantity this bundle re-derives that a landed g1-g6 table also carries; "
                  "a DISAGREE row stops the build", SCRIPT, estimate="exact comparison")
    bad = t[t.verdict == "DISAGREE"]
    C.log(f"   {len(t)} comparisons, {len(bad)} DISAGREE")
    if len(bad):
        pd.set_option("display.width", 200)
        print(bad.to_string(index=False), file=sys.stderr)
        print("FATAL: a re-derived value disagrees with a landed Stage-1 value. Nothing in g1-g7 "
              "is edited; report the discrepancy.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
