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
review_01: Codex, fresh thread 01a0bc96, read-only, 2026-09-20 — ACCEPT_WITH_CHANGES
review_01_changes_applied: all 7
---

> **Independent re-review applied.** A fresh read-only Codex thread (`01a0bc96`) reviewed this
> correction and returned **ACCEPT_WITH_CHANGES** with seven required changes. All seven are
> applied below and each is marked. The reviewer verified every substantive number against the
> landed cells and found no value wrong; the changes concern one mis-attributed source, one
> undisclosed diagnostic row, and five wordings that overstated in one direction or the other.

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

⚠️ **"All four" is agreement, not corroboration, and one of the four is itself uncalibrated.** The
four are alternative analyses of the same 1,075 components, not four independent confirmations, so
their agreement carries much less weight than four independent measurements would. And
`cr1_sandwich_t` **failed its own null-fixture control** — coverage 0.898 against the declared band
[0.90, 0.99] (`A0_control_checks.tsv`, `C3_null_fixture[cr1_sandwich_t]`, `state = FAIL`,
non-blocking and reported). It is retained as a diagnostic and should not be counted as
independent support.

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

2. **Homolog-group identity is not in the component export at all.** Read directly from the export's
   own header, `X2_COMPONENT_LEVEL_EXPORT.tsv` column 7 is `n_rt_homolog_groups` — a **count** — and
   no column carries a group identifier. Identity had to be taken from `CROSSFIT_MANIFEST.tsv`, an
   input T-A0 declared in its preregistration before execution and which the coordinator accepted.

**Therefore a lineage-level interval requires a lineage partition that is neither nested inside the
component unit nor derivable from the component export.** That partition does not exist in this
project today. Producing it is a separate producing step, registered as **T-A0b-lineage-partition**
in `programme/ALL_DOWNSTREAM_TASKS.tsv`.

### 2.3a · The one homolog-level row that does exist, and why it is not the missing test

`A0_blocked_intervals.tsv` carries a row `R - G / homolog_unit / iid_bootstrap_homolog_groups`,
`n_units` = 2455, interval [−0.004514147668024432, −0.0021076656211812543]. **It is disclosed here
so that nobody later finds it and reads it as the lineage result.** Its own `note` field says what
it is: *"DIFFERENT ESTIMAND: homolog-group-weighted component mean; diagnostic only, never used for
the criterion."*

Resampling homolog groups as **units** re-weights the estimand toward components that contain many
groups. That is a different quantity from the component-weighted contrast C-28 concerns. **It is
not a lineage-blocked interval for the C-28 estimand**, and the precise absence claim is therefore:
*no lineage-blocked interval exists for the component-weighted estimand relevant to C-28.*

⛔ **No lineage analysis is manufactured here.** The correct statement about the lineage level is
that it is *absent*, not that it is *negative* and not that it is *favourable*.

### 2.4 · "Blind" is overstated, and the direction of the miscalibration matters

The synthesis called the primary-generator designation **blind**. Corrected wording of record:

> The generator was **selected by a predeclared rule, applied before any real blocked interval was
> computed, on synthetic fixtures calibrated to the real R − G data. It is therefore temporally
> preselected, but neither blind nor independently validated.**

Temporal order is what rules out selecting on the final interval. It is **not** the only property
that matters, and the fixtures were data-adaptive in **both** moments, not only in variance: the
variance components come from the real R − G series (`A0_block_structure.tsv`,
`summary/all/icc_type_RminusG` = 0.028089327361041822, `deff_RminusG` = 2.324180538052522), and the
positive fixture's `mu_true` = −0.005507 (`A0_fixture_coverage.tsv`) **is the landed R − G point
estimate**. A fixture calibrated to the answer cannot certify the instrument against that answer.

**And the selected generator is miscalibrated in the anti-conservative direction.**
`A0_fixture_coverage.tsv` gives `pairs_cluster_bootstrap` coverage **0.915** on the positive
fixture and **0.9** on the null fixture, against the nominal 0.95 named in `A0_control_checks.tsv`
(`declared_band` = "[0.90, 0.99] vs nominal 0.95" — the nominal figure is **not** a field of the
coverage table and is cited from the control table). On the null fixture `frac_excluding_zero` =
**0.1**, twice the 0.05 a nominal 95 % interval permits.

