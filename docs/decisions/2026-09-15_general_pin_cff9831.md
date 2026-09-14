# DECISION 2026-09-15 — move the `general/` governance pin a0f4ded → cff9831

**Decided by:** operator (Melissa Rios), 2026-09-15 — explicit instruction to adopt the pushed
upstream `bundle_valid.sh` `$ROOT` fix rather than modify governance locally.

- **From:** `a0f4dedfd144151feb7cf32b7ecd5be705c6526d`
- **To:** `cff983144e2ad6fc01f648982fb61810dd77ddbe` (upstream branch
  `claude/intelligent-shannon-i1vov1`, a fast-forward)
- **Why:** at `a0f4ded`, `checks/bundle_valid.sh` read `$ROOT` under `set -u` before assigning
  it and aborted before validating anything past BS-3 (`docs/BLOCKED.md`, 2026-09-15).
  `cff9831` resolves `ROOT` first.
- **What else the fast-forward brings:** 33 prose files under `RETRON_STAGES/` and `_DRAFTS/`
  (programme archive and project drafts) and one contract path fix. No other check, tool,
  agreement or rule changed (`git diff --stat a0f4ded cff9831`).
- **Effect on landed bundles:** none. `results/dbchar_g1_corpus_identity/PROVENANCE.md` records
  `agreements: a0f4ded`, the revision it was produced under; bundles are write-once (BS-6) and
  the fix changes only the validator. Re-validated at `cff9831` without the `ROOT=` workaround:
  BS-1..BS-17 OK, clone-safe OK, `run.sh` reproduced byte for byte.
- **Next gate** (`dbchar_g2`) starts at `cff9831` and seals that revision.
