#!/usr/bin/env python3
"""findings - every number and quoted status in the Stage-2 final report, and where it lives.

This module computes nothing. It declares three kinds of lookup, all resolved by build.py:

  TABLE    a cell of a landed table: (repo-relative path, {selector column: value}, column, fmt).
           The build fails unless the selector matches exactly one row.
  DERIVED  a declared display derivation over landed cells (a count of rows, a minimum, a sum),
           with the formula written out. Only used where the frozen record itself states the
           same derivation (e.g. the g6 26-of-50 exclusion count, verified in E-g6-4).
  DOC      a value that exists only in a reviewed record (a decision record, a verbatim review
           or a commit message). The build fails unless the literal string is present in the
           named source, byte for byte.

Paths are relative to the repository root. The source of record is main at PINNED_COMMIT.
"""
from __future__ import annotations

PINNED_COMMIT = "94a1a78868d6039297c78b3fdcc047d633d6645e"

R = "results/"
G1 = R + "rt07_g1_history_and_definition/tables/g1_resolved_values.tsv"
G2 = R + "rt07_g2_reference_reconstruction/tables/g2_resolved_values.tsv"
G2F = R + "rt07_g2_reference_reconstruction/tables/g2_frame_correspondence.tsv"
G3 = R + "rt07_g3_prior_method_replication/tables/g3_resolved_values.tsv"
G4A = R + "rt07_g4a_repaired/tables/g4a_hhmake_M_sensitivity.tsv"
CV = R + "FINAL_PRE_UG25_VALIDATION_BUNDLE/tables/construction_validation_family.tsv"
CAT = R + "rt07_g4b_production_mapper/control/CATALYTIC_STATE_FROZEN.tsv"
SUP = R + "rt07_g4b_production_mapper/control/SUPPORT_RULE_FROZEN.tsv"
SPEC = R + "rt07_g4b_production_mapper/PRODUCTION_SPEC.md"
UGC = R + "rt07_ug25_confirmatory/tables/ug25_criteria.tsv"
UGK = R + "rt07_ug25_confirmatory/tables/ug25_component_summary.tsv"
UGN = R + "rt07_ug25_confirmatory/tables/ug25_control_summary.tsv"
UGS = R + "rt07_ug25_confirmatory/tables/ug25_sequence_results.tsv"
UGG = R + "rt07_ug25_confirmatory/tables/ug25_genealogy_audit.tsv"
G5A = R + "rt07_g5a_eligibility_census/tables/g5a_census_summary.tsv"
G5H = R + "rt07_g5_catalogue_application/tables/g5_qc_headline.tsv"
G5S = R + "rt07_g5_catalogue_application/tables/g5_qc_status_counts.tsv"
G6B = R + "rt07_g6_family_architecture/tables/g6_between_family_rho.tsv"
G6W = R + "rt07_g6_family_architecture/tables/g6_within_retron_rho.tsv"
G6S = R + "rt07_g6_family_architecture/tables/g6_summary.tsv"
G6C = R + "rt07_g6_family_architecture/tables/g6_controls.tsv"
G6T = R + "rt07_g6_family_architecture/tables/g6_retron_subtype_strata.tsv"
G6D = R + "rt07_g6_family_architecture/tables/g6_terminal_decision.tsv"
G7S = R + "rt07_g7a_rt0_rt7_bridge/tables/g7a_summary.tsv"
G7X = R + "rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv"
ERR = "docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv"

D = "docs/decisions/"
DEC_CLOSED = D + "2026-09-19_stage2_closed.md"
DEC_G6E = D + "2026-09-19_stage2_g6_review_errata.md"
DEC_G7E = D + "2026-09-19_stage2_g7a_review_errata.md"
DEC_REV = D + "2026-09-19_stage2_g6_g7a_independent_reviews.md"
DEC_UG5 = D + "2026-09-16_stage2_ug5_v2_closed_failed.md"
DEC_G2L = D + "2026-09-17_stage2_g2l_transfer_review_FAILED.md"
DEC_UG25 = D + "2026-09-17_stage2_ug25_confirmatory_closed.md"
DEC_G4B = D + "2026-09-17_stage2_g4b_production_packaging.md"
REV_G6 = "review-stage/INDEPENDENT_REVIEW_RESULT_g6.md"


