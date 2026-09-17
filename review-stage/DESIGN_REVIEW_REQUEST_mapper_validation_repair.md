# INDEPENDENT REVIEW REQUEST — repaired mapper validation, before the UG25 confirmatory holdout

Track `rt07`, Stage 2. Bundle under review: `results/rt07_mapper_validation_repair/` — **frozen,
locked read-only, manifest-hashed**. Reviewer must be independent of the executor (WA-A.5).

**Verify. Do not accept the operator summary.** The last review's decisive findings were things
the executor's own summary asserted and the reviewer disproved. Re-derive the numbers.

## 0 · Freeze state at the moment this review opens

```
rt07_mapper_validation_repair   ROOT_SHA256 2f0cacc5793e46bdb0b9d0924278f42ceaceb0eecd1c87075700ae2c9f3efe6a  (162 files)
rt07_residue_mapper_gate        ROOT_SHA256 e6eb62bdd80ca691ebd13507d7cabad2063f62374fba294028adcaa6ea41cce1  (132 files)
PRE_REVIEW_UTC = 2026-09-16T22:32:15Z
```

Manifests are **outside** the bundles they cover, at `review-stage/manifests/`. Check them:

```
python3 results/rt07_mapper_validation_repair/scripts/freeze_manifest.py \
    verify results/rt07_mapper_validation_repair \
    review-stage/manifests/rt07_mapper_validation_repair.MANIFEST
```

**If either root hash differs from the above at any point, report a freeze violation and treat
the review snapshot as invalid.** The previous review caught the executor adding a file to a
frozen bundle mid-review; that is why this section exists.

## 1 · What happened last round

Independent review returned **`FAIL/BLOCK`, 4/10**, classification **C** — "the mapper itself
remains inadequately validated for transfer". Confirmed defects:

- criterion 2 claimed MET with **no score rule of any kind** in the code;
- `ambrows` declared and never populated — **no ambiguity notion at all**;
- criterion 3 reported `NOT TESTABLE` when it was testable and **passes** (the executor
  substituted an anchor-proximity test for the declared alignment-path test);
- `T6` returned `True` on every branch — a test that could not fail;
- the `≥5` selection cutoff was the exact winner-flip point between UG25 and G2L;
- the executor **mutated the frozen bundle during review**.

The mapper's *alignment-path* implementation was found sound and interpolation-free; that part is
carried forward unchanged. This bundle is the repair of everything else.

## 2 · Claims to verify (each is independently checkable)

### Support rule — construction only
`PP_LO` 0.50 (fixed by principle, not searched) · `PP_HI` **0.75** · `S_MIN` **10** ·
`K_MIN` **30** · `T1` **0.32** · `D_MAX` **0.48** · `D_RANDOM` **0.067**.
Grid for `PP_HI` = `{0.55, 0.65, 0.75, 0.85, 0.95}`, landed **with failures visible**
(0.55 → negative p95 12; 0.65 → 8). Check the grid is exhaustive and minimality is real — the
project has a prior errata where "8.0 is the smallest threshold" was false because the grid
skipped 6 and 7.

### Call states
`MAPPED` (PP ≥ 0.75) · `AMBIGUOUS` (0.50 ≤ PP < 0.75) · `UNSUPPORTED` (< 0.50) ·
`DELETED_STATE`. **Only `MAPPED` may contribute positive evidence** — verify `AMBIGUOUS` is never
summed into a success count anywhere.

### Ambiguity is real
Claim: 1346 `AMBIGUOUS` calls across 45/45 construction sequences (test U9). Verify the band is
reachable and that U9 could fail if it were not.

### Catalytic rule
`CAT_STATE = 262`, modal state across **210** dyad-bearing construction sequences with
**207/210 = 98.6%** agreement, predeclared falsification floor **0.80**, runner-up state has
**5** occurrences. Verify this is derived from construction only and that the multi-motif case is
resolved by state→residue correspondence, not motif-first matching (test U8).

### Tests
13 mapper tests (11 falsifiable, 2 invariants) + 9 freeze tests, all passing. Verify each
falsifiable test **can actually fail** — the previous suite's T6 could not. Verify the two
`IMPLEMENTATION_INVARIANT` tests (U11 reversibility, U12 monotone order) are excluded from
transfer evidence.

### Verifier and freeze
`verify.sh`: 14/14 computed products byte-identical, regenerates into a temp tree, never writes
into the bundle. `freeze_manifest.py`: detects added / removed / changed / renamed. Verify the
ADDED case specifically — a content-only checksum list would miss it, and ADDED is the breach
that actually occurred.

### Negative controls
mono-shuffle / di-shuffle / reverse, max `MAPPED` anchors **17 / 24 / 25** respectively. The G2L
gate used mono-shuffle only. Verify the di-shuffle preserves dipeptide composition exactly, and
that the **3 disclosed di-shuffle failures** (CRISPR 2, UG3 1) are excluded transparently rather
than silently replaced by a weaker control.

### Carried-forward corrections
Retrons components **93/1/1**; shared core **7.5–27.5%** of full consensus; `-M 50`/`-M 60`
retain the frame while `-M a2m` leaves DGRs and AbiA with **zero** `ALL_PARTNERS` positions and
GII with 115. Confirm these are still consistent across the landed bundles and that no stale
superseded value is being relied on.

