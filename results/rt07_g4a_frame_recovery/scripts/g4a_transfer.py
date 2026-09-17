#!/usr/bin/env python3
"""g4a — transfer of de novo family profiles to held-out CHALLENGE sequences.

The first pass reported only a detection rate at `hmmsearch --max -E 10`. That is a
near-ceiling setting: essentially every RT is detected by essentially every RT profile,
so the rate cannot discriminate and is close to uninformative. It is retained here for
completeness and explicitly flagged, but the reported quantity is CONTINUOUS: the
distribution of per-sequence best bit scores, self versus cross.

No threshold is tuned. Nothing is re-run at a different E-value to improve a result.

Usage: g4a_transfer.py <workdir> <tabledir>
"""
import sys, os, subprocess, statistics, math

WORK, TABLES = sys.argv[1], sys.argv[2]
BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
E_REPORT = "10"          # permissive ON PURPOSE, so the score distribution is not truncated

rows = []
for a in FAMILIES:
    for b in FAMILIES:
        fp = f"{WORK}/{b}.challenge.faa"
        if not os.path.exists(fp):
            continue
        n_ch = sum(1 for l in open(fp) if l.startswith(">"))
        tbl = f"{WORK}/tr_{a}_on_{b}.tbl"
        subprocess.run([BIN + "hmmsearch", "--max", "-E", E_REPORT, "--noali",
                        "--tblout", tbl, f"{WORK}/{a}.deriv.hmm", fp],
                       capture_output=True, text=True, check=True)
        best = {}
        for line in open(tbl):
            if line.startswith("#"):
                continue
            p = line.split()
            sid, ev, sc = p[0], float(p[4]), float(p[5])
            if sid not in best or sc > best[sid][1]:
                best[sid] = (ev, sc)
        sc = [v[1] for v in best.values()]
        ev = [v[0] for v in best.values()]
        if sc:
            rows.append([a, b, "SELF" if a == b else "CROSS", str(n_ch), str(len(sc)),
                         f"{100*len(sc)/n_ch:.1f}",
                         f"{statistics.median(sc):.1f}", f"{min(sc):.1f}", f"{max(sc):.1f}",
                         f"{statistics.median([-math.log10(x) if x > 0 else 300 for x in ev]):.1f}"])
        else:
            rows.append([a, b, "SELF" if a == b else "CROSS", str(n_ch), "0", "0.0",
                         "", "", "", ""])

with open(f"{TABLES}/g4a_transfer_to_challenge.tsv", "w") as f:
    f.write("profile_family\tchallenge_family\tdirection\tn_challenge\tn_detected\t"
            "pct_detected_NON_DISCRIMINATING\tmedian_best_bitscore\tmin_best_bitscore\t"
            "max_best_bitscore\tmedian_neg_log10_evalue\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

self_sc = [float(r[6]) for r in rows if r[2] == "SELF" and r[6]]
cross_sc = [float(r[6]) for r in rows if r[2] == "CROSS" and r[6]]
print(f"SELF  median-of-median bitscore: {statistics.median(self_sc):.1f}  (n={len(self_sc)})")
print(f"CROSS median-of-median bitscore: {statistics.median(cross_sc):.1f}  (n={len(cross_sc)})")
print(f"ratio self/cross: {statistics.median(self_sc)/statistics.median(cross_sc):.2f}x")
print("detection rate at --max -E 10 is near-ceiling and is flagged as NON_DISCRIMINATING")
