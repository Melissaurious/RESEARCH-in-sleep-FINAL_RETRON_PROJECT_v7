# DECISION — Stage-2 `g7` is split into `g7a` (RT0–RT7 bridge) and `g7b` (comparators)

Date: 2026-09-18 · Track: `rt07` · Status: **binding**

## What this record does

It exercises the split that `launchers/LAUNCHER_02_rt0_rt7_definition.md` §3 already permits —

> *"A gate may be split if it does not fit one execution and review unit; it may not be
> silently widened."*

— and records the split rather than leaving it implicit.

`LAUNCHER_02` §7's `rt07_g7_structural_and_published_comparators` bundles **five separate
questions** (`results/rt07_g4b_production_mapper/docs/G7_STRUCTURE_PLAN.md` §"Questions g7 may
ask") together with a full published-comparator campaign. Only one of those questions closes the
historical RT0–RT7 nomenclature. The other four are structural and comparator work with
different inputs, different controls and a different reviewer burden.

| gate | scope | authority | status |
|---|---|---|---|
| **`g7a`** — `rt07_g7a_rt0_rt7_bridge` | the historical RT0–RT7 crosswalk: question 5 of the g7 plan | **`launchers/LAUNCHER_03_rt0_rt7_closure.md`** | **LANDED 2026-09-18** |
| **`g7b`** — `rt07_g7b_structural_and_published_comparators` | questions 1–4 of the g7 plan, plus Toro 2014, Mestre 2020, myRT, Toro 2026, SPIRE and prior project conventions | `LAUNCHER_02` §7, unchanged | **NOT STARTED** |

`LAUNCHER_02`'s `g7` row, its stop condition and its `C7 primary` weighting all pass to `g7b`.
`g7a` settles `C3 primary`, `C9 supporting`, `C7 supporting`.

## What is NOT changed

* `LAUNCHER_02` is **not rewritten**. It remains planning authority for the `rt07` track.
* No gate ordering changes: `g1`–`g4` before `g5`; `g6` and `g7` follow `g5`.
* `g7a` does **not** depend on `g6`, and `g6` does **not** depend on `g7a` — `g6` can operate
  entirely in frozen `state_id` space and does not require RT0–RT7 labels to be valid. The
  independence is preserved deliberately: `g7a` was executed and frozen **before** `g6` ran, and
  read no `g6` output.
* The evidence hierarchy of `LAUNCHER_02` §5d is unchanged. Comparators still may not seed the
  reconstructed frame, and structure still may not manufacture the seven-way partition.

## Why `g7a` was run first

Three reasons, in order:

1. **It is the only gate that can close the track.** `LAUNCHER_02`'s success criterion turns on
   the historical framework being traced and operationalised; the remaining comparator work
   enriches the picture but cannot resolve a label.
2. **It is small and bounded.** The missing link was a single composition step, and every other
   leg was already landed. It cost well under the 30 CPU-minute budget.
3. **It unblocks `g6` cleanly.** With `g7a` frozen, `g6` may quote the crosswalk without any risk
   that the crosswalk was tuned to make `g6` come out well — the anti-circularity rule that
   `LAUNCHER_03` §4 states as a hard input exclusion and `verify.sh` check NC-4 enforces
   mechanically.

## Consequence for `g7b`

`g7b` inherits one correction from `g7a`, recorded in
`docs/decisions/2026-09-18_stage2_g7a_rt0_rt7_closure.md` §C: the g7 plan's identification of
`6AR1` as *"the group II intron RT structure and the natural first crosswalk target"* is
accurate about family but wrong about protein. `6AR1` is GsI-IIC RT from *Geobacillus
stearothermophilus*; **`5G2X` is LtrA itself**. `g7b` should treat `5G2X` as the primary LtrA
structural comparator and `6AR1` as a secondary, tagged, different-protein one.

`g7b` also inherits, untouched: the independence-measurement requirement for all 25 local
structures, the `foldseek` pinning requirement, the tag-offset rule, the prohibition on
inheriting `reference_boundaries.*`, and the `DO-NOT-USE` state of the non-LTR R2 structure.

Supersede this record by a new record, never by rewriting it.
