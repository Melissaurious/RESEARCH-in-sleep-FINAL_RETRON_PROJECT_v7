#!/usr/bin/env python3
"""ledger - transcribed Stage-2 records: reviews, negative results, claims and the figure plan.

Nothing here is measured. Every review row carries the governing record and a literal string
that build.py requires to be present in that record, so a mistranscribed verdict or score fails
the build. Numbers inside prose cells are {{key}} placeholders resolved through findings.py.
"""
from __future__ import annotations

D = "docs/decisions/"

# (seq, layer, object reviewed, verdict, score, disposition, record, literal that must be in it)
# Scope: the review outcomes recorded in docs/decisions/ and the g5 commit message. The ledger
# is not asserted to be exhaustive for g1-g3, whose review history is carried in their bundles.
REVIEWS = [
    (1, "L2", "g4 design (identifiability), round 1", "not ready", "3",
     "design replaced by the identifiability redesign",
     D + "2026-09-16_stage2_g4_identifiability_redesign.md", "score 3 / 10, verdict `not ready`"),
    (2, "L2", "g4 identifiability redesign, round 2", "not ready", "4",
     "stopped for operator decision; scope separated",
     D + "2026-09-16_stage2_g4_review_round2_and_repairs.md", 'round 2:  score 4 / 10,  verdict "not ready"'),
    (3, "L2", "full-length-first design", "FAIL/BLOCK", "5",
     "errata verified; forks returned to the operator",
     D + "2026-09-16_stage2_full_length_first_errata.md", "FAIL/BLOCK at 5/10"),
    (4, "L2", "g4a frame recovery", "PASS_WITH_REQUIRED_REPAIRS", "6",
     "repairs required; UG5 holdout gate mandated",
     D + "2026-09-16_stage2_g4a_review_outcome_and_repairs.md", "PASS_WITH_REQUIRED_REPAIRS (6/10)"),
    (5, "L2", "repaired g4a + UG5 gate", "FAIL/BLOCK", "5",
     "two verified bugs; eight bounded repairs",
     D + "2026-09-16_stage2_g4a_repair_ug5_review_outcome.md", "FAIL/BLOCK (5/10)"),
    (6, "L2", "UG5 v3 placement rule", "FAIL/BLOCK", "5",
     "v3 reclassified as a detection sub-gate, not a mapper gate",
     D + "2026-09-16_stage2_ug5_v3_review_outcome.md", "FAIL/BLOCK (5/10)"),
    (7, "L2", "G2L residue-transfer gate", "FAIL/BLOCK", "4",
     "g4b not authorised; no frozen score rule; next holdout must be untouched and genealogically audited",
     D + "2026-09-17_stage2_g2l_transfer_review_FAILED.md", "**Verdict: `FAIL/BLOCK`. Score: 4/10.**"),
    (8, "L2", "mapper validation repair", "PASS_WITH_REQUIRED_REPAIRS", "6",
     "class B; UG25 stays sealed; six bounded repairs",
     D + "2026-09-17_stage2_mapper_validation_review_outcome.md", "PASS_WITH_REQUIRED_REPAIRS (6/10), class B"),
    (9, "L2", "mapper repair v2", "PASS_WITH_REQUIRED_REPAIRS", "6",
     "class B; UG25 stays sealed; seven new repairs",
     D + "2026-09-17_stage2_mapper_repair_v2_review_outcome.md", "PASS_WITH_REQUIRED_REPAIRS (6/10), class B"),
    (10, "L2", "FINAL_PRE_UG25_VALIDATION_BUNDLE, round 1", "class B", "7",
     "three bounded repairs; UG25 still sealed",
     D + "2026-09-17_stage2_final_pre_ug25_bundle.md", "reviewed: 7/10, class B"),
    (11, "L2", "FINAL_PRE_UG25_VALIDATION_BUNDLE, round 2", "FAIL_BLOCK (formal field)", "8",
     "authorised blocker closed per reviewer; new residual classed out-of-scope, non-load-bearing",
     D + "2026-09-17_stage2_ug25_confirmatory_closed.md", "`8/10`; classification `B`"),
    (12, "L2", "UG25 confirmatory transfer, post-run", "PASS_WITH_REQUIRED_REPAIRS", "7",
     "CONFIRMATORY TRANSFER SUPPORTED; validation closed (Endpoint A)",
     D + "2026-09-17_stage2_ug25_confirmatory_closed.md",
     "**`PASS_WITH_REQUIRED_REPAIRS` · 7/10 · CONFIRMATORY TRANSFER: SUPPORTED"),
    (13, "L2", "g4b production packaging, round 1", "PASS_WITH_REQUIRED_REPAIRS", "6",
     "identity-binding repairs",
     D + "2026-09-17_stage2_g4b_production_packaging.md",
     "**Round 1** (thread `01a0afd9-39e8`): `PASS_WITH_REQUIRED_REPAIRS`, **6/10**"),
    (14, "L2", "g4b production packaging, round 2", "PASS_WITH_REQUIRED_REPAIRS", "9",
     "g5 authorised",
     D + "2026-09-17_stage2_g4b_production_packaging.md", "`PASS_WITH_REQUIRED_REPAIRS` · 9/10 · MAY g5 BEGIN: YES"),
    (15, "L2", "g5 catalogue application", "PASS_WITH_REQUIRED_REPAIRS", "8",
     "canonical g5 dataset trustworthy for g6; both required findings closed",
     "git:6f4a7fe", "PASS_WITH_REQUIRED_REPAIRS, 8/10"),
    (16, "L3", "g6, first attempt", "NOT COMPLETED (external usage limit)", "",
     "gate held OPEN; bounded use only; not self-reviewed",
     D + "2026-09-18_stage2_g6_bs15_open_and_bounded_use.md", "stays OPEN"),
    (17, "L4", "g7a, first attempts", "NOT COMPLETED (fallback reviewer failed)", "",
     "gate held OPEN; failed attempt made durable",
     D + "2026-09-18_stage2_g7a_review_attempt_failed.md", "stays OPEN"),
    (18, "L5", "g6 family architecture", "PASS_WITH_REQUIRED_REPAIRS", "6",
     "0 blockers; 8 required repairs applied as errata E-g6-1..8",
     D + "2026-09-19_stage2_g6_review_errata.md", "`PASS_WITH_REQUIRED_REPAIRS`, 6/10, **0 blockers**"),
    (19, "L5", "g7a historical bridge", "PASS_WITH_REQUIRED_REPAIRS", "7",
     "0 blockers; 5 required repairs applied as errata E-g7a-1..5; all 8 statuses preserved",
     D + "2026-09-19_stage2_g7a_review_errata.md", "`PASS_WITH_REQUIRED_REPAIRS`, 7/10, **0 blockers**"),
]

