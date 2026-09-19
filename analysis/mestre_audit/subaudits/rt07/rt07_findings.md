# rt07 — Mestre RT0–RT7 material: forensic inventory findings

Date 2026-09-18. Read-only against every source. Env `retron_tradicional` (HMMER 3.4, MAFFT 7.525).
Ibex not mounted. Anything that exists only on Ibex is marked **IBEX_UNINSPECTED**, not absent.

Files in this directory:
- `rt07_assets.tsv`: 64 assets, with sha256, size, mtime, sequence counts, substitute status, interval, producer and command.
- `asset_characterisation.tsv`: every Mestre-bearing sequence file checked against the per-terminal proteins.
- `scan_hits.tsv`, `header_scan_hits.tsv`: content scan of 8,097 files by 10-mer matching, plus a header scan.
- `toro2014_per_sequence_termini.tsv`, `toro2014_termini_summary.tsv`, `toro742_hmm_blocks_to_match_states.tsv`
- `mestre_rt0_reach_clean_vs_all.tsv`
- `scripts/`: s1–s5, all rerunnable.

Clean reference: `IBEX_TESTS/Mestre_sequences`. It has 1,926 protein files. 112 of them are `|rescued` substitutes, so the clean set is 1,814. Terminals 461 and 1774 have no protein file.

## 1. Does any asset preserve Mestre's actual RT0–RT7 extracts or alignment? **No.**

Evidence:
- **What Mestre published.** Mestre 2020's only phylogeny file is Supplementary File S1, a newick tree. We checked this in the local PDF text layer (`stage0_positioning/cache/mestre_pdf/mestre2020_layout.txt`, lines 199, 217 and 230). The other supplementary files are Table S1/S2 CSVs. No MSA was published, and no domain boundaries are given ("domain boundaries not given": `mestre_methods_parameters.tsv`).
- **Scope of the scan.** We scanned 8,097 sequence and alignment files across the V2–V5 projects, `RESEARCH-retron-db`, `RETRON_APRIL`, `RETRON_3rd_BATCH`, `PHYLOGENETIC_TREE` and `v7/references`. Files that hold Mestre sequences fall into three groups:
  - (i) the on-disk full-length proteins, or local re-alignments of them;
  - (ii) sub-sequences cut by *this project's* rules;
  - (iii) hmmalign projections.
- **Why none can be Mestre's.**
  - Every asset carrying the 1,926 set includes all 112 rescued substitutes. Mestre's alignment could not contain them.
  - Every extract is exactly reproducible from the on-disk proteins with a locally defined rule (see §2).
- **Lineage of the owner's pipeline.** `phylo_V4_april.py` (and its prefix `V3/MELISSA_SCRIPTS/phylogenetic_tree/phylo_v4.py`) calls its alignment "RT0–7 scope". In fact it is MAFFT G-INS-i on the **full proteins**, then hmmbuild, then `hmmalign --trim`.
- **`research-wClaude-PART1*`.** These folders hold no sequence or alignment files. They contain only prose, e.g. `RT0-RT7_BRIEFING.md`.
- **IBEX_UNINSPECTED:**
  - the `out/*_occ50.afa` and pre-trim MAFFT alignments behind `V4 …v4_and_tree/cache/mestre_trees/*.iqtree`;
  - the original Ibex copies of the phylo pipeline outputs;
  - the download/rescue scripts.

  All of these are downstream of the same on-disk proteins, so none could be Mestre's alignment.

## 2. Closest reusable extraction procedure, and how the Toro 2014 HMM was built

**Toro HMM (`V4 rt0_rt7_domain_test/cache/frame/toro742.hmm`)**
- Built with plain `hmmbuild -n toro742_RT0-RT7 -o hmmbuild.log toro742.hmm toro_2014_Rt0-Rt7.FASTA`.
- HMMER 3.4 **defaults**: symfrac 0.5, fragthresh 0.5, PB weighting, **no `--hand`**.
- **Reproduced here** identical except the DATE line: LENG 465, EFFN 57.246971, CKSUM 2099268526.
- **The 465 match states are inflated.** Every Toro row has fewer than 0.5 × 1,466 residues, so HMMER tags all 742 rows as fragments. Their leading and trailing gaps are then counted as missing data, and every near-empty flank column becomes a match state:
  - states 1–67 map to columns 1–67 (occupancy ≤ 0.135);
  - states 305–465 map to columns 1306–1466 (occupancy ≤ 0.046);
  - with `--fragthresh 0` the same build gives LENG 230.
- **Occupancy blocks** (V4 s07/s11; 29 blocks at occupancy ≥ 0.5) and their match states:
  - **RT0–RT1** = blocks 1–3 = columns 68–182 = **states 68–105**. Block 1 is columns 68–79, states 68–79.
  - **RT7** = block 29 = columns 1297–1305 (GFDFLGFTF, containing FLG/VTG) = **states 296–304**. Column 1305 / state 304 is the RT7 C-terminal end.
  - RT5 (YADD) = columns 1097–1103 = states 251–257.
