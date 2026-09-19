# THESIS_RESULT_STATUS — living status board

**Last updated:** 2026-09-19 · **X2 has LANDED and is CLOSED** (`4f8550b` result, `fdf0872`
closure). Nothing in the embedding track is pending computation.

This file is the single place that answers "can I write this sentence yet?". Every entry points
at a claim id in `CLAIM_EVIDENCE_MATRIX.tsv`. Update it whenever a bundle lands or a claim
changes status — and record the date and the commit when you do.

**The conclusion of record for X2** — which supersedes the bare gate label `X2-A`, and which the
thesis should quote rather than the label:

> Specific RT sequence information provides a reproducible improvement in prediction of the
> cognate ncRNA beyond broad retron type and beyond a coarse 50 %-identity RT homolog-group
> representation. However, most of the RT-associated predictive gain is explained at the
> homolog-lineage level, while the additional specific-RT effect is small, weak at the
> individual-pair level under close counterfactuals, and uncertain in magnitude across training
> seeds.

---

## 1 · Frozen and writable now

| claim | statement, as it may be written | key numbers | source |
|---|---|---|---|
| C-01 | Frozen RT and ncRNA representations identify the observed ncRNA partner far above chance among random candidates | MRR 0.4407 [0.4039, 0.4772] vs chance 0.0900; permutation p = 0.0005 | embed_g2 @ 2c9127b |
| C-02 | The advantage survives length and GC matching | +0.0844 [+0.0503, +0.1187] | embed_g2 @ 2c9127b |
| C-03 | Retron type is independently recoverable from each modality alone | ESM-C 0.4978, RiNALMo 0.6557, majority 0.2693 | embed_g2c @ 9154972 |
| C-04 | Shared-space organisation is type-associated rather than demonstrably pair-specific | 5.32× type enrichment; observed partner at median rank 238/2,756 | embed_g2c @ 9154972 |
| C-07 | Retron-type conditioning improves held-out ncRNA likelihood over no conditioning | T − U = −0.02337 [−0.02775, −0.01902], 76.1 % of 1,075 components | **embed_x2** |
| **C-08** | **Specific-RT conditioning improves held-out likelihood beyond retron type** | **R − T = −0.02470 [−0.02907, −0.02037], 64.9 % of 1,075 components; all 5 folds same sign; 3 seeds same sign** | **embed_x2** |
| **C-09** | The observed RT beats alternative RTs, and the advantage **decays ~10-fold** as the alternative gets closer | C1 +0.01766 → C2 +0.01543 → C3 +0.00397 → C4 +0.00168 | **embed_x2** |
| **C-10** | The advantage holds in T4, the independently recurrent tier | −0.02594 [−0.03508, −0.01731], 247 components (X1 could not resolve this) | **embed_x2** |
| C-11 | RT conditioning does **not** improve marginal generation realism over type conditioning | 3-mer JSD vs real: T 0.00256, R 0.00428, U 0.02812 | embed_x1 @ 8bf7207 |
| C-12 | Pair counts overstate independence by orders of magnitude; n_eff bounds inference | 30,924 pairs → 1,075 components → n_eff 12.5 | embed_g2a/g2b, X2_HANDOFF R2 |
| C-13 | The split must be joint over both modalities | 96.85 % / 82.28 % single-partner; max 176 / 705 — **re-derived from two frozen tables** | embed_g2b + X2 export |
| C-14 | Results are not driven by the residual near-duplicate channel | retrieval 0.4329 vs 0.4407; X2 R − T −0.02532 vs −0.02470 | embed_g2, embed_x2 |
| C-15 | A confirmatory within-type test is infeasible; the constraint is independent components | 2 of 21 types pass; test n_eff 3.7 and 4.6 | embed_g2c @ 9154972 |
| C-16 | R − T replicates under component-blocked cross-fitting | pooled −0.02470; folds −0.0156 … −0.0357, mean −0.02446, sd 0.00921 | **embed_x2** |
| **C-25** | **Most of the RT-associated gain is lineage-level** | G − T = −0.01919 of the total −0.02470 (~78 %) | **embed_x2** |
| C-27 | The effect is not an artefact of repeated deposition | 28 of 36 strata wholly below zero; `multiple_species` −0.02507 (364 comps) | **embed_x2** |
| C-28 | Component- and pair-weighted aggregates differ, and differ in **sign** at C3 | +0.003974 vs −0.000205 | **embed_x2** |
| C-23 | A prior in-lab model performed family recognition, not partner recognition | 78 % of the LOFO gap from family identity; InfoNCE ×43 enrichment, 2AFC 0.9532 → 0.9072 | historical audit @ 506cca2 |
| C-24 | Contrastive/compatibility modelling remains unauthorised and unstarted | X2-A "would justify designing" it; stop condition honoured | decision @ 9154972 + embed_x2 |

