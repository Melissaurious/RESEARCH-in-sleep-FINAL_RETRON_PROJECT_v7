# C6, empty-control and di-shuffle-failure policy — PREDECLARED

Date: 2026-09-17. Repair 6. Written **before** UG25 is opened; **no UG25 object has been
materialised** by any script in this bundle (enforced by `scoped_loader.py`, tested by
`loader_equivalence.py` L2/L3).

Every number below is derived from construction data or fixed by fiat **now**. None may be
revised after UG25 is seen.

## 1 · The problem being fixed

v1's C6 read: *"max negative `MAPPED` < min real `MAPPED` among non-abstaining, **and** the
negative 95th percentile = 0"* — with the percentile computed **pooled** across all three
control classes. Measured on construction data at the frozen `PP_HI = 0.75`:

| class | n | p95 | max |
|---|---|---|---|
| mono-shuffle | 219 | 0 | 17 |
| di-shuffle | 216 | 0 | 24 |
| **reverse** | 219 | **10** | 25 |
| **pooled** | 654 | **0** | 25 |

The pooled p95 of 0 **conceals** a reverse-class p95 of 10. Pooling 654 values where two thirds
are near-zero guarantees the third class cannot move the statistic.

## 2 · C6 is evaluated PER CLASS. A single class failing fails C6.

> **C6 PASS requires, for EVERY control class independently (`MONO`, `DI`, `REV`):**
> **`max(class MAPPED-anchor count) < min(real MAPPED-anchor count among non-abstaining
> sequences)`.**
>
> **If any one class violates this, C6 FAILS — regardless of the pooled statistic.**
> Pooled figures are reported but are **never** the pass condition.

This is the operator's explicit question answered in advance: **one class violating while
pooled passes is a FAIL.**

Margin on construction data, for reference: the strongest negative reaches **25**, and `K_MIN = 30`
means a non-abstaining sequence has at least **30** `MAPPED` anchors. The separation margin is
**5 anchors**. It is real but not comfortable, and it is stated now rather than discovered later.

## 3 · p95 is REPORTED, not a pass condition — and why

A per-class requirement of `p95 = 0` would be **unpassable**: the reverse class already reaches
p95 = 10 on construction data, where the mapper is working correctly. Making it a criterion
would not be a strict test, it would be a guaranteed failure that says nothing about UG25.

> **Per-class and pooled p95 are reported in every control table. Neither is a C6 pass
> condition.** A class whose p95 exceeds 0 must be named explicitly in the summary.

## 4 · Minimum valid replicates, and the empty case

Design: **3 replicates × each eligible UG25 sequence × 3 classes.** UG25 has **28** eligible
sequences (feasibility figure from the pre-existing candidate audit — no mapping performance),
so each class expects **84** replicates.

> **`MIN_REPLICATE_FRACTION = 0.90`** → each class must yield **≥ 76** valid replicates.
>
> - **A class with ZERO valid replicates → C6 FAILS CLOSED.** The gate stops. It is not
>   reported as "separation achieved on the remaining classes".
> - **A class below 76 valid replicates → C6 FAILS CLOSED.** Not "proceed with what we have".
> - Absolute floor regardless of fraction: **20** valid replicates per class.

A control class that cannot be generated is a **failure of the experiment**, not a licence to
evaluate without it. This is the `-M a2m` lesson: an absent measurement is not a passing one.

## 5 · Di-shuffle failures are reported, never replaced

The Altschul–Erikson construction legitimately fails when no valid last-edge tree is found. On
construction data this happened for **3** sequences (CRISPR 2, UG3 1).

> - Every failure is **counted**, its **sequence id listed**, and the count carried in the table
>   header and in the summary.
> - A failed di-shuffle is **never** substituted by a mono-shuffle, a reverse, a retry with a
>   different seed, or anything else. The replicate is **absent**, and its absence is visible.
> - Failures count against the §4 minimum. If di-shuffle failures push the `DI` class below 76,
>   **C6 fails closed** — the gate does not proceed on two classes.

## 6 · Reporting requirements

Each control table must carry, per class: `n_attempted`, `n_valid`, `n_failed`, the failed ids,
`max`, `mean`, `p95`, `n_with_any_mapped`. Pooled rows are labelled `POOLED` and may not be
presented without the per-class rows beside them.

## 7 · Falsifiability

C6 as written can be violated by a UG25 result in four distinct ways: any class whose maximum
reaches the minimum real value; any class with zero valid replicates; any class below the
replicate minimum; or di-shuffle failures depleting the `DI` class. The empty-control branch is
exercised by `control_policy_tests.py` (C1–C5) on synthetic inputs.
