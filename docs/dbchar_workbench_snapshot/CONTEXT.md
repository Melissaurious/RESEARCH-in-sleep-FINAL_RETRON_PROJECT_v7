# CONTEXT — Stage-1 database-characterization workbench

**Status:** exploratory workbench. **Not** a governed gate. It does not rewrite, supersede or
re-derive the landed `dbchar_g1`…`dbchar_g7` bundles. Everything produced here lives under
`ARIS_OUTPUT/dbchar_workbench/` and is disposable until an operator decision promotes it.

**Worktree:** `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-dbchar-workbench`
(branch `dbchar-workbench`). The main worktree is not modified.

**Authority order** (highest first):
1. `docs/decisions/2026-09-15_stage1_population_rules.md` — population rules.
2. `results/dbchar_g7_stage1_report/` — Stage-1 report + `tables/g7_resolved_values.tsv`
   (the resolved-value table is the canonical number registry; every value in it names the
   producing bundle, table, selector and column).
3. `results/dbchar_g2_canonical_units/VIEWS.md` — view/grain and eligibility contract.
4. `results/dbchar_g1…g6/` bundles — the per-gate tables.
5. `results/dbchar_g7b_stage1_extended_report/` — **later exploratory synthesis**. Useful, but
   **not authority** where it disagrees with g1–g7.

Corpus identity pin (record-manifest sha256):
`8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00`
— 43 JSONL files, 81,007,695,609 bytes, 3,358,182 records, zero parse failures.

---

## 1. Canonical analytical units and denominators

A count is meaningless without its unit. The conversion between units is **not** a constant
(loci per exact RT ranges 1.11–5.49 across source databases), so a raw-record rate and a
locus rate describe different populations.

| view (VIEWS.md) | unit | key | Stage-1 size | honest for | NOT honest for |
|---|---|---|---|---|---|
| `V-REC` | raw record | `record_key` | 3,059,700 | provenance, per-file/per-database composition as mined | any biological rate (double-counts loci mined twice) |
| `V-REC-DISTINCT` | distinct raw record | `is_first_copy` | 3,051,238 | as above, minus byte-identical duplicate lines | as above |
| `V-LOC` | genomic locus | `locus_key` | 2,847,312 | per-locus architecture, contig context | counts a RefSeq/GenBank twin as two loci |
| `V-LOC-PHYS` | physical locus | `physical_locus_key` | 2,475,684 | locus counts corrected for twin publication | collapsing only *supported* where `collapse_supported` |
| `V-RT` | exact RT protein | `rt_seq_hash` | 501,561 | sequence diversity, family composition of proteins | genomic frequency |
| `V-RT-TAXOCC` | RT taxonomic occurrence | `(rt_seq_hash, genome_id_norm)` | 2,737,189 | taxonomic spread of a protein | sequence diversity |
| `V-WIN` | extracted window | `window_dna_sha256` | — | identical-context detection (asymmetric) | context *difference* |
| `V-NCRNA-CALL` | ncRNA call | call row | 346,722 | call-level QC, model composition | pair counting |
| `V-PAIR-PLACEMENT` | one placement | `(locus, RT, ncRNA call)` | 346,722 all / 344,154 canonical | geometry as observed | deduplicated biology |
| `V-PAIR-KEY` | exact RT–ncRNA pair | `(rt_seq_hash, nc_seq_hash)` | 30,924 | pair-level association | placement frequency |

Additional strata (`dbchar_g4`): `V-RT-SINGLE` 493,956 exact RTs · `V-RT-MULTI` 7,593 ·
`V-RT-CROSS` 12 (exact RT proteins seen under more than one family label).

Genomes: 1,542,433. Source databases: 8 (`ncbi_bacteria`, `gtdb_bacteria`, `mgnify_human_gut`,
`gem`, `mgnify_soil`, `mgnify_marine`, `ncbi_archaea`, `gtdb_archaea`).

