# SCIENTIFIC DAG — the remaining programme, by dependency type

**As of 2026-09-20, revised after Execution Batch 02.** Companion to
`programme/ALL_DOWNSTREAM_TASKS.tsv` (**59 tasks**) and
`programme/PARALLEL_EXECUTION_PLAN.md` (what runs where, and when).

> ⛔ **INDEPENDENTLY REVIEWED AND REJECTED, then corrected.** A fresh read-only Codex thread
> (`01a0bcb2`) reviewed this DAG with the task register and the execution plan and returned
> **REJECT**. Every coordinator-fixable finding is applied; the corrections are marked
> **`[REVIEW 01a0bcb2]`** where they land. Findings needing a scientific decision are recorded in
> `OVERNIGHT_RUN_REPORT.md` §10 and are **not** resolved here.
>
> The two corrections that change what this document *claims*:
> - §8's assertion that **no edge scores a CM-derived call against a CM-derived call is FALSE.**
>   `T-A19` does exactly that. Corrected in §8.
> - `T-AUDIT1`'s edge is **`SOFT_INTERPRETIVE`, not `CONTROL`.** It produces an inventory and
>   nominates; it may not re-classify any task's outcome, so it blocks nothing.

> ⚠️ **SUPERSEDED IN PART — read §10 first.** Execution Batch 02 and this session's reconciliation
> changed four nodes and added five. The structure below still holds; the **node states do not**.
> `programme/RECONCILIATION_2026-09-20.md` carries the evidence.

> **This document is the dependency structure. It is deliberately written before the compute
> schedule**, because a schedule built from stage numbers rather than from dependencies is how a
> programme serialises work that is independent and parallelises work that is not.

---

## 0 · Edge types, and what each one licenses

| type | meaning | may the downstream task start early? |
|---|---|---|
| `HARD_SCIENTIFIC_DEPENDENCY` | the downstream question is **not well posed** until the upstream result exists | **No.** The orchestrator refuses |
| `CONTROL_DEPENDENCY` | the upstream task is the **blocking control** for the downstream one | **No.** Controls run first and they block |
| `DATA_DEPENDENCY` | the downstream task **reads an artifact** the upstream produces | No, but only the read is blocked — design, preregistration and fixtures may proceed |
| `PROMOTION_DEPENDENCY` | the upstream gate must clear before anything downstream becomes a **claim** | **Yes — the work may run.** Only promotion is blocked |
| `SOFT_INTERPRETIVE_DEPENDENCY` | the upstream result changes how the downstream one is **read**, not whether it is valid | Yes. Must never block |

⚠️ **Two rules this project has already paid for.**

1. **A stage number is not a dependency.** S12 work (`T-A23c` source-data retrieval) has no upstream
   in this DAG at all and is among the highest-yield actions available. S03b (`T-A17`) is a leaf,
   not a trunk. Numbering reflects the order the questions were *asked*, not the order they can be
   *answered*.
2. **`PROMOTION_DEPENDENCY` is not an execution dependency.** `T-HIA-human-input-audit` gates every
   claim in the project and blocks **no** computation. Treating it as an execution edge would idle
   the entire programme behind one operator decision.

---

## 1 · The trunk, and what actually hangs off it

```
                    ┌─ T-C1-rt-core-extraction ─────────────────── (PREP, goal 2)
                    │        │
   Stage 1 corpus ──┤        ├──DATA──▶ T-F1-motif-scan            (PREP, goal 4)
   (landed)         │        ├──DATA──▶ T-F2-domain-architecture   (PREP, goal 4)
                    │        ├──DATA──▶ T-P2-character-economy     (AUDIT, goal 3)
                    │        └──DATA──▶ T-P1-relatedness-backbone  (PREP, goal 3)
                    │                        │
                    │                        │   ◀── THE ONLY REAL TRUNK
                    │                        │
                    │        ┌───────────────┼──────────────────┬─────────────────┐
                    │      HARD            HARD               HARD              HARD
                    │        ▼               ▼                  ▼                 ▼
                    │  T-A0b-lineage   T-F3-retron-      T-N2-neighbourhood   T-P3-relatedness
                    │  -partition-     feature-          -lineage-            -representation
                    │  intervals       contrast          comparison
                    │  (goal 3/10)     (goal 4)          (goal 6)             (goal 3)
                    │
                    └─ T-N1-neighbourhood-extraction-qa ────────── (PREP, goal 6)
                             │
                             └──DATA──▶ T-A10-genomic-architecture
```

