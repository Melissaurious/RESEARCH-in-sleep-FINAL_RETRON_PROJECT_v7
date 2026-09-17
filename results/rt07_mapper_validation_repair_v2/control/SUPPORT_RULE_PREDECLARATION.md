# Support, ambiguity and abstention rule — PREDECLARED PROCEDURE

Date: 2026-09-17. Written **before** `calibrate_support.py` was run. Repairs 3 and 5.

A numeric threshold derived from data cannot be predeclared as a *value*. What is predeclared
here is the **derivation procedure, the complete candidate grid, and the failure condition** —
so the chosen value is auditable and the "smallest working value" error of errata A1 (a grid
that skipped 6 and 7, making "8.0 is the smallest" false) cannot recur.

## 1 · Data that may be used

**Calibration uses construction-family data only:** `Retrons`, `GII`, `DGRs`, `CRISPR`, `UG3`,
`AbiA`.

**Forbidden during calibration:** every G2L object, and **UG25 in its entirety — not inspected
at all**. G2L is development/diagnostic evidence and is excluded from threshold choice for the
same reason UG5 was: its results are already visible, so tuning against them is tuning against
a seen outcome.

## 2 · Negative controls (construction-derived, three kinds)

The previous gate used one kind — a mono-shuffle — three times. That measures one failure mode.
Here, for every calibration sequence:

1. **mono-shuffle** — preserves amino-acid composition, destroys order;
2. **di-shuffle** — preserves *dipeptide* composition (Altschul–Erikson), a strictly harder
   negative: local pair statistics survive;
3. **reverse** — preserves composition *and* all local pair statistics read backwards, and
   retains length and low-complexity structure.

Reversed and di-shuffled sequences are the controls the reviewer asked for. A threshold that
only defeats mono-shuffles is not demonstrated to defeat anything else.

## 3 · The posterior scale

`hmmalign` emits `#=GR <id> PP`. Each character encodes a posterior band; we take its **lower
bound** (`*` → 0.95, digit *d* → *d*/10 − 0.05, `0` → 0.00), so no call is credited with more
confidence than the encoding guarantees.

## 4 · `PP_LO` is fixed by principle, not searched

> **`PP_LO = 0.50`.**

A posterior below 0.5 means the model considers the *alternative* placement more likely than the
one it reported. That is the natural boundary of "a competing mapping is credible", it is not
tuned, and no grid search touches it.

## 5 · `PP_HI` — grid and rule

**Complete grid, exhaustive, no value omitted:**

```
PP_HI ∈ {0.55, 0.65, 0.75, 0.85, 0.95}
```

(These are the only thresholds distinguishable on HMMER's band encoding above `PP_LO`.)

> **Rule: take the SMALLEST grid value at which BOTH hold on construction data —
> (a) the 95th percentile of `MAPPED`-anchor count over all three negative-control classes is
> **0**, and (b) the median `MAPPED`-anchor fraction over real construction sequences is
> **≥ 0.50**.**

If no grid value satisfies both, **FAIL CLOSED**: report, do not widen the grid, do not relax
the targets.

## 6 · `S_MIN` — qualifying-domain bit score

**Complete grid:** `{0, 2, 4, 6, 8, 10, 15, 20, 30}`.

> **Rule: the SMALLEST grid value strictly greater than the maximum best-domain bit score
> achieved by ANY negative-control sequence.**

Reported together with that observed negative maximum, so minimality is checkable.

## 7 · `K_MIN` — minimum supported anchors before a sequence may be called

**Complete grid:** `{1, 2, 3, 5, 10, 15, 20, 30}`.

> **Rule: the SMALLEST grid value strictly greater than the maximum `MAPPED`-anchor count of
> any negative control.**

## 8 · The four per-state calls

| call | condition |
|---|---|
| `MAPPED` | residue present and posterior ≥ `PP_HI` |
| `AMBIGUOUS` | residue present and `PP_LO` ≤ posterior < `PP_HI` |
| `UNSUPPORTED` | residue present and posterior < `PP_LO` |
| `DELETED_STATE` | the match column is a gap |

Only `MAPPED` counts as transfer evidence. `AMBIGUOUS` is reported, never counted.

## 9 · Reason-coded abstention

| verdict | reason |
|---|---|
| `ABSTAIN` | `NO_QUALIFYING_DOMAIN` — best domain bit score < `S_MIN`, or no domain reported |
| `ABSTAIN` | `INSUFFICIENT_SUPPORTED_ANCHORS` — fewer than `K_MIN` anchors `MAPPED` |
| `MAPPED` | `OK` |

## 10 · Numeric, falsifiable criteria for the eventual holdout (repair 5)

Criteria 1, 4 and 6 previously had no boundary a result could cross. They now do:

- **C1 — callability.** Every qualifying component (≥5 sequences) must reach a median
  `MAPPED`-anchor fraction **≥ `T1`**, where `T1` = the **5th percentile** of per-sequence
  `MAPPED` fraction across all construction families, truncated to 2 decimals.
- **C4 — no collapse.** The absolute difference between the median `MAPPED` fractions of the two
  qualifying components must be **≤ `D_MAX`**, where `D_MAX` = the observed spread between the
  highest and lowest construction-family medians, rounded up to 2 decimals.
- **C6 — decoy separation.** Required: `max` negative `MAPPED`-anchor count **<** `min` real
  `MAPPED`-anchor count among non-abstaining sequences, **and** the negative 95th percentile
  **= 0**.

All three are computed from construction data and frozen before the holdout is touched. Each can
be **violated by a result**, which is what criteria 1/4/6 previously could not be.

## 11 · Freeze

On completion the values are written once to `control/SUPPORT_RULE_FROZEN.tsv`, hashed into the
bundle manifest, and not revisited. Any later change requires a new decision record.
