#!/usr/bin/env python3
"""s05 - structural / reference comparators. Structure INTERPRETS or CHALLENGES; it never defines.

5G2X chain C is LtrA itself - the same protein the whole historical frame is denominated in.
That makes it the primary structural comparator for THIS gate, and it is the correction this
gate carries against the registered g7 plan, which named 6AR1. 6AR1 is a DIFFERENT protein
(GsI-IIC RT, Geobacillus stearothermophilus) and is His8-tagged.

Independence is measured, not assumed. A structure whose protein is inside the mapper's
construction population is a crosswalk ILLUSTRATION, not an independent test.

Structure may NOT manufacture the seven-way partition (LAUNCHER_02 section 3, section 5d;
operator decision 2026-09-15 section B).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import TABLES, chain_residues, ltra_sequence, read_tsv, write_tsv  # noqa: E402

# From results/rt07_pre_g4_scope_separation/tables/structure_reference_inventory.tsv, which
# recorded anchor-set membership and expression tags per entry. g3 measured anchors72 at 100%
# seed membership, so an anchor-set member is NOT independent of the mapper.
INVENTORY = {
    "5G2X": dict(chain="C", protein="Lactococcus lactis LtrA P0A3U0", tag="none",
                 in_26_anchor_set="YES", method="EM", resolution="3.8"),
    "6AR1": dict(chain="A", protein="Geobacillus stearothermophilus GsI-IIC RT E2GM63",
                 tag="His8 C-terminal", in_26_anchor_set="YES", method="X-ray",
                 resolution="3.01"),
    "7V9U": dict(chain="A", protein="E. coli retron Ec86 P23070", tag="none",
                 in_26_anchor_set="YES", method="EM", resolution="3.12"),
}

COLUMNS = ["comparator", "chain", "protein", "relation_to_ltra_frame", "independence_verdict",
           "independence_basis", "expression_tag", "numbering_agreement",
           "what_it_says_about_the_crosswalk", "agreement_class", "caveat",
           "unit", "frame", "denominator"]


def main():
    _, ltra = ltra_sequence()
    cross = read_tsv(os.path.join(TABLES, "g7a_crosswalk_resolved.tsv"))
    bridge = read_tsv(os.path.join(TABLES, "g7a_state_to_residue.tsv"))
    mapped = {int(r["state_id"]): int(r["ltra_residue"]) for r in bridge
              if r["call_state"] == "MAPPED"}
    panel = {r["sequence_id"]: r for r in read_tsv(os.path.join(TABLES, "g7a_panel_results.tsv"))}

    rows, extra = [], []

    # ---- 5G2X : LtrA itself ----------------------------------------------------------
    res = chain_residues("5G2X", INVENTORY["5G2X"]["chain"])
    ks = sorted(res)
    agree = sum(1 for k in ks if 1 <= k <= len(ltra) and ltra[k - 1] == res[k])
    numbering = (f"{agree}/{len(ks)} modelled residues agree with the project's LtrA record "
                 f"(AAB06503/P0A3U0); modelled range {ks[0]}-{ks[-1]}")
    # per-label structural coverage
    covered = []
    for c in cross:
        span = c["ltra_residue_span_supported"]
        if not span:
            covered.append(f"{c['historical_label']}: no supported span")
            continue
        lo, hi = (int(x) for x in span.split("-"))
        n = sum(1 for k in ks if lo <= k <= hi)
        covered.append(f"{c['historical_label']}: {n}/{hi - lo + 1} supported residues modelled")
    rows.append(dict(
        comparator="5G2X", chain="C", protein=INVENTORY["5G2X"]["protein"],
        relation_to_ltra_frame="THE SAME PROTEIN - the structure of LtrA itself",
        independence_verdict="NOT_INDEPENDENT",
        independence_basis="5G2X is an anchor-set member (in_26_anchor_set=YES) and g3 measured "
                           "anchors72 at 100% seed membership. It is therefore a crosswalk "
                           "ILLUSTRATION, not an independent test.",
        expression_tag=INVENTORY["5G2X"]["tag"] + " - no tag offset to remove",
        numbering_agreement=numbering,
        what_it_says_about_the_crosswalk="; ".join(covered),
        agreement_class="AGREES_ON_COORDINATES",
        caveat="Agreement here is agreement about RESIDUE NUMBERING, which is what the "
               "crosswalk needs from this structure. It is NOT independent evidence that a "
               "historical label is correctly placed, and it cannot be: structure may not "
               "manufacture the seven-way partition.",
        unit="structural comparator", frame="PDB author residue numbering vs LtrA P0A3U0",
        denominator="3 declared structural comparators"))

    extra.append(dict(check_id="PC-3", kind="structural numbering control",
                      expectation="5G2X chain C author numbering agrees with P0A3U0 at every "
                                  "modelled residue, and Blocker's landmarks A39/R85/R86 are "
                                  "present in the structure",
                      observed=f"{agree}/{len(ks)} modelled residues agree; "
                               f"residue 39={res.get(39)}, 85={res.get(85)}, 86={res.get(86)}, "
                               f"364={res.get(364, 'not modelled')}",
                      result="PASS" if agree == len(ks) else "FAIL",
                      note="Zero offset. This is what makes 5G2X usable as a coordinate "
                           "comparator at all, and it is measured here rather than inherited "
                           "from the prior reference_boundaries extraction, which is DO-NOT-USE."))

    # ---- 6AR1 and 7V9U : different proteins ------------------------------------------
    for pdb, sid in (("6AR1", "GsIIIC_6AR1_A"), ("7V9U", "Ec86_7V9U_A")):
        inv = INVENTORY[pdb]
        p = panel.get(sid)
        if p is None or p.get("verdict") != "MAPPED":
            says = "the frozen instrument did not commit on this sequence; non-comparable"
            cls = "NON_COMPARABLE"
        else:
            says = (f"the frozen instrument commits on this protein "
                    f"({p['n_mapped']}/150 anchors, mapped fraction {p['mapped_fraction']}), so "
                    f"the SAME state_ids are locatable in it. It therefore shows the frozen "
                    f"state axis is not LtrA-specific. It says NOTHING about where a "
                    f"historical label sits, because no held source states an RT0-RT7 "
                    f"coordinate on this protein.")
            cls = "NON_COMPARABLE_FOR_THE_HISTORICAL_LABELS"
        rows.append(dict(
            comparator=pdb, chain=inv["chain"], protein=inv["protein"],
            relation_to_ltra_frame="A DIFFERENT PROTEIN - no held source states an RT0-RT7 "
                                   "coordinate on it",
            independence_verdict="NOT_INDEPENDENT",
            independence_basis=f"anchor-set member (in_26_anchor_set={inv['in_26_anchor_set']}); "
                               "g3 measured anchors72 at 100% seed membership",
            expression_tag=inv["tag"] + (" - residue numbering from a tagged construct is "
                                         "offset by the tag length and was NOT used to place "
                                         "any boundary" if inv["tag"] != "none" else ""),
            numbering_agreement="not applicable - a different protein, not compared residue by "
                                "residue to LtrA",
            what_it_says_about_the_crosswalk=says, agreement_class=cls,
            caveat="Included to test whether the frozen state axis transfers as a COORDINATE "
                   "SYSTEM, not to place a historical label. Panel sequences are built from "
                   "MODELLED residues only and carry internal chain breaks.",
            unit="structural comparator", frame="PDB author residue numbering",
            denominator="3 declared structural comparators"))

    write_tsv(os.path.join(TABLES, "g7a_structural_comparators.tsv"), COLUMNS, rows)

    # append PC-3 to the controls table
    cpath = os.path.join(TABLES, "g7a_controls.tsv")
    ctrl = read_tsv(cpath)
    ctrl = [c for c in ctrl if c["control_id"] != "PC-3"]
    ctrl.append(dict(control_id=extra[0]["check_id"], kind=extra[0]["kind"],
                     expectation=extra[0]["expectation"], observed=extra[0]["observed"],
                     result=extra[0]["result"], note=extra[0]["note"]))
    ctrl.sort(key=lambda c: c["control_id"])
    write_tsv(cpath, ["control_id", "kind", "expectation", "observed", "result", "note"], ctrl)

    print(f"s05: 5G2X numbering {agree}/{len(ks)} modelled residues agree with P0A3U0 "
          f"(PC-3 {extra[0]['result']})")
    for r in rows:
        print(f"  {r['comparator']:<6} {r['independence_verdict']:<17} {r['agreement_class']}")
    if extra[0]["result"] != "PASS":
        raise SystemExit("s05: PC-3 FAILED - the structural comparator carries an offset")


if __name__ == "__main__":
    main()
