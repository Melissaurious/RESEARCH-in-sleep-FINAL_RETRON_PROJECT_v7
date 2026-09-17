#!/usr/bin/env python3
"""s02 - reference coordinate carriage. Every historical coordinate, in LtrA residues, by route.

Route S - source-stated residue coordinates (Blocker 2005, corrected by Amendment 1).
Route P - primary-derived intervals (the six g2 blocks, reconstructed on ALIGN_000044 under
          Xiong & Eickbush's own stated criterion), with their landed uncertainty.
Route C - comparator points (prior-frame RT1-RT7 landmarks carried to LtrA by g3).

Route P and Route C are READ FROM LANDED TABLES, never retyped. Route S is declared from
PDF-verified quotes recorded in s01 and control/ASSIGNMENT_RULE.md Amendment 1.

No g5 or g6 path is read here or anywhere in this gate.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g7alib import G2T, G3T, TABLES, read_tsv, write_tsv  # noqa: E402

# The prior frame used for Route C. g3 carried four prior frames onto LtrA and they AGREE on
# every LtrA residue, so the frame choice does not move a coordinate; RT17_CORE is named
# because the frozen bundle's own crosswalk names it.
ROUTE_C_FRAME = "RT17_CORE"

COLUMNS = ["coordinate_id", "route", "historical_label", "ltra_start", "ltra_end",
           "coordinate_kind", "evidence_class", "source_stated_vs_inferred", "source",
           "uncertainty", "note", "unit", "frame", "denominator"]

FRAME = "LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa"
DENOM = "historical coordinates carried onto LtrA by this gate"


def route_s():
    """Source-stated residue coordinates. See control/ASSIGNMENT_RULE.md Amendment 1."""
    src = "Blocker et al. 2005, PDF-verified in s01 (g1 assignment B02 plus Table 1 and text)"
    return [
        dict(coordinate_id="S-a", route="S", historical_label="RT7",
             ltra_start=364, ltra_end=365, coordinate_kind="stated_domain_junction",
             evidence_class="EXPLICIT_STATED_BOUNDARY", source_stated_vs_inferred="source_stated",
             source=src,
             uncertainty="the junction is a proteolytic cleavage site between R364 and R365; "
                         "the site is stated, the domain edge is inferred to coincide with it",
             note="'two major cleavage sites, one in RT1 and the other BETWEEN RT7 AND DOMAIN "
                  "X'. The strongest historical coordinate in the held corpus. It bounds the "
                  "END of the numbered series."),
        dict(coordinate_id="S-b", route="S", historical_label="RT1",
             ltra_start=85, ltra_end=85, coordinate_kind="stated_interior_point",
             evidence_class="EXPLICIT_STATED_BOUNDARY", source_stated_vs_inferred="source_stated",
             source=src,
             uncertainty="a point, not an edge",
             note="'the Arg-C cleavage site IN RT1 (R85)'. RT1 spans residue 85. This is NOT "
                  "an RT0|RT1 boundary."),
        dict(coordinate_id="S-c1", route="S", historical_label="RT0",
             ltra_start=1, ltra_end=85, coordinate_kind="stated_upper_bound",
             evidence_class="EXPLICIT_STATED_BOUNDARY", source_stated_vs_inferred="source_stated",
             source=src,
             uncertainty="an UPPER BOUND on RT0's extent, not RT0's extent",
             note="'a 10-kDa N-terminal fragment CONTAINING RT0 (M1-R85)'. Table 1's column is "
                  "headed 'Domain composition'."),
        dict(coordinate_id="S-c2", route="S", historical_label="RT0",
             ltra_start=39, ltra_end=39, coordinate_kind="stated_interior_point",
             evidence_class="EXPLICIT_STATED_BOUNDARY", source_stated_vs_inferred="source_stated",
             source=src,
             uncertainty="a point, not an edge",
             note="the conserved alanine in the N-terminal portion of RT0. RT0 contains "
                  "residue 39."),
        dict(coordinate_id="S-d", route="S", historical_label="RT0|RT1",
             ltra_start=39, ltra_end=85, coordinate_kind="unstated_junction_zone",
             evidence_class="NO_STATED_BOUNDARY", source_stated_vs_inferred="project_inferred",
             source="derived from S-b and S-c2",
             uncertainty="the entire 47-residue window is unresolved",
             note="RT0 contains 39 and RT1 contains 85, so the junction between them lies in "
                  "39-85 and is stated NOWHERE in the held corpus."),
    ]


def route_p():
    """The six g2 blocks in LtrA residues, with their landed column-level uncertainty."""
    blocks = read_tsv(os.path.join(G2T, "g2_ltra_mapping.tsv"))
    unc = {r["block_index"]: r for r in read_tsv(os.path.join(G2T, "g2_block_uncertainty.tsv"))}
    corr = {r["frame1_block"]: r for r in
            read_tsv(os.path.join(G2T, "g2_frame_correspondence.tsv"))}
    out = []
    for b in blocks:
        i = b["block_index"]
        u, c = unc.get(i, {}), corr.get(i, {})
        ub = "; ".join(f"{k}={v}" for k, v in u.items()
                       if k not in ("block_index", "unit", "frame", "denominator") and v)
        out.append(dict(
            coordinate_id=f"P-{i}", route="P", historical_label="(unlabelled g2 block)",
            ltra_start=int(b["ltra_start_residue"]), ltra_end=int(b["ltra_end_residue"]),
            coordinate_kind="primary_derived_interval",
            evidence_class="ALIGNMENT_BLOCK", source_stated_vs_inferred="project_inferred",
            source="rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under "
                   "Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion",
            uncertainty=ub or "see g2_block_uncertainty.tsv",
            note=f"g2 block {i}. Cross-frame correspondence: "
                 f"{c.get('correspondence', 'n/a')} (Jaccard "
                 f"{c.get('jaccard_on_ltra_residues', 'n/a')} on LtrA residues). "
                 f"g2 recovered SIX blocks, not seven. Labels are attached in s04 by the "
                 f"declared rule, never here."))
    return out


def route_c():
    """Prior-frame RT1-RT7 point landmarks on LtrA. COMPARATOR ONLY - may never resolve alone."""
    rows = read_tsv(os.path.join(G3T, "g3_prior_region_correspondence.tsv"))
    frames = sorted({r["frame_id"] for r in rows})
    out = []
    for r in rows:
        if r["frame_id"] != ROUTE_C_FRAME or not r["ltra_start"]:
            continue
        # agreement across all prior frames for this label
        same = {x["ltra_start"] for x in rows
                if x["prior_label"] == r["prior_label"] and x["ltra_start"]}
        out.append(dict(
            coordinate_id=f"C-{r['prior_label']}", route="C",
            historical_label=r["prior_label"],
            ltra_start=int(r["ltra_start"]), ltra_end=int(r["ltra_end"]),
            coordinate_kind="comparator_point_landmark",
            evidence_class="PRIOR_FRAME_POINT", source_stated_vs_inferred="project_inferred",
            source=f"rt07_g3_prior_method_replication, prior frame {ROUTE_C_FRAME}",
            uncertainty=f"a single point; agreement across {len(frames)} prior frames: "
                        f"{'ALL AGREE' if len(same) == 1 else 'DISAGREE ' + '/'.join(sorted(same))}",
            note="COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks "
                 "were placed by interpolating order between only 4 motif-anchored blocks."))
    return out


def main():
    rows = route_s() + route_p() + route_c()
    for r in rows:
        r.update(unit="historical coordinate on LtrA", frame=FRAME, denominator=DENOM)
    write_tsv(os.path.join(TABLES, "g7a_coordinate_carriage.tsv"), COLUMNS, rows)
    by = {}
    for r in rows:
        by[r["route"]] = by.get(r["route"], 0) + 1
    print("s02: " + ", ".join(f"Route {k}: {v} coordinates" for k, v in sorted(by.items())))
    for r in rows:
        if r["route"] == "C":
            assert "ALL AGREE" in r["uncertainty"], f"prior frames disagree: {r}"
    print("s02: all Route C landmarks agree across the four prior frames")


if __name__ == "__main__":
    main()
