# M1 — Forensic audit of historical Mestre 2020 reproduction attempts

**Date:** 2026-09-18 · **Worktree:** `RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit`,
branch `worktree-mestre-audit` (base `53ce532`) · **Governance:** `general @ cff9831` (read
from the main checkout; the submodule is not initialised in this worktree).

**Scope.** This is an asset, provenance and implementation audit, plus one verification rerun.
No historical directory was modified; the V4 audit checked this by mtime. M1 inferred no tree,
placed no sequence and used no network. Stage M2 is **proposed only**
(`proposed/LAUNCHER_M2_historical_classification_expansion.md`) and must not run without the
operator's approval.

⚠️ **Brief note.** The M1 request this session received begins at *"Mandatory historical roots"*.
If an earlier part of the brief set further M1 deliverables, they are not reflected here.

**Companions**

| file | content |
|---|---|
| `STAGE05_PATH_REGISTER.tsv` | every path named in `RETRON_STAGES/05_mestre_replication.md` (113 rows), with existence, size and sha256 or a directory-manifest hash |
| `CROSS_ROOT_IDENTITY.tsv` | 869 Mestre-related files across all roots, grouped by sha256 into 520 distinct contents |
| `ASSET_REGISTER.tsv` | 355 assets from the three sub-audits, with producer, inputs, record count, identity group and a reuse grade |
| `subaudits/{v4,v2_v3_v5,retron_db}/` | per-lineage forensic accounts and their re-run evidence |
| `rerun_retron_db_stage1/` | the two reruns of the retron-db bundle, the byte comparison and the one-line remap diff |
| `scripts/m01–m03` | producers of the three registers |
| `ibex_audit/` | *(addendum)* the bounded Ibex inventory script and the borg-side comparator `m05` |
| `subaudits/rt07/` | *(addendum)* historical RT0–RT7 asset inventory and Toro-frame measurements |
| `m2_design/`, `scripts/m04, m06, m07` | *(addendum)* query census and MCC feasibility probes |

Every number below was measured in this session, by me or by a sub-audit whose script and
output are landed here, unless it is attributed to a prior document.

---

## 1 · Verdict on the operator's hypothesis

> *"`/home/borg/RESEARCH-retron-db` contains the final or most mature historical
> Mestre-reproduction attempt."*

**Partly supported.** It is the latest attempt, the most rigorous, and the only reproducible
one. It is **not a superset** of earlier work: it is a narrower, divergent re-implementation.

| test | evidence | result |
|---|---|---|
| latest | retron-db Mestre work dates 2026-09-11/12 (commits `3972c06`, `76ad2af`, `274046c`); V4's arms end 2026-08-27; V5 ends 2026-09-03 | ✅ latest |
| code lineage | **no Mestre script is byte-identical across any two roots** (`CROSS_ROOT_IDENTITY.tsv`). retron-db `s01` re-implements V4's `s2b` + `s5b`; `s02` keeps `s8b`'s true-label silhouette but replaces its null | independent re-implementation, not a copy |
| reproducibility | M1 rerun (§5): 18/18 tables + `BLIND_CONFIRMATION.tsv` byte-identical after one declared remap | ✅ the only reproducible Mestre result on disk |
| scope | its launcher §2 **excludes** tree re-inference, the label-concordance null and the three-tool Ibex verdicts | ❌ not a superset |
| dropped arms | V4's re-inference (six IQ-TREE trees, `s7h`/`s7i`), V4's pLDDT≥90 fold arm, V3's Ibex realpipe verdicts | **divergent** |
| placement | only `stage3_placement_toolkit`: a LIGHT tooling bundle, EPA-ng smoke run on n = 20 | not a reproduction |

**So:** for questions answered **on Mestre's published tree and table** (join, monophyly,
delimitation sweep, ncRNA nesting, paper reading, Khan overlap, accession recovery), retron-db
supersedes V2–V5. For **tree re-inference**, V4 is the only attempt, and nothing supersedes
it. That attempt is itself compromised (§3.2).

---

## 2 · Chronology and implementation lineage

| when | root | Mestre work | nature |
|---|---|---|---|
| 2026-03-08 | `RETRONS_january_2026/…/Mestre_sequences` | download of 1,928 terminals, plus the rescue pass (script on Ibex, not on borg) | **the one sequence source every later tree consumed** |
| 2026-07 | V2 (no commits) | supplement copies; placement *planned*, "not yet run" | no Mestre tree |
| 2026-07-22 → 08-06 | V3 (no commits) | `mestre_scope_audit` (Ibex realpipe `m8`–`m13`), `recover_mestre_reference.py`, an unexecuted `epa_loo.sh` | detector-verdict audit; **no Mestre tree** |
| 2026-08-06 → 08-27 | V4 (not git) | `stage0_positioning` (self-consistency, 200-taxon pilots), `rt0_rt7_domain_test` (unit reconciliation), `…_v4_and_tree` (monophyly, Rule D, **six re-inferences**, ESMFold + foldseek), `25_august_paper_positioning` X14–X16 | **the only re-inference** |
| 2026-08-31 → 09-03 | V5 (git, 3 commits) | research-wiki claim pages only | no computation on Mestre |
| 2026-09-11 → 09-12 | retron-db (git) | `stage1_mestre_replication_and_insights` (4 seals), `stage3_placement_toolkit` | published-tree replication plus tooling |