# (id, layer, result, what it rules out, why it is informative, source)
NEGATIVES = [
    ("N01", "L1", "The held sources state a residue boundary for {{g1_stated_boundary}} of {{g1_regions}} "
     "region names; {{g1_derivable}} are derivable only as a procedure.",
     "Reading RT0-RT7 as a set of published residue coordinates.",
     "Shows the labels are procedural objects; any coordinate must be reconstructed and carry an interval.",
     "results/rt07_g1_history_and_definition/tables/g1_resolved_values.tsv"),
    ("N02", "L1", "The seven-way partition is recovered in the independent frame ({{g2_seven_f2}}) but not "
     "the primary frame ({{g2_seven_f1}}); block-count null p = {{g2_p_block}}. Verdict on the partition "
     "itself: {{g2_kill_verdict}}.",
     "Treating the number of numbered domains as a stable, recoverable property of the alignment.",
     "Conserved positions and the widest gap beat their nulls (p = {{g2_p_cons}}, {{g2_p_gap}}); only the "
     "count does not. Placement is recoverable, cardinality is frame-dependent.",
     "results/rt07_g2_reference_reconstruction/tables/g2_resolved_values.tsv"),
    ("N03", "L1", "No reconstructed block corresponds to RT0 (rt0_block_created = {{g2_rt0_block}}).",
     "An alignment-derived RT0 coordinate.",
     "RT0 is not recovered even on the sequences from which the numbered series was built.",
     "results/rt07_g2_reference_reconstruction/tables/g2_resolved_values.tsv"),
    ("N04", "L1", "Of {{g3_claims}} prior claims, {{g3_repro}} reproduced on the same object and frame; "
     "{{g3_circular}} were circular or seed-dependent; {{g3_objmis}} object mismatches; RT0 verdict "
     "{{g3_rt0_verdict}}; {{g3_collapsing}} collapse onto one reconstructed region.",
     "Reusing prior RT0-RT7 coordinate frames as independent evidence.",
     "The prior frames are coordinate transfers over one anchor-derived landmark set; this is why Route C "
     "is corroboration, not replication (E-g7a-1).",
     "results/rt07_g3_prior_method_replication/tables/g3_resolved_values.tsv"),
    ("N05", "L2", "Two design reviews returned 'not ready' (3/10, 4/10) and the full-length-first design "
     "FAIL/BLOCK (5/10).",
     "Estimating a universal full-length RT0-RT7 architecture with the available data.",
     "Forced the identifiability redesign: the mapper estimates conserved-state occupancy, not domains.",
     "docs/decisions/2026-09-16_stage2_g4_review_round2_and_repairs.md"),
    ("N06", "L2", "Under hhmake -M a2m, DGRs and AbiA retain {{a2m_dgr_all}} and {{a2m_abia_all}} "
     "all-partner states; under -M 50 the all-partner core is {{m50_ug5_pct}}-{{m50_gii_pct}}% of the "
     "full consensus.",
     "A universal conserved core that is invariant to the match-state convention.",
     "Fixes the instrument's scope: it is validated under -M 50 only; robustness under a2m and "
     "equivalence under -M 60 are not claimed.",
     "results/rt07_g4a_repaired/tables/g4a_hhmake_M_sensitivity.tsv"),
    ("N07", "L2", "UG5 gate v2 failed its predeclared criterion 2: monotone placement for "
     "{{ug5_v2_monotone}}.",
     "Transfer of the v2 placement rule to the UG5 holdout.",
     "A predeclared falsification, retained as a valid result; it is why the transfer test was redesigned.",
     "docs/decisions/2026-09-16_stage2_ug5_v2_closed_failed.md"),
    ("N08", "L2", "UG5 v3 FAIL/BLOCK (5/10): a detection sub-gate, not a mapper gate.",
     "Counting UG5 v3 as mapper validation.",
     "Separated detection from residue mapping in every later gate.",
     "docs/decisions/2026-09-16_stage2_ug5_v3_review_outcome.md"),
    ("N09", "L2", "G2L residue-transfer gate FAIL/BLOCK ({{g2l_score}}).",
     "G2L as a mapper transfer test: criterion 2 (a frozen score rule) was not met, and G2L is a fresh "
     "family within a related lineage, not a fresh lineage.",
     "Led to the posterior-based support rule and the predeclared genealogy audit: UG25 has {{ug25_overlap}} exact overlaps with construction "
     "and {{ug25_fulllink}} sequences meeting the full link rule ({{ug25_class}}).",
     "docs/decisions/2026-09-17_stage2_g2l_transfer_review_FAILED.md"),
    ("N10", "L3", "The full between-family concordance ({{g6_rho}}) does not exceed the sequence-level "
     "null p99 ({{g6_null1}}); it exceeds the cluster-level null p99 ({{g6_null2}}).",
     "Reading g6 as significant under every reasonable null.",
     "The two nulls are sensitivity analyses with opposite biases, not bounds (E-g6-2).",
     "results/rt07_g6_family_architecture/tables/g6_between_family_rho.tsv"),
    ("N11", "L3", "The label-free within-Retron arm is {{g6_lf_verdict}}; {{g6_strata_excluded}} of "
     "{{g6_strata_total}} retron subtype strata did not enter a distance matrix.",
     "Label-free recovery of retron subtype structure.",
     "Without an external label the descriptor's concordance is untested at subtype level.",
     "results/rt07_g6_family_architecture/tables/g6_within_retron_rho.tsv"),
    ("N12", "L4", "RT0 and RT1 have no supported crosswalk: zero frozen anchors fall in LtrA "
     "{{rt0_ref}} or {{rt1_ref}}; anchor reach is LtrA {{g7_anchor_span}}.",
     "Any operational RT0 or RT1 coordinate from this instrument.",
     "Localises the limit: historical (no stated boundary; defining source not held) and instrumental "
     "(no N-terminal anchors). Not a statement of biological absence.",
     "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv"),
    ("N13", "L4", "{{g7_struct_indep}} independent structural comparators; {{g7_missing}} primary asset "
     "missing ({{malik_missing}}, the defining source for RT0).",
     "Structural or primary-source adjudication of RT0 within Stage 2.",
     "Names exactly what new evidence could change the RT0/RT1 statuses.",
     "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_summary.tsv"),
]

