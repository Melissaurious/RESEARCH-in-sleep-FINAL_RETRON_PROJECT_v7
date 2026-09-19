# Stage 3A — Structural core of experimental RT structures · CLOSURE PACKAGE

**Status: CLOSED at FAIL** under the frozen verdict rule of `g2r/G2R_PREREGISTRATION.md`, as amended by
`G2R_AMENDMENT_1.md` and `G2R_AMENDMENT_2.md`. The operator accepted the verdict. The instruments passed, so
this is not an instrument limitation. Nothing in this package re-runs a parser, a secondary-structure route or a
C4–C7 rule.

- Tables and figures come only from frozen outputs, via `closure/make_closure.py`.
- The script refuses to run if the frozen partition hashes, or any file under `g2r/results`, `g2r/tables` or
  `STRUCTURE_REGISTER.tsv`, differ from git.

**Central conclusion.** Under a label-free, externally validated structural-domain decomposition, experimental
RT structures do not reproducibly partition into three stable fingers-, palm- and thumb-like regions. A
recurrent palm-like β-sheet-containing unit is detectable in a subset of structures. It does not meet the
prespecified population-wide call-rate threshold. Fingers- and thumb-like units are sparse and unstable.

**What this does not say.** It does not say that fingers, palm or thumb do not exist biologically. It says that
they are not recovered as three reproducible structural-domain units under the tested formalism.

---

## 1 · Methods (thesis-ready)

**Structure population.**
- Sixty-two experimentally determined RT chains from 31 biological groups. A biological group is one protein,
  with one or more depositions of it.
- Methods: 50 cryo-EM and 12 X-ray chains. Resolution 1.2–3.8 Å (median 2.9 Å). 203–1265 modelled residues
  (median 415).
- These were registered with source-file hashes before analysis (`STRUCTURE_REGISTER.tsv`; Table S3A-1).
- Each chain was reduced to a single-chain coordinate extract: model 1, first alternate conformation, author
  numbering retained, ligands and water removed.
- The canonical residue index of a chain is its ordered list of residues carrying a Cα.

**Anti-circularity.** No step used any of the following:
- catalytic motifs or catalytic-site coordinates;
- Stage 3B outputs;
- Stage 2 RT0–RT7 states;
- retron family or lineage labels;
- historical domain boundaries.

The register's lineage/family columns were dropped when it was read. Two further constraints applied:
- One chain (5HHJ_A), whose parse was seen during software set-up, was designated design-exposed. It was
  excluded from the primary population.
- The secondary-structure content of the population had been seen during an earlier step (g1). The palm,
  thumb and fingers thresholds were taken from textbook descriptions of the right-hand polymerase fold and
  were not fitted. This exposure is disclosed as a limitation.

**Structural-domain decomposition (C3r).**
- Tool: the PDP algorithm (Alexandrov & Shindyalov 2003) as implemented in BioJava 7.1.4
  (`LocalProteinDomainParser`), with all library constants unmodified.
- Provenance: the binary and source jars match their Maven Central checksums.
- How it works: PDP recursively splits a chain where the inter-part contact density is minimal. Contacts are
  graded on Cβ, with virtual Cβ built where absent.
- Normalisation: the split step uses size exponent α = 1.3/3 ≈ 0.43. This is corroborated by DDOMAIN (Zhou
  et al. 2007); the merge step uses different exponents. The original PDP paper could not be accessed, so the
  instrument is described as BioJava's port of PDP.
- What is not imposed: no domain number, no contiguity requirement and no merge threshold. Discontinuous
  domains are retained as sets of segments.
- Driver checks: the driver enforces a single model, a single chain and unique residue keys. It emits a
  lossless per-residue assignment.
- Omitted residues: BioJava drops HETATM-modified residues (PTR, CSX) from its input. These are reported as
  unassigned.
- Known translation defects in the BioJava port were disclosed. A variant with four unambiguous index fixes
  (BJ-p4) was run as a sensitivity arm only; it could neither rescue nor veto the primary instrument.

**External validation of the decomposition.**
- Before any RT partition was generated, the parser was scored against CATH (release 2025-01-13).
- Benchmark: 100 chains, stratified 30/30/25/15 by 1–4 CATH domains. Selection was deterministic
  (sha256-ordered), with X-ray ≤ 2.5 Å, S35 representatives and one chain per entry.
