#!/usr/bin/env python
"""embed-g0/a05 - connected-component structure of the relatedness graph (amendment 3).

THE QUESTION THIS ANSWERS, BEFORE ANY THRESHOLD IS FROZEN: if we cluster RTs and ncRNAs and
then contract the 30,924 pairs onto those clusters, does the graph fall apart into usable
blocks, or does one giant component swallow the dataset and make a leakage-free held-out
split impossible?

WHY THE COMPONENT AND NOT THE CLUSTER. Splitting on RT clusters alone leaks through shared
ncRNAs - one ncRNA in this universe has 705 RT partners. Splitting on ncRNA clusters alone
leaks symmetrically. Only the connected component of the bipartite graph is closed under
both relations.

Reports, per threshold combination: component count, the giant component's share of pairs,
and the largest held-out fraction obtainable by whole components. No threshold is chosen
here; that is a frozen operator decision taken with this table in hand.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
RT_IDS = ["0.30", "0.50", "0.70", "0.90"]
NC_IDS = ["0.80", "0.90", "0.95", "0.99"]
TARGET_TEST = 0.20            # the held-out fraction the confirmatory readout wants


def read_mmseqs(p: Path) -> dict[str, str]:
    """mmseqs *_cluster.tsv: representative<TAB>member."""
    d = {}
    for line in p.read_text().splitlines():
        rep, mem = line.split("\t")
        d[mem] = rep
    return d


def read_cdhit(p: Path) -> dict[str, str]:
    """cd-hit .clstr: members of each >Cluster block map to that block's representative (*)."""
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
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[ra] = rb


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet",
                        columns=["rt_seq_hash", "nc_seq_hash", "n_physical_loci"]).to_pandas()
    print(f"pairs {len(reg):,}")

    rows, detail = [], []
    for rid in RT_IDS:
        rmap = read_mmseqs(W / "clusters" / f"rt_id{rid}_cluster.tsv")
        miss = set(reg.rt_seq_hash) - set(rmap)
        assert not miss, f"RT {rid}: {len(miss)} hashes unclustered"
        for nid in NC_IDS:
            nmap = read_cdhit(W / "clusters" / f"nc_id{nid}.clstr")
            missn = set(reg.nc_seq_hash) - set(nmap)
            assert not missn, f"nc {nid}: {len(missn)} hashes unclustered"

            d = DSU()
            rc = reg.rt_seq_hash.map(rmap)
            nc = reg.nc_seq_hash.map(nmap)
            for a, b in zip("R" + rc, "N" + nc):
                d.union(a, b)
            comp = pd.Series([d.find("R" + x) for x in rc], index=reg.index)

            sz = comp.value_counts()                      # pairs per component
            giant = sz.iloc[0]
            # largest held-out fraction reachable with WHOLE components, greedily
            s = sz.sort_values(ascending=False).values
            budget, take = TARGET_TEST * len(reg), 0
            for v in s[::-1]:                             # smallest first, pack up to target
                if take + v <= budget: take += v
            rows.append(dict(
                rt_id=rid, nc_id=nid,
                rt_clusters=int(rc.nunique()), nc_clusters=int(nc.nunique()),
                components=int(sz.size),
                giant_pairs=int(giant), giant_frac=round(giant / len(reg), 4),
                comp_median=int(sz.median()), comp_p90=int(sz.quantile(.90)),
                singleton_comps=int((sz == 1).sum()),
                pairs_outside_giant=int(len(reg) - giant),
                max_heldout_frac=round(take / len(reg), 4),
                split_feasible=bool(take / len(reg) >= 0.8 * TARGET_TEST)))
            if (rid, nid) in {("0.30", "0.80"), ("0.50", "0.90"), ("0.70", "0.95"), ("0.90", "0.99")}:
                for k, v in sz.head(8).items():
                    detail.append(dict(rt_id=rid, nc_id=nid, rank=len(
                        [x for x in detail if x["rt_id"] == rid and x["nc_id"] == nid]) + 1,
                        pairs=int(v)))
            print(f"  RT {rid} / nc {nid}: {sz.size:6,} components  "
                  f"giant {giant:6,} ({giant/len(reg):6.2%})  "
                  f"max held-out {take/len(reg):5.2%}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "g0_component_structure.tsv", sep="\t", index=False)
    pd.DataFrame(detail).to_csv(OUT / "g0_component_top_sizes.tsv", sep="\t", index=False)
    print(f"\nwrote g0_component_structure.tsv ({len(df)} rows)")
    print("\nfeasible combinations (held-out >= 16% of pairs by whole components):")
    f = df[df.split_feasible]
    print(f[["rt_id", "nc_id", "components", "giant_frac", "max_heldout_frac"]].to_string(index=False)
          if len(f) else "  NONE - a giant component makes the proposed split impractical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
