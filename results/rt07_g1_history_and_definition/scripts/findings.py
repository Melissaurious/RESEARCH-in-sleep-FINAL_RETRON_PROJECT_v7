#!/usr/bin/env python3
"""Prose and value lookups for the rt07_g1 report.

Every number the report renders is declared here as a five-tuple
(table, selector, column, format) and resolved from a landed table at build time. The
assembler computes nothing: if a placeholder has no declared lookup, or its selector does
not match exactly one row, the build fails rather than rendering a plausible number.
"""
from __future__ import annotations

# key -> (table, {selector column: value}, value column, format)
VALUES: dict[str, tuple] = {
    "n_sources": ("g1_summary.tsv", {"quantity": "sources_in_evidence_set"}, "value", "int"),
    "n_regions": ("g1_summary.tsv", {"quantity": "region_names_in_scope"}, "value", "int"),
    "n_cells": ("g1_summary.tsv", {"quantity": "matrix_cells"}, "value", "int"),
    "n_cells_evidence": ("g1_summary.tsv", {"quantity": "cells_with_evidence"}, "value", "int"),
    "n_cells_not_named": ("g1_summary.tsv", {"quantity": "cells_not_named"}, "value", "int"),
    "n_quotes": ("g1_summary.tsv", {"quantity": "quotes_verified"}, "value", "int"),
    "n_quotes_bad": ("g1_summary.tsv", {"quantity": "quotes_unverifiable"}, "value", "int"),
    "n_edges": ("g1_summary.tsv", {"quantity": "genealogy_edges"}, "value", "int"),
    "n_edges_unheld": ("g1_summary.tsv", {"quantity": "genealogy_edges_to_unheld_sources"},
                       "value", "int"),
    "n_stated_boundary": ("g1_summary.tsv",
                          {"quantity": "regions_with_stated_residue_boundary"}, "value", "int"),
    "n_derivable": ("g1_summary.tsv", {"quantity": "regions_derivable_procedure_only"},
                    "value", "int"),
    "n_no_basis": ("g1_summary.tsv", {"quantity": "regions_no_operational_basis"},
                   "value", "int"),
    "n_not_in_evidence": ("g1_summary.tsv", {"quantity": "regions_not_in_held_evidence"},
                          "value", "int"),
    "n_unresolved": ("g1_summary.tsv", {"quantity": "unresolved_items_open"}, "value", "int"),
    "n_controls": ("g1_summary.tsv", {"quantity": "positive_controls_pass"}, "value", "int"),
    "n_second": ("g1_summary.tsv", {"quantity": "second_count_checks"}, "value", "int"),
    "n_second_differ": ("g1_summary.tsv", {"quantity": "second_count_disagreements"},
                        "value", "int"),
    "aln_seqs": ("g1_summary.tsv", {"quantity": "align000044_sequences"}, "value", "int"),
    "aln_cols": ("g1_summary.tsv", {"quantity": "align000044_columns"}, "value", "int"),
    "aln_subdomains": ("g1_summary.tsv",
                       {"quantity": "align000044_numbered_subdomain_annotations"},
                       "value", "int"),
    "n_acquired": ("g1_summary.tsv", {"quantity": "assets_acquired_verified"}, "value", "int"),
    "n_missing_primary": ("g1_summary.tsv", {"quantity": "assets_missing_primary"},
                          "value", "int"),
    "aln_rt_span": ("g1_align000044_record_summary.tsv",
                    {"quantity": "annotated_domain:reverse_transcriptase"}, "value", "str"),
    "aln_domains": ("g1_align000044_record_summary.tsv",
                    {"quantity": "n_annotated_domains"}, "value", "int"),
    "aln_method": ("g1_align000044_record_summary.tsv",
                   {"quantity": "alignment_method"}, "value", "str"),
    "aln_submitted": ("g1_align000044_record_summary.tsv",
                      {"quantity": "submission_date"}, "value", "str"),
    "aln_bytes": ("g1_acquisition_source_resolution.tsv",
                  {"file_name": "ALIGN_000044.dat"}, "bytes", "int"),
    "aln_state": ("g1_acquisition_source_resolution.tsv",
                  {"file_name": "ALIGN_000044.dat"}, "resolution_state", "str"),
    "n_op_yes": ("g1_summary.tsv", {"quantity": "operational_pairs_yes"}, "value", "int"),
    "n_op_no": ("g1_summary.tsv", {"quantity": "operational_pairs_no"}, "value", "int"),
    "xiong_blocks": ("g1_literature_evidence_matrix.tsv",
                     {"source_id": "xiong1990", "region_id": "domain_5"},
                     "evidence_class", "str"),
    "rt0_zimmerly": ("g1_literature_evidence_matrix.tsv",
                     {"source_id": "zimmerly2001", "region_id": "domain_0"},
                     "evidence_class", "str"),
    "rt1_spelling_xiong": ("g1_literature_evidence_matrix.tsv",
                           {"source_id": "xiong1990", "region_id": "rt1_spelling"},
                           "n_times_named_in_text", "int"),
    "rt1_spelling_zimmerly": ("g1_literature_evidence_matrix.tsv",
                              {"source_id": "zimmerly2001", "region_id": "rt1_spelling"},
                              "n_times_named_in_text", "int"),
    "rt0_verdict": ("g1_region_verdicts.tsv", {"region_id": "domain_0"}, "verdict", "str"),
    "domain1_verdict": ("g1_region_verdicts.tsv", {"region_id": "domain_1"},
                        "verdict", "str"),
    "domainX_verdict": ("g1_region_verdicts.tsv", {"region_id": "domain_X"},
                        "verdict", "str"),
    "motifE_verdict": ("g1_region_verdicts.tsv", {"region_id": "motif_E"}, "verdict", "str"),
    "motifF_verdict": ("g1_region_verdicts.tsv", {"region_id": "motif_F"}, "verdict", "str"),
}

