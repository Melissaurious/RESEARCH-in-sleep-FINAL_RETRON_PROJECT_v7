#!/usr/bin/env python3
"""pre-g4 step 2 - where every old-seed sequence reappears, by identity and not just by hash.

Exact-duplicate matching answers "is this the same sequence". It does not answer "has the
model already seen something 95% identical to this", which is the question that decides
whether a held-out population is really held out. So each seed member is searched against
every population with mmseqs, and the best hit's identity and coverage are landed alongside
the exact-hash result.

Comparator populations (Toro 2014, myRT) are read HERE ONLY to measure overlap. Nothing in
this bundle uses them to define, seed, fit or threshold anything.

Writes: tables/preg4_leakage_audit.tsv, tables/preg4_leakage_summary.tsv,
        tables/preg4_identity_distribution.tsv
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preg4lib import (ENV, IDENTITY_BINS, POPULATIONS, load_population,  # noqa: E402
                      read_tsv, seq_hash, write_tsv)


def mmseqs_best(query: Path, target: Path, work: Path, tag: str) -> dict[str, tuple]:
    """query id -> (target, fident, qcov, tcov, evalue, bits) for the best hit."""
    out = work / f"hits_{tag}.m8"
    tmp = work / f"tmp_{tag}"
    if not out.is_file():
        subprocess.run(
            [str(ENV / "mmseqs"), "easy-search", str(query), str(target), str(out), str(tmp),
             "--format-output", "query,target,fident,alnlen,evalue,bits,qcov,tcov",
             "-s", "7.5", "--max-seqs", "300", "-e", "1e-3", "--threads", "4", "-v", "1"],
            check=True, capture_output=True)
    best: dict[str, tuple] = {}
    for line in out.read_text().splitlines():
        f = line.split("\t")
        if len(f) < 8:
            continue
        q, t, fid, _aln, ev, bits, qcov, tcov = f[:8]
        cur = best.get(q)
        if cur is None or float(bits) > cur[5]:
            best[q] = (t, float(fid), float(qcov), float(tcov), float(ev), float(bits))
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--skip-stage1", action="store_true")
    args = ap.parse_args()
    T, W = args.out, args.work

    query = W / "all167.faa"
    lineage = {r["sequence_id"]: r for r in read_tsv(T / "preg4_sequence_lineage.tsv")}

    rows, summary = [], []
    for pid, (path, kind, why) in POPULATIONS.items():
        if pid == "stage1_exact_rt" and args.skip_stage1:
            continue
        if not path.is_file():
            continue
        pop = load_population(pid)
        pop_hashes = {seq_hash(v) for v in pop.values()}

        # mmseqs needs a plain FASTA; the alignment substrate is ungapped first.
        target = path
        if kind == "clustal" or pid == "myrt1844":
            target = W / f"{pid}.faa"
            target.write_text("\n".join(f">{k}\n{v}" for k, v in pop.items()) + "\n",
                              encoding="utf-8")
        best = mmseqs_best(query, target, W, pid)

        n_exact = 0
        bins = {b: 0 for b in IDENTITY_BINS}
        n_hit = 0
        for sid, lin in lineage.items():
            exact = lin["sequence_hash"] in pop_hashes
            n_exact += exact
            b = best.get(sid)
            if b:
                n_hit += 1
                for threshold in IDENTITY_BINS:
                    if b[1] >= threshold:
                        bins[threshold] += 1
            rows.append({
                "sequence_id": sid, "membership_class": lin["membership_class"],
                "population": pid,
                "exact_sequence_present": "YES" if exact else "NO",
                "best_hit_target": b[0] if b else "NO_HIT",
                "best_hit_identity": f"{b[1]:.4f}" if b else "",
                "best_hit_query_coverage": f"{b[2]:.4f}" if b else "",
                "best_hit_target_coverage": f"{b[3]:.4f}" if b else "",
                "best_hit_evalue": f"{b[4]:.2e}" if b else "",
                "leakage_class": (
                    "EXACT_DUPLICATE" if exact else
                    "NEAR_DUPLICATE_GE_90" if b and b[1] >= 0.9 else
                    "HIGH_IDENTITY_GE_70" if b and b[1] >= 0.7 else
                    "MODERATE_GE_50" if b and b[1] >= 0.5 else
                    "REMOTE_GE_30" if b and b[1] >= 0.3 else
                    "DISTANT_OR_NO_HIT"),
                "population_role": why,
                "unit": "old-seed sequence vs one population",
                "denominator": f"{len(lineage)} seed sequences vs {len(pop)} in {pid}",
            })
        summary.append({
            "population": pid, "n_population": len(pop),
            "n_seed_sequences": len(lineage),
            "n_exact_duplicates": n_exact,
            "pct_exact": f"{100 * n_exact / len(lineage):.2f}",
            "n_with_any_hit": n_hit,
            **{f"n_ge_{int(b * 100)}pct_identity": bins[b] for b in IDENTITY_BINS},
            "population_role": why,
            "unit": "old-seed sequence",
            "denominator": f"{len(lineage)} sequences in all167.faa",
        })

    write_tsv(T / "preg4_leakage_audit.tsv",
              ["sequence_id", "membership_class", "population", "exact_sequence_present",
               "best_hit_target", "best_hit_identity", "best_hit_query_coverage",
               "best_hit_target_coverage", "best_hit_evalue", "leakage_class",
               "population_role", "unit", "denominator"], rows)
    write_tsv(T / "preg4_leakage_summary.tsv",
              ["population", "n_population", "n_seed_sequences", "n_exact_duplicates",
               "pct_exact", "n_with_any_hit"] +
              [f"n_ge_{int(b * 100)}pct_identity" for b in IDENTITY_BINS] +
              ["population_role", "unit", "denominator"], summary)

    # identity distribution split by membership class - the CAND question specifically
    dist = []
    # sorted(), not a set: set iteration order over strings varies between
    # processes, which made this table differ on rerun while its content was
    # identical. A bundle that cannot reproduce its own byte layout is not
    # reproducible, even when the numbers agree.
    for pid in sorted({r["population"] for r in rows}):
        for cls in ("ANCHOR", "CANDIDATE"):
            sub = [r for r in rows if r["population"] == pid and r["membership_class"] == cls]
            if not sub:
                continue
            ex = sum(1 for r in sub if r["exact_sequence_present"] == "YES")
            ids = sorted(float(r["best_hit_identity"]) for r in sub
                         if r["best_hit_identity"])
            dist.append({
                "population": pid, "membership_class": cls, "n": len(sub),
                "n_exact": ex, "pct_exact": f"{100 * ex / len(sub):.2f}",
                "median_best_identity": f"{ids[len(ids) // 2]:.4f}" if ids else "",
                "max_best_identity": f"{ids[-1]:.4f}" if ids else "",
                "n_no_hit": sum(1 for r in sub if r["best_hit_target"] == "NO_HIT"),
                "unit": "old-seed sequence",
                "denominator": f"{len(sub)} {cls} members",
            })
    write_tsv(T / "preg4_identity_distribution.tsv",
              ["population", "membership_class", "n", "n_exact", "pct_exact",
               "median_best_identity", "max_best_identity", "n_no_hit", "unit",
               "denominator"], dist)

    for s in summary:
        print(f"  {s['population']:<16} n={s['n_population']:<7} exact={s['n_exact_duplicates']:>3} "
              f"ge90={s['n_ge_90pct_identity']:>3} ge70={s['n_ge_70pct_identity']:>3} "
              f"ge50={s['n_ge_50pct_identity']:>3} ge30={s['n_ge_30pct_identity']:>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
