#!/usr/bin/env python3
"""M2b PRE-ACTIVATION CENSUS — size the modern retron / retron-like query universe.

This is a count, not the freeze. It reads only frozen Stage-1 derived datasets and the clean
historical Mestre proteins, and it examines NO placement. The tier rules below were written
before this script was first run and are the ones proposed for the M2b freeze.

UNIT. Exact RT (`rt_seq_hash` = sha256 of `rt_seq`). Only RT-anchored records enter
(`rt_tool_calls_v1`, which excludes the ncRNA-anchor-only population by construction).
Evidence is assessed PER RECORD (one system call at one locus), because system-level evidence
has to co-occur on one locus. An exact RT then takes the BEST record tier it carries, and the
number of records at each tier is kept alongside.

EVIDENCE LINES, per record:
  DF   DefenseFinder called a retron system on this record      (by_DefenseFinder)
  PAD  PADLOC called a retron system on this record             (by_PADLOC)
  NC   the record has >= 1 canonical, geometry-eligible RT-ncRNA pair (rt_ncrna_pairs_v1)
  PROF myRT labelled the RT a Retron-family RT                  (by_myRT, file_label == Retron)
  !! DF, PAD and NC all descend from Mestre/Toro-lab models. PADLOC's 21 retron CMs are
     Mestre-authored, and the DF retron profiles were iterated on the known set. The lines are
     NOT independent of the Mestre classification. Tier A is "strong system context", not
     "independent of Mestre". Every placement summary must carry this circularity flag.

RECORD TIER (file_label == 'Retron'; the MULTI stratum is handled separately):
  A   >= 2 of {DF, PAD, NC}
  B1  exactly 1 of {DF, PAD, NC}
  B0  none of them; PROF only (RT-profile evidence alone)
Other strata:
  M   the exact RT's family_label_set contains Retron AND another label, or it carries a
      MULTI record (Stage-1 rule 2: kept separate, never merged into A/B)
  D   a DF or PAD retron system call on a record whose file_label is NOT Retron
      (tool-family discordance; reported, excluded from primary placement)
  X   no retron evidence of any kind (Group II, DGR, CRISPR, UG*, Abi*, G2L*, ...):
      NOT a query target; eligible only as a declared outgroup/negative-control source
REFERENCE FLAG (orthogonal): REF_MESTRE — rt_seq identical to one of the 1,814 clean
  published-accession Mestre proteins. It is reported, and it promotes nothing. These are
  the historical references themselves and serve as placement-recovery controls.
"""
import csv, glob, hashlib, os, sys
import pandas as pd

V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
OUT_RT, OUT_SUM = sys.argv[1], sys.argv[2]


def clean_mestre():
    """sha256 of the clean published-accession Mestre proteins (header not tagged |rescued)."""
    out = {}
    for f in sorted(glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta")):
        lines = open(f).read().split("\n")
        if "|rescued" in lines[0]:
            continue
        seq = "".join(l.strip() for l in lines[1:]).rstrip("*").upper()
        out.setdefault(hashlib.sha256(seq.encode()).hexdigest(), []).append(f.split("/")[-2])
    return out


t = pd.read_parquet(f"{V7}/rt_tool_calls_v1.parquet",
                    columns=["record_key", "rt_seq_hash", "file_label", "by_myRT", "by_PADLOC", "by_DefenseFinder"])
pairs = pd.read_parquet(f"{V7}/rt_ncrna_pairs_v1.parquet", columns=["record_key", "canonical", "geometry_eligible"])
nc_keys = set(pairs.loc[pairs.canonical & pairs.geometry_eligible, "record_key"])
t["NC"] = t.record_key.isin(nc_keys)
t["n_sys"] = t.by_DefenseFinder.astype(int) + t.by_PADLOC.astype(int) + t.NC.astype(int)
ret = t.file_label == "Retron"
t["rec_tier"] = "X"
t.loc[ret & (t.n_sys >= 2), "rec_tier"] = "A"
t.loc[ret & (t.n_sys == 1), "rec_tier"] = "B1"
t.loc[ret & (t.n_sys == 0), "rec_tier"] = "B0"
t.loc[(t.file_label == "MULTI"), "rec_tier"] = "M"
t.loc[~ret & (t.file_label != "MULTI") & (t.by_DefenseFinder | t.by_PADLOC), "rec_tier"] = "D"
t["A_needs_NC"] = ret & (t.n_sys >= 2) & t.NC  # sensitivity: A with the ncRNA line present

rank = {"A": 0, "B1": 1, "B0": 2, "M": 3, "D": 4, "X": 5}
g = t.groupby("rt_seq_hash")
rt = pd.DataFrame({
    "n_records": g.size(),
    "n_rec_A": g.rec_tier.apply(lambda s: (s == "A").sum()),
    "n_rec_B1": g.rec_tier.apply(lambda s: (s == "B1").sum()),
    "n_rec_B0": g.rec_tier.apply(lambda s: (s == "B0").sum()),
    "any_A_with_NC": g.A_needs_NC.any(),
    "any_DF": g.by_DefenseFinder.any(), "any_PAD": g.by_PADLOC.any(), "any_NC": g.NC.any(),
    "labels": g.file_label.apply(lambda s: "|".join(sorted(set(s)))),
    "best": g.rec_tier.apply(lambda s: min(s, key=rank.get)),
})
ex = pd.read_parquet(f"{V7}/rt_exact_v1.parquet",
                     columns=["rt_seq_hash", "rt_aa_len", "n_genomes", "n_loci", "wellformed", "any_multilabel", "family_label_set"]).set_index("rt_seq_hash")
el = pd.read_csv(f"{V7}/rt07_g5a/g5a_eligibility_partition.tsv.gz", sep="\t").set_index("rt_seq_hash")
rt = rt.join(ex).join(el[["eligible", "ineligibility_reason"]])
fam = rt.family_label_set.astype(str)
has_ret = fam.str.contains("Retron")
mixed = has_ret & (rt.labels.str.contains(r"\|") | rt.any_multilabel.fillna(False).astype(bool))
rt["stratum"] = rt.best
rt.loc[mixed & rt.best.isin(["A", "B1", "B0", "M"]), "stratum"] = "M"
ref = clean_mestre()
rt["REF_MESTRE"] = rt.index.isin(set(ref))
rt.to_csv(OUT_RT, sep="\t", compression="gzip")

rows = []
for s in ["A", "B1", "B0", "M", "D", "X"]:
    sub = rt[rt.stratum == s]
    rows.append([s, len(sub), int(sub.n_records.sum()), int(sub.eligible.fillna(False).sum()),
                 int(sub.REF_MESTRE.sum()), int(sub.any_A_with_NC.sum()),
                 int(sub.rt_aa_len.median()) if len(sub) else "", int((sub.rt_aa_len < 250).sum())])
with open(OUT_SUM, "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["stratum", "exact_RTs", "RT_anchored_records", "g5a_eligible_exact_RTs", "identical_to_clean_Mestre_protein",
                "has_A_record_with_ncRNA_line", "median_aa_len", "exact_RTs_lt_250aa"])
    w.writerows(rows)
    w.writerow(["TOTAL", len(rt), int(rt.n_records.sum()), int(rt.eligible.fillna(False).sum()), int(rt.REF_MESTRE.sum()), "", "", ""])
    w.writerow(["clean_Mestre_distinct_sequences", len(ref), sum(len(v) for v in ref.values()), "", "", "", "", ""])
print(open(OUT_SUM).read())
