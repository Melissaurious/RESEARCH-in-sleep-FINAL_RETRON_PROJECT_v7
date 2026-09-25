# Downstream decision note — what a within-retron-type compatibility experiment would require

**Feasibility audit only. Nothing was trained, no model outcome was inspected, no candidate set
was scored.** This note describes what *would* be needed; it does not propose running it.

## Why this design

`embed_g2` separated two levels of signal:

| level | statement | status |
|---|---|---|
| **1** | shared RT–ncRNA organization at retron-type / system-class level | **supported** |
| **2** | individual RT–ncRNA partner specificity within that organization | **not established** |

A within-type experiment is the design that could address level 2, because restricting
candidates to one retron type removes type-associated structure **by construction** rather than
relying on it being controlled away after the fact.

## Declared feasibility criteria (applied uniformly, not tuned)

`C1` usable candidate pool ≥ 50 unique ncRNAs of that type · `C2` ≥ 30 relatedness components ·
`C3` n_eff ≥ 10 · `C4` ≥ 100 T3 pairs. All four required.

## Per-type audit — full table in `tables/g2a_within_type_feasibility.tsv`

| retron type | pairs | uniq RT | uniq ncRNA | comps | **n_eff** | test comps | test n_eff | T3 | T4 | pool | species | feasible | blocking |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TypeIC1_IC2 | 6,277 | 6,139 | 2,034 | 144 | 1.2 | 42 | 9.2 | 5,319 | 2,012 | 2,004 | 1,129 | no | C3 |
| Ec107_like | 4,555 | 4,170 | 2,023 | 55 | 1.6 | 21 | 1.2 | 4,173 | 1,281 | 2,004 | 286 | no | C3 |
| OutgroupA | 4,359 | 4,302 | 3,319 | 230 | 1.6 | 82 | 20.1 | 3,597 | 964 | 3,315 | 858 | no | C3 |
| TypeIA_IIAI | 3,922 | 3,368 | 2,109 | 157 | 1.8 | 48 | 4.9 | 1,590 | 657 | 1,933 | 918 | no | C3 |
| TypeXIIIB_Ne144 | 2,096 | 2,046 | 1,534 | 41 | 1.7 | 13 | 6.8 | 1,778 | 346 | 1,532 | 631 | no | C3 |
| TypeIB2 | 1,462 | 1,332 | 320 | 46 | 3.8 | 16 | 2.9 | 1,372 | 508 | 272 | 151 | no | C3 |
| **TypeIIIA3** | 1,082 | 1,036 | 736 | 87 | **10.9** | 31 | 3.7 | 945 | 255 | 732 | 487 | **YES** | — |
| **TypeIB1** | 815 | 760 | 574 | 41 | **11.1** | 13 | 4.6 | 540 | 211 | 562 | 338 | **YES** | — |
| TypeXIIIA_firmi | 796 | 689 | 496 | 22 | 1.9 | 6 | 4.5 | 66 | 12 | 484 | 163 | no | C2, C3, C4 |
| TypeIV | 779 | 769 | 285 | 11 | 1.1 | 4 | 1.0 | 676 | 236 | 283 | 252 | no | C2, C3 |
| TypeV | 690 | 628 | 218 | 10 | 2.0 | 2 | 1.4 | 457 | 154 | 208 | 136 | no | C2, C3 |
| TypeIIIA2 | 635 | 610 | 408 | 53 | 3.2 | 19 | 4.0 | 479 | 152 | 405 | 277 | no | C3 |
| OutgroupB | 602 | 591 | 338 | 17 | 1.1 | 4 | 4.0 | 559 | 165 | 335 | 132 | no | C2, C3 |
| TypeIIIA1 | 586 | 571 | 439 | 46 | 3.3 | 17 | 2.2 | 322 | 67 | 437 | 267 | no | C3 |
| TypeXIIIC_Mx162 | 568 | 540 | 425 | 20 | 1.1 | 4 | 4.0 | 472 | 84 | 422 | 131 | no | C2, C3 |
| TypeIIA3_firmi | 460 | 438 | 260 | 20 | 2.4 | 3 | 1.0 | 442 | 138 | 257 | 140 | no | C2, C3 |
| TypeXIII_Mx65 | 455 | 452 | 388 | 28 | 2.1 | 12 | 5.5 | 280 | 49 | 386 | 172 | no | C2, C3 |
| TypeIIA3_proteo | 354 | 342 | 195 | 26 | 1.6 | 7 | 1.1 | 302 | 95 | 191 | 162 | no | C2, C3 |
| TypeIX | 279 | 274 | 233 | 38 | 2.6 | 13 | 2.0 | 252 | 74 | 230 | 184 | no | C3 |
| TypeIB2_firmi | 83 | 78 | 59 | 18 | 4.1 | 5 | 1.5 | 47 | 14 | 55 | 36 | no | C2, C3, C4 |
| TypeIIA2 | 69 | 64 | 65 | 22 | 3.0 | 8 | 3.9 | 12 | 2 | 61 | 26 | no | C2, C3, C4 |

## Which types have sufficient independent data

**Two of twenty-one: `TypeIIIA3` and `TypeIB1`.** Combined 1,897 pairs, 128 components,
1,485 T3, 466 T4.

**The blocking criterion for 19 of 21 types is `C3`, effective independent components.** Pair
counts look generous — `TypeIC1_IC2` has 6,277 pairs — but within a type those pairs concentrate
into a handful of relatedness components, so n_eff collapses to 1.1–4.1. Sample size at the
pair level is not sample size at the inference level.

## The caveat that matters most

Even the two feasible types are feasible **overall**, not **confirmatorily**. Under the frozen
split their *test-fold* effective component counts are **3.7** (`TypeIIIA3`) and **4.6**
(`TypeIB1`). A held-out within-type confirmatory readout at the current split would rest on
roughly four independent units — below what `embed_g2` already used (n_eff 14.1) and far below
what would make a null result interpretable.

So a within-type experiment on the current pair universe would be **descriptive at best**. To
make it confirmatory, one of the following would have to change first, and each is a separate
decision:

1. **more independent data within a type** — additional genomes/loci that add components, not
   just pairs (the corpus is already 1.54 M genomes, so this is not a cheap fix);
2. **a split rule re-derived per type**, accepting that the global frozen split is not
   optimised for within-type partition — this would be a *new* frozen split, not an edit to
   `embed_g2b`;
3. **a different estimand** that does not require held-out components, e.g. a within-component
   leave-one-partner-out design whose independence claim is explicitly weaker and stated as
   such;
4. **pooling types** into system classes, which reintroduces exactly the type-associated
   structure the design exists to remove.

## Recommendation

Do not launch a within-type partner-specificity experiment on the current universe expecting a
confirmatory answer. If level 2 is the scientific priority, the binding constraint is
**independent relatedness components within a retron type**, and that is a data-acquisition and
population-design problem, not a modelling problem. No higher-capacity pairing model should be
attempted until that constraint is addressed, because it would be evaluated against ~4
independent units.
