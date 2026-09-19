#!/usr/bin/env python3
"""g2r C4 / C5 / C4b / C6 / C7, LOGO influence, fusion / EXTRA_DOMAIN — as frozen in G2R_AMENDMENT_1.md §4–5.

INPUT ALLOWLIST (F4). Nothing else is read:
  * C3r per-residue partition  <pdp_prefix>.residues.tsv / .summary.tsv   (RunPDP output; unit = PDP domain)
  * secondary structure         <ss_dir>/<chain>.ss.tsv                     (ss_routes.py)
  * SS chain gate               <ssgate_prefix>.per_chain.tsv / .gate.tsv  (ss_concordance.py)
  * CA coordinates              <extract_dir>/<chain>.pdb                   (g2 single-chain extracts)
  * alignments                  g2r_foldseek_ava.tsv                        (g2r_ava.py; identical to g2)
  * STRUCTURE_REGISTER.tsv, columns pdb_id, chain, biological_group, fused_or_accessory,
    n_modelled_residues ONLY (lineage/family columns are dropped on read and never touched)
Design-exposed chains (listed on the command line) are excluded from the primary population.

Usage: g2r_units.py <pdp_prefix> <ss_dir> <ssgate_prefix> <extract_dir> <ava.tsv> <register.tsv> <out_prefix>
                    [--exposed CHAIN ...]
"""
import sys, csv, collections, statistics, itertools
import gemmi
import numpy as np

args = sys.argv[1:]
exposed = set()
if "--exposed" in args:
    i = args.index("--exposed"); exposed = set(args[i + 1:]); args = args[:i]
PDP, SSD, SSG, EXD, AVA, REG, OUT = args

ALLOWED = ("pdb_id", "chain", "biological_group", "fused_or_accessory", "n_modelled_residues")
reg = {}
for r in csv.DictReader(open(REG), delimiter="\t"):
    r = {k: r[k] for k in ALLOWED}
    reg[f"{r['pdb_id']}_{r['chain']}"] = r
chains = sorted(reg)
group = {c: reg[c]["biological_group"] for c in chains}
flagged = {c for c in chains if reg[c]["fused_or_accessory"] in ("YES", "SUSPECTED") or int(reg[c]["n_modelled_residues"]) > 600}
primary = [c for c in chains if c not in flagged and c not in exposed]

# ---- C3r partition ----
summ = {r["chain"]: r for r in csv.DictReader(open(PDP + ".summary.tsv"), delimiter="\t")}
pdpkey = collections.defaultdict(dict)
for r in csv.DictReader(open(PDP + ".residues.tsv"), delimiter="\t"):
    pdpkey[r["chain"]][(int(r["resnum"]), r["icode"])] = int(r["domain"])

# ---- SS ----
SS = {}
for c in chains:
    L = [l.rstrip("\n").split("\t") for l in open(f"{SSD}/{c}.ss.tsv")]
    h = {k: i for i, k in enumerate(L[0])}
    SS[c] = [dict(idx=int(r[h["idx"]]), key=(int(r[h["resnum"]]), r[h["icode"]]), resname=r[h["resname"]],
                  brk=int(r[h["break_before"]]), A=r[h["A_ss3"]], B=r[h["B_ss3"]], sheet=r[h["A_sheet"]],
                  bp={int(r[h["A_bp1_idx"]]), int(r[h["A_bp2_idx"]])} - {-1}) for r in L[1:]]
# canonical ordered index = residues carrying CA in the extract (== foldseek's index space, asserted in g2r_ava).
# Residues BioJava leaves out of its representative-atom array (e.g. HETATM modified residues under the
# ReducedChemCompProvider) are PDP_ABSENT: label 0, in no unit, counted and reported.
lab, pdp_absent = {}, {}
for c in chains:
    keys = [x["key"] for x in SS[c]]
    assert set(pdpkey[c]) <= set(keys), c
    lab[c] = [pdpkey[c].get(k, 0) for k in keys]
    pdp_absent[c] = [f"{k[0]}{k[1]}:{x['resname']}" for k, x in zip(keys, SS[c]) if k not in pdpkey[c]]
ssgate = {r["chain"]: int(r["chain_ss_gate"]) for r in csv.DictReader(open(SSG + ".per_chain.tsv"), delimiter="\t")}
pop_ss_ok = all(int(r["pass"]) for r in csv.DictReader(open(SSG + ".gate.tsv"), delimiter="\t"))

# ---- CA coordinates (same ordered residue list) ----
CA = {}
for c in chains:
    st = gemmi.read_structure(f"{EXD}/{c}.pdb"); st.remove_alternative_conformations()
    res = [r for r in st[0][0] if r.find_atom("CA", "*")]
    assert [(r.seqid.num, r.seqid.icode.strip()) for r in res] == [x["key"] for x in SS[c]], c
    CA[c] = np.array([[r.find_atom("CA", "*").pos.x, r.find_atom("CA", "*").pos.y, r.find_atom("CA", "*").pos.z] for r in res])


