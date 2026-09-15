# FIGURE_AND_ANALYSIS_PLAN — `dbchar_g7b_stage1_extended_report`

**Written 2026-09-15, before any analysis script was run.** Changes made after execution
started are appended in §F, never edited in place.

## A · What this bundle is, and is not

- A **reporting-only scientific synthesis** over the landed Stage-1 bundles (g1–g7) and the
  registered Stage-1 derived datasets in `data/derived/`. It is a view layer, not a new
  measurement gate.
- It does **not** modify, overwrite or re-land g1–g7. `results/dbchar_g7_stage1_report/` remains the
  authoritative Stage-1 closeout/validation report.
- It does **not** touch Stage-2 files (`launchers/LAUNCHER_02_*`,
  `docs/decisions/2026-09-15_stage2_prior_dossier_audit.md`, `references/`) or the RT0–RT7 package.
- It promotes **no claim**. Every interpretation is `PROPOSED:` and `human_input_audit` stays PENDING.
- If a re-derived number disagrees with a landed g1–g6 value, the build **stops** (`c01_reconcile`
  exits non-zero) and the discrepancy is reported. It is never silently corrected.

Architecture (per REPORTING_STANDARDS, "a figure spanning several gates' tables is its own gate"):

```
a*.py  analysis scripts   derived parquet + landed TSVs  ->  tables/*.tsv   (every new number lands here first)
c*.py  checks             reconcile vs landed g2–g6 values; positive controls; independent recount
f*.py  figure scripts     tables/*.tsv ONLY                ->  figures/*.png|svg  (+ tables/<fig>.tsv)
findings.py               prose with {placeholders}; each placeholder = (table, exact row selector, column)
assemble_report.py        resolves placeholders from tables, embeds figures; COMPUTES NOTHING
```

## B · Inputs and the one declared data gap

Preferred inputs (all hashed in `INPUTS.tsv`): the 13 derived datasets named in the request, plus
`rt_window_cds_v1.parquet` (only for the independent intervening-CDS recount check) and the landed g1–g7
TSVs.

**Raw JSONL is not read.** Every section below can be answered from the landed/derived data.

**Declared gap: taxonomic prevalence denominators (§11).** No landed table carries *sampled genomes
per taxon*. The GTDB catalogue that g5 already hashed and joined
(`MELISSA_DATA/.../gtdb_bacteria_metadata.tsv.gz`, g5 INPUT) is the only source of a per-phylum
denominator. It is read for **two columns only** (`accession`, `gtdb_taxonomy`) and CheckM2
completeness for one QC stratification. This is a registered Stage-1 metadata input, not raw corpus.
Without it §11 could report representation only, never prevalence.

Two small registered detector resources are read as **context tables, not measurements**: the 18
PADLOC `retron_*.yaml` rules, to show whether a rule requires, allows or prohibits an ncRNA (this is
the detector-definition coupling that §6/§7 must state), and `cm_meta.txt` for the CM → described-retron
mapping. Both hashed.

## C · Probes run before writing this plan (facts, not conclusions)

1. **The upstream distance is bimodal, and the median hides it.** CANONICAL upstream gaps pile up at
   21–50 bp (97,825) and 1,001–2,000 bp (122,328), per `g3_distance_bins.tsv`. In the 900–1,100 bp
   band, 117,509 placements have 0 intervening CDS, and **102,853 of those come from one exact RT
   (`4e86f2e4…`), 111,581 from *Salmonella enterica***. The CM is TypeIA_IIAI, with median signed distance
   −1,037 bp (`g3_model_composition.tsv`). This is **not** a g3 counting error: the example records show
   a ~1 kb intergenic gap with no Prodigal CDS in it. It is a **redeposition-driven mode**, so the
   placement-level median (55 bp) is partly a statement about *Salmonella* sequencing effort.
   → §5 must show geometry at placement, physical-locus **and** exact-pair units.
