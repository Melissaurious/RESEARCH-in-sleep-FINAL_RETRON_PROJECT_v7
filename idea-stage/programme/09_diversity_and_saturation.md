# Stage 9 · Analyze diversity and saturation of the data

## 0 · The point of this task

We cannot currently make any statement about diversity, because the four identity figures
that every divergence argument in this project rests on reproduce **none** of the numbers
the script that supposedly produced them actually wrote — and their ordering is inverted.
Separately, we have never asked whether the corpus is **saturated**: whether more
sequencing would reveal new RT families or only more copies of the ones we have. Once this
lands we either have defensible per-family diversity numbers or a documented reason we
cannot have them, plus a rarefaction curve that states how complete the sampling is. Until
then, no diversity sentence can be written in either direction.

## 1 · ⛔ THE BLOCKER — resolve this before anything else in the stage

`stage0_positioning/FROZEN_FACTS.md` §5 records mean pairwise identity:

| subtype | `FROZEN` §5 | the script's own saved table | a verbatim port of that script |
|---|---:|---:|---:|
| VI | **40.4** | 20.99 | 20.99 |
| XI | **36.5** | 27.34 | 27.34 |
| I-C1 | **48.2** | 37.55 | 37.56 |
| III-A2 | **47.0** | 30.03 | 30.59 |

- The port reproduces **the script's own table** to two decimals and **none** of FROZEN's
  four figures.
- The script's own verdict on **all four rows** is `DIVERGE - investigate`.
- ⛔ **FROZEN's *"ordering preserved"* is false** — the script has **XI > VI**; FROZEN has
  **VI > XI**.
- **`V_verify` §V2's entire "divergence, not seed count" account inherits these numbers**,
  as do `denovo_family/PREREG.md` §2 and the owner's last two letters.

> ⛔ **Until the provenance is resolved, no number may be placed on that axis in either
> direction.**

⭐ What survives is a **direction only**, on the real output: 37.56 → 73.3% · 30.59 → 50.0%
· 27.34 → 0/8 · 20.99 → 0/6. ⚠️ **Four points, two tied at zero. Never a curve.**

Artefacts: `denovo_family/tables/d09_ported_identity.tsv`,
`stage0_positioning/tables/claim3_seed_vs_identity.tsv`.

## 2 · What must be delivered

- **Per-family diversity** on a declared unit, with the identity computation re-derived
  here — or a written statement that it cannot be reported and why.
- **A saturation / rarefaction curve** with **replicates**, per family: does adding
  genomes add new families, new unique RTs, or only new loci?
- **The redundancy ladder** as the denominator correction: locus → distinct `genome_id` →
  `species` → `genus` → `source_database`, within each `taxonomy_system`.
- A statement of **which cross-family comparisons the corpus can support** after
  correcting for sampling depth.

## 3 · Prerequisites and gates

| gate | why |
|---|---|
| ⛔ **FROZEN §5 resolved** | it gates every divergence sentence in the project |
| ⛔ **`r02`'s redundancy ladder** | a diversity number without it measures sequencing effort |
| ⛔ **Stage C, a positive control** | this stage will produce negatives; a negative from an instrument that could not have said otherwise is worthless |

## 4 · Traps already paid for

- ⛔ **Nearest-neighbour density IS pool size.** An **8× pool difference** produced an
  entire false "difficulty" finding. Rarefy the larger pool **before** comparing best-hit
  rates.
- ⛔ **Rarefaction needs replicates.** Rarefying removes the bias and adds variance — one
  draw left a family rank uncertain by **±5 places**.
- ⛔ **The locus→unique-RT factor varies 1.74×–7.39× BY FAMILY.** A locus-based diversity
  comparison across families compares sampling depth, not biology.
- ⚠️ **Ranges and ratios hide the cherry-pick** — never verify a range by its endpoints;
  enumerate every pair and check both arms share a denominator and a threshold.
- ⚠️ **A ported predicate is not a preserved predicate** — code carries over, meaning does
  not. Check the new substrate's redundancy before reading any primary number.

## 5 · Decisions for the operator

1. Whether FROZEN §5 is **repaired** (find the real provenance) or **voided** (declare the
   figures unsourced and rebuild from raw). The second is cheaper and more honest.
2. Whether "saturation" is asked at the level of **families**, **unique RTs**, or
   **systems** — three different curves.

---

# 6 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §11

## ⭐ The saturation curves, made specific

The ideas document turns "saturation" from one curve into eight, each answering a different
question:

    genomes sampled -> unique RT sequences        genomes sampled -> ncRNA families
    genomes sampled -> RT clusters                genomes sampled -> accessory architectures
    genomes sampled -> retron RT clusters         genomes sampled -> fusion architectures
    genomes sampled -> unique RT-ncRNA pairs      genomes sampled -> retron subtypes

⭐ **The most valuable question in the whole section:** *are ncRNAs less saturated than RT
proteins?* If they are, the field's ncRNA-based detection is the limiting instrument, which
connects directly to `extraction_first`'s finding that **the detector loses 36 of 45
molecules while extraction loses 6**. Two independent lines pointing at the same
conclusion.

⚠️ Four of the eight curves are **not computable yet**: ncRNA families needs stage 10,
accessory architectures needs stage 7, fusion architectures needs stage 8, retron subtypes
is blocked because **`system_subtypes` is two disagreeing tools pooled** and no per-subtype
rate is currently computable at all.

## Stratification — and one axis the record never handled

Phylum · class · genus · environment · database · **isolate versus metagenome** ·
**assembly quality**.

⭐ **Isolate vs metagenome is a genuine gap.** It appears nowhere in prior work, and it is
likely a large effect: `source_database` spans GTDB, NCBI, MGnify (human gut, marine, soil)
and GEM, which mixes isolate genomes with metagenome-assembled ones. A saturation curve
pooling them measures sequencing programmes, not biology. **Declare the split before
computing.**

⚠️ **`full_lineage` is two schemas** — gtdb 7-field, ncbi 3-field with **no phylum**, and
~61% of rows are ncbi. Phylum- and class-level stratification therefore works on a minority
of the corpus unless the D5 metadata join (stage F) is done first.

## Metrics

Rarefaction · accumulation curves · **Chao estimators** · **Hill numbers** · Shannon ·
**singleton / doubleton counts**.

⭐ Chao and the singleton/doubleton counts are the right additions — they estimate *unseen*
diversity, which is the actual question, rather than describing what was seen. Neither
appears in prior work.
⚠️ **Every one of these needs replicates** — one draw left a family rank uncertain by **±5
places**. And Chao is sensitive to exactly the duplicate classes stage 1 must resolve: a
strain represented by three assemblies inflates the doubleton count.

## ⭐ The question that reframes the stage

> *Does taxonomic oversampling create a false impression of saturation?*

**This is the whole stage in one line, and prior work already says yes in a related case:**
the locus→unique-RT factor varies **1.74×–7.39× by family**, and **nearest-neighbour
density IS pool size** — an 8× pool difference produced an entire false "difficulty"
finding. So the redundancy ladder (`r02`) is not a preliminary to the saturation curve; it
is the **denominator correction inside** it.

## Restatement of the blocker

None of the above changes §1: ⛔ **FROZEN §5's four identity figures reproduce nothing the
script produced, and the ordering is inverted.** A saturation curve can be computed on
counts without touching identity — but the moment a *divergence* or *identity* axis enters,
the blocker applies.
