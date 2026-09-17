# DBCHAR WORKBENCH — the Stage-1 thesis-writing workspace

The Stage-1 database-characterization *gates* are landed and tracked
(`results/dbchar_g1…g7b`). Separately, there is an **exploratory workbench** used to turn
those gates into thesis text and figures. This file says what it is, where it is, what is in
it, and what is safe to rely on.

---

## 1 · Where it is, and what it is not

| | |
|---|---|
| path | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench` |
| git | a **linked worktree** of this repository, branch `dbchar-workbench` — see `docs/EXTERNAL_WORKTREES.md` |
| pushed? | **No — local only, by operator decision** |
| working material | `ARIS_OUTPUT/dbchar_workbench/` — **gitignored, in no branch** |
| size | 88 MB (16 MB excluding a 72 MB `.venv`) |

Its own `CONTEXT.md` states the rule plainly:

> **Status:** exploratory workbench. **Not** a governed gate. It does not rewrite, supersede
> or re-derive the landed `dbchar_g1`…`dbchar_g7` bundles. Everything produced here lives
> under `ARIS_OUTPUT/dbchar_workbench/` and is disposable until an operator decision promotes
> it.

**Authority order** (highest first), from the same file:

1. `docs/decisions/2026-09-15_stage1_population_rules.md` — population rules
2. `results/dbchar_g7_stage1_report/` + `tables/g7_resolved_values.tsv`
3. the landed `dbchar_g*` bundles
4. the workbench — **exploratory, never authoritative**

## 2 · What is in it

| directory | size | files | content |
|---|---|---|---|
| `CONTEXT.md` | 21 KB | 1 | units, denominators, dataset inventory, joins, findings, known artefacts, canonical-vs-exploratory rule |
| `exports/` | 148 KB | 7 | `RESULTS_database_characterization_DRAFT.md`, `THESIS_todo_resolutions.md` |
| `exports_v2/` | 3.1 MB | 45 | thesis figure set, LaTeX tables, numbering plan, corrections, RT–ncRNA dataset handover |
| `figures/` | 3.6 MB | 44 | earlier figure iterations |
| `tables/` | 376 KB | 85 | working summary tables |
| `notes/` | 28 KB | 4 | triage and review-response notes |
| `scripts/` | 300 KB | 18 | `build_nb_part*.py` notebook builders, `check_tex_numbers.py` |
| `*.ipynb` | ~8 MB | 6 | the main workbench notebook, three near-duplicate copies, a playground notebook |
| `.venv/` | 72 MB | — | never track |

## 3 · What a downstream scientific-planning session needs from it

`CONTEXT.md` answers, in its own sections: canonical analytical units and denominators (§1);
dataset inventory (§2); joins and keys (§3); the main Stage-1 findings a new analysis must not
contradict (§4); **known artefacts that must not be interpreted biologically** (§5); QC,
eligibility and exceptional populations to keep visible (§6); and the canonical-vs-exploratory
rule (§7).

`docs/dbchar_workbench_snapshot/exports_v2/RT_NCRNA_DATASET_HANDOVER.md` is the handover for
the RT–ncRNA pair datasets. `docs/dbchar_workbench_snapshot/exports_v2/FIGURE_SET.md` and
`docs/dbchar_workbench_snapshot/exports_v2/PLAN_numbering_and_figures.md` define the thesis
figure set and its numbering.
`docs/dbchar_workbench_snapshot/exports_v2/CORRECTIONS_current_thesis_section.md` lists
corrections already applied to the draft. (Each of these is the tracked snapshot; the live
file sits under `ARIS_OUTPUT/dbchar_workbench/exports_v2/` in the workbench worktree.)

## 4 · A text snapshot IS tracked here

Because the workbench is gitignored on a local-only branch, its markdown was the **only copy**
of substantial scientific writing. A point-in-time snapshot is tracked at:

```
docs/dbchar_workbench_snapshot/        232 KB, 17 markdown files
├── CONTEXT.md                         the handoff document
├── README.md, NEXT_SESSION_PROMPT.md
├── current_thesis_section_content.md   the thesis section draft
├── exports/                            results draft, TODO resolutions
├── exports_v2/                         figure set, numbering plan, corrections, handover
└── notes/                              triage and review notes
```

**This is a snapshot, not the live copy.** Taken 2026-09-17. The live files remain at
`…-dbchar-workbench/ARIS_OUTPUT/dbchar_workbench/`, and they will drift from this snapshot as
work continues. When they do, re-snapshot deliberately rather than editing the copy.

**Not** snapshotted, and still single-copy on local disk: the notebooks (~8 MB), the figures
(~7 MB across `figures/` and `exports_v2/`), the LaTeX tables, and the working `tables/`.

## 5 · Open recommendations for the operator

1. **Back up the notebooks and figures off this host.** They are ~15 MB, they are not in any
   branch, and they represent substantial writing. This is the largest remaining
   single-point-of-failure in the project.
2. **Consolidate the notebooks.** There are four near-identical
   `database_characterization_workbench*.ipynb` files (3.9 MB, 117 KB, 111 KB, 111 KB). Pick
   one; the 3.9 MB size is embedded output, which should be stripped before any tracking.
3. **Decide canonical vs exploratory for `tables/` and `figures/`.** `CONTEXT.md` §7 has the
   rule; the classification has not been applied to the files themselves.
4. If the workbench is ever promoted, promote it to a tracked path on `main`
   (e.g. `sidework/dbchar_workbench/`) rather than pushing the `dbchar-workbench` branch —
   that branch has zero unique commits and adds nothing.
