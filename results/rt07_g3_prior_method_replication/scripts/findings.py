#!/usr/bin/env python3
"""Prose and value lookups for the rt07_g3 report. The assembler computes nothing."""
from __future__ import annotations

VALUES: dict[str, tuple] = {
    "n_claims": ("g3_summary.tsv", {"quantity": "prior_claims_audited"}, "value", "int"),
    "n_repro": ("g3_summary.tsv",
                {"quantity": "verdict_reproduced_same_object_same_frame"}, "value", "int"),
    "n_partial": ("g3_summary.tsv", {"quantity": "verdict_partially_reproduced"},
                  "value", "int"),
    "n_circular": ("g3_summary.tsv", {"quantity": "verdict_circular_or_seed_dependent"},
                   "value", "int"),
    "n_objmis": ("g3_summary.tsv", {"quantity": "verdict_object_mismatch"}, "value", "int"),
    "n_framemis": ("g3_summary.tsv", {"quantity": "verdict_frame_mismatch"}, "value", "int"),
    "n_withdrawn": ("g3_summary.tsv", {"quantity": "verdict_withdrawn_by_prior_work"},
                    "value", "int"),
    "n_nottest": ("g3_summary.tsv", {"quantity": "verdict_not_testable"}, "value", "int"),
    "anchor_seed_pct": ("g3_summary.tsv", {"quantity": "anchors72_in_seed_pct"},
                        "value", "str"),
    "anchor_retron_pct": ("g3_summary.tsv",
                          {"quantity": "anchors72_also_in_retron_population_pct"},
                          "value", "str"),
    "gold_seed_pct": ("g3_summary.tsv", {"quantity": "gold175_uniq_in_seed_pct"},
                      "value", "str"),
    "gold_outside": ("g3_summary.tsv", {"quantity": "gold_panel_members_outside_the_seed"},
                     "value", "int"),
    "landmarks_inside": ("g3_summary.tsv", {"quantity": "prior_landmarks_inside_a_g2_region"},
                         "value", "str"),
    "blocks_anchored": ("g3_summary.tsv",
                        {"quantity": "prior_frame_blocks_fixed_by_a_published_motif"},
                        "value", "str"),
    "collapsing": ("g3_summary.tsv",
                   {"quantity": "prior_labels_collapsing_onto_one_g2_region"}, "value", "str"),
    "rt0_verdict": ("g3_summary.tsv", {"quantity": "rt0_object_verdict"}, "value", "str"),
    "controls_pass": ("g3_summary.tsv", {"quantity": "controls_pass"}, "value", "int"),
    "rt0_frame_extent": ("g3_rt0_object_audit.tsv",
                         {"quantity": "prior_frame_ltra_extent"}, "value", "str"),
    "rt0_alanine": ("g3_rt0_object_audit.tsv",
                    {"quantity": "blocker_rt0_conserved_alanine_ltra"}, "value", "int"),
    "rt0_covered_by_prior": ("g3_rt0_object_audit.tsv",
                             {"quantity": "prior_frame_covers_that_alanine"}, "value", "str"),
    "rt0_covered_by_g2": ("g3_rt0_object_audit.tsv",
                          {"quantity": "g2_region_covering_that_alanine"}, "value", "str"),
    "rt5_block": ("g3_prior_region_correspondence.tsv",
                  {"prior_region_id": "RT17_CORE:RT5"}, "best_g2_block", "str"),
    "rt6_block": ("g3_prior_region_correspondence.tsv",
                  {"prior_region_id": "RT17_CORE:RT6"}, "best_g2_block", "str"),
    "rt1_ltra": ("g3_prior_region_correspondence.tsv",
                 {"prior_region_id": "RT17_CORE:RT1"}, "ltra_start", "int"),
    "rt1_block": ("g3_prior_region_correspondence.tsv",
                  {"prior_region_id": "RT17_CORE:RT1"}, "best_g2_block", "str"),
    "rt17_leng": ("g3_frame_identity.tsv", {"frame_id": "RT17_CORE"}, "leng", "int"),
    "rt17_name": ("g3_frame_identity.tsv", {"frame_id": "RT17_CORE"},
                  "declared_name_inside_file", "str"),
    "pdb_anchors": ("g3_anchor_composition.tsv", {"property": "id_prefix:PDB"},
                    "value", "int"),
    "tagged_anchors": ("g3_anchor_composition.tsv", {"property": "expression_tag:His6"},
                       "value", "int"),
}

