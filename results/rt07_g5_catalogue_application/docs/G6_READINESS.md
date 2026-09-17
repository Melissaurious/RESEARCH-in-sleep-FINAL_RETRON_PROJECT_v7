# g6 readiness — analysis readiness only. **No biology is inferred here.**

g6 is **not executed**. This document says what g6 *can* ask of the landed dataset, what
denominator each question has, and where the data will not support a comparison.

Everything below is **descriptive application QC**. None of it says a family lacks
architecture, that a short or unmapped protein is incomplete, or that a tool label is
correct. Those are g6 questions, and several of them this dataset cannot answer at all.

---

## 1 · Denominators, named once

| name | n | what it is |
|---|---|---|
| CATALOGUE | 501,561 | every Stage-1 exact RT |
| INELIGIBLE | 132,180 | censused out before mapping; retained in `g5_ineligible.parquet` |
| **ELIGIBLE** | **369,381** | the frozen g5 denominator — `G5_ELIGIBLE_N` |
| PROCESSED | 369,381 | produced a full scientific row. 0 tool failures, 0 invalid inputs |
| **INSPECTABLE** | **354,102** (0.9586 of ELIGIBLE) | frozen verdict `MAPPED` — the mapper committed |
| ABSTAINED | 15,279 (0.0414) | frozen abstention. **Not** failure, **not** absence |
| CAT-MAPPED | 356,229 (0.9644 of ELIGIBLE) | `CAT_STATE` 262 call is `MAPPED` — **separate** from the 150 anchors |

**A between-family comparison in g6 must use each family's own ELIGIBLE and INSPECTABLE
counts**, because both differ sharply by family — before the mapper ran (eligibility, see
`rt07_g5a_eligibility_census`) and after it ran (inspectability, below).

## 2 · Which families can support a robust comparison

`tables/g6_readiness_by_family.tsv` carries all 42. `READY` means ≥ 100 INSPECTABLE
sequences — a reporting triage threshold, not a scientific parameter, and it filters nothing.

| family | ELIGIBLE | INSPECTABLE | inspectable fraction | median MAPPED fraction (INSPECTABLE) | CAT-MAPPED |
|---|---|---|---|---|---|
| RVT-GII | 176,126 | 175,588 | 0.9969 | 0.9400 | 169,972 |
| **Retron** | **61,395** | **53,722** | 0.8750 | **0.4933** | 57,217 |
| RVT-DGRs | 59,487 | 58,975 | 0.9914 | 0.8267 | 58,590 |
| RVT-UG2 | 6,510 | 6,304 | 0.9684 | 0.3933 | 6,374 |
| RVT-UG8 | 6,264 | 6,015 | 0.9602 | 0.4800 | 6,030 |
| RVT-UG5 | 6,120 | **1,994** | **0.3258** | 0.3600 | 6,067 |
| RVT-AbiP2 | 5,665 | 5,623 | 0.9926 | 0.4667 | 5,606 |
| RVT-UG3 | 4,886 | 4,867 | 0.9961 | 0.5400 | 4,880 |
| RVT-CRISPR | 3,531 | 3,526 | 0.9986 | 0.9267 | 3,481 |
| RVT-CRISPR-like | 1,837 | 1,698 | 0.9243 | 0.7267 | 1,655 |
| MULTI | 2,824 | 2,584 | 0.9150 | 0.5133 | 2,500 |
| RVT-AbiA | 7 | 7 | 1.0000 | 0.5733 | 7 |

Coverage the operator asked for: **retron 61,395 eligible / 53,722 inspectable**;
**GII 176,126 / 175,588**; **DGR 59,487 / 58,975**; **AbiP2 5,665 / 5,623** (the separate
`RVT-AbiA` label is n=7 — see below); **CRISPR 3,531 / 3,526** plus CRISPR-like 1,837 / 1,698;
the **UG** families run from UG2 at 6,510 down to UG18 at 168, the smallest UG stratum —
**23 of the 42 families have fewer than 1,000 eligible sequences**. **MULTI is 2,824
eligible**, its own population, never folded into a single family.

`RVT-AbiA` is the only family with fewer than 10 eligible sequences (7 eligible, all 7
inspectable, all 7 CAT-MAPPED). It is `UNDERPOWERED_FOR_BETWEEN_FAMILY_COMPARISON` — which
is a statement about comparison, not about usability: those 7 sequences are fully described
in the dataset like any other.

## 3 · Strata where the instrument commits least often

`tables/g6_readiness_flagged_strata.tsv` — inspectable fraction more than 0.10 below the
run-wide 0.9586:

| family | ELIGIBLE | INSPECTABLE | fraction | vs run |
|---|---|---|---|---|
| RVT-UG24 | 839 | 190 | 0.2265 | −0.7321 |
| RVT-UG5 | 6,120 | 1,994 | 0.3258 | −0.6328 |
| RVT-UG6 | 318 | 130 | 0.4088 | −0.5498 |
| RVT-UG11 | 740 | 621 | 0.8392 | −0.1194 |
| RVT-UG16 | 528 | 443 | 0.8390 | −0.1196 |

A pattern worth carrying into g6 **as a question, not an answer**: RVT-UG5 is inspectable in
only 32.6 % of its eligible sequences, yet `CAT_STATE` 262 is MAPPED in **99.1 %** of them.
The two measurements have different denominators and are not pooled. Whether that reflects
biology, the GII-centred frame, or the `K_MIN` = 30 anchor floor is **not decided here**, and
the dataset alone cannot decide it.

## 4 · Per-state occupancy

