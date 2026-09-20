---
task_id: T-GATE1-consumption-gate
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S00
title: Implement the consumption gate end-to-end against landed reports, hashes and declared outputs
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-GATE1-consumption-gate
branch: task/T-GATE1-consumption-gate
output_directory: analysis/t_gate1_consumption_gate/
hard_dependencies: []
populations_touched: []
population_state: NO_POPULATION_SPEND
confirmatory_spend: none
iteration_budget: 2
claim_ids_touched: []
io_class: IO_LOW
frozen: true
---

# T-GATE1 · The consumption gate, end to end

## Why it exists

The independent review's finding, quoted:

> *"It does not prove an operational consumption gate. The function accepts caller-supplied state,
> outcome and consumable lists in `preflight.py:184`, and it is called only by the unit tests. It
> does not read a signed task report, verify controls, verify artifact hashes, or mediate actual
> downstream file access."*

And the coordinator's acceptance of it:

> *"I described a gate; I shipped a function."*

**Consequence today: any artifact from a self-labelled `PASS` task is consumable, regardless of
whether the `PASS` was earned.** That is the hole this task closes.

## Question

Can a downstream task be mechanically prevented from reading an artifact whose producing task is
not in a valid terminal state, whose declared outputs do not hash to their recorded values, or which
is not on that producer's `CONSUMABLE_OUTPUTS` list?

## Hypothesis

Yes, by a gate that reads the landed **task report** rather than caller-supplied arguments.
Alternative: the reports do not carry enough structure to gate on, in which case the task reports
exactly which fields are missing and stops. **That is a successful task with a negative result.**

## What the gate must actually do

Six checks, in order, each of which can refuse:

1. **Locate the producing task's report** from the artifact path. No report ⇒ refuse.
2. **Parse `TASK_STATE` and `SCIENTIFIC_OUTCOME`** from the report, not from an argument.
3. **Refuse if `TASK_STATE` ∉ {`PASS`}.** ⚠️ **And allow every `SCIENTIFIC_OUTCOME`.** A refuted
   hypothesis is a successful task; a gate that refuses `FALSIFIED` or `BOUND` would silently
   discard this project's best assets.
4. **Refuse if the artifact is not on the report's `CONSUMABLE_OUTPUTS` list.**
5. **Re-hash the artifact and compare to the report's recorded sha256.** Mismatch ⇒ refuse.
6. **Refuse if the report's preregistration timestamp does not precede its job timestamp.**

It must be callable as a library function **and** as a CLI, and it must be the only supported way a
task reads an upstream artifact.

## Inputs

| input | path | role |
|---|---|---|
| existing helper | `programme/preflight.py`, `consumption_gate()` | the function to replace; read, do not delete |
| landed task reports | whatever `T-AUDIT2` has produced, plus `T-LINT2`'s | the things to parse |
| gate tests | `programme/test_gates.py`, `PREFLIGHT_TESTS.tsv` | FI-07, FI-08, FI-08b already exist; extend, never weaken |

## Forbidden

Weakening or deleting `FI-08` (a valid negative **must** stay consumable). Gating on scientific
outcome. Accepting caller-supplied state in place of a parsed report.

## Controls — run FIRST and BLOCK

| control | type | must show | if it fails |
|---|---|---|---|
| `GATE_POS_valid_negative` | **positive** | a producer with `TASK_STATE=PASS`, `SCIENTIFIC_OUTCOME=FALSIFIED`, matching hash, artifact on the list ⇒ **ALLOW** | the gate discards valid negatives; VOID |
| `GATE_NEG_void_producer` | negative | producer `TASK_STATE=VOID` ⇒ refuse | the hole is not closed; VOID |
| `GATE_NEG_undeclared_artifact` | negative | artifact absent from `CONSUMABLE_OUTPUTS` ⇒ refuse | — |
| `GATE_NEG_hash_mismatch` | negative | artifact mutated after the report ⇒ refuse | the gate pins nothing |
| `GATE_NEG_no_report` | negative | no report ⇒ refuse | self-labelling still works |
| `GATE_MUT_battery` | **adversarial** | for each of the five checks, a mutant that disables **that check** must be caught by **that** control and by no substitute | the battery is non-discriminating; VOID |

⚠️ **`GATE_MUT_battery` is mandatory and is modelled on `T-LINT2`.** A gate whose tests cannot fail
is the same defect as a control whose pass condition is the result. Each mutant declares its
preregistered catcher; a collateral failure does not count as caught.

## Reachability

The `ALLOW` branch is reachable: `T-LINT2`'s report is `TASK_STATE=PASS` with declared outputs and
full sha256 values, so at least one real artifact can pass all six checks. **Verify this before
building**, not after.

## Endpoint and criterion

- primary endpoint: the six checks, each demonstrated to refuse and to allow
- **criterion:** the gate is operational **iff** every control is `PASS` **and** it is wired as the
  only supported read path, demonstrated on at least one real landed artifact
- **death condition:** landed reports lack the fields to gate on ⇒ report which fields, stop,
  `INCONCLUSIVE`, escalate. Do **not** invent a report format and backfill it silently

## Outputs

`tables/GATE_CONTROL_CHECKS.tsv`, `tables/GATE_MUTATION_BATTERY.tsv`,
`tables/GATE_REPORT_FIELD_AUDIT.tsv` (which reports carry which required fields),
`scripts/consumption_gate.py`, `TASK_REPORT.md`

## What this task may NOT conclude

Anything scientific. It builds a mechanism. **It does not promote anything, and a gate passing is
not evidence that a result is correct** — only that its producer was valid and its bytes are the
ones that were reported.
