---
task_id: T-REG-asset-registration
stage_id: S00
title: Register the discovered asset base
state: AUTHORIZED
autonomy_tier: B
compute_class: ZERO
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-REG-asset-registration
branch: task/T-REG-asset-registration
output_directory: docs/, data/
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
| a deliberately renamed directory | negative | the manifest hash changes, so drift is detectable | the identity pin is useless |
| re-run determinism | baseline | two runs give identical hashes | — |

## Reachability
Attainable; the sweep already produced its output.

## Method
For each collection, add a registry row with path, kind, file count, bytes, manifest hash, and a
**category**: `ASSET` (reusable after hashing), `BOUNDED_NEGATIVE` (inherit as a design constraint),
or `UNVERIFIED_CONCLUSION` (re-derive before any citation). Categorisation of a collection containing
analysis outputs is tier B and goes to review, not to the task.

## Endpoint and criterion
- primary endpoint: registry rows covering every collection above a declared size floor
- **falsification criterion:** none; this is bookkeeping
- **death condition:** none; the sweep becomes a scheduled recurring check

## Outputs
Registry rows in `data/README.md` and `docs/DATASET_REGISTRY.md`; `docs/ASSET_CATEGORIES.tsv`.

## What this task may NOT conclude
Anything scientific. It may not promote a prior number by registering the file that contains it.
