#!/usr/bin/env python3
"""MCC-v3.1 as a reusable function, for controls (M2a) and modern queries (M2b/M2c).

It must reproduce the frozen historical output exactly (see `selftest`). The logic is a
verbatim port of m10 phase 3; parameters are READ from the frozen MCC_V3_PARAMS.json and are
never re-derived here. The MCC-v2 core route (hmmalign into the Toro ft0 profile, required
core = blocks 4-28) is re-run for arbitrary sequences with the m07 rules, because the
orthogonal core-QC needs it.

MCC-v2 semantics, as frozen in m10: core-QC is applied only when the MCC-v2 route is
EXTRACTABLE. When it is not, the v3 interval stands, and the MCC-v2 status is recorded
next to it.
"""
import json, os, subprocess, sys
from collections import defaultdict

E = "/home/borg/miniconda3/envs/retron_tradicional/bin"
AUD = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-mestre-audit"
P = json.load(open(f"{AUD}/analysis/mestre_audit/m2_design/mcc_v3/MCC_V3_PARAMS.json"))
TEMPLATES = f"{AUD}/ARIS_OUTPUT/mestre_audit/m10_work/templates.faa"
HMM = f"{AUD}/ARIS_OUTPUT/mestre_audit/m07_work/toro2014_ft0.hmm"
BLOCKS = f"{AUD}/ARIS_OUTPUT/mestre_audit/agent_rt07/toro742_hmm_blocks_to_match_states.tsv"
STD = set("ACDEFGHIKLMNPQRSTVWY")


def _run(cmd, out=None):
    with (open(out, "w") if out else open(os.devnull, "w")) as fh:
        subprocess.run(cmd, check=True, stdout=fh, stderr=subprocess.DEVNULL)


def _fasta(p):
    d, n = {}, None
    for l in open(p):
        l = l.rstrip("\n")
        if l.startswith(">"):
            n = l[1:].split()[0]; d[n] = []
        elif n:
            d[n].append(l.strip())
    return {k: "".join(v) for k, v in d.items()}


def mcc_v2_core(seqs, work, threads=8):
    """MCC-v2 route 1 (m07 rules E1-E5, anchors blocks 4..28) -> {id: (status, core_start, core_end)}."""
    os.makedirs(work, exist_ok=True)
    qf = f"{work}/v2q.faa"; open(qf, "w").write("".join(f">{k}\n{v}\n" for k, v in seqs.items()))
    state_col, inm = {}, False
    for line in open(HMM):
        if line.startswith("HMM "):
            inm = True; continue
        p = line.split()
        if inm and len(p) >= 22 and p[0].isdigit():
            state_col[int(p[0])] = int(p[21])
    import csv
    bl = {int(r["block"]): (int(r["start_col"]), int(r["end_col"])) for r in csv.DictReader(open(BLOCKS), delimiter="\t") if r["block"].isdigit()}
    cs = lambda a, e: [k for k, c in state_col.items() if a <= c <= e]
    N, C = cs(*bl[4]), cs(*bl[28])
    CORE = [k for k, c in state_col.items() if bl[4][0] <= c <= bl[28][1]]
    WIN = [k for k, c in state_col.items() if 68 <= c <= 1305]
    dom = f"{work}/v2.domtbl"
    _run([f"{E}/hmmsearch", "--cpu", str(threads), "-E", "1e-3", "--domE", "1e-5", "--domtblout", dom, HMM, qf])
    envs = defaultdict(list)
    for line in open(dom):
        if not line.startswith("#"):
            p = line.split()
            if float(p[12]) <= 1e-5:
                envs[p[0]].append((int(p[15]), int(p[16]), int(p[19]), int(p[20])))
    a2m = f"{work}/v2.a2m"
    _run([f"{E}/hmmalign", "--amino", "--outformat", "A2M", "-o", a2m, HMM, qf])
    out = {}
    for t, aln in _fasta(a2m).items():
        k = pos = 0; st = {}
        for ch in aln:
            if ch.isupper():
                k += 1; pos += 1; st[k] = pos
            elif ch == "-":
                k += 1
            elif ch.islower():
                pos += 1
        fr = lambda S: sum(1 for x in S if x in st) / len(S)
        win = [st[x] for x in WIN if x in st]
        ext = seqs[t][min(win) - 1:max(win)] if win else ""
        nonstd = (sum(c not in STD for c in ext) / len(ext)) if ext else 1.0
        big = [e for e in envs.get(t, []) if (min(e[1], CORE[-1]) - max(e[0], CORE[0]) + 1) >= 0.5 * len(CORE)]
        big.sort(key=lambda e: e[2]); multi = any(big[i + 1][2] > big[i][3] for i in range(len(big) - 1))
        if not envs.get(t): s = "NO_HIT"
        elif fr(N) < 0.5: s = "N_TRUNCATED"
        elif fr(C) < 0.5: s = "C_TRUNCATED"
        elif fr(CORE) < 0.7: s = "LOW_CORE_OCCUPANCY"
        elif nonstd > 0.01: s = "NONSTANDARD"
        else: s = "EXTRACTABLE_MULTI_CORE" if multi else "EXTRACTABLE"
        c1 = [st[x] for x in CORE if x in st]
        out[t] = (s, min(c1) if c1 else None, max(c1) if c1 else None)
    for t in seqs:
        out.setdefault(t, ("NO_HIT", None, None))
    return out


