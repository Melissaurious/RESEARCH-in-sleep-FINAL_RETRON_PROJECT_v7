#!/usr/bin/env python3
"""UG5 whole-family holdout gate, v2 — PER-SEQUENCE evaluation.

Operator-authorised rework (PREDECLARATION_ADDENDUM_2 §7). The v1 gate mapped an AGGREGATE
profile per UG5 subset, so monotone order and zero ambiguity were largely guaranteed by the
one-to-one, order-preserving pairwise map — partly tautological.

v2 instead projects the frozen frame onto EACH UG5 SEQUENCE with hmmsearch, where the search
CAN emit out-of-order, duplicated or missing anchors. Order and ambiguity therefore become
falsifiable. Every component is evaluated, including the singleton. All 150 anchor
coordinates are landed. Abstention is explicit.

Usage: ug5_gate_v2.py <g4a_repaired_work> <workdir> <tabledir>
"""
import sys, os, re, random, itertools, collections, statistics
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/"
                   "results/rt07_g4a_repaired/scripts")
from repaired_lib import *          # noqa

G4AWORK, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
HELDOUT = "UG5"
REFERENCE_FAMILY = "GII"
ANCHOR_WINDOW = 5          # +/- residues: an anchor is "placed" if a hit envelope covers it
random.seed(20260916)
os.makedirs(WORK, exist_ok=True); os.makedirs(TABLES, exist_ok=True)
aud = Audit()

elig = eligible_by_family()
ug5 = elig[HELDOUT]
ug5_ids, ug5_seqs = set(ug5), set(ug5.values())

# ---------------------------------------------------------- 1 provenance (unchanged, fails closed)
inputs = []
for fam in CONSTRUCTION:
    inputs += [f"{G4AWORK}/{fam}.derivation.faa", f"{G4AWORK}/{fam}.deriv.mafft.afa",
               f"{G4AWORK}/{fam}.deriv.hmm", f"{G4AWORK}/{fam}.deriv.hhm"]
prov, fail = [], False
for p in inputs:
    if not os.path.exists(p):
        sys.exit("FAIL CLOSED: missing construction input " + p)
    txt = open(p, errors="replace").read()
    by_id = any(i in txt for i in ug5_ids)
    by_seq = False
    if p.endswith((".faa", ".afa")):
        for s in read_fasta(p).values():
            if clean(s) in ug5_seqs:
                by_seq = True; break
    present = by_id or by_seq
    fail |= present
    prov.append([os.path.basename(p), sha256(p), "YES" if by_id else "NO",
                 "YES" if by_seq else "NO", "TRUE" if present else "FALSE"])
with open(f"{TABLES}/ug5_holdout_provenance_audit.tsv", "w") as f:
    f.write("construction_input\tsha256_at_gate_time\tUG5_id_found\tUG5_sequence_found\t"
            "UG5_GENEALOGY_PRESENT\n")
    for r in prov: f.write("\t".join(r) + "\n")
if fail:
    sys.exit("FAIL CLOSED: UG5 genealogy present in a construction input")

# --------------------------------------------- 2 freeze the frame and LAND ALL COORDINATES
pm = {}
for a, b in itertools.permutations(CONSTRUCTION, 2):
    o = f"{WORK}/con_{a}__{b}.hhr"
    run([BIN + "hhalign", "-i", f"{G4AWORK}/{a}.deriv.hhm",
         "-t", f"{G4AWORK}/{b}.deriv.hhm", "-o", o])
    m = pair_map(o)
    if m: pm[(a, b)] = m
sup = collections.Counter()
for b in CONSTRUCTION:
    if b != REFERENCE_FAMILY and (REFERENCE_FAMILY, b) in pm:
        for q in pm[(REFERENCE_FAMILY, b)]: sup[q] += 1