TITLE = "rt07_g3_prior_method_replication"
SUBTITLE = "What survives the prior work, and what was never the object it was named for"

SECTIONS = [
    dict(num="1", title="The audit",
         body="""{n_claims} prior claims were audited on object identity, frame identity, seed
         dependence, conditioning and reproducibility. Verdicts: {n_repro} reproduced in the
         same object and frame, {n_partial} partially reproduced, {n_circular} circular or
         seed-dependent, {n_objmis} object mismatches, {n_framemis} frame mismatch,
         {n_withdrawn} already withdrawn by the prior work, {n_nottest} not testable here.
         {controls_pass} of 4 controls pass.""",
         caveat="""No prior number became an acceptance criterion, including the ones that
         reproduced exactly.""",
         tables=["g3_prior_claim_verdicts.tsv", "g3_controls.tsv"]),
    dict(num="2", title="Independence: the anchors are the seed",
         body="""Re-measured by exact sequence identity, not by identifier: {anchor_seed_pct}%
         of the 72 anchors are members of the model seed, and {anchor_retron_pct}% are also
         members of the retron population they score. Only {pdb_anchors} of 72 carry a PDB
         identifier. New here: {tagged_anchors} carry a His6 expression tag and one carries a
         SUMO tag, so their residue numbering includes vector-derived sequence. The gold panel
         is {gold_seed_pct}% seed, leaving {gold_outside} members genuinely outside it.""",
         caveat="""These reproduce the prior audit's own figures exactly, from the files
         rather than from its report - which is what makes them usable.""",
         tables=["g3_set_overlap.tsv", "g3_anchor_composition.tsv"]),
    dict(num="3", title="Frames: four coordinate systems, one landmark set",
         body="""The primary frame ships as RT17_CORE.hmm but declares NAME {rt17_name},
         {rt17_leng} match states, and is byte-identical to B_span17.hmm. Carried onto shared
         LtrA residues, {landmarks_inside} prior landmark placements fall inside an
         independently reconstructed g2 region, and six of seven landmarks sit at the IDENTICAL
         LtrA residue in every prior frame.""",
         caveat="""PROPOSED: the four frames are not four independent determinations of the
         landmarks. They are four coordinate systems over one anchor-derived landmark set, so
         agreement between them prices transfer consistency, not replication.""",
         tables=["g3_frame_identity.tsv", "g3_prior_region_correspondence.tsv"]),
    dict(num="4", title="The seven-way partition does not survive reconciliation",
         body="""Only {blocks_anchored} prior frame blocks are fixed by a published motif; the
         rest are order-interpolated. The seven prior labels collapse onto SIX g2 regions,
         because {collapsing} both fall inside g2 block {rt5_block}.""",
         caveat="""No old seven-block result is defensible AS a seven-way partition after
         frame reconciliation. The landmarks and their ORDER survive; the seventh boundary
         does not.""",
         tables=["g3_prior_frame_correspondence.tsv"]),
    dict(num="5", title="RT0 was never measured on the RT0 region",
         body="""Verdict: {rt0_verdict}. The prior frame spans LtrA {rt0_frame_extent} and
         does not cover the conserved RT0 alanine at LtrA {rt0_alanine}
         (covered by the prior frame: {rt0_covered_by_prior}); the independently reconstructed
         g2 region {rt0_covered_by_g2} does cover it. The prior RT0 occupancy contrast is real
         and was measured with a declared positive control that passed - but on interpolated
         N-terminal blocks that exclude the only specific RT0 landmark available.""",
         caveat="""U01 stays open and the g2 scope limit stands: the claim that defines RT0 is
         cross-class and remains untestable on the available substrate. No RT0 occupancy value
         may be carried forward as an RT0 number.""",
         tables=["g3_rt0_object_audit.tsv"]),
    dict(num="6", title="RT1, measured and not interpreted",
         body="""RT1 is the only landmark that moves between prior frames, and its prior
         concordance is 0.75 against a declared 0.90 bar. In shared coordinates it falls at
         LtrA {rt1_ltra}, inside g2 block {rt1_block} - which lies in the region Blocker 2005
         assigns to RT0, not RT1.""",
         caveat="""The INTERPRETATION of the RT1 failure is not settled here. Whether it is a
         limitation of the method or an independent recovery of a weakness the founding
         authors flagged remains an operator decision; g3 adds one measured fact to it.""",
         tables=["g3_prior_claim_verdicts.tsv", "g3_handoff_to_g4.tsv"]),
]
