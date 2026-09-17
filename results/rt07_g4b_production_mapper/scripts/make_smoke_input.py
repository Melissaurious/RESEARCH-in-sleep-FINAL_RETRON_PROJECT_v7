#!/usr/bin/env python3
"""Build the production smoke-test input. ENGINEERING ONLY - not a scientific evaluation.

Population: sequences the instrument has ALREADY SEEN, drawn from the construction families
that calibrated it and whose per-sequence results are landed in
`FINAL_PRE_UG25_VALIDATION_BUNDLE/tables/construction_validation_sequence.tsv`. Nothing here
is held out, nothing here is fresh, and no number produced from it is evidence about
generalisation. The point is solely that the production packaging reproduces the frozen
mapper's own landed values on inputs whose answers are already on record.

UG25 is NOT used. It was consumed as the terminal confirmatory family; re-running it would
be tuning against a spent holdout.

Deliberately included alongside the real sequences, to exercise the production failure
states end to end:

    SMOKE_INVALID_SHORT        180 aa            -> BELOW_MIN_LENGTH
    SMOKE_INVALID_NONSTANDARD  contains X and B  -> NON_STANDARD_RESIDUE
    SMOKE_INVALID_EMPTY        no residues       -> EMPTY_SEQUENCE
    <first real id> repeated   duplicate header  -> DUPLICATE_SEQUENCE_ID
    SMOKE_DUPLICATE_OF_<id>    same residues,    -> mapped, shares an rt_hash, one mapping
                               new identifier       call, two output rows

    make_smoke_input.py <out.faa> [n_per_family]
"""
import os
import sys

ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
BUNDLE = f"{ROOT}/results/FINAL_PRE_UG25_VALIDATION_BUNDLE"
sys.path.insert(0, f"{BUNDLE}/code")

EXPECTED = f"{BUNDLE}/tables/construction_validation_sequence.tsv"

# Construction families only. Families are supplied here explicitly rather than read from
# RT07_AUTHORISED_FAMILIES so that a widened runtime authorisation cannot pull an unintended
# family - least of all UG25 - into a smoke input.
SMOKE_FAMILIES = ("Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA")


def main():
    out_path = sys.argv[1]
    n_per = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    from loader import load_families  # the registered loader, unmodified

    landed = set()
    with open(EXPECTED) as f:
        f.readline()
        for ln in f:
            landed.add(ln.split("\t")[1])

    elig = load_families(SMOKE_FAMILIES)
    picked = []
    for fam in SMOKE_FAMILIES:
        # The construction population is the first 40 ids of the sorted family; restrict to
        # that set so every smoke sequence has a landed expected row.
        ids = [k for k in sorted(elig[fam])[:40] if k in landed]
        picked += [(k, elig[fam][k]) for k in ids[:n_per]]
    if not picked:
        raise SystemExit("FAIL CLOSED: no smoke sequences selected")

    first_id, first_seq = picked[0]
    with open(out_path, "w") as f:
        for k, v in picked:
            f.write(f">{k}\n{v}\n")
        f.write(f">SMOKE_DUPLICATE_OF_{first_id}\n{first_seq}\n")
        f.write(f">{first_id}\n{first_seq}\n")                       # duplicate identifier
        f.write(">SMOKE_INVALID_SHORT\n" + "A" * 180 + "\n")
        f.write(">SMOKE_INVALID_NONSTANDARD\n" + ("A" * 150 + "X" + "G" * 150 + "B") + "\n")
        f.write(">SMOKE_INVALID_EMPTY\n\n")

    print(f"{out_path}: {len(picked)} real + 1 duplicate-sequence + 1 duplicate-id + "
          f"3 invalid")
    for k, v in picked:
        print(f"  {k}  {len(v)} aa")


if __name__ == "__main__":
    main()
