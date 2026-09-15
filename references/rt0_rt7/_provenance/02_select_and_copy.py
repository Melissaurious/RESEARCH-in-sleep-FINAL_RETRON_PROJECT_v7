#!/usr/bin/env python3
"""Stage-2 prep step 2: choose ONE canonical copy per asset and copy it in.

Selection policy, declared before running:
  1. a copy already inside this project (CLAUDE.md: reuse an existing MELISSA_DATA copy)
  2. else RETRON-DB_V4  (most complete literature + supporting_material set)
  3. else RETRON-DB_V3, then any remaining copy in sorted path order
Every asset's copies were verified byte-identical in step 1, so selection cannot
change content -- only provenance. Copy only; nothing is moved, deleted or edited.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

PROJ = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
REF = PROJ / "references/rt0_rt7"
DISC = json.loads((REF / "_provenance/discovery.json").read_text(encoding="utf-8"))

# asset_id -> destination relative to references/rt0_rt7/
DEST = {
    "lit_poch1989": "literature/Poch_Sauvaget_Delarue_Tordo_1989_EMBO_J_four_conserved_motifs.pdf",
    "lit_xiong1990": "literature/Xiong_Eickbush_1990_EMBO_J_origin_evolution_retroelements_RT.pdf",
    "lit_zimmerly2001": "literature/Zimmerly_Hausner_Wu_2001_NAR_group_II_intron_ORF_phylogeny.pdf",
    "lit_simon2008": "literature/Simon_Zimmerly_2008_NAR_diversity_uncharacterized_bacterial_RTs.pdf",
    "lit_blocker2005_structural": "literature/Blocker_et_al_2005_RNA_group_II_intron_RT_domain_structure_3D_model.pdf",
    "hist_toro2014_rt0rt7_fasta": "historical/toro_2014_Rt0-Rt7.FASTA",
    "hist_toro2014_tableS1": "historical/TableS1_Toro_2014.XLSX",
    "mestre_tree_nwk": "mestre_2020/Supplementary_mestre_Tree.nwk",
    "mestre_supp_sanitised_a": "mestre_2020/supp_material_systematic_prediction_paper.csv",
    "mestre_supp_sanitised_b": "mestre_2020/Supp_material_T1_R1_systematic_prediction.csv",
    "mestre_supp_original_headers": "mestre_2020/Mestre_supplementary_material.csv",
    "myrt_rvt_ref_hmm": "myrt/RVT-ref.hmm",
    "myrt_suppl_toro_tree": "myrt/Suppl_Toro_Tree.txt",
    "myrt_refpkg_contents": "myrt/myRT-FastTree2.refpkg/CONTENTS.json",
    "myrt_refpkg_mapping": "myrt/myRT-FastTree2.refpkg/Mapping",
    "myrt_refpkg_phylomodel": "myrt/myRT-FastTree2.refpkg/phylo_modeldyadg_ia.json",
    "myrt_rvt_ref_fst": "myrt/myRT-FastTree2.refpkg/RVT-ref.fst",
    "myrt_rvt_ref_sto": "myrt/myRT-FastTree2.refpkg/RVT-ref.sto",
    "myrt_rvt_ref_tre": "myrt/myRT-FastTree2.refpkg/RVT-ref.tre",
    "myrt_rvt_ref_log": "myrt/myRT-FastTree2.refpkg/RVT-ref.log",
    "myrt_buildrvt_sh": "myrt/buildRVT.sh",
    "toro2026_epang_newick": "toro_2026/retron_reference_phylogeny_EPAng.newick",
    "toro2026_type_hmms_tgz": "toro_2026/SPIRE_retron_type_specific_HMMs.tar.gz",
    "toro2026_typexi_contree": "toro_2026/typeXI_local_tree.contree",
    "toro2026_pipeline_scripts_zip": "toro_2026/SPIRE_retron_pipeline_scripts.zip",
}
PREF = [str(PROJ), "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4",
        "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rank(path: str) -> tuple[int, str]:
    for i, pre in enumerate(PREF):
        if path.startswith(pre):
            # Prefer a copy already at the destination, then MELISSA_DATA.
            sub = 0 if "/references/rt0_rt7/" in path else 1
            return (i * 10 + sub, path)
    return (999, path)


def main() -> int:
    sel, copied, kept = {}, 0, 0
    for aid, dest_rel in DEST.items():
        recs = DISC.get(aid) or []
        if not recs:
            print(f"SKIP (not found): {aid}")
            continue
        src = Path(sorted((rank(r["path"]) for r in recs))[0][1])
        want = next(r["sha256"] for r in recs if r["path"] == str(src))
        dest = REF / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and sha256(dest) == want:
            kept += 1
            action = "KEPT (already correct)"
        else:
            shutil.copy2(src, dest)          # copy only; never move
            copied += 1
            action = "COPIED"
        got = sha256(dest)
        assert got == want, f"post-copy hash mismatch for {aid}: {got} != {want}"
        assert dest.stat().st_size == src.stat().st_size, f"size mismatch {aid}"
        sel[aid] = {"selected_source": str(src), "project_path": str(dest),
                    "sha256": got, "bytes": dest.stat().st_size, "action": action}
        print(f"  {action:<22} {aid:<30} <- {src}")
    (REF / "_provenance/selection.json").write_text(
        json.dumps(sel, indent=2), encoding="utf-8")
    print(f"\ncopied: {copied}   already present and correct: {kept}   "
          f"total retained: {len(sel)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