### Binding population rules (decision 2026-09-15)

- **Rule 1 — ncRNA-anchor-only records are outside the RT analytical population.** The 298,482
  `master_ncRNA-anchored_merged.jsonl` records enter **no** RT denominator. They are *already
  absent* from `rt_records_v1.parquet`, which holds 3,059,700 rows over 42 RT-anchored files
  (3,050,688 `POP-RT-FAM` + 9,012 `POP-RT-MULTI`). To analyse them you must go back to the raw
  corpus under an explicitly declared separate denominator.
- **Rule 2 — MULTI is its own stratum.** 9,012 records / 7,593 exact RTs. Never appended to a
  single family. 20 further multi-label records sit inside single-family files
  (`multilabel == True`, 9,032 records total); they must not be counted in two families at once.
- **Rule 3 — RT-anchored records lacking an RT CDS are classified, never dropped.** 31,504 such
  records are resolved in `dbchar_g2b` into `RECOVERED` 14,188 / `SEQUENCE_ONLY` 16,688 /
  `ILL_POSED` 628. Ineligible records keep their flags; every analysis must report the
  denominator effect of its eligibility rule.

### The house analytical population — TWO TIERS (operator 2026-09-16, revised after review)

Geometry eligibility is right for context analyses and wrong for sequence-only analyses, so the
population is two-tiered:

```sql
POP_RT_SEQ = is_first_copy AND file_label <> 'MULTI' AND NOT multilabel AND elig_exact_rt
POP_RT_CTX = POP_RT_SEQ AND elig_geometry          -- aliased POP_RT in the notebook
```

| tier | use for | records | loci | physical loci | exact RTs | genomes |
|---|---|---|---|---|---|---|
| `POP_RT_SEQ` | family, length, completeness, diversity, clustering | 3,042,216 | 2,838,761 | 2,467,291 | **493,964** | 1,540,869 |
| `POP_RT_CTX` | geometry, ncRNA placement, locus architecture | 3,026,000 | 2,822,547 | 2,451,078 | **477,956** | 1,535,827 |

**16,008 exact RT proteins are usable as sequences but have no defensible genomic context** — they
belong in `POP_RT_SEQ` and not in `POP_RT_CTX`. Cost of `POP_RT_CTX`: 33,700 records (1.10 %) —
8,462 duplicate lines, 9,022 MULTI/multilabel, 16,216 geometry-ineligible.

`elig_geometry` is exactly the operator's "ill-posed + off-contig" exclusion: the g2b recovery
states map onto it one-to-one (`RECOVERED` 14,188 → True; `SEQUENCE_ONLY` 16,688 and `ILL_POSED`
628 → False). This is asserted in the notebook, not assumed.

**Not excluded:** contig clipping (`true_start_clipped` 1,249,012 · `clipped_end_flag` 1,270,225,
~41 % of the corpus each) is a **stratification** flag — those RTs are verified, only the window is
truncated. Partial ORFs and atypical geometry likewise stay in.

**A1–A3 do not apply `POP_RT`** — they reproduce the canonical g2 ladder and must not be compared
against the numbers above. Draft decision record: `notes/2026-09-16_house_population_DRAFT_DECISION.md`
(not yet promoted to `docs/decisions/`).

### Eligibility predicates — flags, not filters

`elig_exact_rt` (well-formed protein) · `elig_rt_coords` (RT interval verified against window DNA
by back-translation) · `elig_geometry` (`elig_rt_coords` + self-consistent window) ·
`elig_rt_length` · `elig_rt_completeness`.

At record level in `rt_records_v1`: `elig_exact_rt` 3,059,700 (all); `elig_rt_coords` =
`elig_geometry` = `elig_rt_completeness` = 3,042,279 (17,421 ineligible). `dbchar_g2` reports
**99.47 % geometry-eligible on `POP-RT-FAM`**; the all-RT figure including MULTI is 99.43 %.
Always state which of the two you used.

