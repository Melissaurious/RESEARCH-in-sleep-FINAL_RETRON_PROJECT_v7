# LAUNCHER REVIEW PACKET

**For an independent adversarial reviewer.** Everything needed to stress-test the nine task
launchers is in this one file. Nothing here has been executed.

## Your task

Review each launcher below against the task protocol. For each, answer:

1. Is the question answerable as stated, with this population and this inferential unit?
2. Is the **declared PASS outcome reachable** from the declared inputs? Name any branch that cannot fire.
3. Are the **positive and negative controls the right ones**, and would each actually fail if the
   instrument were broken? A control that cannot fail is the failure mode under test.
4. Is the **falsification criterion** stated before the result, and does it bind?
5. Is anything **circular**: does the truth source derive from the instrument being tested?
6. Is the **effective sample size** honest, given the stated dependence structure?
7. Could an autonomous worker **turn a failed result into a downstream input** here?
8. Is the task **small enough to receive one defensible verdict**, or should it be split?
9. What is missing that the protocol requires?

Return a verdict per launcher: ACCEPT / ACCEPT_WITH_CHANGES / REJECT, with the specific change.

## Context you need

The review these launchers derive from is at
`review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` (19 sections). Five of its conclusions
were reversed during the review by discovering prior work outside the declared project, so treat any
"this has never been done" claim in a launcher with suspicion and say so if you see one.

## PROGRAM LAUNCHER

# PROGRAM LAUNCHER — retron RT/ncRNA programme

**Status:** ACTIVE from 2026-09-20 · **Coordinating session:** this repository, branch `project-synthesis`
**Evidence basis:** `review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` (17 sections)
**Per-task duties:** `review-stage/TASK_PROTOCOL.md` · **Execution rules:** `programme/WORKING_RULES.md`

> This launcher says **what the programme is trying to establish and how its parts depend on each
> other**. It does not contain methods. It is short on purpose.

---

## 1 · The question

> What sequence, structural and genomic features define retron reverse transcriptases within
> bacterial RT diversity; how are those features related to their ncRNA partners through evolution;
> and to what extent does that relationship determine functional RT–ncRNA specificity?

**Claim authority remains `idea-stage/docs/research_contract.md`.** This launcher schedules work; it
does not promote claims.

## 2 · What this programme has already established, and must not re-litigate

These are settled by evidence and are inputs, not open questions. Re-opening any of them requires new
evidence named in advance.

| settled | on what |
|---|---|
| bacterial RT phylogeny **does not resolve** at this character economy | 312 trees, five preregistered routes, two independent reviews; 157 alignable characters for retrons, 1.39 taxa/character; signal real at ~660× chance and insufficient to carry a topology |
| de novo comparative ncRNA **discovery** loses to a fixed positional interval — `CLOSED_CURRENT_DESIGN`, **REOPENABLE ONLY BY A NEW LAUNCHER** that predeclares: grouping independent of the old CM type labels, a materially different method or population, the fixed positional interval as a mandatory baseline, evaluation against published or experimental anchors rather than CM cuts, and explicit matched negative windows | 901 against 343 at IoU ≥ 0.5; per-type priors 969 |
| **placement** into the historical 11-clade system has no validated discriminator | shuffled queries confidently placed at 7.9% against a ≤1% limit |
| **re-inference** of the historical classification is not possible | the source alignment and extracts are not published and not on disk |
| neighbourhood is **not a retron detector** | retrons 27th of 41 families, inside a predeclared dead band |
| the three-way domain partition is **not operationally defined**, in this project's parser *and in the literature* | palm-like 0.565 against a 0.70 bar; literature fingers coincide 0/8; two 2026 papers publish incompatible partitions of the same protein |

## 3 · Stage graph

```
S00 CORRECTIONS · ASSET REGISTRATION · FREEZE          [open now]
      │
      ├── S01 RESOURCE + ANNOTATION LIMITS             [open now]
      │
      ├── S03a RELATEDNESS BACKBONE                    [the trunk]
      │        │
      │        ├── S04 RETRON RT FEATURES
      │        ├── S05 STRUCTURE (existing folds)
      │        ├── S06 GENOMIC ARCHITECTURE            [open now, architecture half]
      │        └── S07 ncRNA DISCOVERY, redesigned
      │
      ├── S03b RESOLVABILITY STUDY                     [optional branch, 1 arm]
      │        deliverable is the BOUND, not a tree
      │
      ├── S08 ncRNA INTERNAL ARCHITECTURE              [gated: prior-work audit]
      │        │
      │        └── S08b ARCHITECTURE-DEFINED PAIR EXPANSION
      │                 │
      │                 └── [lineage-count gate] ─── S09 ancestry-aware correspondence
                                    (gated; the word 'co-evolution' stays prohibited)
      │
      └── S10 EMBEDDINGS / PAIRING BOUNDS              [open now, repair tasks]
               │
               └── S11 INTEGRATIVE MODEL               [must be decomposed before it opens]
                        │
                        └── S12 ORTHOGONALITY          [conditional, see §5]
```

**S03a is the trunk, not S03b.** Downstream stages take a hard dependency on the relatedness
backbone, which is cheap and robust, and **no** dependency on a resolved topology, which has been
measured not to exist.

## 4 · Dependency types

```yaml
hard:         # the orchestrator enforces; a task may not start
  - S04 requires S03a
  - S07 requires S03a
  - S08b requires S08
  - S09 requires S03a AND S08b
soft:         # benefits from, must not block
  - S05 benefits_from S03a
  - S06_functional_identity benefits_from S03a
conditional:  # opens only on a measured count, declared in advance
  - S09 opens_only_if independent_lineages_with_paired_data >= <floor declared before S08b runs>
  - S11 opens_only_if decomposed_into_per_prior_increments_with_declared_floors
  - S12 opens_only_if measured_cross_pair_functional_labels >= <floor declared by T-A23>
```

## 5 · Forbidden shortcuts

Each is here because it has already happened or has been explicitly attempted.

- No claim of biochemical **compatibility, orthogonality or interchangeability** without measured
  cross-pair labels. Unobserved pairings are **never** negatives.
- No current claim may use the word **co-evolution**. S09 may test *ancestry-aware RT-ncRNA
  evolutionary correspondence* only if its predeclared lineage-count and independent-ncRNA-object
  gates are met. The word stays prohibited until a design explicitly separates shared ancestry and
  shared opportunity from correlated evolutionary change.
- No **per-pair biological inference** from a likelihood difference. A counterfactual is a
  conditioning control, not a negative pair.
- No **n × n compatibility matrix**, and no laboratory candidate nomination from a sequence score.
- No **gate label used as a biological conclusion**.
- No statement that something is **absent** without a registry lookup and a positive control.
- No **retron-versus-non-retron** claim evaluated on held-out family: there is only one retron family.
- No number in prose that does not resolve to a canonical table cell.

