#!/usr/bin/env python3
"""Clean-room pipeline: calibration -> catalytic -> construction validation -> controls.

The SCIENCE is unchanged from the accepted construction mapper. Only the execution and
provenance envelope is new. Every threshold, grid, rule and criterion is carried over
verbatim; nothing is re-derived in a way that could move a number.

    pipeline.py <work_dir> <tables_dir> <control_dir>

Authorised development families come from the RT07_AUTHORISED_FAMILIES environment
variable (see loader.py). UG25 is not referenced anywhere in this file.
"""
import collections, math, os, random, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mapper import hmm_leng, state_to_residue, domain_scores, classify_sequence
from loader import load_families, authorised_families, materialisation_log
from controls import make_negatives, INTENDED_NULL
from c6_policy import evaluate_c6, write_control_report, pctl
from canonical_order import (CANONICAL_FAMILY_ORDER, CANONICAL_SEED,
                             CANONICAL_ORDER_HASH, assert_canonical)

WORK, TABLES, CONTROL = sys.argv[1], sys.argv[2], sys.argv[3]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
ANCHOR_TABLE = ("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
                "rt07_ug5_holdout_gate/tables/ug5_frozen_anchor_coordinates.tsv")
ANCH = sorted(int(l.split("\t")[2]) for l in open(ANCHOR_TABLE)
              if not l.startswith("anchor_index"))

DYAD = re.compile(r"[YF].DD")
PP_LO = 0.50
PP_HI_GRID = [0.55, 0.65, 0.75, 0.85, 0.95]
S_MIN_GRID = [0, 2, 4, 6, 8, 10, 15, 20, 30]
K_MIN_GRID = [1, 2, 3, 5, 10, 15, 20, 30]
AGREEMENT_MIN = 0.80
N_PER_FAMILY = 40
SEED = CANONICAL_SEED

# Expected construction population sizes, established in earlier landed bundles. Asserted
# rather than re-derived by calling the historical all-family loader, which would
# materialise every family including the sealed one.
EXPECTED_ELIGIBLE = {"Retrons": 95, "GII": 496, "DGRs": 488,
                     "CRISPR": 129, "UG3": 86, "AbiA": 19}

# Iteration order is LOAD-BEARING: a single shared RNG feeds negative-control generation, so
# visiting families in a different order changes which di-shuffles fail. This is the order
# used by every previous bundle and it is preserved verbatim so the control populations -
# and the failed-replicate identities - reproduce exactly.
CONSTRUCTION_ORDER = list(CANONICAL_FAMILY_ORDER)


# Fails closed if the order or seed ever drifts from the canonical pair.
assert_canonical(CONSTRUCTION_ORDER, SEED)


def anchor_calls(states, leng, pp_hi):
    return sum(1 for s in ANCH if s <= leng and states[s]["residue_index"] is not None
               and states[s]["posterior"] is not None and states[s]["posterior"] >= pp_hi)


