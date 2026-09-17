#!/usr/bin/env python3
"""TRUE HMM-state -> residue mapper. Uses the ACTUAL alignment state path from `hmmalign`.

NO linear endpoint interpolation anywhere. hmmalign emits a Stockholm alignment in which
match columns correspond 1:1, in order, to HMM match states 1..LENG; insert columns are
lowercase/'.'; a '-' in a match column is an explicit DELETION of that state.

Fails closed when: a state is deleted, the state is outside the aligned region, the
alignment is ambiguous, or match-column count != LENG.
"""
import os, re, subprocess, collections

BIN = "/home/borg/miniconda3/envs/retron_tradicional/bin/"


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def hmm_leng(hmm):
    for ln in open(hmm):
        if ln.startswith("LENG"):
            return int(ln.split()[1])
    raise SystemExit("FAIL CLOSED: no LENG in " + hmm)


def read_stockholm(path):
    """id -> aligned string, plus the #=GC RF line if present."""
    seqs, rf = collections.defaultdict(str), None
    for ln in open(path):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("# STOCKHOLM") or ln == "//":
            continue
        if ln.startswith("#=GC RF"):
            rf = (rf or "") + ln.split()[-1]
            continue
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) == 2:
            seqs[p[0]] += p[1]
    return dict(seqs), rf


def state_to_residue(hmm, seqs, work, tag):
    """Return {seq_id: {state -> dict(residue_index, aa, alignment_state)}}.

    alignment_state is one of MATCH, DELETE. Insertions are reported separately.
    Derived from the alignment path itself; nothing is interpolated.
    """
    leng = hmm_leng(hmm)
    fa = f"{work}/{tag}.faa"
    with open(fa, "w") as f:
        for k, v in seqs.items():
            f.write(f">{k}\n{v}\n")
    sto = f"{work}/{tag}.sto"
    run([BIN + "hmmalign", "-o", sto, "--outformat", "Stockholm", hmm, fa])
    aln, rf = read_stockholm(sto)

    # match columns: those where RF is 'x' (hmmalign marks match columns in #=GC RF)
    if rf is None:
        raise SystemExit("FAIL CLOSED: hmmalign produced no #=GC RF line")
    match_cols = [i for i, c in enumerate(rf) if c not in ".-~"]
    if len(match_cols) != leng:
        raise SystemExit(f"FAIL CLOSED: {len(match_cols)} match columns != LENG {leng}")

    out, ins = {}, {}
    for sid, a in aln.items():
        # residue index for every non-gap alignment position
        idx, pos = {}, 0
        for i, ch in enumerate(a):
            if ch not in "-.~":
                pos += 1
                idx[i] = pos
        m = {}
        for st, col in enumerate(match_cols, start=1):
            ch = a[col]
            if ch in "-.~":
                m[st] = dict(residue_index=None, aa="-", alignment_state="DELETE")
            else:
                m[st] = dict(residue_index=idx[col], aa=ch.upper(),
                             alignment_state="MATCH")
        out[sid] = m
        # insertions: runs of non-gap residues in NON-match columns, between match states
        runs, cur, after = [], 0, 0
        mcset = set(match_cols)
        seen_states = 0
        for i, ch in enumerate(a):
            if i in mcset:
                if cur:
                    runs.append((seen_states, cur))
                    cur = 0
                seen_states += 1
            else:
                if ch not in "-.~":
                    cur += 1
        if cur:
            runs.append((seen_states, cur))
        ins[sid] = runs
    return out, ins, leng