2. **PADLOC rule coupling is concrete** (from the YAMLs). The ncRNA is a *secondary* gene in 17/18 retron
   rules. For `retron_Ec107-like` and `retron_outgroup` (min_core 1, min_total 2, ncRNA the only
   secondary gene) **a PADLOC call cannot be made without a second hit, i.e. effectively requires the
   ncRNA**. For `retron_XII` the ncRNA is a **prohibited** gene. The ncRNA calls in the corpus are
   `nc_source = infernal` for 100% of CANONICAL placements and use PADLOC's own CM names. So any
   "ncRNA rate by PADLOC subtype" or "by tool combination" is partly fixed by rule. The old report's
   "confirmed CM-gap subtype Retron_XII" is a rule artefact under this reading.
3. The old report's headline "retron_V is structurally distinct: 67% downstream" coincides with g3's
   TypeV contig-start-clipped technical mode (5,190 placements, 99.96% `true_start_clipped`).
   → reconciled explicitly in §5.
4. The old report's "43.5% separated by exactly one CDS (effector slot)" used gene-order offsets. g3's
   coordinate rule (CDS **wholly** in the gap) gives 3.6%. Both are definitions, not errors. §5 shows
   0/1/2/3/>3 under the landed rule and states the definitional difference.

## D · Proposed figures and tables

Legend. **Unit** = analytical unit of the plotted number; **Denom** = what a rate is out of; **Origin**
= `OLD` (idea in `report_ncbi_bacteria_Bacteria.html`, re-derived here), `G7` (in the closeout report,
re-visualised), `NEW` (enabled by the Stage-1 canonical units). **Cost** is estimated on borg (48 cores,
251 GB): `S` <30 s, `M` 30 s–3 min, `L` 3–10 min, all single-process pandas.

Global conventions, declared now:
- *Rates* carry a Wilson 95% interval (estimator declared; not a census) and always n/N.
- *Major families* = top 12 by exact RTs in `V-RT-SINGLE`; the rest collapse to "other (29 families)".
  MULTI is always its own bar, never in "other".
- *Technical downstream mode* = g3's own rule (CANONICAL, downstream, within ±150 bp of the downstream
  median 2,682 bp), flagged `tech_mode`. Biological-interpretation views exclude it, and every such
  view shows the excluded n.
- *Tool combination of a locus/exact RT* = union of `detected_by` over its distinct records. Loci whose
  records disagree on combination are counted and reported, not dropped.
- *Canonical ncRNA carriage* of a unit = ≥1 CANONICAL placement at that unit.
- No hypothesis tests. Comparisons report effect size (difference or ratio of proportions), n and
  Wilson CI, on physical loci or exact RTs, never on raw placements.

### §1 Corpus and redundancy structure (C1/C2)

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F01 | How much does each normalisation step remove? | `g2_unit_ladder`, `g2_duplicate_lines`, `g2_twin_evidence` | records → distinct → loci → physical loci → exact RTs | previous step | funnel with step losses named (duplicate lines, multi-record loci, RefSeq/GenBank twins, sequence identity) | G7 | ESSENTIAL | S |
| F02 | Does the collapse factor depend on database? Where do exact RTs come from? | `rt_records_v1`, `g2_ladder_by_source_database` | exact RTs × source-database set; loci per exact RT per DB | exact RTs | (a) loci-per-exact-RT by DB (dot); (b) exact-RT sharing across the 3 big DBs + "other", as UpSet bars | NEW | ESSENTIAL | M |
| F03 | How concentrated is recurrence? | `rt_exact_v1`, `rt_family_baseline_v1` | exact RTs | exact RTs of the family | CCDF of loci / genomes / databases per exact RT, top-6 families; top-1% share annotated | NEW | ESSENTIAL | S |
| F04 | How much does apparent family abundance change with the unit? | `rt_records_v1`, loci, physical loci, exact | 4 units | all RT-anchored units of that level | slope/dumbbell of family share: records vs physical loci vs exact RTs | NEW | ESSENTIAL | M |
| F05 | Database × family composition | `rt_records_v1` | exact RTs (distinct within DB) | exact RTs of that DB | column-normalised heatmap, top-12 families + MULTI + other | OLD (idea) | USEFUL | S |

