#!/usr/bin/env python
"""embed_x2/y07 - machine-readable exports for downstream integration.

Writes per-PAIR and per-COMPONENT observed-versus-counterfactual effects alongside the
identifiers and strata a later analysis needs to join on: RT hash, ncRNA hash, component,
cross-fit fold, retron type, RT homolog group (frozen rt_id0.50 representative), the
relatedness stratum, and the tier definitions.

These exports exist so that independently defined features -- Region X/Y annotations, RT
phylogeny, ncRNA family, terminal/fusion architecture -- can be joined later WITHOUT
retraining X2. No such join is performed here.

INTERPRETATION IS BINDING AND TRAVELS WITH THE DATA. Every delta_logP column is
    NLL(ncRNA | alternative RT) - NLL(ncRNA | observed RT),
positive meaning the model assigned higher likelihood under the RT actually observed with
that ncRNA. It is NOT a compatibility score, NOT an interaction probability, and NOT evidence
that an alternative RT is biologically incompatible. A combination absent from the corpus is
a NON-OBSERVED PAIRING, never a negative. Pair-level values are exported for completeness and
for joining; the inference unit of this experiment is the COMPONENT, and no per-pair
biological inference is supported.
"""
from __future__ import annotations
import collections, sys
from pathlib import Path
import numpy as np, pandas as pd, torch

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
ROOT = TASK.parents[1]
POOLED = ROOT / "ARIS_OUTPUT" / "embed_g2_analysis" / "work" / "rt_pooled.npy"
sys.path.insert(0, str(ROOT / "results" / "embed_x1_conditional_pilot" / "scripts"))
sys.path.insert(0, str(TASK / "scripts"))
from x03_model import CondNcRNADecoder                       # noqa: E402
from y03_train_cv import load, make_batch                    # noqa: E402

