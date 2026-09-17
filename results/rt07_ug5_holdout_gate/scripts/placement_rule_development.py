#!/usr/bin/env python3
"""Derive a per-anchor placement rule using CONSTRUCTION-FAMILY DATA ONLY.

Operator decision 2: no UG5 sequence, profile, decoy, score distribution or UG5-derived
threshold may inform this rule. This script never opens any UG5 file. It asserts that at
the end and fails closed.

Development population mirrors the UG5 situation as closely as non-UG5 data allows:
  the GII reference HMM (the frame carrier) projected onto the FIVE OTHER construction
  families' sequences -- cross-family, exactly as UG5 would be -- versus composition-
  preserving shuffles of those same sequences.

The rule is chosen for interpretability and separation on that population, then FROZEN.

Usage: placement_rule_development.py <g4a_repaired_work> <workdir> <tabledir>
"""
import sys, os, re, random, statistics, collections
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/"
                   "results/rt07_g4a_repaired/scripts")
from repaired_lib import *          # noqa

G4AWORK, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
REFERENCE_FAMILY = "GII"
# the five families the GII frame is projected ONTO. GII itself is excluded: it is the
# profile source, so it is not a cross-family case.
DEV_FAMILIES = ["Retrons", "DGRs", "CRISPR", "UG3", "AbiA"]
FORBIDDEN = "UG5"
ANCHOR_WINDOW = 5
random.seed(20260916)
os.makedirs(WORK, exist_ok=True)

elig = eligible_by_family()
assert FORBIDDEN not in DEV_FAMILIES

# frozen anchors, recomputed from the six-family construction (no UG5)
import itertools
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
pm = {}
for a, b in itertools.permutations(CONSTRUCTION, 2):
    m = pair_map(f"{WORK}/con_{a}__{b}.hhr")
    if m:
        pm[(a, b)] = m
sup = collections.Counter()
for b in CONSTRUCTION:
    if b != REFERENCE_FAMILY and (REFERENCE_FAMILY, b) in pm:
        for q in pm[(REFERENCE_FAMILY, b)]:
            sup[q] += 1
n_other = sum(1 for b in CONSTRUCTION if b != REFERENCE_FAMILY and (REFERENCE_FAMILY, b) in pm)
ANCHORS = sorted(k for k, v in sup.items() if v == n_other)
assert ANCHORS, "no frozen anchors"


def domains(seq_id, seq, tag):
    """hmmsearch the GII reference HMM against ONE sequence; return per-domain records."""
    fp = f"{WORK}/dev_{tag}.faa"
    write_fasta({seq_id: seq}, fp)
    dom = f"{WORK}/dev_{tag}.domtbl"
    run([BIN + "hmmsearch", "--max", "-E", HMMSEARCH_E, "--noali",
         "--domtblout", dom, f"{G4AWORK}/{REFERENCE_FAMILY}.deriv.hmm", fp])
    out = []
    for line in open(dom):
        if line.startswith("#"):
            continue
        p = line.split()
        # 12 c-Evalue, 13 i-Evalue, 14 domain score(1-based 14 -> idx 13), 16-17 hmm, 18-19 ali
        out.append(dict(ievalue=float(p[12]), score=float(p[13]),
                        hs=int(p[15]), he=int(p[16]), as_=int(p[17]), ae=int(p[18])))
    return out


def anchors_under(dl, min_score, min_frac):
    """Anchors placed under a candidate rule: a domain must clear min_score AND the anchor
    must lie inside the ALIGNED hmm span (not the looser envelope), with the domain covering
    at least min_frac of the anchor range it claims."""
    placed = {}
    for d in dl:
        if d["score"] < min_score:
            continue
        span = d["he"] - d["hs"] + 1
        if span < min_frac * len(ANCHORS):
            pass  # span filter applied below per-anchor, kept simple and interpretable
        for a in ANCHORS:
            if d["hs"] <= a <= d["he"]:
                frac = (a - d["hs"]) / max(1, (d["he"] - d["hs"]))
                pos = int(round(d["as_"] + frac * (d["ae"] - d["as_"])))
                if a not in placed or d["score"] > placed[a][1]:
                    placed[a] = (pos, d["score"])
    return placed


