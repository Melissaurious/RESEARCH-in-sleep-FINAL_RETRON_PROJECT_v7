# DECISION — v2 re-review: PASS_WITH_REQUIRED_REPAIRS (6/10), class B. UG25 stays SEALED.

Date: 2026-09-17 · Track: `rt07` · Status: **4 of 6 repairs NOT closed; 7 new repairs required**

Reviewer: independent Codex (`gpt-5.6-sol`, xhigh, read-only), thread `01a0ae95`, 1h 10m.
WA-A.5 compliant; not same-family; **not self-reviewed**.
Gate: `review_gate.py --round-backend codex --score 6 --verdict almost` → `{"decision": "stop"}`.

Supersede by a new record, never by rewriting.

---

## 1 · Six-repair status as judged by the reviewer

| # | repair | status |
|---|---|---|
| 1 | `MAPPED`-only catalytic aggregation | **CLOSED** |
| 2 | fail-closed verifier and manifest | **NOT CLOSED** — symlinks invisible; unpinned verification accepts a jointly rewritten bundle+manifest+sidecar |
| 3 | directory lock / bytecode / manifest protection | **NOT CLOSED** — manifest *directory* is writable, so 444 + sidecar can be atomically replaced |
| 4 | U10 exact reason codes | **CLOSED** |
| 5 | family-scoped loader | **NOT CLOSED** — the verification path itself materialises UG25 |
| 6 | C6 / empty-control / di-shuffle policy | **NOT CLOSED** — failed IDs not landed; NaN inputs pass |

Independently reproduced by the reviewer and confirmed sound: `CAT_STATE = 262`, MAPPED-only count
**207**, runner-up **5**, agreement **207/210 = 0.9857**, all **9** exclusions landed; construction
total **217/219** computed from both the family rows and 219 sequence rows; scoped-loader exact
equality (Retrons 95, GII 496, DGRs 488, CRISPR 129, UG3 86, AbiA 19); full `verify.sh` exit 0 with
**17/17** products byte-identical against the pinned root; all three U10 mutants failing.

---

## 2 · SELF-REPORTED FREEZE VIOLATION — the executor mutated the frozen v1 bundle

| field | content |
|---|---|
| **expected** | `results/rt07_mapper_validation_repair/` (v1), the artifact the previous reviewer examined, is byte-identical to its frozen state |
| **observed** | it is **not**. v1 contains **164** files against a **162**-file manifest. `scripts/__pycache__/calibrate_support.cpython-312.pyc` has mtime **2026-09-17 11:22:08**, while the v1 manifest is **01:19:44** — the file was created **~10 hours after v1 was frozen** |
| **cause** | **the executor.** While verifying the previous reviewer's per-class-p95 finding, the executor ran `import calibrate_support` with v1's `scripts/` on `sys.path`. Python wrote bytecode into the frozen bundle |
| **when_detected** | by the **reviewer**, during this review. The executor's own mid-review check saw `FREEZE BROKEN` from the v2 script and **misattributed it entirely to a tooling mismatch** (v2 no longer excludes `__pycache__`). The exclusion difference is real, but it was not the whole story — one `.pyc` genuinely post-dates the freeze |
| **scientific_effect** | **none on any measurement.** No `.py`, `.tsv` or `.md` changed; v1's 162 manifested files all still hash correctly. The damage is to the freeze guarantee: v1's manifest **could not see** these files, which is precisely defect E6 |
| **repair** | **none applied. Not authorised by this record.** v1 is the reviewed artifact and must not be quietly tidied. The violation is recorded here, externally |
| **results_before_repair_invalidated** | **NO** |

This is the **second** time the executor has mutated a bundle while it was under or after review.
The first was writing a file into the G2L bundle mid-review. This one was subtler — a side effect
of *reading* the bundle — which is exactly why bytecode suppression is a governance control and not
housekeeping.

---

## 3 · Other load-bearing findings, all verified by the executor

- **Symlinks are invisible to the manifest.** `walk()` has `if os.path.islink(p): continue`, so an
  added `scripts/injected.py` symlink verified `FREEZE INTACT`. A symlink can redirect an import.
- **Unpinned verification is defeatable.** `verify.sh` accepts an omitted expected-root argument; a
  changed bundle with rebuilt manifest **and** rebuilt sidecar passes unpinned, and fails only when
  the caller pins the root. The pinned root — supplied from outside — is the real trust anchor.
- **The manifest directory is writable (mode 775).** Mode 444 on the manifest and a co-located
  sidecar do not prevent atomic replacement of both. Co-located self-authentication is not
  authentication.
- **The UG25 seal is an accident guard, not authorisation.** `AUTHORISATION_TOKEN` is a public
  source constant, and `loader_equivalence.py` uses it on every routine run: **L4 materialises UG25
  and writes `n=28` into `tables/loader_scope_tests.tsv`**, and L1/L5 still call the all-family
  `eligible_by_family()`. So even the corrected wording *"UG25 was not used for … output
  generation"* is **false** — its count is in a landed output table. Verified directly.
- **`evaluate_c6` accepts non-finite and impossible inputs.** Verified: NaN controls → `PASS`; NaN
  real minimum → `PASS`; negative counts → `PASS`. All three must fail closed.
- **Di-shuffle failure IDs are not landed.** `C6_CONTROL_POLICY.md` §5 requires each failed
  sequence id to be listed; only the count is written. The three are
  `ADE85031.1_CRISPR`, `ESQ17084.1_CRISPR`, `WP_032822382.1_UG3`.
- **The v2 errata record cites a stale root**, `dd3b8eab…`, superseded by `512bb53b…` after the
  `lock()` fix. Confirmed: one occurrence.

---

## 4 · New repairs required before UG25 — NOT AUTHORISED, NOT STARTED

1. Reject or manifest **symlinks**; require a **pinned expected root** in every production
   verification path.
2. Move the manifest trust anchor to a non-writable location, or lock its parent namespace.
3. Remove **all** UG25 materialisation from pre-run tests and verification: do not call the
   all-family legacy loader; do not execute L4 before operator authorisation; take the
   authorisation from outside the source tree, not a public constant.
4. Correct the UG25 access wording again — current verification **does** materialise UG25 and lands
   its count.
5. Make C6 reject non-finite, negative and non-integer counts, and inconsistent
   attempted/valid/failed accounting.
6. Land the three construction di-shuffle failure IDs; guarantee every failed UG25 replicate ID is
   listed.
7. Resolve and externally document the **v1 freeze violation**; supersede the stale `dd3b8eab…`
   statement without rewriting history.

Optional: a fourth U10 mutant (present-but-subthreshold domain, which currently slips through);
replicate-identity uniqueness so duplicates cannot pad a depleted class; narrow or remove the
remaining manifest exclusions.

---

## 5 · Supportable claim — unchanged, construction-only

> Under `-M 50`/`-M 60`, a compact GII-centred correspondence frame is recoverable across the six
> construction families. In those construction data, the alignment-path mapper produces
> posterior-stratified calls, real ambiguity, reason-coded abstention, and a stable operational
> catalytic coordinate at state 262. This does **not** establish robustness under `-M a2m`,
> independent residue-level accuracy, or confirmatory transfer to a held-out non-GII-like family.

It also does **not** support any claim that UG25 remained unread or unmaterialised.

## 6 · Gate state

**UG25 SEALED · g4b BLOCKED · g5 BLOCKED · g6 NOT STARTED.** v2 freeze intact at
`512bb53b…` at review start and end.
