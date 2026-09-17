#!/usr/bin/env python3
"""Construction/development validation of the REPAIRED mapper under the FROZEN rule.

Construction families only. No G2L object and no UG25 object is read.
This is implementation validation, not a transfer claim: these families built the frame.
"""
import collections, os, re, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper_v2 import hmm_leng, state_to_residue, domain_scores, classify_sequence
from scoped_loader import load_families          # REPAIR 5

WORK, TABLES, CONTROL = sys.argv[1], sys.argv[2], sys.argv[3]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
ANCH = sorted(int(l.split("\t")[2]) for l in open(
    "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_ug5_holdout_gate/"
    "tables/ug5_frozen_anchor_coordinates.tsv") if not l.startswith("anchor_index"))
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
DYAD = re.compile(r"[YF].DD")
N_PER_FAMILY = 40

fz = {}
for ln in open(f"{CONTROL}/SUPPORT_RULE_FROZEN.tsv"):
    if not ln.startswith("parameter"):
        k, v, _ = ln.split("\t", 2)
        fz[k] = v
PP_HI, PP_LO = float(fz["PP_HI"]), float(fz["PP_LO"])
S_MIN, K_MIN = float(fz["S_MIN"]), int(fz["K_MIN"])
CAT_STATE = int([l.split("\t")[1] for l in open(f"{CONTROL}/CATALYTIC_STATE_FROZEN.tsv")
                 if l.startswith("CAT_STATE")][0])


def catalytic_verdict(states, seq):
    st = states[CAT_STATE]
    call = st["call"]
    if call == "DELETED_STATE":
        return "CATALYTIC_STATE_DELETED", "", 0
    ri = st["residue_index"]
    n_motifs = len(DYAD.findall(seq))
    is_dyad = bool(DYAD.match(seq[ri - 1:ri + 3])) if ri else False
    if call == "AMBIGUOUS":
        return "CATALYTIC_AMBIGUOUS", seq[ri - 1:ri + 3], n_motifs
    if call == "UNSUPPORTED":
        return "CATALYTIC_UNSUPPORTED", seq[ri - 1:ri + 3], n_motifs
    return ("CATALYTIC_CONFIRMED" if is_dyad else "CATALYTIC_SUBSTITUTED",
            seq[ri - 1:ri + 3], n_motifs)


def main():
    elig = load_families(CONSTRUCTION)
    leng = hmm_leng(HMM)
    fam_rows, seq_rows, cat_rows = [], [], []
    for fam in CONSTRUCTION:
        seqs = {k: v for k, v in sorted(elig[fam].items())[:N_PER_FAMILY]}
        m, ins, L = state_to_residue(HMM, seqs, WORK, f"cv2_{fam}", pp_hi=PP_HI, pp_lo=PP_LO)
        dom = domain_scores(HMM, f"{WORK}/cv2_{fam}.faa", WORK, f"cv2_{fam}")
        fr, ab, cats = [], collections.Counter(), collections.Counter()
        for sid, seq in sorted(seqs.items()):
            v, reason, nm, na, nu, nd = classify_sequence(m[sid], ANCH, L, S_MIN, K_MIN,
                                                          dom.get(sid))
            fr.append(nm / len(ANCH))
            ab[reason] += 1
            cv, motif, n_motifs = catalytic_verdict(m[sid], seq)
            cats[cv] += 1
            seq_rows.append([fam, sid, str(nm), str(na), str(nu), str(nd),
                             f"{100*nm/len(ANCH):.1f}", v, reason,
                             f"{dom.get(sid, (float('nan'),))[0]:.1f}", cv])
            cat_rows.append([fam, sid, str(CAT_STATE),
                             str(m[sid][CAT_STATE]["residue_index"] or ""),
                             m[sid][CAT_STATE]["aa"], m[sid][CAT_STATE]["call"],
                             motif, str(n_motifs), cv])
        fam_rows.append([fam, str(len(seqs)), f"{statistics.median(fr):.4f}",
                         f"{min(fr):.4f}", f"{max(fr):.4f}",
                         str(ab["OK"]), str(ab["NO_QUALIFYING_DOMAIN"]),
                         str(ab["INSUFFICIENT_SUPPORTED_ANCHORS"]),
                         str(cats["CATALYTIC_CONFIRMED"]), str(cats["CATALYTIC_SUBSTITUTED"]),
                         str(cats["CATALYTIC_AMBIGUOUS"] + cats["CATALYTIC_UNSUPPORTED"]),
                         str(cats["CATALYTIC_STATE_DELETED"])])

    with open(f"{TABLES}/construction_validation_v2_family.tsv", "w") as f:
        f.write("family\tn\tmedian_mapped_fraction\tmin_mapped_fraction\tmax_mapped_fraction\t"
                "n_ok\tn_abstain_no_domain\tn_abstain_few_anchors\tcatalytic_confirmed\t"
                "catalytic_substituted\tcatalytic_ambiguous_or_unsupported\t"
                "catalytic_state_deleted\n")
        for r in fam_rows:
            f.write("\t".join(r) + "\n")
        # REPAIR 7: the narrative total is COMPUTED and landed, never transcribed by hand.
        # v1's decision record said 237/239; the tables always said 217/219.
        tot_n = sum(int(r[1]) for r in fam_rows)
        tot_ok = sum(int(r[5]) for r in fam_rows)
        tot = ["TOTAL", str(tot_n), "", "", "", str(tot_ok),
               str(sum(int(r[6]) for r in fam_rows)), str(sum(int(r[7]) for r in fam_rows)),
               str(sum(int(r[8]) for r in fam_rows)), str(sum(int(r[9]) for r in fam_rows)),
               str(sum(int(r[10]) for r in fam_rows)), str(sum(int(r[11]) for r in fam_rows))]
        f.write("\t".join(tot) + "\n")
    with open(f"{TABLES}/construction_validation_v2_sequence.tsv", "w") as f:
        f.write("family\tsequence_id\tn_mapped\tn_ambiguous\tn_unsupported\tn_deleted\t"
                "pct_mapped\tverdict\treason\tdomain_bitscore\tcatalytic_verdict\n")
        for r in seq_rows:
            f.write("\t".join(r) + "\n")
    with open(f"{TABLES}/construction_catalytic_calls.tsv", "w") as f:
        f.write("family\tsequence_id\tcat_state\tresidue_index\tamino_acid\tcall\t"
                "motif_at_cat_state\tn_motifs_in_sequence\tcatalytic_verdict\n")
        for r in cat_rows:
            f.write("\t".join(r) + "\n")

    print(f"{'family':9s} {'n':>3s} {'median':>7s} {'ok':>4s} {'ab_dom':>7s} {'ab_anch':>8s} "
          f"{'cat_conf':>9s} {'cat_sub':>8s} {'cat_amb':>8s} {'cat_del':>8s}")
    for r in fam_rows:
        print(f"{r[0]:9s} {r[1]:>3s} {r[2]:>7s} {r[5]:>4s} {r[6]:>7s} {r[7]:>8s} "
              f"{r[8]:>9s} {r[9]:>8s} {r[10]:>8s} {r[11]:>8s}")


if __name__ == "__main__":
    main()
