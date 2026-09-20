---
record: T-N1c-ESCALATION-01
task_id: T-N1c-neighbourhood-census
date: 2026-09-20
kind: ESCALATION — STOP, operator decision required
state: VOID
prerun_commit: b27014755e6cc93310d7dbadf30f8bae13787540
---

# T-N1c · ESCALATION — three null designs have failed, and I am stopping

**`T-N1c` is `VOID`.** `N1c_NEG_random_position` returned **0.284691** against a declared ceiling of
**0.25**. Per the operator ruling §3 that is a STOP. **The ceiling is not raised.**

**This is the third null design for this one control, and I am not writing a fourth.** That is the
unbounded-iteration hazard this programme was built around, and the point at which §6 requires
escalation rather than another attempt.

---

## The three attempts, and what each one taught

| version | null construction | result | why it failed |
|---|---|---|---|
| `T-N1` | shift the RT CDS against **its own** coordinates by 500 kb | 0.000000 "PASS" | ⛔ **structurally forced to zero.** For ordinary gene lengths it cannot overlap. It could never have failed, so its pass meant nothing |
| `T-N1b` | permute anchors **across records** | **0.070506** vs 0.05 → FAIL | the control was sound and the *construction* was ill-posed: CDS coordinates are contig-global and records share contigs, so permuted anchors land in shared space |
| `T-N1c` | same-length decoy placed uniformly in the record's **own window** | **0.284691** vs 0.25 → FAIL | the geometric estimate `2L/W ≈ 0.125` used **medians**. The rate is driven by the short-window tail, where `span − L` leaves the decoy almost no room |

**Each failure was informative and none was a defect in the locator.**

## What is actually established, and it is not nothing

⚠️ **The discrimination control PASSED, decisively:**

> `N1c_POS_discrimination` — true-anchor recovery **1.000000** minus decoy recovery **0.284691**
> = **0.715309**, against a declared floor of 0.50.

And the other two blocking controls passed exactly:

- `N1c_POS_anchor_unique` — 3,028,196 / 3,028,196 = 1.000000
- `N1c_POS_reproduce_n_cds` — 31,504 / 31,504 = 1.000000 against the landed column

**So the locator demonstrably works and position demonstrably matters.** What has failed three
times is my attempt to declare, in advance, a *ceiling on the null rate* — not the instrument.

**0.284691 is itself a useful measured property**: a same-length decoy dropped anywhere in a
record's own window hits the RT CDS **28.5 %** of the time, which says these windows are tight
relative to RT CDS length. That number is worth keeping whatever is decided below.

## ⛔ The decision I need, and why it is not mine

**Is a ceiling on the null rate the right blocking criterion at all, or is the discrimination margin
the criterion?**

| option | argument for | argument against |
|---|---|---|
| **A — margin is the criterion.** Blocking control becomes `true − null ≥ 0.50`; the null rate is **reported, not gated** | it is the scientifically meaningful quantity, it can genuinely fail (a position-blind locator collapses it to 0), and it does not depend on guessing a window-geometry constant in advance | a large margin could coexist with an implausibly high null, and nothing would flag that |
| **B — keep a ceiling, derived properly.** Compute the expected null from the **actual** `L` and `W` distributions rather than medians, declare it, then run | keeps an absolute check on the geometry | I would be deriving the ceiling from the same data the control runs on, one step away from fitting it to the result |
| **C — a different null entirely**, e.g. decoys drawn from matched windows on *other* contigs | avoids both problems | a fourth attempt at the same control, which is what I am declining to do unilaterally |

**I recommend A, with the null rate reported as a measured quantity.** But choosing between A, B
and C is a scientific control-design decision, it is exactly what the operator's standing
authorisation excludes, and I have now been wrong about this control three times. **It is yours.**

## What is NOT blocked by this

The neighbourhood extraction itself is unaffected — `T-N1c` wrote no primary table, by design, and
the gate held. Once the criterion is settled, the run is minutes.

`T-C1b` and `T-A23c` are unaffected and both PASSED.
