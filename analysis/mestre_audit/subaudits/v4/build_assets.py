#!/usr/bin/env python3
"""agent_v4: build v4_assets.tsv (read-only over V4). Dir hash = sha256 of sorted 'relpath\tsha256' lines."""
import hashlib, os, time, csv, re, sys
V = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/"
A = V + "ARIS_OUTPUT/"
T = A + "rt0_rt7_domain_test_v4_and_tree/"
R = A + "rt0_rt7_domain_test/"
S0 = A + "stage0_positioning/"
P = V + "25_august_paper_positioning/"
def sh(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def nrec(p):
    ext = p.rsplit(".", 1)[-1] if "." in os.path.basename(p) else ""
    try:
        if ext in ("faa", "aln", "afa", "fasta", "fa") or re.search(r"\.c\d+$|/m\.c\d$|mestre\.c\d0$", p):
            return f"{sum(1 for l in open(p) if l.startswith('>'))} seqs"
        if ext == "sto":
            names = set()
            for l in open(p):
                if l and not l.startswith("#") and not l.startswith("//") and l.strip():
                    names.add(l.split()[0])
            return f"{len(names)} seqs"
        if ext in ("treefile", "nwk"):
            s = open(p).read(); return f"{len(re.findall(r'[(,]([^(),:;]+):', s))} tips"
        if ext == "iqtree":
            m = re.search(r"Input data: (\d+) sequences with (\d+) amino-acid sites", open(p).read())
            return f"{m.group(1)} seqs x {m.group(2)} sites" if m else ""
        if ext in ("tsv", "clstr"):
            if ext == "clstr": return f"{sum(1 for l in open(p) if l.startswith('>'))} clusters"
            return f"{sum(1 for l in open(p) if l.strip() and not l.startswith('#')) - 1} rows"
        if ext in ("py", "md", "txt", "log", "sh"):
            return f"{sum(1 for _ in open(p, errors='replace'))} lines"
    except Exception as e:
        return f"ERR {e}"
    return ""
rows = []
def add(aid, path, kind, producer, inputs, notes, nrec_override=None):
    mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path))) if os.path.exists(path) else "MISSING"
    if not os.path.exists(path):
        rows.append([aid, path, kind, "MISSING", "", mt, producer, inputs, "", notes]); return
    if os.path.isdir(path):
        lines, tot, n = [], 0, 0
        for d, _, fs in os.walk(path):
            for f in fs:
                fp = os.path.join(d, f); rp = os.path.relpath(fp, path)
                if os.path.islink(fp) and not os.path.exists(fp):
                    lines.append(f"{rp}\tBROKEN_SYMLINK:{os.readlink(fp)}"); n += 1; continue
                lines.append(f"{rp}\t{sh(fp)}"); tot += os.path.getsize(fp); n += 1
        lines.sort()
        dh = hashlib.sha256("\n".join(lines).encode()).hexdigest()
        rows.append([aid, path, kind, f"dir:{dh}", tot, mt, producer, inputs, nrec_override or f"{n} files", notes])
    else:
        rows.append([aid, path, kind, sh(path), os.path.getsize(path), mt, producer, inputs, nrec_override or nrec(path), notes])

