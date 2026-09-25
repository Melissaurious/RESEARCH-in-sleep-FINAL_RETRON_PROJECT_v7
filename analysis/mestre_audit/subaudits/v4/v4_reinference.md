# V4 Mestre re-inference arm: forensic reconstruction (agent_v4, 2026-09-18)

Scope: `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4` (not a git repo, so dates are file mtimes, local +0300).
Read-only on V4. Everything I wrote is under `ARIS_OUTPUT/mestre_audit/agent_v4/`.
Tags: **[MEASURED]** means I computed it from files in this session. **[ASSERTED]** means it
appears only in V4 prose. **[INFERRED]** means it is my reasoning from indirect evidence.

## 0. Bottom line

1. **Six trees survive; none of their original input alignments do.** Every `.iqtree` names
   `out/<tag>_occ50.afa`, a relative path. No file with that name exists anywhere under
   `/home/borg` [MEASURED, `find`]. No IQ-TREE `.log` survives, so no `Command:` line exists either.
   `s3_object/tables/t7_iqtree_commands.tsv` has an empty command column for all six. `s6_trees`
   FINDINGS and `s8_tree_declared` resp. 06 both say the alignments "were not kept" / "are gone".
2. **I rebuilt four of the six alignments exactly** [MEASURED]. I ran `mafft --auto` (v7.525,
   `retron_tradicional`) on `cache/mestre_{ours,toro,wide,narrow}.faa` and kept columns with
   ≥50% occupancy. Each result matches its V4 `.iqtree` on five checks: site count, constant
   sites, parsimony-informative sites, distinct patterns, and all 20 empirical amino-acid
   frequencies at 4 decimal places. MAFFT reports "FFT-NS-2 (Fast but rough)" for all four,
   which confirms the prose claim. The FFT-NS-i rebuild (`--retree 2 --maxiterate 1000`) comes
   out 1 column off (291 vs 290) and matches only 6 of 20 frequencies, so it is not the original.
   I did not attempt L-INS-i (it takes hours). The files are in `reconstructed_alignments/`, with
   the commands in its README.
3. **The "≤3 of 11" and "RF 0.143–0.232 vs 0.087–0.134" numbers reproduce exactly** when I re-run
   V4's own scripts on the surviving trees (`rerun/s7i_stdout.txt`, `rerun/s7h_stdout.txt`).
   However, both scripts only print to stdout and write no table. The numbers were later written
   to tables by other stages: `s6_trees/tables/v3_*`, `s3_object/tables/t4_rf_matrix.tsv` and
   `s4_motifs/tables/rv1b_g74_ratio.tsv`.
4. **This is not a like-for-like reproduction of Mestre**, and the clade test has a
   rooting defect (see §5).

## 1. Inputs to the arm

| input | path | n | note |
|---|---|---|---|
| Mestre proteins | `ARIS_OUTPUT/rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_proteins.faa` | 1,926 | copy of V3 `mestre_1928_proteins.faa`, renamed to its true count. Headers are `terminal_N\|terminal_N\|<accession-with-pipes>` |
| clade labels | `ARIS_OUTPUT/rt0_rt7_domain_test/cache/mestre_usable_index.tsv` (from `s06_mestre_unit_reconciliation.py`) | 1,814 | joined via accession = `"\|".join(parts[2:])` |
| frame FASTAs | `…_v4_and_tree/cache/mestre_{ours,toro,wide,narrow}.faa` | 1,843 each | unaligned anchor-relative spans ([YFWH].DD carriers). Windows: ours −220…+120 (max 341 aa), toro −197…+57 (255), wide −260…+160 (421), narrow −150…+80 (231) [MEASURED lengths]. All four share an mtime of 2026-08-21 15:33:09 to within milliseconds. **No script on disk writes them** (producer UNKNOWN, probably an inline one-off) |
| published tree | `MELISSA_DATA/supporting_material/Supplementary_mestre_Tree.nwk` (sha256 7a9a1129…) | 1,928 tips | only one support value per node |

