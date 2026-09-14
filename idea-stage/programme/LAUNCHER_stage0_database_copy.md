# LAUNCHER — Stage 0 · Database characterization


## Environment
```bash
conda activate retron_tradicional        # never base
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
# Ibex jobs: conda env /ibex/user/rioszemm/conda-environments/retron_tradicional; never base.
```
---

Project root`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK` and task ID: `stage0_database_characterization` 

## Read first
1. `/home/borg/RESEARCH-in-sleep-GENERAL_v3/CLAUDE.md`
1. `/home/borg/RESEARCH-in-sleep-GENERAL_v3/WORKING_AGREEMENT.md`


---

## Scientific context
I have assembled and deployed a large-scale pipeline for the discovery and annotation of reverse transcriptases (RTs) from eight public databases: `gtdb_bacteria`, `gtdb_archaea`, `ncbi_bacteria`, `ncbi_archaea`, `mgnify_human_gut`, `mgnify_marine`, `mgnify_soil`, and `gem`. The pipeline uses three complementary sequence-based tools (all with their own hidden markov model profiles HHMs and synteny rules) to maximize sensitivity:

- **DefenseFinder** — bacterial phage defense system detector, used here to detect retrons specifically
- **PADLOC** — also a defense system locator, used here to detect retrons specifically; importantly provides ~21 covariance models (CMs) built with Infernal to detect retron ncRNAs. CM matches were provided not only for RT matches from PADLOC but across tools and across RT families.
- **MyRT** — detects all RT families (including retrons).

Each tool provides its own HMM profiles for protein detection. PADLOC's retron CMs were used with Infernal to scan intergenic regions; any ncRNA match within ±10 kbp of an RT hit (regardless of RT family label) was retained in the system record.

**Pipeline output:** One JSON object per system, containing:
- Prodigal metadata for all CDS and intergenic regions within ±10 kbp of the RT, genomic window expanded if needed or truncated if not enough data.
- Identity labels for the RT and ncRNA (where detected)
- No functional annotation for other coding regions (accessory proteins are currently unlabeled)
- Other metadata content explained @//home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK/MELISSA_DATA/templates/input_format_schema_only.md, @/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK/MELISSA_DATA/MELISS_SCRIPTS/utils_FOR_ALL_FILES.py has some useful functions already to manipulate the data under class PipelineData, use as starting point if needed.

Retrons are special type of RTs that are transcribed in the same operon with its RNA substrate, a distinctive trait compared to other RTs.

---

## 0 · The point of this task

Characterize the screening database and surface the most striking, defensible descriptive insights — the foundation later stages and the paper will build on. Decide WHAT is worth reporting (per database, per RT family, per ncRNA CM, per domain Archaea/Bacteria, and across databases), compute it efficiently, then interpret. Descriptive + anomaly-flagging only. This stage should also be the one producing datasets for downstream tasks (not addressed here) and propose a way to pull them, for example: which flags or data features shall be considered during the dataset construction. For example, I need a dataset for RT-ncRNA unique pairs (example of downstream task: study co-evolution of elements; multiple ncRNAs per RT or viceversa has to be resolved or appropiateley flagged/reported), unique RTs (exact RT string deduplication; how to handle if same RT is present across different taxa), and unique locus (what makes a unique locus and why it is important to consider when doing genomic neighborgood analysis around the RT).

---

## Read first (context — do not modify any of these)
- `@MELISSA_DATA/supporting_material/report_ncbi_bacteria_Bacteria.html` — example
  report. Decide what to carry over vs. the PREVIOUS_ARIS_WORK report; don't invent
  a third style.
- `@templates/input_format_schema_only.md` — MANDATORY. Data content and structure, file sizes,
  entry counts per system (RT family, and ncRNA-only anchor systems), schema,
  per-file rules, genome-ID normalization. This is the overview of the large-scale
  public-database mining output. Read the notes in it.
- `@supporting_material/databases_metadata_files`  — 8 files | taxonomy join tables per `source_database`.

---

## ALREADY GENERATED — reference these paths, do not recompute

All paths below are absolute and live in `/home/borg/RESEARCH-retron-db`. They are listed here
as references only.

### The traps, the views, and how to pull