## 6 · Claim promotion

```
task outputs -> stage synthesis -> independent review -> claim promotion -> THESIS_ARTIFACT_BUILD
```

No task promotes its own claim, and **no task session writes interpretive thesis prose**. That would
contradict the facts-only reporting contract. Thesis artifacts are built at **stage** level from
promoted evidence only, and every figure and table carries `artifact_id`, `stage_id`, `claim_ids`,
`source_table`, `source_bundle`, `input_hash`, `generation_script`, `git_commit` and
`promotion_status`. Statuses are the single closed vocabulary in
`review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` §17 and the proposal's §12.

⚠️ **Nothing is promotable today.** `human_input_audit: DONE` appears nowhere in the repository
except the specification that defines it, and `BUNDLE_SPEC.md` makes it a precondition. This is an
operator decision, listed in §8.

## 7 · Autonomy tiers

| tier | covers | decided by |
|---|---|---|
| **A** fully autonomous | computation, validation, artifact generation, reporting a measured number with its unit and denominator | the task |
| **B** gated | status changes, opening a downstream stage, writing interpretation | task proposes, review disposes |
| **C** never autonomous | promoting a claim, changing a criterion, consuming a confirmatory population, waiving a control | the operator |

## 8 · Operator decisions this programme is waiting on

1. Accept withdrawal of the convergence claim.
2. Pre-commit to the verdict of the two cheap checks that decide the pairing paper.
3. How `human_input_audit` clears.
4. Whether the resource is released, and under what provenance.
5. The confirmatory-population freezing rule (Tier C; a task may not choose it).
6. **Back up the 88 MB Stage-1 workbench, which exists in no branch.**

## 9 · Completion

The programme is complete when: the resource paper is submittable with a released resource; the
pairing arm has reported its bound with absolute baselines and lineage-aware variance; the ncRNA
object exists or is closed with a bounded negative; the genomic architecture is described; and every
negative is preserved with its grade. **Orthogonality is not a completion condition.**

---

## WORKING RULES

# WORKING RULES — sessions, worktrees, parallelism, reporting

**Applies to every task session.** Read with `review-stage/TASK_PROTOCOL.md` (per-task duties) and
`programme/PROGRAM_LAUNCHER.md` (what the programme is for).

---

## 1 · Session model

| role | who | responsibilities |
|---|---|---|
| **coordinating session** | one, on `project-synthesis` | owns `TASK_BOARD.tsv`; authorises tasks; creates worktrees; receives reports; runs the consumption gate; never runs a scientific analysis itself |
| **task session** | one per task, in its own worktree | executes exactly one `TASK_LAUNCHER.md`; reports back in the §5 contract; terminates |
| **review session** | one per stage synthesis | model-disjoint where possible; read-only; returns a verdict |

**A task session does one task.** If it discovers a second question, it reports it as a *nomination*
and does not pursue it. Scope creep inside a task session is how a bounded analysis becomes an
unreviewable one.

## 2 · Worktrees

One worktree per task, named for the task, on its own branch.

```
path:   /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-<task-id>
branch: task/<task-id>
base:   main   (unless the launcher names a different base)
```

Rules:

- **The coordinating session creates and removes worktrees.** A task session never does.
- A task session writes **only** inside its own worktree, and inside it only to the paths its
  launcher declares under `output_directory`.
- **Never** write to `results/` of another worktree, to any frozen bundle, or to `general/`.
- ⛔ **Never use bare `git stash` / `git stash pop`.** The stash stack is shared across all worktrees
  and other sessions may be using it. Use a temporary WIP commit instead.
- A task branch merges nowhere automatically. Promotion is §6 of the program launcher.

## 3 · Parallel safety

Two tasks may run concurrently **only if all four hold**:

1. **No shared writes.** Their declared `output_directory` paths are disjoint.
2. **No unfinished-producer reads.** Neither reads an artifact that is not on a `TASK_STATE=PASS`
   task's declared `CONSUMABLE_OUTPUTS` list. Note this gates on **task validity**, never on
   scientific outcome: a refuted hypothesis still yields consumable outputs.
3. **No population collision.** They do not both touch the same confirmatory population. Every task
   declares `populations_touched`; the coordinating session refuses the second one.
4. **No criterion coupling.** Neither's threshold, bar or selection rule is chosen using the other's
   output. If one informs the other, they are sequential by definition.

> Rule 4 exists because a selection cutoff in this project landed exactly at the winner-flip point of
> its own sweep, and because a repaired gate passed on a rule class motivated by the failed
> attempt's results.

**Populations are a depleting budget.** `populations_touched` is recorded permanently. A task that
trains on, tunes against, or merely inspects a population makes that population unavailable for a
later confirmatory claim. The coordinating session enforces this and cannot unwind it.

## 4 · Compute

| class | backend | notes |
|---|---|---|
| `ZERO` | this session | reads landed tables, writes new tables. No job. |
| `CPU_SMALL` / `CPU_MEDIUM` | workstation | under ~4 h |
| `CPU_HIGH` / `MEMORY_HIGH` | Ibex, fallback workstation | checkpointable and resume-safe required |
| `GPU_*` | Ibex GPU, fallback workstation GPU | checkpointable required |

**A cheap pilot is mandatory before any Ibex-scale run.** Declare the pilot's size and its expected
result in the launcher. One acceptance criterion in this project had a ceiling of 84.8% against a
required 95% and was discovered only after the instrument was frozen; a pilot costs minutes.

**The method may not change because the backend changed.** Record backend, job ID, software version,
seed and all input hashes regardless of where it ran.

## 5 · The reporting contract

Every task session returns **exactly this**, and nothing else. Facts only. The task does not say what
its numbers mean.

> ⚠️ **Task validity and hypothesis truth are two different things and must never share a field.**
> A task that executes perfectly and refutes its own hypothesis is a **successful task with a
> negative result**. If that were reported as FAIL, the consumption gate in §3 would refuse to let
> anything downstream read it, and an autonomous orchestrator would quietly discard a valid negative.
> This project's negatives are among its best assets; losing one this way would be the worst failure
> the system could have.

**Two fields, always both:**

```
TASK_STATE:         PASS | STOP | INCONCLUSIVE | BLOCKED | VOID
SCIENTIFIC_OUTCOME: SUPPORTS_H1 | SUPPORTS_H0 | FALSIFIED | BOUND | DESCRIPTIVE | NOT_APPLICABLE
```

`VOID` is reserved for a task whose **execution** is not trustworthy, and it is the only state that
makes the result unusable. A task is VOID when a required positive control failed, preregistration
post-dates job start, a forbidden input was read, or the declared rule changed during execution.

