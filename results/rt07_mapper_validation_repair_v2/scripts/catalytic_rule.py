#!/usr/bin/env python3
"""REPAIR 1 - MAPPED-only catalytic aggregation.  REPAIR 5 - family-scoped loader.

v1 defect, found by independent review: `modal_counter[st] += 1` counted EVERY motif-bearing
state without checking its call, so `AMBIGUOUS`, `UNSUPPORTED` and (vacuously) deleted states
could contribute positive catalytic evidence. Exactly one occurrence did:

    Retrons  EQC02762.1_Retrons  residue 134  FPDD  state 204  AMBIGUOUS  posterior 0.55

Only `MAPPED` now contributes. Excluded occurrences are LANDED in
tables/catalytic_excluded_occurrences.tsv rather than dropped, so the example above stays
visible in the audit trail instead of disappearing into a cleaner number.
"""
import collections, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper_v2 import hmm_leng, state_to_residue
from scoped_loader import load_families

WORK, TABLES, CONTROL = sys.argv[1], sys.argv[2], sys.argv[3]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
DYAD = re.compile(r"[YF].DD")
AGREEMENT_MIN = 0.80          # predeclared falsification condition, unchanged
N_PER_FAMILY = 40


def frozen(control):
    d = {}
    for ln in open(f"{control}/SUPPORT_RULE_FROZEN.tsv"):
        if not ln.startswith("parameter"):
            k, v, _ = ln.split("\t", 2)
            d[k] = v
    return d


def motif_occurrences(states, leng, seq):
    """[(residue_index, hmm_state, motif, call, posterior)] for each [YF].DD occurrence."""
    res2state = {states[s]["residue_index"]: s for s in range(1, leng + 1)
                 if states[s]["residue_index"] is not None}
    out = []
    for m in DYAD.finditer(seq):
        p = m.start() + 1
        st = res2state.get(p)
        if st is None:
            out.append((p, None, m.group(0), "NOT_IN_MATCH_COLUMN", None))
        else:
            out.append((p, st, m.group(0), states[st]["call"], states[st]["posterior"]))
    return out


