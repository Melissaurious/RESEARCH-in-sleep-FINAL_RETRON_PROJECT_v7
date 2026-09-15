#!/usr/bin/env python3
"""rt07_g2 - assemble INPUTS.tsv and MANIFEST.tsv (BS-1, BS-2, BS-17).

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
from rt07g2lib import ACQUIRED, G1, read_tsv, sha256, write_tsv  # noqa: E402

SCRIPT_OF = {
    "g2_reference_sequence_set": "s01_reference_set.py",
    "g2_lineage_groups": "s01_reference_set.py",
    "g2_substrate_identity": "s01_reference_set.py",
    "g2_conserved_positions": "s02_reconstruct_blocks.py",
    "g2_parameter_sweep": "s02_reconstruct_blocks.py",
    "g2_reconstructed_blocks": "s02_reconstruct_blocks.py",
    "g2_block_uncertainty": "s02_reconstruct_blocks.py",
    "g2_landmark_recovery": "s03_landmarks_and_recovery.py",
    "g2_ltra_mapping": "s03_landmarks_and_recovery.py",
    "g2_per_group_conservation": "s03_landmarks_and_recovery.py",
    "g2_interblock_spacers": "s03_landmarks_and_recovery.py",
    "g2_nterminal_region": "s03_landmarks_and_recovery.py",
    "g2_positive_controls": "s04_controls.py",
    "g2_null_model": "s04_controls.py",
    "g2_null_by_gap": "s04_controls.py",
    "g2_null_spatial_statistics": "s04_controls.py",
    "g2_second_frame": "s05_second_frame.py",
    "g2_second_frame_blocks": "s05_second_frame.py",
    "g2_frame_correspondence": "s05_second_frame.py",
    "g2_summary": "s06_summary.py",
    "g2_kill_criterion": "s06_summary.py",
    "g2_unresolved_carried_forward": "s06_summary.py",
    "g2_resolved_values": "assemble_report.py",
}
EXTRA = {
    "reference/g2_reference_set.faa": (
        "s01_reference_set.py", "reference protein sequence",
        "the 66 proteins of ALIGN_000044, ungapped"),
    "reference/g2_second_frame_mafft.afa": (
        "s05_second_frame.py", "aligned reference protein sequence",
        "the same 66 proteins, independently re-aligned"),
    "REPORT.md": ("assemble_report.py", "report",
                  "n/a - narrative; every number resolves to a landed table"),
    "REPORT.html": ("assemble_report.py", "report",
                    "n/a - narrative; every number resolves to a landed table"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    B = args.bundle

    inputs, seen = [], set()

    def add(p: Path, role: str) -> None:
        p = p.resolve()
        if p in seen or not p.is_file():
            return
        seen.add(p)
        inputs.append({"path": str(p), "sha256": sha256(p), "bytes": p.stat().st_size,
                       "mtime": dt.datetime.fromtimestamp(p.stat().st_mtime)
                       .strftime("%Y-%m-%d %H:%M:%S"), "role": role})

    for f in ("ALIGN_000044.aln", "ALIGN_000044.dat"):
        add(ACQUIRED / f, "primary alignment, acquired and verified in rt07_g1")
    for f in ("g1_acquisition_source_resolution.tsv", "g1_align000044_record_summary.tsv",
              "g1_unresolved_definition_register.tsv", "g1_evidence_quotes.tsv"):
        add(G1 / "tables" / f, "landed rt07_g1 output this gate builds on")
    for c in sorted((B / "control").glob("*.tsv")):
        add(c, "declared parameters and statements, fixed before scoring")

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
