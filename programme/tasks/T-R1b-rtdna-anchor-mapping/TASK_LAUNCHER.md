---
task_id: T-R1b-rtdna-anchor-mapping
supersedes: T-A5b1-rtdna-anchors and T-R1-rtdna-direct-mapping (D7 — they are the same task; this is the merge)
governance_base: 9a793c9
base_commit: 0a220e3
base_branch: project-synthesis
stage_id: S09
title: Direct coordinate mapping of measured RT-DNA onto its own retron ncRNA
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_SMALL
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-R1b-rtdna-anchor-mapping
branch: task/T-R1b-rtdna-anchor-mapping
output_directory: analysis/t_r1b_rtdna_anchor_mapping/
hard_dependencies: []
populations_touched: ["PANEL-RTDNA-81 :: analysis_family=rtdna_anchor_mapping :: CONFIRMATORY SPEND"]
population_state: NOT_YET_EXPOSED — this task spends it
confirmatory_spend: YES — one explicit operator authorisation required
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — launcher, implementation and controls frozen in ONE commit BEFORE execution
operator_authorisation: |
  APPROVED 2026-09-20.
  Scientific design approved; freeze + execute authorised.
  PANEL-RTDNA-81 spend AUTHORISED, one task, this one (D7 merge).
  Binding: EXACT/NEAR_EXACT/UNMAPPED stay separate; 0.90/0.90 is a PREDECLARED CONSERVATIVE RESCUE CRITERION, not a claim that 0.90 is a biologically optimal boundary; all equally valid placements reported; orientation ambiguity explicit; NO tie-breaking on biological expectation; NO general msr/msd boundary inference; NO machine learning.
  Max 2 CPU threads, no unrelated large I/O.
---

# T-R1b · RT-DNA anchor mapping

✅ **FROZEN.** Launcher, implementation and control specification entered git together, in one
commit, **before** any run — `WORKING_RULES` §6b. The run records that commit id.

⚠️ **0.90 / 0.90 is a predeclared CONSERVATIVE RESCUE criterion**, not a claim that 0.90 is a
biologically optimal boundary threshold. It exists to refuse a forced coordinate, nothing more.

## 1 · The question

> **Where does each empirically determined RT-DNA sequence map onto its own retron ncRNA?**

## 2 · ⛔ Interpretation ceiling

- **This is a lookup, not a model.** Exact substring search first; local alignment only where exact
  fails.
- ⛔ **No general msr/msd boundary is inferred here.** Generalising 81 anchors to the
  16,458-sequence ncRNA catalogue is a *different* task with a *different* evidence standard —
  `T-R2`, which does not yet exist.
- ⛔ **Not machine learning.** No training, no held-out split, no classifier.
- **n = 81 is the whole population.** Every statistic is a count, never a rate on a small base.
- A mapped anchor says where a measured molecule lies on its own ncRNA. It says nothing about any
  other retron.

## 3 · Population and the spend

| | |
|---|---|
| population | **`PANEL-RTDNA-81`** — the 81 panel elements with a measured `RTDNA_sequence` |
| unit | **one assayed retron element** |
| state | **`NOT_YET_EXPOSED`** — ⛔ **this task spends it** |
| authorisation | **one explicit operator authorisation**, per `WORKING_RULES` §4a |

⚠️ **This is the project's strongest anchor** — the functional outcome was never a training target
anywhere. `D7` is resolved by this launcher: **`T-A5b1` and `T-R1` are the same task and this is
the merge.** They must not both run.

✅ **`T-A22` is parked and no longer blocks this task.** The machine-enforced whitelist
(`A22_FEATURE_WHITELIST.tsv`, `A22_FEATURE_DENYLIST.tsv`, `a22_validate.py`, 17/17 self-tests)
preserves the option of that comparison later **without letting any R1b-derived feature leak into
it** — anchor, RT-DNA, msDNA and `r1b_*` columns are all permanently inadmissible there.

## 4 · Inputs

| input | path / hash | role |
|---|---|---|
| experimental panel | `…retron-db/…/inputs/support.csv`, `80b2f565…9577` | `RTDNA_sequence` + `ncRNA_sequence` |

**Schema verified at design time, not assumed:** 81/81 anchors carry **both** sequences; both are
uppercase `ACGT`; RT-DNA is 55–189 nt (median 91) and ncRNA 88–293 nt (median 167).

## 5 · Method — declared, fixed in this commit

For each of the 81, against **its own** ncRNA:

1. **Exact substring search, forward** — *every* occurrence, not the first.
2. **Exact substring search, reverse complement** — RT-DNA may be reported on either strand, so
   **both orientations are always tested and which one matched is landed**.
