#!/usr/bin/env python3
"""m02 - build the derived tables from e01's shards.

Runs as its own process so the streaming pass stays restartable: the first version did the
pass and the merge together, died in the merge, and threw away a finished pass.

No per-group Python lambda touches a multi-million-group frame. Set-valued columns are built
the cheap way: take `first` and `nunique` vectorised, then materialise the joined set string
only for the few groups that actually hold more than one value.
"""
from __future__ import annotations

import argparse
import csv
import gc
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e01_extract as E  # noqa: E402  (schemas + the shard layout live there)

ZSTD = "zstd"


def shard_index(cache: Path) -> list[dict]:
    with (cache / "shard_index.tsv").open() as fh:
        return [{"source_file": r["source_file"], "chunk": int(r["chunk"]),
                 "n_lines": int(r["n_lines"]), "line_offset": int(r["line_offset"]),
                 "tag": r["tag"]} for r in csv.DictReader(fh, delimiter="\t")]


def add_line_no(t: pa.Table, base: int) -> pa.Table:
    ln = pc.add(t["local_line"].cast(pa.int64()), base + 1)
    return t.drop_columns(["chunk", "local_line"]).add_column(1, "line_no", ln)


def set_cols(df: pd.DataFrame, key: str, col: str) -> tuple[pd.Series, pd.Series]:
    """(joined distinct values, n distinct) per key - vectorised except on multi-valued groups."""
    g = df.groupby(key, sort=True)[col]
    nun = g.nunique()
    out = g.first().astype("string")
    multi = nun.index[nun > 1]
    if len(multi):
        sub = df[df[key].isin(multi)]
        j = (sub.drop_duplicates([key, col]).sort_values([key, col])
             .groupby(key)[col].agg("|".join))
        out.loc[j.index] = j
    return out, nun


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    cache, derived = W / "cache" / "e01", W / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    idx = shard_index(cache)

    # ---- 1 · records ------------------------------------------------------------------
    keep = ["source_file", "chunk", "local_line", "record_sha256"]
    small = pa.concat_tables([pq.read_table(cache / f"rec_{s['tag']}.parquet", columns=keep)
                              for s in idx]).to_pandas()
    off = {(s["source_file"], s["chunk"]): s["line_offset"] for s in idx}
    small["line_no"] = (small["local_line"] + 1 +
                        [off[(f, c)] for f, c in zip(small["source_file"], small["chunk"])])
    small["record_key"] = small["source_file"] + ":" + small["line_no"].astype(str)
    g = small.groupby("record_sha256", sort=False)["record_key"]
    dup = pd.DataFrame({"dup_line_group": g.transform("min"),
                        "n_copies_of_line": g.transform("size").astype("int32")})
    dup["record_key"] = small["record_key"]
    dup["is_first_copy"] = dup["record_key"].eq(dup["dup_line_group"])
    print(f"  records={len(small):,d} duplicate_extra_copies={int((~dup.is_first_copy).sum()):,d}",
          flush=True)
    del small, g
    gc.collect()

    w, pos = None, 0
    for s in idx:
        t = add_line_no(pq.read_table(cache / f"rec_{s['tag']}.parquet"), s["line_offset"])
        n = t.num_rows
        blk = dup.iloc[pos:pos + n]
        pos += n
        for c, ty in (("record_key", pa.string()), ("dup_line_group", pa.string()),
                      ("n_copies_of_line", pa.int32()), ("is_first_copy", pa.bool_())):
            t = t.append_column(c, pa.array(blk[c].to_list(), type=ty))
        if w is None:
            w = pq.ParquetWriter(derived / "rt_records_v1.parquet", t.schema, compression=ZSTD)
        w.write_table(t)
    w.close()
    del dup
    gc.collect()

    # ---- 2 · exact RT -----------------------------------------------------------------
    cols = ["rt_seq_hash", "is_first_copy", "locus_key", "physical_locus_key", "genome_id_norm",
            "source_database", "contig_norm", "source_file", "file_label", "type_set_norm",
            "multilabel", "elig_rt_coords", "rt_aa_len", "rt_seq_wellformed"]
    r = pd.read_parquet(derived / "rt_records_v1.parquet", columns=cols)
    f = r[r.is_first_copy].copy()
    del r
    gc.collect()
    gb = f.groupby("rt_seq_hash", sort=True)
    ex = pd.DataFrame({
        "rt_aa_len": gb.rt_aa_len.first(), "n_records": gb.size(),
        "n_loci": gb.locus_key.nunique(), "n_physical_loci": gb.physical_locus_key.nunique(),
        "n_genomes": gb.genome_id_norm.nunique(), "n_source_databases": gb.source_database.nunique(),
        "n_contigs": gb.contig_norm.nunique(), "n_files": gb.source_file.nunique(),
        "any_multilabel": gb.multilabel.any(), "n_verified_records": gb.elig_rt_coords.sum(),
        "wellformed": gb.rt_seq_wellformed.all()})
    ex["family_label_set"], _ = set_cols(f, "rt_seq_hash", "file_label")
    ex["type_set_norm_set"], _ = set_cols(f, "rt_seq_hash", "type_set_norm")
    ex = ex.reset_index()
    seq = pa.concat_tables([pq.read_table(cache / f"seq_{s['tag']}.parquet") for s in idx]) \
        .to_pandas().drop_duplicates("rt_seq_hash").set_index("rt_seq_hash")
    ex["rt_seq"] = ex["rt_seq_hash"].map(seq["rt_seq"])
    pq.write_table(pa.Table.from_pandas(ex, preserve_index=False),
                   derived / "rt_exact_v1.parquet", compression=ZSTD)
    with (derived / "rt_exact_v1.faa").open("w") as fh:
        for h, s in zip(ex["rt_seq_hash"], ex["rt_seq"]):
            fh.write(f">{h}\n")
            for k in range(0, len(s), 60):
                fh.write(s[k:k + 60] + "\n")
    print(f"  exact_rt={len(ex):,d}", flush=True)
    del ex, seq
    gc.collect()

    # ---- 3 · loci ---------------------------------------------------------------------
    lcols = ["locus_key", "physical_locus_key", "contig", "contig_norm", "rt_start", "rt_end",
             "rt_strand", "rt_system_id", "source_database", "genome_id_norm", "source_file",
             "rt_seq_hash", "file_label", "type_set_norm", "multilabel", "elig_geometry",
             "elig_rt_coords", "bt_status", "no_rt_cds_class", "record_key", "is_first_copy",
             "n_ncrna", "window_dna_sha256", "win_start", "win_end"]
    f = pd.read_parquet(derived / "rt_records_v1.parquet", columns=lcols)
    f = f[f.is_first_copy].copy()
    gb = f.groupby("locus_key", sort=True)
    lo = pd.DataFrame({
        "physical_locus_key": gb.physical_locus_key.first(), "contig": gb.contig.first(),
        "contig_norm": gb.contig_norm.first(), "rt_start": gb.rt_start.first(),
        "rt_end": gb.rt_end.first(), "rt_strand": gb.rt_strand.first(),
        "n_records": gb.size(), "n_rt_system_ids": gb.rt_system_id.nunique(),
        "n_source_databases": gb.source_database.nunique(), "n_genomes": gb.genome_id_norm.nunique(),
        "n_files": gb.source_file.nunique(), "n_rt_hashes": gb.rt_seq_hash.nunique(),
        "rt_seq_hash": gb.rt_seq_hash.first(), "any_multilabel": gb.multilabel.any(),
        "any_elig_geometry": gb.elig_geometry.any(), "all_elig_geometry": gb.elig_geometry.all(),
        "any_elig_rt_coords": gb.elig_rt_coords.any(),
        "representative_record_key": gb.record_key.min(),
        "n_ncrna_max": gb.n_ncrna.max(), "n_ncrna_min": gb.n_ncrna.min()})
    for col, name in (("file_label", "family_label_set"), ("type_set_norm", "type_set_norm_set"),
                      ("source_database", "source_database_set"), ("bt_status", "bt_status_set"),
                      ("no_rt_cds_class", "no_rt_cds_class_set")):
        lo[name], _ = set_cols(f, "locus_key", col)
    lo["rt_hash_conflict"] = lo["n_rt_hashes"] > 1
    spell = f.groupby("physical_locus_key", sort=False)["contig"].nunique()
    lo["physical_locus_n_contig_spellings"] = lo["physical_locus_key"].map(spell)
    lo["is_refseq_genbank_twin"] = lo["physical_locus_n_contig_spellings"] > 1
    lo = lo.reset_index()
    pq.write_table(pa.Table.from_pandas(lo, preserve_index=False),
                   derived / "rt_loci_v1.parquet", compression=ZSTD)
    print(f"  loci={len(lo):,d}", flush=True)
    del lo
    gc.collect()

    # ---- 4 · physical loci, with collapse EVIDENCE -------------------------------------
    gb = f.groupby("physical_locus_key", sort=True)
    ph = pd.DataFrame({
        "n_loci": gb.locus_key.nunique(), "n_records": gb.size(),
        "n_contig_spellings": gb.contig.nunique(),
        "n_rt_hashes": gb.rt_seq_hash.nunique(), "n_window_dna": gb.window_dna_sha256.nunique(),
        "n_empty_window_dna": f.assign(e=f.window_dna_sha256.eq("")).groupby(
            "physical_locus_key", sort=True).e.sum(),
        "n_win_start": gb.win_start.nunique(), "n_win_end": gb.win_end.nunique(),
        "n_strands": gb.rt_strand.nunique(), "n_source_databases": gb.source_database.nunique(),
        "n_genomes": gb.genome_id_norm.nunique(), "any_elig_geometry": gb.elig_geometry.any(),
        "representative_record_key": gb.record_key.min()})
    ph["contig_set"], _ = set_cols(f, "physical_locus_key", "contig")
    ph["family_label_set"], _ = set_cols(f, "physical_locus_key", "file_label")
    # A twin pair is ONE physical locus only where the evidence says so: identical window DNA,
    # RT protein, window coordinates and strand. An empty window sequence is never evidence.
    single = ph.n_contig_spellings <= 1
    empty = ph.n_empty_window_dna > 0
    ident = (ph.n_rt_hashes.eq(1) & ph.n_window_dna.eq(1) & ph.n_win_start.eq(1)
             & ph.n_win_end.eq(1) & ph.n_strands.eq(1))
    cls = pd.Series("twin_disagree", index=ph.index, dtype="object")
    cls[~single & ph.n_rt_hashes.eq(1) & ~empty] = "twin_identical_rt_only"
    cls[~single & ident & ~empty] = "twin_identical_window_dna_and_rt"
    cls[~single & empty] = "twin_not_evaluable_empty_window_dna"
    cls[single] = "single_contig_spelling"
    ph["twin_evidence_class"] = cls
    ph["collapse_supported"] = ph.twin_evidence_class.isin(
        ["single_contig_spelling", "twin_identical_window_dna_and_rt"])
    ph = ph.reset_index()
    pq.write_table(pa.Table.from_pandas(ph, preserve_index=False),
                   derived / "rt_physical_loci_v1.parquet", compression=ZSTD)
    print(f"  physical_loci={len(ph):,d}", flush=True)
    del ph, f, gb
    gc.collect()

    # ---- 5 · ncRNA calls and window CDS ------------------------------------------------
    for kind, name in (("nc", "rt_ncrna_calls_v1.parquet"), ("cds", "rt_window_cds_v1.parquet")):
        w, n = None, 0
        for s in idx:
            t = add_line_no(pq.read_table(cache / f"{kind}_{s['tag']}.parquet"), s["line_offset"])
            if w is None:
                w = pq.ParquetWriter(derived / name, t.schema, compression=ZSTD)
            w.write_table(t)
            n += t.num_rows
        if w:
            w.close()
        print(f"  {name}: {n:,d} rows", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