n_other = sum(1 for b in CONSTRUCTION if b != REFERENCE_FAMILY and (REFERENCE_FAMILY, b) in pm)
ANCHORS = sorted(k for k, v in sup.items() if v == n_other)
if not ANCHORS: sys.exit("FAIL CLOSED: no frozen anchors")

# contiguous runs (the reviewer's point: these are not 150 independent evidence units)
runs, cur = [], [ANCHORS[0]]
for x in ANCHORS[1:]:
    if x == cur[-1] + 1: cur.append(x)
    else: runs.append(cur); cur = [x]
runs.append(cur)
with open(f"{TABLES}/ug5_frozen_anchor_coordinates.tsv", "w") as f:
    f.write("anchor_index\treference_family\treference_consensus_coordinate\trun_id\trun_length\n")
    for ri, r in enumerate(runs, 1):
        for a in r:
            f.write(f"{ANCHORS.index(a)+1}\t{REFERENCE_FAMILY}\t{a}\t{ri}\t{len(r)}\n")
print(f"frozen anchors: {len(ANCHORS)} in {len(runs)} contiguous runs, span {ANCHORS[0]}-{ANCHORS[-1]}")

# ------------------------------------------------------------------ 3 UG5 split (all components)
pairs5 = all_vs_all(ug5, WORK, "UG5")
comps5 = components(list(ug5), pairs5)
evalref = comps5[0]
challenge = [i for c in comps5[1:] for i in c]
comp_of = {i: ci for ci, c in enumerate(comps5) for i in c}
role5 = {i: ("evaluation_reference" if i in set(evalref) else "challenge") for i in ug5}
with open(f"{TABLES}/ug5_evaluation_split.tsv", "w") as f:
    f.write("sequence_id\tsubset\tcomponent_index\tcomponent_size\tlength_aa\thas_dyad\tn_dyad_hits\n")
    for ci, c in enumerate(comps5):
        for i in sorted(c):
            h = DYAD.findall(ug5[i])
            f.write(f"{i}\t{role5[i]}\t{ci}\t{len(c)}\t{len(ug5[i])}\t"
                    f"{'YES' if h else 'NO'}\t{len(h)}\n")
rows = []
for q, t, fi, qc, tc in pairs5:
    if role5[q] != role5[t] and fi >= 0.20:
        rows.append([q, role5[q], t, role5[t], f"{fi:.4f}", f"{qc:.3f}", f"{tc:.3f}",
                     "YES" if (fi >= LINK_IDENTITY and min(qc, tc) >= LINK_COVERAGE) else "NO"])
with open(f"{TABLES}/ug5_split_pairwise_audit.tsv", "w") as f:
    f.write("query_id\tquery_subset\treference_id\treference_subset\tidentity\t"
            "query_coverage\treference_coverage\tviolates_link_rule\n")
    for r in sorted(rows, key=lambda x: (-float(x[4]), x[0], x[2])): f.write("\t".join(r) + "\n")
if any(r[7] == "YES" for r in rows):
    sys.exit("FAIL CLOSED: UG5 cross-subset link-rule violation")

