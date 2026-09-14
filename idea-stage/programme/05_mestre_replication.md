# Stage 5 · Replicate and learn limitations and areas of opportunity from Mestre's work

## 0 · The point of this task

Mestre 2020 defines the reference retron classification that everything in this field is
measured against, including our own work. But its count is not algorithmically
reproducible from its stated method, and its 60% cutoff was set **after** scoring. We
currently cannot separate which parts of it are sound results, which are conventions, and
which are reading errors on our side. Once this lands we can say exactly what replicates,
what does not, and what the published work leaves open — including whether the
ncRNA-family-inside-clade nesting is a finding of ours or something their paper already
states. That decides how much of our classification work is a contribution and how much
is a reproduction.

## 1 · Where this stands — 🟢 done

| | finding |
|---|---|
| `B4` | Mestre's **membership is sound**; their **count is not algorithmically reproducible**. Four different values for the reference-set size appear across sources |
| `B3` | ⭐⭐ Their published clades **do separate in fold space** — silhouette **0.2565**, **z = 25.27**. Largest-cluster fraction not reported (`N9`); no phylogenetic null attempted |
| `C4` | ⭐ **The reference lab reported the same tree failure in print** (Toro 2018, verified verbatim by audit `A33`). This converts our largest negative into an **expected** one |
| lit | `mestre2020-60pct-cutoff-set-after-scoring` — their threshold was chosen after seeing the scores |
| lit | `mestre2020-retron-reference-set-1928`, `mestre-reference-count-four-values` |

**Method document:** `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X14_mestre_reconstruction.md`.
**Scripts:** `s2b_mestre_clade_monophyly.py`, `s5b_E4a_rule_D_on_mestre.py`.
**Data:** `/ibex/project/c2366/RETRONS/Mestre_replication/`; D2 = 1,928 `terminal_N/` dirs
(1,925 genomes, 1,926 proteins; missing `terminal_461`, `terminal_515`, `terminal_1774`).
**Structures:** `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/mestre/` — 1,919 folds on borg, **1,928 on Ibex**.

## 2 · ⛔ Two claims of ours that this stage killed

- `B6` **KILLED** — *"multi-axis classification is our contribution"* is **false. Mestre
  2020 got there first.** Ours is the **measurement**, not the idea. This must be fixed
  before any framing is written.
- `B5` **KILLED** — *"clade × subsystem is circular because Mestre used effectors to define
  clades"* is wrong in its reason: the **11 clades are phylogenetic**; the **13 types** are
  effector-defined. The demotion was right, the justification was not.

## 3 · What is left to do

- ⛔ `PE5` — **is the ncRNA-family-inside-clade nesting already stated in Mestre 2020?**
  This decides whether `R1b` is a **finding** or a **reading correction**, and it is
  urgent because `E6` shows **`msr_msd` is nested inside `clade`**: all 21 ncRNA families
  lie in exactly one clade, so **V = 1.0000 by construction** and **the axis count is TWO,
  not four**. Only 8 of 12 clades carry any ncRNA label.
- **Give `B3` the controls it never got** (`PE4`): does the fold-space clade separation
  survive a phylogenetic null and a largest-cluster-fraction check? ⚠️ Make this argument
  before a referee does.
- **State the areas of opportunity explicitly** — the reproducibility gap in their count,
  the post-hoc cutoff, and the fact that their own lab published the tree failure.

## 4 · Prerequisites and gates

- ⛔ **Stage D (relatedness controls) gates any co-variation claim built on this.** `B1` —
  four label sets co-vary — currently rests on a null that is **mathematically invariant**
  on the pair that matters (`E7`, sd = 0.000000).
- Stage B (the object register) — Mestre's object is one row in it, and the register is
  the natural home for *"what did each study actually align?"*

## 5 · Traps already paid for

- ⚠️ **The Khan panel cannot externally validate anything in the Mestre/Toro lineage** —
  **94.2% exact overlap** with `mestre_1928`; only **8 proteins** lie outside it.
- ⚠️ **All 21 PADLOC retron ncRNA covariance models are authored by Mestre**, and the
  DefenseFinder retron profiles were iterated to recover the known set. Per
  EVIDENCE_STANDARDS §3b, **models descending from one publication cannot corroborate each
  other** — declare this in any methods text.
- ⚠️ **Mine Methods and Limitations, not Results.** The competitor's concession lives in
  its limitations paragraph; Toro 2026's sat unquoted on our own disk for months.

---

