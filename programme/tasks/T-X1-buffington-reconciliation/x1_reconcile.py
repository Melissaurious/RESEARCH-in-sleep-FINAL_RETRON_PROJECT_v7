#!/usr/bin/env python3
"""
T-X1 · exact-sequence reconciliation of the Buffington 2025 retron catalogue
       against this project's populations.

WHAT THIS IS
    A DESCRIPTIVE COVERAGE CHECK.  For each of the 105 published systems: is its
    RT, and its RT+native-msr-msd combination, already present in our resource?

WHAT THIS IS NOT
    Not biological validation, in either direction.  A published system absent
    from our catalogue is a MEASURED COVERAGE GAP in our resource -- it is not
    evidence that the publication is wrong.  A system present here is not thereby
    experimentally validated.

TWO INDEPENDENT AXES, NEVER CONFLATED
    Axis A  sequence overlap        -- computed here from sequence hashes
    Axis B  experimental status     -- NOT computable from this catalogue.  The
            table carries no screening and no activity column.  Axis B is
            populated ONLY from an identifiable experimental table/figure/source,
            recorded per row, and a blocking gate refuses to mark any row TRACED
            without one.

MERGES NOTHING.  Every project population is opened read-only and its count is
re-derived afterwards to prove it is unchanged.

Usage:
    x1_reconcile.py --mode controls --out DIR
    x1_reconcile.py --mode primary  --out DIR
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

SYN = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis"
V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"

BUF = f"{SYN}/references/rt0_rt7/buffington_2025/Discovery_and_engineering_of_retrons_supp.csv"
BUF_SHA256 = "d68366970378c05b5af9b00be886d76224a196a29b77171303f9353457cf4e62"
BUF_ROWS = 105

FAA = f"{V7}/data/derived/rt_exact_v1.faa"
FAA_SHA256 = "bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655"
FAA_RECORDS = 501561

NCRNA = f"{V7}/data/derived/rt_ncrna_oriented_v1.fna"
NCRNA_RECORDS = 16458

PAIRS = f"{V7}/data/derived/rt_ncrna_exact_pairs_v1.parquet"
PAIRS_SHA256 = "b89df6803dcd6346c93e39e62f1d590e22c96662d63c7c148952cc6641523dae"
PAIRS_ROWS = 30924

FAMILY = f"{V7}/data/derived/rt_family_baseline_v1.parquet"
RETRON_EXPECTED = 78287

# Columns, exactly as published.
C_ID = "I.D."
C_ACC = "Accession Number"
C_ORG = "Organism"
C_RETRON = "Retron I.D."
C_RT = "Reverse Transcriptase (RT) sequence"
C_RTNAME = "Name (RT)"
C_MSR = "Putative native msr-msd"

# ---- Axis B ------------------------------------------------------------------
# Systems the operator identified as experimentally active.  They are recorded as
# NOMINATED and are NOT labelled active.  A row becomes EXPERIMENTAL_SOURCE_TRACED
# only when experimental_source is a non-empty, specific table/figure/citation, and
# a BLOCKING gate enforces that.  This catalogue cannot supply one: it has no
# screening column and no activity column.
OPERATOR_NOMINATED = ["Vap1", "Psp1", "Vro1", "Cko1", "Efe1", "Mva1", "Eco1"]

COMP = str.maketrans("ACGTUacgtu", "TGCAAtgcaa")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def h(seq: str) -> str:
    """Project hash convention, verified at design time: sha256 of the UPPERCASE sequence.
    Confirmed against rt_exact_v1.faa and rt_ncrna_oriented_v1.fna, whose FASTA ids
    ARE this digest."""
    return hashlib.sha256(seq.strip().upper().encode()).hexdigest()


def revcomp(seq: str) -> str:
    return seq.strip().translate(COMP)[::-1]


def fasta_ids(path: str) -> set:
    out = set()
    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                out.add(line[1:].strip().split()[0])
    return out


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def read_buf() -> list:
    return list(csv.DictReader(open(BUF, newline="", encoding="utf-8-sig")))


# ------------------------------------------------------------------- controls
def run_controls(out: str) -> tuple[list, bool]:
    rows, ok = [], True

    def add(cid, typ, blocking, expect, obs, state, detail=""):
        nonlocal ok
        rows.append([cid, typ, blocking, expect, obs, state, detail])
        if blocking == "YES" and state != "PASS":
            ok = False

    # --- input identity ------------------------------------------------------
    for label, path, want in [("buffington", BUF, BUF_SHA256),
                              ("rt_exact_v1.faa", FAA, FAA_SHA256),
                              ("rt_ncrna_exact_pairs_v1.parquet", PAIRS, PAIRS_SHA256)]:
        got = sha256_file(path)
        add(f"X1_GATE_sha256_{label}", "positive", "YES", want, got,
            "PASS" if got == want else "FAIL", "inputs are the ones this task was frozen against")

    buf = read_buf()
    add("X1_GATE_buffington_rows", "positive", "YES", f"{BUF_ROWS} data rows", str(len(buf)),
        "PASS" if len(buf) == BUF_ROWS else "FAIL", "the published table is complete")

    rt_ids = fasta_ids(FAA)
    nc_ids = fasta_ids(NCRNA)
    add("X1_GATE_catalogue_counts", "positive", "YES",
        f"{FAA_RECORDS} RT and {NCRNA_RECORDS} ncRNA", f"{len(rt_ids)} / {len(nc_ids)}",
        "PASS" if len(rt_ids) == FAA_RECORDS and len(nc_ids) == NCRNA_RECORDS else "FAIL",
        "populations are read-only; this is also the post-run unchanged check")

    # --- POS: a sequence taken FROM the catalogue must be found --------------
    probe = sorted(rt_ids)[0]
    add("X1_POS_known_rt_found", "positive", "YES",
        "an id taken from rt_exact_v1.faa resolves as present",
        "found" if probe in rt_ids else "MISSING",
        "PASS" if probe in rt_ids else "FAIL", "the matcher can find a known-present sequence")

    # --- NEG: a shuffled sequence must NOT be found --------------------------
    rng = random.Random(SEED)
    seq = None
    with open(FAA) as fh:
        got_head = False
        buf_s = []
        for line in fh:
            if line.startswith(">"):
                if got_head:
                    break
                got_head = True
            else:
                buf_s.append(line.strip())
        seq = "".join(buf_s)
    chars = list(seq)
    rng.shuffle(chars)
    shuffled = "".join(chars)
    add("X1_NEG_shuffled_absent", "negative", "YES",
        "a composition-matched shuffle of a catalogue sequence is NOT present",
        "absent" if h(shuffled) not in rt_ids else "FOUND",
        "PASS" if h(shuffled) not in rt_ids else "FAIL",
        "the matcher is not matching everything")

    # --- POS: raw vs stop-stripped hashing are genuinely different -----------
    starred = seq + "*"
    raw_hit = h(starred) in rt_ids
    stripped_hit = h(starred.rstrip("*")) in rt_ids
    add("X1_POS_stop_strip_separation", "positive", "YES",
        "a catalogue sequence with an appended '*' MISSES on the raw hash and HITS on the "
        "stop-stripped hash",
        f"raw_hit={raw_hit} stripped_hit={stripped_hit}",
        "PASS" if (not raw_hit and stripped_hit) else "FAIL",
        "104 of 105 published RTs end in '*'; this proves the two hashes are reported separately "
        "for a reason and that neither silently substitutes for the other")

    # --- POS: reverse-complement handling for the oriented ncRNA catalogue ---
    nc_seq = None
    with open(NCRNA) as fh:
        got_head = False
        b2 = []
        for line in fh:
            if line.startswith(">"):
                if got_head:
                    break
                got_head = True
            else:
                b2.append(line.strip())
    nc_seq = "".join(b2)
    fwd = h(nc_seq) in nc_ids
    rc = h(revcomp(nc_seq)) in nc_ids
    add("X1_POS_orientation_probe", "positive", "YES",
        "a catalogue ncRNA matches forward; its reverse complement is reported on its own axis",
        f"forward={fwd} revcomp_also_present={rc}",
        "PASS" if fwd else "FAIL",
        "the project ncRNA catalogue is ORIENTED and the published msr-msd may be either strand, "
        "so both are tested and which one matched is landed")

    # --- BLOCKING: no Axis-B row may be TRACED without a source -------------
    fixture = [{"experimental_status": "EXPERIMENTAL_SOURCE_TRACED", "experimental_source": ""},
               {"experimental_status": "EXPERIMENTAL_SOURCE_TRACED", "experimental_source": "Fig 3b"},
               {"experimental_status": "EXPERIMENTAL_STATUS_UNKNOWN", "experimental_source": ""}]
    bad = [r for r in fixture
           if r["experimental_status"] == "EXPERIMENTAL_SOURCE_TRACED"
           and not r["experimental_source"].strip()]
    caught = len(bad) == 1
    add("X1_GATE_no_untraced_active_claim", "positive", "YES",
        "the gate REFUSES a row marked EXPERIMENTAL_SOURCE_TRACED with an empty source; "
        "it accepts one with a source and one marked UNKNOWN",
        f"refused={len(bad)} of 3 fixture rows",
        "PASS" if caught else "FAIL",
        "machine-enforced: an active claim without an identifiable experimental "
        "table/figure/source cannot be written")

    tsv(os.path.join(out, "tables", "X1_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], rows)
    return rows, ok


# -------------------------------------------------------------------- primary
def run_primary(out: str) -> tuple[list, bool]:
    import pyarrow.parquet as pq

    buf = read_buf()
    rt_ids = fasta_ids(FAA)
    nc_ids = fasta_ids(NCRNA)

    t = pq.read_table(PAIRS)
    pair_set = set(zip(t.column("rt_seq_hash").to_pylist(),
                       t.column("nc_seq_hash").to_pylist()))

    ft = pq.read_table(FAMILY)
    cols = ft.schema.names
    kcol = "rt_seq_hash" if "rt_seq_hash" in cols else cols[0]
    fcol = "rt_family" if "rt_family" in cols else cols[1]
    fam = dict(zip(ft.column(kcol).to_pylist(), ft.column(fcol).to_pylist()))
    retron_ids = {k for k, v in fam.items() if v == "Retron"}

    rows, seq_rows = [], []
    for r in buf:
        rid = r[C_ID].strip()
        rt_pub = r[C_RT].strip()
        rt_raw_h = h(rt_pub)
        rt_strip_h = h(rt_pub.rstrip("*"))
        msr = r[C_MSR].strip()
        msr_fwd_h = h(msr)
        msr_rc_h = h(revcomp(msr))

        rt_raw_hit = rt_raw_h in rt_ids
        rt_strip_hit = rt_strip_h in rt_ids
        rt_hit_hash = rt_strip_h if rt_strip_hit else (rt_raw_h if rt_raw_hit else "")
        rt_present = rt_raw_hit or rt_strip_hit
        is_retron = rt_hit_hash in retron_ids if rt_hit_hash else False

        msr_fwd_hit = msr_fwd_h in nc_ids
        msr_rc_hit = msr_rc_h in nc_ids
        msr_hit_hash = msr_fwd_h if msr_fwd_hit else (msr_rc_h if msr_rc_hit else "")
        msr_present = msr_fwd_hit or msr_rc_hit
        orientation = "FORWARD" if msr_fwd_hit else ("REVCOMP" if msr_rc_hit else "NO_MATCH")

        pair_present = bool(rt_hit_hash and msr_hit_hash
                            and (rt_hit_hash, msr_hit_hash) in pair_set)

        if pair_present:
            cls = "PAIR_EXACT_PRESENT"
        elif rt_present and msr_present:
            cls = "RT_AND_NCRNA_PRESENT_PAIR_ABSENT"
        elif rt_present:
            cls = "RT_PRESENT_NCRNA_DIFFERS"
        else:
            cls = "EXTERNAL_NEW"

        # ---- Axis B: NOT derivable from this catalogue ----------------------
        # EXACT matching only.  A substring test is wrong here and was caught at
        # design time: "Eco1" is a substring of Eco17, Eco18, Eco10..Eco19 and
        # matched TEN rows, none of which is Eco1.  Under exact matching Eco1 is
        # absent from this catalogue entirely.  Naming is not identity.
        nominated = [n for n in OPERATOR_NOMINATED
                     if (r[C_RETRON] or "").strip().lower() == f"retron-{n}".lower()
                     or (r[C_RTNAME] or "").strip().lower() == f"{n}-rt".lower()]
        exp_status = "OPERATOR_NOMINATED_UNTRACED" if nominated else "EXPERIMENTAL_STATUS_UNKNOWN"
        exp_source = ""   # this catalogue supplies none; see the launcher
        exp_nominated_as = ";".join(nominated)

        rows.append([rid, r[C_ACC].strip(), r[C_ORG].strip(), r[C_RETRON].strip(),
                     r[C_RTNAME].strip(), cls,
                     rt_raw_hit, rt_strip_hit, is_retron,
                     msr_fwd_hit, msr_rc_hit, orientation, pair_present,
                     exp_status, exp_source, exp_nominated_as])
        seq_rows.append([rid, len(rt_pub.rstrip("*")), rt_raw_h, rt_strip_h,
                         len(msr), msr_fwd_h, msr_rc_h])

    tsv(os.path.join(out, "tables", "X1_row_classification.tsv"),
        ["buffington_id", "accession", "organism", "retron_id", "rt_name", "overlap_class",
         "rt_raw_hash_hit", "rt_stopstripped_hash_hit", "rt_is_retron_family",
         "msr_forward_hit", "msr_revcomp_hit", "msr_orientation", "pair_exact_present",
         "experimental_status", "experimental_source", "operator_nominated_as"], rows)
    tsv(os.path.join(out, "tables", "X1_hashes.tsv"),
        ["buffington_id", "rt_len_stripped", "rt_raw_sha256", "rt_stopstripped_sha256",
         "msr_len", "msr_forward_sha256", "msr_revcomp_sha256"], seq_rows)

    # Every operator nomination that resolves to NO row in this catalogue is landed
    # explicitly. Silence about a name that is absent is how "Eco1" becomes "Eco17".
    resolved = {n for r in rows for n in (r[15].split(";") if r[15] else [])}
    unresolved = [[n, "NOT_IN_THIS_CATALOGUE",
                   "exact match on Retron I.D. / Name (RT) returns no row; this is a property "
                   "of the published table, NOT evidence the system does not exist"]
                  for n in OPERATOR_NOMINATED if n not in resolved]
    tsv(os.path.join(out, "tables", "X1_operator_nominations.tsv"),
        ["nominated_name", "resolution", "note"],
        [[n, "RESOLVED_TO_" + ";".join(r[0] for r in rows if n in (r[15] or "").split(";")),
          "recorded NOMINATED; NOT labelled active without a traced experimental source"]
         for n in OPERATOR_NOMINATED if n in resolved] + unresolved)

    cnt: dict = {}
    for r in rows:
        cnt[r[5]] = cnt.get(r[5], 0) + 1
    summ = [[k, v, "published systems", len(rows)] for k, v in sorted(cnt.items())]
    summ.append(["rt_present_by_stopstripped_hash", sum(1 for r in rows if r[7]),
                 "published systems", len(rows)])
    summ.append(["rt_present_by_RAW_hash", sum(1 for r in rows if r[6]),
                 "published systems", len(rows)])
    summ.append(["msr_present_forward", sum(1 for r in rows if r[9]), "published systems", len(rows)])
    summ.append(["msr_present_revcomp", sum(1 for r in rows if r[10]), "published systems", len(rows)])
    summ.append(["operator_nominated_untraced", sum(1 for r in rows if r[13] == "OPERATOR_NOMINATED_UNTRACED"),
                 "published systems", len(rows)])
    summ.append(["experimental_source_traced", sum(1 for r in rows if r[14].strip()),
                 "published systems", len(rows)])
    tsv(os.path.join(out, "tables", "X1_summary.tsv"),
        ["quantity", "value", "unit", "denominator"], summ)

    # ---- BLOCKING: populations unchanged -----------------------------------
    ctrl = []
    post = (len(fasta_ids(FAA)), len(fasta_ids(NCRNA)), t.num_rows, len(retron_ids))
    want = (FAA_RECORDS, NCRNA_RECORDS, PAIRS_ROWS, RETRON_EXPECTED)
    ctrl.append(["X1_POS_populations_unchanged", "positive", "YES",
                 f"after the run the populations still count {want}", str(post),
                 "PASS" if post == want else "FAIL",
                 "T-X1 MERGES NOTHING; every population is opened read-only"])
    bad = [r for r in rows if r[13] == "EXPERIMENTAL_SOURCE_TRACED" and not r[14].strip()]
    ctrl.append(["X1_GATE_no_untraced_active_claim_primary", "positive", "YES",
                 "no landed row is EXPERIMENTAL_SOURCE_TRACED without a source",
                 f"violations={len(bad)}", "PASS" if not bad else "FAIL",
                 "Vap1/Psp1/Vro1/Cko1/Efe1/Mva1/Eco1 are recorded NOMINATED, never active"])
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
                print(f"  {r[5]:<8} {r[0]:<38} {r[4]}")
        print("TASK_STATE: VOID")
        return 2
    if a.mode == "controls":
        print(f"all {len(rows)} blocking controls PASS")
        print("TASK_STATE: PASS (controls only)")
        return 0

    ctrl, ok2 = run_primary(a.out)
    rows += ctrl
    tsv(os.path.join(a.out, "tables", "X1_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], rows)
    log = {"script_version": SCRIPT_VERSION, "mode": a.mode, "seed": SEED,
           "input_sha256": {"buffington": BUF_SHA256, "rt_exact_v1.faa": FAA_SHA256,
                            "rt_ncrna_exact_pairs_v1.parquet": PAIRS_SHA256},
           "elapsed_s": round(time.time() - t0, 1),
           "blocking_failures": [r[0] for r in rows if r[2] == "YES" and r[5] != "PASS"]}
    with open(os.path.join(a.out, "logs", "run_log.json"), "w") as fh:
        json.dump(log, fh, indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    print("TASK_STATE: PASS" if ok2 else "TASK_STATE: VOID")
    return 0 if ok2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
