# Stage 12 · Annotation disagreement as a signal

*(three tools for retron annotation)*

## 0 · The point of this task

Three tools annotate retrons in this corpus and they agree on **44.6%** of loci. Everyone
in the field treats that agreement as validation — but the tools **share one parent**: all
21 retron ncRNA covariance models were authored by the same group, and the DefenseFinder
profiles were iterated until they recovered the known set. Agreement between them
therefore cannot be corroboration, and nobody has measured the **disagreement**, even
though the largest cell of our own flagship table is *"neither instrument detected
anything."* Once this lands, disagreement becomes a signal that points at what the field
cannot see — a result no published detector paper holds, because **not one published
detection method has ever been evaluated on held-out families**.

## 1 · ⭐ The assets already on disk

| asset | detail |
|---|---|
| **two tools in one field** | `system_subtypes` carries DefenseFinder (capital-initial) and PADLOC (lowercase) **on the same locus**, agreeing on **44.6%**. ⚠️ Never `groupby` the pooled field |
| **asymmetric filtering** | PADLOC and DefenseFinder were extracted **retron-only**; myRT **unfiltered**. `detected_by` is comparable **within retrons only** — a cross-family detector table would be wrong by construction |
| **shared parentage** | `padloc-retron-ncrna-cms-authored-by-mestre` — **all 21**; `defensefinder-retron-profiles-iterated-to-recover-known-set`; `retron-detectors-share-one-parent`. Per EVIDENCE_STANDARDS §3b, **models descending from one publication cannot corroborate each other** |
| **known blind spots** | `padloc-misses-contig-split-systems`; `padloc-single-gene-sensitivity-traded`; `schnoes-misannotation-5-to-63-percent` |
| **the field has no benchmark** | `lit_detector_audit`: our 0/9 is **unmeasurable** against the detection literature — none of the six published detection-in-genomic-context methods was ever evaluated on held-out families. It is *typical* against the adjacent literature that has run the test |
| ⭐ **the measurement is sitting there** | `E2`: `msr_msd_family` is **44.4% the literal string `nan` scored as a category**; `landmark` is **48.3% `NEITHER`**. **The largest cell of the flagship concordance table is "neither instrument detected anything"** — two pattern-matchers failing on the same divergent proteins |

## 2 · What must be delivered

- **The full agreement matrix**, per tool and pairwise, on a declared unit — never pooled.
- **The disagreement classes, named:** which tool sees what the others do not, and what
  those loci have in common. `E2` says the biggest class is *neither* — characterise it.
- **A statement of what the tools jointly cannot see**, with the shared-parentage argument
  made explicit so agreement is never offered as validation.
- ⛔ `PE16` — **annotate by several independently-provenanced routes and prove they CAN
  disagree before claiming they agree.** Never run.
- ⛔ `PE14` — **the object register**: what has the field actually aligned, per study, and
  has the object changed? **Publishable with no computation.** See stage B.

## 3 · Why this should run early

It is the cheapest stage on the list — the data already exists and is merely mis-scored.
It needs no new compute, no cluster, and no model. And it is the project's through-line:

> **The retron detectors share one parent, none has been evaluated on what it cannot see,
> and what they reject is mostly catalytically intact reverse transcriptase.**

That sentence is a paper the field has not written, and it is assembled from this stage
plus `PE14`, `PE16`, `A11`, `D7` and `s5_admission`.

## 4 · Prerequisites

**Stage 1** for the three-tool agreement flags — which stage 1 already lists as a
deliverable. Nothing else blocks it.

## 5 · Traps already paid for

- ⛔ **`system_subtypes` pooled is meaningless.** Split by tool first, always.
- ⛔ **`detected_by` cross-family is invalid** by construction, not by accident.
- ⚠️ **A detectability label tracks lineage**, which inflates a global null and is
  correctly stripped by a relatedness-preserving one — so any "disagreement correlates
  with X" claim needs stage D.
- ⚠️ **Order matters:** ① drop or mark missing → ② re-cut the labels → ③ apply the
  phylogenetic null. Doing ③ first tests the wrong table (`D0`).
- ⚠️ **`D7`:** the selection-error class has **six instances across the project's own
  scripts** — our own annotation disagreements are part of this stage's subject matter.

---

# 6 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §14

## ⭐ The disagreement taxonomy — this is the missing piece

The ideas document enumerates the disagreement *types*, which the record never did. Each
has a different cause and a different consequence:

| disagreement | what it points at | status |
|---|---|---|
| **myRT family disagrees with phylogeny** | ⛔ unavailable — no resolved tree; ⚠️ and myRT was extracted **unfiltered** while PADLOC/DefenseFinder were retron-only, so this comparison is asymmetric by construction |
| **PADLOC vs DefenseFinder** | ⭐ **available now** — `system_subtypes`, agreeing on **44.6%** |
| **sequence classification vs structure** | ⭐ **available now** — `s7q_gateS_structural_concordance.py` exists; 9,965 structures are mapped |
| ⭐⭐ **RT appears valid but no ncRNA is found** | **the ~46% zero-ncRNA class.** This is the single largest disagreement class in the corpus and it is `r03`'s first number. The ideas parking lot calls it *"detect orphan retron-like RTs with no ncRNA"* |
| **ncRNA found but architecture unusual** | needs stage 7's architecture alphabet |
| **YXDD weak or absent despite convincing RT structure** | ⭐ `A5` is the worked precedent — **cluster 170's 0% is biology, not folding failure** (pLDDT 94.8 at the tetrad) |
| **expected domains absent in apparently complete proteins** | ⭐ `E1` — *"complete"* means **ORF-complete**, and **69.2% do not fill the RT window**. This disagreement is already quantified and unreported |

⭐ **Two of these are measurable today with no new compute** (PADLOC vs DefenseFinder;
sequence vs structure), and two more are already quantified but sitting in other stages'
findings (`E1`'s 69.2%, `A5`'s cluster 170).

## The four questions, and how to keep them answerable

> *Which disagreements are technical? Which reflect classification limits? Which identify
> biological novelty? Are disagreements concentrated in particular RT families?*

⚠️ **The last question is the trap.** *"Concentrated in particular families"* is a
lineage claim, and **a detectability label tracks lineage** — which inflates a global null
and is correctly stripped by a relatedness-preserving one. So family concentration needs
**stage D**, and the order is fixed (`D0`): ① drop or mark missing → ② re-cut the labels →
③ apply the phylogenetic null.

⭐ The first three questions are separable **without** a null, by cause: technical →
contig-split, strand, truncation flags (stage 1); classification limit → the tools' shared
parentage (all 21 CMs are Mestre's); novelty → what survives both (stage J).

## From the parking lot (§21), belonging here

- ⭐ *"Quantify where existing retron HMMs fail"* and *"where existing covariance models
  fail"* — this is the **positive form** of the stage, and it is publishable: no published
  detection method has ever been evaluated on held-out families, so a failure map is new
  information rather than criticism.
- *"Look for transitional systems between RT families"* — the disagreement population is
  where these would live, and it overlaps stage H's movers.
