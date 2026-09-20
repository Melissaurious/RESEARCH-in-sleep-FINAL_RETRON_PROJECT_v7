---
record: ARIS_CONFORMANCE_AUDIT
scope: autonomy/d4-wave-runner integration into project-synthesis
date: 2026-09-20
aris_pin: 58d46de166d09db3a677fa26fdf09bcabd6f31cf (ARIS.lock, pinned 2026-09-14)
general_pin: cff9831
verdict: ONE VIOLATION FOUND AND FIXED — integration is ARIS-conformant
---

# ARIS-conformance audit of the autonomous execution layer

Governing principle, `general/CLAUDE.md`:

> **ARIS owns the workflow. This layer constrains how it works.** … ARIS owns the lifecycle …
> together with … its reviewer routing (ARIS's `review_gate.py`, `/auto-review-loop`).
> **Do not build a second one.**

## 1 · What was inspected

`ARIS.lock` → `/home/borg/aris_repo` @ `58d46de`, verified present at the pinned commit; project
`CLAUDE.md`; `general/CLAUDE.md`; and the pinned ARIS contracts for execution, resumable state,
acceptance and queueing — `tools/run_state.py`, `tools/experiment_queue/`,
`skills/experiment-queue`, `skills/run-experiment`, `skills/experiment-bridge`,
`skills/auto-review-loop`.

## 2 · Legitimate extension — kept, and why

These solve workstation-specific execution/provenance problems that pinned ARIS does not address on
this installation. They are **not** a second workflow.

| kept | why ARIS does not cover it |
|---|---|
| `TASK_EXECUTION.json` exact executable binding | ARIS has no equivalent argv/worktree/freeze-commit binding record |
| frozen-file + input hashing, refusal **before** the command runs | project provenance requirement; no ARIS analogue |
| worktree isolation per task, freeze-before-execute | project `WORKING_RULES` §6b |
| P1b `monitor_only` PID handling, no signals | an externally launched, already-detached run |
| NVMe token admission (`RESOURCE_LIMITS.tsv`), I/O lanes | ARIS `/run-experiment` and `/experiment-queue` target local/vast/modal over SSH + `screen`; neither models this workstation's single-NVMe contention, and `general/CLAUDE.md` forbids `/experiment-queue` touching Ibex |
| immutable `WAVE.tsv` + `--authorise-wave-sha256` | project population-protection requirement |
| `OUTPUT_MANIFEST.sha256`, ledger rows | `BUNDLE_SPEC` provenance |
| headless preparation path | **D4**: `CAPABILITY_STATE.md` §3 records that task-session dispatch is a blocked capability here — `launch_task.sh` ends in an interactive `exec claude`, which cannot be queued. This layer exists to solve that, and it is the reason a project-side dispatcher is warranted at all |

## 3 · ⛔ The violation found

**`wave_runner.py` wrote an acceptance from the executor's own self-report.**

```python
if rr.get('worker_state')=='COMPLETE': term=rr['task_state']; set_board(tid,term,...)
```

With `TERMINAL_VALID = {"PASS"}`, a worker that reported its own success had `PASS` written straight
into `TASK_BOARD.tsv` and `EXECUTION_LEDGER.tsv` — and `choose_launchable` treats `PASS` as
satisfying a hard dependency, so a self-report would have unblocked downstream scientific tasks.

Pinned ARIS `tools/run_state.py` exists precisely to forbid this:

> `set` may only write pending/running/done/failed/skipped; only `accept` writes `accepted`, and it
> REQUIRES a verdict id + reviewer … **a loop can DRIVE resume, it cannot ACQUIT a phase past
> itself.**

Confirmed against the pinned tool: `accept` is refused without `--verdict-id` and `--reviewer`, a
`done` phase renders as `✓(unaccepted)`, and `resume` resolves **back** to a `done`-but-unaccepted
phase rather than skipping it.

This was also a regression against the project's own standing rule
(`docs/decisions/2026-09-20_reviewer_availability_check.md`): *"The author of a directive should not
also return the verdict on the artifact that directive shaped."* In `TASK_BOARD.tsv`, `PASS`
currently means operator-accepted (`T-R1b`); the autonomy layer would have minted the same token
from a self-report.

## 4 · The fix — bounded, no scientific change

An **acceptance boundary** was introduced, and `wave_runner.py` was reduced to a thin
resource/process scheduler that stops at execution-completeness.

- `autonomy_state.py` now separates `TERMINAL_VALID = {"PASS"}` (independently accepted) from
  `TERMINAL_EXECUTOR = {"COMPLETE_AWAITING_REVIEW"}` (executor self-report), with
  `executor_terminal_state()` mapping a self-reported success onto the latter. A self-reported
  **failure** is kept verbatim — no reviewer is needed to believe a task that says it failed.
- `COMPLETE_AWAITING_REVIEW` is this project's **existing** ledger vocabulary for executed-but-
  unreviewed tasks (`T-C1b`, `T-X1b`, `T-X1c`), so nothing new was invented.
- `wave_runner.py` imports one shared `TERMINAL` instead of redefining it, and mirrors executor
  phase status into ARIS `run_state.py` under `.aris/runs/<wave>.json` using **`set` only**. A
  regression test asserts the runner never calls `accept`. The mirror is best-effort and non-fatal,
  so ARIS being unavailable cannot kill a detached wave.
- `WAVE_STATUS.tsv` reverts to what `STATE_AUTHORITY.md` already called it: the generated operator
  view, not an independent state authority.

`choose_launchable` needed **no change**, which is the clearest sign the boundary landed in the right
place:

| relation | behaviour with `COMPLETE_AWAITING_REVIEW` | correct? |
|---|---|---|
| `hard_dependencies` (scientific) | `!= PASS` → `WAIT_DEP` | ✅ acceptance required |
| `schedule_after` (I/O lane ordering) | in `TERMINAL` → proceeds | ✅ ordering is not acceptance |
| descendant blocking | not in `TERMINAL_INVALID` → does not poison | ✅ |

## 5 · Effect on Wave 01 — none on scope, none on scheduling

Re-ran after the fix: the live dry-run is **byte-identical** to before, same wave sha256
`ef94fc0c…`, same selection. No scientific criterion, endpoint, population, threshold, R2a/R2b or
D1/D2 definition, Wave 01 membership, or active P1b state was touched.

What changes is only the *terminal* state an autonomously executed task can reach: tasks now end at
`COMPLETE_AWAITING_REVIEW` and wait for ARIS reviewer routing to grant `PASS`. Within Wave 01 no
task hard-depends on another Wave-01 task except `T-P1c` on `T-P1b` (monitor-only, which escalates
on exit regardless), and `T-S1b`'s `schedule_after T-M1b` is lane ordering, which still proceeds.
**Wave 01 therefore runs to completion unchanged, and acquits nothing.**

Test suite: **14/14 pass** (8 original + 6 new acceptance-boundary regressions).

## 6 · Remaining non-conformance, declared not silently accepted

`prepare()` spawns headless Claude with a bespoke prompt rather than reusing
`skills/experiment-bridge`. This is **retained deliberately** for now: experiment-bridge assumes a
dispatch path that `CAPABILITY_STATE.md` §3 records as blocked on this workstation (D4), and
replacing it would be a redesign, not a bounded integration. It is recorded here as the open
conformance item, to be reconnected to experiment-bridge if and when D4 is resolved.

No reviewer routing is implemented in this layer **by design** — that is ARIS's, and the fix above is
what keeps it ARIS's.
