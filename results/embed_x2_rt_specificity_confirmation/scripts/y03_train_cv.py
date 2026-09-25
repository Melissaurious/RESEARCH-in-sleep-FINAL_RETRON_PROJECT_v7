#!/usr/bin/env python
"""embed_x2/y03 - train one (arm, fold) cell of the cross-fit. Hyperparameters FROZEN from X1.

Nothing is tuned. The model class, tokenizer, decoder, RT projection, optimizer, LR schedule,
epoch cap, stopping rule, batching, loss and frozen ESM-C representation are imported from the
X1 code unchanged. The only new things are the fold index and the conditioning SOURCE.

FIVE ARMS. U, T and R reuse the X1 model classes verbatim. G and P use the R ARCHITECTURE with
a different conditioning tensor, so no new parameters and no new code path are introduced:

    U  no protein information            (X1 model arm "U")
    T  retron-type label                 (X1 model arm "T")
    G  ESM-C of the RT CLUSTER REPRESENTATIVE (frozen rt_id0.50) -- coarse RT lineage
    R  ESM-C of the observed RT          (X1 model arm "R")
    P  ESM-C of a PERMUTED RT            -- falsification control, see below

PERMUTATION CONTROL (arm P), one prespecified procedure, declared before running. Within each
retron type, the RT assigned to each TRAINING pair is permuted among the training pairs of that
type (a derangement where the type has >= 2 distinct RTs; seed 20260918). Validation and test
conditioning use the TRUE RT. The question this answers: does the R advantage require the
observed RT<->ncRNA correspondence, or does any RT from the same structural population supply
it? Only the training correspondence is destroyed; nothing else changes.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time
from pathlib import Path

import numpy as np
import torch

# Resolve the frozen X1 model module without hard-coding one machine's layout: prefer the
# landed X1 bundle, else fall back to this script's own directory (how it is staged on Ibex,
# where x03_model.py is copied alongside). Editing a hard-coded path in place on the cluster
# is how the first submission was broken.
_X1_LOCAL = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings"
                 "/results/embed_x1_conditional_pilot/scripts")
for _p in (_X1_LOCAL, Path(__file__).resolve().parent):
    if (_p / "x03_model.py").is_file():
        sys.path.insert(0, str(_p))
        break
else:
    raise SystemExit("cannot locate the frozen X1 x03_model.py")
from x03_model import CondNcRNADecoder, count_params, PAD  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
W = TASK / "work"
# every one of these is inherited from X1 and is not a free parameter here
SEED, MAX_EPOCHS, PATIENCE = 20260918, 40, 5
LR, WARMUP, WD, ACCUM, BATCH = 2e-4, 4000, 0.0, 2, 32
ARMS = {"U": "U", "T": "T", "G": "R", "R": "R", "P": "R"}


def load(work_dir: Path):
    d = np.load(work_dir / "dataset.npz", allow_pickle=False)
    cv = np.load(work_dir / "crossfit.npz", allow_pickle=False)
    rt = np.load(work_dir / "rt_chunks.npy", mmap_mode="r")
    rtm = np.load(work_dir / "rt_chunk_mask.npy")
    ix = [l.split("\t") for l in (work_dir / "rt_chunk_index.tsv").read_text().splitlines()[1:]]
    rrow = {h: int(r) for h, r, _ in ix}
    return d, cv, rt, rtm, rrow


def cond_rows(arm, d, cv, rrow, idx, perm_map=None):
    """Which RT row conditions each pair, per arm. None for U/T."""
    if arm in ("U", "T"):
        return None
    if arm == "G":
        return np.array([rrow[h] for h in cv["rt_rep"][idx]])
    if arm == "P":
        return np.array([rrow[perm_map[i]] for i in idx])
    return np.array([rrow[h] for h in d["rt_hash"][idx]])


def build_permutation(d, tr_idx, seed=SEED):
    """Permute RT within retron type among TRAINING pairs. One rule, applied once."""
    rng = np.random.default_rng(seed)
    out = {}
    types = d["retron_type"][tr_idx]
    for t in np.unique(types):
        sel = tr_idx[types == t]
        hashes = d["rt_hash"][sel]
        if len(sel) == 1:
            out[sel[0]] = hashes[0]; continue
        for _ in range(64):                      # derange: no pair keeps its own RT
            p = rng.permutation(len(sel))
            if not np.any(hashes[p] == hashes):
                break
        for i, j in zip(sel, p):
            out[i] = hashes[j]
    return out


def make_batch(sel, d, rows, rt, rtm, model_arm, dev):
    nc_row = d["nc_row"][sel]
    L = int(d["nc_len"][nc_row].max())
    b = {"tokens": torch.from_numpy(d["nc_tokens"][nc_row][:, :L].astype(np.int64)).to(dev)}
    if model_arm == "T":
        b["type_id"] = torch.from_numpy(d["type_id"][sel].astype(np.int64)).to(dev)
    elif model_arm == "R":
        b["rt_chunks"] = torch.from_numpy(np.asarray(rt[rows], dtype=np.float32)).to(dev)
        b["rt_mask"] = torch.from_numpy(rtm[rows]).to(dev)
    return b


@torch.no_grad()
def evaluate(model, idx, rows, d, rt, rtm, model_arm, dev, bs=64):
    model.eval(); S, N = [], []
    for k in range(0, len(idx), bs):
        sel = idx[k:k + bs]
        r = rows[k:k + bs] if rows is not None else None
        o = model(make_batch(sel, d, r, rt, rtm, model_arm, dev))
        S.append(o["nll_sum"].cpu().numpy()); N.append(o["n_tok"].cpu().numpy())
    S, N = np.concatenate(S), np.concatenate(N)
    return float(S.sum() / N.sum()), S, N


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=list(ARMS))
    ap.add_argument("--fold", type=int, required=True)
    ap.add_argument("--work", type=Path, default=W)
    ap.add_argument("--epochs", type=int, default=MAX_EPOCHS)
    ap.add_argument("--smoke", type=int, default=0)
    # Replicate seeds estimate OPTIMIZATION variance only (DESIGN section 6). They do not
    # increase the biological sample size; predictions are averaged WITHIN component before
    # any inference. The default reproduces the frozen X1 seed exactly, so runs that do not
    # pass --seed are byte-identical to the original cross-fit.
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    model_arm = ARMS[a.arm]
    seed = a.seed

    torch.manual_seed(seed); np.random.seed(seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    d, cv, rt, rtm, rrow = load(a.work)
    f = cv["cv_fold"]
    te = np.where(f == a.fold)[0]
    va = np.where(f == (a.fold + 1) % 5)[0]
    tr = np.where(~np.isin(f, [a.fold, (a.fold + 1) % 5]))[0]
    if a.smoke:
        g = np.random.default_rng(SEED)
        tr = g.choice(tr, size=min(a.smoke, len(tr)), replace=False)
        va = g.choice(va, size=min(a.smoke // 2, len(va)), replace=False)

    comp = d["component"]
    assert not (set(comp[tr]) & set(comp[va])), "train/val component leak"
    assert not (set(comp[tr]) & set(comp[te])), "train/test component leak"

    perm = build_permutation(d, tr, seed) if a.arm == "P" else None
    rows_tr = cond_rows(a.arm, d, cv, rrow, tr, perm)
    # validation and test ALWAYS condition on the true RT, including for arm P
    eval_arm = "R" if a.arm in ("G", "R", "P") else a.arm
    rows_va = cond_rows("G" if a.arm == "G" else ("R" if eval_arm == "R" else a.arm),
                        d, cv, rrow, va)
    rows_te = cond_rows("G" if a.arm == "G" else ("R" if eval_arm == "R" else a.arm),
                        d, cv, rrow, te)

    model = CondNcRNADecoder(model_arm).to(dev)
    pc = count_params(model)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / WARMUP))
    # seed suffix only for replicates, so the primary cross-fit keeps its filenames
    tag = (f"{a.arm}_f{a.fold}" + ("" if seed == SEED else f"_s{seed}")
           + ("_smoke" if a.smoke else ""))
    print(f"[{tag}] model_arm {model_arm}  params {pc['total']:,}  device {dev} "
          f"({torch.cuda.get_device_name(0) if dev=='cuda' else '-'})")
    print(f"[{tag}] train {len(tr):,} / val {len(va):,} / test {len(te):,} pairs; "
          f"train comps {len(set(comp[tr]))}", flush=True)

    best, best_ep, bad, hist = math.inf, -1, 0, []
    # PID-unique checkpoint. If two processes ever run the same cell concurrently, each must
    # reload ITS OWN best-validation checkpoint; a shared path lets one process load the
    # other's weights and silently breaks the frozen stopping rule. The canonical
    # m_{tag}.pt is produced by an atomic rename only once this run is finished.
    ck = a.work / f".m_{tag}.pid{os.getpid()}.pt"
    rng = np.random.default_rng(seed)
    for ep in range(a.epochs):
        model.train(); t0 = time.perf_counter(); tot = ntok = 0.0
        order = rng.permutation(len(tr))
        opt.zero_grad(set_to_none=True)
        for i in range(0, len(order), BATCH):
            j = order[i:i + BATCH]
            o = model(make_batch(tr[j], d, None if rows_tr is None else rows_tr[j],
                                 rt, rtm, model_arm, dev))
            (o["nll_sum"].sum() / o["n_tok"].sum() / ACCUM).backward()
            if (i // BATCH + 1) % ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
            tot += float(o["nll_sum"].sum()); ntok += float(o["n_tok"].sum())
        vnll, _, _ = evaluate(model, va, rows_va, d, rt, rtm, model_arm, dev)
        hist.append(dict(epoch=ep, train_nll=round(tot / ntok, 5), val_nll=round(vnll, 5),
                         sec=round(time.perf_counter() - t0, 1)))
        imp = vnll < best - 1e-5
        print(f"  ep {ep:02d} train {tot/ntok:.4f} val {vnll:.4f} "
              f"{hist[-1]['sec']}s {'*' if imp else ''}", flush=True)
        if imp:
            best, best_ep, bad = vnll, ep, 0
            torch.save({"state_dict": model.state_dict(), "arm": a.arm,
                        "model_arm": model_arm, "fold": a.fold, "epoch": ep,
                        "val_nll": vnll, "params": pc}, ck)
        else:
            bad += 1
            if bad >= PATIENCE:
                print(f"  early stop after {PATIENCE} without improvement"); break

    model.load_state_dict(torch.load(ck, map_location=dev, weights_only=False)["state_dict"])
    ck.replace(a.work / f"m_{tag}.pt")     # publish atomically, only after this run's own load
    tnll, ts, tn = evaluate(model, te, rows_te, d, rt, rtm, model_arm, dev)
    np.savez_compressed(a.work / f"oof_{tag}.npz", idx=te, nll_sum=ts, n_tok=tn)
    (a.work / f"hist_{tag}.json").write_text(json.dumps(
        dict(arm=a.arm, model_arm=model_arm, fold=a.fold, params=pc, best_val_nll=best,
             best_epoch=best_ep, oof_test_nll=tnll, seed=seed, lr=LR, warmup=WARMUP,
             batch=BATCH, accum=ACCUM, patience=PATIENCE, max_epochs=a.epochs,
             gpu=torch.cuda.get_device_name(0) if dev == "cuda" else None,
             gpu_arch=(f"sm_{torch.cuda.get_device_capability(0)[0]}"
                       f"{torch.cuda.get_device_capability(0)[1]}") if dev == "cuda" else None,
             torch=torch.__version__, history=hist), indent=2) + "\n")
    print(f"[{tag}] best val {best:.5f} @ep{best_ep}; OUT-OF-FOLD test NLL {tnll:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
