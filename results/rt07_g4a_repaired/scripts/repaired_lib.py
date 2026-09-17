#!/usr/bin/env python3
"""Shared helpers for the repaired g4a bundle and the UG5 holdout gate.

Every external call is fail-closed (check=True). Nothing here opens any myRT/Pfam
seed-derived object: the only sequence input is RTs-collection.faa.
"""
import os, re, subprocess, collections, hashlib

BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"
COLLECTION = ("/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/"
              "RTs-collection.faa")

# --- predeclared parameters (control/PREDECLARATION_REPAIRED.md) ---
MIN_AA = 250
EXCLUDED_LABELS = {"NotUsed", "UNC"}
LINK_IDENTITY = 0.30
LINK_COVERAGE = 0.50
PILOT_CAP = 90
SMALL_FAMILY_MAX = 40
SPLIT = (0.55, 0.15, 0.30)
SPLIT_SMALL = (0.60, 0.00, 0.40)
HHMAKE_M = "50"
HMMSEARCH_E = "10"
TRANSITIVITY_TOL = 2
TRIPLE_MIN_POSITIONS = 20
DYAD = re.compile(r"[YyFf].[Dd][Dd]")
GAPS = "-."


def run(cmd, **kw):
    """Fail-closed external call."""
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


def eligible_by_family(collection=COLLECTION):
    raw = read_fasta(collection)
    out = collections.defaultdict(dict)
    for h, s0 in raw.items():
        s = clean(s0)
        f = label(h)
        if f in EXCLUDED_LABELS or len(s) < MIN_AA:
            continue
        if re.search(r"[^ACDEFGHIKLMNPQRSTVWY]", s):
            continue
        out[f][h] = s
    return out


def all_vs_all(seqs, work, tag):
    """Pairwise identity + bidirectional coverage.

    REPAIR 1 (PREDECLARATION_ADDENDUM_2 s1): mmseqs normalises identifiers - an input id
    `sp|P23070.1_Retrons` comes back as `P23070.1_Retrons`, so its hits never match the
    input id and it becomes a PHANTOM SINGLETON component. Every sequence is therefore
    renamed to an opaque surrogate `s<NNNNNN>` before the search and mapped back after,
    and the id sets are asserted equal. Fails closed on any mismatch.
    """
    fwd = {f"s{ i:06d}".replace(" ", ""): k for i, k in enumerate(sorted(seqs))}
    rev = {v: k for k, v in fwd.items()}
    fp = f"{work}/{tag}.aa.faa"
    write_fasta({sid: seqs[orig] for sid, orig in fwd.items()}, fp)
    out = f"{work}/{tag}.m8"
    tmp = f"{work}/{tag}.mmtmp"
    os.makedirs(tmp, exist_ok=True)
    run([BIN + "mmseqs", "easy-search", fp, fp, out, tmp,
         "-s", "7.5", "-e", "10000", "--max-seqs", "5000",
         "--format-output", "query,target,fident,qcov,tcov", "-v", "1"])
    rows, seen = [], set()
    for line in open(out):
        p_ = line.rstrip("\n").split("\t")
        if len(p_) < 5:
            continue
        q, t = p_[0], p_[1]
        if q not in fwd or t not in fwd:
            raise SystemExit(
                f"FAIL CLOSED [{tag}]: mmseqs returned an id absent from the surrogate "
                f"table: {q!r} / {t!r}. Identifier normalisation is not neutralised.")
        seen.add(q); seen.add(t)
        if q == t:
            continue
        rows.append((fwd[q], fwd[t], float(p_[2]), float(p_[3]), float(p_[4])))
    missing = set(fwd) - seen
    if missing:
        raise SystemExit(
            f"FAIL CLOSED [{tag}]: {len(missing)} surrogate id(s) never appear in the mmseqs "
            f"output, so their hits cannot be recovered; e.g. "
            f"{[fwd[m] for m in sorted(missing)[:3]]}")
    return rows


