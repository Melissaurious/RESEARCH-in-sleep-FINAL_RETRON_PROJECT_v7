# RT–ncRNA association dataset — handover

Written 2026-09-17 for a fresh conversation. Everything needed to rebuild, extend or defend the
dataset is here or named here. Nothing in this file is a claim; every number traces to a cached
table under `tables/`.

---

## 0. Where you are

| | |
|---|---|
| worktree | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench` (branch `dbchar-workbench`) |
| workbench | `ARIS_OUTPUT/dbchar_workbench/` — gitignored, disposable, **not** a governed gate |
| canonical inputs | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/` — **read-only**, 16 parquet files |
| landed authority | `results/dbchar_g1…g7` in the main worktree — **never rewrite** |

**Do not modify the main worktree.** It is read-only from this session's sandbox by design, and a
governed Stage-2 track lives there.

Read first: `CONTEXT.md` (units, denominators, artefacts) and `exports_v2/README.md`.

## 1. The one rule

> Every number carries its population id. Tables declare it via `cache(..., pop=...)`, figures via
> `savefig(..., pop=...)`, and the ids are computed — never typed — in notebook section **0.2**
> → `tables/Z0_population_registry.tsv`.

Ids used below: `PL-CANON` (eligible, non-redundant placement, 344,154) · `PAIR-CANON` (distinct
exact pair over those placements, 30,427) · `PAIR-ELIG` (the registered pair view, 30,924) ·
`RT-BASE-1F` (single-family exact RT proteins, 493,956).

`PAIR-ELIG` and `PAIR-CANON` differ by 497 pairs represented only by placements removed during
de-duplication. Pair **topology** is reported on 30,924; the **resource** is built on 30,427.
Never mix them. See `tables/F0_pair_view_basis.tsv`.

---

## 2. The dataset: four nested tiers

`tables/Z1_association_resource_tiers.tsv`, notebook section **Z1**.

| tier | rule added | pairs | assoc. | RTs | RNAs |
|---|---|---|---|---|---|
| T1 observed | eligible, non-redundant, Retron | 30,287 | 28,845 | 28,838 | 15,906 |
| T2 architecture | + same strand, not downstream, no intervening CDS, ≤ 200 bp | 25,673 | 24,677 | 24,677 | 13,258 |
| **T3 high-confidence** | **+ model hit E ≤ 1e-5** | **23,680** | **22,727** | 22,727 | 11,849 |
| T4 independently recurrent | + recurs across genomes or species | 7,476 | — | 7,187 | 3,829 |

**T3 is the default and the one to use.** T1 for anything that must not condition on architecture
(any test of whether architecture predicts something else would otherwise be circular). T4 for
evolutionary questions — it is the only tier in which a repeated observation is a repeated *event*
rather than a repeated deposition.

**"assoc." is not a typo.** A pair is a distinct `(rt_seq_hash, nc_seq_hash)`; both hashes are
exact, so one trimmed nucleotide makes a second pair out of one association. Counting distinct
`(rt_seq_hash, detection_model)` gives 22,727 — identical to the number of distinct RT proteins.
Use the association count wherever a trimmed nucleotide should not create a new entity. The gap is
953 pairs, 4.0 %.

### Is the many-to-many structure resolved?

Half of it. Within T3, 97.35 % of RT proteins have exactly one RNA partner, and **every one of the
602 that do not draws all its partners from a single covariance model** (530 differ by ≤ 5 nt).
Collapsing to model level resolves that direction completely.

The other direction is **not** resolved: 81.18 % of RNAs have one RT partner but the most connected
has 690, spanning 58–1,254 aa within one family label set. Fixing that needs clustering the
**proteins**. `tables/Z1_t3_topology.tsv`, `tables/Z1_t3_partner_jitter.tsv`.

---

## 3. Flags — what to account for

Measured, not assumed. Marginal cost is on canonical Retron pairs (baseline 30,287).

### 3a. Use these — they are real, populated, and cheap