---

## 2. Dataset inventory

Canonical derived datasets live in the **main** worktree and are **READ-ONLY**:

`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/`

| file | rows | grain / primary key | notes |
|---|---|---|---|
| `rt_records_v1.parquet` | 3,059,700 | raw RT-anchored record (`record_key`) | 114 columns; 1,114 row groups — **always project columns and push filters down** |
| `rt_loci_v1.parquet` | 2,847,312 | `locus_key` | per-locus rollup; `rt_hash_conflict`, `is_refseq_genbank_twin`, `n_ncrna_min/max` |
| `rt_physical_loci_v1.parquet` | 2,475,684 | `physical_locus_key` | `twin_evidence_class`, `collapse_supported` |
| `rt_exact_v1.parquet` | 501,561 | `rt_seq_hash` | carries `rt_seq` (full protein) — do not select it unless needed |
| `rt_exact_v1.faa` | 501,561 seqs | `rt_seq_hash` | 230 MB FASTA |
| `rt_ncrna_calls_v1.parquet` | 346,722 | ncRNA call (`source_file`,`line_no`,`ncrna_idx`) | call-level, *no* RT join keys |
| `rt_ncrna_pairs_v1.parquet` | 346,722 | placement | calls **joined to their RT locus**; the geometry workhorse |
| `rt_window_cds_v1.parquet` | 44,310,231 | CDS in window (`source_file`,`line_no`,`cds_idx`) | **the big one** — never load whole; aggregate in DuckDB |
| `rt_cds_recovery_v1.parquet` | 31,504 | record | the RT-CDS-less population only |
| `rt_ncrna_exact_pairs_v1.parquet` | 30,924 | `(rt_seq_hash, nc_seq_hash)` | geometry summary per exact pair |
| `rt_ncrna_exact_pair_recurrence_v1.parquet` | 30,924 | `(rt_seq_hash, nc_seq_hash)` | `recurrence_class` |
| `rt_ncrna_nonretron_candidates_v1.parquet` | 266 | placement | retron-CM calls beside non-Retron RTs |
| `rt_family_baseline_v1.parquet` | 501,561 | `rt_seq_hash` | `family_label`, `completeness_class`, `view` |
| `ncrna_family_baseline_v1.parquet` | 16,458 | `nc_seq_hash` | exact ncRNA sequences, `detection_model`, `n_models` |
| `multi_hmm_evidence_v1.parquet` | 7,593 | `rt_seq_hash` (MULTI) | HMM best/second score + `margin_bits` |
| `rt_tool_calls_v1.parquet` | 3,051,238 | distinct record (`record_key`) | `by_myRT`/`by_PADLOC`/`by_DefenseFinder`, `detected_by_set`, `n_ncrna` |

---

## 3. Useful joins and keys

| from → to | key | caution |
|---|---|---|
| records → loci | `locus_key` | many records per locus |
| loci → physical loci | `physical_locus_key` | collapse only supported where `collapse_supported` |
| records / loci / family baseline / exact → exact RT | `rt_seq_hash` | one protein spans many loci |
| records → CDS | `(source_file, line_no)` | 44 M rows; aggregate first |
| records → ncRNA calls | `(source_file, line_no)` [+ `ncrna_idx`] | `rt_ncrna_calls_v1` has **no** `record_key`/`rt_seq_hash`; use `rt_ncrna_pairs_v1` instead, which already carries them |
| pairs → exact pair | `(rt_seq_hash, nc_seq_hash)` | placement → pair is many-to-one |
| exact ncRNA → ncRNA baseline | `nc_seq_hash` | |
| records → tool calls | `record_key` | `rt_tool_calls_v1` is the **distinct-record** population (3,051,238), i.e. `is_first_copy` |
| MULTI exact RT → HMM evidence | `rt_seq_hash` | MULTI stratum only |
| records → taxonomy | in-row `tax_*` + `taxonomy_system` | schemas are **not** interchangeable — see §6 |

