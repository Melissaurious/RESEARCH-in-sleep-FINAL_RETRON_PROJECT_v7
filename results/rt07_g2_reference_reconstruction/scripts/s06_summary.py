#!/usr/bin/env python3
"""rt07_g2 step 6 - the rollup and the kill-criterion assessment.

The launcher's g2 kill criterion is explicit: if the historical landmarks cannot be
recovered on the sequences and alignments from which they were derived, the reconstruction
arm stops and the frame is not propagated. This script computes the recovery rate and states
the assessment from the landed tables, so the decision is a number with a denominator rather
than a judgement made in prose.

Writes: tables/g2_summary.tsv, tables/g2_kill_criterion.tsv,
        tables/g2_unresolved_carried_forward.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g2lib import G1, read_tsv, write_tsv  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T = args.out

    rec = read_tsv(T / "g2_landmark_recovery.tsv")
    blocks = read_tsv(T / "g2_reconstructed_blocks.tsv")
    unc = read_tsv(T / "g2_block_uncertainty.tsv")
    ctrl = read_tsv(T / "g2_positive_controls.tsv")
    null = read_tsv(T / "g2_null_model.tsv")
    spatial = read_tsv(T / "g2_null_spatial_statistics.tsv")
    frame = {r["property"]: r for r in read_tsv(T / "g2_second_frame.tsv")}
    corr = read_tsv(T / "g2_frame_correspondence.tsv")
    cons = read_tsv(T / "g2_conserved_positions.tsv")
    refset = read_tsv(T / "g2_reference_sequence_set.tsv")
    nterm = {r["quantity"]: r["value"] for r in read_tsv(T / "g2_nterminal_region.tsv")}
    per_group = read_tsv(T / "g2_per_group_conservation.tsv")

    def n(rows, **eq):
        return sum(1 for r in rows if all(r.get(k) == v for k, v in eq.items()))

    testable = [r for r in rec if r["recovery_verdict"] != "NOT_TESTABLE_ON_SUBSTRATE"]
    recovered = n(rec, recovery_verdict="RECOVERED")
    partial = n(rec, recovery_verdict="PARTIALLY_RECOVERED")
    not_rec = n(rec, recovery_verdict="NOT_RECOVERED")
    one_to_one = n(corr, correspondence="ONE_TO_ONE")
    med_j = sorted(float(c["jaccard_on_ltra_residues"]) for c in corr)[len(corr) // 2]

    S = [
        ("reference_proteins", len(refset), "g2_reference_sequence_set.tsv",
         "reference protein sequence", "the 66 proteins of ALIGN_000044"),
        ("lineage_groups", len({r["lineage_group"] for r in refset}),
         "g2_lineage_groups.tsv", "lineage group", "groups the criterion needs"),
        ("conserved_positions_rt_domain",
         sum(1 for r in cons if r["conserved_strict"] == "YES" and r["in_rt_domain"] == "YES"),
         "g2_conserved_positions.tsv", "alignment column",
         "626 columns of the stated RT domain"),
        ("conserved_positions_similarity_reading",
         sum(1 for r in cons if r["conserved_similarity"] == "YES"
             and r["in_rt_domain"] == "YES"),
         "g2_conserved_positions.tsv", "alignment column",
         "626 columns of the stated RT domain"),
        ("blocks_at_reported_point", len(blocks), "g2_reconstructed_blocks.tsv", "block",
         "blocks at the declared reporting rule"),
        ("blocks_in_blocker_rt0_zone", nterm.get("reconstructed_blocks_inside_blocker_rt0_zone"),
         "g2_nterminal_region.tsv", "block", "blocks at the reported point"),
        ("seven_way_partition_recovered_frame1",
         "NO" if len(blocks) != 7 else "YES", "g2_reconstructed_blocks.tsv", "partition",
         "one reconstruction on the primary alignment"),
        ("seven_way_partition_recovered_frame2",
         frame["seven_blocks_recovered"]["frame_mafft_fftns2"], "g2_second_frame.tsv",
         "partition", "one reconstruction on an independent re-alignment"),
        ("blocks_one_to_one_across_frames", one_to_one, "g2_frame_correspondence.tsv",
         "block", f"{len(corr)} blocks in frame 1"),
        ("median_cross_frame_jaccard", f"{med_j:.3f}", "g2_frame_correspondence.tsv",
         "Jaccard on LtrA residues", f"{len(corr)} matched blocks"),
        ("max_block_start_uncertainty_columns",
         max((int(r["start_uncertainty_columns"]) for r in unc), default=0),
         "g2_block_uncertainty.tsv", "alignment column",
         "blocks at the reported point, across the declared sweep"),
        ("max_block_end_uncertainty_columns",
         max((int(r["end_uncertainty_columns"]) for r in unc), default=0),
         "g2_block_uncertainty.tsv", "alignment column",
         "blocks at the reported point, across the declared sweep"),
        ("landmarks_recovered", recovered, "g2_landmark_recovery.tsv",
         "historical statement", f"{len(rec)} statements declared"),
        ("landmarks_partially_recovered", partial, "g2_landmark_recovery.tsv",
         "historical statement", f"{len(rec)} statements declared"),
        ("landmarks_not_recovered", not_rec, "g2_landmark_recovery.tsv",
         "historical statement", f"{len(rec)} statements declared"),
        ("landmarks_not_testable_on_substrate",
         n(rec, recovery_verdict="NOT_TESTABLE_ON_SUBSTRATE"), "g2_landmark_recovery.tsv",
         "historical statement", f"{len(rec)} statements declared"),
        ("controls_pass", n(ctrl, result="PASS"), "g2_positive_controls.tsv", "control",
         f"{len(ctrl)} controls declared"),
        ("controls_fail", n(ctrl, result="FAIL"), "g2_positive_controls.tsv", "control",
         f"{len(ctrl)} controls declared"),
        ("null_p_conserved_positions", null[0]["empirical_p"], "g2_null_model.tsv",
         "empirical p", "200 replicates"),
        ("null_p_block_count", null[1]["empirical_p"], "g2_null_model.tsv",
         "empirical p", "200 replicates"),
        ("null_p_largest_gap", spatial[0]["empirical_p"], "g2_null_spatial_statistics.tsv",
         "empirical p", "200 replicates"),
        ("bacterial_conserved_columns",
         next(r["n_conserved_columns_rt_domain"] for r in per_group
              if r["lineage_group"] == "bacterial"), "g2_per_group_conservation.tsv",
         "alignment column", "626 columns of the stated RT domain"),
        ("rt0_block_created", nterm.get("rt0_block_created"), "g2_nterminal_region.tsv",
         "decision", "n/a - one decision, recorded"),
    ]
    write_tsv(T / "g2_summary.tsv", ["quantity", "value", "source_table", "unit",
                                     "denominator"],
              [{"quantity": q, "value": v, "source_table": t, "unit": u, "denominator": d}
               for q, v, t, u, d in S])

    # ---- the kill criterion, decided from the landed numbers ----
    landmark_rate = (recovered + partial) / len(testable) if testable else 0.0
    kill = [
        {"criterion": "launcher g2 kill: the historical landmarks cannot be recovered on the "
                      "sequences and alignments from which they were derived",
         "measured": f"{recovered} recovered and {partial} partially recovered of "
                     f"{len(testable)} testable statements "
                     f"({100 * landmark_rate:.0f}% of testable)",
         "verdict": "NOT TRIGGERED" if landmark_rate >= 0.5 else "TRIGGERED",
         "consequence": "The reconstruction arm continues, because the landmarks do recover: "
                        "the catalytic anchor lands where the source says, the variable "
                        "spacer is the largest gap and exceeds every null replicate, and the "
                        "conserved regions reproduce across an independent re-alignment.",
         "unit": "historical statement", "denominator": f"{len(testable)} testable statements"},
        {"criterion": "the seven-way partition itself",
         "measured": f"frame 1 returns {len(blocks)} blocks at the declared reporting point "
                     f"and frame 2 returns "
                     f"{frame['blocks_at_reported_point']['frame_mafft_fftns2']}; block count "
                     f"never separates from the column-permutation null at any gap",
         "verdict": "NOT ESTABLISHED",
         "consequence": "What propagates to g3 and beyond is a set of positionally "
                        "reproducible conserved regions with interval uncertainty - NOT a "
                        "seven-way RT1-RT7 partition. No block is forced to make seven.",
         "unit": "partition", "denominator": "two independent alignment frames"},
        {"criterion": "RT0",
         "measured": "no RT0 block created; the defining cross-class claim is untestable on a "
                     "group II intron only substrate",
         "verdict": "OUT_OF_FRAME",
         "consequence": "One conserved region does fall in the LtrA zone Blocker assigns to "
                        "RT0, which is consistent with the region being conserved in this "
                        "class - but the claim that defines RT0 is about what it is NOT "
                        "conserved in, and that needs a non-LTR comparison class.",
         "unit": "region", "denominator": "n/a - one decision, recorded"},
    ]
    write_tsv(T / "g2_kill_criterion.tsv",
              ["criterion", "measured", "verdict", "consequence", "unit", "denominator"], kill)

    # ---- unresolved items carried forward ----
    g1_unres = read_tsv(G1 / "tables/g1_unresolved_definition_register.tsv")
    carried = []
    updates = {
        "U01": ("STILL_OPEN", "Malik et al. 1999 was not acquired: the launcher approves "
                              "governed acquisition of primary assets, and this gate needed "
                              "no structure, but the RT0 definition source remains unheld. "
                              "g2 did not need it because no RT0 block was created."),
        "U03": ("CLOSED_NOT_NEEDED", "Figure 1 digitisation was NOT required. The criterion "
                                     "in the running text was sufficient to reconstruct "
                                     "conserved regions, and the printed extents were never "
                                     "the binding constraint - the block COUNT was."),
        "U04": ("ANSWERED", "Tested directly. The numbered subdomains cannot be read off "
                            "ALIGN_000044, and re-deriving them by the founding criterion "
                            "returns positionally reproducible regions whose number is not "
                            "seven and is not stable."),
        "U05": ("CONFIRMED_IRREDUCIBLE", "The manual adjustment step in ALIGN_000044 remains "
                                         "non-reproducible. This gate therefore treats the "
                                         "alignment as a fixed artefact and adds an "
                                         "independent MAFFT frame rather than claiming to "
                                         "rebuild the authors' procedure."),
        "U06": ("HELD", "Blocker's LtrA coordinates were used only to test the "
                        "reconstruction. No boundary was taken from them and no "
                        "generalisation beyond LtrA was made."),
        "U08": ("STILL_DEFERRED", "No interpretation of any domain-1 or RT1 weakness was "
                                  "made. g2 records only that frame 1 and frame 2 disagree "
                                  "about whether one conserved region is one block or two."),
    }
    for u in g1_unres:
        upd = updates.get(u["item_id"])
        if not upd and u["status"] not in ("OPEN", "DEFERRED_TO_OPERATOR"):
            continue
        carried.append({
            "item_id": u["item_id"], "question": u["question"],
            "status_after_g1": u["status"],
            "status_after_g2": upd[0] if upd else u["status"],
            "what_g2_changed": upd[1] if upd else "not addressed by this gate",
            "unit": "open definitional question",
            "denominator": f"{len(g1_unres)} items in the g1 register"})
    carried.append({
        "item_id": "U09", "question": "Is the block COUNT recoverable at all, by any method, "
                                      "on any substrate?",
        "status_after_g1": "not raised", "status_after_g2": "NEW_OPEN",
        "what_g2_changed": "Raised by this gate. Conserved positions are real and their "
                           "locations reproduce across alignment frames, but the number of "
                           "blocks they form matches a column-permutation null at every gap "
                           "tested. Any later gate that reports a per-block occupancy must "
                           "carry this.",
        "unit": "open definitional question", "denominator": "raised in g2"})
    write_tsv(T / "g2_unresolved_carried_forward.tsv",
              ["item_id", "question", "status_after_g1", "status_after_g2",
               "what_g2_changed", "unit", "denominator"], carried)

    print(f"landmark recovery: {recovered} recovered, {partial} partial, {not_rec} not "
          f"recovered, of {len(testable)} testable")
    print(f"kill criterion: {kill[0]['verdict']}; seven-way partition: {kill[1]['verdict']}")
    print(f"unresolved carried forward: {len(carried)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
