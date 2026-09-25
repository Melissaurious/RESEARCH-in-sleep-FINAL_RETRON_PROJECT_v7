#!/usr/bin/env python3
"""MCC-v2 — ONE declared variant of m06, written AFTER m06 (MCC-v1) was seen to fail.

What v1 showed (clean set; no clade information consulted):
  * 554 / 1,814 C_TRUNCATED, yet their required-core occupancy is 0.90. The terminal
    9-state RT7 block (cols 1297-1305) is an alignment-edge artefact, not true truncation.
  * core-start / core-end concordance between routes within 5 residues: 42 % / 27 %.
v2 changes exactly two things, and states them here before running:
  (1) anchor blocks are those occupied by >= 95 % of the 102 Toro-2014 retrons (v1: >= 50 %).
      The terminal RT7 block and the RT0 zone become optional flanks: kept when aligned,
      never required.
  (2) consistency adds a BLOCK-WISE interior measure. For every frame block inside the
      required core, do the two routes put the block's first residue at the same protein
      position (|delta| <= 2)? It reports the per-sequence fraction of agreeing blocks.
All other rules (E1-E5, MULTI_CORE, tolerance 5) are unchanged. If v2 also fails, that is
reported; there is no v3 in this pre-activation work.

--- original m06 docstring follows ---
PRE-ACTIVATION FEASIBILITY — can a Mestre-comparable core (MCC) be extracted consistently
from the historical Mestre proteins?  This is NOT the M2a gate. It builds no tree, places
nothing, and reads no modern catalogue sequence.

Every rule below was written before this script first ran; none was tuned afterwards.

FRAME (terminology).  "RT0–RT7" is historical terminology. The operational object here is
MCC-v1: the interval of the Toro & Nisa-Martínez 2014 RT0–RT7 *extraction* alignment
(742 seqs x 1,466 cols; Toro lab = Mestre's lineage; published; built without Mestre clades),
from column 68 (the modal Toro start) to column 1305 (the modal Toro end, = RT7 C-terminus).
MCC-v1 is NOT "the Mestre alignment": that alignment is unpublished and unrecoverable (M1).

MODEL.  `hmmbuild --amino --fragthresh 0`. The default fragthresh treats all 742 Toro
extracts as fragments and turns the near-empty flanks into 228 spurious match states.

ANCHORS, chosen from Toro-2014 RETRON sequences only (Table S1 class; no Mestre data used):
  N-anchor = first frame block (V4 29-block frame) with occupancy >= 0.5 among Toro retrons
  C-anchor = last frame block with occupancy >= 0.5 among Toro retrons
REQUIRED CORE = match states from the N-anchor block's first state to the C-anchor block's
last state. RT0-zone columns [68, N-anchor) are kept in the alignment when residues align
there, but they are never required (Toro's own retron extracts do not occupy them).

EXTRACTABILITY (per sequence; first failing rule is the reason):
  E1 NO_HIT             no hmmsearch domain with i-Evalue <= 1e-5
  E2 N_TRUNCATED        < 50 % of N-anchor block states occupied (hmmalign route)
  E3 C_TRUNCATED        < 50 % of C-anchor block states occupied
  E4 LOW_CORE_OCCUPANCY < 70 % of required-core match states occupied
  E5 NONSTANDARD        > 1 % of residues in the extracted interval not in the 20 standard aa
  flag MULTI_CORE       >= 2 non-overlapping hmmsearch envelopes each spanning >= 50 % of the
                        required-core states (fusion / tandem RT). Reported; excluded from primary.
EXTRACTED INTERVAL = first..last residue aligned to a match state whose column lies in
[68, 1305] (route 1). Full-protein coordinates are kept.

CONSISTENCY (independent route 2): `mafft --add --keeplength` of each sequence into the
Toro alignment. Per sequence, compare the core start (first residue at or after the N-anchor
block's first column) and the core end (last residue at or before column 1305) between the two
routes. Declared concordance tolerance: |delta| <= 5 residues.

SETS: clean published-accession Mestre proteins (1,814 terminals); rescued substitutes split
into the 15 RNA-polymerase subunits (expected: fail E1, a negative control) and the other 97.
"""
import csv, glob, os, re, subprocess, sys, statistics
from collections import defaultdict

