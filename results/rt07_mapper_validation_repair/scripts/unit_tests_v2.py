#!/usr/bin/env python3
"""REPAIR 4 - non-vacuous test suite.

Every test declares, in the landed matrix: what makes it PASS, what makes it FAIL, its positive
control and its negative control. Where a negative control is executable it is EXECUTED, and the
test fails if the negative control does not trigger.

The v1 suite's T6 returned (True, ...) on every branch - it reported PASS while asserting
nothing. Its replacement (U6) asserts in both directions and can fail.

Classification per test:
    FALSIFIABLE_EMPIRICAL_TEST  some input makes it fail
    IMPLEMENTATION_INVARIANT    true by construction of the tool; NOT evidence of transfer
"""
import collections, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapper_v2 import (BIN, run, hmm_leng, state_to_residue, read_stockholm,
                       domain_scores, classify_sequence)
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
                   "rt07_g4a_repaired/scripts")
from repaired_lib import read_fasta, eligible_by_family

WORK, TABLES, CONTROL = sys.argv[1], sys.argv[2], sys.argv[3]
G4A = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_g4a_repaired/work"
HMM = f"{G4A}/GII.deriv.hmm"
ANCH = sorted(int(l.split("\t")[2]) for l in open(
    "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/rt07_ug5_holdout_gate/"
    "tables/ug5_frozen_anchor_coordinates.tsv") if not l.startswith("anchor_index"))
DYAD = re.compile(r"[YF].DD")
random.seed(20260917)

fz = {}
for ln in open(f"{CONTROL}/SUPPORT_RULE_FROZEN.tsv"):
    if not ln.startswith("parameter"):
        k, v, _ = ln.split("\t", 2)
        fz[k] = v
PP_HI, PP_LO = float(fz["PP_HI"]), float(fz["PP_LO"])
S_MIN, K_MIN = float(fz["S_MIN"]), int(fz["K_MIN"])
CAT_STATE = int([l.split("\t")[1] for l in open(f"{CONTROL}/CATALYTIC_STATE_FROZEN.tsv")
                 if l.startswith("CAT_STATE")][0])

leng = hmm_leng(HMM)
run([BIN + "hmmemit", "-c", "-o", f"{WORK}/u_cons.faa", HMM])
cons = list(read_fasta(f"{WORK}/u_cons.faa").values())[0].upper()

rows = []


def rec(name, cls, ok, detail, pass_when, fail_when, pos, neg):
    rows.append([name, cls, "PASS" if ok else "FAIL", detail, pass_when, fail_when, pos, neg])


def smap(seqs, tag):
    return state_to_residue(HMM, seqs, WORK, tag, pp_hi=PP_HI, pp_lo=PP_LO)


# ---------------------------------------------------------------- U1 consensus, EXACT ------
m, ins, L = smap({"cons": cons}, "u1")
s = m["cons"]
ok_1_470 = all(s[st]["call"] in ("MAPPED", "AMBIGUOUS") and s[st]["residue_index"] == st
               for st in range(1, 471))
# negative control: a sequence with a real internal deletion must NOT satisfy the same check
mneg, _, _ = smap({"d": cons[:49] + cons[59:]}, "u1neg")
sneg = mneg["d"]
neg_triggers = not all(sneg[st]["residue_index"] == st for st in range(1, 471))
rec("U1_consensus_maps_1to1_states_1_470", "FALSIFIABLE_EMPIRICAL_TEST",
    ok_1_470 and neg_triggers,
    f"states 1-470 exact={ok_1_470}; deletion-variant correctly differs={neg_triggers}",
    "every state 1-470 has residue_index == state",
    "any state 1-470 maps to a different residue or is deleted",
    "hmmemit consensus", "consensus with states 50-59 removed (EXECUTED)")

# ---------------------------------------------------------------- U2 terminal state --------
# Documents the v1 'T1 FAIL'. State 471's residue is placed in an INSERT column, so state 471
# reads DELETED_STATE and exactly one residue is insert-assigned. Asserted exactly, not waived.
tail_del = s[471]["call"] == "DELETED_STATE"
tail_ins = sum(n for _, n in ins["cons"]) == 1 and ins["cons"] == [(471, 1)]
rec("U2_terminal_state_471_exact", "FALSIFIABLE_EMPIRICAL_TEST", tail_del and tail_ins,
    f"state471={s[471]['call']}; insert runs={ins['cons']}",
    "state 471 is DELETED_STATE and exactly one residue is an insertion after state 471",
    "state 471 becomes MATCH, or the insertion count changes",
    "hmmemit consensus", "any sequence whose C-terminus aligns into state 471")