# ------------------- 4 PER-SEQUENCE projection: reference-family HMM vs each UG5 sequence
# The reference HMM's match states are its own; map them to REFERENCE_FAMILY consensus coords
# via the hhm LENG ordering (hmmbuild and hhmake both number match states 1..LENG in order).
per_seq, notplaced = [], []
for sid, seq in sorted(ug5.items()):
    fp = f"{WORK}/seq_{abs(hash(sid))%10**9}.faa"
    write_fasta({sid: seq}, fp)
    dom = f"{WORK}/dom_{abs(hash(sid))%10**9}.tbl"
    run([BIN + "hmmsearch", "--max", "-E", HMMSEARCH_E, "--noali",
         "--domtblout", dom, f"{G4AWORK}/{REFERENCE_FAMILY}.deriv.hmm", fp])
    envs = []
    for line in open(dom):
        if line.startswith("#"): continue
        p = line.split()
        # hmm coords 16,17 ; ali coords 18,19 ; env 20,21 ; score 14
        envs.append((int(p[15]), int(p[16]), int(p[17]), int(p[18]), float(p[13])))
    if not envs:
        notplaced.append([sid, role5[sid], str(comp_of[sid]), "NO_DOMAIN_HIT"])
        per_seq.append([sid, role5[sid], str(comp_of[sid]), str(len(ANCHORS)), "0", "0.0",
                        "0", "NOT_PLACED", "NOT_PLACED", "", ""])
        continue
    placed, dup = {}, collections.Counter()
    for hs, he, as_, ae, sc in envs:
        for a in ANCHORS:
            if hs - ANCHOR_WINDOW <= a <= he + ANCHOR_WINDOW:
                frac = (a - hs) / max(1, (he - hs))
                pos = int(round(as_ + frac * (ae - as_)))
                dup[a] += 1
                if a not in placed or sc > placed[a][1]:
                    placed[a] = (pos, sc)
    if not placed:
        notplaced.append([sid, role5[sid], str(comp_of[sid]), "HIT_BUT_NO_ANCHOR_COVERED"])
        per_seq.append([sid, role5[sid], str(comp_of[sid]), str(len(ANCHORS)), "0", "0.0",
                        "0", "NOT_PLACED", "NOT_PLACED", "", ""])
        continue
    order = [placed[a][0] for a in sorted(placed)]
    inversions = sum(1 for i in range(len(order) - 1) if order[i + 1] <= order[i])
    ambiguous = sum(1 for a in placed if dup[a] > 1)
    dy = DYAD.search(seq)
    dyad_in = ""
    if dy:
        dpos = dy.start() + 1
        dyad_in = "YES" if any(abs(p - dpos) <= 10 for p, _ in placed.values()) else "NO"
    per_seq.append([sid, role5[sid], str(comp_of[sid]), str(len(ANCHORS)), str(len(placed)),
                    f"{100*len(placed)/len(ANCHORS):.1f}", str(inversions),
                    "MONOTONE" if inversions == 0 else f"NON_MONOTONE({inversions})",
                    "NONE" if ambiguous == 0 else f"AMBIGUOUS({ambiguous})",
                    dyad_in, f"{max(s for _, s in placed.values()):.1f}"])

with open(f"{TABLES}/ug5_per_sequence_mapping.tsv", "w") as f:
    f.write("sequence_id\tsubset\tcomponent_index\tn_frozen_anchors\tn_anchors_placed\t"
            "pct_anchors_placed\tn_order_inversions\torder_verdict\tambiguity_verdict\t"
            "dyad_within_placed_anchors\tbest_domain_bitscore\n")
    for r in per_seq: f.write("\t".join(r) + "\n")
with open(f"{TABLES}/ug5_abstention.tsv", "w") as f:
    f.write("sequence_id\tsubset\tcomponent_index\tabstention_reason\n")
    for r in notplaced: f.write("\t".join(r) + "\n")

# per-component summary, INCLUDING the singleton
comp_rows = []
for ci, c in enumerate(comps5):
    sub = [r for r in per_seq if r[2] == str(ci)]
    pl = [int(r[4]) for r in sub]
    mono = sum(1 for r in sub if r[7] == "MONOTONE")
    amb = sum(1 for r in sub if r[8] != "NONE")
    dyy = sum(1 for r in sub if r[9] == "YES")
    comp_rows.append([str(ci), "evaluation_reference" if ci == 0 else "challenge",
                      str(len(c)), f"{statistics.median(pl):.0f}",
                      f"{100*statistics.median(pl)/len(ANCHORS):.1f}",
                      str(mono), str(amb), str(dyy),
                      str(sum(1 for r in sub if r[7] == "NOT_PLACED"))])
