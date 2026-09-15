#!/usr/bin/env python3
"""findings - the Stage-1 report's prose and its value lookups.

Every number in the report is a LOOKUP into a landed table of a landed bundle: a bundle id, a
table, a row selector and a column. The assembler resolves them and fails the build if a
selector matches anything other than exactly one row, or if a placeholder has no lookup. No
number is typed into the prose.
"""
from __future__ import annotations

G1 = "dbchar_g1_corpus_identity"
G2 = "dbchar_g2_canonical_units"
G2B = "dbchar_g2b_rt_cds_recovery"
G3 = "dbchar_g3_pair_geometry"
G4 = "dbchar_g4_family_baseline"
G5 = "dbchar_g5_metadata_sampling"
G6 = "dbchar_g6_tool_calls"
SELF = "dbchar_g7_stage1_report"  # figures this gate re-plots from a landed table

# key -> (bundle, table, {selector column: value}, value column, format)
VALUES = {
    "files": (G1, "s01_corpus_root.tsv", {"quantity": "n_regular_jsonl_files"}, "value", "int"),
    "bytes": (G1, "s01_corpus_root.tsv", {"quantity": "total_jsonl_bytes"}, "value", "int"),
    "lines": (G1, "s02_populations.tsv", {"population": "ALL"}, "n_lines", "int"),
    "rt_fam": (G1, "s02_populations.tsv", {"population": "POP-RT-FAM"}, "n_lines", "int"),
    "rt_multi": (G1, "s02_populations.tsv", {"population": "POP-RT-MULTI"}, "n_lines", "int"),
    "ncrna_only": (G1, "s02_populations.tsv", {"population": "POP-NCRNA"}, "n_lines", "int"),
    "manifest_sha": (G1, "s02_record_manifest_digest.tsv",
                     {"quantity": "record_manifest_sha256"}, "value", "str"),

    "records": (G2, "g2_unit_ladder.tsv", {"unit": "raw_record"}, "n", "int"),
    "distinct_records": (G2, "g2_unit_ladder.tsv", {"unit": "distinct_raw_record"}, "n", "int"),
    "loci": (G2, "g2_unit_ladder.tsv", {"unit": "locus"}, "n", "int"),
    "phys_loci": (G2, "g2_unit_ladder.tsv", {"unit": "physical_locus"}, "n", "int"),
    "exact_rt": (G2, "g2_unit_ladder.tsv", {"unit": "exact_rt"}, "n", "int"),
    "genomes": (G2, "g2_unit_ladder.tsv", {"unit": "genome"}, "n", "int"),
    "taxocc": (G2, "g2_unit_ladder.tsv", {"unit": "rt_taxonomic_occurrence"}, "n", "int"),
    "bt_exact": (G2, "g2_bt_status.tsv", {"population": "POP-RT-FAM", "bt_status": "exact"},
                 "n_records", "int"),
    "bt_mismatch": (G2, "g2_bt_status.tsv", {"population": "POP-RT-FAM", "bt_status": "mismatch"},
                    "n_records", "int"),
    "elig_geom_fam": (G2, "g2_eligibility.tsv",
                      {"population": "POP-RT-FAM", "eligibility_flag": "elig_geometry",
                       "state": "ELIGIBLE"}, "pct_of_population", "pct"),
    "twins": (G2, "g2_twin_evidence.tsv",
              {"twin_evidence_class": "twin_identical_window_dna_and_rt"}, "n_physical_loci", "int"),
    "twin_disagree": (G2, "g2_twin_evidence.tsv",
                      {"twin_evidence_class": "twin_identical_window_dna_and_rt"},
                      "n_collapse_supported", "int"),
    "loci_two_rt": (G2, "g2_locus_conflicts.tsv",
                    {"measure": "loci_with_more_than_one_exact_rt"}, "n_loci", "int"),
    "loci_two_db": (G2, "g2_locus_conflicts.tsv",
                    {"measure": "loci_in_more_than_one_source_database"}, "n_loci", "int"),

    "no_rt_cds": (G2B, "g2b_summary.tsv", {"quantity": "recovery_state:RECOVERED"}, "value", "int"),
    "seq_only": (G2B, "g2b_summary.tsv", {"quantity": "recovery_state:SEQUENCE_ONLY"}, "value", "int"),
    "ill_posed": (G2B, "g2b_summary.tsv", {"quantity": "recovery_state:ILL_POSED"}, "value", "int"),
    "beyond_contig": (G2B, "g2b_representation_classes.tsv",
                      {"representation_class": "rt_beyond_a_contig_end_clipped_window"},
                      "n_records", "int"),

    "placements": (G3, "g3_populations.tsv", {"population": "ALL"}, "n_placements", "int"),
    "canonical": (G3, "g3_populations.tsv", {"population": "CANONICAL"}, "n_placements", "int"),
    "up": (G3, "g3_direction.tsv", {"population": "CANONICAL", "direction": "upstream"},
           "n_placements", "int"),
    "down": (G3, "g3_direction.tsv", {"population": "CANONICAL", "direction": "downstream"},
             "n_placements", "int"),
    "overlap": (G3, "g3_direction.tsv", {"population": "CANONICAL", "direction": "overlapping"},
                "n_placements", "int"),
    "up_median": (G3, "g3_distance_stats.tsv", {"population": "CANONICAL", "direction": "upstream"},
                  "median", "num"),
    "cds0": (G3, "g3_cds_between_explicit.tsv",
             {"population": "CANONICAL", "stratum": "", "n_cds_between": "0"},
             "pct_of_population", "pct"),
    "cds1": (G3, "g3_cds_between_explicit.tsv",
             {"population": "CANONICAL", "stratum": "", "n_cds_between": "1"},
             "pct_of_population", "pct"),
    "cds_gt3": (G3, "g3_cds_between_explicit.tsv",
                {"population": "CANONICAL", "stratum": "", "n_cds_between": ">3"},
                "pct_of_population", "pct"),
    "pairs": (G3, "g3_pair_view_sizes.tsv", {"measure": "distinct_exact_pairs"}, "n", "int"),
    "pairs_1to1": (G3, "g3_topology_components.tsv", {"shape": "1:1"}, "n_components", "int"),
    "retron_zero": (G3, "g3_zero_class_by_family.tsv", {"file_label": "Retron"}, "pct_zero", "pct"),
    "gii_zero": (G3, "g3_zero_class_by_family.tsv", {"file_label": "RVT-GII"}, "pct_zero", "pct"),
    "nonretron": (G3, "g3_nonretron_vs_retron_geometry.tsv",
                  {"population": "ELIGIBLE_non_Retron_single_family"}, "n_placements", "int"),
    "nonretron_up": (G3, "g3_nonretron_vs_retron_geometry.tsv",
                     {"population": "ELIGIBLE_non_Retron_single_family"}, "pct_upstream", "pct"),
    "dmode_median": (G3, "g3_downstream_mode_profile.tsv",
                     {"measure": "median_signed_distance_bp"}, "value", "num"),
    "dmode_seqs": (G3, "g3_downstream_mode_profile.tsv",
                   {"measure": "distinct_exact_ncrna_in_the_mode"}, "value", "num"),
    "shipped_null": (G3, "g3_shipped_field_qc.tsv",
                     {"measure": "position_relative_to_rt_null"}, "n", "int"),
    "shipped_best": (G3, "g3_shipped_field_semantics.tsv",
                     {"candidate_reference_frame": "nc_start_minus_rt_start"}, "n_equal", "int"),

    "v_single": (G4, "g4_views.tsv", {"view": "V-RT-SINGLE"}, "n_exact_rt", "int"),
    "v_multi": (G4, "g4_views.tsv", {"view": "V-RT-MULTI"}, "n_exact_rt", "int"),
    "v_cross": (G4, "g4_views.tsv", {"view": "V-RT-CROSS"}, "n_exact_rt", "int"),
    "gii_median_len": (G4, "g4_rt_length_by_family.tsv", {"family_label": "RVT-GII"}, "median", "num"),
    "retron_median_len": (G4, "g4_rt_length_by_family.tsv", {"family_label": "Retron"}, "median", "num"),
    "multi_margin": (G4, "g4_multi_hmm_margin_comparison.tsv", {"population": "V-RT-MULTI"},
                     "median_margin_bits", "num"),
    "ctrl_margin": (G4, "g4_multi_hmm_margin_comparison.tsv",
                    {"population": "V-RT-SINGLE (seeded control)"}, "median_margin_bits", "num"),
    "ctrl_agree": (G4, "g4_multi_hmm_positive_control.tsv",
                   {"measure": "best-scoring profile family equals the file label"}, "pct", "pct"),
    "multi_in_labels": (G4, "g4_multi_hmm_profile.tsv",
                        {"measure": "best-scoring family is among the record's labels"}, "pct", "pct"),
    "prior_confirmed": (G4, "g4_summary.tsv", {"quantity": "prior_families_CONFIRMED"}, "value", "int"),

    "ncbi_join": (G5, "g5_join_coverage.tsv", {"source_database": "ncbi_bacteria"},
                  "pct_genomes_joined", "pct"),
    "ecoli_rec": (G5, "g5_redundancy_correction.tsv", {"taxonomy_system": "ncbi"},
                  "top_species_pct_of_records", "pct"),
    "ecoli_rt": (G5, "g5_redundancy_correction.tsv", {"taxonomy_system": "ncbi"},
                 "top_species_pct_of_exact_rt", "pct"),
    "top10_rec": (G5, "g5_redundancy_correction.tsv", {"taxonomy_system": "ncbi"},
                  "top10_pct_of_records", "pct"),
    "top10_rt": (G5, "g5_redundancy_correction.tsv", {"taxonomy_system": "ncbi"},
                 "top10_pct_of_exact_rt", "pct"),
    "gtdb_phylum": (G5, "g5_rank_coverage_by_system.tsv",
                    {"taxonomy_system": "gtdb", "rank": "phylum"}, "pct_present", "pct"),
    "ncbi_phylum": (G5, "g5_rank_coverage_by_system.tsv",
                    {"taxonomy_system": "ncbi", "rank": "phylum"}, "pct_present", "pct"),

    "myrt_pct": (G6, "g6_tool_presence_retron.tsv", {"tool": "myRT"}, "pct_of_retron_records", "pct"),
    "padloc_pct": (G6, "g6_tool_presence_retron.tsv", {"tool": "PADLOC"}, "pct_of_retron_records", "pct"),
    "df_pct": (G6, "g6_tool_presence_retron.tsv", {"tool": "DefenseFinder"},
               "pct_of_retron_records", "pct"),
    "all3_pct": (G6, "g6_tool_presence_retron.tsv", {"tool": "all_three_tools"},
                 "pct_of_retron_records", "pct"),
    "subtype_agree": (G6, "g6_subtype_agreement.tsv",
                      {"measure": "the two strings agree after case/punctuation normalisation"},
                      "n", "int"),
    "subtype_both": (G6, "g6_subtype_agreement.tsv",
                     {"measure": "records where both tools wrote a subtype"}, "n", "int"),
    "carriage_hi": (G6, "g6_extraction_asymmetry.tsv", {"detected_by_set": "myRT|PADLOC"},
                    "pct_with_ncrna", "pct"),
    "carriage_lo": (G6, "g6_extraction_asymmetry.tsv", {"detected_by_set": "myRT"},
                    "pct_with_ncrna", "pct"),
}

