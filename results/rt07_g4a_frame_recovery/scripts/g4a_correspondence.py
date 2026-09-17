#!/usr/bin/env python3
"""g4a Phase B/C — between-family correspondence from DE NOVO profiles only.

Pairwise profile-profile with hhalign (hhsearch -d needs an ffindex DB; hhalign is
the correct pairwise tool). Maps each family's catalytic-dyad match state through
the pairwise alignment to test anchor-level correspondence, then estimates the
supported intersection.

Usage: g4a_correspondence.py <workdir> <tabledir>
"""
import sys, os, re, subprocess, collections, itertools, statistics, math

WORK, TABLES = sys.argv[1], sys.argv[2]
BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
DYAD = re.compile(r"[YF].DD")
MATCH_GAP_CUTOFF = 0.50          # hhmake -M 50


def read_fasta(p):
    s, n = {}, None
    for line in open(p, errors="replace"):
        line = line.rstrip()
        if line.startswith(">"):
            n = line[1:].split()[0]
            s[n] = []
        elif n is not None:
            s[n].append(line.strip())
    return {k: "".join(v) for k, v in s.items()}


def match_states(aln):
    """MSA column (1-based) -> hhm match-state index (1-based), by the -M 50 rule."""
    ids = list(aln)
    L = len(aln[ids[0]])
    m, k = {}, 0
    for c in range(L):
        col = [aln[i][c] for i in ids]
        gap = sum(1 for x in col if x in "-.") / len(col)
        if gap < MATCH_GAP_CUTOFF:
            k += 1
            m[c + 1] = k
    return m


def dyad_matchstate(fam):
    """Modal match state carrying the catalytic dyad Y/F in this family's derivation MSA."""
    aln = read_fasta(f"{WORK}/{fam}.deriv.mafft.afa")
    ms = match_states(aln)
    cnt = collections.Counter()
    for sid, gapped in aln.items():
        plain = gapped.replace("-", "").replace(".", "").upper()
        # map ungapped index -> alignment column
        u2c, u = {}, 0
        for c, ch in enumerate(gapped, 1):
            if ch not in "-.":
                u += 1
                u2c[u] = c
        for mm in DYAD.finditer(plain):
            c = u2c.get(mm.start() + 1)
            if c and c in ms:
                cnt[ms[c]] += 1
    return (cnt.most_common(1)[0] if cnt else (None, 0)), sum(cnt.values()), len(cnt)


def parse_hhalign(path):
    """Return (prob, evalue, score, cols, qspan, tspan, qlen, tlen, q2t mapping)."""
    txt = open(path).read()
    hdr = re.search(r"^\s*1\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+"
                    r"(\d+)-(\d+)\s+(\d+)-(\d+)\s*\((\d+)\)", txt, re.M)
    if not hdr:
        return None
    prob, ev, score, cols = hdr.group(1), hdr.group(2), hdr.group(4), hdr.group(6)
    q1, q2, t1, t2, tlen = (int(hdr.group(i)) for i in (7, 8, 9, 10, 11))
    mc = re.search(r"^Match_columns\s+(\d+)", txt, re.M)
    qlen = int(mc.group(1)) if mc else 0
    # column mapping from the Q Consensus / T Consensus block pairs
    q2t = {}
    blocks = re.findall(
        r"^Q Consensus\s+(\d+)\s+(\S+)\s+\d+.*?\n.*?\n.*?\n^T Consensus\s+(\d+)\s+(\S+)\s+\d+",
        txt, re.M | re.S)
    for qs, qseq, ts, tseq in blocks:
        qi, ti = int(qs), int(ts)
        for a, b in zip(qseq, tseq):
            qg, tg = a in "-.", b in "-."
            if not qg and not tg:
                q2t[qi] = ti
            if not qg:
                qi += 1
            if not tg:
                ti += 1
    return prob, ev, score, cols, (q1, q2), (t1, t2), qlen, tlen, q2t


# ---------------------------------------------------------------- dyad states
dy = {}
for f in FAMILIES:
    (ms, n), tot, ndist = dyad_matchstate(f)
    dy[f] = dict(state=ms, n_at=n, total=tot, distinct=ndist)

