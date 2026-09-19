# TASK PROTOCOL — what every task must do, and what it may never do alone

**Companion to `INDEPENDENT_SCIENTIFIC_REVIEW_2026-09-20.md` and `STARTUP_PLAN.md`.**
This is the per-task duty list for autonomous execution. Every rule below is derived from a
**documented failure in this project**, cited inline. Nothing here is general good practice for its
own sake.

---

## 1 · Three tiers of autonomy

The useful question is not "can this run autonomously" but "which part of it can".

| tier | what it covers | who decides |
|---|---|---|
| **A · fully autonomous** | computation, validation, artifact generation, reporting a measured number with its unit and denominator | the task |
| **B · autonomous, gated** | changing a task or stage status, opening a downstream stage, writing an interpretation | the task proposes; a **review step** disposes |
| **C · never autonomous** | promoting a number to a claim, changing a criterion, consuming a confirmatory population, waiving a control | the operator, explicitly |

**Tier C exists because each of its four items has already gone wrong here.** A criterion was fitted
at the winner-flip point of its own selection sweep. A confirmatory population was consumed by
cross-fitting every fold, irreversibly. A declared positive control was found arithmetically
unpassable and the instrument was frozen anyway. A gate label was read as a biological conclusion.

---

## 2 · The per-task lifecycle

The operator's sketch was: *see what to achieve → the data → what to do → revise plan → see old work
→ refine or use as comparator → run → insights → iterate.* That is the right shape. What follows
adds the duties at each step and, more importantly, the **stopping rules**, because the sketch as
written is a loop with no exit.

### Step 1 · Declare, before anything else
Question, hypothesis, population, **inferential unit and its dependence structure**, primary
endpoint, minimum detectable effect, falsification criterion, **iteration budget** (§4), and the
declared PASS outcome.

> *Why the dependence structure:* an effective-sample-size formula that reduced to `n²/n = n` was
> published in four landed result tables while the index document carried a different figure, and
> neither was the right number for the estimator actually used. Declaring the unit is not enough.

### Step 2 · Registry lookup, not a search
Query `ASSET_SWEEP.tsv` and the dataset registries for every input and for the question itself.
Returns three categories, treated differently (§3). **This is a lookup of seconds, not a research
task.** It is only a research task while the backlog is unpaid, which is Phase 1 of the startup plan.

> *Why:* the declared project was nine git worktrees. The real evidence base is 155.6 GB across eight
> roots. Four conclusions in the review reversed on discovering it, and a fifth is pending.

### Step 3 · Reachability check, before compute
Demonstrate that the declared PASS outcome is **attainable from the actual input population**.

> *Why:* one held-out tier contained zero instances of the class its success rule required, so the
> PASS branch was unreachable by construction. Two trivial baselines returned a constant on every
> held-out candidate, so a comparison reported as passed was never evaluated.

### Step 4 · Controls run first, and they block
Positive control, negative control and baseline are **tasks with their own states**, not fields in a
document. The primary analysis does not start until they are in PASS.

> *Why, and this is the project's most frequent failure with at least seven instances:* a placement
> positive control was commented out in its runner; an acceptance criterion had a ceiling of 84.8 %
> against a required 95 % and was never run; four declared validation arms were retroactively
> dropped; a retrieval positive control was predeclared and never ran; a held-out tier never opened;
> negative and homologous-chemistry controls were never scored.

### Step 5 · Run
Input hashes pinned, seed recorded, software version recorded, job ID recorded, stdout and stderr
captured, exit code captured, partial output distinguishable from complete, resume-safe, no silent
overwrite. `COMPUTE_COMPLETE` is not `PASS`.

### Step 6 · Validate
Expected-file inventory, then the declared endpoint computed exactly as preregistered. **Consumption
gate:** refuse to read any upstream artifact whose producing task is not in PASS.

> *Why:* nothing currently prevents a downstream task from reading a table produced by a task that
> ended in FAIL or STOP.

### Step 7 · Report facts, not interpretation
The task emits numbers with units, denominators and intervals. **Every number it writes into prose
must resolve to a canonical table cell.** The task does not write what the number means.

