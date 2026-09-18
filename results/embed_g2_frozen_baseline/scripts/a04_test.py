#!/usr/bin/env python
"""embed_g2/a04 - THE CONFIRMATORY RUN. Opens the frozen test fold exactly once.

The M-CCA configuration was selected on validation by the pre-registered rule and is read from
work/selected_config.json. It is NOT re-selected here, and no quantity is tuned against
anything computed in this script.

Produces every deliverable the operator enumerated: natural-vs-random, the predeclared
matched-negative ladder, both marginal baselines, the cross-modal model, retrieval in both
directions, component-level uncertainty and permutation inference, the frozen near-duplicate
sensitivity population, and the T1-T4 strata.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a02_engine import (CHANCE_MRR, N_DECOY, RUNGS, SEED, bootstrap_ci,  # noqa: E402
                        build_candidates, component_mrr, fit_rcca, mrr_expected,
                        mrr_from_scores, paired_diff_ci, project)
from a03_validation import build_scorers, dipeptide, kmer4, read_fasta  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
ROOT = TASK.parents[1]


def summarise(name, rung, S, comp, extra=None):
    rr_p, rr_e = mrr_from_scores(S), mrr_expected(S)
    cm_p = component_mrr(rr_p, comp)
    cm_e = component_mrr(rr_e, comp)
    m, lo, hi = bootstrap_ci(cm_p)
    row = dict(model=name, rung=rung, n_queries=len(rr_p), n_components=int(cm_p.index.nunique()),
               mrr=round(m, 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
               mrr_expected_ties=round(float(cm_e.mean()), 4),
               top1=round(float((rr_p == 1.0).mean()), 4),
               top5=round(float((rr_p >= 1 / 5).mean()), 4))
    if extra:
        row.update(extra)
    return row, cm_p, cm_e


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((W / "selected_config.json").read_text())
    print(f"frozen config: k={cfg['k']} alpha={cfg['alpha']} "
          f"(selected on validation rung-1 MRR = {cfg['val_rung1_mrr']})")

    df = pd.read_parquet(W / "analysis_pairs.parquet")
    RT = np.load(W / "rt_pooled.npy"); NC = np.load(W / "nc_pooled.npy")
    tp = pd.read_pickle(W / "true_partners.pkl")
    tr, te = df[df.fold == "train"], df[df.fold == "test"]
    assert len(te) == 4638 and te.component_id.nunique() == 357
    print(f"TEST fold OPENED: {len(te):,} pairs / {te.component_id.nunique()} components "
          f"(n_eff 14.1)   chance MRR {CHANCE_MRR:.4f}")

    rt_seqs = read_fasta(ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa")
    nc_seqs = read_fasta(ROOT / "data/derived/rt_ncrna_oriented_v1.fna")
    rt_order = df.drop_duplicates("rt_row").sort_values("rt_row").rt_seq_hash.tolist()
    nc_order = df.drop_duplicates("nc_row").sort_values("nc_row").nc_seq_hash.tolist()
    rt_dip, nc_k4 = dipeptide(rt_seqs, rt_order), kmer4(nc_seqs, nc_order)
    nc_len_row = np.zeros(NC.shape[0], np.float32); nc_gc_row = np.zeros(NC.shape[0], np.float32)
    u = df.drop_duplicates("nc_row")
    nc_len_row[u.nc_row.values] = u.nc_len.values
    nc_gc_row[u.nc_row.values] = u.nc_gc.values

    print("\n[1] fit M-CCA on TRAINING components only")
    mdl = fit_rcca(RT[tr.rt_row.values], NC[tr.nc_row.values], cfg["k"], cfg["alpha"])
    A, B = project(mdl, RT, NC)
    scorers = build_scorers(tr, RT, NC, rt_dip, nc_k4, nc_len_row, nc_gc_row)
    scorers["M-CCA"] = lambda q, C: np.einsum("qd,qcd->qc", A[q], B[C])

    print("\n[2] test candidate ladder (seeded; identical sets for every model)")
    cand = {}
    for rung in RUNGS:
        rng = np.random.default_rng(SEED)
        keep, C = build_candidates(te, te, tp, rung, rng)
        cand[rung] = (keep, C)
        status = "OK" if len(keep) >= 200 else "INSUFFICIENT"
        print(f"    {rung:<18} {len(keep):>5,}/{len(te):,} usable "
              f"({100*len(keep)/len(te):5.1f}%)  {status}")

    print("\n[3] primary test ladder")
    rows, cms = [], {}
    for name, fn in scorers.items():
        for rung in RUNGS:
            keep, C = cand[rung]
            if len(keep) < 200:
                rows.append(dict(model=name, rung=rung, n_queries=len(keep), status="INSUFFICIENT"))
                continue
            S = fn(te.rt_row.values[keep], C)
            r, cm_p, _ = summarise(name, rung, S, te.component_id.values[keep],
                                   {"status": "OK"})
            rows.append(r); cms[(name, rung)] = cm_p
        print(f"    {name:<9} " + "  ".join(
            f"{r['rung'].split('_')[0]}={r.get('mrr','--')}"
            for r in rows if r["model"] == name))

    print("\n[4] stop rule: M-CCA vs the best trivial baseline (paired per component)")
    triv = [n for n in scorers if n.startswith("B-")]
    best_t = max(triv, key=lambda n: next((r["mrr"] for r in rows
                                           if r["model"] == n and r["rung"] == "rung1_random"
                                           and r.get("status") == "OK"), 0))
    stop_rows = []
    for rung in RUNGS:
        if ("M-CCA", rung) not in cms or (best_t, rung) not in cms:
            continue
        d, lo, hi, half = paired_diff_ci(cms[("M-CCA", rung)], cms[(best_t, rung)])
        stop_rows.append(dict(rung=rung, best_trivial=best_t, diff=round(d, 4),
                              ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                              half_width=round(half, 4),
                              passes_stop_rule=bool(d > half)))
        print(f"    {rung:<18} M-CCA - {best_t} = {d:+.4f} "
              f"[{lo:+.4f}, {hi:+.4f}]  half-width {half:.4f}  "
              f"{'PASS' if d > half else 'FAIL'}")

    print("\n[5] rung 0F failure control (permutation, 2000 draws)")
    keep, C = cand["rung1_random"]
    rng = np.random.default_rng(SEED)
    fold_nc = te.nc_row.unique()
    obs = component_mrr(mrr_from_scores(scorers["M-CCA"](te.rt_row.values[keep], C)),
                        te.component_id.values[keep]).mean()
    null = np.empty(2000)
    for b in range(2000):
        Cc = C.copy(); Cc[:, 0] = rng.choice(fold_nc, size=len(keep), replace=True)
        null[b] = component_mrr(mrr_from_scores(scorers["M-CCA"](te.rt_row.values[keep], Cc)),
                                te.component_id.values[keep]).mean()
    pval = float((null >= obs).sum() + 1) / 2001
    print(f"    observed {obs:.4f}   null mean {null.mean():.4f} "
          f"[{np.percentile(null,2.5):.4f}, {np.percentile(null,97.5):.4f}]   p = {pval:.5f}")

    print("\n[6] near-duplicate sensitivity population (FROZEN, 1,525 pairs)")
    sens_mask = te.in_sensitivity_population.values == 1
    sens_rows = []
    for rung in RUNGS:
        keep, C = cand[rung]
        sel = sens_mask[keep]
        if sel.sum() < 200:
            sens_rows.append(dict(rung=rung, n_queries=int(sel.sum()), status="INSUFFICIENT"))
            continue
        for name in ("M-CCA", best_t):
            S = scorers[name](te.rt_row.values[keep][sel], C[sel])
            r, _, _ = summarise(name, rung, S, te.component_id.values[keep][sel], {"status": "OK"})
            sens_rows.append(r)
    for r in sens_rows:
        if r.get("status") == "OK" and r["model"] == "M-CCA":
            print(f"    {r['rung']:<18} M-CCA {r['mrr']:.4f} "
                  f"[{r['ci_lo']:.4f},{r['ci_hi']:.4f}]  n={r['n_queries']:,}")

    print("\n[7] T1-T4 strata (descriptive, rung1)")
    keep, C = cand["rung1_random"]
    strata_rows = []
    S = scorers["M-CCA"](te.rt_row.values[keep], C)
    rr = mrr_from_scores(S)
    for t in ("T1", "T2", "T3", "T4"):
        m = te[t].values[keep] == 1
        if m.sum() < 100:
            strata_rows.append(dict(stratum=t, n=int(m.sum()), status="INSUFFICIENT")); continue
        cm = component_mrr(rr[m], te.component_id.values[keep][m])
        mu, lo, hi = bootstrap_ci(cm)
        strata_rows.append(dict(stratum=t, n=int(m.sum()), n_components=int(cm.index.nunique()),
                                mrr=round(mu, 4), ci_lo=round(lo, 4), ci_hi=round(hi, 4),
                                status="OK"))
        print(f"    {t}  n={int(m.sum()):>5,}  MRR {mu:.4f} [{lo:.4f}, {hi:.4f}]")

    print("\n[8] reverse direction (ncRNA -> RT), rung1 equivalent")
    rng = np.random.default_rng(SEED)
    rt_pool = te.drop_duplicates("rt_seq_hash")
    rt_h, rt_r = rt_pool.rt_seq_hash.values, rt_pool.rt_row.values
    h2r = dict(zip(rt_h, rt_r))
    partners_of_nc = te.groupby("nc_seq_hash").rt_seq_hash.apply(set).to_dict()
    keepr, Cr = [], []
    for qi, row in enumerate(te.itertuples(index=False)):
        adm = np.array([h for h in rt_h if h not in partners_of_nc.get(row.nc_seq_hash, set())],
                       dtype=object)
        if len(adm) < N_DECOY:
            continue
        pick = rng.choice(len(adm), size=N_DECOY, replace=False)
        keepr.append(qi); Cr.append([row.rt_row] + [h2r[adm[i]] for i in pick])
    keepr, Cr = np.array(keepr), np.array(Cr)
    Srev = np.einsum("qd,qcd->qc", B[te.nc_row.values[keepr]], A[Cr])
    rrev, cmrev, _ = summarise("M-CCA", "reverse_rung1", Srev,
                               te.component_id.values[keepr], {"status": "OK"})
    print(f"    ncRNA->RT  n={rrev['n_queries']:,}  MRR {rrev['mrr']:.4f} "
          f"[{rrev['ci_lo']:.4f}, {rrev['ci_hi']:.4f}]  top1 {rrev['top1']:.4f}")

    pd.DataFrame(rows).to_csv(OUT / "g2_test_ladder.tsv", sep="\t", index=False)
    pd.DataFrame(stop_rows).to_csv(OUT / "g2_stop_rule.tsv", sep="\t", index=False)
    pd.DataFrame(sens_rows).to_csv(OUT / "g2_sensitivity.tsv", sep="\t", index=False)
    pd.DataFrame(strata_rows).to_csv(OUT / "g2_strata.tsv", sep="\t", index=False)
    pd.DataFrame([rrev]).to_csv(OUT / "g2_reverse.tsv", sep="\t", index=False)
    (OUT / "g2_permutation.json").write_text(json.dumps(
        {"observed": float(obs), "null_mean": float(null.mean()),
         "null_p2.5": float(np.percentile(null, 2.5)),
         "null_p97.5": float(np.percentile(null, 97.5)),
         "p_value": pval, "n_perm": 2000, "chance_mrr": CHANCE_MRR}, indent=2) + "\n")
    print("\nwrote g2_test_ladder.tsv, g2_stop_rule.tsv, g2_sensitivity.tsv, "
          "g2_strata.tsv, g2_reverse.tsv, g2_permutation.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
