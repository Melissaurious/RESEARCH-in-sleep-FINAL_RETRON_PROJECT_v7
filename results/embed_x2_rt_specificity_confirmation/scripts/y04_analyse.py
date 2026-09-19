#!/usr/bin/env python
"""embed_x2/y04 - aggregate the cross-fit and run the frozen counterfactual hierarchy.

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

    print("\n[5] counterfactual hierarchy C1-C4 (frozen rules; evaluation only)")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    pooled = np.load(TASK.parents[1] / "ARIS_OUTPUT/embed_g2_analysis/work/rt_pooled.npy")
    pooled = pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)
    partners = collections.defaultdict(set)
    for h_nc, h_rt in zip(d["nc_hash"], d["rt_hash"]):
        partners[h_nc].add(h_rt)
    rt_rep = cv["rt_rep"]
    cf_rows = []
    models = {}
    for f in range(K):
        ck = torch.load(W / f"m_R_f{f}.pt", map_location=dev, weights_only=False)
        m = CondNcRNADecoder("R").to(dev); m.load_state_dict(ck["state_dict"]); m.eval()
        models[f] = m

    # The tier selection is produced and frozen by y04a_tier_sizing.py under the rules in
    # COUNTERFACTUAL_RULES.md. Reusing that cache guarantees the tiers that were sized are
    # the tiers that get evaluated, and keeps the slow C3 cosine search out of this script.
    cf_sel = np.load(W / "cf_selection.npz")

    for tier in ("C1", "C2", "C3", "C4"):
        rng = np.random.default_rng(SEED)
        q_idx, alts = cf_sel[f"{tier}_q"], cf_sel[f"{tier}_alts"]
        if len(q_idx) == 0:
            cf_rows.append(dict(tier=tier, status="NO_ELIGIBLE_PAIRS")); continue

        obs_pt = oof["R"][0][q_idx] / oof["R"][1][q_idx]
        acc = np.zeros(len(q_idx)); cnt = np.zeros(len(q_idx))
        for j in range(M):
            for f in range(K):
                sub = np.where((fold[q_idx] == f) & (alts[:, j] >= 0))[0]
                if not len(sub):
                    continue
                mdl = models[f]
                S, N = [], []
                for k0 in range(0, len(sub), 64):
                    ss = sub[k0:k0 + 64]
                    b = make_batch(q_idx[ss], d, alts[ss, j], rt, rtm, "R", dev)
                    with torch.no_grad():
                        o = mdl(b)
                    S.append(o["nll_sum"].cpu().numpy()); N.append(o["n_tok"].cpu().numpy())
                acc[sub] += np.concatenate(S) / np.concatenate(N); cnt[sub] += 1
        alt_pt = acc / np.maximum(cnt, 1)
        dlp = alt_pt - obs_pt                      # positive favours the observed RT
        k2, v2 = comp_mean(dlp * oof["R"][1][q_idx], oof["R"][1][q_idx], comp[q_idx])
        mu, lo, hi = boot(v2)
        r = dict(tier=tier, eligible_pairs=int(len(q_idx)), n_components=int(len(v2)),
                 alternatives_per_pair=float(cnt.mean()),
                 delta_logP_per_nt=round(mu, 6), ci_lo=round(lo, 6), ci_hi=round(hi, 6),
                 frac_pairs_favouring_observed=round(float((dlp > 0).mean()), 4),
                 frac_components_favouring_observed=round(float((v2 > 0).mean()), 4),
                 status="OK" if len(v2) >= MIN_COMP else "UNDETERMINED")
        cf_rows.append(r)
        print(f"    {tier}: {len(q_idx):>6,} pairs / {len(v2):>4} comps  "
              f"Δ {mu:+.6f} [{lo:+.6f}, {hi:+.6f}]  "
              f"{r['frac_pairs_favouring_observed']:.1%} pairs favour observed  {r['status']}")

    pd.DataFrame(rows).to_csv(OUT / "COMPONENT_LEVEL_EFFECTS.tsv", sep="\t", index=False)
    pd.DataFrame(fh).to_csv(OUT / "FOLD_HETEROGENEITY.tsv", sep="\t", index=False)
    pd.DataFrame(cf_rows).to_csv(OUT / "COUNTERFACTUAL_EFFECTS.tsv", sep="\t", index=False)
    lin = [r for r in rows if r["contrast"] in ("R - G", "G - T", "G - U")]
    pd.DataFrame(lin).to_csv(OUT / "LINEAGE_CONTROL.tsv", sep="\t", index=False)
    perm = [r for r in rows if r["contrast"] in ("P - T", "R - P")]
    pd.DataFrame(perm).to_csv(OUT / "PERMUTATION_CONTROL.tsv", sep="\t", index=False)
    print("\nwrote COMPONENT_LEVEL_EFFECTS.tsv, FOLD_HETEROGENEITY.tsv, "
          "COUNTERFACTUAL_EFFECTS.tsv, LINEAGE_CONTROL.tsv, PERMUTATION_CONTROL.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
