#!/usr/bin/env python
"""embed_x2/y05 - relatedness, taxonomy and deposition sensitivity strata (spec section 10).

The question this answers is NOT "is the effect bigger somewhere". It is: does the
cross-fitted R - T advantage survive when the strata that could manufacture it are held
down? The six axes are fixed here and each is a property of the pair that was decided
upstream of any X2 model output:

  A  retron_type              does one type carry the whole effect?
  B  rt_homolog_group_size    is it only large, heavily sampled RT clusters?
  C  train_similarity         how close is this pair's RT to the nearest RT the evaluating
                              model actually saw in training (cosine on the frozen pooled
                              ESM-C cache)? This is the relatedness axis: if the advantage
                              lived only in the top bin, it would be residual relatedness,
                              not RT-specific information.
  D  ncrna_cluster_size       is it only ncRNA families with many members?
  E  taxonomy                 species breadth of the pair's observations (n_species from the
                              frozen recurrence table), plus the recurrence class itself.
  F  deposition_multiplicity  n_physical_loci: repeated deposition vs repeated event.

Every stratum is reported as a paired per-component contrast with a component-level
bootstrap, and any stratum spanning fewer than MIN_COMP independent components is reported
UNDETERMINED rather than as a null (X2-D discipline). Strata are NOT used to pick a headline
number; the primary endpoint stays the pooled estimate from y04.
"""
from __future__ import annotations
import collections, gzip, sys
from pathlib import Path
import numpy as np, pandas as pd

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
ROOT = TASK.parents[1]
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
SPLIT = ROOT / "results" / "embed_g2b_frozen_split"
POOLED = ROOT / "ARIS_OUTPUT" / "embed_g2_analysis" / "work" / "rt_pooled.npy"

K, N_BOOT, MIN_COMP, SEED = 5, 10_000, 30, 20260918
CONTRASTS = (("R", "T"), ("R", "G"))


def comp_mean(nll_sum, n_tok, comp):
    s, t = collections.defaultdict(float), collections.defaultdict(float)
    for v, n, c in zip(nll_sum, n_tok, comp):
        s[c] += v; t[c] += n
    ks = sorted(s)
    return np.array(ks), np.array([s[k] / t[k] for k in ks])


def paired(ka, a, kb, b, seed=SEED, n=N_BOOT):
    common = np.intersect1d(ka, kb)
    if len(common) == 0:
        return None
    d = a[np.searchsorted(ka, common)] - b[np.searchsorted(kb, common)]
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(n, len(d)))].mean(1)
    return dict(n_components=int(len(d)), diff=round(float(d.mean()), 6),
                median=round(float(np.median(d)), 6),
                ci_lo=round(float(np.percentile(m, 2.5)), 6),
                ci_hi=round(float(np.percentile(m, 97.5)), 6),
                frac_components_favouring_first=round(float((d < 0).mean()), 4),
                status="OK" if len(d) >= MIN_COMP else "UNDETERMINED")


def load_oof(n):
    oof = {}
    for arm in ("U", "T", "G", "R", "P"):
        s = np.full(n, np.nan); t = np.full(n, np.nan)
        for f in range(K):
            z = np.load(W / f"oof_{arm}_f{f}.npz")
            s[z["idx"]] = z["nll_sum"]; t[z["idx"]] = z["n_tok"]
        assert not np.isnan(s).any(), f"{arm} incomplete"
        oof[arm] = (s, t)
    return oof


