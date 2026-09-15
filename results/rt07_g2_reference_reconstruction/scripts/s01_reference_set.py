#!/usr/bin/env python3
"""rt07_g2 step 1 - the curated historical reference sequence set and its groups.

The reference set is not assembled by this project's judgement: it is the 66 proteins of
ALIGN_000044, the alignment the authors of the only held subdomain-numbering paper built and
adjusted their labels against. Curation here means verifying identity, un-gapping the
sequences, and assigning each to one of the four lineage groups the criterion needs - by
declared keyword rules over the record's OWN description lines, never by hand.

Identity is checked against the g1 acquisition record before anything is parsed: 66
sequences, 1441 columns, sha256 as retrieved. If the alignment and the g1 record disagree,
nothing runs.

Writes: tables/g2_reference_sequence_set.tsv, tables/g2_lineage_groups.tsv,
        tables/g2_substrate_identity.tsv, and (under --work) the ungapped FASTA.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g2lib import (ACQUIRED, G1, assign_groups, control, parse_clustal,  # noqa: E402
                       parse_descriptions, read_tsv, sha256, write_tsv)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    aln_p, dat_p = ACQUIRED / "ALIGN_000044.aln", ACQUIRED / "ALIGN_000044.dat"
    g1_reg = {r["file_name"]: r for r in
              read_tsv(G1 / "tables/g1_acquisition_source_resolution.tsv")}
    g1_sum = {r["quantity"]: r["value"] for r in
              read_tsv(G1 / "tables/g1_align000044_record_summary.tsv")}

    problems = []
    for p in (aln_p, dat_p):
        rec = g1_reg.get(p.name)
        if rec is None:
            problems.append(f"{p.name}: no g1 acquisition row")
        elif rec["resolution_state"] != "ACQUIRED_VERIFIED":
            problems.append(f"{p.name}: g1 state is {rec['resolution_state']}")
        elif sha256(p) != rec["sha256"]:
            problems.append(f"{p.name}: sha256 differs from the g1 acquisition record")

    seqs = parse_clustal(aln_p)
    ncol = len({len(s) for s in seqs.values()})
    if ncol != 1:
        problems.append("alignment rows are not all the same length")
    width = len(next(iter(seqs.values())))
    if str(len(seqs)) != g1_sum.get("n_sequences"):
        problems.append(f"sequence count {len(seqs)} != g1 record {g1_sum.get('n_sequences')}")
    if str(width) != g1_sum.get("alignment_columns"):
        problems.append(f"column count {width} != g1 record {g1_sum.get('alignment_columns')}")
    if problems:
        for p in problems:
            print(f"FAIL {p}", file=sys.stderr)
        return 1

    desc = parse_descriptions(dat_p)
    groups = assign_groups(desc, control("lineage_rules.tsv"))

    refset, counts = [], {}
    fasta = []
    for name, aligned in seqs.items():
        ung = aligned.replace("-", "")
        g, rule = groups.get(name, ("UNASSIGNED", "none"))
        counts[g] = counts.get(g, 0) + 1
        refset.append({
            "sequence_id": name, "description": desc.get(name, "NOT_IN_RECORD"),
            "lineage_group": g, "assigned_by_rule": rule,
            "ungapped_length_aa": len(ung),
            "aligned_columns_occupied": len(ung),
            "occupancy_fraction": f"{len(ung) / width:.4f}",
            "unit": "reference protein sequence",
            "denominator": f"{len(seqs)} proteins in ALIGN_000044",
        })
        fasta.append(f">{name} {desc.get(name, '')}\n{ung}")

    text = "\n".join(fasta) + "\n"
    (args.work / "reference_set.faa").write_text(text, encoding="utf-8")
    # The curated reference sequence set is a required landed product (launcher 7c), so it
    # lives in the bundle, not only in scratch.
    landed = args.out.parent / "reference"
    landed.mkdir(parents=True, exist_ok=True)
    (landed / "g2_reference_set.faa").write_text(text, encoding="utf-8")

    write_tsv(args.out / "g2_reference_sequence_set.tsv",
              ["sequence_id", "description", "lineage_group", "assigned_by_rule",
               "ungapped_length_aa", "aligned_columns_occupied", "occupancy_fraction",
               "unit", "denominator"], refset)
    write_tsv(args.out / "g2_lineage_groups.tsv",
              ["lineage_group", "n_sequences", "pct_of_set", "unit", "denominator"],
              [{"lineage_group": g, "n_sequences": n,
                "pct_of_set": f"{100 * n / len(seqs):.2f}",
                "unit": "reference protein sequence",
                "denominator": f"{len(seqs)} proteins in ALIGN_000044"}
               for g, n in sorted(counts.items(), key=lambda kv: -kv[1])])
    write_tsv(args.out / "g2_substrate_identity.tsv",
              ["quantity", "value", "verified_against", "unit", "denominator"],
              [{"quantity": k, "value": v,
                "verified_against": "rt07_g1 acquisition record and alignment summary",
                "unit": "substrate property",
                "denominator": "n/a - one primary alignment record"}
               for k, v in [("accession", "ALIGN_000044"), ("n_sequences", len(seqs)),
                            ("alignment_columns", width),
                            ("sha256_aln", sha256(aln_p)), ("sha256_dat", sha256(dat_p)),
                            ("unassigned_sequences", counts.get("UNASSIGNED", 0))]])

    print(f"reference set: {len(seqs)} proteins, {width} columns")
    for g, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {g:<20} {n}")
    return 1 if counts.get("UNASSIGNED") else 0


if __name__ == "__main__":
    raise SystemExit(main())
