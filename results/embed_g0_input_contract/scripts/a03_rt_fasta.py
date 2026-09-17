#!/usr/bin/env python
"""embed-g0/a03 - RT protein FASTA for the PAIR-ELIG universe (29,192 exact RTs).

A projection of the canonical `rt_exact_v1.parquet` onto the pair universe. Not a new
measurement; it exists so mmseqs and ESM-C read the same 29,192 sequences in the same order.
Deterministic: sorted by rt_seq_hash, one sequence per line.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
OUT = Path(__file__).resolve().parents[1] / "work"   # sibling of scripts/, so a rerun from an
                                                     # assembled bundle writes into ITS own tree
EXPECT_N = 29_192


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reg = pq.read_table(CANON / "rt_ncrna_exact_pairs_v1.parquet",
                        columns=["rt_seq_hash"]).to_pandas()
    want = set(reg.rt_seq_hash.unique())
    assert len(want) == EXPECT_N, f"{len(want)} != {EXPECT_N}"

    rx = pq.read_table(CANON / "rt_exact_v1.parquet",
                       columns=["rt_seq_hash", "rt_aa_len", "rt_seq"]).to_pandas()
    rx = rx[rx.rt_seq_hash.isin(want)].sort_values("rt_seq_hash")
    assert len(rx) == EXPECT_N, f"resolved {len(rx)} of {EXPECT_N}"

    bad = [(h, n, len(s)) for h, n, s in zip(rx.rt_seq_hash, rx.rt_aa_len, rx.rt_seq)
           if len(s) != n]
    assert not bad, f"length disagreement rt_seq vs rt_aa_len: {bad[:3]}"
    alpha = sorted({c for s in rx.rt_seq for c in s})

    fa = OUT / "rt_pair_universe.faa"
    with fa.open("w") as fh:
        for h, s in zip(rx.rt_seq_hash, rx.rt_seq):
            fh.write(f">{h}\n{s}\n")
    sha = hashlib.sha256(fa.read_bytes()).hexdigest()
    print(f"wrote {fa}  {fa.stat().st_size:,} B  sha256 {sha}")
    print(f"  {len(rx):,} sequences  residues {int(rx.rt_aa_len.sum()):,}  alphabet {''.join(alpha)}")
    (OUT / "rt_pair_universe.json").write_text(json.dumps(
        {"records": len(rx), "sha256": sha, "alphabet": "".join(alpha),
         "order": "sorted(rt_seq_hash)",
         "source": "rt_exact_v1.parquet projected onto rt_ncrna_exact_pairs_v1"}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