A scientific negative is normally `TASK_STATE=PASS` with `SCIENTIFIC_OUTCOME=FALSIFIED` or `BOUND`.

```markdown
# TASK REPORT — <task-id>

TASK_STATE: PASS | STOP | INCONCLUSIVE | BLOCKED | VOID
SCIENTIFIC_OUTCOME: SUPPORTS_H1 | SUPPORTS_H0 | FALSIFIED | BOUND | DESCRIPTIVE | NOT_APPLICABLE
CRITERION: <the preregistered criterion, verbatim>
MET: yes | no | not evaluable — <one line>

## Consumable outputs
<explicit list of outputs downstream tasks may read. Only populated when TASK_STATE=PASS.
A VOID or BLOCKED task may still leave debugging artefacts; they are never consumable.>

## Numbers
| quantity | value | unit | denominator | interval |
(every row must correspond to a cell in a landed table; give the table path)

## Controls
| control | type | state | result |
(positive, negative, baseline — all must be PASS before the primary ran)

## Populations touched
<names, and whether trained on / tuned against / inspected>

## Outputs
<path, sha256, row count> for every declared output

## Provenance
preregistration commit + timestamp | job submission timestamp | software versions | seed | input hashes

## Iterations
<n used of n budgeted; what changed at each>

## Nominations
<questions discovered and NOT pursued>

## What this does not show
<the task's own honest limits, in the task's own words>
```

**Forbidden in a task report:** the words established, proves, confirms, demonstrates, validates,
significant (without the test and its assumptions), and any biological interpretation. A task
reports that a number is what it is.

## 6 · Definition of done, and escalation

A task is done when it is in a terminal state with all of §5 present, its preregistration commit
timestamp **preceding** its job submission timestamp, and every control in `PASS`.

**Escalate to the operator, do not iterate, when:** the iteration budget is exhausted; a control
fails; the declared PASS outcome is found unreachable; an input is missing or its hash does not
match; or the task would need to change its own criterion.

## 6a · What may serve as a blocking control

⚠️ **A biological contrast may not be a blocking control unless it is independently established.**

A control exists to show the **implementation** works. If a launcher says "effect X must remain
significant" and X is one of the quantities under study, then a procedure that weakens X is
indistinguishable from a broken instrument, and the task is pushed toward the expected biological
answer. That is the exact failure this project has already paid for twice, once with a threshold
fitted at the winner-flip point of its own sweep and once with a repaired gate whose rule class was
motivated by the failed attempt.

Admissible blocking controls, in order of preference:

1. **Implementation reproduction** — the new code reproduces an existing landed number exactly.
2. **Synthetic positive fixture** — a simulated dataset with a known effect under the declared
   dependence structure; the instrument must recover it at a declared coverage.
3. **Synthetic null fixture** — zero effect under the same structure; the instrument must contain
   zero at the declared rate.
4. **A named, independently established biological positive**, with the source cited in the launcher.
   Naming it is what makes it admissible; "two families known to share the core" is not named.

Everything else is a **diagnostic**, reported and never blocking.

## 7 · Standing prohibitions for every session

- No scientific analysis begins without an authorised launcher on the board.
- No number is written into prose that does not resolve to a canonical table cell.
- No absence is claimed without a registry lookup and a positive control.
- No frozen bundle is modified, ever. Corrections are errata.
- No criterion is edited. A changed criterion is a new task inheriting the old record.
- Prior work supplies **assets and bounded negatives**. Its numbers are `[UNVERIFIED]` and are
  re-derived before any citation.

---


---

## LAUNCHER · T-A0-lineage-variance

---
task_id: T-A0-lineage-variance
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S10
title: Lineage-clustered variance for the X2 decomposition
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A0-lineage-variance
branch: task/T-A0-lineage-variance
output_directory: analysis/t_a0_lineage_variance/
hard_dependencies: []
populations_touched: ["PAIR-ELIG: inspected (already exhausted by embed_x2 cross-fitting; no further depletion possible)"]
iteration_budget: 1
claim_ids_touched: ["C-27", "C-28"]
---

# T-A0 · Lineage-clustered variance for the X2 decomposition

## Question
What is the uncertainty on G−U, G−T, R−G and R−P when the resampling unit respects that 1,075
components sit inside 21 retron types and a smaller number of 50%-identity lineages?

## Hypothesis
The between-lineage variance component is large and currently excluded, so published intervals are
too narrow, most severely for R−G. Alternative: blocking changes little and the intervals stand.

## Why existing evidence does not answer it
Published intervals come from an **equal-weight bootstrap over components**. The bundle's own `n_eff`
column is a formula defect computing `n²/n = n` and reads 1075.0; the index package states 12.5,
which is a Kish figure over *pair* weights describing a different quantity. Neither is the effective
n of the estimator used. **Registry lookup:** no prior work on this; nothing in the asset sweep.

## Population and inferential unit
- population: all 1,075 components in the frozen X2 component export
- inferential unit: component (observation); retron type and RT homolog group (resampling blocks)
- **dependence structure:** components nest inside 21 dominant retron types; token-weighted effective
  type count is 9.3. Largest component holds 18.5% of pairs; 581 of 1,075 are singletons.
- effective n: **not a single scalar for this estimator**; see the reporting requirement below

## Inputs
| input | path | role |
|---|---|---|
| X2 component export (1,075 rows) | `…_v7-embeddings/results/embed_x2_rt_specificity_confirmation/tables/X2_COMPONENT_LEVEL_EXPORT.tsv` | the inference file |
| X2 strata table | same bundle, `tables/SENSITIVITY_STRATA.tsv` | per-stratum comparison |

Hash every input before reading; the bundle carries `HASHES.sha256`.

## Forbidden inputs
The pair-level export. Pair counts overstate sample size by three orders of magnitude and the
registry says never to infer from it.

## Controls — run FIRST and BLOCK

⚠️ **No biological contrast is a blocking control here.** An earlier draft required G−U to survive
blocking and P−T to lose it. Both are quantities under study. If G−U loses its interval under
correct cluster-aware inference, that may be the answer, and a control demanding otherwise would
push the variance procedure toward a preferred result. Per WORKING_RULES §6a:

| control | type | must show | if it fails |
|---|---|---|---|
| implementation reproduction | **positive** | the unclustered estimates and intervals reproduce the landed values exactly before any blocking is applied | the file is being read wrongly; VOID |
| synthetic hierarchical positive fixture | **positive** | a known non-zero effect simulated under the declared component-in-type structure is recovered at the declared coverage | the estimator cannot see an effect that is there; VOID |
| synthetic null fixture | **negative** | zero effect under the same structure contains zero at the declared rate | the intervals are miscalibrated; VOID |

