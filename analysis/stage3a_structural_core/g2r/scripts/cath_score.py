#!/usr/bin/env python3
"""g2r external validation of C3r against CATH — scoring exactly as frozen in G2R_AMENDMENT_1.md §2.

Residue universe U (per chain): residues of the extract carrying a representative atom (the PDP per-residue
table, keyed by (author seq number, insertion code)) that fall inside a CATH domain segment. A CATH segment
spans the ordered residues from its start key to its end key inclusive; an endpoint key that is not observed
is resolved to the first observed residue at/after (start) or last at/before (end) by sequence number.
Residues in no CATH segment (tails, linkers, fragments) are outside U. PDP residues in no PDP domain
(label 0) stay in U and can match nothing.
Overlap = max over one-to-one (partial) matchings between CATH and PDP domains of the summed residue
intersection, divided by |U| (Hungarian assignment; maximises the total intersection).
Preflight failures / missing output count as count-incorrect with overlap 0.

Acceptance (all required): A count agreement >= 0.60; B CATH-1 parsed as 1 >= 0.70; C CATH-multi parsed as
>= 2 >= 0.60; D median overlap among count-correct >= 0.80; E1 discontinuous stratum parsed as >= 2 >= 0.60;
E2 median overlap over the discontinuous stratum >= 0.70.

Usage: cath_score.py <benchmark_final.tsv> <pdp_prefix> <chain_dir> <out_prefix>
"""
import sys, re, csv, collections, statistics
import numpy as np
import gemmi
from scipy.optimize import linear_sum_assignment

bench, pdp, chain_dir, out = sys.argv[1:5]
B = list(csv.DictReader(open(bench), delimiter="\t"))
summ = {r["chain"]: r for r in csv.DictReader(open(pdp + ".summary.tsv"), delimiter="\t")}
pk = collections.defaultdict(dict)
for r in csv.DictReader(open(pdp + ".residues.tsv"), delimiter="\t"):
    pk[r["chain"]][(int(r["resnum"]), r["icode"])] = int(r["domain"])
# ordered residue list = residues carrying CA in the extract; residues BioJava leaves out of its representative
# array (HETATM modified residues under ReducedChemCompProvider) keep label 0 (PDP_ABSENT) and stay in U.
res = {}
for ch in pk:
    st = gemmi.read_structure(f"{chain_dir}/{ch}.pdb"); st.remove_alternative_conformations()
    keys = [(r.seqid.num, r.seqid.icode.strip()) for r in st[0][0] if r.find_atom("CA", "*")]
    assert set(pk[ch]) <= set(keys), ch
    res[ch] = [(k, pk[ch].get(k, 0)) for k in keys]

KEY = re.compile(r"^(-?\d+)([A-Za-z]?)$")


def key(s):
    m = KEY.match(s)
    assert m, s
    return int(m.group(1)), m.group(2)


def cath_labels(keys, dom_str):
    pos = {k: i for i, k in enumerate(keys)}
    lab = [0] * len(keys)
    notes = []
    for d, segs in enumerate(dom_str.split("|"), 1):
        for seg in segs.split(","):
            s, e = (key(x) for x in seg.split(":"))
            if s in pos:
                i0 = pos[s]
            else:
                c = [i for i, k in enumerate(keys) if k[0] >= s[0]]
                i0 = c[0] if c else len(keys)
                notes.append(f"start{s}~")
            if e in pos:
                i1 = pos[e]
            else:
                c = [i for i, k in enumerate(keys) if k[0] <= e[0]]
                i1 = c[-1] if c else -1
                notes.append(f"end{e}~")
            for i in range(i0, i1 + 1):
                if lab[i] not in (0, d):
                    notes.append(f"cath_overlap@{keys[i]}")
                lab[i] = d
    return lab, notes


