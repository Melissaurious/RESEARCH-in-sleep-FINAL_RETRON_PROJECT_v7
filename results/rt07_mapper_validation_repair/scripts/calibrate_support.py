#!/usr/bin/env python3
"""REPAIR 3 + 5 - derive the support rule from CONSTRUCTION DATA ONLY.

Executes control/SUPPORT_RULE_PREDECLARATION.md literally. No G2L object and no UG25 object is
read, at any point, for any purpose. The only families opened are the six construction families.
"""
import collections, os, random, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper_v2 import (BIN, hmm_leng, state_to_residue, domain_scores, PP_LOWER)
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
                   "rt07_g4a_repaired/scripts")
from repaired_lib import eligible_by_family

WORK, TABLES, CONTROL = sys.argv[1], sys.argv[2], sys.argv[3]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
ANCH = sorted(int(l.split("\t")[2]) for l in open(
    "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_ug5_holdout_gate/"
    "tables/ug5_frozen_anchor_coordinates.tsv") if not l.startswith("anchor_index"))

CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
FORBIDDEN = {"G2L", "UG25"}
PP_LO = 0.50
PP_HI_GRID = [0.55, 0.65, 0.75, 0.85, 0.95]
S_MIN_GRID = [0, 2, 4, 6, 8, 10, 15, 20, 30]
K_MIN_GRID = [1, 2, 3, 5, 10, 15, 20, 30]
N_PER_FAMILY = 40
SEED = 20260917

random.seed(SEED)


def di_shuffle(seq, rng, tries=200):
    """Altschul-Erikson dipeptide shuffle: preserves EVERY adjacent-pair count exactly.

    A plain greedy random Eulerian walk strands edges and fails almost every time (observed:
    0/19 successes). The Altschul-Erikson construction fixes it: for each vertex except the
    final residue, reserve one outgoing edge as its LAST edge, require those reserved edges to
    form a tree rooted at the final residue, then walk taking reserved edges last. That
    precondition is exactly what guarantees the walk consumes every edge.

    Returns None if no valid last-edge tree is found within `tries`; the caller counts those
    rather than silently substituting a weaker control.
    """
    if len(seq) < 3:
        return None
    first, last = seq[0], seq[-1]
    edges = collections.defaultdict(list)
    for a, b in zip(seq, seq[1:]):
        edges[a].append(b)
    verts = sorted(edges)
    total = len(seq) - 1

    for _ in range(tries):
        last_edge, ok = {}, True
        for v in verts:
            if v != last:
                last_edge[v] = rng.choice(edges[v])
        # every reserved edge must lead to `last` without cycling
        for v in last_edge:
            seen, u = set(), v
            while u != last:
                if u in seen or u not in last_edge:
                    ok = False
                    break
                seen.add(u)
                u = last_edge[u]
            if not ok:
                break
        if not ok:
            continue
        rem = {v: list(edges[v]) for v in verts}
        for v, e in last_edge.items():
            rem[v].remove(e)
            rng.shuffle(rem[v])
            rem[v].append(e)          # reserved edge goes last
        if last in rem:
            rng.shuffle(rem[last])
        out, cur = [first], first
        while len(out) - 1 < total and rem.get(cur):
            nxt = rem[cur].pop(0)
            out.append(nxt)
            cur = nxt
        if len(out) == len(seq):
            return "".join(out)
    return None


DI_FAILURES = collections.Counter()


def negatives(seqs, rng):
    mono, di, rev = {}, {}, {}
    for sid, s in sorted(seqs.items()):
        l = list(s)
        rng.shuffle(l)
        mono[sid + "_MONO"] = "".join(l)
        d = di_shuffle(s, rng)
        if d:
            assert collections.Counter(zip(d, d[1:])) == collections.Counter(zip(s, s[1:])), \
                f"di_shuffle broke dipeptide composition for {sid}"
            di[sid + "_DI"] = d
        else:
            DI_FAILURES[sid] += 1
    rev.update({sid + "_REV": s[::-1] for sid, s in sorted(seqs.items())})
    if not di:
        raise SystemExit("FAIL CLOSED: di-shuffle produced no sequences; the negative control "
                         "would silently degrade to mono-shuffle only")
    return mono, di, rev


def anchor_calls(states, leng, pp_hi):
    """Recompute calls at a candidate PP_HI from stored posteriors - no realignment."""
    n = 0
    for s in ANCH:
        if s > leng:
            continue
        st = states[s]
        if st["residue_index"] is not None and st["posterior"] is not None \
                and st["posterior"] >= pp_hi:
            n += 1
    return n


