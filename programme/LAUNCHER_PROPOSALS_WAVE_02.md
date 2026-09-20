---
record: LAUNCHER_PROPOSALS_WAVE_02
date: 2026-09-20
author: reconciliation session
status: PROPOSALS — none written as a TASK_LAUNCHER, none frozen, none executed
gate: operator review required before any is written or dispatched
---

# Wave 02 — proposed launchers, for operator review

**Nothing here is a launcher yet.** The operator asked to review the proposed scientific work
before the next wave begins. These are the review blocks; the `TASK_LAUNCHER.md` files are written
**after** approval, and frozen with their implementation in one commit before any run
(`WORKING_RULES` §6b).

---

## 0 · Readiness classification of the whole register

| class | tasks |
|---|---|
| **`READY_FOR_OPERATOR_REVIEW`** — proposed below | `T-AUDIT2` · `T-M1b` · `T-S1b` · `T-A23d` · `T-P1b` |
| **`READY_AFTER_NAMED_DEPENDENCY`** | `T-GATE1` (after `T-AUDIT2`) · `T-A0b` (after `T-P1b`, **and** a multiway design) · `T-F3`, `T-N2` (after `T-P1b`) · `T-A17` (after `T-A16`) · `T-S3` (after `T-S2` **and** `T-A7`) |
| **`READY_WAITING_OPERATOR_POPULATION`** | `T-A5b1`/`T-R1` (**merge or differentiate first**) · `T-A22` · `T-A7` · `T-A19` · `T-C1` successor work on `RT-EXACT` |
| **`ALREADY_DONE_NEEDS_AUDIT`** — review costs nothing and blocks nothing | `T-F1` · `T-REG3` · `T-C1b` · `T-A23c` |
| **`HELD`** — needs a number or a design declared in advance, which **is** the decision | `T-N1d` (control design) · `T-S2` (metric + threshold) · `T-A16` · `T-A1` · `T-A6` · `T-A10` · `T-A2b` · `T-A3a` · `T-E2` · `T-I1` · `T-S12-floor` · `T-LINT3` · `T-LINT5` |
| **`CLOSED_CURRENT_DESIGN`** — reopening conditions in `SCIENTIFIC_DAG.md` §6, **unchanged** | `S09` coevolution · `S07` de novo ncRNA discovery · palm/fingers/thumb partition · 11-clade placement · neighbourhood-as-detector |

⛔ **Nothing below reopens a closed branch.** `T-N1d` describes neighbourhood *geometry*; it is not
a neighbourhood *detector* and does not touch that settled negative.

---

## 1 · `T-AUDIT2-task-report-backfill`

| field | value |
|---|---|
| **question** | Does a `WORKING_RULES` §5-conformant `TASK_REPORT.md` exist for any executed task, and what does each landed artifact actually support? |
| **why now** | Review `01a0bdfa`: *"None consumable: no `TASK_REPORT.md` anywhere."* Until reports exist, **every artifact from a self-labelled PASS task is consumable regardless of whether the PASS was earned.** `T-GATE1` cannot be built on nothing. |
| **population** | none |
| **inferential unit** | one executed task |
| **prior work found** | `TASK_PRIOR_WORK_SUMMARY`: `n_roots_with_hits = 0` on every substrate. **`NOT_DONE`**, `WEAK — no anchor`. Independently consistent with the review finding. |
| **what is reused** | the landed tables, logs and control tables of all 13 executed tasks |
| **what is independently rederived** | nothing — it transcribes, it does not recompute |
| **endpoint** | one `TASK_REPORT.md` per executed task, each with both §5 fields, its criterion verbatim, its controls, and an explicit `CONSUMABLE_OUTPUTS` list that is **empty** wherever the task is VOID or unreviewed |
| **controls / baselines** | **positive:** a task known to have failed a blocking control (`T-N1c`) must emerge with an empty consumable list. **negative:** a report may not be generated for a task with no landed outputs |
| **confounders** | the temptation to promote while transcribing. The task writes reports; it **decides nothing** |
| **success / falsification** | success = 13 reports, each traceable to landed files. Falsification = a task whose artifacts cannot support any §5 report, which is itself the finding |
| **interpretation ceiling** | ⛔ **A report is not a promotion.** Writing one changes no board state and clears no review |
| **confirmatory spend** | none |
| **dependencies** | none. `DATA_DEPENDENCY` **onto** `T-GATE1` |
| **compute / backend** | `ZERO`, local, `IO_LOW` |
| **may run in parallel with** | everything in this document |
| **expected outputs** | `programme/tasks/<id>/TASK_REPORT.md` ×13 · `AUDIT2_report_index.tsv` · `AUDIT2_controls.tsv` |

