---
record: NEXT_TASKS_OPERATOR_REVIEW
date: 2026-09-20
status: PROPOSALS — nothing written as a launcher, nothing frozen, nothing dispatched
gate: your review before any of this runs
---

# Next tasks — operator review packet

Nine proposals. Every dataset each one consumes is registered in
`programme/CANONICAL_DATASETS.tsv` with its identity, count, limitations and exposure state.

**Read §1 and §2 first — they are the `NEW_SCIENCE` and load-bearing
`CANONICAL_ASSET_CONSTRUCTION` tasks you asked to see. §3 is bookkeeping you can skim.**

| # | task | kind | goal | can start now? |
|---|---|---|---|---|
| 1 | `T-D1-annotation-disagreement` | **NEW_SCIENCE** | 1, 6 | **yes** |
| 2 | `T-D2-taxonomic-distribution` | **NEW_SCIENCE** | 1, 6 | **yes** |
| 3 | `T-R1b-rtdna-anchor-mapping` | **NEW_SCIENCE** | 9 | needs **D7** |
| 4 | `T-A23d-primary-reference-resolution` | **NEW_SCIENCE** (evidence base) | 12 | **yes** |
| 5 | `T-P1b-identity-partition` | **CANONICAL_ASSET_CONSTRUCTION** — the trunk | 3 → 4, 6, 10 | needs **D12** |
| 6 | `T-N1d-neighbourhood-census` | **CANONICAL_ASSET_CONSTRUCTION** | 6 | needs **D2** |
| 7 | `T-M1b-embedding-cache-reverification` | **CANONICAL_ASSET_CONSTRUCTION** | 10, 11 | **yes** |
| 8 | `T-S1b-structure-inventory-correction` | **CANONICAL_ASSET_CONSTRUCTION** | 5 | **yes** |
| 9 | `T-AUDIT2-task-report-backfill` | **REPRODUCTION_REQUIRED** | governance | **yes** |

---

## 1 · NEW_SCIENCE

### 1.1 · `T-D1-annotation-disagreement` — **NEW_SCIENCE**

- **Biological question.** Where do the annotation tools disagree about what an RT record is, and is that disagreement structured by RT family, taxonomy or assembly quality — or is it noise?
- **Why it matters to 1–12.** Goal 1 is a *defensible* resource. Every family label in this project is tool-derived, and goals 2, 4 and 6 all stratify by that label. If disagreement is structured, every family-resolved number inherits a bias nobody has measured.
- **Why now.** It is the **largest untouched signal in the estate** (257,201 content files, 17 roots) and the input has been landed since Stage 1. It costs no confirmatory population and blocks nothing.
- **Canonical datasets consumed.** `RT-TOOL-CALLS-3051238` · `RT-FAMILY-LABELS-613` · `RT-RECORDS-3059700`.
- **Population / inferential unit.** Raw source record. Rows are **not** independent; `locus_key` is landed so a consumer can collapse them.
- **Prior work available.** 257,201 content files across 17 roots (`annotation_disagreement`); `OPERON_function` scripts in `RESEARCH-in-sleep-RETRON-DB`. Anchor control **PASS** (43 hits), so absence here is reportable.
- **What genuinely remains new.** Nobody has produced a **per-record disagreement table with a declared denominator**. Prior material is scripts and one-off inspections, not a census.
- **Method.** Per record, compare each tool's call; classify AGREE / DISAGREE / SINGLE_TOOL / NO_CALL. Cross-tabulate against family, taxonomy and assembly quality. **Never pool tool-specific fields whose provenance differs** — the original call is preserved.
- **Baseline / control.** *Positive:* reproduce a landed Stage-1 `dbchar_g6` count exactly (implementation reproduction). *Negative:* a synthetic record with two identical calls must classify AGREE, and one with two contradictory calls must classify DISAGREE.
- **Main confounders.** Tool **coverage** differs from tool **disagreement** — a tool that never ran is not a tool that disagreed. Missingness is reported as a result, not filtered.
- **Success / falsification / bound.** *Success:* a landed disagreement rate per family with its denominator. *Falsification:* disagreement is uniform across families — a clean negative that **strengthens** every family-stratified analysis. *Bound:* if coverage is too thin in some families, that ceiling is the result.
- **Interpretation ceiling.** ⛔ Disagreement is about **annotation**, not biology. A disputed record is not thereby an unusual retron.
- **Expected output.** `D1_disagreement_per_record.tsv` · `D1_by_family.tsv` · `D1_coverage.tsv` · `D1_controls.tsv`.
- **Downstream enabled.** `T-A6`, `T-A10`; and a measured caveat on every family-stratified number in goals 2, 4, 6.
- **Confirmatory spend.** None — `RT-RECORDS` already inspected.
- **Compute.** Local CPU, `CPU_SMALL`, `IO_MEDIUM`.
- **Parallel with.** Everything except the other `IO_HIGH` lane.
- **Launcher path.** `programme/tasks/T-D1-annotation-disagreement/TASK_LAUNCHER.md` *(to be written on approval)*.

