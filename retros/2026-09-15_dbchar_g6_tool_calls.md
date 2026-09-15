# Retro — dbchar_g6_tool_calls (2026-09-15)

Bundle: `results/dbchar_g6_tool_calls/` — REPRODUCIBLE, human_input_audit PENDING.
16 tables, rerun 78.3 s.

## What happened

- The per-tool call matrix over 663,308 distinct Retron records: myRT 92.77%, PADLOC 68.37%,
  DefenseFinder 67.71%, all three 53.17%. Every Retron record carries at least one tool.
- `system_subtypes` carries **two tools' vocabularies in one field**. The project's standing
  case rule (capital-initial = DefenseFinder, lowercase = PADLOC) **partitions the field exactly**:
  zero strings fall outside it, and every record a tool detected carries that tool's label. Each
  vocabulary is landed separately and the field is never pooled.
- The finding that constrains every other gate: **ncRNA carriage varies 6.6-fold with the tool
  combination** — 89.23% for myRT+PADLOC against 13.50% for myRT alone. A tool-defined subset of
  this corpus is not a random subset, and any ncRNA rate computed on one inherits that selection.
  The prior project named this confounder; here it is measured.

## What went wrong

- **The second count compared grains, not numbers.** The producing script reports first-copy
  (deduplicated) counts; awk over the raw bytes necessarily sees every line, duplicates included.
  The first comparison disagreed by exactly the duplicate lines and I initially read it as a defect
  in one of the routes. Withdrawn, and `g6_tool_matrix_retron_all_records.tsv` landed beside the
  deduplicated table so the comparison is grain-matched on both sides.
- The PADLOC/ncRNA reading was **weakened from an explanation to a `PROPOSED:`**. If PADLOC's
  retron rule is itself ncRNA-model-driven, then "PADLOC called it" and "an ncRNA was found" are
  close to the same event, and the 89% vs 13% contrast measures a rule rather than biology. The
  corpus carries no per-tool provenance detail that separates these, so both readings ship.

## Proposal (not an amendment — WA-S.2)

**A second-count table must name the grain of both routes in its own columns**, not only in
`MANIFEST.tsv`. Two routes over the same population at different grains produce a disagreement
that looks exactly like a measurement error, and the reconciliation table is where a reader will
look first.
- *Would have caught:* this gate's first reconciliation, where a real 8,511-duplicate-line gap read
  as a bug in the awk route.
- *Would wrongly reject:* a reconciliation where both routes are trivially at the same grain —
  most of them — which would carry two identical columns for no gain.

## Carried into later gates

The extraction asymmetry is the selection effect every ncRNA rate in Stage 1 sits inside; it is
stated in the g7 report's section 8 and is the reason no ncRNA rate is presented as a property of
the corpus rather than of the tools that built it.
