#!/usr/bin/env python3
"""Resolve every path, script, input and output named in RETRON_STAGES/05_mestre_replication.md.

Read-only. For files: size, mtime, sha256. For directories: n_files, total bytes and a manifest
sha256 over the sorted "relpath<TAB>sha256" lines (so two directories with the same manifest hash
hold byte-identical files under identical names). Paths the doc names relative to a stated root
are expanded against that root explicitly (ROOTED below) rather than guessed.
"""
import hashlib, os, re, sys, csv, datetime

DOC = "/home/borg/RETRON_STAGES/05_mestre_replication.md"
V4 = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4"
ROOT_A = "/home/borg/RETRON_CLAUDE_PART1/supplementary_material"
ROOT_B = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/supporting_material"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
IBEX = "/ibex/project/c2366/RETRONS/Mestre_replication"
PADLOC = "/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data"

# (section, path, what the doc claims about it). Relative names from the doc, expanded against
# the root the doc itself names for them.
ROOTED = []
for f in ["Supplementary_mestre_Tree.nwk", "Suppl_Toro_Tree.txt", "Supp_material_T1_R1_systematic_prediction.csv",
          "supp_material_systematic_prediction_paper.csv", "myRT-FastTree2.refpkg"]:
    ROOTED += [("6.2", f"{ROOT_A}/{f}", "D3 root A; doc: shared with root B, byte-identical"),
               ("6.2", f"{ROOT_B}/{f}", "D3 root B; doc: shared with root A, byte-identical")]
for f in ["Mestre_supplementary_material.csv", "toro_2014_Rt0-Rt7.FASTA"]:
    ROOTED += [("6.2", f"{ROOT_A}/{f}", "D3 root A only")]
for f in ["support.csv", "taxonomy_lookup.tsv", "gem_metadata.tsv"]:
    ROOTED += [("6.2", f"{ROOT_B}/{f}", "D3 root B only")]
for f in ["Supp_material_with_download_status.csv", "dead_accessions_manual_review.csv", "rescued_accessions.csv",
          "still_manual_review.csv", "wp_fix_report.csv", "retron_download.log", "retron_fix_wp.log", "retron_rescue.log"]:
    ROOTED += [("6.3", f"{D2}/{f}", "D2 download provenance; read before quoting any count")]
for f in ["genomes", "realpipe/results", "realpipe/processed_genomes.txt", "realpipe/stock_verdicts.tsv", "realpipe/logs",
          "realpipe/attempt1_failed_env", "ids_69.txt", "m8_mestre_validation_ibex.sh", "m10_mestre_realpipe_ibex.sh",
          "m11_relaxed_cm_axis.sh", "m12_extract_stock_verdicts.py", "m13_characterise_69.py", "hmm", "models"]:
    ROOTED += [("6.6", f"{IBEX}/{f}", "Ibex realpipe")]
for f in ["cm/padlocdb.cm", "cm_meta.txt", "sys"]:
    ROOTED += [("6.7", f"{PADLOC}/{f}", "PADLOC model")]
for s in ["s6_trees", "s3_object", "s4_motifs", "s7_classification", "s1_review", "rt0_rt7_lit_and_narrative", "crosscheck", "adversarial"]:
    ROOTED += [("6.5e/6.8", f"{V4}/ARIS_OUTPUT/{s}", "stage inheriting Mestre numbers (G74 etc.)")]
