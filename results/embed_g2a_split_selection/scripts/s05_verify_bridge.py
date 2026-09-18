#!/usr/bin/env python
"""embed_g2/s05 - does the fragment bridge actually CLOSE the channel it was built to close?

Option B's entire justification is that bridging removes near-identical cross-boundary pairs.
That is a claim about the resulting split, and it is checked here rather than assumed: the
exact held-out-vs-training probe is re-run ON THE BRIDGED SPLIT and the same three crossing
criteria are recounted. It also reports the ALIGNED LENGTH behind each surviving crossing,
because "90% identity over 30% coverage" means 118 nt on a 395 nt ncRNA and 10 nt on a 34 nt
one, and only one of those is evidence.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s04_fragment_bridge import (  # noqa: E402
    CANON, G0, ROOT, KEY, CRITERIA, assign, build, exact_probe, neff, read_cd, read_mm,
    read_fasta)

W, OUT = Path(__file__).resolve().parents[1] / "work", Path(__file__).resolve().parents[1] / "tables"
BRIDGE = (0.90, 0.30)   # the only variant that survived the n_eff test in s04


def main() -> int:
    tmp = Path(__import__("os").environ.get("TMPDIR", "/tmp")) / "g2verify"
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet", columns=KEY).to_pandas()
    n = len(reg)
    rmap, nmap = read_mm(G0 / "rt_id0.50_cluster.tsv"), read_cd(G0 / "nc_id0.80.clstr")
    rt_seqs = read_fasta(ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa")
    nc_seqs = read_fasta(ROOT / "data/derived/rt_ncrna_oriented_v1.fna")

    mid, mcov = BRIDGE
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

    br = rt_all[(rt_all.fident >= mid) & (rt_all.aln_cov >= mcov)]
    bn = nc_all[(nc_all.fident >= mid) & (nc_all.aln_cov >= mcov)]
    print(f"bridge {mid}/{mcov}: ncRNA bridge aligned length "
          f"min {bn.length.min()} p25 {int(bn.length.quantile(.25))} "
          f"median {int(bn.length.median())} max {bn.length.max()}")
    bridges_rt = [(a, b) for a, b in zip(br.q, br.t) if rmap.get(a) != rmap.get(b)]
    bridges_nc = [(a, b) for a, b in zip(bn.q, bn.t) if nmap.get(a) != nmap.get(b)]

    rows = []
    for tag, brt, bnc in (("A - no bridge", None, None),
                          (f"B - bridge {mid}/{mcov}", bridges_rt, bridges_nc)):
        comp = build(reg, rmap, nmap, brt, bnc)
        sz = pd.Series(comp).value_counts()
        fold = assign(sz, n)
        pf = np.array([fold[c] for c in comp])
        tr = pf != "test"
        tr_rt, tr_nc = set(reg.rt_seq_hash.values[tr]), set(reg.nc_seq_hash.values[tr])
        te_rt = set(reg.rt_seq_hash.values[~tr]) - tr_rt
        te_nc = set(reg.nc_seq_hash.values[~tr]) - tr_nc
        print(f"\n=== {tag}: test {int((~tr).sum()):,} pairs, "
              f"{len(te_rt):,} RT / {len(te_nc):,} ncRNA held out")
        for kind, seqs, te, trn in (("RT", rt_seqs, te_rt, tr_rt),
                                    ("ncRNA", nc_seqs, te_nc, tr_nc)):
            h = exact_probe(tmp / f"{tag[0]}{kind}", seqs, te, trn,
                            "rt" if kind == "RT" else "nc")
            for name, i_, c_ in CRITERIA:
                s = h[(h.fident >= i_) & (h.aln_cov >= c_)]
                rows.append(dict(option=tag, modality=kind, criterion=name,
                                 n_heldout=len(te), n_crossing=int(s.q.nunique()),
                                 frac=round(s.q.nunique() / len(te), 4)))
                print(f"    {kind:<6} {name:<24} {s.q.nunique():>6,}/{len(te):,} "
                      f"= {s.q.nunique()/len(te):7.2%}")
    pd.DataFrame(rows).to_csv(OUT / "g2_bridge_verification.tsv", sep="\t", index=False)
    subprocess.run(["rm", "-rf", str(tmp)], check=False)
    print("\nwrote g2_bridge_verification.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
