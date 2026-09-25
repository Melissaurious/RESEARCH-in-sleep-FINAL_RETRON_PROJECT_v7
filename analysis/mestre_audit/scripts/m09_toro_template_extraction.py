#!/usr/bin/env python3
"""Toro-template extraction (TTE) — a label-independent alternative to MCC-v2, compared on
source-stated ground truth. Rules were written before the first run.

TEMPLATES: the 102 Toro 2014 extracts whose Table S1 'RT phylogeny' is Retrons. They predate
Mestre 2020 and were chosen by Toro, not by us; no Mestre clade label is used.

RULE, per query protein P:
  1. MMseqs2 search: P (query) against the 102 retron extracts (targets), -s 7.5, e <= 1e-5.
  2. Drop templates with identity >= 0.90 to P. This is a leave-near-self-out rule, so the
     76 proteins that carry a Toro extract are not scored against themselves.
  3. Keep hits whose alignment covers >= 0.80 of the template extract; take the best by bitscore.
  4. Transferred interval on P = [qstart - (tstart - 1), qend + (tlen - tend)], clipped to P.
  Status: TTE_EXTRACTED or TTE_NO_TEMPLATE.

GROUND TRUTH: for the 76 clean Mestre proteins that contain a Toro retron extract
(identity >= 0.95, coverage >= 0.95; m08), the source-stated RT0-RT7 interval.
Reported for both TTE and MCC-v2: |start delta|, |end delta| <= 5 aa, and extraction rate.
Also reported: TTE coverage on all 1,814 clean proteins and on the 15 RNA-polymerase
substitutes (expected: no template).
"""
import csv, glob, os, subprocess, sys
import pandas as pd

ENV = "/home/borg/miniconda3/envs/retron_tradicional/bin"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
X = "analysis/mestre_audit/m2_design/toro_crosswalk"
MCC2 = "analysis/mestre_audit/m2_design/mcc_v2/MCC_FEASIBILITY_per_sequence.tsv"
RNAP = "analysis/mestre_audit/subaudits/v2_v3_v5/v235_rnap_substitutes.tsv"
TORO = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/historical/toro_2014_Rt0-Rt7.FASTA"
WORK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(WORK, exist_ok=True)

t14 = pd.read_csv(f"{X}/TORO2014_FASTA_x_TABLES1.tsv", sep="\t")
ret_idx = set(t14.loc[t14.s1_rt_phylogeny == "Retrons", "fasta_index"])
seqs, name = [], None
for line in open(TORO, encoding="utf-8", errors="replace"):
    if line.startswith(">"):
        seqs.append([line, ""])
    else:
        seqs[-1][1] += line.strip()
tf = f"{WORK}/toro_retron_templates.faa"
with open(tf, "w") as fh:
    for i, (h, s) in enumerate(seqs, 1):
        if i in ret_idx:
            fh.write(f">T{i}\n{s.replace('-', '').replace('.', '').upper()}\n")
