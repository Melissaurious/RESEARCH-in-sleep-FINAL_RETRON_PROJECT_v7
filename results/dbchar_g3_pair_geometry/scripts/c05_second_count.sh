#!/usr/bin/env bash
# c05 - the independent second count for g3 (WA-D.3).
#
# One awk pass over the raw bytes finds every ncRNA element, pairs it with the record's
# rt_gene, and applies the SAME declared geometry rules as g3lib - implemented again, in a
# different language, over different input. No Python, no parquet, no g3lib.
#   upstream/downstream: transcription-relative to the RT strand
#   overlapping:         closed-interval intersection
#   gap:                 bases strictly between (abutting = 0)
set -euo pipefail
CORPUS="$1"; OUT="$2"; PROCS="${3:-16}"
mkdir -p "$OUT/second" "$OUT/second/parts"
export LC_ALL=C

one() {
  f="$1"; o="$2"; b="$(basename "$f")"
  awk -v B="$b" '
    function block(line, key,   i, s, e) {
      i = index(line, "\"" key "\": {"); if (i == 0) return ""
      s = substr(line, i + length(key) + 5); e = index(s, "}")
      return e ? substr(s, 1, e - 1) : ""
    }
    function num(blk, key,   r) {
      if (!match(blk, "\"" key "\": -?[0-9]+")) return ""
      r = substr(blk, RSTART, RLENGTH); sub(/^"[a-z_]+": /, "", r); return r + 0
    }
    function str(blk, key,   r) {
      if (!match(blk, "\"" key "\": \"[^\"]*\"")) return ""
      r = substr(blk, RSTART, RLENGTH); sub(/^"[a-z_]+": "/, "", r); sub(/"$/, "", r); return r
    }
    {
      rt = block($0, "rt_gene")
      rs = num(rt, "start"); re = num(rt, "end"); st = str(rt, "strand")
      rest = $0; n_in_line = 0
      while ((i = index(rest, "\"ncrna_id\": \"")) > 0) {
        rest = substr(rest, i + 12)
        # the element continues to the next "}" that closes its own first object level;
        # start/end/strand are the 3rd-5th keys of the element, before any nested object
        head = substr(rest, 1, 400)
        ns = num(head, "start"); ne = num(head, "end"); nst = str(head, "strand")
        if (ns == "" || ne == "") continue
        n++; n_in_line++
        if (ns <= re && rs <= ne) { overlap++ }
        else {
          before = (ne < rs)
          if (st == "+" || st == "-") {
            up = (before == (st == "+"))
            if (up) upstream++; else downstream++
          } else undetermined++
          gap = before ? (rs - ne - 1) : (ns - re - 1)
          if (gap == 0) abutting++
          if (gap <= 100) le100++
        }
        if (nst != "" && st != "") { if (nst == st) same++; else opposite++ }
      }
      if (n_in_line > 0) rec_with_calls++
      if (n_in_line > 1) rec_multi++
    }
    END { printf "%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n", B, n, upstream, downstream,
          overlap, undetermined, same, opposite, abutting, le100, rec_with_calls }
  ' "$f" > "$o/second/parts/g_$b"
}
export -f one

find "$CORPUS" -maxdepth 1 -type f -name '*.jsonl' ! -name 'master_ncRNA-anchored_merged.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"

{ printf 'measure\tn\troute\n'
  cat "$OUT"/second/parts/g_* | awk -F'\t' '
    {n+=$2; u+=$3; d+=$4; o+=$5; x+=$6; s+=$7; p+=$8; a+=$9; l+=$10; r+=$11}
    END {printf "ncrna_placements_total\t%d\tawk element scan\n", n
         printf "direction_upstream\t%d\tawk, transcription-relative\n", u
         printf "direction_downstream\t%d\tawk, transcription-relative\n", d
         printf "direction_overlapping\t%d\tawk, closed-interval intersection\n", o
         printf "direction_undetermined\t%d\tawk\n", x
         printf "same_strand\t%d\tawk\n", s
         printf "opposite_strand\t%d\tawk\n", p
         printf "abutting_gap_zero\t%d\tawk, bases strictly between\n", a
         printf "gap_le_100bp\t%d\tawk, bases strictly between\n", l
         printf "records_carrying_at_least_one_call\t%d\tawk\n", r}'
} > "$OUT/second/c05_geometry.tsv"
rm -rf "$OUT/second/parts"
cat "$OUT/second/c05_geometry.tsv"
