#!/usr/bin/env python3
"""assemble_report - build REPORT.md and the self-contained REPORT.html.

THIS SCRIPT COMPUTES NOTHING. Every value is resolved from one of this bundle's landed tables by
an exact row selector; a selector matching anything other than one row fails the build, as does a
{placeholder} with no declared lookup, or a stray {...} surviving into the finished HTML.

Adapted from `results/dbchar_g7_stage1_report/scripts/assemble_report.py` (same resolver
contract, same house style); the section model and the figure/table expansion differ.
"""
from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings as F  # noqa: E402

CSS = """
:root { --ink:#1b2733; --muted:#5b6b7a; --line:#dde5ec; --accent:#2f6f9f; --warn:#8a5a12;
        --warnbg:#fdf6e7; --bg:#ffffff; --propbg:#f2f7fb; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
       font:15px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
.wrap { max-width: 1040px; margin: 0 auto; padding: 32px 20px 90px; }
header { border-bottom:3px solid var(--accent); padding-bottom:18px; margin-bottom:6px; }
h1 { font-size:27px; margin:0 0 8px; letter-spacing:-.01em; line-height:1.25; }
.sub { color:var(--muted); font-size:14px; max-width:78ch; }
.meta { color:var(--muted); font-size:12px; margin-top:12px; }
nav { margin:18px 0 6px; font-size:13px; color:var(--muted); }
nav a { color:var(--accent); text-decoration:none; margin-right:14px; white-space:nowrap; }
section { border-top:1px solid var(--line); padding:26px 0 8px; }
h2 { font-size:20px; margin:0 0 4px; }
.snum { color:var(--accent); font-weight:700; margin-right:8px; }
.view { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.055em;
        margin-bottom:14px; }
h3 { font-size:14px; margin:18px 0 4px; color:var(--accent); letter-spacing:.01em; }
p { margin:4px 0 10px; max-width:82ch; }
.caveat { background:var(--warnbg); border-left:3px solid var(--warn); color:#4a3a1a;
          padding:10px 14px; margin:16px 0 4px; font-size:13.5px; border-radius:0 4px 4px 0;
          max-width:82ch; }
.prop { background:var(--propbg); border-left:3px solid var(--accent); padding:10px 14px;
        margin:10px 0; border-radius:0 4px 4px 0; max-width:82ch; }
figure { margin:20px 0 6px; }
figure img { width:100%; border:1px solid var(--line); border-radius:4px; background:#fff; }
figcaption { color:var(--muted); font-size:11.5px; margin-top:6px; }
table { border-collapse:collapse; width:100%; font-size:12px; margin:8px 0 4px; }
th,td { border-bottom:1px solid var(--line); padding:4px 8px; text-align:left; }
th { background:#f6f9fb; font-weight:600; }
details { margin:8px 0; }
summary { cursor:pointer; color:var(--accent); font-size:12.5px; }
.tmeta { color:var(--muted); font-size:11px; margin:3px 0 8px; }
code { background:#f2f6f9; padding:1px 4px; border-radius:3px; font-size:12px;
       word-break:break-all; }
b { font-weight:640; }
@media (prefers-color-scheme: dark) {
  :root { --ink:#e6edf3; --muted:#9bb0c2; --line:#26323d; --bg:#11171d; --warnbg:#2a2417;
          --propbg:#152029; }
  th { background:#1a222a; } code { background:#1a222a; }
}
"""


