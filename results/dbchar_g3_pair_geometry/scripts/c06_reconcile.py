#!/usr/bin/env python3
"""c06 - reconcile g3 against its independent second count, the landed g2/g2b bundles, and
prior work. Prior values are read only here, after every g3 number exists."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--g2-bundle", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    p = pd.read_parquet(W / "derived" / "rt_ncrna_pairs_v1.parquet",
                        columns=["direction", "same_strand", "record_key", "geometry_eligible",
                                 "canonical", "locus_key", "nc_seq_hash", "rt_seq_hash", "gap_bp"])
    sec = {x["measure"]: int(x["n"]) for x in rd(W / "second" / "c05_geometry.tsv")}
    A = []

    def cmp(check, ra, va, rb, vb):
        A.append([check, ra, va, rb, vb, va - vb, "AGREE" if va == vb else "DISAGREE"])

    cmp("placements_total", "p01 (parquet, python)", len(p), "c05 (awk on raw bytes)",
        sec["ncrna_placements_total"])
    for d in ("upstream", "downstream", "overlapping"):
        cmp(f"direction_{d}", "p01", int((p.direction == d).sum()), "c05", sec[f"direction_{d}"])
    cmp("same_strand", "p01", int((p.same_strand == True).sum()), "c05", sec["same_strand"])  # noqa: E712
    cmp("opposite_strand", "p01", int((p.same_strand == False).sum()), "c05", sec["opposite_strand"])  # noqa: E712
    cmp("abutting_gap_zero", "p01 gap_bp == 0 and not overlapping",
        int(((p.gap_bp == 0) & (p.direction != "overlapping")).sum()), "c05", sec["abutting_gap_zero"])
    cmp("records_carrying_at_least_one_call", "p01", int(p.record_key.nunique()), "c05",
        sec["records_carrying_at_least_one_call"])

    # against the landed g2 bundle
    rec = pd.read_parquet(Path(a.derived) / "rt_records_v1.parquet", columns=["n_ncrna", "record_key"])
    cmp("sum of n_ncrna over all RT-anchored records", "g2 derived rt_records_v1",
        int(rec.n_ncrna.sum()), "g3 placements", len(p))
    g2t = {x["quantity"]: x["value"] for x in rd(Path(a.g2_bundle) / "tables" / "g2_summary.tsv")}
    cmp("ncRNA calls in the corpus", "landed g2 registry",
        int([x["rows"] for x in rd(Path(a.g2_bundle) / "tables" / "g2_derived_registry.tsv")
             if x["dataset"] == "rt_ncrna_calls_v1.parquet"][0]), "g3 placements", len(p))
    pd.DataFrame(A, columns=["check", "route_a", "value_a", "route_b", "value_b",
                             "delta_a_minus_b", "agreement"]).to_csv(
        T / "g3_second_counts.tsv", sep="\t", index=False)

    # ---- prior work, read only now ---------------------------------------------------
    B = []

    def rec_(quantity, prior, mine, verdict, note):
        B.append([quantity, prior, mine, verdict, note])

    qc = {x["measure"]: x for x in rd(T / "g3_shipped_field_qc.tsv")}
    sem = rd(T / "g3_shipped_field_semantics.tsv")
    best = max(sem, key=lambda x: int(x["n_equal"]))
    rec_("`position_relative_to_rt` is unusable as a direction label",
         "prior: shipped field is a signed bp offset, null for most records; a prior analysis "
         "miscounted its null rate as 'upstream'",
         f"null in {qc['position_relative_to_rt_null']['n']} of {qc['position_relative_to_rt_null']['denominator_n']} "
         f"placements; best coordinate frame ({best['candidate_reference_frame']}) reproduces "
         f"{best['n_equal']}/{best['n_compared']}",
         "CONFIRMED",
         "g3 goes further: no coordinate frame explains it; its variation is -(RT offset into "
         "the window) plus a term tracking the intergenic-region index")
    mm = {x["measure"]: x for x in rd(T / "g3_ncrna_model_multiplicity.tsv")}
    n_multi = int(mm["called_by_more_than_one_model"]["n"])
    rec_("no ncRNA sequence is called by more than one covariance model",
         "prior: zero, with the caveat that the pipeline selects one model per region",
         f"{n_multi} of {mm['exact_ncRNA_sequences']['n']} exact ncRNA sequences",
         "CONFIRMED" if n_multi == 0 else "CHANGED",
         "the caveat stands either way: one model per call is imposed upstream, so this is not "
         "evidence about CM specificity")
    rec_("RT<->ncRNA gap definition",
         "prior: `gap` was a coordinate difference, so abutting features read 1",
         "g3: bases strictly between; abutting = 0, overlap reported separately",
         "CHANGED", "definition changed deliberately; prior distance bins are not comparable "
                    "to g3 bins at the boundary")
    rec_("direction convention",
         "prior: transcription-relative upstream/downstream, but the shipped distance columns "
         "were measured from the ncRNA start in contig frame",
         "g3: direction and signed distance are both transcription-relative; contig-frame "
         "values retained beside them",
         "CHANGED", "same convention for direction, a different one for distance")
    pd.DataFrame(B, columns=["quantity", "prior", "g3", "verdict", "note"]).to_csv(
        T / "g3_prior_reconciliation.tsv", sep="\t", index=False)

    bad = sum(1 for x in A if x[-1] != "AGREE")
    print(f"c06: second counts {len(A)} rows, {bad} DISAGREE; prior rows {len(B)}")
    for x in A:
        if x[-1] != "AGREE":
            print("  A", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