### 1.2 · `T-D2-taxonomic-distribution` — **NEW_SCIENCE**

- **Biological question.** Which taxa carry these RT families, and how much of the catalogue can actually be placed taxonomically at all?
- **Why it matters to 1–12.** Goal 1 and goal 6. Every statement of the form *"retrons are common in X"* depends on a join this project has never measured. It also sets the ceiling on goal 7 — you cannot ask about evolutionary correspondence over records you cannot place.
- **Why now.** The metadata corpora are registered and local (GTDB, NCBI, MGnify, UHGG, GEM). 166,382 content files of prior material exist and **none of it is a measured join coverage**.
- **Canonical datasets consumed.** `RT-RECORDS-3059700` · `RT-FAMILY-LABELS-613` · the registered metadata files in `data/README.md`.
- **Population / inferential unit.** **Taxonomic occurrence** — its own unit, distinct from record, locus and exact RT.
- **Prior work available.** 166,382 content files, 16 roots, concentrated in `RETRONS_january_2026`. Anchor control **PASS** (118 hits).
- **What genuinely remains new.** **Join coverage and missingness as a reported result**, per taxonomy system, kept separate rather than pooled.
- **Method.** Join records to each metadata system on its own key; report coverage and missingness per system **before** any distribution is described. Taxonomy systems are retained separately, never merged into one lineage string.
- **Baseline / control.** *Positive:* a record with a known assembly accession must join. *Negative:* a fabricated accession must **not** join and must be reported as unjoined, not dropped.
- **Main confounders.** ⛔ **Database composition is not biology.** NCBI is dominated by clinically relevant taxa; a family looking "gut-associated" may be a sampling artefact. Metagenome bins carry different taxonomic confidence from isolates, and the distinction is retained.
- **Success / falsification / bound.** *Success:* per-system coverage plus a family × taxon table with explicit missingness. *Bound:* if coverage is low, **the ceiling on every taxonomic claim in the thesis is the result**, and a valuable one.
- **Interpretation ceiling.** ⛔ Describes **the database**, not the biosphere. No prevalence or enrichment claim without a declared sampling model.
- **Expected output.** `D2_join_coverage.tsv` · `D2_family_by_taxon.tsv` · `D2_missingness.tsv` · `D2_controls.tsv`.
- **Downstream enabled.** Goal 7 scoping; `T-A6`; the thesis's taxonomic section.
- **Confirmatory spend.** None.
- **Compute.** Local CPU, `CPU_SMALL`, `IO_MEDIUM` (1.3 GiB NCBI summary is the largest read).
- **Parallel with.** Everything except the `IO_HIGH` lane.
- **Launcher path.** `programme/tasks/T-D2-taxonomic-distribution/TASK_LAUNCHER.md`.

### 1.3 · `T-R1b-rtdna-anchor-mapping` — **NEW_SCIENCE** · ⚠️ merges `T-A5b1` and `T-R1`

