# LAUNCHER — 01_database_characterization

> Stage 1 is a consolidation and gap-closure task, not a fifth independent reimplementation.
> Extensive prior work exists. Reuse it only after auditing its definitions, provenance and
> denominator coverage.

## 1. Objective and success criterion

**Objective.** Establish the canonical analytical representation and defensible descriptive
baseline of the large-scale RT/retron mining corpus by auditing reusable prior work, verifying
load-bearing definitions and provenance, and computing only missing or untrusted quantities.

**Success criterion.** The task is complete when:

1. the in-scope raw corpus is inventoried and identity-pinned;
2. a canonical locus-level representation can be reproduced from the raw inputs and retains
   every downstream-critical flag listed in `data/README.md`;
3. exact RT, locus, taxonomic-occurrence and RT–ncRNA-pair views are explicit queries over
   that representation rather than undocumented filtered copies;
4. RT sequence/coordinate/strand integrity and the contig/window frame have been tested;
5. redundancy, per-family composition/length/completeness, ncRNA multiplicity/geometry,
   metadata coverage/overrepresentation and per-tool call preservation are measured on
   declared units with named denominators;
6. prior tables/scripts used by the task are graded as reusable, requires re-derivation,
   obsolete/wrong, or unknown;
7. publication/presentation-quality tables and figures are generated from landed tables, and
   the final Markdown report can be traced to producing bundles;
8. reusable derived assets are registered with hashes rather than hidden in scratch.

**Primary reusable products.**

- canonical locus table with raw + normalized fields and QC flags;
- exact-RT sequence set plus occurrence mapping;
- RT–ncRNA association/pair table with multiplicity retained;
- documented view/pull vocabulary for common downstream datasets;
- a descriptive Stage-1 report and figure/table set.

**Storage contract.**

- scratch: `ARIS_OUTPUT/01_database_characterization/`;
- measurements: the six `results/dbchar_g*/` directories declared in §7;
- reusable expensive derived datasets: `data/derived/`, only after their producing bundle
  lands and the artifact is registered.

The default is **flag, retain, stratify** — not delete.

## 2. Kill criteria

Stop this task and land the failure instead of freezing a canonical dataset if any of these
holds:

- the canonical raw input set cannot be identity-pinned well enough to state which files and
  records were analysed;
- no deterministic, auditable mapping can be constructed from raw records to the locus,
  exact-RT and RT–ncRNA association units while preserving ambiguous cases;
- RT sequence/coordinate-frame verification reveals an unresolved systematic frame error
  that makes locus geometry uninterpretable;
- a required prior artifact is the only available source for a load-bearing value and cannot
  be re-derived or independently checked;
- execution exceeds 2× the measured full-run estimate or the compute envelope in §9.

A null descriptive result does not kill the task. This is primarily a foundation/description
task; unusual and zero classes are outputs.

## 3. Non-goals — out of scope

This task does **not**:

- derive or redefine RT0–RT7;
- infer palm/fingers/thumb boundaries or discover RT motifs;
- build an RT phylogeny or structural tree;
- functionally annotate the full accessory-protein neighbourhood or delimit operons;
- perform diversity/saturation estimators beyond the baseline redundancy/sampling
  characterization needed to define later populations;
- test RT–ncRNA co-evolution;
- declare annotation disagreement to be biological novelty;
- build a new retron detector or classifier;
- decide a single universal definition of “unique system”;
- silently repair or overwrite prior projects, raw inputs or historical bundles.

Those later tasks consume Stage-1 outputs through explicit views.

## 4. Inputs

| path | what it is | trust grade |
|---|---|---|
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/` | canonical local raw mining corpus; inventory/hash before use | `RAW` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/templates/input_format_schema_only.md` | intended input schema and normalization notes; verify against real values | `RAW` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/databases_metadata_files/metadata_files/` | taxonomy/assembly/environment metadata | `RAW` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/utils_FOR_ALL_FILES.py` | old raw-data helper / `PipelineData` implementation | `RE-DERIVE` |
| `/home/borg/RESEARCH-retron-db/results/` | prior landed production bundles relevant to database characterization | `RE-DERIVE` |
| `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/qa/register/` | prior inventory of datasets/tables/scripts/findings | `RE-DERIVE` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/report_ncbi_bacteria_Bacteria.html` | old report/content precedent | `RE-DERIVE` |
| `/home/borg/RETRON_STAGES/01_database_characterization.md` | scientific ideas, traps, prior attempts and report architecture | `RE-DERIVE` |

All inputs are read-only. The prior production project is not modified.

The Ibex mirror of the raw corpus is `DO-NOT-USE` until its path is located and identity
against the local canonical input is verified.

## 5. What might already exist

Start by reading these. Do **not** assume their numbers are correct merely because the files
exist.

### Prior Stage-1 views and pull machinery

- `/home/borg/RESEARCH-retron-db/docs/DATA_EXPERT_PRIMER.md`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/VIEWS.md`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v01_redundancy_ladder.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v02_window_views.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/v03_multiplicity_tiers.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/tables/pull_vocabulary.tsv`
- `/home/borg/RESEARCH-retron-db/tools/pull.py`

### Prior reusable datasets / bundles

- `/home/borg/RESEARCH-retron-db/data/derived/locus_table_v1.parquet`
- `/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.faa`
- `/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.tsv`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g0-inventory/`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g0b-locus-identity/`
- `/home/borg/RESEARCH-retron-db/results/dbchar-g1-locus-table/`
- `/home/borg/RESEARCH-retron-db/results/stage0_db_characterization/`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/`

### Report/figure architecture worth inspecting

- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/helpers.py`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/assemble_report.py`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/scripts/report_style.css`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/figure_map.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/statistic_inventory.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/proposed_analyses.tsv`

