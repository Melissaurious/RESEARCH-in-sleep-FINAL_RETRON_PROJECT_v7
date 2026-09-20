---
record: R2_ADVERSARIAL_PRECHECK
task_id: T-R2-ncrna-internal-architecture
date: 2026-09-20
kind: ADVERSARIAL PRE-CHECK — does Stage 1 have a biological question, or only 81 numbers?
status: findings for the R2 review. R2 remains DRAFT.
---

# Adversarial pre-check on R2 Stage 1

**Question put to the draft:** *"R1b already showed all 81 are exact reverse-complement matches at
roughly half the ncRNA. What does Stage 1 add beyond restating 81 coordinates?"*

Run on the landed `R1b_anchor_coordinates.tsv`. **No population spent; nothing executed for R2.**

## 1 · ✅ There is a real signal — the RT-DNA fraction is far tighter than chance

| | observed | shuffled pairing (2,000×) |
|---|---|---|
| sd of RT-DNA / ncRNA fraction | **0.1166** | median **0.2203**, p05 0.2024 |

**The observed spread is tighter than 100 % of 2,000 random RT-DNA↔ncRNA re-pairings.** RT-DNA
length is matched to *its own* ncRNA length far more closely than to an arbitrary one.

Mean fraction **0.582**, sd 0.117, CV **0.20**.

## 2 · Subtype explains only about a third of it

| metric | global sd | mean within-subtype sd | ratio |
|---|---|---|---|
| RT-DNA fraction | 0.1166 | 0.0769 | **0.66** |
| normalised 5′ start | 0.1208 | 0.0786 | **0.65** |

A ratio near 1.0 would mean subtype explains nothing; far below 1.0 would mean the architecture is
subtype-specific. **0.66 says the constraint is largely global across retrons**, with a real but
modest subtype component.

**Some subtypes are strikingly tight:**

| subtype | n | mean fraction | sd |
|---|---|---|---|
| **XIII** | 7 | 0.614 | **0.036** |
| **II-A1** | 6 | 0.497 | **0.034** |
| **XI** | 5 | 0.497 | **0.039** |
| III-A2 | 5 | 0.729 | 0.054 |
| III-A5 | 9 | 0.572 | 0.097 |
| I-C1 | 9 | 0.610 | **0.128** |

Three subtypes hold the fraction to within ±4 %. That is a **candidate architectural constraint**,
and it is the kind of thing Stage 1 exists to surface.

## 3 · ⛔ THE BLOCKER FOR THE REVIEW: this may be circular

**Everything above assumes the panel's `ncRNA_sequence` was annotated *independently* of the
measured RT-DNA.**

⛔ **If the panel authors defined the msr–msd boundaries by reference to the msDNA they observed,
then "the RT-DNA occupies ~58 % of its ncRNA" is true by construction and carries no biological
information.** The tightness would be an artefact of the annotation procedure, and the shuffled
null in §1 would not detect it — shuffling breaks the pairing, so it tests whether *this* RT-DNA
matches *this* ncRNA, not whether the ncRNA bound was drawn using it.

**This is exactly the error class R2 already guards against for Buffington** — refusing to call the
`ENGINEERED_DELTA` an msd until construct design is verified. **It applies to Tier A with equal
force and the draft does not currently say so.**

### Required before Stage 1's fraction/normalised-coordinate results may be interpreted

1. **Establish the provenance of `ncRNA_sequence` in the panel.** Was it annotated from the genome
   independently, or derived from the observed RT-DNA extent?
2. If independent → §1 and §2 are interpretable as architecture.
3. If RT-DNA-derived → **the fraction is definitional**, must be reported as such, and only the
   *residual* structure (e.g. why XIII is tight and I-C1 is not) retains meaning.
4. If it cannot be established → report the result **with the ambiguity stated**, never as
   architecture.

⚠️ This is a **Tier-B question** — it needs the panel's own publication, traced. `Tier B is
currently empty.`

## 4 · Effective n is ~23, not 81

81 elements span **23 distinct `retron_sub` values**; 8 strata have n ≥ 5, covering 57 of 81;
8 are singletons. ⛔ **Cross-subtype inference has an effective n nearer 23 than 81**, and the
`n ≥ 5` stratification rule already in the draft is the right instinct but does not by itself fix
the independence problem.

## 5 · Verdict for the review

| | |
|---|---|
| **Does Stage 1 have a biological question?** | **Yes.** The fraction is non-random and subtype-structured |
| **Is it safe to interpret today?** | ⛔ **No** — until §3 is resolved |
| **Does this change the design?** | **One addition:** a Tier-B provenance check on `ncRNA_sequence`, as a **prerequisite to interpretation**, not a caveat in the discussion |
| **Does it change anything already landed?** | **No.** R1b's coordinates are exact and unaffected |

**Recommendation:** add §3 to the R2 launcher as a **blocking interpretive gate** — Stage 1 may
*compute* the fraction regardless, but may not *interpret* it as architecture until the ncRNA
annotation provenance is established.
