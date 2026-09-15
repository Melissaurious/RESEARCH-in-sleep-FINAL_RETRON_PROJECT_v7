#!/usr/bin/env python3
"""j01 - metadata/taxonomy/source-database coverage and overrepresentation.

Declared before any data is read:

  * every catalogue is joined on the key its own `source_database` names, and the join is
    reported per database, never pooled: `gtdb_*` on `accession`, `gem` on `genome_id`,
    `mgnify_*`/uhgg on `Genome`, `ncbi_*` on `#assembly_accession`. The corpus `genome_id`
    carries GTDB's `RS_`/`GB_` prefix, which g2 already normalised.
  * taxonomy is reported PER `taxonomy_system`. The corpus carries `gtdb`, `ncbi` and
    `unknown`, and they are different schemas: GTDB is a 7-rank lineage, the NCBI block has no
    phylum. Ranks are counted inside a system, never across.
  * GEM taxonomy: the schema records that the GTDB lineage sits in the column headed
    `ecosystem`. That is verified here against the column's contents, not assumed.
  * overrepresentation is reported at three units - raw records, loci and exact RTs - because
    correcting for redundancy is exactly what changes it (C8).

Missingness is a value: a genome that does not join is counted and named, never dropped.
"""
from __future__ import annotations

import argparse
import gzip
import sys
from pathlib import Path

import pandas as pd

CATALOGUE = {          # source_database -> (filename, key column, gzip?)
    "gtdb_bacteria": ("gtdb_bacteria_metadata.tsv.gz", "accession", True),
    "gtdb_archaea": ("gtdb_archaea_metadata.tsv.gz", "accession", True),
    "gem": ("gem_metadata.tsv", "genome_id", False),
    "mgnify_human_gut": ("mgnify_human_gut_metadata.tsv", "Genome", False),
    "mgnify_marine": ("mgnify_marine_metadata.tsv", "Genome", False),
    "mgnify_soil": ("mgnify_soil_metadata.tsv", "Genome", False),
    "ncbi_bacteria": ("ncbi_bacteria_assembly_summary.txt", "#assembly_accession", False),
    "ncbi_archaea": ("ncbi_archaea_assembly_summary.txt", "#assembly_accession", False),
}
QUALITY = {            # the concept -> the column that carries it, per catalogue family
    "completeness": {"gtdb": "checkm2_completeness", "gem": "completeness",
                     "mgnify": "Completeness"},
    "contamination": {"gtdb": "checkm2_contamination", "gem": "contamination",
                      "mgnify": "Contamination"},
    "n50": {"gtdb": "n50_contigs", "gem": "n50", "mgnify": "N50"},
}
GTDB_RANKS = ["d__", "p__", "c__", "o__", "f__", "g__", "s__"]


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def norm_key(s: str) -> str:
    """Both sides of the join are normalised the same way.

    GTDB writes its accessions WITH the `RS_`/`GB_` prefix, and the corpus `genome_id` carries
    it too; g2's `genome_id_norm` strips it. Stripping only one side made the GTDB join read
    0%, which is why both sides are normalised here by one function.
    """
    return s[3:] if s.startswith(("RS_", "GB_")) else s


