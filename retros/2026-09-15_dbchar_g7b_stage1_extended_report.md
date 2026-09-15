# Retro — dbchar_g7b_stage1_extended_report (2026-09-15)

Bundle: `results/dbchar_g7b_stage1_extended_report/` — REPRODUCIBLE, human_input_audit PENDING.
112 tables, 68 figure files, `REPORT.html` + `REPORT.md`, rerun ~3 min, byte-identical.

## What happened

The operator asked for a second, richer Stage-1 reporting product beside the g7 closeout report:
a scientific synthesis built only from landed Stage-1 data, with no change to g1–g7. The result
is 13 sections, 34 figures and 112 landed tables, with 153 values resolved into the prose by
g7's resolver contract.

The plan (`FIGURE_AND_ANALYSIS_PLAN.md`) was written and landed **before** any analysis ran, with
priorities and a declared data gap; it dropped eight ideas from the older reference report with
reasons, and retained five as re-derivations.

## What the bundle had to defend against, and how

A reporting layer over landed gates has one characteristic failure: quietly disagreeing with the
gate it reports on. `c01_reconcile.py` re-derives 294 quantities **from the derived parquet
datasets** and compares each against the landed table's value, exiting non-zero on any
disagreement. It fired once, honestly:

- **Retron loci carrying an ncRNA: landed 333,838, my recount 333,733.** Not a g3 defect. g3's
  coverage rule is record-level (`len(ncrnas[]) > 0` on any first-copy record of the locus); I had
  recounted at placement level, where 1,409 geometry-ineligible placements drop out. The check now
  uses g3's own rule, and the three coverage rules are landed side by side in
  `t42_definition_differences.tsv` as a *declared difference*, not a correction. The instinct to
  "fix" the smaller number would have silently redefined a Stage-1 statistic.

## What went wrong in my own work

Three defects, all found by looking rather than by a validator:

1. **A twin counted as two ncRNAs.** The first zero-call view counted *placements* per physical
   locus, so a locus deposited in both RefSeq and GenBank carried "2 ncRNA calls" — 46,071 loci in
   the twin stratum. Found by reading the figure and noticing that the twin row was the only one
   with a large "2" class. The landed version counts distinct exact ncRNA sequences; genuine
   two-sequence loci number 63 in ncbi_bacteria.
2. **A hardcoded total in a figure label, and it was wrong** (282,969 for a population of
   297,793). Every total in a figure label now resolves from a landed table. This is the same
   class of defect g7's retro records (a typed count in prose); it recurred here in an axis label.
3. **A positive control with the wrong expectation.** The Wilson control asserted 0.3983/0.6017
   for 50/100; the correct interval is 0.4038/0.5962. The control failed, the estimator was right,
   and my reference values were wrong. Recorded in the README rather than quietly corrected.

Eleven figures were re-plotted after visual inspection (label collisions, a legend crossing a
title, overlapping translucent bars, a hexbin distorted by setting the axis scale after plotting,
pooled overflow bins creating false spikes). None of these was caught by a check.

## What I could not do

**The assembled `REPORT.html` was never seen rendered.** Every one of the 34 figures was inspected
as an image, and the page was verified structurally, but the only browser on this machine is a
snap-packaged Firefox that cannot start in this execution environment, with or without the command
sandbox, and installing a headless renderer was out of scope. The README says so in §8 rather than
implying the page was viewed. That is the one acceptance step left for the operator.

## What is worth carrying forward

- **Declare the unit three times.** Enforcing `unit`/`denominator` at table-write time (a table
  cannot land without them) made the whole-report discipline automatic rather than remembered.
- **A reporting layer needs a reconciliation, not a second count.** 294 exact comparisons against
  the gates it reports on, build-stopping, is the analogue of WA-D.3 for a view layer.
- **The interesting findings came from re-counting at a different unit**, not from new analysis:
  the 1 kb upstream mode collapsing from 118,275 placements to 1,908 exact pairs, and the Retron
  zero-ncRNA class tracking available upstream window context (0.78% → 60.5%).
