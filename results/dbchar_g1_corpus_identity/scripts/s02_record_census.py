#!/usr/bin/env python3
"""s02 - record census: one strict JSON pass over every line of every corpus .jsonl file.

Emits, stratified by declared anchor population (PLAN.md): parse classes, anchor types,
source-database and taxonomy-system composition, system_types spellings and the
multi-label population, detected_by vocabulary, subtype presence, every declared
validation check, and an observed-vs-documented key-path census.

Also writes a per-record manifest (file, line, byte offset, byte length, sha256 of the raw
line, identifiers) to the cache - regenerable, never landed - and lands its digest, which
pins the exact record set analysed.

Census (WA-D.2): all lines, all files. `--smoke` runs a seeded size-stratified chunk sample
for throughput only; its output directory is separate and never reported.
"""
from __future__ import annotations

import argparse
import hashlib
import multiprocessing as mp
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.compute  # noqa: F401  (pa.compute)
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g1lib as L  # noqa: E402

CHUNK_BYTES = 64 << 20        # DECLARED: newline-aligned byte chunk per task
SMOKE_SEED = 20260915         # DECLARED: smoke chunk sample seed (throughput only)
POPS = ("POP-RT-FAM", "POP-RT-MULTI", "POP-NCRNA", "POP-OTHER", "POP-UNPARSED")
POP_DEF = {
    "POP-RT-FAM": "parsed records with anchor_type RT in the single-RT-family files",
    "POP-RT-MULTI": "parsed records with anchor_type RT in master_MULTI_merged_oriented.jsonl",
    "POP-NCRNA": "parsed records with anchor_type ncRNA, any file",
    "POP-OTHER": "parsed records whose anchor_type is neither RT nor ncRNA, or RT in a file of another role",
    "POP-UNPARSED": "lines that are not a JSON object (blank, bad UTF-8, bad JSON, non-object)",
}
MANIFEST_SCHEMA = pa.schema([
    ("source_file", pa.string()), ("chunk", pa.int32()), ("local_line", pa.int32()),
    ("byte_offset", pa.int64()), ("byte_len", pa.int32()), ("record_sha256", pa.string()),
    ("parse_class", pa.string()), ("population", pa.string()), ("anchor_type", pa.string()),
    ("rt_system_id", pa.string()), ("contig", pa.string()), ("genome_id", pa.string()),
    ("source_database", pa.string()), ("system_types_raw", pa.string()),
    ("system_type_set", pa.string()), ("multilabel", pa.bool_()), ("n_validation_flags", pa.int16()),
    ("validation_flags", pa.string()),
])


def population(rec: dict | None, role: str) -> str:
    if rec is None:
        return "POP-UNPARSED"
    a = rec.get("anchor_type")
    if a == "RT" and role == "family":
        return "POP-RT-FAM"
    if a == "RT" and role == "multi":
        return "POP-RT-MULTI"
    if a == "ncRNA":
        return "POP-NCRNA"
    return "POP-OTHER"


def chunks_of(path: Path) -> list[tuple[int, int]]:
    size = path.stat().st_size
    bounds = [0]
    with path.open("rb") as fh:
        pos = CHUNK_BYTES
        while pos < size:
            fh.seek(pos)
            fh.readline()
            nxt = fh.tell()
            if nxt >= size:
                break
            if nxt > bounds[-1]:
                bounds.append(nxt)
            pos = nxt + CHUNK_BYTES
    bounds.append(size)
    return [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]


def s(v: object) -> str | None:
    return v if isinstance(v, str) else (None if v is None else str(v))


