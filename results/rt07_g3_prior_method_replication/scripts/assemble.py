#!/usr/bin/env python3
"""rt07_g3 - assemble INPUTS.tsv and MANIFEST.tsv (BS-1, BS-2, BS-17).

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
from rt07g3lib import read_tsv, sha256_file as sha256, write_tsv  # noqa: E402

SCRIPT_OF = {
    "g3_set_identity": "s02_contamination.py",
    "g3_set_overlap": "s02_contamination.py",
    "g3_anchor_composition": "s02_contamination.py",
    "g3_frame_identity": "s03_frame_correspondence.py",
    "g3_matchstate_to_ltra": "s03_frame_correspondence.py",
    "g3_prior_region_correspondence": "s03_frame_correspondence.py",
    "g3_prior_frame_correspondence": "s04_prior_frame_and_rt0.py",
    "g3_rt0_object_audit": "s04_prior_frame_and_rt0.py",
    "g3_prior_claim_verdicts": "s05_verdicts.py",
    "g3_controls": "s06_controls_and_summary.py",
    "g3_summary": "s06_controls_and_summary.py",
    "g3_handoff_to_g4": "s06_controls_and_summary.py",
    "g3_unresolved_carried_forward": "s06_controls_and_summary.py",
    "g3_resolved_values": "assemble_report.py",
}
EXTRA = {
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

    from rt07g3lib import G2, resolve, control as ctl
    add(G2 / "reference/g2_reference_set.faa",
        "the g2 curated reference set, the shared substrate for frame correspondence")
    for f in ("g2_ltra_mapping.tsv", "g2_reconstructed_blocks.tsv"):
        add(G2 / "tables" / f, "landed rt07_g2 regions this gate compares prior work against")
    for s_ in ctl("prior_sets.tsv"):
        add(resolve(s_["relative_path"]), "prior sequence set under audit")
    for f_ in ctl("prior_frames.tsv"):
        add(resolve(f_["relative_path"]), "prior frame (profile HMM) under audit")
    add(Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/"
             "tables/rt0_rt7_frame.tsv"), "the prior RT0-RT7 frame table under audit")
    add(Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/"
             "tables/a6_landmark_concordance.tsv"),
        "the prior audit table the landmark states were read from")
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
