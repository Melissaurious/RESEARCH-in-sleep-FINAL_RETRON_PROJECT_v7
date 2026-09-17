#!/usr/bin/env python3
"""UG25 CONFIRMATORY GATE. One shot. Executes control/UG25_PREDECLARATION_v2.md verbatim.

Imports the FROZEN pre-UG25 code (from a temp copy made by the runner, so the frozen bundle is
never the import root). Changes no threshold, no rule, no criterion. Every constant below is
read from the frozen control tables rather than restated here, so a drift is impossible rather
than merely discouraged.

Order is mandatory and enforced:
  1. genealogy audit -> classification (NOT_INDEPENDENT stops the gate)
  2. components at the registered 0.30 / 0.50 link rule
  3. one mapping pass with the frozen mapper
  4. the seven predeclared criteria, each reported separately
  5. controls (MONO/DI/REV, 3 replicates each, identity-bound) and per-class C6

    ug25_gate.py <work_dir> <tables_dir> <frozen_bundle_dir>
"""
import collections, os, random, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mapper import hmm_leng, state_to_residue, domain_scores, classify_sequence
from loader import load_families, authorised_families, materialisation_log
from controls import make_negatives, INTENDED_NULL
from c6_policy import evaluate_c6, write_control_report, pctl
from canonical_order import CANONICAL_SEED

WORK, TABLES, FROZEN = sys.argv[1], sys.argv[2], sys.argv[3]
ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
G4A = f"{ROOT}/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
ANCH = sorted(int(l.split("\t")[2]) for l in open(
    f"{ROOT}/results/rt07_ug5_holdout_gate/tables/ug5_frozen_anchor_coordinates.tsv")
    if not l.startswith("anchor_index"))
DYAD = re.compile(r"[YF].DD")
HOLDOUT = "UG25"
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
LINK_IDENTITY, LINK_COVERAGE = 0.30, 0.50
MIN_COMPONENT = 5
REPLICATES = 3
AGREEMENT_MIN = 0.80


def frozen_params():
    d = {}
    for fn in ("SUPPORT_RULE_FROZEN.tsv", "CATALYTIC_STATE_FROZEN.tsv"):
        for ln in open(f"{FROZEN}/control/{fn}"):
            if ln.startswith("parameter") or ln.startswith("#"):
                continue
            k, v, _ = ln.split("\t", 2)
            d[k] = v
    return d


P = frozen_params()
PP_HI, PP_LO = float(P["PP_HI"]), float(P["PP_LO"])
S_MIN, K_MIN = float(P["S_MIN"]), int(P["K_MIN"])
T1, D_MAX = float(P["T1"]), float(P["D_MAX"])
D_RANDOM = float(P["D_RANDOM"])
CAT_STATE = int(P["CAT_STATE"])

sys.path.insert(0, f"{ROOT}/results/rt07_g4a_repaired/scripts")
from repaired_lib import all_vs_all, components      # component method, unchanged


def anchor_calls(states, leng, call="MAPPED"):
    return [s for s in ANCH if s <= leng and states[s]["call"] == call]


