# Stage 7 · Annotate the neighbourhood of RTs efficiently, and delimit operons

## 0 · The point of this task

We already know the genomic neighbourhood cannot *identify* a retron — retrons rank 27th
of 41 RT families on defence-accessory carriage, so that door is closed and should not be
reopened. What we do not know is what actually surrounds these RTs: **41,250,531 accessory
CDS across 1.65 million genomes have never been parsed**, and doing it costs roughly 26
CPU-minutes. Once this lands we have the effector architecture around every RT family at
corpus scale, annotated by more than one route so that the routes can be *shown* to
disagree rather than assumed to agree. That is the direct input to the fusion stage, the
classification work, and any operon-boundary claim.

## 1 · ⛔ What is already settled — do not redo it

`x1_neighbourhood`: **the neighbourhood is an artefact as an instrument.**

- Non-retron reverse transcriptases carry Tier-A defence accessories at **45.36%** against
  retrons' **53.50%** once neighbour count is matched — a fold of **1.179 [1.161, 1.198]**,
  inside the pre-registered `DEAD` band.
- **Retrons rank 27th of 41 RT families**, with 21 families conservatively above them and
  `RVT-UG6` at **96.19%**.
- *"A modality on which retrons are mid-table cannot be evidence that a locus is a
  retron."*

The neighbourhood is therefore a **description**, not a detector. That is still worth
having — it just cannot be an identification claim.

## 2 · ⛔ What is untouched, and cheap

**The genome layer has never been opened:**

| | |
|---|---|
| genomes | **1,650,000** |
| with ≥ 2 RT families | **384,725** |
| accessory CDS | **41,250,531** |
| full parse + translate | **≈ 26 CPU-min — no cluster needed** |

**`PE11b`** — *what effector architectures surround retron RTs, at corpus scale* — never
run. ⭐⭐
**`PE16`** — *annotate the effectors by SEVERAL independently-provenanced routes and prove
they CAN disagree before claiming they agree* — never run. ⭐⭐ This is the through-line
(see stage 12).
**`PE13`** — *classify on RT + effector architecture FIRST, add ncRNA later* — never run;
builds on the two axes that are reliably observable.

**Operon delimitation: never attempted.** Note that it is a **delimitation** problem, the
same class as the palm boundary (stage 4) and the msr-msd boundary (stage 10) — see
stage A.

## 3 · ⚠️ The blocker to clear first

**InterProScan here ships a stub database.** Pfam-A holds **3–4 profiles**; TIGRFAM holds
**1**. *"Annotate with Pfam" is unrunnable locally*, and **only counting the profiles
detects it** — the tool runs, exits 0, and returns almost nothing.

Pfam-A **37.0** with **21,979 models** exists on Ibex:
`/ibex/user/rioszemm/the-retron-project/src/interproscan/interproscan-5.70-102.0/data/pfam/37.0/pfam_a.hmm`

## 4 · Prerequisites and gates

- **Stage 1** for the locus population and correct strand orientation.
- ⚠️ **`detected_by` is comparable within retrons only** — PADLOC and DefenseFinder were
  extracted **retron-only**, myRT **unfiltered**. A cross-family detector table would be
  wrong by construction.
- ⚠️ **`full_lineage` is two schemas** if any neighbourhood result is broken down by taxon.

## 5 · Parked ideas that belong here

- Defence-system **co-occurrence network**
- **Bipartite network statistics** on the effector matrix
- **Orphan module counts**
- **Recombination detection at the RT/effector junction** (shared with stage 8)

## 6 · Decisions for the operator

1. Which annotation routes count as **independently provenanced** — the whole value of
   `PE16` rests on routes that do not share a parent.
2. Whether operon delimitation is scoped here or moved into stage A.

---

# 7 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §9

## ⭐ The normalized architecture representation — adopt this

The ideas document proposes encoding each system as an architecture string:

```text
ncRNA → RT → effector
ncRNA → effector → RT
RT–effector fusion
ncRNA → RT → unknown → effector
```