Data flow (sha256-traced): the V3 `mestre_1928_proteins.faa` **is** the V4
`mestre_1926_proteins.faa`, same bytes under a different name (identity group `G0083`). V3's
`mestre_1926_vs_RT17CORE.sto` was copied into V4 (`G0082`). retron-db reads V4's folds and
TM matrix in place. So the benchmark download → V3 → V4 → retron-db is **one sequence
population**. Every "replication" that rests on sequences inherits its substitutes (§3.1).

---

## 3 · Findings that change what can be cited

### 3.1 ⛔ 112 benchmark proteins are not Mestre's, and 15 are RNA polymerase subunits

The 2026-03 rescue pass replaced 184 partial terminals by searching for the same species,
then genus, then NCBI, and accepting a product-annotation match. The match was not specific
to RTs.
- **112** terminals carry a `|rescued` protein that is **not** the published accession.
- **15** of those (116, 295, 565, 731, 1086, 1186, 1282, 1327, 1343, 1350, 1367, 1387, 1560,
  1804, 1915) are **DNA-directed RNA polymerase subunits**
  (`subaudits/v2_v3_v5/v235_rnap_substitutes.tsv`). 7 of the 15 are same-taxid rescues, so
  V5's framing "version drift, nothing to fetch" hides them.
- M1 checked that all 15 are inside retron-db's 112 flag, so **retron-db's primary
  population (1,814 proteins / 1,811 folds) excludes them.** They are present in:
  - V3's sequence sets (V3's "99.01% RT recovery" counts them as recovered);
  - V4's sequence sets and fold/TM matrices;
  - retron-db's secondary fold population (1,901);
  - retron-db's `reference_msa_v1.afa` (1,926);
  - V4's re-inference trees (§3.2).
- 9 terminal pairs share an identical sequence, so there are 1,917 distinct sequences among
  1,926 proteins.

### 3.2 V4's re-inference ("≤3 of 11") is reproducible but is not a Mestre reproduction

- The six trees survive: 1,843 tips each, IQ-TREE **3.1.3**, LG+F+R10 in five and
  LG+F+I+R10 in `linsi`, UFBoot and SH-aLRT on all nodes. On borg the input alignments are
  lost and no command line survives. **Corrected 2026-09-19: both survive on Ibex**
  (`rt0_rt7_domain_test_v4_and_tree/mestre/`, §9.2).
- The V4 sub-audit **rebuilt 4 of 6 inputs exactly**: `mafft --auto` gives FFT-NS-2; keeping
  columns ≥ 50 % occupied matches sites, patterns and all 20 amino-acid frequencies.
  `fftnsi` comes out 1 column off, and `linsi` was not attempted. SHA256 sums are in
  `subaudits/v4/reconstructed_alignments_SHA256SUMS`; the alignments themselves stay in scratch.
- "≤3 of 11" and "RF 0.143–0.232 vs 0.087–0.134 (1.70×)" **re-run exactly** from V4's own
  `s7i`/`s7h`. Neither script writes a table.
- Why these trees cannot be read as a reproduction of Mestre:
  - The trees contain **91 of the 112 substitutes, 3 of them RNA polymerase subunits** (M1
    check on `ours.treefile`).
  - They use 219–303 trimmed sites and 1,843 taxa, against Mestre's untrimmed RT0–7
    alignment of 1,928 taxa. Mestre used IQ-TREE 1.6.12 over 546 models; V4 tried a
    5-matrix model set.
  - "≤3/11" is a **support** result. On purity ≥ 0.9 alone the trees recover **4–6 of 11**.
  - V4 ran no positive control. The same rule applied to the published tree gives 10/11 by
    purity and 8–9/11 with support (`subaudits/v4/published_tree_positive_control.tsv`).
  - The clade test takes common ancestors on IQ-TREE's arbitrary root. G69's "clade 1's
    ancestor is the whole tree" is a rooting artefact.
  - The pre-registration was not followed: 10 clades plus an AU test, Q.pfam in the model
    set and L-INS-i were all declared; the runs scored 11 clades, ran no AU test, omitted
    Q.pfam, and used `--auto` for four of six trees.
  - The six trees are one taxon set in four frames plus two aligners, so they are **not six
    independent re-inferences**.

### 3.3 No attempt anywhere re-inferred Mestre's tree like-for-like or placed at scale

V2 planned placement and never ran it. V3's `epa_loo.sh` has no output anywhere. retron-db's
toolkit is a smoke test on 20 sequences. **Mestre's alignment is not published and is not on
disk.** Their Methods say MAFFT, RT0–7 domain, IQ-TREE 1.6.12, LG+F+R10 chosen by BIC over
546 models, UFBoot/SH-aLRT ×1000. Any alignment on disk belongs to a prior session.

### 3.4 retron-db bundle: defects the bundle does not declare

1. **Not rerunnable as sealed.** Root A (`/home/borg/RETRON_CLAUDE_PART1/supplementary_material`)
   is gone. 29 sealed inputs are missing and all 29 have byte-identical copies elsewhere
   (`subaudits/retron_db/retrondb_inputs_today.tsv`).
