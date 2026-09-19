# embed_x2 — DECISION

Adjudicated against the outcome gate frozen in `DESIGN.md` §8 **before** any X2 result was
computed. The gate is applied as written. Where the literal criterion and the quantitative
picture pull apart, both are stated rather than the gate being rewritten.

## Verdict: **X2-A, with three qualifications that bound what may be built on it**

### The five X2-A criteria, applied as frozen

| # | criterion | evidence | met |
|---|---|---|---|
| 1 | cross-fitted component-level R − T directionally and quantitatively consistent with X1 | −0.02470 [−0.02907, −0.02037] vs X1 −0.01778; 64.9 % vs 65.0 % components | **yes** |
| 2 | survives the high-independence / T4 analysis with adequate support | T4 −0.02594 [−0.03508, −0.01731], 247 components | **yes** |
| 3 | observed RT beats stringent same-type / near-neighbour counterfactuals (C3/C4) | C3 +0.00397 [+0.00202, +0.00586]; C4 +0.00168 [+0.00101, +0.00251] | **yes, marginally** |
| 4 | the signal is not fully explained by G | R − G < 0 with CI excluding zero on all three seeds | **yes, directionally only** |
| 5 | P materially weakens the effect | R − P = −0.01880 vs R − T = −0.02470; P retains ~24 % | **yes** |

All five are met on their literal terms, so the frozen gate returns **X2-A**. The X2-B
conditions are specifically *not* met: T4 did not remain unresolved, and R does *not* fail to
beat the close-lineage controls.

### Why the verdict is qualified rather than clean

**Q1 — the counterfactual effect decays ~10-fold as the control tightens.**
C1 +0.0177 → C2 +0.0154 → C3 +0.0040 → C4 +0.0017. At C3, only **52.5 % of pairs** favour the
observed RT. The component-level interval excludes zero, but a near-coin-flip at pair level
means the model does not cleanly separate the observed RT from its nearest sequence
neighbours. Criterion 3 is satisfied statistically, not substantively.

**Q2 — the specific-RT increment beyond homolog group is small and seed-unstable.**
G − T = −0.019 of the total R − T = −0.025, so the 50 %-identity homolog group already
explains most of the advantage over the type label. Across three seeds R − G ranges −0.0055
to −0.0156 (sd 0.0051 against a primary estimate of 0.0055). The sign is stable; **the
magnitude is not determined by this experiment.**

**Q3 — generalisation degrades with distance from training RTs.**
Stratified by nearest-training-RT cosine, R − T runs −0.0058 (CI spans zero) → −0.0232 →
−0.0230 → −0.0319. The least-similar quartile is not adjudicated in favour of R. R − G is
flat across the same quartiles, which localises the gradient to the **T** arm rather than to
relatedness leaking into R — but the limit on extrapolation to unlike RT lineages stands.

**Not a qualification, but recorded:** the permutation control is not flat (P − T = −0.0059),
so a model trained on within-type-deranged RTs still beats the type label. Most, but not all,
of the advantage requires the observed correspondence.

## What this authorises

Per the frozen wording of X2-A, this result **would justify designing** the next experiment
around an explicit compatibility / contrastive representation. It is **still not** evidence of
biochemical compatibility, binding, functional interchangeability, or causal co-evolution.

## What this does NOT authorise, and what is not being started

Per `DESIGN.md` §10 the stop condition is unchanged and **is being honoured**. Nothing below
has been started, and none of it may be started on the strength of this result alone:

- InfoNCE, symmetric cosine contrastive loss, dual encoders, protein–RNA contrastive learning
- compatibility classifiers, cross-modal retrieval objectives
- larger generative architectures, or fine-tuning of ESM-C / RiNALMo
- converting any log-likelihood difference into a compatible/incompatible label, an
  interaction probability, or a pair score
- any AUROC against arbitrary mismatched pairs

**Design constraints any such follow-up must inherit.** Q1–Q3 are not incidental; they define
what the next experiment would have to survive to mean anything:
1. it must be evaluated against **C3/C4-strength** controls, not same-type controls, since
   same-type contrasts are ~10× easier and would inflate any headline number;
2. it must report the **nearest-training-similarity stratum** as a primary axis, because the
   effect is not currently demonstrated in the least-similar quartile;
3. it must **replicate across seeds** before any magnitude is quoted, given Q2;
4. it must keep the **component** as the inference unit and carry a permutation control.

## Stop

Per the X2 specification §16 and `DESIGN.md` §10: **work stops here and returns for operator
review.** No further modelling has been initiated.

## Provenance notes

- The first local cross-fit was launched twice and every cell was trained by two concurrent
  processes sharing one checkpoint path. Those outputs were **quarantined and not used**; the
  full 25-cell cross-fit was re-run once from the frozen scripts. See `EXECUTION_NOTES.md`.
- The seed replicates ran as a single Ibex array (`52095027`, 30/30 COMPLETED) and were
  unaffected.
- X1 (`8bf7207`) and the `embed_g2b` frozen split are untouched. The X1 Outcome-C definition
  is **not** revised retrospectively; X2 was a separate, stronger gate.