def bin_counts(v, edges, labels):
    out = np.empty(len(v), dtype=object)
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        out[(v >= lo) & (v < hi)] = labels[i]
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(W / "dataset.npz", allow_pickle=False)
    cv = np.load(W / "crossfit.npz", allow_pickle=False)
    comp, fold, rt_rep = d["component"], cv["cv_fold"], cv["rt_rep"]
    n = len(comp)
    oof = load_oof(n)
    asg = pd.read_csv(gzip.open(SPLIT / "tables" / "split_assignment.tsv.gz"), sep="\t")
    assert len(asg) == n

    print("[1] building the six stratification axes")
    strata = {}

    # A - retron type ---------------------------------------------------------------
    strata["A_retron_type"] = d["retron_type"].astype(object)

    # B - RT homolog group size (frozen rt_id0.50 clusters) --------------------------
    cs = pd.Series(rt_rep).value_counts()
    v = pd.Series(rt_rep).map(cs).values.astype(float)
    strata["B_rt_homolog_group_size"] = bin_counts(
        v, [1, 2, 6, 21, 101, np.inf], ["1", "2-5", "6-20", "21-100", ">100"])

    # C - similarity to the nearest RT the evaluating model saw in TRAINING ----------
    # Frozen pooled ESM-C (embed_g1), cosine. Computed per fold against that fold's own
    # training pairs, i.e. exactly what the model conditioning this pair had access to.
    pooled = np.load(POOLED).astype(np.float32)
    pooled /= np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)
    ix = [l.split("\t") for l in (W / "rt_chunk_index.tsv").read_text().splitlines()[1:]]
    rrow = {h: int(r) for h, r, _ in ix}
    rows_all = np.array([rrow[h] for h in d["rt_hash"]])
    sim = np.zeros(n, dtype=np.float32)
    for f in range(K):
        te = np.where(fold == f)[0]
        tr = np.where(~np.isin(fold, [f, (f + 1) % K]))[0]
        A = pooled[rows_all[te]]
        B = pooled[np.unique(rows_all[tr])]
        best = np.full(len(te), -1.0, dtype=np.float32)
        for k in range(0, len(te), 2048):
            best[k:k + 2048] = (A[k:k + 2048] @ B.T).max(1)
        sim[te] = best
        print(f"    fold {f}: nearest-train cosine  median {np.median(best):.4f}  "
              f"p05 {np.percentile(best, 5):.4f}  p95 {np.percentile(best, 95):.4f}")
    q = np.quantile(sim, [0, .25, .5, .75, 1.0])
    strata["C_train_similarity_quartile"] = bin_counts(
        sim, [q[0] - 1e-6, q[1], q[2], q[3], np.inf],
        [f"Q1_<{q[1]:.3f}", f"Q2_{q[1]:.3f}-{q[2]:.3f}",
         f"Q3_{q[2]:.3f}-{q[3]:.3f}", f"Q4_>={q[3]:.3f}"])

    # D - ncRNA cluster size ---------------------------------------------------------
    ncs = asg.nc_cluster.value_counts()
    strata["D_ncrna_cluster_size"] = bin_counts(
        asg.nc_cluster.map(ncs).values.astype(float),
        [1, 2, 6, 21, 101, np.inf], ["1", "2-5", "6-20", "21-100", ">100"])

    # E/F - taxonomy and deposition, from the frozen canonical recurrence table -------
    # Joined row-for-row against split_assignment by (rt_seq_hash, nc_seq_hash) in
    # work/recurrence_join.tsv.gz, from the frozen canonical
    # rt_ncrna_exact_pair_recurrence_v1.parquet. Extracted in the retron_tradicional env
    # because the GPU env has no pyarrow; 30,924/30,924 pairs matched.
    got = pd.read_csv(W / "recurrence_join.tsv.gz", sep="\t")
    assert len(got) == n, "recurrence join is not row-aligned with the split assignment"
    print(f"    recurrence join: {int(got.n_species.notna().sum()):,}/{n:,} pairs matched")
    nsp = got.n_species.fillna(-1).values.astype(float)
    strata["E_taxonomy_n_species"] = bin_counts(
        nsp, [-1, 0, 1, 2, 3, 6, np.inf],
        ["unmatched", "0", "1", "2", "3-5", ">=6"])
    strata["E_recurrence_class"] = got.recurrence_class.fillna("unmatched").values.astype(object)
    nloc = got.n_physical_loci.fillna(-1).values.astype(float)
    strata["F_deposition_n_physical_loci"] = bin_counts(
        nloc, [-1, 0, 1, 2, 3, 6, 21, np.inf],
        ["unmatched", "0", "1", "2", "3-5", "6-20", ">=21"])

    print("\n[2] stratified paired contrasts (negative = R better)")
    rows = []
    for axis, lab in strata.items():
        lab = np.array([("NA" if x is None else str(x)) for x in lab], dtype=object)
        for level in sorted(set(lab)):
            m = lab == level
            if m.sum() == 0:
                continue
            for a, b in CONTRASTS:
                ka, va = comp_mean(oof[a][0][m], oof[a][1][m], comp[m])
                kb, vb = comp_mean(oof[b][0][m], oof[b][1][m], comp[m])
                r = paired(ka, va, kb, vb)
                if r is None:
                    continue
                r.update(axis=axis, level=level, contrast=f"{a} - {b}",
                         pairs=int(m.sum()))
                rows.append(r)
        shown = [r for r in rows if r["axis"] == axis and r["contrast"] == "R - T"]
        print(f"  {axis}  ({len(shown)} levels)")
        for r in sorted(shown, key=lambda x: -x["pairs"])[:8]:
            print(f"    {r['level']:<22} {r['pairs']:>6,}p {r['n_components']:>4}c "
                  f"R-T {r['diff']:+.5f} [{r['ci_lo']:+.5f}, {r['ci_hi']:+.5f}] {r['status']}")

    df = pd.DataFrame(rows)[["axis", "level", "contrast", "pairs", "n_components", "diff",
                             "median", "ci_lo", "ci_hi",
                             "frac_components_favouring_first", "status"]]
    df.to_csv(OUT / "SENSITIVITY_STRATA.tsv", sep="\t", index=False)

    ok = df[(df.contrast == "R - T") & (df.status == "OK")]
    print(f"\n[3] {len(ok)} adjudicable R-T strata; "
          f"{int((ok.ci_hi < 0).sum())} with the whole 95% CI below zero, "
          f"{int((ok.ci_lo > 0).sum())} above zero, "
          f"{int(((ok.ci_lo <= 0) & (ok.ci_hi >= 0)).sum())} spanning zero")
    print(f"    direction consistency: {float((ok['diff'] < 0).mean()):.1%} of adjudicable "
          f"strata favour R")
    print(f"\nwrote {OUT / 'SENSITIVITY_STRATA.tsv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
