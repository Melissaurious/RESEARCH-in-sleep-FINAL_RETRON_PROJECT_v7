# PROJECT EVIDENCE MAP — revision 2

**Revision 2 (2026-09-19, later).** Supersedes revision 1, which is stale. Revision 1 was written
before `embed_x2` (`4f8550b`) and before Stage 3C closed (`34000ee`). Four of its judgements were
wrong or overstated and are corrected here — each correction is flagged **[REV-1 CORRECTED]** with
what changed and why. Revision 1's thesis sentence, publication ranking and minimum-work
recommendation are **withdrawn** and re-derived.

Read-only: no bundle was modified, no gate reopened, no compute beyond an exact-hash join started.
This file is **not** claim authority; `idea-stage/docs/research_contract.md` is.

---

## 0 · Evidence sources, pinned

| source | path | commit | change since rev 1 |
|---|---|---|---|
| main — Stage-2 final report | `…_v7` | `46414f4` | unchanged; `human_input_audit` **still PENDING** |
| main — reviewed closed state | `…_v7` | `94a1a78` | unchanged |
| **embeddings + X2 (frozen results)** | `…_v7-embeddings` | **`4f8550b`** | `embed_x2_rt_specificity_confirmation` |
| **X2 closure / handoff / export — GOVERNING** | `…_v7-embeddings` | **`fdf0872`** | **new: `X2_CLOSURE.md`, `X2_HANDOFF.md`, 27-claim matrix, pair- and component-level exports. Supersedes preliminary X2 prose wherever they differ** |
| embedding report | `…_v7-embedding-report` | `e3f96b1` | unchanged (predates X2) |
| **Stage 3A / 3B / 3C** | `…_v7-stage3c` | **`34000ee`** | **new: Stage 3C complete and packaged** |
| Stage 3A / 3B (frozen) | `…_v7-asset-audit` | `67c137b` | unchanged |
| Mestre audit | `…_v7-mestre-audit` | `b05934f` (MCC-v3.1 freeze `e047fdc`) | unchanged |
| SPIRE ncRNA | `…_v7-spire-ncrna` | `ed4a663e19ca0d6625776bb92b1919b37e47e754` | unchanged; **interpretation revised** |
| dbchar workbench | `…_v7-dbchar-workbench` | `12ea561` | unchanged |

---

## 1 · The revised one-paragraph answer

The project has a defensible instrument layer, a strong negative layer, and — new in revision 2 —
**one replicated, controlled positive result about RT→ncRNA conditioning** and **one reproducible
architectural landmark**. `embed_x2` confirms under component-blocked cross-fitting that the
specific RT carries information about its ncRNA beyond both the retron-type label and its own
50 %-identity homolog group, with the increment over the homolog group small, seed-variable and
undemonstrated in the least-similar quartile. Stage 3C shows that what is reproducible across 62
experimental RT chains is a **catalytic centre** locatable by three mutually independent instruments
agreeing to within two residues — not a three-way domain partition, which neither contact density
nor the literature itself supports. What has failed remains failed: independent reproduction of
Mestre's classification, de novo comparative ncRNA discovery as a boundary instrument, and held-out
catalytic-geometry validation. The 175-element experimental panel is now mapped: **only 16 of 175
elements are fully external** to this project's populations, so it is an assay layer, not an
independent benchmark, until that map is respected.

---

## 2 · Evidence by area

### 2.1 Canonical RT/retron population definition — **ESTABLISHED** (as description) · unchanged

43 files, 3,358,182 lines, manifest sha256 `8e9b7999…41d00`; RT-anchored 3,059,700 → loci 2,847,312
→ physical loci 2,475,684 → **exact RT 501,561**; 16,458 exact ncRNAs; 30,924 exact pairs; Retron
family 78,287 exact RTs. Back-translation verifies 99.47 % of POP-RT-FAM with 618 mismatches
retained. No two units convert by a constant (loci per exact RT 1.11–5.49 by database).

### 2.2 RT0–RT7 / the conserved-state mapper — **SUPPORTED_WITH_LIMITATIONS** · strengthened by Stage 3C

Unchanged in scope: `hhmake -M 50`, one confirmatory UG25 lineage, 369,381 eligible of 501,561,
354,102 inspectable, `CATALYTIC_CONFIRMED` 0.9653 of CAT-mapped. Historical labels remain
LtrA-local with **RT0/RT1 UNRESOLVED**.

**New corroboration from Stage 3C, and it is genuinely independent:** applied unmodified to 62
experimental chains, `CAT_STATE 262` lands **exactly 2 residues before the nearest Stage-3B catalytic
aspartate in 17/17 chains** where both instruments commit, and in the same structural unit in 17/19.
A sequence HMM state and metal/substrate/author-derived structural truth share no input. The
GII-centred gradient reappears as expected (retron median mapped fraction **0.427** vs non-LTR
0.813), and RT0/RT1 receive **no interval on any structure — 0/62** (enforced in code).

