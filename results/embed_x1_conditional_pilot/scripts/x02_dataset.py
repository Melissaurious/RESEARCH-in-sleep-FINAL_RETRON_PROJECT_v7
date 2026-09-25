#!/usr/bin/env python
"""embed_x1/x02 - build the modelling dataset from the FROZEN split. No modelling here.

Emits a single .npz that the training env (retron_esmc: torch + einops, NO pyarrow) can read.
The frozen split is consumed as-is: component ids, fold labels, tier flags and the
near-duplicate sensitivity flag all come straight from results/embed_g2b_frozen_split/ and are
never recomputed.

VOCABULARY, declared in PREREG before any model existed:
    0 <pad>  1 <bos>  2 <eos>  3 A  4 C  5 G  6 T  7 K  8 N  9 R  10 Y
The four IUPAC codes actually present in the corpus (K N R Y) are KEPT AS TOKENS - not
substituted, not filtered. No sequence is removed from any fold.
"""
from __future__ import annotations
import gzip, hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[1]
W = TASK / "work"
SPLIT = ROOT / "results" / "embed_g2b_frozen_split"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
VOCAB = {"<pad>": 0, "<bos>": 1, "<eos>": 2,
         "A": 3, "C": 4, "G": 5, "T": 6, "K": 7, "N": 8, "R": 9, "Y": 10}
PAD, BOS, EOS = 0, 1, 2


def read_fasta(p):
    s, sid, buf = {}, None, []
    for l in p.read_text().splitlines():
        if l.startswith(">"):
            if sid: s[sid] = "".join(buf)
            sid, buf = l[1:].split()[0], []
        else: buf.append(l.strip())
    if sid: s[sid] = "".join(buf)
    return s


def main() -> int:
    W.mkdir(parents=True, exist_ok=True)
    asg = pd.read_csv(gzip.open(SPLIT / "tables" / "split_assignment.tsv.gz"), sep="\t")
    assert len(asg) == 30_924
    assert asg.fold.value_counts().to_dict() == {"train": 21647, "val": 4639, "test": 4638}
    assert int(asg.in_sensitivity_population.sum()) == 1525
    print(f"[1] frozen split consumed unchanged: {asg.fold.value_counts().to_dict()}")

    nc = read_fasta(ROOT / "data" / "derived" / "rt_ncrna_oriented_v1.fna")
    assert len(nc) == 16_458
    alpha = sorted({c for s in nc.values() for c in s})
    assert set(alpha) <= set(VOCAB), f"unexpected ncRNA characters: {set(alpha) - set(VOCAB)}"
    print(f"[2] ncRNA alphabet {''.join(alpha)} - all in the declared vocabulary")

    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet",
                      columns=["rt_seq_hash", "nc_seq_hash", "geometry_eligible",
                               "detection_model"]).to_pandas()
    pm = (p[p.geometry_eligible].groupby(["rt_seq_hash", "nc_seq_hash"])
          .detection_model.agg(lambda s: s.mode().iat[0]).rename("retron_type"))
    asg = asg.merge(pm, on=["rt_seq_hash", "nc_seq_hash"], how="left")
    assert asg.retron_type.notna().all()
    types = sorted(asg.retron_type.unique())
    tix = {t: i for i, t in enumerate(types)}
    print(f"[3] {len(types)} retron types")

    rx = pq.read_table(CANON / "rt_exact_v1.parquet",
                       columns=["rt_seq_hash", "rt_aa_len"]).to_pandas()
    asg = asg.merge(rx, on="rt_seq_hash", how="left")
    assert asg.rt_aa_len.notna().all()

    # --- tokenise the ncRNA: <bos> seq <eos>, right-padded to the corpus max -------------
    order = sorted(nc)
    nrow = {h: i for i, h in enumerate(order)}
    Lmax = max(len(s) for s in nc.values()) + 2
    tok = np.zeros((len(order), Lmax), dtype=np.int16)
    ncl = np.zeros(len(order), dtype=np.int32)
    for h in order:
        s = nc[h]
        ids = [BOS] + [VOCAB[c] for c in s] + [EOS]
        tok[nrow[h], :len(ids)] = ids
        ncl[nrow[h]] = len(ids)
    print(f"[4] tokenised {len(order):,} ncRNA, padded length {Lmax} "
          f"(longest sequence {Lmax-2} nt)")

    out = dict(
        nc_tokens=tok, nc_len=ncl,
        nc_row=asg.nc_seq_hash.map(nrow).values.astype(np.int32),
        # np.str_ explicitly: pandas Arrow-backed string columns give OBJECT dtype via
        # .astype(str), and an object array cannot be loaded from .npz without allow_pickle.
        rt_hash=np.array(asg.rt_seq_hash.astype(str).tolist(), dtype=np.str_),
        nc_hash=np.array(asg.nc_seq_hash.astype(str).tolist(), dtype=np.str_),
        fold=np.array(asg.fold.astype(str).tolist(), dtype=np.str_),
        component=np.array(asg.component_id.astype(str).tolist(), dtype=np.str_),
        type_id=asg.retron_type.map(tix).values.astype(np.int16),
        retron_type=np.array(asg.retron_type.astype(str).tolist(), dtype=np.str_),
        rt_aa_len=asg.rt_aa_len.values.astype(np.int32),
        sensitivity=asg.in_sensitivity_population.values.astype(np.int8),
        T1=asg.T1.values.astype(np.int8), T2=asg.T2.values.astype(np.int8),
        T3=asg.T3.values.astype(np.int8), T4=asg.T4.values.astype(np.int8),
        types=np.array(list(map(str, types)), dtype=np.str_),
        nc_order=np.array(list(map(str, order)), dtype=np.str_),
    )
    np.savez_compressed(W / "dataset.npz", **out)
    meta = dict(vocab=VOCAB, pad_len=int(Lmax), n_pairs=int(len(asg)),
                n_ncrna=len(order), n_types=len(types),
                folds=asg.fold.value_counts().to_dict(),
                sensitivity_pairs=int(asg.in_sensitivity_population.sum()),
                split_source="results/embed_g2b_frozen_split (commit 15e00b8)",
                sha256=hashlib.sha256((W / "dataset.npz").read_bytes()).hexdigest())
    (W / "dataset_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"[5] wrote work/dataset.npz  sha256 {meta['sha256'][:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
