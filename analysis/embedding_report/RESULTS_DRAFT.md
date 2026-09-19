# RESULTS — draft for frozen analyses only

Drafted against `THESIS_OUTLINE.md` §§4–7. **Only frozen results are written as prose.** Sections
awaiting X2 are marked `[PENDING]` and contain no anticipated outcome. Every number is read from a
frozen bundle; none was recomputed for this draft.

---

## 4 · Broad RT–ncRNA correspondence (level 1)

### 4.1 Retrieval against random and composition-matched candidates

Across the held-out fold of 4,638 observed pairs spanning 357 relatedness components
(n_eff = 14.1), the shared cross-modal space recovers the observed ncRNA partner far above chance.
In 50-way retrieval against uniformly drawn candidates the regularized-CCA probe reaches
**MRR 0.4407 (95 % CI [0.4039, 0.4772])** against a chance value of 0.0900, with top-1 accuracy
0.1714 and top-5 0.5164. The permutation failure control, in which pair assignments are permuted
within the fold, returns a null mean of 0.0901 [0.0781, 0.1040] over 2,000 permutations
(**p = 0.0005**), so the effect is not an artefact of the scoring procedure. The effect is not a
property of the direction of retrieval either: scoring ncRNA → RT gives MRR 0.4738 [0.4380,
0.5104].

The trivial baselines, which were run first by design, place this number in context. The strongest
of them — a k-mer composition mapping from RT dipeptides to ncRNA 4-mers — reaches 0.2265, while
length, GC, ncRNA training frequency and the RT-only retron-type shortcut are at or below chance.
Against length- and GC-matched candidates the cross-modal probe retains a supported advantage over
the k-mer baseline (**+0.0844 [+0.0503, +0.1187]**), which clears the pre-declared margin rule.

### 4.2 The shared space is organised by retron type

Three independent descriptions agree on what the shared space encodes. First, cross-modal cosine
similarity separates observed pairs from candidates, but the separation **shrinks monotonically as
candidates are matched more closely on retron type**: Cohen's *d* against observed pairs falls from
1.364 for random candidates to 0.420 for length- and GC-matched candidates and to 0.248 for
type-matched candidates. Second, in the open pool of 2,756 held-out ncRNAs, the nearest cross-modal
neighbour of a query RT shares its retron type **51.9 %** of the time against a pool prevalence of
9.4 % — a **5.32-fold** enrichment — while the specific observed partner is the nearest neighbour
for only **0.56 %** of queries and sits at **median rank 238 of 2,756**. Third, the leading
canonical dimension (canonical correlation 0.9865) is largely retron type: type membership accounts
for **η² = 0.809** of its variance on the protein side and **0.724** on the RNA side.

A multinomial probe fit on training components and reported on test components shows why this is
sufficient rather than incidental: retron type is recoverable from **each modality alone** — 0.4978
from ESM-C RT embeddings and 0.6557 from RiNALMo ncRNA embeddings, against a majority-class rate of
0.2693. If an RT can be assigned a type from its own representation, and an ncRNA likewise, then
any method that aligns the two spaces on a type axis will retrieve well against random and
composition-matched candidates **without having learned anything about individual partners**.

> **Level 1 is supported: frozen protein and RNA representations carry shared structure associated
> with naturally occurring RT–ncRNA systems. Nothing in this section is partner-specific.**

## 5 · Where retrieval stops being informative (the rung-3 boundary)

When candidate ncRNAs are restricted to the query's own retron type, the advantage of the
cross-modal probe over the k-mer baseline is **+0.0298 with a 95 % confidence interval of
[−0.0048, +0.0633]** — it does not clear the margin declared before the readout, and the two
scorers are not statistically distinguishable (M-CCA 0.1832 [0.1550, 0.2126] vs B-kmer 0.1534).

Two statements must be made together, and neither may be dropped. **The pre-registered kill
criterion fired**: signal that survived random and composition-matched candidates does not survive
type-matched candidates, so the finding is reported as *explained by retron type* rather than as
pairing compatibility. **And this is not proof of equivalence**: the interval is equally consistent
with a true improvement of up to +0.063, and with n_eff ≈ 14 the test has limited power. The honest
statement is that the data do not distinguish the two.