def main():
    elig = eligible_by_family()
    assert not (FORBIDDEN & set(CONSTRUCTION)), "construction list is contaminated"
    real, negs = {}, {}
    rng = random.Random(SEED)
    for fam in CONSTRUCTION:
        seqs = {k: v for k, v in sorted(elig[fam].items())[:N_PER_FAMILY]}
        real[fam] = seqs
        mono, di, rev = negatives(seqs, rng)
        negs[fam] = dict(MONO=mono, DI=di, REV=rev)

    # --- align everything once; thresholds are then swept over stored posteriors -----------
    leng = hmm_leng(HMM)
    real_states, neg_states = {}, collections.defaultdict(dict)
    real_dom, neg_dom = {}, collections.defaultdict(dict)
    for fam in CONSTRUCTION:
        m, _, L = state_to_residue(HMM, real[fam], WORK, f"cal_{fam}")
        real_states[fam] = m
        real_dom[fam] = domain_scores(HMM, f"{WORK}/cal_{fam}.faa", WORK, f"cal_{fam}")
        for kind, d in negs[fam].items():
            mm, _, _ = state_to_residue(HMM, d, WORK, f"cal_{fam}_{kind}")
            neg_states[fam][kind] = mm
            neg_dom[fam][kind] = domain_scores(HMM, f"{WORK}/cal_{fam}_{kind}.faa", WORK,
                                               f"cal_{fam}_{kind}")

    # --- PP_HI grid sweep ------------------------------------------------------------------
    sweep = []
    chosen_pp = None
    for pp in PP_HI_GRID:
        rvals = [anchor_calls(st, leng, pp) / len(ANCH)
                 for fam in CONSTRUCTION for st in real_states[fam].values()]
        nvals = [anchor_calls(st, leng, pp)
                 for fam in CONSTRUCTION for kind in neg_states[fam]
                 for st in neg_states[fam][kind].values()]
        nvals.sort()
        p95 = nvals[min(int(0.95 * len(nvals)), len(nvals) - 1)]
        med_real = statistics.median(rvals)
        ok = (p95 == 0) and (med_real >= 0.50)
        sweep.append([f"{pp:.2f}", f"{med_real:.4f}", str(p95), str(max(nvals)),
                      "PASS" if ok else "fail"])
        if ok and chosen_pp is None:
            chosen_pp = pp
    if chosen_pp is None:
        raise SystemExit("FAIL CLOSED: no PP_HI in the declared grid satisfies both targets. "
                         "Grid is not widened and targets are not relaxed.")

    # --- S_MIN: smallest grid value strictly above the max negative domain score -----------
    neg_dom_max = max([sc for fam in CONSTRUCTION for kind in neg_dom[fam]
                       for sc, _ in neg_dom[fam][kind].values()] or [float("-inf")])
    s_min = next((g for g in S_MIN_GRID if g > neg_dom_max), None)
    if s_min is None:
        raise SystemExit(f"FAIL CLOSED: no S_MIN grid value exceeds negative max {neg_dom_max}")

    # --- K_MIN: smallest grid value strictly above the max negative MAPPED-anchor count ----
    neg_map_max = max(anchor_calls(st, leng, chosen_pp)
                      for fam in CONSTRUCTION for kind in neg_states[fam]
                      for st in neg_states[fam][kind].values())
    k_min = next((g for g in K_MIN_GRID if g > neg_map_max), None)
    if k_min is None:
        raise SystemExit(f"FAIL CLOSED: no K_MIN grid value exceeds negative max {neg_map_max}")

    # --- criteria thresholds T1 / D_MAX (repair 5) -----------------------------------------
    per_seq = [anchor_calls(st, leng, chosen_pp) / len(ANCH)
               for fam in CONSTRUCTION for st in real_states[fam].values()]
    per_seq.sort()
    t1 = int(per_seq[max(0, int(0.05 * len(per_seq)) - 1)] * 100) / 100.0
    fam_med = {fam: statistics.median(
        anchor_calls(st, leng, chosen_pp) / len(ANCH) for st in real_states[fam].values())
        for fam in CONSTRUCTION}
    import math
    d_max = math.ceil((max(fam_med.values()) - min(fam_med.values())) * 100) / 100.0

    # ADDENDUM 1: D_MAX above is the spread BETWEEN construction families, which is a very
    # permissive bound for two components WITHIN one family - criterion C4 would stay nearly
    # unfalsifiable. Within-family component spread cannot be measured on construction (only
    # GII/CRISPR/Retrons have a second component, of size 1, 4 and 1). So we also derive a
    # same-population null: the 95th percentile of |median(A) - median(B)| over random
    # half-splits of each construction family. Reported alongside; C4 keeps its predeclared
    # bound and D_RANDOM is the stricter companion diagnostic.
    rng2 = random.Random(SEED + 7)
    diffs = []
    for fam in CONSTRUCTION:
        vals = [anchor_calls(st, leng, chosen_pp) / len(ANCH)
                for st in real_states[fam].values()]
        if len(vals) < 10:
            continue
        for _ in range(2000):
            v = vals[:]
            rng2.shuffle(v)
            h = len(v) // 2
            diffs.append(abs(statistics.median(v[:h]) - statistics.median(v[h:])))
    diffs.sort()
    d_random = math.ceil(diffs[int(0.95 * len(diffs))] * 1000) / 1000.0 if diffs else None

    # --- land ------------------------------------------------------------------------------
    with open(f"{TABLES}/support_rule_calibration.tsv", "w") as f:
        f.write("pp_hi\tmedian_real_mapped_fraction\tnegative_p95_mapped\t"
                "negative_max_mapped\tmeets_both_targets\n")
        for r in sweep:
            f.write("\t".join(r) + "\n")

    with open(f"{TABLES}/negative_control_summary.tsv", "w") as f:
        f.write(f"# di-shuffle failed (no valid last-edge tree) for {sum(DI_FAILURES.values())} "
                f"sequence(s); those are ABSENT from the DI rows, which is why some DI n < real n\n")
        f.write("family\tcontrol_kind\tn\tmax_mapped_anchors\tmean_mapped_anchors\t"
                "n_with_any_mapped\tmax_domain_bitscore\n")
        for fam in CONSTRUCTION:
            for kind in ("MONO", "DI", "REV"):
                vals = [anchor_calls(st, leng, chosen_pp)
                        for st in neg_states[fam][kind].values()]
                ds = [sc for sc, _ in neg_dom[fam][kind].values()] or [float("nan")]
                f.write(f"{fam}\t{kind}\t{len(vals)}\t{max(vals)}\t{statistics.mean(vals):.3f}\t"
                        f"{sum(1 for v in vals if v > 0)}\t{max(ds):.1f}\n")

    with open(f"{CONTROL}/SUPPORT_RULE_FROZEN.tsv", "w") as f:
        f.write("parameter\tvalue\tderivation\n")
        f.write(f"PP_LO\t{PP_LO}\tfixed by principle (posterior<0.5 => competing path more likely); not searched\n")
        f.write(f"PP_HI\t{chosen_pp}\tsmallest of grid {PP_HI_GRID} with negative p95==0 and median real fraction>=0.50\n")
        f.write(f"S_MIN\t{s_min}\tsmallest of grid {S_MIN_GRID} strictly > max negative domain bitscore {neg_dom_max:.1f}\n")
        f.write(f"K_MIN\t{k_min}\tsmallest of grid {K_MIN_GRID} strictly > max negative MAPPED-anchor count {neg_map_max}\n")
        f.write(f"T1\t{t1}\t5th percentile of per-sequence MAPPED fraction over construction\n")
        f.write(f"D_MAX\t{d_max}\tspread of construction family medians, rounded up (PREDECLARED C4 bound; permissive)\n")
        f.write(f"D_RANDOM\t{d_random}\taddendum 1: 95th pct |median diff| over 2000 random half-splits per construction family (stricter companion diagnostic)\n")
        f.write(f"N_ANCHORS\t{len(ANCH)}\tfrozen ALL_PARTNERS anchors, unchanged\n")
        f.write(f"CALIBRATION_FAMILIES\t{'|'.join(CONSTRUCTION)}\tconstruction only; G2L and UG25 never read\n")

    with open(f"{TABLES}/construction_family_medians.tsv", "w") as f:
        f.write("family\tn\tmedian_mapped_fraction\n")
        for fam in CONSTRUCTION:
            f.write(f"{fam}\t{len(real_states[fam])}\t{fam_med[fam]:.4f}\n")

    print("PP_HI grid sweep:")
    for r in sweep:
        print(f"  pp_hi={r[0]} median_real={r[1]} neg_p95={r[2]} neg_max={r[3]} {r[4]}")
    print(f"\nFROZEN: PP_LO={PP_LO} PP_HI={chosen_pp} S_MIN={s_min} (neg max {neg_dom_max:.1f}) "
          f"K_MIN={k_min} (neg max {neg_map_max}) T1={t1} D_MAX={d_max} D_RANDOM={d_random}")
    print("family medians:", {k: round(v, 3) for k, v in fam_med.items()})


if __name__ == "__main__":
    main()
