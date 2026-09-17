# g4a REPAIRED — superseding predeclaration

Written **before** any split was regenerated and before any repaired alignment was run.
Supersedes `results/rt07_g4a_frame_recovery/control/PREDECLARATION.md` **only** in the sections
named below. Everything not named here is carried forward unchanged.

Authority: independent review `PASS_WITH_REQUIRED_REPAIRS`, score 6/10, recorded in
`review-stage/AUTO_REVIEW.md` and `docs/decisions/2026-09-16_stage2_g4a_review_outcome_and_repairs.md`.

## 0 · Audit principle, binding on this task

Any deviation from a predeclaration, unexpected result, failed assertion, parameter drift, count
mismatch or contradictory canonical output is surfaced **immediately** in the operator report and
recorded in `tables/g4a_repair_audit.tsv` with `expected`, `observed`, `when_detected`,
`scientific_effect`, `repair`, `results_before_repair_invalidated`.

**A failed predeclared condition fails closed.** No affected analysis is interpreted until a
governance record authorises a superseding design.

## 1 · What is NOT changing

Same seven families, same question, same method family. No broadening of the family set, no new
external assets, no redesign of the scientific method. The scientific question is unchanged:
*what shared sequence structure is recoverable de novo from the selected full-length-source RT
families?*

## 2 · Split separation — the repaired rule (REPLACES the cd-hit rule)

The previous rule assigned whole `cd-hit -c 0.50` clusters to roles and **asserted** that no
challenge sequence had a ≥50% relative in derivation. That assertion was **false**: cd-hit compares
each sequence only to cluster representatives, so cross-cluster pairs may exceed the threshold.
Verified violations: DGRs 17/26 challenge sequences (max 72.97%), CRISPR 3/26, GII 0/40.

**Repaired rule, declared here before regeneration:**

1. Within each family, compute **all-vs-all** pairwise `identity`, `query_coverage` and
   `target_coverage` with `mmseqs easy-search` at high sensitivity.
2. Define a **link** between two sequences when
   **`identity >= 0.30` AND `min(query_coverage, target_coverage) >= 0.50`**.
3. **Separation groups = connected components** of that link graph.
4. Assign **whole components** to roles.

Because roles are unions of connected components, **every cross-role pair is guaranteed by
construction** to have `identity < 0.30` OR `min(coverage) < 0.50`. Separation is enforced, not
inferred.

The thresholds are declared now and are **not** tuned afterwards. `0.30 / 0.50` is chosen to be
**stricter** than the 0.50 identity level whose violation was found, so the repaired claim is
stronger than the one that failed.

**Reported regardless of outcome:** the actual maximum derivation↔challenge identity per family,
and the same at the 0.50 level, so the specific false claim is directly answered.

## 3 · Cap enforcement

The original cap of **90** stands and is **not** retroactively redefined. The landed pilot violated
it (GII 111, DGRs 97); that violation is recorded in the audit table, not reinterpreted.

Components are dealt to roles in order of size (descending), then by lexicographically smallest
member id. **A component that would push the family total above 90 is skipped**, and the next
smaller component is tried. Target proportions remain derivation ≈55%, development ≈15%,
challenge ≈30%; `SMALL_FAMILY` (N < 40) remains derivation ≈60% / challenge ≈40% with no
development set.

## 4 · Cluster diversity is reported, and a family may be downgraded

For every family and role: number of independent separation components, and the component-size
distribution. If a role is a single component, that is reported explicitly. **If a family cannot
supply meaningful derivation/development/challenge diversity, its role is downgraded and reported —
the split is not forced.**

## 5 · Canonical dyad result

The corrected direct-alignment parser (`g4a_dyad_check.py` logic) is the **sole canonical** dyad
result. The superseded match-state-derived verdict column is **removed** from the correspondence
table, not merely supplemented. Superseded values survive only in the errata record.

The per-sequence dyad column mapping is repaired: each sequence's dyad is mapped through **its own**
alignment row, not through one reference sequence's coordinate map.

## 6 · Fail-closed external calls

Every `hhalign`, `hmmsearch`, `hmmbuild`, `hhmake`, `mmseqs` and `mafft` invocation uses
`check=True`. A failed comparison is recorded explicitly as a row; no silent empty or partial table
may be produced.

## 7 · The aligner measure is renamed to what it computes

The previous `entropy_delta_vs_MUSCLE` / "cross-aligner stability" measure compared per-column
entropies, not residue-set stability. It is renamed
**`per_column_entropy_difference_MAFFT_vs_MUSCLE`** and is described as a *method-sensitivity
diagnostic*, never as homology evidence or coordinate stability.

## 8 · Denominators are always named

`pct_global_of_covered` (positions aligned to any partner) and
`pct_global_of_full_consensus` (full HHM consensus length) are **both** reported. Neither is quoted
without its denominator.

## 9 · Categories renamed away from biological language

`CLASS_LEVEL` becomes **`MULTI_FAMILY`** — it means "aligned to 2 to n-1 partner families" and
carries no biological-class claim. No predefined biological class was tested. `GLOBAL_CANDIDATE`
becomes **`ALL_PARTNERS`** for the same reason; "global" is reserved for the seven tested families
and always qualified.

## 10 · Parameter registry

The five previously undeclared parameters — the 250 aa floor, `hhmake -M 50`, `hmmsearch -E 10`,
the ±2 transitivity tolerance and the ≥20-position triple filter — are inventoried in
`tables/g4a_parameter_registry.tsv`, each classified `algorithmic_default` /
`implementation_choice` / `scientific_threshold` / `numerical_convenience`, with justification and,
where it could change a conclusion, a bounded sensitivity test. **No value is tuned to improve the
current outcome.**

## 11 · Comparison against the original

The repaired bundle is compared against the original on: shared-core recovery, pairwise family
correspondence, dyad correspondence, transitivity, shared intersection, retron behaviour, and
real-vs-decoy separation. **If the qualitative conclusion changes materially, work stops before the
UG5 gate and returns to the operator.**

## 12 · Verifier semantics

Input hashes are enforced; verification fails if a registered input differs. Execution goes to a
fresh temporary location; comparison is against frozen canonical outputs; non-zero exit on drift;
canonical outputs are never overwritten. **The regeneration mode is moved out of the verifier into
a separate script** so verification cannot bless changed code or inputs.
