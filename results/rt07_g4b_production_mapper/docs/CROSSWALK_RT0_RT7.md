# Historical RT0–RT7 — a separate crosswalk layer, not a production label

Production emits `state_id` in the frozen profile's own coordinate system. It does **not**
emit RT0–RT7. The freeze tests assert that no production column contains a historical label.

Anything that claims a historical RT label is **interpretation**. It lives in
`control/CROSSWALK_RT0_RT7.tsv`, is read through `code/rtmap/crosswalk.py`, and joins to
production on `state_id`.

## Current state: every row is `UNRESOLVED`

| historical label | prior frame | prior match state | LtrA residue | `operational_state` | correspondence |
|---|---|---|---|---|---|
| RT0 | — | — | — | `UNRESOLVED` | `UNRESOLVED` |
| RT1 | `RT17_CORE` | 42 | 49 | `UNRESOLVED` | `UNRESOLVED` |
| RT2 | `RT17_CORE` | 87 | 102 | `UNRESOLVED` | `UNRESOLVED` |
| RT3 | `RT17_CORE` | 146 | 160 | `UNRESOLVED` | `UNRESOLVED` |
| RT4 | `RT17_CORE` | 193 | 213 | `UNRESOLVED` | `UNRESOLVED` |
| RT5 | `RT17_CORE` | 229 | 308 | `UNRESOLVED` | `UNRESOLVED` |
| RT6 | `RT17_CORE` | 263 | 344 | `UNRESOLVED` | `UNRESOLVED` |
| RT7 | `RT17_CORE` | 276 | 357 | `UNRESOLVED` | `UNRESOLVED` |

## Why

The two coordinate systems are different objects, and **no measurement bridges them**:

* the **production ruler** is `GII.deriv.hmm`, LENG 471, sha256 `292495a4…`, built under
  `hhmake -M 50` in g4a;
* the **historical landmarks** RT1–RT7 are single **points** — not spans — in the prior
  frame `RT17_CORE` / `B_span17`, LENG 305, sha256 `f3ddb0b5…`
  (`results/rt07_g3_prior_method_replication/tables/g3_frame_identity.tsv`), carried onto
  LtrA P0A3U0 residue numbering by g3.

g3 measured *prior-frame match state → LtrA residue*. Nothing has measured *production state
→ LtrA residue* or *production state → prior-frame state*. Producing that bridge is new
measurement, and **g4b is packaging only**. The recipe is registered for g7 in
`G7_STRUCTURE_PLAN.md`.

`crosswalk.assert_unresolved_until_g7()` fails closed if any row is resolved without a
landed g7 measurement. It is a packaging guard: it stops a plausible-looking label from
being typed into the frozen table between now and then.

## Constraints any future resolution inherits from g3

These are carried forward, not re-litigated
(`results/rt07_g3_prior_method_replication/tables/g3_handoff_to_g4.tsv`):

* **The seven prior labels collapse onto six** independently reconstructed g2 regions; RT5
  and RT6 share one. A seven-way partition is not inheritable.
* **RT0 is `OBJECT_MISMATCH`.** There is no block named RT0 in the prior frame — the
  N-terminal interval is named RT0–RT1 and *excludes* the RT0 landmark. The defining claim
  is untestable on the available substrate, and **no RT0 occupancy may be reported**.
* **RT1 is the unstable landmark** — the only one that moves between prior frames, and it
  maps into the Blocker RT0 zone on LtrA. It is a declared uncertainty.
* The prior frame's 29 blocks include **24 placed by interpolating order** between only 4
  motif-anchored blocks.

So even a fully executed g7 bridge cannot return seven clean labels. `UNRESOLVED` is the
honest value today, and it stays the value wherever the bridge does not support one.

## Contract for g5 and g6

* Production tables carry `state_id`. Nothing renames them.
* A historical label is obtained only by an explicit `crosswalk.annotate(state_id)` call, so
  it can never arrive by accident in a production column.
* `annotate()` always returns a **list**. A production state may in principle correspond to
  several historical labels; forcing 1:1 is exactly the seven-boxes error g3 warned against.
* Even `CAT_STATE` 262 carries no historical label. Its catalytic role is established by
  motif concordance in this frame, not by inheritance from the prior framework.

The historical reconstruction remains a comparator and interpretation. It is not ground
truth for the production mapper.
