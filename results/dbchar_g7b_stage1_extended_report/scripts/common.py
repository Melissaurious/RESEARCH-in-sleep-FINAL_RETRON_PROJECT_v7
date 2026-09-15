#!/usr/bin/env python3
"""common - shared, declared conventions for dbchar_g7b_stage1_extended_report.

Every convention that decides a number is declared HERE, before any analysis runs, so that no
analysis script can quietly pick its own. Analysis scripts (a*.py) read the registered Stage-1
derived datasets and landed g1-g7 tables and write TSVs; figure scripts (f*.py) read ONLY this
bundle's tables/; the assembler computes nothing.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- paths (set by run.sh via env)
HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("G7B_ROOT", HERE.parents[2])).resolve()          # project root
DERIVED = Path(os.environ.get("G7B_DERIVED", ROOT / "data" / "derived"))
RESULTS = Path(os.environ.get("G7B_RESULTS", ROOT / "results"))
WORK = Path(os.environ.get("G7B_WORK", ROOT / "ARIS_OUTPUT" / "01_database_characterization"
                           / "dbchar_g7b_stage1_extended_report" / "work"))
T = WORK / "tables"
FIG = WORK / "figures"
META = WORK / "meta"
CACHE = WORK / "cache"
GATE = "dbchar_g7b_stage1_extended_report"
GTDB_CATALOGUE = ROOT / ("MELISSA_DATA/supplementary_material/databases_metadata_files/"
                         "metadata_files/gtdb_bacteria_metadata.tsv.gz")
PADLOC_SYS = Path("/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/sys")
PADLOC_CM_META = Path("/home/borg/RETRONS_january_2026/the-retron-project/src/padloc/data/cm_meta.txt")

# ---------------------------------------------------------------- declared conventions
N_MAJOR_FAMILIES = 12          # top families by V-RT-SINGLE exact RTs; the rest -> "other"
MIN_N_RATE = 30                # a rate on fewer units is shown masked / not plotted
TECH_MODE_HALF_WIDTH = 150     # g3's own rule: CANONICAL downstream within +-150 bp of the median
ADJACENT_MAX_GAP = 500         # "adjacent upstream" configuration: 0 CDS between and gap <= 500 bp
BIG_DBS = ("ncbi_bacteria", "gtdb_bacteria", "mgnify_human_gut")
DB_ORDER = ("ncbi_bacteria", "gtdb_bacteria", "mgnify_human_gut", "gem", "mgnify_soil",
            "mgnify_marine", "ncbi_archaea", "gtdb_archaea")
TOOLS = ("myRT", "PADLOC", "DefenseFinder")
COMBO_ORDER = ("myRT|PADLOC|DefenseFinder", "myRT", "myRT|DefenseFinder", "myRT|PADLOC",
               "PADLOC", "PADLOC|DefenseFinder", "DefenseFinder")
WILSON_Z = 1.959963984540054   # 95% two-sided
SEED = 20260915


def wilson(k, n, z: float = WILSON_Z):
    """Wilson score interval for k successes in n trials. Returns (lo, hi) as proportions.
    Vectorised over numpy arrays; n == 0 -> (nan, nan)."""
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        p = k / n
        den = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / den
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
        lo, hi = centre - half, centre + half
    lo = np.where(n > 0, lo, np.nan)
    hi = np.where(n > 0, hi, np.nan)
    return lo, hi


def add_rate(df: pd.DataFrame, k: str, n: str, prefix: str = "pct") -> pd.DataFrame:
    """Append pct, Wilson lo/hi (as percentages) for columns k/n."""
    lo, hi = wilson(df[k].to_numpy(), df[n].to_numpy())
    with np.errstate(invalid="ignore", divide="ignore"):
        df[prefix] = 100 * df[k] / df[n]
    df[f"{prefix}_ci_lo"] = np.clip(100 * lo, 0, 100)
    df[f"{prefix}_ci_hi"] = np.clip(100 * hi, 0, 100)
    return df


# ---------------------------------------------------------------- IO
def _fmt(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_float_dtype(out[c]):
            out[c] = out[c].round(4)
    return out


def write_table(name: str, df: pd.DataFrame, unit: str, denominator: str, script: str,
                estimate: str = "census") -> Path:
    """Land a table. unit/denominator are REQUIRED (BS-17) and are written both as columns and to
    the manifest metadata. `estimate` is 'census' or names the estimator (WA-D.2)."""
    if not unit or not denominator or unit in ("-", "?") or denominator in ("-", "?"):
        raise SystemExit(f"FATAL: {name}: unit/denominator must say something")
    T.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    d = _fmt(df)
    d["unit"] = unit
    d["denominator"] = denominator
    p = T / f"{name}.tsv"
    d.to_csv(p, sep="\t", index=False, lineterminator="\n", na_rep="")
    (META / f"tables__{name}.json").write_text(json.dumps(dict(
        artifact=f"tables/{name}.tsv", script=f"scripts/{script}", unit=unit,
        denominator=denominator, estimate=estimate), sort_keys=True))
    print(f"  table {name}: {len(d):,d} rows", flush=True)
    return p


def read_table(name: str) -> pd.DataFrame:
    return pd.read_csv(T / f"{name}.tsv", sep="\t", keep_default_na=False, na_values=[""])


def landed(bundle: str, table: str) -> pd.DataFrame:
    return pd.read_csv(RESULTS / bundle / "tables" / table, sep="\t", keep_default_na=False,
                       na_values=[""])


def derived(name: str, columns=None) -> pd.DataFrame:
    return pd.read_parquet(DERIVED / f"{name}.parquet", columns=columns)


# ---------------------------------------------------------------- cached joined views
def cached(name: str, build):
    """A cache is a regenerated intermediate (never landed): WORK/cache/<name>.parquet."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{name}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    df = build()
    df.to_parquet(p, index=False)
    return df


