# LAUNCHER 03B — catalytic-site architecture

> ## ⛔ CLOSED — 2026-09-18. PARTIAL. KILL CRITERION K5 TERMINALLY FIRED.
>
> **Tier B was never opened and contributes zero rows to any evaluation. No Tier-B inference is
> permitted from this launcher. Gates `g3`, `g4` and `g5` must NOT be run under it.**
>
> Terminal reasons: Tier-A calibration completed under the frozen motif-blind detector; exact
> catalytic-residue recovery 13/19 = 0.684; zero abstentions among truth-bearing Tier-A chains;
> diagnostic site-level overlap 19/19, explicitly post hoc and **not** the declared success
> criterion; corrected strict Tier-A decoy pool **19**; legitimate pool including de-duplicated
> predeclared controls **23**; the maximally permissive count including chain-copy/NCS
> pseudo-replicates reaches only **49**; K5 requires **≥ 60**.
>
> **Strongest supported statement:** the frozen motif-blind structural detector localises the
> independently defined RT-polymerase catalytic site consistently across Tier-A calibration
> structures — with 19/19 diagnostic site-level overlap — but exact catalytic-residue recovery is
> 13/19 (0.684), and the predeclared false-positive/decoy-sufficiency criterion is not met.
>
> **Misses — the only supported characterisation:** 6/6 predictions retain at least one independently
> evidenced catalytic residue; 4/6 have an off-target Asp within two residues of a truth residue;
> 1/6 uses a residue independently supported in a replicate of the same protein; 1/6 meets neither.
> The phrase "all six exact-residue misses are adjacent-Asp confusions" may not be used.
>
> Any future Tier-B validation requires a **new, explicitly approved design** that solves decoy
> sufficiency **prospectively** — for example by enlarging the structural population or redefining
> the candidate/control space **before** outcomes are examined. It may not be an amendment to this
> launcher.
>
> Closure record: `analysis/stage3b_design/G2_DECOY_AUDIT_AND_K5_CLOSURE.md`.
> Landed, reproducible, unaltered: `results/cat3b_g1_population_freeze`,
> `results/cat3b_g2_contract_and_thresholds`.

**Track id:** `cat3b` · **Opened:** 2026-09-18 · **Weight:** FULL · **Autonomy:** `AUTO_PROCEED = true`
within §9.

**Design basis, binding:** `analysis/stage3b_design/STAGE3B_DESIGN_DOSSIER.md` as amended by
`analysis/stage3b_design/EVIDENCE_REPAIR_2026-09-18.md`. The register files
(`STRUCTURE_REGISTER.tsv`, `REPLICATE_GROUPS.tsv`, `TIER_ASSIGNMENT.tsv`, `CONTROLS.tsv`,
`ANTICIRCULARITY_CONTRACT.tsv`) are inputs to this track and are frozen at the commit that lands it.

---

## 1. Objective and success criterion

**Question.** Can the catalytic site of bacterial reverse transcriptases be identified reproducibly
from its three-dimensional catalytic-aspartate architecture, independently of a predefined
YXDD-like sequence motif, and how conserved is that geometry across RT families despite variation in
the local sequence motif?

**Secondary question, admitted only as exploratory** (see §3 and §7 `g5`): how do retron RTs compare
with other bacterial RT families in catalytic-site sequence and geometry?

**Object.** The canonical RT catalytic aspartate network — an asymmetric arrangement of a motif-A
aspartate and a motif-C aspartate pair. It is **not** the four-residue "tetrad" of prior work, and
the launcher does not inherit that object.

**The verdict is predeclared before any detector is fitted.** The three outcomes below are fixed by
this document. The thresholds inside them are fixed by gate `g2` and are never moved afterwards.

| verdict | condition |
|---|---|
| **PASS** — transferable | on Tier B clusters, held out and opened once, the hit rate among non-abstaining chains meets the `g2` bar, the abstention rate is at or below the `g2` bar, and the false-fire rate on the motif-positive non-RT controls is at or below the `g2` bar |
| **PARTIAL** — bounded scope | the PASS conditions hold inside a scope named in `g2` **before** Tier B is opened, and demonstrably fail or abstain outside it |
| **FAIL** | geometry alone does not separate the true site from within-protein decoys at the `g2` bar on Tier B. The reportable result is that a combined sequence-plus-structure instrument is required |