**Diagnostics, reported and never blocking:** leave-one-type-out sensitivity for every type; the
direction and magnitude of each contrast under each blocking scheme.

## Effective sample size — report the structure, not one scalar

Do **not** declare a single effective n. Report: the number of type blocks; the number of
homolog-group blocks; component counts per block; the concentration of pairs and tokens across
blocks; and leave-one-block influence. If an effective-n approximation is given, name its formula
and say which estimator it approximates.

With only 21 type blocks, report **at least two** cluster-aware approaches, for example a block
bootstrap alongside a leave-one-type-out jackknife, rather than trusting one interval generator.

## Reachability
The PASS outcome is a set of intervals, which is attainable for any input. There is no unreachable
branch.

## Method
Block bootstrap over retron type; separately over RT homolog group; plus a leave-one-type-out
jackknife. Report all three beside the existing unclustered interval. Seed recorded.

## Endpoint and criterion
- primary endpoint: 95% interval on R−G under type-blocked resampling
- **falsification criterion:** if R−G's lineage-blocked interval includes zero, claim C-28 drops to
  UNDERPOWERED and the exact-RT residual leaves the claim set
- **death condition:** none; this task reports intervals either way

## Expected result patterns
| pattern | reading |
|---|---|
| G−U survives, R−G does not | the pairing arm becomes a lineage-dominance result |
| both survive | level 2 is genuinely established, and better supported than currently claimed |
| neither survives | the pairing paper is not viable; the arm becomes a methods-and-bounds chapter |

## Outputs
`tables/A0_blocked_intervals.tsv`, `tables/A0_jackknife.tsv`, `tables/A0_control_checks.tsv`

## What this task may NOT conclude
Anything about biology. It reports intervals. Whether the exact-RT residual is a claim is decided at
stage synthesis, and the operator has been asked to pre-commit to that verdict.

---

## LAUNCHER · T-A16-reciprocal-frame

---
task_id: T-A16-reciprocal-frame
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S02
title: Reciprocal family-frame analysis of RT core content
state: AWAITING_SPECIFICATION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A16-reciprocal-frame
branch: task/T-A16-reciprocal-frame
output_directory: analysis/t_a16_reciprocal_frame/
hard_dependencies: []
populations_touched: ["exact-RT catalogue: inspected"]
iteration_budget: 1
claim_ids_touched: ["C-04", "C-09"]
---

# T-A16 · Reciprocal family-frame analysis of RT core content

> ⚠️ **AWAITING_SPECIFICATION: name the two positive-control families and their evidence source; name the negative profile and build it by the same procedure; freeze a numerical asymmetry statistic and threshold before execution**

## Question
Is the low retron mapping fraction a property of retron domain content, or of the group-II-seeded
profile the mapper is built on?

## Hypothesis
Predominantly the profile. Alternative: retrons genuinely carry less of the conserved core, which
would make the operator's step-2 parenthetical a biological finding.

## Why existing evidence does not answer it
The one-directional gradient, median mapped fraction 0.94 for group II introns against 0.4933 for
retrons, is confounded by construction. **Registry lookup — and this is the point of the task:** a
reciprocal seven-family table already exists at
`results/rt07_g4a_repaired/tables/g4a_repaired_supported_intersection.tsv`. It shows retrons sharing
**39.2%** of covered positions with all partners against group II introns' **40.0%**, and only **3**
family-private positions out of 260. It was built to select anchor states, has no replicate, no
interval, and no per-sequence version. **It is an asset, not a conclusion.**

## Population and inferential unit
- population: the seven profile families in that table, extended to the full family set in the
  mapper's source sequence file
- inferential unit: profile position for the intersection; exact RT for any per-sequence extension

## Inputs
`results/rt07_g4a_repaired/tables/g4a_repaired_supported_intersection.tsv`;
`results/rt07_g4a_repaired/tables/g4a_repaired_family_selection.tsv`; the mapper's declared sole
sequence input; `results/rt07_g5_catalogue_application/tables/g5_qc_by_family.tsv`.

## Forbidden inputs
The g2 historical-reconstruction set, which was a **declared prohibited input** to the mapper
derivation. Do not reintroduce it.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| two families known to share the core | positive | high reciprocal mapping in both directions | the instrument cannot see sharing where it exists |
| a non-RT profile of similar length | negative | low mapping in both directions | the measure is not specific |
| the existing one-directional gradient | baseline | reproduced, and reported beside the symmetric result | — |

## Reachability
Both outcomes are attainable: symmetry and asymmetry are both measurable on this input.

## Method
Build each family's profile by the same procedure from the same source; compute pairwise reciprocal
mapping; correct for consensus length, which varies from 406 to 1014 across families.

## Endpoint and criterion
- primary endpoint: reciprocal mapping fraction per family pair, length-corrected
- **falsification criterion:** if retron-versus-partner mapping is asymmetric in the same direction
  and magnitude as the one-directional gradient after length correction, the domain-content reading
  survives; if symmetric, the gradient is a frame artefact and may be reported only as such
- **death condition:** a symmetric result permanently closes "retrons lack core domains"

## Expected result patterns
| pattern | reading |
|---|---|
| symmetric | the frame confound is confirmed and strengthened; a clean methodological result for the resource paper |
| asymmetric | a real claim about retron domain content, and a significant finding |

## Outputs
`tables/A16_reciprocal_mapping.tsv`, `tables/A16_length_corrected.tsv`, `tables/A16_controls.tsv`

## What this task may NOT conclude
Where a retron-discriminative signal is. That is T-A18, and it depends on this result.

---

## LAUNCHER · T-A23-crosspair-curation

---
task_id: T-A23-crosspair-curation
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S12
title: Literature curation of measured cross-pair outcomes
state: AUTHORIZED
autonomy_tier: B
compute_class: ZERO
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A23-crosspair-curation
branch: task/T-A23-crosspair-curation
output_directory: analysis/t_a23_crosspair_curation/
hard_dependencies: []
populations_touched: []
iteration_budget: 1
claim_ids_touched: ["C-30"]
---

# T-A23 · Literature curation of measured cross-pair outcomes

## Question
How many measured **non-cognate** RT–ncRNA outcomes exist in the published literature, and are there
enough to support any orthogonality endpoint?

## Why this is first in its stage, and why it is cheap
This determines whether stage 12 exists at all, and it is reading rather than compute. The project
register correctly records that no machine-readable swap data exists **in local assets**. That was
read as "no data exists", which is wrong. **Registry lookup:** text extraction over 61 retron PDFs
already on disk finds at least three published cross-pair designs, the largest being a **7 × 7
cognate-versus-non-cognate editing matrix with three biological replicates**, published as a figure
with values not on disk.

## Population and inferential unit
- population: retron engineering, variant-library and swap literature, including the PDFs on disk
- inferential unit: one measured RT × ncRNA combination under one assay

