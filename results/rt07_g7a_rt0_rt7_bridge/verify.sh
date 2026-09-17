#!/usr/bin/env bash
# Independent checks on the landed bundle. Every one can fail.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
B="results/rt07_g7a_rt0_rt7_bridge"
fail=0
ok()   { printf "  PASS  %s\n" "$1"; }
bad()  { printf "  FAIL  %s\n" "$1"; fail=$((fail+1)); }

echo "verify: rt07_g7a_rt0_rt7_bridge"

# V1 - NC-4: anti-circularity, checked two ways.
#  (a) INPUTS.tsv - the authoritative record of what the gate READ - names no g5/g6 artefact;
#  (b) no measurement script reads one. seal.py is excluded from the text scan because it
#      CONTAINS the guard, and (c) asserts that the guard is actually there.
PAT='g5_(sequences|states|catalytic|ineligible|metadata|state_occupancy|qc)|g6_readiness|rt07_g5|rt07_g6'
hits=$( { grep -IE "$PAT" "$B/INPUTS.tsv" || true; \
          grep -IhE "$PAT" "$B"/scripts/s0*.py "$B"/scripts/g7alib.py || true; } | wc -l )
if [ "$hits" -ne 0 ]; then
  bad "NC-4(a,b) anti-circularity: a g5/g6 artefact is named in INPUTS.tsv or a measurement script"
else
  ok "NC-4(a,b) anti-circularity: no g5 or g6 artefact is an input or is read by any script"
fi
if grep -q "anti-circularity" "$B/scripts/seal.py"; then
  ok "NC-4(c) the input sealer carries its own anti-circularity assertion"
else
  bad "NC-4(c) the input sealer lost its anti-circularity assertion"
fi

# V2 - the frozen bundle was not modified by this gate.
if git -C "$ROOT" status --porcelain -- results/rt07_g4b_production_mapper results/rt07_g4a_repaired 2>/dev/null | grep -q .; then
  bad "V2 a frozen bundle has uncommitted modifications"
else
  ok "V2 no frozen bundle was modified"
fi

# V3 - the frozen crosswalk is still UNRESOLVED in every row.
if python3 -c "import sys; sys.path.insert(0,'results/rt07_g4b_production_mapper/code'); \
from rtmap import crosswalk as C; C.assert_unresolved_until_g7()" >/dev/null 2>&1; then
  ok "V3 g4b control/CROSSWALK_RT0_RT7.tsv is still UNRESOLVED in every row"
else
  bad "V3 the frozen crosswalk was resolved in place - forbidden by LAUNCHER_03 section 9b"
fi

# V4 - every label has exactly one terminal status.
n=$(tail -n +2 "$B/tables/g7a_closure_decision.tsv" | wc -l)
u=$(tail -n +2 "$B/tables/g7a_closure_decision.tsv" | cut -f1 | sort -u | wc -l)
if [ "$n" = 8 ] && [ "$u" = 8 ]; then ok "V4 8 labels, 8 terminal statuses, no duplicates"
else bad "V4 expected 8 unique labels, got n=$n unique=$u"; fi

# V5 - no production output carries a historical label (the standing project constraint).
if grep -qE "RT[0-7]" "$B/tables/g7a_state_to_residue.tsv"; then
  bad "V5 the raw state->residue table carries a historical label"
else
  ok "V5 the raw state->residue table carries state_id only, no historical label"
fi

# V6 - controls: no FAIL.
if awk -F'\t' 'NR>1 && $5=="FAIL"' "$B/tables/g7a_controls.tsv" | grep -q .; then
  bad "V6 a declared control FAILED"
else
  ok "V6 no declared control FAILED"
fi

# V7 - nothing is interpolated: a label with 0 supporting states has no state span.
if awk -F'\t' 'NR>1 && $4==0 && $5!=""' "$B/tables/g7a_crosswalk_resolved.tsv" | grep -q .; then
  bad "V7 a label with zero supporting states was given a state span - interpolation"
else
  ok "V7 no label with zero supporting states was given a state span"
fi

# V8 - the figure exists in both required formats with its data table.
for f in figures/g7a_bridge.png figures/g7a_bridge.svg tables/g7a_bridge.tsv; do
  [ -s "$B/$f" ] && ok "V8 $f present" || bad "V8 $f missing or empty"
done

# V9 - no RT0 occupancy QUANTITY exists (g3 OBJECT_MISMATCH, carried forward). This checks
# columns and values, not prose: the tables are REQUIRED to state the prohibition in words.
if head -1 -q "$B"/tables/*.tsv | tr '\t' '\n' | grep -qiE "^rt0_(occupancy|fraction|coverage|count)"; then
  bad "V9 a table has an RT0 occupancy column"
elif awk -F'\t' 'NR>1 && $1=="RT0" && ($4!="" || $5!="")' "$B/tables/g7a_closure_decision.tsv" | grep -q .; then
  bad "V9 the RT0 row carries supporting states or a supported residue span"
else
  ok "V9 no RT0 occupancy quantity exists: no column, and the RT0 row carries no span"
fi

echo "verify: $fail failure(s)"
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
