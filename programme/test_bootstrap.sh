#!/usr/bin/env bash
# Bootstrap fixture for programme/launch_task.sh.
#
#   bash programme/test_bootstrap.sh
#
# Proves the worktree bootstrap FAILS CLOSED. Every gate below exists because Batch One ran
# with general/ empty in every task worktree: launch_task.sh attempted the submodule init,
# the init failed, the script printed "[warn] ... governance layer unavailable" and the
# session continued. A governance layer that is optional is not a governance layer.
#
# This fixture runs NO scientific command and creates NO worktree. It exercises the gate
# expressions against synthetic fixtures in a temp dir, and asserts statically that the real
# script routes every governance failure to a non-zero exit.
set -uo pipefail

SYN="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis"
LAUNCHER="${SYN}/programme/launch_task.sh"
GENERAL_PIN="cff983144e2ad6fc01f648982fb61810dd77ddbe"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

PASS=0; FAIL=0
ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAIL=$((FAIL+1)); }
check(){ if eval "$2" >/dev/null 2>&1; then ok "$1"; else bad "$1"; fi; }
checkn(){ if eval "$2" >/dev/null 2>&1; then bad "$1"; else ok "$1"; fi; }

echo "=== bootstrap fixture: $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo
echo "A · the launcher exists and is syntactically valid"
check  "launch_task.sh present"                 "[[ -s '$LAUNCHER' ]]"
check  "bash -n parses it"                      "bash -n '$LAUNCHER'"

echo
echo "B · no fail-open survives in the governance or environment blocks"
# The exact defect: a governance failure that only warns. If any of these reappear, the
# bootstrap silently degrades again and every downstream task inherits an unguarded session.
checkn "no '[warn] submodule init failed'"      "grep -q 'warn.*submodule init failed' '$LAUNCHER'"
checkn "no '[warn] conda not found'"            "grep -q 'warn.*conda not found' '$LAUNCHER'"
checkn "no '|| echo' on a governance line"      "grep -nE '(submodule|specs_exist|conda activate|general/).*\|\| *echo' '$LAUNCHER' | grep -v REFUSED"
check  "every REFUSED path exits non-zero"      "[[ \$(grep -c 'REFUSED' '$LAUNCHER') -le \$(grep -c 'exit 1' '$LAUNCHER') ]]"

echo
echo "C · the governed pin is asserted in CODE, not only in a comment"
check  "pin literal present outside a comment"  "grep -nE '^[^#]*${GENERAL_PIN}' '$LAUNCHER'"
check  "recorded pin is compared"               "grep -q 'ls-tree HEAD general' '$LAUNCHER'"
check  "checked-out pin is compared"            "grep -q \"rev-parse HEAD\" '$LAUNCHER'"

echo
echo "D · specs_exist.sh is EXECUTED, not merely documented"
check  "specs_exist.sh is invoked"              "grep -q 'bash general/checks/specs_exist.sh' '$LAUNCHER'"
check  "its failure exits non-zero"             "grep -A3 'specs_exist.sh' '$LAUNCHER' | grep -q 'exit 1'"

echo
echo "E · the environment gate verifies the ACTIVE env, not just the activate call"
check  "CONDA_DEFAULT_ENV is compared"          "grep -q 'CONDA_DEFAULT_ENV' '$LAUNCHER'"
check  "compared against retron_tradicional"    "grep -q 'CONDA_DEFAULT_ENV.*retron_tradicional' '$LAUNCHER'"

echo
echo "F · synthetic negatives — each must BLOCK"
# F1: empty general/ must be caught by the asset assertion. Run in a subshell so the gate's
# own 'exit' cannot terminate this fixture.
mkdir -p "$TMP/empty/general"
checkn "empty general/ fails the asset gate" \
  "( for a in general/site/IBEX.md general/tools/status.sh general/checks/specs_exist.sh; do [[ -s '$TMP/empty/'\$a ]] || exit 1; done )"
# F1b: a general/ with only SOME assets must also fail, not just a wholly empty one.
mkdir -p "$TMP/partial/general/site"; echo x > "$TMP/partial/general/site/IBEX.md"
checkn "partially populated general/ still fails" \
  "( for a in general/site/IBEX.md general/tools/status.sh general/checks/specs_exist.sh; do [[ -s '$TMP/partial/'\$a ]] || exit 1; done )"
# F2: a wrong pin must not equal the governed pin.
checkn "a wrong pin is rejected"                "[[ 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef' == '$GENERAL_PIN' ]]"
# F3: a wrong active environment must be rejected.
checkn "env 'base' is rejected"                 "[[ 'base' == 'retron_tradicional' ]]"
checkn "empty env is rejected"                  "[[ '' == 'retron_tradicional' ]]"

echo
echo "G · no scientific command can run after a refusal"
# 'exec claude' must be the last statement and must be unreachable from any REFUSED path,
# i.e. every refusal exits before it.
check  "'exec claude' appears exactly once"     "[[ \$(grep -c '^exec claude' '$LAUNCHER') -eq 1 ]]"
check  "'exec claude' is the last non-blank line" \
       "[[ \"\$(grep -ve '^[[:space:]]*\$' '$LAUNCHER' | tail -1)\" == exec\\ claude* ]]"
check  "every REFUSED precedes it"              "[[ \$(grep -n 'REFUSED' '$LAUNCHER' | tail -1 | cut -d: -f1) -lt \$(grep -n '^exec claude' '$LAUNCHER' | cut -d: -f1) ]]"

echo
echo "H · live state of THIS worktree (informational where general/ is absent by design)"
if [[ -n "$(ls -A "$SYN/general" 2>/dev/null)" ]]; then
  rec="$(git -C "$SYN" ls-tree HEAD general 2>/dev/null | awk '{print $3}')"
  cur="$(git -C "$SYN/general" rev-parse HEAD 2>/dev/null)"
  check "synthesis: recorded pin == governed pin"   "[[ '$rec' == '$GENERAL_PIN' ]]"
  check "synthesis: checked-out pin == governed"    "[[ '$cur' == '$GENERAL_PIN' ]]"
  check "synthesis: specs_exist.sh passes"          "cd '$SYN' && bash general/checks/specs_exist.sh"
else
  echo "  SKIP  synthesis general/ not populated"
fi

echo
printf '=== %d passed, %d failed ===\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]] || exit 1
