#!/usr/bin/env python
"""embed_g2/a02 - the retrieval engine: candidate ladder, scorers, component-level inference.

Library module. Executes nothing on its own; a02 is imported by a03 (validation) and a04
(test) so that the SAME code produces both, and the test run cannot accidentally differ.

DECOY SAMPLING IS SEEDED. Decoys are drawn with numpy Generator(PCG64, seed=20260918), fixed
here and never varied. A decoy set is therefore a deterministic function of (fold, rung, query)
and re-running reproduces the identical candidate sets. The seed is an implementation detail
declared before any metric was read, not a tuned quantity.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20260918
N_DECOY = 49                     # 50-way retrieval, per PREREG
CHANCE_MRR = float(np.mean([1.0 / r for r in range(1, N_DECOY + 2)]))
RUNGS = ["rung1_random", "rung2_len_gc", "rung3_model", "rung4_nc_cluster",
         "rung5_rt_cluster", "rung6_species"]


# ------------------------------------------------------------------ latent projection
def fit_rcca(X: np.ndarray, Y: np.ndarray, k: int, alpha: float):
    """Regularized CCA by symmetric whitening. Fit on TRAINING PAIRS ONLY.

    alpha is scaled by mean(diag(C)) so it is dimensionless and comparable across the two
    spaces, which have different dimensionality (960 vs 1280) and different scales.
    """
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    n = len(Xc)
    Cxx = Xc.T @ Xc / n
    Cyy = Yc.T @ Yc / n
    Cxy = Xc.T @ Yc / n
    Cxx += np.eye(Cxx.shape[0], dtype=Cxx.dtype) * alpha * np.trace(Cxx) / Cxx.shape[0]
    Cyy += np.eye(Cyy.shape[0], dtype=Cyy.dtype) * alpha * np.trace(Cyy) / Cyy.shape[0]

    def inv_sqrt(C):
        w, V = np.linalg.eigh(C)
        w = np.maximum(w, 1e-12)
        return (V * w ** -0.5) @ V.T

    Wx0, Wy0 = inv_sqrt(Cxx), inv_sqrt(Cyy)
    U, S, Vt = np.linalg.svd(Wx0 @ Cxy @ Wy0, full_matrices=False)
    return dict(mx=X.mean(0), my=Y.mean(0),
                Wx=Wx0 @ U[:, :k], Wy=Wy0 @ Vt[:k].T, corrs=S[:k])


def project(model, X, Y):
    """Project and L2-normalise, so every score is a cosine and any pair scores in O(k)."""
    A = (X - model["mx"]) @ model["Wx"]
    B = (Y - model["my"]) @ model["Wy"]
    A /= np.maximum(np.linalg.norm(A, axis=1, keepdims=True), 1e-9)
    B /= np.maximum(np.linalg.norm(B, axis=1, keepdims=True), 1e-9)
    return A, B


# ------------------------------------------------------------------ candidate ladder
def build_candidates(df: pd.DataFrame, fold_df: pd.DataFrame, true_partners: dict,
                     rung: str, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Return (queries_kept, candidate_nc_rows[n_kept, N_DECOY+1]) with column 0 = true.

    A rung that cannot supply N_DECOY admissible decoys for a query DROPS that query; the
    caller reports how many were dropped rather than substituting an easier pool.
    """
    pool_nc = fold_df.nc_seq_hash.values
    pool_row = fold_df.nc_row.values
    uniq = pd.DataFrame({"h": pool_nc, "r": pool_row}).drop_duplicates("h")
    all_h, all_r = uniq.h.values, uniq.r.values

    # per-rung candidate pools, as index arrays into (all_h, all_r)
    if rung == "rung1_random":
        pools = None                                   # uniform over all_h
    elif rung == "rung2_len_gc":
        meta = fold_df.drop_duplicates("nc_seq_hash").set_index("nc_seq_hash")
        L = meta.loc[all_h, "nc_len"].values.astype(float)
        G = meta.loc[all_h, "nc_gc"].values.astype(float)
    elif rung == "rung3_model":
        key = fold_df.drop_duplicates("nc_seq_hash").set_index("nc_seq_hash")["detection_model"]
        grp = pd.Series(key.loc[all_h].values)
    elif rung == "rung4_nc_cluster":
        key = fold_df.drop_duplicates("nc_seq_hash").set_index("nc_seq_hash")["nc_cluster"]
        grp = pd.Series(key.loc[all_h].values)
    elif rung == "rung5_rt_cluster":
        by_rtc = fold_df.groupby("rt_cluster").nc_seq_hash.apply(lambda s: np.array(sorted(set(s))))
    elif rung == "rung6_species":
        by_sp = (fold_df[fold_df.tax_species_ncbi.notna()]
                 .groupby("tax_species_ncbi").nc_seq_hash.apply(lambda s: np.array(sorted(set(s)))))
    else:
        raise ValueError(rung)

    h2r = dict(zip(all_h, all_r))
    keep, cands = [], []
    for qi, row in enumerate(df.itertuples(index=False)):
        tp = true_partners.get(row.rt_seq_hash, set())
        if rung == "rung1_random":
            pool = all_h
        elif rung == "rung2_len_gc":
            m = (np.abs(L - row.nc_len) <= 0.10 * row.nc_len) & (np.abs(G - row.nc_gc) <= 0.05)
            pool = all_h[m]
        elif rung in ("rung3_model", "rung4_nc_cluster"):
            want = row.detection_model if rung == "rung3_model" else row.nc_cluster
            pool = all_h[(grp == want).values]
        elif rung == "rung5_rt_cluster":
            pool = by_rtc.get(row.rt_cluster, np.array([], dtype=object))
        else:
            if row.tax_species_ncbi is None or (isinstance(row.tax_species_ncbi, float)):
                continue
            pool = by_sp.get(row.tax_species_ncbi, np.array([], dtype=object))
        adm = np.array([h for h in pool if h not in tp], dtype=object)
        if len(adm) < N_DECOY:
            continue
        pick = rng.choice(len(adm), size=N_DECOY, replace=False)
        keep.append(qi)
        cands.append([row.nc_row] + [h2r[adm[i]] for i in pick])
    return np.array(keep, dtype=int), np.array(cands, dtype=int)


