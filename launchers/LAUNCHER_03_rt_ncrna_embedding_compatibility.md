# LAUNCHER — 03_rt_ncrna_embedding_compatibility

**Do naturally paired retron RT and ncRNA sequences contain cross-modal compatibility signal in
frozen pretrained sequence representations, beyond what is explained by sequence relatedness,
taxonomy and trivial dataset structure?**

Track id: `embed`. Written 2026-09-18. Worktree
`/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-embeddings`, branch `embeddings-g0`.
Runs parallel to the `rt07` track; it does not consume, block or modify it.

Three rules this launcher restates, with their ids:

- **WA-A.4** — measure and report; do not conclude. Interpretation lands as `PROPOSED:`.
- **WA-G.5** — a null or refuting measurement is a result and lands like any other.
- **WA-K.1** — size a job from a measured, length-stratified smoke test, never from a count.

---

## 1. Objective and success criterion

### The question

> **Do naturally paired retron RT and ncRNA sequences contain cross-modal compatibility signal
> in frozen pretrained sequence embeddings, beyond what can be explained by sequence
> relatedness, taxonomy and trivial dataset structure?**

The task is **not** "show that RT and ncRNA co-evolve". That phrasing presumes the answer and
also presumes an estimand — co-evolution — that nothing in this track can identify.

### Interpretation boundary — binding on every gate

A positive result here may support, at most:

> RT and ncRNA sequences carry pairing-compatible information beyond the tested nuisance
> structure.

It does **not** establish molecular binding, direct physical interaction, causal co-evolution,
residue–nucleotide contact, or RT0–RT7 / domain-level co-evolution. No gate may report a number
that implies any of those, and no figure may be captioned as if it did. Those require separate
evidence and separate tracks.

### Success criterion

The track succeeds when all of the following hold. Note that a **negative** result satisfies
every one of them.

1. the analysis population is the declared PAIR-ELIG universe, and every reported number names
   its unit and denominator;
2. a frozen representation cache exists for both modalities, keyed by canonical sequence hash,
   with the provenance record of §7c complete for every array, and reproducible under a frozen
   batching rule demonstrated by a bit-identity re-run;
3. the trivial-baseline ladder of §7d has been run **first**, and its numbers are reported
   beside every embedding number in the same table;
4. the confirmatory metric is read out once, on a leakage-free held-out split whose realized
   cross-split identity is measured and reported, not asserted;
5. the full negative/control ladder of §7e is reported — every rung, not the best rung;
6. all four amendments of §7f are honoured, each with a landed table.

## 2. Kill criteria

Stated now, before any number exists, because this is the only moment it is honest.

- **Trivial-baseline kill (operator amendment 4, binding).** If length, GC, k-mer-composition or
  the detection-model label-shortcut baseline **matches or exceeds** the frozen-embedding
  approach on the predeclared confirmatory metric within the declared tolerance, the track
  reports "no embedding-specific compatibility signal detected", and **does not** escalate to
  the contrastive gate to rescue a positive. Escalation to `embed_g3` requires the embedding
  approach to beat every trivial baseline on the held-out split, declared before the readout.
- **Label-shortcut kill.** If retrieval performance is fully accounted for by predicting the
  ncRNA covariance model from the RT alone, the finding is a retron-type classification result,
  not a pairing result, and is reported as such.
- **Split-impracticality kill.** If the frozen relatedness graph yields a giant component that
  leaves no held-out fraction large enough to read the confirmatory metric, the honest product
  is that finding, landed, plus a documented impossibility result for this population.
- **Rung-3 kill.** If signal survives rungs 1 and 2 but vanishes at rung 3 (covariance-model-
  matched mismatches), the result is reported as "explained by retron type", not as pairing
  compatibility.
- **Budget kill.** Compute exceeding 2× the measured pilot estimate stops for diagnosis rather
  than pushing through.

## 3. Non-goals — out of scope

This track does **not** become:

- a co-evolution, phylogenetic-congruence or covariation study;
- a structural, docking, contact-prediction or binding study;
- residue-to-nucleotide interpretation — per-token caches are produced now and **not analysed**
  until msr/msd/a1/a2 and RT-domain annotations are independently established elsewhere;
- an RT0–RT7 analysis of any kind; it consumes no `rt07` output and emits none;
- a retron classification, subtyping or discovery project;
- a model-training project — encoders stay frozen; only small projection heads may be learned,
  and only at `embed_g3`;
