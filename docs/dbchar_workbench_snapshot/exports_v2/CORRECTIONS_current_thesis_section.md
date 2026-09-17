# Corrections to `current_thesis_section_content.md`

Line numbers are from the file as of 2026-09-17. Every entry names the table that proves it.
Nothing in the `.md` has been edited — this is the worklist.

**A — confirmed errors.** The claim is wrong and changes what the chapter says.
**B — denominator not stated.** The number is right; the population is missing or mismatched.
**C — structural.** Two correct numbers colliding.

---

## A — confirmed errors

### A1 · line 112–113 · the family split of the sequence population
> "The \num{493,964} distinct RT proteins of the sequence population resolve into \num{486,371}
> single-family proteins across 41 family labels and \num{7,593} multi-labelled proteins and 12
> cross-labelled proteins."

**Wrong.** `POP_RT_SEQ` excludes MULTI by its own definition
(`file_label <> 'MULTI' AND NOT multilabel`), so the 7,593 cannot be subtracted from it. Verified
directly against `rt_records_v1`:

```
RT-SEQ = 493,952 single-family + 12 cross-labelled = 493,964   -- contains 0 MULTI proteins
```

**Replace with:** *"The \num{493964} distinct RT proteins of the sequence population comprise
\num{493952} proteins carrying a single family label across 41 labels, and 12 carrying two. The
\num{7593} multi-labelled proteins are a separate stratum and are not part of this population."*

This also answers the `\todo` at line 111 (500 → 493): the full baseline is `RT-BASE` 501,561;
the sequence population is `RT-SEQ` 493,964; the difference is the MULTI stratum (7,593) plus the
record-level filters, not a quality cut.
**Evidence:** `tables/Z0_population_registry.tsv`, guard-rail print in notebook cell 9.

### A2 · line 150 · RT length on complete calls
> "On complete calls the overall median is 385 amino acids, with Retron at 342 and RVT-GII at 407"

**All three are pooled (all-completeness) medians**, taken from `g4_views.tsv` and
`B2_rt_length_by_family.tsv`. The paragraph's own argument is that pooling understates every
family, so it currently refutes itself. Complete-only values:

| | overall | Retron | RVT-GII |
|---|---|---|---|
| pooled (what the text quotes) | 385 | 342 | 407 |
| **complete calls only** | **420** | **366** | **434** |

**Evidence:** `tables/N3_completeness_length_shift.tsv`, `tables/N3_length_by_family_completeness.tsv`.
The figure was also wrong — its side table was reversed relative to the plot — and is now fixed
and carries a `family` column.

### A3 · line 258–261 · the downstream remainder
> "Once they are set aside, the \num{1,041} remaining downstream placements lie at a median of
> 64~bp"

6,761 − 5,234 = **1,527**, not 1,041. The 1,041 is a *different partition*: downstream placements
that are **not contig-start-clipped**. The mode and the clipping flag are not the same cut.

**Replace with:** *"Of the \num{6761} downstream placements, the \num{1041} that are not truncated
at a contig start lie at a median of 64~bp over 149 distinct sequences."*
**Evidence:** `tables/D2_downstream_strata.tsv`.

### A4 · line 259 · the 99.96 %
> "with 99.96\% of the dominant stratum truncated at the contig start"

99.96 % describes one `ncbi_bacteria`/Retron/`TypeV` stratum, not the mode. **The mode is
99.81 %.** **Evidence:** `tables/D2_downstream_strata.tsv` (`pct_true_start_clipped` = 99.809).

### A5 · line 198 · the worst-affected covariance model
> "one model returns \SI{39.2}{\percent} of its calls above $10^{-5}$"

That is TypeIIIA2 and it is **not the worst**. `TypeIIIA1` returns **52.03 %** of its 1,647 calls
above 1e-5. Since the sentence exists to show the threshold hits models unequally, use the true
maximum. **Evidence:** new table `tables/N6_cm_confidence_by_model.tsv`, plotted in `N6b`.

### A6 · line 202 · the non-Retron carriage ceiling
> "against at or below \SI{0.1}{\percent} for every other family"

**False.** RVT-UG10 carries a call at **0.479 %** of its loci. Use *"below \SI{0.5}{\percent}"*.
**Evidence:** `tables/C1_zero_class_by_family.tsv`.