# 6 · EVERY PATH NEEDED TO VERIFY OR RE-DO THIS
**Verified by direct inspection 2026-09-11.** Every path below was resolved; counts are
measured, not recalled. ⚠️ All prior artifacts are `[UNVERIFIED]` under WA-I.3 — they enter
a new row only as `RE-DERIVED` or `BLIND-CONFIRMED`, at the point of use.

## 6.1 · The claim to be checked, in its sharpest form

From `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X14_mestre_reconstruction.md`:

> **Mestre's 11 published clades are not algorithmically reproducible from their own
> published tree, and are recovered at ≤3 of 11 by independent re-inference — but their
> membership is sound and the groups are real.**

Object: `O7`. Findings: `G16, G50, G52, G54, G56, G69, G74`.

## 6.2 · Input data — published supplements (D3)

⭐ **Resolved here: the "two candidate roots" problem is NOT a conflict.** The four shared
files are **byte-identical** (md5 verified), and each root holds files the other lacks — so
they are **complementary, and you need both.**

    Root A: /home/borg/RETRON_CLAUDE_PART1/supplementary_material/
    Root B: /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/supporting_material/

| file | in A | in B | md5 (first 12) |
|---|---|---|---|
| `Supplementary_mestre_Tree.nwk` — the published tree | ✅ | ✅ | `73333b3d2d71` **identical** |
| `Suppl_Toro_Tree.txt` — Toro 2019, source of Mestre's population | ✅ | ✅ | `06767ea34e4a` **identical** |
| `Supp_material_T1_R1_systematic_prediction.csv` — per-tip clade/subtype | ✅ | ✅ | `86a31617e77e` **identical** |
| `supp_material_systematic_prediction_paper.csv` | ✅ | ✅ | `1f09f9cbb198` **identical** |
| `myRT-FastTree2.refpkg` — tree + alignment + HMM + model + mapping | ✅ | ✅ | not compared |
| `Mestre_supplementary_material.csv` | ✅ | ⛔ | **A only** |
| `toro_2014_Rt0-Rt7.FASTA` | ✅ | ⛔ | **A only** |
| `support.csv` — Khan gold panel, 175 rows | ⛔ | ✅ | **B only** |
| `taxonomy_lookup.tsv` · `gem_metadata.tsv` | ⛔ | ✅ | **B only** |

⛔ **`support.csv`: the protein is in `rt_protein_aa`, NOT `RT_sequence`** (which is empty).
⚠️ **The Khan panel cannot externally validate anything in this lineage** — 94.2% exact
overlap with `mestre_1928`; only 8 proteins lie outside.
→ **Action for the new session:** write `docs/decisions/` pinning **both** roots with
hashes, and record that the overlap is identical. Do **not** copy (`decisions/0004` §1).

## 6.3 · Input data — the downloaded benchmark (D2)

    /home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences/

**1,928 `terminal_N/` directories**, each with `genome.fasta.gz`, `protein_aminoacid.fasta`,
`protein_nucleotide.fasta`. 2.7 G, local borg disk (`IBEX_TESTS` is a folder name — no ssh).
⚠️ **This is our download, not a Mestre release.** Its provenance is in the same directory
and must be read before any count is quoted:

    Supp_material_with_download_status.csv    dead_accessions_manual_review.csv
    rescued_accessions.csv                   still_manual_review.csv
    wp_fix_report.csv                        retron_download.log
    retron_fix_wp.log                        retron_rescue.log

⚠️ Known gaps: `terminal_461`, `terminal_515`, `terminal_1774` missing → 1,925 genomes /
1,926 proteins against 1,928 members. **Four different values for the reference-set size
circulate** (`mestre-reference-count-four-values`) — establish which denominator you are on
before comparing anything.

Ibex mirror: `/ibex/project/c2366/RETRONS/Mestre_replication/genomes/` — **1,928** entries,
12 G decompressed. ⚠️ Identity vs the borg copy **never hash-compared**.

## 6.4 · The Mestre paper itself, on disk

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/lit_detector_audit/cache/Mestre2020_retron.txt    89 KB  (full text)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/lit_detector_audit/cache/Mestre2020_retron.html  276 KB  (mode rw-------)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/stage0_positioning/cache/mestre_pdf/mestre2020_layout.txt

⭐ Use it for `PE5` (*is the ncRNA-family-inside-clade nesting already stated in their
paper?*) and for the **Methods and Limitations** sections — the standing rule is *mine
Methods and Limitations, not Results*; a competitor's concession lives there.

