# DATA / RESOURCE REGISTER — Retron project

This file is the project-level map of canonical inputs, reusable references, prior work and
compute resources. It is not a result table. Paths are registered so launchers do not have
to rediscover them.

## Policy

- Source and canonical inputs are read-only.
- Large raw data, prior bundles, structures and model collections stay at their canonical
  locations. Register path + identity; do not duplicate them into this project.
- Small load-bearing references may be copied into the project when that makes execution
  self-contained, but only after identity/hash is recorded.
- Prior reports/scripts/bundles are starting points and comparison material. Their numbers
  are `RE-DERIVE` unless explicitly promoted by a project decision.
- No measurement is currently `FROZEN` in this new project.

## Project roots

| resource | path | status / use |
|---|---|---|
| project root | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7` | writable project |
| scratch | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/ARIS_OUTPUT/` | disposable ARIS scratch |
| landed results | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/` | reproducible bundles |
| project supplementary material | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/` | small references already copied here |
| prior production project | `/home/borg/RESEARCH-retron-db/` | read-only reference / `RE-DERIVE` |

## Canonical raw corpus

| resource | path | trust | copy policy | notes |
|---|---|---|---|---|
| RT/retron mining corpus | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/` | `RAW` | **leave in place** | canonical local source to inventory + hash before Stage 1 |
| Ibex mirror of the same corpus | `TO VERIFY` | `DO-NOT-USE` until identity checked | leave in place | user reports a mirror exists; discover and compare hashes before use |
| schema in current project | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/templates/input_format_schema_only.md` | `RAW` reference | already local if present | schema is a hypothesis; probe real values |
| older schema source | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V5/templates/input_format_schema_only.md` | `RE-DERIVE` reference | no duplicate if identical | compare hash/content to current-project copy |

### Corpus scope rule for Stage 1

RT analyses operate on RT-anchored records. An ncRNA-anchor-only master file is not silently
mixed into RT denominators. `MULTI` remains its own multi-label population and is not appended
to any single RT family. Exact in-scope file inventory and counts are derived by Stage 1 and
are not hard-coded here.

## Metadata

Current project location:

`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/databases_metadata_files/metadata_files/`

Known files:

- `gem_metadata.tsv`
- `gtdb_archaea_metadata.tsv.gz`
- `gtdb_bacteria_metadata.tsv.gz`
- `mgnify_human_gut_metadata.tsv`
- `mgnify_marine_metadata.tsv`
- `mgnify_soil_metadata.tsv`
- `ncbi_archaea_assembly_summary.txt`
- `ncbi_bacteria_assembly_summary.txt`
- `uhgg_v2.0.2_metadata.tsv`

Trust: `RAW`. Stage 1 must measure join coverage and missingness before using any metadata
field as a filter. Taxonomy systems/schemas are retained explicitly rather than pooled.
Assembly/environment/quality/isolate-vs-metagenome fields are carried where the source
supports them; missingness is itself reported.

## Existing helper / report precedents

| resource | path | trust | action |
|---|---|---|---|
| raw-data helper | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/utils_FOR_ALL_FILES.py` | `RE-DERIVE` | inspect/port useful extraction logic; never edit in place |
| old NCBI-bacteria report | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/report_ncbi_bacteria_Bacteria.html` | reference only | source of analysis/layout ideas, not numbers |
| mature prior Stage-4 report | `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/REPORT.html` | `RE-DERIVE` | content/style precedent; audit tables before reuse |
| mature prior Stage-4 Markdown | `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/REPORT.md` | `RE-DERIVE` | interpretation precedent, not authority |

## Prior production assets — inspect before recomputing

### Views / pull machinery

- `/home/borg/RESEARCH-retron-db/docs/DATA_EXPERT_PRIMER.md`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/VIEWS.md`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v01_redundancy_ladder.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v02_window_views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v03_multiplicity_tiers.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/pull_vocabulary.tsv`
- `/home/borg/RESEARCH-retron-db/tools/pull.py`

Trust: `RE-DERIVE`. Reuse definitions/code only after checking what they actually did.

### QA register

- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/README.md`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/USING_THE_DATA.md`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/FINDINGS.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/datasets.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/tables.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/scripts.tsv`
- `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/coverage.tsv`

Important known limitation: the production register demonstrates strong producer traceability
but denominator coverage is not sufficient for citation. Treat it as an inventory, not a
blanket validation.

### Reusable derived/reference artifacts in the prior project

- `/home/borg/RESEARCH-retron-db/data/derived/locus_table_v1.parquet`
- `/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.faa`
- `/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.tsv`
- `/home/borg/RESEARCH-retron-db/data/derived/panel_derivation_v1.faa`
- `/home/borg/RESEARCH-retron-db/data/derived/panel_heldout_v1.faa`
- `/home/borg/RESEARCH-retron-db/data/derived/panel_truth_v1.faa`
- `/home/borg/RESEARCH-retron-db/data/derived/frame_rvt_v1.hmm`
- `/home/borg/RESEARCH-retron-db/data/derived/reference_msa_v1.afa`
- `/home/borg/RESEARCH-retron-db/data/derived/reference_tree_pruned_v1.nwk`

