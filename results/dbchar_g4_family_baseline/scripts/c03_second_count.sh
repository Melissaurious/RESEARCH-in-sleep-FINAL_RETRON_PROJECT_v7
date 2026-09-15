#!/usr/bin/env bash
# c03 - the independent second count for g4 (WA-D.3).
#
# awk slices the RT protein out of each raw record and `sort -u` counts the DISTINCT sequences
# per source file, with their length range. No Python, no parquet, no g4 code. The unit is the
# same one b01 reports in g4_exact_rt_per_family_label.tsv: distinct RT sequences per file.
set -euo pipefail
CORPUS="$1"; OUT="$2"; PROCS="${3:-16}"
mkdir -p "$OUT/second" "$OUT/second/parts"
export LC_ALL=C
: "${TMPDIR:=/tmp}"

# Each worker writes its OWN file. Sharing one pipe corrupts the output: an RT protein can
# exceed the 4 KB pipe buffer, and concurrent writers then interleave inside a single line.
one() {
  f="$1"; o="$2"; b="$(basename "$f")"
  lab="${b#master_}"; lab="${lab%_merged_oriented.jsonl}"
  awk -v L="$lab" '
    {
      i = index($0, "\"rt_gene\": {"); if (i == 0) next
      s = substr($0, i + 12); e = index(s, "}"); if (e == 0) next
      blk = substr(s, 1, e - 1)
      if (!match(blk, /"sequence": "[^"]*"/)) next
      q = substr(blk, RSTART, RLENGTH); sub(/^"sequence": "/, "", q); sub(/"$/, "", q)
      sub(/\*$/, "", q)                       # the declared exact-RT string
      print L "\t" q
    }' "$f" > "$o/second/parts/seq_$b"
}
export -f one

find "$CORPUS" -maxdepth 1 -type f -name '*.jsonl' ! -name 'master_ncRNA-anchored_merged.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"
cat "$OUT"/second/parts/seq_* \
  | sort -u -S 12G --parallel="$PROCS" \
  | awk -F'\t' '{n[$1]++; l=length($2); if (mn[$1]=="" || l<mn[$1]) mn[$1]=l; if (l>mx[$1]) mx[$1]=l}
      END {for (k in n) printf "%s\t%d\t%d\t%d\n", k, n[k], mn[k], mx[k]}' \
  | sort > "$OUT/second/parts/per_label.tsv"

{ printf 'file_label\tn_exact_rt\tmin_aa_len\tmax_aa_len\troute\n'
  awk -F'\t' '{printf "%s\t%s\t%s\t%s\tawk slice + sort -u\n", $1, $2, $3, $4}' \
      "$OUT/second/parts/per_label.tsv"; } > "$OUT/second/c03_exact_rt_per_label.tsv"
{ printf 'measure\tn\troute\n'
  awk -F'\t' '{s+=$2} END {printf "sum_of_distinct_exact_rt_per_label\t%d\tawk + sort -u\n", s}' \
      "$OUT/second/parts/per_label.tsv"; } > "$OUT/second/c03_totals.tsv"
rm -rf "$OUT/second/parts"
head -5 "$OUT/second/c03_exact_rt_per_label.tsv"
cat "$OUT/second/c03_totals.tsv"
