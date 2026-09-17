# g4a repaired vs original — does the qualitative conclusion survive?

Required by `PREDECLARATION_REPAIRED.md` §11: *if the qualitative conclusion changes materially
after repairs, stop before the UG5 gate and return to the operator.*

## Headline

**The qualitative conclusion survives.** A compact shared RT core is recoverable de novo across
the tested families; a universal full-protein frame is not supported. Every load-bearing
measurement reproduces in kind, and the one that moved materially moved in the **honest**
direction.

## Side by side

| quantity | original g4a | repaired g4a | survives? |
|---|---|---|---|
| dyad correspondence | 42/42 `DYAD_CORRESPONDS` | **42/42 `DYAD_CORRESPONDS`** | **YES — identical** |
| between-family correspondence | 42/42 pairs align | **42/42 pairs align, 0 failures** | **YES** |
| hhalign probability range | 74.2 – 100.0 | **16.2 – 100.0** | **kind survives; range widened downward** |
| best E-value | 2E-53 *(4.8E-42 was misreported)* | **9.3E-78** | YES — stronger |
| transitivity, mean | 88.2% *(84.9% on exact recomputation)* | **87.0%** | **YES** |
| transitivity, triples ≥80% | 174/210 (83%) | **160/210 (76%)** | YES |
| shared core, % of covered | 18.9 – 57.3% | **22.0 – 47.9%** | **YES — still a minority** |
| shared core, % of full consensus | *not reported* | **7.5 – 27.5%** | CORRECTED 2026-09-16 (errata A7): originally printed 7.7-44.9%, which came from counting HHM rows instead of parsing LENG |
| decoy separation | real 74.2–100 vs decoy 0.0–4.3 | **real 16.2–100 vs SHUF 0.0–0.4, REV 0.1–17.4** | **YES** |
| retron handling | same rules as other families | **same rules** | YES |

## The one material change, and why it is honest

**Minimum correspondence probability fell from 74.2 to 16.2.** The weak pair is **UG5 → AbiA
(16.2)**, with the reciprocal **AbiA → UG5 at 69.2** — a strongly asymmetric pair between the two
smallest and most divergent families.

This is a **consequence of the repairs, not a degradation of the science**:

- the cap is now enforced, so GII dropped 111 → 90 and DGRs 97 → 90;
- five families now use a deterministic draw rather than cd-hit component dealing.

Different derivation sets produce different profiles. The original 74.2 floor was computed on
populations that violated the declared cap. **The repaired floor is the honest one.**

The same asymmetry appears in transfer: AbiA profile → UG5 challenge gives a median best bit score
of **−1.5** with only 5 of 21 detected, and UG5 → AbiA gives **1.8**. The two most divergent
families do not transfer to each other. That is a real, reportable limit of the shared core.

## Transfer is now reported for 2 of 7 families only

Per `PREDECLARATION_ADDENDUM_1` §3.4, transfer is reportable only where the challenge set is
`INDEPENDENT_CHALLENGE` — **UG5 and AbiA**. Every other family's challenge rows are marked
`NOT_REPORTABLE_challenge_set_is_not_independent`.

Reportable SELF: UG5 **342.8**, AbiA **94.6**. Reportable CROSS: **−1.5 to 53.9**.

## Sensitivity of the one genuinely free parameter

Transitivity tolerance sweep — pooled consistency: **±0 → 82.5%**, ±1 → 87.0%, ±2 → 88.9%,
±3 → 91.7%, ±5 → 94.5%. **The conclusion does not depend on the ±2 choice**: even at exact
coordinate agreement, consistency is 82.5%. The ≥20-position triple filter excludes **zero** of 210
triples and is inert.

## Verdict

**Proceed to the UG5 whole-family-holdout gate.** No material change in the qualitative
conclusion; the changes that did occur make the claims weaker and more accurate, which is the
intended direction of a repair.
