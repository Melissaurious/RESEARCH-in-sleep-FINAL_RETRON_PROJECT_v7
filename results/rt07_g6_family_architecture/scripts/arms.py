#!/usr/bin/env python3
"""The split-half reproducibility statistic, exactly as control/PREDECLARATION.md section 4
declares it. Shared by the between-family arm (s03) and the within-Retron arm (s04).

Nothing here chooses a threshold, a family or a state. It computes rho for whatever labelling
it is handed, and the callers hand it labellings declared in advance.
"""
import hashlib
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g6lib import G5, MIN_STRATUM, N_STATES, WORK  # noqa: E402

import pyarrow.parquet as pq  # noqa: E402


def load():
    """profiles, halves, family / retron metadata. INSPECTABLE population is applied here."""
    z = np.load(os.path.join(WORK, "profiles.npz"), allow_pickle=True)
    codes, rt_hash = z["codes"], z["rt_hash"]
    idx = {h: i for i, h in enumerate(rt_hash.tolist())}

    seq = pq.read_table(os.path.join(G5, "g5_sequences.parquet"),
                        columns=["rt_hash", "verdict", "mapped_fraction",
                                 "sequence_length"]).to_pylist()
    cw = pq.read_table(os.path.join(G5, "g5_metadata_crosswalk.parquet"),
                       columns=["rt_hash", "stage1_collapsed_family", "completeness_class",
                                "multi_status", "in_g5_eligible"]).to_pylist()
    meta = {r["rt_hash"]: r for r in cw}

    keep, fam, mf, comp = [], [], [], []
    for r in seq:
        if r["verdict"] != "MAPPED":          # INSPECTABLE denominator, predeclaration section 2
            continue
        m = meta.get(r["rt_hash"])
        if m is None or not m["in_g5_eligible"]:
            continue
        keep.append(idx[r["rt_hash"]])
        fam.append(m["stage1_collapsed_family"])
        mf.append(float(r["mapped_fraction"]))
        comp.append(m["completeness_class"])
    keep = np.array(keep)
    # MAPPED indicator: the frozen rule's only positive evidence
    M = (codes[keep] == 0).astype(np.float32)
    return dict(M=M, rt_hash=rt_hash[keep], family=np.array(fam),
                mapped_fraction=np.array(mf), completeness=np.array(comp),
                state_ids=z["state_ids"])


def load_clusters(identity):
    """rt_hash -> cluster representative, from the label-blind resource built in s01."""
    path = os.path.join(WORK, f"clu_id{identity}_cluster.tsv")
    rep = {}
    for line in open(path):
        p = line.rstrip("\n").split("\t")
        if len(p) > 1:
            rep[p[1]] = p[0]
    return rep


def halves_from(rt_hash, rep):
    """Deterministic LABEL-BLIND half assignment, by CLUSTER (see g6lib.half_of)."""
    out = np.empty(len(rt_hash), dtype="<U1")
    for i, h in enumerate(rt_hash.tolist()):
        r = rep.get(h, h)
        out[i] = "A" if int(hashlib.sha256(r.encode()).hexdigest()[:8], 16) % 2 == 0 else "B"
    return out


def _profiles(M, labels, mask, groups):
    """Mean per-state MAPPED fraction per group, on each group's own denominator."""
    out, n = {}, {}
    for g in groups:
        sel = mask & (labels == g)
        c = int(sel.sum())
        n[g] = c
        if c:
            out[g] = M[sel].mean(axis=0)
    return out, n


def _corr_dist(profiles, groups):
    P = np.vstack([profiles[g] for g in groups])
    P = P - P.mean(axis=1, keepdims=True)
    sd = np.sqrt((P ** 2).sum(axis=1))
    sd[sd == 0] = 1e-12
    C = (P @ P.T) / np.outer(sd, sd)
    return 1.0 - C


def _upper(D):
    i, j = np.triu_indices(D.shape[0], k=1)
    return D[i, j]


def _spearman(a, b):
    if len(a) < 3:
        return float("nan")
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra @ rb) / d) if d else float("nan")


