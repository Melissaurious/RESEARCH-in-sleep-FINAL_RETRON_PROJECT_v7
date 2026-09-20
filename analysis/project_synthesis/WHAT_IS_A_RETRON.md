# WHAT IS A RETRON? — revision 2

**Revision 2** incorporates Stage 3C (`34000ee`) and `embed_x2` (`4f8550b`). Three rows of the
property table change: Region X/Y now has direct measurement, catalytic architecture gains a
reproducible landmark, and the RT–ncRNA pairing row is re-graded at four separate levels. One
revision-1 framing error is corrected: annotation lineage is how the *population* is defined, not a
biological determinant of what a retron is.

An evidence-graded assessment, not a definition. The question is asked three separate ways, because
this project's own results show the three answers are **not** the same object:

1. **Retrons as historically annotated** — what the label has meant in practice.
2. **Retrons as molecular systems** — what is experimentally demonstrated about the mechanism.
3. **Operational criteria for genome-scale detection** — what can actually be measured on 500,000
   sequences, and what each criterion costs.

Where a property is graded, the grade is about *this project's evidence*, not about the field.

---

## 1 · Retrons as historically annotated

The label is an **annotation lineage**, and this project can document the lineage precisely.

- Toro's 9,141-representative RT tree is the source population of Mestre 2020; Mestre's set is
  **1,912 of those tips plus 16 previously characterised retrons**. That is the origin of the
  modern retron census.
- Mestre's 1,928-row supplementary table has **no experimental-validation column**. Its only
  experiment-adjacent field is a `Retron name` on **17 rows**, and the a–g footnote legend is
  absent from every local copy, so "what makes a row validated" is unanswerable from the file.
- Its `msr/msd family` labels are **CMfinder-derived consensus structures** (populated for 1,009 of
  1,928 rows), not measurements.
- All 21 covariance models in the production pipeline are **Mestre-authored**; PADLOC's retron rules
  score on them; DefenseFinder's profiles were iterated to recover the same known set; MyRT supplies
  the family label.
- Mestre's own alignment and RT0–RT7 extracts are **not published and not on disk**, and independent
  re-inference **failed** (≤ 3 of 11 clades recovered, with RNA-polymerase contamination in the
  substitute set).

**Consequence.** "Retron", as used at genome scale today, means *an RT that a Mestre-descended model
lineage places in the retron part of RT sequence space, usually together with a Mestre-authored CM
hit upstream.* That is a real, useful, reproducible operational object. It is **not** an independent
biological definition, and agreement among the three tools is **not** corroboration.

Grade: **ESTABLISHED** as a description of the label. **FAILED** as an independently reproducible
classification.

## 2 · Retrons as molecular systems

Here the local experimental record is thin but real (`EXPERIMENTAL_RT_NCRNA_REGISTER.tsv`).

| property | local experimental evidence | grade |
|---|---|---|
| **An RT produces a short, covalently RNA-linked DNA (msDNA/RT-DNA) from its own cognate ncRNA** | **the defining property.** 81 of 175 panel elements carry an *empirically determined* RT-DNA sequence; RT-DNA production was measured for 103 and is > 0 for **67**. Deposited complexes contain the RT with both an RNA and a DNA chain (Ec86 7V9U/7V9X/7XJG/8QBM; Ec83 9E8Z; Ec78 9VHE/9NNB; Eco8 9X94) | **ESTABLISHED (experimentally defining)** |
| **The RT is functionally paired with a specific ncRNA** | the panel synthesises and assays each RT *with its own ncRNA*; 100 elements give human editing > 0, 27 bacterial, 16 phage — i.e. the pair works as a unit | **ESTABLISHED for the pairing as a unit; NOT_YET_TESTED for exclusivity** — no swap, cross-reactivity or orthogonality experiment exists in any local asset |
| **Sequence-level determinants of *which* ncRNA belongs to *which* RT** (`embed_x2`, 1,075 components) | four separate levels, not one: **(i) broad RT lineage** predicts the ncRNA (G − U −0.04256 [−0.04619, −0.03893]) — **ESTABLISHED**; **(ii) the exact RT adds a residual beyond its 50 %-id homolog group** (R − G −0.00551 [−0.00797, −0.00312], 3/3 seeds same sign, seed sd ≈ the estimate) — **SUPPORTED_WITH_LIMITATIONS**; **(iii) pair-level discrimination against near neighbours** (C3 favours the observed RT in **52.5 % of pairs**) — **UNDERPOWERED**; **(iv) biochemical compatibility** — **NOT_YET_TESTED** | the property is real at lineage scale and **not demonstrated** at pair scale |
| **msDNA is not predictable from sequence alone** | the census paper's own abstract: 62 empirically determined RT-DNAs *"are not predictable from the retron sequence alone"* | **ESTABLISHED (and it is a warning to every computational plan here)** |
| **A catalytic RT core (YxDD-class)** | 0.9653 of CAT-mapped catalogue RTs carry `[YF].DD` at the frozen catalytic state; Ec86 D198 and Ec67 D202 are individuated structurally; Eco8 D107A by mutagenesis, with YADD→AAAA implicating D200/D201 only **jointly** | **ESTABLISHED as necessary; NOT sufficient** — it is shared with every RT family |
| **An effector / accessory partner** | present in many deposited complexes (Ec86 + effector; Ec78 PtuA:PtuB; Eco7 ATPase+HNH; Eco8 OLD nuclease; Ec83 ATPase+HNH) but **absent from others**, and never measured at corpus scale here | **COMMON, LINEAGE-SPECIFIC, not necessary** |
| **A defence phenotype** | phage editing/protection measured for only **16** of 175 elements | **UNDERPOWERED as a general property** |

