#!/usr/bin/env python3
"""findings - the report's prose, and the declared lookup for every number in it.

Each VALUES entry is a five-tuple (table, exact row selector, column, format), resolved by
assemble_report.py out of this bundle's landed tables/. A selector matching anything other than
exactly one row fails the build, and a {placeholder} with no declared lookup fails the build.

The prose is the interpretation layer. Every finding follows REPORTING_STANDARDS: what is
measured, on which unit, against which denominator, what it means (PROPOSED:), whether it is
biological / technical / unresolved, and the caveat that would falsify or weaken it.
"""
from __future__ import annotations

TITLE = "The canonical bacterial RT/retron catalogue: an extended Stage-1 characterisation"
SUBTITLE = ("A scientific synthesis over the landed Stage-1 measurement bundles (g1–g7) and the "
            "registered canonical datasets. It computes no new measurement of record: every "
            "number is a view over landed Stage-1 data, and every re-derivation is reconciled "
            "against the value its gate landed.")

# ---------------------------------------------------------------- declared value lookups
# key: (table, {column: value} selector, column, format)
VALUES = {
    # --- section 1
    "n_raw": ("t01_unit_funnel", {"step": "raw record"}, "n", "int"),
    "n_distinct": ("t01_unit_funnel", {"step": "distinct record"}, "n", "int"),
    "n_loci": ("t01_unit_funnel", {"step": "locus"}, "n", "int"),
    "n_phys": ("t01_unit_funnel", {"step": "physical locus"}, "n", "int"),
    "n_exact": ("t01_unit_funnel", {"step": "exact RT"}, "n", "int"),
    "pct_exact_of_raw": ("t01_unit_funnel", {"step": "exact RT"}, "pct_of_raw_records", "pct"),
    "collapse": ("t01_unit_funnel", {"step": "exact RT"}, "cumulative_collapse_factor", "num"),
    "n_twins": ("t01_unit_funnel", {"step": "physical locus"}, "n_removed", "int"),
    "n_dupe_lines": ("t01_unit_funnel", {"step": "distinct record"}, "n_removed", "int"),
    "n_remined": ("t01_unit_funnel", {"step": "locus"}, "n_removed", "int"),
    "n_genomes": ("t01_other_units", {"unit_name": "genome"}, "n", "int"),
    "lpe_ncbi": ("t02_ladder_by_database", {"source_database": "ncbi_bacteria"},
                 "loci_per_exact_rt", "num"),
    "lpe_soil": ("t02_ladder_by_database", {"source_database": "mgnify_soil"},
                 "loci_per_exact_rt", "num"),
    "shared_ncbi_gtdb": ("t02_exact_rt_database_upset",
                         {"membership": "ncbi_bacteria|gtdb_bacteria"}, "n_exact_rt", "int"),
    "only_ncbi": ("t02_exact_rt_database_upset", {"membership": "ncbi_bacteria"},
                  "n_exact_rt", "int"),
    "gii_top1pct": ("t03_recurrence_concentration",
                    {"family": "RVT-GII", "top_fraction_of_exact_rt": "0.01"},
                    "pct_of_physical_loci", "pct"),
    "retron_top1pct": ("t03_recurrence_concentration",
                       {"family": "Retron", "top_fraction_of_exact_rt": "0.01"},
                       "pct_of_physical_loci", "pct"),
    # --- section 2
    "gii_records_pct": ("t04_family_share_by_unit", {"family": "RVT-GII"}, "pct_records", "pct"),
    "gii_exact_pct": ("t04_family_share_by_unit", {"family": "RVT-GII"}, "pct_exact_rt", "pct"),
    "dgr_shift": ("t04_family_share_by_unit", {"family": "RVT-DGRs"},
                  "shift_records_to_exact_rt", "num"),
    "retron_shift": ("t04_family_share_by_unit", {"family": "Retron"},
                     "shift_records_to_exact_rt", "num"),
    "multi_exact": ("t04_family_share_by_unit", {"family": "MULTI"}, "n_exact_rt", "int"),
    # --- section 3
    "gii_median_len": ("t07_rt_length_quantiles",
                       {"family": "RVT-GII", "completeness_class": "ALL"}, "median", "num"),
    "retron_median_len": ("t07_rt_length_quantiles",
                          {"family": "Retron", "completeness_class": "ALL"}, "median", "num"),
    "retron_complete_median": ("t07_rt_length_quantiles",
                               {"family": "Retron", "completeness_class": "all_complete"},
                               "median", "num"),
    "retron_partial_median": ("t07_rt_length_quantiles",
                              {"family": "Retron", "completeness_class": "all_partial"},
                              "median", "num"),
    "crispr_modes": ("t08_rt_length_shape", {"family": "RVT-CRISPR"}, "n_modes_declared_rule",
                     "int"),
    "gii_modes": ("t08_rt_length_shape", {"family": "RVT-GII"}, "n_modes_declared_rule", "int"),
    # --- section 4
    "n_exact_ncrna_ia": ("t09_ncrna_length_by_model", {"detection_model": "TypeIA_IIAI"},
                         "n_exact_ncrna", "int"),
    "len_ia": ("t09_ncrna_length_by_model", {"detection_model": "TypeIA_IIAI"}, "median", "num"),
    "len_iv": ("t09_ncrna_length_by_model", {"detection_model": "TypeIV"}, "median", "num"),
    "len_iiia3": ("t09_ncrna_length_by_model", {"detection_model": "TypeIIIA3"}, "median", "num"),
    "ia_pct_placements": ("t10_model_composition_by_unit", {"detection_model": "TypeIA_IIAI"},
                          "pct_placements", "pct"),
    "ia_pct_ncrna": ("t10_model_composition_by_unit", {"detection_model": "TypeIA_IIAI"},
                     "pct_exact_ncrna", "pct"),
    "outgroupa_pct_ncrna": ("t10_model_composition_by_unit", {"detection_model": "OutgroupA"},
                            "pct_exact_ncrna", "pct"),
    "outgroupa_pct_placements": ("t10_model_composition_by_unit", {"detection_model": "OutgroupA"},
                                 "pct_placements", "pct"),
    "struct_ia": ("t11_structure_annotation_by_model", {"detection_model": "TypeIA_IIAI"},
                  "pct_with_structure", "pct"),
    # --- section 5
    "n_canonical": ("t12_configuration_classes",
                    {"config_class": "upstream, adjacent (0 CDS, ≤500 bp)"},
                    "n_placements_total", "int"),
    "adj_n": ("t12_configuration_classes",
              {"config_class": "upstream, adjacent (0 CDS, ≤500 bp)"}, "n_placements", "int"),
    "adj_pct": ("t12_configuration_classes",
                {"config_class": "upstream, adjacent (0 CDS, ≤500 bp)"},
                "pct_placements", "pct"),
    "adj_pairs": ("t12_configuration_classes",
                  {"config_class": "upstream, adjacent (0 CDS, ≤500 bp)"},
                  "n_exact_pairs", "int"),
    "long_n": ("t12_configuration_classes",
               {"config_class": "upstream, long intergenic gap (0 CDS, >500 bp)"},
               "n_placements", "int"),
    "long_pct": ("t12_configuration_classes",
                 {"config_class": "upstream, long intergenic gap (0 CDS, >500 bp)"},
                 "pct_placements", "pct"),
    "long_pairs": ("t12_configuration_classes",
                   {"config_class": "upstream, long intergenic gap (0 CDS, >500 bp)"},
                   "n_exact_pairs", "int"),
    "long_species": ("t12_configuration_classes",
                     {"config_class": "upstream, long intergenic gap (0 CDS, >500 bp)"},
                     "n_species", "int"),
    "onecds_n": ("t12_configuration_classes", {"config_class": "upstream, one intervening CDS"},
                 "n_placements", "int"),
    "onecds_pct": ("t12_configuration_classes", {"config_class": "upstream, one intervening CDS"},
                   "pct_placements", "pct"),
    "ovl_rt_n": ("t12_configuration_classes", {"config_class": "overlapping the RT CDS"},
                 "n_placements", "int"),
    "ovl_rt_pct": ("t12_configuration_classes", {"config_class": "overlapping the RT CDS"},
                   "pct_placements", "pct"),
    "tech_n": ("t12_configuration_classes",
               {"config_class": "downstream: technical clipped mode"}, "n_placements", "int"),
    "tech_pct": ("t12_configuration_classes",
                 {"config_class": "downstream: technical clipped mode"}, "pct_placements", "pct"),
    "tech_ncrna": ("t12_configuration_classes",
                   {"config_class": "downstream: technical clipped mode"}, "n_exact_ncrna", "int"),
    "tech_species": ("t12_configuration_classes",
                     {"config_class": "downstream: technical clipped mode"}, "n_species", "int"),
    "dn_other_n": ("t12_configuration_classes", {"config_class": "downstream: other"},
                   "n_placements", "int"),
    "opp_strand": ("t12_configuration_flags", {"flag": "opposite strand to the RT"},
                   "n_placements", "int"),
    "opp_strand_pct": ("t12_configuration_flags", {"flag": "opposite strand to the RT"},
                       "pct_of_canonical", "pct"),
    "band_placements": ("t14_gap_mode_composition",
                        {"measure": "canonical placements in the 900-1,100 bp upstream band"},
                        "value", "int"),
    "band_rts": ("t14_gap_mode_composition",
                 {"measure": "distinct exact RTs in the band"}, "value", "int"),
    "band_top_rt": ("t14_gap_mode_composition",
                    {"measure": "placements contributed by the single most recurrent exact RT"},
                    "value", "int"),
    "band_top_species_n": ("t14_gap_mode_composition",
                           {"measure": "placements contributed by the most frequent species"},
                           "value", "int"),
    "band_species_name": ("t14_gap_mode_composition",
                          {"measure": "distinct exact RTs in the band"}, "top_species", "str"),
    "cds0_placement": ("t15_cds_between_by_unit",
                       {"view_unit": "placement", "n_cds_between": "0"}, "pct", "pct"),
    "cds1_placement": ("t15_cds_between_by_unit",
                       {"view_unit": "placement", "n_cds_between": "1"}, "pct", "pct"),
    "same_strand_up": ("t15_strand_and_overlap", {"direction": "upstream"},
                       "pct_same_strand", "pct"),
    "ia_median_dist": ("t16_geometry_by_model", {"detection_model": "TypeIA_IIAI"},
                       "median_signed_distance_bp", "num"),
    "ic1_median_dist": ("t16_geometry_by_model", {"detection_model": "TypeIC1_IC2"},
                        "median_signed_distance_bp", "num"),
    "typev_tech_pct": ("t16_geometry_by_model", {"detection_model": "TypeV"},
                       "pct_in_technical_mode", "pct"),
    "xiiia_median_dist": ("t16_geometry_by_model", {"detection_model": "TypeXIIIA_firmi"},
                          "median_signed_distance_bp", "num"),
    # --- section 6
    "combo3_n": ("t18_tool_combination_carriage",
                 {"view_unit": "physical locus (union of its records' tools)",
                  "combo": "myRT|PADLOC|DefenseFinder"}, "n", "int"),
    "combo3_pct": ("t18_tool_combination_carriage",
                   {"view_unit": "physical locus (union of its records' tools)",
                    "combo": "myRT|PADLOC|DefenseFinder"}, "pct_with_ncrna", "pct"),
    "myrt_only_pct": ("t18_tool_combination_carriage",
                      {"view_unit": "physical locus (union of its records' tools)",
                       "combo": "myRT"}, "pct_with_ncrna", "pct"),
    "myrt_padloc_pct": ("t18_tool_combination_carriage",
                        {"view_unit": "physical locus (union of its records' tools)",
                         "combo": "myRT|PADLOC"}, "pct_with_ncrna", "pct"),
    "myrt_padloc_n": ("t18_tool_combination_carriage",
                      {"view_unit": "physical locus (union of its records' tools)",
                       "combo": "myRT|PADLOC"}, "n", "int"),
    "combo3_exact_pct": ("t18_tool_combination_carriage",
                         {"view_unit": "exact RT (non-exclusive across combinations)",
                          "combo": "myRT|PADLOC|DefenseFinder"}, "pct_with_ncrna", "pct"),
    "combo_disagree": ("t18_combo_disagreement",
                       {"measure": "Retron physical loci whose records disagree on the tool "
                                   "combination"}, "n", "int"),
    "iia_3tool": ("t20_combo_by_padloc_subtype",
                  {"combo": "myRT|PADLOC|DefenseFinder", "label": "retron_II-A"},
                  "pct_with_ncrna", "pct"),
    "iia_myrt_padloc": ("t20_combo_by_padloc_subtype",
                        {"combo": "myRT|PADLOC", "label": "retron_II-A"}, "pct_with_ncrna", "pct"),
    "iiia_3tool": ("t20_combo_by_padloc_subtype",
                   {"combo": "myRT|PADLOC|DefenseFinder", "label": "retron_III-A"},
                   "pct_with_ncrna", "pct"),
    # --- section 7
    "ec107_pct": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_Ec107-like"},
                  "pct_with_ncrna", "pct"),
    "ec107_n": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_Ec107-like"},
                "n_loci", "int"),
    "xii_pct": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_XII"},
                "pct_with_ncrna", "pct"),
    "xii_n": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_XII"},
              "n_loci", "int"),
    "vi_pct": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_VI"},
               "pct_with_ncrna", "pct"),
    "vi_n": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_VI"}, "n_loci", "int"),
    "iiia_pct": ("t21_carriage_by_subtype", {"tool": "PADLOC", "label": "retron_III-A"},
                 "pct_with_ncrna", "pct"),
    "zero_ncbi": ("t23_zero_call_by_database", {"source_database_set": "ncbi_bacteria"},
                  "pct_zero", "pct"),
    "zero_ncbi_n": ("t23_zero_call_by_database", {"source_database_set": "ncbi_bacteria"},
                    "n_loci", "int"),
    "twin_double": ("t23_zero_call_by_database",
                    {"source_database_set": "ncbi_bacteria|gtdb_bacteria"},
                    "n_loci_with_2plus_placements", "int"),
    "two_seq_ncbi": ("t23_zero_call_by_database", {"source_database_set": "ncbi_bacteria"},
                     "n_2", "int"),
    "ctx_zero": ("t24_carriage_by_upstream_context",
                 {"upstream_context_bin": "0", "upstream_side_clipped": "True"},
                 "pct_with_ncrna", "pct"),
    "ctx_zero_n": ("t24_carriage_by_upstream_context",
                   {"upstream_context_bin": "0", "upstream_side_clipped": "True"},
                   "n_loci", "int"),
    "ctx_full": ("t24_carriage_by_upstream_context",
                 {"upstream_context_bin": ">9,000", "upstream_side_clipped": "False"},
                 "pct_with_ncrna", "pct"),
    "ctx_full_n": ("t24_carriage_by_upstream_context",
                   {"upstream_context_bin": ">9,000", "upstream_side_clipped": "False"},
                   "n_loci", "int"),
    "ctx_200": ("t24_carriage_by_upstream_context",
                {"upstream_context_bin": "1-200", "upstream_side_clipped": "True"},
                "pct_with_ncrna", "pct"),
    "rt_zero_retron": ("t23_zero_call_by_family", {"family_label_set": "Retron"},
                       "pct_zero", "pct"),
    "rt_zero_gii": ("t23_zero_call_by_family", {"family_label_set": "RVT-GII"}, "pct_zero", "pct"),
    # --- section 8
    "n_pairs": ("t29_recurrence_classes", {"recurrence_class": "single_placement"},
                "n_exact_pairs", "int"),
    "pairs_1to1": ("t28_topology_components", {"shape": "1:1"}, "n_components", "int"),
    "pairs_many1": ("t28_topology_components", {"shape": "many:1"}, "n_components", "int"),
    "pairs_manymany": ("t28_topology_components", {"shape": "many:many"}, "n_components", "int"),
    "rec_redeposit_pairs": ("t29_recurrence_classes",
                            {"recurrence_class": "one_physical_locus_multiple_database_copies"},
                            "pct_of_exact_pairs", "pct"),
    "rec_species_pairs": ("t29_recurrence_classes", {"recurrence_class": "multiple_species"},
                          "pct_of_exact_pairs", "pct"),
    "rec_species_placements": ("t29_recurrence_classes",
                               {"recurrence_class": "multiple_species"},
                               "pct_of_placements", "pct"),
    "dom100": ("t30_partner_consistency", {"recurrence_bin": ">=100"},
               "pct_dominant_ge_90", "pct"),
    "dom100_n": ("t30_partner_consistency", {"recurrence_bin": ">=100"}, "n_exact_rt", "int"),
    "single_model100": ("t30_partner_consistency", {"recurrence_bin": ">=100"},
                        "pct_single_model", "pct"),
    "multi_partner_single_model": ("t30_partner_sequence_vs_family",
                                   {"measure": "of those, all partners called by ONE covariance "
                                               "model"}, "pct", "pct"),
    # --- section 9
    "cand_n": ("t31_candidates_vs_retron",
               {"population": "non-Retron retron-CM candidates (single-family)"},
               "n_placements", "int"),
    "cand_up": ("t31_candidates_vs_retron",
                {"population": "non-Retron retron-CM candidates (single-family)"},
                "pct_upstream", "pct"),
    "cand_env": ("t31_candidates_vs_retron",
                 {"population": "non-Retron retron-CM candidates (single-family)"},
                 "pct_in_retron_envelope", "pct"),
    "retron_env": ("t31_candidates_vs_retron", {"population": "CANONICAL Retron placements"},
                   "pct_in_retron_envelope", "pct"),
    "cand_dist": ("t31_candidates_vs_retron",
                  {"population": "non-Retron retron-CM candidates (single-family)"},
                  "median_abs_distance_bp", "num"),
    "retron_dist": ("t31_candidates_vs_retron", {"population": "CANONICAL Retron placements"},
                    "median_abs_distance_bp", "num"),
    # --- section 10
    "multi_n": ("t32_margin_comparison", {"population": "V-RT-MULTI"}, "n_exact_rt", "int"),
    "multi_margin": ("t32_margin_comparison", {"population": "V-RT-MULTI"},
                     "median_margin_bits", "num"),
    "ctrl_margin": ("t32_margin_comparison", {"population": "V-RT-SINGLE (seeded control)"},
                    "median_margin_bits", "num"),
    "multi_below10": ("t32_margin_comparison", {"population": "V-RT-MULTI"},
                      "pct_margin_below_10_bits", "pct"),
    "ctrl_below10": ("t32_margin_comparison", {"population": "V-RT-SINGLE (seeded control)"},
                     "pct_margin_below_10_bits", "pct"),
    "multi_best_in_labels": ("t32_multi_profile",
                             {"measure": "best-scoring family is among the record's labels"},
                             "pct", "pct"),
    "crispr_gii_pairs": ("t33_multi_family_pairs",
                         {"family_a": "RVT-CRISPR", "family_b": "RVT-GII"}, "n_exact_rt", "int"),
    "multi_ncrna_pct": ("t33_multi_architecture", {"population": "MULTI records"},
                        "pct_with_ncrna_call", "pct"),
    "single_ncrna_pct": ("t33_multi_architecture", {"population": "single-family records"},
                         "pct_with_ncrna_call", "pct"),
    "multi_elig": ("t33_multi_architecture", {"population": "MULTI records"},
                   "pct_geometry_eligible", "pct"),
    "single_elig": ("t33_multi_architecture", {"population": "single-family records"},
                    "pct_geometry_eligible", "pct"),
    # --- section 11
    "pseudo_prev": ("t34_gtdb_prevalence_by_rank",
                    {"rank": "phylum", "taxon": "Pseudomonadota"}, "prevalence_pct", "pct"),
    "pseudo_sampled": ("t34_gtdb_prevalence_by_rank",
                       {"rank": "phylum", "taxon": "Pseudomonadota"}, "n_sampled_genomes", "int"),
    "actino_prev": ("t34_gtdb_prevalence_by_rank",
                    {"rank": "phylum", "taxon": "Actinomycetota"}, "prevalence_pct", "pct"),
    "cyano_prev": ("t34_gtdb_prevalence_by_rank",
                   {"rank": "phylum", "taxon": "Cyanobacteriota"}, "prevalence_pct", "pct"),
    "cyano_per_genome": ("t34_gtdb_prevalence_by_rank",
                         {"rank": "phylum", "taxon": "Cyanobacteriota"},
                         "exact_rt_per_positive_genome", "num"),
    "chlamydia_prev": ("t34_gtdb_prevalence_by_rank",
                       {"rank": "phylum", "taxon": "Chlamydiota"}, "prevalence_pct", "pct"),
    "pelagi_prev": ("t34_gtdb_prevalence_by_rank",
                    {"rank": "genus", "taxon": "Pelagibacter"}, "prevalence_pct", "pct"),
    "pelagi_n": ("t34_gtdb_prevalence_by_rank",
                 {"rank": "genus", "taxon": "Pelagibacter"}, "n_sampled_genomes", "int"),
    "kleb_prev": ("t34_gtdb_prevalence_by_rank",
                  {"rank": "genus", "taxon": "Klebsiella"}, "prevalence_pct", "pct"),
    "kleb_n": ("t34_gtdb_prevalence_by_rank",
               {"rank": "genus", "taxon": "Klebsiella"}, "n_sampled_genomes", "int"),
    "ecoli_records_pct": ("t36_ncbi_genus_representation", {"tax_genus": "Escherichia"},
                          "pct_of_records", "pct"),
    "ecoli_exact_pct": ("t36_ncbi_genus_representation", {"tax_genus": "Escherichia"},
                        "pct_of_exact_rt", "pct"),
    "salm_per_exact": ("t36_ncbi_genus_representation", {"tax_genus": "Salmonella"},
                       "records_per_exact_rt", "num"),
    # --- section 12
    "insp_full": ("t40_inspectability",
                  {"inspectability_tier": "fully inspectable (exact back-translation, RT CDS "
                                          "present, window not clipped or edge-touching)"},
                  "pct_of_distinct_records", "pct"),
    "insp_clipped": ("t40_inspectability",
                     {"inspectability_tier": "geometry-eligible, context clipped or RT at a "
                                             "window edge"}, "pct_of_distinct_records", "pct"),
    "insp_recoded": ("t40_inspectability",
                     {"inspectability_tier": "geometry-eligible, translation recoded (alt start "
                                             "/ table 4 / masked stop)"},
                     "pct_of_distinct_records", "pct"),
    "insp_seqonly": ("t40_inspectability",
                     {"inspectability_tier": "sequence only - no defensible genomic context"},
                     "n_records", "int"),
    "insp_illposed": ("t40_inspectability",
                      {"inspectability_tier": "ill-posed - back-translation mismatch"},
                      "n_records", "int"),
    "clip_ncbi": ("t39_context_truncation_by_database", {"source_database": "ncbi_bacteria"},
                  "pct_true_start_clipped", "pct"),
    "mag_recovered": ("t39_no_rt_cds_recovery_by_database",
                      {"source_database": "mgnify_human_gut", "recovery_state": "RECOVERED"},
                      "n_records", "int"),
    # --- section 13
    "len300_carriage": ("t25_carriage_by_rt_length",
                        {"length_bin": "300-349", "completeness_class": "all_complete"},
                        "pct_with_ncrna", "pct"),
    "len_short_carriage": ("t25_carriage_by_rt_length",
                           {"length_bin": "<200", "completeness_class": "all_partial"},
                           "pct_with_ncrna", "pct"),
    "breadth_one_species": ("t38_recurrence_breadth",
                            {"family": "Retron",
                             "breadth_class": "one species (database duplication or clonal)"},
                            "pct_of_family_high_recurrence", "pct"),
    "breadth_broad": ("t38_recurrence_breadth",
                      {"family": "Retron", "breadth_class": ">5 species"},
                      "pct_of_family_high_recurrence", "pct"),
    "gut_myrt_only": ("t26_tool_mix_by_database",
                      {"source_database_set": "mgnify_human_gut", "combo": "myRT"},
                      "pct_of_database_loci", "pct"),
    "ncbi_3tool_share": ("t26_tool_mix_by_database",
                         {"source_database_set": "ncbi_bacteria",
                          "combo": "myRT|PADLOC|DefenseFinder"}, "pct_of_database_loci", "pct"),
    # --- checks
    "n_reconciled": ("t41_reconciliation", {"quantity": "CANONICAL placements"},
                     "landed_value", "int"),
    "cds_recount_agree": ("t43_independent_cds_recount", {"field": "n_cds_between"},
                          "pct_agree", "pct"),
    "cds_recount_n": ("t43_independent_cds_recount", {"field": "n_cds_between"},
                      "n_compared", "int"),
}

