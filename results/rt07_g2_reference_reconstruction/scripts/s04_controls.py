#!/usr/bin/env python3
"""rt07_g2 step 4 - the controls that decide whether the reconstruction means anything.

A reconstruction that would have produced blocks from any protein alignment has recovered
nothing. Four controls, all declared before the observed values were known:

  C1 POSITIVE   the catalytic Y/FxDD column must be called conserved by the criterion.
                It is the one landmark every derivational source agrees on; a criterion that
                misses it is not implementing the criterion.
  C2 POSITIVE   the block containing Y/FxDD must be the fifth, as Zimmerly 2001 states.
                This is what numbers the blocks without importing a modern boundary.
  C3 NULL       residues shuffled within each sequence destroy column identity. The number
                of conserved positions must collapse. This prices the conserved count.
  C4 NULL       columns permuted destroy adjacency while preserving each column's own
                conservation. The block count must rise. This prices the CLUSTERING - the
                claim that conserved positions fall into compact blocks at all.

--seed-bad sets the group threshold to 0, which calls every column conserved. The null
controls must then FAIL; run.sh asserts exactly that. A control that cannot fail is
decoration.

Writes: tables/g2_positive_controls.tsv, tables/g2_null_model.tsv
"""
from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g2lib import (ACQUIRED, blocks_from, col_to_residue, conserved_columns,  # noqa: E402
                       control, parse_clustal, read_tsv, write_tsv)

GROUPS = ["mitochondrial", "bacterial", "algal_chloroplast", "euglenoid"]
LTRA = "L.l."
SEED = 20260915


