# DECISION — MCC-v3 adopted as the primary historical-core extractor; M2a–c active

Date: 2026-09-19 · Track `m2` · Decided by: operator (Melissa Rios). Supersedes the pause in
`2026-09-19_m2ac_approved_paused_on_toro_audit.md`.

Supersede by a new record, never by rewriting.

## 1 · Decision

**MCC-v3 replaces MCC-v2 as the primary extractor, before any M2 execution.** The reason is
that newly audited historical source material — the Toro 2014 RT0–RT7 extracts, with
source-stated boundaries on 76 clean Mestre proteins — provides a stronger, provenance-backed
interval definition.

**What MCC-v3 is:**
- The primary historical interval is projected from the closest eligible Toro 2014 retron
  RT0–RT7 template.
- The Toro 2014 alignment is historical source material, **not a Mestre MSA**.
- No Mestre clade label is used in template choice, extraction, alignment or placement.
- The MCC-v2 required core stays as a prespecified sensitivity / core-consistency analysis.
- The ≥ 70 % MCC-v2-core-inside-interval check stays as an orthogonal quality criterion.
- Extraction is never forced. The failure status is
  `UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY`.
- The 76 source-stated proteins validate the instrument (leave-near-identical-template-out).
  They are **never used to tune thresholds**.

## 2 · Frozen rules (the operator asked for these explicitly)

All six are in launcher rev-4 §4a. The frozen artefacts are
`analysis/mestre_audit/scripts/m10_mcc_v3_freeze.py` and `m2_design/mcc_v3/MCC_V3_PARAMS.json`.
The thresholds come from the Toro reference distribution alone:
- `MIN_IDENT` 0.3503 is the 5th percentile of nearest-neighbour identity within the Toro
  retron set;
- `MAX_BOUNDARY_UNC` 16 aa is the 95th percentile of the concordant-template spread within
  the Toro retron set.

**One specification correction (v3.0 → v3.1), found after the first application and recorded
openly.** v3.0 calibrated R5 on a different quantity from the one R5 applies. v3.1 calibrates
the applied quantity from Toro data only. v3.0 outputs are preserved. No further change.

## 3 · What the frozen instrument measured (before any M2a tree or placement)

| | MCC-v3.1 | MCC-v2 (sensitivity) |
|---|---|---|
| clean historical proteins extracted | 1,490 / 1,814 | 1,729 / 1,814 |
| RNA-polymerase substitutes extracted (negative control) | 0 / 15 | 0 / 15 |
| source-stated validation (76), extracted | 62 / 76 | 71 / 76 |
| source-stated validation (76), start / end within 5 aa | 0.710 / 0.855 | 0.225 / 0.718 (window) |
| clade 10 extracted (evaluation-only denominator) | 72 / 164 | 164 / 164 |

The launcher's K1 extractability bullet was written for MCC-v2 (≥ 90 %; 95.3 %). It is kept as
written; no new threshold was set after seeing 82.1 %. Every M2a result is reported under
both extractors. Where historical clade recovery differs materially between them, that
disagreement is a result and is not harmonised away.

## 4 · Scope

M2a–c are active within ≤ 60 CPU-h, with the stop conditions of launcher rev-4. They end in
the Codex review and an operator stop. **M2d is not approved.** Modern sequences too remote
from the Toro reference may remain unextractable or unplaceable. That is never read, by
itself, as evidence of a new clade.
