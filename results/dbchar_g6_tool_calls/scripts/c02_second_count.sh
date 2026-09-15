#!/usr/bin/env bash
# c02 - the independent second count for g6 (WA-D.3): detected_by combinations and the
# subtype case classes, straight from the raw bytes with awk. No Python, no parquet.
set -euo pipefail
CORPUS="$1"; OUT="$2"; PROCS="${3:-16}"
mkdir -p "$OUT/second" "$OUT/second/parts"
export LC_ALL=C
one() {
  f="$1"; o="$2"; b="$(basename "$f")"
  awk -v B="$b" '
    { n++
      m = index($0, "\"detected_by\": [")
      d = ""
      if (m > 0) { s = substr($0, m + 16); e = index(s, "]"); d = substr(s, 1, e - 1) }
      my = (index(d, "\"myRT\"") > 0); pl = (index(d, "\"PADLOC\"") > 0); df = (index(d, "\"DefenseFinder\"") > 0)
      combo = ""
      if (my) combo = "myRT"
      if (pl) combo = (combo == "" ? "PADLOC" : combo "|PADLOC")
      if (df) combo = (combo == "" ? "DefenseFinder" : combo "|DefenseFinder")
      c[combo]++
      # subtypes: capital-initial = DefenseFinder, lowercase = PADLOC (the declared case rule)
      k = index($0, "\"system_subtypes\": [")
      if (k > 0) { s2 = substr($0, k + 20); e2 = index(s2, "]"); sub_ = substr(s2, 1, e2 - 1)
        hasU = 0; hasL = 0
        while (match(sub_, /"[^"]+"/)) { v = substr(sub_, RSTART + 1, RLENGTH - 2)
          ch = substr(v, 1, 1)
          if (ch ~ /[A-Z]/) hasU = 1; else if (ch ~ /[a-z]/) hasL = 1
          sub_ = substr(sub_, RSTART + RLENGTH) }
        if (hasU) nU++
        if (hasL) nL++
        if (hasU && hasL) nB++ }
    }
    END { for (k in c) printf "COMBO\t%s\t%s\t%d\n", B, k, c[k]
          printf "SUB\t%s\tdefensefinder_style\t%d\n", B, nU
          printf "SUB\t%s\tpadloc_style\t%d\n", B, nL
          printf "SUB\t%s\tboth_styles\t%d\n", B, nB
          printf "SUB\t%s\trecords\t%d\n", B, n }' "$f" > "$o/second/parts/t_$b"
}
export -f one
find "$CORPUS" -maxdepth 1 -type f -name 'master_Retron_merged_oriented.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"
{ printf 'measure\tkey\tn\troute\n'
  awk -F'\t' '$1=="COMBO" {c[$3]+=$4} $1=="SUB" {s[$3]+=$4}
    END {for (k in c) printf "detected_by_combination\t%s\t%d\tawk over master_Retron\n", k, c[k]
         for (k in s) printf "subtype_case_class\t%s\t%d\tawk over master_Retron\n", k, s[k]}' \
    "$OUT"/second/parts/t_* | sort; } > "$OUT/second/c02_tool_counts.tsv"
rm -rf "$OUT/second/parts"
cat "$OUT/second/c02_tool_counts.tsv"
