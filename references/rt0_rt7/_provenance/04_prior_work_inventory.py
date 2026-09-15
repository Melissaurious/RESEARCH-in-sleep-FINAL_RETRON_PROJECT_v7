#!/usr/bin/env python3
"""Stage-2 prep step 4: inventory prior RT0-RT7 work. INVENTORY ONLY.

Nothing here is copied, modified or executed. Large derived datasets are
recorded at directory granularity with counts, not enumerated file-by-file and
not copied (task §7).
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
REF = PROJ / "references/rt0_rt7"
V4 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4")
V5 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V5")

# (path, artifact_type, description, potential_reuse, provenance_status, notes)
ROWS: list[tuple] = [
 ("/home/borg/RETRON_STAGES/02_rt0_rt7_definition.md", "stage_brief",
  "The canonical Stage-2 brief: states the task, the autonomy envelope and a 2026-09-12 correction retracting a mis-attributed Toro 2026 claim about retrons lacking RT0.",
  "REUSE_REFERENCE", "VERIFIED_IDENTICAL_ACROSS_4_COPIES",
  "sha256 03714cba6d426bcf... identical at all 4 discovered paths (RETRON_STAGES, RESEARCH-in-sleep-GENERAL/RETRON_STAGES, v7/general/RETRON_STAGES, v7/idea-stage/programme). NOT modified, NOT executed. The in-project copy at general/RETRON_STAGES is governance-pinned."),
 (str(V4 / "25_august_paper_positioning/WHAT_RT0_RT7_IS.md"), "prior_analysis_doc",
  "A prior session's statement of what RT0-RT7 is taken to mean.",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Prior-session prose; no .prov.json. Hypothesis source only - must not be treated as the operational definition."),
 (str(V4 / "25_august_paper_positioning/experiments/X00_rt0_rt7_domain_derivation.md"), "prior_experiment_design",
  "Prior experiment design for deriving the RT0-RT7 domain boundaries.",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Design intent, not a result. Useful as a candidate method and for known failure modes."),
 (str(V4 / "launchers/LAUNCHER_rt0_rt7_domain_test_v2.md"), "prior_launcher",
  "Prior launcher for the RT0-RT7 domain test (27.9 kB).",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Records the prior task's declared gates and scope; read for method and failure modes."),
 (str(V4 / "launchers/LAUNCHER_rt0_rt7_domain_test_v2_PRIOR_RESULTS.md"), "prior_launcher_results_annex",
  "Prior-results annex to the v2 launcher (16.3 kB).",
  "REVERIFY_RESULT", "UNRESOLVED_PROVENANCE",
  "Contains prior numeric results. Every number is RE-DERIVE; none may be carried forward without recomputation."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_domain_test"), "prior_result_tree",
  "First RT0-RT7 domain test: 24 scripts, 78 tables, 14 docs, 10 figures. Includes s07_frame_blocks_and_anchors.py, s08_rt0_occupancy_by_class.py, s19_a9_offsets_and_extension_domains.py.",
  "REUSE_CODE", "UNRESOLVED_PROVENANCE",
  "0 .prov.json in this tree. Scripts are the reusable part; tables are REVERIFY_RESULT. NOT copied into the project (task S7: do not copy large derived datasets)."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_domain_test_v2"), "prior_result_tree",
  "Second iteration: 18 scripts, 21 tables, 19 docs. Includes scripts/s2_block_extents.py and instrument/make_core_block.py.",
  "REUSE_CODE", "UNRESOLVED_PROVENANCE",
  "0 .prov.json. s2_block_extents.py and make_core_block.py are the most directly relevant boundary-defining code found. Not copied."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_domain_test_v3"), "prior_result_tree",
  "Third iteration: 23 scripts, 75 tables, 16 docs, 5 figures. Includes s13a_subdomain_placement.py and s9b_block_atlas.py.",
  "REUSE_CODE", "UNRESOLVED_PROVENANCE",
  "0 .prov.json. s13a_subdomain_placement.py is directly on the subdomain-placement question. Not copied."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree"), "prior_result_tree",
  "Largest prior tree: 64 scripts, 179 tables, 47 docs. Includes g0c_rederive_tipset.py and s4i_E1_window_occupancy_sweep.py; also the FoldMason structural-MSA arm (s6g/s7a/s7f).",
  "REUSE_CODE", "UNRESOLVED_PROVENANCE",
  "0 .prov.json. Contains the structural arm whose known failure mode is documented in stage 0c: 2,225-residue proteins were aligned against 66-residue spans. Not copied."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_paper"), "prior_result_tree",
  "Paper-facing iteration: 23 scripts, 23 tables, 46 docs. Includes LITERATURE_INDEX.md and FINDINGS.md.",
  "REVERIFY_RESULT", "UNRESOLVED_PROVENANCE",
  "0 .prov.json. Source of two inherited Toro 2026 positioning judgments registered UNPROVEN in the V5 wiki. Prose and numbers both require re-derivation."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_claim_ledger"), "prior_claim_ledger",
  "Prior claim ledger for the RT0-RT7 work: 6 scripts, 6 tables, 14 docs.",
  "REVERIFY_RESULT", "UNRESOLVED_PROVENANCE",
  "0 .prov.json. Useful as a list of what was previously claimed, so Stage 2 can state which claims it is re-testing. Not authority."),
 (str(V4 / "ARIS_OUTPUT/rt0_rt7_lit_and_narrative"), "prior_literature_notes",
  "Literature and narrative notes: 34 documents, no scripts or tables.",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Prose only. Includes INSIGHTS_PER_PAPER.md, PAPERS_READ.md, PRIOR_ART.md, VERIFICATION_LOG.md. Reading list value; no numeric authority."),
 ("/home/borg/research-wClaude-PART1_documents/RT0-RT7_theory.txt", "prior_theory_doc",
  "Free-text RT0-RT7 theory document (45.9 kB).",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Outside any project tree; no provenance record and no stated author or date. Hypothesis source only."),
 ("/home/borg/research-wClaude-PART1_documents/RT0-RT7_BRIEFING.md", "prior_theory_doc",
  "RT0-RT7 briefing document (25.0 kB).",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Outside any project tree; no provenance record. Hypothesis source only."),
 ("/home/borg/research-wClaude-PART1_documents/RT0-RT7_theory_ADDENDUM_SPIRE.tex", "prior_theory_doc",
  "LaTeX addendum relating the RT0-RT7 theory document to SPIRE/Toro 2026 (7.2 kB).",
  "REUSE_REFERENCE", "UNRESOLVED_PROVENANCE",
  "Outside any project tree; no provenance record. Given the Stage-2 brief's 2026-09-12 correction of a mis-attributed Toro 2026 RT0 claim, any Toro-related assertion here needs checking at the PDF before reuse."),
 (str(V5 / "research-wiki/claims"), "structured_claim_records",
  "V5 stage-0c claim nodes for the Tier-1 papers: poch-1989-four-conserved-motifs, xiong-eickbush-rt-tree-82-retroelements, zimmerly2001-rt-subdomains, simon-zimmerly-rt-groupings.",
  "REUSE_REFERENCE", "PROVENANCED_BUT_UNPROVEN",
  "Each carries statement/scope/instrument/lineage and status=unproven, with verbatim anchors re-verified against the PDFs. Usable as a structured reading of the Tier-1 sources; NOT usable as established fact - all are UNPROVEN by design."),
 (str(V5 / "research-wiki/papers"), "structured_paper_records",
  "V5 stage-0c paper pages for the Tier-1 papers plus blocker1999_domain_structure_threedimensional.md.",
  "REUSE_REFERENCE", "PROVENANCED_WITH_KNOWN_METADATA_DEFECT",
  "KNOWN DEFECT, recorded honestly: two page slugs carry wrong years from a heuristic year extractor - xiong1985_... is the 1990 paper and blocker1999_... is the 2005 paper. Page bodies name the extraction method and flag non-filename years as not authoritative. Use the PDFs in references/rt0_rt7/literature/ for citation, not these slugs."),
 (str(PROJ / "references/rt0_rt7/literature/Blocker_et_al_2005_RNA_group_II_intron_RT_domain_structure_3D_model.pdf"),
  "retained_tier1_structural_literature",
  "Blocker FJH, Mohr G, Conlan LH, Qi L, Belfort M, Lambowitz AM 2005, RNA 11(1):14-28. Domain structure and 3D model of a group II intron-encoded RT.",
  "REUSE_REFERENCE", "RETAINED_IN_RESOURCE_REGISTER",
  "RESOLVED by operator amendment 2026-09-15: previously FOUND_NOT_RETAINED, now copied into references/rt0_rt7/literature/ and registered as evidence_tier=TIER1_STRUCTURAL with allowed_to_seed_rt07_definition=NO. See RESOURCE_REGISTER.tsv asset_id lit_blocker2005_structural. Role is independent structural interpretation/validation, not definition of the historical sequence frame."),
]


def main() -> int:
    cols = ["path", "artifact_type", "description", "potential_reuse",
            "provenance_status", "notes"]
    rows = []
    for path, atype, desc, reuse, prov, notes in ROWS:
        p = Path(path)
        exists = p.exists()
        extra = "" if exists else "  [PATH NOT FOUND AT INVENTORY TIME]"
        rows.append({"path": path, "artifact_type": atype, "description": desc,
                     "potential_reuse": reuse, "provenance_status": prov,
                     "notes": notes + extra})
    with (REF / "PRIOR_WORK_INVENTORY.tsv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t",
                           quoting=csv.QUOTE_NONE, escapechar="\\")
        w.writeheader()
        for r in rows:
            w.writerow({k: str(r[k]).replace("\t", " ").replace("\n", " ") for k in cols})
    miss = [r["path"] for r in rows if "[PATH NOT FOUND" in r["notes"]]
    hist: dict[str, int] = {}
    for r in rows:
        hist[r["potential_reuse"]] = hist.get(r["potential_reuse"], 0) + 1
    print(f"PRIOR_WORK_INVENTORY rows: {len(rows)}")
    for k, v in sorted(hist.items()):
        print(f"  {k:<26} {v}")
    print(f"paths not found: {len(miss)}")
    for m in miss:
        print("   ", m)
    print("nothing in this inventory was copied, modified or executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
