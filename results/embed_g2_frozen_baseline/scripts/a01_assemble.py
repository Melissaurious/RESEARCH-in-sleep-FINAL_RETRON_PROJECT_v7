#!/usr/bin/env python
"""embed_g2/a01 - assemble the analysis matrices. No modelling, no metrics.

Joins the frozen pooled representations to the FROZEN split and the metadata the negative
ladder needs. Every join is asserted total: a missing embedding or a missing fold label is a
hard failure, never a silently dropped row.

Pooled only. Token-level arrays are not opened - that stays DEFER in the launcher.
"""
from __future__ import annotations

import gzip
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
W = TASK / "work"
ROOT = TASK.parents[1]
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
SPLIT = ROOT / "results" / "embed_g2b_frozen_split"
KEY = ["rt_seq_hash", "nc_seq_hash"]


def load_pooled(cache: str, dim: int) -> tuple[dict[str, int], np.ndarray]:
    """Concatenate the per-shard pooled arrays into one matrix + hash->row index."""
    shards = sorted((W / cache / "shards").iterdir())
    mats, hashes = [], []
    for sd in shards:
        idx = pd.read_csv(sd / "pooled_index.tsv", sep="\t")
        a = np.load(sd / "pooled.npy")
        assert a.shape == (len(idx), dim), f"{sd.name}: {a.shape}"
        assert list(idx.row) == list(range(len(idx))), f"{sd.name}: index rows not 0..n-1"
        mats.append(a)
        hashes.extend(idx.seq_hash.tolist())
    M = np.concatenate(mats, axis=0).astype(np.float32)
    assert len(hashes) == len(set(hashes)), "duplicate hash across shards"
    print(f"    {cache}: {M.shape} from {len(shards)} shards")
    return {h: i for i, h in enumerate(hashes)}, M


def main() -> int:
    W.mkdir(parents=True, exist_ok=True)
    print("[1] pooled representations")
    rt_ix, RT = load_pooled("esmc300m_v1", 960)
    nc_ix, NC = load_pooled("rinalmo_giga_v1", 1280)
    assert len(rt_ix) == 29_192 and len(nc_ix) == 16_458

    print("[2] frozen split")
    asg = pd.read_csv(gzip.open(SPLIT / "tables" / "split_assignment.tsv.gz"), sep="\t")
    assert len(asg) == 30_924
    assert asg.fold.value_counts().to_dict() == {"train": 21647, "val": 4639, "test": 4638}
    assert int(asg.in_sensitivity_population.sum()) == 1525
    print(f"    {len(asg):,} pairs  "
          f"{asg.fold.value_counts().to_dict()}  sensitivity {int(asg.in_sensitivity_population.sum()):,}")

    miss_rt = set(asg.rt_seq_hash) - set(rt_ix)
    miss_nc = set(asg.nc_seq_hash) - set(nc_ix)
    assert not miss_rt and not miss_nc, f"missing embeddings: {len(miss_rt)} RT, {len(miss_nc)} nc"
    asg["rt_row"] = asg.rt_seq_hash.map(rt_ix).astype(int)
    asg["nc_row"] = asg.nc_seq_hash.map(nc_ix).astype(int)

    print("[3] metadata for the negative ladder")
    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet",
                      columns=KEY + ["geometry_eligible", "detection_model", "gc_content",
                                     "nc_seq_len", "tax_species", "taxonomy_system",
                                     "physical_locus_key"]).to_pandas()
    e = p[p.geometry_eligible]
    # one value per pair: the modal detection model, and the NCBI species where available
    pm = (e.groupby(KEY).detection_model.agg(lambda s: s.mode().iat[0]).rename("detection_model"))
    gc = e.groupby("nc_seq_hash").gc_content.median().rename("nc_gc")
    nl = e.groupby("nc_seq_hash").nc_seq_len.max().rename("nc_len")
    ncbi = e[e.taxonomy_system == "ncbi"]
    sp = (ncbi.groupby(KEY).tax_species.agg(lambda s: s.mode().iat[0] if len(s.mode()) else None)
          .rename("tax_species_ncbi"))
    loc = e.groupby(KEY).physical_locus_key.agg(lambda s: s.mode().iat[0]).rename("physical_locus")

    rx = pq.read_table(CANON / "rt_exact_v1.parquet",
                       columns=["rt_seq_hash", "rt_aa_len"]).to_pandas()
    asg = (asg.merge(pm, on=KEY, how="left").merge(sp, on=KEY, how="left")
              .merge(loc, on=KEY, how="left")
              .merge(gc, on="nc_seq_hash", how="left").merge(nl, on="nc_seq_hash", how="left")
              .merge(rx, on="rt_seq_hash", how="left"))
    assert asg.detection_model.notna().all() and asg.rt_aa_len.notna().all()
    assert asg.nc_gc.notna().all() and asg.nc_len.notna().all()
    print(f"    detection models {asg.detection_model.nunique()}   "
          f"NCBI species on {asg.tax_species_ncbi.notna().mean():.1%} of pairs")

    print("[4] true-partner map for false-negative exclusion")
    true_partners = asg.groupby("rt_seq_hash").nc_seq_hash.apply(set).to_dict()
    np.save(W / "rt_pooled.npy", RT)
    np.save(W / "nc_pooled.npy", NC)
    asg.to_parquet(W / "analysis_pairs.parquet", index=False)
    pd.to_pickle(true_partners, W / "true_partners.pkl")
    print(f"    max partners for one RT: {max(len(v) for v in true_partners.values())}")
    print(f"\nwrote work/rt_pooled.npy {RT.shape}, nc_pooled.npy {NC.shape}, "
          f"analysis_pairs.parquet {asg.shape}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
