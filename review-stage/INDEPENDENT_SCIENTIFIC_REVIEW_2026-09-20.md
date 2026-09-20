# INDEPENDENT SCIENTIFIC REVIEW — retron RT / ncRNA project

**Date:** 2026-09-20 · **Stance:** adversarial, external, no prior context assumed
**Reviewed state:** branch `project-synthesis`, tip `6476ff0` (one documentation-only commit past the
`cfd0a7e` named in the request). Note that `6476ff0` is **two commits ahead of
`origin/project-synthesis` and unpushed**, and that `rt07-stage2-final-report`,
`worktree-mestre-audit` and `worktree-spire-ncrna` are **unmerged into `main`**.
**Entry points used:** `PROJECT_REVIEW_PACKAGE/README_START_HERE.md`, `HANDOFF_PROMPT.md`
**Verification:** `scripts/validate_package.py` PASS (40 paths, 32 commits); plus direct
re-derivation from landed tables across nine worktrees.

> Not claim authority. Claim authority remains `idea-stage/docs/research_contract.md`.
> Nothing here authorises compute.

---

## 0 · Method and standard

I did not summarise the package. I re-derived its load-bearing numbers from landed artefacts and
looked for defects it does **not** already name. The package is unusually candid: a register that
documents its own five upheld blockers, its own inert baselines and its own fired kill criterion is
not carelessly concealing things. So the useful question is not *are they honest* but **is the
remaining, self-declared-strongest material actually strong.**

I applied the project's own standard throughout:

> *A zero needs a positive control showing the same instrument returns non-zero on a known case.*

The project applies this rigorously to covariance-model zeros. It does **not** apply it to its
structural arm, to its historical-placement arm, or to its own frozen instrument.

**Four headline conclusions.**

1. **The convergence claim must be withdrawn.** The proposed thesis spine, that four independent
   instrument families each stopped at the same boundary, fails because the families are not
   independent and at least two of the stops are instrument artefacts.
2. **Three of the package's quoted numbers are wrong or misread**, one of them a load-bearing
   headline. Details in §3.
3. **The pairing arm's central claim is weaker than stated** and its effect sizes are currently
   uninterpretable because no absolute baseline exists anywhere.
4. **Two large, cheap, genuinely biological analyses are available today** and have never been
   started: the internal msr/msd architecture of the ncRNAs, and the genomic architecture around the
   RTs. The second is **not** blocked, contrary to the package's own assessment.

---

## 1 · OVERALL_SCIENTIFIC_ASSESSMENT

### 1.1 What the project actually holds

1. A governed, identity-pinned catalogue: 3,358,182 corpus lines → 3,059,700 RT-anchored records →
   2,847,312 genomic loci → 2,475,684 physical loci → 501,561 exact RTs, plus 16,458 exact ncRNAs
   and 30,924 exact pairs. This is the principal asset and it is sound.
2. A documented demonstration that a genome-scale retron population is defined by its detector.
3. A frozen residue-level instrument applied to 369,381 proteins, with an honest scope statement.
4. A set of negatives, of which two are clean, two are artefacts, and two are underpowered nulls.
5. One quantitative modelling result decomposing RT-to-ncRNA information into lineage and
   exact-sequence components.

### 1.2 Seven structural problems

**P1 · The convergence argument is a shared-dependency artefact.**
Four instrument families are claimed to have independently hit one boundary. They inherit the same
21 Mestre-authored covariance models: those calls define PAIR-ELIG, set the sequence extents the RNA
language model sees, supply the `retron type` label arm T conditions on, and define the positive
class SPIRE was scored against. The embeddings, SPIRE and boundary arms are three views of one
dependency. **A convergent stop across instruments that share their definition of the target is
weak evidence about biology and strong evidence about the definition.**

**P2 · The strongest positive result has no absolute baseline, and its unconditional arm is worse
than uniform.** Landed arm-level held-out cross-entropies are U 1.40666, T 1.38329, G 1.36410,
R 1.35859, P 1.37739 nats/nt. Uniform over four bases is ln 4 = 1.38629. The unconditional arm is
**0.0204 nats/nt worse than random guessing**; the best arm is 0.0277 better. The entire reported
effect range, 0.0017 to 0.0426, is the same order as the model's whole distance from triviality. No
unigram, composition, positional or k-mer baseline exists in any bundle. Until one does, nobody can
tell whether "RT lineage predicts the cognate ncRNA" means the model learned RNA biology or learned
that retron types differ in GC content.

**P3 · The structural negative is a threshold artefact, and is billed as the project's cleanest
result.** The palm-like unit **meets both of its other predeclared bars** (recurrence 0.798,
stability 0.798) and misses only the call rate, 0.565 against 0.70. Under any bar at or below 0.565
the verdict rule yields PARTIAL, not FAIL. Decisively, the closure's own post-freeze note records
that in **17 of the 19 no-call primary chains a unit does carry four or more same-sheet strands**
and is rejected only by the `frac_E ≥ 0.20` composition rule because the unit is too large. The
β-sheet is present; the rule rejects it on size. The only textbook chain, HIV-1 p66 `1RTD_A`,
returns AMBIGUOUS with a candidate thumb at frac_H 0.521 against a 0.60 rule, and the parser
disagrees with itself on 62% of replicate pairs (agreement 0.385). **An instrument that cannot
recover the palm of HIV-1 reverse transcriptase has failed its positive control.**

**P4 · The pairing arm's sample size is unsettled in its own documentation, and the honest figure is
smaller than either candidate.** The package states n_eff ≈ 12.5 in five places and builds it into
the handoff prompt. The landed tables publish `n_eff = 1075.0`, which is a formula defect: the
producing scripts compute `(ones.sum()**2)/len(d)`, algebraically n²/n = n, while the correct Kish
form exists elsewhere in the same bundle. The 12.5 is a Kish figure over **pair** weights,
describing concentration of pairs into components, not the effective n of an estimator that weights
components equally. The estimator is an unweighted mean over 1,075 components, so the bootstrap is a
real n = 1,075 bootstrap. **But components are not independent draws.** They sit inside 21 retron
types with a token-weighted effective type count of 9.3. That variance component appears in no
interval, and the per-type strata show exactly what it costs (§1.3).

**P5 · The project routed around its own subject.** A retron is an RT plus an msr-msd ncRNA that
together make msDNA. The project holds 16,458 exact ncRNAs and has never decomposed one into msr and
msd, located a branching guanosine, found an a1/a2 inverted repeat, or folded one. ViennaRNA sits
unused in the environment lock files; no script imports it. Only **1,251 of 16,458 (7.60%)** carry
even the shipped covariance-model structure annotation. The oriented set is on disk at
`data/derived/rt_ncrna_oriented_v1.fna`: foldable, never folded. The gap was identified and routed
around, named in the reporting package as a *reason to reject* the OpenCRISPR two-segment vocabulary.

**P6 · A large, available analysis was wrongly written off as blocked.** The package states that
accessory architecture is `NOT_YET_TESTED` and blocked because all 41,250,531 accessory CDS carry
`has_sequence = False`. The corpus schema census shows what they **do** carry: contig, start, end,
strand, length, and a `prodigal_metadata` block with GC content, RBS motif, RBS spacer, start type
and partial flag, on all 44,242,429 CDS occurrences. Further, `genomic_context.full_sequence`, the
±10 kb window, is present on **100%** of records, so every accessory protein is re-translatable from
coordinates. A derived table already holds them: `data/derived/rt_window_cds_v1.parquet`,
**44,310,231 rows**. The project's own handover says it correctly and the package did not carry it
forward: *"Neighbourhood architecture is available; neighbourhood identity is not."* **Gene density,
operon structure, strand topology, intergenic spacing, GC deviation and RBS features are all
computable today at near-zero cost.** Only functional identity needs Ibex.

**P7 · No number in this project is promotable under its own governance.** `BUNDLE_SPEC.md` makes
`human_input_audit: DONE` a precondition for promoting any number to a paper or thesis. Across all
nine worktrees, the string `DONE` for that field appears in **exactly one file: the spec that defines
it**. Twenty-nine files carry `PENDING`, and 12 of 29 result bundles omit the field entirely,
including both bundles carrying the terminal Stage-2 claims (g6, g7a) and both carrying the
instrument freeze and the confirmatory run. This is not a formality; it is the project's own stated
gate, and it is closed on everything.

### 1.3 The number that reframes the pairing arm

The distinctive pairing claim is level 2: the exact RT adds information beyond its own 50%-identity
homolog group (R − G). Across the **same 36 adequately-powered strata** the package cites:

| contrast | CI wholly below 0 | spans 0 | wholly above 0 |
|---|---|---|---|
| **R − T** (includes lineage) — *the figure the package quotes* | **28** | 7 | 1 |
| **R − G** (the exact-RT residual — the actual claim) | **20** | **16** | 0 |

On the retron-type axis, R − G has its whole interval below zero in **3 of 11** powered types and
spans zero in 8. Eight of 21 types have a point estimate in the wrong direction.

Three further landed numbers, none in the package's four-level summary:

- **R − G favours the exact RT in 55.35% of components.** The package reports the equivalent for
  level 1 (86.0%) and for pair-level discrimination (52.5%) but omits it for the level that carries
  the claim.
- **The permutation control is larger than the effect it bounds.** P − T = −0.005904 (57.02%)
  against R − G = −0.005507 (55.35%). Different baselines, so not a direct refutation, but it sets
  the scale: the exact-RT residual is the size of a control that should be near null.
- **The one contrast that defends the arm is reported nowhere: R − P = −0.018797** [−0.02457,
  −0.01348], 59.7% of components. The real RT beats a permuted same-type RT by three times the R − G
  margin. See §2 item 4.

### 1.4 Verdict

A **strong dataset-and-epistemics project with a weak biology yield**. The mismatch follows from
three early choices: the population was inherited from one annotation lineage and never anchored to
an independent definition; the RNA was treated as an opaque sequence; and the questions were framed
as predict-the-partner rather than describe-the-system. All three are partly reversible now, and two
of them cheaply.

The thesis is viable. One paper is viable after bounded work. A second is viable only if repitched
from a positive result to a bound, and only if it survives an absolute baseline. The structural arm
should not become a paper.

---

## 2 · STRONGEST_CURRENT_CLAIMS

Ranked by weight-bearing capacity. Wording here is tighter than the package's in three cases and
looser in two.

**1. The analytical units are non-interconvertible, and the choice of unit changes every count.**
Loci per exact RT ranges 1.11 (mgnify_soil) to 5.49 (ncbi_bacteria), and `records_per_locus = 1.0`
inside every database, so **all** redundancy is cross-database re-deposition. The funnel decomposes
into 8,462 duplicate lines, 203,926 re-mined records, 371,628 RefSeq/GenBank twin loci and 1,974,123
repeated proteins, a 6.10× cumulative collapse. Recurrence is structured: of 30,924 exact pairs,
12,005 occur once, 9,362 recur only as database copies of one physical locus, 4,452 within one
species and 5,056 across species, and that last 16.4% of pairs carries **79.4%** of all placements
(largest pair 101,792). *Status:* ESTABLISHED. *Risk:* none material.

**2. All 21 retron covariance models in the production pipeline were authored by one person, and the
three nominally independent tools descend from them.** The chain Toro 9,141-tip tree → Mestre 2020
(1,912 tips + 16 characterised retrons) → CMfinder motifs → 21 covariance models → PADLOC rules (17
of 18 score on the ncRNA) → DefenseFinder profiles iterated to the same known set → MyRT labels is
documented at file level, and `t22_cm_meta.tsv` shows `author = Mestre MR` on all 21. *Status:*
ESTABLISHED as provenance. **Correction, and it matters:** the quantitative anchor the package uses
for this claim, "DefenseFinder and PADLOC agree on only 43.85% of subtypes", **does not support it**.
Of the 205,327 disagreeing records, `Retron_II` versus `retron_II-A` accounts for 179,027 and
`Retron_III` versus `retron_III-A` for 19,696: **96.8% of the disagreement is naming convention, not
classification.** Genuine semantic disagreement is on the order of 1.8% of records. This number must
be removed from every document or restated as a normalisation artefact. The provenance claim stands
on the authorship chain alone, which is sufficient.

**3. A genome-scale retron population is defined by its detector, and the carriage rate moves
6.6-fold.** From 13.50% (myRT alone) to 89.23% (myRT+PADLOC) across seven tool-combination strata,
on 663,308 Retron-family records; 7.08× at physical-locus unit and 4.70× at exact-RT unit. *Status:*
ESTABLISHED **as stated**, with the correction that these are seven different record populations,
not one locus set scored seven ways, and the table's own note says so. The surviving claim is *"if
you change the tool combination that defines your retron set, the published carriage rate moves
6.6-fold"*. That is the claim the field needs and it is defensible. What does **not** follow from
this table is *"the detector misses 47% of real ncRNAs"* (§3 item 8).

**4. [UNDERSTATED — promote] The exact RT beats a deliberately permuted same-type RT.**
R − P = −0.018797 [−0.02457, −0.01348], 59.7% of components: three times the R − G margin, and the
direct test of whether RT identity carries partner information once type is fixed. It appears in no
document. The project chose R − G as its headline because the homolog representative is the tighter
control, which is honest, but **reporting only the tightest contrast and not the direct one
understates the result.** Both belong in the paper, with the permutation arm's own non-flatness
attached.

**5. [UNDERSTATED — promote] The field's fingers/palm/thumb vocabulary is not operationally
defined.** Literature-stated fingers boundaries coincide with a structural unit in **0 of 8** cases
after the motif row is excluded (median best Jaccard 0.488); a *combined* fingers+palm region
coincides 1/1 at 0.713; **two 2026 papers on the same Retron-Eco8 protein publish incompatible
partitions in the same numbering frame**; one LtrA paper carries two thumb definitions; the inherited
boundary product builds fingers and thumb as arithmetic residuals in 25/25 rows and its 5G2X palm
excludes that chain's own catalytic aspartate. **This result does not use the project's parser at
all**, which is why it survives when Stage 3A does not. It is a short publication in its own right.

**6. Broad RT lineage information predicts the cognate ncRNA.** G − U = −0.04256 [−0.04619,
−0.03893], 86.0% of components; G − T = −0.01919, so about three-quarters of the RT-associated gain
sits at the lineage level (77.7% at the bundle's weighting, 74.1% token-weighted, so the *share* is
robust even though the absolute effects are not). *Status:* ESTABLISHED within this population,
**conditional on A1**. The ordering U > T > G > R replicates across all five folds and all three seeds.

**7. A fixed positional interval localises retron ncRNAs better than de novo covariation.** The
method recovers 343 at IoU ≥ 0.5; the fixed interval −193…−24 recovers **901**; per-type intervals
recover **969 (92.2%)**. *Status:* REFUTED against a predeclared gate with a decisive comparator.
One of only two negatives in the project I accept without qualification. *(Note the package reverses
the second comparison: the landed values are method 60, fixed interval 87, not the other way round.
Both comparisons favour the trivial prior, so the conclusion is unaffected.)*

**8. A frozen, versioned residue-level instrument exists and was applied at scale.**
`rtmap-1.0.0/53a1e738a19b3896`, seven predeclared conditions met, 369,381 eligible, 354,102
inspectable, 15,279 frozen abstentions. *Status:* SUPPORTED_WITH_LIMITATIONS, and the limitations
are heavier than the package states (§3 item 5).

**9. The experimental panel is an assay layer on the prediction set, not a benchmark.** 175/175 rows
carry a Mestre accession, 145/175 RTs are in the catalogue, only **16** are fully external. Across
all 185 register rows, `swap_or_crossreactivity`, `orthogonality_exchange` and `ncrna_mutagenesis`
are `NOT_IN_LOCAL_ASSETS` in **every row**. *Status:* ESTABLISHED (measured). A model leakage audit.

**10. Retron prevalence varies by phylum on a genome denominator.** Pseudomonadota 51.85%, Bacillota
42.25%, Bacteroidota 40.70%, Actinomycetota 17.68%, Campylobacterota 13.61%, with binomial
intervals; 58.67% of positive genomes carry one distinct RT, 22.62% two, 16.9% three to five.
*Status:* landed but **under-used** — it appears in no synthesis document and in no publication
option, yet it is exactly the content a resource paper needs.

---

## 3 · CLAIMS_THAT_SHOULD_NOT_BE_MADE

**1. "The exact RT carries information about its cognate ncRNA beyond its homolog group."**
Not generally. Supported in **3 of 11** powered retron types and 20 of 36 strata; favourable in
**55.35%** of components; magnitude −0.0055 to −0.0156 across seeds with sd ≈ the estimate; the
near-duplicate arm spans zero (−0.00210 [−0.00601, +0.00196]); and P − T (−0.00590) is larger. Even
the package's "safe wording" for C-28 is too strong. **Replacement:** *"Beyond broad type, most
RT-associated predictive information is carried at the 50%-identity lineage level. A residual
attributable to the exact sequence is directionally reproducible across seeds and folds but is
present in a minority of retron types, is of undetermined magnitude, and is not separable in size
from the within-type permutation control."*

**2. "Type- and lineage-level structure is recoverable; pair- and partition-level structure is
not."** The proposed thesis spine. Withdraw it. Grounds: P1, P2, P3.

**3. "RT chains do not decompose into fingers, palm and thumb."** See P3. The package's own C-10
prohibited-overclaim line says "do not say RT chains have no palm", and that prohibition is not
honoured by `NEGATIVE_RESULTS.md` §2 or by the proposed chapter title.

**4. Anything about retron catalytic architecture.** All 19 truth-bearing Stage-3B chains are
non-retron. All 21 retron chains sit in Tier B or Tier C. Tier B was never opened.

