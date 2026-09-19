# WORKING RULES — sessions, worktrees, parallelism, reporting

**Applies to every task session.** Read with `review-stage/TASK_PROTOCOL.md` (per-task duties) and
`programme/PROGRAM_LAUNCHER.md` (what the programme is for).

---

## 1 · Session model

| role | who | responsibilities |
|---|---|---|
| **coordinating session** | one, on `project-synthesis` | owns `TASK_BOARD.tsv`; authorises tasks; creates worktrees; receives reports; runs the consumption gate; never runs a scientific analysis itself |
| **task session** | one per task, in its own worktree | executes exactly one `TASK_LAUNCHER.md`; reports back in the §5 contract; terminates |
| **review session** | one per stage synthesis | model-disjoint where possible; read-only; returns a verdict |

**A task session does one task.** If it discovers a second question, it reports it as a *nomination*
and does not pursue it. Scope creep inside a task session is how a bounded analysis becomes an
unreviewable one.

## 2 · Worktrees

One worktree per task, named for the task, on its own branch.

```
path:   /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-<task-id>
branch: task/<task-id>
base:   main   (unless the launcher names a different base)
```

Rules:

- **The coordinating session creates and removes worktrees.** A task session never does.
- A task session writes **only** inside its own worktree, and inside it only to the paths its
  launcher declares under `output_directory`.
- **Never** write to `results/` of another worktree, to any frozen bundle, or to `general/`.
- ⛔ **Never use bare `git stash` / `git stash pop`.** The stash stack is shared across all worktrees
  and other sessions may be using it. Use a temporary WIP commit instead.
- A task branch merges nowhere automatically. Promotion is §6 of the program launcher.

## 3 · Parallel safety

Two tasks may run concurrently **only if all four hold**:

1. **No shared writes.** Their declared `output_directory` paths are disjoint.
2. **No unfinished-producer reads.** Neither reads an artifact that is not on a `TASK_STATE=PASS`
   task's declared `CONSUMABLE_OUTPUTS` list. Note this gates on **task validity**, never on
   scientific outcome: a refuted hypothesis still yields consumable outputs.
3. **No population collision.** They do not both touch the same confirmatory population. Every task
   declares `populations_touched`; the coordinating session refuses the second one.
4. **No criterion coupling.** Neither's threshold, bar or selection rule is chosen using the other's
   output. If one informs the other, they are sequential by definition.

> Rule 4 exists because a selection cutoff in this project landed exactly at the winner-flip point of
> its own sweep, and because a repaired gate passed on a rule class motivated by the failed
> attempt's results.

**Populations are a depleting budget.** `populations_touched` is recorded permanently. A task that
trains on, tunes against, or merely inspects a population makes that population unavailable for a
later confirmatory claim. The coordinating session enforces this and cannot unwind it.

## 4 · Compute

| class | backend | notes |
|---|---|---|
| `ZERO` | this session | reads landed tables, writes new tables. No job. |
| `CPU_SMALL` / `CPU_MEDIUM` | workstation | under ~4 h |
| `CPU_HIGH` / `MEMORY_HIGH` | Ibex, fallback workstation | checkpointable and resume-safe required |
| `GPU_*` | Ibex GPU, fallback workstation GPU | checkpointable required |

**A cheap pilot is mandatory before any Ibex-scale run.** Declare the pilot's size and its expected
result in the launcher. One acceptance criterion in this project had a ceiling of 84.8% against a
required 95% and was discovered only after the instrument was frozen; a pilot costs minutes.

**The method may not change because the backend changed.** Record backend, job ID, software version,
seed and all input hashes regardless of where it ran.

## 5 · The reporting contract

Every task session returns **exactly this**, and nothing else. Facts only. The task does not say what
its numbers mean.

> ⚠️ **Task validity and hypothesis truth are two different things and must never share a field.**
> A task that executes perfectly and refutes its own hypothesis is a **successful task with a
> negative result**. If that were reported as FAIL, the consumption gate in §3 would refuse to let
> anything downstream read it, and an autonomous orchestrator would quietly discard a valid negative.
> This project's negatives are among its best assets; losing one this way would be the worst failure
> the system could have.

