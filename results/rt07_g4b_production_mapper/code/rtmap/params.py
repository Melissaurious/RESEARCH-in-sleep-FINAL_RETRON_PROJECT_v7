#!/usr/bin/env python3
"""Frozen scientific parameters, read from the frozen control tables. Never restated.

g4b is PACKAGING ONLY. No constant in this file is chosen here: every value is read from
`control/SUPPORT_RULE_FROZEN.tsv`, `control/CATALYTIC_STATE_FROZEN.tsv` and
`control/FROZEN_ANCHORS.tsv`, which are byte-identical copies of the tables that the
pre-UG25 validation bundle froze and the UG25 confirmatory gate read.

Two independent guards run at import:

  1. every control file's sha256 must equal the value recorded in EXPECTED_CONTROL_SHA256,
     which is the value the validation bundle carried;
  2. every parameter that the UG25 confirmatory gate read must be present, and must equal
     the value recorded in the closure decision
     `docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md`.

Guard 2 is deliberately redundant with guard 1. A file-hash check alone would pass if the
frozen tables were replaced wholesale together with this module's expectations; pinning the
eight calibrated values plus CAT_STATE as literals here means a drift has to be committed in
two places that a reviewer reads separately.

The literals below are ASSERTIONS ABOUT frozen values. They are not the source of the values
and are never used in a computation - `PARAMS` always comes from the tables.
"""
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CONTROL = os.path.normpath(os.path.join(HERE, "..", "..", "control"))

SUPPORT_RULE = os.path.join(CONTROL, "SUPPORT_RULE_FROZEN.tsv")
CATALYTIC_STATE = os.path.join(CONTROL, "CATALYTIC_STATE_FROZEN.tsv")
ANCHOR_TABLE = os.path.join(CONTROL, "FROZEN_ANCHORS.tsv")

# sha256 of each frozen control file as carried by the validation bundle. The anchor table
# value is the one registered in FINAL_PRE_UG25_VALIDATION_BUNDLE/tables/external_inputs.tsv
# as `frozen_anchor_coordinates`.
EXPECTED_CONTROL_SHA256 = {
    "SUPPORT_RULE_FROZEN.tsv":
        "ecb0451e9680de2edec76836ab630cee9c6526d2c429fbaf045b4f6e6acd7057",
    "CATALYTIC_STATE_FROZEN.tsv":
        "d6fc130148995e2320b7cec8047e920c0f26369b75a4f6e7922aefb2cff8ca78",
    "FROZEN_ANCHORS.tsv":
        "c48315aef8dccdcee1f41ebef512cc69a63e51cfad22df28c73a84c564a30e49",
}

# The values recorded in the Stage-2 closure decision. Redundant guard - see the docstring.
EXPECTED_VALUES = {
    "PP_HI": "0.75",
    "PP_LO": "0.5",
    "S_MIN": "10",
    "K_MIN": "30",
    "T1": "0.32",
    "D_MAX": "0.48",
    "D_RANDOM": "0.067",
    "N_ANCHORS": "150",
    "CAT_STATE": "262",
}

# The instrument is defined under this match-state convention and no other. `-M a2m` and
# `-M 60` are NOT equivalent instruments; see PRODUCTION_SPEC.md §"Match-state sensitivity".
MATCH_STATE_DEFINITION = "hhmake -M 50"

# The frozen profile. Production reads it read-only from its landed location; it is not
# copied into the bundle (220 KB of derived model belonging to the g4a bundle that produced
# it), and its identity is enforced by hash at every run.
PROFILE_HMM = ("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
               "rt07_g4a_repaired/work/GII.deriv.hmm")
PROFILE_SHA256 = "292495a4f4ec2d04c47cf73c658b0f5cbaec7b202de70d97e6fc2496dd82e97b"
PROFILE_LENG = 471

# Catalytic motif class. Frozen rule: the dyad regex applied at CAT_STATE only.
DYAD_PATTERN = r"[YF].DD"

