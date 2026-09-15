#!/usr/bin/env python3
"""r01 - how the RT-anchored records with no marked RT CDS were (or were not) recovered.

g2 classified 31,504 records that carry an `rt_gene` but no `cds_annotations[]` entry flagged
`is_rt_gene`. This gate documents the recovery ROUTE and the evidence behind it, per record, in
a reusable table - not in prose.

Recovery route, stated plainly: the RT protein is present in every one of these records; what is
missing is the Prodigal ORF call. A record is "recovered" when the window DNA, translated in the
frame given by `rt_gene.start/end/strand`, reproduces that protein. The DNA and the protein are
DIFFERENT fields written by different steps of the mining pipeline, so their agreement is
evidence about the coordinates, not a restatement of them. This gate adds two further,
independent pieces of evidence:

  * the translation is re-done with Biopython (a different implementation, table 11) on a seeded
    sample, together with a frame-shifted negative control that must disagree;
  * the CDS that Prodigal DID call around the RT interval are examined - whether one shares a
    boundary with the RT, and whether it lies in the same reading frame.

For the records that cannot be recovered, the point is to separate a COORDINATE/WINDOW
REPRESENTATION problem (the RT interval lies outside the sequence the context extractor
retrieved, i.e. the two steps used different contigs) from a genuinely TRUNCATED biological
context (the contig really ends inside or beside the RT).

Nothing is deleted: every record keeps its per-record eligibility flags.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
from Bio.Seq import Seq

SEED = 20260915
SAMPLE_N = 2000
WINDOW_HALF = 10000
COLS = ["record_key", "source_file", "line_no", "byte_offset", "byte_len", "rt_system_id",
        "locus_key", "physical_locus_key", "contig", "genome_id_norm", "source_database",
        "file_label", "rt_start", "rt_end", "rt_strand", "rt_aa_len", "rt_seq_hash",
        "win_start", "win_end", "fullseq_len", "clipped_end_flag", "true_start_clipped",
        "extended_for_cds", "window_inverted", "window_len_consistent", "rt_in_window",
        "anchor_center", "bt_status", "bt_n_diff", "n_cds", "n_cds_overlapping_rt",
        "no_rt_cds_class", "is_first_copy", "elig_exact_rt", "elig_rt_coords", "elig_geometry",
        "elig_rt_length", "elig_rt_completeness", "elig_rt_coords_reason"]

RECOVERY = {  # class -> (recovered?, what the record can still support)
    "no_prodigal_call_bt_verified_overlapping_cds": ("RECOVERED", "sequence + coordinates"),
    "no_prodigal_call_bt_verified_no_overlapping_cds": ("RECOVERED", "sequence + coordinates"),
    "rt_outside_window": ("SEQUENCE_ONLY", "sequence"),
    "rt_partially_outside_window": ("SEQUENCE_ONLY", "sequence"),
    "context_absent_window_inverted": ("SEQUENCE_ONLY", "sequence"),
    "no_prodigal_call_bt_mismatch": ("ILL_POSED", "sequence, flagged unverified"),
}


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def verdict(got: str, prot: str, dna: str) -> str:
    """The declared equivalence, re-implemented here (nothing imported from g2lib).

    Biopython returns '*' at a stop codon; the corpus writes 'U' where an internal stop was
    masked and 'W' where TGA is read as tryptophan (translation table 4). Comparing without
    those classes would score a recoded record as a mismatch - which is exactly what the
    first version of this check did.
    """
    if got == prot:
        return "exact"
    if len(got) == len(prot) and ("M" + got[1:]) == prot and dna[:3].upper() in (
            "ATG", "GTG", "TTG", "ATT", "CTG"):
        return "alt_start"
    if len(got) != len(prot):
        return "mismatch"
    diffs = [i for i in range(len(got)) if got[i] != prot[i]]
    rest = [i for i in diffs if i != 0]
    start_ok = (0 not in diffs) or (prot[0] == "M")
    if rest and start_ok and all(
            got[i] == "*" and prot[i] in ("U", "W")
            and dna[3 * i:3 * i + 3].upper() in ("TAA", "TAG", "TGA") for i in rest):
        return "recoded_stop"
    return "mismatch"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    D, W = Path(a.derived), Path(a.work)
    T, DV = W / "tables", W / "derived"
    T.mkdir(parents=True, exist_ok=True)
    DV.mkdir(parents=True, exist_ok=True)

    r = pd.read_parquet(D / "rt_records_v1.parquet", columns=COLS)
    n_all = len(r)
    m = r[r.no_rt_cds_class != "has_rt_cds"].copy()
    print(f"  records without a marked RT CDS: {len(m):,d} of {n_all:,d}", flush=True)
    m["recovery_state"] = m.no_rt_cds_class.map(lambda c: RECOVERY[c][0])
    m["supports"] = m.no_rt_cds_class.map(lambda c: RECOVERY[c][1])

    # --- how far outside the retrieved window does the RT lie, and on which side? -----
    beyond_end = np.maximum(0, m.rt_end - m.win_end)
    before_start = np.maximum(0, m.win_start - m.rt_start)
    m["bp_beyond_window_end"] = np.where(m.window_inverted, np.nan, beyond_end)
    m["bp_before_window_start"] = np.where(m.window_inverted, np.nan, before_start)
    m["window_span"] = np.where(m.window_inverted, np.nan, m.win_end - m.win_start + 1)
    # A full window is 2*WINDOW_HALF+1 unless the contig ended first (or it was extended).
    m["window_is_short"] = m.window_span < (2 * WINDOW_HALF + 1)
    m["anchor_center_inside_window"] = (m.win_start <= m.anchor_center) & (m.anchor_center <= m.win_end)

    # Whether the RT interval touches the retrieved window at all is the direct test; an
    # earlier version used anchor_center, which a control showed reads "crosses" for an RT
    # lying wholly outside a window whose anchor happens to sit inside it.
    m["rt_intersects_window"] = (m.rt_start <= m.win_end) & (m.rt_end >= m.win_start) & ~m.window_inverted

    def represent(row) -> str:
        if row.window_inverted:
            return "window_inverted_no_sequence_retrieved"
        if row.rt_in_window:
            return "rt_inside_window"
        if row.bp_before_window_start > 0 and not row.rt_intersects_window:
            return "rt_before_window_start"
        if row.rt_intersects_window:
            return ("rt_crosses_a_contig_end_clipped_window" if row.clipped_end_flag
                    else "rt_crosses_a_window_edge_not_flagged_clipped")
        return ("rt_beyond_a_contig_end_clipped_window" if row.clipped_end_flag
                else "rt_beyond_window_end_not_flagged_clipped")
    m["representation_class"] = [represent(x) for x in m.itertuples()]

    # --- what DID Prodigal call around the RT interval? --------------------------------
    keys = pa.array(m.record_key.unique())
    cds = pq.read_table(D / "rt_window_cds_v1.parquet",
                        columns=["source_file", "line_no", "cds_start", "cds_end", "cds_strand",
                                 "is_rt_gene", "partial", "start_type"])
    ck = pc.binary_join_element_wise(cds["source_file"].cast(pa.string()),
                                     pc.cast(cds["line_no"], pa.string()), ":")
    cds = cds.append_column("record_key", ck)
    cds = cds.filter(pc.is_in(cds["record_key"], value_set=keys)).to_pandas()
    j = m[["record_key", "rt_start", "rt_end", "rt_strand"]].merge(cds, on="record_key", how="left")
    ov = (j.cds_start <= j.rt_end) & (j.cds_end >= j.rt_start)
    j = j[ov].copy()
    j["shares_start"] = j.cds_start == j.rt_start
    j["shares_end"] = j.cds_end == j.rt_end
    j["same_strand"] = j.cds_strand == j.rt_strand
    j["same_frame"] = ((j.cds_start - j.rt_start) % 3 == 0) & j.same_strand
    agg = j.groupby("record_key").agg(
        n_overlapping=("cds_start", "size"), any_shares_start=("shares_start", "any"),
        any_shares_end=("shares_end", "any"), any_same_frame=("same_frame", "any"),
        any_same_strand=("same_strand", "any"),
        overlapping_partial_states=("partial", lambda s: "|".join(sorted(set(s.astype(str)))))).reset_index()
    m = m.merge(agg, on="record_key", how="left")
    for c in ("any_shares_start", "any_shares_end", "any_same_frame", "any_same_strand"):
        m[c] = m[c].fillna(False)
    m["n_overlapping"] = m.n_overlapping.fillna(0).astype("int32")
    m["overlapping_partial_states"] = m.overlapping_partial_states.fillna("")
    m.to_parquet(DV / "rt_cds_recovery_v1.parquet", index=False, compression="zstd")
    print(f"  rt_cds_recovery_v1: {len(m):,d} rows", flush=True)

    # --- summary tables ----------------------------------------------------------------
    w(T / "g2b_recovery_classes.tsv", m.groupby(
        ["recovery_state", "no_rt_cds_class", "supports"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_first_copy=("is_first_copy", "sum"),
        n_elig_exact_rt=("elig_exact_rt", "sum"), n_elig_rt_coords=("elig_rt_coords", "sum"),
        n_elig_geometry=("elig_geometry", "sum"),
        n_elig_completeness=("elig_rt_completeness", "sum")).reset_index().assign(
            n_records_without_rt_cds=len(m), n_rt_anchored_records=n_all,
            unit="records", denominator="RT-anchored records with no marked RT CDS"))
    rec = m[m.recovery_state == "RECOVERED"]
    w(T / "g2b_recovered_evidence.tsv", rec.groupby(
        ["bt_status", "any_shares_start", "any_shares_end", "any_same_frame", "any_same_strand"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        median_overlapping_cds=("n_overlapping", "median")).reset_index().assign(
            n_recovered=len(rec), unit="records", denominator="RECOVERED records"))
    w(T / "g2b_recovered_overlap_partial_states.tsv",
      rec.groupby("overlapping_partial_states").agg(
          n_records=("record_key", "size")).reset_index().assign(
              n_recovered=len(rec), unit="records", denominator="RECOVERED records"))
    so = m[m.recovery_state == "SEQUENCE_ONLY"]
    w(T / "g2b_representation_classes.tsv", so.groupby(
        ["representation_class", "clipped_end_flag", "window_is_short"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        median_bp_beyond_window_end=("bp_beyond_window_end", "median"),
        max_bp_beyond_window_end=("bp_beyond_window_end", "max"),
        median_window_span=("window_span", "median"),
        n_anchor_center_inside=("anchor_center_inside_window", "sum")).reset_index().assign(
            n_sequence_only=len(so), unit="records",
            denominator="records that keep a sequence but no defensible context"))
    w(T / "g2b_sequence_only_by_database.tsv", so.groupby(
        ["source_database", "representation_class"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        median_bp_beyond_window_end=("bp_beyond_window_end", "median")).reset_index().assign(
            unit="records", denominator="SEQUENCE_ONLY records of that database"))
    w(T / "g2b_by_family.tsv", m.groupby(["file_label", "recovery_state"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique")).reset_index().assign(
            unit="records", denominator="records without a marked RT CDS in that family file"))

    # --- an INDEPENDENT translation of the recovery evidence ---------------------------
    # Different implementation (Biopython), different code path, plus a frame-shifted negative
    # control on the same records that MUST disagree - otherwise the check proves nothing.
    rng = random.Random(SEED)
    pool = rec.sample(n=min(SAMPLE_N, len(rec)), random_state=SEED)
    ctrl = r[(r.no_rt_cds_class == "has_rt_cds") & r.elig_rt_coords].sample(
        n=min(SAMPLE_N, int((r.no_rt_cds_class == "has_rt_cds").sum())), random_state=SEED)
    rows = []
    for tag, sub in (("RECOVERED", pool), ("CONTROL_has_rt_cds", ctrl)):
        if not len(sub):        # a fixture may contain no record of that population
            rows.append([tag, 0, 0, "n/a - empty population", 0, 0, 0, 0, 0,
                         "biopython table 11 + the declared equivalence re-implemented here"])
            continue
        agree = shifted_agree = 0
        kinds = {"exact": 0, "alt_start": 0, "recoded_stop": 0, "mismatch": 0}
        for x in sub.itertuples():
            with (Path(a.corpus) / x.source_file).open("rb") as fh:
                fh.seek(x.byte_offset)
                rec_json = json.loads(fh.read(x.byte_len).decode())
            gc = rec_json["genomic_context"]
            fs, ws = gc["full_sequence"], gc["actual_window"]["start"]
            prot = rec_json["rt_gene"]["sequence"]
            nt = Seq(fs[x.rt_start - ws:x.rt_end - ws + 1])
            if x.rt_strand == "-":
                nt = nt.reverse_complement()
            got = str(nt.translate(table=11))
            v = verdict(got, prot, str(nt))
            kinds[v] += 1
            agree += int(v != "mismatch")
            nt2 = Seq(fs[x.rt_start - ws + 1:x.rt_end - ws + 2])
            if x.rt_strand == "-":
                nt2 = nt2.reverse_complement()
            shifted_agree += int(verdict(str(nt2.translate(table=11)), prot, str(nt2)) != "mismatch")
        rows.append([tag, len(sub), agree, round(100 * agree / len(sub), 4), kinds["exact"],
                     kinds["alt_start"], kinds["recoded_stop"], kinds["mismatch"], shifted_agree,
                     "biopython table 11 + the declared equivalence re-implemented here"])
    w(T / "g2b_independent_translation_check.tsv", pd.DataFrame(rows, columns=[
        "population", "n_sampled", "n_agree_with_stored_protein", "pct_agree", "n_exact",
        "n_alt_start", "n_recoded_stop", "n_mismatch",
        "n_agree_after_a_one_base_frame_shift(NEGATIVE CONTROL, must be ~0)", "route"]).assign(
            seed=SEED, unit="records", denominator="the seeded sample named in n_sampled"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
