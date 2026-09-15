#!/usr/bin/env python3
"""c04 - positive controls for g3 geometry on a synthetic corpus with KNOWN placements.

Each fixture record places an ncRNA at a chosen offset from a chosen RT, on a chosen strand,
so direction, signed distance, overlap, intervening-CDS count and multiplicity class are known
independently of the code. The fixture is pushed through the LANDED g2 pipeline (e01 + m02) so
the controls exercise the real input path, then through this gate's p01 and a02.

Cases that must be DETECTED as ineligible or atypical are included: an ncRNA outside the
window, a missing strand, a duplicate call inside one record, and the same call arriving from a
second record of the same locus. `--seed-bad` corrupts one expectation and must fail.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import g3lib as G  # noqa: E402

RETRON = "master_Retron_merged_oriented.jsonl"


def nc(nid, s, e, strand, seq="ACGTACGTAC", region="ir1"):
    return {"ncrna_id": nid, "intergenic_region_id": region, "start": s, "end": e,
            "strand": strand, "length": e - s + 1, "evalue": 1e-12, "score": 60.5,
            "detection_model": "TypeIC1", "source": "infernal", "selection_reason": "best",
            "location_type": "intergenic", "position_relative_to_rt": None,
            "has_cds_overlap": False, "n_overlapping_cds": 0, "overlap_types": "",
            "overlapping_cds_ids": "", "upstream_gene_id": None, "downstream_gene_id": None,
            "genomic_upstream_gene_id": None, "genomic_downstream_gene_id": None,
            "orientation_corrected": True, "sequence_oriented": seq, "gc_content": 0.5,
            "free_energy": "-20.1",
            "structure_annotation": {"dot_bracket": "((..))", "free_energy": "-20.1",
                                     "structure_annotation": "SSHHSS"}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--g2-scripts", required=True, help="the landed g2 bundle's scripts/")
    ap.add_argument("--seed-bad", action="store_true")
    a = ap.parse_args()
    sys.path.insert(0, a.g2_scripts)
    import c04_controls as g2c            # the g2 fixture builders, reused verbatim
    import g2lib as G2                    # noqa: F401

    out = Path(a.out) / "fixture"
    corpus, work = out / "corpus", out / "work"
    if corpus.exists():
        shutil.rmtree(corpus)
    corpus.mkdir(parents=True)

    P = "MKAYTLGDVIRQLESAGVKEVHFVGGEPLLR"
    dna = g2c.rev_translate(P)
    import random
    rng = random.Random(7)
    ws, at = 1001, 2000
    fs = g2c.window(rng, 6000, at, dna)          # RT occupies [rs, rs+len-1]
    rs, re_ = ws + at, ws + at + len(dna) - 1
    recs, exp = [], {}

    def add(case, strand, ncs, cds_extra=(), db="gtdb_bacteria", contig=None, **e):
        cl = [g2c.cds("rt", rs, re_, strand, True, P + "*")] + list(cds_extra)
        r = g2c.record(case, contig or case, ws, fs if strand == "+" else g2c.G.revcomp(dna).join([fs[:at], fs[at + len(dna):]]),
                       rs, re_, strand, P + "*", cl, db=db, ncrnas=ncs)
        r["genomic_context"]["full_sequence"] = fs if strand == "+" else (
            fs[:at] + g2c.G.revcomp(dna) + fs[at + len(dna):])
        r["metadata"]["total_ncrnas"] = len(ncs)
        recs.append(r)
        exp[case] = e

    # gap of exactly 100 bases strictly between, both strands, both sides
    add("up_plus", "+", [nc("n1", rs - 121, rs - 101, "+")],
        direction="upstream", signed_distance_bp=-100.0, gap_bp=100.0, overlap_bp=0.0,
        same_strand=True, geometry_eligible=True, canonical=True, n_cds_between=0)
    add("down_plus", "+", [nc("n1", re_ + 101, re_ + 121, "+")],
        direction="downstream", signed_distance_bp=100.0, geometry_eligible=True, n_cds_between=0)
    add("up_minus", "-", [nc("n1", re_ + 101, re_ + 121, "-")],
        direction="upstream", signed_distance_bp=-100.0, same_strand=True, geometry_eligible=True)
    add("down_minus", "-", [nc("n1", rs - 121, rs - 101, "-")],
        direction="downstream", signed_distance_bp=100.0, geometry_eligible=True)
    add("abutting", "+", [nc("n1", rs - 21, rs - 1, "+")],
        direction="upstream", signed_distance_bp=0.0, gap_bp=0.0, overlap_bp=0.0)
    add("overlapping", "+", [nc("n1", rs - 10, rs + 9, "+")],
        direction="overlapping", signed_distance_bp=0.0, overlap_bp=10.0)
    add("opposite_strand", "+", [nc("n1", rs - 121, rs - 101, "-")],
        direction="upstream", same_strand=False, geometry_eligible=True)
    add("two_cds_between", "+", [nc("n1", rs - 1000, rs - 980, "+")],
        cds_extra=[g2c.cds("c1", rs - 900, rs - 800, "+", False),
                   g2c.cds("c2", rs - 700, rs - 600, "+", False),
                   g2c.cds("c3", re_ + 100, re_ + 200, "+", False)],
        n_cds_between=2, direction="upstream")
    add("ncrna_on_a_cds", "+", [nc("n1", rs - 880, rs - 860, "+")],
        cds_extra=[g2c.cds("c1", rs - 900, rs - 800, "+", False)],
        n_cds_overlapping_ncrna_recomputed=1, direction="upstream")
    add("outside_window", "+", [nc("n1", ws + 9000, ws + 9020, "+")],
        geometry_eligible=False, geometry_ineligible_reason="ncrna_outside_window")
    add("strand_missing", "+", [nc("n1", rs - 121, rs - 101, "")],
        geometry_eligible=False, geometry_ineligible_reason="ncrna_strand_missing")
    add("dup_in_record", "+", [nc("n1", rs - 121, rs - 101, "+"), nc("n2", rs - 121, rs - 101, "+")],
        multiplicity_class="duplicate_call_within_one_record", canonical=False)
    add("two_seqs", "+", [nc("n1", rs - 121, rs - 101, "+"), nc("n2", rs - 400, rs - 380, "+", seq="TTTTGGGGCC")],
        multiplicity_class="distinct_sequences")
    # the same locus mined from a second database: same coordinates, its own copy of the call
    add("same_locus_db2", "+", [nc("n1", rs - 121, rs - 101, "+")], db="ncbi_bacteria",
        contig="dup_locus", multiplicity_class="same_call_from_another_record_of_the_same_locus")
    recs[-1]["contig"] = "dup_locus"
    add("same_locus_db1", "+", [nc("n1", rs - 121, rs - 101, "+")], db="gtdb_bacteria",
        contig="dup_locus", multiplicity_class="same_call_from_another_record_of_the_same_locus")
    recs[-1]["contig"] = "dup_locus"
    # a record with no call at all: the zero class must see it
    add("zero_call", "+", [])

    (corpus / RETRON).write_text("\n".join(json.dumps(r) for r in recs) + "\n")

    py = sys.executable
    g2s = Path(a.g2_scripts)
    for cmd in ([py, str(g2s / "e01_extract.py"), "--corpus", str(corpus), "--out", str(work), "--procs", "2"],
                [py, str(g2s / "m02_build_tables.py"), "--work", str(work)],
                [py, str(HERE / "p01_pairs.py"), "--derived", str(work / "derived"), "--work", str(work)],
                [py, str(HERE / "a02_priors.py"), "--derived", str(work / "derived"), "--work", str(work)]):
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)

    p = pd.read_parquet(work / "derived" / "rt_ncrna_pairs_v1.parquet")
    p1 = p[p.ncrna_id.eq("n1")].set_index("rt_system_id")
    rows, fails = [], []

    def expect(name, want, got):
        ok = (want == got) or (pd.isna(want) and pd.isna(got))
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(name)

    for case, e in exp.items():
        for field, want in e.items():
            if case not in p1.index:
                expect(f"{case}:{field}", want, "<no placement>")
                continue
            v = p1.loc[case, field]
            got = v.iloc[0] if isinstance(v, pd.Series) else v
            expect(f"{case}:{field}", want, got)
    if a.seed_bad:
        expect("up_plus:signed_distance_bp", 999.0, p1.loc["up_plus", "signed_distance_bp"])

    # the geometry helpers themselves, on values whose answer is arithmetic
    expect("gap_bp abutting", 0, G.gap_bp(100, 200, 80, 99))
    expect("gap_bp 1 base between", 1, G.gap_bp(100, 200, 80, 98))
    expect("overlap_len book-ended is 0", 0, G.overlap_len(100, 200, 80, 99))
    expect("overlap_len 1 base", 1, G.overlap_len(100, 200, 80, 100))
    expect("direction minus strand higher coords is upstream", "upstream",
           G.direction(100, 200, "-", 300, 320))
    expect("signed distance is None without a strand", None, G.signed_distance(100, 200, "", 300, 320))
    expect("bin_label boundary 100 is <=100", "51-100", G.bin_label(100, G.DIST_BINS))
    expect("bin_label 101 is the next bin", "101-200", G.bin_label(101, G.DIST_BINS))

    # the zero class must count the call-free record
    z = pd.read_csv(work / "tables" / "g3_zero_class_by_family.tsv", sep="\t")
    expect("zero_class_counts_the_call_free_locus", 1,
           int(z.loc[z.file_label.eq("Retron"), "n_loci_zero_ncrna"].iloc[0]))

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
