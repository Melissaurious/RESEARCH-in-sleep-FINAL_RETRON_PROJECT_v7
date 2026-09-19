# V2 / V3 / V5 Mestre-replication lineage — measured vs asserted

Audit agent v235, 2026-09-18. Read-only over every source tree. Hashes, sizes and counts are in
`v235_assets.tsv` (161 rows). Tags: **[M]** = I measured it on borg this session. **[A]** = asserted
by a source document and not checkable from borg. **[NA]** = Ibex path, `NOT_ACCESSIBLE_FROM_BORG`.

---

## 0. The benchmark every tree consumed

`/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences/`
(2.7 GB, all mtimes 2026-03-08)

| measure | value |
|---|---|
| `terminal_N` dirs | **1,928** [M] |
| with `genome.fasta.gz` | **1,925**. Missing: 461, 515, 1774 [M] |
| with `protein_aminoacid.fasta` | **1,926**. Missing: 461, 1774. One sequence per file [M] |
| with `protein_nucleotide.fasta` | **1,925**. Missing: 461, 515, 1774 [M] |
| distinct protein sequences | **1,917**. 9 pairs of terminals share an identical sequence (e.g. 1223/1349, 1626/1876, 135/136) [M] |
| header accession = Mestre `Accesion` for that `Node` | **1,814** [M] |
| `\|rescued` headers | **112**: 91 are the same taxid with a new genome version or peg; 20 are a different taxid; 1 is an EDM accession replaced by a fig accession [M] |
| protein manifest hash (sorted `terminal\tsha256`, 1,926 lines) | `6d0f122284a4a42c062d22e97075ce362af974db4b7b901dc07de496287b4d53` [M] |

**Downloader and rescue code:** I could not find it on borg. I searched every `*.py`, `*.sh` and
`*.ipynb` under `/home/borg` (depth 9, conda/.git pruned) for the logger names `retron_downloader`,
`retron_rescue` and `retron_fix_wp`. The logs show it ran on Ibex and read
`/ibex/project/c2350/PHYLOGENETIC_TREE/Supp_material_T1_R1_systematic_prediction.csv` [NA].

**Rescue logic, reconstructed from the three logs and CSVs [M]:**
1. The downloader loaded 1,929 rows (1,928 plus one all-empty trailing CSV row). It resolved `fig|`
   accessions through BV-BRC and `WP_` accessions through NCBI protein. It marked 1,744 terminals
   `ok` and 184 `partial`.
2. `retron_rescue` ran on all 184 partial terminals. Its log shows it ran three times. Its method:
   - Query BV-BRC for genomes of the **same species name**. If that fails, fall back to the
     **genus**. If BV-BRC fails, try NCBI.
   - Take a protein whose **product annotation** matches as the "replacement".
   - Write the replacement's AA, NT and genome, with the header tagged `|rescued`.
   - Terminals with no species name are skipped (`no_species_name`; 54 warnings).
3. `retron_fix_wp` resolved 28 `WP_` accessions plus 2 dead `fig|` accessions through NCBI IPG to
   nuccore coordinates and a GCA assembly. Outcomes: 24 `already_complete`, 3 `ipg`, 2 `not_found`,
   1 `ipg_failed`.
4. **Defect: the product match was not RT-specific.** The log records 33 "replacements" annotated
   *DNA-directed RNA polymerase* (EC 2.7.7.6: beta, beta′, alpha, omega and sigma subunits). The
   intended product was *RNA-directed DNA polymerase*. **15 terminals ended with an RNAP subunit as
   their "Mestre RT"**: 116, 295, 565, 731, 1086, 1186, 1282, 1327, 1343, 1350, 1367, 1387, 1560,
   1804 and 1915. Full list: `v235_rnap_substitutes.tsv`. I infer, without seeing the code, that
   the query used a tokenised keyword match. Seven of the 15 are "same taxid" rescues, so the
   classification "91 = version drift, nothing to fetch" hides substitutions that are wrong in
   substance. Substitutes chosen at genus level also produce the duplicate sequences listed above.

Every downstream Mestre sequence set is **sequence-identical to this benchmark**, so every one
carries the 15 RNAP proteins. That includes V3 `mestre_1928_proteins.faa`, V3 `_archive`
`mestre_reference_RTs.faa`, V3 `pilot/terminal_1` and V3 `realpipe_timing` input [M].