- **Biological question.** Where, in each retron's ncRNA, does the empirically determined RT-DNA actually lie?
- **Why it matters to 1–12.** Goal 9, and it is the **only** place this project can anchor ncRNA architecture in wet-lab measurement rather than in covariance-model output. It is the one route that breaks the `CM-CALLS` circularity.
- **Why now.** `PANEL-RTDNA-81` is the strongest anchor in the project and is **entirely unexposed**. ⛔ It is also the one asset that could be **spent twice for one table** — `T-A5b1` and `T-R1` are the same task, which is decision **D7**.
- **Canonical datasets consumed.** `PANEL-RTDNA-81` (81 rows, sha256 verified) · `PANEL-175` for ncRNA sequence.
- **Population / inferential unit.** One assayed element. **n = 81. That is the whole population** — every statistic is small-sample and must be reported as counts, not rates.
- **Prior work available.** `rt_dna` 595 content files across 15 roots — the absence claim that the dead-instrument sweep got wrong. **No named anchor**, so absence is weak. Reclassified `DONE_NEEDS_IDENTITY_CHECK`.
- **What genuinely remains new.** A **direct coordinate mapping** of measured RT-DNA onto its own ncRNA, with no inference and no model.
- **Method.** Exact and near-exact alignment of each measured `RTDNA_sequence` to its own element's `ncRNA_sequence`; report start, end, strand, and ambiguity where the match is not unique. **A lookup, not a model.**
- **Baseline / control.** *Positive:* a known published anchor must recover its published coordinates. *Negative:* a shuffled RT-DNA of identical length and composition must **not** map. *Baseline:* a fixed positional prior — because a fixed positional interval has already beaten a learned method 901 to 343 in this project, and it must be kept as a competing arm.
- **Main confounders.** ⛔ **62 of the 81 anchors are measured producers** (verified this session; 77 of 81 carry a measured production value). Anchor-derived features therefore lean on `PANEL-PRODUCERS-67-36`'s positive class — that is decision **D9**, and `T-A22`'s design must be frozen **before** this runs.
- **Success / falsification / bound.** *Success:* unambiguous coordinates for a stated number of the 81. *Falsification:* anchors are ambiguous or absent — a real bound on goal 9 that **closes** `T-A5b2` rather than leaving it open.
- **Interpretation ceiling.** ⛔ **Mapping 81 anchors is not a general model of RT-DNA boundaries.** Generalisation to the 16,458-ncRNA catalogue is `T-A5b2` and is a separate, model-based, currently circular task.
- **Expected output.** `R1b_anchor_coordinates.tsv` · `R1b_ambiguity.tsv` · `R1b_controls.tsv`.
- **Downstream enabled.** `T-A5b2` (gated), `T-A20`, and the external arm of goal 9.
- **Confirmatory spend.** ⛔ **YES — spends `PANEL-RTDNA-81`, one of two irreplaceable measured populations. One explicit authorisation. Merging `T-A5b1` and `T-R1` first is what stops it being spent twice.**
- **Compute.** Local CPU, `CPU_SMALL`, `IO_LOW`. Minutes.
- **Parallel with.** Everything — **except** it must not run before `T-A22`'s design is frozen.
- **Launcher path.** `programme/tasks/T-R1b-rtdna-anchor-mapping/TASK_LAUNCHER.md`.

### 1.4 · `T-A23d-primary-reference-resolution` — **NEW_SCIENCE** (evidence base)

