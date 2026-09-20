---
task_id: T-A23c-source-retrieval
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S12
title: Bounded retrieval of the primary sources behind the cross-pair curation
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A23c-source-retrieval
branch: task/T-A23c-source-retrieval
output_directory: analysis/t_a23c_source_retrieval/
hard_dependencies: []
populations_touched: ["LIT-CROSSPAIR :: analysis_family=crosspair_evidence_geometry :: EXTERNAL"]
population_state: EXTERNAL — never a project population; consumes no biological population
confirmatory_spend: none
iteration_budget: 1
frozen: true
freeze_rule: WORKING_RULES §6b — launcher and implementation committed BEFORE execution
operator_authorisation: 2026-09-20 §8, bounded retrieval
---

# T-A23c · Bounded source retrieval

**Authorised by the operator, 2026-09-20 §8.** Runs concurrently with C1b/N1b because it consumes
no biological population.

## The load-bearing uncertainties this must resolve

Each is a question the A23 review left open, and each changes the **evidence geometry** rather than
adding rows for their own sake:

1. **Does the 7×7 heatmap caption mean every cell was actually assayed**, or does it describe a
   panel from which only some cells were measured? 42 of 56 curated rows rest on this one reading.
2. **Are the six non-functional rows six measured cross-pairs, or one RT-level statement expanded
   six times?** The review found they take their direction from a single sentence.
3. **The primary sources behind the review-derived rows** — SIM2019 refs 32, 33, 35, 36, currently
   counted as studies but read only through a review.
4. **The Mva1 cross-reactivity evidence.**
5. **The SIM2019-C2 swapped/chimera interpretation.**
6. **Any directly measured non-cognate RT–ncRNA pairing** needed to establish the actual geometry.

## Method

Europe PMC REST and NCBI E-utilities. Metadata for every named source; open-access full text where
the licence permits; recorded refusal where it does not. **No paywall circumvention**, and no
retrieval from sources whose terms forbid it — an unavailable source is recorded as unavailable,
which is itself a finding about the evidence base.

## Controls — run FIRST and BLOCK

| control | type | must show | fails if |
|---|---|---|---|
| `A23c_POS_known_record` | positive | a named, known-indexed article is retrieved with matching title/DOI | the retrieval path is dead and absence is unreportable |
| `A23c_NEG_nonsense_query` | negative | a constructed nonsense query returns **zero** results | the endpoint returns anything for anything |

Opposite directions: an endpoint returning everything fails the negative; a dead one fails the
positive.

## ⛔ Prohibitions

- **No unmeasured negative pair may be inferred.** Absence from a panel is not a measured
  non-functional outcome. This is the programme's standing rule and the single easiest error here.
- **No orthogonality modelling is opened** because additional rows were found. This task returns
  **source-level evidence and curation consequences**. Stage 12 stays shut.
- No numeric value is entered into the curation from a figure read by eye.

## Outputs

`tables/A23c_sources.tsv` (one row per named source: identifiers, availability, licence, what was
retrieved), `tables/A23c_uncertainties.tsv` (one row per §1–6 question: resolved / unresolved / what
the source actually says), `tables/A23c_curation_consequences.tsv`, `tables/A23c_controls.tsv`,
`TASK_REPORT.md`

## What this task may NOT conclude

Anything about orthogonality, compatibility or interchangeability. It establishes **what the
evidence is**, not what it means.
