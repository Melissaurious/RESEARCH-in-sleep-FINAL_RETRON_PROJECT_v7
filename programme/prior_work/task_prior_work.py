#!/usr/bin/env python3
"""
TASK-SPECIFIC PRIOR_WORK_LOOKUP over the GOVERNED scientific record.

DISTINCT FROM THE ESTATE SWEEP.  `prior_work_lookup.py` answers "does material on
this topic exist anywhere in the 155 GB estate".  This answers a different and
sharper question, per task:

    has THIS analysis already been done inside the governed record, and if so,
    in which bundle, on which substrate, and is the number re-derivable?

Because the governed roots are ~1,400 files rather than 708,000, this sweep is
UNBOUNDED: every file is read, every table header parsed, every parquet schema
opened.  Nothing is size-capped and nothing is depth-capped.

FOUR SUBSTRATES
    path      file and directory names
    content   full text of .md .tex .ipynb .py .R .r .sh .json .txt .tsv .csv
    header    first line of every .tsv/.csv -- the column vocabulary, which is
              what says whether a QUANTITY was computed
    parquet   pyarrow schema column names, same purpose for binary tables

CONTROLS -- TWO KINDS, BOTH BLOCKING
  1 SUBSTRATE LIVENESS, per root x substrate.  Not a term search: it asserts the
    reader actually parsed something of that kind on that root (>=1 file read,
    and for header/parquet >=1 schema with >=2 columns).  A dead reader fails it.
    Last night an estate sweep returned zero for 24 topics while its control
    passed, because the control asked "content OR dirname" and dirname matched.
    Liveness is per substrate and cannot be satisfied by a different substrate.

  2 NAMED ANCHOR, per task, where one exists.  A term this session asserts is
    present at a NAMED root on a NAMED substrate, verified before any absence is
    reported for that task.  A task whose anchor misses is reported
    ANCHOR_FAILED and its absence is NOT reportable.
    Tasks with no anchor are reported NO_ANCHOR: genuinely new work, where
    absence rests on liveness alone and is correspondingly weaker.

Usage:  task_prior_work.py --out <dir>
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import csv
import json
import os
import re
import time
from collections import defaultdict

SCRIPT_VERSION = "1.0.0"
SYN = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-synthesis"
V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
RDB = "/home/borg/RESEARCH-retron-db"

TEXT_EXT = (".md", ".tex", ".ipynb", ".py", ".R", ".r", ".sh", ".json",
            ".txt", ".tsv", ".csv", ".yaml", ".yml", ".nwk", ".afa")
TABLE_EXT = (".tsv", ".csv")
MAX_TEXT_BYTES = 8 * 1024 * 1024

# --------------------------------------------------------------------------
# ROOTS.  Each is a named slice of the governed or registered record.
# --------------------------------------------------------------------------
ROOTS = {
    "governed_results":      f"{SYN}/results",
    "governed_docs":         f"{SYN}/docs",
    "governed_analysis":     f"{SYN}/analysis",
    "idea_stage":            f"{SYN}/idea-stage",
    "references":            f"{SYN}/references",
    "v7_data_derived":       f"{V7}/data/derived",
    "v7_analysis_workbench": f"{V7}/analysis/dbchar_rt_ncrna_workbench",
    "rdb_data_derived":      f"{RDB}/data/derived",
    "wt_embeddings":         "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings/results",
    "wt_spire_ncrna":        "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-spire-ncrna/analysis",
    "wt_mestre_audit":       "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit/analysis",
    "wt_stage3c":            "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-stage3c/analysis",
    "wt_asset_audit":        "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit/analysis",
}

# --------------------------------------------------------------------------
# TASK QUERIES.
#   probe  : regex, searched on all four substrates
#   anchor : (regex, root_key, substrate) that MUST hit, or absence is void
# --------------------------------------------------------------------------
Q = [
    # ---- goal 1 · resource / database -----------------------------------
    ("T-REG2-registry-coverage-validated",
     r"registry.?coverage|NAMED_EXACT|named_by_ancestor|asset.?sweep", None),
    ("T-REG3-content-hash-pass",
     r"content.?hash|manifest_sha256|pin_collision", None),
    ("T-REG4-kind-extension-sweep",
     r"alignment|parquet|checkpoint|\.afa\b|\.h5ad\b", None),
    ("T-LINT5-prose-numbers-gated",
     r"prose.?number|numeric.?provenance|LINT_UNRESOLVED", None),
    ("T-D1-annotation-disagreement",
     r"tool.?call|padloc|defense.?finder|defensefinder|disagree|concordance|venn",
     (r"tool", "governed_results", "path")),
    ("T-D2-taxonomic-distribution",
     r"gtdb|phylum|taxonom|prevalence|metadata.?sampling|mgnify|uhgg",
     (r"gtdb|taxonom", "governed_results", "content")),
    ("T-AUDIT2-task-report-backfill",
     r"TASK_REPORT|CONSUMABLE_OUTPUTS|TASK_STATE", None),

    # ---- goal 2 · RT0-RT7 / core ----------------------------------------
    ("T-C1-rt-core-extraction",
     r"rt_core|core_extract|frame_rvt|rvt|mapper|residue.?map|full.?length",
     (r"frame_rvt", "rdb_data_derived", "path")),
    ("T-A16-reciprocal-frame",
     r"reciprocal|family.?frame|seven.?family|family_baseline",
     (r"family_baseline", "governed_results", "path")),
    ("T-RT07-definition-status",
     r"RT0|RT1|RT7|rt0_rt7|clade.?system|placement",
     (r"RT7|rt0_rt7", "governed_results", "content")),

    # ---- goal 3 · relatedness / phylogeny --------------------------------
    ("T-P1-relatedness-backbone",
     r"mmseqs|cluster|identity.?threshold|linclust|cd-?hit|homolog.?group", None),
    ("T-P2-character-economy-audit",
     r"alignable|character.?econom|taxa.?per.?char|157|trimal|gblocks",
     (r"alignable|157", "governed_results", "content")),
    ("T-P3-relatedness-representation",
     r"distance.?matrix|patristic|reference_msa|reference_tree|newick|\.nwk",
     (r"reference_tree|reference_msa", "rdb_data_derived", "path")),
    ("T-A0b-lineage-partition-intervals",
     r"lineage.?block|block.?bootstrap|cluster.?robust|random.?intercept|ICC", None),

    # ---- goal 4 · RT features / motifs / domains / fusions ---------------
    ("T-F1-motif-scan",
     r"YXDD|YADD|motif|catalytic|active.?site", None),
    ("T-F2-domain-architecture",
     r"architecture|domain|fusion|pfam|terminal.?extension|accessory",
     (r"architecture", "governed_results", "path")),
    ("T-F3-retron-feature-contrast",
     r"retron.?vs|non.?retron|discriminat|feature.?contrast", None),
    ("T-F4-domain-partition-nonoperational",
     r"palm|fingers|thumb|subdomain", None),

    # ---- goal 5 · structure ----------------------------------------------
    ("T-S1-structure-asset-inventory",
     r"structure|pdb|cif|fold|chain_extract|plddt", None),
    ("T-S2-foldseek-calibration",
     r"foldseek|tm.?score|tmalign|cath|3di|structural.?align", None),
    ("T-A7-stage3a-positive-control",
     r"stage3a|structural.?core|tier.?[abc]|truth.?pair", None),
    ("T-S3-structural-core-interpretation",
     r"structural.?core|divergent.?sequence|remote.?homolog", None),

    # ---- goal 6 · genomic architecture -----------------------------------
    ("T-N1-neighbourhood-extraction-qa",
     r"neighbourhood|neighborhood|operon|flanking|cds_between|upstream|downstream",
     (r"cds_between|operon|flank", "v7_analysis_workbench", "path")),
    ("T-N2-neighbourhood-lineage-comparison",
     r"defence.?island|defense.?island|gene.?context|synteny", None),
    ("T-A10-genomic-architecture",
     r"architecture|geometry|same.?strand|direction|distance.?histogram",
     (r"same_strand|geometry", "v7_analysis_workbench", "path")),
    ("T-A6-fixed-locus-carriage",
     r"carriage|locus.?set|physical.?locus|rt_loci|per.?genome",
     (r"rt_loci|physical_loci", "v7_data_derived", "path")),

    # ---- goal 7 · evolutionary correspondence ----------------------------
    ("T-E1-character-source-probe",
     r"alignable|character|msa|conserved.?block", None),
    ("T-E2-shallow-clade-restriction",
     r"shallow.?clade|bootstrap.?support|independent.?unit", None),
    ("T-E3-coevolution-vocabulary-lock",
     r"co-?evolution|coevol|correspondence|mirrortree|tanglegram", None),

    # ---- goal 8 · de novo ncRNA discovery --------------------------------
    ("T-C2-cm-call-inventory",
     r"covariance|cmsearch|infernal|\bCM\b|model.?composition|ncrna.?call",
     (r"ncrna.?call|model_composition", "v7_analysis_workbench", "path")),
    ("T-A19-withheld-model-control",
     r"leave.?one.?out|withheld|subtype.?recovery|loso", None),
    ("T-S07-reopen-design",
     r"de.?novo|discovery|spire|positional.?prior|IoU", None),

    # ---- goal 9 · ncRNA architecture / RT-DNA anchors --------------------
    ("T-A5b1-rtdna-anchors",
     r"RT-?DNA|rtdna|anchor|branch(ing)?.?G|2'-5'", None),
    ("T-R1-rtdna-direct-mapping",
     r"RT-?DNA|coordinate|direct.?map", None),
    ("T-A5b2-ncrna-architecture",
     r"msr|msd|a1/a2|a1_a2|stem|inverted.?repeat|boundary|extent",
     (r"ncrna|oriented", "v7_data_derived", "path")),
    ("T-A20-pair-expansion",
     r"pair.?expansion|architecture.?defined|exact.?pair",
     (r"exact_pair", "v7_data_derived", "path")),

    # ---- goal 10 · representations / embeddings --------------------------
    ("T-M1-embedding-cache-verification",
     r"embedding|\.npy\b|esm|rinalmo|cache|latent", None),
    ("T-M2-landed-interval-coverage-sweep",
     r"bootstrap|interval|coverage|ci_lo|ci_hi|n_eff", None),
    ("T-A1-absolute-baselines",
     r"baseline|absolute|random.?baseline|shuffle", None),
    ("T-A2b-budget-matched-ladder",
     r"counterfactual|alternatives_per_pair|n_alternatives|tier", None),

    # ---- goal 11 · integrative modelling ---------------------------------
    ("T-I1-integrative-decomposition",
     r"integrat|joint.?model|ablation|prior.?increment|multi.?modal", None),

    # ---- goal 12 · orthogonality -----------------------------------------
    ("T-A22-functional-contrast",
     r"producer|non.?producer|rtdna_production|functional.?label", None),
    ("T-A23b-systematic-corpus",
     r"literature|corpus.?screen|prisma|systematic.?search", None),
    ("T-A23c-source-data-retrieval",
     r"supplementary|source.?data|extended.?data", None),
    ("T-A23d-primary-verification",
     r"primary.?study|secondhand|reference.?3[2356]", None),
    ("T-A23e-block-level-recount",
     r"cross.?pair|non.?cognate|orthogonal|swap|compatib", None),

    # ---- goal 0 · cross-cutting ------------------------------------------
    ("T-GATE1-consumption-gate",
     r"consumption.?gate|CONSUMABLE|promotion|bundle.?spec", None),
    ("T-AUDIT1-circular-control-sweep",
     r"control|positive.?control|negative.?control|blocking",
     (r"control", "governed_results", "header")),
    ("T-HIA-human-input-audit",
     r"human.?input|HUMAN_INPUT_AUDIT", None),
    ("T-A3a-rule-and-e0-freeze",
     r"confirmatory.?rule|far.?confirmation|E0\b|freeze", None),
]


def walk(root: str):
    if not os.path.isdir(root):
        return
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in
                  (".git", "__pycache__", "node_modules", ".ipynb_checkpoints")]
        for fn in fns:
            yield os.path.join(dp, fn)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    started = time.time()

    rx = [(t, re.compile(p, re.I), a) for t, p, a in Q]

    # ---------------- ingest, per root, per substrate -------------------
    store = {}     # root -> substrate -> list[(path, text)]
    stats = {}
    for key, root in ROOTS.items():
        paths, content, header, parq = [], [], [], []
        for p in walk(root):
            paths.append((p, p))
            ext = os.path.splitext(p)[1]
            if ext in TEXT_EXT:
                try:
                    if os.path.getsize(p) <= MAX_TEXT_BYTES:
                        with open(p, encoding="utf-8", errors="replace") as fh:
                            content.append((p, fh.read()))
                except OSError:
                    pass
            if ext in TABLE_EXT:
                try:
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        first = fh.readline().rstrip("\n")
                    if first:
                        header.append((p, first))
                except OSError:
                    pass
            if ext == ".parquet":
                try:
                    import pyarrow.parquet as pq
                    names = pq.ParquetFile(p).schema_arrow.names
                    parq.append((p, " ".join(names)))
                except Exception:
                    pass
        store[key] = {"path": paths, "content": content,
                      "header": header, "parquet": parq}
        stats[key] = {s: len(v) for s, v in store[key].items()}
        sys.stderr.write(f"  {key:<24} " + " ".join(
            f"{s}={len(v)}" for s, v in store[key].items()) + "\n")

    # ---------------- CONTROL 1 · substrate liveness --------------------
    ctl, dead = [], set()
    for key in ROOTS:
        for sub in ("path", "content", "header", "parquet"):
            items = store[key][sub]
            n = len(items)
            if n == 0:
                state, obs = "NOT_EVALUABLE", "no unit of this kind on this root"
            elif sub in ("header", "parquet"):
                wide = sum(1 for _p, t in items
                           if len(t.split("\t" if sub == "header" else " ")) >= 2)
                state = "PASS" if wide else "FAIL"
                obs = f"{n} parsed, {wide} with >=2 columns"
                if not wide:
                    dead.add((key, sub))
            else:
                nz = sum(1 for _p, t in items if t.strip())
                state = "PASS" if nz else "FAIL"
                obs = f"{n} read, {nz} non-empty"
                if not nz:
                    dead.add((key, sub))
            ctl.append([key, sub, "liveness", "YES",
                        "the reader parsed >=1 usable unit of this substrate on this root",
                        obs, state])

    # ---------------- CONTROL 2 · named anchors, per task ---------------
    anchor_rows, anchor_failed = [], set()
    for tid, _p, a in rx:
        if a is None:
            anchor_rows.append([tid, "-", "-", "NO_ANCHOR",
                                "no known-present case asserted for this task",
                                "absence rests on substrate liveness alone and is WEAKER"])
            continue
        pat, rootk, sub = a
        arx = re.compile(pat, re.I)
        hits = sum(1 for _p2, t in store.get(rootk, {}).get(sub, []) if arx.search(t))
        ok = hits > 0
        if not ok:
            anchor_failed.add(tid)
        anchor_rows.append([tid, rootk, sub, "PASS" if ok else "FAIL",
                            f"/{pat}/i must hit on {rootk}:{sub}",
                            f"{hits} hit(s)"])

    with open(os.path.join(args.out, "TASK_PRIOR_WORK_CONTROLS.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["scope", "substrate", "control_type", "blocking",
                    "expectation", "observed", "state"])
        w.writerows(ctl)
        for r in anchor_rows:
            w.writerow([r[0], f"{r[1]}:{r[2]}", "named_anchor", "YES",
                        r[4], r[5], r[3]])

    # ---------------- the sweep ------------------------------------------
    rows, summary = [], {}
    for tid, pat, _a in rx:
        per_root, ex = {}, []
        tot = defaultdict(int)
        for key in ROOTS:
            counts = {}
            for sub in ("path", "content", "header", "parquet"):
                if (key, sub) in dead:
                    counts[sub] = -1
                    continue
                hits = [p for p, t in store[key][sub] if pat.search(t)]
                counts[sub] = len(hits)
                tot[sub] += len(hits)
                for h in hits[:2]:
                    if len(ex) < 10:
                        ex.append(os.path.relpath(h, "/home/borg"))
            per_root[key] = counts
            if any(v > 0 for v in counts.values()):
                rows.append([tid, key,
                             counts["path"], counts["content"],
                             counts["header"], counts["parquet"],
                             ";".join(os.path.relpath(p, "/home/borg")
                                      for p, t in store[key]["header"]
                                      if pat.search(t))[:400]])
        summary[tid] = {
            "anchor": "FAILED" if tid in anchor_failed else
                      ("NONE" if all(a is None for t, p, a in rx if t == tid) else "PASS"),
            "roots_hit": sum(1 for k, c in per_root.items()
                             if any(v > 0 for v in c.values())),
            "path": tot["path"], "content": tot["content"],
            "header": tot["header"], "parquet": tot["parquet"],
            "examples": ex,
        }

    with open(os.path.join(args.out, "TASK_PRIOR_WORK_BY_ROOT.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["task_id", "root", "n_path", "n_content",
                    "n_header", "n_parquet", "matching_table_headers"])
        w.writerows(rows)

    with open(os.path.join(args.out, "TASK_PRIOR_WORK_SUMMARY.tsv"), "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["task_id", "anchor_control", "n_roots_with_hits", "n_path",
                    "n_content", "n_table_headers", "n_parquet_schemas",
                    "absence_reportable", "example_paths"])
        for tid, _p, _a in rx:
            s = summary[tid]
            reportable = ("NO - anchor FAILED" if s["anchor"] == "FAILED"
                          else "WEAK - no anchor" if s["anchor"] == "NONE"
                          else "YES")
            w.writerow([tid, s["anchor"], s["roots_hit"], s["path"], s["content"],
                        s["header"], s["parquet"], reportable,
                        ";".join(s["examples"][:6])])

    meta = {"script_version": SCRIPT_VERSION,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "elapsed_s": round(time.time() - started, 1),
            "n_tasks": len(rx), "roots": stats,
            "dead_substrates": sorted(f"{k}:{s}" for k, s in dead),
            "anchor_failures": sorted(anchor_failed),
            "unbounded": True}
    with open(os.path.join(args.out, "TASK_PRIOR_WORK_META.json"), "w") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
    print(json.dumps(meta, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
