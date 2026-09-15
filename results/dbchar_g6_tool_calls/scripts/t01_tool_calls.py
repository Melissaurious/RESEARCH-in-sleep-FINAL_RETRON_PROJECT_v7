#!/usr/bin/env python3
"""t01 - the per-tool retron annotation/call matrix, missingness, and the extraction asymmetry.

Declared before any data is read:

  * the population is the **retron locus population**: loci whose records carry the `Retron`
    family label. Other families are reported beside it, never merged into it.
  * `system_subtypes` is NEVER pooled. It is two tools writing into one list, distinguished by
    the case of the first letter: **capital-initial = DefenseFinder, lowercase = PADLOC**
    (the project's standing known-wrong note). Each tool's vocabulary is reported separately,
    and agreement is measured only where both tools wrote something at one locus.
  * `metadata.detected_by` is the detection matrix: myRT / PADLOC / DefenseFinder.
  * agreement between tools is NOT independent corroboration - the tools share model lineage -
    so this gate reports the matrix and the disagreement classes, and claims neither.

The extraction asymmetry audit asks one question with a measurable answer: does what the corpus
*contains* (ncRNA carriage, geometry eligibility, RT length) differ by which tools called the
locus? If it does, any statistic computed on a tool-defined subset inherits that difference.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

TOOLS = ("myRT", "PADLOC", "DefenseFinder")


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def split_subtypes(raw: str) -> tuple[list[str], list[str], list[str]]:
    """(DefenseFinder-style, PADLOC-style, unclassifiable) by the declared case rule."""
    try:
        vals = json.loads(raw) if isinstance(raw, str) else []
    except json.JSONDecodeError:
        return [], [], [str(raw)]
    if not isinstance(vals, list):
        return [], [], [str(vals)]
    df_, pl, other = [], [], []
    for v in vals:
        s = str(v)
        if not s:
            continue
        c = s[0]
        (df_ if c.isupper() else pl if c.islower() else other).append(s)
    return df_, pl, other


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--derived", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    D, W = Path(a.derived), Path(a.work)
    T, DV = W / "tables", W / "derived"
    T.mkdir(parents=True, exist_ok=True)
    DV.mkdir(parents=True, exist_ok=True)

    r = pd.read_parquet(D / "rt_records_v1.parquet", columns=[
        "record_key", "is_first_copy", "locus_key", "rt_seq_hash", "file_label",
        "source_database", "detected_by_raw", "system_subtypes_raw", "n_system_subtypes",
        "n_ncrna", "elig_geometry", "rt_aa_len", "tax_species", "genome_id_norm"])
    f = r[r.is_first_copy].copy()
    det = f.detected_by_raw.fillna("[]")
    for t in TOOLS:
        f[f"by_{t}"] = det.str.contains(f'"{t}"', regex=False)
    f["detected_by_set"] = ["|".join([t for t in TOOLS if row[f"by_{t}"]])
                            for _, row in f[[f"by_{t}" for t in TOOLS]].iterrows()]
    f["n_tools"] = f[[f"by_{t}" for t in TOOLS]].sum(axis=1)

    # ---- 1 · the call matrix, at three units, per family -----------------------------
    w(T / "g6_tool_matrix_by_family.tsv", f.groupby(["file_label", "detected_by_set"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique")).reset_index()
      .sort_values("n_records", ascending=False).assign(
          unit="records / loci / exact RTs",
          denominator="distinct raw records of that family label"))
    retron = f[f.file_label.eq("Retron")]
    w(T / "g6_tool_matrix_retron.tsv", retron.groupby("detected_by_set").agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        n_exact_rt=("rt_seq_hash", "nunique"), n_genomes=("genome_id_norm", "nunique"),
        n_with_ncrna=("n_ncrna", lambda s: int((s > 0).sum())),
        pct_with_ncrna=("n_ncrna", lambda s: round(100 * (s > 0).mean(), 4))).reset_index()
      .sort_values("n_records", ascending=False).assign(
          n_retron_records=len(retron), unit="records / loci / exact RTs",
          denominator="distinct raw records of the Retron family label"))
    w(T / "g6_tool_presence_retron.tsv", pd.DataFrame([
        [t, int(retron[f"by_{t}"].sum()), len(retron),
         round(100 * retron[f"by_{t}"].mean(), 4),
         int(retron.loc[retron[f"by_{t}"], "locus_key"].nunique())] for t in TOOLS]
        + [["any_tool", int((retron.n_tools > 0).sum()), len(retron),
            round(100 * (retron.n_tools > 0).mean(), 4),
            int(retron.loc[retron.n_tools > 0, "locus_key"].nunique())],
           ["all_three_tools", int((retron.n_tools == 3).sum()), len(retron),
            round(100 * (retron.n_tools == 3).mean(), 4),
            int(retron.loc[retron.n_tools == 3, "locus_key"].nunique())]],
        columns=["tool", "n_records", "n_retron_records", "pct_of_retron_records", "n_loci"]).assign(
        unit="records / loci", denominator="distinct raw records of the Retron family label"))

    # The directly comparable quantity for the independent awk route: computed over ALL
    # records of master_Retron, not first copies, because awk sees every line.
    ar = r[r.file_label.eq("Retron")].copy()
    det_all = ar.detected_by_raw.fillna("[]")
    combo_all = []
    for d in det_all:
        combo_all.append("|".join([t for t in TOOLS if f'"{t}"' in d]))
    ar["detected_by_set"] = combo_all
    pa = [split_subtypes(x) for x in ar.system_subtypes_raw]
    w(T / "g6_tool_matrix_retron_all_records.tsv", pd.concat([
        ar.groupby("detected_by_set").size().rename("n").reset_index().rename(
            columns={"detected_by_set": "key"}).assign(measure="detected_by_combination"),
        pd.DataFrame([["subtype_case_class", "defensefinder_style", sum(1 for p in pa if p[0])],
                      ["subtype_case_class", "padloc_style", sum(1 for p in pa if p[1])],
                      ["subtype_case_class", "both_styles",
                       sum(1 for p in pa if p[0] and p[1])],
                      ["subtype_case_class", "records", len(ar)]],
                     columns=["measure", "key", "n"])], ignore_index=True).assign(
        unit="records", denominator="ALL records of master_Retron (including duplicate lines)"))

    # ---- 2 · subtypes, split by tool, NEVER pooled -----------------------------------
    parts = [split_subtypes(x) for x in f.system_subtypes_raw]
    f["subtypes_defensefinder"] = ["|".join(p[0]) for p in parts]
    f["subtypes_padloc"] = ["|".join(p[1]) for p in parts]
    f["subtypes_unclassifiable"] = ["|".join(p[2]) for p in parts]
    f["has_df_subtype"] = f.subtypes_defensefinder.ne("")
    f["has_pl_subtype"] = f.subtypes_padloc.ne("")
    ret = f[f.file_label.eq("Retron")]
    w(T / "g6_subtype_presence.tsv", pd.DataFrame([
        ["records with a DefenseFinder-style subtype", int(ret.has_df_subtype.sum()), len(ret)],
        ["records with a PADLOC-style subtype", int(ret.has_pl_subtype.sum()), len(ret)],
        ["records with both", int((ret.has_df_subtype & ret.has_pl_subtype).sum()), len(ret)],
        ["records with neither", int((~ret.has_df_subtype & ~ret.has_pl_subtype).sum()), len(ret)],
        ["records with an unclassifiable subtype string",
         int(ret.subtypes_unclassifiable.ne("").sum()), len(ret)],
        ["records detected by DefenseFinder but with no DefenseFinder-style subtype",
         int((ret.by_DefenseFinder & ~ret.has_df_subtype).sum()), int(ret.by_DefenseFinder.sum())],
        ["records detected by PADLOC but with no PADLOC-style subtype",
         int((ret.by_PADLOC & ~ret.has_pl_subtype).sum()), int(ret.by_PADLOC.sum())],
    ], columns=["measure", "n", "denominator_n"]).assign(
        unit="records", denominator="Retron records, or the tool-detected subset named in the measure"))
    for tool, col in (("DefenseFinder", "subtypes_defensefinder"), ("PADLOC", "subtypes_padloc")):
        sub = ret[ret[col].ne("")]
        w(T / f"g6_subtype_vocabulary_{tool}.tsv", sub.groupby(col).agg(
            n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
            n_exact_rt=("rt_seq_hash", "nunique")).reset_index().rename(
                columns={col: "subtype_label"}).sort_values("n_records", ascending=False).assign(
                    tool=tool, n_records_with_this_tools_subtype=len(sub), unit="records",
                    denominator=f"Retron records carrying a {tool}-style subtype"))
    both = ret[ret.has_df_subtype & ret.has_pl_subtype].copy()
    if len(both):
        # agreement is compared on the trailing type token, because the two tools spell the
        # same subtype differently (`Retron_I_A` vs `retron_i_a`): the comparison is
        # case-insensitive on non-alphanumeric-stripped strings, and is reported as such.
        norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())  # noqa: E731
        both["df_norm"] = [norm(x) for x in both.subtypes_defensefinder]
        both["pl_norm"] = [norm(x) for x in both.subtypes_padloc]
        both["agree"] = both.df_norm.eq(both.pl_norm)
        w(T / "g6_subtype_agreement.tsv", pd.DataFrame([
            ["records where both tools wrote a subtype", len(both), len(ret)],
            ["the two strings agree after case/punctuation normalisation",
             int(both.agree.sum()), len(both)],
            ["they disagree", int((~both.agree).sum()), len(both)],
        ], columns=["measure", "n", "denominator_n"]).assign(
            unit="records", denominator="Retron records where both tools wrote a subtype",
            caveat="agreement here is NOT independent corroboration: the tools share model lineage"))
        w(T / "g6_subtype_disagreement_pairs.tsv", both[~both.agree].groupby(
            ["subtypes_defensefinder", "subtypes_padloc"]).agg(
            n_records=("record_key", "size"), n_loci=("locus_key", "nunique")).reset_index()
          .sort_values("n_records", ascending=False).head(60).assign(
              unit="records", denominator="Retron records where the two tools disagree (top 60)"))

    # ---- 3 · the extraction asymmetry -------------------------------------------------
    w(T / "g6_extraction_asymmetry.tsv", ret.groupby("detected_by_set").agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique"),
        pct_with_ncrna=("n_ncrna", lambda s: round(100 * (s > 0).mean(), 4)),
        median_ncrna_per_record=("n_ncrna", "median"),
        pct_geometry_eligible=("elig_geometry", lambda s: round(100 * s.mean(), 4)),
        median_rt_aa_len=("rt_aa_len", "median"),
        n_species=("tax_species", "nunique"),
        n_databases=("source_database", "nunique")).reset_index().sort_values(
            "n_records", ascending=False).assign(
                unit="records", denominator="Retron records of that detected_by combination",
                note="a difference here means a tool-defined subset is not a random subset"))
    w(T / "g6_tool_by_database.tsv", ret.groupby(["source_database", "detected_by_set"]).agg(
        n_records=("record_key", "size"), n_loci=("locus_key", "nunique")).reset_index().assign(
        unit="records", denominator="Retron records of that source_database"))
    f[["record_key", "locus_key", "rt_seq_hash", "file_label", "source_database",
       "detected_by_set", "n_tools", "by_myRT", "by_PADLOC", "by_DefenseFinder",
       "subtypes_defensefinder", "subtypes_padloc", "subtypes_unclassifiable",
       "n_ncrna", "elig_geometry"]].to_parquet(
        DV / "rt_tool_calls_v1.parquet", index=False, compression="zstd")
    print(f"  rt_tool_calls_v1: {len(f):,d} rows", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