- Only 4 blocks are motif-anchored (RPL, PQGG, YADD, FLG). The other 25 are `order_interpolated`.

**Closest reusable extraction for Mestre tips**
- `mestre1926_in_toro_frame.sto`: `hmmalign --amino --mapali <Toro FASTA> toro742.hmm mestre_1926_proteins.faa`. **Reproduced byte-identical** (sha 607b4478…).
- Read together with `projected_coordinates.tsv.gz` from s14. That table gives per-sequence start/end residues for all 29 blocks, including block 1 (RT0 start) and block 29 end (RT7 end).
- This is the only full-protein → Toro RT0–RT7 mapping for Mestre tips. Its limitation: it projects the proteins, it does not cut them.

**Explicit cut rules (all verified: 1,843/1,843 sequences identical)**
The four `v4_and_tree` windows are anchor-relative intervals, cut as `protein[a+L : a+H]` inclusive. Here `a` is the first `[YFWH].DD` match (0-based at Y), clipped at the protein ends. The 83 proteins with no match are dropped, and the 1,843 kept include 91 substitutes.

| window | L..H |
|---|---|
| narrow | −150..+80 |
| **toro** | −197..+57 |
| ours | −220..+120 |
| wide | −260..+160 |

The "toro" window comes from G55's median offsets against 80 Toro retron spans. Measured directly on the 102 Toro-2014 retron extracts, the span is anchor **−174 (IQR −191..−163) to +55 (IQR +51..+57)**. So the "toro" window runs about 23 residues further N-terminal than Toro's own retron cuts.

## 3. N-terminal (RT0) reach of Mestre sequences in prior tables

Those tables used the 1,926 set, substitutes included. The figures below for the clean 1,814 were recomputed from the existing projection, with no new alignment.

**V3, RT17_CORE frame (x2/x4/x5)**
- Median first matched state is 33; 1,313/1,926 (68%) reach states ≤ 41.
- The unconditional RT0-region occupancy is 0.217, and 0 of 41 states reach 0.85.
- The earlier "conditional 0.89" figure is VOID (E4).
- Caveat: RT17_CORE has no Toro RT0 column.

**V4, Toro frame (s09)**

| set | block 1 | block 2 | block 3 | core |
|---|---:|---:|---:|---:|
| Mestre 1,926 | 0.166 | 0.208 | 0.896 | 0.984 |
| Toro 742 | 0.696 | 0.716 | — | — |
| **Clean 1,814** | **0.155** | **0.200** | **0.906** | — |
| 112 substitutes | 0.346 | 0.330 | — | — |

The substitutes inflate the N-terminal occupancy.

**s10 verdict: non-alignable, not absent**
- 99.9% of the 1,926 carry unaligned residues upstream of column 68; 87.1% carry more than 20. The median is 39 (IQR 26–65).
- Clean 1,814: median 38, 87.4% carry more than 20.
- The stated conclusion is "retron RTs have no homologous RT0".
- Correction to s10's wording: these are residues upstream of block 1, not strictly residues "the model could not align". About 10% of them sit in the fragment-artefact flank states 1–67.

## 4. Toro 2014 extraction termini (742 sequences, 1,466 columns)

**First non-gap column**
- Median 68 (p05 52, p25 68, p75 76, p95 256).
- Column 68 is the mode: 413 of 742 start there. In GroupII, p05 through p75 are all column 68.

**Last non-gap column**
- Median 1305 (p05 1101, p25 1256, p75–max 1305/1466).
- 598 of 742 end at exactly column 1305.
- So the C-terminal cut is highly consistent at the end of the RT7 block. The N-terminal cut is consistent for GroupII, DGR and CRISPR-RT (all at column 68) but not for retrons.

**Retrons (Table S1 'RT phylogeny' = Retrons; n = 102)**
- First column: median 85 (IQR 48–89). The starts cluster at columns 42–51 and 85–89.
- Last column: 82 of 102 end at column 1305.
- Residue counts: median 231 (IQR 222–249).
- **RT0 occupancy:**

  | | retrons | GroupII |
  |---|---:|---:|
  | mean, blocks 1–3 | 0.288 | 0.901 |
  | block 1 | 0.21 | 0.894 |
  | block 2 (V4 s12) | 0.0 | — |
  | block 3 (V4 s12) | 0.935 | — |

**So retron sequences in the Toro alignment largely do *not* occupy the N-terminal RT0 blocks.** Toro's own retron extracts start roughly at block 3 (RT0–RT1 boundary region) or place their N-terminal residues in gappy, non-block columns.
