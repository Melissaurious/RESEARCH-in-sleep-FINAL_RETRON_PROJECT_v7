# Stage 1 · Database characterization

## 0 · The point of this task

We do not know what is in this database. It was produced by a large-scale mining pipeline
using traditional methods, and nobody has counted it exactly, resolved its
misannotations, or fixed what a "unique system" means. Three different units — locus,
unique RT, unique RT–ncRNA pair — are currently used interchangeably, so every downstream
number rests on a denominator nobody can name. Once this lands we can pull any dataset on
demand by a traceable flag: complete RTs by prodigal flag, correctly-oriented loci,
unique pairs, three-tool agreement. We also get the first publishable description of the
corpus — counts, redundancy, taxa overrepresentation, per-family length distributions and
the RT↔ncRNA geometry — as figures, tables and a delivered HTML report. Nothing else in
the project can be trusted until this exists.

## 1 · What must be delivered

### Counts and units
- Total RT systems **per RT family label**, and unique systems, on **each** unit.
- **A definition of "unique system"**, declared and defensible, on three candidate keys:
  the RT sequence, the RT–ncRNA pair, and the locus. These are not interchangeable — in
  prior work the locus→unique-RT factor ranged **1.74×–7.39× by family**.
- **Redundancy** reported at every level: locus per distinct `genome_id`, per `species`,
  per `genus`, per `source_database`.
- **Taxa overrepresentation** — which organisms dominate each family, and how much of a
  family's apparent size is sequencing depth rather than biology.

### Geometry and distributions
- **Per-RT-family length distribution** with outliers named and statistical values
  reported. Computed on **both** units, **primary = unique RT** (`decisions/0003` §3).
- The same for the **retron ncRNA CM families**.
- **The "geometry" of retron RT systems** — where the ncRNA sits relative to the RT, in
  **base pairs and in number of CDS** — and the corresponding trend in **non-retron** RT
  families.

### ncRNA
- **Rate of retron ncRNA matches across retron-RT-labelled systems**, and the same rate
  **on non-retron RT families**. The second number is the control for the first.
- Cases where **one ncRNA appears across different RTs**, and where **one RT carries
  different ncRNAs** — both reported and explained, not collapsed.
- The size of the **zero-ncRNA class**. An unrepresentative head sample put it near
  **46%**; if that holds, *"retron locus"* and *"retron system"* are different
  populations and every later denominator must say which.

### Integrity
- **Clarify what the `MULTI` family is.** Counted as its own population, never appended
  to any family's statistics.
- **Identify misannotations**, off-contig ones included.
- **Verify strand orientation** — that every extracted element comes from the correct
  strand.
- **Rate of prodigal RT completeness flags** `00 / 10 / 01 / 11`.
- **Traceability to taxonomy and genomic sequence** wherever the database metadata
  carries it.
- **Three-tool agreement** on retron RT annotation, reported per tool and pairwise — never
  as a pooled field (see stage 12).

### Outputs
- Ready-to-use datasets, for retrons **and** for RT families generally, each row carrying
  traceable flags rather than having been filtered.
- Publication-ready figures, tables and diagrams.
- A delivered **HTML report** with the analysis and the insight explanations.

## 2 · Where this stands

**Prior work exists and re-derives.** `s2_corpus` rebuilt the extraction **field-for-field
with 0 mismatches over 3,358,182 source records** across all 43 family files — the logic,
not merely the counts — which closed `CONCERN_REGISTER` D4 by re-derivation.
Denominators on record: **501,561 · 78,287 · 54,865 · 49,919 · 5,495**. All `[UNVERIFIED]`
here.

**Active now:** `r01-corpus-census` → `r02-units` → `r03-rt-ncrna-pairs` →
`r04-geometry` in `research-wClaude-PART1_v2`, which redo this from raw. The scope is 42
files (41 RT families + `MULTI`); `master_ncRNA-anchored_merged.jsonl` is excluded because
it holds loci with an ncRNA and **no RT**.

## 3 · Prerequisites and gates

None — this is the root stage. **Stages 2, 8, 9, 10 and 11 all depend on it**, because
each needs a population it can name.

## 4 · Traps already paid for

