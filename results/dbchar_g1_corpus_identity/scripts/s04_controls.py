#!/usr/bin/env python3
"""s04 - positive controls: every parse class, every check and both count routes must FIRE.

The fixture base is the schema document's own worked example record, placed in the file
whose role it documents. Its expected flag set is empty BY DOCUMENTATION, not by asking the
classifier. Each fixture line is one declared mutation with a hand-written expected flag set.

The shipped s02 (census) and s03 (grep second count) are then run end to end, as
subprocesses, on the fixture corpus, and their landed-format tables are compared with the
expected counts. A check that cannot fire on a known-present case has not measured absence
(EVIDENCE_STANDARDS section 6).

`--seed-bad` corrupts one expected count; the run must then exit non-zero, which run.sh
requires before it trusts a passing run (WA-A.3).
"""
from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import g1lib as L  # noqa: E402

RETRON = "master_Retron_merged_oriented.jsonl"
GII = "master_RVT-GII_merged_oriented.jsonl"
UG9 = "master_RVT-UG9_merged_oriented.jsonl"


def schema_example(schema_md: Path) -> dict:
    m = re.search(r"### Example record:\s*```json\s*(\{.*?\})\s*```", schema_md.read_text(), re.S)
    if not m:
        raise SystemExit("schema example record not found - fixture cannot be built")
    return json.loads(m.group(1))


def build(base: dict) -> list[tuple[str, bytes, str, set, str | None, str | None]]:
    """(file, raw line, parse class, expected flags, anchor token, database token)."""
    def j(o: dict) -> bytes:
        return json.dumps(o).encode()

    def mut(fn) -> dict:
        o = copy.deepcopy(base)
        fn(o)
        return o

    def nc(o: dict) -> None:  # a documented-clean ncRNA-anchored record
        o["anchor_type"] = "ncRNA"
        o["system_types"] = ["ncRNA-anchored"]
        o["rt_gene"] = None
        for c in o["cds_annotations"]:
            c["is_rt_gene"] = False

    db = base["source_database"]
    F = []

    def add(fname, o, flags, pc="ok", raw=None, a="RT", d=db):
        F.append((fname, raw if raw is not None else j(o), pc, set(flags), a, d))

    add(RETRON, base, [])
    add(RETRON, None, [], pc="blank", raw=b"   ", a=None, d=None)
    add(RETRON, None, [], pc="bad_utf8", raw=j(base).replace(b"Retron_I_A", b"Retron_\xff"), a="RT", d=db)
    add(RETRON, None, [], pc="bad_json", raw=j(base)[:-40], a="RT", d=None)
    add(RETRON, None, [], pc="not_object", raw=b"[1, 2, 3]", a=None, d=None)
    add(RETRON, mut(lambda o: o.update(rt_system_id="")), ["V01"])
    add(RETRON, mut(lambda o: o.update(anchor_type="XX")), ["V02", "V03"], a="XX")
    add(RETRON, mut(lambda o: o.update(source_database=None)), ["V04"], d="null")
    add(RETRON, mut(lambda o: o.update(system_types=[])), ["V05", "V06"])
    add(GII, base, ["V06"])
    add(RETRON, mut(lambda o: o["rt_gene"].update(sequence="")), ["V07"])
    add(RETRON, mut(lambda o: [c.update(is_rt_gene=False) for c in o["cds_annotations"]]), ["V09a"])
    add(RETRON, mut(lambda o: [c.update(is_rt_gene=True) for c in o["cds_annotations"]]), ["V09b"])
    add(L.NCRNA_FILE, mut(nc), [], a="ncRNA")
    add(L.NCRNA_FILE, base, ["V03", "V06"])
    add(L.NCRNA_FILE, mut(lambda o: (nc(o), o.update(rt_gene=base["rt_gene"]))), ["V08"], a="ncRNA")
    add(L.NCRNA_FILE, mut(lambda o: (nc(o), o["cds_annotations"][0].update(is_rt_gene=True))), ["V10"], a="ncRNA")
    add(L.NCRNA_FILE, mut(lambda o: (nc(o), o.update(ncrnas=[]), o["metadata"].update(total_ncrnas=0),
                                     [r.update(has_ncrna=False) for r in o["intergenic_regions"]])),
        ["V11"], a="ncRNA")
    add(L.MULTI_FILE, mut(lambda o: o.update(system_types=["RVT-GII/Retron"])), [])
    add(L.MULTI_FILE, base, ["V06"])
    add(RETRON, mut(lambda o: o["metadata"].update(total_ncrnas=5)), ["V12"])
    add(RETRON, mut(lambda o: o["metadata"].update(total_genes=9)), ["V13"])
    add(RETRON, mut(lambda o: o["metadata"].update(total_intergenic_regions=9)), ["V14"])
    add(RETRON, mut(lambda o: o["genomic_context"].update(length=o["genomic_context"]["length"] + 1)), ["V15"])
    add(RETRON, mut(lambda o: o["genomic_context"]["actual_window"].update(start=5000, end=10)), ["V16"])
    add(RETRON, mut(lambda o: (o.update(ncrnas=[]), o["metadata"].update(total_ncrnas=0))), ["V17"])
    add(RETRON, mut(lambda o: o.pop("genome_id")), ["V18", "V21a"])
    add(RETRON, mut(lambda o: o.update(contig="")), ["V19"])
    add(RETRON, mut(lambda o: o.pop("taxonomy")), ["V20a", "V21a"])
    add(RETRON, mut(lambda o: o["taxonomy"].update(taxonomy_system="ncbi")), ["V20b"])
    add(RETRON, mut(lambda o: o.update(extra_key=1)), ["V21b"])
    add(RETRON, mut(lambda o: o.update(system_types=["Retron", "RVT-UG10"])), [])
    add(RETRON, base, [])  # byte-identical duplicate of line 1, same file
    add(GII, base, ["V06"])  # byte-identical duplicate of line 1, another file
    return F