# ------------------------------------------------------------ pairwise hhalign
rows, mapping_rows = [], []
pairmap = {}
for a, b in itertools.permutations(FAMILIES, 2):
    out = f"{WORK}/hha_{a}__{b}.hhr"
    subprocess.run([BIN + "hhalign", "-i", f"{WORK}/{a}.deriv.hhm",
                    "-t", f"{WORK}/{b}.deriv.hhm", "-o", out],
                   capture_output=True, text=True)
    p = parse_hhalign(out) if os.path.exists(out) else None
    if not p:
        rows.append([a, b, "", "", "", "", "", "", "NO_HIT_PARSED"])
        continue
    prob, ev, score, cols, qs, ts, qlen, tlen, q2t = p
    pairmap[(a, b)] = q2t
    # does A's dyad state map onto B's dyad state?
    da, db = dy[a]["state"], dy[b]["state"]
    mapped = q2t.get(da)
    if mapped is None:
        verdict = "DYAD_NOT_IN_ALIGNED_REGION"
        off = ""
    else:
        off = str(mapped - db) if db else ""
        verdict = "DYAD_CORRESPONDS" if db and abs(mapped - db) <= 2 else "DYAD_MAPS_ELSEWHERE"
    rows.append([a, b, prob, ev, score, cols, f"{qs[0]}-{qs[1]}", f"{ts[0]}-{ts[1]}", verdict])
    mapping_rows.append([a, b, str(da or ""), str(db or ""), str(mapped or ""), off,
                         prob, cols, verdict])

with open(f"{TABLES}/g4a_between_family_correspondence.tsv", "w") as f:
    f.write("family_A\tfamily_B\thhalign_probability\thhalign_evalue\thhalign_score\t"
            "aligned_columns\tA_profile_span\tB_profile_span\tdyad_anchor_verdict\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_dyad_anchor_correspondence.tsv", "w") as f:
    f.write("family_A\tfamily_B\tA_dyad_match_state\tB_dyad_match_state\t"
            "A_dyad_mapped_to_B_state\toffset\thhalign_probability\taligned_columns\tverdict\n")
    for r in mapping_rows:
        f.write("\t".join(r) + "\n")

# ------------------------------------------- transitivity / order consistency
tri = []
for a, b, c in itertools.permutations(FAMILIES, 3):
    m1, m2, m3 = pairmap.get((a, b)), pairmap.get((b, c)), pairmap.get((a, c))
    if not (m1 and m2 and m3):
        continue
    agree = tot = 0
    for qa, tb in m1.items():
        if tb in m2 and qa in m3:
            tot += 1
            if abs(m2[tb] - m3[qa]) <= 2:
                agree += 1
    if tot >= 20:
        tri.append([a, b, c, str(tot), str(agree), f"{100*agree/tot:.1f}"])

with open(f"{TABLES}/g4a_transitivity.tsv", "w") as f:
    f.write("family_A\tvia_B\tfamily_C\tn_testable_states\tn_consistent_within_2\t"
            "pct_transitively_consistent\n")
    for r in tri:
        f.write("\t".join(r) + "\n")

# ------------------------------------------------- supported intersection
support = collections.Counter()
for (a, b), m in pairmap.items():
    for qa in m:
        support[(a, qa)] += 1
inter = []
for a in FAMILIES:
    n_other = len(FAMILIES) - 1
    states = [s for (f, s) in support if f == a]
    if not states:
        continue
    hist = collections.Counter(support[(a, s)] for s in states)
    glob = sum(v for k, v in hist.items() if k >= n_other)
    cls = sum(v for k, v in hist.items() if 2 <= k < n_other)
    famonly = sum(v for k, v in hist.items() if k == 1)
    tot_ms = len(read_fasta(f"{WORK}/{a}.deriv.mafft.afa")) and max(
        match_states(read_fasta(f"{WORK}/{a}.deriv.mafft.afa")).values())
    unres = tot_ms - (glob + cls + famonly)
    inter.append([a, str(tot_ms), str(glob), str(cls), str(famonly), str(max(0, unres)),
                  f"{100*glob/tot_ms:.1f}", f"{100*(glob+cls)/tot_ms:.1f}"])

with open(f"{TABLES}/g4a_supported_intersection.tsv", "w") as f:
    f.write("family\tn_match_states\tn_GLOBAL_CANDIDATE\tn_CLASS_LEVEL\tn_FAMILY_LEVEL\t"
            "n_UNRESOLVED\tpct_global\tpct_global_or_class\n")
    for r in inter:
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_dyad_match_states.tsv", "w") as f:
    f.write("family\tmodal_dyad_match_state\tn_seqs_at_that_state\ttotal_dyad_hits_mapped\t"
            "n_distinct_states_carrying_a_dyad\n")
    for k in FAMILIES:
        d = dy[k]
        f.write(f"{k}\t{d['state']}\t{d['n_at']}\t{d['total']}\t{d['distinct']}\n")

print("correspondence complete")