# ---------------------------------------------------------------- U3 deletion, EXACT -------
m3, _, _ = smap({"del": cons[:49] + cons[59:]}, "u3")
s3 = m3["del"]
d_exact = sum(1 for st in range(50, 60) if s3[st]["call"] == "DELETED_STATE") == 10
r100 = s3[100]["residue_index"] == 90
rec("U3_internal_deletion_exact", "FALSIFIABLE_EMPIRICAL_TEST", d_exact and r100,
    f"states 50-59 deleted exactly 10={d_exact}; state100 residue={s3[100]['residue_index']} (exactly 90 required)",
    "exactly states 50-59 DELETED and state 100 maps to residue exactly 90",
    "fewer/more than 10 deletions, or state 100 residue != 90",
    "consensus minus residues 50-59", "unmodified consensus (state 100 -> 100, EXECUTED in U1)")

# ---------------------------------------------------------------- U4 insertion, EXACT ------
m4, ins4, _ = smap({"ins": cons[:80] + "W" * 25 + cons[80:]}, "u4")
s4 = m4["ins"]
gap = s4[81]["residue_index"] - s4[80]["residue_index"] - 1
run25 = [(a, n) for a, n in ins4["ins"] if n == 25]
rec("U4_insertion_exact", "FALSIFIABLE_EMPIRICAL_TEST", gap == 25 and len(run25) == 1,
    f"residues between states 80 and 81 = {gap} (exactly 25 required); runs of 25 = {run25}",
    "exactly 25 residues between states 80 and 81, recorded as one insert run of exactly 25",
    "gap != 25, or the insert run is absent/split",
    "consensus with 25 W spliced after state 80", "unmodified consensus (gap 0)")

# ---------------------------------------------------------------- U5 clipping, EXACT ------
m5, _, _ = smap({"clip": cons[40:len(cons) - 40]}, "u5")
s5 = m5["clip"]
n40 = sum(1 for st in range(1, 41) if s5[st]["call"] == "DELETED_STATE")
c40 = sum(1 for st in range(leng - 39, leng + 1) if s5[st]["call"] == "DELETED_STATE")
mid = sum(1 for st in range(60, 100) if s5[st]["residue_index"] is not None)
rec("U5_terminal_clipping_exact", "FALSIFIABLE_EMPIRICAL_TEST",
    n40 == 40 and c40 == 40 and mid == 40,
    f"N-term deleted {n40}/40, C-term {c40}/40, middle present {mid}/40",
    "all 40 leading and all 40 trailing states DELETED, all 40 middle states present",
    "any clipped state retains a residue, or a middle state loses one",
    "consensus clipped 40 each end", "unmodified consensus (0 terminal deletions)")

# ---------------------------------------------------------------- U6 REPLACES vacuous T6 ---
# v1's T6 returned True on every branch. This asserts BOTH directions and can fail.
shuf = list(cons)
random.shuffle(shuf)
shuf = "".join(shuf)
m6, _, _ = smap({"shuf": shuf, "cons": cons}, "u6")
n_shuf = sum(1 for a in ANCH if a <= leng and m6["shuf"][a]["call"] == "MAPPED")
n_real = sum(1 for a in ANCH if a <= leng and m6["cons"][a]["call"] == "MAPPED")
rec("U6_shuffle_below_KMIN_real_above", "FALSIFIABLE_EMPIRICAL_TEST",
    n_shuf < K_MIN <= n_real,
    f"shuffled MAPPED={n_shuf} (must be < K_MIN={K_MIN}); real MAPPED={n_real} (must be >= K_MIN)",
    "shuffled consensus maps fewer than K_MIN anchors AND real consensus maps at least K_MIN",
    "a shuffle reaching K_MIN anchors, or the real consensus failing to",
    "hmmemit consensus", "composition-preserving shuffle of it (EXECUTED)")

# ---------------------------------------------------------------- U7 multiline Stockholm ---
# Stockholm is interleaved; a parser that keeps only the last block silently truncates.
sto = f"{WORK}/u6.sto"
aln, rf, pp = read_stockholm(sto)
blocks = sum(1 for ln in open(sto) if ln.startswith("#=GC RF"))
len_ok = all(len(v) == len(rf) for v in aln.values()) and \
         all(len(pp[k]) == len(rf) for k in pp)