### 2.3 Stage 3A structural decomposition — **FAILED**, and Stage 3C explains *why* it failed

Unchanged: palm-like called in **0.565** of 46 primary chains against a 0.70 bar; thumb-like 0.130;
fingers-like 0.304; 22/22 LOGO folds FAIL; PDP replicate partition agreement **0.385**.

**[REV-1 CORRECTED]** Revision 1 read this as "RT chains do not decompose into three reproducible
units, instrument-specific". Stage 3C shows the negative is **more general and better explained**
than that: the literature does not agree with itself either (below), and the numbered state series
collapses into *one* structural unit. The honest statement is not "our parser could not find the
three domains" but **"in these structures there is mostly one core unit plus accessory content, and
the three-way partition is a fold-level description that does not correspond to separable
contact-density units."**

### 2.4 Stage 3B catalytic geometry — **NOT_YET_TESTED** as a detector; **mislabelled** · unchanged

Two gates landed; g3–g5 never ran; Tier B never opened; **K5 fired** (pool 23 vs ≥ 60). Only
in-sample Tier-A calibration exists: **13/19 = 0.684**, windows fitted on the same truth pairs, each
window edge set by a single chain. Out-of-sample LOCO 12 HIT / 5 MISS / **2 ABSTAIN**. Tier B holds
**0 `HARD_PAIR`** chains, so a residue-exact HIT was unreachable there. Still labelled "CLOSED at
PARTIAL" — see `TIER0_REPAIR_TABLE.md` T0-1/T0-2. Stage 3C repeats the inherited label, which is how
a mislabel propagates.

### 2.5 Stage 3C architecture integration — **COMPLETE**; a census, no verdict merged · **NEW**

62 chains, 31 groups, 236 hash-checked frozen inputs all matching. No inferential test declared or
run; every interpretation is marked `PROPOSED:`. Six distinct vocabularies are kept apart. Graded
separately, as required:

| sub-question | grade | the number that decides it |
|---|---|---|
| **(a) generic structural-domain decomposition** | **FAILED** (unchanged) | palm-like 0.565 < 0.70; unit *count* agrees in only **3/18** numbering-consistent replicate pairs |
| **(b) catalytic-site localisation** | **SUPPORTED_WITH_LIMITATIONS** — the strongest architectural fact in the project | catalytic Asps inside a **single unit in 19/19** chains; detector prediction in the same unit as truth **19/19** including all 6 residue-level misses; site-containing unit replicate-stable at Jaccard ≥ 0.70 in **13/14** pairs (median 0.897) against a **0.309** median chance share. **Scope: all 19 truth-bearing chains are non-retron.** Carboxylate *distance* is not stable (> 0.5 Å in 4/6 pairs, max 2.77 Å) |
| **(c) RT0–RT7 states vs structure** | **SUPPORTED_WITH_LIMITATIONS** | blocks **merge rather than separate**: SB3+SB56 in the same unit 28/28, SB56+SB7 35/36; SB7 contained 37/37, SB56 53/54; splitting concentrates exactly where Stage 2 said evidence was weakest (SB2p 12/24, SB4 11/37). RT0/RT1: **0/62** |
| **(d) literature fingers/palm/thumb** | **FAILED as a partition; the references disagree with each other** | LITERATURE fingers coincide with a unit **0/11** (median best J 0.429); palm 2/7; thumb 3/9; a **combined fingers+palm** region coincides 1/1 (J 0.713). Two 2026 papers on the same Eco8 protein publish **incompatible** partitions in the same numbering frame; HIV-1 reviews differ by 1–5 residues. Only **17 usable statements over 7 chains** (corrected from 8 in `34000ee`); 21 sources unretrievable |
| **(e) Region X / Region Y** | **PRELIMINARY (Y) / UNDERPOWERED (X)** — and explicitly **not universal** | **No source states a general residue-numbered interval for either region.** Region X scannable in only **33/62** chains, undefined in **13/21 retron** chains. Region Y defined in **15/21** retron chains; **all six Retron-Eco8 chains carry no VTG-like triplet**, and VTG appears in **4 non-retron** chains — *neither universal nor exclusive*. Y carries **1.34×** its length-proportional share of RNA-contacting residues in retrons (median; range **0.59–1.86**, n = 15) vs 1.06 in 4 non-retrons. Controls passed: literature motif positions 9/9, YxDD 19/19, `SUBSTRATE_NA` reproduction 44/44, shuffle null 4/3300 |
| **(f) termini / fusions** | **UNDERPOWERED / NOT_YET_TESTED** | terminal extensions interpretable in only **20/62** chains — in 39 the anchor series is truncated (mostly N-terminally, in retrons), so those residues are *unseen sequence, not measured extension*. Two insertion measures deliberately reported together: the declared gap rule finds **no** insertion ≥ 20 aa (max excess 19) while the instrument's own insertion runs reach **774** residues. Unusual architecture explains the decomposition failures only weakly (median 1 outside-core unit for no-call chains vs 2 for call chains) |