**5. "The frozen mapper was validated on a fresh lineage."** True as written, and materially
incomplete. **UG25 was the third holdout attempt.** UG5 v2 failed outright ("Made falsifiable, they
fail"; monotone placement 31 of 67 = 46.3%). UG5 v3 self-reported a pass and was independently
reviewed **FAIL/BLOCK 5/10** ("MAPPER NOT FROZEN"; the claimed threshold justification "literally
false"; "the provenance layer is broken"). A second holdout, G2L, was reviewed **FAIL/BLOCK 4/10**,
with the selection cutoff fitted at the winner-flip point ("Five is exactly the winner-flip point")
and a recorded governance breach. The launcher's original design required **four** validation arms
(historical reconstruction, held-out PDB structures, the GOLD171 literature challenge, a
family-stratified Stage-1 sample); **none ran**, and a retroactive amendment substituted the single
UG25 run of n = 28. The declared positive control AC1 was **arithmetically unpassable** (ceiling
84.8% against a required 95%) and the mapper was frozen anyway. The frozen 150-anchor table lives
inside the *failed* UG5 bundle. **Permitted wording:** *"frozen after a documented sequence of failed
and repaired holdout attempts, and confirmed once on one fresh lineage of 28 sequences under one
match-state convention, then extrapolated to 369,381 proteins."*

**6. "The profile derives from 66 group II intron ORFs containing zero retrons."** Two errors. The
mapper's sole sequence input is `RTs-collection.faa`, from which **50** myRT-labelled group II
intron proteins were the derivation set (0 retrons, so the retron-free property holds). The 66-ORF
set is the separate g2 historical-reconstruction substrate, and `ALIGN_000044` was a **declared
prohibited input** to the derivation. Moreover **the anchors are not retron-free**: the ALL_PARTNERS
intersection was computed across seven families including Retrons (n = 102), so retron data informed
which states became frozen anchors. The clean "GII-centred frame confounds every between-family
comparison" framing needs qualifying: the frame is GII-**seeded** but retron-**informed** at anchor
selection.

**7. "99.8% of retron ncRNAs are on the same strand as the RT."** **This number is wrong.** The
landed table gives, for CANONICAL placements, same-strand True = 6,700 + 12,108 + 322,305 = 341,113
of 344,154 = **99.12%**. 99.8% is the *overlapping* subset only (99.868%). Its stated source counts
(303,759 of 304,285) exist in no table in any worktree, and the figure is a **hardcoded string** in
`results/dbchar_g7_stage1_report/scripts/findings.py:190`, in a function where every neighbouring
value is a resolved placeholder, with no `same_strand` key in `g7_resolved_values.tsv`. That
falsifies that bundle's own audit claim of zero unsourced numbers. The newer g7b silently corrects to
99.1% without flagging the change. The wrong value propagates into `CLAIM_EVIDENCE_MATRIX.tsv` C-23,
`CURRENT_SCIENTIFIC_STATE.md`, `WHAT_IS_A_RETRON.md` and `RESULT_BUNDLE_REGISTRY.tsv`.

**8. "About 47% of retron loci genuinely lack an ncRNA" *and* "the 47% zero class is detector
scope."** Both unsupported, for opposite reasons. The package attributes the zero class to upstream
context truncation, citing 87.27% unmatched below 200 bp against 42.91% at ≥ 1 kb. The landed table
shows the gradient is **non-monotone** (30.48% carriage at 501–1,000 bp falling to 24.89% at
1,001–2,000 bp) and that the **dominant bin**, 419,613 loci with more than 9 kb of unclipped context,
still sits at **60.52%**. So roughly **40% of retron-labelled loci lack a detected ncRNA even with
abundant context**, and the low-context stratum carrying the 87.27% figure is about 6.6% of the
population. Context moves the overall rate from 47.2% to 42.4%. **Additionally**, the model-coverage
explanation is asserted only in the synthesis layer and is performed by **no landed table**: the true
zero subtypes are VII-A1, VII-A2, VIII and X (986 loci), while VI is 0.0175%, XI 0.1166% and XII
0.0060%, and XII's near-zero is *rule-definitional* (`ncrna_role = PROHIBITED`), not a missing model.
The gate report itself says only that VI "is not explained by the rule and is the better candidate
for a real model gap".

**9. "Carriage ranges from 90.1% to 0% by subtype."** The 90.1% maximum is reached only by dropping
two higher rows, Ec107-like at 98.62% and outgroup at 93.82%, both flagged `REQUIRED IN PRACTICE`.
Report the full range or state the exclusion.

**10. Region X and Region Y as retron-diagnostic.** Y absent in all 6 Retron-Eco8 chains, present in
4 non-retron chains. X defined in 3 of 21 retron chains with **zero** NAXXH or AXXH in any of the 24
declared intervals. The 1.34× Region-Y contact ratio is a median over 15 chains from 5 groups with
range 0.59 to 1.86 against a comparator computed on **three** chains. That range spans 1.0.

**11. "The counterfactual effect decays roughly ten-fold and monotonically."** The tiers use four
different populations: C1 1,019, C2 832, C3 1,073, C4 **451** components, and C4 contains **zero** of
the 581 singletons. On the 423 components common to all four the ladder reads C1 +0.01745, C2
+0.01531, C3 **+0.00080**, C4 +0.00156 — a 22-fold collapse at C3 followed by a rise.

**12. "Stage 3B closed at PARTIAL."** It stopped on a fired kill criterion (decoy pool 23 against
≥ 60) before its held-out tier was evaluated, and it has **no PASS bar at all**. There is still no
Stage-3B erratum; the correction lives only inside a Stage-3C document on another branch.

**13. "Mestre's 18 published tables re-join byte-identically."** It is **17 of 18**
(`inputs_pinned.tsv` differs), and SVGs are 0 of 3. The bundle concedes it: *"The measurements are
reproducible today from graded inputs. Their inputs manifest is not."* Also, "the same rule on the
published tree gives 10/11" is **purity-only**; with support it is 8/11 at ≥ 95 or 9/11 at ≥ 85.

**14. "The Mestre non-retron panel passed."** 1,080 of 1,083 failed extraction (99.72%); the
confidence rule was exercised on **three** negatives. And on the substitute panel, **38 of the 48
that did extract were confidently placed (~79%)**: when the extraction gate does not fire, wrong
proteins are confidently placed. The placement positive control (M2c, 40 queries identical to clean
Mestre proteins) was **declared and never run** — commented out in `run.sh`. **So the instrument was
never shown able to place a correct query, while it was shown to confidently place shuffled noise at
7.9–19.8%.**

**15. Co-evolution, compatibility, orthogonality, interchangeability, any per-pair score, and any
laboratory candidate nomination.** Already correctly prohibited by the package; I concur without
qualification.

**16. Any number at all, in a paper or the thesis, today.** `human_input_audit: DONE` exists nowhere
in the repository except the spec that defines it.

---

## 4 · MAJOR_EVIDENCE_GAPS

**[NEW]** marks gaps not named in the package.

| # | gap | consequence | fixable |
|---|---|---|---|
| G1 **[NEW]** | **No absolute or trivial baseline for the conditional decoder.** U is worse than uniform by 0.0204 nats/nt | every effect size in the pairing arm is uninterpretable; Option B is not submittable | yes, hours |
| G2 **[NEW]** | **No lineage-clustered variance anywhere.** Intervals come from an equal-weight bootstrap over 1,075 components nested in 21 types (effective 9.3); the landed `n_eff` column is a formula defect | the uncertainty on the flagship result is not established | yes, zero compute |
| G3 **[NEW]** | **msr/msd internal architecture never characterised.** No segment boundary, no branching guanosine, no inverted repeat, no fold; only 7.60% of ncRNAs carry even shipped structure annotation | the RNA side of every pairing analysis is an opaque blob; the boundary chapter has no object | yes, days |
| G4 **[NEW]** | **Genomic architecture wrongly written off as blocked.** Coordinates, strand, length, GC, RBS motif and spacer exist on all 44.2 M CDS; the ±10 kb window is on 100% of records; 44,310,231 rows are already landed in a parquet | the largest descriptive biology in the project is sitting unused and was believed unavailable | yes, cheap |
| G5 **[NEW]** | **No rarefaction, accumulation or saturation analysis anywhere.** Contract claim C8 is `UNPROVEN` and has never been measured; the only richness figure is a one-row illustrative Chao1 (78,287 observed, 140,731 estimated) | the project cannot say whether retron diversity is sampled or saturating, which any resource paper will be asked | yes, but needs clustering |
| G6 **[NEW]** | **No ecology.** `tax_environment` is a restatement of `source_database`; GEM's real habitat, ecosystem and geocoordinate columns were identified and never analysed | the metagenome half of the corpus contributes nothing beyond record counts | yes, cheap |
| G7 **[NEW]** | **No mobility or horizontal-transfer analysis.** No GC deviation, codon usage, MGE proximity or defence-island work, though per-CDS GC on 44.2 M CDS and the window DNA are present | a standard and expected axis for a defence-system census is absent | yes, cheap |
| G8 **[NEW]** | **A mandatory X2 control was never implemented.** `DESIGN.md` §69-72 requires the conditioning-reachability check; no implementation, table or value exists in any of the 8 scripts | the gate was declared met while a required check has no landed evidence | yes, low |
| G9 **[NEW]** | **Declared positive controls never run, across three arms.** Mestre M2c (commented out); Stage-2 AC1 (unpassable by construction, 84.8% ceiling against 95%); Stage-2 arms A2, A3, A4 and the A5 natural-protein negative set; SPIRE's end-to-end known-motif recovery (the Rfam set was located and explicitly not used); embed_g2 rung-0 | four instruments were frozen or closed without ever demonstrating they can detect a known positive | partly |
| G10 **[NEW]** | **Stage 3B's declared cleanest negative fired.** HIV-1 p51 `1RTD_B` returns an admissible pair (D110–D186, sep 76, 3.52 Å) under the frozen rule, recorded as a decoy count rather than a specificity failure | a demonstrated false fire is absent from the negative-results register | reporting only |
| G11 **[NEW]** | **No released data product.** `docs/DATASET_REGISTRY.md` states plainly *"None of the files in this document are in GitHub"*; every row reads LOCAL ONLY; no DOI, deposit, release archive or data-availability statement. The 88 MB Stage-1 writing workbench is in **no branch at all** | a resource paper has no resource, and the workbench is a genuine single point of failure with no backup | yes, packaging |
| G12 **[NEW]** | **Nothing is promotable under the project's own governance.** Zero `human_input_audit: DONE` anywhere; 12 of 29 bundles omit the field | every paper and thesis claim is formally blocked | yes, operator action |
| G13 | No independent retron definition; the population, ncRNA calls, type labels and positive class all descend from one lineage | nothing measured here separates from the detector without an external anchor | partly |
| G14 | No phylogeny, therefore no ancestry null; contract rung C6 never built | co-evolution untestable | yes, medium |
| G15 | No exchangeability data in any of 185 register rows | compatibility is terminal computationally; a laboratory precondition | no |
| G16 | No untouched holdout inside PAIR-ELIG; X2 cross-fits all five folds | any pairing follow-up has nowhere to be confirmed | yes, freeze a block now |
| G17 | No biological positive control for the structural decomposition | the structural negative is inadmissible under the project's own rule | yes, low |
| G18 **[NEW]** | **The index branch lacks the evidence it declares binding.** `STAGE3A_CLOSURE.md`, `G2_DECOY_AUDIT_AND_K5_CLOSURE.md` and the Stage-3C errata are absent from `project-synthesis`; the frozen Stage-3C report contains zero references to its own errata | the "self-contained" package cannot open its own mandatory reading | yes, zero compute |

---

## 5 · ANALYSES_WORTH_REPEATING

| # | repeat | what it can overturn | cost |
|---|---|---|---|
| **R1** | **X2 uncertainty with lineage-clustered resampling** (block on retron type and on 50%-identity homolog group) | could remove level 2 from the claim set entirely | **zero compute** |
| **R2** | **Counterfactual ladder on the 423 common components**, with per-tier populations stated | already changes the finding: a 22-fold collapse at C3, then a rise | **zero compute** |
| **R3** | **Stage 3A palm rule with a declared biological positive control** (HIV-1 p66, an external reference partition, and the 17 no-call chains with ≥ 4 same-sheet strands) | decides whether the structural chapter is a negative or a retraction | low |
| **R4** | **Carriage on a fixed locus set**, scoring the same loci with each tool combination | Option A's headline must survive this or be repitched | low |
| **R5** | **The reachability control** X2's frozen design declared mandatory | closes G8 | low |
| **R6** | **Recount the subtype agreement after name normalisation**, and retire or restate the 43.85% figure | a headline number is currently a normalisation artefact (96.8% naming-only) | **zero compute** |
| **R7** | **Recompute and correct the same-strand figure** everywhere it appears | a published number is wrong by 0.7 points and hardcoded | **zero compute** |
| **R8** | **Report R − P wherever R − G is reported** | recovers the arm's strongest defensible contrast | **zero compute** |
| **R9** | **Stage 3C R1–R5** — *only if* the structural chapter must be citable | nothing from Stage 3C may be cited without them | low |

---

## 6 · ANALYSES_NOT_WORTH_REPEATING

| # | do not repeat | what closes it |
|---|---|---|
| N1 | **De novo comparative ncRNA discovery** | `ROUND2_FAIL_STOP`; the fixed interval beats the method 901 to 343 and per-type priors reach 969; the released package abstains on 94% of blinded loci and rediscovers at chance |
| N2 | **Re-inference of Mestre's classification** | her alignment and extracts are not published and not on disk; published accessions are 0 of 115 recoverable upstream. The input does not exist |
| N3 | **Placement into the historical 11-clade system** | K3 failed at 7.9% and 19.8% against ≤ 1%; no confidence statistic separates shuffled from real. The closure's own scope note is correct: this refutes one protocol, not modern phylogenetics |
| N4 | **Neighbourhood as a retron detector** | retrons 27th of 41 families inside a predeclared DEAD band. Says nothing about neighbourhood *biology* (A10) |
| N5 | **Further Stage-2 mapper analysis** | closed with six residual limitations; nothing pending but promotion |
| N6 | **Region X motif scanning** | X defined in 3 of 21 retron chains, zero motif hits in any declared interval |
| N7 | **The cross-modal retrieval ladder** | superseded by X2 at a better endpoint; two of five trivial baselines inert by construction; rung 3 fails at +0.0298 [−0.0048, +0.0633] |
| N8 | **Mantel and Mirrortree matrix correlation** | ruled out by prior decision, and uninterpretable at an effective lineage n near 9 |
| N9 | **CCA, CKA, Procrustes cross-modal geometry** | the leading canonical dimension already carries η²(type) 0.809/0.724. More geometry on the same frozen encoders re-measures type. **Unnecessary** |
| N10 | **Cross-pair compatibility matrices** | forbidden by X2's own decision record; would encode lineage similarity |
| N11 | **Laboratory candidate prioritisation** | needs pair-level discriminability (absent) and a non-circular score (none); RT-DNAs are not predictable from sequence alone |
| N12 | **Region Y × exact-RT residual join** *(package lists this APPROVED; I reject it)* | multiplies two undetermined quantities: a 1.34× ratio over 15 chains from 5 groups with range spanning 1.0, against a residual holding in 3 of 11 types with sd ≈ its estimate. Positive would be uninterpretable, negative uninformative |

---

## 7 · NEXT_ANALYSES_DEPENDENCY_GRAPH

```
LAYER 0 — zero compute, blocking
  A0 lineage-clustered variance for X2 ......... decides whether level 2 exists
  A2 fixed-population counterfactual ladder .... corrects a published shape
  A3 declare the confirmatory population ....... blocks every pairing follow-up
  A4 corrections + errata + governance ......... decides what may be written at all
        |
        v
LAYER 1 — cheap, each unlocks a claim
  A1 absolute baseline ladder .................. decides whether Option B is submittable
  A5 msr/msd decomposition ..................... opens Option C, improves B
  A6 carriage: sensitivity vs selection ........ decides Option A's headline
  A7 Stage 3A positive control ................. decides whether Ch 12 is a negative
  A8 data release and deposition ............... decides whether Option A is a resource paper
  A10 genomic architecture (NOT blocked) ....... the largest untouched biology
        |
        v
LAYER 2 — medium
  A9  relatedness backbone ..................... the null every later control needs
  A11 boundary disagreement .................... needs A5
  A14 mobility / GC deviation .................. needs A10
  A15 diversity saturation (contract C8) ....... needs clustering
        |
        v
LAYER 3 — conditional
  A12 de novo label-independent phylogeny ...... needs A9; separate decision
  A13 co-evolution ............................. underpowered regardless; reframe or drop
  --  compatibility / orthogonality ............ BLOCKED on laboratory data
```

Full specifications follow for the analyses I recommend.

---

### A0 · Lineage-clustered variance for the X2 decomposition — **ESSENTIAL**

- **Question.** What is the uncertainty on G − U, G − T, R − G and R − P when the resampling unit
  respects that 1,075 components sit inside 21 retron types and fewer independent lineages?
- **Hypothesis.** The between-lineage variance component is large and currently excluded, so the
  published intervals are too narrow, most severely for R − G.
- **Why existing evidence does not answer it.** Intervals come from an equal-weight component
  bootstrap. The bundle's `n_eff` column is a formula defect (n²/n); the package's 12.5 is a
  pair-weight Kish figure describing a different quantity. No clustered variance was ever computed.
- **Population.** All 1,075 components in `X2_COMPONENT_LEVEL_EXPORT.tsv`. No new data.
- **Inferential unit.** Retron type and, separately, RT homolog group as resampling blocks;
  component remains the observation.
- **Required inputs.** The component export and the frozen split.
- **Controls.** *Positive:* G − U, which should survive any blocking at 86.0% favourable.
  *Negative:* P − T, which should lose significance. *Reference:* the existing unclustered intervals.
- **Confounders.** Blocks are unbalanced (largest component 5,711 pairs, 18.5% of all pairs; 581
  singletons). Report a block bootstrap and a leave-one-type-out jackknife.
- **Anti-circularity.** The blocking variable is CM-derived, which here is *conservative*: blocking
  on the other modality's label can only widen intervals, never manufacture significance. Say so.
- **Falsification criterion.** Declared in advance: if R − G's lineage-blocked 95% interval includes
  zero, C-28 drops to UNDERPOWERED and level 2 leaves the claim set.
- **Expected patterns.** (i) G − U survives, R − G does not → the paper becomes a clean
  lineage-dominance result, publishable and honest. (ii) Both survive → level 2 is genuinely
  established and the paper is stronger than currently claimed. (iii) Neither survives → Option B
  is not viable and the arm becomes a methods-and-bounds chapter.
- **Claim unlocked.** A defensible uncertainty statement on the flagship result.
- **Decision affected.** Whether Option B exists.
- **Burden.** Minutes. No model training.
- **Dependencies.** None. Do this first.
- **Verdict.** **ESSENTIAL.**

### A1 · Absolute baseline ladder for the conditional decoder — **ESSENTIAL**

- **Question.** How much held-out likelihood is explained by trivial properties of the ncRNAs, and
  where do U, T, G, R, P sit relative to that floor?
- **Hypothesis.** Much of the arms' separation is compatible with per-type base composition and
  length, since the unconditional arm already sits below a uniform 4-base predictor.
- **Why existing evidence does not answer it.** No unigram, composition, positional or k-mer
  baseline exists in any bundle. The only anchor available is ln 4 = 1.38629, against which U
  (1.40666) is worse and R (1.35859) is 0.0277 better.
- **Population.** The same 30,924 pairs / 1,075 components, same folds, same weighting.
- **Inferential unit.** Component, matching the primary endpoint exactly.
- **Required inputs.** The frozen split and the 16,458 ncRNA sequences. No embeddings.
- **Controls.** B0 uniform over the emitted alphabet; B1 global 0-order composition; B2 per-type
  0-order composition; B3 per-type 3-mer or 5-mer Markov. Fitted on training folds, scored on test
  folds, reported in nats/nt.
- **Confounders.** Length varies by type; report raw and length-normalised. The alphabet includes
  ambiguity codes and `<eos>`, so compute B0 over the actual emitted vocabulary and over ACGT, both.
- **Anti-circularity.** B2 and B3 condition on the CM-derived type label, so they are the correct
  comparator for arm T specifically and must be labelled as such.
- **Falsification criterion.** Declared in advance: if arm T does not beat B3 by more than the
  reported R − T effect, no conditional-modelling claim may be made.
- **Expected patterns.** (i) R and G clearly beat B3 → effects are interpretable and Option B
  proceeds with a usable scale. (ii) T ≈ B3 → the arm measures per-type composition and the honest
  output is a negative methods result. (iii) U below B1 → confirms the decoder underfits, reported
  as a limitation of the capacity class, not of the biology.
- **Claim unlocked.** Interpretability of every number in the arm.
- **Decision affected.** Whether Option B is submittable.
- **Burden.** Hours, CPU only.
- **Dependencies.** None. Run beside A0.
- **Verdict.** **ESSENTIAL.** Do not submit Option B without it.

### A2 · Counterfactual ladder on a fixed common population — **ESSENTIAL, zero compute**

- **Question.** Does the effect decay monotonically with control strength, or does the shape come
  from four different component sets?
- **Why existing evidence does not answer it.** Tier populations are 1,019 / 832 / 1,073 / 451, and
  C4 excludes all 581 singletons by construction.
- **Population.** The 423 components common to all four tiers, with full-population figures retained.
- **Falsification criterion.** If the common-population ladder is monotone, current wording stands.
  It is not: C1 +0.01745, C2 +0.01531, C3 +0.00080, C4 +0.00156.
- **Interpretation.** Near-neighbour counterfactuals abolish the effect; C4 is not a tightening of
  C3 but a different, larger-component population.
- **Verdict.** **ESSENTIAL** (it corrects a statement already in the reporting package).

### A3 · Declare the confirmatory population — **ESSENTIAL, zero compute**

X2 cross-fits all five folds; the `embed_g2b` test fold was in training for at least three. No
untouched holdout remains inside PAIR-ELIG, and the 16 fully-external panel elements carry a
**functional** endpoint, not pairing. Freeze a component block **now**, by a rule declared before the
split is inspected, and write it into a decision record. Sixteen elements are an anecdote; say so in
advance rather than at review. **Verdict: ESSENTIAL.**

### A4 · Corrections, errata and governance — **ESSENTIAL, zero compute**

Beyond the package's eight Tier-0 items, this review forces six additions:

1. **Correct the same-strand figure** from 99.8% to 99.12% in the claim matrix, the state document,
   the retron definition document and the bundle registry, and fix the hardcoded literal in
   `findings.py:190`.
2. **Retire or restate the 43.85% subtype agreement.** 96.8% of the disagreement is naming
   convention. The provenance claim must rest on the CM authorship chain instead.
3. **Correct the SPIRE G7 second comparison** (method 60, fixed interval 87 — currently reversed),
   the Mestre table count (17 of 18), and the mapper seed description (50 proteins from
   `RTs-collection.faa`, not 66 from a prohibited input; anchors are retron-informed).
4. **Issue a Stage-3B erratum.** "CLOSED at PARTIAL" is live in five landed places, the only
   correction sits inside a Stage-3C document on another branch, and the `1RTD_B` false fire is
   unrecorded as a specificity failure.
5. **Put the binding errata on the index branch** and add a back-reference inside the frozen
   Stage-3C report, which currently contains zero occurrences of the string "errat".
6. **Resolve the governance blocker.** Decide how `human_input_audit` clears, and clear it for the
   bundles any paper will cite. Until then nothing is promotable under the project's own rules.

### A5 · msr/msd internal decomposition of the ncRNA catalogue — **ESSENTIAL, the largest opening**

- **Question.** Can the msr and msd segments, the a1/a2 inverted repeat and the branching guanosine
  be located within the 16,458 exact ncRNAs, and how well do computational calls agree with
  experimentally supported boundaries?
- **Hypothesis.** The architecture is recoverable for a large fraction of the catalogue, because the
  a1/a2 inverted repeat is a strong, local, well-defined signal independent of the covariance model
  that cut the sequence.
- **Why existing evidence does not answer it.** Never attempted. Only 7.60% of the ncRNAs carry even
  shipped structure annotation, ViennaRNA sits unused in the environment locks, and no script folds
  anything. SPIRE's failure is not relevant: SPIRE tried to **discover ncRNA families de novo**; this
  asks where segments lie **inside an ncRNA already called**. Different question, far stronger prior,
  and a real positive control set exists.
- **Population.** All 16,458 exact ncRNAs (`data/derived/rt_ncrna_oriented_v1.fna`), stratified by
  retron type and by upstream context length.
- **Inferential unit.** ncRNA instance for calls; retron type for rates.
- **Required inputs.** The oriented FASTA; ViennaRNA or equivalent; the 8 deposited retron
  RT–RNA–DNA complexes (Ec86 7V9U/7V9X/7XJG/8QBM, Ec83 9E8Z, Ec78 9VHE/9NNB, Eco8 9X94); the 175
  published extents with their exposure map.
- **Controls.** *Positive:* the deposited complexes, where the RNA chain gives experimentally
  supported geometry, plus published extents with stated msr/msd boundaries. *Negative:* group II
  intron and DGR upstream windows from the same corpus, where no msr-msd architecture should be
  found, plus dinucleotide-shuffled real ncRNAs preserving composition and length. *Reference:* a
  fixed positional split at the median msr/msd ratio.
- **Confounders.** The extent is a CM cut, so a boundary near an end may be an artefact; report the
  distance from every call to the sequence edge. Length varies by type. GC drives inverted-repeat
  detection, so stratify on it.
- **Anti-circularity.** Score against deposited structures and published extents only, **never**
  against the covariance model's own alignment columns. Any agreement with CM-internal annotation is
  same-paradigm and is reported separately, exactly as the SPIRE features are handled.
- **Falsification criterion.** Declared in advance: if the method does not beat the fixed positional
  split on the deposited complexes and the non-train-exposed published extents at a declared
  tolerance, the decomposition is not established and is not used downstream. This mirrors SPIRE's
  G7, which is the right bar, because SPIRE died to a positional prior.
- **Expected patterns.** (i) Inverted repeat found in a large majority, branching G localised,
  agreeing with structures → a real biological object exists at scale, the boundary chapter acquires
  a subject, and the pairing model gains a segmented input. (ii) Found only in well-modelled types →
  itself a result about model coverage, mapping directly onto the zero-class question. (iii) Not
  recoverable above the positional split → a clean, cheap negative that permanently closes the
  boundary arm.
- **Claim unlocked.** The first properly biological object the project would own on the RNA side,
  and a licence to ask whether the exact-RT residual localises to msr rather than msd.
- **Decision affected.** Creates Option C. Improves Option B. Rescues the boundary chapter.
- **Burden.** Days, CPU only. 16,458 sequences is small.
- **Dependencies.** None for the core.
- **Verdict.** **ESSENTIAL.** The highest-value unstarted analysis in the project.

### A6 · Carriage: detector sensitivity versus population selection — **ESSENTIAL for Option A**

- **Question.** Of the 6.6-fold spread, how much is tool sensitivity on a fixed locus set and how
  much is the tools finding different loci?
- **Hypothesis.** A substantial part is selection: PADLOC's retron rules score on the ncRNA in 17 of
  18 cases, so a PADLOC-defined population is enriched by construction.
- **Why existing evidence does not answer it.** The landed table compares seven tool-defined
  **record subsets** with different n, species counts and length distributions; its own note says a
  tool-defined subset is not a random subset.
- **Population.** A single fixed locus set: retron-labelled physical loci with ≥ 1 kb unclipped
  upstream context, which the landed context table shows is the bulk of the population.
- **Inferential unit.** Physical locus. Note the current headline is computed on **records**, which
  the project's own governance says is not a biological unit; fix that too.
- **Controls.** *Positive:* subtypes **with** a dedicated covariance model, where a hit is expected.
  *Negative:* matched non-retron RT loci, where the retron models should not fire. *Reference:* the
  fixed interval −193…−24.
- **Confounders.** Upstream context (non-monotone, must be stratified not pooled); contig clipping;
  source database, where one metagenomic source places 10.8% of RTs outside the window.
- **Anti-circularity.** Report the PADLOC-rule dependency as a structural feature, and never present
  an Ec107-like carriage rate as a positive control, since the rule defines the stratum.
- **Falsification criterion.** If all tool combinations return carriage within a declared band on a
  fixed locus set, the 6.6-fold is a selection effect and the headline is rewritten as a
  population-definition claim.
- **Expected patterns.** (i) Spread persists → the strongest version of Option A's headline.
  (ii) Spread collapses → the claim becomes "who you ask determines which loci you get", still
  publishable, differently framed.
- **Burden.** Low.
- **Verdict.** **ESSENTIAL** for Option A.

### A7 · Stage 3A with a declared biological positive control — **USEFUL, decides a chapter**

- **Question.** Is the failure to recover a three-way partition a property of RT structure, of the
  parser, or of the composition thresholds?
- **Hypothesis.** Substantially the thresholds: 17 of 19 no-call chains carry a unit with ≥ 4
  same-sheet strands, rejected only on `frac_E`.
- **Population.** The 46 primary chains, plus HIV-1 p66 and a small set of RTs with reference
  partitions from an external structural classification.
- **Controls.** *Positive:* HIV-1 p66 and chains with an accepted external partition; the instrument
  must recover these or it is unfit. *Negative:* non-RT α/β proteins of similar size.
- **Anti-circularity.** Use an external structural classification, not narrative literature
  boundaries — the Stage-3C 0-of-8 result is precisely why narrative boundaries cannot serve.
- **Falsification criterion.** If the instrument fails the external positive control, the negative is
  reclassified `INSTRUMENT_VOID` and may not be published as biology. Declare before running.
- **Expected patterns.** (i) Control recovered, 0.565 stands → a genuine publishable negative.
  (ii) Control not recovered → withdraw the negative; what remains is the literature-disagreement
  result, which is parser-independent and the better paper anyway.
- **Verdict.** **USEFUL**, and required before Stage 3A is written up as biology.

### A8 · Data release and deposition — **ESSENTIAL for Option A, not an analysis**

`docs/DATASET_REGISTRY.md` states *"None of the files in this document are in GitHub"*; every row
reads LOCAL ONLY; there is no DOI, deposit, release archive or data-availability statement, and every
`zenodo`/`figshare` occurrence is an inbound reference or a downloader package. **Minimum product:**
the 501,561 exact-RT catalogue with hashes and unit keys; the 16,458 oriented ncRNAs; the unpooled
per-locus tool-call table; the pair table with multiplicity and geometry flags; the unit-ladder
crosswalk; the negative-results register. Deposit under a DOI with a schema document, a licence and
resolved provenance for the underlying assemblies. **Separately and urgently: back up the 88 MB
Stage-1 writing workbench, which exists in no branch.** **Verdict: ESSENTIAL.**

### A10 · Genomic architecture around retron RTs — **ESSENTIAL, and cheaper than believed**

- **Question.** What is the genomic architecture around retron RTs, and how does it differ from other
  RT families?
- **Hypothesis.** Retron loci have a distinguishable architecture (gene density, operon-like spacing,
  strand topology, RBS features) even where accessory identity is unknown.
- **Why existing evidence does not answer it.** The package records this as blocked on
  `has_sequence = False`. **That blocker applies to identity, not architecture.** All 44,242,429 CDS
  occurrences carry contig, start, end, strand, length, GC content, RBS motif, RBS spacer, start type
  and partial flag; the ±10 kb window sequence is on 100% of records; and 44,310,231 rows are already
  landed in `data/derived/rt_window_cds_v1.parquet`. The project's own handover says it:
  *"Neighbourhood architecture is available; neighbourhood identity is not."*
- **Population.** All RT-anchored loci, stratified by RT family, with retrons as the focal class.
- **Inferential unit.** Physical locus, with per-family rates on their own denominators.
- **Controls.** *Positive:* group II intron loci, whose architecture is known to differ. *Negative:*
  family-matched and neighbour-matched random windows. *Reference:* the genome-wide CDS spacing
  distribution from the same assemblies.
- **Confounders.** Contig clipping (38–72% `true_start_clipped` by database, and 71.75% in one),
  window edges, and the fact that operon calls swing from 55.0% to 16.7% with the gap threshold, so
  report a threshold sweep rather than a single value.
- **Anti-circularity.** Treat this as **description, never detection**: neighbourhood as a
  discriminator is already refuted (retrons 27th of 41 families). Do not define the RT core with the
  GII-centred mapper, which truncates N-terminally on 39 of 62 chains.
- **Falsification criterion.** Declare the architectural features and the effect floor before
  computing; report per-family distributions, never a pooled rate, since pooling has already cost
  this project a 112-fold error.
- **Claim unlocked.** The largest genuinely descriptive biology available, and a real Chapter.
- **Burden.** Low for architecture. Ibex and full Pfam-A only for identity, as a later phase.
- **Verdict.** **ESSENTIAL** in its architecture half. This is my second-strongest recommendation
  after A5, and it is currently believed impossible.

### A14 · Mobility and horizontal-transfer signal — **USEFUL, substrate already present**

- **Question.** Do retron loci show compositional signatures of recent horizontal acquisition?
- **Why now.** Per-CDS GC content exists on 44.2 M CDS and the ±10 kb window DNA on 100% of records,
  so GC deviation of the retron locus against its genomic background is computable today. No
  mobility analysis of any kind exists in the project.
- **Controls.** *Positive:* known mobile families in the same corpus. *Negative:* housekeeping CDS
  from the same windows. *Reference:* genome-wide GC distribution per assembly.
- **Confounders.** Genome GC varies enormously across taxa; work in per-genome z-scores, never raw
  GC. Metagenomic bins have unreliable backgrounds, so stratify by source and by completeness.
- **Verdict.** **USEFUL**, and cheap. Do it with A10.

### A15 · Diversity saturation and sampling correction — **USEFUL, and contractually owed**

- **Question.** Is observed retron diversity saturating, and how much does redundancy and database
  composition change the answer?
- **Why it matters.** Contract claim **C8 is `UNPROVEN` and has never been measured.** The only
  richness figure anywhere is a single-row illustrative Chao1 (78,287 observed, 140,731 estimated,
  ratio 1.8), explicitly labelled "illustration". Any resource paper will be asked this.
- **Blocker.** No sequence clustering exists on either side; the workbench states it.
- **Controls.** Rarefy on corrected sampling units (physical locus, species, assembly), not on
  records, and report all three. *Reference:* the same curves computed on raw records, to show how
  much redundancy inflates them.
- **Verdict.** **USEFUL.** Needed for Option A to answer its most predictable reviewer question.

### A9 · Relatedness backbone — **USEFUL, enabling**

An identity/ANI-based nested blocking structure over RT sequences, explicitly **not** a publication
tree. A0 needs blocks; any correspondence test needs a null. Acceptance test: permutation within
blocks destroys G − U while permutation across blocks does not. **Verdict: USEFUL.**

### A11 · Boundary disagreement on non-train-exposed extents — **USEFUL, after A5**

The ~95 published extents not train-exposed. The exact-hash (12) versus blastn (80) gap **is** the
measurable quantity, and A5 would explain it mechanistically. Score against published extents only,
never against CM cuts; SPIRE positional features may be priors and may never be evaluated against CM
truth. No supervised predictor at this n without a stated minimum detectable effect.
**Verdict: USEFUL.**

### A12 · Modern label-independent de novo RT phylogeny — **OPTIONAL, separate decision**

Genuinely open, not refuted; the package is right to reopen it, and the Mestre closure's own scope
note agrees (*"not evidence that modern retron phylogenetics or placement is impossible"*). I still
rank it optional: it is large, its main consumer (A13) is probably underpowered regardless, and its
classification payoff competes with a well-resourced field. The distinctive angle, an all-versus-all
**structural** distance matrix over 1,919 proteins never built as a tree, is real but is a second
project. Only after A9, preregistered, both answers reportable. **Verdict: OPTIONAL.**

### A13 · Phylogeny-corrected co-evolution — **DEFER, probably abandon as a target**

Even with A9 and A12 complete, the between-lineage effective sample size is roughly 9 to 14. A
correspondence test at that effective n, on an effect supported in 3 of 11 types, will return
"undetermined". Say so in advance rather than spending compute on an uninterpretable null.
**Verdict: UNNECESSARY as framed.** Reframe as a prospective chapter stating the power requirement,
or drop it.

### Items from the request assessed and not recommended

| proposal | verdict | reason |
|---|---|---|
| Mantel / Mirrortree | unnecessary | ruled out by prior decision; uninterpretable at this effective n |
| CCA / CKA / Procrustes | unnecessary | the leading canonical dimension already carries η²(type) ≈ 0.8 |
| Region X analysis | unnecessary | 3 of 21 retron chains, zero motif hits in declared intervals |
| Region Y × exact-RT join | unnecessary | multiplies two undetermined quantities |
| Supervised ncRNA boundary prediction | premature | no truth at scale; reframe as A11 after A5 |
| Panel as model validation | prohibited | 159 of 175 exposed; only a functional prospective endpoint is legitimate |
| 16 external elements as confirmatory population | prohibited | wrong endpoint, and n = 16 |
| Compatibility / cross-pair models | blocked | needs laboratory exchangeability data that exists nowhere |
| Experimental candidate selection | prohibited | needs pair-level discriminability, not demonstrated |
| Repair of the Mestre reconstruction | unnecessary | the input does not exist |
| Repair of Stage 3B | essential but documentary | erratum only (A4) |
| Repair of Stage 3C (R1–R5) | conditional | only if the structural chapter must be citable |

---

## 8 · PAPER_OPTIONS

Five architectures, tested adversarially. I do **not** recommend publishing every arm.

### Option A · The detector defines the retron: a resource and annotation-limits paper — **VIABLE AFTER BOUNDED WORK. Write this first.**

- **Central claim.** A genome-scale retron population is an artefact of the detector that defined it,
  and the size of that artefact is measurable. A 501,561-sequence exact-RT catalogue on explicit
  analytical units in which no two units convert by a constant; ncRNA carriage moves 6.6-fold with
  the tool combination; all 21 covariance models in the production pipeline come from one author and
  three nominally independent tools descend from them; and roughly 40% of retron-labelled loci have
  no detected ncRNA even at full upstream context.
- **Minimum figure set.** (1) unit ladder and funnel with the redundancy decomposition;
  (2) extraction asymmetry across seven tool strata, with the fixed-locus-set result from A6 beside
  it; (3) the annotation provenance chain as a directed graph; (4) carriage against upstream context
  **plotted in full so the non-monotonicity and the 60.5% ceiling are visible**; (5) subtype ×
  covariance-model near-diagonal heatmap captioned *neither can validate the other*; (6) phylum
  prevalence on a genome denominator with intervals; (7) an artefact dissection.
- **Evidence already available.** All of it, landed and reviewed, including the phylum-prevalence
  tables that no synthesis document currently uses.
- **Missing decisive evidence.** A6, A8, and preferably A15 (saturation). Correct the same-strand
  figure and retire the 43.85% before drafting.
- **Biggest reviewer objection.** *"This is descriptive, and your headline compares different
  populations rather than different detectors."* A6 answers the second directly; the first is
  answered by leading with the annotation-limits result rather than the catalogue.
- **Second objection.** *"Where is the resource?"* Currently unanswerable. A8 is not optional.
- **Third objection.** *"Is your diversity saturating?"* A15.
- **Verdict.** **Viable after bounded work.** Strongest paper, and its novelty does not depend on any
  contested number.

### Option B · Lineage versus exact sequence in RT–ncRNA correspondence — **VIABLE ONLY AFTER A0 AND A1, AND ONLY IF REPITCHED**

- **Central claim, as it must now be stated.** Conditional sequence modelling decomposes
  RT-to-ncRNA predictive information into a large lineage component and a small exact-sequence
  residual, setting a quantitative upper bound on how much partner-specific information is
  recoverable from sequence alone. About three-quarters of the RT-associated gain is explained at
  the 50%-identity lineage level; near-neighbour counterfactuals abolish the remainder; biochemical
  compatibility is untested and untestable with the assets held.
- **The repitch is the point.** This is a **bounding** paper. Framed as "the exact RT carries
  partner information" it will not survive review (§3 item 1). Framed as "how much of apparent
  pairing specificity is just lineage, measured properly" it is a genuine contribution and the
  negatives become the content.
- **Minimum figure set.** (1) arm ladder U → T → G → R → P **with absolute baselines B0–B3 on the
  same axis**; (2) counterfactual ladder on a fixed population with the component-versus-pair
  weighting and the C3 sign flip; (3) lineage share with lineage-clustered intervals;
  (4) split and leakage schematic (82.46% of held-out RTs have a ≥ 0.50-identity training relative;
  100% of held-out pairs reachable from training); (5) per-retron-type forest plot of R − G showing
  the 3-of-11 support honestly.
- **Missing decisive evidence.** A0, A1, A2, R8, and the unrun reachability control.
- **Biggest reviewer objection.** *"Your unconditional model is worse than uniform over four bases,
  so what is the scale of these differences?"* Fatal if unanswered, fully answered by A1.
  **Second:** *"Your 'beyond type' control uses a label derived from the RNA itself."* The G and P
  arms are the defence and they are protein-side, so this is answerable today. **Third:** *"1,075
  components inside 21 types is not 1,075 independent observations."* Answered only by A0.
- **Verdict.** **Viable after bounded work**, conditional on A0 and A1 not killing it. Assign a
  genuine probability of failure.

### Option C · The msr-msd architecture of retron ncRNAs at scale — **PREMATURE TODAY, POTENTIALLY THE BEST PAPER**

- **Central claim (prospective).** The msr and msd segments, the a1/a2 inverted repeat and the
  branching guanosine can be located across 16,458 retron ncRNAs; the architecture varies
  systematically by type; and published extents disagree with covariance-model cuts in a way the
  decomposition explains.
- **Why it could be the best.** It is the only proposal that yields a **biological object** rather
  than a rate or a bound. It has a genuine positive control (8 deposited complexes). Its scoring is
  independent of the annotation lineage. It is cheap. And it addresses what a retron actually *is*,
  which nothing in the current arms touches.
- **Evidence already available.** Nothing analytic. The inputs are all on disk.
- **Missing decisive evidence.** All of A5.
- **Biggest reviewer objection.** *"Your sequences are covariance-model cuts, so your boundaries
  inherit the model."* Answered by scoring against structures and published extents only, and by
  reporting every call's distance to the sequence edge.
- **Verdict.** **Premature today; viable after A5.** Higher expected value than Option B, lower
  certainty than Option A. Run A5 before fixing a paper order.

### Option D · RT architecture across experimental structures — **DO NOT WRITE**

The bundle carries a `FAIL_BLOCK` 4.5/10 review with five upheld blockers and four withdrawn rows,
and five unauthorised repairs. Beyond that: the register is a convenience panel of 62 locally cached
chains with no systematic search and no coverage estimate; 50 of 62 are cryo-EM; all 31 groups fall
in one structural cluster; **all 19 truth-bearing chains are non-retron**; Tier B was never opened;
and the anchoring negative is a threshold artefact. **Verdict: premature, probably permanently.**
Keep as thesis chapters. Do not spend R1–R5 unless the chapter must be citable.

### Option E · The fingers/palm/thumb vocabulary is not operationally defined — **VIABLE NOW, SHORT, CHEAP**

- **Central claim.** The conventional three-domain description of reverse transcriptases is not
  reproducible as a boundary specification: literature fingers coincide with a structural unit 0 of
  8 times; a combined fingers+palm region coincides 1/1; two 2026 papers on the same protein publish
  incompatible partitions in the same numbering frame; an inherited boundary product builds two of
  three domains as arithmetic residuals and places one chain's catalytic aspartate outside its own
  palm.
- **Why it survives when Option D does not.** It is a claim about the **literature**, not about the
  project's parser. No Stage-3A or Stage-3B defect touches it.
- **Biggest reviewer objection.** *"This is a comment, not a paper."* Fair. Publish as a short
  methods or perspective piece, or fold it into Option A. Do not inflate it.
- **Verdict.** **Viable now.** The lowest-effort real output the project owns.

### What I would not do

No classification or evolution paper. The audit material belongs inside Option A. A classification
paper requires A12, which is optional.

---

## 9 · THESIS_ARCHITECTURE

The package's architecture is right in shape and wrong in its spine. The spine is the convergence
claim, which P1 rejects. Replacement:

> **Proposed spine.** A genome-scale retron catalogue is not a sample of retrons; it is a sample of
> what one annotation lineage can see. This thesis builds such a catalogue on explicit analytical
> units, measures how much of every downstream quantity is attributable to the detector rather than
> to biology, and then tests how far sequence alone can go in recovering the RT–ncRNA relationship
> that defines a retron. Broad lineage carries most of the recoverable information; partner-specific
> information is small and does not survive near-neighbour controls; and the properties most often
> treated as diagnostic are either not universal, not operationally defined, detector-derived, or
> untested. **Where an instrument stopped, this thesis distinguishes the cases where biology stopped
> it from the cases where the instrument did.**

That final sentence is the real contribution, and it converts the artefact-negatives from
embarrassments into the methodological point.

| part | ch | title | status | source | paper |
|---|---|---|---|---|---|
| I · The object | 1 | What a retron is, three ways | framing | `WHAT_IS_A_RETRON.md` | frames A |
| | 2 | From mining records to biological objects | **ESTABLISHED** | `dbchar_g1–g4` | A |
| | 3 | Annotation limits as a measurable object | **ESTABLISHED (methodological)** | `g6`, `g3`, `g7b` + **A6** | core of A |
| | 4 | Where retrons are: taxonomy, prevalence and sampling | **landed but unused** + **A15** | `t34`, `t35`, `N7` | A |
| II · Instruments | 5 | A frozen residue-level instrument for RT conserved states | **METHOD**, with its full freeze history | `rt07_g1–g5`, `g4b` | optional |
| | 6 | What RT0–RT7 can and cannot mean | **ESTABLISHED (bounded) + clean negative** | `g7a` + erratum | strong chapter |
| III · The RNA | 7 | **The internal architecture of retron ncRNAs** | **NEW — from A5** | A5 | **Option C** |
| | 8 | Boundaries: published extents versus model cuts | **from A11** | A11 | part of C |
| IV · Architecture | 9 | **What surrounds a retron** | **NEW — from A10, A14** | A10, A14 | possible |
| V · The pairing question | 10 | Lineage versus exact sequence | **complete, pending A0/A1** | `embed_x2`, `d7d3ece` | **Option B** |
| | 11 | What sequence cannot do, and why compatibility is a laboratory question | bounded negative | X2 limits + 185-row register | part of B |
| VI · Failed hypotheses | 12 | De novo ncRNA discovery: beaten by a fixed interval | **FAILED, clean** | SPIRE | — |
| | 13 | Historical classification: reproduction, placement, and what stays open | **FAILED twice, with a distinction** | mestre-audit | — |
| | 14 | Structural decomposition: **a negative, or an instrument?** | **CONTESTED — resolve with A7** | Stage 3A/3B/3C | Option E |
| VII | 15 | The experimental layer and what it can support | prospective | 185-row register | future work |
| | 16 | Minimum remaining programme | prospective | this document | — |

### Carrying negatives without weakening the argument

Four kinds, kept visibly apart:

1. **Clean refutations with a comparator.** SPIRE (901 versus 343) and the placement failure
   (shuffled at 7.9% against ≤ 1%). These are results.
2. **Instrument stops, honestly relabelled.** Stage 3B's fired kill criterion, with the `1RTD_B`
   false fire reported. The point is that a stop rule is worth having.
3. **Contested negatives that A7 resolves.** Stage 3A. Do not write it until A7 decides. Either
   outcome is publishable; asserting the wrong one is not.
4. **Bounds, not nulls.** The pairing limit, so that "we could not demonstrate pair-level
   discrimination" is never read as "it does not exist".

### Changes from the package's version

- The convergence sentence is removed.
- The structural chapter is demoted to contested pending A7, and Option D is dropped as a paper.
- Three new chapters (4, 7, 9) appear from landed-but-unused taxonomy work, from A5, and from A10.
  These are the chapters that make the thesis about retrons rather than about RT records.
- Chapter 3 acquires A6, without which its headline is attackable.

---

## 10 · MINIMUM_DECISIVE_WORK

**Tier 0 — zero compute, blocks everything (about one week)**

| item | decides |
|---|---|
| **A0** lineage-clustered variance | whether the exact-RT residual is a claim at all |
| **A2** fixed-population counterfactual ladder | corrects a shape already published internally |
| **A3** declare and freeze the confirmatory population | unblocks every pairing follow-up |
| **A4** six corrections, the Stage-3B erratum, errata onto the index branch, and the governance decision | what may legitimately be written |
| **R8** report R − P everywhere R − G appears | recovers the arm's strongest number |

**Tier 1 — cheap compute, each decides a paper (about six to eight weeks)**

| item | decides |
|---|---|
| **A1** absolute baseline ladder | whether Option B is submittable |
| **A5** msr/msd decomposition | whether Option C exists; improves B; rescues the boundary chapter |
| **A6** carriage on a fixed locus set | Option A's headline framing |
| **A10** genomic architecture (architecture half only) | whether the thesis has a fourth biological chapter |
| **A7** Stage 3A positive control | whether the structural chapter is a negative or a retraction |
| **A8** data release and deposition | whether Option A is a resource paper |

**Tier 2 — only if a fifth arm is wanted:** A9, A11, A14, A15, and A12 as a separate decision.

**Explicitly outside the minimum.** Co-evolution. Compatibility and orthogonality modelling.
Cross-pair scoring. Candidate nomination. Stage-3C R1–R5 unless the chapter must be citable.
Region X and Region Y in any form.

**Assessment.** Tier 0 plus Tier 1 is roughly two months, most of it cheap, and it converts a project
with one contested positive result into a thesis with two solid papers, one likely third, one short
fourth, and a properly framed negative-results contribution. That is a defensible PhD.

---

## 11 · TOP_5_OPERATOR_DECISIONS

**D1 · Do you accept that the convergence claim must be withdrawn?**
"Four independent instrument families each stopped at the same boundary, so the information is
type-level" is the spine of the current thesis architecture and I do not accept it: the families
share the annotation lineage that defines their target, and at least two stops are instrument
artefacts. *If you accept:* §9's replacement spine applies and the structural chapter waits for A7.
*If you reject:* you need an argument for the four instruments' independence that I could not
construct from the evidence. **This precedes everything, because it determines what the thesis is
about.**

**D2 · Do you authorise A0 and A1, and will you accept their verdict on Option B in advance?**
Together they cost hours and decide whether the flagship positive result survives. The important
half is the **pre-commitment**: declare now that if R − G's lineage-blocked interval includes zero,
level 2 leaves the claim set, and that if arm T does not beat a per-type Markov model by more than
the reported effect, Option B is not written. Deciding after seeing the numbers is exactly the
failure mode the project's governance exists to prevent.

**D3 · Do you fund A5 (msr/msd) and the architecture half of A10?**
My two strongest recommendations, and both are things the project has never tried. A5 is cheap, has
a real positive control in the 8 deposited complexes, scores independently of the annotation lineage,
and produces a biological object. A10 was believed blocked and is not: 44.3 million CDS rows with
coordinates, strand, GC and RBS features are already landed, and the ±10 kb window is on every
record. Together they would give the thesis the two biological chapters it currently lacks.

**D4 · How does `human_input_audit` clear, and is the resource going to be released?**
Two blockers that are not scientific and are both absolute. Nothing in this project is promotable to
a paper or thesis claim under `BUNDLE_SPEC.md` while zero bundles carry `DONE`. And Option A has no
releasable product: every dataset row reads LOCAL ONLY, there is no DOI, and the 88 MB Stage-1
writing workbench exists in **no branch, published or not**. **Back that workbench up today,
irrespective of every other decision on this list.**

**D5 · Do you spend the Stage-3C repairs, or close the structural arm as a chapter?**
I recommend closing it. The repairs are cheap but do not fix the register's selection, the
retron-free truth set, or the contested Stage-3A negative. Run **A7** instead, which decides whether
the chapter is a negative or a retraction, and publish the literature-disagreement result (Option E)
as the structural arm's real output. *If you want Option D:* R1–R5 plus A7 plus a systematic
structure search is the minimum, and that is a second project.

---

## Appendix · Findings in this review not present in the package

**[D]** = derived by me from landed artefacts during this review.

| # | finding | source |
|---|---|---|
| 1 | **[D]** The unconditional arm (1.40666 nats/nt) is worse than uniform over four bases (1.38629); the best arm is 0.0277 below uniform; no absolute baseline exists anywhere | X2 `RESULTS.md` |
| 2 | **[D]** R − G is supported in **20 of 36** powered strata and **3 of 11** powered retron types, against 28 of 36 for R − T. Only the R − T figure is quoted | `SENSITIVITY_STRATA.tsv` |
| 3 | **[D]** R − G favours the exact RT in **55.35%** of components; the package reports 86.0% for level 1 and 52.5% for pair level but omits this | `LINEAGE_CONTROL.tsv` |
| 4 | **[D]** \|P − T\| = 0.005904 (57.02%) exceeds \|R − G\| = 0.005507 (55.35%) | same |
| 5 | **[D]** R − P = −0.018797 [−0.02457, −0.01348], 59.7% favourable, is the arm's strongest defensible contrast and appears in no document | `X2_COMPONENT_LEVEL_EXPORT.tsv` |
| 6 | **[D]** On the 423 components common to all four tiers the ladder is **not monotone**: C1 +0.01745, C2 +0.01531, C3 +0.00080, C4 +0.00156; C4 contains 0 of 581 singletons | same |
| 7 | **[D]** Component sizes are extreme: median 1 pair, 581 singletons, top 5 hold 55% of tokens, largest holds 18.5% of pairs. The headline is an **equal-weight** component mean, so a singleton counts as much as the 5,711-pair component; token-weighting shrinks G − U to −0.0257 and R − G to −0.0038 | same |
| 8 | The landed `n_eff` column is a formula defect (n²/n) reading 1075.0, contradicting the package's 12.5 | `y04_analyse.py` |
| 9 | Strata are **component-overlapping** (components sum to 1,132–1,875 per axis against 1,075), so the relatedness gradient uses non-disjoint sets | `SENSITIVITY_STRATA.tsv` |
| 10 | A control declared **mandatory** in X2's frozen design has no implementation, table or value | `DESIGN.md` §69-72 |
| 11 | The softener "even Q1 sits above 0.983" is self-contradictory: Q1 is *defined* as cosine < 0.983 | `RESULTS.md` |
| 12 | TypeIIIA2 is the one stratum where the type label significantly beats the observed RT (+0.017374 [+0.002376, +0.036975]); counted as "1 above" and never named, while two non-significant reversals are named | `SENSITIVITY_STRATA.tsv` |
| 13 | **[D]** The same-strand figure is **99.12%, not 99.8%**; its stated source counts exist in no table; it is a hardcoded literal in `findings.py:190`; g7b silently corrects it; the wrong value propagates into four package files | `g3_same_strand.tsv` |
| 14 | **[D]** **96.8% of the DefenseFinder/PADLOC subtype disagreement is naming convention** (`Retron_II` vs `retron_II-A` 179,027; `Retron_III` vs `retron_III-A` 19,696 of 205,327). The 43.85% agreement figure does not support the provenance claim it is used for | `g6_subtype_disagreement_pairs.tsv` |
| 15 | **[D]** The upstream-context gradient is non-monotone and the dominant bin (419,613 loci, > 9 kb unclipped) sits at **60.52%** carriage, so ~40% of retron loci lack a detected ncRNA at full context. The 87.27% figure covers ~6.6% of the population | `t24_carriage_by_upstream_context.tsv` |
| 16 | The CM-coverage explanation of the zero class is asserted only in the synthesis layer and performed by **no landed table**; true zero subtypes are VII-A1, VII-A2, VIII, X (986 loci), and XII's near-zero is rule-definitional, not a model gap | `t21`, `t22`, g7b `REPORT.md` |
| 17 | In **17 of 19** no-call Stage-3A chains a unit does carry ≥ 4 same-sheet strands, rejected only on composition; the palm meets 2 of its 3 bars | Stage 3A closure |
| 18 | Stage 3B's declared cleanest negative control, HIV-1 p51 `1RTD_B`, **fires** (D110–D186, sep 76, 3.52 Å) and was recorded as a decoy, not a specificity failure | `CONTROLS.tsv`, K5 audit |
| 19 | Stage 3B has **no PASS bar at all**; each threshold edge is set by a single extreme member of the 19 truth pairs | `g2_frozen_parameters.tsv` |
| 20 | Two landed Stage-3B files disagree on whether Tier B contains a HARD_PAIR chain | `TRUTH_TABLE.tsv` vs `REPLICATE_GROUPS.tsv` |
| 21 | The Stage-3A closure's "identical primary-population statistics" hides a pooled BJ-p4 flip from STABLE 0.770 to NOT_STABLE 0.314 | `rt_units_p4.report.txt` |
| 22 | UG25 was the **third** holdout attempt: UG5 v2 failed outright, UG5 v3 was reviewed FAIL/BLOCK 5/10, G2L FAIL/BLOCK 4/10 with the cutoff fitted at the winner-flip point and a governance breach recorded | Stage-2 decision records |
| 23 | The launcher's original g4 design required **four** validation arms; none ran, and a retroactive amendment substituted one n = 28 run | `LAUNCHER_02`, 2026-09-17 amendment |
| 24 | Stage-2's declared positive control AC1 was **arithmetically unpassable** (ceiling 84.8% against a required 95%) and the mapper was frozen anyway; the frozen anchor table lives inside the *failed* UG5 bundle | `acceptance_criteria.tsv`, g4 review record |
| 25 | The mapper's seed is misdescribed: 50 proteins from `RTs-collection.faa`, not 66 from `ALIGN_000044`, which was a **prohibited** input; and the anchors are **retron-informed** (ALL_PARTNERS across 7 families, Retrons n = 102) | `g4a_repaired` tables, `PREDECLARATION.md` |
| 26 | The Mestre placement **positive control (M2c) was declared and never run** (commented out in `run.sh`), so the instrument was never shown able to place a correct query while confidently placing shuffled noise at 7.9–19.8% | `run.sh:39-40` |
| 27 | On the Mestre substitute panel, **38 of the 48 that extracted were confidently placed (~79%)**: when the extraction gate does not fire, wrong proteins are confidently placed | `CONTROLS_v3.tsv` |
| 28 | Mestre reproduction is **17 of 18** tables, not 18 of 18 (SVGs 0 of 3); "10/11 on the published tree" is purity-only, 8/11 or 9/11 with support | `COMPARISON.tsv`, `REPORT.md:119` |
| 29 | SPIRE's G7 second comparison is **reversed** in the package: landed values are method 60, fixed interval 87. G7 was added in Amendment 2 after DEV calibration | `HELDOUT_DECISION.json` |
| 30 | SPIRE has **no end-to-end known-motif recovery control**; the Rfam set was located and explicitly not used | SPIRE post-mortem |
| 31 | **[D]** `human_input_audit: DONE` appears in exactly one file in the repository: the spec that defines the field. 29 files carry PENDING; 12 of 29 bundles omit it entirely | repository-wide grep |
| 32 | **Accessory architecture is not blocked.** All 44,242,429 CDS carry coordinates, strand, length, GC, RBS motif/spacer and partial flag; the ±10 kb window is on 100% of records; 44,310,231 rows are landed in `rt_window_cds_v1.parquet` | corpus schema census, `data/README.md` |
| 33 | **No rarefaction, accumulation or saturation analysis exists**; contract claim C8 has never been measured; the only richness figure is a one-row illustrative Chao1 | repository-wide search |
| 34 | **No ecology**: `tax_environment` restates `source_database`; GEM's real habitat and geocoordinate columns were identified and never analysed | `g5_environment_by_database.tsv` |
| 35 | **No mobility or horizontal-transfer analysis**, though per-CDS GC on 44.2 M CDS and the window DNA are present | repository-wide search |
| 36 | **No released data product**: every dataset row reads LOCAL ONLY, no DOI, no deposit, no data-availability statement; the 88 MB Stage-1 workbench is in **no branch** | `docs/DATASET_REGISTRY.md` |
| 37 | The index branch lacks the evidence it declares binding, and the frozen Stage-3C report contains zero references to its own errata | `git cat-file` on `project-synthesis` |
| 38 | `project-synthesis` is 2 commits ahead of origin and unpushed; three evidence branches are unmerged into `main`; no Stage-1 closure decision record exists; `VOID_DO_NOT_CITE.md` has not been consulted | git state, `docs/decisions/` |


---

# 12 · THE ORIGINAL PROGRAMME VISION, ASSESSED

*Added 2026-09-20 after the operator supplied the twelve-step programme the project was conceived
around. This section assesses that programme against the reconstructed evidence, and adds six
analyses (A16–A21) plus two standing design rules that the earlier sections did not contain.*

## 12.1 · Overall judgement

**The vision is better than what was executed, and the divergence between them explains most of the
current state.** Three specific divergences account for nearly every weakness in §1:

| the plan said | what happened | consequence |
|---|---|---|
| analyse **smartly curated subsets** pulled from the pipeline (steps 2, 6, 8) | either corpus-wide (369,381 RTs) or a convenience panel (62 cached structures) | populations are detector-defined or selection-biased; no step has a designed population |
| ncRNA architecture (step 9) **before** embedding analysis (step 10) | step 10 was completed; step 9 was never started | the pairing model conditions on and predicts an uncharacterised RNA blob, which is a large part of why its result is weak and uninterpretable |
| phylogeny (step 3) early, unlocked by the RT0–RT7 work | never attempted; steps far downstream were completed instead | the project has no relatedness backbone, so every later control is a proxy |

The dependency order in the plan is sound. The **serial framing is not**: as a pipeline, a failure at
step 3 blocks steps 7 through 12, and four arms have already failed. Reframe it as a directed graph
in which each node has its own publishable payoff, so that a failed node costs one chapter rather
than the programme.

## 12.2 · Step by step

**(1) Large-scale mining, usable datasets, geometry priors — DONE, and it is the project's best
asset.** With two corrections carried from §3: the same-strand prior is 99.12%, not 99.8%, and the
geometry is partly circular because the covariance models were trained on msr-msd in that position.
The priors are real but they are priors about *detected* systems.

**(2) Define RT0–RT7 across all RTs; "not all of the RT core domains are detected from
[retrons]" — PARTLY DONE, and your parenthetical is the most valuable sentence in the programme.**
See §12.3. The project measured this, recorded it as a **confound**, and never asked whether it is a
finding. A landed table already contains most of the answer, and the answer is not what the project
assumed.

**(3) Phylogeny, with core selection driving topology — NEVER ATTEMPTED, and your framing upgrades
it.** §7 ranked a de novo phylogeny OPTIONAL because it read as a classification exercise competing
with a well-resourced field. Your motivation is different and much stronger: *the RT core is
selected, not the whole RT, and the selection changes the tree.* That is a **methods claim about the
field's published phylogenies**, it is directly testable, and the project holds the one asset
required — a frozen instrument that defines a per-residue core on 369,381 proteins. It also explains
the Mestre re-inference failure mechanistically, since her alignment and extracts, that is, her core
selection, are exactly what is unpublished. **Upgraded to USEFUL and respecified as A17.**

**(4) Blind discriminative motif detection, "in combination" — NOT DONE, and the word *in
combination* is the part that matters.** Every discriminative attempt in the project was
single-feature: Region X alone, Region Y alone, neighbourhood alone, catalytic state alone. Each
failed. A combinatorial discriminator is a different and legitimate question. But it needs an
anti-circularity anchor, because a classifier trained on MyRT and PADLOC labels re-learns the models
that produced them. §12.4 supplies both the anchor and, unexpectedly, the place to look.
**Specified as A18.**

**(5) Structural methods on divergent sequences — PARTLY DONE, and your version is better than what
was run.** The structural arm used 62 locally cached experimental chains with no systematic search,
50 of 62 cryo-EM, and all 31 groups in a single structural cluster. Your proposal, predicting
structures across the sequence diversity, directly fixes that. Stage 3C's binding requirements
exclude predicted structures, but that was a scoping decision, not a scientific one, and it should
be revisited. **Specified as A21.**

**(6) Neighbourhood on smartly selected subsets — AVAILABLE NOW for architecture.** Your instinct to
subsample is right for the *identity* half, which needs Ibex and full Pfam-A. It is unnecessary for
the *architecture* half: coordinates, strand, length, GC, ribosome-binding motif and spacer exist on
all 44.2 million neighbouring CDS, and 44,310,231 rows are already landed. See A10.

**(7) Phylogenetics and co-evolution — the first half is A17; the second half should be dropped as a
target.** Even with a backbone and a tree, the between-lineage effective sample size is roughly 9 to
14. A correspondence test at that effective n, on an effect supported in 3 of 11 retron types, will
return "undetermined". Reframe it as a chapter that states the power requirement, or drop it.

**(8) De novo ncRNA discovery and covariance-model creation on retron-labelled RTs plus ~600 nt
upstream — CLOSED as stated, OPEN in a narrower form.** This was attempted. It lost decisively to a
fixed positional interval: the method recovers 343 at IoU ≥ 0.5, the interval −193…−24 recovers 901,
and per-type intervals recover 969. Your ~600 nt window does not change that, since the winning
interval sits entirely inside it. **But the narrower task survives and is important**: build models
for the **six subtypes that have none** (VI, VII, VIII, X, XI, XII), rather than discovering new
families. That task has a positive control the project never ran and which the whole zero-class
argument depends on. **Specified as A19.**

**(9) Annotate a1/a2 and msr/msd, then expand the high-confidence pair set — the single most
valuable unstarted item, and the second half is the part I under-weighted.** Section 7 already makes
the annotation itself essential (A5). Your consequence is what makes it strategic: if msr/msd
architecture can be called **independently of the covariance models**, then pairs can be defined by
architecture rather than by model hit. That is a route out of the annotation-lineage circularity
that is the deepest problem in the project, and it may reach into the ~40% zero class.
**Specified as A20.**

**(10) Embeddings for RT–ncRNA association — DONE, and bounded.** See §1.3. Its two blocking
defects, no absolute baseline and no lineage-clustered variance, are cheap to fix and must be fixed
before anything is built on it.

**(11) Couple the priors and retrain — LEGITIMATE, but it inherits every bound.** Adding
architecture, geometry and region priors to the conditioning may genuinely help. It does not change
the effective sample size, does not create a holdout, and does not supply an absolute baseline.
Do A0, A1 and A3 first, or step 11 produces a better number that means exactly as little.

**(12) Predict orthogonality, unlock design — NOT REACHABLE on any computational path, and you
should treat that as settled now rather than at the end.** Across 185 experimental register rows,
`swap_or_crossreactivity` and `orthogonality_exchange` are `NOT_IN_LOCAL_ASSETS` in **every row**, as
is `ncrna_mutagenesis`. There is no dataset anywhere in the project's reach that labels an RT–ncRNA
combination compatible or incompatible. Two routes exist and only two:

- **Acquire exchangeability labels.** Even a small designed swap panel, tens of combinations across
  a few types, converts step 12 from impossible to hard. This is a laboratory precondition, not a
  refinement, and it should be planned now because it has the longest lead time of anything here.
- **Change the endpoint.** RT-DNA production and editing **are** measured: 67 elements produce
  RT-DNA, 100 give human editing above zero, and 16 elements are fully external by sequence.
  Predicting a *functional* endpoint on non-exposed elements is preregisterable today and is a real
  step toward design. It is not orthogonality and must never be reported as such.

**The consequence for the whole programme.** Step 12 is the stated destination, and it is blocked by
a missing measurement rather than by missing analysis. **Every upstream step must therefore justify
itself by its own payoff.** Steps 1, 2, 4, 5, 6 and 9 do. Steps 7 and 11 currently do not.

## 12.3 · The finding hiding in your step (2) — and it reverses the project's assumption

Your parenthetical says the RT core domains are not all detectable in retrons. The project measured
a gradient consistent with that and filed it as a limitation: median mapped fraction 0.94 for group
II introns against **0.4933** for retrons, with a retron median `DELETED_STATE` fraction of 0.20
against 0.0467 for group II introns. The package repeats this as "the group-II-centred frame
confounds every between-family comparison".

**But a reciprocal, symmetric, seven-family analysis already exists and says something different.**
`results/rt07_g4a_repaired/tables/g4a_repaired_supported_intersection.tsv` compares each family's
profile against the other six:

| family | consensus length | positions aligned to any partner | shared with **all** partners | all-partner share of covered | family-private positions |
|---|---|---|---|---|---|
| **Retrons** | 475 | 260 (54.7%) | **102** | **39.2%** | **3** |
| GII | 539 | 370 (68.6%) | 148 | 40.0% | 16 |
| DGRs | 406 | 331 (81.5%) | 111 | 33.5% | 14 |
| CRISPR | 796 | 286 (35.9%) | 137 | 47.9% | 2 |
| UG3 | 421 | 342 (81.2%) | 115 | 33.6% | 53 |
| UG5 | 1014 | 345 (34.0%) | 76 | 22.0% | 87 |
| AbiA | 708 | 249 (35.2%) | 75 | 30.1% | 32 |

Three readings follow, and none is in any project document:

1. **In the symmetric frame, retrons are not core-deficient.** Their all-partner share of covered
   positions is **39.2%**, statistically indistinguishable from group II introns' 40.0% and higher
   than four of the other five families. The one-directional 0.49-against-0.94 gradient is therefore
   **most probably a property of the group-II-seeded profile, not of retron domain content.** That
   strengthens the package's confound warning and simultaneously removes the biological reading your
   parenthetical proposed.
2. **What retrons do have is a smaller pan-family-alignable region**: 54.7% of their consensus aligns
   to any partner, against 68.6% for group II introns and 81% for DGRs and UG3. So the difference is
   not a thinner shared core but **more sequence outside the shared core**. That is a different and
   more interesting claim, and it is testable.
3. **Retrons are the least idiosyncratic family in the alignable region**: only **3** family-private
   positions out of 260, against 16 for group II introns, 53 for UG3 and 87 for UG5. This has a
   direct and unwelcome consequence for your step (4), in §12.4.

**Caveat, stated plainly.** This table was built to select anchor states, not to answer a biological
question, and it is a single landed table with no independent replicate. It also means the frozen
anchors are **retron-informed**, which qualifies the clean "group-II-centred frame" story in the
other direction. A16 specifies what would turn it into a result.

## 12.4 · Where a retron-discriminative signal can and cannot be

Combining §12.3 with the structural arm's outcomes gives an unusually clear negative map. A
retron-discriminative signal is **not** in any of these places, and each exclusion rests on a
measurement:

| candidate location | why it is excluded | evidence |
|---|---|---|
| the conserved catalytic core | 3 family-private positions in 260 covered; catalytic confirmation 0.9653 is family-agnostic | intersection table; g5 |
| a three-way domain partition | not recovered, and the literature does not agree with itself either | Stage 3A, Stage 3C |
| Region X | defined in 3 of 21 retron chains; zero motif hits in any declared interval | Stage 3C, corrected |
| Region Y | absent in all 6 Retron-Eco8 chains; present in 4 non-retron chains | Stage 3C |
| genomic neighbourhood, as a discriminator | retrons 27th of 41 families, inside a predeclared dead band | prior project |
| the numbered RT0–RT7 regions | one of 32 region names has a stated residue boundary; RT5 and RT6 are not separable | g7a |

**What is left, and it is where your step (4) should now point:** the **45.3% of the retron
consensus that aligns to no partner family**, the terminal extensions, and the ncRNA itself. The
first has never been characterised. The second is interpretable in only 20 of 62 chains. The third is
A5. That is a genuinely informative process of elimination and it is worth a thesis section in its
own right, independent of whether the discriminator then succeeds.

## 12.5 · Two standing design rules

**Rule 1 · Non-retron RTs are the contrast class in every discriminative analysis, and they are not
an external control.** Your closing remark is correct as design and needs one qualification. There
are **423,274** non-retron exact RTs across roughly 40 families, they are large and structured, and
they have been used mostly as reporting strata rather than as controls. Use them. But they carry
MyRT family labels from the same tool lineage that defines the retron class, so retron-against-other
is a comparison **between two products of one labeller**. It is the right design and it is not
independent evidence. The only genuinely external anchors the project holds are the 8 deposited
retron complexes, the 67 elements with measured RT-DNA production, and the 16 fully-external panel
elements. Every discriminative claim should be checked against at least one of those three.

**Rule 2 · Each node must have its own payoff.** Because step 12 is blocked on a measurement, no
analysis may be justified by its contribution to the destination. State each node's standalone
claim, its falsification criterion and its chapter before it runs.

## 12.6 · Six analyses added to §7

### A16 · Reciprocal family-frame analysis of RT core content — **USEFUL, mostly landed**

- **Question.** Is the low retron mapping fraction a property of retron domain content, or of the
  group-II-seeded profile?
- **Hypothesis.** Predominantly the profile. The symmetric table already points that way (39.2%
  against 40.0%), and the real difference is a larger non-alignable remainder, not a thinner core.
- **Why existing evidence does not answer it.** The one-directional gradient is confounded by
  construction. The symmetric table exists but was built to pick anchors, has no replicate, no
  interval, and no per-sequence version.
- **Population.** The seven profile families already in the table, extended to the full family set in
  `RTs-collection.faa`.
- **Inferential unit.** Profile position for the intersection; exact RT for any per-sequence extension.
- **Controls.** *Positive:* two families known to share the core, which must show high reciprocal
  mapping. *Negative:* a non-RT profile of similar length, which must show low mapping in both
  directions. *Reference:* the existing one-directional g5 gradient, reported beside the symmetric
  result so the difference is visible.
- **Confounders.** Consensus length varies 406 to 1014 and drives coverage; derivation-set size
  varies by family; profile construction convention is fixed at one setting.
- **Anti-circularity.** Build each family's profile by the same procedure from the same source, and
  never compare a family against a profile its own sequences seeded.
- **Falsification criterion.** Declared in advance: if retron-versus-partner mapping is asymmetric in
  the same direction and magnitude as the g5 gradient after length correction, the domain-content
  reading survives; if it is symmetric, the gradient is a frame artefact and must be reported only as
  such.
- **Expected patterns.** (i) Symmetric → the package's confound warning is confirmed and strengthened,
  and the "retrons lack core domains" reading is withdrawn. (ii) Asymmetric → a real claim about
  retron domain content, which would be a significant result.
- **Claim unlocked.** Either a biological statement about retron core content or a clean methodological
  statement about profile-frame artefacts. Both are publishable; the second belongs in Option A.
- **Burden.** Low. The machinery, the source file and one table already exist.
- **Dependencies.** None.
- **Verdict.** **USEFUL**, and unusually cheap for what it settles.

### A17 · Core-selection sensitivity of RT phylogeny — **USEFUL; supersedes A12's framing**

- **Question.** How much of a published RT phylogeny's topology is determined by the undocumented
  choice of which residues constitute the core?
- **Hypothesis.** Substantially. The project has already measured frame-dependence at block level:
  RT4's block splits into three in the independent frame at Jaccard 0.410.
- **Why existing evidence does not answer it.** No phylogeny exists here. The Mestre re-inference
  failure is uninformative about this because her core selection is unpublished, which is precisely
  the variable under test.
- **Population.** A declared, redundancy-corrected sample of exact RTs spanning the family range, with
  retrons and non-retron families both represented.
- **Inferential unit.** Tree topology; the comparison unit is a pair of trees.
- **Required inputs.** The frozen mapper's per-residue state assignments on 369,381 proteins, which
  is the asset that makes this feasible and which no other group holds.
- **Design.** Build trees under at least four core definitions: full-length, the frozen-state core,
  the independent-frame core, and a structural core. Compare with Robinson-Foulds and quartet
  distance, and report clade recovery for the historical clades under each.
- **Controls.** *Positive:* two core definitions that differ trivially must give near-identical trees.
  *Negative:* a random residue subset of matched size must give a clearly worse tree. *Reference:*
  the published topology as a comparator, never as truth.
- **Confounders.** Alignment method, trimming, model selection and taxon sampling all move topology;
  hold every one fixed across arms so that core definition is the only variable. Dereplication
  enriches truncated tips, which the project has already paid for once.
- **Anti-circularity.** Do not score against Mestre's clades as truth; score topology *differences*
  between arms. Clade recovery is reported as a descriptive secondary.
- **Falsification criterion.** Declared in advance: if all four core definitions give trees within the
  distance obtained between two bootstrap replicates of one definition, core selection does not
  matter and the claim is withdrawn.
- **Expected patterns.** (i) Large between-arm distances → a real methods result affecting every
  published RT phylogeny, and the strongest classification-adjacent claim available. (ii) Small
  distances → a clean negative that closes the question and retires the concern.
- **Claim unlocked.** A methods claim about the field's phylogenies that does not require this
  project's tree to be correct, only to be comparably built.
- **Decision affected.** Whether a classification chapter exists, and on what basis.
- **Burden.** Medium. Dominated by tree inference on a bounded sample.
- **Dependencies.** A9 for the sample design.
- **Verdict.** **USEFUL.** This replaces A12's framing, and is a better reason to build a tree than
  classification was.

### A18 · Combinatorial retron discrimination with a functional anchor — **USEFUL, after A16**

- **Question.** Does a **combination** of sequence features separate retron RTs from other RT
  families, when no single feature does?
- **Hypothesis.** If such a signal exists it is in the non-alignable remainder of the retron
  consensus, the terminal extensions, or the ncRNA, because §12.4 excludes everything else.
- **Why existing evidence does not answer it.** Every prior attempt was single-feature and each
  failed against a predeclared criterion. No combinatorial model was built.
- **Population.** 78,287 retron-family exact RTs against 423,274 non-retron exact RTs, family-stratified.
- **Inferential unit.** Exact RT for fitting; **RT family** for evaluation.
- **Controls.** *Positive:* an RT-versus-non-RT discrimination task, which must be easy or the feature
  set is inadequate. *Negative:* a label-shuffled arm within family. *Reference:* each single feature
  alone, so that any combinatorial gain is measured against them.
- **The decisive anti-circularity test.** The labels come from the same tool lineage as the class
  definition, so within-label accuracy proves nothing. Evaluate two ways instead: **hold out whole
  families**, not sequences, so the model cannot memorise a family signature; and **rank the 67
  elements with measured RT-DNA production plus the 8 deposited complexes**. A discriminator that
  separates labels but does not rank the functionally validated retrons highly has re-learned the
  labeller and must be reported as such.
- **Confounders.** Length, composition, family sample-size imbalance, and the fact that eligibility is
  non-uniform across families (11.3% to 73.6%).
- **Falsification criterion.** Declared in advance: if held-out-family performance does not exceed the
  best single feature by a stated margin, the combinatorial hypothesis is refuted and no retron HMM
  is built.
- **Expected patterns.** (i) Combination beats singles on held-out families and ranks the msDNA
  producers → the first genuinely discriminative retron signature, and a real contribution.
  (ii) Beats singles within families but not across → re-learning the labeller; report as a negative
  about annotation-defined classes, which is still Option A material.
- **Claim unlocked.** An operational, evidence-based answer to "what is a retron" at sequence level.
- **Burden.** Low to medium.
- **Dependencies.** A16 tells it where to look; A5 supplies the ncRNA features.
- **Verdict.** **USEFUL.** This is your step (4) made falsifiable.

### A19 · Covariance models for the six unmodelled subtypes, with a leave-one-subtype-out positive control — **ESSENTIAL**

- **Question.** Is the ~40% zero class a model-coverage gap, and can the gap be closed?
- **Hypothesis.** Partly. Subtypes VI, VII, VIII, X, XI and XII have no dedicated model, and their
  carriage is at or near zero.
- **Why existing evidence does not answer it.** The model-coverage explanation is asserted only in the
  synthesis layer and is performed by **no landed table**. And §3 item 8 shows context truncation does
  not explain the residual.
- **Population.** Retron-labelled loci of the six unmodelled subtypes with ≥ 1 kb unclipped upstream
  context.
- **Inferential unit.** Physical locus.
- **The control that makes this worth doing, and that the whole zero-class argument currently
  lacks.** **Leave-one-subtype-out**: take a subtype that *does* have a model, remove that model,
  rebuild it by the same procedure from the loci alone, and measure recovery against the withheld
  model's own calls. Repeat across all modelled subtypes. This is the positive control the project
  never ran, it is the direct answer to "can this procedure find an ncRNA family when one is present",
  and it is the reason this is not a repeat of the closed discovery arm.
- **Confounders.** Same-paradigm rediscovery, since the existing models were built by the same tool;
  report it and do not claim independence. Upstream context length, stratified. The winning positional
  prior, which must be included as a baseline arm.
- **Anti-circularity.** Never score a new model against the covariance-model calls it was meant to
  extend. Score against the leave-one-out withheld model, and against published extents where they
  exist.
- **Falsification criterion.** Declared in advance: if leave-one-subtype-out recovery falls below a
  stated threshold, the procedure cannot find families that are present, the zero class cannot be
  attributed to model coverage, and the claim is permanently withdrawn.
- **Expected patterns.** (i) Recovery good, new models find elements in the zero class → the zero class
  shrinks, the carriage claim is quantified rather than asserted, and the pair set may grow.
  (ii) Recovery good, new models find nothing → **the strongest available evidence that a large part
  of the zero class is biological**, which would be a major result and is currently unclaimable in
  either direction. (iii) Recovery poor → the instrument cannot answer it, and the zero class stays
  formally unexplained.
- **Claim unlocked.** The zero-class question, which is currently the weakest link in Option A.
- **Decision affected.** Whether Option A can make a claim about 40% of its own population.
- **Burden.** Low to medium.
- **Dependencies.** A6 for the fixed locus set.
- **Verdict.** **ESSENTIAL.** Note both outcomes are publishable, which is rare here.

### A20 · Architecture-defined pair expansion — **USEFUL, and the route out of circularity**

- **Question.** Can RT–ncRNA pairs be defined by ncRNA architecture and canonical geometry rather
  than by a covariance-model hit, and does that change the population?
- **Hypothesis.** Yes, at least partly, since the a1/a2 inverted repeat is a local structural signal
  independent of the models.
- **Why it matters more than its size suggests.** Every pairing result rests on PAIR-ELIG, which is
  defined by covariance-model calls. That is the single dependency behind P1, and an
  architecture-defined population is the only route out of it that does not require new laboratory
  data.
- **Population.** Retron-labelled loci with sufficient upstream context, including the zero class.
- **Inferential unit.** Physical locus for calls; exact pair for the expanded set.
- **Controls.** *Positive:* current PAIR-ELIG pairs, which architecture-based calling must largely
  recover. *Negative:* non-retron RT loci and shuffled upstream windows. *Reference:* the canonical
  geometry envelope, upstream, same strand, no intervening CDS, within about 1.1 kb.
- **Confounders.** Calling architecture in a window that a model already cut is not independent;
  restrict the headline to loci **with no model hit**. Contig clipping. GC.
- **Anti-circularity.** The expansion's value is precisely that its calls do not come from the model
  lineage, so any locus whose ncRNA extent was model-derived must be excluded from the expansion set
  and reported separately.
- **Falsification criterion.** Declared in advance: if architecture-based calling does not recover the
  existing pairs at a stated rate, it is not a valid caller and no expansion follows.
- **Expected patterns.** (i) Recovers existing pairs and adds new ones in the zero class → a partially
  de-circularised population, a larger effective sample, and a direct answer to the zero-class
  question. (ii) Recovers existing but adds nothing → strong evidence that the zero class genuinely
  lacks msr-msd architecture. (iii) Does not recover existing → the caller is invalid, reported as a
  negative for A5.
- **Claim unlocked.** An RT–ncRNA population not defined by the annotation lineage. This is the single
  most valuable structural change available to the project.
- **Decision affected.** Whether any pairing follow-up can escape P1.
- **Burden.** Low once A5 exists.
- **Dependencies.** A5, and A19 for the zero-class stratum.
- **Verdict.** **USEFUL, bordering essential.** Promote it if A5 succeeds.

### A21 · Predicted-structure expansion across the sequence diversity — **OPTIONAL, medium cost**

- **Question.** Do the structural conclusions hold on a population selected for diversity rather than
  for local availability?
- **Why.** The current panel is 62 locally cached chains, no systematic search, 50 of 62 cryo-EM, all
  31 groups in one structural cluster, and leave-one-group-out is therefore influence analysis rather
  than independence.
- **Design.** Predict structures for a declared diversity-stratified sample spanning retron subtypes
  and comparator families; carry per-residue confidence as a primary covariate; never pool predicted
  with experimental chains without stratifying, and repeat the Stage-3A decomposition and the
  Region-Y question on the expanded set.
- **Controls.** *Positive:* predicted structures of chains that also have experimental coordinates,
  which must reproduce their partitions. *Negative:* low-confidence predictions, which must be shown
  to behave differently. *Reference:* the existing 62-chain result.
- **Falsification criterion.** If the decomposition behaves the same on predicted and experimental
  chains at matched confidence, the Stage-3A result generalises; if not, it was panel-specific.
- **Verdict.** **OPTIONAL.** Do it only after A7 decides whether the structural negative is real. If
  A7 shows the instrument fails its positive control, expanding the population does not help.

## 12.7 · Revised ordering

The programme, rewritten as a graph with the new nodes and with each node carrying its own payoff:

```
NOW, zero compute:      A0  A2  A3  A4  R8
                          |
cheap, in parallel:     A1 ....... decides the pairing paper
                        A5 ....... the RNA object            -> A20 -> A11
                        A6 ....... the carriage headline     -> A19
                        A16 ...... the frame question        -> A18
                        A7 ....... the structural verdict    -> A21 (optional)
                        A10 ...... genomic architecture      -> A14
                        A8 ....... data release
                          |
medium:                 A9 -> A17 (core-selection phylogeny)
                        A15 (saturation)
                          |
blocked on measurement: orthogonality and design (step 12)
                        -> plan the swap panel NOW; it has the longest lead time
                        -> meanwhile, functional-endpoint prediction on the 16 external elements
```

**What changes in §10's minimum.** Add **A19** to Tier 1, because the zero class is 40% of Option A's
own population and is currently unexplained in either direction. Add **A16** to Tier 1, because it is
cheap and settles whether a headline confound is a confound or a finding. Move **A17** into Tier 2 as
the replacement for A12. Everything else stands.

**What changes in §11's decisions.** D3 gains a third item: A16 and A19 are both cheap, both settle
questions the project currently states in the wrong direction, and A19 is publishable whichever way
it lands. And a sixth decision now exists, which is really the first: **step 12 is blocked on a
measurement no analysis can substitute for, so decide now whether a laboratory swap panel is
obtainable within the thesis timeline.** If it is, plan it immediately, because it has the longest
lead time of anything in this document. If it is not, remove orthogonality and design from the
programme's stated destination and let the upstream chapters stand on their own payoffs.

---

# 13 · RESPONSE TO THE EXTERNAL ADDENDUM

*Added 2026-09-20 after an addendum prepared by a second reviewer was supplied. Per its §6.5 I state
agreement and disagreement explicitly rather than merging silently. Section numbers below refer to
the addendum.*

**Summary.** The addendum is a good document. It corrects this review on two points, adds one item I
missed that is genuinely valuable, and improves the framing of three others. I disagree with it on
one structural matter, the centrality of the phylogeny, and I think it carries one systemic risk
that neither document has named. Both reviews are silent on the constraint most likely to decide the
programme, which §13.5 supplies.

## 13.1 · Where the addendum corrects this review — ACCEPTED

**(a) §1.1 · Two kinds of independence must be kept apart. Accepted in full; this review was wrong.**
I treated the panel primarily through sequence exposure and therefore under-used it. The addendum's
distinction is correct and load-bearing:

- **Functional-label independence:** was RT-DNA production actually measured, or inferred?
- **Sequence/model independence:** was the exact or homologous sequence seen during development?

Exposure invalidates an element as an ML test set. It does **not** invalidate it as biology. The
159 exposed elements remain valid **functional positive anchors** for retron identity, ncRNA
architecture and structural work, because in every case the functional outcome was measured in a
laboratory and was never a training target anywhere in this project.

§13.4 turns this principle into a number, and the number is better than either document assumed.

**(b) §4.6.1 · "If new covariance models find nothing, the zero class is biological" is too strong.
Accepted; the sentence is withdrawn.** My A19 expected-pattern (ii) overstated. Failure to detect
with a validated procedure strengthens an absence hypothesis; it does not establish biological
absence, and this project holds the canonical counter-example, where a search against a database
with no gathering thresholds returned zero unconditionally. **Replacement wording for A19 (ii):**
*"new models recover withheld families but find nothing in the zero class → the strongest available
bound on how much of the zero class is attributable to model coverage, and a licence to state the
residual as unexplained rather than as detector scope. It is not evidence of biological absence."*

## 13.2 · Where the addendum adds something this review missed — ACCEPTED

**(a) §4.5 · Curate published cross-pair experiments before declaring orthogonality unreachable.
Accepted, and this is the addendum's most valuable single contribution.** This review checked
**local assets** and found swap, cross-reactivity, orthogonality and ncRNA mutagenesis absent from
all 185 register rows. It did not check the **literature**, and the project holds variant-library and
engineering papers as PDFs. Retron engineering work does perform swaps. So the correct status is not
"no data exists" but "no data has been extracted". **Specified as A23.**

One addition the addendum does not make, and it decides whether a curated row is usable: a failed
**cognate** pair is a broken element, not an orthogonality datum. Only a tested **non-cognate**
combination is. The curation schema must carry that distinction in its primary key, or the matrix
will silently mix the two.

**(b) §4.3 · De novo ncRNA discovery should be redesigned, not reduced to the six unmodelled
subtypes. Accepted as a broadening.** My A19 was too narrow. Grouping loci by an independently
inferred relatedness structure rather than by inherited subtype is a material design change and is
not closed by the previous failure.

I attach one condition, because the previous branch did not fail on grouping. **It failed because a
fixed positional interval beat it 901 to 343, and per-type intervals reached 969.** Regrouping does
not address that. The falsification criterion must therefore stay the positional baseline, and the
highest-value target is precisely the **zero class**, because that is the only stratum where a
positional prior has no covariance-model call to be fitted on. A redesigned discovery arm that does
not beat the positional baseline outside the zero class has repeated the closed experiment.

**(c) §1.2 and §4.4 · Predicted structures as an independent support layer rather than a Stage-3A
rescue. Accepted as a reframe.** Testing whether homologous regions stay structurally conserved
despite sequence divergence is a better question than re-running a decomposition, and it is the right
use of a diversity-spanning predicted set.

One technical caveat neither document states, and it bites exactly where the addendum wants to use
these structures. Structure predictors are trained on the PDB, and the retron structures in the PDB
are the same small clustered set this project already holds, with all 31 biological groups in one
structural cluster. **Predicted retron structures therefore inherit that training distribution, and
they may be confidently wrong in precisely the divergent regions of interest** — the non-alignable
remainder of the consensus, the terminal extensions, and Region X/Y territory. Per-residue confidence
stratification is necessary but not sufficient. The prediction set must be benchmarked for accuracy
in **low-homology regions specifically**, not only globally, before any conclusion rests on it.

**(d) §3, A1 · `ln 4` is diagnostic, not a sufficient baseline. Accepted.** The addendum is right
that the emitted vocabulary and the termination process differ from a four-letter alphabet, so the
comparison is an anchor rather than a control. My A1 already specifies B0 through B3; the addendum's
wording is the more careful one and is adopted.

## 13.3 · Where I disagree with the addendum

**(a) §4.1 and §5 · The phylogeny should not be the trunk of the programme. This is my main
disagreement.**

We agree it should be upgraded, and §12 already did so for the addendum's own reason, core-selection
sensitivity. I disagree with making it the backbone that feature discovery, structure integration,
neighbourhood evolution and ncRNA discovery all hang from. Three grounds:

1. **It rebuilds the serial-pipeline failure mode both the operator and this review identified.** The
   addendum itself concedes that only shallow lineages may prove robust. If that happens, five
   downstream nodes are compromised at once.
2. **Most of the eight uses the addendum lists do not need a tree.** They need a *relatedness
   structure*: nested clusters at declared identity thresholds. Blocking for permutation, grouping
   for ncRNA discovery, diversity stratification for structure selection and phylogeny-aware feature
   discovery are all served by that. Only two of the eight genuinely require ancestry: ancestry-aware
   RT–ncRNA correspondence, and whether historical types correspond to RT lineages.
3. **The project's track record on tree-adjacent tasks is poor**: a failed re-inference, a failed
   placement gate, and five prior failed tree routes.

**My counter-proposal.** Build the relatedness backbone (A9) first. It is cheap, robust, and unblocks
six of the eight uses immediately. Treat the tree as **A17**, a specific preregistered
core-sensitivity study serving the two uses that need ancestry. That keeps the addendum's scientific
point and removes the single-point-of-failure architecture.

**(b) §5 · Placing ncRNA architecture downstream of the phylogeny is wrong and costly.** The
addendum's graph puts "HIGH-CONFIDENCE ncRNA ARCHITECTURE / PAIRS" below the phylogeny node. The
msr/msd architecture work needs sequences, deposited structures and published extents. It needs no
tree. Sequencing it behind the riskiest node in the programme delays the single most valuable
unstarted item for no methodological gain. **A5 runs immediately and in parallel.**

**(c) The systemic risk neither document names: collectively, the addendum reopens almost
everything.** Co-evolution becomes conditional. De novo discovery is redesigned. The structural arm
is repurposed. Orthogonality acquires a route. Each reopening is individually defensible and I have
accepted three of the four. But a review whose net effect is to restore the original twelve-step
programme, each node conditional on future work, is a wish list rather than a plan.

The discipline that prevents this is already in the project's governance and should be applied here:
**every reopened node carries a preregistered gate and a named death condition before it runs.** A
node that cannot state what result would make it stop should not be reopened. I have written a death
condition into each of A17, A19, A22 and A23, and the same must be done for the redesigned discovery
arm before it is authorised.

**(d) §4.6.2 · On not collapsing the structural conclusions.** I agree with the principle and this
review already applied it: the literature-boundary disagreement is presented as Option E precisely
because it is parser-independent and survives when Stage 3A does not. I do not retreat on the
substance of P3. The palm meets two of its three bars, 17 of 19 no-call chains contain a unit with
four or more same-sheet strands rejected on a composition threshold, the parser disagrees with itself
on 62% of replicate pairs, and the one textbook chain returns AMBIGUOUS. That is an
instrument-limited result under the project's own standing rule, and A7 is the test that settles it.

## 13.4 · The functional contrast both documents missed

Applying the addendum's own §1.1 principle to the register yields a result neither document states.
**103 elements have RT-DNA production actually measured: 67 above zero and 36 at zero.** Sixty-two of
the 67 also have an empirically determined RT-DNA sequence.

Exposure is distributed across **both** classes:

| exposure class | producers (n=67) | measured zero (n=36) |
|---|---|---|
| catalogue only | 25 | 16 |
| train exposed | 21 | 7 |
| val/test exposed | 13 | 5 |
| sequence near corpus | 5 | 3 |
| fully external | 3 | 5 |

**Why this matters more than its size.** The functional outcome was **never a training target
anywhere in this project**; the models were trained on pairing. So sequence exposure here is a
homology concern, not a label-leak concern, and the 67-versus-36 contrast is usable as an endpoint on
exposed elements, which the 16-element external set alone could never support. This is the **only
measured functional retron / non-functional retron contrast that exists anywhere in the project**,
and both reviews treated the panel as a single undifferentiated positive layer.

It also supplies the missing external check for retron discrimination. A discriminative signature
(A18) can be trained on annotation labels but must be **evaluated** on whether it ranks the 67
producers above the 36 non-producers. That evaluation does not use the annotation lineage at all.
**Specified as A22.**

## 13.5 · The constraint neither document has named: a power inventory

Both reviews argue about which analyses to run. Neither states, per claim, how many independent
units exist to run them on. That is the binding constraint on steps 7, 10, 11 and 12, and it should
be settled before any of them is designed.

| claim | inferential unit | independent units available | verdict |
|---|---|---|---|
| lineage predicts the cognate ncRNA | independent lineage | roughly 9 to 14 effective | adequate for a large effect only |
| exact RT beyond lineage | independent lineage | same, and supported in 3 of 11 powered types | **underpowered as stated** |
| retron discriminative signature | RT family for held-out-family evaluation | **1 positive family** | held-out-family design is impossible; use held-out subtype (21) plus A22 |
| ancestry-aware co-evolution | independent co-divergence event | bounded above by the lineage count | **not adequate today** |
| ncRNA architecture validation | deposited RT–RNA–DNA complex | 8 | adequate as calibration, not as inference |
| functional retron identity | element with measured production | **67 positive / 36 negative** | adequate for a bounded, preregistered test |
| orthogonality | measured non-cognate combination | 0 local; unknown in literature | **A23 determines this** |

Two consequences follow immediately. **First**, the addendum's §4.2 hope that a phylogeny and new
pairs will change the number of independent units is only half right: adding pairs **within existing
lineages does not increase independent units**, so A20's expansion helps co-evolution only insofar as
it reaches lineages not currently represented. That specific quantity, new lineages gained, must be
measured before co-evolution is reconsidered, and it should be the preregistered gate.

**Second**, A18 as this review specified it has a design flaw the addendum did not catch and nor did
I: **you cannot hold out the retron family to test retron discrimination, because there is only one
retron family.** The evaluation must be held-out subtype, with A22 as the external arm.

## 13.6 · Revised status of the disputed recommendations

| item | this review said | addendum said | **resolved status** |
|---|---|---|---|
| modern RT phylogeny | optional, then useful as core-sensitivity | central backbone | **useful and preregistered (A17); the backbone is A9, not the tree** |
| co-evolution | probably abandon | defer / conditional | **DEFER, conditional on a preregistered lineage-count floor measured by A20** |
| de novo ncRNA discovery | closed; narrow to six unmodelled subtypes | redesign broadly | **redesign, with the positional baseline as the falsification criterion and the zero class as the primary target** |
| predicted structures | optional, after A7 | independent support layer | **independent support layer, conditional on low-homology-region benchmarking** |
| the 175-element panel | assay layer, mostly exposed | functional positive anchors | **functional anchors, and a measured 67 vs 36 contrast (A22)** |
| orthogonality | blocked; plan a swap panel | curate the literature first | **curate first (A23), then decide on a panel** |
| structural negative | threshold artefact, inadmissible as biology | resolve separately, do not collapse | **unchanged; A7 settles it, and Option E stands independently** |

## 13.7 · Three new analyses

### A22 · Functional retron identity: the 67-versus-36 contrast — **USEFUL, bounded**

- **Question.** Do sequence or architectural features separate retron elements that measurably
  produce RT-DNA from those that measurably do not?
- **Hypothesis.** Partly. Catalytic integrity and ncRNA architecture should carry signal; annotation
  label should not, since both classes carry it.
- **Why existing evidence does not answer it.** Never attempted. The census paper's finding that
  RT-DNAs are not predictable from sequence concerns predicting the **sequence** of the product, not
  whether an element produces at all.
- **Population.** The 103 elements with measured production: 67 positive, 36 negative.
- **Inferential unit.** Assayed retron element.
- **Controls.** *Positive:* catalytic-motif integrity, which must separate the classes if anything
  does. *Negative:* the annotation label and the retron subtype, which are present in both classes
  and must **not** separate them; if they do, the split is confounded by panel construction.
  *Reference:* a features-shuffled arm.
- **Confounders.** Panel construction is not a random sample of retrons; exposure differs modestly
  between classes; n = 103 permits only a small number of features. Declare the feature set and the
  model class before fitting.
- **Anti-circularity.** The functional label was never a training target in this project, so exposure
  is a homology concern only. Report performance stratified by exposure class, and report the fully
  external subset (3 producers, 5 zeros) separately as a descriptive check, never as a test.
- **Falsification criterion.** Declared in advance with a stated minimum detectable effect at n = 103.
  If no feature set separates the classes above that floor, report it as a bounded negative and do
  not build a production predictor.
- **Death condition.** If the annotation label alone separates the classes, the contrast is a panel
  artefact and the analysis stops.
- **Claim unlocked.** The only measured functional statement about retron identity the project can
  make, and the external evaluation arm for A18.
- **Burden.** Low.
- **Dependencies.** A5 supplies the ncRNA features.
- **Verdict.** **USEFUL.**

### A23 · Literature curation of cross-pair and non-cognate experiments — **ESSENTIAL, and first**

- **Question.** Do measured non-cognate RT–ncRNA outcomes exist in the published literature, and how
  many?
- **Why it is first.** It determines whether step 12 is blocked, partially open, or reachable, and it
  is the cheapest item in the entire programme. This review declared orthogonality blocked on the
  basis of **local assets** only, which was an incomplete check.
- **Population.** Retron engineering, variant-library and swap literature, including the PDFs already
  on disk and their supplementary data.
- **Product.** An RT × ncRNA × assay matrix with, for every row: cognate or non-cognate; the assay
  and its endpoint; the measured outcome; the source; and whether supplementary data were recovered
  or the value was read from a figure.
- **The distinction that makes rows usable.** A failed **cognate** pair is a broken element. Only a
  tested **non-cognate** combination is an orthogonality datum. Carry this in the primary key.
- **Anti-circularity.** Unobserved combinations are never negatives. An absent row is absent, not
  incompatible.
- **Falsification criterion.** Declare a floor in advance, for example a minimum number of distinct
  non-cognate combinations with a comparable endpoint, below which a computational orthogonality
  model is not attempted and a designed swap panel becomes the prerequisite.
- **Claim unlocked.** A defensible statement about whether step 12 is reachable, replacing an
  assumption in both reviews.
- **Burden.** Days of reading. No compute.
- **Dependencies.** None. **Do this before anything else in the pairing arm.**
- **Verdict.** **ESSENTIAL.**

### A24 · Redesigned de novo ncRNA discovery — **CONDITIONAL, with a hard gate**

- **Question.** Can ncRNA families be recovered de novo when loci are grouped by an independently
  inferred relatedness structure rather than by inherited subtype?
- **Why it is not the closed experiment.** The grouping variable changes, the evaluation anchors
  change from covariance-model cuts to published and experimental extents, and the primary target
  becomes the zero class.
- **Population.** Retron-labelled loci with sufficient upstream context, primary stratum being those
  with **no** covariance-model call.
- **Controls.** *Positive:* leave-one-subtype-out recovery of a withheld model, carried over from
  A19. *Negative:* matched non-retron and distal windows. *Reference:* the fixed positional interval
  and the per-type intervals, as explicit competing arms.
- **Falsification criterion and death condition, both declared before scanning.** The arm dies if it
  does not beat the positional baseline outside the zero class, or if leave-one-subtype-out recovery
  falls below its stated floor. Freeze model-building and acceptance criteria before any held-out
  locus is scanned.
- **Dependencies.** A9 for grouping, A19 for the control, A6 for the locus set.
- **Verdict.** **CONDITIONAL.** Authorise only with the gate written down.

## 13.8 · Revised minimum decisive programme

Replacing §10's Tier 0 and Tier 1 with the addendum's corrections folded in.

**Tier 0, zero compute, blocks everything:** A0 lineage-aware variance · A2 common-population ladder
· A3 declare the confirmatory population **(omitted by the addendum, and still blocking)** · A4 the
numerical and provenance corrections plus the governance decision **(also omitted, and nothing is
promotable until it is resolved)** · R8 report the real-versus-permuted contrast · **A23 literature
curation**, which is reading rather than compute and determines whether step 12 exists.

**Tier 1, cheap, each decides something:** A1 absolute baselines · A5 msr/msd architecture ·
A6 fixed-locus carriage · A16 reciprocal family frame · A10 genomic architecture · A7 the structural
verdict · A8 data release · **A22 the functional contrast**.

**Tier 2, medium:** A9 relatedness backbone → A17 core-sensitivity phylogeny · A19 withheld-model
control → A24 redesigned discovery · A20 architecture-defined pair expansion · A21 predicted
structures, after A7 and after low-homology benchmarking · A15 saturation · A14 mobility.

**Gated, not scheduled:** co-evolution, on the preregistered lineage-count floor from A20.
Orthogonality modelling, on A23's floor. A designed swap panel, if A23 shows the literature is
insufficient, planned immediately because it has the longest lead time in the programme.

**Revised dependency graph.**

```
READ AND FIX FIRST (no compute)
  A23 literature cross-pair curation ....... decides whether step 12 exists
  A0 A2 A3 A4 R8 .......................... decides what may be claimed at all
        |
        v
CHEAP AND PARALLEL (no single trunk)
  A5  msr/msd architecture ---> A20 pair expansion ---> [lineage-count gate] ---> co-evolution
  A6  fixed-locus carriage ---> A19 withheld-model control ---> A24 redesigned discovery
  A16 reciprocal frame ------> A18 combinatorial discrimination <--- A22 functional contrast
  A10 genomic architecture --> A14 mobility
  A1  absolute baselines ----> decides the pairing paper
  A7  structural verdict ----> A21 predicted structures (after low-homology benchmarking)
  A8  data release
        |
        v
BACKBONE, SERVING SIX USES         BRANCH, SERVING TWO
  A9 relatedness structure   --->  A17 core-sensitivity phylogeny
        |
        v
INTEGRATIVE MODELLING — only after A1, A3 and A20 have reported
        |
        v
ORTHOGONALITY / DESIGN — only with real non-cognate labels from A23 or a designed panel
```

The one structural difference from the addendum's graph: **A9 is the backbone and A17 is a branch**,
and **A5 does not wait for either**.

---

# 14 · CORRECTION: A LARGE UNREGISTERED ASSET BASE EXISTS

*Added 2026-09-20 after the operator supplied a path outside the nine worktrees this review searched.
A full audit is in progress; what is recorded here I verified directly.*

## 14.1 · What exists

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/` is a **prior project directory** that was not searched by
this review, is not searched by `PROJECT_REVIEW_PACKAGE/scripts/validate_package.py`, and is not
listed in either registry. Verified contents under
`ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/`:

| asset | count | note |
|---|---|---|
| ESMFold predictions of the Mestre retron RT set | **1,919 PDB** (498 MB) | with landed per-sequence `plddt_summary_task*.tsv`: `seq_id`, `length`, `mean_plddt`, `n_res_reliable`, `frac_reliable`. First row: 311 residues, mean pLDDT **96.39**, reliable fraction 0.997 |
| folds of the Khan experimental panel | **171 PDB** (`khan171/gold_t*.pdb`) | the 175-element functional panel, 171 of 175 |
| further fold sets | `pdb/` **5,109**, `ldd557/` **1,060**, `ldd_pdb/` **506** | populations not yet identified |
| structural comparison | `foldseek/`, `foldmason/`, `fs557/`, `fs_mestre/` | Foldseek and a structural MSA tool |
| tree work | `s8_tree_declared/cache/scfl_route2/` plus `struct_trees/`, `struct90_trees/`, `mestre_trees/`, `c90_trees/`, `derep_trees/`, `stage0_positioning/cache/refbuild/` | filenames indicate replicate draws across **three representations**: amino acid (`_aa_`), 3Di structural alphabet (`_3di_`) and partitioned (`_parts_`), with concordance-factor trees (`.cf.tree`) |

## 14.2 · Three consequences

**(a) The addendum's §1.2 was right and understated it.** Predicted structures exist for both the
panel and the Mestre set, and per-residue confidence is already tabulated. A21 therefore changes from
*generate a prediction set* to *audit and benchmark an existing one*, which is a different cost and a
different risk. The low-homology-region caveat in §13.2(c) still applies in full, and the landed
`frac_reliable` column is the right starting point for it.

**(b) This review's statement that no phylogeny exists must be qualified, and the package's specific
claim is now in doubt.** The package asserts, at `OPEN_QUESTIONS.md:79` and
`MINIMUM_REMAINING_WORK.md:89`, that the structural representation is *"an all-vs-all distance matrix
over 1,919 proteins that has never been built as a tree"*. The number 1,919 matches this fold set
exactly, so the package's authors knew of these structures. But 3Di treefiles exist under
`s8_tree_declared`. Either the claim is wrong, or those trees are on a different and smaller
population. **The audit will settle which.** Until it does, A17 must be written as *audit, re-derive
and extend existing tree work*, not as *build the first tree*, and its cost and novelty both change.

**(c) The registration gap is itself a finding, and it is the failure mode the project's own
governance warns against.** `CLAUDE.md` states: *"Special tools/resources live outside the primary
environment and are registered in `data/README.md`; do not conclude a dependency is absent until the
registered environments and Ibex resources have been checked."* These assets are **in neither
registry**: `data/README.md` and `docs/DATASET_REGISTRY.md` contain no reference to
`RETRON-DB_V4`. The only mentions anywhere in the repository are in `general/LINEAGE.md` and
`general/RETRON_STAGES/` planning prose, which the research contract explicitly excludes as an
authority: *"these are prose. Nothing cites a number from here."*

So an unregistered directory holds roughly 7,700 predicted structures, a Foldseek and structural-MSA
layer, and multiple tree sets, while the project's canonical dataset registry states that every
registered file is LOCAL ONLY and no phylogeny exists. **Whatever the audit concludes about the
trees, the asset-registration process has a gap large enough to have hidden the single most expensive
computational artefact the wider project owns.**

## 14.3 · Standing constraint, unchanged

Prior-project material is `[UNVERIFIED]` under this project's governance, and the contract is
explicit that no prior numeric measurement is frozen unless a later decision promotes it and names
the producing bundle. **The structures are reusable assets; any V4 conclusion is not.** Reuse
requires identity pinning by hash, a recorded provenance chain, and re-derivation of any number
before it is cited. That constraint is what makes this a cost saving rather than a shortcut.

**Action added to A4:** register `RETRON-DB_V4` in `data/README.md` with paths, counts and hashes,
and record whether an equivalent sweep of other sibling project directories is owed. This review
searched nine worktrees because the package presented them as the project; that framing was
incomplete.

---

# 15 · THE ASSET SWEEP REVERSES TWO OF THIS REVIEW'S CONCLUSIONS

*Added 2026-09-20. A sweep of every retron-related directory on the machine, not only the nine v7
worktrees, changes three things materially. Two of them are reversals of positions taken above and
are marked as such. The tree audit is still running; §14 stands pending it.*

## 15.1 · REVERSAL 1 — Published cross-pair orthogonality data exists. Step 12 is blocked on extraction, not on existence.

§3 item 15, §4 G15 and §12.2 all state that no exchangeability data exists and that orthogonality is
therefore unreachable computationally. That conclusion was drawn from the project's own register,
where `swap_or_crossreactivity` and `orthogonality_exchange` read `NOT_IN_LOCAL_ASSETS` in all 185
rows. **The register is correct about machine-readable assets and wrong as a statement about what is
known.** Text extraction across 61 retron PDFs already on disk finds published cross-pair
measurements in at least three sources:

| source | what it measured | size of the cross-pair design |
|---|---|---|
| **"Discovery and engineering of retrons for precise genome editing"** | gene-editing activity of six most-active retron RTs plus Eco1-RT against **cognate (diagonal) or non-cognate msr-msd**, as a heat map, mean of n = 3 biological replicates | **a 7 × 7 matrix: 7 cognate, 42 non-cognate combinations** |
| **Bobonis et al. 2022, Nature** | binary RcaT-RT combinations from Retron-Sen2 and Retron-Eco9: Se-Se, Ec-Se, Se-Ec, Ec-Ec | 4 combinations, 2 cognate, 2 non-cognate |
| **"Retrons and their applications in genome engineering"** (review) | reciprocal function on non-cognate msr-msd between Retron-Eco2 (Ec67) and Retron-Eco3 (Ec73), and Region-Y swaps between Ec86 and Ec73 | 2 reciprocal pairs, described as *"the only two examples where an RT can function on a non-cognate msr-msd"* |

**Consequences.**

1. **A23 is no longer exploratory; it has a named first target.** The 7 × 7 editing matrix is
   precisely an exchangeability dataset. Its values are published as a figure and are not on disk, so
   the action is to obtain the underlying numbers from the supplementary material or the authors. That
   is a request, not an experiment.
2. **The correct status of claim C-30 changes** from "cannot be tested with the assets currently
   held" to **"not tested here; a small amount of published cross-pair data exists and has not been
   extracted."** Those are very different sentences, and only the second is defensible.
3. **One published result cuts against the project's own pairing hypothesis and must be confronted,
   not cited selectively.** Bobonis reports that *"any msDNA could activate the antitoxin activity in
   cognate RT-RcaT pairs"*, with failure occurring in non-cognate **RT-RcaT** combinations. In that
   system the specificity sits in the protein-effector interface and the msDNA is permissive. Any
   pairing-specificity narrative has to account for this.
4. **Scale realism.** Roughly 50 published cross-pair measurements across a handful of systems is
   enough to *calibrate and sanity-check* a model. It is not enough to *train* one, and it does not
   make an n × n compatibility matrix legitimate. N10 stands.

## 15.2 · REVERSAL 2 — Region Y has direct experimental support as a specificity determinant. N12 is withdrawn as written.

§6 N12 rejected the Region-Y × exact-RT join on the grounds that it multiplies two undetermined
quantities, and §3 item 10 dismissed the 1.34× contact ratio as consistent with noise. **The
statistical criticism stands. The rejection does not**, because it treated Region Y as a
structurally-nominated feature when it is in fact a mechanistically-nominated one with prior
experimental support:

> *"**Swapping region Ys** between RT-Eco1 (Ec86) and RT-Eco3 (Ec73) produced **chimeric proteins**
> with 'swapped' msr recognition."*

That is a reciprocal swap experiment in which exchanging Region Y exchanges which ncRNA the enzyme
recognises. It is the strongest mechanistic statement about RT–ncRNA specificity anywhere in the
project's reach, and it is independent of the project's own structural measurement.

**Revised status of the Region-Y join: from REJECTED to CONDITIONALLY APPROVED as a preregistered,
one-shot, directional test.** The conditions are strict and they are what separate this from the
fishing expedition I refused:

- It is a **directional hypothesis with a stated prior**, not a scan. The prior is the published
  swap. State it, and state that it rests on **two** retrons.
- The **1.34× structural enrichment is not evidence and may not be cited as support.** Its range is
  0.59 to 1.86 across 15 chains from 5 groups and it spans 1.0.
- The test is the declared join of the Region-Y annotations to the modelling population, scored at
  **component level under A0's lineage-clustered variance**, with a single preregistered endpoint and
  no subgroup search.
- **Death condition:** if the exact-RT residual is not concentrated in Region Y at a declared effect
  floor, the hypothesis is reported as refuted and Region Y is closed for this project.
- It runs **after** A0 and A1, because if level 2 does not survive those there is no residual to
  localise.

## 15.3 · A third finding: an independent, protein-side retron type label exists

`references/rt0_rt7/toro_2026/SPIRE_retron_type_specific_HMMs.tar.gz` is registered in the repository
and contains **30 HMMs plus `calibration_thresholds.tsv`**, covering `typeI-A` through `typeXIII`,
`clade11`, `clade2_Ec107like` and an `all_retron_RT.hmm`. These are **protein** HMMs.

This matters because of the project's deepest circularity, stated in `CIRCULARITY_AND_LEAKAGE.md`
§1: *"'Retron type' is the ncRNA's own covariance model"*, which makes the embedding arm's type-label
control a label drawn from the other modality. **A protein-side type assignment breaks that specific
cross-modality tautology.** It is not fully independent, since Toro's tree is the source population
of Mestre 2020, but it moves the control from *tautological* to *same-lineage-different-modality*,
which is a real improvement and is available today.

Two qualifications. The material is registered TIER2, flagged **preprint, not peer reviewed**, with
`allowed_to_seed_rt07_definition = NO`; using it as an independent type label for a control is a
different use from seeding a definition and should be recorded as such. And these HMMs classify the
**RT protein**; they do not detect ncRNAs, so they do **not** directly close the zero-class question,
though the type coverage includes the six subtypes that have no covariance model.

Also registered and unused: `retron_reference_phylogeny_EPAng.newick` (202 KB), a published reference
phylogeny that is an external topology comparator for A17.

## 15.4 · The scale of the unregistered structural estate

| tree | structure files | size | registered in v7? |
|---|---|---|---|
| `RESEARCH-in-sleep-RETRON-DB_V4` | **36,695** | 5.0 GB | **no** |
| `RESEARCH-in-sleep-RETRON-DB_V3` | **6,598** | 1.9 GB | **no** |
| `..._v7-asset-audit` (the 62-chain register plus CATH benchmark) | 603 | 0.4 GB | yes |
| V1, V2, `RETRONS_january_2026`, `RESEARCH-retron-db` | 711 | ~0.2 GB | **no** |
| **the v7 main repo and its other 8 worktrees** | **0** | — | — |

Two independent Mestre-scale ESMFold sets exist: 1,919 models in V4 with landed pLDDT tables, and
1,946 in V3 under a different naming scheme. Nearly everything is ESMFold, so **pLDDT is available
but PAE is not**; the only predictions on disk with full PAE are **three** AlphaFold2 models.

Practical notes for A21: the Khan panel folds carry pLDDT only in the B-factor column with no summary
table, and sampled values sit in the 56 to 84 range, which is moderate rather than high. The Mestre
set does have a summary table and its first rows are high. **Benchmark before use, per §13.2(c), and
do not pool the two.**

## 15.5 · A prior candidate-selection exercise already ran, and one of its outputs looks broken

`/home/borg/RETRONS_january_2026/3rd_selection_ROUND_RETRONS/EMBE_SEQ_STRU_2/` contains a prior
computational orthogonality and candidate-ranking exercise over 62 candidates, with
`FINAL_SYNTHESIS_SHORTLIST.csv`, `double_dissimilar_candidates.csv`, RT TM-score and ESM2 similarity
matrices, and RiNALMo ncRNA similarity. A sibling directory holds nine named lab-candidate structures.

Two observations. **First**, §6 N11 rejects laboratory candidate prioritisation, and that rejection
stands on the evidence, but the operator should know that a prior exercise already produced a
synthesis shortlist. If any of those candidates were synthesised, the results are a genuinely
external functional dataset and should be located. **Second**, and this is a defect worth checking:
`dedup/same_rna_diff_rt_pairs.csv` is **empty, with zero data rows**, while the current project's own
frozen data records one ncRNA observed with **705** distinct RT partners and 17.72% of ncRNAs having
more than one. A zero there is either a different population or a broken query, and by this project's
own standing rule a zero from a search that cannot return anything is a bug signal.

## 15.6 · What changes in the programme

| item | previous status | revised status |
|---|---|---|
| **A23** literature cross-pair curation | essential, exploratory | **essential, with a named first target**: obtain the 7 × 7 editing matrix values |
| **C-30** orthogonality | "cannot be tested with assets held" | **"not tested here; published cross-pair data exists and has not been extracted"** |
| **N12** Region-Y join | rejected | **conditionally approved** as a preregistered directional test with a death condition, after A0 and A1 |
| **A21** predicted structures | generate a set | **audit and benchmark ~7,700 existing models**, ESMFold, pLDDT only, two Mestre-scale sets, do not pool |
| arm T's type-label control | tautological, unavoidable | **improvable today** using Toro 2026 protein-side HMMs as a second, cross-modality-independent type assignment |
| **A17** phylogeny | build from scratch | external comparator topology already registered and unused |
| designed swap panel | the prerequisite for step 12 | **still likely required for scale, but no longer the first action**; A23 determines how much is already published |

**The methodological lesson, and it is the one this review should end on.** Three of this document's
firmest negative statements, no phylogeny, no exchangeability data, no predicted structures, were all
inherited from a package whose scope was nine git worktrees. Each is false outside that scope. The
project's governance already contains the rule that would have caught it: *do not conclude a
dependency is absent until the registered environments and resources have been checked.* The rule
failed because **the registry itself is incomplete**, and no process exists that would notice. An
asset sweep with hashes, recorded in `data/README.md`, is now the highest-priority item in A4.

---

# 16 · THE PHYLOGENY IS NOT AN OPEN QUESTION. IT IS A MEASURED, REVIEWED, BOUNDED FAILURE.

*Added 2026-09-20 on completion of the prior-project audit. This section reverses §12.2(3) and A17 of
this review, and it rejects §4.1 and §4.2 of the external addendum. It is the most consequential
update in this document.*

## 16.1 · What was actually done

The prior project holds **312 tree artefacts**. Among them:

| arm | trees | tips | representation |
|---|---|---|---|
| `mestre_trees` | 6 | 1,843 | six alignment strategies of Mestre's published set |
| `c90_trees` | 5 | **2,000** | amino acid, clustered at 90% |
| `derep_trees` | 4 | 400 | a dereplication ladder at 50, 70, 80, 90% |
| `struct_trees` | 30 | ~400 | **structural MSA in amino acid, 3Di and partitioned** |
| `struct90_trees` | 20 | ~400 | the same, restricted to high-confidence models |
| `E1` | 27 | **5,495** | a window by occupancy sweep across nine settings |
| `s8_tree_declared` | 96 | 400 | every structural draw rescored with concordance factors |

All inference used ModelFinder with 1,000 ultrafast bootstrap and 1,000 SH-aLRT replicates. There is
a 28 KB preregistration written before any tree was built, with seven recorded amendments.

**Every published tree figure was independently verified twice.** Fifteen of seventeen reproduced
exactly on a different instrument. The reviewers found and filed two wrong figures and one arm that
was computed and never reported.

## 16.2 · The result, and why it is not a methods failure

Five routes were tested against predeclared criteria and five failed. The decisive measurement, and
the project's own words:

> *"48% of splits differ between draws that share 500 identical taxa. ... **This cannot be dismissed
> as under-powering. It is the best-powered RF measurement in the project.**"*

Resolution sits between **17.1% and 25.0%** across every representation tried, including the
structural ones. The structural route has its own diagnosis:

> *"All 5,256 RT domains are one tight fold family ... 91.0% of all pairs exceed TM 0.5. A saturating
> similarity measure over a set that is uniformly similar has almost no dynamic range to build a
> topology from."*

And the cause, which is the single most important scientific sentence recovered by this entire
review:

> *"**The trees do not fail because the characters disagree. They fail because there are not enough
> of them** — 157 alignable characters for retrons, 1.39 taxa per character."*

That is an information bound, not a methodological shortcoming. No alignment strategy, no
dereplication threshold, no structural alphabet and no model choice manufactures characters that are
not there.

**The negative was then made stricter and survived.** The preregistered rule required site
concordance above 33.3% in addition to bootstrap and aLRT support. The published statistic had
relaxed that conjunct, because concordance factors had been run once on a 60-taxon probe and transfer
bootstrap never ran at all. A second review computed the missing conjunct on six of nine arms and
reported: *"The negative is CONFIRMED, and the classification's tree-free basis gets STRONGER."*

## 16.3 · REVERSAL 3 — A17 is downgraded, and the addendum's §4.1 is rejected

§12.2(3) of this review upgraded the phylogeny on the operator's reasoning that core selection drives
topology and had never been tested. The external addendum went further and made it the programme's
backbone. **Both positions are wrong, because the sensitivity analysis largely exists.** Six alignment
strategies, a four-level dereplication ladder, a 27-point window and occupancy sweep, and three
structural representations constitute precisely the core-and-alignment sensitivity series I
specified. Its answer is that representation moves resolution between 17% and 25% and that none of
the options clears a defensible bar.

I therefore **reject the addendum's §4.1**. Making a tree the trunk of the programme would place five
downstream nodes on top of a result that has already been measured, independently reviewed twice, and
confirmed under a stricter rule.

**What genuinely remains untried, and it is narrow.** The prior project's own report states:

> *"🔴 **The RT0–RT7 derivation was never fed to the tree.** ... Never describe the phylogeny as
> domain-based."*

Every one of those 312 trees was built on a 341-residue anchor window, not on a derived conserved
core. The current project owns the one asset the prior project lacked: a frozen instrument assigning
conserved states per residue across 369,381 proteins. **Building one arm on that core is the only
untried core definition, and it is exactly the step-2-unlocks-step-3 dependency the operator
intended.** It should be run, once, to complete an existing series. It should **not** be run in the
expectation of producing a usable tree.

## 16.4 · The publishable result is the bound, not the tree

The most valuable finding in the audit is one the prior project's reviewer added and the prior
project itself did not headline:

> *"**And both surviving criteria now have the null neither had.** Supported-backbone recurrence is
> **0.397 against 0.0006**, and the c90 backbone RF is **0.483 against 0.9998**. **The negative is a
> bound, not an absence: there is real phylogenetic signal in these data — 660× chance on one arm —
> and not enough of it to carry a topology.**"*

This converts a five-route failure into a quantitative statement about the limits of bacterial RT
phylogenetics: **the signal is real and roughly 660 times chance, and it is insufficient to support a
resolved topology at 157 alignable characters.** That is a genuine, novel, defensible contribution,
it explains why published RT phylogenies disagree, and it is far more useful than another tree would
have been. It also independently corroborates the Mestre re-inference failure and reframes it: the
re-inference did not fail through incompetence, it failed because the characters are not there.

**Revised A17.** One arm on the mapper-derived core, added to the existing series, with the
**resolvability bound as the declared deliverable and a tree as an explicitly non-expected outcome**.
Falsification criterion: if the mapper-derived core does not exceed the best existing arm at 25.0% by
a declared margin, the series is closed and the bound is the result.

## 16.5 · REVERSAL 4 — co-evolution moves from deferred to closed

§13.6 recorded co-evolution as DEFER, conditional on a lineage-count floor, and the addendum's §4.2
argued against abandoning it. **That condition has now been tested five ways and cannot be met.**
Ancestry-aware co-evolution requires an RT topology. There is no resolvable RT topology, the failure
is bounded rather than merely underpowered, and the cause is a character shortage that no additional
pairs or better ncRNA objects can remedy. Adding pairs does not add alignable sites.

**Status: CLOSED, with two named reopening conditions.** First, a character source that materially
exceeds 157 alignable positions for retrons, which structure-informed alignment at greater depth
might supply and which nothing currently on disk does. Second, restriction to the shallow clades
where support does recur, accepting a correspondingly small number of independent units and declaring
that number in advance. The second is the only version I would entertain, and it is a bounded
sub-analysis, not the thesis chapter the original programme envisaged.

## 16.6 · Three propagating errors, and a tool defect

**(a) The package cites the wrong matrix at the wrong dimension.** `OPEN_QUESTIONS.md:79` and
`MINIMUM_REMAINING_WORK.md:89` describe *"an all-vs-all distance matrix over 1,919 proteins that has
never been built as a tree"*. Two distinct matrices are conflated: the Mestre Foldseek matrix is
**1,902 × 1,902** and was used only for a silhouette, while the tip-set matrix is **5,256 × 5,256**
and **was** built into trees. The error originates in `general/RETRON_STAGES/06_tree_and_structural_route.md:38`
and propagated into the review package. The narrow claim, that no tree was built from the Mestre
structural matrix specifically, is true; the sentence as written is not.

**(b) A superseded statistic is still in print.** The prior project's fold-geometry silhouette
(0.2565, z = 25.27) was superseded inside the current project by **0.156963, z = 2.75 to 2.81**
against random monophyletic partitions. Two current-project files still quote the superseded value.

**(c) A stage brief still asserts a claim the package has withdrawn.** `06_tree_and_structural_route.md`
states that a 2018 publication reported the same failure; the package records that as *"not found in
the sources, claim withdrawn"*.

**(d) A reportable tool defect.** IQ-TREE 3.1.3 accepts `--tbe` together with `--support` and
**silently ignores it**, producing byte-identical output files with a matching checksum. This was
verified by the prior project and is worth reporting upstream, because any study believing it
computed transfer bootstrap with that invocation did not.

## 16.7 · Reuse the assets, never the conclusions

The prior project's own closure documents record a poor reproducibility state: 26 untraced tables, 21
print-only scripts, **19 of 31 tree scripts write no artefact including both arms of the TM-distance
route**, four tables reconstructed from run logs rather than re-runs, a literature basis reconstructed
from the project's own prose rather than from the papers, a landmark register that partly fails
regeneration, and one published headline *"wrong by 224×"*. A supersession register exists and warns
that a reader trusting it before a given date would have cited three withdrawn results.

It also names its own attack surface: the upstream sequence window is *"[CHOICE], and not ours —
inherited from v3 with no derivation anywhere. **Everything downstream sits on it.**"*

**So the standing constraint in §14.3 is reaffirmed and sharpened.** The folds, the distance matrices
and the structural alignments are reusable engineering assets once hashed and registered. The tree
*conclusions* are reusable as **prior art that must be re-derived**, and the two quoted findings this
section relies on, the 157-character diagnosis and the 660-times-chance bound, must be recomputed in
the current project before either appears in a thesis or a paper. Both come from verification passes
rather than from the original analysis, which is the better provenance of the two, but neither is
promoted.

## 16.8 · Net effect on the programme

| item | status before this section | status after |
|---|---|---|
| **A17** de novo / core-sensitivity phylogeny | useful, upgraded on the operator's reasoning | **one confirmatory arm on the mapper-derived core; the deliverable is the resolvability bound, not a tree** |
| **A13 / co-evolution** | defer, conditional on a lineage floor | **CLOSED**, with two narrow reopening conditions |
| addendum §4.1, phylogeny as backbone | under consideration | **rejected** |
| addendum §4.2, co-evolution conditional | accepted in §13.6 | **superseded**; the condition has been tested and cannot be met |
| **A9** relatedness backbone | useful, enabling | **unchanged and now clearly the right instrument**, since it never depended on a resolved topology |
| a new thesis chapter | none | **"Why bacterial RT phylogeny does not resolve": a measured bound at 157 alignable characters and 660× chance, corroborating the Mestre failure** |
| Option A, the resource paper | first | **unchanged, and strengthened**: the bound is a natural companion result about what the catalogue can and cannot support |

---

# 17 · ASSESSMENT OF THE PROPOSED IMPLEMENTATION ARCHITECTURE

*Added 2026-09-20. Assessment of the implementation-architecture document, against the failure
history reconstructed in §1 to §16 rather than against general good practice.*

## 17.1 · Verdict: MODIFY

**Accept** the three-level hierarchy, the typed dependencies, the task state machine with
`COMPUTE_COMPLETE ≠ PASS`, the claim registry and its status vocabulary, the stage decision report
with named outcomes, the compute-class routing, the separation of computation from presentation
formatting, and the three-level prose policy. All are sound and several map directly onto documented
failures.

**Modify** two structural choices, in §17.3.

**The central criticism.** The document optimises for **orchestration**. This project's documented
failures were not orchestration failures. Counted across the arms audited above:

| failure mode | instances found | would the proposed architecture have prevented it? |
|---|---|---|
| a control was **declared and then not run** | **at least 7**, across 5 arms | **no** — declaring controls in a launcher is exactly what already happened |
| a wrong number **propagated through prose** | **at least 4** | **no** — all four lived in scripts and narrative, not in tables |
| **scope blindness**: the evidence base was larger than the declared project | 1, and it reversed 4 conclusions | **no** — nothing in the design discovers unregistered assets |
| a **criterion was amended after seeing results** | 3 | **partly** — a field exists, but self-committed preregistration is what already happened |
| a **PASS branch was structurally unreachable** | 2 | **no** |

A three-level launcher hierarchy is a tidier container for all five. **Build the mechanical checks
first and the hierarchy second**, or the same failures recur in a better directory structure.

## 17.2 · The four checks that matter more than the hierarchy

Each is small, mechanically enforceable, and directly derived from a documented failure. I would
write these against the **current** repository before any reorganisation, because each will find live
defects immediately.

**Check 1 · Controls are tasks, not fields, and they block.**
Every declared positive control, negative control and baseline becomes a task with its own state. **A
stage may not enter PASS while any declared control is in state `NOT_STARTED`.** The orchestrator
enforces it; no document can waive it. Stronger still, and this is the part that pays: **controls run
before the primary analysis, not after.** One documented control was found to be arithmetically
unpassable, with a ceiling of 84.8% against a required 95%, and the instrument was frozen and
deployed anyway. Running it first would have cost nothing and stopped the stage.

**Check 2 · A numeric provenance linter over prose.**
Every number appearing in any `.md` or `.tex` must either resolve to a canonical table cell by
`artifact_id` plus row and column, or be explicitly tagged as narrative. The build fails otherwise.
This single check would have caught all four propagating errors found in this review: a same-strand
figure hardcoded as a string literal in a producing script and wrong by 0.7 points; a distance matrix
cited at the wrong dimension and conflated with a different matrix; a superseded silhouette still in
print in two files; and a tool-agreement percentage used to support a claim it does not support.
§15 of the proposal covers tables and figures. **The errors were all in prose.**

**Check 3 · Reachability precondition.**
Before a task runs, it must demonstrate that its declared PASS outcome is **attainable given its
actual input population**. One stage's held-out tier contained zero instances of the class its
success rule required, so the PASS branch was unreachable by construction. Another arm's two trivial
baselines returned a constant on every held-out candidate, so a comparison reported as passed was
never evaluated. Both are checkable in advance, cheaply.

**Check 4 · Consumption gate on terminal state.**
Artifacts carry their producing task's terminal state, and the orchestrator **refuses to consume an
artifact whose producer is not in PASS**. This is the direct answer to the proposal's own stress-test
question 15, *"is there any way an autonomous worker could silently turn a failed result into a
downstream input?"* In the design as written, **yes**: nothing prevents a downstream task from
reading a table produced by a task that ended in FAIL or STOP. This is the single most important
safeguard in the document and it is currently absent.

**And one cheap addition to preregistration.** Require that the preregistration commit timestamp
precede the compute job's submission timestamp, and check it automatically. One preregistration in
this project was self-committed 53 minutes before its result, with no external timestamp and no
stated derivation for its threshold. Job submission times are recorded anyway, so the ordering check
is free.

## 17.3 · Two structural modifications

**(a) Stage 03 must not be the trunk. Split it.**
The proposal makes the phylogeny *"a central biological backbone"* with stages 04, 05, 06 and 07
depending on it. §16 of this review establishes that the phylogeny has been attempted at scale under
preregistration, failed five routes, was independently reviewed twice, and fails for a measured
character shortage of **157 alignable positions for retrons and 1.39 taxa per character**. Placing
four stages behind that node is the serial failure mode in a new form.

The proposal's own §20 already contains the fix, as decision OUTCOME B. Promote it from an outcome to
the structure:

```
03a · RELATEDNESS BACKBONE      (unconditional, cheap, robust)
        nested identity/ANI clusters; blocking for permutation;
        grouping for discovery; diversity stratification
        └── 04, 05, 06, 07, 09 depend on THIS
03b · RESOLVABILITY STUDY       (optional branch, one arm)
        the mapper-derived core added to the existing sensitivity series;
        deliverable is the BOUND, not a tree
```

Downstream stages take a **hard** dependency on 03a and **no** dependency on 03b. Stage 09's declared
hard dependency on a phylogeny should become a hard dependency on 03a plus a **conditional** one on
03b that, per §16.5, is currently not satisfiable.

**(b) Two stage questions remain circular by construction, and the architecture will not detect it.**
The proposal's stress-test question 4 asks this directly. Two cases:

- **Stage 04, retron RT features.** It asks which features distinguish retron RTs from other
  bacterial RTs. The retron class is defined by the annotation lineage, so a classifier trained and
  evaluated on that label re-learns the labeller. **Required fix, and it must be written into the
  stage launcher's anti-circularity field:** evaluation is held-out **subtype**, never held-out
  family, because there is only one retron family; and the external arm is the measured functional
  contrast of **67 producers against 36 measured non-producers**.
- **Stage 07, ncRNA discovery.** Its truth would again be covariance-model calls. **Required fix:**
  score only against published extents and deposited structures, keep the positional prior as an
  explicit competing arm, and require leave-one-subtype-out recovery of a withheld model as the
  admission control.

**And one task is too large to receive a defensible verdict.** Stage 11, the integrative
association/function model, has no single endpoint. As written it cannot return an adjudicable
PASS/FAIL. It must be decomposed into per-prior increments over a declared reference model, each with
its own floor, or it will produce a number nobody can adjudicate.

## 17.4 · Missing global agreements

The proposed `agreements/` set is good and incomplete. Five additions, each traceable to a documented
failure:

| agreement | why, in one line |
|---|---|
| **`SCOPE_AND_ASSET_DISCOVERY.md`** | the declared project was nine git worktrees; the real evidence base included ~44,000 structures, 312 trees and published cross-pair data. Declare the roots, and run a **periodic sweep that hashes what it finds and diffs against the registry**. A registry alone would not have caught this, because nothing was ever added to it |
| **`NEGATIVE_RESULTS_POLICY.md`** | the negatives are among this project's best assets. Governs how a negative is graded (refuted / underpowered / instrument-void), preserved, versioned, and reported in the thesis. The distinction has already been lost once, when a kill-criterion stop was labelled a partial pass |
| **`EXTERNAL_DATA_POLICY.md`** | the project already has the right pattern in one place, a resource register carrying a tier and an explicit `allowed_to_seed_..._definition = NO`. Generalise it, because published HMMs, a reference topology and published cross-pair measurements are all now in scope |
| **`SUPERSESSION_POLICY.md`** | supersede by a new record, never by editing history. A superseded statistic is currently still in print in two files, and a prior project's own register warns that a reader trusting it before a given date would have cited three withdrawn results |
| **`EFFECTIVE_SAMPLE_SIZE_POLICY.md`** | declaring an inferential unit is not enough. Require a stated **dependence structure** and a reviewed effective-n computation. This project published a degenerate effective-n formula in four result tables while its index document carried a different figure, and neither was the right number for the estimator actually used |

## 17.5 · The thesis artifact layer: yes, it risks becoming a second source of truth

The proposal asks this itself. The answer is yes, and the risk is **not** in the figures and tables,
which §15 handles correctly. It is in `sections/*.tex` and `captions/`. Those are prose containing
numbers, they become what people read and cite, and they drift. That is the same failure as the
hardcoded same-strand figure, one layer up and harder to see.

**Mitigation.** Generated sections and captions carry numeric **placeholders resolved at build time**
from canonical tables, and the build **fails** on an unresolvable placeholder. A hand-typed number in
a `.tex` file is a lint error, not a style preference. The proposal's Level A scaffold is the right
idea; it has to be enforced rather than encouraged.

**On promotion into the final thesis:** require an explicit release step, not a direct import. A
thesis that imports generated assets live will silently change under its author. Promotion should
copy a tagged, hashed artifact set and record the tag.

**On failed stages in the report:** a failed stage should render a full section with its question,
its predeclared criterion, the measured result, and its interpretation as a bound. §16.4 is the
worked example: *"the signal is real at roughly 660 times chance and insufficient to carry a
topology"* is a better section than any tree would have been. The report should make that the normal
presentation of a negative, not an exception.

## 17.6 · What I would do, in order

The proposal's §24 principle is right and I would sharpen it. The scarce resource is not compute, and
it is not reviewer attention either. **It is untouched evidence.** This project has already consumed
its only pairing holdout by cross-fitting every fold, and it cannot get it back. An orchestration
system should therefore treat confirmatory populations as a **budget that depletes**, and require any
task that trains on, tunes against or inspects a population to declare it, so the orchestrator can
refuse a later confirmatory claim on that same population. Nothing in the proposal does this, and it
is the one resource that cannot be replenished with more Ibex hours.

Recommended sequence:

1. **Do not build the full skeleton yet.** It is a large refactor, and the four checks are worth more.
2. **Write the four checks against the current repository.** Each will find live defects; the numeric
   linter is known to find at least three.
3. **Run the asset sweep and register what it finds**, with hashes. This is already the highest
   priority zero-cost item in §15.6.
4. **Pilot the architecture on exactly one stage, end to end**, including the thesis artifact layer
   and a stage decision report. My candidate is **ncRNA architecture (A5)**: it is the highest-value
   unstarted work, it is cheap, it has a genuine positive control in the deposited complexes, and
   because it is currently un-analysed it is the only stage where the pilot cannot be contaminated by
   inherited conclusions.
5. **Generalise only after that pilot produces a stage decision report and a compiling artifact set.**

This ordering also has the property that if the architecture turns out to be wrong in some way
neither reviewer has anticipated, the cost is one stage rather than the repository.

---

# 18 · REVERSAL 5 — the ncRNA work is PARTLY ANSWERED, and the remaining gap is better than the one I proposed

*Added 2026-09-20 on completion of the prior ncRNA audit. A5, this review's single strongest
recommendation, is substantially wrong as framed. What replaces it is narrower, better controlled,
and has the anti-circular anchor the whole RNA side has been missing.*

## 18.1 · What already exists, verified by sequence rather than by citation

| component of A5 | status | evidence |
|---|---|---|
| **fold the ncRNA** | **DONE at scale** | **16,351 of 16,458 (99.35%)** of the current ncRNAs are byte-identical, forward or reverse-complement, to a sequence already folded with RNAfold and annotated with bpRNA, dot-bracket stored, in a prior project's `p2_structures.parquet` (16,359 rows) |
| **a1/a2 inverted repeat** | **DONE at scale, three instruments** | **15,772 of 16,458 (95.83%)** already carry a call, with a per-span dinucleotide-shuffle null and a 210,862-sequence negative set. Gold panel 0.8129 against group II intron background 0.0959, an 8.5-fold separation |
| **msr / msd split** | **DONE as features, NEVER as coordinates**, and the rule was demoted | 346,455 records over 16,359 sequences carry msr and msd presence flags from `cmalign` against the same 21 covariance models. No start/end table exists anywhere. The rule was demoted because it *"would classify 47% of experimentally confirmed ssDNA-producing ncRNAs as structurally incomplete"* |
| **branching guanosine** | **COMPUTED AND REFUTED** | 22 sets. *"Every one of the 22 sets passes the pre-registered ≤10 nt bar — and so does its own dinucleotide shuffle. The median offset is 1.0 nt: from any position in a GC-containing sequence, the nearest G is a base or two away. The tightness is base composition, not a motif."* The gold panel does not beat its own shuffle |
| **msDNA / RT-DNA extent** | **GENUINELY OPEN** | never computed in any tree; the 81 experimentally determined RT-DNA sequences were never used for it |

**None of this was carried into the current project.** The prior task directories return zero hits
across the whole v7 tree. So this review's statement was true of the v7 corpus and false about the
project's history, which is the same failure as §14 through §16.

**One correction to this review's own supporting detail.** §1.2 P5 said ViennaRNA *"sits unused in
the environment lock files"*. True of v7's scripts; but ViennaRNA 2.7.0 is installed and working in
the primary environment, with RNAfold, RNAduplex, RNAplfold, einverted and Infernal all available.

## 18.2 · The bounded negatives are the valuable inheritance

Five successive versions each refuted the previous one, with independent reviews that bit. What they
leave behind constrains any successor:

- **The branching G is not findable from sequence alone**, and the prior work states the precondition
  exactly: *"you cannot identify which G is the branch point without already knowing the msr/msd
  boundary — so it is downstream of the detection problem, not an independent input to it."*
- **An MFE-based a1/a2 completeness caller has a 90.7% false-positive rate on non-retron ncRNA** and
  misses 59.7% of arm truncations. Its own author withdrew it.
- **Naive terminal-complementarity callers lose to baselines**: IoU 0.5174 against 0.5312.
- **Band limits destroy the signal**: `RNAplfold -L 100` provably removes the a1/a2 duplex, and
  94.94% of labelled positives are longer than that limit.
- **RNAfold beats the RNA language model decisively** for base-pair recovery, 0.9508 against 0.6773
  on the low-circularity subset, and the gap *widens* when circularity is suppressed. **This settles
  the tool choice before it is asked**, and it also bears on the pairing arm: the RNA representation
  used there carries the structure poorly.
- **Fold the right object.** *"We fold the EXTRACT; the cell folds the TRANSCRIPT. And it is
  circular: to fold the right object you need the boundary you are predicting."* Never addressed.

## 18.3 · The circularity, stated more bluntly by the prior work than by this review

> *"Every positive label in the training corpus derives from the 21 padlocdb covariance models. ...
> Novelty cannot be demonstrated with ground truth defined by the instrument being beaten. ...
> `support.csv`'s published molecules are the sole label source in this project that is not
> CM-derived. 120 of them locate in the pool. And they split 56 CM-recoverable / 64 CM-gap — so the
> half that could have demonstrated novelty is the half where both arms sit at chance."*

The msr/msd features that exist were produced by `cmalign` against those same 21 models, so they
inherit the circularity in full. **Any coordinate-level successor must not be built that way.**

## 18.4 · The replacement task, and why it is better than A5 was

A5 proposed to fold, find the inverted repeat, locate the branch point and segment. Three of those
four are done or closed. What remains is narrower and has a genuine anti-circular anchor that this
review did not identify:

> **The 81 experimentally determined RT-DNA sequences define where msd is, directly and
> independently of any covariance model, because msd is the template for the RT-DNA.**

That is an experimental readout mapping onto ncRNA coordinates. It is the only non-CM boundary label
the project has ever had on the RNA side, it has never been used for this, and it converts the msr/msd
boundary question from a circular one into an anchored one. It also supplies, for free, the
precondition the branching-G refutation named.

**Revised pilot, `T-A5b`:** establish msr/msd **coordinates** and RT-DNA extent on the ncRNA,
anchored on the 81 experimental RT-DNA sequences, reusing the existing folds and a1/a2 calls rather
than recomputing them, with the prior work's RNAfold base-pair recovery of 0.9137 to 0.9508 as the
declared positive control.

**Population realism, declared in advance.** The anchor is 81 molecules, of which the honest
evaluation split is the 56 CM-recoverable against the 64 CM-gap. This is a small, bounded, carefully
controlled analysis, not a corpus-scale claim. Its deliverable at 16,458 is a **confidence-graded
coordinate set**, and the claim it can support is about the anchored subset.

## 18.5 · Net effect

| item | before | after |
|---|---|---|
| A5 msr/msd architecture | essential, the largest unstarted opening | **superseded by T-A5b**: folds and a1/a2 are done and reusable; coordinates and RT-DNA extent are the real gap |
| the pilot stage | A5 | **T-A5b**, still the pilot, now with a real positive control and a non-circular anchor |
| RNA representation in the pairing arm | untested | **evidence exists that a folding tool recovers the structure far better than the language model used**, which is a live limitation of the pairing work |
| prior-work checking | recommended | **five for five.** Every check changed a conclusion. This is the backlog, not the steady state |