# ---- 1. v4_and_tree
for s, pr, inp, note in [
 ("s2b_mestre_clade_monophyly.py", "-", "MELISSA_DATA/supporting_material/{supp_material_systematic_prediction_paper.csv,Supplementary_mestre_Tree.nwk}", "G16: 10/11 clades are splits on PUBLISHED tree; Clade 10 not. Writes tables/s2b_*.tsv"),
 ("s5b_E4a_rule_D_on_mestre.py", "-", "same supp csv + published nwk", "G50/G56: Rule D surface on PUBLISHED tree (single support value per node). Writes tables/s5b_E4a_ruleD_surface.tsv"),
 ("s5e_E4b_ruleD_on_our_trees.py", "-", "cache/E1/*.nwk (27 FastTree frames of OUR corpus, not Mestre seqs)", "G54: Rule D on OUR trees + rarefaction to 1928; not a Mestre re-inference"),
 ("s7h_mestre_frames.py", "-", "cache/mestre_trees/*.treefile", "PRINT-ONLY (no table). Resolution % and pairwise RF (raw and collapsed UFBoot<95). mtime precedes 4 of 6 trees; re-run by agent_v4 reproduces all printed values"),
 ("s7i_clade_support.py", "-", "cache/mestre_trees/*.treefile; ../rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_proteins.faa; ../rt0_rt7_domain_test/cache/mestre_usable_index.tsv", "PRINT-ONLY. Clade recovery = ete3 get_common_ancestor on IQ-TREE arbitrary root (ROOT-DEPENDENT); purity>=0.90 & UFBoot>=95 & SH-aLRT>=80. Re-run reproduces 3/1/1/1/1/2 of 11"),
 ("s8b_mestre_clade_structure.py", "-", "cache/fs_mestre/ava.tsv; cache/fold/mestre/*.pdb; mestre_1926_proteins.faa; mestre_usable_index.tsv", "G89 structural silhouette of published clades. Writes tables/s8b_mestre_clade_structure.tsv"),
]:
    add(s.replace(".py", ""), T + "scripts/" + s, "script", pr, inp, note)
for f, note in [("mestre_ours.faa", "window -220..+120 anchor-relative spans, 1843 [YFWH].DD carriers, headers terminal_N; unaligned. Input to ours/fftnsi/linsi (inferred: same frame)"),
                ("mestre_toro.faa", "window -197..+57, 1843 seqs, unaligned"),
                ("mestre_wide.faa", "window -260..+160, 1843 seqs, unaligned"),
                ("mestre_narrow.faa", "window -150..+80, 1843 seqs, unaligned"),
                ("mestre_tofold.faa", "1919 full-length proteins sent to ESMFold (7 of 1926 not folded); also cd-hit input for v4_and_paper/mestre_clust")]:
    add(f.replace(".faa", "") + "_faa", T + "cache/" + f, "fasta", "UNKNOWN (no script writes it; all four frame files share mtime to the ms -> one ad-hoc inline run)", "../rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_proteins.faa (inferred)", note)
models = {"fftnsi": "LG+F+R10", "linsi": "LG+F+I+R10", "narrow": "LG+F+R10", "ours": "LG+F+R10", "toro": "LG+F+R10", "wide": "LG+F+R10"}
for t in ("fftnsi", "linsi", "narrow", "ours", "toro", "wide"):
    add(f"mestre_tree_{t}_iqtree", T + f"cache/mestre_trees/{t}.iqtree", "report", "UNKNOWN - iqtree 3.1.3 run outside any surviving script/log; .log (Command: line) not kept", f"out/{t}_occ50.afa (relative path; NOT ON DISK anywhere under /home/borg)", f"IQ-TREE 3.1.3; ModelFinder BIC over {{LG,WAG,JTT,VT,Dayhoff}} (no Q.pfam despite prereg); best {models[t]}; UFBoot 1000 + SH-aLRT (label a/b)")
    add(f"mestre_tree_{t}_treefile", T + f"cache/mestre_trees/{t}.treefile", "tree", "UNKNOWN (same run as .iqtree)", f"out/{t}_occ50.afa (lost)", "1843 tips terminal_N; 1840 internal labels 'SH-aLRT/UFBoot'; unrooted (arbitrary IQ-TREE root)")
