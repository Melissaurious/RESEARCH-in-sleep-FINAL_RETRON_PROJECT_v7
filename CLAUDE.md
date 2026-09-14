# CLAUDE.md — Retron large-scale mining project

This project measures genome- and metagenome-derived RT/retron observations on explicit
analytical units — raw record, genomic locus, exact RT, taxonomic occurrence and RT–ncRNA
pair — so every downstream number has a named biological population and denominator.

**One repo; git holds versions. Never create a version-numbered sibling project directory.**

## Governed by

`general/` is the governance layer and is pinned by git revision. ARIS owns the research
workflow; `general/` constrains data safety, evidence standards, provenance, reporting,
compute policy, Ibex execution and operator-only decisions.

Before provenance-bearing execution:

```bash
git submodule update --init --recursive
bash general/checks/specs_exist.sh
```

Read `general/CLAUDE.md` at session start.

## Read before acting

- `idea-stage/docs/research_contract.md` — single project claim authority.
- `launchers/LAUNCHER_01_database_characterization.md` — current active task scope and autonomy envelope.
- `data/README.md` — canonical inputs, prior resources, environments and trust state.
- `docs/decisions/` — settled operator decisions; supersede by a new record, never by
  silently rewriting history.

Read when relevant:
- `/home/borg/RETRON_STAGES/` or the registered upstream stage briefs — idea/path/history source only,
  not claim authority.
- `IDEAS.md` — deferred work if present.
- `docs/BLOCKED.md` — open questions and defaults.

There is no hand-maintained `GOALS.md`, `CLAIMS.md` or `ROADMAP.md` claim authority.

## Environment

- **Primary local env:** `retron_tradicional`
  - `/home/borg/miniconda3/envs/retron_tradicional`
- **Primary Ibex env:**
  - `/ibex/user/rioszemm/conda-environments/retron_tradicional`
- **Project root:**
  - `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7`

Do not use `base`.

Special tools/resources live outside the primary environment and are registered in
`data/README.md`; do not conclude a dependency is absent until the registered environments
and Ibex resources have been checked.

## Project conventions

- Large canonical data stay in place and are read-only. Do not make another raw-data copy
  merely to start a task.
- Small, load-bearing reference files may be copied into the project after identity/hash is
  recorded; if an equivalent copy already exists under `MELISSA_DATA/`, use it.
- Prior projects and reports are sources to audit and reuse, not numeric authority.
- Atypical biology is flagged before it is filtered. Distance, orientation, missing ncRNA,
  multiplicity, contig-edge state, tool disagreement and unusual architecture are retained.
- `MULTI` remains its own multi-label population and is not appended to a single RT family.
- RT analyses do not silently mix ncRNA-anchor-only records into their denominator.
- Never pool tool-specific fields whose provenance differs; preserve the original tool call.

## Working storage

- ARIS scratch for the current task: `ARIS_OUTPUT/01_database_characterization/` — disposable and gitignored.
- Reproducible scientific products: `results/` with one directory per landed gate.
- Registered expensive reusable derived datasets: `data/derived/` only when a launcher names
  them and their producing bundle/hash is recorded.
- Do not copy an entire `ARIS_OUTPUT/` task into `results/`. Land only what is required to
  reproduce and understand the accepted measurement.

## Before any negative or absence claim

A zero/absence needs a positive control showing that the same instrument can recover a
known-present case on an appropriate substrate. Null and refuting results are retained.

## Stage documents and prior work

`/home/borg/RETRON_STAGES/` contains useful scientific framing, old results, failure modes and paths.
Use it to accelerate planning. When it conflicts with the current raw data, current project
decisions, or a newer verified bundle, the latter wins.

For database characterization, the most current historical source is
`LAUNCHER_stage0_database_copy.md` together with the prior production project
`/home/borg/RESEARCH-retron-db/`. The new task follows:

**REUSE → VERIFY → GAP ANALYSIS → COMPUTE ONLY GAPS.**

## ARIS pipeline state

| | |
|---|---|
| Research direction | Build a defensible large-scale RT/retron catalogue from genome and metagenome mining outputs, then use explicit analytical objects to study RT classification/architecture, genomic organization, ncRNA association, annotation limits, diversity and RT–ncRNA co-evolution. |
| Current stage | `contract` |
| Target venue | PhD thesis plus retron methods/classification manuscript; journal venue TBD |
| `AUTO_PROCEED` | `true` |
| Executor / reviewer | ARIS-configured executor / independent reviewer per project profile and governance |
| Compute budget | see the active launcher §9 |
| Effort levels | ARIS defaults unless a launcher explicitly overrides them |

## Governance

ARIS owns lifecycle, `.aris/`, `idea-stage/`, `research-wiki/`, `paper/`,
`EXPERIMENT_PLAN.md`, `EXPERIMENT_LOG.md`, loops and reviewer routing.

`general/` owns how the work is constrained.

Before the active task:

```bash
bash general/checks/specs_exist.sh
python3 general/tools/check_launcher.py launchers/LAUNCHER_01_database_characterization.md
```
