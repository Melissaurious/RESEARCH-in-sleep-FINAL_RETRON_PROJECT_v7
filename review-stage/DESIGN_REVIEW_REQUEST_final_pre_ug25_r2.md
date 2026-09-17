# BOUNDED RE-REVIEW — are the three blocking defects closed?

**Scope: only the three blockers from your 7/10 class-B review.** Not a fresh review of the
mapper or the architecture, both of which you accepted.

Bundle: `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/` — 43 files, frozen, locked.

```
NEW EXTERNAL PINNED ROOT (hold this independently):
c20be8f953cd1a52ffb8e56564948ac5ed3774e8b1a90457cee5a0be16115b40

previous root (superseded): eb3ac78f48aa0d33bd5fda3f40abcecc554adea40d9418a4f21c3aed67d5415c
manifest  : review-stage/manifests/FINAL_PRE_UG25.MANIFEST        (444)
sidecar   : review-stage/manifests/FINAL_PRE_UG25.MANIFEST.sha256 (444)
root file : review-stage/roots/FINAL_PRE_UG25.root                (444)
```

```
python3 -B results/FINAL_PRE_UG25_VALIDATION_BUNDLE/code/integrity.py \
  verify results/FINAL_PRE_UG25_VALIDATION_BUNDLE \
  review-stage/manifests/FINAL_PRE_UG25.MANIFEST \
  c20be8f953cd1a52ffb8e56564948ac5ed3774e8b1a90457cee5a0be16115b40
```

No historical bundle was regenerated. v1 remains formally FREEZE BROKEN and untouched.

## Blocker 1 — C6 accounting

You found these returning `PASS`: 80 valid + 0 failed of 84 attempted; duplicate failed IDs; an
undeclared class carrying NaN; more real observations than `n_eligible`. Root cause: the check
was `n_valid + n_failed > n_attempted`, catching **over**-accounting only.

Now: **exact reconciliation**, `n_valid + n_failed == n_attempted` per class, plus unique
non-blank list-valued IDs, no replicate in both sets, valid-ID count match, no undeclared class
anywhere, finite non-negative integer counts, `n_real <= n_eligible`, positive integer
denominator, valid design parameter, dict containers.

`tables/c6_negative_test_matrix.tsv` — **25** invalid states each asserting a named reason code,
plus 11 semantic cases: **36/36**.

Please confirm none of your four cases still passes, and look for any remaining invalid state
that returns `PASS` or raises an uncaught exception instead of a controlled `FAIL`. Note one
defect the new tests caught in development: non-numeric values previously reached `sum()`/`max()`
and raised `TypeError`; `healthy`/`pooled_ok` guards now cover that.

## Blocker 2 — environment-specific paths

`tables/freeze_negative_test_matrix.tsv` embedded `/tmp/claude-1000/frz.MANIFEST`, which is why
`verify.sh` exited 1 for you under `/dev/shm`. A `sanitise()` step now maps environment paths to
`<MANIFEST>`, `<BUNDLE>`, `<TMP>` before landing; real paths stay in the uncompared runtime log.

Reproduced under two temp roots and compared: **21 canonical products, 0 drifted.**

**Corrected count:** your figure of 19 was right for the bundle you reviewed (17 tables + 2
control TSVs). These repairs add two canonical products — `c6_negative_test_matrix.tsv` and
`canonical_order.tsv` — so it is now **21 (19 tables + 2 control TSVs)**. Please confirm 21 is
right and that no landed product still carries an environment-specific path.

One environment note, so an empty result is not mistaken for drift: the sandbox gives each shell
command its own `/dev/shm` tmpfs, so a two-root comparison must run inside a single invocation.

## Blocker 3 — stale UG25 predeclaration

`control/UG25_PREDECLARATION_v2.md` is new and supersedes
`control/UG25_PREDECLARATION_SUPERSEDED_v1.md`, which retains its original text unchanged beneath
a supersession banner. The new document names the actual loader, mapper, runtime authorisation
mechanism, external-root requirements, rules, criteria, verifier, output schema and stop
conditions, each against the code hash implementing it:

```
code/mapper.py          69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef
code/loader.py          e39fb4eee45904cab3c681f033744950fe53e9316f5d54809a9c23285b2d3a24
code/c6_policy.py       35b24b9f95b72f97ee6e805099aa26cf24428d09d21daa8a6ee8ec2f76260851
code/canonical_order.py 3f7bf3b6c8245a33abb7899d648cbc4616fc82941c9e4174c6f11794ab52eec7
```

Access wording: **"UG25 is sealed from development execution before operator authorization."** It
explicitly does not claim UG25 was never read by any audit — `sealing_proof.py` loads it once,
after development outputs exist, purely to search them for leakage, and declares it. Authorisation
is the operator setting `RT07_AUTHORISED_FAMILIES` at run time; unset → fails closed; there is no
source-tree constant that can grant it.

## Also preserved (please confirm unchanged)

Canonical family order is now explicit and enforced —
`("Retrons","GII","DGRs","CRISPR","UG3","AbiA")`, seed `20260917`, hashed, with
`assert_canonical()` failing closed; tests S10 (sorted order) and S11 (changed seed) prove both
are caught. Landed as `tables/canonical_order.tsv`.

Science re-derived after repair, all unchanged: `PP_HI` 0.75, `S_MIN` 10, `K_MIN` 30, `T1` 0.32,
`D_MAX` 0.48, `D_RANDOM` 0.067; `CAT_STATE` 262, count 207, runner-up 136@5, agreement
207/210 = 0.9857; construction 217/219; di-shuffle failures `ADE85031.1_CRISPR`,
`ESQ17084.1_CRISPR`, `WP_032822382.1_UG3`. Tests: mapper 14/14, C6 36/36, freeze 18/18,
sealing 8/8.

## Questions

1. Does C6 fail on missing replicates?
2. Does C6 fail on duplicate IDs?
3. Does C6 fail on undeclared classes?
4. Does C6 fail on non-finite values?
5. Does C6 fail on impossible counts?
6. Does valid control accounting still pass?
7. Does any canonical output still contain an environment-specific temp path?
8. Is reproduction byte-identical under a different `TMPDIR`?
9. Is the canonical computed-product count correct?
10. Does the new UG25 predeclaration match the actual clean implementation?
11. Is the old predeclaration clearly superseded?
12. Does UG25 remain sealed?
13. Are the scientific mapper and thresholds unchanged?

## Required verdict

`PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL/BLOCK`, numeric score, and exactly one of:

- **A** `THREE BLOCKERS CLOSED — SINGLE-SHOT UG25 MAY RUN`
- **B** `ONE BOUNDED BLOCKER REMAINS — REPAIR BEFORE UG25`
- **C** `CONFIRMATORY INFRASTRUCTURE STILL UNSOUND — DO NOT RUN UG25`

Only a defect compromising mapper correctness, holdout sealing, confirmatory interpretation or
bundle integrity may block. Refinements that would merely be nice to have may not. Please write
only into your own temporary directory and do not modify any bundle.
