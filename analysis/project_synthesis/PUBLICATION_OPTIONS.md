# PUBLICATION OPTIONS — revision 2

**Revision 1's ranking is withdrawn and re-derived**, because two results landed after it: `embed_x2`
(results `4f8550b`, **closure `fdf0872` — governing**) and the closed Stage 3C (`34000ee`). The Nature Microbiology classification-style paper
remains a **conceptual comparator only**.

Revision 1 ranked C ≫ B ≫ A and recommended writing C first. **Revision 2 keeps C first but for a
different reason, and materially upgrades B.** The re-derivation is below, and it is done by asking
what each paper's central claim would now be — not by fitting a paper to the analyses that exist.

Constraints that apply to every option, unchanged:
- **`human_input_audit: PENDING`** on every bundle, including the Stage-2 final reporting package
  (`46414f4`) and Stage 3C. It must clear before a number becomes a paper claim.
- Anything from `idea-stage/programme/` or a prior project is `[UNVERIFIED]` and must be re-derived.
- The Tier-0 repairs (`TIER0_REPAIR_TABLE.md`) are unapplied; three change what may be written.

---

## Option A · Modern retron classification / evolution paper

**Revision 1 said: do not write this, every pillar has failed. Revision 2 says: premature, not
refuted — and the distinction matters.** [REV-1 CORRECTED]

What actually failed is narrower than revision 1 claimed:

| question | status |
|---|---|
| reproduce Mestre's *published objects* | SUPPORTED_WITH_LIMITATIONS |
| re-infer Mestre's classification from sequence | **FAILED** (alignment and extracts unrecoverable) |
| *place* new sequences into the historical 11-clade system | **FAILED on control gate K3** (shuffled placed at 7.9 %) |
| a **modern, label-independent de novo phylogeny** | **NOT_YET_TESTED — never attempted in this project** |

The five "failed tree routes" are prior-project, `[UNVERIFIED]` here, and targeted different
questions. So the correct statement is: **classification-by-placement into the historical system is
not currently possible with a validated discriminator, and a modern label-independent phylogeny has
not been tried.** A classification paper today would rest on nothing; a classification paper after a
preregistered de novo attempt might rest on something. It is **premature**, and the reason to delay
it is the absence of a relatedness backbone, not a proven impossibility.

**What is publishable now from this material:** the **audit itself** — a short methods/analysis piece
on why retron classification does not currently reduce to one axis, carrying the annotation-lineage
argument, the measured 43.85 % DefenseFinder/PADLOC subtype agreement, the 6.6-fold carriage
asymmetry, and the K3 failure as a documented negative about placement instruments.

**Must be excluded:** any revised nomenclature; any claim of independent validation; any tree built
from the failed routes.

---

## Option B · RT–ncRNA pairing / RT-conditioned ncRNA modelling

**Revision 1 said: "not publishable today; needs arms G and P." Those arms have now run, and X2 is
formally closed — `4f8550b` holds the results, `fdf0872` is the governing interpretive source.
Revision 2: this is a publishable paper, provided its claim is pitched at the level the evidence
supports.**
[REV-1 CORRECTED — the substantive upgrade]

⛔ **X2 must never be reported as PASS or FAIL.** The frozen gate returned `X2-A`, but the
**conclusion of record is the qualified paragraph, not the label** (`X2_CLOSURE.md` §2). Any
write-up carries the four levels separately:

| level | what may be said |
|---|---|
| **1 · broad lineage information** | reproducible and large — conditioning on RT lineage strongly improves prediction of the cognate ncRNA (G − U −0.04256 [−0.04619, −0.03893]) |
| **2 · small exact-RT residual** | the exact RT adds a reproducible-in-sign increment beyond its own 50 %-identity homolog group (R − G −0.00551 [−0.00797, −0.00312]), but **most of the gain is lineage-level** (G − T −0.019 of R − T −0.025) and the **magnitude is seed-unstable** (−0.0055 to −0.0156, sd 0.0051) |
| **3 · weak close-counterfactual pair discrimination** | ~10-fold decay C1 → C4; at C3 **52.5 % of pairs** favour the observed RT and the **raw pair-level mean is −0.000205** |
| **4 · biochemical compatibility** | **untested** — and explicitly not supported by the bundle |

**The central claim that the evidence now supports, stated at four levels and not collapsed:**

> Frozen protein and RNA language-model representations carry information about which ncRNA belongs
> to which RT. Under component-blocked cross-fitting over the whole population (1,075 components /
> 30,924 pairs), **broad RT lineage** is the dominant carrier (G − U −0.04256 [−0.04619, −0.03893]);
> the **exact RT adds a small, sign-replicated but magnitude-undetermined increment beyond its own
> 50 %-identity homolog group** (R − G −0.00551 [−0.00797, −0.00312]; 3/3 seeds same sign; seed
> sd 0.0051 ≈ the estimate); **pair-level discrimination against near neighbours is not
> demonstrated** (the effect decays ~10-fold from C1 +0.0177 to C4 +0.0017, and at C3 only 52.5 % of
> pairs favour the observed RT); and **biochemical compatibility is untested**.

