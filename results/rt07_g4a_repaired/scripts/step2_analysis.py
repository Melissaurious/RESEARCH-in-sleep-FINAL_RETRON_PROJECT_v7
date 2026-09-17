#!/usr/bin/env python3
"""g4a REPAIRED step 2 — alignments, de novo profiles, correspondence, dyad, transitivity,
supported intersection, decoy controls. All calls fail closed.

Repairs applied here:
  * dyad mapped through EACH sequence's own alignment row (the reference-map bug is gone)
  * the superseded match-state dyad verdict is NOT produced at all
  * the aligner measure is renamed per_column_entropy_difference_MAFFT_vs_MUSCLE
  * GLOBAL_CANDIDATE -> ALL_PARTNERS, CLASS_LEVEL -> MULTI_FAMILY
  * both denominators reported
  * transfer reported ONLY for INDEPENDENT_CHALLENGE families

Usage: step2_analysis.py <workdir> <tabledir>
"""
import sys, os, re, collections, statistics, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repaired_lib import *          # noqa

WORK, TABLES = sys.argv[1], sys.argv[2]
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
aud = Audit()

indep = {}
for l in open(f"{TABLES}/g4a_repaired_family_selection.tsv"):
    p = l.rstrip("\n").split("\t")
    if p[0] != "family":
        indep[p[0]] = p[4]

# ------------------------------------------------------------------ alignments
stab, anchor_rows, dyadinfo = [], [], {}
for fam in FAMILIES:
    dp = f"{WORK}/{fam}.derivation.faa"
    a1f, a2f = f"{WORK}/{fam}.deriv.mafft.afa", f"{WORK}/{fam}.deriv.muscle.afa"
    r = run([BIN + "mafft", "--localpair", "--maxiterate", "1000", "--quiet",
             "--thread", "1", dp])
    open(a1f, "w").write(r.stdout)
    run([BIN + "muscle", "-align", dp, "-output", a2f])
    a1, a2 = read_fasta(a1f), read_fasta(a2f)

    def colstats(aln):
        ids = list(aln)
        L = len(aln[ids[0]])
        out = []
        for c in range(L):
            col = [aln[i][c].upper() for i in ids]
            ng = [x for x in col if x not in GAPS]
            gap = 1 - len(ng) / len(col)
            if ng:
                cnt = collections.Counter(ng)
                tot = len(ng)
                ent = -sum((v / tot) * (v / tot and __import__("math").log2(v / tot))
                           for v in cnt.values())
                out.append(dict(col=c + 1, gap=gap, ent=ent,
                                mx=cnt.most_common(1)[0][1] / tot,
                                modal=cnt.most_common(1)[0][0]))
            else:
                out.append(dict(col=c + 1, gap=gap, ent=float("nan"), mx=0.0, modal="-"))
        return out

    s1, s2 = colstats(a1), colstats(a2)

    # --- REPAIRED: each sequence's dyad mapped through ITS OWN alignment row
    dyadcol = collections.Counter()
    for sid, gapped in a1.items():
        plain = gapped.replace("-", "").replace(".", "").upper()
        u2c, u = {}, 0
        for c, ch in enumerate(gapped, 1):
            if ch not in GAPS:
                u += 1
                u2c[u] = c
        for mm in DYAD.finditer(plain):
            c = u2c.get(mm.start() + 1)
            if c:
                dyadcol[c] += 1
    dyadinfo[fam] = dyadcol

    ref = sorted(a1)[0]
    def ungapped_index(seq, c):
        return None if seq[c - 1] in GAPS else sum(1 for x in seq[:c] if x not in GAPS)
    m2 = {}
    for c in range(1, len(a2[ref]) + 1):
        u = ungapped_index(a2[ref], c)
        if u:
            m2[u] = c

    ranked = sorted(s1, key=lambda r: (r["gap"], r["ent"] if r["ent"] == r["ent"] else 9))
    for rank, rr in enumerate(ranked[:40], 1):
        c = rr["col"]
        u = ungapped_index(a1[ref], c)
        d = ""
        if u and u in m2 and s2[m2[u] - 1]["ent"] == s2[m2[u] - 1]["ent"]:
            d = f"{abs(s2[m2[u]-1]['ent'] - rr['ent']):.3f}"
        lo, hi = max(0, c - 4), min(len(s1), c + 3)
        ctx = [x["ent"] for x in s1[lo:hi] if x["ent"] == x["ent"]]
        anchor_rows.append([fam, str(rank), str(c), str(u or ""), rr["modal"],
                            f"{rr['gap']:.3f}", f"{rr['ent']:.3f}", f"{rr['mx']:.3f}",
                            f"{statistics.mean(ctx):.3f}" if ctx else "", d,
                            str(dyadcol.get(c, 0))])

    ents1 = [r["ent"] for r in s1 if r["ent"] == r["ent"]]
    ents2 = [r["ent"] for r in s2 if r["ent"] == r["ent"]]
    stab.append([fam, str(len(a1)), str(len(s1)), str(len(s2)),
                 str(sum(1 for r in s1 if r["gap"] == 0)),
                 f"{statistics.median(ents1):.3f}", f"{statistics.median(ents2):.3f}",
                 str(len(dyadcol)),
                 str(dyadcol.most_common(1)[0][0]) if dyadcol else "",
                 str(dyadcol.most_common(1)[0][1]) if dyadcol else "0",
                 str(sum(dyadcol.values())), str(len(a1))])

    sto = f"{WORK}/{fam}.deriv.sto"
    run([BIN + "esl-reformat", "-o", sto, "stockholm", a1f])
    run([BIN + "hmmbuild", "--amino", "-n", f"g4a_{fam}", f"{WORK}/{fam}.deriv.hmm", sto])
    run([BIN + "hhmake", "-i", a1f, "-o", f"{WORK}/{fam}.deriv.hhm",
         "-name", f"g4a_{fam}", "-M", HHMAKE_M])