### A7 · lines 196, 389 · 97.75 %
97.75 % is the sum of the five **rounded** band percentages. Computed from counts it is
**97.74 %** (336,393 of 344,154). **Evidence:** `tables/N6_cm_confidence.tsv`. *(Already corrected
in `exports/thesis/results_database_characterization.tex`.)*

### A8 · line 277 · the non-Retron comparison
> "57.69\% of 260 eligible placements upstream"

N5 has been re-based from `PL-ELIG` onto `PL-CANON` so that the whole architecture subsection uses
one placement population. The non-Retron group is now **256 placements, 57.42 % upstream**.
**Evidence:** `tables/N5_geometry_retron_vs_not.tsv`.

---

## B — denominator not stated

### B1 · line 19 · the species numbers disagree with their own figure
The text quotes the **landed g5 bundle** (all records): *E. coli* 450,012 / 28,018, *S. enterica*
374,314, *K. pneumoniae* 237,525. Figure `fig:taxa` plots the **workbench `RT-SEQ`** values:
449,992 / 27,998 / 374,290 / 237,479. Both are correct; quoting one while pointing at the other is
not. *(The *Lachnospiraceae* pair 7,539 / 16,408 matches both, which is why it hid.)*

**Decide one.** If g5: change the figure to plot all records. If `RT-SEQ` (recommended — it is the
population the rest of §units uses): update the four numbers and add *"counted on the sequence
population"*. **Evidence:** `results/dbchar_g5_metadata_sampling/tables/g5_overrepresentation_species.tsv`
vs `tables/N6_top_taxa.tsv`.

### B2 · line 177–178 · calls and distinct sequences are mis-paired
> "\num{346,722} calls that reduce to \num{16,458} distinct RNA sequences"

346,722 is **all** calls (`PL-ALL`), which reduce to **16,466** (`NC-ALL`). 16,458 is the
**eligible** figure (`NC-ELIG`). Pick one rung and say which.
**Evidence:** `tables/F0_pair_view_basis.tsv`, `tables/Z0_population_registry.tsv`.

### B3 · line 180 · the RNA length regime
Median 151 nt, IQR 131–193 holds over **16,458 distinct eligible sequences**. Over the 346,722
**calls** it is median 158, IQR 141–167. The sentence follows a call count, so it reads as a call
statistic. Add *"over distinct sequences"*. **Recomputed from `rt_ncrna_pairs_v1`.**

### B4 · line 177 · "21 retron covariance models"
Two of the 21 are outgroup models, and **`OutgroupA` alone contributes 3,319 of the 16,458
distinct RNA sequences — 20.2 %, the largest single share.** Calling the library "21 retron
covariance models" and then reporting 16,458 retron RNAs propagates outgroup hits into the
association resource unflagged. Proposal F4 already asks for this distinction; this is why it
matters. **Evidence:** `tables/C3_model_composition.tsv`. *(Figure S3 in the plan.)*

### B5 · line 17 · the multi-database locus count
203,921 is correct **on the whole corpus** (`LOC`). The workbench's `A4_locus_database_sets` gives
203,448 because it runs on `POP_RT_CTX` loci. Name the denominator.
**Evidence:** new table `tables/A4_multi_database_loci_by_population.tsv` (both rows).

---

## C — structural

### C1 · the three funnels
`tab:dbchar:cascade` (L7, cumulative, step 4 = *upstream*, 26,293 pairs) sits six lines from
`tab:funnel` (N8, cumulative, step 4 = *upstream or overlapping*, 29,440 pairs), with no statement
that they differ — and `tab:dbchar:cascade` is **never `\ref`d in the prose**. A third,
`K2_criterion_sensitivity`, is marginal rather than cumulative (26,805).

**Do:** keep N8 in the chapter. Move L7 to supplementary, retitled *"alternative rule in which
overlapping placements are excluded"* — that clause is the entire difference. Move K2 to
supplementary as *"one-criterion-at-a-time sensitivity"*. The notebook now prints a
`WHICH FUNNEL IS THIS?` block in both L7 and K2.