- a benchmark of RNA or protein language models against each other;
- a rewrite, re-derivation or reinterpretation of any landed Stage-1 or Stage-2 bundle.

Anything else a session believes is needed goes to `docs/BLOCKED.md` with a recommended
default, and is not built.

## 4. Inputs

| path | what it is | trust grade |
|---|---|---|
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_ncrna_exact_pairs_v1.parquet` | the registered eligible exact-pair resource; PAIR-ELIG, 30,924 pairs — the declared universe | `FROZEN:dbchar_g3` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_ncrna_pairs_v1.parquet` | placement grain; geometry, tier predicates, raw-corpus addresses | `FROZEN:dbchar_g3` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_ncrna_exact_pair_recurrence_v1.parquet` | the registered recurrence view — the only admissible recurrence source | `FROZEN:dbchar_g3` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_exact_v1.parquet` | exact RT proteins and sequences | `FROZEN:dbchar_g2` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/rt_family_baseline_v1.parquet` | family label, completeness class | `FROZEN:dbchar_g4` |
| `/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived/ncrna_family_baseline_v1.parquet` | per-ncRNA detection model and model multiplicity | `FROZEN:dbchar_g4` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/` | raw mining corpus; the only source of ncRNA sequence | `RAW` |
| `data/derived/rt_ncrna_oriented_v1.fna` and `.parquet` | oriented ncRNA sequences, produced by this track, hash-verified 16,458 of 16,458 | `FROZEN:embed_g0` |
| `/home/borg/.cache/rinalmo_pretrained/giga-v1.pt` | RiNALMo giga-v1 weights, 2.6 GB | `RAW` |
| `/home/borg/.cache/huggingface/hub/models--biohub--esmc-300m-2024-12` | ESM-C 300M weights | `RAW` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/.../s14_embed_oriented.py` | RiNALMo precedent script — tooling only | `RE-DERIVE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/.../s4n_embed_esmc.py` | ESM-C precedent script — tooling only | `RE-DERIVE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/ncrna_representation_probes/cache/emb_oriented/` | prior RiNALMo arrays; measured zero hash overlap with this universe | `DO-NOT-USE:different population, V4 median 556 nt vs 151 nt here` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/.../cache/E7/emb_esmc.npz` | prior ESM-C arrays; pooled only, positional ids, zero hash overlap | `DO-NOT-USE:different population and key space` |

⛔ Read-only, always. An ungraded input is `DO-NOT-USE` (WA-L.3). Every schema statement above
was probed against real values, not read from a document (WA-D.4).

**Canonical placement caveat.** The canonical derived layer lives in the main worktree and is
read-only from this track's sandbox. `rt_ncrna_oriented_v1.*` is therefore built at this
worktree's `data/derived/`. Promoting it into the main worktree's `data/derived/` is a
copy of four byte-identical files verified against `rt_ncrna_oriented_v1.MANIFEST.tsv`; it is
an operator step, recorded in `docs/DATASET_REGISTRY.md`.

## 5. What might already exist

- **`analysis/dbchar_rt_ncrna_workbench/`** — the T1/T2/T3/T4 tier table, the filter catalogue
  and the splitting-hazard analysis. Exploratory, **not** a governed gate; `results/dbchar_g1…g7`
  win on any disagreement. Its numbers were re-derived from the canonical parquet by
  `embed_g0` and all nine reproduced exactly; that is why they are used here.
- **`docs/dbchar_workbench_snapshot/exports_v2/RT_NCRNA_DATASET_HANDOVER.md`** — the source of
  the three splitting hazards in §7b. Load-bearing and re-checked.
- **The V4 embedding caches.** Both are graded `DO-NOT-USE` above, and the reason is measured,
  not assumed: zero of 16,458 registered ncRNA hashes appear in any of the six V4 oriented sets,
  and zero of the 4,950 ESM-C ids are registered RT hashes.
- **`EMBEDDINGS_HOWTO.md` in RETRON-DB_V4** — environments, weights and the bf16 batch-geometry
  trap. Re-verified on 2026-09-18: both envs import, `esm==3.2.0`, weights present.
  What would make it untrustworthy: it is a dated snapshot; re-run the imports first.

