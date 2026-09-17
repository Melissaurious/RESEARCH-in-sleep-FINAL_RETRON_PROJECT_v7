# g4b PACKAGING REVIEW — ROUND 2. Do the five required repairs hold?

Round 1 (thread `01a0afd9`) returned **`PASS_WITH_REQUIRED_REPAIRS`, 6/10, g5 may NOT begin**,
with five REQUIRED findings. All five were packaging defects. All five are repaired.

**Scope is narrower than round 1.** Please assess ONLY:

1. whether each of R1–R5 is genuinely fixed, by the demonstration you yourself used;
2. whether the repairs changed any science;
3. whether the round-1 overclaims are now corrected honestly;
4. whether g5 may begin.

Mapper validation remains CLOSED. Do not propose new validation families, holdouts,
thresholds or controls. Do not re-review universality, generalisation or transfer.

```
G4B BUNDLE  : results/rt07_g4b_production_mapper/
              root d63010801f556d7cc212971d3c38d358a381416485b0d3d17432da67448036a0  (38 files)
manifest    : review-stage/manifests/RT07_G4B.MANIFEST
pinned root : review-stage/roots/RT07_G4B.root

verify freeze : python3 results/rt07_g4b_production_mapper/code/freeze.py verify \
                  results/rt07_g4b_production_mapper \
                  review-stage/manifests/RT07_G4B.MANIFEST "$(cat review-stage/roots/RT07_G4B.root)"
verify all    : bash results/rt07_g4b_production_mapper/verify.sh
               (freeze tests + 7 smoke checks + 5 repair checks + landed-product diff)
```

Round 1's request, for context: `review-stage/DESIGN_REVIEW_REQUEST_g4b_packaging.md`.

---

## The five repairs

**R1 — instrument provenance was incomplete.** You showed a wrapper that silently reverted to
batched `hmmsearch` would keep the identifier `rtmap-1.0.0/46aa95cb0e197b40`.

Repaired: the digest now includes `instrument_tree_sha256` (every file in `code/` and
`control/`), `eligibility_rule` and `domain_scoring_protocol`. `tables/` is excluded so
landing an output does not change the instrument. `--pinned-root` verifies the whole bundle
against the external root before any record is emitted; provenance records the root and its
status. The identifier is now **`rtmap-1.0.0/e9c3ac1119669c86`**.

**R2 — duplicate identifiers were neither deterministic nor globally enforced.** You showed
`A then C` and `C then A` retained different sequences.

Repaired: an identifier carrying different sequences is `DUPLICATE_SEQUENCE_ID_CONFLICT` and
**every** occurrence is rejected. A repeat with an identical sequence is kept once and logged.
`--reject-ids` carries a global census set, and g5 now shards by `sequence_id`, not `rt_hash`,
so collisions are co-located.

**R3 — failure isolation silently omitted aliases.** You showed `input_valid=2`,
`sequences_emitted=0`, `failures_emitted=1`.

Repaired: every alias sharing the hash gets its own `TOOL_FAILURE` row, and the shard fails
closed unless every valid input identifier appears exactly once across `sequences.tsv` and the
`TOOL_FAILURE` rows of `failures.tsv`.

**R4 — resume trusted mere `DONE` existence.** You showed an empty `probe.DONE` caused a skip
with no outputs.

Repaired: the sidecar carries input sha256, instrument digest and every output hash. A shard
is skipped only if all verify; a tampered output, changed input or changed instrument forces a
redo.

**R5 — a new classification rule was introduced in packaging.** `n_ambiguous + n_unsupported >
n_mapped` was not a frozen rule and could fire with zero `AMBIGUOUS` calls.

Repaired: removed. The inspectability status is now a relabelling of the frozen
`(verdict, reason)` pair plus the frozen `T1` — a bijection onto the frozen reason codes, with
no predicate of its own. An unmapped pair fails closed.

`smoke/check_repairs.py` reproduces each of your demonstrations and asserts it no longer holds
(24 checks). `tests/test_production_freeze.py` gained T11 as the static counterpart.

## Evidence that no science changed

`tables/g4b_repair_no_science_change.tsv` — the smoke products landed BEFORE the repairs,
diffed column by column against the same products regenerated AFTER them on identical input:

| table | rows | columns identical | columns that ever differ |
|---|---|---|---|
| `smoke_states.tsv` | 2850 | YES | `mapper_version` only |
| `smoke_sequences.tsv` | 19 | YES | `mapper_version` only |
| `smoke_failures.tsv` | 4 | YES | `mapper_version`, `detail` (free text, reworded by R2) |

S1 still matches all 18 landed frozen construction results exactly; S2 still matches 2850
per-state calls to the frozen mapper imported from the validation bundle.

## Round-1 overclaims, corrected in place

* the `S_MIN` shard-size hazard — **withdrawn** as not demonstrated; your measurement
  (`CBK99617.1_Retrons`, bitscore 10.3, E = 0.0062 at 560 and 0.015 at 1341) is recorded, and
  the repair is now justified on P1 determinism grounds instead. `PRODUCTION_SPEC.md` §3.
* "strictly more inclusive" — qualified to **reported domains**, explicitly not verdicts.
* "batch size 1000" — corrected to a configured cap over 560 records.
* "provably used the same instrument", "deterministic, order-independent", "valid DONE",
  "no rule or criterion introduced" — each repaired rather than reworded.
* the timing decomposition — `smoke/measure_throughput.py` now produces every figure in one
  run on one substrate and writes the landed table. Components 1.4 + 11.0 = 12.4 ms now sit
  **below** the 12.9 ms end-to-end total, with the remainder attributed; the g5 estimate uses
  the total. The gzip ratio is measured in the same script. The 48-core figure is labelled as
  unmeasured arithmetic.

## What to return

1. VERDICT: PASS / PASS_WITH_REQUIRED_REPAIRS / FAIL_BLOCK
2. SCORE: n/10
3. MAY g5 BEGIN: YES / NO
4. Per repair R1–R5: FIXED / NOT FIXED / PARTIALLY FIXED, with what you ran
5. Did any science change?
6. Any remaining overclaim
7. Anything you could not verify
