#!/usr/bin/env python3
"""
T-R2a · BLOCKING ncRNA-object provenance gate.

⛔ NO R2a PRIMARY OUTPUT IS WRITTEN UNTIL EVERY CHECK HERE PASSES.

WHY IT EXISTS
    R2a reports RT-DNA extents as a FRACTION of, and a POSITION within, each
    element's ncRNA.  Every such number is meaningful only if the ncRNA object
    R2a divides by is the source dataset's own annotated ncRNA sequence, and not
    something this project reconstructed, re-bounded or re-derived after
    ingestion.  If our pipeline had rebuilt the ncRNA boundaries -- in particular
    from the observed RT-DNA extent -- the fraction would be definitional and
    would carry no architectural information.

    The scientific provenance question is settled upstream and is NOT re-opened
    here: the experimental census study annotated the cognate ncRNAs
    bioinformatically BEFORE the natural RT-DNA sequences were determined, and the
    RT-DNA was subsequently measured and aligned back onto those ncRNAs.  RT-DNA
    therefore did not define the ncRNA boundaries.  See R2a_PROVENANCE.md.

    THIS GATE ANSWERS ONLY THE NARROWER IMPLEMENTATION QUESTION:

        Is the ncRNA_sequence R2a consumes the SAME sequence object carried in the
        pinned experimental panel and already used by the accepted T-R1b, or has
        this project transformed or reconstructed it?

    Only explicitly documented normalisation is permitted, and the gate records
    whether even that normalisation changed any byte.

WHAT IT CHECKS, for all 81 Tier-A elements
    G1   pinned panel file is byte-identical to its registered sha256
    G2   the anchor set is exactly 81 (non-empty RTDNA_sequence)
    G3   every anchor carries a non-empty ncRNA_sequence
    G4   normalisation is strip()+upper() ONLY, and its no-op count is recorded
    G5   the ncRNA alphabet is ACGT only -- no reconstruction/ambiguity artefacts
    G6   the panel's own ncRNA_length column equals len(ncRNA_sequence)
    G7   accepted R1b ncrna_len equals len(panel ncRNA_sequence)  [same object]
    G8   revcomp(panel ncRNA[start:end]) == panel RTDNA           [same frame]
    G9   every anchor's R1b mapping_state is EXACT_UNIQUE
    G10  the ncRNA source is the pinned panel, not a derived Tier-D ncRNA asset

    G7 and G8 are the decisive identity checks: they bind the object R2a is about
    to divide by to the object the accepted upstream measurement was made against.

⛔ ANY FAILURE IS A STOP.  No row may be dropped, excluded or "ignored as a
    mismatch" -- a mismatching element ends the task under the normal new-ID rule.

Usage:  r2a_provenance_gate.py --out DIR
Exit:   0 = all checks PASS; 1 = at least one FAIL (STOP)
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import csv
import hashlib
import json
import os

SCRIPT_VERSION = "1.0.0"

PANEL = ("/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights"
         "/inputs/support.csv")
PANEL_SHA256 = "80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577"

R1B = ("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-R1b-rtdna-anchor-mapping"
       "/analysis/t_r1b_rtdna_anchor_mapping/tables/R1b_anchor_coordinates.tsv")
R1B_SHA256 = "713237accf27e7275880b51b4fec268d82a05d6f9d69515d23af8d81df958dca"

N_ANCHORS = 81

C_ID, C_RTDNA, C_NCRNA, C_NCLEN = (
    "terminal_id", "RTDNA_sequence", "ncRNA_sequence", "ncRNA_length")

# Derived ncRNA assets that must NEVER stand in for the panel object here.
FORBIDDEN_NCRNA_SOURCES = ("rt_ncrna_oriented_v1", "NCRNA-16458", "ncrna_16458")

COMP = str.maketrans("ACGT", "TGCA")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def revcomp(seq):
    return seq.translate(COMP)[::-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    checks = []

    def add(name, kind, expected, observed, ok, why):
        checks.append({
            "check": name, "kind": kind, "blocking": "YES",
            "expected": str(expected), "observed": str(observed),
            "result": "PASS" if ok else "FAIL", "rationale": why,
        })

    # ---- G1 -------------------------------------------------------------
    panel_sha = sha256_file(PANEL)
    add("R2a_GATE_panel_sha256", "identity", PANEL_SHA256, panel_sha,
        panel_sha == PANEL_SHA256,
        "the ncRNA objects must come from the registered, unmodified panel file")

    rows = list(csv.DictReader(open(PANEL, encoding="utf-8-sig")))
    anchors = [r for r in rows if (r.get(C_RTDNA) or "").strip()]

    # ---- G2 / G3 --------------------------------------------------------
    add("R2a_GATE_anchor_count", "population", N_ANCHORS, len(anchors),
        len(anchors) == N_ANCHORS,
        "the Tier-A population is exactly the 81 measured RT-DNA anchors")

    with_nc = [r for r in anchors if (r.get(C_NCRNA) or "").strip()]
    add("R2a_GATE_anchors_have_ncrna", "population", N_ANCHORS, len(with_nc),
        len(with_nc) == N_ANCHORS,
        "an anchor without its own ncRNA has no denominator and cannot be reported")

    # ---- G4 / G5 / G6 ---------------------------------------------------
    noop = alpha_ok = len_ok = 0
    alphabet = set()
    per_element = []
    for r in with_nc:
        raw = r[C_NCRNA]
        norm = raw.strip().upper()
        if raw == norm:
            noop += 1
        alphabet |= set(norm)
        if set(norm) <= set("ACGT"):
            alpha_ok += 1
        declared = str(r.get(C_NCLEN, "")).strip()
        if declared and declared == str(len(norm)):
            len_ok += 1
        per_element.append((r[C_ID].strip(), norm, r[C_RTDNA].strip().upper(),
                            hashlib.sha256(norm.encode()).hexdigest()))

    add("R2a_GATE_normalisation_is_documented_only", "transformation",
        f"strip()+upper() only; no-op on all {N_ANCHORS}", f"no-op on {noop}",
        noop == len(with_nc),
        "ONLY case/whitespace normalisation is permitted; a non-no-op must be "
        "declared in the report, and any other edit is a reconstruction")

    add("R2a_GATE_alphabet_ACGT", "transformation", f"ACGT only, {N_ANCHORS}",
        f"{alpha_ok}; observed {sorted(alphabet)}", alpha_ok == len(with_nc),
        "ambiguity codes or gaps would indicate a rebuilt, not ingested, sequence")

    add("R2a_GATE_panel_internal_length", "integrity", N_ANCHORS, len_ok,
        len_ok == len(with_nc),
        "the panel's own ncRNA_length column must match the sequence it ships, "
        "so the ingested object is not truncated or extended")

    # ---- G7 / G8 / G9 ---------------------------------------------------
    r1b_sha = sha256_file(R1B)
    add("R2a_GATE_r1b_table_sha256", "identity", R1B_SHA256, r1b_sha,
        r1b_sha == R1B_SHA256,
        "coordinates must come from the accepted R1b table, unchanged")

    panel_by_id = {tid: (nc, rt, h) for tid, nc, rt, h in per_element}
    r1b_rows = list(csv.DictReader(open(R1B), delimiter="\t"))

    same_obj = revcomp_ok = state_ok = 0
    mismatches = []
    for row in r1b_rows:
        tid = row[C_ID].strip()
        rec = panel_by_id.get(tid)
        if rec is None:
            mismatches.append({"terminal_id": tid, "defect": "NOT_IN_PANEL_ANCHORS"})
            continue
        nc, rt, _ = rec
        if int(row["ncrna_len"]) == len(nc):
            same_obj += 1
        else:
            mismatches.append({
                "terminal_id": tid, "defect": "NCRNA_LENGTH_DISAGREES",
                "r1b_ncrna_len": row["ncrna_len"], "panel_ncrna_len": len(nc)})
        if row["mapping_state"].strip() == "EXACT_UNIQUE":
            state_ok += 1
        else:
            mismatches.append({"terminal_id": tid, "defect": "NOT_EXACT_UNIQUE",
                               "mapping_state": row["mapping_state"]})
        start, end = int(row["ncrna_start"]), int(row["ncrna_end"])
        if revcomp(nc[start - 1:end]) == rt:
            revcomp_ok += 1
        else:
            mismatches.append({"terminal_id": tid, "defect": "REVCOMP_MISMATCH"})

    add("R2a_GATE_same_object_as_r1b", "identity", N_ANCHORS, same_obj,
        same_obj == N_ANCHORS,
        "DECISIVE: the ncRNA R2a divides by must be the one the accepted upstream "
        "measurement was made against, element by element")

    add("R2a_GATE_revcomp_roundtrip", "identity", N_ANCHORS, revcomp_ok,
        revcomp_ok == N_ANCHORS,
        "DECISIVE: the R1b coordinates must resolve on THIS panel object and "
        "regenerate the measured RT-DNA exactly")

    add("R2a_GATE_exact_unique", "integrity", N_ANCHORS, state_ok,
        state_ok == N_ANCHORS,
        "every Tier-A anchor is an unambiguous placement")

    # ---- G10 ------------------------------------------------------------
    forbidden = [s for s in FORBIDDEN_NCRNA_SOURCES if s in PANEL]
    add("R2a_GATE_no_derived_ncrna_substitution", "scope", "none", forbidden or "none",
        not forbidden,
        "the ncRNA denominator must be the panel object, never a Tier-D or "
        "project-derived ncRNA asset")

    # ---- emit -----------------------------------------------------------
    gate_path = os.path.join(args.out, "R2a_provenance_gate.tsv")
    with open(gate_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, delimiter="\t", fieldnames=[
            "check", "kind", "blocking", "expected", "observed", "result", "rationale"])
        w.writeheader()
        w.writerows(checks)

    failed = [c for c in checks if c["result"] == "FAIL"]

    summary = {
        "script_version": SCRIPT_VERSION,
        "panel": PANEL,
        "panel_sha256": panel_sha,
        "r1b_table": R1B,
        "r1b_table_sha256": r1b_sha,
        "n_anchors": len(anchors),
        "normalisation": "strip()+upper() only",
        "normalisation_noop_count": noop,
        "checks_total": len(checks),
        "checks_failed": len(failed),
        "mismatching_elements": mismatches,
        "verdict": "PASS" if not failed else "STOP",
        "ncrna_boundary_provenance": (
            "Inherited from the source study's pre-RT-DNA bioinformatic ncRNA "
            "annotation. RT-DNA did not define these boundaries."),
        "interpretation_ceiling": (
            "All RT-DNA/ncRNA fractions and normalised positions are FRACTION OF "
            "THE PUBLISHED ANNOTATED ncRNA SEQUENCE. They are NOT a fraction of an "
            "experimentally verified full-length transcript."),
        "recorded_limitation": (
            "The repository holds no separate direct source-study supplementary "
            "file from which support.csv was built; the panel is pinned by sha256 "
            "as an ingested object. The ncRNA boundaries are bioinformatic "
            "annotations, not measured transcript ends."),
    }
    with open(os.path.join(args.out, "R2a_provenance_gate.json"), "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")

    for c in checks:
        print(f"{c['result']}\t{c['check']}\texpected={c['expected']}\tobserved={c['observed']}")
    print(f"\nverdict\t{summary['verdict']}\t{len(checks) - len(failed)}/{len(checks)} PASS")
    if mismatches:
        print("mismatching elements (STOP, never dropped):")
        for m in mismatches:
            print("  " + json.dumps(m, sort_keys=True))

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