### Existing tables directly relevant to this task

RT–ncRNA / geometry:
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c14_a25_multiplicity_ladder.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c14_a25_degree_distribution.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c18_geometry_priors.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c09b_a36_cds_between.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c15_a17_orientation_qc.tsv`

RT:
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c16_rt_length_stats_by_family.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage2_leakage_and_sampling-c1/tables/s1_cross_family_keys.tsv`

Locus/context:
- `/home/borg/RESEARCH-retron-db/results/dbchar-g0b-locus-identity/`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c12_a20_edge_adjacency.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c13_a32_contig_census.tsv`
- `/home/borg/RESEARCH-retron-db/results/stage4_db_characterization_full-c1/tables/c20_contig_pair_geometry.tsv`

### When prior work is untrustworthy

A prior artifact must be re-derived or rejected when its analytical unit/denominator is
unstated, it pools tool-specific fields, it treats taxonomy schemas as one, it depends on an
unverified inherited `rt_hash`, it cannot trace back to the raw record, its producer is
unknown, or the current task cannot reproduce its definition independently.

Prior work may still be reused as code/design even when its number is not reusable.

## 6. Claims this task tests

| id | role in this task |
|---|---|
| `C1` | `primary` |
| `C2` | `primary` |
| `C5` | `supporting` |
| `C7` | `supporting` |
| `C8` | `supporting` |

Claim wording/status live only in `idea-stage/docs/research_contract.md`.

## 7. Gates

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| `dbchar_g1_corpus_identity` | exact inventory of in-scope raw files/records, hashes, anchor populations and parse/validation failures | `LIGHT` | `C1` supporting | done when `results/dbchar_g1_corpus_identity/` reruns from the registered source roots and reproduces the inventory |
| `dbchar_g2_canonical_units` | redundancy/identity mapping among raw record, locus, genome, exact RT, taxonomic occurrence and source database | `FULL` | `C1`,`C2` | done when `results/dbchar_g2_canonical_units/` reruns and reproduces the canonical unit table + independent denominator checks |
| `dbchar_g3_pair_geometry` | RT–ncRNA association census: zero class, multiplicity, bp/CDS separation, direction, strand and overlap | `FULL` | `C2`,`C5` | done when `results/dbchar_g3_pair_geometry/` reruns and reproduces the pair/geometry tables from canonical loci |
| `dbchar_g4_family_baseline` | non-redundant per-family RT/ncRNA descriptive baseline: length, completeness, model composition and named outliers | `FULL` | `C1` supporting | done when `results/dbchar_g4_family_baseline/` reruns on the declared unique-RT/ncRNA views and reproduces every reported table |
| `dbchar_g5_metadata_sampling` | metadata/taxonomy/source-database coverage and overrepresentation on declared schema-specific populations | `FULL` | `C8` supporting | done when `results/dbchar_g5_metadata_sampling/` reruns, reports join/missingness coverage and reproduces corrected sampling tables |
| `dbchar_g6_tool_calls` | per-tool retron annotation/call matrix plus missingness and extraction-asymmetry audit on a declared retron locus population | `FULL` | `C7` supporting | done when `results/dbchar_g6_tool_calls/` reruns and reproduces separated per-tool tables without pooled `system_subtypes` |

The task may split a gate if it cannot fit one reliable execution/review unit. It may not
silently broaden a gate into RT0–RT7, operon annotation, co-evolution or novelty analysis.

## 8. Compute

- Expected machine: **borg CPU** for recon, joins, streaming extraction and descriptive
  analysis.
- Escalate an exact pass to **Ibex** only when a representative smoke test predicts
  >2 hours wall-clock locally, memory does not fit, or the registered resource exists only
  on Ibex.
- No GPU is required for the core Stage-1 task.
- Before a full corpus pass, measure throughput on a representative, length/source-stratified
  slice. The measured estimate becomes the run estimate.
- Hard stop at **2× the measured estimate**; diagnose rather than push through.

No package is installed merely because the first environment lacks it. Check registered
environments/resources first.

## 9. Autonomy envelope

**Auto-proceed:** `true`.

**Compute budget**

| | budget |
|---|---|
| CPU-hours | `100` |
| GPU-hours | `0` |
| max single job | `6` hr |
| review rounds per gate | `3` |

### Decide alone and continue

Inside the budget and write boundaries, ARIS may without asking:

- inspect all registered prior work;
- classify prior artifacts as reusable / re-derive / obsolete / unknown;
- port or rewrite old scripts into scratch after documenting what changed;
- choose section ordering and report layout using the established house style;
- add QC flags or retained columns needed by downstream tasks;
- retain ambiguous/missing/unusual records rather than force a classification;
- choose borg versus Ibex from the measured compute rule above;
- compute additional descriptive checks when they are needed to validate a planned table;
- drop a weak/redundant figure from the report or add a better one when its underlying
  measurement is already in scope;
- log surprises and propose biological interpretations without declaring them established.

Do **not** stop for approval merely to propose report sections. The previous launcher did;
this one is intended to run unattended.

### Human gate — stop and wait

Only stop for:

- modifying/deleting/replacing canonical raw data or ground truth;
- changing the project claim wording or scientific question;
- choosing a new hard biological filter that would delete observations from the canonical
  representation rather than flag/stratify them;
- exceeding the compute budget;
- moving/adopting a new governance revision;
- promoting a proposed interpretation to a thesis/paper claim;
- publishing or sending material outside the project.

### Required downstream preservation

Before Stage 1 closes, verify that the canonical representation retains the fields required
by the known downstream tasks: RT0–RT7/domain analysis, neighbourhood/operon analysis,
diversity/saturation, taxonomic/ecological distribution, annotation disagreement and
RT–ncRNA co-evolution. See `data/README.md` for the retained-field contract.
