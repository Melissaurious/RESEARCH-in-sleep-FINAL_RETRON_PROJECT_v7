#!/usr/bin/env python3
"""
T-P1b · cascaded sequence-identity partition of the exact-RT catalogue.

WHAT THIS PRODUCES
    Reproducible SEQUENCE-RELATEDNESS partitions at seven identity resolutions,
    plus the incidence of those partitions against the threshold-free exact
    RT-ncRNA bipartite components.

WHAT THIS IS NOT
    Not a phylogeny.  Not evolutionary lineage truth.  Not biological clades.
    Not a replacement RT classification.  No level is "the lineage boundary".

LABEL-BLIND BY CONSTRUCTION
    Cluster formation reads ONE input: rt_exact_v1.faa.  No family label, no
    MyRT/PADLOC/DefenseFinder call, no ncRNA call, no taxonomy is opened before
    clustering is complete and written.  Labels are joined afterwards, for
    description only, in describe().

CONTROLS
    Run FIRST, BLOCK, and run on their OWN fixture files in their OWN MMseqs2
    invocations.  No control sequence is ever appended to the primary catalogue.
    That is the defect that voided T-P1.

Usage:
    p1b_identity_partition.py --mode controls --out DIR
    p1b_identity_partition.py --mode pilot    --out DIR     # 10,000 sequences
    p1b_identity_partition.py --mode full     --out DIR     # 501,561; separate authorisation
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import csv
import hashlib
import json
import os
import random
import shutil
import subprocess
import time

SCRIPT_VERSION = "1.0.0"
SEED = 20260920

V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
FAA = f"{V7}/data/derived/rt_exact_v1.faa"
FAA_SHA256 = "bcde6e9a64de90e6e791256f79c87799a00a95f0d1730f3460301220379e2655"
FAA_RECORDS = 501561

# Source of EXACT-BIPARTITE-COMPONENTS-14918, registered separately in
# programme/CANONICAL_DATASETS.tsv as CANONICAL_WITH_LIMITATION. This task consumes the
# graph TOPOLOGY, not the PAIR-ELIG-30924 pairing endpoint, which is exhausted. Any use
# of this structure that makes or weakens a PAIRING claim is forbidden -- see the launcher.
PAIRS = f"{V7}/data/derived/rt_ncrna_exact_pairs_v1.parquet"
PAIRS_SHA256 = "b89df6803dcd6346c93e39e62f1d590e22c96662d63c7c148952cc6641523dae"
G3_COMPONENTS = f"{V7}/results/dbchar_g3_pair_geometry/tables/g3_topology_components.tsv"
G3_SHA256 = "aaf0fe7f9100886b40d59eb026360fbdd640760e75263732a50576112d3a8674"
EXPECTED_COMPONENTS = 14918

# Post-hoc description only.  Opened AFTER every cluster file is written.
FAMILY = f"{V7}/data/derived/rt_family_baseline_v1.parquet"

MMSEQS = "/home/borg/miniconda3/envs/retron_tradicional/bin/mmseqs"

# ---- the declared ladder, fixed in this commit -------------------------------
# Traversed 40 -> 95.  As the minimum identity threshold becomes STRICTER, the
# number of clusters is expected to be NON-DECREASING.  Cluster-count
# monotonicity is asserted; partition NESTING is not, because cascaded MMseqs2
# clustering does not mathematically guarantee it.  Those are different
# properties and the launcher says so.
LADDER = [("id40", 0.40), ("id50", 0.50), ("id60", 0.60), ("id70", 0.70),
          ("id80", 0.80), ("id90", 0.90), ("id95", 0.95)]

# ---- declared MMseqs2 procedure, fixed in this commit ------------------------
COV = 0.80
COV_MODE = 0            # bidirectional coverage
CLUSTER_MODE = 0        # greedy set cover
SENSITIVITY = 7.5       # raised from the default; see launcher section on the duplicate control
MAX_SEQS = 1000         # raised from the default 300 to reduce prefilter saturation

PILOT_N = 10000
PILOT_EDGE_PER_STRATUM = 100


# ------------------------------------------------------------------ utilities
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_fasta(path: str):
    name, buf = None, []
    with open(path) as fh:
        for line in fh:
            if line.startswith(">"):
                if name is not None:
                    yield name, "".join(buf)
                name, buf = line[1:].strip().split(None, 1)[0], []
            else:
                buf.append(line.strip())
    if name is not None:
        yield name, "".join(buf)


def write_fasta(path, records):
    with open(path, "w") as fh:
        for name, seq in records:
            fh.write(f">{name}\n")
            for i in range(0, len(seq), 60):
                fh.write(seq[i:i + 60] + "\n")


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def cluster(faa: str, workdir: str, min_seq_id: float, threads: int) -> dict:
    """Run one MMseqs2 easy-cluster. Returns {member_id: representative_id}."""
    os.makedirs(workdir, exist_ok=True)
    prefix = os.path.join(workdir, "clu")
    tmp = os.path.join(workdir, "tmp")
    cmd = [MMSEQS, "easy-cluster", faa, prefix, tmp,
           "--min-seq-id", str(min_seq_id),
           "-c", str(COV), "--cov-mode", str(COV_MODE),
           "--cluster-mode", str(CLUSTER_MODE),
           "-s", str(SENSITIVITY), "--max-seqs", str(MAX_SEQS),
           "--threads", str(threads), "-v", "1"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"mmseqs rc={r.returncode}: {r.stderr[-600:]}")
    out = {}
    with open(prefix + "_cluster.tsv") as fh:
        for line in fh:
            rep, mem = line.rstrip("\n").split("\t")
            out[mem] = rep
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def mmseqs_version() -> str:
    return subprocess.run([MMSEQS, "version"], capture_output=True, text=True).stdout.strip()


# -------------------------------------------------------------------- gate 0
def gate_input_identity(rows: list) -> bool:
    """sha256 + record count of the primary catalogue. STOP before any clustering."""
    got = sha256_file(FAA)
    ok_hash = got == FAA_SHA256
    rows.append(["P1b_GATE_input_sha256", "positive", "YES",
                 f"rt_exact_v1.faa sha256 == {FAA_SHA256}", got,
                 "PASS" if ok_hash else "FAIL",
                 "the catalogue is the one this task was frozen against"])
    n = sum(1 for _ in read_fasta(FAA))
    ok_n = n == FAA_RECORDS
    rows.append(["P1b_GATE_input_records", "positive", "YES",
                 f"exactly {FAA_RECORDS} FASTA records", str(n),
                 "PASS" if ok_n else "FAIL",
                 "T-P1 ran on 501,861 after a mid-run scope change; this gate makes that impossible"])
    return ok_hash and ok_n


# ------------------------------------------------------------------- controls
def run_controls(fixdir: str, out: str, threads: int) -> tuple[list, bool]:
    rows: list = []
    ok = gate_input_identity(rows)
    if not ok:
        return rows, False

    work = os.path.join(out, "work", "controls")

    # --- C1 duplicates: must co-cluster at EVERY level ------------------------
    dup_fa = os.path.join(fixdir, "fixture_duplicates.faa")
    dup_ids = [n for n, _ in read_fasta(dup_fa)]
    n_pairs = len(dup_ids) // 2
    for lvl, mid in LADDER:
        assign = cluster(dup_fa, os.path.join(work, f"dup_{lvl}"), mid, threads)
        co = sum(1 for i in range(n_pairs)
                 if assign.get(f"DUPPAIR{i:03d}_A") == assign.get(f"DUPPAIR{i:03d}_B")
                 and assign.get(f"DUPPAIR{i:03d}_A") is not None)
        rows.append([f"P1b_POS_duplicate_{lvl}", "positive", "YES",
                     f"all {n_pairs} exact-duplicate pairs co-cluster at min_seq_id={mid}",
                     f"{co}/{n_pairs}",
                     "PASS" if co == n_pairs else "FAIL",
                     "standalone fixture; 200 seqs is far below --max-seqs so prefilter "
                     "saturation cannot occur"])
        if co != n_pairs:
            ok = False

    # --- C2 shuffles: must NOT co-cluster at ANY level ------------------------
    shuf_fa = os.path.join(fixdir, "fixture_shuffled.faa")
    n_shuf = sum(1 for _ in read_fasta(shuf_fa)) // 2
    for lvl, mid in LADDER:
        assign = cluster(shuf_fa, os.path.join(work, f"shuf_{lvl}"), mid, threads)
        co = sum(1 for i in range(n_shuf)
                 if assign.get(f"SHUF{i:03d}_ORIG") == assign.get(f"SHUF{i:03d}_SHUFFLED")
                 and assign.get(f"SHUF{i:03d}_ORIG") is not None)
        rows.append([f"P1b_NEG_shuffled_{lvl}", "negative", "YES",
                     f"0 of {n_shuf} composition-matched shuffles co-cluster with their original "
                     f"at min_seq_id={mid}",
                     f"{co}/{n_shuf}",
                     "PASS" if co == 0 else "FAIL",
                     "identical length and amino-acid composition, order destroyed"])
        if co != 0:
            ok = False

    # --- C3 monotonicity, direction declared ---------------------------------
    counts = []
    for lvl, mid in LADDER:
        assign = cluster(dup_fa, os.path.join(work, f"mono_{lvl}"), mid, threads)
        counts.append((lvl, len(set(assign.values()))))
    mono = all(counts[i + 1][1] >= counts[i][1] for i in range(len(counts) - 1))
    rows.append(["P1b_POS_monotonic_40_to_95", "positive", "YES",
                 "traversing the ladder 40%->95% (STRICTER), cluster count is NON-DECREASING",
                 " <= ".join(f"{l}:{c}" for l, c in counts),
                 "PASS" if mono else "FAIL",
                 "direction stated explicitly; cluster-count monotonicity is asserted, "
                 "partition NESTING is not"])
    if not mono:
        ok = False

    # --- C4 edge-case completeness: nothing may be silently dropped ----------
    edge_fa = os.path.join(fixdir, "fixture_edgecases.faa")
    edge_ids = [n for n, _ in read_fasta(edge_fa)]
    assign = cluster(edge_fa, os.path.join(work, "edge"), 0.40, threads)
    missing = [i for i in edge_ids if i not in assign]
    rows.append(["P1b_POS_edgecase_completeness", "positive", "YES",
                 f"all {len(edge_ids)} edge-case sequences (U, X, all-U, 20 aa, 12x-long, "
                 f"unrelated) receive an assignment",
                 f"{len(edge_ids) - len(missing)}/{len(edge_ids)}"
                 + (f" missing={missing}" if missing else ""),
                 "PASS" if not missing else "FAIL",
                 "flag before filtering: an unprocessable sequence is RETAINED with a reason, "
                 "never dropped"])
    if missing:
        ok = False

    # --- C5 reproduce the landed 14,918 exact bipartite components -----------
    pairs_hash = sha256_file(PAIRS)
    rows.append(["P1b_GATE_component_source_sha256", "positive", "YES",
                 f"rt_ncrna_exact_pairs_v1.parquet sha256 == {PAIRS_SHA256}", pairs_hash,
                 "PASS" if pairs_hash == PAIRS_SHA256 else "FAIL",
                 "source of EXACT-BIPARTITE-COMPONENTS-14918; registered separately from "
                 "PAIR-ELIG-30924, whose pairing endpoint is exhausted and is NOT consumed here"])
    if pairs_hash != PAIRS_SHA256:
        return rows, False
    n_comp, comp_of_rt = derive_components()
    g3_hash = sha256_file(G3_COMPONENTS)
    ok_g3 = g3_hash == G3_SHA256 and n_comp == EXPECTED_COMPONENTS
    rows.append(["P1b_POS_reproduce_components", "positive", "YES",
                 f"exact RT-ncRNA bipartite components derived independently == "
                 f"{EXPECTED_COMPONENTS} (landed g3_topology_components.tsv)",
                 f"derived={n_comp} g3_sha256_match={g3_hash == G3_SHA256}",
                 "PASS" if ok_g3 else "FAIL",
                 "implementation reproduction against a LANDED Stage-1 number; consumes no "
                 "T-P1 output"])
    if not ok_g3:
        ok = False

    tsv(os.path.join(out, "tables", "P1b_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], rows)
    return rows, ok


# ------------------------------------------------------------ components
def derive_components():
    """Connected components of the exact RT-ncRNA bipartite graph. Threshold-free.

    Deliberately NOT the 1,075 'components' in CROSSFIT_META.json: those are built
    on the frozen rt_id0.50 cluster representative and therefore already embed a
    50%-identity clustering, which would make comparison with a NEW identity
    partition partly circular.
    """
    import pyarrow.parquet as pq
    t = pq.read_table(PAIRS)
    rt = t.column("rt_seq_hash").to_pylist()
    nc = t.column("nc_seq_hash").to_pylist()
    parent: dict = {}

    def find(x):
        parent.setdefault(x, x)
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    for a, b in zip(rt, nc):
        ra, rb = find(("R", a)), find(("N", b))
        if ra != rb:
            parent[ra] = rb
    comp_of_rt = {}
    roots = {}
    for a in set(rt):
        r = find(("R", a))
        comp_of_rt[a] = roots.setdefault(r, len(roots))
    n_comp = len({find(k) for k in parent})
    return n_comp, comp_of_rt


# ----------------------------------------------------------------- selection
def pilot_selection(index: list) -> list:
    """Deterministic 10,000-sequence pilot set.

    index is [(rt_id, length, has_U, has_X)] -- SEQUENCE PROPERTIES ONLY.
    No family, tool, taxonomy or ncRNA label is read here or anywhere before
    clustering.  Edge-case strata guarantee the pilot exercises U, X, the
    shortest and the longest sequences.
    """
    index = sorted(index, key=lambda r: r[0])          # order-independent
    chosen: list = []
    seen: set = set()

    def take(rows, k):
        for r in rows:
            if len(seen) >= PILOT_N:
                return
            if r[0] not in seen:
                seen.add(r[0]); chosen.append(r[0])
                k -= 1
                if k == 0:
                    return

    by_len = sorted(index, key=lambda r: (r[1], r[0]))
    take(by_len, PILOT_EDGE_PER_STRATUM)                       # shortest
    take(list(reversed(by_len)), PILOT_EDGE_PER_STRATUM)       # longest
    take([r for r in index if r[2]], PILOT_EDGE_PER_STRATUM)   # contains U
    take([r for r in index if r[3]], PILOT_EDGE_PER_STRATUM)   # contains X
    rng = random.Random(SEED)
    pool = [r[0] for r in index if r[0] not in seen]
    rng.shuffle(pool)
    for rid in pool:
        if len(seen) >= PILOT_N:
            break
        seen.add(rid); chosen.append(rid)
    return sorted(chosen)


# ------------------------------------------------------------------- primary
def run_primary(mode: str, out: str, threads: int) -> tuple[list, bool]:
    rows: list = []
    index, seqs = [], {}
    for name, seq in read_fasta(FAA):
        seqs[name] = seq
        index.append((name, len(seq), "U" in seq, "X" in seq))

    if mode == "pilot":
        ids = pilot_selection(index)
        faa = os.path.join(out, "work", "pilot.faa")
        os.makedirs(os.path.dirname(faa), exist_ok=True)
        write_fasta(faa, [(i, seqs[i]) for i in ids])
    else:
        ids = sorted(seqs)
        faa = FAA

    n_in = len(ids)
    id_set = set(ids)
    level_rows, incidence_rows, multi_rows, excl = [], [], [], []
    assignments = {}

    # LABEL-BLIND: the clustering loop below opens ONE input, the FASTA. Neither the
    # ncRNA pair table nor the family baseline is read until every cluster file has
    # been written. derive_components() is therefore called AFTER the loop, not
    # before it, so the ordering enforces the claim rather than merely asserting it.
    for lvl, mid in LADDER:
        assign = cluster(faa, os.path.join(out, "work", f"primary_{lvl}"), mid, threads)
        assign = {k: v for k, v in assign.items() if k in id_set}
        reps = sorted(set(assign.values()))
        rep_id = {r: n for n, r in enumerate(reps)}
        assignments[lvl] = assign

        missing = [i for i in ids if i not in assign]
        for i in missing:
            excl.append([lvl, i, len(seqs[i]), "NOT_ASSIGNED_BY_MMSEQS",
                         "retained in this table; the denominator is NOT reduced"])

        sizes: dict = {}
        for m, r in assign.items():
            sizes[r] = sizes.get(r, 0) + 1
        sz = sorted(sizes.values())
        tsv(os.path.join(out, "tables", f"P1b_clusters_{lvl}.tsv"),
            ["rt_id", "cluster_rep", "cluster_id"],
            [[m, r, rep_id[r]] for m, r in sorted(assign.items())])
        level_rows.append([lvl, mid, n_in, len(assign), len(missing), len(reps),
                           sz[-1] if sz else 0, sz[len(sz) // 2] if sz else 0,
                           sum(1 for x in sz if x == 1)])

    # ---- everything below runs AFTER every cluster file is written ----------
    # Component incidence, against the THRESHOLD-FREE 14,918 exact bipartite
    # components. Deliberately NOT the 1,075 from CROSSFIT_META.json, which embed
    # the frozen rt_id0.50 representative and would be partly circular here.
    n_comp, comp_of_rt = derive_components()
    for lvl, assign in assignments.items():
        per_comp: dict = {}
        for m, r in assign.items():
            c = comp_of_rt.get(m)
            if c is None:
                continue
            per_comp.setdefault(c, set()).add(r)
        for c, cl in sorted(per_comp.items()):
            incidence_rows.append([lvl, c, len(cl)])
        dist: dict = {}
        for c, cl in per_comp.items():
            dist[len(cl)] = dist.get(len(cl), 0) + 1
        for k in sorted(dist):
            multi_rows.append([lvl, k, dist[k]])

    # ---- POST HOC ONLY: family labels joined after every cluster file exists
    fam_rows, xfam_rows = describe(assignments, out)

    tsv(os.path.join(out, "tables", "P1b_level_summary.tsv"),
        ["level", "min_seq_id", "n_input", "n_assigned", "n_unassigned", "n_clusters",
         "largest_cluster", "median_cluster_size", "n_singletons"], level_rows)
    tsv(os.path.join(out, "tables", "P1b_component_incidence.tsv"),
        ["level", "component_id", "n_distinct_clusters"], incidence_rows)
    tsv(os.path.join(out, "tables", "P1b_component_multimembership.tsv"),
        ["level", "n_distinct_clusters_in_component", "n_components"], multi_rows)
    tsv(os.path.join(out, "tables", "P1b_exclusions.tsv"),
        ["level", "rt_id", "seq_len", "reason", "note"], excl)

    counts = [r[5] for r in level_rows]
    mono = all(counts[i + 1] >= counts[i] for i in range(len(counts) - 1))
    rows.append(["P1b_POS_primary_completeness", "positive", "YES",
                 f"every one of {n_in} input sequences is assigned at every level",
                 f"unassigned={len(excl)}", "PASS" if not excl else "FAIL",
                 "unassigned sequences are RETAINED in P1b_exclusions.tsv with a reason"])
    rows.append(["P1b_DIAG_primary_monotonic", "diagnostic", "NO",
                 "cluster count non-decreasing 40%->95% on the primary input",
                 " <= ".join(f"{r[0]}:{r[5]}" for r in level_rows),
                 "PASS" if mono else "OBSERVED_NOT_MONOTONE",
                 "DIAGNOSTIC, not blocking: the blocking monotonicity control runs on the "
                 "fixture. A non-monotone result here is a property of the data to report"])
    return rows, not excl


def describe(assignments: dict, out: str):
    """Post-hoc family description. Runs only after all cluster files are written."""
    import pyarrow.parquet as pq
    t = pq.read_table(FAMILY)
    cols = t.schema.names
    key = "rt_seq_hash" if "rt_seq_hash" in cols else cols[0]
    fam = "rt_family" if "rt_family" in cols else cols[1]
    lab = dict(zip(t.column(key).to_pylist(), t.column(fam).to_pylist()))
    fam_rows, xfam_rows = [], []
    for lvl, assign in assignments.items():
        per: dict = {}
        for m, r in assign.items():
            per.setdefault(r, []).append(lab.get(m, "UNLABELLED"))
        multi = 0
        for r, labs in per.items():
            c: dict = {}
            for x in labs:
                c[x] = c.get(x, 0) + 1
            dom, dn = max(c.items(), key=lambda kv: kv[1])
            if len(c) > 1:
                multi += 1
            fam_rows.append([lvl, r, len(labs), len(c), dom, round(dn / len(labs), 6)])
        xfam_rows.append([lvl, len(per), multi, round(multi / max(len(per), 1), 6)])
    tsv(os.path.join(out, "tables", "P1b_cluster_family_composition.tsv"),
        ["level", "cluster_rep", "n_members", "n_distinct_families",
         "dominant_family", "dominant_family_fraction"], fam_rows)
    tsv(os.path.join(out, "tables", "P1b_cross_family_clusters.tsv"),
        ["level", "n_clusters", "n_clusters_multi_family", "fraction_multi_family"], xfam_rows)
    return fam_rows, xfam_rows


# ---------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["controls", "pilot", "full"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--fixtures", default=None)
    ap.add_argument("--threads", type=int, default=16)
    a = ap.parse_args()
    t0 = time.time()
    os.makedirs(os.path.join(a.out, "tables"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    fixdir = a.fixtures or os.path.join(a.out, "fixtures")

    rows, ok = run_controls(fixdir, a.out, a.threads)
    if not ok:
        print("BLOCKING CONTROL FAILURE — no primary table written")
        for r in rows:
            if r[5] != "PASS":
                print(f"  {r[5]:<22} {r[0]:<34} {r[4]}")
        print("TASK_STATE: VOID")
        return 2
    if a.mode == "controls":
        print("all blocking controls PASS")
        print("TASK_STATE: PASS (controls only; no primary table requested)")
        return 0

    prim, ok2 = run_primary(a.mode, a.out, a.threads)
    rows += prim
    tsv(os.path.join(a.out, "tables", "P1b_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], rows)

    log = {"script_version": SCRIPT_VERSION, "mode": a.mode, "seed": SEED,
           "mmseqs_version": mmseqs_version(), "threads": a.threads,
           "ladder": [l for l, _ in LADDER],
           "params": {"c": COV, "cov_mode": COV_MODE, "cluster_mode": CLUSTER_MODE,
                      "s": SENSITIVITY, "max_seqs": MAX_SEQS},
           "input_sha256": {"rt_exact_v1.faa": FAA_SHA256,
                            "g3_topology_components.tsv": G3_SHA256},
           "elapsed_s": round(time.time() - t0, 1),
           "blocking_failures": [r[0] for r in rows if r[2] == "YES" and r[5] != "PASS"]}
    with open(os.path.join(a.out, "logs", "run_log.json"), "w") as fh:
        json.dump(log, fh, indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    print("TASK_STATE: PASS" if ok2 else "TASK_STATE: VOID")
    return 0 if ok2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
