---
disposition_id: T-REG-DISPOSITION-01
task_id: T-REG-asset-registration
task_artifact_commit: 9052ccb
governance_base: b5443e1
date: 2026-09-20
kind: PARTIAL_WITHDRAWAL
authority: review-stage/BATCH_ONE_INDEPENDENT_REVIEW_VERDICT.md (FAIL)
board_state: REVIEW_FAILED
---

# T-REG · DISPOSITION 01 — the inventory is kept, the coverage endpoint is withdrawn

The independent review returned **FAIL** on T-REG. Its objection is narrow and it is correct: the
matcher that *defines* the headline coverage number was changed after a first result had been seen,
and the repaired matcher received **no blocking validation**. `REG_controls.tsv` shows this plainly —
`CTL-6 registration matcher specificity` is recorded as `diagnostic`, `blocking = NO`. The two
blocking controls, CTL-1 and CTL-2, validate that the *sweep* finds known-present collections and
that renaming is detectable. **Neither validates the matcher.**

This disposition separates what survives from what does not.

---

## 1 · KEPT — the raw inventory, as an asset

The inventory is a census of files on disk. It does not depend on the matcher, and nothing the
review found touches it. It is preserved and remains usable.

| artifact | what it is | status |
|---|---|---|
| `review-stage/ASSET_SWEEP.tsv` | 20,765 collections, 1,120,868 files, 155,622,173,070 bytes, with a per-collection manifest sha256 | **ASSET — usable** |
| `REG_proposed_registry_rows.tsv` | 18,184 proposed registry rows | **ASSET — proposals only, never applied** |
| `REG_appendix_below_floor.tsv` | 2,581 below-floor collections | **ASSET** |
| `REG_summary_by_kind.tsv`, `REG_summary_by_root.tsv`, `REG_top50_by_bytes.tsv` | descriptive rollups of the census | **ASSET** |
| `REG_pin_collisions.tsv`, `REG_pin_collision_summary.tsv` | 12,646 collections sharing one manifest pin | **ASSET — and a live question**, see §4 |
| `REG_control_positive_registered.tsv`, `REG_control_drift_rename.tsv` | CTL-1 / CTL-2 evidence | **ASSET** |

**Consumable, with a stated limit.** Downstream tasks may read the inventory to *locate* material.
They may not cite it as the size of the project's evidence base: the sweep covers **five file
kinds** (profile, matrix, literature, tree, structure) and contains **no alignment, parquet or
checkpoint entries at all**. 155.6 GB is the size of five kinds. It is a floor.

## 2 · WITHDRAWN — the registry-coverage endpoint

⛔ **The following numbers are withdrawn and may not be cited, reused, restored or defended until a
new frozen task produces them under validated rules.**

| withdrawn value | where it appeared |
|---|---|
| **0.217 %** of collections named exactly by a canonical registry (45 of 20,765) | `REG_registry_coverage.tsv`; `BATCH_ONE_SYNTHESIS.md` §5.2 P4; `COORDINATION_STATE.md` §6 |
| 86.878 % of bytes named at no depth | same |
| 1.024 % of bytes named exactly; 63.833 % named by ancestor only | same |
| 99.961 % (the pre-repair figure) | run log only; retained as disclosure, never a result |

**No existing operator decision preserves this endpoint.** Searched: `docs/decisions/` (41
records), `idea-stage/`, and the tracked tree. The value occurs only in two documents this
coordinating session wrote. There is therefore nothing to supersede — the endpoint simply leaves
the evidence set.

**Why withdrawal and not repair.** The first matcher accepted any ancestor at any depth, so one
mention of a parent path registered 17,833 descendants and the coverage read 99.961 %. The repaired
matcher requires the collection itself, and the coverage read 0.217 %. Those two numbers differ by
a factor of 460 and **the only thing that changed was the rule**. A rule that moves the headline by
460× and is validated by nothing is not a measurement, whichever number it lands on. Keeping the
0.217 % because it is the more conservative of the two would be choosing the answer and then
calling it a result.

## 3 · REQUIRED before the endpoint is admissible

Registered as **T-REG2-registry-coverage-validated** in `programme/ALL_DOWNSTREAM_TASKS.tsv`. Its
launcher is frozen before it runs, and it must carry, as **blocking** controls:

1. **Seeded positive fixture.** A synthetic registry and a synthetic collection tree in which the
   set of exactly-registered collections is **known by construction**. The matcher must recover
   that set with declared precision and recall. This control can fail, and a matcher that matches
   by ancestor fails it.
2. **Adversarial negative fixture.** Collections constructed to tempt a false match — a registered
   parent with unregistered children; a collection whose name is a prefix of a registered one; a
   registered path that no longer exists; a generic token (`tables`, `data`, `cache`) appearing in
   a registry row. The matcher must report **zero** exact matches on all of these.
3. **Mutation check.** The ancestor-matching implementation that produced 99.961 % is retained as a
   named mutant and run against the fixtures. The fixture battery **must fail it**. If the battery
   passes the known-broken matcher, the battery is non-discriminating and the task is `VOID`.
4. **Kind extension.** The sweep is extended to alignments, parquet, checkpoints and any other kind
   named in the extension list, because the present five-kind scope is a stated blind spot rather
   than a measured one.
5. **Content hashing** for the collections in §4, since a name-and-size pin cannot answer the
   question those collections raise.

Until all five are in `PASS`, there is **no registry-coverage number in this project**.

## 4 · Live question the inventory raises and cannot answer

`REG_pin_collision_summary.tsv` records **12,646 collections sharing one manifest pin**. The pin is
computed over file **names and sizes**, so the collision is consistent with genuine duplication and
equally consistent with distinct content. A content-hash pass decides which, and it is a cheap,
population-free job. Registered as **T-REG3-content-hash-pass**.

## 5 · Board consequence

`T-REG-asset-registration` stays `REVIEW_FAILED`. `SCIENTIFIC_OUTCOME` is `DESCRIPTIVE` for the
inventory and **withdrawn** for the coverage endpoint. Downstream tasks may consume the inventory
artifacts in §1 under the §1 limit and may not consume `REG_registry_coverage.tsv`, which is
retained only as the record of what was withdrawn.