**`T-P1-relatedness-backbone` is the trunk and it is a PREPARATION task.** It produces a
50 %-identity partition of the exact-RT catalogue. Four separate inference tasks take a
`HARD_SCIENTIFIC_DEPENDENCY` on it, and **none of them takes a dependency on a resolved topology**,
which has been measured not to exist (312 trees; 157 alignable characters; 1.39 taxa/character).

**Why this edge is `HARD` and not `DATA`.** Without a lineage partition that is *not nested inside
the inference unit*, the downstream questions are not merely unanswered — they are **ill-posed**.
T-A0 demonstrated exactly this: the 50 %-identity grouping it had available sits strictly inside
the component unit (2,455 groups inside 1,075 components; every `rt_rep` in exactly one component),
so blocking on it degenerates to no blocking at all.

---

## 2 · Preparation is split from inference everywhere it can be

This is the section that buys the parallelism. Each row is a split that was **not** forced by the
science and **was** being enforced by habit.

| preparation — runs now | inference — waits | edge | what the split buys |
|---|---|---|---|
| `T-C1` RT core extraction | `T-A16` reciprocal frame, `T-A17` sensitivity arm | DATA | feature extraction needs no comparative decision |
| `T-F1` motif scan, `T-F2` domain architecture | `T-F3` feature contrast | DATA + HARD(T-P1) | scanning for YXDD is not comparing YXDD |
| `T-N1` neighbourhood extraction + QA | `T-N2` lineage-controlled comparison | DATA + HARD(T-P1) | extraction and QA are mechanical; the comparison needs the partition |
| `T-S1` structure inventory, `T-S2` Foldseek calibration | `T-S3` structural interpretation | CONTROL | **method calibration precedes biological interpretation**, never the reverse |
| `T-M1` embedding cache verification | `T-A1` baselines, `T-A2b` matched ladder | DATA | caching and hashing 42.4 GB of `.npy` is not pairing inference |
| `T-R1` direct RT-DNA mapping | `T-A5b2` generalised boundary inference | HARD | **direct mapping is a lookup; boundary inference is a model** |
| `T-P3` relatedness representation | *(nothing)* | — | **a representation of relatedness is not a claim of resolved phylogeny**, and must never be scheduled as though it were |
| `T-P1` clustering | everything in §1 | HARD | the partition is the shared prerequisite, computed once |

---

## 3 · Control edges — the ones that block

```
T-S2-foldseek-calibration ──CONTROL──▶ T-A7-stage3a-positive-control ──PROMOTION──▶ T-S3
T-C2-cm-call-inventory    ──DATA─────▶ T-A19-withheld-model-control  ──CONTROL───▶ T-S07-reopen
T-AUDIT2-task-report-backfill ──DATA──▶ T-GATE1-consumption-gate          [REVIEW 01a0bcb2]
T-AUDIT1-circular-control-sweep ──SOFT_INTERPRETIVE──▶ every task carrying a blocking control
```

**`[REVIEW 01a0bcb2]` `T-AUDIT1`'s edge is corrected from `CONTROL` to `SOFT_INTERPRETIVE`.** An
earlier draft here called it a control edge onto the whole programme, which would mean it must run
before everything. Its own launcher says the opposite and is right: *"It may not re-classify any
task's outcome, withdraw any result, or change any board state."* **It produces an inventory and
nominates. It blocks nothing.** Its question is still the one the Batch One reviewer generalised —
*what broken instrument does this catch?* — and it is the one task this session would dispatch
first, but it is not a gate.

**`[REVIEW 01a0bcb2]` `T-GATE1` gains `DATA_DEPENDENCY:T-AUDIT2`.** A gate that reads task reports
needs task reports to exist, and none satisfying the contract is landed.

⚠️ **`T-A7` is a `CONTROL_DEPENDENCY` that is also confirmatory — and it is circular as specified.**
All 19 truth-bearing chains in `STRUCT-62` are **non-retron**; all 21 retron chains sit in Tier B or
C and were never scored, and Tier B is partly design-inspected so not blind.

