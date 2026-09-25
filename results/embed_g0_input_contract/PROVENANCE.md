# PROVENANCE — embed_g0_input_contract

Landed 2026-09-18 from worktree
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings`, branch `embeddings-g0`,
parent commit `53ce532`. Scratch: `ARIS_OUTPUT/embed_g0_population_audit/` (gitignored).

## Environments

| role | interpreter | versions |
|---|---|---|
| CPU audit, extraction, components | `/home/borg/miniconda3/envs/retron_tradicional/bin/python` | pyarrow + pandas; **no duckdb in this env** — the workbench's DuckDB recipes were re-expressed in pyarrow/pandas |
| RT clustering | `/home/borg/miniconda3/envs/colabfold/bin/mmseqs` | mmseqs easy-cluster |
| ncRNA clustering | `/home/borg/miniconda3/envs/retron_tradicional/bin/cd-hit-est` | `-n 8 -aS 0.8` |
| ESM-C pilot | `/home/borg/miniconda3/envs/retron_esmc/bin/python` | torch 2.5.1+cu121, esm 3.2.0 |
| RiNALMo pilot | `/home/borg/miniconda3/envs/rinalmo/bin/python` | torch 2.7.1+cu118 |

GPU: NVIDIA GeForce RTX 4090, 24,564 MiB, driver 535.309.01. Two cards present, both idle at
launch. One card used.

## Weights

| model | identity |
|---|---|
| RiNALMo giga-v1 | `/home/borg/.cache/rinalmo_pretrained/giga-v1.pt`, 2,603,787,622 B. A 2,452,619,264 B `giga-v1.ptfm9r29kc.part` sits beside it — a partial download. It is not loaded |
| ESM-C 300M | HuggingFace `biohub/esmc-300m-2024-12`, resolved by `ESMC.from_pretrained("esmc_300m")` |

## Inputs

`INPUTS.tsv` carries the sha256 and byte count of the six canonical derived-layer parquet
inputs, read read-only from the **main** worktree's `data/derived/`.

The 18 raw corpus files are **not re-hashed here**. Their identity is pinned by
`results/dbchar_g1_corpus_identity/` (record-manifest sha256
`8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00`, 43 files,
81,007,695,609 B, 3,358,182 records, zero parse failures). Re-hashing 21 GB to restate an
existing pin would be duplication, not verification. The 16,458/16,458 sequence-hash
round-trip is the check that actually binds: it verifies the *content* extracted from those
files against a hash computed by a different gate, which a file digest would not do.

## Order of operations

1. `a01_universe.py` — reproduce the nine declared population counts; write the fetch plan.
2. `a02_ncrna_fasta.py` — stream the raw corpus at the addressed lines, recompute every
   sha256, require 16,458/16,458, write `data/derived/rt_ncrna_oriented_v1.*` + manifest +
   provenance. **32.2 s.**
3. `a03_rt_fasta.py` — project `rt_exact_v1` onto the universe; 29,192 sequences.
4. `a04_cluster.sh` — mmseqs at 0.30/0.50/0.70/0.90; cd-hit-est at 0.80/0.90/0.95/0.99.
5. `a05_components.py` — contract pairs onto clusters, union-find, component size
   distribution and maximum reachable held-out fraction per threshold combination.
6. `a06_pilot_esmc.py`, `a07_pilot_rinalmo.py` — the six gated pilot checks.
7. `a08_assemble.py` — this bundle; every artifact given a unit and a denominator.

## Deviations from the precedent scripts, and why

- **Dropped `.replace("T","U")`** (RiNALMo precedent `s14_embed_oriented.py`). RiNALMo's
  alphabet is T-based and `Alphabet.encode` aliases U to T, so the call is a no-op. Verified:
  `batch_tokenize(["ACGTU"])` maps both T and U to index 8.
- **Dropped the prior-cache strand check** (`COS_TOL`, `strand_check`). It compared against a
  prior unoriented cache that does not exist for this population — zero of 16,458 registered
  ncRNA hashes appear in any V4 oriented set. Replaced by the determinism pair: bit-identity
  under the frozen rule, difference under changed geometry.
- **Replaced `-len`-descending order** (ESM-C precedent `s4n_embed_esmc.py`) with the frozen
  `(len, hash)` ascending order plus a solo path above 1,024 aa, so the batching rule is
  total, deterministic and re-runnable.
- **Ragged concatenated token store** rather than one `.npy` per record (the V4 precedent's
  28,431 loose files). Deferred to `embed_g1`; not exercised in this gate.

## Known limits of this gate

- LIGHT. No claim, no figure, no paper number.
- The GPU pilots measure 200 length-stratified sequences per model, not the full population.
  The production estimate they yield is a *measured* extrapolation, not an observation.
- `rt_ncrna_oriented_v1.*` lives in this worktree's `data/derived/`, not the main worktree's.
  See the placement caveat in `docs/DATASET_REGISTRY.md` section 3b. Two derived layers exist
  until an operator makes the copy.
- `bash general/checks/specs_exist.sh` reports one **pre-existing** failure unrelated to this
  track: `docs/BLOCKED.md` line 79 names
  `proposed/research_contract_C3_C9_amendment.md` while recording that it was *withdrawn*, and
  the checker reads the prose mention as a file reference. Not introduced here, not repaired
  here.

## Reproducibility defects found by rerunning this bundle, and their fixes

Recorded because both were found by the bundle's own `run.sh`, not by inspection.

| defect | evidence | fix |
|---|---|---|
| `cd-hit-est -T 16` is not order-deterministic | rerun moved component counts by up to 3 in ~6,000; diffing intermediates showed mmseqs identical, cd-hit differing | `-T 1`; verified byte-identical over two independent runs at `-c 0.90` (8,570 clusters both times) |
| `provenance.json` carried `elapsed_s` | the file's sha256 changed every run, so `MANIFEST.tsv` could never re-verify | field removed; timing goes to stdout and the log |

Neither altered a scientific number, and **the dataset was never affected** —
`rt_ncrna_oriented_v1.fna` (`d04297a8…`) and `.parquet` (`5c81dfe9…`) were byte-identical
across every run, before and after both fixes.

Component counts under the `-T 16` runs differ slightly from the landed `-T 1` numbers at
`nc_id 0.80` and `0.95`. The landed table is the `-T 1` one. The `-T 16` numbers are not
retained as an alternative result; they were never reproducible.