- Exclusions: any chain whose domains belong to polymerase, reverse-transcriptase, maturase or retron nodes,
  and any chain with a structural hit to an RT chain (e ≤ 10⁻³ or TM ≥ 0.50). The screen excluded 0 of 260
  candidates.
- Thirty-three benchmark chains contain a discontinuous CATH domain.
- Overlap = the maximum-intersection one-to-one domain matching ÷ residues assigned by CATH.
- Six gates were frozen in advance; all six were required:

  | gate | measure | bar |
  |---|---|---|
  | A | domain-count agreement | ≥ 0.60 |
  | B | CATH single-domain chains parsed as one domain | ≥ 0.70 |
  | C | multi-domain chains parsed as ≥ 2 domains | ≥ 0.60 |
  | D | median overlap in count-correct chains | ≥ 0.80 |
  | E1 | discontinuous multi-domain chains parsed as ≥ 2 | ≥ 0.60 |
  | E2 | median overlap over discontinuous chains | ≥ 0.70 |

**Secondary structure.**
- Route A: mkdssp 4.5.5. It reproduced 26/26 historical mkdssp outputs identically.
- Route B: pydssp 0.9.1, an independent implementation. Chain breaks were enforced by padding with
  non-bonding spacers.
- Both routes read the same atoms and use the same 3-state mapping: {H,G,I}→H, {E,B}→E.
- Chain gate: coverage ≥ 0.95 and Cohen's κ ≥ 0.70 for both strand and helix.
- Population gate:
  - median κ ≥ 0.75, and median recall and precision ≥ 0.80, for both states;
  - ≥ 90 % of chains passing the chain gate.

**Unit classification (C4, C5, C4b).** Secondary-structure elements were built on the whole chain from
route A, split at chain breaks, then assigned to PDP units.
- **Palm-like (C4):**
  - ≥ 4 strands carrying one mkdssp sheet label;
  - strand fraction ≥ 0.20 and helix fraction ≥ 0.15;
  - a tie between units → AMBIGUOUS;
  - ≥ 70 % of its route-A strand residues also strand in route B.
- **Thumb-like (C5):**
  - a non-palm unit with helix fraction ≥ 0.60 and strand fraction ≤ 0.10;
  - ≥ 3 helices of ≥ 8 residues;
  - ≥ 20 Cα–Cα pairs ≤ 8 Å with the palm-like unit.
- **Fingers-like (C4b):**
  - a non-palm unit that does not meet the thumb criteria;
  - a β-hairpin: two strands with the same sheet label, ≤ 8 residues apart and directly bridge-paired;
  - ≥ 1 helix of ≥ 8 residues;
  - ≥ 20 contacts with the palm.
  - Fingers were never defined as the residual of palm and thumb.
- Thumb and fingers were evaluated only when a palm-like unit was called.
- **Call outcomes:** exactly one qualifying unit → CALL; more than one → AMBIGUOUS; none → NO_CALL.
- **Call rate:** CALLs ÷ all chains in the population. Every abstention counts as not called.

**Recurrence (C6) and replicate stability (C7).**
- **C6** uses the pinned all-vs-all Foldseek 10.941cd33 TM-align alignments. Their identity to the g2
  alignments was asserted: 3844/3844.
  - For chain pairs from different groups with min(qTM, tTM) ≥ 0.50: recurrence = the fraction of the query
    unit's residues aligned into the target's unit of the same type.
  - Values were averaged within each group pair; the median was taken over group pairs.
  - RECURRENT: median ≥ 0.50 over ≥ 10 group pairs.
- **C7** is the Jaccard of same-type units between replicate chains of a group, on shared residue keys.
  - A call in one replicate only scores 0.
  - Values were aggregated by the median over groups.
  - STABLE: median ≥ 0.70 over ≥ 5 groups.
- A region met its bar only if all three held: call rate ≥ 0.70, RECURRENT and STABLE.

**Populations and verdict.**
- **Primary population:** 46 chains. This excludes the 15 flagged chains and the design-exposed chain.
  - Flagged means >1 UniProt accession mapped to the chain, construct length >1.6 × modelled length, or >600
    modelled residues.
  - Flagged chains were analysed identically and reported as a separate stratum.
- **Stage verdict:**
  - PASS: all three regions meet their bars.
  - PARTIAL: one or two regions meet their bars.
  - FAIL: no region meets its bar.
  - INSTRUMENT_LIMITED: an instrument gate failed.
- **Leave-one-biological-group-out (LOGO)** was run as an influence analysis. No parameter was fitted to RT
  data.