**Exact-pair view basis — do not conflate.** `rt_ncrna_exact_pairs_v1` (**30,924** pairs, 29,192
exact RTs, 16,458 exact ncRNAs) is built on the **ELIGIBLE** placement population (345,313), not the
**CANONICAL** one (344,154). Only **30,427** pairs are derivable from canonical placements; the
other **497 are represented solely by placements removed during de-duplication**. Use the registered
30,924 for pair topology (matches g3), the canonical-derived 30,427 for geometry composition, and
never quote one while citing the other. Notebook section F0.

**ncRNA model labels.** Every exact ncRNA sequence is hit by **exactly one** covariance model
(`n_models > 1` for 0 of 16,458), so per-model counts partition the 16,458 and the representative-
model (C2) and call-level (C3) labels are interchangeable. *(An earlier version of this file stated
the opposite; that was wrong.)*

**Source-database attribution.** Per-database counts are **coverage, not shares**: 200,914 `POP_RT`
loci sit under both `ncbi_bacteria` and `gtdb_bacteria` (GTDB is a curated re-derivation of the
same assemblies), 111,394 genomes appear under two databases, and **~45 % of exact RT proteins
occur in ≥2 databases**. Rules: report coverage per database; when a *share* is needed, compute it
at the locus or genome rung under the declared primary-source rule (curated GTDB wins over NCBI —
this partitions exactly to 2,822,547 loci) and show what the rule moved; **never** compute a
database share on exact RTs. Notebook section A4.

`record_key` = `source_file:line_no`. `locus_key` is a coordinate interval on a **contig
accession**: two assembly versions of one contig are two loci; `physical_locus_key` normalises
the `NZ_` spelling.

---

## 4. Main Stage-1 findings (the numbers a new analysis must not contradict)

Every value below is in `results/dbchar_g7_stage1_report/tables/g7_resolved_values.tsv`
with its producing bundle/table/selector — **load it, do not retype it**.

- **Corpus / units.** 3,059,700 raw → 3,051,238 distinct → 2,847,312 loci → 2,475,684 physical
  loci → 501,561 exact RTs, over 1,542,433 genomes / 2,737,189 taxonomic occurrences.
  371,628 RefSeq/GenBank twin pairs, **all** collapse-supported, zero disagreements.
  0 loci carry conflicting RT sequences; 203,921 loci appear under >1 source database.
- **RT integrity.** 2,532,006 records back-translate exactly, 618 mismatch; 99.47 % of
  `POP-RT-FAM` geometry-eligible. Of the RT-CDS-less population: 14,188 recovered,
  16,688 sequence-only (9,128 of them wholly beyond the contig retrieved), 628 ill-posed.
- **RT↔ncRNA geometry (priority output).** 346,722 placements → 344,154 canonical.
  Upstream 325,269 / downstream 6,761 / overlapping 12,124; median upstream gap −55 bp;
  same strand **99.12 %** (`g3_same_strand.tsv`: 341,113 / 344,154 — the g7 REPORT.md prose says
  99.8 %, which is an unregistered hard-coded literal; see §5 artefact 9); no intervening CDS
  94.41 % (1 CDS 3.61 %, >3 CDS 1.55 %).
  Exact-pair view: 30,924 pairs, 12,079 strictly 1:1 components.
- **Families.** `V-RT-SINGLE` 493,956 / `V-RT-MULTI` 7,593 / `V-RT-CROSS` 12. Median RT length:
  RVT-GII 407 aa, Retron 342 aa. 36 of 44 prior-project family length baselines reproduced exactly.
- **MULTI.** Best-scoring HMM family is among the record's own labels for 99.91 % of MULTI
  proteins; median best-vs-second margin 5 bits vs 81.7 bits in a seeded control whose best hit
  matches the known label 98.10 % of the time. → **ambiguity stratum, not mislabelling.**
