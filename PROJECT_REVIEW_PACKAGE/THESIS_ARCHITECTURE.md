# THESIS ARCHITECTURE

A proposed chapter structure that keeps four things visibly apart: **established findings**,
**failed hypotheses**, **methodological development**, and **prospective work**. Nothing here is a
decision; it is a layout the evidence can actually carry.

The governing constraint: **`human_input_audit` is PENDING on every bundle**, and governance requires
it before any number becomes a thesis claim. Chapters are therefore "writable" in the sense of
"the evidence exists and is bounded", not "cleared".

---

## Part I — The object

### Ch 1 · What a retron is, three ways
Established as framing, not as a result. Retrons as historically annotated (an annotation lineage
that can be traced precisely), as molecular systems (an RT that with its cognate ncRNA produces
msDNA — experimentally defining, and **not predictable from sequence alone**), and as an operational
genome-scale detection problem (a multi-axis profile, not a boolean). Source: `WHAT_IS_A_RETRON.md`.

### Ch 2 · From mining records to biological objects — **ESTABLISHED**
The unit ladder and why no two units convert by a constant; coordinate integrity at 99.47 % with 618
mismatches retained; the analytical objects that every later chapter uses. Source: `dbchar_g1–g4`.

### Ch 3 · Annotation limits as a measurable object — **ESTABLISHED (methodological)**
The strongest publishable material in the project: ncRNA carriage swings **6.6-fold** with the tool
combination; 47.24 % of retron loci have no detected ncRNA and that is detector scope; DefenseFinder
and PADLOC subtypes agree on 43.85 %; two artefact dissections (the 2,682 bp downstream mode; a
shipped field that fails all 12 candidate reference frames). Source: `dbchar_g6`, `g3`, `g7b`
(**fix the two circular positive-control claims first**).

## Part II — Methodological development

### Ch 4 · A frozen residue-level instrument for RT conserved states — **METHOD**
Design, failure-driven redesign, freezing, and application to 369,381 proteins; what a
`REPRODUCIBLE` bundle and a versioned instrument buy. Carries its scope sentence everywhere:
`-M 50` only, one fresh lineage, GII-centred frame. Source: `rt07_g1–g5`, `g4b`.

### Ch 5 · What RT0–RT7 can and cannot mean — **ESTABLISHED (bounded) + a clean negative**
Of 32 region names, one has a stated residue boundary; the seven-way partition is not established
(block-count null p = 0.6965); four labels get LtrA-local operational correspondence, two are
partial, and **RT0/RT1 are UNRESOLVED for historical *and* instrumental reasons**. Stage 3C adds that
0 of 62 experimental structures carry RT0/RT1 states, and that the state blocks **merge** into one
structural unit rather than separating. Source: `rt07_g7a` + binding erratum; Stage 3C Comparison B.

## Part III — Failed hypotheses (a chapter, not a footnote)

### Ch 6 · Domain architecture does not decompose as convention assumes — **FAILED**
Palm-like called in 0.565 of 46 chains against a 0.70 bar; 22/22 LOGO folds fail; the PDP partition
is itself unstable (0.385). And the complementary finding: the **literature does not pin these
regions down either** (fingers coincide 0/8; two 2026 papers on the same protein publish
incompatible partitions; the inherited boundary product is RED on its own files). Honest limitation:
no biological positive control — HIV-1 RT is itself AMBIGUOUS, so thresholds share the blame with the
parser.

### Ch 7 · Catalytic geometry, and what a fired kill criterion taught us — **STOPPED**
In-sample calibration only (13/19; LOCO 12/5/2); the decoy-sufficiency criterion fired at 23 vs 60;
Tier B was never opened and its PASS branch was unreachable. A chapter about **why a stop rule is
worth having**, and about the mislabel that followed. *Requires the Stage-3B relabel first.*

### Ch 8 · Historical classification: reproduction, placement, and what is still open — **FAILED (twice), with a distinction**
Mestre's published objects re-join; re-inference fails (≤ 3 of 11 clades, substitute contamination,
no positive control); **placement into the 11-clade system fails its shuffled-query control (7.9 % vs
≤ 1 %)**. The chapter's point is the distinction: none of this touches a **modern, label-independent
de novo phylogeny**, which has never been attempted.