# Claims the thesis may make. (id, layer, claim, evidence keys, permitted-wording note)
CLAIMS = [
    ("S2-01", "L1", "Historical RT0-RT7 are procedural labels: of {{g1_regions}} region names in the held "
     "sources, {{g1_stated_boundary}} has a stated residue boundary.",
     ["g1_regions", "g1_stated_boundary", "g1_derivable", "g1_quotes", "g1_quotes_bad"],
     "held sources only; Malik 1999 not held"),
    ("S2-02", "L1", "The numbered landmarks are reconstructable on ALIGN_000044 ({{g2_proteins}} proteins): "
     "conserved positions and gap structure beat their nulls, the block count does not.",
     ["g2_proteins", "g2_blocks", "g2_blocks_f2", "g2_p_cons", "g2_p_gap", "g2_p_block", "g2_kill_verdict"],
     "project reconstruction, interval-level only"),
    ("S2-03", "L1", "Prior RT0-RT7 frames are not independent: {{g3_repro}} of {{g3_claims}} prior claims "
     "reproduced; RT0 is an object mismatch.",
     ["g3_claims", "g3_repro", "g3_circular", "g3_rt0_verdict", "g3_collapsing"],
     "audit of prior methods, not of the biology"),
    ("S2-04", "L2", "The conserved-state mapper transfers to one fresh lineage (UG25) under hhmake -M 50.",
     ["ug25_k0_med", "ug25_k1_med", "t1", "ug25_c3", "ug25_c4", "ug25_class", "ug25_review"],
     "Endpoint A only; no transfer beyond UG25 claimed"),
    ("S2-05", "L2", "Synthetic sequence controls do not reach the commitment threshold: the maximum mapped "
     "anchors in any control is {{ug25_ctrl_max}} against K_MIN {{k_min}}.",
     ["ug25_mono_max", "ug25_di_max", "ug25_rev_max", "k_min", "ug25_min_real_mapped"],
     "specificity against unrelated natural proteins not claimed"),
    ("S2-06", "L2", "The instrument's conserved core depends on the match-state convention.",
     ["m50_gii_all", "a2m_gii_all", "a2m_dgr_all", "a2m_abia_all"],
     "no universal architecture; valid under -M 50 only"),
    ("S2-07", "L2", "The catalytic state is a single frozen HMM state with {{cat_agree}} construction agreement.",
     ["cat_state", "cat_count", "cat_agree"],
     "separate denominator from the 150 anchors"),
    ("S2-08", "L2", "The eligible Stage-1 catalogue is {{g5a_eligible}} of {{g5a_total}} exact RTs; "
     "{{g5_inspectable}} are inspectable.",
     ["g5a_total", "g5a_eligible", "g5a_short", "g5a_nonstd", "g5_inspectable", "g5_abstained", "g5_failures"],
     "abstention is not failure and not absence"),
    ("S2-09", "L2", "Among CAT_STATE-mapped sequences, {{g5_cat_ratio}} carry a [YF].DD residue at that state.",
     ["g5_cat_mapped", "g5_cat_conf", "g5_cat_ratio"],
     "motif concordance at a state, not residue-level truth"),
    ("S2-10", "L3", "The mapper-derived descriptor shows split-half concordance among predominantly "
     "MyRT-derived family strata ({{g6_rho}}, {{g6_groups}} strata).",
     ["g6_rho", "g6_null1", "g6_null2", "g6_groups", "g6_nseq", "myrt_match", "g6_review"],
     "descriptive concordance only; not independent family discovery (E-g6-1)"),
    ("S2-11", "L3", "Concordance persists after conditioning on scalar MAPPED fraction and relatedness "
     "collapse: {{g6_ctrl_exceed_both}} restricted analyses exceed every sampled replicate of both nulls.",
     ["g6_ctrl_exceed_both", "g6_perm_floor", "g6_n_analyses", "g6_vis_assoc"],
     "not 1%-level significance; no multiplicity control (E-g6-3, E-g6-8)"),
    ("S2-12", "L3", "Within retrons, DefenseFinder and PADLOC subtype strata show concordance "
     "({{g6_df_rho}}, {{g6_pl_rho}}) on their own denominators; the label-free arm is underpowered.",
     ["g6_df_rho", "g6_df_groups", "g6_pl_rho", "g6_pl_groups", "g6_lf_verdict", "g6_strata_excluded"],
     "tool annotations never pooled; 26 of 50 strata excluded"),
    ("S2-13", "L4", "On LtrA the frozen states support observable portions of the reconstructed RT3, RT4, "
     "joint RT5+RT6 and RT7 intervals.",
     ["rt3_obs", "rt4_obs", "rt5_obs", "rt7_obs", "g7_est", "g7a_review"],
     "LtrA-local interpretation-layer correspondence"),
    ("S2-14", "L4", "RT4's cardinality is frame-dependent: 1:1 in the primary frame, split into 3 in the "
     "independent frame (Jaccard {{g2_b4_j}}).",
     ["g2_b4_f1", "g2_b4_f2", "g2_b4_j", "rt4_qual"],
     "E-g7a-3; must be shown wherever RT4 is annotated"),
    ("S2-15", "L4", "RT5 is the only label with a source-stated residue-level catalytic feature measured "
     "on LtrA (CAT_STATE {{cat_state}} -> {{cat_ltra}}).",
     ["cat_state", "cat_ltra", "rt5_ref", "x05", "x06"],
     "named only as joint RT5+RT6 (E-g7a-2)"),
    ("S2-16", "L4", "RT2 is partial: only LtrA {{rt2_obs}} of reconstructed {{rt2_ref}} is observed.",
     ["rt2_obs", "rt2_ref", "rt2_n", "g7_anchor_span"],
     "no statement about the unobserved N-terminal part"),
    ("S2-17", "L4", "RT0 and RT1 are unresolved: no stated boundary in held sources and the frozen anchors "
     "reach only LtrA {{g7_anchor_span}}, C-terminal of both reference intervals ({{rt0_ref}}, {{rt1_ref}}).",
     ["rt0_ref", "rt1_ref", "g7_anchor_span", "g2_rt0_block", "g3_rt0_verdict", "malik_missing"],
     "not biological absence; may not be resolved inferentially"),
    ("S2-18", "L5", "Both terminal Stage-2 analyses passed vendor-disjoint independent review with 0 blockers.",
     ["g6_review", "g7a_review", "g6_thread", "g7a_thread"],
     "repairs applied as additive errata; frozen outputs unchanged"),
    ("S2-19", "L5", "Stage 2 is closed as workflow closure, not complete historical recovery.",
     ["closure_line", "hia_pending"],
     "human_input_audit PENDING before thesis use of any number"),
]

