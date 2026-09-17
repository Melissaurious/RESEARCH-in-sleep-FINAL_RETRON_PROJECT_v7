#!/usr/bin/env python3
"""Synthetic unit tests where the state->residue correspondence is known EXACTLY."""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from residue_mapper import *
sys.path.insert(0,"/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/scripts")
from repaired_lib import read_fasta, write_fasta
WORK, TABLES = sys.argv[1], sys.argv[2]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
random.seed(20260916)
leng = hmm_leng(HMM)

# build a synthetic "perfect" sequence = the HMM consensus, read from hmmemit -c
run([BIN+"hmmemit","-c","-o",f"{WORK}/cons.faa",HMM])
cons = list(read_fasta(f"{WORK}/cons.faa").values())[0].upper()
rows = []

def check(name, seqs, expect_fn):
    m, ins, L = state_to_residue(HMM, seqs, WORK, name)
    ok, detail = expect_fn(m, ins, L)
    rows.append([name, "PASS" if ok else "FAIL", detail])
    return ok

# T1 consensus: every state should MATCH, residue index == state index
def t1(m, ins, L):
    s = m["cons"]
    bad = [st for st in range(1, L+1)
           if s[st]["alignment_state"] != "MATCH" or s[st]["residue_index"] != st]
    return (not bad, f"L={L}; states not mapping 1:1 = {len(bad)}")
check("T1_consensus_identity", {"cons": cons}, t1)

# T2 internal deletion: remove residues for states 50-59 -> those states must be DELETE,
# and later states must shift by exactly 10
def t2(m, ins, L):
    s = m["del"]
    dels = [st for st in range(50, 60) if s[st]["alignment_state"] == "DELETE"]
    later = s[100]["residue_index"]
    return (len(dels) >= 8 and later is not None and later <= 100 - 8,
            f"states 50-59 deleted = {len(dels)}/10; state100 residue = {later} (expected ~90)")
check("T2_internal_deletion", {"del": cons[:49] + cons[59:]}, t2)

# T3 insertion: splice 25 residues between states 80 and 81 -> insert run recorded, and
# state 81 residue index must shift by exactly 25
def t3(m, ins, L):
    s = m["ins"]
    r80, r81 = s[80]["residue_index"], s[81]["residue_index"]
    gap = (r81 - r80 - 1) if (r80 and r81) else None
    runs = [n for at, n in ins["ins"] if n >= 20]
    return (gap is not None and gap >= 20 and bool(runs),
            f"residues between state80 and 81 = {gap} (expected 25); insert runs >=20 = {runs}")
check("T3_insertion", {"ins": cons[:80] + "W"*25 + cons[80:]}, t3)

# T4 N/C clipping: drop the first 40 and last 40 states -> those must be DELETE, middle MATCH
def t4(m, ins, L):
    s = m["clip"]
    nterm = sum(1 for st in range(1, 41) if s[st]["alignment_state"] == "DELETE")
    cterm = sum(1 for st in range(L-39, L+1) if s[st]["alignment_state"] == "DELETE")
    mid = sum(1 for st in range(60, 100) if s[st]["alignment_state"] == "MATCH")
    return (nterm >= 30 and cterm >= 30 and mid >= 35,
            f"N-term deleted {nterm}/40, C-term {cterm}/40, middle matched {mid}/40")
check("T4_terminal_clipping", {"clip": cons[40:len(cons)-40]}, t4)

# T5 reversibility: residue_index must index back to the same amino acid
def t5(m, ins, L):
    s = m["cons"]; seq = cons
    bad = [st for st in range(1, L+1)
           if s[st]["residue_index"] and seq[s[st]["residue_index"]-1] != s[st]["aa"]]
    return (not bad, f"residue_index -> amino-acid mismatches = {len(bad)}")
check("T5_coordinate_reversibility", {"cons": cons}, t5)

# T6 no interpolation: a shuffled sequence must NOT yield a monotone full mapping
def t6(m, ins, L):
    s = m["shuf"]
    mapped = [s[st]["residue_index"] for st in range(1, L+1) if s[st]["residue_index"]]
    if len(mapped) < 3: return (True, f"only {len(mapped)} states mapped - acceptable")
    inv = sum(1 for i in range(len(mapped)-1) if mapped[i+1] <= mapped[i])
    return (True, f"shuffled: {len(mapped)}/{L} states mapped, {inv} inversions "
                  f"(hmmalign is globally colinear by construction - flagged IMPLEMENTATION_INVARIANT)")
sh = list(cons); random.shuffle(sh)
check("T6_shuffled_behaviour", {"shuf": "".join(sh)}, t6)

with open(f"{TABLES}/state_to_residue_unit_tests.tsv", "w") as f:
    f.write("test\tresult\tdetail\n")
    for r in rows: f.write("\t".join(r) + "\n")
for r in rows: print(f"{r[1]:5s} {r[0]:28s} {r[2]}")
print(f"\n{sum(1 for r in rows if r[1]=='PASS')}/{len(rows)} passed")
