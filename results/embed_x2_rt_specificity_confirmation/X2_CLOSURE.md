# embed_x2 — CLOSURE

**Status: CLOSED.** The preregistered decision rule was applied as written and is not revised.

---

## 1 · Formal frozen verdict

**X2-A.** All five criteria frozen in `DESIGN.md` §8 were met on their literal terms, and the
X2-B conditions were specifically not met (T4 did not remain unresolved; R did not fail to
beat the close-lineage controls).

The gate is **not** retrospectively changed to X2-B. It did its job: it was fixed before any
effect estimate was inspected, and it returned A. What follows narrows the *scientific
interpretation*, which is a separate act from adjudicating the gate.

| # | criterion | evidence | met |
|---|---|---|---|
| 1 | cross-fitted R − T consistent with X1 | −0.02470 [−0.02907, −0.02037] vs X1 −0.01778; 64.9 % vs 65.0 % of components | yes |
| 2 | survives high-independence / T4 | −0.02594 [−0.03508, −0.01731], 247 components | yes |
| 3 | beats stringent C3/C4 counterfactuals | C3 +0.00397 [+0.00202, +0.00586]; C4 +0.00168 [+0.00101, +0.00251] | yes, marginally |
| 4 | not fully explained by G | R − G < 0, CI excluding zero on all three seeds | yes, directionally only |
| 5 | P materially weakens the effect | R − P = −0.01880 vs R − T = −0.02470 | yes |

## 2 · Qualified biological interpretation (binding)

> Specific RT sequence information provides a reproducible improvement in prediction of the
> cognate ncRNA beyond broad retron type and beyond a coarse 50 %-identity RT homolog-group
> representation. However, most of the RT-associated predictive gain is explained at the
> homolog-lineage level, while the additional specific-RT effect is small, weak at the
> individual-pair level under close counterfactuals, and uncertain in magnitude across
> training seeds.

This paragraph, not the label `X2-A`, is the conclusion of record.

## 3 · Positive findings

1. **The primary endpoint replicates X1 under component-blocked cross-fitting.**
   R − T = **−0.02470 [−0.02907, −0.02037]**, 64.9 % of 1,075 independent components favour
   R (X1: −0.01778, 65.0 %). No component, RT cluster or ncRNA cluster crosses a
   train/validation/test boundary in any fold.

2. **T4 resolves in the same direction.** R − T = **−0.02594 [−0.03508, −0.01731]** over 247
   components. `DESIGN.md` §3 predicted prospectively that T4 might remain underpowered,
   because cross-fitting raises T4 coverage 83 → 247 components while n_eff moves 9.0 → 8.6.
   **That prediction was wrong in the favourable direction** and is retained in the record.

3. **Stable across folds.** All five folds the same sign, each interval excluding zero;
   mean −0.02446, sd 0.00921.

4. **Robust to near-duplicates.** The frozen near-duplicate-excluded sensitivity population
   gives −0.02532 [−0.03410, −0.01682] over 284 components.

5. **Robust to optimization noise on the primary endpoint.** Three seeds: −0.02470, −0.03674,
   −0.02093; same sign, all intervals excluding zero.

6. **Broadly distributed.** 36 adjudicable strata; 28 with the whole 95 % CI below zero, 1
   above, 7 spanning zero; 86.1 % favour R. Present across taxonomy breadth and deposition
   multiplicity, including the repeated-*event* class `multiple_species`
   (−0.02507, 364 components).

## 4 · Falsification and control findings

These are the results that constrain the interpretation, and they are reported with the same
weight as the positive ones.

1. **Most of R − T is explained by G − T.** G − T = −0.01919 of the total R − T = −0.02470.
   The 50 %-identity RT homolog group already accounts for the large majority of the
   advantage over the broad type label.

2. **R − G is directionally positive but small and seed-unstable.** Primary seed −0.00551
   [−0.00797, −0.00312], 55.3 % of components. Across three seeds: −0.00551, −0.01133,
   −0.01560 — a factor-of-three spread, sd 0.00506 against a primary point estimate of
   0.00551. **The sign is stable; the magnitude is not determined by this experiment.**

3. **Counterfactual discrimination decays strongly as alternatives become more similar.**

   | tier | alternative drawn from | comps | Δ log P/nt | 95 % CI | % pairs favouring observed |
   |---|---|---|---|---|---|
   | C1 | same retron type | 1,019 | +0.01766 | [+0.01533, +0.01994] | 72.6 % |
   | C2 | + RT length within 10 % | 832 | +0.01543 | [+0.01291, +0.01786] | 70.6 % |
   | C3 | + 8 nearest ESM-C neighbours | 1,073 | +0.00397 | [+0.00202, +0.00586] | **52.5 %** |
   | C4 | within 50 %-identity RT cluster | 451 | +0.00168 | [+0.00101, +0.00251] | 60.7 % |

   A ~10-fold decay from C1 to C4.

