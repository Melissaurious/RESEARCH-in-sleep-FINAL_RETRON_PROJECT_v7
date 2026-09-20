---
task_id: T-AUDIT1-circular-control-sweep
governance_base: 9a793c9
base_commit: 94a1a78
stage_id: S00
title: Sweep every blocking control in the programme for circularity and non-discrimination
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-AUDIT1-circular-control-sweep
branch: task/T-AUDIT1-circular-control-sweep
output_directory: analysis/t_audit1_circular_control_sweep/
hard_dependencies: []
populations_touched: []
population_state: NO_POPULATION_SPEND
confirmatory_spend: none
iteration_budget: 1
claim_ids_touched: []
io_class: IO_LOW
frozen: true
---

# T-AUDIT1 · What broken instrument does this control catch?

## Why it exists

The Batch One reviewer's generalisation, which the coordinator asked to be kept because it
generalises:

> *"A positive control whose pass condition is the headline result is not a control. That is
> T-A23's POS-a, and the same shape should be looked for everywhere else in this programme."*

And its sibling, learned the hard way in `T-LINT2` and recorded in
`tasks/T-LINT2-prose-numbers-gated/VOID_02_second_review_rejected.md`:

> *"A catcher chosen after watching the mutant escape is not a preregistered catcher."*

**This task looks for both shapes everywhere, and it is cheap.**

## Question

For every control declared **blocking** anywhere in this programme: what specific broken instrument
would it catch, and is there a broken instrument it would **not** catch that it is widely assumed to?

## Hypothesis

Some blocking controls in this programme cannot fail, or can only fail for reasons unrelated to what
they are believed to check. Alternative: all of them discriminate, which would be a genuinely
reassuring negative result.

## Scope — enumerate, do not sample

Every blocking control in:

| source | what to read |
|---|---|
| landed control tables | `A0_control_checks.tsv`, `A2_controls.tsv`, `REG_controls.tsv`, `A23_controls.tsv`, `LINT_CONTROL_CHECKS.tsv`, `LINT2_CONTROL_CHECKS.tsv` |
| launchers | every `programme/tasks/*/TASK_LAUNCHER.md` control table |
| gate tests | `programme/PREFLIGHT_TESTS.tsv`, `programme/test_gates.py` |

## Classification — one row per control, and the classes are fixed here

| class | meaning |
|---|---|
| `DISCRIMINATING` | a specific broken instrument is named **and** would be caught |
| `CIRCULAR` | its pass condition **is**, or is a large part of, the headline result |
| `NON_DISCRIMINATING` | it accepts every outcome the instrument can emit, so it cannot distinguish |
| `TAUTOLOGICAL` | hard-coded, or asserts a constant rather than an observation |
| `SHADOWED` | a second rule produces the same observable, so this control cannot isolate its own target |
| `UNAUDITABLE` | ordering or provenance cannot be established from the artifact |
| `POST_HOC_CATCHER` | the control-to-defect mapping was decided **after** observing a failure |

Four are already known and are the **seeded positives** for this task's own control:

| known instance | class | source |
|---|---|---|
| T-A23 `POS-a` | `CIRCULAR` | Batch One verdict |
| T-LINT `NEG_no_resolved_status` | `TAUTOLOGICAL` | Batch One verdict |
| T-LINT positive controls (status ∈ {either}) | `NON_DISCRIMINATING` | Batch One verdict |
| T-LINT2 `FIX_NEG_mask[URL]` | `SHADOWED` | `VOID_02`, verified against the frozen tokeniser |

## Controls — run FIRST and BLOCK

| control | type | must show | if it fails |
|---|---|---|---|
| `AUD_POS_seeded_known` | **positive** | the sweep independently classifies **all four** known instances above into their **named** class, without being told which controls they are | the classifier does not detect the shape it exists to detect; VOID |
| `AUD_NEG_known_good` | **negative** | T-A2's three controls and T-A0's `C1_implementation_reproduction` are classified `DISCRIMINATING` | the classifier calls everything circular, which is as useless as calling nothing circular; VOID |
| `AUD_BASE_coverage` | baseline | every blocking control in scope appears exactly once, and the count is reconciled against the source tables | — |

⚠️ **`AUD_POS_seeded_known` is the whole task's own answer to its own question.** It could fail: a
classifier that merely counts keywords would miss the `SHADOWED` case, which is only visible by
reasoning about two rules interacting.

## Reachability

Both branches are reachable: classifications exist for every control either way, and "all
discriminating" is a legitimate, reportable outcome.

## Endpoint and criterion

- primary endpoint: the classification table, complete over the enumerated scope
- **criterion:** the sweep is admissible **iff** `AUD_POS_seeded_known` and `AUD_NEG_known_good`
  both pass
- **death condition:** none — a sweep finding nothing is a result

## Outputs

`tables/AUDIT1_control_inventory.tsv` (one row per blocking control: task, control id, source,
stated expectation, class, the specific broken instrument it would catch, the one it would not),
`tables/AUDIT1_controls.tsv`, `tables/AUDIT1_by_class.tsv`, `TASK_REPORT.md`

## What this task may NOT conclude

**It may not re-classify any task's outcome, withdraw any result, or change any board state.** It
produces an inventory and nominates. A control found `CIRCULAR` does **not** by itself void its
task — that is a judgement for the stage synthesis and the reviewer, and this task's own report must
say so about every row it flags.