**No universal Region-Y motif is claimed, and none is supported.** **No universal three-domain
architecture is claimed, and the evidence refutes it as a contact-density partition.** Stage 3C
issues no verdict, merges nothing, and leaves Stage 2, 3A and 3B closed as they were.

### 2.6 Historical Mestre classification — three different questions, three different answers **[REV-1 CORRECTED]**

Revision 1 collapsed these. They must be separated:

| question | grade | evidence |
|---|---|---|
| **(i) Reproduction of Mestre's published objects** | **SUPPORTED_WITH_LIMITATIONS** | 18/18 tables and 3/3 PNGs byte-identical after one declared root remap; but the inputs manifest is not reproducible, `s00` passes vacuously, `env.lock` is conda base |
| **(ii) Re-inference of Mestre's classification from sequences** | **FAILED** | ≤ 3 of 11 clades; the alignment and RT0–RT7 extracts are *not published and not on disk*; 112 substitute proteins, 15 RNA polymerase subunits; **no positive control ran** (the same rule on the published tree gives 10/11) |
| **(iii) Phylogenetic *placement* into the historical 11-clade system (the M2a instrument)** | **FAILED on its own control gate** | K3: shuffled queries confidently placed at **7.9 %** (MCC-v3.1) and **19.8 %** (v2) against a ≤ 1 % limit; *"LWR does not separate: shuffled median 0.998"*; Codex **FAIL 4.5/10**; the non-retron panel "PASS" is 1,080/1,083 extraction failures. MCC-v3.1 extractability **82.1 %** against a written ≥ 90 % (K1) — a missed criterion not declared a failure |
| **(iv) A modern, label-independent de novo RT phylogeny** | **NOT_YET_TESTED** | **no such analysis has been run in this project.** The five failed tree routes are prior-project (`RETRON-DB V3/V4`), `[UNVERIFIED]` here, and were routes to *different* questions |

**[REV-1 CORRECTED]** Revision 1 recommended closing "sequence-tree routes" permanently on the
strength of (ii)+(iii) plus unverified prior failures. **That recommendation is withdrawn.** The
failure of a historical-placement instrument does not falsify a modern de novo phylogeny; they have
different inputs, different targets and different success criteria. What (iii) *does* establish is
that **placement into the historical 11-clade system is not currently possible with a validated
discriminator** — which is an argument for label-independence, not against phylogeny.

### 2.7 De novo ncRNA discovery / SPIRE — **FAILED as an instrument**, with **two reusable features** **[REV-1 CORRECTED]**

The failure stands and is not softened: `ROUND2_FAIL_STOP`; G1 enrichment **2.88×** against a
required ≥ 3×; **G7 decisive — the method finds 343 while a fixed interval (−193…−24) finds 901**,
both ends within ±20 nt 60 vs 87; the released package abstains on 94 % of blinded CM-positive loci
and performs at chance; covariation is non-specific (88 % of distal windows, 100 % of group II sets).

**[REV-1 CORRECTED]** Revision 1 filed the post-mortem only as "preliminary and partly circular" and
recommended closure without inheritance. That under-reads it. The post-mortem establishes two
things that are **features for a future boundary task, not discoveries of ncRNA families**:

1. a **retron-enriched ~90-nt internal ncRNA submotif** — 1,793 instances, median centre −116 nt,
   median length 88 nt; retron 140/164 (85 %) vs pooled non-retron 42/80 (52.5 %), Fisher
   **p = 1.0e-7**, OR 5.3;
2. a **strong RT-relative, type-conditioned positional prior** — global 901 (85.7 %) and **per-type
   969 (92.2 %)** at IoU ≥ 0.5, against the method's 343.

Both are **derived from CM calls and overlap the locus's own CM call 97.9 % of the time**, so they
are same-paradigm rediscovery and cannot validate a CM-based truth. As *priors/features* for a
supervised boundary model evaluated against **non-CM** truth, they are legitimate and strong. The
correct status is: **FAILED as de novo family discovery; PRELIMINARY-but-useful as positional
features.** The discovery branch stays closed; the features are inherited.

### 2.8 Existing CM-based ncRNA annotation — **ESTABLISHED as detector description** · unchanged

