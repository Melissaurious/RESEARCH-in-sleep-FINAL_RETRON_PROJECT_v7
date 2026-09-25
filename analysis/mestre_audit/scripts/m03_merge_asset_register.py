#!/usr/bin/env python3
"""Merge the three M1 sub-audit asset tables into one register and attach
(a) the cross-root identity group (from CROSS_ROOT_IDENTITY.tsv, by sha256) so duplicate
paths are visibly one piece of evidence, and (b) a reuse grade from ORDERED, declared rules.
The first matching rule wins; an asset matching no rule is UNGRADED (= DO-NOT-USE, WA-L.3).
"""
import csv, re, sys
AUD = "ARIS_OUTPUT/mestre_audit"
SRC = [("V4", f"{AUD}/agent_v4/v4_assets.tsv"), ("V2_V3_V5_D2", f"{AUD}/agent_v235/v235_assets.tsv"),
       ("RETRON_DB", f"{AUD}/agent_retrondb/retrondb_assets.tsv")]
# (regex on path, kind-regex, grade, decision) — order matters.
RULES = [
    (r"RETRON_CLAUDE_PART1/supplementary_material", r".", "RED", "PATH GONE — use the sha256-identical copy in v7 MELISSA_DATA/supplementary_material"),
    (r"/ibex/project/c2366/RETRONS/rt0_rt7_domain_test_v4_and_tree/mestre", r".", "AMBER", "AUDITED over SSH 2026-09-19 (job 52089162): V4 re-inference inputs, IBEX_ONLY; comparator only (91 substitutes); see ibex_audit/results"),
    (r"/ibex/", r".", "AMBER", "AUDITED over SSH 2026-09-19 (jobs 52089161-3); per-file identity in ibex_audit/results/*/IBEX_VS_BORG.tsv.gz; no Mestre RT0-RT7 material"),
    (r"(Supplementary_mestre_Tree\.nwk|Supp_material_T1_R1|supp_material_systematic_prediction_paper|Mestre_supplementary_material\.csv|Suppl_Toro_Tree|toro_2014_Rt0-Rt7)", r".", "GREEN", "RAW published input; one content per identity group — never count copies as independent"),
    (r"(Mestre2020_retron\.txt|mestre2020_layout|paper_pmc_fulltext|paper_pdf_layout|p4_mestre_systematic|mestre2020\.txt)", r".", "GREEN", "paper text; 2 distinct renderings only"),
    (r"Mestre_sequences/.*(protein_aminoacid|manifest)", r".", "AMBER", "our download; exclude the 112 rescued substitutes (incl. 15 RNA-polymerase subunits) and 2 absent terminals"),
    (r"Mestre_sequences", r".", "AMBER", "download provenance; rescue logic reconstructed from logs only (script on Ibex)"),
    (r"stage1_mestre_replication_and_insights/(tables|BLIND)", r".", "GREEN", "FROZEN retron-db 76ad2af; M1 rerun reproduced 18/18 tables byte-for-byte after declared root-A remap"),
    (r"stage1_mestre_replication_and_insights/scripts", r".", "GREEN", "reusable code; s00 vacuous-pass on missing root must be guarded before reuse"),
    (r"stage1_mestre_replication_and_insights/env\.lock", r".", "RED", "exports conda base, not the executing env"),
    (r"stage1_mestre_replication_and_insights/PROVENANCE", r".", "AMBER", "stale: identical to discarded first assembly"),
    (r"discarded_bundle_assembly1", r".", "RED", "discarded pre-review assembly"),
    (r"reference_msa_v1|stage3_placement_toolkit/(cache|data)", r".", "AMBER", "full-length mafft --auto alignment of 1926 incl. 112 substitutes; rebuild without substitutes, RT0-7 cut"),
    (r"stage3_placement_toolkit", r".", "AMBER", "tooling reference for M2 (place.py design); smoke only"),
    (r"mestre_trees(/|$)", r".", "AMBER", "COMPARATOR ONLY: 1843 tips incl. 91 substitutes (3 RNAP); input alignments lost (4/6 rebuilt); support-based '<=3/11'"),
    (r"reconstructed_alignments", r".", "AMBER", "M1 rebuild of V4 inputs; comparator only"),
    (r"(refbuild/mestre_ref\.aln|mestre_ref\.trim50|mestre_ref\.mafft|mestre_1926|mestre_1928|mestre_(wide|narrow|ours|toro|tofold)\.faa)", r".", "RED", "as reference: contains the rescued substitutes; producer/params partial"),
    (r"fs_mestre(/|$|\.log)", r".", "RED", "foldseek shards: no recorded command/version (consistent with prior-asset-audit)"),
    (r"fold/mestre", r".", "AMBER", "ESMFold structures, named ids without hash check; 112 are substitutes"),
    (r"stock_verdicts", r".", "AMBER", "1925 rows; denominator 1920 integrated, not 537; tool agreement is not independent (Mestre-authored CMs)"),
    (r"R1_mestre_validation_FULL_quarantined", r".", "RED", "string-match columns, not tool calls; row wrapping"),
    (r"(R2_mestre_validation_CLEAN|REPAIRED_summary)", r".", "AMBER", "use REPAIRED_summary; R2 has wrapped rows"),
    (r"(padlocdb\.cm|cm_meta|retron_.*\.yaml|defense-finder|\.hmm$)", r".", "GREEN", "detector model; descends from Mestre — cannot corroborate Mestre"),
    (r"stage0_positioning/cache/refbuild", r".", "RED", "V4 stage0 pilot (200-taxon subsample trees, trimmed alns) incl. substitutes; not a reference"),
    (r"mestre_from_V3|cache/frame|cache/nterm|fm/mestre_span", r".", "RED", "derived from the 1926 set incl. substitutes; frame/profile provenance partial"),
    (r"verify_(orig|all)", r".", "AMBER", "prior self-verification copies; comparator only"),
    (r"\.(treefile|iqtree|nwk|tre)$", r".", "AMBER", "prior tree; comparator only"),
    (r"\.(aln|afa|sto|faa|fasta|fa)$", r".", "RED", "prior sequence set/alignment; rebuild from graded inputs"),
    (r"\.(log|json|clstr)$|mestre\.c[0-9]+$|mestre_clust", r".", "AMBER", "prior run log / clustering; record-only"),
    (r"\.(py|sh)$", r".", "REFERENCE", "prior code: read for method, re-implement; never evidence"),
    (r"\.(md|txt)$", r".", "CLAIM-ONLY", "prose; claims must be re-derived before citation"),
    (r"\.(tsv|csv)$", r".", "AMBER", "prior table; re-derive before use"),
]
ident = {}
for r in csv.DictReader(open("analysis/mestre_audit/CROSS_ROOT_IDENTITY.tsv"), delimiter="\t"):
    ident[r["sha256"]] = (r["identity_group"], r["group_size"])
out = csv.writer(open(sys.argv[1], "w", newline=""), delimiter="\t", lineterminator="\n")
cols = ["asset_id", "audit_scope", "path", "kind", "sha256", "bytes", "mtime", "producer", "inputs", "n_records",
        "identity_group", "identity_group_size", "reuse_grade", "reuse_decision", "notes"]
out.writerow(cols)
n = {}
for scope, f in SRC:
    for r in csv.DictReader(open(f), delimiter="\t"):
        g, gs = ident.get(r["sha256"], ("", ""))
        grade, dec = "UNGRADED", "DO-NOT-USE until graded (WA-L.3)"
        for pat, kpat, gr, d in RULES:
            if re.search(pat, r["path"]) and re.search(kpat, r["kind"] or "."):
                grade, dec = gr, d; break
        n[grade] = n.get(grade, 0) + 1
        out.writerow([f"{scope}:{r['asset_id']}", scope, r["path"], r["kind"], r["sha256"], r["bytes"], r["mtime"],
                      r["producer"], r["inputs"], r["n_records"], g, gs, grade, dec, r["notes"]])
print(n, file=sys.stderr)