The three harder rungs — candidates from the same ncRNA identity cluster, from RTs in the same
identity cluster, and from the same species — cannot adjudicate the question at all in this
population: their candidate pools draw on **1, 10 and 22 independent components** respectively.
They are reported `UNDETERMINED` everywhere, including in the figures. This is absence of
sufficient measurement, not measured absence.

Two further results bound what could be done next. A within-type experiment would remove
type-associated structure by construction rather than controlling it away afterwards, and is
therefore the natural design; but of the 21 retron types, only **TypeIIIA3** and **TypeIB1** pass
the four pre-declared population criteria, and under the frozen split their **test-fold n_eff are
3.7 and 4.6**. Raw pair counts are actively misleading here: `TypeIC1_IC2` has 6,277 pairs at
n_eff 1.2. Consequently the pre-registered escalation to a contrastive partner-specificity model
was **not authorised**, and none was trained; the recorded status is *not yet justified as a
confirmatory partner-specific test*, explicitly not *method rejected*. Independent support for that
decision comes from a prior model in this laboratory, which reached the same conclusion from the
opposite direction — a protein-conditioned generator performed family recognition rather than
partner recognition, with 78 % of its leave-one-family-out gap attributable to family identity, and
whose contrastive arm raised the metric it optimised 43-fold while **degrading** the rank statistic
(2AFC 0.9532 → 0.9072, t = −21).

> **The binding constraint on a confirmatory partner-specificity test in this population is the
> number of independent relatedness components, not model capacity and not raw pair count.**

## 6 · Conditional RNA modelling: does the individual RT help? (level 2, PRELIMINARY)

Retrieval asks whether the observed partner can be ranked first among candidates. A conditional
generative formulation asks a different and more forgiving question: does knowing *this* RT change
the probability the model assigns to the ncRNA actually observed with it? Three arms share a
**byte-identical decoder** and differ only in the conditioning path — U conditions on a learned
constant, T on an embedding of the 21 retron types, and R on the frozen ESM-C representation of the
specific RT. The primary comparison, declared before any model existed, is **R versus T**, because
R versus U would only re-establish level 1.

### 6.1 Held-out likelihood

On the same frozen test fold, component-mean negative log-likelihood falls from **1.41097** nats/nt
(U, perplexity 4.100) to **1.37513** (T, 3.956) to **1.35734** (R, 3.886). Paired per-component
differences give:

| comparison | Δ NLL | 95 % CI | components favouring the first arm |
|---|---|---|---|
| T − U | −0.03585 | [−0.04262, −0.02924] | 80.7 % |
| R − U | −0.05363 | [−0.06224, −0.04454] | 82.9 % |
| **R − T** | **−0.01778** | **[−0.02428, −0.01052]** | **65.0 %** |

The R − T advantage survives the frozen near-duplicate-excluded sensitivity population
(−0.01809 [−0.02530, −0.00992] over 284 components), so it is not produced by the residual fragment
channel.

Two qualifications belong in the same breath as the estimate. **The effect is small** — about 1.3 %
relative — and **retron-type conditioning explains roughly twice as much as the additional
specific-RT increment** (−0.036 versus −0.018), so type remains the dominant signal. The
component-level distribution shows the same thing in a different way: the effect is a modest shift
of a wide distribution rather than a uniform gain, and 35 % of components do not favour R.

### 6.2 The observed RT versus same-type alternatives

An evaluation-only control substitutes, for each held-out pair, **M = 8 alternative RTs** drawn
from the same retron type in the test fold, excluding the observed RT and any RT observed with that
ncRNA; the same arm-R model scores the same ncRNA with only the conditioning RT swapped.
4,630 of 4,638 pairs (99.8 %) are eligible.

> **Δ log P per nucleotide = +0.013512 [+0.006820, +0.018813]** over 355 components, with **71.0 %
> of pairs** and 75.8 % of components favouring the RT actually observed with that ncRNA.

These alternatives are **counterfactual conditioning controls, not biological negatives**: they are
not incompatible pairs, and no combination absent from the corpus is treated as one.

### 6.3 Where the effect does not appear

Two negatives travel with the result and are reported at equal prominence.

