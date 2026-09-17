# DATASET REGISTRY — heavy local datasets, and where they are

**None of the files in this document are in GitHub.** They live on the workstation. This
registry is what GitHub carries *instead* of them: path, size, record count, unit, sha256,
producing task, purpose and downstream consumers — enough for a future session to know
exactly what exists, what it means and whether the local copy is the right one.

Sizes and hashes are quoted from landed manifests (`g5_dataset_manifest.tsv`,
`g5a_census_summary.tsv`, `INPUTS.tsv`), not re-computed here.

Host: this workstation. Project root
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7`. All paths below are relative to it.

---

## 1 · Stage-1 canonical derived datasets — `data/derived/`

Produced by the `dbchar_g1…g7b` gates. These are the substrate everything else reads.

| name | path | bytes | records | unit | sha256 | by | GitHub |
|---|---|---|---|---|---|---|---|
| exact RT catalogue (FASTA) | `data/derived/rt_exact_v1.faa` | 230,435,383 | 501,561 | exact RT | `bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655` | `dbchar_g2` | **LOCAL ONLY** |
| exact RT catalogue (parquet) | `data/derived/rt_exact_v1.parquet` | 113,736,821 | 501,561 | exact RT | `44fd615e73f97134eb20e9c5d2e142ca4eff733e919746cc622ecd2cf05f7b9f` | `dbchar_g2` | LOCAL ONLY |
| raw records | `data/derived/rt_records_v1.parquet` | 701,984,868 | 3,059,700 | raw record | `546605034a2e5f21794a842d…` | `dbchar_g2` | LOCAL ONLY |
| window CDS | `data/derived/rt_window_cds_v1.parquet` | ~594 MB | — | CDS in window | — | `dbchar_g2` | LOCAL ONLY |
| loci | `data/derived/rt_loci_v1.parquet` | ~145 MB | — | genomic locus | — | `dbchar_g2` | LOCAL ONLY |
| physical loci | `data/derived/rt_physical_loci_v1.parquet` | ~45 MB | — | physical locus | — | `dbchar_g2` | LOCAL ONLY |
| tool calls | `data/derived/rt_tool_calls_v1.parquet` | 72,251,025 | 3,051,238 | record | `27c6b5c6fbf06f042fee8d5a…` | `dbchar_g6` | LOCAL ONLY |
| family baseline | `data/derived/rt_family_baseline_v1.parquet` | 19,012,020 | 501,561 | exact RT | `92e0197959174945eaad9b32…` | `dbchar_g4` | LOCAL ONLY |
| ncRNA calls / pairs / recurrence | `data/derived/rt_ncrna_*.parquet` | ~64 MB | — | RT–ncRNA pair | — | `dbchar_g3` | LOCAL ONLY |
| CDS recovery | `data/derived/rt_cds_recovery_v1.parquet` | ~4 MB | — | exact RT | — | `dbchar_g2b` | LOCAL ONLY |

**Unit discipline:** raw record, genomic locus, exact RT, taxonomic occurrence and RT–ncRNA
pair are *different* populations with *different* denominators. Never mix them.

## 2 · g5a — the frozen eligibility partition — `data/derived/rt07_g5a/`

Produced by `results/rt07_g5a_eligibility_census/` (commit `cf96dd1`). **This is where the
g5/g6 denominator comes from.**

| name | path | bytes | records | unit | sha256 | GitHub |
|---|---|---|---|---|---|---|
| eligibility partition | `g5a_eligibility_partition.tsv.gz` | 20,084,071 | 501,561 | exact RT | `249e334b04b2db7975b498949d57bcc89613e43512baad5a007b47ea21de7dfa` | **LOCAL ONLY** |
| eligible identifiers | `g5a_eligible_ids.txt.gz` | 13,514,830 | 369,381 | exact RT | `6f2028fa46563ebedb11442bf21341ce0565b230d5ccf68f748ba3b676d02d11` | LOCAL ONLY |
| ineligible records + metadata | `g5a_ineligible_records.tsv.gz` | 6,937,603 | 132,180 | exact RT | `9fd48b77df6d8e3e1af0aa7e2b1358b1690b587cfb6e0911804991da42139a06` | LOCAL ONLY |

Purpose: fixes `G5_ELIGIBLE_N = 369,381` and retains every excluded record with an exact
reason. Consumers: `g5` (sharding), `g6` (denominators).

## 3 · g5 — the canonical mapped dataset — `data/derived/rt07_g5/`

Produced by `results/rt07_g5_catalogue_application/` (commit `cf96dd1`) with instrument
`rtmap-1.0.0/53a1e738a19b3896`. **This is the dataset g6 consumes.**

| name | path | bytes | rows | unit | sha256 | GitHub |
|---|---|---|---|---|---|---|
| **state calls** | `g5_states.parquet` | 108,189,029 | 55,407,150 | exact RT × frozen state | `5bdcb6e3ef4344da8d64a8fe9f59fd641138115b68dc88aff4c3e80b970a4eae` | **LOCAL ONLY** |
| **sequence summaries** | `g5_sequences.parquet` | 41,842,661 | 369,381 | exact RT | `55bd268a1b8ff01bd8d4cf61f85bfda3909919b3faec74da752186a6a6ebbbb5` | **LOCAL ONLY** |
| catalytic | `g5_catalytic.parquet` | 26,660,834 | 369,381 | exact RT | `95dcb20aac95946cb3c54c41b7bd0dc496239422620416d15675611806bf0887` | LOCAL ONLY |
| ineligible | `g5_ineligible.parquet` | 10,192,406 | 132,180 | exact RT | `253a092fd4d72b1593cbb15a5b82ca2739891cc3570336da0370f5aff36b4635` | LOCAL ONLY |
| run failures | `g5_run_failures.parquet` | 4,177 | 0 | failed record | `4b1d1ae5ce9033c3e1471b20a68633ba51e20ee643ad4998114fc6142de0f52a` | LOCAL ONLY |
| **metadata crosswalk** | `g5_metadata_crosswalk.parquet` | 56,149,583 | 501,561 | exact RT | `02c6e54d12e4a1c2ec3d35f8d0260d8104077f87365e16a509a9940d4f47dd14` | LOCAL ONLY |

All joins are on `rt_hash`. The crosswalk covers the **whole** 501,561-record catalogue with
an `in_g5_eligible` flag, so any denominator can be taken without re-deriving eligibility.

Integrity check at any time:

```bash
bash results/rt07_g5_catalogue_application/verify.sh
```

## 3b · embed_g0 — oriented ncRNA sequences — `data/derived/rt_ncrna_oriented_v1.*`

Produced by the `embed` track (`launchers/LAUNCHER_03_rt_ncrna_embedding_compatibility.md`),
script `ARIS_OUTPUT/embed_g0_population_audit/scripts/a02_ncrna_fasta.py`.

**Why it exists.** The Stage-1 derived layer carries `nc_seq_hash` and `nc_seq_len` but **no
ncRNA sequence**. This dataset closes that gap. It unblocks RNA language-model
representations *and* the ncRNA clustering that the dbchar workbench records as its
outstanding blocker.

| name | path | bytes | records | unit | sha256 | GitHub |
|---|---|---|---|---|---|---|
| oriented ncRNA (FASTA) | `data/derived/rt_ncrna_oriented_v1.fna` | 3,953,406 | 16,458 | exact oriented ncRNA | `d04297a823e249061a320897233afac581bbfb0bf26b33942f5c0f6630258e35` | **LOCAL ONLY** |
| oriented ncRNA (parquet) | `data/derived/rt_ncrna_oriented_v1.parquet` | 1,492,723 | 16,458 | exact oriented ncRNA | `5c81dfe91e0dac8144839c945f1d7694d388354cbf2841ad14d7097f98187706` | LOCAL ONLY |
| provenance | `data/derived/rt_ncrna_oriented_v1.provenance.json` | 1,143 | — | — | `c04b6048359e6b5f6a5a8a5ce2e6bbd5ef778f018bc65f9f3f5210bf7b13632f` | LOCAL ONLY |
| manifest | `data/derived/rt_ncrna_oriented_v1.MANIFEST.tsv` | 364 | 3 | file | — | LOCAL ONLY |

| | |
|---|---|
| **key** | `nc_seq_hash` — joins `rt_ncrna_pairs_v1`, `rt_ncrna_exact_pairs_v1`, `ncrna_family_baseline_v1` |
| **population** | PAIR-ELIG — every ncRNA in `rt_ncrna_exact_pairs_v1.parquet` (30,924 pairs) |
| **orientation** | `sequence_oriented` as stored in the raw corpus. All source placements carry `orientation_corrected = True`; **zero** hashes appear under conflicting orientation states |
| **verification** | **16,458 / 16,458 sha256 round-trip.** Every sequence's `sha256(seq.upper())` was recomputed and asserted equal to its registered `nc_seq_hash`, which is how `dbchar_g2` defined that hash (`e01_extract.py:294`). Zero mismatches |
| **determinism** | order is `sorted(nc_seq_hash)`, one sequence per line; a re-run is byte-identical |
| **alphabet** | `ACGKNRTY` — 214 sequences (1.30 %) carry IUPAC ambiguity, 4,117 nt (0.151 %), almost all `N` |
| **lengths** | 34–395 nt, median 151, total 2,719,581 |
| **source** | `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/` (corpus pin `8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00`); 16,351 hashes from the Retron master, 107 from 17 others |
| **producer** | `a02_ncrna_fasta.py` sha256 `2d2192d450ac3cf98e357bf64fce7dfa8699230aca1c22343eac790e3eb976ea`, git `53ce532` |
| **rebuild cost** | 32 s, single pass, CPU only |

⚠️ **Placement caveat — an operator step remains.** The canonical derived layer is in the main
worktree and is read-only from the `embed` track's sandbox, so these files were written to the
**`embeddings-g0` worktree's** `data/derived/`. Promoting them to
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/` is a copy of four
byte-identical files verified against `rt_ncrna_oriented_v1.MANIFEST.tsv`. Until that copy is
made, **two derived layers exist** and a consumer must be told which one it is reading.

