# Plan — one population registry, and the figure set that follows from it

Status 2026-09-17. Sections 1–3 are **implemented**; section 4 is the build queue.

---

## 1. The registry (implemented — notebook section 0.2 / Z0)

`tables/Z0_population_registry.tsv`, computed from parquet on every build. Eighteen rows:

| id | unit | n | honest for | not honest for |
|---|---|---|---|---|
| `REC-ALL` | raw record | 3,059,700 | provenance, per-file composition | any biological rate |
| `REC-DIST` | distinct record | 3,051,238 | as above, minus duplicate lines | any biological rate |
| `LOC` | accession-defined locus | 2,847,312 | per-locus architecture | counts a RefSeq/GenBank twin twice |
| `PLOC` | physical locus | 2,475,684 | locus counts after twin collapse | collapse only where supported |
| `GEN` | genome identifier | 1,542,433 | taxonomic breadth | genome-level prevalence |
| `RT-BASE` | exact RT protein | 501,561 | the full exact-sequence baseline | any `POP_RT`-filtered statement |
| `RT-BASE-1F` | exact RT protein | 493,956 | family composition of the baseline | the record-filtered population |
| `RT-MULTI` | exact RT protein | 7,593 | the multi-label stratum alone | never appended to a family |
| `RT-CROSS` | exact RT protein | 12 | proteins under >1 single-family label | family denominators |
| `RT-SEQ` | exact RT protein | 493,964 | family, length, completeness, diversity | geometry |
| `RT-CTX` | exact RT protein | 477,956 | geometry, placement, architecture | sequence diversity |
| `PL-ALL` | placement | 346,722 | call-level QC | geometry |
| `PL-ELIG` | eligible placement | 345,313 | geometry before de-duplication | counting distinct biology |
| `PL-CANON` | eligible, non-redundant placement | 344,154 | **all geometry in the chapter** | raw call frequency |
| `NC-ALL` | exact ncRNA sequence | 16,466 | the sequence set as called | pairing with eligible placements |
| `NC-ELIG` | exact ncRNA sequence | 16,458 | the ncRNA side of the pair view | call-level composition |
| `PAIR-ELIG` | exact RT–ncRNA pair | 30,924 | pair topology; matches `rt_ncrna_exact_pairs_v1` | geometry composition |
| `PAIR-CANON` | exact RT–ncRNA pair | 30,427 | **the funnel and geometry composition** | pair topology |

Five guard rails run beside it and print `OK`/`BAD` on every execution — including the one the
draft got backwards:

```
[OK ] RT-BASE-1F + RT-MULTI + RT-CROSS == RT-BASE  (493,956 + 7,593 + 12 = 501,561)
[OK ] RT-SEQ = 493,952 single-family + 12 cross-labelled = 493,964  -- contains 0 MULTI proteins
[OK ] PL-ALL 346,722 >= PL-ELIG 345,313 >= PL-CANON 344,154
[OK ] PAIR-ELIG 30,924 - PAIR-CANON 30,427 = 497 pairs carried only by de-duplicated placements
[OK ] NC-ALL 16,466 vs NC-ELIG 16,458  -- PL-ALL pairs with NC-ALL, never with NC-ELIG
```

**In the thesis**, the registry is Table 1 (extend the existing `tab:units`, which is six of these
rows), and **every figure caption ends with its population id and n**. That is the whole
reader-facing fix: a caption that names its population cannot collide with one that names another.

---

## 2. The six collisions, and how each is now closed

| # | collision | closed by |
|---|---|---|
| 1 | three funnels: L7 cascade / N8 / K2 | L7 and K2 now print a `WHICH FUNNEL IS THIS?` block naming all three and their step-4 values (26,293 / 29,440 / 26,805). **N8 is the chapter's**; L7 → supplementary as "alternative rule, overlaps excluded"; K2 → supplementary as "one-at-a-time sensitivity". Delete `tab:dbchar:cascade` from the chapter — it is never `\ref`d. |
| 2 | 30,924 vs 30,427 | `F0_pair_view_basis` now declares `pop=["PAIR-ELIG","PAIR-CANON"]` and its print is computed, not hard-coded. **Put F0 in the chapter** as a four-row inset at the head of §pairs. |
| 3 | 94.51 % twice | N5 re-based from `PL-ELIG` onto `PL-CANON`. The false coincidence is gone: Retron-only is now **94.54 %** (n = 343,892) against **94.51 %** for all canonical placements (n = 344,154). Quote both, or quote one and say which. |
| 4 | two 266s | the overlap class is renamed **"ncRNA fully enclosed by a CDS"** and the cell prints an explicit warning that it is not the 266 retron-CM calls at non-Retron loci. |
| 5 | 203,921 vs 203,448 | new table `A4_multi_database_loci_by_population` emits both rows: `LOC (whole corpus)` 203,921 and `RT-CTX (POP_RT loci)` 203,448. |
| 6 | two tool tables | `N1_tool_sets` **no longer carries any protein column**. The protein axis exists only in `N1_tool_sets_protein` (78,287, a true partition). The record table summed to 84,032 and existed only to be misquoted. |

