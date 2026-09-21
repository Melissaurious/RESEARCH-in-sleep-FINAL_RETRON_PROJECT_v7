# rt07_stage2_final_report — Stage-2 synthesis and thesis reporting package

STATUS: VERIFIED — `run.sh` was rerun from a cleared scratch directory and reproduced every landed artefact byte for byte; `verify.sh` passes.

n_attempted: 8      historical labels RT0-RT7 carried into the final table
n_succeeded: 8      labels given their reviewed final status, verified against the governing erratum
n_dropped:   0      nothing dropped; UNRESOLVED and PARTIAL labels are reported, not removed

**Start with `DELIVERABLES_INDEX.md`.**

## What this is

This is the final reporting package for Stage 2 (RT0–RT7 definition and the conserved-state
mapper). It is built from the frozen, independently reviewed record on `main` at
`94a1a78868d6039297c78b3fdcc047d633d6645e`. It **computes no science**:

- every number in the prose is looked up from a landed table (exactly one row per selector),
  from a declared count over landed rows, or from a literal checked against a reviewed record;
- the eight RT0–RT7 statuses are checked against the governing erratum table
  (`docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv`), and the build fails if any
  differs;
- wording withdrawn by the 2026-09-19 errata fails the build if it appears in any output;
- no frozen bundle, figure or table is modified. The thesis figures are re-drawn here from
  landed tables, because two frozen figures carry superseded wording.

## Final reviewed statuses

RT0 UNRESOLVED · RT1 UNRESOLVED · RT2 PARTIAL · RT3 ESTABLISHED (with qualification) · RT4
ESTABLISHED (with frame-instability qualification) · RT5 ESTABLISHED (joint RT5+RT6) · RT6
PARTIAL (jointly with RT5 only) · RT7 ESTABLISHED (narrowed wording). All are LtrA-local
interpretation-layer correspondences. g6 shows descriptive concordance across largely
MyRT-defined strata, not independent family discovery.

## Layout

| path | content |
|---|---|
| `OUTLINE.md` | outline, figure/table inventory and file paths, written before the build |
| `DELIVERABLES_INDEX.md` | index of every deliverable, canonical frozen asset and final commit |
| `report/` | technical report; thesis Methods, Results, Discussion |
| `tables/` | T1–T7, bundle index, and the plotted numbers for each figure |
| `figures/` | F1–F6 (png + svg) |
| `templates/` | the prose with `{{placeholders}}`; `report/` is rendered from here |
| `scripts/findings.py` | the value registry: every number's source |
| `scripts/ledger.py` | transcribed reviews, negative results, claims, figure plan |
| `scripts/build.py`, `figures.py`, `seal.py` | builder, figure script, sealer |
| `run.sh` / `verify.sh` | byte-identical rerun / independent checks |

## Limits of this package

- `human_input_audit: PENDING` on the landed Stage-2 bundles. Per governance, this audit must be
  done before any number here becomes a thesis claim.
- The review ledger covers reviews recorded in `docs/decisions/` and the g5 commit message. It
  is not asserted to be exhaustive for g1–g3.
- This package has had no independent review of its own. It adds no scientific claim; the
  claims it reports are the ones already reviewed.