**Predeclared expectation: PARTIAL.** Tier B is 4 unique biological sequences in 3 relatedness
clusters. That supports a bounded transfer statement and not a general one. A PASS verdict requires
Tier B to be enlarged first (§10), never a bar to be relaxed.

**Success criterion for the track.** `results/cat3b_g1…g5/` exist, every gate's `run.sh` reproduces
its landed numbers, the frozen detector package annotates an unseen experimental RT chain, and the
verdict is one of PASS / PARTIAL / FAIL with abstention reported separately from failure.

---

## 2. Kill criteria

The track stops and reports, rather than continuing, if any of these fires.

| # | condition | action |
|---|---|---|
| K1 | the anti-circularity checker in `g2` detects any forbidden input reaching the detector | stop; the detector is void and is rebuilt, not patched |
| K2 | Tier B truth is read, plotted or summarised before the detector digest is frozen and landed | stop; Tier B is burned and the track reports on Tier A only |
| K3 | any threshold is changed after Tier B has been scored | stop; the run is void and reported as void |
| K4 | fewer than 12 Tier A chains survive the declared eligibility cut | stop; the calibration population is too small and the launcher is amended by a decision record |
| K5 | the within-protein decoy pool falls below 60 pairs after eligibility filtering | stop; specificity cannot be measured on this set |
| K6 | the detector's abstention rate on Tier A exceeds 0.50 | stop at `g3`; report FAIL early rather than tuning to reduce abstention |
| K7 | a Tier A truth label is found to rest on a motif call rather than on metal, substrate, author annotation or mutation | stop; that label is removed and the denominators are recomputed before `g3` |

---

## 3. Non-goals / out of scope

* **Fingers, palm and thumb boundaries.** Stage 3A owns them. No boundary from any source enters this
  track, and none is produced by it.
* **Any catalogue-scale application.** The 8,765 ESMFold models are not touched until a verdict exists.
* **Any phylogeny.** The structural-tree route is a recorded dead end; it is not re-attempted.
* **Any claim that retron catalytic architecture is distinctive.** The secondary question is
  descriptive and exploratory in this track and may not produce a confirmatory claim (§7 `g5`).
* **Any accuracy, sensitivity, precision, recall or F1 against a tool label or a motif call.**
* **Any re-derivation of the RT0–RT7 sequence frame**, and any use of it here.
* **Repairing the prior boundary extraction, Gate S, or the structural-MSA route.**

---

## 4. Inputs (with trust grades)

