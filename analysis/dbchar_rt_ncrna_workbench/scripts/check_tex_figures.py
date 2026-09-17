#!/usr/bin/env python
"""Verify that every \\includegraphics in the thesis .tex resolves to a real figure,
and emit exports/thesis/FIGURE_PROVENANCE.tsv linking each LaTeX label to its source tables.

Usage:  .venv/bin/python scripts/check_tex_figures.py
Exit code 1 if a referenced figure is missing and is not a declared placeholder.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
import pandas as pd

WB   = Path(__file__).resolve().parents[1]
TEX  = (Path(sys.argv[1]) if len(sys.argv) > 1
        else WB / "exports_v2" / "results_database_characterization.tex")
FIGS = WB / "figures"
PROV = FIGS / "FIGURE_PROVENANCE.tsv"
OUT  = TEX.parent / "FIGURE_PROVENANCE.tsv"

def _resolve(stem: str) -> bool:
    """A reference may be bare ("N8_dataset_funnel") or carry the thesis graphics path and
    extension ("figures_db_thesis_section/N8_dataset_funnel.png"). Accept either, and look in
    the workbench figures/ AND in the folder staged next to the .tex."""
    name = Path(stem).stem
    rel  = TEX.parent / stem
    return (rel.exists() or (FIGS / f"{name}.png").exists()
            or (TEX.parent / "figures_db_thesis_section" / f"{name}.png").exists())

src = TEX.read_text()

# pair each figure environment's \includegraphics with its \label and caption
rows = []
for env in re.findall(r"\\begin\{figure\}.*?\\end\{figure\}", src, flags=re.S):
    inc = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", env)
    lab = re.search(r"\\label\{([^}]+)\}", env)
    cap = re.search(r"\\caption(?:\[[^\]]*\])?\{(.+?)\}\s*\n?\s*\\label", env, flags=re.S)
    if not inc:
        continue
    stem = inc.group(1)
    placeholder = "Placeholder" in env or "not yet generated" in env
    rows.append({
        "tex_label": lab.group(1) if lab else "(no label)",
        "figure_stem": Path(stem).stem,
        "file_exists": _resolve(stem),
        "declared_placeholder": placeholder,
        "caption_head": re.sub(r"\s+", " ", cap.group(1))[:70] + "…" if cap else "",
    })

df = pd.DataFrame(rows)

# attach provenance where the notebook recorded it
if PROV.exists():
    prov = pd.read_csv(PROV, sep="\t")
    prov["figure_stem"] = prov.figure.str.replace(".png", "", regex=False)
    df = df.merge(prov[["figure_stem", "section", "source_tables", "generated_utc"]],
                  on="figure_stem", how="left")
else:
    for c in ("section", "source_tables", "generated_utc"):
        df[c] = pd.NA

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, sep="\t", index=False)

missing   = df[~df.file_exists & ~df.declared_placeholder]
todo      = df[~df.file_exists &  df.declared_placeholder]
unused    = sorted({p.stem for p in FIGS.glob("*.png")} - set(df.figure_stem))

print(f"{len(df)} figure references in {TEX.name}")
print(f"  resolved ............. {int(df.file_exists.sum())}")
print(f"  declared placeholder . {len(todo)}   {list(todo.figure_stem)}")
print(f"  MISSING .............. {len(missing)} {list(missing.figure_stem)}")
if unused:
    print(f"  figures not cited in the .tex: {unused}")
print(f"\nwrote {OUT.relative_to(WB)}")
sys.exit(1 if len(missing) else 0)
