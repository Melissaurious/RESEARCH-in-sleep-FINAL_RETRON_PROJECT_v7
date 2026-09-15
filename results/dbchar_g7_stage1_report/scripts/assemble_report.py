#!/usr/bin/env python3
"""assemble_report - build the self-contained Stage-1 REPORT.html (and REPORT.md).

This script COMPUTES NOTHING. Every value is resolved from a landed table of a landed bundle by
an exact row selector; a selector that matches zero or several rows fails the build, and so does
any placeholder with no declared lookup. Figures are embedded as base64 from the bundles that
produced them, so the HTML is self-contained.
"""
from __future__ import annotations

import argparse
import base64
import csv
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import findings as F  # noqa: E402

CSS = """
:root { --ink:#1b2733; --muted:#5b6b7a; --line:#dde5ec; --accent:#2f6f9f; --warn:#8a5a12;
        --warnbg:#fdf6e7; --bg:#ffffff; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
       font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
.wrap { max-width: 980px; margin: 0 auto; padding: 32px 20px 80px; }
header { border-bottom:3px solid var(--accent); padding-bottom:18px; margin-bottom:8px; }
h1 { font-size:26px; margin:0 0 6px; letter-spacing:-.01em; }
.sub { color:var(--muted); font-size:13.5px; }
.meta { color:var(--muted); font-size:12px; margin-top:10px; }
section { border-top:1px solid var(--line); padding:26px 0 6px; }
h2 { font-size:19px; margin:0 0 4px; }
.snum { color:var(--accent); font-weight:700; margin-right:8px; }
.view { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em;
        margin-bottom:12px; }
.finding { font-size:15.5px; }
.caveat { background:var(--warnbg); border-left:3px solid var(--warn); color:#4a3a1a;
          padding:10px 14px; margin:14px 0; font-size:14px; border-radius:0 4px 4px 0; }
figure { margin:18px 0; }
figure img { width:100%; border:1px solid var(--line); border-radius:4px; }
figcaption { color:var(--muted); font-size:12px; margin-top:6px; }
table { border-collapse:collapse; width:100%; font-size:12.5px; margin:8px 0 4px; }
th,td { border-bottom:1px solid var(--line); padding:5px 8px; text-align:left; }
th { background:#f6f9fb; font-weight:600; }
details { margin:10px 0; }
summary { cursor:pointer; color:var(--accent); font-size:13px; }
.tmeta { color:var(--muted); font-size:11.5px; margin:2px 0 10px; }
code { background:#f2f6f9; padding:1px 4px; border-radius:3px; font-size:12.5px;
       word-break:break-all; }
.kicker { font-weight:600; color:var(--accent); font-size:12px; letter-spacing:.08em;
          text-transform:uppercase; }
@media (prefers-color-scheme: dark) {
  :root { --ink:#e6edf3; --muted:#9bb0c2; --line:#26323d; --bg:#11171d; --warnbg:#2a2417; }
  th { background:#1a222a; } code { background:#1a222a; } figure img { background:#fff; }
}
"""


def write_tsv(p: Path, cols: list[str], rs: list[dict]) -> None:
    with p.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rs:
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")


