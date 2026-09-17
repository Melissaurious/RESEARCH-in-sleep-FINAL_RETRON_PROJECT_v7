#!/usr/bin/env python3
"""Compact production instrument identifier.

Requirement (launcher §6): every g5 record must be traceable to the exact mapper version,
profile version, anchor/state definition, software versions, runtime parameters, input
sequence hash and output schema version - WITHOUT carrying the whole research-review bundle
on every row.

The resolution: one short string per record, plus one provenance sidecar per run that
expands it. The identifier is a hash over the *defining* components, so two runs that carry
the same identifier provably used the same instrument, and any change to any component
changes the identifier rather than being absorbed silently.

    rtmap-1.0.0/<16 hex>

Components hashed, in this fixed order:

    schema_version
    match_state_definition
    mapper.py sha256                (the frozen alignment-path mapper, byte-identical)
    profile HMM sha256              (GII.deriv.hmm)
    profile LENG
    anchor-set sha256               (the 150 frozen conserved states, in order)
    frozen parameter values         (PP_HI PP_LO S_MIN K_MIN T1 D_MAX D_RANDOM CAT_STATE)
    dyad pattern
    hmmalign sha256
    hmmsearch sha256
    instrument_tree_sha256          (every file in code/ and control/)
    eligibility_rule                (the inherited minimum length and alphabet)
    domain_scoring_protocol         (per-sequence, database size 1)

`instrument_tree_sha256`, `eligibility_rule` and `domain_scoring_protocol` close a gap the
independent packaging review found: without them, a wrapper that silently reverted to
batched `hmmsearch`, or changed the eligibility rule, or altered the runner's catalytic,
deduplication or inspectability logic, would keep the same identifier. The tree digest
covers `code/` and `control/` **only** — not `tables/` — so landing an output does not
change the instrument, but changing any code or control file does.

What is deliberately NOT hashed: the input sequences, the run timestamp, the partition, the
host, and the bundle's own manifest root. Those are per-run provenance, recorded in the run
sidecar; folding them in would give every shard a different instrument id and make the
identifier useless for grouping. (The bundle root additionally cannot be an input to the
identifier without circularity, since the manifest hashes the code that computes it. The
runner records it, verified against the external pinned root, in provenance instead.)
"""
import hashlib
import os
import subprocess

from . import params as P

SCHEMA_VERSION = "rtmap-schema-1.0"
PACKAGE_VERSION = "rtmap-1.0.0"

RTMAP_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(RTMAP_DIR)
BUNDLE_DIR = os.path.dirname(CODE_DIR)
MAPPER_PATH = os.path.join(RTMAP_DIR, "mapper.py")

# The eligibility rule the instrument has always been exercised under, inherited verbatim
# from the registered loader. Bound into the identifier so it cannot change silently.
ELIGIBILITY_RULE = "MIN_AA=250;ALPHABET=ACDEFGHIKLMNPQRSTVWY;CLEAN=strip[-.]upper,rstrip*"

# How `domain_scores` is invoked. Per-sequence (database size 1), so a bitscore and E-value
# are properties of the sequence alone. See PRODUCTION_SPEC.md section 3.
DOMAIN_SCORING_PROTOCOL = "PER_SEQUENCE_DB_SIZE_1"

# Directories whose contents define the instrument. `tables/` is excluded on purpose: landing
# an output must not change the instrument identifier.
INSTRUMENT_TREES = ("code", "control")
_TREE_SKIP_DIRS = {"__pycache__", ".claude", ".git"}


def instrument_tree_sha256():
    """Hash over every file in code/ and control/, as (relpath, sha256) pairs.

    Binds the production wrapper - the runner, the schema, the parameter loader, the
    crosswalk accessor, the freeze tool - and every frozen control table into the instrument
    identity, so a behavioural change anywhere in the package changes the identifier.
    """
    rows = []
    for tree in INSTRUMENT_TREES:
        base = os.path.join(BUNDLE_DIR, tree)
        for root, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in _TREE_SKIP_DIRS)
            for fn in sorted(files):
                p = os.path.join(root, fn)
                if os.path.islink(p):
                    raise SystemExit(f"FAIL CLOSED: symlink inside the instrument tree: {p}")
                rows.append((os.path.relpath(p, BUNDLE_DIR), P.sha256_file(p)))
    if not rows:
        raise SystemExit("FAIL CLOSED: the instrument tree is empty")
    body = "".join(f"{rel}  {h}\n" for rel, h in sorted(rows))
    return hashlib.sha256(body.encode()).hexdigest()

# The mapper frozen by the Stage-2 closure decision. Byte-identical to
# FINAL_PRE_UG25_VALIDATION_BUNDLE/code/mapper.py and to the copy the UG25 gate imported.
FROZEN_MAPPER_SHA256 = \
    "69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef"