## 2 · `T-M1b-embedding-cache-reverification`

| field | value |
|---|---|
| **question** | What are the embedding caches actually of, and do their norms and coverage hold when computed correctly? |
| **why now** | `T-M1` is `ACCEPT_WITH_CHANGES` with four changes unapplied, and one is a **misidentification**: `rt_positives_emb` is ncRNA positive-region embeddings, **not RT embeddings**. Goal 10 and every pairing follow-up would read it as RT |
| **population** | none — file identity only |
| **inferential unit** | one `.npy` cache file |
| **prior work found** | `TASK_PRIOR_WORK`: 461 content files over 12 roots, **no named anchor** so absence is weak. `embeddings` topic: 7,584 content files plus 42.4 GB of `.npy` in the asset sweep. **`ASSET_ONLY`** |
| **what is reused** | the 26,016 existing `.npy` files; `T-M1`'s collection list |
| **what is independently rederived** | **every quantity.** Norms in float32/64 (`T-M1`'s were `inf` from float16 overflow), coverage, dimension, and the provenance of each collection's name |
| **endpoint** | per-collection identity (**what the vectors are of**), sha256 per cache file, finite-norm statistics, coverage at dimension 1280 |
| **controls / baselines** | **positive:** re-derive `T-M1`'s reproduced counts (13,214 / 12,802, dim 1280 coverage 1.0000) exactly — an implementation-reproduction control, the preferred kind. **negative:** a synthetic float16-overflow fixture must produce `inf` under the old method and finite norms under the new |
| **confounders** | collection names asserting a provenance the files do not have. Identity is resolved from **upstream provenance**, never from the directory name |
| **success / falsification** | success = every collection carries a provenance-verified identity and a hash. Falsification = a second misidentified collection, which would make the whole cache register unreliable |
| **interpretation ceiling** | ⛔ **Verifying a cache says nothing about whether its embeddings are useful.** No pairing claim follows |
| **confirmatory spend** | none |
| **dependencies** | `DATA_DEPENDENCY:T-REG` |
| **compute / backend** | `CPU_SMALL`, local, **`IO_HIGH` — serial against `T-S1b`** |
| **may run in parallel with** | lanes A, C, D. **Not** with `T-S1b` |
| **expected outputs** | `M1b_collections.tsv` (with `identity_provenance`) · `M1b_file_hashes.tsv` · `M1b_sampled_rows.tsv` (**all 4,000, not 100**) · `M1b_controls.tsv` |

## 3 · `T-S1b-structure-inventory-correction`

| field | value |
|---|---|
| **question** | How many **unique structures**, as opposed to files on disk, does the estate hold, and is "0 missing" a statement about files or directories? |
| **why now** | `T-S1` is `ACCEPT_WITH_CHANGES`. Its three defects are all denominator defects: "0 missing" means **zero missing directories**; 44,608 is **files**, not unique structures or independent evidence items; the absent-path negative never ran the scanner against a synthetic path |
| **population** | none |
| **inferential unit** | one structure file, and separately one **unique structure** |
| **prior work found** | `TASK_PRIOR_WORK`: 919 content files over 13 roots, **no named anchor**. `structure_prediction_assets` 1,897 files; `foldseek_structural` 1,534. **`ASSET_ONLY`** |
| **what is reused** | `T-S1`'s 97 collections, independently rescanned and already confirmed to match exactly |
| **what is independently rederived** | the **file-level** missing check, and a **unique-structure** count with its deduplication rule stated |
| **endpoint** | files on disk; unique structures under a declared identity rule; missing **files**; bytes — four separate denominators, never pooled |
| **controls / baselines** | **positive:** reproduce all 97 name-and-size manifest hashes. **negative:** run the scanner against a **synthetic absent path** and require it to report missing — the control `T-S1` never ran |
| **confounders** | the same chain deposited under several accessions inflates "unique". The identity rule is declared before the count |
| **success / falsification** | success = four denominators, each with its rule. Falsification = unique structures far below 44,608, which would materially shrink the structural evidence base — a useful negative |
| **interpretation ceiling** | ⛔ **An inventory is not evidence about structure.** It bounds what could be analysed |
| **confirmatory spend** | none |
| **dependencies** | `DATA_DEPENDENCY:T-REG` |
| **compute / backend** | `CPU_SMALL`, local, **`IO_HIGH` — serial against `T-M1b`** |
| **may run in parallel with** | lanes A, C, D. **Not** with `T-M1b` |
| **expected outputs** | `S1b_collections.tsv` · `S1b_unique_structures.tsv` · `S1b_missing_files.tsv` · `S1b_controls.tsv` |

## 4 · `T-A23d-primary-reference-resolution`

| field | value |
|---|---|
| **question** | What do `SIM2019`'s references 32, 33, 35 and 36 actually report — read from the **correct** primaries, identified from `SIM2019`'s own bibliography? |
| **why now** | `T-A23c` resolved all four by keyword match on invented titles and returned **four 2026 papers as references of a 2019 review** (`ERRATUM_01`). Four studies counted in the cross-pair evidence base have still never been read, and **no control asserted record identity** |
| **population** | `LIT-CROSSPAIR`, external — never a project population |
| **inferential unit** | one published study |
| **prior work found** | `TASK_PRIOR_WORK`: `n_roots_with_hits = 0` on every substrate. **`NOT_DONE`**. The four primaries have never been read at first hand in this estate |
| **what is reused** | `SIM2019`'s **retrieved full text**, including its reference list — already on disk from `T-A23c` and correctly identified by DOI `10.1093/nar/gkz865` |
| **what is independently rederived** | the identity of all four references, and whatever each actually reports |
| **endpoint** | per reference: the identifiers as `SIM2019` lists them, the resolved record, an **identity verdict**, availability, and what the primary states about non-cognate RT–ncRNA function |
| **controls / baselines** | ⛔ **the control `T-A23c` lacked.** **positive `IDENTITY`:** a reference resolved from the bibliography must match on **author + year + journal + title**, not title alone; a deliberately mis-specified reference must be **rejected**. **negative:** a nonsense query returns zero |
| **confounders** | a plausible-but-wrong top hit — the exact failure being corrected. **A title match is not an identification** |
| **success / falsification** | success = four references identified and verified, whether or not their text is obtainable. **An unobtainable primary recorded as unobtainable is a successful task with a negative result** |
| **interpretation ceiling** | ⛔ **No row of the `T-A23` curation may be re-attributed on a title match.** No unmeasured negative pair may be inferred. **Stage 12 stays closed** and this task cannot open it |
| **confirmatory spend** | none — external population |
| **dependencies** | `DATA_DEPENDENCY:T-A23c` (its retrieved `SIM2019` full text **only**) |
| **compute / backend** | `ZERO`, local, network, `IO_LOW` |
| **may run in parallel with** | everything |
| **expected outputs** | `A23d_reference_identity.tsv` · `A23d_primary_findings.tsv` · `A23d_curation_consequences.tsv` · `A23d_controls.tsv` |

## 5 · `T-P1b-identity-partition` — **two-stage authorisation**

| field | value |
|---|---|
| **question** | Does a cascaded identity partition of the exact-RT catalogue produce groupings that are **not nested inside the pairing inference unit**? |
| **why now** | It is the trunk. Four inference tasks take a `HARD_SCIENTIFIC_DEPENDENCY` on a lineage partition, and `T-P1` is `VOID` — its four declared blocking controls **were never implemented as gates**, two never ran, and the controls were **appended to the primary input**, changing the clustering they were meant to check |
| **population** | `RT-EXACT-501561`, `analysis_family = rt_identity_clustering`, **`INSPECTED_FOR_THIS_ENDPOINT`** — already spent by `T-P1` even though `T-P1` is void (operator ruling §1) |
| **inferential unit** | one exact RT sequence; the **cluster** is the unit the downstream design consumes |
| **prior work found** | `TASK_PRIOR_WORK`: 373 content files over 12 roots, 30 table headers, **no named anchor** — absence is weak. `diversity_saturation` carries the mmseqs tooling. **`FAILED_CURRENT_DESIGN`** (T-P1) |
| **what is reused** | the Stage-1 catalogue and the declared identity ladder {40, 50, 60, 70, 80, 90, 95} % |
| **what is independently rederived** | **everything.** No number from `T-P1` is inherited — it is void, and `ERRATUM_01` was itself false |
| **endpoint** | a cluster assignment per sequence at each level; per-level cluster counts; and the **cross-component incidence table** that `T-A0b` needs |
| **controls / baselines** | **all blocking, all on fixtures, none appended to the primary input.** ① seeded exact duplicates co-cluster at ≥ 99/100 — `T-P1` scored **98/100 and reported a pass**; ② shuffled sequences co-cluster at 0/100; ③ monotonicity: cluster count is non-increasing across **every** adjacent level — `T-P1` failed this at every pair; ④ implementation reproduction against a landed Stage-1 count |
| **confounders** | ⛔ **the one that voided `T-P1`** — controls mixed into the primary FASTA change the clustering. Controls run in a **separate invocation on separate files**, per operator ruling §3 |
| **success / falsification** | success = a partition with all four controls PASS. ⛔ **A partition that does *not* cross the inference unit is a valid negative that CLOSES `T-A0b`** rather than leaving it open. Both outcomes are useful; only a control failure is not |
| **interpretation ceiling** | ⛔ **An identity partition is not a phylogeny and is not lineage.** The deep tree does not resolve — 312 trees, 157 alignable characters, 1.39 taxa/character — and nothing here changes that |
| **confirmatory spend** | none beyond the already-inspected endpoint |
| **dependencies** | `DATA_DEPENDENCY:Stage1`. ⛔ **Also an operator ruling** (`ERRATUM_02`): may a full-catalogue clustering inform a lineage design at all, given that components hold multiple RT lineages? |
| **compute / backend** | **Stage 1 — pilot:** 10,000 sequences, `CPU_MEDIUM`, Ibex, expected result declared in the launcher. **Stage 2 — full:** `CPU_HIGH`, Ibex, ~32 CPU / 120 GB. ⚠️ `batch` currently shows **7 idle nodes**; expect to queue. Staging the catalogue is local `IO_MEDIUM` and is declared |
| **may run in parallel with** | everything else here — it is the only Ibex candidate |
| **expected outputs** | `P1b_pilot_summary.tsv` · `P1b_clusters_id{40,50,60,70,80,90,95}.tsv` · `P1b_level_summary.tsv` · `P1b_cross_component_incidence.tsv` · `P1b_controls.tsv` |

> **Two authorisations, not one.** The pilot is cheap and its expected result is declared in
> advance. **The full run is a separate go/no-go** taken after the pilot's controls report.

## 6 · `T-N1d-neighbourhood-census` — **blocked on a decision, not on a task**

| field | value |
|---|---|
| **question** | What is the CDS-neighbourhood geometry of RT-bearing records, with edge state retained rather than filtered? |
| **why now** | The extraction has never landed a primary table under a passing control, and it feeds `T-A10` and `T-N2`. **Three null designs have failed and the fourth must not be invented by the coordinator** |
| **population** | `RT-RECORDS-ALL-FAMILIES`, `analysis_family = neighbourhood_geometry`, **`INSPECTED_FOR_THIS_ENDPOINT`**. ⛔ **Not `RETRON-LOCI`** — that misdeclaration is what failed `T-N1` |
| **inferential unit** | one **raw source record**. ⛔ Rows are **not** independent loci; `locus_key` and `physical_locus_key` are landed so a consumer can collapse them |
| **prior work found** | `TASK_PRIOR_WORK`: 601 content files over 13 roots, **named anchor PASS (3 hits)**, so absence here is **reportable**. `genomic_neighbourhood` 22,348 files. **`FAILED_CURRENT_DESIGN`** for the control; the extraction itself is `NOT_DONE` |
| **what is reused** | `rt_window_cds_v1.parquet`, 44,310,231 CDS rows; the locator, which three controls show works |
| **what is independently rederived** | the full census and its controls |
| **endpoint** | per record: neighbour count, gap distances, window span, clipping flag, contig-edge distance, and zero-neighbour split into **`EDGE_CLIPPED_ZERO`** vs **`TRUE_ZERO_NEIGHBOUR`** with the edge-clipping denominator reported |
| **controls / baselines** | ⛔ **This is the operator decision.** **Implementation / blocking** — exact known-coordinate fixtures, strand fixtures, off-by-one fixtures, contig-edge fixtures, deliberately incorrect-anchor fixtures, reproduction of landed examples. **Descriptive, reported and NOT gated** — tight/short-window frequency, edge clipping, neighbour-count distribution, family-specific architecture, and the observed **≈0.285** null rate |
| **confounders** | ⛔ **population-derived architecture forced to satisfy an arbitrary ceiling in order to validate the locator.** That is what happened three times |
| **success / falsification** | success = a landed census with implementation controls PASS. The null rate is a **measured property**, not a pass condition |
| **interpretation ceiling** | ⛔ **Description only.** Neighbourhood as a retron detector is a **settled negative** — retrons 27th of 41 families, inside a predeclared dead band. This task does not reopen it |
| **confirmatory spend** | none |
| **dependencies** | ⛔ `CONTROL_DEPENDENCY` on an **operator control-design ruling** — `ESCALATION_01` options **A** (margin is the criterion, null reported), **B** (ceiling from the actual `L`/`W` distributions), **C** (a different null entirely). The escalating session recommends **A** and declines to choose |
| **compute / backend** | `CPU_MEDIUM`, local, `IO_HIGH` |
| **may run in parallel with** | lanes A, C, D — **not** with `T-M1b` / `T-S1b` |
| **expected outputs** | `N1d_neighbourhood_per_record.tsv` · `N1d_qa_breakdown.tsv` · `N1d_summary.tsv` · `N1d_controls.tsv` |

⛔ **No new pass threshold may be derived from the already-observed data and then treated as
preregistered.** If a quantitative blocking threshold is still required, it is calibrated
**independently** before the run.

---

## 7 · Specification requests — not launchers, because the missing piece is a number

| task | what is actually missing |
|---|---|
| `T-S2-foldseek-calibration` | **foldseek is installed** (v10.941cd33, two local envs, registered at `data/README.md` L182 and L194). The only blocker is that **no metric and no threshold are declared**. Declaring them is the scientific decision |
| `T-A5b1` / `T-R1` | **the same task** — both map the 81 empirical RT-DNA sequences directly. Merge, or define a genuinely distinct artifact, **before either spend**. And **62 of 81 anchors are measured producers**, overlapping `T-A22`'s positive class |
| `T-A7` / `T-S3` | both would spend `STRUCT-62` Tier B — one as control, one as headline. The independent spec names **HIV-1 p66 and externally partitioned RTs** as the positive; returning to those dissolves the conflict |
| `T-A19` | scores a **CM-derived caller against CM-derived calls**. Reportable as a same-paradigm implementation diagnostic only, and it is **one of five** `S07` reopening conditions |
| `T-E1` / `T-E2` | *"materially exceeding 157 alignable positions"* must be a number fixed **in advance**, or `T-E1` cannot classify its own result |
| `T-A3a`, `T-I1`, `T-S12-floor` | each requires declaring an increment, a floor or a rule **in advance** — the declaration **is** the decision |
