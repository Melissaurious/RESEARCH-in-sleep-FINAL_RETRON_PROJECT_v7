#!/usr/bin/env python3
"""rt07_g2 step 5 - does the reconstruction depend on Zimmerly's alignment?

Everything so far is measured on ALIGN_000044, which is one alignment of these 66 proteins,
built in 2000 with PILEUP, CLUSTALX and a manual step that cannot be rerun. If the recovered
landmarks are properties of the protein family they should survive re-aligning the same
ungapped sequences independently; if they are properties of that one alignment, they will
not. This is the frame-independence check the reconstruction owes itself.

MAFFT is run deterministically (FFT-NS-2, one thread, no iterative refinement) so the second
frame is reproducible. The same criterion, the same declared sweep, the same reporting rule
are then applied unchanged - the point is to vary the alignment, not the method.

Writes: tables/g2_second_frame.tsv (and, under --work, the MAFFT alignment)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g2lib import (blocks_from, col_to_residue, conserved_columns, control,  # noqa: E402
                       read_tsv, sha256, write_tsv)

GROUPS = ["mitochondrial", "bacterial", "algal_chloroplast", "euglenoid"]
LTRA = "L.l."


def read_fasta(p: Path) -> dict[str, str]:
    out, name, buf = {}, None, []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith(">"):
            if name:
                out[name] = "".join(buf)
            name, buf = line[1:].split()[0], []
        else:
            buf.append(line.strip())
    if name:
        out[name] = "".join(buf)
    return out


def widest_plateau(counts: dict[int, int]) -> tuple[int, int, int]:
    best, gaps, i = (0, 0, 0), sorted(counts), 0
    while i < len(gaps):
        j = i
        while j + 1 < len(gaps) and counts[gaps[j + 1]] == counts[gaps[i]]:
            j += 1
        if j - i + 1 > best[1]:
            best = (gaps[(i + j) // 2], j - i + 1, counts[gaps[i]])
        i = j + 1
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T = args.out

    P = {r["parameter"]: r["value"] for r in control("reconstruction_parameters.tsv")}
    gap_lo, gap_hi = (int(x) for x in P["block_gap_sweep"].split(".."))
    thr = float(P["group_threshold_fraction"])
    min_groups = int(P["min_groups_satisfied"])

    faa = args.work / "reference_set.faa"
    out_aln = args.work / "second_frame_mafft.afa"
    ver = subprocess.run(["mafft", "--version"], capture_output=True, text=True)
    cmd = ["mafft", "--retree", "2", "--maxiterate", "0", "--thread", "1",
           "--anysymbol", "--quiet", str(faa)]
    with out_aln.open("w") as fh:
        subprocess.run(cmd, check=True, stdout=fh)

    landed = T.parent / "reference"
    landed.mkdir(parents=True, exist_ok=True)
    (landed / "g2_second_frame_mafft.afa").write_text(
        out_aln.read_text(encoding="utf-8"), encoding="utf-8")

    seqs = read_fasta(out_aln)
    groups = {r["sequence_id"]: r["lineage_group"]
              for r in read_tsv(T / "g2_reference_sequence_set.tsv")}
    seqs = {k: v.upper() for k, v in seqs.items() if k in groups}
    width = len(next(iter(seqs.values())))

    ltra_map = col_to_residue(seqs[LTRA])
    ung = seqs[LTRA].replace("-", "")

    # The two frames must cover the SAME region or the comparison is between a window and a
    # whole protein. The stated RT domain (ALIGN_000044 columns 261-886) is carried across by
    # its LtrA residues, which both alignments contain: columns -> residues in frame one,
    # residues -> columns in frame two.
    from rt07g2lib import ACQUIRED, parse_clustal
    first_seqs = parse_clustal(ACQUIRED / "ALIGN_000044.aln")
    first_map = col_to_residue(first_seqs[LTRA])
    lo1, hi1 = (int(x) for x in P["rt_domain_columns"].split("-"))
    res_lo = min((r for c, r in first_map.items() if c >= lo1), default=1)
    res_hi = max((r for c, r in first_map.items() if c <= hi1), default=len(ung))
    second_map = {r: c for c, r in ltra_map.items()}
    lo2 = min(second_map[r] for r in second_map if r >= res_lo)
    hi2 = max(second_map[r] for r in second_map if r <= res_hi)

    cons = [r["column"] for r in
            conserved_columns(seqs, groups, threshold=thr, min_groups=min_groups,
                              similarity=False, group_names=GROUPS)
            if r["conserved"] and lo2 <= r["column"] <= hi2]
    counts = {g: len(blocks_from(cons, g, 2)) for g in range(gap_lo, gap_hi + 1)}
    chosen_gap, plateau, n_blocks = widest_plateau(counts)
    blocks = blocks_from(cons, chosen_gap, 2)

    yxdd_col = next((c for c in ltra_map
                     if re.match(r"[YF].DD", ung[ltra_map[c] - 1:ltra_map[c] + 3])), None)
    yxdd_block = next((i for i, (s, e, _) in enumerate(blocks, 1)
                       if yxdd_col and s <= yxdd_col <= e), None)
    gaps = [(blocks[i + 1][0] - blocks[i][1] - 1, f"{i + 1}/{i + 2}")
            for i in range(len(blocks) - 1)]
    widest = max(gaps)[1] if gaps else "n/a"

    # Land the second frame's own blocks with their LtrA coordinates, so the two frames can
    # be compared on a shared coordinate system rather than on raw block indices.
    second_rows = []
    for i, (bs, be, bn) in enumerate(blocks, start=1):
        rs = ltra_map.get(bs) or min((r for c, r in ltra_map.items() if c >= bs), default="n/a")
        re_ = ltra_map.get(be) or max((r for c, r in ltra_map.items() if c <= be), default="n/a")
        zone = ("RT0_ZONE (LtrA M1-R85)" if isinstance(re_, int) and re_ <= 85
                else "SPANS_RT0_AND_RT1_7_ZONES" if isinstance(rs, int) and rs <= 85
                else "RT1_7_ZONE (LtrA R86-R364)")
        second_rows.append({
            "block_index": i, "start_column": bs, "end_column": be,
            "ltra_start_residue": rs, "ltra_end_residue": re_,
            "n_conserved_positions": bn,
            "contains_catalytic_yxdd": "YES" if i == yxdd_block else "NO",
            "blocker_zone": zone,
            "unit": "reconstructed block in the MAFFT frame",
            "frame": "MAFFT FFT-NS-2 re-alignment of the same 66 proteins",
            "denominator": f"{len(blocks)} blocks in the second frame"})
    write_tsv(T / "g2_second_frame_blocks.tsv",
              ["block_index", "start_column", "end_column", "ltra_start_residue",
               "ltra_end_residue", "n_conserved_positions", "contains_catalytic_yxdd",
               "blocker_zone", "unit", "frame", "denominator"], second_rows)
    second_rt0 = sum(1 for r in second_rows if r["blocker_zone"].startswith("RT0_ZONE"))
    second_yxdd_norm = (yxdd_block - second_rt0) if yxdd_block else None

    first = read_tsv(T / "g2_reconstructed_blocks.tsv")
    first_n = len(first)
    first_yxdd = next((int(m["block_index"]) for m in read_tsv(T / "g2_ltra_mapping.tsv")
                       if m["contains_catalytic_yxdd"] == "YES"), None)
    first_widest = next((s["between_blocks"] for s in
                         read_tsv(T / "g2_interblock_spacers.tsv")
                         if s["is_widest_gap"] == "YES"), "n/a")
    first_map_rows = read_tsv(T / "g2_ltra_mapping.tsv")
    first_rt0 = sum(1 for r in first_map_rows if r["blocker_zone"].startswith("RT0_ZONE"))
    first_yxdd_norm = (first_yxdd - first_rt0) if first_yxdd else None
    first_cons = sum(1 for r in read_tsv(T / "g2_conserved_positions.tsv")
                     if r["conserved_strict"] == "YES" and r["in_rt_domain"] == "YES")

    rows = [
        ("alignment_columns", first["0"] if False else
         read_tsv(T / "g2_substrate_identity.tsv")[2]["value"], width,
         "n/a - different alignments have different widths"),
        ("conserved_positions", first_cons, len(cons),
         "AGREE_IN_MAGNITUDE" if abs(first_cons - len(cons)) <= 0.5 * first_cons
         else "DIFFER"),
        ("blocks_at_reported_point", first_n, n_blocks,
         "AGREE" if first_n == n_blocks else "DIFFER"),
        ("block_containing_catalytic_YxDD", first_yxdd, yxdd_block,
         "AGREE" if first_yxdd == yxdd_block else "DIFFER"),
        ("widest_interblock_gap", first_widest, widest,
         "AGREE" if first_widest == widest else "DIFFER"),
        ("blocks_in_RT0_zone", first_rt0, second_rt0,
         "AGREE" if first_rt0 == second_rt0 else "DIFFER"),
        ("blocks_C_terminal_to_the_RT0_zone", first_n - first_rt0, n_blocks - second_rt0,
         "AGREE" if (first_n - first_rt0) == (n_blocks - second_rt0) else "DIFFER"),
        ("YxDD_block_index_excluding_RT0_zone_blocks", first_yxdd_norm, second_yxdd_norm,
         "AGREE" if first_yxdd_norm == second_yxdd_norm else "DIFFER"),
        ("seven_blocks_recovered", "NO" if first_n != 7 else "YES",
         "NO" if n_blocks != 7 else "YES",
         "AGREE" if (first_n == 7) == (n_blocks == 7) else "DIFFER"),
    ]
    write_tsv(T / "g2_second_frame.tsv",
              ["property", "frame_align000044", "frame_mafft_fftns2", "verdict",
               "second_frame_tool", "second_frame_sha256", "unit", "frame", "denominator"],
              [{"property": k, "frame_align000044": a, "frame_mafft_fftns2": b,
                "verdict": v,
                "second_frame_tool": (ver.stdout or ver.stderr).strip().splitlines()[0],
                "second_frame_sha256": sha256(out_aln),
                "unit": "reconstruction property",
                "frame": "same 66 ungapped proteins, independently re-aligned; both "
                         "frames restricted to the same LtrA residue window",
                "denominator": "9 properties compared across two alignment frames"}
               for k, a, b, v in rows])

    # Block indices are a blunt comparison: two frames can place the same conserved regions
    # and still disagree on whether one region is one block or two. The correspondence is
    # therefore measured on shared LtrA residues, where 'DIFFER' on a count and 'AGREE' on a
    # position are no longer forced into the same verdict.
    corr = []
    for a in first_map_rows:
        try:
            a_lo, a_hi = int(a["ltra_start_residue"]), int(a["ltra_end_residue"])
        except ValueError:
            continue
        a_set = set(range(a_lo, a_hi + 1))
        best, best_j = None, 0.0
        for b in second_rows:
            if not isinstance(b["ltra_start_residue"], int):
                continue
            b_set = set(range(b["ltra_start_residue"], b["ltra_end_residue"] + 1))
            j = len(a_set & b_set) / len(a_set | b_set) if a_set | b_set else 0.0
            if j > best_j:
                best, best_j = b, j
        overlaps = [b["block_index"] for b in second_rows
                    if isinstance(b["ltra_start_residue"], int)
                    and not (b["ltra_end_residue"] < a_lo or b["ltra_start_residue"] > a_hi)]
        corr.append({
            "frame1_block": a["block_index"],
            "frame1_ltra_span": f"{a_lo}-{a_hi}",
            "frame2_best_match_block": best["block_index"] if best else "NONE",
            "frame2_ltra_span": (f"{best['ltra_start_residue']}-{best['ltra_end_residue']}"
                                 if best else "NONE"),
            "jaccard_on_ltra_residues": f"{best_j:.3f}",
            "n_frame2_blocks_overlapping": len(overlaps),
            "correspondence": ("ONE_TO_ONE" if len(overlaps) == 1 else
                               f"SPLIT_INTO_{len(overlaps)}" if len(overlaps) > 1
                               else "NO_COUNTERPART"),
            "unit": "reconstructed block, matched across two alignment frames",
            "frame": "LtrA residue coordinates, shared by both frames",
            "denominator": f"{len(first_map_rows)} blocks in frame 1 vs {len(second_rows)} "
                           f"in frame 2"})
    write_tsv(T / "g2_frame_correspondence.tsv",
              ["frame1_block", "frame1_ltra_span", "frame2_best_match_block",
               "frame2_ltra_span", "jaccard_on_ltra_residues", "n_frame2_blocks_overlapping",
               "correspondence", "unit", "frame", "denominator"], corr)
    one_to_one = sum(1 for c in corr if c["correspondence"] == "ONE_TO_ONE")
    med_j = sorted(float(c["jaccard_on_ltra_residues"]) for c in corr)[len(corr) // 2]
    print(f"  cross-frame correspondence: {one_to_one}/{len(corr)} one-to-one, "
          f"median Jaccard {med_j:.2f} on LtrA residues")

    agree = sum(1 for _, _, _, v in rows if v.startswith("AGREE"))
    print(f"  comparable window: LtrA residues {res_lo}-{res_hi} -> MAFFT columns "
          f"{lo2}-{hi2}")
    print(f"second frame: MAFFT {width} columns, {len(cons)} conserved positions, "
          f"{n_blocks} blocks at gap {chosen_gap} (plateau {plateau})")
    print(f"  catalytic motif in block {yxdd_block}; widest gap {widest}")
    print(f"  {agree}/{len(rows)} properties agree across frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
