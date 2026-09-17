# REVIEW REQUEST — clean pre-UG25 validation bundle

**Question: is this execution/provenance envelope sound enough to authorise the single-shot
UG25 confirmatory run?** Not a re-review of the scientific mapper, which was accepted; not a
request to rehabilitate v1 or v2.

Bundle: `results/FINAL_PRE_UG25_VALIDATION_BUNDLE/` — frozen, locked, 39 files.

```
EXTERNAL PINNED ROOT (hold this independently of the bundle):
eb3ac78f48aa0d33bd5fda3f40abcecc554adea40d9418a4f21c3aed67d5415c

manifest : review-stage/manifests/FINAL_PRE_UG25.MANIFEST        (mode 444)
sidecar  : review-stage/manifests/FINAL_PRE_UG25.MANIFEST.sha256 (mode 444)
root file: review-stage/roots/FINAL_PRE_UG25.root                (mode 444)
```

Verify with:
```
python3 -B results/FINAL_PRE_UG25_VALIDATION_BUNDLE/code/integrity.py \
  verify results/FINAL_PRE_UG25_VALIDATION_BUNDLE \
  review-stage/manifests/FINAL_PRE_UG25.MANIFEST \
  eb3ac78f48aa0d33bd5fda3f40abcecc554adea40d9418a4f21c3aed67d5415c
```
There is **no unpinned verify mode**. Report any root change as a freeze violation.

## Why a clean room

Your last two reviews found the defects concentrating in the provenance envelope, not the
science: post-freeze bytecode mutation, symlink invisibility, fail-open manifest/root handling,
a mutable manifest anchor, pre-run UG25 materialisation, C6 accepting NaN, unlanded failed-control
IDs. The operator authorised one clean room rather than another patch cycle. **Historical bundles
are untouched audit history, including their defects.**

## 1 · The science is unchanged — by hash

```
69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef  code/mapper.py          (this bundle)
69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef  v2/scripts/mapper_v2.py
69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef  v1/scripts/mapper_v2.py
```

Reproduced values, all identical to v2: `PP_LO` 0.50, `PP_HI` 0.75, `S_MIN` 10, `K_MIN` 30,
`T1` 0.32, `D_MAX` 0.48, `D_RANDOM` 0.067; `CAT_STATE` **262**, MAPPED-only count **207**,
runner-up **136 @ 5**, agreement **207/210 = 0.9857**; construction **217/219**.

## 2 · v1 is formally marked FREEZE BROKEN

Recorded in `AUDIT.md` §2 and in the decision record. v1 holds 164 files against a 162-file
manifest; a `.pyc` post-dates its manifest by ~10 hours, written by the executor *importing* a
module from it. Its 162 manifested scientific files remain content-identical, so **provenance
guarantees are broken, measurements are not**. v1 is not cleaned, not regenerated, not modified.

## 3 · What to attack

Please verify by execution, on **copies in your own temp directory**:

- **Symlinks** — `tests_freeze.py` N5–N8 cover added symlink, symlink replacing a registered
  script, symlink escaping the bundle root, symlink to another registered artifact. v2 *skipped*
  symlinks and reported INTACT. Try to find a link-shaped bypass these miss.
- **External root** — N12 (all-zero), N13 (wrong root), N14 (absent root), and decisively **N15**:
  a bundle whose files, manifest **and** sidecar are all rebuilt together still fails against the
  externally held root. Try to make a modified bundle self-validate.
- **C6 input validation** — `tests_c6.py` I1–I14 cover NaN, Inf, negative, non-integer,
  non-numeric, zero/negative/non-integer denominators, malformed failed-ID lists, inconsistent
  accounting and an invalid design parameter. Try to find an invalid input that returns PASS.
- **UG25 sealing** — `code/loader.py` has **no** UG25 reference, no sealed list, no token; the
  authorised families come from `RT07_AUTHORISED_FAMILIES` at runtime and the pipeline fails
  closed if unset. `sealing_proof.py` reports **8/8 SEALED**. Check that the claim made is
  *"UG25 SEALED FROM DEVELOPMENT EXECUTION"* and **not** "UG25 was never read" — the sealing
  audit itself deliberately loads UG25 to search for leaks, and says so. Judge whether that is
  honest and correctly scoped, or whether it reintroduces the v2 problem.
- **Bytecode** — `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `PYTHONPYCACHEPREFIX` outside the
  bundle, code executed from a temp copy so the bundle is never the import root, `__pycache__`
  **not** excluded from the manifest (N16).
- **Determinism** — `verify.sh` reproduces into a separate temp dir and diffs; 17/17 products
  byte-identical. Note the family iteration order is load-bearing (a shared RNG feeds control
  generation); a sorted order produced a *different* di-shuffle failure set, so the historical
  order is preserved verbatim.

## 4 · Landed results

- **Controls, per class** (max / p95): mono 17/0, di 24/0, **reverse 25/10**, pooled 25/**0** —
  the pooled p95 hides the reverse tail, which is why C6 is per-class.
- **Failed di-shuffle IDs landed**: `ADE85031.1_CRISPR`, `ESQ17084.1_CRISPR`,
  `WP_032822382.1_UG3`. Never substituted.
- Tests: mapper **14/14** (12 falsifiable, 2 invariants), C6 **21/21**, freeze **18/18**,
  sealing **8/8**, reproduction **17/17**, `VERIFY OK`.

## 5 · Honest limits, stated in `AUDIT.md` §4 and §7

Cryptographic detection is claimed; **OS-level immutability is not**, because this environment
cannot provide it — the process runs as the owner and the manifest's parent directory is
owner-writable. The trust anchor is the root value you hold out-of-band. C4 remains weak
(`D_MAX` 0.48 vs null 0.067) and a C4 pass is explicitly non-evidential. Controls are synthetic
only; unrelated natural proteins were deferred rather than added after C6 was frozen.

## 6 · Questions

1. Is the scientific mapper unchanged?
2. Is catalytic aggregation correct (MAPPED-only)?
3. Are ambiguity and abstention logic correct?
4. Does family-scoped loading truly seal UG25 from development execution?
5. Does C6 fail closed on every invalid input?
6. Are all three control classes correctly represented?
7. Are the failed di-shuffle IDs landed?
8. Are symlinks and bytecode visible to provenance?
9. Does the external pinned root actually anchor integrity?
10. Does the verifier fail on every declared corruption test?
11. Is clean reproduction deterministic?
12. Does the construction claim remain supported?
13. Is the UG25 predeclaration frozen and falsifiable?

## 7 · Required verdict

`PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL/BLOCK`, numeric score, and exactly one of:

- **A** `CLEAN PRE-UG25 BUNDLE PASSES — AUTHORISE SINGLE-SHOT UG25`
- **B** `BOUNDED DEFECT REMAINS — REPAIR BEFORE UG25`
- **C** `VALIDATION INFRASTRUCTURE UNSOUND — STOP CONFIRMATORY PATH`

Tag every requested change `REQUIRED BEFORE UG25` or `OPTIONAL / FUTURE STRENGTHENING`. Under the
operator's hard-stop rule, only defects compromising mapper correctness, UG25 sealing,
confirmatory interpretation or bundle integrity may block UG25; optional provenance refinements
may not. **Do not modify any bundle.**