def extract(seqs, work, leave_near_self=False, threads=8):
    """seqs: {id: protein}. Returns {id: dict}, with the same fields and rules as m10."""
    os.makedirs(work, exist_ok=True)
    qf = f"{work}/v3q.faa"; open(qf, "w").write("".join(f">{k}\n{v}\n" for k, v in seqs.items()))
    m8 = f"{work}/v3q.m8"
    _run([f"{E}/mmseqs", "easy-search", qf, TEMPLATES, m8, f"{work}/tmp", "--threads", str(threads), "-s", "7.5", "-e", "1e-5",
          "--max-seqs", "200", "--format-output", "query,target,fident,qstart,qend,qlen,tstart,tend,tlen,bits"])
    hits = defaultdict(list)
    for line in open(m8):
        q, t, fi, qs, qe, ql, ts, te, tl, b = line.rstrip("\n").split("\t")
        qs, qe, ql, ts, te, tl = map(int, (qs, qe, ql, ts, te, tl))
        hits[q].append(dict(template=t, fident=float(fi), bits=float(b), tcov=(te - ts + 1) / tl,
                            start=max(1, qs - (ts - 1)), end=min(ql, qe + (tl - te))))
    v2 = mcc_v2_core(seqs, f"{work}/v2", threads)
    res = {}
    for t in seqs:
        hs = [h for h in hits.get(t, []) if h["tcov"] >= P["MIN_TCOV"] and h["fident"] >= P["MIN_IDENT"]]
        if leave_near_self:
            hs = [h for h in hs if h["fident"] < P["LEAVE_NEAR_SELF"]]
        r = dict(mcc_v2_status=v2[t][0], mcc_v2_core_start=v2[t][1], mcc_v2_core_end=v2[t][2])
        if not hs:
            raw = hits.get(t, [])
            why = "NO_HIT" if not raw else ("LOW_TEMPLATE_COVERAGE" if max(h["tcov"] for h in raw) < P["MIN_TCOV"] else "LOW_IDENTITY")
            r.update(status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", reason=why); res[t] = r; continue
        top = max(h["bits"] for h in hs)
        tied = [h for h in hs if h["bits"] >= top * (1 - P["TIE_BITS_FRAC"])]
        best = sorted(tied, key=lambda h: (-h["bits"], -h["tcov"], h["template"]))[0]
        conc = [h for h in hs if h["bits"] >= top * P["CONCORD_BITS_FRAC"]]
        us = max(abs(h["start"] - best["start"]) for h in conc); ue = max(abs(h["end"] - best["end"]) for h in conc)
        r.update(status="EXTRACTED", reason="", template=best["template"], template_identity=round(best["fident"], 4),
                 template_coverage=round(best["tcov"], 4), start=best["start"], end=best["end"], n_tied=len(tied),
                 n_concordant=len(conc), unc_start=us, unc_end=ue,
                 discordant=bool(us > P["MAX_BOUNDARY_UNC"] or ue > P["MAX_BOUNDARY_UNC"]))
        if r["discordant"]:
            r.update(status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", reason="DISCORDANT_TEMPLATES")
        elif str(v2[t][0]).startswith("EXTRACTABLE"):
            cs_, ce_ = v2[t][1], v2[t][2]
            ov = max(0.0, min(ce_, r["end"]) - max(cs_, r["start"]) + 1) / (ce_ - cs_ + 1)
            r["mcc_v2_core_inside"] = round(ov, 4)
            if ov < 0.70:
                r.update(status="UNABLE_TO_EXTRACT_HISTORICAL_CORE_RELIABLY", reason="CORE_QC_FAILED")
        r["seq"] = seqs[t][r["start"] - 1:r["end"]] if r["status"] == "EXTRACTED" else ""
        res[t] = r
    return res


def selftest(work):
    """Must reproduce m10's frozen status/start/end for all 1,926 historical proteins."""
    import glob, pandas as pd
    D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
    seqs = {}
    for f in glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta"):
        L = open(f).read().split("\n"); seqs[f.split("/")[-2]] = "".join(x.strip() for x in L[1:]).rstrip("*").upper()
    got = extract(seqs, work)
    ref = pd.read_csv(f"{AUD}/analysis/mestre_audit/m2_design/mcc_v3/MCC_V3_per_sequence.tsv", sep="\t").set_index("terminal")
    bad = [t for t in seqs if got[t]["status"] != ref.loc[t, "mcc_v3_status"]
           or (got[t]["status"] == "EXTRACTED" and (got[t]["start"] != ref.loc[t, "start"] or got[t]["end"] != ref.loc[t, "end"]))]
    print("selftest mismatches:", len(bad), bad[:10])
    return len(bad) == 0


if __name__ == "__main__":
    sys.exit(0 if selftest(sys.argv[1]) else 1)
