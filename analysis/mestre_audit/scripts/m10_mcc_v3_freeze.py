#!/usr/bin/env python3
"""MCC-v3 — freeze the historical-core extractor, then apply and validate it.

MCC-v3 projects the historical core interval from the closest eligible Toro 2014 retron
RT0-RT7 template. The Toro 2014 alignment is historical SOURCE MATERIAL; it is not a Mestre
MSA. No Mestre clade label is used in template choice, extraction, alignment or placement.
MCC-v2 stays as a prespecified sensitivity / core-consistency analysis and supplies the
orthogonal >= 70 % core-inside-interval check.

ORDER OF OPERATIONS, and why it is not circular:
  Phase 1 CALIBRATE from the Toro reference set ALONE (102 Table S1 'Retrons' extracts).
          No Mestre sequence and no boundary-accuracy measurement enters phase 1.
  Phase 2 FREEZE params.json + this file's sha256.
  Phase 3 APPLY to the historical proteins.
  Phase 4 VALIDATE against the 76 source-stated boundaries, leave-near-identical-template-out.
          Phase 4 never changes a threshold. It only reports.

FROZEN RULES
  R1 Template eligibility. The 102 Toro 2014 extracts whose Table S1 'RT phylogeny' is
     'Retrons'. Toro 2014 predates the Mestre clade labels. In historical validation only, a
     template with identity >= LEAVE_NEAR_SELF (0.90) to the query is dropped, so a protein is
     never scored against its own source extract. For modern queries every template is
     eligible and the identity is reported.
  R2 Similarity metric. MMseqs2 easy-search, -s 7.5, e-value <= 1e-5, query = protein,
     target = template. identity = MMseqs `fident` over the alignment; template coverage =
     (tend - tstart + 1) / tlen. Both are recorded per sequence.
  R3 Tie handling. Best bitscore wins. Ties within TIE_BITS_FRAC (0.005) of the best are
     resolved by higher template coverage, then by the lexicographically smallest template id,
     so the result is deterministic. The number of tied templates is recorded.
  R4 Minimum acceptable template similarity. MIN_IDENT is calibrated in phase 1 as the 5th
     percentile of the nearest-neighbour identity distribution *within* the Toro retron
     reference set: the similarity at which that reference set still covers itself. Template
     coverage must also be >= MIN_TCOV (0.80, declared in m09 before any result was seen).
  R5 Maximum boundary uncertainty. Among templates scoring >= CONCORD_BITS_FRAC (0.90) of the
     best, the projected starts and ends must agree within MAX_BOUNDARY_UNC, calibrated in
     phase 1 as the 95th percentile of that same concordant-template spread *within* the Toro
     reference set (v3.1; see the correction note in phase 1). Sequences exceeding it are reported as discordant, not forced.
  R6 No acceptable template, or failed QC -> status
     UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY, with a reason:
     NO_HIT | LOW_IDENTITY | LOW_TEMPLATE_COVERAGE | DISCORDANT_TEMPLATES | CORE_QC_FAILED.
     This is an extraction status. It is never evidence that a sequence is not a retron.

PROJECTION. interval = [qstart - (tstart - 1), qend + (tlen - tend)], clipped to the protein.
"""
import csv, glob, hashlib, json, os, subprocess, sys
from collections import defaultdict
import pandas as pd

ENV = "/home/borg/miniconda3/envs/retron_tradicional/bin"
REF = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7"
TORO = f"{REF}/historical/toro_2014_Rt0-Rt7.FASTA"
X = "analysis/mestre_audit/m2_design/toro_crosswalk"
MCC2 = "analysis/mestre_audit/m2_design/mcc_v2/MCC_FEASIBILITY_per_sequence.tsv"
RNAP = "analysis/mestre_audit/subaudits/v2_v3_v5/v235_rnap_substitutes.tsv"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
WORK, OUT = sys.argv[1], sys.argv[2]
LEAVE_NEAR_SELF, MIN_TCOV, TIE_BITS_FRAC, CONCORD_BITS_FRAC = 0.90, 0.80, 0.005, 0.90
os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def search(q, t, out, maxseqs=200):
    run([f"{ENV}/mmseqs", "easy-search", q, t, out, f"{WORK}/tmp_{os.path.basename(out)}", "--threads", "8",
         "-s", "7.5", "-e", "1e-5", "--max-seqs", str(maxseqs),
         "--format-output", "query,target,fident,qstart,qend,qlen,tstart,tend,tlen,bits"])
    rows = defaultdict(list)
    for line in open(out):
        q_, t_, fi, qs, qe, ql, ts, te, tl, b = line.rstrip("\n").split("\t")
        rows[q_].append(dict(template=t_, fident=float(fi), qs=int(qs), qe=int(qe), ql=int(ql),
                             ts=int(ts), te=int(te), tl=int(tl), bits=float(b),
                             tcov=(int(te) - int(ts) + 1) / int(tl),
                             start=max(1, int(qs) - (int(ts) - 1)), end=min(int(ql), int(qe) + (int(tl) - int(te)))))
    return rows


