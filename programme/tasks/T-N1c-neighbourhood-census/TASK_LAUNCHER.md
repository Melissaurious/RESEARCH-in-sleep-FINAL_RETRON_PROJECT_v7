---
task_id: T-N1c-neighbourhood-census
supersedes: T-N1b-neighbourhood-census (VOID, blocking control failed, preserved as executed)
inherits_record_of: T-N1-neighbourhood-extraction-qa
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S06
title: CDS-neighbourhood census with a geometry-derived positional null
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_MEDIUM
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-N1c-neighbourhood-census
branch: task/T-N1c-neighbourhood-census
output_directory: analysis/t_n1c_neighbourhood_census/
hard_dependencies: []
populations_touched: ["RT-RECORDS-ALL-FAMILIES :: analysis_family=neighbourhood_geometry :: INSPECTED_FOR_THIS_ENDPOINT"]
population_state: INSPECTED_FOR_ENDPOINT (operator ruling 2026-09-20 §1)
confirmatory_spend: none
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b
---

# T-N1c · CDS-neighbourhood census, with a geometry-derived positional null

**T-N1b is `VOID` and preserved exactly as executed.** Its blocking negative,
`N1b_NEG_permuted_anchor`, returned **0.070506** against a declared ceiling of **0.05**. Per the
operator ruling §3 that is a STOP, and the threshold is **not** relaxed after seeing the number.
This is a new task with a **differently constructed null**, not a looser one.

## Why the N1b null was the wrong construction

N1b permuted anchors **across records**. CDS coordinates in this corpus are **contig-global**
(median `cds_start` 39,219; max 15,288,634), and many records derive from the same contigs and
genomes. A permuted anchor therefore lands in shared coordinate space often enough to overlap —
7.05 % of the time. **That is a real property of the data, not an instrument defect**, and it makes
cross-record permutation an ill-posed null.

## The replacement null, derived from geometry BEFORE the run

For each record, place a decoy interval of **the same length as that record's RT CDS**, uniformly at
random **inside that record's own window span** `[win_start, win_end]`. Ask how often the decoy
overlaps the true RT CDS.

**Expected rate from geometry**, declared here and not fitted:

> two intervals of length `L` placed in a window of span `W` overlap with probability ≈ `2L / W`.
> Median RT CDS ≈ 1.2 kb, median window span ≈ 19.2 kb (`win_start`/`win_end` medians 8,698 and
> 27,873) ⇒ **≈ 0.125**.

| declared parameter | value | basis |
|---|---|---|
| `NULL_MAX` | **0.25** | 2× the geometric expectation of 0.125 — loose on purpose, so the control tests the *construction* and not a tuned number |
| `DISCRIMINATION_MIN` | **0.50** | the true anchor must exceed the decoy null by at least this margin |
| anchor-uniqueness floor | 0.99 | structural, declared definitional |
| reproduction floor | 0.999 | against the landed `rt_cds_recovery_v1.n_cds` |

⚠️ **Both numbers are derived from interval geometry and stated before execution.** Neither is
chosen from an observed result. If the decoy rate exceeds 0.25 the task stops, and the correct
response is a different null again — not a higher ceiling.

## Controls — run FIRST, BLOCK, fixtures never touch the primary input

| control | type | must show | can it fail? |
|---|---|---|---|
| `N1c_NEG_random_position` | **negative** | a same-length decoy placed uniformly in the record's own window overlaps the true RT CDS at ≤ 0.25 | **yes** — it returned 0.07 under a different construction, and geometry could be worse than assumed |
| `N1c_POS_discrimination` | **positive** | true-anchor recovery **minus** decoy recovery ≥ 0.50 | **yes** — a position-blind locator scores both at 1.0 and the margin collapses to 0 |
| `N1c_POS_anchor_unique` | positive | exactly one `is_rt_gene` CDS per record, ≥ 0.99 | declared **definitional**; structural check only |
| `N1c_POS_reproduce_n_cds` | positive | reproduces landed `n_cds` on the 31,504 exception records, ≥ 0.999 | yes |

`N1c_NEG_random_position` and `N1c_POS_discrimination` fail in **opposite** directions.

## Everything else is unchanged from T-N1b

Zero-neighbour split into `EDGE_CLIPPED_ZERO` / `TRUE_ZERO_NEIGHBOUR` with the edge denominator
reported; clipping, window, contig-distance and locus keys landed; population declared
**`RT-RECORDS-ALL-FAMILIES`** with the row unit named a **raw source record, not an independent
locus**; `RETRON-LOCI` reserved for an actually retron-restricted population.

## What this task may NOT conclude

That a zero-neighbour record is genomically isolated. Anything comparative between retrons and other
RT families — that is `T-N2`, and neighbourhood is already a settled non-detector.