2. **`s00` passes vacuously on a missing root.** `ok_identity = len(differing) == 0` is true
   when zero files are shared. The clean run prints *"OK: both roots pinned; shared files
   byte-identical"* after comparing **0** root-A files. Only the seeded control notices, and
   only because it cannot find a file to corrupt (`rerun_asis.log`).
3. `env.lock` is an export of conda **base**. `run.sh` executes in `retron_tradicional`.
4. `PROVENANCE.md` is byte-identical to the discarded first assembly: it predates three seals
   and `s08`.
5. None of the nine claims was ever signed off. Every status is still "proposed".

### 3.5 The Ibex realpipe denominator is 1,920, not 537

`processed_genomes.txt` logs a genome only on a clean exit, and 1,383 of the 1,391
"failures" failed only at the final bpRNA step. The local `stock_verdicts.tsv` has
**1,925 rows**, of which **1,920** have integrated results. The earlier harness returned 0
CM hits **by construction**: `padlocdb.cm` has no GA lines, so `--cut_ga` finds nothing. R1
is correctly quarantined (string matches, wrapped rows). The Ibex copies themselves are
**unreachable from borg** (`/ibex` is not mounted), so the Ibex-vs-borg identity is still
never hash-compared.

### 3.6 Duplicate paths are one piece of evidence

| content | copies | distinct |
|---|---|---|
| published tree `Supplementary_mestre_Tree.nwk` | 7 paths, 5 roots | **1** |
| per-tip table: `T1_R1`, `…_paper.csv`, `Mestre_supplementary_material.csv` | 20 paths | **3 files, 1 body** (header-only differences) |
| paper text | 10 paths | **2 renderings** (layout text; PMC text) |
| Khan panel `support.csv` | 6 paths | **1** |
| PADLOC `padlocdb.cm`, two mirrors | 2 | bytes differ; the **21 models are identical, reordered** |

No agreement among copies inside one identity group may be cited as corroboration.

---

## 4 · Corrections to `RETRON_STAGES/05_mestre_replication.md`

| doc says | measured |
|---|---|
| Root A `/home/borg/RETRON_CLAUDE_PART1/supplementary_material/` | **gone**. Its 23 Mestre-relevant files are sha256-identical in v7 `MELISSA_DATA/supplementary_material/` |
| root B holds `support.csv`, `taxonomy_lookup.tsv` | true. The v7 copy **lacks** both |
| "missing `terminal_461`, `515`, `1774`" | protein gaps are **2** (461, 1774). 515 holds its published protein but has no genome |
| `realpipe/processed_genomes.txt` = 537 → "run incomplete" | 537 counts clean exits, not results. **1,920** integrated (§3.5) |
| `ids_69.txt` "named 69, holds 68" | **holds 69**. There is no trailing newline, so `wc -l` reports 68 |
| `m11_relaxed_cm_axis.sh` | the local file is `m11_strict_E1e-5_cm_axis.sh` |
| 1,919 folds on borg | ✅ 1,919 `.pdb`; 112 of them are substitutes |
| clade separation "silhouette 0.2565, z = 25.27" | superseded by retron-db: **0.156963, z = 2.75–2.81** against random monophyletic partitions (1,811 folds) |
| "≤3 of 11 by independent re-inference" | reproduces from V4 files, but it is a support count on a substitute-contaminated, trimmed, non-Mestre alignment (§3.2) |
| "Toro 2018 lab reported the same tree failure" (C4) | retron-db: **not found by 4 probes in 2 main-text renderings**. Scoped negative, not refuted |
| "60 % cutoff set after scoring" | retron-db found **no** supporting text. UNVERIFIED |
| `crosscheck/FROZEN_DENOMINATORS.tsv` has no Mestre row | ✅ confirmed: 80 lines, 0 Mestre rows |
| `padloc2` `padlocdb.cm` mirror "identity UNVERIFIED" | bytes differ; model content identical, reordered |

---

## 5 · Verification rerun of the retron-db bundle

| run | change | result |
|---|---|---|
| `rerun_asis` | none | **EXIT 1** at `s00 --seed-bad`, after a vacuous clean-mode "OK" (§3.4) |
| `rerun_remapA` | `SUPP_ROOT_A` → v7 `MELISSA_DATA/supplementary_material` (one line, `remap.diff`); 23/23 sealed Mestre-relevant files sha256-identical there | **EXIT 0**. All 8 seeded controls OK. **18/18 scientific tables, `BLIND_CONFIRMATION.tsv` and 3/3 PNGs byte-identical.** `inputs_pinned.tsv` differs only by 6 absent non-Mestre `stats/*.json` and 1 extra html; 3 SVGs differ by matplotlib ids and timestamps (`COMPARISON.tsv`) |

The retron-db stage-1 **measurements** are therefore reproducible today from graded inputs.
Their **inputs manifest** is not.

---

## 6 · Reuse grades (summary; per-asset detail in `ASSET_REGISTER.tsv`)