def main():
    fz = frozen(CONTROL)
    pp_hi, pp_lo = float(fz["PP_HI"]), float(fz["PP_LO"])
    elig = load_families(CONSTRUCTION)
    leng = hmm_leng(HMM)

    store, excluded = {}, []
    modal_counter = collections.Counter()
    n_dyad_seqs = 0
    per_family = collections.defaultdict(lambda: [0, 0])

    for fam in CONSTRUCTION:
        seqs = {k: v for k, v in sorted(elig[fam].items())[:N_PER_FAMILY]}
        m, _, L = state_to_residue(HMM, seqs, WORK, f"cat_{fam}", pp_hi=pp_hi, pp_lo=pp_lo)
        store[fam] = (seqs, m)
        for sid, seq in sorted(seqs.items()):
            occ = motif_occurrences(m[sid], L, seq)
            if not occ:
                continue
            n_dyad_seqs += 1
            per_family[fam][0] += 1
            for p, st, motif, call, post in occ:
                if st is not None and call == "MAPPED":
                    modal_counter[st] += 1           # REPAIR 1: MAPPED only
                else:
                    excluded.append([fam, sid, str(p), str(st or ""), motif, call,
                                     "" if post is None else f"{post:.2f}",
                                     "EXCLUDED_FROM_POSITIVE_EVIDENCE"])

    if not modal_counter:
        raise SystemExit("FAIL CLOSED: no MAPPED [YF].DD occurrence maps to any HMM state")
    cat_state, cat_n = modal_counter.most_common(1)[0]

    # agreement now also requires the CAT_STATE call itself to be MAPPED
    rows, agree = [], 0
    for fam in CONSTRUCTION:
        seqs, m = store[fam]
        for sid, seq in sorted(seqs.items()):
            occ = motif_occurrences(m[sid], leng, seq)
            if not occ:
                continue
            st = m[sid][cat_state]
            hit = (st["call"] == "MAPPED"
                   and any(p == st["residue_index"] and c == "MAPPED" for p, s_, _, c, _ in occ
                           if s_ == cat_state))
            agree += hit
            per_family[fam][1] += hit
            rows.append([fam, sid, str(len(occ)), str(cat_state),
                         str(st["residue_index"] or ""), st["aa"], st["call"],
                         "YES" if hit else "NO",
                         ";".join(f"{p}@{s_ or '-'}:{g}:{c}" for p, s_, g, c, _ in occ)])
    frac = agree / n_dyad_seqs if n_dyad_seqs else 0.0
    verdict = "FROZEN" if frac >= AGREEMENT_MIN else "FAIL_CLOSED"

    with open(f"{TABLES}/catalytic_state_derivation.tsv", "w") as f:
        f.write("family\tsequence_id\tn_motifs_in_sequence\tcat_state\tresidue_at_cat_state\t"
                "aa_at_cat_state\tcall_at_cat_state\tmotif_mapped_at_cat_state\tall_motifs\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    with open(f"{TABLES}/catalytic_excluded_occurrences.tsv", "w") as f:
        f.write("# REPAIR 1: motif occurrences NOT counted as positive catalytic evidence\n")
        f.write("# because their call at the mapped state is not exactly MAPPED.\n")
        f.write("# Retained deliberately: the known AMBIGUOUS example must stay auditable.\n")
        f.write("family\tsequence_id\tresidue_index\thmm_state\tmotif\tcall\tposterior\t"
                "disposition\n")
        for r in excluded:
            f.write("\t".join(r) + "\n")

    with open(f"{TABLES}/catalytic_state_agreement.tsv", "w") as f:
        f.write("family\tn_dyad_bearing\tn_with_mapped_motif_at_cat_state\tfraction\n")
        for fam in CONSTRUCTION:
            a, b = per_family[fam]
            f.write(f"{fam}\t{a}\t{b}\t{(b/a if a else 0):.4f}\n")
        f.write(f"ALL\t{n_dyad_seqs}\t{agree}\t{frac:.4f}\n")

    top = modal_counter.most_common(5)
    with open(f"{TABLES}/catalytic_state_candidates.tsv", "w") as f:
        f.write("# counts are MAPPED-only (REPAIR 1)\n")
        f.write("hmm_state\tn_mapped_motif_occurrences\n")
        for st, n in top:
            f.write(f"{st}\t{n}\n")

    if verdict == "FAIL_CLOSED":
        raise SystemExit(f"FAIL CLOSED: construction agreement {frac:.4f} < {AGREEMENT_MIN}")

    with open(f"{CONTROL}/CATALYTIC_STATE_FROZEN.tsv", "w") as f:
        f.write("parameter\tvalue\tderivation\n")
        f.write(f"CAT_STATE\t{cat_state}\tmodal HMM state of MAPPED [YF].DD occurrences across "
                f"{n_dyad_seqs} dyad-bearing construction sequences (REPAIR 1: MAPPED only)\n")
        f.write(f"CAT_STATE_COUNT\t{cat_n}\tMAPPED motif occurrences at CAT_STATE\n")
        f.write(f"RUNNER_UP\t{top[1][0] if len(top) > 1 else ''}\t"
                f"{top[1][1] if len(top) > 1 else 0} MAPPED occurrences\n")
        f.write(f"CONSTRUCTION_AGREEMENT\t{frac:.4f}\tfraction with a MAPPED motif at CAT_STATE "
                f"(predeclared minimum {AGREEMENT_MIN})\n")
        f.write(f"AGREEMENT_MIN\t{AGREEMENT_MIN}\tpredeclared falsification condition\n")
        f.write(f"N_EXCLUDED_NON_MAPPED\t{len(excluded)}\toccurrences excluded from positive "
                f"evidence; landed in catalytic_excluded_occurrences.tsv\n")

    print(f"CAT_STATE = {cat_state} (MAPPED-only count {cat_n}); top: {top}")
    print(f"agreement = {agree}/{n_dyad_seqs} = {frac:.4f} (min {AGREEMENT_MIN}) -> {verdict}")
    print(f"excluded non-MAPPED motif occurrences: {len(excluded)}")
    for r in excluded:
        print(f"    EXCLUDED {r[0]} {r[1]} res{r[2]} state{r[3]} {r[4]} {r[5]} pp={r[6]}")
    for fam in CONSTRUCTION:
        a, b = per_family[fam]
        print(f"  {fam:9s} dyad_bearing={a:3d} mapped_at_cat_state={b:3d} "
              f"{(b/a if a else 0):.3f}")


if __name__ == "__main__":
    main()
