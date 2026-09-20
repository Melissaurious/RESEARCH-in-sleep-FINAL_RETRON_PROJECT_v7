---
task_id: T-LINT2-prose-numbers-gated
inherits_record_of: T-LINT-prose-numbers
governance_base: b5443e1
base_commit: 94a1a78
stage_id: S00
title: Numeric-provenance triage linter, control-gated and mutation-tested
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-LINT2-prose-numbers-gated
branch: task/T-LINT2-prose-numbers-gated
output_directory: analysis/t_lint2_prose_numbers_gated/
hard_dependencies: []
populations_touched: []
population_state: NO_POPULATION_SPEND
confirmatory_spend: none
iteration_budget: 1
claim_ids_touched: []
frozen: true
---

# T-LINT2 · Numeric-provenance triage linter, control-gated and mutation-tested

**This is a new task, not an edit.** Under `TASK_PROTOCOL.md` §4 a changed criterion is a new task
that inherits the old one's record. T-LINT-prose-numbers stays `REVIEW_FAILED` on the board with
its artifacts intact; this task inherits its record and replaces its control architecture.

## Why it exists

Independent review found two defects in T-LINT, both of which this task must fix and neither of
which requires an operator decision:

1. **Controls were evaluated after the primary outputs were written.** `lint_prose_numbers.py:545`
   writes `LINT_UNRESOLVED.tsv` before the `---- CONTROLS ----` block begins. A failing control
   could not have prevented the corpus output from existing.
2. **The positive control could not fail.** Its pass condition was *"value V appears with a status
   in `UNRESOLVED`/`COINCIDENTAL_MATCH`"* — that is, with **either** of the only two statuses the
   tool can emit. It therefore tested token visibility, not defect discrimination. A third defect
   follows: `NEG_no_resolved_status` was hard-coded `PASS` and could not produce a `FAIL` row in a
   completed run.

## What is unchanged, and must stay unchanged

The **preregistered token rule, masking rules, exclusion vocabulary, status vocabulary, index scope
and mode A/B separation of T-LINT 1.0.1 are carried over verbatim**, by importing the frozen module
and calling its functions rather than by copying them. A control battery is only meaningful if the
thing under test is the same thing. Any divergence in the token rule would make the two runs
incomparable and would be a new method, not a repaired one.

`assert_vocabulary()` and the two-status vocabulary stand: numeric equality is not provenance, and
the tool still has no status meaning "resolved".

## Question

Does the triage instrument (a) flag the known numeric-provenance defects, (b) distinguish a value
absent from the index from a value coincidentally equal to an unrelated cell, and (c) refuse to
emit primary outputs when either property fails?

## Hypothesis

The instrument satisfies (a)–(c). Alternative: it does not, in which case it emits no primary
output and reports `VOID`.

## Execution order — BINDING

The script must execute in exactly this order, and the order is itself a checked property:

```
  phase 1  fixture construction      (self-contained, inside output_directory)
  phase 2  fixture control battery   (BLOCKING)
  phase 3  mutation battery          (BLOCKING)
  phase 4  GATE 1 -- abort if any phase-2/3 blocking control is not PASS
  phase 5  corpus scan, IN MEMORY, nothing written
  phase 6  corpus recall + false-positive controls  (BLOCKING)
  phase 7  GATE 2 -- abort if any phase-6 blocking control is not PASS
  phase 8  write primary outputs
```

⛔ **No primary table may exist on disk if any blocking control is not `PASS`.** On abort the
script writes `LINT_CONTROL_CHECKS.tsv` and `VOID` and exits non-zero. A run log records the
wall-clock timestamp at the end of each phase, so the ordering is auditable from the artifact and
not only from the source.

## Controls — every one must be able to fail

### Phase 2 · seeded fixture, ground truth by construction

A fixture corpus is built inside `output_directory` with a **known** correct answer per token.

| control | type | expectation — a SPECIFIC status, not "either" |
|---|---|---|
| `FIX_POS_unmatched` | positive | every seeded value present in the fixture document and in **no** fixture table comes back **exactly `UNRESOLVED`** |
| `FIX_POS_matched` | positive | every seeded value present in the fixture document and **also** a cell of an unrelated fixture table comes back **exactly `COINCIDENTAL_MATCH`** |
| `FIX_NEG_ineligible` | negative | every seeded ineligible token (small integer, ISO date, clock time, URL, sha, path, `§`/Table/Figure reference) is **absent** from the output and is counted under its **named** exclusion reason |
| `FIX_DISCRIMINATION` | positive | the fixture output contains **both** statuses. An instrument that returns one status for everything is not discriminating, whichever status it is |
| `FIX_VOCABULARY` | negative | **no emitted row** carries a forbidden status token. This is checked against produced rows, not against the constant tuple |

