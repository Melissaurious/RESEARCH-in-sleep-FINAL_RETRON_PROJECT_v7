import nbformat as nbf
C=[]
def md(s): C.append(nbf.v4.new_markdown_cell(s.strip("\n")))
def code(s): C.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# Stage-1 RT / retron database characterization — exploratory workbench

**This notebook is exploratory. It is not a governed gate and it does not supersede the landed
`dbchar_g1`…`dbchar_g7` bundles.** Read `CONTEXT.md` next to this file before using any number
from here.

Working rules:

* Every analytical section declares its **scientific question**, **analytical unit**,
  **denominator** and **datasets/columns**.
* Canonical Stage-1 values are *loaded* from
  `results/dbchar_g7_stage1_report/tables/g7_resolved_values.tsv`, never retyped. Where this
  notebook recomputes such a value it prints an explicit `MATCH` / `DIFF` check.
* Heavy parquet is queried through DuckDB with column projection and predicate pushdown.
  Aggregates are cached as TSV under `tables/`; plots are drawn from those cached tables.
* ncRNA-anchor-only records are **outside every RT denominator here** (decision 2026-09-15,
  Rule 1). They are already absent from `rt_records_v1.parquet`.
* `MULTI` is a stratum, never merged into a single family (Rule 2).

Sections **A–D** are implemented. **E–I** are scaffolded with their declarations only.
**J** is the open slot for analyses added later.

---

## 0. Setup

