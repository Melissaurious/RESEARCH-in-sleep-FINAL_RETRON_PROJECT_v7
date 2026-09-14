#!/usr/bin/env bash
# s03 - the denominator's independent second count (WA-D.3).
#
# Shares NO code with s02: no Python, no JSON parser, no g1lib. Coreutils `wc -l` counts
# newlines per file; `LC_ALL=C grep -o` extracts every serialised `"anchor_type": <v>` and
# `"source_database": <v>` token as bytes, one process per file. The per-record joint
# (anchor x database) is recovered by pairing the two tokens that grep emits per line in
# order; a line carrying a key twice or not at all surfaces as a count disagreement, never
# as a silent correction.
#
#   bash s03_second_count.sh <corpus_dir> <out_dir> [procs]
set -euo pipefail
CORPUS="$1"; OUT="$2"; PROCS="${3:-16}"
mkdir -p "$OUT/second"
export LC_ALL=C

one() {  # $1 = file path, $2 = out dir
  f="$1"; o="$2"; b="$(basename "$f")"
  n=$(wc -l < "$f")
  printf '%s\t%s\n' "$b" "$n" > "$o/second/wc_${b}.tsv"
  # -n keeps the line number, so tokens are grouped per line without trusting order alone
  grep -noE '"(anchor_type|source_database)": ("[^"]*"|null)' "$f" \
    | awk -F: -v b="$b" '
        { ln=$1; tok=substr($0, length(ln)+2)
          key = (tok ~ /^"anchor_type"/) ? "a" : "d"
          val = tok; sub(/^"[a-z_]+": /, "", val); gsub(/"/, "", val)
          if (key == "a") { na[ln]++; A[ln]=val } else { nd[ln]++; D[ln]=val }
          seen[ln]=1 }
        END {
          for (l in seen) {
            a = (na[l] == 1) ? A[l] : ("<" na[l]+0 " anchor tokens>")
            d = (nd[l] == 1) ? D[l] : ("<" nd[l]+0 " database tokens>")
            c[a "\t" d]++
          }
          for (k in c) printf "%s\t%s\t%d\n", b, k, c[k]
        }' > "$o/second/grep_${b}.tsv"
}
export -f one

find "$CORPUS" -maxdepth 1 -type f -name '*.jsonl' -print0 \
  | xargs -0 -P "$PROCS" -I{} bash -c 'one "$1" "$2"' _ {} "$OUT"

{ printf 'source_file\tn_newlines_wc\n'; cat "$OUT"/second/wc_*.tsv | sort; } > "$OUT/second/s03_wc_lines.tsv"
{ printf 'source_file\tanchor_type_token\tsource_database_token\tn_lines\n'; cat "$OUT"/second/grep_*.tsv | sort; } \
  > "$OUT/second/s03_grep_anchor_db.tsv"
rm -f "$OUT"/second/wc_*.tsv "$OUT"/second/grep_*.tsv
echo "s03 done: $(($(wc -l < "$OUT/second/s03_wc_lines.tsv") - 1)) files"
