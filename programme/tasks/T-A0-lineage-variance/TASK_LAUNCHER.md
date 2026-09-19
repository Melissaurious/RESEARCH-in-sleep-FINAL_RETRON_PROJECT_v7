---
task_id: T-A0-lineage-variance
stage_id: S10
title: Lineage-clustered variance for the X2 decomposition
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A0-lineage-variance
branch: task/T-A0-lineage-variance
output_directory: analysis/t_a0_lineage_variance/
hard_dependencies: []
populations_touched: ["PAIR-ELIG: inspected (already exhausted by embed_x2 cross-fitting; no further depletion possible)"]
iteration_budget: 1
claim_ids_touched: ["C-27", "C-28"]
---

# T-A0 · Lineage-clustered variance for the X2 decomposition

## Question
What is the uncertainty on G−U, G−T, R−G and R−P when the resampling unit respects that 1,075
components sit inside 21 retron types and a smaller number of 50%-identity lineages?

## Hypothesis
The between-lineage variance component is large and currently excluded, so published intervals are
too narrow, most severely for R−G. Alternative: blocking changes little and the intervals stand.

## Why existing evidence does not answer it
Published intervals come from an **equal-weight bootstrap over components**. The bundle's own `n_eff`
column is a formula defect computing `n²/n = n` and reads 1075.0; the index package states 12.5,
which is a Kish figure over *pair* weights describing a different quantity. Neither is the effective
n of the estimator used. **Registry lookup:** no prior work on this; nothing in the asset sweep.

## Population and inferential unit
- population: all 1,075 components in the frozen X2 component export
- inferential unit: component (observation); retron type and RT homolog group (resampling blocks)
- **dependence structure:** components nest inside 21 dominant retron types; token-weighted effective
  type count is 9.3. Largest component holds 18.5% of pairs; 581 of 1,075 are singletons.
- effective n, expected: between 9 and 25 depending on blocking

## Inputs
| input | path | role |
|---|---|---|
| X2 component export (1,075 rows) | `…_v7-embeddings/results/embed_x2_rt_specificity_confirmation/tables/X2_COMPONENT_LEVEL_EXPORT.tsv` | the inference file |
| X2 strata table | same bundle, `tables/SENSITIVITY_STRATA.tsv` | per-stratum comparison |

Hash every input before reading; the bundle carries `HASHES.sha256`.

## Forbidden inputs
The pair-level export. Pair counts overstate sample size by three orders of magnitude and the
registry says never to infer from it.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| G−U under blocking | positive | survives; it is favourable in 86.0% of components | the blocking is too aggressive; report and stop |
| P−T under blocking | negative | loses significance; it is a within-type permutation arm | blocking is not removing the dependence it should |
| existing unclustered intervals | baseline | reproduced exactly before any blocking is applied | the reader is not reading the file correctly; stop |

## Reachability
The PASS outcome is a set of intervals, which is attainable for any input. There is no unreachable
branch.

## Method
Block bootstrap over retron type; separately over RT homolog group; plus a leave-one-type-out
jackknife. Report all three beside the existing unclustered interval. Seed recorded.

## Endpoint and criterion
- primary endpoint: 95% interval on R−G under type-blocked resampling
- **falsification criterion:** if R−G's lineage-blocked interval includes zero, claim C-28 drops to
  UNDERPOWERED and the exact-RT residual leaves the claim set
- **death condition:** none; this task reports intervals either way

## Expected result patterns
| pattern | reading |
|---|---|
| G−U survives, R−G does not | the pairing arm becomes a lineage-dominance result |
| both survive | level 2 is genuinely established, and better supported than currently claimed |
| neither survives | the pairing paper is not viable; the arm becomes a methods-and-bounds chapter |

## Outputs
`tables/A0_blocked_intervals.tsv`, `tables/A0_jackknife.tsv`, `tables/A0_control_checks.tsv`

## What this task may NOT conclude
Anything about biology. It reports intervals. Whether the exact-RT residual is a claim is decided at
stage synthesis, and the operator has been asked to pre-commit to that verdict.
