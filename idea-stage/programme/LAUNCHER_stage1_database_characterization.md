# LAUNCHER — Stage 1 · Database characterization

**Task id:** `dbchar-g1-census`
**Stage document:** `RETRON_STAGES/01_database_characterization.md`
**Template lineage:** `LAUNCHER_HYBRID_TEMPLATE.md` skeleton (rule ids, trust grades,
claims ledger) + `LAUNCHER_stage1_paper_positioning.md` input-availability discipline.

> **`<PROJECT_ROOT>` and `<TASK_ID>` are placeholders.** Fill them before the session
> starts. Nothing else in this launcher depends on which tree it runs in.

## Read first

1. `<PROJECT_ROOT>/CLAUDE.md`
2. `<PROJECT_ROOT>/agreements/WORKING_AGREEMENT.md` — the ALWAYS rules
3. `<PROJECT_ROOT>/docs/decisions/` — **every** record; `0003-units-and-views.md` is
   binding on this task
4. `<PROJECT_ROOT>/agreements/BUNDLE_SPEC.md` — before producing any number
5. **This file**

⛔ Do **not** read `RETRON_STAGES/01_database_characterization.md` §2 *"Where this stands"*
before §0.2 below. It prints prior denominators.

## Environment

```bash
conda activate retron_tradicional        # never base
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=100000
bash agreements/checks/specs_exist.sh && bash agreements/checks/rules_current.sh
```

---

## 0 · The point of this task

We do not know what is in this database. It was produced by a large-scale mining pipeline
using traditional methods, and nobody has counted it exactly, resolved its
misannotations, or fixed what a "unique system" means. Three units — locus, unique RT,
unique RT–ncRNA pair — are currently used interchangeably, so every downstream number
rests on a denominator nobody can name. Once this lands we can pull any dataset on demand
by a traceable flag, and we have the first publishable description of the corpus as
figures, tables and a report.

**Why now, and not later.** Stages 2, 8, 9, 10 and 11 each need a population they can
name. None of them can start until this exists.

### 0.1 Write boundary (WA-C.6)

This task writes to `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/` and
`<PROJECT_ROOT>/results/<TASK_ID>/` and nowhere else. Everything else is read-only.

**Registered-derived-artifact exception:** none. The locus table re-derives in ~3 min
(`decisions/0004`), so it is **regenerated, not stored**. If that turns out false —
measured runtime over 10× the estimate — stop and log it in `<PROJECT_ROOT>/docs/BLOCKED.md` rather than
inventing a storage location.

### 0.2 Sealed — do not open until the corresponding number has been measured (WA-D.6)

This task's whole value is an **independent** count. Prior work produced counts that
re-derive field-for-field, so the strongest available result is a **blind confirmation** —
which is destroyed by reading the target first.

| sealed | where it lives |
|---|---|
| per-file record counts | the `n claimed` column of `data/README.md` **D1**, and `D1-MULTI` |
| corpus denominators (the five headline totals) | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s2_corpus/` and `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/FROZEN_DENOMINATORS.tsv` |
| the ORF-completeness fraction | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/CLAIM_REGISTER.md` row `E1` |
| the zero-ncRNA fraction | `RETRON_STAGES/01_database_characterization.md` §1, and `ROADMAP.md`'s smoke-probe block |
| the locus→unique-RT dedup factor range | `decisions/0003-units-and-views.md` §1 |

**Protocol.** Measure first, write the number into `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/`, **then** open the sealed
source and record agreement or disagreement in `BLIND_CONFIRMATION.tsv` (§4.6).
⛔ A disagreement is a **result**, not an error to reconcile away. Report both values and
whose unit each is on before deciding which is wrong.

---

## 1 · Objective, success criterion, kill criteria

**Objective.** An exact, streamed census of the 42 source JSONL files, producing (a) the
counts and field-presence matrix, (b) the three uniqueness keys and their per-family
conversion, (c) the RT–ncRNA pair table with its multiplicity distribution, and (d)
per-family geometry and length distributions — each on a declared unit.

**Success criterion.** `<PROJECT_ROOT>/results/<TASK_ID>/` exists, `bundle_valid.sh` passes, **`run.sh`
reruns and reproduces every reported count**, and the operator has opened `INPUTS.tsv` and
recognised the inputs. Not "a report exists".

**Kill criteria** — any one of these stops the task rather than pushing through:

1. Per-file record count ≠ `wc -l` for any file. **The reader is wrong; stop.**
2. RT back-translation (§5.1) fails on more than 20% of records where the frames can
   disagree. The coordinate model is wrong and every geometry number would be wrong.
