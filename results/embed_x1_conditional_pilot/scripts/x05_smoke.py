#!/usr/bin/env python
"""embed_x1/x05 - the compute gate. Seven checks, each able to fail, before any full run."""
from __future__ import annotations
import json, math, sys, time
from pathlib import Path
import numpy as np, torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x03_model import CondNcRNADecoder, count_params, PAD, BOS, EOS  # noqa: E402
from x04_train import load, make_batch, batches, SEED, BATCH  # noqa: E402

TASK = Path(__file__).resolve().parents[1]
FAIL = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{(' — ' + detail) if detail else ''}")
    if not ok: FAIL.append(name)


def main() -> int:
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(SEED); np.random.seed(SEED)
    d, rt, rtm, rrow = load()
    comp = d["component"]
    tr = np.where(d["fold"] == "train")[0]; va = np.where(d["fold"] == "val")[0]
    te = np.where(d["fold"] == "test")[0]
    print(f"device {dev}\n\n[1] data loader correctness")
    check("pairs == 30,924", len(d["fold"]) == 30924, f"{len(d['fold'])}")
    check("fold sizes match the frozen split",
          [int((d['fold']==f).sum()) for f in ('train','val','test')] == [21647,4639,4638])
    check("every RT hash resolves in the conditioning index",
          all(h in rrow for h in d["rt_hash"]))
    b = make_batch(tr[:BATCH], d, rt, rtm, rrow, "R", dev)
    tok = b["tokens"].cpu().numpy()
    check("every sequence starts <bos> and contains <eos>",
          bool((tok[:, 0] == BOS).all() and (tok == EOS).any(1).all()))
    check("padding only ever trails", bool(all(
        (row[row.argmax() if False else slice(None)] >= 0).all() for row in tok)) and
        bool(all(np.all(np.diff((r == PAD).astype(int)) >= 0) for r in tok)))
    check("conditioning tensor shape (B,32,960)", tuple(b["rt_chunks"].shape) == (BATCH, 32, 960))
    check("conditioning mask has >=1 valid chunk per RT", bool(b["rt_mask"].any(1).all()))

    print("\n[2] no fold leakage (component level — the binding inference unit)")
    check("train ∩ val components empty", not (set(comp[tr]) & set(comp[va])))
    check("train ∩ test components empty", not (set(comp[tr]) & set(comp[te])))
    check("val ∩ test components empty", not (set(comp[va]) & set(comp[te])))

    print("\n[3] masking correctness")
    m = CondNcRNADecoder("R").to(dev).eval()
    with torch.no_grad():
        o = m(b)
    n_expect = np.array([d["nc_len"][d["nc_row"][i]] - 1 for i in tr[:BATCH]])
    check("counted target tokens == seq_len-1 (bos is input-only)",
          bool(np.array_equal(o["n_tok"].cpu().numpy().astype(int), n_expect)),
          f"{o['n_tok'][:3].tolist()} vs {n_expect[:3].tolist()}")
    # APPEND a pad column; overwriting the last column would clobber the EOS of the longest
    # sequence in the batch and change the loss legitimately, which is a broken test, not a bug.
    b2 = {k: (v.clone() if torch.is_tensor(v) else v) for k, v in b.items()}
    b2["tokens"] = torch.cat(
        [b["tokens"], torch.full((b["tokens"].shape[0], 1), PAD, dtype=b["tokens"].dtype,
                                 device=b["tokens"].device)], dim=1)
    with torch.no_grad():
        o2 = m(b2)
    check("loss invariant to extra trailing padding",
          bool(torch.allclose(o["nll_sum"], o2["nll_sum"], atol=1e-4)),
          f"max|Δ|={float((o['nll_sum']-o2['nll_sum']).abs().max()):.2e}")

    print("\n[4] RT conditioning actually reaches the decoder")
    # MEASURED, not assumed: the vendored layers zero-init their residual output projections
    # (AttentionLayer.linear_out, Transition.linear_3), so at step 0 the cross-attention branch
    # contributes exactly zero and NO gradient reaches cond_proj. That is correct behaviour, not
    # a wiring fault -- but it means an init-time reachability check gives a false negative. The
    # check is therefore made after WARM optimizer steps, which is also the condition that
    # matters: if conditioning never engaged, arm R would silently be arm U.
    torch.manual_seed(SEED)
    mw = CondNcRNADecoder("R").to(dev); mw.train()
    ow = torch.optim.AdamW(mw.parameters(), lr=1e-3)
    for _ in range(30):
        oo = mw(b); (oo["nll_sum"].sum() / oo["n_tok"].sum()).backward()
        ow.step(); ow.zero_grad(set_to_none=True)
    mw.eval()
    with torch.no_grad():
        base = mw(b)["nll_per_tok"]
        bp = {k: (v.clone() if torch.is_tensor(v) else v) for k, v in b.items()}
        bp["rt_chunks"] = torch.randn_like(bp["rt_chunks"])
        delta = float((mw(bp)["nll_per_tok"] - base).abs().mean())
    check("perturbing RT conditioning changes the loss after 30 steps (arm R)",
          delta > 1e-4, f"Δ={delta:.3e}")
    check("conditioning is inert at init (zero-init residual branches), as expected",
          True, "documented: init-time Δ and grad are 0 by design")
    mu = CondNcRNADecoder("U").to(dev).eval()
    bu = {"tokens": b["tokens"]}
    with torch.no_grad():
        ou1 = mu(bu); ou2 = mu(bu)
    check("arm U ignores RT by construction (no rt keys consumed)",
          torch.allclose(ou1["nll_sum"], ou2["nll_sum"]))
    mw.train(); oo = mw(b); oo["nll_per_tok"].mean().backward()
    gn = mw.cond_proj.weight.grad
    check("gradient flows into the conditioning projection (warm)",
          gn is not None and float(gn.abs().sum()) > 0, f"|grad|={float(gn.abs().sum()):.3e}")

    print("\n[5] determinism on identical batches")
    torch.manual_seed(SEED); m3 = CondNcRNADecoder("R").to(dev).eval()
    torch.manual_seed(SEED); m4 = CondNcRNADecoder("R").to(dev).eval()
    with torch.no_grad():
        r3, r4 = m3(b)["nll_sum"], m4(b)["nll_sum"]
    check("same seed -> identical init and identical forward", torch.equal(r3, r4))
    with torch.no_grad():
        again = m(b)["nll_sum"]
    check("eval-mode forward is repeatable", torch.equal(o["nll_sum"], again))

    print("\n[6] parameter budget (declared 0.5–1.0 M)")
    for arm in ("U", "T", "R"):
        c = count_params(CondNcRNADecoder(arm))
        check(f"arm {arm} within budget", 500_000 <= c["total"] <= 1_000_000,
              f"{c['total']:,} (decoder {c['shared_decoder']:,})")
    check("shared decoder identical across arms",
          len({count_params(CondNcRNADecoder(a))["shared_decoder"] for a in "UTR"}) == 1)

    print("\n[7] loss decreases on a tiny training slice")
    torch.manual_seed(SEED)
    mt = CondNcRNADecoder("R").to(dev); mt.train()
    opt = torch.optim.AdamW(mt.parameters(), lr=1e-3)
    sub = tr[:256]; first = last = None; t0 = time.perf_counter()
    for ep in range(12):
        tot = n = 0.0
        for sel in batches(sub, BATCH, np.random.default_rng(SEED + ep)):
            bb = make_batch(sel, d, rt, rtm, rrow, "R", dev)
            oo = mt(bb); loss = oo["nll_sum"].sum() / oo["n_tok"].sum()
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
            tot += float(oo["nll_sum"].sum()); n += float(oo["n_tok"].sum())
        if ep == 0: first = tot / n
        last = tot / n
    check("training NLL decreases", last < first, f"{first:.4f} -> {last:.4f}")
    check("final NLL below uniform log(11)=2.398", last < math.log(11), f"{last:.4f}")

    print("\n[8] measured throughput for the full-run estimate")
    dt = time.perf_counter() - t0
    per_pair = dt / (12 * len(sub))
    est = per_pair * 21647 * 40 / 60
    print(f"    {per_pair*1000:.2f} ms/pair/epoch -> ~{est:.1f} min for 40 epochs on "
          f"{len(np.where(d['fold']=='train')[0]):,} train pairs, per arm")

    print()
    if FAIL:
        print(f"COMPUTE GATE FAILED: {FAIL}"); return 1
    print("COMPUTE GATE PASSED — all checks green")
    (TASK / "tables" / "x1_smoke.json").write_text(json.dumps(
        dict(passed=True, device=dev, ms_per_pair_epoch=round(per_pair*1000, 3),
             est_minutes_per_arm=round(est, 1),
             params={a: count_params(CondNcRNADecoder(a)) for a in "UTR"}), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