- **Biological question.** What do `SIM2019`'s references 32, 33, 35 and 36 actually report about non-cognate RT–ncRNA function?
- **Why it matters to 1–12.** Goal 12 exists or does not exist on this evidence. Four studies are currently **counted** in the cross-pair base and have never been read; `T-A23c` read four **different, wrong** papers.
- **Why now.** `SIM2019`'s full text — including its bibliography — is already retrieved and correctly identified. The resolution is minutes of work and no compute.
- **Canonical datasets consumed.** `A23C-SOURCES-8`, **the `SIM2019` row only** · `LIT-CROSSPAIR-A23` for context, never as authority.
- **Population / inferential unit.** One published study. n = 4.
- **Prior work available.** `TASK_PRIOR_WORK`: **zero hits on every substrate**. Genuinely `NOT_DONE`.
- **What genuinely remains new.** The **identity** of four references, and whatever each actually reports.
- **Method.** Read the four entries from `SIM2019`'s own reference list; resolve each by author + year + journal + title; retrieve where the licence permits; record unavailability as a finding.
- **Baseline / control.** ⛔ **The control `T-A23c` lacked.** *Positive `IDENTITY`:* a resolved record must match the bibliography on author **and** year **and** journal **and** title; a deliberately mis-specified reference must be **rejected**. *Negative:* a nonsense query returns zero.
- **Main confounders.** A plausible-but-wrong top hit — the exact failure being corrected. **A title match is not an identification.**
- **Success / falsification / bound.** *Success:* four references identified, whether or not obtainable. **An unobtainable primary, recorded as unobtainable, is a successful task with a negative result** and bounds goal 12 honestly.
- **Interpretation ceiling.** ⛔ **No curation row may be re-attributed on a title match. No unmeasured negative pair may be inferred. Stage 12 stays closed** and this task cannot open it.
- **Expected output.** `A23d_reference_identity.tsv` · `A23d_primary_findings.tsv` · `A23d_curation_consequences.tsv` · `A23d_controls.tsv`.
- **Downstream enabled.** `T-A23b`, `T-A23e`, and `T-S12-floor` — the declaration that would make goal 12 well-formed.
- **Confirmatory spend.** None — external population.
- **Compute.** Local, `ZERO`, network, `IO_LOW`.
- **Parallel with.** Everything.
- **Launcher path.** `programme/tasks/T-A23d-primary-reference-resolution/TASK_LAUNCHER.md`.

---

## 2 · CANONICAL_ASSET_CONSTRUCTION — load-bearing

### 2.1 · `T-P1b-identity-partition` — ⭐ **the trunk**

- **Biological question.** Does a cascaded identity partition of the exact-RT catalogue yield groupings that are **not nested inside the pairing inference unit**?
- **Why it matters to 1–12.** Goal 3, and through it goals 4, 6 and 10. **Four inference tasks take a hard dependency on a lineage partition**, and none of them can be posed without one. This is the single highest-leverage asset in the programme.
- **Why now.** `T-P1` is `VOID` and nothing has replaced it. Every downstream inference task is idle behind it.
- **Canonical datasets consumed.** `RT-EXACT-501561` (sha256 verified) · `RT-FAMILY-LABELS-613`.
- **Population / inferential unit.** Exact RT sequence in; **cluster** out — the unit downstream consumes.
- **Prior work available.** 373 content files over 12 roots; `diversity_saturation` carries the mmseqs tooling. **No named anchor**, so absence is weak. `P1-CLUSTERS-VOID` is history and **no number is inherited**.
- **What genuinely remains new.** A partition whose **controls actually gate**, and the cross-component incidence table `T-A0b` needs.
- **Method.** Cascaded identity clustering at a **predeclared** ladder {40, 50, 60, 70, 80, 90, 95} %, on Ibex, with a mandatory 10,000-sequence pilot whose expected result is declared in the launcher.
- **Baseline / control.** All blocking, **all on fixtures, none appended to the primary input**: ① seeded exact duplicates co-cluster ≥ 99/100 — `T-P1` scored **98/100 and called it a pass**; ② shuffled sequences co-cluster 0/100; ③ cluster count non-increasing across **every** adjacent level — `T-P1` failed this at every pair; ④ implementation reproduction against a landed Stage-1 count.
- **Main confounders.** ⛔ **The one that voided `T-P1`** — controls mixed into the primary FASTA change the clustering they measure. Separate invocation, separate files.
- **Success / falsification / bound.** *Success:* a partition with all four controls PASS. ⛔ **A partition that does not cross the inference unit is a VALID NEGATIVE that CLOSES `T-A0b`.** Both outcomes are useful; only a control failure is not.
- **Interpretation ceiling.** ⛔ **An identity partition is not a phylogeny and is not lineage.** The deep tree does not resolve — 312 trees, 157 alignable characters, 1.39 taxa/character — and nothing here changes that.
- **Expected output.** `P1b_pilot_summary.tsv` · `P1b_clusters_id{40…95}.tsv` · `P1b_level_summary.tsv` · `P1b_cross_component_incidence.tsv` · `P1b_controls.tsv`.
- **Downstream enabled.** `T-A0b`, `T-F3`, `T-N2`, `T-P3` — four inference tasks, all currently idle.
- **Confirmatory spend.** None beyond the already-inspected `rt_identity_clustering` endpoint.
- **Compute.** **Ibex CPU.** Pilot `CPU_MEDIUM`; full run `CPU_HIGH`, ~32 CPU / 120 GB. ⚠️ `batch` shows **7 idle nodes** — expect to queue. Staging is local `IO_MEDIUM` and is declared.
- **Parallel with.** Everything — it is the only Ibex candidate.
- **Launcher path.** `programme/tasks/T-P1b-identity-partition/TASK_LAUNCHER.md`.
- **⛔ Two authorisations.** Pilot first; the full run is a **separate go/no-go** after the pilot's controls report. Also needs **D12**.

