# Retro — dbchar_g2b_rt_cds_recovery (2026-09-15)

Bundle: `results/dbchar_g2b_rt_cds_recovery/` — REPRODUCIBLE, human_input_audit PENDING.
Rerun 37.8 s.

## What happened

- The operator's population rule required the 31,504 RT-anchored records with no RT CDS to be
  classified rather than dropped. All 31,504 are classified and all are retained:
  **14,188 RECOVERED** (RT coordinates reconstructed and verified by back-translation against the
  window DNA), **16,688 SEQUENCE_ONLY** (a usable RT sequence but no defensible genomic context —
  every one contig-end-clipped, 9,128 lying wholly beyond the contig the extractor retrieved),
  **628 ILL_POSED**.
- Per-record eligibility flags carry the consequence forward: a SEQUENCE_ONLY record is eligible
  for exact-RT statistics and ineligible for geometry, and the denominator effect is stated
  wherever it applies. Nothing was globally deleted.

## What went wrong

- **My Biopython cross-check read 34.6% agreement** and I nearly reported a failed verification.
  The harness was comparing under a stricter rule than g2's *declared* recoding classes — it
  demanded exact identity where the declared equivalence allows `alt_start`, `code4_tga_trp` and
  `internal_stop_masked`. Re-implemented the declared equivalence independently: **99.95%**, with
  the frame-shift control at 0. An independent check has to be independent of the implementation,
  not of the definition.
- **`representation_class` was computed from `anchor_center`**, which put an RT lying wholly
  outside the window into the "crosses the window boundary" class. The positive control caught it.
  Replaced with an interval-intersection test — and the fixture was fixed too, because the first
  version of the fixture only moved the RT coordinates and left the anchor fields agreeing with
  the old answer.

## Proposal (not an amendment — WA-S.2)

**A fixture that a broken implementation still passes is not a fixture.** When a control is added
for a defect, the retro should record the *fixture edit* as well as the code edit, and the control
table should carry a column naming the field the fixture perturbs.
- *Would have caught:* this gate's first fixture, which perturbed RT coordinates but left
  `anchor_center` consistent with the wrong answer, so the broken code passed.
- *Would wrongly reject:* a control whose fixture legitimately perturbs nothing — a pure
  invariance check — which would have to declare `n/a - invariance`.

## Carried into later gates

`recovery_class` and `representation_class` are join keys for g3's geometry eligibility; the
16,688 SEQUENCE_ONLY records are the population behind g3's contig-start-clipping finding.