⭐ **This is the right deliverable, and it links four stages at once**: it is stage 7's
output, stage 8's fusion row (`RT–effector fusion` is one architecture, not a separate
object), stage J's *architecture novelty* axis, and stage 1's *recurrent system
architectures* geometry field. Define the alphabet once, here.

⚠️ **`unknown` must be a first-class symbol, not a gap.** The ideas document's own question
*"which 'unknown' proteins form recurrent families?"* is only answerable if unknowns are
retained and clustered rather than dropped — the never-delete-always-flag rule applied to
neighbours.

## The operon definition, as features rather than a threshold

Same strand · distance to RT · distance between CDSs · gene overlap · intervening CDSs ·
orientation · recurrent synteny · ncRNA position · known validated architectures.

⭐ **Treat the definition as a measurement, not a parameter.** Prior work's failure mode is
a `[CHOICE]` threshold that becomes load-bearing and unexamined — `X04`'s window cut is the
precedent. Report the architecture distribution across a *range* of distance cutoffs and
show which conclusions are cutoff-invariant.

## Accessory-protein questions, ranked by what they would change

| ideas question | why it matters here |
|---|---|
| ⭐ *Are accessory proteins better predictors of system type than RT sequence?* | This is `PE13` — *classify on RT + effector architecture FIRST, add ncRNA later*. Never run, and it is the strongest claim in this stage |
| *Which accessory proteins recur by clade vs across clades?* | the clade-specific/general split, same shape as `s4_motifs`' general/family-specific result |
| *Are there lineage-specific replacements of effectors?* | needs a tree (stage 6) or at least a stable grouping (stage H) |
| *Are certain architectures associated with specific ncRNA families?* | ⛔ **gated by `E6`** — `msr_msd` is nested inside `clade`, so any architecture↔ncRNA-family association is confounded by lineage until stage D supplies a control that can move |
| *Which "unknown" proteins form recurrent families?* | the untouched 41.25 M accessory CDS; ≈26 CPU-min |

## From the parking lot (§21), belonging here

*"Compare accessory architecture versus RT phylogeny"* · *"Test whether accessory proteins
evolve faster than RTs"* — both need stage 6 or H first.

---

# 8 · EVERYTHING NEEDED TO HAND THIS TO A NEW SESSION
**Traced 2026-09-13.** All paths absolute and `test -e` verified.
⛔ **Correction to §2 of this document:** the genome layer is untouched **at corpus scale**,
but a **940,264-CDS annotated subset around retron RTs already exists**. That is ~2.3% of
the 41,250,531 accessory CDS — small as a fraction, large as a starting point, and it was
not recorded here before.

## 8.1 · ⭐⭐ The pre-computed neighbourhood dataset — 1.2 GB, on borg, in V3

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/cache/neighborhood_annotation/

| artefact | scale |
|---|---|
| `accessory_proteins.faa` | ⭐ **940,264 accessory CDS proteins**, 301 MB — already translated |
| `cds_manifest.tsv` | ⭐ **940,264 rows** · `rt_hash · gene_id · strand · partial · offset_bp · cds_nt_len · prot_aa_len` — **`offset_bp` is the RT→CDS distance, i.e. the geometry** |
| `rt_proteins.faa` | **77,685** RT proteins |
| `fused_effector_rt.faa` · `fused_effector_rt_clean.faa` | ⭐⭐ **14,778** fused effector–RT proteins |
| `hmm/tierA_nonretron.hmm` | **1,139** profiles (DefenseFinder-derived) |
| `hmm/tierB_retron_mestre.hmm` | **39** profiles (Mestre retron) |
| `hits_acc_tierA.domtbl` | **307,435** hits |
| `hits_acc_tierB.domtbl` | **111,936** hits |
| `hits_rt_tierA.domtbl` | **6,579** hits |
| `hits_rt_tierB.domtbl` | **738,142** hits |
| `pfam_rt.domtbl` | **73,060** hits |
| `p3z.log` | the run log — *"target unique retron rt_hashes: 78,287"*, full pass |