| flag | column(s) | in T3? | cost alone |
|---|---|---|---|
| same strand | `same_strand` | yes | 450 |
| not downstream | `direction` | yes | 408 |
| no intervening CDS | `n_cds_between = 0` | yes | 1,539 |
| within 200 bp | `signed_distance_bp` | yes | 4,361 |
| call confidence | `evalue`, `score` | yes (E ≤ 1e-5) | 2,379 |
| RT fully inside window | `rt_in_window`, `rt_at_window_edge` | **no** | 1,436 |
| back-translation exact | `bt_status` | **no** | 4,362 |
| RT complete at both ends | `completeness_class` (join `rt_family_baseline_v1`) | **no** | — |

The last three are the only substantive additions available beyond T3. `bt_status` is worth
knowing about regardless: 322,806 placements are `exact`, but **20,662 are `alt_start`**, 362
`internal_stop_masked`, 62 `code4_tga_trp`.

### 3b. Carry as columns, never filter on them

`true_start_clipped`, `clipped_end_flag` — contig clipping is a **stratification** flag by project
convention; the RT is verified, only the window is truncated. Cost if you did filter: 10,138 and
10,842 pairs respectively, a third of the dataset.

`multiplicity_class`, `n_calls_at_locus`, `recurrence_class`, `physical_locus_key` — for weighting
and splitting, not filtering.

`detection_model`, `taxonomy_system`, `source_database`, `file_label` — stratification.

### 3c. Three traps

1. **`has_structure_annotation` is not a quality flag.** Populated on **1.37 %** of placements.
   Filtering on it takes 30,287 → 1,814. It records whether an annotation happened to exist.
   Same for `free_energy`, meaningful only where structure exists.
2. **Tool labels are not confidence.** `by_myRT` / `by_PADLOC` / `by_DefenseFinder` are
   stratification only. **Every RNA call in the corpus has `nc_source = 'infernal'`** — none came
   from a detection tool. Any association between tool set and RNA carriage is a selection effect.
3. **Do not drop the outgroup models.** See §4.

### 3d. Four flags that are already no-ops

`nc_in_window`/`nc_at_window_edge` (0 lost), `window_len_consistent AND NOT window_inverted`
(0 lost), `wellformed` (all True), `n_distinct_ncrna_seq_at_locus = 1` (118 lost). Guaranteed
upstream by the canonical definition — don't spend a filter step on them.

---

## Z6 — Matched vs unmatched retron loci (**start here for any absence work**)

`tables/Z6_locus_matched_status.parquet` is the **canonical entry point for any matched-vs-
unmatched ncRNA work.** One row per Retron locus of the context population, 630,741 rows.
Aggregates are in `tables/Z6_matched_summary.tsv`; the row-level parquet is 53 MB and lives in
the workbench, not in the committed snapshot.

**Language.** The unmatched class is `NO_NCRNA_CALL_IN_RETAINED_WINDOW`. It is **not** biological
absence of an ncRNA. It says one retron-derived covariance-model library produced no call inside
one retained window. `CLAUDE.md` requires a positive control before any absence claim, and there
is none. Never relabel this column.

| | loci | unmatched |
|---|---|---|
| overall | 630,741 | **47.24 %** |

**Condition before comparing anything.** Three strata change the answer materially:

| stratum | loci | unmatched |
|---|---|---|
| window clipped at a contig edge | 212,449 | 62.52 % |
| window intact | 418,292 | 39.48 % |
| **< 200 bp retained upstream of the RT** | 44,038 | **87.27 %** |
| 200–1000 bp upstream | 24,923 | 74.07 % |
| ≥ 1000 bp upstream | 561,780 | 42.91 % |

`bp_available_upstream` is the field that separates *detector absence* from *unavailable search
space*: essentially every real call sits upstream, so a locus retaining under 200 bp there was
never searched where the signal lives. 68,961 loci are in that position. Comparing matched
against unmatched without conditioning on it produces a difference that is mostly instrument.