Trust: `RE-DERIVE` unless a later task explicitly verifies/promotes one.

### Prior landed bundles most relevant to Stage 1

- `/home/borg/RESEARCH-retron-db/results/dbchar-g0-inventory/`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g0b-locus-identity/`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g1-locus-table/`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/`

The new Stage 1 follows: **REUSE → VERIFY → GAP ANALYSIS → COMPUTE ONLY GAPS**.

## Small reference files already available in the current project

Directory:

`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/`

Known useful resources include:

- `Mestre_supplementary_material.csv`
- `Supplementary_mestre_Tree.nwk`
- `Supp_material_T1_R1_systematic_prediction.csv`
- `supp_material_systematic_prediction_paper.csv`
- `Suppl_Toro_Tree.txt`
- `toro_2014_Rt0-Rt7.FASTA`
- `myRT-FastTree2.refpkg/`

Keep these small resources here rather than making another copy. Stage-specific launchers
declare which are inputs.

## Detector/model resources

| resource | borg path | role / caution |
|---|---|---|
| PADLOC ncRNA CMs | `/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm/padlocdb.cm` | retron ncRNA detection; model provenance matters |
| PADLOC CM metadata | `/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm_meta.txt` | CM → retron/clade metadata |
| PADLOC retron rules | `/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/sys/retron_*.yaml` | synteny/subtype rules |
| DefenseFinder retron profiles | `/home/borg/.macsyfinder/models/defense-finder-models/profiles/*Retron*` | retron protein profiles |
| MyRT all-RT HMM | `/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/HMM/RVT-All.hmm` | RT family classification |
| MyRT reference package | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/myRT-FastTree2.refpkg/` | reference HMM/tree/alignment |

Do not treat agreement between tools as independent corroboration until model/publication
lineage is explicitly checked.

## Environments and compute

### borg

Primary environment:

`/home/borg/miniconda3/envs/retron_tradicional`

Expected tools include `hmmsearch`, `hmmbuild`, `hmmalign`, `mafft`, `muscle`, `cd-hit`,
`mmseqs`, `blastp`, `trimal`, `cmsearch`, `cmbuild`, `cmfinder.pl`, and `mkdssp`.

Other environments:
- Foldseek: `/home/borg/miniconda3/envs/esmologs/bin/foldseek`
- FoldMason: `/home/borg/miniconda3/envs/foldmason/bin/foldmason`
- RNAfold: `/home/borg/.local/bin/RNAfold`

### Ibex

Primary conda environment:

`/ibex/user/rioszemm/conda-environments/retron_tradicional`

Known modules/resources:
- `esm/1.0.3`
- `foldseek/10-941cd33`
- AlphaFold databases: `/ibex/reference/KSL/alphafold/{2.1.1,2.3.1,3.0.0}`
- Full Pfam-A 37.0:
  `/ibex/user/rioszemm/the-retron-project/src/interproscan/interproscan-5.70-102.0/data/pfam/37.0/pfam_a.hmm`

⚠️ Local InterProScan is known to have an inadequate/stub profile database for Pfam/TIGRFAM
work. Do not use its apparently successful execution as evidence of full annotation coverage.

## Stage 1 retained-field contract

The canonical locus-level representation produced by Stage 1 must retain enough information
that later tasks do not have to re-stream the raw corpus merely because a field was dropped.

At minimum retain or make losslessly traceable:

- source database and original record/system identifiers
- anchor type and original tool labels
- per-tool calls separately (`MyRT`, `PADLOC`, `DefenseFinder` where available)
- RT amino-acid sequence, coordinates, strand, completeness/partial flags
- exact RT sequence hash computed in this project
- contig/genome identifiers and coordinate frame / actual-window offsets
- contig-edge/clipping/truncation flags
- all ncRNA calls with sequence, model/CM, coordinates, strand and confidence fields
- RT↔ncRNA distance in bp, direction, same/opposite strand, CDS-between count and overlaps
- multiplicity class rather than a silently selected one-to-one pair
- CDS/intergenic neighbourhood needed to reconstruct later architecture analyses
- taxonomy system and raw lineage fields
- keys needed for source-database metadata joins
- environment/isolate/metagenome/assembly-quality metadata where available, with missingness
- raw and normalized family/subtype labels without pooling provenance
- flags/views used for downstream extraction rather than destructive filtering

## New-project derived assets

Stage 1 may propose registered reusable derived artifacts such as:

- `data/derived/locus_table_v1.parquet`
- `data/derived/rt_unique_v1.faa` + mapping table
- `data/derived/rt_ncrna_pairs_v1.parquet`

These are created only after their producing bundles land, carry hashes, and are registered.
The locus table is the canonical retained representation; downstream “clean” datasets are
declared views/queries over it.