ENV = "/home/borg/miniconda3/envs/retron_tradicional/bin"
TORO = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references/rt0_rt7/historical/toro_2014_Rt0-Rt7.FASTA"
GROUPS = "ARIS_OUTPUT/mestre_audit/agent_rt07/toro2014_per_sequence_termini.tsv"
BLOCKS = "ARIS_OUTPUT/mestre_audit/agent_rt07/toro742_hmm_blocks_to_match_states.tsv"
D2 = "/home/borg/RETRONS_january_2026/the-retron-project/PHYLOGENETIC_TREE/IBEX_TESTS/Mestre_sequences"
RNAP = "analysis/mestre_audit/subaudits/v2_v3_v5/v235_rnap_substitutes.tsv"
WORK, OUTDIR = sys.argv[1], sys.argv[2]
COL_LO, COL_HI = 68, 1305
STD = set("ACDEFGHIKLMNPQRSTVWY")
os.makedirs(WORK, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)


def run(cmd, out=None):
    with (open(out, "w") if out else open(os.devnull, "w")) as fh:
        subprocess.run(cmd, check=True, stdout=fh, stderr=subprocess.PIPE)


def read_fasta(p):
    seqs, name = {}, None
    for line in open(p):
        line = line.rstrip("\n")
        if line.startswith(">"):
            name = line[1:].split()[0]; seqs[name] = []
        elif name:
            seqs[name].append(line.strip())
    return {k: "".join(v) for k, v in seqs.items()}


# ---- frame blocks and Toro-retron occupancy -> anchors (no Mestre data) --------------
toro = read_fasta(TORO)
grp = {r["header"].split()[0]: r["coarse_group"] for r in csv.DictReader(open(GROUPS), delimiter="\t")}
blocks = [(int(r["block"]), int(r["start_col"]), int(r["end_col"])) for r in csv.DictReader(open(BLOCKS), delimiter="\t")
          if r["block"].isdigit()]
ret = [s for h, s in toro.items() if grp.get(h) == "Retrons"]
occ = {b: sum(any(s[c - 1] not in "-." for c in range(a, e + 1)) for s in ret) / len(ret) for b, a, e in blocks}
good = [b for b, _, _ in blocks if occ[b] >= 0.95]
N_ANCHOR, C_ANCHOR = good[0], good[-1]
bcols = {b: (a, e) for b, a, e in blocks}

# ---- model -----------------------------------------------------------------------------
hmm = f"{WORK}/toro2014_ft0.hmm"
run([f"{ENV}/hmmbuild", "--amino", "--fragthresh", "0", "-n", "TORO2014_FT0", hmm, TORO])
state_col = {}
inm = False
for line in open(hmm):
    if line.startswith("HMM "):
        inm = True; continue
    p = line.split()
    if inm and len(p) >= 22 and p[0].isdigit():
        state_col[int(p[0])] = int(p[21])
col_states = lambda a, e: [k for k, c in state_col.items() if a <= c <= e]
N_STATES, C_STATES = col_states(*bcols[N_ANCHOR]), col_states(*bcols[C_ANCHOR])
CORE = [k for k, c in state_col.items() if bcols[N_ANCHOR][0] <= c <= bcols[C_ANCHOR][1]]
WIN = {k for k, c in state_col.items() if COL_LO <= c <= COL_HI}

# ---- query sets ---------------------------------------------------------------------------
rnap = {r["terminal"] for r in csv.DictReader(open(RNAP), delimiter="\t")}
qfa, qset = f"{WORK}/queries.faa", {}
with open(qfa, "w") as fh:
    for f in sorted(glob.glob(f"{D2}/terminal_*/protein_aminoacid.fasta")):
        t = f.split("/")[-2]; L = open(f).read().split("\n")
        s = "".join(x.strip() for x in L[1:]).rstrip("*").upper()
        qset[t] = "RNAP_SUBSTITUTE" if t in rnap else ("OTHER_SUBSTITUTE" if "|rescued" in L[0] else "CLEAN")
        fh.write(f">{t}\n{s}\n")
