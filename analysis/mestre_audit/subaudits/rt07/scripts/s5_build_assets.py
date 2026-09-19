#!/usr/bin/env python3
"""s5 - assemble rt07_assets.tsv: hash + characterise every asset in the inventory.

Sequence counts / substitute status come from asset_characterisation.tsv (s3) when the path is
there; otherwise from a direct read. Directories get n_files, bytes and a manifest hash
(sha256 of the sorted 'relpath<TAB>sha256' lines). Read-only against sources.
"""
from __future__ import annotations

import csv
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import dir_manifest, sha256  # noqa: E402

OUT = Path(__file__).resolve().parents[1]
V2 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V2"
V3 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3"
V4 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4"
T = f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test"
TT = f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree"
PT = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE"
RDB = "/home/borg/RESEARCH-retron-db"
H7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/historical"

TORO_FRAME = ("Toro-2014 frame: blocks 1-3 (cols 68-182; toro742.hmm states 68-105) = RT0-RT1; "
              "block 29 cols 1297-1305 (states 296-304) = RT7/region Y; Toro C-terminal cut = col 1305")

# (id, path, kind, full_or_extract, interval_definition, producer, command, notes)
A = [
 ("R01", f"{H7}/toro_2014_Rt0-Rt7.FASTA", "reference_extraction_alignment", "extract (RT0-RT7 extraction, 742 RTs, NOT Mestre)",
  "Toro & Nisa-Martinez 2014 RT0-RT7 extraction; 1466 cols; N-cut modal col 68 (413/742), C-cut modal col 1305 (598/742); retrons median anchor-174..+55 (YxDD Y=0)",
  "Toro & Nisa-Martinez 2014 (published supplement)", "n/a (published)", "identical sha to V4 MELISSA_DATA/supporting_material copy; 0 Mestre tips"),
 ("R02", f"{H7}/TableS1_Toro_2014.XLSX", "reference_table", "NA", "Table S1: RT class, RT phylogeny (102 'Retrons'), aa REfSeq full length", "Toro 2014", "n/a", "joined to alignment headers by V4 s05 (723/742)"),
 ("A01", f"{PT}/IBEX_TESTS/Mestre_sequences", "source_protein_set_dir", "full-length",
  "none (per-terminal protein_aminoacid.fasta + genome + CDS)", "owner Ibex download/rescue (retron_download.log, retron_rescue.log)", "IBEX script not local (IBEX_UNINSPECTED)",
  "1926 protein files; 112 '|rescued' substitutes; terminals 461,1774 absent; clean=1814"),
 ("A02", f"{V3}/ARIS_OUTPUT/mestre_scope_audit/cache/mestre_1928_proteins.faa", "protein_set", "full-length", "none", "V3 mestre_scope_audit (pooled per-dir FASTAs)", "concatenation of Mestre_sequences/*/protein_aminoacid.fasta", "misnamed 1928; holds 1926"),
 ("A03", f"{T}/cache/mestre_from_V3/mestre_1926_proteins.faa", "protein_set", "full-length", "none", "copy of A02 (PROVENANCE.md)", "cp", "renamed to true count"),
 ("A04", f"{V3}/ARIS_OUTPUT/mestre_scope_audit/cache/mestre_1926_vs_RT17CORE.sto", "hmmalign_projection (pre-trim)", "full-length projected",
  "RT17_CORE frame span17 = RT1-150..RT7+150, 305 states; landmarks RT1=42..RT7=276; states 1-41 = 'RT0 region'; NO Toro RT0 column", "V3 m5_rt0_placeability.py", "hmmalign RT17_CORE.hmm mestre_1928_proteins.faa (V3 stage2b step3 model)", "source of x1-x5 tables"),
 ("A05", f"{T}/cache/mestre_from_V3/mestre_1926_vs_RT17CORE.sto", "hmmalign_projection (pre-trim)", "full-length projected", "as A04", "copy of A04", "cp", ""),
 ("B01", f"{T}/cache/frame/toro742.hmm", "HMM (extraction-frame profile)", "NA",
  "LENG 465 = states 1-67 -> cols 1-67 (occ<=0.135), 68-304 -> cols 68-1305, 305-465 -> cols 1306-1466 (occ<=0.046). " + TORO_FRAME,
  "V4 rt0_rt7_domain_test A3 (ad hoc, logged in cache/frame/hmmbuild.log)",
  "hmmbuild -n toro742_RT0-RT7 -o cache/frame/hmmbuild.log cache/frame/toro742.hmm toro_2014_Rt0-Rt7.FASTA  (HMMER 3.4, ALL defaults: symfrac 0.5, fragthresh 0.5, PB weights, no --hand)",
  "REPRODUCED here byte-identical except DATE (LENG 465, EFFN 57.246971, CKSUM 2099268526). Every Toro row is a 'fragment' (L<=0.5*alen) so leading/trailing gaps = missing data -> flank columns become match states; --fragthresh 0 gives LENG 230"),
 ("B02", f"{T}/cache/frame/hmmbuild.log", "log", "NA", "", "hmmbuild", "see B01", "no non-default options listed"),
 ("B03", f"{T}/cache/frame/mestre1926_in_toro_frame.sto", "hmmalign_projection (pre-trim) + mapali", "full-length projected (not extracted)",
  "4203 cols; RF match cols = 465 toro742 states; " + TORO_FRAME, "V4 rt0_rt7_domain_test A6 (ad hoc; consumed by s09/s10/s14/s17)",
  "hmmalign --amino --mapali toro_2014_Rt0-Rt7.FASTA -o cache/frame/mestre1926_in_toro_frame.sto cache/frame/toro742.hmm cache/mestre_from_V3/mestre_1926_proteins.faa",
  "REPRODUCED here byte-identical (sha 607b4478...). 742 Toro rows + 1926 Mestre rows. This is the only full-protein -> Toro RT0-RT7 frame mapping for Mestre tips"),
 ("B04", f"{T}/cache/projected_coordinates.tsv.gz", "per-sequence block coordinates", "coordinates",
  "per sequence x 29 Toro-frame blocks: start_res/end_res in own protein numbering (MAP->RF chain)", "V4 s14_per_sequence_coordinates.py", "python s14_per_sequence_coordinates.py",
  "77,372 rows / 2,668 seqs (55,854 Mestre rows); gives residue boundaries of blocks 1..29 = usable RT0/RT7 cut coordinates in Toro frame"),
 ("B05", f"{T}/tables/rt0_rt7_frame.tsv", "frame definition table", "NA", "29 occupancy>=0.5 width>=4 blocks with RT intervals (RT0-RT1 = blocks 1-3; RT7 = block 29) + LtrA P0A3U0/Ec86 coords", "V4 s07 + s11_canonical_rt_numbering.py", "python s11_canonical_rt_numbering.py", "4 blocks motif-anchored (RPL, PQGG, YADD, FLG), 25 order_interpolated"),
 ("B06", f"{T}/tables/mestre_in_toro_frame_occupancy.tsv", "result table", "NA", "per-block Mestre-1926 vs Toro-742 occupancy", "V4 s09_mestre_in_toro_frame.py", "python s09_mestre_in_toro_frame.py", "blocks 1-2: 0.166/0.208 vs 0.696/0.716"),
 ("B07", f"{T}/tables/absence_vs_nonalignability.tsv", "result table", "NA", "upstream-of-col68 residues (Mestre) + Table S1 flank mass", "V4 s10_absence_vs_nonalignability.py", "python s10_absence_vs_nonalignability.py", "verdict: non-alignable, not absent"),
 ("B08", f"{T}/cache/nterm/mestre_nterm_ext.faa", "extract (N-terminal, pre-RT0)", "extract",
  "residues upstream of projected column of toro742 state 68 (= Toro col 68 = block-1 start), len>=30; median start anchor-214, end anchor-161", "V4 s17_verify_trackD_extensions.py", "python s17_verify_trackD_extensions.py (MIN_LEN=30; mmseqs easy-cluster 0.30/c0.5)", "1319 terminals incl. 79 substitutes; N-terminal EXTENSION, not RT0-RT7 body"),
 ("B09", f"{T}/cache/a9_ibex/nterm.faa", "extract (N-terminal)", "extract", "identical content to B08", "V4 A9 (InterProScan staging)", "copy of B08", ""),
 ("B10", f"{T}/cache/frameR/frameR.afa", "de novo MSA (pre-trim)", "full-length (Mestre) + Toro retron extracts",
  "no interval; MAFFT of 102 ungapped Toro retron extracts + 1540 full-length Mestre (every 5th held out)", "V4 s20_build_frame_R.py", "mafft --auto --quiet --thread 8 frameR_seed.faa; hmmbuild --amino --informat afa -n FRAME_R", "5088 cols; FRAME_R.hmm 446 states; boundaries mapped back to Frame U"),
 ("B11", f"{T}/cache/frameR/frameR.hmm", "HMM", "NA", "446 states, Mestre-derived retron frame", "V4 s20", "see B10", "not a reporting frame"),
 ("B12", f"{T}/scripts/s07_frame_blocks_and_anchors.py", "script (frame logic)", "NA", "occupancy>=0.5 blocks, width>=4; motif anchors", "V4", "", ""),
 ("B13", f"{T}/scripts/s09_mestre_in_toro_frame.py", "script (projection readout)", "NA", "MAP->RF chain; blocks 1-2 control, 12-18 core, 25-29 C-term", "V4", "", ""),
 ("B14", f"{T}/scripts/s10_absence_vs_nonalignability.py", "script", "NA", "boundary = first state at/after Toro col 68", "V4", "", ""),
 ("B15", f"{T}/scripts/s14_per_sequence_coordinates.py", "script (per-seq coordinates)", "NA", "", "V4", "", ""),
 ("B16", f"{T}/scripts/s20_build_frame_R.py", "script", "NA", "", "V4", "", ""),
 ("B17", f"{T}/cache/toro742_rt_class.tsv", "join table", "NA", "Toro header -> Table S1 key/class", "V4 s05 (A1)", "", "723/742 joined"),
 ("C01", f"{TT}/cache/mestre_toro.faa", "anchor-window extract", "extract",
  "protein[a-197 : a+57] (inclusive), a = first [YFWH].DD match (0-based Y); clipped at protein ends",
  "V4 rt0_rt7_domain_test_v4_and_tree (G67/G74; producer script not found locally)", "inferred & VERIFIED here: 1843/1843 identical from mestre_1926_proteins.faa",
  "'toro' window derived from G55 median offsets vs 80 Toro retron spans; direct Toro-retron median is anchor-174..+55. 83 of 1926 lack [YFWH].DD -> excluded"),
 ("C02", f"{TT}/cache/mestre_narrow.faa", "anchor-window extract", "extract", "protein[a-150 : a+80]", "as C01", "VERIFIED 1843/1843", ""),
 ("C03", f"{TT}/cache/mestre_ours.faa", "anchor-window extract", "extract (144 whole proteins shorter than window)", "protein[a-220 : a+120] (project span17-like window)", "as C01 (s4a_build_tipset.py LO,HI)", "VERIFIED 1843/1843", ""),
 ("C04", f"{TT}/cache/mestre_wide.faa", "anchor-window extract", "extract (969 whole proteins)", "protein[a-260 : a+160]", "as C01", "VERIFIED 1843/1843", ""),
 ("C05", f"{TT}/cache/mestre_tofold.faa", "protein_set", "full-length", "none", "V4 s5a_fold_esmfold.py input", "", "1919 terminals"),
 ("C06", f"{TT}/cache/fm/mestre_span", "structure set (PDB)", "extract (structure sliced)", "ESMFold full-length models sliced to a-220..a+120 ([LIV].DD fallback for 59)", "V4 s6g_span_pdbs.py", "python s6g_span_pdbs.py", "1902 PDBs; 90 substitutes; 144 whole-length"),
 ("C07", f"{TT}/cache/mestre_trees", "IQ-TREE outputs", "NA", "trees on occ50-trimmed MAFFT alignments of C01-C04 windows (input out/*_occ50.afa)", "V4 G67/G74 Ibex runs", "mafft --auto (ours also FFT-NS-i, L-INS-i) -> drop cols >50% gaps -> IQ-TREE 3.1.3 MFP (LG+F+R10) UFBoot1000",
  "alignments themselves IBEX_UNINSPECTED (not local); sites: toro 231, narrow 219, ours 297, wide 295, fftnsi 290, linsi 303"),
 ("C08", f"{TT}/scripts/s7h_mestre_frames.py", "script (tree comparison)", "NA", "documents ours -220..+120, toro -197..+57", "V4", "", "does not write the windows"),
 ("C09", f"{TT}/scripts/s5g_E3_fidelity.py", "script (Toro-span measurement)", "NA", "Toro retron spans matched verbatim in our proteins; anchor [YFWH].DD", "V4 G55", "", "basis of the -197..+57 'toro' window"),
 ("C10", f"{TT}/tables/s5g_E3_fidelity.tsv", "table", "NA", "per-protein Toro span start/end vs our window", "V4 s5g", "", "80 retron spans"),
 ("D01", f"{V4}/ARIS_OUTPUT/s5_admission/cache/mestre_ref.mafft.faa", "de novo MSA (pre-trim)", "full-length aligned", "none", "V4 s5_admission p5_build_toro_profile.py",
  "mafft --auto --anysymbol --thread 24 mestre_1928_proteins.faa", "6056 cols"),
 ("D02", f"{V4}/ARIS_OUTPUT/s5_admission/cache/mestre_ref.trim50.faa", "trimmed MSA", "column-trimmed (not contiguous extract)", "keep cols with <=50% gaps (Toro 2026 rule) -> 310 cols", "p5_build_toro_profile.py", "python p5_build_toro_profile.py", "Toro 2026 states 203 positions 'RT1-RT7 core'; this gives 310"),
 ("D03", f"{V4}/ARIS_OUTPUT/s5_admission/cache/toro_recon_RT1_RT7.hmm", "HMM", "NA", "LENG 293 from D02", "p5", "hmmbuild --amino -n toro_recon_RT1_RT7", ""),
 ("D04", f"{V4}/ARIS_OUTPUT/s5_admission/scripts/p5_build_toro_profile.py", "script", "NA", "", "V4", "", ""),
 ("E01", f"{V4}/ARIS_OUTPUT/stage0_positioning/cache/refbuild/mestre_ref.aln", "de novo MSA (pre-trim)", "full-length aligned", "none", "V4 stage0 Stage D measurement", "mafft --auto (7.62 s, MEASUREMENTS.txt)", "6202 cols"),
 ("E02", f"{V4}/ARIS_OUTPUT/stage0_positioning/cache/refbuild/ref_gappyout.aln", "trimmed MSA", "column-trimmed", "trimal -gappyout -> 262 cols", "stage0", "trimal -gappyout", "drops 1 seq (1925)"),
 ("E03", f"{V4}/ARIS_OUTPUT/stage0_positioning/cache/refbuild/ref_automated1.aln", "trimmed MSA", "column-trimmed", "trimal -automated1 -> 63 cols", "stage0", "trimal -automated1", ""),
 ("E04", f"{V4}/ARIS_OUTPUT/stage0_positioning/cache/refbuild/mestre_ref.faa", "protein_set", "full-length", "none", "stage0", "", ""),
 ("E05", f"{V4}/ARIS_OUTPUT/stage0_positioning/cache/refbuild/MEASUREMENTS.txt", "log", "NA", "", "stage0", "", "commands/timings"),
 ("F01", f"{RDB}/data/derived/reference_msa_v1.afa", "de novo MSA (registered derived)", "full-length aligned", "none (trimming deliberately NONE)", "retron-db stage3_placement_toolkit s01_build_reference.py",
  "mafft --auto --anysymbol --thread N (7.525); hmmbuild --amino (3.4)", "6056 cols; tip-named incl. 16 short names; 112 substitutes"),
 ("F02", f"{RDB}/results/stage3_placement_toolkit/cache/reference.hmm", "HMM", "NA", "LENG 412 from full-length MSA", "s01_build_reference.py", "hmmbuild --amino", ""),
 ("F03", f"{RDB}/results/stage3_placement_toolkit/scripts/s01_build_reference.py", "script", "NA", "", "retron-db", "", ""),
 ("G01", f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_aligned.fasta", "de novo MSA (pre-trim)", "full-length aligned", "none (docstring claims 'RT0-7 scope' but input is full proteins)", "owner phylo_V4_april.py Block D2",
  "mafft --globalpair --maxiterate 1000 --thread N reference_RTs_raw.fasta", "5811 cols"),
 ("G02", f"{PT}/PIPELINE_SEQUENCES/outfiles/retron_RT_custom.hmm", "HMM", "NA", "LENG 336 (Apr 5); built on full-length G-INS-i MSA", "phylo_V4_april.py D3", "hmmbuild --cpu N retron_RT_custom.hmm reference_RTs_aligned.fasta", "backup (Mar 9) LENG 408; FINAL_V2_MARCH LENG 405"),
 ("G03", f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_hmmaligned.fasta", "hmmalign --trim (de facto extract)", "extract (HMM match-span)",
  "first..last match state of G02: median anchor-181..+123 (p05 -225, p95 +162)", "phylo_V4_april.py Block E", "hmmalign --trim --outformat afa retron_RT_custom.hmm <ref+query>; '.'->'-'", "NOT an RT0-RT7 definition; 3224 cols; 112 substitutes"),
 ("G04", f"{PT}/PIPELINE_SEQUENCES/outfiles/reference_RTs_aligned_synced.fasta", "hmmalign --trim subset", "extract (HMM match-span)", "as G03, 1910 tree-synced", "phylo_V4_april.py", "", ""),
 ("G05", f"{PT}/IBEX_TESTS/output_files_FINAL_V2_MARCH/reference_RTs_hmmaligned.fasta", "hmmalign --trim (earlier run)", "extract (HMM match-span)", "median anchor-182..+124", "phylo_V2/V3 (March)", "", "2699 cols"),
 ("G06", f"{PT}/reference_RTs_aligned.fasta", "de novo MSA", "full-length aligned", "none", "owner phylo pipeline (earlier)", "", "6037 cols"),
 ("G07", f"{PT}/IBEX_TESTS/phylo_V4_april.py", "script (owner pipeline)", "NA", "no extraction step; MAFFT full-length -> hmmbuild -> hmmalign --trim", "owner", "", ""),
 ("G08", f"{V3}/MELISSA_SCRIPTS/phylogenetic_tree/phylo_v4.py", "script (owner pipeline)", "NA", "byte-identical prefix (first 74,854 B) of G07", "owner", "", ""),
 ("G09", f"{PT}/Supplementary_mestre_Tree.nwk", "published tree", "NA", "Mestre 2020 Supplementary File S1 (newick only)", "Mestre 2020", "", "1928 tips; only Mestre phylogeny artefact published"),
 ("H01", f"{V3}/MELISSA_SCRIPTS/custom_and_hmm_analysis/extract_domain_sequences_171", "subdomain extracts + coordinates", "extract (structural subdomains)",
  "fingers/palm/thumb/active-site from foldseek/HHpred structural boundaries (not RT0-RT7)", "V3 extract_subdomain_seqs.py <- annotate_rt_domains_v5.py", "", "166 Mestre terminals (Khan validated subset), 0 substitutes; identical copy in V2"),
 ("I01", f"{V3}/ARIS_OUTPUT/mestre_scope_audit/scripts/m5_rt0_placeability.py", "script", "NA", "RT17_CORE states 1-41 = RT0 region", "V3", "", ""),
 ("I02", f"{V3}/ARIS_OUTPUT/mestre_scope_audit/tables/x4_mestre_nterminal_reach.tsv", "result table", "NA", "first matched RT17_CORE state", "V3 m5", "", "median state 33; 1313/1926 reach <=41"),
 ("I03", f"{V3}/ARIS_OUTPUT/mestre_scope_audit/tables/x5_mestre_rt0_region_profile.tsv", "result table", "NA", "per-state occupancy states 1-41", "V3 m5", "", ""),
 ("I04", f"{V3}/ARIS_OUTPUT/mestre_scope_audit/tables/x2_mestre_block_occupancy.tsv", "result table", "NA", "RT0 region mean 0.217; 0/41 states >=0.85", "V3 m5", "", "VOID E4 retracted conditional 0.89"),
 ("J01", f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v2/scripts/s2_block_extents.py", "script (RT1..RT7 extents)", "NA", "IC>=1.0 bits around RT17_CORE anchors, window states 42-276", "V4 v2", "", "not Toro frame; no RT0"),
 ("J02", f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v2/instrument/make_core_block.py", "script (trim)", "NA", "RT17_CORE states 42-276 (RT1..RT7), or 52 IC blocks", "V4 v2", "", "explicitly RT1-RT7, excludes RT0"),
 ("J03", f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v3/scripts/s13a_subdomain_placement.py", "script", "NA", "crystal-derived fingers/palm/thumb on anchor coords (-220..+120)", "V4 v3", "", "no Mestre sequences"),
 ("K01", f"{V2}/ARIS_OUTPUT/phylogeny_paper_plan/cache/job2/job2_aligned.fasta", "hmmalign of OUR retron reps", "NA", "PIPELINE HMM frame (expected width 3224)", "V2 job2_placement.sh", "", "NOT Mestre sequences (0 Mestre-named; k-mer overlap only via shared proteins)"),
]


def main() -> None:
    ch = {r["path"]: r for r in csv.DictReader(open(OUT / "asset_characterisation.tsv"), delimiter="\t")}
    rows = []
    for aid, path, kind, foe, interval, prod, cmd, notes in A:
        p = Path(path)
        if not p.exists():
            rows.append([aid, path, kind, "MISSING", "", "", "", "", foe, interval, prod, cmd, notes])
            continue
        st = p.stat()
        mt = dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
        if p.is_dir():
            n, b, h = dir_manifest(p)
            sha, byt = f"manifest:{h}", f"{b} ({n} files)"
        else:
            sha, byt = sha256(p), str(st.st_size)
        c = ch.get(path)
        if c:
            nseq = c["n_records"] + (f" ({c['n_unique_terminals']} Mestre terminals)" if c["n_non_mestre_records"] != "0" else "")
            subs = f"Y ({c['n_rescued_substitute_terminals']})" if c["n_rescued_substitute_terminals"] not in ("0", "") else "N"
        else:
            nseq, subs = "", "NA"
        rows.append([aid, path, kind, sha, byt, mt, nseq, subs, foe, interval, prod, cmd, notes])
    # fill a few known counts not in s3
    known = {"A01": ("1926 (1814 clean)", "Y (112)"), "C06": ("1902", "Y (90)"), "H01": ("166 x5 domain FASTAs", "N"),
             "G04": ("1910", "Y (111)"), "B04": ("2668 seqs (1926 Mestre terminals)", "Y (112)"), "R01": ("742", "N (no Mestre)"), "K01": ("6100", "N")}
    for r in rows:
        if r[0] in known and not r[6]:
            r[6], r[7] = known[r[0]]
    hdr = ["asset_id", "path", "kind", "sha256", "bytes", "mtime", "n_seqs", "includes_substitutes",
           "full_or_extract", "interval_definition", "producer", "command", "notes"]
    with open(OUT / "rt07_assets.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(hdr)
        w.writerows(rows)
    print(len(rows), "assets")


if __name__ == "__main__":
    main()
