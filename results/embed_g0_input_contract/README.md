# embed_g0_input_contract

**Gate weight: LIGHT.** It fixes the input contract for the `embed` track. It settles no
scientific claim and no number here may enter one (WA-B.3).

Track: `embed` — `launchers/LAUNCHER_03_rt_ncrna_embedding_compatibility.md`.
Worktree `…-embeddings`, branch `embeddings-g0`. Landed 2026-09-18.

---

## What this gate fixes

1. **The population.** PAIR-ELIG — 30,924 exact pairs, 29,192 unique RT hashes, 16,458 unique
   oriented ncRNA hashes, from the registered `rt_ncrna_exact_pairs_v1.parquet`. T1/T2/T3/T4
   are pair-level views only.
2. **A registered canonical dataset** — `data/derived/rt_ncrna_oriented_v1.*`, the oriented
   ncRNA sequences, which did not previously exist in the derived layer.
3. **The frozen batching rule** for both encoders, demonstrated reproducible.
4. **The relatedness-graph component structure**, which is the evidence a split threshold is
   frozen against.

## The nine counts that must reproduce

`a01_universe.py` asserts, and will exit non-zero on, all of these:

| quantity | value |
|---|---|
| placements, all | 346,722 |
| placements, canonical | 344,154 |
| PAIR-ELIG pairs | 30,924 |
| PAIR-CANON pairs | 30,427 |
| T1 / T2 / T3 | 30,287 / 25,673 / 23,680 |
| unique RT hashes | 29,192 |
| unique ncRNA hashes | 16,458 |

They reproduce the `analysis/dbchar_rt_ncrna_workbench` tier table exactly. That agreement is
why the workbench's splitting-hazard analysis is relied on here; it is not itself authority.

`PAIR-ELIG \ T1 = 637` decomposes exactly as 497 de-duplication-removed pairs + 140
non-Retron-file-label canonical pairs, and `T1 \ PAIR-ELIG = 0` — the universe is a strict
superset of every tier.

## The load-bearing verification

**16,458 / 16,458 sha256 round-trip on the ncRNA sequences.** `dbchar_g2` defined
`nc_seq_hash = sha256(sequence_oriented.upper())` (`e01_extract.py:294`), so recomputing that
hash on every extracted sequence and requiring equality makes the FASTA self-verifying: it
cannot silently hold the wrong molecule, the wrong strand, or a sequence from the wrong
record. Zero mismatches, zero unrecovered.

## What the pilots established

| | ESM-C 300M | RiNALMo giga-v1 |
|---|---|---|
| params | 332,997,184 | 650,901,793 |
| dim | 960 | 1280 |
| token geometry | `(B, L+2, 960)`, BOS/EOS stripped | `(B, L+2, 1280)`, CLS/EOS stripped |
| positional scheme | rotary — **no learned position table** | — |
| truncation | **none**; longest 2,860 aa forwards finite at 0.97 GB | **none**; max length 395 nt |
| throughput | 69,900 res/s | 25,634 nt/s |
| peak VRAM | 1.20 GB | 3.84 GB |
| projected production | 2.7 min | 1.8 min |
| pooled == mean of tokens | max\|d\| 4.83e-4 | max\|d\| 8.82e-4 |
| frozen rule re-run | **bit-identical**, 200/200 | **bit-identical**, 200/200 |
| changed batch geometry | 92/200 differ, cosine 0.999779 | 193/200 differ, cosine 0.999985 |

Both determinism branches fire, so the check is not vacuous. Arrays are never compared by
maximum absolute difference — that statistic is a length correlate, not a measure of sameness.

## Two traps defused before production, not after

1. **`.replace("T","U")` in the RiNALMo precedent is a no-op.** The alphabet is T-based and
   `Alphabet.encode` aliases U to T internally. Removed rather than carried.
2. **The ncRNA alphabet carries IUPAC ambiguity** — `ACGKNRTY`, 214 sequences (1.30 %), 4,117
   nt (0.151 %), almost all `N`. RiNALMo's vocabulary covers R/Y/K/M/S/W/B/D/H/V/N natively,
   so nothing maps to `<unk>` and no substitution is applied.

## The split-feasibility finding

`tables/g0_component_structure.tsv`, all 16 threshold combinations. Contracting the 30,924
pairs onto clustered RTs and clustered ncRNAs and taking connected components:

| RT id | ncRNA id | components | giant | giant share | max held-out |
|---|---|---|---|---|---|
| 0.30 | 0.80 | 156 | 27,572 | 89.2 % | 10.8 % |
| 0.30 | 0.99 | 278 | 20,894 | 67.6 % | 17.1 % |
| **0.50** | **0.90** | **1,242** | **5,561** | **18.0 %** | **19.8 %** |
| 0.70 | 0.90 | 5,859 | 822 | 2.7 % | 20.0 % |
| 0.90 | 0.99 | 10,539 | 783 | 2.5 % | 20.0 % |

- **RT 0.30 is infeasible.** A giant component holds 68–89 % of the pairs at every ncRNA
  threshold. The proposed split cannot be built there.
- **RT 0.50 and above is feasible.** The giant falls to 17.4–18.5 % at RT 0.50 and to
  2.5–4.0 % at RT 0.70/0.90, and a full 20 % held-out fraction is reachable using whole
  components.
- The trade-off is visible and is the operator's to make: a **lower** RT threshold is a
  **stronger** independence guarantee between folds, and RT 0.30 — the strongest available —
  is exactly the one the graph will not support.

No threshold is chosen here. Freezing one is a human gate in the launcher's §9.

## Reproducibility — one defect found by rerunning, and fixed

The first rerun of this bundle did **not** reproduce: component counts moved by up to 3 in
~6,000. Diffing the intermediate cluster files across the two runs isolated the cause —
**mmseqs was identical; `cd-hit-est` differed.** Its multithreaded path is not
order-deterministic. Clustering now runs single-threaded, verified byte-identical over two
independent runs at 0.90 (8,570 clusters both times).

A second defect was found in the same pass: `rt_ncrna_oriented_v1.provenance.json` carried an
`elapsed_s` wall-clock field, so the file — and therefore its sha256 in the manifest — changed
on every run, silently breaking the byte-reproducibility contract the manifest exists to
assert. The field is removed; timing goes to the log. The **dataset itself was never
affected**: `rt_ncrna_oriented_v1.fna` and `.parquet` were byte-identical across all runs.

Neither defect changed a scientific number. Both are recorded because a split rule that cannot
be regenerated exactly is not a frozen split rule.

## Layout

```
scripts/   a01 population audit · a02 ncRNA reconstruction · a03 RT FASTA
           a04 clustering sweep · a05 components · a06/a07 GPU pilots · a08 assemble
tables/    18 artifacts; every one has a declared unit and denominator in MANIFEST.tsv
run.sh     end-to-end rerun (--with-gpu to include the pilots)
INPUTS.tsv derived-layer inputs hashed; the raw corpus cited by its dbchar_g1 pin
```

## Reproducing

```bash
bash results/embed_g0_input_contract/run.sh            # ~3 min, CPU
bash results/embed_g0_input_contract/run.sh --with-gpu # + ~2 min GPU
```

The rerun writes to `ARIS_OUTPUT/rerun-embed_g0_input_contract/`; diff its `tables/` against
this bundle's. It also rewrites `data/derived/rt_ncrna_oriented_v1.*` byte-identically and
verifies them against the landed manifest.

## What this gate does NOT establish

No pairing signal, no compatibility, no association, no co-evolution. It establishes only that
the inputs are what they are claimed to be and that the instruments are reproducible.
