#!/usr/bin/env python
"""embed_x1/x06 - evaluation. Opens TEST once, after all three arms are fixed.

Component-level throughout: per-sequence NLL -> per-component mean -> bootstrap over components.
Pair count is never the inferential sample size.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x03_model import CondNcRNADecoder, count_params  # noqa: E402
from x04_train import load, make_batch, batches, evaluate, SEED  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
M_COUNTERFACTUAL = 8          # PREREG: alternatives per eligible pair
MIN_TYPE_RTS = 9              # PREREG: a type needs >= 9 distinct test RTs to be eligible
N_BOOT = 10_000


def comp_mean(vals, n_tok, comp):
    """Per-sequence NLL -> per-component mean. Token-weighted within a component."""
    import collections
    s, t = collections.defaultdict(float), collections.defaultdict(float)
    for v, n, c in zip(vals, n_tok, comp):
        s[c] += v; t[c] += n
    ks = sorted(s)
    return np.array(ks), np.array([s[k] / t[k] for k in ks])


def boot(x, seed=SEED, n=N_BOOT):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    m = x[idx].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def paired(a_keys, a, b_keys, b, seed=SEED, n=N_BOOT):
    """Paired per-component difference a - b, bootstrapped over components."""
    common = np.intersect1d(a_keys, b_keys)
    da = a[np.searchsorted(a_keys, common)]; db = b[np.searchsorted(b_keys, common)]
    d = da - db
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    m = d[idx].mean(1)
    return dict(n_components=len(d), diff=float(d.mean()),
                ci_lo=float(np.percentile(m, 2.5)), ci_hi=float(np.percentile(m, 97.5)),
                frac_components_favouring_a=float((d < 0).mean()))


@torch.no_grad()
def per_seq(model, idx, d, rt, rtm, rrow, arm, dev, bs=64, rt_rows_override=None):
    model.eval(); S, N = [], []
    for k in range(0, len(idx), bs):
        sel = idx[k:k + bs]
        b = make_batch(sel, d, rt, rtm, rrow, arm, dev)
        if rt_rows_override is not None:
            rows = rt_rows_override[k:k + bs]
            b["rt_chunks"] = torch.from_numpy(np.asarray(rt[rows], dtype=np.float32)).to(dev)
            b["rt_mask"] = torch.from_numpy(rtm[rows]).to(dev)
        o = model(b)
        S.append(o["nll_sum"].cpu().numpy()); N.append(o["n_tok"].cpu().numpy())
    return np.concatenate(S), np.concatenate(N)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    d, rt, rtm, rrow = load()
    comp = d["component"]
    te = np.where(d["fold"] == "test")[0]
    va = np.where(d["fold"] == "val")[0]
    assert len(te) == 4638

    models, res = {}, {}
    for arm in ("U", "T", "R"):
        ck = torch.load(W / f"model_{arm}.pt", map_location=dev, weights_only=False)
        m = CondNcRNADecoder(arm).to(dev); m.load_state_dict(ck["state_dict"]); m.eval()
        models[arm] = m
        res[arm] = dict(params=ck["params"], best_epoch=ck["epoch"],
                        val_nll_at_selection=ck["val_nll"])
        print(f"loaded {arm}: epoch {ck['epoch']}, val NLL {ck['val_nll']:.5f}, "
              f"{ck['params']['total']:,} params")

    print("\n[1] validation and TEST per-nucleotide NLL (component-level)")
    rows, ck_keys, ck_vals = [], {}, {}
    for arm in ("U", "T", "R"):
        vs, vn = per_seq(models[arm], va, d, rt, rtm, rrow, arm, dev)
        ts, tn = per_seq(models[arm], te, d, rt, rtm, rrow, arm, dev)
        kk, cv = comp_mean(ts, tn, comp[te])
        ck_keys[arm], ck_vals[arm] = kk, cv
        mu, lo, hi = boot(cv)
        rows.append(dict(arm=arm, params=res[arm]["params"]["total"],
                         val_nll=round(float(vs.sum() / vn.sum()), 5),
                         test_nll_pooled=round(float(ts.sum() / tn.sum()), 5),
                         test_nll_component_mean=round(mu, 5),
                         ci_lo=round(lo, 5), ci_hi=round(hi, 5),
                         test_ppl=round(math.exp(mu), 4), n_components=len(cv)))
        print(f"    {arm}: val {rows[-1]['val_nll']:.5f}  test {mu:.5f} "
              f"[{lo:.5f}, {hi:.5f}]  ppl {math.exp(mu):.4f}")
        np.save(W / f"test_seqnll_{arm}.npy", ts); np.save(W / f"test_ntok_{arm}.npy", tn)

    print("\n[2] paired per-component comparisons (negative diff = first arm better)")
    cmp_rows = []
    for a, b in (("T", "U"), ("R", "U"), ("R", "T")):
        r = paired(ck_keys[a], ck_vals[a], ck_keys[b], ck_vals[b])
        r.update(comparison=f"{a} - {b}")
        cmp_rows.append(r)
        print(f"    {a} - {b}: {r['diff']:+.5f} [{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}]  "
              f"components favouring {a}: {r['frac_components_favouring_a']:.1%}")

    print("\n[3] near-duplicate sensitivity population (frozen, 1,525 pairs)")
    sens = te[d["sensitivity"][te] == 1]
    sens_rows = []
    sk, sv = {}, {}
    for arm in ("U", "T", "R"):
        ss, sn = per_seq(models[arm], sens, d, rt, rtm, rrow, arm, dev)
        kk, cv = comp_mean(ss, sn, comp[sens]); sk[arm], sv[arm] = kk, cv
        mu, lo, hi = boot(cv)
        sens_rows.append(dict(arm=arm, n_pairs=len(sens), n_components=len(cv),
                              nll=round(mu, 5), ci_lo=round(lo, 5), ci_hi=round(hi, 5)))
    for a, b in (("R", "T"), ("R", "U")):
        r = paired(sk[a], sv[a], sk[b], sv[b]); r.update(comparison=f"{a} - {b}")
        sens_rows.append(r)
        print(f"    {a} - {b}: {r['diff']:+.5f} [{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}]")

    print("\n[4] same-type counterfactual conditioning control (evaluation only)")
    rng = np.random.default_rng(SEED)
    te_types = d["retron_type"][te]
    partners = {}
    for i in range(len(d["fold"])):
        partners.setdefault(d["nc_hash"][i], set()).add(d["rt_hash"][i])
    by_type = {}
    for t in np.unique(te_types):
        by_type[t] = np.unique(d["rt_hash"][te][te_types == t])
    elig, alt_rows, base_rows = [], [], []
    for pos, i in enumerate(te):
        t = d["retron_type"][i]
        pool = by_type[t]
        if len(pool) < MIN_TYPE_RTS:
            continue
        bad = partners.get(d["nc_hash"][i], set()) | {d["rt_hash"][i]}
        cand = np.array([h for h in pool if h not in bad])
        if len(cand) < M_COUNTERFACTUAL:
            continue
        pick = rng.choice(len(cand), size=M_COUNTERFACTUAL, replace=False)
        elig.append(pos)
        alt_rows.append([rrow[cand[j]] for j in pick])
    elig = np.array(elig); alt_rows = np.array(alt_rows)
    print(f"    eligible held-out pairs: {len(elig):,}/{len(te):,} "
          f"({100*len(elig)/len(te):.1f}%); {M_COUNTERFACTUAL} alternatives each")
    idx = te[elig]
    obs_s, obs_n = per_seq(models["R"], idx, d, rt, rtm, rrow, "R", dev)
    obs_pt = obs_s / obs_n
    alt_pt = np.zeros((len(idx), M_COUNTERFACTUAL))
    for j in range(M_COUNTERFACTUAL):
        s_, n_ = per_seq(models["R"], idx, d, rt, rtm, rrow, "R", dev,
                         rt_rows_override=alt_rows[:, j])
        alt_pt[:, j] = s_ / n_
    # Delta log P per nucleotide = NLL(alt) - NLL(observed); positive favours the observed RT
    dlp = alt_pt.mean(1) - obs_pt
    kk, cv = comp_mean(dlp * obs_n, obs_n, comp[idx])
    mu, lo, hi = boot(cv)
    cf = dict(n_eligible=int(len(idx)), n_alternatives=M_COUNTERFACTUAL,
              min_type_rts=MIN_TYPE_RTS, n_components=int(len(cv)),
              delta_logP_per_nt=round(mu, 6), ci_lo=round(lo, 6), ci_hi=round(hi, 6),
              frac_pairs_favouring_observed=round(float((dlp > 0).mean()), 4),
              frac_components_favouring_observed=round(float((cv > 0).mean()), 4))
    print(f"    Δ log P per nt (observed vs same-type alternative): {mu:+.6f} "
          f"[{lo:+.6f}, {hi:+.6f}]  over {len(cv)} components")
    print(f"    pairs favouring the observed RT: {cf['frac_pairs_favouring_observed']:.1%}")

    print("\n[5] descriptive strata (T1-T4), arm R minus arm T")
    strat = []
    for t in ("T1", "T2", "T3", "T4"):
        mask = d[t][te] == 1
        if mask.sum() < 100:
            strat.append(dict(stratum=t, n=int(mask.sum()), status="INSUFFICIENT")); continue
        sub = te[mask]
        rs, rn = per_seq(models["R"], sub, d, rt, rtm, rrow, "R", dev)
        ts_, tn_ = per_seq(models["T"], sub, d, rt, rtm, rrow, "T", dev)
        ka, va_ = comp_mean(rs, rn, comp[sub]); kb, vb = comp_mean(ts_, tn_, comp[sub])
        r = paired(ka, va_, kb, vb); r.update(stratum=t, n=int(mask.sum()), status="OK")
        strat.append(r)
        print(f"    {t}: n={int(mask.sum()):,}  R-T {r['diff']:+.5f} "
              f"[{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}]  ({r['n_components']} comps)")

    import pandas as pd
    pd.DataFrame(rows).to_csv(OUT / "x1_arms.tsv", sep="\t", index=False)
    pd.DataFrame(cmp_rows).to_csv(OUT / "x1_comparisons.tsv", sep="\t", index=False)
    pd.DataFrame(sens_rows).to_csv(OUT / "x1_sensitivity.tsv", sep="\t", index=False)
    pd.DataFrame(strat).to_csv(OUT / "x1_strata.tsv", sep="\t", index=False)
    (OUT / "x1_counterfactual.json").write_text(json.dumps(cf, indent=2) + "\n")
    print("\nwrote x1_arms.tsv, x1_comparisons.tsv, x1_sensitivity.tsv, x1_strata.tsv, "
          "x1_counterfactual.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