## Inputs
The PDF corpus identified by the asset sweep; any supplementary data recoverable from publishers.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| the three known designs | positive | all three are recovered by the curation procedure | the procedure misses known data and its count cannot be trusted |
| a paper with no cross-pair data | negative | yields zero rows, not spurious ones | the extraction invents rows |
| independent re-read of one paper | baseline | two readers agree on the row count | — |

## Reachability
Attainable; at least three designs are known to exist.

## Method
Build an `RT × ncRNA × assay × outcome × source` matrix. **The primary key must carry
cognate-versus-non-cognate**, because a failed *cognate* pair is a broken element and not an
orthogonality datum, while only a tested *non-cognate* combination is. Record whether each value came
from supplementary data, from text, or was read off a figure, and mark figure-read values as
provisional.

## Endpoint and criterion
- primary endpoint: the curated matrix **plus its geometry**, because a raw cell count misleads. One
  7x7 matrix yields 42 non-cognate cells from **7 RTs, 7 ncRNAs, one study, one assay context**,
  with correlated measurements. That is not 42 independent labels. Report `n_distinct_RTs`,
  `n_distinct_ncRNAs`, `n_retron_systems`, `n_independent_studies`, `n_assay_contexts`,
  `n_experimental_blocks`, `n_positive_cross_reactions`, `n_negative_cross_reactions`,
  `evolutionary_span`
- **falsification criterion:** none. This task curates; it does not judge model eligibility.
- **Stage 12 is NOT gated on a pair count.** Eligibility is a separate tier-B judgement (`T-A23b`)
  made on dataset **geometry and independent blocks**, choosing between descriptive evidence only,
  calibration and sanity checking, a low-capacity supervised endpoint, or no modelling. The rubric
  is declared before A23b runs.
- **death condition:** none; the matrix is valuable at any size

## Expected result patterns
| pattern | reading |
|---|---|
| tens of combinations recovered with values | enough to calibrate and sanity-check, not to train; stage 12 remains gated |
| designs found, values not obtainable | request supplementary data from authors; the panel decision moves up |
| far fewer than expected | the swap panel is the prerequisite and should be planned immediately, as it has the longest lead time in the programme |

## Outputs
`tables/A23_crosspair_matrix.tsv`, `tables/A23_source_provenance.tsv`, `tables/A23_controls.tsv`

## What this task may NOT conclude
That any combination is incompatible. An absent row is absent, never a negative. It also may not
treat a cognate failure as an orthogonality result.

---

## LAUNCHER · T-A2-ladder-population

---
task_id: T-A2-ladder-population
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S10
title: Counterfactual ladder on a fixed common population
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A2-ladder-population
branch: task/T-A2-ladder-population
output_directory: analysis/t_a2_ladder_population/
hard_dependencies: []
populations_touched: ["PAIR-ELIG: inspected (already exhausted)"]
iteration_budget: 1
claim_ids_touched: ["C-29", "C-39"]
---

# T-A2 · Counterfactual ladder on a fixed common population

## Question
Does the counterfactual effect decay monotonically as the control tightens, or does the reported
shape come from evaluating four tiers on four different component populations?

## Hypothesis
The shape is partly a population artefact. Alternative: the ladder is monotone on a fixed population
and the published description stands.

## Why existing evidence does not answer it
Tier populations are C1 1,019, C2 832, C3 1,073 and C4 **451** components, and C4 contains **zero**
of the 581 singleton components, so it is structurally the large-component subset. The published
"~10-fold decay" compares non-identical sets. **Registry lookup:** none.

## Population and inferential unit
- population: the components present in **all four** tiers (expected ≈ 423), with full-population
  figures retained alongside
- inferential unit: component, primary. The pair-weighted view is a **descriptive sensitivity**, reported beside it and never primary
- dependence structure: as T-A0

## Inputs
X2 component export; `tables/COUNTERFACTUAL_EFFECTS.tsv` from the same bundle.

## Forbidden inputs
The pair-level export as an inference file.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| full-population ladder | baseline | reproduces the published C1–C4 values exactly | the reader is wrong; stop |
| tier membership counts | positive | reproduces 1,019 / 832 / 1,073 / 451 | stop |
| singletons in C4 | **structural sanity check** | is zero, confirming the tier is the large-component subset | the population claim is wrong; VOID |

## Reachability
Attainable for any input.

## Method
Intersect tier memberships; recompute each tier's component-level and pair-weighted mean on the
common set; report both alongside the full-population values.

## Endpoint and criterion
- primary endpoint: the four tier means on the common population
- **falsification criterion:** if the common-population ladder is monotone, the published wording
  stands and this task reports `TASK_STATE=PASS` with `SCIENTIFIC_OUTCOME=FALSIFIED`.
  A refuted hypothesis is a **successful task**, never a failed one
- **death condition:** none

## Expected result patterns
| pattern | reading |
|---|---|
| non-monotone, collapse at C3 | PASS / SUPPORTS_H1. Near-neighbour counterfactuals abolish the effect; C4 is a different population, not a tighter control |
| monotone | PASS / FALSIFIED. The published description is correct and this objection is withdrawn |

## Outputs
`tables/A2_common_population_ladder.tsv`, `tables/A2_tier_membership.tsv`

## What this task may NOT conclude
Whether pair-level discrimination exists. It describes the shape of an existing measurement.

---

## LAUNCHER · T-A3a-rule-and-e0-freeze

---
task_id: T-A3a-rule-and-e0-freeze
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S00
title: Freeze the confirmatory rule and the exposure set E0
state: AWAITING_ADOPTION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A3-confirmatory-population
branch: task/T-A3-confirmatory-population
output_directory: analysis/t_a3a_rule_and_e0_freeze/
hard_dependencies: []
populations_touched: ["defines E0; touches no endpoint and assigns no candidate population"]
iteration_budget: 1
claim_ids_touched: []
---

# T-A3a · Freeze the confirmatory rule and the exposure set E0

**Supersedes the withdrawn `T-A3`, which asked to assign "any future pairing population" and was
therefore not a bounded, reproducible task.** That launcher is split: this one freezes the rule and
the exposure set, which can run today. A separate `T-A3b-<population-name>` instantiates the rule on
one named, hash-pinned candidate population, and is written when such a population exists.

## Why this is a task and not a decision
The **rule** is tier C: the operator adopts it once. **Executing** it is tier A and fully
deterministic. Once adopted, this task needs no human ever again and reproduces byte-identically.

## Question
What exactly is the exposure set E0, and what is the frozen, machine-checkable rule by which any
future candidate pairing population will be split?

## THE RULE — frozen text, applied verbatim, never re-derived