First, in **T4 — the independently recurrent tier**, where a repeated observation is a repeated
biological event rather than repeated deposition — the advantage is not resolved: R − T =
**−0.00776 [−0.01761, +0.00169]**, an interval that includes zero, over 83 components (n_eff 9.02).
This is descriptive and under-powered rather than a refutation, but it is the single most important
caveat on the result: the tier with the strongest independence is the one in which the effect is
not established.

Second, the likelihood advantage **does not appear in generation**. Type conditioning transforms
marginal realism (3-mer Jensen–Shannon divergence against real held-out ncRNA falls from 0.02812
for U to 0.00256 for T), but RT conditioning does not improve it further: R is slightly worse
(0.00428) and over-generates length (median 178 nt against 156 nt for real ncRNA). All arms produce
markedly less structured RNA than real ncRNA (median MFE −24.8 / −39.4 / −42.7 against −58.7). No
generated sequence is claimed to be functional, and none is ranked by compatibility.

> **Preliminary evidence that specific RT sequence representations carry information predictive of
> their observed ncRNA beyond retron type. This is one pilot run with one seed per arm on a single
> fold; it is not co-evolution, physical interaction, or biochemical compatibility, and it says
> nothing about whether non-observed combinations would function.**

## 7 · A stricter test of pair-specific versus lineage-level information  `[PENDING]`

### 7.1 What X1 cannot settle  *(writable now)*

Three limitations of the pilot define the next test. The estimate rests on a single fold and a
single seed per arm. The counterfactual control uses the weakest available tier — alternatives of
the same retron type, with no constraint on length, embedding proximity or homolog-cluster
membership. And the design cannot distinguish information specific to the individual RT from
information carried by its **finer lineage**: a 50 %-identity homolog group, a subtype, or a
taxonomic neighbourhood would all improve the likelihood without any pair-specific content.

### 7.2 Design  *(frozen before any result; writable now)*

X2 answers those three points with a design frozen in advance: component-blocked **5-fold
cross-fitting** in which every one of the 1,075 components is evaluated out-of-fold exactly once
and no component, RT cluster or ncRNA cluster crosses a fold boundary; two additional arms — **G**,
conditioning on the ESM-C representation of the frozen 50 %-identity cluster representative (coarse
RT lineage), and **P**, conditioning on a within-type **permuted** RT during training only, as a
falsification control; and four counterfactual tiers of increasing stringency (**C1** same type,
**C2** + length-matched, **C3** + nearest ESM-C neighbours, **C4** within the same 50 %-identity
RT cluster), each requiring the alternative RT to lie in the same fold so that novelty is not
confounded with specificity. Architecture and hyperparameters are imported unchanged; no capacity
was added and no contrastive term introduced. A tier or stratum spanning fewer than 30 independent
components is reported `UNDETERMINED`.

One prospective statement was recorded before the run and is reported whatever the outcome:
cross-fitting raises T4 coverage from 83 to 247 components, but **n_eff moves from 9.0 to 8.6** —
it does not improve, because n_eff is a property of the component-size distribution and not of the
number of folds. **Cross-fitting buys coverage and robustness, not statistical power.** If T4
remains unresolved, that was predicted in advance.

### 7.3 Results  `[PENDING — X2 is running; nothing to report]`

*This subsection will be written only after X2 lands and is read against its frozen outcome gate
(X2-A confirmed / X2-B lineage-level only / X2-C not replicated / X2-D under-powered). No direction
or magnitude is anticipated here. The sentences this section may eventually license, and those it
may not, are listed in `THESIS_RESULT_STATUS.md` §2.*

### 7.4 What each outcome would license  `[PENDING]`

*To be written with the result, against the frozen gate, not reconstructed afterwards.*

## 8 · Level 3 — not addressed by any result above

No analysis in this chapter bears on functional compatibility, orthogonality, binding or
co-evolution, and none can: the data are sequence representations and natural co-occurrence.
A combination absent from the corpus is a **non-observed pairing** — the corpus records what was
found, not what is possible, and every ncRNA call in it comes from covariance models, so ncRNAs no
model detects are invisible by construction. The prospective framework for eventually nominating
candidate low-cross-reactivity pairs for laboratory testing is described in
`CANDIDATE_SELECTION_DESIGN.md` and illustrated schematically in Figure F7; it has not been run,
its prerequisites are unmet, and any score it would produce is a **predicted pairing score** until
an experiment says otherwise.