1,926 − 1,843 = 83 proteins were dropped because they lack a `[YFWH].DD` anchor [ASSERTED in the
s7h docstring; the count is consistent with the files].

## 2. The six trees [all MEASURED from `.iqtree`/`.treefile`]

| tag | finished (mtime) | input named in .iqtree | alignment method | sites (PI) | best model (BIC) | tips | supports | wall / CPU |
|---|---|---|---|---:|---|---:|---|---|
| toro | 08-21 21:02 | `out/toro_occ50.afa` | `mafft --auto` → FFT-NS-2 (**rebuilt exactly**) | 231 (230) | LG+F+R10 | 1843 | SH-aLRT/UFBoot on 1840 nodes | 5.1 h / 78 h |
| ours | 08-22 01:57 | `out/ours_occ50.afa` | `--auto` → FFT-NS-2 (**rebuilt exactly**) | 297 (295) | LG+F+R10 | 1843 | same | 10.0 h / 132 h |
| narrow | 08-22 18:48 | `out/narrow_occ50.afa` | `--auto` → FFT-NS-2 (**rebuilt exactly**) | 219 (218) | LG+F+R10 | 1843 | same | 4.5 h / 68 h |
| wide | 08-22 20:15 | `out/wide_occ50.afa` | `--auto` → FFT-NS-2 (**rebuilt exactly**) | 295 (293) | LG+F+R10 | 1843 | same | 5.9 h / 91 h |
| fftnsi | 08-22 22:30 | `out/fftnsi_occ50.afa` | FFT-NS-i on ours frame [ASSERTED]; my rebuild is 1 column off | 290 (288) | LG+F+R10 | 1843 | same | 6.5 h / 179 h |
| linsi | 08-22 22:58 | `out/linsi_occ50.afa` | L-INS-i on ours frame [ASSERTED; not rebuilt] | 303 (300) | **LG+F+I+R10** | 1843 | same | 6.4 h / 178 h |

- **IQ-TREE version:** "IQ-TREE 3.1.3 built Jul 26 2026" in all six. The host is not recorded.
  The same build string appears in the borg-hosted `stage0_positioning/cache/refbuild/s200*.log`
  ("Host: borg-AS-5014A-TT") [INFERRED: probably run on borg, not proven].
- **Analysis:** "ModelFinder + tree reconstruction + ultrafast bootstrap (1000 replicates)". Node
  labels are "SH-aLRT support (%) / ultrafast bootstrap support (%)". The ModelFinder candidate
  set contains only LG, WAG, JTT, VT and Dayhoff (20 or 31 models listed).
  [INFERRED] That fits `-m MFP -mset LG,WAG,JTT,VT,Dayhoff -B 1000 --bnni -alrt 1000`, which is
  verbatim in `scripts/s6e_tcore_draws.sh` for the T-core trees. The actual Mestre command
  line is lost.
- The seeds are recorded in the `.iqtree` files (557897, 749198, 774490, 47634, 440060, 395906).
  The alignments were not recorded until now.
- **The trees are unrooted.** Tips are named `terminal_N`, and the root is IQ-TREE's arbitrary one.

## 3. Other Mestre alignments on disk (answering "does any usable alignment survive?")

| file | rows × cols | what it is | usable for ML re-inference? |
|---|---|---|---|
| `stage0_positioning/cache/refbuild/mestre_ref.aln` | 1926 × 6202 | MAFFT `--auto`, full-length, untrimmed (MEASUREMENTS.txt). The ungapped sequences equal the 1,926 FASTA [MEASURED] | yes, but it is full-length rather than the RT0–7 domain |
| `…/refbuild/ref_gappyout.aln` / `ref_automated1.aln` | 1925 × 262 / 1925 × 63 | trimAl on the above (1 sequence dropped) | 262-column version yes |
| `s5_admission/cache/mestre_ref.mafft.faa` / `.trim50.faa` | 1926 × 6056 / 1926 × 310 | `p5_build_toro_profile.py`: `mafft --auto --anysymbol`, then columns with ≤50% gaps. **Reproducible from a surviving script** | yes (full 1,926) |
| `rt0_rt7_domain_test/cache/frame/mestre1926_in_toro_frame.sto` | 2668 rows (742 Toro + 1926), 4203 cols | hmmalign `--mapali` onto the Toro-742 HMM | profile projection, not a free MSA |
| `…/mestre_from_V3/mestre_1926_vs_RT17CORE.sto` | 1926, 2877 RF cols | hmmalign to V3 RT17_CORE (no RT0) | profile projection |
| `/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/reference_RTs_aligned.fasta` | 1926 × 6037 | in-house, March 2026, producer unknown | full-length |
| `agent_v4/reconstructed_alignments/{ours,toro,wide,narrow}_occ50.RECON.afa` | 1843 × 297/231/295/219 | **my exact rebuild of the V4 inputs** | yes: these are the four V4 tree inputs |