⛔ **`[REVIEW 01a0bcb2]` worse than that: `T-A7` and `T-S3` would spend the same Tier B chains** —
one as the control, the other as the headline. **A control and an inference cannot both claim the
same chains as independent evidence.** The independent specification names HIV-1 p66 and externally
partitioned RTs as the biological positive; the task should return to those named external
positives. **Operator decision; not fixed here.**

---

## 4 · Promotion edges — they block claims, never compute

```
T-HIA-human-input-audit ──PROMOTION──▶ EVERY task in the programme
T-AUDIT2-task-report-backfill ──DATA──▶ T-GATE1-consumption-gate ──PROMOTION──▶ every consumer
T-S12-floor-declaration ──PROMOTION──▶ S12
```

**Nothing in this project is promotable today.** `human_input_audit: DONE` appears nowhere except
the specification that defines it, and `BUNDLE_SPEC.md` makes it a precondition. That is one
operator decision standing between 53 tasks and any claim at all — **and it blocks none of them
from running.**

`T-GATE1` is worth naming separately. The review's finding was blunt: *"I described a gate; I
shipped a function."* The helper is called only by its own tests, reads no task report, verifies no
hash and mediates no file access. Until `T-GATE1` lands, **every artifact from a self-labelled PASS
task is consumable regardless of whether the PASS was earned.** `T-AUDIT2` feeds it, because a gate
that reads task reports needs task reports to exist, and none satisfying the contract is landed.

---

## 5 · Soft interpretive edges — they must never block

```
T-M2-landed-interval-coverage-sweep ──SOFT──▶ every pairing-arm reading
T-P2-character-economy-audit        ──SOFT──▶ S09 reopening proposal
T-D1-annotation-disagreement        ──SOFT──▶ T-A6, T-A10
T-A23e-block-level-recount          ──SOFT──▶ T-S12-floor-declaration
```

`T-M2` is the widest-reaching Batch One finding and is currently unbounded: the unclustered
generator behind the landed pairing intervals covered **0.65** on its positive fixture and **0.659**
on its null fixture, against a nominal 0.95. ⚠️ **Those numbers are from one R − G fixture under a
fitted Gaussian random-intercept model.** They are a warning about a shared method, not a
measurement of any other interval, which is precisely why `T-M2` exists and why **each bundle needs
its own fixture** rather than an inherited number.

---

## 6 · Closed branches, and the exact condition that reopens each

Recorded here so no downstream task quietly re-derives a bounded negative, and so the reopening
conditions are not lost.

| branch | state | reopens **only** on |
|---|---|---|
| `S09` ancestry-aware correspondence | `CLOSED_CURRENT_EVIDENCE` | a character source **materially exceeding 157 alignable positions** (probed by `T-E1`), **or** restriction to shallow clades with the independent-unit count **declared in advance** (`T-E2`, operator) |
| `S07` de novo ncRNA discovery as implemented | `CLOSED_CURRENT_DESIGN` | a design that groups loci by an **independent** relatedness structure, scores against **published extents** rather than CM cuts, keeps the **fixed positional interval as a competing arm**, and passes **leave-one-subtype-out** recovery (`T-A19`) |
| palm/fingers/thumb partition | settled negative | not reopenable as posed — the partition is not operationally defined in this project's parser **or in the literature**; two 2026 papers publish incompatible partitions of the same protein |
| historical 11-clade placement | settled negative | shuffled queries were confidently placed at 7.9 % against a ≤1 % limit |
| neighbourhood as a retron detector | settled negative | retrons 27th of 41 families, inside a **predeclared** dead band |

⚠️ **`T-E1` tests S09's own declared reopening condition. It does not reopen S09.** A positive
result is a *proposal to the operator*, and the distinction is the whole reason the condition was
written down in advance.

---

## 7 · What has no upstream at all

These take **no** dependency on anything in this programme, and any schedule that makes them wait
is wrong:

`T-GATE1-consumption-gate` · `T-AUDIT1-circular-control-sweep` · `T-AUDIT2-task-report-backfill` ·
`T-REG2` · `T-REG3` · `T-REG4` · `T-A23b` · `T-A23c` · `T-A23d` · `T-A3a` · `T-HIA`

