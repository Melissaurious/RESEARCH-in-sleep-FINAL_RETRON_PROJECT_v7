# UG5 whole-family holdout — transfer summary

Predeclaration: `control/ug5_holdout_predeclaration.md`, written before construction and before any
UG5 sequence was mapped. A NEW pre-`g4b` gate.

## The holdout is genuine

**24 of 24 construction inputs: `UG5_GENEALOGY_PRESENT = FALSE`.** Audited by scanning file
**content** for UG5 sequence ids *and* for the UG5 sequences themselves — not by filename. The gate
fails closed on any hit; it did not fire.

Construction: six families (`Retrons`, `GII`, `DGRs`, `CRISPR`, **`UG3` retained**, `AbiA`).
Frozen frame: **150 anchors** — positions aligned to all five partners — in `GII` coordinates,
span 107–317. Fixed before UG5 was touched.

UG5 split by whole separation components: **evaluation-reference 42**, **challenge 25**
(components of 21 + 3 + 1). Maximum cross-subset identity **0.3730**, and **zero** pairs violate the
link rule — that pair clears the 0.30 identity leg but fails the 0.50 bidirectional-coverage leg.

## Results against the frozen estimands

| id | quantity | result |
|---|---|---|
| **A** | anchor callability | **135 / 150 = 90.0%** on challenge; 148/150 = 98.7% on eval-reference |
| **B** | anchor ordering | **monotone YES** for every real target |
| **C** | coordinate stability | **54 anchors** map in every UG5 subset; **mean range 14.72**, max 16 positions |
| **D** | ambiguity | **0.0%** — no anchor shares a target position, in any target |
| **E** | cross-family support | hhalign probability **97.3** (challenge), **97.9** (eval-ref); E-values 2.7E-11, 5E-13 |
| **F** | decoy separation | shuffled challenge **0 / 150 anchors, prob 0.0**; shuffled eval-ref 11/150, prob 0.0 |
| **G** | challenge transfer | **90.0%** on components used in no UG5-side object |

The permissive `hmmsearch` detection rate is **not** used here; it was already shown
`NON_DISCRIMINATING`.

## Success criterion — all six met, with one stated limitation

1. multiple frozen anchors map — **YES**, 135 of 150;
2. anchor order coherent — **YES**, monotone;
3. stable across held-out components — **YES for coordinates, NOT uniform for callability** (below);
4. separates from valid decoys — **YES, decisively**: 135 vs 0 anchors mapped, probability 97.3 vs 0.0;
5. no UG5-specific tuning — **YES by construction**, and audited;
6. failure and ambiguity states represented — **YES**.

### The limitation, stated rather than buried

**Transfer is not uniform across UG5's internal structure.** The large held-out component
(`UG5_comp1`, 21 sequences) maps **135/150 = 90.0%** of anchors; the small one (`UG5_comp2`,
3 sequences) maps **54/150 = 36.0%**.

So the honest statement is two-part: **among anchors mappable in every subset (54), coordinates
agree to within ~15 positions**; but **which anchors are mappable varies substantially with the
UG5 sub-population**. The predeclaration anticipated this — *"a smaller transferable intersection
is a valid positive outcome"* — and 54 anchors is that smaller intersection.

## What this does and does not license

**Does:** *whole-family transfer demonstrated to UG5* — a shared coordinate structure derived with
no UG5 information maps to UG5 sequences in order, without ambiguity, and separates decisively from
valid decoys.

**Does not:** transfer demonstrated to all unseen RT families · a universal RT core · any
biological boundary claim · any statement about absence. One family was withheld, and UG5 is a
long, divergent UG family, not a random draw from RT diversity.

Language remains **"shared broad-RT core across tested lineages"**.