def conserved_count(seqs, groups, thr, min_groups, lo, hi) -> list[int]:
    rows = conserved_columns(seqs, groups, threshold=thr, min_groups=min_groups,
                             similarity=False, group_names=GROUPS)
    return [r["column"] for r in rows if r["conserved"] and lo <= r["column"] <= hi]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed-bad", action="store_true")
    args = ap.parse_args()
    T = args.out

    P = {r["parameter"]: r["value"] for r in control("reconstruction_parameters.tsv")}
    lo, hi = (int(x) for x in P["rt_domain_columns"].split("-"))
    thr = 0.0 if args.seed_bad else float(P["group_threshold_fraction"])
    min_groups = int(P["min_groups_satisfied"])
    n_rep = int(re.search(r"(\d+) replicates", P["null_model"]).group(1))

    seqs = parse_clustal(ACQUIRED / "ALIGN_000044.aln")
    refset = read_tsv(T / "g2_reference_sequence_set.tsv")
    groups = {r["sequence_id"]: r["lineage_group"] for r in refset}
    seqs = {k: v for k, v in seqs.items() if k in groups}
    blocks = [(int(r["start_column"]), int(r["end_column"]))
              for r in read_tsv(T / "g2_reconstructed_blocks.tsv")]
    gap = int(read_tsv(T / "g2_reconstructed_blocks.tsv")[0]["reported_at_max_gap"])

    obs_cols = conserved_count(seqs, groups, thr, min_groups, lo, hi)
    obs_blocks = blocks_from(obs_cols, gap, 2)

    ltra_map = col_to_residue(seqs[LTRA])
    ung = seqs[LTRA].replace("-", "")
    yxdd_col = next((c for c in ltra_map
                     if re.match(r"[YF].DD", ung[ltra_map[c] - 1:ltra_map[c] + 3])), None)
    yxdd_conserved = yxdd_col in obs_cols
    yxdd_block = next((i for i, (s, e) in enumerate(blocks, 1)
                       if yxdd_col and s <= yxdd_col <= e), None)

    # ---------------- null models ----------------
    rng = random.Random(SEED)
    null_shuffled, null_permuted = [], []
    names = list(seqs)
    for _ in range(n_rep):
        shuf = {}
        for n in names:
            chars = list(seqs[n])
            rng.shuffle(chars)
            shuf[n] = "".join(chars)
        null_shuffled.append(len(conserved_count(shuf, groups, thr, min_groups, lo, hi)))

        order = list(range(len(seqs[names[0]])))
        rng.shuffle(order)
        perm = {n: "".join(seqs[n][i] for i in order) for n in names}
        cols = conserved_count(perm, groups, thr, min_groups, lo, hi)
        null_permuted.append(len(blocks_from(cols, gap, 2)))

    p_cons = (sum(1 for v in null_shuffled if v >= len(obs_cols)) + 1) / (n_rep + 1)
    p_block = (sum(1 for v in null_permuted if v <= len(obs_blocks)) + 1) / (n_rep + 1)

    controls = [
        {"control": "C1:catalytic_YxDD_column_is_conserved", "kind": "POSITIVE",
         "expected": "YES - the one landmark every derivational source shares",
         "observed": f"{'YES' if yxdd_conserved else 'NO'} (column {yxdd_col}, LtrA residue "
                     f"{ltra_map.get(yxdd_col)})",
         "result": "PASS" if yxdd_conserved else "FAIL"},
        {"control": "C2:YxDD_block_is_the_fifth", "kind": "POSITIVE",
         "expected": "5 - Zimmerly 2001 places the catalytic motif in subdomain 5",
         "observed": f"block {yxdd_block} of {len(blocks)}",
         "result": "PASS" if yxdd_block == 5 else "FAIL"},
        {"control": "C3:conserved_positions_collapse_under_residue_shuffling", "kind": "NULL",
         "expected": f"far fewer than the observed {len(obs_cols)} conserved columns",
         "observed": f"null max {max(null_shuffled)}, mean "
                     f"{sum(null_shuffled) / len(null_shuffled):.1f}, empirical p={p_cons:.4f}",
         "result": "PASS" if p_cons < 0.05 else "FAIL"},
        {"control": "C4:block_clustering_beats_column_permutation", "kind": "NULL",
         "expected": f"more than the observed {len(obs_blocks)} blocks once adjacency is "
                     f"destroyed",
         "observed": f"null min {min(null_permuted)}, mean "
                     f"{sum(null_permuted) / len(null_permuted):.1f}, empirical p={p_block:.4f}",
         "result": "PASS" if p_block < 0.05 else "FAIL"},
    ]
    for c in controls:
        c.update({"unit": "control", "denominator": f"4 controls declared; {n_rep} null "
                                                    f"replicates, seed {SEED}"})
    write_tsv(T / "g2_positive_controls.tsv",
              ["control", "kind", "expected", "observed", "result", "unit", "denominator"],
              controls)

    write_tsv(T / "g2_null_model.tsv",
              ["null_model", "statistic", "observed", "null_mean", "null_min", "null_max",
               "empirical_p", "verdict", "unit", "denominator"],
              [{"null_model": "residue shuffling within each sequence",
                "statistic": "conserved columns in the RT domain",
                "observed": len(obs_cols),
                "null_mean": f"{sum(null_shuffled) / len(null_shuffled):.2f}",
                "null_min": min(null_shuffled), "null_max": max(null_shuffled),
                "empirical_p": f"{p_cons:.4f}",
                "verdict": "conservation is not a compositional artefact"
                           if p_cons < 0.05 else "NOT SEPARABLE FROM THE NULL",
                "unit": "alignment column", "denominator": f"{n_rep} replicates"},
               {"null_model": "column permutation (conservation kept, adjacency destroyed)",
                "statistic": "blocks at the reported parameters",
                "observed": len(obs_blocks),
                "null_mean": f"{sum(null_permuted) / len(null_permuted):.2f}",
                "null_min": min(null_permuted), "null_max": max(null_permuted),
                "empirical_p": f"{p_block:.4f}",
                "verdict": "conserved positions genuinely cluster into blocks"
                           if p_block < 0.05 else "NOT SEPARABLE FROM THE NULL",
                "unit": "block", "denominator": f"{n_rep} replicates"}])

    # ---------------- POST-HOC diagnostic, landed as such ----------------
    # C4 tests block COUNT at one permissive gap. When it fails, the question it leaves open
    # is whether conserved positions cluster at ANY gap, so the same null is re-run across
    # the whole declared sweep. This is post-hoc: it is a diagnostic, not a second chance for
    # the declared control, and it is labelled that way in the landed table.
    gap_lo, gap_hi = (int(x) for x in P["block_gap_sweep"].split(".."))
    by_gap = []
    rng2 = random.Random(SEED + 1)
    perms = []
    for _ in range(n_rep):
        order = list(range(len(seqs[names[0]])))
        rng2.shuffle(order)
        perms.append(conserved_count({n: "".join(seqs[n][i] for i in order) for n in names},
                                     groups, thr, min_groups, lo, hi))
    for g in range(gap_lo, gap_hi + 1):
        o = len(blocks_from(obs_cols, g, 2))
        nulls = [len(blocks_from(c, g, 2)) for c in perms]
        p_g = (sum(1 for v in nulls if v <= o) + 1) / (n_rep + 1)
        by_gap.append({
            "max_gap": g, "observed_blocks": o,
            "null_mean_blocks": f"{sum(nulls) / len(nulls):.2f}",
            "null_min_blocks": min(nulls), "null_max_blocks": max(nulls),
            "empirical_p_observed_fewer_or_equal": f"{p_g:.4f}",
            "separates_from_null": "YES" if p_g < 0.05 else "NO",
            "status": "POST_HOC_DIAGNOSTIC - not a declared control",
            "unit": "block", "denominator": f"{n_rep} column-permutation replicates"})
    write_tsv(T / "g2_null_by_gap.tsv",
              ["max_gap", "observed_blocks", "null_mean_blocks", "null_min_blocks",
               "null_max_blocks", "empirical_p_observed_fewer_or_equal",
               "separates_from_null", "status", "unit", "denominator"], by_gap)
    # Block COUNT may simply be a blunt statistic. Two sharper spatial statistics are run
    # against the same null: the largest gap between consecutive conserved positions (a real
    # spacer should produce one much larger than chance), and the coefficient of variation of
    # those gaps (clumping makes gaps uneven). Post-hoc, and labelled.
    def spatial(cols: list[int]) -> tuple[int, float]:
        d = [b - a for a, b in zip(cols, cols[1:])]
        if len(d) < 2:
            return 0, 0.0
        mean = sum(d) / len(d)
        var = sum((x - mean) ** 2 for x in d) / len(d)
        return max(d), (var ** 0.5) / mean if mean else 0.0

    obs_max, obs_cv = spatial(obs_cols)
    null_stats = [spatial(c) for c in perms]
    p_max = (sum(1 for m, _ in null_stats if m >= obs_max) + 1) / (n_rep + 1)
    p_cv = (sum(1 for _, c in null_stats if c >= obs_cv) + 1) / (n_rep + 1)
    write_tsv(T / "g2_null_spatial_statistics.tsv",
              ["statistic", "observed", "null_mean", "null_max", "empirical_p",
               "separates_from_null", "status", "interpretation", "unit", "denominator"],
              [{"statistic": "largest gap between consecutive conserved positions",
                "observed": obs_max,
                "null_mean": f"{sum(m for m, _ in null_stats) / n_rep:.1f}",
                "null_max": max(m for m, _ in null_stats),
                "empirical_p": f"{p_max:.4f}",
                "separates_from_null": "YES" if p_max < 0.05 else "NO",
                "status": "POST_HOC_DIAGNOSTIC",
                "interpretation": "a genuine spacer should leave a gap larger than chance",
                "unit": "alignment columns", "denominator": f"{n_rep} replicates"},
               {"statistic": "coefficient of variation of inter-position gaps",
                "observed": f"{obs_cv:.3f}",
                "null_mean": f"{sum(c for _, c in null_stats) / n_rep:.3f}",
                "null_max": f"{max(c for _, c in null_stats):.3f}",
                "empirical_p": f"{p_cv:.4f}",
                "separates_from_null": "YES" if p_cv < 0.05 else "NO",
                "status": "POST_HOC_DIAGNOSTIC",
                "interpretation": "clumping makes the spacing of conserved positions uneven",
                "unit": "dimensionless", "denominator": f"{n_rep} replicates"}])
    print(f"  post-hoc spatial: largest gap obs={obs_max} p={p_max:.4f}; "
          f"gap CV obs={obs_cv:.3f} p={p_cv:.4f}")

    sep = [r["max_gap"] for r in by_gap if r["separates_from_null"] == "YES"]
    print(f"  post-hoc: observed clustering separates from the null at gap(s) "
          f"{sep if sep else 'NONE'} of {gap_lo}..{gap_hi}")

    failed = [c for c in controls if c["result"] != "PASS"]
    for c in controls:
        print(f"  {c['result']:<4} {c['control']}: {c['observed']}")
    if args.seed_bad:
        print("seed-bad mode: the null controls SHOULD have failed")
        return 0 if any(c["kind"] == "NULL" and c["result"] == "FAIL" for c in controls) else 1
    # A failing control is a RESULT, not a crash: C4 fails on this substrate and that failure
    # is the most important line in the bundle. It is landed in g2_positive_controls.tsv and
    # carried into the report and the kill-criterion assessment. Reproduction is what guards
    # it - if a rerun ever flipped C4 to PASS, run.sh's byte comparison would fail on that
    # table. Exiting non-zero here would instead abort the rerun before the finding is landed.
    if failed:
        print(f"NOTE: {len(failed)} declared control(s) FAILED. This is landed as a result; "
              f"see tables/g2_positive_controls.tsv and tables/g2_kill_criterion.tsv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
