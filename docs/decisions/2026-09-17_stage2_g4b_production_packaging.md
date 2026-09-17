# DECISION — g4b: the validated mapper frozen as a production instrument

Date: 2026-09-17 · Track `rt07` · Stage 2, post-closure · Status: **g4b COMPLETE · g5 AUTHORISED TO BEGIN**

Supersede by a new record, never by rewriting.

---

## 1 · What g4b is, and what it is not

g4b is **packaging and operationalisation only**. Stage-2 validation closed at Endpoint A
(`docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md`): UG25 confirmatory transfer
`SUPPORTED`, post-run review `PASS_WITH_REQUIRED_REPAIRS` 7/10, remaining repairs documentary.

Nothing in g4b re-validates the mapper, adds a family, adds a threshold, adds a control or
widens a claim. UG25 was not re-run and not re-scored by the executor. No Stage-1 catalogue
pass ran; g5 remains unexecuted.

**Governance note for the operator:** `g4b` is **not** a gate in the launcher's gate table
(`launchers/LAUNCHER_02_rt0_rt7_definition.md` §"gate id"), which runs g1–g4 then g5–g7. It
is an operator-defined packaging step satisfying the launcher's own ordering requirement that
"`g4` must be frozen before `g5`". It produces no claim-bearing number, so it needs no `FULL`
gate row; if the operator wants it to carry one, the launcher needs an amendment.

## 2 · The production instrument

| | |
|---|---|
| bundle | `results/rt07_g4b_production_mapper/` |
| bundle root | `0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f` (49 files) |
| manifest / pinned root | `review-stage/manifests/RT07_G4B.MANIFEST`, `review-stage/roots/RT07_G4B.root` |
| **compact mapper version** | **`rtmap-1.0.0/53a1e738a19b3896`** |
| instrument sha256 | `53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5` |
| mapper code | `code/rtmap/mapper.py`, sha256 `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` — **byte-identical** to the validation bundle's |
| profile | `GII.deriv.hmm` sha256 `292495a4…`, LENG 471 |
| anchors | 150, `control/FROZEN_ANCHORS.tsv` sha256 `c48315ae…` |
| schema | `rtmap-schema-1.0` |

Frozen and unchanged: `PP_HI` 0.75, `PP_LO` 0.50, `S_MIN` 10, `K_MIN` 30, `T1` 0.32,
`D_MAX` 0.48, `D_RANDOM` 0.067, `CAT_STATE` 262, `hhmake -M 50`, the alignment-path
state→residue correspondence with no endpoint interpolation, the four-way ambiguity logic,
reason-coded abstention, the catalytic rule, and the MONO/DI/REV control interpretation.

Parameters are **read from** byte-identical copies of the frozen control tables and
cross-checked against this project's closure decision; a mismatch in either place fails
closed. `CAT_STATE` 262 is not one of the 150 anchors, and the two denominators are never
pooled.

## 3 · Two packaging repairs found by the executor

Both concern `hmmsearch`, whose E-values scale with database size and whose default reporting
threshold is an E-value.

* **P1** — the reported domain E-value moved with shard size (`AFZ52119.1_GII`: `2.1e-130` at
  an effective database of 100, `1.2e-129` at 560; bitscore identical at 428.1).
* **P2** — whether a marginal domain was reported at all moved with shard size
  (`YP_217686.1_Retrons`: bitscore −0.6 reported at 100, absent at 560).

**Repair:** production scores domains one sequence at a time, so database size is always 1.
`domain_scores` is the frozen function called with a one-sequence FASTA; no frozen code,
threshold or rule changed.

**Evidence it changed nothing on the calibration population**
(`tables/g4b_domain_scoring_repair_evidence.tsv`): over the complete 219-sequence
construction population, batched (the frozen pipeline's own one-call-per-family-of-40
geometry) against per-sequence — 219/219 reported in both arms, 0 reported only per-sequence,
0 reported only batched, 0 bitscore differences, **0 qualifying-domain verdict flips**. The
independent reviewer additionally checked UG25 read-only and reported 0 bitscore and 0 verdict
differences on all 28 records at database sizes 28, 588 and 1341.

**An executor overclaim, withdrawn.** The first draft justified the repair by asserting a
sequence at or just above `S_MIN` = 10 could vanish at planned Stage-1 shard sizes. The
reviewer measured the closest case — `CBK99617.1_Retrons`, bitscore 10.3 — at E = 0.0062
(560 records) and E = 0.015 (1341), three orders of magnitude below the E ≤ 10 cutoff. **The
claim is withdrawn.** The repair is retained on the narrower ground that a value a production
record carries must not depend on its shard-mates, which P1 demonstrates directly.

## 4 · Independent packaging review, and five required repairs

Reviewer: Codex `gpt-5.6-sol`, xhigh, read-only.
Request: `review-stage/DESIGN_REVIEW_REQUEST_g4b_packaging.md`.

