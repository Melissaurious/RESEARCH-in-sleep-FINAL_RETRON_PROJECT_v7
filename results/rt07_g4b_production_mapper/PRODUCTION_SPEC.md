# rt07 g4b — the frozen RT state→residue mapper as a production instrument

Gate: `rt07_g4b_production_mapper` · Date: 2026-09-17 · Track `rt07` · Stage 2, post-closure.

**g4b is packaging and operationalisation only.** Stage-2 validation closed at Endpoint A
(`docs/decisions/2026-09-17_stage2_ug25_confirmatory_closed.md`). Nothing in this bundle
re-validates the mapper, adds a family, adds a threshold, adds a control or widens a claim.

---

## 1 · The production instrument

| | |
|---|---|
| package version | `rtmap-1.0.0` |
| **compact mapper version** | **`rtmap-1.0.0/53a1e738a19b3896`** |
| instrument sha256 | `53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5` |
| mapper code | `code/rtmap/mapper.py`, sha256 `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` |
| profile HMM | `results/rt07_g4a_repaired/work/GII.deriv.hmm`, sha256 `292495a4…`, LENG 471 |
| match-state convention | `hhmake -M 50` |
| frozen conserved states | 150 anchors, `control/FROZEN_ANCHORS.tsv`, sha256 `c48315ae…` |
| output schema | `rtmap-schema-1.0` |
| HMMER | 3.4 (Aug 2023); `hmmalign` `532f1ed4…`, `hmmsearch` `e73bad9d…` |
| Python | 3.12.12, `retron_tradicional` |

`code/rtmap/mapper.py` is a **byte-identical copy** of
`results/FINAL_PRE_UG25_VALIDATION_BUNDLE/code/mapper.py` — the file the UG25 confirmatory
gate imported. It is not re-implemented, not refactored and not wrapped. Everything else in
`code/rtmap/` is engineering that calls it.

### Frozen scientific parameters

