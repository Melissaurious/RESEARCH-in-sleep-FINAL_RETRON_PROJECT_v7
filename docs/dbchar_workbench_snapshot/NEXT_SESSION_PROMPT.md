# Prompt for the next clean session

Copy everything below the line into a fresh session started in
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench`.

---

I am continuing work on the Stage-1 retron database-characterization workbench. Read
`ARIS_OUTPUT/dbchar_workbench/README.md` and `ARIS_OUTPUT/dbchar_workbench/CONTEXT.md` first —
they define the analytical units, denominators and known artefacts. Do not re-derive them.

## Where things are

- Worktree: `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench` (branch
  `dbchar-workbench`). **Never modify the main worktree** at
  `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7`; a parallel governed session may be running.
- Everything I am working on is under `ARIS_OUTPUT/dbchar_workbench/` (gitignored, disposable).
- Canonical datasets are **read-only** in the main worktree at
  `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/` (16 parquet files).
- Landed Stage-1 bundles `results/dbchar_g1…g7` are **authority and must not be rewritten**. The
  workbench is exploratory, not a governed gate.

## Current state

- `database_characterization_workbench.ipynb` — 148 cells, 0 errors. Sections: A corpus/redundancy,
  B families, C ncRNA, D geometry, E scaffold, F pairing topology, G/H/I scaffolds, J open slot,
  K dataset inventory, L thesis-question resolutions, M operon visualisation, N thesis figure set.
- `exports/thesis/results_database_characterization.tex` — the thesis Results chapter, v2,
  restructured around a dataset funnel. 10 figures, 5 tables, all resolving.
- 28 PNG + 11 PDF figures, 69 cached TSVs. Every number in the `.tex` traces to a table.

## Working rules — important

1. **The notebook is generated.** Its source is `scripts/build_nb_part1..9.py`; `scripts/README.md`
   maps each file to its sections. Edit those and rebuild. Never hand-edit the `.ipynb`.
2. **Never read the `.ipynb` into context** — it is ~3.6 MB, mostly base64 images. To inspect a
   result, read the relevant `tables/*.tsv` (all small) or view one specific PNG.
3. Rebuild and verify with:
   ```bash
   cd ARIS_OUTPUT/dbchar_workbench
   export JUPYTER_PATH=$PWD/.venv/share/jupyter MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar
   .venv/bin/python scripts/build_nb.py database_characterization_workbench.ipynb
   .venv/bin/python -m nbconvert --to notebook --execute --inplace \
     --ExecutePreprocessor.timeout=2400 --ExecutePreprocessor.kernel_name=dbchar-workbench \
     database_characterization_workbench.ipynb
   .venv/bin/python scripts/check_tex_figures.py
   ```
   ~45 s cold. Then `cp database_characterization_workbench.ipynb playground/melissa_playground.ipynb`.
4. Python lives in `ARIS_OUTPUT/dbchar_workbench/.venv` (overlay on `retron_tradicional`, adds
   duckdb, matplotlib, matplotlib-venn). The setup cell bootstraps it onto `sys.path` under any
   kernel. **Do not install into `retron_tradicional`** — it is the governed env.
5. `playground/melissa_playground.ipynb` is my editable copy; it redirects output via `DBCHAR_OUT`
   so it cannot overwrite the canonical `tables/` and `figures/`.

## Decisions already made — do not reopen

- Two analytical populations: `POP_RT_SEQ` (sequence-level, 493,964 distinct proteins) and
  `POP_RT_CTX` (context-level, 477,956). Contig clipping is a **stratification flag, not an
  exclusion**.
- MULTI is excluded from family statistics and retained in sequence-level ones; 99.8 % of its
  proteins have a best-vs-second margin below 20 bits, so pooling to a best label is not supportable.
- `RVT-CRISPR` and `RVT-CRISPR-like` are **not** merged (median lengths 468 vs 331 aa).
- Overlapping placements are **retained** as a flagged class (97.36 % overlap only the RT gene
  itself, median 22 bp). Only 266 fully-internal and 45 non-RT-CDS cases are set aside.
- "Canonical placement" is renamed **"eligible, non-redundant placements"** in the thesis text.
- Tool-agreement analysis is on **distinct RT proteins**, not records.
- The operon figure uses the project artwork `retron_ncrna4.svg`, all loci normalised to the `+`
  strand with an always-visible badge giving the strand actually found.

## Corrections already applied — keep them

- Same-strand rate is **99.12 %**, not the 99.8 % in the landed g7 report prose (that figure is an
  unregistered hard-coded literal; see `notes/2026-09-16_same_strand_discrepancy.md`).
- NCBI records carry **no phylum at all**; the phylum-naming hazard is *within* the GTDB block, where
  `gtdb_bacteria` uses current names and `mgnify_human_gut` an older release vintage.
- "18 distinct ncRNAs" describes the downstream **technical mode** (5,234 placements), not all
  downstream placements (6,761 over 230 sequences).
- The exact-pair view (30,924) is built on **eligible**, not canonical, placements; 30,427 pairs are
  canonical-derived.

## What I want to do next

1. **Refine the notebook** — tighten sections, fix anything I flag, and implement the remaining
   scaffolds (E tool agreement at protein level, G MULTI, H taxonomy, I QC) if I ask for them.
2. **Refine the figures** — I will review them individually and ask for changes to specific panels.
3. **Refine the final analysis text** in
   `exports/thesis/results_database_characterization.tex`, paragraph by paragraph.

Start by telling me the current state of the three, then wait for my direction — do not begin
rewriting anything until I say which part to work on.

## Known blockers, unresolved

- **Sequence clustering has not been run**, on either the RT or the ncRNA side. It blocks the true
  pairing topology, the distinctness claim, and any train/test split. All counts are upper bounds.
- **Phylum name harmonisation** across GTDB vintages is not done; no phylum figure exists.
- Covariance-model `score`/`evalue` are now used in the dataset funnel (E ≤ 1e-5) but nowhere else.

## Style

Report outcomes faithfully; if something fails or a number disagrees with a landed bundle, say so
plainly with the evidence rather than smoothing it over. Check claims against the data instead of
asserting them. Every number needs its analytical unit and denominator named.