| grade | n | examples |
|---|---:|---|
| GREEN | 69 | published tree and table, paper text, retron-db stage-1 tables and scripts, detector models (flagged: Mestre-descended) |
| AMBER | 129 | benchmark proteins (exclude the 112), V4 trees (comparator only), `stock_verdicts` (1,920 denominator), folds, stage-3 toolkit |
| RED | 42 | every alignment or sequence set carrying the substitutes as a *reference*, foldseek shards with no command, R1 quarantined, the discarded assembly, `env.lock` |
| REFERENCE / CLAIM-ONLY | 37 / 43 | prior code (re-implement) / prose (re-derive before citing) |
| Ibex (audited 2026-09-19) | 6 register rows, graded AMBER; all 16 stage-05 Ibex rows resolved (`YES_IBEX`) except the doc-regex artefact `hmm/{df_tierA` | per-file identity in `ibex_audit/results/` (§9) |
| UNGRADED | 29 | non-Mestre neighbours (MyRT refpkg, metadata, report templates, figures): `DO-NOT-USE` for Mestre work |

---

## 7 · What M1 did not do

- Did not infer any tree, rebuild the L-INS-i alignment, or run placement.
- On 2026-09-18 Ibex was not reached, and its assets were recorded as `IBEX_UNINSPECTED`.
  **Superseded 2026-09-19:** audited over SSH with operator authorisation (§9).
- Did not re-query BV-BRC or NCBI. retron-db's 0/115 recovery stands as measured on 2026-09-12.
- Did not sign any historical claim. Claim status stays with the operator.

## 8 · Handoff to M2

⚠️ **Superseded by revision 2 (§13).** Revision 1 of the launcher would have placed
representatives of all 501,561 RTs and cut the region with the Stage-2 mapper. The operator
rejected both.

---

# Addendum 2026-09-18 — operator scope corrections

## 9 · The Ibex Mestre roots — AUDITED 2026-09-19

> **Update 2026-09-19.** `general/` is now initialised at the pinned `cff9831`, and the
> operator authorised SSH through a per-command sandbox bypass. The audit below **was run**
> and supersedes the "uninspected" state recorded on 2026-09-18. `specs_exist.sh` reports one
> pre-existing problem outside this work: `docs/BLOCKED.md` references the untracked
> `proposed/research_contract_C3_C9_amendment.md`.

### 9.1 What was run

The read-only inventory (`ibex_audit/ibex_mestre_inventory.sh`, sha256 `c361db52…b808`,
identical on both ends) ran as a SLURM job per root. Account `pi-hohndor`; outputs under
`/ibex/user/rioszemm/experiments/m1_ibex_mestre_audit/`; nothing was written under the audited
roots.

| root | job | wall | files hashed | outcome |
|---|---|---|---:|---|
| `…/RETRONS/Mestre_replication` (83 GB) | 52089161 | 8 min | **128,701 / 128,701** | COMPLETED |
| `…/RETRONS/rt0_rt7_domain_test_v4_and_tree` (11 GB) | 52089162 | 55 s | 12,605 / 12,605 | COMPLETED |
| `…/RETRONS/retron_phylo_REPLICATION` (9 MB) | 52089163 | 2 s | 21 / 21 | COMPLETED |

- The second and third roots were **not** in the brief. A bounded name search of
  `/ibex/project/c2366` and `/ibex/user/rioszemm` (`*occ50*`, `*mestre*`) found them, and
  both hold Mestre-related material.
- The first submission (52089097) failed in 1 s: exit 13, a SIGPIPE from
  `sha256sum --version | head -1` under `pipefail`. That line was fixed, and the failure is
  recorded in the script.
- Outputs were pulled back and every `SHA256SUMS` verified. `m05` compared each file with
  borg; the comparator was fixed before use so that zero-byte files count as `EMPTY_FILE`,
  not "copies".
- Landed: `ibex_audit/results/{mestre_replication,v4_and_tree,retron_phylo_REPLICATION}/`,
  containing the inventory, a per-file `IBEX_VS_BORG.tsv.gz`, env and dir tables, plus
  `IBEX_IDENTITY_SUMMARY.tsv`. The text bundles remain in scratch.

### 9.2 What Ibex holds that borg does not

**`Mestre_replication`: a detector-pipeline workspace, not a phylogenetic one.**
- **Byte-identical to V3 (no new evidence):**
  - the drivers `m8`, `m10`, `m12`, `m13`;
  - `stock_verdicts.tsv`, `ids_69.txt` and `char69.tsv` (= V3 `S3_char69_positional.tsv`);
  - all **1,926 `protein_aminoacid.fasta`**, the same benchmark proteins, substitutes included;
  - all 1,925 `genome.fasta.gz`.
- **Ibex-only, all derived from those same proteins and genomes:**
  - `m11_relaxed_cm_axis.sh`, the original of V3's relabelled `m11_strict_E1e-5_cm_axis.sh`
    (V3 renamed it and corrected the "relaxed" wording, since E ≤ 1e-5 is stricter than stock);
  - `processed_genomes.txt`;
  - 49,947 realpipe result files;
  - 1,924 decompressed genomes;
  - the DefenseFinder tier-A/B HMM databases;
  - the 40 harness logs;
  - 101 MyRT `.sto`/`.jplace` outputs. These are placements onto **MyRT's** reference, not
    Mestre's tree.
- **No alignment of Mestre RTs, no tree, and no RT0–RT7 extraction logic.** The 3,850 files
  flagged "extraction candidates" are pipeline logs matching the word "extract".

