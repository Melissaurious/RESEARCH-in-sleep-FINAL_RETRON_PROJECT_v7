#!/usr/bin/env python
"""embed_g2/s06 - FREEZE the primary split. Operator decision 2026-09-18, Option A.

Produces the frozen split manifest and the assignment it authorises. Run ONCE, before any
downstream compatibility result is examined. s07 then reconstructs the split from this
manifest and asserts exact equality.

WHAT IS FROZEN
  RT clustering     mmseqs easy-cluster --min-seq-id 0.50 -c 0.8 --cov-mode 0
  ncRNA clustering  cd-hit-est -c 0.80 -aS 0.8 -n 8 -T 1
  split unit        connected component of the bipartite RT-cluster <-> ncRNA-cluster graph
  fragment bridge   NONE - rejected, rationale recorded in this manifest
  allocation        deterministic greedy, NO RANDOM SEED (see below)
  sensitivity       near-duplicate stratum: local identity >= 0.90 AND aligned coverage >= 0.30

COMPONENT KEY AND THE TIE-BREAK - read before re-implementing
  The allocation sorts components by (pairs DESC, str(component_key) ASC). The component key is
  the union-find root label produced by the pinned DSU in this file, over the pair rows in the
  row order of rt_ncrna_exact_pairs_v1.parquet. Both the code and that input are hashed here,
  so the key is reproducible - but it is an artefact of this implementation, not a canonical
  name. A re-implementation with a different union order could produce different roots and
  therefore a different tie-break among EQUAL-SIZED components. That is why s07 verifies by
  re-running this pinned code and comparing against the frozen assignment table, and why the
  ASSIGNMENT TABLE, not the algorithm, is the authority on membership.

COVERAGE SYMMETRIZATION FOR THE NEAR-DUPLICATE RULE - frozen, do not alter
  aligned_coverage = max(query_coverage, target_coverage)
    RT     query_coverage / target_coverage are mmseqs `qcov` / `tcov` on the local alignment.
    ncRNA  query_coverage = alignment_length / query_length,
           target_coverage = alignment_length / subject_length, from blastn fields.
  max() is used so a fragment counts whichever way round it is: a short held-out sequence fully
  contained in a long training one has high query coverage and low target coverage, and the
  reverse case is equally a near-duplicate. Taking the minimum would miss both.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[1]
OUT = ROOT / "results" / "embed_g2b_frozen_split"
G0 = TASK.parents[0] / "embed_g0_population_audit" / "work" / "clusters"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")
KEY = ["rt_seq_hash", "nc_seq_hash"]
TARGET = {"train": 0.70, "val": 0.15, "test": 0.15}

def _resolve(name: str) -> Path:
    """Find a declared cluster input. A FROZEN gate must be self-contained, so the bundle's own
    inputs/ copy wins; the ARIS_OUTPUT scratch is only the fallback for a pre-freeze run.
    Stored gzipped in the bundle to keep the repository lean; hashes in the manifest are always
    of the DECOMPRESSED bytes, so they stay comparable across both locations."""
    for cand in (ROOT / "results" / "embed_g2b_frozen_split" / "inputs" / (name + ".gz"),
                 ROOT / "results" / "embed_g2b_frozen_split" / "inputs" / name,
                 G0 / name):
        if cand.is_file():
            return cand
    raise SystemExit(f"cannot locate declared input {name}")


def read_text_any(p: Path) -> str:
    """Read a declared input whether it is stored plain or gzipped."""
    if p.suffix == ".gz":
        return gzip.decompress(p.read_bytes()).decode()
    return p.read_text()


def sha256_declared(p: Path) -> str:
    """sha256 of the DECOMPRESSED content, so a gzipped copy hashes like the original."""
    return hashlib.sha256(read_text_any(p).encode()).hexdigest()


RT_CLUSTER = _resolve("rt_id0.50_cluster.tsv")
NC_CLUSTER = _resolve("nc_id0.80.clstr")

VERSIONS = {"mmseqs": "18.8cc5c", "cd-hit-est": "CD-HIT 4.8.1 (built Apr 24 2025)",
            "blastn": "2.16.0+", "python": "3.12.12", "numpy": "1.26.4",
            "pandas": "3.0.2", "pyarrow": "25.0.0"}
COMMANDS = {
    "rt_clustering": ("/home/borg/miniconda3/envs/colabfold/bin/mmseqs easy-cluster "
                      "rt_pair_universe.faa rt_id0.50 <tmp> --min-seq-id 0.50 -c 0.8 "
                      "--cov-mode 0 --threads 16 -v 1"),
    "ncrna_clustering": ("/home/borg/miniconda3/envs/retron_tradicional/bin/cd-hit-est "
                         "-i rt_ncrna_oriented_v1.fna -o nc_id0.80 -c 0.80 -n 8 -aS 0.8 "
                         "-M 8000 -T 1 -d 0"),
    "rt_leakage_probe": ("mmseqs search <heldout> <training-only> -s 7.5 --min-seq-id 0.0 "
                         "-e 1000 --max-seqs 300 -c 0.0 --threads 16"),
    "ncrna_leakage_probe": ("blastn -task blastn -word_size 7 -query <heldout> "
                            "-db <training-only> -evalue 1000 -max_target_seqs 300"),
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_mm(p):
    return {m: r for r, m in (l.split("\t") for l in read_text_any(p).splitlines())}


def read_cd(p):
    d, block, rep = {}, [], None
    def flush():
        if block:
            r = rep or block[0]
            for m in block:
                d[m] = r
    for l in read_text_any(p).splitlines():
        if l.startswith(">Cluster"):
            flush(); block, rep = [], None; continue
        s = l.split(">", 1)[1].split("...")[0].strip()
        block.append(s)
        if l.rstrip().endswith("*"):
            rep = s
    flush(); return d


class DSU:
    """PINNED. Union order and path compression are part of the frozen component key."""
    def __init__(self): self.p = {}
    def find(self, x):
        self.p.setdefault(x, x); r = x
        while self.p[r] != r: r = self.p[r]
        while self.p[x] != r: self.p[x], x = r, self.p[x]
        return r
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[ra] = rb


def assign(sizes: pd.Series, n: int) -> dict:
    """THE FROZEN ALLOCATION. Deterministic greedy; no seed, no RNG, no shuffling.

    Components are visited largest-first; each goes to the fold whose remaining pair deficit is
    largest; exact ties break train > val > test. The result is a pure function of the component
    sizes and keys, so 'reproducible' here means bit-identical, not distributionally similar.
    """
    order = sorted(sizes.index, key=lambda c: (-int(sizes[c]), str(c)))
    got = {"train": 0, "val": 0, "test": 0}
    fold = {}
    for c in order:
        deficit = {f: TARGET[f] * n - got[f] for f in got}
        best = max(("train", "val", "test"),
                   key=lambda f: (deficit[f], -["train", "val", "test"].index(f)))
        fold[c] = best
        got[best] += int(sizes[c])
    return fold


def neff(s) -> float:
    """Effective number of independent components = (sum s)^2 / sum(s^2) (inverse Simpson).

    Equals the component count when all components are equal-sized, and collapses toward 1 when
    one component dominates. It is the quantity that bounds component-level inference; the raw
    component COUNT does not.
    """
    s = np.asarray(s, dtype=float)
    return float((s.sum() ** 2) / (s ** 2).sum())


def main() -> int:
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    reg_path = CANON / "rt_ncrna_exact_pairs_v1.parquet"
    reg = pq.read_table(reg_path, columns=KEY).to_pandas()
    n = len(reg)
    assert n == 30_924, n

    rmap, nmap = read_mm(RT_CLUSTER), read_cd(NC_CLUSTER)
    d = DSU()
    rc = reg.rt_seq_hash.map(rmap).values
    nc = reg.nc_seq_hash.map(nmap).values
    assert not pd.isna(rc).any() and not pd.isna(nc).any(), "unclustered sequence"
    for a, b in zip(rc, nc):
        d.union("R" + a, "N" + b)
    comp = np.array([d.find("R" + x) for x in rc])
    sizes = pd.Series(comp).value_counts()
    fold_of = assign(sizes, n)
    pf = np.array([fold_of[c] for c in comp])

    # stable, implementation-independent display ids, ordered exactly as the allocation visits
    order = sorted(sizes.index, key=lambda c: (-int(sizes[c]), str(c)))
    disp = {c: f"CMP{i:05d}" for i, c in enumerate(order)}

    # ---- tiers -----------------------------------------------------------------------
    p = pq.read_table(CANON / "rt_ncrna_pairs_v1.parquet",
                      columns=KEY + ["canonical", "file_label", "same_strand", "direction",
                                     "n_cds_between", "signed_distance_bp", "evalue"]).to_pandas()
    cr = p[p.canonical & (p.file_label == "Retron")]
    m2 = (cr.same_strand & (cr.direction != "downstream") & (cr.n_cds_between == 0)
          & (cr.signed_distance_bp.abs() <= 200))
    T = {"T1": set(map(tuple, cr[KEY].drop_duplicates().values)),
         "T2": set(map(tuple, cr[m2][KEY].drop_duplicates().values)),
         "T3": set(map(tuple, cr[m2 & (cr.evalue <= 1e-5)][KEY].drop_duplicates().values))}
    rec = pq.read_table(CANON / "rt_ncrna_exact_pair_recurrence_v1.parquet",
                        columns=KEY + ["recurrence_class"]).to_pandas()
    T["T4"] = T["T3"] & set(map(tuple, rec[rec.recurrence_class.isin(
        ["multiple_species", "one_species_multiple_genomes"])][KEY].values))
    tup = list(map(tuple, reg[KEY].values))
    flags = {k: np.array([x in s for x in tup]) for k, s in T.items()}

    # ---- near-duplicate stratum: COMPUTED HERE, not referenced -------------------------
    # The sensitivity population has to be a concrete, frozen list of sequences, or it is not
    # predeclared - it is a rule someone re-evaluates later under different conditions.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from s04_fragment_bridge import exact_probe, read_fasta  # noqa: E402
    tmp = Path(__import__("os").environ.get("TMPDIR", "/tmp")) / "g2freeze"
    rt_seqs = read_fasta(ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa")
    nc_seqs = read_fasta(ROOT / "data/derived/rt_ncrna_oriented_v1.fna")
    tr = pf != "test"
    tr_rt, tr_nc = set(reg.rt_seq_hash.values[tr]), set(reg.nc_seq_hash.values[tr])
    te_rt = set(reg.rt_seq_hash.values[~tr]) - tr_rt
    te_nc = set(reg.nc_seq_hash.values[~tr]) - tr_nc
    hr = exact_probe(tmp / "rt", rt_seqs, te_rt, tr_rt, "rt")
    hn = exact_probe(tmp / "nc", nc_seqs, te_nc, tr_nc, "nc")
    ND_ID, ND_COV = 0.90, 0.30
    nd_rt = sorted(hr[(hr.fident >= ND_ID) & (hr.aln_cov >= ND_COV)].q.unique())
    nd_nc = sorted(hn[(hn.fident >= ND_ID) & (hn.aln_cov >= ND_COV)].q.unique())
    # A pair is NEAR-DUPLICATE-TOUCHED if either of its sequences is in the stratum.
    is_nd = (reg.rt_seq_hash.isin(nd_rt) | reg.nc_seq_hash.isin(nd_nc)).values
    # The FROZEN sensitivity population excludes whole COMPONENTS containing any touched pair,
    # not just the touched pairs. Two reasons, and they both matter:
    #   1. the frozen split unit is the component; excluding a pair but keeping its component
    #      siblings would silently break indivisibility inside the sensitivity analysis;
    #   2. a component with a near-identical bridge into training is suspect as a whole, not
    #      only at the specific pair carrying the bridge.
    # Pair-level exclusion would instead leave 4,114 pairs at n_eff 12.6; that is recorded as a
    # descriptive alternative but is NOT the frozen definition.
    nd_components = {c for c, t in zip(comp, is_nd) if t}
    in_nd_comp = np.array([c in nd_components for c in comp])
    nd_tbl = pd.DataFrame(
        [{"modality": "RT", "seq_hash": s} for s in nd_rt]
        + [{"modality": "ncRNA", "seq_hash": s} for s in nd_nc])
    ndbuf = nd_tbl.to_csv(sep="\t", index=False).encode()
    (OUT / "tables" / "near_duplicate_stratum.tsv").write_bytes(ndbuf)
    sens = (~tr) & (~in_nd_comp)
    sens_sizes = pd.Series(comp[sens]).value_counts()
    print(f"  near-duplicate stratum: {len(nd_rt)} RT, {len(nd_nc)} ncRNA; "
          f"sensitivity population {int(sens.sum()):,} pairs, "
          f"{len(sens_sizes)} comps, n_eff {neff(sens_sizes.values):.1f}, "
          f"T4 {int(flags['T4'][sens].sum()):,} "
          f"({100*flags['T4'][sens].sum()/flags['T4'].sum():.2f}%)")
    subprocess.run(["rm", "-rf", str(tmp)], check=False)

    # ---- assignment table ------------------------------------------------------------
    asg = pd.DataFrame({
        "pair_index": np.arange(n),
        "rt_seq_hash": reg.rt_seq_hash.values,
        "nc_seq_hash": reg.nc_seq_hash.values,
        "rt_cluster": rc, "nc_cluster": nc,
        "component_key": comp,
        "component_id": [disp[c] for c in comp],
        "fold": pf,
        **{k: flags[k].astype(int) for k in ("T1", "T2", "T3", "T4")},
        "near_duplicate": is_nd.astype(int),
        "near_duplicate_component": in_nd_comp.astype(int),
        "in_sensitivity_population": sens.astype(int),
    })
    buf = asg.to_csv(sep="\t", index=False).encode()
    (OUT / "tables" / "split_assignment.tsv.gz").write_bytes(gzip.compress(buf, 9))
    asg_sha = sha256_bytes(buf)

    comps = pd.DataFrame({
        "component_id": [disp[c] for c in sizes.index],
        "component_key": sizes.index,
        "n_pairs": sizes.values,
        "fold": [fold_of[c] for c in sizes.index],
    }).sort_values("component_id")
    for k in ("T1", "T2", "T3", "T4"):
        m = pd.Series(flags[k]).groupby(comp).sum()
        comps[k] = comps.component_key.map(m).fillna(0).astype(int)
    cbuf = comps.to_csv(sep="\t", index=False).encode()
    (OUT / "tables" / "split_components.tsv").write_bytes(cbuf)

    folds = {}
    for f in ("train", "val", "test"):
        m = pf == f
        cs = sizes[[c for c, x in fold_of.items() if x == f]]
        folds[f] = dict(
            pairs=int(m.sum()), pct=round(100 * float(m.mean()), 2),
            components=int(len(cs)), n_eff=round(neff(cs.values), 1),
            unique_rt=int(len(set(reg.rt_seq_hash.values[m]))),
            unique_ncrna=int(len(set(reg.nc_seq_hash.values[m]))),
            largest_component_pairs=int(cs.max()),
            **{k: int(flags[k][m].sum()) for k in ("T1", "T2", "T3", "T4")},
            **{k + "_pct": round(100 * float(flags[k][m].sum() / flags[k].sum()), 2)
               for k in ("T1", "T2", "T3", "T4")})

    manifest = {
        "gate": "embed_g2b_frozen_split",
        "status": "FROZEN",
        "frozen_on": "2026-09-18",
        "operator_decision": "Option A approved: no secondary fragment bridge.",
        "frozen_before": "any downstream embedding compatibility result was examined",

        "thresholds_and_coverage_semantics": {
            "rt_identity": 0.50,
            "rt_coverage": "-c 0.8 --cov-mode 0 = BIDIRECTIONAL; both sequences >=80% covered",
            "ncrna_identity": 0.80,
            "ncrna_coverage": "-aS 0.8 = SHORTER-sequence coverage; shorter member >=80% aligned",
            "why_asymmetric": ("a protein pair aligning over 80% of both is homologous along its "
                               "length; ncRNAs at 34-395 nt are short enough that anchoring on "
                               "the shorter member avoids discarding a real relative over a "
                               "length difference"),
            "split_unit": ("connected component of the bipartite RT-cluster <-> ncRNA-cluster "
                           "graph; components are INDIVISIBLE"),
            "fragment_bridge": "NONE",
        },
        "allocation": {
            "method": "deterministic greedy, largest component first to largest pair deficit",
            "random_seed": None,
            "rng_used": False,
            "targets": TARGET,
            "tie_break": "exact deficit ties break train > val > test",
            "component_order": "sorted by (n_pairs DESC, str(component_key) ASC)",
            "component_key_caveat": ("component_key is the union-find root from the pinned DSU "
                                     "in s06_freeze_split.py over the row order of "
                                     "rt_ncrna_exact_pairs_v1.parquet. Reproducible with that "
                                     "code and that input; NOT a canonical name. The assignment "
                                     "table is the authority on membership."),
        },
        "populations": {
            "primary_confirmatory": {
                "definition": "the full frozen test fold",
                "pairs": folds["test"]["pairs"],
                "components": folds["test"]["components"],
                "n_eff": folds["test"]["n_eff"],
                "T4_pct": folds["test"]["T4_pct"],
            },
            "near_duplicate_sensitivity": {
                "role": ("PREDECLARED SENSITIVITY ANALYSIS. Not a replacement primary test, and "
                         "not an alternative split selected on model performance."),
                "rule": "local identity >= 0.90 AND aligned coverage >= 0.30",
                "coverage_symmetrization": "aligned_coverage = max(query_coverage, target_coverage)",
                "coverage_fields": {
                    "rt": "mmseqs qcov and tcov on the local alignment",
                    "ncrna": "alignment_length/query_length and alignment_length/subject_length",
                },
                "why_max": ("a fragment must count whichever way round it is; min() would miss "
                            "both a short held-out sequence inside a long training one and the "
                            "reverse"),
                "measured_pre_freeze": {
                    "rt_crossing": "3 / 4,469 held-out RT (0.07%)",
                    "ncrna_crossing": "263 / 2,756 held-out ncRNA (9.54%)",
                    "excluded_population_pairs": 1525,
                    "excluded_population_n_eff": 24.5,
                    "excluded_population_T4_pct": 3.20,
                    "affected_test_components": "73 of 357",
                    "frozen_sequence_list": "tables/near_duplicate_stratum.tsv",
                    "n_rt_sequences": len(nd_rt),
                    "n_ncrna_sequences": len(nd_nc),
                    "exclusion_unit": "whole test COMPONENTS containing any near-duplicate-touched pair",
                    "pair_level_alternative_not_frozen": "4,114 pairs at n_eff 12.6",
                    "sensitivity_pairs_recomputed": int(sens.sum()),
                    "sensitivity_n_eff_recomputed": round(neff(sens_sizes.values), 1),
                },
            },
        },
        "n_eff_definition": {
            "formula": "n_eff = (sum_i s_i)^2 / sum_i (s_i^2), s_i = pairs in component i",
            "name": "inverse Simpson / effective number of components",
            "why": ("equals the component count when components are equal-sized and collapses "
                    "toward 1 when one dominates; the raw component COUNT does not bound "
                    "component-level inference, this does"),
        },
        "folds": folds,
        "tier_totals": {k: int(flags[k].sum()) for k in ("T1", "T2", "T3", "T4")},
        "measured_leakage_at_freeze": {
            "instrument": ("INDEPENDENT of the clustering and more sensitive than it: held-out "
                           "searched against a TRAINING-ONLY database, so censoring is "
                           "impossible. mmseqs -s 7.5 --min-seq-id 0 (RT), blastn -word_size 7 "
                           "(ncRNA)."),
            "held_out_definition": ("test; training means train + validation, because validation "
                                    "is inspected during development"),
            "rt": {"id>=0.50 & cov>=0.50": "3685/4469 = 82.46%",
                   "id>=0.70 & cov>=0.50": "57/4469 = 1.28%",
                   "id>=0.90 & cov>=0.30": "3/4469 = 0.07%",
                   "id>=0.50 & bidirectional cov>=0.80": "55.2%",
                   "id>=0.50 & query cov>=0.50": "77.0%"},
            "ncrna": {"id>=0.50 & cov>=0.50": "1175/2756 = 42.63%",
                      "id>=0.70 & cov>=0.50": "1122/2756 = 40.71%",
                      "id>=0.90 & cov>=0.30": "263/2756 = 9.54%"},
            "reachability": "held-out pairs reachable from training via either modality: 4638/4638 = 100.00%",
            "isolation": "held-out components with NO detectable relationship to training: 0/357 = 0.00%",
            "isolation_note": ("all 29,192 sequences are reverse transcriptases - one protein "
                               "family - so DETECTABILITY is saturated and uninformative. The "
                               "identity-and-coverage tiers are the instrument that carries "
                               "information."),
            "ncrna_artefact": ("every held-out ncRNA has a 100%-identity training match at <30% "
                               "coverage - short conserved msr/msd motifs, not homology. "
                               "UNFILTERED maximum ncRNA identity is saturated at 1.0 and must "
                               "never be quoted; only coverage-filtered numbers are "
                               "interpretable."),
        },
        "fragment_bridge_rejection_rationale": {
            "decision": "REJECTED - Option A frozen",
            "motivating_concern": ("the 80% coverage requirement lets a near-identical FRAGMENT "
                                   "of a training sequence form its own cluster and cross into "
                                   "the held-out fold"),
            "finding_1": ("the concern does not hold on the protein side: only 3 of 4,469 "
                          "held-out RTs (0.07%) cross at id>=0.90/cov>=0.30 under Option A"),
            "finding_2": ("the best bridge variant (id>=0.90, cov>=0.30) was VERIFIED, not "
                          "assumed: it closes the RT channel completely (3 -> 0) but only "
                          "reduces ncRNA 263 -> 54 (1.96%), because bridges are built from a "
                          "probe capped at 300 hits per query"),
            "finding_3": ("it costs 82% of validation independence, val n_eff 14.2 -> 2.6; "
                          "looser variants are worse - id>=0.70/cov>=0.50 gives val n_eff 1.0, "
                          "id>=0.50/cov>=0.50 collapses the graph to a 94.3% giant component"),
            "finding_4": ("a surgical quarantine of the 73 affected test components was also "
                          "priced and rejected: test falls to 1,525 pairs (4.93%) and T4 "
                          "retention to 3.20%"),
            "accepted_residual": ("the ncRNA near-duplicate channel is ACCEPTED AND REPORTED, "
                                  "not eliminated. It is handled by the predeclared sensitivity "
                                  "stratum, not by a structural change."),
        },
        "frozen_interpretation": (
            "The primary experiment tests RT-ncRNA compatibility generalization across the "
            "declared sequence-relatedness component split. It does not establish generalization "
            "to evolutionarily unrelated RT or ncRNA sequences."),
        "frozen_inference_unit": (
            "Inference for confirmatory results MUST operate at the COMPONENT level. The 4,638 "
            "test pairs are NOT independent observations; the effective number of independent "
            "units is n_eff = 14.1. Any test treating pairs as exchangeable overstates "
            "significance."),
        "immutability": (
            "Thresholds, split membership, sensitivity definition and inference unit must NOT be "
            "changed in response to downstream model performance. Any change requires a new "
            "operator decision record and supersedes this manifest rather than editing it."),
        "software_versions": VERSIONS,
        "commands": COMMANDS,
        "inputs": {
            "rt_ncrna_exact_pairs_v1.parquet": sha256_file(reg_path),
            "rt_pair_universe.faa": sha256_file(
                ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa"),
            "rt_ncrna_oriented_v1.fna": sha256_file(ROOT / "data/derived/rt_ncrna_oriented_v1.fna"),
            "rt_id0.50_cluster.tsv": sha256_declared(RT_CLUSTER),
            "nc_id0.80.clstr": sha256_declared(NC_CLUSTER),
        },
        "outputs": {
            "split_assignment.tsv.gz": {"sha256_uncompressed": asg_sha, "rows": n},
            "split_components.tsv": {"sha256": sha256_bytes(cbuf), "rows": len(comps)},
            "near_duplicate_stratum.tsv": {"sha256": sha256_bytes(ndbuf), "rows": len(nd_tbl)},
        },
        "producer": "embed_g2/s06_freeze_split.py",
        "producer_sha256": sha256_file(Path(__file__)),
        "git_rev": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip(),
    }
    (OUT / "SPLIT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n")

    print("FROZEN SPLIT")
    for f in ("train", "val", "test"):
        d_ = folds[f]
        print(f"  {f:<6} {d_['pairs']:>7,} pairs ({d_['pct']:>5.2f}%)  "
              f"{d_['components']:>5,} comps  n_eff {d_['n_eff']:>6.1f}  "
              f"T3 {d_['T3']:>6,} T4 {d_['T4']:>6,} ({d_['T4_pct']:.2f}%)")
    print(f"  assignment sha256 (uncompressed) {asg_sha}")
    print(f"  wrote {OUT}/SPLIT_MANIFEST.json + tables/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
