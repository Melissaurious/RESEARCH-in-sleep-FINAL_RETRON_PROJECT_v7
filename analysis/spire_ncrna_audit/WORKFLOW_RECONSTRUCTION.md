# WORKFLOW RECONSTRUCTION — Toro 2026 / SPIRE retron pipeline scripts

Source: `SPIRE_retron_pipeline_scripts.zip` (sha256 `3d4a99b2…`, 12 members, 51,719 bytes
unpacked) plus the separate `SPIRE_retron_type_specific_HMMs.tar.gz` (`046d42d5…`). Both read
from `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/references/rt0_rt7/toro_2026/`,
unpacked to `ARIS_OUTPUT/spire_ncrna_audit/unpacked/`, never modified. Every statement below
was checked against the script text; nothing was taken from the README alone. Per-file facts:
`ASSET_REGISTER.tsv`.

## 1 · Which of the seven claimed workflows exist

| # | operator's belief | present? | executable as released? | complete from raw inputs? |
|---|---|---|---|---|
| 1 | general RT HMM screening | yes, inline in `00` step 1 (`hmmsearch` + 160-bit filter) | yes, in form | **no** — `general_retron_RT.hmm` is not released; the tarball's `all_retron_RT.hmm` is the 29 type models concatenated, not a general model |
| 2 | type-specific calibration / classification | yes, `02` | yes, in form | **no** — needs `mestre_1928_refs.fasta` with `group\|`-prefixed IDs (unreleased); released thresholds exist; 17/29 types have `neg_max > pos_min` |
| 3 | accessory-protein enrichment | yes, `03` (+ `01`, mmseqs, hmmscan in `00`) | `03` yes | **no** — `01` never writes the protein FASTA `00` feeds to mmseqs; the membership table `03` needs is produced by no script |
| 4 | upstream sequence extraction | yes, `04` | GenBank mode only | **no** — needs a hand-annotated GenBank (RT CDS tagged `RT`); GFF mode raises `ValueError("…not yet implemented…")` |
| 5 | taxonomic / ecological analysis | yes, `05` | yes | **no** — `phylum`, `biome_top` columns joined by no script |
| 6 | novelty prioritisation | yes, `06` | yes | **no** — phylogenetic score is a placeholder equal to the confidence score ("update manually after inspecting EPA-ng placement tree"); EPA-ng/IQ-TREE not scripted |
| 7 | de novo ncRNA discovery (mLocARNA + R-scape) | yes, `07` | **yes after two environment fixes** | **no** — input FASTA is assembled by hand; no boundary is assigned; its summary parser is wrong |

**Verdict:** the package documents a workflow; it does not reproduce one from raw inputs.
Unreleased intermediates are required at steps 1, 2, 3, 4 and 5, plus manual steps at 4, 6 and 7.

## 2 · Execution order as written

```
00_run_full_pipeline.sh   (conda: struct_annot)
  1  hmmsearch general_retron_RT.hmm × spire_all_proteins.faa → keep ≥160 bits (IDs list, never used again)
  2  [optional] mafft + hmmbuild for a NEW_LINEAGE
  3  02_hmm_calibrate_and_classify.py  (candidates = the FULL proteome, not the ≥160-bit list)
  4  inline: drop protein_id matching k141_|k119_ (MEGAHIT-style contigs)
  5  01_extract_neighborhood.py  → mmseqs easy-cluster 30 %/80 % → hmmscan Pfam-A
  6  03_accessory_enrichment.py ; 05_taxonomic_stats.py
  7  06_novelty_prioritization.py
  "Next: run 07 for candidate novel lineages"
manual  04_extract_flanking_upstream.py --gbk <hand-annotated> --window 270|300
manual  07_run_mlocarna_rscape.sh upstream_300bp.fasta outdir label   (conda: mlocarna_env)
manual  r2r figure; judge obs/exp > 1.1; cmbuild + cmcalibrate
```

