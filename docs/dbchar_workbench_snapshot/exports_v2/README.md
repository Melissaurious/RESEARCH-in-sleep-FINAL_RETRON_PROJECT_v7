# exports_v2 — the numbering rebuild

Created 2026-09-17. `exports/` is untouched and remains the audit trail of what the chapter said
before this pass.

| file | what it is |
|---|---|
| **`results_database_characterization.tex`** | **the complete chapter, corrected.** Drop-in replacement for `current_thesis_section_content.md`. 12 figures, 6 tables, 0 orphan labels, all `\includegraphics` verified against the staged figure folder |
| `figures_db_thesis_section/` | the 12 chapter figures (PNG + PDF where available), named exactly as the `.tex` expects |
| `figures_supplementary/` | the 13 supplementary figures |
| `FIGURE_SET.md` | the figure/table manifest, what changed from your draft's set, and specs for the 6 plots still to build |
| `PLAN_numbering_and_figures.md` | the population registry, the six collisions and how each is closed, and where to edit each figure in the notebook |
| `CORRECTIONS_current_thesis_section.md` | line-by-line corrections to `current_thesis_section_content.md`, each with the table that proves it |
| **`RT_NCRNA_DATASET_HANDOVER.md`** | **self-contained handover for a fresh conversation** — the four tiers, every confidence flag with its measured cost, the splitting hazards, and how to pull the data |
| `IMPLEMENTED.md` | what was changed in the notebook on 2026-09-17, and what is still open |

Nothing here is a governed gate. `results/dbchar_g1…g7` remain authority.

## The one rule this directory exists to enforce

> Every number carries its population id. Every cached table declares one via
> `cache(..., pop=...)`. Every figure declares one via `savefig(..., pop=...)` and prints it
> along its bottom edge. The ids and their sizes are computed, never typed, in notebook
> section **0.2 (Z0)** → `tables/Z0_population_registry.tsv`.

None of the six confusions found in the draft was a wrong number. Every one was a correct number
whose population was not printed beside it.
