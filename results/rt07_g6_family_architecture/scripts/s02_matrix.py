#!/usr/bin/env python3
"""s02 - build the frozen-state representation: one 150-length call-state profile per exact RT.

Reads g5_states.parquet only. Nothing is re-mapped, re-fitted or re-thresholded.

The 150 anchor states are taken in their frozen anchor_index order (1..150), which the frozen
instrument emits as state_id 107..317. That ordering is a property of the FROZEN ANCHOR SET,
read here from the g5 output itself, and it is VERIFIED in this script rather than assumed.

Writes to scratch (large, regenerable):
  work/profiles.npz    codes[n_seq, 150] int8, and the rt_hash index
"""
import os
import sys

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g6lib import G5, N_STATES, TABLES, WORK, write_tsv  # noqa: E402

CODE = {"MAPPED": 0, "AMBIGUOUS": 1, "UNSUPPORTED": 2, "DELETED_STATE": 3}
NAME = {v: k for k, v in CODE.items()}


def main():
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(G5, "g5_states.parquet")
    pf = pq.ParquetFile(path)
    n_rows = pf.metadata.num_rows
    if n_rows % N_STATES:
        raise SystemExit(f"s02: {n_rows} state rows is not a multiple of {N_STATES}")
    n_seq = n_rows // N_STATES
    print(f"s02: {n_rows} state rows / {N_STATES} = {n_seq} sequences")

    codes = np.empty((n_seq, N_STATES), dtype=np.int8)
    hashes = []
    state_ids = None
    row = 0
    checked = 0
    for batch in pf.iter_batches(batch_size=N_STATES * 4000,
                                 columns=["rt_hash", "anchor_index", "call_state", "state_id"]):
        m = len(batch)
        if m % N_STATES:
            raise SystemExit("s02: a batch did not align to a sequence boundary")
        blocks = m // N_STATES
        ai = np.asarray(batch.column("anchor_index"), dtype=np.int32).reshape(blocks, N_STATES)
        if not np.all(ai == np.arange(1, N_STATES + 1)):
            raise SystemExit("s02: anchor_index does not run 1..150 in every block")
        sid = np.asarray(batch.column("state_id"), dtype=np.int32).reshape(blocks, N_STATES)
        if state_ids is None:
            state_ids = sid[0].copy()
        if not np.all(sid == state_ids):
            raise SystemExit("s02: the frozen state_id order is not constant across sequences")
        rh = batch.column("rt_hash").to_pylist()
        rhb = np.array(rh, dtype=object).reshape(blocks, N_STATES)
        if not np.all(rhb == rhb[:, :1]):
            raise SystemExit("s02: rt_hash is not constant within a 150-row block")
        hashes.extend(rhb[:, 0].tolist())
        cs = batch.column("call_state").to_pylist()
        arr = np.fromiter((CODE[c] for c in cs), dtype=np.int8, count=m).reshape(blocks, N_STATES)
        codes[row:row + blocks] = arr
        row += blocks
        checked += blocks
    if row != n_seq:
        raise SystemExit(f"s02: filled {row} of {n_seq} rows")
    hashes = np.array(hashes)
    if len(set(hashes.tolist())) != n_seq:
        raise SystemExit("s02: rt_hash is not unique per sequence")

    np.savez_compressed(os.path.join(WORK, "profiles.npz"),
                        codes=codes, rt_hash=hashes, state_ids=state_ids)

    # per-call-state totals, for the record - all four reported, none collapsed
    rows = []
    for c, name in NAME.items():
        n = int((codes == c).sum())
        rows.append(dict(call_state=name, n_state_calls=n,
                         fraction=f"{n / (n_seq * N_STATES):.6f}",
                         unit="exact RT x frozen anchor state",
                         denominator=f"{n_seq * N_STATES} = {n_seq} x {N_STATES}"))
    write_tsv(os.path.join(TABLES, "g6_call_state_totals.tsv"),
              ["call_state", "n_state_calls", "fraction", "unit", "denominator"], rows)
    print(f"s02: verified {checked} blocks; frozen anchor state_id span "
          f"{state_ids.min()}-{state_ids.max()}")
    for r in rows:
        print(f"  {r['call_state']:<14} {r['n_state_calls']:>12}  {r['fraction']}")


if __name__ == "__main__":
    main()
