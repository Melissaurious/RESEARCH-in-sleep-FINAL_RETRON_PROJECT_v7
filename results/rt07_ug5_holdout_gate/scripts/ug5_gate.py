#!/usr/bin/env python3
"""UG5 whole-family holdout gate. Frozen per control/ug5_holdout_predeclaration.md.

Construction uses SIX families (UG3 retained, UG5 totally absent). UG5 is examined only
after the frame is frozen. Provenance is audited by CONTENT, not by filename.

Usage: ug5_gate.py <g4a_repaired_work> <workdir> <tabledir>
"""
import sys, os, re, random, itertools, collections, statistics
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/"
                   "results/rt07_g4a_repaired/scripts")
from repaired_lib import *          # noqa

G4AWORK, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
HELDOUT = "UG5"
REFERENCE_FAMILY = "GII"            # declared before execution
random.seed(20260916)
os.makedirs(WORK, exist_ok=True)
os.makedirs(TABLES, exist_ok=True)
aud = Audit()

elig = eligible_by_family()
ug5_ids = set(elig[HELDOUT])
ug5_seqs = set(elig[HELDOUT].values())

# ---------------------------------------------------------------- 1 provenance audit
prov = []
inputs = []
for fam in CONSTRUCTION:
    inputs += [f"{G4AWORK}/{fam}.derivation.faa", f"{G4AWORK}/{fam}.deriv.mafft.afa",
               f"{G4AWORK}/{fam}.deriv.hmm", f"{G4AWORK}/{fam}.deriv.hhm"]
fail = False
for p in inputs:
    if not os.path.exists(p):
        aud.add("construction_input_missing", "present", p, "provenance audit",
                "cannot audit an absent input", "FAIL CLOSED", "YES")
        sys.exit("FAIL CLOSED: missing construction input " + p)
    txt = open(p, errors="replace").read()
    by_id = any(i in txt for i in ug5_ids)
    # sequence-level check on the fasta/alignment inputs
    by_seq = False
    if p.endswith((".faa", ".afa")):
        for s in read_fasta(p).values():
            if clean(s) in ug5_seqs:
                by_seq = True
                break
    present = by_id or by_seq
    if present:
        fail = True
    prov.append([os.path.basename(p), sha256(p), "YES" if by_id else "NO",
                 "YES" if by_seq else "NO",
                 "TRUE" if present else "FALSE"])
with open(f"{TABLES}/ug5_holdout_provenance_audit.tsv", "w") as f:
    f.write("construction_input\tsha256\tUG5_id_found_in_content\tUG5_sequence_found_in_content\t"
            "UG5_GENEALOGY_PRESENT\n")
    for r in prov:
        f.write("\t".join(r) + "\n")
if fail:
    aud.add("ug5_genealogy", "UG5_GENEALOGY_PRESENT=FALSE for every input", "TRUE somewhere",
            "provenance audit", "the holdout is not genuine", "FAIL CLOSED", "YES")
    aud.write(f"{TABLES}/ug5_audit.tsv")
    sys.exit("FAIL CLOSED: UG5 genealogy present in a construction input")

# ------------------------------------------------- 2 freeze the six-family shared frame
pm = {}
for a, b in itertools.permutations(CONSTRUCTION, 2):
    o = f"{WORK}/con_{a}__{b}.hhr"
    run([BIN + "hhalign", "-i", f"{G4AWORK}/{a}.deriv.hhm",
         "-t", f"{G4AWORK}/{b}.deriv.hhm", "-o", o])
    m = pair_map(o)
    if m:
        pm[(a, b)] = m

sup = collections.Counter()
for b in CONSTRUCTION:
    if b != REFERENCE_FAMILY and (REFERENCE_FAMILY, b) in pm:
        for q in pm[(REFERENCE_FAMILY, b)]:
            sup[q] += 1
n_other = sum(1 for b in CONSTRUCTION if b != REFERENCE_FAMILY
              and (REFERENCE_FAMILY, b) in pm)
ANCHORS = sorted(k for k, v in sup.items() if v == n_other)
if not ANCHORS:
    aud.add("frozen_anchors", ">0 ALL_PARTNERS anchors", 0, "frame freeze",
            "no shared frame to test", "FAIL CLOSED", "n/a")
    sys.exit("FAIL CLOSED: no frozen anchors")
print(f"frozen anchors (ALL_PARTNERS across {n_other} partners, {REFERENCE_FAMILY} coords): "
      f"{len(ANCHORS)}  span {ANCHORS[0]}-{ANCHORS[-1]}")