def read_keys(meta: Path, fname: str, key: str, gz: bool) -> tuple[set, list[str], int]:
    """Keys from a catalogue. The NCBI assembly summaries carry a comment line BEFORE the
    header, so the header is the first line that actually contains the key column - taking
    line 1 blindly made both NCBI catalogues read as 'key column absent'."""
    op = gzip.open if gz else open
    with op(meta / fname, "rt", errors="replace") as fh:
        header = None
        for line in fh:
            t = line.rstrip("\n").split("\t")
            if key in t:
                header = t
                break
        if header is None:
            return set(), [], 0
        i = header.index(key)
        keys, n = set(), 0
        for line in fh:
            if line.startswith("#"):
                continue
            n += 1
            t = line.rstrip("\n").split("\t")
            if len(t) > i:
                keys.add(norm_key(t[i]))
        return keys, header, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    D, M, W = Path(a.derived), Path(a.meta), Path(a.work)
    T = W / "tables"
    T.mkdir(parents=True, exist_ok=True)

    r = pd.read_parquet(D / "rt_records_v1.parquet", columns=[
        "record_key", "is_first_copy", "source_database", "genome_id", "genome_id_norm",
        "genome_asm_core", "locus_key", "physical_locus_key", "rt_seq_hash", "file_label",
        "taxonomy_system", "tax_domain", "tax_phylum", "tax_class", "tax_order", "tax_family",
        "tax_genus", "tax_species", "tax_full_lineage", "tax_environment"])
    f = r[r.is_first_copy]

    # ---- 1 · catalogue shape, and whether the key column is even there ----------------
    cat_keys, rows = {}, []
    for db, (fname, key, gz) in CATALOGUE.items():
        keys, header, n = read_keys(M, fname, key, gz)
        cat_keys[db] = keys
        qual = {}
        fam = "gtdb" if db.startswith("gtdb") else ("gem" if db == "gem" else
                                                    "mgnify" if db.startswith("mgnify") else "ncbi")
        for concept, cols in QUALITY.items():
            col = cols.get(fam)
            qual[concept] = "present" if (col and col in header) else "ABSENT"
        rows.append([db, fname, key, key in header, n, len(keys), len(header),
                     qual["completeness"], qual["contamination"], qual["n50"]])
    w(T / "g5_catalogue_shape.tsv", pd.DataFrame(rows, columns=[
        "source_database", "file", "key_column", "key_column_present", "n_rows", "n_distinct_keys",
        "n_columns", "completeness_column", "contamination_column", "n50_column"]).assign(
        unit="catalogue rows", denominator="n/a - describes the catalogue file itself"))

    # ---- 2 · the join, per database, at three units ----------------------------------
    def joined(series, db):
        return series.isin(cat_keys.get(db, set()))
    f = f.copy()
    f["genome_joins"] = [g in cat_keys.get(db, set())
                         for g, db in zip(f.genome_id_norm, f.source_database)]
    rows = []
    for db, sub in f.groupby("source_database"):
        g = sub.drop_duplicates("genome_id_norm")
        rows.append([db, len(sub), int(sub.genome_joins.sum()),
                     round(100 * sub.genome_joins.mean(), 4),
                     sub.locus_key.nunique(),
                     sub.loc[sub.genome_joins, "locus_key"].nunique(),
                     sub.rt_seq_hash.nunique(),
                     sub.loc[sub.genome_joins, "rt_seq_hash"].nunique(),
                     len(g), int(g.genome_joins.sum()),
                     round(100 * g.genome_joins.mean(), 4)])
    w(T / "g5_join_coverage.tsv", pd.DataFrame(rows, columns=[
        "source_database", "n_records", "n_records_joined", "pct_records_joined",
        "n_loci", "n_loci_joined", "n_exact_rt", "n_exact_rt_joined",
        "n_genomes", "n_genomes_joined", "pct_genomes_joined"]).assign(
        unit="records / loci / exact RTs / genomes",
        denominator="distinct raw records of that source_database, and its distinct genomes"))
    nj = f[~f.genome_joins]
    w(T / "g5_unjoined_examples.tsv", nj.groupby("source_database").agg(
        n_records=("record_key", "size"), n_genomes=("genome_id_norm", "nunique"),
        example_genome_id=("genome_id", "first"),
        example_genome_id_norm=("genome_id_norm", "first")).reset_index().assign(
            unit="records / genomes", denominator="records of that database that do NOT join"))

    # ---- 2b · what a quality filter can actually speak for ----------------------------
    # A join that resolves a ROW is not a join that resolves a VALUE. Per database: of the
    # genomes that join, how many carry a usable completeness/contamination/N50 value?
    rows = []
    for db, (fname, key, gz) in CATALOGUE.items():
        fam = "gtdb" if db.startswith("gtdb") else ("gem" if db == "gem" else
                                                    "mgnify" if db.startswith("mgnify") else "ncbi")
        sub = f[f.source_database.eq(db)].drop_duplicates("genome_id_norm")
        for concept, cols in QUALITY.items():
            col = cols.get(fam)
            if not col:
                rows.append([db, concept, "no column in this catalogue", 0, len(sub), 0.0])
                continue
            op = gzip.open if gz else open
            vals = {}
            with op(M / fname, "rt", errors="replace") as fh:
                header = None
                for line in fh:
                    t = line.rstrip("\n").split("\t")
                    if key in t:
                        header = t
                        break
                if header is None or col not in header:
                    rows.append([db, concept, "no column in this catalogue", 0, len(sub), 0.0])
                    continue
                ik, ic = header.index(key), header.index(col)
                for line in fh:
                    if line.startswith("#"):
                        continue
                    t = line.rstrip("\n").split("\t")
                    if len(t) > max(ik, ic):
                        vals[norm_key(t[ik])] = t[ic]
            have = sum(1 for g in sub.genome_id_norm
                       if vals.get(g, "") not in ("", "NA", "None", "null", "-"))
            rows.append([db, concept, col, have, len(sub),
                         round(100 * have / len(sub), 4) if len(sub) else 0.0])
    w(T / "g5_quality_availability.tsv", pd.DataFrame(rows, columns=[
        "source_database", "concept", "column", "n_genomes_with_a_value", "n_genomes",
        "pct_genomes_with_a_value"]).assign(
        unit="genomes", denominator="distinct genomes of that source_database in the corpus"))

    # ---- 3 · taxonomy, per schema ----------------------------------------------------
    w(T / "g5_taxonomy_system_by_database.tsv", f.groupby(
        ["taxonomy_system", "source_database"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique")).reset_index()
      .assign(unit="records / loci / exact RTs",
              denominator="distinct raw records of that taxonomy system and database"))
    ranks = ["tax_domain", "tax_phylum", "tax_class", "tax_order", "tax_family", "tax_genus",
             "tax_species"]
    rows = []
    for ts, sub in f.groupby("taxonomy_system"):
        for c in ranks:
            present = sub[c].notna() & sub[c].ne("") & ~sub[c].astype(str).str.startswith("[")
            rows.append([ts, c.replace("tax_", ""), int(present.sum()), len(sub),
                         round(100 * present.mean(), 4),
                         int(sub[c].astype(str).str.startswith("[").sum())])
    w(T / "g5_rank_coverage_by_system.tsv", pd.DataFrame(rows, columns=[
        "taxonomy_system", "rank", "n_present", "n_records_in_system", "pct_present",
        "n_family_level_fallback_brackets"]).assign(
        unit="records", denominator="distinct raw records carrying that taxonomy_system",
        note="schemas are never pooled: the NCBI block has no phylum by construction"))
    # the GTDB lineage string: how many of the 7 rank slots are populated, per system
    def slots(s):
        if not isinstance(s, str) or not s:
            return -1
        return sum(1 for p in GTDB_RANKS if f";{p}" in f";{s}" and
                   s.split(p, 1)[1].split(";")[0].strip() not in ("", " "))
    samp = f.sample(n=min(200000, len(f)), random_state=20260915)
    samp = samp.assign(n_slots=[slots(x) for x in samp.tax_full_lineage])
    w(T / "g5_lineage_slots_by_system.tsv", samp.groupby(
        ["taxonomy_system", "n_slots"]).size().rename("n_records").reset_index().assign(
        n_sampled=len(samp), seed=20260915, unit="records",
        denominator="a seeded 200k sample of distinct raw records (estimate, not a census)"))

    # ---- 4 · the GEM `ecosystem` column: verify the documented mislabel ----------------
    gem_head = pd.read_csv(M / "gem_metadata.tsv", sep="\t", nrows=5000)
    eco = gem_head["ecosystem"].astype(str) if "ecosystem" in gem_head.columns else pd.Series(dtype=str)
    looks_lineage = eco.str.startswith("d__")
    w(T / "g5_gem_ecosystem_column.tsv", pd.DataFrame([
        ["column present", "ecosystem" in gem_head.columns, ""],
        ["rows inspected", len(gem_head), "the first 5,000 rows of gem_metadata.tsv"],
        ["values starting with d__ (a GTDB lineage)", int(looks_lineage.sum()),
         round(100 * looks_lineage.mean(), 3) if len(eco) else 0],
        ["example value", eco.iloc[0] if len(eco) else "", ""],
    ], columns=["measure", "value", "note"]).assign(
        unit="catalogue rows", denominator="the inspected rows of gem_metadata.tsv"))

    # ---- 5 · overrepresentation, at three units (C8) -----------------------------------
    for rank, col in (("species", "tax_species"), ("genus", "tax_genus")):
        sub = f[f[col].notna() & f[col].ne("")]
        agg = sub.groupby(["taxonomy_system", col]).agg(
            n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
            n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique")).reset_index()
        tot = agg.groupby("taxonomy_system")[["n_records", "n_loci", "n_exact_rt"]].transform("sum")
        agg["pct_of_records"] = (100 * agg.n_records / tot.n_records).round(4)
        agg["pct_of_loci"] = (100 * agg.n_loci / tot.n_loci).round(4)
        agg["pct_of_exact_rt"] = (100 * agg.n_exact_rt / tot.n_exact_rt).round(4)
        agg["records_per_exact_rt"] = (agg.n_records / agg.n_exact_rt).round(3)
        top = agg.sort_values("n_records", ascending=False).groupby("taxonomy_system").head(40)
        w(T / f"g5_overrepresentation_{rank}.tsv", top.assign(
            unit="records / loci / exact RTs",
            denominator="all records of that taxonomy system carrying that rank (top 40 by records)"))
    # the correction, as one number per system
    rows = []
    for ts, sub in f.groupby("taxonomy_system"):
        s = sub[sub.tax_species.notna() & sub.tax_species.ne("")]
        if not len(s):
            continue
        by_rec = s.tax_species.value_counts(normalize=True)
        by_rt = s.drop_duplicates(["tax_species", "rt_seq_hash"]).tax_species.value_counts(normalize=True)
        rows.append([ts, len(s), s.tax_species.nunique(),
                     round(100 * by_rec.iloc[0], 4), by_rec.index[0],
                     round(100 * by_rt.get(by_rec.index[0], 0), 4),
                     round(100 * by_rec.head(10).sum(), 4), round(100 * by_rt.head(10).sum(), 4)])
    w(T / "g5_redundancy_correction.tsv", pd.DataFrame(rows, columns=[
        "taxonomy_system", "n_records", "n_species", "top_species_pct_of_records",
        "top_species", "top_species_pct_of_exact_rt", "top10_pct_of_records",
        "top10_pct_of_exact_rt"]).assign(
        unit="records vs exact RTs", denominator="records of that taxonomy system with a species"))

    # ---- 6 · environment / database composition ---------------------------------------
    w(T / "g5_environment_by_database.tsv", f.groupby(
        ["source_database", "tax_environment"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique")).reset_index().assign(
        unit="records / loci / exact RTs", denominator="distinct raw records of that database"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