3. `metadata.total_ncrnas ≠ len(ncrnas)` for more than 5% of records. The ncRNA field
   semantics are not what the schema says; re-probe before designing anything on them.
4. Measured throughput is >10× worse than the estimate in §6. Re-scope, do not queue it.
5. A uniqueness key cannot be computed because a required field is absent at scale.
   That absence is the finding; report it and stop.

---

## 2 · Out of scope, and non-goals

- **No motif finding, no covariance models, no HMMs, no models of any kind.**
- **No dedup applied to stored output.** Dedup is a regenerable *view* (`decisions/0003`
  §1). Nothing is filtered out of the canonical table; exclusions are **columns**.
- **No per-subtype rates.** `system_subtypes` pools two tools; it is carried, never
  grouped (`decisions/0003` §6).
- **No cross-family `detected_by` comparison** — comparable within retrons only, by
  construction.
- **No taxonomy repair from the D5 metadata files.** That join is its own row (stage F).
- **No interpretation of what the counts mean for the paper.** Measure, record, report the
  ugly ones. Do not conclude (WA-I.1).

**Explicitly not archaeology.** Prior trees (`RETRON-DB_V2/V3/V4/V5`,
`research-wClaude-PART1`) are read for **ideas and input paths**, never for results.
This task does not audit a prior tree, does not grade a prior artifact's provenance, and
does not re-derive a prior number *to check it*. The one exception is §0.2's blind
confirmation, which is a by-product of measuring, not a separate audit.

---

## 3 · Inputs, with trust grades (WA-L.3)

Grades: **RAW** (use as-is) · **FROZEN** (this project produced it, hash recorded) ·
**RE-DERIVE** (recompute here before use).

### 3.1 · Raw data — the only thing this task actually consumes

| input | path | grade | why |
|---|---|---|---|
| D1 · source JSONL | `RESEARCH-in-sleep-/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/master_*.jsonl` | **RAW** | the corpus. 43 files; **42 in scope** |
| D1-MULTI | `…/master_MULTI_merged_oriented.jsonl` | **RAW** | loci with >1 RT. In scope, **reported as its own population**, never summed into a family |
| D1-X | `…/master_ncRNA-anchored_merged.jsonl` | ⛔ **EXCLUDED** | ncRNA present, **no RT**. Not a second anchoring of D1. Never joined to it |

Mode is `r--r--r--`. **Stream record-by-record; never load** (WA-D.2). One line = **one
locus**.

**Schema as observed** — see `ROADMAP.md` § *Schema as observed*. Treat it as a
**hypothesis** (WA-D.3): probe the actual values on real records across **several** family
files, never the head of one. ⚠️ The first 20,000 records of the Retron file are **100%
gtdb**, so the file is ordered by source database — a head sample is unrepresentative by
demonstration, not by theory.

### 3.2 · Supplementary and reference material — traced, and mostly NOT needed here

Recorded so the next stage does not have to find them again. **None is consumed by this
task**; each row says which stage needs it.