1. **E0, the exposure set.** Every sequence used by the retrieval gate, X1 or X2 during model
   development is E0. **No member of E0 may ever be called untouched confirmation of those
   analyses.** X2 cross-fitted all five folds, so all of PAIR-ELIG is in E0.
2. **Leakage components.** Candidate pairs are grouped by sequence-only edges:
   - RT edge at **>= 50% amino-acid identity over >= 80% coverage**;
   - ncRNA edge at **>= 80% nucleotide identity over >= 80% coverage**;
   - exact duplicates and copies of the same biological pair are always connected.
3. **Assignment, exactly specified.** Deterministic and component-level. Compute
   `h = SHA256(component_id + "PAIR_CONFIRMATORY_V1_2026-09-20")`, take the first 8 bytes as a
   big-endian unsigned integer `u`, and assign `CONFIRMATORY` if and only if
   `u < floor(0.20 * 2**64)`, otherwise `DEVELOPMENT`. No rounding to "approximately 20%", no RNG,
   no reseeding. `component_id` is the sorted, newline-joined list of member pair identifiers, hashed;
   its construction is frozen by this task and emitted as code.
4. **Ordering.** Assignment happens **before** any model score, endpoint or component composition is
   inspected. No rebalancing after inspection, ever.
5. **Near and far, with distances.** Report `CONFIRMATORY_NEAR` and `CONFIRMATORY_FAR` separately.
   **FAR** means no RT edge **and** no ncRNA edge to any member of E0 *under the declared thresholds*.
   ⚠️ FAR is **not** biological independence. Remote homology below the thresholds remains. Always
   report the **continuous nearest-neighbour identity and distance to E0** for every component, on
   both modalities, alongside the categorical label.
6. **Sealing.** Once frozen, confirmatory components may not influence feature selection,
   architecture, thresholds, stopping rules, hyperparameters or error analysis. They are opened
   **once**, after the relevant analysis is frozen.
7. **Honesty clause.** If no adequate prospective population exists, the follow-up is reported as
   **lacking confirmatory evidence**. An untouched set is never manufactured retrospectively.
8. **The FAR adequacy criterion.** The operator declares, **with the rule and before any candidate
   composition is inspected**, the minimum `|CONFIRMATORY_FAR|` required, tied to the inferential
   precision the follow-up intends to claim rather than to a round number. Below it, the follow-up is
   reported as lacking distant confirmation.

## Scope of this task
Produce the E0 manifest, the frozen component-ID algorithm as executable code, the fixed thresholds,
the exact hash interval, the salt, the declared FAR adequacy criterion, and the adoption record.
**Assign nothing.** There is no candidate population yet.

## Inputs
The frozen split manifest and cluster assignments from the existing embedding gates; the exact RT and
ncRNA catalogues.

## Forbidden inputs
Any model score, endpoint value or per-component composition summary. Reading one voids the rule
irreversibly.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| determinism | **positive** | two independent runs of the component-ID and hash code give byte-identical output | the algorithm is not stable; VOID |
| hash interval calibration | **positive** | on 10^6 synthetic component ids the assignment rate matches 0.20 within Monte Carlo error | the interval arithmetic is wrong; VOID |
| E0 containment | **positive** | every PAIR-ELIG pair lands in E0 | the exposure set is wrong; VOID |
| edge-direction fixture | **negative** | a synthetic component with no edge to E0 is never labelled NEAR, and one with a planted edge is never labelled FAR | the edge test is inverted; VOID |
| ordering audit | **positive** | no endpoint file was opened before the freeze timestamp | the rule is void; escalate |

## Reachability
Attainable. This task produces a specification and a manifest; there is no branch that cannot fire.

## Endpoint and criterion
- primary endpoint: the frozen rule artifacts and the E0 manifest
- **falsification criterion:** none; this task tests no hypothesis
- **death condition:** none

## Outputs
`tables/A3a_E0_manifest.tsv`, `scripts/component_id.py`, `tables/A3a_hash_calibration.tsv`,
`tables/A3a_controls.tsv`, `A3A_FROZEN.md` carrying the rule text, the thresholds, the salt, the
hash interval, the FAR adequacy criterion and the adoption record.

## What this task may NOT conclude
Anything scientific. It may not assign a candidate population, and it may not choose the rule it
executes.

---

## LAUNCHER · T-A5b1-rtdna-anchors

---
task_id: T-A5b1-rtdna-anchors
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S08
title: Experimental RT-DNA coordinate anchors on cognate ncRNAs
state: AWAITING_SPECIFICATION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A5b1-rtdna-anchors
branch: task/T-A5b1-rtdna-anchors
output_directory: analysis/t_a5b1_rtdna_anchors/
hard_dependencies: []
soft_dependencies: ["T-REG-asset-registration"]
populations_touched: ["experimental panel: RT-DNA sequences used as a coordinate anchor, not as a model test set"]
iteration_budget: 1
claim_ids_touched: []
---

# T-A5b1 · Experimental RT-DNA coordinate anchors on cognate ncRNAs

**Supersedes the withdrawn `T-A5b`, which conflated two questions and contained an arithmetic error.**

> ⚠️ **AWAITING_SPECIFICATION: the minimum unambiguous-anchor floor is referenced but not stated. Declare it before execution**

## Question
Where does each experimentally determined RT-DNA sequence map onto its cognate ncRNA?

## Hypothesis
A substantial fraction map unambiguously, because the RT-DNA is reverse-transcribed from a defined
template region of the ncRNA. Alternative: mappings are ambiguous or absent at a rate that makes the
anchor set unusable, which is itself a reportable bound.

## Scope, stated negatively and bindingly
This task establishes **where the reverse-transcribed extent sits**. It does **not** establish:

- the full biological **msd** segment beyond the reverse-transcribed extent;
- the **msr/msd boundary**;
- **msr coordinates** by any route, including "the complement region bounded by the a1/a2 arms",
  which an earlier draft wrongly proposed and which is hereby withdrawn;
- transcript boundaries, branching-guanosine placement, pairing, or orthogonality.

Those are inference steps and belong to `T-A5b2`.

## Population and inferential unit — read the arithmetic carefully
- **anchor population:** the **81** panel elements carrying an empirically determined RT-DNA
  sequence. Of these, **62** come from elements with measured RT-DNA production above zero.
- **a different population, do not conflate:** prior work reports **120** published molecules that
  locate in the ncRNA pool, splitting **56** covariance-model-recoverable against **64** model-gap.
  That is a property of the 120, **not of the 81**.
  ⚠️ An earlier draft wrote "effective n 81, split 56/64". 56 + 64 = 120. That was wrong.
- **first computational step, before anything else:** compute and report the **actual overlap**
  between the 81 anchors and the 120 located molecules, and the recoverable/gap split *within the
  81*. Do not assume it.
- inferential unit: assayed retron element.

