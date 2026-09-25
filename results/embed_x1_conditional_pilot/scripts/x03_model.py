#!/usr/bin/env python
"""embed_x1/x03 - the conditional ncRNA decoder. ADAPTED, not reimplemented.

REUSE DECISION, recorded before training (PREREG section 0). The vendored Profluent
`grna-modeling` release ships the architecture this pilot needs. Its `model/transformer.py` is
SELF-CONTAINED - it imports only math/typing/torch/einops - and provides `EncoderLayer`
(bidirectional) and `CrossDecoderLayer` (causal self-attention + cross-attention to a
conditioning representation). Those are imported READ-ONLY from the vendored tree at a pinned
sha256; nothing is copied into this repository and nothing in that tree is modified.

What is NOT reused: `model/gRNAModel.py`, whose batch plumbing imports the unpublished
`profluent.*` namespace and `Bio`, and needs a namespace shim to load at all. Its
`ProteinBatch`/`NucleicAcidBatch` types carry structure this pilot does not use. Re-deriving a
~40-line dataset/collate path is cheaper and clearer than shimming a partially-broken tree
across project boundaries.

THE THREE ARMS SHARE ONE DECODER. `U`, `T` and `R` instantiate the identical conditioning
encoder, decoder stack and LM head with identical hyperparameters. They differ only in what
produces the conditioning tensor:
    U  a single learned constant vector                    (no protein, no type)
    T  a learned embedding of the retron-type label        (21 types)
    R  the frozen ESM-C RT chunk array, linearly projected (the primary model)
So a difference between arms is attributable to the conditioning signal, not to decoder
capacity. Parameter counts are reported per arm and differ only in the conditioning input path.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import torch
import torch.nn as nn

VENDOR = Path("/home/borg/openCRISPR_for_retrons/src/grna-modeling/grna_modeling/model")
VENDOR_SHA = "c1f2112b4b91e8424b173d49da43e7ff14fc1ec0bf39ddc0e419147a2b90af3f"


def _load_vendor():
    got = hashlib.sha256((VENDOR / "transformer.py").read_bytes()).hexdigest()
    if got != VENDOR_SHA:
        raise SystemExit(f"vendored transformer.py changed: {got} != {VENDOR_SHA}")
    sys.path.insert(0, str(VENDOR))
    import transformer as T  # noqa: E402
    return T


T = _load_vendor()

VOCAB_SIZE = 11
PAD, BOS, EOS = 0, 1, 2


class CondNcRNADecoder(nn.Module):
    """Frozen-conditioning -> lightweight encoder -> causal cross-attending RNA decoder."""

    def __init__(self, arm: str, d_s=128, n_heads=8, n_enc=1, n_dec=3,
                 dropout=0.1, d_rt=960, n_types=21, k_chunks=32):
        # d_hidden is the PER-HEAD dimension in this layer library, and the released model sets
        # it to d_s // n_heads (gRNAModel.__init__). Passing a feed-forward-sized value here
        # inflates every projection to d_hidden*n_heads and blows the parameter budget by ~10x.
        d_hidden = d_s // n_heads
        super().__init__()
        assert arm in ("U", "T", "R")
        self.arm, self.d_s, self.k_chunks = arm, d_s, k_chunks

        # ---- conditioning input path: the ONLY place the arms differ -------------------
        if arm == "U":
            self.cond_const = nn.Parameter(torch.zeros(1, 1, d_s))
            nn.init.normal_(self.cond_const, std=0.02)
        elif arm == "T":
            self.cond_type = nn.Embedding(n_types, d_s)
            nn.init.normal_(self.cond_type.weight, std=0.02)
        else:
            self.cond_proj = nn.Linear(d_rt, d_s)

        # ---- everything below is IDENTICAL across arms ---------------------------------
        self.enc_layers = nn.ModuleList(
            [T.EncoderLayer(d_s=d_s, d_hidden=d_hidden, n_heads=n_heads,
                            dropout_rate=dropout) for _ in range(n_enc)])
        self.rna_embed = nn.Embedding(VOCAB_SIZE, d_s)
        self.dec_layers = nn.ModuleList(
            [T.CrossDecoderLayer(d_s_self=d_s, d_s_cross=d_s, d_hidden=d_hidden,
                                 n_heads=n_heads, dropout_rate=dropout,
                                 use_self_rope=True)   # as in the released decoder
             for _ in range(n_dec)])
        self.norm = nn.LayerNorm(d_s)
        self.lm_head = nn.Linear(d_s, VOCAB_SIZE)

    def conditioning(self, batch):
        """-> (B, L_cond, d_s), (B, L_cond) mask. Shapes are arm-specific, decoder is not."""
        if self.arm == "U":
            B = batch["tokens"].shape[0]
            s = self.cond_const.expand(B, 1, self.d_s)
            m = torch.ones(B, 1, dtype=torch.int32, device=s.device)
        elif self.arm == "T":
            s = self.cond_type(batch["type_id"]).unsqueeze(1)
            m = torch.ones(s.shape[0], 1, dtype=torch.int32, device=s.device)
        else:
            s = self.cond_proj(batch["rt_chunks"])
            m = batch["rt_mask"].int()
        return s, m

    def forward(self, batch):
        tokens = batch["tokens"]                       # (B, L) int64, <bos>..<eos>, pad 0
        cond, cond_mask = self.conditioning(batch)
        for layer in self.enc_layers:
            cond = layer(cond, cond_mask)

        inp = tokens[:, :-1]
        tgt = tokens[:, 1:]
        s = self.rna_embed(inp)
        rna_mask = (inp != PAD).int()
        for layer in self.dec_layers:
            s = layer(s, cond, rna_mask, cond_mask)
        logits = self.lm_head(self.norm(s))            # (B, L-1, V)

        # loss is masked at pad; <bos> is an input only, never a target
        loss_mask = (tgt != PAD).float()
        ce = nn.functional.cross_entropy(
            logits.reshape(-1, VOCAB_SIZE).float(), tgt.reshape(-1),
            reduction="none").view(tgt.shape)
        per_seq_sum = (ce * loss_mask).sum(-1)
        per_seq_n = loss_mask.sum(-1)
        return dict(logits=logits, nll_sum=per_seq_sum, n_tok=per_seq_n,
                    nll_per_tok=per_seq_sum / per_seq_n.clamp(min=1))


def count_params(m: nn.Module) -> dict:
    tot = sum(p.numel() for p in m.parameters() if p.requires_grad)
    cond = sum(p.numel() for n, p in m.named_parameters()
               if n.startswith("cond") and p.requires_grad)
    return dict(total=tot, conditioning_path=cond, shared_decoder=tot - cond)


if __name__ == "__main__":
    print(f"vendored transformer.py sha256 verified: {VENDOR_SHA}")
    for arm in ("U", "T", "R"):
        m = CondNcRNADecoder(arm)
        c = count_params(m)
        print(f"  arm {arm}: total {c['total']:,}  "
              f"conditioning path {c['conditioning_path']:,}  "
              f"shared decoder {c['shared_decoder']:,}")
