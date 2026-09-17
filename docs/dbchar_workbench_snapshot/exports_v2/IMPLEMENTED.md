# Implemented 2026-09-17

Notebook rebuilt and executed cold: **165 cells, 0 errors, ~90 s**.
`check_tex_figures.py`: **11 figure references, 11 resolved, 0 missing.**

## Notebook / scripts

| change | file |
|---|---|
| `cache(..., pop=)` records a table's population into `tables/_table_populations.tsv` | `build_nb_part1.py` |
| `savefig(..., pop=)` stamps the population onto the figure and into `FIGURE_PROVENANCE.tsv` (new `population` column) | `build_nb_part1.py` |
| `register_pop`, `pop_row`, `pop_stamp` helpers | `build_nb_part1.py` |
| `savefig2(..., pop=)` passes through for the PDF figures | `build_nb_part9.py` |
| **new section 0.2 (Z0)** — the 18-row registry, computed from parquet, plus five guard rails | `build_nb_part1b.py` |
| N3 side table no longer reversed relative to its plot; gained a `family` column | `build_nb_part9.py` |
| N6 split into `N6a_taxa_redundancy` and `N6b_cm_confidence`; N6b gained a per-model panel | `build_nb_part9.py` |
| new table `N6_cm_confidence_by_model` | `build_nb_part9.py` |
| N5 re-based from `PL-ELIG` onto `PL-CANON` | `build_nb_part9.py` |
| overlap class renamed "ncRNA fully enclosed by a CDS" + a printed warning about the other 266 | `build_nb_part9.py` |
| `N1_tool_sets` stripped of its double-counting protein columns | `build_nb_part9.py` |
| new table `A4_multi_database_loci_by_population` (both locus populations) | `build_nb_part2b.py` |
| F0 print computed instead of hard-coded 30,924 / 30,427 | `build_nb_part5f.py` |
| `WHICH FUNNEL IS THIS?` block in L7 and a matching warning in K2 | `build_nb_part7.py`, `build_nb_part6.py` |
| 17 A–F figures + 9 N figures now carry a population stamp | all parts |
| **new section Z1** — the four resulting dataset tiers, the T3 topology per direction, and the boundary-jitter measurement | `build_nb_part9.py` |
| new tables `Z1_association_resource_tiers`, `Z1_t3_topology`, `Z1_t3_partner_jitter` | `build_nb_part9.py` |
| **new section Z2.1** — the tool-agreement table on both axes, asserted to partition each axis, emitted as generated LaTeX to `exports_v2/tables_tex/tab_venn_agreement.tex` | `build_nb_part9.py` |
| **new section Z2.2** — redundancy by taxonomic domain, figure `Z2_redundancy_by_domain` | `build_nb_part9.py` |
| new tables `N1_tool_agreement_table`, `Z2_redundancy_by_domain`, `Z2_redundancy_by_domain_family` | `build_nb_part9.py` |
| **new section Z3** — what the exact-sequence grain measures: singletons tested against both technical explanations, then located by sampling depth | `build_nb_part9.py` |
| new tables `Z3_singleton_diagnosis`, `Z3_singleton_sampling_context`, `Z3_distinct_rt_within_species` | `build_nb_part9.py` |
| **new section Z4** — tests whether outgroup-model calls differ geometrically from the rest; they do not, so they are retained | `build_nb_part9.py` |
| new tables `Z4_outgroup_vs_rest`, `Z4_outgroup_per_model` | `build_nb_part9.py` |
| **corrected** the chapter's outgroup paragraph, which claimed the resource excluded outgroup models — it never did, and the geometry does not support excluding them | `exports_v2/*.tex` |

## Thesis `.tex` (mechanical only — no prose rewritten)

`exports/thesis/results_database_characterization.tex`:
- the N6 figure block split into `fig:taxa` (N6a) and a new `fig:cmconf` (N6b)
- the confidence sentence now cites `fig:cmconf`, not `fig:taxa`
- 97.75 % → 97.74 %; "one model … 39.2 %" → "the worst-affected model … 52.0 %"

`exports/` is otherwise untouched and remains the audit trail.

## Not done — waiting on a decision

- **The `.md` is not edited.** `current_thesis_section_content.md` is your working copy;
  `CORRECTIONS_current_thesis_section.md` is the worklist for it, keyed by line number. Say the
  word and I apply it.
- **Which document is authoritative** — the `.md` and the `.tex` have diverged (the `.md` has the
  `\dbcharproposal` blocks, the `\todo`s and `tab:dbchar:cascade`; the `.tex` has `tab:crosslabel`,
  which the `.md` dropped). They should be reconciled to one source before more text work.
- Figures **S1–S6** from the plan (MULTI margins, cross-labelled 12, outgroup separation, RT length
  ECDF, geometry schematic, locus gallery).
- Promoting `A1_unit_ladder` and `D6_joint_geometry` into the chapter, and demoting `N7`.
- Sequence clustering, phylum harmonisation — both still blocking, unchanged.

## Verification you can repeat

```bash
cd ARIS_OUTPUT/dbchar_workbench
export JUPYTER_PATH=$PWD/.venv/share/jupyter MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar
.venv/bin/python scripts/build_nb.py database_characterization_workbench.ipynb
.venv/bin/python -m nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=2400 --ExecutePreprocessor.kernel_name=dbchar-workbench \
  database_characterization_workbench.ipynb
.venv/bin/python scripts/check_tex_figures.py
```

Notebook cell **9** prints the five guard rails. All five must read `OK`.
