#!/usr/bin/env bash
# g4b verifier. FAIL-CLOSED.
#
#   verify.sh [work_dir]
#
# 1. the ten freeze tests: the mapper, the parameters, the schema, the crosswalk, the
#    identifier, and that each way of silently changing the science is caught;
# 2. the seven smoke checks, reproduced into a temp directory;
# 3. a diff of the regenerated smoke products against the landed ones.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
WORK="${1:-${TMPDIR:-/tmp}/verify_g4b_$$}"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$WORK/pycache"
mkdir -p "$WORK"
status=0

echo "=============================================================="
echo " 1. FREEZE TESTS"
echo "=============================================================="
"$PY" -B "$HERE/scripts/test_production_freeze.py" || status=1

echo
echo "=============================================================="
echo " 2. PRODUCTION SMOKE TEST (engineering only)"
echo "=============================================================="
bash "$HERE/scripts/run_smoke.sh" "$WORK/smoke" || status=1

echo
echo "=============================================================="
echo " 3. REVIEW-REPAIR CHECKS R1-R5 (engineering only)"
echo "=============================================================="
"$PY" -B "$HERE/scripts/check_repairs.py" "$WORK/repairs" || status=1

echo
echo "=============================================================="
echo " 4. REGENERATED SMOKE PRODUCTS vs LANDED"
echo "=============================================================="
for pair in "smoke.states.tsv:smoke_states.tsv" \
            "smoke.sequences.tsv:smoke_sequences.tsv" \
            "smoke.failures.tsv:smoke_failures.tsv" \
            ; do
    gen="$WORK/smoke/main/${pair%%:*}"
    landed="$HERE/tables/${pair##*:}"
    if [ ! -f "$gen" ]; then
        echo "FAIL  $gen not regenerated"; status=1; continue
    fi
    if diff -q "$landed" "$gen" >/dev/null; then
        echo "  ok    ${pair##*:}"
    else
        echo "FAIL  ${pair##*:} DRIFTED"; diff "$landed" "$gen" | head -6; status=1
    fi
done

# The smoke input must be the same population. It is regenerated from the registered loader,
# so a drift here means the source collection changed.
if diff -q "$HERE/tables/smoke_input.faa" "$WORK/smoke/smoke_input.faa" >/dev/null; then
    echo "  ok    smoke_input.faa"
else
    echo "FAIL  smoke_input.faa DRIFTED - the source sequence collection changed"; status=1
fi

# Provenance legitimately differs between runs (timestamps, host, paths, batch geometry).
# Only its DETERMINISTIC keys are compared - the instrument identity and the counts.
echo
echo "  provenance: comparing deterministic keys only"
"$PY" -B - "$HERE/tables/smoke_provenance.tsv" \
        "$WORK/smoke/main/smoke.provenance.tsv" <<'EOF' || status=1
import sys
# Keys that legitimately differ between two runs of the same data. `bundle_root_sha256`
# is volatile because landing an output changes the bundle root by construction; the
# instrument digest, which covers code/ and control/, is NOT volatile and is compared.
VOLATILE = {"started_utc", "finished_utc", "host", "input_path", "metadata_path", "shard",
            "reject_ids_path", "bundle_root_sha256", "bundle_root_status"}
def load(p):
    d = {}
    with open(p) as f:
        f.readline()
        for ln in f:
            k, v = ln.rstrip("\n").split("\t", 1)
            d[k] = v
    return d
a, b = load(sys.argv[1]), load(sys.argv[2])
keys = (set(a) | set(b)) - VOLATILE
bad = [k for k in sorted(keys) if a.get(k) != b.get(k)]
for k in bad:
    print(f"FAIL  provenance {k}: landed {a.get(k)!r} != regenerated {b.get(k)!r}")
print(f"  ok    {len(keys) - len(bad)}/{len(keys)} deterministic provenance keys match")
sys.exit(1 if bad else 0)
EOF

echo
if [ $status -eq 0 ]; then
    echo "g4b VERIFY OK"
else
    echo "g4b VERIFY FAILED"
fi
echo "artefacts: $WORK"
exit $status
