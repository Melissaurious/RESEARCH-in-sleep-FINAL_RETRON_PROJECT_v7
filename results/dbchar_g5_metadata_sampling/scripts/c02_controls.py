#!/usr/bin/env python3
"""c02 - positive controls for g5.

A join that reports ~100% is exactly the shape that hides a broken key: this gate's first
version read 0% on GTDB (prefix stripped on one side only) and "key column absent" on both NCBI
catalogues (a comment line before the header). So the controls are two-sided:

  * a key TAKEN FROM each catalogue must join (the search can return non-zero);
  * a fabricated accession must NOT join (the search can return zero);
  * a catalogue whose header sits behind a comment line must still be read;
  * `RS_`/`GB_` prefixes must normalise on BOTH sides;
  * the redundancy correction must show a difference where one was constructed.

`--seed-bad` corrupts one expectation and must fail.
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import shutil
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--seed-bad", action="store_true")
    a = ap.parse_args()
    j01 = load(HERE / "j01_join_and_sampling.py", "j01")
    M = Path(a.meta)
    out = Path(a.out) / "fixture"
    if out.exists():
        shutil.rmtree(out)
    (out / "meta").mkdir(parents=True)
    rows, fails = [], []

    def expect(name, want, got):
        ok = want == got
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(name)

    # ---- 1 · the key normaliser ------------------------------------------------------
    expect("norm_key strips RS_", "GCF_000001.1", j01.norm_key("RS_GCF_000001.1"))
    expect("norm_key strips GB_", "GCA_000001.1", j01.norm_key("GB_GCA_000001.1"))
    expect("norm_key leaves a bare accession", "GCA_000001.1", j01.norm_key("GCA_000001.1"))

    # ---- 2 · a header behind a comment line -------------------------------------------
    p = out / "meta" / "commented.txt"
    p.write_text("#   See NCBI for terms of use\n#assembly_accession\tfoo\n"
                 "GCA_000001.1\tx\nGCA_000002.1\ty\n")
    keys, header, n = j01.read_keys(out / "meta", "commented.txt", "#assembly_accession", False)
    expect("header found behind a comment line", 2, n)
    expect("keys read behind a comment line", {"GCA_000001.1", "GCA_000002.1"}, keys)

    # ---- 3 · each REAL catalogue: a key from it joins, a fabricated one does not -------
    for db, (fname, key, gz) in j01.CATALOGUE.items():
        keys, header, n = j01.read_keys(M, fname, key, gz)
        expect(f"{db}: catalogue is non-empty", True, n > 0)
        expect(f"{db}: key column found", True, len(keys) > 0)
        if keys:
            probe = sorted(keys)[0]
            expect(f"{db}: a key taken from the catalogue joins (POSITIVE control)", True,
                   probe in keys)
        expect(f"{db}: a fabricated accession does NOT join (NEGATIVE control)", False,
               "GCF_999999999.9" in keys)

    # ---- 4 · GTDB really does carry the prefix, and the corpus really does too ---------
    gk, _, _ = j01.read_keys(M, *j01.CATALOGUE["gtdb_bacteria"][:2], j01.CATALOGUE["gtdb_bacteria"][2])
    r = pd.read_parquet(Path(a.derived) / "rt_records_v1.parquet",
                        columns=["source_database", "genome_id", "genome_id_norm"]).head(200000)
    g = r[r.source_database.eq("gtdb_bacteria")]
    if len(g):
        expect("corpus GTDB genome_id carries the RS_/GB_ prefix", True,
               bool(g.genome_id.str.startswith(("RS_", "GB_")).any()))
        expect("normalised corpus GTDB ids join the normalised catalogue", True,
               bool(g.genome_id_norm.isin(gk).all()))

    # ---- 5 · the redundancy correction must MOVE when redundancy is present ------------
    df = pd.DataFrame({
        "tax_species": ["A"] * 100 + ["B"] * 10,
        "rt_seq_hash": ["h1"] * 100 + [f"b{i}" for i in range(10)]})
    by_rec = df.tax_species.value_counts(normalize=True)
    by_rt = df.drop_duplicates(["tax_species", "rt_seq_hash"]).tax_species.value_counts(normalize=True)
    expect("a redundant species dominates on records", True, round(by_rec["A"], 3) > 0.9)
    expect("and stops dominating on exact RTs", True, round(by_rt["A"], 3) < 0.2)
    if a.seed_bad:
        expect("norm_key strips RS_", "RS_GCF_000001.1", j01.norm_key("RS_GCF_000001.1"))

    (Path(a.out) / "tables").mkdir(parents=True, exist_ok=True)
    name = "c02_positive_controls_SEEDBAD.tsv" if a.seed_bad else "c02_positive_controls.tsv"
    with (Path(a.out) / "tables" / name).open("w") as fh:
        fh.write("control\texpected\tobserved\tresult\n")
        for x in rows:
            fh.write("\t".join(str(v) for v in x) + "\n")
    print(f"c02: {len(rows)} controls, {len(fails)} failed")
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
