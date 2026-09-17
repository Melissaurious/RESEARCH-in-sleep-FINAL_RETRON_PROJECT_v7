# Clean-room audit record — FINAL_PRE_UG25_VALIDATION_BUNDLE

Date: 2026-09-17 · Track `rt07` · Purpose: **a trustworthy execution/provenance envelope for
an already-defined mapper, before the single confirmatory UG25 run.** Nothing scientific is
redesigned here.

## 1 · The scientific mapper is unchanged — by hash

`code/mapper.py` is byte-identical to the accepted construction mapper:

```
69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef  code/mapper.py                     (this bundle)
69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef  rt07_mapper_validation_repair_v2/scripts/mapper_v2.py
69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef  rt07_mapper_validation_repair/scripts/mapper_v2.py
```

Preserved unchanged: `-M 50` operational implementation and the `-M 60` / `-M a2m` sensitivity
statement; the four posterior call categories; `PP_LO` 0.50; `PP_HI` 0.75; the score/support
rule; ambiguity and abstention rules; `CAT_STATE` 262; the construction-derived catalytic rule;
the six construction families; the frozen 150 `ALL_PARTNERS` anchors. No G2L or UG25 tuning.

## 2 · Historical bundles are audit history, including their defects

- **v1 (`rt07_mapper_validation_repair`) — FREEZE BROKEN.** Post-freeze Python bytecode was
  written into it by the executor, ~10 hours after its manifest, by *importing* a module from
  it during verification. It holds 164 files against a 162-file manifest.
  **v1 is no longer a valid immutable review artifact.** Its 162 originally manifested
  scientific files remain content-identical, so the violation affects **provenance guarantees,
  not the underlying measurements**. It will not be modified, cleaned or regenerated, and the
  `.pyc` files are deliberately left in place.
- **v2 (`rt07_mapper_validation_repair_v2`)** remains as landed, with the defects the reviewer
  identified (symlink blindness, writable manifest anchor, UG25 materialised by its own
  verification path, C6 accepting NaN).
- **G2L and UG5 bundles** remain as landed, including the failed gates.

No historical bundle is patched. This clean room is the only candidate for final pre-UG25
validation.

## 3 · Execution envelope

- `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`, with `PYTHONPYCACHEPREFIX` redirected out of
  the bundle.
- **Code is copied to a temp location and executed from there.** The frozen bundle is never
  the import root — importing from a frozen bundle is exactly what mutated v1.
- Symlinks: refused at build, and a violation at verify.
- Hard-linked (aliased) files: refused at build, and a violation at verify.
- `__pycache__` is **not excluded** from the manifest, so any stray bytecode is an `ADDED`
  violation rather than an invisible file.
- Every manifest exclusion is **printed by `verify`**; the only exclusions are the
  sandbox-injected `.claude/` directory and `.mcp.json` (a character device owned by nobody).

## 4 · What is cryptographically detected vs what is only a permission

**Detected cryptographically:** any change to file content, any added or removed file, any
rename, any symlink, any hard-link alias, any manifest edit (detached sidecar), any
manifest-root disagreement, and — decisively — a **jointly rebuilt bundle + manifest +
sidecar**, which still fails against the externally held root (`tests_freeze.py` N15).

**Only a filesystem permission, not immutability:** the 444 modes on files and 555 on
directories. This process runs as the owner and could chmod them back. The manifest's parent
directory is likewise owner-writable.

**The actual trust anchor is the root value held outside the bundle** — written to
`review-stage/roots/FINAL_PRE_UG25.root` and quoted in the review request, so the reviewer
holds it independently of anything the bundle can rewrite. `verify.sh` has **no unpinned
mode**. This is stated plainly rather than claimed as OS-level immutability, which this
environment cannot provide.

## 5 · UG25 sealing — precise wording

> **UG25 SEALED FROM DEVELOPMENT EXECUTION.**

Not *"UG25 never existed in the source collection"* — it is present in the shared collection
file, and any claim otherwise would be false for the same reason the two previous claims were.

`code/loader.py` contains **no** UG25 reference, no sealed-family list and no authorisation
token. The authorised development family list is read from `RT07_AUTHORISED_FAMILIES` at
runtime; absent or empty, the pipeline **fails closed**. A source-tree edit alone cannot widen
the scope.

`code/sealing_proof.py` is the post-development audit that searches for leaks. It is the only
file permitted to name the sealed family, it is not part of the pipeline, and it builds no
alignment, profile or score.

## 6 · Reproduction discipline

Before freeze: build from registered inputs → run pipeline and all test suites → land tables →
freeze → external manifest and root → review mode. After freeze: reproduction happens **only**
in a separate temp directory, the frozen bundle is read-only reference, and `verify.sh`
compares the temp reproduction against the frozen expected outputs.

## 7 · Known, disclosed limitations

- **Criterion C4 remains weak** (`D_MAX` 0.48 vs the same-population null `D_RANDOM` 0.067) and
  is kept as predeclared. A C4 pass is close to uninformative and must not be presented as
  evidence.
- **Negative controls are synthetic only** — mono-shuffle, di-shuffle, reverse. They establish
  separation from sequence-order disruption, **not** general biological specificity. Unrelated
  natural proteins and distant RT families were classified `OPTIONAL — DEFER` because adding a
  control class after C6 was frozen would change the confirmatory design.
- **Family iteration order is load-bearing.** A single shared RNG feeds control generation, so
  visiting families in a different order changes which di-shuffles fail. The historical order
  is preserved verbatim; this was found when a sorted order produced a *different* failed-ID
  set (2 UG3) from the established one (2 CRISPR + 1 UG3).
- The construction C6 demonstration uses **1** replicate per sequence; the UG25 design
  specifies **3**. The design parameter is passed explicitly at every call site, never inferred.