⚠️ Absence is loud; wrongness is quiet. In this project's own history, 21.4 GB of embeddings
existed, read as ready, and had been computed on unoriented sequence. Two specific traps this
track inherits and has already defused:

1. **`.replace("T","U")` in the RiNALMo precedent is a no-op.** RiNALMo's alphabet is T-based
   and `Alphabet.encode` aliases U to T internally. The call is harmless but misleading and is
   removed, not carried.
2. **The ncRNA alphabet contains IUPAC ambiguity codes** — 214 sequences, 4,117 nt, almost all
   N. RiNALMo's vocabulary covers R, Y, K, M, S, W, B, D, H, V and N natively, so nothing maps
   to `<unk>` and no substitution is applied. This was checked before, not after, production.

## 6. Claims this task tests

| id | role in this task |
|---|---|
| `C6` | primary |
| `C2` | supporting |

⛔ Ids and roles only. Wording and status live in `idea-stage/docs/research_contract.md`.
`REFUTED` is a result, not a failure.

## 7. Gates

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| `embed_g0_input_contract` | the PAIR-ELIG universe and the ncRNA hash round-trip, 16,458 of 16,458 | LIGHT | `C2` | done when results/embed_g0_input_contract/ exists and run.sh reproduces every count and hash |
| `embed_g1_representations` | frozen pooled and per-token caches for 29,192 RT and 16,458 ncRNA, bit-identical on re-run | LIGHT | `C2` | done when results/embed_g1_representations/ exists and run.sh reproduces the manifest hashes |
| `embed_g2_frozen_baseline` | held-out-component retrieval MRR under the full control ladder, against the trivial baselines | FULL | `C6` | done when results/embed_g2_frozen_baseline/ exists and run.sh reproduces the ladder table |
| `embed_g3_contrastive` | the same confirmatory metric under learned linear projection heads | FULL | `C6` | done when results/embed_g3_contrastive/ exists and run.sh reproduces the held-out metric |

`embed_g3` is **conditional**: it runs only if `embed_g2` beats every trivial baseline on the
held-out split by the margin declared before that readout. Otherwise the track closes at `g2`.

### 7a. Population — frozen

**PAIR-ELIG**: 30,924 exact pairs, 29,192 unique RT hashes, 16,458 unique oriented ncRNA hashes,
from `rt_ncrna_exact_pairs_v1.parquet`. T1, T2, T3 and T4 are attached as **pair-level boolean
views only**; they never define the representation population and never silently become a
denominator. Non-Retron file-label pairs, outgroup-model pairs, contig-clipped pairs, partial
RTs and short RTs are **retained and stratified**, never filtered.

### 7b. Splitting rule — the three inherited hazards

1. `rt_seq_hash` is the leakiest key; exact sequences are strain variants.
2. `tax_species` is never split across taxonomy systems; 10,452 genomes appear under both NCBI
   and GTDB, 8,882 under different species names.
3. `genome_id_norm` is not safe; one physical locus is republished under several accessions.

The split unit is therefore the **connected component of the bipartite pair graph after both
sides are clustered**. Pairs are weighted by `physical_locus_key`, not counted raw: 9,362 of
30,924 pairs are one physical locus republished across databases.

**The frozen split lands as an explicit assignment table**, hashed in the gate manifest —
sequence hash to cluster id to component id to split fold — and is never re-derived at use
time. `embed_g0` measured why: mmseqs is reproducible, but `cd-hit-est` under multithreading
is not, and a first rerun moved component counts by up to 3 in ~6,000. Clustering now runs
single-threaded, which was verified byte-reproducible over two runs; the assignment table is
the belt to that braces. A split rule that cannot be regenerated exactly is not frozen.

### 7c. Provenance required on every array

sequence hash · exact sequence length · model name · weights identity · package version ·
torch and CUDA version · layer used · pooling method · dtype · special-token handling ·
orientation rule · batching and bucketing rule · truncation status · producer version and hash.

The batching rule is frozen before production and demonstrated two ways, both of which must
fire: a re-run under the identical rule must be **bit-identical**, and a re-run under a
deliberately different batch geometry must **differ**. Arrays are never compared by maximum
absolute difference — that statistic is a length correlate, not a measure of sameness.

### 7d. Trivial baselines — run first, reported beside every embedding number