def write_fixture(F, corpus: Path) -> dict:
    if corpus.exists():
        shutil.rmtree(corpus)
    corpus.mkdir(parents=True)
    by_file: dict[str, list[bytes]] = {}
    for fname, raw, *_ in F:
        by_file.setdefault(fname, []).append(raw)
    for fname, lines in by_file.items():
        (corpus / fname).write_bytes(b"\n".join(lines) + b"\n")
    # UG9: one CRLF line and an unterminated final line - the byte-level cases s01/s03 must see
    base_line = F[0][1]
    (corpus / UG9).write_bytes(base_line + b"\r\n" + base_line)
    return {f: len(v) for f, v in by_file.items()}


def read_tsv(p: Path) -> list[dict]:
    with p.open() as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prior-g0", required=True, help="prior g0 bundle root (s05 reads its tables)")
    ap.add_argument("--seed-bad", action="store_true")
    a = ap.parse_args()
    out = Path(a.out) / "fixture"
    corpus = out / "corpus"
    base = schema_example(Path(a.schema))
    F = build(base)
    write_fixture(F, corpus)

    fails: list[str] = []
    rows: list[list] = []

    def expect(name, want, got):
        ok = want == got
        rows.append([name, want, got, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(name)

    # -- 1. the classifier, line by line, against hand-written expectations -------------
    doc_top = L.documented_top_level(L.documented_paths(Path(a.schema)))
    fired_total = Counter()
    for i, (fname, raw, pc, flags, *_ ) in enumerate(F, 1):
        got_pc, rec = L.parse_line(raw)
        got = set(L.validate(rec, fname, doc_top)) if rec is not None else set()
        expect(f"line{i:02d}:{fname}:parse_class", pc, got_pc)
        expect(f"line{i:02d}:{fname}:flags", "|".join(sorted(flags)), "|".join(sorted(got)))
        fired_total.update(got)
    never = sorted(set(L.CHECKS) - set(fired_total))
    expect("every_declared_check_fires_at_least_once", "", "|".join(never))
    expect("every_parse_class_occurs", "|".join(sorted(L.PARSE_CLASSES)),
           "|".join(sorted({pc for _, _, pc, *_ in F})))

    # -- 2. chunk tiling: a small chunk size must tile the file exactly on newlines ------
    spec = importlib.util.spec_from_file_location("s02", HERE / "s02_record_census.py")
    s02 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s02)
    s02.CHUNK_BYTES = 3000
    p = corpus / RETRON
    data = p.read_bytes()
    ch = s02.chunks_of(p)
    tiles = ch[0][0] == 0 and ch[-1][1] == len(data) and all(ch[k][1] == ch[k + 1][0] for k in range(len(ch) - 1))
    on_nl = all(data[e - 1:e] == b"\n" for _, e in ch)
    expect("chunks_tile_file_on_newline_boundaries(>1 chunk)", "True|True|True", f"{tiles}|{on_nl}|{len(ch) > 1}")

    # -- 3. the shipped s01, s02 and s03, end to end, on the fixture corpus --------------
    work = out / "work"
    if work.exists():
        shutil.rmtree(work)
    py = sys.executable
    subprocess.run([py, str(HERE / "s01_file_identity.py"), "--corpus", str(corpus), "--out", str(work),
                    "--procs", "2"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([py, str(HERE / "s02_record_census.py"), "--corpus", str(corpus), "--schema", a.schema,
                    "--out", str(work), "--procs", "2"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["bash", str(HERE / "s03_second_count.sh"), str(corpus), str(work), "2"], check=True,
                   stdout=subprocess.DEVNULL)
    T = work / "tables"

    want_parse = Counter(pc for _, _, pc, *_ in F) + Counter({"ok": 2})           # +2 UG9 lines
    got_parse = Counter()
    for r in read_tsv(T / "s02_parse_census.tsv"):
        for c in L.PARSE_CLASSES:
            got_parse[c] += int(r[c])
    for c in L.PARSE_CLASSES:
        expect(f"s02_parse_census:{c}", want_parse[c], got_parse[c])

    want_chk = Counter()
    for fname, raw, pc, flags, *_ in F:
        want_chk.update(flags)
    want_chk.update(["V06", "V06"])                                                # the two UG9 lines
    got_chk = Counter()
    for r in read_tsv(T / "s02_validation_by_population.tsv"):
        got_chk[r["check_id"]] += int(r["n_flagged"])
    if a.seed_bad:
        want_chk["V16"] += 1
    for c in L.CHECKS:
        expect(f"s02_validation:{c}", want_chk[c], got_chk[c])

    dup = Counter()
    for r in read_tsv(T / "s02_byte_identical_records.tsv"):
        dup[r["scope"]] += int(r["n_lines_beyond_first"])
    # The unmodified base serialisation is on 7 lines in 5 files: Retron x2, GII x2, ncRNA x1,
    # MULTI x1, UG9 x1 (the unterminated one; the CRLF line differs by its trailing \r).
    # One hash -> across_files, 6 lines beyond the first; nothing duplicates within one file only.
    expect("s02_byte_identical:across_files_lines_beyond_first", 6, dup["across_files"])
    expect("s02_byte_identical:within_one_file_lines_beyond_first", 0, dup["within_one_file"])

    ident = {r["entry"]: r for r in read_tsv(T / "s01_file_identity.tsv")}
    expect("s01_detects_unterminated_final_line", "False", ident[UG9]["ends_with_newline"])
    expect("s01_detects_crlf", "1", ident[UG9]["n_crlf"])

    wc = {r["source_file"]: int(r["n_newlines_wc"]) for r in read_tsv(work / "second" / "s03_wc_lines.tsv")}
    nlines = {r["source_file"]: int(r["n_lines"]) for r in read_tsv(T / "s02_parse_census.tsv")}
    expect("s03_wc_vs_s02_lines_differ_by_exactly_the_unterminated_line",
           {f: (1 if f == UG9 else 0) for f in nlines}, {f: nlines[f] - wc[f] for f in nlines})

    want_grep = Counter()
    for fname, raw, pc, flags, at, dt in F:
        if pc == "blank" or pc == "not_object":
            continue
        a_tok = at if at is not None else "<0 anchor tokens>"
        d_tok = dt if dt is not None else "<0 database tokens>"
        want_grep[(fname, a_tok, d_tok)] += 1
    want_grep[(UG9, "RT", base["source_database"])] += 2
    got_grep = Counter()
    for r in read_tsv(work / "second" / "s03_grep_anchor_db.tsv"):
        got_grep[(r["source_file"], r["anchor_type_token"], r["source_database_token"])] += int(r["n_lines"])
    expect("s03_grep_joint_anchor_database_counts", sorted(want_grep.items()), sorted(got_grep.items()))

    # -- 4. the reconciler must REPORT the disagreements it is shown ----------------------
    # Two Retron lines carry both serialised keys yet are not JSON objects to s02 (bad UTF-8:
    # RT x gtdb_archaea; bad JSON: RT x <absent database>). Those, and only those, must DISAGREE.
    subprocess.run([py, str(HERE / "s05_reconcile.py"), "--work", str(work), "--schema", a.schema,
                    "--prior-g0", a.prior_g0], check=True, stdout=subprocess.DEVNULL)
    dis = sorted(f"{r['check']}|{r['scope']}|{r['delta_a_minus_b']}" for r in read_tsv(T / "s05_second_counts.tsv")
                 if r["agreement"] != "AGREE")
    expect("s05_reports_exactly_the_seeded_disagreements", [
        f"population_total|POP-RT-FAM|-2",
        f"records_per_file_all_anchor_database|{RETRON}|-2",
        f"records_per_file_anchor_database|{RETRON}|RT|<absent>|-1",
        f"records_per_file_anchor_database|{RETRON}|RT|gtdb_archaea|-1",
    ], dis)

    (Path(a.out) / "tables").mkdir(parents=True, exist_ok=True)
    L.write_tsv(Path(a.out) / "tables" / ("s04_positive_controls_SEEDBAD.tsv" if a.seed_bad else
                                          "s04_positive_controls.tsv"),
                ["control", "expected", "observed", "result"], rows)
    print(f"s04: {len(rows)} controls, {len(fails)} failed", flush=True)
    for f in fails:
        print(f"  FAIL {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
