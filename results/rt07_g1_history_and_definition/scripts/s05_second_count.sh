#!/usr/bin/env bash
# rt07_g1 step 5 - the independent second count (WA-D.3).
#
# Route A is the Python census of step 2: compiled regexes over NFKC-normalised text.
# Route B is this script: tr/grep/wc over the same extracted text, sharing no code with
# route A - not a library, not a helper, not the normalisation. If the two routes disagree
# the disagreement is landed, because a count nobody could reproduce a second way is a
# number with one witness.
#
# Newlines are folded to spaces first so that a phrase broken across a PDF line is counted
# by both routes; that is the only normalisation route B does.
#
# Usage: s05_second_count.sh <work-dir> <out-dir>
set -euo pipefail
WORK="$1"
OUT="$2"
CENSUS="$OUT/g1_token_census.tsv"
DEST="$OUT/g1_second_counts.tsv"

printf 'check\tscope\troute_a\tvalue_a\troute_b\tvalue_b\tdelta_a_minus_b\tagreement\tunit\tdenominator\n' > "$DEST"

# check_id | source_id | region_id | extended-regex for route B
CHECKS='
subdomain_0_zimmerly|zimmerly2001|domain_0|(sub)?domains? 0([^0-9]|$)
subdomain_5_zimmerly|zimmerly2001|domain_5|(sub)?domains? 5([^0-9]|$)
domain_x_zimmerly|zimmerly2001|domain_X|domain X
domain_1_xiong|xiong1990|domain_1|(sub)?domains? 1([^0-9]|$)
domain_x_simon|simon2008|domain_X|domain X
rt0_blocker|blocker2005|rt0_spelling|RT-?0([^0-9]|$)
rt1_blocker|blocker2005|rt1_spelling|RT-?1([^0-9]|$)
motif_a_poch|poch1989|motif_A|motifs? A([^A-Za-z]|$)
subdomain_any_alignment|align000044|domain_0|(sub)?domains? 0([^0-9]|$)
'

while IFS='|' read -r check src region pat; do
  [ -z "${check// }" ] && continue
  a=$(awk -F'\t' -v s="$src" -v r="$region" \
        'NR==1{for(i=1;i<=NF;i++)h[$i]=i; next} $h["source_id"]==s && $h["region_id"]==r {print $h["n_literal_raw"]}' \
        "$CENSUS")
  # grep exits 1 on no match, and 'no match' is a legitimate result here - the alignment
  # check exists precisely to confirm a zero. `|| true` keeps pipefail from turning an
  # expected zero into a dead script.
  b=$( { tr '\n' ' ' < "$WORK/text/${src}.raw.txt" | grep -o -E -i "$pat" || true; } | wc -l | tr -d ' ')
  d=$(( a - b ))
  if [ "$d" -eq 0 ]; then agree=AGREE; else agree=DIFFER; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$check" "$src:$region" "python_regex_census" "$a" "tr_grep_wc" "$b" "$d" "$agree" \
    "literal namings of one region in one source" \
    "9 spot-checks spanning every source and both spellings" >> "$DEST"
done <<< "$CHECKS"

n=$(( $(wc -l < "$DEST") - 1 ))
differ=$(awk -F'\t' 'NR>1 && $8=="DIFFER"' "$DEST" | wc -l | tr -d ' ')
echo "second count: $n check(s), $differ disagreement(s) - all landed either way"
