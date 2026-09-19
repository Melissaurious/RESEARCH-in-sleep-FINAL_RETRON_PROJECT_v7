# NEGATIVE RESULTS — revision 2

**Revision 2.** Two sections are revised after `embed_x2` (`4f8550b`) and Stage 3C (`34000ee`):
§5 (SPIRE — the failure stands, but two reusable features are separated out) and §6 (embeddings —
the conditional-modelling negative is **superseded**, not deleted). §2a is new (Stage 3C). The
closing statement in §9 is rewritten, because revision 1's version overclaimed.

Negatives are assets here, not embarrassments. This register exists so that no later session
re-runs a closed failure, and so that the thesis can state plainly what was tried and refuted.

Three distinctions are kept throughout:

| kind | meaning | may support an absence claim? |
|---|---|---|
| **REFUTED** | a predeclared criterion was tested and not met, with demonstrated power | yes, within scope |
| **UNDERPOWERED** | the test ran but could not have detected the effect it sought | **no** |
| **DATA_INADEQUATE / INSTRUMENT_VOID** | the instrument could not return a positive at all | **no** — and a zero here is a bug signal |

Governance requires a positive control before any zero is read as absence. Where a positive control
is missing, it is named.

---

## 1 · Stage 2 — the RT0–RT7 track (13 landed negatives)

Frozen as `results/rt07_stage2_final_report/tables/stage2_negative_results.tsv` (commit `46414f4`).
The load-bearing ones:

| id | result | rules out | kind |
|---|---|---|---|
| N01 | Of 32 region names in the held sources, **1** has a stated residue boundary; 18 are derivable only as a procedure. | reading RT0–RT7 as published coordinates | REFUTED |
| N02 | The seven-way partition is recovered in the independent frame but **not** the primary frame; block-count null **p = 0.6965**. Partition itself **NOT ESTABLISHED**. | a stable, recoverable number of numbered domains | REFUTED |
| N03 | **No reconstructed block corresponds to RT0**, even on the sequences the series was built from. | an alignment-derived RT0 coordinate | REFUTED |
| N04 | Of 13 prior claims, **2** reproduced; 3 were circular or seed-dependent; RT5 and RT6 collapse onto one region. | reusing prior RT0–RT7 frames as independent evidence | REFUTED |
| N06 | Under `-M a2m`, DGRs and AbiA retain **0** all-partner states. | a convention-invariant universal conserved core | REFUTED |
| N07 | UG5 v2 failed its predeclared criterion 2: monotone placement for **31 of 67 (46.3 %)**. | transfer of the v2 placement rule | REFUTED |
| N09 | G2L residue-transfer gate **FAIL/BLOCK 4/10** — a fresh family in a related lineage is not a fresh lineage. | G2L as a transfer test | REFUTED |
| N10 | Between-family concordance **0.9865** does not exceed the sequence-level null p99 **0.9906** (it does exceed the cluster-level null p99 0.9066). | reading g6 as significant under every reasonable null | REFUTED (bounded) |
| N11 | The label-free within-Retron arm is underpowered; **26 of 50** subtype strata never entered a distance matrix. | label-free recovery of retron subtype structure | UNDERPOWERED |
| N12 | **Zero frozen anchors** fall in LtrA 1–85 or 39–61; anchor reach is LtrA 97–363. | any operational RT0 or RT1 coordinate from this instrument | REFUTED (instrumental) |
| N13 | **0 independent structural comparators**; the defining RT0 source (Malik, Burke & Eickbush 1999) is not held. | structural or primary-source adjudication of RT0 in Stage 2 | DATA_INADEQUATE |

Also negative, and recorded as design history rather than as a result: two g4 design reviews
returned *not ready* (3/10, 4/10) and the full-length-first design **FAIL/BLOCK 5/10** — which is
what forced the redesign from "estimate domains" to "estimate conserved-state occupancy".

## 2 · Stage 3A — the structural decomposition negative

The cleanest negative in the project, and the most publishable.

