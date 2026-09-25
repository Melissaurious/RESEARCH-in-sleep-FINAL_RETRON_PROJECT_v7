#!/usr/bin/env python
"""embed_g2/a03 - trivial baselines, then the M-CCA grid, evaluated on VALIDATION ONLY.

Trivial baselines run FIRST, per LAUNCHER §7d. The ONE quantity selected here is the M-CCA
configuration, by the single predeclared rule: maximise validation rung-1 MRR over the 9-point
grid k in {16,32,64} x alpha in {1e-2,1e-1,1}. Nothing else is selected on validation - not the
negatives, not the metric, not a threshold.

TEST IS NOT OPENED BY THIS SCRIPT.
"""
from __future__ import annotations

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a02_engine import (CHANCE_MRR, RUNGS, SEED, build_candidates, component_mrr,  # noqa: E402
                        fit_rcca, mrr_from_scores, project)

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
ROOT = TASK.parents[1]
GRID_K = [16, 32, 64]
GRID_A = [1e-2, 1e-1, 1e0]
AA = "ACDEFGHIKLMNPQRSTVWY"
NT = "ACGT"


def read_fasta(p):
    s, sid, buf = {}, None, []
    for l in p.read_text().splitlines():
        if l.startswith(">"):
            if sid: s[sid] = "".join(buf)
            sid, buf = l[1:].split()[0], []
        else: buf.append(l.strip())
    if sid: s[sid] = "".join(buf)
    return s


def dipeptide(seqs, order):
    idx = {a + b: i for i, (a, b) in enumerate(itertools.product(AA, AA))}
    M = np.zeros((len(order), 400), dtype=np.float32)
    for r, h in enumerate(order):
        s = seqs[h]
        c = Counter(s[i:i + 2] for i in range(len(s) - 1))
        for k, v in c.items():
            j = idx.get(k)
            if j is not None:
                M[r, j] = v
        n = M[r].sum()
        if n: M[r] /= n
    return M


def kmer4(seqs, order):
    idx = {"".join(t): i for i, t in enumerate(itertools.product(NT, repeat=4))}
    M = np.zeros((len(order), 256), dtype=np.float32)
    for r, h in enumerate(order):
        s = seqs[h]
        c = Counter(s[i:i + 4] for i in range(len(s) - 3))
        for k, v in c.items():
            j = idx.get(k)
            if j is not None:
                M[r, j] = v
        n = M[r].sum()
        if n: M[r] /= n
    return M


def ridge(X, Y, lam=1.0):
    Xc, Yc = X - X.mean(0), Y - Y.mean(0)
    Wt = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1], dtype=X.dtype), Xc.T @ Yc)
    return dict(mx=X.mean(0), my=Y.mean(0), W=Wt)


def ridge_pred(m, X):
    return (X - m["mx"]) @ m["W"] + m["my"]


