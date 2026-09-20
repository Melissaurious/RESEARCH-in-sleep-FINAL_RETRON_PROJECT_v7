---
task_id: T-P1-relatedness-backbone
governance_base: 7e7ccd8
base_commit: 94a1a78
stage_id: S03a
title: Cascaded identity clustering of the exact-RT catalogue, including the 50% level
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_HIGH
preferred_backend: ibex
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-P1-relatedness-backbone
branch: task/T-P1-relatedness-backbone
output_directory: analysis/t_p1_relatedness_backbone/
hard_dependencies: []
soft_dependencies: ["T-C1-rt-core-extraction (cores improve it; full-length works)"]
populations_touched: ["RT-EXACT-501561: inspected"]
population_state: EXPLORATORY_POPULATION
confirmatory_spend: none
iteration_budget: 1
claim_ids_touched: []
io_class: IO_HIGH
frozen: true
---

# T-P1 · The relatedness backbone

**This is the trunk of the remaining programme, and it is a PREPARATION task.** Four separate
inference tasks take a `HARD_SCIENTIFIC_DEPENDENCY` on its output. **None of them depends on a
resolved topology**, which has been measured not to exist.

## Why it exists

T-A0 needed a lineage-level interval and could not compute one. The reason is structural, from
`A0_block_structure.tsv`: the 50 %-identity grouping available (`rt_rep`, 2,455 groups) sits
**strictly inside** the 1,075-component inference unit — `homolog_groups_nested_in_components` = 1.0,
every `rt_rep` in exactly one component. **A partition nested inside the resampling unit cannot
block over it**, so `homolog_block` degenerated to `n_blocks` = 1075 and reproduced the unclustered
interval exactly.

**A lineage partition that is not nested inside the component unit does not exist in this project.**
This task produces one.

## Question

What is the partition of the exact-RT catalogue at a declared ladder of sequence-identity
thresholds, and how does each level relate to the component and retron-type partitions already in
use?

## Hypothesis

Not applicable — this is a census of a partition, not a test. **There is no falsification criterion
because there is no claim.** The deliverable is a table of cluster assignments and a table
describing how each level cross-cuts the existing partitions.

## Population and inferential unit

- population: `RT-EXACT-501561`, the exact-RT catalogue, **501,561 exact RT sequences**
- unit: exact RT sequence; the **output** unit is a cluster at each declared level
- ⚠️ **exposure:** `RT-EXACT-501561` is `INSPECTED`, not exhausted. This task inspects it further
  and evaluates **no endpoint** on it. See §"Population note" below — there is an unresolved
  contradiction in the governing documents and it is the operator's to settle

## Declared threshold ladder — fixed here, before any run

**40 %, 50 %, 60 %, 70 %, 80 %, 90 %, 95 %** sequence identity, with coverage ≥ 0.8, bidirectional.

⚠️ **This ladder is declared in advance and may not be tuned.** 50 % is included because it is the
level `T-A0b` requires and the level the original review named. The others bracket it so the
sensitivity of any downstream blocking to the exact threshold is visible rather than assumed.
**Choosing a level afterwards because it gives a preferred downstream interval is forbidden**, and
is the failure this project already paid for twice.

## Inputs

| input | path | role |
|---|---|---|
| exact-RT catalogue | Stage-1 landed bundle; hash-pin before reading | the sequences |
| prior unique-RT FASTA | `/home/borg/RESEARCH-retron-db/data/derived/rt_unique_v1.faa` | **comparator only**, `[UNVERIFIED]`; re-derive, never cite |
| component/type partitions | `X2_COMPONENT_LEVEL_EXPORT.tsv`, `CROSSFIT_MANIFEST.tsv` | to compute cross-cutting, not to define clusters |

**Registry lookup performed:** `diversity_saturation` returns 1,777 content files across 17 roots
including MMseqs2 tooling (`programme/prior_work/PRIOR_WORK_SUMMARY.tsv`). **Reuse the tooling.
Re-derive every number.** No prior cluster count is inherited.

## Forbidden

Choosing a threshold after seeing a downstream interval. Treating any clustering as a phylogeny.
Emitting a tree. Citing a prior cluster count.

## Controls — run FIRST and BLOCK

