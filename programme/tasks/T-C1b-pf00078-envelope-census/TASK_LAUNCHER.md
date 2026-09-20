---
task_id: T-C1b-pf00078-envelope-census
supersedes: T-C1-rt-core-extraction (REVIEW_FAILED, preserved as executed)
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S02
title: PF00078 envelope census over the full exact-RT catalogue
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_MEDIUM
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-C1b-pf00078-envelope-census
branch: task/T-C1b-pf00078-envelope-census
output_directory: analysis/t_c1b_envelope_census/
hard_dependencies: []
populations_touched: ["RT-EXACT-501561 :: analysis_family=rt_profile_detection :: INSPECTED_FOR_THIS_ENDPOINT"]
population_state: INSPECTED_FOR_ENDPOINT (operator ruling 2026-09-20 §1)
confirmatory_spend: none — exploratory / asset construction / method development
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — this launcher and its implementation are committed BEFORE execution
---

# T-C1b · PF00078 envelope census

**This is a new task, not a patch.** `T-C1-rt-core-extraction` is `REVIEW_FAILED` and is preserved
exactly as executed. Its run is not overwritten, defended or re-labelled.

## What the review rejected, and what changes

| rejected | corrected here |
|---|---|
| called a **core asset** while writing `core_seq=None` in the full branch | the output is named an **envelope census**; `envelope_seq` is **populated**, and the word *core* is not used for it |
| **67,272 no-hit RTs omitted** from the table | **one row per RT, all 501,561**, each carrying `hit_state ∈ {HIT, NO_HIT}` |
| heterogeneity of the no-hits invisible | no-hit rate reported **overall and per RT family**, with length and eligibility strata |
| called `0.865875` a **"frame recovery rate"** | renamed **`pf00078_domain_call_fraction`**. Frame recovery is *not* demonstrated here and the term is not used |

> ⚠️ **Envelope detection is not core extraction.** A PF00078 envelope is where the profile aligns.
> An RT *core* is a structural/functional claim about boundaries. **They are different operations**,
> and conflating them is what this task exists to stop doing. Actual core extraction, if it is
> wanted, is a **separate downstream task** with its own criterion — it is not hidden inside this
> one's terminology.

## Question

For each of the 501,561 exact RT sequences, does the registered PF00078 profile call a domain at
the declared threshold, where does it align, and how does the call rate vary across RT families and
length/eligibility strata?

## Hypothesis

Not applicable — this is a census. There is no falsification criterion because there is no claim.
The deliverable is a complete per-sequence table plus its stratified rates.

## Population and exposure

- population: `RT-EXACT-501561`, all 501,561 exact RT sequences
- **analysis family:** `rt_profile_detection`
- **exposure:** `INSPECTED_FOR_THIS_ENDPOINT`. Under the operator ruling of 2026-09-20 §1 this
  permits exploratory work, QC, asset construction, method development and unrelated preregistered
  endpoints with no plausible leakage. It **forbids** later describing this population as untouched
  confirmatory evidence for profile-detection or RT-core-definition endpoints.

## Inputs

| input | path | role |
|---|---|---|
| exact-RT catalogue | `…_v7/data/derived/rt_exact_v1.faa` | 501,561 sequences |
| registered RVT profile | `…retron-db/data/derived/frame_rvt_v1.hmm` | PF00078.32, GA 29.6 |
| master record table | `…_v7/data/derived/rt_records_v1.parquet` | family label + frozen eligibility flags, joined on `rt_seq_hash` |
| curated panels | `panel_{truth,derivation,heldout}_v1.faa` | control fixtures only |

## Declared parameters, fixed in this commit

`--domE 1e-5` · panel positive floor **0.70** · shuffled-decoy ceiling **0.05** ·
completeness requirement **exactly 501,561 output rows** · seed **20260920**.

## Controls — run FIRST, BLOCK, and fixtures are SEPARATE from the primary input

⚠️ Per the operator ruling §3, **no control sequence is appended to the primary FASTA.** Controls
run on their own files, in their own hmmsearch invocations.

| control | type | must show | fails if |
|---|---|---|---|
| `C1b_POS_panel` | positive | curated panel RTs carry a PF00078 domain at ≥ 0.70 | the profile cannot find itself in known RTs |
| `C1b_NEG_shuffled` | negative | the same sequences, residue-shuffled at identical length and composition, call at ≤ 0.05 | the profile calls anything |
| `C1b_POS_completeness` | positive | the output has **exactly one row per input sequence, 501,561** | records are being silently dropped — the defect that failed T-C1 |
| `C1b_POS_input_identity` | positive | every input matches its recorded sha256 where one exists | the catalogue moved |

The first two fail in **opposite** directions: a call-everything profile fails the negative, a
call-nothing profile fails the positive. `C1b_POS_completeness` is new and directly targets the
omission the reviewer found.

## Outputs

`tables/C1b_envelopes.tsv` (501,561 rows), `tables/C1b_by_family.tsv`,
`tables/C1b_strata.tsv`, `tables/C1b_summary.tsv`, `tables/C1b_controls.tsv`,
`TASK_REPORT.md`, `logs/run_log.json`

## What this task may NOT conclude

That a domain call is an RT core. That a no-hit sequence is not an RT — it may be a fragment, a
divergent family, or a profile limitation, and the per-family rates are reported precisely so that
this stays visible. Anything comparative or biological.
