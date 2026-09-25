#!/usr/bin/env python
"""embed_g2/a05 - descriptive embedding atlas. CHARACTERIZATION OF A COMPLETED EXPERIMENT.

This is not a model-selection stage and not a new gate. Nothing is fitted to improve a
metric; the M-CCA configuration is the one already frozen in embed_g2 (k=32, alpha=0.01,
fit on training components) and is reused unchanged.

TERMINOLOGY, used consistently in every output of this script:
    observed pair / natural pair   an RT-ncRNA pair recorded in the corpus
    mismatched candidate           a candidate that is not the observed partner
    retrieval decoy                a mismatched candidate placed in a retrieval candidate set
    non-observed pairing           an RT-ncRNA combination not seen in the corpus
    type-matched decoy             a retrieval decoy sharing the query's retron type

A mismatched candidate is NOT a "negative pair" and NOT an "incompatible pair". Nothing here
has been experimentally shown to be incompatible; absence from the corpus is absence of
observation, not evidence of incompatibility.

Probes in section 7 are fit on TRAIN, tuned on nothing, and reported on TEST. They are
explanatory, not an escalation gate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a02_engine import RUNGS, SEED, build_candidates, fit_rcca, project  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
W, OUT, PLOT = TASK / "work", TASK / "tables", TASK / "plotdata"
SEED_ATLAS = 20260918
SUBSAMPLE = 8000          # atlas points per modality, for readable panels and tractable UMAP


def umap2(X, seed=SEED_ATLAS):
    import umap
    return umap.UMAP(n_neighbors=30, min_dist=0.25, metric="cosine",
                     random_state=seed).fit_transform(X)


def main() -> int:
    for d in (OUT, PLOT):
        d.mkdir(parents=True, exist_ok=True)
    from sklearn.decomposition import PCA

    df = pd.read_parquet(W / "analysis_pairs.parquet")
    RT = np.load(W / "rt_pooled.npy"); NC = np.load(W / "nc_pooled.npy")
    tp = pd.read_pickle(W / "true_partners.pkl")
    cfg = json.loads((W / "selected_config.json").read_text())
    tr, te = df[df.fold == "train"], df[df.fold == "test"]
    rng = np.random.default_rng(SEED_ATLAS)

    # the frozen M-CCA, refit exactly as in embed_g2 - same config, same training components
    mdl = fit_rcca(RT[tr.rt_row.values], NC[tr.nc_row.values], cfg["k"], cfg["alpha"])
    A, B = project(mdl, RT, NC)
    print(f"[0] frozen M-CCA k={cfg['k']} alpha={cfg['alpha']}; "
          f"canonical corrs {mdl['corrs'][0]:.3f}..{mdl['corrs'][-1]:.3f}")

    # ---- per-sequence metadata (a sequence can occur in several pairs; take the mode) ------
    rtm = (df.groupby("rt_row")
             .agg(retron_type=("detection_model", lambda s: s.mode().iat[0]),
                  fold=("fold", lambda s: s.mode().iat[0]),
                  rt_aa_len=("rt_aa_len", "first"),
                  species=("tax_species_ncbi", lambda s: s.dropna().mode().iat[0]
                           if s.notna().any() else None),
                  T3=("T3", "max"), T4=("T4", "max"), T1=("T1", "max"), T2=("T2", "max"),
                  rt_cluster=("rt_cluster", lambda s: s.mode().iat[0])).reset_index())
    ncm = (df.groupby("nc_row")
             .agg(retron_type=("detection_model", lambda s: s.mode().iat[0]),
                  fold=("fold", lambda s: s.mode().iat[0]),
                  nc_len=("nc_len", "first"), nc_gc=("nc_gc", "first"),
                  species=("tax_species_ncbi", lambda s: s.dropna().mode().iat[0]
                           if s.notna().any() else None),
                  T3=("T3", "max"), T4=("T4", "max"), T1=("T1", "max"), T2=("T2", "max"),
                  nc_cluster=("nc_cluster", lambda s: s.mode().iat[0])).reset_index())
    print(f"[1] {len(rtm):,} unique RT, {len(ncm):,} unique ncRNA; "
          f"{df.detection_model.nunique()} retron types")

    # ---- 1 & 2 : per-modality atlases ------------------------------------------------------
    print("[2] per-modality PCA + UMAP")
    for tag, M, meta in (("rt", RT, rtm), ("ncrna", NC, ncm)):
        idx = meta[f"{tag if tag=='rt' else 'nc'}_row"].values
        sub = rng.choice(len(idx), size=min(SUBSAMPLE, len(idx)), replace=False)
        sel = idx[np.sort(sub)]
        p = PCA(n_components=10, random_state=SEED_ATLAS).fit(M)
        P = p.transform(M[sel])
        U = umap2(M[sel])
        out = meta.iloc[np.sort(sub)].copy()
        out["pc1"], out["pc2"] = P[:, 0], P[:, 1]
        out["umap1"], out["umap2"] = U[:, 0], U[:, 1]
        out.to_csv(PLOT / f"atlas_{tag}.tsv", sep="\t", index=False)
        pd.DataFrame({"pc": np.arange(1, 11),
                      "explained_variance_ratio": p.explained_variance_ratio_}).to_csv(
            OUT / f"g2a_pca_variance_{tag}.tsv", sep="\t", index=False)
        print(f"    {tag}: {len(sel):,} points; PC1-2 explain "
              f"{100*p.explained_variance_ratio_[:2].sum():.1f}%")

    # ---- 3 : shared CCA-space atlas --------------------------------------------------------
    print("[3] shared CCA-space atlas")
    pair_sub = te.sample(n=min(1200, len(te)), random_state=SEED_ATLAS)
    joint = np.vstack([A[pair_sub.rt_row.values], B[pair_sub.nc_row.values]])
    JU = umap2(joint)
    n = len(pair_sub)
    shared = pd.concat([
        pd.DataFrame(dict(modality="RT", retron_type=pair_sub.retron_type_x
                          if "retron_type_x" in pair_sub else pair_sub.detection_model.values,
                          pair_id=np.arange(n), x=JU[:n, 0], y=JU[:n, 1])),
        pd.DataFrame(dict(modality="ncRNA", retron_type=pair_sub.detection_model.values,
                          pair_id=np.arange(n), x=JU[n:, 0], y=JU[n:, 1]))])
    shared.to_csv(PLOT / "atlas_shared_cca.tsv", sep="\t", index=False)
    print(f"    {n:,} observed pairs sampled from the test fold "
          f"({2*n:,} points, line segments join observed partners)")

    # ---- 4 : cross-modal similarity distributions ------------------------------------------
    print("[4] similarity: observed pairs vs retrieval decoys")
    obs = np.einsum("qd,qd->q", A[te.rt_row.values], B[te.nc_row.values])
    dist_rows, sim_long = [], [("observed_pair", obs)]
    for rung, label in (("rung1_random", "random_decoy"),
                        ("rung2_len_gc", "length_gc_matched_decoy"),
                        ("rung3_model", "type_matched_decoy")):
        r = np.random.default_rng(SEED)
        keep, C = build_candidates(te, te, tp, rung, r)
        d = np.einsum("qd,qcd->qc", A[te.rt_row.values[keep]], B[C[:, 1:]]).ravel()
        sim_long.append((label, d))
    for label, v in sim_long:
        dist_rows.append(dict(population=label, n=len(v), mean=round(float(v.mean()), 4),
                              sd=round(float(v.std()), 4),
                              **{f"q{q}": round(float(np.percentile(v, q)), 4)
                                 for q in (5, 25, 50, 75, 95)}))
    base = {r["population"]: r for r in dist_rows}
    for r in dist_rows:
        if r["population"] == "observed_pair":
            r["cohens_d_vs_observed"] = 0.0
            continue
        o = base["observed_pair"]
        sp = np.sqrt((o["sd"] ** 2 + r["sd"] ** 2) / 2)
        r["cohens_d_vs_observed"] = round((o["mean"] - r["mean"]) / sp, 3) if sp else None
    pd.DataFrame(dist_rows).to_csv(OUT / "g2a_similarity_distributions.tsv", sep="\t", index=False)
    pd.DataFrame({"population": np.concatenate([[l] * len(v) for l, v in sim_long]),
                  "cosine": np.concatenate([v for _, v in sim_long])}).sample(
        n=60000, random_state=SEED_ATLAS).to_csv(PLOT / "similarity_long.tsv",
                                                 sep="\t", index=False)
    for r in dist_rows:
        print(f"    {r['population']:<26} mean {r['mean']:+.4f}  "
              f"Cohen's d vs observed {r['cohens_d_vs_observed']}")

    # ---- 5 : neighbourhood analysis ---------------------------------------------------------
    print("[5] neighbourhood structure in the shared space")
    te_nc = te.drop_duplicates("nc_row")
    NCsub, nc_rows = B[te_nc.nc_row.values], te_nc.nc_row.values
    # np.asarray(..., object): these columns are Arrow-backed, and an ArrowStringArray cannot
    # be indexed with the 2-D neighbour-order matrix below.
    nc_type = np.asarray(te_nc.detection_model.values, dtype=object)
    S = A[te.rt_row.values] @ NCsub.T
    order = np.argsort(-S, axis=1)
    true_col = {r: i for i, r in enumerate(nc_rows)}
    tcol = np.array([true_col[r] for r in te.nc_row.values])
    rank_of_true = (S > S[np.arange(len(S)), tcol][:, None]).sum(1) + 1
    q_type = np.asarray(te.detection_model.values, dtype=object)
    nb = dict(
        n_queries=len(S), pool_size=len(nc_rows),
        observed_partner_is_nearest=round(float((rank_of_true == 1).mean()), 4),
        observed_partner_in_top5=round(float((rank_of_true <= 5).mean()), 4),
        observed_partner_in_top10=round(float((rank_of_true <= 10).mean()), 4),
        median_rank_of_observed_partner=int(np.median(rank_of_true)),
        nearest_neighbour_shares_retron_type=round(
            float((nc_type[order[:, 0]] == q_type).mean()), 4),
        top10_fraction_sharing_retron_type=round(
            float((nc_type[order[:, :10]] == q_type[:, None]).mean()), 4),
        type_prevalence_in_pool=round(float(pd.Series(nc_type).value_counts(normalize=True)
                                            .reindex(pd.Series(q_type)).mean()), 4))
    nb["neighbourhood_is_type_specific_not_pair_specific"] = (
        nb["top10_fraction_sharing_retron_type"] > 0.5
        and nb["observed_partner_is_nearest"] < 0.5)
    (OUT / "g2a_neighbourhood.json").write_text(json.dumps(nb, indent=2) + "\n")
    for k, v in nb.items():
        print(f"    {k}: {v}")

    # ---- 6 : CCA dimension characterization -------------------------------------------------
    print("[6] canonical dimensions")
    corrs = mdl["corrs"]
    Atr, Btr = A[te.rt_row.values], B[te.nc_row.values]
    dim_rows = []
    for j in range(cfg["k"]):
        a, b = Atr[:, j], Btr[:, j]
        row = dict(dim=j + 1, canonical_corr=round(float(corrs[j]), 4),
                   share_of_total_corr=round(float(corrs[j] / corrs.sum()), 4),
                   cum_share=round(float(corrs[:j + 1].sum() / corrs.sum()), 4))
        for name, v in (("rt_len", te.rt_aa_len.values), ("nc_len", te.nc_len.values),
                        ("nc_gc", te.nc_gc.values)):
            row[f"corr_rtdim_{name}"] = round(float(np.corrcoef(a, v)[0, 1]), 3)
        # eta^2 of retron type on each modality's dimension j
        for tag, vec in (("rt", a), ("nc", b)):
            g = pd.Series(vec).groupby(te.detection_model.values)
            ss_b = float(((g.mean() - vec.mean()) ** 2 * g.size()).sum())
            ss_t = float(((vec - vec.mean()) ** 2).sum())
            row[f"eta2_retron_type_{tag}"] = round(ss_b / ss_t, 4) if ss_t else None
        dim_rows.append(row)
    pd.DataFrame(dim_rows).to_csv(OUT / "g2a_cca_dimensions.tsv", sep="\t", index=False)
    d1 = dim_rows[0]
    print(f"    dim1 corr {d1['canonical_corr']}, eta2(type) RT {d1['eta2_retron_type_rt']} "
          f"nc {d1['eta2_retron_type_nc']}; top-5 dims carry "
          f"{dim_rows[4]['cum_share']:.1%} of summed canonical correlation")

    # ---- 7 : modality-specific retron-type encoding ------------------------------------------
    print("[7] retron-type information present independently in each modality")
    from sklearn.linear_model import LogisticRegression
    enc = []
    for tag, M, col in (("ESM-C RT", RT, "rt_row"), ("RiNALMo ncRNA", NC, "nc_row")):
        Xtr, ytr = M[tr[col].values], tr.detection_model.values
        Xte, yte = M[te[col].values], te.detection_model.values
        clf = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr, ytr)
        acc = float((clf.predict(Xte) == yte).mean())
        maj = float(pd.Series(ytr).value_counts(normalize=True).iloc[0])
        enc.append(dict(modality=tag, probe="multinomial logistic on frozen pooled embedding",
                        fit_on="train components", reported_on="test components",
                        n_classes=int(pd.Series(ytr).nunique()),
                        test_accuracy=round(acc, 4),
                        majority_class_rate=round(maj, 4),
                        accuracy_above_majority=round(acc - maj, 4)))
        print(f"    {tag:<14} type accuracy {acc:.4f} (majority {maj:.4f})")
    pd.DataFrame(enc).to_csv(OUT / "g2a_type_encoding.tsv", sep="\t", index=False)

    print("\nwrote atlas plot tables to plotdata/ and descriptive tables to tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
