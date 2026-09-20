# OPEN QUESTIONS

Only genuinely unresolved scientific questions. Each is filed under **one** of four kinds, because
they demand different responses:

| kind | meaning | correct response |
|---|---|---|
| **A · MISSING DATA** | the evidence needed does not exist locally (or at all) | acquire it, or state the limit permanently |
| **B · UNDERPOWERED** | the analysis ran but could not adjudicate | power it, or report it as undetermined — **never as a null** |
| **C · NOT YET TESTED** | never attempted here | design it, preregistered |
| **D · FAILED — do not reopen without new evidence** | tested against a predeclared criterion and refuted | leave closed; name what new evidence would change it |

---

## A · Unresolved because the data does not exist

**A1 · What were the historical RT0 and RT1?**
The defining source (Malik, Burke & Eickbush 1999) **is not held**, no held source states a residue
boundary for them, and the frozen anchors reach only LtrA 97–363 — so 0 of 62 experimental
structures carry any RT0/RT1 state. *Changes only with primary historical evidence. No inferential,
analogical or structural resolution is permitted.*

**A2 · Can Mestre's classification be diagnosed rather than merely failed?**
Her **alignment and RT0–RT7 extracts are not published and not on disk**, so the re-inference failure
cannot be localised. *Changes only if the original alignment surfaces.*

**A3 · Is there a boundary truth set at usable scale?**
The assumed **977-element validated ncRNA set does not exist** on this machine (two independent
searches; nearest candidates are CM calls with `validated_ncrna` true for only 165). The only
non-CM truth is **175 published extents**, of which 58 are train-exposed. *Changes by acquiring
published boundary data, or by accepting n ≈ 95.*

**A4 · How specific is an RT for its own ncRNA, biochemically?**
**No swap, cross-reactivity or orthogonality experiment exists in any local asset.** Variant-library
and engineering papers are on disk as **PDFs only**. This is why `C-30` is `NOT_YET_TESTED` and
cannot become anything else computationally. *Changes only with measured exchangeability data.*

**A5 · What surrounds these RTs?**
**All 41,250,531 accessory CDS carry `has_sequence = False`**, and the local Pfam/InterProScan is a
stub (3–4 profiles). *Changes with a neighbourhood parse plus the full Pfam-A registered on Ibex.*

## B · Unresolved because the analysis is underpowered

**B1 · How large is the exact-RT residual beyond lineage?**
R − G = −0.00551 [−0.00797, −0.00312], **same sign on 3/3 seeds but ranging −0.0055 to −0.0156**
(sd 0.0051 ≈ the point estimate), and the near-duplicate sensitivity arm **spans zero**. The sign is
established; the magnitude is not. *Needs ≥ 3 seeds averaged within component, per `X2_HANDOFF` R3.*

**B2 · Does any partner information survive against near neighbours?**
C3 gives +0.00397 at component level but **52.5 % of pairs** and a raw pair-level mean of
**−0.000205**; C4 is +0.00168 over 451 components. *Needs a C3/C4-strength design with a declared
magnitude floor — and a confirmatory population, which does not currently exist (see D-note below).*

**B3 · Does the effect generalise to unlike RT lineages?**
The least-similar quartile is **not adjudicated**: R − T −0.00584, CI spans zero. And the whole
similarity range is narrow (median nearest-training cosine 0.987). *Needs a genuinely distant
evaluation set.*

**B4 · Is retron subtype structure recoverable without labels?**
g6's label-free within-Retron arm is `UNDERPOWERED`; **26 of 50** subtype strata never entered a
distance matrix.

**B5 · Is Region Y actually involved in pairing?**
A location ratio of **1.34×** over 15 chains from five groups (range 0.59–1.86), against 1.06 over
three non-retron chains, plus a classical reciprocal-fragment experiment covering exactly **two**
retrons. *The declared join of `XY_REGION_ANNOTATIONS.tsv` (rt_hash-keyed) to the modelling dataset
is the natural next test, and Stage 3C deliberately left it out of scope.*

