#!/usr/bin/env python3
"""Stage-2 prep step 1: discover every local copy of each candidate RT0-RT7 asset,
hash it, and group byte-identical copies.

Read-only over all source trees. Writes references/rt0_rt7/SOURCE_AUDIT.tsv and a
cache of the discovery for the copy/register steps. No file outside
references/rt0_rt7/ is created, moved, deleted or modified.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
REF = PROJ / "references/rt0_rt7"
SEARCH_ROOT = Path("/home/borg")

# Directories that cannot contain a project reference asset; skipping them keeps the
# sweep to minutes instead of hours.
SKIP_DIRS = {"miniconda3", ".cache", ".git", "node_modules", "site-packages",
             ".conda", ".codex", ".claude", ".cursor-server", "RNAformer",
             "foldseek", "esm", "evo2", "DeepFRI", "boltzgen", ".local"}

# asset_id -> (basename to match, exact match or suffix)
CANDIDATES: dict[str, str] = {
    # --- TIER1 primary literature (PDFs located by content sweep) ---
    "lit_poch1989": "Poch Sauvaget Delarue Tordo 1989 EMBO J - Identification of four conserved motifs among the RNA-dependent polymerase encoding elements.pdf",
    "lit_xiong1990": "Origin and evolution of retroelements based upon their reverse transcriptase sequences. .pdf",
    "lit_zimmerly2001": "Zimmerly Hausner Wu 2001 NAR - Phylogenetic relationships among group II intron ORFs (defines RT subdomain 0).pdf",
    "lit_simon2008": "A diversity of uncharacterized reverse transcriptases in bacteria .pdf",
    # TIER1_STRUCTURAL -- structural primary evidence; NOT allowed to seed the
    # historical sequence RT0-RT7 frame (operator amendment 2026-09-15).
    "lit_blocker2005_structural": "Domain structure and three-dimensional model of a group II intron-encoded reverse transcriptase.pdf",
    # --- TIER2 comparators already expected in the project ---
    "hist_toro2014_rt0rt7_fasta": "toro_2014_Rt0-Rt7.FASTA",
    "mestre_tree_nwk": "Supplementary_mestre_Tree.nwk",
    "mestre_supp_sanitised_a": "supp_material_systematic_prediction_paper.csv",
    "mestre_supp_sanitised_b": "Supp_material_T1_R1_systematic_prediction.csv",
    "myrt_rvt_ref_hmm": "RVT-ref.hmm",
    "myrt_suppl_toro_tree": "Suppl_Toro_Tree.txt",
    "toro2026_epang_newick": "retron_reference_phylogeny_EPAng.newick",
    "toro2026_type_hmms_tgz": "SPIRE_retron_type_specific_HMMs.tar.gz",
    "toro2026_typexi_contree": "typeXI_local_tree.contree",
    # --- TIER2 comparators discovered by this sweep ---
    "hist_toro2014_tableS1": "TableS1_Toro_2014.XLSX",
    "mestre_supp_original_headers": "Mestre_supplementary_material.csv",
    "myrt_rvt_ref_sto": "RVT-ref.sto",
    "myrt_rvt_ref_tre": "RVT-ref.tre",
    "myrt_rvt_ref_fst": "RVT-ref.fst",
    "myrt_rvt_ref_log": "RVT-ref.log",
    "myrt_refpkg_mapping": "Mapping",
    "myrt_refpkg_contents": "CONTENTS.json",
    "myrt_refpkg_phylomodel": "phylo_modeldyadg_ia.json",
    "myrt_buildrvt_sh": "buildRVT.sh",
    "toro2026_pipeline_scripts_zip": "SPIRE_retron_pipeline_scripts (1).zip",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def walk() -> dict[str, list[Path]]:
    """One pass over the tree, collecting every path whose basename is a candidate."""
    want: dict[str, list[str]] = {}
    for aid, base in CANDIDATES.items():
        want.setdefault(base, []).append(aid)
    found: dict[str, list[Path]] = {aid: [] for aid in CANDIDATES}
    for root, dirs, files in os.walk(SEARCH_ROOT, topdown=True):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in files:
            if fn in want:
                for aid in want[fn]:
                    found[aid].append(Path(root) / fn)
    return found


def main() -> int:
    found = walk()
    rows, cache = [], {}
    for aid, paths in sorted(found.items()):
        if not paths:
            rows.append({"asset_id": aid, "discovered_path": "NOT_FOUND",
                         "sha256": "", "bytes": "", "selected_project_copy": "NO",
                         "duplicate_group": "", "notes":
                         f"expected basename '{CANDIDATES[aid]}' not present anywhere "
                         f"under {SEARCH_ROOT} outside skipped tool/env trees"})
            cache[aid] = []
            continue
        recs = []
        for p in sorted(paths):
            try:
                recs.append({"path": str(p), "sha256": sha256(p),
                             "bytes": p.stat().st_size})
            except OSError as e:
                recs.append({"path": str(p), "sha256": f"UNREADABLE:{e.errno}",
                             "bytes": -1})
        # Group byte-identical copies; group letter is stable by sorted hash order.
        hashes = sorted({r["sha256"] for r in recs})
        gmap = {h: f"{aid}#g{i+1}" for i, h in enumerate(hashes)}
        for r in recs:
            r["duplicate_group"] = gmap[r["sha256"]]
        cache[aid] = recs
        n_groups = len(hashes)
        for r in recs:
            note = ("single local copy" if len(recs) == 1 else
                    f"{len(recs)} local copies in {n_groups} distinct-content group(s)")
            if n_groups > 1:
                note += " — NOT all byte-identical; see other rows for this asset_id"
            rows.append({"asset_id": aid, "discovered_path": r["path"],
                         "sha256": r["sha256"], "bytes": r["bytes"],
                         "selected_project_copy": "PENDING",
                         "duplicate_group": r["duplicate_group"], "notes": note})
    REF.mkdir(parents=True, exist_ok=True)
    (REF / "_provenance/discovery.json").write_text(
        json.dumps(cache, indent=2), encoding="utf-8")
    cols = ["asset_id", "discovered_path", "sha256", "bytes",
            "selected_project_copy", "duplicate_group", "notes"]
    with (REF / "SOURCE_AUDIT.tsv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t",
                           quoting=csv.QUOTE_NONE, escapechar="\\")
        w.writeheader()
        w.writerows(rows)

    print(f"assets sought        : {len(CANDIDATES)}")
    print(f"assets NOT FOUND     : {sum(1 for a, v in cache.items() if not v)}")
    print(f"discovered copies    : {sum(len(v) for v in cache.values())}")
    multi = {a: v for a, v in cache.items()
             if len({r['sha256'] for r in v}) > 1}
    print(f"assets with NON-IDENTICAL copies: {len(multi)}")
    for a, v in sorted(multi.items()):
        print(f"   {a}: {len({r['sha256'] for r in v})} distinct contents "
              f"over {len(v)} copies")
    dupes = {a: v for a, v in cache.items()
             if len(v) > 1 and len({r['sha256'] for r in v}) == 1}
    print(f"assets with byte-identical duplicates: {len(dupes)}")
    for a, v in sorted(dupes.items()):
        print(f"   {a}: {len(v)} identical copies")
    for a, v in sorted(cache.items()):
        if not v:
            print(f"   NOT_FOUND: {a}  ({CANDIDATES[a]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
