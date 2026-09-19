#!/usr/bin/env python3
"""g2r external benchmark — deterministic CATH selection, exactly as pre-registered.

Eligible chain: CathDomall entry with 1-4 domains and ZERO fragments; resolution <= 2.5 A;
span of CATH-assigned residues 80-700; its first domain (00 or 01) is an S35 representative;
PDB ID not in the Stage-3A RT population; no domain whose CATH topology (C.A.T) or superfamily
(C.A.T.H) node name contains reverse transcriptase / polymerase / maturase / retron.
One chain per PDB entry: CathDomall lines are read in lexicographic order and the first eligible chain of an
entry is kept (tie rule, amendment 1).  Order each stratum by sha256(chain id).  No RNG.
Amendment 1: writes the ordered CANDIDATE pools (first QUOTA+EXTRA per stratum, rank = position in the
stratum order) with insertion codes kept; the structural independence screen (cath_screen.py) then takes the
first QUOTA survivors per stratum.  If a stratum has fewer survivors than its quota, all survivors are
taken and the shortfall is reported (no substitution from other strata).

Usage: cath_select.py <cath_dir> <rt_register.tsv> <out_candidates.tsv>
"""
import sys, re, csv, hashlib, collections

cath, reg, out = sys.argv[1], sys.argv[2], sys.argv[3]
QUOTA = {1: 30, 2: 30, 3: 25, 4: 15}
EXTRA = 40
BAD = re.compile(r"reverse transcriptase|polymerase|maturase|retron", re.I)

rt_pdbs = {r["pdb_id"].lower() for r in csv.DictReader(open(reg), delimiter="\t")}

bad_nodes = set()
for l in open(f"{cath}/cath-names.txt"):
    if l.startswith("#") or not l.strip():
        continue
    node = l.split()[0]
    if BAD.search(l.split(":", 1)[-1]):
        bad_nodes.add(node)

dom_sf, dom_res = {}, {}
for l in open(f"{cath}/cath-domain-list.txt"):
    if l.startswith("#") or not l.strip():
        continue
    p = l.split()
    dom_sf[p[0]] = ".".join(p[1:5])
    dom_res[p[0]] = float(p[11])

s35 = set()
for l in open(f"{cath}/cath-domain-list-S35.txt"):
    if l.startswith("#") or not l.strip():
        continue
    s35.add(l.split()[0])


def parse_domall(line):
    """-> (chain, ndom, nfrag, [[(start, end), ...] per domain]) with numeric residue parts."""
    t = line.split()
    chain, ndom, nfrag = t[0], int(t[1][1:]), int(t[2][1:])
    i, doms = 3, []
    for _ in range(ndom):
        nseg = int(t[i]); i += 1
        segs = []
        for _ in range(nseg):
            s, si, e, ei = t[i + 1], t[i + 2], t[i + 4], t[i + 5]
            segs.append((s, "" if si == "-" else si, e, "" if ei == "-" else ei)); i += 6
        doms.append(segs)
    return chain, ndom, nfrag, doms


def num(x):
    m = re.match(r"-?\d+", x)
    return int(m.group(0)) if m else None


elig = collections.defaultdict(list)
seen_pdb = set()
for l in sorted(open(f"{cath}/cath-domain-boundaries.txt")):
    if l.startswith("#") or not l.strip():
        continue
    try:
        chain, ndom, nfrag, doms = parse_domall(l)
    except (IndexError, ValueError):
        continue
    if not (1 <= ndom <= 4) or nfrag != 0:
        continue
    pdb = chain[:4].lower()
    if pdb in rt_pdbs or pdb in seen_pdb:
        continue
    ids = [chain + "00"] if ndom == 1 else [f"{chain}{k:02d}" for k in range(1, ndom + 1)]
    if any(d not in dom_sf for d in ids):
        continue
    if ids[0] not in s35:
        continue
    if dom_res[ids[0]] > 2.5:
        continue
    sfs = [dom_sf[d] for d in ids]
    if any(sf in bad_nodes or ".".join(sf.split(".")[:3]) in bad_nodes for sf in sfs):
        continue
    nums = [num(v) for segs in doms for s, _, e, _ in segs for v in (s, e)]
    if None in nums:
        continue
    span = max(nums) - min(nums) + 1
    if not (80 <= span <= 700):
        continue
    seen_pdb.add(pdb)
    elig[ndom].append(dict(chain=chain, pdb_id=pdb.upper(), chain_id=chain[4:], n_domains=ndom,
                           span=span, resolution=dom_res[ids[0]], superfamilies=";".join(sfs),
                           domains="|".join(",".join(f"{s}-{e}" for s, _, e, _ in segs) for segs in doms),
                           domains_icode="|".join(",".join(f"{s}{si}:{e}{ei}" for s, si, e, ei in segs) for segs in doms),
                           discontinuous=int(any(len(segs) > 1 for segs in doms)),
                           order_key=hashlib.sha256(chain.encode()).hexdigest()))

rows = []
for k, q in QUOTA.items():
    pool = sorted(elig[k], key=lambda r: r["order_key"])
    for rank, r in enumerate(pool[:q + EXTRA]):
        rows.append(dict(r, rank=rank, quota=q))
    print(f"{k}-domain: eligible {len(pool):6d}  candidates {min(q + EXTRA, len(pool))}")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
print("candidates:", len(rows))
