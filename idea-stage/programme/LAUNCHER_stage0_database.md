# LAUNCHER — Stage 0 · Database characterization


## Environment
```bash
conda activate retron_tradicional        # never base
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
# Ibex jobs: conda env /ibex/user/rioszemm/conda-environments/retron_tradicional; never base.
```
---

Project root`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK` and task ID: `stage0_database_characterization` 

## Read first
1. `/home/borg/RESEARCH-in-sleep-GENERAL_v3/CLAUDE.md`
1. `/home/borg/RESEARCH-in-sleep-GENERAL_v3/WORKING_AGREEMENT.md`


---

## Scientific context
I have assembled and deployed a large-scale pipeline for the discovery and annotation of reverse transcriptases (RTs) from eight public databases: `gtdb_bacteria`, `gtdb_archaea`, `ncbi_bacteria`, `ncbi_archaea`, `mgnify_human_gut`, `mgnify_marine`, `mgnify_soil`, and `gem`. The pipeline uses three complementary sequence-based tools (all with their own hidden markov model profiles HHMs and synteny rules) to maximize sensitivity:

- **DefenseFinder** — bacterial phage defense system detector, used here to detect retrons specifically
- **PADLOC** — also a defense system locator, used here to detect retrons specifically; importantly provides ~21 covariance models (CMs) built with Infernal to detect retron ncRNAs. CM matches were provided not only for RT matches from PADLOC but across tools and across RT families.
- **MyRT** — detects all RT families (including retrons).

Each tool provides its own HMM profiles for protein detection. PADLOC's retron CMs were used with Infernal to scan intergenic regions; any ncRNA match within ±10 kbp of an RT hit (regardless of RT family label) was retained in the system record.

**Pipeline output:** One JSON object per system, containing:
- Prodigal metadata for all CDS and intergenic regions within ±10 kbp of the RT, genomic window expanded if needed or truncated if not enough data.
- Identity labels for the RT and ncRNA (where detected)
- No functional annotation for other coding regions (accessory proteins are currently unlabeled)
- Other metadata content explained @//home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK/MELISSA_DATA/templates/input_format_schema_only.md, @/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK/MELISSA_DATA/MELISS_SCRIPTS/utils_FOR_ALL_FILES.py has some useful functions already to manipulate the data under class PipelineData, use as starting point if needed.

Retrons are special type of RTs that are transcribed in the same operon with its RNA substrate, a distinctive trait compared to other RTs.

---

## 0 · The point of this task

Characterize the screening database and surface the most striking, defensible descriptive insights — the foundation later stages and the paper will build on. Decide WHAT is worth reporting (per database, per RT family, per ncRNA CM, per domain Archaea/Bacteria, and across databases), compute it efficiently, then interpret. Descriptive + anomaly-flagging only. This stage should also be the one producing datasets for downstream tasks (not addressed here) and propose a way to pull them, for example: which flags or data features shall be considered during the dataset construction. For example, I need a dataset for RT-ncRNA unique pairs (example of downstream task: study co-evolution of elements; multiple ncRNAs per RT or viceversa has to be resolved or appropiateley flagged/reported), unique RTs (exact RT string deduplication; how to handle if same RT is present across different taxa), and unique locus (what makes a unique locus and why it is important to consider when doing genomic neighborgood analysis around the RT).

---

## Read first (context — do not modify any of these)
- `@MELISSA_DATA/supporting_material/report_ncbi_bacteria_Bacteria.html` — example
  report. Decide what to carry over vs. the PREVIOUS_ARIS_WORK report; don't invent
  a third style.
- `@templates/input_format_schema_only.md` — MANDATORY. Data content and structure, file sizes,
  entry counts per system (RT family, and ncRNA-only anchor systems), schema,
  per-file rules, genome-ID normalization. This is the overview of the large-scale
  public-database mining output. Read the notes in it.
- `@supporting_material/databases_metadata_files`  — 8 files | taxonomy join tables per `source_database`.

---

## Approach (section-based; compute then interpret)

### Step 1 — Recon (facts only, no analysis)

> **Note to ARIS:** Treat all scripts as starting points. They may have issues with structure, efficiency, methodology, or correctness. Review them, propose improvements, and implement improved versions in `ARIS_OUTPUT/` — never edit the originals.

### Step 2 — Propose report SECTIONS (PLAN — wait for approval)

### Step 3 — Compute sections (Phase A: numbers only)

### Step 4 — Interpret (Phase B: one round over all numbers)

### Step 5 — Assemble & close


## Execution protocol — work phase by phase, report incrementally, stop for approval


---


## Compute


---


## Stop condition


---

## Required outputs → ARIS_OUTPUT/stage0_database_characterization/
- cache/   — intermediate streamed tables (reusable by later stages)
- scripts/ — one script per section + the assembler
- figures/ — PNG + EPS + SVG per figure
- tables/  — the TSV behind every figure + data_profile + resource_estimates
- REPORT.md, REPORT.html (established style), STATUS.md (last)

---

## Guardrails
- Never modify outside the task subfolder at ARIS_OUTPUT, anything outside shall be only read or copy into cached files needed by the currrent session.
- retron_tradicional only; missing package → report and STOP (don't install).
- Exclude `anchor_type="ncRNA"` from RT analyses; exlcude MULTI = multi-label from any per data analysis, do not include in any per RT family analysis.
