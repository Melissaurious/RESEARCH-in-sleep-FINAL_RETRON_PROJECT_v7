# RESULTS — draft for frozen analyses only

Drafted against `THESIS_OUTLINE.md` §§4–8. **Every analysis reported here is frozen**: the
embedding baseline (`embed_g2` @ `2c9127b`), the conditional pilot (`embed_x1` @ `8bf7207`) and the
cross-fitted confirmation (`embed_x2` @ `4f8550b`, closed at `fdf0872`). Nothing is pending
computation. Every number is read from a frozen bundle; none was recomputed for this draft.

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

## 6 · Conditional RNA modelling: does the individual RT help? (level 2, pilot)

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

The cross-fitted confirmation in §7 sustains the direction of this pilot result — and bounds it in
three ways the pilot could not see: most of the gain is lineage rather than pair-specific, the
advantage collapses under close counterfactuals, and the residue beyond the homolog group is
seed-unstable in magnitude.

## 7 · A stricter test: pair-specific versus lineage-level information (X2)

### 7.1 What the pilot could not settle

Three limitations of X1 defined the next test. The estimate rested on a single fold and a single
seed per arm. Its counterfactual control used the weakest available tier — alternatives of the
same retron type, unconstrained in length, embedding proximity or homolog-cluster membership. And
the design could not distinguish information specific to the individual RT from information
carried by its **finer lineage**: a 50 %-identity homolog group would improve the likelihood
without any pair-specific content.

### 7.2 Design

X2 answers those three points with a design frozen before any effect estimate was inspected:
component-blocked **5-fold cross-fitting** in which each of the 1,075 components is evaluated
out-of-fold exactly once and no component, RT cluster or ncRNA cluster crosses a fold boundary;
two additional arms — **G**, conditioning on the ESM-C representation of the frozen 50 %-identity
cluster representative (coarse RT lineage), and **P**, conditioning on a within-type **permuted**
RT during training only (falsification); and four counterfactual tiers of increasing stringency
(**C1** same type, **C2** + length-matched, **C3** + the eight nearest ESM-C neighbours, **C4**
within the same 50 %-identity RT cluster), each requiring the alternative RT to lie in the same
fold so that novelty is not confounded with specificity. Architecture and hyperparameters were
imported unchanged from X1. A tier or stratum spanning fewer than 30 independent components is
reported `UNDETERMINED`.

One prospective statement was recorded before the run: cross-fitting raises T4 coverage from 83
to 247 components while n_eff moves from 9.0 to 8.6, so T4 might well remain unresolved —
cross-fitting buys coverage and robustness, not power. **That prediction proved wrong in the
favourable direction (§7.3), and is retained in the record rather than removed.**

### 7.3 The primary endpoint replicates, and T4 resolves

Out-of-fold component-mean negative log-likelihood falls from 1.40666 nats/nt (U) to 1.38329 (T)
to 1.36410 (G) to 1.35859 (R), with the permuted arm P at 1.37739. The primary contrast:

> **R − T = −0.02470 [−0.02907, −0.02037] nats/nt, with 64.9 % of 1,075 independent components
> favouring R** (X1: −0.01778, 65.0 %).

The effect is not carried by one fold — all five folds share the sign and every fold interval
excludes zero (−0.0156, −0.0144, −0.0269, −0.0357, −0.0297; mean −0.02446, sd 0.00921) — nor by
optimization noise, since three seeds give −0.02470, −0.03674 and −0.02093. It survives the frozen
near-duplicate-excluded population (−0.02532 [−0.03410, −0.01682]) and the high-confidence T3
stratum (−0.02848). Across 36 prespecified adjudicable strata, 28 have the whole interval below
zero, one above, seven spanning zero, and 86.1 % favour R; the effect is mildly *weaker* at high
deposition multiplicity, so it is not an artefact of repeated database deposition.