Verify at any time:

```bash
cd <worktree> && sha256sum -c <(awk 'NR>1{print $3"  "$1}' data/derived/rt_ncrna_oriented_v1.MANIFEST.tsv)
```

## 4 · g5 shard scratch — `ARIS_OUTPUT/rt07_g5/` — **DO NOT DELETE YET**

| | |
|---|---|
| size | **12 GB** (`out/` 12 GB, `shards/` 181 MB, `work/` 102 MB) |
| contents | 512 shard FASTAs, 512 × 4 shard TSVs, 512 `DONE` sidecars |
| manifest | `shards/shard_index.tsv` (41 KB) + one `DONE` per shard carrying input sha256, instrument digest and all four output hashes |
| can the canonical dataset be rebuilt from it? | **Yes** — `scripts/merge.py` |
| can it be rebuilt from scratch? | Yes — `bash run.sh`, ~10 min on 44 cores |
| does any landed table reference it? | **No** — zero hits for `ARIS_OUTPUT` in either bundle's tables |

**Cleanup condition — not yet met.** Delete only after: (a) `data/derived/rt07_g5/` is
independently backed up **off this host**; (b) its hashes are registered here and verified
after the backup; and (c) `g6` no longer needs shard-level diagnostics. Until all three hold,
this is the only copy of the per-shard audit evidence.