> *Why:* a same-strand figure wrong by 0.7 points was a hardcoded string literal in a producing
> script and propagated into four index documents; a distance matrix was cited at the wrong
> dimension and conflated with a different matrix, propagating from a stage brief into two more; a
> superseded silhouette is still in print in two files.

### Step 8 · Stop, or iterate within budget (§4)

### Step 9 · Stage synthesis, then review, then promotion
A task never promotes its own claim. The path is task → validation → stage synthesis → independent
review → claim registry → promoted claim → thesis or paper.

---

## 3 · Prior work: three categories, three treatments

The operator's doubt is well founded and the evidence resolves it sharply. Prior work here is not one
thing.

| category | value | treatment | evidence |
|---|---|---|---|
| **Assets** — structures, matrices, alignments, embeddings, profiles | **high**, and expensive to regenerate | reuse after hashing and registration | 44,608 structures, 1.06 M matrix files, 155.6 GB. Two independent Mestre-scale fold sets already exist |
| **Bounded negatives** — a question tested against a predeclared criterion and refuted with demonstrated power | **high, and systematically underrated** | inherit as a constraint on design; do not re-run | the phylogeny: 312 trees, five preregistered routes, two independent reviews, and a measured character bound of 157 alignable positions. Re-running it would have cost months |
| **Conclusions and numbers** | **near zero, and actively hazardous** | `[UNVERIFIED]`; re-derive before any citation | the same prior project records 26 untraced tables, 21 print-only scripts, 19 of 31 tree scripts writing no artefact, four tables rebuilt from logs, one headline wrong by 224×, and a supersession register warning that a reader before a given date would have cited three withdrawn results |

**So: take the files and the refutations. Leave the numbers.** That is already this project's governing
rule; the failure was never the rule, it was that nothing looked.

**A comparator is a fourth use and it is legitimate.** A published reference topology, a prior
positional prior, a prior silhouette: these may be used as *comparators* provided the comparison is
declared in advance and the prior value is never treated as truth.

---

## 4 · The iteration budget, and why it is the most important rule here

An autonomous loop whose last step is "refine and iterate" will refine until something passes. That
is hypothesis-fitting by machine.

**Rule.** Every task declares an iteration budget in advance. Every iteration is recorded with what
changed and why. On exhausting the budget without meeting the criterion, the task terminates as
`INCONCLUSIVE` and **escalates to a human**. It does not quietly try a seventh variant.

**A changed criterion is a new task**, with a new ID, that inherits the old one's record. It is never
an edit.

> *Why:* a holdout gate failed, was repaired, and passed on the second attempt; independent review
> then returned FAIL/BLOCK 5/10 with the finding that human blinding was not established, because
> the first attempt's results had motivated the rule class used in the second. A separate transfer
> gate had its selection cutoff land exactly at the winner-flip point of its own sweep. Both are
> unbounded iteration, and both were caught only by external review.

---

## 5 · Definition of done

A task is done when it is in a terminal state with: preregistration committed **before** job
submission, and the ordering checked automatically; all controls in PASS; declared outputs present
and hash-pinned; the endpoint computed as preregistered; every emitted number resolving to a table;
the confirmatory populations it touched recorded; and its interpretation left to the stage synthesis.

A stage is done when it has a decision report naming the outcome that fired, the downstream stages
that outcome opens and closes, and a thesis artifact set that compiles **including when the outcome
is negative**.

---

## 6 · What this does not fix

Two things no protocol reaches, stated so nobody assumes otherwise.

**Untouched evidence does not regenerate.** The pairing holdout is gone. Treat confirmatory
populations as a depleting budget, require every task to declare what it touches, and let the
orchestrator refuse a later confirmatory claim on a population already consumed.

**A protocol cannot supply a missing measurement.** Orthogonality needs cross-pair functional labels.
Roughly fifty exist in the published literature and none is on disk in machine-readable form. No
amount of orchestration substitutes for extracting them, and no amount substitutes for the swap panel
if they prove insufficient.
