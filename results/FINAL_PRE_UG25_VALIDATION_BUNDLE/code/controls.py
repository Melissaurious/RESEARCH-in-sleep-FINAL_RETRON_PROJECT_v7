#!/usr/bin/env python3
"""Negative-control generation: mono-shuffle, di-shuffle, reverse.

Three classes, because one is not enough: the G2L gate used mono-shuffle alone and its
decoy ceiling was measured against the weakest available null (mono 17, di 24, reverse 25
MAPPED anchors at PP_HI 0.75).

Failed di-shuffle generations are RECORDED BY IDENTITY and never substituted.
"""
import collections, random

INTENDED_NULL = {
    "MONO": "amino-acid composition preserved, all order destroyed",
    "DI": "every adjacent-pair (dipeptide) count preserved, longer-range order destroyed",
    "REV": "composition, length and all local pair structure preserved, read backwards",
}


def di_shuffle(seq, rng, tries=200):
    """Altschul-Erikson dipeptide shuffle: preserves every adjacent-pair count exactly.

    A plain greedy Eulerian walk strands edges and fails almost every time (observed 0/19).
    Reserving one outgoing 'last edge' per vertex, constrained to form a tree rooted at the
    final residue, is what guarantees the walk consumes every edge.

    Returns None when no valid last-edge tree is found; the caller records the failure by id.
    """
    if len(seq) < 3:
        return None
    first, last = seq[0], seq[-1]
    edges = collections.defaultdict(list)
    for a, b in zip(seq, seq[1:]):
        edges[a].append(b)
    verts = sorted(edges)
    total = len(seq) - 1
    for _ in range(tries):
        last_edge, ok = {}, True
        for v in verts:
            if v != last:
                last_edge[v] = rng.choice(edges[v])
        for v in last_edge:
            seen, u = set(), v
            while u != last:
                if u in seen or u not in last_edge:
                    ok = False
                    break
                seen.add(u)
                u = last_edge[u]
            if not ok:
                break
        if not ok:
            continue
        rem = {v: list(edges[v]) for v in verts}
        for v, e in last_edge.items():
            rem[v].remove(e)
            rng.shuffle(rem[v])
            rem[v].append(e)
        if last in rem:
            rng.shuffle(rem[last])
        out, cur = [first], first
        while len(out) - 1 < total and rem.get(cur):
            out.append(rem[cur].pop(0))
            cur = out[-1]
        if len(out) == len(seq):
            return "".join(out)
    return None


def replicate_id(source_id, cls, rep=0):
    """Canonical replicate identity. One id space for attempted, valid and failed."""
    return f"{source_id}#{cls}#{rep}"


def make_negatives(seqs, rng, rep=0):
    """Return (sequences, attempted_ids, valid_ids, failed_ids, failed_source_ids).

    Identity binding is produced HERE, in production, not reconstructed later from counts:
    a replicate that silently disappears is invisible to counting but not to an attempted-ID
    universe. `attempted` is every replicate the design calls for; `valid` is every one
    generated; `failed` is the remainder. By construction
    `attempted == valid | failed` and `valid & failed == {}` - which is exactly what C6 then
    re-verifies rather than assumes.

    Every di-shuffle result is asserted to preserve dipeptide composition exactly before it
    is accepted; a silent composition break is treated as a failure, never substituted.
    """
    out = {c: {} for c in INTENDED_NULL}
    attempted = {c: [] for c in INTENDED_NULL}
    valid = {c: [] for c in INTENDED_NULL}
    failed = {c: [] for c in INTENDED_NULL}
    failed_source = {c: [] for c in INTENDED_NULL}

    for sid, s in sorted(seqs.items()):
        for c in ("MONO", "DI", "REV"):
            attempted[c].append(replicate_id(sid, c, rep))

        l = list(s)
        rng.shuffle(l)
        out["MONO"][sid + "_MONO"] = "".join(l)
        valid["MONO"].append(replicate_id(sid, "MONO", rep))

        out["REV"][sid + "_REV"] = s[::-1]
        valid["REV"].append(replicate_id(sid, "REV", rep))

        d = di_shuffle(s, rng)
        if d is None or (collections.Counter(zip(d, d[1:]))
                         != collections.Counter(zip(s, s[1:]))):
            failed["DI"].append(replicate_id(sid, "DI", rep))
            failed_source["DI"].append(sid)
            continue
        out["DI"][sid + "_DI"] = d
        valid["DI"].append(replicate_id(sid, "DI", rep))

    return out, attempted, valid, failed, failed_source
