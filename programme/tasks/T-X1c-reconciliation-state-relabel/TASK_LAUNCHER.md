---
task_id: T-X1c-reconciliation-state-relabel
consumes: T-X1b-buffington-reconciliation (landed measurements only)
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S00
title: Relabel the X1b reconciliation into four mutually exclusive exact-presence states
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-X1c-reconciliation-state-relabel
branch: task/T-X1c-reconciliation-state-relabel
output_directory: analysis/t_x1c_reconciliation_state_relabel/
hard_dependencies: ["T-X1b landed X1_row_classification.tsv"]
populations_touched: []
population_state: NONE — no population is opened
confirmatory_spend: none
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — frozen in ONE commit BEFORE execution
operator_authorisation: |
  APPROVED 2026-09-20. X1b measurements accepted; EXTERNAL_NEW RETRACTED as an
  authoritative state label. Must NOT rerun sequence matching. Keep minimal and do
  not let it delay R2.
---

# T-X1c · reconciliation state relabel

✅ **FROZEN.** Launcher and implementation in one commit before the run.

## 1 · Why

`T-X1b`'s `overlap_class` used **`EXTERNAL_NEW` for two different situations** — *neither sequence
present* (43) and *the ncRNA is present but the RT is absent* (6). **The measurements were correct
and landed; the class name was not.** `overlap_class` is **RETRACTED as an authoritative state
label** and superseded here.

## 2 · ⛔ What this task must not do

**It does not rerun sequence matching.** It opens no FASTA, no parquet, no catalogue and no panel.
Its only input is `T-X1b`'s landed table, **pinned by sha256
`3a0b7fa73f789690b1bc383c1717c33c3354d82b5e8bb3715fc0ddd0977cc0ce`**. If it ever needed to hash a
sequence, it would be the wrong task.

## 3 · The authoritative reconciliation — a two-axis exact-presence matrix

| RT exact | native msr-msd exact | state | predeclared |
|---|---|---|---|
| 1 | 1 | `PAIR_EXACT_PRESENT` | **5** |
| 1 | 0 | `RT_ONLY_EXACT_PRESENT` | **51** |
| 0 | 1 | `NCRNA_ONLY_EXACT_PRESENT` | **6** |
| 0 | 0 | `NEITHER_EXACT_PRESENT` | **43** |

Axis totals: **exact RT present 56/105 · exact native msr-msd present 11/105 · exact pair 5/105.**

⛔ **`ncRNA = 0` means "no exact native-msr-msd sequence match in the project ncRNA catalogue".
It does NOT mean biological incompatibility**, and nothing produced here may be read that way.

## 4 · Controls — 8 blocking, all reproduced

Source sha256 (**asserts**, and a negative test confirms it fires) · 105 source rows · the four
states sum to 105 · **each of the four predeclared counts reproduced exactly** · both axis totals
carried through unchanged (56, 11).

⚠️ **An earlier draft of the hash gate passed unconditionally.** That is the defect class this
project keeps finding — *a gate that cannot fail is not a gate* — and it was corrected before the
freeze, with a negative test proving the corrected gate returns `VOID` on a wrong hash.

## 5 · Outputs

`X1c_reconciliation_states.tsv` (105 rows; carries the retracted `overlap_class` alongside for
traceability) · `X1c_state_counts.tsv` · `X1c_controls.tsv` · `logs/run_log.json`

## 6 · Interpretation ceiling

Unchanged from `T-X1b`: coverage of **our** resource against **one** published catalogue. Not
validation in either direction, no experimental activity, no compatibility or orthogonality
inference, nothing merged.
