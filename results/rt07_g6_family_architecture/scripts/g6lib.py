#!/usr/bin/env python3
"""Shared helpers for rt07_g6_family_architecture.

No science lives here. Every scientific rule is declared in control/PREDECLARATION.md.
This module reads landed g5 products, writes TSVs and hashes files.

ANTI-CIRCULARITY: nothing in this gate reads results/rt07_g7a_rt0_rt7_bridge/. See
control/PREDECLARATION.md section 0 and verify.sh.
"""
import hashlib
import os

BUNDLE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT = os.path.normpath(os.path.join(BUNDLE, "..", ".."))
PROJ = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
DERIVED = os.path.join(PROJ, "data", "derived")
G5 = os.path.join(DERIVED, "rt07_g5")
SCRATCH = os.path.join(ROOT, "ARIS_OUTPUT", "rt07_g6")
WORK = os.path.join(SCRATCH, "work")
TABLES = os.path.join(BUNDLE, "tables")
CONTROL = os.path.join(BUNDLE, "control")
FIGURES = os.path.join(BUNDLE, "figures")

ENVBIN = "/home/borg/miniconda3/envs/retron_tradicional/bin"
MMSEQS = os.path.join(ENVBIN, "mmseqs")

# Declared in control/PREDECLARATION.md section 5, before anything was computed.
CLUSTER_PRIMARY = "0.90"
CLUSTER_SENSITIVITY = ["0.50", "0.30"]
CLUSTER_COV = "0.8"
CLUSTER_COV_MODE = "0"

MIN_STRATUM = 100          # section 4/6: a stratum below this is UNDERPOWERED
RHO_FLOOR = 0.50           # section 8: effect floor
NULL_REPLICATES = 200      # section 7 NULL-1
NULL_PERCENTILE = 99       # section 8 significance criterion
N_STATES = 150


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tsv(path, columns, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\t".join(columns) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in columns) + "\n")
    return path


def read_tsv(path, comment="#"):
    rows, header = [], None
    for line in open(path):
        if line.startswith(comment) or not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if header is None:
            header = parts
            continue
        rows.append(dict(zip(header, parts)))
    return rows


def half_of(cluster_rep):
    """Deterministic, LABEL-BLIND split of clusters into halves A and B.

    Keyed on the cluster representative's hash only: no family label, tool label, taxonomy or
    state call participates. Splitting by CLUSTER (not by sequence) is what keeps
    near-duplicates out of both halves; the residual leakage is MEASURED in PC-SPLIT rather
    than assumed to be zero (Principle 7).
    """
    return "A" if int(hashlib.sha256(cluster_rep.encode()).hexdigest()[:8], 16) % 2 == 0 else "B"
