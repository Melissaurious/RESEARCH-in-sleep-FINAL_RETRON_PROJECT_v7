# m2a_reference_reconstruction

STATUS: UNVERIFIED — `run.sh` was **not** re-executed end to end from the assembled bundle
(BS-3). A full rerun repeats about 60 CPU-h, and the approved M2a–c budget is exhausted
(64.5 CPU-h measured against 60 approved, §6). `bash verify.sh` re-derives every table that
follows from the shipped placements, fits and trees in a temporary copy of the bundle:
**12 / 12 byte-identical** on 2026-09-19. Invoke both scripts with `bash`, because `chmod`
was refused in `results/`.

**GATE OUTCOME: STOP.**
- **K3 FAILED** on the shuffled-query control.
- **K1 is INCOMPLETE:** the AU sub-criterion was not evaluated. Only the pruning/mapping check
  ran, and it is near-tautological.
- **K2 passed numerically only under the design as IMPLEMENTED**, which deviates from the
  launcher (§1a).

M2c was not run. M2d is not approved. No threshold or rule was changed after the evaluation
replicates were read.

**Independent review (Codex, read-only, thread `01a0ba36`): FAIL, 4.5 / 10.** It confirms the
STOP, the table reproducibility, the controls and the V4 reconciliation, and it lists REQUIRED
repairs. Verbatim record: `docs/decisions/2026-09-19_m2a_outcome_stop_and_review.md`. This
README was amended **before landing**, in response to that review; the amendments are listed
in that record.

Launcher: `launchers/LAUNCHER_M2_historical_classification_expansion.md` (rev-4).
Decisions: `docs/decisions/2026-09-19_m2_mcc_v3_adopted_m2ac_active.md`.
Weight FULL. Claims touched: C8, C3 and C7 (support roles). **No claim status is proposed.**

---

## 1 · What was measured — one measurement

**Can the clade membership of a withheld, clean historical Mestre reference be recovered from
the remaining historical reference system, without the clade label constructing the placement?**

- **Primary design:** relatedness-blocked leave-out. Whole 85 %-identity groups are withheld;
  10 replicates per extractor; thresholds calibrated on reps 1–5 and evaluated on reps 6–10.
- **Secondary design:** sequence-level random holdout, 5 replicates, MCC-v3.1 only.
- **Two extractors, both reported, never harmonised:** MCC-v3.1 is primary (Toro-template RT0–RT7
  interval); MCC-v2 required core is the sensitivity analysis.

### 1a · Where the implementation departs from the frozen contract (found by review; all REQUIRED)

1. **The holdout is not clade-stratified.**
   - The launcher asks for about 10 % of groups withheld, stratified by clade.
   - `a03` shuffles all groups globally until 10 % of *taxa* are withheld, with no labels.
   - Rare clades are thinly evaluated as a result (clade 5: one evaluation placement under
     v3.1).
2. **Calibration and evaluation are not query-disjoint.**
   - Replicates were drawn independently, so evaluation replicates 6–10 reuse queries from
     calibration replicates 1–5.
   - Overlap: v3.1 249 / 618 unique evaluation taxa (305 / 746 placements); v2 303 / 702
     (366 / 860).
3. **The reduced references are not independent of the query.**
   - Each replicate's reference MSA is the full alignment (built *with* the withheld
     sequences) minus their rows.
   - So this is a repeated placement check against a query-influenced reference system, not a
     reconstruction from the remaining sequences alone.
4. **MCC-v3.1's core-QC is conditional.**
   - The ≥ 70 % MCC-v2-core-inside-interval check is applied only when the MCC-v2 route is
     itself extractable (`m10`, `mcc_v3.py`).
   - **75 clean proteins entered the MCC-v3.1 reference without it.** The launcher and
     decision prose did not state this condition.
5. **The 76 source-stated proteins are not independent validation.**
   - They were used to choose MCC-v3 over MCC-v2, so they support method selection and
     description, not independent post-selection validation.
   - The v3.0 → v3.1 correction was technically appropriate but post-application. It changed
     the counts from 1,446 to 1,490 clean extracts, and from 58/76 to 62/76.
