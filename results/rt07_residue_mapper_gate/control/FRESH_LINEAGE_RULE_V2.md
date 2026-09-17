# Fresh-lineage selection rule — SUPERSEDING PREDECLARATION (v2)

Date: 2026-09-17 · Written **before** the mechanical audit was run and **before** any held-out
mapping result was examined.

Supersedes the v1 selection rule recorded in `control/FRESH_LINEAGE_SELECTION_STOP.md`. That record
is not rewritten.

## 1 · Why the v1 rule was insufficient

v1 said: *"among eligible families never used in construction, development, threshold selection or
anchor selection, rank by N descending and take the first with ≥2 separation components."*

It selected **UG7** (N=77, components **76 / 1**). A singleton second component provides **no
meaningful multi-cluster within-lineage challenge**, which was the whole point of requiring
components. The rule encoded the *form* of the requirement and not its *purpose*.

## 2 · The superseding rule

> **A lineage is eligible as a fresh holdout when it has at least 2 sequence components, each
> containing at least 5 eligible sequences**, under the already-registered component definition
> (connected components of the link graph at `identity ≥ 0.30` **and** `min(query_coverage,
> target_coverage) ≥ 0.50`).

**The component-definition method and its thresholds are NOT changed in this task.** Only the
eligibility criterion over the resulting components changes.

This criterion is fixed **now**, before any residue-level transfer performance is examined, and it
restates the original requirement — that the held-out lineage support internal challenge across
meaningfully distinct sequence clusters.

## 3 · Applied mechanically

The rule is applied to **every otherwise-eligible unused lineage** — every family label in the
eligible collection that appears in **none** of: g4a construction, UG5 development, placement-rule
development, threshold selection, anchor selection. No family is excluded for having a small `N`
before the rule is applied; the rule itself decides.

Used, and therefore ineligible: `Retrons`, `GII`, `DGRs`, `CRISPR`, `UG3`, `AbiA` (construction);
`UG5` (development/tuning). The five placement-rule development families are a subset of
construction.

## 4 · Tie-break, declared now

If more than one lineage passes, take, in order:

1. the largest number of components with ≥5 sequences;
2. then the largest `N` in the **second**-largest qualifying component — the binding constraint on
   challenge-set size;
3. then the largest eligible `N`;
4. then the lexicographically smallest family label.

**Mapping outcome may not enter the tie-break, and no candidate is privileged in advance** —
including G2L.

## 5 · Genealogy is a separate gate, applied after selection

Mechanical selection does **not** confer the label "fresh". Whichever lineage is selected is then
audited against the construction families and classified as exactly one of `FRESH_LINEAGE`,
`FRESH_FAMILY_WITHIN_RELATED_LINEAGE` or `NOT_INDEPENDENT`. A `NOT_INDEPENDENT` classification
**stops the gate**.

## 6 · The mapper is frozen

The state→residue algorithm, alignment-path parser, score rule, abstention logic, ambiguity logic,
anchor/state list, HMM construction and decoy logic are **frozen as of this record** and may not be
altered in response to any candidate lineage. An implementation bug found before evaluation may be
repaired only through an explicit audit entry, never tuned against held-out outcomes.

## 7 · Order is not evidence

Monotone state order is an **implementation invariant** of `hmmalign`'s globally colinear model and
is **not** reinstated as a success criterion. It is reported descriptively only.
