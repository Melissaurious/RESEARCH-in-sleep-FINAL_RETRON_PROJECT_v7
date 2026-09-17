#!/usr/bin/env python3
"""g5 step C — verify every shard, then merge into the canonical g5 dataset.

    merge.py <out_dir> <shard_dir> <dataset_dir> <tables_dir>

Order is mandatory and fail-closed. Nothing is merged until everything verifies:

  1. every shard named in the shard index has a DONE sidecar, and that sidecar VERIFIES -
     input sha256, instrument digest, and the sha256 of all four outputs;
  2. exactly one instrument identifier and one verified bundle root across all shards;
  3. the run reconciles against the FROZEN CENSUS: every censused-eligible identifier appears
     exactly once across all shards' sequences.tsv and TOOL_FAILURE rows, and nothing else
     appears at all;
  4. only then is the canonical dataset written.

Stage-1 metadata is joined HERE, after mapping, against landed outputs. The mapper never saw
it: every shard ran with no `--metadata`, and the runner's only metadata destination is the
single `family_metadata` column, which is `NOT_SUPPLIED` throughout. Metadata is a downstream
stratification variable, never validation truth and never an input to inference.
"""
import collections
import gzip
import hashlib
import os
import sys

import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
G4B = f"{ROOT}/results/rt07_g4b_production_mapper"
sys.path.insert(0, f"{G4B}/code")
from rtmap import schema as S               # noqa: E402
from rtmap import version as V              # noqa: E402

PARTITION = f"{ROOT}/data/derived/rt07_g5a/g5a_eligibility_partition.tsv.gz"
EXACT = f"{ROOT}/data/derived/rt_exact_v1.parquet"
FAMBASE = f"{ROOT}/data/derived/rt_family_baseline_v1.parquet"
TOOLS = f"{ROOT}/data/derived/rt_tool_calls_v1.parquet"
RECORDS = f"{ROOT}/data/derived/rt_records_v1.parquet"

OUT, SHARDS, DATASET, TABLES = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

CANON_MV = "rtmap-1.0.0/53a1e738a19b3896"
INT_COLS = {"state_id", "anchor_index", "sequence_residue_index", "sequence_length",
            "n_states_total", "n_mapped", "n_ambiguous", "n_unsupported", "n_deleted",
            "cat_state", "cat_residue_index", "n_dyad_motifs_in_sequence",
            "n_insertion_runs", "total_inserted_residues", "max_insertion_run"}
