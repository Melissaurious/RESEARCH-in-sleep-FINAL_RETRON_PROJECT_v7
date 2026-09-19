---
task_id: T-A23-crosspair-curation
governance_base: b5443e1
stage_id: S12
title: Literature curation of measured cross-pair outcomes
state: AUTHORIZED
autonomy_tier: B
compute_class: ZERO
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A23-crosspair-curation
branch: task/T-A23-crosspair-curation
output_directory: analysis/t_a23_crosspair_curation/
hard_dependencies: []
populations_touched: []
iteration_budget: 1
claim_ids_touched: ["C-30"]
---

# T-A23 · Literature curation of measured cross-pair outcomes

## Question
How many measured **non-cognate** RT–ncRNA outcomes exist in the published literature, and are there
enough to support any orthogonality endpoint?

## Why this is first in its stage, and why it is cheap
This determines whether stage 12 exists at all, and it is reading rather than compute. The project
register correctly records that no machine-readable swap data exists **in local assets**. That was
read as "no data exists", which is wrong. **Registry lookup:** text extraction over 61 retron PDFs
already on disk finds at least three published cross-pair designs, the largest being a **7 × 7
cognate-versus-non-cognate editing matrix with three biological replicates**, published as a figure
with values not on disk.

## Population and inferential unit
- population: retron engineering, variant-library and swap literature, including the PDFs on disk
- inferential unit: one measured RT × ncRNA combination under one assay

## Inputs
The PDF corpus identified by the asset sweep; any supplementary data recoverable from publishers.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| the three known designs | positive | all three are recovered by the curation procedure | the procedure misses known data and its count cannot be trusted |
| a paper with no cross-pair data | negative | yields zero rows, not spurious ones | the extraction invents rows |
| independent re-read of one paper | baseline | two readers agree on the row count | — |

## Reachability
Attainable; at least three designs are known to exist.

## Method
Build an `RT × ncRNA × assay × outcome × source` matrix. **The primary key must carry
cognate-versus-non-cognate**, because a failed *cognate* pair is a broken element and not an
orthogonality datum, while only a tested *non-cognate* combination is. Record whether each value came
from supplementary data, from text, or was read off a figure, and mark figure-read values as
provisional.

## Endpoint and criterion
- primary endpoint: the curated matrix **plus its geometry**, because a raw cell count misleads. One
  7x7 matrix yields 42 non-cognate cells from **7 RTs, 7 ncRNAs, one study, one assay context**,
  with correlated measurements. That is not 42 independent labels. Report `n_distinct_RTs`,
  `n_distinct_ncRNAs`, `n_retron_systems`, `n_independent_studies`, `n_assay_contexts`,
  `n_experimental_blocks`, `n_positive_cross_reactions`, `n_negative_cross_reactions`,
  `evolutionary_span`
- **falsification criterion:** none. This task curates; it does not judge model eligibility.
- **Stage 12 is NOT gated on a pair count.** Eligibility is a separate tier-B judgement (`T-A23b`)
  made on dataset **geometry and independent blocks**, choosing between descriptive evidence only,
  calibration and sanity checking, a low-capacity supervised endpoint, or no modelling. The rubric
  is declared before A23b runs.
- **death condition:** none; the matrix is valuable at any size

## Expected result patterns
| pattern | reading |
|---|---|
| tens of combinations recovered with values | enough to calibrate and sanity-check, not to train; stage 12 remains gated |
| designs found, values not obtainable | request supplementary data from authors; the panel decision moves up |
| far fewer than expected | the swap panel is the prerequisite and should be planned immediately, as it has the longest lead time in the programme |

## Outputs
`tables/A23_crosspair_matrix.tsv`, `tables/A23_source_provenance.tsv`, `tables/A23_controls.tsv`

## What this task may NOT conclude
That any combination is incompatible. An absent row is absent, never a negative. It also may not
treat a cognate failure as an orthogonality result.
