# Retro — dbchar_g7_stage1_report (2026-09-15)

Bundle: `results/dbchar_g7_stage1_report/` — REPRODUCIBLE, human_input_audit PENDING.
5 tables, 4 figure files, `REPORT.html` + `REPORT.md`, rerun 1.2 s.

## What happened

- The Stage-1 closeout report over the seven landed measurement gates. It computes no scientific
  result: 70 declared values are each resolved from a landed table of a landed bundle by an exact
  row selector, and a selector matching anything other than one row fails the build, as does a
  placeholder with no lookup and a `{...}` surviving into the finished HTML.
- Every resolved value is landed as `g7_resolved_values.tsv` (key, bundle, table, selector, column,
  raw string, rendered string), so a number in the prose can be traced to its row without reading
  the prose.

## What went wrong

**The validators all passed on a report with two unreadable figures.** `bundle_valid.sh`,
`clone_safe.sh`, BS-13's figure/TSV pairing and the byte-for-byte rerun were all green. What found
the defect was rendering the page and looking at it — the inspection the launcher requires and
which I had queued as the last item rather than the first.

- `dbchar_g3_pair_geometry/fig01_distance_distribution`: raw-float bin labels rotated into the
  denominator stamp, the two panels' stamps overlapping each other.
- `dbchar_g4_family_baseline/fig01_rt_length_by_family`: the denominator stamp placed at −0.22
  axes fractions of a 25-row axis, i.e. a ~2-inch band of white between the plot and its stamp.

Both are landed bundles, so neither was edited. `REPORTING_STANDARDS` routes a restyle into a new
gate reading the landed table, which is what `f01_restyle_figures.py` does: it reads only the TSV
each figure shipped beside itself and re-emits those rows verbatim. The only transformation
applied to a number is a label format.

Two smaller ones, also found by looking rather than by a check:
- a section title written as `RT&harr;ncRNA`, which the HTML escaper correctly turned into visible
  markup — titles now carry the literal character;
- the closing paragraph claimed **eleven** registered derived datasets where **sixteen** exist.
  That is how the four unregistered g4/g6 datasets were found; they are now in `data/README.md`,
  and the count is asserted against the bundle registries at build time instead of typed.

Separately: matplotlib salts SVG element ids from a random seed and stamps a `<dc:date>`, so the
figures were not byte-reproducible and this gate could not have passed its own stop condition
until `svg.hashsalt` was declared and the metadata suppressed.

## Proposal (not an amendment — WA-S.2)

**A gate that lands a figure must record that a human looked at the rendered figure, and at what
size.** BS-13 requires a figure to have a producing script and a landed TSV; nothing requires that
anyone ever saw it. Both figures here were correct by every mechanical check and unusable.
- *Would have caught:* both defects, and would have caught them in g3 and g4 rather than two gates
  later in the report that embeds them.
- *Would wrongly reject:* a gate landing a figure intended only as machine input — e.g. a diagnostic
  raster consumed by a later script — which would have to declare `n/a - not for reading`.

## What is retained rather than fixed

In the landed `fig03_direction_by_family`, the legend box covers the `n=` label of the third row.
The number is in `g3_direction.tsv` and the row is legible; re-plotting a third figure to recover a
label the table already carries is not worth a fourth landed figure.
