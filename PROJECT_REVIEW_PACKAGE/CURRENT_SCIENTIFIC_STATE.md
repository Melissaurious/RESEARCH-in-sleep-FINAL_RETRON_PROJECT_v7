# CURRENT SCIENTIFIC STATE — one section per project arm

Each section: **status · exact claim · denominator · inferential unit · commit · canonical file ·
limitations · downstream relevance.** Numbers are quoted from landed artefacts, not from memory.

---

## 1 · Database characterisation (Stage 1)

| | |
|---|---|
| **status** | **CLOSED**, all gates REPRODUCIBLE; `human_input_audit: PENDING` |
| **exact claim** | The corpus is identity-pinned; record, locus, exact RT, taxonomic occurrence and RT–ncRNA pair are non-equivalent units and **no two convert by a constant** (loci per exact RT 1.11–5.49 by database). ncRNA carriage varies **6.6-fold** with the detecting tool combination (89.23 % myRT+PADLOC → 13.50 % myRT alone). |
| **denominator** | 3,358,182 corpus lines → 3,059,700 RT-anchored records → 2,847,312 loci → **501,561 exact RTs**; 344,154 canonical ncRNA placements; 630,741 Retron loci |
| **inferential unit** | five declared units, never collapsed; rates name their own |
| **commit** | `8f3ea78` (g1) · `27ae7aa` (g2) · `2b13a9e` (g2b, g3) · `8e56a53` (g4) · `5636735` (g5) · `ab50f34` (g6) · `5e74794` / `8c8e5cf` (reports) |
| **canonical file** | `results/dbchar_g1…g7b/`; derived data in `data/derived/` |
| **limitations** | C1/C2/C8 all derive from **one JSON parse of one corpus** — circularity `LOW`, not `NONE`. The geometry figures (94.5 % upstream, 99.8 % same strand) are **partly circular**: the covariance models were trained on msr-msd in that position. The extended report contains **two circular positive-control claims** (Ec107-like 98.6 %; the "≥ 2 of three lines" stratum). |
| **downstream relevance** | Supplies every denominator, PAIR-ELIG, and the annotation-limits result that is the strongest publishable material in the project. |

## 2 · RT0–RT7 and the conserved-state mapper (Stage 2)

| | |
|---|---|
| **status** | **CLOSED 2026-09-19** with six explicit residual limitations; g6 and g7a each passed an independent, vendor-disjoint review with **0 blockers** |
| **exact claim** | Under `hhmake -M 50`, the frozen mapper `rtmap-1.0.0/53a1e738a19b3896` met all seven predeclared conditions in one confirmatory run on a fresh lineage (UG25), and maps conserved HMM states to residues in individual RT proteins. Applied: **369,381** eligible, **354,102** inspectable, `CATALYTIC_CONFIRMED` **0.9653 of CAT-mapped**. Historical labels: 4 ESTABLISHED / 2 PARTIAL / **2 UNRESOLVED (RT0, RT1)**, all LtrA-local. |
| **denominator** | 501,561 → **369,381 eligible** (the g5/g6 denominator) → 354,102 MAPPED; CAT rate on its own denominator of 356,229 |
| **inferential unit** | exact RT protein; for g6, the family stratum |
| **commit** | `dd9cdae` (g4b instrument) · `6f4a7fe` (g5a, g5) · `049d7ab` (g6) · `34db87f` (g7a) · `46414f4` (final report) |
| **canonical file** | `results/rt07_g4b_production_mapper/` (instrument) · `docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv` (**binding** for label wording) |
| **limitations** | GII-centred frame (median MAPPED 0.94 GII → 0.49 Retron) confounds **every** between-family comparison. Scope is `-M 50` only. `DELETED_STATE` ≠ absent region; `NO_SUPPORTED_MAPPING` ≠ biological absence. MyRT/PADLOC/DefenseFinder are **strata, never truth** — no accuracy, precision, recall or ROC against a tool label, ever. g6 is **descriptive concordance**; thesis-level biological claims and classification reassessment are **BLOCKED on the evidence**. |
| **downstream relevance** | The mapper is the most reusable instrument the project owns. Its state system may be used descriptively by Stage 3; it may **not** be presented as resolving any historical label. |