def work(task: tuple) -> dict:
    path_s, ci, start, end, cache_dir, doc_top_l = task
    t0 = time.time()
    path = Path(path_s)
    fname = path.name
    role, _ = L.file_role(fname)
    doc_top = set(doc_top_l)
    with path.open("rb") as fh:
        fh.seek(start)
        data = fh.read(end - start)
    lines = data.split(b"\n")
    if data.endswith(b"\n"):
        lines.pop()

    parse = Counter()
    comp = Counter()        # (pop, anchor_class, source_database, taxonomy_system)
    types = Counter()       # (pop, raw, set, ntok, multilabel)
    detby = Counter()       # (pop, detected_by combo)
    subt = Counter()        # (pop, state)
    checks = Counter()      # (pop, check)
    mdelta = Counter()      # (pop, check, direction) for V12-V14
    paths: dict[str, dict[str, list]] = {}
    cols = {f.name: [] for f in MANIFEST_SCHEMA}
    off = start
    for i, line in enumerate(lines):
        pc, rec = L.parse_line(line)
        parse[pc] += 1
        pop = population(rec, role)
        row = {"source_file": fname, "chunk": ci, "local_line": i, "byte_offset": off,
               "byte_len": len(line), "record_sha256": L.record_sha256(line), "parse_class": pc,
               "population": pop}
        off += len(line) + 1
        if rec is None:
            for c in MANIFEST_SCHEMA.names[len(row):]:
                row[c] = None
            row["multilabel"] = None
        else:
            ac = L.anchor_class(rec)
            tax = rec.get("taxonomy")
            ts = tax.get("taxonomy_system", "<absent>") if isinstance(tax, dict) else "<no taxonomy object>"
            db = rec.get("source_database")
            comp[(pop, ac, L.value_label(rec, "source_database"), s(ts) if ts is not None else "<null>")] += 1
            raw, tset, ntok, multi = L.type_tokens(rec.get("system_types"))
            types[(pop, raw, tset, ntok, multi)] += 1
            md = rec.get("metadata")
            dbv = md.get("detected_by") if isinstance(md, dict) else None
            detby[(pop, "|".join(sorted(map(str, dbv))) if isinstance(dbv, list) else f"<{L._tname(dbv)}>")] += 1
            sub = rec.get("system_subtypes")
            subt[(pop, "absent" if "system_subtypes" not in rec else
                  ("nonempty_list" if isinstance(sub, list) and sub else
                   ("empty_list" if isinstance(sub, list) else f"<{L._tname(sub)}>")))] += 1
            fired = L.validate(rec, fname, doc_top)
            for c in fired:
                checks[(pop, c)] += 1
            for c, fld, arr in (("V12", "total_ncrnas", "ncrnas"), ("V13", "total_genes", "cds_annotations"),
                                ("V14", "total_intergenic_regions", "intergenic_regions")):
                if c in fired:
                    tot = md.get(fld) if isinstance(md, dict) else None
                    ln = len(rec[arr]) if isinstance(rec.get(arr), list) else None
                    sign = ("metadata_gt_array" if tot > ln else "metadata_lt_array") \
                        if isinstance(tot, int) and isinstance(ln, int) else "non_integer_or_missing"
                    mdelta[(pop, c, sign)] += 1
            local: dict[str, list] = {}
            L.walk_paths(rec, "", local)
            acc = paths.setdefault(pop, {})
            for p, (occ, nnull, ty) in local.items():
                slot = acc.get(p)
                if slot is None:
                    slot = acc[p] = [0, 0, 0, Counter()]
                slot[0] += 1
                slot[1] += occ
                slot[2] += nnull
                slot[3].update(ty)
            row.update(anchor_type=s(rec.get("anchor_type")), rt_system_id=s(rec.get("rt_system_id")),
                       contig=s(rec.get("contig")), genome_id=s(rec.get("genome_id")),
                       source_database=s(db), system_types_raw=raw, system_type_set=tset,
                       multilabel=multi, n_validation_flags=len(fired), validation_flags="|".join(fired))
        for c, v in row.items():
            cols[c].append(v)
    shard = Path(cache_dir) / f"manifest_{fname}_{ci:05d}.parquet"
    pq.write_table(pa.table(cols, schema=MANIFEST_SCHEMA), shard, compression="zstd")
    return {"file": fname, "chunk": ci, "n_lines": len(lines), "bytes": end - start, "parse": parse,
            "comp": comp, "types": types, "detby": detby, "subt": subt, "checks": checks, "mdelta": mdelta,
            "paths": paths, "shard": str(shard), "seconds": time.time() - t0}