**What is conspicuously absent from every local asset:** ncRNA mutagenesis data, RT mutagenesis
libraries, swap/cross-reactivity experiments and orthogonality panels. Variant-library and
engineering papers are on disk **as PDFs only**, with no supplementary data. So the single question
this project is named for — *how specific is an RT for its own ncRNA?* — has **no local experimental
ground truth at all**.

## 3 · Property-by-property verdict

| property | necessary? | common? | lineage-specific? | historical/conventional? | experimentally defining? | this project's grade |
|---|---|---|---|---|---|---|
| RT phylogenetic lineage (retron clade membership) | as currently used, **yes by definition** | — | **yes** | **yes — this is the label** | no | ESTABLISHED as convention; FAILED as independent classification |
| Catalytic RT core (YxDD / palm Asp) | **yes** | yes (all RTs) | no | no | **yes, for RT-ness** | ESTABLISHED, not discriminative. **Stage 3C adds a reproducible architectural landmark:** the catalytic aspartates lie in a **single structural unit in 19/19** chains, replicate-stable at Jaccard ≥ 0.70 in **13/14** pairs (median 0.897) against a 0.309 chance share, and `CAT_STATE 262` sits exactly **2 residues** before the nearest catalytic Asp in **17/17** chains — two instruments sharing no input. **Scope: all 19 truth-bearing chains are non-retron** |
| RT0–RT7 numbered regions | **no** | — | GII-derived | **yes, procedurally** | no | Of 32 region names, **1** has a stated residue boundary; RT0/RT1 UNRESOLVED; the seven-way partition is NOT ESTABLISHED (block-count null p = 0.6965) |
| Retron-specific X / Y regions | **no** (Y is not universal) | Y defined in **15/21** retron chains; X in only **8/21** (undefined in 13) | partly — but **not exclusive** | **yes** — no source states a general numbered interval for either | not as a motif | **PRELIMINARY (Y) / UNDERPOWERED (X)**. Stage 3C, rule frozen before scanning: **all 6 Retron-Eco8 chains lack a VTG-like triplet**; VTG appears in **4 non-retron** chains; Y median length 74 aa vs the literature's "~90 aa"; Y coincides with the Ec86 **thumb** (238–320) and carries **1.34×** its length share of RNA-contacting residues (range 0.59–1.86, n = 15) vs 1.06 in non-retrons. ⚠️ group II "domain X" is the **thumb**; retron "Region X" is between RT2 and RT3 — different objects |
| ncRNA / msr-msd | **yes for a retron *system***; **no** for a retron *locus as annotated* | detected at ~53 % of retron loci — but that rate swings 6.6-fold with the detecting tool and reaches 0 % for subtypes with no model | model coverage is subtype-specific (types VI–XII largely unmodelled) | **yes** | **yes** | ESTABLISHED as detector description; **the ~47 % zero-class is detector scope, not biology** |
| msDNA production | **yes — the defining property** | yes where tested (67 of 103 measured) | no | no | **YES** | ESTABLISHED experimentally; **UNPREDICTABLE from sequence** |
| Genomic adjacency / orientation | no (it is a consequence, not a criterion) | overwhelmingly: 94.5 % upstream, median gap 55 bp, 99.8 % same strand, 94.41 % zero CDS between | — | **partly** | no | ESTABLISHED as description; **partly circular** — the CMs were trained on msr-msd in that position |
| Effector / accessory genes | **no** | common in solved structures; unmeasured at scale | **yes** (Toprim, TIR, HNH/ATPase, protease, OLD nuclease by subtype) | **yes** — the evidence here is PADLOC *rule definitions*, not observations | partly | **NOT_YET_TESTED** (all 41.3 M neighbour CDS lack sequences); neighbourhood is **REFUTED as a detector** (retrons 27th of 41 families) |
| Terminal / fused domains | no | unknown | unknown | no | no | **NOT_YET_TESTED**; Stage 3A `EXTRA_DOMAIN` is length-confounded |
| Compact palm / fingers / thumb decomposition | **no** | — | — | **yes — textbook convention, and the convention is not self-consistent** | no | **FAILED**: palm-like 0.565 vs a 0.70 bar; 22/22 LOGO folds FAIL; PDP partition unstable (0.385). **Stage 3C explains why:** literature fingers coincide with a unit **0/11**, a *combined* fingers+palm region coincides 1/1, two 2026 papers on the same protein publish incompatible partitions, and the inherited boundary product is RED (residual construction 25/25; the 5G2X palm excludes its own catalytic Asp). The state series **merges** into one unit (SB3+SB56 28/28, SB56+SB7 35/36) |
| Defence phenotype | no | unknown | yes | increasingly **yes** (retrons entered the literature as defence systems) | for 16 elements | **UNDERPOWERED** |

