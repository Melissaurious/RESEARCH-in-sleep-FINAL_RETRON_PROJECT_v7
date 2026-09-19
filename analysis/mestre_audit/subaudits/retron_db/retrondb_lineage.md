# RESEARCH-retron-db — Mestre lineage audit (read-only, 2026-09-18)

Subject: `/home/borg/RESEARCH-retron-db/results/stage1_mestre_replication_and_insights/`
(landed in commit `76ad2af`, 2026-09-12 23:07 +0300). Companion files are `retrondb_assets.tsv` (87 rows)
and `retrondb_inputs_today.tsv` (5,827 rows).

## 1. Launcher scope (`launchers/LAUNCHER_stage1_mestre_replication_and_insights.md`, 546 lines)

- **In scope:** replicate Mestre 2020 **on the published tree and the published per-tip table** (both are RAW
  inputs). The five objectives are to pin the inputs and the denominator, clade recovery/monophyly,
  a fold-space phylogenetic null plus the largest-cluster fraction, a paper reading (Methods and
  Discussion), and a conclusions section.
- **Explicitly excluded (§2):** any audit of V4 prior work; the label-concordance null ("mathematically
  invariant", named as blocked); the three-tool agreement analysis (the Ibex `Mestre_replication/`
  per-terminal verdicts, 537/1928 terminals); the expanded-dataset improvement; and
  **"No tree re-inference at scale"** unless §4.2 made it the only route, with the cost declared first.
  The launcher does not scope any alignment. The only alignment it mentions is `myRT-FastTree2.refpkg`,
  which is hashed as a RAW input and never used.
- **Prior-tree rule (§0.1):** V4 X14/X15/X16, CLAIM_REGISTER, FINDINGS, VERDICT, the Ibex run and
  scripts s2b/s5b/s8b are "IDEAS ONLY. No number carried". Four quantities are sealed (§0.2) until
  they have been measured.
- **§3b claims `mestre:C1`–`C9`:** C1 monophyly N/11, C2 reference-set size and the four circulating
  values, C3 algorithmic reproducibility of the clade assignment, C4 the fold-space silhouette against
  a phylogenetic null, C5 the largest-cluster fraction, C6 whether the ncRNA-in-clade nesting is
  already stated in Mestre, C7 axis count 2-not-4 (HIGH circularity), C8 whether Mestre published the
  tree-reconstruction failure, C9 the Khan overlap.
  **The committed launcher still shows every claim as `UNPROVEN`.** The bundle README lists all nine
  as "proposed SUPPORTED". No operator sign-off (CL-5) is recorded anywhere in git, and the landing
  commit says the claims "remain where the operator put them".

## 2. Retros and responses

- Retro 2026-09-11 (build plus two Codex adversarial passes). It records 7 defects and then 6
  defects. C3 was restated: "never 11" was withdrawn. C4 was reversed and then narrowed: z 1.67 →
  2.74/5.10 → 2.75–2.81. C7 was corrected to "4 axes collapse to 3, not 2". The prior-script docstrings
  leaked sealed numbers, so three BLIND rows were regraded to RECONCILED. A hard-coded
  `mean_fraction_labels_changed` string was replaced by a measured ARI of 0.9996.
- Retro 2026-09-12 (close). s08 was added and recovered 0 of 115 proteins via BV-BRC/NCBI.
  `terminal_515` was never a gap, so there are 2 missing terminals, not 3. The Toro overlap was
  closed at 1912/1928 but stays **[UNVERIFIED] recon, outside the bundle**.
- r06 (Toro): `Suppl_Toro_Tree.txt` has 9,141 tips, matching the paper. Toro is a co-author of
  Mestre, so the population is same-lineage. **Zero bundle scripts read a Toro file.** The files are
  only hashed. The recon overlap was 1841/1928 (a lower bound); r07 corrected it to **1912/1928,
  with the 16 absentees being exactly the validated retrons**. None of this is landed.
- r08 (placement-script assessment): this is a WA-K.7 design review of the Ibex
  `/ibex/project/c2350/PHYLOGENETIC_TREE/retron_phylogenetic_tree.py`: about 870 lines, "Adapted from
  Mestre 2020 and Durrant 2023", with blocks A/D/E/F/G.
  - **Verdict:** keep the radial visualiser (blocks A and G). **The placement half (D–G) has never
    run.** Only `reference_tree.png` exists, and mafft, hmmalign, raxml and epa-ng are all absent on
    the Ibex login node.
  - **Defects D1–D8.** D1 is the main one: `_core_id` sync would silently prune 129/1928 tips
    (the 16 validated retrons plus 113 substituted or absent). D2 is path-existence caching. D3 is a
    call to `raxmlHPC`, which does not exist here, and the script hardcodes PROTGAMMAAUTO where
    Mestre used LG+F+R10. D4 ignores the LWR. D5 notes that clade 10 is paraphyletic. D6 is a hand
    clade map that contains Vc137. D7 uses absolute or in-place output paths. D8 has no seed, lock
    or hashes.
  - **Recommendation:** "Rescue the visualisation, rewrite the placement". It warns that "placing
    onto Mestre's tree requires an alignment they never published … it cannot produce *Mestre's*
    placements."
  - r08 also reports, unverifiable from here, that the Ibex `Supplementary FiLE S1_RT_Tree.newick.nwk`
    is byte-identical to the pinned tree (`7a9a1129…`).