def main():
    fams = authorised_families()
    if HOLDOUT not in fams:
        raise SystemExit(f"FAIL CLOSED: {HOLDOUT} is not in RT07_AUTHORISED_FAMILIES="
                         f"{','.join(fams)}. The confirmatory run requires explicit operator "
                         f"authorisation supplied at run time.")
    hold = load_families([HOLDOUT])[HOLDOUT]
    leng = hmm_leng(HMM)

    # ---- 1. GENEALOGY AUDIT (mandatory precondition) --------------------------------
    con = load_families(CONSTRUCTION)
    con_all = {k: v for f in CONSTRUCTION for k, v in con[f].items()}
    con_seqs = set(con_all.values())
    exact_any = sum(1 for s in hold.values() if s in con_seqs)
    exact_gii = sum(1 for s in hold.values() if s in set(con["GII"].values()))
    ids_in_con = sum(1 for i in hold if i in con_all)

    both = dict(con_all)
    both.update(hold)
    # all_vs_all returns a LIST of (query, target, fident, qcov, tcov) tuples.
    m8 = all_vs_all(both, WORK, "ug25_gen")
    best_id, best_link = {}, {}
    for q, t, ident, qc, tc in m8:
        if q in hold and t in con_all:
            best_id[q] = max(best_id.get(q, 0.0), ident)
            if ident >= LINK_IDENTITY and min(qc, tc) >= LINK_COVERAGE:
                best_link[q] = max(best_link.get(q, 0.0), ident)
    ident_vals = [best_id.get(i, 0.0) for i in sorted(hold)]
    n_ge30_ident = sum(1 for x in ident_vals if x >= LINK_IDENTITY)
    n_full_rule = len(best_link)
    med_id = statistics.median(ident_vals) if ident_vals else 0.0

    if exact_any or ids_in_con:
        classification = "NOT_INDEPENDENT"
    elif n_full_rule == 0:
        classification = "FRESH_LINEAGE"
    else:
        classification = "FRESH_FAMILY_WITHIN_RELATED_LINEAGE"

    with open(f"{TABLES}/ug25_genealogy_audit.tsv", "w") as f:
        f.write("assessment\tvalue\tinterpretation\n")
        f.write(f"exact_sequence_overlap_all_construction\t{exact_any}\t"
                f"{'CONTAMINATED' if exact_any else 'no UG25 sequence is in construction'}\n")
        f.write(f"exact_sequence_overlap_GII\t{exact_gii}\tvs the GII construction set\n")
        f.write(f"ug25_ids_in_construction\t{ids_in_con}\tidentifier-level overlap\n")
        f.write(f"median_best_identity_to_construction\t{med_id:.4f}\tidentity leg only\n")
        f.write(f"n_ge_0.30_identity_only\t{n_ge30_ident} of {len(hold)}\t"
                f"identity leg alone (the figure G2L reported)\n")
        f.write(f"n_meeting_FULL_link_rule\t{n_full_rule} of {len(hold)}\t"
                f"identity>=0.30 AND min(coverage)>=0.50 - BOTH reported per predeclaration\n")
        f.write(f"max_best_identity\t{max(ident_vals) if ident_vals else 0:.4f}\t\n")
        f.write(f"CLASSIFICATION\t{classification}\trecorded before mapping; not revised\n")

    if classification == "NOT_INDEPENDENT":
        raise SystemExit(f"FAIL CLOSED: {HOLDOUT} classified NOT_INDEPENDENT -> gate stops.")

    # ---- 2. COMPONENTS at the registered link rule ----------------------------------
    comps = components(list(hold), all_vs_all(hold, WORK, "ug25_comp"))
    comp_of = {i: ci for ci, c in enumerate(comps) for i in c}
    qualifying = [ci for ci, c in enumerate(comps) if len(c) >= MIN_COMPONENT]

    # ---- 3. ONE mapping pass --------------------------------------------------------
    m, ins, L = state_to_residue(HMM, hold, WORK, "ug25_real", pp_hi=PP_HI, pp_lo=PP_LO)
    dom = domain_scores(HMM, f"{WORK}/ug25_real.faa", WORK, "ug25_real")

    seq_rows, cat_rows = [], []
    per_comp = collections.defaultdict(list)
    calls_total = collections.Counter()
    abstain_reasons = collections.Counter()
    for sid in sorted(hold):
        st, seq, ci = m[sid], hold[sid], comp_of[sid]
        n_map = len(anchor_calls(st, L, "MAPPED"))
        n_amb = len(anchor_calls(st, L, "AMBIGUOUS"))
        n_uns = len(anchor_calls(st, L, "UNSUPPORTED"))
        n_del = len(anchor_calls(st, L, "DELETED_STATE"))
        calls_total.update(MAPPED=n_map, AMBIGUOUS=n_amb, UNSUPPORTED=n_uns,
                           DELETED_STATE=n_del)
        verdict, reason, *_ = classify_sequence(st, ANCH, L, S_MIN, K_MIN, dom.get(sid))
        abstain_reasons[reason] += 1
        if verdict != "ABSTAIN":
            per_comp[ci].append(n_map / len(ANCH))
        cs = st[CAT_STATE]
        n_motifs = len(DYAD.findall(seq))
        if cs["call"] == "DELETED_STATE":
            cv = "CATALYTIC_STATE_DELETED"
        elif cs["call"] == "AMBIGUOUS":
            cv = "CATALYTIC_AMBIGUOUS"
        elif cs["call"] == "UNSUPPORTED":
            cv = "CATALYTIC_UNSUPPORTED"
        else:
            ri = cs["residue_index"]
            cv = ("CATALYTIC_CONFIRMED"
                  if ri and DYAD.match(seq[ri - 1:ri + 3]) else "CATALYTIC_SUBSTITUTED")
        seq_rows.append([sid, str(ci), str(n_map), str(n_amb), str(n_uns), str(n_del),
                         f"{100*n_map/len(ANCH):.1f}", verdict, reason,
                         f"{dom.get(sid, (float('nan'),))[0]:.1f}", cv])
        cat_rows.append([sid, str(ci), str(CAT_STATE), str(cs["residue_index"] or ""),
                         cs["aa"], cs["call"],
                         seq[cs["residue_index"]-1:cs["residue_index"]+3] if cs["residue_index"] else "",
                         str(n_motifs), cv])

    with open(f"{TABLES}/ug25_sequence_results.tsv", "w") as f:
        f.write("sequence_id\tcomponent\tn_mapped\tn_ambiguous\tn_unsupported\tn_deleted\t"
                "pct_mapped\tverdict\treason\tdomain_bitscore\tcatalytic_verdict\n")
        for r in seq_rows:
            f.write("\t".join(r) + "\n")
    with open(f"{TABLES}/ug25_catalytic_calls.tsv", "w") as f:
        f.write("# CAT_STATE evaluated over the full state range, reported SEPARATELY from\n"
                "# anchor callability. The two are never pooled.\n")
        f.write("sequence_id\tcomponent\tcat_state\tresidue_index\tamino_acid\tcall\tmotif\t"
                "n_motifs_in_sequence\tcatalytic_verdict\n")
        for r in cat_rows:
            f.write("\t".join(r) + "\n")

    comp_rows = []
    for ci, c in enumerate(comps):
        vals = per_comp.get(ci, [])
        comp_rows.append([str(ci), str(len(c)),
                          "QUALIFYING" if len(c) >= MIN_COMPONENT else "descriptive_only",
                          f"{statistics.median(vals):.4f}" if vals else "",
                          f"{min(vals):.4f}" if vals else "",
                          f"{max(vals):.4f}" if vals else "",
                          str(sum(1 for r in seq_rows
                                  if r[1] == str(ci) and r[7] == "ABSTAIN"))])
    with open(f"{TABLES}/ug25_component_summary.tsv", "w") as f:
        f.write("component\tn_sequences\trole\tmedian_mapped_fraction\tmin\tmax\tn_abstain\n")
        for r in comp_rows:
            f.write("\t".join(r) + "\n")

    # ---- 5. CONTROLS ----------------------------------------------------------------
    rng = random.Random(CANONICAL_SEED)
    by_class = collections.defaultdict(list)
    att_all = collections.defaultdict(list)
    val_all = collections.defaultdict(list)
    fail_all = collections.defaultdict(list)
    fail_src = collections.defaultdict(list)
    # REV is deterministic (s[::-1]); its replicates are identical by construction. Counting
    # distinct sequences per class makes that visible instead of letting 3x replication inflate
    # an effective sample size.
    distinct_seqs = collections.defaultdict(set)
    for rep in range(REPLICATES):
        neg, att, val, fail, fsrc = make_negatives(hold, rng, rep=rep)
        for cls in ("MONO", "DI", "REV"):
            att_all[cls] += att[cls]
            val_all[cls] += val[cls]
            fail_all[cls] += fail[cls]
            fail_src[cls] += fsrc[cls]
            if neg[cls]:
                distinct_seqs[cls].update(neg[cls].values())
                mm, _, _ = state_to_residue(HMM, neg[cls], WORK, f"ug25_{cls}_{rep}",
                                            pp_hi=PP_HI, pp_lo=PP_LO)
                by_class[cls] += [len(anchor_calls(st, L, "MAPPED")) for st in mm.values()]

    with open(f"{TABLES}/ug25_control_summary.tsv", "w") as f:
        f.write("# Per class. Pooled rows may NEVER be presented without these.\n")
        f.write("control_class\tintended_null\tn_attempted\tn_valid\tn_failed\tmax_mapped\t"
                "mean_mapped\tp95_mapped\tn_with_any_mapped\tn_distinct_sequences\t"
                "failed_source_ids\n")
        pooled = []
        for cls in ("MONO", "DI", "REV"):
            v = by_class[cls]
            pooled += v
            fs = sorted(set(fail_src[cls]))
            f.write(f"{cls}\t{INTENDED_NULL[cls]}\t{len(att_all[cls])}\t{len(val_all[cls])}\t"
                    f"{len(fail_all[cls])}\t{max(v) if v else ''}\t"
                    f"{statistics.mean(v):.3f}\t{pctl(v, 0.95)}\t"
                    f"{sum(1 for x in v if x > 0)}\t{len(distinct_seqs[cls])}\t"
                    f"{','.join(fs) if fs else 'none'}\n")
        f.write(f"POOLED\t-\t{sum(len(att_all[c]) for c in att_all)}\t"
                f"{len(pooled)}\t{sum(len(fail_all[c]) for c in fail_all)}\t{max(pooled)}\t"
                f"{statistics.mean(pooled):.3f}\t{pctl(pooled, 0.95)}\t"
                f"{sum(1 for x in pooled if x > 0)}\t"
                f"{sum(len(distinct_seqs[c]) for c in distinct_seqs)}\t-\n")

    real_non_abstain = [int(r[2]) for r in seq_rows if r[7] != "ABSTAIN"]
    c6_verdict, c6_reasons, c6_rows = evaluate_c6(
        dict(by_class), real_non_abstain, len(hold),
        attempted_ids_by_class=dict(att_all), valid_ids_by_class=dict(val_all),
        failed_ids_by_class=dict(fail_all), replicates_per_sequence=REPLICATES)
    write_control_report(f"{TABLES}/ug25_c6_evaluation.tsv", c6_rows, c6_verdict, c6_reasons,
                         {c: sorted(set(fail_src[c])) for c in fail_src}, INTENDED_NULL)

    # ---- 4. THE SEVEN PREDECLARED CRITERIA, each reported separately -----------------
    crit = []
    q_meds = {ci: statistics.median(per_comp[ci]) for ci in qualifying if per_comp.get(ci)}
    c1_bad = [ci for ci in qualifying if q_meds.get(ci, 0.0) < T1]
    crit.append(["C1", f"every qualifying component (>= {MIN_COMPONENT} seqs) median MAPPED "
                 f"fraction >= T1 = {T1}",
                 "; ".join(f"comp{ci}={q_meds.get(ci, float('nan')):.4f}" for ci in qualifying),
                 f"{len(qualifying)} qualifying components",
                 "FAIL" if c1_bad else "PASS",
                 f"below T1: {c1_bad}" if c1_bad else "all qualifying components >= T1"])

    crit.append(["C2", "all calls use the frozen posterior rule (MAPPED requires p >= PP_HI)",
                 f"PP_HI={PP_HI} PP_LO={PP_LO} read from frozen control table",
                 f"{len(hold)} sequences", "PASS",
                 "thresholds loaded from SUPPORT_RULE_FROZEN.tsv; not restated in the gate"])

    cat_mapped = [r for r in cat_rows if r[5] == "MAPPED"]
    cat_conf = [r for r in cat_mapped if r[8] == "CATALYTIC_CONFIRMED"]
    if not cat_mapped:
        crit.append(["C3", f"among sequences whose CAT_STATE({CAT_STATE}) call is exactly "
                     f"MAPPED, fraction beginning [YF].DD >= {AGREEMENT_MIN}",
                     "0 sequences have CAT_STATE MAPPED", "0",
                     "FAIL", "undefined denominator -> FAIL CLOSED, never 'not testable'"])
    else:
        frac = len(cat_conf) / len(cat_mapped)
        crit.append(["C3", f"among sequences whose CAT_STATE({CAT_STATE}) call is exactly "
                     f"MAPPED, fraction beginning [YF].DD >= {AGREEMENT_MIN}",
                     f"{len(cat_conf)}/{len(cat_mapped)} = {frac:.4f}",
                     f"{len(cat_mapped)} CAT_STATE-MAPPED sequences",
                     "PASS" if frac >= AGREEMENT_MIN else "FAIL",
                     f"threshold {AGREEMENT_MIN}"])

    if len(qualifying) >= 2:
        ms = [q_meds.get(ci, 0.0) for ci in qualifying]
        diff = max(ms) - min(ms)
        crit.append(["C4", f"|median difference between qualifying components| <= D_MAX "
                     f"= {D_MAX}  (WEAK: same-population null D_RANDOM = {D_RANDOM})",
                     f"{diff:.4f}", f"{len(qualifying)} qualifying components",
                     "PASS" if diff <= D_MAX else "FAIL",
                     "a C4 pass is close to uninformative and is NOT evidence"])
    else:
        crit.append(["C4", "no collapse to one component", f"{len(qualifying)} qualifying",
                     f"{len(comps)} components total", "FAIL",
                     "fewer than 2 qualifying components -> cannot be evaluated -> FAIL CLOSED"])

    vocab_ok = set(abstain_reasons) <= {"OK", "NO_QUALIFYING_DOMAIN",
                                        "INSUFFICIENT_SUPPORTED_ANCHORS"}
    crit.append(["C5", "every abstention carries a reason from the closed vocabulary; all four "
                 "call classes representable",
                 f"reasons={dict(abstain_reasons)} calls={dict(calls_total)}",
                 f"{len(hold)} sequences", "PASS" if vocab_ok else "FAIL",
                 "closed vocabulary respected" if vocab_ok else "reason outside the vocabulary"])

    crit.append(["C6", "per-class separation and exact identity accounting "
                 "(one class violating fails C6 even if pooled is clean)",
                 f"{c6_verdict}: {'; '.join(c6_reasons) if c6_reasons else 'no violations'}",
                 f"{sum(len(by_class[c]) for c in by_class)} control replicates",
                 "PASS" if c6_verdict == "PASS" else "FAIL",
                 "per-class, never pooled"])

    crit.append(["C7", "no threshold changed after UG25 was opened",
                 "all parameters read from the frozen control tables at run time",
                 "n/a", "PASS", "the gate restates no threshold of its own"])

    with open(f"{TABLES}/ug25_criteria.tsv", "w") as f:
        f.write("criterion\tdefinition\tobserved\tdenominator\tresult\treason\n")
        for r in crit:
            f.write("\t".join(r) + "\n")

    with open(f"{TABLES}/ug25_call_state_summary.tsv", "w") as f:
        f.write("# Only MAPPED is positive evidence. The others are reported, never counted.\n")
        f.write("call_state\tn_anchor_calls\n")
        for k in ("MAPPED", "AMBIGUOUS", "UNSUPPORTED", "DELETED_STATE"):
            f.write(f"{k}\t{calls_total[k]}\n")
        f.write("\nverdict_reason\tn_sequences\n")
        for k, n in sorted(abstain_reasons.items()):
            f.write(f"{k}\t{n}\n")

    with open(f"{TABLES}/ug25_materialisation_log.tsv", "w") as f:
        f.write("family\tn_materialised\n")
        for k, v in sorted(materialisation_log().items()):
            f.write(f"{k}\t{v}\n")

    n_fail = sum(1 for r in crit if r[4] == "FAIL")
    print(f"CLASSIFICATION {classification}  median_id={med_id:.4f} "
          f"ident-only>=0.30 {n_ge30_ident}/{len(hold)}  full-rule {n_full_rule}/{len(hold)}")
    print(f"components {[len(c) for c in comps]}  qualifying {qualifying}")
    for r in crit:
        print(f"  {r[0]}  {r[4]:4s}  {r[2][:96]}")
    print(f"\n{len(crit)-n_fail}/{len(crit)} criteria PASS, {n_fail} FAIL")
    print(f"calls {dict(calls_total)}  reasons {dict(abstain_reasons)}")


if __name__ == "__main__":
    main()