Read at import from `control/SUPPORT_RULE_FROZEN.tsv` and `control/CATALYTIC_STATE_FROZEN.tsv`
(byte-identical copies of the validation bundle's tables), and cross-checked against the
values recorded in the closure decision. A mismatch in either place fails closed.

| parameter | value |
|---|---|
| `PP_HI` | 0.75 |
| `PP_LO` | 0.50 |
| `S_MIN` | 10 |
| `K_MIN` | 30 |
| `T1` | 0.32 |
| `D_MAX` | 0.48 |
| `D_RANDOM` | 0.067 |
| `CAT_STATE` | 262 |
| `N_ANCHORS` | 150 |

Also frozen and unchanged: the alignment-path state→residue correspondence (no endpoint
interpolation), the four-way ambiguity logic, the reason-coded abstention logic, the
catalytic rule (`[YF].DD` at `CAT_STATE`, motif concordance only), and the interpretation of
the registered MONO / DI / REV controls.

`CAT_STATE` 262 is **not** one of the 150 anchors. Anchor callability and catalytic
placement are separate measurements over separate denominators and are never pooled — the
schema keeps them in separate column blocks and the freeze tests assert it.

### The identifier

`rtmap-1.0.0/<16 hex>` is a hash over: schema version, match-state definition, mapper
sha256, profile sha256 and LENG, anchor-set sha256, the eight calibrated parameters,
`CAT_STATE`, the dyad pattern, the two HMMER binaries, **the instrument tree digest over
every file in `code/` and `control/`**, **the eligibility rule** and **the domain-scoring
protocol**. Changing any of them changes the identifier — including a change to the
production wrapper itself (repair R1, §3b).

`tables/` is deliberately outside the tree digest, so landing an output does not change the
instrument. Input sequences, timestamps, host, shard and the bundle's own manifest root are
**not** in the hash either: they are per-run provenance in the shard sidecar. The bundle
root additionally cannot be an input without circularity, since the manifest hashes the code
that computes it — the runner verifies it against the external pinned root and records it in
provenance instead.

---

## 2 · Supported scope — used as written, not widened

> Under `hhmake -M 50`, the frozen alignment-path mapper met all seven predeclared
> conditions in a single confirmatory UG25 run. It maps conserved HMM states to actual
> residues in individual RT proteins and transferred to one fresh UG25 lineage under the
> registered independence rule.

Retained UG25 evidence: median MAPPED callability **51.3 %** (n=19 component) and **59.3 %**
(n=5 component); `CAT_STATE` 262 MAPPED in **27/28**, with **26/27** MAPPED calls beginning
`[YF].DD`; MONO / DI / REV maxima **10 / 13 / 17** MAPPED anchors against **54** for the
weakest real sequence — complete separation under the frozen criterion.

**Not claimed, and not claimable from any g5 output:** universal RT architecture;
residue-level accuracy against external truth; transfer beyond UG25; specificity against
unrelated natural proteins; robustness under `-M a2m`; equivalence under `-M 60`; universal
RT0–RT7 architecture.

### Match-state sensitivity — preserved as a limitation

`-M 50` and `-M 60` support the compact correspondence frame. Under HHmake's documented
default `-M a2m`, DGRs and AbiA retain **zero** `ALL_PARTNERS` positions while GII retains
115, and the family-symmetric universal shared-core claim was **withdrawn** on that basis.
The production instrument is defined under `-M 50` and every product names the convention.
**This question is not reopened in g4b**, and `-M 60` / `-M a2m` variants are not built.

The frame is **GII-centred**. Even on construction data the median MAPPED fraction ran GII
0.950, CRISPR 0.913, DGRs 0.800, UG3 0.550, AbiA 0.493, Retrons 0.473. A low mapped
fraction in g5 is expected for families distant from GII and is **not** evidence that the
protein is not an RT.

---

## 3 · Two packaging repairs, and the proof they changed no science

Both were found by running the packaging at 560 sequences rather than 19. Both concern
`hmmsearch`, whose E-values scale with the size of the database it is handed and whose
default reporting threshold is an E-value.

**P1 — the reported domain E-value moved with shard size.** Measured on 560 construction
sequences: `AFZ52119.1_GII` reported `2.1e-130` at a 100-sequence batch cap and `1.2e-129`
at a cap large enough to hold all 560. (Both runs used the same 560 records; the caps were
100 and 1000, so the *effective* databases were 100 and 560. The independent reviewer
reproduced the same ratio and correctly noted that "batch size 1000" describes the
configured cap, not a 1000-sequence database.) The bitscore, 428.1, was identical.

**P2 — whether a marginal domain was reported at all moved with shard size.** Measured:
`YP_217686.1_Retrons` was reported with bitscore −0.6 at an effective database of 100
(E = 2.2) and was absent at 560. For that sequence the verdict does not move, because
`classify_sequence` treats "no domain reported" and "bitscore < `S_MIN`" identically.

**How far this generalises — corrected.** An earlier draft of this document claimed a
sequence at or just above `S_MIN` = 10 could disappear at planned Stage-1 shard sizes.
**That was an overclaim and is withdrawn.** The independent reviewer measured the closest
case in the whole construction population, `CBK99617.1_Retrons` at bitscore 10.3:
E = 0.0062 at a 560-record database and E = 0.015 at 1341 — roughly three orders of
magnitude below the E ≤ 10 reporting cutoff. At the shard sizes g5 plans, a qualifying
sequence does **not** vanish.

**Why the repair is kept anyway.** Not on the strength of that hypothetical, but on two
grounds that hold as measured:

* a value a production record carries — the E-value — must not be a function of which other
  sequences happened to share a shard. P1 is a real, reproduced determinism defect in the
  output, independent of any verdict;
* P2 shows the *reporting* boundary genuinely moves with database size. That it currently
  moves only among sequences far below `S_MIN` is a fact about this profile and this
  population, not a property the packaging enforces. Pinning the database size at 1 makes
  shard-independence structural rather than fortunate, for 11 ms per sequence.

**Repair:** production scores domains **one sequence at a time**, so the database size is
always 1 and both the bitscore and the E-value are properties of the sequence alone.

It is more inclusive **for reported domains** — no sequence can lose a reported domain
because of its neighbours. It is *not* more inclusive in terms of positive mapper verdicts;
an earlier "strictly more inclusive" without that qualifier was imprecise, and the reviewer
was right to flag it.

**No frozen code, threshold or rule changed.** `domain_scores` is the frozen function,
called with a one-sequence FASTA. Bit scores are database-size independent.

Measured over the **complete 219-sequence construction population**, batched (the frozen
pipeline's own geometry, one call per family of 40) against per-sequence
(`tables/g4b_domain_scoring_repair_evidence.tsv`):

| | |
|---|---|
| sequences with a reported domain, batched / per-sequence | 219 / 219 |
| reported only per-sequence | **0** |
| reported only batched (i.e. lost by the repair) | **0** |
| bitscore differences | **0** |
| **qualifying-domain verdict flips** | **0** |

So the repair changes nothing on the population the instrument was calibrated on — which
smoke check S1 also confirms sequence by sequence — and it is not *less* inclusive on that
population either.

**Limit, stated rather than glossed:** this evidence covers the construction population.
UG25 is not re-scored here — it was consumed as the terminal confirmatory family, and
re-running it to re-check a packaging repair is the holdout reuse the closure decision
forbids. The independent reviewer, working read-only, did check UG25 as part of the review
and reported 0 bitscore differences and 0 verdict differences on all 28 records, at
original, 588- and 1341-record database sizes.

Cost of the repair, measured in one harness by `scripts/measure_throughput.py`: ~11.4 ms per
sequence for per-sequence domain search against ~1.4 ms per sequence for batched alignment,
inside a ~13 ms end-to-end cost. Wall-clock figures vary a few per cent between runs on this
shared host — `docs/G5_EXECUTION_PLAN.md` §5 records the observed spread rather than a single
number. It is not the binding cost of g5.

Alignment stays batched. `hmmalign` scores each sequence against the profile independently,
and this is asserted empirically, not assumed: `states.tsv` is byte-identical at batch size
1, 100, 500 and 1000. The independent reviewer additionally confirmed an identical
state/insertion digest across those batch sizes **and under reversed input composition**, on
all 560 records.

---

## 3b · Five repairs required by the independent packaging review

The independent packaging review (`review-stage/DESIGN_REVIEW_REQUEST_g4b_packaging.md`,
Codex `gpt-5.6-sol`, xhigh, read-only) returned `PASS_WITH_REQUIRED_REPAIRS`, 6/10, **g5 may
not begin**, with five REQUIRED findings. All five were packaging defects, all five are
repaired, and `scripts/check_repairs.py` reproduces the reviewer's own demonstration of each
and asserts it no longer holds.

| # | the defect, as demonstrated by the reviewer | repair |
|---|---|---|
| **R1** | the instrument digest bound neither `run_mapper.py`, nor the bundle, nor the eligibility rule, nor the domain-scoring protocol — so a wrapper that silently reverted to batched `hmmsearch` would keep the identifier `rtmap-1.0.0/46aa95cb0e197b40` | the digest now includes `instrument_tree_sha256` (every file in `code/` and `control/`), `eligibility_rule` and `domain_scoring_protocol`. `tables/` is excluded, so landing an output does not change the instrument. `--pinned-root` verifies the whole bundle against an external root before any record is emitted, and provenance records the root and its status |
| **R2** | with one identifier carrying two *different* sequences, which one survived depended on input order; and `rt_hash` sharding sent the two to different shards, where both passed the shard-local check | an identifier carrying different sequences is now a `DUPLICATE_SEQUENCE_ID_CONFLICT` and **every** occurrence is rejected — order-independent by construction. A repeat with an identical sequence is kept once and logged. `--reject-ids` carries the **global** census set, which g5 computes over the whole catalogue, and g5 now shards by `sequence_id` so collisions are co-located |
| **R3** | when the mapper failed, only the representative identifier got a `TOOL_FAILURE` row; an alias sharing the sequence got no row at all | every alias sharing the hash gets its own `TOOL_FAILURE` row, and the shard now **fails closed** unless every valid input identifier appears exactly once across `sequences.tsv` and the `TOOL_FAILURE` rows of `failures.tsv` |
| **R4** | an empty `probe.DONE` caused the shard to be skipped with no outputs at all | the sidecar now carries the input sha256, the instrument digest and the hash of every output. A shard is skipped only if all of them verify; a tampered output, a changed input or a changed instrument forces a redo |
| **R5** | `AMBIGUOUS_MAPPING` used an invented comparison, `n_ambiguous + n_unsupported > n_mapped`, which is not a frozen rule and could fire with zero `AMBIGUOUS` calls | removed. The inspectability status is now a **relabelling** of the frozen `(verdict, reason)` pair plus the frozen `T1` — a bijection onto the frozen reason codes, with no predicate of its own. The claim "no rule or criterion is introduced" is now true rather than aspirational |

Because R1 changed the instrument components, the compact identifier changed — by design,
and it is the whole point of the repair. **No scientific parameter, rule or call changed**:
smoke checks S1 and S2 still reproduce the landed frozen values and the frozen mapper's
per-state calls exactly.

Overclaims the reviewer identified in the g4b documentation, all corrected in place: the
`S_MIN` shard-size hazard (§3, withdrawn as not demonstrated), "strictly more inclusive"
(§3, qualified to reported domains), "batch size 1000" (§3, corrected to a configured cap),
"provably used the same instrument" (repaired by R1), "deterministic, order-independent"
(repaired by R2), "valid DONE" (repaired by R4), "no rule or criterion introduced" (repaired
by R5), and the timing decomposition, which is now produced in one harness by
`scripts/measure_throughput.py` so components and total are commensurable.

## 4 · Documentary errata from the UG25 post-run review

Recorded non-rewritingly. `UG25_RESULT.md` inside the frozen confirmatory bundle is **not**
edited. These corrections do not require a rerun and do not reinterpret the result.

| # | superseded statement | correction |
|---|---|---|
| U1 | "roughly **half** the frozen anchors are `DELETED_STATE` in UG25" | **FALSE.** `DELETED_STATE` is **1128/4200 = 26.9 %**. Non-`MAPPED` of any kind is 42.9 %; `MAPPED` is 57.1 % of all anchor calls. The intended point — that callability is far from complete — stands; the number quoted did not support it. |
| U2 | the C7 gate "restates no threshold of its own" | **FALSE.** `ug25_gate.py` restates five constants (`LINK_IDENTITY` 0.30, `LINK_COVERAGE` 0.50, `MIN_COMPONENT` 5, `REPLICATES` 3, `AGREEMENT_MIN` 0.80). **Each matches the frozen predeclaration exactly**, so this is inaccurate provenance wording, not tuning. The eight calibrated parameters *are* read from the frozen tables. |
| U3 | the predeclared post-run root verification ran as specified | **PARTIALLY.** `run_ug25_once.sh` verifies the root **pre-run only**. The post-run verification was executed as a separate manual command and is reported in the closure decision, but the runner does not implement it, so §13 of the predeclaration was not satisfied verbatim. |

Carried with them, as wording corrections: `FRESH_LINEAGE` is an operational classification
under the registered link rule and must **not** be read as "no evolutionary relationship"
(all 28 UG25 sequences have short high-identity local hits, median identity 0.588 at median
min-coverage 0.021); REV replication is **not** independent (28 unique reversals repeated
three times — "84 independent REV controls" would be inflation, and max-based C6 is
unaffected); the UG25 run tested **`-M 50` only**; and "confirmed" for catalytic placement
means motif concordance at a state, **not** independent residue truth.

---

## 5 · What this bundle contains

```
PRODUCTION_SPEC.md              this file — the frozen instrument
docs/OUTPUT_SCHEMA.md           rtmap-schema-1.0, call states, failure states
docs/CROSSWALK_RT0_RT7.md       historical labels, kept separate and UNRESOLVED
docs/STAGE1_METADATA_ROLE.md    MyRT / PADLOC / DefenseFinder are strata, not truth
docs/G5_EXECUTION_PLAN.md       catalogue application — planned, NOT executed here
docs/G6_ANALYSIS_PLAN.md        downstream architecture analysis targets
docs/G7_STRUCTURE_PLAN.md       structures, reserved as an orthogonal layer
code/rtmap/mapper.py            THE FROZEN MAPPER, byte-identical
code/rtmap/params.py            frozen parameters, read from control/, double-guarded
code/rtmap/version.py           instrument check + compact identifier
code/rtmap/schema.py            rtmap-schema-1.0
code/rtmap/crosswalk.py         historical crosswalk accessor
code/rtmap/run_mapper.py        the production runner
control/                        frozen parameter tables, anchors, crosswalk table
scripts/test_production_freeze.py  freeze tests (11 groups)
scripts/run_smoke.sh            the production smoke test (7 checks)
scripts/check_repairs.py        the 5 review repairs (R1-R5), each a reproduced defect
scripts/measure_throughput.py   reproducible timing, writes the throughput table
code/freeze.py                  bundle manifest and external-pinned-root verification
tables/                         landed smoke outputs + measured throughput
verify.sh                       reruns the smoke test and the freeze tests
```

## 6 · Running it

```bash
export PYTHONDONTWRITEBYTECODE=1
PY=/home/borg/miniconda3/envs/retron_tradicional/bin/python3

$PY -B code/rtmap/run_mapper.py \
    --in  shard_0001.faa \
    --out /path/to/output \
    --shard shard_0001 \
    [--metadata strata.tsv] [--reject-ids conflicts.txt] \
    [--pinned-root @../../review-stage/roots/RT07_G4B.root] \
    [--batch-size 500] [--force]
```

`--pinned-root` and `--reject-ids` are optional here and **required in g5**
(`docs/G5_EXECUTION_PLAN.md` §1, §4).

Per shard it writes `<shard>.states.tsv`, `<shard>.sequences.tsv`, `<shard>.failures.tsv`,
`<shard>.provenance.tsv` and a `<shard>.DONE` sidecar carrying the input sha256, the
instrument digest and the hash of every output. A shard is skipped on restart only if all of
those **verify** — presence alone is not completion (repair R4). Every write is atomic
(`.part` → `rename`), so an interrupted run leaves no half-written shard.

## 7 · Verification

```bash
bash verify.sh
```

Runs the ten freeze tests, the seven smoke checks and the five repair checks, and diffs the
regenerated smoke products against the landed ones.
