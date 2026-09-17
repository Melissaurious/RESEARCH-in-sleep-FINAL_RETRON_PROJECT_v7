# CURRENT PROJECT STATE

**Read this first.** It is the single place that says where the project is. Updated
2026-09-17, at the close of `g5`.

Every number below was read from a landed artifact, not from memory. The artifact is named
beside it so you can re-check it in one command.

---

## 1 · Where we are

| stage | state |
|---|---|
| Stage 1 — database characterization | **CLOSED**. `results/dbchar_g1…g7b`. |
| Stage 2 — RT0–RT7 definition / mapper | **validation CLOSED at Endpoint A**; production frozen; catalogue applied. |
| `g1` history and definition | landed |
| `g2` reference reconstruction | landed |
| `g3` prior-method replication | landed |
| `g4a` mapper development + validation | landed |
| confirmatory transfer (UG25) | **CLOSED — transfer SUPPORTED** |
| **`g4b` production freeze** | **COMPLETE** |
| **`g5a` eligibility census** | **COMPLETE** |
| **`g5` catalogue application** | **COMPLETE** |
| `g6` family architecture | **AUTHORISED, NOT STARTED** |
| `g7` structural + published comparators | **NOT STARTED** |

Do not start `g6` without reading `results/rt07_g5_catalogue_application/docs/G6_READINESS.md`.

## 2 · The frozen instrument

| | |
|---|---|
| **mapper version** | **`rtmap-1.0.0/53a1e738a19b3896`** |
| instrument sha256 | `53a1e738a19b38967563b4f4d733047b26123f754a7d592fd0186e7bd9c331f5` |
| mapper code sha256 | `69575dc7ac74f6094bda3c35df100d0f8f5a0e4c25142ac61c5d1026f10fceef` |
| bundle | `results/rt07_g4b_production_mapper/` |
| bundle root | `0b025cbab192f64d05ef0a9aff47859b998fe3158dc0199cd47cbbd040620d3f` |
| profile | `results/rt07_g4a_repaired/work/GII.deriv.hmm`, LENG 471, sha256 `292495a4…` |
| convention | `hhmake -M 50` |
| schema | `rtmap-schema-1.0` |

Frozen parameters: `PP_HI` 0.75 · `PP_LO` 0.50 · `S_MIN` 10 · `K_MIN` 30 · `T1` 0.32 ·
`D_MAX` 0.48 · `D_RANDOM` 0.067 · `CAT_STATE` 262 · 150 anchors.

**`CAT_STATE` 262 is NOT one of the 150 anchors.** Anchor callability and catalytic placement
are separate measurements over separate denominators and are never pooled.

Verify in one command:

```bash
python3 -c "import sys; sys.path.insert(0,'results/rt07_g4b_production_mapper/code'); \
from rtmap import version as V; print(V.mapper_version(V.check_instrument()))"
```

## 3 · The numbers that matter

Source: `results/rt07_g5a_eligibility_census/tables/g5a_census_summary.tsv` and
`results/rt07_g5_catalogue_application/tables/g5_qc_headline.tsv`.

| quantity | value |
|---|---|
| Stage-1 exact RT catalogue | **501,561** |
| ineligible (censused, retained) | **132,180** — 108,439 `< 250 aa`, 23,741 non-standard residue |
| **`G5_ELIGIBLE_N` — the g5/g6 denominator** | **369,381** (0.7365) |
| processed | 369,381 · 0 tool failures · 0 invalid inputs |
| **INSPECTABLE** (frozen verdict `MAPPED`) | **354,102** (0.9586 of eligible) |
| abstained | 15,279 — frozen abstention, **not** failure, **not** absence |
| state rows | 55,407,150 = 369,381 × 150 |
| `CAT_STATE` 262 MAPPED | 356,229 (0.9644 of eligible) |
| `CATALYTIC_CONFIRMED` | 343,880 — **0.9653 of CAT-MAPPED**, its own denominator |

**501,561 is not the denominator.** Use 369,381. The eligibility rule removed 26.35 % of the
catalogue before the mapper ran, and it removed it *unevenly* — see §5.

## 4 · What is and is not established

Established, and the only thing established:

> Under `hhmake -M 50`, the frozen alignment-path mapper met all seven predeclared conditions
> in a single confirmatory UG25 run. It maps conserved HMM states to actual residues in
> individual RT proteins and transferred to one fresh UG25 lineage under the registered
> independence rule.

**Not** established, and not claimable from any g5 output: universal RT architecture;
residue-level accuracy against external truth; transfer beyond UG25; specificity against
unrelated natural proteins; robustness under `-M a2m`; equivalence under `-M 60`; universal
RT0–RT7 architecture.

## 5 · Constraints a downstream analysis must respect

1. **The frame is GII-centred.** Median MAPPED fraction runs 0.94 (GII) → 0.49 (Retron), the
   same gradient seen on construction data. It is a property of the instrument and a confound
   for **every** between-family architecture comparison.
2. **Eligibility is not uniform.** `mixed_or_codon_evidence` 11.3 % eligible, `MULTI` 37.2 %,
   `all_partial` 57.4 %, against 73.6 % catalogue-wide. Report both filters — eligibility and
   inspectability — with each stratum's own denominator.
3. **`DELETED_STATE` ≠ absent region.** It is a statement about the alignment path.
4. **`NO_SUPPORTED_MAPPING` ≠ biological absence.** Abstention is not failure.
5. **MyRT / PADLOC / DefenseFinder are strata, never truth.** No accuracy, sensitivity,
   specificity, precision, recall, F1 or ROC against a tool label, ever. Allowed: *"among
   sequences labelled F, state S was MAPPED in X % of inspectable sequences."*
6. **`MULTI` is its own population** and is never folded into a single family.
7. **Historical RT0–RT7 remains `UNRESOLVED`** in all eight rows. Production emits `state_id`.
   The bridge that could resolve it is registered for `g7`.
8. **Scope is `-M 50` only.**

## 6 · Canonical datasets

Small, tracked, in this repository: every `results/*/tables/` summary, the frozen control
tables, manifests and roots.

Large, **local only, never pushed**: `data/derived/` (2.2 GB) including the g5 dataset.
Full registry with sizes, row counts and sha256: **`docs/DATASET_REGISTRY.md`**.

## 7 · Repository facts that are easy to get wrong

* **`general/` is a git submodule.** Clone with `--recurse-submodules` or the governance
  layer is empty.
* **There is a second worktree**, `dbchar-workbench`, which is **local only and not pushed**.
  See `docs/EXTERNAL_WORKTREES.md`.
* `ARIS_OUTPUT/` (23 GB) and `data/` (2.2 GB) are gitignored scratch and data.
* `ARIS_OUTPUT/rt07_g5/` holds 12 GB of per-shard g5 output. **Do not delete yet** — see
  `docs/DATASET_REGISTRY.md` §"g5 shard scratch".

## 8 · If you are a fresh session, read in this order

1. this file
2. `docs/PROJECT_ANALYSIS_PRINCIPLES.md` — 40 methodological principles from Stage 2
3. `docs/PROJECT_MAP.md` — what lives where
4. `idea-stage/docs/research_contract.md` — the single claim authority
5. `launchers/LAUNCHER_02_rt0_rt7_definition.md` — the active track
6. `results/rt07_g5_catalogue_application/docs/G6_READINESS.md` — what g6 may ask
7. `docs/decisions/` — settled decisions, newest last