def build_scorers(tr, RT, NC, rt_dip, nc_k4, nc_len_row, nc_gc_row):
    """Every scorer maps (query rt rows, candidate nc rows) -> score matrix."""
    sc = {}

    # --- B-pop : ncRNA-only marginal (training frequency of the candidate)
    cnt = np.zeros(NC.shape[0], dtype=np.float32)
    for r, c in Counter(tr.nc_row.values).items():
        cnt[r] = c
    pop = np.log1p(cnt)
    sc["B-pop"] = lambda q, C: pop[C]

    # --- B-len : predicted ncRNA length from RT length
    ml = ridge(tr.rt_aa_len.values.reshape(-1, 1).astype(np.float32),
               tr.nc_len.values.reshape(-1, 1).astype(np.float32), lam=1.0)
    rt_len_row = np.zeros(RT.shape[0], dtype=np.float32)
    rt_len_row[tr.rt_row.values] = tr.rt_aa_len.values
    def s_len(q, C, ml=ml):
        pred = ridge_pred(ml, rt_len_row[q].reshape(-1, 1))
        return -np.abs(nc_len_row[C] - pred)
    sc["B-len"] = s_len

    # --- B-gc : predicted ncRNA GC from RT length
    mg = ridge(tr.rt_aa_len.values.reshape(-1, 1).astype(np.float32),
               tr.nc_gc.values.reshape(-1, 1).astype(np.float32), lam=1.0)
    def s_gc(q, C, mg=mg):
        pred = ridge_pred(mg, rt_len_row[q].reshape(-1, 1))
        return -np.abs(nc_gc_row[C] - pred)
    sc["B-gc"] = s_gc

    # --- B-kmer : RT dipeptide -> ncRNA 4-mer, cosine
    mk = ridge(rt_dip[tr.rt_row.values], nc_k4[tr.nc_row.values], lam=1.0)
    K = nc_k4 / np.maximum(np.linalg.norm(nc_k4, axis=1, keepdims=True), 1e-9)
    def s_kmer(q, C, mk=mk):
        P = ridge_pred(mk, rt_dip[q])
        P /= np.maximum(np.linalg.norm(P, axis=1, keepdims=True), 1e-9)
        return np.einsum("qd,qcd->qc", P, K[C])
    sc["B-kmer"] = s_kmer

    # --- B-model : RT-only marginal / label shortcut
    from sklearn.linear_model import LogisticRegression
    labs = sorted(tr.detection_model.unique())
    li = {m: i for i, m in enumerate(labs)}
    # sklearn >=1.8 removed `multi_class`; multinomial is the default for multiclass targets.
    clf = LogisticRegression(max_iter=1000, C=1.0)
    clf.fit(RT[tr.rt_row.values], tr.detection_model.map(li).values)
    nc_lab = np.full(NC.shape[0], -1, dtype=int)
    for r, m in zip(tr.nc_row.values, tr.detection_model.map(li).values):
        nc_lab[r] = m
    def s_model(q, C, clf=clf):
        P = clf.predict_proba(RT[q])
        lab = nc_lab[C]
        out = np.zeros(C.shape, dtype=np.float32)
        ok = lab >= 0
        rows = np.repeat(np.arange(C.shape[0])[:, None], C.shape[1], axis=1)
        out[ok] = P[rows[ok], lab[ok]]
        return out
    sc["B-model"] = s_model
    return sc