with open(f"{TABLES}/ug5_component_summary.tsv", "w") as f:
    f.write("component_index\tsubset\tn_sequences\tmedian_anchors_placed\t"
            "median_pct_placed\tn_monotone\tn_with_ambiguity\tn_dyad_within_anchors\t"
            "n_abstained\n")
    for r in comp_rows: f.write("\t".join(r) + "\n")

# coordinate stability across components (per-anchor spread of placed positions, normalised)
byanchor = collections.defaultdict(list)
for sid, seq in sorted(ug5.items()):
    pass
stab = []
placed_by_seq = {}
for r in per_seq:
    placed_by_seq[r[0]] = r
# recompute per-anchor normalised positions for stability
norm = collections.defaultdict(list)
for sid, seq in sorted(ug5.items()):
    dom = f"{WORK}/dom_{abs(hash(sid))%10**9}.tbl"
    if not os.path.exists(dom): continue
    envs = []
    for line in open(dom):
        if line.startswith("#"): continue
        p = line.split()
        envs.append((int(p[15]), int(p[16]), int(p[17]), int(p[18]), float(p[13])))
    best = {}
    for hs, he, as_, ae, sc in envs:
        for a in ANCHORS:
            if hs - ANCHOR_WINDOW <= a <= he + ANCHOR_WINDOW:
                frac = (a - hs) / max(1, (he - hs))
                pos = (as_ + frac * (ae - as_)) / len(seq)
                if a not in best or sc > best[a][1]: best[a] = (pos, sc)
    for a, (pos, _) in best.items(): norm[a].append(pos)
for a in sorted(norm):
    v = norm[a]
    if len(v) >= 3:
        stab.append([str(a), str(len(v)), f"{statistics.median(v):.4f}",
                     f"{statistics.pstdev(v):.4f}", f"{max(v)-min(v):.4f}"])
with open(f"{TABLES}/ug5_coordinate_stability.tsv", "w") as f:
    f.write("frozen_anchor_reference_coord\tn_ug5_sequences_placing_it\t"
            "median_normalised_position\tstdev_normalised\trange_normalised\n")
    for r in stab: f.write("\t".join(r) + "\n")

# ---------------------------------------------------- 5 decoy: shuffled UG5 sequences
dec = []
for rep in range(3):                       # multiple replicates, per the reviewer
    random.seed(20260916 + rep)
    nplaced = []
    for sid, seq in sorted(ug5.items()):
        s = list(seq.upper()); random.shuffle(s)
        fp = f"{WORK}/dec_{rep}.faa"; write_fasta({sid: "".join(s)}, fp)
        dom = f"{WORK}/dec_{rep}.tbl"
        run([BIN + "hmmsearch", "--max", "-E", HMMSEARCH_E, "--noali",
             "--domtblout", dom, f"{G4AWORK}/{REFERENCE_FAMILY}.deriv.hmm", fp])
        cov = set()
        for line in open(dom):
            if line.startswith("#"): continue
            p = line.split()
            hs, he = int(p[15]), int(p[16])
            cov |= {a for a in ANCHORS if hs - ANCHOR_WINDOW <= a <= he + ANCHOR_WINDOW}
        nplaced.append(len(cov))
    dec.append([f"SHUF_rep{rep}", str(len(ug5)), f"{statistics.median(nplaced):.0f}",
                f"{100*statistics.median(nplaced)/len(ANCHORS):.1f}", str(max(nplaced))])
real_med = statistics.median([int(r[4]) for r in per_seq])
with open(f"{TABLES}/ug5_decoy_controls.tsv", "w") as f:
    f.write("control\tn_sequences\tmedian_anchors_placed\tmedian_pct_placed\tmax_anchors_placed\n")
    f.write(f"REAL_UG5\t{len(ug5)}\t{real_med:.0f}\t{100*real_med/len(ANCHORS):.1f}\t"
            f"{max(int(r[4]) for r in per_seq)}\n")
    for r in dec: f.write("\t".join(r) + "\n")

aud.write(f"{TABLES}/ug5_audit.tsv")
print("UG5 gate v2 complete")
