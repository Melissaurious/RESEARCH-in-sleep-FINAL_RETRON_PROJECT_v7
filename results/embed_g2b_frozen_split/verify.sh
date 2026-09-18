#!/usr/bin/env bash
# embed_g2b - reconstruct the frozen split from SPLIT_MANIFEST.json and require exact equality.
# The seeded-bad run comes FIRST: a verifier that cannot fail is not evidence (PRINCIPLES §13).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python

echo "== seeded-bad: the verifier MUST reject a corrupted reconstruction"
if ! "$PY" "$HERE/scripts/s07_verify_split.py" --seed-bad > /dev/null 2>&1; then
  echo "FATAL: the verifier ACCEPTED a corrupted split. It is broken; a pass proves nothing." >&2
  exit 1
fi
echo "   rejected, as required"
echo
echo "== real verification"
"$PY" "$HERE/scripts/s07_verify_split.py"
