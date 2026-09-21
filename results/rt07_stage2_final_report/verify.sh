#!/usr/bin/env bash
# Independent checks on the landed reporting bundle. Every one can fail. None recomputes science.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
B="results/rt07_stage2_final_report"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python
fail=0
ok()  { printf "  PASS  %s\n" "$1"; }
bad() { printf "  FAIL  %s\n" "$1"; fail=$((fail+1)); }

echo "verify: rt07_stage2_final_report"

# V1 - the eight final statuses in T1 are exactly the erratum's, label for label.
if "$PY" - <<'E' >/dev/null 2>&1
import csv
t = {r["label"]: r["final_status"] for r in csv.DictReader(open("results/rt07_stage2_final_report/tables/stage2_rt0_rt7_final.tsv"), delimiter="\t")}
e = {r["historical_label"]: r["terminal_status"] for r in csv.DictReader(open("docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv"), delimiter="\t")}
assert t == e and len(t) == 8, (t, e)
E
then ok "V1 T1 statuses equal the governing erratum for all 8 labels"
else bad "V1 T1 statuses differ from docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv"; fi

# V2 - the production crosswalk is still UNRESOLVED in every row (the instrument emits state_id only).
if python3 -c "import sys; sys.path.insert(0,'results/rt07_g4b_production_mapper/code'); \
from rtmap import crosswalk as C; C.assert_unresolved_until_g7()" >/dev/null 2>&1; then
  ok "V2 production crosswalk UNRESOLVED in all 8 rows"
else bad "V2 production crosswalk no longer UNRESOLVED"; fi

# V3 - no superseded or withdrawn wording anywhere in the package's outputs.
pat='RT0[[:space:]]*=[[:space:]]*M1|R86[[:space:]]*[-–][[:space:]]*R364|bracket(s|ed)? the truth|structure is real|three routes agree|best-determined label|significant at 1[[:space:]]*%|not an artefact of the mapper|stated domain junction'
if grep -rIiEl "$pat" "$B/report" "$B/tables" "$B/DELIVERABLES_INDEX.md" >/dev/null 2>&1; then
  bad "V3 superseded wording present: $(grep -rIiEl "$pat" "$B/report" "$B/tables" "$B/DELIVERABLES_INDEX.md" | tr '\n' ' ')"
else ok "V3 no superseded or withdrawn wording in report/, tables/ or the index"; fi

# V4 - every review verdict/score is still verbatim in its governing record.
if "$PY" - <<'E' >/dev/null 2>&1
import csv, subprocess
for r in csv.DictReader(open("results/rt07_stage2_final_report/tables/stage2_review_ledger.tsv"), delimiter="\t"):
    rec = r["record"]
    txt = subprocess.run(["git", "show", "-s", "--format=%B", rec[4:]], capture_output=True, text=True).stdout \
        if rec.startswith("git:") else open(rec).read()
    assert r["verified_literal"] in txt.replace("\n", " "), rec
E
then ok "V4 every review-ledger literal is present in its record"
else bad "V4 a review-ledger literal is missing from its record"; fi

# V5 - every input hash in INPUTS.tsv still matches (the frozen record did not move).
n=0; m=0
while IFS=$'\t' read -r p s _ _; do
  [ "$p" = "path" ] && continue; n=$((n+1))
  [ "$(sha256sum "$p" | cut -d' ' -f1)" = "$s" ] || { m=$((m+1)); echo "    changed: $p"; }
done < "$B/INPUTS.tsv"
if [ "$m" -eq 0 ] && [ "$n" -gt 0 ]; then ok "V5 $n/$n input hashes unchanged"
else bad "V5 $m of $n inputs changed since the report was built"; fi

# V6 - no frozen Stage-2 bundle has uncommitted changes.
if git status --porcelain -- results/rt07_g1_history_and_definition results/rt07_g2_reference_reconstruction \
   results/rt07_g3_prior_method_replication results/rt07_g4a_repaired results/rt07_g4b_production_mapper \
   results/rt07_ug25_confirmatory results/FINAL_PRE_UG25_VALIDATION_BUNDLE results/rt07_g5a_eligibility_census \
   results/rt07_g5_catalogue_application results/rt07_g6_family_architecture results/rt07_g7a_rt0_rt7_bridge \
   docs/errata docs/decisions | grep -q .; then
  bad "V6 a frozen bundle or governing record has uncommitted changes"
else ok "V6 frozen bundles and governing records are clean"; fi

# V7 - g6 is never described as discovery; the required descriptive framing is present.
if grep -q "descriptive concordance" "$B/report/STAGE2_TECHNICAL_REPORT.md" \
   && grep -q "descriptive concordance" "$B/report/THESIS_RESULTS.md" \
   && ! grep -rIiqE "(demonstrates|shows|establishes) (independent )?(biological )?family (structure|discovery)" "$B/report"; then
  ok "V7 g6 framed as descriptive concordance; no discovery claim"
else bad "V7 g6 framing"; fi

# V8 - every resolved value is referenced by a lookup that still resolves (fresh rebuild into scratch).
T="$(mktemp -d)"
if "$PY" "$B/scripts/build.py" --root . --out "$T" >/dev/null 2>&1 \
   && cmp -s "$T/tables/stage2_resolved_values.tsv" "$B/tables/stage2_resolved_values.tsv"; then
  ok "V8 all values re-resolve identically"
else bad "V8 resolved values differ on a fresh rebuild"; fi

# V9 - the pinned source-of-record commit is an ancestor of HEAD.
if git merge-base --is-ancestor 94a1a78868d6039297c78b3fdcc047d633d6645e HEAD; then
  ok "V9 source-of-record 94a1a78 is an ancestor of HEAD"
else bad "V9 source-of-record commit is not in this history"; fi

echo
if [ "$fail" -eq 0 ]; then echo "VERIFY OK"; else echo "VERIFY FAILED: $fail check(s)"; fi
exit "$fail"
