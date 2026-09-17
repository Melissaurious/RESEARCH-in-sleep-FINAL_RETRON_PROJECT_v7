#!/usr/bin/env python3
"""g4a REPAIRED step 1 — split with an ENFORCED identity/coverage separation rule.

Replaces the cd-hit-membership split whose separation claim was false.
Roles are unions of connected components of the link graph, so every cross-role pair
is below the link rule BY CONSTRUCTION. The audit table verifies it empirically anyway.

Usage: step1_split.py <workdir> <tabledir>
"""
import sys, os, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repaired_lib import *          # noqa

WORK, TABLES = sys.argv[1], sys.argv[2]
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
LINEAGE = {"Retrons": "Retron", "GII": "GII_like", "DGRs": "DGR",
           "CRISPR": "CRISPR", "UG3": "UG", "UG5": "UG", "AbiA": "Abi"}
# what the ORIGINAL bundle landed, for the audit trail
ORIGINAL_PILOT = {"Retrons": 90, "GII": 111, "DGRs": 97, "CRISPR": 90,
                  "UG3": 86, "UG5": 67, "AbiA": 19}

os.makedirs(WORK, exist_ok=True)
os.makedirs(TABLES, exist_ok=True)
aud = Audit()

elig = eligible_by_family()
sel, roles, audit_pairs, clus_rows = [], {}, [], []

for fam in FAMILIES:
    d = elig[fam]
    n_av = len(d)
    small = n_av < SMALL_FAMILY_MAX
    pilot_n = min(n_av, PILOT_CAP)

    # ---- surface the ORIGINAL cap violation before repairing it
    if ORIGINAL_PILOT[fam] > PILOT_CAP:
        aud.add(f"pilot_cap.{fam}", f"<= {PILOT_CAP}", ORIGINAL_PILOT[fam],
                "original bundle, re-checked at repair time",
                "predeclaration violation: the original pilot exceeded the declared cap; "
                "population size and therefore every per-family statistic differed from the "
                "declared design",
                "components are now dealt only while the family total stays <= 90; a component "
                "that would overshoot is skipped",
                "YES for that family's landed per-family statistics")

    pairs = all_vs_all(d, WORK, fam)
    comps = components(list(d), pairs)
    sizes0 = sorted((len(c) for c in comps), reverse=True)
    # REPAIR 3 / ADDENDUM_2 s3: the 90%-dominance criterion, now registered.
    DOMINANCE = 0.90
    fragments = len(comps) > 1 and sizes0[0] <= DOMINANCE * n_av
    if not fragments:
        aud.add(f"within_family_independence.{fam}",
                "family fragments into components so an INDEPENDENT challenge set exists",
                f"{len(comps)} component(s); largest = {sizes0[0]} of {n_av} "
                f"({100*sizes0[0]/n_av:.1f}%)",
                "repaired split, before any repaired analysis was interpreted",
                "no independent within-family held-out set exists at the declared separation "
                "rule: the family is one homology component. Any within-family transfer or "
                "generalisation claim for this family is unsupportable",
                "PREDECLARATION_ADDENDUM_1 §3.3: derivation drawn deterministically from the "
                "dominant component (ids sorted, first k); remainder labelled "
                "NON_INDEPENDENT_CHALLENGE; no transfer claim made from it. Threshold NOT lowered",
                "YES for the original bundle's within-family transfer/holdout claims for this family")
        got = deterministic_draw(d, pilot_n, small)
        indep = "NON_INDEPENDENT_CHALLENGE"
    else:
        got = deal_components(comps, pilot_n, small)
        indep = "INDEPENDENT_CHALLENGE"

    n_taken = sum(len(v) for v in got.values())
    if n_taken > PILOT_CAP:
        aud.add(f"cap_enforcement.{fam}", f"<= {PILOT_CAP}", n_taken, "repaired split",
                "cap enforcement failed", "FAIL CLOSED", "YES")
        sys.exit(f"FAIL CLOSED: {fam} exceeded the cap after repair")

    for r, ids in got.items():
        for i in ids:
            roles[i] = (fam, r)

    # ---- empirical verification of the separation guarantee
    role_of = {i: r for r, ids in got.items() for i in ids}
    worst = collections.defaultdict(float)
    worst50 = collections.Counter()
    unordered50 = collections.defaultdict(set)
    for q, t, fi, qc, tc in pairs:
        rq, rt = role_of.get(q), role_of.get(t)
        if not rq or not rt or rq == rt:
            continue
        key = tuple(sorted((rq, rt)))
        worst[key] = max(worst[key], fi)
        viol = "YES" if (fi >= LINK_IDENTITY and min(qc, tc) >= LINK_COVERAGE) else "NO"
        if fi >= 0.50 and min(qc, tc) >= LINK_COVERAGE:
            worst50[key] += 1                       # directional rows
            unordered50[key].add(tuple(sorted((q, t))))   # REPAIR 3: unordered pairs
        if fi >= 0.25:          # only the near-threshold tail is landed, to keep the table bounded
            audit_pairs.append([fam, q, rq, t, rt, f"{fi:.4f}", f"{qc:.3f}", f"{tc:.3f}", viol])

    dc = worst.get(("challenge", "derivation"), 0.0)
    n50 = worst50.get(("challenge", "derivation"), 0)
    n50u = len(unordered50.get(("challenge", "derivation"), set()))
    if n50 and indep == "INDEPENDENT_CHALLENGE":
        aud.add(f"separation.{fam}", "0 derivation-challenge pairs at >=50% identity", n50,
                "repaired split", "separation rule breached", "FAIL CLOSED", "YES")
        sys.exit(f"FAIL CLOSED: {fam} has {n50} derivation-challenge pairs >= 50% identity")

    sizes = sorted((len(c) for c in comps), reverse=True)
    ncomp = {r: len({tuple(sorted(c)) for c in comps if set(c) & set(ids)})
             for r, ids in got.items()}
    for r, ids in got.items():
        if ids and ncomp[r] == 1 and fragments:
            aud.add(f"role_diversity.{fam}.{r}", ">1 independent component",
                    "1 component", "repaired split",
                    "that role is a single separation group, so it does not represent diverse "
                    "held-out sequence structure",
                    "reported and the role is flagged SINGLE_COMPONENT; the split is not forced",
                    "NO - the role is retained but its diversity claim is downgraded")
    clus_rows.append([fam, str(len(comps)), str(sizes[0]), str(sum(1 for s in sizes if s == 1)),
                      str(ncomp["derivation"]), str(ncomp["development"]),
                      str(ncomp["challenge"]),
                      indep])

    sel.append([fam, LINEAGE[fam], str(n_av), str(n_taken), indep,
                str(len(got["derivation"])), str(len(got["development"])),
                str(len(got["challenge"])), str(len(comps)),
                "SMALL_FAMILY" if small else "FULL_SPLIT",
                str(int(statistics.median([len(s) for s in d.values()]))),
                f"{dc:.4f}", str(n50), str(n50u), str(ORIGINAL_PILOT[fam])])

