#!/usr/bin/env python3
"""
PRIOR_WORK_LOOKUP -- bounded semantic sweep of the registered prior-work roots.

WHAT THIS IS
    The coordinating session's registry lookup (TASK_PROTOCOL step 2), run once
    per topic over the registered roots, so the downstream programme does not
    re-run what the estate already contains.

WHAT THIS IS NOT
    Not a verifier.  A hit means "material about this topic exists at this path".
    It does NOT mean the material is correct, reproducible or usable.  A hit can
    only move a topic OUT of NOT_DONE; it can never move one INTO
    SCIENTIFICALLY_ADMISSIBLE.  That classification is recorded separately and is
    a judgement, not an output of this script.

THE THREE SUBSTRATES, and each one's blind spot
      content  files <= CONTENT_MAX_BYTES, read in full.  Docs, scripts, small
               tables.  Blind to what exists only inside a large table.
      header   .tsv/.csv above that cap: first line only.  Recovers column
               semantics ("patristic_distance") without reading GBs of rows.
               Blind to row content.
      dirname  every directory path.  In this estate what was computed is often
               encoded in directory names, and those leaves are excluded from
               the content substrate.  Blind to anything not named.

POSITIVE CONTROLS -- ONE PER ROOT *PER SUBSTRATE*, AND THEY BLOCK THAT SUBSTRATE
    ⚠️ Version 1 of this script got this wrong, and the error is worth keeping
    because it is the exact failure class this programme exists to catch.  It
    OR-ed the substrates: a root passed its control if the known-present term was
    found in content *or* in directory names.  The content sweep was in fact dead
    -- it shelled out to `rg`, which on this host is a shell function and not a
    binary, so every content search returned zero -- and every root control
    nonetheless reported PASS on directory-name hits alone.  A control that
    aggregates across substrates cannot detect a dead substrate.  Controls are
    now per substrate, and a dead substrate reports SUBSTRATE_BLOCKED, under
    which absence is not reportable for that substrate.

    No external search binary is used.  Everything is read in-process.

Usage:  prior_work_lookup.py --lists <dir> --out <dir> [--workers N]
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

SCRIPT_VERSION = "2.0.0"
CONTENT_MAX_BYTES = 2 * 1024 * 1024
HEADER_EXTS = (".tsv", ".csv")
MAX_EXAMPLES = 6
CHUNK = 400

# --------------------------------------------------------------------------
# TOPICS.  One row per downstream scientific question the programme may open.
# `goals` are the operator's biological goals 1-12 the topic serves.
# --------------------------------------------------------------------------
TOPICS = [
    ("rt0_rt7_families", [1, 2],
     r"RT0|RT1|RT2|RT3|RT4|RT5|RT6|RT7|rt0_rt7|rt0-rt7"),
    ("rt_core_extraction", [2, 4],
     r"rt_core|core_extract|RT core|frame_rvt|rvt_1|core_frame|mapper_core|"
     r"core extraction|RT-core"),
    ("palm_fingers_thumb", [4],
     r"palm|fingers|thumb|subdomain_partition|three-?way domain"),
    ("yxdd_motif", [4],
     r"YXDD|YADD|YIDD|YMDD|catalytic motif|motif_[abc]\b|RT motif"),
    ("rt_tree_alignment", [3],
     r"iqtree|raxml|fasttree|treefile|patristic|bootstrap support|newick|\.nwk|"
     r"muscle|mafft|trimal|alignment_trim"),
    ("lineage_patristic_correction", [3, 7, 11],
     r"patristic|phylogenetic independent contrast|lineage.?block|lineage.?clust|"
     r"random intercept|mixed.?effect|\bICC\b|phylogenetic correction"),
    ("foldseek_structural", [5],
     r"foldseek|TM.?score|tmalign|structural alignment|3Di|structure MSA|"
     r"esmfold|alphafold|colabfold|pdb_chain|foldmason"),
    ("terminal_fusion_architecture", [4, 6],
     r"fusion|domain architecture|N-?terminal extension|C-?terminal extension|"
     r"pfam_arch|domain_order|accessory domain|domain fusion"),
    ("genomic_neighbourhood", [6],
     r"neighbourhood|neighborhood|operon|synteny|flanking gene|gene_context|"
     r"upstream_cds|downstream_cds|defence island|defense island"),
    ("ncrna_boundaries", [8, 9],
     r"ncrna_bound|msr_start|msd_end|positional prior|cmsearch|"
     r"covariance model|infernal|ncRNA extent|boundary inference"),
    ("msr_msd", [8, 9],
     r"\bmsr\b|\bmsd\b|msr_msd|msdna|msDNA|multicopy single-?stranded"),
    ("a1_a2_annotation", [9],
     r"\ba1/a2\b|\ba1_a2\b|a1 stem|a2 stem|inverted repeat|stem.?loop annot"),
    ("rt_dna", [9, 12],
     r"RT-?DNA|rtdna|reverse.?transcribed DNA|branching (G|guanosine)|2'-5'"),
    ("embeddings", [10],
     r"embedding|esm2|esm-?2|esmc|rinalmo|rna-?fm|evo2|latent space|"
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
     r"producer|non-?producer|assayed|experimental evidence register|"
     r"support\.csv|efe1|ec86|eco1|eco2|retron panel"),
]

# Known-present on every registered root.  One per substrate, and BLOCKING for
# that substrate alone.
ROOT_CONTROL = r"retron"

_RX = [(name, re.compile(pat, re.I)) for name, _g, pat in TOPICS]
_CTL = re.compile(ROOT_CONTROL, re.I)


def scan_chunk(paths: list[str]) -> dict:
    """Read each file once; test every topic regex plus the control."""
    hits = defaultdict(list)
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        if _CTL.search(text):
            hits["__CONTROL__"].append(p)
        for name, rx in _RX:
            if rx.search(text):
                hits[name].append(p)
    return {k: v for k, v in hits.items()}


def scan_headers(paths: list[str]) -> dict:
    hits = defaultdict(list)
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                first = fh.readline()
        except OSError:
            continue
        if _CTL.search(first):
            hits["__CONTROL__"].append(p)
        for name, rx in _RX:
            if rx.search(first):
                hits[name].append(p)
    return {k: v for k, v in hits.items()}


def scan_dirs(dirs: list[str]) -> dict:
    hits = defaultdict(list)
    for d in dirs:
        base = os.path.basename(d)
        if _CTL.search(base):
            hits["__CONTROL__"].append(d)
        for name, rx in _RX:
            if rx.search(base):
                hits[name].append(d)
    return {k: v for k, v in hits.items()}


def merge(into: dict, frm: dict) -> None:
    for k, v in frm.items():
        into[k].extend(v)


def read_list(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as fh:
        return [ln.rstrip("\n") for ln in fh if ln.strip()]


def rel(p: str) -> str:
    return os.path.relpath(p, "/home/borg")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lists", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()

    roots = sorted(f[:-len(".files")] for f in os.listdir(args.lists)
                   if f.endswith(".files"))

    per_root: dict[str, dict] = {}
    for tag in roots:
        files = read_list(os.path.join(args.lists, tag + ".files"))
        dirs = read_list(os.path.join(args.lists, tag + ".dirs"))
        content, header = [], []
        for p in files:
            try:
                sz = os.path.getsize(p)
            except OSError:
                continue
            (content if sz <= CONTENT_MAX_BYTES
             else (header if p.lower().endswith(HEADER_EXTS) else [])).append(p)

        c_hits: dict = defaultdict(list)
        if content:
            chunks = [content[i:i + CHUNK] for i in range(0, len(content), CHUNK)]
            with ProcessPoolExecutor(max_workers=args.workers) as ex:
                for res in ex.map(scan_chunk, chunks):
                    merge(c_hits, res)
        h_hits = defaultdict(list)
        merge(h_hits, scan_headers(header))
        d_hits = defaultdict(list)
        merge(d_hits, scan_dirs(dirs))

        per_root[tag] = {
            "n_content": len(content), "n_header": len(header), "n_dirs": len(dirs),
            "content": c_hits, "header": h_hits, "dirname": d_hits,
        }
        sys.stderr.write(
            f"  {tag:<56} content={len(content):>7} "
            f"ctl_hits={len(c_hits.get('__CONTROL__', []))}\n")

    # ---- CONTROLS, PER SUBSTRATE, BLOCKING THAT SUBSTRATE ONLY -------------
    ctl_rows, blocked = [], set()
    for tag in roots:
        r = per_root[tag]
        for sub, n_searched in (("content", r["n_content"]),
                                ("header", r["n_header"]),
                                ("dirname", r["n_dirs"])):
            n_ctl = len(r[sub].get("__CONTROL__", []))
            if n_searched == 0:
                state, note = "NOT_EVALUABLE", "substrate is empty on this root"
            elif n_ctl > 0:
                state, note = "PASS", ""
            else:
                state, note = "FAIL", "substrate searched but known-present term not recovered"
                blocked.add((tag, sub))
            ctl_rows.append([
                tag, sub, "positive", "YES",
                f"/{ROOT_CONTROL}/i recoverable on this substrate of this root",
                f"{n_ctl} hit(s) over {n_searched} unit(s)", state, note])

    with open(os.path.join(args.out, "PRIOR_WORK_CONTROLS.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["root", "substrate", "control_type", "blocking",
                    "expectation", "observed", "state", "note"])
        w.writerows(ctl_rows)

    # ---- per-root-per-topic ------------------------------------------------
    rows = []
    for topic, goals, _ in TOPICS:
        for tag in roots:
            r = per_root[tag]
            counts, examples, states = {}, [], []
            for sub in ("content", "header", "dirname"):
                hs = r[sub].get(topic, [])
                counts[sub] = len(hs)
                examples += [rel(x) for x in hs[:2]]
                if (tag, sub) in blocked:
                    states.append("BLOCKED")
                elif r["n_" + ("content" if sub == "content"
                               else "header" if sub == "header" else "dirs")] == 0:
                    states.append("EMPTY")
                else:
                    states.append("HIT" if hs else "NO_HIT")
            overall = ("HIT" if "HIT" in states
                       else "SUBSTRATE_BLOCKED" if "BLOCKED" in states
                       else "NO_HIT")
            rows.append([topic, ",".join(map(str, goals)), tag, overall,
                         counts["content"], counts["header"], counts["dirname"],
                         "/".join(states), ";".join(examples[:MAX_EXAMPLES])])

    with open(os.path.join(args.out, "PRIOR_WORK_LOOKUP.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["topic", "goals", "root", "state", "n_content_files",
                    "n_table_headers", "n_dir_names",
                    "substrate_states_content/header/dirname",
                    "example_paths_rel_home"])
        w.writerows(rows)

    # ---- topic rollup ------------------------------------------------------
    with open(os.path.join(args.out, "PRIOR_WORK_SUMMARY.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["topic", "goals", "n_roots_with_hits", "n_content_files",
                    "n_table_headers", "n_dir_names", "top_roots",
                    "example_paths_rel_home"])
        for topic, goals, _ in TOPICS:
            tot = {"content": 0, "header": 0, "dirname": 0}
            rootn, ex = {}, []
            for tag in roots:
                r = per_root[tag]
                n = sum(len(r[s].get(topic, [])) for s in tot)
                if n:
                    rootn[tag] = n
                for s in tot:
                    tot[s] += len(r[s].get(topic, []))
                    ex += [rel(x) for x in r[s].get(topic, [])[:1]]
            top = sorted(rootn.items(), key=lambda kv: -kv[1])[:4]
            w.writerow([topic, ",".join(map(str, goals)), len(rootn),
                        tot["content"], tot["header"], tot["dirname"],
                        ";".join(f"{k}({v})" for k, v in top),
                        ";".join(ex[:MAX_EXAMPLES])])

    meta = {
        "script_version": SCRIPT_VERSION,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_s": round(time.time() - started, 1),
        "content_max_bytes": CONTENT_MAX_BYTES,
        "n_topics": len(TOPICS),
        "external_search_binary_used": None,
        "blocked_substrates": sorted(f"{t}:{s}" for t, s in blocked),
        "roots": {t: {"n_content": per_root[t]["n_content"],
                      "n_header": per_root[t]["n_header"],
                      "n_dirs": per_root[t]["n_dirs"]} for t in roots},
    }
    with open(os.path.join(args.out, "PRIOR_WORK_META.json"), "w") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
    print(json.dumps(meta, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
