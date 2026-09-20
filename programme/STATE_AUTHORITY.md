# Autonomous execution — existing state authorities

This file does **not** add a governance layer. It records which existing artefact owns each transition so the wave runner does not create competing truth.

| question | authority | runner behaviour |
|---|---|---|
| May this task be prepared/launched? | `programme/TASK_BOARD.tsv` | requires the task row and `state=AUTHORIZED`; changes terminal state here after execution |
| What science is authorised? | frozen task-worktree `TASK_LAUNCHER.md` | never inferred from wave status; no scientific field is duplicated into `TASK_EXECUTION.json` |
| Which datasets may be consumed? | `programme/CANONICAL_DATASETS.tsv` | only `CANONICAL` / `CANONICAL_WITH_LIMITATION`; limitations remain binding |
| What exact code/input/backend is executed? | `programme/executions/<task>/TASK_EXECUTION.json` | generated only after the task freeze commit exists; binds exact worktree, branch, freeze SHA, argv, input hashes and resources |
| Did the task execute validly? | final task-worktree `TASK_REPORT.md` | `TASK_STATE` and `SCIENTIFIC_OUTCOME` are parsed from the report; valid negatives remain consumable |
| What are the output bytes? | task `OUTPUT_MANIFEST.sha256` | verified before terminal state is accepted |
| What ran, where and when? | `programme/EXECUTION_LEDGER.tsv` | programme-wide execution index; updated at freeze/start/terminal transitions |
| What is the authorised scope of one autonomous batch? | immutable `programme/waves/<wave>/WAVE.tsv` | its SHA-256 must be supplied at `--start`; it is not a task-state authority |
| What is happening right now? | generated `WAVE_STATUS.tsv` | runtime view only; reconstructable from workers/reports/ledger |
| What is the long-range task catalogue? | `programme/ALL_DOWNSTREAM_TASKS.tsv` | planning context only; not used to overrule a launcher/board/report |
| What is the old human live dashboard? | `programme/LIVE_EXECUTION.tsv` | human-facing historical/status view; not used by the autonomous eligibility gate |

## Freeze rule

Preparation occurs in the task worktree. The runner, not the preparation agent, creates the freeze commit. The exact freeze SHA is then written to the synthesis-side `TASK_EXECUTION.json`, avoiding the impossible circular requirement for a commit to contain its own hash.

## Failure rule

A terminal-invalid hard dependency blocks only its descendants. `schedule_after` is an ordering/resource relationship, not a scientific dependency: its predecessor need only become terminal before the next task is considered.