**Review.** The design and code were reviewed independently (Codex) in three rounds before any outcome
existed; the final round returned CLEARED_TO_RUN. The reviewer was never shown expected
fingers/palm/thumb boundaries. Every design change was frozen in a commit before the outcome it could affect.

## 2 · Results (thesis-ready)

**The decomposition instrument passed external validation, but narrowly** (Table S3A-2, Fig. S3A-1).

| gate | measure | value | bar |
|---|---|---|---|
| A | domain-count agreement | 0.610 | 0.60 |
| B | single-domain chains parsed as one | 0.733 | 0.70 |
| C | multi-domain chains parsed as ≥ 2 | 0.886 | 0.60 |
| D | median overlap, count-correct chains | 0.993 (n = 61) | 0.80 |
| E1 | discontinuous chains parsed as ≥ 2 | 0.939 | 0.60 |
| E2 | median overlap, discontinuous chains | 0.849 | 0.70 |

- Errors ran in both directions: 8/30 single-domain chains were over-split, and over- and under-splitting
  occurred among multi-domain chains.
- The BJ-p4 variant also passed all six gates.

**Secondary structure was reliable** (Table S3A-3, Fig. S3A-2).
- mkdssp and pydssp agreed with median κ 0.986 for strand and 0.981 for helix.
- The per-chain minima were 0.846 and 0.925.
- All 62 chains passed the chain gate, with coverage 1.000.

**RT chains decompose into variable, often discontinuous units** (Table S3A-4, Fig. S3A-3, Fig. S3A-5).
- The 46 primary chains yielded 139 units, 1–5 per chain (median 3).
- **48/139 units (35 %) are discontinuous.**
- Flagged chains yielded more units (2–8 per chain; 38/78 discontinuous).
- Four modified residues were omitted by the parser: 7R06_A 44 PTR, 8C8J_A 661 CSX, 9Z6Y_H/9Z6Z_H 650 PTR.
- This agrees with the earlier, independent g2 contact-graph analysis:
  - the natural module number was 3 in only 5 % of chains;
  - 0 of 186 forced three-way modules were a single contiguous span.

**The partition is not replicate-stable** (Table S3A-7, Fig. S3A-6). In 13 groups with ≥ 2 depositions,
**replicate chains of the same protein received the same unit count in only 38.5 % of primary pairs (20/52)**.
In flagged groups the figure was 0/12.

**No region meets its prespecified bars** (Tables S3A-5 and S3A-6, Fig. S3A-4).

| region | call rate (n = 46) | recurrence (C6) | replicate stability (C7) |
|---|---|---|---|
| palm-like | **0.565** (26 CALL, 19 NO_CALL, 1 AMBIGUOUS) | RECURRENT, median 0.798 (35 group pairs) | STABLE, median 0.798 (8 groups) |
| thumb-like | 0.130 | UNDERPOWERED, median 0.000 (7) | NOT_STABLE, median 0.000 (5) |
| fingers-like | 0.304 | UNDERPOWERED, median 0.721 (8) | NOT_STABLE, median 0.000 (5) |

- The palm-like unit meets the recurrence and stability bars and misses only the call-rate bar, 0.565 against
  0.70.
- Where the palm-like unit is called, it is usually discontinuous (19/26).
- Thumb- and fingers-like units were not evaluable in the 20 chains without a palm call.
- **No chain was instrument-limited.**

The stage verdict is therefore **FAIL**.

**The verdict is robust** (Table S3A-8).
- **LOGO:** the **FAIL verdict survives all 22 leave-one-group-out analyses**. No fold changes any region's
  outcome.
  - Palm-like call rate: 0.500–0.650.
  - Palm C6 median: 0.778–0.831.
  - Palm C7 median: 0.628–0.968.
- **Fixed-code parser:** the **BJ-p4 parser gives the same verdict and identical primary-population
  statistics**. It partitions differently from the primary parser in 5/62 chains, which remained in all
  denominators (Table S3A-8b).
- **Fused/large chains (n = 15):** FAIL, with palm-like call rate 0.467 and recurrence and stability
  underpowered.
- **Pooled non-exposed chains (n = 61):** FAIL, with palm-like call rate 0.541.
- **Units unique to their group:** 26/219 units align to no other group. Of these, 18 are in flagged chains,
  consistent with accessory or fused content.

**Descriptive observation, made after the freeze and not acted on.** In 17 of the 19 primary chains with no
palm call, some PDP unit carries ≥ 4 same-sheet strands, but that unit is too large and too helix/coil-rich to
reach 20 % strand content. The β-sheet is present, but PDP does not isolate it as a compact unit in those
chains.

