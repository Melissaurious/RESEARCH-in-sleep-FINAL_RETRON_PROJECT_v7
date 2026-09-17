#!/usr/bin/env python3
"""s04 - the historical-to-operational crosswalk, under the rule declared in control/.

Implements control/ASSIGNMENT_RULE.md exactly:

  A3  RT5 <-> g2 block 5 is the ONE anchored pair (source-stated Z11, MEASURED by PC-4).
  A3  every other label<->interval pair is monotone ordinal propagation - `project_inferred`.
  A4  a propagated pair is admissible only if its Route C point falls inside the interval.
  A5  two labels on one interval are reported jointly as SUPPORTED_MANY_TO_1, never split.
  A6  a label inside the unstated RT0/RT1 junction zone, or straddling a stated junction,
      is capped at PARTIAL.
  A7  an interval resolves only if >= 1 frozen anchor state is MAPPED inside it.

Nothing is read from g5 or g6.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import TABLES, read_tsv, write_tsv  # noqa: E402

LABELS = [f"RT{i}" for i in range(8)]
JUNCTION_LO, JUNCTION_HI = 39, 85          # A6, Amendment 1: the unstated RT0/RT1 junction zone
NEAREST_ANCHOR_MAX = 25                    # A8

COLUMNS = ["historical_label", "correspondence", "operational_states", "n_supporting_states",
           "state_span", "ltra_residue_span_supported", "reference_interval_ltra",
           "reference_interval_source", "mapping_route", "route_c_point",
           "route_c_offset_to_nearest_mapped_anchor", "nearest_mapped_anchor_state",
           "uncertainty", "status_reason", "unit", "frame", "denominator"]

FRAME = ("frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue "
         "numbering")
DENOM = "8 historical labels"


def main():
    coords = read_tsv(os.path.join(TABLES, "g7a_coordinate_carriage.tsv"))
    bridge = read_tsv(os.path.join(TABLES, "g7a_state_to_residue.tsv"))
    ctrl = {c["control_id"]: c for c in read_tsv(os.path.join(TABLES, "g7a_controls.tsv"))}

    mapped = [(int(r["state_id"]), int(r["ltra_residue"])) for r in bridge
              if r["call_state"] == "MAPPED"]
    res_lo = min(r for _, r in mapped)
    res_hi = max(r for _, r in mapped)

    blocks = {int(c["coordinate_id"].split("-")[1]): (int(c["ltra_start"]), int(c["ltra_end"]),
                                                      c["uncertainty"], c["note"])
              for c in coords if c["route"] == "P"}
    cpts = {c["historical_label"]: int(c["ltra_start"]) for c in coords if c["route"] == "C"}
    srcs = {c["coordinate_id"]: c for c in coords if c["route"] == "S"}

    if ctrl["PC-4"]["result"] != "PASS":
        raise SystemExit("s04: PC-4 failed - the single anchored pair is lost (rule A3)")

    # --- A3/A4: assignment of labels to g2 blocks -------------------------------------
    # The anchor. Then Route C admissibility decides which block each remaining label sits in.
    assign, admissibility = {}, {}
    for lab in LABELS[1:]:
        pt = cpts.get(lab)
        hit = [i for i, (lo, hi, _, _) in blocks.items() if pt is not None and lo <= pt <= hi]
        assign[lab] = hit[0] if len(hit) == 1 else None
        admissibility[lab] = (
            f"Route C point {pt} falls inside g2 block {hit[0]}" if len(hit) == 1
            else f"Route C point {pt} falls in {len(hit)} blocks - not admissible")
    # A3 check: the anchored pair must agree with the propagation.
    if assign.get("RT5") != 5:
        raise SystemExit(f"s04: anchor violated - RT5 assigned to block {assign.get('RT5')}")
    # A3 check: assignment must be monotone non-decreasing in label order.
    seq = [assign[l] for l in LABELS[1:] if assign[l] is not None]
    if seq != sorted(seq):
        raise SystemExit(f"s04: propagation is not monotone: {seq}")

    shared = {}
    for lab, b in assign.items():
        if b is not None:
            shared.setdefault(b, []).append(lab)

    rows = []
    for lab in LABELS:
        b = assign.get(lab)
        route_c = cpts.get(lab, "")
        # nearest MAPPED anchor to the Route C point (A8)
        near_state, near_off = "", ""
        if route_c:
            cand = sorted(mapped, key=lambda sr: (abs(sr[1] - route_c), sr[0]))
            if cand and abs(cand[0][1] - route_c) <= NEAREST_ANCHOR_MAX:
                near_state, near_off = cand[0][0], cand[0][1] - route_c
            else:
                near_state = "NONE"
                near_off = (f"nearest MAPPED anchor is {abs(cand[0][1] - route_c)} residues "
                            f"away, beyond the declared {NEAREST_ANCHOR_MAX}") if cand else ""

        if lab == "RT0":
            lo, hi = int(srcs["S-c1"]["ltra_start"]), int(srcs["S-c1"]["ltra_end"])
            interval, isrc = f"{lo}-{hi}", ("Blocker 2005 UPPER BOUND (S-c1) plus the interior "
                                            "landmark A39 (S-c2). No stated extent.")
            route = "S (upper bound + interior point)"
        elif b is None:
            interval, isrc, route, lo, hi = "", "no admissible interval", "none", None, None
        else:
            lo, hi, unc, note = blocks[b]
            interval = f"{lo}-{hi}"
            isrc = f"g2 reconstructed block {b} (Route P)"
            route = "P interval, anchored via A3, corroborated by C" if lab != "RT5" else \
                    "P interval, ANCHORED by the source-stated catalytic landmark (Z11), " \
                    "measured by PC-4"

        # --- A7: frozen-state support --------------------------------------------------
        sup = [(s, r) for s, r in mapped if lo is not None and lo <= r <= hi]
        n = len(sup)
        states = ",".join(str(s) for s, _ in sorted(sup)) if n else ""
        span = f"{min(s for s, _ in sup)}-{max(s for s, _ in sup)}" if n else ""
        rspan = f"{min(r for _, r in sup)}-{max(r for _, r in sup)}" if n else ""

        # --- classification ------------------------------------------------------------
        caps, reasons = [], []
        if lo is None:
            corr = "UNRESOLVED"
            reasons.append("no admissible reference interval")
        elif n == 0:
            corr = "NO_SUPPORTED_CROSSWALK"
            reasons.append(
                f"ZERO frozen anchor states map inside LtrA {interval}. The 150 anchors cover "
                f"LtrA {res_lo}-{res_hi} only, so this region lies OUTSIDE the instrument's "
                f"anchor span entirely (rule A7). This is a property of the frozen instrument, "
                f"not a statement about the biology.")
        else:
            partners = shared.get(b, [lab])
            if len(partners) > 1:
                corr = "SUPPORTED_MANY_TO_1"
                reasons.append(f"{' and '.join(partners)} both fall in g2 block {b} and are "
                               f"NOT separable within it (rule A5). Reported jointly.")
            else:
                corr = "SUPPORTED_1_TO_1"
            # A7 partial coverage of the interval
            if lo < res_lo or hi > res_hi:
                caps.append("PARTIAL")
                reasons.append(
                    f"the reference interval {interval} extends beyond the anchor span "
                    f"{res_lo}-{res_hi}; only LtrA {rspan} carries frozen-state support")
            # A6 junction zone
            if lo <= JUNCTION_HI and hi >= JUNCTION_LO:
                caps.append("PARTIAL")
                reasons.append(
                    f"the interval overlaps the UNSTATED RT0/RT1 junction zone "
                    f"{JUNCTION_LO}-{JUNCTION_HI}: Blocker places RT0's conserved alanine at "
                    f"A39 and a cleavage site 'in RT1' at R85, so both labels have a "
                    f"source-stated claim there and the junction is stated nowhere (rule A6)")
        if caps and corr.startswith("SUPPORTED"):
            corr = "PARTIAL"

        # label-specific carried constraints
        if lab == "RT0":
            reasons.append(
                "g3 ruled RT0 OBJECT_MISMATCH and no RT0 occupancy may be reported. Its "
                "defining source (Malik, Burke & Eickbush 1999) is a MISSING_PRIMARY_ASSET, "
                "so RT0 has no stated boundary anywhere in this project's evidence - only an "
                "upper bound and an interior point.")
        if lab == "RT1":
            reasons.append(
                "RT1 is additionally the only landmark that MOVES between prior frames (g3), "
                "and Blocker places R85 INSIDE RT1, so RT1 spans the junction zone.")
        if lab == "RT6":
            reasons.append(
                "RT6 carries no anchor of its own: only ordinal adjacency to the anchored RT5 "
                "and a Route C point, which is comparator evidence and may not resolve alone "
                "(rule A4, route kill). The JOINT RT5+RT6 statement is supported; RT6's own "
                "position inside block 5 is not.")
        if lab == "RT7":
            reasons.append(
                "Independently corroborated by the strongest historical coordinate in the "
                "corpus: Blocker's stated junction 'between RT7 and domain X' at R364/R365 "
                "(S-a). The anchor span ends at LtrA " + str(res_hi) + " and g2 block 6 ends "
                "at 361 - three routes agree the numbered series ends at about 357-365.")

        rows.append(dict(
            historical_label=lab, correspondence=corr, operational_states=states,
            n_supporting_states=n, state_span=span, ltra_residue_span_supported=rspan,
            reference_interval_ltra=interval, reference_interval_source=isrc,
            mapping_route=route, route_c_point=route_c,
            route_c_offset_to_nearest_mapped_anchor=near_off,
            nearest_mapped_anchor_state=near_state,
            uncertainty=blocks[b][2] if b is not None else "n/a",
            status_reason=" | ".join(reasons), unit="historical label", frame=FRAME,
            denominator=DENOM))

    write_tsv(os.path.join(TABLES, "g7a_crosswalk_resolved.tsv"), COLUMNS, rows)

    # --- the prior proposal, as a COMPARATOR column only ------------------------------
    prior = os.path.join(
        os.path.dirname(TABLES), "..", "rt07_pre_g4_identifiability_redesign", "tables",
        "historical_to_operational_mapping_proposed.tsv")
    cmp_rows = []
    if os.path.exists(prior):
        pr = {r["historical_label"]: r for r in read_tsv(prior)}
        for r in rows:
            p = pr.get(r["historical_label"], {})
            cmp_rows.append(dict(
                historical_label=r["historical_label"],
                prior_proposal_cardinality=p.get("cardinality", "(not proposed)"),
                prior_proposal_object=p.get("operational_object", ""),
                g7a_measured_correspondence=r["correspondence"],
                agreement="AGREES" if _agrees(p.get("cardinality", ""), r["correspondence"])
                          else "DIFFERS",
                note="The prior table is a PROPOSAL made before the mapper was frozen and "
                     "before any state->residue measurement existed. It is a hypothesis this "
                     "gate tested, never a result inherited."))
    write_tsv(os.path.join(TABLES, "g7a_prior_proposal_comparison.tsv"),
              ["historical_label", "prior_proposal_cardinality", "prior_proposal_object",
               "g7a_measured_correspondence", "agreement", "note"], cmp_rows)

    print("s04: crosswalk")
    for r in rows:
        print(f"  {r['historical_label']:<4} {r['correspondence']:<22} "
              f"n_states={r['n_supporting_states']:<4} interval={r['reference_interval_ltra']:<8} "
              f"states={r['state_span']}")


def _agrees(prior_card, measured):
    p = (prior_card or "").lower()
    m = measured.lower()
    if "no_valid" in p and ("no_supported" in m or "unresolved" in m):
        return True
    if "many:1" in p and "many_to_1" in m:
        return True
    if "1:1" in p and "1_to_1" in m:
        return True
    if "unresolved" in p and ("unresolved" in m or "no_supported" in m or "partial" in m):
        return True
    return False


if __name__ == "__main__":
    main()
