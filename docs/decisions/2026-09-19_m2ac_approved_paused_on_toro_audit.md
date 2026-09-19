# DECISION — M2a–c approved; execution paused pending the extraction contract

Date: 2026-09-19 · Track proposed `m2` · Recorded by the executing session from the operator's
instructions of 2026-09-19.

Supersede by a new record, never by rewriting.

## 1 · What the operator approved

- **M2a–c approved** within the existing ≤ 60 CPU-h budget. **M2d is NOT approved.**
- The scientific objective is historical **reconstruction** (not exact reproduction),
  validated by relatedness-blocked leave-out, then a bounded modern smoke test.
- The recovered V4 products are reused as comparators only
  (`2026-09-19_m1_mestre_audit_and_k0_disposition.md`).
- Codex reviews independently at the M2c stop.

## 2 · Why nothing has executed

The operator required a Toro 2014 source audit **before** freezing MCC-v2, with the rule:
*"if this audit materially changes the historical-core definition, pause before M2 execution
and report the revised extraction contract."*

The audit (`analysis/mestre_audit/REPORT.md` §14–17) found source-stated Toro RT0–RT7
boundaries on 76 clean Mestre proteins.

- Against them, **Toro-template extraction** (label-independent) reproduces the boundaries
  with median error 0 aa and extracts 1,814 / 1,814 clean proteins.
- MCC-v2 extracts 1,729 / 1,814. Its required core, the approved primary, omits a median
  of about 36 source-stated residues per protein.

That is material, so execution is paused.

## 3 · Open for the operator

Choose the extraction contract in launcher rev-3 §4a:

- **MCC-v3** (recommended): TTE edges, the MCC-v2 profile route as core QC, the full TTE
  interval as primary, and MCC-v2 required-core as sensitivity;
- **or MCC-v2** required core, as approved, with TTE as sensitivity.

On that choice, the launcher is copied to `launchers/` and M2a begins.