**Mestre's own published MSA is not on disk.** No file anywhere has Mestre's tip names (their
accessions) in an aligned form. The only Mestre phylogenetic artefact on disk is the newick
(Supp. File S1). It is md5-identical to the copy under `RETRONS_january_2026/.../PHYLOGENETIC_TREE/`
(per MESTRE_ASSESSMENT). `stage0_positioning/tables/mestre_methods_parameters.tsv` records that
the paper gives no MAFFT parameters and no trimming.

## 4. The claims and the files that produce them

### "≤3 of 11" (G69 → G74)
- Producer: `scripts/s7i_clade_support.py` (mtime 08-23 10:18, which is after all six trees). It
  prints only. Independent re-implementation: `s6_trees/scripts/v3_frame_aligner_rf_and_clades.py`
  → `s6_trees/tables/v3_clade_recovery.tsv`.
- Re-run [MEASURED]: ours **3/11** (clades 2, 4, 5), toro 1/11 (5), wide 1/11 (4), narrow 1/11 (4),
  fftnsi 1/11 (2), linsi **2/11** (2, 4). Join: 1,926 terminals, 1,814 labelled. This matches the
  G74 table and s6_trees V7.
- Criterion: the ete3 `get_common_ancestor` of the clade's members on the as-written (arbitrarily
  rooted) tree must have purity ≥0.90, UFBoot ≥95 and SH-aLRT ≥80, with n ≥4. The "Orphan" label
  is skipped as too small.

### "RF 0.143–0.232 (frame) vs 0.087–0.134 (aligner)", ratio 1.70×
- Producer: `scripts/s7h_mestre_frames.py` (prints only; mtime 08-22 14:41, which is **before**
  narrow, wide, fftnsi and linsi finished, so it was re-run afterwards without a saved output).
  Tabulated by `s3_object/scripts/v4_rf_frame_vs_aligner.py` → `t4_rf_matrix.tsv`, then
  `s4_motifs/scripts/rv1b_g74_ratio.py` → `rv1b_g74_ratio.tsv` (1.702 / 1.473 / 1.392).
- Re-run [MEASURED], RF after collapsing nodes with UFBoot <95, on 1,843 identical tips:
  - Aligner pairs: ours–fftnsi 0.087, fftnsi–linsi 0.131, ours–linsi 0.134. Mean 0.117.
  - Frame pairs: ours–wide 0.143, narrow–toro 0.190, ours–toro 0.204, toro–wide 0.213,
    narrow–ours 0.218, narrow–wide 0.232. Mean 0.200.
  - Resolution (UFB≥95 ∧ aLRT≥80): ours 36.4, linsi 36.4, wide 36.3, fftnsi 35.0, toro 32.4, narrow 30.0 %.
- **The collapse rule is UFBoot only**, while resolution is computed on UFBoot ∧ SH-aLRT. s6_trees
  flagged this asymmetry and did not repair it.

### Are they reproducible from surviving files?
- **From the trees: yes, exactly** (both scripts re-run cleanly in `retron_tradicional`).
- **From sequences: 4 of 6 trees can now be rebuilt.** Their exact inputs are in
  `reconstructed_alignments/`. The IQ-TREE command is inferred, but the seeds are recorded.
  fftnsi cannot be rebuilt exactly. linsi was not attempted. Re-running IQ-TREE would take
  4–10 h wall each at the original thread counts, and ML searches are thread-sensitive, so
  bit-identical trees are not guaranteed even from the same alignment and seed.