add("mestre_trees_dir", T + "cache/mestre_trees", "cache", "UNKNOWN", "-", "12 files: 6 .iqtree + 6 .treefile; no .log/.ckp/.afa/.contree/.splits")
add("fold_mestre", T + "cache/fold/mestre", "structure_dir", "scripts/s5a_fold_esmfold.py via slurm/fold_retrons.sbatch-style array on Ibex (8 tasks, logs/task_00*.log 2026-08-23); exact submission not preserved", "cache/mestre_tofold.faa", "ESMFold full-length PDBs + pLDDT summaries", None)
add("fm_mestre_span", T + "cache/fm/mestre_span", "structure_dir", "UNKNOWN (ad-hoc variant of scripts/s6g_span_pdbs.py; no script names mestre_span)", "cache/fold/mestre/*.pdb", "span-sliced PDBs (window -220..+120)")
add("fs_mestre", T + "cache/fs_mestre", "cache", "foldseek (MMseqs Version 10.941cd33) createdb/search/convertalis; command in logs/fs_mestre.log; wrapper sh only under tmp/", "cache/fm/mestre_span", "ava.tsv = all-vs-all alntmscore; 1902 structures in db.source")
add("fs_mestre_log", T + "logs/fs_mestre.log", "report", "foldseek", "cache/fm/mestre_span", "ends FS_MESTRE_DONE")
for tb, pr, note in [("s2b_mestre_clade_monophyly", "s2b_mestre_clade_monophyly.py", "byte-identical to verify_orig & verify_all"),
                     ("s2c_mestre_intruder_identity", "UNKNOWN (PROVENANCE.tsv: UNKNOWN)", ""),
                     ("s5b_E4a_ruleD_surface", "s5b_E4a_rule_D_on_mestre.py", "byte-identical to verify_orig & verify_all"),
                     ("s5d_mestre_landmark_audit", "UNKNOWN (PROVENANCE.tsv: UNKNOWN)", ""),
                     ("s5e_E4b_ruleD_our_trees", "s5e_E4b_ruleD_on_our_trees.py", "on OUR E1 trees; byte-identical to verify dirs"),
                     ("s5f_mestre_msr_msd_audit", "UNKNOWN (PROVENANCE.tsv: UNKNOWN)", ""),
                     ("s5h_mestre_unmatched_groups", "orphan; regenerated by s5h_regen_unmatched_groups.py", ""),
                     ("s5h_mestre_unmatched_groups_REGEN", "s5h_regen_unmatched_groups.py", ""),
                     ("s8b_mestre_clade_structure", "s8b_mestre_clade_structure.py", "")]:
    add("tbl_" + tb, T + f"tables/{tb}.tsv", "table", pr, "see producer", note)
add("verify_orig", T + "cache/verify_orig", "cache", "UNKNOWN (snapshot of 4 original tables before re-run)", "tables/", "s2b,s5b,s5e,s5g originals")
add("verify_all", T + "cache/verify_all", "cache", "scripts/s8f_verify_all_tables.sh", "tables/", "73 re-run tables; no s7h/s7i output (they print only)")
add("prereg_s3", T + "prereg/s3_tree_and_mestre_reconstruction.md", "report", "-", "-", "E4a/b/c. No re-inference-of-Mestre-sequences arm; E4c says 'against 10 clades, never 11' + AU test; mset includes Q.pfam; L-INS-i single alignment")
add("FINDINGS", T + "FINDINGS.md", "report", "-", "-", "G67 (s7h), G69 (s7i), G74 (6 trees; corrected RF range)")
add("MESTRE_EVIDENCE", T + "MESTRE_EVIDENCE.md", "report", "-", "-", "2026-08-20; predates all six re-inferences; no G67/G69/G74")
add("resp13", T + "responses/13_2026-08-20_mestre_msr_msd_missing_data.md", "report", "-", "-", "msr/msd missing-data; no tree re-inference")
add("resp14", T + "responses/14_2026-08-20_landmarks_mestre_audit_E4b.md", "report", "-", "-", "G52/G54 E4b; no tree re-inference")
# ---- 2. rt0_rt7_domain_test
add("s06_mestre_unit_reconciliation", R + "scripts/s06_mestre_unit_reconciliation.py", "script", "-", "MELISSA_DATA/supporting_material/Supp_material_T1_R1_systematic_prediction.csv; cache/mestre_from_V3/mestre_1926_proteins.faa; published nwk", "writes tables/mestre_unit_reconciliation|discrepant_ids|faa_duplicates + cache/mestre_usable_index.tsv")
add("s09_mestre_in_toro_frame", R + "scripts/s09_mestre_in_toro_frame.py", "script", "-", "cache/frame/mestre1926_in_toro_frame.sto; tables/rt0_rt7_frame.tsv", "writes tables/mestre_in_toro_frame_occupancy.tsv, mestre_rt0_summary.tsv")
for tb in ("mestre_clade_counts", "mestre_discrepant_ids", "mestre_faa_duplicates", "mestre_in_toro_frame_occupancy", "mestre_retron_subsystem_counts", "mestre_rt0_summary", "mestre_unit_reconciliation"):
    pr = "s09_mestre_in_toro_frame.py" if tb in ("mestre_in_toro_frame_occupancy", "mestre_rt0_summary") else ("s06_mestre_unit_reconciliation.py" if tb in ("mestre_discrepant_ids", "mestre_faa_duplicates", "mestre_unit_reconciliation") else "UNKNOWN")
    add("rt_" + tb, R + f"tables/{tb}.tsv", "table", pr, "-", "")