6. **The status rule makes category 2 unreachable.**
   - The launcher defines category 2, "deeper expansion", as a confident placement with
     pendant length above the clade's 95th percentile.
   - The implemented rule assigns such placements to `OUTSIDE`.
7. **Terminology.** The launcher says "column-shuffled"; the implementation shuffles residues
   before re-alignment. That is an appropriate non-homology control, but the name differs.

This is a **historical reconstruction**, not an exact reproduction. Mestre's RT0–RT7 MSA is
unrecoverable, and the reference alignment here is ours: MAFFT FFT-NS-2, untrimmed, on MCC
extracts.

## 2 · Denominators (`tables/DENOMINATOR_LEDGER.json`, `tables/*_tip_status.tsv`)

| | MCC-v3.1 (primary) | MCC-v2 (sensitivity) |
|---|---:|---|
| published tips | 1,928 | 1,928 |
| no published protein held (112 substitutes + 2 absent) | 114 | 114 |
| clean proteins | 1,814 | 1,814 |
| not admitted to the reference | 324 (296 discordant templates, 27 low identity, 1 core-QC) | 86 (85 not extractable + 1 MULTI_CORE) |
| duplicates collapsed | 4 | 5 |
| **reference taxa** | **1,486** | **1,723** |
| 85 %-identity groups | 1,469 | 1,698 |

Because the Mestre population was itself drawn from Toro's 85 %-identity representatives, the
85 % groups are nearly singletons. **The blocked and random designs therefore differ very
little**, and that is stated rather than presented as a relatedness control that bites.

## 3 · Results

### K1 — reference reconstructable: INCOMPLETE (AU sub-criterion not evaluated)

The pruning check below is near-tautological: it retests splits of the already-published topology after pruning. It verifies mapping consistency, not reconstruction of the clades.

- After pruning to reference taxa, **all 10** published-monophyletic clades stay unrooted-
  monophyletic under both extractors. Clade 10 stays non-monophyletic, as published.
- Fixed-topology `LG+F+R10` fits on the published topology:
  - MCC-v3.1: lnL −479,046.69, BIC 980,078.9 (1,486 taxa × 1,501 columns);
  - MCC-v2: lnL −429,962.47, BIC 883,566.2 (1,723 × 892).
- **The AU test and the clean unconstrained ML tree were NOT completed.** Ibex job 52098505 was
  cancelled after 28.5 min (5.7 CPU-h) to stay near the budget; its checkpoint is preserved at
  `/ibex/user/rioszemm/experiments/m2a/tree/`. The K1 AU sub-criterion is therefore
  **not evaluated**.

### K2 — historical clade recovery: numerically met, under the IMPLEMENTED design only (unstratified global holdout with calibration/evaluation query overlap; §1a), both extractors

| evaluation | held-out real queries | confident-correct | **confident-wrong** | ambiguous | outside |
|---|---:|---:|---:|---:|---:|
| MCC-v3.1 blocked, reps 6–10 (K2: clades 1–9, 11) | 705 | **88.2 %** | **0.0 %** | — | — |
| MCC-v2 blocked, reps 6–10 | 778 | **90.0 %** | **0.0 %** | — | — |
| MCC-v3.1 random, reps 1–5 (secondary) | 717 | 87.0 % | 0.0 % | — | — |

- Per clade, never pooled: `tables/{v3,v2}_blocked_per_clade.tsv` and `v3_random_per_clade.tsv`.
  **There is no confident wrong-clade placement in any clade, in any design.**
- Weakest clades:
  - clade 6: MCC-v3.1 1/4, MCC-v2 4/5;
  - clade 5: 1–4 withheld, underpowered under v3.1 (3 groups);
  - clade 7: ~79 %.
- Clade 10 is reported separately. Under MCC-v3.1 only 72 of 164 clean clade-10 proteins
  extract, but the held-out ones that do recover at 39/41. Under MCC-v2 the figure is 74/81.

### K3 — controls: **FAIL** (shuffled-query control), PASS (negative panels)

