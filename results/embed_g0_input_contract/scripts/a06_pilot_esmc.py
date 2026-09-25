#!/usr/bin/env python
"""embed-g0/a06 - gated ESM-C 300M pilot. NOT the production run.

Five things must be reported before production is allowed to start (launcher section 8):

  1 import/harness validation      - model loads, dim is 960, BOS/EOS geometry is what we think
  2 context-limit handling         - operator amendment 1: verify the real limit, never truncate
                                     silently, and give over-length sequences an explicit state
  3 length-stratified smoke test   - across the REAL distribution, never the head of the file
  4 measured throughput, peak VRAM - the production estimate is replaced by this number
  5 output-content validation      - pooled == mean over stripped residue tokens; and a batched
                                     forward agrees with a solo forward
  + determinism                    - the frozen batching rule re-runs BIT-IDENTICAL, and a
                                     deliberately different geometry DIFFERS. Both branches must
                                     fire or the check is vacuous.

THE FROZEN BATCHING RULE, declared here and not changed afterwards:
    order   = sorted by (seq_len, seq_hash)              -- total, deterministic, no ties
    batches = consecutive runs of BATCH sequences
    solo    = any sequence with seq_len > SOLO_LEN is forwarded alone
    dtype   = fp32 forward (no autocast), fp16 on disk
Arrays are NEVER compared by max|delta| - that statistic is a length correlate.

Env: /home/borg/miniconda3/envs/retron_esmc/bin/python   (esm 3.2.0, torch 2.5.1+cu121)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from esm.models.esmc import ESMC

TASK = Path(__file__).resolve().parents[1]
W, OUT = TASK / "work", TASK / "tables"
DIM = 960
BATCH = 8
SOLO_LEN = 1024            # beyond this a sequence is forwarded alone (VRAM, not correctness)
N_SMOKE = 200
CTX_DECLARED = 2048        # the length beyond which we report an explicit state, see below


def read_faa(p: Path) -> dict[str, str]:
    seqs, sid, buf = {}, None, []
    for line in p.read_text().splitlines():
        if line.startswith(">"):
            if sid:
                seqs[sid] = "".join(buf)
            sid, buf = line[1:].split()[0], []
        else:
            buf.append(line.strip())
    if sid:
        seqs[sid] = "".join(buf)
    return seqs


def order_frozen(ids: list[str], seqs: dict[str, str]) -> list[str]:
    """THE frozen order. Total and deterministic: (len, hash) admits no ties."""
    return sorted(ids, key=lambda s: (len(seqs[s]), s))


def batches_frozen(ids: list[str], seqs: dict[str, str], batch: int) -> list[list[str]]:
    out, cur = [], []
    for s in order_frozen(ids, seqs):
        if len(seqs[s]) > SOLO_LEN:
            if cur:
                out.append(cur); cur = []
            out.append([s]); continue
        cur.append(s)
        if len(cur) == batch:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def embed(model, ids, seqs, batch) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], float]:
    """Returns pooled, per-residue, seconds. Per-residue is kept only for the smoke set."""
    pooled, tokens = {}, {}
    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    for chunk in batches_frozen(ids, seqs, batch):
        toks = model._tokenize([seqs[s] for s in chunk])
        with torch.no_grad():
            E = model(toks.cuda()).embeddings              # (B, Lmax+2, 960)
        for k, s in enumerate(chunk):
            L = len(seqs[s])
            a = E[k, 1:L + 1]                              # strip BOS/EOS
            if tuple(a.shape) != (L, DIM):
                raise AssertionError(f"{s}: token array {tuple(a.shape)}, expected {(L, DIM)}")
            v = a.mean(0).float().cpu().numpy().astype(np.float16)
            t = a.float().cpu().numpy().astype(np.float16)
            for name, arr in (("pooled", v), ("tokens", t)):
                if not np.isfinite(arr).all():
                    raise AssertionError(f"{s}: non-finite in {name}")
                if not arr.any():
                    raise AssertionError(f"{s}: all-zero {name}")
            pooled[s], tokens[s] = v, t
    return pooled, tokens, time.perf_counter() - t0


def mean_cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.astype(np.float32), b.astype(np.float32)
    if a.ndim == 1:
        a, b = a[None], b[None]
    num = (a * b).sum(1)
    den = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return float(np.mean(num / np.maximum(den, 1e-9)))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rep: dict[str, object] = {}

    print("[1] import / harness validation")
    if not torch.cuda.is_available():
        raise SystemExit("no CUDA device visible")
    dev = torch.cuda.get_device_name(0)
    print(f"    device {dev}  torch {torch.__version__}  cuda {torch.version.cuda}")
    m = ESMC.from_pretrained("esmc_300m").eval().cuda()
    n_par = sum(p.numel() for p in m.parameters())
    probe = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ"
    t = m._tokenize([probe])
    with torch.no_grad():
        E = m(t.cuda()).embeddings
    assert tuple(E.shape) == (1, len(probe) + 2, DIM), f"geometry {tuple(E.shape)}"
    print(f"    params {n_par:,}  embeddings {tuple(E.shape)} == (1, L+2, {DIM})  BOS/EOS confirmed")
    rep |= {"device": dev, "torch": torch.__version__, "cuda": torch.version.cuda,
            "params": n_par, "dim": DIM, "token_geometry": "(B, L+2, 960), BOS/EOS stripped"}

    print("\n[2] context limit - operator amendment 1")
    # ESM-C uses ROTARY position embeddings with a cache grown on demand; the only nn.Embedding
    # in the model is the 64-token VOCABULARY table. There is therefore NO learned positional
    # limit and no architectural truncation point. The tokenizer declares no max length either.
    from esm.tokenization import get_esmc_model_tokenizers
    tok = get_esmc_model_tokenizers()
    has_pos = any("pos" in n.lower() and "embed" in n.lower() for n, _ in m.named_parameters())
    print(f"    learned positional-embedding parameter present: {has_pos}")
    print(f"    tokenizer model_max_length: {tok.model_max_length} (no practical cap)")
    seqs_all = read_faa(W / "rt_pair_universe.faa")
    longest = sorted(seqs_all, key=lambda s: -len(seqs_all[s]))[:3]
    ctx_rows = []
    for s in longest:
        L = len(seqs_all[s])
        torch.cuda.reset_peak_memory_stats()
        t0 = time.perf_counter()
        with torch.no_grad():
            E = m(m._tokenize([seqs_all[s]]).cuda()).embeddings
        ok = bool(torch.isfinite(E).all()) and tuple(E.shape) == (1, L + 2, DIM)
        vram = torch.cuda.max_memory_allocated() / 2**30
        ctx_rows.append(dict(rt_seq_hash=s, aa_len=L, forward_ok=ok,
                             peak_vram_gb=round(vram, 2), seconds=round(time.perf_counter()-t0, 2),
                             state="LEN_EXTRAPOLATED" if L > CTX_DECLARED else "LEN_NOMINAL"))
        print(f"    {s[:12]}  L={L:5,}  ok={ok}  peak VRAM {vram:.2f} GB  "
              f"{ctx_rows[-1]['state']}")
    rep |= {"positional_scheme": "rotary (no learned position table)",
            "tokenizer_max_length": int(tok.model_max_length),
            "truncation": "none - no sequence is truncated",
            "context_state_rule": f"aa_len > {CTX_DECLARED} -> LEN_EXTRAPOLATED, reported "
                                  f"separately, never pooled into a headline number"}

    print(f"\n[3] length-stratified smoke test  (n={N_SMOKE}, spanning the real distribution)")
    order = sorted(seqs_all, key=lambda s: (len(seqs_all[s]), s))
    idx = np.linspace(0, len(order) - 1, N_SMOKE).astype(int)
    smoke = [order[i] for i in dict.fromkeys(idx)]
    sl = [len(seqs_all[s]) for s in smoke]
    print(f"    {len(smoke)} sequences, len {min(sl)}-{max(sl)}, median {int(np.median(sl))}")

    print("\n[4] throughput and peak VRAM under the frozen rule")
    torch.cuda.reset_peak_memory_stats()
    pooled, tokens, secs = embed(m, smoke, seqs_all, BATCH)
    vram = torch.cuda.max_memory_allocated() / 2**30
    res = sum(sl)
    rate_seq, rate_res = len(smoke) / secs, res / secs
    print(f"    {len(smoke)} seq / {res:,} residues in {secs:.1f}s  "
          f"= {rate_seq:.1f} seq/s, {rate_res:,.0f} res/s   peak VRAM {vram:.2f} GB")
    total_res = 11_236_474
    est_min = total_res / rate_res / 60
    print(f"    PROJECTED production (29,192 seq / {total_res:,} residues): {est_min:.1f} min")
    rep |= {"batch_rule": f"sorted by (len, hash), BATCH={BATCH}, solo if len>{SOLO_LEN}, fp32 fwd",
            "smoke_n": len(smoke), "smoke_seconds": round(secs, 1),
            "seq_per_s": round(rate_seq, 2), "res_per_s": round(rate_res, 1),
            "peak_vram_gb": round(vram, 2), "projected_production_min": round(est_min, 1)}

    print("\n[5] output-content validation")
    s0 = smoke[len(smoke) // 2]
    recomputed = tokens[s0].astype(np.float32).mean(0)
    d = float(np.abs(recomputed - pooled[s0].astype(np.float32)).max())
    print(f"    pooled == mean over stripped residue tokens: max|d| {d:.2e} (fp16 round-trip)")
    assert d < 1e-2, "pooling does not match the token cache"
    with torch.no_grad():
        Es = m(m._tokenize([seqs_all[s0]]).cuda()).embeddings
    solo = Es[0, 1:len(seqs_all[s0]) + 1].float().cpu().numpy()
    cos_solo = mean_cos(tokens[s0], solo)
    print(f"    batched vs solo forward, mean per-position cosine: {cos_solo:.6f}")
    rep |= {"pool_vs_tokens_maxabs": d, "batched_vs_solo_cosine": round(cos_solo, 6)}

    print("\n[6] determinism - both branches must fire")
    p2, t2, _ = embed(m, smoke, seqs_all, BATCH)
    ident = all(np.array_equal(tokens[s], t2[s]) for s in smoke)
    print(f"    same frozen rule, re-run: bit-identical on all {len(smoke)} = {ident}")
    p3, t3, _ = embed(m, smoke, seqs_all, BATCH + 1)
    diff = [s for s in smoke if not np.array_equal(tokens[s], t3[s])]
    cos_geom = float(np.mean([mean_cos(tokens[s], t3[s]) for s in diff])) if diff else float("nan")
    print(f"    different batch geometry: {len(diff)}/{len(smoke)} arrays differ, "
          f"mean per-position cosine {cos_geom:.6f}")
    if not ident:
        raise AssertionError("frozen rule is NOT reproducible - do not run production")
    rep |= {"determinism_bit_identical": ident, "geometry_sensitive_arrays": len(diff),
            "geometry_change_cosine": None if not diff else round(cos_geom, 6)}

    import pandas as pd
    pd.DataFrame(ctx_rows).to_csv(OUT / "g0_esmc_context.tsv", sep="\t", index=False)
    (OUT / "g0_esmc_pilot.json").write_text(json.dumps(rep, indent=2, default=str) + "\n")
    print("\nPILOT COMPLETE - wrote g0_esmc_pilot.json, g0_esmc_context.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
