#!/usr/bin/env python3
"""h02 - why do the MULTI records carry several RT family labels?

The corpus records the labels but not the evidence behind them. This gate re-derives that
evidence with the same instrument family the miner used: the myRT all-RT HMM library
(`RVT-All.hmm`, 45 profiles), run over the RT proteins themselves.

Design, declared before the run:

  * population: every EXACT RT sequence in the MULTI stratum (deduplicated - a protein is
    scored once however many records carry it);
  * POSITIVE CONTROL: a seeded random sample of exact RTs from single-family files. If the
    instrument works, its best-scoring profile should agree with the file label there. A
    near-tie analysis on MULTI means nothing unless the same analysis separates single-family
    RTs cleanly;
  * the measurement is the SCORE MARGIN between the best and second-best profile family, and
    whether the labels in `system_types` are the profiles that actually score.

⚠️ Stage 1 does not resolve MULTI. This gate measures the basis of the labels; assigning a
family to a MULTI record would need an auditable resolution rule and is the operator's.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

SEED = 20260915
CONTROL_N = 2000          # DECLARED: exact RTs sampled from single-family files
HMMSEARCH_ARGS = ["--cpu", "8", "-E", "10"]   # DECLARED: report-level E only; no bit-score gate


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


# Profile name -> corpus family label. DECLARED explicitly rather than inferred by a pattern:
# the first version used a regex and silently failed on `RVT-GII-I/-II` and `RVT-Retrons`,
# which the positive control caught as 0/1,029 and 0/294 agreement on the two largest families.
PROFILE_TO_FAMILY = {"RVT-Retrons": "Retron"}
PROFILE_PREFIX = {"RVT-GII-": "RVT-GII", "RVT-CRISPR-G": "RVT-CRISPR"}


def family_of_profile(name: str) -> str:
    if name in PROFILE_TO_FAMILY:
        return PROFILE_TO_FAMILY[name]
    for pre, fam in PROFILE_PREFIX.items():
        if name.startswith(pre):
            return fam
    return name


def run_hmmsearch(hmm: Path, fasta: Path, out: Path, bin_dir: str) -> Path:
    dom = out.with_suffix(".domtbl")
    cmd = [str(Path(bin_dir) / "hmmsearch"), "--domtblout", str(dom), *HMMSEARCH_ARGS,
           str(hmm), str(fasta)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return dom


def parse_domtbl(p: Path) -> pd.DataFrame:
    rows = []
    with p.open() as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            t = line.split()
            rows.append([t[0], t[3], float(t[7]), float(t[13])])   # target, query, seq E, dom score
    df = pd.DataFrame(rows, columns=["rt_seq_hash", "profile", "evalue", "score"])
    return df.groupby(["rt_seq_hash", "profile"], as_index=False).agg(
        score=("score", "max"), evalue=("evalue", "min"))


def best_two(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["profile_family"] = df.profile.map(family_of_profile)
    fam = df.groupby(["rt_seq_hash", "profile_family"], as_index=False).score.max()
    fam = fam.sort_values(["rt_seq_hash", "score"], ascending=[True, False])
    g = fam.groupby("rt_seq_hash")
    top = g.nth(0).rename(columns={"profile_family": "best_family", "score": "best_score"})
    sec = g.nth(1).rename(columns={"profile_family": "second_family", "score": "second_score"})
    out = top.merge(sec, on="rt_seq_hash", how="left")
    out["margin_bits"] = (out.best_score - out.second_score.fillna(0)).round(2)
    out["n_families_hit"] = g.size().values
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--hmm", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--bin", default="/home/borg/miniconda3/envs/retron_tradicional/bin")
    a = ap.parse_args()
    D, W = Path(a.derived), Path(a.work)
    T, C = W / "tables", W / "cache"
    T.mkdir(parents=True, exist_ok=True)
    C.mkdir(parents=True, exist_ok=True)

    base = pd.read_parquet(W / "derived" / "rt_family_baseline_v1.parquet")
    seqs = pd.read_parquet(D / "rt_exact_v1.parquet",
                           columns=["rt_seq_hash", "rt_seq", "type_set_norm_set", "family_label_set"])
    multi = base[base.view.eq("V-RT-MULTI")].merge(seqs, on="rt_seq_hash")
    ctrl = base[base.view.eq("V-RT-SINGLE")].sample(n=CONTROL_N, random_state=SEED).merge(
        seqs, on="rt_seq_hash")
    print(f"  MULTI exact RTs: {len(multi):,d}   control exact RTs: {len(ctrl):,d}", flush=True)

    res = {}
    for tag, df in (("multi", multi), ("control", ctrl)):
        fa = C / f"{tag}.faa"
        with fa.open("w") as fh:
            for h, s in zip(df.rt_seq_hash, df.rt_seq):
                fh.write(f">{h}\n{s}\n")
        dom = run_hmmsearch(Path(a.hmm), fa, C / tag, a.bin)
        hits = parse_domtbl(dom)
        b = best_two(hits)
        res[tag] = df.merge(b, on="rt_seq_hash", how="left")
        print(f"  {tag}: {len(b):,d} of {len(df):,d} sequences hit at least one profile", flush=True)

    # ---- the positive control: does the instrument recover a known label? -------------
    c = res["control"]
    c["best_equals_file_label"] = c.best_family.eq(c.family_label)
    w(T / "g4_multi_hmm_positive_control.tsv", pd.DataFrame([
        ["control exact RTs scored", len(c), ""],
        ["with at least one profile hit", int(c.best_family.notna().sum()),
         round(100 * c.best_family.notna().mean(), 3)],
        ["best-scoring profile family equals the file label", int(c.best_equals_file_label.sum()),
         round(100 * c.best_equals_file_label.mean(), 3)],
        ["median best-vs-second margin (bits)", float(c.margin_bits.median()), ""],
        ["median profile families hit per sequence", float(c.n_families_hit.median()), ""],
        ["control sequences with a margin below 10 bits", int((c.margin_bits < 10).sum()),
         round(100 * (c.margin_bits < 10).mean(), 3)],
    ], columns=["measure", "value", "pct"]).assign(
        seed=SEED, unit="exact RT sequences",
        denominator=f"a seeded random sample of {CONTROL_N} V-RT-SINGLE exact RTs"))
    w(T / "g4_multi_hmm_control_by_family.tsv", c.groupby("family_label").agg(
        n=("rt_seq_hash", "size"), n_best_equals_label=("best_equals_file_label", "sum"),
        median_margin_bits=("margin_bits", "median")).reset_index().sort_values(
            "n", ascending=False).assign(
                unit="exact RT sequences", denominator="sampled control exact RTs of that family"))

    # ---- MULTI: do the labels correspond to profiles that actually score? -------------
    m = res["multi"]
    m["labels"] = m.type_set_norm_set.fillna("")
    m["best_in_labels"] = [b in set(l.split("/")) if isinstance(b, str) else False
                           for b, l in zip(m.best_family, m.labels)]
    m["second_in_labels"] = [s in set(l.split("/")) if isinstance(s, str) else False
                             for s, l in zip(m.second_family, m.labels)]
    w(T / "g4_multi_hmm_profile.tsv", pd.DataFrame([
        ["MULTI exact RTs scored", len(m), ""],
        ["with at least one profile hit", int(m.best_family.notna().sum()),
         round(100 * m.best_family.notna().mean(), 3)],
        ["best-scoring family is among the record's labels", int(m.best_in_labels.sum()),
         round(100 * m.best_in_labels.mean(), 3)],
        ["second-best family also among the labels", int(m.second_in_labels.sum()),
         round(100 * m.second_in_labels.mean(), 3)],
        ["both best and second among the labels",
         int((m.best_in_labels & m.second_in_labels).sum()),
         round(100 * (m.best_in_labels & m.second_in_labels).mean(), 3)],
        ["median best-vs-second margin (bits)", float(m.margin_bits.median()), ""],
        ["margin below 10 bits", int((m.margin_bits < 10).sum()),
         round(100 * (m.margin_bits < 10).mean(), 3)],
        ["median profile families hit per sequence", float(m.n_families_hit.median()), ""],
    ], columns=["measure", "value", "pct"]).assign(
        unit="exact RT sequences", denominator="V-RT-MULTI exact RTs"))
    w(T / "g4_multi_hmm_margin_comparison.tsv", pd.DataFrame([
        ["V-RT-MULTI", len(m), float(m.margin_bits.median()),
         float(m.margin_bits.quantile(.25)), float(m.margin_bits.quantile(.75)),
         round(100 * (m.margin_bits < 10).mean(), 3), float(m.n_families_hit.median())],
        ["V-RT-SINGLE (seeded control)", len(c), float(c.margin_bits.median()),
         float(c.margin_bits.quantile(.25)), float(c.margin_bits.quantile(.75)),
         round(100 * (c.margin_bits < 10).mean(), 3), float(c.n_families_hit.median())],
    ], columns=["population", "n_exact_rt", "median_margin_bits", "q25_margin_bits",
                "q75_margin_bits", "pct_margin_below_10_bits", "median_families_hit"]).assign(
        unit="exact RT sequences", denominator="the population named in the row"))
    w(T / "g4_multi_label_sets_vs_hmm.tsv", m.groupby(
        ["labels", "best_family"]).agg(
        n_exact_rt=("rt_seq_hash", "size"), median_margin_bits=("margin_bits", "median"),
        n_best_in_labels=("best_in_labels", "sum")).reset_index().sort_values(
            "n_exact_rt", ascending=False).head(60).assign(
                unit="exact RT sequences", denominator="V-RT-MULTI exact RTs with that label set"))
    m[["rt_seq_hash", "labels", "best_family", "best_score", "second_family", "second_score",
       "margin_bits", "n_families_hit", "best_in_labels", "second_in_labels", "rt_aa_len",
       "n_loci", "n_species"]].to_parquet(
        W / "derived" / "multi_hmm_evidence_v1.parquet", index=False, compression="zstd")
    print(f"  multi_hmm_evidence_v1: {len(m):,d} rows", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