---

## 3. Supporting material — the table inventory

**Verified correct, quotable as-is (14).** Every number traced into these reproduced exactly:
`A0_pop_rt_units` · `A0_population_cascade` · `A1_unit_ladder` · `D1_direction` · `D1_same_strand` ·
`D2_downstream_strata` · `D3_cds_between` · `D5_opposite_strand_profile` ·
`D5_opposite_strand_composition` · `L1_sequence_only_by_database` · `L3_prodigal_partial_flags` ·
`L4_opposite_strand_independence` · `L7_dataset_rule_cascade` · `N8_dataset_funnel`

**Correct, but the draft mis-reads them (5)** — see `CORRECTIONS_current_thesis_section.md`:
`N3_completeness_length_shift` · `N3_length_by_family_completeness` · `N6_top_taxa` ·
`C1_zero_class_by_family` · `F0_pair_view_basis` · `B1_views` / `N2_family_all`

**Correct but homeless — give these a home (3).**
`L2_cross_label_proteins` (all 12 cross-labelled proteins are `RVT-CRISPR|RVT-CRISPR-like` —
this answers the `\todo` at line 113) · `D6_marginals_by_weighting` (the evidence for the
"coupled, not independent" claim the text asserts without a figure) ·
`F2_component_shapes` (already carries `unit`/`denominator` columns — the model for all of them)

**New (3).** `A4_multi_database_loci_by_population` · `N6_cm_confidence_by_model` ·
`Z0_population_registry` (+ the `_table_populations.tsv` sidecar)

**Still missing (2).** No table separates outgroup from retron covariance models — `OutgroupA`
alone is **3,319 of the 16,458** distinct RNA sequences (20.2 %, the largest single share) and
propagates into the resource unflagged. And no workbench table exists for the MULTI stratum;
its evidence is quoted from the landed `g4` bundle only.

---

## 4. The figure plan

### Chapter set — 11 figures (all resolve; `check_tex_figures.py` reports 11/11)

| # | figure | notebook **plot cell** | population stamp | status |
|---|---|---|---|---|
| 1 | `A1_unit_ladder` | **13** | `REC-ALL` | **promote** — §units currently has no figure |
| 2 | `N2_family_composition_all` | **132** | `RT-BASE-1F` + `RT-SEQ` | keep |
| 3 | `N3_rt_length_by_completeness` | **135** | `RT-BASE-1F` | **fixed** (table was reversed) |
| 4 | `C2_ncrna_length_by_model` | **49** | `NC-ELIG` | keep; flag outgroup models |
| 5 | `N4_family_x_model` | **138** | `PL-CANON` | keep |
| 6 | `N5_architecture_retron_vs_not` | **141** | `PL-CANON` | **re-based** |
| 7 | `D6_joint_geometry` | **78** | `PL-CANON` | **promote** — the "coupled, not independent" claim has no figure |
| 8 | `N8_dataset_funnel` | **151** | `PAIR-CANON` | keep |
| 9 | `N1_tool_venn` | **129** | `RT-BASE-1F` + `REC-DIST` | keep |
| 10 | `N6a_taxa_redundancy` | **144** | `RT-SEQ` | **split out of N6** |
| 11 | `M2_operons_strand_normalised` | **~120** | — | keep, **but add a `\ref`** (currently orphaned) |

Plus `N6b_cm_confidence` (cell **145**, `PL-CANON`), moved to §ncrna beside N4 where the text that
cites it lives. **Demote** `N7_burden_and_cooccurrence` (cell **148**) to supplementary: it is
orphaned in the prose, and proposal F8 says co-occurrence is an extension *after* assembly
deduplication.

### Supplementary — twelve that already exist and need only an S-number