def rho(M, labels, halves, mask=None, min_stratum=MIN_STRATUM):
    """The split-half reproducibility statistic. Returns (rho, qualifying groups, per-half n)."""
    if mask is None:
        mask = np.ones(len(labels), dtype=bool)
    A, B = mask & (halves == "A"), mask & (halves == "B")
    # Counting per candidate group with a full boolean mask each time is O(n_candidates x n_seq)
    # and becomes impractical when the labelling has many thousands of candidate groups (the
    # LABEL_FREE arm has 11,301). One pass with np.unique gives IDENTICAL counts. This is a
    # performance fix only: same semantics, same groups, same rho.
    ua, ca = np.unique(labels[A], return_counts=True)
    ub, cb = np.unique(labels[B], return_counts=True)
    na = dict(zip(ua.tolist(), ca.tolist()))
    nb = dict(zip(ub.tolist(), cb.tolist()))
    groups = sorted(g for g in set(na) & set(nb)
                    if na[g] >= min_stratum and nb[g] >= min_stratum)
    if len(groups) < 3:
        return float("nan"), groups, {}
    pa, na = _profiles(M, labels, A, groups)
    pb, nb = _profiles(M, labels, B, groups)
    r = _spearman(_upper(_corr_dist(pa, groups)), _upper(_corr_dist(pb, groups)))
    return r, groups, {g: (na[g], nb[g]) for g in groups}


def permuted_null(M, labels, halves, mask, n_rep, seed, strat):
    """NULL-1: shuffle labels WITHIN a stratifier, so visibility is held fixed."""
    rng = np.random.default_rng(seed)
    idx = np.where(mask)[0]
    lab = labels.copy()
    out = []
    bins = {}
    for i in idx:
        bins.setdefault(strat[i], []).append(i)
    for _ in range(n_rep):
        for _b, members in bins.items():
            m = np.array(members)
            lab[m] = labels[rng.permutation(m)]
        r, _g, _n = rho(M, lab, halves, mask)
        if not np.isnan(r):
            out.append(r)
    return np.array(out)


def cluster_permuted_null(M, labels, halves, mask, reps, n_rep, seed, strat):
    """NULL-2 (repair 1): permute labels at CLUSTER level, within a visibility stratum.

    Real family labels are near-constant within a cluster (measured: 99.92%). A sequence-level
    permutation destroys that and makes the null easier than the alternative (Principle 12).
    Reassigning whole clusters preserves it. See control/REPAIR_1.md, including the statement
    of how this null errs in the OPPOSITE direction to NULL-1.
    """
    rng = np.random.default_rng(seed)
    uniq, inv = np.unique(reps, return_inverse=True)
    order = np.argsort(inv, kind="stable")
    starts = np.searchsorted(inv[order], np.arange(len(uniq)))
    ends = np.append(starts[1:], len(order))
    cl_lab = np.empty(len(uniq), dtype=labels.dtype)
    cl_bin = np.empty(len(uniq), dtype=int)
    for k in range(len(uniq)):
        idx = order[starts[k]:ends[k]]
        cl_lab[k] = labels[idx[0]]
        cl_bin[k] = int(np.round(np.mean(strat[idx])))
    bins = {}
    for k, b in enumerate(cl_bin):
        bins.setdefault(b, []).append(k)
    out = []
    for _ in range(n_rep):
        perm = cl_lab.copy()
        for _b, members in bins.items():
            m = np.array(members)
            perm[m] = cl_lab[rng.permutation(m)]
        r, _g, _n = rho(M, perm[inv], halves, mask)
        if not np.isnan(r):
            out.append(r)
    return np.array(out)


def cluster_family_purity(reps, labels):
    """How often a cluster spans exactly one label. The evidence that triggered repair 1."""
    d = {}
    for c, f in zip(reps.tolist(), labels.tolist()):
        d.setdefault(c, set()).add(f)
    pure = sum(1 for v in d.values() if len(v) == 1)
    return pure, len(d)


def decile(x):
    q = np.quantile(x, np.linspace(0, 1, 11))
    q[0] -= 1e-9
    return np.clip(np.searchsorted(q, x, side="left") - 1, 0, 9)
