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
review_01: Codex, fresh thread 01a0bc97, read-only, 2026-09-20 — ACCEPT_WITH_CHANGES
review_01_changes_applied: all 7
---

> **Independent re-review applied.** A fresh read-only Codex thread (`01a0bc97`) reviewed this
> correction and returned **ACCEPT_WITH_CHANGES** with seven required changes, all applied.
>
> **One of them was a factual error in the first draft of this document, and it mattered.** The
> draft said the common-population alternative budget "is not available from any landed table".
> **That is false.** `X2_PAIR_LEVEL_EFFECTS.tsv.gz` is a landed, hash-manifested table in the same
> bundle and carries `n_alternatives_C1…C4` per pair. The budget on the common 423 components is
> therefore derivable, the reviewer derived it, and the coordinating session **re-derived it
> independently** before accepting it (§2.2). The correction is stronger for it: the second axis is
> now **measured** on the common set rather than argued from the full-tier aggregates.

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

On the **full tier populations** the budget is a landed cell:

| tier | `alternatives_per_pair` | source |
|---|---|---|
| C1 | 8.0 | `embed_x2_rt_specificity_confirmation/tables/COUNTERFACTUAL_EFFECTS.tsv` |
| C2 | 8.0 | same |
| C3 | 7.983054136213699 | same |
| C4 | 7.44473377646817 | same |

**On the common 423 components it is also derivable, and it is still unequal.** The bundle's
`X2_PAIR_LEVEL_EFFECTS.tsv.gz` — landed and listed in the bundle's `HASHES.sha256` — carries
`n_alternatives_C1…C4` per pair. Joining it to the 423 components where
`A2_tier_membership.tsv / in_common_population = 1` gives:

| tier | eligible common-set pairs | alternatives total | common-set alternatives/pair |
|---|---|---|---|
| C1 | 30,096 | 240,768 | **8.0** |
| C2 | 29,016 | 232,128 | **8.0** |
| C3 | 30,147 | 240,975 | **7.9933326699174** |
| C4 | 29,092 | 217,034 | **7.46026399010037** |

The four pair counts independently equal `A2_common_population_ladder.tsv / n_pairs_in_tier`,
which is what confirms the join. **Derived twice**: by the independent reviewer, and re-derived
from scratch by the coordinating session before acceptance.

**T-A2 did not read that file, and that was correct for T-A2** — it is a pair-level export, and
pair counts overstate sample size by three orders of magnitude. "Not an admissible inference input
for this task" is, however, a different statement from "not available from any landed table", and
the first draft of this document confused the two.

### 2.2a · Three things change across the tiers, not two

| axis | full-tier ladder | **common-population ladder** |
|---|---|---|
| component membership | varies (1019 / 832 / 1073 / 451) | **fixed at 423** |
| eligible-pair membership and count | varies | **still varies**: 30,096 / 29,016 / 30,147 / 29,092 |
| alternative budget per pair | varies | **still varies**: 8.0 / 8.0 / 7.9933 / 7.4603 |

> **T-A2 fixes the component population. It does not fix the eligible-pair set, and it does not fix
> the alternative budget. Two of the three axes remain free, so no causal attribution to any of
> them is available from this task.**

Both remaining axes are recorded here as **explicit, declared-uncontrolled** axes. Making them
controlled is a separate producing task, **T-A2b-budget-matched-ladder**, registered in
`programme/ALL_DOWNSTREAM_TASKS.tsv`. ⚠️ **Matching the mean budget would not by itself isolate
the mechanism**: alternative *identity* and the eligible-pair set would still need explicit
treatment, and that is part of T-A2b's design problem rather than a detail of it.

### 2.3 · What may and may not be said

| may be said | may not be said |
|---|---|
| the published ladder's monotone shape does not survive holding the **component** population fixed | population composition explains the published ladder |
| the pair-weighted ladder is non-monotone on the **full** populations too, before any intersection | the pair-weighted result corrects the component-level one |
| the C3 common-population component-level mean, 0.0007958345153664303, has a bootstrap interval spanning zero, [−0.0004492768912529554, 0.001977148581560283] | C3 has no effect |
| the **observed** common-population ladder is non-monotone: C4 (0.0015582978723404255) exceeds C3 (0.0007958345153664303) | monotonicity has been **inferentially refuted** with calibrated uncertainty |
| monotonicity recurs in 0.1673 of component-level bootstrap replicates | that fraction is a calibrated probability |

⚠️ **"Pair-weighted" means a pair-count-weighted mean of the component-level estimates.** It is
**not** a raw mean over the landed pair-level effects; the two differ because the component values
are themselves token-weighted. It is a sensitivity row, not a superseding estimator.

### 2.4 · `SCIENTIFIC_OUTCOME` is corrected from `SUPPORTS_H1` to `DESCRIPTIVE`

The synthesis recorded `SUPPORTS_H1`. **The launcher's hypothesis was explicitly mechanistic — "the
shape is partly a population artefact"** — not merely a statement about shape. T-A2 does not
isolate that mechanism, because two of the three axes in §2.2a remain free. **`DESCRIPTIVE` is the
honest field value.**

`TASK_STATE` is unchanged at `PASS`: the task executed its frozen procedure, its controls passed
and its tables are internally consistent. **An interpretation failure is not an execution
failure**, and this correction concerns only the former.

## 3 · Controls, unchanged and still sound

All three blocking controls ran before the primary. **The ordering is verified in the script, not
only in the log**: `a2_ladder_population.py` evaluates the controls at lines 88–142, writes a
failure log and exits at 144–148 if any of `ok_a`, `ok_b`, `ok_c` is false, prints
`all blocking controls PASS — running primary` only after that branch at line 150, and begins the
common-set primary at line 152. The pass line therefore **cannot** be printed independently of the
three control booleans. Confirmed by the independent reviewer against the source.

One qualification, so the word "exact" is not overclaimed: the reproduction control compares means
rounded to six decimals and fractions to four; only the pair totals are compared exactly.
"Row-for-row" is accurate; "exact reproduction" would not be.

**T-A2 is the task whose control ordering is demonstrated rather than asserted**, and it is the
model the T-LINT2 repair was built from.

## 4 · What this task does not show

- Nothing about biology.
- Nothing about which of the three axes in §2.2a drives the published shape.
- **Nothing about whether any tier's effect differs from zero.** T-A2 uses the same unclustered,
  equal-weight component resampling algorithm that T-A0 measured at **0.65** coverage on its
  positive fixture and **0.659** on its null fixture, against a nominal 0.95.
  ⚠️ **Those two numbers are not T-A2's coverage.** They come from a synthetic R − G fixture with
  1,075 components, R − G variance parameters and the dominant-retron-type partition. T-A2 uses 423
  components, four different outcomes, a paired four-tier bootstrap and a different weighted
  estimator on its sensitivity rows; **its own coverage was never measured.** What follows is only
  that T-A2 performed no calibrated cluster-aware inference, so it establishes no tier's difference
  from zero — **not** that a correct analysis would find zero inside every interval.

## 5 · Board consequence

`T-A2-ladder-population` stays `ACCEPT_WITH_CHANGES` until this correction is independently
reviewed. `SCIENTIFIC_OUTCOME` is corrected to `DESCRIPTIVE`. No claim status changes.
