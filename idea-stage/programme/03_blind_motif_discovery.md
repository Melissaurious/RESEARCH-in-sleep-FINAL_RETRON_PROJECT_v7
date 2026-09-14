# Stage 3 · Blind discovery of motifs per RT family

## 0 · The point of this task

Sequence and structural studies defined the motifs of reverse transcriptases — and some
specific to retrons — decades ago, on tens of sequences, and three separate naming systems
have been layered on them since without anyone mapping one onto another. So we cannot
currently say which features are informative about family membership and which are simply
"this is an RT", nor even state which published motif our own "tetrad" corresponds to.
Once this lands we can state, per family and blind to the published expectation, which
positions are constrained, which residue satisfies each constraint, and where the insertion
motifs sit relative to the catalytic motif — with every number on a named denominator.
That converts inherited assertions into measurements, and tells the classification work
which axes carry information.

## 0a · ⭐ Three naming systems for the same residues, and no map between them

| system | source | names |
|---|---|---|
| **motifs A–D** | Poch et al. 1989 | `motif A`, `motif B` = `(S/T)GxxxTxxxN(S/T)`, **`motif C`** *"embedded in hydrophobic residues"* — the one carrying the aspartates — `motif D` |
| **RT1–RT7** | Xiong & Eickbush 1990 | seven blocks, from **42 conserved positions** |
| **"the tetrad"** | ours | the 4 residues `YxDD` — observed as `YADD`, `YMDD`, `YSDD`, `WMDD`. **`RT5`'s block spells `YADD`** |

⛔ **`the tetrad` ≈ Poch's motif C ≈ (part of) RT5, and that correspondence is nowhere
stated in our record.** Every result in this stage is reported in the third system, which
is the one with no publication behind it.

⭐ **Consequence, and it is cheap:** a three-column correspondence table is a deliverable of
this stage and a row of the object register (stage B). It also disambiguates the trap
below: **"position 1" is the `Y`/`W` of `YxDD`; "position 2" is the `x`.**

Primary sources, on disk:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Poch Sauvaget Delarue Tordo 1989 EMBO J - Identification of four conserved motifs among the RNA-dependent polymerase encoding elements.pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Origin and evolution of retroelements based upon their reverse transcriptase sequences. .pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/A diversity of uncharacterized reverse transcriptases in bacteria .pdf

⚠️ **None of the three is cited anywhere in `s4_motifs`.** They were on disk throughout.

## 1 · Where this stands — 🟡 the discovery holds; three derived claims did not

