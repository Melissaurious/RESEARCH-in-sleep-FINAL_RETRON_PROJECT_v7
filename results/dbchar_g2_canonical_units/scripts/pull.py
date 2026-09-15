#!/usr/bin/env python3
"""pull - run a declared view over the Stage-1 canonical tables (VIEWS.md).

A view is a query, not a copied subset. Every pull prints the filter cascade and the
population it ended on, so a number taken from it arrives with its denominator.

    python pull.py --derived data/derived --view V-RT --family Retron --count
    python pull.py --derived data/derived --view V-REC --record-key <file>:<line> --raw
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

VIEWS = {
    "V-REC": ("rt_records_v1.parquet", None),
    "V-REC-DISTINCT": ("rt_records_v1.parquet", "is_first_copy"),
    "V-LOC": ("rt_records_v1.parquet", "locus_key"),
    "V-LOC-PHYS": ("rt_records_v1.parquet", "physical_locus_key"),
    "V-RT": ("rt_records_v1.parquet", "rt_seq_hash"),
    "V-RT-TAXOCC": ("rt_records_v1.parquet", ("rt_seq_hash", "genome_id_norm")),
    "V-WIN": ("rt_records_v1.parquet", "window_dna_sha256"),
    "V-NCRNA-CALL": ("rt_ncrna_calls_v1.parquet", None),
    "V-PAIR-PLACEMENT": ("rt_ncrna_calls_v1.parquet", None),
}
ELIG = ["elig_exact_rt", "elig_rt_coords", "elig_geometry", "elig_rt_length",
        "elig_rt_completeness"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--view", required=True, choices=sorted(VIEWS))
    ap.add_argument("--elig", action="append", default=[], choices=ELIG)
    ap.add_argument("--family")
    ap.add_argument("--database")
    ap.add_argument("--taxonomy-system")
    ap.add_argument("--multi-only", action="store_true", help="the MULTI stratum alone")
    ap.add_argument("--exclude-multi", action="store_true")
    ap.add_argument("--with-ncrna", action="store_true")
    ap.add_argument("--record-key")
    ap.add_argument("--raw", action="store_true", help="print the original JSON record")
    ap.add_argument("--corpus", default="/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()

    fname, key = VIEWS[a.view]
    df = pd.read_parquet(Path(a.derived) / fname)
    steps = [("view " + a.view, len(df))]
    if a.view in ("V-REC-DISTINCT", "V-LOC", "V-LOC-PHYS", "V-RT", "V-RT-TAXOCC", "V-WIN"):
        df = df[df.is_first_copy]
        steps.append(("is_first_copy", len(df)))
    if a.record_key:
        df = df[df.record_key.eq(a.record_key)]
        steps.append(("record_key", len(df)))
    for flag in a.elig:
        df = df[df[flag]] if flag in df.columns else df
        steps.append((flag, len(df)))
    if a.family:
        df = df[df.file_label.eq(a.family)]
        steps.append((f"family={a.family}", len(df)))
    if a.database:
        df = df[df.source_database.eq(a.database)]
        steps.append((f"database={a.database}", len(df)))
    if a.taxonomy_system:
        df = df[df.taxonomy_system.eq(a.taxonomy_system)]
        steps.append((f"taxonomy_system={a.taxonomy_system}", len(df)))
    if a.multi_only:
        df = df[df.file_label.eq("MULTI")]
        steps.append(("MULTI stratum only", len(df)))
    if a.exclude_multi:
        df = df[~df.file_label.eq("MULTI")]
        steps.append(("MULTI excluded", len(df)))
    if a.with_ncrna and "n_ncrna" in df.columns:
        df = df[df.n_ncrna > 0]
        steps.append(("n_ncrna > 0", len(df)))
    if key is not None and key != "is_first_copy":
        cols = list(key) if isinstance(key, tuple) else [key]
        n_units = len(df.drop_duplicates(cols))
        steps.append((f"distinct {cols}", n_units))
    for name, n in steps:
        print(f"  {name:48s} {n:,d}", file=sys.stderr)
    if "source_database" in df.columns and len(df):
        comp = df.source_database.value_counts()
        print("  composition: " + ", ".join(f"{k}={v:,d}" for k, v in comp.items()), file=sys.stderr)

    if a.raw:
        for row in df.head(a.limit).itertuples():
            with (Path(a.corpus) / row.source_file).open("rb") as fh:
                fh.seek(row.byte_offset)
                print(json.dumps(json.loads(fh.read(row.byte_len).decode()), indent=1)[:4000])
        return 0
    if a.count:
        print(steps[-1][1])
        return 0
    if a.out:
        df.to_csv(a.out, sep="\t", index=False)
        print(f"wrote {a.out}: {len(df)} rows", file=sys.stderr)
    else:
        print(df.head(a.limit).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
