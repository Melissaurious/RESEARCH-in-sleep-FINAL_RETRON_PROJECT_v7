#!/usr/bin/env python3
"""rt07_g1 step 6 - the rollup, and the reconciliation against prior statements.

g1_summary.tsv is the gate's headline table: every quantity resolves to a landed table, so
no number in the report is computed by the report.

g1_prior_reconciliation.tsv is where prior statements meet what this gate actually read.
Prior work is PRIOR / UNVERIFIED (launcher 5d): it is reconciled, never adopted. A prior
statement that this gate confirms lands AGREE with the quote that confirms it; one it
cannot confirm lands UNVERIFIED_HERE with what is missing. No prior number becomes an
acceptance criterion here, including the ones that turned out to be right.

Writes (under --out): g1_summary.tsv, g1_prior_reconciliation.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g1lib import read_tsv, write_tsv  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    T = args.out

    census = read_tsv(T / "g1_token_census.tsv")
    matrix = read_tsv(T / "g1_literature_evidence_matrix.tsv")
    quotes = read_tsv(T / "g1_evidence_quotes.tsv")
    gen = read_tsv(T / "g1_terminology_genealogy.tsv")
    verdicts = read_tsv(T / "g1_region_verdicts.tsv")
    unres = read_tsv(T / "g1_unresolved_definition_register.tsv")
    acq = read_tsv(T / "g1_acquisition_source_resolution.tsv")
    ctrl = read_tsv(T / "g1_detector_positive_control.tsv")
    second = read_tsv(T / "g1_second_counts.tsv")
    aln = {r["quantity"]: r["value"] for r in read_tsv(T / "g1_align000044_record_summary.tsv")}
    ops = read_tsv(T / "g1_operational_evidence_matrix.tsv")

    sources = sorted({r["source_id"] for r in census})
    regions = sorted({r["region_id"] for r in census})

    def n(rows, **eq) -> int:
        return sum(1 for r in rows if all(r.get(k) == v for k, v in eq.items()))

    S = [
        ("sources_in_evidence_set", len(sources), "g1_token_census.tsv",
         "evidence source", "derivational primary literature plus the acquired alignment"),
        ("region_names_in_scope", len(regions), "g1_region_verdicts.tsv",
         "region name", "region names traced in this gate"),
        ("matrix_cells", len(matrix), "g1_literature_evidence_matrix.tsv",
         "(source, region) cell", f"{len(sources)} sources x {len(regions)} regions"),
        ("cells_with_evidence", sum(1 for m in matrix if m["evidence_class"] not in
                                    ("NOT_NAMED_IN_SOURCE", "NAMED_UNCLASSIFIED")),
         "g1_literature_evidence_matrix.tsv", "(source, region) cell", "all matrix cells"),
        ("cells_not_named", n(matrix, evidence_class="NOT_NAMED_IN_SOURCE"),
         "g1_literature_evidence_matrix.tsv", "(source, region) cell", "all matrix cells"),
        ("quotes_verified", len(quotes), "g1_evidence_quotes.tsv", "quoted passage",
         "assignments declared in control/"),
        ("quotes_unverifiable", n(quotes, verification="NOT_FOUND"),
         "g1_evidence_quotes.tsv", "quoted passage", "assignments declared in control/"),
        ("genealogy_edges", len(gen), "g1_terminology_genealogy.tsv", "genealogy edge",
         "edges traceable in the held derivational set"),
        ("genealogy_edges_to_unheld_sources",
         n(gen, antecedent_held_locally="NO"), "g1_terminology_genealogy.tsv",
         "genealogy edge", "all genealogy edges"),
        ("regions_with_stated_residue_boundary",
         n(verdicts, verdict="STATED_RESIDUE_BOUNDARY"), "g1_region_verdicts.tsv",
         "region name", "region names in scope"),
        ("regions_derivable_procedure_only", n(verdicts, verdict="DERIVABLE_PROCEDURE"),
         "g1_region_verdicts.tsv", "region name", "region names in scope"),
        ("regions_scope_rule_only", n(verdicts, verdict="SCOPE_RULE_ONLY"),
         "g1_region_verdicts.tsv", "region name", "region names in scope"),
        ("regions_no_operational_basis", n(verdicts, verdict="NO_OPERATIONAL_BASIS"),
         "g1_region_verdicts.tsv", "region name", "region names in scope"),
        ("regions_not_in_held_evidence", n(verdicts, verdict="NOT_IN_HELD_EVIDENCE"),
         "g1_region_verdicts.tsv", "region name", "region names in scope"),
        ("unresolved_items_open", n(unres, status="OPEN"),
         "g1_unresolved_definition_register.tsv", "open question",
         "items in the unresolved-definition register"),
        ("positive_controls_pass", n(ctrl, result="PASS"),
         "g1_detector_positive_control.tsv", "detector control",
         f"{len(ctrl)} controls declared"),
        ("second_count_checks", len(second), "g1_second_counts.tsv", "spot-check",
         "independent second-count checks"),
        ("second_count_disagreements", n(second, agreement="DIFFER"),
         "g1_second_counts.tsv", "spot-check", "independent second-count checks"),
        ("align000044_sequences", aln.get("n_sequences", "NOT_ACQUIRED"),
         "g1_align000044_record_summary.tsv", "aligned sequence",
         "n/a - one primary alignment record"),
        ("align000044_columns", aln.get("alignment_columns", "NOT_ACQUIRED"),
         "g1_align000044_record_summary.tsv", "alignment column",
         "n/a - one primary alignment record"),
        ("align000044_numbered_subdomain_annotations",
         aln.get("n_numbered_subdomain_annotations", "NOT_ACQUIRED"),
         "g1_align000044_record_summary.tsv", "annotation",
         "the whole alignment record, by a detector validated on that record"),
        ("assets_acquired_verified", n(acq, resolution_state="ACQUIRED_VERIFIED"),
         "g1_acquisition_source_resolution.tsv", "acquired file",
         "files approved for governed acquisition"),
        ("assets_missing_primary", n(acq, resolution_state="MISSING_PRIMARY_ASSET"),
         "g1_acquisition_source_resolution.tsv", "acquired file",
         "files approved for governed acquisition"),
        ("operational_pairs_yes",
         n(ops, can_define_operational_boundary="YES"),
         "g1_operational_evidence_matrix.tsv", "(source, region) pair",
         "pairs assessed in the operational-evidence matrix"),
        ("operational_pairs_no", n(ops, can_define_operational_boundary="NO"),
         "g1_operational_evidence_matrix.tsv", "(source, region) pair",
         "pairs assessed in the operational-evidence matrix"),
    ]

    write_tsv(T / "g1_summary.tsv", ["quantity", "value", "source_table", "unit",
                                     "denominator"],
              [{"quantity": q, "value": v, "source_table": t, "unit": u, "denominator": d}
               for q, v, t, u, d in S])

    def cell(src, rid, col="evidence_class"):
        return next((m[col] for m in matrix
                     if m["source_id"] == src and m["region_id"] == rid), "ABSENT")

    prior = [
        {"quantity": "Zimmerly 2001 defines subdomain 0 as conserved only between group II "
                     "intron and non-LTR RTs (prior dossier D9)",
         "prior": "USE_AS_PRIOR - quoted from p.1241, to be re-verified at the PDF",
         "g1": "CONFIRMED verbatim in the extracted text (assignment Z06)",
         "verdict": "AGREE",
         "note": "The single most load-bearing prior reading in the dossier now rests on the "
                 "source instead of on the dossier. RT0 stays analytically separate."},
        {"quantity": "Simon & Zimmerly 2008 transferability: retrons 157, group II introns "
                     "177, DGRs 179, five other groups 126-167",
         "prior": "COMPARATOR_ONLY benchmark, never extracted by this project before",
         "g1": "CONFIRMED verbatim (assignment S04); retrons are the hard case",
         "verdict": "AGREE",
         "note": "Extracted at last, and it is the external benchmark g6 will improve on."},
        {"quantity": "The 59 characters alignable across all bacterial RTs lie in RT domains 3-5",
         "prior": "stated in the prior dossier",
         "g1": "The count of 59 is confirmed (S07); the localisation to domains 3-5 does NOT "
               "appear in the extracted running text",
         "verdict": "UNVERIFIED_HERE",
         "note": "Register item U02. Figure 4 was not read in this gate, so the claim is "
                 "neither confirmed nor refuted - it is unsupported by what was read."},
        {"quantity": "Xiong & Eickbush 1990 drew Figure 1 boundaries by eye with no published "
                     "criterion",
         "prior": "the familiar story the dossier flagged as possibly false",
         "g1": "REFUTED: the paper states an explicit quantitative criterion - conserved "
               "positions present in over 50% of RT elements from three of the four most "
               "abundant groups (X04), with the construction procedure in Methods (X02)",
         "verdict": "DIFFER",
         "note": "Route 2 of launcher 5e succeeds. Figure digitisation is therefore not "
                 "needed to recover the criteria, only possibly the extents (U03)."},
        {"quantity": "ALIGN_000044 would let the historical frame be read off the authors own "
                     "alignment columns",
         "prior": "the stated reason the asset was high value",
         "g1": "PARTLY REFUTED: the record was acquired and annotates three domains "
               "(RT 261-886, maturase 1123-1235, nuclease 1319-1441) and zero numbered "
               "subdomains",
         "verdict": "DIFFER",
         "note": "The alignment is the right substrate but carries no block labels, so g2 "
                 "must re-derive the blocks on it rather than read them off (U04)."},
        {"quantity": "Trap D10 - Simon & Zimmerly do not license a LIV residue criterion",
         "prior": "registered trap, already paid for once",
         "g1": "CONFIRMED verbatim (S06): the hydrophobic statement is about position 2 of "
               "Y/FxDD and the excluded class differs elsewhere",
         "verdict": "AGREE", "note": "Closed by verification; register item U07."},
        {"quantity": "RT1-RT7 numbering appears in none of the four Tier-1 papers "
                     "(reference-package string census)",
         "prior": "recorded in references/rt0_rt7/README.md",
         "g1": f"CONFIRMED by an independently written detector validated on a positive "
               f"control: modern RT1 spelling in xiong1990 = "
               f"{cell('xiong1990', 'rt1_spelling', 'n_times_named_in_text')}, "
               f"zimmerly2001 = "
               f"{cell('zimmerly2001', 'rt1_spelling', 'n_times_named_in_text')}",
         "verdict": "AGREE",
         "note": "The numbered concept is present; the modern spelling is not. Spelling and "
                 "concept are kept as separate rows throughout this gate."},
    ]
    for p in prior:
        p.update({"unit": "prior statement", "denominator":
                  "prior statements this gate could test against its own reading"})
    write_tsv(T / "g1_prior_reconciliation.tsv",
              ["quantity", "prior", "g1", "verdict", "note", "unit", "denominator"], prior)

    print(f"summary rows: {len(S)}; prior statements reconciled: {len(prior)}")
    for q, v, *_ in S:
        print(f"  {q:<44} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