Run this section once per kernel. After that, every analytical cell is independently rerunnable:
each opens its own DuckDB connection and re-reads its cached table from disk.
""")

code(r'''
import os, sys, tempfile, textwrap
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "mplconfig_dbchar"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

def _bootstrap_venv():
    """Make the workbench .venv importable even under a different kernel.

    The heavy dependencies (duckdb, matplotlib, matplotlib-venn) live in
    ARIS_OUTPUT/dbchar_workbench/.venv, which is a --system-site-packages overlay on the
    retron_tradicional env. If this notebook is run under the plain retron_tradicional kernel
    (or any other Python 3.12 kernel), duckdb is missing. Rather than require a particular
    kernel, add the overlay's site-packages to sys.path on demand.
    """
    try:
        import duckdb  # noqa: F401
        return None
    except ModuleNotFoundError:
        pass
    here = Path.cwd()
    for base in [here, *here.parents]:
        for cand in sorted(base.glob(".venv/lib/python*/site-packages")):
            if (cand / "duckdb").exists():
                sys.path.insert(0, str(cand))
                return cand
        for cand in sorted(base.glob("ARIS_OUTPUT/dbchar_workbench/.venv/lib/python*/site-packages")):
            if (cand / "duckdb").exists():
                sys.path.insert(0, str(cand))
                return cand
    raise ModuleNotFoundError(
        "duckdb not found, and the workbench .venv could not be located from "
        f"{here}.\n"
        "Fix one of these ways:\n"
        "  1. select the 'dbchar-workbench' kernel (see playground/README.md), or\n"
        "  2. launch Jupyter from ARIS_OUTPUT/dbchar_workbench so the .venv can be found, or\n"
        "  3. recreate the venv:\n"
        "     /home/borg/miniconda3/envs/retron_tradicional/bin/python -m venv \\\n"
        "         --system-site-packages ARIS_OUTPUT/dbchar_workbench/.venv\n"
        "     ARIS_OUTPUT/dbchar_workbench/.venv/bin/pip install duckdb matplotlib "
        "matplotlib-venn ipykernel")

_BOOTSTRAPPED = _bootstrap_venv()

import duckdb, pandas as pd, numpy as np
import matplotlib
import matplotlib.pyplot as plt

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 60)
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 150, "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.25, "axes.axisbelow": True})

def _find_wb() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if p.name == "dbchar_workbench" and (p / "CONTEXT.md").exists():
            return p
        if (p / "ARIS_OUTPUT/dbchar_workbench/CONTEXT.md").exists():
            return p / "ARIS_OUTPUT/dbchar_workbench"
    raise RuntimeError("cannot locate ARIS_OUTPUT/dbchar_workbench from %s" % Path.cwd())

WB       = _find_wb()
REPO     = WB.parents[1]                                   # the dbchar-workbench worktree
MAIN     = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7")
DERIVED  = MAIN / "data" / "derived"                       # READ-ONLY canonical datasets
RESULTS  = REPO / "results"

# Output root. Set DBCHAR_OUT to redirect tables/ and figures/ somewhere else -- do this in a
# personal copy of the notebook so your experiments never overwrite the canonical cached
# tables and figures that the .tex and the manifest refer to. Reading is unaffected: an empty
# output dir simply means cache() recomputes from parquet (~40 s cold).
OUT      = Path(os.environ["DBCHAR_OUT"]).resolve() if os.environ.get("DBCHAR_OUT") else WB
TABLES   = OUT / "tables"; FIGURES = OUT / "figures"
EXPORTS  = WB / "exports"; NOTES  = WB / "notes"
for d in (TABLES, FIGURES, EXPORTS, NOTES): d.mkdir(parents=True, exist_ok=True)

assert DERIVED.is_dir(), DERIVED
print("workbench :", WB)
print("output    :", OUT, "(canonical)" if OUT == WB else "(REDIRECTED via DBCHAR_OUT)")
print("worktree  :", REPO)
print("derived   :", DERIVED, "(read-only)")
print("python    :", sys.version.split()[0], "| duckdb", duckdb.__version__,
      "| pandas", pd.__version__, "| matplotlib", matplotlib.__version__)
print("kernel    :", Path(sys.prefix).name,
      f"(+ bootstrapped {_BOOTSTRAPPED})" if _BOOTSTRAPPED else "(deps native to this kernel)")
''')

code(r'''
# --- DuckDB access layer ------------------------------------------------------------------
# One view per canonical parquet, named without the _v1 suffix. Views are lazy: a query only
# touches the columns and row groups it needs, so rt_records (3.06M x 114) and rt_window_cds
# (44.3M) are never materialised in full.

PARQUETS = {p.stem.replace("_v1", ""): p for p in sorted(DERIVED.glob("*.parquet"))}

def con():
    c = duckdb.connect()
    c.execute("SET threads TO 8")
    c.execute("PRAGMA memory_limit='8GB'")
    for name, path in PARQUETS.items():
        c.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet('{path}')")
    return c

def Q(sql: str) -> pd.DataFrame:
    """Run one SQL statement against the canonical parquet views and return a DataFrame."""
    c = con()
    try:
        return c.execute(sql).df()
    finally:
        c.close()

def cache(name: str, sql: str = None, fn=None, force: bool = False, pop=None) -> pd.DataFrame:
    """Compute-once aggregate, persisted to tables/<name>.tsv. Plots read these, not parquet.

    `pop` names the analytical population the table is counted on, as a Z0 registry id (or a
    list of ids for a table that deliberately spans several rungs). It is recorded in
    tables/_table_populations.tsv so that no cached number is ever separated from its
    denominator. See section Z0.
    """
    p = TABLES / f"{name}.tsv"
    if pop is not None:
        register_pop(name, pop)
    if p.exists() and not force:
        return pd.read_csv(p, sep="\t")
    df = Q(sql) if sql is not None else fn()
    df.to_csv(p, sep="\t", index=False)
    return df

def save(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Re-persist a cached table after derived columns were added in-cell."""
    df.to_csv(TABLES / f"{name}.tsv", sep="\t", index=False)
    return df

# --- population bookkeeping ---------------------------------------------------------------
# Every cached table and every figure declares the population it is counted on. The ids are
# defined once, computed not typed, in section Z0 -> tables/Z0_population_registry.tsv.

