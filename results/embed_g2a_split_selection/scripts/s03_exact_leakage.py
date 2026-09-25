#!/usr/bin/env python
"""embed_g2/s03 - EXACT, uncensorable leakage for the candidate threshold combinations.

WHY s02 IS NOT ENOUGH. The s01 probe keeps <=300 hits per query against the WHOLE universe.
At RT 0.30 the held-out components are small and their members' 300 best hits are saturated by
within-component relatives, so 75-82% of held-out RTs never reach a training sequence in the
retained list. Their measured leakage is a LOWER BOUND, and a lower bound is exactly the wrong
statistic for choosing the strictest defensible blocking - it flatters the strict thresholds.

THE FIX. Search each held-out set against a database containing ONLY training sequences.
Censoring then cannot occur: every hit that exists is a hit into training.

TWO COVERAGE VIEWS, because they answer different questions:
  qcov>=0.5           "is there a training sequence that looks like most of this held-out one"
  qcov>=0.8 & tcov>=0.8  the SAME bidirectional rule mmseqs easy-cluster used to build the RT
                      clusters. A pair that passes this and is above the clustering identity
                      but sits across the split boundary is a genuine clustering failure. A
                      pair that is highly identical but fails it is the COVERAGE RULE letting a
                      fragment through - a different problem with a different remedy.
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

CANDIDATES = [("0.30", "0.95"), ("0.50", "0.80"), ("0.50", "0.90"), ("0.50", "0.95"),
              ("0.70", "0.90")]
TARGET = {"train": 0.70, "val": 0.15, "test": 0.15}
TIERS = [0.30, 0.50, 0.70, 0.90]
KEY = ["rt_seq_hash", "nc_seq_hash"]


def read_mmseqs(p):
    return {m: r for r, m in (l.split("\t") for l in p.read_text().splitlines())}


def read_cdhit(p):
    d, block, rep = {}, [], None
    def flush():
        if block:
            r = rep or block[0]
            for m in block:
                d[m] = r
    for line in p.read_text().splitlines():
        if line.startswith(">Cluster"):
            flush(); block, rep = [], None; continue
        sid = line.split(">", 1)[1].split("...")[0].strip()
        block.append(sid)
        if line.rstrip().endswith("*"):
            rep = sid
    flush(); return d


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


def assign_folds(sizes, n_pairs):
    order = sorted(sizes.index, key=lambda c: (-int(sizes[c]), str(c)))
    got = {"train": 0, "val": 0, "test": 0}; fold = {}
    for c in order:
        d = {f: TARGET[f] * n_pairs - got[f] for f in got}
        best = max(("train", "val", "test"),
                   key=lambda f: (d[f], -["train", "val", "test"].index(f)))
        fold[c] = best; got[best] += int(sizes[c])
    return fold


def read_fasta(p):
    s, sid, buf = {}, None, []
    for line in p.read_text().splitlines():
        if line.startswith(">"):
            if sid: s[sid] = "".join(buf)
            sid, buf = line[1:].split()[0], []
        else: buf.append(line.strip())
    if sid: s[sid] = "".join(buf)
    return s


def write_fasta(p, seqs, ids):
    p.write_text("".join(f">{i}\n{seqs[i]}\n" for i in sorted(ids)))


def rt_search(tmp, q, db):
    for a in (["createdb", str(q), f"{tmp}/q", "-v", "1"],
              ["createdb", str(db), f"{tmp}/t", "-v", "1"],
              ["search", f"{tmp}/q", f"{tmp}/t", f"{tmp}/r", f"{tmp}/w",
               "-s", "7.5", "--min-seq-id", "0.0", "-e", "1000", "--max-seqs", "300",
               "-c", "0.0", "--threads", "16", "-v", "1"],
              ["convertalis", f"{tmp}/q", f"{tmp}/t", f"{tmp}/r", f"{tmp}/hits.tsv",
               "--format-output", "query,target,fident,qcov,tcov", "-v", "1"]):
        subprocess.run([MM] + a, check=True, capture_output=True)
    return pd.read_csv(f"{tmp}/hits.tsv", sep="\t", header=None,
                       names=["q", "t", "fident", "qcov", "tcov"])


def nc_search(tmp, q, db):
    subprocess.run([MK, "-in", str(db), "-dbtype", "nucl", "-out", f"{tmp}/ncdb"],
                   check=True, capture_output=True)
    subprocess.run([BN, "-task", "blastn", "-word_size", "7", "-query", str(q),
                    "-db", f"{tmp}/ncdb", "-evalue", "1000", "-max_target_seqs", "300",
                    "-num_threads", "16", "-outfmt",
                    "6 qseqid sseqid pident length qlen slen", "-out", f"{tmp}/hits.tsv"],
                   check=True, capture_output=True)
    h = pd.read_csv(f"{tmp}/hits.tsv", sep="\t", header=None,
                    names=["q", "t", "pident", "length", "qlen", "slen"])
    h["fident"] = h.pident / 100
    h["qcov"] = h.length / h.qlen
    h["tcov"] = h.length / h.slen
    return h[["q", "t", "fident", "qcov", "tcov"]]


def summarise(h, test_ids, tag):
    n = len(test_ids)
    out = {f"{tag}_n_test": n}
    for name, sub in (("cov50", h[h.qcov >= 0.5]),
                      ("bidir80", h[(h.qcov >= 0.8) & (h.tcov >= 0.8)])):
        best = sub.groupby("q").fident.max()
        out[f"{tag}_{name}_max"] = round(float(best.max()), 4) if len(best) else 0.0
        out[f"{tag}_{name}_p99"] = round(float(best.quantile(.99)), 4) if len(best) else 0.0
        for t in TIERS:
            out[f"{tag}_{name}_ge{t}"] = round(float((best >= t).sum() / n), 4)
    out[f"{tag}_detectable"] = round(float(h.q.nunique() / n), 4)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    tmpbase = Path(__import__("os").environ.get("TMPDIR", "/tmp")) / "g2exact"
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet", columns=KEY).to_pandas()
    n_pairs = len(reg)
    rt_seqs = read_fasta(ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa")
    nc_seqs = read_fasta(ROOT / "data/derived/rt_ncrna_oriented_v1.fna")

    rows = []
    for rid, nid in CANDIDATES:
        rmap, nmap = read_mmseqs(G0 / f"rt_id{rid}_cluster.tsv"), read_cdhit(G0 / f"nc_id{nid}.clstr")
        d = DSU()
        rc = reg.rt_seq_hash.map(rmap).values
        nc = reg.nc_seq_hash.map(nmap).values
        for a, b in zip(rc, nc):
            d.union("R" + a, "N" + b)
        comp = np.array([d.find("R" + x) for x in rc])
        fold_of = assign_folds(pd.Series(comp).value_counts(), n_pairs)
        pf = np.array([fold_of[c] for c in comp])

        tr = pf != "test"
        tr_rt, tr_nc = set(reg.rt_seq_hash.values[tr]), set(reg.nc_seq_hash.values[tr])
        te_rt = set(reg.rt_seq_hash.values[~tr]) - tr_rt
        te_nc = set(reg.nc_seq_hash.values[~tr]) - tr_nc
        print(f"\n=== RT {rid} / nc {nid}: test {int((~tr).sum()):,} pairs, "
              f"{len(te_rt):,} RT, {len(te_nc):,} ncRNA vs train {len(tr_rt):,}/{len(tr_nc):,}",
              flush=True)

        t = tmpbase / f"{rid}_{nid}"
        subprocess.run(["rm", "-rf", str(t)], check=False)
        (t / "rt").mkdir(parents=True, exist_ok=True); (t / "nc").mkdir(parents=True, exist_ok=True)
        write_fasta(t / "q_rt.faa", rt_seqs, te_rt); write_fasta(t / "d_rt.faa", rt_seqs, tr_rt)
        write_fasta(t / "q_nc.fna", nc_seqs, te_nc); write_fasta(t / "d_nc.fna", nc_seqs, tr_nc)

        r = {"rt_id": rid, "nc_id": nid, "test_pairs": int((~tr).sum()),
             "test_comps": len({c for c, f in fold_of.items() if f == "test"})}
        r |= summarise(rt_search(t / "rt", t / "q_rt.faa", t / "d_rt.faa"), te_rt, "rt")
        r |= summarise(nc_search(t / "nc", t / "q_nc.fna", t / "d_nc.fna"), te_nc, "nc")
        rows.append(r)
        print(f"    RT  cov50 max {r['rt_cov50_max']:.3f}  >=0.5 {r['rt_cov50_ge0.5']:.1%}  "
              f"| bidir80 max {r['rt_bidir80_max']:.3f}  >=0.5 {r['rt_bidir80_ge0.5']:.1%}")
        print(f"    nc  cov50 max {r['nc_cov50_max']:.3f}  >=0.5 {r['nc_cov50_ge0.5']:.1%}  "
              f"| bidir80 max {r['nc_bidir80_max']:.3f}  >=0.5 {r['nc_bidir80_ge0.5']:.1%}")
        subprocess.run(["rm", "-rf", str(t)], check=False)

    pd.DataFrame(rows).to_csv(OUT / "g2_exact_leakage.tsv", sep="\t", index=False)
    print(f"\nwrote g2_exact_leakage.tsv ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
