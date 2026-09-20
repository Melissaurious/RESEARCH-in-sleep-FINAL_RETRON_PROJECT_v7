#!/usr/bin/env bash
# Start authorised autonomous Wave 01, detached.
#
# WHY THIS FILE EXISTS
#   Every validation gate for Wave 01 passed on 2026-09-20 (see
#   programme/DURABLE_HANDOFF.md section 3). The only thing that did not happen is the
#   start itself: the coordinating Claude session's permission classifier refuses to
#   spawn the detached coordinator. That is the SAME blocked capability this project
#   already records as D4 in programme/CAPABILITY_STATE.md section 3 -- the host
#   harness will not let an agent session spawn an autonomous task process.
#
#   So the start is an operator action. This script is the exact reviewed route from
#   programme/AUTONOMY_IMPLEMENTATION_HANDOFF.md, with nothing added.
#
# RUN IT FROM THE SYNTHESIS CHECKOUT:
#   bash programme/START_WAVE_01.sh
#
# It refuses to start on a wrong branch, a dirty tree, or a changed WAVE.tsv.
set -euo pipefail

SYN=/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python   # never base
WAVE=programme/waves/autonomous-wave-01/WAVE.tsv
EXPECTED_WAVE_SHA=be06882012d54ee046df617a26cea5e36e358829aabd624f6df9017944de641f
STATE_DIR="$HOME/.local/state/retron-autonomy/autonomous-wave-01"

cd "$SYN"

[ "$(git branch --show-current)" = "project-synthesis" ] || { echo "ABORT: not on project-synthesis"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "ABORT: working tree is dirty"; exit 1; }

WAVE_SHA="$(sha256sum "$WAVE" | awk '{print $1}')"
[ "$WAVE_SHA" = "$EXPECTED_WAVE_SHA" ] || {
  echo "ABORT: WAVE.tsv changed since validation."
  echo "  expected $EXPECTED_WAVE_SHA"
  echo "  observed $WAVE_SHA"
  echo "  Re-validate before starting; do not widen the wave."
  exit 1
}

# P1b finished 2026-09-20T20:17 and was reconciled into TASK_BOARD/EXECUTION_LEDGER, so its
# monitor row was removed from the wave and the full 8 I/O tokens are free. P1c stays blocked
# because P1b is COMPLETE_AWAITING_REVIEW, not PASS -- the board, not this script, enforces that.
if ps -p 810502 -o args= 2>/dev/null | grep -q p1b_identity_partition; then
  echo "ABORT: pid 810502 is running P1b again; the wave expects the heavy lane free."
  exit 1
fi
echo "P1b: complete and reconciled; heavy I/O lane free (8/8 tokens)"

mkdir -p "$STATE_DIR"

nohup setsid "$PY" programme/wave_runner.py "$WAVE" \
  --start \
  --authorise-wave-sha256 "$WAVE_SHA" \
  --poll-seconds 5 \
  >"$STATE_DIR/runner.log" 2>&1 < /dev/null &

RUNNER_PID=$!
echo "$RUNNER_PID" > "$STATE_DIR/runner.pid"

echo
echo "coordinator_pid   $RUNNER_PID"
echo "wave_sha256       $WAVE_SHA"
echo "runner_log        $STATE_DIR/runner.log"
echo "integrated_commit $(git rev-parse HEAD)"
echo
echo "Expected first scheduling round:"
echo "  SELECTED       T-A23d-primary-verification, T-R2a-tierA-internal-geometry"
echo "  MONITOR_ONLY   T-P1b-identity-partition (alive, io=6)"
echo "  WAIT_RESOURCE  T-R2b, T-D1, T-D2, T-M1b"
echo "  WAIT_DEP       T-P1c (on P1b)"
echo "  WAIT_ORDER     T-S1b (after T-M1b)"
echo
echo "Watch it with:"
echo "  tail -f $STATE_DIR/runner.log"
echo "  $PY programme/wave_runner.py $WAVE --status"