## 3 · Limitations and discussion

1. **The instrument sits close to its acceptance bar.** Count agreement (0.610) and single-domain fidelity
   (0.733) pass narrowly. PDP both over- and under-splits, and its unit count is not replicate-stable on RTs
   (38.5 %). Any unit-level statement beyond the palm-like unit is therefore limited by the decomposition
   itself, not only by biology.
2. **One formalism was tested.**
   - PDP optimises contact-density cuts. Other domain definitions could partition RTs differently:
     evolutionary units, hinge or dynamic domains, or CATH/SCOP-curated conventions.
   - Under the operator's instruction no alternative decomposition was run. The result is specific to
     label-free, size-normalised contact-density decomposition.
3. **The region classifiers are heuristics.** Palm-, thumb- and fingers-like are textbook-derived "-like"
   rules, not validated annotations.
   - Raw Cα-contact counts depend on unit size.
   - The fingers rule requires a bridge-paired hairpin plus a helix, which some fingers subdomains may lack.
   - The thumb rule requires a ≥ 60 % helical unit contacting the palm.
4. **Secondary-structure blinding was incomplete.** The population's secondary-structure content was seen
   before the thresholds were written. They were not fitted, but they were not blind.
5. **The palm-like result is conditional.**
   - Recurrence (0.798) is computed only over pairs in which both chains are called. Prevalence is carried
     separately by the call rate.
   - Stability rests on 8 groups.
   - Most called palm-like units are discontinuous, so a contiguous "palm interval" is not implied.
6. **Population structure.**
   - The 31 groups form one structural fold; LOGO addresses this as influence, not independence.
   - Fifteen chains are fused or large and are analysed separately.
   - Cryo-EM dominates the population (50/62).
7. **The parser omits modified residues.** Four residues are affected. The code disclosed the loss and the
   sequence gaps it creates.
8. **Interpretation.** The data are consistent with a conserved β-sheet core that a contact-density parser
   isolates only sometimes. They are also consistent with helical and fingers elements that do not form
   compact, separable units under this formalism. They do **not** show that fingers or thumb are absent, that
   the classical model is wrong, or that the palm is universal. Whether the conventional annotations align
   with the structural units that were found is a post-hoc question for Stage 3C.

## 4 · Final tables

All tables are in `closure/tables/` (TSV). `ALL_TABLES.md` holds the rendered versions.

| table | file | content |
|---|---|---|
| S3A-1 | `T1_structure_register.tsv` | 62 chains: group, method, resolution, modelled length, gaps, fused flag, modified residues, stratum, unit count, implementation sensitivity, SS gate |
| S3A-2 / 2b | `T2_parser_validation.tsv`, `T2b_parser_confusion_primary.tsv` | CATH gates A–E2, primary and BJ-p4; CATH→PDP count confusion |
| S3A-3 | `T3_secondary_structure_validation.tsv` | E/H κ, recall, precision, chain-gate fraction, per-chain minima |
| S3A-4 | `T4_unit_counts_discontinuity.tsv` | units per chain, discontinuous units (48/139 primary), palm discontinuity, EXTRA_DOMAIN |
| S3A-5 | `T5_call_rates.tsv` | palm/thumb/fingers call rates and status counts by stratum |
| S3A-6 | `T6_recurrence_stability.tsv` | C6/C7 medians, n, status, bar outcome by stratum |
| S3A-7 | `T7_replicate_instability.tsv` | per-group replicate unit counts and pair agreement |
| S3A-8 / 8b | `T8_fusion_and_sensitivity.tsv`, `T8b_implementation_sensitive_chains.tsv` | flagged/pooled strata, BJ-p4, LOGO ranges; the 5 implementation-sensitive chains |

## 5 · Claim–evidence matrix

Commits referenced below:

| commit | content |
|---|---|
| `03cf6f15` | g0–g2 checkpoint |
| `ee49f57e` | pre-registration |
| `4aeb2181` | amendment 1 |
| `efb1eadf` | amendment 2 |
| `6f37711e` | instrument gates |
| `76526444` | RT partition freeze |
| `891036e5` | C4–C7 results |

Paths are relative to `analysis/stage3a_structural_core/`.