| id | path | what it supplies | needed by |
|---|---|---|---|
| D2 | `/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences/` — local disk, 2.7 G | 1,928 `terminal_N/` dirs; genomes + RT proteins. ⚠️ **our download, not a Mestre release** — provenance in `D2b` | 5, 6, I |
| D3 | ⚠️ **two candidate roots hold the same filenames; canonical is UNRESOLVED** — `RETRON_CLAUDE_PART1/supplementary_material/` and `…/MELISSA_DATA/supporting_material/` | Mestre tree (`Supplementary_mestre_Tree.nwk`), per-tip clade CSV, `support.csv` (Khan gold panel), Toro 2019 tree, `myRT-FastTree2.refpkg`, `toro_2014_Rt0-Rt7.FASTA` | 2, 5, 6, 11 |
| D4 | `/home/borg/RETRON_CLAUDE_PART1/Toro_2026/` | reference phylogeny, SPIRE type-specific HMMs, `spire_pipeline_scripts/` (⚠️ **someone else's pipeline** — read-only) | 5, 6, 10 |
| D5 | `…/MELISSA_DATA/databases_metadata_files/` — 8 files | taxonomy join tables per `source_database`. ⚠️ **`gem_metadata.tsv` is claimed to hold the GTDB lineage under a column headed `ecosystem`** — a testable claim, not a fact | F, 9 |
| D6 | PADLOC `/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm/padlocdb.cm` (21 retron ncRNA CMs) · `cm_meta.txt` · DefenseFinder `*Retron*` profiles · myRT `RVT-All.hmm` · Pfam-A 37.0 (Ibex) | detection models. ⚠️ **all 21 CMs authored by Mestre**; DefenseFinder profiles iterated to recover the known set → **models from one publication cannot corroborate each other** (EVIDENCE_STANDARDS §3b) | 10, 11, 12, E |

⛔ **Fix D3 before any stage consumes it.** The fix is to **pin one root and hash it**, not
to copy (`decisions/0004` §1). That pin is its own decision record, written by the row
that first needs D3 — **not by this task**.

### 3.3 · Pre-computed artifacts that exist — availability, not permission

Prior compute that a later stage can avoid repeating. ⚠️ **All `[UNVERIFIED]` (WA-I.3).**
Each enters only as `RE-DERIVED` or `BLIND-CONFIRMED`, at the point of use, in the row that
needs it. **None is consumed by this task** — recorded so it is not rebuilt from scratch
later.

| artifact | where | scale | needed by |
|---|---|---|---|
| ESMFold structures, **full-length** (`O2`) | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/` — `pdb/` `mestre/` `ldd557/` `ldd_pdb/` `khan171/` | **8,765** `.pdb`, ~2.1 G | 4, 6, 11, J |
| ESMFold structures, **span-sliced** (`O6`) | Ibex `/ibex/project/c2366/RETRONS/rt0_rt7_domain_test_v4_and_tree/struct/span_pdb/` | **5,256** `.pdb` — ⛔ **not on borg** | 6 |
| admission-band folds | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s5_admission/cache/fold/{admit,reject}/` | 600 + 600 | 11, E |
| crystal boundaries | `RETRON-DB_V3/MELISSA_DATA/crystal_structures/` — `boundary_extraction_report.txt`, `reference_boundaries.json` | **25** structures, fingers/palm/thumb + YXDD + DSSP | **4** ⭐ |
| foldseek all-vs-all TM | `…/v4_and_tree/cache/foldseek/tm.npy` + `tm.ids` | 1,919 proteins | 6 |
| structure id → sequence map | `/home/borg/RETRON_STRUCTURE_ID_MAP_2026-09-09.tsv` | 9,965 rows, sha1-verified | 4, 6, J |
| ESM-2 / ESM-C embeddings | `…/v4_and_tree/scripts/s4l_embed_esm2.py`, `s4n_embed_esmc.py` | scripts, not outputs | 11, J |

⭐ **The ID contract, so nobody re-derives it:** an ESMFold `.pdb` filename **is** the FASTA
header, and for the 16-hex scheme that header is **`sha1(sequence)[:16]`** — self-verifying.
`khan171` uses `gold_t<N>` where `<N>` is the Khan `support.csv` **`terminal_id`**, protein
in **`rt_protein_aa`** (⚠️ *not* `RT_sequence`, which is empty).
⛔ **The same 16-hex id appears in several `.faa` carrying different sequences**
(full-length vs span-sliced). Resolve by **hashing the sequences**, never by header lookup —
header lookup gives 5,002 mismatches out of 5,109.
⛔ **No `.pdb` → `rt_system_id` → genome map exists.** Closing it needs the sequence
re-hashed against the locus JSONL — **which is what §4.2 makes possible**, and is the one
place this task serves the structural stages.

### 3.4 · Reproduce, do not trust

Two values in circulation were produced by coordinator-side probes, not by bundles:

- **Throughput** — a session measured ~358 MB/s, then ~460–470 MB/s
  (`decisions/0004` §2, amended in place). **Both are session measurements.** Re-derive the
  figure and report it; §6's estimate is sizing input only.
- **The zero-ncRNA fraction** — from an unrepresentative head sample. **Sealed** (§0.2).

⛔ **This launcher deliberately prints no count that the task is meant to derive.**

---

## 3a · Prior work → ideas, not results

**Inventory, do not mine.** Record what exists, what it would supply, and which claim it
bears on — then stop. Nothing below is evidence here.

| prior effort | where | the idea it contributes |
|---|---|---|
| corpus re-derivation | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s2_corpus/`, `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s3_object/` | ⭐ the extraction logic was re-derived **field-for-field**, not merely recounted — the right standard for this task. Method: `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X01_corpus_and_unit.md`, `X02_completeness_filter.md` |
| the completeness defect | `CLAIM_REGISTER.md` `E1`, `E3`, debate `D1b` | *"complete"* means **ORF-complete**, and dereplication **enriches** truncated tips. → carry `partial` + contig-edge distance as columns (`decisions/0003` §4) |
| the denominator failure | `denominators-must-equal-a-known-population` | ⛔ **never glob a cache dir that also holds an aggregate file** — one glob swept the merged table into a "non-retron" denominator. → assert every denominator equals a **named** population |
| unit discipline | `decisions/0003` §1 | three keys, none convertible by a constant; the factor varies **by family** |
| the pooling defect | `pool-hides-the-distribution` | a pooled cross-group rate is the biggest group's rate. → report per-family, always |
| the frame trap | `locus-jsonl-coords-are-contig`, `verify-a-frame-where-it-cannot-coincide` | ⛔ verify the frame **only** on records where it can disagree |
| the object defect | `crosscheck/VERDICT.md` §4.10 | a table on one object, prose on another, inherited onward. → **every deliverable names its object** |
| tool asymmetry | `retron-tool-filtering-asymmetry`, `system-subtypes-is-two-tools` | carry both tools separately; the disagreement is **stage 12's subject**, not noise |

**Ideas this task should surface but not pursue** — append to `IDEAS.md` as `parked`, with
the falsifiable form if one is statable: orphan retron-like RTs with no ncRNA · isolate vs
metagenome as a redundancy axis · whether `has_ncrna` and `ncrnas` disagree systematically ·
what `MULTI` actually is.

---

## 3b · Input availability discipline

> ⛔ **`ls` is not evidence. `exists()` is not evidence. A directory that exists and is
> empty is the trap, not the answer.**

Grade every availability row `MEASURED` / `DERIVED` / `INFERRED`. A row is **`MEASURED`**
only when the file was **opened, parsed, and an invariant asserted** — a record count, a
key that joins at a stated rate, a field that is populated. A negative — *"this input does
not exist"* — is **`INFERRED`** unless the search's **scope and key** are recorded and
cover what the claim asserts.

**Three precedents, each a different mistake:**

| precedent | the mistake |
|---|---|
| a reference set declared absent | searched for a **format**, then for the **wrong key** |
| corrected, still wrong | **a partial hit closed the search** |
| a disagreement count read off a table | the table **did not contain the quantity** |
| `esmfold_khan171/pdb` reported empty (2026-09-09) | a **filtered command ate the count line** — the directory held 171 files |

Deliverable: `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/INPUT_AVAILABILITY.tsv`, columns `input_id · path · what_it_would_supply ·
verification_performed · invariant_asserted · result · availability
(AVAILABLE|PARTIAL|ABSENT|NEEDS_NETWORK) · grade (MEASURED|DERIVED|INFERRED) ·
stages_depending`.

⚠️ **`NEEDS_NETWORK` is valid and expected.** Record it; do not take a network action to
resolve it. The operator decides.

---

## 3c · Claims this task settles

Ids assigned **here and nowhere else** (CL-2). Every claim born **UNPROVEN** (CL-1) and
carries a **value, unit, denominator and scope** (CL-4).

| ID | Claim — value, unit, denominator, scope | Circ. | Status |
|---|---|---|---|
| `dbchar:C1` | Record count per source file. Unit: **locus**. Denominator: the file's own `wc -l`. Scope: 42 files | NONE | UNPROVEN |
| `dbchar:C2` | Field presence and emptiness per field. Unit: **% of records**. Denominator: records in that file | NONE | UNPROVEN |
| `dbchar:C3` | Distinct RT proteins. Unit: **`sha256(rt_gene.sequence)`**. Denominator: loci in scope, per family | NONE | UNPROVEN |
| `dbchar:C4` | locus→unique-RT conversion factor, **per family**. Unit: ratio. Denominator: that family's loci | LOW | UNPROVEN |
| `dbchar:C5` | ncRNAs per locus, **including zero**. Unit: count distribution. Denominator: retron-labelled loci | NONE | UNPROVEN |
| `dbchar:C6` | Distinct RT–ncRNA pairs. Unit: **(sha256 RT, sha256 ncRNA)**. Denominator: loci with ≥1 ncRNA | LOW | UNPROVEN |
| `dbchar:C7` | Prodigal RT completeness flag rates `00/10/01/11`. Unit: % of loci. Denominator: loci with an RT gene | NONE | UNPROVEN |
| `dbchar:C8` | Redundancy ladder: loci per distinct `genome_id`, `species`, `genus`, `source_database` — **within each `taxonomy_system`** | LOW | UNPROVEN |
| `dbchar:C9` | RT–ncRNA geometry: distance in **bp** and in **CDS count**, strand relationship, upstream/downstream. Unit: distribution. Denominator: verified pairs | MEDIUM | UNPROVEN |
| `dbchar:C10` | Retron-CM ncRNA match rate on **retron-labelled** vs **non-retron** RT families. Unit: % of loci. Denominator: loci per family | MEDIUM | UNPROVEN |
| `dbchar:C11` | Off-contig / misannotation rate. Unit: % of loci. Denominator: loci in scope | LOW | UNPROVEN |
| `dbchar:C12` | Three-tool agreement on retron RT annotation, **pairwise and per tool**. Denominator: retron-labelled loci | MEDIUM | UNPROVEN |
| `dbchar:C13` | Strand-orientation consistency of extracted elements. Unit: % consistent. Denominator: loci with ≥1 extracted element | LOW | UNPROVEN |
| `dbchar:C14` | What `MULTI` is: RTs per locus, family composition. Denominator: the 42nd file's own records | NONE | UNPROVEN |

⚠️ `C9`/`C10`/`C12` carry **MEDIUM** circularity: geometry is measured in a frame this task
also defines, the CM match rate uses models from one publication lineage, and tool
agreement is between tools that share a parent. **State the circularity in the bundle
README; do not resolve it here.**

---

## 4 · Deliverables — one section per file produced

All under `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/<TASK_ID>/`; numbers land in `<PROJECT_ROOT>/results/<TASK_ID>/` (WA-B.1).
**Every table names its unit and its denominator in a header comment.**

### 4.1 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/census_per_file.tsv` — settles `C1`, `C2`, `C7`, `C14`
One row per file: records, distinct `genome_id`/`contig`/`species`/`genus`, field presence
matrix, prodigal flag rates, `wc -l` assertion result. `MULTI` on its own rows.

### 4.2 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/locus_keys.tsv` — settles `C3`, `C4`
One row per locus: `rt_system_id`, `sha256(rt_gene.sequence)`, `sha1(rt_gene.sequence)[:16]`,
family, `genome_id`, `contig`, `source_database`, `taxonomy_system`, `partial`,
distance-to-each-contig-edge, RT length.
⭐ **Emit the sha1-16 column.** It is the ESMFold structure id (§3.3), so this single column
closes the `.pdb` → `rt_system_id` gap for stages 4, 6 and J at no extra cost.

### 4.3 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/rt_ncrna_pairs.tsv` — settles `C5`, `C6`, `C9`
One row per (locus, RT, ncRNA): both sequences, coordinates in a **declared** frame, the
multiplicity class, bp distance, intervening CDS count, strand relationship,
upstream/downstream, CDS-overlap flag. **Gated on §5.1 passing.**
Multiplicity is **classified, not silently resolved**; the resolution rule is chosen after
the distribution is seen and recorded in the bundle README.

### 4.4 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/geometry_by_family.tsv` + `figures/` — settles `C9`
Per-family length distributions for RT (aa) and ncRNA (nt) with quantiles, outliers named,
on **both** units with **unique RT primary** (`decisions/0003` §3), plus the conservative-
subset version so truncation's effect is visible. Every figure ships **PNG + SVG + its
`.tsv`** (REPORTING_STANDARDS).

### 4.5 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/integrity.tsv` — settles `C10`, `C11`, `C12`, `C13`
Off-contig and misannotation classes, strand consistency, retron-CM match rate on retron
vs non-retron families, three-tool agreement **per tool and pairwise, never pooled**.

### 4.6 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/BLIND_CONFIRMATION.tsv` — the §0.2 output
`quantity · measured_here · sealed_value · unit_of_each · agree(Y/N) · note`. Filled
**after** measurement. ⛔ A disagreement is reported, not reconciled.

### 4.7 · `<PROJECT_ROOT>/ARIS_OUTPUT/<TASK_ID>/tables/INPUT_AVAILABILITY.tsv` — §3b

### 4.8 · `REPORT.md` + `REPORT.html`
Two-phase (REPORTING_STANDARDS): **Phase A** computes every section — numbers, cached
tables, figures with their TSVs, **no prose conclusions**. **Phase B** is a single
interpretation round reading all tables together. Counts reported so defects are visible:
**n attempted, n succeeded, n dropped and why** (BS-5). **Never footnote a failure.**

### 4.9 · `STATUS.md`
Written **last**. What ran, what failed, what is cached, what is pending.

---

## 5 · Controls

### 5.1 · Frame verification — a gate, not a check
⛔ `intergenic_regions[].start/end` and `rt_gene.start/end` are **contig** coordinates;
`genomic_context.full_sequence` is a **window**; `actual_window.start` is the offset.
**Verify by RT back-translation:** cut `rt_gene` at the shifted coordinates, translate,
require equality with `rt_gene.sequence`.
⛔ **Verify only on records where the frames CAN disagree** (`actual_window.start ≠ 1`).
Roughly 1 in 6 records has `start == 1`, where both frames coincide and every arithmetic
check passes — generalising from one such record once excluded **97.2%** of regions.
Report attempted / verified / dropped and why. §4.3 is blocked until this passes.

### 5.2 · Hand-tallied fixture — the positive control (RM-5, EVIDENCE_STANDARDS §6)
⚠️ **This task reports emptiness and absence**, so a wrong key path makes every record read
"empty" and produces a clean, plausible, entirely wrong number. **A negative that is wrong
looks exactly like a negative that is right.**

~20 real records, expected counts written down **before** the script runs, covering:
`ncrnas` non-empty **and** empty · a gtdb record with `phylum` **and** an ncbi record
without · `partial != "00"` · `actual_window.start == 1` **and** `≠ 1` · a record where
`intergenic_regions[].has_ncrna` is true while `ncrnas` is empty · a `MULTI` record.
**The control must be able to fail** — confirm that a deliberately wrong key path makes it
fail before trusting a pass.

### 5.3 · Denominator assertion
For **every** denominator, assert it equals a population you can name — one `assert`.
⛔ **Never glob a cache or source directory that also holds an aggregate file**; enumerate
the 42 parts explicitly.

### 5.4 · Equal rates are not equal sets
If two rules return the same rate, compute the **Jaccard of their sets** before treating
them as the same measurement. Three "complete retron" rules once gave 70.08 / 69.97 /
70.45% on the same population and agreed at only **Jaccard 0.728**.

---

## 6 · Compute

**Local, single-core, streamed. No cluster, no queue.** Sizing estimate: a session
measured ~3 min of pure parse for all 42 files; allow **10–30 min** with hashing and
output. `--limit N` on every script (WA-E.3); smoke on a **length-stratified sample across
several family files**, never the head of one (WA-K.4).

If measured throughput is >10× worse than the estimate → kill criterion 4.

---

## 7 · The review gate

Before the bundle is offered for acceptance, attack it on these axes — each is a real
failure this project has already paid for:

1. **Unit** — does every number name its unit, in the same sentence, including in prose?
2. **Denominator** — does each equal a nameable population? Show the `assert`.
3. **Object** — does any table use one object while its prose uses another?
4. **Frame** — was the frame verified where it could disagree?
5. **Pooling** — is any cross-family rate pooled?
6. **Control** — could §5.2 have failed? Demonstrate it.
7. **Seal** — was anything in §0.2 opened before the corresponding measurement?

---

## 8 · Stop condition

Done when `<PROJECT_ROOT>/results/<TASK_ID>/` exists per BUNDLE_SPEC, `bundle_valid.sh` passes,
**`run.sh` has been rerun and reproduced the counts**, and `INPUTS.tsv` has been opened by
the operator and recognised. `PROVENANCE.md` carries `seed: n/a — no RNG` (BS-9) and the
agreements sha (BS-10).

Then **write `STATUS.md` last and halt.** Do not loop, do not start the next stage.

---

## 9 · Working rules

- **Locate, then patch.** Never regenerate a file to change a few lines. No `sed -i`.
- **One script per task, ≤200 lines** (project override: ≤500 for report assemblers).
  Run each after writing it.
- **A census is exact; an estimate declares itself** (WA-D.2). The only permitted estimate
  here is wall-clock, labelled as such.
- **Retain maximally** (WA-D.4): keep every field touched, not today's subset. A carried
  column costs bytes; a missing one costs a 75 GB re-read.
- **Never delete, always flag.** Exclusions are columns.
- **Blocked?** Append to `<PROJECT_ROOT>/docs/BLOCKED.md` with options and a recommended default.
  LOW-STAKES: take it, log it, continue. HIGH-STAKES: stop and wait (WA-S.4).
- **Retro** to `retros/YYYY-MM-DD_<TASK_ID>.md` before close (WA-S.3).

---

## 10 · The question

> **What is actually in this database — exactly, per unit, with the defects visible — and
> can any downstream stage now pull the dataset it needs by naming a flag instead of
> re-reading 75 GB?**
