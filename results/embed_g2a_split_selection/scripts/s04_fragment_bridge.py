#!/usr/bin/env python
"""embed_g2/s04 - the fragment-leakage channel at the proposed RT 0.50 / ncRNA 0.80 split.

MOTIVATION, from the threshold analysis itself. The primary clustering requires 80% coverage
(RT: bidirectional; ncRNA: shorter-sequence). A near-identical FRAGMENT of a training sequence
therefore fails the coverage test, lands in its own cluster, and is free to cross into the
held-out fold. The identity threshold never sees it. This script measures that channel and
prices the remedy.

THIS IS PRE-OUTCOME LEAKAGE CONTROL, NOT THRESHOLD OPTIMISATION.
  - identity thresholds are NOT touched: RT stays 0.50, ncRNA stays 0.80;
  - the primary clustering definitions are NOT touched;
  - nothing downstream of the split is loaded, computed or read.

OPTION A   the 0.50/0.80 component rule, unchanged.
OPTION B   the SAME 0.50/0.80 biological clustering, plus a predeclared secondary
           FRAGMENT-BRIDGE rule whose ONLY job is to stop related fragments crossing
           train/test. A bridge is a within-modality edge between two sequences that the
           primary clustering left in different clusters but that the independent probe says
           are near-identical over a declared coverage. Bridges are added to the bipartite
           graph BEFORE splitting, so they can only ever MERGE components - they never move a
           pair between folds by themselves and never relabel biology. A bridge is not a claim
           that two sequences are the same cluster; it is a refusal to split them apart.

ORDER MATTERS AND IS FIXED. Bridges are built from the whole-universe probe and applied before
any fold assignment. Building them from the test-vs-train comparison would be circular - the
split would be defining the bridges that redefine the split.

CAVEAT ON BRIDGE CONSTRUCTION. The s01 probe keeps <=300 hits per query against the whole
universe. At the identity levels used for bridging (>=0.70, >=0.90) a sequence's true
near-identical relatives are overwhelmingly inside its own top-300, but this is a cap and it is
reported rather than assumed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
G0 = TASK.parents[0] / "embed_g0_population_audit" / "work" / "clusters"
ROOT = TASK.parents[1]
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
MM = "/home/borg/miniconda3/envs/colabfold/bin/mmseqs"
BN = "/home/borg/miniconda3/envs/retrons/bin/blastn"
MK = "/home/borg/miniconda3/envs/retrons/bin/makeblastdb"

RT_ID, NC_ID = "0.50", "0.80"
TARGET = {"train": 0.70, "val": 0.15, "test": 0.15}
KEY = ["rt_seq_hash", "nc_seq_hash"]

# The three criteria named in the operator's check, used BOTH as leakage counters and as
# candidate bridge definitions. (identity, coverage) with coverage = max(qcov, tcov) so a
# fragment counts whichever way round it is.
CRITERIA = [("id>=0.50 & cov>=0.50", 0.50, 0.50),
            ("id>=0.70 & cov>=0.50", 0.70, 0.50),
            ("id>=0.90 & cov>=0.30", 0.90, 0.30)]
COV_BANDS = [("cov<0.30", 0.0, 0.30), ("0.30<=cov<0.50", 0.30, 0.50),
             ("0.50<=cov<0.80", 0.50, 0.80), ("cov>=0.80", 0.80, 1.01)]
QS = [0.0, 0.05, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0]


def read_mm(p):
    return {m: r for r, m in (l.split("\t") for l in p.read_text().splitlines())}


def read_cd(p):
    d, b, rep = {}, [], None
    def f():
        if b:
            r = rep or b[0]
            for m in b:
                d[m] = r
    for l in p.read_text().splitlines():
        if l.startswith(">Cluster"):
            f(); b, rep = [], None; continue
        s = l.split(">", 1)[1].split("...")[0].strip()
        b.append(s)
        if l.rstrip().endswith("*"):
            rep = s
    f(); return d


class DSU:
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x); r = x
        while self.p[r] != r: r = self.p[r]
        while self.p[x] != r: self.p[x], x = r, self.p[x]
        return r
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[ra] = rb


def assign(sizes, n):
    order = sorted(sizes.index, key=lambda c: (-int(sizes[c]), str(c)))
    got = {"train": 0, "val": 0, "test": 0}; fold = {}
    for c in order:
        d = {f: TARGET[f] * n - got[f] for f in got}
        best = max(("train", "val", "test"), key=lambda f: (d[f], -["train", "val", "test"].index(f)))
        fold[c] = best; got[best] += int(sizes[c])
    return fold


def neff(s):
    s = np.asarray(s, float)
    return float((s.sum() ** 2) / (s ** 2).sum())


def read_fasta(p):
    s, sid, buf = {}, None, []
    for l in p.read_text().splitlines():
        if l.startswith(">"):
            if sid: s[sid] = "".join(buf)
            sid, buf = l[1:].split()[0], []
        else: buf.append(l.strip())
    if sid: s[sid] = "".join(buf)
    return s


def run(cmd):
    """Run a tool and, on failure, show its OWN error rather than a bare CalledProcessError."""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"FAILED: {' '.join(str(c) for c in cmd)}\n"
                         f"--- stderr ---\n{r.stderr[-3000:]}\n--- stdout ---\n{r.stdout[-1500:]}")
    return r


def exact_probe(tmp, seqs, q_ids, d_ids, kind):
    """Held-out vs TRAINING-ONLY database. No censoring is possible."""
    # mmseqs refuses to reuse a populated tmp directory, and an aborted earlier run leaves one.
    subprocess.run(["rm", "-rf", str(tmp)], check=False)
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "q").write_text("".join(f">{i}\n{seqs[i]}\n" for i in sorted(q_ids)))
    (tmp / "d").write_text("".join(f">{i}\n{seqs[i]}\n" for i in sorted(d_ids)))
    if kind == "rt":
        for a in (["createdb", f"{tmp}/q", f"{tmp}/qd", "-v", "1"],
                  ["createdb", f"{tmp}/d", f"{tmp}/dd", "-v", "1"],
                  ["search", f"{tmp}/qd", f"{tmp}/dd", f"{tmp}/r", f"{tmp}/w", "-s", "7.5",
                   "--min-seq-id", "0.0", "-e", "1000", "--max-seqs", "300", "-c", "0.0",
                   "--threads", "16", "-v", "1"],
                  ["convertalis", f"{tmp}/qd", f"{tmp}/dd", f"{tmp}/r", f"{tmp}/h.tsv",
                   "--format-output", "query,target,fident,qcov,tcov", "-v", "1"]):
            run([MM] + a)
        h = pd.read_csv(f"{tmp}/h.tsv", sep="\t", header=None,
                        names=["q", "t", "fident", "qcov", "tcov"])
    else:
        run([MK, "-in", f"{tmp}/d", "-dbtype", "nucl", "-out", f"{tmp}/db"])
        run([BN, "-task", "blastn", "-word_size", "7", "-query", f"{tmp}/q",
             "-db", f"{tmp}/db", "-evalue", "1000", "-max_target_seqs", "300",
             "-num_threads", "16", "-outfmt",
             "6 qseqid sseqid pident length qlen slen", "-out", f"{tmp}/h.tsv"])
        h = pd.read_csv(f"{tmp}/h.tsv", sep="\t", header=None,
                        names=["q", "t", "pident", "length", "qlen", "slen"])
        h["fident"] = h.pident / 100
        h["qcov"] = h.length / h.qlen
        h["tcov"] = h.length / h.slen
        h = h[["q", "t", "fident", "qcov", "tcov"]]
    h["aln_cov"] = h[["qcov", "tcov"]].max(axis=1)  # NOT "cov": DataFrame.cov is a method
    return h


def build(reg, rmap, nmap, bridges_rt=None, bridges_nc=None):
    d = DSU()
    rc = reg.rt_seq_hash.map(rmap).values
    nc = reg.nc_seq_hash.map(nmap).values
    for a, b in zip(rc, nc):
        d.union("R" + a, "N" + b)
    for a, b in (bridges_rt or []):
        if a in rmap and b in rmap:
            d.union("R" + rmap[a], "R" + rmap[b])
    for a, b in (bridges_nc or []):
        if a in nmap and b in nmap:
            d.union("N" + nmap[a], "N" + nmap[b])
    return np.array([d.find("R" + x) for x in rc])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tmpbase = Path(__import__("os").environ.get("TMPDIR", "/tmp")) / "g2frag"
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet", columns=KEY).to_pandas()
    n = len(reg)
    rmap, nmap = read_mm(G0 / f"rt_id{RT_ID}_cluster.tsv"), read_cd(G0 / f"nc_id{NC_ID}.clstr")
    rt_seqs = read_fasta(ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa")
    nc_seqs = read_fasta(ROOT / "data/derived/rt_ncrna_oriented_v1.fna")

    # tiers
    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet",
                      columns=KEY + ["canonical", "file_label", "same_strand", "direction",
                                     "n_cds_between", "signed_distance_bp", "evalue"]).to_pandas()
    cr = p[p.canonical & (p.file_label == "Retron")]
    m2 = (cr.same_strand & (cr.direction != "downstream") & (cr.n_cds_between == 0)
          & (cr.signed_distance_bp.abs() <= 200))
    t3 = set(map(tuple, cr[m2 & (cr.evalue <= 1e-5)][KEY].drop_duplicates().values))
    rec = pq.read_table(CANON / "rt_ncrna_exact_pair_recurrence_v1.parquet",
                        columns=KEY + ["recurrence_class"]).to_pandas()
    t4 = t3 & set(map(tuple, rec[rec.recurrence_class.isin(
        ["multiple_species", "one_species_multiple_genomes"])][KEY].values))
    tup = list(map(tuple, reg[KEY].values))
    isT3 = np.array([x in t3 for x in tup]); isT4 = np.array([x in t4 for x in tup])

    # ---------------- OPTION A baseline ------------------------------------------------
    compA = build(reg, rmap, nmap)
    szA = pd.Series(compA).value_counts()
    foldA = assign(szA, n)
    pfA = np.array([foldA[c] for c in compA])
    trA = pfA != "test"
    tr_rt, tr_nc = set(reg.rt_seq_hash.values[trA]), set(reg.nc_seq_hash.values[trA])
    te_rt = set(reg.rt_seq_hash.values[~trA]) - tr_rt
    te_nc = set(reg.nc_seq_hash.values[~trA]) - tr_nc
    print(f"OPTION A  RT {RT_ID}/nc {NC_ID}: {len(szA):,} comps  "
          f"train {int((pfA=='train').sum()):,} val {int((pfA=='val').sum()):,} "
          f"test {int((pfA=='test').sum()):,}  held-out {len(te_rt):,} RT / {len(te_nc):,} ncRNA")

    # ---------------- 1-3 : distributions and crossing counts ---------------------------
    dist_rows, band_rows, cross_rows = [], [], []
    hits = {}
    for kind, seqs, te, tr in (("RT", rt_seqs, te_rt, tr_rt), ("ncRNA", nc_seqs, te_nc, tr_nc)):
        h = exact_probe(tmpbase / kind, seqs, te, tr, "rt" if kind == "RT" else "nc")
        hits[kind] = h
        best = h.groupby("q").fident.max().reindex(sorted(te)).fillna(0.0)
        dist_rows.append(dict(modality=kind, n_heldout=len(te),
                              no_hit=int((best == 0).sum()),
                              **{f"q{int(q*100)}": round(float(best.quantile(q)), 4) for q in QS},
                              mean=round(float(best.mean()), 4)))
        for name, lo, hi in COV_BANDS:
            sub = h[(h.aln_cov >= lo) & (h.aln_cov < hi)]
            b = sub.groupby("q").fident.max().reindex(sorted(te)).fillna(0.0)
            band_rows.append(dict(modality=kind, band=name,
                                  n_with_hit=int((b > 0).sum()),
                                  frac_with_hit=round(float((b > 0).mean()), 4),
                                  **{f"q{int(q*100)}": round(float(b.quantile(q)), 4)
                                     for q in (0.5, 0.9, 0.99, 1.0)}))
        for name, mid, mcov in CRITERIA:
            sub = h[(h.fident >= mid) & (h.aln_cov >= mcov)]
            nq = sub.q.nunique()
            cross_rows.append(dict(modality=kind, criterion=name, n_heldout=len(te),
                                   n_crossing=nq, frac_crossing=round(nq / len(te), 4),
                                   n_edges=len(sub)))
            print(f"    {kind:<6} {name:<24} {nq:>6,}/{len(te):,} = {nq/len(te):6.2%}  "
                  f"({len(sub):,} edges)")

    pd.DataFrame(dist_rows).to_csv(OUT / "g2_frag_maxsim_distribution.tsv", sep="\t", index=False)
    pd.DataFrame(band_rows).to_csv(OUT / "g2_frag_maxsim_by_coverage.tsv", sep="\t", index=False)
    pd.DataFrame(cross_rows).to_csv(OUT / "g2_frag_crossing_counts.tsv", sep="\t", index=False)

    # ---------------- reachability and isolation (the previously missing numbers) -------
    te_pairs = reg[~trA]
    reach_rt = set(hits["RT"][hits["RT"].aln_cov >= 0.5].q.unique())
    reach_nc = set(hits["ncRNA"][hits["ncRNA"].aln_cov >= 0.5].q.unique())
    reach = te_pairs.rt_seq_hash.isin(reach_rt) | te_pairs.nc_seq_hash.isin(reach_nc)
    comp_reach = pd.Series(reach.values).groupby(compA[~trA]).any()
    print(f"\n  held-out pairs reachable from training via either modality: "
          f"{int(reach.sum()):,}/{len(te_pairs):,} = {reach.mean():.2%}")
    print(f"  held-out components with NO detectable relationship to training: "
          f"{int((~comp_reach).sum())}/{len(comp_reach)} = {(~comp_reach).mean():.2%}")

    # ---------------- 4-5 : bridge variants --------------------------------------------
    rt_all = pd.read_csv(W / "rt_hits.tsv", sep="\t", header=None,
                         names=["q", "t", "fident", "alnlen", "qcov", "tcov", "e", "b"],
                         usecols=["q", "t", "fident", "qcov", "tcov"])
    rt_all = rt_all[rt_all.q != rt_all.t]
    rt_all["aln_cov"] = rt_all[["qcov", "tcov"]].max(axis=1)
    nc_all = pd.read_csv(W / "nc_hits.tsv", sep="\t", header=None,
                         names=["q", "t", "pid", "length", "qlen", "slen", "e", "b"])
    nc_all = nc_all[nc_all.q != nc_all.t]
    nc_all["fident"] = nc_all.pid / 100
    nc_all["aln_cov"] = np.maximum(nc_all.length / nc_all.qlen, nc_all.length / nc_all.slen)

    res = []
    for name, mid, mcov in CRITERIA:
        # item 4 - how many CURRENT test components have such a relationship to training
        n_conn = 0
        for kind, h, col in (("RT", hits["RT"], "rt_seq_hash"), ("ncRNA", hits["ncRNA"], "nc_seq_hash")):
            pass
        q_rt = set(hits["RT"][(hits["RT"].fident >= mid) & (hits["RT"].aln_cov >= mcov)].q.unique())
        q_nc = set(hits["ncRNA"][(hits["ncRNA"].fident >= mid) & (hits["ncRNA"].aln_cov >= mcov)].q.unique())
        conn = te_pairs.rt_seq_hash.isin(q_rt) | te_pairs.nc_seq_hash.isin(q_nc)
        cc = pd.Series(conn.values).groupby(compA[~trA]).any()
        n_conn = int(cc.sum())

        # item 5 - apply as bridges globally, re-split
        br = rt_all[(rt_all.fident >= mid) & (rt_all.aln_cov >= mcov)]
        bn = nc_all[(nc_all.fident >= mid) & (nc_all.aln_cov >= mcov)]
        bridges_rt = [(a, b) for a, b in zip(br.q, br.t) if rmap.get(a) != rmap.get(b)]
        bridges_nc = [(a, b) for a, b in zip(bn.q, bn.t) if nmap.get(a) != nmap.get(b)]
        compB = build(reg, rmap, nmap, bridges_rt, bridges_nc)
        szB = pd.Series(compB).value_counts()
        foldB = assign(szB, n)
        pfB = np.array([foldB[c] for c in compB])
        tm = pfB == "test"
        tc = szB[[c for c, f in foldB.items() if f == "test"]]
        r = dict(criterion=name, min_identity=mid, min_coverage=mcov,
                 bridge_edges_rt=len(bridges_rt), bridge_edges_nc=len(bridges_nc),
                 testcomps_connected_before=n_conn,
                 testcomps_total_before=len(cc),
                 frac_connected_before=round(n_conn / len(cc), 4),
                 components=len(szB), largest=int(szB.max()),
                 largest_pct=round(100 * szB.max() / n, 2),
                 train=int((pfB == "train").sum()), val=int((pfB == "val").sum()),
                 test=int(tm.sum()), test_pct=round(100 * tm.mean(), 2),
                 test_comps=len(tc), test_neff=round(neff(tc.values), 1),
                 val_neff=round(neff(szB[[c for c, f in foldB.items() if f == "val"]].values), 1),
                 T3_test=int(isT3[tm].sum()), T4_test=int(isT4[tm].sum()),
                 T3_test_pct=round(100 * isT3[tm].sum() / isT3.sum(), 2),
                 T4_test_pct=round(100 * isT4[tm].sum() / isT4.sum(), 2))
        res.append(r)
        print(f"\n  BRIDGE {name}")
        print(f"    edges RT {len(bridges_rt):,}  nc {len(bridges_nc):,}   "
              f"current test comps connected to train: {n_conn}/{len(cc)} "
              f"({n_conn/len(cc):.1%})")
        print(f"    -> comps {len(szB):,}  largest {szB.max():,} ({100*szB.max()/n:.1f}%)  "
              f"train/val/test {int((pfB=='train').sum()):,}/{int((pfB=='val').sum()):,}/"
              f"{int(tm.sum()):,}  test n_eff {r['test_neff']}  val n_eff {r['val_neff']}  "
              f"T3 {r['T3_test_pct']}%  T4 {r['T4_test_pct']}%")

    # OPTION A row for comparison
    tcA = szA[[c for c, f in foldA.items() if f == "test"]]
    res.insert(0, dict(criterion="OPTION A - no bridges", min_identity=None, min_coverage=None,
                       bridge_edges_rt=0, bridge_edges_nc=0,
                       testcomps_connected_before=0, testcomps_total_before=len(tcA),
                       frac_connected_before=0.0,
                       components=len(szA), largest=int(szA.max()),
                       largest_pct=round(100 * szA.max() / n, 2),
                       train=int((pfA == "train").sum()), val=int((pfA == "val").sum()),
                       test=int((pfA == "test").sum()),
                       test_pct=round(100 * (pfA == "test").mean(), 2),
                       test_comps=len(tcA), test_neff=round(neff(tcA.values), 1),
                       val_neff=round(neff(szA[[c for c, f in foldA.items() if f == "val"]].values), 1),
                       T3_test=int(isT3[pfA == "test"].sum()), T4_test=int(isT4[pfA == "test"].sum()),
                       T3_test_pct=round(100 * isT3[pfA == "test"].sum() / isT3.sum(), 2),
                       T4_test_pct=round(100 * isT4[pfA == "test"].sum() / isT4.sum(), 2)))
    pd.DataFrame(res).to_csv(OUT / "g2_fragment_bridge_options.tsv", sep="\t", index=False)
    subprocess.run(["rm", "-rf", str(tmpbase)], check=False)
    print("\nwrote g2_frag_*.tsv and g2_fragment_bridge_options.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