- ⛔ **Coordinates are contig-based.** `intergenic_regions[].start/end` and
  `rt_gene.start/end` are contig coordinates; `genomic_context.full_sequence` is a window;
  `actual_window.start` is the offset. **1 in 6 records has `start == 1`**, where both
  frames coincide and every arithmetic check passes. Generalising from one such record
  once excluded **97.2%** of regions. Verify by **RT back-translation**, never inspection.
- ⛔ **"Complete" means ORF-complete.** **69.2%** of previously-admitted proteins do not
  fill the RT window, and three live "complete" rules reach the same 70% on sets agreeing
  at only **Jaccard 0.728** — equal rates are not equal sets.
- ⛔ **Never glob a cache directory that also holds an aggregate file.** One such glob
  swept the merged table into a "non-retron" denominator and produced n = 924,847 against
  a real population of 423,274; 99.65% of the resulting "non-retron" hits were retrons.
- ⚠️ **`full_lineage` is two schemas** keyed by `taxonomy_system` — gtdb 7-field, ncbi
  3-field with **no phylum**. Count per system, never pooled.
- ⚠️ **`system_subtypes` is two tools on one locus** (capital-initial = DefenseFinder,
  lowercase = PADLOC), agreeing on **44.6%**. Carry it; do not `groupby` it.
- ⚠️ **Pooling hides the distribution** — a pooled cross-group rate is the largest group's
  rate. `PQG[GA]` read **41.78% pooled vs 0.373% median-family**, a 112× gap.
- ⚠️ **`rt_hash` is not inherited** — not a sequence hash, and no `rt_hash → locus` link
  exists. Compute `sha256` here.

## 5 · Decisions for the operator

1. The **declared definition of "unique system"** — the three keys are measured, but which
   one carries the phrase in the paper is a scientific call.
2. Whether the **HTML report** ships per row or once at the end of `r04`.
3. Whether `MULTI` gets its own figure or a footnote once its size is known.

---

# 6 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §2

## The uniqueness question, as a ladder rather than a choice

The ideas document lists candidate definitions at three levels. Prior work says **keep them
all and regenerate views** rather than pick one (`decisions/0003`):

| level | candidates |
|---|---|
| **unique RT** | exact amino-acid sequence · sequence hash · clustered sequence · conserved-core identity · full-length identity |
| **unique system** | RT sequence · genomic locus · RT + ncRNA · RT + ncRNA + accessory · system architecture · genome/strain/assembly identity |
| **unique pair** | exact RT + exact ncRNA · clustered RT + clustered ncRNA · same locus · same operon architecture |

⭐ **The ideas document's own open question — *"should several parallel datasets be kept
instead of choosing one definition?"* — is already answered yes** by the
one-canonical-table-many-views rule. The choice is a `SELECT`, not a filter.

## Duplicate classes to resolve explicitly

- Same system under **different genome IDs**
- Same biological **strain across multiple assemblies**
- Same **RT sequence in multiple records**
- Same **locus recovered by multiple tools** → this is `system_subtypes` / `detected_by`,
  and it is stage 12's raw material, not noise to remove
- Same system **in multiple source databases** → the `source_database` rung of the
  redundancy ladder
- ⚠️ **Exact biological duplicates versus genuine repeated systems** — these are not
  distinguishable by sequence identity alone, and conflating them is what makes a
  "diversity" number meaningless

## Additional geometry axes worth capturing

Beyond distance in bp and CDS count, the ideas document adds axes the record does not:
**upstream vs downstream** ncRNA · **same-strand vs opposite-strand** · **ncRNA
overlapping a CDS** · **RT–accessory-gene distance** · **operon span** · **gene order** ·
**recurrent system architectures**. All are computable in the same pass (WA-D.4: retain
maximally).

⚠️ **`intergenic_regions[].has_ncrna` can be true while `ncrnas` is empty** — the schema
doc records that these exist. Any geometry built on `has_ncrna` must reconcile against
`ncrnas` per record.

## ⭐ The frozen reference dataset — a decision this stage must force

