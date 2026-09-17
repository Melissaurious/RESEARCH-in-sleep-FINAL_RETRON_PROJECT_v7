#!/usr/bin/env python3
"""g4a — recover within-family conserved structure from full-length-source RT proteins,
then test between-family correspondence, WITHOUT any myRT/Pfam seed-derived profile.

Only sequence input: RTs-collection.faa.  No .fst, no .hmm, no .sto, no Pfam is opened.

Usage:  g4a_pipeline.py <collection.faa> <workdir> <tabledir>
"""
import sys, os, re, subprocess, collections, statistics, math, hashlib, random, json

COLL, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"
SEED = 20260916
MIN_AA = 250
EXCLUDED = {"NotUsed", "UNC"}
# --- fixed by control/PREDECLARATION.md, before any alignment was run ---
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
LINEAGE = {"Retrons": "Retron", "GII": "GII_like", "DGRs": "DGR",
           "CRISPR": "CRISPR", "UG3": "UG", "UG5": "UG", "AbiA": "Abi"}
SMALL_FAMILY_MAX = 40
PILOT_CAP = 90
SPLIT = (0.55, 0.15, 0.30)
SPLIT_SMALL = (0.60, 0.00, 0.40)
DYAD = re.compile(r"[YF].DD")

os.makedirs(WORK, exist_ok=True)
os.makedirs(TABLES, exist_ok=True)
random.seed(SEED)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def read_fasta(p):
    s, n = {}, None
    for line in open(p, errors="replace"):
        line = line.rstrip()
        if line.startswith(">"):
            n = line[1:].split()[0]
            s[n] = []
        elif n is not None:
            s[n].append(line.strip())
    return {k: "".join(v) for k, v in s.items()}


def clean(x):
    return x.replace("-", "").replace(".", "").upper().rstrip("*").replace("*", "")


def write_fasta(d, p):
    with open(p, "w") as f:
        for k, v in d.items():
            f.write(f">{k}\n")
            for i in range(0, len(v), 60):
                f.write(v[i:i + 60] + "\n")


def label(h):
    return h.rsplit("_", 1)[1] if "_" in h else "NONE"


# ------------------------------------------------------------------ eligible
raw = read_fasta(COLL)
elig = collections.defaultdict(dict)
for h, s0 in raw.items():
    s = clean(s0)
    f = label(h)
    if f in EXCLUDED or len(s) < MIN_AA:
        continue
    if re.search(r"[^ACDEFGHIKLMNPQRSTVWY]", s):
        continue
    elig[f][h] = s

# ------------------------------------------- roles by cd-hit cluster holdout
roles, selrows = {}, []
for fam in FAMILIES:
    d = elig[fam]
    n_av = len(d)
    small = n_av < SMALL_FAMILY_MAX
    pilot_n = min(n_av, PILOT_CAP)
    fp = f"{WORK}/{fam}.all.faa"
    write_fasta(d, fp)
    run([BIN + "cd-hit", "-i", fp, "-o", f"{WORK}/{fam}.cdhit",
         "-c", "0.50", "-n", "3", "-M", "2000", "-d", "0"])
    clus, cur = collections.defaultdict(list), None
    for line in open(f"{WORK}/{fam}.cdhit.clstr"):
        if line.startswith(">Cluster"):
            cur = int(line.split()[1])
        else:
            clus[cur].append(re.search(r">(\S+?)\.\.\.", line).group(1))
    order = sorted(clus.values(), key=lambda c: (-len(c), c[0]))
    tgt = SPLIT_SMALL if small else SPLIT
    want = [int(round(pilot_n * t)) for t in tgt]
    got = {"derivation": [], "development": [], "challenge": []}
    names = ["derivation", "development", "challenge"]
    for cl in order:
        if sum(len(v) for v in got.values()) >= pilot_n:
            break
        deficit = [want[i] - len(got[names[i]]) for i in range(3)]
        i = deficit.index(max(deficit))
        got[names[i]].extend(cl)
    for r, ids in got.items():
        for i in ids:
            roles[i] = (fam, r)
    n_sing = sum(1 for c in clus.values() if len(c) == 1)
    selrows.append([fam, LINEAGE[fam], str(n_av), str(sum(len(v) for v in got.values())),
                    str(len(got["derivation"])), str(len(got["development"])),
                    str(len(got["challenge"])), str(len(clus)), str(n_sing),
                    "SMALL_FAMILY" if small else "FULL_SPLIT",
                    str(int(statistics.median([len(s) for s in d.values()])))])