# The figure plan. (id, stem, question, source tables, may show, may not show)
FIGURES = [
    ("F1", "F1_review_trajectory", "How did independent review shape Stage 2?",
     "tables/stage2_review_ledger.tsv (transcribed from docs/decisions/)",
     "every recorded review score in sequence, by layer, against the >=6 transition threshold",
     "any quality ranking of the gates beyond their recorded scores"),
    ("F2", "F2_validation", "Is the instrument callable, specific and transferable?",
     "FINAL_PRE_UG25_VALIDATION_BUNDLE construction_validation_family.tsv; rt07_ug25_confirmatory "
     "ug25_component_summary.tsv, ug25_control_summary.tsv, ug25_sequence_results.tsv",
     "construction family medians and ranges vs T1; UG25 components vs T1; control maxima vs K_MIN and "
     "the weakest real UG25 sequence",
     "residue-level accuracy; transfer beyond UG25; specificity against natural non-RT proteins"),
    ("F3", "F3_match_state_sensitivity", "Is there a universal conserved core?",
     "rt07_g4a_repaired g4a_hhmake_M_sensitivity.tsv",
     "all-partner states as % of each family's full consensus under -M 50, 60 and a2m",
     "robustness of the instrument under a2m"),
    ("F4", "F4_catalogue_application", "What population was mapped, and how did it resolve?",
     "rt07_g5a_eligibility_census g5a_census_summary.tsv; rt07_g5_catalogue_application "
     "g5_qc_headline.tsv, g5_qc_status_counts.tsv; rt07_g6_family_architecture g6_call_state_totals.tsv",
     "denominator funnel; inspectability status; call-state composition of all state calls",
     "DELETED_STATE or NO_SUPPORTED_MAPPING as biological absence"),
    ("F5", "F5_g6_concordance", "Is the descriptor reproducible across family strata?",
     "rt07_g6_family_architecture g6_between_family_rho.tsv, g6_within_retron_rho.tsv",
     "each of the 13 analyses: observed rank correlation vs NULL-1 and NULL-2 p99, with the E-g6 captions",
     "independent family discovery; bounds; 1%-level significance"),
    ("F6", "F6_rt0_rt7_final", "What is the final reviewed status of each historical label on LtrA?",
     "rt07_g7a_rt0_rt7_bridge g7a_state_to_residue.tsv, g7a_crosswalk_resolved.tsv; "
     "docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv",
     "anchor reach; reconstructed intervals; supported spans; RT4 frame instability; joint RT5+RT6; "
     "RT0/RT1 unresolved outside reach",
     "any RT0 or RT1 coordinate; RT6 alone; universal domains"),
]
