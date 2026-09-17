#!/usr/bin/env python3
"""g4a — does the catalytic dyad correspond ACROSS families?

Reads the hhalign consensus alignment DIRECTLY. Deliberately does NOT reimplement
hhmake's match-state numbering: an earlier version of this analysis did, got the
numbering wrong, and produced a spurious "the dyad does not correspond" result.
The alignment text is the evidence; nothing is recomputed from it.

Usage: g4a_dyad_check.py <workdir> <tabledir>
"""
import sys, os, re, itertools, collections

WORK, TABLES = sys.argv[1], sys.argv[2]
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
DYAD = re.compile(r"[YyFf].[Dd][Dd]")


def aligned_consensus(path):
    """Concatenate the Q/T Consensus lines of hit 1 into one aligned pair."""
    if not os.path.exists(path):
        return None
    lines = open(path).read().split("\n")
    q, t = [], []
    for i, ln in enumerate(lines):
        if ln.startswith("Q Consensus"):
            m = re.match(r"Q Consensus\s+\d+\s+(\S+)\s+\d+", ln)
            if m:
                q.append(m.group(1))
        elif ln.startswith("T Consensus"):
            m = re.match(r"T Consensus\s+\d+\s+(\S+)\s+\d+", ln)
            if m:
                t.append(m.group(1))
    if not q or len(q) != len(t):
        return None
    if any(len(a) != len(b) for a, b in zip(q, t)):
        return None
    return "".join(q), "".join(t)


rows = []
for a, b in itertools.permutations(FAMILIES, 2):
    ac = aligned_consensus(f"{WORK}/hha_{a}__{b}.hhr")
    if not ac:
        rows.append([a, b, "", "", "", "NO_PARSABLE_ALIGNMENT", ""])
        continue
    Q, T = ac
    qh = list(DYAD.finditer(Q))
    th = list(DYAD.finditer(T))
    if not qh:
        rows.append([a, b, "0", str(len(th)), "", "QUERY_CONSENSUS_HAS_NO_DYAD", ""])
        continue
    verdict, off, detail = "DYAD_NOT_ALIGNED_TO_DYAD", "", ""
    for m in qh:
        # the DD of the query motif sits at aligned columns m.start()+2, +3
        d1, d2 = m.start() + 2, m.start() + 3
        tseg = T[d1:d2 + 1]
        if tseg.upper() == "DD":
            verdict = "DYAD_CORRESPONDS"
            off = "0"
            detail = f"Q[{m.start()}:{m.end()}]={Q[m.start():m.end()]} aligned to T={T[m.start():m.end()]}"
            break
    if verdict != "DYAD_CORRESPONDS" and th:
        # nearest template dyad, in aligned columns
        best = min(th, key=lambda x: abs(x.start() - qh[0].start()))
        off = str(best.start() - qh[0].start())
        verdict = "DYAD_OFFSET_IN_ALIGNMENT"
        detail = (f"Q={Q[qh[0].start():qh[0].end()]} at col {qh[0].start()}; "
                  f"nearest T={T[best.start():best.end()]} at col {best.start()}")
    rows.append([a, b, str(len(qh)), str(len(th)), off, verdict, detail])

with open(f"{TABLES}/g4a_dyad_anchor_correspondence.tsv", "w") as f:
    f.write("family_A\tfamily_B\tn_dyad_motifs_in_A_consensus\tn_in_B_consensus\t"
            "aligned_column_offset\tverdict\tdetail\n")
    for r in rows:
        f.write("\t".join(r) + "\n")

c = collections.Counter(r[5] for r in rows)
for k, v in c.most_common():
    print(f"{k}\t{v}")
print("pairs_tested", len(rows))