add("mestre_1926_proteins_faa", R + "cache/mestre_from_V3/mestre_1926_proteins.faa", "fasta", "copy of V3 mestre_scope_audit/cache/mestre_1928_proteins.faa (PROVENANCE.md)", "V3", "1926 full-length proteins; header terminal_N|terminal_N|<accession with pipes>")
add("mestre_1926_vs_RT17CORE_sto", R + "cache/mestre_from_V3/mestre_1926_vs_RT17CORE.sto", "alignment", "V3 (hmmalign to RT17_CORE HMM)", "mestre_1926_proteins.faa", "profile alignment, 2877 RF cols, no RT0 column; NOT a phylogenetic MSA")
add("mestre_from_V3_dir", R + "cache/mestre_from_V3", "cache", "copy from V3 2026-08-16", "-", "")
add("mestre_usable_index", R + "cache/mestre_usable_index.tsv", "table", "s06_mestre_unit_reconciliation.py", "Supp T1 csv + faa", "1814 accessions with clade/subsystem/msr_msd; label source for s7i")
add("mestre1926_in_toro_frame_sto", R + "cache/frame/mestre1926_in_toro_frame.sto", "alignment", "UNKNOWN (hmmalign --mapali per s09 docstring; no script writes it)", "toro742.hmm + toro_2014_Rt0-Rt7.FASTA + 1926 proteins", "2668 rows = 742 Toro + 1926 Mestre; 4203 cols; HMM-profile projection, not an MSA for ML")
add("frame_dir", R + "cache/frame", "cache", "hmmbuild (HMMER 3.4) + hmmalign", "MELISSA_DATA/supporting_material/toro_2014_Rt0-Rt7.FASTA", "")
add("nterm_dir", R + "cache/nterm", "cache", "scripts/s17_verify_trackD_extensions.py (mmseqs easy-cluster)", "mestre_1926_proteins.faa", "N-terminal extensions of Mestre proteins")
# ---- 3. stage0
add("sA_mestre_selfconsistency", S0 + "scripts/sA_mestre_selfconsistency.py", "script", "-", "published nwk + Supp T1", "writes tables/mestre_selfconsistency.tsv")
add("sA_methods_table", S0 + "scripts/sA_methods_table.py", "script", "-", "Mestre PDF text", "writes tables/mestre_methods_parameters.tsv")
add("sA_rooting_and_denominators", S0 + "scripts/sA_rooting_and_denominators.py", "script", "-", "published nwk + Supp T1", "writes tables/mestre_rooting_sensitivity.tsv; establishes MRCA statements are ROOT-DEPENDENT")
for tb, pr in (("mestre_selfconsistency", "sA_mestre_selfconsistency.py"), ("mestre_methods_parameters", "sA_methods_table.py"), ("mestre_rooting_sensitivity", "sA_rooting_and_denominators.py")):
    add("s0_" + tb, S0 + f"tables/{tb}.tsv", "table", pr, "-", "")
