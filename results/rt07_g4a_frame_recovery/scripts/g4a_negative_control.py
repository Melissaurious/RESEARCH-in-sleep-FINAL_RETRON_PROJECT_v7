#!/usr/bin/env python3
"""g4a NEGATIVE CONTROL — added after the main result, to test whether the headline
numbers are impressive or near-inevitable.

The executing session flagged three weaknesses in its own study:
  (a) hhalign probability 74.2-100.0 across 42/42 pairs may be what ANY profile pair gives;
  (b) 42/42 DYAD_CORRESPONDS may be near-inevitable if each consensus has one [YF]xDD
      and the profiles align at all;
  (c) SELF 424.1 vs CROSS 32.6 may be near-tautological.

This control can only WEAKEN the claims; it cannot strengthen them. Decoys are built
from the derivation sequences themselves, so no external data is needed:

  SHUF : per-sequence residue shuffle, composition preserved exactly, length preserved
  REV  : sequence reversed - preserves composition AND local complexity, destroys order

For each decoy class the SAME pipeline is applied: align, hmmbuild, hhmake, then
hhalign real-vs-decoy and decoy-vs-decoy, and hmmsearch real-profile-vs-decoy-sequences.

Usage: g4a_negative_control.py <workdir> <tabledir>
"""
import sys, os, re, random, subprocess, itertools, statistics, collections

WORK, TABLES = sys.argv[1], sys.argv[2]
BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"
FAMILIES = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "UG5", "AbiA"]
SEED = 20260916
DYAD = re.compile(r"[YyFf].[Dd][Dd]")
random.seed(SEED)


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


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


def write_fasta(d, p):
    with open(p, "w") as f:
        for k, v in d.items():
            f.write(f">{k}\n")
            for i in range(0, len(v), 60):
                f.write(v[i:i + 60] + "\n")


def build_decoy_profile(fam, mode):
    src = read_fasta(f"{WORK}/{fam}.deriv.faa")
    out = {}
    for k, v in src.items():
        s = list(v.upper())
        if mode == "SHUF":
            random.shuffle(s)
        else:
            s = s[::-1]
        out[k] = "".join(s)
    tag = f"{fam}.{mode}"
    write_fasta(out, f"{WORK}/{tag}.faa")
    r = run([BIN + "mafft", "--localpair", "--maxiterate", "1000",
             "--quiet", "--thread", "1", f"{WORK}/{tag}.faa"])
    open(f"{WORK}/{tag}.afa", "w").write(r.stdout)
    run([BIN + "esl-reformat", "-o", f"{WORK}/{tag}.sto", "stockholm", f"{WORK}/{tag}.afa"])
    run([BIN + "hmmbuild", "--amino", "-n", f"neg_{tag}", f"{WORK}/{tag}.hmm", f"{WORK}/{tag}.sto"])
    run([BIN + "hhmake", "-i", f"{WORK}/{tag}.afa", "-o", f"{WORK}/{tag}.hhm",
         "-name", f"neg_{tag}", "-M", "50"])
    return tag


def hha(i, t, out):
    subprocess.run([BIN + "hhalign", "-i", i, "-t", t, "-o", out],
                   capture_output=True, text=True)
    if not os.path.exists(out):
        return None, None
    txt = open(out).read()
    m = re.search(r"^\s*1\s+\S+\s+(\S+)\s+(\S+)", txt, re.M)
    if not m:
        return None, None
    # dyad correspondence, same method as the main analysis
    q, t_ = [], []
    for ln in txt.split("\n"):
        a = re.match(r"Q Consensus\s+\d+\s+(\S+)\s+\d+", ln)
        if a:
            q.append(a.group(1))
        b = re.match(r"T Consensus\s+\d+\s+(\S+)\s+\d+", ln)
        if b:
            t_.append(b.group(1))
    dy = ""
    if q and len(q) == len(t_) and all(len(x) == len(y) for x, y in zip(q, t_)):
        Q, T = "".join(q), "".join(t_)
        hits = list(DYAD.finditer(Q))
        dy = "NO_DYAD_IN_QUERY" if not hits else "DYAD_NOT_ALIGNED_TO_DYAD"
        for mm in hits:
            if T[mm.start() + 2:mm.start() + 4].upper() == "DD":
                dy = "DYAD_CORRESPONDS"
                break
    return (m.group(1), m.group(2)), dy


