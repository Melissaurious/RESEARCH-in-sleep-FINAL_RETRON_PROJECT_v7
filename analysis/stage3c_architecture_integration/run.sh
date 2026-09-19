#!/usr/bin/env bash
# Stage 3C — regenerate every landed table and figure from the hashed frozen inputs.
#
#   bash run.sh
#
# Reproducibility, per product (BS-3):
#   DETERMINISTIC          every TSV, every figure and every figure data table, including the frozen
#                          mapper's state and sequence tables.
#   NOT BYTE-REPRODUCIBLE  tables/mapper/s3c.provenance.tsv — host, paths and timestamps, written by
#                          the frozen instrument itself and declared exactly as g4b declares its own.
#   NOT RE-RETRIEVED       the literature retrieval was a one-time audited acquisition over the
#                          network. Its products are LANDED (XY_REGION_EVIDENCE.tsv,
#                          tables/C_literature_boundaries_retrieved.tsv, tables/C_sources.tsv,
#                          tables/D_sources.tsv, tables/*_audit_notes.md, tables/D_source_cache_hashes.tsv)
#                          and are inputs to s09; this script never re-fetches them.
#   AUTHORED               CONTRADICTIONS_AND_UNCERTAINTY.tsv, CLAIM_EVIDENCE_MATRIX.tsv,
#                          STAGE3C_DECISION_REPORT.md, README.md — written, not computed.
#
# Kill criteria are enforced inside the scripts: K1/K2/K4 in s00, K3/K6 in s02, K5/K7 in s04.
# Any of them exits non-zero and stops the run.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="${TMPDIR:-/tmp}/s3c_mpl"
mkdir -p "$MPLCONFIGDIR"

"$PY" "$HERE/scripts/s00_inputs.py"             # g0  input provenance          (K1, K2, K4)
"$PY" "$HERE/scripts/s01_sequences.py"          # g0  modelled sequences, verified by two paths
"$PY" "$HERE/scripts/s02_catalytic_join.py"     # gA  catalytic join            (K3, K6)
"$PY" "$HERE/scripts/s03_catalytic_summary.py"  # gA  analysis
"$PY" "$HERE/scripts/s04_states_join.py"        # gB  frozen mapper + join      (K5, K7)
"$PY" "$HERE/scripts/s05_states_summary.py"     # gB  analysis
"$PY" "$HERE/scripts/s06_termini.py"            # gE  termini / insertions / fusions
"$PY" "$HERE/scripts/s07_xy_regions.py"         # gD  X/Y scan + controls
"$PY" "$HERE/scripts/s08_xy_summary.py"         # gD  analysis
"$PY" "$HERE/scripts/s09_boundary_audit.py"     # gC  boundary provenance audit + overlap
"$PY" "$HERE/scripts/s10_figures.py"            # figures, from landed tables only
"$PY" "$HERE/scripts/s11_package.py"            # MANIFEST.tsv / INPUTS.tsv / OUTPUTS.tsv
