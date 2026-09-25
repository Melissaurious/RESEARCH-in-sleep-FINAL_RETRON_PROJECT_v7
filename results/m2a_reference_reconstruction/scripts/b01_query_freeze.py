#!/usr/bin/env python3
"""M2b — freeze the modern retron / retron-like query-population table (all 501,561 exact RTs).

Strata are taken from the M1 census (m04, rules declared before it ran): A, B1, B0, M, D, X.
Only A/B1/B0/M/D are extracted. X is NOT_QUERY: it is a control source and never a target.
Extraction is MCC-v3.1 in modern mode, so every Toro template is eligible (mcc_v3.extract,
which reproduces the frozen historical output exactly).
Inclusion (primary universe = A ∪ B1 ∪ B0; M and D are separate strata):
  INCLUDED                      MCC-v3.1 EXTRACTED and extract length <= 2 x the historical
                                median (2 x 229 = 458 aa)
  CORE_LENGTH_OUTLIER           extracted but longer than 458 aa (flagged, not primary)
  UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY:<reason>
  NOT_QUERY                     stratum X
Carried identifiers (never used to place): evidence lines, ncRNA CM models, family/type
label sets, n_genomes, and g5a eligibility.
"""
import hashlib, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcc_v3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived"
CEN = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit/ARIS_OUTPUT/mestre_audit/m2b_census_per_rt.tsv.gz"
OUT = f"{ROOT}/m2b"; os.makedirs(OUT, exist_ok=True)
HIST_MEDIAN = 229

cen = pd.read_csv(CEN, sep="\t", index_col=0)
q_ids = set(cen.index[cen.stratum.isin(["A", "B1", "B0", "M", "D"])])
ex = pd.read_parquet(f"{V7}/rt_exact_v1.parquet", columns=["rt_seq_hash", "rt_seq", "n_genomes", "family_label_set", "type_set_norm_set"])
ex = ex.set_index("rt_seq_hash")
seqs = {h: ex.at[h, "rt_seq"].upper().rstrip("*") for h in q_ids}
res = mcc_v3.extract(seqs, f"{ROOT}/work_m2b", leave_near_self=False, threads=16)

pairs = pd.read_parquet(f"{V7}/rt_ncrna_pairs_v1.parquet", columns=["rt_seq_hash", "canonical", "geometry_eligible", "detection_model"])
pc = pairs[pairs.canonical & pairs.geometry_eligible].groupby("rt_seq_hash").agg(
    n_canonical_ncrna_pairs=("detection_model", "size"), ncrna_cm_models=("detection_model", lambda s: "|".join(sorted(set(s)))))

T = cen[["stratum", "n_records", "n_rec_A", "n_rec_B1", "n_rec_B0", "any_DF", "any_PAD", "any_NC", "any_A_with_NC", "labels",
         "rt_aa_len", "n_genomes", "family_label_set", "eligible", "ineligibility_reason", "REF_MESTRE"]].copy()
T = T.join(pc).join(ex[["type_set_norm_set"]])
T["n_canonical_ncrna_pairs"] = T.n_canonical_ncrna_pairs.fillna(0).astype(int)
cols = ["status", "reason", "template", "template_identity", "template_coverage", "start", "end", "unc_start", "unc_end",
        "n_tied", "n_concordant", "discordant", "mcc_v2_status", "mcc_v2_core_start", "mcc_v2_core_end", "mcc_v2_core_inside"]
R = pd.DataFrame.from_dict({h: {c: r.get(c, "") for c in cols} for h, r in res.items()}, orient="index").add_prefix("mcc_v3_")
T = T.join(R)
T["nonstd_frac"] = [sum(c not in "ACDEFGHIKLMNPQRSTVWY" for c in seqs[h]) / len(seqs[h]) if h in seqs else "" for h in T.index]
T["extract_len"] = [(int(r.mcc_v3_end) - int(r.mcc_v3_start) + 1) if r.mcc_v3_status == "EXTRACTED" else "" for r in T.itertuples()]


def incl(r):
    if r.stratum == "X":
        return "NOT_QUERY"
    if r.mcc_v3_status != "EXTRACTED":
        return f"UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY:{r.mcc_v3_reason}"
    return "CORE_LENGTH_OUTLIER" if r.extract_len > 2 * HIST_MEDIAN else "INCLUDED"


T["inclusion"] = [incl(r) for r in T.itertuples()]
T.index.name = "rt_seq_hash"
p = f"{OUT}/M2B_QUERY_FREEZE.tsv.gz"
T.to_csv(p, sep="\t", compression="gzip")
with open(f"{OUT}/M2B_extracts.faa", "w") as fh:
    for h, r in res.items():
        if r["status"] == "EXTRACTED":
            fh.write(f">{h}\n{r['seq']}\n")
S = T.groupby(["stratum", "inclusion"]).size().unstack(fill_value=0)
S["total"] = S.sum(1)
S.to_csv(f"{OUT}/M2B_inclusion_by_stratum.tsv", sep="\t")
sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
open(f"{OUT}/M2B_QUERY_FREEZE.sha256", "w").write(f"{sha}  M2B_QUERY_FREEZE.tsv.gz\n")
print(S.to_string()); print("rows", len(T), "sha256", sha)