21 Mestre-authored CMs; types VI, VII, VIII, X, XI, XII unmodelled. Geometry on 344,154 canonical
placements: 94.5 % upstream, median gap 55 bp, 99.8 % same strand, 94.41 % zero CDS between. Retron
zero-ncRNA **47.24 %**; carriage swings 6.6-fold with tool combination (89.23 % → 13.50 %); by
subtype 90.1 % → 0 %. In 17 of 18 PADLOC retron rules the ncRNA is a scoring element, so carriage is
partly definitional.

### 2.9 RT/ncRNA embeddings (retrieval) — **SUPPORTED_WITH_LIMITATIONS** at type level; rung 3 still **UNDERPOWERED**

Unchanged by X2, because X2 is a likelihood experiment, not a retrieval one: MRR **0.4407** vs chance
0.0900; permutation p = 0.0005; **rung 3 (type-matched decoys) +0.0298 [−0.0048, +0.0633]** — margin
not cleared, escalation correctly refused. η²(type) 0.809/0.724 on the leading canonical dimension.
Two trivial baselines were inert by construction (T0-5).

### 2.10 Conditional RT→ncRNA modelling — **[REV-1 CORRECTED]**, and this is the substantive change

Revision 1 said partner-specific pairing "failed" and treated X1's effect as sign-unstable and
possibly absent. **`embed_x2` supersedes that reading**, and X2 is now formally **CLOSED**:
`4f8550b` holds the frozen results, **`fdf0872` is the governing interpretive source**.

**The conclusion of record is the qualified paragraph, not the label `X2-A`** (`X2_CLOSURE.md` §2,
binding):

> Specific RT sequence information provides a reproducible improvement in prediction of the cognate
> ncRNA beyond broad retron type and beyond a coarse 50 %-identity RT homolog-group representation.
> However, **most of the RT-associated predictive gain is explained at the homolog-lineage level**,
> while the additional specific-RT effect is **small, weak at the individual-pair level under close
> counterfactuals, and uncertain in magnitude across training seeds**.

The preregistered gate returned X2-A on all five literal criteria and is **not** retrospectively
revised; narrowing the interpretation is a separate act from adjudicating the gate. X2 is a materially stronger
design: **component-blocked 5-fold cross-fitting over the entire population (1,075 components /
30,924 pairs)** rather than one held-out fold; five arms (U, T, G, R, P) with a byte-identical
decoder; aggregation per-sequence → per-component (token-weighted) → bootstrap over components; the
outcome gate frozen in `DESIGN.md` §8 **before** any estimate was inspected. Verdict: **X2-A with
three qualifications**.

| contrast | Δ (per nt) | 95 % CI | % components favouring first |
|---|---|---|---|
| T − U (type label vs nothing) | −0.02337 | [−0.02775, −0.01902] | 76.1 % |
| G − U (homolog representative vs nothing) | −0.04256 | [−0.04619, −0.03893] | 86.0 % |
| **R − T (primary)** | **−0.02470** | **[−0.02907, −0.02037]** | **64.9 %** |
| **R − G (exact RT beyond its 50 %-id homolog group)** | **−0.00551** | **[−0.00797, −0.00312]** | **55.3 %** |
| G − T | −0.01919 | [−0.02339, −0.01498] | 62.4 % |
| **P − T (within-type deranged RT, falsification)** | **−0.00590** | **[−0.01109, −0.00023]** | 57.0 % |
| R − P | −0.01880 | [−0.02460, −0.01359] | 59.7 % |

**T4 is resolved:** −0.02594 [−0.03508, −0.01731] over **247 components** (cross-fitting raised T4
coverage from 83 to 247). Near-duplicate-excluded sensitivity −0.02532 [−0.03410, −0.01682].
Replication across three seeds: R − T all same sign, mean −0.02746 (sd 0.00826); R − G all same
sign, mean −0.01081 (**sd 0.00506** against a primary estimate of 0.00551).

Counterfactual conditioning, admissibility frozen in advance (alternative RT must be unobserved with
that ncRNA *and* drawn from the same cross-fit fold):

| tier | control | Δ log P/nt | 95 % CI | % **pairs** favouring observed |
|---|---|---|---|---|
| C1 | same retron type | +0.01766 | [+0.01533, +0.01994] | 72.6 % |
| C2 | + similar RT length | +0.01543 | [+0.01291, +0.01786] | 70.6 % |
| **C3** | **+ 8 nearest RTs by ESM-C cosine** | **+0.00397** | **[+0.00202, +0.00586]** | **52.5 %** |
| **C4** | **within the same 50 %-id cluster** | **+0.00168** | **[+0.00101, +0.00251]** | 60.7 % |

**Now the four distinctions the operator asked for, kept separate and not collapsed:**

