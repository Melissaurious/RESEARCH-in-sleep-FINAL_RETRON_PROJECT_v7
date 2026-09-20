# Autonomy implementation handoff

## Branch identity

- Remote branch: `autonomy/d4-wave-runner`
- Validated implementation payload tip before this handoff-only commit: `99a529712c0870621b5bc9b1bff4bc08b6b966dc`
- Base used to build the branch: `project-synthesis@da2c734456eada9dcbc49a9bd2f74c598f13b123`
- Final publication tip: resolve `origin/autonomy/d4-wave-runner` after fetch; the exact final SHA is returned by the coordinating handoff message. A tracked file cannot self-embed the SHA of the commit that contains itself because changing that text changes the commit SHA.

No scientific task was dispatched while building or validating this branch. Active P1b remains external/monitor-only.

## Files added or modified

Added:

- `programme/autonomy_state.py`
- `programme/task_worker.py`
- `programme/wave_runner.py`
- `programme/test_autonomous_execution.py`
- `programme/RESOURCE_LIMITS.tsv`
- `programme/STATE_AUTHORITY.md`
- `programme/templates/TASK_EXECUTION.template.json`
- `programme/waves/autonomous-wave-01/WAVE.tsv`
- `programme/waves/autonomous-wave-01/README.md`
- `programme/tasks/T-R2a-tierA-internal-geometry/TASK_LAUNCHER.md`
- `programme/tasks/T-R2b-buffington-engineered-delta/TASK_LAUNCHER.md`

Modified:

- `programme/launch_task.sh`
- `programme/preflight.py`
- `programme/TASK_BOARD.tsv`
- `programme/ALL_DOWNSTREAM_TASKS.tsv`

The final engineering pass also fixed a live-launch-only Python shadowing defect in `wave_runner.spawn()` and added a regression test for it.

## State-authority model

No new scientific state system was introduced.

| Question | Authority |
|---|---|
| May a task prepare or launch? | `programme/TASK_BOARD.tsv` |
| What science is authorised? | frozen task-worktree `TASK_LAUNCHER.md` |
| Which datasets may be consumed? | `programme/CANONICAL_DATASETS.tsv` |
| What exact executable/input/backend is bound? | `programme/executions/<task>/TASK_EXECUTION.json` |
| Did execution finish validly and what was its scientific outcome? | task `TASK_REPORT.md` |
| What output bytes are valid? | task `OUTPUT_MANIFEST.sha256` |
| What ran, where, and when? | `programme/EXECUTION_LEDGER.tsv` |
| What tasks are authorised for this autonomous batch? | immutable `programme/waves/<wave>/WAVE.tsv` |
| What is happening now? | generated `WAVE_STATUS.tsv` |
| Long-range catalogue/context | `programme/ALL_DOWNSTREAM_TASKS.tsv` |
| Historical human dashboard | `programme/LIVE_EXECUTION.tsv`; not an execution authority |

`TASK_EXECUTION.json` contains executable binding only: exact worktree/branch/freeze commit, argv, input hashes, output directory, backend, resource declaration, runtime metadata, and frozen-file hashes. Scientific criteria remain in `TASK_LAUNCHER.md`.

## Integration assumptions

1. Integrate into the workstation synthesis checkout, not into any task worktree.
2. The synthesis checkout must be on `project-synthesis` and clean before integration or Wave start.
3. Do not reset a fresher local `project-synthesis` backwards to the remote branch base. Merge/reconcile the autonomy branch into the current local state.
4. If `TASK_BOARD.tsv` or `ALL_DOWNSTREAM_TASKS.tsv` has fresher workstation state, preserve that state and reconcile only the autonomy/state-authority semantics; do not overwrite newer task facts.
5. Active `T-P1b-identity-partition` PID `810502` is monitor-only. Do not signal, restart, re-freeze, rebase, modify, or compete heavily with it.
6. P1b's recorded freeze is `1a6909f`; verify the live process identity from the workstation rather than trusting PID existence alone.
7. The runner expects the `retron_tradicional` conda environment and the existing governed `general/` submodule/bootstrap used by `launch_task.sh`.
8. The current local I/O budget is 8 tokens. While P1b is live, it reserves 6.
9. Wave 01 scope is already reviewed. Do not redesign R2a, R2b, D1, D2, or Wave 01 during integration unless implementation reveals a genuinely new scientific decision.

## Exact workstation validation sequence

Run from the synthesis checkout. These commands perform no scientific dispatch.

```bash
cd /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis

test "$(git branch --show-current)" = "project-synthesis"
test -z "$(git status --porcelain)"

PRE_AUTONOMY="$(git rev-parse HEAD)"
git branch -f backup/autonomy-preintegration "$PRE_AUTONOMY"

git fetch origin autonomy/d4-wave-runner
git rev-parse origin/autonomy/d4-wave-runner
git log --oneline --decorate --no-merges "$PRE_AUTONOMY"..origin/autonomy/d4-wave-runner
git diff --name-status "$PRE_AUTONOMY"...origin/autonomy/d4-wave-runner

# Integrate without committing so the merged tree can be tested first.
git merge --no-ff --no-commit origin/autonomy/d4-wave-runner
```

If the merge reports conflicts in scientific launchers, Wave scope, or fresher task state, STOP instead of choosing a scientific resolution automatically. Mechanical conflicts in autonomy code may be resolved while preserving the branch implementation.

Verify active P1b without signalling it:

```bash
ps -p 810502 -o pid=,lstart=,args=
readlink -f /proc/810502/cwd
```

