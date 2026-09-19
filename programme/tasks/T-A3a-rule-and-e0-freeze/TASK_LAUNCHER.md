---
task_id: T-A3a-rule-and-e0-freeze
governance_base: b5443e1
stage_id: S00
title: Freeze the confirmatory rule and the exposure set E0
state: AWAITING_ADOPTION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A3-confirmatory-population
branch: task/T-A3-confirmatory-population
output_directory: analysis/t_a3a_rule_and_e0_freeze/
hard_dependencies: []
populations_touched: ["defines E0; touches no endpoint and assigns no candidate population"]
iteration_budget: 1
claim_ids_touched: []
---

# T-A3a · Freeze the confirmatory rule and the exposure set E0

**Supersedes the withdrawn `T-A3`, which asked to assign "any future pairing population" and was
therefore not a bounded, reproducible task.** That launcher is split: this one freezes the rule and
the exposure set, which can run today. A separate `T-A3b-<population-name>` instantiates the rule on
one named, hash-pinned candidate population, and is written when such a population exists.

## Why this is a task and not a decision
The **rule** is tier C: the operator adopts it once. **Executing** it is tier A and fully
deterministic. Once adopted, this task needs no human ever again and reproduces byte-identically.

## Question
What exactly is the exposure set E0, and what is the frozen, machine-checkable rule by which any
future candidate pairing population will be split?

## THE RULE — frozen text, applied verbatim, never re-derived

1. **E0, the exposure set.** Every sequence used by the retrieval gate, X1 or X2 during model
   development is E0. **No member of E0 may ever be called untouched confirmation of those
   analyses.** X2 cross-fitted all five folds, so all of PAIR-ELIG is in E0.
2. **Leakage components.** Candidate pairs are grouped by sequence-only edges:
   - RT edge at **>= 50% amino-acid identity over >= 80% coverage**;
   - ncRNA edge at **>= 80% nucleotide identity over >= 80% coverage**;
   - exact duplicates and copies of the same biological pair are always connected.
3. **Assignment, exactly specified.** Deterministic and component-level. Compute
   `h = SHA256(component_id + "PAIR_CONFIRMATORY_V1_2026-09-20")`, take the first 8 bytes as a
   big-endian unsigned integer `u`, and assign `CONFIRMATORY` if and only if
   `u < floor(0.20 * 2**64)`, otherwise `DEVELOPMENT`. No rounding to "approximately 20%", no RNG,
   no reseeding. `component_id` is the sorted, newline-joined list of member pair identifiers, hashed;
   its construction is frozen by this task and emitted as code.
4. **Ordering.** Assignment happens **before** any model score, endpoint or component composition is
   inspected. No rebalancing after inspection, ever.
5. **Near and far, with distances.** Report `CONFIRMATORY_NEAR` and `CONFIRMATORY_FAR` separately.
   **FAR** means no RT edge **and** no ncRNA edge to any member of E0 *under the declared thresholds*.
   ⚠️ FAR is **not** biological independence. Remote homology below the thresholds remains. Always
   report the **continuous nearest-neighbour identity and distance to E0** for every component, on
   both modalities, alongside the categorical label.
6. **Sealing.** Once frozen, confirmatory components may not influence feature selection,
   architecture, thresholds, stopping rules, hyperparameters or error analysis. They are opened
   **once**, after the relevant analysis is frozen.
7. **Honesty clause.** If no adequate prospective population exists, the follow-up is reported as
   **lacking confirmatory evidence**. An untouched set is never manufactured retrospectively.
8. **The FAR adequacy criterion.** The operator declares, **with the rule and before any candidate
   composition is inspected**, the minimum `|CONFIRMATORY_FAR|` required, tied to the inferential
   precision the follow-up intends to claim rather than to a round number. Below it, the follow-up is
   reported as lacking distant confirmation.

## Scope of this task
Produce the E0 manifest, the frozen component-ID algorithm as executable code, the fixed thresholds,
the exact hash interval, the salt, the declared FAR adequacy criterion, and the adoption record.
**Assign nothing.** There is no candidate population yet.

## Inputs
The frozen split manifest and cluster assignments from the existing embedding gates; the exact RT and
ncRNA catalogues.

## Forbidden inputs
Any model score, endpoint value or per-component composition summary. Reading one voids the rule
irreversibly.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| determinism | **positive** | two independent runs of the component-ID and hash code give byte-identical output | the algorithm is not stable; VOID |
| hash interval calibration | **positive** | on 10^6 synthetic component ids the assignment rate matches 0.20 within Monte Carlo error | the interval arithmetic is wrong; VOID |
| E0 containment | **positive** | every PAIR-ELIG pair lands in E0 | the exposure set is wrong; VOID |
| edge-direction fixture | **negative** | a synthetic component with no edge to E0 is never labelled NEAR, and one with a planted edge is never labelled FAR | the edge test is inverted; VOID |
| ordering audit | **positive** | no endpoint file was opened before the freeze timestamp | the rule is void; escalate |

## Reachability
Attainable. This task produces a specification and a manifest; there is no branch that cannot fire.

## Endpoint and criterion
- primary endpoint: the frozen rule artifacts and the E0 manifest
- **falsification criterion:** none; this task tests no hypothesis
- **death condition:** none

## Outputs
`tables/A3a_E0_manifest.tsv`, `scripts/component_id.py`, `tables/A3a_hash_calibration.tsv`,
`tables/A3a_controls.tsv`, `A3A_FROZEN.md` carrying the rule text, the thresholds, the salt, the
hash interval, the FAR adequacy criterion and the adoption record.

## What this task may NOT conclude
Anything scientific. It may not assign a candidate population, and it may not choose the rule it
executes.
