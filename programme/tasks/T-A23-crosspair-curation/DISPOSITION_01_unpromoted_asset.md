---
disposition_id: T-A23-DISPOSITION-01
task_id: T-A23-crosspair-curation
task_artifact_commit: 98f3125
governance_base: b5443e1
date: 2026-09-20
kind: PRESERVE_UNPROMOTED
authority: review-stage/BATCH_ONE_INDEPENDENT_REVIEW_VERDICT.md (FAIL)
board_state: REVIEW_FAILED
stage_12_opened: false
---

# T-A23 · DISPOSITION 01 — curated evidence preserved, unpromoted; Stage 12 stays shut

The independent review returned **FAIL**. This disposition preserves what the curation produced,
refuses the count it was built to support, and records the redesign and retrieval that a future
task must perform. **No orthogonality or compatibility claim is promoted. Stage 12 is not opened
and is not auto-launched.**

---

## 1 · KEPT — the curation, as an unpromoted asset

| artifact | what it is | status |
|---|---|---|
| `A23_crosspair_matrix.tsv` | 71 curated rows (56 non-cognate, 15 cognate) with per-row provenance | **ASSET — unpromoted** |
| `A23_geometry.tsv` | the geometry of that evidence, which is the actually useful output | **ASSET — unpromoted** |
| `A23_source_provenance.tsv` | per-row source attribution | **ASSET — unpromoted** |
| `A23_corpus_screen.tsv` | 79 PDFs screened, 23 retron-relevant, 3 yielding rows | **ASSET — and the record of the scope error** |

Every one of the 56 non-cognate rows carries `provisional == TRUE` (`A23_geometry.tsv`,
`n_rows_provisional` = 56). The task flagged its own softness before any reviewer did, and that
self-report is why the asset is worth keeping.

## 2 · REFUSED — 56 as a measurement count

⛔ **56 is not a headline count and may not be cited as one.**

The review's arithmetic is in the task's own table. `A23_geometry.tsv` records
`largest_block_share` = **75.0 %** — 42 of the 56 rows are the single BUF2025 Fig. 1h matrix, one
study, one assay, one published panel. It also records `n_rows_with_numeric_value` = **0**, and
`n_no_direction_reported` = **34**, all of them cells of that same heat map.

**Blocks are the unit of evidence here, not cells.** A 7×7 panel expanded cell by cell under one
caption-reading decision yields 42 rows that are not 42 independent observations; they are one
experiment.

**The defensible statement of record:**

| quantity | value | source cell |
|---|---|---|
| experimental blocks | **7** | `A23_geometry.tsv`, `n_experimental_blocks` |
| non-cognate rows, all provisional | 56 | `n_noncognate_rows` |
| rows carrying a numeric value | **0** | `n_rows_with_numeric_value` |
| author lineages | 3 | `n_independent_research_groups` |
| source documents on disk yielding rows | **3** of 79 screened | `n_source_documents_on_disk` |

If a combination count is demanded, the strict primary-paper prose-named floor is **8**, of which
**6** are unconfounded on the RT–ncRNA axis. The six Efe1 direction labels come from one sentence
and are already inside the 42-cell panel; they are not six independently evidenced measurements.

## 3 · REFUSED — the positive control, because it is circular

`POS-a` made recovery of the disputed 42 cells simultaneously the control's pass condition **and**
most of the headline result. A control whose pass condition is the result is not a control.

> **This shape generalises and the programme should hunt it everywhere.** It is now written into
> `WORKING_RULES.md` §6a as a named prohibition rather than left as one task's finding.

## 4 · Four "primary studies" are not verified

`A23_geometry.tsv` `n_independent_studies` = 6, and its own basis field says so outright: *"BUF2025;
BOB2022; and 4 primary refs (32, 33, 35, 36) reported secondhand by the SIM2019 review."* **Four of
the six were read through a review, not from the primary artifact.** They are recorded as
`UNVERIFIED_SECONDHAND` and may not be counted as primary sources until the primary papers are on
disk and read.

## 5 · The scope error, repeated from the original review

The launcher said *published literature*. The task searched **79 PDFs already on disk**. No
systematic external search was performed, and no source data were retrieved. This is the same
narrowing that the independent scientific review found five times, and it is the reason the corpus
coverage is not systematic enough to support any denominator.

## 6 · REQUIRED redesign and retrieval, registered as tasks

| task | what it must do | why it is separate |
|---|---|---|
| **T-A23b-systematic-corpus** | a declared, reproducible external literature search with predeclared inclusion rules, a stated database and date, and a PRISMA-style count; report **blocks**, not cells | the present corpus is a convenience sample and no denominator exists without this |
| **T-A23c-source-data-retrieval** | obtain the supplementary/source data files that one source states accompany the paper; convert `design_only` rows to numeric | **the highest-yield action available** — it converts 34 of 56 rows from design-only to measured, and needs no experiment |
| **T-A23d-primary-verification** | obtain and read refs 32, 33, 35, 36 from the primary papers | four counted studies are presently secondhand |
| **T-A23e-block-level-recount** | recount on blocks with a predeclared expansion rule, and a **non-circular** positive control: a held-out published panel not used to build the rule | the current count depends on a reading decision made during curation |

**None of these opens Stage 12.** Stage 12's gate in `PROGRAM_LAUNCHER.md` §4 is
`measured_cross_pair_functional_labels >= <floor declared by T-A23>`. **No floor was declared**, and
the measured-label count is **0**. The gate is therefore not merely unmet — it is not yet
well-formed. Declaring that floor is an operator decision and is listed as such.

## 7 · Board consequence

`T-A23-crosspair-curation` stays `REVIEW_FAILED`. Its artifacts are preserved as unpromoted assets
under §1. **No orthogonality, compatibility or interchangeability claim exists or is proposed.**
`S12-orthogonality` stays closed. `T-A23b/c/d/e` are registered; whether any of them launches is
governed by the readiness class recorded for each in `ALL_DOWNSTREAM_TASKS.tsv`.