def q(k: str) -> dict:
    return {"quantity": k}


def key(k: str) -> dict:
    return {"key": k}


# key -> (path, selector, column, fmt)
TABLE = {
    # ---- L1 historical definition: g1 -------------------------------------------------------
    "g1_sources": (G1, key("n_sources"), "raw_value", "int"),
    "g1_regions": (G1, key("n_regions"), "raw_value", "int"),
    "g1_cells": (G1, key("n_cells"), "raw_value", "int"),
    "g1_cells_evidence": (G1, key("n_cells_evidence"), "raw_value", "int"),
    "g1_quotes": (G1, key("n_quotes"), "raw_value", "int"),
    "g1_quotes_bad": (G1, key("n_quotes_bad"), "raw_value", "int"),
    "g1_edges": (G1, key("n_edges"), "raw_value", "int"),
    "g1_edges_unheld": (G1, key("n_edges_unheld"), "raw_value", "int"),
    "g1_stated_boundary": (G1, key("n_stated_boundary"), "raw_value", "int"),
    "g1_derivable": (G1, key("n_derivable"), "raw_value", "int"),
    "g1_controls": (G1, key("n_controls"), "raw_value", "int"),
    "g1_aln_seqs": (G1, key("aln_seqs"), "raw_value", "int"),
    "g1_aln_cols": (G1, key("aln_cols"), "raw_value", "int"),
    "g1_aln_subdomains": (G1, key("aln_subdomains"), "raw_value", "int"),
    "g1_aln_submitted": (G1, key("aln_submitted"), "raw_value", "str"),
    "g1_rt0_verdict": (G1, key("rt0_verdict"), "raw_value", "str"),
    # ---- L1: g2 reconstruction --------------------------------------------------------------
    "g2_proteins": (G2, key("n_proteins"), "raw_value", "int"),
    "g2_groups": (G2, key("n_groups"), "raw_value", "int"),
    "g2_cons": (G2, key("n_cons"), "raw_value", "int"),
    "g2_blocks": (G2, key("n_blocks"), "raw_value", "int"),
    "g2_blocks_f2": (G2, key("n_blocks_f2"), "raw_value", "int"),
    "g2_seven_f1": (G2, key("seven_f1"), "raw_value", "str"),
    "g2_seven_f2": (G2, key("seven_f2"), "raw_value", "str"),
    "g2_one_to_one": (G2, key("one_to_one"), "raw_value", "int"),
    "g2_median_j": (G2, key("median_j"), "raw_value", "str"),
    "g2_p_cons": (G2, key("p_cons"), "raw_value", "str"),
    "g2_p_block": (G2, key("p_block"), "raw_value", "str"),
    "g2_p_gap": (G2, key("p_gap"), "raw_value", "str"),
    "g2_rec": (G2, key("n_rec"), "raw_value", "int"),
    "g2_part": (G2, key("n_part"), "raw_value", "int"),
    "g2_notrec": (G2, key("n_notrec"), "raw_value", "int"),
    "g2_kill_verdict": (G2, key("kill_verdict"), "raw_value", "str"),
    "g2_kill_main": (G2, key("kill_main"), "raw_value", "str"),
    "g2_rt0_block": (G2, key("rt0_block"), "raw_value", "str"),
    "g2_b4_f1": (G2F, {"frame1_block": "4"}, "frame1_ltra_span", "str"),
    "g2_b4_f2": (G2F, {"frame1_block": "4"}, "frame2_ltra_span", "str"),
    "g2_b4_j": (G2F, {"frame1_block": "4"}, "jaccard_on_ltra_residues", "str"),
    "g2_b6_j": (G2F, {"frame1_block": "6"}, "jaccard_on_ltra_residues", "str"),
    "g2_b1_span": (G2F, {"frame1_block": "1"}, "frame1_ltra_span", "str"),
    "g2_b2_span": (G2F, {"frame1_block": "2"}, "frame1_ltra_span", "str"),
    "g2_b5_span": (G2F, {"frame1_block": "5"}, "frame1_ltra_span", "str"),
    "g2_b6_span": (G2F, {"frame1_block": "6"}, "frame1_ltra_span", "str"),
    # ---- L1: g3 prior-method audit -----------------------------------------------------------
    "g3_claims": (G3, key("n_claims"), "raw_value", "int"),
    "g3_repro": (G3, key("n_repro"), "raw_value", "int"),
    "g3_partial": (G3, key("n_partial"), "raw_value", "int"),
    "g3_circular": (G3, key("n_circular"), "raw_value", "int"),
    "g3_objmis": (G3, key("n_objmis"), "raw_value", "int"),
    "g3_framemis": (G3, key("n_framemis"), "raw_value", "int"),
    "g3_withdrawn": (G3, key("n_withdrawn"), "raw_value", "int"),
    "g3_nottest": (G3, key("n_nottest"), "raw_value", "int"),
    "g3_anchor_seed_pct": (G3, key("anchor_seed_pct"), "raw_value", "str"),
    "g3_gold_seed_pct": (G3, key("gold_seed_pct"), "raw_value", "str"),
    "g3_landmarks_inside": (G3, key("landmarks_inside"), "raw_value", "str"),
    "g3_blocks_anchored": (G3, key("blocks_anchored"), "raw_value", "str"),
    "g3_collapsing": (G3, key("collapsing"), "raw_value", "str"),
    "g3_rt0_verdict": (G3, key("rt0_verdict"), "raw_value", "str"),
    "g3_rt0_alanine": (G3, key("rt0_alanine"), "raw_value", "str"),
    "g3_rt0_frame_extent": (G3, key("rt0_frame_extent"), "raw_value", "str"),
    # ---- L2 operational mapper ---------------------------------------------------------------
    "m50_gii_all": (G4A, {"hhmake_M": "50", "family": "GII"}, "n_ALL_PARTNERS", "int"),
    "m50_gii_pct": (G4A, {"hhmake_M": "50", "family": "GII"}, "pct_of_full_consensus", "str"),
    "m50_ug5_pct": (G4A, {"hhmake_M": "50", "family": "UG5"}, "pct_of_full_consensus", "str"),
    "a2m_dgr_all": (G4A, {"hhmake_M": "a2m", "family": "DGRs"}, "n_ALL_PARTNERS", "int"),
    "a2m_abia_all": (G4A, {"hhmake_M": "a2m", "family": "AbiA"}, "n_ALL_PARTNERS", "int"),
    "a2m_gii_all": (G4A, {"hhmake_M": "a2m", "family": "GII"}, "n_ALL_PARTNERS", "int"),
    "cv_n": (CV, {"family": "TOTAL"}, "n", "int"),
    "cv_ok": (CV, {"family": "TOTAL"}, "n_ok", "int"),
    "cv_cat_conf": (CV, {"family": "TOTAL"}, "catalytic_confirmed", "int"),
    "cv_med_retron": (CV, {"family": "Retrons"}, "median_mapped_fraction", "str"),
    "cv_med_gii": (CV, {"family": "GII"}, "median_mapped_fraction", "str"),
    "cv_med_abia": (CV, {"family": "AbiA"}, "median_mapped_fraction", "str"),
    "cat_state": (CAT, {"parameter": "CAT_STATE"}, "value", "str"),
    "cat_count": (CAT, {"parameter": "CAT_STATE_COUNT"}, "value", "int"),
    "cat_runner": (CAT, {"parameter": "RUNNER_UP_STATE"}, "value", "str"),
    "cat_agree": (CAT, {"parameter": "CONSTRUCTION_AGREEMENT"}, "value", "str"),
    "pp_hi": (SUP, {"parameter": "PP_HI"}, "value", "str"),
    "pp_lo": (SUP, {"parameter": "PP_LO"}, "value", "str"),
    "s_min": (SUP, {"parameter": "S_MIN"}, "value", "str"),
    "k_min": (SUP, {"parameter": "K_MIN"}, "value", "str"),
    "t1": (SUP, {"parameter": "T1"}, "value", "str"),
    "d_max": (SUP, {"parameter": "D_MAX"}, "value", "str"),
    "d_random": (SUP, {"parameter": "D_RANDOM"}, "value", "str"),
    "n_anchors": (SUP, {"parameter": "N_ANCHORS"}, "value", "int"),
    "ug25_c1": (UGC, {"criterion": "C1"}, "observed", "str"),
    "ug25_c3": (UGC, {"criterion": "C3"}, "observed", "str"),
    "ug25_c4": (UGC, {"criterion": "C4"}, "observed", "str"),
    "ug25_k0_n": (UGK, {"component": "0"}, "n_sequences", "int"),
    "ug25_k1_n": (UGK, {"component": "1"}, "n_sequences", "int"),
    "ug25_k2_n": (UGK, {"component": "2"}, "n_sequences", "int"),
    "ug25_k0_med": (UGK, {"component": "0"}, "median_mapped_fraction", "str"),
    "ug25_k1_med": (UGK, {"component": "1"}, "median_mapped_fraction", "str"),
    "ug25_mono_max": (UGN, {"control_class": "MONO"}, "max_mapped", "int"),
    "ug25_di_max": (UGN, {"control_class": "DI"}, "max_mapped", "int"),
    "ug25_rev_max": (UGN, {"control_class": "REV"}, "max_mapped", "int"),
    "ug25_ctrl_n": (UGN, {"control_class": "POOLED"}, "n_attempted", "int"),
    "ug25_ctrl_valid": (UGN, {"control_class": "POOLED"}, "n_valid", "int"),
    "ug25_overlap": (UGG, {"assessment": "exact_sequence_overlap_all_construction"}, "value", "int"),
    "ug25_fulllink": (UGG, {"assessment": "n_meeting_FULL_link_rule"}, "value", "str"),
    "ug25_class": (UGG, {"assessment": "CLASSIFICATION"}, "value", "str"),
    "mapper_version": (G5A, q("mapper_version"), "value", "str"),
    "instrument_sha": (G5A, q("instrument_sha256"), "value", "str"),
    "min_aa": (G5A, q("MIN_AA"), "value", "int"),
    "g5a_total": (G5A, q("n_total_exact_rt"), "value", "int"),
    "g5a_eligible": (G5A, q("G5_ELIGIBLE_N"), "value", "int"),
    "g5a_ineligible": (G5A, q("n_ineligible"), "value", "int"),
    "g5a_short": (G5A, q("n_below_min_length"), "value", "int"),
    "g5a_nonstd": (G5A, q("n_non_standard_residue"), "value", "int"),
    "g5a_frac": (G5A, q("eligible_fraction"), "value", "str"),
    "g5_failures": (G5H, q("n_tool_failures"), "value", "int"),
    "g5_inspectable": (G5H, q("n_inspectable"), "value", "int"),
    "g5_abstained": (G5H, q("n_abstained"), "value", "int"),
    "g5_state_rows": (G5H, q("n_state_rows"), "value", "int"),
    "g5_cat_mapped": (G5H, q("n_cat_state_mapped"), "value", "int"),
    "g5_cat_conf": (G5H, q("n_cat_state_confirmed"), "value", "int"),
    "g5_cat_ratio": (G5H, q("cat_confirmed_over_cat_mapped"), "value", "str"),
    "g5_mappable": (G5S, {"inspectability_status": "MAPPABLE"}, "n", "int"),
    "g5_partial": (G5S, {"inspectability_status": "PARTIAL_MAPPING"}, "n", "int"),
    "g5_ambig": (G5S, {"inspectability_status": "AMBIGUOUS_MAPPING"}, "n", "int"),
    "g5_nosupp": (G5S, {"inspectability_status": "NO_SUPPORTED_MAPPING"}, "n", "int"),
    # ---- L3 family-level description: g6 ----------------------------------------------------
    "g6_rho": (G6B, {"analysis_id": "PRIMARY"}, "rho", "str"),
    "g6_null1": (G6B, {"analysis_id": "PRIMARY"}, "null1_p99", "str"),
    "g6_null2": (G6B, {"analysis_id": "PRIMARY"}, "null2_p99", "str"),
    "g6_groups": (G6B, {"analysis_id": "PRIMARY"}, "n_groups", "int"),
    "g6_nseq": (G6B, {"analysis_id": "PRIMARY"}, "n_sequences", "int"),
    "g6_df_rho": (G6W, {"analysis_id": "DF_subtype"}, "rho", "str"),
    "g6_df_groups": (G6W, {"analysis_id": "DF_subtype"}, "n_groups", "int"),
    "g6_pl_rho": (G6W, {"analysis_id": "PL_subtype"}, "rho", "str"),
    "g6_pl_groups": (G6W, {"analysis_id": "PL_subtype"}, "n_groups", "int"),
    "g6_lf_rho": (G6W, {"analysis_id": "LABEL_FREE"}, "rho", "str"),
    "g6_lf_verdict": (G6D, {"arm": "within_retron", "rho": "0.8061"}, "terminal_verdict", "str"),
    "g6_verdict": (G6S, q("terminal_verdict_between_family"), "value", "str"),
    "g6_families": (G6S, q("families_total"), "value", "int"),
    "g6_qualifying": (G6S, q("families_qualifying"), "value", "int"),
    "g6_clusters": (G6S, q("clusters_primary_id0.90"), "value", "int"),
    "g6_purity": (G6S, q("cluster_family_purity"), "value", "str"),
    "cs_mapped": (G6S, q("call_state_MAPPED"), "value", "int"),
    "cs_amb": (G6S, q("call_state_AMBIGUOUS"), "value", "int"),
    "cs_uns": (G6S, q("call_state_UNSUPPORTED"), "value", "int"),
    "cs_del": (G6S, q("call_state_DELETED_STATE"), "value", "int"),
    "g6_pcpos_result": (G6C, {"control_id": "PC-POS"}, "result", "str"),
    # ---- L4 historical bridge: g7a -----------------------------------------------------------
    "g7_est": (G7S, q("terminal_ESTABLISHED"), "value", "int"),
    "g7_part": (G7S, q("terminal_PARTIAL"), "value", "int"),
    "g7_unres": (G7S, q("terminal_UNRESOLVED"), "value", "int"),
    "g7_register": (G7S, q("evidence_register_rows"), "value", "int"),
    "g7_register_stated": (G7S, q("evidence_rows_source_stated"), "value", "int"),
    "g7_anchors_ltra": (G7S, q("anchors_mapped_on_ltra"), "value", "int"),
    "g7_anchor_span": (G7S, q("anchor_ltra_residue_span"), "value", "str"),
    "g7_state_span": (G7S, q("anchor_state_span"), "value", "str"),
    "g7_ctrl_pass": (G7S, q("controls_pass"), "value", "int"),
    "g7_ctrl_fail": (G7S, q("controls_fail"), "value", "int"),
    "g7_ctrl_inc": (G7S, q("controls_inconclusive"), "value", "int"),
    "g7_numbering": (G7S, q("ltra_numbering_checks_agree"), "value", "str"),
    "g7_missing": (G7S, q("missing_primary_assets"), "value", "int"),
    "g7_struct_indep": (G7S, q("structural_comparators_independent"), "value", "int"),
    "rt0_ref": (G7X, {"historical_label": "RT0"}, "reference_interval_ltra", "str"),
    "rt1_ref": (G7X, {"historical_label": "RT1"}, "reference_interval_ltra", "str"),
    "rt1_c": (G7X, {"historical_label": "RT1"}, "route_c_point", "str"),
    "rt2_ref": (G7X, {"historical_label": "RT2"}, "reference_interval_ltra", "str"),
    "rt2_obs": (G7X, {"historical_label": "RT2"}, "ltra_residue_span_supported", "str"),
    "rt2_n": (G7X, {"historical_label": "RT2"}, "n_supporting_states", "int"),
    "rt3_obs": (G7X, {"historical_label": "RT3"}, "ltra_residue_span_supported", "str"),
    "rt3_n": (G7X, {"historical_label": "RT3"}, "n_supporting_states", "int"),
    "rt4_obs": (G7X, {"historical_label": "RT4"}, "ltra_residue_span_supported", "str"),
    "rt4_n": (G7X, {"historical_label": "RT4"}, "n_supporting_states", "int"),
    "rt5_ref": (G7X, {"historical_label": "RT5"}, "reference_interval_ltra", "str"),
    "rt5_obs": (G7X, {"historical_label": "RT5"}, "ltra_residue_span_supported", "str"),
    "rt5_n": (G7X, {"historical_label": "RT5"}, "n_supporting_states", "int"),
    "rt5_states": (G7X, {"historical_label": "RT5"}, "state_span", "str"),
    "rt7_obs": (G7X, {"historical_label": "RT7"}, "ltra_residue_span_supported", "str"),
    "rt7_n": (G7X, {"historical_label": "RT7"}, "n_supporting_states", "int"),
    "rt7_c": (G7X, {"historical_label": "RT7"}, "route_c_point", "str"),
    "rt4_qual": (ERR, {"historical_label": "RT4"}, "correspondence_qualified", "str"),
}