| level | grade | the number |
|---|---|---|
| **(i) broad RT-lineage information predicts the ncRNA** | **ESTABLISHED** (within this population and its relatedness structure) | G − U −0.04256 [−0.04619, −0.03893], 86.0 % of components; G − T −0.01919. The homolog group alone beats the type label decisively |
| **(ii) exact-RT residual information beyond lineage** | **SUPPORTED_WITH_LIMITATIONS — small, replicated in sign, magnitude undetermined** | R − G −0.00551 [−0.00797, −0.00312]; same sign on 3/3 seeds but range −0.0055 → −0.0156, **sd 0.0051 ≈ the point estimate**; holds in T4 (−0.00499 [−0.00945, −0.00055], 247 comps) and T3, but the near-duplicate sensitivity arm **spans zero** (−0.00210 [−0.00601, +0.00196], 284 comps). **G − T = −0.019 of the total R − T = −0.025, so the homolog group explains ~77 % of the advantage over the type label** |
| **(iii) pair-level discriminability** | **UNDERPOWERED / not demonstrated** | the effect decays **~10-fold** as the control tightens (C1 +0.0177 → C4 +0.0017), and at C3 only **52.5 % of pairs** favour the observed RT. **The closure sharpens this further:** at C3 the *raw pair-level mean* is **−0.000205 — nominally negative** — with a barely positive median (+0.000187), even though the component-level interval excludes zero. That is a weighting effect, not an inconsistency, and the closure states it is "what forbids any per-pair biological reading". C4 is statistically non-zero (+0.00168 over 451 components) but "significance here does not imply substantive discrimination". Retrieval agrees: rung 3 fails; the observed partner is the nearest cross-modal neighbour for **0.56 %** of queries |
| **(iv) biochemical compatibility / functional pairing** | **NOT_YET_TESTED** | nothing in any arm measures binding, msDNA production or interchangeability. The bundle states this itself and forbids conversion of a likelihood difference into a compatibility label. **No local asset contains a swap, cross-reactivity or orthogonality experiment** |

Three further qualifications the bundle records and that must travel with any use:

- **Generalisation degrades with distance from training RTs.** By nearest-training-RT cosine
  quartile, R − T runs **−0.0058 (CI spans zero)** → −0.0232 → −0.0230 → −0.0319. The least-similar
  quartile is **not** adjudicated. R − G is flat across the same quartiles, which localises the
  gradient to the **T** arm rather than to relatedness leaking into R.
- **The permutation control is not flat**: P − T = −0.00590, i.e. a model trained on within-type
  *deranged* RTs still beats the type label by ~24 % of the full effect. Some benefit comes from
  conditioning on *a* real RT embedding rather than *the* right one.
