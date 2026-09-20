---
task_id: T-A16-reciprocal-frame
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S02
title: Reciprocal family-frame analysis of RT core content
state: AWAITING_SPECIFICATION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A16-reciprocal-frame
branch: task/T-A16-reciprocal-frame
output_directory: analysis/t_a16_reciprocal_frame/
hard_dependencies: []
populations_touched: ["exact-RT catalogue: inspected"]
iteration_budget: 1
claim_ids_touched: ["C-04", "C-09"]
---

# T-A16 · Reciprocal family-frame analysis of RT core content

> ⚠️ **AWAITING_SPECIFICATION: name the two positive-control families and their evidence source; name the negative profile and build it by the same procedure; freeze a numerical asymmetry statistic and threshold before execution**

## Question
Is the low retron mapping fraction a property of retron domain content, or of the group-II-seeded
profile the mapper is built on?

## Hypothesis
Predominantly the profile. Alternative: retrons genuinely carry less of the conserved core, which
would make the operator's step-2 parenthetical a biological finding.

## Why existing evidence does not answer it
The one-directional gradient, median mapped fraction 0.94 for group II introns against 0.4933 for
retrons, is confounded by construction. **Registry lookup — and this is the point of the task:** a
reciprocal seven-family table already exists at
`results/rt07_g4a_repaired/tables/g4a_repaired_supported_intersection.tsv`. It shows retrons sharing
**39.2%** of covered positions with all partners against group II introns' **40.0%**, and only **3**
family-private positions out of 260. It was built to select anchor states, has no replicate, no
interval, and no per-sequence version. **It is an asset, not a conclusion.**

## Population and inferential unit
- population: the seven profile families in that table, extended to the full family set in the
  mapper's source sequence file
- inferential unit: profile position for the intersection; exact RT for any per-sequence extension

## Inputs
`results/rt07_g4a_repaired/tables/g4a_repaired_supported_intersection.tsv`;
`results/rt07_g4a_repaired/tables/g4a_repaired_family_selection.tsv`; the mapper's declared sole
sequence input; `results/rt07_g5_catalogue_application/tables/g5_qc_by_family.tsv`.

## Forbidden inputs
The g2 historical-reconstruction set, which was a **declared prohibited input** to the mapper
derivation. Do not reintroduce it.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| two families known to share the core | positive | high reciprocal mapping in both directions | the instrument cannot see sharing where it exists |
| a non-RT profile of similar length | negative | low mapping in both directions | the measure is not specific |
| the existing one-directional gradient | baseline | reproduced, and reported beside the symmetric result | — |

## Reachability
Both outcomes are attainable: symmetry and asymmetry are both measurable on this input.

## Method
Build each family's profile by the same procedure from the same source; compute pairwise reciprocal
mapping; correct for consensus length, which varies from 406 to 1014 across families.

## Endpoint and criterion
- primary endpoint: reciprocal mapping fraction per family pair, length-corrected
- **falsification criterion:** if retron-versus-partner mapping is asymmetric in the same direction
  and magnitude as the one-directional gradient after length correction, the domain-content reading
  survives; if symmetric, the gradient is a frame artefact and may be reported only as such
- **death condition:** a symmetric result permanently closes "retrons lack core domains"

## Expected result patterns
| pattern | reading |
|---|---|
| symmetric | the frame confound is confirmed and strengthened; a clean methodological result for the resource paper |
| asymmetric | a real claim about retron domain content, and a significant finding |

## Outputs
`tables/A16_reciprocal_mapping.tsv`, `tables/A16_length_corrected.tsv`, `tables/A16_controls.tsv`

## What this task may NOT conclude
Where a retron-discriminative signal is. That is T-A18, and it depends on this result.
