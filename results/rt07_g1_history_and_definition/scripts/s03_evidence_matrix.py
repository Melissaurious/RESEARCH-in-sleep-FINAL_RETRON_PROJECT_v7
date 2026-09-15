#!/usr/bin/env python3
"""rt07_g1 step 3 - the gate's measurement: evidence class per (source, region name).

Every assignment in control/evidence_assignments.tsv carries a verbatim quote, and this
script VERIFIES each quote against the extracted text before it is allowed to support a
cell. A quote that does not appear is a build failure, not a warning: the whole point of
the gate is that its classifications are checkable at the source, and an unverifiable
quote is indistinguishable from a remembered one. Page locators are derived from the text,
never asserted by hand.

Cells with no assignment are filled from the census as NOT_NAMED_IN_SOURCE or
NAMED_UNCLASSIFIED - and a NOT_NAMED cell is reportable only where the positive control of
step 2 licensed that zero. Naming is not defining, and not naming is not absence.

Region verdicts follow from the classes, not from an opinion:
  STATED_RESIDUE_BOUNDARY  some source states residue coordinates for the region
  DERIVABLE_PROCEDURE      no coordinates, but a restatable construction rule or motif
                           evidence exists, so g2 can attempt recovery
  SCOPE_RULE_ONLY          only a statement of WHERE the concept applies
  NO_OPERATIONAL_BASIS     named, but no source supplies motif, alignment, procedure or
                           boundary evidence. Per launcher section 2 such a region is NOT
                           given a boundary later in the track.

Writes (under --out): g1_evidence_quotes.tsv, g1_literature_evidence_matrix.tsv,
                      g1_terminology_genealogy.tsv, g1_operational_evidence_matrix.tsv,
                      g1_region_verdicts.tsv, g1_unresolved_definition_register.tsv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g1lib import control, multi, normalise, read_tsv, write_tsv  # noqa: E402

UNIT = "(source, region_name) pair"
FRAME = "derivational primary literature plus the acquired primary alignment (launcher 5d)"

# Strongest last: which class a cell reports when several apply.
STRENGTH = ["TERMINOLOGY_ONLY", "INHERITED_WITHOUT_DEFINITION", "MOTIF_EVIDENCE",
            "ALIGNMENT_BLOCK", "EXPLICIT_STATED_BOUNDARY"]
OPERATIONAL_CLASSES = {"MOTIF_EVIDENCE", "ALIGNMENT_BLOCK", "EXPLICIT_STATED_BOUNDARY"}


def locate(quote: str, work: Path, sid: str) -> tuple[str, str]:
    """Verify a quote against the source text and derive its page. Never asserted."""
    whole = normalise((work / "text" / f"{sid}.raw.txt").read_text(encoding="utf-8",
                                                                  errors="replace"))
    q = normalise(quote)
    if q in whole:
        for p in sorted((work / "text" / "pages").glob(f"{sid}.raw.p*.txt")):
            if q in normalise(p.read_text(encoding="utf-8", errors="replace")):
                return "VERIFIED", p.stem.split(".p")[-1].lstrip("0")
        return "VERIFIED", "spans a page break"
    # second route, in case the raw rendering broke the sentence differently
    alt = normalise((work / "text" / f"{sid}.layout.txt").read_text(encoding="utf-8",
                                                                   errors="replace"))
    if q in alt:
        return "VERIFIED_LAYOUT_ROUTE_ONLY", "layout route"
    return "NOT_FOUND", ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    vocab = {r["region_id"]: r for r in control("region_vocabulary.tsv")}
    sources = {r["source_id"]: r for r in control("sources.tsv")}
    kinds = {r["assignment_id"]: r["boundary_kind"] for r in control("boundary_kinds.tsv")}
    census = {(r["source_id"], r["region_id"]): r
              for r in read_tsv(args.out / "g1_token_census.tsv")}
    ctrl = read_tsv(args.out / "g1_detector_positive_control.tsv")
    licensed = {c["region_id"] for c in ctrl if c["result"] == "PASS"}

    # ---- quotes, verified ----
    quotes, unverified = [], []
    for a in control("evidence_assignments.tsv"):
        state, page = locate(a["quote"], args.work, a["source_id"])
        row = {"assignment_id": a["assignment_id"], "source_id": a["source_id"],
               "region_ids": a["region_id"], "evidence_class": a["evidence_class"],
               "boundary_kind": kinds.get(a["assignment_id"], "NOT_A_BOUNDARY"),
               "verification": state, "page_locator": page,
               "quote": normalise(a["quote"]), "note": a["note"],
               "unit": "quoted passage", "denominator": "assignments declared in control/"}
        quotes.append(row)
        if state == "NOT_FOUND":
            unverified.append(row)

    if unverified:
        for u in unverified:
            print(f"FAIL unverifiable quote {u['assignment_id']} ({u['source_id']}): "
                  f"{u['quote'][:90]}", file=sys.stderr)
        return 1

    # ---- literature evidence matrix: every source x every region ----
    per_cell: dict[tuple[str, str], list[dict]] = {}
    for q in quotes:
        for rid in multi(q["region_ids"]):
            per_cell.setdefault((q["source_id"], rid), []).append(q)

    matrix = []
    for sid, s in sources.items():
        for rid, v in vocab.items():
            c = census[(sid, rid)]
            named = int(c["n_named_total_raw"])
            cell = per_cell.get((sid, rid), [])
            if cell:
                classes = sorted({x["evidence_class"] for x in cell},
                                 key=STRENGTH.index)
                reported = classes[-1]
                boundaries = sorted({x["boundary_kind"] for x in cell} - {"NOT_A_BOUNDARY"})
            else:
                classes, boundaries = [], []
                reported = "NAMED_UNCLASSIFIED" if named else "NOT_NAMED_IN_SOURCE"
            matrix.append({
                "source_id": sid, "evidence_tier": s["evidence_tier"],
                "region_id": rid, "region_name": v["region_name"],
                "rt0_rt7_scope": v["rt0_rt7_scope"],
                "evidence_class": reported,
                "all_classes_present": "|".join(classes) or "NONE",
                "boundary_kinds": "|".join(boundaries) or "NONE",
                "n_supporting_quotes": len(cell),
                "assignment_ids": "|".join(x["assignment_id"] for x in cell) or "NONE",
                "n_times_named_in_text": named,
                "zero_is_licensed_by_control": (
                    "n/a - the region is named here" if named else
                    ("YES" if rid in licensed else "NO - reported as NOT_NAMED without a "
                                                   "validated detector")),
                "unit": UNIT, "frame": FRAME, "stratum": s["evidence_tier"],
                "denominator": f"{len(sources)} sources x {len(vocab)} region names "
                               f"= {len(sources) * len(vocab)} cells",
            })

    # ---- terminology genealogy ----
    genealogy = []
    for g in control("genealogy_edges.tsv"):
        state, page = locate(g["quote"], args.work, g["naming_source"])
        if state == "NOT_FOUND":
            print(f"FAIL unverifiable genealogy quote {g['edge_id']}", file=sys.stderr)
            return 1
        genealogy.append({
            "edge_id": g["edge_id"], "region_ids": g["region_id"],
            "n_regions": len(multi(g["region_id"])),
            "naming_source": g["naming_source"], "label_used": g["label_used"],
            "inherits_from_citation": g["inherits_from_citation"],
            "antecedent_held_locally": g["source_held_locally"],
            "edge_kind": g["edge_kind"], "verification": state, "page_locator": page,
            "quote": normalise(g["quote"]), "note": g["note"],
            "unit": "genealogy edge (region, naming source, antecedent)",
            "denominator": "edges traceable in the held derivational set",
        })

    # ---- operational-evidence matrix ----
    qid = {q["assignment_id"]: q for q in quotes}
    operational = []
    for o in control("operational_assessment.tsv"):
        basis = multi(o["basis_assignments"])
        missing = [b for b in basis if b not in qid]
        if missing:
            print(f"FAIL {o['assessment_id']} cites unknown assignment(s) {missing}",
                  file=sys.stderr)
            return 1
        for rid in multi(o["region_id"]):
            operational.append({
                "assessment_id": o["assessment_id"], "source_id": o["source_id"],
                "region_id": rid, "region_name": vocab[rid]["region_name"],
                "can_define_operational_boundary": o["can_define_operational_boundary"],
                "operational_output_available": o["operational_output_available"],
                "what_it_cannot_do": o["what_it_cannot_do"],
                "circularity_risk": o["circularity_risk"],
                "basis_assignments": o["basis_assignments"],
                "basis_all_verified": "YES",
                "unit": "(source, region) operational capability",
                "frame": FRAME,
                "stratum": sources[o["source_id"]]["evidence_tier"],
                "denominator": "region-source pairs with any evidence in this gate",
            })

    # ---- region verdicts ----
    verdicts = []
    for rid, v in vocab.items():
        cells = [m for m in matrix if m["region_id"] == rid]
        classes = {c for m in cells for c in m["all_classes_present"].split("|")} - {"NONE"}
        bkinds = {b for m in cells for b in m["boundary_kinds"].split("|")} - {"NONE"}
        named_in = [m["source_id"] for m in cells if m["n_times_named_in_text"] != "0"
                    and int(m["n_times_named_in_text"]) > 0]
        # A spelling and the concept it spells are different objects, and so are a
        # structural region and a sequence block. Collapsing either pair into one verdict
        # would make 'RT1 has no operational basis' readable as a statement about the
        # block, which is false: the block is domain_1 and it is DERIVABLE_PROCEDURE.
        if v["series"] == "modern_spelling":
            verdict = ("SPELLING_WITH_STRUCTURAL_COORDINATE_ONLY"
                       if "RESIDUE_COORDINATE" in bkinds
                       else "SPELLING_ONLY_NO_INDEPENDENT_DERIVATION")
        elif v["series"] == "structural_partition":
            verdict = ("STRUCTURAL_DEFINED_ELSEWHERE" if classes
                       else "NOT_IN_HELD_EVIDENCE")
        elif "RESIDUE_COORDINATE" in bkinds:
            verdict = "STATED_RESIDUE_BOUNDARY"
        elif classes & OPERATIONAL_CLASSES:
            verdict = "DERIVABLE_PROCEDURE"
        elif "SCOPE_RULE" in bkinds:
            verdict = "SCOPE_RULE_ONLY"
        elif classes:
            verdict = "NO_OPERATIONAL_BASIS"
        elif named_in:
            verdict = "NAMED_NO_EVIDENCE_CLASS"
        else:
            verdict = "NOT_IN_HELD_EVIDENCE"
        verdicts.append({
            "region_id": rid, "region_name": v["region_name"], "series": v["series"],
            "rt0_rt7_scope": v["rt0_rt7_scope"], "verdict": verdict,
            "classes_anywhere": "|".join(sorted(classes, key=STRENGTH.index)) or "NONE",
            "boundary_kinds_anywhere": "|".join(sorted(bkinds)) or "NONE",
            "n_sources_naming_it": len(named_in),
            "sources_naming_it": ",".join(sorted(named_in)) or "NONE",
            "may_receive_a_boundary_later": (
                "NO - launcher section 2: no operational basis" if verdict in
                ("NO_OPERATIONAL_BASIS", "NOT_IN_HELD_EVIDENCE", "NAMED_NO_EVIDENCE_CLASS")
                else "NO - not a sequence block" if verdict == "STRUCTURAL_DEFINED_ELSEWHERE"
                else "YES - as the concept it spells, not as a spelling"
                if verdict.startswith("SPELLING") else "YES"),
            "unit": "region name", "frame": FRAME,
            "stratum": v["series"],
            "denominator": f"{len(vocab)} region names in scope",
        })

    # ---- unresolved-definition register ----
    unresolved = []
    for u in control("unresolved_items.tsv"):
        unresolved.append({**u, "origin": "declared in control/unresolved_items.tsv",
                           "unit": "open definitional question",
                           "denominator": "questions this gate could not close"})
    for v in verdicts:
        if v["verdict"] in ("NO_OPERATIONAL_BASIS", "NOT_IN_HELD_EVIDENCE",
                            "NAMED_NO_EVIDENCE_CLASS"):
            unresolved.append({
                "item_id": f"AUTO_{v['region_id']}",
                "question": f"Does any primary source supply operational evidence for "
                            f"{v['region_name']}?",
                "region_id": v["region_id"],
                "why_it_matters": "A region with no operational basis may not be given a "
                                  "boundary later in this track (launcher section 2).",
                "evidence_state_after_g1": f"{v['verdict']}; named by "
                                           f"{v['n_sources_naming_it']} source(s); classes: "
                                           f"{v['classes_anywhere']}",
                "blocking_for": "nothing - the region is excluded from boundary work",
                "default_taken": "Record NO_OPERATIONAL_BASIS and do not score the region.",
                "status": "CLOSED_AS_NO_BASIS",
                "origin": "derived from the region verdicts",
                "unit": "open definitional question",
                "denominator": "questions this gate could not close",
            })

    write_tsv(args.out / "g1_evidence_quotes.tsv",
              ["assignment_id", "source_id", "region_ids", "evidence_class",
               "boundary_kind", "verification", "page_locator", "quote", "note", "unit",
               "denominator"], quotes)
    write_tsv(args.out / "g1_literature_evidence_matrix.tsv",
              ["source_id", "evidence_tier", "region_id", "region_name", "rt0_rt7_scope",
               "evidence_class", "all_classes_present", "boundary_kinds",
               "n_supporting_quotes", "assignment_ids", "n_times_named_in_text",
               "zero_is_licensed_by_control", "unit", "frame", "stratum", "denominator"],
              matrix)
    write_tsv(args.out / "g1_terminology_genealogy.tsv",
              ["edge_id", "region_ids", "n_regions", "naming_source", "label_used",
               "inherits_from_citation", "antecedent_held_locally", "edge_kind",
               "verification", "page_locator", "quote", "note", "unit", "denominator"],
              genealogy)
    write_tsv(args.out / "g1_operational_evidence_matrix.tsv",
              ["assessment_id", "source_id", "region_id", "region_name",
               "can_define_operational_boundary", "operational_output_available",
               "what_it_cannot_do", "circularity_risk", "basis_assignments",
               "basis_all_verified", "unit", "frame", "stratum", "denominator"],
              operational)
    write_tsv(args.out / "g1_region_verdicts.tsv",
              ["region_id", "region_name", "series", "rt0_rt7_scope", "verdict",
               "classes_anywhere", "boundary_kinds_anywhere", "n_sources_naming_it",
               "sources_naming_it", "may_receive_a_boundary_later", "unit", "frame",
               "stratum", "denominator"], verdicts)
    write_tsv(args.out / "g1_unresolved_definition_register.tsv",
              ["item_id", "question", "region_id", "why_it_matters",
               "evidence_state_after_g1", "blocking_for", "default_taken", "status",
               "origin", "unit", "denominator"], unresolved)

    counts: dict[str, int] = {}
    for m in matrix:
        counts[m["evidence_class"]] = counts.get(m["evidence_class"], 0) + 1
    print(f"quotes verified  : {len(quotes)}/{len(quotes)}")
    print(f"matrix cells     : {len(matrix)}")
    for k in sorted(counts, key=lambda x: -counts[x]):
        print(f"  {k:<28} {counts[k]}")
    print(f"genealogy edges  : {len(genealogy)}")
    print(f"unresolved items : {len(unresolved)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