The honest reading is **"anti-conservative or otherwise miscalibrated on these fitted fixtures"**,
not flatly "too narrow": under-coverage can also arise from bias or tail-shape error. Either way
the consequence for this task is the same and is the part most easily lost in summary — **"excludes
zero" deserves less confidence than its 95 % label suggests, not more.**

## 2.5 · Three landed cells that bear on C-28 and were not cited — added by review 02

A second independent scientific review (Codex `01a0bde9`) found three cells in the **upstream
bundle** that bear directly on the R − G result and that neither the task nor this correction had
cited. All three were verified here before being recorded. **Two weaken it. One strengthens it.**

| cell | value | reading |
|---|---|---|
| `LINEAGE_CONTROL.tsv`, `R - G / near_dup_sensitivity` | interval **[−0.006009444221056286, +0.0019628428863705427]** over 284 components | ⚠️ **spans zero.** Restricted to the near-duplicate-sensitivity population the contrast is not distinguishable from zero |
| `SEED_VARIANCE_SUMMARY.tsv`, `R - G` | `across_seed_sd` = **0.005064**, `primary_seed_diff` = **−0.005507**, range [−0.015595, −0.005507], `all_same_sign` = True | ⚠️ **training-seed variation is the size of the estimate.** The reported interval conditions on one seed and does not carry this |
| `A0_leave_one_type_out.tsv` | **no sign flip in any of the 21 rows**; maximum shift 0.00168846 | ✅ **strengthens it.** No single retron type creates the negative mean — the simplest artefact is ruled out |

> **Net effect: the type-blocked bound is weaker than §2.1 alone implies.** An interval that excludes
> zero on one seed, from a generator with a 0.100 false-exclusion rate, whose effect is the size of
> its own across-seed spread, and which spans zero on a near-duplicate-restricted population, is
> evidence of an **operational model residual**. It is not evidence of a biological exact-RT residual.

**Also corrected, in the other direction.** The earlier draft said C-28 is "unchanged" by this task.
That over-withdrew. Batch One **does** add information: the R − G mean is robust to dominant-type
resampling and to deletion of any one type. That is not claim support, and it is not nothing.

## 3 · What this task is good for, unchanged

- It shows the unclustered interval generator **fails under the fitted Gaussian random-intercept
  fixture model**: `iid_bootstrap_unclustered` covers 0.65 (positive) and 0.659 (null) against the
  nominal 0.95 (`A0_fixture_coverage.tsv`; nominal per `A0_control_checks.tsv`). ⚠️ **This is a
  simulation result under an assumed dependence model, not a measurement of real-world coverage.**
  It is a **warning about a shared method** — the same generator stands behind the landed pairing
  intervals — and **not** an adjudication of those intervals, none of which was examined here.
- It **settles the effective-sample-size confusion with a number that names its own estimator**:
  n_eff ≈ **462.528612730216** by design effect (`A0_block_structure.tsv`,
  `summary/all/n_eff_deff_RminusG`), against the bundle's `n²/n = n` value of 1075.0 and the index
  figure of 12.493453742983672, which is a Kish count over *pair* weights.
- It **shows homolog blocking is degenerate here**, which is a structural fact about the data and
  saves a later task from repeating it.

## 4 · What this task does not show

- **No lineage-general, mechanistic, causal or biological interpretation.** The earlier draft said
  "nothing about biology", which is too absolute: the task does report a sample-level R − G contrast
  measured on biological data, and its robustness to dominant-retron-type blocking. What it does
  not supply is any reading of what that contrast means.
- Nothing at the 50 %-identity lineage level, for the component-weighted estimand C-28 concerns.
- Nothing about the other intervals in the pairing bundle, which were not examined.
- No absolute baseline. The ladder of absolute baselines is a separate task (`T-A1`).

## 5 · Board consequence

`T-A0-lineage-variance` stays `ACCEPT_WITH_CHANGES` until this correction is independently
reviewed. `SCIENTIFIC_OUTCOME` stays `BOUND`, now with the bound's level stated in its name:
**type-blocked**. No claim status changes.
