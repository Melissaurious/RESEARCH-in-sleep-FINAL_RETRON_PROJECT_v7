#!/usr/bin/env python3
"""s4 - re-read V4 mestre1926_in_toro_frame.sto: RT0 reach restricted to the CLEAN 1,814, and how
many 'upstream' residues actually sit in the fragment-artefact match states 1-67 vs insert columns.
Read-only; no alignment is recomputed."""
import csv, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_mestre, read_stockholm
V4 = Path("/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test")
from s2_toro_termini import hmm_map
mp = hmm_map(V4 / "cache/frame/toro742.hmm"); c2k = {c: k for k, c in mp.items()}
recs, rf = read_stockholm(V4 / "cache/frame/mestre1926_in_toro_frame.sto")
mcols = [i for i, c in enumerate(rf) if c not in ".~"]
ref, _ = load_mestre()
k68 = c2k[68]; bnd = mcols[k68 - 1]
blocks = [(1, 68, 79), (2, 96, 103), (3, 178, 182), (29, 1297, 1305)]
out = []
for label, keep in (("all_1926", lambda t: True), ("clean_1814", lambda t: not ref[t]["rescued"]), ("rescued_112", lambda t: ref[t]["rescued"])):
    rows = [(int(h.split("|")[0].split("_")[1]), s) for h, s in recs if h.startswith("terminal_")]
    rows = [(t, s) for t, s in rows if keep(t)]
    up = [sum(1 for c in s[:bnd] if c not in "-.") for _, s in rows]
    up_match = [sum(1 for i in mcols[:k68 - 1] if s[i] not in "-.") for _, s in rows]
    occ = {}
    for b, lo, hi in blocks:
        ks = [c2k[c] for c in range(lo, hi + 1)]
        occ[b] = round(st.mean(sum(1 for _, s in rows if s[mcols[k - 1]] not in "-.") / len(rows) for k in ks), 4)
    # C-terminal: residues downstream of block 29 end (state for col 1305)
    bend = mcols[c2k[1305] - 1]
    down = [sum(1 for c in s[bend + 1:] if c not in "-.") for _, s in rows]
    q = lambda x: (sorted(x)[len(x) // 4], st.median(x), sorted(x)[3 * len(x) // 4])
    r = dict(set=label, n=len(rows), block1_occ=occ[1], block2_occ=occ[2], block3_occ=occ[3], block29_RT7_occ=occ[29],
             upstream_of_col68_q1_med_q3=q(up), frac_gt20_upstream=round(sum(x > 20 for x in up) / len(up), 4),
             upstream_residues_in_flank_match_states_1_67_med=st.median(up_match),
             frac_upstream_residues_in_flank_match_states=round(sum(up_match) / max(1, sum(up)), 4),
             downstream_of_col1305_q1_med_q3=q(down))
    out.append(r); print(r)
with open(Path(__file__).resolve().parents[1] / "mestre_rt0_reach_clean_vs_all.tsv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]), delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(out)