- **Type remains an ncRNA-derived label** (`retron_type` is the ncRNA's own covariance model), so
  "beyond type" is measured against a label from the other modality. The G and P arms are what make
  the result meaningful despite that, since they are protein-side constructs.

Two further limitations the closure records and that bear directly on how this synthesis reads the
result:

- **X2 is INTERNAL cross-fitted confirmation, not external validation.** No new data exist; the same
  30,924-pair population underlies X1 and X2. Cross-fitting buys *coverage and robustness, not
  power* — it raised T4 coverage 83 → 247 components while n_eff moved 9.0 → 8.6; **n_eff is 12.5**
  for the full population, so pair counts overstate sample size by more than three orders of
  magnitude.
- **The similarity range is narrow.** Median nearest-training cosine is **0.987**, with even Q1
  above 0.983 — so the generalisation gradient is measured across *near* homology, not near-vs-far.
- Effect sizes are small in absolute terms throughout: **0.0017–0.0177 nats/nt**.
- The largest ncRNA clusters are **not adjudicated**; the effect is carried by small clusters.

**Explicitly NOT supported by X2** (`X2_CLOSURE.md` §6, binding): biochemical compatibility; physical
interaction or binding; functional interchangeability or **orthogonality**; causal **co-evolution**;
that any non-observed combination is incompatible or a biological negative; that the model identifies
the cognate RT at the individual-pair level; **any per-pair biological inference whatsoever**. A
counterfactual RT is a *conditioning control*, never a negative pair; an absent combination is a
*non-observed pairing*.

**Six binding requirements for any later pairing-specificity analysis** (`X2_HANDOFF.md` R1–R6):
use **C3/C4-strength** counterfactuals (same-type contrasts are ~10× easier and would overstate
specificity by an order of magnitude); evaluate at **component level**; carry **seed uncertainty**
(≥ 3 seeds; a magnitude from one seed is not a result); always report **both R − T and R − G**, since
"RT beats type" measures lineage, not pairing; keep **distance-to-training** as a primary
stratification axis; and never treat unobserved pairings as biological negatives.

**What X2 authorises:** designing a compatibility/contrastive experiment under R1–R6. **What it does
not authorise:** any compatibility label, interaction probability, pair score, AUROC against
arbitrary mismatches, or co-evolution claim. The bundle honours its own stop condition.

### 2.10a OpenCRISPR — **METHODOLOGICAL PRECEDENT, not an experimental result of this project**

This must not be read as evidence produced here. It is recorded because it is the design lineage of
X1/X2, and because conflating the two would misattribute both claims and negatives.

| | |
|---|---|
| **What OpenCRISPR did** | trained a **protein-conditioned gRNA decoder** and used **conditional RNA likelihood** to study Cas9–RNA **exchangeability** |
| **What this project did with it** | **audited the released implementation** and **adapted reusable causal-decoder / cross-attention components** (frozen protein-LM encoder → linear conditioning → bidirectional encoder layer → cross-attention decoder → autoregressive RNA head; ~0.7 M trainable parameters; two-segment sentinel vocabulary) |
| **What this project did NOT reuse** | their **training split**, their **performance claims**, and their **biological negatives**. None of those enters any grade in this map |
| **What X1/X2 therefore are** | an **OpenCRISPR-inspired retron adaptation**, **not a replication** — different molecule class, different population, different endpoint, different controls |
| **What this project added, and why** | a **component-blocked bipartite split** (RT-cluster ↔ ncRNA-cluster connected components), the **G** (homolog-representative) and **P** (within-type derangement) arms, and the **C1–C4 counterfactual hierarchy** — all introduced specifically to address **retron sequence relatedness and lineage confounding**, which a protein-identity split does not control on the RNA side |
| **What remains untested here** | there is **no equivalent experimentally measured RT–ncRNA swap / exchangeability dataset**, so **biochemical compatibility and orthogonality remain `NOT_YET_TESTED`** |

Provenance quality of the audit itself is good and self-limiting: the published methods could not be
retrieved (auth/403/429), and the audit says so explicitly — *"tier A below is almost empty, and that
is a limitation of my access, not evidence that the authors omitted anything"*. What it verified is
code- and checkpoint-level (85/85 tensors load byte-identically; SpCas9 conditioning emits the
verbatim repeat, 16/16 well-formed; MalE conditioning gives 0/64). A separate prior
retron-retargeting effort concluded *"the model does FAMILY RECOGNITION, not partner recognition"* —
that is a **prior-project result, audited and not reproduced here**, and it is cited as context, never
as this project's evidence.

**Grade: ESTABLISHED as a code/design audit and precedent; NOT AN EVIDENCE SOURCE for any biological
claim in this project.**

### 2.11 Phylogeny / co-evolution assets — **NOT_YET_TESTED** · and the door is *not* closed **[REV-1 CORRECTED]**

No phylogeny exists in this project; the contract's "phylogenetically matched" C6 rung was never
built; co-evolution has **no null for shared ancestry**. X2 supplies the strongest argument yet that
a relatedness-aware control ladder is worth building — because the effect it measures lives largely
*in* the lineage structure (G explains ~77 % of R − T). A modern label-independent phylogeny is
**NOT_YET_TESTED**, not refuted (§2.6 (iv)). ⛔ Mantel remains ruled out; PP-style block-constrained
permutation is the named alternative.

### 2.12 Terminal / fusion architecture — **UNDERPOWERED**, upgraded from NOT_YET_TESTED

Stage 3C measured what it could on 62 chains (§2.5 (f)) and, more usefully, produced **six design
requirements** for a later task: do not define the RT core by the GII-centred mapper (it truncates
N-terminally on exactly the families of interest); an insertion measure must not require anchors to
be mapped; separate expression constructs from biology by per-accession identity; carry the numbering
hazard; predicted structures stay out of scope; keep the strata and the BJ-p4 arm. Corpus-scale
fusion remains untested.

### 2.13 Neighbouring / accessory proteins — **NOT_YET_TESTED** · wording corrected **[REV-1 CORRECTED]**

All 41,250,531 accessory CDS carry `has_sequence = False`; effector information exists only as
PADLOC *rule definitions*; operon figures are illustrative and support no rate. Revision 1's thesis
sentence asserted that neighbourhood "does not carry retron identity". **That was wrong as stated:**
what was tested (in a prior project, `[UNVERIFIED]` here) is that neighbourhood composition is a poor
*discriminator* — retrons rank **27th of 41** RT families on defence-accessory carriage, 53.50 % vs
45.36 % neighbour-matched, fold 1.179 [1.161, 1.198], inside a predeclared `DEAD` band. That is a
statement about **detection**, on **one modality**, from **unverified prior work**. It is not a
finding that neighbourhood architecture is uninformative about retron biology, which has never been
measured here.

### 2.14 ncRNA boundary prediction — **NOT_YET_TESTED**, now with inherited features

Comparative recovery remains **FAILED** (±20 nt: 0–17.5 % Round 1, 0 % Z6, 60/1,051 Round 2; median
5′/3′ error 29.5/37 nt). What is new is that the two SPIRE post-mortem features (§2.7) are the right
*inputs* to a supervised boundary task, and the panel's 175 published extents are the only non-CM
truth — of which, by the exposure map below, a usable subset must be selected deliberately.

### 2.15 The experimental panel — **REGISTERED, with an exposure map** · **NEW**

`PANEL_LEAKAGE_MAP.tsv` (175 rows) joins the panel to every project population by **exact sequence
hash** under the project's own rules (`rt_seq_hash` = sha256 of the uppercased protein with one
trailing `*` removed; `nc_seq_hash` = sha256 of the uppercased oriented sequence; both orientations
tried on the ncRNA side). Near-sequence exposure is **not recomputed** — it is read from the SPIRE
audit's existing blastn.