### §2 RT-family composition

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F06 | Ranked family abundance that cannot masquerade | `rt_family_baseline_v1`, `g2_ladder_by_family_label` | exact RTs (bar), physical loci & records (markers) | n/a (counts) | ranked horizontal bars, log axis, DB-stacked at exact-RT level, MULTI separate, long tail collapsed | OLD | ESSENTIAL | S |

### §3 RT length

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F07 | Length distribution per major family, complete vs partial | `rt_family_baseline_v1` | exact RTs (V-RT-SINGLE; MULTI separate) | exact RTs of family × completeness class | split violins from 10-aa histograms + median/IQR, n per side | G7 (re-visualised) | ESSENTIAL | S |
| F08 | Whole-catalogue shape; shifted/broad/multimodal families | same | exact RTs | exact RTs of family | ECDF (top 12) + shape table (IQR/median, q95/q05, modes by a declared peak rule, % beyond Tukey fences) | NEW | USEFUL | S |

### §4 ncRNA length and CM/model composition

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F09 | ncRNA length by CM; boundary variability visible | `ncrna_family_baseline_v1` | exact ncRNA sequences | exact ncRNAs of that CM | box + strip-density per CM sorted by median, n; overall histogram inset | OLD | ESSENTIAL | S |
| F10 | CM composition changes with the unit | `rt_ncrna_pairs_v1` | placements / physical loci / exact pairs / exact ncRNAs | all CANONICAL units of that level | 100% stacked bars, 4 units | NEW | ESSENTIAL | S |
| F11 | Which CM calls which subtype, per tool (unpooled) | pairs + `rt_tool_calls_v1` | Retron loci | Retron loci carrying that tool's subtype label | 2 heatmaps (PADLOC subtype × CM, DefenseFinder subtype × CM), row-normalised, with row carriage and n | OLD (re-derived per tool) | ESSENTIAL | M |
| T-structure | structure annotation vs biological absence | pairs, `ncrna_family_baseline_v1` | exact ncRNAs | exact ncRNAs of CM | table only | NEW | USEFUL | S |

### §5 RT–ncRNA genomic geometry (major section)

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F12 | Dominant configurations as a category schematic with counts | pairs + `rt_window_cds_v1` not needed | placements / physical loci / exact pairs | CANONICAL of that unit | schematic (not to scale) + counts per class: adjacent upstream (≤500 bp, 0 CDS) · long upstream intergenic (>500 bp, 0 CDS) · upstream across 1 CDS · upstream across ≥2 CDS · overlapping RT CDS · downstream (non-technical) · technical clipped downstream mode · opposite strand | NEW | ESSENTIAL | S |
| F13 | Signed distance: central zoom + tail-aware view, at 3 units | pairs, exact pairs | placements, physical loci, exact pairs | CANONICAL, tech mode flagged | (a) −300…+300 bp, 5-bp bins; (b) full range, symlog bins, tech mode shaded; densities per unit | G7 (re-visualised) + NEW units | ESSENTIAL | S |
| F14 | Absolute distance & the ~1 kb mode | pairs | placements vs physical loci vs exact pairs | same | ECDF by unit; decomposition of the 900–1,100 bp band by top exact RTs / species | NEW | ESSENTIAL | S |
| F15 | Intervening CDS 0/1/2/3/>3, strand, CDS overlap | pairs | placements and physical loci | CANONICAL | grouped bars (two units) + overlap panel: any CDS / RT CDS / non-RT CDS; same/opposite strand by direction | G7/OLD | ESSENTIAL | S |
| F16 | Geometry by CM model | pairs | physical loci | CANONICAL physical loci of that CM | small multiples: signed-distance histogram per CM (symlog bins) + direction/CDS-between stacked bars with n | NEW | ESSENTIAL | S |
| T-oldrecon | old-report geometry headlines vs canonical definitions | tables | — | — | reconciliation table (retron_V downstream, 1-CDS effector slot, 73.7% upstream) | NEW | ESSENTIAL | S |

