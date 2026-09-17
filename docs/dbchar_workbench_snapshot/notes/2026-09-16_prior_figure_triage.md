# NOTE 2026-09-16 — triage of the RETRON-DB_V3 stage-1 figure set

Source (read-only, ideas only):
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage1_db_analysis/{figures,scripts}`

**Nothing from there is reused numerically.** That run was built on a different extraction with a
different denominator (its ncRNA axis is 645,330 rows because it *included* the ncRNA-anchored
records, which the 2026-09-15 Rule 1 now excludes; ours is 346,722). Every item below is a
**question worth re-asking on the current canonical datasets**, not a result to carry over.

## Verdict on the operator's keep-list

| prior figure | verdict | where it lands | what has to change |
|---|---|---|---|
| `s02_family_composition` | **already built**, extend | B1 | show all 41 families, not top 18 — one-hue ranked bars, log x |
| `s02b_redundancy` | **already built** | A2 | prior did it per family; ours is per database. Both are worth having — add the per-family fold |
| `n1_ncrna_rate_by_family` | **already built** | C1 | ours is the zero-rate on loci; prior used exact RTs. Add the `V-RT` axis |
| `s09_cm_models` | **already built** | C3 | — |
| `s09_ncrna_distributions` | **already built**, extend | C2 | prior also had GC and folding free-energy panels; we have `gc_content` + `free_energy` and are not using them |
| `s10b_direction` / `s10b_gap_distance` / `s10b_cds_between` | **already built, refined** | D1–D3 | ours already adds the clipping stratification the prior lacked |
| `n1_family_x_cm_matrix` | **add** — high value | C4 (new) | family × CM heatmap, single-hue sequential + LogNorm. Directly tests whether retron CMs are retron-specific. Must carry the detector-scope caveat |
| `s08_venn_diagram` | **add** | E | `matplotlib_venn.venn3` on `rt_tool_calls_v1`; the seven `detected_by_set` classes are already a partition |
| `s07_cooccur_by_tool` | **add**, as venn + table | E | ncRNA carriage per tool set. Ours currently exists at *record* level; the exact-RT axis is the better one. Prior showed 88.3 % myRT+PADLOC vs 20.8 % myRT-alone on exact RTs — we get 89.23 % vs 13.50 % on records, so the axis materially changes it |
| `subtype_breakdown` | **add**, enhanced | E or a new subtype section | The prior's real contribution is the **normalisation-first** approach: two tools use incompatible naming schemes (`Retron_I_C` vs `retron_I-C`), so any raw subtype count double-counts. We have `subtypes_padloc` / `subtypes_defensefinder` and g6 already measured 160,381/365,708 agreement. Port the canonicalisation map as its own auditable table before any subtype number |
| `genus_overrep` | **add**, with a fix | H | Prior's `enrichment = genus share in db / genus share in corpus` is a **relative-composition ratio, not an enrichment test** — there is no surveyed-genome denominator. Keep the figure, rename the quantity to "relative representation", and state that an enrichment claim needs a denominator this corpus does not contain |
| `s03_archaea_by_family` | **add**, improved | H | Prior put MULTI in the family bars — hold it out as a labelled stratum (Rule 2). Report per taxonomy system |
| `s04_phylum_composition` | **add**, materially fixed | H | **Prior pooled taxonomy schemas**: its bars contain both `Pseudomonadota` and `Proteobacteria`, and both `Bacillota` and `Firmicutes` — the same phyla under GTDB and NCBI names, counted as four. Must be split by `taxonomy_system`, and reported on exact RTs as well as records |
| `s04_rank_depth_by_db` | **add as a table**, per operator | H | It is 8 rows × 3 states; a table carries it better than a bar chart |
| `n3_metagenomic_by_family` | **add** | H or A4 | metagenomic share per family. Note the A4 caveat: metagenomic databases never collide, so this one *is* partitionable |
| `s10_position_relative_to_rt` | **add**, repurposed | I, not D | This is the best existing exhibit of the shipped-field artefact: 97.7 % null and its non-null values are nonsense (`-9452`, `-9764`). It belongs in QC as the provenance record, never in the geometry section |
| `s12_systems_per_genome` | **add** (operator said "maybe") | H | RT burden per genome, counting **distinct `rt_seq_hash` per `genome_id_norm`** so a twin-published genome counts once. Multi-RT genomes are the candidate-island population |

## From the prior set the operator did not list, worth a look

| prior figure | why |
|---|---|
| `n2_clipping_effects` / `n2_clip_vs_partial` / `s05_length_clip_shift` | quantifies the clipping↔partiality confound. This is exactly the confound B3 flags and does not yet measure; and it is the evidence base for the `POP_RT` decision to *stratify* clipping rather than exclude it |
| `s13_multi_combos` | MULTI label-set combinations — section G already plans it |
| `s11_cds_per_window` | CDS density per window; the denominator behind `n_cds_between` |
| `n3_gem_ecosystem` | the only ecological axis in the corpus (GEM `ecosystem_category` / `habitat`). Metagenomic subset only |
| `subtype_entropy` | Shannon entropy of host genus per subtype — a host-range measure that survives dedup |
| `n4_duplicate_ids` | g1/g2 covered this more rigorously; skip |

## Method carry-overs worth adopting regardless of figure

1. **Normalisation before counting** for any string label from two tools (the subtype case).
2. **Every figure stamped with its axis, exact n and caveat** — the prior did this consistently and
   it is why its figures are still readable a year later. Our notebook does it in markdown; the
   figures themselves should carry it if any is promoted to `results/`.
3. **One hue for magnitude, never a categorical rainbow** — the prior's stated form rule; correct.