with open(f"{TABLES}/g4a_repaired_alignment_stability.tsv", "w") as f:
    f.write("family\tn_derivation\tmafft_columns\tmuscle_columns\tn_gapless_columns\t"
            "median_entropy_mafft\tmedian_entropy_muscle\tn_distinct_dyad_columns\t"
            "modal_dyad_column\tn_seqs_at_modal_dyad_column\ttotal_dyad_hits\t"
            "denominator_n_derivation_sequences\n")
    for r in stab:
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_repaired_anchor_candidates.tsv", "w") as f:
    f.write("family\tevidence_rank\talignment_column\tref_residue_index\tmodal_residue\t"
            "gap_fraction\tshannon_entropy\tmax_residue_fraction\tcontext_mean_entropy\t"
            "per_column_entropy_difference_MAFFT_vs_MUSCLE\tn_dyad_hits_in_this_column\n")
    for r in anchor_rows:
        f.write("\t".join(r) + "\n")

# ------------------------------------------------- pairwise correspondence (fail closed)
corr, pm = [], {}
for a, b in itertools.permutations(FAMILIES, 2):
    out = f"{WORK}/hha_{a}__{b}.hhr"
    run([BIN + "hhalign", "-i", f"{WORK}/{a}.deriv.hhm",
         "-t", f"{WORK}/{b}.deriv.hhm", "-o", out])           # check=True
    h = hhr_header(out)
    if not h:
        aud.add(f"hhalign.{a}_{b}", "a parsable hit 1", "no hit parsed", "step2",
                "a missing correspondence would silently become an empty cell",
                "recorded explicitly as NO_HIT", "NO")
        corr.append([a, b, "", "", "", "", "NO_HIT"])
        continue
    m = pair_map(out)
    if m:
        pm[(a, b)] = m
    corr.append([a, b, h[0], h[1], h[2], h[3], "OK"])

with open(f"{TABLES}/g4a_repaired_between_family_correspondence.tsv", "w") as f:
    f.write("family_A\tfamily_B\thhalign_probability\thhalign_evalue\thhalign_score\t"
            "aligned_columns\tstatus\n")
    for r in corr:
        f.write("\t".join(r) + "\n")

# --------------------------------------------------- canonical dyad (direct from alignment)
dy = []
for a, b in itertools.permutations(FAMILIES, 2):
    ap = aligned_consensus(f"{WORK}/hha_{a}__{b}.hhr")
    if not ap:
        dy.append([a, b, "", "", "NO_PARSABLE_ALIGNMENT"])
        continue
    Q, T = ap[0], ap[1]
    qh, th = list(DYAD.finditer(Q)), list(DYAD.finditer(T))
    v = "DYAD_NOT_ALIGNED_TO_DYAD" if qh else "QUERY_CONSENSUS_HAS_NO_DYAD"
    for mm in qh:
        if T[mm.start() + 2:mm.start() + 4].upper() == "DD":
            v = "DYAD_CORRESPONDS"
            break
    dy.append([a, b, str(len(qh)), str(len(th)), v])

with open(f"{TABLES}/g4a_repaired_dyad_correspondence_CANONICAL.tsv", "w") as f:
    f.write("family_A\tfamily_B\tn_dyad_motifs_in_A_consensus\tn_in_B_consensus\tverdict\n")
    for r in dy:
        f.write("\t".join(r) + "\n")

