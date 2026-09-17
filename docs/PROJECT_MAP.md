# PROJECT MAP — what lives where

A guide to the repository for someone who has never seen it. Paths are relative to the
project root.

---

## 1 · Read-first documents

| path | what it is |
|---|---|
| `docs/CURRENT_PROJECT_STATE.md` | **start here** — stage, frozen instrument, headline numbers, constraints |
| `docs/PROJECT_ANALYSIS_PRINCIPLES.md` | 40 methodological principles distilled from Stage-2 development. Reusable, not task-specific |
| `docs/DATASET_REGISTRY.md` | every heavy local dataset: path, size, rows, sha256, purpose |
| `docs/EXTERNAL_WORKTREES.md` | the second worktree and the submodule |
| `docs/DBCHAR_WORKBENCH.md` | the Stage-1 thesis-writing workbench, which is local only |
| `CLAUDE.md` | operating context and project conventions |
| `idea-stage/docs/research_contract.md` | the single claim authority |
| `launchers/LAUNCHER_02_rt0_rt7_definition.md` | the active track: objective, gates, autonomy envelope |

## 2 · Governance

| path | what it is |
|---|---|
| `general/` | **git submodule** → `RESEARCH-in-sleep-GENERAL_v3`. Data-safety, evidence, provenance, reporting and bundle standards. Clone with `--recurse-submodules` |
| `general/checks/bundle_valid.sh` | the BS-1..BS-11 bundle standard every landed gate must pass |
| `docs/decisions/` | settled operator decisions, chronological. **Superseded by new records, never rewritten** |
| `docs/BLOCKED.md` | open questions with recommended defaults |
| `retros/` | one retro per gate |
| `review-stage/` | independent-review requests, plus the **manifests and external pinned roots** that make bundle freezes verifiable |

## 3 · Results — one directory per landed gate

Every bundle carries `README.md`, `PROVENANCE.md`, `MANIFEST.tsv`, `INPUTS.tsv`,
`OUTPUTS.tsv`, `run.sh`, `env.lock` and `scripts/`, and passes `bundle_valid.sh`.

### Stage 1 — database characterization (closed)

`results/dbchar_g1_corpus_identity` · `dbchar_g2_canonical_units` · `dbchar_g2b_rt_cds_recovery`
· `dbchar_g3_pair_geometry` · `dbchar_g4_family_baseline` · `dbchar_g5_metadata_sampling` ·
`dbchar_g6_tool_calls` · `dbchar_g7_stage1_report` · `dbchar_g7b_stage1_extended_report`

### Stage 2 — RT0–RT7 definition and the mapper

| bundle | role |
|---|---|
| `rt07_g1_history_and_definition` | what the historical RT0–RT7 labels ever meant |
| `rt07_g2_reference_reconstruction` | independent reconstruction of the landmarks |
| `rt07_g3_prior_method_replication` | which prior results survive regeneration |
| `rt07_g4a_repaired`, `rt07_g4a_frame_recovery` | mapper development and repair |
| `rt07_pre_g4_*`, `rt07_mapper_validation_repair*`, `rt07_residue_mapper_gate`, `rt07_ug5_holdout_gate` | the validation trail, including **failed designs** — kept deliberately |
| `FINAL_PRE_UG25_VALIDATION_BUNDLE` | the frozen pre-holdout state |
| `rt07_ug25_confirmatory` | the single confirmatory holdout run |
| **`rt07_g4b_production_mapper`** | **the frozen production instrument** |
| **`rt07_g5a_eligibility_census`** | **the frozen denominator** |
| **`rt07_g5_catalogue_application`** | **the canonical mapped dataset** |

Superseded bundles are retained as audit history. They are **not** rebuilt to satisfy later
packaging conventions; see `docs/decisions/2026-09-17_stage2_launcher_g4b_freeze_amendment.md` §2.

## 4 · The frozen instrument

```
results/rt07_g4b_production_mapper/
├── PRODUCTION_SPEC.md          the instrument, its scope and its limits
├── code/rtmap/
│   ├── mapper.py               THE FROZEN MAPPER — byte-identical since validation
│   ├── params.py               frozen parameters, read from control/, double-guarded
│   ├── version.py              instrument identity and the compact version id
│   ├── schema.py               rtmap-schema-1.0
│   ├── crosswalk.py            historical RT0–RT7 accessor (all UNRESOLVED)
│   └── run_mapper.py           the production runner
├── control/                    frozen parameter tables, 150 anchors, RT0–RT7 crosswalk
├── docs/                       output schema, Stage-1 metadata role, g5/g6/g7 plans
├── scripts/                    freeze tests, smoke test, repair checks, timing
└── tables/                     landed smoke products and evidence
```

The profile itself lives at `results/rt07_g4a_repaired/work/GII.deriv.hmm` — tracked as an
explicit exception to the `results/**/work/` ignore rule, because it defines the coordinate
system.

## 5 · Data and scratch — not in GitHub

| path | size | state |
|---|---|---|
| `data/derived/` | 2.2 GB | canonical derived datasets. Gitignored; `data/README.md` is the register and **is** tracked |
| `ARIS_OUTPUT/` | 23 GB | disposable scratch, including 12 GB of g5 shards |
| `MELISSA_DATA/` | 1.8 GB | raw external corpora |
| `references/rt0_rt7/literature/*.pdf` | — | publisher PDFs, registered but not redistributed |

## 6 · Conventions worth knowing before editing anything

* **One repo; git holds versions.** Never create a version-numbered sibling project directory.
* Large canonical data stay in place and are read-only. Do not copy raw data to start a task.
* Atypical biology is **flagged before it is filtered** — distance, orientation, missing
  ncRNA, multiplicity, contig-edge state, tool disagreement and unusual architecture are all
  retained.
* `MULTI` is its own multi-label population, never appended to a single RT family.
* Tool-specific fields whose provenance differs are never pooled.
* A zero/absence claim needs a positive control on an appropriate substrate.
* `results/` holds only reproducible bundles. Scratch belongs in `ARIS_OUTPUT/`.