with open(f"{TABLES}/g4a_family_selection.tsv", "w") as f:
    f.write("family\tlineage\tN_eligible\tpilot_N\tn_derivation\tn_development\tn_challenge\t"
            "n_cdhit_clusters_at_0.50\tn_singleton_clusters\tsplit_mode\tmedian_len_aa\n")
    for r in selrows:
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_sequence_roles.tsv", "w") as f:
    f.write("sequence_id\tfamily\trole\tlength_aa\thas_dyad\tn_dyad_hits\n")
    for sid, (fam, r) in sorted(roles.items()):
        s = elig[fam][sid]
        hits = DYAD.findall(s)
        f.write(f"{sid}\t{fam}\t{r}\t{len(s)}\t{'YES' if hits else 'NO'}\t{len(hits)}\n")


# --------------------------------------------------------------- alignments
def align(fam, ids, tag, tool):
    fp = f"{WORK}/{fam}.{tag}.faa"
    write_fasta({i: elig[fam][i] for i in ids}, fp)
    out = f"{WORK}/{fam}.{tag}.{tool}.afa"
    if tool == "mafft":
        # --thread 1 is REQUIRED for determinism. With --thread 4 the same input gave
        # different column counts between runs (Retrons 1237 vs 1192, CRISPR 1424 vs
        # 1378); the repaired harness caught it. Conclusions were stable across those
        # runs (dyad 42/42 both times, pct_global moved <= 2.3 points), but the tables
        # were not byte-reproducible. See control/ERRATA.md.
        r = run([BIN + "mafft", "--localpair", "--maxiterate", "1000",
                 "--quiet", "--thread", "1", fp])
        open(out, "w").write(r.stdout)
    else:
        run([BIN + "muscle", "-align", fp, "-output", out])
    return read_fasta(out)


def colstats(aln):
    ids = list(aln)
    L = len(aln[ids[0]])
    rows = []
    for c in range(L):
        col = [aln[i][c].upper() for i in ids]
        ng = [x for x in col if x not in "-."]
        gap = 1 - len(ng) / len(col)
        if ng:
            cnt = collections.Counter(ng)
            tot = len(ng)
            ent = -sum((v / tot) * math.log2(v / tot) for v in cnt.values())
            mx = cnt.most_common(1)[0][1] / tot
            modal = cnt.most_common(1)[0][0]
        else:
            ent, mx, modal = float("nan"), 0.0, "-"
        rows.append(dict(col=c + 1, gap=gap, ent=ent, maxfrac=mx, modal=modal))
    return rows


def ungapped_index(seq, c):
    """1-based residue index of alignment column c (1-based), or None if gap."""
    if seq[c - 1] in "-.":
        return None
    return sum(1 for x in seq[:c] if x not in "-.")


