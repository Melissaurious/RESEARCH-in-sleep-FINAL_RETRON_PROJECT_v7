#!/usr/bin/env python3
"""Shared helpers for rt07_g7a_rt0_rt7_bridge.

No science lives here. Every scientific rule is either (a) frozen in the g4b instrument and
called through it, or (b) declared in `control/` and read from there. This module only reads
files, writes TSVs and hashes things.
"""
import hashlib
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BUNDLE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRATCH = os.path.join(ROOT, "ARIS_OUTPUT", "rt07_g7a")
WORK = os.path.join(SCRATCH, "work")
TABLES = os.path.join(BUNDLE, "tables")
CONTROL = os.path.join(BUNDLE, "control")
FIGURES = os.path.join(BUNDLE, "figures")

# The frozen instrument. Read and executed, never modified.
G4B = os.path.join(ROOT, "results", "rt07_g4b_production_mapper")
G4B_CODE = os.path.join(G4B, "code")

# Landed inputs.
G1T = os.path.join(ROOT, "results", "rt07_g1_history_and_definition", "tables")
G2T = os.path.join(ROOT, "results", "rt07_g2_reference_reconstruction", "tables")
G2REF = os.path.join(ROOT, "results", "rt07_g2_reference_reconstruction", "reference",
                     "g2_reference_set.faa")
G3T = os.path.join(ROOT, "results", "rt07_g3_prior_method_replication", "tables")
STRUCT = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures"

# LtrA is the bridge substrate: the one protein every held historical coordinate is
# denominated in. Its header in the landed g2 reference set.
LTRA_HEADER_KEY = "ltrb"

THREE_TO_ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
    "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
    "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_fasta(path):
    seqs, name = {}, None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith(">"):
            name = line[1:]
            seqs[name] = []
        elif name is not None:
            seqs[name].append(line.strip())
    return {k: "".join(v) for k, v in seqs.items()}


def write_fasta(seqs, path):
    with open(path, "w") as fh:
        for k, v in seqs.items():
            fh.write(f">{k}\n")
            for i in range(0, len(v), 60):
                fh.write(v[i:i + 60] + "\n")


def ltra_sequence():
    """The LtrA protein as landed in the g2 reference set. 599 aa, P0A3U0 numbering."""
    seqs = read_fasta(G2REF)
    hits = [(k, v) for k, v in seqs.items() if LTRA_HEADER_KEY in k.lower()]
    if len(hits) != 1:
        raise SystemExit(f"FAIL: expected exactly one LtrA record, found {len(hits)}")
    return hits[0]


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


def write_tsv(path, columns, rows):
    with open(path, "w") as fh:
        fh.write("\t".join(columns) + "\n")
        for r in rows:
            fh.write("\t".join(str(r.get(c, "")) for c in columns) + "\n")
    return path


def chain_residues(pdb_id, chain):
    """Author residue numbering -> one-letter code, for one protein chain of one structure.

    Returns author numbering exactly as deposited. No renumbering, no tag correction: any
    offset is a MEASUREMENT reported by s05, never a silent fix.
    """
    cif = os.path.join(STRUCT, f"{pdb_id}.cif")
    pdb = os.path.join(STRUCT, f"{pdb_id}.pdb")
    res = {}
    if os.path.exists(cif):
        hdr = []
        for line in open(cif):
            if line.startswith("_atom_site."):
                hdr.append(line.strip().split(".")[1])
            elif line.startswith("ATOM"):
                f = line.split()
                if len(f) != len(hdr):
                    continue
                rec = dict(zip(hdr, f))
                if rec.get("auth_asym_id") != chain:
                    continue
                comp = rec.get("auth_comp_id", rec.get("label_comp_id", ""))
                if comp in THREE_TO_ONE:
                    res[int(rec["auth_seq_id"])] = THREE_TO_ONE[comp]
    elif os.path.exists(pdb):
        for line in open(pdb):
            if line.startswith("ATOM") and line[21] == chain:
                comp = line[17:20].strip()
                if comp in THREE_TO_ONE:
                    res[int(line[22:26])] = THREE_TO_ONE[comp]
    else:
        raise SystemExit(f"FAIL: no structure file for {pdb_id}")
    return res