seqs = read_fasta(qfa)

# ---- route 1: hmmsearch (E1, MULTI_CORE) + hmmalign A2M (state occupancy, interval) --------
dom = f"{WORK}/hmmsearch.domtbl"
run([f"{ENV}/hmmsearch", "--cpu", "8", "-E", "1e-3", "--domE", "1e-5", "--domtblout", dom, hmm, qfa])
envs = defaultdict(list)
for line in open(dom):
    if line.startswith("#"):
        continue
    p = line.split()
    if float(p[12]) <= 1e-5:
        envs[p[0]].append((int(p[15]), int(p[16]), int(p[19]), int(p[20])))  # hmm_from, hmm_to, env_from, env_to
a2m = f"{WORK}/hmmalign.a2m"
run([f"{ENV}/hmmalign", "--amino", "--outformat", "A2M", "-o", a2m, hmm, qfa])
r1 = {}
for t, aln in read_fasta(a2m).items():
    k, pos, st = 0, 0, {}
    for ch in aln:
        if ch.isupper():
            k += 1; pos += 1; st[k] = pos
        elif ch == "-":
            k += 1
        elif ch.islower():
            pos += 1
    r1[t] = st

# ---- route 2: mafft --add --keeplength into the Toro alignment -----------------------------
madd = f"{WORK}/mafft_add.afa"
# BUG FIX (2026-09-18, found AFTER the first v1/v2 runs showed implausible route-2 discordance;
# it touches only the route-2 concordance numbers, never extractability): --keeplength DELETES query residues
# that would open new columns, so counting non-gap characters in the output does not give
# protein positions. The residue->column map comes from --mapout (letter, orig pos, column).
run([f"{ENV}/mafft", "--add", qfa, "--keeplength", "--mapout", "--thread", "8", "--anysymbol", TORO], out=madd)
r2, cur = {}, None
for line in open(qfa + ".map"):
    line = line.strip()
    if line.startswith(">"):
        cur = line[1:].split()[0]; r2[cur] = {}
    elif line and not line.startswith("#") and cur:
        _, pos, col = [x.strip() for x in line.split(",")]
        if col != "-":
            r2[cur][int(col)] = int(pos)


def core_bounds_cols(colres):
    """(first residue at col >= N-anchor start, last residue at col <= 1305) from a col->res map."""
    s = [r for c, r in colres.items() if c >= bcols[N_ANCHOR][0] and c <= bcols[C_ANCHOR][1]]
    return (min(s), max(s)) if s else (None, None)


