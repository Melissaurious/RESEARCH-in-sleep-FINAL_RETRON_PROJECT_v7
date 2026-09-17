#!/usr/bin/env python3
"""REPAIR 3 - mapper v2: alignment-state -> residue WITH posterior support and real ambiguity.

What v1 did right and is preserved unchanged:
  - the state->residue correspondence comes from the ACTUAL hmmalign path, never from
    interpolation between endpoints;
  - match columns are read from #=GC RF and the count is checked against LENG.

What v1 got wrong and this file repairs:
  - v1 called a state "mapped" on bare NON-DELETION. Any residue sitting in a match column
    counted, however little the model believed it. hmmalign already emits per-residue
    posterior probabilities as `#=GR <id> PP`; v1 PARSED THEM AND THREW THEM AWAY.
  - v1 declared an `ambrows` container and never populated it. There was no ambiguity notion
    at all.

Per-state call, one of four:
    MAPPED         residue present, posterior >= PP_HI
    AMBIGUOUS      residue present, PP_LO <= posterior < PP_HI  (a competing path is credible)
    UNSUPPORTED    residue present, posterior < PP_LO           (the chosen path is a minority)
    DELETED_STATE  match column is a gap

Thresholds are NOT defined here. They are frozen in control/SUPPORT_RULE_FROZEN.tsv by
calibrate_support.py, which reads construction-family data only.
"""
import collections, os, re, subprocess

BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"

# HMMER posterior encoding. '0' = 0.00-0.05, d = (d*0.1-0.05)..(d*0.1+0.05), '*' = 0.95-1.00.
# We take the LOWER BOUND of each band: a call is never credited with more confidence than
# the encoding guarantees.
PP_LOWER = {".": None, "-": None, "~": None, "*": 0.95, "0": 0.00}
for _d in range(1, 10):
    PP_LOWER[str(_d)] = round(_d * 0.1 - 0.05, 2)


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def hmm_leng(hmm):
    for ln in open(hmm):
        if ln.startswith("LENG"):
            return int(ln.split()[1])
    raise SystemExit("FAIL CLOSED: no LENG in " + hmm)


def read_stockholm(path):
    """Return (aligned_seqs, RF, per-sequence PP strings).

    Stockholm is INTERLEAVED: one sequence's alignment is split across many blocks and every
    block's fragment must be concatenated in file order. Getting this wrong silently
    truncates the alignment, so `parse_multiline_stockholm` in the test suite asserts it.
    """
    seqs, pp, rf = collections.defaultdict(str), collections.defaultdict(str), None
    for ln in open(path):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("# STOCKHOLM") or ln == "//":
            continue
        if ln.startswith("#=GC RF"):
            rf = (rf or "") + ln.split()[-1]
            continue
        if ln.startswith("#=GR "):
            p = ln.split()
            if len(p) == 4 and p[2] == "PP":
                pp[p[1]] += p[3]
            continue
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) == 2:
            seqs[p[0]] += p[1]
    return dict(seqs), rf, dict(pp)


def domain_scores(hmm, fa, work, tag):
    """Best per-sequence domain bit score and E-value from hmmsearch.

    Used only for reason-coded abstention (NO_QUALIFYING_DOMAIN). Sequences with no reported
    domain are absent from the returned dict.
    """
    out = f"{work}/{tag}.domtbl"
    run([BIN + "hmmsearch", "--domtblout", out, "-o", os.devnull, "--max", hmm, fa])
    best = {}
    for ln in open(out):
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) < 14:
            continue
        sid, sc, ev = p[0], float(p[13]), float(p[12])
        if sid not in best or sc > best[sid][0]:
            best[sid] = (sc, ev)
    return best


def state_to_residue(hmm, seqs, work, tag, pp_hi=None, pp_lo=None):
    """{seq_id: {state -> dict(residue_index, aa, call, posterior)}}, insertions, LENG.

    With pp_hi/pp_lo None the posterior is still reported but every residue-bearing state is
    called MAPPED - i.e. v1 behaviour, retained ONLY so the test suite can demonstrate the
    difference the support rule makes.
    """
    leng = hmm_leng(hmm)
    fa = f"{work}/{tag}.faa"
    with open(fa, "w") as f:
        for k, v in seqs.items():
            f.write(f">{k}\n{v}\n")
    sto = f"{work}/{tag}.sto"
    run([BIN + "hmmalign", "-o", sto, "--outformat", "Stockholm", hmm, fa])
    aln, rf, ppmap = read_stockholm(sto)
    if rf is None:
        raise SystemExit("FAIL CLOSED: hmmalign produced no #=GC RF line")
    match_cols = [i for i, c in enumerate(rf) if c not in ".-~"]
    if len(match_cols) != leng:
        raise SystemExit(f"FAIL CLOSED: {len(match_cols)} match columns != LENG {leng}")

    out, ins = {}, {}
    for sid, a in aln.items():
        ppstr = ppmap.get(sid)
        if ppstr is not None and len(ppstr) != len(a):
            raise SystemExit(f"FAIL CLOSED: PP length {len(ppstr)} != alignment length "
                             f"{len(a)} for {sid}")
        idx, pos = {}, 0
        for i, ch in enumerate(a):
            if ch not in "-.~":
                pos += 1
                idx[i] = pos
        m = {}
        for st, col in enumerate(match_cols, start=1):
            ch = a[col]
            if ch in "-.~":
                m[st] = dict(residue_index=None, aa="-", call="DELETED_STATE", posterior=None)
                continue
            post = PP_LOWER.get(ppstr[col]) if ppstr else None
            if pp_hi is None:
                call = "MAPPED"
            elif post is None:
                call = "UNSUPPORTED"
            elif post >= pp_hi:
                call = "MAPPED"
            elif post >= pp_lo:
                call = "AMBIGUOUS"
            else:
                call = "UNSUPPORTED"
            m[st] = dict(residue_index=idx[col], aa=ch.upper(), call=call, posterior=post)
        out[sid] = m

        runs, cur, seen_states = [], 0, 0
        mcset = set(match_cols)
        for i, ch in enumerate(a):
            if i in mcset:
                if cur:
                    runs.append((seen_states, cur))
                    cur = 0
                seen_states += 1
            elif ch not in "-.~":
                cur += 1
        if cur:
            runs.append((seen_states, cur))
        ins[sid] = runs
    return out, ins, leng


def classify_sequence(states, anchors, leng, s_min, k_min, dom):
    """Reason-coded sequence verdict. `dom` is (score, evalue) or None.

    Returns (verdict, reason, n_mapped, n_ambiguous, n_unsupported, n_deleted).
    """
    a = [s for s in anchors if s <= leng]
    n_map = sum(1 for s in a if states[s]["call"] == "MAPPED")
    n_amb = sum(1 for s in a if states[s]["call"] == "AMBIGUOUS")
    n_uns = sum(1 for s in a if states[s]["call"] == "UNSUPPORTED")
    n_del = sum(1 for s in a if states[s]["call"] == "DELETED_STATE")
    if dom is None or dom[0] < s_min:
        return ("ABSTAIN", "NO_QUALIFYING_DOMAIN", n_map, n_amb, n_uns, n_del)
    if n_map < k_min:
        return ("ABSTAIN", "INSUFFICIENT_SUPPORTED_ANCHORS", n_map, n_amb, n_uns, n_del)
    return ("MAPPED", "OK", n_map, n_amb, n_uns, n_del)
