#!/usr/bin/env python3
"""e01 - the canonical extraction pass over the RT-anchored corpus (g1 population contract).

One strict JSON pass over the 42 RT-anchored files (the ncRNA-anchored master file is NOT
opened: it is outside the RT analytical population, docs/decisions/2026-09-15). Produces the
Stage-1 derived datasets:

  rt_records_v1.parquet     one row per RT-anchored raw record, with unit keys, RT
                            back-translation verdict, QC flags and eligibility flags
  rt_exact_v1.parquet/.faa  one row per exact RT amino-acid sequence (sha256 of the
                            normalised sequence), with its occurrence counts
  rt_loci_v1.parquet        one row per genomic locus (contig, RT interval, strand)
  rt_ncrna_calls_v1.parquet one row per ncRNA call inside an RT-anchored record
  rt_window_cds_v1.parquet  one row per CDS inside an RT-anchored record's window

Census (WA-D.2): all records, all files. Nothing is filtered; unusable records carry an
eligibility flag and a reason. `--limit-chunks` is a throwaway smoke slice, never reported.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g2lib as G  # noqa: E402

CHUNK_BYTES = 64 << 20          # DECLARED: newline-aligned byte chunk per task
ZSTD = "zstd"

S = pa.string(); I32 = pa.int32(); I64 = pa.int64(); B = pa.bool_(); F = pa.float64()

REC_SCHEMA = pa.schema([
    ("source_file", S), ("chunk", I32), ("local_line", I32), ("byte_offset", I64),
    ("byte_len", I32), ("record_sha256", S),
    ("rt_system_id", S), ("contig", S), ("contig_norm", S), ("genome_id", S),
    ("genome_id_norm", S), ("genome_asm_core", S), ("source_database", S),
    ("file_label", S), ("system_types_raw", S), ("type_set_norm", S), ("n_type_tokens", I32),
    ("multilabel", B), ("system_subtypes_raw", S), ("n_system_subtypes", I32),
    ("detected_by_raw", S),
    ("taxonomy_system", S), ("tax_domain", S), ("tax_phylum", S), ("tax_class", S),
    ("tax_order", S), ("tax_family", S), ("tax_genus", S), ("tax_species", S),
    ("tax_full_lineage", S), ("tax_environment", S),
    ("anchor_gene_id", S), ("anchor_start", I64), ("anchor_end", I64), ("anchor_strand", S),
    ("anchor_center", I64), ("anchor_eq_rt", B),
    ("win_start", I64), ("win_end", I64), ("win_len_field", I64), ("fullseq_len", I64),
    ("clipped_end_flag", B), ("clipped_start_flag_raw", B), ("extended_for_cds", B),
    ("window_dna_sha256", S), ("frame_disambiguating", B),
    ("window_inverted", B), ("window_len_consistent", B), ("true_start_clipped", B),
    ("contig_len_lower_bound", I64), ("dist_rt_to_contig_start", I64),
    ("dist_rt_to_contig_end", I64), ("rt_at_window_edge", B),
    ("rt_start", I64), ("rt_end", I64), ("rt_strand", S), ("rt_len_nt", I64),
    ("rt_aa_len", I32), ("rt_seq_hash", S), ("rt_seq_hash_raw", S), ("rt_seq_wellformed", B),
    ("rt_internal_stops", I32), ("rt_nonstd_residues", I32), ("rt_has_terminal_stop", B),
    ("rt_len_nt_eq_3aa", B), ("rt_interval_valid", B), ("rt_in_window", B),
    ("bt_status", S), ("bt_n_diff", I32), ("bt_first_codon", S), ("bt_last_codon", S),
    ("bt_internal_stops_dna", I32), ("orf_start_codon_ok", B), ("orf_stop_ok", B),
    ("n_cds", I32), ("n_cds_with_sequence", I32), ("n_rt_cds", I32),
    ("rtcds_gene_id", S), ("rtcds_start", I64), ("rtcds_end", I64), ("rtcds_strand", S),
    ("rtcds_partial", S), ("rtcds_start_type", S), ("rtcds_coords_eq_rt", B),
    ("rtcds_seq_eq_rt", B), ("seqcds_all_are_rt", B), ("no_rt_cds_class", S),
    ("n_cds_overlapping_rt", I32),
    ("n_intergenic", I32), ("n_igr_has_ncrna_true", I32), ("n_ncrna_ids_referenced", I32),
    ("n_ncrna_ids_missing_from_array", I32),
    ("n_ncrna", I32), ("meta_total_ncrnas", I64), ("meta_total_genes", I64),
    ("meta_total_igr", I64), ("ncrna_count_qc", S),
    ("locus_key", S), ("physical_locus_key", S),
    ("elig_exact_rt", B), ("elig_exact_rt_reason", S),
    ("elig_rt_coords", B), ("elig_rt_coords_reason", S),
    ("elig_geometry", B), ("elig_geometry_reason", S),
    ("elig_rt_length", B), ("elig_rt_length_reason", S),
    ("elig_rt_completeness", B), ("elig_rt_completeness_reason", S),
])

NC_SCHEMA = pa.schema([
    ("source_file", S), ("chunk", I32), ("local_line", I32), ("ncrna_idx", I32),
    ("ncrna_id", S), ("intergenic_region_id", S), ("nc_start", I64), ("nc_end", I64),
    ("nc_strand", S), ("nc_len_field", I64), ("evalue", F), ("score", F),
    ("detection_model", S), ("nc_source", S), ("selection_reason", S), ("location_type", S),
    ("position_relative_to_rt", I64), ("has_cds_overlap", B), ("n_overlapping_cds", I32),
    ("overlap_types", S), ("overlapping_cds_ids", S), ("upstream_gene_id", S),
    ("downstream_gene_id", S), ("genomic_upstream_gene_id", S),
    ("genomic_downstream_gene_id", S), ("orientation_corrected", B),
    ("nc_seq_len", I32), ("nc_seq_hash", S), ("has_structure_annotation", B),
    ("free_energy", S), ("gc_content", F),
])

CDS_SCHEMA = pa.schema([
    ("source_file", S), ("chunk", I32), ("local_line", I32), ("cds_idx", I32),
    ("gene_id", S), ("cds_start", I64), ("cds_end", I64), ("cds_strand", S),
    ("cds_len", I64), ("is_rt_gene", B), ("has_sequence", B), ("partial", S),
    ("start_type", S), ("rbs_motif", S), ("rbs_spacer", S), ("gc_cont", F),
])

SEQ_SCHEMA = pa.schema([("rt_seq_hash", S), ("rt_seq", S)])


def _s(v):
    return v if isinstance(v, str) else ("" if v is None else str(v))


def _i(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else None


def type_tokens(st) -> tuple[str, str, int, bool]:
    raw = json.dumps(st, separators=(",", ":"), ensure_ascii=False)
    if not isinstance(st, list):
        return raw, "", 0, False
    elems = [e if isinstance(e, str) else json.dumps(e) for e in st]
    toks = sorted({t for e in elems for t in e.split("/") if t})
    return raw, "/".join(toks), len(toks), (len(elems) > 1 or any("/" in e for e in elems))


def build_row(rec: dict, fname: str, ci: int, li: int, off: int, blen: int, sha: str) -> tuple[dict, list, list, str]:
    gc = rec.get("genomic_context") or {}
    aw = gc.get("actual_window") or {}
    fs = gc.get("full_sequence") or ""
    rt = rec.get("rt_gene") or {}
    cds = rec.get("cds_annotations") or []
    igr = rec.get("intergenic_regions") or []
    ncs = rec.get("ncrnas") or []
    md = rec.get("metadata") or {}
    tax = rec.get("taxonomy") or {}

    ws, we = _i(aw.get("start")), _i(aw.get("end"))
    rs, re_, strand = _i(rt.get("start")), _i(rt.get("end")), _s(rt.get("strand"))
    seq = rt.get("sequence") if isinstance(rt.get("sequence"), str) else ""
    nseq = G.rt_seq_norm(seq)
    ok, internal, nonstd = G.seq_wellformed(seq)
    interval_ok = bool(rs is not None and re_ is not None and rs <= re_ and strand in ("+", "-"))
    inverted = bool(ws is not None and we is not None and ws > we)
    win_len_ok = bool(ws is not None and we is not None and not inverted and len(fs) == we - ws + 1)
    in_win = bool(interval_ok and ws is not None and we is not None and ws <= rs and re_ <= we)
    partial_out = bool(interval_ok and ws is not None and we is not None and not in_win
                       and rs <= we and re_ >= ws)

    if not interval_ok:
        bt, ndiff, fc, lc, ist = "not_testable_bad_rt_interval", 0, "", "", 0
    elif inverted:
        bt, ndiff, fc, lc, ist = "not_testable_window_inverted", 0, "", "", 0
    elif not win_len_ok:
        bt, ndiff, fc, lc, ist = "not_testable_window_length_inconsistent", 0, "", "", 0
    elif not in_win:
        bt = ("not_testable_rt_partially_outside_window" if partial_out
              else "not_testable_rt_outside_window")
        ndiff, fc, lc, ist = 0, "", "", 0
    else:
        bt, ndiff, fc, lc, ist = G.classify_bt(seq, G.rt_dna(fs, ws, rs, re_, strand))

    rtc = [c for c in cds if isinstance(c, dict) and c.get("is_rt_gene") is True]
    withseq = [c for c in cds if isinstance(c, dict) and isinstance(c.get("sequence"), str)]
    ov = [c for c in cds if isinstance(c, dict) and interval_ok
          and _i(c.get("start")) is not None and _i(c.get("end")) is not None
          and c["start"] <= re_ and c["end"] >= rs]
    c0 = rtc[0] if rtc else {}
    pm = c0.get("prodigal_metadata") or {}
    if rtc:
        cls = "has_rt_cds"
    elif inverted:
        cls = "context_absent_window_inverted"
    elif partial_out:
        cls = "rt_partially_outside_window"
    elif not in_win:
        cls = "rt_outside_window"
    elif bt in G.BT_VERIFIED:
        cls = ("no_prodigal_call_bt_verified_overlapping_cds" if ov
               else "no_prodigal_call_bt_verified_no_overlapping_cds")
    elif bt == "mismatch":
        cls = "no_prodigal_call_bt_mismatch"
    else:
        cls = "no_prodigal_call_not_testable_other"

    ref_ids, have = set(), {_s(n.get("ncrna_id")) for n in ncs if isinstance(n, dict)}
    n_true = 0
    for r in igr:
        if not isinstance(r, dict):
            continue
        if r.get("has_ncrna") is True:
            n_true += 1
        for x in (r.get("ncrna_ids") or []):
            ref_ids.add(_s(x))
    mt = _i(md.get("total_ncrnas"))
    qc = ("agree" if mt == len(ncs) else
          ("metadata_gt_array" if isinstance(mt, int) and mt > len(ncs) else
           ("metadata_lt_array" if isinstance(mt, int) else "metadata_missing_or_non_integer")))
    ac = _i(rec.get("anchor_center"))
    lk, plk = G.locus_keys(_s(rec.get("contig")), rs if rs is not None else -1,
                           re_ if re_ is not None else -1, strand)
    gnorm, gcore = G.genome_keys(_s(rec.get("genome_id")))
    st_raw, st_norm, ntok, multi = type_tokens(rec.get("system_types"))
    subs = rec.get("system_subtypes")
    row = {
        "source_file": fname, "chunk": ci, "local_line": li, "byte_offset": off,
        "byte_len": blen, "record_sha256": sha,
        "rt_system_id": _s(rec.get("rt_system_id")), "contig": _s(rec.get("contig")),
        "contig_norm": G.contig_norm(_s(rec.get("contig"))), "genome_id": _s(rec.get("genome_id")),
        "genome_id_norm": gnorm, "genome_asm_core": gcore,
        "source_database": _s(rec.get("source_database")), "file_label": G.file_label(fname),
        "system_types_raw": st_raw, "type_set_norm": st_norm, "n_type_tokens": ntok,
        "multilabel": multi,
        "system_subtypes_raw": json.dumps(subs, separators=(",", ":"), ensure_ascii=False),
        "n_system_subtypes": len(subs) if isinstance(subs, list) else 0,
        "detected_by_raw": json.dumps(md.get("detected_by"), separators=(",", ":"), ensure_ascii=False),
        "taxonomy_system": _s(tax.get("taxonomy_system")), "tax_domain": _s(tax.get("domain")),
        "tax_phylum": _s(tax.get("phylum")), "tax_class": _s(tax.get("class")),
        "tax_order": _s(tax.get("order")), "tax_family": _s(tax.get("family")),
        "tax_genus": _s(tax.get("genus")), "tax_species": _s(tax.get("species")),
        "tax_full_lineage": _s(tax.get("full_lineage")), "tax_environment": _s(tax.get("environment")),
        "anchor_gene_id": _s(rec.get("anchor_gene_id")), "anchor_start": _i(rec.get("anchor_start")),
        "anchor_end": _i(rec.get("anchor_end")), "anchor_strand": _s(rec.get("anchor_strand")),
        "anchor_center": ac,
        "anchor_eq_rt": (_i(rec.get("anchor_start")), _i(rec.get("anchor_end")),
                         _s(rec.get("anchor_strand"))) == (rs, re_, strand),
        "win_start": ws, "win_end": we, "win_len_field": _i(gc.get("length")),
        "fullseq_len": len(fs), "clipped_end_flag": aw.get("clipped_at_contig_end") is True,
        "clipped_start_flag_raw": aw.get("clipped_at_contig_start") is True,
        "extended_for_cds": gc.get("extended_for_cds") is True,
        "window_dna_sha256": G.hashlib.sha256(fs.upper().encode()).hexdigest() if fs else "",
        # Where actual_window.start == 1 the absolute and window-relative coordinate frames
        # COINCIDE, so a passing back-translation there cannot distinguish them. Verification
        # rates are therefore also reported on this disambiguating stratum alone.
        "frame_disambiguating": bool(ws is not None and ws > 1),
        "window_inverted": inverted, "window_len_consistent": win_len_ok,
        "true_start_clipped": bool(ac is not None and ac - G.WINDOW_HALF < 1),
        "contig_len_lower_bound": we if (aw.get("clipped_at_contig_end") is True and not inverted) else None,
        "dist_rt_to_contig_start": (rs - 1) if (interval_ok and ws == 1) else None,
        "dist_rt_to_contig_end": (we - re_) if (interval_ok and not inverted
                                                and aw.get("clipped_at_contig_end") is True) else None,
        "rt_at_window_edge": bool(interval_ok and (rs == ws or re_ == we)),
        "rt_start": rs, "rt_end": re_, "rt_strand": strand, "rt_len_nt": _i(rt.get("length")),
        "rt_aa_len": len(nseq), "rt_seq_hash": G.rt_hash(seq),
        "rt_seq_hash_raw": G.hashlib.sha256((seq or "").upper().encode()).hexdigest(),
        "rt_seq_wellformed": ok,
        "rt_internal_stops": internal, "rt_nonstd_residues": nonstd,
        "rt_has_terminal_stop": (seq or "").upper().endswith("*"),
        "rt_len_nt_eq_3aa": (_i(rt.get("length")) == 3 * len(seq or "")),
        "rt_interval_valid": interval_ok, "rt_in_window": in_win,
        "bt_status": bt, "bt_n_diff": ndiff, "bt_first_codon": fc, "bt_last_codon": lc,
        "bt_internal_stops_dna": ist,
        "orf_start_codon_ok": (fc in G.START_CODONS) if fc else None,
        "orf_stop_ok": (lc in G.STOP_CODONS) if lc else None,
        "n_cds": len(cds), "n_cds_with_sequence": len(withseq), "n_rt_cds": len(rtc),
        "rtcds_gene_id": _s(c0.get("gene_id")), "rtcds_start": _i(c0.get("start")),
        "rtcds_end": _i(c0.get("end")), "rtcds_strand": _s(c0.get("strand")),
        "rtcds_partial": _s(pm.get("partial")), "rtcds_start_type": _s(pm.get("start_type")),
        "rtcds_coords_eq_rt": ((_i(c0.get("start")), _i(c0.get("end")), _s(c0.get("strand")))
                               == (rs, re_, strand)) if rtc else None,
        "rtcds_seq_eq_rt": (c0.get("sequence") == seq) if rtc else None,
        "seqcds_all_are_rt": all(c.get("is_rt_gene") is True for c in withseq) if withseq else None,
        "no_rt_cds_class": cls, "n_cds_overlapping_rt": len(ov),
        "n_intergenic": len(igr), "n_igr_has_ncrna_true": n_true,
        "n_ncrna_ids_referenced": len(ref_ids),
        "n_ncrna_ids_missing_from_array": len(ref_ids - have),
        "n_ncrna": len(ncs), "meta_total_ncrnas": mt, "meta_total_genes": _i(md.get("total_genes")),
        "meta_total_igr": _i(md.get("total_intergenic_regions")), "ncrna_count_qc": qc,
        "locus_key": lk, "physical_locus_key": plk,
    }
    row.update(G.eligibility(row))

    ncrows = []
    for j, n in enumerate(ncs):
        if not isinstance(n, dict):
            continue
        so = n.get("sequence_oriented") if isinstance(n.get("sequence_oriented"), str) else (
            n.get("sequence") if isinstance(n.get("sequence"), str) else "")
        sa = n.get("structure_annotation")
        ncrows.append({
            "source_file": fname, "chunk": ci, "local_line": li, "ncrna_idx": j,
            "ncrna_id": _s(n.get("ncrna_id")), "intergenic_region_id": _s(n.get("intergenic_region_id")),
            "nc_start": _i(n.get("start")), "nc_end": _i(n.get("end")), "nc_strand": _s(n.get("strand")),
            "nc_len_field": _i(n.get("length")),
            "evalue": n.get("evalue") if isinstance(n.get("evalue"), (int, float)) else None,
            "score": n.get("score") if isinstance(n.get("score"), (int, float)) else None,
            "detection_model": _s(n.get("detection_model")), "nc_source": _s(n.get("source")),
            "selection_reason": _s(n.get("selection_reason")), "location_type": _s(n.get("location_type")),
            "position_relative_to_rt": _i(n.get("position_relative_to_rt")),
            "has_cds_overlap": n.get("has_cds_overlap") is True,
            "n_overlapping_cds": _i(n.get("n_overlapping_cds")) or 0,
            "overlap_types": _s(n.get("overlap_types")), "overlapping_cds_ids": _s(n.get("overlapping_cds_ids")),
            "upstream_gene_id": _s(n.get("upstream_gene_id")), "downstream_gene_id": _s(n.get("downstream_gene_id")),
            "genomic_upstream_gene_id": _s(n.get("genomic_upstream_gene_id")),
            "genomic_downstream_gene_id": _s(n.get("genomic_downstream_gene_id")),
            "orientation_corrected": n.get("orientation_corrected") is True,
            "nc_seq_len": len(so), "nc_seq_hash": G.hashlib.sha256(so.upper().encode()).hexdigest() if so else "",
            "has_structure_annotation": isinstance(sa, dict),
            "free_energy": _s(n.get("free_energy")),
            "gc_content": n.get("gc_content") if isinstance(n.get("gc_content"), (int, float)) else None,
        })
    cdsrows = []
    for j, c in enumerate(cds):
        if not isinstance(c, dict):
            continue
        p = c.get("prodigal_metadata") or {}
        cdsrows.append({
            "source_file": fname, "chunk": ci, "local_line": li, "cds_idx": j,
            "gene_id": _s(c.get("gene_id")), "cds_start": _i(c.get("start")), "cds_end": _i(c.get("end")),
            "cds_strand": _s(c.get("strand")), "cds_len": _i(c.get("length")),
            "is_rt_gene": c.get("is_rt_gene") is True, "has_sequence": isinstance(c.get("sequence"), str),
            "partial": _s(p.get("partial")), "start_type": _s(p.get("start_type")),
            "rbs_motif": _s(p.get("rbs_motif")), "rbs_spacer": _s(p.get("rbs_spacer")),
            "gc_cont": p.get("gc_cont") if isinstance(p.get("gc_cont"), (int, float)) else None,
        })
    return row, ncrows, cdsrows, nseq


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


def write_shard(path: Path, schema: pa.Schema, rows: list[dict]) -> None:
    cols = {f.name: [r.get(f.name) for r in rows] for f in schema}
    pq.write_table(pa.table(cols, schema=schema), path, compression=ZSTD)


def work(task) -> dict:
    path_s, ci, start, end, cache = task
    t0 = time.time()
    path = Path(path_s)
    fname = path.name
    with path.open("rb") as fh:
        fh.seek(start)
        data = fh.read(end - start)
    lines = data.split(b"\n")
    if data.endswith(b"\n"):
        lines.pop()
    recs, ncs, cdss = [], [], []
    seqs: dict[str, str] = {}
    counts = Counter()
    off = start
    for i, line in enumerate(lines):
        sha = G.hashlib.sha256(line).hexdigest()
        rec = json.loads(line.decode("utf-8"))
        row, nc, cd, nseq = build_row(rec, fname, ci, i, off, len(line), sha)
        off += len(line) + 1
        recs.append(row)
        ncs.extend(nc)
        cdss.extend(cd)
        seqs.setdefault(row["rt_seq_hash"], nseq)
        counts[row["bt_status"]] += 1
    tag = f"{fname}_{ci:05d}"
    write_shard(Path(cache) / f"rec_{tag}.parquet", REC_SCHEMA, recs)
    write_shard(Path(cache) / f"nc_{tag}.parquet", NC_SCHEMA, ncs)
    write_shard(Path(cache) / f"cds_{tag}.parquet", CDS_SCHEMA, cdss)
    pq.write_table(pa.table({"rt_seq_hash": list(seqs), "rt_seq": list(seqs.values())},
                            schema=SEQ_SCHEMA), Path(cache) / f"seq_{tag}.parquet", compression=ZSTD)
    return {"file": fname, "chunk": ci, "n": len(lines), "tag": tag, "bytes": end - start,
            "counts": counts, "seconds": time.time() - t0}


def add_line_no(t: pa.Table, base: int) -> pa.Table:
    ln = pc.add(t["local_line"].cast(pa.int64()), base + 1)
    return t.drop_columns(["chunk", "local_line"]).add_column(1, "line_no", ln)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=40)
    ap.add_argument("--limit-chunks", type=int, default=0, help="throwaway smoke slice")
    a = ap.parse_args()
    out = Path(a.out)
    derived, cache = out / "derived", out / "cache" / "e01"
    derived.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    for old in cache.glob("*.parquet"):
        old.unlink()

    files = sorted(Path(a.corpus) / n for n in os.listdir(a.corpus)
                   if n.endswith(".jsonl") and n != G.NCRNA_FILE)
    tasks = [(str(f), ci, s, e, str(cache)) for f in files for ci, (s, e) in enumerate(chunks_of(f))]
    if a.limit_chunks:
        tasks = tasks[:a.limit_chunks]
    tb = sum(t[3] - t[2] for t in tasks)
    print(f"e01: {len(files)} RT-anchored files, {len(tasks)} chunks, {tb:,d} bytes", flush=True)

    t0 = time.time()
    res = []
    with mp.Pool(a.procs) as pool:
        for r in pool.imap_unordered(work, sorted(tasks, key=lambda t: -(t[3] - t[2])), chunksize=1):
            res.append(r)
    wall = time.time() - t0
    cpu = sum(r["seconds"] for r in res)
    n_rec = sum(r["n"] for r in res)
    print(f"e01 pass wall={wall:.1f}s worker_s={cpu:.1f} records={n_rec:,d} "
          f"MB/worker_s={tb / 1e6 / max(cpu, 1e-9):.1f}", flush=True)
    res.sort(key=lambda r: (r["file"], r["chunk"]))

    # The pass writes shards and a shard index; m02 builds the derived tables from them.
    # Splitting the two keeps the expensive streaming pass restartable and lets the merge
    # run in its own process (the first version did both in one process and died in the
    # merge, throwing away a finished pass).
    with (cache / "shard_index.tsv").open("w") as fh:
        fh.write("source_file\tchunk\tn_lines\tline_offset\ttag\n")
        cur, run = None, 0
        for r in res:
            if r["file"] != cur:
                cur, run = r["file"], 0
            fh.write(f"{r['file']}\t{r['chunk']}\t{r['n']}\t{run}\t{r['tag']}\n")
            run += r["n"]
    print(f"e01 shards={len(res)} records={n_rec:,d} index={cache / 'shard_index.tsv'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
