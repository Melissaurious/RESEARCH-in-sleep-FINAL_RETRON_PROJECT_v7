#!/usr/bin/env python3
"""g2r secondary-structure instrument gate (G2R_AMENDMENT_1.md §3), routes A (mkdssp) vs B (pydssp).

Per chain, over residues carrying BOTH a route-A and a route-B 3-state assignment:
  coverage = |common| / |residues with CA|
  for S in {E, H}: kappa(S vs not-S), recall = |A_S & B_S| / |A_S|, precision = |A_S & B_S| / |B_S|
  kappa is undefined only when both routes assign no S (then the chain is 'concordant-empty' for S);
  recall is undefined when A has no S, precision when B has no S; undefined values are omitted from medians
  and counted.
Chain SS gate (needed for any C4/C5/C4b call): coverage >= 0.95 AND for S in {E, H}: kappa >= 0.70 or
  concordant-empty.
Population gate: for S in {E, H}: median kappa >= 0.75, median recall >= 0.80, median precision >= 0.80
  (medians over chains where the value is defined). E and H must both pass; otherwise C4/C5/C4b are
  INSTRUMENT_LIMITED for the whole stage.
Route C (DSSP-KS, g1) is not used here.

Usage: ss_concordance.py <ss_dir> <out_prefix> <chain> [...]
"""
import sys, statistics


def stats(a, b, s):
    n = len(a)
    ta = [x == s for x in a]; tb = [x == s for x in b]
    na, nb = sum(ta), sum(tb)
    both = sum(x and y for x, y in zip(ta, tb))
    po = sum(x == y for x, y in zip(ta, tb)) / n
    pe = (na / n) * (nb / n) + (1 - na / n) * (1 - nb / n)
    kappa = None if pe == 1 else (po - pe) / (1 - pe)
    return dict(kappa=kappa, recall=(both / na if na else None), precision=(both / nb if nb else None),
                nA=na, nB=nb, empty=(na == 0 and nb == 0))


ss_dir, prefix, chains = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = []
for ch in chains:
    L = [l.rstrip("\n").split("\t") for l in open(f"{ss_dir}/{ch}.ss.tsv")]
    h = {k: i for i, k in enumerate(L[0])}
    R = L[1:]
    com = [(r[h["A_ss3"]], r[h["B_ss3"]]) for r in R if r[h["A_ss3"]] and r[h["B_ss3"]]]
    a = [x for x, _ in com]; b = [y for _, y in com]
    cov = len(com) / len(R)
    e, hh = stats(a, b, "E"), stats(a, b, "H")
    ok = cov >= 0.95 and all(s["empty"] or (s["kappa"] is not None and s["kappa"] >= 0.70) for s in (e, hh))
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
with open(prefix + ".gate.tsv", "w") as fh:
    fh.write("state\tmetric\tmedian\tn_defined\tn_undefined\tbar\tpass\n" + "\n".join(lines) + "\n")
print("\n".join(lines))
print("chains passing chain SS gate:", sum(r["chain_ss_gate"] for r in rows), "/", len(rows),
      "; min coverage:", f"{min(r['coverage'] for r in rows):.3f}")
print("population SS gate:", "RELIABLE" if allpass else "UNRELIABLE -> C4/C5/C4b INSTRUMENT_LIMITED")
