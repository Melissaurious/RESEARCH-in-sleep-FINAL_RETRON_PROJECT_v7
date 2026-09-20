---
correction_id: T-A2-CORRECTION-01
task_id: T-A2-ladder-population
task_artifact_commit: a1b76d1
governance_base: b5443e1
date: 2026-09-20
kind: INTERPRETATION_CORRECTION
authority: review-stage/BATCH_ONE_INDEPENDENT_REVIEW_VERDICT.md (ACCEPT_WITH_CHANGES)
criterion_changed: false
outputs_changed: false
reruns: none
---

# T-A2 · CORRECTION 01 — the ladder is descriptive, and the budget is a second uncontrolled axis

**This is an erratum, not a rerun.** No frozen table was modified, no criterion was edited, no
number was recomputed. Every value below is read from a named cell.

The independent review returned **ACCEPT_WITH_CHANGES**: the common-population ladder is
non-monotone, but the tiers still differ in alternative budget, so the task does not isolate
population composition as the cause. This document makes that correction.

---

## 1 · What the task measured

Four counterfactual tiers C1–C4, first on their own full tier populations and then on the
**423 components present in all four tiers** (`A2_common_population_ladder.tsv`, `n_components`
= 423 on every `common_population` row; tier-presence histogram in `RUN_LOG.txt`).

| population | weighting | C1 | C2 | C3 | C4 | monotone decreasing |
|---|---|---|---|---|---|---|
| full tier | component-level | 0.01766406084396467 | 0.015434391826923077 | 0.00397384715750233 | 0.0016829844789356984 | **True** |
| full tier | pair-weighted | 0.009792635991687233 | 0.00783581353745884 | −0.00020632533471314922 | 0.0024728971767285684 | **False** |
| common 423 | component-level | 0.017451881796690306 | 0.015308650118203312 | 0.0007958345153664303 | 0.0015582978723404255 | **False** |
| common 423 | pair-weighted | 0.009574114732854865 | 0.0077163775847808105 | −0.00038708405479815575 | 0.002462530145744534 | **False** |

All sixteen cells are in `A2_common_population_ladder.tsv`, columns `mean_component_level` and
`mean_pair_weighted`, with the monotonicity flags in `ladder_monotone_decreasing_component_level`
and `ladder_monotone_decreasing_pair_weighted`.

Bootstrap stability on the common set: the component-level ladder is monotone decreasing in
**0.1673** of 10,000 replicates and the pair-weighted ladder in **0.0000**
(`A2_common_population_ladder.tsv`, `boot_frac_replicates_monotone_component_level` /
`..._pair_weighted`).

## 2 · The correction

### 2.1 · This is a descriptive result, not a mechanistic one

> **Corrected statement of record.** The published monotone decay is **not reproduced** once the
> population is held fixed or the pairs are weighted. The shape of the published ladder is
> therefore **not a stable feature of the measurement**. That is a description of the ladder's
> instability. **It is not a demonstration that population composition causes the decay.**

**Withdrawn framing.** Any reading in which "holding the population fixed breaks the ladder,
therefore the ladder was an artefact of population composition" is withdrawn. It does not follow,
for the reason in §2.2.

### 2.2 · The alternative budget is a second axis and it was never held constant

The tiers differ in how many counterfactual alternatives each pair receives, and they differ on
the full tier populations by a landed, cited amount:

| tier | `alternatives_per_pair` | source |
|---|---|---|
| C1 | 8.0 | `embed_x2_rt_specificity_confirmation/tables/COUNTERFACTUAL_EFFECTS.tsv` |
| C2 | 8.0 | same |
| C3 | 7.983054136213699 | same |
| C4 | 7.44473377646817 | same |

**Fixing the population does not fix the budget.** T-A2 intersected the four tiers to 423 common
components; it did not equalise, match or even measure the per-pair alternative budget *inside*
that common set. The upstream bundle publishes the budget only as a **tier-level aggregate** —
`COUNTERFACTUAL_TIER_SIZING.tsv` and its four per-tier files each carry a single row — so the
common-population budget is **not available from any landed table**, and computing it requires the
pair-level export.

> **Therefore: at least two things change across the tiers of this ladder — which components are
> in it, and how many alternatives each pair is scored against. T-A2 controls the first and leaves
> the second free. No causal attribution to either is available from this task.**

The budget is recorded here as an **explicit second axis, declared uncontrolled**, not as a
controlled one. Making it genuinely controlled means a budget-matched ladder, which is a separate
producing task, registered as **T-A2b-budget-matched-ladder** in
`programme/ALL_DOWNSTREAM_TASKS.tsv`.

### 2.3 · What may and may not be said

| may be said | may not be said |
|---|---|
| the published ladder's monotone shape does not survive holding the population fixed | population composition explains the published ladder |
| the pair-weighted ladder is non-monotone on the **full** populations too, before any intersection | the pair-weighted result corrects the component-level one |
| the C3 common-population component-level mean, 0.0007958345153664303, has a bootstrap interval spanning zero, [−0.0004492768912529554, 0.001977148581560283] | C3 has no effect |
| monotonicity recurs in 0.1673 of component-level replicates | monotonicity is refuted |

### 2.4 · `SCIENTIFIC_OUTCOME` is corrected from `SUPPORTS_H1` to `DESCRIPTIVE`

The synthesis recorded `SUPPORTS_H1`. The hypothesis as stated was about the ladder's shape on a
fixed population; the measurement is a description of that shape's instability under two
simultaneous changes, only one of which was controlled. **`DESCRIPTIVE` is the honest field
value.** `TASK_STATE` is unchanged at `PASS`: the task executed correctly, and this correction
concerns what its numbers mean, not whether they are trustworthy.

## 3 · Controls, unchanged and still sound

All three blocking controls ran before the primary and are recorded in order in `RUN_LOG.txt`,
which prints `all blocking controls PASS — running primary` before any primary line. Each could
have failed: the reproduction control compares against landed cells row-for-row, and the tier
membership control against landed counts. The review confirmed this independently. **T-A2 is the
task whose control ordering is demonstrated rather than asserted**, and it is the model for the
T-LINT repair.

## 4 · What this task does not show

- Nothing about biology.
- Nothing about which of the two axes drives the published shape.
- Nothing about whether any tier's effect is different from zero after correct cluster-aware
  inference; T-A2 uses the equal-weight component bootstrap, which T-A0 measured at 0.650 coverage
  against a nominal 0.95.

## 5 · Board consequence

`T-A2-ladder-population` stays `ACCEPT_WITH_CHANGES` until this correction is independently
reviewed. `SCIENTIFIC_OUTCOME` is corrected to `DESCRIPTIVE`. No claim status changes.
