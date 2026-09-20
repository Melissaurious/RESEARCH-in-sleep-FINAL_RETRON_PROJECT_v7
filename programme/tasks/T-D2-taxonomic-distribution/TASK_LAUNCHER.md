---
task_id: T-D2-taxonomic-distribution
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S01
title: Taxonomy join coverage and descriptive distribution of RT records
state: DRAFT_AWAITING_FREEZE
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-D2-taxonomic-distribution
branch: task/T-D2-taxonomic-distribution
output_directory: analysis/t_d2_taxonomic_distribution/
hard_dependencies: []
populations_touched: ["RT-RECORDS-3059700 :: analysis_family=taxonomic_occurrence :: INSPECTED_FOR_THIS_ENDPOINT"]
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

# T-D2 · taxonomy join coverage and distribution

## 1 · The question

> How much of the RT record set can be placed taxonomically at all, per taxonomy system — and, for
> the part that can, how is it distributed?

⛔ **Coverage first. The distribution is reported only for the part that joins, with its
denominator.**

## 2 · ⛔ Interpretation ceiling

- ⛔ **This describes the DATABASE, not the biosphere.** NCBI is dominated by clinically relevant
  taxa; a family looking "gut-associated" may be a sampling artefact.
- ⛔ **No prevalence, enrichment or abundance claim.** None is licensed without a declared sampling
  model, and D2 declares none.
- **Unit: taxonomic occurrence** — its own unit, distinct from raw record, locus and exact RT.
- ⛔ **Taxonomy systems are NEVER merged into one lineage string.** GTDB, NCBI, MGnify, UHGG and GEM
  are reported **separately**, each with its own coverage and its own denominator.
- **Missingness is a RESULT, not a filter.** Nothing is dropped for failing to join.

## 3 · Inputs

`rt_records_v1.parquet` (3,059,700 rows) for the join keys, and the registered metadata corpora in
`data/README.md`: `gtdb_bacteria_metadata.tsv.gz`, `gtdb_archaea_metadata.tsv.gz`,
`ncbi_bacteria_assembly_summary.txt`, `ncbi_archaea_assembly_summary.txt`,
`mgnify_{human_gut,marine,soil}_metadata.tsv`, `uhgg_v2.0.2_metadata.tsv`, `gem_metadata.tsv`.

⚠️ **Each is `RAW` trust.** `data/README.md`: *"Stage 1 must measure join coverage and missingness
before using any metadata field as a filter."* D2 is that measurement.

## 4 · Method

1. **Per system, per key**: attempt the join on its own identifier (`genome_id_norm`,
   `genome_asm_core`, accession), and record which key was used.
2. **Report coverage and missingness BEFORE any distribution** — joined, unjoined, ambiguous
   (multi-hit), per system.
3. Only then, for the joined subset, report the family × taxon table **at a declared rank**, with
   the joined denominator printed beside every cell.
4. **Isolate vs metagenome-bin provenance is retained**, never pooled — they carry different
   taxonomic confidence.

## 5 · Controls — blocking

| control | must show |
|---|---|
| `D2_GATE_input_sha256` | `rt_records_v1.parquet` matches `5466050…fb6f` |
| `D2_GATE_row_count` | exactly 3,059,700 rows |
| `D2_POS_known_join` | a record with a known assembly accession joins, and to the right row |
| `D2_NEG_fabricated_accession` | a fabricated accession **does not** join and is reported `UNJOINED`, **not dropped** |
| `D2_POS_denominator_conservation` | joined + unjoined + ambiguous == 3,059,700, per system |
| `D2_NEG_no_cross_system_merge` | a record joining in two systems yields **two rows**, never one merged lineage |

`D2_NEG_fabricated_accession` and `D2_POS_denominator_conservation` are the two that matter: together
they make silent shrinkage impossible.

## 6 · Outputs

`D2_join_coverage.tsv` (per system: joined / unjoined / ambiguous, with the key used) ·
`D2_missingness.tsv` · `D2_family_by_taxon.tsv` (per system, joined subset only, denominator on
every row) · `D2_provenance_split.tsv` (isolate vs metagenome bin) · `D2_controls.tsv` ·
`logs/run_log.json` · `OUTPUT_MANIFEST.sha256`

## 7 · The most likely outcome, declared in advance

**If coverage is low, that ceiling IS the result** — and a valuable one, because it bounds every
taxonomic claim the thesis can make, including the scope of goal 7. A low number here is **not** a
failed task.

## 8 · STOP conditions

Input hash or row-count mismatch · any blocking control fails · a denominator not conserved ·
**a taxonomy system merged into another** · any record dropped for failing to join.

## 9 · Escalation triggers

A new biological endpoint · a rank or threshold chosen after seeing primary results · an
incompatible dataset status · a protected-population spend · **any prevalence or enrichment claim**,
which is outside §1 by construction.