FLOAT_COLS = {"posterior", "support", "mapped_fraction", "domain_bitscore",
              "domain_evalue", "cat_support"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def write_tsv(path, header, rows):
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    print(f"  wrote {os.path.basename(path)} ({len(rows)} rows)")


def read_done(path):
    rows, meta = {}, {}
    for ln in open(path):
        ln = ln.rstrip("\n")
        if ln.startswith("# ") and "=" in ln:
            k, v = ln[2:].split("=", 1)
            meta[k] = v
        elif ln.startswith("#") or not ln:
            continue
        else:
            h, name = ln.split("  ", 1)
            rows[name] = h
    return rows, meta


def read_tsv_rows(path):
    with open(path) as f:
        cols = f.readline().rstrip("\n").split("\t")
        for ln in f:
            if ln.strip():
                yield dict(zip(cols, ln.rstrip("\n").split("\t")))


def typed(df, cols):
    for c in cols:
        if c in INT_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
        elif c in FLOAT_COLS:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
        else:
            df[c] = df[c].astype("string")
    return df


def main():
    os.makedirs(DATASET, exist_ok=True)
    os.makedirs(TABLES, exist_ok=True)
    comps = V.check_instrument()
    mv = V.mapper_version(comps)
    if mv != CANON_MV:
        raise SystemExit(f"FAIL CLOSED: instrument is {mv}, not the canonical {CANON_MV}")

    # ---- 1. shard verification ------------------------------------------------------
    index = [ln.split("\t") for ln in
             open(f"{SHARDS}/shard_index.tsv").read().splitlines()[1:]]
    shard_names = [r[0] for r in index]
    expected_n = {r[0]: int(r[1]) for r in index}
    print(f"verifying {len(shard_names)} shards")

    problems, instruments, roots, statuses = [], set(), set(), set()
    for name in shard_names:
        done = f"{OUT}/{name}.DONE"
        if not os.path.isfile(done):
            problems.append(f"{name}: no DONE sidecar")
            continue
        rows, meta = read_done(done)
        want = {f"{name}.{k}.tsv" for k in
                ("states", "sequences", "failures", "provenance")}
        if set(rows) != want:
            problems.append(f"{name}: DONE lists {sorted(rows)}")
            continue
        if meta.get("instrument_sha256") != V.instrument_digest(comps):
            problems.append(f"{name}: instrument digest differs")
        if meta.get("input_sha256") != sha256_file(f"{SHARDS}/{name}.faa"):
            problems.append(f"{name}: input sha256 differs from the shard on disk")
        for fn, h in sorted(rows.items()):
            p = f"{OUT}/{fn}"
            if not os.path.isfile(p):
                problems.append(f"{name}: output missing {fn}")
            elif sha256_file(p) != h:
                problems.append(f"{name}: output changed since written: {fn}")
        prov = {r["key"]: r["value"]
                for r in read_tsv_rows(f"{OUT}/{name}.provenance.tsv")}
        instruments.add(prov.get("mapper_version"))
        roots.add(prov.get("bundle_root_sha256"))
        statuses.add(prov.get("bundle_root_status"))
    if problems:
        for p in problems[:20]:
            print(f"  FAIL {p}")
        raise SystemExit(f"FAIL CLOSED: {len(problems)} shard verification problem(s)")
    if instruments != {CANON_MV}:
        raise SystemExit(f"FAIL CLOSED: more than one instrument across shards: {instruments}")
    if len(roots) != 1 or statuses != {"VERIFIED"}:
        raise SystemExit(f"FAIL CLOSED: bundle roots {roots}, statuses {statuses}")
    print(f"  all {len(shard_names)} shards verified; instrument {instruments.pop()}; "
          f"root {list(roots)[0][:16]} VERIFIED on every shard")

    # ---- 2. reconcile against the frozen census -------------------------------------
    eligible = set()
    with gzip.open(PARTITION, "rt") as f:
        cols = f.readline().rstrip("\n").split("\t")
        i_h, i_e = cols.index("rt_seq_hash"), cols.index("eligible")
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if p[i_e] == "True":
                eligible.add(p[i_h])
    print(f"censused eligible population (frozen denominator): {len(eligible)}")

    seen = collections.Counter()
    n_seq_rows = n_fail_rows = 0
    for name in shard_names:
        k = 0
        for r in read_tsv_rows(f"{OUT}/{name}.sequences.tsv"):
            seen[r["sequence_id"]] += 1
            k += 1
        n_seq_rows += k
        for r in read_tsv_rows(f"{OUT}/{name}.failures.tsv"):
            n_fail_rows += 1
            if r["inspectability_status"] == "TOOL_FAILURE":
                seen[r["sequence_id"]] += 1
        if k + sum(1 for r in read_tsv_rows(f"{OUT}/{name}.failures.tsv")
                   if r["inspectability_status"] == "TOOL_FAILURE") != expected_n[name]:
            raise SystemExit(f"FAIL CLOSED: {name} does not reconcile against its shard index")
    dupes = [k for k, v in seen.items() if v > 1]
    missing = eligible - set(seen)
    extra = set(seen) - eligible
    if dupes or missing or extra:
        raise SystemExit(f"FAIL CLOSED: {len(dupes)} duplicated, {len(missing)} missing, "
                         f"{len(extra)} unexpected identifiers")
    print(f"  reconciled: {len(seen)} identifiers, each exactly once; "
          f"0 duplicates, 0 missing, 0 unexpected")

    # ---- 3. canonical dataset -------------------------------------------------------
    print("writing the canonical dataset")
    seq_writer = st_writer = None
    seq_frames, cat_rows = [], []
    n_state_rows = 0
    for i, name in enumerate(shard_names):
        sdf = typed(pd.DataFrame(list(read_tsv_rows(f"{OUT}/{name}.sequences.tsv"))),
                    S.SEQUENCES_COLUMNS)
        tdf = typed(pd.DataFrame(list(read_tsv_rows(f"{OUT}/{name}.states.tsv"))),
                    S.STATES_COLUMNS)
        n_state_rows += len(tdf)
        st_tbl = pa.Table.from_pandas(tdf, preserve_index=False)
        if st_writer is None:
            st_writer = pq.ParquetWriter(f"{DATASET}/g5_states.parquet", st_tbl.schema,
                                         compression="zstd", compression_level=9)
        st_writer.write_table(st_tbl)
        seq_tbl = pa.Table.from_pandas(sdf, preserve_index=False)
        if seq_writer is None:
            seq_writer = pq.ParquetWriter(f"{DATASET}/g5_sequences.parquet", seq_tbl.schema,
                                          compression="zstd", compression_level=9)
        seq_writer.write_table(seq_tbl)
        seq_frames.append(sdf[["rt_hash", "sequence_id", "sequence_length", "verdict",
                               "reason", "inspectability_status", "n_mapped", "n_ambiguous",
                               "n_unsupported", "n_deleted", "mapped_fraction",
                               "domain_bitscore", "cat_state", "cat_call_state",
                               "cat_residue_index", "cat_residue", "cat_motif_class",
                               "cat_support", "cat_motif_window",
                               "n_dyad_motifs_in_sequence"]])
        if (i + 1) % 128 == 0:
            print(f"  merged {i + 1}/{len(shard_names)} shards")
    st_writer.close()
    seq_writer.close()
    allseq = pd.concat(seq_frames, ignore_index=True).sort_values(
        "rt_hash", kind="mergesort").reset_index(drop=True)
    del seq_frames

    # catalytic table: one row per RT, its OWN denominator, never pooled with the 150 anchors
    cat = allseq[["rt_hash", "sequence_id", "cat_state", "cat_call_state",
                  "cat_residue_index", "cat_residue", "cat_motif_class", "cat_support",
                  "cat_motif_window", "n_dyad_motifs_in_sequence"]].copy()
    pq.write_table(pa.Table.from_pandas(cat, preserve_index=False),
                   f"{DATASET}/g5_catalytic.parquet", compression="zstd",
                   compression_level=9)

    # failures: production failures from the run, plus the censused ineligible population
    fail_rows = []
    for name in shard_names:
        for r in read_tsv_rows(f"{OUT}/{name}.failures.tsv"):
            fail_rows.append({**r, "origin": "g5_run"})
    fdf = pd.DataFrame(fail_rows) if fail_rows else pd.DataFrame(
        columns=list(S.FAILURES_COLUMNS) + ["origin"])
    inel = pd.read_csv(f"{ROOT}/data/derived/rt07_g5a/g5a_ineligible_records.tsv.gz",
                       sep="\t", dtype=str)
    inel["origin"] = "g5a_census_ineligible"
    pq.write_table(pa.Table.from_pandas(fdf.astype(str), preserve_index=False),
                   f"{DATASET}/g5_run_failures.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pandas(inel, preserve_index=False),
                   f"{DATASET}/g5_ineligible.parquet", compression="zstd",
                   compression_level=9)

    # ---- 4. metadata crosswalk, built AFTER mapping ---------------------------------
    print("building the metadata crosswalk (post-mapping join)")
    ex = pd.read_parquet(EXACT, columns=["rt_seq_hash", "rt_aa_len", "any_multilabel",
                                         "family_label_set", "wellformed",
                                         "n_source_databases", "n_records", "n_loci",
                                         "n_physical_loci", "n_genomes", "n_contigs"])
    fam = pd.read_parquet(FAMBASE, columns=["rt_seq_hash", "family_label",
                                            "completeness_class", "view", "n_species",
                                            "n_edge", "n_true_start_clipped",
                                            "n_clipped_end"])
    tl = pd.read_parquet(TOOLS, columns=["rt_seq_hash", "by_myRT", "by_PADLOC",
                                         "by_DefenseFinder", "n_tools"])
    tl = tl.groupby("rt_seq_hash", sort=True).agg(
        by_myRT=("by_myRT", "max"), by_PADLOC=("by_PADLOC", "max"),
        by_DefenseFinder=("by_DefenseFinder", "max"),
        max_n_tools=("n_tools", "max")).reset_index()
    rec = pd.read_parquet(RECORDS, columns=["rt_seq_hash", "source_database",
                                           "type_set_norm", "tax_domain", "tax_phylum",
                                           "tax_class", "tax_genus", "genome_id_norm",
                                           "rt_system_id"])

    def joined_per_hash(col, out):
        sub = (rec[["rt_seq_hash", col]].dropna().drop_duplicates()
               .sort_values(["rt_seq_hash", col], kind="mergesort"))
        s = sub.groupby("rt_seq_hash", sort=True)[col].agg(";".join).rename(out)
        n = sub.groupby("rt_seq_hash", sort=True)[col].size().rename(f"n_distinct_{out}")
        return pd.concat([s, n], axis=1).reset_index()

    cross = ex.merge(fam, on="rt_seq_hash", how="left").merge(tl, on="rt_seq_hash",
                                                              how="left")
    for col, out in (("source_database", "source_databases"),
                     ("type_set_norm", "system_types"),
                     ("tax_domain", "tax_domains"), ("tax_phylum", "tax_phyla"),
                     ("tax_class", "tax_classes"), ("tax_genus", "tax_genera"),
                     ("genome_id_norm", "genome_ids"), ("rt_system_id", "rt_system_ids")):
        cross = cross.merge(joined_per_hash(col, out), on="rt_seq_hash", how="left")
        print(f"  crosswalk: {col}")
    del rec
    cross["multi_status"] = cross.any_multilabel.map({True: "MULTI", False: "NON_MULTI"})
    cross["in_g5_eligible"] = cross.rt_seq_hash.isin(eligible)
    cross = cross.rename(columns={"rt_seq_hash": "rt_hash",
                                  "family_label_set": "raw_myrt_family_label_set",
                                  "family_label": "stage1_collapsed_family"})
    cross = cross.sort_values("rt_hash", kind="mergesort").reset_index(drop=True)
    pq.write_table(pa.Table.from_pandas(cross, preserve_index=False),
                   f"{DATASET}/g5_metadata_crosswalk.parquet", compression="zstd",
                   compression_level=9)

    # ---- 5. run manifest -------------------------------------------------------------
    man = []
    for name in shard_names:
        rows, meta = read_done(f"{OUT}/{name}.DONE")
        n_seq = sum(1 for _ in read_tsv_rows(f"{OUT}/{name}.sequences.tsv"))
        n_st = sum(1 for _ in read_tsv_rows(f"{OUT}/{name}.states.tsv"))
        n_fl = sum(1 for _ in read_tsv_rows(f"{OUT}/{name}.failures.tsv"))
        man.append([name, expected_n[name], n_seq, n_st, n_fl, meta.get("mapper_version"),
                    meta.get("input_sha256"),
                    rows[f"{name}.sequences.tsv"], rows[f"{name}.states.tsv"]])
    write_tsv(f"{TABLES}/g5_shard_manifest.tsv",
              ["shard", "n_input", "n_sequences", "n_state_rows", "n_failure_rows",
               "mapper_version", "input_sha256", "sequences_sha256", "states_sha256"], man)

    files = sorted(os.listdir(DATASET))
    write_tsv(f"{TABLES}/g5_dataset_manifest.tsv", ["file", "bytes", "sha256"],
              [[f, os.path.getsize(f"{DATASET}/{f}"), sha256_file(f"{DATASET}/{f}")]
               for f in files])

    print(f"\nmerged: {n_seq_rows} sequence rows, {n_state_rows} state rows, "
          f"{n_fail_rows} failure rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