- **Metadata / taxonomy.** Catalogue joins resolve (ncbi_bacteria 100.00 %), but the NCBI
  summaries carry **no completeness column**; phylum coverage 100.00 % under GTDB, 0.00 % under
  NCBI *by construction*. Redundancy correction moves the distribution hard: *E. coli* 19.97 % of
  NCBI records → 6.09 % of exact RTs; top-10 species 66.21 % of records → 18.95 % of exact RTs.
- **Tools.** On Retron records: myRT 92.77 %, PADLOC 68.37 %, DefenseFinder 67.71 %, all three
  53.17 %. Where both tools wrote a subtype (365,708 records) they agree on 160,381.
  ncRNA carriage is 89.23 % for myRT+PADLOC vs 13.50 % for myRT alone.

---

## 5. Known artefacts — do NOT interpret biologically

1. **The downstream-distance mode (median 2,682 bp) — define it precisely.** *All* canonical
   downstream placements are **6,761 over 230 distinct ncRNA sequences**. *The mode* is the subset
   within ±150 bp of the median: **5,234 placements over 18 distinct ncRNA sequences**, 99.96 % of
   its dominant stratum contig-start-clipped: the window begins at
   the contig start, so any call is *forced* downstream. Labelled a **technical mode**. Never use
   it as a prior; if you plot signed distance, stratify by `true_start_clipped` /
   `clipped_end_flag`. Stratifying also reveals **1,041 downstream placements that are NOT
   contig-start-clipped, at a median of 64 bp over 149 distinct ncRNA sequences** — a near-range
   population the artefact does not explain.
2. **The shipped `position_relative_to_rt` field.** Null on 331,897 placements and matching no
   coordinate frame — the best of twelve candidate frames reproduces 146 values. It behaves as
   −(RT offset into the window) + the ncRNA's intergenic-region index, i.e. an index minus a
   coordinate. **Retained as provenance only.** Canonical geometry is the coordinate-derived
   `direction` / `signed_distance_bp` / `same_strand` / `n_cds_between` in `rt_ncrna_pairs_v1`.
3. **Zero-ncRNA rates outside Retron.** The covariance models *are* retron models. Zero-ncRNA is
   47.23 % for Retron loci and 99.99 % for RVT-GII: outside Retron this measures **detector
   scope**, never biological absence.
4. **Tool intersections are not independent corroboration.** myRT / PADLOC / DefenseFinder share
   model lineage, and *"tool absent from a record"* cannot be distinguished from *"tool never run
   on that genome"*. Any ncRNA-carriage difference across tool sets is a **detector-definition
   effect first**; biology only after that is excluded.
5. **Join rates are descriptions, not tests.** A corpus whose genome ids were harvested from these
   catalogues resolves into them by construction.
6. **"Verified" means two fields of one record agree.** Where the pipeline wrote both from the
   same wrong place, they agree and are still wrong.
7. **The 266 retron-CM / non-Retron-RT placements** are a retained **candidate** population, not
   novel retrons. (260 of the 266 are single-family non-Retron; 6 are MULTI. The report's "260"
   is the single-family eligible subset — quote the right one.)
8. **The "99.8 % same strand" figure in the g7 report prose is wrong.** The gate table
   `g3_same_strand.tsv` gives **99.116 %** on `CANONICAL` placements (341,113 same / 3,041
   opposite of 344,154), and recomputation from `rt_ncrna_pairs_v1` reproduces the gate table
   exactly. The `99.8%` string is a hard-coded literal in
   `dbchar_g7_stage1_report/scripts/findings.py:190` — every other number in that sentence is a
   resolved placeholder, and there is no `same_strand` key in `g7_resolved_values.tsv`. Use the
   gate table. Full write-up: `notes/2026-09-16_same_strand_discrepancy.md`. **Open for the
   operator**: whether to correct the report by a new record and whether to register the key.