Ideas §20 step 2 makes *"frozen reference datasets"* a stage of its own, and §2 asks
**"which dataset becomes the frozen reference for downstream tasks?"** That is the right
question and it is an operator call (WA-I.1). Recommendation: **freeze the locus-level
table with flags, not a filtered subset**, and freeze *views* by declared query rather
than by copying rows — so a downstream stage cites a view definition plus the table hash.

## Two open questions to settle here

- **Metagenomic versus isolate records** — treated together or separately? This affects
  every diversity and saturation number (see stage 9) and is currently undeclared.
- **Assembly quality** as a carried flag; contig-edge status is already required.

---

# 7 · THE REPORT AND FIGURE PIPELINE — five generations, and what to reuse
**Traced 2026-09-12.** Every path verified. This is the lineage of *"database
characterization → figures → HTML report"*, which is what this stage must produce again.

## 7.1 · Generation 0 — the operator's own scripts

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/LATEST_REPORT_april_V4.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/UNIFIED_report_analysis_V2.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/utils_FOR_ALL_FILES.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/RETRON_analysis_clean_V3.ipynb
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/run_mmseqs2_enrichment.sh
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/NOTES.md
    output: /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/supporting_material/report_ncbi_bacteria_Bacteria.html

⛔ **READ-ONLY** (`MELISSA_SCRIPTS/`). Reference only — never modified, never re-run in place.

## 7.2 · Generation 1 — `PREVIOUS_ARIS_WORK`, the source of the house style

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/PREVIOUS_ARIS_WORK/REPORT.html   2.4 MB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/PREVIOUS_ARIS_WORK/REPORT.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/PREVIOUS_ARIS_WORK/scripts/
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/database_analysis/PREVIOUS_ARIS_WORK/figures/

⭐ **This is the style every later report inherits** — REPORTING_STANDARDS' *"reuse the
project's established HTML style; don't invent a new look per stage."*

## 7.3 · Generation 2 — V1, monolith then split

    /home/borg/RESEARCH-in-sleep-RETRON-DB/ARIS_OUTPUT/stage1/scripts/stage1_analysis.py        1 script, 14 figures
    /home/borg/RESEARCH-in-sleep-RETRON-DB/ARIS_OUTPUT/stage1_v2/scripts/stage1_v2.py           6 scripts, 48 figures
    /home/borg/RESEARCH-in-sleep-RETRON-DB/ARIS_OUTPUT/stage1_v2/scripts/generate_report_v3.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB/ARIS_OUTPUT/stage1_v2/scripts/fix_A2_venn.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB/ARIS_OUTPUT/stage1_v2/scripts/fix_E2_archaea.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB/ARIS_OUTPUT/stage1_v2/scripts/fix_E3_gem_ecosystem.py
    reports: .../stage1_v2/STAGE1_REPORT_v2.html · STAGE1_REPORT_v3.html

⚠️ The three `fix_*.py` scripts are the tell: a monolith needs patches per defect. That is
why generation 3 went section-based.

## 7.4 · Generation 3 — V2, section-based with an assembler

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V2/ARIS_OUTPUT/stage1_db_analysis/
        27 scripts · 90 figures · 49 tables · REPORT.html
    scripts/helpers.py · scripts/assemble_report.py
    scripts/s01_overview.py  s02_family_composition.py  s03_domain.py  s04_taxonomy.py
    scripts/s05_rt_length.py  s06_ncrna_cooccur.py  s07_ncrna_char.py  s08_tool_venn.py
    scripts/s09_genomic_context.py  s11_ncrna_overlap.py  s12_ncrna_position.py
    scripts/s13_genome_burden.py  s14_taxonomy_overrep.py  s15_multi_length.py
    scripts/s16_rt_ncrna_pairing.py
    scripts/sa1_genome_redundancy.py  sa2_dedup_ratio.py  sa3_niche.py
    scripts/sa4_orientation_qc.py  sa5_yxdd.py

⭐ `sa1_genome_redundancy.py`, `sa2_dedup_ratio.py`, `sa4_orientation_qc.py` and
`s16_rt_ncrna_pairing.py` are **precisely this stage's §1 deliverables**, already written
once.

## 7.5 · ⭐⭐ Generation 4 — V3, the most mature. Reuse this architecture.

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage1_db_analysis/
        38 scripts · 108 figures (36 × PNG+SVG+EPS) · 90 tables · REPORT.html