def merge_paths(into: dict, frm: dict) -> None:
    for pop, acc in frm.items():
        dst = into.setdefault(pop, {})
        for p, (r, o, n, ty) in acc.items():
            slot = dst.get(p)
            if slot is None:
                dst[p] = [r, o, n, Counter(ty)]
            else:
                slot[0] += r
                slot[1] += o
                slot[2] += n
                slot[3].update(ty)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=40)
    ap.add_argument("--smoke", type=int, default=0, help="chunks per size stratum; throughput only")
    a = ap.parse_args()
    out = Path(a.out)
    tdir, cdir = out / "tables", out / "cache" / "manifest_shards"
    tdir.mkdir(parents=True, exist_ok=True)
    cdir.mkdir(parents=True, exist_ok=True)
    for old in cdir.glob("manifest_*.parquet"):
        old.unlink()

    doc = L.documented_paths(Path(a.schema))
    doc_top = sorted(L.documented_top_level(doc))
    files = sorted(Path(a.corpus) / n for n in os.listdir(a.corpus) if n.endswith(".jsonl"))
    tasks = []
    for f in files:
        for ci, (st, en) in enumerate(chunks_of(f)):
            tasks.append((str(f), ci, st, en, str(cdir), doc_top))
    if a.smoke:
        rng = random.Random(SMOKE_SEED)
        by_size = sorted(files, key=lambda p: p.stat().st_size)
        k = len(by_size) // 3
        strata = [by_size[:k], by_size[k:2 * k], by_size[2 * k:]]
        pick = []
        for stratum in strata:
            names = {p.name for p in stratum}
            pool_ = [t for t in tasks if Path(t[0]).name in names]
            pick += rng.sample(pool_, min(a.smoke, len(pool_)))
        pick += rng.sample([t for t in tasks if Path(t[0]).name == L.NCRNA_FILE], 1)
        tasks = pick
    total_bytes = sum(t[3] - t[2] for t in tasks)
    print(f"s02: {len(files)} files, {len(tasks)} chunks, {total_bytes:,d} bytes, procs={a.procs}", flush=True)

    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for r in pool.imap_unordered(work, sorted(tasks, key=lambda t: -(t[3] - t[2])), chunksize=1):
            res.append(r)
    wall = time.time() - t0
    cpu = sum(r["seconds"] for r in res)
    print(f"s02 pass wall_seconds={wall:.1f} worker_seconds={cpu:.1f} "
          f"MB_per_worker_second={total_bytes / 1e6 / max(cpu, 1e-9):.1f} "
          f"records={sum(r['n_lines'] for r in res):,d}", flush=True)
    if a.smoke:
        print(f"SMOKE ONLY - projected full-pass worker_seconds for all corpus bytes: see s02 log", flush=True)
        return 0

    res.sort(key=lambda r: (r["file"], r["chunk"]))
    parse_f: dict[str, Counter] = {}
    nlines_f: Counter = Counter()
    comp_f = Counter()
    types_f = Counter()
    checks_f = Counter()
    comp = Counter(); types = Counter(); detby = Counter(); subt = Counter(); checks = Counter()
    mdelta = Counter()
    paths: dict = {}
    for r in res:
        parse_f.setdefault(r["file"], Counter()).update(r["parse"])
        nlines_f[r["file"]] += r["n_lines"]
        for k, v in r["comp"].items():
            comp[k] += v
            comp_f[(r["file"],) + k] += v
        for k, v in r["types"].items():
            types[k] += v
            types_f[(r["file"],) + k] += v
        detby.update(r["detby"])
        mdelta.update(r["mdelta"])
        subt.update(r["subt"])
        for k, v in r["checks"].items():
            checks[k] += v
            checks_f[(r["file"],) + k] += v
        merge_paths(paths, r["paths"])

    # ---- the record manifest: global line numbers, then its digest -------------------
    offsets, run_file, run = {}, None, 0
    for r in res:
        if r["file"] != run_file:
            run_file, run = r["file"], 0
        offsets[(r["file"], r["chunk"])] = run
        run += r["n_lines"]
    mtabs = []
    for r in res:
        t = pq.read_table(r["shard"])
        base = offsets[(r["file"], r["chunk"])]
        line_no = pa.compute.add(t["local_line"].cast(pa.int64()), base + 1)
        mtabs.append(t.drop_columns(["chunk", "local_line"]).add_column(1, "line_no", line_no))
    man = pa.concat_tables(mtabs)
    pq.write_table(man, out / "cache" / "record_manifest.parquet", compression="zstd")
    for r in res:
        os.unlink(r["shard"])
    h = hashlib.sha256()
    for sf, ln, bo, bl, rs in zip(*(man[c].to_pylist() for c in
                                    ("source_file", "line_no", "byte_offset", "byte_len", "record_sha256"))):
        h.update(f"{sf}\t{ln}\t{bo}\t{bl}\t{rs}\n".encode())
    digest = h.hexdigest()

    # ---- tables ----------------------------------------------------------------------
    roles = {f.name: L.file_role(f.name) for f in files}
    L.write_tsv(tdir / "s02_parse_census.tsv",
                ["source_file", "file_role", "file_label", "n_lines"] + list(L.PARSE_CLASSES),
                [[f, roles[f][0], roles[f][1], nlines_f[f]] + [parse_f[f].get(c, 0) for c in L.PARSE_CLASSES]
                 for f in sorted(parse_f)])

    anc = Counter()
    for (f, pop, ac, db, ts), v in comp_f.items():
        anc[(f, pop, ac)] += v
    for f in parse_f:
        bad = sum(v for c, v in parse_f[f].items() if c != "ok")
        if bad:
            anc[(f, "POP-UNPARSED", "<unparsed>")] += bad
    L.write_tsv(tdir / "s02_anchor_by_file.tsv", ["source_file", "file_role", "population", "anchor_type", "n_lines"],
                [[f, roles[f][0], pop, ac, v] for (f, pop, ac), v in sorted(anc.items())])

    pop_n = Counter()
    pop_files: dict[str, set] = {}
    for (f, pop, ac), v in anc.items():
        pop_n[pop] += v
        pop_files.setdefault(pop, set()).add(f)
    L.write_tsv(tdir / "s02_populations.tsv", ["population", "definition", "n_lines", "n_files"],
                [[p, POP_DEF[p], pop_n.get(p, 0), len(pop_files.get(p, ()))] for p in POPS] +
                [["ALL", "every newline-delimited line of every .jsonl file in the corpus root",
                  sum(nlines_f.values()), len(parse_f)]])

    dbc = Counter()
    for (pop, ac, db, ts), v in comp.items():
        dbc[(pop, db)] += v
    L.write_tsv(tdir / "s02_source_database.tsv", ["population", "source_database", "n_records", "population_total"],
                [[p, db, v, pop_n[p]] for (p, db), v in sorted(dbc.items())])
    fdb = Counter()
    for (f, pop, ac, db, ts), v in comp_f.items():
        fdb[(f, pop, ac, db)] += v
    L.write_tsv(tdir / "s02_source_database_by_file.tsv",
                ["source_file", "population", "anchor_type", "source_database", "n_records"],
                [[f, p, ac, db, v] for (f, p, ac, db), v in sorted(fdb.items())])
    L.write_tsv(tdir / "s02_taxonomy_system.tsv",
                ["population", "source_database", "taxonomy_system", "schema_documented_value", "n_records"],
                [[p, db, ts, ts in L.DOC_TAXONOMY_SYSTEMS, v] for (p, ac, db, ts), v in sorted(comp.items())])

    L.write_tsv(tdir / "s02_system_types_by_file.tsv",
                ["source_file", "population", "system_types_raw", "type_set_normalised", "n_tokens", "multilabel", "n_records"],
                [[f, p, raw, ts, nt, ml, v] for (f, p, raw, ts, nt, ml), v in sorted(types_f.items())])
    ml_file = Counter()
    for (f, p, raw, ts, nt, ml), v in types_f.items():
        ml_file[(f, p, ml)] += v
    L.write_tsv(tdir / "s02_multilabel_by_file.tsv",
                ["source_file", "file_role", "population", "n_records", "n_multilabel", "n_single_label"],
                [[f, roles[f][0], p, ml_file[(f, p, True)] + ml_file[(f, p, False)], ml_file[(f, p, True)],
                  ml_file[(f, p, False)]] for (f, p) in sorted({(f, p) for f, p, _ in ml_file})])
    sets: dict[str, list] = {}
    for (f, p, raw, ts, nt, ml), v in types_f.items():
        if not ml:
            continue
        e = sets.setdefault((p, ts), [nt, set(), 0, Counter()])
        e[1].add(raw)
        e[2] += v
        e[3][f] += v
    L.write_tsv(tdir / "s02_multilabel_sets.tsv",
                ["population", "type_set_normalised", "n_tokens", "n_raw_spellings", "n_records", "n_files", "files"],
                [[p, ts, e[0], len(e[1]), e[2], len(e[3]), "|".join(f"{k}:{c}" for k, c in sorted(e[3].items()))]
                 for (p, ts), e in sorted(sets.items(), key=lambda kv: (kv[0][0], -kv[1][2], kv[0][1]))])
    L.write_tsv(tdir / "s02_detected_by.tsv", ["population", "detected_by", "n_records", "population_total"],
                [[p, d, v, pop_n[p]] for (p, d), v in sorted(detby.items())])
    L.write_tsv(tdir / "s02_system_subtypes_state.tsv", ["population", "state", "n_records", "population_total"],
                [[p, st, v, pop_n[p]] for (p, st), v in sorted(subt.items())])

    L.write_tsv(tdir / "s02_validation_by_population.tsv",
                ["population", "check_id", "description", "n_flagged", "n_parsed_records_in_population"],
                [[p, c, L.CHECKS[c], checks.get((p, c), 0), pop_n.get(p, 0)]
                 for p in POPS[:4] for c in L.CHECKS])
    L.write_tsv(tdir / "s02_metadata_count_mismatch_direction.tsv",
                ["population", "check_id", "direction", "n_records", "n_flagged_for_check"],
                [[p, c, d, v, checks.get((p, c), 0)] for (p, c, d), v in sorted(mdelta.items())])
    L.write_tsv(tdir / "s02_validation_by_file.tsv",
                ["source_file", "population", "check_id", "n_flagged"],
                [[f, p, c, v] for (f, p, c), v in sorted(checks_f.items())])

    rows = []
    allp = sorted(set(doc) | {p for acc in paths.values() for p in acc})
    for p in allp:
        for pop in POPS[:4]:
            slot = paths.get(pop, {}).get(p)
            if slot is None and p not in doc:
                continue
            r, o, n, ty = slot if slot else (0, 0, 0, Counter())
            rows.append([pop, p, p in doc, r, pop_n.get(pop, 0), o, n,
                         "|".join(f"{k}:{c}" for k, c in sorted(ty.items()))])
    L.write_tsv(tdir / "s02_schema_paths.tsv",
                ["population", "path", "schema_documented", "n_records_with_path", "n_parsed_records_in_population",
                 "n_occurrences", "n_null_occurrences", "observed_types"], rows)

    df = man.select(["source_file", "record_sha256", "parse_class", "population"]).to_pandas()
    df = df[df.parse_class != "blank"]
    vc = df["record_sha256"].value_counts()
    n_distinct_hash = int(vc.shape[0])
    dd = df[df["record_sha256"].isin(vc.index[vc > 1])]
    dup = dd.groupby("record_sha256").agg(n=("source_file", "size"), nf=("source_file", "nunique"),
                                          pops=("population", lambda x: "|".join(sorted(set(x)))))
    L.write_tsv(tdir / "s02_byte_identical_records.tsv",
                ["scope", "populations", "n_distinct_line_hashes", "n_lines", "n_lines_beyond_first"],
                [["within_one_file", pops, int((sub.nf == 1).sum()), int(sub[sub.nf == 1].n.sum()),
                  int((sub[sub.nf == 1].n - 1).sum())] for pops, sub in sorted(dup.groupby("pops"))] +
                [["across_files", pops, int((sub.nf > 1).sum()), int(sub[sub.nf > 1].n.sum()),
                  int((sub[sub.nf > 1].n - 1).sum())] for pops, sub in sorted(dup.groupby("pops"))])
    L.write_tsv(tdir / "s02_record_manifest_digest.tsv", ["quantity", "value"], [
        ["manifest_rows", man.num_rows],
        ["manifest_serialisation", "sha256 over 'source_file\\tline_no\\tbyte_offset\\tbyte_len\\trecord_sha256\\n' in file,line order"],
        ["record_manifest_sha256", digest],
        ["n_distinct_line_sha256_excluding_blank", n_distinct_hash],
    ])
    print(f"s02 total wall_seconds (stdout only): {time.time() - t0:.1f}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