**Round 1** (thread `01a0afd9-39e8`): `PASS_WITH_REQUIRED_REPAIRS`, **6/10**,
**g5 may NOT begin**, five REQUIRED findings. Every one was a genuine packaging defect
demonstrated by the reviewer with a reproduction, not a style objection. All five were
repaired under the anti-churn rule — repair packaging, verify no scientific behaviour changed.

| # | defect, as demonstrated | repair |
|---|---|---|
| R1 | the instrument digest bound neither the runner, nor the bundle, nor the eligibility rule, nor the domain-scoring protocol — a wrapper silently reverting to batched `hmmsearch` would keep identifier `…/46aa95cb0e197b40` | digest now includes `instrument_tree_sha256` over `code/`+`control/`, `eligibility_rule`, `domain_scoring_protocol`; `tables/` excluded so landing an output does not change the instrument; `--pinned-root` verifies the whole bundle before any record is emitted and provenance records it |
| R2 | with one identifier carrying two different sequences, which survived depended on input order; `rt_hash` sharding split them across shards where both passed the local check | every occurrence of a conflicting identifier is rejected (`DUPLICATE_SEQUENCE_ID_CONFLICT`) — order-independent by construction; identical repeats kept once and logged; `--reject-ids` carries a global census; g5 shards by `sequence_id` |
| R3 | on a mapper failure, an alias sharing the sequence received neither a scientific row nor a failure row | every alias gets a `TOOL_FAILURE` row, and the shard **fails closed** unless every valid input identifier appears exactly once across `sequences.tsv` and the `TOOL_FAILURE` rows |
| R4 | an empty `probe.DONE` skipped a shard that had produced nothing | the sidecar carries input sha256, instrument digest and every output hash; a shard is skipped only if all verify |
| R5 | `AMBIGUOUS_MAPPING` used an invented predicate, `n_ambiguous + n_unsupported > n_mapped`, not a frozen rule, able to fire with zero `AMBIGUOUS` calls | removed. The status is now a relabelling of the frozen `(verdict, reason)` pair plus the frozen `T1` — a bijection onto the frozen reason codes, failing closed on an unmapped pair |

R1 deliberately changed the compact identifier from `rtmap-1.0.0/46aa95cb0e197b40` to
**`rtmap-1.0.0/53a1e738a19b3896`**. That is the repair working, not drift.

**Proof the repairs changed no science** (`tables/g4b_repair_no_science_change.tsv`): the
smoke products landed before the repairs, diffed column by column against the same products
regenerated after them on identical input — `smoke_states.tsv` (2850 rows) and
`smoke_sequences.tsv` (19 rows) differ in **`mapper_version` only**; `smoke_failures.tsv` also
in `detail`, free text reworded by R2. Smoke check S1 still reproduces all 18 landed frozen
construction results exactly, and S2 still reproduces 2850 per-state calls against the frozen
mapper imported from the validation bundle.

**Round 2** — see §7.

## 5 · Executor overclaims corrected

All identified by the reviewer, all corrected in place rather than reworded away:

| overclaim | disposition |
|---|---|
| a bitscore near `S_MIN` could vanish at planned shard sizes | **withdrawn**; the repair is rejustified on P1 grounds (§3) |
| "strictly more inclusive" | qualified to **reported domains**, explicitly not verdicts |
| "batch size 1000" | corrected — a configured cap over 560 records, so effective databases were 100 and 560 |
| "provably used the same instrument" | repaired by R1, not reworded |
| "deterministic, order-independent" | repaired by R2 |
| "a valid `DONE` is skipped" | repaired by R4 |
| "no threshold, rule or criterion is introduced" | repaired by R5; now true rather than aspirational |
| the 2.2 / 11.9 / 13.8 ms timing decomposition, from different harnesses and not additive | `smoke/measure_throughput.py` now produces every figure in one run on one substrate and writes the landed table: 1.4 + 11.0 = 12.4 ms sits **below** the 12.9 ms end-to-end total, remainder attributed to startup, I/O and row rendering |
| the 48-core wall projection | labelled as unmeasured arithmetic; only the single-core cost is measured |

## 6 · Documentary errata from the UG25 post-run review, landed non-rewritingly

`UG25_RESULT.md` inside the frozen confirmatory bundle is **not** edited.

* **U1** — `DELETED_STATE` in UG25 was **26.9 %** (1128/4200), not "roughly half". Non-`MAPPED`
  of any kind is 42.9 %. The intended point stands; the number quoted did not support it.
* **U2** — `ug25_gate.py` **does** restate five constants (`LINK_IDENTITY` 0.30,
  `LINK_COVERAGE` 0.50, `MIN_COMPONENT` 5, `REPLICATES` 3, `AGREEMENT_MIN` 0.80). Each matches
  the frozen predeclaration exactly, so this is inaccurate provenance wording, **not** tuning.
* **U3** — post-run root verification was executed as a separate manual command; the runner
  implements only the pre-run check, so §13 of the predeclaration was not satisfied verbatim.

Carried with them: `FRESH_LINEAGE` is an operational classification, not "no evolutionary
relationship"; REV replication is not independent (28 unique reversals × 3); UG25 tested
`-M 50` only; "confirmed" for catalytic placement means motif concordance at a state, not
independent residue truth. The reviewer independently reproduced U1 (26.86 %) and confirmed
U2 and U3.

