#!/usr/bin/env python3
"""rt07_g1 step 1 - extract the evidence text, per page, by two independent routes.

Every PDF is rendered twice: `raw` (pdftotext reading order) and `layout` (-layout, which
preserves column geometry). These are two renderings of the same bytes, and step 2 counts
every token in both. A count that differs between them is retained and reported, never
averaged away - that is the independent second count this gate owes (WA-D.3).

The acquired primary alignment ALIGN_000044 is not a PDF and is not re-rendered: its flat
file is already text, so it is carried through verbatim and both routes are the same bytes.
Recording that honestly matters more than manufacturing a second route for it.

Inputs are verified by sha256 before a character is extracted - against
references/rt0_rt7/RESOURCE_REGISTER.tsv for the registered PDFs, and against the
acquisition register for the alignment. If a file and its register disagree, nothing runs.

Writes (under --work):  text/<source_id>.<route>.txt
                        text/pages/<source_id>.<route>.p<NN>.txt
                        text/extraction_manifest.tsv
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rt07g1lib import (ACQUIRED, PROJ, control, embl_prose, register, sha256,  # noqa: E402
                       write_tsv)

# source_id -> register asset_id. Tier-2 comparators are deliberately absent: they carry
# the RT0-RT7 convention this stage audits, and may not seed it (launcher 5d).
PDF_SOURCES = {
    "poch1989": "lit_poch1989",
    "xiong1990": "lit_xiong1990",
    "zimmerly2001": "lit_zimmerly2001",
    "simon2008": "lit_simon2008",
    "blocker2005": "lit_blocker2005_structural",
}
ALIGNMENT_FILE = "ALIGN_000044.dat"


def pdftotext(pdf: Path, dest: Path, layout: bool,
              first: int | None = None, last: int | None = None) -> None:
    cmd = ["pdftotext"] + (["-layout"] if layout else [])
    if first is not None:
        cmd += ["-f", str(first), "-l", str(last)]
    subprocess.run(cmd + [str(pdf), str(dest)], check=True, capture_output=True)


def page_count(pdf: Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    raise RuntimeError(f"no page count for {pdf}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    args = ap.parse_args()
    out = args.work / "text"
    pages = out / "pages"
    pages.mkdir(parents=True, exist_ok=True)

    reg = register()
    srcs = {r["source_id"]: r for r in control("sources.tsv")}
    rows, problems = [], []

    for sid, aid in PDF_SOURCES.items():
        r = reg.get(aid)
        if r is None:
            problems.append(f"{sid}: asset_id {aid} absent from RESOURCE_REGISTER.tsv")
            continue
        pdf = PROJ / r["project_path"]
        if not pdf.is_file():
            problems.append(f"{sid}: missing input {pdf}")
            continue
        observed = sha256(pdf)
        if observed != r["sha256"]:
            problems.append(f"{sid}: SHA MISMATCH vs register")
            continue
        n = page_count(pdf)
        for route, layout in (("raw", False), ("layout", True)):
            pdftotext(pdf, out / f"{sid}.{route}.txt", layout)
            for p in range(1, n + 1):
                pdftotext(pdf, pages / f"{sid}.{route}.p{p:02d}.txt", layout, p, p)
        rows.append({"source_id": sid, "asset_id": aid,
                     "evidence_tier": srcs[sid]["evidence_tier"],
                     "source_path": str(pdf), "sha256_verified": observed,
                     "bytes": r["bytes"], "pages": n,
                     "extraction_routes": "raw|layout",
                     "route_independence": "INDEPENDENT_RENDERINGS"})

    # ---- the acquired primary alignment: text already, carried verbatim ----
    aln = ACQUIRED / ALIGNMENT_FILE
    acq = {a["attempt_id"]: a for a in control("acquisition_attempts.tsv")}
    if not aln.is_file():
        problems.append(f"align000044: not in the governed acquisition cache ({aln}). "
                        f"Run s04_acquisition_register.py --acquire, or land "
                        f"MISSING_PRIMARY_ASSET.")
    else:
        # EMBL line-type codes are structure, not content: left in place they split every
        # wrapped sentence with a 'CC'. Stripped once here so both routes read the record
        # as the authors wrote it.
        text = embl_prose(aln.read_text(encoding="utf-8", errors="replace"))
        for route in ("raw", "layout"):
            (out / f"align000044.{route}.txt").write_text(text, encoding="utf-8")
            (pages / f"align000044.{route}.p01.txt").write_text(text, encoding="utf-8")
        rows.append({"source_id": "align000044",
                     "asset_id": "zimmerly2001_align_000044",
                     "evidence_tier": "TIER1_PRIMARY_ALIGNMENT",
                     "source_path": str(aln), "sha256_verified": sha256(aln),
                     "bytes": aln.stat().st_size, "pages": 1,
                     "extraction_routes": "embl_prose",
                     "route_independence": ("NOT_INDEPENDENT - a flat file needs no "
                                            "rendering; EMBL line-type codes stripped, both "
                                            "routes identical; "
                                            f"acquired {acq['AQ05']['retrieval_date_utc']}")})

    if problems:
        for p in problems:
            print(f"FAIL {p}", file=sys.stderr)
        return 1

    write_tsv(out / "extraction_manifest.tsv",
              ["source_id", "asset_id", "evidence_tier", "source_path", "sha256_verified",
               "bytes", "pages", "extraction_routes", "route_independence"], rows)
    print(f"extracted {len(rows)} sources "
          f"({sum(int(r['pages']) for r in rows)} pages), routes verified by sha256")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
