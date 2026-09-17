# BOUNDED REVIEW — is the C6 identity-binding blocker closed?

**Scope: one blocker.** Everything else in this bundle you have already passed. Please do not
solicit optional improvements unless they directly threaten UG25 validity.

Bundle: `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/` — 44 files, frozen, locked.

```
NEW EXTERNAL PINNED ROOT (hold independently):
489e1095e055aa45a8765823fcb0ff2f7d68c6db05282cd37a6e1fcc804eebcc

superseded roots: c20be8f953cd1a52... (your 8/10 review) ; eb3ac78f48aa0d33... (your 7/10 review)
manifest  : review-stage/manifests/FINAL_PRE_UG25.MANIFEST        (444)
sidecar   : review-stage/manifests/FINAL_PRE_UG25.MANIFEST.sha256 (444)
root file : review-stage/roots/FINAL_PRE_UG25.root                (444)
```

```
python3 -B results/FINAL_PRE_UG25_VALIDATION_BUNDLE/code/integrity.py \
  verify results/FINAL_PRE_UG25_VALIDATION_BUNDLE \
  review-stage/manifests/FINAL_PRE_UG25.MANIFEST \
  489e1095e055aa45a8765823fcb0ff2f7d68c6db05282cd37a6e1fcc804eebcc
```

## What you found

> C6 does not yet enforce typed, explicit identity binding for valid and failed control
> replicates.

Specifically: set- and dict-valued ID collections returned `PASS`; `None`/`int`/generator raised
uncaught `TypeError`; valid-ID tracking was optional, so 83 values + 1 failed ID with no
valid-ID list passed and disjointness was unverifiable; and production supplied no valid IDs.

## What was changed

**Type contract** (`code/c6_policy.py:strict_id_list`): every ID collection must be exactly
`list[str]` — `type(x) is list` (not `isinstance`, so list subclasses are rejected too) with
every element `type(e) is str`, non-empty after stripping. Rejected with a reason code, **never
coerced**: set, dict, tuple, generator, iterator, `None`, int, float, scalar str, bytes, nested
containers, non-string elements. A malformed container is a controlled `FAIL`, never a raise.

**Identity reconciliation** — the three identity arguments are now **required parameters**;
there is no count-only mode:

```
set(valid_ids) | set(failed_ids) == set(attempted_ids)
set(valid_ids) & set(failed_ids) == empty
len(valid_ids) == n_valid ,  len(failed_ids) == n_failed ,  n_valid + n_failed == n_attempted
```

Reason codes: `INVALID_ATTEMPTED_IDS`, `INVALID_VALID_IDS`, `INVALID_FAILED_IDS`,
`REPLICATE_IN_BOTH_SETS`, `UNKNOWN_VALID_ID`, `UNKNOWN_FAILED_ID`,
`UNACCOUNTED_ATTEMPTED_ID`, `ATTEMPTED_ID_COUNT_MISMATCH`, `VALID_ID_COUNT_MISMATCH`,
`IDENTITY_NOT_RECONCILED`, plus the pre-existing accounting and value codes.

**Production call site** — `code/controls.py:make_negatives` now *emits* the identities
(`attempted`, `valid`, `failed` in a single replicate-ID space `<source>#<CLASS>#<rep>`), and
`code/pipeline.py` passes all three into C6 and lands them:

```
tables/control_replicate_identities.tsv
control_class  n_attempted  n_valid  n_failed  failed_replicate_ids
MONO           219          219      0         none
DI             219          216      3         ADE85031.1_CRISPR#DI#0,ESQ17084.1_CRISPR#DI#0,WP_032822382.1_UG3#DI#0
REV            219          219      0         none
```

**Tests** — `tables/c6_negative_test_matrix.tsv`: **39 negative cases**, each asserting a named
reason code, and each recorded as `RAISED:<type>` if it raises instead. Plus 8 positive/semantic
cases. **47/47.** The 17 categories you specified are covered as T1–T23 (container types,
duplicates, overlap, missing/unknown/extra IDs, count mismatch, missing valid list, missing
failed list, missing attempted list, undeclared class) with V1–V16 for value faults.

## Unchanged (please confirm)

`code/mapper.py` sha256 `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef`,
identical across all three bundles. `PP_HI` 0.75 · `S_MIN` 10 · `K_MIN` 30 · `T1` 0.32 ·
`D_MAX` 0.48 · `D_RANDOM` 0.067 · `CAT_STATE` **262**, count 207, runner-up 136@5, agreement
**207/210** · construction **217/219** · same three di-shuffle source IDs · canonical order and
seed enforced · mono/di/reverse definitions untouched · UG25 sealing 8/8.

Reproduction: **22 canonical products byte-identical across two temp roots** (default and
`/dev/shm`). The count rose from 21 because this repair adds
`tables/control_replicate_identities.tsv`.

The UG25 predeclaration §2 code hashes and §7 C6 description were updated to match this repair —
leaving them stale would have re-created the blocker you closed last round.

Note: the sandbox gives each shell command its own `/dev/shm` tmpfs, so a two-root comparison
must run inside a single command invocation.

## Please verify

1. only concrete approved ID-list types are accepted;
2. malformed containers fail cleanly (no uncaught exception);
3. explicit valid IDs are mandatory;
4. explicit failed IDs are mandatory;
5. attempted = valid ∪ failed exactly;
6. valid ∩ failed is empty;
7. counts equal identity-list lengths;
8. unknown / missing / duplicate IDs fail;
9. production control generation actually supplies the identities;
10. confirmatory C6 can no longer pass with unverifiable identity accounting;
11. the scientific mapper and thresholds remain unchanged;
12. UG25 remains sealed.

## Required verdict

`PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL/BLOCK`, numeric score, and exactly one of:

- **A** `C6 IDENTITY BINDING CLOSED — UG25 MAY RUN`
- **B** `ONE LOAD-BEARING C6 DEFECT REMAINS — UG25 SEALED`
- **C** `C6 CONFIRMATORY ACCOUNTING UNSOUND — STOP`

Please write only into your own temporary directory and do not modify any bundle.