---

## 1. V3 `ARIS_OUTPUT/mestre_scope_audit/`

### 1.1 What each Ibex job ran

The scripts are on borg. All outputs are Ibex paths under `/ibex/project/c2366/RETRONS/Mestre_replication/` [NA].

| job | driver | what it ran | status |
|---|---|---|---|
| 50025828 | `m8_mestre_validation_ibex.sh` (array 0-19) | A bespoke harness, **not** the pipeline: `prodigal -p meta`; `blastp` Mestre protein vs called CDS (`-evalue 1e-5 -max_target_seqs 5`, full-length = ≥90% qcov and ≥90% pident); `hmmsearch` DF non-Retron (1,139) and DF Retron_* (39) `--cut_ga`, myRT `cat Models/HMM/*.hmm` `-E 1e-5`, `padlocdb.hmm --cut_ga`; `cmsearch --cut_ga padlocdb.cm` genome-wide | RT-recovery axis kept. The CM axis is VOID: padlocdb.cm has **0 GA/TC/NC lines** [M], so `--cut_ga` returns nothing by construction |
| 50027177 | first m10 attempt | ran under `/usr/bin/python` without biopython | VOID [A] |
| 50060998 | `m10_mestre_realpipe_ibex.sh` (array 0-9 × 16 parallel) | stock `python run_pipeline.py -i <terminal dir> -o <results> --run-infernal` with the Ibex `retron_tradicional` env on PATH. `--cleanup` and `rm -rf` removed. Inner tools: prodigal `-p meta`, myRT, PADLOC v2.0.0 (`conda run -n padloc2 … --fix-prodigal`), DefenseFinder, `rt_integration_corrected.py`, and Infernal `cmsearch --FZ 500 --acc --noali` whole genome (TEST_SCRIPT_31_nov_v5.py:297-306) | the corpus-comparable axis |
| 50071034 | `m11_strict_E1e-5_cm_axis.sh` | `cmsearch -E 1e-5 --acc --noali` genome-wide with the Ibex `src/padloc/data/cm/padlocdb.cm` | output directory has the legacy name `relaxed_cm/` |

Versions: the Ibex tool versions cannot be checked from borg [NA]. On borg the same envs report:
Infernal 1.1.5, HMMER 3.4, Prodigal 2.6.3, BLAST 2.17.0+, DefenseFinder 2.0.1 (models 2.0.2) and
padloc v2.0.0 (DB v2.0.0) [M]. The production code at TEST_SCRIPT:249/1016 reads the CM from the
**padloc2 env copy**, while the argparse default points at the `src/` copy (l.1467).

### 1.2 Terminal count and denominator

- **The "537 processed of 1,928" in RETRON_STAGES/05 is not a denominator.** `m10` appends to
  `processed_genomes.txt` only when `run_pipeline.py` exits 0. SESSION_STATE §0a asserts
  `failed_genomes.txt` has 1,391 entries, of which 1,383 still have `tool_integrated_results.json`
  (they failed only at step4 bpRNA). 1,928 − 1,391 = **537**, so the two figures reconcile exactly.
  The 537 is an artefact of the pipeline's exit code [A for 537 and 1,391; the arithmetic is M].
- **Local evidence** is `cache/stock_verdicts.tsv`, a borg copy of the Ibex `realpipe/stock_verdicts.tsv`
  [the Ibex original is NA]:
  - **1,925 data rows**, 13 columns: `terminal integrated n_systems n_retron_systems system_types
    n_ncrnas_total ncrna_models ncrna_best_evalue ncrna_best_score any_ncrna rt_gene_ids
    n_high_conf ncrna_types`.
  - **terminals 461, 515 and 1774 are absent.** They have no genome, and m12 lists only result
    directories.
  - `integrated=True` on **1,920**. False on 313, 320, 324, 928 and 999.
  - ≥1 retron system: **1,874/1,920**. `any_ncrna`: **1,301/1,920** (67.76%). 619 have no ncRNA [M].
  - The correct denominator is **1,920 integrated / 1,925 genomes / 1,928 members**.
