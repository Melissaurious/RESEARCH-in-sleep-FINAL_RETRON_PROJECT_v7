#!/usr/bin/env python3
"""g4a Phase C — supported intersection and transitivity, computed DIRECTLY from the
hhalign consensus alignments.

Supersedes the match-state reimplementation used in the first pass, which was wrong
and produced an all-zero transitivity table and a spurious dyad result. Nothing here
recomputes hhmake's numbering; the alignment text is the evidence.

Coordinates are CONSENSUS INDEX: the 1-based position within a family's own profile
consensus, counting non-gap characters of that family's consensus line.

Usage: g4a_intersection.py <workdir> <tabledir>
"""
import sys, os, re, itertools, collections, statistics

WORK, TABLES = sys.argv[1], sys.argv[2]
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
GAPS = "-."


def aligned_pair(path):
    """(Q_aligned_consensus, T_aligned_consensus, q_start, t_start) for hit 1."""
    if not os.path.exists(path):
        return None
    q, t, qs, ts = [], [], None, None
    for ln in open(path):
        m = re.match(r"Q Consensus\s+(\d+)\s+(\S+)\s+\d+", ln)
        if m:
            if qs is None:
                qs = int(m.group(1))
            q.append(m.group(2))
            continue
        m = re.match(r"T Consensus\s+(\d+)\s+(\S+)\s+\d+", ln)
        if m:
            if ts is None:
                ts = int(m.group(1))
            t.append(m.group(2))
    if not q or len(q) != len(t) or any(len(a) != len(b) for a, b in zip(q, t)):
        return None
    return "".join(q), "".join(t), qs, ts


def pair_map(path):
    """A_consensus_index -> B_consensus_index for aligned (non-gap/non-gap) columns."""
    ap = aligned_pair(path)
    if not ap:
        return None
    Q, T, qs, ts = ap
    qi, ti, m = qs, ts, {}
    for a, b in zip(Q, T):
        qg, tg = a in GAPS, b in GAPS
        if not qg and not tg:
            m[qi] = ti
        if not qg:
            qi += 1
        if not tg:
            ti += 1
    return m


pm = {}
for a, b in itertools.permutations(FAMILIES, 2):
    m = pair_map(f"{WORK}/hha_{a}__{b}.hhr")
    if m:
        pm[(a, b)] = m

# --------------------------------------------------------------- transitivity
tri = []
for a, b, c in itertools.permutations(FAMILIES, 3):
    m_ab, m_bc, m_ac = pm.get((a, b)), pm.get((b, c)), pm.get((a, c))
    if not (m_ab and m_bc and m_ac):
        continue
    tot = agree = 0
    offs = []
    for qa, tb in m_ab.items():
        if tb in m_bc and qa in m_ac:
            tot += 1
            d = m_bc[tb] - m_ac[qa]
            offs.append(d)
            if abs(d) <= 2:
                agree += 1
    if tot >= 20:
        tri.append([a, b, c, str(tot), str(agree), f"{100*agree/tot:.1f}",
                    str(int(statistics.median(offs)))])

with open(f"{TABLES}/g4a_transitivity.tsv", "w") as f:
    f.write("family_A\tvia_B\tfamily_C\tn_testable_positions\tn_consistent_within_2\t"
            "pct_transitively_consistent\tmedian_offset\n")
    for r in tri:
        f.write("\t".join(r) + "\n")

# ------------------------------------------------- supported intersection
rows = []
consensus_len = {}
for a in FAMILIES:
    for b in FAMILIES:
        ap = aligned_pair(f"{WORK}/hha_{a}__{b}.hhr") if a != b else None
        if ap:
            consensus_len[a] = max(consensus_len.get(a, 0), ap[2] + len(ap[0].replace("-", "").replace(".", "")))
for a in FAMILIES:
    sup = collections.Counter()
    for b in FAMILIES:
        if a == b:
            continue
        m = pm.get((a, b))
        if m:
            for qa in m:
                sup[qa] += 1
    if not sup:
        continue
    n_other = sum(1 for b in FAMILIES if b != a and (a, b) in pm)
    glob = sum(1 for v in sup.values() if v == n_other)
    cls = sum(1 for v in sup.values() if 2 <= v < n_other)
    fam = sum(1 for v in sup.values() if v == 1)
    covered = len(sup)
    span = max(sup) - min(sup) + 1
    rows.append([a, str(n_other), str(covered), str(span), str(glob), str(cls), str(fam),
                 f"{100*glob/covered:.1f}", f"{100*(glob+cls)/covered:.1f}",
                 f"{min(sup)}-{max(sup)}"])

with open(f"{TABLES}/g4a_supported_intersection.tsv", "w") as f:
    f.write("family\tn_partner_families\tn_consensus_positions_aligned_to_any_partner\t"
            "span_of_those_positions\tn_GLOBAL_CANDIDATE_all_partners\tn_CLASS_LEVEL_2_to_n-1\t"
            "n_FAMILY_LEVEL_exactly_1\tpct_global_of_covered\tpct_global_or_class_of_covered\t"
            "consensus_index_range\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

# global-candidate core as a per-family interval
core = []
for a in FAMILIES:
    sup = collections.Counter()
    for b in FAMILIES:
        if a != b and (a, b) in pm:
            for qa in pm[(a, b)]:
                sup[qa] += 1
    n_other = sum(1 for b in FAMILIES if b != a and (a, b) in pm)
    g = sorted(k for k, v in sup.items() if v == n_other)
    if g:
        core.append([a, str(len(g)), f"{g[0]}-{g[-1]}", str(g[-1] - g[0] + 1),
                     f"{100*len(g)/(g[-1]-g[0]+1):.1f}"])

with open(f"{TABLES}/g4a_global_core_extent.tsv", "w") as f:
    f.write("family\tn_global_candidate_positions\tconsensus_index_span\tspan_width\t"
            "pct_of_span_that_is_global\n")
    for r in core:
        f.write("\t".join(r) + "\n")

print("intersection complete; pairs mapped:", len(pm))
