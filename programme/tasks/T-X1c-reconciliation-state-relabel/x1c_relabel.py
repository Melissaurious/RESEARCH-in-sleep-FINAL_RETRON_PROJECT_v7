#!/usr/bin/env python3
"""
T-X1c · relabel the X1b reconciliation into four mutually exclusive states.

WHAT THIS IS
    A RELABEL.  It consumes the LANDED Boolean measurements of T-X1b and derives
    four mutually exclusive states from them.

⛔ WHAT THIS IS NOT
    It does NOT rerun sequence matching.  It opens no FASTA, no parquet, no
    catalogue and no panel.  Its ONLY input is X1b's landed table, pinned by hash.
    If it ever needed to hash a sequence, it would be the wrong task.

WHY IT EXISTS
    X1b's `overlap_class` used EXTERNAL_NEW for two different situations: "neither
    sequence present" (43) and "the ncRNA is present but the RT is absent" (6).
    The measurements were correct and landed; the class NAME was not.  T-X1b's
    `overlap_class` is RETRACTED as an authoritative state label and is superseded
    by the four states below.

THE AUTHORITATIVE RECONCILIATION IS A TWO-AXIS EXACT-PRESENCE MATRIX
    RT=1 ncRNA=1 -> PAIR_EXACT_PRESENT        predeclared  5
    RT=1 ncRNA=0 -> RT_ONLY_EXACT_PRESENT     predeclared 51
    RT=0 ncRNA=1 -> NCRNA_ONLY_EXACT_PRESENT  predeclared  6
    RT=0 ncRNA=0 -> NEITHER_EXACT_PRESENT     predeclared 43

⛔ ncRNA=0 MEANS "no exact native-msr-msd sequence match in the project ncRNA
   catalogue".  It does NOT mean biological incompatibility, and nothing here may
   be read that way.

Usage:  x1c_relabel.py --out DIR
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import csv
import hashlib
import json
import os
import time

SCRIPT_VERSION = "1.0.0"

X1B = ("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-X1b-buffington-reconciliation"
       "/analysis/t_x1b_buffington_reconciliation/tables/X1_row_classification.tsv")
X1B_SHA256 = "3a0b7fa73f789690b1bc383c1717c33c3354d82b5e8bb3715fc0ddd0977cc0ce"
N_ROWS = 105

# Predeclared from the exposed X1b measurements, fixed in this commit.
EXPECTED = {"PAIR_EXACT_PRESENT": 5, "RT_ONLY_EXACT_PRESENT": 51,
            "NCRNA_ONLY_EXACT_PRESENT": 6, "NEITHER_EXACT_PRESENT": 43}

C_ID = "buffington_id"
C_RT = "rt_stopstripped_hash_hit"     # the axis that actually matched; raw was 0/105
C_MSR_F = "msr_forward_hit"
C_MSR_R = "msr_revcomp_hit"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def tv(x) -> bool:
    return str(x).strip().lower() == "true"


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def state_of(rt: bool, nc: bool) -> str:
    if rt and nc:
        return "PAIR_EXACT_PRESENT"
    if rt:
        return "RT_ONLY_EXACT_PRESENT"
    if nc:
        return "NCRNA_ONLY_EXACT_PRESENT"
    return "NEITHER_EXACT_PRESENT"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    ctrl = []

    def add(cid, typ, exp, obs, ok, det=""):
        ctrl.append([cid, typ, "YES", exp, obs, "PASS" if ok else "FAIL", det])

    # --- GATE: the source is the exact landed X1b table -----------------------
    got = sha256_file(X1B)
    add("X1c_GATE_source_sha256", "positive",
        X1B_SHA256, got, got == X1B_SHA256,
        "⛔ ASSERTS the hash. An earlier draft of this gate passed unconditionally, which is "
        "the defect class this project keeps finding -- a gate that cannot fail is not a gate")
    if got != X1B_SHA256:
        tsv(os.path.join(a.out, "tables", "X1c_controls.tsv"),
            ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
        print("BLOCKING: X1b source table hash mismatch — no relabel written")
        print("TASK_STATE: VOID")
        return 2

    rows_in = list(csv.DictReader(open(X1B), delimiter="\t"))
    add("X1c_GATE_source_rows", "positive", f"{N_ROWS} rows", str(len(rows_in)),
        len(rows_in) == N_ROWS, "the relabel covers every published system")

    out, counts = [], {k: 0 for k in EXPECTED}
    for r in rows_in:
        rt = tv(r[C_RT])
        nc = tv(r[C_MSR_F]) or tv(r[C_MSR_R])
        st = state_of(rt, nc)
        counts[st] += 1
        out.append([r[C_ID], int(rt), int(nc), st, r.get("overlap_class", "")])

    # --- the four states are mutually exclusive and exhaustive by construction
    add("X1c_POS_states_exhaustive", "positive",
        f"the four states sum to {N_ROWS}", str(sum(counts.values())),
        sum(counts.values()) == N_ROWS,
        "every row gets exactly one state; state_of() is a total function on two Booleans")

    # --- each predeclared count must be reproduced exactly --------------------
    for k, v in EXPECTED.items():
        add(f"X1c_POS_count_{k}", "positive", f"{k} == {v}", str(counts[k]),
            counts[k] == v,
            "PREDECLARED from the exposed X1b measurements before this run")

    # --- the relabel must not have invented or lost any RT/ncRNA presence -----
    rt_tot = sum(r[1] for r in out)
    nc_tot = sum(r[2] for r in out)
    add("X1c_POS_axis_totals", "positive",
        "exact RT present 56/105 and exact native msr-msd present 11/105",
        f"RT={rt_tot} ncRNA={nc_tot}", rt_tot == 56 and nc_tot == 11,
        "the two axes are carried through unchanged from X1b")

    tsv(os.path.join(a.out, "tables", "X1c_reconciliation_states.tsv"),
        ["buffington_id", "rt_exact_present", "ncrna_exact_present",
         "reconciliation_state", "x1b_overlap_class_RETRACTED"], out)
    tsv(os.path.join(a.out, "tables", "X1c_state_counts.tsv"),
        ["reconciliation_state", "n", "unit", "denominator"],
        [[k, counts[k], "published systems", N_ROWS] for k in
         ("PAIR_EXACT_PRESENT", "RT_ONLY_EXACT_PRESENT",
          "NCRNA_ONLY_EXACT_PRESENT", "NEITHER_EXACT_PRESENT")]
        + [["exact_rt_present", rt_tot, "published systems", N_ROWS],
           ["exact_native_msrmsd_present", nc_tot, "published systems", N_ROWS]])
    tsv(os.path.join(a.out, "tables", "X1c_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)

    ok = all(c[5] == "PASS" for c in ctrl)
    log = {"script_version": SCRIPT_VERSION, "source": X1B, "source_sha256": got,
           "n_rows": len(rows_in), "counts": counts,
           "exact_rt_present": rt_tot, "exact_native_msrmsd_present": nc_tot,
           "reran_sequence_matching": False,
           "elapsed_s": round(time.time() - t0, 2),
           "blocking_failures": [c[0] for c in ctrl if c[5] != "PASS"]}
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    with open(os.path.join(a.out, "logs", "run_log.json"), "w") as fh:
        json.dump(log, fh, indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    print("TASK_STATE: PASS" if ok else "TASK_STATE: VOID")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