def evaluate(scorer, q_rows, cands, comp):
    rr = mrr_from_scores(scorer(q_rows, cands))
    cm = component_mrr(rr, comp)
    return float(cm.mean()), cm, rr


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(W / "analysis_pairs.parquet")
    RT = np.load(W / "rt_pooled.npy"); NC = np.load(W / "nc_pooled.npy")
    tp = pd.read_pickle(W / "true_partners.pkl")
    tr, va = df[df.fold == "train"], df[df.fold == "val"]
    print(f"train {len(tr):,} pairs / {tr.component_id.nunique()} comps   "
          f"val {len(va):,} / {va.component_id.nunique()} comps   chance MRR {CHANCE_MRR:.4f}")

    rt_seqs = read_fasta(ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa")
    nc_seqs = read_fasta(ROOT / "data/derived/rt_ncrna_oriented_v1.fna")
    rt_order = df.drop_duplicates("rt_row").sort_values("rt_row").rt_seq_hash.tolist()
    nc_order = df.drop_duplicates("nc_row").sort_values("nc_row").nc_seq_hash.tolist()
    assert rt_order == [h for h in rt_order] and len(rt_order) == RT.shape[0]
    print("  building composition features ...", flush=True)
    rt_dip = dipeptide(rt_seqs, rt_order)
    nc_k4 = kmer4(nc_seqs, nc_order)
    nc_len_row = np.zeros(NC.shape[0], dtype=np.float32)
    nc_gc_row = np.zeros(NC.shape[0], dtype=np.float32)
    u = df.drop_duplicates("nc_row")
    nc_len_row[u.nc_row.values] = u.nc_len.values
    nc_gc_row[u.nc_row.values] = u.nc_gc.values

    print("\n[1] validation candidate sets (seeded, identical for every scorer)")
    cand = {}
    for rung in RUNGS:
        rng = np.random.default_rng(SEED)
        keep, C = build_candidates(va, va, tp, rung, rng)
        cand[rung] = (keep, C)
        print(f"    {rung:<18} {len(keep):>5,}/{len(va):,} queries usable "
              f"({100*len(keep)/len(va):5.1f}%)", flush=True)

    print("\n[2] trivial baselines (run BEFORE the cross-modal model)")
    scorers = build_scorers(tr, RT, NC, rt_dip, nc_k4, nc_len_row, nc_gc_row)
    rows = []
    for name, fn in scorers.items():
        for rung in RUNGS:
            keep, C = cand[rung]
            if len(keep) < 50:
                continue
            m, _, _ = evaluate(fn, va.rt_row.values[keep], C, va.component_id.values[keep])
            rows.append(dict(model=name, rung=rung, val_mrr=round(m, 4), n_queries=len(keep)))
        print(f"    {name:<9} rung1 MRR "
              f"{[r['val_mrr'] for r in rows if r['model']==name and r['rung']=='rung1_random'][0]:.4f}")

    print("\n[3] M-CCA grid on train -> validation (9 configs, ONE selection rule)")
    Xtr, Ytr = RT[tr.rt_row.values], NC[tr.nc_row.values]
    keep1, C1 = cand["rung1_random"]
    grid = []
    for k, a in itertools.product(GRID_K, GRID_A):
        mdl = fit_rcca(Xtr, Ytr, k, a)
        A, B = project(mdl, RT, NC)
        m, _, _ = evaluate(lambda q, C, A=A, B=B: np.einsum("qd,qcd->qc", A[q], B[C]),
                           va.rt_row.values[keep1], C1, va.component_id.values[keep1])
        grid.append(dict(k=k, alpha=a, val_rung1_mrr=round(m, 4),
                         mean_canon_corr=round(float(mdl["corrs"].mean()), 4)))
        print(f"    k={k:<3} alpha={a:<6} val rung1 MRR {m:.4f}  "
              f"mean canonical corr {mdl['corrs'].mean():.3f}", flush=True)
    g = pd.DataFrame(grid)
    best = g.sort_values(["val_rung1_mrr", "k"], ascending=[False, True]).iloc[0]
    print(f"\n  SELECTED (max validation rung-1 MRR): k={int(best.k)} alpha={best.alpha} "
          f"-> {best.val_rung1_mrr:.4f}")

    # full validation ladder for the selected configuration, for the record
    mdl = fit_rcca(Xtr, Ytr, int(best.k), float(best.alpha))
    A, B = project(mdl, RT, NC)
    for rung in RUNGS:
        keep, C = cand[rung]
        if len(keep) < 50:
            continue
        m, _, _ = evaluate(lambda q, Cc, A=A, B=B: np.einsum("qd,qcd->qc", A[q], B[Cc]),
                           va.rt_row.values[keep], C, va.component_id.values[keep])
        rows.append(dict(model="M-CCA", rung=rung, val_mrr=round(m, 4), n_queries=len(keep)))

    pd.DataFrame(rows).to_csv(OUT / "g2_validation_ladder.tsv", sep="\t", index=False)
    g.to_csv(OUT / "g2_cca_grid.tsv", sep="\t", index=False)
    (W / "selected_config.json").write_text(json.dumps(
        {"k": int(best.k), "alpha": float(best.alpha),
         "selection_rule": "max validation rung-1 MRR over the predeclared 9-point grid",
         "val_rung1_mrr": float(best.val_rung1_mrr),
         "frozen": True, "test_opened": False}, indent=2) + "\n")
    print(f"\nwrote g2_validation_ladder.tsv, g2_cca_grid.tsv, selected_config.json")
    print("TEST NOT OPENED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
