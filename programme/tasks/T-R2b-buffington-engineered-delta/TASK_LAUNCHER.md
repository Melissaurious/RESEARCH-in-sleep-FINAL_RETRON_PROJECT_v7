---
task_id: T-R2b-buffington-engineered-delta
governance_base: 9a793c9
base_commit: SET_BY_AUTONOMOUS_PREPARE_FROM_CURRENT_PROJECT_SYNTHESIS
base_branch: project-synthesis
stage_id: S08
title: Buffington native-to-engineered msr-msd delta description
state: APPROVED_FOR_AUTONOMOUS_PREP
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-R2b-buffington-engineered-delta
branch: task/T-R2b-buffington-engineered-delta
output_directory: analysis/t_r2b_buffington_engineered_delta/
hard_dependencies: []
populations_touched: ["BUFFINGTON2025_RETRON_CATALOGUE :: EXTERNAL comparator only"]
population_state: EXTERNAL; no project-population spend
confirmatory_spend: none
iteration_budget: 1
frozen: false
freeze_rule: WORKING_RULES §6b
operator_authorisation: scientific design approved for autonomous implementation/freeze/execution; no further implementation-level review unless a genuinely new biological decision appears
---

# T-R2b · Buffington engineered delta

## 1 · Question

> For each of the 105 published Buffington catalogue systems, what sequence delta separates the putative native msr-msd from the published engineered msr-msd construct?

This task is independent of R2a validity. A failure here must not VOID or alter R2a.

## 2 · Evidence and interpretation ceiling

Input is only `BUFFINGTON2025_RETRON_CATALOGUE`, 105 rows, SHA-256 `d68366970378c05b5af9b00be886d76224a196a29b77171303f9353457cf4e62`.

The native sequence is bioinformatically identified/predicted material and the modified sequence is an engineered repair-template construct. Therefore the output label is **`ENGINEERED_DELTA` only**.

It may not be promoted to `msd`, `template`, `a1`, `a2`, natural boundary or experimental truth. It consumes no `NCRNA-16458` and no project ncRNA population.

## 3 · Global alignment — frozen policy

Use Biopython `Align.PairwiseAligner` in **global** mode with exactly:

- match score `+2`;
- mismatch score `-1`;
- gap-open score `-5`;
- gap-extension score `-1`.

The full native sequence and full engineered sequence are aligned; no local alignment and no end trimming.

### Equally optimal alignment ambiguity

The implementation must inspect equally optimal global alignments rather than silently taking the first alignment returned.

For every optimal alignment derive the engineered-delta event representation in native coordinates, preserving substitutions, insertions and deletions. Then:

- if all optimal alignments produce the same delta coordinates/events: state `UNIQUE_DELTA`;
- if equally optimal alignments produce different delta coordinates/events: state `AMBIGUOUS_DELTA`, retain the competing representations, and do not choose one by order;
- if the optimal-alignment multiplicity exceeds the implementation enumeration cap, state `AMBIGUOUS_DELTA` / `TOO_MANY_OPTIMA` rather than assuming coordinate uniqueness.

Enumeration cap is fixed before execution at **10,000 optimal alignments per pair**. Reaching the cap is an ambiguity outcome, not a reason to tune scoring.

## 4 · Blocking controls

- `R2b_GATE_catalogue_sha256`: exact registered source hash;
- `R2b_GATE_rows`: exactly 105 systems and unique `I.D.` key 105/105;
- `R2b_POS_single_insertion`: synthetic native/modified pair with one known 81-nt insertion recovers its exact insertion coordinates and sequence;
- `R2b_POS_sub_del_mix`: synthetic fixture containing a known substitution plus deletion preserves both event types separately;
- `R2b_NEG_identical`: identical pair yields empty delta, not a fabricated event;
- `R2b_POS_repetitive_ambiguity`: repetitive synthetic pair with multiple equally optimal placements yields `AMBIGUOUS_DELTA` and no arbitrary chosen coordinate;
- `R2b_GATE_no_tierD`: no read of `NCRNA-16458` / project ncRNA catalogue.

Any blocking control failure = STOP. Do not alter scores or ambiguity policy after seeing primary rows.

## 5 · Outputs

- `R2b_engineered_delta.tsv` — 105 rows with system ID, alignment state, event count, event representation, ambiguity state and source columns;
- `R2b_ambiguous_alignments.tsv` — competing delta representations for `AMBIGUOUS_DELTA` rows;
- `R2b_controls.tsv`;
- `logs/run_log.json`;
- `OUTPUT_MANIFEST.sha256`;
- `TASK_REPORT.md`.

## 6 · STOP conditions

Source hash/row/key mismatch; any blocking control failure; any arbitrary first-optimum tie break; any attempt to label `ENGINEERED_DELTA` as a natural msd/template/a1/a2 boundary; any read of Tier D; any post-result scoring change.

## 7 · Future integration

No integration/propagation is part of this task. Any R2c combining R2a/R2b or propagating toward Tier D is a separate future task requiring scientific review before freeze.