# key -> (formula shown in the audit trail, callable over TABLE raw values and loaded tables)
# Each is a count/min over landed rows - the same derivation the governing record states.
DERIVED = {
    "g6_strata_total": "count(rows of g6_retron_subtype_strata.tsv)",
    "g6_strata_underpowered": "count(rows of g6_retron_subtype_strata.tsv with powered=UNDERPOWERED)",
    "g6_strata_excluded": ("count(powered=UNDERPOWERED) + [count(DefenseFinder powered=YES) - DF_subtype n_groups]"
                           " + [count(PADLOC powered=YES) - PL_subtype n_groups]  (E-g6-4)"),
    "ug25_min_real_mapped": "min(n_mapped) over the 28 rows of ug25_sequence_results.tsv",
    "ug25_n_seq": "count(rows of ug25_sequence_results.tsv)",
    "ug25_ctrl_max": "max(max_mapped) over the MONO, DI and REV rows of ug25_control_summary.tsv",
    "g6_ctrl_exceed_both": ("count(rows of g6_between_family_rho.tsv with analysis_id starting CTRL-VIS "
                            "or CTRL-REL and exceeds_null1=YES and exceeds_null2=YES)"),
}

# key -> (source, literal that must appear verbatim in it, rendered value)
# source is a repo-relative path, or "git:<commit>" for a commit message.
DOC = {
    "ug5_v2_monotone": (DEC_UG5, "monotone for 31 of 67 sequences = 46.3%", "31 of 67 sequences (46.3%)"),
    "g2l_score": (DEC_G2L, "**Verdict: `FAIL/BLOCK`. Score: 4/10.**", "FAIL/BLOCK, 4/10"),
    "ug25_review": (DEC_UG25, "**`PASS_WITH_REQUIRED_REPAIRS` · 7/10 · CONFIRMATORY TRANSFER: SUPPORTED",
                    "PASS_WITH_REQUIRED_REPAIRS, 7/10"),
    "g4b_review": (DEC_G4B, "> **`PASS_WITH_REQUIRED_REPAIRS` · 9/10 · MAY g5 BEGIN: YES**",
                   "PASS_WITH_REQUIRED_REPAIRS, 9/10"),
    "g5_review": ("git:6f4a7fe", "PASS_WITH_REQUIRED_REPAIRS, 8/10", "PASS_WITH_REQUIRED_REPAIRS, 8/10"),
    "g6_review": (DEC_G6E, "`PASS_WITH_REQUIRED_REPAIRS`, 6/10, **0 blockers**",
                  "PASS_WITH_REQUIRED_REPAIRS, 6/10, 0 blockers"),
    "g7a_review": (DEC_G7E, "`PASS_WITH_REQUIRED_REPAIRS`, 7/10, **0 blockers**",
                   "PASS_WITH_REQUIRED_REPAIRS, 7/10, 0 blockers"),
    "g6_thread": (DEC_REV, "`01a0b99f-4837-7ce1-9ddd-9d0138441c55`", "01a0b99f-4837-7ce1-9ddd-9d0138441c55"),
    "g7a_thread": (DEC_REV, "`01a0b9a1-1d76-7193-9d7b-89cb6a41e875`", "01a0b9a1-1d76-7193-9d7b-89cb6a41e875"),
    "profile_leng": (SPEC, "LENG 471", "471"),
    "profile_m": (SPEC, "`hhmake -M 50`", "hhmake -M 50"),
    "myrt_match": (DEC_G6E, "**369,370 of 369,381**", "369,370 of 369,381"),
    "myrt_direct": (DEC_G6E, "**363,447** carry a direct `by_myRT` call", "363,447"),
    "myrt_without": (DEC_G6E, "**5,934** without one are all labelled `Retron`", "5,934"),
    "g6_c2": (DEC_G6E, "(C2: 61 groups, ρ = 0.8689,\nNULL-2 p99 = 0.8779)",
              "61 groups, ρ = 0.8689 against NULL-2 p99 = 0.8779"),
    "g6_perm_floor": (DEC_G6E, "1/61 ≈ **0.0164**", "1/61 ≈ 0.0164"),
    "g6_n_analyses": (DEC_G6E, "across the **13** analyses", "13"),
    "g6_leak_hits": (DEC_G6E, "**11.2 %** (11.22 %, of 14,943 hits)", "11.2% of 14,943 retrieved hits"),
    "g6_leak_queries": (DEC_G6E, "**19.8 %** (595 / 3,000)", "19.8% (595 of 3,000 sampled queries)"),
    "g6_pcpos_bundle": (G6C, "Spearman rho = 0.9230", "0.9230"),
    "g6_pcpos_std": (DEC_G6E, "**0.9307** with\n  standard tie-aware Spearman", "0.9307"),
    "g6_vis_assoc": (DEC_G6E, "ρ = 0.5692 (C4)", "0.5692"),
    "closure_line": (DEC_CLOSED, "**Closure is workflow closure, not complete recovery.**",
                     "Closure is workflow closure, not complete recovery."),
    "g7a_route_c_note": (DEC_G7E, "g3 established that the four prior frames are coordinate\ntransfers over **one** "
                         "anchor-derived landmark set, not replication", "one anchor-derived landmark set"),
    "x05": (DEC_G7E, "\"In the case of Poch et al. (1989) the five motifs identified (regions a-e) correspond to our "
            "domains 3-7.\"", "Poch regions a–e ↔ Xiong domains 3–7"),
    "x06": (DEC_G7E, "\"In the case of Webster et al. (1989) the four blocks identified correspond to our "
            "domains 2-5.\"", "Webster blocks ↔ Xiong domains 2–5"),
    "cat_ltra": (DEC_G7E, "`CAT_STATE` 262 maps to LtrA 306 (YADD)", "LtrA 306 (YADD)"),
    "malik_missing": (DEC_CLOSED, "the defining source, Malik,\n  Burke & Eickbush 1999, is not held",
                      "Malik, Burke & Eickbush 1999"),
    "commit_closure": ("git:93a4e88", "rt07: close Stage 2 with explicit residual limitations", "93a4e88"),
    "commit_errata": ("git:3a19e2e", "rt07: apply the 13 required review repairs", "3a19e2e"),
    "commit_reviews": ("git:af7c405", "rt07: record the completed independent reviews of g6 and g7a", "af7c405"),
    "hia_pending": (DEC_CLOSED, "`human_input_audit: PENDING` on the landed bundles", "PENDING"),
}

