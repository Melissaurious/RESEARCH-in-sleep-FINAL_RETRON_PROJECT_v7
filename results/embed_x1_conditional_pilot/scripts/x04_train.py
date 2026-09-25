#!/usr/bin/env python
"""embed_x1/x04 - train one arm (U / T / R). Hyperparameters are PREREG-fixed; nothing is tuned.

Validation is used for exactly one thing: selecting the checkpoint with the lowest validation
per-nucleotide NLL (patience 5, max 40 epochs). TEST IS NEVER TOUCHED HERE.
"""
from __future__ import annotations

import argparse, json, math, sys, time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x03_model import CondNcRNADecoder, count_params, PAD  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
W = TASK / "work"
SEED, MAX_EPOCHS, PATIENCE = 20260918, 40, 5
LR, WARMUP, WD, ACCUM, BATCH = 2e-4, 4000, 0.0, 2, 32


def load():
    d = np.load(W / "dataset.npz", allow_pickle=False)
    rt = np.load(W / "rt_chunks.npy", mmap_mode="r")
    rtm = np.load(W / "rt_chunk_mask.npy")
    ix = [l.split("\t") for l in (W / "rt_chunk_index.tsv").read_text().splitlines()[1:]]
    rrow = {h: int(r) for h, r, _ in ix}
    return d, rt, rtm, rrow


def batches(idx, bs, rng=None):
    order = rng.permutation(idx) if rng is not None else idx
    for i in range(0, len(order), bs):
        yield order[i:i + bs]


def make_batch(sel, d, rt, rtm, rrow, arm, dev):
    nc_row = d["nc_row"][sel]
    L = int(d["nc_len"][nc_row].max())
    tok = torch.from_numpy(d["nc_tokens"][nc_row][:, :L].astype(np.int64)).to(dev)
    b = {"tokens": tok}
    if arm == "T":
        b["type_id"] = torch.from_numpy(d["type_id"][sel].astype(np.int64)).to(dev)
    elif arm == "R":
        rows = np.array([rrow[h] for h in d["rt_hash"][sel]])
        b["rt_chunks"] = torch.from_numpy(np.asarray(rt[rows], dtype=np.float32)).to(dev)
        b["rt_mask"] = torch.from_numpy(rtm[rows]).to(dev)
    return b


@torch.no_grad()
def evaluate(model, idx, d, rt, rtm, rrow, arm, dev, bs=64):
    model.eval()
    s, n = [], []
    for sel in batches(idx, bs):
        o = model(make_batch(sel, d, rt, rtm, rrow, arm, dev))
        s.append(o["nll_sum"].cpu().numpy()); n.append(o["n_tok"].cpu().numpy())
    s, n = np.concatenate(s), np.concatenate(n)
    return float(s.sum() / n.sum()), s, n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["U", "T", "R"])
    ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=MAX_EPOCHS)
    a = ap.parse_args()

    torch.manual_seed(SEED); np.random.seed(SEED)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    d, rt, rtm, rrow = load()
    tr = np.where(d["fold"] == "train")[0]
    va = np.where(d["fold"] == "val")[0]
    if a.smoke:
        rng0 = np.random.default_rng(SEED)
        tr = rng0.choice(tr, size=min(a.smoke, len(tr)), replace=False)
        va = rng0.choice(va, size=min(a.smoke // 2, len(va)), replace=False)

    # ---- leakage guard: the training indices must not touch val or test components ----
    comp = d["component"]
    assert not (set(comp[tr]) & set(comp[va])), "component leakage between train and val"
    te = np.where(d["fold"] == "test")[0]
    assert not (set(comp[tr]) & set(comp[te])), "component leakage between train and test"

    model = CondNcRNADecoder(a.arm).to(dev)
    pc = count_params(model)
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / WARMUP))
    print(f"arm {a.arm}  params {pc['total']:,} (decoder {pc['shared_decoder']:,}, "
          f"conditioning {pc['conditioning_path']:,})  device {dev}")
    print(f"train {len(tr):,} pairs / {len(set(comp[tr]))} comps   "
          f"val {len(va):,} / {len(set(comp[va]))} comps", flush=True)

    best, best_ep, bad, hist = math.inf, -1, 0, []
    ckpt = W / f"model_{a.arm}{'_smoke' if a.smoke else ''}.pt"
    rng = np.random.default_rng(SEED)
    step = 0
    for ep in range(a.epochs):
        model.train(); t0 = time.perf_counter(); tot, ntok = 0.0, 0.0
        opt.zero_grad(set_to_none=True)
        for i, sel in enumerate(batches(tr, BATCH, rng)):
            o = model(make_batch(sel, d, rt, rtm, rrow, a.arm, dev))
            loss = o["nll_sum"].sum() / o["n_tok"].sum()
            (loss / ACCUM).backward()
            if (i + 1) % ACCUM == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step(); sched.step(); opt.zero_grad(set_to_none=True); step += 1
            tot += float(o["nll_sum"].sum()); ntok += float(o["n_tok"].sum())
        trn = tot / ntok
        vnll, _, _ = evaluate(model, va, d, rt, rtm, rrow, a.arm, dev)
        hist.append(dict(epoch=ep, train_nll=round(trn, 5), val_nll=round(vnll, 5),
                         val_ppl=round(math.exp(vnll), 4), sec=round(time.perf_counter() - t0, 1)))
        improved = vnll < best - 1e-5
        print(f"  ep {ep:02d}  train {trn:.4f}  val {vnll:.4f} (ppl {math.exp(vnll):.3f})  "
              f"{hist[-1]['sec']}s {'*' if improved else ''}", flush=True)
        if improved:
            best, best_ep, bad = vnll, ep, 0
            torch.save({"state_dict": model.state_dict(), "arm": a.arm, "epoch": ep,
                        "val_nll": vnll, "params": pc}, ckpt)
        else:
            bad += 1
            if bad >= PATIENCE:
                print(f"  early stop: no improvement for {PATIENCE} epochs"); break

    (W / f"hist_{a.arm}{'_smoke' if a.smoke else ''}.json").write_text(json.dumps(
        dict(arm=a.arm, params=pc, best_val_nll=best, best_epoch=best_ep,
             seed=SEED, lr=LR, warmup=WARMUP, batch=BATCH, accum=ACCUM,
             max_epochs=a.epochs, patience=PATIENCE, smoke=a.smoke, history=hist),
        indent=2) + "\n")
    print(f"BEST val NLL {best:.5f} at epoch {best_ep} -> {ckpt.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