- **The RT-recovery "99.01%" (1,906/1,925) is inflated.** `REPAIRED_summary.tsv` [M] marks all 15
  RNAP-substituted terminals `rt_recovered=yes`: blastp finds the RNAP in the substitute genome.
  None of them has a myRT or DF-Retron HMM hit on its target, and all 15 have `n_retron_systems=0`
  in stock. The same no-HMM-hit profile covers 20 terminals in total (the 15 plus 929, 356, 629,
  1196 and 1166). A corrected figure needs the substitutes treated as a named stratum.

### 1.3 `ids_69.txt`: resolved

It holds **69 IDs**. `wc -l` reports 68 because the file has no trailing newline. It has no header
and no duplicates. Its set equals the terminals in S2 (69 rows) and the unique terminals in S3 (69)
[M]. The RETRON_STAGES/05 warning "named 69, holds 68" is a newline-counting artefact.

### 1.4 R1 vs R2 and why R1 was quarantined

`m9` renamed six columns of R1 with a `QUARANTINED__` prefix: `ORTH_myrt_hit/bits`,
`REF_padloc_hmm_hit`, `ORTH_df_nonretron_hits` and `REF_df_retron_hit/bits_QC`. They were produced by
shell `awk` string-matching of hmmsearch bit scores on the blastp target. They are domain-hit flags,
not tool or integration calls (no synteny, completeness or reconciliation). R2 keeps the 15 "valid"
columns.

**Both tables are also structurally broken [M].** They were built from the raw, line-wrapped
`summary_task*.tsv` files (trap F1: `grep -c || echo 0` emitted two zeros), so each has **3,856
rows for 1,928 terminals**. Only the 3 NO_GENOME rows carry a status. R2's `ncrna_cm_hit` and
`null_class` are VOID (A1-A3). The usable table is `cache/run50025828/REPAIRED_summary.tsv`:
1,928 rows, 1,925 OK and 3 NO_GENOME.

### 1.5 Other caches

- `mestre_1928_proteins.faa` holds **1,926** sequences, despite its name.
- `mestre_1926_vs_RT17CORE.sto` holds 1,926 hmmalign rows against RT17_CORE; x1-x5 are derived from it.
  This is not a tree alignment.
- `pilot/terminal_1/cm_hits.tbl` is 0 bytes because of the `--cut_ga` artefact.
- `realpipe_timing/`: the borg `run_pipeline.py` run **omitted `--run-infernal`**, so its `ncrnas: []`
  was never a CM null. `realpipe_cost.md` §2 nevertheless reads it as cross-validating the null.
  The stock Ibex run found TypeIA_IIAI at 142.7 bits, E 1.1e-30 (VOID A6).
- `cache/hmm/tierB.hmm` is byte-identical to stage3 `tierB_retron_mestre.hmm`. Both are the 39
  DefenseFinder `Retron_*` profiles (block-identical to the current `~/.macsyfinder` set). "mestre"
  in the name refers to lineage, not authorship. `tierA.hmm` is the 1,139 DF non-Retron profiles,
  also block-identical.

---

## 2. V3 phylogeny: did V3 infer a Mestre tree? **No.**

- `_archive/stage3_phylogenetic_paper/scripts/recover_mestre_reference.py` (2026-07-22) joins the
  1,928 published tips to the benchmark through `Accesion`, falling back to a paren short-code.
  Result: 1,926 resolved, 2 unresolved (nodes 461 and 1774). It writes `mestre_reference_RTs.faa`
  (1,926 sequences, the same multiset as the benchmark, **RNAP substitutes included**) plus a map
  and PROVENANCE.json.
- `_archive/.../epa_loo.sh`: `mafft --auto` on those 1,926 → hmmalign → `raxml-ng --evaluate` on
  the **pruned published topology** → epa-ng leave-one-out. **No `epa_loo/` output exists anywhere**,
  so there is no evidence it ran. It would not have been a de-novo inference in any case.
- `ARIS_OUTPUT/retron_phylogenetic_tree/` built trees with IQ-TREE (A2/B2 `LG+F+R10`), RAxML-NG (A3)
  and FastME/BIONJ (A4/B4). Those trees are on **our corpus's c60 representatives (5,966 tips)**,
  not on Mestre's sequences. Mestre clades were only projected from 103 "gold" retrons (p5c/p5d).
  STATUS reports clade recovery at best F1 0.13-0.50, "clades NOT recovered".
- `limitations_stage/a1_count_clades.py` counts clades on the **published** newick: 3-7 clades at
  support >85/90/95 [M, table]. This is not an inference.
