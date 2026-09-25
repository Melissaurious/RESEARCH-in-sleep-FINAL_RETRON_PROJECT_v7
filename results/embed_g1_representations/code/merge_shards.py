#!/usr/bin/env python
"""embed_g1/merge_shards.py - verify the shard set and build the cache-level index.

DELIBERATELY DOES NOT CONCATENATE THE TOKEN FILES. ESM-C's per-residue cache is ~21.6 GiB;
rewriting it into one array would double the storage and the IO for no gain, since a global
index over (shard, offset, length) memory-maps just as well. Shard files stay as produced and
stay mode 444.

WHAT IT ACTUALLY CHECKS - each of these can fail:
  1 every shard named by the frozen sharding rule is present;
  2 each shard's files match the sha256 its own DONE.json recorded;
  3 the union of shard members is EXACTLY the input universe - no missing hash, no extra
    hash, no hash claimed by two shards;
  4 each shard's members are exactly the contiguous block of the frozen (len, hash) order
    that its index implies, so a shard cannot silently hold the right count of wrong
    sequences;
  5 the summed sequence and residue/nucleotide counts equal the declared totals;
  6 pooled row count and token row count agree with the indices;
  7 every shard's declared frozen contract (model, dim, dtype, pooling, special tokens,
    batching rule) is IDENTICAL across shards - a cache assembled from two different
    contracts is not one cache.

Writes manifests/<cache>.tsv, manifests/<cache>_pooled_index.tsv,
manifests/<cache>_tokens_index.tsv and manifests/<cache>_provenance.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

DECLARED = {
    "esmc300m_v1": {"n": 29_192, "units": 11_236_474, "dim": 960,
                    "fasta": "rt_pair_universe.faa"},
    "rinalmo_giga_v1": {"n": 16_458, "units": 2_719_581, "dim": 1280,
                        "fasta": "rt_ncrna_oriented_v1.fna"},
}
# fields that MUST agree across every shard of one cache
CONTRACT = ["model", "model_id", "dim", "dtype", "layer", "pooling", "special_tokens",
            "orientation_rule", "alphabet_rule", "batching_rule", "truncation",
            "weights_identity", "torch", "package_version", "input_fasta_sha256",
            # gpu_arch is in here deliberately. Compute capability decides kernel selection and
            # reduction order, so a cache half-produced on sm_80 (A100) and half on sm_89
            # (RTX 4090) is two computations wearing one name. Without this the mix would slip
            # through for ESM-C, where Ibex and borg run the SAME torch 2.5.1 and every other
            # contract field matches. A100-40GB and A100-80GB are both sm_80 and stay
            # interchangeable, which is why this is the arch and not the device name.
            "gpu_arch"]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_fasta_lens(p: Path) -> dict[str, int]:
    out, sid, n = {}, None, 0
    with p.open() as fh:
        for line in fh:
            if line.startswith(">"):
                if sid:
                    out[sid] = n
                sid, n = line[1:].split()[0], 0
            else:
                n += len(line.strip())
    if sid:
        out[sid] = n
    return out


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", type=Path,
                    default=Path("/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings"))
    ap.add_argument("--cache", required=True, choices=sorted(DECLARED))
    a = ap.parse_args()
    d = DECLARED[a.cache]
    shards_dir = a.base / a.cache / "shards"
    man = a.base / "manifests"
    man.mkdir(parents=True, exist_ok=True)

    lens = read_fasta_lens(a.base / "inputs" / d["fasta"])
    order = sorted(lens, key=lambda s: (lens[s], s))
    if len(order) != d["n"]:
        fail(f"input FASTA has {len(order)} sequences, declared {d['n']}")

    shard_dirs = sorted(p for p in shards_dir.iterdir()
                        if p.is_dir() and p.name.startswith("shard_"))
    print(f"[1] {len(shard_dirs)} shard directories under {shards_dir}")
    if not shard_dirs:
        fail("no shards present")

    seen: dict[str, str] = {}
    contract_ref, rows_pool, rows_tok, man_rows = None, [], [], []
    total_units = 0
    for sd in shard_dirs:
        done = sd / "DONE.json"
        if not done.is_file():
            fail(f"{sd.name} has no DONE.json - it did not complete")
        rec = json.loads(done.read_text())
        for f, h in rec["sha256"].items():
            got = sha256_file(sd / f)
            if got != h:
                fail(f"{sd.name}/{f} sha256 {got[:16]} != recorded {h[:16]}")
            man_rows.append(f"{a.cache}/shards/{sd.name}/{f}\t{got}\t{(sd/f).stat().st_size}")
        prov = json.loads((sd / "PROVENANCE.json").read_text())

        # 7 - one contract across the whole cache
        cur = {k: prov.get(k) for k in CONTRACT}
        if contract_ref is None:
            contract_ref = cur
        elif cur != contract_ref:
            diff = {k: (contract_ref[k], cur[k]) for k in CONTRACT if contract_ref[k] != cur[k]}
            fail(f"{sd.name} was produced under a DIFFERENT frozen contract: {diff}")

        idx = [l.split("\t") for l in
               (sd / "pooled_index.tsv").read_text().splitlines()[1:]]
        tix = [l.split("\t") for l in
               (sd / "tokens_index.tsv").read_text().splitlines()[1:]]
        if len(idx) != rec["n"] or len(tix) != rec["n"]:
            fail(f"{sd.name} index rows {len(idx)}/{len(tix)} != n {rec['n']}")

        members = [r[0] for r in idx]
        for h in members:
            if h in seen:
                fail(f"sequence {h[:16]} claimed by both {seen[h]} and {sd.name}")
            seen[h] = sd.name

        # 4 - the shard is the contiguous block its position implies
        k = int(sd.name.split("_")[1])
        ss = prov["shard_size"]
        expect = order[k * ss:(k + 1) * ss]
        if members != expect:
            fail(f"{sd.name} members are not the frozen contiguous block "
                 f"[{k*ss}:{k*ss+len(expect)}] of the (len, hash) order")

        pv = np.load(sd / "pooled.npy", mmap_mode="r")
        tv = np.load(sd / "tokens.npy", mmap_mode="r")
        # pooled_index.tsv columns are (seq_hash, row, seq_len) -> lengths are r[2], NOT r[1].
        # r[1] is the row index; summing it yields n*(n-1)/2, which for a 4096-sequence shard
        # is 8,386,560 - a plausible-looking number that has nothing to do with the data.
        su = sum(int(r[2]) for r in idx)
        if pv.shape != (rec["n"], d["dim"]) or pv.dtype != np.float16:
            fail(f"{sd.name} pooled {pv.shape} {pv.dtype}")
        if tv.shape != (su, d["dim"]) or tv.dtype != np.float16:
            fail(f"{sd.name} tokens {tv.shape} != {(su, d['dim'])}")
        for h, l in ((r[0], int(r[2])) for r in idx):
            if l != lens[h]:
                fail(f"{sd.name}: {h[:16]} length {l} != FASTA {lens[h]}")
        total_units += su
        for r in idx:
            rows_pool.append(f"{r[0]}\t{sd.name}\t{r[1]}\t{r[2]}")
        for r in tix:
            rows_tok.append(f"{r[0]}\t{sd.name}\t{r[1]}\t{r[2]}")
        print(f"    {sd.name}: {rec['n']:5,} seq  {su:9,} units  "
              f"{prov['units_per_s']:>9,.0f} u/s  VRAM {prov['peak_vram_gb']:.2f} GB  "
              f"RSS {prov['peak_host_rss_gb']:.2f} GB  {prov['gpu']}")

    print(f"\n[2] coverage")
    missing, extra = set(order) - set(seen), set(seen) - set(order)
    if missing:
        fail(f"{len(missing)} sequences have NO representation, e.g. {sorted(missing)[:3]}")
    if extra:
        fail(f"{len(extra)} representations are not in the universe")
    if len(seen) != d["n"]:
        fail(f"{len(seen)} covered, declared {d['n']}")
    if total_units != d["units"]:
        fail(f"{total_units:,} residues/nt, declared {d['units']:,}")
    print(f"    OK  {len(seen):,}/{d['n']:,} sequences, {total_units:,}/{d['units']:,} units, "
          f"no duplicates, no gaps")

    (man / f"{a.cache}_pooled_index.tsv").write_text(
        "seq_hash\tshard\trow\tseq_len\n" + "\n".join(rows_pool) + "\n")
    (man / f"{a.cache}_tokens_index.tsv").write_text(
        "seq_hash\tshard\toffset\tlength\n" + "\n".join(rows_tok) + "\n")
    (man / f"{a.cache}.tsv").write_text(
        "path\tsha256\tbytes\n" + "\n".join(sorted(man_rows)) + "\n")
    (man / f"{a.cache}_provenance.json").write_text(json.dumps(
        {"cache": a.cache, "sequences": len(seen), "units": total_units,
         "dim": d["dim"], "shards": len(shard_dirs),
         "frozen_contract": contract_ref,
         "token_layout": "per-shard tokens.npy, ragged; use manifests/"
                         f"{a.cache}_tokens_index.tsv -> (shard, offset, length)",
         "pooled_layout": "per-shard pooled.npy; use manifests/"
                          f"{a.cache}_pooled_index.tsv -> (shard, row)"},
        indent=2, sort_keys=True) + "\n")
    print(f"\n[3] wrote manifests/{a.cache}.tsv, _pooled_index.tsv, _tokens_index.tsv, "
          f"_provenance.json")
    print("\nCACHE VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
