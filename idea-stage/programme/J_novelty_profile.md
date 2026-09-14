# Stage J · Novelty as a profile, not a score
**Proposed addition. From `RETRON_RT_PROJECT_IDEAS.md` §17.**

## 0 · The point of this task

"Novel" in this field almost always means low RT sequence identity, which is one axis out
of many — a system can be entirely conventional in its RT and unprecedented in its ncRNA,
its effector, its fusion, or its architecture. We currently have no way to say *how* a
candidate is new, only how far it sits from known sequences. Once this lands, every system
carries a **novelty profile** across independent axes rather than a single collapsed
score, so a reader can see which dimension is unusual. That is what makes experimental
prioritisation defensible instead of a ranking nobody can interrogate.

## 1 · The axes

From the ideas document, with the prior work that already bears on each:

| axis | what exists already |
|---|---|
| **RT sequence** | the corpus and the redundancy ladder (stage 1); ⚠️ the identity figures that would calibrate "far" are **blocked** — see stage 9 |
| **RT structure** | 9,965 structures mapped and sha1-verified; foldseek all-vs-all TM matrix over 1,919 proteins |
| **ncRNA sequence** | needs `r03`'s paired table; ⚠️ **~46% of retron loci may carry no ncRNA at all** |
| **ncRNA structure** | ⛔ never attempted; CMcompare + R-scape on the existing 21 CMs is parked |
| **accessory protein** | ⛔ the genome layer is untouched — **41,250,531 accessory CDS, ≈26 CPU-min** |
| **fusion domain** | ⛔ fusion has only been a confound, never catalogued (stage 8) |
| **operon architecture** | ⛔ never delimited (stages 7, A) |
| **unusual RT–ncRNA pairing** | ⭐ stage 1 already asks for one-ncRNA-across-many-RTs and the converse |

## 2 · Why a profile beats a score

- ⛔ **Ranges and ratios hide the cherry-pick.** A collapsed score is a range read by its
  endpoints; enumerate the axes and report each.
- ⛔ **Never pick candidates by top-N score** — stratify against the positive distribution.
  A single novelty score invites exactly the top-N selection that has already produced bad
  candidate sets here.
- ⚠️ **The axes are not independent, and that is measurable.** `polythetic` found that
  **every real axis fell BELOW chance** against a shuffled one — the axes group what
  sequence already groups. So a profile must report **axis redundancy**, or it will present
  one signal as six.

## 3 · What must be delivered

- **A per-system profile** — one value plus its reference population per axis, never a sum.
- **The reference for each axis, declared.** "Novel" is relative; stage I (the non-retron
  reference set) and stage 1's frozen datasets are what it is relative to.
- **Axis redundancy, measured.** Pairwise correlation between the axes, so a reader knows
  how many independent dimensions there really are. `polythetic`'s result predicts fewer
  than the list suggests.
- **The absence axis handled explicitly.** A system with no detected ncRNA is either novel
  or a detection failure, and the project cannot yet tell those apart — say so rather than
  scoring it.

## 4 · Prerequisites and gates

| gate | why |
|---|---|
| ⛔ **Stage 9's FROZEN §5 blocker** | the identity axis has no calibration until the four irreproducible figures are resolved; **no number may go on that axis in either direction** |
| ⛔ **Stage I** | novelty is relative to a reference set that does not yet exist |
| ⛔ **Stage A (delimitation)** | an "unusual boundary" cannot be distinguished from a badly-drawn one while both instruments localise and neither delimits |
| ⚠️ **Stage H** | a system that moves placement under perturbation will look novel; those are different things and must be separated |

## 5 · The honest caveat to build in

`polythetic` already ran the closest thing to this and returned a **pre-registered
negative**: polythetic coverage of the myRT-alone stratum reached **60.26%** but beat the
shuffled axis in **0 of 24 cells**, at any floor, in either arm — and every real axis fell
*below* chance, which the pre-registration named as **positive evidence of redundancy**.

> The conclusion on record: *"a de novo scheme cannot cover this population, and the honest
> paper is about why classification stalls rather than a new scheme."*

**This stage must be designed against that finding, not in ignorance of it.** A novelty
profile is defensible as a *description* with declared axes and measured redundancy. It is
not defensible as a new classification, and the difference should be stated in the
pre-registration.

## 6 · Downstream, explicitly out of scope here

Experimental candidate prioritisation, conditional RT/ncRNA design, and any
compatibility-prediction model are **downstream sub-projects** (ideas §19), unlocked by
this stage but not part of it.