**Evidence already available:** the full X2 table set; the frozen split and its leakage measurements;
the retrieval ladder (rung 3 fails at +0.0298 [−0.0048, +0.0633]); the permutation control (P − T
−0.00590, **not flat**); the generalisation gradient (Q1 R − T spans zero); tier resolution (T4
−0.02594 over 247 components).

**Strongest figures:**
1. **The arm ladder** U → T → G → R with paired component-level CIs — it *shows* the decomposition of
   lineage versus exact-RT information in one panel.
2. **The counterfactual decay curve** C1 → C2 → C3 → C4, with the % of pairs favouring the observed
   RT on a second axis. This is the honest centrepiece: the effect and its limit in one figure.
3. **The generalisation gradient** by nearest-training-RT similarity quartile, with Q1 spanning zero.
4. **Seed replication** (3 seeds, R − T and R − G) — rarely shown, and it is what makes Q2 credible.
5. The **split/leakage schematic** (component-blocked folds; 82.46 % RT homology at ≥ 0.50 id).

**Missing decisive analyses — now short:**
- the predeclared **rung-0 positive control** (never run);
- a **declared confirmatory population**, because X2 trained on every fold and **no untouched holdout
  remains inside PAIR-ELIG** (OQ-16). Candidates: the 16 fully-external panel elements, or a
  component block frozen now;
- the X1 prose repair (T0-4), since the workbench still cites X1's unweighted figure alone.

**Risks a reviewer will press:** "retron type" is the **ncRNA's own covariance-model label**, so
"beyond type" is measured against a label from the other modality (the G and P arms are the defence,
and they are protein-side); n_eff ≈ 14 in the original split; the ~10-fold decay invites the reading
that the residual is lineage-fine-structure rather than pairing; the non-flat permutation control
means a quarter of the advantage does not require the correct correspondence.

**Methodological precedent, to be stated explicitly in the paper.** OpenCRISPR trained a
protein-conditioned gRNA decoder and used conditional RNA likelihood to study Cas9–RNA
exchangeability. This project **audited the released implementation and adapted reusable
causal-decoder / cross-attention components**; it did **not** reuse their training split, performance
claims or biological negatives. X1/X2 are an **OpenCRISPR-inspired retron adaptation, not a
replication**, and the component-blocked split, the G/P arms and the C1–C4 hierarchy were introduced
here to address **retron sequence relatedness and lineage confounding**. Because no equivalent
experimentally measured RT–ncRNA swap/exchangeability data exist, **biochemical compatibility and
orthogonality remain NOT_YET_TESTED**.

**Must be excluded:** any compatibility label, interaction probability or pair score; any AUROC
against arbitrary mismatches; the word **co-evolution** (no phylogeny, no null); candidate nomination
for the lab; the prior openCRISPR numbers as evidence (audited, not reproduced); and any use of the
panel's 16 external elements as a **compatibility** validation set — they carry functional
measurements, not exchangeability labels.

**Binding design requirements for any follow-up** (`X2_HANDOFF.md` R1–R6): C3/C4-strength
counterfactuals; component-level inference; ≥ 3 seeds with the spread reported; both R − T and R − G;
distance-to-training as a primary axis; unobserved pairings are never biological negatives.

---

## Option C · Large-scale resource + annotation-limits paper

**Still first — but revision 2 sharpens why.** In revision 1 it won because everything else was
failing. It now wins on its own merits *and* because Stage 3C supplies a second, independent
methodological result that fits the same paper's thesis.

**Central claim:** a 501,561-sequence exact-RT catalogue on explicit analytical units, in which the
**annotation limits are measured rather than assumed** — the ncRNA carriage rate moves 6.6-fold with
the detector combination, the tools share model provenance, and the "unique system" count depends
entirely on which unit is chosen.

**Evidence, all landed and reviewed:** corpus identity pin; the unit ladder (no two units convert by
a constant, 1.11–5.49 loci per exact RT); back-translation 99.47 % with 618 mismatches retained; pair
geometry on 344,154 canonical placements; the extraction asymmetry (89.23 % → 13.50 %); the 47.24 %
zero-ncRNA class shown to be detector scope; eligibility/inspectability 501,561 → 369,381 → 354,102;
two artefact dissections (the 2,682 bp downstream mode; `position_relative_to_rt` failing all 12
candidate frames).

**Strongest figures:** the unit ladder/funnel; the extraction-asymmetry panel; pair geometry
(signed distance + CDS-between); the eligibility funnel with per-stratum rates; the artefact
dissection; the subtype × CM near-diagonal heatmap captioned *neither can validate the other*.

**What makes it publishable:** it is a resource **plus** a methods critique, and the critique is the
novelty — the field computes retron ncRNA rates without naming the detector.

**Risks:** "descriptive"; no new sequencing. Mitigate by leading with the annotation-limits result.
**Fix first:** the two circular positive-control claims (T0-7).

