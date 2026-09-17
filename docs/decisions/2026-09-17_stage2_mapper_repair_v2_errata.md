# DECISION — Mapper repair v2: errata, retractions, and the six required repairs

Date: 2026-09-17 · Track: `rt07` · Status: **six repairs applied in v2; UG25 still SEALED**

Bundle: `results/rt07_mapper_validation_repair_v2/`
Manifest `ROOT_SHA256 dd3b8eab29980993f75570d33187cfbb8f9944b1b1965ee18d3a5b9817ece364` (174
files), held outside the bundle at
`review-stage/manifests/rt07_mapper_validation_repair_v2.MANIFEST` with a detached
`.sha256` sidecar.

**v1 (`rt07_mapper_validation_repair`, ROOT `2f0cacc5…`) is NOT modified.** It remains frozen
and INTACT as the artifact the reviewer examined. v2 is a new bundle; nothing is overwritten.

Supersede by a new record, never by rewriting.

---

## 1 · Errata — superseded value, corrected value, where the wrong value appears

| # | superseded | corrected | appears in |
|---|---|---|---|
| E1 | construction total **237/239** callable | **217/219** (`40+40+40+40+40+19 = 219`; `38+40+40+40+40+19 = 217`) | `2026-09-17_stage2_mapper_validation_repair.md` §6 — **stale**. The tables always said 217/219; only the narrative was wrong. v2 now **computes** a `TOTAL` row into `construction_validation_v2_family.tsv` so the number can never again be transcribed by hand |
| E2 | "**no UG25 object was read**" | **FALSE.** `eligible_by_family()` materialised all 38 families, UG25 n=28 included, on every call. Correct: **"UG25 was not used for alignment, scoring, calibration, thresholding, output generation or mapper development."** `UNEVALUATED` ≠ `UNREAD` | `2026-09-17_stage2_mapper_validation_repair.md` §8 · v1 `UG25_PREDECLARATION.md` header |
| E3 | "**only `MAPPED` contributes positive evidence**" | **FALSE in v1's catalytic aggregation.** `catalytic_rule.py:62` counted every motif-bearing state regardless of call. One `AMBIGUOUS` occurrence was counted: `EQC02762.1_Retrons`, residue 134, `FPDD`, state **204**, posterior **0.55** | `2026-09-17_stage2_mapper_validation_repair.md` §2 |
| E4 | `freeze_manifest.py verify` reports integrity | **v1 failed OPEN on a corrupted root header** — an all-zero expected root over genuine rows returned exit 0 and `FREEZE INTACT`. `ok` never compared the roots | v1 `scripts/freeze_manifest.py` |
| E5 | "`lock()` makes the bundle immutable" | **v1 chmodded files only.** Directories stayed mode 775, so add / delete / rename / atomic-replace all still worked | v1 `scripts/freeze_manifest.py` |
| E6 | "the verifier never writes into the bundle" | **not guaranteed** — v1 wrote `scripts/__pycache__/*.pyc`, and `__pycache__` was *excluded from the manifest*, so those writes were invisible | v1 bundle |
| E7 | negative 95th percentile **= 0** | **pooled only.** Per class: mono **0**, di **0**, **reverse 10**. The pooled figure conceals the reverse tail | v1 `SUPPORT_RULE_ADDENDUM_1.md` · v1 C6 |

**E1 and E7 change no measurement.** E2–E6 are governance/integrity defects. **E3 changes no
number either**: re-deriving with `MAPPED`-only leaves `CAT_STATE = 262` and agreement
**207/210 = 0.9857** untouched — the excluded occurrence was at a *different* state (204).

## 2 · The six required repairs

