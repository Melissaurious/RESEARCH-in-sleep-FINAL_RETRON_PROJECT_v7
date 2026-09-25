# embed_g2_frozen_baseline — **FROZEN RESULT**

**Gate weight: FULL.** Settles `C6` for this stage. Split definition: commit `15e00b8`,
`results/embed_g2b_frozen_split/` — used unmodified. Pre-registration: `PREREG.md`, written
before any validation or test number existed.

> ## Headline
> **A cross-modal signal exists and survives random and composition-matched negatives, but it
> is NOT distinguishable from a trivial k-mer baseline once negatives are matched on retron
> type.** The declared stop rule **FAILS at rung 3**, so **escalation to `embed_g3` is NOT
> authorised**.

## Exact models and probes

Frozen **pooled** representations only — ESM-C 300M (960-d) and RiNALMo giga-v1 (1280-d) from
`embed_g1`. Token-level arrays untouched (`DEFER`).

| id | what it scores a candidate by | role |
|---|---|---|
| `B-pop` | candidate ncRNA's training frequency | **ncRNA-only marginal** |
| `B-len` | −\|len_nc − ridge(len_rt)\| | length |
| `B-gc` | −\|gc_nc − ridge(len_rt)\| | composition |
| `B-kmer` | cosine(ridge RT-dipeptide→ncRNA-4-mer, candidate 4-mer) | composition |
| `B-model` | P(candidate's `detection_model` \| RT embedding), multinomial logistic | **RT-only marginal / label shortcut** |
| `M-CCA` | cosine in a shared latent space from regularized CCA | **cross-modal compatibility model** |

An RT-only score is constant across candidates and therefore exactly chance; the informative
RT-only baseline is the label shortcut, which is why `B-model` fills that role.

## Training / validation choices

`M-CCA` fit on **training components only** (21,647 pairs). The **only** validation-selected
quantity was the CCA configuration, over the predeclared 9-point grid `k∈{16,32,64} ×
α∈{1e-2,1e-1,1}`, by the single rule *maximise validation rung-1 MRR*. Selected **k=32,
α=0.01** (validation rung-1 MRR 0.4773). No negatives, metric or threshold was selected on
validation. Test was opened once, after that freeze.

## Negative construction

50-way retrieval (1 true + 49 decoys), RT→ncRNA primary. Decoys seeded
(`PCG64(20260918)`), identical sets for every model. **False negatives excluded**: any decoy
that is a true partner of the query RT anywhere in the 30,924-pair table is removed and
redrawn — necessary because one ncRNA has 705 RT partners. Chance MRR = **0.0900**.

## Primary result — test fold, 4,638 pairs / 357 components

| rung | decoys matched on | `B-kmer` | **`M-CCA`** | 95 % CI | components |
|---|---|---|---|---|---|
| 1 | nothing (random) | 0.2265 | **0.4407** | [0.4039, 0.4772] | 357 |
| 2 | length + GC | 0.1418 | **0.2262** | [0.1972, 0.2565] | 316 |
| 3 | **detection model (retron type)** | 0.1534 | **0.1832** | [0.1550, 0.2126] | 299 |
| 4 | ncRNA cluster | 0.0764 | 0.0925 | degenerate | **1** |
| 5 | RT cluster | 0.1050 | 0.0992 | [0.0867, 0.1127] | **10** |
| 6 | species | 0.1111 | 0.2982 | [0.1904, 0.4262] | **22** |

`M-CCA` top-1 = 0.1714, top-5 = 0.5164 at rung 1. Reverse direction (ncRNA→RT) rung 1:
MRR **0.4738** [0.4380, 0.5104], top-1 0.1828 — the effect is not an artefact of direction.

## Component-level uncertainty and the failure control

Every interval is a **bootstrap over components** (10,000 resamples), never over pairs.
Permutation control (rung 0F, 2,000 draws, true partner replaced by a random fold ncRNA):
observed **0.4407** against null mean **0.0901** [0.0781, 0.1040], **p = 0.0005**. The rung-1
effect is not a scoring artefact.

## Stop rule — the decisive table

`M-CCA` must exceed the best trivial baseline by more than the 95 % bootstrap half-width of the
**paired per-component difference**.

| rung | components | diff (M-CCA − B-kmer) | 95 % CI | verdict |
|---|---|---|---|---|
| 1 random | 357 | +0.2142 | [+0.1737, +0.2537] | **PASS** |
| 2 len+GC | 316 | +0.0844 | [+0.0503, +0.1187] | **PASS** |
| 3 model | 299 | **+0.0298** | **[−0.0048, +0.0633]** | **FAIL** |
| 4 nc cluster | 1 | +0.0161 | degenerate | UNDETERMINED |
| 5 RT cluster | 10 | −0.0058 | [−0.0222, +0.0111] | UNDETERMINED |
| 6 species | 22 | +0.1872 | [+0.0864, +0.3051] | UNDETERMINED |

**`embed_g3` escalation is NOT authorised** (`tables/g2_escalation_decision.json`).

## Near-duplicate sensitivity (frozen, 1,525 pairs / 284 components)

| rung | M-CCA | 95 % CI | n |
|---|---|---|---|
| 1 | 0.4329 | [0.3910, 0.4751] | 1,525 |
| 2 | 0.2219 | [0.1885, 0.2570] | 1,328 |
| 3 | 0.1936 | [0.1596, 0.2301] | 1,310 |
| 5 | 0.0913 | [0.0864, 0.0962] | 340 |

Removing near-duplicates changes rung 1 by −0.008. **The result is not driven by the residual
near-duplicate channel.**

## Strata (descriptive, rung 1)

T1 0.4588 [0.4210, 0.4962] (n=4,574) · T2 0.4912 [0.4477, 0.5332] (n=3,922) ·
T3 0.5263 [0.4768, 0.5746] (n=3,430) · T4 0.4732 [0.4053, 0.5437] (n=991). Intervals overlap
throughout; no stratum is distinguishable from another.

## Failure modes found and recorded

1. **My component-sufficiency guard was wrong.** Rungs were gated on ≥200 *queries*, but the
   immutable inference unit is the **component**. Rung 4 has **one** component and rung 5 has
   **ten**, so their intervals are degenerate — rung 4's apparent stop-rule "PASS" (half-width
   0.0000) is an artefact of a single component, not evidence. Corrected post hoc with a
   declared ≥30-component floor in `g2_stop_rule_corrected.tsv`; the uncorrected table is kept
   beside it. **This is structural, not fixable by resampling**: within-cluster decoy pools are
   necessarily drawn from few components, so the hardest rungs are exactly where
   component-level inference cannot be supported at this universe size.