## 5. Defects and contradictions (prose vs files)

1. **The clade test depends on the root.** s7i takes MRCAs on IQ-TREE's arbitrary root, yet
   `stage0_positioning/tables/mestre_rooting_sensitivity.tsv` (T1.1) had already ruled that
   MRCA statements on these trees are root-dependent. I re-measured with a root-free version
   (`rerun/unrooted_clade_recovery.py` → `.tsv`: the smallest side of any edge that contains all
   members). The **counts do not change** (3/1/1/1/1/2). But G69's statement that "clade 1's MRCA
   is the entire tree (purity 0.19)" is a **rooting artefact**. Unrooted, clade 1 sits in a
   365-tip side at purity 0.948 in `ours` and 0.969 in `linsi`/`narrow`. It is recovered
   topologically but has low support (UFBoot 35–79).
2. **"≤3/11" is a support statement, not a topology statement.** On purity ≥0.90 alone, the
   re-inferences recover **4–6 of 11** clades (ours 5, toro 6, wide 5, narrow 4, fftnsi 4,
   linsi 6) [MEASURED]. Examples: linsi clade 3 is 234/235 pure at UFBoot 89; toro clades 1, 3
   and 7 are ≥0.95 pure.
3. **Positive control (not done in V4, done here).** The same unrooted purity rule on Mestre's
   **published** tree recovers 10/11 clades at purity ≥0.9 (only Clade 10 fails, at 0.604). With
   its single support value it gives 8/11 at ≥95 and 9/11 at ≥85 (`rerun/published_tree_positive_control.tsv`).
   One caveat: Clade 11's edge reads support 0 because it is the root-adjacent edge in the
   published newick. The instrument can therefore return a high count, but the published tree
   has one support value where the re-inferences have two, so the comparison is not symmetric.
4. **The pre-registration was not followed** (`prereg/s3_tree_and_mestre_reconstruction.md`, 08-19):
   (a) E4 has **no arm for re-inferring Mestre's sequences**; that arm came from a "parallel
   session Q3" (G67, TRACKER), after the prereg. (b) E4c says "against 10 clades, never 11" and
   "monophyly + AU test". G69/G74 score **X/11 including Clade 10**, which is not a bipartition
   even on Mestre's own tree, and run no AU test. (c) The model policy is
   `-mset LG,WAG,JTT,Q.pfam,VT,Dayhoff`, but the six runs' ModelFinder lists have **no Q.pfam**.
   (d) The policy is "One alignment: MAFFT L-INS-i", but 4 of 6 trees use `--auto` (FFT-NS-2).
   (e) Amendment 6 (TBE) is absent: `s6_trees/v2_iqtree_report_sweep.tsv` shows tbe=0.
5. **This is not Mestre's method.** Mestre used IQ-TREE 1.6.12, ModelFinder over 546 models,
   LG+F+R10, an untrimmed RT0–7 MSA and 1,928 taxa. V4 used IQ-TREE 3.1.3, a 5-matrix mset,
   anchor windows trimmed to occ ≥0.5 (219–303 sites) and 1,843 taxa. LG+F+R10 was selected
   anyway in 5 of 6 runs (linsi chose LG+F+I+R10).
6. **The six are not independent.** G74 calls them "6 independent re-inferences", but they are
   one taxon set, four frames × `--auto`, and two extra aligners on the `ours` frame.
7. **Stale prose.** `PAPER_SKELETON.md:89-90`, `REPORT.md:63` and `TRACKER.md:45` still say
   "RF 0.19–0.23 vs 0.09–0.13" and "2×". FINDINGS G74, X14 and s3_object V4 carry the correction
   (0.143–0.232; 1.70×). The "0.09–0.13" is 0.087–0.134 rounded.
