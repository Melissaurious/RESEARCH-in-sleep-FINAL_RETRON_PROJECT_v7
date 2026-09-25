#!/usr/bin/env python
"""embed_x2/y04b - PRIMARY endpoint only: the cross-fitted component-level contrasts.

Split out of y04_analyse.py because the primary endpoint (R - T), the lineage control
(R - G), the permutation control and the fold heterogeneity depend only on the out-of-fold
predictions, NOT on the counterfactual hierarchy. They are therefore computed as soon as the
25 cells land, while the C1-C4 tier selection is still being built. Identical code path --
this file only drops section [5].

Component-level throughout. Pairs are never the inference unit.
"""
from __future__ import annotations
import collections, json, sys
from pathlib import Path
import numpy as np, pandas as pd, torch

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
X1 = TASK.parents[1] / "results" / "embed_x1_conditional_pilot" / "scripts"
sys.path.insert(0, str(X1)); sys.path.insert(0, str(TASK / "scripts"))
from x03_model import CondNcRNADecoder                       # noqa: E402
from y03_train_cv import load, make_batch                    # noqa: E402

ARMS = ["U", "T", "G", "R", "P"]
K, M, N_BOOT, MIN_COMP = 5, 8, 10_000, 30
SEED = 20260918


def comp_mean(nll_sum, n_tok, comp):
    s, t = collections.defaultdict(float), collections.defaultdict(float)
    for v, n, c in zip(nll_sum, n_tok, comp):
        s[c] += v; t[c] += n
    ks = sorted(s)
    return np.array(ks), np.array([s[k] / t[k] for k in ks])


def boot(x, seed=SEED, n=N_BOOT):
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(n, len(x)))].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def paired(ka, a, kb, b, seed=SEED, n=N_BOOT):
    common = np.intersect1d(ka, kb)
    d = a[np.searchsorted(ka, common)] - b[np.searchsorted(kb, common)]
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(n, len(d)))].mean(1)
    trim = np.sort(d)[int(.05 * len(d)):max(int(.95 * len(d)), int(.05 * len(d)) + 1)]
    return dict(n_components=len(d), diff=float(d.mean()), median=float(np.median(d)),
                trimmed_mean_90=float(trim.mean()),
                ci_lo=float(np.percentile(m, 2.5)), ci_hi=float(np.percentile(m, 97.5)),
                frac_components_favouring_first=float((d < 0).mean()),
                n_eff=float((np.ones(len(d)).sum() ** 2) / len(d)))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d, cv, rt, rtm, rrow = load(W)
    comp, fold = d["component"], cv["cv_fold"]
    n = len(comp)

    print("[1] assemble out-of-fold predictions")
    oof = {}
    for arm in ARMS:
        s = np.full(n, np.nan); t = np.full(n, np.nan)
        for f in range(K):
            p = W / f"oof_{arm}_f{f}.npz"
            if not p.is_file():
                print(f"    MISSING {p.name}"); return 1
            z = np.load(p)
            s[z["idx"]] = z["nll_sum"]; t[z["idx"]] = z["n_tok"]
        assert not np.isnan(s).any(), f"{arm}: not every pair evaluated out-of-fold"
        oof[arm] = (s, t)
        k, v = comp_mean(s, t, comp)
        mu, lo, hi = boot(v)
        print(f"    {arm}: OOF NLL (component mean) {mu:.5f} [{lo:.5f}, {hi:.5f}] "
              f"over {len(v)} components")

    print("\n[2] paired per-component contrasts (negative = first arm better)")
    rows = []
    for a, b in (("T", "U"), ("G", "U"), ("R", "U"), ("R", "T"), ("R", "G"),
                 ("G", "T"), ("P", "T"), ("R", "P")):
        ka, va = comp_mean(*oof[a], comp); kb, vb = comp_mean(*oof[b], comp)
        r = paired(ka, va, kb, vb); r["contrast"] = f"{a} - {b}"; r["population"] = "all"
        rows.append(r)
        print(f"    {a}-{b}: {r['diff']:+.5f} [{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}] "
              f"med {r['median']:+.5f}  {r['frac_components_favouring_first']:.1%} favour {a}")

    print("\n[3] prespecified strata")
    for name, mask in (("T4", d["T4"] == 1), ("T3", d["T3"] == 1),
                       ("near_dup_sensitivity", d["sensitivity"] == 1)):
        for a, b in (("R", "T"), ("R", "G")):
            ka, va = comp_mean(oof[a][0][mask], oof[a][1][mask], comp[mask])
            kb, vb = comp_mean(oof[b][0][mask], oof[b][1][mask], comp[mask])
            r = paired(ka, va, kb, vb); r["contrast"] = f"{a} - {b}"; r["population"] = name
            r["status"] = "OK" if r["n_components"] >= MIN_COMP else "UNDETERMINED"
            rows.append(r)
            if a == "R" and b == "T":
                print(f"    {name:<22} R-T {r['diff']:+.5f} "
                      f"[{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}]  "
                      f"{r['n_components']} comps  {r['status']}")

    print("\n[4] between-fold heterogeneity of R - T")
    fh = []
    for f in range(K):
        m = fold == f
        ka, va = comp_mean(oof["R"][0][m], oof["R"][1][m], comp[m])
        kb, vb = comp_mean(oof["T"][0][m], oof["T"][1][m], comp[m])
        r = paired(ka, va, kb, vb); r["fold"] = f
        fh.append(r)
        print(f"    fold {f}: {r['diff']:+.5f} [{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}] "
              f"({r['n_components']} comps)")
    dif = np.array([x["diff"] for x in fh])
    print(f"    across folds: mean {dif.mean():+.5f}  sd {dif.std(ddof=1):.5f}  "
          f"all same sign: {bool((dif < 0).all() or (dif > 0).all())}")

    pd.DataFrame(rows).to_csv(OUT / "COMPONENT_LEVEL_EFFECTS.tsv", sep="\t", index=False)
    pd.DataFrame(fh).to_csv(OUT / "FOLD_HETEROGENEITY.tsv", sep="\t", index=False)
    lin = [r for r in rows if r["contrast"] in ("R - G", "G - T", "G - U")]
    pd.DataFrame(lin).to_csv(OUT / "LINEAGE_CONTROL.tsv", sep="\t", index=False)
    perm = [r for r in rows if r["contrast"] in ("P - T", "R - P")]
    pd.DataFrame(perm).to_csv(OUT / "PERMUTATION_CONTROL.tsv", sep="\t", index=False)
    print("\nwrote COMPONENT_LEVEL_EFFECTS.tsv, FOLD_HETEROGENEITY.tsv, "
          "LINEAGE_CONTROL.tsv, PERMUTATION_CONTROL.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