Note that search space explains part and not the bulk — at ≥ 1000 bp upstream, 42.9 % are still
unmatched.

**Unit effect.** At locus level 52.8 % are matched; at protein level only 37.8 % (28,838 of
76,381 exact RTs). Matched RTs are the heavily deposited ones occupying many loci.

**Join keys** back to the rest of the project: `locus_key`, `physical_locus_key`, `rt_system_id`,
`record_key_any`, `rt_seq_hash`, `genome_id_norm`, `contig_norm`.

**Columns** include the identifiers above; `source_database`, `taxonomy_system`, `tax_domain`,
`tax_species`; `family_label`, `system_type_norm`, `system_subtype_raw`; `ncrna_status`,
`n_ncrna_calls`, `n_distinct_ncrna`, `detection_models`, `best_evalue`, `best_score`,
`evidence_tier` (`T3_HIGH_CONFIDENCE` / `T2_ARCHITECTURE` / `T1_OBSERVED` / `UNMATCHED`);
`win_len_retained`, `win_len_field`, `win_start`, `win_end`, `rt_start`, `rt_end`, `rt_strand`;
`clipped_start`, `clipped_start_raw`, `clipped_end`, `any_window_clipped`;
`dist_rt_to_contig_start`, `dist_rt_to_contig_end`, `contig_len_lower_bound`;
`rt_aa_len`, `rtcds_partial`, `bt_status`, `rt_seq_wellformed`, `elig_rt_completeness`;
`rt_in_window`, `rt_at_window_edge`, `window_inverted`, `window_len_consistent`;
and `bp_available_upstream`.

Five summary checks are asserted in notebook section Z6 and all reproduce: 630,741 total loci;
332,769 matched; 297,972 unmatched; 76,381 distinct exact RTs; 28,838 exact RTs with at least one
matched locus.

---

## 4. The outgroup models — retained, and why

`OutgroupA` and `OutgroupB` are two of the 21 covariance models. They contribute **22 % of distinct
RNA sequences but only 3.7 % of calls**, which looks alarming and prompted an earlier
recommendation in this project to exclude them. **That recommendation was wrong and has been
withdrawn.** It was made from the model's name, never from its placements.

Tested on the placements (`tables/Z4_outgroup_vs_rest.tsv`, notebook section **Z4**):

| | outgroup (2) | other (19) |
|---|---|---|
| upstream | 93.05 % | 94.60 % |
| same strand | 99.32 % | 99.14 % |
| no intervening CDS | **99.17 %** | 94.27 % |
| median \|gap\| | **27 bp** | 55 bp |

Outgroup-model calls sit in canonical retron architecture — as often upstream, as often
same-strand, *more* often with no intervening gene, and *closer* to the RT. The name records which
model matched, not a verdict on the hit. Excluding them would discard **4,156 pairs** from T3 on a
label.

What the 22 %/3.7 % disparity *does* require: any count of **distinct RNA sequences** must state
which models it includes.

---

## 5. Splitting — read this before any train/test split

**The honest split needs clustering, which has not been run.** Until then:

Grouping keys, coarsest first: `source_database` (8) → `tax_species` (10,370, *within one taxonomy
system only*) → `physical_locus_key` (297,608) → `genome_id_norm` (323,024) → `rt_seq_hash`
(28,838).

Three hazards, in order of how badly they bite:

1. **`rt_seq_hash` is the leakiest key.** Exact sequences are strain-level variants: *E. coli*
   alone carries 6,628 distinct exact Retron RT sequences across 82,695 genomes. Splitting on it
   puts near-identical proteins on both sides.
2. **Never split on `tax_species` across taxonomy systems.** NCBI resolves 4,388 species here,
   GTDB 7,596 — different granularity, not poolable. **10,452 genomes appear under both systems,
   8,882 of them under different species names**, so those land on both sides of the split.
3. **`genome_id_norm` is not safe either** — 323,024 genomes against 297,608 physical loci,
   because one locus is republished under several genome accessions.

