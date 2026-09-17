#!/usr/bin/env python3
"""seal - writes INPUTS.tsv, MANIFEST.tsv and (last) OUTPUTS.tsv.

  python3 seal.py inputs     hash everything the gate READ
  python3 seal.py manifest   artifact -> producing script
  python3 seal.py outputs    hash every file in the bundle except OUTPUTS.tsv itself (BS-11)

OUTPUTS is written LAST, after README.md carries its final STATUS: line.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import BUNDLE, G1T, G2REF, G2T, G3T, G4B, ROOT, sha256, write_tsv  # noqa: E402

LIT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/literature"
STRUCT = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures"

INPUT_FILES = [
    # landed project evidence
    os.path.join(G1T, "g1_region_verdicts.tsv"),
    os.path.join(G1T, "g1_evidence_quotes.tsv"),
    os.path.join(G1T, "g1_terminology_genealogy.tsv"),
    os.path.join(G1T, "g1_operational_evidence_matrix.tsv"),
    os.path.join(G1T, "g1_unresolved_definition_register.tsv"),
    os.path.join(G2T, "g2_ltra_mapping.tsv"),
    os.path.join(G2T, "g2_block_uncertainty.tsv"),
    os.path.join(G2T, "g2_frame_correspondence.tsv"),
    os.path.join(G2T, "g2_landmark_recovery.tsv"),
    G2REF,
    os.path.join(G3T, "g3_prior_region_correspondence.tsv"),
    os.path.join(G3T, "g3_rt0_object_audit.tsv"),
    os.path.join(G3T, "g3_handoff_to_g4.tsv"),
    # the frozen instrument
    os.path.join(G4B, "code", "rtmap", "mapper.py"),
    os.path.join(G4B, "code", "rtmap", "params.py"),
    os.path.join(G4B, "code", "rtmap", "run_mapper.py"),
    os.path.join(G4B, "control", "FROZEN_ANCHORS.tsv"),
    os.path.join(G4B, "control", "CATALYTIC_STATE_FROZEN.tsv"),
    os.path.join(G4B, "control", "CROSSWALK_RT0_RT7.tsv"),
    os.path.join(ROOT, "results", "rt07_g4a_repaired", "work", "GII.deriv.hmm"),
    # primary literature (read-only, gitignored, hashed here)
    os.path.join(LIT, "Blocker_et_al_2005_RNA_group_II_intron_RT_domain_structure_3D_model.pdf"),
    # structural comparators
    os.path.join(STRUCT, "5G2X.cif"),
    os.path.join(STRUCT, "6AR1.cif"),
    os.path.join(STRUCT, "7V9U.pdb"),
    os.path.join(STRUCT, "5VBS.pdb"),
    # the prior PROPOSAL, read only as a comparator
    os.path.join(ROOT, "results", "rt07_pre_g4_identifiability_redesign", "tables",
                 "historical_to_operational_mapping_proposed.tsv"),
    # this gate's own predeclaration
    os.path.join(BUNDLE, "control", "ASSIGNMENT_RULE.md"),
]

MANIFEST = [
    ("tables/g7a_historical_evidence_register.tsv", "scripts/s01_evidence_register.py",
     "python3 s01_evidence_register.py", "(historical label, primary source) pair",
     "labels x the primary sources that name them"),
    ("tables/g7a_ltra_numbering_control.tsv", "scripts/s01_evidence_register.py",
     "python3 s01_evidence_register.py", "stated residue identity",
     "12 Blocker-stated residues + 4 Edman sequences"),
    ("tables/g7a_acquisition_register.tsv", "scripts/s01_evidence_register.py",
     "python3 s01_evidence_register.py", "external asset", "assets this gate needed"),
    ("tables/g7a_coordinate_carriage.tsv", "scripts/s02_coordinates.py",
     "python3 s02_coordinates.py", "historical coordinate on LtrA",
     "coordinates carried by this gate"),
    ("tables/g7a_state_to_residue.tsv", "scripts/s03_bridge.py", "python3 s03_bridge.py",
     "frozen conserved state on LtrA", "150 frozen anchor states"),
    ("tables/g7a_controls.tsv", "scripts/s05_structural.py",
     "python3 s03_bridge.py; python3 s05_structural.py  (s03 writes it, s05 appends PC-3)",
     "control", "declared controls"),
    ("tables/g7a_panel.tsv", "scripts/s03_bridge.py", "python3 s03_bridge.py",
     "panel sequence", "6 declared panel members"),
    ("tables/g7a_panel_results.tsv", "scripts/s03_bridge.py", "python3 s03_bridge.py",
     "panel sequence", "panel members that produced a scientific row"),
    ("tables/g7a_crosswalk_resolved.tsv", "scripts/s04_crosswalk.py", "python3 s04_crosswalk.py",
     "historical label", "8 historical labels"),
    ("tables/g7a_prior_proposal_comparison.tsv", "scripts/s04_crosswalk.py",
     "python3 s04_crosswalk.py", "historical label", "8 historical labels"),
    ("tables/g7a_structural_comparators.tsv", "scripts/s05_structural.py",
     "python3 s05_structural.py", "structural comparator", "3 declared comparators"),
    ("tables/g7a_bridge.tsv", "scripts/s06_figure.py", "python3 s06_figure.py",
     "historical label", "8 historical labels"),
    ("figures/g7a_bridge.png", "scripts/s06_figure.py", "python3 s06_figure.py",
     "historical label", "8 historical labels"),
    ("figures/g7a_bridge.svg", "scripts/s06_figure.py", "python3 s06_figure.py",
     "historical label", "8 historical labels"),
    ("tables/g7a_closure_decision.tsv", "scripts/s07_closure.py", "python3 s07_closure.py",
     "historical label", "8 historical labels"),
    ("tables/g7a_unresolved_carried_forward.tsv", "scripts/s07_closure.py",
     "python3 s07_closure.py", "open question", "items carried into or out of this gate"),
    ("tables/g7a_summary.tsv", "scripts/s07_closure.py", "python3 s07_closure.py",
     "resolved value", "see each row"),
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
        assert "rt07_g5" not in r["path"] and "rt07_g6" not in r["path"], \
            f"anti-circularity: g5/g6 input {r['path']}"
    if bad:
        raise SystemExit("seal: an input is missing: " + ", ".join(r["path"] for r in bad))


def do_manifest():
    write_tsv(os.path.join(BUNDLE, "MANIFEST.tsv"),
              ["artifact", "script", "command", "unit", "denominator"],
              [dict(artifact=a, script=s, command=c, unit=u, denominator=d)
               for a, s, c, u, d in MANIFEST])
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
