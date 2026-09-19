#!/usr/bin/env python3
"""M2a — calibrate the placement-status thresholds on replicates 1-5, evaluate on 6-10.

usage: a04_calibrate_evaluate.py <extractor>

STATUS RULE (declared before any evaluation replicate was read):
  UNABLE_TO_ALIGN_OR_PLACE_RELIABLY  unplaced, or < 50 % of the query's residues survive the
                                     keeplength alignment into reference columns
  CONFIDENTLY_PLACED                 best label is a historical clade, its summed LWR >= tau_LWR,
                                     EDPL <= tau_EDPL and pendant <= tau_pend[clade]
  OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE
                                     summed LWR >= tau_LWR and EDPL <= tau_EDPL, but the best
                                     label is NONE (a backbone edge), or pendant > tau_pend[clade]
  AMBIGUOUS                          everything else (low LWR, high EDPL, the clade-10/11 grade)
CALIBRATION (reps 1-5 of the PRIMARY blocked design only):
  tau_LWR     smallest grid value >= 0.80 at which <= 1 % of shuffled queries have a
              clade-labelled best label with LWR >= the value (grid 0.80, 0.85, 0.90, 0.95, 0.99)
  tau_EDPL    95th percentile of EDPL among correctly labelled real calibration queries
  tau_pend[c] 95th percentile of pendant length among correctly labelled real calibration
              queries of clade c; clades with < 5 such queries use the pooled value
EVALUATION: reps 6-10 of the blocked design (PRIMARY), and every rep of the random design
(SECONDARY), with the frozen taus. K2 counts clades 1-9 and 11; clade 10 and the Orphan are
reported separately. Clades are never pooled in the per-clade table.
"""
import glob, json, os, sys
from collections import defaultdict
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ext = sys.argv[1]
CLADES = [str(i) for i in range(1, 12)] + ["Orphan"]


def load(design, reps):
    out = []
    for r in reps:
        W = f"{ROOT}/val/{ext}_{design}_r{r:02d}"
        p = f"{W}/placements.tsv"
        if not os.path.exists(p):
            continue
        d = pd.read_csv(p, sep="\t", dtype={"true_clade_EVALUATION": str, "best_label": str, "best_edge_label": str})
        qa = {}
        name = None
        for l in open(f"{W}/query_aln.afa"):
            if l.startswith(">"):
                name = l[1:].strip(); qa[name] = 0
            else:
                qa[name] += sum(c not in "-." for c in l.strip())
        raw = {}
        for l in open(f"{W}/queries.faa"):
            if l.startswith(">"):
                name = l[1:].strip(); raw[name] = 0
            else:
                raw[name] += len(l.strip())
        d["aligned_frac"] = d["query"].map(lambda q: qa.get(q, 0) / max(1, raw.get(q, 1)))
        out.append(d)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def status(r, tau):
    if r.best_label == "UNPLACED" or r.aligned_frac < 0.5:
        return "UNABLE_TO_ALIGN_OR_PLACE_RELIABLY"
    lwr_ok = r.best_label_lwr >= tau["LWR"] and (pd.isna(r.edpl) or r.edpl == "" or float(r.edpl) <= tau["EDPL"])
    if not lwr_ok:
        return "AMBIGUOUS"
    if r.best_label == "NONE":
        return "OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE"
    if r.best_label not in CLADES:
        return "AMBIGUOUS"
    if r.pendant > tau["pend"].get(r.best_label, tau["pend_pooled"]):
        return "OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE"
    return "CONFIDENTLY_PLACED"


cal = load("blocked", range(1, 6))
real, shuf = cal[~cal.shuffled], cal[cal.shuffled]
tau_lwr, grid = None, [0.80, 0.85, 0.90, 0.95, 0.99]
shuf_rates = {}
for g in grid:
    rate = ((shuf.best_label.isin(CLADES)) & (shuf.best_label_lwr >= g)).mean()
    shuf_rates[g] = round(float(rate), 4)
    if tau_lwr is None and rate <= 0.01:
        tau_lwr = g
