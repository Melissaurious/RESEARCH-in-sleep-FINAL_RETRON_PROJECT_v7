# Addendum 1 to the support-rule predeclaration

Date: 2026-09-17. Written **after** the construction-only calibration ran and **before** any
holdout family was touched. **UG25 has not been read.** Nothing here is derived from G2L or UG25.

The predeclaration is **not rewritten**. This addendum records what the calibration exposed.

## 1 · The frozen values

| parameter | value | note |
|---|---|---|
| `PP_LO` | **0.50** | fixed by principle, never searched |
| `PP_HI` | **0.75** | smallest of `{0.55, 0.65, 0.75, 0.85, 0.95}` meeting both targets — **full grid reported** |
| `S_MIN` | **10** | smallest grid value strictly above the observed negative max of **8.1** bits |
| `K_MIN` | **30** | smallest grid value strictly above the observed negative max of **25** anchors |
| `T1` | **0.32** | 5th percentile of per-sequence `MAPPED` fraction across construction |
| `D_MAX` | **0.48** | predeclared C4 bound — see §3 |
| `D_RANDOM` | **0.067** | addendum companion — see §3 |

Minimality of `PP_HI` is **checkable**, not asserted: 0.55 and 0.65 are printed with their
failures (negative 95th percentile 12 and 8, both required to be 0). This is the discipline
errata A1 established after "8.0 is the smallest threshold" turned out to be false because the
grid skipped 6 and 7.

## 2 · The previous decoy design understated the null — materially

Maximum negative `MAPPED`-anchor count at the frozen `PP_HI`, by control class:

| class | what it preserves | worst case |
|---|---|---|
| mono-shuffle | composition | **17** |
| **di-shuffle** | composition **+ every dipeptide count** | **24** |
| **reverse** | composition + all local pair structure + length | **25** |

The G2L gate used **mono-shuffle only**. Had the stronger controls been present, its decoy
ceiling would have been visibly higher. This is why `K_MIN` is **30** and not a token value: a
sequence must beat the strongest observed negative before it may be called at all.

`di_shuffle` failed to find a valid last-edge tree for **3** sequences (CRISPR 2, UG3 1); those
are absent from the DI rows and the table header says so. The count is disclosed rather than
papered over by substituting a mono-shuffle.

## 3 · The predeclared C4 bound is weak, and is kept anyway

`D_MAX = 0.48` is the spread between construction **family** medians (Retrons 0.473 → GII 0.950).
That is a bound on *different families*, applied to two components *within one family*. Almost
nothing could violate it.

The honest measurement of "two groups drawn from the same population" is **`D_RANDOM = 0.067`** —
the 95th percentile of `|median(A) − median(B)|` over 2000 random half-splits of each construction
family. It is **seven times tighter**.

Within-family *component* spread cannot be measured on construction data: only GII, CRISPR and
Retrons have a second component at all, of sizes 1, 4 and 1. So neither number is ideal —
`D_MAX` is too loose, `D_RANDOM` too tight, because true separation components are more divergent
than a random split.

**Decision: the predeclared `D_MAX` remains the C4 pass/fail bound.** Substituting `D_RANDOM`
now would be replacing a predeclared criterion after seeing calibration output, which is the
error that sank UG5 v2. `D_RANDOM` is reported alongside as a **descriptive diagnostic**, so a
result that passes C4 while sitting far outside the same-population null is visible rather than
hidden behind a pass.

**Consequence to state plainly: C4 is a weak criterion. A C4 pass is close to uninformative.**
C1, C6 and the abstention rule carry the evidential weight.

## 4 · What the calibration says about the construction families themselves

Median `MAPPED` fraction at `PP_HI = 0.75`: GII 0.950, CRISPR 0.913, DGRs 0.800, UG3 0.550,
AbiA 0.493, Retrons 0.473.

The frame is **GII-centred**, exactly as the `-M a2m` sensitivity already established. Retrons
and AbiA — the families furthest from GII — sit near half the anchors even under construction
conditions. `T1 = 0.32` is low because it must accommodate them.