ARMS = ["U", "T", "G", "R", "P"]
TIERS = ["C1", "C2", "C3", "C4"]
K, M, SEED = 5, 8, 20260918


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d, cv, rt, rtm, rrow = load(W)
    comp, fold, rt_rep = d["component"], cv["cv_fold"], cv["rt_rep"]
    n = len(comp)
    dev = "cuda" if torch.cuda.is_available() else "cpu"

    print("[1] out-of-fold per-pair NLL for every arm")
    pt = {}
    for arm in ARMS:
        s = np.full(n, np.nan); t = np.full(n, np.nan)
        for f in range(K):
            z = np.load(W / f"oof_{arm}_f{f}.npz")
            s[z["idx"]] = z["nll_sum"]; t[z["idx"]] = z["n_tok"]
        assert not np.isnan(s).any(), f"{arm} incomplete"
        pt[arm] = s / t
        pt[arm + "_sum"] = s; pt["n_tok"] = t

    print("[2] relatedness stratum (cosine to nearest RT seen in that fold's training set)")
    pooled = np.load(POOLED).astype(np.float32)
    pooled /= np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)
    rows_all = np.array([rrow[h] for h in d["rt_hash"]])
    sim = np.zeros(n, dtype=np.float32)
    for f in range(K):
        te = np.where(fold == f)[0]
        tr = np.where(~np.isin(fold, [f, (f + 1) % K]))[0]
        A, B = pooled[rows_all[te]], pooled[np.unique(rows_all[tr])]
        best = np.full(len(te), -1.0, dtype=np.float32)
        for k in range(0, len(te), 2048):
            best[k:k + 2048] = (A[k:k + 2048] @ B.T).max(1)
        sim[te] = best
    q = np.quantile(sim, [.25, .5, .75])
    strat = np.where(sim < q[0], "Q1", np.where(sim < q[1], "Q2",
                     np.where(sim < q[2], "Q3", "Q4")))

    print("[3] per-pair counterfactual delta log P per tier")
    models = {}
    for f in range(K):
        ck = torch.load(W / f"m_R_f{f}.pt", map_location=dev, weights_only=False)
        m = CondNcRNADecoder("R").to(dev); m.load_state_dict(ck["state_dict"]); m.eval()
        models[f] = m
    cf_sel = np.load(W / "cf_selection.npz")
    dlp = {t: np.full(n, np.nan) for t in TIERS}
    nalt = {t: np.zeros(n, dtype=np.int16) for t in TIERS}
    for tier in TIERS:
        q_idx, alts = cf_sel[f"{tier}_q"], cf_sel[f"{tier}_alts"]
        acc = np.zeros(len(q_idx)); cnt = np.zeros(len(q_idx))
        for j in range(M):
            for f in range(K):
                sub = np.where((fold[q_idx] == f) & (alts[:, j] >= 0))[0]
                if not len(sub):
                    continue
                S, N = [], []
                for k0 in range(0, len(sub), 64):
                    ss = sub[k0:k0 + 64]
                    b = make_batch(q_idx[ss], d, alts[ss, j], rt, rtm, "R", dev)
                    with torch.no_grad():
                        o = models[f](b)
                    S.append(o["nll_sum"].cpu().numpy()); N.append(o["n_tok"].cpu().numpy())
                acc[sub] += np.concatenate(S) / np.concatenate(N); cnt[sub] += 1
        alt_pt = acc / np.maximum(cnt, 1)
        dlp[tier][q_idx] = alt_pt - pt["R"][q_idx]     # positive favours the OBSERVED RT
        nalt[tier][q_idx] = cnt.astype(np.int16)
        ok = ~np.isnan(dlp[tier])
        print(f"    {tier}: {int(ok.sum()):,} pairs scored, mean {np.nanmean(dlp[tier]):+.6f}")

    print("[4] write per-pair export")
    pair = pd.DataFrame(dict(
        rt_seq_hash=d["rt_hash"], nc_seq_hash=d["nc_hash"],
        component_id=comp, cv_fold=fold, retron_type=d["retron_type"],
        rt_homolog_group=rt_rep, rt_aa_len=d["rt_aa_len"],
        nc_len=d["nc_len"][d["nc_row"]], n_tok=pt["n_tok"].astype(int),
        T3=d["T3"], T4=d["T4"], in_sensitivity_population=d["sensitivity"],
        nearest_train_rt_cosine=np.round(sim, 6), relatedness_stratum=strat,
        nll_per_nt_U=np.round(pt["U"], 6), nll_per_nt_T=np.round(pt["T"], 6),
        nll_per_nt_G=np.round(pt["G"], 6), nll_per_nt_R=np.round(pt["R"], 6),
        nll_per_nt_P=np.round(pt["P"], 6),
        delta_R_minus_T=np.round(pt["R"] - pt["T"], 6),
        delta_R_minus_G=np.round(pt["R"] - pt["G"], 6),
    ))
    for t in TIERS:
        pair[f"delta_logP_{t}"] = np.round(dlp[t], 6)
        pair[f"n_alternatives_{t}"] = nalt[t]
    pair.to_csv(OUT / "X2_PAIR_LEVEL_EFFECTS.tsv.gz", sep="\t", index=False)
    print(f"    {len(pair):,} rows -> X2_PAIR_LEVEL_EFFECTS.tsv.gz")

    print("[5] write per-component export (token-weighted; the inference unit)")
    g = pair.groupby("component_id")
    wsum = lambda col: (pair[col] * pair.n_tok).groupby(pair.component_id).sum() / \
        pair.n_tok.groupby(pair.component_id).sum()
    ccomp = pd.DataFrame(dict(
        n_pairs=g.size(), n_tok=g.n_tok.sum(),
        n_distinct_rt=g.rt_seq_hash.nunique(), n_distinct_ncrna=g.nc_seq_hash.nunique(),
        n_retron_types=g.retron_type.nunique(), n_rt_homolog_groups=g.rt_homolog_group.nunique(),
        cv_fold=g.cv_fold.first(),
        dominant_retron_type=g.retron_type.agg(lambda s: s.value_counts().index[0]),
        any_T4=g.T4.max(), any_T3=g.T3.max(),
        in_sensitivity_population=g.in_sensitivity_population.max(),
        mean_nearest_train_rt_cosine=np.round(g.nearest_train_rt_cosine.mean(), 6),
        relatedness_stratum=g.relatedness_stratum.agg(lambda s: s.value_counts().index[0]),
    ))
    for a in ARMS:
        ccomp[f"nll_per_nt_{a}"] = np.round(wsum(f"nll_per_nt_{a}"), 6)
    ccomp["delta_R_minus_T"] = np.round(ccomp.nll_per_nt_R - ccomp.nll_per_nt_T, 6)
    ccomp["delta_R_minus_G"] = np.round(ccomp.nll_per_nt_G.rsub(ccomp.nll_per_nt_R), 6)
    ccomp["delta_R_minus_P"] = np.round(ccomp.nll_per_nt_R - ccomp.nll_per_nt_P, 6)
    ccomp["delta_P_minus_T"] = np.round(ccomp.nll_per_nt_P - ccomp.nll_per_nt_T, 6)
    for t in TIERS:
        sub = pair[~pair[f"delta_logP_{t}"].isna()]
        num = (sub[f"delta_logP_{t}"] * sub.n_tok).groupby(sub.component_id).sum()
        den = sub.n_tok.groupby(sub.component_id).sum()
        ccomp[f"delta_logP_{t}"] = np.round((num / den).reindex(ccomp.index), 6)
        ccomp[f"n_pairs_{t}"] = sub.groupby("component_id").size().reindex(
            ccomp.index).fillna(0).astype(int)
    ccomp.reset_index().to_csv(OUT / "X2_COMPONENT_LEVEL_EXPORT.tsv", sep="\t", index=False)
    print(f"    {len(ccomp):,} components -> X2_COMPONENT_LEVEL_EXPORT.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
