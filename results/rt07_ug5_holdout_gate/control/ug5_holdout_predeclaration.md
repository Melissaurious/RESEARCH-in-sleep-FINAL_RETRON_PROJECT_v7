# UG5 whole-family holdout — PREDECLARATION

Written **before** any construction on the six retained families and **before** any UG5 sequence
was mapped. A NEW pre-`g4b` gate, not a repair to g4a: g4a's within-family challenge claim is
separately and honestly bounded.

Authority: independent review of g4a, `WHOLE_FAMILY_HOLDOUT: REQUIRED`, classification **B**.

## 1 · The question

> Can a shared RT coordinate structure derived **without any UG5 information** transfer to UG5
> sequences better than negative controls, with stable anchor order and coordinates?

This is a **transferability** test. It is **not** a test of biological boundary accuracy, and no
boundary claim may be made from it.

## 2 · Construction set

Six families: `Retrons`, `GII`, `DGRs`, `CRISPR`, `UG3`, `AbiA`.

**`UG3` is retained** as the represented UG lineage, so a successful transfer cannot be dismissed
as "UG was simply absent", and a failed transfer cannot be excused by it.

Derivation sequences are exactly the repaired g4a derivation sets for those six families.

## 3 · Total UG5 exclusion

Excluded from construction: every UG5 amino-acid sequence · alignment · HMM · HHM · pairwise
map · threshold · tuning decision · match-state definition · any cached object derived from UG5.

**Audited mechanically, not by filename inspection.** `ug5_holdout_provenance_audit.tsv` records,
for every construction input, whether any UG5 sequence appears in it — by scanning file **content**
for UG5 sequence ids and for the sequences themselves. The gate asserts
`UG5_GENEALOGY_PRESENT = FALSE` for every input and **fails closed** otherwise.

## 4 · The frozen shared frame

After construction the frame is **frozen**. Frozen means: the set of anchor positions, in the
coordinate system of a declared construction-side reference family, fixed before any UG5 sequence
is examined.

Anchors are the **`ALL_PARTNERS` positions of the six-family construction** — positions aligned to
every one of the other five construction families. No UG5 information enters their selection.

The declared reference family for anchor coordinates is **`GII`**, chosen before execution because
it is the construction family with the largest eligible population and it is not a UG family.

## 5 · UG5 evaluation split, declared before any mapping result is seen

UG5's 67 eligible sequences are split by **whole separation components** at the same link rule
(`identity >= 0.30`, `min(coverage) >= 0.50`). Measured components: **42 / 21 / 3 / 1**.

- **evaluation-reference subset** — the largest component (42), used only if a reference-side
  sequence is technically necessary to project the frozen frame;
- **challenge subset** — the remaining components (21 + 3 + 1 = 25), used for **no** UG5-side
  calibration or tuning of any kind.

Pairwise identity and bidirectional coverage between the two subsets are computed and landed
(`ug5_split_pairwise_audit.tsv`). Because they are unions of whole components, every cross-subset
pair is below the link rule by construction.

**This split is fixed here and is not revisited after results are visible.**

## 6 · Estimands, frozen before execution

| id | quantity |
|---|---|
| **A** | **anchor callability** — fraction of frozen shared anchors mappable to UG5 challenge sequences |
| **B** | **anchor ordering** — whether mapped anchors retain the construction-side order |
| **C** | **coordinate stability** — variation of mapped anchor coordinates across the held-out UG5 components |
| **D** | **ambiguity** — frequency of multiple competing mappings |
| **E** | **cross-family support** — score/support using only the frozen non-UG5 construction |
| **F** | **decoy separation** — the same mapping against valid shuffled controls |
| **G** | **challenge transfer** — performance on UG5 challenge components not used in any UG5 evaluation-side object |

**The permissive `hmmsearch` detection rate is NOT a primary success quantity.** It was already
shown `NON_DISCRIMINATING` and is reported only as a flagged diagnostic.

## 7 · Success criterion — qualitative, no post-hoc number

Success requires **all** of:

1. multiple frozen shared anchors map in UG5;
2. anchor order is coherent;
3. mappings are stable across held-out UG5 components;
4. signal separates clearly from valid decoys;
5. **no UG5-specific tuning** is required;
6. failure and ambiguity states are explicitly represented.

**Not** required: that every anchor transfers. A smaller transferable intersection is a valid
positive outcome.

No numeric threshold is invented after seeing results.

## 8 · Negative controls

Valid: **real-vs-shuffled**, and shuffled-vs-shuffled. **Reversing both homologous families is not
a valid negative** — mutual homology is preserved — and reversed-vs-reversed may **not** be counted
as evidence against the method. Any unrelated-real-protein negative would need its source and
rationale predeclared; none is used here.

## 9 · Language

Even on success: **"whole-family transfer demonstrated to UG5"**, never "transfer demonstrated to
all unseen RT families"; **"shared broad-RT core across tested lineages"**, never "universal RT
core".

## 10 · Audit principle

Every deviation, failed assertion, count mismatch or contradictory output is surfaced immediately
with `expected`, `observed`, `when_detected`, `scientific_effect`, `repair`,
`results_before_repair_invalidated`. A failed predeclared condition **fails closed**.