# The final reviewed statuses. The build checks each against the erratum table, which is the
# governing machine-readable record (docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv),
# and fails if any differs. Nothing here is decided by this package.
STATUS = {
    "RT0": ("UNRESOLVED / NOT IDENTIFIABLE", "UNRESOLVED", ""),
    "RT1": ("UNRESOLVED / NOT IDENTIFIABLE", "UNRESOLVED", ""),
    "RT2": ("PARTIAL / INTERPRETIVE CORRESPONDENCE", "PARTIAL", ""),
    "RT3": ("ESTABLISHED OPERATIONAL CORRESPONDENCE", "ESTABLISHED", "with qualification"),
    "RT4": ("ESTABLISHED OPERATIONAL CORRESPONDENCE", "ESTABLISHED", "with frame-instability qualification"),
    "RT5": ("ESTABLISHED OPERATIONAL CORRESPONDENCE", "ESTABLISHED", "named jointly as RT5+RT6"),
    "RT6": ("PARTIAL / INTERPRETIVE CORRESPONDENCE", "PARTIAL", "jointly with RT5 only"),
    "RT7": ("ESTABLISHED OPERATIONAL CORRESPONDENCE", "ESTABLISHED", "with narrowed wording"),
}

# Superseded or withdrawn wording that must never reappear in any output of this package.
# Each regex names the governing record that withdrew it.
FORBIDDEN = [
    (r"RT0\s*=\s*M1", "withdrawn: M1-R85 contains RT0; it is not RT0 (E-g7a-5, Amendment 1)"),
    (r"R86\s*[-–]\s*R364", "withdrawn Blocker reading (E-g7a-5)"),
    (r"bracket(s|ed)? the truth", "withdrawn by E-g6-2"),
    (r"structure is real", "withdrawn by E-g6-2"),
    (r"three routes agree", "withdrawn by E-g7a-4"),
    (r"best-determined label", "withdrawn by E-g7a-4"),
    (r"significant at 1\s*%", "not permitted by E-g6-3"),
    (r"not an artefact of the mapper", "withdrawn by E-g6-8"),
    (r"stated domain junction", "withdrawn by E-g7a-4"),
]

