#!/usr/bin/env python3
"""c04 - positive controls for g4.

Two halves:
  (1) a synthetic corpus with known family membership, known lengths and known completeness
      evidence, pushed through the landed g2 pipeline and then b01. The view assignment, the
      three-state completeness (a MISSING Prodigal flag must never be read as "partial") and
      the within-family Tukey fences must all come out as constructed.
  (2) h02's profile->family mapping, domtbl parsing and margin arithmetic, on values whose
      answer is known - including the two names whose mapping the first version got wrong.

`--seed-bad` corrupts one expectation and must fail.
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
FAM_A = "master_RVT-UG5_merged_oriented.jsonl"      # the big synthetic family
FAM_B = "master_RVT-UG9_merged_oriented.jsonl"      # a family below MIN_GROUP
RETRON = "master_Retron_merged_oriented.jsonl"
MULTI = "master_MULTI_merged_oriented.jsonl"


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
    rng = random.Random(11)
    files: dict[str, list] = {FAM_A: [], FAM_B: [], RETRON: [], MULTI: []}

    def make(case, fname, aa_len, *, partial="00", with_rt_cds=True, types=None, contig=None):
        """One record whose RT protein has exactly `aa_len` residues."""
        prot = "M" + "".join(rng.choice("ACDEFGHIKLMNPQRSTVWY") for _ in range(aa_len - 1))
        dna = g2c.rev_translate(prot)
        ws, at = 1001, 200
        fs = g2c.window(rng, max(3000, len(dna) + 1000), at, dna)
        rs, re_ = ws + at, ws + at + len(dna) - 1
        cl = [g2c.cds("c", rs, re_, "+", True, prot + "*", partial=partial)] if with_rt_cds else []
        r = g2c.record(case, contig or case, ws, fs, rs, re_, "+", prot + "*", cl,
                       types=types or [fname.split("_")[1]])
        files[fname].append(r)
        return prot

    # family A: 40 sequences at length 300, plus two at 900 -> outliers above the fence
    for i in range(40):
        make(f"a{i}", FAM_A, 300)
    make("a_out1", FAM_A, 900)
    make("a_out2", FAM_A, 910)
    # family B: 5 sequences -> below MIN_GROUP, no fences
    for i in range(5):
        make(f"b{i}", FAM_B, 400)
    # completeness cases in Retron
    make("comp_complete", RETRON, 310, partial="00", types=["Retron"])
    make("comp_partial", RETRON, 320, partial="01", types=["Retron"])
    make("comp_no_prodigal", RETRON, 330, with_rt_cds=False, types=["Retron"])
    # one protein in two family files -> V-RT-CROSS
    p_cross = make("cross_a", FAM_A, 555)
    dna = g2c.rev_translate(p_cross)
    ws, at = 1001, 200
    fs = g2c.window(rng, 3000, at, dna)
    rs, re_ = ws + at, ws + at + len(dna) - 1
    files[RETRON].append(g2c.record("cross_b", "cross_b", ws, fs, rs, re_, "+", p_cross + "*",
                                    [g2c.cds("c", rs, re_, "+", True, p_cross + "*")],
                                    types=["Retron"]))
    make("multi1", MULTI, 280, types=["RVT-UG5/Retron"])

    for fname, recs in files.items():
        (corpus / fname).write_text("\n".join(json.dumps(r) for r in recs) + "\n")

    py = sys.executable
    g2s = Path(a.g2_scripts)
    for cmd in ([py, str(g2s / "e01_extract.py"), "--corpus", str(corpus), "--out", str(work), "--procs", "2"],
                [py, str(g2s / "m02_build_tables.py"), "--work", str(work)]):
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    # b01 needs a pair table; an empty one is enough for the RT half of the baseline
    pd.DataFrame({"nc_seq_hash": [], "nc_seq_len": [], "detection_model": [], "file_label": [],
                  "geometry_eligible": [], "canonical": [], "locus_key": [], "tax_species": [],
                  "evalue": [], "score": [], "has_structure_annotation": []}).to_parquet(
        work / "derived" / "rt_ncrna_pairs_v1.parquet", index=False)
    subprocess.run([py, str(HERE / "b01_baseline.py"), "--derived", str(work / "derived"),
                    "--work", str(work)], check=True, stdout=subprocess.DEVNULL)

    base = pd.read_parquet(work / "derived" / "rt_family_baseline_v1.parquet")
    rec = pd.read_parquet(work / "derived" / "rt_records_v1.parquet",
                          columns=["rt_system_id", "rt_seq_hash"])
    h = dict(zip(rec.rt_system_id, rec.rt_seq_hash))
    b = base.set_index("rt_seq_hash")
    ln = pd.read_csv(work / "tables" / "g4_rt_length_by_family.tsv", sep="\t")
    comp = pd.read_csv(work / "tables" / "g4_completeness_by_family.tsv", sep="\t")
    rows, fails = [], []

    def expect(name, want, got):
        ok = want == got
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(name)

    expect("view:single", "V-RT-SINGLE", b.loc[h["a0"], "view"])
    expect("view:cross_labelled_protein", "V-RT-CROSS", b.loc[h["cross_a"], "view"])
    expect("view:multi", "V-RT-MULTI", b.loc[h["multi1"], "view"])
    expect("completeness:prodigal_complete", "all_complete", b.loc[h["comp_complete"], "completeness_class"])
    expect("completeness:prodigal_partial", "all_partial", b.loc[h["comp_partial"], "completeness_class"])
    expect("completeness:no_prodigal_call_is_NOT_partial", "mixed_or_codon_evidence",
           b.loc[h["comp_no_prodigal"], "completeness_class"])
    a_row = ln[ln.family_label.eq("RVT-UG5")].iloc[0]
    expect("fences_declared_for_a_family_above_MIN_GROUP", True, bool(a_row.fences_declared))
    expect("fence_high_is_finite", True, float(a_row.fence_high) > 0)
    b_row = ln[ln.family_label.eq("RVT-UG9")].iloc[0]
    expect("no_fences_below_MIN_GROUP", False, bool(b_row.fences_declared))
    outl = pd.read_csv(work / "tables" / "g4_rt_length_named_outliers.tsv", sep="\t")
    expect("the two long sequences are named outliers", 2,
           int(outl[outl.family_label.eq("RVT-UG5") & outl.side.eq("above")].shape[0]))
    expect("no outlier is reported for the small family", 0,
           int(outl[outl.family_label.eq("RVT-UG9")].shape[0]))
    expect("completeness table never says partial for the missing flag", 0,
           int(comp[comp.family_label.eq("Retron") & comp.completeness_class.eq("all_partial")
                    & comp.n_exact_rt.gt(1)].shape[0]))
    if a.seed_bad:
        expect("view:single", "V-RT-MULTI", b.loc[h["a0"], "view"])

    # ---- h02's mapping, parsing and margins -----------------------------------------
    h02 = load(HERE / "h02_multi_hmm.py", "h02")
    expect("profile RVT-GII-I maps to RVT-GII", "RVT-GII", h02.family_of_profile("RVT-GII-I"))
    expect("profile RVT-GII-II maps to RVT-GII", "RVT-GII", h02.family_of_profile("RVT-GII-II"))
    expect("profile RVT-Retrons maps to Retron", "Retron", h02.family_of_profile("RVT-Retrons"))
    expect("profile RVT-CRISPR-G3 maps to RVT-CRISPR", "RVT-CRISPR", h02.family_of_profile("RVT-CRISPR-G3"))
    expect("profile RVT-UG5 maps to itself", "RVT-UG5", h02.family_of_profile("RVT-UG5"))
    dom = out / "mini.domtbl"
    dom.write_text(
        "# a synthetic domtblout\n"
        + " ".join(["seqA", "-", "300", "RVT-UG5", "-", "300", "1e-40", "120.0", "0.0", "1", "1",
                    "1e-40", "1e-40", "100.5", "0.0"] + ["-"] * 8) + "\n"
        + " ".join(["seqA", "-", "300", "RVT-GII-I", "-", "300", "1e-10", "40.0", "0.0", "1", "1",
                    "1e-10", "1e-10", "30.5", "0.0"] + ["-"] * 8) + "\n")
    parsed = h02.parse_domtbl(dom)
    expect("domtbl parsed rows", 2, len(parsed))
    bt = h02.best_two(parsed)
    expect("best family", "RVT-UG5", bt.best_family.iloc[0])
    expect("second family", "RVT-GII", bt.second_family.iloc[0])
    expect("margin in bits", 70.0, float(bt.margin_bits.iloc[0]))

    (Path(a.out) / "tables").mkdir(parents=True, exist_ok=True)
    name = "c04_positive_controls_SEEDBAD.tsv" if a.seed_bad else "c04_positive_controls.tsv"
    with (Path(a.out) / "tables" / name).open("w") as fh:
        fh.write("control\texpected\tobserved\tresult\n")
        for r in rows:
            fh.write("\t".join(str(v) for v in r) + "\n")
    print(f"c04: {len(rows)} controls, {len(fails)} failed")
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