## 6.5 · ⚠️ Mestre work is spread across FIVE stages, not one

### (a) `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/` — unit reconciliation, earliest arm
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/scripts/s06_mestre_unit_reconciliation.py      /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/scripts/s09_mestre_in_toro_frame.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_unit_reconciliation.tsv          /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_clade_counts.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_in_toro_frame_occupancy.tsv      /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_rt0_summary.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_retron_subsystem_counts.tsv      /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_faa_duplicates.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/tables/mestre_discrepant_ids.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/cache/mestre_from_V3/                          /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/cache/mestre_usable_index.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/responses/2026-08-16_r04_254-criterion_stratified-specificity_mestre-contamination.md

### (b) `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/` — the main arm (`V4T`)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s2b_mestre_clade_monophyly.py     ✅  -> /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s2b_mestre_clade_monophyly.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s5b_E4a_rule_D_on_mestre.py       ✅
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s5e_E4b_ruleD_on_our_trees.py     ✅  (the paired arm — X14 names it)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s7h_mestre_frames.py                  /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s7i_clade_support.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s8b_mestre_clade_structure.py         -> /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s8b_mestre_clade_structure.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s2c_mestre_intruder_identity.tsv       /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s5d_mestre_landmark_audit.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s5f_mestre_msr_msd_audit.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s5h_mestre_unmatched_groups.tsv    ⚠️ and _REGEN.tsv — **use _REGEN**
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_narrow.faa
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_wide.faa
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_ours.faa
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_toro.faa
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_tofold.faa     /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/mestre_trees/
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/mestre/                     1,919 ESMFold .pdb, 498 M
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fs_mestre/                       ava.tsv + 12 shards + foldseek DB
                                           (db, db_ca, db_h, db_ss + .dbtype/.index/.lookup/.source)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/FINDINGS.md                            carries G16, G50, G54, G56, G69, G74, G89

⭐ `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fs_mestre/ava.tsv` is **the input `PE1` requires** for the relatedness control
(stage D) — structure-based blocks, so they are not the c50 clusters that caused the
confound. It exists.

### (c) `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_paper/`
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_paper/cache/mestre_clust/        FINDINGS.md (G50, G54, G56, G69, G74, G89)

### (d) `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/stage0_positioning/` — did Mestre agree with themselves?
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/stage0_positioning/scripts/sA_mestre_selfconsistency.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/stage0_positioning/tables/mestre_selfconsistency.tsv          /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/stage0_positioning/tables/mestre_methods_parameters.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/stage0_positioning/tables/mestre_rooting_sensitivity.tsv
⭐ `mestre_methods_parameters.tsv` and `mestre_rooting_sensitivity.tsv` are where the
*"60% cutoff set after scoring"* and the reproducibility gap are quantified.

### (e) Stages whose FINDINGS/VERDICT inherit the Mestre numbers
`s6_trees` (G50, G69, G74) · `s3_object` (G74) · `s4_motifs` (G74) ·
`s7_classification` (G89) · `s1_review` (G89) · `rt0_rt7_lit_and_narrative` (G74).
⚠️ `G74` appears in **nine** files — if it moves, all nine move.

## 6.6 · ⭐ The Ibex replication pipeline — 83 GB, and it actually ran

    /ibex/project/c2366/RETRONS/Mestre_replication/          83 G

| path | measured | note |
|---|---|---|
| `genomes/` | **1,928** | the benchmark, decompressed |
| `realpipe/results/` | **3,854 files** | the run's outputs |
| `realpipe/processed_genomes.txt` | **537 lines** | ⚠️ **537 of 1,928 — the run is INCOMPLETE.** Any rate from it has a 537 denominator, not 1,928 |
| `realpipe/stock_verdicts.tsv` | — | the per-terminal verdict table (columns below) |
| `realpipe/logs/` · `realpipe/attempt1_failed_env/` | — | ⭐ a **preserved failed attempt** — read it before re-running |
| `ids_69.txt` | **68 lines** | ⚠️ **named 69, holds 68.** Header, or an off-by-one. Resolve before quoting "69" |
| `m8_mestre_validation_ibex.sh` · `m10_mestre_realpipe_ibex.sh` · `m11_relaxed_cm_axis.sh` | — | the pipeline drivers |
| `m12_extract_stock_verdicts.py` · `m13_characterise_69.py` | — | the analysis scripts |
| `hmm/` | `df_tierA.hmm`, `df_tierB.hmm`, `myrt.hmm` (+ h3i/h3m/h3f/h3p), `.ready` | the models used |
| `models/` | ⛔ **EMPTY** | listed but holds nothing — do not plan on it |