# ------------------------------------------------------------- 3 UG5 evaluation split
pairs5 = all_vs_all(elig[HELDOUT], WORK, "UG5")
comps5 = components(list(elig[HELDOUT]), pairs5)
evalref = comps5[0]
challenge = [i for c in comps5[1:] for i in c]
role5 = {i: "evaluation_reference" for i in evalref}
role5.update({i: "challenge" for i in challenge})
with open(f"{TABLES}/ug5_evaluation_split.tsv", "w") as f:
    f.write("sequence_id\tsubset\tcomponent_index\tlength_aa\thas_dyad\tn_dyad_hits\n")
    for ci, c in enumerate(comps5):
        for i in sorted(c):
            s = elig[HELDOUT][i]
            h = DYAD.findall(s)
            f.write(f"{i}\t{role5[i]}\t{ci}\t{len(s)}\t{'YES' if h else 'NO'}\t{len(h)}\n")
rows = []
for q, t, fi, qc, tc in pairs5:
    rq, rt = role5.get(q), role5.get(t)
    if rq and rt and rq != rt and fi >= 0.20:
        rows.append([q, rq, t, rt, f"{fi:.4f}", f"{qc:.3f}", f"{tc:.3f}",
                     "YES" if (fi >= LINK_IDENTITY and min(qc, tc) >= LINK_COVERAGE) else "NO"])
with open(f"{TABLES}/ug5_split_pairwise_audit.tsv", "w") as f:
    f.write("query_id\tquery_subset\treference_id\treference_subset\tidentity\t"
            "query_coverage\treference_coverage\tviolates_link_rule\n")
    for r in sorted(rows, key=lambda x: -float(x[4])):
        f.write("\t".join(r) + "\n")
mx = max((float(r[4]) for r in rows), default=0.0)
viol = sum(1 for r in rows if r[7] == "YES")
if viol:
    aud.add("ug5_split_separation", "0 cross-subset pairs above the link rule", viol,
            "UG5 split", "the UG5 challenge subset is not independent of the reference subset",
            "FAIL CLOSED", "YES")
    sys.exit("FAIL CLOSED: UG5 cross-subset link-rule violations")

# ------------------------------------- 4 project the frozen frame onto UG5 (and decoys)
def ug5_profile(ids, tag):
    write_fasta({i: elig[HELDOUT][i] for i in ids}, f"{WORK}/{tag}.faa")
    r = run([BIN + "mafft", "--localpair", "--maxiterate", "1000", "--quiet",
             "--thread", "1", f"{WORK}/{tag}.faa"])
    open(f"{WORK}/{tag}.afa", "w").write(r.stdout)
    run([BIN + "hhmake", "-i", f"{WORK}/{tag}.afa", "-o", f"{WORK}/{tag}.hhm",
         "-name", tag, "-M", HHMAKE_M])
    return f"{WORK}/{tag}.hhm"

def shuffled_profile(ids, tag):
    d = {}
    for i in ids:
        s = list(elig[HELDOUT][i].upper())
        random.shuffle(s)
        d[i] = "".join(s)
    write_fasta(d, f"{WORK}/{tag}.faa")
    r = run([BIN + "mafft", "--localpair", "--maxiterate", "1000", "--quiet",
             "--thread", "1", f"{WORK}/{tag}.faa"])
    open(f"{WORK}/{tag}.afa", "w").write(r.stdout)
    run([BIN + "hhmake", "-i", f"{WORK}/{tag}.afa", "-o", f"{WORK}/{tag}.hhm",
         "-name", tag, "-M", HHMAKE_M])
    return f"{WORK}/{tag}.hhm"

targets = {"UG5_challenge": ug5_profile(challenge, "UG5_challenge"),
           "UG5_evalref": ug5_profile(evalref, "UG5_evalref"),
           "UG5_challenge_SHUF": shuffled_profile(challenge, "UG5_challenge_SHUF"),
           "UG5_evalref_SHUF": shuffled_profile(evalref, "UG5_evalref_SHUF")}
# per-component profiles for coordinate stability (C)
for ci, c in enumerate(comps5[1:], start=1):
    if len(c) >= 3:
        targets[f"UG5_comp{ci}"] = ug5_profile(c, f"UG5_comp{ci}")

