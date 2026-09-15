#!/usr/bin/env python3
"""assemble - g5 rollup and MANIFEST. Computes nothing."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path

R, G, GEN = "records", "genomes", "genomes"
UNITS = {
 "g5_catalogue_shape.tsv": ("j01_join_and_sampling.py", "catalogue rows", "n/a - describes the catalogue file itself"),
 "g5_join_coverage.tsv": ("j01_join_and_sampling.py", "records / loci / exact RTs / genomes", "distinct raw records of that source_database, and its distinct genomes"),
 "g5_unjoined_examples.tsv": ("j01_join_and_sampling.py", "records / genomes", "records of that database that do NOT join"),
 "g5_quality_availability.tsv": ("j01_join_and_sampling.py", GEN, "distinct genomes of that source_database in the corpus"),
 "g5_taxonomy_system_by_database.tsv": ("j01_join_and_sampling.py", R, "distinct raw records of that taxonomy system and database"),
 "g5_rank_coverage_by_system.tsv": ("j01_join_and_sampling.py", R, "distinct raw records carrying that taxonomy_system"),
 "g5_lineage_slots_by_system.tsv": ("j01_join_and_sampling.py", R, "a seeded 200k sample of distinct raw records (estimate, not a census)"),
 "g5_gem_ecosystem_column.tsv": ("j01_join_and_sampling.py", "catalogue rows", "the inspected rows of gem_metadata.tsv"),
 "g5_overrepresentation_species.tsv": ("j01_join_and_sampling.py", "records / loci / exact RTs", "all records of that taxonomy system carrying that rank (top 40)"),
 "g5_overrepresentation_genus.tsv": ("j01_join_and_sampling.py", "records / loci / exact RTs", "all records of that taxonomy system carrying that rank (top 40)"),
 "g5_redundancy_correction.tsv": ("j01_join_and_sampling.py", "records vs exact RTs", "records of that taxonomy system with a species"),
 "g5_environment_by_database.tsv": ("j01_join_and_sampling.py", "records / loci / exact RTs", "distinct raw records of that database"),
 "g5_second_counts.tsv": ("c04_reconcile.py", "genomes / catalogue keys", "named per row; both routes count the same population"),
 "g5_prior_reconciliation.tsv": ("c04_reconcile.py", "named per row", "named per row"),
 "c02_positive_controls.tsv": ("c02_controls.py", "controls", "n/a - one pass/fail control per row"),
 "g5_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}

def rd(p):
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--work", required=True)
    W = Path(ap.parse_args().work); T = W / "tables"
    join = rd(T / "g5_join_coverage.tsv"); qual = rd(T / "g5_quality_availability.tsv")
    corr = rd(T / "g5_redundancy_correction.tsv"); sc = rd(T / "g5_second_counts.tsv")
    ctl = rd(T / "c02_positive_controls.tsv"); pr = rd(T / "g5_prior_reconciliation.tsv")
    rank = rd(T / "g5_rank_coverage_by_system.tsv")
    rows = []
    for x in join:
        rows.append([f"join_pct_genomes:{x['source_database']}", x["pct_genomes_joined"], "g5_join_coverage.tsv"])
    for x in qual:
        if x["concept"] == "completeness":
            rows.append([f"completeness_available_pct:{x['source_database']}", x["pct_genomes_with_a_value"], "g5_quality_availability.tsv"])
    for x in corr:
        rows.append([f"top_species_pct_of_records:{x['taxonomy_system']}", x["top_species_pct_of_records"], "g5_redundancy_correction.tsv"])
        rows.append([f"top_species_pct_of_exact_rt:{x['taxonomy_system']}", x["top_species_pct_of_exact_rt"], "g5_redundancy_correction.tsv"])
        rows.append([f"top10_pct_of_records:{x['taxonomy_system']}", x["top10_pct_of_records"], "g5_redundancy_correction.tsv"])
        rows.append([f"top10_pct_of_exact_rt:{x['taxonomy_system']}", x["top10_pct_of_exact_rt"], "g5_redundancy_correction.tsv"])
    for x in rank:
        if x["rank"] == "phylum":
            rows.append([f"phylum_present_pct:{x['taxonomy_system']}", x["pct_present"], "g5_rank_coverage_by_system.tsv"])
    rows.append(["second_count_rows", len(sc), "g5_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for x in sc if x["agreement"] != "AGREE"), "g5_second_counts.tsv"])
    rows.append(["prior_rows_CONFIRMED", sum(1 for x in pr if x["verdict"] == "CONFIRMED"), "g5_prior_reconciliation.tsv"])
    rows.append(["prior_rows_CHANGED", sum(1 for x in pr if x["verdict"] == "CHANGED"), "g5_prior_reconciliation.tsv"])
    rows.append(["positive_controls", len(ctl), "c02_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for x in ctl if x["result"] != "PASS"), "c02_positive_controls.tsv"])
    with (T / "g5_summary.tsv").open("w") as fh:
        fh.write("quantity\tvalue\tsource_table\n")
        for r in rows: fh.write("\t".join(str(x) for x in r) + "\n")
    present = sorted(x.name for x in T.glob("*.tsv"))
    missing = [n for n in present if n not in UNITS]
    if missing:
        print(f"assemble: tables with no MANIFEST row: {missing}", file=sys.stderr); return 1
    with (W / "MANIFEST.tsv").open("w") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for n in present:
            s, u, d = UNITS[n]
            fh.write(f"tables/{n}\tscripts/{s}\tsee run.sh: {s}\t{u}\t{d}\n")
    print(f"assemble: {len(rows)} summary rows, {len(present)} tables")
    return 0

if __name__ == "__main__":
    sys.exit(main())