def runs(c, state):
    """maximal runs of route-A `state`, split at chain breaks and at residues lacking a route-A assignment"""
    out, cur = [], []
    for x in SS[c]:
        if x["A"] == state and not (x["brk"] and cur):
            cur.append(x["idx"])
        else:
            if cur: out.append(cur)
            cur = [x["idx"]] if x["A"] == state else []
    if cur: out.append(cur)
    return out


def pieces(c, unit_idx, state, minlen):
    """element pieces inside a unit: each chain-level run split by unit membership; keep pieces >= minlen"""
    s = set(unit_idx)
    out = []
    for run in runs(c, state):
        cur = []
        for i in run:
            if i in s: cur.append(i)
            elif cur: out.append(cur); cur = []
        if cur: out.append(cur)
    return [p for p in out if len(p) >= minlen]


def sheet_of(c, p):
    labs = [SS[c][i]["sheet"] for i in p if SS[c][i]["sheet"]]
    return collections.Counter(labs).most_common(1)[0][0] if labs else None


def contacts(c, u, v):
    d = np.linalg.norm(CA[c][u][:, None, :] - CA[c][v][None, :, :], axis=-1)
    return int((d <= 8.0).sum())


def unit_features(c, u):
    n = len(u)
    fE = sum(SS[c][i]["A"] == "E" for i in u) / n
    fH = sum(SS[c][i]["A"] == "H" for i in u) / n
    strands = pieces(c, u, "E", 2)
    helices = pieces(c, u, "H", 8)
    sheets = collections.Counter(sheet_of(c, p) for p in strands if sheet_of(c, p))
    max_sheet = max(sheets.values()) if sheets else 0
    hairpin = False
    for p, q in itertools.combinations(sorted(strands), 2):
        if sheet_of(c, p) and sheet_of(c, p) == sheet_of(c, q) and q[0] - p[-1] - 1 <= 8:
            if any(SS[c][i]["bp"] & set(q) for i in p):
                hairpin = True
    return dict(n=n, fE=fE, fH=fH, n_strands=len(strands), max_strands_one_sheet=max_sheet,
                n_helices8=len(helices), hairpin=hairpin)


calls, unitrows = {}, []
for c in chains:
    L = lab[c]
    units = {d: [i for i, x in enumerate(L) if x == d] for d in sorted(set(L)) if d}
    F = {d: unit_features(c, u) for d, u in units.items()}
    ok = summ[c]["status"] == "OK" and pop_ss_ok and ssgate.get(c, 0) == 1
    res = dict(n_units=len(units), C4="NO_CALL", C5="NOT_EVALUABLE", C4b="NOT_EVALUABLE", palm=None, thumb=None,
               fingers=None, units=units)
    if summ[c]["status"] != "OK":
        res["C4"] = "INSTRUMENT_LIMITED:pdp"
    elif not pop_ss_ok:
        res["C4"] = "INSTRUMENT_LIMITED:ss_population"
    elif ssgate.get(c, 0) != 1:
        res["C4"] = "INSTRUMENT_LIMITED:ss_chain"
    else:
        cand = [d for d, f in F.items() if f["max_strands_one_sheet"] >= 4 and f["fE"] >= 0.20 and f["fH"] >= 0.15]
        if cand:
            best = max(F[d]["max_strands_one_sheet"] for d in cand)
            top = [d for d in cand if F[d]["max_strands_one_sheet"] == best]
            if len(top) > 1:
                res["C4"] = "AMBIGUOUS"
            else:
                p = top[0]
                aE = [i for i in units[p] if SS[c][i]["A"] == "E"]
                bfrac = sum(SS[c][i]["B"] == "E" for i in aE) / len(aE)
                if bfrac >= 0.70:
                    res["C4"], res["palm"] = "CALL", p
                else:
                    res["C4"] = "INSTRUMENT_LIMITED:palm_routeB"
    if res["C4"] == "CALL":
        p = res["palm"]
        ct = {d: contacts(c, units[d], units[p]) for d in units if d != p}
        q5 = [d for d in ct if F[d]["fH"] >= 0.60 and F[d]["fE"] <= 0.10 and F[d]["n_helices8"] >= 3 and ct[d] >= 20]
        res["C5"] = "CALL" if len(q5) == 1 else ("AMBIGUOUS" if q5 else "NO_CALL")
        if len(q5) == 1: res["thumb"] = q5[0]
        qb = [d for d in ct if d not in q5 and F[d]["hairpin"] and F[d]["n_helices8"] >= 1 and ct[d] >= 20]
        res["C4b"] = "CALL" if len(qb) == 1 else ("AMBIGUOUS" if qb else "NO_CALL")
        if len(qb) == 1: res["fingers"] = qb[0]
    else:
        ct = {}
    calls[c] = res
    for d, u in units.items():
        role = "palm-like" if d == res["palm"] else "thumb-like" if d == res["thumb"] else "fingers-like" if d == res["fingers"] else ""
        f = F[d]
        segs, s0 = [], u[0]
        for a, b in zip(u, u[1:] + [None]):
            if b != a + 1:
                segs.append(f"{SS[c][s0]['key'][0]}{SS[c][s0]['key'][1]}-{SS[c][a]['key'][0]}{SS[c][a]['key'][1]}")
                if b is not None: s0 = b
        unitrows.append(dict(chain=c, group=group[c], unit=d, n_res=f["n"], segments=",".join(segs), n_segments=len(segs),
                             frac_E=round(f["fE"], 3), frac_H=round(f["fH"], 3), n_strands=f["n_strands"],
                             max_strands_one_sheet=f["max_strands_one_sheet"], n_helices8=f["n_helices8"],
                             hairpin=int(f["hairpin"]), contacts_with_palm=ct.get(d, ""), role=role))

