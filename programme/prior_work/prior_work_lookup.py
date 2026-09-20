#!/usr/bin/env python3
"""
PRIOR_WORK_LOOKUP -- bounded semantic sweep of the registered prior-work roots.

WHAT THIS IS
    The coordinating session's registry lookup (TASK_PROTOCOL step 2), run once
    per topic over the registered roots, so that the downstream programme does
    not re-run something the estate already contains.

WHAT THIS IS NOT
    It is not a verifier.  A hit means "material about this topic exists at this
    path".  It does NOT mean the material is correct, reproducible, or usable.
    Classification into the eight readiness classes is a human/coordinator
    judgement recorded in PRIOR_WORK_CLASSIFICATION.tsv, and a hit only ever
    moves a topic OUT of NOT_DONE -- never into SCIENTIFICALLY_ADMISSIBLE.

THE THREE SUBSTRATES, and why there are three
    The estate is 115 GB in one root.  A single content sweep would not finish,
    so the sweep is split and each part's blind spot is stated:

      content  files <= CONTENT_MAX_BYTES, searched in full.  Docs, scripts,
               small tables.  Blind to what is only inside a large table.
      header   .tsv/.csv above that cap: first line only.  Recovers column
               semantics ("patristic_distance") without reading GBs of rows.
               Blind to row content.
      dirname  every directory path.  In this estate what was computed is
               encoded in directory names, and those leaves are excluded from
               the content sweep.  Blind to anything not named.

POSITIVE CONTROL, per root, BLOCKING for that root
    Every root sweep carries a control term that is known present on that
    substrate.  If the control returns zero hits, the sweep of that root is
    reported ROOT_BLOCKED and its topics are NOT reported as absent.  This is
    the programme's rule that no absence is claimed without a positive control
    showing the instrument can recover a known-present case.

Usage:  prior_work_lookup.py --lists <dir> --out <dir>
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict

CONTENT_MAX_BYTES = 2 * 1024 * 1024
HEADER_EXTS = (".tsv", ".csv")
MAX_EXAMPLES = 6

# --------------------------------------------------------------------------
# TOPICS.  One row per downstream scientific question the programme may open.
# `probe` is a case-insensitive extended regex searched on all three substrates.
# `goals` are the operator's biological goals 1-12 this topic serves.
# --------------------------------------------------------------------------
TOPICS = [
    ("rt0_rt7_families", [1, 2],
     r"RT0|RT1|RT2|RT3|RT4|RT5|RT6|RT7|rt0_rt7|rt0-rt7"),
    ("rt_core_extraction", [2, 4],
     r"rt_core|core_extract|RT core|frame_rvt|rvt_1|RVT_1|core_frame|mapper_core"),
    ("palm_fingers_thumb", [4],
     r"palm|fingers|thumb|subdomain_partition|three-?way domain"),
    ("yxdd_motif", [4],
     r"YXDD|YADD|YIDD|YMDD|catalytic motif|motif_[abc]\b|RT motif"),
    ("rt_tree_alignment", [3],
     r"iqtree|raxml|fasttree|treefile|patristic|bootstrap support|newick|\.nwk|"
     r"muscle|mafft|trimal|alignment_trim"),
    ("lineage_patristic_correction", [3, 7, 11],
     r"patristic|phylogenetic independent contrast|lineage.?block|lineage.?clust|"
     r"random intercept|mixed.?effect|ICC|phylogenetic correction"),
    ("foldseek_structural", [5],
     r"foldseek|TM.?score|tmalign|structural alignment|3Di|structure MSA|"
     r"esmfold|alphafold|colabfold|pdb_chain"),
    ("terminal_fusion_architecture", [4, 6],
     r"fusion|domain architecture|N-?terminal extension|C-?terminal extension|"
     r"pfam_arch|domain_order|accessory domain"),
    ("genomic_neighbourhood", [6],
     r"neighbourhood|neighborhood|operon|synteny|flanking gene|gene_context|"
     r"upstream_cds|downstream_cds|defence island|defense island"),
    ("ncrna_boundaries", [8, 9],
     r"ncrna_bound|boundary|msr_start|msd_end|extent|interval prior|"
     r"positional prior|cmsearch|covariance model|infernal"),
    ("msr_msd", [8, 9],
     r"\bmsr\b|\bmsd\b|msr_msd|msdna|multicopy single-?stranded"),
    ("a1_a2_annotation", [9],
     r"\ba1/a2\b|\ba1_a2\b|a1 stem|a2 stem|inverted repeat|stem.?loop annot"),
    ("rt_dna", [9, 12],
     r"RT-?DNA|rtdna|reverse.?transcribed DNA|branch(ing)? (G|guanosine)|2'-5'"),
    ("embeddings", [10],
     r"embedding|esm2|esm-?2|esmc|rinalmo|rna-?fm|evo2|\.npy|latent space|"
     r"cosine similarity|umap|t-?sne"),
    ("rt_ncrna_pairing", [10, 11, 12],
     r"pairing|cognate|pair_elig|rt_ncrna_pair|retrieval gate|counterfactual|"
     r"decoder|likelihood difference"),
    ("orthogonality_crosspair", [12],
     r"orthogonal|cross-?pair|non-?cognate|swap|compatibility matrix|interchangeab"),
    ("database_characterization", [1],
     r"database characteri|db_characteri|dbchar|corpus identity|record manifest|"
     r"unit ladder|redundancy ladder"),
    ("taxonomy_distribution", [1, 6],
     r"gtdb|taxonom|phylum|lineage assignment|ncbi_bacteria|mgnify|uhgg|gem_metadata"),
    ("diversity_saturation", [1, 3],
     r"rarefaction|saturation|novelty|diversity index|accumulation curve|"
     r"cluster_count|mmseqs"),
    ("evolutionary_correspondence", [7],
     r"co-?evolution|coevol|mirrortree|tanglegram|cophylo|correspondence|"
     r"mantel|procrustes"),
    ("integrative_model", [11],
     r"integrat(ive|ed) model|joint model|multi-?modal|feature_union|"
     r"ablation|prior increment"),
    ("annotation_disagreement", [1, 6],
     r"tool disagree|annotation disagree|padloc|defensefinder|defense-?finder|"
     r"discrepan|concordance"),
    ("structure_prediction_assets", [5],
     r"\.pdb\b|\.cif\b|predicted structure|plddt|pae_|structure_register"),
    ("experimental_panel", [12],
     r"panel|producer|non-?producer|assayed|experimental evidence register|"
     r"support\.csv|efe1|ec86|eco1|eco2"),
]

# --------------------------------------------------------------------------
# POSITIVE CONTROLS, one per root, BLOCKING for that root.
# Each is a term the root is known to contain.  It proves the instrument can
# recover a known-present case on this substrate before any absence is reported.
# --------------------------------------------------------------------------
ROOT_CONTROL = r"retron|Retron|RETRON"


def read_list(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as fh:
        return [ln.rstrip("\n") for ln in fh if ln.strip()]


def split_substrates(files: list[str]) -> tuple[list[str], list[str]]:
    """Return (content_files, header_files)."""
    content, header = [], []
    for p in files:
        try:
            sz = os.path.getsize(p)
        except OSError:
            continue
        if sz <= CONTENT_MAX_BYTES:
            content.append(p)
        elif p.lower().endswith(HEADER_EXTS):
            header.append(p)
    return content, header


def rg_count(pattern: str, file_list_path: str) -> tuple[int, list[str]]:
    """Files-with-matches count and up to MAX_EXAMPLES example paths."""
    if not os.path.exists(file_list_path) or os.path.getsize(file_list_path) == 0:
        return 0, []
    proc = subprocess.run(
        ["xargs", "-0", "-r", "rg", "--no-messages", "--files-with-matches",
         "-i", "-e", pattern, "--"],
        input=open(file_list_path, "rb").read(),
        capture_output=True,
    )
    out = proc.stdout.decode("utf-8", "replace").splitlines()
    return len(out), out[:MAX_EXAMPLES]


def header_hits(pattern: str, paths: list[str]) -> tuple[int, list[str]]:
    rx = re.compile(pattern, re.I)
    hits = []
    for p in paths:
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
        except OSError:
            continue
        if rx.search(first):
            hits.append(p)
    return len(hits), hits[:MAX_EXAMPLES]


def dir_hits(pattern: str, dirs: list[str]) -> tuple[int, list[str]]:
    rx = re.compile(pattern, re.I)
    hits = [d for d in dirs if rx.search(os.path.basename(d))]
    return len(hits), hits[:MAX_EXAMPLES]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lists", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()

    roots = sorted(
        f[:-len(".files")] for f in os.listdir(args.lists) if f.endswith(".files")
    )

    # ---- substrate preparation, per root ---------------------------------
    prepared = {}
    for tag in roots:
        files = read_list(os.path.join(args.lists, tag + ".files"))
        dirs = read_list(os.path.join(args.lists, tag + ".dirs"))
        content, header = split_substrates(files)
        cpath = os.path.join(args.out, tag + ".content.nul")
        with open(cpath, "wb") as fh:
            for p in content:
                fh.write(p.encode() + b"\0")
        prepared[tag] = {"content_list": cpath, "n_content": len(content),
                         "header": header, "dirs": dirs, "n_files": len(files)}

    # ---- CONTROLS FIRST, and they block the root they cover ---------------
    control_rows = []
    blocked = set()
    for tag in roots:
        p = prepared[tag]
        n_c, ex_c = rg_count(ROOT_CONTROL, p["content_list"])
        n_d, _ = dir_hits(ROOT_CONTROL, p["dirs"])
        ok = (n_c + n_d) > 0
        if not ok:
            blocked.add(tag)
        control_rows.append([
            tag, "positive", "YES", "known-present term recoverable on this root",
            f"content_files={n_c} dirs={n_d}", "PASS" if ok else "FAIL",
            f"n_content_files_searched={p['n_content']} of {p['n_files']}; "
            f"examples={';'.join(os.path.relpath(e, '/home/borg') for e in ex_c[:3])}",
        ])
    with open(os.path.join(args.out, "PRIOR_WORK_CONTROLS.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["root", "control_type", "blocking", "expectation",
                    "observed", "state", "detail"])
        w.writerows(control_rows)

    if blocked:
        sys.stderr.write("ROOT_BLOCKED (absence not reportable here): "
                         + ", ".join(sorted(blocked)) + "\n")

    # ---- topic sweep -------------------------------------------------------
    rows = []
    summary = defaultdict(lambda: {"content": 0, "header": 0, "dirname": 0,
                                   "roots": set(), "examples": []})
    for topic, goals, probe in TOPICS:
        for tag in roots:
            p = prepared[tag]
            n_c, ex_c = rg_count(probe, p["content_list"])
            n_h, ex_h = header_hits(probe, p["header"])
            n_d, ex_d = dir_hits(probe, p["dirs"])
            state = "ROOT_BLOCKED" if tag in blocked else (
                "HIT" if (n_c + n_h + n_d) else "NO_HIT")
            ex = (ex_c + ex_h + ex_d)[:MAX_EXAMPLES]
            rows.append([topic, ",".join(map(str, goals)), tag, state,
                         n_c, n_h, n_d,
                         ";".join(os.path.relpath(e, "/home/borg") for e in ex)])
            if state == "HIT":
                s = summary[topic]
                s["content"] += n_c
                s["header"] += n_h
                s["dirname"] += n_d
                s["roots"].add(tag)
                for e in ex:
                    if len(s["examples"]) < MAX_EXAMPLES:
                        s["examples"].append(os.path.relpath(e, "/home/borg"))
        sys.stderr.write(f"  swept {topic}\n")

    with open(os.path.join(args.out, "PRIOR_WORK_LOOKUP.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["topic", "goals", "root", "state",
                    "n_content_files", "n_table_headers", "n_dir_names",
                    "example_paths_rel_home"])
        w.writerows(rows)

    with open(os.path.join(args.out, "PRIOR_WORK_SUMMARY.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["topic", "goals", "n_roots_with_hits",
                    "n_content_files", "n_table_headers", "n_dir_names",
                    "example_paths_rel_home"])
        for topic, goals, _ in TOPICS:
            s = summary[topic]
            w.writerow([topic, ",".join(map(str, goals)), len(s["roots"]),
                        s["content"], s["header"], s["dirname"],
                        ";".join(s["examples"])])

    meta = {
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "elapsed_s": round(time.time() - started, 1),
        "content_max_bytes": CONTENT_MAX_BYTES,
        "n_topics": len(TOPICS),
        "roots": {t: {"n_files": prepared[t]["n_files"],
                      "n_content_searched": prepared[t]["n_content"],
                      "n_table_headers": len(prepared[t]["header"]),
                      "n_dirs": len(prepared[t]["dirs"]),
                      "control": "FAIL" if t in blocked else "PASS"} for t in roots},
    }
    with open(os.path.join(args.out, "PRIOR_WORK_META.json"), "w") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
    print(json.dumps(meta, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
