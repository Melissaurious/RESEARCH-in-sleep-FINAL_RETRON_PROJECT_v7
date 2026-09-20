---
erratum_id: T-P1-ERRATUM-02
task_id: T-P1-relatedness-backbone
supersedes: ERRATUM_01_not_the_c28_rescue.md (MATERIALLY FALSE — do not cite)
date: 2026-09-20
kind: CORRECTION_OF_A_CORRECTION + VOID
authority: independent review, fresh Codex thread 01a0bdfa, VERDICT REJECT/VOID
job: Ibex 52124966 — VOID, outputs NOT consumable
---

# T-P1 · ERRATUM 02 — my erratum was wrong, and the run is void anyway

**Two separate things went wrong and they point in opposite directions.** Both are recorded because
correcting only one of them would leave a different false statement standing.

---

## 1 · ERRATUM_01 was materially false. Re-clustering at 50 % DOES cross components

ERRATUM_01 said that searching for a 50 %-identity partition crossing PAIR-ELIG components is a
"design tautology", because `CROSSFIT_META.json` records components and RT clusters as built
non-crossing.

⛔ **That conflated two different clusterings.** The frozen `rt_rep` groups used to *build* the
components cannot cross them, by construction. **T-P1 clustered a different and much larger
universe** — 501,561 catalogue RTs rather than the 29,192 paired ones — and the result is not the
same object.

**Independently verified by this session, joining the landed `P1_clusters_id5.tsv` to
`CROSSFIT_MANIFEST.tsv`:**

| quantity | value |
|---|---|
| manifest RTs located in the P1 50 % clustering | 29,192 of 29,192 |
| **P1 50 % clusters spanning ≥ 2 components** | **134** |
| largest span | **12 components** |
| paired RTs inside those cross-component clusters | **8,941** |
| **OLD frozen `rt_rep` groups spanning ≥ 2 components** | **0 of 2,455** |

The old groups span zero, exactly as the tautology argument predicts. **The new clustering spans
134.** ERRATUM_01's further claim that 60–95 % "cannot cross either" is also false: the landed 60 %,
70 % and 80 % levels contain 26, 1 and 1 cross-component clusters.

> **So the finding ERRATUM_01 threw away was real.** A full-catalogue clustering can link components
> that the frozen pairing partition keeps apart, because the catalogue contains RTs the pairing
> population never saw. Whether those links are genuine homology, greedy chaining, or coverage
> artefacts is **unknown and untested** — which is why this does not rescue anything either.

## 2 · ERRATUM_01 also misstated its own timing, and so did the report

ERRATUM_01 says it was "issued before the job landed". **It was not.**

| file | mtime |
|---|---|
| `P1_clusters_id95.tsv` (last output) | **11:36:52** |
| `ERRATUM_01_…md` | **11:37:32** |

**Forty seconds after, not before.** The coordinator's report to the operator repeated the claim.
Both are corrected here. The erratum was written after every cluster table existed.

## 3 · The run is VOID regardless, and this is the larger failure

The launcher declared four blocking controls. **The landed script implements none of them as
gates.** It appends the control sequences to the primary FASTA, clusters, and writes outputs
immediately; the duplicate/shuffled outcomes were evaluated afterwards, by me, outside the script.
`P1_POS_monotone_nesting` and `P1_MUT_battery` **never ran at all**.

**When the missing controls are run, they fail.**

| control | required | observed | state |
|---|---|---|---|
| exact duplicates co-cluster | 100/100 at every level | **98/100** at 40–70 %, 99/100 at 80 %, 100/100 at 90–95 % | ⛔ **FAIL** |
| clusters nest monotonically | every higher level inside the lower | crossings at **every adjacent pair**: 5,658 / 8,932 / 10,115 / 7,104 / 9,805 / 4,821 | ⛔ **FAIL** |
| shuffled decoys never co-cluster | 0/100 | 0/100 | PASS |
| mutation battery | each mutant caught | **never ran** | ⛔ absent |

⚠️ **I reported 98–100/100 as if it were a pass. It is a failed "MUST co-cluster" control.** Two
seeded *byte-identical* sequences landed under different representatives. That is possible for
greedy representative clustering without being a crash — and it means the output **is not an
equivalence relation**, so it may not be used as a nested lineage ladder or as a resampling block.

⛔ **The controls also contaminated the primary run.** Every output has 501,861 rows — the 501,561
catalogue plus 300 control sequences — and some real catalogue members are assigned to `CTL*`
representatives. Filtering the control rows out afterwards does **not** undo their effect on greedy
representative selection. The controls changed the thing they were meant to check.

## 4 · Disposition

**Ibex job 52124966 is `VOID`. No cluster table may be consumed** — not by `T-F3`, not by `T-P3`,
not as an asset, not as a comparator.

The successor is a **new task ID** with, at minimum: controls run as a **separate pilot before** the
catalogue is clustered; controls **never appended** to the primary input; exact-duplicate
co-clustering and input-order stability required and tested; either an algorithm that delivers the
promised nested partition or an explicitly redefined non-nested heuristic task; and a clean
501,561-row assignment plus the cross-cutting/incidence tables.

**It is not launched.** It needs a frozen launcher committed before execution and, because the
cross-component question is now live rather than tautological, an operator ruling on whether a
full-catalogue clustering may inform a lineage design at all.