**Producing scripts** — `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/scripts/`:

    p3y_extract_neighborhood_proteins.py    extract the accessory CDS around each retron RT
    p3z_annotate_neighborhood.sh            hmmsearch --cut_ga --domtblout, Tier A + Tier B
    p3zz_summarise_effectors.py             collapse hits to per-system composition

**Outputs** — `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/tables/`:

    neighborhood_effector_composition.tsv
    neighborhood_effector_frequency.tsv
    fused_effector_residual.tsv

**The spec, and read its scope boundary before reusing anything** —
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/NEIGHBORHOOD_ANNOTATION_SPEC.md`
(27 KB), verbatim:

> *"**Status:** Tier A running (local, borg). **Tier 1 / Tier 2 specified, not launched.**"*
> *"**Scope, and it is a hard boundary.** This is **annotation to support interpretation**…
> It is **NOT** a reclassification of subtypes by neighbourhood… If this work starts to look
> like *redefine subtypes by neighbourhood clustering*, **stop**."*

⚠️ **`PE13` (classify on RT + effector architecture first) runs straight into that ruling.**
It is not forbidden — but it is a **scope change the owner previously closed**, and it must
be reopened deliberately, not inherited by accident.

## 8.2 · The V4 audit that closed the instrument question

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/x1_neighbourhood/
        14 scripts · 14 tables · 145 MB cache

    PREREG_X1.md     ⭐ written before the non-retron arm existed
    VERDICT.md · FINDINGS.md · STATUS.md · RETRO.md · responses/

| script | what it does |
|---|---|
| `scripts/x0_boundary.sh`, `scripts/x13_boundary_diff.sh` | write-boundary checks |
| `scripts/x1_retron_baseline.py` | re-derives the **retron** Tier A arm from V3's table |
| `scripts/x2_draw_sample.py` | draws the non-retron sample **exactly as `PREREG_X1.md` fixed it** |
| `scripts/x3_extract_neighbourhoods.py` | recovers accessory CDS around each drawn non-retron RT |
| `scripts/x4_annotate_nonretron.sh` | `hmmsearch --cut_ga --domtblout`, no score/E override |
| `scripts/x5_summarise_nonretron.py` | per-system Tier A composition |
| `scripts/x6_retron_subtypes.py` | subtype arm |
| `scripts/x7_null_analysis.py` | **JOB 1 — the null**: do non-retron RTs carry Tier A at the same rate? |
| `scripts/x8_rejected_band_by_type.py` | the rejected 40–160-bit band by type |
| `scripts/x9_port_fidelity_control.py` | port-fidelity control |
| `scripts/x10_job3_gate.py` | the job-3 gate |
| ⭐ `scripts/x11_tool_disagreement.py` | **tool disagreement — stage 12 material, filed here** |
| `scripts/x12_family_rank.py` | **where retrons rank among the 41 families** → the 27/41 result |

**Tables** — `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/x1_neighbourhood/tables/`:
`j1_draw_design.tsv` · `j1a_retron_baseline_by_ncrna.tsv` · `j1a_retron_confound_direction.tsv` ·
`j1a_retron_ncds_distribution.tsv` · `j1b_matched_on_ncds.tsv` · `j1c_port_fidelity_control.tsv` ·
`j1d_family_rank.tsv` · `j1_nonretron_effector_composition.tsv` ·
`j1_nonretron_effector_frequency.tsv` · `j1_null_tierA_by_set.tsv` · `j2_rejected_band_by_type.tsv` ·
`j2b_enrichment_ranking.tsv` · `j2c_tool_disagreement.tsv` · `j3_capture_recapture.tsv`

**Cache** — `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/x1_neighbourhood/cache/`:
`neighborhood_nonretron/` (`accessory_proteins.faa`, `cds_manifest.tsv`, `hits_acc_tierA.domtbl`,
`hits_rt_tierA.domtbl`, `recovery_by_family.tsv`, `rt_proteins.faa`, `system_covariates.tsv`) ·
`port_control/` · `x2_draw.tsv` · `x6_retron_subtype_per_protein.tsv`

## 8.3 · The genome-layer feasibility stage

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/discovery/
        scripts/f1_unit_census.py          tables/feasibility_f1_unit_census.tsv
        scripts/f2_locus_census.py         tables/feasibility_f2_locus_census.tsv
                                           tables/feasibility_f2_translation_yield.tsv
        scripts/f3_provenance_sweep.sh     tables/feasibility_f3_provenance.tsv
        scripts/f4_genome_multiplicity.sh  tables/feasibility_f4_genome_multiplicity.tsv
        scripts/f4b_genome_summary.py
        ⭐ scripts/f5_annotation_resources.sh  tables/feasibility_f5_annotation_resources.tsv
        scripts/f6_ncrna_gap_sweep.sh      tables/feasibility_f6_ncrna_gap.tsv
        ⭐ scripts/f7_neighbour_inventory.sh  tables/feasibility_f7_neighbour_inventory.tsv
        cache/f2_locus_rows.tsv.gz · cache/f4_family_genome.tsv.gz
        ⭐ QUESTIONS.md (35 KB — the ranked genome-layer questions)
        ⭐ WHAT_THE_CORPUS_CANNOT_ANSWER.md (10 KB)

**The measured scale**, from these tables: **1,653,827** genomes with ≥1 RT locus ·
**695,408** with ≥2 loci · **384,725 with ≥2 DIFFERENT family labels** (72,616 with ≥3; max
12 labels; max 239 loci in `GCA_050562215.1`) · **128,870** genomes appear only in the
ncRNA-anchored file · **41,250,531 accessory CDS** over 3,059,700 RT-anchored loci
(14.48/locus; the Retron file alone is 10,860,065 at 17.32/locus).
**Cost, measured: ~50 MB/s/core → 79 GB ≈ 26 CPU-min**, ~4 min wall on 48 cores.

## 8.4 · On Ibex

    /ibex/project/c2366/RETRONS/rt_cds_linkage_diagnosis_2026-09/
        scripts/{reconcile_cds.py, diagnose_one_genome.sh, diagnose_array.slurm,
                 make_negative_control.sh, stage_a_setup.sh, example_of_pipeline.sh}
        inputs/terminal_* · window_probe/ · work/ · logs/ · env/
        r01e_a/ · r01f_c45/ · r01f_gem/ · r01g_c44/

⛔ **This is NOT stage 7.** Its own docstring: *"STAGE 30 — reconcile the CDS across pipeline
stages, for ONE genome. **Sidework. Nothing this emits is a number: it may not be cited,
plotted, or written into `CLAIMS.md`.**"* It belongs to **stage 1** (CDS/frame provenance),
and its row names (`r01e_a`, `r01f_c45`, `r01g_c44`) are the new repo's `r01` ids.

⭐ **But note what it exists to answer**, because stage 1 needs it: *"The June corpus records
the outcome (`is_rt_gene` set, or not) and the production run passed `--cleanup`, which
deleted `prodigal_results/` — so from the corpus alone **you cannot tell whether Prodigal
ever called the CDS**."*

## 8.5 · ⛔ Four hazards, all verified today

**1 · The Tier A profile is reused, not rebuilt — and the source has since grown.**
`x4_annotate_nonretron.sh` warns: *"🔴 THE PROFILE FILE IS REUSED, NOT REBUILT. p3z built
`tierA_nonretron.hmm` on 2026-07-28 by **globbing** `$HOME/.macsyfinder/models`. Rebuilding
it today would silently score the two arms [differently]."* The script asserts the count and
prints a sha256.

| | |
|---|---|
| `…/neighborhood_annotation/hmm/tierA_nonretron.hmm` | **1,139** profiles ✅ assertion still holds · sha256 `cedf17d9e4b393b8…` |
| `/home/borg/.macsyfinder/models/defense-finder-models/profiles/` | ⛔ **1,178 files today** |

**Rebuilding would give 1,178, not 1,139.** ⛔ **Use the pinned file; never re-glob.** This is
the same implicit-set-construction defect class as the 924,847 denominator.

**2 · The corpus carries no neighbour sequences.** **0 of 299,320** accessory CDS have a
`sequence` field — corpus-wide, not a sampling artefact. Translation from coordinates is
mandatory (that is what the 26 CPU-min buys), and `p3y_extract_neighborhood_proteins.py`
already does it at 98.88% recovery.

**3 · InterProScan here ships a stub database** — Pfam-A holds 3–4 profiles, TIGRFAM 1. The
real Pfam-A 37.0 (21,979 models) is **Ibex only**:
`/ibex/user/rioszemm/the-retron-project/src/interproscan/interproscan-5.70-102.0/data/pfam/37.0/pfam_a.hmm`.
⚠️ But `pfam_rt.domtbl` (73,060 hits) exists, so a Pfam pass **was** run — find out where
before re-running it.

**4 · `genome_id` is an assembly accession.** Collapse to a species-level unit before any
rate, or the redundancy ladder is being measured, not biology.

## 8.6 · Recipe to pick this up

1. **Read `NEIGHBORHOOD_ANNOTATION_SPEC.md` first** — it defines the scope boundary and
   records the owner's Tier-B split ruling. `PE13` crosses it.
2. **Read `x1_neighbourhood/PREREG_X1.md` then `VERDICT.md`** — the instrument question is
   closed (retrons 27th of 41); do not reopen it.
3. **Inventory what already exists before computing anything**: 940,264 annotated accessory
   CDS with `offset_bp`, 14,778 fused effector–RT proteins, Tier A + Tier B hits.
   **The gap is corpus scale (2.3% covered), not method.**
4. **Pin the Tier A profile by sha256**, never re-glob (§8.5).
5. **Then** the corpus-scale pass: 26 CPU-min, no Ibex, using
   `p3y_extract_neighborhood_proteins.py` as the precedent.
6. ⛔ **Operon delimitation is still untouched** — and it is a *delimitation* problem
   (`/home/borg/RETRON_STAGES/A_delimitation.md`), not an annotation one.

---

# 9 · THE ANNOTATION ITSELF — tool, coverage, and exactly where it stopped
**Read from the scripts and the spec, 2026-09-13.** This section is what makes the document
self-contained: a session should not need to open anything else to know what was run.

## 9.1 · The tool — one command, two profile sets, no thresholds of our own

    /home/borg/miniconda3/envs/retron_tradicional/bin/hmmsearch \
        --cut_ga --cpu $CPU --domtblout <out>.domtbl -o /dev/null <profiles.hmm> <proteins.faa>

⭐ **`--cut_ga` only — gathering thresholds as shipped. No score or E-value override
anywhere**, in either arm. That is what makes the two arms comparable at all.

| profile set | file | n | what it is |
|---|---|---:|---|
| **Tier A** | `…/neighborhood_annotation/hmm/tierA_nonretron.hmm` | **1,139** | DefenseFinder models, **globbed** from `/home/borg/.macsyfinder/models` on 2026-07-28 |
| **Tier B** | `…/neighborhood_annotation/hmm/tierB_retron_mestre.hmm` | **39** | retron models mapping **one-to-one onto Mestre's Table 1** |

Tier B profile names, verbatim: `Retron_I_B__ATPase_TOPRIM`, `Retron_II__NDT`,
`Retron_III__PRTase`, `Retron_V__CSD`, `Retron_VI__HTH`, `Retron_VIII__DUF626`,
`Retron_IX__HEPN`, `Retron_XIII__WHSWIM`, and whole-RT models `Retron_XI__RT_11`,
`Retron_XII__RT_12`, `Retron_I_C__RT_1_C{1,2,3}`, `Retron_VII_1__RT_7_A1`.

⚠️ **`pfam_rt.domtbl` (73,060 hits) is Pfam against the RT proteins**, not against the
accessory CDS. Pfam-vs-accessory is **Tier 1a, and it was never launched** (§9.3).

## 9.2 · ⛔ Retron AND non-retron — but they are NOT the same unit

**Retron arm — a CENSUS.** Full pass, no sampling.

    target: 78,287 unique retron rt_hashes  (p3z.log: "target unique retron rt_hashes: 78,287")
    result: 72,530 systems · 940,264 accessory CDS
    output: /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/cache/neighborhood_annotation/

**Non-retron arm — a STRATIFIED SAMPLE.** Not a census, and it must never be read as one.
From `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/x1_neighbourhood/cache/x2_draw.tsv`, verbatim header:

    # x2_draw_sample.py | UNIT = unique rt_hash | POPULATION = nonretron_no_multi = 415,681
    # seed=20260826 target=25000 floor=200; allocation formula in PREREG_X1.md s2
    # weight_f = N_f / 415681 -> the design-weighted pooled estimator. NEVER the raw sample mean.

    drawn:     25,000 rt_hashes
    recovered: 24,814 RT proteins -> 279,659 accessory CDS
    per-family recovery: /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/x1_neighbourhood/cache/neighborhood_nonretron/recovery_by_family.tsv

> ⛔⛔ **The two arms are a census (940,264 CDS) and a design-weighted sample (279,659 CDS).
> Never pool them, and never use the raw non-retron sample mean** — the estimator is
> `weight_f = N_f / 415,681`, fixed in `PREREG_X1.md` §2 **before** the draw.

## 9.3 · ⭐ The tier ladder — where it stopped, and why

`NEIGHBORHOOD_ANNOTATION_SPEC.md` status line, verbatim:
*"**Tier A running (local, borg). Tier 1 / Tier 2 specified, not launched.**"*

| tier | what | target | status |
|---|---|---|---|
| **A** | `hmmsearch --cut_ga` vs **1,139 DefenseFinder** profiles | accessory CDS + RT | ✅ **COMPLETE** |
| **B** | `hmmsearch --cut_ga` vs **39 Mestre retron** profiles | accessory CDS + RT | ✅ **COMPLETE — but ⛔ FIREWALLED (§9.4)** |
| **1a** | `hmmsearch --cut_ga` vs **Pfam 37.0 — 21,979 profiles** | same | ⛔ **SPECIFIED, NOT LAUNCHED** |
| **1b** | **full InterProScan, all 17 member DBs** | residual fused-effector RT proteins only — subtypes **I-C1/C2/C3, VII-A1, XI, XII** | ⛔ **SPECIFIED, NOT LAUNCHED** |
| **2** | build a query profile from **UniRef30_2020_06**, then `hhsearch` vs **pdb70** | fused-effector residuals | ⛔ **GATED** — UniRef30 extraction required |

⭐ **The spec pre-answers the obvious risk:** *"If Tier 2 cannot be unblocked at acceptable
cost, **Tier 1 still stands**. Fused-effector [residuals are] disclosed as a stated
limitation. **Tier 2 never blocks the job.**"*

⭐⭐ **So the single highest-value unrun step in this stage is Tier 1a** — one `hmmsearch`
against Pfam 37.0 over 940,264 proteins that are already extracted and on disk. It needs no
new extraction, no cluster job for the retron arm, and the database is already pinned.

## 9.4 · ⭐⭐ THE TIER-B FIREWALL — structural, evidenced, and it generalises

> **FIREWALL.** *"**Tier B may NEVER enter any analysis that also uses the subtype labels.**
> Specifically and by name: Tier B is excluded from the finding-#4 effector-vs-RT
> predictability analysis. Tier B is admissible for exactly one purpose: an
> **internal-coherence diagnostic** — 'does DefenseFinder's effector call agree with the
> subtype label DefenseFinder itself produced?' That is a QC statement about our annotation
> stack. It is never evidence about biology, and never evidence about Mestre's framework."*

**Why:** our **48,856** subtype labels come from PADLOC/DefenseFinder models that encode
Mestre's scheme. *"Scoring a Tier-B hit against a subtype label correlates a DefenseFinder
call with a DefenseFinder call."*

**The firewall is EVIDENCED, and the spec requires this table to be cited wherever the
firewall is described** — measured on the completed run (72,530 systems, 940,264 CDS):

| Tier-B profile | systems hit | % of systems |
|---|---:|---:|
| `Retron_II__NDT` | 5,066 | **6.99%** |
| `Retron_VI__HTH` | 4,456 | **6.14%** |
| `Retron_XIII__WHSWIM` | 4,415 | **6.09%** |
| `Retron__RT_Tot_7` | 4,307 | 5.94% |
| `Retron_I_A__ATPase_TypeIA` | 3,868 | 5.33% |

> Merging the tiers would have injected **>6% DefenseFinder-vs-DefenseFinder circularity**
> into the predictability analysis — **on the most frequent effector calls**, i.e. exactly
> the ones that would have driven the score.

**Enforcement, mechanical not advisory:** Tier A and Tier B hits go to **separate `.domtbl`
files** and to **separate, never-summed columns** of
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/tables/neighborhood_effector_composition.tsv`
— `acc_effectors_tierA` / `acc_effectors_tierB`, `rt_fused_tierA` / `rt_fused_tierB`.
*"Any script computing ARI / V-measure / predictability against subtype labels must read
**only** the `_tierA` columns. **A merged 'effector' column must not be created.**"*