def rows(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def fmt(v: str, kind: str) -> str:
    if kind == "int":
        return f"{int(float(v)):,d}"
    if kind == "pct":
        f = float(v)
        return f"{f:.2f}%" if abs(f) < 10 else f"{f:.1f}%"
    if kind == "num":
        f = float(v)
        return f"{f:,.0f}" if f == int(f) else f"{f:,.2f}"
    return str(v)


def resolve(tables: Path, trace: list) -> dict[str, str]:
    out = {}
    for key, (table, sel, col, kind) in F.VALUES.items():
        p = tables / f"{table}.tsv"
        if not p.exists():
            raise SystemExit(f"FATAL: {key}: no such table {p}")
        rs = rows(p)
        match = [r for r in rs if all(str(r.get(k, "")) == str(v) for k, v in sel.items())]
        if len(match) != 1:
            raise SystemExit(f"FATAL: {key}: selector {sel} matched {len(match)} rows in {table}")
        if col not in match[0]:
            raise SystemExit(f"FATAL: {key}: no column {col} in {table}")
        out[key] = fmt(match[0][col], kind)
        trace.append(dict(key=key, table=f"tables/{table}.tsv",
                          selector=";".join(f"{k}={v}" for k, v in sel.items()), column=col,
                          raw_value=match[0][col], rendered=out[key]))
    return out


def fill(text: str, vals: dict[str, str], where: str, bold: bool = True) -> str:
    def sub(m):
        k = m.group(1)
        if k not in vals:
            raise SystemExit(f"FATAL: {where}: placeholder {{{k}}} has no declared lookup")
        return f"<b>{vals[k]}</b>" if bold else vals[k]
    return re.sub(r"\{([a-z0-9_]+)\}", sub, text)


def md_inline(s: str) -> str:
    """The prose uses **bold** and *italic*; everything else is escaped."""
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    return s


def table_html(tables: Path, name: str, meta: dict, limit: int = 10) -> str:
    p = tables / f"{name}.tsv"
    if not p.exists():
        raise SystemExit(f"FATAL: section references a table that did not land: {name}")
    rs = rows(p)
    if not rs:
        return ""
    cols = [c for c in rs[0] if c not in ("unit", "denominator")][:9]
    head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    body = ""
    for r in rs[:limit]:
        body += "<tr>" + "".join(f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in cols) + "</tr>"
    m = meta.get(f"tables/{name}.tsv", {})
    more = f" &middot; showing {min(limit, len(rs))} of {len(rs)} rows" if len(rs) > limit else ""
    info = (f"unit: {html.escape(m.get('unit', '?'))} &middot; denominator: "
            f"{html.escape(m.get('denominator', '?'))} &middot; "
            f"{html.escape(m.get('estimate', ''))} &middot; produced by "
            f"<code>{html.escape(m.get('script', '?'))}</code>{more}")
    return (f"<details><summary>{html.escape(name)}.tsv</summary>"
            f"<div class='tmeta'>{info}</div><table><tr>{head}</tr>{body}</table></details>")


def figure_html(figs: Path, tables: Path, name: str, meta: dict) -> str:
    png = figs / f"{name}.png"
    if not png.exists():
        raise SystemExit(f"FATAL: figure {png} missing")
    if not (tables / f"{name}.tsv").exists():
        raise SystemExit(f"FATAL: figure {name} has no table beside it (BS-13)")
    b64 = base64.b64encode(png.read_bytes()).decode()
    m = meta.get(f"figures/{name}.png", {})
    return (f"<figure><img alt='{html.escape(name)}' src='data:image/png;base64,{b64}'>"
            f"<figcaption><b>{html.escape(name)}</b> &middot; drawn by "
            f"<code>{html.escape(m.get('script', '?'))}</code> from "
            f"<code>tables/{html.escape(name)}.tsv</code> &middot; unit: "
            f"{html.escape(m.get('unit', '?'))} &middot; denominator: "
            f"{html.escape(m.get('denominator', '?'))}</figcaption></figure>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True, help="directory holding tables/ figures/ meta/")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    work, out = Path(a.work), Path(a.out)
    tables, figs, metad = work / "tables", work / "figures", work / "meta"
    out.mkdir(parents=True, exist_ok=True)

    meta = {}
    for mp in sorted(metad.glob("*.json")):
        d = json.loads(mp.read_text())
        meta[d["artifact"]] = d

    trace: list[dict] = []
    vals = resolve(tables, trace)

    # ---------------- HTML
    h = [f"<!-- generated by assemble_report.py; computes nothing -->",
         f"<style>{CSS}</style>", "<div class='wrap'>", "<header>",
         f"<h1>{html.escape(F.TITLE)}</h1>",
         f"<div class='sub'>{md_inline(F.SUBTITLE)}</div>",
         "<div class='meta'>bundle <code>results/dbchar_g7b_stage1_extended_report</code> &middot; "
         "reporting layer over the landed Stage-1 gates g1&ndash;g7 &middot; no claim status is "
         "proposed &middot; human_input_audit: PENDING</div>", "</header>", "<nav>"]
    for s in F.SECTIONS:
        h.append(f"<a href='#s{s['id']}'>{s['id']}. {html.escape(s['title'])}</a>")
    h.append("</nav>")

    md = [f"# {F.TITLE}", "", F.SUBTITLE, "",
          "> Bundle: `results/dbchar_g7b_stage1_extended_report` — a reporting layer over the "
          "landed Stage-1 gates g1–g7. No claim status is proposed; `human_input_audit` is "
          "PENDING.", ""]

    for s in F.SECTIONS:
        where = f"section {s['id']}"
        h.append(f"<section id='s{s['id']}'><h2><span class='snum'>{s['id']}</span>"
                 f"{html.escape(s['title'])}</h2>")
        h.append(f"<div class='view'>{fill(html.escape(s['view']), vals, where, bold=False)}</div>")
        md += [f"## {s['id']} · {s['title']}", "",
               f"*{fill(s['view'], vals, where, bold=False)}*", ""]
        for head, body in s["prose"]:
            filled = fill(md_inline(body), vals, where)
            cls = " class='prop'" if head.startswith("PROPOSED") else ""
            h.append(f"<h3>{html.escape(head)}</h3><p{cls}>{filled}</p>")
            md += [f"**{head}.** " + fill(body, vals, where, bold=False), ""]
        for fg in s.get("figures", []):
            h.append(figure_html(figs, tables, fg, meta))
            md += [f"![{fg}](figures/{fg}.png)", ""]
        for t in s.get("tables", []):
            h.append(table_html(tables, t, meta))
        md += ["Landed tables: " + ", ".join(f"`tables/{t}.tsv`" for t in s.get("tables", [])), ""]
        if s.get("caveat"):
            h.append(f"<div class='caveat'><b>Caveat.</b> "
                     f"{fill(md_inline(s['caveat']), vals, where)}</div>")
            md += ["> **Caveat.** " + fill(s["caveat"], vals, where, bold=False), ""]
        h.append("</section>")

    h.append(f"<section><h2><span class='snum'>·</span>What this bundle is not</h2>"
             f"<p>{md_inline(F.CLOSING.strip()).replace(chr(10) + chr(10), '</p><p>')}</p>"
             f"</section>")
    md += ["## · What this bundle is not", "", F.CLOSING.strip(), ""]
    h.append("</div>")

    html_doc = "\n".join(h)
    leftover = re.findall(r"\{[a-z0-9_]+\}", html_doc)
    if leftover:
        raise SystemExit(f"FATAL: unresolved placeholders survived into the HTML: {leftover[:5]}")
    (out / "REPORT.html").write_text(html_doc, encoding="utf-8")
    (out / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

    with (tables / "g7b_resolved_values.tsv").open("w", encoding="utf-8") as fh:
        cols = ["key", "table", "selector", "column", "raw_value", "rendered"]
        fh.write("\t".join(cols) + "\tunit\tdenominator\n")
        for r in sorted(trace, key=lambda x: x["key"]):
            fh.write("\t".join(str(r[c]) for c in cols)
                     + "\tresolved values\tn/a - one table lookup per row; no rate\n")
    (metad / "tables__g7b_resolved_values.json").write_text(json.dumps(dict(
        artifact="tables/g7b_resolved_values.tsv", script="scripts/assemble_report.py",
        unit="resolved values", denominator="n/a - one table lookup per row; no rate",
        estimate="n/a - provenance trace"), sort_keys=True))

    n_fig = sum(len(s.get("figures", [])) for s in F.SECTIONS)
    print(f"REPORT.html: {len(html_doc):,d} bytes, {len(F.SECTIONS)} sections, {n_fig} figures, "
          f"{len(vals)} resolved values", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
