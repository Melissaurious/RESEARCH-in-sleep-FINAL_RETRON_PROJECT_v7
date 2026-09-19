#!/usr/bin/env python3
"""g2r secondary-structure instrument gate (G2R_AMENDMENT_1.md §3), routes A (mkdssp) vs B (pydssp).

Per chain, over residues carrying BOTH a route-A and a route-B 3-state assignment:
  coverage = |common| / |residues with CA|
  for S in {E, H}: kappa(S vs not-S), recall = |A_S & B_S| / |A_S|, precision = |A_S & B_S| / |B_S|
  kappa is undefined when both routes are constant and identical for S (both no S = 'concordant-empty', or
  both all S); such a chain is concordant for S (R2 B5);
  recall is undefined when A has no S, precision when B has no S; undefined values are omitted from medians
  and counted.
Chain SS gate (needed for any C4/C5/C4b call): coverage >= 0.95 AND for S in {E, H}: kappa >= 0.70 or
  concordant-constant. A chain with no common residue fails the gate (all metrics undefined).
Population gate: for S in {E, H}: median kappa >= 0.75, median recall >= 0.80, median precision >= 0.80
  (medians over chains where the value is defined) AND >= 0.90 of the cohort passes the chain SS gate
  (R2 B5, so widespread chain-level failure cannot turn into biological non-calls). All must pass; otherwise
  C4/C5/C4b are INSTRUMENT_LIMITED for the whole stage.
The cohort is the frozen chain list file; the SS directory must contain exactly those chains, no duplicates.
Route C (DSSP-KS, g1) is not used here.

Usage: ss_concordance.py <ss_dir> <out_prefix> <cohort.txt>   (one chain name per line)
"""
import sys, statistics


def stats(a, b, s):
    n = len(a)
    if n == 0:
        return dict(kappa=None, recall=None, precision=None, nA=0, nB=0, empty=False)
    ta = [x == s for x in a]; tb = [x == s for x in b]
    na, nb = sum(ta), sum(tb)
    both = sum(x and y for x, y in zip(ta, tb))
    po = sum(x == y for x, y in zip(ta, tb)) / n
    pe = (na / n) * (nb / n) + (1 - na / n) * (1 - nb / n)
    kappa = None if pe == 1 else (po - pe) / (1 - pe)
    return dict(kappa=kappa, recall=(both / na if na else None), precision=(both / nb if nb else None),
                nA=na, nB=nb, empty=(pe == 1 and na == nb))


import os
ss_dir, prefix, cohort = sys.argv[1], sys.argv[2], sys.argv[3]
chains = [l.strip() for l in open(cohort) if l.strip()]
assert len(chains) == len(set(chains)), "duplicate chain in cohort"
present = sorted(f[:-7] for f in os.listdir(ss_dir) if f.endswith(".ss.tsv"))
assert present == sorted(chains), ("SS directory != frozen cohort", sorted(set(present) ^ set(chains)))
rows = []
for ch in chains:
    L = [l.rstrip("\n").split("\t") for l in open(f"{ss_dir}/{ch}.ss.tsv")]
    h = {k: i for i, k in enumerate(L[0])}
    R = L[1:]
    com = [(r[h["A_ss3"]], r[h["B_ss3"]]) for r in R if r[h["A_ss3"]] and r[h["B_ss3"]]]
    a = [x for x, _ in com]; b = [y for _, y in com]
    cov = len(com) / len(R) if R else 0.0
    e, hh = stats(a, b, "E"), stats(a, b, "H")
    ok = bool(com) and cov >= 0.95 and all(s["empty"] or (s["kappa"] is not None and s["kappa"] >= 0.70) for s in (e, hh))
    rows.append(dict(chain=ch, n=len(R), common=len(com), coverage=cov,
                     **{f"E_{k}": v for k, v in e.items()}, **{f"H_{k}": v for k, v in hh.items()},
                     chain_ss_gate=int(ok)))


def fmt(v):
    return "NA" if v is None else (f"{v:.4f}" if isinstance(v, float) else str(v))


with open(prefix + ".per_chain.tsv", "w") as fh:
    fh.write("\t".join(rows[0].keys()) + "\n")
    for r in rows:
        fh.write("\t".join(fmt(v) for v in r.values()) + "\n")
lines, allpass = [], True
for s in ("E", "H"):
    for m, bar in (("kappa", 0.75), ("recall", 0.80), ("precision", 0.80)):
        v = [r[f"{s}_{m}"] for r in rows if r[f"{s}_{m}"] is not None]
        med = statistics.median(v) if v else float("nan")
        ok = bool(v) and med >= bar
        allpass &= ok
        lines.append(f"{s}\t{m}\t{med:.4f}\t{len(v)}\t{len(rows) - len(v)}\t{bar}\t{int(ok)}")
frac_ok = sum(r["chain_ss_gate"] for r in rows) / len(rows)
allpass &= frac_ok >= 0.90
lines.append(f"cohort\tfrac_chain_ss_gate\t{frac_ok:.4f}\t{len(rows)}\t0\t0.9\t{int(frac_ok >= 0.90)}")
with open(prefix + ".gate.tsv", "w") as fh:
    fh.write("state\tmetric\tmedian\tn_defined\tn_undefined\tbar\tpass\n" + "\n".join(lines) + "\n")
print("\n".join(lines))
print("chains passing chain SS gate:", sum(r["chain_ss_gate"] for r in rows), "/", len(rows),
      "; min coverage:", f"{min(r['coverage'] for r in rows):.3f}")
print("population SS gate:", "RELIABLE" if allpass else "UNRELIABLE -> C4/C5/C4b INSTRUMENT_LIMITED")
