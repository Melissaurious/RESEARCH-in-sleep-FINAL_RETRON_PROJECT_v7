# dbchar RT–ncRNA workbench — evidence and analysis layer

## Status — read before using anything here

> **This is an exploratory / curation workbench snapshot. It is NOT a governed gate.**
>
> - It is **not** a Stage-1 gate bundle and must not be cited as one. It has no `MANIFEST.tsv`,
>   no pinned root, no independent review and no operator acceptance.
> - It is **not authoritative over `results/dbchar_g1`…`dbchar_g7`**. Those remain the Stage-1
>   authority. Where anything here disagrees with them, **they win**, and the disagreement is a
>   finding about this workbench, not about the database.
> - Nothing here is a project decision. The filter categories in
>   `tables/Z5_filter_catalogue.tsv` are **analytical proposals recorded by the workbench**, not
>   canonical inclusion rules. In particular `USE` means *"defensible, and here is what it
>   costs"* — it does **not** mean the project has adopted those filters.
> - It lives under `analysis/`, deliberately outside `results/`, so that it cannot be mistaken
>   for a landed gate by a reader or by a script that walks `results/`.
> - It may be **promoted later only through an explicit governed task** that re-derives what it
>   needs, lands a proper bundle with provenance and review, and records an operator decision.
>   Until then, treat every number here as exploratory.

## Where the prose lives — not here

> **`docs/dbchar_workbench_snapshot/` is the canonical copy of the workbench's prose and
> context.** Read it first. This directory deliberately does not duplicate it.

| you want | go to |
|---|---|
| the dataset tiers, every confidence flag and its cost, splitting hazards, how to pull the data | `docs/dbchar_workbench_snapshot/exports_v2/RT_NCRNA_DATASET_HANDOVER.md` |
| analytical units, denominators, known artefacts | `docs/dbchar_workbench_snapshot/CONTEXT.md` |
| the population registry and how six denominator collisions were closed | `docs/dbchar_workbench_snapshot/exports_v2/PLAN_numbering_and_figures.md` |
| line-by-line corrections to the earlier thesis draft | `docs/dbchar_workbench_snapshot/exports_v2/CORRECTIONS_current_thesis_section.md` |
| the figure/table manifest and the plots still to build | `docs/dbchar_workbench_snapshot/exports_v2/FIGURE_SET.md` |
| what changed in the notebook and what is still open | `docs/dbchar_workbench_snapshot/exports_v2/IMPLEMENTED.md` |
| decisions and discrepancies found along the way | `docs/dbchar_workbench_snapshot/notes/` |
| **matched vs unmatched retron loci — start here for absence work** | the **Z6** section of `…/RT_NCRNA_DATASET_HANDOVER.md` |
| which build script holds which notebook section | `docs/dbchar_workbench_snapshot/exports_v2/SCRIPTS_README.md` |

**This directory holds the reproducible evidence and analysis layer** — the numbers those
documents cite, the code that regenerates them, the rendered figures, and the thesis chapter
source. Prose there, evidence here.

## Layout

```
tables/    87 TSV — the evidence layer. Every number in the chapter traces to one of these.
scripts/   17 py — the notebook generator plus two checkers. Regenerates everything.
           Its section map is the canonical SCRIPTS_README.md linked above, not duplicated here.
figures/   13 PNG — the chapter figure set.
docs/      results_database_characterization.tex — the thesis Results chapter
           tables_tex/tab_venn_agreement.tex     — a generated table the chapter includes
```

Snapshot date 2026-09-17, amended 2026-09-18 to remove prose duplicated in the canonical docs
snapshot. Source: `ARIS_OUTPUT/dbchar_workbench/` (gitignored, disposable).

Deliberately absent: the `.ipynb` (4 MB, regenerates in ~90 s from `scripts/`), the playground
copy, the virtualenv, and the pre-correction `exports/` audit trail.

## The proposed datasets

`tables/Z1_association_resource_tiers.tsv`. Nested. **T3 is the workbench's proposed default —
a proposal, not an adopted project population.**

| tier | rule added | pairs | assoc. | RTs | RNAs |
|---|---|---|---|---|---|
| T1 observed | eligible, non-redundant, Retron | 30,287 | 28,845 | 28,838 | 15,906 |
| T2 architecture | + same strand, not downstream, no CDS between, ≤ 200 bp | 25,673 | 24,677 | 24,677 | 13,258 |
| **T3 high-confidence** | **+ model hit E ≤ 1e-5** | **23,680** | **22,727** | 22,727 | 11,849 |
| T4 independently recurrent | + recurs across genomes or species | 7,476 | — | 7,187 | 3,829 |

