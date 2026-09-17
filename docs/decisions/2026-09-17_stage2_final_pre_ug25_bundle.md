# DECISION — FINAL_PRE_UG25_VALIDATION_BUNDLE built, reviewed: 7/10, class B

Date: 2026-09-17 · Track `rt07` · Status: **three bounded repairs required; UG25 still SEALED**

Bundle: `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/` — 39 files, frozen, locked.
External pinned root `eb3ac78f48aa0d33bd5fda3f40abcecc554adea40d9418a4f21c3aed67d5415c`
(`review-stage/roots/FINAL_PRE_UG25.root`, mode 444), manifest + sidecar in
`review-stage/manifests/`, all outside the bundle.

Reviewer: independent Codex (`gpt-5.6-sol`, xhigh, read-only), thread `01a0af1b`, 14m 50s.
Gate: `--score 7 --verdict almost` → `{"decision": "stop"}`. Freeze INTACT at review start and end.

**A first attempt was refused by the provider as a possible cybersecurity risk.** The prompt had
been written in penetration-testing language ("attack", "find a bypass", "defeat the anchor") for
what is a file-integrity checker on a research bundle. It was rephrased in
research-integrity terms and re-sent; **no verdict was inferred from the refusal**, and the gate
was not advanced for it.

Supersede by a new record, never by rewriting.

---

## 1 · v1 is formally marked FREEZE BROKEN

Recorded here and in `AUDIT.md` §2. v1 holds **164** files against a **162**-file manifest; a
`.pyc` post-dates its manifest by ~10 hours, written by the executor *importing* a module from it
during verification. Its 162 manifested scientific files remain content-identical, so **provenance
guarantees are broken; measurements are not.**

**v1 is not modified, not cleaned, not regenerated, and the `.pyc` files stay in place.** All
prior bundles are retained as historical evidence, defects included.

## 2 · The science is unchanged — confirmed by hash and by re-derivation

`code/mapper.py` sha256 `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef`,
byte-identical to v1 and v2. Reviewer-reproduced: `PP_LO` 0.50, `PP_HI` 0.75, `S_MIN` 10,
`K_MIN` 30, `T1` 0.32, `D_MAX` 0.48, `D_RANDOM` 0.067; `CAT_STATE` **262**, count **207**,
runner-up **136 @ 5**, agreement **207/210**; construction **217/219**. Controls independently
regenerated: MONO 219 composition-preserving, DI 216 with every adjacent-pair count preserved,
REV 219 exact reversals.

## 3 · What the clean room fixed, confirmed by the reviewer

- **Symlinks** now reported, not skipped: N5–N8 plus linked directories and dangling links all
  fail. (Executor also verified symlinked-directory and dangling cases independently.)
- **External root anchors integrity**: editing `mapper.py` in a copy and rebuilding *both* the
  manifest and its sidecar still fails with `EXTERNAL PINNED ROOT MISMATCH`. There is no unpinned
  verify mode.
- **Freeze negative matrix 18/18**, including bytecode-as-`ADDED` and hard-link aliasing.
- **UG25 sealing**: 8/8. No UG25 identifier or sequence bytes in any landed table; the pipeline
  names UG25 in no executable construct; the family list is a runtime input.
- Code executes from a temp copy, so the bundle is never the import root — the mechanism that
  mutated v1.

## 4 · Three blocking defects — all verified by the executor

### 4.1 C6 still passes several invalid states

Verified directly:

| input | result | should be |
|---|---|---|
| 80 valid + 0 failed of 84 attempted | **PASS** | FAIL — 4 replicates vanished |
| duplicate failed IDs `['a','a','a']` | **PASS** | FAIL |
| unknown class `BOGUS` carrying `NaN` | **PASS** | FAIL |
| more real observations than `n_eligible` | **PASS** | FAIL |
| `failed_ids` as a bare string `'oops'` | FAIL, **wrong reason** (counted 4 characters) | FAIL with a correct reason |

The accounting check is `len(vals) + n_failed > expected` — it catches **over**-accounting only.
**Under**-accounting passes because 80 ≥ the 76 minimum. That is precisely the "silently thinner
control class" the policy was written to prevent, and it can change a confirmatory C6 verdict.

### 4.2 A landed table embeds an absolute temporary path

`tables/freeze_negative_test_matrix.tsv` row N9 contains `/tmp/claude-1000/frz.MANIFEST`. Under a
different `TMPDIR` the regenerated row differs and **`verify.sh` exits 1** — as it did in the
reviewer's `/dev/shm` environment (18/19 matched). All *scientific* products matched. The
reviewer also notes the "17/17" figure is stale: the current script compares **19** products.

### 4.3 The UG25 predeclaration is stale

`control/UG25_PREDECLARATION.md` still describes the **superseded** arrangement — `scoped_loader.py`,
the public `AUTHORISATION_TOKEN`, `loader_equivalence.py` (line 22–25) — and names
`scripts/mapper_v2.py` rather than this bundle's `code/mapper.py` (line 76). Its C6 requirements
also exceed what the validator currently enforces. A confirmatory run must not be governed by a
predeclaration describing code that no longer exists.

## 5 · Disclosed, non-blocking

- `verify` reports its exclusions (`.claude`, `.mcp.json`); a symlink *inside* those declared
  exclusions is not flagged. Neither is on any import path and the pipeline copies only
  `code/*.py`, but the unqualified phrase "every symlink" is too strong.
- Mode-only changes and empty directories are outside the content model. Stated, not claimed.
- `loader.py` mentions UG25 in its docstring — no executable reference. The wording
  "contains **no** UG25 reference" should read "no executable UG25 reference".

## 6 · Supportable claim — unchanged

> Under the tested `hhmake -M 50` / `-M 60` match-state conventions, a compact GII-centred shared
> RT correspondence frame is recoverable across the six construction families. In those
> construction data the alignment-path mapper produces posterior-stratified residue calls,
> reachable ambiguity, reason-coded abstention, and a stable operational catalytic coordinate at
> HMM state 262.

Not robust under `-M a2m`; no independent residue-level accuracy; no general biological
specificity; no confirmatory transfer to a held-out non-GII-like family.

## 7 · Required before UG25 — NOT AUTHORISED, NOT STARTED

1. C6: require exactly the expected class keys; unique, non-blank, list-valued failure IDs;
   `n_valid + n_failed == n_attempted` per class; reject impossible real-vector cardinalities;
   regression test each case above.
2. Bind real and control counts to sequence identities so an omitted or duplicated observation
   cannot alter C6 silently.
3. Supersede the UG25 predeclaration with the actual `code/loader.py` runtime-authorisation
   design, `code/mapper.py`, and the disclosed audit-only UG25 read; preserve every scientific
   threshold; issue a new external manifest and root.

Optional: strip absolute temp paths from the landed freeze table and correct the denominator to
19; type-check before applying exclusions; recompute the manifest-body root so a rebuilt sidecar
cannot hide comment or size edits.

## 8 · Gate state

**UG25 SEALED · g4b BLOCKED · g5 BLOCKED · g6 NOT STARTED.**