| control | type | must show | if it fails |
|---|---|---|---|
| `P1_POS_known_identical` | **positive** | a seeded set of exact duplicates and a seeded set at a known, constructed identity land in the expected clusters at each level | the clusterer is not measuring identity; VOID |
| `P1_NEG_known_unrelated` | **negative** | seeded sequences below the lowest threshold do **not** cluster together at any level | the clusterer merges everything; VOID |
| `P1_POS_monotone_nesting` | **positive** | clusters at a higher identity are **contained in** clusters at a lower one, for every adjacent pair | the ladder is incoherent; VOID |
| `P1_MUT_battery` | **adversarial** | mutants — identity threshold ignored, coverage ignored, single-linkage chaining — are each caught by their **preregistered** catcher | the battery is non-discriminating; VOID |

⚠️ **Each mutant's catcher is named in this launcher, before the run.** If a mutant survives its
named catcher, the task **escalates**; it does not repoint the catcher. *(That instruction exists
because T-LINT2 did exactly that and was voided for it.)*

**Diagnostic, never blocking:** cluster-size distribution; singleton fraction; how each level
cross-cuts components and retron types.

## The deliverable that matters, and the one that decides T-A0b

`tables/P1_cross_cutting.tsv` must answer, per level, **the question that voided T-A0's lineage
arm**:

| quantity | why |
|---|---|
| clusters entirely inside one component | nested — useless as a block |
| clusters spanning ≥ 2 components | **cross-cutting — this is what makes a block possible** |
| components spanning ≥ 2 clusters | the converse |
| the partition's blocks, if used as a resampling block over components | the number `T-A0b` needs |

⛔ **If no level produces a partition that cross-cuts components, say so.** That is a **valid
negative** and it closes `T-A0b` with a bounded result rather than leaving it open forever. It is
`TASK_STATE=PASS`, `SCIENTIFIC_OUTCOME=BOUND`.

## Reachability

Both branches are reachable and both are reportable: a cross-cutting partition exists at some
level, or none does. Neither is a failure of the task.

## Pilot — MANDATORY before the full run

10,000 sequences, on Ibex, `--partition=batch`. **Declared expectation:** completes in under
20 minutes and all four controls pass. If the pilot's per-unit rate implies more than 8 hours for
501,561, **stop and report the projection** rather than queuing it.

## Compute

Ibex, `--account=pi-hohndor`, `--partition=batch`. Record job ID, software version, every input
hash, and the seed. ⚠️ **Submit over `rioszemm@ilogin.ibex.kaust.edu.sa` explicitly** — the `ibex`
alias resolves into the vscode pool on this host, which `general/site/IBEX.md` forbids for scripted
access.

## Outputs

`tables/P1_cluster_assignments.tsv` (one row per sequence per level),
`tables/P1_level_summary.tsv`, `tables/P1_cross_cutting.tsv`,
`tables/P1_controls.tsv`, `tables/P1_mutation_battery.tsv`, `TASK_REPORT.md`

## Population note — an unresolved contradiction, flagged not resolved

⚠️ **Two governing documents disagree about what inspection costs.**

- `WORKING_RULES` §3: *"A task that trains on, tunes against, or **merely inspects** a population
  makes that population unavailable for a later confirmatory claim."*
- `POPULATION_LEDGER.tsv`, `RT-EXACT-501561`: *"**Inspection is not consumption.** A confirmatory
  split could still be drawn here for a question that has never used it."* — and
  `can_serve_as_confirmation: YES for non-pairing endpoints`.

**Under either reading this task is safe**, because `RT-EXACT-501561` is *already* marked
`INSPECTED` by Stage 1 and Stage 2 g5: under the first reading it is already unavailable, and under
the second nothing is spent. The marginal cost is zero either way.

**But the contradiction itself is live and is the operator's to settle**, because it decides
whether a confirmatory split can ever be drawn from the exact-RT catalogue. It is on the operator
decision list. **This task does not settle it and does not act as though it were settled.**

## What this task may NOT conclude

Anything about evolution, relatedness as ancestry, or biology. **It produces a partition.** A
partition is not a phylogeny, and this project has already measured that the phylogeny does not
resolve: 312 trees, five preregistered routes, two independent reviews, 157 alignable characters
for retrons at 1.39 taxa per character. **Nothing here reopens that.**