| result | value | kind |
|---|---|---|
| **Palm-like unit called** in primary chains | **0.565** (26/46) against a predeclared bar of **0.70** | REFUTED |
| Thumb-like | 0.130 | REFUTED |
| Fingers-like | 0.304 | REFUTED |
| LOGO robustness | **22/22 folds FAIL**; no fold flips a bar | REFUTED |
| Group-level check (reviewer-added) | 12/22 groups = 0.545 — still below the bar | REFUTED |
| PDP replicate partition agreement | **0.385** (20/52 pairs) — the partition itself is unstable | REFUTED |
| C1 spectral modularity (earlier design) | natural k = 3 in **3 of 62** chains (5 %); Q 0.582 natural vs 0.495 forced to 3 | REFUTED |
| C2 contiguity | median **0.255**, median 8 spans per module, **0 of 186** modules a single contiguous span | REFUTED |
| C3 normalised cut | objective degenerate — run **VOID** | INSTRUMENT_VOID |
| Thumb / fingers recurrence | 7 and 8 group pairs, below the ≥ 10 floor | UNDERPOWERED |

**Missing positive control, and it matters.** CATH validated the parser (count agreement 0.6100 vs a
0.6 bar), not the palm/thumb/fingers rules — literature annotation was forbidden by the
anti-circularity contract. The one textbook RT in the population, HIV-1 p66 `1RTD_A`, is itself
**AMBIGUOUS**, and its candidate thumb unit has frac_H 0.521 against the rule's 0.60 threshold. So
the negative is properly stated as: *under this parser **and these thresholds**, the three-unit
decomposition is not recovered* — not as *RT chains have no palm*.

**Reviewer-added caveat not in the closure:** under the BJ-p4 sensitivity arm, the **pooled** palm
C7 flips STABLE 0.770 → NOT_STABLE 0.314.

## 2a · Stage 3C — negatives about the *reference vocabulary* itself · NEW

Stage 3C ran as a census with no inferential test. Its negatives are about what the field's own
descriptions can support.

| result | value | kind |
|---|---|---|
| **Literature fingers coincide with a structural unit** | **0 of 11** (median best Jaccard 0.429); palm 2/7; thumb 3/9 | REFUTED — the literature does not pin these down either |
| A **combined** fingers+palm region | coincides 1/1 (J 0.713) — one unit, not two | the boundary that is real is not the one convention names |
| **References contradict each other** | two 2026 papers on the same Retron-Eco8 protein publish **incompatible** partitions in the same numbering frame; HIV-1 reviews differ by 1–5 residues; one LtrA paper carries two thumb definitions | REFUTED (as a usable truth source) |
| The inherited boundary product | **RED, re-verified on file**: fingers and thumb are arithmetic residuals in **25/25** rows; hardcoded 5HHJ anchor; self-warnings that gate nothing; the **5G2X palm excludes that chain's own catalytic aspartate**; same Ec86 protein given boundaries differing by **77 residues**; anchor misfamilied as a retron when it is a group II intron maturase | INSTRUMENT_VOID |
| Its high thumb agreement (14/25) | an artefact of residual construction — "everything after the palm" | not independent support |
| **RT0/RT1 on structures** | **0 of 62** chains carry any RT0/RT1 state, by construction (enforced in code) | REFUTED (instrumental), not biological absence |
| **Region Y as a universal retron motif** | **all 6 Retron-Eco8 chains lack a VTG-like triplet**; VTG present in **4 non-retron** chains | REFUTED as universal *and* as exclusive |
| Region X coverage | scannable in only **33/62** chains; undefined in **13/21 retron** chains | UNDERPOWERED |
| A general residue-numbered interval for X or Y | **no source states one** | DATA_INADEQUATE |
| Terminal extensions | interpretable in only **20/62** chains; 39 have a truncated anchor series | UNDERPOWERED |
| "No insertions ≥ 20 aa" | the declared gap rule says so (max excess 19) while the instrument's own insertion runs reach **774** residues — **a 'no insertions' statement would have been false** | both measures reported together |
| Does unusual architecture explain the 3A failures? | only weakly: median **1** outside-core unit for no-call chains vs **2** for call chains, identical median unit counts | the easy excuse is refused |

**Two positive findings are recorded here because they bound the negatives**: the catalytic site lies
in a single unit 19/19 and the detector's prediction shares that unit 19/19 *including all six
residue-level misses* — so **localisation and residue membership separate cleanly**; and `CAT_STATE
262` sits exactly **2 residues** before the nearest catalytic aspartate in **17/17** chains, two
instruments with no shared input. Scope: **all 19 truth-bearing chains are non-retron.**