def records() -> pd.DataFrame:
    """Distinct RT-anchored records (first copy of byte-identical lines) with the fields used."""
    cols = ["record_key", "locus_key", "physical_locus_key", "rt_seq_hash", "source_database",
            "file_label", "multilabel", "genome_id_norm", "taxonomy_system", "tax_phylum",
            "tax_class", "tax_order", "tax_genus", "tax_species", "rt_aa_len", "bt_status",
            "no_rt_cds_class", "elig_rt_coords", "elig_geometry", "win_start", "win_end",
            "fullseq_len", "rt_start", "rt_end", "rt_strand", "true_start_clipped",
            "clipped_end_flag", "rt_at_window_edge", "window_inverted", "rt_in_window",
            "rtcds_partial", "n_rt_cds", "n_ncrna", "is_first_copy", "n_copies_of_line"]

    def build():
        r = derived("rt_records_v1", cols)
        return r[r.is_first_copy].drop(columns=["is_first_copy"]).reset_index(drop=True)
    return cached("records_distinct", build)


def combo_name(df: pd.DataFrame) -> pd.Series:
    """'myRT|PADLOC|DefenseFinder'-style name from boolean by_<tool> columns (vectorised)."""
    parts = [np.where(df[f"by_{t}"].to_numpy(), t, "") for t in TOOLS]
    out = pd.Series(["|".join(x for x in trio if x) for trio in zip(*parts)], index=df.index)
    return out