**`rt0_rt7_domain_test_v4_and_tree/mestre/`: the V4 re-inference workspace.**
- **The inputs M1 recorded as lost are here, and Ibex-only:**
  - 6 pre-trim alignments (1,309–2,765 columns);
  - 6 `_occ50` alignments (219–303 columns), all 1,843 taxa;
  - full IQ-TREE `.log`s with command lines;
  - `.model.gz`, `.ufboot`, `.contree`, `.splits.nex`, `.mldist` and `.ckp.gz`;
  - the drivers `mestre_frames.slurm` (ours / toro / wide / narrow; `mafft --auto`) and
    `mestre_align.slurm` (fftnsi: `--retree 2 --maxiterate 1000`; linsi:
    `--localpair --maxiterate 1000`, both on the `ours` window).
- The IQ-TREE command is identical for all six trees:
  `iqtree -m MFP -mset LG,WAG,JTT,VT,Dayhoff -B 1000 --bnni -alrt 1000` (v3.1.3), after an
  occupancy ≥ 0.5 column filter.
- The input FASTAs and the six `.treefile`/`.iqtree` files are byte-identical to V4 on borg.
- **The earlier sub-audit's four "exact" rebuilds are confirmed byte-identical** to the Ibex
  `ours`, `toro`, `wide` and `narrow` `_occ50` originals. Its `fftnsi` rebuild is not, as it
  reported.
- Side find, not Mestre: `struct/scripts/foldseek_ava.slurm` + `mk_matrix.py` produce
  `tm.npy` for the 5,256 span-sliced set, the producer the prior asset audit could not find.

**`retron_phylo_REPLICATION`: an earlier replication of the owner's phylogeny pipeline.**
It is a 500-sequence, 169-column probe of **project-corpus** RTs (16-hex IDs; no Mestre tips),
run under LG+C60+F+R6 and LG+F+G4 with 100 bootstraps. The trees, logs, sbatch files and
`probe500.afa` are byte-identical to V3 `retron_phylogenetic_tree_REPLICATION/`; only IQ-TREE
intermediates are Ibex-only. It is **not a Mestre reproduction.**

### 9.3 Answers to the operator's two questions

1. **Missing historical tree re-inference inputs: yes, found.** They are all V4's, and all
   are windowed alignments of the 1,843-protein set carrying 91 substitutes (3 of them
   RNA-polymerase subunits). They make V4's "≤3 of 11" **fully reproducible from its original
   inputs**, but they are **not** a Mestre reproduction (M1 §3.2 stands).
2. **RT0–RT7 extraction logic: no.** The V4 windows are fixed offsets around the first
   `[YFWH].DD` motif, cut on borg by `s7h_mestre_frames.py`; Ibex only aligned them. No Ibex
   file holds Mestre RT0–RT7 extracts, extraction coordinates or Mestre's alignment. MCC-v2
   (§11) is unaffected.

### 9.4 Pre-audit expectations (2026-09-18, kept for the record)

**What borg already implied Ibex held:**
- the realpipe outputs (partial local mirror: V4 `ncrna_extractor_detector_V3/cache/ibex_mestre`,
  1,925 metadata + 1,920 integrated JSONs, tool subfolders empty);
- the drivers `m8`/`m10`/`m11` (V3 holds `m8`, `m10`, `m12`, `m13` and
  `m11_strict_E1e-5_cm_axis.sh`, not the `m11_relaxed…` the stage doc names);
- the downloader/rescue code (not on borg; its logs say it ran on Ibex, reading
  `/ibex/project/c2350/…`);
- possibly the lost V4 `out/*_occ50.afa` inputs and pre-trim alignments.

Every one of these derives from the same substitute-contaminated protein set (M1 §3.1), so even
if found, none is Mestre's own RT0–RT7 material. Only a Mestre-lineage extract or coordinate
set would change the plan (launcher K0).

**Bounded audit, prepared and tested on borg:**

    # from borg (the operator's shell; this session has no route)
    scp analysis/mestre_audit/ibex_audit/ibex_mestre_inventory.sh rioszemm@ilogin.ibex.kaust.edu.sa:~/
    ssh rioszemm@ilogin.ibex.kaust.edu.sa 'sbatch ~/ibex_mestre_inventory.sh'
    # when DONE exists (≤ 2 h, 8 cores, read-only on ROOT):
    scp -r rioszemm@ilogin.ibex.kaust.edu.sa:~/m1_ibex_mestre_audit_<YYYYMMDD> ARIS_OUTPUT/mestre_audit/ibex/
    python3 analysis/mestre_audit/ibex_audit/m05_compare_ibex_inventory.py \
        ARIS_OUTPUT/mestre_audit/ibex/m1_ibex_mestre_audit_<YYYYMMDD> analysis/mestre_audit/ibex_audit/IBEX_VS_BORG.tsv

**What the inventory script collects:**
- a sha256 of every file ≤ 4 GiB; larger files are listed as `SKIPPED_SIZE`;
- per-directory counts;
- tool availability on the node;
- a copy of every text-like file (scripts, logs, alignments, trees, HMMs, tables; ≤ 50 MiB
  each, ≤ 2 GiB total), excluding `genomes/`;
