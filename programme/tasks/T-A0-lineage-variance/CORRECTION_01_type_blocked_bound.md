---
correction_id: T-A0-CORRECTION-01
task_id: T-A0-lineage-variance
task_artifact_commit: c724df7
governance_base: b5443e1
date: 2026-09-20
kind: INTERPRETATION_CORRECTION
authority: review-stage/BATCH_ONE_INDEPENDENT_REVIEW_VERDICT.md (ACCEPT_WITH_CHANGES)
criterion_changed: false
outputs_changed: false
reruns: none
---

# T-A0 · CORRECTION 01 — the result is a type-blocked bound, not a lineage test

**This is an erratum, not a rerun.** No frozen table was modified, no criterion was edited, no
number was recomputed. Every value below is read from a cell in the task's landed tables on
`task/T-A0-lineage-variance` at `c724df7`, and the table and row are named for each one.

The independent review returned **ACCEPT_WITH_CHANGES** for T-A0 with one required change: the
result supports only a type-blocked bound, and no interval exists at the 50 %-identity lineage
level relevant to claim C-28. This document makes that correction and withdraws the wording that
overstated it.

---

## 1 · What the task measured

| quantity | value | source cell |
|---|---|---|
| inferential unit | component | `A0_block_structure.tsv`, `summary/all/n_components` = 1075.0 |
| blocking level actually used for the primary | dominant retron type | `A0_block_structure.tsv`, `summary/all/n_type_blocks` = 21.0 |
| primary generator | `pairs_cluster_bootstrap` | `A0_control_checks.tsv`, `C4_primary_estimator_designation` |
| R − G point estimate | −0.005506593488372089 | `A0_blocked_intervals.tsv`, `R - G / type_block / pairs_cluster_bootstrap` |
| R − G 95 % interval, type-blocked | [−0.009845703175768238, −0.0018512811925093958] | same row, `ci_lo` / `ci_hi` |
| `includes_zero` | False | same row |

All four type-block generators exclude zero for R − G. The only contrast whose type-blocked
interval includes zero is **P − T**, at [−0.015138288891128724, +0.010450378618329932]
(`A0_blocked_intervals.tsv`, `P - T / type_block / pairs_cluster_bootstrap`).

## 2 · The correction

### 2.1 · The outcome is `BOUND`, and the bound is type-blocked

> **Corrected statement of record.** Under resampling that respects the 21-block dominant-retron-type
> partition of the 1,075 components, the R − G 95 % interval excludes zero. **This is robustness to
> type-level blocking and nothing more.**

**Withdrawn wording.** `programme/BATCH_ONE_SYNTHESIS.md` §6 reads *"The review predicted it might
not survive. It did."* **That sentence is withdrawn.** It reports a test that was not performed.
Nothing in this task shows the exact-RT residual survives lineage-level blocking, because no
lineage-level interval was computed.

**Withdrawn wording.** Any phrasing in which claim C-28 "survived", "held up", or "was supported"
is withdrawn for the same reason.

### 2.2 · C-28 remains unresolved and unpromotable

The preregistered falsification criterion did not fire (`A0_control_checks.tsv`,
`criterion_evaluation`, observed `False`, "criterion fires if True"). **A criterion that does not
fire is not a claim.** C-28 stays where it was: unresolved, unpromoted, and unpromotable. Its
status is unchanged by this task and unchanged by this correction.

### 2.3 · The 50 %-identity lineage analysis was not performed, and why

Two separate facts, both from landed cells, and they are not the same fact:

1. **The 50 %-identity grouping that exists is strictly finer than the inference unit.**
   `A0_block_structure.tsv` `summary/all/n_homolog_group_blocks` = 2455.0 distinct `rt_rep`
   against 1,075 components, and `summary/all/homolog_groups_nested_in_components` = 1.0 — every
   `rt_rep` lies in exactly one component. 879 of the 1,075 components contain a single homolog
   group (`summary/all/n_components_single_homolog_group`). A partition nested *inside* the
   resampling unit cannot act as a block over it, which is why the `homolog_block` row reports
   `n_blocks` = 1075 and reproduces the unclustered interval
   [−0.007968794488372087, −0.00312316537209302] exactly.

2. **Homolog-group identity is not in the component export at all.** The export carries homolog-group
   *counts*; identity had to be taken from `CROSSFIT_MANIFEST.tsv`, an input T-A0 declared in its
   preregistration before execution and which the coordinator accepted.

**Therefore a lineage-level interval requires a lineage partition that is neither nested inside the
component unit nor derivable from the component export.** That partition does not exist in this
project today. Producing it is a separate producing step, registered as **T-A0b-lineage-partition**
in `programme/ALL_DOWNSTREAM_TASKS.tsv`.

⛔ **No lineage analysis is manufactured here.** The correct statement about the lineage level is
that it is *absent*, not that it is *negative* and not that it is *favourable*.

### 2.4 · "Blind" is overstated, and the direction of the miscalibration matters

The synthesis called the primary-generator designation **blind**. Corrected: the generator was
designated **before any real blocked interval was computed**, which is true and is the property that
matters for selection, but its fixtures were **not independent of the real data** — their variance
parameters were fitted to the real R − G series (`A0_block_structure.tsv`,
`summary/all/icc_type_RminusG` = 0.028089327361041822, `deff_RminusG` = 2.324180538052522). Call it
**pre-designated**, not blind.

**And the selected generator under-covers.** `A0_fixture_coverage.tsv` gives
`pairs_cluster_bootstrap` coverage **0.915** on the positive fixture and **0.900** on the null
fixture, against a nominal 0.95. Under-coverage means the intervals are, if anything, **too
narrow** — so "excludes zero" is a **weaker** finding than its nominal 95 % label suggests, not a
stronger one. This direction was stated in the synthesis and is restated here because it is the
part most easily lost in summary.

## 3 · What this task is good for, unchanged

- It **refutes the unclustered interval generator**: `iid_bootstrap_unclustered` covers 0.650
  (positive) and 0.659 (null) against nominal 0.95 (`A0_fixture_coverage.tsv`). That bears on every
  interval produced by the scripts behind the landed pairing results, none of which was examined.
- It **settles the effective-sample-size confusion with a number that names its own estimator**:
  n_eff ≈ **462.528612730216** by design effect (`A0_block_structure.tsv`,
  `summary/all/n_eff_deff_RminusG`), against the bundle's `n²/n = n` value of 1075.0 and the index
  figure of 12.493453742983672, which is a Kish count over *pair* weights.
- It **shows homolog blocking is degenerate here**, which is a structural fact about the data and
  saves a later task from repeating it.

## 4 · What this task does not show

- Nothing about biology.
- Nothing at the 50 %-identity lineage level.
- Nothing about the other intervals in the pairing bundle, which were not examined.
- No absolute baseline. The ladder of absolute baselines is a separate task (`T-A1`).

## 5 · Board consequence

`T-A0-lineage-variance` stays `ACCEPT_WITH_CHANGES` until this correction is independently
reviewed. `SCIENTIFIC_OUTCOME` stays `BOUND`, now with the bound's level stated in its name:
**type-blocked**. No claim status changes.