flag = tau_lwr is None
tau_lwr = tau_lwr or 0.99
corr = real[real.best_label == real.true_clade_EVALUATION]
tau_edpl = float(pd.to_numeric(corr.edpl, errors="coerce").quantile(0.95))
pooled = float(corr.pendant.quantile(0.95))
pend = {c: float(g.pendant.quantile(0.95)) for c, g in corr.groupby("true_clade_EVALUATION") if len(g) >= 5}
tau = dict(LWR=tau_lwr, LWR_grid_shuffled_confident_rate=shuf_rates, LWR_no_grid_value_met=flag, EDPL=tau_edpl,
           pend=pend, pend_pooled=pooled, n_calibration_real=len(real), n_calibration_correct=len(corr))
os.makedirs(f"{ROOT}/eval", exist_ok=True)
json.dump(tau, open(f"{ROOT}/eval/{ext}_tau_FROZEN.json", "w"), indent=1)

refst = pd.read_csv(f"{ROOT}/ref/{ext}_tip_status.tsv", sep="\t", dtype={"clade_EVALUATION_ONLY": str})
refst = refst[refst.status == "IN_REFERENCE"]
grp = {}
for l in open(f"{ROOT}/groups2/{ext}_c85_cluster.tsv"):
    a, b = l.split(); grp[b] = a
refst["group"] = refst.taxon.map(grp)
summary = {}
for design, reps in (("blocked", range(6, 11)), ("random", range(1, 11))):
    ev = load(design, reps)
    if ev.empty:
        continue
    ev["status"] = ev.apply(lambda r: status(r, tau), axis=1)
    ev["correct"] = ev.best_label == ev.true_clade_EVALUATION
    ev.to_csv(f"{ROOT}/eval/{ext}_{design}_evaluation_rows.tsv", sep="\t", index=False)
    R = ev[~ev.shuffled]
    rows = []
    for c in CLADES:
        g = R[R.true_clade_EVALUATION == c]
        rs = refst[refst.clade_EVALUATION_ONLY == c]
        conf = g.status == "CONFIDENTLY_PLACED"
        rows.append(dict(clade=c, reference_sequences=len(rs), independent_85pct_groups=rs.group.nunique(),
                         withheld_placements=len(g), confident_correct=int((conf & g.correct).sum()),
                         confident_wrong=int((conf & ~g.correct).sum()), ambiguous=int((g.status == "AMBIGUOUS").sum()),
                         outside=int((g.status == "OUTSIDE_WELL_SUPPORTED_HISTORICAL_CLADE_SPACE").sum()),
                         unable=int((g.status == "UNABLE_TO_ALIGN_OR_PLACE_RELIABLY").sum()),
                         confident_correct_rate=round(float((conf & g.correct).mean()), 4) if len(g) else "",
                         underpowered=rs.group.nunique() < 5))
    T = pd.DataFrame(rows)
    T.to_csv(f"{ROOT}/eval/{ext}_{design}_per_clade.tsv", sep="\t", index=False)
    k2 = R[R.true_clade_EVALUATION.isin([str(i) for i in range(1, 10)] + ["11"])]
    cc = ((k2.status == "CONFIDENTLY_PLACED") & k2.correct).mean()
    cw = ((k2.status == "CONFIDENTLY_PLACED") & ~k2.correct).mean()
    S = ev[ev.shuffled]
    sc = (S.status == "CONFIDENTLY_PLACED").mean()
    summary[design] = dict(reps=list(reps), n_real=len(R), K2_n=len(k2), K2_confident_correct=round(float(cc), 4),
                           K2_confident_wrong=round(float(cw), 4), K2_pass=bool(cc >= 0.80 and cw <= 0.02),
                           shuffled_n=len(S), shuffled_confident=round(float(sc), 4), shuffled_pass=bool(sc <= 0.01),
                           status_counts=R.status.value_counts().to_dict())
json.dump(dict(tau=tau, summary=summary), open(f"{ROOT}/eval/{ext}_SUMMARY.json", "w"), indent=1)
print(json.dumps(dict(tau={k: v for k, v in tau.items() if k != "pend"}, summary=summary), indent=1))