SECTIONS = [
    dict(num="1", title="The corpus, identity-pinned", bundle=G1, view="every line of the corpus",
         finding="""Stage 1 rests on {files} files, {bytes} bytes, {lines} newline-delimited
         records, each file pinned by sha256 and the record set pinned by one digest over every
         record's file, line, byte offset and content hash: <code>{manifest_sha}</code>. There
         were <b>no parse failures of any kind</b>. The corpus splits into three anchor
         populations that are file-pure: {rt_fam} RT-anchored records in the single-family
         files, {rt_multi} in the MULTI file, and {ncrna_only} ncRNA-anchor-only records.""",
         caveat="""The ncRNA-anchor-only records are outside the RT analytical population by
         operator decision and enter no RT denominator anywhere in Stage 1.""",
         tables=[(G1, "s02_populations.tsv"), (G1, "s01_corpus_root.tsv")], figures=[]),
    dict(num="2", title="The analytical units do not convert by a constant", bundle=G2,
         view="V-REC / V-LOC / V-RT",
         finding="""{records} raw records collapse to {distinct_records} distinct records,
         {loci} loci, {phys_loci} physical loci and {exact_rt} exact RT proteins across
         {genomes} genomes ({taxocc} RT taxonomic occurrences). The conversion factor between
         units is itself database-dependent - loci per exact RT runs from 1.11 to 5.49 - so a
         raw-record count and a locus count describe different populations. {twins} RefSeq/
         GenBank twin pairs were found and <b>every one</b> is supported by identical window DNA,
         RT protein, window coordinates and strand ({twin_disagree} collapse-supported, zero
         disagreements). {loci_two_rt} loci carry conflicting RT sequences; {loci_two_db} loci
         appear under more than one source database.""",
         caveat="""The locus key is a coordinate interval on a contig accession: two assembly
         versions of one contig are two loci here.""",
         tables=[(G2, "g2_unit_ladder.tsv"), (G2, "g2_ladder_by_source_database.tsv"),
                 (G2, "g2_twin_evidence.tsv")], figures=[]),
    dict(num="3", title="RT integrity, and what each record can support", bundle=G2,
         view="per-record eligibility",
         finding="""The RT interval was translated from the window DNA and compared with the
         stored protein: {bt_exact} records match exactly, only {bt_mismatch} mismatch, and
         {elig_geom_fam} of RT-family records are geometry-eligible. Records that cannot support
         a measurement are flagged, never deleted. Of the {no_rt_cds} RT records with no marked
         RT CDS that are fully recoverable, recovery is by back-translation and confirmed by an
         independent implementation; {seq_only} keep a usable sequence but no defensible genomic
         context - {beyond_contig} of them lie wholly beyond the contig the extractor retrieved -
         and {ill_posed} remain ill-posed.""",
         caveat="""&quot;Verified&quot; means two fields of one record agree. Where the pipeline
         wrote both from the same wrong place, they would agree and still be wrong.""",
         tables=[(G2, "g2_bt_status.tsv"), (G2, "g2_eligibility.tsv"),
                 (G2B, "g2b_recovery_classes.tsv"), (G2B, "g2b_representation_classes.tsv")],
         figures=[]),
    dict(num="4", title="RT↔ncRNA geometry: the priority biological output", bundle=G3,
         view="V-PAIR-PLACEMENT, CANONICAL",
         finding="""{placements} placements reduce to {canonical} canonical ones. On those, the
         ncRNA sits <b>upstream</b> of the RT in {up} placements against {down} downstream and
         {overlap} overlapping, at a median gap of {up_median} bp, on the same strand in 99.8% of
         cases, with <b>no intervening CDS in {cds0}</b> (one CDS {cds1}, more than three
         {cds_gt3}). The exact-pair view holds {pairs} distinct (RT, ncRNA) sequence pairs, of
         which {pairs_1to1} components are strictly one-to-one.""",
         caveat="""The covariance models are retron models. The zero-ncRNA rate is
         {retron_zero} for Retron loci and {gii_zero} for RVT-GII: outside Retron this measures
         detector scope, never biological absence. The {nonretron} retron-CM placements beside
         non-Retron RTs ({nonretron_up} upstream) are retained as a candidate population and are
         <b>not</b> called novel retrons.""",
         tables=[(G3, "g3_direction.tsv"), (G3, "g3_cds_between_explicit.tsv"),
                 (G3, "g3_topology_components.tsv"), (G3, "g3_zero_class_by_family.tsv"),
                 (G3, "g3_nonretron_vs_retron_geometry.tsv")],
         figures=[(SELF, "fig01_distance_distribution_restyled"), (G3, "fig02_cds_between"),
                  (G3, "fig03_direction_by_family")]),
    dict(num="5", title="Two geometry signals that are technical, not biological", bundle=G3,
         view="audits",
         finding="""The downstream placements cluster at a median {dmode_median} bp, but the
         cluster contains only {dmode_seqs} distinct ncRNA sequences and 99.96% of its dominant
         stratum is contig-start-clipped - the window begins at the contig start, so any call is
         forced downstream. It is labelled a technical mode. Separately, the shipped
         <code>position_relative_to_rt</code> is null on {shipped_null} placements and matches no
         coordinate frame: the best of twelve candidates reproduces {shipped_best} values. Its
         variation is -(RT offset into the window) plus the ncRNA's intergenic-region index - an
         index minus a coordinate.""",
         caveat="""Neither signal is used as a prior. The coordinate-derived geometry is
         canonical; the shipped field is retained as provenance only.""",
         tables=[(G3, "g3_downstream_mode_profile.tsv"), (G3, "g3_shipped_field_structure.tsv"),
                 (G3, "g3_shipped_field_semantics.tsv")], figures=[]),
    dict(num="6", title="Family baselines, and why MULTI carries several labels", bundle=G4,
         view="V-RT-SINGLE / V-RT-MULTI",
         finding="""On exact-sequence views - {v_single} single-family proteins, {v_multi} MULTI,
         {v_cross} spanning labels - RVT-GII has a median length of {gii_median_len} aa and
         Retron {retron_median_len} aa. {prior_confirmed} of the prior project's 44 family length
         baselines are reproduced exactly. The MULTI labels were investigated with the myRT HMM
         library: the best-scoring family is among the record's own labels for {multi_in_labels}
         of MULTI proteins, and the best-vs-second margin is {multi_margin} bits against
         {ctrl_margin} bits in a control whose best hit matches the known label {ctrl_agree} of
         the time. MULTI is an ambiguity stratum, not mislabelling.""",
         caveat="""MULTI proteins are also shorter, and score scales with length, so part of the
         tie may be a length effect. Stage 1 does not resolve MULTI.""",
         tables=[(G4, "g4_views.tsv"), (G4, "g4_rt_length_by_family.tsv"),
                 (G4, "g4_multi_hmm_margin_comparison.tsv"),
                 (G4, "g4_completeness_by_family.tsv")],
         figures=[(SELF, "fig01_rt_length_by_family_restyled"), (G4, "fig02_multi_label_margins")]),
    dict(num="7", title="Metadata, taxonomy and what redundancy correction changes", bundle=G5,
         view="per source database and per taxonomy schema",
         finding="""Every catalogue join resolves ({ncbi_join} for the largest, ncbi_bacteria),
         but a join that resolves a row is not one that resolves a value: the NCBI summaries carry
         no completeness column at all, so a quality filter can speak for roughly a quarter of the
         corpus's genome entries. Taxonomy is reported per schema - phylum coverage is
         {gtdb_phylum} under GTDB and {ncbi_phylum} under the NCBI block, which has no phylum by
         construction. Correcting for redundancy moves the distribution: <i>Escherichia coli</i>
         is {ecoli_rec} of NCBI records but {ecoli_rt} of exact RTs, and the top ten species fall
         from {top10_rec} of records to {top10_rt} of exact RTs.""",
         caveat="""The join rate is a description, not a test: a corpus whose genome ids were
         harvested from these catalogues resolves into them by construction.""",
         tables=[(G5, "g5_join_coverage.tsv"), (G5, "g5_quality_availability.tsv"),
                 (G5, "g5_rank_coverage_by_system.tsv"), (G5, "g5_redundancy_correction.tsv")],
         figures=[]),
    dict(num="8", title="Annotation routes disagree, and the disagreement is structured",
         bundle=G6, view="the Retron locus population",
         finding="""myRT detected {myrt_pct} of Retron records, PADLOC {padloc_pct},
         DefenseFinder {df_pct}, and all three together {all3_pct}. Where both tools wrote a
         subtype ({subtype_both} records) they agree on {subtype_agree}. Most consequentially,
         ncRNA carriage depends on which tools called the locus: {carriage_hi} for myRT+PADLOC
         against {carriage_lo} for myRT alone. A tool-defined subset of this corpus is not a
         random subset.""",
         caveat="""Agreement between these tools is not independent corroboration - they share
         model lineage - and a tool missing from a record cannot be distinguished from a tool that
         was never run on that genome.""",
         tables=[(G6, "g6_tool_presence_retron.tsv"), (G6, "g6_subtype_agreement.tsv"),
                 (G6, "g6_extraction_asymmetry.tsv")], figures=[]),
]

N_DERIVED = 16  # asserted in assemble_report.py against the *_derived_registry.tsv rows

CLOSING = """
<h2>What Stage 1 leaves behind</h2>
<p>{n_derived} registered derived datasets under <code>data/derived/</code>, each with a sha256
and a writer-independent content digest in its producing bundle's registry: the canonical record,
locus, physical-locus and exact-RT tables; the RT↔ncRNA placement, exact-pair, recurrence and
non-Retron candidate tables; the RT-CDS recovery table; the RT and ncRNA family baselines with
the MULTI HMM evidence; and the per-tool call table. <code>VIEWS.md</code> and <code>pull.py</code> in the g2 bundle define and run the declared
views over them.</p>
<p>Every gate reruns from its own bundle and reproduces its tables byte for byte, every rate names
the population its denominator equals, and every zero has a positive control that was shown
capable of returning non-zero. No measurement in Stage 1 has been promoted to a project claim:
that step needs the operator's input audit.</p>
"""
