# UG25 confirmatory result — one shot, all seven predeclared criteria

Executed 2026-09-17T14:05:41Z, once, under `control/UG25_PREDECLARATION_v2.md` of the frozen
pre-UG25 bundle (root `fc9cde03a13282b2aaa176a10b5da7c5798a4f2cce763dffad076575a8d2d889`,
verified INTACT immediately before execution).

Authorisation supplied at run time:
`RT07_AUTHORISED_FAMILIES=Retrons,GII,DGRs,CRISPR,UG3,AbiA,UG25`.

**No exploratory rerun. No threshold tuned. No criterion substituted. No alternate holdout.**

---

## 1 · Genealogy audit (mandatory precondition, run before any mapping)

| measure | value |
|---|---|
| exact sequence overlap with construction | **0** |
| exact overlap with GII | **0** |
| UG25 identifiers in construction | **0** |
| median best identity to construction | **0.588** |
| ≥0.30 on the identity leg alone | **28 of 28** |
| **meeting the FULL link rule** (identity ≥0.30 **and** min-coverage ≥0.50) | **0 of 28** |
| **classification** | **`FRESH_LINEAGE`** |

**The 0.588 figure must not be read alone, and this is the single most misreadable number in
the result.** Those best hits cover a **median 2.1%** of the sequence (max 6.7%) — short
high-identity patches, not sequence-level homology. Under the full link rule that defines
relatedness everywhere else in this project, **no UG25 sequence links to construction at all**.

For comparison, G2L — classified `FRESH_FAMILY_WITHIN_RELATED_LINEAGE` — had a *lower* median
identity (0.326) but met the full rule for **28 of 51**. UG25 meets it for **0 of 28**. UG25 is
genuinely the more independent holdout, and the identity number inverts that impression unless
coverage is quoted with it. Landed in `tables/ug25_identity_coverage_diagnostic.tsv`.

## 2 · Components

19 / 5 / 4. Qualifying (≥5): **component 0 (n=19)** and **component 1 (n=5)**. Component 2
(n=4) is descriptive only and takes no part in pass/fail.

## 3 · The seven criteria, each reported separately

| # | definition | observed | denominator | result |
|---|---|---|---|---|
| **C1** | every qualifying component median `MAPPED` fraction ≥ `T1` = 0.32 | comp0 **0.5133**, comp1 **0.5933** | 2 qualifying components | **PASS** |
| **C2** | all calls use the frozen posterior rule (`MAPPED` needs p ≥ `PP_HI`) | `PP_HI` 0.75, `PP_LO` 0.50 read from the frozen table at run time | 28 sequences | **PASS** |
| **C3** | among sequences whose `CAT_STATE`(262) call is exactly `MAPPED`, fraction beginning `[YF].DD` ≥ 0.80 | **26/27 = 0.9630** | 27 `CAT_STATE`-MAPPED sequences | **PASS** |
| **C4** | \|median difference between qualifying components\| ≤ `D_MAX` = 0.48 | **0.0800** | 2 qualifying components | **PASS** *(weak — see below)* |
| **C5** | every abstention reason from the closed vocabulary; all four call classes representable | reasons `{OK: 28}`; calls `{MAPPED 2400, AMBIGUOUS 375, UNSUPPORTED 297, DELETED_STATE 1128}` | 28 sequences | **PASS** |
| **C6** | per-class control separation and exact identity accounting | `PASS`, no violations | 252 control replicates | **PASS** |
| **C7** | no threshold changed after UG25 was opened | all parameters read from the frozen control tables at run time | n/a | **PASS** |

**7 PASS · 0 FAIL · 0 NOT TESTABLE.**

**C4 is weak by prior declaration and is not evidence.** The observed 0.0800 clears `D_MAX`
0.48 with enormous margin, but it also sits *above* the same-population null `D_RANDOM` = 0.067.
A C4 pass was declared close to uninformative before the run and is reported as such now.

## 4 · Call states — only `MAPPED` counted

| call state | anchor calls |
|---|---|
| **`MAPPED`** | **2400** *(the only positive evidence)* |
| `AMBIGUOUS` | 375 |
| `UNSUPPORTED` | 297 |
| `DELETED_STATE` | 1128 |

28 of 28 sequences returned `(MAPPED, OK)`. **No abstentions.** `AMBIGUOUS` and `UNSUPPORTED`
are reported and were never added to any success count.

## 5 · Catalytic — reported separately, never pooled with anchor callability

`CAT_STATE` = **262**, evaluated over the full 471-state range, not the 150 anchors.

| verdict | n |
|---|---|
| `CATALYTIC_CONFIRMED` | **26** |
| `CATALYTIC_SUBSTITUTED` | 1 |
| `CATALYTIC_STATE_DELETED` | 1 |

27 of 28 have `CAT_STATE` called `MAPPED`; of those, 26 begin `[YF].DD` → **0.9630**, against
the frozen floor 0.80. The frozen state-based rule was used throughout; multi-motif sequences
are resolved by state, never by motif-first matching.

## 6 · Controls — per class, never pooled away

| class | intended null | attempted | valid | failed | max | mean | p95 | ≥1 mapped | **distinct sequences** |
|---|---|---|---|---|---|---|---|---|---|
| MONO | composition preserved | 84 | 84 | 0 | 10 | 0.238 | 0 | 2 | 84 |
| DI | every dipeptide count preserved | 84 | 84 | 0 | 13 | 0.345 | 0 | 3 | 84 |
| **REV** | composition + local pair structure + length | 84 | 84 | 0 | **17** | 0.607 | 0 | 3 | **28** |
| POOLED | — | 252 | 252 | 0 | 17 | 0.397 | 0 | 8 | 196 |

Identity accounting reconciled exactly for every class: attempted = valid ∪ failed, disjoint.
**Zero di-shuffle generation failures on UG25.**

**Disclosure — the reverse control is deterministic.** `s[::-1]` returns the same sequence every
replicate, so REV's 84 replicates are **28 distinct sequences counted three times**. MONO and DI
are stochastic and give 84 distinct each. REV's nominal n therefore overstates its information
content, and `n_distinct_sequences` is landed in the control table so this cannot be read off
wrongly. REV is also the strongest control (max 17), consistent with construction.

**Separation:** the weakest real sequence maps **54** anchors (comp0 min 0.36 × 150); the
strongest control of any class maps **17**. No overlap.

## 7 · Disposition

**All seven predeclared criteria PASS on a `FRESH_LINEAGE` holdout.**

## 8 · Honest limits on what this supports

- **One holdout family, n=28.** Component 1 has only **5** sequences; its median carries wide
  uncertainty and was declared thin before the run.
- **Median callability is ~51–59%**, not near-complete: roughly half the frozen anchors are
  `DELETED_STATE` in UG25. The claim is that conserved states are *callable at rates well above
  T1 and far above every control*, not that the frame maps UG25 densely.
- **Controls are synthetic only** — order-disruption nulls. They establish separation from
  shuffled and reversed sequence, **not** general biological specificity against unrelated
  natural proteins.
- **Still `-M 50` / `-M 60` dependent.** Under `-M a2m`, DGRs and AbiA retain zero
  `ALL_PARTNERS` positions. Nothing here tests that.
- **No independent residue-level truth set.** Posterior stratification is the model's own
  confidence, not measured accuracy.
- **C4 is not evidence**, by prior declaration.