add("mestre_ref_faa_s0", S0 + "cache/refbuild/mestre_ref.faa", "fasta", "UNKNOWN (ad hoc; MEASUREMENTS.txt)", "per-genome protein_aminoacid.fasta", "1926 seqs identical to mestre_1926_proteins.faa (agent_v4 checked)")
add("mestre_ref_aln_s0", S0 + "cache/refbuild/mestre_ref.aln", "alignment", "MAFFT --auto (7.62 s, borg) per MEASUREMENTS.txt; exact cmd not logged", "mestre_ref.faa", "1926 x 6202 full-length, untrimmed. ungapped == faa for all 1926")
add("ref_gappyout_aln", S0 + "cache/refbuild/ref_gappyout.aln", "alignment", "trimal -gappyout per MEASUREMENTS.txt", "mestre_ref.aln", "1925 x 262 (drops 1 seq)")
add("ref_automated1_aln", S0 + "cache/refbuild/ref_automated1.aln", "alignment", "trimal -automated1", "mestre_ref.aln", "1925 x 63")
add("sub200_aln", S0 + "cache/refbuild/sub200.aln", "alignment", "UNKNOWN (200-tip subsample of gappyout)", "ref_gappyout.aln", "200 x 262 smoke")
for t, note in (("s200", "iqtree -m LG+F+R10 -bb 1000 -alrt 1000 -T 8; DID NOT FINISH (treefile is checkpoint intermediate)"), ("s200g4", "iqtree -m LG+F+G4 -T 8; finished"), ("s200r10", "iqtree -m LG+F+R10 -T 8; DID NOT FINISH")):
    add(f"{t}_treefile", S0 + f"cache/refbuild/{t}.treefile", "tree", f"iqtree 3.1.3 (Command in {t}.log)", "sub200.aln", note)
    add(f"{t}_log", S0 + f"cache/refbuild/{t}.log", "report", "iqtree 3.1.3", "sub200.aln", "")
add("refbuild_MEASUREMENTS", S0 + "cache/refbuild/MEASUREMENTS.txt", "report", "manual", "-", "")
add("refbuild_dir", S0 + "cache/refbuild", "cache", "mixed", "-", "")
add("MESTRE_ASSESSMENT", S0 + "MESTRE_ASSESSMENT.md", "report", "-", "-", "")
add("mestre_pdf_dir", S0 + "cache/mestre_pdf", "cache", "pdftotext (layout)", "Mestre 2020 PDF", "mestre2020_layout.txt")
# ---- 4.
add("mestre_clust_v4paper", A + "rt0_rt7_domain_test_v4_and_paper/cache/mestre_clust", "cache", "cd-hit V4.8.1 (retron_tradicional) -c 0.50/0.70/0.90 -n 3/4/5 -M 4000 -T 4 -d 0 (Command in c*.log); consumed by scripts/a21_g89_restricted_null.py", "v4_and_tree/cache/mestre_tofold.faa (1919)", "c5=712, c7=1556, c9=1900 clusters")
add("mestre_clusters_ledger", A + "rt0_rt7_claim_ledger/cache/mestre_clusters", "cache", "cd-hit V4.8.1 -c 0.50..0.90 -n 3/4/5/5/5 -M 4000 -T 4 -d 0 (Command in cdhit_c*.log); consumed by l05/l06", "rt0_rt7_domain_test/cache/mestre_from_V3/mestre_1926_proteins.faa (1926)", "c50=714 c60=1226 c70=1562 c80=1841 c90=1907 clusters")
for f, kind, pr, note in (("cache/mestre_ref.mafft.faa", "alignment", "scripts/p5_build_toro_profile.py (mafft --auto --anysymbol --thread 24)", "1926 x 6056 full-length"),
                          ("cache/mestre_ref.trim50.faa", "alignment", "scripts/p5_build_toro_profile.py (columns <=50% gaps)", "1926 x 310; used to build toro_recon_RT1_RT7.hmm"),
                          ("cache/pe2_mestre1928.RVT-Retrons_full_RT.tblout", "cache", "UNKNOWN (hmmsearch); read by p4_calibrate_160.py", ""),
                          ("cache/pe2_mestre1928.toro_recon_RT1_RT7.tblout", "cache", "UNKNOWN (hmmsearch); read by p4_calibrate_160.py", ""),
                          ("tables/pe2_t05_mestre_ref_scores.RVT-Retrons_full_RT.tsv", "table", "p4_calibrate_160.py", ""),
                          ("tables/pe2_t05_mestre_ref_scores.toro_recon_RT1_RT7.tsv", "table", "p4_calibrate_160.py", "")):
    add("s5adm_" + os.path.basename(f), A + "s5_admission/" + f, kind, pr, "mestre reference set (1926)", note)
