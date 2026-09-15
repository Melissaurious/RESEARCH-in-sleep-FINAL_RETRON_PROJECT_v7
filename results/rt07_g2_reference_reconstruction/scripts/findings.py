#!/usr/bin/env python3
"""Prose and value lookups for the rt07_g2 report. The assembler computes nothing."""
from __future__ import annotations

# key -> (table, {selector column: value}, value column, format)
VALUES: dict[str, tuple] = {
    "n_proteins": ("g2_summary.tsv", {"quantity": "reference_proteins"}, "value", "int"),
    "n_groups": ("g2_summary.tsv", {"quantity": "lineage_groups"}, "value", "int"),
    "n_cons": ("g2_summary.tsv", {"quantity": "conserved_positions_rt_domain"}, "value", "int"),
    "n_cons_sim": ("g2_summary.tsv", {"quantity": "conserved_positions_similarity_reading"},
                   "value", "int"),
    "n_blocks": ("g2_summary.tsv", {"quantity": "blocks_at_reported_point"}, "value", "int"),
    "n_blocks_f2": ("g2_second_frame.tsv", {"property": "blocks_at_reported_point"},
                    "frame_mafft_fftns2", "int"),
    "n_cons_f2": ("g2_second_frame.tsv", {"property": "conserved_positions"},
                  "frame_mafft_fftns2", "int"),
    "seven_f1": ("g2_summary.tsv", {"quantity": "seven_way_partition_recovered_frame1"},
                 "value", "str"),
    "seven_f2": ("g2_summary.tsv", {"quantity": "seven_way_partition_recovered_frame2"},
                 "value", "str"),
    "one_to_one": ("g2_summary.tsv", {"quantity": "blocks_one_to_one_across_frames"},
                   "value", "int"),
    "median_j": ("g2_summary.tsv", {"quantity": "median_cross_frame_jaccard"}, "value", "str"),
    "p_cons": ("g2_summary.tsv", {"quantity": "null_p_conserved_positions"}, "value", "str"),
    "p_block": ("g2_summary.tsv", {"quantity": "null_p_block_count"}, "value", "str"),
    "p_gap": ("g2_summary.tsv", {"quantity": "null_p_largest_gap"}, "value", "str"),
    "n_rec": ("g2_summary.tsv", {"quantity": "landmarks_recovered"}, "value", "int"),
    "n_part": ("g2_summary.tsv", {"quantity": "landmarks_partially_recovered"}, "value", "int"),
    "n_notrec": ("g2_summary.tsv", {"quantity": "landmarks_not_recovered"}, "value", "int"),
    "n_nottest": ("g2_summary.tsv", {"quantity": "landmarks_not_testable_on_substrate"},
                  "value", "int"),
    "ctrl_pass": ("g2_summary.tsv", {"quantity": "controls_pass"}, "value", "int"),
    "ctrl_fail": ("g2_summary.tsv", {"quantity": "controls_fail"}, "value", "int"),
    "bact_cons": ("g2_summary.tsv", {"quantity": "bacterial_conserved_columns"},
                  "value", "int"),
    "rt0_block": ("g2_summary.tsv", {"quantity": "rt0_block_created"}, "value", "str"),
    "rt0_zone_blocks": ("g2_summary.tsv", {"quantity": "blocks_in_blocker_rt0_zone"},
                        "value", "str"),
    "yxdd_block": ("g2_landmark_recovery.tsv", {"statement_id": "H05"}, "observed", "str"),
    "spacer_obs": ("g2_landmark_recovery.tsv", {"statement_id": "H06"}, "observed", "str"),
    "kill_verdict": ("g2_kill_criterion.tsv",
                     {"criterion": "the seven-way partition itself"}, "verdict", "str"),
    "kill_main": ("g2_kill_criterion.tsv",
                  {"criterion": "launcher g2 kill: the historical landmarks cannot be "
                                "recovered on the sequences and alignments from which they "
                                "were derived"}, "verdict", "str"),
    "unc_max_start": ("g2_summary.tsv", {"quantity": "max_block_start_uncertainty_columns"},
                      "value", "int"),
    "unc_max_end": ("g2_summary.tsv", {"quantity": "max_block_end_uncertainty_columns"},
                    "value", "int"),
}

TITLE = "rt07_g2_reference_reconstruction"
SUBTITLE = ("The landmarks reconstruct. The seven-way partition does not.")

