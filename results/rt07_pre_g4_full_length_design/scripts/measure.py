#!/usr/bin/env python3
"""Reproduce every number quoted in rt07_pre_g4_full_length_design.

Read-only. Touches no Stage-1 catalogue file. Prints a labelled value per line so
the output can be diffed against the landed tables.

    python3 scripts/measure.py [MYRT_MODELS_DIR]
"""
import sys, os, re, glob, json, hashlib, statistics, collections, random

M = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/"
if not M.endswith("/"):
    M += "/"
EXCLUDED_LABELS = {"NotUsed", "UNC"}
MIN_AA = 250                      # declared fragment floor
KMER = 4
CLUST_J = 0.90
SEED = 20260916


def read_fasta(path):
    """id -> ungapped uppercase sequence, terminal stop stripped."""
    seqs, name = {}, None
    for line in open(path, errors="replace"):
        line = line.rstrip()
        if line.startswith(">"):
            name = line[1:].split()[0]
            seqs[name] = []
        elif name is not None:
            seqs[name].append(line.strip())
    return {k: "".join(v).replace("-", "").replace(".", "").upper()
            .rstrip("*").replace("*", "") for k, v in seqs.items()}


def label(h):
    return h.rsplit("_", 1)[1] if "_" in h else "NONE"


LINEAGE = {"GII": "GII_like", "G2L": "GII_like", "G2L4": "GII_like",
           "DGRs": "DGR", "Retrons": "Retron", "CRISPR": "CRISPR",
           "AbiA": "Abi", "AbiK": "Abi", "AbiP2": "Abi"}


def lineage(l):
    return LINEAGE.get(l, "UG" if l.startswith("UG") else "OTHER")


def kmers(s, k=KMER):
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def jac(a, b):
    u = len(a | b)
    return len(a & b) / u if u else 0.0


def out(k, v):
    print(f"{k}\t{v}")


# ---------------------------------------------------------------- inputs
canon = [l.split()[1] for l in open(M + "HMM/RVT-All.hmm") if l.startswith("NAME")]
nseq = {}
n = None
for line in open(M + "HMM/RVT-All.hmm"):
    if line.startswith("NAME"):
        n = line.split()[1]
    if line.startswith("NSEQ"):
        nseq[n] = int(line.split()[1])
out("myrt.models_in_RVT_All", len(canon))
out("myrt.NSEQ_sum", sum(nseq.values()))

seeds = {}
for fp in glob.glob(M + "HMM/*.fst"):
    fam = os.path.basename(fp)[:-4]
    if fam in set(canon):
        for h, s in read_fasta(fp).items():
            seeds[(fam, h)] = s
out("myrt.seed_records", len(seeds))
out("myrt.seed_unique_aa",
    len({hashlib.sha256(s.encode()).hexdigest() for s in seeds.values()}))
out("myrt.NSEQ_equals_fasta_for_every_family",
    all(nseq[f] == sum(1 for (ff, _) in seeds if ff == f) for f in canon))

coll = read_fasta(M + "RTs-collection.faa")
out("collection.records", len(coll))
out("collection.unique_aa",
    len({hashlib.sha256(s.encode()).hexdigest() for s in coll.values()}))
out("collection.nonstandard_residue_seqs",
    sum(1 for s in coll.values() if re.search(r"[^ACDEFGHIKLMNPQRSTVWY]", s)))

# ------------------------------------------- fragment -> full-length mapping
items = list(coll.items())
mapped, unmapped = [], []
for (fam, h), fs in seeds.items():
    if len(fs) < 40:
        continue
    for cn, cs in items:
        i = cs.find(fs)
        if i >= 0:
            mapped.append((fam, h, cn, i + 1, i + len(fs), len(fs), len(cs),
                           i, len(cs) - (i + len(fs))))
            break
    else:
        unmapped.append((fam, h))
out("map.seeds_mapped", len(mapped))
out("map.seeds_unmapped", len(unmapped))
nx = [r[7] for r in mapped]
cx = [r[8] for r in mapped]
out("map.N_ext_median", int(statistics.median(nx)))
out("map.N_ext_mean", round(sum(nx) / len(nx), 1))
out("map.N_ext_max", max(nx))
out("map.C_ext_median", int(statistics.median(cx)))
ge80 = sum(1 for x in nx if x >= 80)
out("map.sources_with_ge80aa_N_ext", ge80)
out("map.pct_with_ge80aa_N_ext", round(100 * ge80 / len(nx), 1))
per = collections.defaultdict(list)
for r in mapped:
    per[r[0]].append(r[7])
for fam in ("RVT-GII-I", "RVT-GII-II", "RVT-Retrons", "RVT-DGRs"):
    if fam in per:
        out(f"map.N_ext_median.{fam}", int(statistics.median(per[fam])))

# ------------------------------------------------------- eligible panel
elig = {h: s for h, s in coll.items()
        if label(h) not in EXCLUDED_LABELS
        and not re.search(r"[^ACDEFGHIKLMNPQRSTVWY]", s)
        and len(s) >= MIN_AA}
out("panel.eligible_full_length", len(elig))
byfam = collections.defaultdict(list)
for h, s in elig.items():
    byfam[label(h)].append(s)
nrep = 0
for f, S in byfam.items():
    K = [kmers(x) for x in S]
    reps = []
    for a in K:
        if all(jac(a, K[r]) < CLUST_J for r in reps):
            reps.append(K.index(a))
    nrep += len(reps)
out("panel.non_redundant_at_kmerJ_0.90", nrep)
bylin = collections.Counter()
for f, S in byfam.items():
    bylin[lineage(f)] += len(S)
for l, c in bylin.most_common():
    out(f"panel.eligible.{l}", c)

# --------------------------------------------------- anchor occupancy
DYAD = re.compile(r"[YF].DD")
win = {r[2]: (r[3], r[4]) for r in mapped}
tot = collections.Counter()
hit = collections.Counter()
multi = 0
inwin = 0
denom_inwin = 0
for h, s in coll.items():
    f = label(h)
    if f in EXCLUDED_LABELS:
        continue
    tot[f] += 1
    m = [mm.start() + 1 for mm in DYAD.finditer(s)]
    if m:
        hit[f] += 1
        if len(m) > 1:
            multi += 1
        if h in win:
            denom_inwin += 1
            a, b = win[h]
            if any(a <= p <= b for p in m):
                inwin += 1
out("anchor.dyad_present", sum(hit.values()))
out("anchor.labelled_proteins", sum(tot.values()))
out("anchor.dyad_pct", round(100 * sum(hit.values()) / sum(tot.values()), 1))
out("anchor.multi_dyad_proteins", multi)
low = sorted(f for f in tot if hit[f] / tot[f] < 0.90)
out("anchor.families_below_90pct", ",".join(low))
for f in low:
    out(f"anchor.dyad_pct.{f}", round(100 * hit[f] / tot[f], 1))
out("anchor.dyad_inside_RVT1_window", f"{inwin}/{denom_inwin}")

# --------------------------------------------------- per-label cap effect
real = {f: len(S) for f, S in byfam.items()}
for cap in (20, 30, 40):
    d = collections.Counter()
    for f, nn in real.items():
        d[lineage(f)] += min(nn, cap)
    t = sum(d.values())
    out(f"perlabel_cap_{cap}.total", t)
    out(f"perlabel_cap_{cap}.UG_pct", round(100 * d["UG"] / t, 1))
    out(f"perlabel_cap_{cap}.Retron_pct", round(100 * d["Retron"] / t, 1))