**`T-A23c-source-data-retrieval` is the one to notice.** It is a Stage-12 task, Stage 12 is closed,
and it is still the highest-yield action in the programme: one source states that source data
accompany the paper, and obtaining it converts **34 of 56** cross-pair rows from design-only to
numeric — **no experiment, no population, no compute.** A stage-ordered schedule would have placed
it last.

---

## 8 · Cycles, and the one that must not form

There is exactly one place a cycle threatens, and it is the circularity the original review named:

```
   CM-CALLS  ──defines──▶  ncRNA calls  ──scored against──▶  CM-CALLS
```

`CM-CALLS` — the 21 Mestre-authored covariance models — **defines the population it would be scored
on**. Any boundary or type claim evaluated against those calls is same-paradigm and adjudicates
nothing.

⛔ **`[REVIEW 01a0bcb2]` An earlier draft of this section claimed "No edge in this DAG scores a
CM-derived call against a CM-derived call." THAT WAS FALSE. `T-A19` does exactly that.**

`T-A19-withheld-model-control` withholds a subtype, rebuilds a covariance model, and scores recovery
**against the withheld model's own calls** — a CM-derived caller judged by CM-derived calls. It
closes the very cycle this section says it breaks.

**Consequence, recorded not repaired:**

| `T-A19` may be | `T-A19` may NOT be |
|---|---|
| a **same-paradigm implementation diagnostic**: does the machinery recover a subtype it was not shown? | an independently established biological positive control |
| reported with that limitation stated | sufficient on its own to reopen `S07` |

`S07` reopening requires **five** declared conditions, not one, and `T-A19` is one of them.
Redesigning it so it is not circular is an **operator decision**.

What genuinely does break the cycle, and all that does: **inventory** (`T-C2`), and evaluation
against **published or experimental** anchors (`T-A5b1`, `T-R1`) — anchors that do not descend from
the covariance models. ⚠️ And `T-A5b2` re-closes it in a different way: its positive control
("held-out anchors are recovered") **is** its headline endpoint. Also an operator decision.

---

## 9 · Task count by edge position

**`[REVIEW 01a0bcb2]` recounted after the review.** 54 tasks. ⚠️ **Superseded by §10.6: the register now holds 59.** The table below is the post-review state of 2026-09-20 05:58 and is kept as that record.

| readiness | n |
|---|---|
| `READY_WAITING_OPERATOR` | **31** |
| `BLOCKED_DEPENDENCY` | 13 |
| `LAUNCH_NOW` | 7 — of which **one** has a frozen launcher and passes preflight |
| `CLOSED` | 2 |
| `VOID_REVIEW_FAILED` | 1 |

| population state | n |
|---|---|
| `UNEXPOSED_CONFIRMATORY` | **26** |
| `NO_POPULATION_SPEND` | 19 |
| `EXHAUSTED` | 5 |
| `EXPLORATORY_POPULATION` | 4 |

⛔ **The jump from 5 `UNEXPOSED_CONFIRMATORY` to 26 is the review's central correction.** An earlier
draft read `RT-EXACT-501561`, `RETRON-LOCI` and `NCRNA-16458` as spent because they are marked
`INSPECTED`. **The ledger says the opposite** — each `can_serve_as_confirmation`, so each is an
*unexhausted confirmatory-capable* population, and `WORKING_RULES` §4a requires **one explicit
operator authorisation per launch** for those. Twenty-one tasks moved to
`READY_WAITING_OPERATOR` as a result.

### The corrected edge types

| edge | was | is | why |
|---|---|---|---|
| `T-P1 → T-N2` | `HARD` | **`SOFT_INTERPRETIVE`** | `PROGRAM_LAUNCHER` §4: S06 functional identity *benefits from* S03a |
| `T-P1 → T-P3` | `HARD` | **removed** | `T-P3` overlaps `T-P1`'s own groupings; it needs a non-duplicative deliverable or should merge into it |
| `T-C1 → T-A16` | `DATA` | **removed** | `T-A16`'s launcher declares no such input; its real blocker is an unspecified control and statistic |
| `T-REG4 → T-S1` | `DATA` | **removed** | structures were already one of the five swept kinds |
| `T-S1 → T-S2` | `DATA` | **removed** | CATH and the deposited complexes are already registered |
| `T-AUDIT2 → T-GATE1` | absent | **`DATA`** | added |
| `T-REG3, T-REG4 → T-REG2` | absent | **`DATA`** | added |

