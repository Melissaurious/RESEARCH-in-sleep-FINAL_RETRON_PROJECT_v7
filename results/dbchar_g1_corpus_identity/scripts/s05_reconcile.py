#!/usr/bin/env python3
"""s05 - reconcile: (A) the census against its independent second count; (B) the census
against every prior corpus assumption this task inherited.

Prior values enter HERE ONLY, after s01-s03 have run; none of them is an input to any count.
They were read during the reuse audit before the census ran, so (B) is reconciliation, not
blind re-derivation - stated in the README, not hidden.

A disagreement is written as a finding (WA-D.3), never smoothed. Exit status is 0 either
way; run.sh's byte-for-byte comparison is what makes a changed result visible.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import g1lib as L  # noqa: E402

# --- prior values stated in PROSE (no table exists for them) - cited, never computed ---
STAGE_BRIEF = "idea-stage/programme/01_database_characterization.md"
STAGE_BRIEF_RECORDS_43_FILES = 3358182        # "0 mismatches over 3,358,182 source records across all 43 family files"
PRIOR_G0_README = "/home/borg/RESEARCH-retron-db/results/dbchar-g0-inventory/README.md"
PRIOR_G0_MULTI_RECORDS = 9012                 # "MULTI file: 9,012 records"
PRIOR_G0_MULTI_ONE_ELEMENT_LIST = 9009        # "9,009 of 9,012 MULTI records have a one-element system_types list"
PRIOR_G0_TWO_ELEMENT_LISTS_42 = 23            # "23 records corpus-wide have two" (42 files)
PRIOR_G0_MULTI_SUBTYPES_NONEMPTY = 0          # "system_subtypes is empty for all 9,012"
PRIOR_G0_UNPARSEABLE_42 = 0                   # "unparseable lines 0"
SCHEMA_NOTE_TAXONOMY_SYSTEMS = "gtdb|ncbi|unknown"   # schema note (stage 0a): observed value set


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def grep_label(tok: str, what: str) -> str:
    if tok == f"<0 {what} tokens>":
        return "<absent>"
    if tok == "null":
        return "<null>"
    if tok.startswith("<") and tok.endswith(f" {what} tokens>"):
        return tok  # a line carrying the key more than once: never equal to a JSON label
    return tok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    ap.add_argument("--schema", required=True)
    ap.add_argument("--prior-g0", required=True, help="prior dbchar-g0-inventory bundle root")
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"

    ident = {r["entry"]: r for r in rd(T / "s01_file_identity.tsv") if r["kind"] == "file" and r["jsonl"] == "True"}
    parse = {r["source_file"]: r for r in rd(T / "s02_parse_census.tsv")}
    wc = {r["source_file"]: int(r["n_newlines_wc"]) for r in rd(W / "second" / "s03_wc_lines.tsv")}
    grep = Counter()
    for r in rd(W / "second" / "s03_grep_anchor_db.tsv"):
        grep[(r["source_file"], grep_label(r["anchor_type_token"], "anchor"),
              grep_label(r["source_database_token"], "database"))] += int(r["n_lines"])
    s02j = Counter()
    for r in rd(T / "s02_source_database_by_file.tsv"):
        s02j[(r["source_file"], r["anchor_type"], r["source_database"])] += int(r["n_records"])

    # ---------------- (A) second counts ------------------------------------------------
    A: list[list] = []

    def cmp(check, scope, ra, va, rb, vb):
        A.append([check, scope, ra, va, rb, vb, (va - vb) if isinstance(va, int) and isinstance(vb, int) else "",
                  "AGREE" if va == vb else "DISAGREE"])

    files = sorted(set(ident) | set(parse) | set(wc))
    for f in files:
        cmp("newlines_per_file", f, "s01 python byte count", int(ident[f]["n_newlines"]) if f in ident else "",
            "s03 coreutils wc -l", wc.get(f, ""))
    for f in files:
        tail = 0 if ident.get(f, {}).get("ends_with_newline") == "True" else 1
        cmp("lines_per_file", f, "s02 split lines", int(parse[f]["n_lines"]) if f in parse else "",
            "s03 wc -l + unterminated final line", wc.get(f, 0) + tail)
    for k in sorted(set(grep) | set(s02j)):
        cmp("records_per_file_anchor_database", "|".join(k), "s02 json census", s02j.get(k, 0),
            "s03 grep -o token pairs", grep.get(k, 0))
    for f in files:
        cmp("records_per_file_all_anchor_database", f, "s02 parsed objects", int(parse[f]["ok"]) if f in parse else 0,
            "s03 lines with any token pair", sum(v for (ff, _, _), v in grep.items() if ff == f))
    pops = {"POP-RT-FAM": lambda f, an: an == "RT" and L.file_role(f)[0] == "family",
            "POP-RT-MULTI": lambda f, an: an == "RT" and L.file_role(f)[0] == "multi",
            "POP-NCRNA": lambda f, an: an == "ncRNA"}
    s02pop = {r["population"]: int(r["n_lines"]) for r in rd(T / "s02_populations.tsv")}
    for p, pred in pops.items():
        cmp("population_total", p, "s02 json census", s02pop.get(p, 0), "s03 grep, same definition",
            sum(v for (f, an, _), v in grep.items() if pred(f, an)))
    cmp("all_lines_total", "corpus", "s02 split lines", s02pop["ALL"], "s03 wc -l + unterminated",
        sum(wc.values()) + sum(1 for f in files if ident.get(f, {}).get("ends_with_newline") != "True"))
    L.write_tsv(T / "s05_second_counts.tsv",
                ["check", "scope", "route_a", "value_a", "route_b", "value_b", "delta_a_minus_b", "agreement"], A)

    # ---------------- (B) prior assumptions ----------------------------------------------
    B: list[list] = []

    def rec(source, quantity, scope, prior, measured, note=""):
        if isinstance(prior, int) and isinstance(measured, int):
            status, delta = ("AGREE" if prior == measured else "DIFFER"), measured - prior
        else:
            status, delta = ("AGREE" if str(prior) == str(measured) else "DIFFER"), ""
        B.append([source, quantity, scope, prior, measured, delta, status, note])

    g0 = Path(a.prior_g0) / "tables"
    prior_files = {r["source_file"]: r for r in rd(g0 / "s01_file_census.tsv")}
    for f in sorted(set(prior_files) | set(ident)):
        pf = prior_files.get(f)
        if pf is None:
            rec("prior g0 s01_file_census.tsv", "file_in_scope", f, "absent (not opened by prior g0)",
                "present", "prior g0 excluded this file by launcher scope")
            continue
        if f not in ident or f not in parse:
            rec("prior g0 s01_file_census.tsv", "file_in_scope", f, "present", "absent from measured corpus")
            continue
        rec("prior g0 s01_file_census.tsv", "sha256", f, pf["sha256"], ident[f]["sha256"])
        rec("prior g0 s01_file_census.tsv", "bytes", f, int(pf["bytes"]), int(ident[f]["bytes"]))
        rec("prior g0 s01_file_census.tsv", "n_records", f, int(pf["n_records"]), int(parse[f]["ok"]),
            "prior = json-parsed non-blank lines; measured = parse class ok")
        rec("prior g0 s01_file_census.tsv", "n_unparseable_lines", f, int(pf["n_unparseable_lines"]),
            int(parse[f]["n_lines"]) - int(parse[f]["ok"]),
            "prior skipped blank lines silently and decoded with errors=replace")
    in42 = [f for f in parse if f != L.NCRNA_FILE]
    rec("prior g0 s01_corpus_totals.tsv", "P-REC records", "42 files (all but ncRNA-anchored)",
        int({r["quantity"]: r["value"] for r in rd(g0 / "s01_corpus_totals.tsv")}["P-REC_records_42_files"]),
        sum(int(parse[f]["ok"]) for f in in42))
    rec(PRIOR_G0_README, "unparseable lines", "42 files", PRIOR_G0_UNPARSEABLE_42,
        sum(int(parse[f]["n_lines"]) - int(parse[f]["ok"]) for f in in42))
    dbm = Counter()
    for (f, an, db), v in s02j.items():
        if f != L.NCRNA_FILE:
            dbm[db] += v
    for r in rd(g0 / "s01_db_census.tsv"):
        rec("prior g0 s01_db_census.tsv", "n_records", f"source_database={r['source_database']}, 42 files",
            int(r["n_records"]), dbm.get(r["source_database"], 0))
    for db in sorted(set(dbm) - {r["source_database"] for r in rd(g0 / "s01_db_census.tsv")}):
        rec("prior g0 s01_db_census.tsv", "n_records", f"source_database={db}, 42 files", 0, dbm[db],
            "value absent from prior table")

    listing = {}
    for line in Path(a.schema).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(master_\S+\.jsonl)\s+\S+\s+(\d+)\s*$", line)
        if m:
            listing[m.group(1)] = int(m.group(2))
    for f in sorted(set(listing) | set(wc)):
        rec("schema document wc -l listing", "n_newlines", f, listing.get(f, "absent from listing"),
            wc.get(f, "absent from corpus"))
    rec(STAGE_BRIEF, "source records", "all 43 files", STAGE_BRIEF_RECORDS_43_FILES, s02pop["ALL"],
        "prose value in the stage brief; measured = all lines")

    types = rd(T / "s02_system_types_by_file.tsv")
    two_el_42 = sum(int(r["n_records"]) for r in types
                    if r["source_file"] != L.NCRNA_FILE and isinstance(json.loads(r["system_types_raw"]), list)
                    and len(json.loads(r["system_types_raw"])) == 2)
    multi_one = sum(int(r["n_records"]) for r in types if r["source_file"] == L.MULTI_FILE
                    and isinstance(json.loads(r["system_types_raw"]), list) and len(json.loads(r["system_types_raw"])) == 1)
    rec(PRIOR_G0_README, "MULTI file records", L.MULTI_FILE, PRIOR_G0_MULTI_RECORDS, int(parse[L.MULTI_FILE]["ok"]))
    rec(PRIOR_G0_README, "MULTI records with a one-element system_types list", L.MULTI_FILE,
        PRIOR_G0_MULTI_ONE_ELEMENT_LIST, multi_one)
    rec(PRIOR_G0_README, "records with a two-element system_types list", "42 files", PRIOR_G0_TWO_ELEMENT_LISTS_42, two_el_42)
    sub = {r["population"] + ":" + r["state"]: int(r["n_records"]) for r in rd(T / "s02_system_subtypes_state.tsv")}
    rec(PRIOR_G0_README, "MULTI records with non-empty system_subtypes", "POP-RT-MULTI",
        PRIOR_G0_MULTI_SUBTYPES_NONEMPTY, sub.get("POP-RT-MULTI:nonempty_list", 0))
    tsys = sorted({r["taxonomy_system"] for r in rd(T / "s02_taxonomy_system.tsv") if r["population"] != "POP-NCRNA"})
    rec("schema note (stage 0a)", "observed taxonomy_system value set", "RT-anchored + other, 42 files",
        SCHEMA_NOTE_TAXONOMY_SYSTEMS, "|".join(tsys))
    tsys_all = sorted({r["taxonomy_system"] for r in rd(T / "s02_taxonomy_system.tsv")})
    rec("schema field list", "documented taxonomy_system values", "all 43 files",
        "|".join(L.DOC_TAXONOMY_SYSTEMS), "|".join(tsys_all), "documented set vs observed set")
    rec("data/README.md + CLAUDE.md scope rule", "ncRNA-anchor-only records confined to their master file",
        "all 43 files", 0, sum(v for (f, an, db), v in s02j.items() if an == "ncRNA" and f != L.NCRNA_FILE),
        "measured = ncRNA-anchored records found in any other file")
    rec("data/README.md + CLAUDE.md scope rule", "RT-anchored records inside the ncRNA-anchored master file",
        L.NCRNA_FILE, 0, sum(v for (f, an, db), v in s02j.items() if an != "ncRNA" and f == L.NCRNA_FILE))
    L.write_tsv(T / "s05_prior_reconciliation.tsv",
                ["source", "quantity", "scope", "prior_value", "measured_value", "delta_measured_minus_prior",
                 "status", "note"], B)

    nA = sum(1 for r in A if r[-1] != "AGREE")
    nB = sum(1 for r in B if r[6] != "AGREE")
    print(f"s05: second counts {len(A)} rows, {nA} DISAGREE; prior reconciliation {len(B)} rows, {nB} DIFFER")
    for r in A:
        if r[-1] != "AGREE":
            print("  A", r)
    for r in B:
        if r[6] != "AGREE":
            print("  B", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