### 2.2 · `T-N1d-neighbourhood-census` — blocked on **D2**

- **Biological question.** What is the CDS-neighbourhood geometry of RT-bearing records, with edge state retained rather than filtered?
- **Why it matters to 1–12.** Goal 6, and it feeds `T-A10` and `T-N2`. The extraction has **never landed a primary table under a passing control**.
- **Why now.** Only the blocking criterion is missing. Once settled, the run is minutes.
- **Canonical datasets consumed.** `RT-WINDOW-CDS` (44,310,231 CDS — ⚠️ **needs a hash before consumption**) · `RT-RECORDS-3059700`.
- **Population / inferential unit.** **Raw source record**, declared as such. ⛔ **Not `RETRON-LOCI`** — that misdeclaration failed `T-N1`.
- **Prior work available.** 601 content files over 13 roots, **anchor control PASS**, so absence here is reportable. Three executed attempts are recorded as `N1-N1B-N1C-VOID`.
- **What genuinely remains new.** The census itself, under a criterion that can actually fail for the right reason.
- **Method.** Same locator — three passing controls show it works. Per record: neighbour count, gap distances, window span, clipping flag, contig-edge distance, and zero-neighbour split into `EDGE_CLIPPED_ZERO` vs `TRUE_ZERO_NEIGHBOUR` with the edge-clipping denominator reported.
- **Baseline / control.** ⛔ **This is decision D2.** *Implementation, blocking:* exact known-coordinate fixtures, strand fixtures, off-by-one fixtures, contig-edge fixtures, deliberately wrong-anchor fixtures, reproduction of landed examples. *Descriptive, reported and NOT gated:* tight-window frequency, edge clipping, neighbour-count distribution, family architecture, **and the observed ≈0.285 null rate**.
- **Main confounders.** ⛔ **Population-derived architecture forced to satisfy an arbitrary ceiling in order to validate the locator.** That has now happened three times.
- **Success / falsification / bound.** *Success:* a landed census with implementation controls PASS. The null rate is a **measured property**, not a pass condition.
- **Interpretation ceiling.** ⛔ **Description only.** Neighbourhood as a retron detector is a **settled negative** — retrons 27th of 41 families inside a predeclared dead band. This does not reopen it.
- **Expected output.** `N1d_neighbourhood_per_record.tsv` · `N1d_qa_breakdown.tsv` · `N1d_summary.tsv` · `N1d_controls.tsv`.
- **Downstream enabled.** `T-A10`, `T-N2`.
- **Confirmatory spend.** None.
- **Compute.** Local CPU, `CPU_MEDIUM`, **`IO_HIGH`**.
- **Parallel with.** Everything except the other `IO_HIGH` tasks.
- **Launcher path.** `programme/tasks/T-N1d-neighbourhood-census/TASK_LAUNCHER.md`.
- ⛔ **No fourth ceiling derived from already-observed data and called preregistered.** If a quantitative threshold is still wanted, it is calibrated **independently**, before the run.