**T4 resolves in the same direction**: R − T = **−0.02594 [−0.03508, −0.01731]** over 247
components, where X1 had −0.00776 with an interval including zero. The tier in which a repeated
observation is a repeated biological *event* now supports the effect.

Against the gate frozen in advance, all five X2-A criteria are met on their literal terms, and the
gate is not retrospectively revised. Two of the five, however, are recorded by the bundle itself
as "yes, marginally" and "yes, directionally only" — and §§7.4–7.5 are why.

### 7.4 Most of the gain is lineage, and the residue is small and unstable

Decomposing the primary contrast through the lineage arm:

| contrast | Δ NLL | 95 % CI | components favouring first |
|---|---|---|---|
| T − U (broad type vs none) | −0.02337 | [−0.02775, −0.01902] | 76.1 % |
| G − T (**lineage beyond type**) | **−0.01919** | [−0.02339, −0.01498] | 62.4 % |
| R − T (specific RT beyond type) | −0.02470 | [−0.02907, −0.02037] | 64.9 % |
| R − G (**specific RT beyond its own homolog group**) | **−0.00551** | [−0.00797, −0.00312] | 55.3 % |
| P − T (permuted RT vs type) | −0.00590 | [−0.01109, −0.00023] | 57.0 % |
| R − P | −0.01880 | [−0.02460, −0.01359] | 59.7 % |

**G − T accounts for roughly 78 % of R − T.** The frozen 50 %-identity homolog group — not the
individual RT — already supplies most of the advantage over the broad type label. The residual
R − G is directionally reproducible (the interval excludes zero on all three seeds) but **small
and not well determined in magnitude**: across seeds it runs −0.00551, −0.01133 and −0.01560, a
factor-of-three spread whose standard deviation (0.0051) is as large as the primary point estimate
(0.0055). In the near-duplicate-excluded population its interval includes zero. A magnitude quoted
from one seed is therefore not a result, and none is quoted here.

The falsification arm adds a second qualification. **P − T = −0.00590** is not flat: a model
trained on RTs deranged *within* retron type still beats the type label, retaining about a quarter
of the full effect. R − P = −0.01880 confirms that the observed correspondence supplies most of the
advantage — but not all of it. Some of the benefit comes from conditioning on *a* realistic RT
representation rather than on *the* right one.

### 7.5 Counterfactual discrimination decays, and at pair level approaches chance

The counterfactual hierarchy is the decisive result of X2. With Δ log P per nucleotide defined as
NLL(ncRNA | alternative RT) − NLL(ncRNA | observed RT), positive favouring the observed RT:

| tier | alternative drawn from | components | Δ log P/nt | 95 % CI | % of pairs favouring the observed RT |
|---|---|---|---|---|---|
| C1 | same retron type | 1,019 | +0.01766 | [+0.01533, +0.01994] | 72.6 % |
| C2 | + RT length within 10 % | 832 | +0.01543 | [+0.01291, +0.01786] | 70.6 % |
| C3 | + 8 nearest ESM-C neighbours | 1,073 | **+0.00397** | [+0.00202, +0.00586] | **52.5 %** |
| C4 | within the same 50 %-identity RT cluster | 451 | **+0.00168** | [+0.00101, +0.00251] | 60.7 % |

Every interval excludes zero, and the effect **decays roughly ten-fold from C1 to C4**. Once the
alternative RT is drawn from the observed RT's own embedding neighbourhood, only **52.5 % of
pairs** favour the observed RT: barely above a coin flip at the level of the individual pair, even
though the component-level mean remains positive.

The weighting makes this sharper. Component-level and raw pair-weighted aggregates agree in
direction at C1, C2 and C4 but **differ in sign at C3** (+0.003974 versus −0.000205, median
+0.000187). This is a weighting effect rather than an inconsistency — the component-level estimate
gives every independent component equal weight, whereas an unweighted pair mean lets the largest
components dominate — and the component-level estimate remains the pre-registered endpoint. But
the pair-level view is what forbids any per-pair biological reading of these likelihoods.