`FIX_POS_unmatched` and `FIX_POS_matched` fail in opposite directions, so no single degenerate
resolver can satisfy both.

### Phase 3 · adversarial mutation battery

The phase-2 battery is run against deliberately broken variants of the instrument. **Each mutant
must be caught** — at least one phase-2 blocking control must return `FAIL`. A mutant that passes
the battery proves the battery is non-discriminating, and the task is `VOID`.

| mutant | what it breaks | which control must catch it |
|---|---|---|
| `M1_resolver_blind` | resolver returns no match, ever | `FIX_POS_matched` |
| `M2_resolver_promiscuous` | resolver matches every query | `FIX_POS_unmatched` |
| `M3_token_rule_off` | eligibility always false | `FIX_POS_*` (no rows at all) |
| `M4_mask_off` | date/time/URL/hash masking disabled | `FIX_NEG_ineligible` |
| `M5_forbidden_status` | emits the status `RESOLVED` | `FIX_VOCABULARY` |

⚠️ **This is the control on the controls, and it is the part T-LINT did not have.** It answers the
question "could this battery ever have failed?" with an executed demonstration rather than an
assertion.

### Phase 6 · real corpus

| control | type | blocking | expectation |
|---|---|---|---|
| `COR_POS_recall` | positive | YES | each of the three named known defects is flagged in the corpus output. Recall is necessary, not sufficient; phase 2 supplies the sufficiency |
| `COR_NEG_false_positive` | negative | YES | three values that provably **are** cells of landed tables under `results/` and are also asserted in tracked markdown carry **zero** `UNRESOLVED` rows |
| `COR_BASE_queue` | baseline | NO | the full adjudication queue is reported, both statuses, not the `UNRESOLVED` subset alone |

> **Why `COR_POS_recall` is recall-only and stays blocking.** The expected *status* of a real-corpus
> defect depends on whether some unrelated landed table happens to contain the same number, which
> is a property of the corpus and not of the instrument. Demanding a specific status here would be
> a criterion fitted to the corpus. The specific-status requirement therefore lives on the fixture,
> where ground truth is constructed, and the corpus control asserts only what is legitimately
> assertable: the defect must not go unreported.

## Reporting requirement — corrects a stated defect

The primary count reported is the **full adjudication queue**, with its split. T-LINT's synthesis
reported 633 and the review correctly noted the table holds 9,471 rows, of which 8,838 are
`COINCIDENTAL_MATCH` and require adjudication under the tool's own definition. The report names
the total first and the split second.

## Inputs

| input | path | role |
|---|---|---|
| frozen instrument | `…-T-LINT-prose-numbers/analysis/t_lint_prose_numbers/scripts/lint_prose_numbers.py` | imported, **never edited**; hash pinned |
| corpus | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis` | read-only |

## Forbidden

Editing the frozen instrument. Writing anywhere but `output_directory`. Changing the token rule,
the exclusion vocabulary or the status vocabulary. Reporting `UNRESOLVED` alone as the queue size.

## Outputs

`tables/LINT2_CONTROL_CHECKS.tsv`, `tables/LINT2_MUTATION_BATTERY.tsv`,
`tables/LINT2_FIXTURE_ROWS.tsv`, `tables/LINT2_UNRESOLVED.tsv`,
`tables/LINT2_UNRESOLVED_MODE_B.tsv`, `tables/LINT2_QUEUE_SUMMARY.tsv`,
`tables/LINT2_PHASE_ORDER.tsv`, `logs/run_log.json`, `controls/fixture/`

## Endpoint and criterion

- primary endpoint: the state of the blocking control battery
- **criterion:** the instrument is admissible **iff** every phase-2, phase-3 and phase-6 blocking
  control is `PASS`. Otherwise `TASK_STATE=VOID` and no primary table is written
- **death condition:** a mutant survives the battery

## What this task may NOT conclude

Anything about whether any flagged number is actually wrong. This is triage. Adjudication is a
separate step against the declared-source schema, and that schema stays specified and unpopulated.