**Must be excluded:** the 266 non-Retron CM placements as "divergent retrons"; per-subtype carriage
as biology; unre-derived prior-project numbers.

---

## Option C2 · NEW — RT architecture: what is reproducible across experimental structures

Stage 3C created a paper-shaped result that revision 1 could not see.

**Central claim:** across 62 experimentally determined RT chains, the reproducible architectural
facts are a **catalytic centre** and a **single large core unit** — not a three-way fingers/palm/thumb
partition, which is supported neither by contact density nor by the literature, which does not agree
with itself.

**Evidence:** catalytic Asps in a single unit **19/19**; detector prediction in the same unit as
truth **19/19** including all 6 residue-level misses; site-containing unit replicate-stable at
Jaccard ≥ 0.70 in **13/14** pairs (median 0.897) against a 0.309 chance share, while unit *count*
agrees in only **3/18**; `CAT_STATE 262` exactly **2 residues** before the nearest catalytic Asp in
**17/17** chains — two instruments sharing no input; state blocks **merge** (SB3+SB56 28/28,
SB56+SB7 35/36); literature fingers coincide with a unit **0/11**; two 2026 papers on the same Eco8
protein publish **incompatible** partitions; the inherited boundary product is RED on its own files
(residual construction 25/25; the 5G2X palm excludes that chain's own catalytic Asp).

**Strongest figures:** F1 catalytic site vs units; F2 state blocks vs units; F3 literature overlap
with the reference-disagreement panel; a "six vocabularies" schematic.

**Risks:** 62 chains, 31 groups, one structural cluster, cryo-EM 50/62; Comparison A is
**retron-free** (all 19 truth-bearing chains are non-retron) and that must be stated as prominently
as the result; Stage 3B's mislabel must be repaired first (T0-1), since this paper would cite it.

**Must be excluded:** any universal three-domain claim; any universal Region-Y motif (absent in all
6 Eco8 chains, present in 4 non-retrons); any retron-specific catalytic statement.

---

## Option D · Thesis architecture (revised)

| ch | title | source | status | paper? |
|---|---|---|---|---|
| 1 | What a retron is, three ways | `WHAT_IS_A_RETRON.md` | ready | frames C |
| 2 | From mining records to biological objects | `dbchar_g1…g7b` | landed | **Option C** |
| 3 | Annotation limits as a measurable object | g6 tool calls, g3 zero-class, g7b §6–7 | landed | core of C |
| 4 | A frozen residue-level instrument for RT conserved states | `rt07_g1…g5`, UG25, g4b | landed | methods paper (optional) |
| 5 | What RT0–RT7 can and cannot mean | `rt07_g7a` + erratum + **Stage 3C Comparison B** | landed | strong chapter |
| 6 | **Architecture across experimental structures** | Stage 3A FAIL + **Stage 3C** | complete | **Option C2** |
| 7 | Catalytic geometry: a fired kill criterion | Stage 3B | stopped on K5 | chapter only, **after T0-1** |
| 8 | **RT-conditioned ncRNA modelling: lineage, residual, and the limit** | `embed_g2` + **`embed_x2`** | complete | **Option B** |
| 9 | What did not work, and why that is informative | `NEGATIVE_RESULTS.md` | ready | the distinctive chapter |
| 10 | The experimental layer, and what it can and cannot support | register + **`PANEL_LEAKAGE_MAP.tsv`** | ready | future-work chapter |

### The revised thesis sentence

Revision 1's sentence is **withdrawn**: it asserted that neighbourhood and other features do not
carry retron identity, when neighbourhood was tested only as a *discriminator*, in prior unverified
work, and fusions/effectors were never tested at all. It also leaned on "annotation lineage" as
though it were a biological determinant.

> **Proposed replacement.** Retron systems are defined operationally by an RT–ncRNA pairing whose
> genome-scale population is inherited from a single annotation lineage. Where that population can
> be interrogated directly, the information that identifies a partner is carried mostly by **broad RT
> lineage**, with a small, reproducible-in-sign residual attributable to the **exact RT**; the
> architecture that is reproducible across experimental structures is a **catalytic centre within a
> single core unit**, not a three-way domain partition; and the properties most often treated as
> diagnostic — a universal Region-Y motif, a stereotyped ncRNA position, a characteristic
> neighbourhood — are either not universal, detector-defined, or **not yet tested**.

Every clause names what was measured, and the untested things are called untested.

---

## Revised sequencing

1. **Now, no compute:** Tier-0 repairs (operator sign-off on T0-1, T0-4, T0-5, T0-7), register the
   panel with its exposure map, clear `human_input_audit` for the bundles the route names.
2. **Write Option C** — unchanged as the first paper.
3. **Write Option B** — now viable, pitched at the four-level claim, after the rung-0 control and an
   explicit declaration of the confirmatory population (OQ-16).
4. **Option C2** — assemble from the closed Stage-3C bundle after T0-1.
5. **Option A** — hold. Revisit only if a preregistered de novo phylogeny is attempted and lands.
