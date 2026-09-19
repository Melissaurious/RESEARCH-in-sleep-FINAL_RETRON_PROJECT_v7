"""Shared helpers for Stage 3C (LAUNCHER_03C). Reads frozen inputs only; writes only under
analysis/stage3c_architecture_integration/.

Nothing here defines a threshold. Declared rules live in the gate scripts, marked DECLARED, and
mirror LAUNCHER_03C section 7a.
"""
import collections
import csv
import hashlib
import itertools
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
S3C = os.path.dirname(HERE)                                   # analysis/stage3c_architecture_integration
ROOT = os.path.dirname(os.path.dirname(S3C))                  # worktree root
TABLES = os.path.join(S3C, "tables")
FIGURES = os.path.join(S3C, "figures")
INPUTS = os.path.join(S3C, "inputs")

S3A = os.path.join(ROOT, "analysis", "stage3a_structural_core")
S3A_RES = os.path.join(S3A, "g2r", "results")
PDP_PRIMARY = os.path.join(S3A_RES, "rt_pdp_primary.residues.tsv")
PDP_P4 = os.path.join(S3A_RES, "rt_pdp_p4.residues.tsv")
UNITS = {"primary": os.path.join(S3A_RES, "rt_units.units.tsv"),
         "p4": os.path.join(S3A_RES, "rt_units_p4.units.tsv")}
CALLS = {"primary": os.path.join(S3A_RES, "rt_units.calls.tsv"),
         "p4": os.path.join(S3A_RES, "rt_units_p4.calls.tsv")}
PDP = {"primary": PDP_PRIMARY, "p4": PDP_P4}
SS_DIR = os.path.join(S3A_RES, "rt_ss")
REGISTER = os.path.join(S3A, "STRUCTURE_REGISTER.tsv")
T1 = os.path.join(S3A, "closure", "tables", "T1_structure_register.tsv")

CAT3B_G1 = os.path.join(ROOT, "results", "cat3b_g1_population_freeze")
CAT3B_G2 = os.path.join(ROOT, "results", "cat3b_g2_contract_and_thresholds")
MAPPER = os.path.join(ROOT, "results", "rt07_g4b_production_mapper")
STAGE2 = os.path.join(INPUTS, "stage2_94a1a788")
STAGE2_COMMIT = "94a1a78868d6039297c78b3fdcc047d633d6645e"
STAGE3A_CLOSURE_COMMIT = "67c137ba"

THREE2ONE = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
             "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
             "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}
# Modified residues present in the 62 chains (register column modified_polymer_residues; 3A
# report PDP_ABSENT list). Mapped to the parent amino acid; every use is recorded per chain.
MODIFIED_PARENT = {"MSE": "M", "PTR": "Y", "CSX": "C"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(commit, relpath):
    """Bytes of a file at a commit, or None if absent there."""
    try:
        return subprocess.run(["git", "-C", ROOT, "show", f"{commit}:{relpath}"],
                              check=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return None


def read_tsv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def write_tsv(path, rows, columns):
    """Deterministic TSV: fixed column order, '\\n' line ends, rows in the order given."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        f.write("\t".join(columns) + "\n")
        for r in rows:
            missing = [c for c in columns if c not in r]
            if missing:
                raise KeyError(f"{path}: row lacks {missing}")
            f.write("\t".join(fmt(r[c]).replace("\t", " ").replace("\n", " ") for c in columns) + "\n")


# ---------------------------------------------------------------- 3A frozen structure layer
def chains():
    return sorted(r["chain"] for r in read_tsv(T1))


def t1():
    return {r["chain"]: r for r in read_tsv(T1)}


def register():
    return {f"{r['pdb_id']}_{r['chain']}": r for r in read_tsv(REGISTER)}


def ss_residues(chain):
    """Canonical ordered residue list of a chain (residues carrying CA; 3A's index space)."""
    out = []
    for r in read_tsv(os.path.join(SS_DIR, f"{chain}.ss.tsv")):
        out.append(dict(idx=int(r["idx"]), key=(int(r["resnum"]), r["icode"]), resname=r["resname"],
                        brk=int(r["break_before"]), ss=r["A_ss3"], sheet=r["A_sheet"]))
    return out


def pdp_labels(arm="primary"):
    """{chain: {(resnum, icode): label}}; label 0 = PDP-unassigned. Keys absent = PDP_ABSENT."""
    lab = collections.defaultdict(dict)
    for r in read_tsv(PDP[arm]):
        lab[r["chain"]][(int(r["resnum"]), r["icode"])] = int(r["domain"])
    return lab


def residue_state(labels_chain, key, modelled_keys):
    if key not in modelled_keys:
        return "NOT_MODELLED", None
    if key not in labels_chain:
        return "PDP_ABSENT", None
    u = labels_chain[key]
    if u == 0:
        return "PDP_UNASSIGNED", None
    return "IN_UNIT", u


def unit_members(labels_chain):
    m = collections.defaultdict(set)
    for k, u in labels_chain.items():
        if u != 0:
            m[u].add(k)
    return dict(m)


def units_table(arm="primary"):
    """{(chain, unit): row} from the frozen units table."""
    return {(r["chain"], int(r["unit"])): r for r in read_tsv(UNITS[arm])}


def calls_table(arm="primary"):
    return {r["chain"]: r for r in read_tsv(CALLS[arm])}


def one_letter(resname):
    if resname in THREE2ONE:
        return THREE2ONE[resname], False
    if resname in MODIFIED_PARENT:
        return MODIFIED_PARENT[resname], True
    return "X", True


def numbering_consistent(a, b):
    """Stage-3A C7 rule, verbatim in effect (g2r_units.py c7): two chains are comparable on
    author residue keys only if they share keys and >= 0.95 of shared keys carry the same
    residue name. Returns (ok, shared_keys)."""
    ka = {x["key"]: x["resname"] for x in ss_residues(a)}
    kb = {x["key"]: x["resname"] for x in ss_residues(b)}
    common = set(ka) & set(kb)
    if not common:
        return False, common
    same = sum(ka[k] == kb[k] for k in common) / len(common)
    return same >= 0.95, common


def replicate_pairs(chain_list, group_of):
    byg = collections.defaultdict(list)
    for c in chain_list:
        byg[group_of[c]].append(c)
    for g in sorted(byg):
        for a, b in itertools.combinations(sorted(byg[g]), 2):
            yield g, a, b


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else float("nan")