| # | claim | evidence (frozen file) | commit |
|---|---|---|---|
| 1 | Criteria, thresholds and verdict rule were fixed before outcomes | `g2r/G2R_PREREGISTRATION.md`, `G2R_AMENDMENT_1.md`, `G2R_AMENDMENT_2.md`; `g2r/review/CODEX_REVIEW_R1–R3.md` | ee49f57e, 4aeb2181, efb1eadf |
| 2 | The parser is unmodified BioJava 7.1.4 PDP with α = 1.3/3 in the split step | `g2r/tables/biojava_classpath_sha256.txt`, `biojava_7.1.4_domain_src_sha256.txt`, `g2r/review/biojava_7.1.4_domain_src/Cut.java` | 4aeb2181 |
| 3 | The parser passed external CATH validation, narrowly (A 0.610, B 0.733) | `g2r/results/cath_score_primary.gates.tsv`, `.per_chain.tsv`; `g2r/tables/cath_benchmark_final.tsv` | 6f37711e |
| 4 | The benchmark is structurally screened against RTs (0/260 excluded) | `g2r/tables/cath_screen_hits.tsv`, `cath_benchmark_candidates.tsv` | 4aeb2181 |
| 5 | Secondary structure is reliable (κ E 0.986, H 0.981; 62/62) | `g2r/results/rt_ss_concordance.gate.tsv`, `.per_chain.tsv`, `g2r/results/rt_ss/` | 6f37711e |
| 6 | The RT partition was frozen before C4–C7 | `g2r/results/RT_PARTITION_FREEZE_sha256.txt`, `rt_pdp_primary.*` | 76526444 |
| 7 | 48/139 primary units are discontinuous | `g2r/results/rt_units.units.tsv` (n_segments); `closure/tables/T4` | 891036e5 |
| 8 | Replicate unit-count agreement is 38.5 % (20/52 primary pairs) | `g2r/results/rt_units.report.txt`; `closure/tables/T7` | 891036e5 |
| 9 | Palm-like: call rate 0.565 < 0.70; RECURRENT 0.798; STABLE 0.798 | `g2r/results/rt_units.report.txt`, `rt_units.calls.tsv` | 891036e5 |
| 10 | Thumb-like (0.130) and fingers-like (0.304) are sparse and not stable | same | 891036e5 |
| 11 | No chain was instrument-limited | `g2r/results/rt_units.calls.tsv` (no INSTRUMENT_LIMITED status); `rt_ss_concordance.per_chain.tsv` | 891036e5 |
| 12 | FAIL survives all 22 LOGO folds; no region's outcome flips | `g2r/results/rt_units.report.txt` (LOGO section) | 891036e5 |
| 13 | The fixed-code parser gives the same verdict | `g2r/results/rt_units_p4.report.txt`, `rt_pdp_implementation_sensitivity.tsv`, `cath_score_p4.gates.tsv` | 891036e5 |
| 14 | Fused/large chains also FAIL; their unique units concentrate there (18/26) | `g2r/results/rt_units.report.txt` (flagged), `rt_units.units.tsv` (EXTRA_DOMAIN) | 891036e5 |
| 15 | No motif, Stage 3B, RT0–RT7, family or historical-boundary input was used | `g2r/scripts/g2r_units.py` (allowlist), Codex R2 §F4 statement | efb1eadf |
| 16 | Independent g2 contact-graph modularity also fails to give three contiguous modules | `DECISION_REPORT.md` §1, §3; `tables/g2_C1_natural_k.tsv`, `g2_segmentation_curve.tsv` | 03cf6f15 |

## 6 · Figures

All figures are in `closure/figures/` and are regenerated by `make_closure.py` from frozen outputs only.

| figure | file | content |
|---|---|---|
| S3A-1 | `F1_parser_validation.png` | CATH→PDP domain-count confusion; gates A–E2 against frozen bars |
| S3A-2 | `F2_ss_concordance.png` | per-chain κ for strand and helix, mkdssp vs pydssp, with gate lines |
| S3A-3 | `F3_units_discontinuity.png` | units per chain (primary vs flagged); discontinuous fraction of all and palm-like units |
| S3A-4 | `F4_call_rates_logo.png` | palm/thumb/fingers call rates with LOGO ranges and the 0.70 bar |
| S3A-5 | `F5_unit_maps.png` | linear maps of every chain's PDP units, with palm/thumb/fingers-like calls coloured |
| S3A-6 | `F6_replicate_unit_counts.png` | replicate unit counts per biological group |

Recommended main-text figure: S3A-5 with S3A-4 as an inset. The others are supplementary.
