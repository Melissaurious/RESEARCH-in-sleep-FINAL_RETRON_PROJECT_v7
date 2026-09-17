#!/usr/bin/env python3
"""g4a — the retron derivation/development/challenge split, as a reproducible table.

Derived from the landed g4a_family_selection.tsv and g4a_sequence_roles.tsv, so it
carries no independent assumptions.

Usage: g4a_retron_split.py <tabledir>
"""
import sys, collections, statistics

T = sys.argv[1]
sel = {r[0]: r for r in
       [l.rstrip("\n").split("\t") for l in open(f"{T}/g4a_family_selection.tsv")][1:]}
roles = [l.rstrip("\n").split("\t") for l in open(f"{T}/g4a_sequence_roles.tsv")][1:]

ret = [r for r in roles if r[1] == "Retrons"]
byrole = collections.Counter(r[2] for r in ret)
dy = collections.Counter(r[2] for r in ret if r[4] == "YES")
multi = collections.Counter(r[2] for r in ret if int(r[5]) > 1)
lens = collections.defaultdict(list)
for r in ret:
    lens[r[2]].append(int(r[3]))

out = ["\t".join(["role", "n", "n_with_dyad", "pct_with_dyad", "n_with_multiple_dyads",
                  "len_min", "len_median", "len_max"])]
for role in ("derivation", "development", "challenge"):
    n = byrole[role]
    out.append("\t".join([role, str(n), str(dy[role]), f"{100*dy[role]/n:.1f}",
                          str(multi[role]), str(min(lens[role])),
                          str(int(statistics.median(lens[role]))), str(max(lens[role]))]))
s = sel["Retrons"]
for k, v in (("TOTAL_PILOT", s[3]), ("N_ELIGIBLE_IN_myRT", s[2]),
             ("NOT_DRAWN_INTO_PILOT", str(int(s[2]) - int(s[3]))),
             ("cdhit_clusters_at_0.50", s[7]), ("singleton_clusters", s[8])):
    out.append("\t".join([k, v, "", "", "", "", "", ""]))

open(f"{T}/g4a_retron_split.tsv", "w").write("\n".join(out) + "\n")
print("retron split written")
