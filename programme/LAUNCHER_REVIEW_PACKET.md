# LAUNCHER REVIEW PACKET

**For an independent adversarial reviewer.** Everything needed to stress-test the eight task
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
`review-stage/INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` (18 sections). Five of its conclusions
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
| de novo comparative ncRNA **discovery** loses to a fixed positional interval | 901 against 343 at IoU ≥ 0.5; per-type priors 969 |
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
- No **co-evolution** language. There is no ancestry null and none is currently obtainable.
- No **per-pair biological inference** from a likelihood difference. A counterfactual is a
  conditioning control, not a negative pair.
- No **n × n compatibility matrix**, and no laboratory candidate nomination from a sequence score.
- No **gate label used as a biological conclusion**.
- No statement that something is **absent** without a registry lookup and a positive control.
- No **retron-versus-non-retron** claim evaluated on held-out family: there is only one retron family.
- No number in prose that does not resolve to a canonical table cell.

## 6 · Claim promotion

`task → validation → stage synthesis → independent review → claim registry → promoted claim → thesis/paper`

No task promotes its own claim. Statuses are the single closed vocabulary in
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
2. **No unfinished-producer reads.** Neither reads an artifact whose producing task is not in `PASS`.
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

```markdown
# TASK REPORT — <task-id>

STATE: PASS | FAIL | STOP | INCONCLUSIVE | BLOCKED
CRITERION: <the preregistered criterion, verbatim>
MET: yes | no | not evaluable — <one line>

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
governance_base: b5443e1
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
- effective n, expected: between 9 and 25 depending on blocking

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
| control | type | must show | if it fails |
|---|---|---|---|
| G−U under blocking | positive | survives; it is favourable in 86.0% of components | the blocking is too aggressive; report and stop |
| P−T under blocking | negative | loses significance; it is a within-type permutation arm | blocking is not removing the dependence it should |
| existing unclustered intervals | baseline | reproduced exactly before any blocking is applied | the reader is not reading the file correctly; stop |

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
governance_base: b5443e1
stage_id: S02
title: Reciprocal family-frame analysis of RT core content
state: AUTHORIZED
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
governance_base: b5443e1
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
- primary endpoint: count of distinct measured non-cognate combinations with a comparable endpoint
- **falsification criterion / stage-12 gate:** declare the floor **before** curating. Below it, no
  computational orthogonality model is attempted and a designed swap panel becomes the prerequisite.
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
governance_base: b5443e1
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
- inferential unit: component, with the pair-weighted view reported beside it
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
| singletons in C4 | negative | is zero, confirming the structural exclusion | the population claim is wrong; stop |

## Reachability
Attainable for any input.

## Method
Intersect tier memberships; recompute each tier's component-level and pair-weighted mean on the
common set; report both alongside the full-population values.

## Endpoint and criterion
- primary endpoint: the four tier means on the common population
- **falsification criterion:** if the common-population ladder is monotone, the current wording stands
  and this task returns FAIL for its own hypothesis
- **death condition:** none

## Expected result patterns
| pattern | reading |
|---|---|
| non-monotone, collapse at C3 | near-neighbour counterfactuals abolish the effect; C4 is a different population, not a tighter control |
| monotone | the published description is correct and this objection is withdrawn |

## Outputs
`tables/A2_common_population_ladder.tsv`, `tables/A2_tier_membership.tsv`

## What this task may NOT conclude
Whether pair-level discrimination exists. It describes the shape of an existing measurement.

---

## LAUNCHER · T-A3-confirmatory-population

---
task_id: T-A3-confirmatory-population
governance_base: b5443e1
stage_id: S00
title: Freeze the pairing confirmatory population
state: AWAITING_ADOPTION
autonomy_tier: A
compute_class: CPU_SMALL
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A3-confirmatory-population
branch: task/T-A3-confirmatory-population
output_directory: analysis/t_a3_confirmatory_population/
hard_dependencies: []
populations_touched: ["defines E0 and freezes the split; touches no endpoint"]
iteration_budget: 1
claim_ids_touched: []
---

# T-A3 · Freeze the pairing confirmatory population

## Why this is a task and not a decision — read this first

The **rule** below is tier C: the operator declares it, and no task may choose it. **Executing** the
rule is tier A: it is deterministic by construction, uses SHA256 with a fixed salt and no random
number generator, and needs no human once the rule is adopted.

**This launcher carries the rule in full.** Once the operator marks it adopted, the board state moves
`AWAITING_ADOPTION → AUTHORIZED` and every later run of this task is fully autonomous and reproduces
byte-identically. The human writes nothing again.

## Question
Which components of any future pairing population may serve as confirmation, and which are already
exposed?

## THE RULE — frozen text, applied verbatim, never re-derived

1. **E0, the exposure set.** Every sequence used by the retrieval gate, X1, or X2 during model
   development is E0. **No member of E0 may ever be called untouched confirmation of those
   analyses.** X2 cross-fitted all five folds, so all of PAIR-ELIG is in E0.
2. **Leakage components.** Candidate pairs are grouped by sequence-only edges:
   - RT edge at **≥ 50% amino-acid identity over ≥ 80% coverage**;
   - ncRNA edge at **≥ 80% nucleotide identity over ≥ 80% coverage**;
   - exact duplicates and copies of the same biological pair are always connected.
3. **Assignment.** Component-level and deterministic, `SHA256(component_id + salt)`, salt
   `PAIR_CONFIRMATORY_V1_2026-09-20`, lowest ~20% of the hash space to `CONFIRMATORY`, remainder to
   `DEVELOPMENT`.
4. **Ordering.** Assignment happens **before** any model score, endpoint or component composition is
   inspected. No rebalancing after inspection, ever.
5. **Near and far.** Report `CONFIRMATORY_NEAR` and `CONFIRMATORY_FAR` separately. **FAR** means no
   declared RT edge **and** no declared ncRNA edge to any member of E0.
6. **Sealing.** Once frozen, confirmatory components may not influence feature selection,
   architecture, thresholds, stopping rules, hyperparameters or error analysis. They are opened
   **once**, after the relevant analysis is frozen.
7. **Honesty clause.** If no adequate prospective population exists, the follow-up is reported as
   **lacking confirmatory evidence**. An untouched set is never manufactured retrospectively.

## THE FIRST OUTPUT, AND IT BLOCKS

⚠️ **Report `|CONFIRMATORY_FAR|` before anything else, and stop there if it is below a floor the
operator declares with the rule.**

Rationale, measured: **100% of held-out pairs in the existing split were reachable from training by
at least one modality**, and 82.46% of held-out RTs had a ≥ 0.50-identity training relative. A far
set that comes back empty or tiny is therefore the expected outcome and **is itself the finding**: it
means distant confirmation is not obtainable from this corpus at all, and every future pairing claim
must say so in advance rather than discover it at review.

## Population and inferential unit
- population: any candidate pairing population presented for confirmation, plus E0 for the edge test
- inferential unit: leakage component

## Inputs
The frozen split manifest and cluster assignments from the existing embedding gates; the exact RT and
ncRNA catalogues; any new candidate pairs offered for confirmation.

## Forbidden inputs
Any model score, endpoint value, or per-component composition summary. Reading one before assignment
voids the split irreversibly.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| determinism | positive | two independent runs give byte-identical assignments | the salt or the component id is not stable; stop |
| E0 containment | positive | every PAIR-ELIG pair lands in E0 | the exposure set is wrong |
| edge symmetry | negative | a pair with no edge to E0 is never labelled NEAR | the edge test is inverted |
| ordering audit | baseline | no endpoint file was opened before the assignment timestamp | the split is void; escalate |

## Reachability
Both outcomes attainable. An empty FAR set is a valid and expected result, not a failure.

## Endpoint and criterion
- primary endpoint: the frozen assignment table, plus `|CONFIRMATORY_NEAR|` and `|CONFIRMATORY_FAR|`
- **falsification criterion:** none; this task freezes a population, it tests no hypothesis
- **death condition:** if `|CONFIRMATORY_FAR|` is below the declared floor, pairing follow-ups are
  reported as lacking distant confirmation, permanently, unless a new population is acquired

## Outputs
`tables/A3_component_assignment.tsv`, `tables/A3_near_far_counts.tsv`, `tables/A3_E0_manifest.tsv`,
`tables/A3_controls.tsv`, `A3_FROZEN.md` with the rule text and its adoption record

## What this task may NOT conclude
Anything scientific. It may not evaluate a model, and it may not adjust the split to make any later
result come out better.

---

## LAUNCHER · T-A5b-msrmsd-coordinates

---
task_id: T-A5b-msrmsd-coordinates
governance_base: b5443e1
stage_id: S08
title: msr/msd coordinates and RT-DNA extent, anchored on experimental RT-DNA
state: AUTHORIZED
autonomy_tier: A
compute_class: CPU_MEDIUM
preferred_backend: workstation
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-A5b-msrmsd-coordinates
branch: task/T-A5b-msrmsd-coordinates
output_directory: analysis/t_a5b_msrmsd_coordinates/
hard_dependencies: []
soft_dependencies: ["T-REG-asset-registration"]
populations_touched: ["exact ncRNA catalogue 16,458: inspected", "published panel 175: used as ANCHOR, not as a model test set"]
iteration_budget: 2
claim_ids_touched: ["C-34", "C-09"]
thesis_artifacts: ["S08 figures, tables, methods, limitations"]
---

# T-A5b · msr/msd coordinates and RT-DNA extent, anchored on experimental RT-DNA

## Question
Can the msr/msd boundary and the RT-DNA extent be located as **coordinates** on retron ncRNAs, using
the experimentally determined RT-DNA sequences as an anchor that is independent of the covariance
models?

## Hypothesis
Yes for the anchored subset, because msd is the template for the RT-DNA, so an experimentally
determined RT-DNA sequence maps onto ncRNA coordinates and fixes one boundary directly. Alternative:
the mapping is ambiguous or the anchor set is too small, in which case the task returns a bounded
negative and the ncRNA boundary question closes.

## Why existing evidence does not answer it — registry lookup result
**This is a revision of an earlier, wider proposal that the registry lookup partly closed.**

| component | prior state | consequence for this task |
|---|---|---|
| folding | **DONE**: 16,351 of 16,458 (99.35%) already folded with RNAfold + bpRNA, dot-bracket stored | **reuse, do not recompute**; build the join on the current sequence hash and fold only the ~107 missing |
| a1/a2 inverted repeat | **DONE**: 15,772 of 16,458 (95.83%) already called, with a per-span shuffle null and a 210,862-sequence negative | **reuse**; gold 0.8129 against group II background 0.0959 |
| msr/msd as features | **DONE but demoted**: presence flags from `cmalign` against the same 21 covariance models; the rule classified 47% of confirmed ssDNA producers as incomplete | **inherit as a warning, not as input.** Coordinates were never landed and must not be built this way |
| branching guanosine | **REFUTED from sequence alone**: every set passes its bar and so does its own shuffle; the gold panel does not beat its shuffle | **out of scope.** The prior work states its precondition is the msr/msd boundary, which is what this task produces |
| RT-DNA extent | **NEVER COMPUTED**; the 81 RT-DNA sequences were never used for it | **this is the gap** |

## Population and inferential unit
- **anchor population:** the 81 elements with an empirically determined RT-DNA sequence
- **application population:** 16,458 exact ncRNAs, output as a confidence-graded coordinate set
- inferential unit: ncRNA instance for calls; **retron type for any rate**
- dependence structure: anchor molecules are not independent of each other by type; report per-type
- **effective n for any claim: 81, and the honest evaluation split is 56 CM-recoverable against 64 CM-gap**

## Inputs
| input | path | role |
|---|---|---|
| oriented ncRNAs, 16,458 | `data/derived/rt_ncrna_oriented_v1.fna` | application population |
| prior folds, 16,359 | prior project `stage4_ncRNA_assessment/cache/p2_structures.parquet` | **ASSET** — reuse |
| prior a1/a2 per span | prior project `ncrna_extractor_detector/tables/c1_a1a2_per_span.tsv.gz` | **ASSET** — reuse |
| experimental panel, 81 RT-DNA sequences | `support.csv` in the prior project's supporting material | **the anchor. Not in v7; register it first** |
| deposited complexes, 8 | registered structure cache | independent geometric check |

Hash every input. Prior tables enter as **assets**; none of their conclusions may be cited.

## Forbidden inputs
`cmalign` msr/msd consensus coordinates against the 21 production covariance models, as a source of
truth. They define the population and cannot adjudicate a boundary within it. They may be reported as
a **comparator**, declared in advance.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| RNAfold base-pair recovery on known msr-msd | **positive** | reproduces the prior 0.9137–0.9508 range on the same molecules | the folding instrument is not behaving as it did; stop before any boundary work |
| deposited complexes | **positive** | called coordinates agree with the RNA chain geometry in the 8 structures | the coordinate frame is wrong |
| group II intron and DGR upstream windows | **negative** | no msr/msd architecture recovered | the caller fires on anything |
| dinucleotide-shuffled real ncRNAs | **negative** | recovery collapses to chance | the signal is composition |
| fixed positional split at the median msr/msd ratio | **baseline** | the method must beat it | there is no method, only a prior |

## Reachability
Both outcomes attainable. The anchor is 81 real molecules with real RT-DNA sequences; a mapping
either exists or does not, and both are measurable. **The PASS branch requires the positive control
to reproduce first**, which is exactly the check the prior branching-G work shows to be decisive.

## Method
Map each experimental RT-DNA sequence onto its cognate ncRNA to fix the msd extent. Derive msr as the
complement region bounded by the a1/a2 arms already called. Fold only what is not already folded.
Report coordinates with a confidence grade and with the distance from every call to the sequence
edge, because the extent is a covariance-model cut and a boundary near an edge may be its artefact.

## Endpoint and criterion
- primary endpoint: agreement between the RT-DNA-anchored msd boundary and the called boundary, on
  the anchor population, at a declared tolerance
- **falsification criterion:** if the method does not beat the fixed positional split on the anchored
  molecules and the deposited complexes at the declared tolerance, the decomposition is not
  established and is not used downstream
- **death condition:** failing the above closes coordinate-level ncRNA decomposition for this project
  and the boundary chapter becomes a bounded negative

## Expected result patterns
| pattern | reading |
|---|---|
| anchored boundaries recovered, generalise to the 16,458 with grades | the project gains its first biological object on the RNA side; S08b pair expansion opens |
| recovered only on the 56 CM-recoverable, chance on the 64 CM-gap | matches the prior work's own limit; report as a bound, do not claim corpus scale |
| not recovered above the positional split | a clean, cheap, permanent closure; the chapter is a negative |

## Outputs
`tables/A5b_anchor_mapping.tsv`, `tables/A5b_coordinates_graded.tsv`, `tables/A5b_controls.tsv`,
`tables/A5b_comparator_cmalign.tsv`, `figures/`, `ARTIFACT_MANIFEST.tsv`

## What this task may NOT conclude
That an ncRNA lacking a call lacks the architecture. That a coordinate set at 16,458 is validated;
only the anchored subset is. Anything about the branching guanosine. Anything about RT–ncRNA pairing.

---

## LAUNCHER · T-LINT-prose-numbers

---
task_id: T-LINT-prose-numbers
governance_base: b5443e1
stage_id: S00
title: Numeric provenance linter over prose
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

# T-LINT · Numeric provenance linter over prose

## Question
Which numbers asserted in this project's markdown documents cannot be resolved to a cell in any
landed canonical table?

## Hypothesis
A non-trivial number cannot be resolved, including at least three already identified by hand.

## Why existing evidence does not answer it
No such check exists. Existing provenance discipline covers tables and figures; **all four
propagating errors found by review lived in prose or in a script string literal.**

## Population and inferential unit
- population: every tracked `.md` in the repository and in `PROJECT_REVIEW_PACKAGE/`
- inferential unit: a distinct numeric token in prose

## Inputs
All tracked `.md`; all `.tsv` under `results/` and the registered bundle paths, as the resolution index.

## Controls — run FIRST and BLOCK
| control | type | must show | if it fails |
|---|---|---|---|
| three known defects | positive | the linter flags the same-strand figure, the matrix dimension, and the superseded silhouette | the linter cannot see what it exists to see; fix before trusting any output |
| three known-good numbers | negative | numbers that provably come from landed tables are NOT flagged | the false-positive rate makes it unusable |
| resolution rate per file | baseline | reported, so the operator can judge the signal | — |

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
governance_base: b5443e1
stage_id: S00
title: Register the discovered asset base
state: AUTHORIZED
autonomy_tier: B
compute_class: ZERO
worktree: /home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-T-REG-asset-registration
branch: task/T-REG-asset-registration
output_directory: docs/, data/
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
| a deliberately renamed directory | negative | the manifest hash changes, so drift is detectable | the identity pin is useless |
| re-run determinism | baseline | two runs give identical hashes | — |

## Reachability
Attainable; the sweep already produced its output.

## Method
For each collection, add a registry row with path, kind, file count, bytes, manifest hash, and a
**category**: `ASSET` (reusable after hashing), `BOUNDED_NEGATIVE` (inherit as a design constraint),
or `UNVERIFIED_CONCLUSION` (re-derive before any citation). Categorisation of a collection containing
analysis outputs is tier B and goes to review, not to the task.

## Endpoint and criterion
- primary endpoint: registry rows covering every collection above a declared size floor
- **falsification criterion:** none; this is bookkeeping
- **death condition:** none; the sweep becomes a scheduled recurring check

## Outputs
Registry rows in `data/README.md` and `docs/DATASET_REGISTRY.md`; `docs/ASSET_CATEGORIES.tsv`.

## What this task may NOT conclude
Anything scientific. It may not promote a prior number by registering the file that contains it.