## 5 · Raw / external corpora — `MELISSA_DATA/`

| path | size | class | GitHub |
|---|---|---|---|
| `MELISSA_DATA/supplementary_material/` | ~1.8 GB | raw metadata corpora | **LOCAL ONLY** |
| `…/metadata_files/ncbi_bacteria_assembly_summary.txt` | 1.3 GiB | raw input | LOCAL ONLY |
| `…/metadata_files/gtdb_bacteria_metadata.tsv.gz` | 225 MiB | raw input | LOCAL ONLY |
| `…/metadata_files/uhgg_v2.0.2_metadata.tsv` | 110 MiB | raw input | LOCAL ONLY |
| `…/metadata_files/mgnify_human_gut_metadata.tsv` | 110 MiB | raw input | LOCAL ONLY |

Also registered in `data/README.md`. Gitignored as of 2026-09-17.

## 6 · Small load-bearing assets that ARE in GitHub

Do not let any future ignore rule catch these:

| path | bytes | why |
|---|---|---|
| `results/rt07_g4a_repaired/work/GII.deriv.hmm` | 220,026 | **the frozen profile — the production coordinate system.** The only file re-included from an otherwise ignored `work/` directory |
| `results/rt07_g4b_production_mapper/code/rtmap/*.py` | ~60 KB | the frozen instrument |
| `results/rt07_g4b_production_mapper/control/*.tsv` | ~10 KB | frozen parameters, 150 anchors, RT0–RT7 crosswalk |
| `review-stage/manifests/*`, `review-stage/roots/*` | ~80 KB | external pinned roots; bundles cannot be verified without them |
| every `results/*/tables/*.tsv` | ~5 MB total | the canonical summaries |

## 7 · Duplication note

`ARIS_OUTPUT/` contains up to **four** copies of the large `dbchar_g2` products
(`rt_records_v1.parquet` 670 MiB × 4, `rt_window_cds_v1.parquet` 566 MiB × 4,
`rt_exact_v1.faa` 220 MiB × 4). The canonical copy is the one in `data/derived/`. The
`ARIS_OUTPUT` copies are rerun scratch and are safe to delete independently of §4; they are
not referenced by any landed bundle.
