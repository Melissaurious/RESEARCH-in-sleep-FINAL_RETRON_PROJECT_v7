# DECISION — Final pre-UG25 bundle: three authorised repairs applied; root superseded

Date: 2026-09-17 · Track `rt07` · Status: **repairs applied; awaiting bounded re-review**

## Root supersession chain

| stage | ROOT_SHA256 | files | reason |
|---|---|---|---|
| clean bundle, first freeze | `eb3ac78f48aa0d33bd5fda3f40abcecc554adea40d9418a4f21c3aed67d5415c` | 39 | reviewed at 7/10, class B |
| **after the three authorised repairs** | **`c20be8f953cd1a52ffb8e56564948ac5ed3774e8b1a90457cee5a0be16115b40`** | **43** | C6 accounting · temp-path removal · new UG25 predeclaration |

External root file `review-stage/roots/FINAL_PRE_UG25.root`, manifest and detached sidecar in
`review-stage/manifests/`, all mode 444, all outside the bundle.

**No historical bundle was regenerated.** v1 remains formally FREEZE BROKEN and untouched; v2
remains as landed.

---

## 1 · C6 accounting — fails closed

The check was `n_valid + n_failed > n_attempted`, which catches over-accounting only.
**Under**-accounting passed whenever the surviving count still cleared the 90% minimum — so
80 valid + 0 failed out of 84 returned `PASS` with four replicates silently gone. Reconciliation
is now **exact**: `n_valid + n_failed == n_attempted` per class.

Also rejected, each with its own reason code: duplicate or blank failed IDs; duplicate valid
IDs; a replicate in both the valid and failed sets; a valid-ID count mismatch; an undeclared
control class anywhere (values, failed IDs or valid IDs); non-finite, negative, non-integer or
non-numeric counts; `n_real > n_eligible`; a non-positive or non-integer denominator; a bad
design parameter; a non-dict container; a bare string where an ID list is required.

**A defect found by the new tests themselves:** non-numeric control values reached `sum()`/`max()`
and raised `TypeError` instead of returning a controlled `FAIL` — exactly the failure mode the
reviewer flagged. `healthy`/`pooled_ok` guards now make every aggregate numeric-safe.

**Nothing is silently repaired.** A malformed row is a `FAIL` with a reason code.

## 2 · C6 negative-test matrix

`tables/c6_negative_test_matrix.tsv` — **25** invalid states, each asserting a specific reason
code, plus **11** semantic cases. **36/36 pass.** Categories: under-accounting, over-accounting,
duplicate failed IDs, duplicate valid IDs, replicate in both sets, valid-ID count mismatch,
undeclared class (two routes), `n_real > n_eligible`, bare-string ID list, blank IDs, NaN, Inf,
negative, non-integer, non-numeric, four denominator faults, bad design parameter, non-dict
container.

## 3 · Control policy preserved

Mono-shuffle, di-shuffle and reverse definitions, thresholds and the C6 scientific criterion are
**unchanged**. The canonical family order is now explicit and enforced:

```
CANONICAL_FAMILY_ORDER = ("Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA")   # NOT sorted
CANONICAL_SEED         = 20260917
```

`code/canonical_order.py` derives a diagnostic hash over `(order, seed)`; `assert_canonical()`
fails closed on any drift. Tests **S10** (a sorted order) and **S11** (a changed seed) prove both
are caught. Landed as `tables/canonical_order.tsv`.

This matters because it is empirical: sorting the order produced a *different* di-shuffle
failure set (2 UG3) from the established one (2 CRISPR + 1 UG3).

## 4 · Temp paths removed from landed outputs

`tables/freeze_negative_test_matrix.tsv` embedded `/tmp/claude-1000/frz.MANIFEST`, so a reviewer
under `/dev/shm` regenerated a different string and `verify.sh` failed on a purely environmental
difference. A `sanitise()` step now maps environment paths to logical labels — `<MANIFEST>`,
`<BUNDLE>`, `<TMP>` — before anything is landed. Real paths remain in the runtime log, which is
not compared.

## 5 · Multi-root reproduction

Reproduced under two temp roots — the default and `/dev/shm` — and compared:

```
compared 21 canonical products across two temp roots; 0 drifted
```

**Note on the count.** The operator's figure of **19** was correct for the previously reviewed
bundle (17 tables + 2 control TSVs). These repairs add two canonical products —
`c6_negative_test_matrix.tsv` and `canonical_order.tsv` — so the corrected count is
**21 (19 tables + 2 control TSVs)**. The stale "17/17" is withdrawn; "19" is superseded by "21".

Both runs also had to be executed inside a single shell invocation: the sandbox gives each
command its own `/dev/shm` tmpfs, so a cross-command comparison sees an empty directory. That is
an environment artefact, not a product defect, and is recorded here so the empty first attempt is
not mistaken for drift.

## 6 · New UG25 predeclaration

`control/UG25_PREDECLARATION_v2.md` — names the actual loader (`code/loader.py`), mapper
(`code/mapper.py`), runtime authorisation (`RT07_AUTHORISED_FAMILIES`, fails closed if unset),
external-root requirements, score/support rules, ambiguity and abstention vocabulary, the
`CAT_STATE` rule, control classes, C6 logic, success/failure criteria, verifier, output schema
and stop conditions — each with the code hash that implements it.

Access wording is exact: **"UG25 is sealed from development execution before operator
authorization."** It explicitly does **not** claim UG25 was never read by any audit process —
`sealing_proof.py` loads it once, after development outputs exist, purely to search them for
leakage, and says so.

`control/UG25_PREDECLARATION_SUPERSEDED_v1.md` retains the original text unchanged beneath a
supersession banner. It was **not** rewritten.

## 7 · Mapper and thresholds unchanged

`code/mapper.py` sha256 `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef`,
identical to v1 and v2. Re-derived after the repairs: `PP_HI` 0.75, `S_MIN` 10, `K_MIN` 30,
`T1` 0.32, `D_MAX` 0.48, `D_RANDOM` 0.067; `CAT_STATE` **262**, count **207**, runner-up
**136 @ 5**, agreement **207/210 = 0.9857**; construction **217/219**; di-shuffle failures the
same three IDs. **No scientific measurement changed.**

## 8 · Test totals after repair

mapper **14/14** · C6 **36/36** (11 semantic + 25 negative) · freeze **18/18** · sealing **8/8** ·
reproduction **21/21 byte-identical across two temp roots** · `VERIFY OK` against the pinned root.

## 9 · Gate state

**UG25 SEALED · g4b BLOCKED · g5 BLOCKED · g6 NOT STARTED.**