# ------------------------------------------------------------------ scoring and MRR
def mrr_from_scores(S: np.ndarray) -> np.ndarray:
    """PRIMARY, as pre-registered: pessimistic ties, rank = 1 + #(decoy >= true)."""
    better = (S[:, 1:] >= S[:, [0]]).sum(axis=1)
    return 1.0 / (1.0 + better)


def mrr_expected(S: np.ndarray) -> np.ndarray:
    """Expected rank under random tie-breaking: rank = 1 + #(>) + #(=)/2.

    WHY THIS EXISTS, declared when it was added and before the test fold was opened. The
    pre-registered pessimistic convention is conservative for a scorer with distinct values,
    but it is severely and ARTIFICIALLY punitive for a scorer that produces mass ties - which
    is exactly what the marginal baselines do (`B-pop` is an integer count, `B-model` is one
    probability per detection-model label, so dozens of candidates share a value). On
    validation both sat at 0.0200, BELOW the 0.0900 chance floor, which is a tie artefact and
    not a statement about the baseline's information content.

    That bias runs in the dangerous direction: it depresses the baselines and therefore
    FLATTERS the cross-modal model in the stop-rule comparison. The pre-registered metric stays
    primary and is not replaced; this is reported beside it for every model and rung, and the
    stop rule is evaluated under BOTH. If the two disagree, that is a reported finding, not a
    choice to be made after the fact.
    """
    gt = (S[:, 1:] > S[:, [0]]).sum(axis=1)
    eq = (S[:, 1:] == S[:, [0]]).sum(axis=1)
    return 1.0 / (1.0 + gt + eq / 2.0)


def score_latent(A, B, q_rt_rows, cand_nc_rows):
    """Cosine in the shared latent space; A,B already L2-normalised."""
    return np.einsum("qd,qcd->qc", A[q_rt_rows], B[cand_nc_rows])


# ------------------------------------------------------------------ component inference
def component_mrr(rr: np.ndarray, comp: np.ndarray) -> pd.Series:
    return pd.Series(rr).groupby(comp).mean()


def bootstrap_ci(cm: pd.Series, n_boot: int = 10_000, seed: int = SEED):
    """95% CI by resampling COMPONENTS, never pairs. Components are the inference unit."""
    rng = np.random.default_rng(seed)
    v = cm.values
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    means = v[idx].mean(axis=1)
    return float(v.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def paired_diff_ci(cm_a: pd.Series, cm_b: pd.Series, n_boot: int = 10_000, seed: int = SEED):
    """Bootstrap the PAIRED per-component difference a - b. This is the stop-rule statistic."""
    common = cm_a.index.intersection(cm_b.index)
    d = (cm_a.loc[common] - cm_b.loc[common]).values
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n_boot, len(d)))
    means = d[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi), float((hi - lo) / 2)


def permutation_null(A, B, q_rt_rows, cand_nc_rows, comp, fold_nc_rows,
                     n_perm: int = 2_000, seed: int = SEED):
    """rung 0F. The 'true' partner is replaced by a random ncRNA from the fold, keeping the
    same 49 decoys. This is the pair table permuted within block: if the score carries no
    pairing information the observed statistic sits inside this null."""
    rng = np.random.default_rng(seed)
    n = len(q_rt_rows)
    obs = component_mrr(mrr_from_scores(score_latent(A, B, q_rt_rows, cand_nc_rows)), comp).mean()
    null = np.empty(n_perm)
    for b in range(n_perm):
        fake = rng.choice(fold_nc_rows, size=n, replace=True)
        C = cand_nc_rows.copy()
        C[:, 0] = fake
        null[b] = component_mrr(mrr_from_scores(score_latent(A, B, q_rt_rows, C)), comp).mean()
    p = float((null >= obs).sum() + 1) / (n_perm + 1)
    return float(obs), null, p