- `METHOD_AUDIT_VS_MESTRE.md`, `origin_retron_data/notes/04_…md` and `cache/p4_…txt` are documents
  only. The p4 text cache is sha-identical to the V5 `49dcf404b055b066.txt`.
- A grep of V3 for `iqtree|fasttree|mafft` together with `mestre` found only documents, plans, the
  scripts above, and the owner's `MELISSA_SCRIPTS/phylogenetic_tree/phylo_v4.py`. That script is a
  reference-tree pipeline pointing at the benchmark; there is no V3 run evidence for it.

---

## 3. Supplements: "Root B" vs the current copy

| file | V3 (Root B) | V7 current | V4 | V2 |
|---|---|---|---|---|
| Supplementary_mestre_Tree.nwk | `7a9a1129…` | same | same | – |
| Supp_material_T1_R1_systematic_prediction.csv | `42f05d16…` | same | same | same |
| supp_material_systematic_prediction_paper.csv | `6a904dc2…` | same | same | – |
| Suppl_Toro_Tree.txt | `ea0ee646…` | same | same | – |
| myRT-FastTree2.refpkg (7 files) | all identical | same | same | – |
| report_ncbi_bacteria_Bacteria.html | `019c5c1c…` | same | same | same |
| gem_metadata.tsv | `fd0ad382…` | same (under `databases_metadata_files/metadata_files/`) | same | same |
| support.csv | `80b2f565…` | **absent** | same | same |
| report_template.html_8.j2 | `0ace8b31…` | **absent** | same | same |
| taxonomy_lookup.tsv (624,764,403 B) | `2abfe69e…` | **absent** | same | same |
| Mestre_supplementary_material.csv | – | **V7 only** `536c5d0c…` | – | – |
| toro_2014_Rt0-Rt7.FASTA | – | `6e43c4cc…` | same | – |

- **Every file shared between Root B and the current copy is byte-identical.**
- The three Mestre CSV variants have **identical bodies** after the header line (sha256
  `8f12377f35ef6a96…`). They differ only in their header labels, and all three have 1,928 data
  rows plus one all-empty trailing row [M].
- Clade distribution from the CSV: 8:427, 1:362, 9:324, 3:296, 10:198, 2:123, 11:123, 7:38, 4:25,
  6:6, 5:5, **Orphan:1** [M].
- The tree md5 is `73333b3d…`, matching V2/V3's recorded value. The RETRONS_january_2026 "foreign
  copy" `Supplementary FiLE S1_RT_Tree.newick.nwk` is sha-identical.
- **Root A (`/home/borg/RETRON_CLAUDE_PART1/supplementary_material/`) does not exist.** The
  directory holds only `claude_specs/` [M].

---

## 4. V2: not empty of Mestre work, but no Mestre tree

V2 has no commits (`master` has no commits yet) and is 142 GB. Mestre-related content:
- `MELISSA_DATA/supporting_material/`: 6 files, all byte-identical to V3.
- `ARIS_OUTPUT/phylogeny_paper_plan/` (2026-07-24) plans *placement onto* the Mestre and myRT
  reference. STATUS: "clean placement READY — not yet run". The earlier April-scaffold placement
  (56.48%) is marked VOID/foreign. The only related cache content is `job2/` (cluster reps
  alignment and hmmalign), which is not a Mestre tree.
- `ARIS_OUTPUT/stage3_ncrna/` measures 21-CM recall on 175 Mestre positives from `support.csv`.
  96 are assessable.
- There is no iqtree, fasttree or MAFFT run on Mestre sequences.

---

## 5. V5 research-wiki claims

`git log`: `fd46b8c` init (2026-08-31 19:14), `a3b2891` templates (20:08), `c07edc4` "stages 0a-0g"
(21:34), all by Melissa Rios. **`ARIS_OUTPUT/` is gitignored**, so none of the evidence paths
below are under version control. The working tree has uncommitted modifications, including the
mestre2020 paper page, and the untracked `padloc-retron-ncrna-cms-authored-by-mestre.md`.