Only **one** of the four original `HARD:T-P1` edges survives review as genuinely hard:
**`T-A0b`**, and only if the partition is demonstrably not nested in components — which is the
question `T-P1` exists to answer.


---

## 10 · DELTA — Execution Batch 02 and the reconciliation pass

**Added 2026-09-20 by the reconciliation session.** §§0–9 above are the reviewed structure and are
kept verbatim. This section records every node whose **state** changed, and the five nodes added.
**No edge type in §§0–9 is revised.**

### 10.1 · The trunk is still empty, and that is the single most consequential fact

§1 names `T-P1-relatedness-backbone` as *the only real trunk*. **`T-P1` is `VOID`** — its controls
never gated, two never ran, and the controls contaminated the primary input. Its Ibex job
`52124966` COMPLETED with exit `0:0`; **the job ran and the task is void**, and those are different
things.

```
   Stage 1 corpus ──▶ T-P1b-identity-partition   [READY_WAITING_OPERATOR, no launcher]
                            │
                            └── still the shared prerequisite for T-A0b, T-F3, T-N2
```

`ERRATUM_02` changed the *reason* `T-A0b` is blocked, and the change matters:

- **The old reason was a tautology** — "the 50 % grouping nests inside the component unit".
  `ERRATUM_01` asserted it and was **itself false**.
- **The measured fact:** a full-catalogue 50 % clustering **does** cross components — 134 clusters,
  largest spanning 12, 8,941 paired RTs — while the old frozen groups span **0 of 2,455**.
- **The live blocker** is therefore *multi-membership*: components hold multiple RT lineages, so a
  lineage-blocked interval needs a **multiway / incidence-graph design**, not a nested one.

`T-A0b` is `HELD_SCIENTIFIC_DEPENDENCY` for a real reason now, not a false one.

### 10.2 · Node state changes

| node | was | is | why |
|---|---|---|---|
| `T-C1-rt-core-extraction` | `READY_WAITING_OPERATOR` | **`SUPERSEDED`** | REJECT `01a0bdfa`; replaced by `T-C1b` |
| `T-C1b-pf00078-envelope-census` | — | **`DONE_AWAITING_REVIEW`** | frozen at `c77adb9`, 4/4 controls PASS |
| `T-P1-relatedness-backbone` | `READY_WAITING_OPERATOR` | **`VOID_SUPERSEDED`** | controls never gated; `ERRATUM_01` false |
| `T-P1b-identity-partition` | — | **`READY_WAITING_OPERATOR`** | the trunk, rebuilt; no launcher yet |
| `T-N1-neighbourhood-extraction-qa` | `READY_WAITING_OPERATOR` | **`SUPERSEDED`** | REJECT; population misdeclared |
| `T-N1b` / `T-N1c` | — | **`VOID`** / **`VOID_ESCALATED`** | each stopped by its own blocking control |
| `T-N1d-neighbourhood-census` | — | **`BLOCKED_OPERATOR_CONTROL_DESIGN`** | see §10.3 |
| `T-F1-motif-scan` | `LAUNCH_NOW` | **`DONE_AWAITING_REVIEW`** | executed without a freeze; unreviewed |
| `T-M1`, `T-S1` | `LAUNCH_NOW` | **`DONE_CHANGES_PENDING`** | `ACCEPT_WITH_CHANGES`, changes unapplied |
| `T-REG3-content-hash-pass` | `LAUNCH_NOW` | **`DONE_AWAITING_REVIEW`** | executed without a freeze; unreviewed |
| `T-A23c-source-data-retrieval` | `READY_WAITING_OPERATOR` | **`DONE_ERRATUM_REQUIRED`** | executed; source identity unverified (`ERRATUM_01`) |
| `T-A23d-primary-verification` | `READY_WAITING_OPERATOR` | **`READY_FOR_OPERATOR_REVIEW`** | scope redefined; absorbs the A23c erratum |
| `T-S2-foldseek-calibration` | `READY_WAITING_OPERATOR` (resource) | **`READY_FOR_OPERATOR_REVIEW`** | **foldseek is installed and registered**; the block was false |

### 10.3 · A new edge type is needed, and `T-N1d` is why

`T-N1` has now had **three** null designs, each failing differently:

| version | null | result | diagnosis |
|---|---|---|---|
| `T-N1` | shift the RT CDS against **its own** coordinates by 500 kb | `0.000000` "PASS" | ⛔ structurally forced to zero; **could never fail** |
| `T-N1b` | permute anchors **across records** | **0.070506** vs 0.05 | sound control, **ill-posed construction** — coordinates are contig-global and records share contigs |
| `T-N1c` | same-length decoy inside the record's **own** window | **0.284691** vs 0.25 | ceiling estimated from **medians**; the rate is driven by the short-window tail |

⛔ **The repeated failure is evidence about the criterion, not about the locator.** Three blocking
controls passed decisively in `T-N1c`: discrimination `1.000 − 0.285 = 0.715` against a floor of
0.50, anchor uniqueness `3,028,196 / 3,028,196`, reproduction `31,504 / 31,504` against a landed
column. **The locator works and position matters.**

`T-N1d` therefore carries a `CONTROL_DEPENDENCY` on an **operator control-design ruling**, which is
a dependency on a *decision*, not on an upstream task. Its launcher must separate:

| implementation / blocking controls | scientific / descriptive outputs |
|---|---|
| exact known-coordinate fixtures | frequency of tight/short windows |
| strand fixtures | edge clipping and its denominator |
| off-by-one fixtures | neighbour-count distributions |
| contig-edge fixtures | family-specific architecture |
| deliberately incorrect-anchor fixtures | **the observed ~0.285 null/population rate, reported not gated** |
| reproduction of landed examples | |

⚠️ **Population-derived architecture must not be forced to satisfy an arbitrary ceiling in order to
validate the locator**, and **no new pass threshold may be derived from the already-observed data
and then treated as preregistered.** If a quantitative blocking threshold is still scientifically
necessary, it must be calibrated **independently**, before the run.

### 10.4 · §8's cycle warning gains a second instance, in a new substrate

§8 records one place a cycle threatens — `CM-CALLS` scored against `CM-CALLS`. Batch 02 produced a
structurally identical failure in **bibliography**: `T-A23c` resolved four references by keyword
match and its controls could not tell a **wrong** match from **no** match.

> **Generalised, and this is the rule to carry forward:** a control that establishes only that the
> instrument *returned something* cannot establish that it returned *the right thing*. It holds for
> a covariance model scored on its own calls, for a search that matches a title, and for the three
> null constructions above.

### 10.5 · §6 closed branches — unchanged, and none reopened

`S09`, `S07`, the palm/fingers/thumb partition, the 11-clade placement and neighbourhood-as-detector
all stand exactly as §6 records them, with their reopening conditions intact. **Nothing in Batch 02
or this reconciliation touches any of them.** `T-N1d` is *description* of neighbourhood geometry and
is explicitly **not** a reopening of neighbourhood-as-detector, which remains a settled negative
(retrons 27th of 41 families, inside a predeclared dead band).

### 10.6 · Recount

| readiness | n |
|---|---|
| `READY_WAITING_OPERATOR` | 26 |
| `BLOCKED_DEPENDENCY` | 13 |
| `LAUNCH_NOW` | 4 |
| `DONE_AWAITING_REVIEW` | 3 |
| `SUPERSEDED` | 2 |
| `READY_FOR_OPERATOR_REVIEW` | 2 |
| `DONE_CHANGES_PENDING` | 2 |
| `CLOSED` | 2 |
| `VOID` / `VOID_SUPERSEDED` / `VOID_ESCALATED` / `VOID_REVIEW_FAILED` | 4 |
| **total** | **59** |

| population state | n |
|---|---|
| `UNEXPOSED_CONFIRMATORY` | 22 |
| `NO_POPULATION_SPEND` | 19 |
| **`INSPECTED_FOR_ENDPOINT`** | **9** |
| `EXHAUSTED` | 5 |
| `EXPLORATORY_POPULATION` | 4 |

**`INSPECTED_FOR_ENDPOINT` is new**, and it is the operator ruling of 2026-09-20 §1 arriving in the
register: nine task-rows now carry an exposure scoped to *one analysis family*, not to a whole
dataset. Four moved out of `UNEXPOSED_CONFIRMATORY` because their endpoint was spent — including by
runs that were rejected or void.
