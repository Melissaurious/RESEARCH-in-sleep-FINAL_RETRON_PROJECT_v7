#!/usr/bin/env python
"""embed_g2/s07 - can the frozen manifest RECONSTRUCT the exact split?

Reconstruction is the only thing that makes a freeze meaningful. This script starts from
SPLIT_MANIFEST.json, re-derives the split from the declared inputs and rule, and requires exact
equality with the frozen assignment - same components, same folds, same 30,924 rows, same
sha256, same near-duplicate stratum, same summary statistics.

    python s07_verify_split.py              verify
    python s07_verify_split.py --seed-bad   prove the verifier can FAIL

--seed-bad exists because a check that always passes is not evidence (PROJECT_ANALYSIS_
PRINCIPLES §13). It flips ONE pair's fold in the reconstruction and requires the comparison to
reject it. If the seeded-bad run passes, the verifier is broken and the real run means nothing.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s06_freeze_split import (  # noqa: E402
    CANON, KEY, NC_CLUSTER, RT_CLUSTER, ROOT, DSU, assign, neff, read_cd, read_mm,
    sha256_declared, sha256_file)

BUNDLE = ROOT / "results" / "embed_g2b_frozen_split"
FAILED: list[str] = []


def check(name, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: {got!r}" + ("" if ok else f" != {want!r}"))
    if not ok:
        FAILED.append(name)
    return ok


def main() -> int:
    seed_bad = "--seed-bad" in sys.argv
    man = json.loads((BUNDLE / "SPLIT_MANIFEST.json").read_text())
    print(f"manifest: {man['gate']}  status {man['status']}  frozen {man['frozen_on']}")
    if seed_bad:
        print("  *** --seed-bad: one fold label will be corrupted; the verifier MUST reject it")

    print("\n[1] declared inputs still hash as recorded")
    paths = {
        "rt_ncrna_exact_pairs_v1.parquet": CANON / "rt_ncrna_exact_pairs_v1.parquet",
        "rt_pair_universe.faa": ROOT / "ARIS_OUTPUT/embed_g0_population_audit/work/rt_pair_universe.faa",
        "rt_ncrna_oriented_v1.fna": ROOT / "data/derived/rt_ncrna_oriented_v1.fna",
        "rt_id0.50_cluster.tsv": RT_CLUSTER,
        "nc_id0.80.clstr": NC_CLUSTER,
    }
    for k, p in paths.items():
        h = sha256_declared(p) if k.startswith(("rt_id", "nc_id")) else sha256_file(p)
        check(k, h, man["inputs"][k])

    print("\n[2] re-derive the split from the declared rule")
    reg = pq.read_table(paths["rt_ncrna_exact_pairs_v1.parquet"], columns=KEY).to_pandas()
    n = len(reg)
    rmap, nmap = read_mm(RT_CLUSTER), read_cd(NC_CLUSTER)
    d = DSU()
    rc = reg.rt_seq_hash.map(rmap).values
    nc = reg.nc_seq_hash.map(nmap).values
    for a, b in zip(rc, nc):
        d.union("R" + a, "N" + b)
    comp = np.array([d.find("R" + x) for x in rc])
    sizes = pd.Series(comp).value_counts()
    fold_of = assign(sizes, n)
    pf = np.array([fold_of[c] for c in comp])
    if seed_bad:
        i = int(np.where(pf == "test")[0][0])
        pf[i] = "train"
    print(f"  re-derived {len(sizes):,} components over {n:,} pairs")

    print("\n[3] compare against the FROZEN assignment table")
    frozen_bytes = gzip.decompress((BUNDLE / "tables" / "split_assignment.tsv.gz").read_bytes())
    check("split_assignment.tsv.gz sha256 (uncompressed)",
          hashlib.sha256(frozen_bytes).hexdigest(),
          man["outputs"]["split_assignment.tsv.gz"]["sha256_uncompressed"])
    frozen = pd.read_csv(gzip.open(BUNDLE / "tables" / "split_assignment.tsv.gz"), sep="\t")
    check("rows", len(frozen), n)
    check("pair identity (rt_seq_hash)", list(frozen.rt_seq_hash) == list(reg.rt_seq_hash), True)
    check("pair identity (nc_seq_hash)", list(frozen.nc_seq_hash) == list(reg.nc_seq_hash), True)
    check("component membership", list(frozen.component_key) == list(comp), True)
    check("fold assignment", list(frozen.fold) == list(pf), True)
    same = int((frozen.fold.values == pf).sum())
    print(f"        {same:,}/{n:,} pair fold labels agree")

    print("\n[4] summary statistics re-derived from the reconstruction")
    for f in ("train", "val", "test"):
        m = pf == f
        cs = sizes[[c for c, x in fold_of.items() if x == f]]
        check(f"{f} pairs", int(m.sum()), man["folds"][f]["pairs"])
        check(f"{f} components", int(len(cs)), man["folds"][f]["components"])
        check(f"{f} n_eff", round(neff(cs.values), 1), man["folds"][f]["n_eff"])

    print("\n[5] frozen pre-freeze facts, as enumerated by the operator")
    prim = man["populations"]["primary_confirmatory"]
    sens = man["populations"]["near_duplicate_sensitivity"]["measured_pre_freeze"]
    check("primary test pairs == 4,638", prim["pairs"], 4638)
    check("primary test n_eff ~= 14.1", prim["n_eff"], 14.1)
    check("T4 test representation ~= 13.3%", prim["T4_pct"], 13.26)
    check("RT near-duplicate crossing", sens["rt_crossing"], "3 / 4,469 held-out RT (0.07%)")
    check("ncRNA near-duplicate crossing", sens["ncrna_crossing"],
          "263 / 2,756 held-out ncRNA (9.54%)")
    check("sensitivity pairs ~= 1,525", sens["sensitivity_pairs_recomputed"], 1525)
    check("sensitivity n_eff ~= 24.5", sens["sensitivity_n_eff_recomputed"], 24.5)
    check("sensitivity T4 ~= 3.2%", sens["excluded_population_T4_pct"], 3.20)
    check("all held-out components connected to training",
          man["measured_leakage_at_freeze"]["isolation"],
          "held-out components with NO detectable relationship to training: 0/357 = 0.00%")

    print("\n[6] near-duplicate stratum is a concrete frozen list")
    nd = pd.read_csv(BUNDLE / "tables" / "near_duplicate_stratum.tsv", sep="\t")
    check("near-duplicate stratum sha256",
          hashlib.sha256(nd.to_csv(sep="\t", index=False).encode()).hexdigest(),
          man["outputs"]["near_duplicate_stratum.tsv"]["sha256"])
    check("RT sequences in stratum", int((nd.modality == "RT").sum()), 3)
    check("ncRNA sequences in stratum", int((nd.modality == "ncRNA").sum()), 263)
    check("sensitivity population reproduces from the frozen flag",
          int(frozen.in_sensitivity_population.sum()), 1525)

    print("\n[7] the frozen non-numeric commitments are present verbatim")
    check("interpretation frozen", man["frozen_interpretation"].startswith(
        "The primary experiment tests RT-ncRNA compatibility generalization"), True)
    check("inference unit frozen", "COMPONENT level" in man["frozen_inference_unit"], True)
    check("no fragment bridge",
          man["thresholds_and_coverage_semantics"]["fragment_bridge"], "NONE")
    check("coverage symmetrization recorded",
          man["populations"]["near_duplicate_sensitivity"]["coverage_symmetrization"],
          "aligned_coverage = max(query_coverage, target_coverage)")
    check("allocation is seedless", man["allocation"]["rng_used"], False)

    print()
    if seed_bad:
        if FAILED:
            print(f"SEEDED-BAD REJECTED as required ({len(FAILED)} checks failed: "
                  f"{FAILED[:3]}). The verifier can fail, so a passing run is evidence.")
            return 0
        print("SEEDED-BAD ACCEPTED - THE VERIFIER IS BROKEN. A passing run proves nothing.")
        return 1
    if FAILED:
        print(f"VERIFICATION FAILED: {len(FAILED)} checks -> {FAILED}")
        return 1
    print("VERIFICATION PASSED - the manifest reconstructs the exact split.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
