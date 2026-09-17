# Retron / reverse-transcriptase PhD project

Large-scale mining and characterization of reverse transcriptases and retrons from genome and
metagenome data, and the construction of a defensible instrument for mapping conserved HMM
states to actual residues in individual RT proteins.

Every measurement is made on an explicit analytical unit — raw record, genomic locus, exact
RT, taxonomic occurrence, RT–ncRNA pair — so that every number has a named biological
population and a stated denominator.

> **New here?** Read **[`docs/CURRENT_PROJECT_STATE.md`](docs/CURRENT_PROJECT_STATE.md)**
> first. It gives the stage, the frozen instrument and the headline numbers in one page.

---

## Where the project stands

| | |
|---|---|
| Stage 1 — database characterization | **closed** |
| Stage 2 — mapper validation | **closed at Endpoint A**; confirmatory transfer supported |
| `g4b` production freeze | **complete** |
| `g5` catalogue application | **complete** |
| `g6`, `g7` | authorised / not started |

**Frozen instrument:** `rtmap-1.0.0/53a1e738a19b3896`
(mapper code `69575dc7…f10fceef`, profile LENG 471 under `hhmake -M 50`).

**Catalogue:** 501,561 Stage-1 exact RTs → **369,381 eligible** → **354,102 inspectable**,
55,407,150 state calls. The denominator is 369,381, not 501,561.

## Clone

```bash
git clone --recurse-submodules <repo-url>
```

`general/` is a **submodule** carrying the governance layer. Without `--recurse-submodules`
it is empty and the project appears to have no rules.

## Layout

| path | what it is |
|---|---|
| `docs/CURRENT_PROJECT_STATE.md` | **start here** — state, instrument, numbers, constraints |
| `docs/PROJECT_ANALYSIS_PRINCIPLES.md` | 40 reusable methodological principles from Stage 2 |
| `docs/PROJECT_MAP.md` | what lives where |
| `docs/DATASET_REGISTRY.md` | every heavy local dataset: path, size, rows, sha256 |
| `docs/EXTERNAL_WORKTREES.md` | the submodule and the second worktree |
| `docs/DBCHAR_WORKBENCH.md` | the Stage-1 thesis workbench (local only) |
| `docs/decisions/` | settled decisions; superseded by new records, never rewritten |
| `docs/BLOCKED.md` | open questions and recommended defaults |
| `CLAUDE.md` | operating context and conventions |
| `idea-stage/docs/research_contract.md` | the single claim authority |
| `launchers/` | one per track — objective, kill criteria, inputs, gates |
| `results/` | one directory per landed gate, and nothing else |
| `retros/` | one retro per gate |
| `review-stage/` | independent-review requests, manifests, external pinned roots |
| `references/` | comparator assets and prior-work inventory |
| `general/` | **submodule** — the governance layer |
| `data/README.md` | the input register (`data/` itself is not in git) |

## What is deliberately not in this repository

| path | size | why |
|---|---|---|
| `data/` | 2.2 GB | canonical derived datasets. Registered in `docs/DATASET_REGISTRY.md` |
| `ARIS_OUTPUT/` | 23 GB | disposable scratch, incl. 12 GB of g5 shards |
| `MELISSA_DATA/` | 1.8 GB | raw external corpora |
| `results/**/work/` | ~98 MB | per-gate alignment intermediates, regenerable |
| `references/**/*.pdf` | — | publisher PDFs: registered, not redistributed |

The one exception inside an ignored directory is
`results/rt07_g4a_repaired/work/GII.deriv.hmm` (215 KB) — the frozen profile that defines the
production coordinate system. It is tracked on purpose.

## Reproducing the landed work

Every bundle under `results/` carries `run.sh`, `verify.sh`, `MANIFEST.tsv`, `INPUTS.tsv`,
`OUTPUTS.tsv`, `PROVENANCE.md` and `env.lock`, and passes the governance bundle standard:

```bash
bash general/checks/bundle_valid.sh results/<bundle>
bash results/rt07_g5_catalogue_application/verify.sh
```

The g5 application itself re-runs in about ten minutes on 44 cores, CPU only, from
`data/derived/rt_exact_v1.faa` plus the frozen instrument.

## Standing constraints on interpretation

* The mapper's frame is **GII-centred**: median callability runs 0.94 (GII) to 0.49 (Retron).
  This is a property of the instrument and a confound for every between-family comparison.
* `DELETED_STATE` is a statement about the alignment path, **not** an absent region.
* `NO_SUPPORTED_MAPPING` is **not** biological absence; abstention is not failure.
* MyRT / PADLOC / DefenseFinder labels are **strata, never validation truth**. No accuracy,
  sensitivity, specificity or ROC against them.
* Historical RT0–RT7 remains `UNRESOLVED`; production emits `state_id`.
* Scope is `hhmake -M 50` only.