rows = []
for mode in ("SHUF", "REV"):
    tags = {f: build_decoy_profile(f, mode) for f in FAMILIES}
    # real vs decoy, across different families (the honest comparison)
    for a, b in itertools.permutations(FAMILIES, 2):
        r, dy = hha(f"{WORK}/{a}.deriv.hhm", f"{WORK}/{tags[b]}.hhm",
                    f"{WORK}/neg_{mode}_{a}__{b}.hhr")
        rows.append([mode, "REAL_vs_DECOY", a, b,
                     r[0] if r else "", r[1] if r else "", dy])
    # decoy vs decoy, across different families
    for a, b in itertools.permutations(FAMILIES, 2):
        r, dy = hha(f"{WORK}/{tags[a]}.hhm", f"{WORK}/{tags[b]}.hhm",
                    f"{WORK}/neg_{mode}_dd_{a}__{b}.hhr")
        rows.append([mode, "DECOY_vs_DECOY", a, b,
                     r[0] if r else "", r[1] if r else "", dy])

with open(f"{TABLES}/g4a_negative_control.tsv", "w") as f:
    f.write("decoy_mode\tcomparison\tfamily_A\tfamily_B\thhalign_probability\t"
            "hhalign_evalue\tdyad_verdict\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")

# hmmsearch: real profiles against decoy SEQUENCES
tr = []
for mode in ("SHUF", "REV"):
    for a in FAMILIES:
        for b in FAMILIES:
            fp = f"{WORK}/{b}.{mode}.faa"
            if not os.path.exists(fp):
                continue
            n = sum(1 for l in open(fp) if l.startswith(">"))
            tbl = f"{WORK}/neg_tr_{mode}_{a}_{b}.tbl"
            run([BIN + "hmmsearch", "--max", "-E", "10", "--noali",
                 "--tblout", tbl, f"{WORK}/{a}.deriv.hmm", fp])
            best = {}
            for line in open(tbl):
                if line.startswith("#"):
                    continue
                p = line.split()
                sc = float(p[5])
                if p[0] not in best or sc > best[p[0]]:
                    best[p[0]] = sc
            sc = list(best.values())
            tr.append([mode, a, b, str(n), str(len(sc)),
                       f"{100*len(sc)/n:.1f}",
                       f"{statistics.median(sc):.1f}" if sc else ""])

with open(f"{TABLES}/g4a_negative_control_transfer.tsv", "w") as f:
    f.write("decoy_mode\tprofile_family\tdecoy_family\tn_decoys\tn_detected\tpct_detected\t"
            "median_best_bitscore\n")
    for r in tr:
        f.write("\t".join(r) + "\n")

# ---- summary to stdout
for mode in ("SHUF", "REV"):
    for comp in ("REAL_vs_DECOY", "DECOY_vs_DECOY"):
        p = [float(r[4]) for r in rows if r[0] == mode and r[1] == comp and r[4]]
        d = collections.Counter(r[6] for r in rows if r[0] == mode and r[1] == comp)
        if p:
            print(f"{mode:5s} {comp:16s} n={len(p):3d}  hhalign prob "
                  f"min={min(p):5.1f} median={statistics.median(p):5.1f} max={max(p):5.1f}  "
                  f"dyad={dict(d)}")
        else:
            print(f"{mode:5s} {comp:16s} NO ALIGNMENT RETURNED for any pair")
for mode in ("SHUF", "REV"):
    v = [float(r[6]) for r in tr if r[0] == mode and r[6]]
    if v:
        print(f"{mode:5s} real-profile-vs-decoy-sequences: median bitscore "
              f"{statistics.median(v):.1f} (n={len(v)} cells)")
