# G2L held-out gate — transfer summary

Scope: **`FRESH_FAMILY_WITHIN_RELATED_LINEAGE`**. Mapper frozen before selection. One run, no tuning.

## Result against the frozen success criterion

| # | criterion | result |
|---|---|---|
| 1 | multiple frozen states callable in **both** non-trivial components | **MET** — comp0 (n=40) median **141/150 = 94.0%**; comp1 (n=9) median **126/150 = 84.0%** |
| 2 | mappings supported under the frozen rule | **MET** — actual `hmmalign` state path; 1 abstention, in a singleton component |
| 3 | catalytic landmark recovers | **NOT TESTABLE** — see below |
| 4 | mapping does not collapse to one component | **MET** — 94.0% vs 84.0%, both at or above the construction spread (0.713–0.953) |
| 5 | abstention and ambiguity explicit | **MET** — 1 `ABSTAIN` landed, per-state `MATCH`/`DELETE` landed for all 51 sequences |
| 6 | real separates from decoys | **MET, not absolute** — real median **141**, decoy median **0**; but **37 of 153** decoy replicates map ≥1 state, max **33/150 (22%)** |
| 7 | no G2L-specific tuning | **MET** by construction |

**5 met, 1 not testable, 0 failed.**

## Why criterion 3 is not testable

The catalytic dyad occupies **HMM state 262** in 27 of 30 GII construction sequences. State 262 is
inside the anchor span (107–317) but is **not one of the 150 frozen anchors** — the nearest is 267.

The anchors are `ALL_PARTNERS` positions, i.e. states aligned across **all six** construction
families; state 262 is not. So `catalytic_at_anchor = 0` everywhere is a property of the **anchor
set**, not of the mapper or of G2L. The mapper does map the dyad residue — it maps every state —
but there is no catalytic anchor to recover.

This is reported as **not testable**, not as pass or fail.

## Honest limits

- **Scope is a related family, not an unseen lineage.** Median G2L→GII-construction identity is
  **0.326**, with **48 of 51** sequences above the 0.30 link threshold and 2 at ≥0.50 (max 0.636).
  Zero contamination — 0 exact overlap, 0 ids in any construction object — but G2L is *group-II-like*
  and GII is in construction.
- **Decoys are not fully silent.** 24% of decoy replicates map at least one state, up to 22% of the
  frame. The separation is large in the median but the tail overlaps.
- **Order is not evidence.** `hmmalign` is globally colinear by construction; state order remains an
  `IMPLEMENTATION_INVARIANT` and is not claimed.
- One family was withheld. No universality, no distant-lineage claim.

## Supported claim

> The frozen state→residue mapping transfers to a **held-out RT family within a related GII-like
> lineage**, mapping a median **94%** (component 0) and **84%** (component 1) of 150 frozen
> conserved states to actual residues via the alignment path, with no family-specific tuning,
> against a decoy median of 0.
