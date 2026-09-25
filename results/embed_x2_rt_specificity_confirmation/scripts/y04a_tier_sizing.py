#!/usr/bin/env python
"""embed_x2/y04a - size the C1-C4 counterfactual tiers BEFORE spending GPU time on them.

Pure CPU. This applies the frozen admissibility rules from COUNTERFACTUAL_RULES.md and counts
how many pairs and INDEPENDENT COMPONENTS each tier can support. It computes no likelihood,
loads no model and touches no out-of-fold prediction, so it reveals nothing about any effect.
Its only purpose is to know, in advance, which tiers can be adjudicated at all and which will
be reported UNDETERMINED under the frozen <30-component rule.

This script is the single source of the C1-C4 selection. It writes work/cf_selection.npz,
which y04_analyse.py evaluates verbatim, so the tiers that are sized here are exactly the
tiers that get scored -- they cannot drift apart.
"""
from __future__ import annotations
import argparse, collections, sys
from pathlib import Path
import numpy as np, pandas as pd

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
ROOT = TASK.parents[1]
POOLED = ROOT / "ARIS_OUTPUT" / "embed_g2_analysis" / "work" / "rt_pooled.npy"
K, M, MIN_COMP, SEED = 5, 8, 30, 20260918


def main() -> int:
    ap = argparse.ArgumentParser()
    # The four tiers are independent, so they are run as separate processes and their
    # per-tier caches merged by y04a_merge.py. Splitting changes nothing about the
    # selection: each tier reseeds its own rng at SEED and never reads another tier.
    ap.add_argument("--tier", choices=["C1", "C2", "C3", "C4"], default=None)
    args = ap.parse_args()
    TIERS = (args.tier,) if args.tier else ("C1", "C2", "C3", "C4")
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(W / "dataset.npz", allow_pickle=False)
    cv = np.load(W / "crossfit.npz", allow_pickle=False)
    comp, fold, rt_rep = d["component"], cv["cv_fold"], cv["rt_rep"]
    ix = [l.split("\t") for l in (W / "rt_chunk_index.tsv").read_text().splitlines()[1:]]
    rrow = {h: int(r) for h, r, _ in ix}
    pooled = np.load(POOLED).astype(np.float32)
    pooled /= np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)

    partners = collections.defaultdict(set)
    for h_nc, h_rt in zip(d["nc_hash"], d["rt_hash"]):
        partners[h_nc].add(h_rt)

    rows = []
    sel_cache = {}
    # Vectorised selection. The first implementation built each pair's pool with a Python
    # comprehension and ran a separate cosine search per pair (copying up to ~10k x 960
    # embeddings each time); under multithreaded BLAS contending with training it burned
    # 14.5 CPU-hours without finishing C3. Here each (fold, type) block gets ONE index map
    # and, for C3, ONE similarity matrix. The admissibility rules, pool ORDER (sorted RT
    # hash, as np.unique gives), pair loop order and RNG draw sequence are unchanged, so
    # C1/C2/C4 draws are identical to the per-pair form. C3 ranks with a stable argsort, so
    # an exact cosine tie is broken by pool order rather than arbitrarily.
    for tier in TIERS:
        rng = np.random.default_rng(SEED)
        q_idx, n_alt, alts = [], [], []
        for f in range(K):
            sel = np.where(fold == f)[0]
            hashes = d["rt_hash"][sel]
            types_f = d["retron_type"][sel]
            blocks = {}
            for t in np.unique(types_f):
                U = np.unique(hashes[types_f == t])
                pos = {h: k for k, h in enumerate(U)}
                blocks[t] = dict(U=U, pos=pos, S=None)
            rlen = {h: l for h, l in zip(hashes, d["rt_aa_len"][sel])}
            for t, b in blocks.items():
                b["len"] = np.array([rlen[h] for h in b["U"]], dtype=np.float64)
                if tier == "C3":
                    E = pooled[[rrow[h] for h in b["U"]]]
                    b["S"] = E @ E.T
            by_clu = collections.defaultdict(set)
            for h, rp in zip(hashes, rt_rep[sel]):
                by_clu[rp].add(h)
            for i in sel:
                own, nc = d["rt_hash"][i], d["nc_hash"][i]
                bad = partners[nc] | {own}
                if tier == "C4":
                    pool = np.array(sorted(by_clu[rt_rep[i]] - bad), dtype=object)
                    if len(pool) == 0:
                        continue
                    pick = pool[:M] if len(pool) <= M else pool[
                        rng.choice(len(pool), size=M, replace=False)]
                else:
                    b = blocks[d["retron_type"][i]]
                    ok = np.ones(len(b["U"]), dtype=bool)
                    for h in bad:
                        k = b["pos"].get(h)
                        if k is not None:
                            ok[k] = False
                    if tier == "C2":
                        L0 = rlen[own]
                        ok &= np.abs(b["len"] - L0) <= 0.10 * L0
                    cand = np.flatnonzero(ok)
                    if len(cand) == 0:
                        continue
                    if tier == "C3":
                        sims = b["S"][b["pos"][own], cand]
                        pick = b["U"][cand[np.argsort(-sims, kind="stable")[:M]]]
                    else:
                        if len(cand) < M:
                            continue
                        pick = b["U"][cand[rng.choice(len(cand), size=M, replace=False)]]
                    if tier in ("C1", "C2") and len(pick) < M:
                        continue
                q_idx.append(i); n_alt.append(len(pick))
                alts.append([rrow[h] for h in pick] + [-1] * (M - len(pick)))
            print(f"    {tier} fold {f}: {len(q_idx):,} eligible so far", flush=True)
        q_idx = np.array(q_idx)
        sel_cache[f"{tier}_q"] = q_idx.astype(np.int64)
        sel_cache[f"{tier}_alts"] = np.array(alts, dtype=np.int64) if len(alts) \
            else np.zeros((0, M), dtype=np.int64)
        nc = len(set(comp[q_idx])) if len(q_idx) else 0
        r = dict(tier=tier, eligible_pairs=int(len(q_idx)),
                 pct_of_population=round(100 * len(q_idx) / len(comp), 2),
                 n_components=int(nc), mean_alternatives=round(float(np.mean(n_alt)), 2)
                 if len(n_alt) else 0.0,
                 forward_passes=int(np.sum(n_alt)),
                 adjudicable="YES" if nc >= MIN_COMP else "NO_UNDETERMINED")
        rows.append(r)
        print(f"  {tier}: {r['eligible_pairs']:>6,} pairs ({r['pct_of_population']:>5.2f}%)  "
              f"{r['n_components']:>4} components  {r['mean_alternatives']:.2f} alt/pair  "
              f"{r['forward_passes']:>8,} fwd passes  -> {r['adjudicable']}")

    suffix = f"_{args.tier}" if args.tier else ""
    pd.DataFrame(rows).to_csv(OUT / f"COUNTERFACTUAL_TIER_SIZING{suffix}.tsv",
                              sep="\t", index=False)
    # The selection is deterministic under the frozen rules and seed. Cache it so y04
    # evaluates exactly these sets rather
    # than recomputing them, which also guarantees the sized tiers and the evaluated tiers
    # are the same sets.
    np.savez_compressed(W / f"cf_selection{suffix}.npz", **sel_cache)
    print(f"  cached selection -> {W / f'cf_selection{suffix}.npz'}")
    tot = sum(r["forward_passes"] for r in rows)
    print(f"\n  total counterfactual forward passes: {tot:,}")
    print(f"  wrote {OUT / 'COUNTERFACTUAL_TIER_SIZING.tsv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