⭐ **This is the best worked example of tool-circularity control in the project**, and it is
the template for `/home/borg/RETRON_STAGES/12_annotation_disagreement.md` and
`/home/borg/RETRON_STAGES/05_mestre_replication.md`: when a model set descends from the
scheme you are testing, split it off at the file level and forbid the merged column.

## 9.5 · Gate-A pinned resources — cite these in Methods

| resource | version | md5 | status |
|---|---|---|---|
| **Pfam-A** | **37.0** (in InterProScan 5.70-102.0) | `7d88757d30b089b9ed5758a0e12d5754` (`pfam_a.hmm`) | on Ibex; **pin the existing copy, no fetch** |
| **padlocdb CM set** | PADLOC-DB for padloc 2.x | `a482e6aa697e5bad8e8f377633f7d2e8` (`padlocdb.cm`) | on Ibex |
| **pdb70** (HH-suite) | `pdb70_from_mmcif_latest` | 8-file manifest at `databases/md5sum` | on Ibex, complete |
| **UniRef30** | 2020_06 | 6-file manifest `UniRef30_2020_06.md5sums` | ⛔ **incomplete — extraction required** |

**The spec's own Methods requirement, verbatim:** *"Methods must record: Pfam 37.0;
InterProScan 5.70-102.0; DefenseFinder model set as shipped; PADLOC-DB as shipped;
UniRef30_2020_06 and pdb70 if Tier 2 runs."*

## 9.6 · Answers, in one place

| question | answer |
|---|---|
| **Which tool?** | `hmmsearch --cut_ga --domtblout` (HMMER, `retron_tradicional`). Two profile sets: 1,139 DefenseFinder (Tier A) + 39 Mestre-derived (Tier B). No score/E override |
| **Retron only, or general?** | **Both, asymmetrically.** Retron = **census**, 72,530 systems / 940,264 CDS. Non-retron = **design-weighted sample**, 25,000 drawn of 415,681, → 279,659 CDS. ⛔ Different units, never pooled |
| **Where did it stop?** | Tier A ✅ · Tier B ✅ (firewalled) · **Tier 1a (Pfam 37.0) ⛔ not launched** · Tier 1b (InterProScan) ⛔ not launched · Tier 2 (hhsearch/pdb70) ⛔ gated on UniRef30 |
| **Cheapest next step** | **Tier 1a** — one `hmmsearch` vs Pfam 37.0 over proteins already extracted, database already pinned |
