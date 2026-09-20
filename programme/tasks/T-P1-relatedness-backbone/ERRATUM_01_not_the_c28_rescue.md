---
erratum_id: T-P1-ERRATUM-01
task_id: T-P1-relatedness-backbone
date: 2026-09-20
kind: SCOPE_CORRECTION
authority: independent scientific review, fresh Codex thread 01a0bde9, ACCEPT_WITH_CHANGES
issued: WHILE THE JOB WAS STILL RUNNING (Ibex 52124966)
---

# T-P1 · ERRATUM 01 — this is catalogue preparation, not the C-28 rescue

**Issued before the job landed, deliberately**, so that nobody reads its output as the missing
lineage test. Ibex job `52124966` continues; its *purpose* is corrected here.

## What the launcher claimed, and why it was wrong

The launcher said T-P1 would produce "a lineage partition that is not nested inside the component
unit", and that `T-A0b` would then compute the missing 50 %-identity interval for C-28.

⛔ **At the 50 % level, non-crossing is a design tautology, not a discovery.** Verified directly in
the upstream bundle's own metadata:

> `CROSSFIT_META.json` — *"component, RT cluster and ncRNA cluster all verified **non-crossing**"*

The components were **built** so that 50 %-identity RT clusters do not cross them. Re-clustering at
50 % and finding no cross-cutting partition therefore discovers nothing; it restates a construction
choice. And if the ladder is nested, 60–95 % only refine the 50 % groups, so they cannot cross
either. **Only the 40 % level could plausibly merge components — and that is a different lineage
definition, not the analysis the review asked for.**

## A second defect, independent of the first

A component can contain several RT clusters: only **879 of 1,075** components hold a single homolog
group (`A0_block_structure.tsv`, `summary/all/n_components_single_homolog_group`), so 196 hold more
than one. **A partition over RTs therefore does not induce a partition over components.** Once a
component belongs to several lineage clusters the dependence is multi-membership — graph-shaped, not
block-shaped — and forcing it into one block recreates exactly the "dominant type" approximation
T-A0 already used.

## What T-P1's output IS good for

It remains worth having, and the job is not cancelled:

- a **cascaded identity partition of 501,561 exact RTs** at seven declared thresholds, a reusable
  registered asset that does not exist in this project today;
- input to `T-F3` (feature contrast), `T-P3` (relatedness representation) and any lineage-aware
  descriptive work;
- a **component–lineage incidence graph**, which is the object a multiway or similarity-kernel
  analysis would actually need.

## What it may NOT be used for

⛔ It **may not** be presented as producing a non-nested partition.
⛔ A finding of "no level cross-cuts" is **not** a biological bound. The only valid statement is:

> *Under this sequence set, this clustering algorithm, this coverage rule and thresholds 40–95 %, no
> cluster links two PAIR-ELIG components.*

That is a statement about a construction and an algorithm. It does not mean no biological lineage
partition exists, and it does not close C-28 — it closes only the simple one-dimensional
block-bootstrap route.

⛔ **No threshold may be selected after seeing a downstream interval.** All seven levels are
reported; none is promoted.

## Board consequence

`T-P1` stays `PREPARATION`. The `HARD_SCIENTIFIC_DEPENDENCY` edge `T-P1 → T-A0b` is **withdrawn**:
T-P1 does not unblock T-A0b, because the analysis T-A0b needs is not a block bootstrap over a nested
partition. `T-A0b` is re-registered as requiring a **multiway / incidence-graph** design, which is a
new scientific specification and therefore `READY_WAITING_OPERATOR`.

**Nothing on the exhausted PAIR-ELIG population can restore confirmation for C-28.** That needs a
prospective population declared in advance, which is an operator decision.