### §6 Tool intersection and ncRNA carriage

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F17 | 3-tool Venn (intuition) | `rt_tool_calls_v1`, pairs | Retron physical loci | Retron physical loci | 3-circle Venn with n and canonical-carriage % per region | OLD | ESSENTIAL | M |
| F18 | UpSet: combination size at 4 units + carriage with CI | same | records, loci, physical loci, exact RTs | units of that combination | UpSet (matrix + bars) + carriage dots with Wilson CI at physical-locus and exact-RT units | NEW | ESSENTIAL | M |
| F19 | Is the gradient composition? | same + subtypes | Retron physical loci | loci of (combination, PADLOC subtype) | heatmap combination × PADLOC subtype carriage, cells with n<30 masked | NEW | ESSENTIAL | M |
| T-rules | detector-definition coupling | PADLOC YAMLs | rules | n/a | table: ncRNA role per rule | NEW | ESSENTIAL | S |
| T-allRT | non-Retron families by tool | `g6_tool_matrix_by_family` | records | family | table only | G7 | USEFUL | S |

### §7 Retron ncRNA detection coverage / zero-call structure

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F20 | 0/1/2/>2 calls per Retron physical locus, by DB | `rt_loci_v1`, pairs | Retron physical loci | Retron physical loci of DB | 100% stacked bars with n | OLD/G7 | ESSENTIAL | S |
| F21 | Is zero-call explained by missing upstream context? | `rt_records_v1` (window coords), pairs | Retron physical loci (representative record) | loci in upstream-context bin | carriage vs bp of upstream window available (bins), CI, split contig-clipped vs not | OLD (boundary proximity, re-derived) | ESSENTIAL | M |
| F22 | Carriage by tool subtype with rule annotation | tool calls, pairs | Retron physical loci | loci carrying that subtype label (per tool) | lollipop ± Wilson CI, PADLOC and DefenseFinder panels; rule glyphs (required / secondary / prohibited) | OLD (reinterpreted) | ESSENTIAL | S |
| T-quality | carriage vs RT completeness and host CheckM completeness (GTDB/MGnify only) | tool calls, family baseline, GTDB catalogue | Retron physical loci | loci of stratum | table (+ panel in F21 if informative) | NEW | USEFUL | M |
| T-multiplicity | ncRNA call multiplicity per locus by CM | `g3_calls_per_locus`, pairs | loci | loci with ≥1 call | table only | G7 | USEFUL | S |

### §8 Exact RT–ncRNA pairing topology

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F23 | Topology and recurrence of the 30,924 exact pairs | `g3_topology_components`, `rt_ncrna_exact_pair_recurrence_v1` | components; exact pairs | components; exact pairs | (a) component-shape bars (components / RTs / ncRNAs); (b) CCDF of placements & species per pair by recurrence class; (c) class share at pair vs placement unit | G7 re-visualised + NEW | ESSENTIAL | S |
| F24 | Do recurrent exact RTs keep the same ncRNA partner? Same CM? | exact pairs, pairs | exact RTs with calls at ≥2 physical loci | those RTs | dominant-partner fraction histogram by recurrence bin; single-CM share | NEW | ESSENTIAL | S |

### §9 Atypical non-Retron retron-CM candidates (266 rows)

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F25 | What the candidate population looks like vs ordinary Retron placements | `rt_ncrna_nonretron_candidates_v1`, pairs | placements (and physical loci / exact RTs in table) | 266 candidates; CANONICAL Retron | 4 panels: family × CM counts; signed distance strip vs Retron density; strand/direction/CDS-between bars; recurrence (loci/species per candidate exact RT). Fraction inside a declared Retron envelope | G7/NEW | ESSENTIAL | S |

