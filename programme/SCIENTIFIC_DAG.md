# SCIENTIFIC DAG — the remaining programme, by dependency type

**As of 2026-09-20.** Companion to `programme/ALL_DOWNSTREAM_TASKS.tsv` (53 tasks) and
`programme/PARALLEL_EXECUTION_PLAN.md` (what runs where, and when).

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
T-AUDIT1-circular-control-sweep ──CONTROL──▶ every task carrying a blocking control
```

⚠️ **`T-AUDIT1` is a control edge onto the whole programme, and it is `LAUNCH_NOW`.** Its question
is the one the reviewer generalised from T-A23: *a positive control whose pass condition is the
headline result is not a control.* Every blocking control in the project is asked the same thing —
**what broken instrument does this catch?** — and `T-LINT2`'s mutation battery is the executed
template for answering it.

⚠️ **`T-A7` is a `CONTROL_DEPENDENCY` that is also `UNEXPOSED_CONFIRMATORY`.** All 19 truth-bearing
chains in `STRUCT-62` are **non-retron**; all 21 retron chains sit in Tier B or C and were never
scored. Tier B is partly design-inspected and therefore not blind. It is operator-only, and it
cannot be auto-launched to unblock `T-S3`.

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
nothing. The DAG breaks the cycle by permitting only three things: inventory (`T-C2`), evaluation
against **published or experimental** anchors (`T-A5b1`, `T-R1`), and leave-one-subtype-out recovery
(`T-A19`). **No edge in this DAG scores a CM-derived call against a CM-derived call.**

---

## 9 · Task count by edge position

| position | n | readiness |
|---|---|---|
| no upstream | 11 | mostly `LAUNCH_NOW` |
| preparation, upstream = landed Stage 1 only | 11 | `LAUNCH_NOW` |
| downstream of `T-P1` by `HARD` | 4 | `BLOCKED_DEPENDENCY` until the partition exists |
| downstream by `CONTROL` | 3 | blocked by design |
| downstream by `PROMOTION` only | 3 | **runnable now**; only the claim waits |
| operator-gated by population or by an undeclared number | 20 | `READY_WAITING_OPERATOR` |
| closed | 2 | recorded, not scheduled |