Run as `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/`
(registered beforehand as `PE12`, from the operator's own question).

### ⭐ What survived, and survived attack

**General to reverse transcriptases:** a **constraint at tetrad position 2, in 40 of 40
families, at less than half the entropy of position 1** — and position 1 is the position
this project had never varied.

**Family-specific:** *which* residue satisfies it — retrons **A**, DGRs **M**,
`RVT-AbiP2` **R at 85%**, `RVT-UG28b` **C at 86%** — and *where* the interdomain-insertion
motifs sit: **region X is fixed 93 residues upstream of the tetrad in retrons, IQR 9
residues**, positionally diffuse in the two families the literature names as lacking it.

⭐ **`R1`, the strongest result here:** re-run **uncapped at full scale (340,931 sequences)**,
**0 of 40 top tetrads change**, and `A3` reproduced exactly.

> ⚠️ **But scope the word "blind" precisely.** `R1`'s own verdict: *"the blind discovery is
> robust to the cap; **the entropy beside it is not**."* Blindness and robustness attach to
> **which tetrad is top per family**, not to the entropy ranking computed alongside it.

### 🔴 What failed — and the failures are more instructive than the summary

**`V3` / `G63` — REFUTED, and not by rarefaction.** Verdict, verbatim: *"**False at full n,
on its own data.** Retron is **8th of 40**; **the seven lower families were hidden by the
script's `abs(z) > 1.0` display filter**, and **the script writes no artefact**."*
`C12` was **dropped under `Q-5`'s pre-registered rule** — a rule declared in
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_claim_ledger/PROPOSED_ANALYSES.md`
**before any of this ran**.
*(🔴 Denominator corrected 2026-08-26: **"8th of 40"**, not "of 42" — the rank was right,
the denominator was not. `G63`'s 42 was its own glob: 40 real family labels + `MULTI` + the
merged corpus.)*

⭐ **Three independent defects in one claim: a display filter that hid every
counter-example, a script that wrote no artefact, and a glob for a denominator.** That is
the shape to check for elsewhere, not a one-off.

**Tetrad entropy cannot be ranked across families**, even after rarefaction.

🔴 **`G28` rests on an ORPHANED table.** From `FINDINGS.md`: *"`rt0_rt7_domain_test_v4_and_tree/tables/s4f_pssm_crossfamily_masked.tsv` — the table `G28`
rests on — is **ORPHANED**. Swept `v3/scripts` and `v4_and_tree/scripts`: **no script writes
it.** `s4e_pssm_admission_filter.py` computes the masked threshold but **never emits that
table**. It was re-implemented here to be checkable at all."*
⚠️ **"Orphaned" does not mean missing — it means unproduced.** The file **is on disk**
(`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s4f_pssm_crossfamily_masked.tsv`,
491 bytes). It looks fine. **Nothing regenerates it**, so it cannot be checked, only
trusted — which is strictly worse than an absent file, because an absent file announces
itself.

⭐ On re-implementation it **does** reproduce — masked threshold recalibrates to
**−36.981**, the header value **to three decimals**, and all eight published rows return
within **2.5 points** (largest deviation `RVT-DGRs`, 46.1 → 43.6). **The number was right;
the provenance did not exist.**

⚠️ **And the denominator error was pre-registered.** `Q-5`'s own title reads
*"Reconstruct G63 — position-1 constraint across **42 families**"*. The 42 entered at the
pre-registration, not at the analysis — so **a pre-registered quantity can still carry a
wrong denominator**, and pre-registration does not substitute for asserting the population.

### Adjacent, and a different result

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/denovo_family/` ran de novo **ncRNA**
motif discovery with CMfinder; its **positive control FAILED at 6/17 = 35.3%** against a
≥50% bar. ⭐ The failure is **delimitation, not detection** — CMfinder places a motif *on*
the true msr-msd at **12/17 (70.6%)** covering only **~24%**. See `/home/borg/RETRON_STAGES/A_delimitation.md`.

## 2 · What is left to do

- ⭐ **The three-system correspondence table** (§0a) — Poch A–D ↔ RT1–RT7 ↔ tetrad/position.
  Cheap, publishable as part of the object register, and it is the thing that lets anyone
  else read our results.
- **Re-derive under current standards and bundle.** The discovery is strong but
  `[UNVERIFIED]` here, and one of its supporting tables had no producer until it was
  re-implemented.
- ⛔ `PE15` — **source the character class, or withdraw it.** Where do `W` and `H` in
  `[YFWH].DD` come from? Never run. It matters because `A10` is killed: **`[YFWH].DD` is
  ours, not the field's** — published tools admit by HMM bit score. And `[YFWH]` is a claim
  about **tetrad position 1** specifically (§0a).
- **Protein motifs at family level are done; ncRNA motifs are not**, and are gated on
  delimitation rather than on more discovery.
- ⚠️ **Sweep for the `G63` defect shape elsewhere**: display filters that suppress
  counter-examples, scripts that emit no artefact, globs used as denominators.

## 3 · Traps already paid for

- ⛔ **Never pool across families.** `PQG[GA]` reads **41.78% pooled** and **0.373%
  median-family** — a **112× gap**. A pooled cross-group rate is the biggest group's rate.
- ⭐ **Rarefaction needs replicates — and this stage is where that was learned and fixed.**
  `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/scripts/v2r1_uncapped_rarefied.py`
  rarefies to **n = 153 with 25 replicates and a recorded seed**, and emits
  `rank_rarefied_min/max` spanning the draws — because *"a single draw at n = 153 is itself
  a random variable."* **Reuse this, do not re-invent it.**
- ⚠️ **A superlative read off a console is unfalsifiable.** `G63` is the case: the display
  filter hid all seven counter-examples and the script wrote no table.
- ⚠️ **Do not cite Simon & Zimmerly 2008 as licensing `[LIV]`** — their *"x is nearly always
  hydrophobic"* is about **position 2**; our excluded class differs at **position 1**
  (`D10`). §0a's naming table is what keeps these straight. Same shape as `L04`, where
  `YIDD` was treated as excluded although it matches `[YFWH]` at position 1.

## 4 · Prerequisites

`/home/borg/RETRON_STAGES/01_database_characterization.md` for the population;
`/home/borg/RETRON_STAGES/02_rt0_rt7_definition.md` or
`/home/borg/RETRON_STAGES/04_palm_fingers_thumb_yxdd.md` for the frame positions are
measured against — *"93 residues upstream of the tetrad"* is meaningless until the anchor is
declared. ⚠️ And per `/home/borg/RETRON_STAGES/I_non_retron_reference_set.md`, the
general/family-specific split needs the **non-retron reference set** to mean anything.

---

## 5 · EVERY PATH NEEDED TO VERIFY OR RE-DO THIS
**Verified by direct inspection 2026-09-12.** All paths absolute and `test -e` checked.
⚠️ Everything is `[UNVERIFIED]` under WA-I.3 — it enters a new row only as `RE-DERIVED` or
`BLIND-CONFIRMED`, at the point of use.

### 5.1 · The stage itself

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/        19 scripts, 24 tables

Read in this order:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/VERDICT.md       ⭐ start here
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/FINDINGS.md      56 KB, the detail
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/REPAIR_LOG.md    21 KB ⭐ what was broken and how it was fixed
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/S2_REVIEW.md     27 KB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/S3_REVIEW.md     11 KB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/PROPOSALS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/PLAN.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/STATUS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/responses/01_2026-08-25_s4_motifs.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/responses/02_2026-08-25_s2_review.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/responses/03_2026-08-26_landmark_register.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/responses/04_2026-08-26_denominator_repair.md

### 5.2 · Script → table, by result

All under `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/`.

| result | script | table(s) |
|---|---|---|
| ⭐ **generality / family-specific split** | `scripts/f2_generality_decomposed.py` | `tables/f2_generality_by_family.tsv`, `tables/f2_tetrad_inheritance.tsv` |
| ⭐ **tetrad positions 1 and 2** | `scripts/r2_position1_and_2.py` | `tables/r2_position1_and_2.tsv` |
| ⭐ **region X positional (93 aa, IQR 9)** | `scripts/p1_regionx_positional.py` | `tables/p1_regionX_dispersion.tsv`, `tables/p1_regionX_positional_vs_freetext.tsv`, `tables/p1_regionXY_freetext.tsv` |
| region X/Y band sweeps | `scripts/p1b_band_sweep.py`, `scripts/f1b_regionY_band_sweep.py` | `tables/p1b_band_sweep.tsv`, `tables/f1b_regionY_band_sweep.tsv` |
| landmark register | `scripts/f1_landmark_register.py` | `tables/f1_landmark_register.tsv`, `tables/f1_landmark_positional.tsv` |
| recall cliff | `scripts/f3_recall_cliff.py` | `tables/f3_recall_cliff.tsv` |
| ⭐ **rarefaction, 25 replicates** | `scripts/v2r1_uncapped_rarefied.py` | `tables/v2r1_uncapped_rarefied.tsv` |
| 🔴 **`G63` re-derivation (REFUTED)** | `scripts/v3_position1_rarefied.py` | `tables/v3_position1_rarefied.tsv` — *"two units"* |
| 🔴 **the orphaned-table re-implementation** | `scripts/v4v5_pssm_masked_and_training.py` | `tables/v4_pssm_masked_vs_full.tsv`, `tables/v5_pssm_columns.tsv`, `tables/v5b_score_decomposition.tsv` |
| matched recall | `scripts/v4b_matched_recall.py` | `tables/v4b_matched_recall.tsv` |
| ⭐ **lineage blocks** (the relatedness control for motifs) | `scripts/v6_lineage_blocks.py` | `tables/v6_lineage_blocks.tsv` |
| ⭐ **denominator objects** | `scripts/rp1_denominator_objects.py` | `tables/rp1_denominator_objects.tsv` |
| s3a re-derivation | `scripts/v1_rederive_s3a.py` | `tables/v1_s3a_rederivation.tsv` |
| review checks | `scripts/rv1_s3_review_checks.py`, `scripts/rv1b_g74_ratio.py`, `scripts/rv2_s2_draft_numbers.py`, `scripts/rv3_s2_architectural_row.py` | `tables/rv1_s3_review_checks.tsv`, `tables/rv1b_g74_ratio.tsv`, `tables/rv2_s2_draft_numbers.tsv`, `tables/rv3_s2_architectural_row.tsv` |
| boundary fingerprint | `scripts/boundary_fingerprint.sh` | — |

Cache (4 files):
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s4_motifs/cache/` —
`f1_landmark_positional.tsv`, `f1_landmark_register.tsv`, `f2_generality_by_family.tsv`,
`f2_tetrad_inheritance.tsv`.

⭐ **`v6_lineage_blocks.py` is the motif-side relatedness control** and belongs in the
conversation with `/home/borg/RETRON_STAGES/D_relatedness_controls.md` — a "family-specific"
motif claim is a lineage claim.

### 5.3 · The pre-registration, and the defect artifacts

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_claim_ledger/PROPOSED_ANALYSES.md
        ^ Q-5, line 41. ⚠️ its own title says "across 42 families" - the wrong denominator
          entered at pre-registration, not at analysis.

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s4f_pssm_crossfamily_masked.tsv
        ^ 491 bytes, EXISTS, and no script writes it
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s4e_pssm_admission_filter.py
        ^ computes the masked threshold, never emits the table

### 5.4 · Primary sources — all on disk, none cited by the stage

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Poch Sauvaget Delarue Tordo 1989 EMBO J - Identification of four conserved motifs among the RNA-dependent polymerase encoding elements.pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Origin and evolution of retroelements based upon their reverse transcriptase sequences. .pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/A diversity of uncharacterized reverse transcriptases in bacteria .pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Zimmerly Hausner Wu 2001 NAR - Phylogenetic relationships among group II intron ORFs (defines RT subdomain 0).pdf

### 5.5 · Inputs — the population (identical to stage 2's tier 3)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign/step4_scoring/cache/corpus/
        ^ 21 chunks, 501,561 sequences. ⚠️ in V3.
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/retron.faa      78,287
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/nonretron.faa  423,274

⚠️ `R1` ran **uncapped at 340,931 sequences** — a third denominator again. **Name which of
501,561 / 423,274 / 340,931 / 78,287 any figure is on.**

### 5.6 · The adjacent ncRNA arm

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/denovo_family/VERDICT.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/denovo_family/PREREG.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/denovo_family/tables/d07_localisation_secondary.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/scripts/          ⭐ the CM/boundary arm

### 5.7 · Recipe to re-do

1. **Write the three-system correspondence table first** (§0a). Every later number is
   reported in a naming system with no publication behind it; the table is what makes the
   results legible to anyone else, and it costs a day of reading.
2. **Assert the denominator before anything** — 40 family labels, not 42, and name which
   sequence count the figure is on (§5.5). `rp1_denominator_objects.py` is the precedent.
3. **Re-derive the generality split** (`f2_generality_decomposed.py`) and the tetrad
   positions (`r2_position1_and_2.py`). The claim to beat: **position 2 constrained in
   40 of 40 families at <half the entropy of position 1.**
4. **Re-run the rarefaction with the existing 25-replicate machinery**
   (`v2r1_uncapped_rarefied.py`) — do not re-invent it, and report `rank_*_min/max`.
5. ⛔ **Do not re-report any entropy ranking across families.** It did not survive, and
   `R1` scopes robustness to *which tetrad is top*, not to the entropy beside it.
6. ⛔ **Run `PE15`** — source `W` and `H` in `[YFWH]`, or withdraw the class. §0a says it is
   a claim about tetrad position 1, and `D10` is the trap waiting if it is confused with
   position 2.
7. **Sweep for the `G63` defect shape** — display filters, scripts emitting no artefact,
   globs as denominators. Two of the three are already known to recur elsewhere.

---

## 6 · METHODS AND TOOLS — what was used, and what "blind discovery" actually means
**Established by reading the 19 scripts, 2026-09-12.**

### 6.1 · ⛔ No structures and no structural methods were used in this stage

| check | result |
|---|---|
| scripts invoking foldseek / DSSP / ESMFold / TM-score / pLDDT / `.pdb` | **0 of 19** |
| non-stdlib imports across all 19 scripts | **none** — only `pathlib`, `collections`, `csv`, `gzip` |
| external binaries called | **none** — no HMMER, MAFFT, cd-hit, MMseqs, Infernal, anything |

**`s4_motifs` is a re-analysis stage over precomputed per-family sequence tables**, not a
pipeline that runs tools. Its input is:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v3/cache/s1a/
        47 files. Columns: rt_hash · family_file · strand · seq_len · starts_M ·
        ends_stop · partial · start_type · seq
        Retron.tsv.gz = 78,292 data rows

⭐ **Where "structure" appears in the record, it is inherited or figurative, not done here:**
one script comment refers to *"the five consensus blocks S1 recovered by structural probe"*
(a result taken from `s1_review`); `FINDINGS.md`'s *"the structure is relatedness, not
length"* uses *structure* in the statistical sense; and *"§1.7's structural claim also holds
on all 26 blocks"* is §1's claim being re-tested on sequence.

### 6.2 · ⭐⭐ What "blind discovery" precisely means — two different operations

The stage title flattens two things that must not be quoted as one:

| operation | what it is | script |
|---|---|---|
| ⭐ **enumeration** — genuinely data-driven | the `..DD` frame is **given** (the catalytic aspartates); **x1 and x2 are counted from the data** per family via `collections.Counter`, with the unit declared as *"(protein, distinct `..DD` tetrad) pairs"* | `scripts/r2_position1_and_2.py`, `scripts/v1_rederive_s3a.py` |
| ⚠️ **re-measurement** — **not** discovery | four **pre-specified literal regexes** counted per family: `[VIL]TG` (RegionY), `PQG[GA]`, `GAPTS`, `[YFWH].DD` (anchor) | `scripts/f2_generality_decomposed.py` |

> **So "blind" attaches to the enumeration of x1/x2 inside a fixed `..DD` frame.** The named
> motifs were **specified in the script**, not discovered — they are the published patterns
> being re-measured at scale, which is `PE12`'s actual brief.

⚠️ **`[YFWH].DD` is one of the pre-specified patterns** — so the character class disputed by
`PE15` / `A10` is an *input* to this stage, never an output of it. It cannot be defended by
anything measured here.

### 6.3 · ⛔ No de novo motif-discovery algorithm was used, and none is installed

    meme      ✗ absent locally
    streme    ✗ absent locally

**There is no MEME-suite equivalent on this machine.** Every "motif" result in this stage is
regex counting plus 4-mer enumeration. That is a defensible method and it scales — but the
stage cannot claim *de novo discovery* in the sense the phrase normally carries, and a
reviewer will read the title that way.

⭐ The project's only true de novo motif discovery is on the **ncRNA** side —
`cmfinder.pl`, used by `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/denovo_family/`
— and its positive control failed (§1).

### 6.4 · Tools actually available, verified 2026-09-12

**Local — `/home/borg/miniconda3/envs/retron_tradicional/bin/`**

    hmmsearch  hmmbuild  hmmalign      profile HMMs
    mafft  muscle                      alignment
    cd-hit  mmseqs                     clustering / redundancy reduction
    blastp                             similarity search
    trimal                             alignment trimming
    cmsearch  cmbuild  cmfinder.pl     covariance models, ncRNA de novo
    mkdssp                             secondary structure from coordinates

**Local — elsewhere**

    /home/borg/miniconda3/envs/esmologs/bin/foldseek        structural search / 3Di
    /home/borg/miniconda3/envs/foldmason/bin/foldmason      structural MSA
    /home/borg/miniconda3/pkgs/foldmason-4.dd3c235-h5021889_0/bin/foldmason
    /home/borg/.local/bin/RNAfold                           RNA secondary structure

⚠️ **foldseek is NOT in `retron_tradicional`** — it is in `esmologs`. foldmason has **both**
a package copy and its own env; prefer the env.

**Ibex**

    module load esm/1.0.3
    module load foldseek/10-941cd33      -> /ibex/sw/rl9c/foldseek/10.941.33/linux_binary/foldseek/bin
    export PATH=/ibex/user/rioszemm/conda-environments/<env>/bin:$PATH
    AlphaFold databases: /ibex/reference/KSL/alphafold/{2.1.1,2.3.1,3.0.0}

⚠️ **InterProScan here ships a stub database** — Pfam-A holds 3–4 profiles, TIGRFAM 1. Pfam-A
37.0 (21,979 models) exists only on Ibex at
`/ibex/user/rioszemm/the-retron-project/src/interproscan/interproscan-5.70-102.0/data/pfam/37.0/pfam_a.hmm`.

### 6.5 · ⭐ What a structure-informed version of this stage would use

The motif question has a structural form that has never been asked: **does a motif's
conservation track its structural role?**

- **`mkdssp`** on the 25 crystals → secondary structure per motif position. The
  boundaries are already extracted in
  `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/reference_boundaries.json`.
- **`foldseek` 3Di** over the 9,965 mapped predicted structures → whether the tetrad's
  structural neighbourhood is conserved where its sequence is not.
- **Region X at "93 residues upstream, IQR 9"** is a *sequence* distance. Its structural
  distance is computable and is a different, stronger claim.
- ⚠️ **Caution carried from stage 2:** 3Di is a *neighbourhood* code — truncation shifts
  states even far from the cut, so this must run on full-length folds (`cache/fold/pdb/`),
  not span-sliced ones.

### 6.6 · ⭐ One piece of discipline to copy verbatim

The header of `tables/f2_generality_by_family.tsv`:

> `# 39 non-retron families >=100 rows; MULTI and the union file excluded.`
> `# others_pooled_pct is divided by 415682 ROWS (415670 unique proteins), THIS script's`
> `# pool -- NOT f1's PRIMARY 423286 and NOT its ROBUST 415693.`

**A table header that names its own denominator and distinguishes it from two other
denominators in the same project.** That is the standard. ✅ And the producing script
explicitly skips the union file (`if p.name == UNION: continue`), so the 924,847 glob defect
did **not** recur here — checked.