def physical_retron_loci() -> pd.DataFrame:
    """Retron physical loci (family_label_set == 'Retron') with tool union, canonical carriage and
    the representative record's window/context fields."""
    def build():
        pl = derived("rt_physical_loci_v1", ["physical_locus_key", "family_label_set",
                                             "representative_record_key", "n_source_databases",
                                             "n_genomes", "any_elig_geometry"])
        pl = pl[pl.family_label_set == "Retron"].drop(columns="family_label_set")
        tc = derived("rt_tool_calls_v1", ["record_key", "locus_key", "by_myRT", "by_PADLOC",
                                          "by_DefenseFinder", "subtypes_padloc",
                                          "subtypes_defensefinder", "n_ncrna"])
        rec = records()[["record_key", "physical_locus_key", "source_database", "rt_seq_hash"]]
        tc = tc.merge(rec, on="record_key", how="inner")
        tc = tc[tc.physical_locus_key.isin(pl.physical_locus_key)]
        g = tc.groupby("physical_locus_key", sort=False)
        agg = g.agg(by_myRT=("by_myRT", "max"), by_PADLOC=("by_PADLOC", "max"),
                    by_DefenseFinder=("by_DefenseFinder", "max"), n_records=("record_key", "size"),
                    max_ncrna=("n_ncrna", "max"), rt_seq_hash=("rt_seq_hash", "first"))
        combo_rec = (tc.by_myRT.astype(int) * 4 + tc.by_PADLOC.astype(int) * 2
                     + tc.by_DefenseFinder.astype(int))
        agg["n_combos"] = combo_rec.groupby(tc.physical_locus_key).nunique()
        agg = agg.reset_index()
        agg["combo"] = combo_name(agg)
        # per-tool subtype label of the locus: the set of non-empty labels over its records
        def labels(col):
            s = tc[tc[col].fillna("") != ""].groupby("physical_locus_key")[col].agg(
                lambda v: "||".join(sorted(set(v))))
            return s
        agg = agg.merge(labels("subtypes_padloc").rename("padloc_subtype"),
                        left_on="physical_locus_key", right_index=True, how="left")
        agg = agg.merge(labels("subtypes_defensefinder").rename("defensefinder_subtype"),
                        left_on="physical_locus_key", right_index=True, how="left")
        dbs = rec[rec.physical_locus_key.isin(pl.physical_locus_key)].groupby(
            "physical_locus_key").source_database.agg(lambda v: "|".join(
                d for d in DB_ORDER if d in set(v)))
        agg = agg.merge(dbs.rename("source_database_set"), left_on="physical_locus_key",
                        right_index=True, how="left")
        pairs = derived("rt_ncrna_pairs_v1", ["physical_locus_key", "canonical", "file_label",
                                              "nc_seq_hash"])
        cp = pairs[pairs.canonical]
        can = cp.groupby("physical_locus_key").size().rename("n_canonical")
        # A locus deposited in two databases carries the SAME ncRNA call twice (g3's
        # "same_call_from_another_record_of_the_same_locus"). Counting placements would make a
        # RefSeq/GenBank twin look like a two-ncRNA locus, so every multiplicity view uses the
        # number of DISTINCT exact ncRNA sequences at the locus.
        seqs = cp.groupby("physical_locus_key").nc_seq_hash.nunique().rename("n_canonical_seqs")
        allc = pairs.groupby("physical_locus_key").size().rename("n_placements_all")
        agg = agg.merge(can, left_on="physical_locus_key", right_index=True, how="left")
        agg = agg.merge(seqs, left_on="physical_locus_key", right_index=True, how="left")
        agg = agg.merge(allc, left_on="physical_locus_key", right_index=True, how="left")
        for c in ("n_canonical", "n_canonical_seqs", "n_placements_all"):
            agg[c] = agg[c].fillna(0).astype(int)
        agg = agg.merge(pl, on="physical_locus_key", how="left")
        return agg
    return cached("retron_physical_loci_v2", build)


# ---------------------------------------------------------------- figure style
PALETTE = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
NEUTRAL = "#9a9993"
INK = "#1b1b1a"
INK2 = "#52514e"
GRID = "#e4e3df"
SEQ = ("#eef4fb", "#cfe0f5", "#a3c4ec", "#6fa3e0", "#3f80d0", "#2a62ad", "#1d4886", "#10305e")


def mpl_setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10,
        "axes.titleweight": "bold", "axes.labelsize": 9, "axes.edgecolor": "#8a8984",
        "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
        "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
        "svg.hashsalt": GATE, "figure.dpi": 100, "savefig.dpi": 150,
        "axes.prop_cycle": matplotlib.cycler(color=list(PALETTE)),
    })
    return plt


def save_fig(fig, name: str, data: pd.DataFrame, unit: str, denominator: str, script: str):
    """PNG + SVG with deterministic metadata, and the plotted data as tables/<name>.tsv."""
    FIG.mkdir(parents=True, exist_ok=True)
    write_table(name, data, unit, denominator, script)
    fig.savefig(FIG / f"{name}.png", metadata={"Software": None}, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", metadata={"Date": None, "Creator": None},
                bbox_inches="tight")
    for ext in ("png", "svg"):
        (META / f"figures__{name}.{ext}.json").write_text(json.dumps(dict(
            artifact=f"figures/{name}.{ext}", script=f"scripts/{script}", unit=unit,
            denominator=denominator, estimate="n/a - a view over the same-basename table"),
            sort_keys=True))
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f"  figure {name}", flush=True)


def stamp(ax, text: str, y: float = -0.16, width: int = 118):
    """Unit/denominator stamp under an axis, in secondary ink.

    The text is wrapped: an unwrapped stamp widens the saved bounding box (`bbox_inches="tight"`)
    far past the plot and leaves a band of white space beside the figure."""
    import textwrap
    wrapped = "\n".join(textwrap.wrap(text, width=width, break_long_words=False))
    ax.text(0, y, wrapped, transform=ax.transAxes, fontsize=7.5, color=INK2, va="top", ha="left",
            linespacing=1.45)


def fmt_int(v) -> str:
    return f"{int(v):,d}"


def log(msg: str):
    print(msg, flush=True)


def isnan(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))
