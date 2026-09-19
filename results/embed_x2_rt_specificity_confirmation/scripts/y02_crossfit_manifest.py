#!/usr/bin/env python
"""embed_x2/y02 - build and FREEZE the 5-fold component-blocked cross-fit assignment.

Frozen and hashed BEFORE any training. The fold assignment is a deterministic function of the
frozen component sizes; it is never optimised against R-T or any other outcome.

BLOCKING GUARANTEE. The split unit is the embed_g2b connected component, which is already
closed under both RT-cluster and ncRNA-cluster adjacency. Assigning whole components to folds
therefore guarantees, by construction and asserted below, that no RT cluster and no ncRNA
cluster crosses a train/eval boundary in any fold.

NESTING. For fold k: test = fold k, validation = fold (k+1) mod 5, train = the other three.
Validation exists solely to run the frozen X1 stopping rule; it is never used for anything else.

Also checks feasibility of the G (RT-homolog-group) arm and the C1-C4 counterfactual tiers, so
that arms which cannot be supported are dropped BEFORE training rather than after.
"""
from __future__ import annotations
import gzip, hashlib, json, sys
from pathlib import Path
import numpy as np, pandas as pd

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[1]
OUT, W = TASK / "tables", TASK / "work"
SPLIT = ROOT / "results" / "embed_g2b_frozen_split"
K_FOLDS = 5


def neff(s):
    s = np.asarray(s, float)
    return float((s.sum() ** 2) / (s ** 2).sum()) if len(s) else 0.0


def read_mm_clusters(p: Path):
    """mmseqs *_cluster.tsv: representative<TAB>member (gz-aware, as in the frozen bundle)."""
    txt = gzip.decompress(p.read_bytes()).decode() if p.suffix == ".gz" else p.read_text()
    rep = {}
    for line in txt.splitlines():
        r, m = line.split("\t")
        rep[m] = r
    return rep