## 3 · Stage 3A — structural decomposition

| | |
|---|---|
| **status** | **CLOSED at FAIL** (a clean, preregistered negative) |
| **exact claim** | Under PDP plus predeclared secondary-structure rules, a three-way fingers/palm/thumb partition is not recovered: palm-like called in **0.565** of primary chains against a **0.70** bar; thumb-like 0.130; fingers-like 0.304; **22/22** leave-one-group-out folds FAIL. The PDP partition is itself unstable: unit count agrees in **20/52** replicate pairs (0.385). |
| **denominator** | **46 primary chains in 22 biological groups** (register: 62 chains / 31 groups) |
| **inferential unit** | RT chain (group-level check: 12/22 groups = 0.545, also below the bar) |
| **commit** | `67c137b` (closure; via `…_v7-stage3c` or `…_v7-asset-audit`) |
| **canonical file** | `analysis/stage3a_structural_core/closure/STAGE3A_CLOSURE.md`; `g2r/results/rt_units.report.txt` |
| **limitations** | **No biological positive control** — CATH validated the *parser*, not the palm/thumb/fingers *rules*; literature annotation was forbidden by the anti-circularity contract; the one textbook RT (HIV-1 `1RTD_A`) is itself **AMBIGUOUS**, and its candidate thumb has frac_H 0.521 against a 0.60 rule, so thresholds — not only the parser — drive some NO_CALLs. All 31 groups fall in **one** structural cluster; LOGO is influence, not independence. `EXTRA_DOMAIN` is length-confounded. Under the BJ-p4 arm the *pooled* palm stability flips (0.770 → 0.314). `TRANSFER_READINESS.md` carries a stale "mkdssp BROKEN" claim. |
| **downstream relevance** | Publishable as a negative. It also frames Stage 3C: the failure is not "our parser missed it" but "these regions are not separable contact-density units — and the literature has not pinned them down either". |

## 4 · Stage 3B — catalytic geometry

| | |
|---|---|
| **status** | **STOPPED on kill criterion K5.** Labelled "CLOSED at PARTIAL", which is a **mislabel** — PARTIAL means a bounded-scope *pass on Tier B*, and Tier B was never evaluated |
| **exact claim** | Only in-sample Tier-A calibration exists: **13 HIT / 6 MISS / 0 ABSTAIN = 0.684**. Out-of-sample LOCO: **12 HIT / 5 MISS / 2 ABSTAIN**. K5 (decoy sufficiency) **TERMINALLY FIRED**: legitimate pool **23** (49 counting NCS pseudo-replicates) against a required **≥ 60**. |
| **denominator** | 19 truth-bearing Tier-A chains; Tier B 17 chains never opened; register 62 chains |
| **inferential unit** | RT chain |
| **commit** | `67c137b` |
| **canonical file** | `results/cat3b_g2_contract_and_thresholds/`; `analysis/stage3b_design/G2_DECOY_AUDIT_AND_K5_CLOSURE.md` |
| **limitations** | `SEP_MIN` 75, `SEP_MAX` 115 and `D_MAX` 6.0 Å were each derived **from the same 19 truth pairs then scored on them**, and each window edge is set by a single chain (one of which, `8SXT_A`, is itself a MISS). **Tier B contains 0 `HARD_PAIR` chains**, so a residue-exact HIT was structurally unreachable there. Tier B was partly inspected during design, so it is **not blind** for future use. No hit/abstention/false-fire bar was ever declared. Negative and homologous-chemistry controls were never scored. **Tier A contains no retron.** |
| **downstream relevance** | Usable only as in-sample calibration material. The "PARTIAL" label must be erratum'd before any citation — Stage 3C already inherited it. |

## 5 · Stage 3C — architecture integration