| # | repair | evidence |
|---|---|---|
| 1 | `MAPPED`-only catalytic aggregation | `CAT_STATE = 262` (count 207), runner-up 5, agreement **207/210 = 0.9857** ≥ 0.80. **9** excluded occurrences landed in `catalytic_excluded_occurrences.tsv` — 1 `AMBIGUOUS`, 8 `NOT_IN_MATCH_COLUMN`. **No material change** |
| 2 | fail-closed verifier and manifest | missing manifest, corrupt root header, tampered manifest, caller-expected-root mismatch, add / remove / change / rename — all exit non-zero. Freeze tests **F2–F9** |
| 3 | directory lock, bytecode, manifest protection | `lock()` now clears write on directories deepest-first; add/delete/rename all blocked (**F10**). `PYTHONDONTWRITEBYTECODE=1` + `python3 -B`; `__pycache__` **no longer excluded** from the manifest, so a stray `.pyc` is an `ADDED` violation (**F11**). Manifest authenticated by a detached `.sha256` sidecar (**F8**), and lives outside the bundle |
| 4 | U10 exact reason codes | closed vocabulary of three `(verdict, reason)` pairs. **U10** asserts exact pairs; **U10m** runs three deliberately-wrong classifiers — swapped-reason, never-abstains, out-of-vocabulary — and requires all three to FAIL the predicate while the real one passes |
| 5 | family-scoped loader | `scoped_loader.py` discards non-allowed records at parse time; UG25 is `SEALED` behind an explicit operator token. **L1** proves construction families are byte-identical to the old loader; **L5** proves the old loader leaked |
| 6 | C6 / empty-control / di-shuffle policy | `C6_CONTROL_POLICY.md` + `control_policy.py` + 7 tests. **C6 is per-class**; a single class violating fails **even when pooled passes** (**C4**). Empty class, missing class, depleted class and empty real set all fail closed |

## 3 · A defect the repaired verifier caught on its own bundle

On its first run `verify.sh` reported `FAIL __pycache__ present inside the bundle` — bytecode
left by runs made before `-B` was added, which the *build* step had already hashed into the
manifest. The cache was removed and the manifest rebuilt. **The v1 verifier could not have
reported this**, because v1 excluded `__pycache__` from the manifest entirely.

## 4 · Test totals

- mapper: **14/14** (12 falsifiable empirical, 2 implementation invariants)
- freeze: **13/13**
- loader scope: **5/5**
- C6 control policy: **7/7**
- reproducibility: **17/17** computed products byte-identical, `VERIFY OK` against a pinned root

## 5 · Optional items — explicit classification

| item | classification | justification |
|---|---|---|
| per-control-class p95 reporting | **OPTIONAL — IMPLEMENT NOW** | pure reporting; it is what exposes the reverse tail the pooled figure hid, and C6 was being rewritten anyway |
| `PP_LO` wording refinement | **OPTIONAL — IMPLEMENT NOW** | wording only; no threshold moves |
| 237/239 → 217/219 correction | **OPTIONAL — IMPLEMENT NOW** | required by §7 of the authorisation regardless; now computed rather than transcribed |
| unrelated real-protein controls | **OPTIONAL — DEFER** | adds a new negative-control class and a new external data dependency, which would change the confirmatory control design after C6 was frozen — exactly what must not happen before a single-shot holdout |

## 6 · The narrowed claim is unchanged

> Under `-M 50`/`-M 60`, a compact GII-centred correspondence frame is recoverable across the
> construction families, and the alignment-path mapper produces posterior-stratified calls, real
> ambiguity, reason-coded abstention and a stable operational catalytic coordinate in
> construction data.

Every calibrated value is identical to v1: `PP_HI` 0.75, `S_MIN` 10, `K_MIN` 30, `T1` 0.32,
`D_MAX` 0.48, `D_RANDOM` 0.067, `CAT_STATE` 262. The scoped loader changed **nothing**
numerically, which is exactly what L1 exists to prove.

## 7 · Gate state

**UG25 SEALED · g4b BLOCKED · g5 BLOCKED · g6 NOT STARTED.** UG25 has not been run, and the
repairs are not yet independently re-reviewed.
