#!/usr/bin/env python3
"""s07 - the closure decision: one terminal status per label, and the permitted wording.

Terminal status follows control/ASSIGNMENT_RULE.md A10, with one declared downgrade:

  D1  a label whose INDIVIDUAL position rests only on comparator (Route C) evidence is
      downgraded one step, even when the JOINT statement it belongs to is supported. This is
      the route kill of LAUNCHER_03 section 2 applied at label granularity. It affects RT6:
      the joint RT5+RT6 region is supported, RT6's own position inside it is not.

The `downstream_may_say` column is the operative output. It is what g6, g7b, the thesis and
any paper are permitted to assert about each label - nothing more.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import TABLES, read_tsv, write_tsv  # noqa: E402

ESTABLISHED = "ESTABLISHED OPERATIONAL CORRESPONDENCE"
PARTIAL = "PARTIAL / INTERPRETIVE CORRESPONDENCE"
UNRESOLVED = "UNRESOLVED / NOT IDENTIFIABLE"

BASE = {"SUPPORTED_1_TO_1": ESTABLISHED, "SUPPORTED_1_TO_MANY": ESTABLISHED,
        "SUPPORTED_MANY_TO_1": ESTABLISHED, "PARTIAL": PARTIAL,
        "NO_SUPPORTED_CROSSWALK": UNRESOLVED, "UNRESOLVED": UNRESOLVED}
DOWNGRADE = {ESTABLISHED: PARTIAL, PARTIAL: UNRESOLVED, UNRESOLVED: UNRESOLVED}

# D1 applies to labels whose individual position rests only on comparator evidence.
D1_LABELS = {"RT6"}

COLUMNS = ["historical_label", "terminal_status", "correspondence", "supporting_states",
           "ltra_residues_supported", "evidence_basis", "downstream_may_say",
           "downstream_may_not_say", "unit", "denominator"]

MAY_NOT_COMMON = ("May not be called a partition of the RT domain; may not be used to claim a "
                  "family lacks this region (DELETED_STATE is an alignment-path state); may "
                  "not be transferred to another protein without a new measurement - every "
                  "correspondence here was measured ON LtrA.")


def main():
    cross = {r["historical_label"]: r for r in
             read_tsv(os.path.join(TABLES, "g7a_crosswalk_resolved.tsv"))}
    rows = []
    for lab in [f"RT{i}" for i in range(8)]:
        c = cross[lab]
        status = BASE[c["correspondence"]]
        basis = []
        if lab in D1_LABELS and status != UNRESOLVED:
            status = DOWNGRADE[status]
            basis.append("DOWNGRADED by declared rule D1: this label's individual position "
                         "rests only on comparator (Route C) evidence")

        st, res = c["operational_states"], c["ltra_residue_span_supported"]
        span = c["state_span"]

        if lab == "RT0":
            basis.append("Its defining source (Malik, Burke & Eickbush 1999) is a "
                         "MISSING_PRIMARY_ASSET. The held sources give a scope rule, an upper "
                         "bound (M1-R85, which CONTAINS RT0) and an interior landmark (A39) - "
                         "no boundary. Zero frozen anchor states lie in LtrA 1-85.")
            may = ("Nothing operational. RT0 may be discussed as a HISTORICAL concept with its "
                   "scope rule - conserved between group II intron and non-LTR RTs - and as a "
                   "region of LtrA bounded above by residue 85 and containing the conserved "
                   "alanine A39. No RT0 occupancy, fraction, count or boundary may be reported "
                   "on any population.")
        elif lab == "RT1":
            basis.append("Zero frozen anchor states lie in LtrA 39-61, the interval the "
                         "evidence places RT1 in: the instrument's 150 anchors begin at LtrA "
                         "97. RT1 is additionally the only landmark that moves between prior "
                         "frames, and Blocker places the R85 cleavage site INSIDE RT1.")
            may = ("Nothing operational. RT1 may be discussed historically, including the "
                   "founding authors' own statement that domain 1 was the one domain not "
                   "independently confirmed, and Blocker's placement of R85 within it. No RT1 "
                   "occupancy or boundary may be reported. Whether a modern RT1 result "
                   "recovers the 1990 caveat remains a DEFERRED OPERATOR DECISION (g1 U08) "
                   "and is not settled here.")
        elif lab == "RT2":
            basis.append(f"{c['n_supporting_states']} frozen anchor states map inside LtrA "
                         f"{c['reference_interval_ltra']}, but the interval extends below the "
                         f"anchor span, so only LtrA {res} carries support; the interval also "
                         f"overlaps the unstated RT0/RT1 junction zone.")
            may = (f"'Frozen states {span} (LtrA {res}) overlap a literature-supported portion "
                   f"of historical RT2.' The word 'portion' is load-bearing: the N-terminal "
                   f"part of the RT2 interval has no frozen-state support. Do not write 'RT2 "
                   f"is states {span}'.")
        elif lab in ("RT3", "RT4", "RT7"):
            basis.append(f"{c['n_supporting_states']} frozen anchor states map inside LtrA "
                         f"{c['reference_interval_ltra']}, the interval is wholly within the "
                         f"anchor span, and the Route C comparator point falls inside it.")
            if lab == "RT7":
                basis.append("Independently corroborated by the strongest historical "
                             "coordinate in the corpus: Blocker's stated junction 'between RT7 "
                             "and domain X' at R364/R365. Three routes agree the numbered "
                             "series ends at about 357-365.")
            may = (f"'The signal localises to frozen states {span}; these states overlap a "
                   f"literature-supported portion of historical {lab}.' A correspondence "
                   f"measured on LtrA, with {c['n_supporting_states']} supporting states.")
        elif lab in ("RT5", "RT6"):
            basis.append("RT5 and RT6 both fall in g2 block 5 and are NOT separable within it. "
                         "RT5 carries the single source-stated anchor in the whole corpus - "
                         "'the catalytic YxDD motif lies in subdomain 5' - which the frozen "
                         "instrument independently confirmed by placing CAT_STATE 262 at LtrA "
                         "residue 306, inside block 5.")
            if lab == "RT5":
                may = (f"'The signal localises to frozen states {span}; these states overlap a "
                       f"literature-supported portion of the joint historical RT5+RT6 region.' "
                       f"RT5 is the ONLY label with a source-stated feature anchor. The region "
                       f"must be named RT5+RT6 jointly, never RT5 alone.")
            else:
                may = (f"Only as part of the joint region: 'frozen states {span} overlap the "
                       f"joint historical RT5+RT6 region.' No statement may attribute a state "
                       f"to RT6 rather than RT5 - the two are not separable on this evidence.")
        rows.append(dict(
            historical_label=lab, terminal_status=status, correspondence=c["correspondence"],
            supporting_states=st, ltra_residues_supported=res,
            evidence_basis=" | ".join(basis), downstream_may_say=may,
            downstream_may_not_say=MAY_NOT_COMMON,
            unit="historical label", denominator="8 historical labels"))

    write_tsv(os.path.join(TABLES, "g7a_closure_decision.tsv"), COLUMNS, rows)

    # ---- carried-forward register ----------------------------------------------------
    carried = [
        dict(item_id="U01", question="Where is the primary definition of domain 0 / RT0?",
             status_after_g7a="CLOSED_AS_MISSING_PRIMARY_ASSET",
             what_g7a_changed="Retrieval of Malik, Burke & Eickbush 1999 was attempted and "
                              "failed (Europe PMC 403; publisher abstract-only, and the "
                              "abstract does not mention domain 0, domain Z or numbered RT "
                              "domains). Combined with the measured absence of any frozen "
                              "anchor state in LtrA 1-85, RT0's status is now TERMINAL rather "
                              "than open: UNRESOLVED / NOT IDENTIFIABLE."),
        dict(item_id="U02", question="Which blocks do Simon & Zimmerly's 59 alignable "
                                     "characters fall in?",
             status_after_g7a="STILL_OPEN - belongs to g7b",
             what_g7a_changed="Not addressed. It is a published-comparator question."),
        dict(item_id="U06", question="Is Blocker's RT0 (M1-R85) boundary transferable beyond "
                                     "LtrA?",
             status_after_g7a="CLOSED_BY_CORRECTION",
             what_g7a_changed="The premise was wrong. M1-R85 is not an RT0 boundary even ON "
                              "LtrA: Blocker states the R85 cleavage site is IN RT1 and that "
                              "the fragment CONTAINS RT0. The question of transferring it "
                              "does not arise. See control/ASSIGNMENT_RULE.md Amendment 1."),
        dict(item_id="U08", question="Is domain 1's weaker support in 1990 the same object as "
                                     "a later RT1 concordance failure?",
             status_after_g7a="STILL_DEFERRED_TO_OPERATOR",
             what_g7a_changed="g7a measured RT1 (NO_SUPPORTED_CROSSWALK: zero anchors in LtrA "
                              "39-61) and did NOT interpret it. The two objects remain "
                              "distinct. LAUNCHER_02 section 9b reserves this to the operator."),
        dict(item_id="U09", question="Is the block COUNT recoverable at all?",
             status_after_g7a="STILL_OPEN",
             what_g7a_changed="g7a adds one fact: the frozen instrument's 150 anchors resolve "
                              "the region of LtrA carrying blocks 2-6 but none of block 1, so "
                              "no instrument in this project can currently count seven."),
        dict(item_id="U11", question="What is the tag offset in the tagged anchors?",
             status_after_g7a="NOT_NEEDED_FOR_THIS_GATE",
             what_g7a_changed="The primary structural comparator 5G2X is UNTAGGED and its "
                              "numbering agrees with P0A3U0 at 487/487 modelled residues. No "
                              "residue coordinate in this gate was read off a tagged construct."),
        dict(item_id="G7A-1", question="Does the frozen anchor span limit the crosswalk, and "
                                       "can that be repaired?",
             status_after_g7a="NEW - ANSWERED, AND NOT REPAIRED",
             what_g7a_changed="Measured: the 150 anchors span LtrA 97-363 on the bridge "
                              "substrate. Everything N-terminal to 97 is unreachable by the "
                              "frozen instrument. Repairing it would mean rebuilding the "
                              "instrument, which LAUNCHER_03 section 3 forbids and section 2 "
                              "makes a scope kill. It is recorded as a property of the "
                              "instrument."),
    ]
    write_tsv(os.path.join(TABLES, "g7a_unresolved_carried_forward.tsv"),
              ["item_id", "question", "status_after_g7a", "what_g7a_changed"], carried)

    # ---- resolved-value summary ------------------------------------------------------
    bridge = read_tsv(os.path.join(TABLES, "g7a_state_to_residue.tsv"))
    mapped = [r for r in bridge if r["call_state"] == "MAPPED"]
    ctrl = read_tsv(os.path.join(TABLES, "g7a_controls.tsv"))
    reg = read_tsv(os.path.join(TABLES, "g7a_historical_evidence_register.tsv"))
    counts = {}
    for r in rows:
        counts[r["terminal_status"]] = counts.get(r["terminal_status"], 0) + 1

    S = [("historical_labels_in_scope", 8, "g7a_closure_decision.tsv", "historical label",
          "8 historical labels"),
         ("terminal_ESTABLISHED", counts.get(ESTABLISHED, 0), "g7a_closure_decision.tsv",
          "historical label", "8 historical labels"),
         ("terminal_PARTIAL", counts.get(PARTIAL, 0), "g7a_closure_decision.tsv",
          "historical label", "8 historical labels"),
         ("terminal_UNRESOLVED", counts.get(UNRESOLVED, 0), "g7a_closure_decision.tsv",
          "historical label", "8 historical labels"),
         ("evidence_register_rows", len(reg), "g7a_historical_evidence_register.tsv",
          "(label, source) pair", "labels x the sources that name them"),
         ("evidence_rows_source_stated",
          sum(1 for r in reg if r["source_stated_vs_inferred"] == "source_stated"),
          "g7a_historical_evidence_register.tsv", "(label, source) pair",
          "all evidence register rows"),
         ("anchors_mapped_on_ltra", len(mapped), "g7a_state_to_residue.tsv",
          "frozen anchor state", "150 frozen anchor states"),
         ("anchor_state_span", f"{min(int(r['state_id']) for r in mapped)}-"
                               f"{max(int(r['state_id']) for r in mapped)}",
          "g7a_state_to_residue.tsv", "state_id", "n/a - a span"),
         ("anchor_ltra_residue_span", f"{min(int(r['ltra_residue']) for r in mapped)}-"
                                      f"{max(int(r['ltra_residue']) for r in mapped)}",
          "g7a_state_to_residue.tsv", "LtrA residue", "n/a - a span"),
         ("controls_pass", sum(1 for c in ctrl if c["result"] == "PASS"),
          "g7a_controls.tsv", "control", f"{len(ctrl)} declared controls"),
         ("controls_fail", sum(1 for c in ctrl if c["result"] == "FAIL"),
          "g7a_controls.tsv", "control", f"{len(ctrl)} declared controls"),
         ("controls_inconclusive", sum(1 for c in ctrl if c["result"] == "INCONCLUSIVE"),
          "g7a_controls.tsv", "control", f"{len(ctrl)} declared controls"),
         ("ltra_numbering_checks_agree", "12/12 residues, 3/4 Edman sequences",
          "g7a_ltra_numbering_control.tsv", "stated residue identity",
          "12 Blocker-stated residues"),
         ("structural_comparators_independent", 0, "g7a_structural_comparators.tsv",
          "structure", "3 declared structural comparators"),
         ("missing_primary_assets", 1, "g7a_acquisition_register.tsv", "asset",
          "assets this gate needed")]
    write_tsv(os.path.join(TABLES, "g7a_summary.tsv"),
              ["quantity", "value", "source_table", "unit", "denominator"],
              [dict(quantity=a, value=b, source_table=c, unit=d, denominator=e)
               for a, b, c, d, e in S])

    print("s07: closure decision")
    for r in rows:
        print(f"  {r['historical_label']:<4} {r['terminal_status']}")
    print(f"  -> {counts.get(ESTABLISHED,0)} established, {counts.get(PARTIAL,0)} partial, "
          f"{counts.get(UNRESOLVED,0)} unresolved")


if __name__ == "__main__":
    main()