| control | result | limit | verdict |
|---|---|---|---|
| residue-shuffled held-out queries, MCC-v3.1 (reps 6–10) | **7.9 %** confidently placed (59 / 746) | ≤ 1 % | **FAIL** |
| residue-shuffled held-out queries, MCC-v2 | **19.8 %** (170 / 860) | ≤ 1 % | **FAIL** |
| non-retron panels: 583 Toro-2014 non-retron extracts + 500 no-evidence catalogue RTs | 0 / 1,083 confident. 1,080 fail MCC-v3.1 extraction; 3 are placed `OUTSIDE` | ≤ 5 % | PASS |
| 15 RNA-polymerase substitutes | 0 reach placement (all `NO_HIT` at extraction) | 0 | PASS |
| 97 other substitutes (not in the reference) | 49 not extracted; 38 confident, 3 ambiguous, 7 outside | report | reported |

**Why the shuffled control fails (diagnosis only; no rule was changed):**
- LWR does not separate: shuffled median 0.998; τ_LWR hit the grid ceiling 0.99, and the
  flag is recorded in `tables/*_tau_FROZEN.json`.
- The confidently placed shuffled queries sit on **very short** pendants (median 0.105 against
  0.47 for real), at an attractor region mostly in **clade 3** (38 / 59 under v3.1;
  158 / 170 under v2).
- Only a median 71–74 % of their residues survive the keep-length alignment (real queries:
  100 %).
- The frozen rule had only an *upper* pendant bound and a 50 % alignment floor, so these pass.
- **Conclusion:** the confidence rule is **not a validated discriminator** of non-homologous
  input. On historical data it is protected mainly by the upstream MCC-v3.1 extraction gate,
  which shuffled sequences bypass by construction.

## 4 · Historical-tree comparison (`tables/TREE_COMPARISON_*`)

| tree | exact unrooted clade splits (of 11) | best-split Jaccard ≥ 0.9 |
|---|---:|---:|
| published Mestre tree (1,928 tips) | **10** | 10 |
| V4 recovered, contaminated (1,843 tips; 91 substitutes), six trees | 2–3 | 7–9 |
| clean MCC-v3.1 reconstruction | **not computed** (cancelled for budget) | — |

**Denominator reconciliation:**

