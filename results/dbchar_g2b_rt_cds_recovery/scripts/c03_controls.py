#!/usr/bin/env python3
"""c03 - positive controls for g2b: every recovery/representation class must fire on a
synthetic corpus whose answer is known, and the independent-translation verdict must reject
the cases it is supposed to reject. `--seed-bad` corrupts one expectation and must fail.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RETRON = "master_Retron_merged_oriented.jsonl"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--g2-scripts", required=True)
    ap.add_argument("--seed-bad", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, a.g2_scripts)
    import c04_controls as g2c

    out = Path(a.out) / "fixture"
    corpus, work = out / "corpus", out / "work"
    if corpus.exists():
        shutil.rmtree(corpus)
    corpus.mkdir(parents=True)
    rng = random.Random(3)
    P = "MKAYTLGDVIRQLESAGVKEVHFVGGEPLLR"
    dna = g2c.rev_translate(P)
    ws, at = 1001, 500
    fs = g2c.window(rng, 3000, at, dna)
    rs, re_ = ws + at, ws + at + len(dna) - 1
    recs, exp = [], {}

    def add(case, rec, **e):
        rec["rt_system_id"] = case
        recs.append(rec)
        exp[case] = e

    def base(cds_list, **kw):
        return g2c.record("x", "C", ws, fs, rs, re_, "+", P + "*", cds_list, **kw)

    def move_rt(rec, new_start):
        """Move the RT and keep the anchor fields consistent, as the miner would."""
        n = len(dna)
        rec["rt_gene"].update(start=new_start, end=new_start + n - 1, length=n)
        rec.update(anchor_start=new_start, anchor_end=new_start + n - 1,
                   anchor_center=(new_start + new_start + n - 1) // 2)
        return rec

    add("recovered_with_overlap", base([g2c.cds("c1", rs - 30, rs + 60, "+", False)]),
        recovery_state="RECOVERED", representation_class="rt_inside_window",
        any_same_frame=True, elig_rt_coords=True)
    add("recovered_no_overlap", base([g2c.cds("c1", ws + 2500, ws + 2600, "+", False)]),
        recovery_state="RECOVERED", representation_class="rt_inside_window",
        n_overlapping=0, elig_rt_coords=True)
    r = move_rt(base([]), ws + 5000)
    r["genomic_context"]["actual_window"]["clipped_at_contig_end"] = True
    add("beyond_window_end", r, recovery_state="SEQUENCE_ONLY",
        representation_class="rt_beyond_a_contig_end_clipped_window", elig_rt_coords=False)
    r2 = move_rt(base([]), ws + 2990)
    r2["genomic_context"]["actual_window"]["clipped_at_contig_end"] = True
    add("crossing_window_edge", r2, recovery_state="SEQUENCE_ONLY",
        representation_class="rt_crosses_a_contig_end_clipped_window")
    r3 = base([])
    r3["genomic_context"]["actual_window"] = {"start": 9000, "end": 5000,
                                              "clipped_at_contig_start": False,
                                              "clipped_at_contig_end": True}
    r3["genomic_context"]["full_sequence"] = ""
    r3["genomic_context"]["length"] = 0
    add("inverted_window", r3, recovery_state="SEQUENCE_ONLY",
        representation_class="window_inverted_no_sequence_retrieved")
    r4 = base([])
    r4["rt_gene"]["start"] = rs + 1          # a one-base frame shift: must stay ILL_POSED
    r4["rt_gene"]["end"] = re_ + 1
    add("frameshift_ill_posed", r4, recovery_state="ILL_POSED", elig_rt_coords=False)

    (corpus / RETRON).write_text("\n".join(json.dumps(x) for x in recs) + "\n")
    py = sys.executable
    g2s = Path(a.g2_scripts)
    for cmd in ([py, str(g2s / "e01_extract.py"), "--corpus", str(corpus), "--out", str(work), "--procs", "2"],
                [py, str(g2s / "m02_build_tables.py"), "--work", str(work)],
                [py, str(HERE / "r01_recovery.py"), "--derived", str(work / "derived"),
                 "--corpus", str(corpus), "--work", str(work)]):
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    m = pd.read_parquet(work / "derived" / "rt_cds_recovery_v1.parquet").set_index("rt_system_id")
    rows, fails = [], []

    def expect(name, want, got):
        ok = want == got
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(name)

    for case, e in exp.items():
        for field, want in e.items():
            expect(f"{case}:{field}", want, m.loc[case, field] if case in m.index else "<absent>")
    if a.seed_bad:
        expect("recovered_with_overlap:recovery_state", "SEQUENCE_ONLY",
               m.loc["recovered_with_overlap", "recovery_state"])
    expect("every_declared_class_fires", "",
           "|".join(sorted({"RECOVERED", "SEQUENCE_ONLY", "ILL_POSED"} - set(m.recovery_state))))

    # the independent-translation verdict, on strings whose answer is arithmetic
    v = load(HERE / "r01_recovery.py", "r01").verdict
    expect("verdict exact", "exact", v("MKA*", "MKA*", "ATGAAAGCCTAA"))
    expect("verdict alt_start", "alt_start", v("LKA*", "MKA*", "TTGAAAGCCTAA"))
    expect("verdict recoded U", "recoded_stop", v("MK*A*", "MKUA*", "ATGAAATAAGCCTAA"))
    expect("verdict recoded W", "recoded_stop", v("MK*A*", "MKWA*", "ATGAAATGAGCCTAA"))
    expect("verdict mismatch", "mismatch", v("MKQA*", "MKUA*", "ATGAAACAGGCCTAA"))
    expect("verdict length mismatch", "mismatch", v("MKA", "MKA*", "ATGAAAGCC"))

    (Path(a.out) / "tables").mkdir(parents=True, exist_ok=True)
    name = "c03_positive_controls_SEEDBAD.tsv" if a.seed_bad else "c03_positive_controls.tsv"
    with (Path(a.out) / "tables" / name).open("w") as fh:
        fh.write("control\texpected\tobserved\tresult\n")
        for x in rows:
            fh.write("\t".join(str(y) for y in x) + "\n")
    print(f"c03: {len(rows)} controls, {len(fails)} failed")
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