# Every landed Stage-2 bundle this report relies on, with its role. Landing commits are read
# from git at build time, never typed.
BUNDLES = [
    ("rt07_g1_history_and_definition", "L1", "historical definition: sources, genealogy, evidence matrix"),
    ("rt07_g2_reference_reconstruction", "L1", "independent reconstruction of the landmarks on ALIGN_000044"),
    ("rt07_g3_prior_method_replication", "L1", "audit of prior RT0-RT7 methods and frames"),
    ("rt07_g4a_frame_recovery", "L2", "mapper frame recovery (reviewed 6/10, repaired)"),
    ("rt07_g4a_repaired", "L2", "repaired mapper development; hhmake -M sensitivity; profile"),
    ("rt07_ug5_holdout_gate", "L2", "UG5 holdout gate v2/v3 - falsified designs, retained"),
    ("FINAL_PRE_UG25_VALIDATION_BUNDLE", "L2", "frozen pre-holdout calibration and construction validation"),
    ("rt07_ug25_confirmatory", "L2", "single confirmatory transfer to a fresh lineage (Endpoint A)"),
    ("rt07_g4b_production_mapper", "L2", "the frozen production instrument"),
    ("rt07_g5a_eligibility_census", "L2", "the frozen eligibility denominator"),
    ("rt07_g5_catalogue_application", "L2", "the canonical mapped catalogue"),
    ("rt07_g6_family_architecture", "L3", "descriptive concordance across MyRT-defined strata"),
    ("rt07_g7a_rt0_rt7_bridge", "L4", "historical RT0-RT7 bridge on LtrA"),
]
