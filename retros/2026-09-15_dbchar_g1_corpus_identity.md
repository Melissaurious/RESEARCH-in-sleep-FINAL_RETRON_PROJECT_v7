# Retro — dbchar_g1_corpus_identity (2026-09-15)

Bundle: `results/dbchar_g1_corpus_identity/` — REPRODUCIBLE, human_input_audit PENDING.

## What happened

- Reused prior `dbchar-g0-inventory` as design and as a reconciliation target, not as numbers.
  Audit found two blind spots in its parser (blank lines skipped silently; `errors="replace"`
  decoding) and one scope gap (the ncRNA-anchored master file was never opened). All three were
  closed here; the strict census still found 0 parse failures and agreed with every prior
  per-file hash and count.
- Measured before running: seeded size-stratified smoke 67.8 MB/worker-s → full pass 49.5 under
  contention (within 2×). Whole gate 2 min 50 s wall, 0.55 CPU-h.
- The record-level structure diverged from the schema in ways that matter for g2/g3 (inverted
  windows, RT records with no RT CDS, a two-way ncRNA sub-schema split in the ncRNA-anchored file,
  metadata ncRNA totals disagreeing with the array, multi-label records filed in family files).

## What went wrong

- My first path census reported container keys as "undocumented" because the schema lists only
  leaves. Caught on inspection before landing; fixed in `g1lib.documented_paths`.
- `general/checks/bundle_valid.sh` aborts with `ROOT: unbound variable` (line 173) unless `ROOT`
  is exported. Run with `ROOT=$(pwd)`; logged in `docs/BLOCKED.md`.

## Proposal (not an amendment — WA-S.2)

**Initialise `ROOT` in `bundle_valid.sh` before the BS-12 ledger lookup**
(`ROOT="${ROOT:-$(git -C "$B" rev-parse --show-toplevel 2>/dev/null)}"` near the top of `validate`).
- *Would have caught:* this gate's validation silently not running — the abort printed one line
  and, behind a pipe, exited 0.
- *Would wrongly reject:* nothing it accepts today; a bundle outside any git checkout still gets
  an empty ROOT and falls through to the existing "no ledger" branch.

**Outcome:** landed upstream as `cff9831` (same approach: `ROOT` resolved first, `${ROOT:-}`
guards). The project adopted it by moving the pin, not by a local edit
(`docs/decisions/2026-09-15_general_pin_cff9831.md`), and re-validated g1 without `ROOT=`.

## Operator decisions arising

Stage-1 population rules for ncRNA-anchor-only, MULTI and RT-CDS-less records:
`docs/decisions/2026-09-15_stage1_population_rules.md`.