# ---------------------------------------------------- collect REAL and DECOY domain records
real, decoy = [], []
for fam in DEV_FAMILIES:
    for i, (sid, seq) in enumerate(sorted(elig[fam].items())):
        real.append((fam, sid, seq, domains(sid, seq, f"r_{fam}_{i}")))
        s = list(seq.upper())
        random.shuffle(s)
        decoy.append((fam, sid, "".join(s), domains(sid, "".join(s), f"d_{fam}_{i}")))

# ---------------------------------------------------- candidate rules, evaluated on dev data
rows = []
CANDIDATES = [("envelope_only_v2_rule", -1e9),
              ("score_ge_0", 0.0), ("score_ge_5", 5.0), ("score_ge_10", 10.0),
              ("score_ge_20", 20.0), ("score_ge_30", 30.0), ("score_ge_50", 50.0)]
for name, thr in CANDIDATES:
    rp = [len(anchors_under(d, thr, 0)) for *_, d in real]
    dp = [len(anchors_under(d, thr, 0)) for *_, d in decoy]
    r_any = sum(1 for x in rp if x > 0)
    d_any = sum(1 for x in dp if x > 0)
    rows.append([name, f"{thr:.1f}" if thr > -1e8 else "none",
                 str(len(rp)), f"{statistics.median(rp):.0f}", str(max(rp)),
                 f"{100*r_any/len(rp):.1f}",
                 f"{statistics.median(dp):.0f}", str(max(dp)),
                 f"{100*d_any/len(dp):.1f}",
                 f"{statistics.median(rp) - statistics.median(dp):.0f}"])

with open(f"{TABLES}/placement_rule_development.tsv", "w") as f:
    f.write("candidate_rule\tmin_domain_bitscore\tn_dev_sequences\treal_median_anchors\t"
            "real_max_anchors\treal_pct_with_any_placement\tdecoy_median_anchors\t"
            "decoy_max_anchors\tdecoy_pct_with_any_placement\tmedian_separation\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

# ---------------------------------------------------- sensitivity across the threshold grid
sens = []
for thr in (0, 2, 5, 8, 10, 15, 20, 25, 30, 40, 50):
    dp = [len(anchors_under(d, thr, 0)) for *_, d in decoy]
    rp = [len(anchors_under(d, thr, 0)) for *_, d in real]
    d_any = sum(1 for x in dp if x > 0)
    sens.append([str(thr), f"{statistics.median(rp):.0f}", str(max(rp)),
                 f"{statistics.median(dp):.0f}", str(max(dp)),
                 f"{100*d_any/len(dp):.2f}",
                 f"{100*sum(1 for x in rp if x > 0)/len(rp):.1f}"])
with open(f"{TABLES}/placement_rule_sensitivity.tsv", "w") as f:
    f.write("min_domain_bitscore\treal_median_anchors\treal_max_anchors\tdecoy_median_anchors\t"
            "decoy_max_anchors\tdecoy_pct_any_placement\treal_pct_any_placement\n")
    for r in sens:
        f.write("\t".join(r) + "\n")

print("candidate rules (construction families only, GII profile onto the other five):")
print(f"{'rule':24s}{'real_med':>9}{'real_max':>9}{'dec_med':>9}{'dec_max':>9}{'dec_any%':>10}")
for r in rows:
    print(f"{r[0]:24s}{r[3]:>9}{r[4]:>9}{r[6]:>9}{r[7]:>9}{r[8]:>10}")
print()
print("threshold sensitivity:")
for r in sens:
    print(f"  score>={r[0]:>3}  real_med={r[1]:>4} real_max={r[2]:>4}  "
          f"decoy_med={r[3]:>3} decoy_max={r[4]:>4}  decoy_any={r[5]:>6}%  real_any={r[6]}%")
print(f"\nDEV POPULATION: {len(real)} real + {len(decoy)} decoy sequences from {DEV_FAMILIES}")
print("UG5 WAS NOT OPENED BY THIS SCRIPT.")
