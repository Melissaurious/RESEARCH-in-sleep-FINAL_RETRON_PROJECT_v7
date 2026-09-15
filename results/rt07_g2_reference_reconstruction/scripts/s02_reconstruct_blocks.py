#!/usr/bin/env python3
"""rt07_g2 step 2 - reconstruct the numbered blocks by the founding paper's own criterion.

The procedure, declared in control/reconstruction_parameters.tsv before anything was
counted:

  1. a position is CONSERVED when, in at least 3 of the 4 lineage groups, more than 50% of
     that group's sequences carry the group's modal residue (gaps count against);
  2. conserved positions are merged into BLOCKS when separated by no more than `max_gap`
     columns, keeping blocks of at least `min_size` conserved positions;
  3. both free parameters are swept over their whole declared range and the entire surface
     is landed;
  4. the reported point is the midpoint of the widest plateau in block count - a rule about
     stability, chosen before any block was counted, and deliberately not a rule that says
     'take the parameters that give seven'.

Modern RT1-RT7 boundaries are never consulted. Nothing here reads a comparator. RT0 is not
reconstructed as a block: the N-terminal region is measured separately in step 3, because
the claim that defines RT0 is a cross-class claim this single-class substrate cannot test.

Writes: tables/g2_conserved_positions.tsv, tables/g2_parameter_sweep.tsv,
        tables/g2_reconstructed_blocks.tsv, tables/g2_block_uncertainty.tsv
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g2lib import (ACQUIRED, blocks_from, conserved_columns, control,  # noqa: E402
                       parse_clustal, read_tsv, write_tsv)

GROUPS = ["mitochondrial", "bacterial", "algal_chloroplast", "euglenoid"]


def params() -> dict[str, str]:
    return {r["parameter"]: r["value"] for r in control("reconstruction_parameters.tsv")}


def widest_plateau(counts: dict[int, int]) -> tuple[int, int, int]:
    """(chosen gap, plateau width, block count) for the widest run of equal counts.

    Ties are broken toward the plateau that occurs at the smaller gap, so the rule is
    deterministic and cannot be steered by reordering the sweep.
    """
    best = (0, 0, 0)
    gaps = sorted(counts)
    i = 0
    while i < len(gaps):
        j = i
        while j + 1 < len(gaps) and counts[gaps[j + 1]] == counts[gaps[i]]:
            j += 1
        width = j - i + 1
        if width > best[1]:
            best = (gaps[(i + j) // 2], width, counts[gaps[i]])
        i = j + 1
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--alignment", type=Path, default=None,
                    help="override substrate (used by the second-frame and null routes)")
    ap.add_argument("--tag", default="align000044")
    args = ap.parse_args()

    P = params()
    lo, hi = (int(x) for x in P["rt_domain_columns"].split("-"))
    gap_lo, gap_hi = (int(x) for x in P["block_gap_sweep"].split(".."))
    size_lo, size_hi = (int(x) for x in
                        P["block_min_conserved_positions_sweep"].split(".."))
    thr = float(P["group_threshold_fraction"])
    min_groups = int(P["min_groups_satisfied"])

    seqs = parse_clustal(args.alignment or ACQUIRED / "ALIGN_000044.aln")
    groups = {r["sequence_id"]: r["lineage_group"]
              for r in read_tsv(args.out / "g2_reference_sequence_set.tsv")}
    seqs = {k: v for k, v in seqs.items() if k in groups}

    strict = conserved_columns(seqs, groups, threshold=thr, min_groups=min_groups,
                              similarity=False, group_names=GROUPS)
    similar = conserved_columns(seqs, groups, threshold=thr, min_groups=min_groups,
                               similarity=True, group_names=GROUPS)
    sim_by_col = {r["column"]: r for r in similar}

    cons_rt = [r["column"] for r in strict if r["conserved"] and lo <= r["column"] <= hi]
    cons_all = [r["column"] for r in strict if r["conserved"]]
    sim_rt = [r["column"] for r in similar if r["conserved"] and lo <= r["column"] <= hi]

    sweep = []
    for size in range(size_lo, size_hi + 1):
        for gap in range(gap_lo, gap_hi + 1):
            b_rt = blocks_from(cons_rt, gap, size)
            b_all = blocks_from(cons_all, gap, size)
            b_sim = blocks_from(sim_rt, gap, size)
            sweep.append({
                "min_conserved_positions": size, "max_gap": gap,
                "n_blocks_rt_domain_strict": len(b_rt),
                "n_blocks_whole_alignment_strict": len(b_all),
                "n_blocks_rt_domain_similarity": len(b_sim),
                "total_block_span_columns": sum(e - s + 1 for s, e, _ in b_rt),
                "total_conserved_positions_in_blocks": sum(n for _, _, n in b_rt),
                "unit": "block", "frame": "ALIGN_000044 RT domain columns "
                                          f"{lo}-{hi}",
                "denominator": f"{len(cons_rt)} conserved columns in the RT domain",
            })
    write_tsv(args.out / (f"g2_parameter_sweep.tsv" if args.tag == "align000044"
                          else f"g2_parameter_sweep_{args.tag}.tsv"),
              ["min_conserved_positions", "max_gap", "n_blocks_rt_domain_strict",
               "n_blocks_whole_alignment_strict", "n_blocks_rt_domain_similarity",
               "total_block_span_columns", "total_conserved_positions_in_blocks",
               "unit", "frame", "denominator"], sweep)

    # ---- the declared reporting point ----
    at2 = {int(r["max_gap"]): int(r["n_blocks_rt_domain_strict"])
           for r in sweep if int(r["min_conserved_positions"]) == 2}
    chosen_gap, plateau_width, n_blocks = widest_plateau(at2)
    blocks = blocks_from(cons_rt, chosen_gap, 2)

    block_rows = []
    for i, (s, e, n) in enumerate(blocks, start=1):
        block_rows.append({
            "block_index": i, "start_column": s, "end_column": e,
            "span_columns": e - s + 1, "n_conserved_positions": n,
            "conserved_density": f"{n / (e - s + 1):.3f}",
            "reported_at_max_gap": chosen_gap, "reported_at_min_size": 2,
            "plateau_width_columns_of_gap": plateau_width,
            "selection_rule": P["reporting_point_rule"],
            "unit": "reconstructed block",
            "frame": f"ALIGN_000044 RT domain columns {lo}-{hi}",
            "denominator": f"{n_blocks} blocks recovered at the reported point",
        })
    write_tsv(args.out / (f"g2_reconstructed_blocks.tsv" if args.tag == "align000044"
                          else f"g2_reconstructed_blocks_{args.tag}.tsv"),
              ["block_index", "start_column", "end_column", "span_columns",
               "n_conserved_positions", "conserved_density", "reported_at_max_gap",
               "reported_at_min_size", "plateau_width_columns_of_gap", "selection_rule",
               "unit", "frame", "denominator"], block_rows)

    # ---- uncertainty: where each block's edges sit across the WHOLE sweep ----
    # Matching is by OVERLAP with the reported block, not by index, and every setting in the
    # declared sweep contributes - including the ones that return a different number of
    # blocks. Restricting the interval to settings that happen to agree on the count would
    # report zero uncertainty for a partition that visibly changes across the sweep, which is
    # the false precision this gate exists to avoid.
    unc = []
    for i, (bs, be, _) in enumerate(blocks):
        starts, ends, counts_n, settings = [], [], [], 0
        for size in range(size_lo, size_hi + 1):
            for gap in range(gap_lo, gap_hi + 1):
                for s2, e2, n2 in blocks_from(cons_rt, gap, size):
                    if not (e2 < bs or s2 > be):          # any overlap with the reported block
                        starts.append(s2)
                        ends.append(e2)
                        counts_n.append(n2)
                        settings += 1
        if not starts:
            continue
        unc.append({
            "block_index": i + 1,
            "reported_start_column": bs, "reported_end_column": be,
            "start_column_min": min(starts), "start_column_max": max(starts),
            "end_column_min": min(ends), "end_column_max": max(ends),
            "start_uncertainty_columns": max(starts) - min(starts),
            "end_uncertainty_columns": max(ends) - min(ends),
            "n_overlapping_blocks_across_sweep": settings,
            "n_conserved_positions_min": min(counts_n),
            "n_conserved_positions_max": max(counts_n),
            "edge_precision_claim": "INTERVAL_ONLY - the sources state a procedure and no "
                                    "residue edges, so no single-column edge is claimed",
            "unit": "reconstructed block",
            "frame": f"ALIGN_000044 RT domain columns {lo}-{hi}",
            "denominator": f"{(gap_hi - gap_lo + 1) * (size_hi - size_lo + 1)} parameter "
                           f"settings in the declared sweep",
        })
    write_tsv(args.out / (f"g2_block_uncertainty.tsv" if args.tag == "align000044"
                          else f"g2_block_uncertainty_{args.tag}.tsv"),
              ["block_index", "reported_start_column", "reported_end_column",
               "start_column_min", "start_column_max", "end_column_min",
               "end_column_max", "start_uncertainty_columns", "end_uncertainty_columns",
               "n_overlapping_blocks_across_sweep", "n_conserved_positions_min",
               "n_conserved_positions_max", "edge_precision_claim", "unit", "frame",
               "denominator"], unc)

    rows = []
    for r in strict:
        s = sim_by_col[r["column"]]
        rows.append({
            "column": r["column"],
            "in_rt_domain": "YES" if lo <= r["column"] <= hi else "NO",
            "conserved_strict": "YES" if r["conserved"] else "NO",
            "n_groups_satisfied_strict": r["n_groups_satisfied"],
            "conserved_similarity": "YES" if s["conserved"] else "NO",
            "n_groups_satisfied_similarity": s["n_groups_satisfied"],
            "per_group_fraction_strict": r["per_group_fraction"],
            "unit": "alignment column",
            "frame": "ALIGN_000044 columns, as submitted",
            "block_id_at_reported_point": next(
                (str(i) for i, (bs, be, _) in enumerate(blocks, 1)
                 if bs <= r["column"] <= be), "none"),
            "denominator": f"{len(strict)} alignment columns; "
                           f"{hi - lo + 1} inside the stated RT domain",
        })
    write_tsv(args.out / f"g2_conserved_positions.tsv" if args.tag == "align000044"
              else args.out / f"g2_conserved_positions_{args.tag}.tsv",
              ["column", "in_rt_domain", "conserved_strict", "n_groups_satisfied_strict",
               "conserved_similarity", "n_groups_satisfied_similarity",
               "per_group_fraction_strict", "block_id_at_reported_point", "unit",
               "frame", "denominator"], rows)


    hist = Counter(at2.values())
    print(f"conserved columns (strict, RT domain): {len(cons_rt)}  "
          f"(similarity reading: {len(sim_rt)})")
    print(f"reporting point: max_gap={chosen_gap} (widest plateau, width {plateau_width}), "
          f"min_size=2 -> {n_blocks} blocks")
    print("block-count distribution over the gap sweep at min_size=2:")
    for k in sorted(hist):
        print(f"  {k:>3} blocks : {hist[k]:>3} of {len(at2)} gap values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