"assoc." counts distinct `(rt_seq_hash, detection_model)` — invariant to the boundary trimming
that inflates exact pairs by 4.0 %.

## Matched vs unmatched retron loci — Z6

`tables/Z6_matched_summary.tsv` carries the aggregates. The **row-level table
`Z6_locus_matched_status.parquet` (630,741 rows, one per Retron locus, 53 MB) is NOT in this
snapshot** — it lives in the workbench at `ARIS_OUTPUT/dbchar_workbench/tables/` and is rebuilt by
notebook section Z6. Keys to rejoin it: `locus_key`, `physical_locus_key`, `rt_system_id`,
`record_key_any`, `rt_seq_hash`, `genome_id_norm`, `contig_norm`.

The unmatched class is `NO_NCRNA_CALL_IN_RETAINED_WINDOW` — **not** biological absence. One
detector, one retained window, no positive control. Never relabel it.

| stratum | loci | unmatched |
|---|---|---|
| overall | 630,741 | 47.24 % |
| window clipped at a contig edge | 212,449 | 62.52 % |
| window intact | 418,292 | 39.48 % |
| **< 200 bp retained upstream of the RT** | 44,038 | **87.27 %** |
| 200–1000 bp upstream | 24,923 | 74.07 % |
| ≥ 1000 bp upstream | 561,780 | 42.91 % |

`bp_available_upstream` separates detector absence from unavailable search space. Condition on it
before any matched-vs-unmatched comparison, or the difference you measure is mostly instrument.

## Filtering further — and what the categories mean

`tables/Z5_filter_catalogue.tsv`, one row per candidate flag with its SQL predicate and measured
cost. The `category` column records **the workbench's assessment**, and nothing more:

| category | meaning | n |
|---|---|---|
| `IN_T3` | already applied in the proposed default tier | 5 |
| `USE` | defensible addition, with its measured cost stated — **not an adopted rule** | 5 |
| `STRATIFY` | keep as a column; filtering on it is not supported | 3 |
| `TRAP` | looks like a quality flag, is not — see the row's `note` | 2 |
| `NOOP` | already guaranteed upstream; costs nothing, gains nothing | 3 |

Two `TRAP` rows are load-bearing and should not be quietly re-adopted:

- `has_structure_annotation` is populated on **1.37 %** of placements. It records annotation
  coverage, not quality; filtering on it keeps 1,814 of 30,287 pairs.
- `drop_outgroup_models` was **proposed and rejected**. Outgroup-model calls sit in canonical
  retron architecture — 93.1 % upstream, 99.3 % same-strand, 99.2 % with no intervening CDS,
  median gap 27 bp, all comparable to or tighter than the other nineteen models. Evidence:
  `tables/Z4_outgroup_vs_rest.tsv`.

Costs in that table are **marginal** — each flag applied alone to T1. For cumulative tiers use
`tables/Z1_association_resource_tiers.tsv`.

## Reproducing

Canonical inputs are unchanged and read-only at `data/derived/`. With the workbench venv:

```bash
cd ARIS_OUTPUT/dbchar_workbench
export JUPYTER_PATH=$PWD/.venv/share/jupyter MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar
.venv/bin/python scripts/build_nb.py database_characterization_workbench.ipynb
.venv/bin/python -m nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=2400 --ExecutePreprocessor.kernel_name=dbchar-workbench \
  database_characterization_workbench.ipynb
.venv/bin/python scripts/check_tex_figures.py    # 13/13 figures resolve
.venv/bin/python scripts/check_tex_numbers.py    # 92/92 chapter numbers match tables/
```

## Known limits

- **No sequence clustering, either side.** Every distinctness and topology count is an upper
  bound; no saturation or richness estimate is available; no defensible train/test split exists.
  RT clustering is unblocked (`rt_exact_v1.faa`); ncRNA clustering needs a FASTA that does not yet
  exist in `data/derived/`.
- **No phylum harmonisation** across GTDB vintages; NCBI carries no phylum at all.
- **No functional annotation of RT neighbours** — all 41.3 M neighbouring CDS have
  `has_sequence = False`.
- One `% CITATION NEEDED` remains in the chapter `.tex`.