2. **The pre-registered pessimistic tie-breaking biases against tie-heavy baselines**, and that
   bias flatters the cross-modal model. `B-pop` and `B-model` sat at 0.0200 — below the 0.0900
   chance floor — which is a tie artefact. The standard expected-rank convention is reported
   beside the pre-registered one for every cell (`mrr_expected_ties`); it moves those two to
   0.0392, still below chance, and **changes no conclusion**.
3. `B-pop` and `B-model` are uninformative under both conventions: ncRNA popularity and the
   retron-type label shortcut do not by themselves retrieve partners.

## Exact strongest statement supported

> Frozen pretrained ESM-C and RiNALMo representations of naturally paired retron RT and ncRNA
> sequences contain cross-modal information that identifies the true partner far above chance
> (MRR 0.44 vs 0.09) and above length-, GC- and k-mer-matched controls, and this generalizes
> across the declared sequence-relatedness component split. **Once candidate negatives are
> matched on retron type (detection model), the advantage over a trivial RT-k-mer→ncRNA-k-mer
> baseline is no longer statistically distinguishable (+0.0298, 95 % CI [−0.0048, +0.0633]).**

## Exact claims NOT supported

- **Not** co-evolution, molecular binding, physical interaction, or residue–nucleotide contact.
- **Not** compatibility signal beyond retron-type structure — rung 3 fails the stop rule.
- **Not** any claim at rungs 4, 5 or 6: component-level inference is unsupported there
  (1, 10 and 22 components).
- **Not** generalization to evolutionarily unrelated RT or ncRNA sequences — the frozen
  interpretation, unchanged.
- **Not** a per-pair result: 4,638 test pairs carry n_eff = 14.1.
