#!/usr/bin/env python3
"""REPAIR 6 - derive and freeze CAT_STATE from construction families only.

Executes control/CATALYTIC_MULTIMOTIF_RULE.md. No G2L object and no UG25 object is read.
"""
import collections, os, re, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper_v2 import hmm_leng, state_to_residue, domain_scores
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
                   "rt07_g4a_repaired/scripts")
from repaired_lib import eligible_by_family

WORK, TABLES, CONTROL = sys.argv[1], sys.argv[2], sys.argv[3]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
DYAD = re.compile(r"[YF].DD")
AGREEMENT_MIN = 0.80          # predeclared falsification condition
N_PER_FAMILY = 40


def frozen(control):
    d = {}
    for ln in open(f"{control}/SUPPORT_RULE_FROZEN.tsv"):
        if ln.startswith("parameter"):
            continue
        k, v, _ = ln.split("\t", 2)
        d[k] = v
    return d


def motif_states(states, leng, seq):
    """HMM states at which a [YF].DD occurrence begins. Inverts the state->residue path."""
    res2state = {states[s]["residue_index"]: s for s in range(1, leng + 1)
                 if states[s]["residue_index"] is not None}
    out = []
    for m in DYAD.finditer(seq):
        out.append((m.start() + 1, res2state.get(m.start() + 1), m.group(0)))
    return out


def main():
    fz = frozen(CONTROL)
    pp_hi, pp_lo = float(fz["PP_HI"]), float(fz["PP_LO"])
    elig = eligible_by_family()
    leng = hmm_leng(HMM)

    rows, modal_counter, n_dyad_seqs = [], collections.Counter(), 0
    per_family = collections.defaultdict(lambda: [0, 0])   # [dyad_seqs, at_modal]
    store = {}
    for fam in CONSTRUCTION:
        seqs = {k: v for k, v in sorted(elig[fam].items())[:N_PER_FAMILY]}
        m, _, L = state_to_residue(HMM, seqs, WORK, f"cat_{fam}", pp_hi=pp_hi, pp_lo=pp_lo)
        store[fam] = (seqs, m)
        for sid, seq in sorted(seqs.items()):
            ms = motif_states(m[sid], L, seq)
            if not ms:
                continue
            n_dyad_seqs += 1
            per_family[fam][0] += 1
            for _, st, _ in ms:
                if st:
                    modal_counter[st] += 1

    if not modal_counter:
        raise SystemExit("FAIL CLOSED: no [YF].DD occurrence maps to any HMM state")
    cat_state, _ = modal_counter.most_common(1)[0]

    # agreement: fraction of dyad-bearing construction sequences with a motif AT cat_state
    agree = 0
    for fam in CONSTRUCTION:
        seqs, m = store[fam]
        for sid, seq in sorted(seqs.items()):
            ms = motif_states(m[sid], leng, seq)
            if not ms:
                continue
            hit = any(st == cat_state for _, st, _ in ms)
            agree += hit
            per_family[fam][1] += hit
            rows.append([fam, sid, str(len(ms)), str(cat_state),
                         str(m[sid][cat_state]["residue_index"] or ""),
                         m[sid][cat_state]["aa"], m[sid][cat_state]["call"],
                         "YES" if hit else "NO",
                         ";".join(f"{p}@{st}:{g}" for p, st, g in ms)])
    frac = agree / n_dyad_seqs if n_dyad_seqs else 0.0
    verdict = "FROZEN" if frac >= AGREEMENT_MIN else "FAIL_CLOSED"

    with open(f"{TABLES}/catalytic_state_derivation.tsv", "w") as f:
        f.write("family\tsequence_id\tn_motifs_in_sequence\tcat_state\tresidue_at_cat_state\t"
                "aa_at_cat_state\tcall_at_cat_state\tmotif_at_cat_state\tall_motifs\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    with open(f"{TABLES}/catalytic_state_agreement.tsv", "w") as f:
        f.write("family\tn_dyad_bearing\tn_with_motif_at_cat_state\tfraction\n")
        for fam in CONSTRUCTION:
            a, b = per_family[fam]
            f.write(f"{fam}\t{a}\t{b}\t{(b/a if a else 0):.4f}\n")
        f.write(f"ALL\t{n_dyad_seqs}\t{agree}\t{frac:.4f}\n")

    top = modal_counter.most_common(5)
    with open(f"{TABLES}/catalytic_state_candidates.tsv", "w") as f:
        f.write("hmm_state\tn_motif_occurrences\n")
        for st, n in top:
            f.write(f"{st}\t{n}\n")

    if verdict == "FAIL_CLOSED":
        raise SystemExit(f"FAIL CLOSED: construction agreement {frac:.3f} < {AGREEMENT_MIN}; "
                         f"no CAT_STATE frozen, no catalytic claim may be made")

    with open(f"{CONTROL}/CATALYTIC_STATE_FROZEN.tsv", "w") as f:
        f.write("parameter\tvalue\tderivation\n")
        f.write(f"CAT_STATE\t{cat_state}\tmodal HMM state of [YF].DD across "
                f"{n_dyad_seqs} dyad-bearing construction sequences\n")
        f.write(f"CONSTRUCTION_AGREEMENT\t{frac:.4f}\tfraction with a motif at CAT_STATE "
                f"(predeclared minimum {AGREEMENT_MIN})\n")
        f.write(f"AGREEMENT_MIN\t{AGREEMENT_MIN}\tpredeclared falsification condition\n")
        f.write("ANCHOR_MEMBERSHIP\tsee tables\tCAT_STATE is evaluated over all 471 states, "
                "not restricted to the 150 ALL_PARTNERS anchors\n")

    print(f"CAT_STATE = {cat_state}  (top candidates: {top})")
    print(f"agreement = {agree}/{n_dyad_seqs} = {frac:.4f}  (min {AGREEMENT_MIN}) -> {verdict}")
    for fam in CONSTRUCTION:
        a, b = per_family[fam]
        print(f"  {fam:9s} dyad_bearing={a:3d} at_cat_state={b:3d} "
              f"{(b/a if a else 0):.3f}")


if __name__ == "__main__":
    main()