## 3. Scratch vs bundle (`ARIS_OUTPUT/stage1_mestre_replication_and_insights/`)

- Scratch holds 331 files (19 MB). The bundle holds 60 files (5.3 MB).
- 53 bundle files are byte-identical to the same path in scratch.
- 3 SVGs differ only in matplotlib `dc:date` and clip-path ids, so the SVGs are non-deterministic.
- 7 files exist only in the bundle. Of these, INPUTS.tsv, PROVENANCE.md and env.lock are
  byte-identical to `discarded_bundle_assembly1/`. MANIFEST, OUTPUTS, README and STATUS are unique
  to the bundle.
- `discarded_bundle_assembly1/` (56 files, 2026-09-11 16:45–16:48) is the **first bundle assembly,
  made before the adversarial passes**. Its README is the unfilled BUNDLE template ("STATUS:
  UNVERIFIED"), and its figures use the old names (clade_monophyly, foldspace_null_sweep, …). It was
  renamed rather than deleted because `rm` was denied (retro 09-11). Scratch also keeps the stepwise
  versions tables_prev2–5, bundle_tables_v1–v3 and figures_prev2–5.
- All 59 hashes in OUTPUTS.tsv match the current bundle files. The file set is exactly
  OUTPUTS plus OUTPUTS.tsv. `git status` is clean.

## 4. Inputs today (`retrondb_inputs_today.tsv`)

- 5,827 sealed inputs: **5,798 are unchanged (same sha256) and 29 are missing**. All 29 missing
  inputs are under `/home/borg/RETRON_CLAUDE_PART1/supplementary_material/`, which is now empty.
- Byte-identical copies exist for all 29:
  - 23 are in `…FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material/`, including
    `Mestre_supplementary_material.csv` (Root A only), `toro_2014_Rt0-Rt7.FASTA`, the refpkg and the
    metadata.
  - The 6 `databases_metadata_files/stats/*.json` are **not in v7 MELISSA_DATA**. They are identical
    in `…FINAL_RETRON_PROJECT_WORK/MELISSA_DATA/…`, `…RETRON-DB_V3/MELISSA_DATA/databases_metadata_files/stats/`
    and `RETRONS_january_2026/…/genome_fetcher/…/stats/`. No bundle script consumes them.
- Everything else is unchanged: the V3 root, V4 fold pdbs (1,919), V4 `ava.tsv` (127 MB),
  Mestre_sequences (1,928 terminals plus 8 provenance files) and the two paper texts.
- `run.sh` still depends on out-of-repo V4 paths (fold/ and ava.tsv) for s00/s02. These are intact
  today.

## 5. Bundle scripts vs V4 prior scripts (all sha256 differ; see assets TSV)

| bundle | V4 ancestor | relation |
|---|---|---|
| s00_pin_inputs | none | new |
| s01_clade_recovery | s2b (unrooted edge-split monophyly) + s5b (rule D, the same S∈{70..95}×F∈{.005,.01,.02} grid, maximal smaller-side clusters) | **Independent re-implementation of the same criteria.** Shared lines are boilerplate only (about 10). New: a 1928/1928 join (V4 joined 1912 by `Accesion` only), a rooted reading as well as the unrooted one, and seed-bad controls |
| s02_foldspace_null | s8b (silhouette of true labels on 1−TM, **global** 30-perm null) | The true-label silhouette is kept. The null is **replaced** by random monophyletic partitions plus within-block nulls, and ARI and a triangle check are added. About 5 lines are shared |
| s03 nesting, s04 paper, s06 blind, s07 figs | none (s03 echoes the X15 idea) | new |
| s05 khan | topic-adjacent to s6c (Khan calibration) | no shared logic |
| s08 recovery | none | new (A05, 2026-09-12) |

**V4 Mestre arms not carried over:**
- s7h/s7i **re-inferred Mestre's tree** from 1,843 proteins: mafft (fftnsi/linsi) plus IQ-TREE, in
  four RT0–7 frames (ours/toro/narrow/wide), with clade-node support. Six `.treefile`s are in
  `V4/…/cache/mestre_trees/`.
- The pLDDT≥90 fold-space arm (s8b).
- The ESMFold folding itself (s5a). The bundle consumes V4's folds and TM matrix but does not
  re-derive them. No V4 script builds `cache/fs_mestre/`, so the TM matrix's producing command is
  unrecorded.

## 6. Does anything in retron-db re-infer, align or place onto the Mestre tree?

I checked with `git log --all -S` and `git grep` for iqtree, mafft, FastTree, epa-ng, pplacer,
hmmalign and raxml.

- **stage1 bundle: no.** The only hits are the refpkg name in the INPUTS list, a
  "FastTree-style rooting" comment in s01, and the paper text.
- **stage3_placement_toolkit (commit `274046c`, 2026-09-12 23:09) does all three, as a TOOLING
  task:**
  - **Mestre alignment built:** `data/derived/reference_msa_v1.afa` (sha `4e864b3f…`, verified;
    1,926 seqs × 6,056 cols) from `mafft --auto`, with no trimming, plus a `hmmbuild` HMM.
    ⚠️ **It includes the 112 substituted proteins** (flagged `is_substituted_protein=Y`, but aligned
    under the published tip names). Stage1 excluded these from its primary fold-space population.
  - **Placement:** `place.py` (`hmmalign --mapali` then `epa-ng`) was smoke-run only. It placed 20
    held-out references (20/20 returned to their clade) and 20 shuffled controls onto the pruned
    Mestre tree (`reference_tree_pruned_v1.nwk`, `fca6e3c8…`).
  - **Tree inference:** `build_tree.sh` (raxml-ng, LG+G4) ran on a **100-taxon smoke subset
    only**, labelled "not a phylogeny". No full 1,926-tip re-inference exists.
- Other hits for these terms are env.lock/REPORT package lists (stage0/2/4) and rtdomain-g0
  profile inventories. None of them concern Mestre.

## 7. Other consumers of Mestre in retron-db

- `stage3_placement_toolkit` is the successor to r08. It consumes stage1's join, the tree and
  `clade_recovery.tsv`. It found that 4 of 17 entries in the hand clade map were wrong (Mx162/Ne144/Sa163
  are 10 not 11, and Vc137 was mis-keyed), and that the reference HMM misses 20 of 1,926 self-hits.
- `stage0_db_characterization/scripts/w05_integrity.py` has a note that C21's ncRNA CMs are all
  Mestre-authored (the corroboration trap).
- `stage2_leakage_and_sampling-c1` cites stage1's hard-coded-string defect as prior art. It uses no
  Mestre data.
- `rtdomain-g0-provenance` inventories the V3 `tierB_retron_mestre.hmm` profiles, not the tree.
- `stage4_db_characterization_full-c1/REPORT.html` matched only inside base64, a false positive.
- Docs:
  - `DATA_EXPERT_PRIMER.md` L182: "stage1_mestre… the Mestre tree, clade recovery". L349: the
    `mestre:C1-C9` ids are taken.
  - `LAUNCHER_AMENDMENTS.md` A05 records the gap that was reported but never closed, which led to s08.
  - `data/README.md` registers the stage3 MSA and tree.
  - `docs/REFERENCE_prior-artifact-paths.md` gives the paths.
  - `CLAUDE.md` says nothing Mestre-specific. It only names "retron clade classification" as a
    subject.

## 8. Git history

- The whole repo has 71 commits (2026-09-08 → 09-14). Stage-1 files were touched by only two commits:
  - `3972c06` (2026-09-12 15:16) added the launcher, the r01–r08 responses and the retros.
  - `76ad2af` (2026-09-12 23:07) added the bundle.
- **The bundle has not been modified since landing.** Only one commit touches the path, and the
  working tree is clean.
- The governance submodule is pinned: `general` is at `d7bfc47` in both HEAD and `76ad2af`
  (`.gitmodules` points to `RESEARCH-in-sleep-GENERAL_v6`). The pin moved to d7bfc47 in `aed6e0b`
  (2026-09-10).

## 9. Findings that contradict or weaken the bundle's own claims

1. **The environment lock is wrong.** `env.lock` is a `conda env export` of **base**
   (`prefix: /home/borg/miniconda3`, python 3.12.7, no ete3/scipy/pandas/matplotlib/sklearn).
   `run.sh` runs under `envs/retron_tradicional`. `PROVENANCE.md` hashes this lock
   (`7372d135…`), so what BS-10/BS-15 pin is not the executing environment.
2. **Stale provenance.** `PROVENANCE.md` is byte-identical to the discarded first assembly
   (2026-09-11 16:46). It gives `git_sha: aed6e0b` and `date: 2026-09-11`, yet the bundle went
   through three more seals and gained s08 on 2026-09-12.
3. **Claim status is still open.** Every claim status is "proposed". The launcher §3b still reads
   UNPROVEN, and no operator sign-off is committed.
4. **Toro is unused.** The Toro relationship (1912/1928, same-lineage population) is not in the
   bundle, even though the bundle hashes both Toro files.
5. **Maturity is scope-limited.** V4 went further on tree re-inference: six IQ-TREE re-inferences of
   1,843 Mestre proteins, plus frame and aligner sensitivity. retron-db stage1 dropped this by launcher
   design. The only retron-db alignment is stage3's own mafft MSA, which includes the 112 substituted
   proteins.
6. **The input copy is not self-contained.** The launcher says to copy every small file, but the
   bundle's `inputs/` lacks `Suppl_Toro_Tree.txt`, `toro_2014_Rt0-Rt7.FASTA` and the refpkg. These
   are hashed only, and their Root-A location is now gone. Identical copies survive in v7
   MELISSA_DATA.
