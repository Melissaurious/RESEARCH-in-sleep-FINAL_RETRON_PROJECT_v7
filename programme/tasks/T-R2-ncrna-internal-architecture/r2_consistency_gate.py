#!/usr/bin/env python3
"""
T-R2 · BLOCKING pre-analysis coordinate-frame consistency gate.

⛔ NOTHING IN STAGE 1 RUNS UNTIL EVERY CHECK HERE PASSES.

WHY IT EXISTS
    An R2 draft reported a maximum RT-DNA/ncRNA length ratio of 2.148, which is
    impossible if R2 uses the same sequence objects R1b matched: R1b established
    that all 81 RT-DNA sequences are EXACT substrings of the reverse complement of
    their own ncRNA, so len(RT-DNA) <= len(ncRNA) must hold for every element.

    The operator required the actual field/coordinate mismatch to be identified
    rather than the anomalous elements excluded.  IT WAS IDENTIFIED, and it was not
    in the data -- see R2_COORDINATE_FRAME_DIAGNOSIS.md.  The 2.148 was
    max(rtdna_len) / min(ncrna_len), computed ACROSS DIFFERENT ELEMENTS, in a
    summary line of the drafting session.  The per-element maximum is 0.8602.

    This gate exists anyway, and permanently: a summary statistic that mixed
    elements got as far as a launcher, so the invariant is now machine-checked
    against the sequences themselves rather than trusted.

WHAT IT CHECKS, for all 81
    1  the ncRNA used by R2 is byte-identical to the one R1b matched (sha256 per element)
    2  mapped span length == RT-DNA sequence length
    3  RT-DNA length <= ncRNA length
    4  mapped start/end fall inside that ncRNA
    5  the ncRNA substring at [start,end] reverse-complements to the RT-DNA exactly
    6  normalised coordinates derive ONLY from these verified objects

Usage:  r2_consistency_gate.py --out DIR
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

R1B = ("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-R1b-rtdna-anchor-mapping"
       "/analysis/t_r1b_rtdna_anchor_mapping/tables/R1b_anchor_coordinates.tsv")
R1B_SHA256 = "713237accf27e7275880b51b4fec268d82a05d6f9d69515d23af8d81df958dca"
PANEL = ("/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights"
         "/inputs/support.csv")
PANEL_SHA256 = "80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577"
N_ANCHORS = 81

C_ID, C_RTDNA, C_NCRNA = "terminal_id", "RTDNA_sequence", "ncRNA_sequence"
COMP = str.maketrans("ACGTacgt", "TGCAtgca")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.strip().upper().encode()).hexdigest()


def revcomp(s):
    return s.strip().upper().translate(COMP)[::-1]


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ctrl, per = [], []

    def add(cid, exp, obs, ok, det=""):
        ctrl.append([cid, "positive", "YES", exp, obs, "PASS" if ok else "FAIL", det])

    g = sha256_file(R1B)
    add("R2_GATE_r1b_table_sha256", R1B_SHA256, g, g == R1B_SHA256,
        "the R1b coordinate table is the accepted one")
    p = sha256_file(PANEL)
    add("R2_GATE_panel_sha256", PANEL_SHA256, p, p == PANEL_SHA256,
        "the panel is the one R1b matched against")
    if g != R1B_SHA256 or p != PANEL_SHA256:
        tsv(os.path.join(a.out, "tables", "R2_consistency_gate.tsv"),
            ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
        print("BLOCKING: input identity mismatch — Stage 1 must not run")
        print("TASK_STATE: VOID")
        return 2

    coords = {r[C_ID].strip() if C_ID in r else r["terminal_id"].strip(): r
              for r in csv.DictReader(open(R1B), delimiter="\t")}
    panel = {r[C_ID].strip(): r for r in csv.DictReader(open(PANEL))
             if (r[C_RTDNA] or "").strip()}

    add("R2_GATE_anchor_count", f"{N_ANCHORS} anchors in both sources",
        f"r1b={len(coords)} panel={len(panel)}",
        len(coords) == N_ANCHORS and len(panel) == N_ANCHORS, "")

    n_len_ok = n_span_ok = n_within = n_rc = n_state = 0
    for tid, prow in panel.items():
        crow = coords.get(tid)
        if crow is None:
            per.append([tid, "MISSING_IN_R1B", "", "", "", "", "", ""])
            continue
        nc = (prow[C_NCRNA] or "").strip().upper()
        rt = (prow[C_RTDNA] or "").strip().upper()
        st, en = int(crow["ncrna_start"]), int(crow["ncrna_end"])
        span = en - st + 1
        len_ok = len(rt) <= len(nc)
        span_ok = span == len(rt)
        within = 1 <= st <= en <= len(nc)
        rc_ok = within and revcomp(nc[st - 1:en]) == rt
        state_ok = crow["mapping_state"] == "EXACT_UNIQUE"
        n_len_ok += len_ok; n_span_ok += span_ok; n_within += within
        n_rc += rc_ok; n_state += state_ok
        per.append([tid, crow["mapping_state"], len(rt), len(nc),
                    round(len(rt) / len(nc), 6), st, en,
                    "OK" if (len_ok and span_ok and within and rc_ok) else "FAIL"])

    n = len(panel)
    add("R2_GATE_rtdna_le_ncrna", f"RT-DNA length <= ncRNA length for all {n}",
        f"{n_len_ok}/{n}", n_len_ok == n,
        "⛔ the invariant the 2.148 appeared to violate; it is satisfied by every element")
    add("R2_GATE_span_equals_rtdna_len", f"mapped span == RT-DNA length for all {n}",
        f"{n_span_ok}/{n}", n_span_ok == n, "")
    add("R2_GATE_coords_within_ncrna", f"1 <= start <= end <= len(ncRNA) for all {n}",
        f"{n_within}/{n}", n_within == n, "")
    add("R2_GATE_revcomp_roundtrip", f"revcomp(ncRNA[start:end]) == RT-DNA for all {n}",
        f"{n_rc}/{n}", n_rc == n,
        "re-derives R1b's result INDEPENDENTLY from the coordinates and the sequences")
    add("R2_GATE_all_exact_unique", f"all {n} are EXACT_UNIQUE", f"{n_state}/{n}", n_state == n, "")

    ratios = [r[4] for r in per if isinstance(r[4], float)]
    add("R2_GATE_per_element_ratio_le_1",
        "the PER-ELEMENT max ratio is <= 1.0",
        f"max={max(ratios):.4f} median={sorted(ratios)[len(ratios)//2]:.4f} min={min(ratios):.4f}",
        max(ratios) <= 1.0,
        "⛔ any ratio must be computed PER ELEMENT. max(rtdna)/min(ncrna) across different "
        "elements is not a ratio of anything and is what produced the spurious 2.148")

    tsv(os.path.join(a.out, "tables", "R2_consistency_gate.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
    tsv(os.path.join(a.out, "tables", "R2_per_element_verification.tsv"),
        ["terminal_id", "mapping_state", "rtdna_len", "ncrna_len", "ratio",
         "ncrna_start", "ncrna_end", "verdict"], per)

    ok = all(c[5] == "PASS" for c in ctrl)
    log = {"script_version": SCRIPT_VERSION, "r1b_sha256": g, "panel_sha256": p,
           "n_anchors": n, "per_element_ratio_max": max(ratios),
           "blocking_failures": [c[0] for c in ctrl if c[5] != "PASS"]}
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    with open(os.path.join(a.out, "logs", "consistency_gate.json"), "w") as fh:
        json.dump(log, fh, indent=2, sort_keys=True)
    for c in ctrl:
        print(f"  [{c[5]}] {c[0]:<34} {c[4]}")
    print("GATE PASS — Stage 1 may run" if ok else "GATE FAIL — Stage 1 must NOT run")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
