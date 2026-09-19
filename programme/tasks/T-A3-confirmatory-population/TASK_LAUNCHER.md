---
task_id: T-A3-confirmatory-population
stage_id: S00
title: Freeze the pairing confirmatory population
state: AWAITING_ADOPTION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A3-confirmatory-population
branch: task/T-A3-confirmatory-population
output_directory: analysis/t_a3_confirmatory_population/
hard_dependencies: []
populations_touched: ["defines E0 and freezes the split; touches no endpoint"]
iteration_budget: 1
claim_ids_touched: []
---

# T-A3 · Freeze the pairing confirmatory population

## Why this is a task and not a decision — read this first

The **rule** below is tier C: the operator declares it, and no task may choose it. **Executing** the
rule is tier A: it is deterministic by construction, uses SHA256 with a fixed salt and no random
number generator, and needs no human once the rule is adopted.

**This launcher carries the rule in full.** Once the operator marks it adopted, the board state moves
`AWAITING_ADOPTION → AUTHORIZED` and every later run of this task is fully autonomous and reproduces
byte-identically. The human writes nothing again.

## Question
Which components of any future pairing population may serve as confirmation, and which are already
exposed?

## THE RULE — frozen text, applied verbatim, never re-derived

1. **E0, the exposure set.** Every sequence used by the retrieval gate, X1, or X2 during model
   development is E0. **No member of E0 may ever be called untouched confirmation of those
   analyses.** X2 cross-fitted all five folds, so all of PAIR-ELIG is in E0.
2. **Leakage components.** Candidate pairs are grouped by sequence-only edges:
   - RT edge at **≥ 50% amino-acid identity over ≥ 80% coverage**;
   - ncRNA edge at **≥ 80% nucleotide identity over ≥ 80% coverage**;
   - exact duplicates and copies of the same biological pair are always connected.
3. **Assignment.** Component-level and deterministic, `SHA256(component_id + salt)`, salt
   `PAIR_CONFIRMATORY_V1_2026-09-20`, lowest ~20% of the hash space to `CONFIRMATORY`, remainder to
   `DEVELOPMENT`.
4. **Ordering.** Assignment happens **before** any model score, endpoint or component composition is
   inspected. No rebalancing after inspection, ever.
5. **Near and far.** Report `CONFIRMATORY_NEAR` and `CONFIRMATORY_FAR` separately. **FAR** means no
   declared RT edge **and** no declared ncRNA edge to any member of E0.
6. **Sealing.** Once frozen, confirmatory components may not influence feature selection,
   architecture, thresholds, stopping rules, hyperparameters or error analysis. They are opened
   **once**, after the relevant analysis is frozen.
7. **Honesty clause.** If no adequate prospective population exists, the follow-up is reported as
   **lacking confirmatory evidence**. An untouched set is never manufactured retrospectively.

## THE FIRST OUTPUT, AND IT BLOCKS

⚠️ **Report `|CONFIRMATORY_FAR|` before anything else, and stop there if it is below a floor the
operator declares with the rule.**

Rationale, measured: **100% of held-out pairs in the existing split were reachable from training by
at least one modality**, and 82.46% of held-out RTs had a ≥ 0.50-identity training relative. A far
set that comes back empty or tiny is therefore the expected outcome and **is itself the finding**: it
means distant confirmation is not obtainable from this corpus at all, and every future pairing claim
must say so in advance rather than discover it at review.

## Population and inferential unit
- population: any candidate pairing population presented for confirmation, plus E0 for the edge test
- inferential unit: leakage component

## Inputs
The frozen split manifest and cluster assignments from the existing embedding gates; the exact RT and
ncRNA catalogues; any new candidate pairs offered for confirmation.

## Forbidden inputs
Any model score, endpoint value, or per-component composition summary. Reading one before assignment
voids the split irreversibly.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| determinism | positive | two independent runs give byte-identical assignments | the salt or the component id is not stable; stop |
| E0 containment | positive | every PAIR-ELIG pair lands in E0 | the exposure set is wrong |
| edge symmetry | negative | a pair with no edge to E0 is never labelled NEAR | the edge test is inverted |
| ordering audit | baseline | no endpoint file was opened before the assignment timestamp | the split is void; escalate |

## Reachability
Both outcomes attainable. An empty FAR set is a valid and expected result, not a failure.

## Endpoint and criterion
- primary endpoint: the frozen assignment table, plus `|CONFIRMATORY_NEAR|` and `|CONFIRMATORY_FAR|`
- **falsification criterion:** none; this task freezes a population, it tests no hypothesis
- **death condition:** if `|CONFIRMATORY_FAR|` is below the declared floor, pairing follow-ups are
  reported as lacking distant confirmation, permanently, unless a new population is acquired

## Outputs
`tables/A3_component_assignment.tsv`, `tables/A3_near_far_counts.tsv`, `tables/A3_E0_manifest.tsv`,
`tables/A3_controls.tsv`, `A3_FROZEN.md` with the rule text and its adoption record

## What this task may NOT conclude
Anything scientific. It may not evaluate a model, and it may not adjust the split to make any later
result come out better.