| figure | what it counts | denominator | source |
|---|---|---|---|
| `10/11` | clades that are exact unrooted splits of the **published** tree | 11 published clades, 1,928 tips | this bundle, `a05`; retron-db `clade_recovery.tsv` agrees |
| `9/10` | the **K1 criterion**: monophyletic clades that must survive pruning | the 10 published-monophyletic clades | launcher K1; here **10/10** survive under both extractors |
| `≤3/11` | V4 **support-based** recovery (common ancestor on IQ-TREE's root, supported) | 11 clades, 1,843-tip contaminated trees | V4 `s7i`, re-run by M1 |
| `2–3/11` | exact unrooted splits in the V4 trees | 11 clades, 1,843 tips | this bundle, `a05` |
| `4–6/11` | V4 purity ≥ 0.9 on a root-dependent common ancestor | 11 clades, 1,843 tips | M1 V4 sub-audit |
| `7–9/11` | V4 best-split Jaccard ≥ 0.9, root-independent | 11 clades, 1,843 tips | this bundle, `a05` |

## 5 · The M2b query freeze (step 10; recorded here, table stored locally)

`data/derived/m2_mestre/M2B_QUERY_FREEZE.tsv.gz` has 501,561 rows, sha256 `63603e3e…dd92`
(`tables/M2B_QUERY_FREEZE.sha256`). Extracts: `M2B_extracts.faa`, sha256 `0734f7b2…3110`.
Inclusion (MCC-v3.1, modern mode), by stratum:

| stratum | included | of |
|---|---:|---:|
| A (≥ 2 system lines) | 25,454 | 33,670 (75.6 %) |
| B1 (1 line) | 10,456 | 20,451 (51.1 %) |
| B0 (profile only) | 9,514 | 24,166 (39.4 %) |
| MULTI / mixed | 0 | 7,593 (6,105 `NO_HIT`) |
| D (discordant call) | 1 | 5 |
| X (no retron evidence) | not a query | 415,676 |

## 6 · Counts that look bad (BS-5)

Primary unit: published historical tips entering the reference, MCC-v3.1.

    n_attempted: 1928
    n_succeeded: 1486
    n_dropped: 442   (114 no published protein · 324 MCC-v3.1 not extractable · 4 duplicates collapsed)

MCC-v2 sensitivity: n_attempted 1928, n_succeeded 1723, n_dropped 205 (114 · 86 · 5).
Placement: every withheld query in all 25 replicates was placed (0 `UNPLACED`, 0
`UNABLE_TO_ALIGN_OR_PLACE_RELIABLY`).

- **Compute: 64.5 CPU-h against 60 approved (+4.5 CPU-h, 7.5 % over).** This mixes process user+sys time (58.8) with 5.7 *allocated* core-hours for the cancelled Ibex job. The attribution of the replicate overrun to host load rests on the observed load average, not on landed timing evidence. The 0.84 CPU-h raxml-ng full-reference fit is included in the total (see `PROVENANCE.md`).
  - IQ-TREE fixed-topology fits: 13.0 + 8.4 CPU-h. The estimate had been small; `LG+F+R10` on
    about 1,500 taxa was far costlier.
  - Replicates: 35.2 CPU-h, twice the estimate, because the host was shared at load ~80 on
    48 cores.
  - Ibex tree (cancelled): 5.7 CPU-h. M2b: 1.3 CPU-h.
  - The overrun was noticed only once the fits completed, and was not approved in advance.
- The AU test and the clean ML tree were not run (K1 sub-criterion **not evaluated**).
- τ_LWR could not meet its declared rule; it defaulted to 0.99, and the flag is recorded.
- MCC-v3.1 does not extract 324 clean historical proteins, and the loss is clade-dependent
  (clade 10: 72/164).
- `a04`'s random-design summary lists `reps: 1..10`, but only reps 1–5 exist. The counts are
  correct, from 5 reps (`n_real` 745); only the list field is wrong. It is not edited (BS-1).
- `groups2/` came from a second, single-command MMseqs2 run after the first used a fallback
  invocation. Group counts are identical (1,469 / 1,698); membership order differs.

## 7 · The six adversarial questions (BS-14)

1. **Where is a headline overstated?**
   - "Recovers historical clade membership": true for **held-out clean historical
     references** that pass extraction.
   - It says nothing about modern sequences. A 0 % confident-wrong rate coexists with a
     7.9–19.8 % confident rate for **shuffled** input: "confidently placed" does not mean
     "homologous".
2. **Which alternative explanation produces these numbers?**
   - High recovery is expected when a withheld sequence has close relatives left in the
     reference.
   - The 85 % blocking barely removes relatives (the groups are nearly singletons), so this is
     largely a near-neighbour recovery test, **not** a test of placement at depth.
3. **Could this have returned a negative?** Yes, and it did: K3 failed as specified.
4. **The unit of every rate:** held-out real queries within each evaluation design; shuffled
   rates are per shuffled query. Per-clade tables carry their own counts.
5. **Numbers without a producing script:** none in `tables/`. The CPU accounting (§6) is from
   `/usr/bin/time` and `sacct`, recorded in `PROVENANCE.md`.
6. **What was withdrawn or weakened?**
   - The clean-tree comparison is not delivered.
   - The K1 AU test is not evaluated.
   - The confidence rule is **withdrawn as a validated instrument** until the shuffled control
     passes on fresh replicates.
   - MCC-v3 went to v3.1: the one R5 calibration-quantity correction, disclosed.

## 8 · Contents

| path | content |
|---|---|
| `scripts/` | `a01`, `a03`–`a06`, `b01`, `c01` (not run), `mcc_v3.py`, `place_full.py`, plus copies of `m04`, `m07`, `m10` |
| `slurm/` | the two Ibex scripts (tree: cancelled; AU: cancelled before start) |
| `ref/`, `aln/`, `groups2/`, `rx/` | reference sets, alignments, 85 % groups, full-reference raxml-ng fit |
| `val/` | per-replicate placements, query alignments, per-replicate fitted model and tree, EDPL |
| `tables/` | every number quoted above |
| `run.sh` / `verify.sh` | recorded commands / the cheap re-derivation check |