### 2.3 · `T-M1b-embedding-cache-reverification`

- **Biological question.** What are the cached embeddings actually *of*?
- **Why it matters to 1–12.** Goals 10 and 11 read these caches. **`rt_positives_emb` is ncRNA positive-region embeddings, not RT embeddings** — anything treating it as RT is measuring the wrong molecule.
- **Why now.** It is an unapplied `ACCEPT_WITH_CHANGES`, and the misidentification is load-bearing.
- **Canonical datasets consumed.** `EMBED-CACHES-26016` (⚠️ `NEEDS_REDERIVATION`, **no file hashed**).
- **Population / inferential unit.** One `.npy` cache file. No biological population.
- **Prior work available.** 461 content files, 12 roots, no anchor; 42.4 GB of `.npy` in the asset sweep. `ASSET_ONLY`.
- **What genuinely remains new.** Provenance-verified **identity** per collection, plus a hash per file.
- **Method.** Resolve each collection's identity from **upstream provenance, never from its directory name**; recompute norms in float32/64; land all 4,000 sampled rows; hash every cache file.
- **Baseline / control.** *Positive:* reproduce `T-M1`'s counts exactly — 13,214 / 12,802, dim-1280 coverage 1.0000 (implementation reproduction). *Negative:* a synthetic float16-overflow fixture gives `inf` under the old method and finite norms under the new.
- **Main confounders.** Collection names asserting a provenance the files do not have — the defect being fixed.
- **Success / falsification / bound.** *Success:* every collection carries a verified identity and a hash. *Falsification:* a **second** misidentified collection, which would make the whole cache register unreliable — an important negative.
- **Interpretation ceiling.** ⛔ Verifying a cache says nothing about whether its embeddings are useful. **No pairing claim follows.**
- **Expected output.** `M1b_collections.tsv` (with `identity_provenance`) · `M1b_file_hashes.tsv` · `M1b_sampled_rows.tsv` (all 4,000) · `M1b_controls.tsv`.
- **Downstream enabled.** `T-A1`, `T-A2b`, `T-M2`.
- **Confirmatory spend.** None.
- **Compute.** Local CPU, `CPU_SMALL`, **`IO_HIGH` — serial against `T-S1b`**.
- **Launcher path.** `programme/tasks/T-M1b-embedding-cache-reverification/TASK_LAUNCHER.md`.

### 2.4 · `T-S1b-structure-inventory-correction`