### §10 MULTI ambiguity

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F26 | Margin, family pairs, length | `multi_hmm_evidence_v1`, `g4_multi_hmm_*`, `g4_multi_label_sets_vs_hmm` | MULTI exact RTs (7,593) | MULTI exact RTs | (a) margin ECDF MULTI vs landed control; (b) margin vs length hexbin; (c) label-pair co-occurrence heatmap (best family marked) | G7 + NEW | ESSENTIAL | S |
| T-multi-arch | MULTI with unusual architecture (edge/clipped/ncRNA) vs single families | `rt_records_v1` | records → exact RT | MULTI vs single-family records | table | NEW | OPTIONAL | S |

### §11 Taxonomic representation vs prevalence

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F27 | Phylum: sampled genomes vs RT-positive genomes; prevalence with CI (GTDB schema, `gtdb_bacteria` DB only) | `rt_records_v1` + GTDB catalogue | genomes | catalogue genomes of phylum (**sampled** = in catalogue, a stated upper bound on attempted) | paired bars (log) + prevalence dot ± CI; exact RTs per RT-positive genome | OLD (idea) + NEW denominator | ESSENTIAL | M |
| F28 | Family × phylum prevalence | same | genomes | catalogue genomes of phylum | heatmap (% genomes with ≥1 locus of family), top phyla ≥1,000 sampled genomes | NEW | ESSENTIAL | M |
| F29 | Class/order/genus prevalence, top by sampled genomes | same | genomes | catalogue genomes of taxon (≥500) | dot ± CI, three small panels | NEW | USEFUL | M |
| F30 | NCBI schema: representation only (no denominator used) | `g5_overrepresentation_genus` | records / exact RTs / genomes | records of that taxonomy system | dumbbell: % of records vs % of exact RTs, top 20 genera | G7/OLD | USEFUL | S |

### §12 Data quality and eligibility

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F31 | How much is directly inspectable? | `rt_records_v1`, `g2_*`, `g2b_*`, `g5_quality_availability` | distinct records (and physical loci in table) | RT-anchored distinct records of DB | 4 panels: back-translation class by DB; no-RT-CDS recovery class by DB; context truncation (inverted / RT outside / start-clipped / end-clipped / RT at edge) by DB; CheckM availability by DB. Summary tier bar: fully inspectable / retained-with-caveat / sequence-only / ill-posed | G7/NEW | ESSENTIAL | M |

### §13 Secondary analyses unlocked by Stage 1 (exploratory, associations only)

| id | question | source | unit | denominator | plot | origin | prio | cost |
|---|---|---|---|---|---|---|---|---|
| F32 | RT length vs ncRNA carriage (Retron) | family baseline, pairs | Retron exact RTs | exact RTs in length bin × completeness | carriage by length bin ± CI | NEW | USEFUL | S |
| F33 | Are high-recurrence RTs taxonomically broad or database-duplicated? | `rt_exact_v1`, records | exact RTs with ≥20 genomes | those RTs | hexbin genomes vs species (log), coloured by DB-span; table of top 25 | NEW | USEFUL | M |
| F34 | Database-specific annotation: Retron tool-combination mix and carriage by DB | tool calls, pairs | Retron physical loci | Retron loci of DB | 100% stacked combo mix + carriage dots per DB | NEW | USEFUL | S |
| T-subtype-geom | family/subtype-specific intervening-CDS & distance | pairs + tool calls | Retron physical loci | loci of PADLOC subtype | table (distance quantiles, CDS-between mix) | NEW | USEFUL | S |

**Total proposed: 34 figures (27 ESSENTIAL, 7 USEFUL) + ~40 landed tables.** Several will merge into
multi-panel figures, and the final count is reported in the README. OPTIONAL items (T-multi-arch) are
run only if cost is trivial.

### Dropped from the old report, and why

