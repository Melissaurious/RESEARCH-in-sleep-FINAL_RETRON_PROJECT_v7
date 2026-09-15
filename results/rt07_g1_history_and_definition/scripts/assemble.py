#!/usr/bin/env python3
"""rt07_g1 step 8 - assemble INPUTS.tsv and MANIFEST.tsv (BS-1, BS-2, BS-17).

INPUTS.tsv hashes every file the gate READ: the five registered PDFs, the two acquired
alignment files, the register it verified them against, and the bundle's own control tables
- the curated evidence layer is an input like any other, and a change to it must invalidate
the bundle's hashes rather than pass unnoticed.

MANIFEST.tsv names, for every landed artifact, the script that produced it and the unit and
denominator it is counted in. An artifact whose unit or denominator is '-' or '?' fails
BS-17, which is the check that stops a number from being landed without a population.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g1lib import ACQUIRED, PROJ, REGISTER, control, register, sha256, write_tsv  # noqa: E402

# artifact -> (script, unit, denominator)
M: dict[str, tuple[str, str, str]] = {
    "tables/g1_token_census.tsv": (
        "scripts/s02_token_census.py", "(source, region_name) pair",
        "6 sources x 32 region names = 192 cells"),
    "tables/g1_census_route_agreement.tsv": (
        "scripts/s02_token_census.py", "(source, region_name) pair",
        "cells where the two extraction routes disagree"),
    "tables/g1_detector_positive_control.tsv": (
        "scripts/s02_token_census.py", "detector control",
        "9 controls declared before any zero was reported"),
    "tables/g1_evidence_quotes.tsv": (
        "scripts/s03_evidence_matrix.py", "quoted passage",
        "assignments declared in control/evidence_assignments.tsv"),
    "tables/g1_literature_evidence_matrix.tsv": (
        "scripts/s03_evidence_matrix.py", "(source, region_name) cell",
        "6 sources x 32 region names = 192 cells"),
    "tables/g1_terminology_genealogy.tsv": (
        "scripts/s03_evidence_matrix.py", "genealogy edge (region, naming source, antecedent)",
        "edges traceable in the held derivational set"),
    "tables/g1_operational_evidence_matrix.tsv": (
        "scripts/s03_evidence_matrix.py", "(source, region) operational capability",
        "region-source pairs with any evidence in this gate"),
    "tables/g1_region_verdicts.tsv": (
        "scripts/s03_evidence_matrix.py", "region name", "32 region names in scope"),
    "tables/g1_unresolved_definition_register.tsv": (
        "scripts/s03_evidence_matrix.py", "open definitional question",
        "questions this gate could not close"),
    "tables/g1_acquisition_source_resolution.tsv": (
        "scripts/s04_acquisition_register.py", "externally acquired file or attempt",
        "2 files approved for governed acquisition; 7 attempts made or declined"),
    "tables/g1_derived_registry.tsv": (
        "scripts/s04_acquisition_register.py", "acquired primary asset",
        "assets landed in the governed acquisition cache by this gate"),
    "tables/g1_align000044_record_summary.tsv": (
        "scripts/s04_acquisition_register.py", "alignment record field",
        "n/a - one primary alignment record; values read, not derived"),
    "tables/g1_second_counts.tsv": (
        "scripts/s05_second_count.sh", "literal namings of one region in one source",
        "9 spot-checks spanning every source and both spellings"),
    "tables/g1_summary.tsv": (
        "scripts/s06_summary.py", "declared quantity",
        "n/a - rollup; each row names its own source table"),
    "tables/g1_prior_reconciliation.tsv": (
        "scripts/s06_summary.py", "prior statement",
        "prior statements this gate could test against its own reading"),
    "tables/g1_resolved_values.tsv": (
        "scripts/assemble_report.py", "resolved report value",
        "every value rendered in REPORT.md and REPORT.html"),
    "REPORT.md": ("scripts/assemble_report.py", "report",
                  "n/a - narrative; every number resolves to a landed table"),
    "REPORT.html": ("scripts/assemble_report.py", "report",
                    "n/a - narrative; every number resolves to a landed table"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    B = args.bundle

    reg = register()
    inputs = []
    seen = set()

    def add(p: Path, role: str) -> None:
        # Absolute always: INPUTS.tsv must hash the same file whether the bundle was
        # invoked by a relative or an absolute path, or a rerun "differs" on spelling.
        p = p.resolve()
        if p in seen or not p.is_file():
            return
        seen.add(p)
        inputs.append({
            "path": str(p), "sha256": sha256(p), "bytes": p.stat().st_size,
            "mtime": dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "role": role})

    for r in control("sources.tsv"):
        a = reg.get(r["asset_id"])
        if a and a["project_path"] not in ("NOT_ACQUIRED", "NOT_COPIED_EXTERNAL"):
            add(PROJ / a["project_path"], "registered primary source")
    for a in control("acquired_assets.tsv"):
        add(ACQUIRED / a["file_name"], "governed acquisition, this gate")
    add(REGISTER, "reference register the inputs were verified against")
    for c in sorted((B / "control").glob("*.tsv")):
        add(c, "curated evidence layer, verified against the sources at build time")

    write_tsv(args.out / "INPUTS.tsv", ["path", "sha256", "bytes", "mtime", "role"], inputs)
    write_tsv(args.out / "MANIFEST.tsv", ["artifact", "script", "command", "unit",
                                          "denominator"],
              [{"artifact": k, "script": s, "command": f"see run.sh: {Path(s).name}",
                "unit": u, "denominator": d} for k, (s, u, d) in M.items()])
    print(f"INPUTS.tsv: {len(inputs)} inputs hashed; MANIFEST.tsv: {len(M)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