| | |
|---|---|
| **status** | **COMPLETE as a census, but NOT PROMOTABLE.** Independent, model-disjoint review (Codex): **`FAIL_BLOCK`, 4.5/10, 5 blockers — all upheld** after the author re-derived each contested number |
| **exact claim (as corrected)** | Across nonuniform subsets of a **selected** 62-chain register, mapped sequence-state blocks and Tier-A **non-retron** catalytic labels often occupy a large PDP unit. "Conserved core plus variable accessory architecture" is a **hypothesis**, not an established representation. |
| **denominator** | 62 chains / 31 groups; Comparison A 19 truth-bearing chains (**none a retron**); Comparison C **16** statements over **7** chains; Comparison D 21 retron chains |
| **inferential unit** | RT chain; no inferential test was declared or run |
| **commit** | bundle `34000ee`; review, errata and decision `eeaf0ae` |
| **canonical file** | `analysis/stage3c_architecture_integration/` — ⛔ **`STAGE3C_DECISION_REPORT.md` and `README.md` may not be read or cited without `docs/errata/2026-09-19_stage3c_review_errata.md`** |
| **limitations (the five blockers)** | **B1** the headline `13/14` replicate figure is not the declared analysis — it mixes 7 truth-based and 7 detector-based pairs; under the declared truth-bearing scope it is **7/7 (median 0.882) from only TWO biological groups**, against **0/7** for unit count. **B2** a motif row contaminated the fingers denominator; corrected literature fingers **0/8**. **B3** a source is `NOT_RETRIEVED` in one audit and `FULL_TEXT` in another. **B4** every reported Region-X motif hit came from an **undeclared wide-window fallback**; under the declared rule X is defined in **24/62** chains (**3/21** retron) and **none** contains NAXXH or AXXH. **B5** the Stage-3B defects were not bounded. Also: `CAT_STATE 262` was **constructed** as the modal HMM state of `[YF].DD` motif starts, so its 2-residue offset is an **expected motif-identity check, not independent validation**. |
| **downstream relevance** | Rows **S05, S11, S12 and the Region-X part of S16 are WITHDRAWN**. Five re-runs (R1–R5) are specified, **not authorised, not performed**. Nothing may be promoted until they are. |

## 6 · Mestre historical classification

| | |
|---|---|
| **status** | **CLOSED.** M2a closed as a **stopped, failed validation attempt**; M2c and M2d not run |
| **exact claim** | Three separable questions, three answers. (i) Mestre's *published objects* re-join and re-plot (18/18 tables byte-identical). (ii) Independent *re-inference* of the classification **FAILED** (≤ 3 of 11 clades; 91 of 112 substitute proteins present, 3 of them RNA polymerase subunits; the same rule on the published tree gives 10/11). (iii) *Placement* into the 11-clade system **FAILED its control gate K3**: shuffled queries confidently placed at **7.9 %** (MCC-v3.1) and **19.8 %** (v2) against a ≤ 1 % limit. |
| **denominator** | 1,928 Mestre nodes; 746 shuffled queries (v3.1) / 860 (v2); 1,083 non-retron panel proteins |
| **inferential unit** | RT sequence / clade / query |
| **commit** | `b05934f` (M2a bundle) · `e047fdc` (MCC-v3.1 freeze) · `033bfcb` (closure/handoff) |
| **canonical file** | `analysis/mestre_audit/REPORT.md`; `results/m2a_reference_reconstruction/tables/CONTROLS_v3_K3.json` |
| **limitations** | Mestre's **alignment and RT0–RT7 extracts are not published and not on disk**, so the failure cannot be diagnosed further. Independent review **FAIL 4.5/10**: the 76-protein validation set had already been used to choose v3 over v2. The non-retron panel "PASS" (0/1,083) is **1,080 extraction failures** — the confidence rule was never exercised on negatives. K1 INCOMPLETE (AU test cancelled for budget); extractability **82.1 %** against a written ≥ 90 %. Compute overrun 64.5 CPU-h vs 60 approved, accepted retrospectively. |
| **downstream relevance** | The published tree/table remain a **comparator**. Placement is closed as an instrument. ⚠️ **None of this speaks to a modern, label-independent de novo phylogeny, which has never been attempted here.** |

