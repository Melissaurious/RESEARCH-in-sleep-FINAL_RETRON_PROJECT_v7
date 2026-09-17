# Current supportable scientific claim

## The claim

> Under the tested `hhmake -M 50` / `-M 60` match-state conventions, a compact **GII-centred**
> shared RT correspondence frame is recoverable across the six construction families. In those
> construction data the alignment-path mapper produces posterior-stratified residue calls, a
> genuinely reachable ambiguity state, reason-coded abstention, and a stable operational
> catalytic coordinate at **HMM state 262**.

## What it does NOT establish

- **Not robust to the match-state definition.** Under HHmake's documented default `-M a2m`,
  DGRs and AbiA retain **zero** `ALL_PARTNERS` positions while GII retains 115. The `-M 50`
  frame is implementation-dependent and is always reported with the convention named.
- **No independent residue-level accuracy.** Nothing here is validated against an external
  truth set. Posterior stratification is a confidence statement from the alignment model, not
  measured correctness.
- **No confirmatory transfer.** G2L is a *related* GII-like family and is development /
  diagnostic evidence only. No held-out non-GII-like lineage has been evaluated.
- **No family-symmetric or universal shared-core claim.** Withdrawn, and not reinstated.
- **Monotone state order is an `IMPLEMENTATION_INVARIANT`** — `hmmalign` is globally colinear
  by construction — and is never transfer evidence.
- **`BOUNDARY_ACCURACY` and `BOUNDARY_CALIBRATION` remain `UNESTABLISHED`**; there is no RT0
  occupancy; the seven-way partition is unsupported.

## Estimand discipline

| quantity | status |
|---|---|
| alignment-path callability on construction families | `ESTABLISHED` |
| catalytic-state concordance at 262 on construction families | `ESTABLISHED` (207/210 = 0.9857) |
| ambiguity reachability and reason-coded abstention | `ESTABLISHED` (implementation property) |
| residue-mapping **accuracy** | `UNESTABLISHED` |
| transfer to a distant RT lineage | `UNESTABLISHED` — UG25 is sealed and unrun |
| robustness to match-state definition | `REFUTED` for family symmetry under `-M a2m` |

## Construction result

**217 of 219** construction sequences callable under the frozen rule (2 Retrons abstain on
`NO_QUALIFYING_DOMAIN`). The superseded narrative figure **237/239** was an arithmetic error in
a decision record; the tables always read 217/219, and the total is now computed rather than
transcribed. Both values remain visible in the errata trail.

Median `MAPPED` fraction by family: GII 0.950, CRISPR 0.913, DGRs 0.800, UG3 0.550, AbiA 0.493,
Retrons 0.473. The frame is **GII-centred**: the families furthest from GII sit near half the
anchors even under construction conditions.
