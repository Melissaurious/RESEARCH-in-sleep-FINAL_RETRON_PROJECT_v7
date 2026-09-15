#!/usr/bin/env python3
"""c04 - positive controls for g2 on a synthetic corpus with KNOWN ground truth.

The fixture is built, not sampled: each record's window DNA is generated from a chosen
protein, so the expected back-translation verdict, RT-CDS class, eligibility flags and unit
keys are known independently of the code under test. Cases that MUST be detected as broken
(a one-base frameshift, a flipped strand, a conflicting RT at one locus) are included -
a check validated only on cases it should accept has been demonstrated, not tested
(EVIDENCE_STANDARDS section 6).

The shipped e01, a02 and c03 then run end to end on the fixture as subprocesses.
`--seed-bad` corrupts one expectation; the run must exit non-zero.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import g2lib as G  # noqa: E402

SEED = 20260915
RETRON = "master_Retron_merged_oriented.jsonl"
UG2 = "master_RVT-UG2_merged_oriented.jsonl"
MULTI = G.MULTI_FILE
BACK = {}                      # one codon per amino acid, table 11
for _c, _a in G.CODON11.items():
    BACK.setdefault(_a, _c)


def rev_translate(prot: str, start_codon: str = "ATG", stop_codon: str = "TAA",
                  recode: dict[int, str] | None = None) -> str:
    """DNA whose table-11 translation is `prot` (+ terminal stop), with optional per-position
    codon overrides used to build the recoding controls."""
    out = [start_codon]
    for i, aa in enumerate(prot[1:], start=1):
        out.append((recode or {}).get(i) or BACK[aa])
    return "".join(out) + stop_codon


def window(rng: random.Random, length: int, insert_at: int, dna: str) -> str:
    filler = "".join(rng.choice("ACGT") for _ in range(length))
    return filler[:insert_at] + dna + filler[insert_at + len(dna):]


def cds(gene_id, start, end, strand, is_rt, seq=None, partial="00", start_type="ATG"):
    c = {"gene_id": gene_id, "contig": "C", "start": start, "end": end, "strand": strand,
         "length": end - start + 1, "is_rt_gene": is_rt,
         "prodigal_metadata": {"partial": partial, "start_type": start_type,
                               "rbs_motif": "AGGAG", "rbs_spacer": "5bp", "gc_cont": 0.5}}
    if seq is not None:
        c["sequence"] = seq
    return c


def record(case, contig, win_start, fullseq, rt_start, rt_end, strand, protein,
           cds_list, *, db="gtdb_bacteria", genome="RS_GCF_000001.1", types=None,
           ncrnas=None, win_end=None, types_raw=None):
    we = win_end if win_end is not None else win_start + len(fullseq) - 1
    ncr = ncrnas or []
    return {
        "rt_system_id": case, "contig": contig, "anchor_type": "RT",
        "system_types": types_raw if types_raw is not None else (types or ["Retron"]),
        "system_subtypes": [],
        "genomic_context": {"actual_window": {"start": win_start, "end": we,
                                              "clipped_at_contig_start": False,
                                              "clipped_at_contig_end": False},
                            "full_sequence": fullseq, "length": len(fullseq),
                            "extended_for_cds": False},
        "cds_annotations": cds_list, "intergenic_regions": [], "ncrnas": ncr,
        "metadata": {"detected_by": ["myRT"], "total_genes": len(cds_list),
                     "total_intergenic_regions": 0, "total_ncrnas": len(ncr)},
        "rt_gene": {"start": rt_start, "end": rt_end, "strand": strand,
                    "length": rt_end - rt_start + 1, "sequence": protein},
        "genome_id": genome,
        "taxonomy": {"taxonomy_system": "gtdb", "environment": "mixed", "domain": "Bacteria",
                     "phylum": "P", "class": "C", "order": "O", "family": "F", "genus": "G",
                     "species": "S", "full_lineage": "d__Bacteria;p__P"},
        "anchor_gene_id": "g1", "anchor_start": rt_start, "anchor_end": rt_end,
        "anchor_strand": strand, "anchor_center": (rt_start + rt_end) // 2,
        "source_database": db,
    }


def build(corpus: Path) -> tuple[dict[str, dict], dict[str, list]]:
    rng = random.Random(SEED)
    P1 = "MKAYTLGDVIRQLESAGVKEVHFVGGEPLLR"          # 31 aa
    P2 = "MTTQLIVNGKEYRVSDLAREHNLSLSTVSRW"
    files: dict[str, list] = {RETRON: [], UG2: [], MULTI: []}
    exp: dict[str, dict] = {}

    def add(fname, rec, **expect):
        files[fname].append(rec)
        exp[rec["rt_system_id"]] = expect

    # 1 plus-strand exact
    dna = rev_translate(P1)
    ws, at = 1001, 200
    fs = window(rng, 2000, at, dna)
    rs = ws + at
    add(RETRON, record("plus_exact", "C1", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C1_1", rs, rs + len(dna) - 1, "+", True, P1 + "*")]),
        bt_status="exact", no_rt_cds_class="has_rt_cds", elig_rt_coords=True, elig_geometry=True)

    # 2 minus-strand exact
    fs2 = window(rng, 2000, at, G.revcomp(dna))
    add(RETRON, record("minus_exact", "C2", ws, fs2, rs, rs + len(dna) - 1, "-", P1 + "*",
                       [cds("C2_1", rs, rs + len(dna) - 1, "-", True, P1 + "*")]),
        bt_status="exact", no_rt_cds_class="has_rt_cds", elig_rt_coords=True, elig_geometry=True)

    # 3 alternative start codon reported as M
    dna3 = rev_translate(P1, start_codon="TTG")
    fs3 = window(rng, 2000, at, dna3)
    add(RETRON, record("alt_start", "C3", ws, fs3, rs, rs + len(dna3) - 1, "+", P1 + "*",
                       [cds("C3_1", rs, rs + len(dna3) - 1, "+", True, P1 + "*", start_type="TTG")]),
        bt_status="alt_start", no_rt_cds_class="has_rt_cds", elig_rt_coords=True)

    # 4 translation table 4: internal TGA read as W
    p4 = P1[:10] + "W" + P1[11:]
    dna4 = rev_translate(p4, recode={10: "TGA"})
    fs4 = window(rng, 2000, at, dna4)
    add(RETRON, record("code4", "C4", ws, fs4, rs, rs + len(dna4) - 1, "+", p4 + "*",
                       [cds("C4_1", rs, rs + len(dna4) - 1, "+", True, p4 + "*")]),
        bt_status="code4_tga_trp", no_rt_cds_class="has_rt_cds", elig_rt_coords=True)

    # 5 internal stop written as U in the protein
    p5 = P1[:12] + "U" + P1[13:]
    dna5 = rev_translate(p5, recode={12: "TAA"})
    fs5 = window(rng, 2000, at, dna5)
    add(RETRON, record("stop_masked", "C5", ws, fs5, rs, rs + len(dna5) - 1, "+", p5 + "*",
                       [cds("C5_1", rs, rs + len(dna5) - 1, "+", True, p5 + "*")]),
        bt_status="internal_stop_masked", no_rt_cds_class="has_rt_cds", elig_rt_coords=True)

    # 6 one-base frameshift - MUST be caught
    add(RETRON, record("frameshift", "C6", ws, fs, rs + 1, rs + len(dna), "+", P1 + "*",
                       [cds("C6_1", rs + 1, rs + len(dna), "+", True, P1 + "*")]),
        bt_status="mismatch", no_rt_cds_class="has_rt_cds", elig_rt_coords=False, elig_geometry=False)

    # 7 strand recorded as + while the ORF is on - : a strand error, not a frame error
    add(RETRON, record("strand_flipped", "C7", ws, fs2, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C7_1", rs, rs + len(dna) - 1, "+", True, P1 + "*")]),
        bt_status="matches_opposite_strand", no_rt_cds_class="has_rt_cds", elig_rt_coords=False)

    # 8 RT beyond the window (the MAG pattern)
    add(RETRON, record("rt_outside", "C8", ws, fs, ws + 5000, ws + 5000 + len(dna) - 1, "+", P1 + "*", []),
        bt_status="not_testable_rt_outside_window", no_rt_cds_class="rt_outside_window",
        elig_rt_coords=False, elig_exact_rt=True)

    # 9 inverted window with an empty sequence
    r9 = record("inverted", "C9", 5000, "", 9000, 9000 + len(dna) - 1, "+", P1 + "*", [], win_end=3000)
    add(RETRON, r9, bt_status="not_testable_window_inverted",
        no_rt_cds_class="context_absent_window_inverted", elig_geometry=False, elig_exact_rt=True)

    # 10/11 no is_rt_gene CDS, back-translation verified, with and without an overlapping CDS
    add(RETRON, record("nortcds_overlap", "C10", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C10_1", rs - 30, rs + 60, "+", False)]),
        bt_status="exact", no_rt_cds_class="no_prodigal_call_bt_verified_overlapping_cds",
        elig_rt_coords=True, elig_rt_completeness=True)
    add(RETRON, record("nortcds_nooverlap", "C11", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C11_1", ws + 1500, ws + 1600, "+", False)]),
        bt_status="exact", no_rt_cds_class="no_prodigal_call_bt_verified_no_overlapping_cds",
        elig_rt_coords=True)

    # 12 window shorter than its declared span
    add(RETRON, record("win_len_bad", "C12", ws, fs[:-10], rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C12_1", rs, rs + len(dna) - 1, "+", True, P1 + "*")], win_end=ws + 1999),
        bt_status="not_testable_window_length_inconsistent", no_rt_cds_class="has_rt_cds",
        elig_geometry=False, elig_exact_rt=True)

    # 13 malformed protein: an internal stop in the REPORTED sequence
    add(RETRON, record("bad_protein", "C13", ws, fs, rs, rs + len(dna) - 1, "+", P1[:10] + "*" + P1[11:] + "*",
                       [cds("C13_1", rs, rs + len(dna) - 1, "+", True)]),
        elig_exact_rt=False, elig_rt_coords=False)

    # 14 an ncRNA call rides along on an otherwise clean record
    nc = {"ncrna_id": "ncrna_001", "intergenic_region_id": "ir1", "start": rs + 200, "end": rs + 320,
          "strand": "+", "length": 121, "evalue": 1e-12, "score": 60.5, "detection_model": "TypeIC1",
          "source": "infernal", "selection_reason": "best", "location_type": "intergenic",
          "position_relative_to_rt": None, "has_cds_overlap": False, "n_overlapping_cds": 0,
          "overlap_types": "", "overlapping_cds_ids": "", "upstream_gene_id": "C14_1",
          "downstream_gene_id": None, "genomic_upstream_gene_id": "C14_1",
          "genomic_downstream_gene_id": None, "orientation_corrected": True,
          "sequence_oriented": "ACGTACGTAC", "gc_content": 0.5, "free_energy": "-20.1",
          "structure_annotation": {"dot_bracket": "((..))", "free_energy": "-20.1",
                                   "structure_annotation": "SSHHSS"}}
    add(RETRON, record("with_ncrna", "C14", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C14_1", rs, rs + len(dna) - 1, "+", True, P1 + "*")], ncrnas=[nc]),
        bt_status="exact", no_rt_cds_class="has_rt_cds", elig_geometry=True)

    # 15 the same locus mined from a second database (different bytes, same locus key)
    add(RETRON, record("plus_exact_db2", "C1", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("C1_1", rs, rs + len(dna) - 1, "+", True, P1 + "*")],
                       db="ncbi_bacteria", genome="GB_GCA_000001.1"),
        bt_status="exact", no_rt_cds_class="has_rt_cds")

    # 16 RefSeq/GenBank twin with identical window DNA and RT -> collapse supported
    add(RETRON, record("twin_refseq", "NZ_C15", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("x", rs, rs + len(dna) - 1, "+", True, P1 + "*")], db="ncbi_bacteria"),
        bt_status="exact")
    add(RETRON, record("twin_genbank", "C15", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("x", rs, rs + len(dna) - 1, "+", True, P1 + "*")], db="gtdb_bacteria"),
        bt_status="exact")

    # 17 twin whose RT proteins disagree -> must NOT collapse
    dna17 = rev_translate(P2)
    fs17 = window(rng, 2000, at, dna17)
    add(RETRON, record("twin_bad_refseq", "NZ_C16", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                       [cds("y", rs, rs + len(dna) - 1, "+", True, P1 + "*")]),
        bt_status="exact")
    add(RETRON, record("twin_bad_genbank", "C16", ws, fs17, rs, rs + len(dna17) - 1, "+", P2 + "*",
                       [cds("y", rs, rs + len(dna17) - 1, "+", True, P2 + "*")]),
        bt_status="exact")

    # 18 two different RT proteins at ONE locus key -> rt_hash_conflict
    add(UG2, record("conflict_a", "C17", ws, fs, rs, rs + len(dna) - 1, "+", P1 + "*",
                    [cds("z", rs, rs + len(dna) - 1, "+", True, P1 + "*")], types=["RVT-UG2"]),
        bt_status="exact")
    add(UG2, record("conflict_b", "C17", ws, fs17, rs, rs + len(dna) - 1, "+", P2 + "*",
                    [cds("z", rs, rs + len(dna) - 1, "+", True, P2 + "*")], types=["RVT-UG2"]),
        bt_status="exact")

    # 19 a multi-label record inside a single-family file
    add(UG2, record("multilabel_in_family", "C18", ws, fs17, rs, rs + len(dna17) - 1, "+", P2 + "*",
                    [cds("m", rs, rs + len(dna17) - 1, "+", True, P2 + "*")],
                    types_raw=["RVT-UG2", "Retron"]), bt_status="exact")

    # 20 a MULTI-file record with a slash-joined label
    add(MULTI, record("multi_file_record", "C19", ws, fs17, rs, rs + len(dna17) - 1, "+", P2 + "*",
                      [cds("mm", rs, rs + len(dna17) - 1, "+", True, P2 + "*")],
                      types_raw=["RVT-UG2/Retron"]), bt_status="exact")

    if corpus.exists():
        shutil.rmtree(corpus)
    corpus.mkdir(parents=True)
    for fname, recs in files.items():
        lines = [json.dumps(r) for r in recs]
        if fname == RETRON:                       # 21 a byte-identical duplicate line
            lines.append(lines[0])
        (corpus / fname).write_text("\n".join(lines) + "\n")
    return exp, files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed-bad", action="store_true")
    a = ap.parse_args()
    out = Path(a.out) / "fixture"
    corpus, work = out / "corpus", out / "work"
    exp, files = build(corpus)
    if work.exists():
        shutil.rmtree(work)
    py = sys.executable
    subprocess.run([py, str(HERE / "e01_extract.py"), "--corpus", str(corpus), "--out", str(work),
                    "--procs", "2"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([py, str(HERE / "m02_build_tables.py"), "--work", str(work)], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([py, str(HERE / "a02_units.py"), "--work", str(work)], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run(["bash", str(HERE / "c03_second_count.sh"), str(corpus), str(work), "2"],
                   check=True, stdout=subprocess.DEVNULL)

    r = pd.read_parquet(work / "derived" / "rt_records_v1.parquet").set_index("rt_system_id")
    lo = pd.read_parquet(work / "derived" / "rt_loci_v1.parquet")
    ph = pd.read_parquet(work / "derived" / "rt_physical_loci_v1.parquet")
    nc = pd.read_parquet(work / "derived" / "rt_ncrna_calls_v1.parquet")
    ladder = {x["unit"]: int(x["n"]) for x in csv.DictReader(
        (work / "tables" / "g2_unit_ladder.tsv").open(), delimiter="\t")}
    dist = {x["measure"]: int(x["n"]) for x in csv.DictReader(
        (work / "second" / "c03_distinct.tsv").open(), delimiter="\t")}

    rows, fails = [], []

    def expect(name, want, got):
        ok = want == got
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(name)

    def cell(case, field):
        """One value, even where a case has two rows (the duplicated line)."""
        v = r.loc[case, field]
        return v.iloc[0] if isinstance(v, pd.Series) else v

    n_records = sum(len(v) for v in files.values()) + 1        # + the duplicated line
    for case, e in exp.items():
        for field, want in e.items():
            expect(f"{case}:{field}", want, cell(case, field))
    if a.seed_bad:
        expect("plus_exact:bt_status", "mismatch", cell("plus_exact", "bt_status"))

    expect("records", n_records, len(r))
    expect("distinct_raw_records", n_records - 1, ladder["distinct_raw_record"])
    expect("duplicate_line_extra_copies", 1, n_records - ladder["distinct_raw_record"])
    # C1 carries three records (two databases + the duplicated line) on ONE locus key
    expect("locus_C1_records", 3, int(lo.loc[lo.contig.eq("C1"), "n_records"].iloc[0]) + 1)
    expect("loci", len({("C1", 1), ("C2",), ("C3",), ("C4",), ("C5",), ("C6",), ("C7",), ("C8",),
                        ("C9",), ("C10",), ("C11",), ("C12",), ("C13",), ("C14",), ("NZ_C15",),
                        ("C15",), ("NZ_C16",), ("C16",), ("C17",), ("C18",), ("C19",)}),
           ladder["locus"])
    expect("physical_loci", ladder["locus"] - 2, ladder["physical_locus"])   # two NZ_ twins fold
    expect("twin_identical_window_dna_and_rt", 1, int(
        (ph.twin_evidence_class == "twin_identical_window_dna_and_rt").sum()))
    expect("twin_disagree", 1, int((ph.twin_evidence_class == "twin_disagree").sum()))
    expect("collapse_supported_excludes_the_bad_twin", ladder["physical_locus"] - 1,
           ladder["physical_locus_collapse_supported"])
    expect("locus_with_two_exact_rts", 1, int((lo.n_rt_hashes > 1).sum()))
    expect("ncrna_calls", 1, len(nc))
    expect("ncrna_seq_hash", G.hashlib.sha256(b"ACGTACGTAC").hexdigest(), nc.nc_seq_hash.iloc[0])
    expect("multilabel_records", 2, int(r.multilabel.sum()))
    expect("multi_population_records", 1, int(r.file_label.eq("MULTI").sum()))

    # the independent route must agree with the derived tables
    expect("c03_lines", n_records, dist["lines_total"])
    expect("c03_distinct_locus_key", ladder["locus"], dist["distinct_locus_key"])
    expect("c03_distinct_exact_rt", ladder["exact_rt"], dist["distinct_exact_rt_sequence"])
    expect("c03_lines_without_is_rt_gene_true", int((r.n_rt_cds == 0).sum()),
           dist["lines_without_is_rt_gene_true"])
    expect("c03_window_inverted", int(r.window_inverted.sum()), dist["window_inverted"])
    expect("c03_rt_not_inside_window", int((~r.rt_in_window).sum()), dist["rt_not_inside_window"])

    (Path(a.out) / "tables").mkdir(parents=True, exist_ok=True)
    name = "c04_positive_controls_SEEDBAD.tsv" if a.seed_bad else "c04_positive_controls.tsv"
    with (Path(a.out) / "tables" / name).open("w") as fh:
        fh.write("control\texpected\tobserved\tresult\n")
        for x in rows:
            fh.write("\t".join(str(v) for v in x) + "\n")
    print(f"c04: {len(rows)} controls, {len(fails)} failed")
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
