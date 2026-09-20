#!/usr/bin/env python3
"""
T-P1b fixture generator.

Builds the SEPARATE control inputs.  Nothing here ever touches, appends to, or
modifies the primary catalogue -- that is the defect that voided T-P1, whose
controls were appended to the primary FASTA and changed the clustering they were
meant to check (operator ruling 2026-09-20 section 3, WORKING_RULES 6b rule 3).

Fixtures are drawn FROM the catalogue by reading it, but are written to their own
files and clustered in their own MMseqs2 invocations.

Deterministic: one seed, fixed here, recorded in the launcher.  No RNG anywhere
else in this task.

Usage:  p1b_fixtures.py --out <dir>
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import os
import random

SCRIPT_VERSION = "1.0.0"
SEED = 20260920

V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
FAA = f"{V7}/data/derived/rt_exact_v1.faa"
FAA_SHA256 = "bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655"
FAA_RECORDS = 501561

N_DUP_PAIRS = 100      # -> 200 sequences in the duplicate fixture
N_SHUF = 100           # -> 200 sequences in the shuffled fixture (orig + shuffled)

# Fixture donors are drawn only from sequences long enough that a coverage-0.8
# clustering is well posed.  This is a SEQUENCE-LENGTH criterion, not a label:
# no family, tool, taxonomy or ncRNA annotation is read anywhere in this file.
DONOR_MIN_LEN = 300
DONOR_MAX_LEN = 600


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_fasta(path: str):
    """Yield (id, seq).  id is the token up to the first whitespace."""
    name, buf = None, []
    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(buf)
                name, buf = line[1:].strip().split(None, 1)[0], []
            else:
                buf.append(line.strip())
    if name is not None:
        yield name, "".join(buf)


def write_fasta(path: str, records) -> None:
    with open(path, "w") as fh:
        for name, seq in records:
            fh.write(f">{name}\n")
            for i in range(0, len(seq), 60):
                fh.write(seq[i:i + 60] + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # ---- GATE: the fixtures are drawn from the catalogue, so its identity is
    # ---- asserted here too.  A fixture built from the wrong catalogue is not a
    # ---- control.
    got = sha256_file(FAA)
    if got != FAA_SHA256:
        print(f"BLOCKING: rt_exact_v1.faa sha256 {got} != {FAA_SHA256}")
        return 2

    donors = []
    n_records = 0
    for name, seq in read_fasta(FAA):
        n_records += 1
        if DONOR_MIN_LEN <= len(seq) <= DONOR_MAX_LEN:
            donors.append((name, seq))
    if n_records != FAA_RECORDS:
        print(f"BLOCKING: rt_exact_v1.faa has {n_records} records, expected {FAA_RECORDS}")
        return 2

    rng = random.Random(SEED)
    # Sort before sampling so the sample does not depend on file order.
    donors.sort(key=lambda t: t[0])
    picked = rng.sample(donors, N_DUP_PAIRS + N_SHUF)

    # ---- FIXTURE 1 : exact duplicates -------------------------------------
    # Each donor appears twice under two different ids, in a file of its own.
    # 200 sequences, which is below the MMseqs2 prefilter --max-seqs ceiling, so
    # prefilter saturation -- the only mechanism by which identical sequences can
    # fail to co-cluster -- cannot occur at this size.  See the launcher.
    dup = []
    for i, (name, seq) in enumerate(picked[:N_DUP_PAIRS]):
        dup.append((f"DUPPAIR{i:03d}_A", seq))
        dup.append((f"DUPPAIR{i:03d}_B", seq))
    write_fasta(os.path.join(a.out, "fixture_duplicates.faa"), dup)

    # ---- FIXTURE 2 : composition-matched shuffles -------------------------
    # Each donor and a residue-shuffle of itself: identical length, identical
    # amino-acid composition, destroyed order.  Must NOT co-cluster at any level.
    shuf = []
    for i, (name, seq) in enumerate(picked[N_DUP_PAIRS:]):
        chars = list(seq)
        rng.shuffle(chars)
        shuf.append((f"SHUF{i:03d}_ORIG", seq))
        shuf.append((f"SHUF{i:03d}_SHUFFLED", "".join(chars)))
    write_fasta(os.path.join(a.out, "fixture_shuffled.faa"), shuf)

    # ---- FIXTURE 3 : sequence-content edge cases --------------------------
    # Synthetic, so the control does not depend on which catalogue sequences
    # happen to carry U or X.  Built from one donor.
    base = picked[0][1]
    edge = [
        ("EDGE_plain", base),
        ("EDGE_with_U", base[:-1] + "U"),
        ("EDGE_with_X", base[:-1] + "X"),
        ("EDGE_all_U", base.replace("C", "U")),
        ("EDGE_short20", base[:20]),
        ("EDGE_long", base * 12),
        ("EDGE_unrelated", "".join(rng.choice("ACDEFGHIKLMNPQRSTVWY") for _ in range(len(base)))),
    ]
    write_fasta(os.path.join(a.out, "fixture_edgecases.faa"), edge)

    manifest = os.path.join(a.out, "FIXTURE_MANIFEST.tsv")
    with open(manifest, "w") as fh:
        fh.write("fixture\tn_sequences\tsha256\tpurpose\n")
        for fn, purpose in [
            ("fixture_duplicates.faa",
             f"{N_DUP_PAIRS} exact-duplicate pairs; must co-cluster at every level"),
            ("fixture_shuffled.faa",
             f"{N_SHUF} orig/composition-matched-shuffle pairs; must NOT co-cluster"),
            ("fixture_edgecases.faa",
             "U, X, all-U, 20 aa, 12x-long and unrelated; must all be ASSIGNED, none dropped"),
        ]:
            p = os.path.join(a.out, fn)
            n = sum(1 for _ in read_fasta(p))
            fh.write(f"{fn}\t{n}\t{sha256_file(p)}\t{purpose}\n")

    print(f"fixtures written to {a.out}")
    print(f"  seed={SEED}  donors_eligible={len(donors)}  script_version={SCRIPT_VERSION}")
    with open(manifest) as fh:
        sys.stdout.write(fh.read())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