- FASTA/alignment record and column counts, with a `|rescued` header flag;
- a method grep for mafft, iqtree, raxml, trimal, hmmalign, EPA-ng, RT0/RT7 and extract.

**What the comparator (`m05`) does:**
- classifies each Ibex file as `COPY_ON_BORG` (with its borg paths), `IBEX_ONLY` or
  `NOT_HASHED`;
- flags `TREE_REINFERENCE_INPUT_CANDIDATE`, `RT0_RT7_EXTRACTION_LOGIC_CANDIDATE` and
  `PLACEMENT_LOGIC_CANDIDATE`;
- treats `COPY_ON_BORG` files as adding no independent evidence.

**Self-test on borg:** the script ran on V3 `mestre_scope_audit`: 216 files hashed, text bundle
built, `DONE` written. `m05` then classified 216/216 as `COPY_ON_BORG` and flagged 7 extraction
candidates. This proves the mechanics only, because the test directory is itself on borg.
Known limit: Stockholm files report 0 records in `headers.tsv`, but they are still hashed and
bundled.

## 10 · RT0–RT7 material: what survives (`subaudits/rt07/`)

8,097 sequence and alignment files were scanned by content and header.

- **No asset preserves Mestre's RT0–RT7 extracts, extraction coordinates or alignment.**
  - Every local Mestre-bearing sequence file contains all 112 substitutes.
  - The owner's `phylo_v4.py` calls its alignment "RT0–7 scope", but it aligns **full-length**
    proteins (G-INS-i, then `hmmalign --trim`).
  - V4's `narrow`/`toro`/`ours`/`wide` sets are fixed windows around the first `[YFWH].DD`,
    for example −197..+57. They are not RT0–RT7 extracts.
- **Closest prior extraction logic:** V4 `s09`/`s14`, which projects the proteins into the
  Toro 2014 frame with `hmmalign --mapali`. It is reproduced byte-identically, but it uses a
  default-fragthresh profile: 465 states, of which states 1–67 and 305–465 are flank artefacts.
- **The Toro 2014 extraction frame itself:**
  - Ends are consistent: 598/742 sequences end at column 1305, the RT7 C-terminus.
  - Starts are consistent for group II, DGRs and CRISPR-RTs but **not for retrons**: retron
    start column median 85; RT0 blocks 1 and 2 are occupied at 0.47 / 0.00 among the 102 Toro
    retrons, against ≈ 0.9 for group II.
  - **So, in the Toro lab's own RT0–RT7 practice, retron extracts carry little aligned RT0.**
- **Mestre N-terminal reach (clean 1,814):** RT0 blocks 1 and 2 are occupied at 0.155 and
  0.200. The prior V4 conclusion was "non-alignable, not absent": 87 % carry more than 20
  residues upstream of block 1.

## 11 · A Mestre-comparable core (MCC) — feasibility on historical sequences

Scripts: `scripts/m06_mcc_feasibility.py` (v1) and `m07_mcc_v2_feasibility.py` (v2). Outputs:
`m2_design/mcc_v1/`, `m2_design/mcc_v2/`. Rules were written into each script before its first
run. Only clean historical proteins and the Toro frame were used; there were **no clade labels
and no modern sequences.**

| | MCC-v1 (anchors ≥ 50 % Toro-retron occupancy) | **MCC-v2 (≥ 95 %)** |
|---|---|---|
| required core | blocks 3→29 (200 states) | **blocks 4→28 (182 states)**; RT0 zone and RT7 tail optional |
| clean extractable | 1,162 / 1,814 (64.1 %) | **1,729 / 1,814 (95.3 %)** |
| failures | 554 C-truncated, 98 N-truncated | 54 C-truncated, 30 N-truncated, 1 non-standard |
| core start / end within 5 aa, two routes | 98.1 % / 97.6 % | **99.1 % / 99.5 %** |
| interior block starts within 2 aa | — | median 0.917 of blocks per sequence; 51.7 % of sequences ≥ 0.9 |
| 15 RNA-polymerase substitutes | 15 NO_HIT | **15 NO_HIT** |
| extract length (clean, extractable) | — | median 217 aa (IQR 206–225) |

**Why v1 failed.** Its C-anchor was the terminal 9-state RT7 block. 554 clean proteins were
marked C-truncated despite a core occupancy of 0.90. That is an alignment-edge artefact, not
truncation. v2 was **designed after seeing that failure**, is labelled as such in its
docstring, and is the only variant tried.

**A defect caught during the probe.** The first route-2 implementation counted residues in
`mafft --keeplength` output, which deletes insertions. It produced an implausible 0 % block
agreement. The fix reads `--mapout`, the MAFFT residue→column map. The fix came **after** the
first runs, touches only the concordance columns, and is recorded in both scripts. The pre-fix
outputs are kept, unlanded, in `ARIS_OUTPUT/mestre_audit/superseded_prefix_route2/`.

**What this establishes.** The MCC-v2 **bounds** reconstruct consistently across two
independent alignment routes for 95 % of clean historical proteins. **Interior column
assignment is only moderately stable**, which is exactly the alignment uncertainty M2a must
measure. This is feasibility, not the M2a gate.

