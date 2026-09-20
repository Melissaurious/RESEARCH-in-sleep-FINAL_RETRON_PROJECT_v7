#!/usr/bin/env python3
"""
T-R1b · direct coordinate mapping of measured RT-DNA onto its own retron ncRNA.

THE QUESTION
    Where does each empirically determined RT-DNA sequence map onto its OWN
    retron ncRNA?

WHAT THIS IS
    A LOOKUP.  Exact substring search first, local alignment only where exact
    fails, both orientations always, every placement reported.

WHAT THIS IS NOT
    Not machine learning.  Not general msr/msd boundary inference.  Not a model.
    R1b produces the experimentally anchored coordinate table that a LATER
    ncRNA-architecture task (T-R2) may consume.  It infers no general boundary
    itself.

NEVER FORCE A RESULT
    A sequence that does not map is reported UNMAPPED.  A sequence that maps in
    several equally valid places reports ALL of them.  There is no tie-break that
    invents a single answer, because the number of placements is itself a result.

Usage:
    r1b_map.py --mode controls --out DIR
    r1b_map.py --mode primary  --out DIR
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import csv
import hashlib
import json
import os
import random
import time

SCRIPT_VERSION = "1.0.0"
SEED = 20260920

PANEL = ("/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights"
         "/inputs/support.csv")
PANEL_SHA256 = "80b2f565515c96bb1b9b0082c261dd6184c67672e29bb96c813cf6abdd9d9577"
PANEL_ROWS = 175
N_ANCHORS = 81

C_ID = "terminal_id"
C_RTDNA = "RTDNA_sequence"
C_NCRNA = "ncRNA_sequence"
C_NAME = "retron_name"
C_SUB = "retron_sub"

# ---- declared parameters, fixed in this commit ------------------------------
# Local alignment is used ONLY where exact substring search fails.  The scores are
# conventional nucleotide values and are not tuned to any observed result.
MATCH, MISMATCH, GAP_OPEN, GAP_EXT = 2, -3, -5, -2
# A near-exact call requires BOTH: the alignment covers >=90% of the RT-DNA, and
# >=90% of aligned positions are identities.  Anything below is UNMAPPED -- an
# honest state, never a forced low-quality coordinate.
NEAR_COV_MIN = 0.90
NEAR_ID_MIN = 0.90

COMP = str.maketrans("ACGTacgt", "TGCAtgca")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def revcomp(s: str) -> str:
    return s.translate(COMP)[::-1]


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def all_occurrences(hay: str, needle: str):
    """EVERY start index, not just the first. Overlaps included."""
    out, i = [], hay.find(needle)
    while i != -1:
        out.append(i)
        i = hay.find(needle, i + 1)
    return out


def local_align(query: str, subject: str):
    """Best local alignment. Returns (score, s_start, s_end, n_match, n_mismatch,
    n_gap, aligned_query_len) using 1-based inclusive subject coordinates."""
    from Bio import Align
    a = Align.PairwiseAligner()
    a.mode = "local"
    a.match_score, a.mismatch_score = MATCH, MISMATCH
    a.open_gap_score, a.extend_gap_score = GAP_OPEN, GAP_EXT
    try:
        aln = a.align(subject, query)[0]
    except Exception:
        return None
    sb, qb = aln.aligned
    if len(sb) == 0:
        return None
    s_start, s_end = int(sb[0][0]), int(sb[-1][1])
    n_match = n_mis = 0
    for (s0, s1), (q0, q1) in zip(sb, qb):
        for si, qi in zip(range(s0, s1), range(q0, q1)):
            if subject[si] == query[qi]:
                n_match += 1
            else:
                n_mis += 1
    q_aligned = sum(int(q1 - q0) for q0, q1 in qb)
    s_span = s_end - s_start
    n_gap = max(0, s_span - q_aligned) + max(0, q_aligned - s_span)
    return (float(aln.score), s_start + 1, s_end, n_match, n_mis, n_gap, q_aligned)


def map_one(rtdna: str, ncrna: str) -> dict:
    """Map one RT-DNA onto one ncRNA. Pure function; no I/O; no global state.

    INVARIANT: `starts` and `ends` are ALWAYS strings, possibly ';'-joined, on every
    path. A multi-placement result has no single integer coordinate, so a column that
    is sometimes int and sometimes str would be a type trap for every consumer.
    The control battery caught exactly that during drafting."""
    rtdna, ncrna = rtdna.strip().upper(), ncrna.strip().upper()
    if not rtdna or not ncrna:
        return {"state": "INPUT_MISSING", "orientation": "", "n_placements": 0,
                "starts": "", "ends": "", "n_mismatch": "", "n_gap": "",
                "pct_identity": "", "pct_coverage": "", "score": ""}

    fwd = all_occurrences(ncrna, rtdna)
    rev = all_occurrences(ncrna, revcomp(rtdna))
    n = len(fwd) + len(rev)
    if n:
        if fwd and rev:
            orient = "BOTH_AMBIGUOUS"
        else:
            orient = "FORWARD" if fwd else "REVCOMP"
        starts = [i + 1 for i in fwd] + [i + 1 for i in rev]
        ends = [i + len(rtdna) for i in fwd] + [i + len(rtdna) for i in rev]
        return {"state": "EXACT_UNIQUE" if n == 1 else "EXACT_MULTIPLE",
                "orientation": orient, "n_placements": n,
                "starts": ";".join(map(str, starts)), "ends": ";".join(map(str, ends)),
                "n_mismatch": 0, "n_gap": 0, "pct_identity": 1.0,
                "pct_coverage": 1.0, "score": ""}

    best, best_or = None, ""
    for lab, q in (("FORWARD", rtdna), ("REVCOMP", revcomp(rtdna))):
        r = local_align(q, ncrna)
        if r and (best is None or r[0] > best[0]):
            best, best_or = r, lab
    if best is None:
        return {"state": "UNMAPPED", "orientation": "", "n_placements": 0,
                "starts": "", "ends": "", "n_mismatch": "", "n_gap": "",
                "pct_identity": "", "pct_coverage": "", "score": ""}

    score, s0, s1, nm, nmis, ngap, qaln = best
    cov = qaln / len(rtdna)
    ident = nm / max(1, nm + nmis)
    near = cov >= NEAR_COV_MIN and ident >= NEAR_ID_MIN
    return {"state": "NEAR_EXACT" if near else "UNMAPPED",
            "orientation": best_or if near else "",
            "n_placements": 1 if near else 0,
            "starts": str(s0) if near else "", "ends": str(s1) if near else "",
            "n_mismatch": nmis, "n_gap": ngap,
            "pct_identity": round(ident, 4), "pct_coverage": round(cov, 4),
            "score": score}


# ------------------------------------------------------------------- controls
def run_controls(out: str) -> tuple[list, bool]:
    rows, ok = [], True

    def add(cid, typ, blk, exp, obs, st, det=""):
        nonlocal ok
        rows.append([cid, typ, blk, exp, obs, st, det])
        if blk == "YES" and st != "PASS":
            ok = False

    got = sha256_file(PANEL)
    add("R1b_GATE_panel_sha256", "positive", "YES", PANEL_SHA256, got,
        "PASS" if got == PANEL_SHA256 else "FAIL", "the panel is the one this task was frozen against")

    panel = list(csv.DictReader(open(PANEL)))
    anch = [r for r in panel if (r[C_RTDNA] or "").strip()]
    add("R1b_GATE_panel_rows", "positive", "YES", f"{PANEL_ROWS} rows / {N_ANCHORS} anchors",
        f"{len(panel)} / {len(anch)}",
        "PASS" if len(panel) == PANEL_ROWS and len(anch) == N_ANCHORS else "FAIL",
        "PANEL-RTDNA-81 is exactly the rows with a measured RTDNA_sequence")
    both = [r for r in anch if (r[C_NCRNA] or "").strip()]
    add("R1b_GATE_anchors_have_ncrna", "positive", "YES",
        f"all {N_ANCHORS} anchors carry an ncRNA_sequence to map onto", str(len(both)),
        "PASS" if len(both) == N_ANCHORS else "FAIL",
        "an anchor without its own ncRNA cannot be mapped and would be INPUT_MISSING")

    # ---- synthetic fixtures: none of the 81 is used here -------------------
    rng = random.Random(SEED)
    bg = "".join(rng.choice("ACGT") for _ in range(200))
    frag = bg[40:130]                      # a known 90 nt window, 1-based 41..130

    r = map_one(frag, bg)
    add("R1b_POS_planted_exact", "positive", "YES",
        "a fragment planted at 41..130 is found EXACT_UNIQUE, FORWARD, at 41..130",
        f"{r['state']} {r['orientation']} {r['starts']}..{r['ends']} n={r['n_placements']}",
        "PASS" if (r["state"] == "EXACT_UNIQUE" and r["orientation"] == "FORWARD"
                   and str(r["starts"]) == "41" and str(r["ends"]) == "130") else "FAIL",
        "coordinates are 1-based inclusive on the ncRNA")

    r = map_one(revcomp(frag), bg)
    add("R1b_POS_planted_revcomp", "positive", "YES",
        "its reverse complement is found REVCOMP at the same 41..130",
        f"{r['state']} {r['orientation']} {r['starts']}..{r['ends']}",
        "PASS" if (r["state"] == "EXACT_UNIQUE" and r["orientation"] == "REVCOMP"
                   and str(r["starts"]) == "41" and str(r["ends"]) == "130") else "FAIL",
        "both orientations are always tested and which one matched is landed")

    dup = bg[:40] + frag + bg[40:80] + frag + bg[80:]
    r = map_one(frag, dup)
    add("R1b_POS_multiple_placements_reported", "positive", "YES",
        "a fragment planted TWICE reports n_placements=2 and BOTH coordinate sets",
        f"{r['state']} n={r['n_placements']} starts={r['starts']}",
        "PASS" if (r["state"] == "EXACT_MULTIPLE" and r["n_placements"] == 2
                   and ";" in str(r["starts"])) else "FAIL",
        "⛔ there is NO tie-break; the number of equally valid placements IS a result")

    rand = "".join(rng.choice("ACGT") for _ in range(90))
    r = map_one(rand, bg)
    add("R1b_NEG_unrelated_unmapped", "negative", "YES",
        "an unrelated random sequence of the same length is UNMAPPED, not forced",
        f"{r['state']} cov={r['pct_coverage']} id={r['pct_identity']}",
        "PASS" if r["state"] == "UNMAPPED" else "FAIL",
        "the mapper does not invent a coordinate for something that is not there")

    mut = list(frag)
    for i in (10, 30, 50):
        mut[i] = {"A": "C", "C": "G", "G": "T", "T": "A"}[mut[i]]
    r = map_one("".join(mut), bg)
    add("R1b_POS_near_exact_detected", "positive", "YES",
        "a fragment with 3 planted substitutions is NEAR_EXACT with the mismatches counted",
        f"{r['state']} mism={r['n_mismatch']} id={r['pct_identity']} cov={r['pct_coverage']}",
        "PASS" if (r["state"] == "NEAR_EXACT" and r["n_mismatch"] == 3) else "FAIL",
        "exact and near-exact are reported SEPARATELY, never merged into 'mapped'")

    r = map_one(frag[:20] + rand, bg)
    add("R1b_NEG_partial_not_forced", "negative", "YES",
        "a chimera of 20 nt real + 90 nt random falls below the declared floor and is UNMAPPED",
        f"{r['state']} cov={r['pct_coverage']}",
        "PASS" if r["state"] == "UNMAPPED" else "FAIL",
        f"floor declared in advance: coverage>={NEAR_COV_MIN} AND identity>={NEAR_ID_MIN}")

    tsv(os.path.join(out, "tables", "R1b_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], rows)
    return rows, ok


# -------------------------------------------------------------------- primary
def run_primary(out: str) -> tuple[list, bool]:
    panel = list(csv.DictReader(open(PANEL)))
    anch = [r for r in panel if (r[C_RTDNA] or "").strip()]
    rows = []
    for r in anch:
        m = map_one(r[C_RTDNA], r[C_NCRNA])
        rows.append([r.get(C_ID, "").strip(), r.get(C_NAME, "").strip(),
                     r.get(C_SUB, "").strip(),
                     len(r[C_RTDNA].strip()), len((r[C_NCRNA] or "").strip()),
                     m["state"], m["orientation"], m["n_placements"],
                     m["starts"], m["ends"], m["n_mismatch"], m["n_gap"],
                     m["pct_identity"], m["pct_coverage"], m["score"]])
    tsv(os.path.join(out, "tables", "R1b_anchor_coordinates.tsv"),
        ["terminal_id", "retron_name", "retron_sub", "rtdna_len", "ncrna_len",
         "mapping_state", "orientation", "n_placements", "ncrna_start", "ncrna_end",
         "n_mismatch", "n_gap", "pct_identity", "pct_coverage", "align_score"], rows)

    cnt: dict = {}
    for r in rows:
        cnt[r[5]] = cnt.get(r[5], 0) + 1
    summ = [[k, v, "assayed elements", len(rows)] for k, v in sorted(cnt.items())]
    for lab, f in [("orientation_FORWARD", lambda r: r[6] == "FORWARD"),
                   ("orientation_REVCOMP", lambda r: r[6] == "REVCOMP"),
                   ("orientation_BOTH_AMBIGUOUS", lambda r: r[6] == "BOTH_AMBIGUOUS"),
                   ("multiple_placements", lambda r: isinstance(r[7], int) and r[7] > 1)]:
        summ.append([lab, sum(1 for r in rows if f(r)), "assayed elements", len(rows)])
    tsv(os.path.join(out, "tables", "R1b_summary.tsv"),
        ["quantity", "value", "unit", "denominator"], summ)

    amb = [r for r in rows if r[5] in ("EXACT_MULTIPLE", "UNMAPPED", "INPUT_MISSING")
           or r[6] == "BOTH_AMBIGUOUS"]
    tsv(os.path.join(out, "tables", "R1b_ambiguous_and_unmapped.tsv"),
        ["terminal_id", "retron_name", "retron_sub", "rtdna_len", "ncrna_len",
         "mapping_state", "orientation", "n_placements", "ncrna_start", "ncrna_end",
         "n_mismatch", "n_gap", "pct_identity", "pct_coverage", "align_score"], amb)

    ctrl = [["R1b_POS_every_anchor_reported", "positive", "YES",
             f"all {N_ANCHORS} anchors appear in the output with an explicit state",
             str(len(rows)), "PASS" if len(rows) == N_ANCHORS else "FAIL",
             "⛔ an anchor is never dropped; UNMAPPED and AMBIGUOUS are states, not omissions"]]
    return ctrl, all(c[5] == "PASS" for c in ctrl)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["controls", "primary"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(os.path.join(a.out, "tables"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)

    rows, ok = run_controls(a.out)
    if not ok:
        print("BLOCKING CONTROL FAILURE — no primary table written")
        for r in rows:
            if r[5] != "PASS":
                print(f"  {r[5]:<6} {r[0]:<36} {r[4]}")
        print("TASK_STATE: VOID")
        return 2
    if a.mode == "controls":
        print(f"all {len(rows)} blocking controls PASS")
        print("TASK_STATE: PASS (controls only)")
        return 0

    ctrl, ok2 = run_primary(a.out)
    rows += ctrl
    tsv(os.path.join(a.out, "tables", "R1b_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], rows)
    log = {"script_version": SCRIPT_VERSION, "mode": a.mode, "seed": SEED,
           "panel_sha256": PANEL_SHA256,
           "params": {"match": MATCH, "mismatch": MISMATCH, "gap_open": GAP_OPEN,
                      "gap_extend": GAP_EXT, "near_cov_min": NEAR_COV_MIN,
                      "near_id_min": NEAR_ID_MIN},
           "elapsed_s": round(time.time() - t0, 1),
           "blocking_failures": [r[0] for r in rows if r[2] == "YES" and r[5] != "PASS"]}
    with open(os.path.join(a.out, "logs", "run_log.json"), "w") as fh:
        json.dump(log, fh, indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    print("TASK_STATE: PASS" if ok2 else "TASK_STATE: VOID")
    return 0 if ok2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