| claim (all `status: unproven`) | evidence it cites | exists? | re-checked |
|---|---|---|---|
| mestre2020-60pct-cutoff-set-after-scoring | stage0c `cache/text/49dcf404b055b066.txt` | yes (gitignored) | anchor at l.141 [M]. The "set after inspecting outcome" framing is interpretation |
| mestre-reference-count-four-values | same text; Toro script; V4 line refs | text and Toro script yes; V4 lines not opened (out of scope) | 1,928 [M]; **1,927 = NSEQ sum of 29 Toro HMMs [M]**; 1,926 matches the benchmark protein count [M]; V4 1,926/1,843 citations not verified |
| mestre2020-retron-reference-set-1928 | same text | yes | anchor l.88/230 [M]; the CSV has 1,928 rows [M] |
| padloc-retron-ncrna-cms-authored-by-mestre (untracked, 2026-09-01) | stage1 `AXIS_LINEAGE_GRADING.md`; padloc2 `cm_meta.txt`, `padlocdb.cm` | yes | **21/21 `Mestre MR` / `10/fzk3` [M]; 21 INFERNAL + 21 HMMER3 blocks [M]**. The page cites `tables/s03_premise_grades.tsv`, which exists only under `stage2_ncrna_position/` (path ambiguity) |
| toro2026-hmms-seeded-from-mestre | `Toro_2026/spire_pipeline_scripts/02_hmm_calibrate_and_classify.py` | yes (identical copy in stage0c cache) | l.16 and l.33 anchors [M]; NSEQ sum 1,927 [M]. "Seeded" goes beyond "calibrated against"; the seed alignments are not on disk |

Checks on `stage0g_synthesis/VERIFICATION_mestre_residues.md` (gitignored):
- **Reproduced [M]:** 1,926 residues via the Node join; 1,814 exact accessions; 112 `|rescued`
  (91 same stem, 21 other genome, counting the EDM→fig case).
- **Mis-stated:** "1,930 lines" — the file has 1,929 newline-terminated lines. That is 1,930 CSV
  records only if the empty trailing row is counted.
- **Not reproduced by my method:** body sha `ec0a42e0…`. The byte-identity of the bodies is reproduced.
- **Missed:** its "version drift, nothing needs fetching" framing does not catch the **15 RNAP
  substitutes (7 of them same-taxid)**.

---

## 6. Model files (§7 of the brief)

- **padlocdb.cm, src vs padloc2 env:** the files are **byte-different** (`09449bdf…` vs `12dbc1bb…`,
  both 2,399,817 B). The **21 CM blocks are identical as a multiset**, and only their order
  differs. The `.i1*` press files differ accordingly. The mirror is therefore content-identical,
  not byte-identical.
- **padlocdb.hmm:** the same pattern. Byte-different, but the 5,027 profiles are block-identical.
- `cm_meta.txt`: byte-identical in both copies (`193b290c…`).
- `sys/retron_*.yaml`: 18 files, set-identical in both copies.
- DefenseFinder models 2.0.2 (DefenseFinder 2.0.1):
  - **39** `Retron_*` profiles (HMMER3/f 3.3 ×34, 3.1b2 ×4, 3.3.2 ×1), all with GA lines;
  - 1,178 profiles in total.
- myRT:
  - `RVT-All.hmm` sha `74556bd2…`: **45** profiles, HMMER 3.1b1, NSEQ sum 1,988;
  - `Models/HMM/` holds 46 per-family `.hmm` plus RVT-All;
  - `RVT-Retrons.hmm` NSEQ 91;
  - `m8`'s `cat *.hmm` would therefore give 91 profiles with duplicates, not the "65" its header states;
  - the stage-doc figure "~2,051 seeds / 47 families" was not reproduced.

---

## 7. Measured vs asserted: summary

| statement | status |
|---|---|
| 1,920/1,925 integrated; 1,874 retron; 1,301 ncRNA | **M** (from the local stock_verdicts copy; the Ibex original is NA) |
| 537 processed = incomplete run | **refuted as a denominator**: it is the exit-0 subset (arithmetic M, inputs A) |
| ids_69 holds 68 | **refuted**: 69 IDs, no trailing newline (M) |
| RT recovery 99.01% | **M, but inflated** by 15 RNAP substitutes counted as recovered |
| padloc mirror "identity UNVERIFIED" | **resolved**: content-identical, byte-different (M) |
| V3 inferred a Mestre tree | **no** (M: only published-tree counting and an unexecuted EPA-LOO plan) |
| Root B = current copy | **yes** for all shared files (M). Root A is gone |