`00` never calls `04` or `07`. The ncRNA path is detached from the driver and begins from a
hand-assembled per-lineage FASTA.

## 3 · Hard-coded paths

`BASE=/home/ntoro/spire/retron_pipeline_v2`, `GFF_DIR=/home/ntoro/spire/representative_genomes/prodigal_gff`,
`CONTIG_GFF_MAP=/tmp/contig_to_gff.tsv`, `${BASE}/db/Pfam-A.hmm`, `${BASE}/hmm_rt/…`. None exist here.

## 4 · External tools and versions

| tool | where named | SPIRE version | recovered how | local |
|---|---|---|---|---|
| HMMER | README, requirements, `00`, `02` | 3.3 (README); HMMs built with **3.3.2** | README; HMM file headers `HMMER3/f [3.3.2 \| Nov 2020]` | 3.4 |
| mLocARNA | README, `07` | **2.0.1** | README | 2.0.1 ✔ |
| R-scape | README, `07` | **2.0.4** (patch level UNKNOWN) | README | 2.0.4.a ✔ |
| Infernal | README, `07` next steps | 1.1.5 | README | 1.1.5 ✔ |
| ViennaRNA (inside mLocARNA) | — | UNKNOWN | — | 2.7.2 |
| R2R | `07` comments | UNKNOWN | — | present |
| MAFFT | README, `00` | 7.490 | README | 7.525 |
| CMfinder | README only | 0.4 | README | 0.4.1.9 (wrapper broken) |
| MMseqs2, EPA-ng, Gappa | README | "latest" = UNKNOWN | — | — |
| IQ-TREE2, HHsuite, taxonkit, trimal, Prodigal | README/requirements | 2.3.2, 3, 0.14, 1.4, 2.6.3 | README | not invoked by any script |
| Python pkgs | requirements.txt | numpy 1.24.3, pandas 2.0.3, scipy 1.11.4, statsmodels 0.14.1, biopython 1.81, Python 3.11 | requirements | — |

Clustering tools for ncRNA homolog grouping: **none** — grouping is manual.

## 5 · Stochastic steps

mLocARNA is deterministic for a fixed input order (its guide tree comes from pairwise scores).
R-scape's null distribution comes from simulated alignments with a fixed default seed, so
reruns are identical. MAFFT (used only by us, Arm B-seq) is deterministic. The manual selection
of ≤ 40 sequences is the dominant and **undocumented** source of variation.

## 6 · Defects found by execution (smoke tests in `ARIS_OUTPUT/spire_ncrna_audit/smoke/`)

1. `07` calls `rscape`; bioconda installs `R-scape`. Shim needed.
2. `07`'s inline Python imports numpy; the mLocARNA env has none. Shim needed.
3. `--alifold-cons` and `--indel-open` are not mLocARNA 2.0.1 option names; they work only as
   Getopt::Long prefix abbreviations of `--alifold-consensus-dp` and `--indel-opening`.
4. **Summary parser bug:** `float(parts[6])` reads the *substitutions* column of `.cov`, not the
   E-value (column 5 of 8). Result: "Significantly covarying BPs (E<0.05): 0" whenever R-scape
   reports significant pairs. Reproduced: toy set R-scape 2 → wrapper 0; `POS_XIII_1` 24 → 0.
   Any published claim that depends on this printed count is not supported by the script.
5. The obs/exp lines are searched for in `*.surv`, which holds survival-function data. They are
   in R-scape stdout (`# BPAIRS expected to covary …`, `# BPAIRS observed to covary …`), which
   `07` does not save. The "> 1.1× obs/exp" criterion therefore can never be printed by `07`.
6. `07` prints `result.R2R.sto` under `mlocarna/results/`; R-scape actually writes
   `rscape/result_1.R2R.sto`.

Arm A in this audit runs `07` **byte-identical to the archive member** with shims 1–2 only, and
recomputes the summary correctly from R-scape's own files.