### Ch 9 · De novo ncRNA discovery — **FAILED**, with two features inherited
`ROUND2_FAIL_STOP`; a fixed positional interval beats the method 901 vs 343. What survives is a
retron-enriched ~90-nt submotif and a type-conditioned positional prior — **priors for a boundary
model, never their own validation**, since both are CM-derived.

## Part IV — The pairing question

### Ch 10 · RT–ncRNA correspondence: lineage, residual, and the limit — **the project's main positive result**
Drafted material already exists: `…_v7-embedding-report/analysis/embedding_report/` at **`d7d3ece`**
supplies the Methods and Results prose, the 29-claim reporting matrix, and figures **F8/F9/F10**.
⛔ The chapter is written around *"supported only with its qualifier attached"*, and **`X2-A` never
appears as a biological conclusion** — it is a gate label; the conclusion of record is the qualified
paragraph. Structured exactly at the four levels, never as PASS/FAIL:
1. **lineage** — G − U −0.04256 [−0.04619, −0.03893], 86.0 % of components;
2. **exact-RT residual** — R − G −0.00551 [−0.00797, −0.00312], sign replicated on 3/3 seeds,
   magnitude undetermined (sd ≈ estimate), homolog group explaining ~78 % of R − T;
3. **pair discrimination** — C1 +0.0177 → C4 +0.0017; at C3, 52.5 % of pairs and a raw pair-level
   mean of −0.000205;
4. **biochemical compatibility** — untested, and untestable with current assets.
With the permutation control (not flat: P − T −0.00590), the generalisation gradient (least-similar
quartile spans zero), the pair-versus-component weighting (at C3 the two **differ in sign**), and
replication across all 5 folds and all 3 seeds.

**§1.4 · OpenCRISPR as precedent** — a six-point drop-in subsection already drafted at `d7d3ece`:
what they did (a ~0.7 M-parameter protein-conditioned gRNA decoder, plain next-token loss, **no**
contrastive term, validated *functionally*); what was reused (`transformer.py` at a pinned sha256,
architecture shape, capacity class, objective, optimiser, frozen-encoder pattern); what was rejected
(their checkpoint weights, ESM2 8M, the sentinel vocabulary, their split, and **any** OpenCRISPR
sequence); what was reproduced (the *question*, turned from a qualitative demo into a graded
statistical experiment) — **an adaptation, not a replication**; why the design is component-blocked
and lineage-controlled (one ncRNA has **705** RT partners; the homolog representative alone gives
~78 % of the gain); and why their exchangeability validation **cannot** be reproduced here — there
are no experimentally labelled compatible/incompatible RT–ncRNA combinations, which makes acquiring
them a **precondition**, not a refinement.

## Part V — Prospective

### Ch 11 · The experimental layer and what it can support
185-row register: 81 empirically determined RT-DNA sequences, 67 elements producing RT-DNA, 100/27/16
editing phenotypes, 31 tested-but-undetermined, 8 deposited complexes — and the **exposure map** that
bounds all of it (only 16 of 175 fully external). Includes the honest statement that the field's
question — *how specific is an RT for its own ncRNA?* — has **no local experimental ground truth**.

### Ch 12 · Minimum remaining programme
Tier-0 repairs; a declared confirmatory population; a relatedness backbone; the Region-Y × exact-RT
join; boundary-disagreement characterisation. And what should stay closed.

---

## Mapping chapters to status

| status | chapters |
|---|---|
| **ESTABLISHED** | 2, 3, 5 (bounded), 10 level 1 |
| **SUPPORTED_WITH_LIMITATIONS** | 4, 10 level 2 |
| **FAILED / STOPPED** | 6, 7, 8, 9, 10 level 3 (as a bounded negative) |
| **METHODOLOGICAL** | 4, 7, and the instrument thread running through 2–5 |
| **PROSPECTIVE** | 11, 12, 10 level 4 |

**A note on ordering.** The failed chapters are placed together and early rather than buried,
because the thesis's distinctive contribution is that four independent instrument families were each
pushed to a predeclared criterion and each stopped at the same boundary — type- and lineage-level
structure is recoverable; pair- and partition-level structure is not. That is a result about where
the information lives, and it only reads as one if the negatives are visible.
