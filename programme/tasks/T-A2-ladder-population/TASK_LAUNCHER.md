---
task_id: T-A2-ladder-population
stage_id: S10
title: Counterfactual ladder on a fixed common population
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A2-ladder-population
branch: task/T-A2-ladder-population
output_directory: analysis/t_a2_ladder_population/
hard_dependencies: []
populations_touched: ["PAIR-ELIG: inspected (already exhausted)"]
iteration_budget: 1
claim_ids_touched: ["C-29", "C-39"]
---

# T-A2 · Counterfactual ladder on a fixed common population

## Question
Does the counterfactual effect decay monotonically as the control tightens, or does the reported
shape come from evaluating four tiers on four different component populations?

## Hypothesis
The shape is partly a population artefact. Alternative: the ladder is monotone on a fixed population
and the published description stands.

## Why existing evidence does not answer it
Tier populations are C1 1,019, C2 832, C3 1,073 and C4 **451** components, and C4 contains **zero**
of the 581 singleton components, so it is structurally the large-component subset. The published
"~10-fold decay" compares non-identical sets. **Registry lookup:** none.

## Population and inferential unit
- population: the components present in **all four** tiers (expected ≈ 423), with full-population
  figures retained alongside
- inferential unit: component, with the pair-weighted view reported beside it
- dependence structure: as T-A0

## Inputs
X2 component export; `tables/COUNTERFACTUAL_EFFECTS.tsv` from the same bundle.

## Forbidden inputs
The pair-level export as an inference file.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| full-population ladder | baseline | reproduces the published C1–C4 values exactly | the reader is wrong; stop |
| tier membership counts | positive | reproduces 1,019 / 832 / 1,073 / 451 | stop |
| singletons in C4 | negative | is zero, confirming the structural exclusion | the population claim is wrong; stop |

## Reachability
Attainable for any input.

## Method
Intersect tier memberships; recompute each tier's component-level and pair-weighted mean on the
common set; report both alongside the full-population values.

## Endpoint and criterion
- primary endpoint: the four tier means on the common population
- **falsification criterion:** if the common-population ladder is monotone, the current wording stands
  and this task returns FAIL for its own hypothesis
- **death condition:** none

## Expected result patterns
| pattern | reading |
|---|---|
| non-monotone, collapse at C3 | near-neighbour counterfactuals abolish the effect; C4 is a different population, not a tighter control |
| monotone | the published description is correct and this objection is withdrawn |

## Outputs
`tables/A2_common_population_ladder.tsv`, `tables/A2_tier_membership.tsv`

## What this task may NOT conclude
Whether pair-level discrimination exists. It describes the shape of an existing measurement.
