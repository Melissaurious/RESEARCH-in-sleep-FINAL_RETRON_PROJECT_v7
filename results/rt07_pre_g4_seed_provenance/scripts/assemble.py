#!/usr/bin/env python3
"""rt07_pre_g4_seed_provenance - assemble INPUTS.tsv and MANIFEST.tsv (BS-1, BS-2, BS-17).

Every landed table already carries its own `unit` and `denominator` columns, so the manifest
reads them off the tables instead of restating them by hand. A table whose rows do not name
a unit and a denominator cannot be manifested, which is the same rule BS-17 enforces one
level up.

INPUTS.tsv hashes the acquired alignment, the g1 tables this gate builds on, and the
bundle's own control layer - the declared parameters are an input, and editing them after
the fact must invalidate the bundle rather than pass unnoticed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preg4lib import read_tsv, sha256_file as sha256, write_tsv  # noqa: E402

SCRIPT_OF = {
    "preg4_seed_identity": "s01_seed_lineage.py",
    "preg4_sequence_lineage": "s01_seed_lineage.py",
    "preg4_leakage_audit": "s02_leakage_audit.py",
    "preg4_leakage_summary": "s02_leakage_audit.py",
    "preg4_identity_distribution": "s02_leakage_audit.py",
    "preg4_model_lineage": "s03_model_lineage.py",
    "preg4_cand_provenance": "s04_cand_provenance.py",
}
EXTRA = {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    B = args.bundle

    from preg4lib import POPULATIONS, V3
    inputs, seen = [], set()

    def add(p: Path, role: str) -> None:
        p = p.resolve()
        if p in seen or not p.is_file():
            return
        seen.add(p)
        inputs.append({"path": str(p), "sha256": sha256(p), "bytes": p.stat().st_size,
                       "mtime": dt.datetime.fromtimestamp(p.stat().st_mtime)
                       .strftime("%Y-%m-%d %H:%M:%S"), "role": role})

    add(V3 / "stage2b_assessor_redesign/step3_hmm/cache/all167.faa",
        "the old seed under audit")
    add(V3 / "stage2b_assessor_redesign/anchors/anchor_set_v1.faa", "the anchor set")
    add(V3 / "stage2b_assessor_redesign/anchors/anchor_set_v1_provenance.tsv",
        "the anchor provenance table")
    for pid, (path, kind, why) in POPULATIONS.items():
        add(path, f"population read ONLY to measure overlap: {pid}")

    write_tsv(args.out / "INPUTS.tsv", ["path", "sha256", "bytes", "mtime", "role"], inputs)

    man = []
    for stem, script in SCRIPT_OF.items():
        p = B / "tables" / f"{stem}.tsv"
        if not p.is_file():
            print(f"FAIL missing table {p}", file=sys.stderr)
            return 1
        rows = read_tsv(p)
        unit = rows[0].get("unit", "") if rows else ""
        den = rows[0].get("denominator", "") if rows else ""
        if not unit or not den:
            print(f"FAIL {stem}.tsv rows do not name a unit and a denominator",
                  file=sys.stderr)
            return 1
        man.append({"artifact": f"tables/{stem}.tsv", "script": f"scripts/{script}",
                    "command": f"see run.sh: {script}", "unit": unit, "denominator": den})
    for art, (script, unit, den) in EXTRA.items():
        man.append({"artifact": art, "script": f"scripts/{script}",
                    "command": f"see run.sh: {script}", "unit": unit, "denominator": den})

    write_tsv(args.out / "MANIFEST.tsv",
              ["artifact", "script", "command", "unit", "denominator"], man)
    print(f"INPUTS.tsv: {len(inputs)} inputs hashed; MANIFEST.tsv: {len(man)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