def components(ids, pairs, ident=LINK_IDENTITY, cov=LINK_COVERAGE):
    """Connected components of the link graph. Whole components go to one role, so
    every cross-component pair is BELOW the link rule by construction."""
    parent = {i: i for i in ids}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for q, t, fi, qc, tc in pairs:
        if q in parent and t in parent and fi >= ident and min(qc, tc) >= cov:
            union(q, t)
    comp = collections.defaultdict(list)
    for i in ids:
        comp[find(i)].append(i)
    return sorted(comp.values(), key=lambda c: (-len(c), sorted(c)[0]))


def deal_components(comps, pilot_n, small):
    """Whole components -> roles, never exceeding pilot_n (the cap is enforced)."""
    tgt = SPLIT_SMALL if small else SPLIT
    want = [int(round(pilot_n * t)) for t in tgt]
    names = ["derivation", "development", "challenge"]
    got = {n: [] for n in names}
    total = 0
    for cl in comps:
        if total + len(cl) > pilot_n:
            continue                      # skip; try the next smaller component
        deficit = [want[i] - len(got[names[i]]) for i in range(3)]
        if small:
            deficit[1] = -10 ** 9         # no development set
        i = deficit.index(max(deficit))
        got[names[i]].extend(cl)
        total += len(cl)
        if total >= pilot_n:
            break
    return got


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def aligned_consensus(path):
    """(Q_aligned, T_aligned, q_start, t_start) for hit 1 of an hhalign .hhr."""
    if not os.path.exists(path):
        return None
    q, t, qs, ts = [], [], None, None
    for ln in open(path):
        m = re.match(r"Q Consensus\s+(\d+)\s+(\S+)\s+\d+", ln)
        if m:
            if qs is None:
                qs = int(m.group(1))
            q.append(m.group(2))
            continue
        m = re.match(r"T Consensus\s+(\d+)\s+(\S+)\s+\d+", ln)
        if m:
            if ts is None:
                ts = int(m.group(1))
            t.append(m.group(2))
    if not q or len(q) != len(t) or any(len(a) != len(b) for a, b in zip(q, t)):
        return None
    return "".join(q), "".join(t), qs, ts


def pair_map(path):
    ap = aligned_consensus(path)
    if not ap:
        return None
    Q, T, qs, ts = ap
    qi, ti, m = qs, ts, {}
    for a, b in zip(Q, T):
        qg, tg = a in GAPS, b in GAPS
        if not qg and not tg:
            m[qi] = ti
        if not qg:
            qi += 1
        if not tg:
            ti += 1
    return m


def hhr_header(path):
    """(prob, evalue, score, cols) of hit 1."""
    txt = open(path).read()
    m = re.search(r"^\s*1\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)", txt, re.M)
    return (m.group(1), m.group(2), m.group(4), m.group(6)) if m else None


class Audit:
    """Every deviation is surfaced, never silently repaired."""

    def __init__(self):
        self.rows = []

    def add(self, item, expected, observed, when, effect, repair, invalidated):
        self.rows.append([item, str(expected), str(observed), when, effect, repair,
                          invalidated])
        print(f"[AUDIT] {item}: expected={expected} observed={observed} ({when})")

    def write(self, path):
        with open(path, "w") as f:
            f.write("item\texpected\tobserved\twhen_detected\tscientific_effect\trepair\t"
                    "results_before_repair_invalidated\n")
            for r in self.rows:
                f.write("\t".join(r) + "\n")


def deterministic_draw(seqs, pilot_n, small):
    """Used ONLY where a family does not fragment (PREDECLARATION_ADDENDUM_1 §3.3).
    Deterministic and non-outcome-driven: ids sorted lexicographically, first k taken.
    The resulting 'challenge' set is NON_INDEPENDENT and licenses no transfer claim."""
    ids = sorted(seqs)[:pilot_n]
    tgt = SPLIT_SMALL if small else SPLIT
    nd = int(round(pilot_n * tgt[0]))
    nv = int(round(pilot_n * tgt[1]))
    return {"derivation": ids[:nd],
            "development": ids[nd:nd + nv],
            "challenge": ids[nd + nv:]}