## Inputs
| input | role |
|---|---|
| `support.csv`, 175 rows, 81 with `RTDNA_sequence` | **the anchor. Not in the v7 tree; register it via T-REG first** |
| oriented exact ncRNAs, 16,458 | the coordinate frame |
| deposited RT-RNA-DNA complexes, 8 | independent geometric cross-check, diagnostic only |

Hash every input before reading.

## Forbidden inputs
`cmalign` consensus coordinates against the 21 production covariance models, as truth. They may be
reported as a **comparator**, declared in advance, and never as an adjudicator.

## Controls — run FIRST and BLOCK
These validate **sequence mapping, orientation and coordinate handling**. They do not validate a
folding tool, which is irrelevant to this task. Per WORKING_RULES section 6a, no biological contrast
is a blocking control here.

| control | type | must show | if it fails |
|---|---|---|---|
| synthetic exact-substring fixture | **positive** | a known substring planted at a known offset, in both orientations, is recovered at exactly that offset with the correct orientation flag | coordinate or strand handling is wrong; VOID |
| synthetic mutated fixture | **positive** | a substring carrying a declared number of mismatches is recovered with the expected identity and coverage | the tolerance model is wrong; VOID |
| scrambled-pairing fixture | **negative** | RT-DNA sequences deliberately paired with non-cognate ncRNAs yield `NO_MAP` or `AMBIGUOUS` at a high rate | the mapper matches anything; VOID |
| off-by-one round trip | **positive** | converting a called coordinate back to sequence returns the original substring | classic frame error; VOID |

## Reachability
Both outcomes are attainable. A high `NO_MAP` rate is a valid, reportable result, not a failure.

## Method
Map each RT-DNA sequence to its cognate ncRNA in both orientations. Record identity, coverage,
uniqueness and every equivalent best hit. Classify. No folding, no inference, no extrapolation.

## Output schema, one row per anchor element
```
element_id · rtdna_sequence · mapping_orientation · start · end · identity · coverage
n_equivalent_best_mappings · mapping_class · distance_to_5prime_edge · distance_to_3prime_edge
cm_recoverable_flag · source · evidence_provenance
```
`mapping_class` is one of `EXACT_UNIQUE`, `HIGH_CONFIDENCE_UNIQUE`, `AMBIGUOUS`, `NO_MAP`.

**Report the distance to each sequence edge for every call.** The ncRNA extent is a covariance-model
cut, so a mapping that abuts an edge may be truncated by the cut rather than by biology.

## Endpoint and criterion
- primary endpoint: the count of `EXACT_UNIQUE` plus `HIGH_CONFIDENCE_UNIQUE` anchors
- **falsification criterion:** if unambiguous anchors fall below a floor declared before running,
  the anchor set is insufficient and `T-A5b2` does not open
- **death condition:** none. Either outcome is informative and publishable as a bound

## Expected result patterns
| pattern | TASK_STATE | SCIENTIFIC_OUTCOME |
|---|---|---|
| most anchors map unambiguously | PASS | SUPPORTS_H1; A5b2 opens |
| anchors map only for model-recoverable elements | PASS | BOUND; A5b2 opens on the anchored subset only |
| widespread ambiguity or no-map | PASS | FALSIFIED; the coordinate route closes, and that is the result |

## What this task may NOT conclude
Anything about msr, about the full msd, about ncRNAs outside the anchor set, or about pairing.

---

## LAUNCHER · T-A5b2-ncrna-architecture

---
task_id: T-A5b2-ncrna-architecture
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S08
title: Infer ncRNA coordinate architecture from the experimental anchors
state: HELD
autonomy_tier: A
compute_class: CPU_MEDIUM
worktree: TBC
branch: TBC
output_directory: analysis/t_a5b2_ncrna_architecture/
hard_dependencies: ["T-A5b1-rtdna-anchors"]
populations_touched: ["exact ncRNA catalogue: inspected"]
iteration_budget: 2
claim_ids_touched: []
---

# T-A5b2 · Infer ncRNA coordinate architecture from the experimental anchors

**HELD.** Opens only if `T-A5b1` returns `TASK_STATE=PASS` with unambiguous anchors above its declared
floor. Its scope is then set by what A5b1 actually anchored, not by what was hoped for.

## Question
Given the experimental anchor set, can ncRNA coordinate architecture be inferred for molecules that
have no experimental RT-DNA, and with what confidence?

## Why this is a separate task
A5b1 is direct measurement: a sequence maps somewhere, or it does not. This is inference from a small
anchor set to a large population. Different logic, different controls, different failure modes.
Merging them would let a caller's performance borrow credibility from the mapping's directness.

## Population and inferential unit
- fitting and evaluation population: the anchors produced by A5b1
- application population: whatever subset A5b1's result licenses, which may be far short of 16,458
- inferential unit: ncRNA instance for calls; retron type for any rate
- dependence structure: anchors are not independent across types; evaluation is lineage-blocked

## Reusable assets, not to be recomputed
Existing folds cover 99.35% of the catalogue and existing a1/a2 calls cover 95.83%, both with their
failure modes already measured. Reuse them, join on the current sequence hash, and fold only what is
genuinely missing. Their prior **conclusions** remain unverified and are not cited.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| held-out anchors | **positive** | anchors withheld from fitting are recovered at a declared tolerance | the caller does not generalise even inside the anchor set; VOID |
| lineage-blocked splitting | **positive** | held-out sets are blocked by RT lineage, never drawn at random | near-duplicates inflate the result |
| dinucleotide-shuffled ncRNAs | **negative** | recovery collapses to chance | the signal is composition |
| group II intron and DGR upstream windows | **negative** | no architecture is recovered | the caller fires on anything |
| fixed positional split at the median | **baseline** | the caller must beat it | there is no method, only a prior. This is the exact bar the previous ncRNA arm died to, 343 against 901 |

## Reachability
Attainable in both directions once A5b1 has reported.

## Endpoint and criterion
- primary endpoint: boundary agreement on lineage-blocked held-out anchors, at a declared tolerance
- **falsification criterion:** failing to beat the fixed positional baseline on lineage-blocked
  held-out anchors closes coordinate-level ncRNA inference for this project
- **death condition:** the above, permanently

## Expected result patterns
| pattern | TASK_STATE | SCIENTIFIC_OUTCOME |
|---|---|---|
| beats the positional baseline on blocked held-out anchors | PASS | SUPPORTS_H1; S08b pair expansion may be proposed |
| beats it only within model-recoverable types | PASS | BOUND; report the limit, do not claim corpus scale |
| does not beat it | PASS | FALSIFIED; a clean, cheap, permanent closure |

## What this task may NOT conclude
That a coordinate set across 16,458 is validated. Only the anchored and held-out subsets are.
Nothing about the branching guanosine, whose sequence-only route is already refuted and whose stated
precondition is exactly the boundary this task would produce.

