# Stage-1 database-characterization workbench

Exploratory workspace over the landed Stage-1 bundles. **Not a governed gate**; nothing here
rewrites `results/dbchar_g1…g7`. Everything is gitignored.

## Start here

| file | what it is |
|---|---|
| `CONTEXT.md` | units, denominators, dataset inventory, joins, artefacts. **Read first.** |
| `exports/thesis/results_database_characterization.tex` | **the thesis Results chapter** — paste-ready LaTeX |
| `exports/thesis/FIGURE_PLAN_v2.md` | every figure triaged, with denominators and verdicts |
| `database_characterization_workbench.ipynb` | the canonical notebook, 148 cells, sections A–N |
| `playground/melissa_playground.ipynb` | **your copy** — edit freely, writes to `playground/` |

## Layout

```
CONTEXT.md                     units, denominators, artefacts, joins
README.md                      this file
database_characterization_workbench.ipynb    GENERATED — do not hand-edit

scripts/                       the notebook's source (edit these, then rebuild)
  build_nb.py                    build order
  build_nb_part1..9.py           one file per group of sections (README maps them)
  check_tex_figures.py           verifies .tex <-> figures, writes FIGURE_PROVENANCE.tsv
  README.md                      rebuild command + which file holds which section

exports/thesis/                THE DELIVERABLES
  results_database_characterization.tex   thesis chapter (10 figures, 5 tables)
  FIGURE_PLAN_v2.md                       figure/table plan, post-review
  FIGURES_AND_TABLES.md                   earlier manifest, still useful for supplementaries
  FIGURE_PROVENANCE.tsv                   tex label -> figure -> notebook section -> source tables
  REVIEW_DISCUSSION.md                    your review comments, answered with data

exports/                       working drafts (audit trail, not for pasting)
  RESULTS_database_characterization_DRAFT.md   superseded by the .tex; keeps the ⚙ provenance marks
  THESIS_todo_resolutions.md                   your \todo items, answered

figures/    28 PNG + 11 PDF, plus FIGURE_PROVENANCE.tsv
tables/     69 cached aggregate TSVs (every number in the .tex traces to one)
notes/      decisions and discrepancies found along the way
playground/ your editable copy + its own tables/ and figures/
.venv/      overlay on retron_tradicional (matplotlib, duckdb, matplotlib-venn)
```

## Notebook sections

A corpus/redundancy · B families · C ncRNA · D geometry · F pairing topology · K dataset inventory ·
L thesis-question resolutions · M operon visualisation · **N the thesis figure set** ·
E/G/H/I scaffolds (tool agreement, MULTI, taxonomy, QC) · J open slot.

## Rebuild

```bash
export JUPYTER_PATH=$PWD/.venv/share/jupyter MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar
.venv/bin/python scripts/build_nb.py database_characterization_workbench.ipynb
.venv/bin/python -m nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=2400 --ExecutePreprocessor.kernel_name=dbchar-workbench \
  database_characterization_workbench.ipynb
.venv/bin/python scripts/check_tex_figures.py
```

~45 s cold. See `playground/README.md` to work in your own copy without overwriting these outputs.

## Stale files

`database_characterization_workbench copy.ipynb` and `... copy 2.ipynb` predate most of this work
and are superseded by `playground/melissa_playground.ipynb`. Safe to delete.