transfer, order_rows, stab_rows, amb_rows, decoy_rows = [], [], [], [], []
for tname, thhm in targets.items():
    o = f"{WORK}/proj_{REFERENCE_FAMILY}__{tname}.hhr"
    run([BIN + "hhalign", "-i", f"{G4AWORK}/{REFERENCE_FAMILY}.deriv.hhm",
         "-t", thhm, "-o", o])
    h = hhr_header(o)
    m = pair_map(o) or {}
    mapped = [a for a in ANCHORS if a in m]
    coords = [m[a] for a in mapped]
    monotone = all(coords[i] < coords[i + 1] for i in range(len(coords) - 1))
    row = [tname, "DECOY" if "SHUF" in tname else "REAL",
           str(len(ANCHORS)), str(len(mapped)),
           f"{100*len(mapped)/len(ANCHORS):.1f}",
           h[0] if h else "", h[1] if h else "", h[3] if h else ""]
    transfer.append(row)
    order_rows.append([tname, "DECOY" if "SHUF" in tname else "REAL", str(len(mapped)),
                       "YES" if monotone else "NO",
                       f"{coords[0]}-{coords[-1]}" if coords else ""])
    if "SHUF" in tname:
        decoy_rows.append([tname, h[0] if h else "", str(len(mapped)),
                           f"{100*len(mapped)/len(ANCHORS):.1f}"])
    # ambiguity: how many anchors map to a target position also claimed by another anchor
    inv = collections.Counter(m[a] for a in mapped)
    amb_rows.append([tname, str(len(mapped)),
                     str(sum(1 for a in mapped if inv[m[a]] > 1)),
                     f"{100*sum(1 for a in mapped if inv[m[a]] > 1)/max(1,len(mapped)):.1f}"])

# C: coordinate stability across held-out UG5 components
comp_targets = [t for t in targets if t.startswith("UG5_comp")]
percomp = {}
for t in comp_targets + ["UG5_challenge"]:
    m = pair_map(f"{WORK}/proj_{REFERENCE_FAMILY}__{t}.hhr") or {}
    percomp[t] = {a: m[a] for a in ANCHORS if a in m}
common = set.intersection(*[set(v) for v in percomp.values()]) if len(percomp) > 1 else set()
for a in sorted(common):
    vals = [percomp[t][a] for t in percomp]
    stab_rows.append([str(a), str(len(vals)), str(min(vals)), str(max(vals)),
                      str(max(vals) - min(vals)),
                      f"{statistics.pstdev(vals):.2f}" if len(vals) > 1 else "0"])

for name, path, hdr in [
        ("ug5_anchor_transfer.tsv", transfer,
         "target\ttarget_kind\tn_frozen_anchors\tn_anchors_mapped\tpct_anchors_mapped\t"
         "hhalign_probability\thhalign_evalue\taligned_columns\n"),
        ("ug5_anchor_order.tsv", order_rows,
         "target\ttarget_kind\tn_anchors_mapped\tmonotone_order\tmapped_coordinate_span\n"),
        ("ug5_coordinate_stability.tsv", stab_rows,
         "frozen_anchor_reference_coord\tn_ug5_subsets_mapping_it\tmin_mapped\tmax_mapped\t"
         "range\tstdev\n"),
        ("ug5_mapping_ambiguity.tsv", amb_rows,
         "target\tn_anchors_mapped\tn_anchors_sharing_a_target_position\tpct_ambiguous\n"),
        ("ug5_decoy_controls.tsv", decoy_rows,
         "decoy_target\thhalign_probability\tn_anchors_mapped\tpct_anchors_mapped\n")]:
    with open(f"{TABLES}/{name}", "w") as f:
        f.write(hdr)
        for r in path:
            f.write("\t".join(str(x) for x in r) + "\n")

with open(f"{TABLES}/ug5_frozen_anchors.tsv", "w") as f:
    f.write(f"reference_family\t{REFERENCE_FAMILY}\n")
    f.write(f"n_partner_families\t{n_other}\n")
    f.write(f"n_frozen_anchors\t{len(ANCHORS)}\n")
    f.write(f"anchor_coordinate_span\t{ANCHORS[0]}-{ANCHORS[-1]}\n")
    f.write(f"ug5_evaluation_reference_n\t{len(evalref)}\n")
    f.write(f"ug5_challenge_n\t{len(challenge)}\n")
    f.write(f"max_cross_subset_identity\t{mx:.4f}\n")

aud.write(f"{TABLES}/ug5_audit.tsv")
print("UG5 gate complete")