# ---- alignments -> residue maps (ordered-index; qlen/tlen asserted) ----
ALN = {}
for r in csv.DictReader(open(AVA), delimiter="\t"):
    q, t = r["query"], r["target"]
    if q == t or q not in reg or t not in reg: continue
    if int(r["qlen"]) != len(SS[q]) or int(r["tlen"]) != len(SS[t]): continue
    tm = min(float(r["qtmscore"]), float(r["ttmscore"]))
    qi, ti, m = int(r["qstart"]) - 1, int(r["tstart"]) - 1, {}
    for a, b in zip(r["qaln"], r["taln"]):
        if a != "-" and b != "-": m[qi] = ti
        if a != "-": qi += 1
        if b != "-": ti += 1
    ALN[(q, t)] = (tm, m)

ROLES = {"C4": "palm", "C5": "thumb", "C4b": "fingers"}


def unit_of(c, T):
    d = calls[c][ROLES[T]]
    return set(calls[c]["units"][d]) if d is not None else None


def c6(T, pop):
    pop = set(pop)
    per_pair, absent = collections.defaultdict(list), 0
    for (x, y), (tm, m) in ALN.items():
        if x not in pop or y not in pop or group[x] == group[y] or tm < 0.50: continue
        ux = unit_of(x, T)
        if ux is None: continue
        uy = unit_of(y, T)
        if uy is None: absent += 1; continue
        rec = sum(1 for i in ux if m.get(i) in uy) / len(ux)
        per_pair[tuple(sorted((group[x], group[y])))].append(rec)
    gp = [statistics.mean(v) for v in per_pair.values()]
    med = statistics.median(gp) if gp else float("nan")
    status = "UNDERPOWERED" if len(gp) < 10 else ("RECURRENT" if med >= 0.50 else "NOT_RECURRENT")
    return dict(median=med, n_group_pairs=len(gp), n_absent_in_Y=absent, status=status)


def c7(T, pop):
    pop = set(pop)
    byg = collections.defaultdict(list)
    for c in pop: byg[group[c]].append(c)
    gvals, excluded = [], 0
    for g, cs in byg.items():
        vals = []
        for a, b in itertools.combinations(sorted(cs), 2):
            ka = {x["key"]: x for x in SS[a]}; kb = {x["key"]: x for x in SS[b]}
            common = set(ka) & set(kb)
            if not common or sum(ka[k]["resname"] == kb[k]["resname"] for k in common) / len(common) < 0.95:
                excluded += 1; continue
            ua, ub = unit_of(a, T), unit_of(b, T)
            if ua is None and ub is None: continue
            if ua is None or ub is None: vals.append(0.0); continue
            sa = {SS[a][i]["key"] for i in ua} & common; sb = {SS[b][i]["key"] for i in ub} & common
            vals.append(len(sa & sb) / len(sa | sb) if sa | sb else 0.0)
        if vals: gvals.append(statistics.median(vals))
    med = statistics.median(gvals) if gvals else float("nan")
    status = "UNDERPOWERED" if len(gvals) < 5 else ("STABLE" if med >= 0.70 else "NOT_STABLE")
    return dict(median=med, n_groups=len(gvals), n_pairs_numbering_excluded=excluded, status=status)


def evaluate(pop):
    out = {}
    for T in ("C4", "C5", "C4b"):
        rate = sum(calls[c][T] == "CALL" for c in pop) / len(pop) if pop else float("nan")
        r6, r7 = c6(T, pop), c7(T, pop)
        meets = rate >= 0.70 and r6["status"] == "RECURRENT" and r7["status"] == "STABLE"
        out[T] = dict(call_rate=rate, n=len(pop), C6=r6, C7=r7, meets=meets)
    return out