rec("U7_multiline_stockholm_concatenated", "FALSIFIABLE_EMPIRICAL_TEST",
    blocks > 1 and len_ok and len(pp) == len(aln),
    f"{blocks} interleaved blocks; all seq/PP strings length {len(rf)}; PP present for {len(pp)}/{len(aln)}",
    "every sequence and PP string equals the RF length after concatenating all blocks",
    "any sequence or PP string shorter than RF (a block was dropped)",
    "a real multi-block hmmalign output", "single-block file would make blocks==1 and not exercise it")

# ---------------------------------------------------------------- U8 multi-motif ----------
# The G2L failure class: a spurious upstream FDDD plus the true dyad at CAT_STATE.
spur = "FDDD"
multi = cons[:20] + spur + cons[24:]
m8, _, _ = smap({"multi": multi}, "u8")
s8 = m8["multi"]
occ = [(mm.start() + 1, mm.group(0)) for mm in DYAD.finditer(multi)]
res2state = {s8[st]["residue_index"]: st for st in range(1, leng + 1)
             if s8[st]["residue_index"] is not None}
first_pos = occ[0][0] if occ else None
state_rule_residue = s8[CAT_STATE]["residue_index"]
motif_at_cat = state_rule_residue is not None and \
    bool(DYAD.match(multi[state_rule_residue - 1:state_rule_residue + 3]))
old_logic_wrong = first_pos is not None and first_pos != state_rule_residue
rec("U8_multimotif_state_rule_beats_motif_first", "FALSIFIABLE_EMPIRICAL_TEST",
    len(occ) >= 2 and motif_at_cat and old_logic_wrong,
    f"{len(occ)} motifs at {[p for p, _ in occ]}; state-anchored call -> residue "
    f"{state_rule_residue}; motif-first would have taken {first_pos}",
    "with >=2 motifs present, the CAT_STATE residue still begins a real dyad and differs "
    "from the first regex hit",
    "the state-anchored call lands on the spurious motif, or no second motif is constructed",
    "consensus with a spurious FDDD spliced at residue 21",
    "motif-first logic on the same sequence (EXECUTED, shown wrong)")

# ---------------------------------------------------------------- U9 ambiguity reachable --
# If AMBIGUOUS is never produced, the ambiguity implementation is as vacuous as v1's `ambrows`.
elig = eligible_by_family()
probe = {}
for fam in ["Retrons", "UG3", "AbiA"]:
    probe.update({k: v for k, v in sorted(elig[fam].items())[:15]})
m9, _, _ = smap(probe, "u9")
n_amb = sum(1 for sid in m9 for st in range(1, leng + 1) if m9[sid][st]["call"] == "AMBIGUOUS")
n_uns = sum(1 for sid in m9 for st in range(1, leng + 1) if m9[sid][st]["call"] == "UNSUPPORTED")
n_seq_amb = sum(1 for sid in m9
                if any(m9[sid][st]["call"] == "AMBIGUOUS" for st in range(1, leng + 1)))
rec("U9_ambiguity_state_is_reachable", "FALSIFIABLE_EMPIRICAL_TEST",
    n_amb > 0 and n_seq_amb > 0,
    f"{n_amb} AMBIGUOUS calls across {n_seq_amb}/{len(probe)} construction sequences; "
    f"{n_uns} UNSUPPORTED",
    "at least one real state is called AMBIGUOUS on construction data",
    "no state is ever AMBIGUOUS - which would mean the band is unreachable and the "
    "implementation vacuous",
    "45 construction sequences from the 3 lowest-callability families",
    "v1 behaviour: ambrows declared, never populated -> would score 0 here")

# ---------------------------------------------------------------- U10 abstention reachable -
junk = {"JUNK_RANDOM": "".join(random.choice("ACDEFGHIKLMNPQRSTVWY") for _ in range(400)),
        "JUNK_LOWCOMPLEX": "A" * 400}