### 7.6 Generalisation is weakest where RTs least resemble training

Stratifying by cosine similarity between the evaluated RT and the nearest RT the evaluating model
actually saw in training:

| quartile | R − T | 95 % CI | components | R − G |
|---|---|---|---|---|
| Q1 < 0.983 | **−0.00584** | **[−0.01288, +0.00136]** | 371 | −0.00426 |
| Q2 0.983–0.988 | −0.02317 | [−0.02869, −0.01765] | 378 | −0.00686 |
| Q3 0.988–0.991 | −0.02298 | [−0.02793, −0.01831] | 447 | −0.00480 |
| Q4 ≥ 0.991 | −0.03193 | [−0.03994, −0.02454] | 473 | −0.00430 |

R − T strengthens monotonically with similarity to training, and **in the least-similar quartile
its interval spans zero**. Two observations bound this without dissolving it: RT ESM-C embeddings
are highly compressed — the median nearest-training cosine is 0.987 and even Q1 sits above 0.983,
so this is a narrow band rather than near-versus-far homology — and R − G is *flat* across the
same quartiles (−0.0043 to −0.0069), which localises the gradient to the **T** arm rather than to
residual RT relatedness leaking into R. The limit on extrapolation to RT lineages unlike anything
in training nevertheless stands.

Some strata remain **UNDETERMINED** rather than null: RT homolog groups above 100 members (22
components), ncRNA clusters above 100 members (14), and two rare recurrence classes. The effect is
carried by small ncRNA clusters (−0.025 at sizes 1 and 2–5) and is not demonstrated for the
largest ones.

### 7.7 What X2 establishes, in one paragraph

> Specific RT sequence information provides a reproducible improvement in prediction of the
> cognate ncRNA beyond broad retron type and beyond a coarse 50 %-identity RT homolog-group
> representation. However, most of the RT-associated predictive gain is explained at the
> homolog-lineage level, while the additional specific-RT effect is small, weak at the individual-
> pair level under close counterfactuals, and uncertain in magnitude across training seeds.

This paragraph, and not the gate label `X2-A`, is the conclusion of record. X2 is **internal
cross-fitted confirmation, not external validation**: no new data exist, and the same 30,924-pair
population underlies both X1 and X2.


## 8 · Level 3 — not addressed by any result above

No analysis in this chapter bears on functional compatibility, orthogonality, binding or
co-evolution, and none can: the data are sequence representations and natural co-occurrence. The
X2 closure record states this explicitly and at length — biochemical compatibility, physical
interaction, functional interchangeability, orthogonality, causal co-evolution, the incompatibility
of any non-observed combination, and **any per-pair biological inference whatsoever** are all
listed there as statements that do not follow from the result. The pair-level findings of §7.5 are
the concrete reason for the last of those: at the strictest embedding-neighbour control the model
favours the observed RT for 52.5 % of pairs, and the raw pair-weighted mean is nominally negative.

A combination absent from the corpus remains a **non-observed pairing** — the corpus records what
was found, not what is possible, and every ncRNA call in it comes from covariance models, so
ncRNAs that no model detects are invisible by construction.

The prospective framework for eventually nominating candidate low-cross-reactivity pairs for
laboratory testing is described in `CANDIDATE_SELECTION_DESIGN.md` and illustrated schematically in
Figure F7. It has not been run. X2 makes its prerequisites **harder**, not easier: any such score
would have to be built against C3/C4-strength counterfactuals, where the effect is +0.004 and
+0.002 nats/nt respectively; it would have to carry across-seed spread, since the specific-RT
increment beyond homolog lineage moves by a factor of three between seeds; it would have to report
distance-to-training as a primary axis, since the effect is not demonstrated in the least-similar
quartile; and it may never treat a non-observed pairing as a negative. Until an experiment says
otherwise, any such quantity is a **predicted pairing score**, not evidence of compatibility or
orthogonality.