**The shared layer — read these two first:**

    .../scripts/helpers.py
        "Shared helpers for Stage 1 section scripts: cache loading, figure saving,
         denominators.  Every section imports this so the four denominator axes, the
         figure triple-format rule (PNG+EPS+SVG + underlying TSV, per REPORTING_STANDARDS)
         and the taxonomy-coverage caveat are implemented once rather than restated 19
         times."
        ⭐ Palette taken verbatim from the dataviz reference palette; magnitude figures use
          a single hue per the form rule.
    .../scripts/report_style.css
        the house style, extracted once from PREVIOUS_ARIS_WORK

**The assembler — and note what it does NOT do:**

    .../scripts/assemble_report.py
        "Phase B assembler — build REPORT.html and REPORT.md from cached tables + findings.
         Self-contained: figures are embedded as base64 PNGs, so REPORT.html has no
         external refs.  Computes nothing -- every number comes from cache/sections/*.json
         and tables/*.tsv, and every interpretation comes from findings.py."
    .../scripts/findings.py
        ⭐ the interpretations, in their own file, separate from computation

⭐⭐ **Phase A / Phase B is actually implemented here**, not just declared:
computation → `cache/sections/*.json` + `tables/*.tsv`; interpretation → `findings.py`;
assembly → `assemble_report.py`, which computes nothing.

**The extraction layer (streaming, with logs kept):**

    .../scripts/s00_stream_extract.py      + s00_extract.log
    .../scripts/s00b_dedup_build.py        + s00b_dedup.log
    .../scripts/s00c_taxonomy_join.py      + s00c_join.log
    .../scripts/s00d_stream_ncrna.py       + s00d_ncrna.log
    .../scripts/recon_profile.py           + recon_profile.log · recon_exact.log

**The section scripts:**

    s01_overview.py          s02_family_composition.py   s03_domain.py
    s04_taxonomy.py          s05_rt_length.py            s06_partial_rate.py
    s07_ncrna_cooccur.py     s08_tool_venn.py            s08_venn_diagram.py
    s09_ncrna_char.py        s10_ncrna_position.py       s10b_rt_ncrna_direction.py
    s11_genomic_context.py   s12_genome_burden.py        s13_multi.py

**The additional analyses:**

    n1_cm_cross_family.py    ⭐ retron CM × family matrix — this stage's §1 "CM match rate
                                on retron vs non-retron families"
    n2_clipping_audit.py     ⭐ off-contig / clipping — this stage's misannotation deliverable
    n3_niche.py              n4_label_conflicts.py  ⭐ label conflicts = stage 12 material
    taxa_overrep.py          ⭐ taxa overrepresentation
    retron_subtypes.py       ⚠️ subtypes — see the `system_subtypes` two-tool caveat
    retron_ncrna_absence.py  ⭐⭐ the ZERO-ncRNA class, already asked once

## 7.6 · What this means for the new stage 1

⭐ **Nearly every deliverable in §1 of this document has been implemented at least once.**
`retron_ncrna_absence.py` asked the zero-ncRNA question; `sa2_dedup_ratio.py` and
`sa1_genome_redundancy.py` are the redundancy ladder; `sa4_orientation_qc.py` is the strand
check; `n2_clipping_audit.py` is off-contig misannotation; `s16_rt_ncrna_pairing.py` and
`s10b_rt_ncrna_direction.py` are the pairing and geometry.

⛔ **But none of it is evidence here** (WA-I.3) — and generation 4 predates the current
agreements, so it has no bundle. **Reuse the architecture, re-derive the numbers.**

**The architecture worth copying verbatim:**
1. one script per section, never a monolith (generation 2's three `fix_*.py` show why);
2. `helpers.py` centralising denominators + the PNG/SVG/EPS + TSV rule;
3. `findings.py` separating interpretation from computation;
4. an assembler that **computes nothing** and embeds figures base64 for a self-contained HTML;
5. streaming extraction with its `.log` kept beside the script.

⚠️ **And re-check each inherited section against this project's known traps** — pooled
cross-family rates, globs used as denominators, `system_subtypes` treated as one field,
`full_lineage` as one schema. Generation 4 predates all four corrections.
