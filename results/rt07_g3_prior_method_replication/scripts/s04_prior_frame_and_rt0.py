#!/usr/bin/env python3
"""rt07_g3 step 4 - the prior RT0-RT7 frame, carried onto shared residues, and the RT0 audit.

The prior frame table carries its own LtrA residue coordinates, so its blocks can be compared
with the independently reconstructed g2 regions WITHOUT going through an HMM at all. That
makes two independent correspondence routes - the match-state route of step 3 and this direct
one - and the two can disagree, which is worth knowing.

The RT0 audit asks the question the launcher insists on: not "does the prior RT0 number
replicate", but WHAT REGION the prior method called RT0. The prior work measured occupancy of
its N-terminal blocks. Whether those blocks contain the historically relevant RT0 landmark is
a separate, checkable fact, and it decides whether the prior number is an RT0 number at all.

Writes: tables/g3_prior_frame_correspondence.tsv, tables/g3_rt0_object_audit.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g3lib import V4, g2_blocks, jaccard, read_tsv, write_tsv  # noqa: E402

PRIOR_FRAME = V4 / "rt0_rt7_domain_test/tables/rt0_rt7_frame.tsv"
# Blocker 2005's LtrA landmarks, from rt07_g1 (assignment B02) - used to TEST, never to define.
BLOCKER_RT0_SPAN = (1, 85)
BLOCKER_RT0_ALANINE = 39


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T = args.out

    blocks = [(int(b["block_index"]), int(b["ltra_start_residue"]), int(b["ltra_end_residue"]),
               b["contains_catalytic_yxdd"], b["blocker_zone"])
              for b in g2_blocks()
              if b["ltra_start_residue"].isdigit() and b["ltra_end_residue"].isdigit()]

    if not PRIOR_FRAME.is_file():
        write_tsv(T / "g3_prior_frame_correspondence.tsv",
                  ["state"], [{"state": f"PRIOR_FRAME_ABSENT: {PRIOR_FRAME}"}])
        return 1

    rows, prior_rows = [], read_tsv(PRIOR_FRAME)
    for r in prior_rows:
        try:
            ps, pe = int(r["LtrA_P0A3U0_start"]), int(r["LtrA_P0A3U0_end"])
        except ValueError:
            rows.append({
                "prior_block": r["block"], "rt_interval": r["rt_interval"],
                "derivation": r["derivation"], "ltra_start": r["LtrA_P0A3U0_start"],
                "ltra_end": r["LtrA_P0A3U0_end"], "best_g2_block": "",
                "jaccard_on_ltra_residues": "", "n_g2_blocks_overlapping": "",
                "correspondence": "NOT_TESTABLE - the prior row has no usable LtrA coordinate",
                "fixed_by_published_motif": "", "mean_occupancy": r.get("mean_occupancy", ""),
                "consensus": r.get("consensus", ""),
                "unit": "prior frame block", "frame": "LtrA P0A3U0 residue numbering",
                "denominator": f"{len(prior_rows)} prior frame blocks"})
            continue
        best, best_j, overlapping = None, 0.0, []
        for idx, bs, be, yx, zone in blocks:
            j = jaccard((ps, pe), (bs, be))
            if j > best_j:
                best, best_j = idx, j
            if not (be < ps or bs > pe):
                overlapping.append(idx)
        rows.append({
            "prior_block": r["block"], "rt_interval": r["rt_interval"],
            "derivation": r["derivation"], "ltra_start": ps, "ltra_end": pe,
            "best_g2_block": best if best else "NONE",
            "jaccard_on_ltra_residues": f"{best_j:.3f}",
            "n_g2_blocks_overlapping": len(overlapping),
            "correspondence": ("INSIDE_A_G2_REGION" if overlapping else
                               "IN_A_GAP_BETWEEN_G2_REGIONS"),
            "fixed_by_published_motif": ("YES" if r["derivation"].startswith("published")
                                         else "NO - order_interpolated"),
            "mean_occupancy": r.get("mean_occupancy", ""),
            "consensus": r.get("consensus", ""),
            "unit": "prior frame block mapped onto shared LtrA residues",
            "frame": "LtrA P0A3U0 residue numbering",
            "denominator": f"{len(prior_rows)} prior frame blocks"})
    write_tsv(T / "g3_prior_frame_correspondence.tsv",
              ["prior_block", "rt_interval", "derivation", "ltra_start", "ltra_end",
               "best_g2_block", "jaccard_on_ltra_residues", "n_g2_blocks_overlapping",
               "correspondence", "fixed_by_published_motif", "mean_occupancy", "consensus",
               "unit", "frame", "denominator"], rows)

    # ---------------- the RT0 object audit ----------------
    mapped = [r for r in rows if isinstance(r["ltra_start"], int)]
    frame_lo = min(r["ltra_start"] for r in mapped)
    frame_hi = max(r["ltra_end"] for r in mapped)
    nterm_blocks = [r for r in mapped if r["rt_interval"] == "RT0-RT1"]
    nterm_lo = min((r["ltra_start"] for r in nterm_blocks), default=None)
    nterm_hi = max((r["ltra_end"] for r in nterm_blocks), default=None)
    covers_alanine = [r for r in mapped
                      if r["ltra_start"] <= BLOCKER_RT0_ALANINE <= r["ltra_end"]]
    g2_covers_alanine = [idx for idx, bs, be, _, _ in blocks
                         if bs <= BLOCKER_RT0_ALANINE <= be]
    fixed = sum(1 for r in mapped if r["fixed_by_published_motif"] == "YES")

    audit = [
        ("prior_frame_ltra_extent", f"{frame_lo}-{frame_hi}",
         "the whole prior RT0-RT7 frame, in LtrA residues"),
        ("prior_blocks_total", len(prior_rows), "blocks in the prior frame table"),
        ("prior_blocks_fixed_by_published_motif", fixed,
         "blocks whose position is anchored to a published motif rather than interpolated"),
        ("prior_blocks_order_interpolated", len(mapped) - fixed,
         "blocks placed by interpolating the order between anchored blocks"),
        ("prior_block_named_RT0", "NONE",
         "there is no block named RT0 in the prior frame; the N-terminal interval is named "
         "RT0-RT1"),
        ("prior_RT0_proximal_blocks_ltra_extent",
         f"{nterm_lo}-{nterm_hi}" if nterm_lo else "n/a",
         "the region whose occupancy the prior work reported as the RT0 result"),
        ("prior_RT0_proximal_blocks_all_interpolated",
         "YES" if all(r["fixed_by_published_motif"].startswith("NO") for r in nterm_blocks)
         else "NO",
         "whether any published motif fixes the region the RT0 number was measured on"),
        ("blocker_rt0_span_ltra", f"{BLOCKER_RT0_SPAN[0]}-{BLOCKER_RT0_SPAN[1]}",
         "the LtrA region Blocker 2005 assigns to RT0, from rt07_g1 assignment B02"),
        ("blocker_rt0_conserved_alanine_ltra", BLOCKER_RT0_ALANINE,
         "the conserved RT0 alanine, the single most specific RT0 landmark available"),
        ("prior_frame_covers_that_alanine",
         "YES" if covers_alanine else "NO",
         "whether the region the prior RT0 number was measured on contains the RT0 landmark"),
        ("prior_frame_starts_n_residues_after_the_alanine",
         frame_lo - BLOCKER_RT0_ALANINE,
         "how far the prior frame begins downstream of the RT0 landmark"),
        ("g2_region_covering_that_alanine",
         ",".join(map(str, g2_covers_alanine)) or "NONE",
         "whether the independently reconstructed g2 regions cover the RT0 landmark"),
        ("object_verdict",
         "OBJECT_MISMATCH" if (not covers_alanine and g2_covers_alanine) else
         "OBJECTS_AGREE" if covers_alanine else "NOT_TESTABLE",
         "the prior RT0 number and the historically relevant RT0 region are different objects "
         "if the prior frame excludes the landmark that the independent reconstruction covers"),
        ("rt0_scope_limit_carried",
         "U01 remains open; the defining cross-class claim was NOT_TESTABLE_ON_SUBSTRATE in g2",
         "RT0's defining source (Malik et al. 1999) is still unheld, and a group II intron "
         "alignment cannot test a claim about what RT0 is NOT conserved in"),
    ]
    write_tsv(T / "g3_rt0_object_audit.tsv",
              ["quantity", "value", "what_it_means", "unit", "frame", "denominator"],
              [{"quantity": q, "value": v, "what_it_means": w,
                "unit": "RT0 audit quantity",
                "frame": "LtrA P0A3U0 residue numbering",
                "denominator": "n/a - object audit, not a rate"} for q, v, w in audit])

    inside = sum(1 for r in rows if r["correspondence"] == "INSIDE_A_G2_REGION")
    print(f"prior frame blocks mapped: {len(mapped)}/{len(prior_rows)}; "
          f"{inside} fall inside a g2 region, {len(mapped) - inside} in gaps")
    print(f"prior blocks fixed by a published motif: {fixed}/{len(mapped)}")
    print(f"prior frame extent LtrA {frame_lo}-{frame_hi}; Blocker RT0 alanine "
          f"{BLOCKER_RT0_ALANINE} covered by prior frame: {'YES' if covers_alanine else 'NO'}; "
          f"by g2 region(s): {g2_covers_alanine or 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