# ---------------------------------------------------------------- the report
# Each section: id, title, view (unit/denominator line), figures, prose blocks, tables, caveat.
SECTIONS = [
    dict(
        id="1", title="Corpus and redundancy structure",
        view="units: raw record → distinct record → locus → physical locus → exact RT · "
             "denominator: the RT-anchored population of the g1 corpus pin",
        figures=["fig01_unit_funnel", "fig02_database_structure", "fig03_exact_rt_recurrence"],
        tables=["t01_unit_funnel", "t02_ladder_by_database", "t02_exact_rt_database_upset",
                "t03_recurrence_concentration"],
        prose=[
            ("What is measured", "The catalogue's {n_raw} raw RT-anchored records collapse to "
             "{n_distinct} distinct records, {n_loci} loci, {n_phys} physical loci and "
             "{n_exact} exact RT proteins across {n_genomes} genomes. The last step is the "
             "large one: {pct_exact_of_raw} of the raw records survive as distinct proteins, a "
             "{collapse}-fold collapse. Only {n_dupe_lines} records are literal duplicate lines; "
             "{n_remined} are the same locus re-mined from a second database and {n_twins} are "
             "RefSeq/GenBank twins of one physical locus."),
            ("Principal observation", "The collapse factor is not a constant of the corpus but a "
             "property of each database: {lpe_ncbi} loci per exact RT in ncbi_bacteria against "
             "{lpe_soil} in mgnify_soil. Redundancy is also concentrated within families — the "
             "most re-deposited 1% of RVT-GII proteins account for {gii_top1pct} of that family's "
             "physical loci, and for Retron {retron_top1pct}."),
            ("PROPOSED: reading", "**Technical, not biological.** The dominant signal in raw "
             "record counts is deposition practice: which catalogue a genome was submitted to, "
             "and how many near-identical genomes of a heavily sequenced species exist. Any "
             "statement about how common an RT is must name its unit; at the record unit it is "
             "largely a statement about sequencing effort."),
            ("Would be wrong if", "the exact-RT key were collapsing genuinely different proteins. "
             "It cannot: it is the sha256 of the amino-acid sequence, and g2 verified that 0 loci "
             "carry conflicting RT sequences. The opposite error — one protein split across two "
             "keys by a single residue — remains possible and would make the collapse factor an "
             "underestimate."),
        ],
        caveat="A physical locus is a coordinate interval on a normalised contig accession. Two "
               "assembly versions of one contig remain two loci, so the twin collapse is a lower "
               "bound on deposition redundancy.",
    ),
    dict(
        id="2", title="RT-family composition, and what the unit does to it",
        view="unit: exact RT sequences, with loci and records shown beside them · denominator: "
             "all RT-anchored units of that level",
        figures=["fig04_family_share_by_unit", "fig06_family_ranked",
                 "fig05_database_family_heatmap"],
        tables=["t04_family_share_by_unit", "t06_family_ranked",
                "t05_database_family_composition"],
        prose=[
            ("What is measured", "Family share at four units. RVT-GII is {gii_records_pct} of raw "
             "records but {gii_exact_pct} of exact RT proteins. The families move in opposite "
             "directions: RVT-DGRs gains {dgr_shift}× share when counted on proteins rather than "
             "records, Retron loses ({retron_shift}×)."),
            ("Principal observation", "Ranking families by raw records and by distinct proteins "
             "gives materially different pictures of the catalogue. The MULTI stratum "
             "({multi_exact} exact RTs) is kept as its own bar throughout and never merged into a "
             "family."),
            ("PROPOSED: reading", "**Technical.** The families that shrink are those sampled from "
             "heavily re-sequenced clinical genera; the families that grow are those found once "
             "per genome in diverse hosts. This is the C1/C2 evidence in one figure: the same "
             "catalogue supports two different family rankings depending on the declared unit."),
            ("Would be wrong if", "family labels were unstable across records of one protein. "
             "g2 flags the 20 multi-label records inside single-family files and g4 keeps the 12 "
             "V-RT-CROSS proteins out of every family; both are excluded from the single-family "
             "view rather than silently assigned."),
        ],
        caveat="'other' pools 29 small families for the figure only; the table carries every "
               "family separately.",
    ),
    dict(
        id="3", title="RT length",
        view="unit: exact RT sequences (V-RT-SINGLE; MULTI separate) · denominator: exact RTs of "
             "that family and Prodigal completeness class",
        figures=["fig07_rt_length_violins", "fig08_rt_length_ecdf"],
        tables=["t07_rt_length_quantiles", "t08_rt_length_shape"],
        prose=[
            ("What is measured", "Length distributions per family, split by whether Prodigal "
             "called the ORF complete or partial. RVT-GII has a median of {gii_median_len} aa and "
             "Retron {retron_median_len} aa; within Retron, complete ORFs run "
             "{retron_complete_median} aa against {retron_partial_median} aa for partial ones."),
            ("Principal observation", "Several families are not unimodal under the declared "
             "mode-counting rule: RVT-CRISPR resolves into {crispr_modes} modes and RVT-GII into "
             "{gii_modes}. The partial class is shifted low in every family, which is what a "
             "truncation flag should do."),
            ("PROPOSED: reading", "**Mixed.** The complete/partial split is technical and behaves "
             "as expected. The multimodality of RVT-CRISPR and RVT-GII survives that split and is "
             "a candidate for domain-architecture heterogeneity — but Stage 1 measures length, "
             "not domains, and the launcher puts domain analysis out of scope."),
            ("Would be wrong if", "the mode rule were finding noise. It is declared in advance, "
             "smooths at 10 aa, requires a peak to reach 10% of the maximum and a valley below "
             "60% of the lower peak, and a control shows it returns 2 on a constructed bimodal "
             "sample and 1 on a unimodal one."),
        ],
        caveat="A missing Prodigal flag is 'no completeness evidence', never 'partial' (g4); "
               "those RTs and the 'mixed' class are in the table but not drawn.",
    ),
    dict(
        id="4", title="ncRNA length and covariance-model composition",
        view="unit: exact ncRNA sequences and CANONICAL placements · denominator: as named per "
             "panel",
        figures=["fig09_ncrna_length_by_model", "fig10_model_composition_by_unit",
                 "fig11_subtype_by_model"],
        tables=["t09_ncrna_length_by_model", "t10_model_composition_by_unit",
                "t11_subtype_by_model", "t11_structure_annotation_by_model"],
        prose=[
            ("What is measured", "Length and usage of the 21 retron covariance models. Median "
             "lengths run from {len_iv} nt (TypeIV) to {len_iiia3} nt (TypeIIIA3); TypeIA_IIAI, "
             "the most-used model, calls {n_exact_ncrna_ia} distinct sequences at a median "
             "{len_ia} nt."),
            ("Principal observation", "Model composition changes with the unit exactly as family "
             "composition does: TypeIA_IIAI is {ia_pct_placements} of placements but only "
             "{ia_pct_ncrna} of distinct ncRNA sequences, while OutgroupA is "
             "{outgroupa_pct_placements} of placements and {outgroupa_pct_ncrna} of sequences. "
             "The subtype × model heatmaps are close to diagonal: each tool's subtype label "
             "corresponds to one model, which is what shared model lineage predicts."),
            ("PROPOSED: reading", "**Technical.** The placement-level dominance of TypeIA_IIAI is "
             "re-deposition (§5), not diversity. The near-diagonal subtype × model structure means "
             "'which subtype' and 'which CM' are close to the same variable, and neither can be "
             "used to validate the other."),
            ("Would be wrong if", "one ncRNA sequence were called by several models — it would "
             "break the diagonal reading. g3 measured this: 0 of 16,458 exact ncRNA sequences are "
             "called by more than one model, which is imposed by the pipeline's winner-take-all "
             "model selection and is therefore not evidence about model specificity."),
        ],
        caveat="Structure annotation is sparse and uneven across models ({struct_ia} of "
               "TypeIA_IIAI sequences carry one). Missing structure annotation is a missing "
               "field, never evidence that no structure exists.",
    ),
    dict(
        id="5", title="RT↔ncRNA genomic geometry",
        view="unit: CANONICAL placements, the same placements re-counted as physical loci and as "
             "exact pairs · denominator: all CANONICAL placements ({n_canonical})",
        figures=["fig12_configuration_schematic", "fig13_signed_distance",
                 "fig14_abs_distance_and_mode", "fig15_cds_strand_overlap",
                 "fig16_geometry_by_model"],
        tables=["t12_configuration_classes", "t14_gap_mode_composition", "t15_cds_between_by_unit",
                "t16_geometry_by_model", "t27_old_report_reconciliation"],
        prose=[
            ("What is measured", "Every CANONICAL placement assigned to one of eight exclusive "
             "configurations. Two dominate: an ncRNA immediately upstream of the RT ({adj_n} "
             "placements, {adj_pct}) and an ncRNA upstream across a long empty intergenic gap "
             "({long_n}, {long_pct}). One intervening CDS accounts for {onecds_n} "
             "({onecds_pct}), overlap with the RT CDS for {ovl_rt_n} ({ovl_rt_pct}), and the "
             "known technical clipped mode for {tech_n} ({tech_pct}). {cds0_placement} of "
             "placements have no CDS at all in the gap; upstream placements are on the RT's own "
             "strand in {same_strand_up} of cases."),
            ("The second upstream mode is one protein", "The long-gap configuration looks like a "
             "second biological architecture and is not one. Its 900–1,100 bp band holds "
             "{band_placements} placements but only {band_rts} distinct exact RTs — "
             "{band_top_rt} of them come from a single protein, and {band_top_species_n} from "
             "*{band_species_name}*. Counted as exact pairs the configuration falls from "
             "{long_n} to {long_pairs} (against {adj_pairs} for the adjacent class), and it "
             "spans {long_species} species against thousands for the adjacent class."),
            ("PROPOSED: reading", "**Technical for the mode, biological for the shape.** The "
             "canonical retron architecture in this corpus is an ncRNA a few tens of bases "
             "upstream of the RT, on the same strand, with no gene between them — that survives "
             "every change of unit. The 1 kb mode is a redeposition artefact of one Salmonella "
             "locus and must not be reported as a second architecture. The ~2.7 kb downstream "
             "mode is g3's contig-start clipping artefact ({tech_ncrna} distinct ncRNA sequences "
             "across {tech_species} species) and is excluded from every biological reading here."),
            ("Geometry differs by model", "TypeIC1_IC2 sits at a median {ic1_median_dist} bp, "
             "TypeIA_IIAI at {ia_median_dist} bp (the Salmonella mode), TypeXIIIA_firmi at "
             "{xiiia_median_dist} bp, and {typev_tech_pct} of TypeV loci fall inside the "
             "technical clipped mode."),
            ("Would be wrong if", "the intervening-CDS count were wrong, since three "
             "configurations depend on it. An independent recount from `rt_window_cds_v1`, "
             "sharing no code with g3, reproduced it on {cds_recount_n} sampled placements at "
             "{cds_recount_agree}."),
        ],
        caveat="{opp_strand} placements ({opp_strand_pct}) are on the opposite strand and "
               "{dn_other_n} are downstream outside the technical mode. They are retained, not "
               "filtered, and are the natural starting population for an atypical-architecture "
               "question.",
    ),
    dict(
        id="6", title="Tool intersection and ncRNA carriage",
        view="unit: Retron records, loci, physical loci and exact RTs · denominator: units of "
             "that tool combination",
        figures=["fig17_tool_venn", "fig18_tool_upset_carriage", "fig19_combo_by_padloc_subtype"],
        tables=["t18_tool_combination_carriage", "t20_combo_by_padloc_subtype", "t22_padloc_rules"],
        prose=[
            ("What is measured", "The seven tool-call combinations over Retron loci, with ncRNA "
             "carriage in each. All three tools agree on {combo3_n} physical loci, of which "
             "{combo3_pct} carry a canonical ncRNA; myRT alone reaches {myrt_only_pct} and "
             "myRT+PADLOC {myrt_padloc_pct} ({myrt_padloc_n} loci). Only {combo_disagree} loci "
             "have records that disagree about which tools called them."),
            ("The gradient is partly definitional", "PADLOC's own rule files decide part of this. "
             "In 17 of 18 retron rules the ncRNA is a scoring element; for `retron_Ec107-like` "
             "and `retron_outgroup` the rule cannot be satisfied without a second element, so an "
             "ncRNA is required in practice; for `retron_XII` the ncRNA is a **prohibited** gene. "
             "A carriage rate computed on a PADLOC-defined subset is therefore partly a "
             "restatement of the rule."),
            ("But composition does not explain all of it", "Holding the PADLOC subtype fixed, "
             "carriage still moves with the tool combination: retron_II-A runs {iia_3tool} at "
             "three-tool agreement against {iia_myrt_padloc} in myRT+PADLOC, while retron_III-A "
             "stays low throughout ({iiia_3tool} at three-tool agreement). The myRT-only and "
             "DefenseFinder-only columns cannot be compared this way at all: a locus PADLOC did "
             "not call carries no PADLOC subtype."),
            ("PROPOSED: reading", "**Unresolved, and this bundle does not resolve it.** The "
             "Stage-1 conclusion stands unchanged: a tool-defined subset of this corpus is not a "
             "random subset, and the carriage gradient is confounded with detector definition. "
             "What is added here is that the gradient survives at the exact-RT unit "
             "({combo3_exact_pct} for three-tool agreement) and is not purely subtype "
             "composition."),
            ("Would be wrong if", "'detected by' meant 'the tool was run and returned negative "
             "elsewhere'. It does not: a tool absent from a record cannot be distinguished from a "
             "tool never run on that genome, which is a limit of the corpus, not of the analysis."),
        ],
        caveat="A locus's combination is the union over its records. Exact RTs are NOT exclusive "
               "between combinations, so the exact-RT row of the UpSet is a composition, not a "
               "partition.",
    ),
    dict(
        id="7", title="Retron ncRNA detection coverage and the zero-call class",
        view="unit: Retron physical loci · denominator: Retron physical loci of the named stratum",
        figures=["fig20_zero_call_by_database", "fig21_carriage_by_upstream_context",
                 "fig22_carriage_by_subtype"],
        tables=["t23_zero_call_by_database", "t24_carriage_by_upstream_context",
                "t21_carriage_by_subtype", "t23_zero_call_by_family"],
        prose=[
            ("What is measured", "How many Retron loci carry no ncRNA call, and what predicts it. "
             "In ncbi_bacteria {zero_ncbi} of {zero_ncbi_n} physical loci have none. Loci "
             "carrying two *distinct* ncRNA sequences are rare ({two_seq_ncbi} in ncbi_bacteria): "
             "the apparent 'two ncRNA' class is mostly one call arriving twice from a "
             "RefSeq/GenBank twin ({twin_double} loci in the twin stratum)."),
            ("Most of the zero class is missing context", "Carriage rises monotonically with the "
             "window context available upstream of the RT: {ctx_zero} of {ctx_zero_n} loci with "
             "no upstream context at all, {ctx_200} in the 1–200 bp bin, and {ctx_full} of "
             "{ctx_full_n} loci with more than 9 kb and no clipping. The canonical ncRNA sits a "
             "few tens of bases upstream, so a locus whose window starts at the RT cannot show "
             "one."),
            ("PROPOSED: reading", "**Technical and definitional, not biological absence.** The "
             "Retron zero-ncRNA rate is an upper bound on missingness, composed of at least "
             "three effects: windows clipped at a contig start, subtypes whose PADLOC rule "
             "prohibits or does not require an ncRNA, and genuine model gaps. retron_XII's "
             "{xii_pct} over {xii_n} loci is a rule; retron_VI's {vi_pct} over {vi_n} loci is not "
             "explained by the rule and is the better candidate for a real model gap."),
            ("Outside Retron this measures nothing about biology", "The zero rate is "
             "{rt_zero_retron} for Retron-labelled loci and {rt_zero_gii} for RVT-GII. The "
             "covariance models in this corpus are retron models; outside Retron the rate "
             "measures where the detector was pointed."),
            ("Would be wrong if", "the context gradient were an artefact of the eligibility "
             "filter. It is computed on geometry-eligible loci only, and the clipped and "
             "unclipped strata are plotted separately so the gradient can be read within each."),
        ],
        caveat="A positive control exists for the instrument: the same pipeline recovers ncRNAs "
               "at {ec107_n} retron_Ec107-like loci at {ec107_pct}. A zero is therefore a "
               "statement about scope and context, never about the organism.",
    ),
    dict(
        id="8", title="Exact RT–ncRNA pairing topology",
        view="unit: the 30,924 distinct (exact RT, exact ncRNA) pairs and their components · "
             "denominator: as named per panel",
        figures=["fig23_pair_topology_recurrence", "fig24_partner_consistency"],
        tables=["t28_topology_components", "t29_recurrence_classes", "t30_partner_consistency",
                "t30_partner_sequence_vs_family"],
        prose=[
            ("What is measured", "The bipartite structure of the exact-pair view: "
             "{pairs_1to1} strictly one-to-one components, {pairs_many1} many-RT-to-one-ncRNA and "
             "{pairs_manymany} many-to-many. {n_pairs} pairs occur exactly once."),
            ("Recurrence is mostly deposition", "{rec_redeposit_pairs} of pairs recur only as "
             "copies of one physical locus in several databases. Pairs recurring across species "
             "are {rec_species_pairs} of pairs but {rec_species_placements} of placements — the "
             "few genuinely widespread pairs dominate any placement-level count."),
            ("Recurrent proteins keep their partner", "Among exact RTs found at 100 or more "
             "physical loci ({dom100_n} proteins), {dom100} carry the same dominant exact ncRNA "
             "partner at 90% or more of their loci, and {single_model100} use a single covariance "
             "model. Where a protein does have several partners, {multi_partner_single_model} of "
             "those partner sets are still called by one model."),
            ("PROPOSED: reading", "**Biological, with a technical floor.** Partner identity "
             "travelling with an exact protein across hundreds of deposits is consistent with a "
             "tightly coupled RT–ncRNA unit. The floor is that many of those loci are copies of "
             "the same deposit, so the honest statement is at the pair-and-species level: the "
             "cross-species pairs are the ones worth a co-evolution question, and they are a "
             "minority of pairs."),
            ("Would be wrong if", "'a different exact ncRNA' meant 'a different ncRNA family'. It "
             "does not — two sequences differing by where the model cut the boundary are two "
             "nodes here and one molecule in biology. g3 tested the co-located case (366 sequence "
             "pairs at one locus, all with disjoint intervals) but the corpus-wide node count "
             "remains an upper bound on distinct molecules."),
        ],
        caveat="The exact-pair view is built on CANONICAL placements only, so a pair present only "
               "in an atypical or ineligible placement is absent from it.",
    ),
    dict(
        id="9", title="Atypical non-Retron retron-CM candidates",
        view="unit: the 266 retained placements · denominator: the candidate population, "
             "with CANONICAL Retron placements as the comparison",
        figures=["fig25_candidates"],
        tables=["t31_candidates_family_model", "t31_candidates_vs_retron",
                "t31_candidate_exact_rts"],
        prose=[
            ("What is measured", "Every retron covariance-model call that landed beside an RT "
             "that is not labelled Retron. {cand_n} single-family candidate placements (plus 6 in "
             "the MULTI stratum), spread thinly across RVT-GII, RVT-DGRs and a dozen other "
             "families and across most of the model library."),
            ("Principal observation", "They do not look like retrons. {cand_up} are upstream "
             "against {retron_env} of CANONICAL Retron placements inside the declared Retron "
             "envelope (upstream, same strand, no intervening CDS, within 1.1 kb); only "
             "{cand_env} of the candidates fall inside it, and their median separation is "
             "{cand_dist} bp against {retron_dist} bp for Retron."),
            ("PROPOSED: reading", "**Unresolved; most likely annotation disagreement.** This is a "
             "candidate/atypical population, explicitly **not** novel or divergent retrons. The "
             "geometry is what a scattered low-scoring model hit beside an unrelated RT would "
             "look like; a handful of same-strand, close, upstream cases are the only ones that "
             "resemble the Retron prior and they are individually listed in the landed tables."),
            ("Would be wrong if", "the family label were wrong rather than the model call. That "
             "is exactly what cannot be settled inside Stage 1, which is why the population is "
             "retained with its per-placement geometry rather than reclassified."),
        ],
        caveat="With 266 placements over ~40 family × model combinations, most cells hold single "
               "digits. No rate in this section should be read as a population estimate.",
    ),
    dict(
        id="10", title="MULTI: a real ambiguity stratum",
        view="unit: the {multi_n} V-RT-MULTI exact RT proteins · denominator: MULTI exact RTs, "
             "against g4's seeded single-family control",
        figures=["fig26_multi_ambiguity"],
        tables=["t32_margin_comparison", "t33_multi_family_pairs", "t33_multi_architecture"],
        prose=[
            ("What is measured", "The best-vs-second HMM margin for every MULTI protein. The "
             "median margin is {multi_margin} bits against {ctrl_margin} bits in the control, and "
             "{multi_below10} of MULTI proteins sit below 10 bits against {ctrl_below10} of "
             "controls. The best-scoring family is among the record's own labels for "
             "{multi_best_in_labels} of them."),
            ("Principal observation", "The ambiguity is concentrated, not diffuse: "
             "{crispr_gii_pairs} MULTI proteins carry the RVT-CRISPR/RVT-GII pair, by far the "
             "largest cell of the family-pair matrix. MULTI records are otherwise ordinary — "
             "{multi_ncrna_pct} carry an ncRNA call against {single_ncrna_pct} of single-family "
             "records, and {multi_elig} are geometry-eligible against {single_elig}."),
            ("PROPOSED: reading", "**Methodological, and unresolved by design.** MULTI is not "
             "mislabelling: the labels name precisely the profiles that score, and those profiles "
             "are a few bits apart. Choosing the top hit would impose a decision the evidence "
             "does not support. The concentration in specific family pairs says the boundary "
             "between those profile sets is where a classification effort should be spent."),
            ("Would be wrong if", "the small margins were a length artefact — MULTI proteins are "
             "shorter than single-family ones and HMM score scales with length. The margin-vs-"
             "length panel shows the confound directly and Stage 1 does not separate the two."),
        ],
        caveat="These are HMM scores from one library at one setting. A different profile library "
               "could resolve some of these ties and create others.",
    ),
    dict(
        id="11", title="Taxonomic representation, and prevalence where a denominator exists",
        view="unit: genomes · denominator: genomes of that taxon in the GTDB bacterial catalogue "
             "(prevalence), or records/exact RTs of the NCBI schema (representation)",
        figures=["fig27_gtdb_prevalence_phylum", "fig28_family_phylum_prevalence",
                 "fig29_rank_prevalence", "fig30_ncbi_genus_representation"],
        tables=["t34_gtdb_prevalence_by_rank", "t35_family_by_phylum_prevalence",
                "t36_ncbi_genus_representation"],
        prose=[
            ("What is measured", "For the gtdb_bacteria database only — where the corpus and the "
             "catalogue share the GTDB schema — the fraction of *sampled* genomes carrying at "
             "least one RT locus. Pseudomonadota: {pseudo_prev} of {pseudo_sampled} sampled "
             "genomes. Actinomycetota: {actino_prev}. Chlamydiota: {chlamydia_prev}."),
            ("Principal observation", "Prevalence and burden separate. Cyanobacteriota is at "
             "{cyano_prev} prevalence but {cyano_per_genome} exact RTs per positive genome, the "
             "highest of the large phyla. At genus level the spread is wider still — Klebsiella "
             "{kleb_prev} of {kleb_n} sampled genomes, Pelagibacter {pelagi_prev} of "
             "{pelagi_n}."),
            ("Representation is not prevalence", "The NCBI block has no phylum by construction "
             "and no sampled-genome denominator, so nothing there may be called enriched. What it "
             "shows is redundancy: Escherichia is {ecoli_records_pct} of NCBI-schema records but "
             "{ecoli_exact_pct} of exact RTs, and Salmonella contributes {salm_per_exact} records "
             "per distinct protein."),
            ("PROPOSED: reading", "**Biological signal, technically bounded.** A prevalence "
             "difference between phyla computed against a catalogue denominator is a real "
             "difference in how often these genomes carry a detectable RT. It is not a clean "
             "estimate of biological prevalence: the catalogue is an upper bound on what the "
             "pipeline attempted, and the corpus records no pipeline failures, so every "
             "prevalence here is a floor."),
            ("Would be wrong if", "the zero-prevalence genera were instrument failures. The same "
             "instrument recovered RT-positive genomes in 299,306 GTDB genomes including small-"
             "genome lineages, so a zero across a well-sampled genus is a recovery statement — "
             "but 'attempted and negative' and 'never attempted' cannot be separated in this "
             "corpus, which is why no absence claim is made."),
        ],
        caveat="GTDB and NCBI taxonomies are never pooled. All prevalence numbers are "
               "gtdb_bacteria only; the other seven databases contribute representation only.",
    ),
    dict(
        id="12", title="Data quality and eligibility: what a reader can inspect",
        view="unit: distinct records · denominator: all {n_distinct} distinct RT-anchored records",
        figures=["fig31_data_quality"],
        tables=["t40_inspectability", "t39_context_truncation_by_database",
                "t39_no_rt_cds_recovery_by_database", "t39_checkm_availability"],
        prose=[
            ("What is measured", "Every distinct record placed in one inspectability tier. "
             "{insp_full} are fully inspectable — exact back-translation, an RT CDS present, no "
             "clipping and no window-edge contact. {insp_clipped} are geometry-eligible but "
             "clipped or edge-touching, {insp_recoded} are geometry-eligible with a recoded "
             "translation, {insp_seqonly} records keep a usable sequence with no defensible "
             "genomic context, and {insp_illposed} remain ill-posed."),
            ("Principal observation", "Clipping is the dominant caveat, not translation failure: "
             "{clip_ncbi} of ncbi_bacteria records sit in a window clipped at the contig start. "
             "Records with no marked RT CDS come exclusively from the MAG catalogues — "
             "{mag_recovered} of them recovered in mgnify_human_gut alone, and exactly zero from "
             "either NCBI or either GTDB catalogue."),
            ("PROPOSED: reading", "**Technical.** The catalogue is usable at two very different "
             "levels of confidence, and §7 shows the practical consequence: the clipped fraction "
             "is where the ncRNA zero-class lives. An analysis that needs intact upstream context "
             "should declare the clipped stratum rather than inherit it silently."),
            ("Would be wrong if", "'fully inspectable' were doing more work than it can. It is a "
             "conjunction of five landed flags, not an assessment of whether the underlying "
             "assembly is correct."),
        ],
        caveat="A CheckM-style completeness value exists for only about a quarter of genome "
               "entries (g5): the NCBI summaries carry no such column, so a quality filter can "
               "never speak for the whole corpus.",
    ),
    dict(
        id="13", title="Secondary associations unlocked by the canonical units",
        view="unit: as named per panel · denominator: as named per panel",
        figures=["fig32_carriage_by_rt_length", "fig33_recurrence_breadth",
                 "fig34_tool_mix_by_database"],
        tables=["t25_carriage_by_rt_length", "t38_recurrence_breadth", "t26_tool_mix_by_database",
                "t37_carriage_by_host_completeness"],
        prose=[
            ("RT length and ncRNA carriage", "Carriage rises with RT length and with completeness: "
             "complete Retron proteins of 300–349 aa carry an ncRNA at {len300_carriage}, partial "
             "proteins under 200 aa at {len_short_carriage}. This is association, not mechanism — "
             "short partial RTs also sit disproportionately in clipped windows (§7)."),
            ("High recurrence is not taxonomic breadth", "Among Retron proteins found in 20 or "
             "more genomes, {breadth_one_species} are confined to a single species (deposition or "
             "clonal expansion) and {breadth_broad} span more than five species. A recurrence "
             "count alone therefore says nothing about host range."),
            ("Databases annotate differently", "The tool mix is database-specific: "
             "{ncbi_3tool_share} of ncbi_bacteria Retron loci have all three tools against "
             "{gut_myrt_only} of mgnify_human_gut loci called by myRT alone. Within each tool "
             "combination the carriage ordering repeats across databases, so the §6 gradient is "
             "not a property of one catalogue."),
            ("PROPOSED: reading", "**All three are associations on non-independent units.** They "
             "are reported with their units and denominators so a later stage can test them on a "
             "de-duplicated population; none is offered as a mechanism, and no hypothesis test is "
             "applied to counts inflated by re-deposition."),
            ("Would be wrong if", "these were read at the record unit, where one heavily "
             "deposited locus can move a percentage point on its own. Every panel here is at the "
             "exact-RT or physical-locus unit for that reason."),
        ],
        caveat="Host CheckM completeness is available only for GTDB/GEM/MGnify genomes, so the "
               "quality stratification in t37 covers a minority of the corpus.",
    ),
]

# What the report must not be read as saying.
CLOSING = """
This bundle is a **reporting layer**. It measured nothing new: every number above is a view over
the landed Stage-1 bundles and the registered canonical datasets, and every quantity that a
landed g1–g6 table also carries was compared against it before the report was built. The
comparison covers 294 quantities and found **0 disagreements**; where this bundle counts
something differently from a landed gate — coverage by placement versus by record, for instance —
the difference is landed as a declared definition difference, not presented as a correction.

`results/dbchar_g7_stage1_report/` remains the authoritative Stage-1 closeout and validation
report. Nothing in g1–g7 was modified, and **no claim status is proposed here**: the launcher
reserves promoting an interpretation to a thesis or paper claim for the operator, and
`human_input_audit` is PENDING for every Stage-1 bundle including this one.
"""
