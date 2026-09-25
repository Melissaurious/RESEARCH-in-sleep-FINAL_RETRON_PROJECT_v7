#!/usr/bin/env python
"""embed-g0/a02 - reconstruct the oriented ncRNA sequences for the PAIR-ELIG universe.

WHY THIS EXISTS. `data/derived/` carries `nc_seq_hash` and `nc_seq_len` but NO ncRNA
sequence. Without the sequences there is no RiNALMo representation and no ncRNA clustering,
so this is the one new data product the embedding track needs.

WHAT MAKES IT SAFE. `nc_seq_hash` was defined in dbchar_g2 as

    sha256(ncrnas[j]["sequence_oriented"].upper())          (e01_extract.py:294)

so the hash is ALREADY the hash of the ORIENTED sequence. Every sequence written here has
its sha256 recomputed and asserted equal to the registered `nc_seq_hash`. The FASTA is
therefore self-verifying: it cannot silently contain the wrong molecule, the wrong strand or
a sequence from the wrong record. The run REQUIRES 16,458/16,458 and fails otherwise.

ADDRESSING. Every eligible placement carries (source_file, line_no, ncrna_idx). `line_no` is
the 1-BASED GLOBAL line number in the raw file (m02_build_tables.py:70,
`local_line + 1 + line_offset`). Only the needed lines are JSON-parsed. If the addressing
were wrong the hash assertion would fire -- the address is a hint, the hash is the contract.

DETERMINISM. Output order is `sorted(nc_seq_hash)`, one sequence per line, uppercase DNA
alphabet as stored. Re-running produces a byte-identical file; its sha256 is recorded.

Inputs are READ-ONLY. Writes only under data/derived/ and this task's ARIS_OUTPUT.
Env: /home/borg/miniconda3/envs/retron_tradicional/bin/python
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
DERIVED = ROOT / "data" / "derived"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
RAW = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june")
TASK = Path(__file__).resolve().parents[1]
STEM = "rt_ncrna_oriented_v1"
EXPECT_N = 16_458
PRODUCER = "embed_g0/a02_ncrna_fasta.py"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    t0 = time.perf_counter()
    DERIVED.mkdir(parents=True, exist_ok=True)

    # ---- 1 - the universe, from the registered resource ------------------------------
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet",
                        columns=["nc_seq_hash"]).to_pandas()
    want = set(reg.nc_seq_hash.unique())
    if len(want) != EXPECT_N:
        raise AssertionError(f"universe is {len(want)}, expected {EXPECT_N}")
    print(f"[1] universe: {len(want):,} unique oriented ncRNA hashes")

    # ---- 2 - one raw-corpus address per hash ------------------------------------------
    cols = ["nc_seq_hash", "source_file", "line_no", "ncrna_idx", "nc_seq_len",
            "geometry_eligible", "nc_strand", "orientation_corrected", "detection_model"]
    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet", columns=cols).to_pandas()
    e = p[p.geometry_eligible & p.nc_seq_hash.isin(want)]
    if not bool(e.orientation_corrected.all()):
        raise AssertionError("a target placement is not orientation_corrected")
    addr = (e.sort_values(["source_file", "line_no", "ncrna_idx"])
              .drop_duplicates("nc_seq_hash"))
    if len(addr) != EXPECT_N:
        raise AssertionError(f"addresses for {len(addr)}, expected {EXPECT_N}")
    want_len = dict(zip(addr.nc_seq_hash, addr.nc_seq_len))
    print(f"[2] addresses: {len(addr):,} over {addr.source_file.nunique()} raw files")

    # ---- 3 - stream the raw corpus, parse only the addressed lines --------------------
    plan: dict[str, dict[int, list[tuple[int, str]]]] = defaultdict(lambda: defaultdict(list))
    for h, f, ln, ix in zip(addr.nc_seq_hash, addr.source_file, addr.line_no, addr.ncrna_idx):
        plan[f][int(ln)].append((int(ix), h))

    seqs: dict[str, str] = {}
    mismatch: list[tuple[str, str, str]] = []
    for fname in sorted(plan):
        src = RAW / fname
        if not src.is_file():
            raise AssertionError(f"raw file missing: {src}")
        lines = plan[fname]
        hit = 0
        with src.open("r") as fh:
            for n, line in enumerate(fh, start=1):          # line_no is 1-BASED
                tgt = lines.get(n)
                if tgt is None:
                    continue
                ncs = json.loads(line).get("ncrnas") or []
                for ix, h in tgt:
                    so = ncs[ix].get("sequence_oriented")
                    if not isinstance(so, str) or not so:
                        raise AssertionError(f"{fname}:{n}[{ix}] has no sequence_oriented")
                    s = so.upper()
                    got = hashlib.sha256(s.encode()).hexdigest()
                    if got != h:
                        mismatch.append((h, got, f"{fname}:{n}[{ix}]"))
                        continue
                    if len(s) != want_len[h]:
                        raise AssertionError(f"{h}: length {len(s)} != registered {want_len[h]}")
                    seqs[h] = s
                    hit += 1
                lines.pop(n)
                if not lines:
                    break
        print(f"    {fname:<46} {hit:6,} recovered", flush=True)

    # ---- 4 - the contract: 16,458 / 16,458 ------------------------------------------
    print(f"\n[3] hash round-trip: {len(seqs):,}/{EXPECT_N:,} verified, "
          f"{len(mismatch)} mismatches, {len(want - set(seqs)):,} unrecovered")
    if mismatch:
        for h, got, where in mismatch[:5]:
            print(f"    MISMATCH {where}: registered {h[:16]} got {got[:16]}")
        raise AssertionError(f"{len(mismatch)} sequences failed the hash round-trip")
    if len(seqs) != EXPECT_N:
        raise AssertionError(f"recovered {len(seqs)}, required {EXPECT_N}")
    print("    OK  every sequence hashes to its registered nc_seq_hash")

    # ---- 5 - deterministic outputs ---------------------------------------------------
    order = sorted(seqs)
    fa = DERIVED / f"{STEM}.fna"
    with fa.open("w") as fh:
        for h in order:
            fh.write(f">{h} len={len(seqs[h])}\n{seqs[h]}\n")
    meta = (addr.set_index("nc_seq_hash").reindex(order)
                .reset_index()[["nc_seq_hash", "nc_seq_len", "nc_strand",
                                "detection_model", "source_file", "line_no", "ncrna_idx"]])
    meta["nc_seq"] = [seqs[h] for h in order]
    pqp = DERIVED / f"{STEM}.parquet"
    pq.write_table(pa.Table.from_pandas(meta, preserve_index=False), pqp, compression="zstd")

    alphabet = sorted({c for s in seqs.values() for c in s})
    lens = pd.Series([len(seqs[h]) for h in order])
    prov = {
        "dataset": STEM, "unit": "exact oriented ncRNA sequence", "key": "nc_seq_hash",
        "records": len(order), "producer": PRODUCER,
        "producer_sha256": sha256_file(Path(__file__)),
        "git_rev": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip(),
        "population": "PAIR-ELIG - rt_ncrna_exact_pairs_v1.parquet (30,924 pairs)",
        "orientation_rule": "sequence_oriented as stored in the raw corpus; "
                            "all source placements orientation_corrected=True",
        "hash_rule": "sha256(sequence_oriented.upper()) == nc_seq_hash (dbchar_g2 e01_extract.py:294)",
        "round_trip_verified": f"{len(seqs)}/{EXPECT_N}",
        "alphabet": "".join(alphabet),
        "len_min": int(lens.min()), "len_median": int(lens.median()),
        "len_max": int(lens.max()), "len_total": int(lens.sum()),
        "order": "sorted(nc_seq_hash) - byte-reproducible",
        "raw_corpus": str(RAW),
        "raw_corpus_pin": "dbchar_g1 record-manifest sha256 "
                          "8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00",
        "inputs": ["rt_ncrna_exact_pairs_v1.parquet", "rt_ncrna_pairs_v1.parquet"],
        # NO TIMING FIELD HERE. A wall-clock number makes this file - and therefore its sha256
        # in the manifest - differ on every run, which silently breaks the byte-reproducibility
        # contract the manifest exists to assert. Timing goes to stdout and the log.
    }
    (DERIVED / f"{STEM}.provenance.json").write_text(json.dumps(prov, indent=2) + "\n")

    man = ["path\tbytes\tsha256"]
    for f in (fa, pqp, DERIVED / f"{STEM}.provenance.json"):
        man.append(f"data/derived/{f.name}\t{f.stat().st_size}\t{sha256_file(f)}")
    (DERIVED / f"{STEM}.MANIFEST.tsv").write_text("\n".join(man) + "\n")
    (TASK / "tables" / "g0_ncrna_fasta_manifest.tsv").write_text("\n".join(man) + "\n")

    print(f"\n[4] wrote  {fa.name}  {fa.stat().st_size:,} B")
    print(f"           {pqp.name}  {pqp.stat().st_size:,} B")
    print(f"    alphabet {alphabet}  len {lens.min()}-{lens.max()} median {int(lens.median())}")
    print("\n".join("    " + r for r in man))
    print(f"\nDONE in {time.perf_counter() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
