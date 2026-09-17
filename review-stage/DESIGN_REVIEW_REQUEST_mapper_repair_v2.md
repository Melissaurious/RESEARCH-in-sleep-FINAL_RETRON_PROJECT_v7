# RE-REVIEW REQUEST — are the six required defects closed?

Track `rt07`, Stage 2. **Scope: only whether the six `REQUIRED BEFORE UG25` defects are closed.**
Not a fresh review of the whole design — that was done last round (6/10, class B).

Bundle under review: `results/rt07_mapper_validation_repair_v2/` — frozen, locked, manifest-hashed.

```
rt07_mapper_validation_repair_v2   ROOT_SHA256 512bb53bc071053b7b45921ea8d01a5082098f91ac863ef9cb8033e1498a0d0d   174 files
rt07_mapper_validation_repair (v1) ROOT_SHA256 2f0cacc5793e46bdb0b9d0924278f42ceaceb0eecd1c87075700ae2c9f3efe6a   162 files  (UNCHANGED, the artifact you reviewed)
rt07_residue_mapper_gate           ROOT_SHA256 e6eb62bdd80ca691ebd13507d7cabad2063f62374fba294028adcaa6ea41cce1   132 files  (UNCHANGED)
```

v1 was **not modified**. v2 is a new bundle. Manifests live in `review-stage/manifests/`, each
with a detached `.sha256` sidecar, all mode 444.

**Verify by execution.** Every finding you made last round was something the executor asserted in
prose and you disproved by running the code.

## The six repairs and what to check

| # | defect you found | what was done |
|---|---|---|
| 1 | `catalytic_rule.py:62` counted every motif-bearing state regardless of call; one `AMBIGUOUS` (`EQC02762.1_Retrons`, state 204, pp 0.55) contributed positive evidence | aggregation filtered to `call == "MAPPED"`; excluded occurrences **landed** in `tables/catalytic_excluded_occurrences.tsv` rather than dropped |
| 2 | missing manifest and corrupt root header both failed **open** | `verify()` now fails closed on: missing manifest, malformed manifest, missing/מmismatched root header, caller-expected-root mismatch, tampered manifest (detached sidecar), add/remove/change/rename |
| 3 | `lock()` chmodded files only; bytecode written into an unmanifested `__pycache__` | directories locked deepest-first; `PYTHONDONTWRITEBYTECODE=1` + `python3 -B`; `__pycache__` **no longer excluded** from the manifest; manifest authenticated by sidecar and held outside the bundle |
| 4 | U10 checked only `ABSTAIN`, not the exact reason | closed 3-pair vocabulary; U10 asserts exact pairs; **U10m** runs three deliberately-wrong classifiers (swapped-reason, never-abstains, out-of-vocabulary) and requires all three to FAIL |
| 5 | "UG25 was never read" false — `eligible_by_family()` materialised all 38 families | `scoped_loader.py` discards non-allowed records at parse time; UG25 `SEALED` behind an explicit token; claim retracted and replaced with "not used for alignment, scoring, calibration, thresholding, output generation or mapper development" |
| 6 | pooled p95 hid the reverse tail; empty/failed-control behaviour undefined | `control/C6_CONTROL_POLICY.md` + `control_policy.py` + 7 tests. **C6 is per-class**; one class violating fails **even when pooled passes** |

Plus repair 7 (narrative): construction total **217/219**, now **computed** as a `TOTAL` row in
`construction_validation_v2_family.tsv` rather than transcribed. Errata in
`docs/decisions/2026-09-17_stage2_mapper_repair_v2_errata.md`, which preserves both values.

## Results claimed (verify each)

- `CAT_STATE` **262**, MAPPED-only count **207**, runner-up **5**, agreement **207/210 = 0.9857**
  ≥ 0.80 — **unchanged** from v1, because the excluded occurrence was at state **204**.
- **9** excluded occurrences: 1 `AMBIGUOUS`, 8 `NOT_IN_MATCH_COLUMN`.
- Every calibrated value identical to v1: `PP_HI` 0.75, `S_MIN` 10, `K_MIN` 30, `T1` 0.32,
  `D_MAX` 0.48, `D_RANDOM` 0.067.
- Tests: mapper **14/14** (12 falsifiable, 2 invariants), freeze **13/13**, loader scope **5/5**,
  C6 policy **7/7**, reproducibility **17/17** byte-identical, `VERIFY OK` against a pinned root.
- Per-class negative p95 now reported: mono **0**, di **0**, **reverse 10**, pooled **0**.

## Two defects the executor found in its own repairs, disclosed

1. `verify.sh` **failed on its first v2 run** — `__pycache__` present inside the bundle, left by
   runs made before `-B` was added, and already hashed into the manifest. Cache removed, manifest
   rebuilt. The v1 verifier **could not** have reported this.
2. `lock()` initially descended into `.claude` (a sandbox-injected read-only mount), raised EROFS
   and left the bundle **half-locked** — which looks locked. Fixed by applying `EXCLUDE_DIRS` in
   `chmod_tree`; freeze test F10 re-run.

## Questions — answer each explicitly

1. Is catalytic aggregation now strictly `MAPPED`-only?
2. Are ambiguous catalytic states excluded from positive evidence?
3. Do verifier and manifest checks fail closed?
4. Does root-hash corruption fail?
5. Do missing/add/delete/rename/change events fail integrity?
6. Is directory freeze enforcement real?
7. Is bytecode controlled?
8. Is the external manifest itself protected?
9. Does U10 assert exact reason codes?
10. Is the loader now genuinely family-scoped?
11. Is the UG25 access claim worded accurately?
12. Are C6 and empty-control behaviour predeclared and falsifiable?
13. Are di-shuffle failures handled exactly as declared?
14. Does the corrected construction count equal **217/219**?
15. Does the narrowed scientific claim remain supported?
16. Is UG25 now safe to open as the final confirmatory holdout?

Specifically probe: whether `scoped_loader` is **exactly** equivalent to the old loader on
construction families (test L1 — it was NOT at first: it kept GII 497 vs 496 and DGRs 492 vs 488
until it replicated the old loader's rejection of non-standard amino acids); whether the U10m
mutants genuinely fail the predicate; whether `evaluate_c6` can be made to pass with an empty
control class; and whether any *new* fail-open path was introduced.

## Required verdict

`PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL/BLOCK`, numeric score, and exactly one of:

- **A** `UG25 READY — FINAL CONFIRMATORY HOLDOUT MAY RUN`
- **B** `BOUNDED REPAIR STILL REQUIRED — UG25 REMAINS SEALED`
- **C** `MAPPER VALIDATION NOT READY — DO NOT OPEN UG25`

Every requested change tagged `REQUIRED BEFORE UG25` or `OPTIONAL / FUTURE STRENGTHENING`. No
"nice to have" language for load-bearing issues.

**Do not modify any file in any bundle.** Report findings in your reply only. Check the v2 root
hash at start and at end and report any change as a freeze violation.