**`stock_verdicts.tsv` columns:**

    terminal · integrated · n_systems · n_retron_systems · system_types ·
    n_ncrnas_total · ncrna_models · ncrna_best_evalue · ncrna_best_score ·
    any_ncrna · rt_gene_ids · n_high_conf · ncrna_types

⭐⭐ **`system_types` carries all three tool labels on one row** — e.g.
`RVT-Retrons;Retron;retron` = myRT ; DefenseFinder ; PADLOC. **This file is
three-tool-agreement data at the terminal level**, and it is stage 12's raw material, not
just a Mestre artifact. ⚠️ And `ncrna_types` shows `msr-msd;unknown` — the `unknown` class
is stage 12's disagreement population.

## 6.7 · Detection models used (D6), and the corroboration trap

    PADLOC:  /home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm/padlocdb.cm       21 retron ncRNA CMs
             /home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm_meta.txt        CM -> Mestre RT-clade map
             /home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/sys/retron_*.yaml  18 subtype rules
             /home/borg/miniconda3/envs/padloc2/data/cm/padlocdb.cm   mirror, identity UNVERIFIED
    DefenseFinder: /home/borg/.macsyfinder/models/defense-finder-models/profiles/*Retron*   ~39 HMMs
    myRT:    /home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/HMM/RVT-All.hmm  + family FASTAs  (~2,051 seeds / 47 families)
    Ibex run copies: /ibex/project/c2366/RETRONS/Mestre_replication/hmm/{df_tierA,df_tierB,myrt}.hmm

⛔ **All 21 PADLOC retron CMs are authored by Mestre**, and the DefenseFinder retron
profiles were iterated to recover the known set. Per EVIDENCE_STANDARDS §3b, **models
descending from one publication cannot corroborate each other.** State this in any methods
text. It is also why §6.6's three-tool agreement is *not* independent validation.

## 6.8 · Reports and verdicts to read, in order

    1. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X14_mestre_reconstruction.md   the method + the claim
    2. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X15_label_concordance.md       the "so what", and its contested null
    3. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X16_structural_clade_separation.md   fold-space separation (B3)
    4. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/CLAIM_REGISTER.md                         rows B3, B4, and ⛔ killed B5, B6
    5. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/FINDINGS.md               G16/G50/G54/G56/G69/G74/G89
    6. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s7_classification/VERDICT.md                              what the concordance does and does not show
    7. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/crosscheck/VERDICT.md                                     cross-section consistency (78 of 81 agree)
    8. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/adversarial/VERDICT.md                                    what a hostile referee breaks first
    9. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/DEBATE_QUEUE.md                           D0, D1, D1b — still open

⚠️ `crosscheck/FROZEN_DENOMINATORS.tsv` contains **no** Mestre or clade row — so the
Mestre denominators were never frozen. That is a gap, not an oversight to inherit.

## 6.9 · Recipe to re-do the cross-check

1. **Pin D3.** Hash both roots, record that the four shared files are identical, write the
   decision record. Nothing else can be cited until the root is named.
2. **Settle the denominator.** 1,928 members / 1,925 genomes / 1,926 proteins / 537
   processed / 68-or-69 ids. Pick one, name it, and put it in every table header.
3. **Re-derive the clade recovery** with `s2b_mestre_clade_monophyly.py` against
   `Supplementary_mestre_Tree.nwk` + `Supp_material_T1_R1_systematic_prediction.csv`.
   The claim to beat: **≤3 of 11 recovered by independent re-inference.**
4. **Re-derive the fold-space separation** (`s8b_mestre_clade_structure.py`) from
   `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/mestre/` + `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fs_mestre/ava.tsv`. ⚠️ `PE4` — give it the controls it
   never got: a phylogenetic null and the largest-cluster fraction.
5. **Run `PE5`** against `Mestre2020_retron.txt` — is the ncRNA-nesting already theirs?
   This decides finding vs reading-correction, and `E6` makes it urgent.
6. **Do NOT rebuild the concordance** until stage D supplies a null that can move
   (`E7`: sd = 0.000000). Order is fixed (`D0`): ① mark missing → ② `NA..H` re-cut →
   ③ phylogenetic null.
7. **Harvest §6.6's `stock_verdicts.tsv` for stage 12**, not for stage 5. It is the best
   three-tool table in the project and it is filed under the wrong stage.
