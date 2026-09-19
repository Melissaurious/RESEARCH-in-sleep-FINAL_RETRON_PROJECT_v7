# THESIS SECTION OUTLINE — RT–ncRNA representation and conditional modelling

**Chapter question**

> Do naturally associated retron RTs and ncRNAs contain partner-specific sequence information
> beyond broad retron lineage/type, and can that information eventually be used to prioritize
> candidate low-cross-reactivity RT–ncRNA pairs for experimental testing?

The chapter is organised so that the reader meets the three claim levels **before** any number,
and so that each result is delivered against the level it can actually bear on.

| level | statement | status at time of writing |
|---|---|---|
| **1 · broad association** | RT and ncRNA sequence properties track retron type / lineage | **established** in this population |
| **2 · RT-specific statistical association** | knowing the individual RT improves prediction/scoring of its observed ncRNA beyond broad type | **preliminary** (X1); stricter test (X2) **pending** |
| **3 · functional compatibility / orthogonality** | an RT works with one ncRNA and not another | **not addressable** without experiment |

Levels 1 and 2 are computational questions with the present data. Level 3 is an experimental
question and is never inferred from levels 1–2, nor from natural pairing.

---

## 1 · Introduction and framing  *(writable now)*

1.1 Retrons as tripartite elements; the RT–ncRNA functional interdependence that motivates the
question.
1.2 What "partner specificity" would mean, and the three-level decomposition above. Define the
vocabulary once and use it everywhere: *observed pair*, *candidate*, *mismatched candidate*,
*non-observed pairing*, *counterfactual conditioning control*. State that *negative pair* and
*incompatible pair* are not used.
1.3 Why language-model representations are a reasonable instrument, and what they cannot see.
1.4 The methodological precedent (protein-conditioned RNA generation, OpenCRISPR) and why this
work borrows its **architecture**, not its **evaluation** (→ §5, `OPENCRISPR_COMPARISON.md`).
1.5 Chapter roadmap and the pre-registration discipline (launcher, kill criteria, "test opened
once").

*Figures: none. Sources: LAUNCHER_03 @ 89d06b1; research contract claims C2, C6.*

## 2 · Dataset construction and the leakage-aware split  *(writable now)*

2.1 The observed-pair universe (PAIR-ELIG: 30,924 pairs / 29,192 RTs / 16,458 ncRNAs / 21 types)
and the nested tiers T1–T4, with T4 defined as the *repeated-event* tier.
2.2 ncRNA sequence reconstruction, orientation and the 16,458/16,458 hash round-trip — including
the cautionary history (21.4 GB of embeddings previously computed on unoriented sequence).
2.3 Multiplicity as a design constraint: one ncRNA observed with 705 RTs; why in-batch negatives
are biologically wrong here.
2.4 Why raw pair counts are the wrong sample size: relatedness components and n_eff.
2.5 Threshold selection blind to any compatibility result; the leakage instrument that is
independent of the clustering; **blocking versus power as an unavoidable trade-off**.
2.6 The frozen split, its determinism, and its verification.
2.7 Measured leakage and the near-duplicate sensitivity population; fragment bridges priced and
rejected.

**This section carries one of the chapter's genuine methodological contributions** — that in this
universe strict relatedness blocking and statistical power are in direct opposition, and that the
honest response is to declare the trade-off, freeze a point on it, and report n_eff everywhere.

*Figure: **F1**. Sources: embed_g0 @ fe6e1a3; embed_g2a @ fd5efc9; embed_g2b @ 15e00b8.*

## 3 · Frozen representations  *(writable now)*

3.1 ESM-C 300M and RiNALMo giga-v1; why frozen encoders and why pooled representations first.
3.2 Production, verification and provenance; A100/bf16 as a correctness requirement.
3.3 Token-level arrays: produced, retained, deliberately unanalysed — and the annotation
prerequisites that would change that.

*Figure: none (table only). Source: embed_g1 @ 5dbd368.*

## 4 · Level 1 — broad RT–ncRNA correspondence  *(writable now)*

4.1 The retrieval task, the candidate ladder, false-candidate exclusion, and the trivial baselines
that ran first.
4.2 Result: strong retrieval against random and composition-matched candidates; permutation
failure control; reverse direction.
4.3 Shared-space organisation: cross-modal similarity by candidate class; neighbourhood
composition (5.32× type enrichment, observed partner at median rank 238/2,756).
4.4 Canonical dimensions and modality-specific type encoding (type recoverable from each modality
alone: 0.498 / 0.656 vs 0.269 majority) — **the mechanism that makes level 2 hard to test**.
4.5 Interpretation: level 1 is supported; nothing here is partner-specific.

*Figures: **F6** (a–c). Sources: embed_g2 @ 2c9127b; embed_g2c @ 9154972.*

## 5 · The rung-3 boundary — where retrieval stops being informative  *(writable now)*

5.1 The decisive comparison: with type-matched candidates, the cross-modal probe is **not
distinguishable** from a k-mer baseline (+0.0298, 95 % CI [−0.0048, +0.0633]).
5.2 Why this is *not* proof of equivalence, and why rungs 4–6 are `UNDETERMINED` rather than null.
5.3 The pre-registered escalation rule and the decision not to escalate to contrastive modelling;
the in-lab precedent in which an InfoNCE arm inflated its own metric 43× while degrading the rank
statistic.
5.4 Within-type feasibility audit: 2 of 21 types pass the population criteria, and even those have
test-fold n_eff 3.7 and 4.6. **The binding constraint is independent components, not capacity.**

*Figures: **F6b** (UNDETERMINED rungs), optional feasibility table. Sources: embed_g2 @ 2c9127b;
embed_g2c @ 9154972; decision record @ 9154972.*

## 6 · Level 2 — conditional RNA modelling (X1)  *(writable now, labelled PRELIMINARY)*

6.1 Why a conditional generative formulation asks a different question than retrieval, and why the
primary contrast is **R vs T** rather than R vs U.
6.2 Model, arms, the shared byte-identical decoder, and the conditioning representation.
6.3 The compute gate, including the zero-initialised residual projections that make an init-time
conditioning check a false negative.
6.4 Results: U/T/R held-out NLL; T − U; **R − T = −0.01778 [−0.02428, −0.01052], 65.0 % of
components**; near-duplicate sensitivity.
6.5 The component-level effect distribution: a small shift of a wide distribution, not a uniform
gain.
6.6 Same-type counterfactual conditioning: **Δ log P = +0.013512 [+0.006820, +0.018813]**, 71.0 %
of pairs.
6.7 The caveats that travel with it: T4 unresolved (interval includes zero); type conditioning
explains twice as much as the RT increment; generation realism **not** improved by RT
conditioning; one seed, one fold.
6.8 Interpretation: preliminary evidence for level 2; explicitly not level 3.

*Figures: **F2**, **F3**, **F4**, **F5**. Source: embed_x1 @ 8bf7207 (+ derived component table).*

## 7 · A stricter test of pair-specific versus lineage-level information (X2)  *(PENDING)*

7.1 What X1 cannot settle: a single fold, a single seed, and a counterfactual tier (same type) that
is the weakest of the four available.
7.2 The X2 design, frozen before any result: cross-fitted component-blocked evaluation; arms G
(coarse RT lineage) and P (permuted-RT falsification); counterfactual tiers C1–C4; the
`UNDETERMINED` rule at < 30 components.
7.3 The prospective power statement: cross-fitting buys coverage, not power (T4 83 → 247
components, n_eff 9.0 → 8.6).
7.4 **[PLACEHOLDER — results pending]** outcome against the frozen gate X2-A/B/C/D.
7.5 **[PLACEHOLDER]** what each outcome would and would not license.

*Figures: F3/F4/F5 to be extended with cross-fitted panels once X2 lands; a per-tier counterfactual
panel (C1→C4) is specified in `FIGURE_PLAN.md` as F8 (pending).*

## 8 · Level 3 — what would be required, and the prospective candidate-selection framework
*(writable now as METHODS/PROSPECTIVE only)*

8.1 Why natural pairing cannot establish compatibility, and why non-observed pairings are not
incompatible pairs.
8.2 The prospective scoring framework: an RT × ncRNA conditional score matrix, the native-minus-
cross **margin**, and selection of candidate SETS rather than individual pairs.
8.3 Confidence conditioning: model uncertainty, sequence relatedness, retron type, lineage
distance, in-distribution status, replicate/seed consistency, margin size — and why choosing the
most evolutionarily distant RTs is a trap rather than a strategy.
8.4 What the experiment would look like, what result would refute the score, and the reporting
discipline (*predicted pairing / cross-reactivity score* until validated).

*Figure: **F7** (explicitly labelled prospective schematic; synthetic values).
Source: `CANDIDATE_SELECTION_DESIGN.md` — design only, nothing executed.*

## 9 · Discussion  *(writable now, one subsection pending)*

9.1 What the chapter establishes: level 1 firmly; level 2 preliminarily and at a small effect size.
9.2 The honest limiting factor: **independent relatedness components**, which cannot be increased
by re-folding, re-weighting or adding pairs from the same lineages.
9.3 The ncRNA-recovery argument: every ncRNA call comes from covariance models, so undetected
ncRNAs sit disproportionately in divergent lineages — exactly the ones that would add independent
components. Any advance in recovery should re-trigger the feasibility audit.
9.4 What this says about method choice generally: with n_eff ≈ 14, evaluation design dominates
model capacity; the constraint is the evaluation, not the architecture.
9.5 **[PENDING X2]** whether pair-specific information survives the stricter test, and what that
licenses next.
9.6 Relationship to the methodological precedent, and what a functional endpoint would change.

## 10 · Limitations  *(writable now)*

Population and detection limits; leakage that is accepted rather than eliminated; n_eff; one seed
per arm in X1; likelihood ≠ compatibility; generation realism; tier T4 unresolved; no phylogeny;
no structural or biochemical evidence; UMAP is visualisation only and no claim rests on it.

---

## Writing order recommended

1. §2, §3, §6.2–6.3 (methods; stable, already drafted in `METHODS_PROVENANCE.md`).
2. §4, §5, §6.4–6.8 (results from frozen bundles; draft in `RESULTS_DRAFT.md`).
3. §8 as prospective methods (`CANDIDATE_SELECTION_DESIGN.md`).
4. §1, §9, §10 last, so the framing matches what the results actually say.
5. §7.4–7.5 only after X2 lands, and only against its frozen outcome gate.

**Status of every claim in this outline is tracked in `CLAIM_EVIDENCE_MATRIX.tsv` and
`THESIS_RESULT_STATUS.md`. If a statement here is not in that matrix, it is not yet a claim.**
