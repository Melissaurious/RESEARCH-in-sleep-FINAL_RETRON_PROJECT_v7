# BLOCKED

Open questions, timestamped: what is needed, why, the options, the
recommended default (WA-S.1).

## 2026-09-15 · `bundle_valid.sh` aborts on unset `ROOT` (LOW-STAKES, default taken)

- **Needed:** `general/checks/bundle_valid.sh results/<gate>` to run to completion.
- **Why blocked:** line 173 reads `$ROOT` under `set -u` before any assignment, so the check exits
  with `ROOT: unbound variable` and validates nothing past BS-3.
- **Options:** (a) export `ROOT=<project root>` when invoking; (b) patch `general/` (not permitted —
  the layer is amended only by the operator); (c) skip validation (unacceptable).
- **Default taken:** (a). `dbchar_g1_corpus_identity` validated with `ROOT=$(pwd)`: OK BS-1..BS-10.
  Fix proposed in `retros/2026-09-15_dbchar_g1_corpus_identity.md`.
- **RESOLVED 2026-09-15:** upstream fix `cff9831` adopted by moving the `general/` pin
  (`docs/decisions/2026-09-15_general_pin_cff9831.md`). `bundle_valid.sh` now passes on
  `results/dbchar_g1_corpus_identity/` with no `ROOT=` workaround.