def rows(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def fmt(v: str, kind: str) -> str:
    if kind == "int":
        return f"{int(float(v)):,d}"
    if kind == "pct":
        return f"{float(v):.2f}%"
    if kind == "num":
        f = float(v)
        return f"{f:,.0f}" if f == int(f) else f"{f:,.1f}"
    return str(v)


def derived_count(results: Path, derived: Path | None) -> int:
    """Count the derived datasets the landed bundles registered, and check the registries agree
    with what is on disk. This is a consistency check on landed provenance, not a measurement:
    the closing sentence's count comes from here rather than from a number typed into prose."""
    reg: dict[str, str] = {}
    for rp in sorted(results.glob("dbchar_g*/tables/*_derived_registry.tsv")):
        for r in rows(rp):
            name = r.get("dataset") or r.get("artifact") or r.get("file") or next(iter(r.values()))
            if name in reg:
                raise SystemExit(f"FATAL: {name} registered twice ({reg[name]}, {rp})")
            reg[name] = str(rp)
    # The on-disk check runs only when data/derived is present. It is gitignored, so a clone-safe
    # rerun has no such directory - and a check that silently turned into a hard dependency on
    # regenerated 40 GB of parquet would make this bundle unverifiable in a fresh clone.
    if derived is not None and derived.is_dir():
        on_disk = {f.name for f in derived.iterdir() if f.is_file()}
        if on_disk != set(reg):
            raise SystemExit("FATAL: data/derived and the bundle registries disagree: "
                             f"unregistered={sorted(on_disk - set(reg))} "
                             f"missing_from_disk={sorted(set(reg) - on_disk)}")
    else:
        print("  note: data/derived absent - registries checked against each other only")
    if len(reg) != F.N_DERIVED:
        raise SystemExit(f"FATAL: findings.N_DERIVED={F.N_DERIVED} but {len(reg)} are registered")
    return len(reg)


def resolve(results: Path, trace: list | None = None) -> dict[str, str]:
    out = {}
    for key, (bundle, table, sel, col, kind) in F.VALUES.items():
        p = results / bundle / "tables" / table
        if not p.exists():
            raise SystemExit(f"FATAL: {key}: no such table {p}")
        match = [r for r in rows(p) if all(r.get(k, "") == v for k, v in sel.items())]
        if len(match) != 1:
            raise SystemExit(f"FATAL: {key}: selector {sel} matched {len(match)} rows in {table}")
        if col not in match[0]:
            raise SystemExit(f"FATAL: {key}: no column {col} in {table}")
        out[key] = fmt(match[0][col], kind)
        if trace is not None:
            trace.append(dict(key=key, bundle=bundle, table=f"tables/{table}",
                              selector=";".join(f"{k}={v}" for k, v in sel.items()),
                              column=col, raw_value=match[0][col], rendered=out[key]))
    return out


def fill(text: str, vals: dict[str, str], where: str) -> str:
    def sub(m):
        k = m.group(1)
        if k not in vals:
            raise SystemExit(f"FATAL: {where}: placeholder {{{k}}} has no declared lookup")
        return f"<b>{vals[k]}</b>"
    return re.sub(r"\{([a-z0-9_]+)\}", sub, text)


def table_html(results: Path, bundle: str, name: str, manifest: dict, limit: int = 12) -> str:
    p = results / bundle / "tables" / name
    rs = rows(p)
    if not rs:
        return ""
    cols = [c for c in rs[0] if c not in ("unit", "denominator", "note", "caveat")][:9]
    head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    body = ""
    for r in rs[:limit]:
        body += "<tr>" + "".join(f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in cols) + "</tr>"
    key = f"tables/{name}"
    m = manifest.get((bundle, key), {})
    meta = (f"unit: {html.escape(m.get('unit', '?'))} &middot; denominator: "
            f"{html.escape(m.get('denominator', '?'))} &middot; produced by "
            f"<code>{html.escape(m.get('script', '?'))}</code> in <code>{bundle}</code>")
    more = f" &middot; showing {min(limit, len(rs))} of {len(rs)} rows" if len(rs) > limit else ""
    return (f"<details><summary>{html.escape(name)}</summary>"
            f"<div class='tmeta'>{meta}{more}</div>"
            f"<table><tr>{head}</tr>{body}</table></details>")


def figure_html(results: Path, bundle: str, name: str, selfdir: Path) -> str:
    """Figures come from the bundle that produced them. `SELF` is this gate's own restyle of a
    landed table - a new figure over unchanged numbers, which REPORTING_STANDARDS puts in a new
    gate rather than in an edit to the landed bundle (BS-6)."""
    png = (selfdir / f"{name}.png") if bundle == F.SELF else (results / bundle / "figures" / f"{name}.png")
    if not png.exists():
        raise SystemExit(f"FATAL: figure {png} missing")
    b64 = base64.b64encode(png.read_bytes()).decode()
    return (f"<figure><img alt='{html.escape(name)}' src='data:image/png;base64,{b64}'>"
            f"<figcaption>{html.escape(name)} &middot; produced by the figure script in "
            f"<code>{bundle}</code>; the plotted numbers are in "
            f"<code>tables/{html.escape(name)}.tsv</code></figcaption></figure>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--derived", default=None,
                    help="data/derived, checked against the bundle registries when present")
    ap.add_argument("--self-figures", default=None,
                    help="where this gate's own re-plotted figures live "
                         "(default: <results>/dbchar_g7_stage1_report/figures)")
    a = ap.parse_args()
    results, out = Path(a.results).resolve(), Path(a.out)
    selfdir = Path(a.self_figures) if a.self_figures else results / F.SELF / "figures"
    out.mkdir(parents=True, exist_ok=True)
    trace: list[dict] = []
    vals = resolve(results, trace)
    vals["n_derived"] = f"{derived_count(results, Path(a.derived) if a.derived else None):,d}"
    trace.append(dict(key="n_derived", bundle="(all gates)",
                      table="tables/*_derived_registry.tsv", selector="row count across registries",
                      column="dataset", raw_value=vals["n_derived"], rendered=vals["n_derived"]))

    manifest = {}
    for b in {s["bundle"] for s in F.SECTIONS} | {v[0] for v in F.VALUES.values()}:
        mp = results / b / "MANIFEST.tsv"
        if mp.exists():
            for r in rows(mp):
                manifest[(b, r["artifact"])] = r

    body, md = [], ["# Stage 1 — RT/retron corpus characterisation\n"]
    for s in F.SECTIONS:
        finding = fill(" ".join(s["finding"].split()), vals, f"section {s['num']} finding")
        caveat = fill(" ".join(s["caveat"].split()), vals, f"section {s['num']} caveat")
        figs = "".join(figure_html(results, b, n, selfdir) for b, n in s["figures"])
        tabs = "".join(table_html(results, b, n, manifest) for b, n in s["tables"])
        body.append(
            f"<section><h2><span class='snum'>{s['num']}</span>{html.escape(s['title'])}</h2>"
            f"<div class='view'>computed on: {html.escape(s['view'])} &middot; bundle "
            f"{html.escape(s['bundle'])}</div>"
            f"<div class='finding'>{finding}</div>"
            f"<div class='caveat'>{caveat}</div>{figs}{tabs}</section>")
        md.append(f"\n## {s['num']}. {s['title']}\n\n{re.sub('<[^>]+>', '', finding)}\n\n"
                  f"> {re.sub('<[^>]+>', '', caveat)}\n")

    gates = ["dbchar_g1_corpus_identity", "dbchar_g2_canonical_units", "dbchar_g2b_rt_cds_recovery",
             "dbchar_g3_pair_geometry", "dbchar_g4_family_baseline", "dbchar_g5_metadata_sampling",
             "dbchar_g6_tool_calls"]
    grows, gate_rows = "", []
    for g in gates:
        rd = (results / g / "README.md").read_text(encoding="utf-8").splitlines()
        status = next((ln for ln in rd if ln.startswith("STATUS:")), "STATUS: ?")
        gate_rows.append(dict(bundle=g, status=status.split("\u2014")[0].strip(),
                              n_landed_tables=len(list((results / g / "tables").glob("*.tsv")))))
        grows += (f"<tr><td><code>{g}</code></td><td>{html.escape(status.split('—')[0].strip())}</td>"
                  f"<td>{len(list((results / g / 'tables').glob('*.tsv')))}</td></tr>")

    doc = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
           f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
           f"<title>Stage 1 — RT/retron corpus characterisation</title><style>{CSS}</style></head>"
           f"<body><div class='wrap'><header>"
           f"<div class='kicker'>Stage 1 · database characterisation</div>"
           f"<h1>A defensible representation of the RT/retron mining corpus</h1>"
           f"<div class='sub'>Seven landed bundles over one pinned corpus. Every number below is "
           f"resolved from a landed table; this page computes nothing.</div>"
           f"<div class='meta'>corpus record-manifest sha256 <code>{vals['manifest_sha']}</code>"
           f" &middot; human input audit: PENDING &middot; no measurement here is a project claim"
           f"</div></header>"
           f"<section><h2><span class='snum'>0</span>Gates</h2>"
           f"<table><tr><th>bundle</th><th>status</th><th>landed tables</th></tr>{grows}</table>"
           f"</section>"
           + "".join(body)
           + f"<section>{fill(F.CLOSING, vals, 'closing')}</section></div></body></html>")
    tdir = out / "tables"
    tdir.mkdir(parents=True, exist_ok=True)
    write_tsv(tdir / "g7_resolved_values.tsv",
              ["key", "bundle", "table", "selector", "column", "raw_value", "rendered"],
              sorted(trace, key=lambda r: r["key"]))
    write_tsv(tdir / "g7_figure_map.tsv",
              ["section", "figure", "produced_by_bundle", "plotted_numbers"],
              [dict(section=s["num"], figure=n, produced_by_bundle=bd,
                    plotted_numbers=f"{bd}/tables/{n}.tsv")
               for s in F.SECTIONS for bd, n in s["figures"]])
    write_tsv(tdir / "g7_gate_status.tsv", ["bundle", "status", "n_landed_tables"], gate_rows)
    (out / "REPORT.html").write_text(doc, encoding="utf-8")
    (out / "REPORT.md").write_text("\n".join(md), encoding="utf-8")
    if re.search(r"\{[a-z0-9_]+\}", doc):
        raise SystemExit("FATAL: an unresolved placeholder survived into the HTML")
    # MANIFEST: every artifact this gate lands, the script that made it, its unit and the
    # population its denominator equals (BS-17). The report itself carries no rate of its own -
    # every number in it belongs to the landed table g7_resolved_values.tsv names.
    F01, SELFP = "scripts/f01_restyle_figures.py", "scripts/assemble_report.py"
    man = [
        ("REPORT.html", SELFP, "see run.sh: assemble_report.py",
         "n/a - assembled document", "n/a - every rate is resolved from a landed table"),
        ("REPORT.md", SELFP, "see run.sh: assemble_report.py",
         "n/a - assembled document", "n/a - every rate is resolved from a landed table"),
        ("tables/g7_resolved_values.tsv", SELFP, "see run.sh: assemble_report.py",
         "resolved values", "n/a - one table lookup per row; no rate"),
        ("tables/g7_figure_map.tsv", SELFP, "see run.sh: assemble_report.py",
         "figures", "n/a - one figure per row; no rate"),
        ("tables/g7_gate_status.tsv", SELFP, "see run.sh: assemble_report.py",
         "bundles", "n/a - one landed gate per row; no rate"),
        ("tables/fig01_distance_distribution_restyled.tsv", F01,
         "see run.sh: f01_restyle_figures.py", "placements",
         "CANONICAL / ATYPICAL placements with a defined signed distance (carried from g3)"),
        ("tables/fig01_rt_length_by_family_restyled.tsv", F01,
         "see run.sh: f01_restyle_figures.py", "exact RT sequences",
         "V-RT-SINGLE exact RTs of that family, top 25 by n (carried from g4)"),
    ]
    for ext in ("png", "svg"):
        man.append((f"figures/fig01_distance_distribution_restyled.{ext}", F01,
                    "see run.sh: f01_restyle_figures.py", "placements",
                    "CANONICAL / ATYPICAL placements with a defined signed distance"))
        man.append((f"figures/fig01_rt_length_by_family_restyled.{ext}", F01,
                    "see run.sh: f01_restyle_figures.py", "exact RT sequences",
                    "V-RT-SINGLE exact RTs of that family, top 25 by n"))
    with (out / "MANIFEST.tsv").open("w", encoding="utf-8") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for row in sorted(man):
            fh.write("\t".join(row) + "\n")

    print(f"REPORT.html: {len(doc):,d} bytes, {len(F.SECTIONS)} sections, "
          f"{sum(len(s['figures']) for s in F.SECTIONS)} figures, {len(vals)} resolved values")
    return 0


if __name__ == "__main__":
    sys.exit(main())