rnap = {r["terminal"] for r in csv.DictReader(open(RNAP), delimiter="\t")}
qf, qset, qlen = f"{WORK}/queries.faa", {}, {}
with open(qf, "w") as fh:
    for f in sorted(glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta")):
        t = f.split("/")[-2]; L = open(f).read().split("\n")
        s = "".join(x.strip() for x in L[1:]).rstrip("*").upper()
        qset[t] = "RNAP_SUBSTITUTE" if t in rnap else ("OTHER_SUBSTITUTE" if "|rescued" in L[0] else "CLEAN")
        qlen[t] = len(s)
        fh.write(f">{t}\n{s}\n")
m8 = f"{WORK}/q_vs_toro_retrons.m8"
subprocess.run([f"{ENV}/mmseqs", "easy-search", qf, tf, m8, f"{WORK}/tmp", "--threads", "8", "-s", "7.5", "-e", "1e-5",
                "--max-seqs", "200", "--format-output", "query,target,fident,qstart,qend,qlen,tstart,tend,tlen,bits"],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
best = {}
for line in open(m8):
    q, t, fi, qs, qe, ql, ts, te, tl, b = line.rstrip("\n").split("\t")
    fi, qs, qe, ql, ts, te, tl, b = float(fi), int(qs), int(qe), int(ql), int(ts), int(te), int(tl), float(b)
    if fi >= 0.90 or (te - ts + 1) / tl < 0.80:
        continue
    if q not in best or b > best[q]["bits"]:
        best[q] = dict(template=t, fident=fi, bits=b, start=max(1, qs - (ts - 1)), end=min(ql, qe + (tl - te)))

gt = pd.read_csv(f"{X}/TORO2014_x_MESTRE2020_CROSSWALK.tsv", sep="\t")
gt = gt[gt.mapped].sort_values("fident", ascending=False).drop_duplicates("mestre_terminal").set_index("mestre_terminal")
mcc = pd.read_csv(MCC2, sep="\t").set_index("terminal")
rows = []
for t in sorted(qset, key=lambda x: int(x.split("_")[1])):
    b = best.get(t)
    m = mcc.loc[t] if t in mcc.index else None
    mok = m is not None and str(m.status).startswith("EXTRACTABLE")
    g = gt.loc[t] if t in gt.index else None
    rows.append(dict(terminal=t, set=qset[t], protein_len=qlen[t],
                     tte_status="TTE_EXTRACTED" if b else "TTE_NO_TEMPLATE", tte_template=b["template"] if b else "",
                     tte_template_identity=b["fident"] if b else "", tte_start=b["start"] if b else "", tte_end=b["end"] if b else "",
                     mcc2_status=m.status if m is not None else "", mcc2_start=m.mcc_start if mok else "", mcc2_end=m.mcc_end if mok else "",
                     mcc2_core_start=m.core_start_route1 if mok else "", mcc2_core_end=m.core_end_route1 if mok else "",
                     toro_stated_start=g.toro_stated_start if g is not None else "", toro_stated_end=g.toro_stated_end if g is not None else ""))
R = pd.DataFrame(rows)
os.makedirs(OUT, exist_ok=True)
R.to_csv(f"{OUT}/TTE_vs_MCC2_per_sequence.tsv", sep="\t", index=False)


def agree(df, s, e):
    d = df[(df[s] != "") & (df.toro_stated_start != "")]
    ds = (d[s].astype(float) - d.toro_stated_start.astype(float)).abs()
    de = (d[e].astype(float) - d.toro_stated_end.astype(float)).abs()
    return len(d), (ds <= 5).mean(), (de <= 5).mean(), ds.median(), de.median()


gtR = R[R.toro_stated_start != ""]
lines = [("ground-truth proteins (Toro-stated interval)", len(gtR))]
for lab, s, e, st in [("TTE interval", "tte_start", "tte_end", "tte_status"),
                      ("MCC-v2 window", "mcc2_start", "mcc2_end", "mcc2_status"),
                      ("MCC-v2 required core", "mcc2_core_start", "mcc2_core_end", "mcc2_status")]:
    n, fs, fe, ms, me = agree(gtR, s, e)
    lines.append((f"{lab}: extracted / compared", f"{n} / {len(gtR)}"))
    lines.append((f"{lab}: start within 5 aa / end within 5 aa", f"{fs:.3f} / {fe:.3f}"))
    lines.append((f"{lab}: median |d start| / |d end|", f"{ms} / {me}"))
for s in ["CLEAN", "OTHER_SUBSTITUTE", "RNAP_SUBSTITUTE"]:
    sub = R[R.set == s]
    lines.append((f"{s}: TTE extracted", f"{(sub.tte_status == 'TTE_EXTRACTED').sum()} / {len(sub)}"))
    lines.append((f"{s}: MCC-v2 extractable", f"{sub.mcc2_status.astype(str).str.startswith('EXTRACTABLE').sum()} / {len(sub)}"))
c = R[R.set == "CLEAN"]
both = c[(c.tte_status == "TTE_EXTRACTED") & c.mcc2_status.astype(str).str.startswith("EXTRACTABLE")]
lines.append(("CLEAN: extracted by both", len(both)))
lines.append(("CLEAN: TTE only / MCC-v2 only / neither",
              f"{((c.tte_status == 'TTE_EXTRACTED') & ~c.mcc2_status.astype(str).str.startswith('EXTRACTABLE')).sum()} / "
              f"{((c.tte_status != 'TTE_EXTRACTED') & c.mcc2_status.astype(str).str.startswith('EXTRACTABLE')).sum()} / "
              f"{((c.tte_status != 'TTE_EXTRACTED') & ~c.mcc2_status.astype(str).str.startswith('EXTRACTABLE')).sum()}"))
dd = both.copy()
lines.append(("CLEAN both: TTE start - MCC-v2 core start (median)", (dd.tte_start.astype(float) - dd.mcc2_core_start.astype(float)).median()))
lines.append(("CLEAN both: TTE end - MCC-v2 core end (median)", (dd.tte_end.astype(float) - dd.mcc2_core_end.astype(float)).median()))
lines.append(("CLEAN both: TTE contains MCC-v2 required core (frac)",
              ((dd.tte_start.astype(float) <= dd.mcc2_core_start.astype(float)) & (dd.tte_end.astype(float) >= dd.mcc2_core_end.astype(float))).mean().round(4)))
te = c[c.tte_status == "TTE_EXTRACTED"]
lines.append(("CLEAN TTE: extracted length median", (te.tte_end.astype(float) - te.tte_start.astype(float) + 1).median()))
with open(f"{OUT}/TTE_vs_MCC2_SUMMARY.tsv", "w") as fh:
    for k, v in lines:
        fh.write(f"{k}\t{v}\n")
print(open(f"{OUT}/TTE_vs_MCC2_SUMMARY.tsv").read())
