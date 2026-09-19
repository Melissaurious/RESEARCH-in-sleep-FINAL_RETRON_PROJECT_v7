#!/usr/bin/env python
"""Re-AGGREGATE the frozen embed_x1 per-sequence held-out NLL arrays to the component level.

This does NOT recompute any model output. It reads the per-sequence NLL sums and token counts
written by the frozen x1 evaluation run (x06_eval.py:103) and applies the same aggregation the
frozen bundle used (per-sequence NLL sum -> per-component token-weighted mean). The script then
ASSERTS that the re-aggregation reproduces every number in the frozen summary tables. If it does
not, the script fails and nothing is written.

Why it exists: the frozen bundle carries only summaries, so the component-level effect
distribution (FIGURE_PLAN F4) cannot be drawn from it. The per-sequence arrays live in the
embeddings worktree's ARIS_OUTPUT scratch, which is disposable and gitignored; this table is the
durable, checked record of the same quantities.

Read-only with respect to the source worktree.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings")
WORK = SRC / "ARIS_OUTPUT/embed_x1_conditional/work"
FROZEN = SRC / "results/embed_x1_conditional_pilot/tables"
OUT = Path(__file__).resolve().parents[1] / "derived"
SEED = 20260918          # x04_train.SEED, as used by the frozen bootstrap
N_BOOT = 10_000
# float32 per-sequence arrays accumulated in a different order give |delta| <= 4e-8 against the
# frozen tables; the reported precision is 5 decimals, so 1e-6 is a strict check, not a loose one.
TOL = 1e-6
ARMS = ("U", "T", "R")


def comp_mean(nll_sum, n_tok, comp):
    """per-sequence NLL sum -> per-component token-weighted mean (x06_eval.comp_mean)."""
    import collections
    s, t = collections.defaultdict(float), collections.defaultdict(float)
    for v, n, c in zip(nll_sum, n_tok, comp):
        s[c] += v
        t[c] += n
    ks = sorted(s)
    return np.array(ks), np.array([s[k] / t[k] for k in ks])


def boot(x, seed=SEED, n=N_BOOT):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n, len(x)))
    m = x[idx].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def paired(d, seed=SEED, n=N_BOOT):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    m = d[idx].mean(1)
    return dict(n_components=len(d), diff=float(d.mean()),
                ci_lo=float(np.percentile(m, 2.5)), ci_hi=float(np.percentile(m, 97.5)),
                frac_components_favouring_a=float((d < 0).mean()))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(WORK / "dataset.npz", allow_pickle=True)
    te = np.where(d["fold"] == "test")[0]
    assert len(te) == 4638, len(te)
    comp = d["component"][te]

    seqnll = {a: np.load(WORK / f"test_seqnll_{a}.npy") for a in ARMS}
    ntok = {a: np.load(WORK / f"test_ntok_{a}.npy") for a in ARMS}
    for a in ARMS:
        assert len(seqnll[a]) == len(te)
        # token counts are a property of the ncRNA, identical across arms
        assert np.array_equal(ntok[a], ntok["U"])
    n_tok = ntok["U"]

    keys, vals = {}, {}
    for a in ARMS:
        keys[a], vals[a] = comp_mean(seqnll[a], n_tok, comp)
    assert all(np.array_equal(keys[a], keys["U"]) for a in ARMS)
    ck = keys["U"]

    # ---- verification against the frozen summary tables -------------------------------------
    checks = []
    arms_frozen = pd.read_csv(FROZEN / "x1_arms.tsv", sep="\t").set_index("arm")
    for a in ARMS:
        mu, lo, hi = boot(vals[a])
        pooled = float(seqnll[a].sum() / n_tok.sum())
        for name, got, want in (
            (f"{a} test_nll_component_mean", round(mu, 5), arms_frozen.loc[a, "test_nll_component_mean"]),
            (f"{a} ci_lo", round(lo, 5), arms_frozen.loc[a, "ci_lo"]),
            (f"{a} ci_hi", round(hi, 5), arms_frozen.loc[a, "ci_hi"]),
            (f"{a} test_nll_pooled", round(pooled, 5), arms_frozen.loc[a, "test_nll_pooled"]),
            (f"{a} n_components", len(vals[a]), arms_frozen.loc[a, "n_components"]),
        ):
            checks.append(dict(quantity=name, rederived=got, frozen=want, match=bool(got == want)))

    cmp_frozen = pd.read_csv(FROZEN / "x1_comparisons.tsv", sep="\t").set_index("comparison")
    diffs = {}
    for a, b in (("T", "U"), ("R", "U"), ("R", "T")):
        dd = vals[a] - vals[b]
        diffs[f"{a}_minus_{b}"] = dd
        r = paired(dd)
        row = cmp_frozen.loc[f"{a} - {b}"]
        for k in ("diff", "ci_lo", "ci_hi", "frac_components_favouring_a", "n_components"):
            checks.append(dict(quantity=f"{a}-{b} {k}",
                               rederived=round(float(r[k]), 10), frozen=round(float(row[k]), 10),
                               match=bool(abs(float(r[k]) - float(row[k])) < TOL)))

    # descriptive strata, recomputed per stratum exactly as the frozen run did
    strat_frozen = pd.read_csv(FROZEN / "x1_strata.tsv", sep="\t").set_index("stratum")
    for t in ("T1", "T2", "T3", "T4"):
        mask = d[t][te] == 1
        ka, va = comp_mean(seqnll["R"][mask], n_tok[mask], comp[mask])
        kb, vb = comp_mean(seqnll["T"][mask], n_tok[mask], comp[mask])
        assert np.array_equal(ka, kb)
        r = paired(va - vb)
        row = strat_frozen.loc[t]
        for k in ("diff", "ci_lo", "ci_hi", "n_components"):
            checks.append(dict(quantity=f"stratum {t} R-T {k}",
                               rederived=round(float(r[k]), 10), frozen=round(float(row[k]), 10),
                               match=bool(abs(float(r[k]) - float(row[k])) < TOL)))

    chk = pd.DataFrame(checks)
    chk.to_csv(OUT / "x1_rederivation_check.tsv", sep="\t", index=False)
    bad = chk.loc[~chk["match"]]
    if len(bad):
        print(bad.to_string(index=False), file=sys.stderr)
        print(f"FAIL: {len(bad)}/{len(chk)} checks disagree with the frozen bundle", file=sys.stderr)
        return 1

    # ---- the component-level table ----------------------------------------------------------
    rows = []
    for i, c in enumerate(ck):
        m = comp == c
        types, counts = np.unique(d["retron_type"][te][m], return_counts=True)
        rows.append(dict(
            component_id=c,
            n_pairs=int(m.sum()),
            n_tokens=int(n_tok[m].sum()),
            nll_U=vals["U"][i], nll_T=vals["T"][i], nll_R=vals["R"][i],
            d_R_minus_T=vals["R"][i] - vals["T"][i],
            d_T_minus_U=vals["T"][i] - vals["U"][i],
            d_R_minus_U=vals["R"][i] - vals["U"][i],
            majority_retron_type=str(types[counts.argmax()]),
            n_retron_types=int(len(types)),
            n_pairs_T3=int((d["T3"][te][m] == 1).sum()),
            n_pairs_T4=int((d["T4"][te][m] == 1).sum()),
            in_sensitivity_population=int((d["sensitivity"][te][m] == 1).any()),
            median_rt_aa_len=float(np.median(d["rt_aa_len"][te][m])),
        ))
    tab = pd.DataFrame(rows).sort_values("n_pairs", ascending=False)
    tab.to_csv(OUT / "x1_component_level.tsv", sep="\t", index=False)

    n_eff = float(tab["n_pairs"].sum() ** 2 / (tab["n_pairs"] ** 2).sum())
    meta = dict(
        source_run="results/embed_x1_conditional_pilot (commit 8bf7207)",
        per_sequence_arrays=str(WORK),
        aggregation="per-sequence NLL sum -> per-component token-weighted mean (x06_eval.comp_mean)",
        bootstrap=dict(seed=SEED, resamples=N_BOOT, unit="component"),
        n_test_pairs=int(len(te)), n_components=int(len(tab)), n_eff_test=round(n_eff, 2),
        frozen_checks=dict(total=int(len(chk)), passed=int(chk["match"].sum())),
        recomputed_model_outputs=False,
    )
    (OUT / "x1_component_level.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"OK: {len(chk)}/{len(chk)} checks reproduce the frozen bundle; "
          f"{len(tab)} components, n_eff {n_eff:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