TITLE = "rt07_g1_history_and_definition"
SUBTITLE = ("What the derivational primary sources actually define, and what they only "
            "name")

SECTIONS = [
    dict(num="1", title="The measurement",
         body="""This gate classified the evidence for every region name in scope across the
         derivational primary literature. {n_sources} sources x {n_regions} region names =
         {n_cells} cells; {n_cells_evidence} carry evidence, {n_cells_not_named} are cells
         where the source never names the region at all. Every classification rests on a
         verbatim quote checked against the extracted text by the code that builds this
         table: {n_quotes} quotes declared, {n_quotes_bad} unverifiable. A quote that cannot
         be found is a build failure, not a warning.""",
         caveat="""Naming is not defining, and not naming is not absence. A cell reading
         NOT_NAMED_IN_SOURCE says the source does not use that name - nothing about biology,
         and nothing about whether the source describes the region under another name.""",
         tables=["g1_literature_evidence_matrix.tsv", "g1_evidence_quotes.tsv"]),
    dict(num="2", title="ALIGN_000044 was acquired, and it does not contain the blocks",
         body="""The primary-source alignment behind the only held paper that numbers RT
         subdomains was approved for governed acquisition and is now in hand:
         {n_acquired} file(s), state {aln_state}, {aln_bytes} bytes, from the EMBL-EBI public
         archive; {n_missing_primary} asset(s) landed MISSING_PRIMARY_ASSET. It is a
         {aln_cols}-column alignment of {aln_seqs} protein sequences, submitted
         {aln_submitted}, built by {aln_method}. It annotates {aln_domains} domains - the RT
         domain at columns {aln_rt_span}, plus maturase and nuclease - and
         {aln_subdomains} numbered subdomains.""",
         caveat="""PROPOSED: the alignment is the right substrate for g2 and the wrong
         source for the labels. The blocks must be re-derived on it from the stated
         conservation criteria and the recovery reported as a measurement; they cannot be
         read off it. The record also states a manual adjustment step, so the alignment is a
         fixed primary artefact, not a reproducible procedure.""",
         tables=["g1_acquisition_source_resolution.tsv",
                 "g1_align000044_record_summary.tsv"]),
    dict(num="3", title="The numbering is inherited, and one link leaves the held set",
         body="""{n_edges} genealogy edges were traced, each carrying a verified quote.
         {n_edges_unheld} of them point at a source this project does not hold. The
         seven-way partition originates with Xiong & Eickbush 1990 (domains 1-7, 178 aa);
         Zimmerly 2001 numbers subdomains 0-7 but states plainly that the labels are
         inherited from three earlier papers and only adjusted against its own alignment;
         Blocker 2005 supplies the modern RT0-RT7 spelling as a respelling with citations.
         RT0 itself was renamed from domain Z in Malik, Burke & Eickbush 1999 - which is not
         held here.""",
         caveat="""PROPOSED: RT0's definitional source being unheld is the weakest link in
         the chain, and it is the link RT0 hangs from. Both held statements of RT0's scope
         cite that paper rather than deriving the region.""",
         tables=["g1_terminology_genealogy.tsv"]),
    dict(num="4", title="What can and cannot be operationalised",
         body="""Of {n_regions} region names: {n_stated_boundary} has a stated residue
         boundary, {n_derivable} have a derivable procedure but no coordinates,
         {n_no_basis} is NO_OPERATIONAL_BASIS and {n_not_in_evidence} is not in the held
         evidence at all. Across (source, region) pairs, {n_op_yes} could define an
         operational boundary and {n_op_no} could not. Xiong & Eickbush give a restatable
         criterion for the blocks - conserved positions present in over 50% of RT elements
         from three of the four most abundant groups - so the textual-criteria route of
         launcher 5e succeeds and figure digitisation is not needed to recover the criteria.
         What no source gives is a per-block residue extent.""",
         caveat="""RT0 lands {rt0_verdict} and domain 1 lands {domain1_verdict}; domain X
         lands {domainX_verdict}. Motif E lands {motifE_verdict} and motif F
         {motifF_verdict} - the F label does not exist in the held derivational sources.""",
         tables=["g1_region_verdicts.tsv", "g1_operational_evidence_matrix.tsv"]),
    dict(num="5", title="Spelling and concept are different objects",
         body="""The modern spelling RT1 appears {rt1_spelling_xiong} times in Xiong &
         Eickbush 1990 and {rt1_spelling_zimmerly} times in Zimmerly 2001. The concept is
         present in both; the spelling is not. Every modern-spelling row therefore lands
         SPELLING_ONLY_NO_INDEPENDENT_DERIVATION rather than a verdict about the block, so
         that 'RT1 has no operational basis' can never be read off this table as a statement
         about domain 1.""",
         caveat="""Zimmerly 2001's evidence class for subdomain 0 is {rt0_zimmerly} and
         Xiong's for domain 5 is {xiong_blocks}. Different classes, different objects,
         different papers.""",
         tables=["g1_token_census.tsv", "g1_region_verdicts.tsv"]),
    dict(num="6", title="Controls and the second count",
         body="""{n_controls} positive controls pass: the modern-spelling detector is
         demonstrated on a source known to use that spelling, and the alignment-annotation
         detector is demonstrated on the alignment record itself before its zero is
         reported. {n_second} independent second-count checks were run through a route
         sharing no code with the census, with {n_second_differ} disagreements.""",
         caveat="""The alignment-annotation control earned its place: on the first run it
         FAILED, because EMBL line-type codes split every wrapped sentence. The zero it was
         guarding was an artefact, and the control is what found it.""",
         tables=["g1_detector_positive_control.tsv", "g1_second_counts.tsv",
                 "g1_census_route_agreement.tsv"]),
    dict(num="7", title="What stays open",
         body="""{n_unresolved} items are open in the unresolved-definition register,
         including where RT0 is actually defined, which blocks Simon & Zimmerly's 59
         across-the-set alignable characters fall in, and whether Figure 1's printed columns
         yield per-block extents.""",
         caveat="""Two questions are deliberately NOT answered here and may not be settled
         by a gate: whether this operational method becomes its own methods paper, and how
         any future RT1 concordance failure is interpreted.""",
         tables=["g1_unresolved_definition_register.tsv", "g1_prior_reconciliation.tsv"]),
]
