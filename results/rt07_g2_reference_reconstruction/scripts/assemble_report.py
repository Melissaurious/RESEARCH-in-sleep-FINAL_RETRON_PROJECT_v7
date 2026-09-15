#!/usr/bin/env python3
"""rt07_g2 step 7 - assemble REPORT.md and a self-contained REPORT.html.

The assembler computes NOTHING. Every rendered number resolves to a
(bundle, table, row selector, column, format) five-tuple declared in findings.py, and the
resolution trace is landed as g2_resolved_values.tsv so any number in the report can be
walked back to the row it came from. An unresolved placeholder, or a selector matching
anything other than exactly one row, fails the build (launcher 9d).

Writes: REPORT.md, REPORT.html, tables/g2_resolved_values.tsv
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings as F  # noqa: E402
from rt07g2lib import read_tsv, write_tsv  # noqa: E402


def fmt(raw: str, kind: str) -> str:
    if kind == "int":
        return f"{int(raw):,d}"
    if kind == "pct":
        return f"{float(raw):.2f}%"
    return str(raw)


def resolve(tables: Path, trace: list) -> dict[str, str]:
    out = {}
    for key, (table, sel, col, kind) in F.VALUES.items():
        p = tables / table
        if not p.exists():
            raise SystemExit(f"FATAL: {key}: no such table {p}")
        match = [r for r in read_tsv(p) if all(r.get(k, "") == v for k, v in sel.items())]
        if len(match) != 1:
            raise SystemExit(f"FATAL: {key}: selector {sel} matched {len(match)} rows "
                             f"in {table}")
        if col not in match[0]:
            raise SystemExit(f"FATAL: {key}: no column {col} in {table}")
        out[key] = fmt(match[0][col], kind)
        trace.append({"key": key, "bundle": "rt07_g2_history_and_definition",
                      "table": table,
                      "selector": ";".join(f"{k}={v}" for k, v in sel.items()),
                      "column": col, "raw_value": match[0][col], "rendered": out[key],
                      "unit": "resolved report value",
                      "denominator": f"{len(F.VALUES)} declared lookups"})
    return out


def fill(text: str, vals: dict[str, str], where: str, bold: bool) -> str:
    def sub(m):
        k = m.group(1)
        if k not in vals:
            raise SystemExit(f"FATAL: {where}: placeholder {{{k}}} has no declared lookup")
        return f"**{vals[k]}**" if bold else f"<b>{vals[k]}</b>"
    return re.sub(r"\{([a-z0-9_]+)\}", sub, re.sub(r"\s+", " ", text).strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    tables = args.bundle / "tables"

    trace: list[dict] = []
    vals = resolve(tables, trace)
    write_tsv(tables / "g2_resolved_values.tsv",
              ["key", "bundle", "table", "selector", "column", "raw_value", "rendered",
               "unit", "denominator"], trace)

    md = [f"# {F.TITLE}", "", f"_{F.SUBTITLE}_", "",
          "Every number below resolves to a landed table via `tables/g2_resolved_values.tsv`. "
          "This document computes nothing.", ""]
    body = []
    for s in F.SECTIONS:
        md += [f"## {s['num']} · {s['title']}", "",
               fill(s["body"], vals, s["title"], True), "",
               "> " + fill(s["caveat"], vals, s["title"], True), "",
               "Tables: " + ", ".join(f"`tables/{t}`" for t in s["tables"]), ""]
        body.append(
            f"<section><h2>{s['num']} &middot; {html.escape(s['title'])}</h2>"
            f"<p>{fill(html.escape(s['body']), vals, s['title'], False)}</p>"
            f"<blockquote>{fill(html.escape(s['caveat']), vals, s['title'], False)}"
            f"</blockquote><p class='t'>Tables: "
            + ", ".join(f"<code>tables/{html.escape(t)}</code>" for t in s["tables"])
            + "</p></section>")
    (args.out / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

    css = ("body{font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;max-width:52em;"
           "margin:2em auto;padding:0 1.2em;color:#1a1a1a;background:#fff}"
           "h1{font-size:1.6em;margin-bottom:0}h2{font-size:1.1em;margin-top:2em;"
           "border-bottom:1px solid #e3e3e3;padding-bottom:.3em}"
           "blockquote{margin:1em 0;padding:.6em 1em;background:#f6f7f9;"
           "border-left:3px solid #b9c0c8;color:#333}"
           ".sub{color:#555;font-style:italic}.t{color:#666;font-size:.86em}"
           "code{background:#f2f3f5;padding:.1em .35em;border-radius:3px;font-size:.9em}"
           "b{background:#fff3c4;padding:0 .2em;border-radius:2px}")
    (args.out / "REPORT.html").write_text(
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{html.escape(F.TITLE)}</title><style>{css}</style></head><body>"
        f"<h1>{html.escape(F.TITLE)}</h1><p class='sub'>{html.escape(F.SUBTITLE)}</p>"
        "<p class='t'>Every highlighted number resolves to a landed table via "
        "<code>tables/g2_resolved_values.tsv</code>. This page computes nothing.</p>"
        + "".join(body) + "</body></html>", encoding="utf-8")

    print(f"report assembled: {len(vals)} values resolved, {len(F.SECTIONS)} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
