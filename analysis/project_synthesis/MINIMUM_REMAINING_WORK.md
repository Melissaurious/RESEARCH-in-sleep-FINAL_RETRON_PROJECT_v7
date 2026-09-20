# MINIMUM REMAINING WORK — revision 2

**Revision 1's ranking is withdrawn.** Two results landed after it (`embed_x2` — results `4f8550b`,
**closure `fdf0872` governing**; Stage 3C `34000ee`), and two of revision 1's adjudications were wrong: it closed sequence-tree routes on
evidence that does not support closure, and it treated the SPIRE post-mortem as disposable.

Nothing below is authorised by this document. No compute has been started. Tier 0 is unapplied and
itemised for sign-off in `TIER0_REPAIR_TABLE.md`.

---

## Tier 0 · Zero-compute repairs (unchanged, still first)

Eight repairs, itemised in `TIER0_REPAIR_TABLE.md` with affected file, affected claim, whether they
change scientific status or only wording, and supporting evidence. **Status-changing: T0-1 (Stage-3B
relabel), T0-5 (inert baselines), T0-7 (circular positive controls), and T0-4 (X1's reported effect
size in prose).** Sign-off needed on those four; the rest are provenance.

One escalation since revision 1: **Stage 3C has now inherited the "3B CLOSED at PARTIAL" label**, so
T0-1 is no longer cosmetic — the mislabel is propagating into a freshly packaged bundle.

---

## Tier 1 · Approved, and decisive

### 1.1 Declare the confirmatory population for any pairing follow-up — **APPROVED, no compute** · NEW

X2 cross-fits all five folds, so **no untouched holdout remains inside PAIR-ELIG**. Any future
compatibility or contrastive experiment has nowhere to be confirmed. This must be fixed *before*
design, not after: freeze a component block now, and/or designate the **16 fully-external** panel
elements (`PANEL_LEAKAGE_MAP.tsv`). Sixteen is small — say so in advance rather than discovering it
at review. **Decision required: yes.**

### 1.2 The predeclared rung-0 positive control — **APPROVED** (carried from rev 1)

Boundary-trimmed true ncRNA must rank top. Predeclared, never run; governance requires a positive
control before absence-flavoured statements, and the retrieval track has none of its own. Cost: low.

### 1.3 A relatedness backbone for permutation controls — **APPROVED** (strengthened by X2)

X2 makes this more valuable, not less: the effect it measures lives largely **in** lineage structure
(G − T = −0.019 of R − T = −0.025, i.e. the homolog group explains ~77 %). Build an
identity/ANI-based **blocking structure for PP-style block-constrained permutation** — explicitly not
a publication tree. ⛔ Mantel stays ruled out. **Decision required: yes.**

### 1.4 Region Y × exact-RT residual — the declared join — **APPROVED as a bounded, preregistered analysis** · NEW

The single most interesting link the two new results create. Stage 3C measured **1.34×**
RNA-contact enrichment in Region Y (median, range 0.59–1.86, n = 15 retron chains) and deliberately
left the join out of scope, publishing `XY_REGION_ANNOTATIONS.tsv` with `rt_hash` so a later governed
task can perform it. X2 found a small exact-RT residual beyond homolog group. The testable question:
**is the residual carried by Region Y?**

Conditions: the six binding requirements of `X2_HANDOFF.md` (R1–R6) apply in full — C3/C4-strength
counterfactuals, component-level inference, ≥ 3 seeds with the across-seed spread reported, **both
R − T and R − G** (reporting only "RT beats type" measures lineage, not pairing),
distance-to-training as a primary stratification axis, and no treatment of unobserved pairings as
biological negatives. **Do not run it as an exploratory sweep** — n = 15 annotated retron chains is small, and the
structural and modelling populations overlap only partially. **Decision required: yes.**

---

## Tier 2 · Approved in reduced form

### 2.1 Modern label-independent RT phylogeny — **REOPENED** [REV-1 CORRECTED]

Revision 1 closed this. **That closure is withdrawn**, because it imported the failure of a
*historical-placement* instrument (M2a/K3) and of *prior-project* sequence-tree routes into a
question neither addressed. Three distinct things:

| question | status | verdict |
|---|---|---|
| reproduce Mestre's classification | **FAILED** (alignment unrecoverable) | closed, correctly |
| place sequences into the historical 11-clade system | **FAILED on K3** (shuffled at 7.9 % vs ≤ 1 %) | closed as an instrument |
| **a modern de novo label-independent phylogeny** | **NOT_YET_TESTED** | **open** |

**Approved:** a preregistered de novo attempt with declared criteria and both answers reportable,
*after* 1.3 (the backbone is the cheaper, more broadly useful half). The untried structural
representation — an all-vs-all distance matrix over 1,919 proteins that has never been built as a
tree — remains the distinctive angle. **Not approved:** repeating the prior sequence routes as they
were run.

### 2.2 ncRNA boundary work — **REFRAMED and now better resourced** [REV-1 CORRECTED]

Revision 1 rejected supervised prediction for want of truth, and dismissed the SPIRE post-mortem.
Two corrections:

- The post-mortem yields **two legitimate features**: a retron-enriched ~90-nt internal submotif
  (1,793 instances; retron 85 % vs non-retron 52.5 %; Fisher p = 1.0e-7, OR 5.3) and a **strong
  RT-relative, type-conditioned positional prior** (per-type 969 = 92.2 % at IoU ≥ 0.5 vs the
  method's 343). They are **features/priors**, not discoveries, and they are CM-derived — so they
  may never be *evaluated* against CM truth.
- The panel gives the only non-CM truth: 175 published extents, of which **58 are train-exposed** and
  33 val/test-exposed, leaving ~95 not train-exposed. And the **exact-hash (12) versus blastn (80)
  gap is itself the measurable quantity**: published extent versus CM cut.

**Approved:** characterise boundary disagreement on the non-train-exposed extents, using the SPIRE
features as priors, evaluated against the published extents.

**Separately preserved opportunity (different endpoint).** The panel may support **external
functional validation of RT-DNA production or editing-related predictions** on elements outside a
model's training exposure. That is legitimate, valuable and preregisterable — and it is **not**
orthogonality or compatibility validation. The 16 fully-external elements carry functional
measurements, **not RT–ncRNA exchangeability labels**. **Still not approved:** a supervised
predictor without a declared MDE at this n.

### 2.3 Stage 3C follow-ups — **APPROVED: promotion decision only; no new comparisons**

Stage 3C is complete and issues no verdict. What remains is an operator promotion decision
(`CLAIM_EVIDENCE_MATRIX.tsv` marks every statement "after operator review") and the X12 question
(whether Tier-B/C truth may be admitted descriptively). **Recommended:** promote the
catalytic-localisation and block-merging censuses; **leave X12 at its default** so Comparison A stays
retron-free, because Tier B never opened. Revision 1's "run Comparison C only" is **obsolete** — C
has run.

---

## Tier 3 · Blocked, then worthwhile

### 3.1 Neighbouring / accessory-protein architecture — **BLOCKED, then approved**

Blocker unchanged: **all 41,250,531 accessory CDS have `has_sequence = False`**, and local
InterProScan/Pfam is a stub (full Pfam-A 37.0 is registered on Ibex). Conditions carried: annotate by
**≥ 2 independently provenanced routes** and show they *can* disagree; treat the result as
**description, not detection** — prior work already put retrons 27th of 41 families as a
discriminator. **Wording correction from rev 1:** that prior result does *not* show neighbourhood is
uninformative about retron biology; it shows one modality does not discriminate. **Decision required:
yes (Ibex).**

### 3.2 Terminal / fusion architecture — **CONDITIONALLY APPROVED**, with Stage 3C's requirements binding

Stage 3C upgraded this from untested to **UNDERPOWERED** and produced six design requirements that
any later task must inherit: do not define the RT core by the GII-centred mapper (it truncates
N-terminally on exactly the families of interest — 39/62 chains); an insertion measure must not
require anchors to be mapped (the declared gap rule found no insertion ≥ 20 aa while the instrument's
own runs reach **774** residues); separate constructs from biology by per-accession identity; carry
the numbering hazard; predicted structures stay out of scope; keep the strata and the BJ-p4 arm.

---

## Tier 4 · Rejected, or left as recorded negatives

| task | verdict | reason |
|---|---|---|
| **Conditional cross-pair scoring (n×n compatibility matrices)** | **STILL REJECTED** | X2 makes this *more* clearly premature, not less: the effect decays ~10-fold from C1 to C4 and at C3 only **52.5 % of pairs** favour the observed RT. A cross-pair matrix built now would encode lineage similarity. X2's own decision record forbids it explicitly |
| **Laboratory candidate prioritisation** | **STILL REJECTED** | Requires pair-level discriminability (not demonstrated) and a non-circular score (none). The census paper's own finding — RT-DNAs are **not predictable from sequence alone** — is the direct warning |
| **Any compatibility/contrastive model today** | **REJECTED for now** | X2 authorises *designing* such an experiment against C3/C4-strength controls; it does not authorise running one, and the confirmatory population does not yet exist (1.1) |
| **Phylogeny-corrected co-evolution** | **REJECTED for now** | Downstream of 1.3 and 2.1. No null for shared ancestry exists; the prior co-variation result was **V = 1.0000 by construction** |
| **Reopening SPIRE de novo discovery** | **REJECTED** | `ROUND2_FAIL_STOP`; a fixed interval beats the method 901 vs 343. The *features* are inherited (2.2); the discovery branch stays closed |
| **Re-running the g6 rank statistic** | **REJECTED** | Frozen as reported; per-half vectors not landed |
| **Any further Stage-2 analysis** | **REJECTED** | Closed with six residual limitations |
| **New Stage-3A/3B comparisons** | **REJECTED** | 3A closed at FAIL, 3B stopped on K5, 3C complete. Nothing is pending except promotion |

---

## What can be closed permanently (revised)

| closed | on what evidence | what is explicitly NOT closed |
|---|---|---|
| De novo comparative ncRNA **discovery** | held-out `ROUND2_FAIL_STOP`; positional prior beats the method | the **features** it produced, which are inherited by boundary work |
| **Reproduction** of Mestre's classification | alignment and extracts unrecoverable | nothing else about phylogeny |
| **Placement** into the historical 11-clade system | K3 failed; no validated discriminator | **de novo label-independent phylogeny, which is untested** |
| Neighbourhood as a **detector** | retrons 27th of 41, predeclared `DEAD` band | neighbourhood as **description**, never measured |
| The three-unit decomposition **as a contact-density partition** | 0.565 < 0.70; 22/22 LOGO FAIL; literature 0/11 fingers | fold-level fingers/palm/thumb as descriptive vocabulary with a named reference |
| RT0/RT1 as operational coordinates | 0 anchors in LtrA 1–85 / 39–61; **0/62 structures** | RT0/RT1 as historical concepts |
| The "977 validated ncRNA" set | does not exist; two searches agree | the 175-element panel, now mapped |
| Stage 2; Stage 3A; Stage 3B; Stage 3C | each closed on its own record | the promotion decisions they leave open |

## The minimum programme, in order

1. **Tier 0** — no compute; four items need sign-off.
2. **1.1** declare the confirmatory population (no compute, but blocking for everything downstream).
3. **1.2** rung-0 positive control · **1.3** relatedness backbone.
4. Write **Option C**; assemble **Option C2** after T0-1.
5. **1.4** the Region-Y × exact-RT-residual join, preregistered.
6. Write **Option B** at the four-level claim.
7. **2.2** boundary disagreement on non-train-exposed extents · **2.1** de novo phylogeny, preregistered.
8. **3.1** neighbour annotation on Ibex, then **3.2** fusions.

That is **four compute items** (1.2, 1.3, 1.4, 2.2) before the two blocked Ibex items — with 2.1 as a
separate preregistered decision. Revision 1 said three; the difference is that a genuine positive
result now exists to build on, and a question it wrongly closed has been reopened.