ROOTED += [("6.8", f"{V4}/ARIS_OUTPUT/crosscheck/FROZEN_DENOMINATORS.tsv", "doc: contains no Mestre/clade row"),
           ("6.5b", f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/tables/s5h_mestre_unmatched_groups_REGEN.tsv", "doc: use _REGEN"),
           ("6.5b", f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s5e_E4b_ruleD_on_our_trees.py", "paired arm"),
           ("6.5b", f"{V4}/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s7i_clade_support.py", "clade support"),
           ("6.7", "/home/borg/.macsyfinder/models/defense-finder-models/profiles", "DefenseFinder profiles (Retron subset)")]


def sha(p, bs=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(bs), b""):
            h.update(b)
    return h.hexdigest()


IBEX = {}  # path -> inventory row, from ibex_mestre_inventory.sh outputs (IBEX_INVENTORIES=dir1:dir2)
for d in filter(None, os.environ.get("IBEX_INVENTORIES", "").split(":")):
    for r in csv.DictReader(open(os.path.join(d, "inventory.tsv")), delimiter="\t"):
        IBEX[r["path"].rstrip("/")] = r
IBEX_ROOTS = sorted({p for p, r in IBEX.items() if r["type"] == "d"}, key=len)


def describe_ibex(p):
    """Resolve an Ibex path from a fetched inventory; UNINSPECTED if no inventory covers it."""
    covered = any(p == root or p.startswith(root + "/") for root in IBEX_ROOTS)
    r = IBEX.get(p)
    if r is None:
        return dict(exists="NO_IN_IBEX_INVENTORY" if covered else "IBEX_UNINSPECTED",
                    kind="", bytes="", n_files="", mtime="", sha256="")
    if r["type"] == "f":
        return dict(exists="YES_IBEX", kind="file", bytes=r["bytes"], n_files=1, mtime=r["mtime"][:19], sha256=r["sha256"])
    lines = sorted(f"{os.path.relpath(q, p)}\t{x['sha256']}" for q, x in IBEX.items() if x["type"] == "f" and q.startswith(p + "/"))
    tot = sum(int(x["bytes"]) for q, x in IBEX.items() if x["type"] == "f" and q.startswith(p + "/"))
    return dict(exists="YES_IBEX", kind="dir", bytes=tot, n_files=len(lines), mtime=r["mtime"][:19],
                sha256="manifest:" + hashlib.sha256("\n".join(lines).encode()).hexdigest())


def describe(p):
    # /ibex is not mounted on borg: an Ibex path is resolved from a fetched inventory, or is
    # UNINSPECTED — never "absent" on the strength of borg not seeing it.
    if p.startswith("/ibex/") and not os.path.isdir("/ibex"):
        return describe_ibex(p)
    if not os.path.lexists(p):
        return dict(exists="NO", kind="", bytes="", n_files="", mtime="", sha256="")
    if os.path.isfile(p):
        st = os.stat(p)
        return dict(exists="YES", kind="file", bytes=st.st_size, n_files=1,
                    mtime=datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"), sha256=sha(p))
    lines, tot, latest = [], 0, 0
    for root, _, files in os.walk(p):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.isfile(fp):
                continue
            st = os.stat(fp); tot += st.st_size; latest = max(latest, st.st_mtime)
            lines.append(f"{os.path.relpath(fp, p)}\t{sha(fp)}")
    lines.sort()
    return dict(exists="YES", kind="dir", bytes=tot, n_files=len(lines),
                mtime=datetime.datetime.fromtimestamp(latest).isoformat(timespec="seconds") if latest else "",
                sha256="manifest:" + hashlib.sha256("\n".join(lines).encode()).hexdigest())


def main(out):
    text = open(DOC).read()
    absolute = sorted({re.sub(r"[.:]+$", "", m) for m in re.findall(r"(?:/home/borg|/ibex)[^\s`|)*,]*", text)})
    rows = [("abs", p, "named verbatim in doc") for p in absolute] + ROOTED
    seen = set()
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["row", "doc_section", "path", "doc_claim", "exists", "kind", "bytes", "n_files", "latest_mtime", "sha256"])
        for i, (sec, p, claim) in enumerate(rows, 1):
            p = p.rstrip("/")
            if p in seen:
                continue
            seen.add(p)
            d = describe(p)
            w.writerow([f"S05_{i:03d}", sec, p, claim, d["exists"], d["kind"], d["bytes"], d["n_files"], d["mtime"], d["sha256"]])
            print(d["exists"], d["kind"], d["n_files"], p, file=sys.stderr, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