## 12 · The modern retron query universe — census (`m2_design/M2B_QUERY_CENSUS.tsv`)

Script: `scripts/m04_query_population_census.py`, with rules declared in its docstring before
the first run. It reads frozen Stage-1 datasets only and makes no placement.

| stratum | exact RTs | RT-anchored records | g5a-eligible | < 250 aa |
|---|---:|---:|---:|---:|
| **A** (≥ 2 of DF / PAD / ncRNA on one record) | **33,670** | 483,848 | 31,952 | 1,488 |
| **B1** (exactly 1 system line) | **20,451** | 96,624 | 16,130 | 3,908 |
| **B0** (myRT Retron profile only) | **24,166** | 82,836 | 13,313 | 8,576 |
| M (MULTI / mixed family) | 7,593 | 9,012 | 2,824 | 3,391 |
| D (retron system call, non-Retron record) | 5 | 11 | 1 | 4 |
| X (no retron evidence; controls only) | 415,676 | 2,378,907 | 305,161 | 91,072 |

- **Primary query universe: A ∪ B1 ∪ B0 = 78,287 exact RTs** (663,308 records). A and B are
  never pooled.
- 23,556 tier-A RTs carry the ncRNA line inside an A record; this is the A-nc sensitivity set.
- System calls are essentially confined to Retron records: only 10 non-Retron, non-MULTI
  records carry one. Stratum D is their 5 exact RTs, 11 records in all.
- **All three system lines descend from Mestre/Toro models** (all 21 ncRNA CMs are
  Mestre-authored), so tier A is strong context, **not** Mestre-independent evidence.
- 1,603 of the 1,813 distinct clean Mestre sequences occur verbatim in the catalogue
  (1,289 in A, 227 in B1, 87 in B0).
- MCC-v2 extractability of the modern universe has **not** been computed. That is M2b's freeze
  measurement.

## 13 · Revised M2 (proposed, revision 2)

`proposed/LAUNCHER_M2_historical_classification_expansion.md` passes `check_launcher.py`.
The stages are:
- **g0**, Ibex reconciliation, with K0: stop if a Mestre-lineage extract exists;
- **M2a**, the MCC-v2 reference reconstruction, with K1–K3 and calibration/evaluation split
  replicates;
- **M2b**, the tiered query freeze with exclusion reasons;
- **M2c**, the stratified smoke test, then a **mandatory stop**;
- **M2d**, placement of the primary 85 % MCC representatives with 95/70 % sensitivity, and
  expansion/accumulation on the retron population only.

Budget: M2a–c ≤ 60 CPU-h; **M2d ≈ 40 CPU-h expected, 100 CPU-h budget, 0 GPU**, re-sized from
the M2c measurement. Nothing is activated.

---

# Addendum 2026-09-19 (b) — Toro 2014 source audit, before any MCC freeze

Scripts: `scripts/m08_toro_mestre_crosswalk.py` and `m09_toro_template_extraction.py`.
Outputs: `m2_design/toro_crosswalk/`. No Mestre clade label is used to build anything here;
clade appears only as an `…_EVALUATION_ONLY` column.

## 14 · What the historical sources are, and are not

| asset (sha256) | contents | what it is | what it is **not** |
|---|---|---|---|
| `toro_2014_Rt0-Rt7.FASTA` (`6e43c4cc…95b1`) | 742 gapped sequences × 1,466 columns (741 distinct extracts). Three header schemes: GenBank GI 137 + 1 by accession; PATRIC fid 465 (with a taxon-group prefix, `Afid`/`Gfid`/`cianobacteriafid`…); group-II-database name 139 | **Toro RT0–RT7 definition/reference.** Every sequence is an RT0–RT7 *extract*, already aligned | not the Mestre MSA; not a tree |
| `TableS1_Toro_2014.XLSX` (`385e8043…8505`) | 742 rows; 685 join to FASTA headers by key. By RT phylogeny: Group II 425, **Retrons 102**, DGRs 62, Abi 33 + Abi* 25, UG* 78, CRISPR-RT 14, UNC 9 | the class labels of the 742; Retrons = 102 | not all retrons: 640 are other RT classes |
| `Suppl_Toro_Tree.txt` (`ea0ee646…be31`) | 9,141 tips labelled `accession \| species` | Toro's later 9,141-representative RT tree, **the source population of Mestre 2020** | **not the Toro 2014 tree**: only 34/675 Toro 2014 accessions occur in it; no 2014 tree is on disk |
| `Supplementary_mestre_Tree.nwk` (`7a9a1129…34ce`) | 1,928 tips | Mestre 2020 tree: **1,912 Toro-tree tips + the 16 experimentally validated retrons** (all 16 absent from the Toro tree carry a `Retron_name`), which reproduces "1,912 + 16" by identifier; 11 clades + 1 Orphan in the per-tip table | — |

All copies of each asset across V4, the v7 references and v7 `MELISSA_DATA` are byte-identical.
Register: `m2_design/toro_crosswalk/TORO_MESTRE_SOURCE_ASSETS.tsv`.

**The crosswalk: Toro 2014 → Mestre 2020 by sequence** (`TORO2014_x_MESTRE2020_CROSSWALK.tsv`)
- Identifiers changed between 2014 and 2020 (old PATRIC fids and GIs versus `fig|genome.peg`
  and `WP_`), so the crosswalk is by sequence.
