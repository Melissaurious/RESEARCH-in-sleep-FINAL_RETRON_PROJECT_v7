#!/usr/bin/env python3
"""s3c packaging — MANIFEST.tsv, INPUTS.tsv, OUTPUTS.tsv, laid out per BUNDLE_SPEC.

`unit` and `denominator` must SAY something (BS-17): where an artefact carries no rate, the value is
`n/a - <why>`, never blank.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

SCRIPT_OF = [
    ("INPUT_PROVENANCE.tsv", "scripts/s00_inputs.py", "python3 scripts/s00_inputs.py"),
    ("tables/chain_sequences.tsv", "scripts/s01_sequences.py", "python3 scripts/s01_sequences.py"),
    ("tables/chain_index_map.tsv", "scripts/s01_sequences.py", "python3 scripts/s01_sequences.py"),
    ("tables/chains.faa", "scripts/s01_sequences.py", "python3 scripts/s01_sequences.py"),
    ("STRUCTURE_STAGE3B_CROSSWALK.tsv", "scripts/s02_catalytic_join.py", "python3 scripts/s02_catalytic_join.py"),
    ("tables/A_residue_join.tsv", "scripts/s02_catalytic_join.py", "python3 scripts/s02_catalytic_join.py"),
    ("tables/A_", "scripts/s03_catalytic_summary.py", "python3 scripts/s03_catalytic_summary.py"),
    ("STRUCTURE_STAGE2_CROSSWALK.tsv", "scripts/s04_states_join.py", "python3 scripts/s04_states_join.py"),
    ("tables/B_state_residue_join.tsv", "scripts/s04_states_join.py", "python3 scripts/s04_states_join.py"),
    ("tables/B_unit_block_membership.tsv", "scripts/s04_states_join.py", "python3 scripts/s04_states_join.py"),
    ("tables/B_control_K5_ltra.tsv", "scripts/s04_states_join.py", "python3 scripts/s04_states_join.py"),
    ("tables/mapper/", "scripts/s04_states_join.py",
     "results/rt07_g4b_production_mapper/code/rtmap/run_mapper.py --in tables/chains.faa --shard s3c"),
    ("tables/B_", "scripts/s05_states_summary.py", "python3 scripts/s05_states_summary.py"),
    ("TERMINI_FUSION_SUMMARY.tsv", "scripts/s06_termini.py", "python3 scripts/s06_termini.py"),
    ("tables/E_", "scripts/s06_termini.py", "python3 scripts/s06_termini.py"),
    ("XY_REGION_ANNOTATIONS.tsv", "scripts/s07_xy_regions.py", "python3 scripts/s07_xy_regions.py"),
    ("tables/D_controls.tsv", "scripts/s07_xy_regions.py", "python3 scripts/s07_xy_regions.py"),
    ("tables/D_na_contacts_by_region.tsv", "scripts/s07_xy_regions.py", "python3 scripts/s07_xy_regions.py"),
    ("tables/D_summary.tsv", "scripts/s08_xy_summary.py", "python3 scripts/s08_xy_summary.py"),
    ("tables/D_region_y", "scripts/s08_xy_summary.py", "python3 scripts/s08_xy_summary.py"),
    ("LITERATURE_BOUNDARY_AUDIT.tsv", "scripts/s09_boundary_audit.py", "python3 scripts/s09_boundary_audit.py"),
    ("tables/C_overlap.tsv", "scripts/s09_boundary_audit.py", "python3 scripts/s09_boundary_audit.py"),
    ("tables/C_summary.tsv", "scripts/s09_boundary_audit.py", "python3 scripts/s09_boundary_audit.py"),
    ("tables/C_reference_disagreement.tsv", "scripts/s09_boundary_audit.py", "python3 scripts/s09_boundary_audit.py"),
    ("figures/", "scripts/s10_figures.py", "python3 scripts/s10_figures.py"),
    ("tables/F", "scripts/s10_figures.py", "python3 scripts/s10_figures.py"),
    ("MANIFEST.tsv", "scripts/s11_package.py", "python3 scripts/s11_package.py"),
    ("INPUTS.tsv", "scripts/s11_package.py", "python3 scripts/s11_package.py"),
]
# retrieved / authored artefacts: no producing script in this bundle, and that is stated, not blank
RETRIEVED = {
    "XY_REGION_EVIDENCE.tsv": "one-time audited literature retrieval (Europe PMC / NCBI), quotes verbatim",
    "tables/C_literature_boundaries_retrieved.tsv": "one-time audited literature retrieval",
    "tables/C_sources.tsv": "one-time audited literature retrieval",
    "tables/D_sources.tsv": "one-time audited literature retrieval",
    "tables/C_audit_notes.md": "one-time audited literature retrieval",
    "tables/D_audit_notes.md": "one-time audited literature retrieval",
    "tables/D_source_cache_hashes.tsv": "sha256 of each retrieved text, cached in disposable scratch",
}
AUTHORED = {
    "CONTRADICTIONS_AND_UNCERTAINTY.tsv": "authored register of contradictions and uncertainty",
    "CLAIM_EVIDENCE_MATRIX.tsv": "authored claim-evidence matrix",
    "STAGE3C_DECISION_REPORT.md": "authored report",
    "README.md": "authored",
    "run.sh": "authored entry point",
    "PROVENANCE.md": "authored provenance record",
    "env.lock": "conda env export -p /home/borg/miniconda3/envs/retron_tradicional (verbatim; BS-8)",
}
UNIT = {
    "INPUT_PROVENANCE.tsv": ("input file", "244 declared Stage-3C inputs"),
    "STRUCTURE_STAGE3B_CROSSWALK.tsv": ("chain x partition arm", "62 chains x 2 arms; 19 in 3B Tier-A scope"),
    "STRUCTURE_STAGE2_CROSSWALK.tsv": ("chain x state block x arm", "62 chains x 8 blocks x 2 arms"),
    "LITERATURE_BOUNDARY_AUDIT.tsv": ("boundary source statement or verification check", "94 audit rows"),
    "XY_REGION_EVIDENCE.tsv": ("literature statement", "41 statements over 30 sources"),
    "XY_REGION_ANNOTATIONS.tsv": ("chain", "62 chains; 21 retron"),
    "TERMINI_FUSION_SUMMARY.tsv": ("chain", "62 chains; extensions interpretable in 20"),
    "CONTRADICTIONS_AND_UNCERTAINTY.tsv": ("recorded contradiction or uncertainty", "22 entries"),
    "CLAIM_EVIDENCE_MATRIX.tsv": ("statement", "22 statements"),
}
DEFAULT_UNIT = {
    "figures/": ("figure", "n/a - a figure is a view over its data TSV of the same basename"),
    "tables/mapper/": ("frozen-instrument output row", "60 sequences x 150 states; 2 INPUT_INVALID"),
    "tables/chains.faa": ("sequence", "62 modelled chain sequences"),
    "scripts/": ("script", "n/a - code, carries no rate"),
    "inputs/": ("frozen input copy", "n/a - vendored Stage-2 tables, hashed in INPUT_PROVENANCE.tsv"),
}


def walk():
    """Every file of the bundle except OUTPUTS.tsv itself (BS-11, exhaustively).

    Compiled artefacts and hidden harness files (.claude/, .mcp.json) are not results and are not
    sealed: sealing them makes a bundle fail its own hash check on the next run (BS-16).
    """
    for base, dirs, files in os.walk(L.S3C):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
        for f in sorted(files):
            if f.startswith("."):
                continue
            p = os.path.relpath(os.path.join(base, f), L.S3C)
            if p in ("OUTPUTS.tsv",):
                continue
            yield p


NOT_COMPUTED = "scripts/NOT_COMPUTED.md"  # the producer record for everything no script computes


def producer(p):
    if p in AUTHORED:
        return NOT_COMPUTED, "authored, not computed - " + AUTHORED[p]
    if p in RETRIEVED:
        return NOT_COMPUTED, "one-time audited retrieval, landed, never re-fetched by run.sh - " + RETRIEVED[p]
    if p == NOT_COMPUTED:
        return NOT_COMPUTED, "authored, not computed - producer record for non-computed artefacts"
    if p.startswith("scripts/"):
        return p, "bash run.sh"
    if p.startswith("inputs/"):
        return NOT_COMPUTED, "git show 94a1a78868d6039297c78b3fdcc047d633d6645e:<path>, hash-verified in INPUT_PROVENANCE.tsv"
    for prefix, script, cmd in SCRIPT_OF:
        if p == prefix or p.startswith(prefix):
            return script, cmd
    return "UNKNOWN", "UNKNOWN"


def unit_of(p):
    if p in UNIT:
        return UNIT[p]
    for prefix, v in DEFAULT_UNIT.items():
        if p.startswith(prefix):
            return v
    if p.endswith(".md"):
        return "prose", "n/a - prose carries no rate"
    if p.startswith("tables/"):
        return "table row", "stated in the table's own denominator column or in its README entry"
    return "file", "n/a - not a rate-bearing artefact"


man = []
for p in walk():
    script, cmd = producer(p)
    u, d = unit_of(p)
    man.append(dict(artifact=p, script=script, command=cmd, unit=u, denominator=d))

L.write_tsv(os.path.join(L.S3C, "MANIFEST.tsv"), man, ["artifact", "script", "command", "unit", "denominator"])

# INPUTS.tsv carries the inputs that were actually read and hashed. Four rows of
# INPUT_PROVENANCE.tsv have no sha256 and are deliberately NOT repeated here: the three
# __pycache__ paths the Stage-3B bundles seal but git never tracked (BS-16 defect of those
# bundles), and the mapper's instrument-identity row, whose "hash" is the version string
# rtmap-1.0.0/53a1e738a19b3896. INPUT_PROVENANCE.tsv remains the complete record of all 244.
inp = []
for r in L.read_tsv(os.path.join(L.S3C, "INPUT_PROVENANCE.tsv")):
    if len(r["sha256_observed"]) != 64:
        continue
    q = r["path"] if os.path.isabs(r["path"]) else os.path.join(L.ROOT, r["path"])
    inp.append(dict(path=r["path"], sha256=r["sha256_observed"], bytes=r["bytes"],
                    mtime=(f"{os.path.getmtime(q):.0f}" if os.path.exists(q) else "unknown"),
                    trust_grade=r["trust_grade"], verdict=r["verdict"]))
L.write_tsv(os.path.join(L.S3C, "INPUTS.tsv"), inp, ["path", "sha256", "bytes", "mtime", "trust_grade", "verdict"])

# OUTPUTS last, after MANIFEST.tsv and INPUTS.tsv are on disk, so it seals what actually landed
# (BS-11: every file in the bundle except OUTPUTS.tsv itself).
out = []
for p in walk():
    full = os.path.join(L.S3C, p)
    out.append(dict(path=p, sha256=L.sha256_file(full), bytes=os.path.getsize(full)))
L.write_tsv(os.path.join(L.S3C, "OUTPUTS.tsv"), out, ["path", "sha256", "bytes"])

unknown = [r["artifact"] for r in man if r["script"] == "UNKNOWN"]
print(f"MANIFEST {len(man)} artefacts, INPUTS {len(inp)} hashed (of 244 recorded), OUTPUTS {len(out)};"
      f" unknown producer: {unknown}")
if unknown:
    sys.exit("every artefact must name its producer (BS-13)")