sequence length · GC content · k-mer composition · the detection-model label shortcut ·
RT length against ncRNA length. See the kill criterion in §2.

### 7e. Negative and control ladder — every rung reported

| rung | mismatch drawn from |
|---|---|
| 0 positive control | same physical locus, boundary-trimmed variant; must match |
| 0F failure control | pair table permuted within block; must read null |
| 1 | anywhere in the universe |
| 2 | length- and GC-matched |
| 3 | same detection model — the retron-type label control |
| 4 | same ncRNA identity cluster |
| 5 | same RT identity cluster |
| 6 | same species or genus, within one taxonomy system only |

A candidate negative is **excluded** when the decoy RT and the true partner RT fall in the same
cluster at the frozen threshold; false negatives are counted and reported, not ignored.

### 7f. Operator amendments of 2026-09-18 — binding

1. **ESM-C context.** The exact installed context limit is verified, not assumed. No silent
   truncation. Any sequence beyond the verified in-distribution regime carries an explicit
   state and is reported separately; it is never pooled into a headline number.
2. **Confirmatory population.** The primary confirmatory framework is the leakage-free held-out
   connected-component test on PAIR-ELIG. Independently recurrent T4 pairs are a **secondary**
   replication and robustness stratum, not the sole confirmatory estimand.
3. **Relatedness split.** Thresholds may be explored. One RT threshold, one ncRNA threshold, one
   graph construction and one split rule are **frozen before confirmation**, after the
   component-size distribution is reported and judged practical. Every other threshold is a
   sensitivity analysis.
4. **Trivial-baseline stop rule.** As in §2. No escalation to rescue a positive.

### 7g. Exploration versus confirmation

`embed_g2` is **EXPLORATORY** and is used to choose the smallest defensible analysis. Before the
final pairing readout, these are frozen and recorded: population, split rule,
relatedness-control construction, negative definitions, projection architecture, objective,
evaluation metrics, stopping rule. The confirmatory evaluation then runs **once**. The final
holdout is not serially tuned against; if it influences any choice, it is demoted to development
data and said so.

## 8. Compute

- Expected: borg GPU 1 (RTX 4090, 24 GB) — measured idle at launch; Ibex is not used unless a
  measured pilot shows borg cannot hold the job.
- Estimated **2** GPU-hours for the whole `embed_g1` production across both models, from the
  workload size: 29,192 proteins / 11,236,474 residues and 16,458 RNAs / 2,719,581 nt, no ncRNA
  over 395 nt. This estimate is **replaced** by the measured smoke-test rate before production.
- Hard stop at 2× the measured estimate — report, do not push through.
- Storage at fp16: 21.57 GB ESM-C per-residue, 6.96 GB RiNALMo per-nucleotide, 0.10 GB pooled.
- Sizing comes from a length-stratified smoke test spanning the real distribution, never the
  head of a file (WA-K.1).

**Production is gated.** No full run before all five of these are reported: import and harness
validation; length-stratified smoke test; context-limit handling; measured throughput and peak
VRAM; output-content validation. The component-size distribution is reported before any split is
frozen.

## 9. Autonomy envelope

**Auto-proceed:** `true`.

**Compute budget** — inside it, do not ask:

| | budget |
|---|---|
| CPU-hours | 60 |
| GPU-hours | 12 |
| max single job | 4 hr |
| review rounds per gate | 3 |

**Decide alone and continue** (log in `docs/BLOCKED.md`): anything reversible, inside the
budget, inside this track's scratch — implement, smoke-test, fail, debug, rerun, add a control,
rerun, report.

**Human gate — stop and wait.** These are the only ones:

- modifying ground truth, or deleting or replacing canonical data;
- promoting `rt_ncrna_oriented_v1.*` into the main worktree's canonical `data/derived/`;
- changing the scientific question, or any frozen evaluation criterion;
- freezing the primary relatedness thresholds and the split rule;
- opening the confirmatory holdout;
- escalating to `embed_g3` after a trivial-baseline result that does not clear §2;
- exceeding the compute budget above;
- promoting an interpretation to a paper or thesis claim;
- anything published or sent outside this machine.

⭐ Not on that list: interpreting a result. This track may generate interpretations, compare
competing explanations, flag surprises and rank them by evidence — it may not declare one
established (WA-A.4). A budget-halt is reported as a budget-halt, never as a pass (WA-A.3).
