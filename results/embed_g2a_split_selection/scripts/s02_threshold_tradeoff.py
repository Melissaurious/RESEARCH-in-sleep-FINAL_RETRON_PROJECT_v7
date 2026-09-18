#!/usr/bin/env python
"""embed_g2/s02 - relatedness-threshold trade-off analysis. STRUCTURE ONLY.

This script is deliberately BLIND to compatibility. It never loads an embedding, never
computes a similarity between an RT and an ncRNA, and never reads a retrieval, CCA, CKA or
contrastive result. Every quantity below is a property of sequence relatedness and pair
topology, so the threshold decision cannot be contaminated by the thing it will later be used
to test.

============================ DECLARED RULES, FIXED BEFORE ANY NUMBER ============================

COVERAGE RULE (as already used in embed_g0, restated because it defines what "identity" means)
  RT    mmseqs easy-cluster --min-seq-id X -c 0.8 --cov-mode 0
        -> bidirectional coverage: BOTH sequences must be >=80% covered by the alignment.
  ncRNA cd-hit-est -c X -n 8 -aS 0.8 -T 1
        -> -aS is SHORTER-sequence coverage: the shorter sequence must be >=80% aligned.
  These differ, and the difference is deliberate: a protein pair that aligns over 80% of both
  is homologous along its length, while an ncRNA is short enough that anchoring on the shorter
  member is the standard and avoids discarding a genuine relative for a length difference.

SPLIT UNIT
  A connected component of the bipartite graph in which RT exact sequences are collapsed to RT
  relatedness clusters, ncRNA exact sequences to ncRNA relatedness clusters, and an observed
  RT-ncRNA pair is an edge. Components are indivisible.

FROZEN SPLIT RULE
  Target 70 / 15 / 15 by PAIR COUNT. Components sorted by (pairs desc, component key asc);
  each assigned to the fold with the largest remaining deficit; ties break train > val > test.
  Fully deterministic - no seed, no randomness, identical on every re-run.

LEAKAGE INSTRUMENT
  An INDEPENDENT all-vs-all probe (s01), more sensitive than any clustering threshold under
  consideration: mmseqs -s 7.5 --min-seq-id 0 for RT, blastn -task blastn -word_size 7 for
  ncRNA, both at e<=1e-3. Measuring leakage with the clustering tool at the clustering
  threshold would return zero by construction.

  HELD-OUT MEANS TEST, AND TRAINING MEANS TRAIN + VALIDATION. Validation is inspected during
  development, so leakage into it is leakage. Reporting test-vs-train alone would flatter the
  result.

  PRIMARY leakage identity requires query coverage >= 0.5; the uncovered maximum is reported
  beside it, because a 20-residue 100%-identical hit is not the same event as a full-length
  one.

CENSORING
  The probe keeps <=300 hits per query. If every retained hit of a held-out sequence lands in
  the held-out side, its true maximum identity to training is unknown-but-<= the smallest
  retained identity. Those queries are COUNTED and reported, never silently treated as zero.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
G0 = TASK.parents[0] / "embed_g0_population_audit" / "work" / "clusters"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")

RT_IDS = ["0.30", "0.50", "0.70", "0.90"]
NC_IDS = ["0.80", "0.90", "0.95"]
TARGET = {"train": 0.70, "val": 0.15, "test": 0.15}
TIERS = [0.30, 0.40, 0.50, 0.70, 0.90]
QCOV_MIN = 0.5
KEY = ["rt_seq_hash", "nc_seq_hash"]


# ------------------------------------------------------------------ cluster readers
def read_mmseqs(p: Path) -> dict[str, str]:
    d = {}
    for line in p.read_text().splitlines():
        rep, mem = line.split("\t")
        d[mem] = rep
    return d


def read_cdhit(p: Path) -> dict[str, str]:
    d, block, rep = {}, [], None
    def flush():
        if block:
            r = rep or block[0]
            for m in block:
                d[m] = r
    for line in p.read_text().splitlines():
        if line.startswith(">Cluster"):
            flush(); block, rep = [], None
            continue
        sid = line.split(">", 1)[1].split("...")[0].strip()
        block.append(sid)
        if line.rstrip().endswith("*"):
            rep = sid
    flush()
    return d


class DSU:
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x)
        r = x
        while self.p[r] != r:
            r = self.p[r]
        while self.p[x] != r:
            self.p[x], x = r, self.p[x]
        return r
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def assign_folds(sizes: pd.Series, n_pairs: int) -> dict[str, str]:
    """THE FROZEN RULE. Deterministic greedy: largest component to the largest deficit."""
    order = sorted(sizes.index, key=lambda c: (-int(sizes[c]), str(c)))
    got = {"train": 0, "val": 0, "test": 0}
    fold = {}
    for c in order:
        deficits = {f: TARGET[f] * n_pairs - got[f] for f in ("train", "val", "test")}
        best = max(("train", "val", "test"), key=lambda f: (deficits[f],
                                                           -["train", "val", "test"].index(f)))
        fold[c] = best
        got[best] += int(sizes[c])
    return fold


# ------------------------------------------------------------------ leakage
def load_rt_hits() -> pd.DataFrame:
    h = pd.read_csv(W / "rt_hits.tsv", sep="\t", header=None,
                    names=["q", "t", "fident", "alnlen", "qcov", "tcov", "evalue", "bits"])
    return h[h.q != h.t]


def load_nc_hits() -> pd.DataFrame:
    h = pd.read_csv(W / "nc_hits.tsv", sep="\t", header=None,
                    names=["q", "t", "pident", "length", "qlen", "slen", "evalue", "bits"])
    h = h[h.q != h.t].copy()
    h["fident"] = h.pident / 100.0
    h["qcov"] = h.length / h.qlen
    return h[["q", "t", "fident", "qcov"]]


def leakage(hits: pd.DataFrame, test_ids: set, train_ids: set) -> dict:
    """Max identity and tier fractions from held-out sequences into training."""
    if not test_ids:
        return dict(n_test=0, max_id=float("nan"), max_id_cov=float("nan"),
                    censored=0, **{f"frac_ge_{t}": float("nan") for t in TIERS})
    h = hits[hits.q.isin(test_ids)]
    into = h[h.t.isin(train_ids)]
    cov = into[into.qcov >= QCOV_MIN]
    best = into.groupby("q").fident.max()
    best_cov = cov.groupby("q").fident.max()
    # censored: a held-out query whose retained hits never reach training
    censored = len(test_ids - set(into.q.unique()) - (test_ids - set(h.q.unique())))
    out = dict(
        n_test=len(test_ids),
        max_id=float(best.max()) if len(best) else 0.0,
        max_id_cov=float(best_cov.max()) if len(best_cov) else 0.0,
        censored=int(censored),
        frac_detectable=float(len(best) / len(test_ids)),
    )
    for t in TIERS:
        out[f"frac_ge_{t}"] = float((best_cov >= t).sum() / len(test_ids))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet",
                        columns=KEY).to_pandas()
    n_pairs = len(reg)
    print(f"pair universe: {n_pairs:,}  RT {reg.rt_seq_hash.nunique():,}  "
          f"ncRNA {reg.nc_seq_hash.nunique():,}")

    # ---- tier membership, recomputed here so the table is self-contained --------------
    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet",
                      columns=KEY + ["canonical", "file_label", "same_strand", "direction",
                                     "n_cds_between", "signed_distance_bp", "evalue"]).to_pandas()
    cr = p[p.canonical & (p.file_label == "Retron")]
    t1 = set(map(tuple, cr[KEY].drop_duplicates().values))
    m2 = (cr.same_strand & (cr.direction != "downstream") & (cr.n_cds_between == 0)
          & (cr.signed_distance_bp.abs() <= 200))
    t2 = set(map(tuple, cr[m2][KEY].drop_duplicates().values))
    t3 = set(map(tuple, cr[m2 & (cr.evalue <= 1e-5)][KEY].drop_duplicates().values))
    rec = pq.read_table(CANON / "rt_ncrna_exact_pair_recurrence_v1.parquet",
                        columns=KEY + ["recurrence_class"]).to_pandas()
    recur = set(map(tuple, rec[rec.recurrence_class.isin(
        ["multiple_species", "one_species_multiple_genomes"])][KEY].values))
    t4 = t3 & recur
    print(f"tiers: T1 {len(t1):,}  T2 {len(t2):,}  T3 {len(t3):,}  T4 {len(t4):,}")
    ptup = list(map(tuple, reg[KEY].values))
    in_t = {n: np.array([x in s for x in ptup])
            for n, s in (("T1", t1), ("T2", t2), ("T3", t3), ("T4", t4))}

    print("loading the independent relatedness probe ...")
    rt_hits, nc_hits = load_rt_hits(), load_nc_hits()
    print(f"    RT hits {len(rt_hits):,}   ncRNA hits {len(nc_hits):,}")

    rows, dists = [], []
    for rid in RT_IDS:
        rmap = read_mmseqs(G0 / f"rt_id{rid}_cluster.tsv")
        for nid in NC_IDS:
            nmap = read_cdhit(G0 / f"nc_id{nid}.clstr")
            d = DSU()
            rc = reg.rt_seq_hash.map(rmap).values
            nc = reg.nc_seq_hash.map(nmap).values
            for a, b in zip(rc, nc):
                d.union("R" + a, "N" + b)
            comp = np.array([d.find("R" + x) for x in rc])
            sizes = pd.Series(comp).value_counts()

            fold_of = assign_folds(sizes, n_pairs)
            pf = np.array([fold_of[c] for c in comp])
            npf = {f: int((pf == f).sum()) for f in ("train", "val", "test")}

            # sequences per fold
            seq = {}
            for f in ("train", "val", "test"):
                m = pf == f
                seq[f] = (set(reg.rt_seq_hash.values[m]), set(reg.nc_seq_hash.values[m]))
            tr_rt, tr_nc = seq["train"][0] | seq["val"][0], seq["train"][1] | seq["val"][1]
            te_rt, te_nc = seq["test"][0] - tr_rt, seq["test"][1] - tr_nc

            lr = leakage(rt_hits, te_rt, tr_rt)
            ln = leakage(nc_hits, te_nc, tr_nc)

            # pair-level reachability through EITHER modality
            rt_reach = set(rt_hits[rt_hits.q.isin(te_rt) & rt_hits.t.isin(tr_rt)
                                   & (rt_hits.qcov >= QCOV_MIN)].q.unique())
            nc_reach = set(nc_hits[nc_hits.q.isin(te_nc) & nc_hits.t.isin(tr_nc)
                                   & (nc_hits.qcov >= QCOV_MIN)].q.unique())
            tm = pf == "test"
            te_pairs = reg[tm]
            reach = (te_pairs.rt_seq_hash.isin(rt_reach) | te_pairs.nc_seq_hash.isin(nc_reach))
            # components with NO relatedness connection at all
            tc = sorted({c for c, f in fold_of.items() if f == "test"})
            comp_reach = pd.Series(reach.values).groupby(comp[tm]).any()
            iso = int((~comp_reach).sum())

            sz = sizes.values
            rows.append(dict(
                rt_id=rid, nc_id=nid,
                rt_clusters=int(pd.Series(rc).nunique()), nc_clusters=int(pd.Series(nc).nunique()),
                components=int(sizes.size),
                largest=int(sz.max()), largest_pct=round(100 * sz.max() / n_pairs, 2),
                median_comp=int(np.median(sz)), singletons=int((sz == 1).sum()),
                pairs=n_pairs, uniq_rt=int(reg.rt_seq_hash.nunique()),
                uniq_nc=int(reg.nc_seq_hash.nunique()),
                train=npf["train"], val=npf["val"], test=npf["test"],
                test_pct=round(100 * npf["test"] / n_pairs, 2),
                test_comps=len(tc),
                **{f"{k}_test": int(in_t[k][tm].sum()) for k in in_t},
                **{f"{k}_test_pct": round(100 * in_t[k][tm].sum() / max(in_t[k].sum(), 1), 2)
                   for k in in_t},
                rt_max_id=round(lr["max_id"], 4), rt_max_id_cov=round(lr["max_id_cov"], 4),
                nc_max_id=round(ln["max_id"], 4), nc_max_id_cov=round(ln["max_id_cov"], 4),
                rt_frac_detectable=round(lr["frac_detectable"], 4),
                nc_frac_detectable=round(ln["frac_detectable"], 4),
                **{f"rt_frac_ge_{t}": round(lr[f"frac_ge_{t}"], 4) for t in TIERS},
                **{f"nc_frac_ge_{t}": round(ln[f"frac_ge_{t}"], 4) for t in TIERS},
                rt_censored=lr["censored"], nc_censored=ln["censored"],
                test_pairs_reachable=int(reach.sum()),
                test_pairs_reachable_frac=round(float(reach.mean()), 4),
                test_comps_isolated=iso,
                test_comps_isolated_frac=round(iso / max(len(tc), 1), 4),
            ))
            q = np.percentile(sz, [50, 75, 90, 95, 99])
            dists.append(dict(rt_id=rid, nc_id=nid, n=int(sizes.size),
                              p50=int(q[0]), p75=int(q[1]), p90=int(q[2]),
                              p95=int(q[3]), p99=int(q[4]), max=int(sz.max()),
                              n_size1=int((sz == 1).sum()),
                              n_size2_10=int(((sz >= 2) & (sz <= 10)).sum()),
                              n_size11_100=int(((sz >= 11) & (sz <= 100)).sum()),
                              n_size101_1000=int(((sz >= 101) & (sz <= 1000)).sum()),
                              n_size_gt1000=int((sz > 1000).sum())))
            print(f"  RT {rid}/nc {nid}: {sizes.size:6,} comps  giant {sz.max():6,} "
                  f"({100*sz.max()/n_pairs:5.1f}%)  test {npf['test']:6,} "
                  f"({100*npf['test']/n_pairs:4.1f}%)  RTmaxid {lr['max_id_cov']:.3f}  "
                  f"NCmaxid {ln['max_id_cov']:.3f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "g2_threshold_tradeoff.tsv", sep="\t", index=False)
    pd.DataFrame(dists).to_csv(OUT / "g2_component_size_distribution.tsv", sep="\t", index=False)
    print(f"\nwrote g2_threshold_tradeoff.tsv ({len(df)} rows) and "
          f"g2_component_size_distribution.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