with open(f"{TABLES}/g4a_repaired_family_selection.tsv", "w") as f:
    f.write("family\tlineage\tN_eligible\tpilot_N_repaired\tchallenge_independence\t"
            "n_derivation\tn_development\t"
            "n_challenge\tn_separation_components\tsplit_mode\tmedian_len_aa\t"
            "max_derivation_challenge_identity\tn_directional_rows_ge50pct\t"
            "n_unordered_pairs_ge50pct\tpilot_N_original\n")
    for r in sel:
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_repaired_sequence_roles.tsv", "w") as f:
    f.write("sequence_id\tfamily\trole\tlength_aa\thas_dyad\tn_dyad_hits\n")
    for sid, (fam, r) in sorted(roles.items()):
        s = elig[fam][sid]
        hits = DYAD.findall(s)
        f.write(f"{sid}\t{fam}\t{r}\t{len(s)}\t{'YES' if hits else 'NO'}\t{len(hits)}\n")

with open(f"{TABLES}/g4a_split_pairwise_audit.tsv", "w") as f:
    f.write("family\tquery_id\tquery_role\treference_id\treference_role\tidentity\t"
            "query_coverage\treference_coverage\tviolates_rule\n")
    for r in sorted(audit_pairs, key=lambda x: (x[0], -float(x[5]), x[1], x[3])):
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_cluster_role_summary.tsv", "w") as f:
    f.write("family\tn_components\tlargest_component\tn_singleton_components\t"
            "n_components_derivation\tn_components_development\tn_components_challenge\t"
            "challenge_independence\n")
    for r in clus_rows:
        f.write("\t".join(r) + "\n")

# write the challenge/derivation FASTAs for the later steps
for fam in FAMILIES:
    for role in ("derivation", "development", "challenge"):
        ids = [i for i, (f, r) in roles.items() if f == fam and r == role]
        if ids:
            write_fasta({i: elig[fam][i] for i in ids}, f"{WORK}/{fam}.{role}.faa")

aud.write(f"{TABLES}/g4a_repair_audit.tsv")
print("step1 complete; audit rows:", len(aud.rows))