SECTIONS = [
    dict(num="1", title="What was reconstructed, and on what",
         body="""The substrate is ALIGN_000044 itself - the alignment Zimmerly 2001 adjusted
         its inherited subdomain labels against, acquired and hash-verified in g1.
         {n_proteins} proteins in {n_groups} lineage groups, assigned by declared keyword
         rules over the record's own description lines. Applying the Xiong & Eickbush
         criterion verbatim - a residue present in over 50% of the elements of at least three
         of four groups - yields {n_cons} conserved positions in the stated RT domain
         ({n_cons_sim} under the chemically-similar reading).""",
         caveat="""No comparator was read. No Toro, Mestre, myRT, SPIRE, prior HMM, prior
         boundary or prior anchor set touched this reconstruction; those belong to g3.""",
         tables=["g2_reference_sequence_set.tsv", "g2_conserved_positions.tsv"]),
    dict(num="2", title="The conserved positions are real",
         body="""Shuffling residues within each sequence destroys the signal completely:
         across 200 replicates the null never produced a single conserved column, against
         {n_cons} observed (empirical p={p_cons}). The largest gap between consecutive
         conserved positions also exceeds every replicate (p={p_gap}), so the conserved
         positions are not scattered evenly - they leave one long empty stretch.""",
         caveat="""{ctrl_pass} of the declared controls pass and {ctrl_fail} fails. The
         failure is reported in section 4 and it is the most important number in this
         bundle.""",
         tables=["g2_null_model.tsv", "g2_null_spatial_statistics.tsv"]),
    dict(num="3", title="The landmarks recover",
         body="""Of the declared historical statements, {n_rec} recover outright, {n_part}
         recover partially, {n_notrec} do not, and {n_nottest} are not testable on this
         substrate. The catalytic motif lands exactly where Zimmerly 2001 says it does:
         {yxdd_block}. The widest inter-block gap is the one the source describes as the
         variable insertion site: {spacer_obs}. Within-group conservation is close to the
         authors' own figures - {bact_cons} conserved columns for the bacterial group against
         their published 94.""",
         caveat="""Kill criterion: {kill_main}. The landmarks do recover on the substrate they
         came from, so the reconstruction arm continues.""",
         tables=["g2_landmark_recovery.tsv", "g2_interblock_spacers.tsv",
                 "g2_per_group_conservation.tsv"]),
    dict(num="4", title="The block COUNT does not",
         body="""At the reporting point declared before any block was counted, the criterion
         returns {n_blocks} blocks, not seven. Re-aligning the same {n_proteins} sequences
         independently with MAFFT returns {n_blocks_f2}. Seven blocks recovered in frame one:
         {seven_f1}; in frame two: {seven_f2}. And the count never separates from a
         column-permutation null at any gap in the declared sweep (p={p_block} at the
         reporting point) - scattering the same conserved positions at random produces just
         as many blocks.""",
         caveat="""{kill_verdict}: what propagates to later gates is a set of positionally
         reproducible conserved regions with interval uncertainty, NOT an RT1-RT7 partition.
         No block was split or merged to make seven.""",
         tables=["g2_parameter_sweep.tsv", "g2_null_by_gap.tsv", "g2_second_frame.tsv"]),
    dict(num="5", title="Positions agree across frames even where the count does not",
         body="""Matched on shared LtrA residues rather than on block index, {one_to_one} of
         the frame-one blocks have a one-to-one counterpart in the independent re-alignment,
         at a median Jaccard of {median_j}. The single disagreement is one conserved region
         that frame one treats as a single block and frame two splits. Conserved positions
         themselves are stable: {n_cons} against {n_cons_f2}.""",
         caveat="""PROPOSED: the reconstruction is stable in WHERE the conserved regions are
         and unstable in HOW MANY blocks they are cut into. That distinction is the finding,
         and it is what a later occupancy analysis has to respect.""",
         tables=["g2_frame_correspondence.tsv", "g2_second_frame_blocks.tsv"]),
    dict(num="6", title="RT0 was not created",
         body="""RT0 block created: {rt0_block}. Block {rt0_zone_blocks} falls inside the
         LtrA region Blocker 2005 assigns to RT0, and that region is conserved here - which
         is what Zimmerly's statement predicts for group II intron RTs. But the claim that
         DEFINES subdomain 0 is that it is conserved only between group II intron and non-LTR
         RTs, and this substrate has no non-LTR class. The claim is untestable here and no
         block was created because later literature uses the name.""",
         caveat="""Uncertainty is carried as intervals, not edges: the widest block start
         interval across the declared sweep is {unc_max_start} columns and the widest end
         interval {unc_max_end}. The sources state a procedure and no residue edges, so no
         single-column boundary is claimed.""",
         tables=["g2_nterminal_region.tsv", "g2_block_uncertainty.tsv",
                 "g2_unresolved_carried_forward.tsv"]),
]