`A2_redundancy_by_database` (17) · `A3_occurrence_distribution` (21) · `A4_database_attribution` (27) ·
`B1_family_composition` (32) · `B3_completeness_by_family` (40) · `C1_ncrna_call_landscape` (45) ·
`C3_model_composition` (53) · `D3_cds_and_strand` (64) · `D5_strand_agreement` (73) ·
`F_pairing_topology` (89) · `L_dataset_rule_and_multiplicity` (114) · `M3_operons_minimal` (~123)

### To build — six, in priority order

| new | what it shows | why | notebook home |
|---|---|---|---|
| **S1** MULTI margins | best-vs-second bit margin, MULTI vs seeded control | §families claims median 5 vs 81.7 bits with **no workbench table and no figure** | **section G scaffold, cell 92** |
| **S2** cross-labelled 12 | the 12 proteins, lengths, label sets | answers the `\todo` at line 113; `L2` already computed | section G, cell 92 |
| **S3** outgroup separation | calls and distinct sequences, retron models vs `OutgroupA`/`OutgroupB` | 20.2 % of distinct RNAs come from an outgroup model | **C3, cells 52–53** |
| **S4** RT length ECDF | length by family, no KDE | the shape figure to use instead of violins; `g7b/fig08` is the precedent | **B2, cells 35–36** |
| **S5** geometry schematic | direction / strand / gap / overlap, drawn not measured | proposal F5; readers cannot parse the `signed_distance_bp` sign convention without it | **M section, cell 116+** |
| **S6** locus gallery | one example each: adjacent, overlapping, near-downstream, distant, opposite-strand, non-Retron | proposal F5; M2 machinery needs only a different selector | **M3, cell 123** |

Blocked until sequence clustering: cluster-level pairing topology, the distinctness claim, any
train/test split. Blocked until phylum harmonisation: any phylum figure.

---

## 5. Working in the notebook

Cells are strictly paired — an **odd cell caches**, the **next plots from the cache**. To restyle,
edit only the plot cell; it reads the TSV and is instant. Indices above are for the 152-cell build
of 2026-09-17 and shift as soon as cells are added, so **navigate by the markdown heading**.

`playground/melissa_playground.ipynb` is the editable copy. Launch it with the isolation switch:

```bash
cd ARIS_OUTPUT/dbchar_workbench
export JUPYTER_PATH=$PWD/.venv/share/jupyter MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar
export DBCHAR_OUT=$PWD/playground
.venv/bin/python -m jupyter lab playground/melissa_playground.ipynb
```

The setup cell must print `(REDIRECTED via DBCHAR_OUT)`. If it says `(canonical)`, stop — you would
overwrite the figures the chapter points at.

To add a population to a new table or figure:

```python
df  = cache("X1_my_table", "SELECT ...", pop="PL-CANON")
savefig(fig, "X1_my_figure", pop="PL-CANON")      # or pop=["A","B"] when a figure spans two
```

`pop_stamp("PL-CANON")` returns the caption string on its own if you want it in prose.

---

## 6. Statistics to add, and what not to add

- **`n` is missing from most plot axes.** It is in N3's side table and nowhere else. Every
  distribution panel should carry its n on the axis label.
- **No dispersion on the pair and geometry claims** — point estimates only.
- **Do not add significance tests.** At n = 344,154 every comparison is p < 10⁻³⁰⁰ and the p-value
  carries no information. Where a difference needs quantifying (opposite- vs same-strand
  separation, say), report the **difference in medians with a bootstrap CI**, or a rank-based
  effect size (Cliff's δ), and state that tests are omitted because the denominators make them
  uninformative.
- **Box, not violin.** n ranges from 11 to 256,624, so KDE bandwidth is not comparable across
  rows; the distributions are hard-bounded below and heavy-tailed right, so a violin invents
  density below the minimum; and the bimodality that matters (complete vs partial) is already
  resolved by stratification, which is strictly better than showing it as a lumpy violin. Where
  shape genuinely matters, use an **ECDF** (S4) — exact, no bandwidth, overlays many families.
- **The Venn belongs on distinct proteins**, as it already is. Clustering will shrink every cell
  non-uniformly — myRT-only proteins are enriched in metagenomes where near-identical variants
  proliferate — so the 29,436 > 20,203 finding is the one most likely to move. State it as an
  upper bound now; re-run after clustering. Do not hold the figure back.
