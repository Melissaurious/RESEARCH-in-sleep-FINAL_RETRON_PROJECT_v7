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

**Measured local capacity, 2026-09-20:** 48 logical CPUs (24 physical), 251 GB RAM with 232 GB
available, load ~2.4 of 48. Verified directly, not assumed.

| class | backend | notes |
|---|---|---|
| `ZERO` | this session | reads landed tables, writes new tables. No job. |
| `CPU_SMALL` / `CPU_MEDIUM` | workstation | under ~4 h |
| `CPU_HIGH` / `MEMORY_HIGH` | workstation, or **Ibex over SSH** | 48 cores and 232 GB free make most of this local |
| `GPU_*` | **workstation, RESOLVED** | 2 x RTX 4090, 24,564 MiB each, driver 535.309.01, both idle |

### Correction, and how I got it wrong

An earlier revision of this table declared **"Ibex is not reachable from this host"** on the evidence
that `sbatch`, `squeue`, `sinfo`, `sacct` and `srun` are all absent. **That was wrong, and the
correction matters more than the error.**

`general/site/IBEX.md` states, and verifies, that this workstation **has no SLURM client by design**:
*"`borg` has no SLURM client at all ... every scheduler command therefore runs on Ibex, over SSH."*
Submission is by `ssh rioszemm@ilogin.ibex.kaust.edu.sa`, key-based, last exercised 2026-09-06 with
four named job IDs. **A wrapper already exists** at `general/tools/status.sh`, which polls
`squeue --me` over SSH. Anything needing Ibex job state should call that, not reimplement it.

So the absent client is the documented, expected state, not a defect. I read a *correctly absent*
tool as a finding, and wrote a rule that would have stopped legitimate work.

**Why I got it wrong is the part to keep.** The document that answers this was in my own worktree the
whole time, at `general/site/IBEX.md`. I checked the machine and did not check the governance layer.
That is the same failure this programme was built around, at smaller scale: five conclusions in the
underlying review were reversed by looking outside a declared scope, and here the scope was one
directory away. **Check `general/` before recording any capability as absent.**

⚠️ **Latent break, unfixed:** `status.sh` defaults `IBEX_HOST` to the alias `ibex`, which `IBEX.md`
marks *optional and not re-verified*. If the alias is missing the wrapper prints UNREACHABLE and the
next reader concludes Ibex is down when it is merely unaliased. Set the full hostname or verify the
alias. Do **not** use the `vscode.` host for scripted access; it is a load-balanced pool with a
documented node that hangs at SSH userauth. The SSH marks are two weeks old; re-verify before Batch
Two treats Ibex as available.

### ⛔ The real defect: `general/` is empty in every task worktree

| worktree | `general/` entries |
|---|---|
| synthesis | **15** |
| every `task/*` worktree | **0** |

The governance layer, which carries the Ibex profile, the compute policy, the evidence standards and
the wrapper, **does not materialise in a task worktree**. `CLAUDE.md` requires
`git submodule update --init --recursive && bash general/checks/specs_exist.sh` before
provenance-bearing execution, and in a task worktree as created that check **cannot run**.

This is the same failure class as a deferred tool arriving as a bare name: **the capability exists at
the root and is absent in the spawned context, so the spawned context concludes it does not exist.**
A Batch-Two task needing Ibex would find no client, find no profile explaining why, and report the
backend unavailable, reproducing exactly the error corrected above.

`programme/launch_task.sh` already initialises the submodule on first use. **Batch One did not go
through it** — those sessions were dispatched directly, bypassing the script, so they ran without the
governance layer. That is a dispatch error, not a script error, and it is mine. Every future dispatch
goes through `launch_task.sh`, or performs the submodule init and the specs check explicitly.

✅ **GPU state RESOLVED, and the earlier reading was a sandbox artefact.** Inside the sandbox
`nvidia-smi` fails to reach a driver and no `/dev/nvidia*` nodes are visible. Outside it: **two
NVIDIA RTX 4090s, 24,564 MiB each, driver 535.309.01**, all six device nodes present, four kernel
modules loaded, both cards essentially free.

**This is the third time in this programme that an absence turned out to be a context artefact**, and
the pattern is now unmistakable. A deferred tool arrived as a bare name and was read as an
unavailable reviewer. A submodule failed to initialise in a task worktree and its governance was
read as missing. A sandbox hid device nodes and two idle GPUs were read as no GPUs. Each time the
capability was present at the root and absent in the spawned context. **Before recording any
capability as absent, establish which context you are measuring from.**

⚠️ **The binding constraint is I/O, not CPU or RAM.** `/home/borg` and `$TMPDIR` are the same NVMe
device (2.8 TB free of 7 TB). Project data, scratch and checkpoints contend for one device, so with
48 idle cores and 232 GB free, concurrency saturates disk first. Declare expected I/O, not just cores.

### 4a · Scheduling and population depletion — the rule a scheduler must not automate

Parallel safety in §3 prevents two tasks **colliding** on one population. It does not prevent the
programme **spending** populations faster than it learns from them, and those are different failures.

`TASK_PROTOCOL.md` §1 makes consuming a confirmatory population **tier C, operator only**, and §3
above records that the coordinator cannot unwind it. A scheduler that auto-launches "the maximum
safe set of independent tasks" would therefore automate a tier-C decision every time a task touches
an unexhausted confirmatory population. Sequential execution preserves the option to learn from the
first task and decline to spend a population on the fifth. A parallel wave forecloses that
permanently, in exchange for wall-clock time that is not scarce at 5% load.

**Therefore the launch gate splits by population exposure, not by independence alone:**

| `populations_touched` | scheduling |
|---|---|
| empty | **auto-schedule freely.** Prior-work lookups, asset audits, `ZERO` tasks, pilots and implementation review. This is most of the available parallelism |
| already exhausted | **auto-schedulable**, since nothing further is spent. State the exhaustion in the launcher |
| **unexhausted confirmatory** | **`READY_WAITING_OPERATOR`. Never auto-launched. One explicit authorisation per launch** |

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