**Writable methods**: all of `METHODS_PROVENANCE.md`, including §7 (X2) which is now a landed
method rather than a pending one.

**Writable figures**: F1–F10 (`FIGURE_PLAN.md`).

## 2 · Supported, but only in a qualified form — write these with their qualifier attached

These are real, frozen results. Each is **conditionally** true and must never be quoted without
the clause that bounds it.

| claim | may be written as | the qualifier that must travel with it |
|---|---|---|
| **C-17** | The specific RT beats its own 50 %-identity homolog-group representative | **direction only.** R − G = −0.00551 [−0.00797, −0.00312] on the primary seed, but across three seeds −0.0055 / −0.0113 / −0.0156 (sd 0.0051 ≈ the point estimate). The sign is stable; **the magnitude is not determined by this experiment**. In the near-duplicate-excluded population the interval includes zero. **Never quote a single-seed magnitude.** |
| **C-18** | Most of the advantage requires the observed RT–ncRNA correspondence | **the permutation control is not flat.** P − T = −0.00590 [−0.01109, −0.00023]: a model trained on within-type-deranged RTs still beats the type label, retaining ~24 % of the effect. R − P = −0.01880. |
| **C-19** | The observed RT beats nearest-neighbour (C3) and within-homolog-cluster (C4) counterfactuals | **statistically, not substantively.** At C3 only **52.5 %** of pairs favour the observed RT (60.7 % at C4); C4 is +0.00168 nats/nt. The frozen gate itself records criterion 3 as "yes, marginally". |
| **C-26** | The effect is present across the population | **not in the least-similar quartile.** By nearest-training-RT cosine, R − T runs −0.00584 (**CI spans zero**) → −0.02317 → −0.02298 → −0.03193. Generalisation to RT lineages unlike anything in training is **not demonstrated**. |
| C-08 (scope) | R − T replicates | **internal cross-fitted confirmation, not external validation.** No new data exist; X1 and X2 share the same 30,924-pair population. |

## 3 · Exploratory only

Useful, reportable, **never confirmatory**.

- Descriptive strata T1–T3 in X1; the retrieval strata in `embed_g2` (all overlapping).
- Cross-modal similarity distributions by candidate class (F6a) and neighbourhood composition (F6c).
- Canonical-dimension structure (dim 1 canonical correlation 0.9865, type η² 0.809 / 0.724).
- The UMAP atlases — **visualisation only**; no claim rests on them.
- The component-level effect distribution (F4) as a description of heterogeneity.
- X2's 36 strata as a description of breadth; the prespecified endpoint remains the pooled
  component-level contrast.
- Seed-averaged X2 values (R − T = −0.02746) are a stability check, **not** the headline, and add
  no independent biological observations.

## 4 · Rejected, negative and null results — **kept, not buried**

