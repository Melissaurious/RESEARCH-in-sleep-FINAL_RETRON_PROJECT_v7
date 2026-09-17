# g4a REPAIRED — superseding predeclaration ADDENDUM 1

Written **immediately on detection**, **before** any repaired split was accepted and before any
repaired analysis was interpreted. Required by the audit principle: *a failed predeclared
condition must fail closed unless the governance record explicitly authorises a superseding design
before the affected analysis is interpreted.* This is that authorisation, and it records the
failure rather than hiding it.

## 1 · The predeclared condition that failed

`PREDECLARATION_REPAIRED.md` §2 assumed that assigning whole connected components of the
identity/coverage link graph to roles would yield a valid derivation / development / challenge
split for every family.

**It does not.** Measured at the declared link rule — `identity >= 0.30` **and**
`min(query_coverage, target_coverage) >= 0.50`:

| family | N eligible | components | largest component | split achievable? |
|---|---|---|---|---|
| DGRs | 488 | **1** | **488 (100%)** | **NO** |
| UG3 | 86 | **1** | **86 (100%)** | **NO** |
| GII | 496 | 2 | **495 (99.8%)** | **NO** |
| CRISPR | 129 | 2 | **125 (96.9%)** | **NO** |
| Retrons | 95 | 4 | **92 (96.8%)** | **NO** |
| UG5 | 67 | 4 | 42 (62.7%) | **YES** — 42 / 21 / 3 / 1 |
| AbiA | 19 | 4 | 12 (63.2%) | **YES** — 12 / 3 / 3 / 1 |

**For 5 of 7 families, an independent within-family held-out set does not exist at the declared
separation level.** The sequences of a family form one connected homology component.

Part of this is single-linkage chaining, which is inherent to connected components. The rest is a
property of the data: members of an RT family are mutually homologous throughout, which is what
makes them a family.

## 2 · What is NOT done

**The threshold is not lowered to manufacture a split.** Relaxing `0.30 / 0.50` until the
components fragment would be outcome-driven tuning of a separation rule to obtain a desired
population — the exact class of defect this repair exists to remove. The declared rule stands and
the consequence is reported.

## 3 · Superseding design, authorised here

1. **The link rule is unchanged**: `identity >= 0.30` and `min(coverage) >= 0.50`.
2. **Where a family fragments** (UG5, AbiA), whole components are dealt to roles as declared, and
   the challenge set is `INDEPENDENT_CHALLENGE`.
3. **Where a family does not fragment** (DGRs, UG3, GII, CRISPR, Retrons), no independent
   within-family challenge set exists. For these families:
   - the derivation set is drawn from the single dominant component by a deterministic,
     non-outcome-driven rule — **sort member ids lexicographically, take the first k** — capped at
     the declared proportions and the declared pilot cap of 90;
   - the remaining drawn sequences are labelled **`NON_INDEPENDENT_CHALLENGE`**;
   - **no transfer, generalisation or held-out claim may be made from them.** They may only
     support descriptive statements about the family itself.
4. **The `g4a` transfer estimand is downgraded accordingly.** `G08`/`G10` transfer results are
   reported **only** for `INDEPENDENT_CHALLENGE` sets, and are explicitly marked as covering 2 of
   7 families. The previous bundle's cross-family transfer numbers are retained in the errata and
   are **not** carried into a canonical claim.
5. **The actual maximum derivation↔challenge identity is reported per family**, together with the
   count of pairs at or above 50% identity, so the specific false claim of the original bundle is
   answered with numbers rather than with a rule.

## 4 · Scientific consequence, stated plainly

**This strengthens, rather than weakens, the reviewer's mandate.** The reviewer classified a
whole-family holdout as `B — REQUIRED` because cluster-held sequences from families that all
contributed profiles cannot identify transfer to an unseen family. The measurement above shows a
sharper version of the same point: **for most families, within-family holdout cannot deliver
independence at any defensible separation level**, because the family is one homology component.

The **UG5 whole-family gate is therefore the only valid transfer test available**, not merely the
preferred one.

## 5 · What this does NOT change

The between-family results — correspondence, dyad correspondence, transitivity, supported
intersection, real-vs-decoy separation — are computed from **derivation sequences only** and do not
depend on the challenge split. They are recomputed on the repaired derivation sets and compared
against the original. If that comparison changes the qualitative conclusion materially, work stops
before the UG5 gate and returns to the operator, per `PREDECLARATION_REPAIRED.md` §11.