## 4 · Operational criteria for genome-scale detection — and their cost

What this project can actually recommend, with the price of each criterion measured:

| criterion | what it buys | what it costs (measured here) |
|---|---|---|
| RT family label from a model lineage (MyRT/PADLOC/DefenseFinder) | scale: 501,561 exact RTs, 78,287 retron-labelled | not independent evidence; three tools share provenance; DefenseFinder/PADLOC subtype strings agree on only **43.85 %** of records where both wrote one |
| Requiring an upstream CM hit | high precision for canonical subtypes | **discards ~47 % of retron-labelled loci**, and the discard is structured: 87.27 % unmatched where < 200 bp of upstream context exists vs 42.91 % with ≥ 1 kb; carriage is 0 % for subtypes with no model |
| Requiring a catalytic residue at a conserved state | 0.9653 of CAT-mapped sequences pass; a clean, family-agnostic filter | **RT-catalytic, not retron-specific**; it admits ~90 % catalytically intact RTs of other families |
| Length / completeness eligibility (≥ 250 aa, standard residues) | makes residue-level analysis possible | removes **26.35 %** of the catalogue *unevenly* — 11.3 % eligible for mixed/codon evidence, 37.2 % for MULTI, 57.4 % for all-partial |
| Requiring msDNA production | the only criterion that matches the molecular definition | **not computable** — the census paper states RT-DNAs are not predictable from sequence alone |

**The honest operational recommendation.** A genome-scale retron call should be reported as a
**profile, not a boolean**: (RT lineage label + which tools called it) × (CM hit present/absent, with
upstream context length) × (catalytic state mapped/abstained) × (ncRNA geometry class) × (accessory
architecture, once annotated). Every one of those axes is measurable on this catalogue today except
the last. Collapsing them into "is a retron" is exactly what produces the circular rates this project
spent Stage 1 documenting.

## 5 · The one-sentence answers

- **As historically annotated:** a retron is an RT that a Mestre-descended model lineage places in
  retron sequence space, usually with a Mestre-authored covariance-model hit immediately upstream and
  on the same strand.
- **As a molecular system:** a retron is an RT that, together with its own cognate ncRNA, produces a
  specific short RNA-linked DNA (msDNA) — a property that is experimentally demonstrated, frequently
  coupled to an effector, and **not predictable from sequence alone**.
- **Operationally at genome scale:** a retron is best reported as a multi-axis profile whose ncRNA
  axis is detector-limited, whose catalytic axis is family-agnostic, and whose domain-architecture
  axis this project has shown **does not** decompose into the conventional three-unit picture — while
  the one architectural landmark that *is* reproducible across experimental structures is the
  **catalytic centre inside a single core unit**, independently located by a sequence HMM state to
  within two residues.

**A note on what "retron-specific" can mean after Stage 3C.** The two candidate retron-specific
sequence features behave differently. Region X is mostly **not observable** with the current
instrument (defined in 8 of 21 retron chains). Region Y *is* observable, coincides with the thumb,
and is RNA-contact-enriched — but it is **neither universal** (absent in all six Retron-Eco8 chains)
**nor exclusive** (present in four non-retron chains). So "retron-specific region" is at present a
**hypothesis with one classical two-retron experiment behind it and one modest structural
enrichment**, not a defining property.

## 6 · What would change these answers

| statement | what would falsify or sharpen it |
|---|---|
| The ~53 % ncRNA carriage rate is detector scope, not biology | a retron definition independent of the CM lineage, applied to the same loci |
| The ncRNA is necessary for a retron *system* | an RT with demonstrated msDNA production and no identifiable msr-msd |
| The RT–ncRNA pairing is specific | **the missing experiment**: a swap / cross-reactivity / orthogonality panel. None exists in any local asset. Computationally, the nearest thing is `embed_x2`, which shows a small exact-RT residual (R − G −0.0055) but only **52.5 %** pair-level preference against nearest neighbours |
| Region Y contributes to pairing specificity | the declared join of `XY_REGION_ANNOTATIONS.tsv` (`rt_hash`-keyed) to the RT–ncRNA modelling dataset — deliberately left out of scope by Stage 3C, and the most testable link the new results create |
| Broad RT lineage, not the exact RT, carries the pairing information | a lineage-matched control (arm G) that *eliminates* the residual; currently the residual survives in sign but not in determined magnitude |
| Domain geometry does not define retrons | a parser-independent decomposition clearing 0.70, or a demonstration that the textbook thresholds — not the parser — caused the failure (`1RTD_A` is the test case) |
| RT0/RT1 are not recoverable | primary historical evidence (Malik, Burke & Eickbush 1999) stating a boundary |