add("ibex_mestre", A + "ncrna_extractor_detector_V3/cache/ibex_mestre", "cache", "rsync/scp pull from Ibex /ibex/project/c2366/RETRONS/Mestre_replication/realpipe/results (FINDINGS W34)", "Ibex realpipe over Mestre tree genomes", "PARTIAL mirror: 1925 terminal dirs, 1925 ground_truth_metadata.json + 1920 tool_integrated_results.json only; tool subdirs (padloc/defensefinder/infernal/prodigal/myrt) are EMPTY")
# ---- 5.
for f in ("experiments/X14_mestre_reconstruction.md", "experiments/X15_label_concordance.md", "experiments/X16_structural_clade_separation.md", "CLAIM_REGISTER.md", "FROZEN_DENOMINATORS.tsv", "DEBATE_QUEUE.md"):
    add("pp_" + os.path.basename(f).split(".")[0], P + f, "report" if f.endswith(".md") else "table", "-", "-", {"FROZEN_DENOMINATORS.tsv": "NO Mestre row (no 1843/1926/1928/1814 value)", "experiments/X14_mestre_reconstruction.md": "lists s2b/s5b/s5e as scripts but NOT s7h/s7i which produce G69/G74"}.get(f, ""))
for s in ("s7_classification", "crosscheck", "adversarial"):
    add(f"verdict_{s}", A + f"{s}/VERDICT.md", "report", "-", "-", "")
add("s6_v3_script", A + "s6_trees/scripts/v3_frame_aligner_rf_and_clades.py", "script", "-", "v4_and_tree/cache/mestre_trees/*.treefile", "independent re-implementation of G74 RF + clade recovery (MRCA, rooted)")
add("s6_v3_clade_recovery", A + "s6_trees/tables/v3_clade_recovery.tsv", "table", "v3_frame_aligner_rf_and_clades.py", "mestre_trees", "")
add("s6_v3_frame_aligner_rf", A + "s6_trees/tables/v3_frame_aligner_rf.tsv", "table", "v3_frame_aligner_rf_and_clades.py", "mestre_trees", "")
add("s3_t4_rf_matrix", A + "s3_object/tables/t4_rf_matrix.tsv", "table", "s3_object/scripts/v4_rf_frame_vs_aligner.py", "mestre_trees", "source of corrected 0.143-0.232")
add("s3_t7_iqtree_commands", A + "s3_object/tables/t7_iqtree_commands.tsv", "table", "s3_object/scripts/v7_prereg_vs_execution.py", ".iqtree/.log files", "command column EMPTY for all six mestre_trees -> no surviving command line")
add("s4_rv1b_g74_ratio", A + "s4_motifs/tables/rv1b_g74_ratio.tsv", "table", "s4_motifs/scripts/rv1b_g74_ratio.py", "s3_object/tables/t4_rf_matrix.tsv", "ratio 1.702/1.473/1.392")
add("ext_RETRONS_jan2026_aligned", "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/reference_RTs_aligned.fasta", "alignment", "UNKNOWN (phylogenetic_analysis.ipynb reads it; no mafft cmd found)", "reference_RTs_raw.fasta", "OUTSIDE V4: 1926 x 6037 in-house full-length alignment of Mestre set (Mar 2026)")
add("published_nwk", V + "MELISSA_DATA/supporting_material/Supplementary_mestre_Tree.nwk", "tree", "Mestre et al. 2020 Supplementary File S1", "-", "1928 tips; ONE support value per node; the only Mestre-published phylogenetic artefact on disk")
w = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
w.writerow(["asset_id", "path", "kind", "sha256", "bytes", "mtime", "producer", "inputs", "n_records", "notes"])
for r in rows: w.writerow(r)