def _binary_sha256(name):
    return P.sha256_file(os.path.join(P.BIN, name))


def check_instrument():
    """Verify every identity-bearing component. Returns the component dict, or fails closed.

    Called at the start of every production run. A production record is never emitted by an
    instrument whose components were not checked first.
    """
    got = P.sha256_file(MAPPER_PATH)
    if got != FROZEN_MAPPER_SHA256:
        raise SystemExit(
            f"FAIL CLOSED: mapper.py is NOT the frozen mapper.\n"
            f"  expected {FROZEN_MAPPER_SHA256}\n  observed {got}\n"
            f"  The Stage-2 closure decision freezes this file byte-for-byte.")

    if not os.path.isfile(P.PROFILE_HMM):
        raise SystemExit(f"FAIL CLOSED: frozen profile absent: {P.PROFILE_HMM}")
    prof = P.sha256_file(P.PROFILE_HMM)
    if prof != P.PROFILE_SHA256:
        raise SystemExit(f"FAIL CLOSED: profile HMM CHANGED\n  expected {P.PROFILE_SHA256}"
                         f"\n  observed {prof}")

    bins = {}
    for name, want in sorted(P.EXPECTED_BINARY_SHA256.items()):
        path = os.path.join(P.BIN, name)
        if not os.path.isfile(path):
            raise SystemExit(f"FAIL CLOSED: required binary absent: {path}")
        got_b = _binary_sha256(name)
        if got_b != want:
            raise SystemExit(
                f"FAIL CLOSED: {name} CHANGED\n  expected {want}\n  observed {got_b}\n"
                f"  The registered binary is part of the instrument identity. A different "
                f"HMMER build is a different instrument and requires an operator decision, "
                f"not a silent run.")
        bins[name] = got_b

    return {
        "schema_version": SCHEMA_VERSION,
        "match_state_definition": P.MATCH_STATE_DEFINITION,
        "mapper_sha256": got,
        "profile_sha256": prof,
        "profile_leng": str(P.PROFILE_LENG),
        "anchor_set_sha256": P.anchor_set_sha256(),
        "n_anchors": str(len(P.ANCHORS)),
        "PP_HI": P.PARAMS["PP_HI"],
        "PP_LO": P.PARAMS["PP_LO"],
        "S_MIN": P.PARAMS["S_MIN"],
        "K_MIN": P.PARAMS["K_MIN"],
        "T1": P.PARAMS["T1"],
        "D_MAX": P.PARAMS["D_MAX"],
        "D_RANDOM": P.PARAMS["D_RANDOM"],
        "CAT_STATE": P.PARAMS["CAT_STATE"],
        "dyad_pattern": P.DYAD_PATTERN,
        "hmmalign_sha256": bins["hmmalign"],
        "hmmsearch_sha256": bins["hmmsearch"],
        "instrument_tree_sha256": instrument_tree_sha256(),
        "eligibility_rule": ELIGIBILITY_RULE,
        "domain_scoring_protocol": DOMAIN_SCORING_PROTOCOL,
    }


# The order is fixed and load-bearing: it defines the identifier.
_ID_FIELDS = ("schema_version", "match_state_definition", "mapper_sha256", "profile_sha256",
              "profile_leng", "anchor_set_sha256", "PP_HI", "PP_LO", "S_MIN", "K_MIN",
              "T1", "D_MAX", "D_RANDOM", "CAT_STATE", "dyad_pattern",
              "hmmalign_sha256", "hmmsearch_sha256", "instrument_tree_sha256",
              "eligibility_rule", "domain_scoring_protocol")


def instrument_digest(components):
    body = "\n".join(f"{k}={components[k]}" for k in _ID_FIELDS)
    return hashlib.sha256(body.encode()).hexdigest()


def mapper_version(components=None):
    """The compact identifier carried on every production record."""
    c = components or check_instrument()
    return f"{PACKAGE_VERSION}/{instrument_digest(c)[:16]}"


def hmmer_version():
    out = subprocess.run([os.path.join(P.BIN, "hmmalign"), "-h"], capture_output=True,
                         text=True).stdout
    for ln in out.splitlines():
        if ln.startswith("# HMMER"):
            return ln.lstrip("# ").strip()
    return "UNKNOWN"


if __name__ == "__main__":
    c = check_instrument()
    print(f"mapper_version   {mapper_version(c)}")
    print(f"instrument_sha   {instrument_digest(c)}")
    print(f"hmmer            {hmmer_version()}")
    for k in _ID_FIELDS:
        print(f"  {k:<24} {c[k]}")