**Two fields, always both:**

```
TASK_STATE:         PASS | STOP | INCONCLUSIVE | BLOCKED | VOID
SCIENTIFIC_OUTCOME: SUPPORTS_H1 | SUPPORTS_H0 | FALSIFIED | BOUND | DESCRIPTIVE | NOT_APPLICABLE
```

`VOID` is reserved for a task whose **execution** is not trustworthy, and it is the only state that
makes the result unusable. A task is VOID when a required positive control failed, preregistration
post-dates job start, a forbidden input was read, or the declared rule changed during execution.

A scientific negative is normally `TASK_STATE=PASS` with `SCIENTIFIC_OUTCOME=FALSIFIED` or `BOUND`.

```markdown
# TASK REPORT — <task-id>

TASK_STATE: PASS | STOP | INCONCLUSIVE | BLOCKED | VOID
SCIENTIFIC_OUTCOME: SUPPORTS_H1 | SUPPORTS_H0 | FALSIFIED | BOUND | DESCRIPTIVE | NOT_APPLICABLE
CRITERION: <the preregistered criterion, verbatim>
MET: yes | no | not evaluable — <one line>

## Consumable outputs
<explicit list of outputs downstream tasks may read. Only populated when TASK_STATE=PASS.
A VOID or BLOCKED task may still leave debugging artefacts; they are never consumable.>

## Numbers
| quantity | value | unit | denominator | interval |
(every row must correspond to a cell in a landed table; give the table path)

## Controls
| control | type | state | result |
(positive, negative, baseline — all must be PASS before the primary ran)

## Populations touched
<names, and whether trained on / tuned against / inspected>

## Outputs
<path, sha256, row count> for every declared output

## Provenance
preregistration commit + timestamp | job submission timestamp | software versions | seed | input hashes

## Iterations
<n used of n budgeted; what changed at each>

## Nominations
<questions discovered and NOT pursued>

## What this does not show
<the task's own honest limits, in the task's own words>
```

**Forbidden in a task report:** the words established, proves, confirms, demonstrates, validates,
significant (without the test and its assumptions), and any biological interpretation. A task
reports that a number is what it is.

## 6 · Definition of done, and escalation

A task is done when it is in a terminal state with all of §5 present, its preregistration commit
timestamp **preceding** its job submission timestamp, and every control in `PASS`.

**Escalate to the operator, do not iterate, when:** the iteration budget is exhausted; a control
fails; the declared PASS outcome is found unreachable; an input is missing or its hash does not
match; or the task would need to change its own criterion.

## 6a · What may serve as a blocking control

⚠️ **A biological contrast may not be a blocking control unless it is independently established.**

A control exists to show the **implementation** works. If a launcher says "effect X must remain
significant" and X is one of the quantities under study, then a procedure that weakens X is
indistinguishable from a broken instrument, and the task is pushed toward the expected biological
answer. That is the exact failure this project has already paid for twice, once with a threshold
fitted at the winner-flip point of its own sweep and once with a repaired gate whose rule class was
motivated by the failed attempt.

Admissible blocking controls, in order of preference:

1. **Implementation reproduction** — the new code reproduces an existing landed number exactly.
2. **Synthetic positive fixture** — a simulated dataset with a known effect under the declared
   dependence structure; the instrument must recover it at a declared coverage.
3. **Synthetic null fixture** — zero effect under the same structure; the instrument must contain
   zero at the declared rate.
4. **A named, independently established biological positive**, with the source cited in the launcher.
   Naming it is what makes it admissible; "two families known to share the core" is not named.

Everything else is a **diagnostic**, reported and never blocking.

## 7 · Standing prohibitions for every session

- No scientific analysis begins without an authorised launcher on the board.
- No number is written into prose that does not resolve to a canonical table cell.
- No absence is claimed without a registry lookup and a positive control.
- No frozen bundle is modified, ever. Corrections are errata.
- No criterion is edited. A changed criterion is a new task inheriting the old record.
- Prior work supplies **assets and bounded negatives**. Its numbers are `[UNVERIFIED]` and are
  re-derived before any citation.