- **Biological question.** How many **unique structures**, as opposed to files on disk, does the estate hold?
- **Why it matters to 1–12.** Goal 5's evidence base is currently quoted as 44,608 — a **file** count. The real number of independent structural evidence items is unknown.
- **Why now.** Unapplied `ACCEPT_WITH_CHANGES`, and `T-REG3` independently showed that **name+size is not content identity** (602 shared-pin groups, **357 content-distinct**).
- **Canonical datasets consumed.** `PRED-STRUCT-44608` (⚠️ `NEEDS_REDERIVATION`).
- **Population / inferential unit.** One structure file, and separately one **unique structure**.
- **Prior work available.** 919 content files over 13 roots, no anchor; `structure_prediction_assets` 1,897; `foldseek_structural` 1,534. `ASSET_ONLY`.
- **What genuinely remains new.** A **file-level** missing check and a **unique-structure** count with its deduplication rule declared in advance.
- **Method.** Re-scan all 97 collections; declare the identity rule; report four denominators separately — files, unique structures, missing files, bytes. **Never pooled.**
- **Baseline / control.** *Positive:* reproduce all 97 name-and-size manifest hashes. *Negative:* run the scanner against a **synthetic absent path** and require it to report missing — the control `T-S1` never ran.
- **Main confounders.** The same chain deposited under several accessions inflates "unique". The rule is declared **before** the count.
- **Success / falsification / bound.** *Success:* four denominators, each with its rule. *Falsification:* unique structures far below 44,608, materially shrinking goal 5's evidence base — a useful negative.
- **Interpretation ceiling.** ⛔ An inventory is not evidence about structure. It bounds what could be analysed.
- **Expected output.** `S1b_collections.tsv` · `S1b_unique_structures.tsv` · `S1b_missing_files.tsv` · `S1b_controls.tsv`.
- **Downstream enabled.** `T-S2` (once its metric is declared — **D10**), `T-S3`.
- **Confirmatory spend.** None.
- **Compute.** Local CPU, `CPU_SMALL`, **`IO_HIGH` — serial against `T-M1b`**.
- **Launcher path.** `programme/tasks/T-S1b-structure-inventory-correction/TASK_LAUNCHER.md`.

---

## 3 · REPRODUCTION_REQUIRED — skim

### 3.1 · `T-AUDIT2-task-report-backfill`

Writes a `WORKING_RULES` §5 `TASK_REPORT.md` for each of the 13 executed tasks. **No task in this project has one**, which is why *"none is consumable"* and why `T-GATE1` has nothing to read. Transcribes only — recomputes nothing, promotes nothing, decides nothing. *Positive control:* a task known to have failed a blocking control (`T-N1c`) must emerge with an **empty** consumable list. `ZERO`, local, parallel with everything. Prior work: **zero hits, genuinely `NOT_DONE`**.

**No `THESIS_CORRECTION_ONLY` task is proposed.** The two corrections this session found — the `T-A23c` source-identity erratum and the `T-C1b` naming repair — are already landed as errata and need no task.

---

## 4 · Goals 1–12 — does this still look like your project?

| goal | current status | strongest existing evidence | next necessary task | start now? | dependency |
|---|---|---|---|---|---|
| **1** large-scale RT/retron resource | **substantially done, unpromoted** | 501,561 exact RTs, sha256-verified; 3,059,700 raw records; 613 families; full unit discipline | `T-D1`, `T-D2` | **yes** | none |
| **2** RT0–RT7 / core definition | **Stage 2 CLOSED with residual limits** | `G5-MAPPED-369381`, 55.4 M state calls, hashes verified; `C1B-ENVELOPES-501561` 0.865875 across 613 families | review `T-C1b`; then `T-A16` | review **yes**; A16 needs a spec | RT0/RT1 remain UNRESOLVED |
| **3** relatedness / phylogenetic structure | ⛔ **trunk empty — `T-P1` VOID** | bounded negative: 312 trees, 157 alignable characters, 1.39 taxa/char — the deep tree **does not resolve** | **`T-P1b`** | needs **D12** | the whole of goals 4, 6, 10 inference waits here |
| **4** retron RT features / motifs / fusions | **preparation done, unreviewed** | `T-F1`: 380,948/501,561 YxDD (0.7595), 98.87 % inside the envelope, chance 0.0784 | review `T-F1`; then `T-F2` | review **yes** | `T-F3` needs `T-P1b` |
| **5** structural analysis | **inventory only, denominators wrong** | 97 collections / 44,608 **files** — not unique structures | `T-S1b`, then `T-S2` | `T-S1b` **yes** | `T-S2` needs **D10** (metric + threshold); foldseek **is** installed |
| **6** genomic neighbourhood / architecture | ⛔ **three VOID attempts; locator proven** | discrimination 0.715 vs floor 0.50; anchor uniqueness 3,028,196/3,028,196 | **`T-N1d`** | needs **D2** | neighbourhood-as-detector is a **settled negative** |
| **7** evolutionary correspondence | ⛔ **CLOSED_CURRENT_EVIDENCE** | bounded by 157 alignable characters | `T-E1` character-source probe | needs **D11** (predeclare "materially exceeding 157") | reopening is an operator decision |
| **8** ncRNA discovery | ⛔ **CLOSED_CURRENT_DESIGN** | a fixed positional interval beats the method **901 to 343**; per-type priors reach 969 | `T-C2` inventory | **yes** (inventory only) | `S07` needs **five** declared conditions, not one |
| **9** ncRNA architecture / RT-DNA anchors | **unexposed, strongest anchor intact** | `PANEL-RTDNA-81`, 81 verified, never a training target | **`T-R1b`** | needs **D7** | 62 of 81 overlap `T-A22`'s positives (**D9**) |
| **10** RT–ncRNA embedding / pairing | ⚠️ **population EXHAUSTED permanently** | `PAIR-ELIG-30924` / 1,075 components; effective n ≈ 463 | `T-M1b`, then `T-A1` | `T-M1b` **yes** | **no confirmatory pairing claim is possible** without a new declared population |
| **11** integrative modelling | **not started, correctly** | — | none until components survive controls | **no** | needs goals 3, 5, 9 signals first |
| **12** orthogonality / compatibility | ⛔ **floor never declared; gate not well-formed** | **7 experimental blocks**, not 56 rows; **zero** numeric values; only **two** native non-cognate functional examples | **`T-A23d`** | **yes** | `T-S12-floor` is a declaration, i.e. a decision |

