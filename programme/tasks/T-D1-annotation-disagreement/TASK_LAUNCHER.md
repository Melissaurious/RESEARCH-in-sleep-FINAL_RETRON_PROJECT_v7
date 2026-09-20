---
task_id: T-D1-annotation-disagreement
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S01
title: Operational annotation-tool coverage and disagreement across RT records
state: DRAFT_AWAITING_FREEZE
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-D1-annotation-disagreement
branch: task/T-D1-annotation-disagreement
output_directory: analysis/t_d1_annotation_disagreement/
hard_dependencies: []
populations_touched: ["RT-RECORDS-3059700 :: analysis_family=annotation_agreement :: INSPECTED_FOR_THIS_ENDPOINT"]
population_state: INSPECTED_FOR_ENDPOINT — no confirmatory spend
confirmatory_spend: none
iteration_budget: 1
frozen: false
freeze_rule: WORKING_RULES §6b
operator_authorisation: |
  Autonomous-task rules, 2026-09-20. Ordinary implementation choices need no further
  approval. ESCALATE only for a new biological endpoint, a threshold chosen after
  inspecting primary results, an incompatible dataset status, a protected-population
  spend, or a claim beyond the approved scope.
  DO NOT EXECUTE while T-P1b holds the heavy I/O lane.
---

# T-D1 · annotation coverage and disagreement

## 1 · The question

> Where do the annotation tools disagree about what an RT record is, and is that disagreement
> structured by RT family or assembly source — or is it noise?

## 2 · ⛔ Interpretation ceiling

- **This is about ANNOTATION, not biology.** A disputed record is not thereby an unusual retron.
- ⛔ **Disagreement is NOT a quality score and must NOT be used to select a "high-confidence"
  subset.** Any such filter would silently define a population by tool concordance.
- ⛔ **Taxonomy is NOT used.** `T-D2` supplies that join; D1 does not anticipate it.
- Rows are **raw source records** and are **not independent** — `locus_key` and `rt_seq_hash` are
  landed so a consumer can collapse them.

## 3 · Population and inputs

`RT-RECORDS-3059700` via `data/derived/rt_tool_calls_v1.parquet` — **3,051,238 rows, 15 columns**,
carrying `by_myRT`, `by_PADLOC`, `by_DefenseFinder`, `n_tools`, `detected_by_set`,
`subtypes_{defensefinder,padloc,unclassifiable}`, `source_database`, `file_label`, `locus_key`,
`rt_seq_hash`.

⚠️ `rt_tool_calls_v1` has **3,051,238** rows against `rt_records_v1`'s **3,059,700**. The
**8,462-row difference is a denominator question D1 must resolve and report**, not paper over.

## 4 · ⛔ The first thing D1 must establish: can NOT_RUN be told from NO_CALL?

**A tool that never ran on a record is not a tool that ran and declined.** Conflating them would
inflate apparent disagreement.

D1 **first** measures, per `source_database` and `file_label`, whether tool coverage is uniform. If
the schema **cannot** separate `NOT_RUN` from `NO_CALL`, **that is the finding**, it is reported as
such, and every downstream rate is labelled `CALL_vs_NOCALL_OR_NOTRUN` rather than pretending to a
distinction the data does not support.

## 5 · Per-record classification, preserving each tool's original call

| class | meaning |
|---|---|
| `ALL_AGREE_CALL` | every tool with coverage called it |
| `ALL_AGREE_NOCALL` | every tool with coverage declined |
| `DISAGREE` | at least one called and at least one declined |
| `SINGLE_TOOL_ONLY` | exactly one tool had coverage |
| `NO_COVERAGE` | no tool had coverage |

⛔ **Each tool's original call is preserved in its own column.** `CLAUDE.md`: never pool
tool-specific fields whose provenance differs.

**Subtype disagreement is reported separately** from presence/absence disagreement —
`subtypes_padloc` vs `subtypes_defensefinder` is a different question from whether a record is an RT
at all.

## 6 · Views — record, and two collapsed sensitivity views

| view | unit | why |
|---|---|---|
| **record** | raw source record | the primary description |
| collapsed to `rt_seq_hash` | exact RT sequence | does disagreement track the sequence? |
| collapsed to `locus_key` | genomic locus | does it track the locus? |

Every rate carries its own denominator. ⛔ **The three are never mixed in one statistic.**

## 7 · Controls — blocking

| control | must show |
|---|---|
| `D1_GATE_input_sha256` | `rt_tool_calls_v1.parquet` matches its recorded hash |
| `D1_GATE_row_count` | exactly 3,051,238 rows |
| `D1_POS_reproduce_landed` | a landed Stage-1 `dbchar_g6` count is reproduced exactly |
| `D1_POS_synthetic_agree` | a fixture with two identical calls classifies `ALL_AGREE_CALL` |
| `D1_POS_synthetic_disagree` | a fixture with one call and one decline classifies `DISAGREE` |
| `D1_NEG_no_coverage` | a fixture with no tool coverage classifies `NO_COVERAGE`, **never** `ALL_AGREE_NOCALL` |
| `D1_POS_completeness` | every input row appears in exactly one class |

`D1_NEG_no_coverage` is the one that matters: it is the machine check on §4.

## 8 · Outputs

`D1_per_record.tsv` · `D1_coverage_by_source.tsv` · `D1_class_counts.tsv` ·
`D1_by_family.tsv` (`file_label`, with its vocabulary named) · `D1_subtype_disagreement.tsv` ·
`D1_collapsed_views.tsv` · `D1_controls.tsv` · `logs/run_log.json` · `OUTPUT_MANIFEST.sha256`

## 9 · STOP conditions

Input hash or row-count mismatch · any blocking control fails · a record would be dropped ·
**a "high-confidence subset" would be derived** — that is a new biological endpoint and escalates.

## 10 · Escalation triggers

A new biological endpoint · a threshold chosen after seeing primary results · an incompatible
dataset status · a protected-population spend · any claim beyond §1.