## 7 · Decision

**Round 2** (`review-stage/DESIGN_REVIEW_REQUEST_g4b_round2.md`, thread `01a0aff7-9be3`):

> **`PASS_WITH_REQUIRED_REPAIRS` · 9/10 · MAY g5 BEGIN: YES**
>
> "The five blocking packaging defects are fixed. The remaining repairs are documentary and
> do not block execution." · R1–R5 each **FIXED**, each re-verified by the reviewer's own
> round-1 demonstration re-run against the repaired code · **Did any science change? NO.**

The reviewer independently confirmed: `mapper.py` byte-identical at `69575dc7…`; 162
scientific-field comparisons across the 18 shared smoke/construction sequences with **zero**
differences; all 2,850 per-state calls matching the directly imported frozen mapper;
`FREEZE INTACT`; `FREEZE TESTS OK`; `SMOKE OK`; `REPAIR CHECKS OK`; `g4b VERIFY OK`. On R1 the
reviewer's own edit to `run_mapper.py` moved the identifier to `rtmap-1.0.0/ba19d43c44b30c7b`
while an edit under `tables/` left it unchanged — exactly the intended behaviour.

**Two residual documentary overstatements, raised in round 2 and repaired here:**

1. calling the projected core-hours an "upper bound" — it is a full-count extrapolation *at
   the measured 477 aa substrate rate*, and the wider Stage-1 length distribution can push the
   per-record cost **up**. Corrected in `docs/G5_EXECUTION_PLAN.md` §5 and in the throughput
   table's own note, which the measuring script now writes.
2. "the whole run fits in a few minutes" stated as fact while the 48-core figure was labelled
   unmeasured; and "family-balanced by construction" for a hash prefix. Both now phrased as
   projections / balance **in expectation**, with g5 required to report the realised shard-size
   distribution.

Also addressed: the reviewer could not recompute the before/after column diff because the
pre-repair products were not landed. They now are, at
`tables/pre_repair_snapshot/`, with a README carrying the exact command that reproduces the
diff. Re-run: `mapper_version` only for states and sequences; plus free-text `detail` for
failures.

**DECISION — `g4b` is COMPLETE.** The validated mapper is frozen as a production instrument
`rtmap-1.0.0/53a1e738a19b3896`, bundle root
`0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f`. No scientific parameter,
rule, call or claim changed. **`g5` is authorised to begin** under
`docs/G5_EXECUTION_PLAN.md`, with `--pinned-root` and `--reject-ids` mandatory. `g6` and `g7`
remain NOT STARTED.

## 7b · Governance bundle conformance — a gap closed

`g4b` is the **first Stage-2 bundle to pass `general/checks/bundle_valid.sh` (BS-1..BS-10)**.

| bundle | BS findings |
|---|---|
| `results/dbchar_g7_stage1_report` (Stage 1) | 0 |
| `results/FINAL_PRE_UG25_VALIDATION_BUNDLE` | 8 |
| `results/rt07_ug25_confirmatory` | 8 |
| **`results/rt07_g4b_production_mapper`** | **0** |

The Stage-2 line had been landing bundles in its own layout (`code/`, `control/`, `tables/`)
without the governance spec's `run.sh`, `MANIFEST.tsv`, `OUTPUTS.tsv`, `PROVENANCE.md`,
`README.md`, `env.lock` and `scripts/`. g4b was restructured to conform, because it is the
bundle g5 depends on. **For the operator:** the two earlier Stage-2 bundles still carry 8
findings each. They are frozen and reviewed, so this record does not touch them — but
retrofitting them is open work if the operator wants the Stage-2 line uniformly conformant.

One landed product is **declared non-byte-reproducible** rather than quietly excluded:
`tables/g4b_throughput_measurement.tsv` is a wall-clock measurement (12.9–14.1 ms per
sequence across runs on this host). It is stated as such in `README.md` under `STATUS:`, it
is outside `verify.sh`'s byte-diff, it is not part of the instrument identifier, and no
scientific result depends on it.

## 8 · Standing constraints carried into g5, g6 and g7

* Historical RT0–RT7 stays a **separate crosswalk**, `UNRESOLVED` in all eight rows, and
  appears in no production column. The bridge that could resolve it is registered for g7.
* Stage-1 MyRT / PADLOC / DefenseFinder labels are **strata, never validation truth**. No
  accuracy, sensitivity, specificity or ROC against a tool label, in any gate.
* `NO_SUPPORTED_MAPPING` and `DELETED_STATE` are **not biological absence**.
* `MULTI` remains its own multi-label population.
* The eligible g5 denominator is the **censused** eligible count, not 501,561; the census is
  g5's first step and also produces the global duplicate-identifier conflict set.
* Structures are reserved for g7 and may not redefine the frozen sequence coordinate system.
* The supported scope is `-M 50` only. No `-M 60` or `-M a2m` claim.