- `/home/borg/RESEARCH-retron-db/docs/DATA_EXPERT_PRIMER.md`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/VIEWS.md`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v01_redundancy_ladder.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v02_window_views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v03_multiplicity_tiers.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/pull_vocabulary.tsv`
- `/home/borg/RESEARCH-retron-db/tools/pull.py`  (`--describe`, `--view`, `--group-report`)

### The data register — assets, scripts, tables, findings

- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/README.md`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/USING_THE_DATA.md`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/FINDINGS.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/datasets.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/tables.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/scripts.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/coverage.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/build_register.py`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/build_datasets.py`

### Derived artifacts on disk

- `/home/borg/RESEARCH-retron-db/data/README.md`  (the register; 3 of 12 artifacts described)
- `/home/borg/RESEARCH-retron-db/data/derived/locus_table_v1.parquet`  (+ `.sha256`)
- `/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.faa`  (+ `.tsv`, `.sha256`)
- `/home/borg/RESEARCH-retron-db/data/derived/panel_derivation_v1.faa`  (+ `.tsv`, `.sha256`)
- `/home/borg/RESEARCH-retron-db/data/derived/panel_heldout_v1.faa`  (+ `.tsv`, `.sha256`)
- `/home/borg/RESEARCH-retron-db/data/derived/panel_truth_v1.faa`  (+ `.tsv`, `.sha256`)
- `/home/borg/RESEARCH-retron-db/data/derived/frame_rvt_v1.hmm`  (+ `.sha256`)
- `/home/borg/RESEARCH-retron-db/data/derived/reference_msa_v1.afa`
- `/home/borg/RESEARCH-retron-db/data/derived/reference_tree_pruned_v1.nwk`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g1-locus-table/INPUTS.tsv`  (the 42 in-scope JSONL at their sha256)

### Landed bundles — scripts, tables, figures, provenance

- `/home/borg/RESEARCH-retron-db/results/dbchar-g0-inventory/`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g0b-locus-identity/`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g1-locus-table/`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/`
- `/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights/`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/`
- `/home/borg/RESEARCH-retron-db/results/stage3_placement_toolkit/`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/`
- `/home/borg/RESEARCH-retron-db/results/rtdomain-g0-provenance/`
- `/home/borg/RESEARCH-retron-db/results/rtdomain-g1a-structures-c1/`
- `/home/borg/RESEARCH-retron-db/results/rtelem-g1-frame-and-occupancy/`
- `/home/borg/RESEARCH-retron-db/results/rtelem-g2-panels/`

### Reports already assembled

- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/REPORT.md`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/REPORT.html`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/REPORT.md`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/deck/DECK.html`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/deck/DECK_interactive.html`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/deck/figures/`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/deck/tables/`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/deck/README.md`

### The reporting and figure layer (style, assembler, figure map)

- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full/scripts/_style.py`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/helpers.py`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/assemble_report.py`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/report_style.css`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/figure_map.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/statistic_inventory.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/proposed_analyses.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/deck/_deck.py`

### Per-question tables for the three dataset asks in §0

RT–ncRNA pairs:
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c14_a25_multiplicity_ladder.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c14_a25_degree_distribution.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c07_a12_cm_model_composition.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c07_a18_duplicate_call_qc.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c18_geometry_priors.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c18_distance_classes.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c18_annotation_artefact_signatures.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c09b_a36_cds_between.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c09b_a37_rank_state.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c15_a17_orientation_qc.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/q06_ncrna_model_check.py`

Unique RTs, including the same RT across taxa:
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/tables/s1_cross_family_keys.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/tables/s2_ncrna_portability.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/tables/s3_rarefaction.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/tables/s5_three_state_filters.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c16_rt_length_stats_by_family.tsv`
- `/home/borg/RESEARCH-retron-db/results/rtelem-g2-panels/tables/p1_completeness_screen.tsv`
- `/home/borg/RESEARCH-retron-db/results/rtelem-g2-panels/tables/p2_family_funnel.tsv`
- `/home/borg/RESEARCH-retron-db/results/rtelem-g2-panels/tables/p3_holdout_separation.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/q04_domain_and_records.py`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/q05_domain_two_routes.py`

