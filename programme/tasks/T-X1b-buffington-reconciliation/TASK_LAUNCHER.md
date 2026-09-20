---
task_id: T-X1b-buffington-reconciliation
supersedes: T-X1-buffington-reconciliation (VOID, preserved exactly as executed, nothing inherited)
inherits_record_of: T-X1-buffington-reconciliation
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S00
title: Exact-sequence reconciliation of the Buffington 2025 catalogue, with the family join gated
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-X1b-buffington-reconciliation
branch: task/T-X1b-buffington-reconciliation
output_directory: analysis/t_x1b_buffington_reconciliation/
hard_dependencies: []
populations_touched: ["BUFFINGTON2025_RETRON_CATALOGUE :: EXTERNAL", "RT-EXACT-501561 :: READ-ONLY", "NCRNA-16458 :: READ-ONLY"]
population_state: EXTERNAL_COMPARISON_ONLY — merges nothing, spends no endpoint
confirmatory_spend: none
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — launcher, implementation and controls frozen in ONE commit BEFORE execution
operator_authorisation: |
  APPROVED 2026-09-20 as a NEW task identity after T-X1 went VOID.
  The correction is MINIMAL and is enumerated in §2. Every other constraint and
  control reviewed for T-X1 is preserved unchanged.
  Execute at <=2 threads while T-P1b continues, without contending for the heavy I/O lane.
---

# T-X1b · Buffington reconciliation, family join gated

✅ **FROZEN.** Launcher, implementation and controls entered git together, before any run.

⛔ **`T-X1` is VOID and nothing is inherited from it** — no table, no count, no threshold.
`T-X1`'s outputs are preserved exactly as executed and are not consumable. Record:
`programme/tasks/T-X1-buffington-reconciliation/VOID_01_family_join_defect.md`.

## 1 · Why this task exists

`T-X1`'s blocking control `X1_POS_populations_unchanged` expected **78,287** Retron sequences and
observed **0**. The cause was a positional fallback:

```python
fcol = "rt_family" if "rt_family" in cols else cols[1]      # ⛔ bound "family" to rt_aa_len
```

**The column is `family_label`.** The fallback turned *"the column I expected is absent"* — which
should stop a task — into *"use whatever is second"*, which produced a confident wrong number.

## 2 · The correction, and it is the whole of it

| # | change |
|---|---|
| 1 | bind **explicitly** to `family_label` (and `rt_seq_hash`), declared as module constants |
| 2 | ⛔ **every positional / fallback column selection deleted.** `load_retron_ids()` **raises** when a declared column is absent; the caller turns that into a blocking control failure |
| 3 | new **blocking pre-primary gate** `X1b_GATE_family_join_retron_count`: `family_label == "Retron"` must yield **exactly 78,287** |
| 4 | new **blocking gate** `X1b_GATE_family_vocabulary_size`: `family_label` holds **exactly 42** distinct values — recorded, not reconciled |

**Nothing else changes.** The Buffington reconciliation logic, both RT hashes, the orientation
handling, the engineered-construct exclusion, Axis B and all ten original controls are **unchanged
and were never implicated** — `T-X1`'s ten pre-run controls all passed.

## 3 · ⛔ The family vocabulary is recorded, not reconciled

| fact | value |
|---|---|
| `family_label` distinct values | **42** |
| `family_label == "Retron"` | **78,287** |
| top five | RVT-GII 256,624 · Retron 78,287 · RVT-DGRs 76,111 · RVT-UG2 8,423 · MULTI 7,593 |

⛔ **The historical registry name `RT-FAMILY-LABELS-613` does not describe this vocabulary.** The
origin and meaning of **613** are **unresolved** and appear to belong to a different
`type_set_norm` vocabulary in `rt_records_v1.parquet`.

**`T-X1b` does not consume, interpret, guess at or silently reconcile the 613.** It is out of scope
and recorded as backlog.

## 4 · Everything carried forward unchanged from the reviewed T-X1 design

- ⛔ **Coverage, not validation.** A published system absent from our catalogue is a **measured
  coverage gap in our resource**, not evidence the publication is wrong. A system present is **not**
  thereby experimentally validated.
- **Raw and stop-stripped RT hashes** are separate columns with separate summary counts.
- **Native msr-msd only** is matched. The engineered RFP repair-template construct is never matched,
  never pooled, never counted toward coverage.
- **Both ncRNA orientations** tested; which one matched is landed.
- **Axis B stays empty** unless traced to an identifiable experimental source; the blocking gate
  refuses any `TRACED` row without one.
- **Vap1 · Psp1 · Vro1 · Cko1 · Efe1 · Mva1** → `OPERATOR_NOMINATED_UNTRACED`, resolved by **exact**
  name match. **Eco1 → `NOT_IN_THIS_CATALOGUE`**, external to these 105.
- ⛔ **No compatibility or orthogonality inference.** Stage 12 stays closed.
- ⛔ **`PAIR-ELIG` is not reinterpreted as pairing evidence** — the pair list is read only for
  combination presence.
- **Merges nothing.** `X1_POS_populations_unchanged` re-counts every population after the run.

## 5 · Controls — **12 blocking, 12 PASS**

Ten inherited from the reviewed `T-X1` design, plus the two new gates:

| new control | expectation | observed | state |
|---|---|---|---|
| `X1b_GATE_family_join_retron_count` | `family_label == "Retron"` → **78,287** | **78287** | **PASS** |
| `X1b_GATE_family_vocabulary_size` | `family_label` → **42** distinct | **42** | **PASS** |

⛔ **These are the gates whose absence voided `T-X1`.** A wrong column now stops the task **before
the primary runs**, instead of surfacing as a `0` afterwards.

## 6 · Outputs, STOP conditions, interpretation ceiling

Unchanged from `T-X1`: `X1_row_classification.tsv` (105) · `X1_hashes.tsv` (105) ·
`X1_operator_nominations.tsv` (7) · `X1_summary.tsv` · `X1_controls.tsv` · `logs/run_log.json` ·
`OUTPUT_MANIFEST.sha256`.

**STOP on:** any input hash mismatch · ≠105 Buffington rows · catalogue counts ≠ 501,561 / 16,458 ·
**the family join not yielding exactly 78,287** · a population count changing after the run · a
`TRACED` row with an empty source · any blocking control failing.
