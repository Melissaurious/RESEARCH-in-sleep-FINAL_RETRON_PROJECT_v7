# NOTE 2026-09-16 — the "99.8 % same strand" figure in the g7 report prose

**Status:** workbench observation. Not a gate finding, not a correction to a landed bundle.
Raised for the operator to decide what, if anything, to do.

## What was observed

`results/dbchar_g7_stage1_report/REPORT.md` §4 states that canonical RT–ncRNA placements are

> "on the same strand in 99.8% of cases"

Recomputing that quantity from `data/derived/rt_ncrna_pairs_v1.parquet` on the `CANONICAL`
placement population (n = 344,154) gives **99.116 %** same-strand (341,113 same / 3,041 opposite).

That recomputation **agrees exactly** with the landed gate table
`results/dbchar_g3_pair_geometry/tables/g3_same_strand.tsv`, population `CANONICAL`:

| direction | same_strand=True | same_strand=False |
|---|---|---|
| upstream | 322,305 | 2,964 |
| overlapping | 12,108 | 16 |
| downstream | 6,700 | 61 |
| **total** | **341,113** | **3,041** |

341,113 / 344,154 = **99.1164 %**.

## Why the prose differs

The string is a **hard-coded literal** in the report generator:

`results/dbchar_g7_stage1_report/scripts/findings.py:190`

```
{overlap} overlapping, at a median gap of {up_median} bp, on the same strand in 99.8% of
```

Every other number in that sentence (`{placements}`, `{canonical}`, `{up}`, `{down}`,
`{overlap}`, `{up_median}`, `{cds0}`, `{cds1}`, `{cds_gt3}`, `{pairs}`, `{pairs_1to1}`) is a
placeholder resolved from the value registry. `99.8%` is the only one that is not, and
consistently there is **no `same_strand` key in `g7_resolved_values.tsv`** — so the figure never
passed through the registry and never had a named bundle/table/selector behind it.

## Consequence for this workbench

The gate table is the authority; the prose is not. This workbench reports **99.12 %**, checks it
against `g3_same_strand.tsv`, and prints an explicit `[ NOTE]` line wherever the quantity appears
(notebook section D1, interpreted in D3).

## Open for the operator

1. Whether the g7 REPORT.md sentence should be corrected by a new record (landed bundles are not
   silently rewritten).
2. Whether `same_strand` should be added to `g7_resolved_values.tsv` so the quantity acquires a
   registered provenance like every other headline number.

Nothing in the g3 bundle itself is affected — its table is correct and internally consistent.