### C2 · 30,924 vs 30,427
§pairs (line 296) is built on `PAIR-ELIG`; §dataset (line 368) on `PAIR-CANON`. Both correct, never
reconciled. **Do:** put `F0_pair_view_basis` in the chapter as a four-row inset at the head of
§pairs, and add one sentence: *"497 pairs are represented solely by placements removed during
de-duplication; pair topology is reported on the registered 30,924, the resource on the
canonical-derived 30,427."*

### C3 · 94.51 % appearing twice
Previously `tab:geometry` (`PL-CANON`, all placements) and Figure N5 (`PL-ELIG`, Retron only) both
rounded to 94.51 %. After the re-base they visibly differ — **94.51 % all canonical** vs
**94.54 % Retron-only** — which is honest. Update line 277 accordingly.

### C4 · two different 266s
Line 250 ("266 lying entirely within a coding sequence") and line 277 (266 retron-CM placements at
non-Retron loci) are unrelated populations of the same size. The overlap class is now named
**"ncRNA fully enclosed by a CDS"** in `N5_overlap_profile`; render the other as *"260 eligible
single-family placements (266 including MULTI)"*.

### C5 · the two tool tables
`N1_tool_sets` used to carry per-row protein counts that summed to 84,032 against a true 78,287,
because a protein spanning two tool sets appeared in both rows. **Those columns have been
deleted.** The chapter already uses the correct table (`N1_tool_sets_protein`); no text change
needed, but never re-add them.

### C6 · do not recount recurrence from species names
Not an error in your draft --- your text correctly uses the registered recurrence classification
--- but a trap for any recount. **\num{2760} of the T3 pairs sit in one genome that NCBI and GTDB
name differently**, so a rule based on `count(distinct tax_species) > 1` scores every one of them
as cross-species recurrence. Distinct `genome_id_norm` is also not safe on its own: one physical
locus is republished under several genome accessions. The landed
`rt_ncrna_exact_pair_recurrence_v1` handles both correctly --- I checked all \num{5056} of its
`multiple_species` pairs and every one genuinely spans more than one genome. **Use the registered
view; never recompute this from taxonomy fields.**

---

## Orphans to resolve while editing

- `fig:burden` (N7) — figure present, **never `\ref`d**. Recommend demoting to supplementary.
- `fig:operons` (M2) — figure present, **never `\ref`d**. Recommend adding a citation in §dataset.
- `tab:dbchar:cascade` — table present, **never `\ref`d**. See C1.
- `tab:crosslabel` — exists in `exports/thesis/results_database_characterization.tex`, **dropped
  entirely from the `.md`**. Its content answers the `\todo` at line 113: all 12 cross-labelled
  proteins are `RVT-CRISPR|RVT-CRISPR-like` (`tables/L2_cross_label_proteins.tsv`).

## Remaining `\todo`s and what answers them

| line | `\todo` | answer |
|---|---|---|
| 73 | "clarify then what will move on onto the datasets" | the two-tier population: 14,188 recovered records enter `RT-CTX`; the 16,688 context-less enter `RT-SEQ` only; the 628 ill-posed enter neither |
| 111 | "add the 500K, explain why 500 → 493" | A1 above |
| 113 | "present them and under which family group they stayed" | MULTI stays its own stratum, entering no family denominator; the 12 cross-labelled are all `RVT-CRISPR\|RVT-CRISPR-like` and keep both labels |
| 309 | "what makes a unique pair?" | a pair is a distinct `(rt_seq_hash, nc_seq_hash)`; because both hashes are **exact**, boundary variants of one RNA count as several pairs — which is why 659 of the 921 multi-partner RTs differ by ≤5 nt. Clustering is required before the topology means anything |
| 319 | "what does this mean?" | of 30,924 pairs, 9,362 (30.3 %) recur only as several database copies of **one physical locus** — that is deposition, not independent observation. Only the 4,452 one-species and 5,056 multi-species classes support an evolutionary reading |
| 419 | "200 bp correct? does it contain all matches?" | no — 200 bp is the joint-geometry mode, not a completeness bound. It costs 2,769 pairs (N8 step 6). `K2_criterion_sensitivity` gives the 500 bp alternative (26,999 vs 25,938 pairs marginally) |