rows, summ = [], defaultdict(lambda: defaultdict(int))
deltas = defaultdict(list)
deltas_bw = defaultdict(list)
for t in sorted(seqs, key=lambda x: int(x.split("_")[1])):
    st = r1.get(t, {})
    fr = lambda S: sum(1 for k in S if k in st) / len(S)
    win_res = [st[k] for k in WIN if k in st]
    start, end = (min(win_res), max(win_res)) if win_res else (None, None)
    ext = seqs[t][start - 1:end] if start else ""
    nonstd = (sum(ch not in STD for ch in ext) / len(ext)) if ext else 1.0
    core_len = len(CORE)
    big = [e for e in envs.get(t, []) if (min(e[1], CORE[-1]) - max(e[0], CORE[0]) + 1) >= 0.5 * core_len]
    nonov = sorted(big, key=lambda e: e[2])
    multi = any(nonov[i + 1][2] > nonov[i][3] for i in range(len(nonov) - 1))
    if not envs.get(t):
        status = "NO_HIT"
    elif fr(N_STATES) < 0.5:
        status = "N_TRUNCATED"
    elif fr(C_STATES) < 0.5:
        status = "C_TRUNCATED"
    elif fr(CORE) < 0.7:
        status = "LOW_CORE_OCCUPANCY"
    elif nonstd > 0.01:
        status = "NONSTANDARD"
    else:
        status = "EXTRACTABLE_MULTI_CORE" if multi else "EXTRACTABLE"
    # consistency on the required-core bounds
    c1 = [st[k] for k in CORE if k in st]
    b1 = (min(c1), max(c1)) if c1 else (None, None)
    b2 = core_bounds_cols(r2.get(t, {}))
    agree = tot = 0
    cr2 = r2.get(t, {})
    for b in range(N_ANCHOR, C_ANCHOR + 1):
        a, e = bcols[b]
        p1 = [st[k] for k in col_states(a, e) if k in st]
        p2 = [cr2[c] for c in range(a, e + 1) if c in cr2]
        if p1 and p2:
            tot += 1; agree += abs(min(p1) - min(p2)) <= 2
    blockwise = round(agree / tot, 3) if tot else ""
    ds = de = ""
    if status.startswith("EXTRACTABLE") and None not in b1 + b2:
        ds, de = b1[0] - b2[0], b1[1] - b2[1]
        deltas[qset[t]].append((abs(ds), abs(de)))
    rt0_res = sum(1 for k in WIN if k in st and state_col[k] < bcols[N_ANCHOR][0])
    rows.append([t, qset[t], len(seqs[t]), status, start or "", end or "", len(ext), round(fr(N_STATES), 3),
                 round(fr(C_STATES), 3), round(fr(CORE), 3), rt0_res, b1[0] or "", b1[1] or "", b2[0] or "", b2[1] or "", ds, de, blockwise])
    if status.startswith("EXTRACTABLE") and blockwise != "":
        deltas_bw[qset[t]].append(blockwise)
    summ[qset[t]][status] += 1

with open(f"{OUTDIR}/MCC_FEASIBILITY_per_sequence.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["terminal", "set", "protein_len", "status", "mcc_start", "mcc_end", "mcc_len", "N_anchor_occ", "C_anchor_occ",
                "core_occ", "rt0_zone_residues", "core_start_route1", "core_end_route1", "core_start_route2", "core_end_route2",
                "delta_start", "delta_end", "frac_core_blocks_agree_within_2"])
    w.writerows(rows)
with open(f"{OUTDIR}/MCC_FEASIBILITY_summary.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["# model", f"hmmbuild --fragthresh 0: {len(state_col)} match states; window cols {COL_LO}-{COL_HI} = {len(WIN)} states"])
    w.writerow(["# anchors (Toro-2014 retrons, n=%d)" % len(ret), f"N-anchor block {N_ANCHOR} occ {occ[N_ANCHOR]:.3f} cols {bcols[N_ANCHOR]}; "
                f"C-anchor block {C_ANCHOR} occ {occ[C_ANCHOR]:.3f} cols {bcols[C_ANCHOR]}; required core {len(CORE)} states"])
    w.writerow(["# toro_retron_block_occupancy", " ".join(f"{b}:{occ[b]:.2f}" for b, _, _ in blocks)])
    w.writerow(["set", "status", "n"])
    for s in summ:
        for k, v in sorted(summ[s].items()):
            w.writerow([s, k, v])
    w.writerow(["set", "n_extractable_compared", "frac_start_within_5", "frac_end_within_5", "median_abs_dstart", "median_abs_dend"])
    for s, d in deltas.items():
        w.writerow([s, len(d), round(sum(a <= 5 for a, _ in d) / len(d), 4), round(sum(b <= 5 for _, b in d) / len(d), 4),
                    statistics.median(a for a, _ in d), statistics.median(b for _, b in d)])
    w.writerow(["set", "n", "median_frac_core_blocks_agree", "frac_seqs_with_ge_0.9_blocks_agree"])
    for s, d in deltas_bw.items():
        w.writerow([s, len(d), statistics.median(d), round(sum(x >= 0.9 for x in d) / len(d), 4)])
print(open(f"{OUTDIR}/MCC_FEASIBILITY_summary.tsv").read())