# Binaries whose identity is part of the instrument.
BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"
EXPECTED_BINARY_SHA256 = {
    "hmmalign": "532f1ed4c21dc03a12007b31c2dc0568e82cab659b0d75c20efd20e6374f53e2",
    "hmmsearch": "e73bad9d701f129795dd3ffb108ee2d4724ab4c8b1a46269bd5671bdcfcdc8f2",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_param_table(path):
    d = {}
    for ln in open(path):
        if ln.startswith("parameter") or ln.startswith("#") or not ln.strip():
            continue
        k, v = ln.split("\t", 2)[:2]
        d[k] = v
    return d


def _load():
    for name, want in sorted(EXPECTED_CONTROL_SHA256.items()):
        p = os.path.join(CONTROL, name)
        if not os.path.isfile(p):
            raise SystemExit(f"FAIL CLOSED: frozen control file absent: {p}")
        got = sha256_file(p)
        if got != want:
            raise SystemExit(
                f"FAIL CLOSED: frozen control file CHANGED: {name}\n"
                f"  expected {want}\n  observed {got}\n"
                f"  The scientific parameters are frozen by the Stage-2 closure decision "
                f"and may not be edited in g4b.")

    p = _read_param_table(SUPPORT_RULE)
    p.update(_read_param_table(CATALYTIC_STATE))
    for k, want in sorted(EXPECTED_VALUES.items()):
        if k not in p:
            raise SystemExit(f"FAIL CLOSED: frozen parameter {k} absent from the control "
                             f"tables")
        if p[k] != want:
            raise SystemExit(
                f"FAIL CLOSED: frozen parameter DRIFTED: {k} = {p[k]!r}, closure decision "
                f"records {want!r}")
    return p


PARAMS = _load()

PP_HI = float(PARAMS["PP_HI"])
PP_LO = float(PARAMS["PP_LO"])
S_MIN = float(PARAMS["S_MIN"])
K_MIN = int(PARAMS["K_MIN"])
T1 = float(PARAMS["T1"])
D_MAX = float(PARAMS["D_MAX"])
D_RANDOM = float(PARAMS["D_RANDOM"])
CAT_STATE = int(PARAMS["CAT_STATE"])
N_ANCHORS = int(PARAMS["N_ANCHORS"])

# The frozen conserved-state (anchor) set. Sorted ascending, exactly as every prior bundle
# read it. `sorted()` here is the same call the validation pipeline and the UG25 gate made,
# so the anchor sequence is identical, not merely equivalent.
ANCHORS = sorted(int(l.split("\t")[2]) for l in open(ANCHOR_TABLE)
                 if not l.startswith("anchor_index"))

if len(ANCHORS) != N_ANCHORS:
    raise SystemExit(f"FAIL CLOSED: {len(ANCHORS)} anchors read, frozen N_ANCHORS is "
                     f"{N_ANCHORS}")
if max(ANCHORS) > PROFILE_LENG:
    raise SystemExit(f"FAIL CLOSED: anchor {max(ANCHORS)} exceeds profile LENG "
                     f"{PROFILE_LENG}")
if CAT_STATE > PROFILE_LENG:
    raise SystemExit(f"FAIL CLOSED: CAT_STATE {CAT_STATE} exceeds profile LENG "
                     f"{PROFILE_LENG}")


def anchor_set_sha256():
    """Stable hash over the frozen anchor sequence, for the instrument identifier."""
    return hashlib.sha256(",".join(str(a) for a in ANCHORS).encode()).hexdigest()


if __name__ == "__main__":
    print(f"match_state_definition {MATCH_STATE_DEFINITION}")
    for k in ("PP_HI", "PP_LO", "S_MIN", "K_MIN", "T1", "D_MAX", "D_RANDOM", "CAT_STATE"):
        print(f"{k:>10} {PARAMS[k]}")
    print(f"{'N_ANCHORS':>10} {len(ANCHORS)}  sha256 {anchor_set_sha256()[:16]}")
    print(f"{'CAT_STATE':>10} in anchors: {CAT_STATE in ANCHORS}")