8. **Missing provenance.** `25_august_paper_positioning/experiments/X14_mestre_reconstruction.md`
   lists s2b/s5b/s5e as the arm's scripts but **omits s7h/s7i**, which produce its G74 row.
   `MESTRE_EVIDENCE.md` (08-20) and responses 13 and 14 (08-20) all predate the re-inference and
   never mention it. `MANIFEST.sha256` has **no `cache/` entries**, so the trees are not
   manifested. The hashes of the manifested s7h, s7i, s2b, s5b and s8b scripts and tables verify OK.
9. `FROZEN_DENOMINATORS.tsv` has **no Mestre row**: none of 1,843, 1,926, 1,928 or 1,814 appears.

## 6. Adjacent Mestre assets (brief)

- `cache/fold/mestre`: 1,919 ESMFold PDBs from 8 Ibex array tasks (logs dated 08-23), input
  `mestre_tofold.faa`. `cache/fm/mestre_span`: 1,902 span-sliced PDBs (producer UNKNOWN).
  `cache/fs_mestre`: foldseek (MMseqs 10.941cd33) all-vs-all, 1,902 structures,
  `ava.tsv` = 3,601,534 lines. `s8b_mestre_clade_structure.py` → G89.
- cd-hit V4.8.1 (`retron_tradicional`), with commands in the logs:
  - `rt0_rt7_claim_ledger/cache/mestre_clusters`: 1,926 proteins, `-c 0.5..0.9 -n 3/4/5/5/5 -M 4000 -T 4 -d 0`,
    giving 714/1226/1562/1841/1907 clusters.
  - `rt0_rt7_domain_test_v4_and_paper/cache/mestre_clust`: `mestre_tofold.faa` (1,919),
    c0.5/0.7/0.9 with `-n 3/4/5`, giving 712/1556/1900 clusters. Note that c70 uses `-n 4` here but `-n 5` in the ledger.
- `ncrna_extractor_detector_V3/cache/ibex_mestre` is a **partial mirror** of Ibex
  `/ibex/project/c2366/RETRONS/Mestre_replication/realpipe/results`. It holds 1,925 terminal dirs
  with only `ground_truth_metadata.json` (1,925) and `tool_integrated_results.json` (1,920). The
  per-tool subdirectories (padloc, defensefinder, infernal, prodigal, myrt) are empty.
- G74 appears in: `s6_trees/{FINDINGS.md, VERDICT.md, PROPOSALS.md, responses/01_corrections_to_tree_stage.md, scripts/v1_resolution_recompute.py, tables/v1_resolution_by_set.tsv, logs/boundary.txt}`;
  `s3_object/{FINDINGS.md, PROPOSALS.md, VERDICT.md, responses/01_2026-08-25_s3_object.md, scripts/v4_rf_frame_vs_aligner.py, logs/v4.log}`;
  `s4_motifs/{S3_REVIEW.md, PLAN.md, FINDINGS.md, VERDICT.md, scripts/rv1b_g74_ratio.py, scripts/rv1_s3_review_checks.py, tables/rv1b_g74_ratio.tsv}`;
  `rt0_rt7_lit_and_narrative/{FINDINGS.md, responses/01_…first_pass.md, responses/09_…foundation.md}`. It does **not** appear in `s1_review`.

## 7. Files written by agent_v4

- `v4_assets.tsv`: 107 assets with sha256/size/mtime/producer/inputs/n_records. Directory hash =
  sha256 of the sorted `relpath\tsha256` lines; broken symlinks are recorded as `BROKEN_SYMLINK`.
- `rerun/s7i_stdout.txt`, `rerun/s7h_stdout.txt`: V4 scripts re-run unmodified with cwd = V4 stage.
- `rerun/unrooted_clade_recovery.{py,tsv}`: root-independent re-measurement. The two empty
  columns (`root_tip_side`, `s7i_style_note`) are unused placeholders.
- `rerun/published_tree_positive_control.{py,tsv}`: the same rule on Mestre's published tree.
- `rerun/build_assets.py`: generator for `v4_assets.tsv`.
- `reconstructed_alignments/`: rebuilt occ50 alignments, README and SHA256SUMS.