# ---- templates ---------------------------------------------------------------------------
t14 = pd.read_csv(f"{X}/TORO2014_FASTA_x_TABLES1.tsv", sep="\t")
ret = set(t14.loc[t14.s1_rt_phylogeny == "Retrons", "fasta_index"])
recs, name = [], None
for line in open(TORO, encoding="utf-8", errors="replace"):
    if line.startswith(">"):
        recs.append([line, ""])
    else:
        recs[-1][1] += line.strip()
tmpl = {f"T{i}": s.replace("-", "").replace(".", "").upper() for i, (h, s) in enumerate(recs, 1) if i in ret}
tf = f"{WORK}/templates.faa"
open(tf, "w").write("".join(f">{k}\n{v}\n" for k, v in tmpl.items()))

# ---- PHASE 1 · calibrate from the Toro reference set alone -------------------------------
self_hits = search(tf, tf, f"{WORK}/toro_self.m8", maxseqs=len(tmpl))
nn = []
for q, hs in self_hits.items():
    others = [h for h in hs if h["template"] != q and h["tcov"] >= MIN_TCOV]
    if others:
        nn.append(max(others, key=lambda h: h["bits"])["fident"])
nn_s = pd.Series(nn)
MIN_IDENT = round(float(nn_s.quantile(0.05)), 4)
# v3.1 SPEC CORRECTION (2026-09-19). Found AFTER the first application (v3.0), whose outputs
# are kept in mcc_v3/superseded_v3.0/. v3.0 calibrated R5 on the best template's deviation
# from truth but APPLIED R5 to the spread among concordant templates, which is a different
# quantity. v3.1 calibrates exactly the applied quantity: per Toro query (self excluded;
# MIN_TCOV and MIN_IDENT applied), the maximum |start/end| difference between the best
# template and every template scoring >= CONCORD_BITS_FRAC of the best. Toro data only; the
# 76 source-stated Mestre proteins play no part. This is the one and only correction.
dev = []
for q, hs in self_hits.items():
    others = [h for h in hs if h["template"] != q and h["tcov"] >= MIN_TCOV and h["fident"] >= MIN_IDENT]
    if not others:
        continue
    top = max(h["bits"] for h in others)
    best = sorted([h for h in others if h["bits"] >= top * (1 - TIE_BITS_FRAC)], key=lambda h: (-h["bits"], -h["tcov"], h["template"]))[0]
    conc = [h for h in others if h["bits"] >= top * CONCORD_BITS_FRAC]
    dev.append(max(max(abs(h["start"] - best["start"]), abs(h["end"] - best["end"])) for h in conc))
dev_s = pd.Series(dev)
MAX_BOUNDARY_UNC = int(round(float(dev_s.quantile(0.95))))

# ---- PHASE 2 · freeze --------------------------------------------------------------------
params = dict(
    name="MCC-v3.1", frozen_utc=pd.Timestamp.utcnow().isoformat(),
    script_sha256=hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
    toro_fasta_sha256=hashlib.sha256(open(TORO, "rb").read()).hexdigest(),
    n_templates=len(tmpl), LEAVE_NEAR_SELF=LEAVE_NEAR_SELF, MIN_TCOV=MIN_TCOV,
    TIE_BITS_FRAC=TIE_BITS_FRAC, CONCORD_BITS_FRAC=CONCORD_BITS_FRAC,
    MIN_IDENT=MIN_IDENT, MIN_IDENT_basis="5th percentile of nearest-neighbour identity within the Toro retron reference set",
    MAX_BOUNDARY_UNC=MAX_BOUNDARY_UNC,
    MAX_BOUNDARY_UNC_basis="95th percentile of the concordant-template boundary spread within the Toro retron reference set (v3.1 correction: the quantity R5 applies)",
    calib_nn_ident=dict(n=len(nn), p05=MIN_IDENT, median=round(float(nn_s.median()), 4), min=round(float(nn_s.min()), 4)),
    calib_boundary_spread=dict(n=len(dev), p50=float(dev_s.median()), p90=float(dev_s.quantile(0.90)), p95=float(dev_s.quantile(0.95)), max=float(dev_s.max())),
    superseded="v3.0 (R5 calibrated on best-template deviation, 10 aa): outputs in superseded_v3.0/",
    core_qc="MCC-v2 hmmalign route: >= 70 % of required-core states (blocks 4-28) inside the interval",
    mestre_labels_used="none")
