# THESIS_RESULT_STATUS — living status board

**Last updated:** 2026-09-19 · **X2 status: RUNNING (pending). No X2 number appears anywhere in
this workbench.**

This file is the single place that answers "can I write this sentence yet?". Every entry points at
a claim id in `CLAIM_EVIDENCE_MATRIX.tsv`. Update it whenever a bundle lands, a run finishes, or a
claim changes status — and record the date and the commit when you do.

---

## 1 · Frozen and writable now

Numbers below are read from frozen bundles and may be written into the thesis as stated, with the
limitation that accompanies each one.

| claim | statement, as it may be written | key numbers | source |
|---|---|---|---|
| C-01 | Frozen RT and ncRNA representations share structure that identifies the observed ncRNA partner far above chance among random candidates | MRR 0.4407 [0.4039, 0.4772] vs chance 0.0900; permutation p = 0.0005; reverse direction 0.4738 | embed_g2 @ 2c9127b |
| C-02 | The advantage over the strongest trivial baseline survives length and GC matching | +0.0844 [+0.0503, +0.1187] | embed_g2 @ 2c9127b |
| C-03 | Retron type is independently recoverable from each modality alone | ESM-C 0.4978, RiNALMo 0.6557, majority 0.2693 | embed_g2c @ 9154972 |
| C-04 | Shared-space organisation is type-associated rather than demonstrably pair-specific | nearest neighbour is the observed partner 0.56 % of the time; median rank 238/2,756; 5.32× type enrichment | embed_g2c @ 9154972 |
| C-11 | RT conditioning does **not** improve marginal generation realism over type conditioning | 3-mer JSD vs real: T 0.00256, R 0.00428, U 0.02812 | embed_x1 @ 8bf7207 |
| C-12 | Pair counts overstate independence by more than two orders of magnitude; n_eff bounds inference | test fold 4,638 pairs → n_eff 14.1 | embed_g2a/g2b |
| C-13 | The split must be joint over both modalities | one ncRNA observed with 705 RTs; 17.72 % of ncRNAs have > 1 RT partner | embed_g0, embed_g2b |
| C-14 | Results are not driven by the residual near-duplicate channel | retrieval 0.4329 vs 0.4407; X1 R−T −0.01809 vs −0.01778 | embed_g2, embed_x1 |
| C-15 | A confirmatory within-type test is currently infeasible; the binding constraint is independent components | 2 of 21 types pass; their test n_eff 3.7 and 4.6 | embed_g2c @ 9154972 |
| C-23 | A prior in-lab protein-conditioned model performed family recognition, not partner recognition | 78 % of the LOFO gap attributed to family identity; InfoNCE arm: enrichment ×43, row 2AFC 0.9532 → 0.9072 | HISTORICAL_MODEL_ASSET_AUDIT @ 506cca2 |
| C-24 | Escalation to contrastive partner-specificity modelling is not currently justified as a confirmatory test | rung-3 difference +0.0298 [−0.0048, +0.0633] fails the pre-declared margin | decision record @ 9154972 |

**Writable methods**: all of `METHODS_PROVENANCE.md` §§1–6 and §§8–10, plus §7 as *specified,
result pending*.

**Writable figures**: F1–F7 (`FIGURE_PLAN.md`).

## 2 · Awaiting confirmation

These are real results that should be written **with the word preliminary attached**, because a
stricter test of the same question is running.

| claim | statement | why it is not final | what would settle it |
|---|---|---|---|
| C-07 | Type conditioning improves held-out ncRNA likelihood over no conditioning (T − U = −0.03585 [−0.04262, −0.02924], 80.7 % of components) | one pilot run, one seed, single fold; arm U overfits at epoch 0 | X2 cross-fitted U/T arms |
| C-08 | **Specific-RT conditioning improves likelihood beyond type** (R − T = −0.01778 [−0.02428, −0.01052], 65.0 % of components; survives near-duplicate exclusion) | single fold and seed; small effect (~1.3 % relative); not resolved in T4; does not appear in generation realism | X2 pooled out-of-fold R − T, plus arms G and P |
| C-09 | The observed RT beats same-type counterfactual RTs (Δ log P = +0.013512 [+0.006820, +0.018813], 71.0 % of pairs) | C1 is the weakest counterfactual tier; per-pair values were not frozen | X2 tiers C2 (length-matched), C3 (nearest ESM-C neighbours), C4 (same 50 %-identity cluster) |

**Sentences that must wait for X2** — do not write these in any form until the run lands and is
read against its frozen gate:

1. That the RT-specific effect **replicates** or is **reproducible** (C-16).
2. That the effect is **not explained by coarse RT lineage** (C-17) — arm G has not been read.
3. That the effect **requires the observed RT–ncRNA correspondence** (C-18) — the permutation
   control P has not been read.
