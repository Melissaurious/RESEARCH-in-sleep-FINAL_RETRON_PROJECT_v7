#!/usr/bin/env python3
"""Historical RT0-RT7 crosswalk - a SEPARATE interpretation layer, never a production label.

Launcher §5: production outputs are not renamed RT0-RT7. Production emits `state_id` in the
frozen GII-derived profile's coordinate system. Anything that claims a historical RT label
is interpretation and lives here, joined on `state_id`, with `UNRESOLVED` preserved wherever
the correspondence is not supported.

## Why every row is currently UNRESOLVED

The two coordinate systems are different objects and no measured bridge between them exists:

  * the PRODUCTION ruler is `GII.deriv.hmm`, LENG 471, sha256 292495a4..., built under
    `hhmake -M 50` in g4a;
  * the HISTORICAL landmarks RT1-RT7 are single POINTS - not spans - in the prior frame
    `RT17_CORE` / `B_span17`, LENG 305, sha256 f3ddb0b5...
    (`results/rt07_g3_prior_method_replication/tables/g3_frame_identity.tsv`), carried onto
    LtrA residue coordinates in `g3_prior_region_correspondence.tsv`.

g3 measured prior-frame match state -> LtrA residue. Nothing measured production state ->
LtrA residue, and nothing measured production state -> prior-frame state. Producing that
bridge is new measurement. g4b is packaging only, so the bridge is NOT manufactured here;
the recipe is registered for g7 instead (see `docs/G7_STRUCTURE_PLAN.md`).

## Findings that constrain any future resolution - carried forward from g3, not re-litigated

  * the seven prior labels collapse onto SIX independently reconstructed g2 regions; RT5 and
    RT6 share one. A seven-way partition is not inheritable
    (`g3_handoff_to_g4.tsv`: `no_seven_way_partition_to_inherit`).
  * RT0 is `OBJECT_MISMATCH`: the prior RT0 region excludes the RT0 landmark, and the
    defining claim is untestable on the available substrate. No RT0 occupancy may be
    reported (`rt0_out_of_scope_for_occupancy`).
  * RT1 is the only landmark that MOVES between prior frames, and it maps into the Blocker
    RT0 zone on LtrA. It is a declared uncertainty (`rt1_is_the_unstable_landmark`).

So even a fully executed g7 bridge cannot return seven clean labels. `UNRESOLVED` is the
honest value, and `RT0` additionally carries `OBJECT_MISMATCH`.

## Contract

`crosswalk_rows()` returns the frozen table. `annotate(state_id)` returns the historical
correspondence for a production state. Downstream code that wants a historical label must
call this module explicitly - it can never arrive by accident in a production column.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CROSSWALK_TABLE = os.path.normpath(
    os.path.join(HERE, "..", "..", "control", "CROSSWALK_RT0_RT7.tsv"))

COLUMNS = ("historical_label", "historical_frame", "historical_frame_leng",
           "historical_coordinate_kind", "historical_match_state", "ltra_residue",
           "operational_state", "historical_RT0_RT7_correspondence_if_supported",
           "status_reason", "source")

UNRESOLVED = "UNRESOLVED"


def crosswalk_rows():
    rows = []
    for ln in open(CROSSWALK_TABLE):
        if ln.startswith("#") or ln.startswith("historical_label") or not ln.strip():
            continue
        rows.append(dict(zip(COLUMNS, ln.rstrip("\n").split("\t"))))
    return rows


def annotate(state_id):
    """Historical correspondence for one production state. Always a list - a production
    state may in principle correspond to several historical labels, and forcing 1:1 is
    exactly the seven-boxes error g3 warned against."""
    hits = [r for r in crosswalk_rows()
            if r["operational_state"] not in ("", UNRESOLVED)
            and int(r["operational_state"]) == int(state_id)]
    return hits or [{"historical_RT0_RT7_correspondence_if_supported": UNRESOLVED,
                     "status_reason": "NO_MEASURED_BRIDGE_PRODUCTION_STATE_TO_PRIOR_FRAME"}]


def assert_unresolved_until_g7():
    """Fail closed if anyone resolves a crosswalk row without landing a g7 measurement.

    This is a packaging guard, not a scientific one: it stops a plausible-looking label from
    being typed into the frozen table between now and g7.
    """
    bad = [r["historical_label"] for r in crosswalk_rows()
           if r["historical_RT0_RT7_correspondence_if_supported"] != UNRESOLVED]
    if bad:
        raise SystemExit(
            f"FAIL CLOSED: crosswalk rows claim a resolved correspondence without a landed "
            f"g7 measurement: {bad}. Resolving these requires measuring production state -> "
            f"prior frame, which is g7 work and needs its own evidence and review.")
    return True


if __name__ == "__main__":
    assert_unresolved_until_g7()
    for r in crosswalk_rows():
        print(f"{r['historical_label']:<5} {r['historical_frame']:<10} "
              f"state {r['historical_match_state']:>4} LtrA {r['ltra_residue']:>4}  -> "
              f"{r['historical_RT0_RT7_correspondence_if_supported']}  "
              f"({r['status_reason']})")
