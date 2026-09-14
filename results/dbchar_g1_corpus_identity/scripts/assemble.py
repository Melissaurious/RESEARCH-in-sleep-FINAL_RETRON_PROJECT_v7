#!/usr/bin/env python3
"""assemble - the rollup (g1_summary.tsv) and MANIFEST.tsv. Reads section tables; computes
no new measurement: every summary value is a lookup or a sum over one named table column."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g1lib as L  # noqa: E402

UNITS = {  # artifact -> (script, unit, denominator)
    "s01_file_identity.tsv": ("s01_file_identity.py", "files (bytes, newlines, sha256 per file)",
                              "n/a - identity table, one row per entry of the corpus root; no rate"),
    "s01_corpus_root.tsv": ("s01_file_identity.py", "files / bytes / newlines",
                            "n/a - totals over every entry of the registered corpus root; no rate"),
    "s01_schema_identity.tsv": ("s01_file_identity.py", "documents",
                                "n/a - identity of the schema document copies; no rate"),
    "s02_parse_census.tsv": ("s02_record_census.py", "lines", "all newline-delimited lines of that file"),
    "s02_anchor_by_file.tsv": ("s02_record_census.py", "lines", "all lines of that file, split by population and anchor_type"),
    "s02_populations.tsv": ("s02_record_census.py", "lines / records", "ALL row: every line of the 43 files; each population row is a part of it"),
    "s02_source_database.tsv": ("s02_record_census.py", "records", "population_total column: parsed records in that anchor population"),
    "s02_source_database_by_file.tsv": ("s02_record_census.py", "records", "parsed records of that file and anchor_type"),
    "s02_taxonomy_system.tsv": ("s02_record_census.py", "records", "parsed records of that population and source_database"),
    "s02_system_types_by_file.tsv": ("s02_record_census.py", "records", "parsed records of that file and population"),
    "s02_multilabel_by_file.tsv": ("s02_record_census.py", "records", "n_records column: parsed records of that file and population"),
    "s02_multilabel_sets.tsv": ("s02_record_census.py", "records", "multi-label parsed records of that population"),
    "s02_detected_by.tsv": ("s02_record_census.py", "records", "population_total column: parsed records in that anchor population"),
    "s02_system_subtypes_state.tsv": ("s02_record_census.py", "records", "population_total column: parsed records in that anchor population"),
    "s02_validation_by_population.tsv": ("s02_record_census.py", "records", "n_parsed_records_in_population column"),
    "s02_validation_by_file.tsv": ("s02_record_census.py", "records", "parsed records of that file and population (s02_anchor_by_file.tsv)"),
    "s02_metadata_count_mismatch_direction.tsv": ("s02_record_census.py", "records", "n_flagged_for_check column: records flagged by that check in that population"),
    "s02_schema_paths.tsv": ("s02_record_census.py", "records (n_records_with_path) and key occurrences",
                             "n_parsed_records_in_population column for records; occurrences have no denominator"),
    "s02_byte_identical_records.tsv": ("s02_record_census.py", "lines", "non-blank lines of the 43 files (s02_record_manifest_digest.tsv manifest_rows)"),
    "s02_record_manifest_digest.tsv": ("s02_record_census.py", "records", "n/a - identity digest of the per-record manifest; no rate"),
    "s04_positive_controls.tsv": ("s04_controls.py", "controls", "n/a - each row is one pass/fail control on the synthetic fixture"),
    "s05_second_counts.tsv": ("s05_reconcile.py", "lines / records", "named per row in scope; the two routes count the same population"),
    "s05_prior_reconciliation.tsv": ("s05_reconcile.py", "named per row in quantity", "named per row in scope"),
    "g1_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    T = out / "tables"
    root = {r["quantity"]: r["value"] for r in rd(T / "s01_corpus_root.tsv")}
    pops = {r["population"]: r["n_lines"] for r in rd(T / "s02_populations.tsv")}
    dig = {r["quantity"]: r["value"] for r in rd(T / "s02_record_manifest_digest.tsv")}
    parse = rd(T / "s02_parse_census.tsv")
    ml = rd(T / "s02_multilabel_by_file.tsv")
    dup = rd(T / "s02_byte_identical_records.tsv")
    val = rd(T / "s02_validation_by_population.tsv")
    sc = rd(T / "s05_second_counts.tsv")
    pr = rd(T / "s05_prior_reconciliation.tsv")
    ctl = rd(T / "s04_positive_controls.tsv")
    rows = [
        ["corpus_root", root["corpus_root"], "s01_corpus_root.tsv"],
        ["jsonl_files", root["n_regular_jsonl_files"], "s01_corpus_root.tsv"],
        ["non_jsonl_or_non_regular_entries", root["n_non_jsonl_or_non_regular_entries"], "s01_corpus_root.tsv"],
        ["jsonl_bytes", root["total_jsonl_bytes"], "s01_corpus_root.tsv"],
        ["lines_all_files", pops["ALL"], "s02_populations.tsv"],
        ["record_manifest_sha256", dig["record_manifest_sha256"], "s02_record_manifest_digest.tsv"],
    ]
    rows += [[f"population:{p}", pops[p], "s02_populations.tsv"] for p in
             ("POP-RT-FAM", "POP-RT-MULTI", "POP-NCRNA", "POP-OTHER", "POP-UNPARSED")]
    for c in L.PARSE_CLASSES[1:]:
        rows.append([f"parse_class:{c}", sum(int(r[c]) for r in parse), "s02_parse_census.tsv"])
    rows.append(["multilabel_records_in_single_family_files",
                 sum(int(r["n_multilabel"]) for r in ml if r["file_role"] == "family"), "s02_multilabel_by_file.tsv"])
    rows.append(["single_label_records_in_MULTI_file",
                 sum(int(r["n_single_label"]) for r in ml if r["file_role"] == "multi"), "s02_multilabel_by_file.tsv"])
    for scope in ("within_one_file", "across_files"):
        rows.append([f"byte_identical_lines_beyond_first:{scope}",
                     sum(int(r["n_lines_beyond_first"]) for r in dup if r["scope"] == scope),
                     "s02_byte_identical_records.tsv"])
    for p in ("POP-RT-FAM", "POP-RT-MULTI", "POP-NCRNA"):
        fired = [r["check_id"] for r in val if r["population"] == p and int(r["n_flagged"]) > 0]
        rows.append([f"checks_firing:{p}", "|".join(fired) if fired else "none", "s02_validation_by_population.tsv"])
    rows.append(["second_count_rows", len(sc), "s05_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for r in sc if r["agreement"] != "AGREE"), "s05_second_counts.tsv"])
    rows.append(["prior_reconciliation_rows", len(pr), "s05_prior_reconciliation.tsv"])
    rows.append(["prior_reconciliation_differences", sum(1 for r in pr if r["status"] != "AGREE"),
                 "s05_prior_reconciliation.tsv"])
    rows.append(["positive_controls", len(ctl), "s04_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for r in ctl if r["result"] != "PASS"), "s04_positive_controls.tsv"])
    L.write_tsv(T / "g1_summary.tsv", ["quantity", "value", "source_table"], rows)

    present = sorted(p.name for p in T.glob("*.tsv"))
    missing = [n for n in present if n not in UNITS]
    if missing:
        print(f"assemble: tables with no MANIFEST row: {missing}", file=sys.stderr)
        return 1
    L.write_tsv(out / "MANIFEST.tsv", ["artifact", "script", "command", "unit", "denominator"],
                [[f"tables/{n}", f"scripts/{UNITS[n][0]}", f"see run.sh: {UNITS[n][0]}", UNITS[n][1], UNITS[n][2]]
                 for n in present])
    print(f"assemble: {len(rows)} summary rows, {len(present)} tables in MANIFEST")
    return 0


if __name__ == "__main__":
    sys.exit(main())