| exposure class | n | meaning |
|---|---|---|
| `TRAIN_EXPOSED` | **58** | an exact RT/ncRNA/pair of this element is in the X1 train fold |
| `VAL_TEST_EXPOSED` | **33** | in the val (18) or test (15) fold |
| `CATALOGUE_ONLY` | **56** | in the corpus, but not as a PAIR-ELIG pair |
| `SEQUENCE_NEAR_CORPUS` | **12** | no exact hash match; a ≥ 90 % id / ≥ 80 % length blastn match exists |
| **`FULLY_EXTERNAL`** | **16** | no exact and no near match anywhere |

Supporting counts: **175/175** rows carry a Mestre accession (the panel is entirely inside Mestre's
reference set); **145/175** RTs are in the 501,561 exact-RT catalogue; **88/175** RTs and **12/175**
ncRNAs are in PAIR-ELIG; **9/175** exact pairs are in PAIR-ELIG; **80/175** have a ≥ 90 % blastn
ncRNA match. **For `embed_x2` there is no untouched fold** — X2 cross-fits all five folds, so every
one of the 91 split-present elements is X2-exposed.

**Final X2 overlap interpretation.** X2 cross-fits **all five folds**, so every one of the 91
split-present elements was trained on in some cell; there is **no untouched holdout inside
PAIR-ELIG**, and the panel cannot supply one retrospectively. Combined with the closure's own
limitation — *"INTERNAL cross-fitted confirmation, not external validation"* — the position is:
**nothing in the panel validates X1 or X2**, and the 16 fully-external elements do not change that,
because external status is a statement about *sequence overlap*, not about endpoint.

Three readings follow, and the third is the one most easily got wrong:

1. **The panel is not independent validation of anything in this project**, and must not be called
   that. Its RT side in particular is almost entirely inside the catalogue (145/175).
2. **The low exact-ncRNA match (12) beside the high blastn match (80) is itself a result**: the
   published boundary and the covariance model's cut rarely coincide exactly — precisely the quantity
   a boundary task needs, measurable on the ~95 non-train-exposed elements.
3. ⛔ **The 16 fully-external elements are NOT a compatibility or orthogonality validation set.**
   They carry **functional measurements** — RT-DNA production, editing rates — **not RT–ncRNA
   exchangeability labels**. Nothing in the panel says which *non-cognate* ncRNA an RT would or would
   not use, and X2's endpoint (conditional likelihood of the observed ncRNA) is a different quantity
   again. Using them to "validate pairing specificity" would silently swap the endpoint.

**A future opportunity worth preserving, stated at its correct endpoint.** The panel *may* provide
**external functional validation of RT-DNA production or editing-related predictions** — a
prospective analysis in which a model trained on sequence predicts a measured functional outcome on
elements outside its training exposure. That is a legitimate and valuable use of the 16 external (and,
with care, the 56 catalogue-only) elements. **It is a different endpoint from orthogonality**, it
requires its own preregistration, and it must not be presented as evidence about pairing
specificity.

Functional measurements are preserved unchanged in `EXPERIMENTAL_RT_NCRNA_REGISTER.tsv`: **81**
empirically determined RT-DNA sequences; RT-DNA production measured for 103 with **67 > 0**; human
editing > 0 for **100**, bacterial **27**, phage **16**; 31 elements synthesised and tested with
outcome undetermined — a genuine negative population.

---

## 3 · Contradictions, circularities and framing problems (revised)

**C-1 · The retron axis is one annotation lineage** — unchanged and still first. 21 Mestre-authored
CMs → PADLOC rules → DefenseFinder profiles → MyRT labels → g6's grouping → the embeddings' "retron
type". **Corrected wording:** this is a statement about **how the population was defined and how
evidence is (non-)independent**, not a claim that annotation lineage is a biological determinant of
what a retron is. Revision 1 blurred that line.

**C-2 · Stage 3B is labelled PARTIAL but stopped on a fired kill criterion**, with an unreachable
PASS branch and two superseded claims frozen in a landed README — and Stage 3C has now inherited the
label. See `TIER0_REPAIR_TABLE.md` T0-1/T0-2.

