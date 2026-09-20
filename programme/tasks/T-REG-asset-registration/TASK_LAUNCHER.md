---
task_id: T-REG-asset-registration
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S00
title: Register the discovered asset base
state: AUTHORIZED
autonomy_tier: B
compute_class: ZERO
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-REG-asset-registration
branch: task/T-REG-asset-registration
output_directory: analysis/t_reg_asset_registration/
hard_dependencies: []
populations_touched: []
iteration_budget: 1
---

# T-REG · Register the discovered asset base

## Question
What scientific assets exist across every project root, and which of them is an asset, a bounded
negative, or an unverified conclusion?

## Why this exists
The declared project was nine git worktrees. The real evidence base is **155.6 GB in 20,765
collections across eight roots**: 44,608 structures, 520 trees, 15,427 profiles, 1,059,907
matrix/embedding files, 406 PDFs. The registries list almost none of it. **Four review conclusions
reversed on discovering this**, and a fifth is pending.

## Population and inferential unit
- population: every collection in `review-stage/ASSET_SWEEP.tsv`
- inferential unit: asset collection

## Inputs
`review-stage/ASSET_SWEEP.tsv`; `review-stage/tools/asset_sweep.py`; `data/README.md`;
`docs/DATASET_REGISTRY.md`.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| already-registered assets | positive | the sweep finds the 62-chain structure register and the CATH benchmark, which ARE registered | the sweep has a blind spot |
| a renamed directory **in a throwaway fixture** | negative | the manifest hash changes, so drift is detectable. Never mutate the real asset base to test a control | the identity pin is useless; VOID |
| re-run determinism | baseline | two runs give identical hashes | — |

## Reachability
Attainable; the sweep already produced its output.

## Method
For each collection, add a registry row with path, kind, file count, bytes, manifest hash, and a
**category**: `ASSET` (reusable after hashing), `BOUNDED_NEGATIVE` (inherit as a design constraint),
or `UNVERIFIED_CONCLUSION` (re-derive before any citation). Categorisation of a collection containing
analysis outputs is tier B and goes to review, not to the task.

## Endpoint and criterion
- primary endpoint: **proposed** registry rows for every collection of at least **1 MiB or at least
  10 files**, whichever is met first. Smaller collections go in an appendix table, never omitted
- **falsification criterion:** none; this is bookkeeping
- **death condition:** none; the sweep becomes a scheduled recurring check

## Outputs
**This task does not write to `docs/` or `data/`.** It emits *proposed* rows inside its own output
directory: `tables/REG_proposed_registry_rows.tsv`, `tables/REG_asset_categories.tsv`,
`tables/REG_controls.tsv`. A **tier-B review step** merges accepted rows into the canonical registries.
This separates registration from promotion and avoids merge collisions with concurrent sessions.

Category assignment is **tier B**: file existence is factual, scientific category is interpretive.
Propose, do not decide.

## What this task may NOT conclude
Anything scientific. It may not promote a prior number by registering the file that contains it.
