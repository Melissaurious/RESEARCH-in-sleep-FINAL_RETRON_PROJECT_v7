#!/usr/bin/env python3
"""pre-g4 step 1 - the identity and composition of the old seed, and every member's lineage.

This is not a rediscovery. The old seed `all167.faa` was built deliberately as
anchors72 + 95 CAND_* candidates, and the anchor set was selected on documented criteria
including measured RT-DNA production. `anchors72 = 72/72 of the seed` is therefore TRUE BY
CONSTRUCTION, and this gate records it as construction rather than as contamination.

What is genuinely unresolved, and what this step lands, is the per-sequence lineage: for
every member of the seed, its hash, its stated origin, and - in step 2 - its relationship to
every population the later work used as a comparator or a validation set.

The scientific problem is not that the seed contains its own anchors. It is the downstream
reuse of seed components as purported independent validation.

Writes: tables/preg4_seed_identity.tsv, tables/preg4_sequence_lineage.tsv
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preg4lib import POPULATIONS, read_fasta, seq_hash, sha256_file, write_tsv  # noqa: E402

SEED = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign"
            "/step3_hmm/cache/all167.faa")
ANCHOR_PROV = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/"
                   "stage2b_assessor_redesign/anchors/anchor_set_v1_provenance.tsv")
TAGS = {"His6": "HHHHHH", "SUMO/SMT3": "QDSSEIHFKVKMTTHLKKLKESYCQRQGVP",
        "thrombin_LVPRGS": "LVPRGS", "TEV_ENLYFQ": "ENLYFQ", "Strep_WSHPQFEK": "WSHPQFEK"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    args = ap.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)

    if not SEED.is_file():
        print(f"FAIL seed absent: {SEED}", file=sys.stderr)
        return 1
    seed = read_fasta(SEED)
    prefixes: dict[str, int] = {}
    for k in seed:
        prefixes[k.split("_")[0]] = prefixes.get(k.split("_")[0], 0) + 1

    prov = {}
    if ANCHOR_PROV.is_file():
        import csv
        with ANCHOR_PROV.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                key = r.get("anchor_id") or r.get("id") or ""
                prov[key] = r

    identity = [
        ("seed_path", str(SEED)), ("seed_sha256", sha256_file(SEED)),
        ("n_sequences", len(seed)),
        ("n_unique_sequences", len({seq_hash(v) for v in seed.values()})),
        ("n_anchor_members", sum(v for k, v in prefixes.items() if k != "CAND")),
        ("n_CAND_members", prefixes.get("CAND", 0)),
        ("composition", " + ".join(f"{v} {k}_*" for k, v in sorted(prefixes.items()))),
        ("anchors_in_seed_by_construction",
         "YES - the seed was built as anchors72 + 95 CAND_*, so 72/72 anchor membership is "
         "a property of how it was made, not a contamination discovery"),
        ("what_is_actually_circular",
         "downstream reuse of seed components as purported independent validation material"),
    ]
    write_tsv(args.out / "preg4_seed_identity.tsv",
              ["quantity", "value", "unit", "denominator"],
              [{"quantity": q, "value": v, "unit": "seed property",
                "denominator": f"{len(seed)} sequences in all167.faa"} for q, v in identity])

    rows = []
    for name, s in seed.items():
        pre = name.split("_")[0]
        p = prov.get(name, {})
        tags = [t for t, m in TAGS.items() if m in s.upper()]
        rows.append({
            "sequence_id": name, "sequence_hash": seq_hash(s), "length_aa": len(s),
            "id_prefix": pre,
            "membership_class": ("ANCHOR" if pre in ("RETRON", "PDB", "UNIPROT")
                                 else "CANDIDATE"),
            "evidence_tier": p.get("tier", p.get("evidence_tier", "")) or
                             ("A_experimental_structure" if pre == "PDB" else
                              "B_characterised_protein" if pre in ("RETRON", "UNIPROT")
                              else "UNDOCUMENTED_IN_ANCHOR_PROVENANCE"),
            "declared_source": p.get("source", p.get("source_db", "")) or
                               ("RCSB PDB" if pre == "PDB" else
                                "UniProtKB" if pre == "UNIPROT" else
                                "support.csv (measured RT-DNA activity)" if pre == "RETRON"
                                else "SEE_CAND_PROVENANCE"),
            "original_identifier": p.get("original_id", p.get("pdb_id", "")) or "",
            "selection_reason": p.get("selection_reason", p.get("reason", "")) or
                                ("RTDNA_DEMONSTRATED >= 0.10" if pre == "RETRON" else ""),
            "activity_evidence_if_any": p.get("rtdna", p.get("rtdna_production", "")) or "",
            "expression_tags_detected": ",".join(tags) or "none",
            "coordinate_offset_risk": ("YES - vector-derived residues precede the native "
                                       "sequence" if tags else "no"),
            "unit": "seed member",
            "denominator": f"{len(seed)} sequences in all167.faa",
        })
    write_tsv(args.out / "preg4_sequence_lineage.tsv",
              ["sequence_id", "sequence_hash", "length_aa", "id_prefix", "membership_class",
               "evidence_tier", "declared_source", "original_identifier", "selection_reason",
               "activity_evidence_if_any", "expression_tags_detected",
               "coordinate_offset_risk", "unit", "denominator"], rows)

    # the query FASTA every later step searches with
    (args.work / "all167.faa").write_text(
        "\n".join(f">{k}\n{v}" for k, v in seed.items()) + "\n", encoding="utf-8")

    print(f"seed: {len(seed)} sequences, {len({seq_hash(v) for v in seed.values()})} unique")
    for k, v in sorted(prefixes.items(), key=lambda kv: -kv[1]):
        print(f"  {k + '_*':<12} {v}")
    print(f"anchor provenance rows read: {len(prov)}")
    print(f"tagged constructs in the seed: "
          f"{sum(1 for r in rows if r['expression_tags_detected'] != 'none')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
