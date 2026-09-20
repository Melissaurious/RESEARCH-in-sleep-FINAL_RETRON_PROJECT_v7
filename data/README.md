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

**Identity pin (2026-09-15):** `results/dbchar_g1_corpus_identity/` — per-file sha256 in its
`INPUTS.tsv`/`tables/s01_file_identity.tsv`, record-manifest digest in
`tables/s02_record_manifest_digest.tsv`, anchor populations in `tables/s02_populations.tsv`.
Counts live in the bundle, not here.

RT analyses operate on RT-anchored records. An ncRNA-anchor-only master file is not silently
mixed into RT denominators. The binding Stage-1 population rules (ncRNA-anchor-only exclusion,
MULTI stratum, RT-CDS-less eligibility classification) are
`docs/decisions/2026-09-15_stage1_population_rules.md`. `MULTI` remains its own multi-label population and is not appended
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

### External published source data — `references/rt0_rt7/`

Published literature source data lives under `references/rt0_rt7/<source>_<year>/`, **registered
with citation, DOI, sha256, bytes and untouched-source path** in
`references/rt0_rt7/RESOURCE_REGISTER.tsv`. That register is the authority; do not add a second
hierarchy for the same purpose.

| source | directory | register `asset_id` |
|---|---|---|
| Mestre *et al.* 2020 | `references/rt0_rt7/mestre_2020/` | `mestre_supp_*`, `mestre_tree_nwk` |
| Toro *et al.* 2014 | `references/rt0_rt7/historical/` | `hist_toro2014_*` |
| Toro *et al.* 2026 | `references/rt0_rt7/toro_2026/` | — |
| myRT reference package | `references/rt0_rt7/myrt/` | `myrt_*` |
| **Buffington *et al.* 2025** | **`references/rt0_rt7/buffington_2025/`** | **`buffington2025_supp_T1_retron_catalogue`** |

**`BUFFINGTON2025_RETRON_CATALOGUE`** — Supplementary Table 1 of
*Discovery and engineering of retrons for precise genome editing*,
`doi:10.1038/s41587-025-02879-3`. 105 rows, 8 columns, sha256
`d68366970378c05b5af9b00be886d76224a196a29b77171303f9353457cf4e62`, acquired 2026-09-20.
Untouched source: `/home/borg/Discovery_and_engineering_of_retrons_supp.csv`.
Identity record: `references/rt0_rt7/buffington_2025/PROVENANCE.md`.

⛔ **Presence in that table is a bioinformatic identification, not experimental validation** — it
carries no screening and no activity column. **It is merged into no project population**; the
proposed reconciliation is `T-X1-buffington-reconciliation`.

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

## Registered derived assets — Stage 1 (produced by `results/dbchar_g2_canonical_units`)

Location: `data/derived/` (gitignored; regenerated by that bundle's `run.sh` in ~13 min).
Identity, per-file sha256 and a writer-independent content digest:
`results/dbchar_g2_canonical_units/tables/g2_derived_registry.tsv`. Determinism was tested: an
independent merge rerun reproduced every file byte-identically.

| dataset | grain | rows |
|---|---|---:|
| `rt_records_v1.parquet` | one RT-anchored raw record, with unit keys, QC and eligibility flags | 3,059,700 |
| `rt_loci_v1.parquet` | one locus (contig, RT interval, strand) | 2,847,312 |
| `rt_physical_loci_v1.parquet` | one physical locus (`NZ_` normalised) + twin collapse evidence | 2,475,684 |
| `rt_exact_v1.parquet` + `.faa` | one exact RT protein (sha256, one trailing `*` removed) | 501,561 |
| `rt_ncrna_calls_v1.parquet` | one ncRNA call inside an RT-anchored record | 346,722 |
| `rt_window_cds_v1.parquet` | one CDS inside an RT-anchored record's window | 44,310,231 |

Views and pulls over them: `results/dbchar_g2_canonical_units/VIEWS.md` and `scripts/pull.py`.
Trust: `RE-DERIVE` from the g1 corpus pin; not `FROZEN`.

Produced by `results/dbchar_g2b_rt_cds_recovery` (registry: `g2b_derived_registry.tsv`):

| dataset | grain | rows |
|---|---|---:|
| `rt_cds_recovery_v1.parquet` | one RT-anchored record with no marked RT CDS, with its recovery state, representation class and eligibility flags | 31,504 |

Produced by `results/dbchar_g3_pair_geometry` (registry: `g3_derived_registry.tsv`):

| dataset | grain | rows |
|---|---|---:|
| `rt_ncrna_pairs_v1.parquet` | one RT↔ncRNA placement, with signed distance, direction, strand, intervening CDS, overlap, edge state, model, family, database, eligibility | 346,722 |
| `rt_ncrna_exact_pairs_v1.parquet` | one distinct (exact RT, exact ncRNA) pair | 30,924 |
| `rt_ncrna_exact_pair_recurrence_v1.parquet` | the same pairs with their recurrence class (redeposition vs species vs cross-species) | 30,924 |
| `rt_ncrna_nonretron_candidates_v1.parquet` | retron-CM placements beside **non-Retron-labelled** RTs — an atypical/candidate population, explicitly not called novel retrons | 266 |

⛔ The ncRNA covariance models in this corpus are **retron** models. A zero-ncRNA rate outside
Retron-labelled RTs measures detector scope, never biological absence (`g3_zero_class_by_family.tsv`).

Produced by `results/dbchar_g4_family_baseline` (registry: `g4_derived_registry.tsv`):

| dataset | grain | rows |
|---|---|---:|
| `rt_family_baseline_v1.parquet` | one exact RT protein, with its family label set, `V-RT-SINGLE`/`V-RT-MULTI` view membership, length and completeness state | 501,561 |
| `ncrna_family_baseline_v1.parquet` | one exact ncRNA sequence, with the covariance model(s) that called it and the RT family labels it occurs beside | 16,458 |
| `multi_hmm_evidence_v1.parquet` | one MULTI exact RT, with its per-profile `RVT-All.hmm` bit scores and the best-vs-second margin that shows the labels tie | 7,593 |

⛔ `MULTI` is an **ambiguity stratum**, not a family. These rows are never appended to a
single-family statistic: `rt_family_baseline_v1` keeps the label set, and the tie evidence that
justifies keeping it separate is in `multi_hmm_evidence_v1`.

Produced by `results/dbchar_g6_tool_calls` (registry: `g6_derived_registry.tsv`):

| dataset | grain | rows |
|---|---|---:|
| `rt_tool_calls_v1.parquet` | one distinct raw record, with per-tool detection flags, the tool combination, and **each tool's subtype label kept in its own column** | 3,051,238 |

⛔ `system_subtypes` carries two tools' vocabularies in one field (capital-initial =
DefenseFinder, lowercase = PADLOC). Never `groupby` the raw field; use the split columns. Tool
agreement is not independent corroboration — the tools share model lineage — and a tool absent
from a record cannot be distinguished from a tool that was never run on that genome.