| result | what it says | where |
|---|---|---|
| **Rung-3 null** (C-05) | With type-matched candidates the cross-modal retrieval probe is not distinguishable from a k-mer baseline (+0.0298 [−0.0048, +0.0633]). The pre-declared kill criterion fired and was honoured. | embed_g2 @ 2c9127b |
| **Rungs 4–6 UNDETERMINED** (C-06) | 1, 10 and 22 components: absence of sufficient measurement, not measured absence. | embed_g2 @ 2c9127b |
| **Counterfactual decay** (C-09) | The ~10-fold fall from C1 to C4 is the single most important bound on the level-2 claim: same-type contrasts are about an order of magnitude easier than within-homolog-cluster ones. | embed_x2 |
| **Pair-level discrimination near chance** (C-09, C-28) | 52.5 % of pairs at C3, and a raw pair-weighted mean that is nominally **negative** there. No per-pair biological reading is supported. | embed_x2 |
| **Lineage dominance** (C-25) | ~78 % of the gain over the type label is already captured by the 50 %-identity homolog group. "RT beats type" measures lineage, not pairing. | embed_x2 |
| **R − G seed instability** (C-17) | A factor-of-three spread across three seeds; a magnitude quoted from one seed is not a result. | embed_x2 |
| **Permutation control not flat** (C-18) | P − T = −0.0059; part of the gain needs only *a* realistic RT, not *the* right one. | embed_x2 |
| **Relatedness gradient** (C-26) | The least-similar training quartile is not adjudicated in favour of R. | embed_x2 |
| **Large-cluster strata UNDETERMINED** (C-29) | RT homolog groups > 100 members (22 comps) and ncRNA clusters > 100 (14 comps) are not adjudicated; the 21–100 ncRNA bin spans zero. | embed_x2 |
| **T4 prediction wrong** | `DESIGN.md` §3 predicted T4 might stay under-powered; it resolved. The failed prediction is retained in the record rather than quietly dropped. | embed_x2 |
| **Generation realism not improved by RT conditioning** (C-11) | R is slightly worse than T on 3-mer JSD and over-generates length. | embed_x1 |
| **Fragment bridges / strict-blocking split rejected** | Measured, priced, rejected: the best bridge costs 82 % of validation independence; RT 0.30 blocking leaves validation n_eff 1.0. | embed_g2a/g2b |
| **Prior contrastive arm degraded discrimination** (C-23) | Enrichment ×43 while the rank statistic fell (2AFC 0.9532 → 0.9072, t = −21). | historical audit |
| **Prior V4 embedding caches unusable** | Zero hash overlap; one earlier cache computed on unoriented sequence. | LAUNCHER_03 §5 |

## 5 · Future experimental validation (level 3)

Nothing here is a result, and none of it may be written as one. X2 explicitly does **not** support
biochemical compatibility, binding, functional interchangeability, orthogonality, co-evolution,
that any non-observed combination is incompatible, or any per-pair biological inference
(`X2_CLOSURE.md` §6).

| item | status | blocked by |
|---|---|---|
| Candidate low-cross-reactivity pair nomination (C-22) | **design only** — `CANDIDATE_SELECTION_DESIGN.md`, schematic F7 | an authorised model and scoring run; the X2 handoff requirements R1–R6; pair-level discrimination is near chance at C3 today |
| Functional compatibility / orthogonality (C-20) | not addressable computationally | laboratory assay or equivalent independent functional evidence |
| Turning non-observed pairings into assayed incompatible pairs (C-21) | not available | experimental RT–ncRNA swap data — also the precondition for an OpenCRISPR-style exchangeability validation |
| Within-type confirmatory test | infeasible today (C-15) | more independent within-type components; improved ncRNA recovery beyond covariance models |
| Effect in the largest homolog groups / ncRNA clusters (C-29) | UNDETERMINED | more independent components in those bins |
| Generalisation to divergent RT lineages (C-26) | not demonstrated | RTs materially less similar to training than the current Q1 (< 0.983 cosine) |
| Residue–nucleotide interpretation from the retained token caches | deferred by design | independently established msr/msd/a1/a2 and RT-domain annotations |

**Reopening triggers for the modelling track** are unchanged: materially more RT–ncRNA
associations; **more independent within-type components**; ncRNA recovery beyond covariance
models; independent functional evidence; a prospectively designed within-type split with a
declared minimum test n_eff.

---

## Update protocol

1. When a bundle lands: add a row to `RESULT_INVENTORY.tsv`, then move the affected claims
   between the sections above.
2. When a claim changes status: edit `CLAIM_EVIDENCE_MATRIX.tsv` **and** this file in the same
   commit; never change one alone.
3. Downstream work consumes `X2_COMPONENT_LEVEL_EXPORT.tsv` (inference) and
   `X2_PAIR_LEVEL_EFFECTS.tsv.gz` (joins only), under the binding requirements R1–R6 in
   `X2_HANDOFF.md`.
4. Never delete a negative result from §4 to make the narrative cleaner, and never promote a
   §2 claim by dropping its qualifier.
