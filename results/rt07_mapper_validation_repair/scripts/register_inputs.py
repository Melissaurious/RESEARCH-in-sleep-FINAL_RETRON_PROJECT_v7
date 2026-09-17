#!/usr/bin/env python3
"""REPAIR 1 - hash every EXTERNAL input this bundle depends on.

The manifest covers files inside the bundle. These live outside it, and a silent change to any
one of them would change every result while the bundle manifest still verified clean.
"""
import hashlib, os, sys

TABLES = sys.argv[1]
ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
INPUTS = [
    ("profile_hmm", f"{ROOT}/results/rt07_g4a_repaired/work/GII.deriv.hmm"),
    ("frozen_anchor_coordinates",
     f"{ROOT}/results/rt07_ug5_holdout_gate/tables/ug5_frozen_anchor_coordinates.tsv"),
    ("sequence_collection",
     "/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/RTs-collection.faa"),
    ("eligibility_library", f"{ROOT}/results/rt07_g4a_repaired/scripts/repaired_lib.py"),
]
BINS = ["hmmalign", "hmmsearch", "hmmemit"]
BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


rows = []
for name, p in INPUTS:
    if not os.path.exists(p):
        raise SystemExit(f"FAIL CLOSED: declared input missing: {p}")
    rows.append([name, p, sha256(p), str(os.path.getsize(p))])
for b in BINS:
    p = BIN + b
    rows.append([f"binary_{b}", p, sha256(p), str(os.path.getsize(p))])

with open(f"{TABLES}/external_inputs.tsv", "w") as f:
    f.write("input\tpath\tsha256\tbytes\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[0]:28s} {r[2][:16]}  {r[1]}")
