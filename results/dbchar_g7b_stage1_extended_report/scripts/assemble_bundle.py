#!/usr/bin/env python3
"""assemble_bundle - copy the scratch run into results/dbchar_g7b_stage1_extended_report.

Writes INPUTS.tsv (every input hashed, BS-2) and MANIFEST.tsv (artifact | script | command |
unit | denominator, from the per-artifact metadata each producing script wrote). Scripts are
copied verbatim (BS-1). This is packaging, not analysis: it computes no scientific number.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / "work"
DEST = ROOT / "results" / "dbchar_g7b_stage1_extended_report"
DERIVED = ROOT / "data" / "derived"

SCRIPTS = ["common.py", "a01_units_families.py", "a02_geometry.py", "a03_tools_zero_call.py",
           "a04_pairs_candidates_multi.py", "a05_taxonomy_quality.py", "c01_reconcile.py",
           "c02_independent_cds_between.py", "c03_controls.py", "f01_corpus.py",
           "f02_geometry.py", "f03_tools_taxonomy.py", "findings.py", "assemble_report.py",
           "assemble_bundle.py"]

DERIVED_USED = ["rt_records_v1.parquet", "rt_loci_v1.parquet", "rt_physical_loci_v1.parquet",
                "rt_exact_v1.parquet", "rt_ncrna_pairs_v1.parquet",
                "rt_ncrna_exact_pairs_v1.parquet", "rt_ncrna_exact_pair_recurrence_v1.parquet",
                "rt_ncrna_nonretron_candidates_v1.parquet", "rt_family_baseline_v1.parquet",
                "ncrna_family_baseline_v1.parquet", "multi_hmm_evidence_v1.parquet",
                "rt_tool_calls_v1.parquet", "rt_cds_recovery_v1.parquet",
                "rt_window_cds_v1.parquet"]

LANDED_TABLES = {
    "dbchar_g2_canonical_units": ["g2_unit_ladder.tsv", "g2_duplicate_lines.tsv",
                                  "g2_ladder_by_source_database.tsv",
                                  "g2_ladder_by_family_label.tsv"],
    "dbchar_g2b_rt_cds_recovery": ["g2b_recovery_classes.tsv"],
    "dbchar_g3_pair_geometry": ["g3_populations.tsv", "g3_direction.tsv",
                                "g3_cds_between_explicit.tsv", "g3_same_strand.tsv",
                                "g3_zero_class_by_family.tsv", "g3_pair_view_sizes.tsv",
                                "g3_topology_degrees.tsv", "g3_topology_components.tsv",
                                "g3_nonretron_cm_placements.tsv",
                                "g3_downstream_mode_profile.tsv"],
    "dbchar_g4_family_baseline": ["g4_rt_length_by_family.tsv", "g4_ncrna_length_by_model.tsv",
                                 "g4_multi_hmm_profile.tsv", "g4_multi_hmm_positive_control.tsv",
                                 "g4_multi_hmm_margin_comparison.tsv"],
    "dbchar_g5_metadata_sampling": ["g5_join_coverage.tsv", "g5_quality_availability.tsv",
                                    "g5_overrepresentation_genus.tsv"],
    "dbchar_g6_tool_calls": ["g6_tool_matrix_retron.tsv"],
}

REFERENCE = [ROOT / ("MELISSA_DATA/supplementary_material/databases_metadata_files/metadata_files/"
                     "gtdb_bacteria_metadata.tsv.gz"),
             Path("/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm_meta.txt")]
PADLOC_SYS = Path("/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/sys")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    (DEST / "scripts").mkdir(parents=True, exist_ok=True)
    (DEST / "tables").mkdir(parents=True, exist_ok=True)
    (DEST / "figures").mkdir(parents=True, exist_ok=True)
    (DEST / "provenance").mkdir(parents=True, exist_ok=True)

    for s in SCRIPTS:
        shutil.copy2(HERE / s, DEST / "scripts" / s)
    for t in sorted((WORK / "tables").glob("*.tsv")):
        shutil.copy2(t, DEST / "tables" / t.name)
    for f in sorted((WORK / "figures").glob("*")):
        shutil.copy2(f, DEST / "figures" / f.name)
    for d in ("REPORT.html", "REPORT.md"):
        shutil.copy2(WORK / d, DEST / d)

    # ---- MANIFEST from the metadata each producing script wrote beside its artifact
    rows = []
    for mp in sorted((WORK / "meta").glob("*.json")):
        d = json.loads(mp.read_text())
        rows.append((d["artifact"], d["script"],
                     f"see run.sh: {Path(d['script']).name}", d["unit"], d["denominator"]))
    rows.append(("REPORT.html", "scripts/assemble_report.py", "see run.sh: assemble_report.py",
                 "n/a - assembled document",
                 "n/a - every value is resolved from a landed table of this bundle"))
    rows.append(("REPORT.md", "scripts/assemble_report.py", "see run.sh: assemble_report.py",
                 "n/a - assembled document",
                 "n/a - every value is resolved from a landed table of this bundle"))
    # FIGURE_AND_ANALYSIS_PLAN.md, README.md and PROVENANCE.md are hand-written documents with
    # no producing script, so they are not MANIFEST rows (BS-1 requires a named script to exist).
    with (DEST / "MANIFEST.tsv").open("w", encoding="utf-8") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for r in sorted(set(rows)):
            fh.write("\t".join(r) + "\n")

    # ---- INPUTS: every input hashed
    inputs: list[Path] = [DERIVED / n for n in DERIVED_USED]
    for bundle, tabs in LANDED_TABLES.items():
        inputs += [ROOT / "results" / bundle / "tables" / t for t in tabs]
    inputs += REFERENCE + sorted(PADLOC_SYS.glob("retron_*.yaml"))
    with (DEST / "INPUTS.tsv").open("w", encoding="utf-8") as fh:
        fh.write("path\tsha256\tbytes\tmtime\n")
        for p in inputs:
            if not p.exists():
                raise SystemExit(f"FATAL: declared input missing: {p}")
            st = p.stat()
            fh.write(f"{p}\t{sha(p)}\t{st.st_size}\t"
                     f"{__import__('datetime').datetime.fromtimestamp(st.st_mtime):%Y-%m-%d %H:%M:%S}\n")
            print(f"  hashed {p.name}", flush=True)

    # ---- environment, by content (BS-8)
    env = subprocess.run(["conda", "env", "export", "-p",
                          "/home/borg/miniconda3/envs/retron_tradicional"],
                         capture_output=True, text=True)
    if env.returncode != 0:
        env = subprocess.run(["/home/borg/miniconda3/bin/conda", "env", "export", "-p",
                              "/home/borg/miniconda3/envs/retron_tradicional"],
                             capture_output=True, text=True)
    (DEST / "env.lock").write_text(env.stdout)
    print(f"env.lock sha256: {sha(DEST / 'env.lock')}")
    print(f"assembled into {DEST}")


if __name__ == "__main__":
    main()
