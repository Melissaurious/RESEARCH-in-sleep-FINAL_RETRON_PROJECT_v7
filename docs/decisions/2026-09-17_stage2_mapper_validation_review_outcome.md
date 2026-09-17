# DECISION — Mapper-validation review outcome: PASS_WITH_REQUIRED_REPAIRS (6/10), class B

Date: 2026-09-17 · Track: `rt07` · Status: **UG25 remains SEALED; six bounded repairs required**

Reviewer: independent Codex (`gpt-5.6-sol`, xhigh, read-only), thread `01a0ac9a`. Routed per
WA-A.5; not same-family; **not self-reviewed**. First attempt died on a provider quota after 12
minutes and produced no verdict; it was **not** interpreted as PASS or FAIL and the gate was not
advanced for it. This record covers the second, successful attempt (17m 40s).

Gate: `review_gate.py --round-backend codex --score 6 --verdict almost` → `{"decision": "stop"}`.

**Verdict `PASS_WITH_REQUIRED_REPAIRS` · score 6/10 · classification B · UG25 may NOT be run ·
g4b blocked · g5 blocked.**

Supersede by a new record, never by rewriting.

---

## 1 · Freeze held

| bundle | ROOT_SHA256 | pre | post |
|---|---|---|---|
| `rt07_mapper_validation_repair` | `2f0cacc5793e46bd…` (162 files) | INTACT | **INTACT** |
| `rt07_residue_mapper_gate` | `e6eb62bdd80ca691…` (132 files) | INTACT | **INTACT** |

No review-time mutation. Manifests confirmed external to the bundles they protect. The previous
round's breach did not recur.

The reviewer's environment mounted everything read-only, so `verify.sh` could not create its temp
tree. It instead executed the production generators with writes intercepted in memory: **13 of 14
products byte-identical, the 14th independently reconstructed byte-identically.** That verifies
table-generation determinism from the frozen HMMER intermediates but is **not** a clean end-to-end
HMM rerun. The executor's own end-to-end `verify.sh` run (14/14) stands separately.

## 2 · Findings against the executor's own claims — all four verified by re-execution

### 2.1 "Only `MAPPED` contributes positive evidence" is **FALSE**

`catalytic_rule.py:62` increments `modal_counter[st]` for every motif-bearing state **without
checking the call**. Verified by re-running the mapper over all six construction families:

```
motif occurrences counted into modal_counter whose call is NOT MAPPED: 1
  ('Retrons', 'EQC02762.1_Retrons', 134, 'FPDD', state 204, AMBIGUOUS, posterior 0.55)
```

Exactly the occurrence the reviewer named. The executor checked `mapper_v2.py` and
`construction_validation_v2.py` for this and **did not check `catalytic_rule.py`** — the claim was
verified in two of three places and asserted for all three.

**`CAT_STATE = 262`, 207/210 agreement and the runner-up count of 5 are unchanged** — filtering to
`MAPPED` removes only state 204's single count. The number survives; the **claim** does not.

### 2.2 "No UG25 object was read" is **FALSE** — and repeats a corrected error

`eligible_by_family()` parses and materialises the **entire** collection before construction
families are selected. Verified:

```
families materialised by the loader: 38
UG25 present: True  n = 28      G2L present: True  n = 51
```

This is **the identical error as errata A5**, where "UG5 was never opened" was found literally
false for the same reason, in the same loader. The executor corrected that wording once and then
reproduced the error verbatim for UG25.

What **is** true, and what the reviewer confirmed independently: no UG25 alignment, score, table
row, work product or calibration access exists. **UG25 is unevaluated, not unread.** The
supportable wording is the latter.

### 2.3 `freeze_manifest.py verify` **fails open** on a corrupted root header

Verified by injecting an all-zero expected root against the genuine 162 manifest rows:

```
expected ROOT_SHA256 0000…0000
observed ROOT_SHA256 2f0cacc5…
FREEZE INTACT        exit=0
```

`ok` is computed from added/removed/changed only and **never compares the roots**. The root hash —
the headline integrity number reported to the operator — is decorative. Combined with the already
disclosed missing-manifest fail-open, the freeze checker has two paths that report success without
provenance.

### 2.4 Construction total is **217/219**, not 237/239

`40+40+40+40+40+19 = 219`; callable `38+40+40+40+40+19 = 217`. The tables are correct; the
**narrative in `2026-09-17_stage2_mapper_validation_repair.md` §6 is wrong**. Arithmetic error by
the executor, not a data error.

## 3 · Further verified defects

- **`lock()` chmods files but not directories.** Bundle directories stay mode 775, so addition,
  deletion and atomic replacement remain possible. Test F6 only tests appending to a 444 file.
