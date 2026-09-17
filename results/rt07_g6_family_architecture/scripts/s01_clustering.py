#!/usr/bin/env python3
"""s01 - the sequence-relatedness resource: audit the prior one, then build a clean one.

Two products:
  tables/g6_clustering_reuse_audit.tsv   why no existing clustering resource is reusable
  work/eligible.faa + cluster TSVs       the minimum clean, LABEL-BLIND replacement

Label-blind means exactly that: the clustering input is amino-acid sequence and nothing else.
No family label, tool label, taxonomy or state call is used to build or tune it.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pyarrow.parquet as pq                                             # noqa: E402
from g6lib import (CLUSTER_COV, CLUSTER_COV_MODE, CLUSTER_PRIMARY,       # noqa: E402
                   CLUSTER_SENSITIVITY, DERIVED, G5, MMSEQS, TABLES, WORK,
                   sha256, write_tsv)

PRIOR = ("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/clustering_experiments/"
         "cluster_work/full_id0.90_cluster.tsv".replace("0.90", "0.9"))
PRIOR_SCRIPT = ("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_SCRIPTS/"
                "clustering_experiments/run_clustering_experiments.sh")

AUDIT_COLUMNS = ["candidate", "audit_item", "finding", "verdict", "why_it_matters"]


def audit_prior():
    members = set()
    n_rows = 0
    if os.path.exists(PRIOR):
        for line in open(PRIOR):
            p = line.rstrip("\n").split("\t")
            n_rows += 1
            if len(p) > 1:
                members.add(p[1])
    example = sorted(members)[0] if members else "n/a"
    rows = [
        dict(candidate=PRIOR, audit_item="input population",
             finding=f"{n_rows} rows, {len(members)} unique members. The producing script "
                     f"describes it as 'the 397K assembled set'.",
             verdict="FAIL",
             why_it_matters="g6's denominators are 369,381 eligible / 354,102 inspectable exact "
                            "RTs. This is a different population from a different project "
                            "version, so its clusters do not partition g6's population."),
        dict(candidate=PRIOR, audit_item="identifier space",
             finding=f"members are contig/locus-style identifiers, e.g. '{example}'. Not "
                     f"rt_hash.",
             verdict="FAIL",
             why_it_matters="Every g5 join is on rt_hash (sha256 of the amino-acid sequence, "
                            "computed in THIS project). The research contract records that "
                            "inherited rt_hash is not a sequence hash and that no rt_hash to "
                            "locus link exists, so these clusters cannot be attached to the "
                            "g6 population at all without new derivation work."),
        dict(candidate=PRIOR, audit_item="tool and version",
             finding="mmseqs easy-linclust with --min-seq-id {0.3,0.5,0.7,0.9} -c 0.8 "
                     "--cov-mode 1. Parameters are recorded in the script; NO VERSION is "
                     "pinned anywhere - the script only states 'requires mmseqs2 in PATH'.",
             verdict="FAIL",
             why_it_matters="An unpinned clustering tool is not reproducible, and a "
                            "relatedness control that cannot be reproduced cannot support a "
                            "denominator."),
        dict(candidate=PRIOR, audit_item="identity / coverage / cov-mode",
             finding="identity swept 0.3-0.9; coverage -c 0.8; --cov-mode 1 (coverage of "
                     "target only).",
             verdict="RECORDED",
             why_it_matters="Parameters are legible, which is why the audit could be bounded. "
                            "cov-mode 1 is one-directional; this gate uses --cov-mode 0 "
                            "(bidirectional) as the stricter redundancy criterion and does not "
                            "inherit the prior choice."),
        dict(candidate=PRIOR, audit_item="reproducibility",
             finding="the input FASTA is neither hashed nor registered; the producing "
                     "extraction directory is a runtime argument, not a recorded artifact.",
             verdict="FAIL",
             why_it_matters="The exact input cannot be reconstructed, so the clustering cannot "
                            "be re-derived or checked."),
        dict(candidate="ALL CANDIDATES", audit_item="overall",
             finding="No existing clustering resource partitions the g6 population on the g6 "
                     "key with a pinned tool.",
             verdict="DO-NOT-USE",
             why_it_matters="A minimum clean label-blind resource is built in this gate "
                            "instead. Audit bounded to what reuse required (input population, "
                            "hashes, tool/version, identity/coverage/cov-mode, "
                            "reproducibility); nothing further was inspected."),
    ]
    write_tsv(os.path.join(TABLES, "g6_clustering_reuse_audit.tsv"), AUDIT_COLUMNS, rows)
    return rows


def build_eligible_fasta():
    """Exactly the eligible exact RTs, keyed by rt_hash. Label-blind by construction."""
    cw = pq.read_table(os.path.join(G5, "g5_metadata_crosswalk.parquet"),
                       columns=["rt_hash", "in_g5_eligible"]).to_pylist()
    elig = {r["rt_hash"] for r in cw if r["in_g5_eligible"]}
    out = os.path.join(WORK, "eligible.faa")
    src = os.path.join(DERIVED, "rt_exact_v1.faa")
    n = 0
    with open(out, "w") as fh:
        keep = False
        for line in open(src):
            if line.startswith(">"):
                keep = line[1:].strip().split()[0] in elig
                if keep:
                    n += 1
            if keep:
                fh.write(line)
    if n != len(elig):
        raise SystemExit(f"s01: wrote {n} sequences, expected {len(elig)}")
    print(f"s01: eligible.faa {n} sequences  sha256 {sha256(out)[:16]}...")
    return out, n


def cluster(faa, ident):
    tag = f"clu_id{ident}"
    pref = os.path.join(WORK, tag)
    tmp = os.path.join(WORK, f"tmp_{tag}")
    res = pref + "_cluster.tsv"
    if not os.path.exists(res):
        subprocess.run([MMSEQS, "easy-linclust", faa, pref, tmp,
                        "--min-seq-id", ident, "-c", CLUSTER_COV,
                        "--cov-mode", CLUSTER_COV_MODE, "--threads", "8"],
                       check=True, stdout=subprocess.DEVNULL)
    pairs = [ln.rstrip("\n").split("\t") for ln in open(res)]
    reps = {p[0] for p in pairs if len(p) > 1}
    print(f"s01: identity {ident} -> {len(reps)} clusters over {len(pairs)} members")
    return res, len(reps), len(pairs)


def main():
    os.makedirs(WORK, exist_ok=True)
    audit_prior()
    faa, n = build_eligible_fasta()

    ver = subprocess.run([MMSEQS, "version"], capture_output=True, text=True).stdout.strip()
    rows = []
    for ident in [CLUSTER_PRIMARY] + CLUSTER_SENSITIVITY:
        path, n_clu, n_mem = cluster(faa, ident)
        rows.append(dict(identity=ident, coverage=CLUSTER_COV, cov_mode=CLUSTER_COV_MODE,
                         role="PRIMARY" if ident == CLUSTER_PRIMARY else "SENSITIVITY",
                         n_input_sequences=n, n_members_clustered=n_mem, n_clusters=n_clu,
                         collapse_ratio=f"{n_clu / n:.4f}",
                         tool=f"mmseqs {ver}", input_sha256=sha256(faa),
                         cluster_tsv=os.path.relpath(path, WORK),
                         label_blind="YES - input is amino-acid sequence only; no family, "
                                     "tool, taxonomy or state call participates",
                         unit="cluster", denominator=f"{n} eligible exact RTs"))
    write_tsv(os.path.join(TABLES, "g6_clustering_resource.tsv"),
              ["identity", "coverage", "cov_mode", "role", "n_input_sequences",
               "n_members_clustered", "n_clusters", "collapse_ratio", "tool", "input_sha256",
               "cluster_tsv", "label_blind", "unit", "denominator"], rows)
    print(f"s01: clustering resource built with mmseqs {ver}, pinned and recorded")


if __name__ == "__main__":
    main()