# ------------------------------------------------------------------- transitivity
tri = []
for a, b, c in itertools.permutations(FAMILIES, 3):
    m1, m2_, m3 = pm.get((a, b)), pm.get((b, c)), pm.get((a, c))
    if not (m1 and m2_ and m3):
        continue
    tot = ag = 0
    for qa, tb in m1.items():
        if tb in m2_ and qa in m3:
            tot += 1
            if abs(m2_[tb] - m3[qa]) <= TRANSITIVITY_TOL:
                ag += 1
    if tot >= TRIPLE_MIN_POSITIONS:
        tri.append([a, b, c, str(tot), str(ag), f"{100*ag/tot:.1f}"])

with open(f"{TABLES}/g4a_repaired_transitivity.tsv", "w") as f:
    f.write("family_A\tvia_B\tfamily_C\tn_testable_positions\tn_consistent_within_2\t"
            "pct_transitively_consistent\n")
    for r in tri:
        f.write("\t".join(r) + "\n")

# ------------------------------------------- supported intersection, BOTH denominators
inter = []
for a in FAMILIES:
    sup = collections.Counter()
    for b in FAMILIES:
        if a != b and (a, b) in pm:
            for qa in pm[(a, b)]:
                sup[qa] += 1
    if not sup:
        continue
    n_other = sum(1 for b in FAMILIES if b != a and (a, b) in pm)
    allp = sum(1 for v in sup.values() if v == n_other)
    multi = sum(1 for v in sup.values() if 2 <= v < n_other)
    one = sum(1 for v in sup.values() if v == 1)
    covered = len(sup)
    # REPAIR 2 (ADDENDUM_2 s4): parse the HHM LENG field. The previous row-count heuristic
    # undercounted badly - CRISPR 305 against LENG 796 - inflating pct_of_full_consensus.
    full = 0
    for ln in open(f"{WORK}/{a}.deriv.hhm"):
        if ln.startswith("LENG"):
            full = int(ln.split()[1])
            break
    if not full:
        raise SystemExit(f"FAIL CLOSED: no LENG field in {a}.deriv.hhm")
    inter.append([a, str(n_other), str(covered), str(full), str(allp), str(multi), str(one),
                  f"{100*allp/covered:.1f}", f"{100*allp/full:.1f}" if full else "",
                  f"{100*(allp+multi)/covered:.1f}"])

with open(f"{TABLES}/g4a_repaired_supported_intersection.tsv", "w") as f:
    f.write("family\tn_partner_families\tn_positions_aligned_to_any_partner\t"
            "full_hhm_consensus_length\tn_ALL_PARTNERS\tn_MULTI_FAMILY_2_to_n-1\t"
            "n_SINGLE_PARTNER\tpct_ALL_PARTNERS_of_covered\tpct_ALL_PARTNERS_of_full_consensus\t"
            "pct_ALL_or_MULTI_of_covered\n")
    for r in inter:
        f.write("\t".join(r) + "\n")

# ------------------------------------------ transfer: ONLY for INDEPENDENT_CHALLENGE
tr = []
for a in FAMILIES:
    for b in FAMILIES:
        fp = f"{WORK}/{b}.challenge.faa"
        if not os.path.exists(fp):
            continue
        n = sum(1 for l in open(fp) if l.startswith(">"))
        tbl = f"{WORK}/tr_{a}_{b}.tbl"
        run([BIN + "hmmsearch", "--max", "-E", HMMSEARCH_E, "--noali",
             "--tblout", tbl, f"{WORK}/{a}.deriv.hmm", fp])
        best = {}
        for line in open(tbl):
            if line.startswith("#"):
                continue
            p = line.split()
            sc = float(p[5])
            if p[0] not in best or sc > best[p[0]]:
                best[p[0]] = sc
        sc = list(best.values())
        tr.append([a, b, indep[b], "SELF" if a == b else "CROSS", str(n), str(len(sc)),
                   f"{statistics.median(sc):.1f}" if sc else "",
                   "REPORTABLE" if indep[b] == "INDEPENDENT_CHALLENGE" else
                   "NOT_REPORTABLE_challenge_set_is_not_independent"])

with open(f"{TABLES}/g4a_repaired_transfer.tsv", "w") as f:
    f.write("profile_family\tchallenge_family\tchallenge_independence\tdirection\t"
            "n_challenge\tn_detected_NON_DISCRIMINATING\tmedian_best_bitscore\tclaim_status\n")
    for r in tr:
        f.write("\t".join(r) + "\n")

aud.write(f"{TABLES}/g4a_repair_audit_step2.tsv")
print("step2 complete")