m10, _, _ = smap(junk, "u10")
dom10 = domain_scores(HMM, f"{WORK}/u10.faa", WORK, "u10")
verd = {k: classify_sequence(m10[k], ANCH, leng, S_MIN, K_MIN, dom10.get(k)) for k in junk}
m10b, _, _ = smap({"cons": cons}, "u10b")
dom10b = domain_scores(HMM, f"{WORK}/u10b.faa", WORK, "u10b")
vcons = classify_sequence(m10b["cons"], ANCH, leng, S_MIN, K_MIN, dom10b.get("cons"))
reasons = {v[1] for v in verd.values()}
rec("U10_abstention_reachable_and_reason_coded", "FALSIFIABLE_EMPIRICAL_TEST",
    all(v[0] == "ABSTAIN" for v in verd.values()) and vcons[0] == "MAPPED",
    f"junk verdicts={{k: (v[0], v[1]) for k, v in verd.items()}}; consensus={vcons[0]}/{vcons[1]}"
    .replace("{k: (v[0], v[1]) for k, v in verd.items()}",
             str({k: (v[0], v[1]) for k, v in verd.items()})),
    "random and low-complexity sequences ABSTAIN with a reason code, and the real consensus "
    "does not abstain",
    "junk is accepted, or the real consensus abstains",
    "hmmemit consensus (must not abstain)", "random + poly-A sequences (EXECUTED)")

# ------------------------------------------------- U10b second reason code reachable -------
# A reason code that nothing can trigger is as vacuous as the old `ambrows`. This fragment
# has a STRONG qualifying domain, so it cannot abstain for lack of a domain; it lies outside
# the anchor span 107-317, so it maps no anchors. It separates the two reason codes.
frag = {"NTERM_1_100": cons[0:100]}
m10c, _, _ = smap(frag, "u10c")
dom10c = domain_scores(HMM, f"{WORK}/u10c.faa", WORK, "u10c")
v_frag = classify_sequence(m10c["NTERM_1_100"], ANCH, leng, S_MIN, K_MIN,
                           dom10c.get("NTERM_1_100"))
dom_score = dom10c.get("NTERM_1_100", (None,))[0]
rec("U10b_second_abstention_reason_reachable", "FALSIFIABLE_EMPIRICAL_TEST",
    v_frag[0] == "ABSTAIN" and v_frag[1] == "INSUFFICIENT_SUPPORTED_ANCHORS"
    and dom_score is not None and dom_score >= S_MIN,
    f"domain bitscore={dom_score} (>= S_MIN={S_MIN}, so NOT a domain failure); "
    f"anchors MAPPED={v_frag[2]}; verdict={v_frag[0]}/{v_frag[1]}",
    "a fragment with a strong domain but no anchor coverage abstains specifically for "
    "INSUFFICIENT_SUPPORTED_ANCHORS",
    "it abstains for the wrong reason, or is accepted despite mapping no anchors",
    "consensus states 1-100 (outside the 107-317 anchor span)",
    "junk sequences in U10, which abstain for the OTHER reason (EXECUTED)")

# ---------------------------------------------------------------- U11 reversibility --------
bad = [st for st in range(1, leng + 1)
       if s[st]["residue_index"] and cons[s[st]["residue_index"] - 1] != s[st]["aa"]]
rec("U11_coordinate_reversibility", "IMPLEMENTATION_INVARIANT", not bad,
    f"residue_index -> amino-acid mismatches = {len(bad)}",
    "every residue_index indexes back to the recorded amino acid",
    "an index/amino-acid mismatch (an indexing bug)",
    "hmmemit consensus",
    "n/a - this asserts internal consistency of the indexing, NOT biological transfer")

# ---------------------------------------------------------------- U12 monotone order -------
mapped_idx = [s[st]["residue_index"] for st in range(1, leng + 1) if s[st]["residue_index"]]
rec("U12_monotone_state_order", "IMPLEMENTATION_INVARIANT",
    all(mapped_idx[i] < mapped_idx[i + 1] for i in range(len(mapped_idx) - 1)),
    "hmmalign is globally colinear by construction",
    "mapped residue indices increase with state index",
    "nothing - hmmalign cannot emit a non-colinear path",
    "any sequence", "n/a - NOT usable as evidence of transfer")

with open(f"{TABLES}/mapper_test_matrix.tsv", "w") as f:
    f.write("test\tclassification\tresult\tdetail\tpasses_when\tfails_when\t"
            "positive_control\tnegative_control\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[2]:4s} {r[0]:42s} [{r[1][:28]}] {r[3]}")
bad_rows = [r for r in rows if r[2] != "PASS"]
n_emp = sum(1 for r in rows if r[1] == "FALSIFIABLE_EMPIRICAL_TEST")
print(f"\n{len(rows)-len(bad_rows)}/{len(rows)} passed  "
      f"({n_emp} falsifiable empirical, {len(rows)-n_emp} implementation invariants)")
sys.exit(1 if bad_rows else 0)