| input | role | trust |
|---|---|---|
| `analysis/stage3b_design/STRUCTURE_REGISTER.tsv` — 60 RT chains, 31 unique sequences | the population and its truth labels | `FROZEN` at the landing commit |
| `analysis/stage3b_design/REPLICATE_GROUPS.tsv`, `TIER_ASSIGNMENT.tsv` | the split | `FROZEN` |
| `analysis/stage3b_design/CONTROLS.tsv` | the control inventory | `FROZEN` |
| `analysis/stage3b_design/ANTICIRCULARITY_CONTRACT.tsv` | the machine-checkable input contract | `FROZEN` — unchanged by the 2026-09-18 repair |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/` — 25 entries | coordinates | `RAW` — coordinates only; the boundary files beside them are `DO-NOT-USE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign/columns/cache/cif/` — 25 mmCIF | coordinates | `RAW`, hash in `g1` |
| `/home/borg/RESEARCH-retron-db/ARIS_OUTPUT/rtelem-g2-panels/cache/rcsb_cif/` — 38 mmCIF with a hashed fetch log | coordinates, incl. the non-LTR class and the motif-positive non-RT decoys | `RAW` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign/columns_rt17/cache/cif/1RTD.cif` | HIV-1 RT nomenclature outgroup, p51 conformer control, RNase H comparator | `RAW` |
| `data/stage3b_external_structures/` — 9 mmCIF landed 2026-09-18 with sha256 | the retron evidence repair | `RAW` |
| `data/stage3b_external_structures/FETCH_LOG.tsv` | acquisition provenance | `FROZEN` |
| Nat Commun 2026;17:7374 (PMID 42270618); Nucleic Acids Res 2026;54(4):gkag111 (PMID 41665008); Mol Cell 2025 (PMID 41172990) | primary-source catalytic truth for Eco8 and the Eco8 metal attribution | `FROZEN` as quoted in the repair record |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/reference_boundaries.*` and `boundary_extraction_report.txt` | — | **`DO-NOT-USE`** — graded RED in the prior asset audit |
| `s6b_gateS_LDD.py` | — | **`DO-NOT-USE`** — three defects that inflate the null |
| `s6d_gateS_f14_exact.py` (Gate S) | comparator after the detector is frozen | `RE-DERIVE` — code reusable, no prior number is an acceptance criterion |
| `results/rt07_g4b_production_mapper/` frozen mapper and `CAT_STATE` 262 | post-freeze comparison only | `FROZEN`, forbidden as a detector input |
| the three local foldseek builds | structural superposition, if used at all | **`DO-NOT-USE`** until one build is pinned and recorded in `g1` |
| the 8,765 ESMFold models | downstream application after a verdict | `DO-NOT-USE` in `g1`–`g5` |

---

## 5. What might already exist

Measured in the design dossier; re-verified, never inherited as a number.

* **60 RT chains over 31 unique biological sequences**, with construct-to-parent offsets measured per
  chain, including three fusion constructs whose offsets are recorded (`9WY8` +398, `9HDO` +522,
  `26CZ` +108) and twelve chains with no external accession at all.
* **A motif-free truth layer already computed**: metal coordination at or under 3.2 Å, substrate
  contact at or under 4.0 Å, deposition author site records, and — added 2026-09-18 — author-assigned
  and mutational evidence from the primary literature. 15 groups `HARD_PAIR`, 2 `HARD_SINGLE`,
  1 `FUNCTIONAL_PAIR`, 1 `HARD_MULTISITE_UNRESOLVED`, 13 `NONE`.
* **The candidate space, measured**: median 2 and at most 6 aspartate carboxylate pairs at or under
  6 Å per chain; 113 within-protein decoy pairs; no compact aspartate triplet in 44 of 51 chains
  under a uniform 8 Å criterion.
* **The known failure mode**: among chains where the true pair is independently supported and
  resolvable, it is the tightest pair in 12 cases, second in 5 and third in 1 — failing
  preferentially on large multi-domain retroelement ORFs.
* **The state effect, measured**: metal-bound catalytic carboxylate separations 2.5–3.6 Å against apo
  4.2–5.0 Å.
* **Two falsification gates already run** in prior work with declared thresholds (N-terminal
  admissibility; two-algorithm secondary-structure edge agreement). Their instruments stand; their
  claims are re-derived, not inherited.
* **Prior numbers that are known wrong and must not reappear**: the 18-of-25 crystal denominator, the
  "72 structure-validated anchors" phrasing, and the claim that a YXDD-like character class is the
  field's standard. All three are recorded as killed in `analysis/prior_asset_audit/`.

---

## 6. Claims this track settles

| claim | what this track contributes | role |
|---|---|---|
| `C4` | whether catalytic-site geometry is identifiable and conserved across RT families independently of the local sequence motif, with motif variation and geometry reported as separately measurable quantities | primary |
| `C9` | whether locating the catalytic site and delimiting its residue membership are separable measurable properties, with abstention reported as its own state | primary |
| `C3` | a reproducible operational definition of the catalytic site with explicit failure and uncertainty states, usable across RT families | supporting |
| `C7` | whether disagreement between the structural detector and the motif call carries information about detector scope rather than about biology | supporting |

---

## 7. Gates

| gate | deliverable | weight | claims | stop condition |
|---|---|---|---|---|
| `cat3b_g1` population freeze | every coordinate file hashed; each accession re-verified against its in-file identity; mmCIF fetched for the 11 legacy-PDB entries; one foldseek build pinned and recorded; the eligibility cut on resolution declared; the frozen population digest | FULL | `C3` | `results/cat3b_g1_population_freeze/` exists and `run.sh` reproduces the register, the hashes and the population digest |
| `cat3b_g2` contract and thresholds | the anti-circularity checker as executable code; the declared hit, abstention and false-fire bars; the candidate-residue sequence-separation range calibrated on Tier A only; the PARTIAL scope named; the truth table landed with a transferred-truth flag on every inherited label | FULL | `C3`, `C9` | `results/cat3b_g2_contract_and_thresholds/` exists and `run.sh` reproduces the threshold table and the checker's own self-test |
| `cat3b_g3` detector development and freeze | the detector fitted on Tier A only, then frozen by digest; Tier A hit, miss and abstention rates with their own denominators; within-protein decoy performance; replicate-state agreement | FULL | `C4`, `C9` | `results/cat3b_g3_detector_freeze/` exists and `run.sh` reproduces the Tier A tables and the instrument digest |
| `cat3b_g4` held-out validation | Tier B opened exactly once against the frozen detector; hit, miss and abstention with denominators; the motif-positive non-RT controls; the p51 conformer control; the homologous-chemistry comparators; the verdict | FULL | `C4`, `C9` | `results/cat3b_g4_heldout/` exists and `run.sh` reproduces the held-out tables and the verdict from the frozen detector |
| `cat3b_g5` comparators and exploratory description | post-freeze comparison against the motif call, against Gate S and against `CAT_STATE` 262; the exploratory state-matched retron-versus-other-bacterial description, barred from a confirmatory claim | FULL | `C4`, `C7` | `results/cat3b_g5_comparators/` exists and `run.sh` reproduces the agreement and disagreement tables and the exploratory description |

**Ordering is strict.** `g4` may not begin until `g3` has landed a frozen instrument digest. `g5` may
not begin until `g4` has landed a verdict.

---

## 8. Compute

| resource | budget |
|---|---|
| GPU | **zero**. No structure prediction, no folding, no embedding |
| CPU | under one core-hour per gate. The whole population is 60 chains and the candidate space is at most 6 pairs per chain |
| network | only for `g1`: mmCIF for the 11 legacy-PDB entries, fetched through the logged, hashing pattern in `data/stage3b_external_structures/FETCH_LOG.tsv` |
| disk | under 250 MB for all coordinates; large historical assets stay in place and are read-only |
| Ibex | not required. If a structural superposition arm is later added, it runs locally on 60 chains |
| wall clock | days, not weeks; no queue |

---

## 9. Autonomy: decide-alone vs stop-and-wait

**Decide alone**

* every implementation choice inside the declared contract: candidate enumeration, feature
  computation, scoring form, tie-breaking, code structure, table and figure layout;
* the eligibility cut on resolution and the sequence-separation range, **provided both are declared in
  `g2` before any detector is fitted and neither is revisited afterwards**;
* which of the allowed features to use and which to drop, on Tier A evidence only;
* reporting a FAIL verdict, and reporting abstention rates that are higher than hoped;
* landing negative and refuting results, and recording rule defects found mid-track — as was done on
  2026-09-18 when the pair rule was found to merge two different active sites.

**Stop and wait for the operator**

* any change to `ANTICIRCULARITY_CONTRACT.tsv`;
* any movement of a threshold after `g2` has landed, for any reason;
* re-opening Tier B after `g4`, or moving any cluster between tiers;
* acquiring structures beyond the declared inclusion rule, or admitting a new RT class;
* promoting the exploratory retron comparison in `g5` to a confirmatory claim;
* any use of predicted structures before a verdict exists;
* raising a `DO-NOT-USE` grade on any input in §4.

---

## 10. What would change the predeclared expectation

Recorded so that a later PASS is earned rather than argued.

1. **A catalytic-state retron RT structure** — a ternary complex with an incoming nucleotide at the RT
   site. None exists today across six retron groups and 24 depositions searched.
2. **Ec67 site attribution** — one targeted read of the Eco2 paper would move `RG24` out of
   `HARD_MULTISITE_UNRESOLVED`, since that chain carries metal at the polymerase aspartate D202 and at
   the fused nuclease aspartate D460 and nothing in the deposition attributes either.
3. **Functional truth for Ec78, Ec83 and retron I-A** — the three remaining `NONE` retron groups.
4. **Functional truth for the six non-retron Tier C groups** — AbiK, AbiP2, AbiA, UG28, DRT6, Drt3a.

Any of these enlarges Tier B. None of them may be pursued by relaxing a bar instead.

---

## 11. Reporting discipline

* every rate carries its own denominator, and abstention is never folded into failure;
* retron, group II intron, non-LTR and viral strata are reported separately and never pooled;
* a chain whose truth was transferred from a replicate-group partner is flagged in every table it
  appears in, and a sensitivity analysis excluding all transferred truth is reported beside the main
  result;
* a detector firing on a genuine second active site of homologous chemistry — the HIV-1 RNase H
  centre, the Ec67 fused nuclease centre — is reported as a third outcome, not as a false positive;
* the motif comparison in `g5` reports agreement and disagreement in both directions and is never
  used to repair the detector;
* the Eco8 magnesium is reported as an author interpretation that is absent from every deposited
  model, and never as structural metal evidence.