json.dump(params, open(f"{OUT}/MCC_V3_PARAMS.json", "w"), indent=2)

# ---- PHASE 3 · apply ---------------------------------------------------------------------
rnap = {r["terminal"] for r in csv.DictReader(open(RNAP), delimiter="\t")}
qf, qset, qlen = f"{WORK}/queries.faa", {}, {}
with open(qf, "w") as fh:
    for f in sorted(glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta")):
        t = f.split("/")[-2]; L = open(f).read().split("\n")
        s = "".join(x.strip() for x in L[1:]).rstrip("*").upper()
        qset[t] = "RNAP_SUBSTITUTE" if t in rnap else ("OTHER_SUBSTITUTE" if "|rescued" in L[0] else "CLEAN")
        qlen[t] = len(s); fh.write(f">{t}\n{s}\n")
hits = search(qf, tf, f"{WORK}/q_vs_templates.m8")
mcc2 = pd.read_csv(MCC2, sep="\t").set_index("terminal")
gt = pd.read_csv(f"{X}/TORO2014_x_MESTRE2020_CROSSWALK.tsv", sep="\t")
gt = gt[gt.mapped].sort_values("fident", ascending=False).drop_duplicates("mestre_terminal").set_index("mestre_terminal")


def extract(t, leave_near_self):
    hs = [h for h in hits.get(t, []) if h["tcov"] >= MIN_TCOV and h["fident"] >= MIN_IDENT]
    if leave_near_self:
        hs = [h for h in hs if h["fident"] < LEAVE_NEAR_SELF]
    if not hs:
        raw = hits.get(t, [])
        why = "NO_HIT" if not raw else ("LOW_TEMPLATE_COVERAGE" if max(h["tcov"] for h in raw) < MIN_TCOV else "LOW_IDENTITY")
        return dict(status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", reason=why)
    top = max(h["bits"] for h in hs)
    tied = [h for h in hs if h["bits"] >= top * (1 - TIE_BITS_FRAC)]
    best = sorted(tied, key=lambda h: (-h["bits"], -h["tcov"], h["template"]))[0]
    conc = [h for h in hs if h["bits"] >= top * CONCORD_BITS_FRAC]
    us = max(abs(h["start"] - best["start"]) for h in conc)
    ue = max(abs(h["end"] - best["end"]) for h in conc)
    d = dict(status="EXTRACTED", reason="", template=best["template"], template_identity=round(best["fident"], 4),
             template_coverage=round(best["tcov"], 4), start=best["start"], end=best["end"],
             n_tied=len(tied), n_concordant=len(conc), unc_start=us, unc_end=ue,
             discordant=(us > MAX_BOUNDARY_UNC or ue > MAX_BOUNDARY_UNC))
    if d["discordant"]:
        d.update(status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", reason="DISCORDANT_TEMPLATES")
    return d


rows = []
for t in sorted(qset, key=lambda x: int(x.split("_")[1])):
    e = extract(t, leave_near_self=False)
    v = extract(t, leave_near_self=True)
    m = mcc2.loc[t] if t in mcc2.index else None
    mok = m is not None and str(m.status).startswith("EXTRACTABLE")
    cs, ce = (float(m.core_start_route1), float(m.core_end_route1)) if mok else ("", "")
    inside = ""
    if e["status"] == "EXTRACTED" and mok:
        ov = max(0.0, min(ce, e["end"]) - max(cs, e["start"]) + 1) / (ce - cs + 1)
        inside = round(ov, 4)
        if ov < 0.70:
            e.update(status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", reason="CORE_QC_FAILED")
    g = gt.loc[t] if t in gt.index else None
    rows.append(dict(terminal=t, set=qset[t], protein_len=qlen[t], mcc_v3_status=e["status"], mcc_v3_reason=e["reason"],
                     template=e.get("template", ""), template_identity=e.get("template_identity", ""),
                     template_coverage=e.get("template_coverage", ""), start=e.get("start", ""), end=e.get("end", ""),
                     core_len=(e["end"] - e["start"] + 1) if e["status"] == "EXTRACTED" else "",
                     n_tied_templates=e.get("n_tied", ""), n_concordant_templates=e.get("n_concordant", ""),
                     boundary_unc_start=e.get("unc_start", ""), boundary_unc_end=e.get("unc_end", ""),
                     discordant_templates=e.get("discordant", ""),
                     mcc_v2_status=m.status if m is not None else "", mcc_v2_core_start=cs, mcc_v2_core_end=ce,
                     mcc_v2_core_inside_interval=inside,
                     val_status=v["status"], val_reason=v["reason"], val_template=v.get("template", ""),
                     val_template_identity=v.get("template_identity", ""), val_start=v.get("start", ""), val_end=v.get("end", ""),
                     toro_stated_start=g.toro_stated_start if g is not None else "",
                     toro_stated_end=g.toro_stated_end if g is not None else ""))
R = pd.DataFrame(rows)
R.to_csv(f"{OUT}/MCC_V3_per_sequence.tsv", sep="\t", index=False)

# ---- PHASE 4 · validate (reporting only) -------------------------------------------------
L = [("MIN_IDENT (R4, Toro-calibrated)", MIN_IDENT), ("MAX_BOUNDARY_UNC aa (R5, Toro-calibrated)", MAX_BOUNDARY_UNC),
     ("templates", len(tmpl))]
for s in ["CLEAN", "OTHER_SUBSTITUTE", "RNAP_SUBSTITUTE"]:
    sub = R[R.set == s]
    L.append((f"{s}: extracted / n", f"{(sub.mcc_v3_status == 'EXTRACTED').sum()} / {len(sub)}"))
    for r, n in sub[sub.mcc_v3_status != "EXTRACTED"].mcc_v3_reason.value_counts().items():
        L.append((f"  {s}: {r}", n))
c = R[(R.set == "CLEAN") & (R.mcc_v3_status == "EXTRACTED")]
L.append(("CLEAN extracted: core length median / IQR", f"{c.core_len.median()} / {c.core_len.quantile(.25)}-{c.core_len.quantile(.75)}"))
L.append(("CLEAN extracted: template identity median", round(float(c.template_identity.median()), 4)))
L.append(("CLEAN extracted: boundary uncertainty (start/end) median", f"{c.boundary_unc_start.median()} / {c.boundary_unc_end.median()}"))
L.append(("CLEAN extracted: MCC-v2 core inside interval, median", c[c.mcc_v2_core_inside_interval != ""].mcc_v2_core_inside_interval.median()))
L.append(("CLEAN: MCC-v2 extractable but MCC-v3 not", int(((R.set == "CLEAN") & (R.mcc_v3_status != "EXTRACTED") & R.mcc_v2_status.astype(str).str.startswith("EXTRACTABLE")).sum())))
L.append(("CLEAN: MCC-v3 extracted but MCC-v2 not", int(((R.set == "CLEAN") & (R.mcc_v3_status == "EXTRACTED") & ~R.mcc_v2_status.astype(str).str.startswith("EXTRACTABLE")).sum())))
g = R[R.toro_stated_start != ""].copy()
v = g[g.val_status == "EXTRACTED"]
if len(v):
    ds = (v.val_start.astype(float) - v.toro_stated_start.astype(float)).abs()
    de = (v.val_end.astype(float) - v.toro_stated_end.astype(float)).abs()
    L += [("VALIDATION (76, leave-near-identical-out): extracted", f"{len(v)} / {len(g)}"),
          ("  start within 5 aa / end within 5 aa", f"{(ds <= 5).mean():.3f} / {(de <= 5).mean():.3f}"),
          ("  median |d start| / |d end|", f"{ds.median()} / {de.median()}"),
          ("  start within MAX_BOUNDARY_UNC / end within it", f"{(ds <= MAX_BOUNDARY_UNC).mean():.3f} / {(de <= MAX_BOUNDARY_UNC).mean():.3f}")]
with open(f"{OUT}/MCC_V3_SUMMARY.tsv", "w") as fh:
    for k, x in L:
        fh.write(f"{k}\t{x}\n")
print(json.dumps(params, indent=2)); print(open(f"{OUT}/MCC_V3_SUMMARY.tsv").read())