---

## LAUNCHER · T-LINT-prose-numbers

---
task_id: T-LINT-prose-numbers
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S00
title: Numeric-provenance CANDIDATE linter (triage, not a gate)
state: AUTHORIZED
autonomy_tier: A
compute_class: ZERO
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-LINT-prose-numbers
branch: task/T-LINT-prose-numbers
output_directory: analysis/t_lint_prose_numbers/
hard_dependencies: []
populations_touched: []
iteration_budget: 2
claim_ids_touched: []
---

# T-LINT · Numeric-provenance CANDIDATE linter

**Numeric equality is not provenance.** A prose value of 99.1 may coincide with an unrelated cell in
an unrelated table and be wrongly marked resolved. This task therefore produces a **triage list of
numbers needing adjudication**, not a provenance verdict.

**A true standing gate needs a declared mapping**, not a global equality search. Emit the schema for
`PROSE_NUMBER_PROVENANCE.tsv` with `document, claim_id, numeric_value, table_path, row_key, column,
bundle, commit`, so a later gate verifies the *declared* source rather than hunting for an equal
token. Specifying that schema is part of this task; populating it is not.

## Question
Which numbers asserted in this project's markdown documents cannot be resolved to a cell in any
landed canonical table?

## Hypothesis
A non-trivial number cannot be resolved, including at least three already identified by hand.

## Why existing evidence does not answer it
No such check exists. Existing provenance discipline covers tables and figures; **all four
propagating errors found by review lived in prose or in a script string literal.**

## Population and inferential unit
- population: **mode A**, every tracked `.md`. **mode B, run separately and never silently merged**,
  the reporting and figure-generating sources (`.py`, `.R`, `.sh`, `.tex`) scanned for hardcoded
  literals, because the same-strand defect lived in a script string and not in prose
- inferential unit: a distinct numeric token in prose

## Inputs
All tracked `.md`; all `.tsv` under `results/` and the registered bundle paths, as the resolution index.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| three known defects | positive | the linter flags the same-strand figure, the matrix dimension, and the superseded silhouette | the linter cannot see what it exists to see; fix before trusting any output |
| three known-good numbers | negative | numbers that provably come from landed tables are NOT flagged | the false-positive rate makes it unusable |
| resolution rate per file | baseline | reported, so the operator can judge the signal | - |
| planted coincidence fixture | **negative** | a prose number equal to an unrelated table cell is reported as COINCIDENTAL_MATCH, never as resolved | the tool claims provenance it cannot establish; VOID |

## Reachability
The PASS outcome is a defect list, which is attainable. Note the positive control is the design
constraint: a linter that cannot find the three known cases is void regardless of what else it finds.

## Method
Extract numeric tokens with at least three significant digits or a decimal point, to avoid matching
small integers. Build a set of all numeric tokens present in landed tables. Report unresolved tokens
per file with surrounding context. Do not attempt automatic correction.

## Endpoint and criterion
- primary endpoint: count and list of unresolved numeric assertions
- **falsification criterion:** if the positive control does not flag all three known defects, the
  instrument is void and no output may be acted on
- **death condition:** none; this becomes a standing check

## Expected result patterns
| pattern | reading |
|---|---|
| finds the three, plus others | the check works; the others become an errata queue |
| finds the three, nothing else | the prose is cleaner than feared; keep the check as a gate |
| high false-positive rate | tighten the token rule and re-run, within the iteration budget of 2 |

## Outputs
`scripts/lint_prose_numbers.py`, `tables/LINT_UNRESOLVED.tsv`, `tables/LINT_CONTROL_CHECKS.tsv`

## What this task may NOT conclude
That a flagged number is wrong. Unresolved means unresolved. Adjudication is a separate errata step.

---

## LAUNCHER · T-REG-asset-registration

---
task_id: T-REG-asset-registration
governance_base: 9678a95
base_commit: 94a1a78
stage_id: S00
title: Register the discovered asset base
state: AUTHORIZED
autonomy_tier: B
compute_class: ZERO
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-REG-asset-registration
branch: task/T-REG-asset-registration
output_directory: analysis/t_reg_asset_registration/
hard_dependencies: []
populations_touched: []
iteration_budget: 1
---

# T-REG · Register the discovered asset base

## Question
What scientific assets exist across every project root, and which of them is an asset, a bounded
negative, or an unverified conclusion?

## Why this exists
The declared project was nine git worktrees. The real evidence base is **155.6 GB in 20,765
collections across eight roots**: 44,608 structures, 520 trees, 15,427 profiles, 1,059,907
matrix/embedding files, 406 PDFs. The registries list almost none of it. **Four review conclusions
reversed on discovering this**, and a fifth is pending.

## Population and inferential unit
- population: every collection in `review-stage/ASSET_SWEEP.tsv`
- inferential unit: asset collection

## Inputs
`review-stage/ASSET_SWEEP.tsv`; `review-stage/tools/asset_sweep.py`; `data/README.md`;
`docs/DATASET_REGISTRY.md`.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| already-registered assets | positive | the sweep finds the 62-chain structure register and the CATH benchmark, which ARE registered | the sweep has a blind spot |
| a renamed directory **in a throwaway fixture** | negative | the manifest hash changes, so drift is detectable. Never mutate the real asset base to test a control | the identity pin is useless; VOID |
| re-run determinism | baseline | two runs give identical hashes | — |

## Reachability
Attainable; the sweep already produced its output.

## Method
For each collection, add a registry row with path, kind, file count, bytes, manifest hash, and a
**category**: `ASSET` (reusable after hashing), `BOUNDED_NEGATIVE` (inherit as a design constraint),
or `UNVERIFIED_CONCLUSION` (re-derive before any citation). Categorisation of a collection containing
analysis outputs is tier B and goes to review, not to the task.

## Endpoint and criterion
- primary endpoint: **proposed** registry rows for every collection of at least **1 MiB or at least
  10 files**, whichever is met first. Smaller collections go in an appendix table, never omitted
- **falsification criterion:** none; this is bookkeeping
- **death condition:** none; the sweep becomes a scheduled recurring check

## Outputs
**This task does not write to `docs/` or `data/`.** It emits *proposed* rows inside its own output
directory: `tables/REG_proposed_registry_rows.tsv`, `tables/REG_asset_categories.tsv`,
`tables/REG_controls.tsv`. A **tier-B review step** merges accepted rows into the canonical registries.
This separates registration from promotion and avoids merge collisions with concurrent sessions.

Category assignment is **tier B**: file existence is factual, scientific category is interpretive.
Propose, do not decide.

## What this task may NOT conclude
Anything scientific. It may not promote a prior number by registering the file that contains it.