**Reading of this table, plainly.** Goals 1, 2 and 4 have real substance and need **review**, not more computation. Goal 3 is the bottleneck and one task fixes it. Goals 7, 8 and 12 are honestly bounded and their reopening conditions are written down. Goals 9 and 10 hold the project's only irreplaceable measured populations, one intact and one spent. Goal 11 has correctly not started.

⚠️ **The one thing the repository has drifted toward** is auditing rather than measuring. Five of the nine proposals above are asset construction or reproduction. That is the right *next* step given three VOIDs, but if the wave after this one is not dominated by `NEW_SCIENCE`, the programme has become its own subject.

---

## 5 · Proposed first parallel wave — **not launched**

Maximum sensible concurrency. Nothing here consumes an unexposed confirmatory population.

| backend | tasks | concurrency |
|---|---|---|
| **local CPU** | `T-D1` · `T-D2` · `T-AUDIT2` · `T-A23d` | **4 concurrent** — all `IO_LOW`/`IO_MEDIUM` |
| **local CPU, `IO_HIGH` lane** | `T-M1b` **then** `T-S1b` | **1 at a time** — one NVMe, strictly serial |
| **local GPU** | ⛔ **nothing** | 2 × RTX 4090 idle. **No proposed task needs a GPU** — say so rather than inventing work for them. Embedding *regeneration* would; `T-M1b` is verification |
| **Ibex CPU** | `T-P1b` **pilot only** (10,000 sequences) | **1** — the full run is a separate authorisation |
| **Ibex GPU** | ⛔ **nothing** | no proposed task needs it |
| **Codex review** | `T-C1b` · `T-A23c` · `T-F1` · `T-REG3` | **4 concurrent** — read-only, model-disjoint threads |

**Total: 10 concurrent streams, 4 of them review.**

⛔ **Not in the wave, and why:** `T-N1d` (blocked on **D2** — scheduling it would schedule a decision) · `T-R1b` (blocked on **D7**, and `T-A22`'s design must freeze first) · `T-P1b` full run (separate authorisation after the pilot) · everything touching `STRUCT-62` Tier B (**D8**).

⭐ **The Codex lane is free throughput.** Four executed tasks have never been reviewed; it costs no compute, no population and no decision beyond dispatch. If you approve nothing else, approve that.

⚠️ **The dispatch blocker still stands** (**D4**): the host refuses to spawn a task session, so today this wave runs only via manual `bash programme/launch_task.sh <task-id>` per task, or with the coordinator executing under disclosure.