## 7 · SPIRE — de novo ncRNA discovery

| | |
|---|---|
| **status** | **CLOSED** at `ROUND2_FAIL_STOP`; discovery branch terminated |
| **exact claim** | On a frozen held-out split, the method failed its predeclared gates: G1 enrichment **343 vs 118.9 expected = 2.88×** against a required ≥ 3×; **G7 decisive — a fixed positional interval (−193…−24) recovers 901 against the method's 343**, and both-ends ±20 nt 60 vs 87. |
| **denominator** | DEV 88 groups / HELDOUT 85 (81 evaluable); 1,051 members; 377 blinded CM-positive loci for the package test |
| **inferential unit** | locus group |
| **commit** | `ed4a663` |
| **canonical file** | `analysis/spire_ncrna_audit/ROUND2/RESULTS.md`; `POSTMORTEM/RESULTS.md` |
| **limitations** | Truth coordinates are **production-CM calls**, and the 21 CMs were themselves built by CMfinder — so any agreement is partly same-paradigm rediscovery (the post-mortem submotif overlaps the locus's own CM call **97.9 %** of the time). Covariation is non-specific: 88 % of distal windows, 100 % of group II intron sets. "No novel retron ncRNA exists" is **not claimable**. |
| **downstream relevance** | **Two features are inherited, not the instrument**: a retron-enriched ~90-nt internal submotif (retron 85 % vs non-retron 52.5 %, Fisher p = 1.0e-7, OR 5.3) and a **type-conditioned positional prior** (per-type 969 = 92.2 % at IoU ≥ 0.5). They may be **priors** for a boundary model but may **never be evaluated against CM truth**. |

## 8 · Embeddings — cross-modal retrieval

| | |
|---|---|
| **status** | **CLOSED**; escalation to a contrastive model correctly **refused** |
| **exact claim** | Frozen ESM-C (RT) and RiNALMo (ncRNA) representations identify the observed partner far above chance: MRR **0.4407** [0.4039, 0.4772] vs chance 0.0900, permutation p = 0.0005, reverse direction 0.4738. **But the type-matched rung fails**: +0.0298, 95 % CI **[−0.0048, +0.0633]**. |
| **denominator** | 4,638 test pairs / **357 components** (n_eff 14.1) |
| **inferential unit** | bipartite connected component (RT-cluster ↔ ncRNA-cluster) |
| **commit** | `2c9127b` (g2) · `15e00b8` (g2b split) · `9154972` (g2c) |
| **canonical file** | `results/embed_g2_frozen_baseline/tables/g2_test_ladder.tsv` |
| **limitations** | Splits are cluster-disjoint (0 of 16,458 ncRNAs in >1 fold) but **not homology-disjoint**: 82.46 % of held-out RTs have a ≥ 0.50-identity training relative; 100 % of held-out pairs are reachable from training by one modality. **Two of five trivial baselines were inert by construction** (`B-pop`, `B-model` return a constant 0 on every held-out candidate), so the README's "the retron-type label shortcut does not by itself retrieve partners" describes a test that never ran. The **predeclared rung-0 positive control was never run**. Mechanistically the leading canonical dimension carries η²(type) **0.809 / 0.724**. |
| **downstream relevance** | Establishes that the recoverable cross-modal signal is **type-level**. This is why X1/X2 moved to a likelihood endpoint. |

## 9 · X1 / X2 — conditional RT→ncRNA modelling

| | |
|---|---|
| **status** | **X2 CLOSED.** Frozen gate returned `X2-A`; **the conclusion of record is the qualified paragraph, not the label** |
| **exact claim (binding, `X2_CLOSURE.md` §2)** | *Specific RT sequence information provides a reproducible improvement in prediction of the cognate ncRNA beyond broad retron type and beyond a coarse 50 %-identity RT homolog-group representation. However, **most of the RT-associated predictive gain is explained at the homolog-lineage level**, while the additional specific-RT effect is **small, weak at the individual-pair level under close counterfactuals, and uncertain in magnitude across training seeds**.* |
| **denominator** | **1,075 components / 30,924 pairs**, 5-fold component-blocked cross-fit (T4 stratum: 247 components) |
| **inferential unit** | bipartite component, token-weighted within component, bootstrap over components (n_eff **12.5**) |
| **commit** | results `4f8550b`; **closure `fdf0872` — governing**; chapter reporting layer `d7d3ece` |
| **canonical file** | `results/embed_x2_rt_specificity_confirmation/X2_CLOSURE.md`, `X2_HANDOFF.md`; **inference export** `tables/X2_COMPONENT_LEVEL_EXPORT.tsv` (1,075 rows); **join-only export** `tables/X2_PAIR_LEVEL_EFFECTS.tsv.gz` (30,924 rows, carries `nearest_train_rt_cosine` and `relatedness_stratum`) |
| **replication detail (reporting layer, `d7d3ece`)** | R − T is the same sign in **all 5 folds and all 3 seeds**; **28 of 36 strata** have the whole 95 % CI below zero, 1 above, 7 spanning zero; the repeated-event class `multiple_species` gives −0.02507 over 364 components, so the effect is **not** an artefact of repeated database deposition. **UNDETERMINED** (below the 30-component floor): RT homolog groups > 100 members (22 components) and ncRNA clusters > 100 (14) |
| **pair vs component, stated as a finding** | component-level vs raw pair-weighted: C1 +0.017664 / +0.009894 · C2 +0.015434 / +0.007951 · **C3 +0.003974 / −0.000205** · C4 +0.001683 / +0.002391. At the nearest-neighbour tier the two **differ in sign**. The component estimate is the preregistered endpoint; the pair view is what forbids per-pair reading |
| **the four levels — never collapse them** | **(1) lineage:** G − U −0.04256 [−0.04619, −0.03893], 86.0 % of components. **(2) exact-RT residual:** R − G −0.00551 [−0.00797, −0.00312]; same sign on 3/3 seeds but −0.0055…−0.0156, sd 0.0051 ≈ the estimate; T4 −0.00499; near-duplicate arm **spans zero**. **(3) pair discrimination:** C1 +0.01766 → C2 +0.01543 → C3 **+0.00397** → C4 +0.00168; at C3 **52.5 % of pairs** and the raw pair-level mean is **−0.000205**. **(4) biochemical compatibility: NOT_YET_TESTED.** |
| **limitations** | **Internal cross-fitted confirmation, not external validation** — no new data; the same 30,924-pair population underlies X1 and X2. The permutation arm is **not flat** (P − T −0.00590): a model trained on within-type *deranged* RTs still beats the type label by ~24 % of the effect. Generalisation is undemonstrated in the least-similar quartile (R − T −0.00584, CI spans zero), and the similarity range is narrow (median nearest-training cosine 0.987). Effects are small in absolute terms (0.0017–0.0177 nats/nt). The largest ncRNA clusters are not adjudicated. X1's prose reports only one weighting; its own table carries pooled −0.00066 and pair-weighted +0.00486. |
| **explicitly NOT supported** | biochemical compatibility · binding · interchangeability · **orthogonality** · causal **co-evolution** · that any non-observed combination is incompatible · identification of the cognate RT at pair level · **any per-pair biological inference**. A counterfactual RT is a *conditioning control*, never a negative pair. |
| **downstream relevance** | Any follow-up inherits `X2_HANDOFF.md` **R1–R6**: C3/C4-strength counterfactuals; component-level inference; ≥ 3 seeds; report **both** R − T and R − G (reporting only "RT beats type" measures lineage, not pairing); distance-to-training as a primary axis; unobserved pairings are never negatives. |
| **reporting layer (`d7d3ece`)** | The RT-ncRNA chapter package is now built on the frozen X2 result — every `PENDING` section resolved, 29 reporting claims (C-25…C-29 added for lineage dominance, seed instability, the relatedness gradient, the pair-vs-component weighting and the UNDETERMINED large-cluster strata), figures **F8** (cross-fitted decomposition, replication, folds), **F9** (counterfactual decay + weighting) and **F10** (lineage share, seed spread, relatedness gradient) generated from landed tables. Multiplicity is **re-derived** from two independent frozen sources and fails if they disagree: **96.85 %** of RTs have one ncRNA partner (max 176); **82.28 %** of ncRNAs have one RT partner (max **705**). |
| **methodological precedent (six points, `d7d3ece` §8)** | **(1)** OpenCRISPR trained a small protein-conditioned gRNA generator: frozen ESM2 → linear projection → one bidirectional encoder layer → three cross-attention decoder layers, ~0.7 M trainable parameters, plain next-token cross-entropy, **no contrastive or mismatch term**; their decisive evidence is **functional**. **(2)** Reused here: the vendored `transformer.py` at a pinned sha256 (`c1f2112b…`), the architectural shape, the capacity class, the objective, the optimiser settings and the frozen-encoder pattern. **(3)** Rejected: `gRNAModel.py` (needs an unpublished namespace), the released **checkpoint weights** (they carry a CRISPR prior), ESM2 8M, the two-segment sentinel vocabulary (needs msr/msd boundaries this project has not established), their train/validation arrangement, and **any OpenCRISPR sequence**. **(4)** What was reproduced is the *question* — does a protein-conditioned RNA decoder depend on **which** protein it is given — turned from their qualitative demonstration (SpCas9 16/16 well-formed vs MalE 0/64) into a **graded, statistical** experiment with five conditioning arms. **An adaptation, not a replication**; OpenCRISPR numbers are never a benchmark. **(5)** The component-blocked, lineage-controlled design is forced by two measured facts: one ncRNA is observed with **705** RTs (so a protein-only split cannot stop near-identical RNAs appearing on both sides), and the homolog representative alone captures **~78 %** of the advantage over the type label. **(6)** Their exchangeability validation **cannot be reproduced**: there is no set of retron RT–ncRNA combinations experimentally labelled compatible or incompatible, so no classification metric, no calibrated probability of function, and no validated generated ncRNA. Acquiring exchangeability labels is **the precondition**, not a refinement. |

## 10 · The experimental panel

| | |
|---|---|
| **status** | **REGISTERED with a measured exposure map**; not independent |
| **exact claim** | 175 retron elements carry functional measurements: **81** empirically determined RT-DNA sequences; RT-DNA production measured for 103 with **67 > 0**; human editing > 0 for **100**, bacterial **27**, phage **16**; **31** synthesised and tested with outcome undetermined. Exposure against project populations: **58 train-exposed · 33 val/test-exposed · 56 catalogue-only · 12 sequence-near · 16 fully external**. |
| **denominator** | 175 panel rows; 145/175 RTs in the 501,561 catalogue; 175/175 carry a Mestre accession |
| **inferential unit** | retron element (assayed) |
| **commit** | external assets (sha256 `80b2f565…` panel, `8a51cf71…` ncRNA FASTA); exposure map computed at `48f9e1b` |
| **canonical file** | `EXPERIMENTAL_EVIDENCE_REGISTER.tsv` (this package) |
| **limitations** | The panel is **an assay layer on the same prediction set the project analyses** (174/175 inside Mestre's reference set). `RT_sequence` is empty in all 175 rows — use `rt_protein_aa`. Only **12** ncRNAs match the corpus by exact hash while **80** match by blastn ≥ 90 %, which measures **published-extent vs CM-cut disagreement**. **No swap, cross-reactivity or orthogonality experiment exists in any local asset.** |
| **downstream relevance** | ⛔ Not a compatibility or orthogonality validation set — **functional measurements, not exchangeability labels**. ✅ A preserved opportunity: **prospective external functional validation** of RT-DNA production or editing predictions on non-exposed elements — a **different endpoint**, requiring its own preregistration. |

## 11 · ncRNA boundary project

| | |
|---|---|
| **status** | **NOT_YET_TESTED** as prediction; comparative recovery **FAILED** |
| **exact claim** | Every comparative boundary result is at or near zero: Round 1 ±20 nt recovery **0–17.5 %**, Z6 **0 %**, Round 2 both-ends ±20 nt **60/1,051** (median 5′/3′ error 29.5/37 nt, median length error −69.5 nt). |
| **denominator** | 1,051 Round-2 members; 175 published extents as candidate truth |
| **inferential unit** | ncRNA instance |
| **commit** | `ed4a663` |
| **canonical file** | `analysis/spire_ncrna_audit/POSTMORTEM/RESULTS.md` |
| **limitations** | **The assumed 977-element truth set does not exist on this machine** (two independent searches; nearest candidates are CM calls with `validated_ncrna` true for only 165). The only non-CM truth is the 175 published extents, of which **58 are train-exposed**. Per-type positional priors reach 92.2 % IoU ≥ 0.5 but are scored **against the CM's own cut** — circular. |
| **downstream relevance** | Feasible today: characterise **boundary disagreement** on the ~95 non-train-exposed extents, using the SPIRE features as priors. Not feasible: a supervised predictor at this n without a declared minimum detectable effect. |

## 12 · Phylogeny and co-evolution

| | |
|---|---|
| **status** | **NOT_YET_TESTED** — no phylogeny exists anywhere in this project |
| **exact claim** | Co-evolution has **no null for shared ancestry** here, so it has not been tested. The contract's "phylogenetically matched" control rung (C6) was never built. |
| **denominator** | — |
| **inferential unit** | RT–ncRNA pair (prospectively) |
| **commit** | contract at `94a1a78` |
| **canonical file** | `idea-stage/docs/research_contract.md` (C6); planning only in `idea-stage/programme/06_…md` |
| **limitations** | The prior co-variation result is **void**: `msr_msd` is nested inside clade, so V = **1.0000 by construction**, and `msr_msd_family` was 44.4 % the literal string `nan` scored as a category. Five prior sequence-tree routes failed — **prior-project, `[UNVERIFIED]` here**, and aimed at different questions. ⛔ **Mantel tests are ruled out** by prior decision; a PP-style block-constrained permutation is the named alternative. |
| **downstream relevance** | X2 strengthens the case for a **relatedness backbone** (not a publication tree), because the measured effect lives largely in lineage structure (G explains ~78 % of R − T). A modern label-independent de novo phylogeny is **open, not refuted**. |

## 13 · Accessory and fusion architecture

| | |
|---|---|
| **status** | **NOT_YET_TESTED** at corpus scale; **UNDERPOWERED** on 62 structures |
| **exact claim** | Nothing has been measured at scale: **all 41,250,531 accessory CDS carry `has_sequence = False`**, and effector information exists only as **PADLOC rule definitions**. On the structure panel, terminal extensions are interpretable in only **20/62** chains (39 truncated, 3 with no mapped anchor), and two insertion measures disagree by construction (declared gap rule: no insertion ≥ 20 aa; instrument insertion runs reach **774** residues). |
| **denominator** | 41,250,531 accessory CDS; 62 chains |
| **inferential unit** | accessory CDS / locus / chain |
| **commit** | `12ea561` (workbench handover) · `34000ee` (Stage 3C Comparison E) |
| **canonical file** | `docs/dbchar_workbench_snapshot/exports_v2/RT_NCRNA_DATASET_HANDOVER.md`; `analysis/stage3c_architecture_integration/TERMINI_FUSION_SUMMARY.tsv` |
| **limitations** | Local InterProScan/Pfam is a **stub** (3–4 profiles) — a clean run against it is `DATA_INADEQUATE`, **not** a negative; full Pfam-A 37.0 is registered on Ibex. Operon figures are *illustrative examples chosen by a query* and support no rate; single-gene runs swing 55.0 % → 16.7 % with the gap threshold. |
| **downstream relevance** | Stage 3C produced **six binding design requirements** for a later task, chiefly: do **not** define the RT core with the GII-centred mapper (it truncates N-terminally on exactly the families of interest), and use an insertion measure that does not require anchors to be mapped. Prior work closed only the **detector** question (retrons 27th of 41 families) — the descriptive question is untouched. |
