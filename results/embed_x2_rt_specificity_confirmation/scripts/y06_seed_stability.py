#!/usr/bin/env python
"""embed_x2/y06 - optimization-variance stability check (DESIGN Amendment A).

Three seeds (20260918 primary, 20260919 and 20260920 replicates) for arms T, G and R across
all 5 folds. The binding conditions from Amendment A are enforced here, not assumed:

  * replicate seeds estimate OPTIMIZATION variance only. They do NOT increase the biological
    sample size. The inference unit stays the connected component and the component count is
    IDENTICAL across seeds -- the bootstrap is never run over seed x component.
  * predictions are averaged WITHIN COMPONENT before any inference.
  * the primary endpoint remains the seed-20260918 cross-fit. The seed-averaged number is
    reported BESIDE it as a stability check and never substituted for it.

The question is narrow: is the sign and rough magnitude of R - T a property of the data, or
of one lucky optimization trajectory?
"""
from __future__ import annotations
import collections, sys
from pathlib import Path
import numpy as np, pandas as pd

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
SEEDS = [20260918, 20260919, 20260920]
ARMS = ["T", "G", "R"]
K, N_BOOT, PRIMARY = 5, 10_000, 20260918


def comp_mean(nll_sum, n_tok, comp):
    s, t = collections.defaultdict(float), collections.defaultdict(float)
    for v, n, c in zip(nll_sum, n_tok, comp):
        s[c] += v; t[c] += n
    ks = sorted(s)
    return np.array(ks), np.array([s[k] / t[k] for k in ks])


def paired(ka, a, kb, b, seed=PRIMARY, n=N_BOOT):
    common = np.intersect1d(ka, kb)
    d = a[np.searchsorted(ka, common)] - b[np.searchsorted(kb, common)]
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(n, len(d)))].mean(1)
    return dict(n_components=int(len(d)), diff=round(float(d.mean()), 6),
                median=round(float(np.median(d)), 6),
                ci_lo=round(float(np.percentile(m, 2.5)), 6),
                ci_hi=round(float(np.percentile(m, 97.5)), 6),
                frac_components_favouring_first=round(float((d < 0).mean()), 4))


def path_for(arm, f, seed):
    """Primary seed lives in work/; replicates were run on Ibex and land in work/seeds/."""
    return (W / f"oof_{arm}_f{f}.npz") if seed == PRIMARY \
        else (W / "seeds" / f"oof_{arm}_f{f}_s{seed}.npz")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(W / "dataset.npz", allow_pickle=False)
    comp = d["component"]
    n = len(comp)

    print("[1] load per-seed out-of-fold predictions")
    per = {}                                   # (arm, seed) -> (nll_sum, n_tok)
    for arm in ARMS:
        for s in SEEDS:
            acc = np.full(n, np.nan); tok = np.full(n, np.nan)
            missing = False
            for f in range(K):
                p = path_for(arm, f, s)
                if not p.is_file():
                    print(f"    MISSING {p}"); missing = True; break
                z = np.load(p)
                acc[z["idx"]] = z["nll_sum"]; tok[z["idx"]] = z["n_tok"]
            if missing:
                return 1
            assert not np.isnan(acc).any(), f"{arm}/{s} incomplete"
            per[(arm, s)] = (acc, tok)
        print(f"    {arm}: {len(SEEDS)} seeds x {K} folds complete")

    print("\n[2] per-seed contrasts (the SAME components every time)")
    rows = []
    for a, b in (("R", "T"), ("R", "G")):
        for s in SEEDS:
            ka, va = comp_mean(*per[(a, s)], comp)
            kb, vb = comp_mean(*per[(b, s)], comp)
            r = paired(ka, va, kb, vb)
            r.update(contrast=f"{a} - {b}", seed=s,
                     role="primary" if s == PRIMARY else "replicate")
            rows.append(r)
            print(f"    {a}-{b}  seed {s} ({r['role']:<9}): {r['diff']:+.6f} "
                  f"[{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}]  "
                  f"{r['frac_components_favouring_first']:.1%} favour {a}")

    print("\n[3] seed-averaged within component, then contrasted")
    for a, b in (("R", "T"), ("R", "G")):
        # average the per-component NLL across seeds FIRST (Amendment A), then difference
        ks = None; A = []; B = []
        for s in SEEDS:
            ka, va = comp_mean(*per[(a, s)], comp)
            kb, vb = comp_mean(*per[(b, s)], comp)
            assert np.array_equal(ka, kb)
            ks = ka if ks is None else ks
            assert np.array_equal(ka, ks), "component set differs between seeds"
            A.append(va); B.append(vb)
        r = paired(ks, np.mean(A, 0), ks, np.mean(B, 0))
        r.update(contrast=f"{a} - {b}", seed="mean_of_3", role="stability_check")
        rows.append(r)
        print(f"    {a}-{b}  seed-averaged: {r['diff']:+.6f} "
              f"[{r['ci_lo']:+.6f}, {r['ci_hi']:+.6f}]  "
              f"{r['frac_components_favouring_first']:.1%} favour {a}")

    print("\n[4] optimization variance of the point estimate")
    summ = []
    for a, b in (("R", "T"), ("R", "G")):
        v = np.array([r["diff"] for r in rows
                      if r["contrast"] == f"{a} - {b}" and r["seed"] in SEEDS])
        prim = [r["diff"] for r in rows
                if r["contrast"] == f"{a} - {b}" and r["seed"] == PRIMARY][0]
        summ.append(dict(contrast=f"{a} - {b}", n_seeds=len(v),
                         primary_seed_diff=prim,
                         across_seed_mean=round(float(v.mean()), 6),
                         across_seed_sd=round(float(v.std(ddof=1)), 6),
                         across_seed_min=round(float(v.min()), 6),
                         across_seed_max=round(float(v.max()), 6),
                         all_same_sign=bool((v < 0).all() or (v > 0).all())))
        print(f"    {a}-{b}: primary {prim:+.6f}  across-seed mean {v.mean():+.6f} "
              f"sd {v.std(ddof=1):.6f}  range [{v.min():+.6f}, {v.max():+.6f}]  "
              f"same sign: {summ[-1]['all_same_sign']}")

    pd.DataFrame(rows).to_csv(OUT / "SEED_STABILITY.tsv", sep="\t", index=False)
    pd.DataFrame(summ).to_csv(OUT / "SEED_VARIANCE_SUMMARY.tsv", sep="\t", index=False)
    print(f"\nwrote SEED_STABILITY.tsv and SEED_VARIANCE_SUMMARY.tsv")
    print("NOTE: the primary endpoint remains the seed-20260918 cross-fit. Seed replicates "
          "bound optimization noise; they do not add independent biological observations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