- **Bytecode is written into the bundle.** `scripts/__pycache__/mapper_v2.cpython-312.pyc` exists,
  and `__pycache__` is *excluded from the manifest* — so writes there are invisible to the freeze
  check. "Never writes into the bundle" is not guaranteed.
- **The pooled negative p95 hides the reverse class.** Verified per class at `PP_HI = 0.75`:

  | class | n | p95 | max |
  |---|---|---|---|
  | mono-shuffle | 219 | 0 | 17 |
  | di-shuffle | 216 | 0 | 24 |
  | **reverse** | 219 | **10** | 25 |
  | pooled | 654 | **0** | 25 |

  Criterion C6 requires "negative 95th percentile = 0", evaluated **pooled**. Against reverse
  alone it would be 10. The criterion as written is the weaker test.
- **U10 under-asserts.** It checks `ABSTAIN` but not the exact reason `NO_QUALIFYING_DOMAIN`, so a
  mutant returning one reason for both cases passes U10 and U10b together.
- **C3 and C6 have undefined empty denominators**; the di-shuffle replicate rule has no
  generation-failure branch.

## 4 · What the reviewer confirmed as sound

- The `PP_HI` grid **reproduces exactly** and is exhaustive over HMMER's posterior bands. 0.75 is
  the smallest admitted band — *not* a repeat of the skipped-6-and-7 error. Any real threshold in
  (0.65, 0.75] behaves identically.
- **Ambiguity is real**: 1346 `AMBIGUOUS` calls across 45/45 sequences, 1475 `UNSUPPORTED`.
- **All 11 empirical predicates can take a false branch.** None is equivalent to the old always-true
  T6. U6, U8, U9, U10b are genuinely non-vacuous.
- U11/U12 correctly classified `IMPLEMENTATION_INVARIANT` and excluded from transfer evidence.
- **All 216 successful di-shuffles preserve dipeptide composition exactly**; the 3 failures are
  exactly 2 CRISPR + 1 UG3, disclosed and not replaced.
- Retrons **93/1/1** and shared core **7.5–27.5%** independently reconstructed and still valid.
- `-M 50` 7.5–27.5%, `-M 60` 7.3–25.8%, `-M a2m` DGRs 0 / AbiA 0 / GII 115. The claim's
  match-state dependence is correctly stated.
- **Keeping predeclared `D_MAX = 0.48` rather than substituting `D_RANDOM = 0.067` after
  calibration was the correct governance decision.** A C4 pass must remain explicitly
  non-evidential.
- Added / removed / changed / renamed detection works when the manifest is trusted; manifests are
  external.

## 5 · Required repairs — all tagged REQUIRED BEFORE UG25

1. Filter catalytic candidate and agreement aggregation to `MAPPED`-only; land per-motif call
   status; regenerate; issue a new manifest.
2. Make `verify.sh` fail on a missing manifest, and `freeze_manifest.py verify` fail on any
   root-header mismatch.
3. Lock directories as well as files; test add/delete/atomic-replace after locking; disable
   bytecode writes; protect the external manifest itself.
4. Strengthen U10 to assert the exact reason codes on both sides.
5. Retract the literal "UG25 was never read" assertion; use a family-scoped loader for the
   authorised run; describe UG25 as **unevaluated**, not unread.
6. Predeclare empty-denominator behaviour: zero `CAT_STATE=MAPPED` fails C3; zero non-abstaining
   real sequences fails C6; specify the UG25 di-shuffle failure branch.

Optional: per-class p95 reporting; rephrase the `PP_LO` rationale as "all alternatives
collectively exceed 0.5"; non-rewriting correction of 237/239 → 217/219; add unrelated natural
proteins and distant RT families as controls.

**None of these is authorised or started by this record.** The frozen bundle is unmodified.

## 6 · Reviewer's supportable claim, adopted

> Under the tested `hhmake -M 50`/`-M 60` match-state conventions, a compact GII-centred
> correspondence frame can be recovered across the six construction families, and its
> alignment-path mapper produces posterior-stratified residue calls, real ambiguity, reason-coded
> abstention, and a stable operational catalytic coordinate at state 262 in those construction
> data. The frame is not robust to `-M a2m`, has not been validated against independent
> residue-level truth, and has not yet demonstrated confirmatory transfer to a held-out
> non-GII-like lineage.

## 7 · Gate state

**UG25 SEALED · g4b BLOCKED · g5 BLOCKED · g6 NOT STARTED.** G2L remains development/diagnostic
evidence and may not be described as a confirmatory holdout.