9. **Raw taxonomic representation ≠ enrichment.** Sequencing effort dominates record counts. Any
   over/under-representation statement needs an explicit normalisation and denominator.

---

## 6. QC / eligibility / exceptional populations to keep visible

- `bt_status` ∈ {exact, mismatch, …}; `bt_n_diff`.
- Window pathologies: `window_inverted`, `window_len_consistent`, `clipped_end_flag`,
  `true_start_clipped`, `rt_at_window_edge`, `rt_in_window`.
- `rt_cds_recovery_v1.representation_class`: `rt_inside_window` 14,816 ·
  `rt_beyond_a_contig_end_clipped_window` 9,128 · `window_inverted_no_sequence_retrieved` 3,924 ·
  `rt_crosses_a_contig_end_clipped_window` 3,636.
- Placement `multiplicity_class`: `single_call` 321,562 ·
  `same_call_from_another_record_of_the_same_locus` 24,770 ·
  `duplicate_call_within_one_record` 192 · `distinct_sequences` 174 ·
  `same_sequence_other_coordinates` 24.
- Geometry-ineligible placements (2,568 non-canonical): `byte_identical_duplicate_line` 1,303 ·
  `rt_partially_outside_window` 41 · `rt_outside_window` 37 · `mismatch` 28. (1,159 are
  geometry-eligible but non-canonical, i.e. removed by placement de-duplication, not by QC.)
- Atypical-geometry catalogue: `results/dbchar_g3_pair_geometry/tables/g3_atypical_catalogue.tsv`
  (overlapping-the-RT 12,259; >5 kb 557; opposite strand 3,095; >2 CDS between 5,903;
  window clipped at contig end 57,571; true-start-clipped 59,510 — denominator 345,313 eligible).
- `completeness_class` over exact RTs: `all_complete` 342,256 · `all_partial` 127,473 ·
  `mixed_or_codon_evidence` 31,832.
- Taxonomy schema split: `ncbi` 2,267,726 records · `gtdb` 769,698 · `unknown` 22,276. NCBI rows
  have **no** phylum. Report per schema; never pool NCBI and GTDB ranks.

---

## 7. Canonical vs exploratory — the rule for this workbench

- A number that exists in `g7_resolved_values.tsv` is **canonical**: load it from there.
- A number recomputed here from `data/derived/` that *matches* the canonical value is a
  reproduction — fine, and worth asserting explicitly.
- A number recomputed here that *differs* is a **finding about the workbench**, not about the
  database, until the definition difference is located. Say so in the notebook.
- Anything genuinely new (a cross-gate combination, a new stratification, a new plot) is
  **exploratory**, is labelled as such, and acquires no authority by being in a notebook. It
  becomes a claim only through a landed bundle / operator decision.
- `dbchar_g7b_stage1_extended_report` is in the exploratory tier too.

## 8. Workbench conventions

- Compute engine: **DuckDB** over the parquet files (column projection + predicate pushdown).
  Never `read_parquet(...).to_pandas()` on `rt_records_v1` or `rt_window_cds_v1` in full.
- Every aggregate is cached as a TSV under `tables/`; plots are drawn **from those TSVs**.
- Every section declares: scientific question · analytical unit · denominator · datasets/columns.
- Cells are independently rerunnable: each re-opens its own DuckDB connection through the shared
  `Q()` helper and re-reads cached tables from disk.
- Python: `ARIS_OUTPUT/dbchar_workbench/.venv` — a `--system-site-packages` overlay on
  `retron_tradicional` adding matplotlib / matplotlib-venn / duckdb. The governed env is
  **not** modified. Recreate with:
  `/home/borg/miniconda3/envs/retron_tradicional/bin/python -m venv --system-site-packages ARIS_OUTPUT/dbchar_workbench/.venv && ARIS_OUTPUT/dbchar_workbench/.venv/bin/pip install matplotlib matplotlib-venn duckdb ipykernel`