Unique locus and genomic neighbourhood:
- `/home/borg/RESEARCH-retron-db/results/dbchar-g0b-locus-identity/`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v02_window_views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c12_a20_edge_adjacency.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c12_a35_window_extension.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c13_a32_contig_census.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c20_contig_pair_geometry.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/q02_qc_flag_menu.py`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/q03_same_rt_diff_nbhd.py`
- `/home/borg/RESEARCH-retron-db/docs/responses/2026-09-10_dbchar_r02_flanking-adequacy.md`

### Process history — failures already paid for, and open questions

- `/home/borg/RESEARCH-retron-db/docs/LAUNCHER_AMENDMENTS.md`
- `/home/borg/RESEARCH-retron-db/docs/BLOCKED.md`
- `/home/borg/RESEARCH-retron-db/docs/decisions/`
- `/home/borg/RESEARCH-retron-db/docs/decisions_pending/OLD_ANALYSIS_CENSUS.tsv`
- `/home/borg/RESEARCH-retron-db/docs/responses/`
- `/home/borg/RESEARCH-retron-db/retros/`
- `/home/borg/RESEARCH-retron-db/launchers/`
- `/home/borg/RESEARCH-retron-db/general/` (governance layer, pinned; `general/tools/index.sh`)

### Pipeline that produced the corpus — code only, provenance unverified

- `/home/borg/RETRONS_january_2026/the-retron-project/pipeline_for_negative_dataset_with_deleting/TEST_SCRIPT_31_nov_v5.py`
- `/home/borg/RETRONS_january_2026/the-retron-project/pipeline_for_negative_dataset_with_deleting/rt_integration_corrected.py`
- `/home/borg/RESEARCH-retron-db/docs/responses/2026-09-14_coordination_r08_answers-to-nbhd-data-questions.md`

---

## Approach (section-based; compute then interpret)

### Step 1 — Recon (facts only, no analysis)

> **Note to ARIS:** Treat all scripts as starting points. They may have issues with structure, efficiency, methodology, or correctness. Review them, propose improvements, and implement improved versions in `ARIS_OUTPUT/` — never edit the originals.

Recon reads, before anything is computed:
`/home/borg/RESEARCH-retron-db/docs/DATA_EXPERT_PRIMER.md` ·
`/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/VIEWS.md` ·
`/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/USING_THE_DATA.md` ·
`/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/FINDINGS.tsv` ·
`/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/tables.tsv`

### Step 2 — Propose report SECTIONS (PLAN — wait for approval)

Section precedent: `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/statistic_inventory.tsv` ·
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/proposed_analyses.tsv` ·
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/figure_map.tsv`

### Step 3 — Compute sections (Phase A: numbers only)

Before computing a section, check for an existing table:
`/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/tables.tsv`

### Step 4 — Interpret (Phase B: one round over all numbers)

### Step 5 — Assemble & close


## Execution protocol — work phase by phase, report incrementally, stop for approval


---


## Compute


---


## Stop condition


---

## Required outputs → ARIS_OUTPUT/stage0_database_characterization/
- cache/   — intermediate streamed tables (reusable by later stages)
- scripts/ — one script per section + the assembler
- figures/ — PNG + EPS + SVG per figure
- tables/  — the TSV behind every figure + data_profile + resource_estimates
- REPORT.md, REPORT.html (established style), STATUS.md (last)

Layout and style precedent:
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/` ·
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full/scripts/_style.py` ·
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/helpers.py` ·
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/assemble_report.py` ·
`/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/report_style.css`

---

## Guardrails
- Never modify outside the task subfolder at ARIS_OUTPUT, anything outside shall be only read or copy into cached files needed by the currrent session.
- retron_tradicional only; missing package → report and STOP (don't install).
- Exclude `anchor_type="ncRNA"` from RT analyses; exlcude MULTI = multi-label from any per data analysis, do not include in any per RT family analysis.
- Environment incantation and package versions: `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/USING_THE_DATA.md` §0
- Known traps before any number: `/home/borg/RESEARCH-retron-db/docs/DATA_EXPERT_PRIMER.md` §2
- Failures already paid for: `/home/borg/RESEARCH-retron-db/docs/LAUNCHER_AMENDMENTS.md`