For recurrence, **use the registered view** `rt_ncrna_exact_pair_recurrence_v1`, never a recount
from taxonomy fields. I verified all 5,056 of its `multiple_species` pairs genuinely span more than
one genome. A naive species-based recount scores 2,760 T3 pairs as cross-species when they sit in
one genome named differently by the two systems.

---

## 6. How to pull the data

Inputs are read-only parquet. Query with DuckDB; never materialise `rt_records_v1` or
`rt_window_cds_v1` whole.

```python
import duckdb
D = '/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/'
c = duckdb.connect()
c.execute(f"CREATE VIEW p AS SELECT * FROM read_parquet('{D}rt_ncrna_pairs_v1.parquet')")

T3 = ("canonical AND file_label = 'Retron' AND same_strand "
      "AND direction <> 'downstream' AND n_cds_between = 0 "
      "AND abs(signed_distance_bp) <= 200 AND evalue <= 1e-5")

pairs = c.execute(f"""
    SELECT DISTINCT rt_seq_hash, nc_seq_hash, detection_model
    FROM p WHERE {T3}""").df()            # 23,680 rows
```

Useful joins: `rt_family_baseline_v1` on `rt_seq_hash` (`family_label`, `completeness_class`) ·
`rt_exact_v1` on `rt_seq_hash` (`rt_aa_len`, `rt_seq` — don't select `rt_seq` unless needed) ·
`ncrna_family_baseline_v1` on `nc_seq_hash` · `rt_ncrna_exact_pair_recurrence_v1` on the pair ·
`rt_tool_calls_v1` on `record_key` (stratification only).

`rt_ncrna_calls_v1` has **no** RT join keys — use `rt_ncrna_pairs_v1`, which already carries them.

**No ncRNA sequences exist in the derived layer** — only `nc_seq_hash` and `nc_seq_len`. Exporting
an ncRNA FASTA from the raw corpus is a prerequisite for ncRNA clustering. RT clustering is
unblocked: `rt_exact_v1.faa`, 501,561 sequences, ready for mmseqs.

## 7. Rebuilding the notebook

The notebook is **generated**. Edit `scripts/build_nb_part*.py`, never the `.ipynb`.
Never read the `.ipynb` into context — it is ~4 MB, mostly base64.

```bash
cd ARIS_OUTPUT/dbchar_workbench
export JUPYTER_PATH=$PWD/.venv/share/jupyter MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar
.venv/bin/python scripts/build_nb.py database_characterization_workbench.ipynb
.venv/bin/python -m nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=2400 --ExecutePreprocessor.kernel_name=dbchar-workbench \
  database_characterization_workbench.ipynb
.venv/bin/python scripts/check_tex_figures.py    # 13/13 resolve
.venv/bin/python scripts/check_tex_numbers.py    # 92/92 numbers match tables/
```

Sections relevant here: **Z0** registry · **Z1** tiers and topology · **Z2** tool table and domain
redundancy · **Z3** exact-sequence grain · **Z4** outgroup test · **F0–F3** pairing · **D1–D6**
geometry · **N8** funnel.

`playground/melissa_playground.ipynb` is the editable copy; launch it with `DBCHAR_OUT=$PWD/playground`
set, and confirm the setup cell prints `(REDIRECTED via DBCHAR_OUT)`.

## 8. Open, and honest

- **Sequence clustering has not been run**, either side. Every distinctness and topology count is
  an upper bound. This blocks the true pairing topology, any saturation or richness estimate, and
  any defensible train/test split.
- **No phylum harmonisation** across GTDB vintages; NCBI carries no phylum at all.
- **No functional annotation of RT neighbours exists** — all 41.3 M neighbouring CDS have
  `has_sequence = False`. Neighbourhood *architecture* is available; neighbourhood *identity* is not.
- One `% CITATION NEEDED` remains in the chapter (line ~131), on "retron types in the order of ten"
  in *E. coli*.
