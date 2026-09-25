#!/usr/bin/env python
"""embed_x1/x01 - build the RT conditioning array from the VERIFIED per-residue cache. Runs on Ibex.

Reduces each RT's per-residue ESM-C representation to K=32 equal-width mean-pooled chunks,
as declared in PREREG before any model existed. Runs on Ibex because the 21.6 GB token cache
lives there and transfers at ~12 MB/s; the derived array is ~1.8 GB.

Chunking rule, fixed: for an RT of length L, chunk j covers residues
[floor(j*L/K), floor((j+1)*L/K)) and is the mean over that span. When L < K some chunks are
empty; those are zero-filled AND flagged in a mask so cross-attention ignores them. The mask is
written out, not inferred downstream.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np

B = Path("/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings")
CACHE, K, DIM = "esmc300m_v1", 32, 960
OUT = B / "derived_rt_chunks"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    shards = sorted((B / CACHE / "shards").glob("shard_*"))
    hashes, chunks, masks, lens = [], [], [], []
    for sd in shards:
        idx = [l.split("\t") for l in (sd / "tokens_index.tsv").read_text().splitlines()[1:]]
        tok = np.load(sd / "tokens.npy", mmap_mode="r")
        # tokens_index.tsv columns are (seq_hash, offset, length) -- three, not four.
        for h, off, L in ((r[0], int(r[1]), int(r[2])) for r in idx):
            a = np.asarray(tok[off:off + L], dtype=np.float32)
            assert a.shape == (L, DIM), (h, a.shape)
            b = np.zeros((K, DIM), dtype=np.float32)
            m = np.zeros(K, dtype=bool)
            edges = [(j * L) // K for j in range(K + 1)]
            for j in range(K):
                s, e = edges[j], edges[j + 1]
                if e > s:
                    b[j] = a[s:e].mean(0); m[j] = True
            assert m.any(), h
            hashes.append(h); chunks.append(b.astype(np.float16)); masks.append(m); lens.append(L)
        print(f"  {sd.name}: {len(idx):,} cumulative {len(hashes):,}", flush=True)

    C = np.stack(chunks); M = np.stack(masks); Ln = np.array(lens, dtype=np.int32)
    assert C.shape == (29192, K, DIM), C.shape
    assert len(set(hashes)) == 29192
    np.save(OUT / "rt_chunks.npy", C)
    np.save(OUT / "rt_chunk_mask.npy", M)
    (OUT / "rt_chunk_index.tsv").write_text(
        "seq_hash\trow\taa_len\n" + "".join(f"{h}\t{i}\t{l}\n" for i, (h, l) in enumerate(zip(hashes, Ln))))
    meta = dict(cache=CACHE, K=K, dim=DIM, records=len(hashes),
                rule="chunk j = mean of residues [floor(jL/K), floor((j+1)L/K)); empty chunks "
                     "zero-filled and masked False",
                dtype="float16", shape=list(C.shape),
                short_rts_below_K=int((Ln < K).sum()),
                sha256_chunks=hashlib.sha256((OUT / "rt_chunks.npy").read_bytes()).hexdigest(),
                sha256_mask=hashlib.sha256((OUT / "rt_chunk_mask.npy").read_bytes()).hexdigest())
    (OUT / "PROVENANCE.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({k: v for k, v in meta.items() if k != "rule"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
