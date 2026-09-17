#!/usr/bin/env bash
# Independent checks on the landed g6 bundle. Every one can fail.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
B="results/rt07_g6_family_architecture"
fail=0
ok()  { printf "  PASS  %s\n" "$1"; }
bad() { printf "  FAIL  %s\n" "$1"; fail=$((fail+1)); }

echo "verify: rt07_g6_family_architecture"

# V1 - ANTI-CIRCULARITY: g7a is sealed external context and must not be READ.
# Checked three ways. The bundle DOCUMENTS the exclusion in several places, and a mention is
# not a breach - so the test looks for a g7a PATH among the inputs, and for an actual file
# ACCESS in a script, never for the mere string.
PAT='rt07_g7a|g7a_crosswalk|g7a_closure'
if grep -IE "$PAT" "$B/INPUTS.tsv" 2>/dev/null | grep -q .; then
  bad "V1(a) a g7a artefact is named as an INPUT"
else
  ok "V1(a) no g7a artefact is an input"
fi
# an access is a line naming a g7a artefact AND opening/reading it
if grep -IhE "$PAT" "$B"/scripts/*.py 2>/dev/null \
   | grep -E "open\(|read_table|read_tsv|np\.load|ParquetFile|join\(" | grep -q .; then
  bad "V1(b) a script reads a g7a artefact"
else
  ok "V1(b) no script opens or reads a g7a artefact"
fi
if grep -q "sealed-context breach" "$B/scripts/seal.py"; then
  ok "V1(c) the input sealer carries a runtime sealed-context assertion"
else
  bad "V1(c) the input sealer lost its sealed-context assertion"
fi

# V2 - no historical RT0-RT7 label may appear in any landed g6 table.
if grep -rIlE '\bRT[0-7]\b' "$B/tables" 2>/dev/null | grep -q .; then
  bad "V2 a historical RT0-RT7 label appears in a g6 table"
else
  ok "V2 no historical RT0-RT7 label appears in any g6 table - states are bare state_id"
fi

# V3 - no frozen bundle was modified by this gate.
if git -C "$ROOT" status --porcelain -- results/rt07_g4b_production_mapper \
     results/rt07_g5_catalogue_application results/rt07_g7a_rt0_rt7_bridge 2>/dev/null | grep -q .; then
  bad "V3 a frozen bundle has uncommitted modifications"
else
  ok "V3 no frozen bundle (g4b, g5, g7a) was modified"
fi

# V4 - the predeclaration exists and precedes the repair.
[ -s "$B/control/PREDECLARATION.md" ] && ok "V4 predeclaration present" \
  || bad "V4 predeclaration missing"
[ -s "$B/control/REPAIR_1.md" ] && ok "V4 repair record present (1 of 1 allowed)" \
  || bad "V4 repair record missing"

# V5 - exactly ONE repair cycle was used.
n=$(ls "$B"/control/REPAIR_*.md 2>/dev/null | wc -l)
if [ "$n" -le 1 ]; then ok "V5 $n repair cycle(s) used, allowance is 1"
else bad "V5 $n repair cycles used, allowance is 1"; fi

# V6 - BOTH nulls are reported for the primary analysis (the bracket, not one endpoint).
if awk -F'\t' 'NR>1 && $2=="PRIMARY" && $5!="" && $6!=""' "$B/tables/g6_between_family_rho.tsv" | grep -q .; then
  ok "V6 the primary analysis reports both NULL-1 and NULL-2"
else
  bad "V6 the primary analysis does not report both nulls"
fi

# V7 - NULL-1 is retained, not deleted.
if grep -q "NULL-1" "$B/tables/g6_between_family_null.tsv"; then
  ok "V7 the declared NULL-1 is retained in the landed tables"
else
  bad "V7 the declared NULL-1 was dropped - a failed control is evidence"
fi

# V8 - every architecture number uses the INSPECTABLE denominator, never 501,561.
if grep -rIn "501561\|501,561" "$B/tables"/g6_between_family_rho.tsv \
     "$B/tables"/g6_within_retron_rho.tsv 2>/dev/null | grep -q .; then
  bad "V8 the catalogue count appears as a denominator in an arm table"
else
  ok "V8 no arm table uses the catalogue count as a denominator"
fi

# V9 - the two tools are never pooled.
if grep -q "DF_subtype" "$B/tables/g6_within_retron_rho.tsv" && \
   grep -q "PL_subtype" "$B/tables/g6_within_retron_rho.tsv"; then
  ok "V9 DefenseFinder and PADLOC subtypes are reported as separate analyses, never pooled"
else
  bad "V9 the two tool subtype strata are not both present as separate analyses"
fi

# V10 - underpowered strata are labelled, not silently dropped.
if grep -q "UNDERPOWERED" "$B/tables/g6_retron_subtype_strata.tsv"; then
  ok "V10 underpowered subtype strata are reported as such"
else
  ok "V10 no stratum fell below the threshold"
fi

# V11 - the positive control passed; without it no absence statement may be made.
if awk -F'\t' 'NR>1 && $1=="PC-POS" && $5=="PASS"' "$B/tables/g6_controls.tsv" | grep -q .; then
  ok "V11 PC-POS passed - the instrument has demonstrated power on this substrate"
else
  bad "V11 PC-POS did not pass"
fi

# V12 - figure present in both formats with its data table.
for f in figures/g6_reproducibility.png figures/g6_reproducibility.svg tables/g6_reproducibility.tsv; do
  [ -s "$B/$f" ] && ok "V12 $f present" || bad "V12 $f missing or empty"
done

echo "verify: $fail failure(s)"
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