def assign_folds(sizes: pd.Series, k: int) -> dict:
    """Deterministic greedy: largest component to the currently smallest fold.

    Pure function of (component size, component key). No RNG, no seed, no outcome involved.
    """
    order = sorted(sizes.index, key=lambda c: (-int(sizes[c]), str(c)))
    load = {f: 0 for f in range(k)}
    fold = {}
    for c in order:
        f = min(range(k), key=lambda j: (load[j], j))
        fold[c] = f
        load[f] += int(sizes[c])
    return fold


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True); W.mkdir(parents=True, exist_ok=True)
    a = pd.read_csv(gzip.open(SPLIT / "tables" / "split_assignment.tsv.gz"), sep="\t")
    assert len(a) == 30_924
    sizes = a.component_id.value_counts()
    print(f"[1] eligible population: {len(a):,} pairs over {len(sizes):,} frozen components")

    fold_of = assign_folds(sizes, K_FOLDS)
    a["cv_fold"] = a.component_id.map(fold_of).astype(int)
    a["cv_val_for"] = (a.cv_fold - 1) % K_FOLDS      # this fold is validation for fold k+1...

    print(f"\n[2] fold sizes (test role) and blocking assertions")
    rows = []
    for f in range(K_FOLDS):
        m = a.cv_fold == f
        s = a[m].component_id.value_counts()
        rows.append(dict(fold=f, pairs=int(m.sum()), pct=round(100 * float(m.mean()), 2),
                         components=len(s), n_eff=round(neff(s.values), 2),
                         T3=int(a[m].T3.sum()), T4=int(a[m].T4.sum()),
                         T4_components=int(a[m][a[m].T4 == 1].component_id.nunique()),
                         largest_component=int(s.max())))
        print(f"    fold {f}: {int(m.sum()):>6,} pairs  {len(s):>4} comps  "
              f"n_eff {neff(s.values):>6.2f}  T4 {int(a[m].T4.sum()):>5,} "
              f"({rows[-1]['T4_components']} comps)")

    # hard blocking checks
    for f in range(K_FOLDS):
        te = a[a.cv_fold == f]
        tr = a[~a.cv_fold.isin([f, (f + 1) % K_FOLDS])]
        va = a[a.cv_fold == (f + 1) % K_FOLDS]
        assert not (set(te.component_id) & set(tr.component_id)), f"fold {f}: component leak"
        assert not (set(te.rt_cluster) & set(tr.rt_cluster)), f"fold {f}: RT cluster crosses"
        assert not (set(te.nc_cluster) & set(tr.nc_cluster)), f"fold {f}: ncRNA cluster crosses"
        assert not (set(va.rt_cluster) & set(tr.rt_cluster)), f"fold {f}: val RT cluster crosses"
        assert not (set(va.nc_cluster) & set(tr.nc_cluster)), f"fold {f}: val nc cluster crosses"
    print("    PASS  no component, RT cluster or ncRNA cluster crosses train/val/test "
          "in any fold")
    assert a.cv_fold.notna().all() and sorted(a.cv_fold.unique()) == list(range(K_FOLDS))
    print(f"    PASS  every one of {len(sizes):,} components is evaluated out-of-fold exactly once")

    print("\n[3] G arm feasibility (RT-homolog-group conditioning)")
    rt_rep = read_mm_clusters(SPLIT / "inputs" / "rt_id0.50_cluster.tsv.gz")
    miss = set(a.rt_seq_hash) - set(rt_rep)
    assert not miss, f"{len(miss)} RTs absent from the frozen cluster file"
    a["rt_rep"] = a.rt_seq_hash.map(rt_rep)
    same = (a.rt_rep == a.rt_seq_hash)
    print(f"    G conditions on the ESM-C representation of the RT CLUSTER REPRESENTATIVE")
    print(f"    (frozen mmseqs --min-seq-id 0.50 clusters from embed_g2b; not re-derived)")
    print(f"    distinct RT clusters spanned: {a.rt_rep.nunique():,}")
    print(f"    pairs whose RT IS its own representative (G == R exactly): "
          f"{int(same.sum()):,} ({100*float(same.mean()):.1f}%)")
    print(f"    -> R-G is also reported on the {int((~same).sum()):,} pairs where G differs "
          f"from R, since identical-conditioning pairs attenuate the contrast toward zero")

    print("\n[4] counterfactual tier feasibility (eligible = an alternative exists)")
    cf = []
    for f in range(K_FOLDS):
        te = a[a.cv_fold == f]
        by_type = te.groupby("retron_type").rt_seq_hash.nunique() if "retron_type" in te \
            else None
    # retron_type is not in the split table; load it from the X1 dataset for the audit
    ds = np.load(ROOT / "ARIS_OUTPUT/embed_x1_conditional/work/dataset.npz", allow_pickle=False)
    a["retron_type"] = ds["retron_type"]
    a["rt_aa_len"] = ds["rt_aa_len"]
    partners = a.groupby("nc_seq_hash").rt_seq_hash.apply(set).to_dict()
    for f in range(K_FOLDS):
        te = a[a.cv_fold == f]
        n_type = te.groupby("retron_type").rt_seq_hash.nunique()
        n_clu = te.groupby("rt_rep").rt_seq_hash.nunique()
        c1 = int(te.retron_type.map(n_type).ge(9).sum())
        c4 = int(te.rt_rep.map(n_clu).ge(2).sum())
        cf.append(dict(fold=f, pairs=len(te),
                       C1_same_type_eligible=c1,
                       C4_within_rt_cluster_eligible=c4,
                       C4_components=int(te[te.rt_rep.map(n_clu).ge(2)].component_id.nunique())))
        print(f"    fold {f}: C1 {c1:>6,}/{len(te):,}   C4 {c4:>6,}/{len(te):,} "
              f"({cf[-1]['C4_components']} components)")

    man = a[["rt_seq_hash", "nc_seq_hash", "component_id", "cv_fold", "rt_cluster",
             "nc_cluster", "rt_rep", "retron_type", "T1", "T2", "T3", "T4",
             "in_sensitivity_population"]].copy()
    buf = man.to_csv(sep="\t", index=False).encode()
    (OUT / "CROSSFIT_MANIFEST.tsv").write_bytes(buf)
    sha = hashlib.sha256(buf).hexdigest()
    (OUT / "CROSSFIT_MANIFEST.sha256").write_text(f"{sha}  CROSSFIT_MANIFEST.tsv\n")
    pd.DataFrame(rows).to_csv(OUT / "CROSSFIT_FOLDS.tsv", sep="\t", index=False)
    pd.DataFrame(cf).to_csv(OUT / "CROSSFIT_CF_FEASIBILITY.tsv", sep="\t", index=False)
    np.savez_compressed(W / "crossfit.npz",
                        cv_fold=man.cv_fold.values.astype(np.int8),
                        rt_rep=np.array(man.rt_rep.astype(str).tolist(), dtype=np.str_))
    meta = dict(k_folds=K_FOLDS, pairs=len(a), components=len(sizes),
                assignment_rule="largest component to the currently smallest fold; "
                                "deterministic, no RNG, never optimised against any outcome",
                nesting="fold k: test=k, validation=(k+1) mod 5, train=the other three",
                blocking="component, RT cluster and ncRNA cluster all verified non-crossing",
                G_arm="ESM-C representation of the frozen rt_id0.50 cluster representative",
                sha256_manifest=sha,
                is_internal_crossfit=True,
                note=("INTERNAL cross-fitted confirmation, NOT external validation. The frozen "
                      "embed_g2b test fold and the X1 result are untouched and retain their "
                      "original interpretation."))
    (OUT / "CROSSFIT_META.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"\n[5] frozen. CROSSFIT_MANIFEST.tsv sha256 {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
