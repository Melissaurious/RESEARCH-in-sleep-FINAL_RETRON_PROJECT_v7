#!/usr/bin/env python3
"""seal - writes INPUTS.tsv, MANIFEST.tsv and (last) OUTPUTS.tsv for g6."""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g6lib import BUNDLE, DERIVED, G5, PROJ, sha256, write_tsv  # noqa: E402

INPUT_FILES = [
    os.path.join(G5, "g5_states.parquet"),
    os.path.join(G5, "g5_sequences.parquet"),
    os.path.join(G5, "g5_catalytic.parquet"),
    os.path.join(G5, "g5_metadata_crosswalk.parquet"),
    os.path.join(DERIVED, "rt_exact_v1.faa"),
    os.path.join(DERIVED, "rt_tool_calls_v1.parquet"),
    os.path.join(PROJ, "results", "rt07_g4b_production_mapper", "control",
                 "FROZEN_ANCHORS.tsv"),
    os.path.join(PROJ, "results", "rt07_g4b_production_mapper", "control",
                 "CATALYTIC_STATE_FROZEN.tsv"),
    os.path.join(BUNDLE, "control", "PREDECLARATION.md"),
    os.path.join(BUNDLE, "control", "REPAIR_1.md"),
]

MANIFEST = [
    ("tables/g6_clustering_reuse_audit.tsv", "scripts/s01_clustering.py", "audit item",
     "the reuse decision"),
    ("tables/g6_clustering_resource.tsv", "scripts/s01_clustering.py", "clustering run",
     "3 declared identities"),
    ("tables/g6_call_state_totals.tsv", "scripts/s02_matrix.py",
     "exact RT x frozen anchor state", "55,407,150 state calls"),
    ("tables/g6_between_family_rho.tsv", "scripts/s03_between_family.py", "analysis",
     "primary plus declared controls"),
    ("tables/g6_between_family_null.tsv", "scripts/s03_between_family.py", "null distribution",
     "both nulls per analysis"),
    ("tables/g6_family_state_profiles.tsv", "scripts/s03_between_family.py", "family",
     "qualifying families"),
    ("tables/g6_cluster_family_purity.tsv", "scripts/s03_between_family.py", "cluster",
     "clusters at identity 0.90"),
    ("tables/g6_within_retron_rho.tsv", "scripts/s04_within_retron.py", "analysis",
     "3 declared labellings"),
    ("tables/g6_within_retron_null.tsv", "scripts/s04_within_retron.py", "null distribution",
     "one per labelling"),
    ("tables/g6_retron_subtype_strata.tsv", "scripts/s04_within_retron.py", "subtype stratum",
     "per tool, own denominator, never pooled"),
    ("tables/g6_controls.tsv", "scripts/s05_controls.py", "control", "2 declared controls"),
    ("tables/g6_pc_pos_catalytic.tsv", "scripts/s05_controls.py", "family",
     "CAT_STATE-MAPPED in that family-half"),
    ("figures/g6_reproducibility.png", "scripts/s06_figure.py", "analysis", "all analyses"),
    ("figures/g6_reproducibility.svg", "scripts/s06_figure.py", "analysis", "all analyses"),
    ("tables/g6_reproducibility.tsv", "scripts/s06_figure.py", "analysis", "all analyses"),
    ("tables/g6_terminal_decision.tsv", "scripts/s07_decision.py", "arm x labelling",
     "2 arms"),
    ("tables/g6_summary.tsv", "scripts/s07_decision.py", "resolved value", "see each row"),
]


def do_inputs():
    rows = []
    for p in INPUT_FILES:
        if not os.path.exists(p):
            rows.append(dict(path=p, sha256="MISSING", bytes="", mtime=""))
            continue
        st = os.stat(p)
        rows.append(dict(path=p, sha256=sha256(p), bytes=st.st_size,
                         mtime=datetime.datetime.fromtimestamp(
                             st.st_mtime, datetime.timezone.utc
                         ).strftime("%Y-%m-%dT%H:%M:%SZ")))
    write_tsv(os.path.join(BUNDLE, "INPUTS.tsv"), ["path", "sha256", "bytes", "mtime"], rows)
    bad = [r for r in rows if r["sha256"] == "MISSING"]
    print(f"seal: INPUTS.tsv {len(rows)} inputs, {len(bad)} missing")
    for r in rows:
        # Anti-circularity: the sealed external gate must never appear as an input.
        # Matched on the BUNDLE name `rt07_g7a` (underscores), not the loose substring "g7a":
        # this work happens inside a git worktree directory literally named
        # `rt07-g7a-bridge` (hyphens), so every path in the repo contains "g7a" and the loose
        # form would flag the g6 bundle's own control files. The underscore form is the
        # bundle, the hyphen form is the working directory, and only the first is a breach.
        assert "rt07_g7a" not in r["path"], f"sealed-context breach: {r['path']}"
    if bad:
        raise SystemExit("seal: an input is missing: " + ", ".join(r["path"] for r in bad))


def do_manifest():
    write_tsv(os.path.join(BUNDLE, "MANIFEST.tsv"),
              ["artifact", "script", "command", "unit", "denominator"],
              [dict(artifact=a, script=s, command=f"python3 {os.path.basename(s)}",
                    unit=u, denominator=d) for a, s, u, d in MANIFEST])
    missing = [a for a, *_ in MANIFEST if not os.path.exists(os.path.join(BUNDLE, a))]
    print(f"seal: MANIFEST.tsv {len(MANIFEST)} artifacts, {len(missing)} missing")
    if missing:
        raise SystemExit("seal: manifest names a missing artifact: " + ", ".join(missing))


def do_outputs():
    rows = []
    for dirpath, dirnames, filenames in os.walk(BUNDLE):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, BUNDLE)
            if rel == "OUTPUTS.tsv":
                continue
            rows.append(dict(path=rel, sha256=sha256(full), bytes=os.path.getsize(full)))
    rows.sort(key=lambda r: r["path"])
    write_tsv(os.path.join(BUNDLE, "OUTPUTS.tsv"), ["path", "sha256", "bytes"], rows)
    print(f"seal: OUTPUTS.tsv {len(rows)} files sealed")


if __name__ == "__main__":
    {"inputs": do_inputs, "manifest": do_manifest, "outputs": do_outputs}[sys.argv[1]]()
