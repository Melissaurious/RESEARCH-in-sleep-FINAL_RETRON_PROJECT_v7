# rt07_g4b_production_mapper

STATUS: VERIFIED — `verify.sh` was rerun from this assembled bundle and reproduced
`tables/smoke_states.tsv`, `tables/smoke_sequences.tsv`, `tables/smoke_failures.tsv` and
`tables/smoke_input.faa` **byte for byte**, together with every deterministic key of
`tables/smoke_provenance.tsv` (BS-3, WA-B.2). Log in `tables/smoke_run.log`.

**One landed product is deliberately NOT byte-reproducible and is declared here rather than
buried:** `tables/g4b_throughput_measurement.tsv` is a wall-clock measurement. Re-running
`scripts/measure_throughput.py` rewrites it with that run's timings; observed end-to-end cost
across runs on this host spans 12.9–14.1 ms per sequence. It is excluded from `verify.sh`'s
byte-diff for that reason, it is not part of the instrument identifier, and no scientific
result depends on it — it exists to make the g5 compute estimate a measurement instead of a
guess.

    bundle_status:     REPRODUCIBLE (deterministic products)
    human_input_audit: PENDING

    n_attempted:  23   input records in the smoke population
    n_succeeded:  19   records that reached the mapper and produced a full scientific row
    n_dropped:     4   records rejected as INPUT_INVALID, each with a reason code

Weight **ENGINEERING**. This gate produces **no scientific result and no claim-bearing
number**. It packages an already-validated instrument for use.

---

## 1 · What this bundle is

The frozen RT state→residue mapper, packaged as a production instrument for the Stage-1
catalogue application (g5).

| | |
|---|---|
| **mapper version** | **`rtmap-1.0.0/53a1e738a19b3896`** |
| mapper code | `code/rtmap/mapper.py`, sha256 `69575dc7…` — **byte-identical** to `FINAL_PRE_UG25_VALIDATION_BUNDLE/code/mapper.py` |
| profile | `GII.deriv.hmm`, LENG 471, `hhmake -M 50` |
| frozen conserved states | 150 anchors |
| schema | `rtmap-schema-1.0` |

`PRODUCTION_SPEC.md` is the entry point. Read it first.

## 2 · What was measured

**Nothing scientific.** Stage-2 validation closed at Endpoint A
(`docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md`) and is not reopened here.
g4b adds no family, no threshold, no control, no criterion and no claim. UG25 was neither
re-run nor re-scored by the executor.

What *was* established is engineering: that the packaged instrument reproduces the frozen
mapper exactly, deterministically, and independently of shard and batch geometry.

## 3 · Layout

```
PRODUCTION_SPEC.md   the frozen instrument — start here
README.md            this file
PROVENANCE.md        instrument identity, environment, governing decisions, review threads
MANIFEST.tsv         every landed artefact, the script that made it, its unit and denominator
INPUTS.tsv           every external input, hashed
OUTPUTS.tsv          every file in this bundle, hashed
run.sh               regenerate and RE-LAND the products
verify.sh            regenerate into a temp dir and CHECK against what is landed
env.lock             the environment, pinned by content

code/rtmap/          the instrument: mapper.py (frozen), params, version, schema,
                     crosswalk, run_mapper
code/freeze.py       bundle manifest + external-pinned-root verification
control/             frozen parameter tables, the 150 anchors, the RT0–RT7 crosswalk
docs/                output schema, crosswalk, Stage-1 metadata role, g5 / g6 / g7 plans
scripts/             smoke test, repair checks, freeze tests, throughput measurement
tables/              landed smoke products, throughput, repair evidence, pre-repair snapshot
```

## 4 · Checks that must pass before g5

```bash
bash verify.sh
```

* **11 freeze-test groups** — the mapper is byte-identical; every frozen parameter matches the
  closure decision; a retuned control table or an edited `mapper.py` is rejected at import;
  the schema keeps all four call states and both denominators; the crosswalk is `UNRESOLVED`;
  the instrument identifier moves when any component moves.
* **7 smoke checks** — 18 construction sequences reproduce the landed frozen results exactly;
  2850 per-state calls match the frozen mapper imported directly; byte-identical rerun; batch
  sizes 1 and 500 agree on every scientific column including domain scores; all four call
  states reachable; every `INPUT_INVALID` reason reachable; deduplication preserves per-row
  calls.
* **5 repair checks (R1–R5)** — each reproduces a defect the independent packaging review
  demonstrated, and asserts it no longer holds.

Freeze the bundle against its external pinned root with:

```bash
python3 code/freeze.py verify . ../../review-stage/manifests/RT07_G4B.MANIFEST \
        "$(cat ../../review-stage/roots/RT07_G4B.root)"
```

## 5 · Independent review

| round | verdict | score | g5 |
|---|---|---|---|
| 1 (`01a0afd9-39e8`) | `PASS_WITH_REQUIRED_REPAIRS` | 6/10 | **NO** — five REQUIRED packaging defects |
| 2 (`01a0aff7-9be3`) | `PASS_WITH_REQUIRED_REPAIRS` | 9/10 | **YES** — all five FIXED, no science changed |

Round 1 found five real packaging defects; all five were repaired, and round 2 re-ran the
reviewer's own demonstrations against the repaired code. Round 2's two residual findings were
documentary overstatements about the compute estimate, both corrected. Full account, including
every executor overclaim and its disposition:
`docs/decisions/2026-09-17_stage2_g4b_production_packaging.md`.

## 6 · What this bundle does not license

* No universal RT architecture claim, no residue-level accuracy against external truth, no
  transfer beyond UG25, no natural-protein specificity, no `-M a2m` or `-M 60` claim, no
  universal RT0–RT7 architecture.
* No renaming of production `state_id` to RT0–RT7. The crosswalk is separate and every row is
  `UNRESOLVED` until a g7 measurement resolves it.
* No accuracy statement against MyRT / PADLOC / DefenseFinder labels; those are strata.
* `NO_SUPPORTED_MAPPING` and `DELETED_STATE` are **not** biological absence.

## 7 · Verification log

`tables/smoke_run.log` is the captured output of the `verify.sh` run that this bundle's
landed products came from: freeze tests OK, smoke OK, repair checks OK, landed-product diff
clean, deterministic provenance keys matching, `g4b VERIFY OK`.