`tables/g5_state_occupancy.tsv`, one row per frozen state, denominator ELIGIBLE. The 150
anchors are far from uniform:

| | state | MAPPED fraction |
|---|---|---|
| least mapped | 247 | 0.1899 |
| | 252 | 0.1928 |
| | 251 | 0.2023 |
| most mapped | 237 | 0.9425 |
| | 236 | 0.9424 |
| | 267 | 0.9391 |

g6 may describe this. It may **not** read a low-occupancy state as a region that families
lack: `DELETED_STATE` is a statement about the alignment path, and state 247 is `DELETED` in
257,675 of 369,381 eligible sequences — which is a property of this GII-derived profile on
this population, not an observation about protein content.

## 5 · Call-state distributions over ELIGIBLE

| quantity | p5 | p25 | median | p75 | p95 | mean |
|---|---|---|---|---|---|---|
| MAPPED fraction | 0.2533 | 0.5333 | 0.8267 | 0.9400 | 0.9933 | 0.7259 |
| AMBIGUOUS fraction | 0.0000 | 0.0000 | 0.0267 | 0.0733 | 0.1733 | 0.0485 |
| UNSUPPORTED fraction | 0.0000 | 0.0000 | 0.0133 | 0.0667 | 0.1867 | 0.0462 |
| DELETED_STATE fraction | 0.0000 | 0.0467 | 0.0733 | 0.2800 | 0.6267 | 0.1795 |

## 6 · Catalytic, on its own denominator

`CAT_STATE` 262 is **not** one of the 150 anchors and is never pooled with them.

| | n | denominator | fraction |
|---|---|---|---|
| `CAT_STATE` MAPPED | 356,229 | ELIGIBLE | 0.9644 |
| `CATALYTIC_CONFIRMED` | 343,880 | ELIGIBLE | 0.9310 |
| `CATALYTIC_CONFIRMED` | 343,880 | **CAT-MAPPED** | **0.9653** |
| `CATALYTIC_SUBSTITUTED` | 12,349 | ELIGIBLE | 0.0334 |
| `CATALYTIC_STATE_DELETED` | 11,995 | ELIGIBLE | 0.0325 |

"Confirmed" is **motif concordance at a state** — the residue at state 262 begins `[YF].DD`.
It is not independent residue truth, and g6 must not upgrade it into one.

## 7 · Tool strata — available, and constrained

`tables/g5_qc_by_tool_support.tsv`, keyed `myRT/PADLOC/DefenseFinder`:

| support | ELIGIBLE | INSPECTABLE | fraction | median MAPPED fraction |
|---|---|---|---|---|
| 1/0/0 | 323,580 | 314,034 | 0.9705 | 0.8800 |
| 1/1/1 | 19,106 | 18,628 | 0.9750 | 0.5000 |
| 1/0/1 | 11,954 | 10,011 | 0.8375 | 0.5067 |
| 1/1/0 | 8,807 | 8,717 | 0.9898 | 0.4600 |
| 0/1/0 | 3,225 | 770 | 0.2388 | 0.4800 |
| 0/0/1 | 1,556 | 833 | 0.5353 | 0.5067 |
| 0/1/1 | 1,153 | 1,109 | 0.9618 | 0.5067 |

**Binding constraint.** These are strata. g6 may say *"among sequences labelled family F by
MyRT, state S was MAPPED in X % of inspectable sequences."* g6 may **not** compute mapper
accuracy, sensitivity, specificity, precision, recall or ROC against any tool label, and may
not treat tool disagreement as mapper error. No independent truth for those estimands exists.

## 8 · Data-quality limitations g6 inherits

1. **The frame is GII-centred.** Median MAPPED fraction runs 0.94 (GII) to 0.49 (Retron) —
   the same gradient seen on construction data. It is a property of the instrument, and it
   is a confound for **every** between-family architecture comparison.
2. **Eligibility is not uniform.** 26.35 % of the catalogue never reached the mapper, and the
   loss is concentrated: `mixed_or_codon_evidence` 11.3 % eligible, MULTI 37.2 %,
   `all_partial` 57.4 %. Both filters — eligibility and inspectability — must be reported.
3. **`DELETED_STATE` ≠ absent region.** Alignment-path statement only.
4. **Abstention ≠ failure.** 15,279 sequences abstained under the frozen rule; 0 sequences
   failed technically.
5. **23 of 42 families have < 1,000 eligible sequences**, and one (`RVT-AbiA`, n=7) has
   fewer than 10. Under-powered strata must be reported as such rather than compared; they
   are still fully described in the dataset.
6. **Scope is `-M 50` only.** No `-M 60` or `-M a2m` claim, and no universal RT architecture,
   residue-level accuracy, or transfer claim beyond UG25 follows from this dataset.
7. **Historical RT0–RT7 remains `UNRESOLVED`.** States are `state_id`; no g5 output carries a
   historical label.

## 9 · Joins g6 will use

All keyed on `rt_hash`, all deterministic, all one-to-one unless stated:

```
g5_sequences.parquet   369,381  one row per eligible exact RT
g5_states.parquet   55,407,150  one row per RT x frozen state (150 each)
g5_catalytic.parquet   369,381  one row per RT, separate catalytic denominator
g5_ineligible.parquet  132,180  the excluded population, retained
g5_run_failures.parquet      0  no technical failure occurred
g5_metadata_crosswalk.parquet
                       501,561  rt_hash -> Stage-1 context, with in_g5_eligible
```

The crosswalk covers the **whole catalogue**, not just the eligible part, so g6 can compute
any denominator — including "of all Stage-1 RTs labelled F" — without re-deriving eligibility.
