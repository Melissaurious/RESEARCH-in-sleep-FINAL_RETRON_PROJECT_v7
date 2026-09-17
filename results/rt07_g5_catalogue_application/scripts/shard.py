#!/usr/bin/env python3
"""g5 step A — deterministically shard the censused eligible population into FASTA shards.

    shard.py <shard_dir> [n_shards]

Sharding rule, from `rt07_g4b_production_mapper/docs/G5_EXECUTION_PLAN.md` §3:

  * the population is the CENSUSED ELIGIBLE set, read from the g5a partition - not the
    catalogue, and not re-derived here. The eligibility rule is applied exactly once, in g5a;
  * shards are assigned by the first 9 bits of a sha256 over the SEQUENCE ID, giving 512
    shards. Sharding on the identifier rather than on `rt_hash` guarantees that every record
    sharing an identifier lands in the same shard, so an identifier collision cannot hide by
    being split across two (review finding R2). In this catalogue the identifier IS the
    sequence hash and the census found 0 collisions, so the guarantee is currently vacuous -
    it is kept because the runner's contract should not depend on that staying true;
  * within a shard, records are written in sorted identifier order, so shard contents are a
    pure function of the input and the shard count.

Writes `<shard_dir>/shard_XXXX.faa` plus `shard_index.tsv` (shard, n_sequences, sha256).
"""
import hashlib
import os
import sys

ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
G4B = f"{ROOT}/results/rt07_g4b_production_mapper"
sys.path.insert(0, f"{G4B}/code")
from rtmap import run_mapper as R           # noqa: E402

FAA = f"{ROOT}/data/derived/rt_exact_v1.faa"
PARTITION = f"{ROOT}/data/derived/rt07_g5a/g5a_eligibility_partition.tsv.gz"

SHARD_DIR = sys.argv[1]
N_SHARDS = int(sys.argv[2]) if len(sys.argv) > 2 else 512


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def shard_of(sid, n):
    return int.from_bytes(hashlib.sha256(sid.encode()).digest()[:2], "big") % n


def main():
    import gzip
    eligible = set()
    with gzip.open(PARTITION, "rt") as f:
        cols = f.readline().rstrip("\n").split("\t")
        i_h, i_e = cols.index("rt_seq_hash"), cols.index("eligible")
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if p[i_e] == "True":
                eligible.add(p[i_h])
    print(f"censused eligible population: {len(eligible)}")

    # Read the catalogue and keep only the censused-eligible records. The eligibility rule is
    # NOT re-applied here: g5a is the single place it runs, and this step must not be able to
    # disagree with it.
    kept = {}
    for sid, raw in R.read_fasta(FAA):
        if sid in eligible:
            kept[sid] = R.clean(raw)
    if len(kept) != len(eligible):
        raise SystemExit(f"FAIL CLOSED: {len(kept)} sequences recovered for "
                         f"{len(eligible)} censused-eligible ids")

    os.makedirs(SHARD_DIR, exist_ok=True)
    buckets = {}
    for sid in sorted(kept):
        buckets.setdefault(shard_of(sid, N_SHARDS), []).append(sid)

    rows, written = [], 0
    for s in range(N_SHARDS):
        ids = buckets.get(s, [])
        path = f"{SHARD_DIR}/shard_{s:04d}.faa"
        with open(path, "w") as f:
            for sid in ids:
                f.write(f">{sid}\n{kept[sid]}\n")
        written += len(ids)
        rows.append((f"shard_{s:04d}", len(ids), sha256_file(path)))
    if written != len(kept):
        raise SystemExit(f"FAIL CLOSED: wrote {written} of {len(kept)} sequences")

    with open(f"{SHARD_DIR}/shard_index.tsv", "w") as f:
        f.write("shard\tn_sequences\tsha256\n")
        for name, n, h in rows:
            f.write(f"{name}\t{n}\t{h}\n")

    sizes = sorted(n for _, n, _ in rows)
    print(f"{N_SHARDS} shards, {written} sequences")
    print(f"shard size: min {sizes[0]}  median {sizes[len(sizes) // 2]}  max {sizes[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
