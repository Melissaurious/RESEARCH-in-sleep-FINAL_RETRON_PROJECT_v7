---
task_id: T-LINT-prose-numbers
stage_id: S00
title: Numeric provenance linter over prose
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-LINT-prose-numbers
branch: task/T-LINT-prose-numbers
output_directory: analysis/t_lint_prose_numbers/
hard_dependencies: []
populations_touched: []
iteration_budget: 2
claim_ids_touched: []
---

# T-LINT · Numeric provenance linter over prose

## Question
Which numbers asserted in this project's markdown documents cannot be resolved to a cell in any
landed canonical table?

## Hypothesis
A non-trivial number cannot be resolved, including at least three already identified by hand.

## Why existing evidence does not answer it
No such check exists. Existing provenance discipline covers tables and figures; **all four
propagating errors found by review lived in prose or in a script string literal.**

## Population and inferential unit
- population: every tracked `.md` in the repository and in `PROJECT_REVIEW_PACKAGE/`
- inferential unit: a distinct numeric token in prose

## Inputs
All tracked `.md`; all `.tsv` under `results/` and the registered bundle paths, as the resolution index.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| three known defects | positive | the linter flags the same-strand figure, the matrix dimension, and the superseded silhouette | the linter cannot see what it exists to see; fix before trusting any output |
| three known-good numbers | negative | numbers that provably come from landed tables are NOT flagged | the false-positive rate makes it unusable |
| resolution rate per file | baseline | reported, so the operator can judge the signal | — |

## Reachability
The PASS outcome is a defect list, which is attainable. Note the positive control is the design
constraint: a linter that cannot find the three known cases is void regardless of what else it finds.

## Method
Extract numeric tokens with at least three significant digits or a decimal point, to avoid matching
small integers. Build a set of all numeric tokens present in landed tables. Report unresolved tokens
per file with surrounding context. Do not attempt automatic correction.

## Endpoint and criterion
- primary endpoint: count and list of unresolved numeric assertions
- **falsification criterion:** if the positive control does not flag all three known defects, the
  instrument is void and no output may be acted on
- **death condition:** none; this becomes a standing check

## Expected result patterns
| pattern | reading |
|---|---|
| finds the three, plus others | the check works; the others become an errata queue |
| finds the three, nothing else | the prose is cleaner than feared; keep the check as a gate |
| high false-positive rate | tighten the token rule and re-run, within the iteration budget of 2 |

## Outputs
`scripts/lint_prose_numbers.py`, `tables/LINT_UNRESOLVED.tsv`, `tables/LINT_CONTROL_CHECKS.tsv`

## What this task may NOT conclude
That a flagged number is wrong. Unresolved means unresolved. Adjudication is a separate errata step.
