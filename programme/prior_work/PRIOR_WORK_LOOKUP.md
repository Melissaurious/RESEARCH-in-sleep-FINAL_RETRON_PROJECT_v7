# PRIOR_WORK_LOOKUP — what the estate already contains

**Run 2026-09-20, elapsed 1,451 s (24 min).** Instrument:
`programme/prior_work/prior_work_lookup.py` v2.0.0, driven by
`programme/prior_work/build_filelists.sh`. Results:
`PRIOR_WORK_LOOKUP.tsv` (per topic × root), `PRIOR_WORK_SUMMARY.tsv` (per topic),
`PRIOR_WORK_CONTROLS.tsv`, `PRIOR_WORK_META.json`.

> **A hit means material about this topic exists at this path. It does not mean the material is
> correct, reproducible or usable.** A hit can only move a topic **out of** `NOT_DONE`; it can never
> move one **into** `SCIENTIFICALLY_ADMISSIBLE`.

---

## 1 · Scope, and its declared blind spots

**17 registered roots · 707,902 files read in full · 24 topics · 3 substrates.**

| substrate | what | blind to |
|---|---|---|
| **content** | every file ≤ 2 MB, read in full: docs, scripts, small tables | anything that exists only inside a large table |
| **header** | first line of `.tsv`/`.csv` above 2 MB — recovers column semantics without reading GBs | row content |
| **dirname** | every directory path | anything not named |

The bound is declared so the blind spots are auditable rather than accidental. The estate is 115 GB
in one root alone; an unbounded sweep is not the "lookup of seconds" `TASK_PROTOCOL` step 2
describes, and would not finish.

## 2 · Controls — per substrate, per root, blocking that substrate only

| substrate | PASS | FAIL | NOT_EVALUABLE |
|---|---|---|---|
| content | **17 / 17** | 0 | 0 |
| dirname | **17 / 17** | 0 | 0 |
| header | 3 | **12** | 2 |

**Absence is reportable on `content` and `dirname`. It is NOT reportable on `header`**, which is
recorded `SUBSTRATE_BLOCKED` for 12 roots.

⚠️ **The header failures are a control-design fault, not a dead substrate.** The control term is
`/retron/i`, which is a plausible word in prose and a directory name and an **implausible column
name**. Headers hold `component_id`, `delta_logP_C1`, `n_alternatives_C3`. The right repair is a
substrate-appropriate control term. It was not re-run for it: the header substrate is marginal —
tens of files against 707,902 — and every absence claim in this programme rests on `content` and
`dirname`, both of which passed.

## 3 · ⛔ Version 1 of this instrument was dead, and its own control said PASS

**This is the finding worth keeping.**

v1 shelled out to `rg`. On this host `rg` is a **Claude Code shell function, not a binary**, so
`xargs` could not exec it and **every content search returned zero**. All 24 topics reported
`n_content_files = 0`.

**Every per-root control still reported `PASS`**, because it asked whether the known-present term
appeared in content **or** in directory names — and directory names still matched.

> **A control that aggregates across substrates cannot detect a dead substrate.**

Controls are now per substrate. No external search binary is used at all: one pass in process, every
topic regex tested against each file as it is read.

This is the **fourth** instance in this programme of a capability being present at the root and
absent in a spawned context — and the first where the instrument built to detect the pattern fell
to it. See `programme/CAPABILITY_STATE.md` §5.

## 4 · Three entries in the task register asserted absence from the dead instrument

They were written before the sweep was fixed, and are **corrected in
`programme/ALL_DOWNSTREAM_TASKS.tsv`**:

| task | said | actually |
|---|---|---|
| `T-F2-domain-architecture` | "terminal_fusion_architecture returned no prior-work hits" | **1,232 content files across 16 roots** |
| `T-R1-rtdna-direct-mapping-prep` | "rt_dna returned no prior-work hits" | **595 content files across 15 roots** |
| `T-I1-integrative-decomposition` | "integrative_model returned no prior-work hits" | **204 content files across 15 roots** |

All three are now `DONE_NEEDS_IDENTITY_CHECK`: material exists, identity unverified.

## 5 · Results, by topic

| topic | goals | roots | content files | dir names | reading |
|---|---|---|---|---|---|
| `annotation_disagreement` | 1,6 | 17 | **257,201** | 33,630 | the largest signal in the estate |
| `taxonomy_distribution` | 1,6 | 16 | 166,382 | 45 | concentrated in the January pipeline |
| `ncrna_boundaries` | 8,9 | 16 | 94,230 | **16,816** | directory-encoded, as expected |
| `yxdd_motif` | 4 | 16 | 93,605 | 1 | 87,067 in `RETRONS_january_2026` |
| `msr_msd` | 8,9 | 16 | 43,423 | 0 | |
| `palm_fingers_thumb` | 4 | 17 | 24,344 | 8 | ⚠️ the partition is a **settled negative** — material ≠ a usable definition |
| `genomic_neighbourhood` | 6 | 17 | 22,348 | 4 | |
| `rt0_rt7_families` | 1,2 | 16 | 17,203 | 213 | |
| `embeddings` | 10 | 17 | 7,584 | 15 | plus 42.4 GB of `.npy` in the asset sweep |
| `orthogonality_crosspair` | 12 | 16 | 2,317 | 2 | ⚠️ **zero measured cross-pair labels on disk** |
| `experimental_panel` | 12 | 16 | 2,317 | 1 | |
| `rt_tree_alignment` | 3 | 16 | 2,158 | 15 | ⚠️ 312 trees already ran; **bounded negative** |
| `evolutionary_correspondence` | 7 | 16 | 1,994 | 3 | |
| `database_characterization` | 1 | 14 | 1,996 | 149 | |
| `structure_prediction_assets` | 5 | 16 | 1,897 | 0 | |
| `diversity_saturation` | 1,3 | 17 | 1,777 | 9 | mmseqs tooling for `T-P1` |
| `rt_ncrna_pairing` | 10,11,12 | 17 | 1,770 | 1 | |
| `foldseek_structural` | 5 | 16 | 1,534 | 16 | |
| `terminal_fusion_architecture` | 4,6 | 16 | **1,232** | 0 | corrected, §4 |
| `rt_core_extraction` | 2,4 | 17 | 840 | 0 | |
| `rt_dna` | 9,12 | 15 | **595** | 0 | corrected, §4 |
| `a1_a2_annotation` | 9 | 15 | 292 | 0 | 95.83 % already a1/a2-called in a prior project |
| `integrative_model` | 11 | 15 | **204** | 0 | corrected, §4 |
| `lineage_patristic_correction` | 3,7,11 | 15 | 124 | 1 | **the thinnest topic**, and the one `T-A0b` needs |

**Every one of the 24 topics has material.** `NOT_DONE` now means *this specific analysis, as
specified, does not exist* — never *nobody has looked at this subject*.

## 6 · How a hit is used

Per `TASK_PROTOCOL` §3, unchanged:

| category | treatment |
|---|---|
| **assets** — structures, matrices, alignments, embeddings, profiles | reuse after hashing and registration |
| **bounded negatives** — refuted against a predeclared criterion with demonstrated power | inherit as a **design constraint**; do not re-run |
| **conclusions and numbers** | `[UNVERIFIED]`; re-derive before any citation |

**Take the files and the refutations. Leave the numbers.** Two topics carry the loudest warning:
`rt_tree_alignment`, where 312 trees and two independent reviews already established that the
phylogeny does not resolve at 157 alignable characters; and `palm_fingers_thumb`, where 24,344
content files coexist with a partition that is **not operationally defined in this project's parser
or in the literature**. Volume of prior material is not evidence that a question is answered.
