# RESEARCH CONTRACT — Retron large-scale mining and biological analysis
_Standing science only. Stable across tasks; per-task execution belongs in `launchers/` and ARIS owns the workflow._
## The question
How can a large genome- and metagenome-derived catalogue of reverse transcriptase (RT) systems be converted from heterogeneous mining records into defensible biological objects, and what can those objects reveal about retron diversity, RT architecture and classification, genomic organization, ncRNA association, annotation limits, and RT–ncRNA co-evolution?

Retrons are the primary biological target. Other bacterial and archaeal RT families are retained as evolutionary and methodological comparators.

## Claims

Every claim is born `UNPROVEN`. Prior projects, stage notes, reports, scripts and bundles are evidence/idea sources, not automatic authority here.

| id | claim | status | settled by | circularity |
|---|---|---|---|---|
| `C1` | The mined corpus contains non-uniform redundancy and source representation that materially changes the population described by a raw-record count. | `UNPROVEN` | — | `LOW` |
| `C2` | Record, genomic locus, exact RT sequence, RT taxonomic occurrence and RT–ncRNA pair are non-equivalent analytical units and support different downstream questions. | `UNPROVEN` | — | `LOW` |
| `C3` | RT0–RT7 and related RT sequence/structural elements can be given reproducible operational definitions with explicit failure and uncertainty states across relevant RT families. | `UNPROVEN` | — | `LOW` |
| `C4` | RT domain geometry, catalytic motifs and additional sequence/structural features vary systematically across RT families/retron groups rather than being explained only by annotation convention. | `UNPROVEN` | — | `LOW` |
| `C5` | Retron loci show reproducible patterns of ncRNA position, orientation, multiplicity and neighbouring architecture that can be separated from technical or annotation anomalies. | `UNPROVEN` | — | `LOW` |
| `C6` | Bona fide RT–ncRNA pairs retain evidence of association beyond shared ancestry, taxonomy and detector-derived grouping. | `UNPROVEN` | — | `MEDIUM` |
| `C7` | Disagreement among retron/RT annotation routes contains measurable information about detector scope, technical failure and candidate biological divergence; agreement is not independent corroboration when tools share provenance. | `UNPROVEN` | — | `LOW` |
| `C8` | Apparent RT/retron diversity, saturation and taxonomic/ecological distribution change after correcting for redundancy, database composition and sampling depth. | `UNPROVEN` | — | `LOW` |
| `C9` | Detection/localisation and boundary delimitation are separable measurable properties for ncRNAs, RT subdomains and operon boundaries. | `UNPROVEN` | — | `LOW` |

⚠️ **No claim here is circularity `NONE`.** `C1`, `C2` and `C8` all describe units derived
from **one JSON parse of one corpus** — a coordinate or extraction defect moves all of them
together, so they can agree while all being wrong. That is `LOW`, not `NONE`, and the
independent second count each gate owes (WA-D.3) is what prices it.

## Canonical analytical objects

The phrase “unique system” is never used without naming the operational unit.

| object | working definition |
|---|---|
| raw record | one mining-pipeline output record |
| RT occurrence | one RT call at one genomic occurrence |
| locus | one genomic occurrence/context defined by auditable genomic identity and coordinates |
| exact RT | exact amino-acid sequence identity, hashed from sequence in this project |
| RT taxonomic occurrence | an exact RT observed in a declared genome/taxon occurrence |
| RT–ncRNA association | observed RT/ncRNA relation with coordinates, strand, distance and multiplicity retained |
| exact RT–ncRNA pair | exact RT + exact ncRNA after duplicate-call reconciliation; genuine multiplicity stays flagged |
| analytical view | declared query over the canonical locus table, never an undocumented copied subset |

Operational definitions may be refined by the task that measures them. Ambiguous/atypical observations are flagged rather than silently deleted.

## Datasets

| name | path | what it is | trust |
|---|---|---|---|
| raw mining corpus | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/` | canonical genome/metagenome mining output to inventory/hash | `RAW` |
| current project metadata | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/databases_metadata_files/metadata_files/` | taxonomy/assembly/environment metadata where available | `RAW` |
| input schema | `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/templates/input_format_schema_only.md` | intended structure; verify against real records | `RAW` |
| prior production project | `/home/borg/RESEARCH-retron-db/` | prior bundles/views/reports/QA register | `RE-DERIVE` |
| stage briefs | `/home/borg/RETRON_STAGES/` | ideas, paths, prior findings and dependencies | **not an authority** — a trust grade applies to a measurement; these are prose. Nothing cites a number from here. |

No prior numeric measurement is `FROZEN` here unless a later decision explicitly promotes it and names the producing bundle.

## Biological priors

Known retron architecture, catalytic motifs, expected strand/orientation, ncRNA proximity and published subtype/domain conventions are priors/QC features, not automatic filters. ncRNA distance, CDS separation, overlap, orientation or unexpected order may reflect misassociation, overlapping systems, contig effects or real biology; Stage 1 records them before a later task decides how to use them.

## Baselines and metrics