- **73 Toro 2014 extracts map to 76 clean Mestre proteins** (≥ 0.95 identity, ≥ 0.95 extract
  coverage). 58 are exact substrings, and **all 73 are Table S1 "Retrons"** — a clean
  class-level positive control.
- 29 of the 102 Toro retrons map to no clean Mestre protein (median best identity 0.55).
- Retron-Sen2 (St85, terminal 116), one of the 16 validated retrons, is an RNA-polymerase
  substitute in our download, so it is absent from the clean reference.

## 15 · The material finding: Toro states RT0–RT7 boundaries on 76 clean Mestre proteins

For those 76 proteins, the extract's position is a **source-stated** RT0–RT7 interval. Two
label-independent extractors were scored against it (`TTE_vs_MCC2_SUMMARY.tsv`).
**TTE** (*Toro-template extraction*) was declared in `m09` before it ran. Templates are the 102
Toro 2014 retron extracts; for each protein, the best template with < 0.90 identity is used
(near-self excluded) and must cover ≥ 0.80 of itself; its boundaries are transferred to the
protein.

| on the 76 source-stated proteins | **TTE** | MCC-v2 window | MCC-v2 required core |
|---|---|---|---|
| extracted | **76 / 76** | 71 / 76 | 71 / 76 |
| start within 5 aa / end within 5 aa | **0.658 / 0.816** | 0.225 / 0.718 | 0.000 / 0.127 |
| median absolute error, start / end | **0 / 0 aa** | 11 / 2 aa | 29 / 10 aa |

| all sets | TTE | MCC-v2 |
|---|---|---|
| clean historical proteins extracted | **1,814 / 1,814** | 1,729 / 1,814 |
| other substitutes | 78 / 97 | 78 / 97 |
| 15 RNA-polymerase substitutes (negative control) | **0 / 15** | 0 / 15 |
| median extract length (clean) | 231.5 aa (Toro retron extracts: 231) | 217 aa window |

- On the 1,729 clean proteins both extract, the TTE interval starts a median **26 aa before**
  the MCC-v2 required core and ends **10 aa after** it, and contains the required core in
  87.5 %.
- **The Toro-stated historical RT0–RT7 interval for retrons therefore includes about 36
  residues per protein that an MCC-v2 required-core-only primary would discard.**
- TTE recovers those edges stably on historical proteins: median error 0 aa.

**Why this is provenance-driven, not outcome-driven.** It was measured on source-stated
boundaries before any placement, tree or clade evaluation. No Mestre clade entered either
extractor. The comparison was run once, with rules declared in the script.

## 16 · The three objects, kept apart

| object | status |
|---|---|
| **Toro RT0–RT7 definition/reference** (2014 extracts) | on disk, hashed; source-stated boundaries on 76 clean Mestre proteins |
| **Mestre RT0–RT7 alignment** | **not recoverable**; exact reproduction is impossible |
| **Our operational reconstruction** (MCC-v2, or the proposed TTE-based contract) | a choice we make; never called "the Mestre alignment" |

## 17 · Revised extraction contract — PAUSED for the operator

The operator's rule applies: *"if this audit materially changes the historical-core
definition, pause before M2 execution and report the revised extraction contract."* It does,
so **M2a–c have not been activated and nothing is frozen.**

**Proposed `MCC-v3` (Toro-template contract):**
1. **Primary boundaries: TTE**, which transfers Toro 2014 retron-extract boundaries.
   - templates: the 102 Table S1 "Retrons" extracts;
   - template selection: best bitscore, template coverage ≥ 0.80;
   - leave-near-self-out (< 0.90 identity) **for historical validation only**. For modern
     queries every template is eligible, and the template identity is recorded.
2. **Core QC from the profile route.** The MCC-v2 hmmalign route must place ≥ 70 % of the
   required-core states (blocks 4–28) **inside** the TTE interval; failing that, the status
   is `UNABLE_TO_EXTRACT_MCC_RELIABLY`.
   - This keeps the profile route as an anti-truncation check, but it no longer sets the
     edges.
   - It is an extraction status, not evidence that a sequence is non-retron.
3. **Primary alignment input:** the full TTE interval, so the reference matches the
   source-stated RT0–RT7 extent. **Sensitivity:** the same alignment restricted to the
   MCC-v2 required-core columns, reported beside the primary for every validation number.
4. **Not used anywhere:** Stage-2 `CAT_STATE`, the 150 anchors, Stage-2 RT5, Stage-3
   structure, or Mestre clade labels.

**The alternative** is to keep the approved primary, MCC-v2 required core only, and report
TTE as a sensitivity analysis. Under that choice, 85 clean historical proteins fall out as
non-extractable, and the ~36 source-stated residues per protein stay out of the primary
alignment.

**Recommendation: MCC-v3**, because it reproduces the only source-stated boundary evidence
(median error 0 aa) and extracts every clean historical protein. Its known risk: for **modern**
sequences distant from every Toro retron, no template may reach 0.80 coverage. Those sequences
get `UNABLE_TO_EXTRACT_MCC_RELIABLY` (category 5); they are never forced.