3. **Local alignment only if exact fails** — Biopython `PairwiseAligner`, `mode="local"`,
   match `+2`, mismatch `−3`, gap open `−5`, gap extend `−2`.
4. **Near-exact floor, declared in advance:** coverage ≥ **0.90** of the RT-DNA **and** identity
   ≥ **0.90**. ⛔ **Below either → `UNMAPPED`.** Never a forced low-quality coordinate.

### 5a · Mapping states — exact and near-exact reported separately

| state | meaning |
|---|---|
| `EXACT_UNIQUE` | exactly one exact placement |
| `EXACT_MULTIPLE` | several exact placements — ⛔ **all reported, no tie-break** |
| `NEAR_EXACT` | above the floor, with mismatches and gaps counted |
| `UNMAPPED` | below the floor, or no alignment — **a result, not a failure** |
| `INPUT_MISSING` | a required sequence is absent |

Orientation ∈ `FORWARD` · `REVCOMP` · `BOTH_AMBIGUOUS` · *(empty when unmapped)*.

⛔ **Exact and near-exact are never merged into "mapped".** They are different evidence.

> **The number of equally valid placements is itself a result.** There is no rule that picks one.

## 6 · Controls — **9 blocking, 9 PASS**, all synthetic, no panel sequence used

| control | type | expectation | observed | state |
|---|---|---|---|---|
| `R1b_GATE_panel_sha256` | positive | `80b2f565…9577` | match | **PASS** |
| `R1b_GATE_panel_rows` | positive | 175 rows / 81 anchors | 175 / 81 | **PASS** |
| `R1b_GATE_anchors_have_ncrna` | positive | all 81 carry an ncRNA | 81 | **PASS** |
| `R1b_POS_planted_exact` | positive | fragment planted at 41..130 found `EXACT_UNIQUE FORWARD 41..130` | exact | **PASS** |
| `R1b_POS_planted_revcomp` | positive | its revcomp found `REVCOMP` at the same span | exact | **PASS** |
| `R1b_POS_multiple_placements_reported` | positive | planted twice → `n=2`, **both** coordinate sets | `starts=41;171` | **PASS** |
| `R1b_NEG_unrelated_unmapped` | negative | an unrelated sequence of equal length is `UNMAPPED` | `cov=0.0778` | **PASS** |
| `R1b_POS_near_exact_detected` | positive | 3 planted substitutions → `NEAR_EXACT`, `n_mismatch=3` | `id=0.9667` | **PASS** |
| `R1b_NEG_partial_not_forced` | negative | 20 nt real + 90 nt random falls below the floor | `UNMAPPED cov=0.2364` | **PASS** |

**Positive and negative fail in opposite directions:** a map-everything procedure fails the two
negatives; a map-nothing procedure fails the four positives.

⚠️ **One defect these controls caught during drafting, recorded because it is the point of having
them.** `starts`/`ends` were a `';'`-joined **string** on the exact path and an **int** on the
near-exact path. A column that is sometimes int and sometimes str is a type trap for every
consumer. The implementation now emits strings on every path, and the invariant is a docstring.

### 6a · On the primary run

| control | blocking |
|---|---|
| `R1b_POS_every_anchor_reported` | **YES** — all 81 appear with an explicit state. ⛔ **An anchor is never dropped; `UNMAPPED` and `AMBIGUOUS` are states, not omissions** |

## 7 · Outputs

| file | contents |
|---|---|
| `R1b_anchor_coordinates.tsv` | **81 rows** — `mapping_state`, `orientation`, `n_placements`, `ncrna_start`, `ncrna_end`, `n_mismatch`, `n_gap`, `pct_identity`, `pct_coverage`, `align_score` |
| `R1b_ambiguous_and_unmapped.tsv` | the subset needing human attention, surfaced rather than buried |
| `R1b_summary.tsv` | counts by state and by orientation |
| `R1b_controls.tsv` | §6 |

**This is the experimentally anchored coordinate table `T-R2` will consume.**

## 8 · STOP conditions

| condition | action |
|---|---|
| panel sha256 mismatch | **STOP** before mapping |
| fewer than 81 anchors, or an anchor without its ncRNA | **STOP** |
| any blocking control fails | **STOP**, `VOID`, no primary table, escalate, **new task ID** |
| an anchor would be dropped | **STOP** — it must be reported with a state |

## 9 · What this task may NOT conclude

Any general msr/msd boundary. Anything about the 16,458-sequence ncRNA catalogue. Anything about
retron function, activity or orthogonality. Anything about a retron not in these 81.