| claim | metric / unit | baseline compared against | why the baseline can disagree |
|---|---|---|---|
| `C1`,`C2` | exact counts/redundancy on record, locus, genome, exact-RT and pair units | raw-record view vs independently built canonical views | the units intentionally collapse different duplicate classes |
| `C3` | per-block occupancy, boundary uncertainty and failure state per RT family | published conventions + held-out structural/reference anchors | convention and structure are different instruments |
| `C4` | motif/domain occupancy and geometry on non-redundant RTs | independent structures and family-matched controls | motif sequence and geometry can fail independently |
| `C5` | ncRNA distance/orientation/CDS separation/overlap/multiplicity per locus | retron-labelled vs appropriate non-retron/context controls | comparator is not defined by the same ncRNA prior |
| `C6` | paired-vs-mismatched association under progressively stronger relatedness controls | random, within-clade, within-genus, phylogenetically matched, taxonomy-only | each preserves a different amount of shared ancestry |
| `C7` | per-tool agreement/disagreement classes on declared loci | independently provenanced routes where available | different program names do not imply independent evidence |
| `C8` | replicated diversity/rarefaction/distribution on corrected sampling units | raw vs redundancy/database-composition-corrected sampling | sequencing effort and biology contribute differently |
| `C9` | localisation plus boundary error/coverage on known-boundary controls | independently known positive controls | finding an object and delimiting its edges are distinct measurements |

Every rate names its population in words and carries a denominator that can be independently checked.

## Project dependencies

Stage 1 establishes canonical objects and retained flags. RT0–RT7/domain work consumes the non-redundant RT view; neighbourhood work the locus/context view; diversity/taxonomy the redundancy+metadata views; annotation-disagreement the per-tool calls/missingness; co-evolution the RT–ncRNA pair view plus later relatedness and delimitation controls. Future launchers are written just-in-time from this contract plus landed evidence; `/home/borg/RETRON_STAGES/` is a planning archive, not a predeclared workflow.

## Kill criteria for the project

- If the canonical raw corpus cannot be identity-pinned and reconstructed with auditable sequence, coordinate and source provenance, no corpus-wide biological claim is promoted; narrow to reference/method work until repaired.
- If a headline effect cannot be separated from the detector/model convention that defined its population, do not promote it as biology.
- A null/refuting result kills the scientific line it addresses, not the whole project. Negative results land when the instrument has demonstrated power to detect the corresponding positive.

## Key decisions

| date | decision | why | supersedes |
|---|---|---|---|
| 2026-09-14 | ARIS owns lifecycle/artifacts/loops/reviewer routing; governance constrains data safety, evidence, provenance, reporting and compute. | avoid a second workflow engine | governance-orchestrated lifecycle |
| 2026-09-14 | `/home/borg/RETRON_STAGES/` and earlier projects are idea/evidence sources, not authorities. | prior work is useful but carries known provenance/definition problems | treating stage notes as frozen truth |
| 2026-09-14 | Keep parallel analytical units/views instead of one universal “unique system.” | locus, exact RT and RT–ncRNA pair answer different questions | one deduplicated master subset |
| 2026-09-14 | Stage 1 follows REUSE → VERIFY → GAP ANALYSIS → COMPUTE ONLY GAPS. | extensive prior work exists | recompute-everything Stage 1 |
| 2026-09-14 | Keep large/canonical data in place; register path+hash and copy only small load-bearing references when useful. | avoid duplicate research trees | indiscriminate copying |

## Known-wrong

⚠️ Absence is loud; wrongness is quiet — a stale artefact reads as ready and nothing
prompts a check. Each of these was paid for once; the numbers are what make them stick.

- ⛔ **Coordinates are contig-based.** `intergenic_regions[].start/end` and `rt_gene.start/end`
  are contig coordinates; `genomic_context.full_sequence` is a window and `actual_window.start`
  the offset. **1 in 6 records has `start == 1`**, where both frames coincide and every
  arithmetic check passes anyway. Generalising from one such record once excluded **97.2%** of
  regions. Verify by **RT back-translation**, never by inspection.
- ⛔ **"Complete" means ORF-complete.** **69.2%** of previously-admitted proteins do not fill
  the RT window, and three live "complete" rules reach the same ~70% on sets agreeing at only
  **Jaccard 0.728**. Equal rates are not equal sets.
- ⛔ **Never glob a cache directory that also holds an aggregate file.** One such glob swept a
  merged table into a "non-retron" denominator: **n = 924,847 against a real 423,274**, and
  **99.65%** of the resulting "non-retron" hits were retrons.
- ⚠️ **Do not pool `system_subtypes`** — it is two tools on one locus (capital-initial =
  DefenseFinder, lowercase = PADLOC), agreeing on **44.6%**. Carry it; never `groupby` it.
- ⚠️ **`taxonomy.full_lineage` is two schemas** keyed by `taxonomy_system` — gtdb 7-field,
  ncbi 3-field with **no phylum**. Count per system, never pooled.
- ⚠️ **Pooling hides the distribution.** A pooled cross-group rate is the largest group's rate:
  `PQG[GA]` read **41.78% pooled vs 0.373% median-family**, a **112×** gap.
- ⚠️ **Inherited `rt_hash` is not a sequence hash** and no `rt_hash → locus` link exists.
  Compute `sha256` over the amino-acid sequence in this project.
- ⚠️ **`intergenic_regions[].has_ncrna` can be true while `ncrnas` is empty.** Any geometry
  built on `has_ncrna` must reconcile against `ncrnas` per record.
- ⚠️ `V_verify/cache/v1b_collapsed_RTxncRNA.parquet` is **not** the canonical pair set.
- ⚠️ Historical diversity/identity figures that do not reproduce their saved tables are not
  evidence here.
- ⚠️ Local InterProScan/Pfam is a **stub** — Pfam-A holds 3–4 profiles, TIGRFAM 1. A clean run
  against it is `DATA_INADEQUATE`, **not a negative**. Full Pfam-A 37.0 (21,979 models) is
  registered on Ibex.
- ⛔ **`VOID_DO_NOT_CITE.md` has not been consulted.** `idea-stage/programme/00_INDEX.md` says to check
  it before quoting any prior figure. **Locate it before any prior number is cited.**