4. **C4 remains statistically non-zero but is very small.** +0.00168 nats/nt, with an
   interval excluding zero over 451 independent components. Statistical significance here
   does not imply substantive discrimination.

5. **Pair-level discrimination approaches chance under the strongest controls.** At C3 only
   **52.5 %** of pairs favour the observed RT. The component-level mean is positive, but the
   model does not cleanly separate the observed RT from its nearest sequence neighbours on a
   per-pair basis.

   **Pair-weighted and component-weighted aggregates differ, and at C3 they differ in sign:**

   | tier | component-level mean (inference unit) | raw pair-level mean | % pairs > 0 | pair-level median |
   |---|---|---|---|---|
   | C1 | +0.017664 | +0.009894 | 72.6 % | +0.008057 |
   | C2 | +0.015434 | +0.007951 | 70.6 % | +0.006026 |
   | C3 | +0.003974 | **−0.000205** | 52.5 % | +0.000187 |
   | C4 | +0.001683 | +0.002391 | 60.7 % | +0.001841 |

   This is a weighting effect, not an inconsistency: the component-level estimate gives every
   independent component equal weight, whereas an unweighted pair mean lets the largest
   components dominate. It is reported because it sharpens the finding — at C3 the raw
   pair-level mean advantage of the observed RT is **indistinguishable from zero and nominally
   negative**, with a barely positive median (+0.000187), even though the component-level
   interval excludes zero. The component-level estimate remains the preregistered endpoint;
   the pair-level view is what forbids any per-pair biological reading.

6. **The within-type permutation arm still improves over T.** P − T = **−0.00590
   [−0.01109, −0.00023]**. A model trained on RTs deranged within retron type still beats the
   type label, by roughly a quarter of the full effect. **Some gain therefore comes from
   conditioning on a realistic RT representation independent of correct pairing.**
   R − P = −0.01880 confirms the observed correspondence supplies most, but not all, of it.

7. **Generalisation varies with training-set relatedness.** By nearest-training-RT cosine
   quartile, R − T runs −0.00584 (CI **spans zero**) → −0.02317 → −0.02298 → −0.03193. The
   least-similar quartile is not adjudicated in favour of R. Note that R − G is *flat* across
   the same quartiles (≈ −0.004 to −0.007), which localises the gradient to the **T** arm
   rather than to residual RT relatedness leaking into R.

## 5 · Limitations

1. Effect sizes are **small in absolute terms**: 0.0017–0.0177 nats/nt.
2. The specific-RT increment beyond homolog lineage is small **and its magnitude is
   seed-unstable** (§4.2).
3. The permutation control is **not flat** (§4.6).
4. Generalisation to RT lineages unlike anything in training is **not demonstrated** (§4.7).
   RT ESM-C embeddings are highly compressed — median nearest-training cosine 0.987, with
   even Q1 above 0.983 — so this is a narrow similarity range, not near-vs-far homology.
5. **INTERNAL cross-fitted confirmation, not external validation.** No new data exist; the
   same 30,924-pair population underlies X1 and X2.
6. Some strata remain **UNDETERMINED** for want of independent components, and are reported
   as such rather than as nulls: RT homolog groups > 100 members (22 components), ncRNA
   clusters > 100 members (14), and two rare recurrence classes.
7. The largest ncRNA clusters are not adjudicated: the effect is carried by small clusters
   (−0.025 at sizes 1 and 2–5) while the 21–100 bin spans zero.
8. A single model family, frozen from X1, on frozen representations. Nothing here
   characterises what a different architecture would find.

## 6 · Statements explicitly NOT supported

None of the following follows from any result in this bundle, and none may be asserted on its
basis:

- biochemical compatibility between an RT and an ncRNA
- physical interaction or binding
- functional interchangeability, or **orthogonality** between retron systems
- causal **co-evolution** of RT and ncRNA
- that any non-observed RT–ncRNA combination is **incompatible**, non-functional, or a
  biological negative
- that retron type has been proven to explain all, or none, of the observed signal
- that the model identifies the cognate RT of an ncRNA at the individual-pair level
- any per-pair biological inference whatsoever

**Terminology, binding.** A counterfactual RT is a **conditioning control**, never a negative
pair. A combination absent from the corpus is a **non-observed pairing**. Likelihood
differences are **not** converted into compatibility labels, interaction probabilities or pair
scores, and no AUROC against artificial mismatches is reported.

## 7 · Stop condition — honoured

Not started, and not authorised by this result: InfoNCE · contrastive learning · dual
encoders · compatibility classifiers · AUROC against artificial mismatches · large-scale
cross-pair ranking · larger generative architectures · fine-tuning of ESM-C or RiNALMo.

Requirements for any future pairing-specificity analysis are in `X2_HANDOFF.md`.