**C-3 · X1's prose omits its own adverse weighting** (pooled −0.00066 vs component-mean −0.01778).
X2 does not inherit this defect — it aggregates token-weighted within component and bootstraps over
components — but X1's narrative files are still cited in the reporting workbench (T0-4).

**C-4 · Two circular positive controls** (Ec107-like carriage 98.6 %; SPIRE's per-type positional
prior scored against the CM boundary it came from). Unchanged.

**C-5 · Stage 3B supplied Stage 3A's population.** Unchanged; Stage 3C inherits the same 62 chains
and states the transition where family labels enter.

**C-6 · Held-out material has been opened repeatedly**, and X2 makes this structural rather than
incidental: the embedding population's every fold is now trained on. There is no untouched holdout
left in PAIR-ELIG. Any future confirmatory test must use an external population — which is exactly
what the 16 fully-external panel elements are, and 16 is small.

**C-7 · Prior-project numbers circulate in planning documents.** Unchanged; `VOID_DO_NOT_CITE.md`
applies.

**C-8 · A missed criterion was not declared a failure** (MCC-v3.1 extractability 82.1 % vs ≥ 90 %).
Unchanged.

**C-9 · `human_input_audit: PENDING` everywhere**, including the Stage-2 final reporting package
(`46414f4`) and Stage 3C. Nothing has cleared it.

**C-10 · NEW — the literature itself is not a consistent reference.** Two 2026 papers on the same
retron protein publish incompatible fingers/palm/thumb partitions in the same numbering frame; the
inherited boundary product is RED on its own files (fingers and thumb are arithmetic residuals in
**25/25** rows; a hardcoded anchor; self-warnings that gate nothing; the **5G2X palm excludes that
chain's own catalytic aspartate**; the same Ec86 protein receives boundaries differing by 77
residues). Any claim that uses literature domain boundaries as truth is building on sand, and Stage
3C is right to keep it as its own stratum.

---

## 4 · The "977" set — verdict unchanged

It does not exist on this machine; no local document attributes one to Mestre 2020; nearest
candidates (1,216 / 936) are CM calls with `validated_ncrna` true for only **165**. No filter of the
Mestre table yields 977. The real experimental basis is the 175-element panel, **as bounded by
`PANEL_LEAKAGE_MAP.tsv`**.

---

## 5 · What a skeptical reviewer would accept today (revised)

| statement | accept? | change from rev 1 |
|---|---|---|
| A 501,561-sequence exact-RT catalogue on explicit units | **yes** | — |
| A frozen mapper validated on one fresh lineage, applied to 369,381 proteins | **yes, with its scope sentence** | — |
| `CAT_STATE 262` sits 2 residues before the catalytic Asp in 17/17 structures | **yes** | **new** — independent cross-instrument agreement |
| Catalytic *location* is a reproducible architectural landmark (19/19 single unit; 13/14 replicate-stable) | **yes, on non-retron chains only** | **new** |
| RT chains decompose into three reproducible compact units | **no** | — |
| The *literature* pins down fingers/palm/thumb | **no** — 0/11 fingers coincide; references contradict each other | **new** |
| Broad RT-lineage information predicts the cognate ncRNA | **yes** | **upgraded** |
| The exact RT adds information beyond its 50 %-id homolog group | **yes in sign, no in magnitude** (R − G −0.0055, seed sd 0.0051, sensitivity arm spans zero) | **upgraded from "failed"** |
| The model can pick the right partner among near neighbours | **no** — C3 is 52.5 % of pairs; rung 3 fails | — |
| Biochemical compatibility or co-evolution | **no — never tested** | — |
| Retron Region Y is a universal diagnostic motif | **no** — absent in all 6 Eco8 chains, present in 4 non-retrons | **new** |
| A motif-blind geometric rule identifies the catalytic site | **no** — in-sample only, K5 fired | — |
| Mestre's classification is reproducible / independently validated | **no** | — |
| Placement into the historical 11-clade system is currently possible | **no** — K3 failed | **sharpened** |
| A modern label-independent RT phylogeny would fail | **not supported either way — never attempted here** | **[REV-1 CORRECTED]** |
| Novel retron ncRNAs can be discovered de novo by covariation | **no — falsified on held-out data** | — |
| The SPIRE positional prior and ~90-nt submotif are useful features for a boundary model | **yes, as features evaluated against non-CM truth** | **[REV-1 CORRECTED]** |
| Neighbourhood composition is uninformative about retron biology | **no — that was never tested**; only its use as a *discriminator* was, in prior work | **[REV-1 CORRECTED]** |
| The 175-element panel is independent validation | **no** — 16/175 fully external | **new, measured** |
