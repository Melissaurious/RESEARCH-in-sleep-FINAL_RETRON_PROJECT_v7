---
record: BACKLOG_family_vocabularies
date: 2026-09-20
status: RECORDED, NOT A CURRENT-WAVE BLOCKER
rule: do not guess; do not silently reconcile
---

# Backlog — the RT family vocabularies do not agree, and 613 is unexplained

**Recorded because it was found while fixing something else, and parked because no task in the
current wave depends on resolving it.**

## What is verified

| vocabulary | file · column | distinct values | `Retron` count |
|---|---|---|---|
| **A** | `data/derived/rt_family_baseline_v1.parquet` · **`family_label`** | **42** | **78,287** |
| **B** | `data/derived/rt_records_v1.parquet` · `file_label` | **42** | not counted |
| **C** | `data/derived/rt_records_v1.parquet` · `type_set_norm` | **not counted** | not counted |

Vocabulary **A**, top five: RVT-GII 256,624 · **Retron 78,287** · RVT-DGRs 76,111 ·
RVT-UG2 8,423 · MULTI 7,593.

## What is not established

⛔ **Where 613 comes from.** `T-C1b` reported *"613 families"* and read `type_set_norm` from
`rt_records_v1.parquet` — vocabulary **C**. Neither **A** nor **B** has 613 values; both have 42.

⛔ **Whether A and B are the same 42**, or two different 42-value vocabularies that merely coincide
in size. **Not checked.** The coincidence is suggestive and is exactly the kind of thing that
should not be assumed.

⛔ **What relation C bears to A or B** — a finer stratification, a different axis, or something
else.

## Consequences already applied

- `programme/CANONICAL_DATASETS.tsv` → `RT-FAMILY-LABELS-613` **corrected**: the column is
  `family_label`, it holds **42** values, and the **613 in the dataset's own name does not describe
  it**. The id keeps its name for continuity only.
- `T-X1b` binds explicitly to `family_label`, gates on `Retron == 78,287` and on **42** distinct
  values, and **does not consume, interpret or reconcile 613**.
- `T-C1b`'s per-family table stands on vocabulary **C** as executed. ⚠️ **Its 613 families and
  `T-X1b`'s 42 are NOT the same axis and must never be presented in one table or one sentence
  without saying which is which.**

## ⛔ What must not happen

**Do not guess.** Do not rename one vocabulary to match another, do not assume A and B are
identical because both have 42 values, and do not quietly map C onto either. Any reconciliation is
its own task with its own evidence.

## When this becomes a blocker

Only when a task needs to **stratify by family across the two vocabularies at once**, or to quote a
family count as a project-level number. `T-P1c` will touch vocabulary **A** only, explicitly, and
is therefore not blocked.

**Nothing in the current wave is blocked by this.**
