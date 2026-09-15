#!/usr/bin/env python3
"""rt07_g1 step 2 - the mechanical naming census, and the control that licenses its zeros.

For every (source, region name) this counts how often the region is NAMED, on both
extraction routes, with page locators. Naming is not defining: the evidence class is
assigned in step 3 from quoted text. Keeping the two apart is the point of the gate.

Ranges are expanded explicitly. 'subdomains 0-7' names eight regions, and a census that
counted only the literal token '0' would under-read exactly the paper that numbers the
partition. Literal and range-expanded counts are both kept.

POSITIVE CONTROL (EVIDENCE_STANDARDS 6). Most cells here are zero, and a zero from an
untested detector is not evidence. Two controls run:
  - MODERN SPELLING: Blocker 2005 is known to use RT0-RT7, so the identical pattern must
    return non-zero there. If it does not, every zero elsewhere lands DETECTOR_UNVALIDATED.
  - ALIGNMENT ANNOTATION: the claim that ALIGN_000044 carries no subdomain annotation is a
    negative about a file, so the same detector must be shown to find the domain names the
    file does carry. A detector that finds nothing anywhere proves nothing.
--seed-bad corrupts the patterns on purpose; run.sh asserts that the controls then FAIL.

Writes (under --out): g1_token_census.tsv, g1_census_route_agreement.tsv,
                      g1_detector_positive_control.tsv
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g1lib import control, normalise, read_tsv, write_tsv  # noqa: E402

UNIT = "(source, region_name) pair"
FRAME = "extracted-text naming census v1 (poppler pdftotext; routes raw|layout)"

# region_id -> regex naming ONE region. Built from control/region_vocabulary.tsv ids.
PATTERNS: dict[str, str] = {
    **{f"domain_{i}": rf"\b(?:sub)?domains?\s+{i}\b" for i in range(0, 8)},
    **{f"rt{i}_spelling": rf"\bRT-?{i}\b" for i in range(0, 8)},
    "rt_domain_whole": r"\breverse transcriptase domain\b|\bRT domain\b",
    "domain_2a": r"\b(?:sub)?domains?\s+2[aA]\b",
    "domain_X": r"\bdomain\s+X\b",
    **{f"motif_{c}": rf"\bmotifs?\s+{c}\b" for c in "ABCDEF"},
    "regions_a_e": r"\bregions?\s+[a-e]\b",
    "spacer_4_5": r"\b4/5\s+spacer\b",
    "spacer_7_X": r"\b7/X\s+spacer\b",
    "struct_palm": r"\bpalm\b",
    "struct_fingers": r"\bfingers?\b",
    "struct_thumb": r"\bthumb\b",
    "motif_YXDD": r"\b[YF]\s?[xX]\s?DD\b|\bYGDD\b",
}

RANGE_PAT = re.compile(
    r"\b(?:sub)?domains?\s+(\d)\s*(?:-|to|and|,)\s*(?:and\s+)?(\d)\b"
    r"|\bRT-?(\d)\s*(?:-|to)\s*(?:RT-?)?(\d)\b", re.I)

CONTROL_SPELLING = [f"rt{i}_spelling" for i in range(0, 8)]
CONTROL_SOURCE = "blocker2005"
# The alignment record's own domain vocabulary: what a working detector must find there.
ALIGNMENT_CONTROL_REGIONS = ["rt_domain_whole"]
ALIGNMENT_SOURCE = "align000044"
ALIGNMENT_ABSENT_REGIONS = [f"domain_{i}" for i in range(0, 8)] + \
                           [f"rt{i}_spelling" for i in range(0, 8)]


def count(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.I))


def ranges(text: str) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for m in RANGE_PAT.finditer(text):
        a, b = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        lo, hi = sorted((int(a), int(b)))
        if hi - lo > 7:
            continue
        key = "domain_{}" if m.group(1) else "rt{}_spelling"
        for i in range(lo, hi + 1):
            out[key.format(i)] += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seed-bad", action="store_true",
                    help="corrupt the detector on purpose; the controls must then fail")
    args = ap.parse_args()

    pats = dict(PATTERNS)
    if args.seed_bad:
        # A detector that cannot match anything. If the controls still pass with this in
        # place, the controls are decorative and the gate's zeros mean nothing.
        pats = {k: r"(?!x)x" for k in pats}

    text_dir = args.work / "text"
    vocab = {r["region_id"]: r for r in control("region_vocabulary.tsv")}
    srcs = read_tsv(text_dir / "extraction_manifest.tsv")

    census, disagree = [], []
    for s in srcs:
        sid = s["source_id"]
        texts = {r: normalise((text_dir / f"{sid}.{r}.txt").read_text(encoding="utf-8",
                                                                     errors="replace"))
                 for r in ("raw", "layout")}
        rng = {r: ranges(t) for r, t in texts.items()}
        page_files = sorted((text_dir / "pages").glob(f"{sid}.raw.p*.txt"))
        page_text = [(int(p.stem.split(".p")[-1]),
                      normalise(p.read_text(encoding="utf-8", errors="replace")))
                     for p in page_files]

        for rid, meta in vocab.items():
            pat = pats[rid]
            n = {r: count(t, pat) for r, t in texts.items()}
            nr = {r: rng[r].get(rid, 0) for r in ("raw", "layout")}
            hits = sorted({pg for pg, t in page_text if re.search(pat, t, re.I)})
            census.append({
                "source_id": sid, "evidence_tier": s["evidence_tier"],
                "region_id": rid, "region_name": meta["region_name"],
                "series": meta["series"], "rt0_rt7_scope": meta["rt0_rt7_scope"],
                "n_literal_raw": n["raw"], "n_literal_layout": n["layout"],
                "n_range_expanded_raw": nr["raw"], "n_range_expanded_layout": nr["layout"],
                "n_named_total_raw": n["raw"] + nr["raw"],
                "routes_agree": "YES" if (n["raw"] == n["layout"]
                                          and nr["raw"] == nr["layout"]) else "NO",
                "pages_with_hit": ",".join(map(str, hits)) or "NONE",
                "unit": UNIT, "frame": FRAME, "stratum": s["evidence_tier"],
                "denominator": f"{len(vocab)} region names x {len(srcs)} sources in scope",
            })
            if n["raw"] != n["layout"] or nr["raw"] != nr["layout"]:
                disagree.append({
                    "source_id": sid, "region_id": rid, "region_name": meta["region_name"],
                    "n_literal_raw": n["raw"], "n_literal_layout": n["layout"],
                    "n_range_expanded_raw": nr["raw"],
                    "n_range_expanded_layout": nr["layout"],
                    "delta_layout_minus_raw": (n["layout"] + nr["layout"]) - (n["raw"] + nr["raw"]),
                    "reported_route": "raw", "retained_as": "ROUTE_DISAGREEMENT_RETAINED",
                    "unit": UNIT, "denominator": "cells where the two routes differ",
                })

    by = {(r["source_id"], r["region_id"]): r for r in census}
    controls = []

    for rid in CONTROL_SPELLING:
        others = [r for (s, i), r in by.items() if i == rid and s != CONTROL_SOURCE]
        n_ctrl = by[(CONTROL_SOURCE, rid)]["n_named_total_raw"]
        zeros = sorted(r["source_id"] for r in others if r["n_named_total_raw"] == 0)
        controls.append({
            "control_id": f"spelling:{rid}", "control_kind": "MODERN_SPELLING_DETECTOR",
            "region_id": rid, "control_source": CONTROL_SOURCE,
            "expected": "non-zero in a source known to use the modern spelling",
            "observed": n_ctrl,
            "result": "PASS" if n_ctrl > 0 else "FAIL",
            "licenses": f"reading {len(zeros)} zero cell(s) as 'this source does not use "
                        f"this name': {','.join(zeros) or 'none'}",
            "n_zero_cells_licensed": len(zeros),
            "denominator": f"{len(others)} non-control sources searched",
            "unit": UNIT, "frame": FRAME,
        })

    for rid in ALIGNMENT_CONTROL_REGIONS:
        n_ctrl = by[(ALIGNMENT_SOURCE, rid)]["n_named_total_raw"]
        absent = [r for r in ALIGNMENT_ABSENT_REGIONS
                  if by[(ALIGNMENT_SOURCE, r)]["n_named_total_raw"] == 0]
        controls.append({
            "control_id": f"alignment_annotation:{rid}",
            "control_kind": "ALIGNMENT_ANNOTATION_DETECTOR",
            "region_id": rid, "control_source": ALIGNMENT_SOURCE,
            "expected": "non-zero: the record does name the domain it annotates",
            "observed": n_ctrl,
            "result": "PASS" if n_ctrl > 0 else "FAIL",
            "licenses": f"reading {len(absent)} numbered region(s) as not annotated in the "
                        f"authors own alignment record",
            "n_zero_cells_licensed": len(absent),
            "denominator": f"{len(ALIGNMENT_ABSENT_REGIONS)} numbered regions searched in "
                           f"the alignment record",
            "unit": UNIT, "frame": FRAME,
        })

    write_tsv(args.out / "g1_token_census.tsv",
              ["source_id", "evidence_tier", "region_id", "region_name", "series",
               "rt0_rt7_scope", "n_literal_raw", "n_literal_layout",
               "n_range_expanded_raw", "n_range_expanded_layout", "n_named_total_raw",
               "routes_agree", "pages_with_hit", "unit", "frame", "stratum",
               "denominator"], census)
    write_tsv(args.out / "g1_census_route_agreement.tsv",
              ["source_id", "region_id", "region_name", "n_literal_raw", "n_literal_layout",
               "n_range_expanded_raw", "n_range_expanded_layout", "delta_layout_minus_raw",
               "reported_route", "retained_as", "unit", "denominator"], disagree)
    write_tsv(args.out / "g1_detector_positive_control.tsv",
              ["control_id", "control_kind", "region_id", "control_source", "expected",
               "observed", "result", "licenses", "n_zero_cells_licensed", "denominator",
               "unit", "frame"], controls)

    failed = [c for c in controls if c["result"] != "PASS"]
    print(f"census rows      : {len(census)} ({len(srcs)} sources x {len(vocab)} regions)")
    print(f"named cells      : {sum(1 for r in census if r['n_named_total_raw'] > 0)}")
    print(f"route disagreement: {len(disagree)} cell(s), retained")
    print(f"positive controls: {len(controls) - len(failed)}/{len(controls)} PASS")
    if args.seed_bad:
        print("seed-bad mode: controls SHOULD have failed")
        return 0 if failed else 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
