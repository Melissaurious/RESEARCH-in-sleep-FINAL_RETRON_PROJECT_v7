# embed_x2 — RT-specific conditioning confirmation · DESIGN

**Frozen before any X2 result was computed.** X1 (`8bf7207`) and the `embed_g2` split and
baselines are untouched and are neither reopened nor reinterpreted.

## 1 · Question

> Does the RT-conditioned RNA model contain reproducible information beyond retron type that is
> **specific to the observed RT–ncRNA association**, rather than merely encoding finer RT
> lineage, subtype, taxonomy, or deposition redundancy?

**Not tested**: biochemical compatibility · binding · functional interchangeability · physical
interaction · causal co-evolution · whether counterfactual pairs are biologically incompatible.
**Counterfactual RTs are controls, not biological negatives.**

## 2 · X1 findings preserved verbatim (not re-derived, not re-interpreted)

U 1.41097 · T 1.37513 · R 1.35734 · **R − T = −0.01778 [−0.02428, −0.01052]** · 65.0 % of
components favour R · near-duplicate sensitivity **−0.01809 [−0.02530, −0.00992]** · same-type
counterfactual **Δ log P = +0.013512/nt [+0.006820, +0.018813]** · **T4 R − T = −0.00776
[−0.01761, +0.00169]**.

Also preserved: the effect is **small**; type conditioning explains substantially more than the
additional specific-RT increment (T−U −0.036 vs R−T −0.018); generation showed **no** improved
marginal RNA realism under R vs T; **no per-pair biological inference is supported**. The X1
Outcome-C definition is **not** changed retrospectively. X2 is a separate, stronger gate.

## 3 · T4 audit (§3) — completed before any X2 computation

`tables/T4_AUDIT.tsv`. Tier definitions restated from `dbchar_g3`, not redefined here.
T4 = T3 + `recurrence_class ∈ {multiple_species, one_species_multiple_genomes}`, i.e. the tier
in which a repeat is a repeated **event** rather than repeated **deposition**.

| T4 inside the frozen test fold | |
|---|---|
| pairs | **991** |
| independent components | **83** — confirmed as the X1 denominator |
| **n_eff** | **9.02** |
| unique RT / ncRNA | 966 / 607 |
| RT clusters / ncRNA clusters | 125 / 253 |
| retron types | 19 |
| largest component | 229 pairs = **23.1 %** of T4 test pairs |
| median component | 2 pairs; 35 singletons |
| pairs spanning >1 physical locus | **991 / 991** |
| components with a repeated exact ncRNA | 28 / 83 |

**The 83-component denominator is confirmed.** But its **n_eff is 9.02**, which is the real
reason the X1 T4 interval was wide.

### A prospective statement that must be made now, not after the result

Cross-fitting raises T4 coverage from 83 to **247** components, but n_eff moves from **9.0 to
8.6** — it does **not** improve. n_eff is a property of the component-size distribution of the
population, not of how many folds are used. The same holds for the whole eligible population:
n_eff **12.5** across all 1,075 components, against **14.1** in the single frozen test fold.

> **Therefore: cross-fitting buys coverage and robustness of the estimate — every component
> evaluated out-of-fold exactly once, and fold-level heterogeneity made visible — but it does
> NOT buy statistical power. If the T4 question remains unresolved, that is predicted in
> advance and is an X2-D outcome for that stratum, not evidence of absence.**

## 4 · Frozen architecture and hyperparameters

Imported unchanged from `results/embed_x1_conditional_pilot/scripts/x03_model.py`. No
architecture tuning, no added capacity, no InfoNCE, no contrastive loss, no new RNA encoder, no
hyperparameter search. AdamW, lr 2e-4, 4,000-step warmup, wd 0, accum 2, batch 32, fp32,
seed 20260918, ≤40 epochs, patience-5 lowest-validation-NLL stopping rule. Frozen ESM-C
representation (32 × 960 chunks), never fine-tuned.

The conditioning-reachability check remains **mandatory** and is used in its corrected
post-training-step form established in X1 (the vendored layers zero-initialise their residual
output projections, so an init-time check is a false negative).

## 5 · Cross-fitted component-blocked confirmation — INTERNAL, not external

5 folds over the same connected components used by `embed_g2`. Whole components are assigned to
folds by a deterministic rule (largest component to the currently smallest fold; no RNG, never
optimised against R−T). For fold *k*: **test = k, validation = (k+1) mod 5, train = the other
three**. Validation exists only to run the frozen stopping rule.

Verified by assertion, not assumption: **no component, no RT cluster and no ncRNA cluster
crosses train/val/test in any fold**, and **every one of the 1,075 components is evaluated
out-of-fold exactly once**.

`CROSSFIT_MANIFEST.tsv` sha256 `65228b34f7a1fec983c34d5d639a9c7029b5123e749e4797ead15412cc4a6a12`,
frozen before training.

| fold | pairs | components | n_eff | T4 pairs | T4 components |
|---|---|---|---|---|---|
| 0 | 6,185 | 194 | 1.17 | 1,961 | 30 |
| 1 | 6,185 | 219 | 2.33 | 1,471 | 54 |
| 2 | 6,185 | 220 | 3.03 | 1,694 | 54 |
| 3 | 6,185 | 221 | 4.04 | 1,292 | 54 |
| 4 | 6,184 | 221 | 7.07 | 1,058 | 55 |

Per-fold n_eff is low because the 5,711-pair giant component lands in one fold. The endpoint is
the **pooled out-of-fold component-level estimate**; per-fold heterogeneity is reported
separately, as required.

> **This is INTERNAL cross-fitted confirmation, not external validation.** No new data exist.

