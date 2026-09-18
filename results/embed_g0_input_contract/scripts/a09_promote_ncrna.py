#!/usr/bin/env python
"""embed-g0/a09 - promote rt_ncrna_oriented_v1.* into the CANONICAL derived layer.

THE PROBLEM THIS SOLVES. embed_g0 built the dataset in the `embeddings-g0` worktree's
data/derived/ because the main worktree's is read-only from that sandbox. Two directories
now both look like "the derived layer", and a consumer cannot tell which one it read. That
is the thing to close - not by picking one at read time, but by making the canonical layer
hold the file and the worktree copy be provably identical to it.

SAFETY CONTRACT - this script will NOT:
  - overwrite an existing canonical file whose content differs (it REFUSES and reports);
  - overwrite an existing canonical file whose content is identical (it reports a no-op);
  - modify, rename or delete anything else in the canonical layer;
  - run at all without --apply. The default is a dry run that only reads.

It WILL, under --apply and only for files that are absent from the canonical layer:
  copy, re-hash at the destination, and set mode 444.

Usage:
    python a09_promote_ncrna.py              # dry run, read-only, exit 0/1
    python a09_promote_ncrna.py --apply      # promote the absent files only
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

SRC = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings/data/derived")
DST = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
MANIFEST = SRC / "rt_ncrna_oriented_v1.MANIFEST.tsv"
FILES = ["rt_ncrna_oriented_v1.fna", "rt_ncrna_oriented_v1.parquet",
         "rt_ncrna_oriented_v1.provenance.json", "rt_ncrna_oriented_v1.MANIFEST.tsv"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="actually copy the ABSENT files; without it nothing is written")
    a = ap.parse_args()

    # 1 - the source must still match the manifest it shipped with
    declared = {}
    for line in MANIFEST.read_text().splitlines()[1:]:
        p, _b, h = line.split("\t")
        declared[Path(p).name] = h
    print("[1] source integrity against rt_ncrna_oriented_v1.MANIFEST.tsv")
    bad = []
    for n, h in declared.items():
        got = sha(SRC / n)
        ok = got == h
        print(f"    {'OK  ' if ok else 'FAIL'}  {n}  {got[:16]}")
        if not ok:
            bad.append(n)
    if bad:
        print(f"\nREFUSING: source does not match its own manifest ({bad}). Nothing done.")
        return 1

    # 2 - classify each destination
    print("\n[2] destination state")
    absent, identical, conflict = [], [], []
    for n in FILES:
        d = DST / n
        if not d.exists():
            absent.append(n); print(f"    ABSENT     {n}")
        elif sha(d) == sha(SRC / n):
            identical.append(n); print(f"    IDENTICAL  {n}  (already promoted; no-op)")
        else:
            conflict.append(n); print(f"    CONFLICT   {n}  destination differs from source")

    if conflict:
        print(f"\nREFUSING: {len(conflict)} canonical file(s) exist with DIFFERENT content:")
        for n in conflict:
            print(f"    {n}\n      canonical {sha(DST/n)}\n      worktree  {sha(SRC/n)}")
        print("\nA canonical file is never silently replaced. Resolve by hand: decide which is\n"
              "authoritative, record the decision in docs/decisions/, then re-run.")
        return 1

    if not absent:
        print("\nNOTHING TO DO - every file is already present and identical.")
        print("The worktree copy is now provably a duplicate, not a competing layer.")
        return 0

    # 3 - act
    if not a.apply:
        print(f"\nDRY RUN. {len(absent)} file(s) would be copied: {', '.join(absent)}")
        print(f"  {SRC}/  ->  {DST}/")
        print("Re-run with --apply to promote. Nothing has been written.")
        return 0

    print(f"\n[3] promoting {len(absent)} absent file(s)")
    for n in absent:
        shutil.copy2(SRC / n, DST / n)
        got = sha(DST / n)
        if got != sha(SRC / n):
            raise AssertionError(f"copy corrupted {n}")
        os.chmod(DST / n, 0o444)
        print(f"    promoted  {n}  {got[:16]}  mode 444")
    print("\nPROMOTED. Verify independently with:")
    print(f"  cd {DST.parent.parent} && sha256sum -c <(awk 'NR>1{{print $3\"  \"$1}}' "
          f"data/derived/rt_ncrna_oriented_v1.MANIFEST.tsv)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
