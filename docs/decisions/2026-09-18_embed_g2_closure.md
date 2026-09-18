# Decision — `embed_g2` closed as a bounded negative for escalation

**Date:** 2026-09-18 · **Operator decision, recorded by the `embed` track.**
**Supersedes nothing. Superseded by nothing.**

## Decision

`embed_g2` is **CLOSED**. Escalation to partner-specific contrastive modelling
(`embed_g3`: InfoNCE, symmetric contrastive cosine, cross-attention or any higher-capacity
pairing model) is **NOT AUTHORISED** and was not attempted.

The launcher conditions `embed_g3` on `embed_g2` beating every trivial baseline on the held-out
split by the predeclared margin. It does not: at rung 3 (retron-type-controlled candidates) the
M-CCA advantage over the k-mer baseline is **+0.0298, 95 % CI [−0.0048, +0.0633]** — not
statistically distinguishable.

## What is established

> Frozen ESM-C and RiNALMo representations contain substantial shared structure associated with
> naturally occurring RT–ncRNA systems. This supports strong retrieval against random and
> length/GC-controlled candidate sets. However, the current experiment does not establish
> individual partner-specific compatibility beyond retron-type-associated structure: when
> candidate ncRNAs are restricted by retron type, the M-CCA improvement over the k-mer baseline
> is no longer statistically distinguishable.

Two levels were separated:

| level | statement | status |
|---|---|---|
| 1 | shared RT–ncRNA organization at retron-type / system-class level | **evidence for** |
| 2 | individual RT–ncRNA partner specificity within that organization | **not established** |

## What is explicitly NOT claimed

- **Not** that retron type has been *proven* to explain all observed signal. Rung 3 is an
  absence of a distinguishable difference, not a demonstration of equivalence.
- **Not** co-evolution, molecular binding, physical interaction or residue–nucleotide contact.
- **Not** a negative result at rungs 4–6. Those are **`UNDETERMINED`**: their candidate pools
  draw on 1, 10 and 22 independent relatedness components, too few for component-level
  confirmatory inference. Absence of measurement, not measured absence.
- **Not** generalization to evolutionarily unrelated RT or ncRNA sequences — the frozen
  interpretation from `embed_g2b`, unchanged.
- **Not** any per-pair inference: 4,638 test pairs carry n_eff = 14.1.

## Terminology binding on all downstream work

**observed / natural pair** · **mismatched candidate** · **retrieval decoy** ·
**non-observed pairing** · **type-matched decoy**. A mismatched candidate is **not** a
"negative pair" and **not** an "incompatible pair"; absence from the corpus is absence of
observation, not evidence of incompatibility.

## Immutable, carried forward unchanged

RT and ncRNA clustering thresholds and coverage rules · component membership ·
train/validation/test assignment · primary test population · near-duplicate sensitivity
population · component-level confirmatory inference · the frozen interpretation. None of these
were altered in response to model performance.

## Artefacts

| bundle | commit | content |
|---|---|---|
| `results/embed_g2b_frozen_split/` | `15e00b8` | binding split definition; verified reconstructible |
| `results/embed_g2_frozen_baseline/` | `2c9127b` | confirmatory retrieval result and stop-rule outcome |
| `results/embed_g2c_atlas/` | this commit | descriptive atlas, figures, within-type feasibility audit |

## Downstream

`results/embed_g2c_atlas/DOWNSTREAM_DECISION_NOTE.md`. The binding constraint on any future
within-retron-type partner-specificity experiment is **independent relatedness components
within a type**: only 2 of 21 types (`TypeIIIA3`, `TypeIB1`) meet the declared criteria, and
even those carry test-fold n_eff of 3.7 and 4.6. That is a data-acquisition and
population-design problem, not a modelling problem, and no higher-capacity pairing model should
be attempted until it is addressed.