def register_pop(table_name: str, pop) -> None:
    """Record which Z0 population id(s) a cached table is counted on."""
    ids = [pop] if isinstance(pop, str) else list(pop)
    p = TABLES / "_table_populations.tsv"
    rows = pd.read_csv(p, sep="\t").to_dict("records") if p.exists() else []
    rows = [r for r in rows if r["table"] != table_name]
    rows.append({"table": table_name, "pop_id": ";".join(ids)})
    pd.DataFrame(rows).sort_values("table").to_csv(p, sep="\t", index=False)

def pop_row(pop_id: str):
    """Look one population id up in the Z0 registry. Returns None before Z0 has been run."""
    p = TABLES / "Z0_population_registry.tsv"
    if not p.exists():
        return None
    r = pd.read_csv(p, sep="\t")
    r = r.loc[r["pop_id"] == pop_id]
    return r.iloc[0] if len(r) == 1 else None

def pop_stamp(pop_id: str) -> str:
    """'PL-CANON - eligible, non-redundant placement - n = 344,154', for a figure caption."""
    r = pop_row(pop_id)
    if r is None:
        return pop_id
    return f"{pop_id} · {r['unit']} · n = {int(r['n']):,}"

print(len(PARQUETS), "canonical datasets available as views:")
print(textwrap.fill(", ".join(PARQUETS), 100))
''')

code(r'''
# --- canonical Stage-1 values -------------------------------------------------------------
# g7_resolved_values.tsv is the number registry: key -> (bundle, table, selector, column, value).
# Never retype a Stage-1 number; load it and check against it.

RESOLVED = pd.read_csv(RESULTS / "dbchar_g7_stage1_report/tables/g7_resolved_values.tsv", sep="\t")

def canon(key: str, numeric: bool = True):
    row = RESOLVED.loc[RESOLVED["key"] == key]
    if len(row) != 1:
        raise KeyError(f"{key!r} not in g7_resolved_values.tsv (n={len(row)})")
    v = row["raw_value"].iloc[0]
    return float(v) if numeric else v

def gate_table(bundle: str, name: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS / bundle / "tables" / f"{name}.tsv", sep="\t")

def check(label: str, got, key: str = None, expected=None, tol: float = 0.0):
    """Assert a recomputed value against the canonical Stage-1 value; report, never raise."""
    exp = canon(key) if key is not None else expected
    ok = abs(float(got) - float(exp)) <= tol
    print(f"  [{'MATCH' if ok else ' DIFF'}] {label:<46} recomputed={got:<16} canonical={exp}")
    return ok

FIGURE_PROVENANCE = []

def savefig(fig, name: str, sources=None, section: str = None, pop=None):
    """Save a figure and record where it came from, into figures/FIGURE_PROVENANCE.tsv.

    `pop` is a Z0 population id (or list of ids). It is stamped onto the figure itself, so a
    reader can never see a percentage without seeing the denominator it was taken over.
    """
    ids = ([pop] if isinstance(pop, str) else list(pop)) if pop is not None else []
    if ids:
        fig.text(0.0, -0.008, "population:  " + "      |      ".join(pop_stamp(i) for i in ids),
                 fontsize=6.6, color="#555555", ha="left", va="top",
                 transform=fig.transFigure)
    p = FIGURES / f"{name}.png"
    fig.savefig(p, bbox_inches="tight")
    if sources is None:                      # infer: cached tables whose stem shares the prefix
        pre = name.split("_")[0]
        sources = sorted(f.stem for f in TABLES.glob(f"{pre}*.tsv"))
    FIGURE_PROVENANCE.append({
        "figure": f"{name}.png",
        "section": section or name.split("_")[0],
        "source_tables": ";".join(sources),
        "population": ";".join(ids),
        "generated_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    pd.DataFrame(FIGURE_PROVENANCE).to_csv(FIGURES / "FIGURE_PROVENANCE.tsv", sep="\t", index=False)
    return p

print(f"{len(RESOLVED)} canonical Stage-1 values registered.")
print("corpus record-manifest sha256:", canon("manifest_sha", numeric=False))
''')