## 3 · Stage 3B — a kill criterion, not a partial success

| result | value | kind |
|---|---|---|
| **K5 decoy sufficiency** | legitimate pool **23** (31 per chain copy, 49 with NCS pseudo-replicates) against a required **≥ 60** — **TERMINALLY FIRED** | REFUTED (the track's own stop rule) |
| Decoy pool as first reported | 36 → corrected to **19** under the operator's definition | self-correction, retained |
| In-sample Tier-A recovery | 13/19 = **0.684**, with 4 of the 13 hits AMBIGUOUS and one decided by 2.51 vs 2.576 Å | PRELIMINARY, not a performance number |
| Out-of-sample LOCO (reviewer recomputation) | **12 HIT / 5 MISS / 2 ABSTAIN** — the two abstentions are omitted from the closure summary | UNDERPOWERED |
| Two misses could never have been hits | `9NL3_A` truth is a single residue; `9Z6Z_H` truth has \|i−j\| = 1, far below SEP_MIN 75 | design artefact |
| Tier B | **0 HARD_PAIR chains** — under the frozen HIT rule the PASS branch was **unreachable** | INSTRUMENT_VOID |
| Negative and homologous-chemistry controls (C2b, C3, C3b) | **never scored as outcomes** | NOT_YET_TESTED |

The operator's ruling that *"all six exact-residue misses are adjacent-Asp confusions" may not be
used* is itself a retained negative — and that superseded sentence is still sitting in the landed
`cat3b_g2/README.md`.

## 4 · Mestre / historical classification

| result | value | kind |
|---|---|---|
| **M2a control gate K3** | shuffled queries confidently placed at **7.9 %** (v3.1) and **19.8 %** (v2) against a ≤ 1 % limit — **FAIL** | REFUTED |
| Placement confidence as a discriminator | *"LWR does not separate: shuffled median 0.998"* | REFUTED |
| Independent review | Codex **FAIL 4.5/10**; the 76-protein validation set had already been used to pick v3 over v2 | REFUTED |
| Non-retron panel "PASS" (0/1,083) | **1,080 fail extraction** — the confidence rule was never exercised on the negatives | DATA_INADEQUATE, not a pass |
| V4 re-inference of Mestre's tree | ≤ 3 of 11 clades; contains 91 of 112 substitutes, 3 of them RNA polymerase subunits; **no positive control ran** (the same rule on the published tree gives 10/11) | REFUTED as a reproduction |
| Mestre's alignment and RT0–RT7 extracts | *not published and not on disk*; no asset preserves them | DATA_INADEQUATE |
| MCC-v3.1 extractability | **82.1 %** against a written **≥ 90 %** (K1) | a missed criterion **not** declared a failure — see OQ-08 |
| "Toro 2018 reported the same tree failure" | **not found** in the sources; scoped negative | claim withdrawn |
| Superseded silhouette statistics | 0.2565 / z = 25.27 superseded by **0.156963 / z = 2.75–2.81** | retraction, retained |
| Five prior sequence-tree routes | five failures against predeclared criteria; partly self-inflicted by cd-hit-50 (19.1 → **28.5 %** with redundancy restored); dereplication **enriches** truncated tips (30.8 → 24.1 % full-window) | REFUTED (prior project, `[UNVERIFIED]` here) |

## 5 · De novo ncRNA discovery (SPIRE)

| result | value | kind |
|---|---|---|
| **Round 2 held-out decision** | **`ROUND2_FAIL_STOP`** on the predeclared G1–G6 and on G1–G7 | REFUTED |
| G1 enrichment | 343 vs 118.9 expected = **2.88×**, p = 5e-5, against a required **≥ 3×** | REFUTED |
| **G7 positional prior** | the method finds 343; a **fixed interval (−193…−24) finds 901**; both ends ±20 nt: 60 vs 87 | REFUTED — decisively |
| Per-type positional priors | **969 (92.2 %)** IoU ≥ 0.5 against the method's 343 | the prior wins |
| Released SPIRE package on 377 blinded CM-positive loci | abstains on **94 %**, performs at chance (12 rediscovered vs 12.2 expected); a parser bug always prints 0 significant pairs | INSTRUMENT_VOID |
| Covariation specificity | 88 % of distal windows, 75 % of non-retron RT windows, **3/3 group II intron sets**, against 74 % of positives | REFUTED |
| Round 1 boundary recovery | CMfinder 62/120 at IoU ≥ 0.5 but **0 % within ±20 nt**; mLocARNA passed 13/24 real vs **16/24 distal controls** | REFUTED |
| Round 1 full rule sensitivity | **3/10** POS sets | REFUTED |
| The two Round-1 candidates | *"neither is credible"* — the unmatched spans lie in CDS | withdrawn |
| Design leak found and recorded | the coding filter exempted the first 50 nt of the RT ORF | self-correction |
| "No novel retron ncRNA exists" | **not claimable** — the source says explicitly it is not evidence of absence | UNDERPOWERED |

**What the post-mortem leaves behind, and revision 1 wrongly discarded.** The instrument failed; two
*features* survive and are inherited by any future boundary task:

1. a **retron-enriched ~90-nt internal ncRNA submotif** — 1,793 instances, median centre −116 nt,
   median length 88 nt; retron 140/164 (85 %) vs pooled non-retron 42/80 (52.5 %), Fisher
   **p = 1.0e-7**, OR 5.3;
2. a **strong RT-relative, type-conditioned positional prior** — per-type **969 (92.2 %)** at
   IoU ≥ 0.5 against the method's 343.

Both are **CM-derived** and overlap the locus's own CM call **97.9 %** of the time. So they are
same-paradigm rediscovery and **may never be evaluated against CM truth** — but as priors/features
scored against *non-CM* truth (the published extents) they are legitimate and strong. Correct status:
**FAILED as de novo ncRNA-family discovery; PRELIMINARY-but-useful as positional features.**

## 6 · Embeddings and conditional modelling

| result | value | kind |
|---|---|---|
| **Rung 3 (type-matched decoys)** | +0.0298, 95 % CI **[−0.0048, +0.0633]** — margin not cleared, escalation refused | UNDERPOWERED (correctly *not* read as equivalence) |
| Rung 5 (same-RT-cluster decoys) | M-CCA **below** the k-mer baseline (0.0992 vs 0.1050), 10 components | UNDERPOWERED |
| Neighbourhood retrieval in the open pool | partner is the nearest neighbour for **0.56 %** of queries; median rank **238 of 2,756** | REFUTED as partner identification |
| **R-conditioned generation realism** | R's 3-mer JSD **0.00428** is *worse* than T's 0.00256; R over-generates length (178 vs 156 nt); all arms far less structured than real ncRNA (MFE −42.65 vs −58.70) | REFUTED |
| R − T in tier T4 (X1) | −0.00776 [−0.01761, +0.00169] | **SUPERSEDED by X2** — T4 resolves at −0.02594 [−0.03508, −0.01731] over 247 components |
| R − T under pair weighting (X1) | +0.00486; pooled −0.00066 | **X1's reporting defect stands** (T0-4); X2 aggregates token-weighted within component and cross-fits all folds |
| Two trivial baselines (`B-pop`, `B-model`) | return a constant 0 on every held-out candidate — never actually evaluated | INSTRUMENT_VOID (defect) |
| Prior openCRISPR-for-retrons model | *"does FAMILY RECOGNITION, not partner recognition"*; LOFO TypeIV **0.5020 = chance** vs 0.7136 row-matched; decomposition **22 % training volume / 78 % family identity** | REFUTED (prior, audited not re-run) |
| Prior structure-supervision arm | clean preregistered null, **−0.0010 (t = −0.55)** | REFUTED |
| **X2 · pair-level discrimination against near neighbours** | the counterfactual effect decays ~10-fold as the control tightens (C1 +0.01766 → C2 +0.01543 → C3 +0.00397 → C4 +0.00168); at C3 only **52.5 % of pairs** favour the observed RT | **UNDERPOWERED / not demonstrated** — and this is the negative that bounds the whole pairing story |
| **X2 · generalisation to unlike RTs** | least-similar quartile (nearest-training cosine < 0.983): R − T **−0.00584 [−0.01288, +0.00136]**, spans zero | UNDERPOWERED |
| **X2 · permutation control is NOT flat** | P − T = **−0.00590 [−0.01109, −0.00023]** — a model trained on within-type *deranged* RTs still beats the type label by ~24 % of the full effect | a real qualification, reported not absorbed |
| **X2 · magnitude of the exact-RT residual** | R − G seeds −0.0055 / −0.0113 / −0.0156, **sd 0.0051 ≈ the primary estimate 0.0055**; near-duplicate sensitivity arm **spans zero** (−0.00210 [−0.00601, +0.00196]) | sign replicated, **magnitude undetermined** |
| Prior co-variation result | `msr_msd` **nested inside** clade → V = **1.0000 by construction**; `msr_msd_family` 44.4 % the literal string `nan` scored as a category | VOID |

## 7 · Neighbourhood, fusion, annotation

| result | value | kind |
|---|---|---|
| Neighbourhood as a retron **detector** | retrons rank **27th of 41** RT families on Tier-A defence accessory carriage; 53.50 % vs 45.36 % neighbour-matched, fold **1.179 [1.161, 1.198]** — inside a predeclared `DEAD` band | REFUTED (prior project) |
| Operon delimitation | single-gene runs 55.0 % at 150 bp vs 16.7 % at 500 bp on 60 loci; figures are *"illustrative examples chosen by a query"* | NOT_YET_TESTED |
| Neighbour annotation | **all 41,250,531 accessory CDS have `has_sequence = False`** | DATA_INADEQUATE |
| Local InterProScan / Pfam | Pfam-A holds 3–4 profiles, TIGRFAM 1 — a clean run is `DATA_INADEQUATE`, **not** a negative | INSTRUMENT_VOID |
| `position_relative_to_rt` shipped field | present on 4.28 % of placements; **all 12 candidate reference frames fail** (best 0.99 %); it is an index minus a coordinate | REFUTED and characterised |
| The ~2,682 bp downstream mode | 99.96 % `true_start_clipped` in the dominant stratum; 18 distinct sequences supply it | technical artefact, not a biological prior |
| Old report headlines | reconciled as definitional or technical (e.g. 43.5 % "effector slot" → 3.29 % canonical) | retraction, retained |
| CM null from `--cut_ga` against a GA-less database | "0 % of 1,925 genomes carry a retron ncRNA" → the correct figure is **67.76 %** | the project's own canonical example of a broken-search zero |

## 8 · The 977 set

**A 977-element experimentally validated retron ncRNA set does not exist on this machine.** Two
independent searches agree; the nearest candidates (1,216 and 936) are covariance-model calls whose
"validated" flag means the *RT protein* matches Mestre 2020, with `validated_ncrna` true for only
**165**. No filter of the Mestre table yields 977. This is a negative about an asset, and it blocks
every plan that assumed boundary truth at that scale.

---

## 9 · What these negatives are worth — revised

Revision 1 closed with a sentence that overclaimed in three ways: it asserted neighbourhood does not
carry retron identity (only its use as a *discriminator* was ever tested, in unverified prior work);
it treated annotation lineage as though it were a biological determinant; and it said the
representation models failed to recover partner-level structure, which `embed_x2` has since
qualified. **That sentence is withdrawn.** The replacement:

> **Where the information is, and is not.** Across four instrument families pushed to predeclared
> criteria, *type- and lineage-level* structure is recovered easily and *partition- and pair-level*
> structure is not. Contact-density decomposition does not recover a three-way domain partition
> (0.565 < 0.70) — and neither does the literature, which disagrees with itself (fingers coincide
> 0/11). Comparative covariation does not localise ncRNA boundaries better than a fixed positional
> interval (343 vs 901). Conditional modelling recovers a large lineage effect (G − U −0.0426) and
> only a small exact-RT residual beyond the homolog group (R − G −0.0055, seed sd 0.0051), with
> near-neighbour discrimination at 52.5 % of pairs. What *is* reproducible is a catalytic centre:
> single-unit in 19/19 chains, replicate-stable 13/14, and independently located to within two
> residues by a sequence HMM state.

Three things this does **not** say, deliberately: it does not say neighbourhood or fusion
architecture is uninformative — **those were not tested**; it does not say a modern label-independent
phylogeny would fail — **that was never attempted**; and it does not say the exact RT carries no
partner information — **it carries a small amount whose magnitude is undetermined**.