4. That the observed RT beats **stringent** counterfactual conditioning (C-19) — C2/C3/C4 pending.
5. Any statement about **between-fold heterogeneity**, or about T4 being resolved either way.
6. Any escalation language ("this justifies a compatibility model", "the next experiment should
   be contrastive") — that is gated on outcome X2-A, which has five conditions.
7. Any restatement of the X1 Outcome-C definition: it is **not** changed retrospectively by X2.

## 3 · Exploratory only

Useful, reportable, **never confirmatory**.

- Descriptive strata T1–T3 in X1 (all intervals overlap; no stratum distinguishable).
- The retrieval strata in `embed_g2` (T1 0.4588 · T2 0.4912 · T3 0.5263 · T4 0.4732 — overlapping).
- Cross-modal similarity distributions by candidate class (F6a) and the neighbourhood composition
  (F6c).
- Canonical-dimension structure (dim 1 canonical correlation 0.9865, type η² 0.809 / 0.724) — read
  as mechanism, not as evidence for a claim.
- The UMAP atlases — **visualisation only**; no claim rests on them, and apparent islands are not
  evidence of discrete biological classes.
- The component-level effect distribution (F4b, F4c) as a description of heterogeneity.

## 4 · Rejected, negative and null results — **kept, not buried**

These belong in the thesis. Several are among its most useful contributions.

| result | what it says | where |
|---|---|---|
| **Rung-3 null** (C-05) | With type-matched candidates the cross-modal probe is not distinguishable from a k-mer baseline: retrieval does not establish partner specificity. The pre-declared kill criterion fired and was honoured. | embed_g2 @ 2c9127b |
| **Rungs 4–6 UNDETERMINED** (C-06) | 1, 10 and 22 components: absence of sufficient measurement, not measured absence. | embed_g2 @ 2c9127b |
| **T4 unresolved in X1** (C-10) | In the independently recurrent tier the R−T interval includes zero (−0.00776 [−0.01761, +0.00169]); this is the single most important caveat on the X1 outcome. | embed_x1 @ 8bf7207 |
| **Generation realism not improved by RT conditioning** (C-11) | The likelihood advantage does not translate into a better marginal sequence distribution; R is slightly worse than T on 3-mer JSD and over-generates length. | embed_x1 @ 8bf7207 |
| **Fragment bridges rejected** | The best structural remedy closes the RT leakage channel (3 → 0) but only reduces ncRNA 263 → 54, at the cost of 82 % of validation independence. Measured, priced, rejected. | embed_g2a/g2b |
| **Strict-blocking split rejected** | RT 0.30 blocks leakage superbly and is unusable (validation n_eff 1.0). Blocking and power are in direct opposition in this universe. | embed_g2a @ fd5efc9 |
| **Escalation not authorised** (C-24) | Status is `NOT YET JUSTIFIED AS A CONFIRMATORY PARTNER-SPECIFIC TEST`, not `METHOD REJECTED`. The constraint is the evaluation, not the architecture. | decision @ 9154972 |
| **Prior contrastive arm degraded discrimination** (C-23) | It raised the metric it optimised 43-fold while the rank statistic fell (2AFC 0.9532 → 0.9072, t = −21). A project reporting enrichment alone would have called it a success. | historical audit @ 506cca2 |
| **Prior V4 embedding caches unusable** | Zero hash overlap with this universe; one earlier cache was computed on unoriented sequence. Absence is loud; wrongness is quiet. | LAUNCHER_03 §5, embed_g0 |

## 5 · Future experimental validation (level 3)

Nothing in this category is a result, and none of it may be written as one.

| item | status | blocked by |
|---|---|---|
| Candidate low-cross-reactivity RT–ncRNA pair nomination (C-22) | **design only** — `CANDIDATE_SELECTION_DESIGN.md`, schematic F7 | an authorised model; an experimentally tractable named set; the prerequisites in that document §5 |
| Functional compatibility / orthogonality (C-20) | not addressable computationally | laboratory assay or equivalent independent functional evidence |
| Turning non-observed pairings into assayed incompatible pairs (C-21) | not available | experimental data; this is also **reopening trigger 4** for the modelling track |
| Within-type confirmatory test | infeasible today (C-15) | more independent within-type components; improved ncRNA recovery beyond covariance models |
| Residue–nucleotide interpretation from the retained token caches | deferred by design | independently established msr/msd/a1/a2 and RT-domain annotations |
| msr/msd two-segment modelling (the OpenCRISPR sentinel design) | deferred | msr/msd boundary annotations |

**Reopening triggers for the modelling track** (any one is a reason to revisit; 2 and 5 would
actually change the answer): (1) materially more RT–ncRNA associations; (2) **more independent
within-type components**; (3) ncRNA recovery beyond covariance models — re-run
`a07_within_type_feasibility.py` whenever it improves; (4) independent functional evidence; (5) a
prospectively designed within-type split with a declared minimum test n_eff.

---

## Update protocol

1. When a bundle lands: add a row to `RESULT_INVENTORY.tsv` (id, path, commit, key quantities,
   status), then move the affected claims between the sections above.
2. When a claim changes status: edit `CLAIM_EVIDENCE_MATRIX.tsv` **and** this file in the same
   commit; never change one alone.
3. When X2 lands: read it against the frozen gate in `DESIGN.md` §8 **before** writing prose,
   record the outcome class (A/B/C/D), then release the sentences listed in §2 that the outcome
   actually licenses — and only those.
4. Never delete a negative result from §4 to make the narrative cleaner.