def verdict(ev):
    k = sum(ev[T]["meets"] for T in ev)
    return "PASS" if k == 3 else ("PARTIAL" if k >= 1 else "FAIL")


def dcount_agreement(pop):
    byg = collections.defaultdict(list)
    for c in pop: byg[group[c]].append(calls[c]["n_units"])
    pairs = [int(a == b) for v in byg.values() for a, b in itertools.combinations(v, 2)]
    return (sum(pairs) / len(pairs), len(pairs)) if pairs else (float("nan"), 0)


# ---- EXTRA_DOMAIN ----
for row in unitrows:
    c, u = row["chain"], set(calls[row["chain"]]["units"][row["unit"]])
    aligned = set()
    for (x, y), (tm, m) in ALN.items():
        if x == c and group[y] != group[c] and tm >= 0.50:
            aligned |= {i for i in u if i in m}
    row["frac_aligned_other_groups"] = round(len(aligned) / len(u), 3)
    row["EXTRA_DOMAIN"] = int(len(aligned) / len(u) < 0.10)

# ---- outputs ----
with open(OUT + ".units.tsv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(unitrows[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(unitrows)
with open(OUT + ".calls.tsv", "w") as fh:
    fh.write("chain\tgroup\tstratum\tn_units\tC4\tC5\tC4b\tpalm_unit\tthumb_unit\tfingers_unit\n")
    for c in chains:
        s = "design_exposed" if c in exposed else ("flagged" if c in flagged else "primary")
        r = calls[c]
        fh.write(f"{c}\t{group[c]}\t{s}\t{r['n_units']}\t{r['C4']}\t{r['C5']}\t{r['C4b']}\t{r['palm'] or ''}\t{r['thumb'] or ''}\t{r['fingers'] or ''}\n")

rep = []
for label, pop in (("primary", primary), ("flagged", sorted(flagged - exposed)), ("all_nonexposed", [c for c in chains if c not in exposed])):
    ev = evaluate(pop)
    rep.append(f"## {label} (n={len(pop)})  verdict-rule outcome: {verdict(ev)}")
    for T, e in ev.items():
        rep.append(f"{T}\tcall_rate={e['call_rate']:.3f}\tC6={e['C6']['status']}(median={e['C6']['median']:.3f},group_pairs={e['C6']['n_group_pairs']},absent_in_Y={e['C6']['n_absent_in_Y']})"
                   f"\tC7={e['C7']['status']}(median={e['C7']['median']:.3f},groups={e['C7']['n_groups']},numbering_excluded={e['C7']['n_pairs_numbering_excluded']})\tmeets={e['meets']}")
    a, n = dcount_agreement(pop)
    rep.append(f"replicate PDP domain-count agreement: {a:.3f} over {n} pairs")
    rep.append("call-status counts: " + "; ".join(f"{T}: {dict(collections.Counter(calls[c][T] for c in pop))}" for T in ROLES))
# LOGO influence on the primary population
ev0 = evaluate(primary)
rep.append("## LOGO influence (primary)")
flips = collections.Counter()
rng = {T: [] for T in ROLES}
vcount = collections.Counter()
for g in sorted({group[c] for c in primary}):
    pop = [c for c in primary if group[c] != g]
    ev = evaluate(pop)
    vcount[verdict(ev)] += 1
    for T in ROLES:
        rng[T].append((ev[T]["call_rate"], ev[T]["C6"]["median"], ev[T]["C7"]["median"]))
        if ev[T]["meets"] != ev0[T]["meets"]: flips[(T, g)] += 1
for T in ROLES:
    cr = [x[0] for x in rng[T]]; r6 = [x[1] for x in rng[T] if x[1] == x[1]]; r7 = [x[2] for x in rng[T] if x[2] == x[2]]
    rep.append(f"{T}\tcall_rate {min(cr):.3f}-{max(cr):.3f}\tC6 median {min(r6, default=float('nan')):.3f}-{max(r6, default=float('nan')):.3f}"
               f"\tC7 median {min(r7, default=float('nan')):.3f}-{max(r7, default=float('nan')):.3f}")
rep.append(f"LOGO folds by verdict: {dict(vcount)}; folds flipping a region's bar outcome: {sorted(flips)}")
rep.append("PDP_ABSENT residues (not in BioJava's representative-atom array): " +
           (", ".join(f"{c}[{';'.join(v)}]" for c, v in pdp_absent.items() if v) or "none"))
rep.append(f"EXTRA_DOMAIN units: {sum(r['EXTRA_DOMAIN'] for r in unitrows)} / {len(unitrows)} "
           f"(flagged chains: {sum(r['EXTRA_DOMAIN'] for r in unitrows if r['chain'] in flagged)})")
open(OUT + ".report.txt", "w").write("\n".join(rep) + "\n")
print("\n".join(rep))
