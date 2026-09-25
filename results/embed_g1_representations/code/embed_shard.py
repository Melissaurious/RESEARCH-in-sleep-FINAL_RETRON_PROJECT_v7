#!/usr/bin/env python
"""embed_g1/embed_shard.py - one shard of the frozen representation cache. Ibex GPU.

Carries the embed_g0 frozen contract unchanged:

  FROZEN ORDER       sorted by (seq_len, seq_hash)  - total, no ties
  FROZEN BATCHING    consecutive runs of BATCH; a sequence longer than SOLO_LEN goes alone
  SHARD BOUNDARIES   ALWAYS a multiple of BATCH, so shard-local batch geometry is IDENTICAL
                     to what a single-stream run would produce. This is what makes a sharded
                     run and a one-process run the same computation, and what makes any one
                     shard re-runnable in isolation.
  ESM-C              fp32 forward, strip BOS/EOS -> rows 1..L
  RiNALMo            bf16 autocast, strip CLS/EOS -> rows 1..L; DNA as stored (the alphabet is
                     T-based and encode() aliases U to T, so no T->U rewrite); IUPAC codes are
                     native to the vocabulary, so no substitution and no <unk> path
  ON DISK            fp16; pooled (N, D); tokens ragged (sum_L, D) + an offset index

NO pyarrow / pandas: the Ibex retron_esmc env does not carry them. TSV and .npy only.

TRANSIENT WORK GOES TO NODE-LOCAL SCRATCH, never to /ibex/project. The scratch path is
PROBED, not assumed - if the scheduler gives us nothing usable we say so and fall back
loudly. A shard is copied into the project area only after it validates, and a shard that is
already present and validates is NEVER recomputed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

BATCH = 8
SOLO_LEN = 1024          # ESM-C only; no ncRNA approaches it
CTX_DECLARED = 2048      # above this an RT is reported LEN_EXTRAPOLATED, never silently pooled
DIMS = {"esmc": 960, "rinalmo": 1280}


# ---------------------------------------------------------------- scratch

def node_local_scratch(job_tag: str) -> tuple[Path, str]:
    """Probe for node-local temporary space. Returns (path, how_we_got_it).

    Order: SLURM's own TMPDIR, then the TmpFS the cluster advertises (/local/scratch), then
    /tmp. Each candidate is tested by actually creating and writing a file - an advertised
    path that is not writable inside the job is not scratch.
    """
    cands = []
    if os.environ.get("TMPDIR"):
        cands.append((Path(os.environ["TMPDIR"]), "$TMPDIR (set by SLURM)"))
    jid = os.environ.get("SLURM_JOB_ID", "nojob")
    cands.append((Path("/local/scratch") / jid, "/local/scratch/$SLURM_JOB_ID (cluster TmpFS)"))
    cands.append((Path("/local/scratch"), "/local/scratch (cluster TmpFS, unscoped)"))
    cands.append((Path("/tmp"), "/tmp (last resort)"))
    for base, how in cands:
        try:
            d = base / f"embed_{job_tag}"
            d.mkdir(parents=True, exist_ok=True)
            p = d / ".wtest"
            p.write_text("x")
            p.unlink()
            free = shutil.disk_usage(d).free / 2**30
            return d, f"{how} -> {d} ({free:.0f} GiB free)"
        except Exception:
            continue
    raise SystemExit("no writable node-local scratch found; refusing to stage through /ibex/project")


# ---------------------------------------------------------------- io

def read_fasta(p: Path) -> dict[str, str]:
    seqs, sid, buf = {}, None, []
    with p.open() as fh:
        for line in fh:
            if line.startswith(">"):
                if sid:
                    seqs[sid] = "".join(buf)
                sid, buf = line[1:].split()[0], []
            else:
                buf.append(line.strip())
    if sid:
        seqs[sid] = "".join(buf)
    return seqs


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def frozen_order(seqs: dict[str, str]) -> list[str]:
    return sorted(seqs, key=lambda s: (len(seqs[s]), s))


def smoke_ids(order: list[str], n: int) -> list[str]:
    """The SAME length-stratified rule the embed_g0 local pilot used - never the file head."""
    idx = np.linspace(0, len(order) - 1, n).astype(int)
    return [order[i] for i in dict.fromkeys(idx)]


def batches(ids: list[str], seqs: dict[str, str], model: str) -> list[list[str]]:
    out, cur = [], []
    for s in ids:
        if model == "esmc" and len(seqs[s]) > SOLO_LEN:
            if cur:
                out.append(cur); cur = []
            out.append([s]); continue
        cur.append(s)
        if len(cur) == BATCH:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- models

def load_model(model: str):
    if model == "esmc":
        from esm.models.esmc import ESMC
        m = ESMC.from_pretrained("esmc_300m").eval().cuda()
        return m, None
    from rinalmo.pretrained import get_pretrained_model
    m, alphabet = get_pretrained_model(model_name="giga-v1")
    return m.to(device="cuda").eval(), alphabet


def forward(model, alphabet, chunk: list[str], seqs: dict[str, str], kind: str):
    if kind == "esmc":
        toks = model._tokenize([seqs[s] for s in chunk])
        with torch.no_grad():
            return model(toks.cuda()).embeddings
    toks = torch.tensor(alphabet.batch_tokenize([seqs[s] for s in chunk])).cuda()
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        return model(toks)["representation"]


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", required=True, choices=["esmc", "rinalmo"])
    ap.add_argument("--fasta", type=Path, required=True)
    ap.add_argument("--project", type=Path, required=True, help="persistent shard root")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shard-size", type=int, default=4096,
                    help="MUST be a multiple of BATCH; asserted below")
    ap.add_argument("--smoke", type=int, default=0,
                    help="run the declared length-stratified sample of N instead of a shard")
    ap.add_argument("--determinism", action="store_true",
                    help="re-run the shard under the frozen rule and require bit-identity")
    a = ap.parse_args()

    if a.shard_size % BATCH:
        raise SystemExit(f"--shard-size {a.shard_size} is not a multiple of BATCH={BATCH}; "
                         "shard-local batch geometry would not match a single-stream run")

    D = DIMS[a.model]
    tag = f"{a.model}_{'smoke' if a.smoke else f'{a.shard:04d}'}"
    t_start = time.perf_counter()
    print(f"[host] {socket.gethostname()}  job {os.environ.get('SLURM_JOB_ID','-')}  "
          f"gpu {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'}",
          flush=True)
    if not torch.cuda.is_available():
        raise SystemExit("no CUDA device visible")

    # ---- hardware capability, checked BEFORE any work ---------------------------------
    # A first Ibex smoke run was routed to a GTX 1080 Ti (Pascal). RiNALMo's frozen contract
    # is a bf16 autocast forward, and Pascal/Volta have no bf16, so the job died mid-batch
    # with "Current CUDA Device does not support bfloat16". The fix is NOT to drop to fp16 -
    # that would silently change the numerics the whole cache is defined by. The fix is to
    # refuse the node, loudly, before a single forward runs.
    gpu_name = torch.cuda.get_device_name(0)
    cap = torch.cuda.get_device_capability(0)
    if a.model == "rinalmo" and not torch.cuda.is_bf16_supported():
        raise SystemExit(
            f"REFUSING: {gpu_name} (sm_{cap[0]}{cap[1]}) has no bfloat16. RiNALMo's frozen "
            f"contract is a bf16 autocast forward; running fp16 here would produce a cache "
            f"that is not the declared computation. Request an Ampere-or-newer GPU "
            f"(--gres=gpu:a100:1).")
    print(f"[gpu] {gpu_name}  sm_{cap[0]}{cap[1]}  bf16={torch.cuda.is_bf16_supported()}",
          flush=True)

    scratch, how = node_local_scratch(tag)
    print(f"[scratch] {how}", flush=True)

    seqs = read_fasta(a.fasta)
    order = frozen_order(seqs)
    if a.smoke:
        # the smoke record is tagged with the GPU, because a smoke result IS a statement about
        # a piece of hardware and two different cards must not overwrite each other's numbers
        gtag = gpu_name.split()[-1].replace("-", "").lower()
        ids, shard_name = smoke_ids(order, a.smoke), f"smoke_{a.smoke}_{gtag}"
    else:
        lo, hi = a.shard * a.shard_size, min((a.shard + 1) * a.shard_size, len(order))
        if lo >= len(order):
            print(f"[skip] shard {a.shard} is past the end ({len(order)} sequences)")
            return 0
        ids, shard_name = order[lo:hi], f"shard_{a.shard:04d}"
    print(f"[work] {shard_name}: {len(ids):,} sequences, "
          f"{sum(len(seqs[s]) for s in ids):,} residues/nt", flush=True)

    dest = a.project / shard_name
    done = dest / "DONE.json"
    if done.is_file():
        try:
            rec = json.loads(done.read_text())
            ok = all(sha256_file(dest / f) == h for f, h in rec["sha256"].items())
            if ok and rec["n"] == len(ids):
                print(f"[skip] {shard_name} already present and validates - not recomputed")
                return 0
            print(f"[warn] {shard_name} present but does NOT validate; recomputing")
        except Exception as e:
            print(f"[warn] {shard_name} DONE unreadable ({e}); recomputing")

    model, alphabet = load_model(a.model)
    torch.cuda.reset_peak_memory_stats()

    pooled = np.zeros((len(ids), D), dtype=np.float16)
    tok_parts: list[np.ndarray] = []
    rows, off = [], 0
    pos = {s: i for i, s in enumerate(ids)}
    t0 = time.perf_counter()
    for chunk in batches(ids, seqs, a.model):
        E = forward(model, alphabet, chunk, seqs, a.model)
        for k, s in enumerate(chunk):
            L = len(seqs[s])
            arr = E[k, 1:L + 1]
            if tuple(arr.shape) != (L, D):
                raise AssertionError(f"{s}: {tuple(arr.shape)} != {(L, D)}")
            t = arr.float().cpu().numpy().astype(np.float16)
            if not np.isfinite(t).all():
                raise AssertionError(f"{s}: non-finite")
            if not t.any():
                raise AssertionError(f"{s}: all-zero")
            pooled[pos[s]] = t.astype(np.float32).mean(0).astype(np.float16)
            tok_parts.append(t)
            rows.append((s, L, off))
            off += L
    secs = time.perf_counter() - t0
    tokens = np.concatenate(tok_parts, axis=0)
    assert tokens.shape == (off, D), f"{tokens.shape} != {(off, D)}"

    peak_vram = torch.cuda.max_memory_allocated() / 2**30
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20

    if a.determinism:
        p2 = np.zeros_like(pooled)
        for chunk in batches(ids, seqs, a.model):
            E = forward(model, alphabet, chunk, seqs, a.model)
            for k, s in enumerate(chunk):
                L = len(seqs[s])
                p2[pos[s]] = (E[k, 1:L + 1].float().cpu().numpy()
                              .astype(np.float16).astype(np.float32).mean(0).astype(np.float16))
        ident = bool(np.array_equal(pooled, p2))
        print(f"[determinism] frozen rule re-run bit-identical: {ident}")
        if not ident:
            raise AssertionError("frozen rule not reproducible on this node - do not run production")

    # ---- write to NODE-LOCAL scratch, validate, then copy in --------------------------
    work = scratch / shard_name
    work.mkdir(parents=True, exist_ok=True)
    np.save(work / "pooled.npy", pooled)
    np.save(work / "tokens.npy", tokens)
    (work / "pooled_index.tsv").write_text(
        "seq_hash\trow\tseq_len\n"
        + "".join(f"{s}\t{i}\t{len(seqs[s])}\n" for i, s in enumerate(ids)))
    (work / "tokens_index.tsv").write_text(
        "seq_hash\toffset\tlength\n" + "".join(f"{s}\t{o}\t{L}\n" for s, L, o in rows))

    lens = np.array([len(seqs[s]) for s in ids])
    prov = {
        "shard": shard_name, "n": len(ids), "dim": D, "dtype": "float16",
        "model": {"esmc": "ESM-C 300M", "rinalmo": "RiNALMo giga-v1"}[a.model],
        "model_id": "esmc_300m" if a.model == "esmc" else "giga-v1",
        "weights_identity": ("HF EvolutionaryScale/esmc-300m-2024-12" if a.model == "esmc"
                             else "~/.cache/rinalmo_pretrained/giga-v1.pt "
                                  "sha256 cd93c3f21eb3e767373c9491192686b5846247bd1110693e453c1dd0f321c0db"),
        "package_version": (f"esm {__import__('importlib.metadata', fromlist=['x']).version('esm')}"
                            if a.model == "esmc" else "rinalmo (git install)"),
        "torch": torch.__version__, "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0),
        # gpu_arch is part of the FROZEN CONTRACT, not just a note. Compute capability is what
        # actually decides kernel selection and reduction order, so a cache whose shards span
        # sm_80 (A100) and sm_89 (RTX 4090) is not one computation. It is the arch and not the
        # device NAME because A100-40GB and A100-80GB are both sm_80 and are interchangeable
        # here, while a 4090 is not. merge_shards.py refuses a cache that mixes them.
        "gpu_arch": f"sm_{cap[0]}{cap[1]}",
        "bf16_supported": bool(torch.cuda.is_bf16_supported()),
        "layer": "final encoder output (the model's returned representation)",
        "pooling": "unweighted mean over real residue/nucleotide tokens, fp32 accumulate",
        "special_tokens": ("BOS/EOS stripped, rows 1..L" if a.model == "esmc"
                           else "CLS/EOS stripped, rows 1..L"),
        "orientation_rule": ("n/a - protein" if a.model == "esmc"
                             else "sequence_oriented as stored; all placements orientation_corrected"),
        "alphabet_rule": ("as stored" if a.model == "esmc"
                          else "DNA as stored; encode() aliases U->T; IUPAC native; no <unk>"),
        "batching_rule": f"sorted by (len, hash); BATCH={BATCH}"
                         + (f"; solo if len>{SOLO_LEN}" if a.model == "esmc" else "")
                         + f"; shard boundaries at multiples of {BATCH}",
        "shard_size": a.shard_size,
        "truncation": "none",
        "len_extrapolated": int((lens > CTX_DECLARED).sum()) if a.model == "esmc" else 0,
        "len_extrapolated_rule": f"len > {CTX_DECLARED} -> LEN_EXTRAPOLATED, reported separately",
        "producer": "embed_g1/embed_shard.py",
        "producer_sha256": sha256_file(Path(__file__)),
        "input_fasta": str(a.fasta), "input_fasta_sha256": sha256_file(a.fasta),
        "host": socket.gethostname(), "slurm_job": os.environ.get("SLURM_JOB_ID", ""),
        "seconds": round(secs, 2),
        "seq_per_s": round(len(ids) / secs, 2), "units_per_s": round(int(lens.sum()) / secs, 1),
        "peak_vram_gb": round(peak_vram, 2), "peak_host_rss_gb": round(peak_rss, 2),
        "len_min": int(lens.min()), "len_max": int(lens.max()), "len_total": int(lens.sum()),
        "scratch": how,
    }
    (work / "PROVENANCE.json").write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")

    files = ["pooled.npy", "tokens.npy", "pooled_index.tsv", "tokens_index.tsv", "PROVENANCE.json"]
    rec = {"shard": shard_name, "n": len(ids), "dim": D,
           "sha256": {f: sha256_file(work / f) for f in files}}

    # validate on READ, from the files we just wrote, before anything is copied
    pv = np.load(work / "pooled.npy", mmap_mode="r")
    tv = np.load(work / "tokens.npy", mmap_mode="r")
    assert pv.shape == (len(ids), D) and pv.dtype == np.float16, f"pooled {pv.shape} {pv.dtype}"
    assert tv.shape == (off, D) and tv.dtype == np.float16, f"tokens {tv.shape} {tv.dtype}"
    s_mid = ids[len(ids) // 2]
    o, L = next((o, L) for s, L, o in rows if s == s_mid)
    d = float(np.abs(np.asarray(tv[o:o + L], dtype=np.float32).mean(0)
                     - np.asarray(pv[pos[s_mid]], dtype=np.float32)).max())
    assert d < 1e-2, f"pooled does not match tokens for {s_mid}: {d}"
    print(f"[validate] pooled=={pv.shape} tokens=={tv.shape} pool-vs-token max|d| {d:.2e}")

    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(work / f, dest / f)
    for f in files:
        if sha256_file(dest / f) != rec["sha256"][f]:
            raise AssertionError(f"copy into the project area corrupted {f}")
        os.chmod(dest / f, 0o444)                       # write-once discipline
    done.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    os.chmod(done, 0o444)
    shutil.rmtree(work, ignore_errors=True)

    print(f"[done] {shard_name}  {len(ids):,} seq  {secs:.1f}s  "
          f"{prov['units_per_s']:,.0f} units/s  VRAM {peak_vram:.2f} GB  "
          f"RSS {peak_rss:.2f} GB  total {time.perf_counter()-t_start:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
