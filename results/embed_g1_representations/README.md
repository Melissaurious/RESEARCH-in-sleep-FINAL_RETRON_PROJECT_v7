# embed_g1_representations

**Gate weight: LIGHT.** It produces the frozen representation caches and proves they are
complete and internally consistent. It settles no scientific claim.

Track `embed` — `launchers/LAUNCHER_03_rt_ncrna_embedding_compatibility.md`. Landed 2026-09-18.
Executed on **Ibex**, per operator decision, so as not to compete with the active `rt07_g6`
work on borg.

---

## What exists now

| cache | sequences | units | dim | shards | size | GPU |
|---|---|---|---|---|---|---|
| `esmc300m_v1` | **29,192 / 29,192** | **11,236,474 / 11,236,474** residues | 960 | 8 | 21 GB | A100-SXM4-80GB |
| `rinalmo_giga_v1` | **16,458 / 16,458** | **2,719,581 / 2,719,581** nt | 1280 | 5 | 6.6 GB | A100-SXM4-80GB |

Persistent home:
`/ibex/project/c2366/RETRONS/FINAL_RETRON_PROJECT_v7/embeddings/`
Inputs and every landed shard file are mode `444`. Transient work went to node-local scratch
(`$TMPDIR`, probed inside the job, 741 GiB free) and was copied in only after validating.

Both caches carry pooled **and** per-token representations, keyed by exact sequence hash.
Token files stay per-shard; `manifests/<cache>_tokens_index.tsv` gives `(shard, offset,
length)`. Concatenating 21 GB into one array would double storage and IO for no gain.

## What `merge_shards.py` actually verified

Each of these can fail, and each was checked:

1. every shard of the frozen sharding rule present — 8 / 8 and 5 / 5;
2. every file matching the sha256 its own `DONE.json` recorded;
3. the union of shard members being **exactly** the universe — no missing hash, no extra hash,
   no hash claimed by two shards;
4. each shard being the **contiguous block of the frozen (len, hash) order** its position
   implies, so a shard cannot hold the right *count* of wrong sequences;
5. summed sequences and units equalling the declared totals — both exact;
6. pooled and token array shapes agreeing with the indices;
7. every shard declaring an **identical frozen contract** — a cache built from two contracts
   is not one cache.

## The frozen contract, as recorded

| field | `esmc300m_v1` | `rinalmo_giga_v1` |
|---|---|---|
| model / id | ESM-C 300M / `esmc_300m` | RiNALMo giga-v1 / `giga-v1` |
| weights | HF `EvolutionaryScale/esmc-300m-2024-12` | `giga-v1.pt` sha256 `cd93c3f2…` |
| package | esm 3.2.0 | rinalmo (git install) |
| torch | 2.5.1+cu121 | 2.1.0 |
| **gpu_arch** | **sm_80** | **sm_80** |
| dim / dtype | 960 / float16 | 1280 / float16 |
| layer | final encoder output | final encoder output |
| pooling | unweighted mean over real tokens, fp32 accumulate | same |
| special tokens | BOS/EOS stripped, rows 1..L | CLS/EOS stripped, rows 1..L |
| orientation | n/a — protein | `sequence_oriented` as stored; all placements orientation-corrected |
| alphabet | as stored | DNA as stored; `encode()` aliases U→T; IUPAC native; no `<unk>` |
| batching | sorted by (len, hash); BATCH=8; solo if len>1024; shard boundaries ×8 | same, no solo path |
| truncation | **none** | **none** |
| input sha256 | `db87de17…` | `d04297a8…` |

`gpu_arch` is a **contract** field, not a note. Compute capability decides kernel selection and
reduction order, so a cache half-produced on sm_80 and half on sm_89 is two computations
wearing one name — and for ESM-C nothing else would have caught it, since Ibex and borg run
the same torch 2.5.1 and every other field matches.

## Measured throughput, and why the hardware mattered

`tables/g1_hardware_comparison.tsv`.

| model | RTX 4090 sm_89 | GTX 1080 Ti sm_61 | A100 sm_80 |
|---|---|---|---|
| ESM-C | 69,900 res/s | 4,412 res/s | 48,667 res/s |
| RiNALMo | 25,634 nt/s | **FAILED — no bf16** | 19,775 nt/s |

The first Ibex submission was routed to a 1080 Ti. ESM-C ran and validated there, 16× slower.
RiNALMo died: `Current CUDA Device does not support bfloat16`. Its frozen contract is a bf16
autocast forward, so dropping to fp16 to fit Pascal would have produced a cache that is not
the declared computation. **A100 is the only bf16-capable GPU on the cluster** (a100 252,
v100 265, p100 20, p6000 4, plus 1080 Ti / 2080 Ti — only a100 is Ampere). `embed_shard.py`
now refuses a non-bf16 GPU before running a single forward.

## Resource request, sized from measurement

Requested `--mem=32G`; worst observed host RSS **9.76 GB** (ESM-C shard 6, the longest
sequences). My pre-run estimate was ~14 GB, so the request carried ~3.3× headroom against
actual and could drop to 16G. Peak VRAM never exceeded **1.56 GB** (ESM-C) / **3.86 GB**
(RiNALMo) on an 80 GB card — GPU memory was never the constraint. Requested 1:00:00 per task;
longest task ran **1:20**.

## Resume

Shards are contiguous blocks with boundaries at multiples of `BATCH=8`, so shard-local batch
geometry equals a single-stream run. A shard present and validating against its `DONE.json` is
skipped. **Re-submitting the array is the resume**; no validated shard is ever recomputed.

## A defect found here, and it was in the verifier

The first verification run reported
`FAIL: shard_0000 tokens (736483, 960) != (8386560, 960)`.
The data was correct; `merge_shards.py` summed `pooled_index.tsv` column `row` instead of
`seq_len`, giving n(n−1)/2 = 8,386,560 for a 4,096-sequence shard — a plausible-looking number
with nothing to do with the data. Fixed, re-run, both caches verified. Recorded because a
verifier that fails loudly on good data is one bug away from passing quietly on bad data.

## Reproducing

```bash
sbatch code/prod_esmc.sbatch        # array 0-7, a100, ~1 min/shard
sbatch code/prod_rinalmo.sbatch     # array 0-4, a100, ~1 min/shard
python code/merge_shards.py --base <namespace> --cache esmc300m_v1
python code/merge_shards.py --base <namespace> --cache rinalmo_giga_v1
```

`code/fallback_borg.sh` runs the same producer on borg's 4090s. It **refuses to start** if any
shard of the target cache already exists on Ibex, because that would mix sm_80 and sm_89
within one cache. It was not used.

## What this gate does NOT establish

No pairing signal, no compatibility, no association. Only that representations exist for the
declared universe, are complete, are keyed by exact sequence hash, and carry a single frozen
contract. Token-level arrays are produced but **not analysed** — that stays `DEFER` in the
launcher until msr/msd/a1/a2 and RT-domain annotations are independently established.
