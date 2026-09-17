# Fresh-lineage selection — AUDIT ITEM, and a decision returned to the operator

Surfaced immediately on detection, before any fresh-lineage evaluation was run.

| field | content |
|---|---|
| **expected** | the predeclared rule — *"among eligible families never used in construction, development, threshold selection or anchor selection, rank by N descending and take the first with ≥2 separation components"* — selects a lineage that also satisfies the operator's §6 criterion *"ability to reserve multiple independent sequence clusters"* |
| **observed** | it does not. Measured at the declared link rule (`identity ≥ 0.30`, `min(coverage) ≥ 0.50`): |

    UG8    N=83  components=1   sizes=[83]            <- fails the >=2 rule
    UG17   N=78  components=1   sizes=[78]            <- fails
    UG7    N=77  components=2   sizes=[76, 1]         <- FIRST to pass the literal rule
    G2L    N=51  components=4   sizes=[40, 9, 1, 1]   <- the only usable multi-cluster structure
    UG4    N=45  components=1   sizes=[45]            <- fails

| field | content |
|---|---|
| **when_detected** | fresh-lineage selection, **before** any residue mapping of a held-out lineage |
| **scientific_effect** | applying the rule **literally** selects **UG7**, whose second component is a **singleton**. That cannot support an evaluation-reference / challenge split into independent clusters, so the gate would have no independent within-lineage challenge structure — the identical defect that sank the g4a within-family holdouts. The only candidate with real multi-cluster structure is **G2L**, but G2L is *group-II-like* and therefore **genealogically adjacent to GII, which is in construction** |
| **repair** | **none applied. Work stopped.** Choosing G2L over the literal rule after seeing component structure would be a post-hoc selection change; choosing UG7 knowingly accepts a holdout that cannot provide independent clusters. Neither is this session's call |
| **results_before_repair_invalidated** | **NO** — nothing downstream was run |

## The decision

**Option 1 — UG7, the literal predeclared rule.** N=77, components 76/1. Honest to the
predeclaration, but the "challenge set" would be a **single sequence**, so within-lineage
independence is unavailable and the gate tests only whole-lineage transfer, not cluster-held
transfer.

**Option 2 — G2L, the only real multi-cluster candidate.** N=51, components 40/9/1/1 — an
evaluation-reference of 40 and a challenge of 11 across three components. But a **provenance audit
against GII is mandatory first**: G2L is group-II-like, and if its sequences are close relatives of
GII construction sequences the "fresh" label is false. This also changes the selection rule after
seeing structure, which must be recorded as such rather than presented as the original rule.

**Option 3 — relax the rule prospectively**, e.g. "≥2 components each of size ≥ 5", and re-apply.
Under that rule only **G2L** qualifies, reaching the same lineage by a stated rule rather than by
preference. This is the cleanest route **if** the GII provenance audit clears.

## Recommended default

**Option 3**, conditional on the G2L↔GII provenance audit. It reaches a usable lineage through an
explicitly restated rule instead of a silent override, and it keeps the "multiple independent
clusters" criterion the operator specified. **Not taken unilaterally**: it changes a predeclared
selection rule, and the genealogical adjacency of G2L to a construction family is a scientific
judgement about what "fresh" means.

## State

Repairs A, B and C are **complete**. The residue mapper is **built and validated**. Only the
held-out-lineage evaluation is blocked, on this one decision.
