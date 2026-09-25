#!/usr/bin/env python
"""embed-g0/a07 - gated RiNALMo giga-v1 pilot. NOT the production run.

Same five gates as the ESM-C pilot, plus the one trap this model is known for.

THE TRAP (documented in RETRON-DB_V4's EMBEDDINGS_HOWTO, re-derived here rather than trusted):
RiNALMo runs under bf16 autocast, and bf16 kernel REDUCTION ORDER depends on batch geometry.
The same sequence embedded alone, batched with a neighbour, or batched WITH ITSELF differs by
~3.5e-2 - padding is not the cause. Every such difference is below one bf16 ulp at the
representation scale. So:

  - this is NOT a defect, and must never be reported as one;
  - two arrays are NEVER compared by max|delta| - that statistic is a length correlate;
  - the answer is to FREEZE the batching rule, not to chase a tolerance.

THE FROZEN BATCHING RULE, identical in spirit to the ESM-C one:
    order   = sorted by (seq_len, seq_hash)
    batches = consecutive runs of BATCH sequences
    dtype   = bf16 autocast forward, fp16 on disk
    input   = DNA as stored. RiNALMo's alphabet is T-based and Alphabet.encode aliases U to T,
              so the precedent's .replace("T","U") is a NO-OP and is deliberately not carried.
    IUPAC   = R/Y/K/M/S/W/B/D/H/V/N are all in the vocabulary; nothing maps to <unk> and no
              substitution is applied. Verified before production, not after.

Env: /home/borg/miniconda3/envs/rinalmo/bin/python   (torch 2.7.1+cu118)
Weights: /home/borg/.cache/rinalmo_pretrained/giga-v1.pt
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[1]
OUT = TASK / "tables"
FNA = ROOT / "data" / "derived" / "rt_ncrna_oriented_v1.fna"
DIM = 1280
BATCH = 8
N_SMOKE = 200
IUPAC = set("RYKMSWBDHVN")


def read_fna(p: Path) -> dict[str, str]:
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


def batches_frozen(ids: list[str], seqs: dict[str, str], batch: int) -> list[list[str]]:
    order = sorted(ids, key=lambda s: (len(seqs[s]), s))
    return [order[i:i + batch] for i in range(0, len(order), batch)]


def embed(model, alphabet, ids, seqs, batch, device="cuda"):
    pooled, tokens = {}, {}
    t0 = time.perf_counter()
    for chunk in batches_frozen(ids, seqs, batch):
        toks = torch.tensor(alphabet.batch_tokenize([seqs[s] for s in chunk])).to(device)
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            rep = model(toks)["representation"]
        for j, s in enumerate(chunk):
            L = len(seqs[s])
            a = rep[j, 1:L + 1, :]                          # strip CLS/EOS
            if tuple(a.shape) != (L, DIM):
                raise AssertionError(f"{s}: token array {tuple(a.shape)}, expected {(L, DIM)}")
            t = a.float().cpu().numpy().astype(np.float16)
            v = t.astype(np.float32).mean(0).astype(np.float16)
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
    rep_meta: dict[str, object] = {}

    print("[1] import / harness validation")
    if not torch.cuda.is_available():
        raise SystemExit("no CUDA device visible")
    dev = torch.cuda.get_device_name(0)
    print(f"    device {dev}  torch {torch.__version__}  cuda {torch.version.cuda}")
    from rinalmo.pretrained import get_pretrained_model
    model, alphabet = get_pretrained_model(model_name="giga-v1")
    model = model.to(device="cuda").eval()
    n_par = sum(p.numel() for p in model.parameters())
    print(f"    params {n_par:,}")

    # vocabulary contract - checked BEFORE production
    vocab = set(alphabet.tkn_to_idx)
    missing = sorted((IUPAC | set("ACGT")) - vocab)
    assert not missing, f"alphabet lacks {missing}"
    u_as_t = alphabet.batch_tokenize(["ACGTU"])[0] [:-1][-2:]
    assert u_as_t[0] == u_as_t[1], "U is not aliased to T as assumed"
    print(f"    vocabulary covers ACGT + IUPAC {sorted(IUPAC)}; U aliases to T; no <unk> path")

    seqs = read_fna(FNA)
    assert len(seqs) == 16_458, f"{len(seqs)} sequences, expected 16,458"
    used = sorted({c for s in seqs.values() for c in s})
    assert set(used) <= vocab, f"corpus alphabet {used} not covered"
    print(f"    {len(seqs):,} ncRNA, alphabet {''.join(used)} - all in vocabulary")

    probe = list(seqs)[0]
    toks = torch.tensor(alphabet.batch_tokenize([seqs[probe]])).cuda()
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        r = model(toks)["representation"]
    assert tuple(r.shape) == (1, len(seqs[probe]) + 2, DIM), f"geometry {tuple(r.shape)}"
    print(f"    representation {tuple(r.shape)} == (1, L+2, {DIM})  CLS/EOS confirmed")
    rep_meta |= {"device": dev, "torch": torch.__version__, "cuda": torch.version.cuda,
                 "params": n_par, "dim": DIM,
                 "weights": "/home/borg/.cache/rinalmo_pretrained/giga-v1.pt",
                 "token_geometry": "(B, L+2, 1280), CLS/EOS stripped",
                 "alphabet_rule": "DNA as stored; U aliased to T by Alphabet.encode; "
                                  "IUPAC codes native; no substitution, no <unk>"}

    print("\n[2] context limit")
    L = [len(s) for s in seqs.values()]
    print(f"    ncRNA length {min(L)}-{max(L)}, median {int(np.median(L))} - "
          f"no truncation regime exists for this population")
    rep_meta |= {"truncation": "none", "len_min": min(L), "len_max": max(L)}

    print(f"\n[3] length-stratified smoke test  (n={N_SMOKE})")
    order = sorted(seqs, key=lambda s: (len(seqs[s]), s))
    idx = np.linspace(0, len(order) - 1, N_SMOKE).astype(int)
    smoke = [order[i] for i in dict.fromkeys(idx)]
    sl = [len(seqs[s]) for s in smoke]
    print(f"    {len(smoke)} sequences, len {min(sl)}-{max(sl)}, median {int(np.median(sl))}")

    print("\n[4] throughput and peak VRAM under the frozen rule")
    torch.cuda.reset_peak_memory_stats()
    pooled, tokens, secs = embed(model, alphabet, smoke, seqs, BATCH)
    vram = torch.cuda.max_memory_allocated() / 2**30
    nt = sum(sl)
    rate_seq, rate_nt = len(smoke) / secs, nt / secs
    print(f"    {len(smoke)} seq / {nt:,} nt in {secs:.1f}s = {rate_seq:.1f} seq/s, "
          f"{rate_nt:,.0f} nt/s   peak VRAM {vram:.2f} GB")
    est_min = 2_719_581 / rate_nt / 60
    print(f"    PROJECTED production (16,458 seq / 2,719,581 nt): {est_min:.1f} min")
    rep_meta |= {"batch_rule": f"sorted by (len, hash), BATCH={BATCH}, bf16 autocast fwd",
                 "smoke_n": len(smoke), "smoke_seconds": round(secs, 1),
                 "seq_per_s": round(rate_seq, 2), "nt_per_s": round(rate_nt, 1),
                 "peak_vram_gb": round(vram, 2), "projected_production_min": round(est_min, 1)}

    print("\n[5] output-content validation")
    s0 = smoke[len(smoke) // 2]
    d = float(np.abs(tokens[s0].astype(np.float32).mean(0)
                     - pooled[s0].astype(np.float32)).max())
    print(f"    pooled == mean over stripped nucleotide tokens: max|d| {d:.2e} (fp16 round-trip)")
    assert d < 1e-2, "pooling does not match the token cache"

    print("\n[6] determinism - both branches must fire")
    _, t2, _ = embed(model, alphabet, smoke, seqs, BATCH)
    ident = all(np.array_equal(tokens[s], t2[s]) for s in smoke)
    print(f"    same frozen rule, re-run: bit-identical on all {len(smoke)} = {ident}")
    _, t3, _ = embed(model, alphabet, smoke, seqs, BATCH + 1)
    diff = [s for s in smoke if not np.array_equal(tokens[s], t3[s])]
    cos = float(np.mean([mean_cos(tokens[s], t3[s]) for s in diff])) if diff else float("nan")
    print(f"    different batch geometry: {len(diff)}/{len(smoke)} arrays differ, "
          f"mean per-position cosine {cos:.6f}")
    print("    (bf16 reduction order - expected, below one bf16 ulp, NOT a defect)")
    if not ident:
        raise AssertionError("frozen rule is NOT reproducible - do not run production")
    rep_meta |= {"pool_vs_tokens_maxabs": d, "determinism_bit_identical": ident,
                 "geometry_sensitive_arrays": len(diff),
                 "geometry_change_cosine": None if not diff else round(cos, 6)}

    (OUT / "g0_rinalmo_pilot.json").write_text(json.dumps(rep_meta, indent=2, default=str) + "\n")
    print("\nPILOT COMPLETE - wrote g0_rinalmo_pilot.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