### UG25 is sealed
Claim: no UG25 object was read for any purpose. Verify by your own search across scripts, tables
and `work/`, not by reading the claim.

## 3 · Questions — answer each explicitly

1. Was the support/scoring rule derived entirely from construction/development data, and not from
   G2L or UG25 outcomes?
2. Are the four posterior-based call states implemented as declared?
3. Does only `MAPPED` contribute positive mapping evidence?
4. Is the ambiguity logic real and falsifiable, rather than a declared-but-unused container?
5. Are abstentions reason-coded correctly, and are both reason codes reachable and distinct?
6. Was the catalytic-state rule derived from construction data only (`CAT_STATE = 262`, 207/210),
   and are multi-motif cases resolved by state→residue correspondence rather than motif-first?
7. Are the synthetic/unit tests genuinely capable of failing?
8. Are the two `IMPLEMENTATION_INVARIANT` tests correctly excluded from transfer evidence?
9. Are the 13 mapper tests and 9 freeze tests implemented as described?
10. Does the verifier authenticate registered inputs/scripts/control files, reproduce all computed
    outputs, compare against frozen outputs, fail on drift, and leave the bundle unmutated?
11. Does the freeze mechanism detect added, removed, modified, renamed files, and script drift?
12. Are manifests genuinely external to the bundles they protect?
13. Do the corrected denominator/identifier repairs remain valid (Retrons 93/1/1; 7.5–27.5%)?
14. Is the `-M` sensitivity reported correctly, and is the claim narrow enough given that `-M a2m`
    removes `ALL_PARTNERS` support for DGRs and AbiA?
15. Is *"a compact GII-centred shared RT correspondence frame can be recovered under the tested
    match-state definitions"* supported and appropriately limited?
16. Are the construction validation numbers and family differences correctly calculated and
    interpreted?
17. Are the three decoy/control classes implemented correctly, and is their role scientifically
    appropriate?
18. Are the disclosed di-shuffle failures handled transparently?
19. Is the UG25 predeclaration sufficiently prospective and frozen?
20. Has UG25 genuinely not been evaluated or used for calibration?
21. Are the seven numeric UG25 criteria sufficiently falsifiable and not outcome-tuned?
22. Is criterion C4 correctly acknowledged as weak rather than overinterpreted? (The executor kept
    the predeclared `D_MAX = 0.48` rather than substituting the tighter same-population null
    `D_RANDOM = 0.067`, on the grounds that swapping a predeclared criterion after seeing
    calibration output is what sank UG5 v2. Judge whether that was the right call.)
23. Can UG25 now serve as a single-shot confirmatory holdout?
24. Is any additional repair **REQUIRED** before opening UG25?

## 4 · Classification — choose exactly one

- **A** `MAPPER VALIDATION PASSES — UG25 MAY BE OPENED AS THE FINAL CONFIRMATORY HOLDOUT`
- **B** `MAPPER VALIDATION PASSES WITH BOUNDED REQUIRED REPAIRS — UG25 MUST REMAIN SEALED UNTIL THOSE REPAIRS ARE VERIFIED`
- **C** `MAPPER VALIDATION FAILS — CURRENT SCORING/AMBIGUITY FRAMEWORK IS NOT READY FOR CONFIRMATORY HOLDOUT`

**Every requested change must be classified `REQUIRED BEFORE UG25` or
`OPTIONAL / FUTURE STRENGTHENING`. No "nice to have" language for load-bearing issues.**

## 4b · Known post-freeze defect, disclosed by the executor — please classify it

Found by the **executor**, while the first review attempt was running, and deliberately **not
patched**:

> When the verifier's manifest is absent, `verify.sh` currently prints a "no manifest yet" message
> and can still exit `VERIFY OK`.

The manifest check sits behind `if [ -f "$MAN" ]; then … else echo "(no manifest yet…)"; fi`, and
the `else` branch does not set `status=1`. So a bundle with **no provenance at all** verifies
clean. Absence of provenance should fail closed.

It was not fixed because the bundle was frozen and under review, and patching a frozen bundle
mid-review is the exact violation the executor committed in the previous round. It is recorded
externally in `docs/BLOCKED.md`.

**Classify this defect as `REQUIRED BEFORE UG25` or `OPTIONAL / NON-BLOCKING`**, and state
whether the otherwise-demonstrated freeze behaviour (added / removed / changed / renamed all
detected, manifests external, both bundles verifying INTACT across a live 12-minute external
review session) is sufficient to review **this** snapshot — whose manifest **does** exist and
**does** verify.

## 5 · Required verdict

`PASS` / `PASS_WITH_REQUIRED_REPAIRS` / `FAIL/BLOCK`, numeric score out of 10, the A/B/C
classification, load-bearing findings, required repairs, optional improvements, the exact
supportable scientific claim in your own words, whether UG25 may now be run, whether g4b remains
blocked, whether g5 remains blocked.

Be adversarial. Prefer finding a real defect over endorsing. **Do not modify any file in any
bundle** — write nothing; report findings in your reply only.