anchor_rows, stab_rows, prof = [], [], {}
for fam in FAMILIES:
    deriv = [i for i, (f, r) in roles.items() if f == fam and r == "derivation"]
    a1 = align(fam, deriv, "deriv", "mafft")
    a2 = align(fam, deriv, "deriv", "muscle")
    s1, s2 = colstats(a1), colstats(a2)
    # map MAFFT columns onto MUSCLE columns via a shared reference sequence
    ref = sorted(deriv)[0]
    m1 = {}
    for c in range(1, len(a1[ref]) + 1):
        u = ungapped_index(a1[ref], c)
        if u:
            m1[u] = c
    m2 = {}
    for c in range(1, len(a2[ref]) + 1):
        u = ungapped_index(a2[ref], c)
        if u:
            m2[u] = c
    # dyad position in the derivation alignment
    dyadcol = collections.Counter()
    for sid in deriv:
        s = elig[fam][sid]
        for mm in DYAD.finditer(s):
            u = mm.start() + 1
            if u in m1:
                dyadcol[m1[u]] += 1
    ranked = sorted(s1, key=lambda r: (r["gap"], r["ent"] if r["ent"] == r["ent"] else 9))
    for rank, r in enumerate(ranked[:40], 1):
        c = r["col"]
        u = ungapped_index(a1[ref], c)
        stab = ""
        if u and u in m2:
            c2 = m2[u]
            stab = f"{abs(s2[c2 - 1]['ent'] - r['ent']):.3f}" if s2[c2 - 1]["ent"] == s2[c2 - 1]["ent"] else ""
        lo, hi = max(0, c - 4), min(len(s1), c + 3)
        ctx = [x["ent"] for x in s1[lo:hi] if x["ent"] == x["ent"]]
        anchor_rows.append([fam, str(rank), str(c), str(u or ""), r["modal"],
                            f"{r['gap']:.3f}", f"{r['ent']:.3f}", f"{r['maxfrac']:.3f}",
                            f"{statistics.mean(ctx):.3f}" if ctx else "",
                            stab, str(dyadcol.get(c, 0))])
    gapless = [r for r in s1 if r["gap"] == 0]
    low_ent = [r for r in s1 if r["gap"] <= 0.1 and r["ent"] == r["ent"] and r["ent"] < 1.0]
    stab_rows.append([fam, str(len(deriv)), str(len(s1)), str(len(s2)),
                      str(len(gapless)), str(len(low_ent)),
                      f"{statistics.median([r['ent'] for r in s1 if r['ent'] == r['ent']]):.3f}",
                      f"{statistics.median([r['ent'] for r in s2 if r['ent'] == r['ent']]):.3f}",
                      str(len(dyadcol)),
                      str(dyadcol.most_common(1)[0][0]) if dyadcol else "",
                      str(dyadcol.most_common(1)[0][1]) if dyadcol else "0",
                      str(sum(dyadcol.values()))])
    # de novo profile from the derivation alignment ONLY
    sto = f"{WORK}/{fam}.deriv.sto"
    run([BIN + "esl-reformat", "-o", sto, "stockholm", f"{WORK}/{fam}.deriv.mafft.afa"])
    run([BIN + "hmmbuild", "--amino", "-n", f"g4a_{fam}",
         f"{WORK}/{fam}.deriv.hmm", sto])
    run([BIN + "hhmake", "-i", f"{WORK}/{fam}.deriv.mafft.afa",
         "-o", f"{WORK}/{fam}.deriv.hhm", "-name", f"g4a_{fam}", "-M", "50"])
    prof[fam] = (f"{WORK}/{fam}.deriv.hmm", f"{WORK}/{fam}.deriv.hhm")

with open(f"{TABLES}/g4a_within_family_anchor_candidates.tsv", "w") as f:
    f.write("family\tevidence_rank\talignment_column\tref_residue_index\tmodal_residue\t"
            "gap_fraction\tshannon_entropy\tmax_residue_fraction\tcontext_mean_entropy\t"
            "entropy_delta_vs_MUSCLE\tn_dyad_hits_in_this_column\n")
    for r in anchor_rows:
        f.write("\t".join(r) + "\n")

with open(f"{TABLES}/g4a_alignment_stability.tsv", "w") as f:
    f.write("family\tn_derivation\tmafft_columns\tmuscle_columns\tn_gapless_columns\t"
            "n_lowgap_lowentropy_columns\tmedian_entropy_mafft\tmedian_entropy_muscle\t"
            "n_distinct_dyad_columns\tmodal_dyad_column\tn_seqs_at_modal_dyad_column\t"
            "total_dyad_hits_mapped\n")
    for r in stab_rows:
        f.write("\t".join(r) + "\n")

# --------------------------------------------------- write the challenge FASTAs
# (Phase B/C consume these; they are produced here so the phases stay separable.)
for b in FAMILIES:
    ch = [i for i, (f, r) in roles.items() if f == b and r == "challenge"]
    if ch:
        write_fasta({i: elig[b][i] for i in ch}, f"{WORK}/{b}.challenge.faa")

# ---------------------------------------------------------------------------
# Phase B (between-family correspondence) and Phase C (supported intersection)
# are NOT done here. An earlier version of this file ran `hhsearch -i A.hhm -d B.hhm`,
# which fails because -d requires a prebuilt ffindex database; the failure was silent
# because the return code was not checked, and it produced an EMPTY correspondence
# table that could have been misread as "no cross-family correspondence".
#
# The corrected work lives in, and must be run in, this order:
#   scripts/g4a_correspondence.py  - pairwise hhalign, the correct pairwise tool
#   scripts/g4a_dyad_check.py      - dyad correspondence read from the alignment text
#   scripts/g4a_intersection.py    - transitivity + supported intersection
#   scripts/g4a_transfer.py        - transfer, reported as a score distribution
#
# g4a_dyad_check.py and g4a_intersection.py deliberately do NOT reimplement hhmake's
# match-state numbering. An earlier version did, got it wrong, and produced a spurious
# "the catalytic dyad does not correspond across families" result plus an all-zero
# transitivity table. Both are superseded; see control/ERRATA.md.
# ---------------------------------------------------------------------------

print("g4a phase A complete (selection, roles, alignments, de novo profiles)")