def main():
    fams = authorised_families()
    elig = load_families(fams)

    # population check: the scoped loader must reproduce the established counts exactly.
    mismatches = {f: (len(elig.get(f, {})), EXPECTED_ELIGIBLE.get(f))
                  for f in EXPECTED_ELIGIBLE
                  if len(elig.get(f, {})) != EXPECTED_ELIGIBLE.get(f)}
    if mismatches:
        raise SystemExit(f"FAIL CLOSED: scoped loader population differs from the "
                         f"established construction counts: {mismatches}")
    with open(f"{TABLES}/loader_population_check.tsv", "w") as f:
        f.write("family\texpected_eligible\tobserved_eligible\tmatch\n")
        for fam in CONSTRUCTION_ORDER:
            f.write(f"{fam}\t{EXPECTED_ELIGIBLE[fam]}\t{len(elig[fam])}\tYES\n")

    leng = hmm_leng(HMM)
    rng = random.Random(SEED)
    real, negs = {}, {}
    att_ids, val_ids, fail_ids, fail_src = {}, {}, {}, {}
    for fam in CONSTRUCTION_ORDER:
        seqs = {k: v for k, v in sorted(elig[fam].items())[:N_PER_FAMILY]}
        real[fam] = seqs
        (negs[fam], att_ids[fam], val_ids[fam],
         fail_ids[fam], fail_src[fam]) = make_negatives(seqs, rng)

    # ---- align once; sweep thresholds over stored posteriors -------------------------
    rs, nd, rd = {}, collections.defaultdict(dict), {}
    ns = collections.defaultdict(dict)
    for fam in CONSTRUCTION_ORDER:
        m, _, _ = state_to_residue(HMM, real[fam], WORK, f"cal_{fam}")
        rs[fam] = m
        rd[fam] = domain_scores(HMM, f"{WORK}/cal_{fam}.faa", WORK, f"cal_{fam}")
        for kind, d in negs[fam].items():
            if not d:
                continue
            mm, _, _ = state_to_residue(HMM, d, WORK, f"cal_{fam}_{kind}")
            ns[fam][kind] = mm
            nd[fam][kind] = domain_scores(HMM, f"{WORK}/cal_{fam}_{kind}.faa", WORK,
                                          f"cal_{fam}_{kind}")

    sweep, chosen_pp = [], None
    for pp in PP_HI_GRID:
        rv = [anchor_calls(st, leng, pp) / len(ANCH)
              for fam in rs for st in rs[fam].values()]
        nv = sorted(anchor_calls(st, leng, pp)
                    for fam in ns for kind in ns[fam] for st in ns[fam][kind].values())
        p95 = nv[min(int(0.95 * len(nv)), len(nv) - 1)]
        med = statistics.median(rv)
        ok = (p95 == 0) and (med >= 0.50)
        sweep.append([f"{pp:.2f}", f"{med:.4f}", str(p95), str(max(nv)),
                      "PASS" if ok else "fail"])
        if ok and chosen_pp is None:
            chosen_pp = pp
    if chosen_pp is None:
        raise SystemExit("FAIL CLOSED: no PP_HI in the declared grid meets both targets")

    neg_dom_max = max(sc for fam in nd for kind in nd[fam]
                      for sc, _ in nd[fam][kind].values())
    s_min = next((g for g in S_MIN_GRID if g > neg_dom_max), None)
    neg_map_max = max(anchor_calls(st, leng, chosen_pp)
                      for fam in ns for kind in ns[fam] for st in ns[fam][kind].values())
    k_min = next((g for g in K_MIN_GRID if g > neg_map_max), None)
    if s_min is None or k_min is None:
        raise SystemExit("FAIL CLOSED: no grid value exceeds the observed negative maximum")

    per_seq = sorted(anchor_calls(st, leng, chosen_pp) / len(ANCH)
                     for fam in rs for st in rs[fam].values())
    t1 = int(per_seq[max(0, int(0.05 * len(per_seq)) - 1)] * 100) / 100.0
    fam_med = {fam: statistics.median(anchor_calls(st, leng, chosen_pp) / len(ANCH)
                                      for st in rs[fam].values()) for fam in rs}
    d_max = math.ceil((max(fam_med.values()) - min(fam_med.values())) * 100) / 100.0
    rng2 = random.Random(SEED + 7)
    diffs = []
    for fam in rs:
        vals = [anchor_calls(st, leng, chosen_pp) / len(ANCH) for st in rs[fam].values()]
        if len(vals) < 10:
            continue
        for _ in range(2000):
            v = vals[:]
            rng2.shuffle(v)
            h = len(v) // 2
            diffs.append(abs(statistics.median(v[:h]) - statistics.median(v[h:])))
    diffs.sort()
    d_random = math.ceil(diffs[int(0.95 * len(diffs))] * 1000) / 1000.0

    with open(f"{TABLES}/support_rule_calibration.tsv", "w") as f:
        f.write("pp_hi\tmedian_real_mapped_fraction\tnegative_p95_mapped\t"
                "negative_max_mapped\tmeets_both_targets\n")
        for r in sweep:
            f.write("\t".join(r) + "\n")

    with open(f"{CONTROL}/SUPPORT_RULE_FROZEN.tsv", "w") as f:
        f.write("parameter\tvalue\tderivation\n")
        f.write(f"PP_LO\t{PP_LO}\tfixed by principle (posterior below 0.5 means the reported "
                f"placement is a minority against all alternatives combined); not searched\n")
        f.write(f"PP_HI\t{chosen_pp}\tsmallest of grid {PP_HI_GRID} with pooled negative p95==0 "
                f"and median real fraction>=0.50\n")
        f.write(f"S_MIN\t{s_min}\tsmallest of grid {S_MIN_GRID} strictly > max negative domain "
                f"bitscore {neg_dom_max:.1f}\n")
        f.write(f"K_MIN\t{k_min}\tsmallest of grid {K_MIN_GRID} strictly > max negative "
                f"MAPPED-anchor count {neg_map_max}\n")
        f.write(f"T1\t{t1}\t5th percentile of per-sequence MAPPED fraction over construction\n")
        f.write(f"D_MAX\t{d_max}\tspread of construction family medians (predeclared C4 bound; "
                f"weak - see addendum)\n")
        f.write(f"D_RANDOM\t{d_random}\t95th pct |median diff| over 2000 random half-splits "
                f"(stricter companion diagnostic, reported not enforced)\n")
        f.write(f"N_ANCHORS\t{len(ANCH)}\tfrozen ALL_PARTNERS anchors, unchanged\n")
        f.write(f"CALIBRATION_FAMILIES\t{'|'.join(CONSTRUCTION_ORDER)}\t"
                f"construction only, supplied at runtime\n")

    # ---- negative control report, with failed IDs landed ------------------------------
    by_class = collections.defaultdict(list)
    failed_ids = collections.defaultdict(list)
    for fam in CONSTRUCTION_ORDER:
        for kind in ("MONO", "DI", "REV"):
            if kind in ns[fam]:
                by_class[kind] += [anchor_calls(st, leng, chosen_pp)
                                   for st in ns[fam][kind].values()]
            failed_ids[kind] += fail_src[fam][kind]

    with open(f"{TABLES}/negative_control_summary.tsv", "w") as f:
        f.write("# per-class AND pooled. The pooled p95 of 0 hides the reverse class (p95 10).\n")
        for kind in ("MONO", "DI", "REV"):
            ids = sorted(failed_ids[kind])
            f.write(f"# {kind} intended null: {INTENDED_NULL[kind]}\n")
            f.write(f"# {kind} generation failures ({len(ids)}), NOT replaced: "
                    f"{','.join(ids) if ids else 'none'}\n")
        f.write("family\tcontrol_class\tn\tmax_mapped\tmean_mapped\tp95_mapped\t"
                "n_with_any_mapped\tmax_domain_bitscore\n")
        for fam in CONSTRUCTION_ORDER:
            for kind in ("MONO", "DI", "REV"):
                if kind not in ns[fam]:
                    continue
                vals = [anchor_calls(st, leng, chosen_pp) for st in ns[fam][kind].values()]
                ds = [sc for sc, _ in nd[fam][kind].values()] or [float("nan")]
                f.write(f"{fam}\t{kind}\t{len(vals)}\t{max(vals)}\t"
                        f"{statistics.mean(vals):.3f}\t{pctl(vals, 0.95)}\t"
                        f"{sum(1 for v in vals if v > 0)}\t{max(ds):.1f}\n")
        pooled = []
        for kind in ("MONO", "DI", "REV"):
            v = by_class[kind]
            pooled += v
            f.write(f"ALL\t{kind}\t{len(v)}\t{max(v)}\t{statistics.mean(v):.3f}\t"
                    f"{pctl(v, 0.95)}\t{sum(1 for x in v if x > 0)}\tNA\n")
        f.write(f"ALL\tPOOLED\t{len(pooled)}\t{max(pooled)}\t{statistics.mean(pooled):.3f}\t"
                f"{pctl(pooled, 0.95)}\t{sum(1 for x in pooled if x > 0)}\tNA\n")

    with open(f"{TABLES}/control_failed_replicates.tsv", "w") as f:
        f.write("# Failed generations, landed by IDENTITY. Never substituted.\n")
        f.write("control_class\tn_failed\tfailed_sequence_ids\n")
        for kind in ("MONO", "DI", "REV"):
            ids = sorted(failed_ids[kind])
            f.write(f"{kind}\t{len(ids)}\t{','.join(ids) if ids else 'none'}\n")

    # ---- catalytic derivation, MAPPED-only -------------------------------------------
    modal, excluded, n_dyad = collections.Counter(), [], 0
    per_fam = collections.defaultdict(lambda: [0, 0])
    cs = {}
    for fam in CONSTRUCTION_ORDER:
        m, _, _ = state_to_residue(HMM, real[fam], WORK, f"cat_{fam}",
                                   pp_hi=chosen_pp, pp_lo=PP_LO)
        cs[fam] = m
        for sid, seq in sorted(real[fam].items()):
            r2s = {m[sid][s]["residue_index"]: s for s in range(1, leng + 1)
                   if m[sid][s]["residue_index"] is not None}
            occ = [(mm.start() + 1, r2s.get(mm.start() + 1), mm.group(0))
                   for mm in DYAD.finditer(seq)]
            if not occ:
                continue
            n_dyad += 1
            per_fam[fam][0] += 1
            for p, st, motif in occ:
                call = m[sid][st]["call"] if st else "NOT_IN_MATCH_COLUMN"
                if st is not None and call == "MAPPED":
                    modal[st] += 1
                else:
                    post = m[sid][st]["posterior"] if st else None
                    excluded.append([fam, sid, str(p), str(st or ""), motif, call,
                                     "" if post is None else f"{post:.2f}",
                                     "EXCLUDED_FROM_POSITIVE_EVIDENCE"])
    if not modal:
        raise SystemExit("FAIL CLOSED: no MAPPED dyad occurrence maps to any HMM state")
    cat_state, cat_n = modal.most_common(1)[0]
    top = modal.most_common(5)

    agree, rows = 0, []
    for fam in CONSTRUCTION_ORDER:
        m = cs[fam]
        for sid, seq in sorted(real[fam].items()):
            if not DYAD.search(seq):
                continue
            st = m[sid][cat_state]
            hit = (st["call"] == "MAPPED" and st["residue_index"] is not None
                   and bool(DYAD.match(seq[st["residue_index"] - 1:st["residue_index"] + 3])))
            agree += hit
            per_fam[fam][1] += hit
            rows.append([fam, sid, str(len(DYAD.findall(seq))), str(cat_state),
                         str(st["residue_index"] or ""), st["aa"], st["call"],
                         "YES" if hit else "NO"])
    frac = agree / n_dyad if n_dyad else 0.0
    if frac < AGREEMENT_MIN:
        raise SystemExit(f"FAIL CLOSED: catalytic agreement {frac:.4f} < {AGREEMENT_MIN}")

    with open(f"{TABLES}/catalytic_state_derivation.tsv", "w") as f:
        f.write("family\tsequence_id\tn_motifs\tcat_state\tresidue_at_cat_state\t"
                "aa_at_cat_state\tcall_at_cat_state\tmapped_motif_at_cat_state\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    with open(f"{TABLES}/catalytic_excluded_occurrences.tsv", "w") as f:
        f.write("# Motif occurrences NOT counted as positive catalytic evidence because the\n"
                "# call at the mapped state is not exactly MAPPED. Retained as diagnostics.\n")
        f.write("family\tsequence_id\tresidue_index\thmm_state\tmotif\tcall\tposterior\t"
                "disposition\n")
        for r in excluded:
            f.write("\t".join(r) + "\n")
    with open(f"{TABLES}/catalytic_state_candidates.tsv", "w") as f:
        f.write("# MAPPED-only counts\nhmm_state\tn_mapped_motif_occurrences\n")
        for st, n in top:
            f.write(f"{st}\t{n}\n")
    with open(f"{TABLES}/catalytic_state_agreement.tsv", "w") as f:
        f.write("family\tn_dyad_bearing\tn_mapped_motif_at_cat_state\tfraction\n")
        for fam in CONSTRUCTION_ORDER:
            a, b = per_fam[fam]
            f.write(f"{fam}\t{a}\t{b}\t{(b/a if a else 0):.4f}\n")
        f.write(f"ALL\t{n_dyad}\t{agree}\t{frac:.4f}\n")
    with open(f"{CONTROL}/CATALYTIC_STATE_FROZEN.tsv", "w") as f:
        f.write("parameter\tvalue\tderivation\n")
        f.write(f"CAT_STATE\t{cat_state}\tmodal HMM state of MAPPED [YF].DD occurrences over "
                f"{n_dyad} dyad-bearing construction sequences\n")
        f.write(f"CAT_STATE_COUNT\t{cat_n}\tMAPPED motif occurrences at CAT_STATE\n")
        f.write(f"RUNNER_UP_STATE\t{top[1][0]}\t{top[1][1]} MAPPED occurrences\n")
        f.write(f"CONSTRUCTION_AGREEMENT\t{frac:.4f}\t{agree}/{n_dyad}, predeclared minimum "
                f"{AGREEMENT_MIN}\n")
        f.write(f"AGREEMENT_MIN\t{AGREEMENT_MIN}\tpredeclared falsification condition\n")
        f.write(f"N_EXCLUDED_NON_MAPPED\t{len(excluded)}\tlanded in "
                f"catalytic_excluded_occurrences.tsv\n")

    # ---- construction validation -----------------------------------------------------
    fam_rows, seq_rows = [], []
    for fam in CONSTRUCTION_ORDER:
        m = cs[fam]
        dom = rd[fam]
        fr, ab, cat = [], collections.Counter(), collections.Counter()
        for sid, seq in sorted(real[fam].items()):
            v, reason, nm, na, nu, ndel = classify_sequence(m[sid], ANCH, leng, float(s_min),
                                                            k_min, dom.get(sid))
            fr.append(nm / len(ANCH))
            ab[reason] += 1
            st = m[sid][cat_state]
            if st["call"] == "DELETED_STATE":
                cv = "CATALYTIC_STATE_DELETED"
            elif st["call"] == "AMBIGUOUS":
                cv = "CATALYTIC_AMBIGUOUS"
            elif st["call"] == "UNSUPPORTED":
                cv = "CATALYTIC_UNSUPPORTED"
            else:
                ri = st["residue_index"]
                cv = ("CATALYTIC_CONFIRMED"
                      if ri and DYAD.match(seq[ri - 1:ri + 3]) else "CATALYTIC_SUBSTITUTED")
            cat[cv] += 1
            seq_rows.append([fam, sid, str(nm), str(na), str(nu), str(ndel),
                             f"{100*nm/len(ANCH):.1f}", v, reason,
                             f"{dom.get(sid, (float('nan'),))[0]:.1f}", cv])
        fam_rows.append([fam, str(len(real[fam])), f"{statistics.median(fr):.4f}",
                         f"{min(fr):.4f}", f"{max(fr):.4f}", str(ab["OK"]),
                         str(ab["NO_QUALIFYING_DOMAIN"]),
                         str(ab["INSUFFICIENT_SUPPORTED_ANCHORS"]),
                         str(cat["CATALYTIC_CONFIRMED"]), str(cat["CATALYTIC_SUBSTITUTED"]),
                         str(cat["CATALYTIC_AMBIGUOUS"] + cat["CATALYTIC_UNSUPPORTED"]),
                         str(cat["CATALYTIC_STATE_DELETED"])])

    with open(f"{TABLES}/construction_validation_family.tsv", "w") as f:
        f.write("family\tn\tmedian_mapped_fraction\tmin_mapped_fraction\t"
                "max_mapped_fraction\tn_ok\tn_abstain_no_domain\tn_abstain_few_anchors\t"
                "catalytic_confirmed\tcatalytic_substituted\t"
                "catalytic_ambiguous_or_unsupported\tcatalytic_state_deleted\n")
        for r in fam_rows:
            f.write("\t".join(r) + "\n")
        tot = ["TOTAL", str(sum(int(r[1]) for r in fam_rows)), "", "", ""] + \
              [str(sum(int(r[i]) for r in fam_rows)) for i in range(5, 12)]
        f.write("\t".join(tot) + "\n")
    with open(f"{TABLES}/construction_validation_sequence.tsv", "w") as f:
        f.write("family\tsequence_id\tn_mapped\tn_ambiguous\tn_unsupported\tn_deleted\t"
                "pct_mapped\tverdict\treason\tdomain_bitscore\tcatalytic_verdict\n")
        for r in seq_rows:
            f.write("\t".join(r) + "\n")

    # ---- C6 applied to the construction controls (demonstration of the frozen logic) ---
    # Identity vectors, aggregated across families in canonical order.
    attempted_all = {c: [i for fam in CONSTRUCTION_ORDER for i in att_ids[fam][c]]
                     for c in ("MONO", "DI", "REV")}
    valid_all = {c: [i for fam in CONSTRUCTION_ORDER for i in val_ids[fam][c]]
                 for c in ("MONO", "DI", "REV")}
    failed_all = {c: [i for fam in CONSTRUCTION_ORDER for i in fail_ids[fam][c]]
                  for c in ("MONO", "DI", "REV")}

    with open(f"{TABLES}/control_replicate_identities.tsv", "w") as f:
        f.write("# Replicate identity binding, produced in production and re-verified by C6.\n")
        f.write("# attempted == valid U failed, and valid & failed == empty, per class.\n")
        f.write("control_class\tn_attempted\tn_valid\tn_failed\tfailed_replicate_ids\n")
        for c in ("MONO", "DI", "REV"):
            fid = sorted(failed_all[c])
            f.write(f"{c}\t{len(attempted_all[c])}\t{len(valid_all[c])}\t{len(fid)}\t"
                    f"{','.join(fid) if fid else 'none'}\n")

    real_non_abstain = [int(r[2]) for r in seq_rows if r[7] != "ABSTAIN"]
    # The construction demonstration generates ONE replicate per sequence per class; the
    # UG25 confirmatory design specifies three. The design parameter is passed explicitly
    # so the replicate minimum matches the design actually run, and is never inferred.
    verdict, reasons, rep = evaluate_c6(dict(by_class), real_non_abstain,
                                        sum(len(real[f]) for f in real),
                                        attempted_ids_by_class=attempted_all,
                                        valid_ids_by_class=valid_all,
                                        failed_ids_by_class=failed_all,
                                        replicates_per_sequence=1)
    write_control_report(f"{TABLES}/c6_construction_evaluation.tsv", rep, verdict, reasons,
                         dict(failed_ids), INTENDED_NULL)

    with open(f"{TABLES}/canonical_order.tsv", "w") as f:
        f.write("# Load-bearing: a shared RNG feeds control generation, so this order\n")
        f.write("# determines which di-shuffles fail. NOT sorted. NOT derived.\n")
        f.write("parameter\tvalue\n")
        f.write(f"CANONICAL_FAMILY_ORDER\t{'|'.join(CANONICAL_FAMILY_ORDER)}\n")
        f.write(f"CANONICAL_SEED\t{CANONICAL_SEED}\n")
        f.write(f"CANONICAL_ORDER_HASH\t{CANONICAL_ORDER_HASH}\n")

    with open(f"{TABLES}/loader_materialisation_log.tsv", "w") as f:
        f.write("# every family label this process materialised, and how many sequences\n")
        f.write("family\tn_materialised\n")
        for k, v in sorted(materialisation_log().items()):
            f.write(f"{k}\t{v}\n")

    print(f"PP_HI={chosen_pp} S_MIN={s_min} K_MIN={k_min} T1={t1} D_MAX={d_max} "
          f"D_RANDOM={d_random}")
    print(f"CAT_STATE={cat_state} count={cat_n} runner_up={top[1]} "
          f"agreement={agree}/{n_dyad}={frac:.4f}")
    print(f"construction TOTAL n={tot[1]} ok={tot[5]}")
    print(f"C6 on construction controls: {verdict} {reasons}")
    print(f"di-shuffle failures: {sorted(failed_ids['DI'])}")
    print(f"materialised families: {sorted(materialisation_log())}")


if __name__ == "__main__":
    main()
