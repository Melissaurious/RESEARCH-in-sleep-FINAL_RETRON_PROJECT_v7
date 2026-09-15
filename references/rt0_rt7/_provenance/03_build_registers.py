#!/usr/bin/env python3
"""Stage-2 prep step 3: build RESOURCE_REGISTER.tsv, finalise SOURCE_AUDIT.tsv,
build PRIOR_WORK_INVENTORY.tsv, and validate all of it.

Validation (task §8): recompute sha256 for every retained asset, verify every
project_path exists, verify byte counts, verify no source original changed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
REF = PROJ / "references/rt0_rt7"
SEL = json.loads((REF / "_provenance/selection.json").read_text(encoding="utf-8"))
DISC = json.loads((REF / "_provenance/discovery.json").read_text(encoding="utf-8"))

# asset_id -> (citation_or_source, year, tier, asset_type, scientific_role, may_seed, notes)
M: dict[str, tuple] = {
 "lit_poch1989": (
  "Poch O, Sauvaget I, Delarue M, Tordo N. Identification of four conserved motifs among the RNA-dependent polymerase encoding elements. EMBO J 8(12):3867-3874",
  "1989", "TIER1", "pdf_primary_literature",
  "Derivational primary evidence: motif-level definition of the RNA-dependent polymerase core.",
  "YES",
  "PROVIDES: motif evidence (81 'motif' mentions; 34 'motif A-F' labels), consensus blocks (8), alignment discussion (11), 2 explicit residue-coordinate spans. DOES NOT PROVIDE: the literal token 'RT0' (0 occurrences), RT1-RT7 numbering (0), subdomain numbering (0). Terminology is motif A-F, not RT0-RT7."),
 "lit_xiong1990": (
  "Xiong Y, Eickbush TH. Origin and evolution of retroelements based upon their reverse transcriptase sequences. EMBO J 9(10):3353-3362",
  "1990", "TIER1", "pdf_primary_literature",
  "Derivational primary evidence: the founding RT alignment/phylogeny frame over 82 retroelements.",
  "YES",
  "PROVIDES: alignment blocks (27 'alignment' mentions), YXDD-class motif anchors (23), cross-element transferability statements (11). DOES NOT PROVIDE: literal 'RT0' (0), RT1-RT7 numbering (0), subdomain numbering (0), explicit residue boundaries for named blocks."),
 "lit_zimmerly2001": (
  "Zimmerly S, Hausner G, Wu X. Phylogenetic relationships among group II intron ORFs. Nucleic Acids Res 29(5):1238-1250",
  "2001", "TIER1", "pdf_primary_literature",
  "Derivational primary evidence: the only retained Tier-1 source that numbers RT subdomains and names domain 0.",
  "YES",
  "PROVIDES: subdomain numbering ('subdomains 1-7', 1 occurrence; 'subdomain/domain 0', 4), verbatim 'Subdomain 0 can be considered an N-terminal extension of the RT domain and is conserved among non-LTR RTs', palm/finger terminology (3), YXDD (13), consensus blocks (18), 2 alignment figures. DOES NOT PROVIDE: the literal token 'RT0' (0 occurrences) or the composite 'RT0-RT7' spelling. NOTE: the single 'RT1' regex hit is the gene name C.e.RT1, not a subdomain label."),
 "lit_simon2008": (
  "Simon DM, Zimmerly S. A diversity of uncharacterized reverse transcriptases in bacteria. Nucleic Acids Res 36(22):7219-7229",
  "2008", "TIER1", "pdf_primary_literature",
  "Derivational primary evidence: bacterial RT class census and the terminology carried into later bacterial RT work.",
  "YES",
  "PROVIDES: terminology and class scope, alignment discussion (12), cross-class transferability statements (5), palm/finger terminology (2). DOES NOT PROVIDE: literal 'RT0' (0), RT1-RT7 numbering (0), subdomain numbering (0), explicit boundaries."),
 "lit_blocker2005_structural": (
  "Blocker FJH, Mohr G, Conlan LH, Qi L, Belfort M, Lambowitz AM. Domain structure and three-dimensional model of a group II intron-encoded reverse transcriptase. RNA 11(1):14-28, doi:10.1261/rna.7181105",
  "2005", "TIER1_STRUCTURAL", "pdf_primary_literature",
  "Structural primary evidence. Role: INDEPENDENT STRUCTURAL INTERPRETATION / VALIDATION and later structural-domain work. NOT evidence for defining the historical SEQUENCE RT0-RT7 frame.",
  "NO",
  "Added by operator amendment 2026-09-15. Deliberately NOT allowed to seed the sequence frame even though it is primary and Tier-1-grade: its contribution is a 3D model and domain architecture, and it is the one retained paper that already uses the modern block spelling, so seeding from it would import the convention being audited. STRING CENSUS (factual): literal 'RT0' 14 occurrences; 'RT1'-'RT7' tokens 38; one 'RT0-RT7' composite; 'RT1 to 7' range 1; 'domain X' 28; fingers/palm/thumb 82; 'subdomain 0' 0 (it writes 'motif RT0' rather than Zimmerly's 'subdomain 0')."),
 "hist_toro2014_rt0rt7_fasta": (
  "Toro N, Nisa-Martinez R. Comprehensive Phylogenetic Analysis of Bacterial Reverse Transcriptases. PLoS ONE (supplementary sequence set, RT0-RT7 blocks)",
  "2014", "TIER2", "fasta_sequence_set",
  "Published comparator: an existing RT0-RT7 block sequence set to TEST an independently reconstructed frame against.",
  "NO",
  "Comparator only. Carries the inherited RT0-RT7 convention, so seeding a definition from it would make the reconstruction agree with the convention by construction."),
 "hist_toro2014_tableS1": (
  "Toro N, Nisa-Martinez R 2014, Table S1 (supplementary table)",
  "2014", "TIER2", "xlsx_supplementary_table",
  "Published comparator: supplementary table accompanying the same 2014 RT analysis.",
  "NO",
  "DISCOVERED BY THIS SWEEP; was not previously in the project. Comparator only. Contents not parsed in this task."),
 "mestre_tree_nwk": (
  "Mestre MR, Gonzalez-Delgado A, Gutierrez-Rus LI, Martinez-Abarca F, Toro N. Systematic prediction of genes functionally associated with bacterial retrons. Nucleic Acids Res 48:12632-12650 (supplementary tree)",
  "2020", "TIER2", "newick_reference_tree",
  "Published comparator: the reference retron RT phylogeny widely reused downstream.",
  "NO", "Comparator only."),
 "mestre_supp_sanitised_a": (
  "Mestre et al. 2020 supplementary table - header-sanitised variant A",
  "2020", "TIER2", "csv_supplementary_table",
  "Published comparator: retron/clade/subtype assignment table.",
  "NO",
  "NOT byte-identical to the other two Mestre CSVs: this is a header-SANITISED derivative (headers 'Node,RT_Clade,Retron_subtype,...'). Prefer mestre_supp_original_headers for anything provenance-bearing."),
 "mestre_supp_sanitised_b": (
  "Mestre et al. 2020 supplementary table - header-sanitised variant B",
  "2020", "TIER2", "csv_supplementary_table",
  "Published comparator: retron/clade/subsystem assignment table.",
  "NO",
  "NOT byte-identical to the other two Mestre CSVs: header-SANITISED derivative (headers 'Node,Clade,Retron_subsystem,...'). Column NAMES differ from variant A ('Clade' vs 'RT_Clade', 'Retron_subsystem' vs 'Retron_subtype'); do not join the three on header name."),
 "mestre_supp_original_headers": (
  "Mestre et al. 2020 supplementary table - original published headers",
  "2020", "TIER2", "csv_supplementary_table",
  "Published comparator: the closest-to-published form of the Mestre supplementary table.",
  "NO",
  "DISCOVERED BY THIS SWEEP. Retains the published header footnote markers ('Nodea,RT/Cladea,Retron (sub)b,...'), so this is the least-derived of the three Mestre CSVs. The other two are sanitised derivatives of the same table."),
 "myrt_rvt_ref_hmm": (
  "Sharifi F, Ye Y. myRT reference package (RVT-ref.hmm). Nucleic Acids Res 50(5):e29",
  "2022", "TIER2", "hmm_profile",
  "Published comparator: myRT reference RT profile.",
  "NO",
  "AMBIGUOUS PROVENANCE: this file is NOT listed in the refpkg's own CONTENTS.json manifest, so it carries no published checksum to verify against. Comparator only."),
 "myrt_suppl_toro_tree": (
  "Toro et al., supplementary tree distributed alongside the myRT reference material",
  "unknown", "TIER2", "newick_reference_tree",
  "Published comparator: supplementary RT tree.",
  "NO",
  "MISFILED in the existing layout: the filename attributes this to Toro, not myRT, but it sits under myrt/. Left in place rather than silently reorganised. Year not established from the file itself."),
 "myrt_refpkg_contents": (
  "myRT-FastTree2.refpkg CONTENTS.json (package manifest, author 'fsharifi', create_date 2021-06-09)",
  "2021", "TIER2", "json_manifest",
  "Provenance manifest for the myRT reference package; the checksum authority for it.",
  "NO",
  "The manifest covers only 4 of the 7 refpkg payload files. 3 of those 4 FAIL their recorded md5 (see refpkg asset notes)."),
 "myrt_refpkg_mapping": (
  "myRT-FastTree2.refpkg Mapping",
  "2021", "TIER2", "mapping_table",
  "Published comparator: myRT reference sequence/taxon mapping table.",
  "NO", "Not covered by the refpkg manifest; no published checksum available."),
 "myrt_refpkg_phylomodel": (
  "myRT-FastTree2.refpkg phylo_modeldyadg_ia.json",
  "2021", "TIER2", "json_phylo_model",
  "Published comparator: the phylogenetic model shipped with the myRT reference tree.",
  "NO", "The ONLY refpkg file whose md5 MATCHES the manifest."),
 "myrt_rvt_ref_fst": (
  "myRT-FastTree2.refpkg RVT-ref.fst (reference alignment, FASTA)",
  "2021", "TIER2", "alignment_fasta",
  "Published comparator: myRT reference RT ALIGNMENT. A candidate comparator alignment for block-occupancy testing.",
  "NO",
  "DISCOVERED BY THIS SWEEP. md5 MISMATCH vs the refpkg manifest (manifest 925131942f89283b0df7d6340e2ee1e5, actual 97ea389857c52b5367a59d48896244a8); not explained by CRLF/LF or trailing-newline normalisation. Treat as myRT-derived but NOT manifest-verified."),
 "myrt_rvt_ref_sto": (
  "myRT-FastTree2.refpkg RVT-ref.sto (reference alignment, Stockholm)",
  "2021", "TIER2", "alignment_stockholm",
  "Published comparator: myRT reference RT alignment in Stockholm form.",
  "NO",
  "DISCOVERED BY THIS SWEEP. Not covered by the refpkg manifest at all; no published checksum available."),
 "myrt_rvt_ref_tre": (
  "myRT-FastTree2.refpkg RVT-ref.tre (reference tree)",
  "2021", "TIER2", "newick_reference_tree",
  "Published comparator: myRT reference RT tree.",
  "NO",
  "DISCOVERED BY THIS SWEEP. md5 MISMATCH vs the refpkg manifest (manifest 63da9234e67d02e8bfbd365c64d70afb, actual d40ebda92b198ca3d326f2f16e805d74). Treat as myRT-derived but NOT manifest-verified."),
 "myrt_rvt_ref_log": (
  "myRT-FastTree2.refpkg RVT-ref.log (FastTree run log / tree_stats)",
  "2021", "TIER2", "run_log",
  "Generation evidence: records the FastTreeMP invocation that produced the myRT reference tree.",
  "NO",
  "DISCOVERED BY THIS SWEEP. md5 MISMATCH vs the refpkg manifest (manifest 8a6284d3f90a71ffac3e6ca2ef952462, actual 9fad8b74c381f1c819c980df0f5a3b28). First line records 'Command: /home/fsharifi/Apps/FastTreeMP -log June8-phy.log ...', consistent with the manifest author string 'fsharifi'."),
 "myrt_buildrvt_sh": (
  "myRT Models/HMM/buildRVT.sh (model build script shipped with the myRT distribution)",
  "unknown", "TIER2", "build_script",
  "Generation evidence: documents, in the authors' own words, how the myRT RVT_1 class models were built.",
  "NO",
  "DISCOVERED BY THIS SWEEP, from a myRT source checkout at /home/borg/RETRONS_january_2026/the-retron-project/src/myRT. Comment-only script (steps are commented out); documents the intended build procedure, it is not a runnable pipeline as shipped."),
 "toro2026_epang_newick": (
  "Toro N. Landscape of retron diversity across the SPIRE prokaryotic metagenome resource. bioRxiv 2026.05.14.725207 (EPA-ng reference phylogeny)",
  "2026", "TIER2", "newick_reference_tree",
  "Published comparator: the reference phylogeny Toro 2026 places candidates against.",
  "NO", "PREPRINT, not peer reviewed. Comparator only."),
 "toro2026_type_hmms_tgz": (
  "Toro 2026, SPIRE retron type-specific HMMs (Zenodo archive)",
  "2026", "TIER2", "tar_gz_archive_of_hmms",
  "Published comparator: per-type retron HMMs plus their calibration thresholds.",
  "NO",
  "Archive listed non-destructively: 32 entries = 1 directory + 30 .hmm + calibration_thresholds.tsv (876 B). Listing kept at _provenance/archive_listing_spire_hmms.txt. NOT extracted into the project. PREPRINT source."),
 "toro2026_typexi_contree": (
  "Toro 2026, type XI local tree (IQ-TREE .contree)",
  "2026", "TIER2", "newick_consensus_tree",
  "Published comparator: local consensus tree for the candidate type XI-like lineages.",
  "NO", "PREPRINT, not peer reviewed. Comparator only."),
 "toro2026_pipeline_scripts_zip": (
  "Toro 2026, SPIRE retron mining pipeline scripts",
  "2026", "TIER2", "zip_archive_of_scripts",
  "Generation evidence: documents how the Toro 2026 reference classification was produced.",
  "NO",
  "DISCOVERED BY THIS SWEEP. Listed non-destructively: 12 entries (8 scripts, README.md, requirements.txt, LICENSE.txt). Listing kept at _provenance/archive_listing_spire_scripts.txt. NOT extracted. Renamed on copy from 'SPIRE_retron_pipeline_scripts (1).zip' to drop the ' (1)' download suffix; content byte-identical (sha256 recorded)."),
}

TIER1_EXPECTED = ["lit_poch1989", "lit_xiong1990", "lit_zimmerly2001", "lit_simon2008"]

# Assets that are NOT present locally but are load-bearing enough to be registered
# rather than merely mentioned. project_path is NOT_ACQUIRED by construction.
# asset_id -> (citation, year, tier, asset_type, role, may_seed, prov_status, notes)
MISSING: dict[str, tuple] = {
 "zimmerly2001_align_000044": (
  "Zimmerly S, Hausner G, Wu X 2001, group II intron ORF amino-acid alignment submitted to EMBL, accession ALIGN_000044",
  "2001", "TIER1_MISSING_EXTERNAL", "alignment_external_accession",
  "HIGH VALUE. The primary-source alignment underlying the only Tier-1 paper that numbers RT subdomains. Would let the historical frame be read off the authors' own alignment columns instead of inferred from the printed figures.",
  "YES",
  "MISSING_NOT_ACQUIRED",
  "Cited verbatim on the paper's front page as 'DDBJ/EMBL/GenBank accession no. ALIGN_000044' and in the body as 'the alignment has been submitted to the EMBL database (accession number ALIGN_000044)'. NOT present anywhere under /home/borg and NOT downloaded during reference assembly, per the operator instruction in force at that time. STATUS CHANGE 2026-09-15: governed acquisition is now APPROVED by docs/decisions/2026-09-15_stage2_operator_decisions.md section A, to be performed during rt07_g1_history_and_definition and IDEALLY BEFORE rt07_g2_reference_reconstruction. This row stays MISSING_NOT_ACQUIRED until an acquisition row exists in results/rt07_g1_history_and_definition/; acquired bytes land in data/derived/rt07_external_assets/ and are NEVER written into references/rt0_rt7/. If the accession is unavailable, inaccessible or ambiguous, MISSING_PRIMARY_ASSET is landed and no substitute is invented. ALIGN_* is a legacy EMBL alignment accession space."),
}

# Assets that ARE on disk but OUTSIDE this project tree and are deliberately NOT copied in.
# Registered by identity - source path, sha256, byte count - so that a measurement taken on
# one is checkable without duplicating a large binary into the project (CLAUDE.md: large
# canonical data stay in place, read-only). project_path is NOT_COPIED_EXTERNAL by
# construction, and these files were not part of the content-based sweep, so they have no
# SOURCE_AUDIT row.
# asset_id -> (external_path, citation, year, tier, asset_type, role, may_seed, prov_status, notes)
EXTERNAL: dict[str, tuple] = {
 "myrt_rvt_all_hmm_external": (
  "/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/HMM/RVT-All.hmm",
  "Sharifi F, Ye Y. myRT: the myRT distribution's combined RT model set (RVT-All.hmm). Nucleic Acids Res 50(5):e29",
  "2022", "TIER2", "hmm_profile_set",
  "Published comparator AND the provenance basis for one correction: this is the file on which the myRT model count was measured. Comparator / provenance evidence only.",
  "NO",
  "PROVENANCE_IDENTIFIED_EXTERNAL_COPY_NOT_RETAINED",
  "REGISTERED 2026-09-15 to close a provenance gap: launcher section 5b and docs/decisions/2026-09-15_stage2_prior_dossier_audit.md section F correct the prior dossier's myRT counts (roughly 2,051 seeds over 47 families) using a measurement taken on THIS file, which was not previously a register row. MEASURED 2026-09-15 on the path recorded here: 45 models (grep -c '^NAME') and 1,988 summed NSEQ (awk over '^NSEQ'), matching the myRT publication's own statement of 45 HMM models for 41 RT classes built from 1,988 RVT_1 sequences. NO PUBLISHED CHECKSUM EXISTS for this file and none is invented: the myRT refpkg CONTENTS.json manifest does not list it. Identity is therefore source-path plus observed sha256 only. NOT COPIED into references/rt0_rt7/ (3.9 MB, and the project convention is to leave large canonical data in place); it lives outside this project and outside its read-only guarantee, so any later use re-verifies the sha256 recorded here. NOT part of the content-based discovery sweep, so it has no SOURCE_AUDIT row. TIER2: comparator only, and MUST NOT seed the reconstructed RT0-RT7 frame - it carries the myRT convention."),
}


# provenance_status vocabulary, chosen so that no value implies random corruption:
#   PROVENANCE_PUBLISHED_SOURCE            identity from the publication/release itself
#   PROVENANCE_VERIFIED_AGAINST_MANIFEST   a shipped manifest checksum was checked and MATCHES
#   PROVENANCE_IDENTIFIED_CHECKSUM_UNVERIFIED
#       the file is identified (named in a shipped manifest, content attributable to the
#       authors) but its observed checksum DISAGREES with that manifest. The file is not
#       claimed to be damaged; the manifest simply does not describe this version.
#   PROVENANCE_IDENTIFIED_NOT_IN_MANIFEST  identified, but the manifest does not list it at
#       all, so no published checksum exists to verify against
#   MISSING_NOT_ACQUIRED                   registered but not present locally
#   PROVENANCE_IDENTIFIED_EXTERNAL_COPY_NOT_RETAINED
#       present on disk but OUTSIDE this project and deliberately not copied in; identity is
#       the recorded source path plus the observed sha256, and no published checksum exists
PROV_STATUS: dict[str, str] = {
    "myrt_refpkg_phylomodel": "PROVENANCE_VERIFIED_AGAINST_MANIFEST",
    "myrt_rvt_ref_fst": "PROVENANCE_IDENTIFIED_CHECKSUM_UNVERIFIED",
    "myrt_rvt_ref_tre": "PROVENANCE_IDENTIFIED_CHECKSUM_UNVERIFIED",
    "myrt_rvt_ref_log": "PROVENANCE_IDENTIFIED_CHECKSUM_UNVERIFIED",
    "myrt_rvt_ref_hmm": "PROVENANCE_IDENTIFIED_NOT_IN_MANIFEST",
    "myrt_rvt_ref_sto": "PROVENANCE_IDENTIFIED_NOT_IN_MANIFEST",
    "myrt_refpkg_mapping": "PROVENANCE_IDENTIFIED_NOT_IN_MANIFEST",
}
BYTE_IDENTICAL_NOTE = (
    " ALL discovered local copies of this file are BYTE-IDENTICAL to one another, so the"
    " manifest disagreement predates every local copy and is not a local-copy defect.")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_register() -> list[dict]:
    rows = []
    for aid, meta in M.items():
        s = SEL.get(aid)
        if s is None:
            continue
        pp = Path(s["project_path"])
        cite, year, tier, atype, role, seed, notes = meta
        pstat = PROV_STATUS.get(aid, "PROVENANCE_PUBLISHED_SOURCE")
        if aid in PROV_STATUS and aid != "myrt_refpkg_phylomodel":
            notes = notes + BYTE_IDENTICAL_NOTE
        rows.append({
            "asset_id": aid, "citation_or_source": cite, "year": year,
            "evidence_tier": tier, "provenance_status": pstat,
            "project_path": str(pp.relative_to(PROJ)),
            "original_path": s["selected_source"],
            "sha256": sha256(pp), "bytes": pp.stat().st_size,
            "asset_type": atype, "scientific_role": role,
            "allowed_to_seed_rt07_definition": seed, "notes": notes,
        })
    for aid, (cite, year, tier, atype, role, seed, pstat, notes) in MISSING.items():
        rows.append({
            "asset_id": aid, "citation_or_source": cite, "year": year,
            "evidence_tier": tier, "provenance_status": pstat,
            "project_path": "NOT_ACQUIRED", "original_path": "NOT_ACQUIRED",
            "sha256": "NOT_ACQUIRED", "bytes": "0", "asset_type": atype,
            "scientific_role": role,
            "allowed_to_seed_rt07_definition": seed, "notes": notes,
        })
    for aid, (ext, cite, year, tier, atype, role, seed, pstat, notes) in EXTERNAL.items():
        p = Path(ext)
        found = p.is_file()
        rows.append({
            "asset_id": aid, "citation_or_source": cite, "year": year,
            "evidence_tier": tier, "provenance_status": pstat,
            "project_path": "NOT_COPIED_EXTERNAL", "original_path": ext,
            "sha256": sha256(p) if found else "SOURCE_NOT_FOUND",
            "bytes": p.stat().st_size if found else "0", "asset_type": atype,
            "scientific_role": role,
            "allowed_to_seed_rt07_definition": seed, "notes": notes,
        })
    return rows


def finalise_source_audit(reg: list[dict]) -> list[dict]:
    chosen = {r["asset_id"]: r["original_path"] for r in reg}
    rows = []
    for aid, recs in sorted(DISC.items()):
        if not recs:
            rows.append({"asset_id": aid, "discovered_path": "NOT_FOUND", "sha256": "",
                         "bytes": "", "selected_project_copy": "NO",
                         "duplicate_group": "", "notes": "not present anywhere searched"})
            continue
        n_groups = len({r["sha256"] for r in recs})
        for r in recs:
            rows.append({
                "asset_id": aid, "discovered_path": r["path"], "sha256": r["sha256"],
                "bytes": r["bytes"],
                "selected_project_copy": "YES" if chosen.get(aid) == r["path"] else "NO",
                "duplicate_group": r["duplicate_group"],
                "notes": (f"{len(recs)} local copy(ies); {n_groups} distinct-content "
                          f"group(s); " + ("ALL byte-identical" if n_groups == 1
                                           else "NOT all identical")),
            })
    return rows


def write_tsv(path: Path, cols: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t",
                           quoting=csv.QUOTE_NONE, escapechar="\\")
        w.writeheader()
        for r in rows:
            w.writerow({k: str(r.get(k, "")).replace("\t", " ").replace("\n", " ")
                        for k in cols})


def main() -> int:
    reg = build_register()
    write_tsv(REF / "RESOURCE_REGISTER.tsv",
              ["asset_id", "citation_or_source", "year", "evidence_tier",
               "provenance_status", "project_path", "original_path", "sha256",
               "bytes", "asset_type", "scientific_role",
               "allowed_to_seed_rt07_definition", "notes"], reg)
    audit = finalise_source_audit(reg)
    write_tsv(REF / "SOURCE_AUDIT.tsv",
              ["asset_id", "discovered_path", "sha256", "bytes",
               "selected_project_copy", "duplicate_group", "notes"], audit)

    # ---- validation ----
    probs = []
    for r in reg:
        if r["project_path"] == "NOT_ACQUIRED":
            if r["provenance_status"] != "MISSING_NOT_ACQUIRED":
                probs.append(f"unacquired asset not flagged MISSING: {r['asset_id']}")
            continue
        if r["project_path"] == "NOT_COPIED_EXTERNAL":
            # Registered by identity, not by retention: the file must still be where the
            # register says it is, and must still hash to what was measured there.
            src = Path(r["original_path"])
            if not src.is_file():
                probs.append(f"EXTERNAL asset gone: {r['asset_id']} -> {src}")
            elif sha256(src) != r["sha256"]:
                probs.append(f"EXTERNAL asset changed: {r['asset_id']} -> {src}")
            continue
        pp = PROJ / r["project_path"]
        if not pp.exists():
            probs.append(f"MISSING project_path: {r['project_path']}")
            continue
        if sha256(pp) != r["sha256"]:
            probs.append(f"SHA MISMATCH on recompute: {r['asset_id']}")
        if pp.stat().st_size != int(r["bytes"]):
            probs.append(f"BYTE MISMATCH: {r['asset_id']}")
        src = Path(r["original_path"])
        if src.exists() and sha256(src) != r["sha256"]:
            probs.append(f"SOURCE CHANGED since copy: {src}")
    for aid in TIER1_EXPECTED:
        if not any(r["asset_id"] == aid for r in reg):
            probs.append(f"TIER1 MISSING: {aid}")
    t1 = [r for r in reg if r["evidence_tier"] == "TIER1"]
    bad_seed = [r["asset_id"] for r in reg
                if r["evidence_tier"] in ("TIER2", "TIER1_STRUCTURAL")
                and r["allowed_to_seed_rt07_definition"] != "NO"]
    if bad_seed:
        probs.append(f"TIER2 asset not marked NO: {bad_seed}")

    print(f"RESOURCE_REGISTER rows : {len(reg)}")
    tiers: dict[str, int] = {}
    for r in reg:
        tiers[r["evidence_tier"]] = tiers.get(r["evidence_tier"], 0) + 1
    for k, v in sorted(tiers.items()):
        print(f"  {k:<24} {v}")
    print(f"  allowed_to_seed YES  : {sum(1 for r in reg if r['allowed_to_seed_rt07_definition']=='YES')}")
    print(f"  allowed_to_seed NO   : {sum(1 for r in reg if r['allowed_to_seed_rt07_definition']=='NO')}")
    print(f"SOURCE_AUDIT rows      : {len(audit)}")
    print(f"total retained bytes   : "
          f"{sum(int(r['bytes']) for r in reg if r['project_path'] not in ('NOT_ACQUIRED', 'NOT_COPIED_EXTERNAL')):,}")
    pstats: dict[str, int] = {}
    for r in reg:
        pstats[r["provenance_status"]] = pstats.get(r["provenance_status"], 0) + 1
    print("provenance_status:")
    for k, v in sorted(pstats.items()):
        print(f"  {k:<42} {v}")
    print(f"\nVALIDATION: {'PASS - no problems' if not probs else str(len(probs))+' PROBLEM(S)'}")
    for p in probs:
        print("   ", p)
    return 1 if probs else 0


if __name__ == "__main__":
    raise SystemExit(main())
