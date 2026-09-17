#!/usr/bin/env python3
"""rt07_g3 step 2 - independence and contamination, re-measured from the prior files.

The prior audit reported that its validation sets were seed-contaminated. This gate does not
adopt those figures; it recomputes them from the prior FASTA files by exact sequence
identity - sha256 over residues - because that is the only identifier that survives between
project versions. Ids and accessions were reassigned; sequences were not.

Three questions, each with its own denominator:
  1. how much of each prior validation set is also in the set that built the frame;
  2. what those sets are actually made of (a crystallography construct with a purification
     tag is not a native RT, and residue numbers taken from one are not native numbering);
  3. whether the prior sets appear in the frozen Stage-1 catalogue at all, which is what
     decides whether g4 can build a held-out population from them.

Writes: tables/g3_set_identity.tsv, tables/g3_set_overlap.tsv,
        tables/g3_anchor_composition.tsv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g3lib import (PROJ, control, fasta_hashes, read_fasta, resolve,  # noqa: E402
                       seq_hash, sha256_file, write_tsv)

STAGE1_FAA = PROJ / "data/derived/rt_exact_v1.faa"
# Expression-construct fingerprints. A native bacterial RT does not carry these.
TAGS = {
    "His6": "HHHHHH",
    "SUMO/SMT3": "QDSSEIHFKVKMTTHLKKLKESYCQRQGVP",
    "thrombin_LVPRGS": "LVPRGS",
    "TEV_ENLYFQ": "ENLYFQ",
    "Strep_WSHPQFEK": "WSHPQFEK",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--with-stage1", action="store_true",
                    help="also hash the 501,561-sequence Stage-1 catalogue (~40 s)")
    args = ap.parse_args()
    T = args.out

    sets = control("prior_sets.tsv")
    loaded: dict[str, dict[str, str]] = {}
    identity = []
    for s in sets:
        p = resolve(s["relative_path"])
        if not p.is_file():
            identity.append({"set_id": s["set_id"], "path": str(p), "state": "MISSING",
                             "n_sequences": 0, "n_unique_sequences": 0, "sha256": "ABSENT",
                             "name_claims": s["name_claims"], "role_in_prior_work": s["role"],
                             "unit": "sequence set", "denominator": "prior sets declared"})
            continue
        seqs = read_fasta(p)
        loaded[s["set_id"]] = {k: seq_hash(v) for k, v in seqs.items()}
        uniq = len(set(loaded[s["set_id"]].values()))
        identity.append({
            "set_id": s["set_id"], "path": str(p), "state": "READ",
            "n_sequences": len(seqs), "n_unique_sequences": uniq,
            "sha256": sha256_file(p), "name_claims": s["name_claims"],
            "role_in_prior_work": s["role"],
            "name_matches_content": ("YES" if str(s["name_claims"]) in ("", "n/a")
                                     or str(len(seqs)) == str(s["name_claims"]) else "NO"),
            "unit": "sequence set", "denominator": "prior sets declared in control/"})
    write_tsv(T / "g3_set_identity.tsv",
              ["set_id", "path", "state", "n_sequences", "n_unique_sequences", "sha256",
               "name_claims", "name_matches_content", "role_in_prior_work", "unit",
               "denominator"], identity)

    # ---------- overlaps, by exact sequence identity ----------
    pairs = control("overlap_pairs.tsv")
    overlaps = []
    for pr in pairs:
        a, b = pr["set_a"], pr["set_b"]
        if a not in loaded or b not in loaded:
            overlaps.append({"set_a": a, "set_b": b, "state": "SET_MISSING",
                             "n_a": 0, "n_b": 0, "n_shared_sequences": 0,
                             "pct_of_a_in_b": "", "prior_reported": pr["prior_reported"],
                             "verdict": "NOT_TESTABLE", "question": pr["question"],
                             "unit": "exact protein sequence",
                             "denominator": "members of set A"})
            continue
        ha, hb = set(loaded[a].values()), set(loaded[b].values())
        shared = ha & hb
        pct = 100 * len(shared) / len(ha) if ha else 0.0
        overlaps.append({
            "set_a": a, "set_b": b, "state": "MEASURED",
            "n_a": len(ha), "n_b": len(hb), "n_shared_sequences": len(shared),
            "pct_of_a_in_b": f"{pct:.2f}",
            "prior_reported": pr["prior_reported"],
            "verdict": ("SEED_CONTAMINATED" if pct >= 50 else
                        "PARTIALLY_CONTAMINATED" if pct > 0 else "DISJOINT"),
            "question": pr["question"],
            "unit": "exact protein sequence (sha256 over residues)",
            "denominator": f"{len(ha)} unique sequences in {a}"})
    write_tsv(T / "g3_set_overlap.tsv",
              ["set_a", "set_b", "state", "n_a", "n_b", "n_shared_sequences",
               "pct_of_a_in_b", "prior_reported", "verdict", "question", "unit",
               "denominator"], overlaps)

    # ---------- what the anchor set is actually made of ----------
    comp = []
    if "anchors72" in loaded:
        seqs = read_fasta(resolve(next(s["relative_path"] for s in sets
                                    if s["set_id"] == "anchors72")))
        kinds: dict[str, int] = {}
        tagged: dict[str, list[str]] = {t: [] for t in TAGS}
        for k, v in seqs.items():
            kinds[k.split("_")[0]] = kinds.get(k.split("_")[0], 0) + 1
            for t, motif in TAGS.items():
                if motif in v.upper():
                    tagged[t].append(k)
        for kind, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
            comp.append({
                "property": f"id_prefix:{kind}", "value": n,
                "pct_of_set": f"{100 * n / len(seqs):.2f}",
                "why_it_matters": ("PDB entries are the only members with an actual structure; "
                                   "the rest are sequence-propagated"
                                   if kind == "PDB" else
                                   "carries no structure of its own"),
                "members": "", "unit": "anchor", "denominator": f"{len(seqs)} anchors"})
        for t, ids in tagged.items():
            if ids:
                comp.append({
                    "property": f"expression_tag:{t}", "value": len(ids),
                    "pct_of_set": f"{100 * len(ids) / len(seqs):.2f}",
                    "why_it_matters": "A purification tag is vector-derived sequence. Residue "
                                      "numbering taken from a tagged construct is offset from "
                                      "native numbering by the length of the tag, so any "
                                      "boundary read off it is shifted unless the offset was "
                                      "removed.",
                    "members": ",".join(sorted(ids)),
                    "unit": "anchor", "denominator": f"{len(seqs)} anchors"})
    write_tsv(T / "g3_anchor_composition.tsv",
              ["property", "value", "pct_of_set", "why_it_matters", "members", "unit",
               "denominator"], comp)

    # ---------- presence in the frozen Stage-1 catalogue ----------
    if args.with_stage1 and STAGE1_FAA.is_file():
        stage1 = set(fasta_hashes(STAGE1_FAA).values())
        rows = []
        for sid, h in loaded.items():
            if len(h) > 5000:
                continue
            hs = set(h.values())
            n = len(hs & stage1)
            rows.append({
                "set_a": sid, "set_b": "stage1_exact_rt_catalogue", "state": "MEASURED",
                "n_a": len(hs), "n_b": len(stage1), "n_shared_sequences": n,
                "pct_of_a_in_b": f"{100 * n / len(hs):.2f}" if hs else "",
                "prior_reported": "not previously measured",
                "verdict": "PRESENT_IN_CATALOGUE" if n else "ABSENT_FROM_CATALOGUE",
                "question": "can g4 build a held-out population from this set at all?",
                "unit": "exact protein sequence (sha256 over residues)",
                "denominator": f"{len(hs)} unique sequences in {sid}"})
        prev = list(read_tsv(T / "g3_set_overlap.tsv"))
        write_tsv(T / "g3_set_overlap.tsv",
                  ["set_a", "set_b", "state", "n_a", "n_b", "n_shared_sequences",
                   "pct_of_a_in_b", "prior_reported", "verdict", "question", "unit",
                   "denominator"], prev + rows)

    print(f"sets read: {sum(1 for i in identity if i['state'] == 'READ')}/{len(identity)}")
    for o in overlaps:
        print(f"  {o['set_a']:>14} in {o['set_b']:<18} "
              f"{o['n_shared_sequences']:>6}/{o['n_a']:<6} = {o['pct_of_a_in_b']:>6}%  "
              f"{o['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