## 6 · Arms

| arm | conditioning | model class | purpose |
|---|---|---|---|
| **U** | none (learned constant) | X1 `U` | RNA grammar floor |
| **T** | retron-type label (21) | X1 `T` | level-1 type organisation |
| **G** | ESM-C of the **RT cluster representative** (frozen `rt_id0.50`) | X1 `R` | **coarse RT lineage** |
| **R** | ESM-C of the **observed RT** | X1 `R` | specific RT |
| **P** | ESM-C of a **permuted** RT (training only) | X1 `R` | falsification control |

**G is not an invented grouping.** It reuses the mmseqs `--min-seq-id 0.50` clusters already
frozen in `embed_g2b`, and conditions on the *representative's ESM-C representation* rather than
a learned per-cluster embedding. That choice is forced: components never share RT clusters
across folds, so a learned cluster-embedding table would be untrained for every evaluation
cluster and degenerate. Conditioning on the representative's frozen embedding generalises,
uses the identical parameter path as R, and makes **R − G** a clean test of information finer
than the 50 %-identity homolog group. 2,455 clusters; 8.0 % of pairs are their own
representative (G ≡ R there), so R−G is reported both on all pairs and on the 28,450 where G
genuinely differs.

**P, one prespecified procedure.** Within each retron type, the RT assigned to each *training*
pair is deranged among that type's training pairs (seed 20260918; 20 of 18,554 unavoidably keep
their own RT in singleton types). **Validation and test condition on the true RT.** This asks
whether the advantage requires the observed RT↔ncRNA correspondence or merely an RT from the
right structural population. Reported separately from U/T/G/R.

## 7 · Primary endpoint

**Out-of-fold component-level R − T NLL**, aggregated as: per-sequence NLL → per-component
token-weighted mean → paired per-component difference → bootstrap over components (10,000
resamples). Reported with mean, median, 95 % CI, fraction of components favouring R, n_eff, and
between-fold heterogeneity. **Components are the inference unit; pairs are not.** Highly
deposited components cannot dominate because every component carries equal weight in the mean;
a median and a trimmed variant are reported alongside.

Repeated on the pre-existing T4 definition as a prespecified high-independence stratum, and on
the frozen near-duplicate-excluded sensitivity population.

## 8 · Outcome gate — frozen before running

**X2-A — RT-specific signal confirmed.** Requires *all* of: (1) cross-fitted component-level
R−T directionally and quantitatively consistent with X1; (2) the effect survives the
high-independence/T4 analysis with adequate support; (3) observed RT beats stringent
same-type/near-neighbour counterfactual conditioning (C3/C4); (4) the signal is not fully
explained by G; (5) P materially weakens the effect. Would justify designing the next
experiment around explicit compatibility/contrastive representation — still **not** biochemical
compatibility or co-evolution.

**X2-B — population/lineage signal only.** Full-population R−T replicates, but T4 /
high-independence evidence remains unresolved, or R does not beat close-lineage/group controls.
Reproducible RT-associated information beyond the broad type label, but **pair-specific
information not demonstrated**. Do not proceed to a compatibility model.

**X2-C — not replicated.** R−T disappears under component-blocked cross-fitting or the
controls. Preserve X1 as a pilot and stop this branch.

**X2-D — underpowered.** The stricter counterfactual/T4 tests have too few independent
components to adjudicate. **Absence of significance is not turned into absence of signal.**

## 9 · Compute

25 cells (5 arms × 5 folds), fp32, ~0.7–0.8 M trainable parameters each. Smoke-measured
~35–60 s/epoch on 18,554 training pairs; ≤40 epochs with patience 5. Estimated ~3.3 GPU-hours
total. Submitted to Ibex as array `52089885` (`--array=0-24%8`, `--time=01:30:00`,
`--mem=32G`) rather than occupying the workstation for hours. **No GPU constraint** — the model
needs no bfloat16, so any GPU is correct and the contended A100 queue is avoided. GPU name and
compute capability are recorded per cell in provenance; each cell is an independent training
run, not a shared numerical artefact.

## 10 · Stop condition

Stop after X2. No InfoNCE, dual encoders, protein–RNA contrastive learning, compatibility
classifiers, cross-modal retrieval objectives, larger generative architectures, or fine-tuning
of ESM-C/RiNALMo. No log-likelihood difference is converted into a compatible/incompatible
label, an interaction probability, or a pair score; no AUROC is reported against arbitrary
mismatched pairs.

---

## Amendment A — seed replication for optimization variance

**Declared 2026-09-19, before any X2 result was computed or inspected.**

The primary X1 effect is small (−0.018 nats/nt). The first threat to it is therefore
**optimization noise**, not biology. §6 of this design explicitly contemplates replicate seeds
for exactly this purpose, so two additional seeds (`20260919`, `20260920`) are run for the
three arms entering the primary contrasts — **T, G and R** — across all 5 folds (30 cells).

Binding conditions, unchanged from §6:

- replicate seeds estimate **optimization variance only** and **do not increase the biological
  sample size**;
- predictions are **averaged within component** before any inference;
- the primary endpoint remains the seed-`20260918` cross-fit, with the replicates reported as a
  stability check beside it, not substituted for it;
- U and P are not replicated: U is a floor and P is a falsification control, and neither enters
  the primary contrast.

Runs that do not pass `--seed` reproduce the original cross-fit exactly, so the primary result
is unaffected by this amendment.

**Placement.** The 30 replicate cells run on Ibex (array, no GPU constraint, fp32) while the
25 primary cells run locally on the two idle RTX 4090s. This is parallel use of both resources,
not a migration of the primary run.