**B6 · Retron catalytic architecture.**
Untouched: all 19 truth-bearing Stage-3B chains are **non-retron**, and Tier B never opened. A
Tier-B appendix (5 chains, 3 retron, exploratory) is proposed but unauthorised.

## C · Not yet tested

**C1 · A modern, label-independent de novo RT phylogeny.**
Never attempted in this project. ⚠️ Do **not** treat the failures of Mestre *reproduction* (C-18) or
of *placement* into the 11-clade system (C-19) as evidence about this — they are different questions
with different inputs. The untried representation is the **structural** one: an all-vs-all distance
matrix over 1,919 proteins that has never been built as a tree.

**C2 · Co-evolution of RT and ncRNA beyond shared ancestry.**
No phylogeny, therefore **no null for shared ancestry**. ⛔ Mantel tests are ruled out; use a
PP-style block-constrained permutation.

**C3 · Corpus-scale effector, fusion and operon architecture.**
Blocked by A5. Stage 3C already supplies six binding design requirements for whoever runs it.

**C4 · Supervised ncRNA boundary prediction.**
Feasible only as **boundary-disagreement characterisation** today (≈ 95 non-train-exposed published
extents), with the SPIRE positional features as priors — which may never be evaluated against CM truth.

**C5 · Prospective external functional validation.**
Can a sequence-derived model predict **RT-DNA production or editing** on panel elements outside its
training exposure? Legitimate, preregisterable, and a **different endpoint from orthogonality**.

**C6 · What confirmatory population remains for any pairing follow-up?**
`embed_x2` cross-fits **all five folds**, so **no untouched holdout remains inside PAIR-ELIG**. The
only external material is the **16 fully-external** panel elements — and they carry functional, not
exchangeability, labels. *This must be declared before, not after, the next model is designed.*

## D · Failed — do not reopen without new evidence

| question | why closed | what would reopen it |
|---|---|---|
| Three-way fingers/palm/thumb decomposition as a contact-density partition | 0.565 < 0.70; 22/22 LOGO folds FAIL; literature fingers coincide 0/8; references contradict each other | a parser-independent decomposition clearing the bar, or a demonstration that the thresholds (not the parser) caused the failure — `1RTD_A` is the test case |
| De novo comparative ncRNA discovery | `ROUND2_FAIL_STOP`; a fixed interval beats the method 901 vs 343; the released package performs at chance | a method that beats the positional prior on held-out loci |
| Placement into the historical 11-clade system | K3: shuffled queries confidently placed at 7.9 % vs a ≤ 1 % limit; LWR shuffled median 0.998 | a confidence statistic that separates shuffled from real input |
| Re-inference of Mestre's classification | ≤ 3 of 11 clades; substitute contamination; no positive control | recovery of the original alignment (see A2) |
| Neighbourhood as a retron **detector** | retrons 27th of 41 families, inside a predeclared DEAD band | nothing — but this says nothing about neighbourhood **biology**, which is C3 |
| The "977 validated ncRNA" set | does not exist; two searches agree | production of the file with stated provenance |
| Stage-2 analysis generally | closed with six residual limitations | a new decision record and a new task |

## Process questions currently blocking promotion

These are not scientific, but nothing can be promoted until they are answered.

1. **Stage 3B's "CLOSED at PARTIAL" label** misdescribes a kill-criterion stop, and Stage 3C has
   inherited it. Repair is specified, unapplied.
2. **Stage 3C's five required re-runs (R1–R5)** are specified but **not authorised**; until then no
   Stage-3C number may be promoted and rows S05, S11, S12 and the Region-X part of S16 stay withdrawn.
3. **X1's prose** reports one weighting; its own table carries pooled −0.00066 and pair-weighted
   +0.00486.
4. **`embed_g2`'s inert baselines** mean a README sentence describes a test that never ran.
5. **Two circular positive controls** in the Stage-1 extended report.
6. **`human_input_audit: PENDING`** on every bundle — governance requires it before any number
   becomes a thesis or paper claim.