The displayed process/cwd must be the known P1b full run. PID existence alone is not sufficient.

Run static and unit tests:

```bash
python3 -m py_compile   programme/autonomy_state.py   programme/task_worker.py   programme/preflight.py   programme/wave_runner.py   programme/test_autonomous_execution.py

bash -n programme/launch_task.sh

python3 programme/test_autonomous_execution.py
```

Expected: **8/8 tests pass**, including scheduler isolation, hash refusal, synthetic deterministic execution, and the worker-spawn regression.

Run the live-state dry-run only:

```bash
python3 programme/wave_runner.py   programme/waves/autonomous-wave-01/WAVE.tsv   --dry-run
```

With P1b correctly detected as alive and consuming 6/8 I/O tokens, the expected initial scheduler state is:

- `T-P1b-identity-partition`: `MONITOR_ONLY alive=True io=6`
- `T-A23d-primary-verification`: `SELECTED`
- `T-R2a-tierA-internal-geometry`: `SELECTED`
- `T-R2b-buffington-engineered-delta`: `WAIT_RESOURCE` after the two available lightweight tokens are allocated
- `T-D1-annotation-disagreement`: `WAIT_RESOURCE`
- `T-D2-taxonomic-distribution`: `WAIT_RESOURCE`
- `T-M1b-embedding-cache-reverification`: `WAIT_RESOURCE`
- `T-P1c-family-label-description`: `WAIT_DEP:T-P1b-identity-partition:RUNNING`
- `T-S1b-structure-inventory-correction`: `WAIT_ORDER:T-M1b-embedding-cache-reverification:AUTHORIZED`
- selected set: `T-A23d-primary-verification;T-R2a-tierA-internal-geometry`

If that differs materially, do not start the wave.

If all checks pass, finish the merge:

```bash
git commit -m "autonomy: integrate deterministic wave runner"
```

## Harmless headless-Claude preparation capability test

This tests the exact headless invocation style used by the runner while giving Claude no repository and no permission to perform useful work.

```bash
TMP_CLAUDE_TEST="$(mktemp -d)"
CLAUDE_TEST_OUT="$(
  cd "$TMP_CLAUDE_TEST"
  claude --dangerously-skip-permissions -p     'Do not call tools. Do not read, create, edit, or delete files. Do not execute commands. Reply exactly: HEADLESS_PREP_OK'
)"
rm -rf "$TMP_CLAUDE_TEST"

test "$(printf '%s' "$CLAUDE_TEST_OUT" | tr -d '\r')" = "HEADLESS_PREP_OK"
echo "HEADLESS_PREP_OK"
```

If this fails, deterministic execution remains implemented, but autonomous task preparation is not ready on this workstation. Do not start Wave 01 because Wave 01 contains `prepare_execute` tasks.

## Exact detached Wave 01 start

Run only after integration, all tests, live P1b identity check, dry-run, and the harmless headless-Claude test pass.

The runner requires a clean `project-synthesis` at start. Therefore keep runner stdout/PID files **outside the repository**.

```bash
cd /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis
test "$(git branch --show-current)" = "project-synthesis"
test -z "$(git status --porcelain)"

WAVE="programme/waves/autonomous-wave-01/WAVE.tsv"
WAVE_SHA="$(sha256sum "$WAVE" | awk '{print $1}')"

AUTONOMY_STATE_DIR="$HOME/.local/state/retron-autonomy/autonomous-wave-01"
mkdir -p "$AUTONOMY_STATE_DIR"

nohup setsid python3 programme/wave_runner.py "$WAVE"   --start   --authorise-wave-sha256 "$WAVE_SHA"   --poll-seconds 5   >"$AUTONOMY_STATE_DIR/runner.log" 2>&1 < /dev/null &

echo "$!" > "$AUTONOMY_STATE_DIR/runner.pid"
cat "$AUTONOMY_STATE_DIR/runner.pid"
```

This is the operator action that authorises/starts the wave. Integration and validation must not run it.

## STOP conditions

STOP integration/start and do not improvise if any of the following occurs:

- `project-synthesis` is dirty before integration/start;
- a merge conflict requires changing an approved scientific endpoint, population, threshold, control, interpretation ceiling, R2 split, D1/D2 scope, or Wave 01 membership;
- PID 810502 is absent or does not resolve to the known active P1b run;
- static syntax, Bash syntax, or any autonomy test fails;
- live dry-run does not reserve 6/8 tokens for P1b or selects medium/heavy-I/O work beside it;
- headless Claude capability test fails;
- a prepared task returns `REVIEW_REQUIRED`;
- frozen-file or input hashes mismatch;
- required `TASK_REPORT.md`, run log, or output manifest is missing/invalid;
- a protected population would be spent without explicit immutable-wave authorisation;
- a task would need criterion/threshold/population redesign after exposure;
- any operation would signal, restart, modify, re-freeze, or heavily compete with active P1b.

## Rollback if integration validation fails

The validation sequence creates `backup/autonomy-preintegration` before changing the synthesis tree.

If the merge has not been committed:

```bash
git merge --abort 2>/dev/null || true
git reset --hard backup/autonomy-preintegration
```

If the merge was committed but **Wave 01 has not been started** and no new synthesis work was added afterward:

```bash
git reset --hard backup/autonomy-preintegration
```

Do not delete or reset any task worktree, and do not signal P1b as part of rollback.

If Wave 01 has already been started, rollback is no longer an ordinary integration rollback: preserve ledgers/runtime records and follow the task STOP/recovery rules instead of erasing execution state.