rows = []
for b in B:
    ch, n_cath = b["chain"], int(b["n_domains"])
    s = summ.get(ch)
    r = dict(chain=ch, n_cath=n_cath, discontinuous=int(b["discontinuous"]), status=s["status"] if s else "MISSING")
    if not s or s["status"] != "OK" or ch not in res:
        rows.append(dict(r, n_pdp=0, count_ok=0, overlap=0.0, U=0, pdp_absent=0, unassigned=0, pdp_discont=0, notes="no_output"))
        continue
    keys = [k for k, _ in res[ch]]
    plab = [d for _, d in res[ch]]
    clab, notes = cath_labels(keys, b["domains_icode"])
    U = [i for i in range(len(keys)) if clab[i]]
    pd = sorted({plab[i] for i in range(len(keys)) if plab[i]})
    n_pdp = int(s["n_domains"])
    assert len(pd) <= n_pdp, (ch, pd, n_pdp)
    M = np.zeros((n_cath, max(1, len(pd))))
    for i in U:
        if plab[i]:
            M[clab[i] - 1, pd.index(plab[i])] += 1
    ri, ci = linear_sum_assignment(-M)
    ov = M[ri, ci].sum() / len(U) if U else 0.0
    # discontinuous PDP output: a domain whose residues are not one contiguous idx run
    pdisc = 0
    for d in pd:
        idx = [i for i in range(len(keys)) if plab[i] == d]
        pdisc += int(idx[-1] - idx[0] + 1 != len(idx))
    absent = sum(1 for k in keys if k not in pk[ch])
    rows.append(dict(r, n_pdp=n_pdp, count_ok=int(n_pdp == n_cath), overlap=round(float(ov), 4), U=len(U), pdp_absent=absent,
                     unassigned=sum(1 for i in U if plab[i] == 0), pdp_discont=pdisc, notes=";".join(notes)))

with open(out + ".per_chain.tsv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)


def frac(xs):
    return (sum(xs) / len(xs), len(xs)) if xs else (float("nan"), 0)


A = frac([r["count_ok"] for r in rows])
Bm = frac([int(r["n_pdp"] == 1) for r in rows if r["n_cath"] == 1])
C = frac([int(r["n_pdp"] >= 2) for r in rows if r["n_cath"] >= 2])
Dv = [r["overlap"] for r in rows if r["count_ok"]]
D = (statistics.median(Dv), len(Dv)) if Dv else (float("nan"), 0)
disc = [r for r in rows if r["discontinuous"]]
E1 = frac([int(r["n_pdp"] >= 2) for r in disc])
E2 = (statistics.median([r["overlap"] for r in disc]), len(disc)) if disc else (float("nan"), 0)
gates = [("A", "count agreement", A, 0.60), ("B", "CATH-1 parsed as 1", Bm, 0.70),
         ("C", "CATH-multi parsed >=2", C, 0.60), ("D", "median overlap | count-correct", D, 0.80),
         ("E1", "discontinuous parsed >=2", E1, 0.60), ("E2", "median overlap | discontinuous", E2, 0.70)]
with open(out + ".gates.tsv", "w") as fh:
    fh.write("gate\tmetric\tvalue\tn\tbar\tpass\n")
    for g, m, (v, n), bar in gates:
        fh.write(f"{g}\t{m}\t{v:.4f}\t{n}\t{bar}\t{int(v >= bar)}\n")
        print(f"{g:3s} {m:34s} {v:.3f} (n={n})  bar {bar}  {'PASS' if v >= bar else 'FAIL'}")
allpass = all(v >= bar for _, _, (v, _), bar in gates)
print("C3r external validation:", "ACCEPT" if allpass else "INSTRUMENT_LIMITED")
print("secondary: boundary-correct (overlap>=0.85) among count-correct:",
      f"{sum(o >= 0.85 for o in Dv)}/{len(Dv)};", "median overlap all chains:",
      f"{statistics.median(r['overlap'] for r in rows):.3f};", "PDP outputs with a discontinuous domain:",
      sum(r["pdp_discont"] > 0 for r in rows), "; status:", dict(collections.Counter(r["status"] for r in rows)))
print("confusion (CATH n -> PDP n):", dict(sorted(collections.Counter((r["n_cath"], r["n_pdp"]) for r in rows).items())))