## New-project derived assets

Stage 1 may propose registered reusable derived artifacts such as:

- `data/derived/locus_table_v1.parquet`
- `data/derived/rt_unique_v1.faa` + mapping table
- `data/derived/rt_ncrna_pairs_v1.parquet`

These are created only after their producing bundles land, carry hashes, and are registered.
The locus table is the canonical retained representation; downstream “clean” datasets are
declared views/queries over it.

## Registered derived assets — Stage 2 (`g5a` census and `g5` catalogue application)

Added 2026-09-17. Full registry with sizes, row counts and sha256:
**`docs/DATASET_REGISTRY.md`**. All are **LOCAL ONLY** — gitignored under `data/*`, never
pushed.

### `data/derived/rt07_g5a/` — the frozen eligibility partition

Produced by `results/rt07_g5a_eligibility_census/`. Fixes the g5/g6 denominator.

| file | rows | unit | sha256 |
|---|---|---|---|
| `g5a_eligibility_partition.tsv.gz` | 501,561 | exact RT | `249e334b04b2db79…` |
| `g5a_eligible_ids.txt.gz` | 369,381 | exact RT | `6f2028fa46563ebe…` |
| `g5a_ineligible_records.tsv.gz` | 132,180 | exact RT | `9fd48b77df6d8e3e…` |

`G5_ELIGIBLE_N = 369,381` of 501,561. The 132,180 excluded records (108,439 below the frozen
250 aa floor, 23,741 carrying a non-standard residue) are **retained in full with metadata**,
never dropped.

### `data/derived/rt07_g5/` — the canonical mapped dataset

Produced by `results/rt07_g5_catalogue_application/` with instrument
`rtmap-1.0.0/53a1e738a19b3896`. This is what `g6` consumes.

| file | rows | unit | sha256 |
|---|---|---|---|
| `g5_states.parquet` | 55,407,150 | exact RT × frozen state | `5bdcb6e3ef4344da…` |
| `g5_sequences.parquet` | 369,381 | exact RT | `55bd268a1b8ff01b…` |
| `g5_catalytic.parquet` | 369,381 | exact RT | `95dcb20aac95946c…` |
| `g5_ineligible.parquet` | 132,180 | exact RT | `253a092fd4d72b15…` |
| `g5_run_failures.parquet` | 0 | failed record | `4b1d1ae5ce9033c3…` |
| `g5_metadata_crosswalk.parquet` | 501,561 | exact RT | `02c6e54d12e4a1c2…` |

All joins are on `rt_hash`. The crosswalk covers the whole catalogue with an
`in_g5_eligible` flag, so any denominator can be taken without re-deriving eligibility.

Verify with `bash results/rt07_g5_catalogue_application/verify.sh`.

### Scratch not to delete yet

`ARIS_OUTPUT/rt07_g5/` (12 GB) holds the 512 per-shard FASTAs, TSVs and `DONE` sidecars —
the shard-level audit evidence. Deletion conditions are in `docs/DATASET_REGISTRY.md` §4.
