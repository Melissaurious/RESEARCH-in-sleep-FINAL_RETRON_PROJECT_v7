# embed_x2 — counterfactual conditioning rules

**Frozen before any counterfactual result was computed.** Evaluation only: no counterfactual
RT is ever used as a training label, and none is a biological negative.

## Terminology (binding)

A **counterfactual conditioning control** is an alternative RT representation substituted for
the observed one at evaluation time, to ask how much of the model's likelihood depends on
*which* RT it was given. It is **not** a negative pair, **not** an incompatible pair, and
**not** evidence that the alternative RT could not function with that ncRNA. A combination
absent from the corpus is a **non-observed pairing**.

## Common admissibility rule (all tiers)

For an observed pair (RT_A → ncRNA_A), an alternative RT_B is admissible only if:

1. RT_B ≠ RT_A;
2. RT_B is **not** observed with ncRNA_A anywhere in the full 30,924-pair table;
3. RT_B lies in the **same cross-fit fold** as the query, so the evaluating model has never
   seen it in training either.

Condition 3 matters: drawing an alternative from a training fold would compare a
never-seen RT against a seen one and confound novelty with specificity.

## Quantity reported

For each tier, per pair:

> Δ log P per nt = NLL(ncRNA_A | alternative RT) − NLL(ncRNA_A | observed RT_A)

averaged over that pair's alternatives. **Positive favours the observed RT.** Aggregated
per-sequence → per-component (token-weighted) → bootstrap over components, 10,000 resamples.
The model used for each pair is the out-of-fold **R** model for that pair's fold.

## Tiers, in increasing stringency

### C1 — same retron type
As in X1. Alternatives drawn uniformly without replacement from admissible RTs of the same
retron type. **M = 8**; a type needs ≥ 9 distinct RTs in the fold for its pairs to be eligible.

### C2 — same type + similar RT length
C1 plus **|len(RT_B) − len(RT_A)| / len(RT_A) ≤ 0.10**. Removes the trivial possibility that
the model is reacting to gross length or truncation differences rather than sequence identity.
M = 8; pairs with fewer than 8 admissible alternatives are reported ineligible, not back-filled
from an easier tier.

### C3 — same type + nearest RT embedding neighbourhood
C1 plus: alternatives are the **8 nearest admissible RTs by cosine similarity on the frozen
pooled ESM-C representation** (`embed_g1`, 960-d, the same frozen cache the model conditions
on). This is the hardest *continuous* control — the alternatives are as similar to the observed
RT as the fold allows while still belonging to a different observed pairing.

The similarity rule is frozen here: **cosine on frozen pooled ESM-C, top-8 admissible, no
threshold, no tuning.**

### C4 — within RT homolog cluster
Alternatives restricted to the **same frozen `rt_id0.50` cluster** as RT_A — i.e. ≥ 50 %
identity over ≥ 80 % bidirectional coverage. Up to M = 8 admissible alternatives; all of them
if fewer than 8 exist. A pair is eligible only if its cluster contains ≥ 2 distinct paired RTs
**in the same fold**. This is the strongest available test of information finer than broad RT
lineage. **C4 is not forced** where no valid alternative exists; ineligible pairs are counted
and reported.

## Reported per tier

eligible pair count · independent-component count · alternatives per pair · observed-minus-
counterfactual Δ log P per nt · component-level 95 % CI · proportion of pairs favouring the
observed RT · proportion of components favouring the observed RT.

A tier whose eligible set spans **fewer than 30 independent components** is reported
`UNDETERMINED` rather than as a null, consistent with the X2-D outcome class.

## What a positive Δ log P does and does not mean

It means the model's likelihood for this ncRNA is higher when conditioned on the RT actually
observed with it than on a comparable alternative. It does **not** mean the alternative RT is
incompatible, that the observed pair binds, or that the difference reflects co-evolution.