| old idea | decision | reason |
|---|---|---|
| genome outcome donut (with systems / empty / failed) | **dropped** | the corpus contains only RT-positive records; failed/empty genomes are not in any Stage-1 input |
| Shannon entropy per subtype over genera | **dropped** | a genus entropy on records is sequencing-effort weighted; exact-RT-level breadth (F33) answers the HGT-breadth question with a stated unit |
| species "≥2× genus median" enrichment | **dropped** | no per-species sampled-genome denominator for NCBI; GTDB prevalence (F27–F29) replaces it |
| subtype co-occurrence per genome | **dropped (deferred)** | needs per-genome multi-locus neighbourhood reasoning, out of Stage-1 scope (launcher non-goal: operon delimitation) |
| systems per contig / densest contigs | **dropped** | context-window grain cannot separate tandem loci from twins without an unregistered contig-level view |
| window-extension "lift" | **dropped** | `extended_for_cds` is set on 66.6% of records by the extractor's own rule; a lift conflates window size with locus class. F21 (upstream context bp) asks the same question directly |
| Infernal score by subtype | **dropped to table** | scores are CM-specific (not comparable across CMs); carried in T-structure per CM only |
| GC content by group | **dropped** | no host-GC denominator is landed; per-ncRNA GC without host GC is uninterpretable |
| retron_V "biological downstream anomaly" | **retained as a correction** | re-derived: coincides with the technical clipped mode (§5, T-oldrecon) |
| 1-CDS "effector slot" 43.5% | **retained as a reconciliation** | definitional difference (gene-order offset vs CDS wholly in gap), shown in F15/T-oldrecon |
| CM-gap subtypes (VI, XI, XII at 0%) | **retained, reinterpreted** | F22 with PADLOC rule glyphs; XII prohibits ncRNA by rule |
| tool Venn + ncRNA rate per combo | **retained** | F17–F19, at physical-locus/exact-RT units with CI and a composition control |
| RT length by subtype | **retained** | F07/F08 on exact RTs, families (subtype-level lengths deferred: subtypes are tool labels) |
| boundary-proximity detection gradient | **retained** | F21, measured as upstream bp available, not CDS rank |

## E · Checks (all in `run.sh`, before the report is assembled)

1. **Reconciliation against landed values (STOP on mismatch)** — `c01_reconcile.py`: every
   re-derived quantity that a landed g2–g6 table also carries (unit ladder, per-DB ladder, canonical
   direction/strand/CDS-between counts, zero-class Retron loci, tool matrix records and carriage,
   exact pairs/topology, 266 candidates, MULTI margins, GTDB top species share) is compared exactly.
   Any disagreement → exit 1 and a `c01_discrepancies.tsv` row. No correction is attempted.
2. **Independent recount** — `c02_independent_cds_between.py`: on a seeded sample of 5,000 CANONICAL
   placements, intervening CDS and CDS overlap are recomputed from `rt_window_cds_v1` with an
   interval-array implementation that shares no code with g3.
3. **Positive controls** — `c03_controls.py`: the Wilson interval on known values; UpSet/Venn regions
   partition their population exactly; configuration classes partition CANONICAL; funnel monotone;
   the peak-count rule finds 2 modes on a constructed bimodal sample and 1 on a unimodal one; the
   assembler refuses an unresolvable placeholder (seeded-bad).
4. **Figure/table integrity** — every figure has `tables/<same basename>.tsv`, and figure scripts open
   nothing outside `tables/` (asserted by path audit in `run.sh`).
5. **Byte reproducibility** — `run.sh` reruns from the assembled bundle and `cmp`s every table, figure,
   REPORT.md/.html and MANIFEST.
6. Optional independent reproduction by a second implementation (Codex, if available) of 3 headline
   numbers (F12 class counts, F18 physical-locus carriage per combination, F27 top-phylum prevalence),
   recorded as such, never as the source of a number.

## F · Amendments after execution started

_(none yet)_
