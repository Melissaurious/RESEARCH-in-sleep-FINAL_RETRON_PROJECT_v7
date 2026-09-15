#!/usr/bin/env python3
"""c05 - reconcile g2: (A) against its independent second count and the landed g1 bundle,
(B) against the prior project's landed units, classified only AFTER (A) is computed.

Prior values are read here and nowhere else. Anti-anchoring: nothing in e01/a02/c03 reads a
prior artifact, so every g2 number is derived from the pinned g1 corpus first and compared
second. Each prior row is classified CONFIRMED / CHANGED / OBSOLETE / UNRESOLVED with the
grain difference stated, because the prior grain is not always this project's grain.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--g1-bundle", required=True)
    ap.add_argument("--prior-locus-table", required=True)
    ap.add_argument("--prior-rt-unique", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    r = pd.read_parquet(W / "derived" / "rt_records_v1.parquet",
                        columns=["source_file", "rt_system_id", "locus_key", "physical_locus_key",
                                 "rt_seq_hash", "n_rt_cds", "window_inverted", "rt_in_window",
                                 "ncrna_count_qc", "file_label", "is_first_copy", "n_ncrna",
                                 "genome_id_norm", "elig_geometry", "elig_rt_coords"])
    ladder = {x["unit"]: int(x["n"]) for x in rd(T / "g2_unit_ladder.tsv")}
    dist = {x["measure"]: int(x["n"]) for x in rd(W / "second" / "c03_distinct.tsv")}
    per_file = {x["source_file"]: x for x in rd(W / "second" / "c03_per_file.tsv")}
    f = r[r.is_first_copy]

    A = []

    def cmp(check, scope, ra, va, rb, vb):
        A.append([check, scope, ra, va, rb, vb, (va - vb) if isinstance(va, int) and isinstance(vb, int) else "",
                  "AGREE" if va == vb else "DISAGREE"])

    cmp("records_total", "RT-anchored corpus", "e01 json census", len(r),
        "c03 awk line count", dist["lines_total"])
    for fn, g in r.groupby("source_file"):
        cmp("records_per_file", fn, "e01 json census", len(g),
            "c03 awk line count", int(per_file[fn]["n_lines"]))
    cmp("distinct_rt_system_id", "RT-anchored corpus", "e01", int(r.rt_system_id.nunique()),
        "c03 sort -u", dist["distinct_rt_system_id"])
    # NOTE: the locus key and rt_system_id are NOT independent - the id encodes contig and RT
    # start. What differs between the routes is the PARSER, not the definition.
    cmp("distinct_locus_key", "distinct raw records", "e01 (json)", ladder["locus"],
        "c03 (awk byte slice)", dist["distinct_locus_key"])
    cmp("distinct_exact_rt", "distinct raw records", "e01 sha256 of normalised sequence",
        ladder["exact_rt"], "c03 sort -u of the same normalised string",
        dist["distinct_exact_rt_sequence"])
    cmp("records_without_rt_cds", "RT-anchored corpus", "e01 is_rt_gene count",
        int((r.n_rt_cds == 0).sum()), "c03 substring test", dist["lines_without_is_rt_gene_true"])
    cmp("window_inverted", "RT-anchored corpus", "e01", int(r.window_inverted.sum()),
        "c03 numeric compare", dist["window_inverted"])
    cmp("rt_not_inside_window", "RT-anchored corpus", "e01", int((~r.rt_in_window).sum()),
        "c03 numeric compare", dist["rt_not_inside_window"])

    # --- against the LANDED g1 bundle (a different gate, different code) ---------------
    g1 = Path(a.g1_bundle) / "tables"
    pops = {x["population"]: int(x["n_lines"]) for x in rd(g1 / "s02_populations.tsv")}
    cmp("RT-anchored records", "g1 POP-RT-FAM + POP-RT-MULTI", "e01", len(r),
        "g1 bundle s02_populations.tsv", pops["POP-RT-FAM"] + pops["POP-RT-MULTI"])
    cmp("MULTI records", "g1 POP-RT-MULTI", "e01", int(r.file_label.eq("MULTI").sum()),
        "g1 bundle", pops["POP-RT-MULTI"])
    v = {(x["population"], x["check_id"]): int(x["n_flagged"]) for x in rd(g1 / "s02_validation_by_population.tsv")}
    pop = r.file_label.eq("MULTI").map({True: "POP-RT-MULTI", False: "POP-RT-FAM"})
    for p in ("POP-RT-FAM", "POP-RT-MULTI"):
        s = r[pop.eq(p)]
        cmp("records_without_rt_cds", p, "e01", int((s.n_rt_cds == 0).sum()), "g1 check V09a", v[(p, "V09a")])
        cmp("window_inverted", p, "e01", int(s.window_inverted.sum()), "g1 check V16", v[(p, "V16")])
        cmp("ncrna_count_mismatch", p, "e01 ncrna_count_qc != agree",
            int((s.ncrna_count_qc != "agree").sum()), "g1 check V12", v[(p, "V12")])
    dup = {x["scope"]: int(x["n_lines_beyond_first"]) for x in rd(g1 / "s02_byte_identical_records.tsv")
           if x["populations"] in ("POP-RT-FAM", "POP-RT-MULTI", "POP-RT-FAM|POP-RT-MULTI")}
    cmp("byte_identical_extra_copies", "RT-anchored corpus", "e01", len(r) - ladder["distinct_raw_record"],
        "g1 s02_byte_identical_records.tsv", sum(dup.values()))
    pd.DataFrame(A, columns=["check", "scope", "route_a", "value_a", "route_b", "value_b",
                             "delta_a_minus_b", "agreement"]).to_csv(
        T / "g2_second_counts.tsv", sep="\t", index=False)

    # --- (B) prior project, read only now ---------------------------------------------
    B = []

    def rec(quantity, prior_scope, prior, mine_scope, mine, verdict, note):
        B.append([quantity, prior_scope, prior, mine_scope, mine,
                  (mine - prior) if isinstance(prior, int) and isinstance(mine, int) else "",
                  verdict, note])

    pl = pq.read_metadata(a.prior_locus_table)
    prior_loci = pl.num_rows
    rec("locus count", "prior locus_table_v1.parquet (P-LOC-COLLAPSED: NZ_ twins folded)",
        prior_loci, "g2 physical_locus (NZ_-normalised)", ladder["physical_locus"],
        "CONFIRMED" if prior_loci == ladder["physical_locus"] else "CHANGED",
        "prior folded NZ_ twins only when a 4-criteria evidence rule passed; g2 reports the "
        "normalised grain and the evidence class separately (g2_twin_evidence.tsv)")
    rec("locus count", "prior locus_table_v1.parquet", prior_loci,
        "g2 locus (contig spelling as given)", ladder["locus"],
        "CONFIRMED" if prior_loci == ladder["locus"] else "CHANGED",
        "different grain: g2 locus keeps the contig spelling, so twins are two loci")
    # Count comparison is weak for a key set: two sets of equal size can be disjoint. Compare
    # the KEYS. (The prior file carries 9 comment lines; counting lines once read them as rows.)
    prior_keys = set(pd.read_csv(a.prior_rt_unique, sep="\t", comment="#",
                                 usecols=["rt_prot_sha256"]).rt_prot_sha256)
    mine_keys = set(pd.read_parquet(W / "derived" / "rt_exact_v1.parquet",
                                    columns=["rt_seq_hash"]).rt_seq_hash)
    only_prior, only_mine = len(prior_keys - mine_keys), len(mine_keys - prior_keys)
    rec("exact RT count", "prior rt_unique_v1.tsv keys", len(prior_keys),
        "g2 exact_rt (sha256 of sequence, one trailing * removed)", ladder["exact_rt"],
        "CONFIRMED" if len(prior_keys) == ladder["exact_rt"] else "CHANGED",
        "same declared hash rule, independently re-derived from the pinned g1 corpus")
    rec("exact RT key set", "keys only in the prior set", only_prior,
        "keys only in the g2 set", only_mine,
        "CONFIRMED" if only_prior == only_mine == 0 else "CHANGED",
        "set comparison, not a count comparison: equal sizes would not prove equal sets")

    # Decompose the locus difference instead of asserting it: the prior grain is the
    # rt_system_id (which encodes contig + RT start), g2's is the RT coordinate interval.
    n_ids = int(r.rt_system_id.nunique())
    rec("loci carrying more than one rt_system_id", "not measured by the prior grain", 0,
        "g2 loci where the id differs but the RT interval does not",
        int((f.groupby("locus_key").rt_system_id.nunique() > 1).sum()),
        "CHANGED", f"id grain {n_ids} vs coordinate grain {ladder['locus']}: the difference is "
                   "loci whose records carry different id suffixes at one RT interval")
    rec("twin pairs folded", "prior: id-string pairs (X, NZ_X) passing a 4-criteria rule",
        n_ids - prior_loci, "g2: physical loci with two contig spellings, same rule on evidence",
        ladder["locus"] - ladder["physical_locus"], "CHANGED",
        "g2 pairs on the RT coordinate interval, so a twin whose id suffix differs is still a "
        "pair; the prior id-string test could not see those")
    # A prose finding from the prior g0 README, re-derived here before being read:
    # "9 loci appear in more than one source file".
    PRIOR_G0_CROSS_FILE_LOCI = 9
    xf = {x["measure"]: int(x["n_loci"]) for x in rd(T / "g2_locus_conflicts.tsv")}
    mine_xf = xf["loci_spanning_more_than_one_source_file_INCLUDING_duplicate_copies"]
    rec("loci in more than one source file", "prior g0 README (prose)", PRIOR_G0_CROSS_FILE_LOCI,
        "g2 over all records including byte-identical duplicate copies", mine_xf,
        "CONFIRMED" if mine_xf == PRIOR_G0_CROSS_FILE_LOCI else "CHANGED",
        "counted over ALL records: these loci are byte-identical lines filed in two family "
        "files, so a first-copy-only count reads 0")
    pd.DataFrame(B, columns=["quantity", "prior_scope", "prior_value", "g2_scope", "g2_value",
                             "delta", "verdict", "note"]).to_csv(
        T / "g2_prior_reconciliation.tsv", sep="\t", index=False)

    nA = sum(1 for x in A if x[-1] != "AGREE")
    print(f"c05: second counts {len(A)} rows, {nA} DISAGREE; prior rows {len(B)}")
    for x in A:
        if x[-1] != "AGREE":
            print("  A", x)
    for x in B:
        print("  B", x[0], x[6], f"prior={x[2]} g2={x[4]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
