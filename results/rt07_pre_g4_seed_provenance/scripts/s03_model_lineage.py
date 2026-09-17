#!/usr/bin/env python3
"""pre-g4 step 3 - which prior model was built from which subset, read off the files.

Every prior profile declares its own NSEQ. Matching that against the sizes of the known
subsets (all167, anchors72, the balanced 25, ph38, RETRON_SEED's 1,500) says which set a
model was trained on without trusting any document. Where NSEQ is ambiguous the row says so
rather than guessing.

This matters for one reason: a model trained on all167 has seen every anchor and every
candidate, so it cannot be used to score them. g4 inherits none of these as training truth.

Writes: tables/preg4_model_lineage.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preg4lib import V3, V4, sha256_file, write_tsv  # noqa: E402

SEARCH_ROOTS = [
    V3 / "stage2b_assessor_redesign",
    V4 / "D_instrument/cache",
    V4 / "rt0_rt7_domain_test/cache",
    V4 / "rt0_rt7_domain_test_v2/cache",
]
# NSEQ -> the set that size implies
KNOWN_SIZES = {
    167: "all167 (anchors72 + 95 CAND_*) - the old seed",
    72: "anchors72 - the anchor set, itself inside all167",
    25: "the balanced 25-anchor subset",
    38: "ph38 - the earlier crystal panel",
    24: "the 24 re-scanned crystal entries upstream of the 26 PDB anchors",
    26: "the 26 PDB structural anchors",
    1500: "RETRON_SEED - 1,500 sampled corpus retrons",
    742: "Toro 2014 published RT0-RT7 set (comparator)",
    1642: "frameR - a 1,642-sequence reconstruction frame",
    1844: "myRT reference set (comparator)",
}


def hmm_header(p: Path) -> dict[str, str]:
    out = {}
    with p.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("HMM "):
                break
            parts = line.split(None, 1)
            if len(parts) == 2:
                out.setdefault(parts[0], parts[1].strip())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    seen: set[str] = set()
    for root in SEARCH_ROOTS:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.hmm")):
            sha = sha256_file(p)
            hdr = hmm_header(p)
            nseq = hdr.get("NSEQ", "")
            implied = KNOWN_SIZES.get(int(nseq)) if nseq.isdigit() else None
            rows.append({
                "model_path": str(p), "model_name_declared": hdr.get("NAME", ""),
                "file_stem": p.stem, "leng": hdr.get("LENG", ""), "nseq": nseq,
                "built_from_set_implied_by_nseq": implied or "AMBIGUOUS - NSEQ matches no "
                                                             "known subset size",
                "name_matches_file": "YES" if hdr.get("NAME", "") == p.stem else
                                     f"NO - declares {hdr.get('NAME', '?')}",
                "duplicate_of": "",
                "sha256": sha,
                "role_in_g4": ("PRIOR / AUDIT / COMPARATOR - not training truth for g4"),
                "unit": "prior model", "denominator": "profile HMMs found under the "
                                                      "audited prior trees",
            })
            seen.add(sha)

    by_sha: dict[str, list[str]] = {}
    for r in rows:
        by_sha.setdefault(r["sha256"], []).append(r["file_stem"])
    for r in rows:
        twins = [x for x in by_sha[r["sha256"]] if x != r["file_stem"]]
        r["duplicate_of"] = ",".join(sorted(set(twins))) or "none"

    write_tsv(args.out / "preg4_model_lineage.tsv",
              ["model_path", "model_name_declared", "file_stem", "leng", "nseq",
               "built_from_set_implied_by_nseq", "name_matches_file", "duplicate_of",
               "sha256", "role_in_g4", "unit", "denominator"], rows)

    counts: dict[str, int] = {}
    for r in rows:
        counts[r["built_from_set_implied_by_nseq"]] = \
            counts.get(r["built_from_set_implied_by_nseq"], 0) + 1
    print(f"prior models found: {len(rows)} ({len(set(by_sha))} distinct by sha256)")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {v:>3}  {k}")
    dups = sum(1 for r in rows if r["duplicate_of"] != "none")
    mism = sum(1 for r in rows if r["name_matches_file"].startswith("NO"))
    print(f"models shipping under a name they do not declare: {mism}")
    print(f"models that are byte-duplicates of another file: {dups}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
