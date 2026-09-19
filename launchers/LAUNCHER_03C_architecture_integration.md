# LAUNCHER 03C — post-hoc integration of independently frozen RT architecture analyses

**Track id:** `s3c` · **Opened:** 2026-09-19 · **Branch:** `worktree-stage3c` (from Stage-3A closure
`67c137ba`) · **Autonomy:** `AUTO_PROCEED = true` within §9 · **Character:** POST HOC, DESCRIPTIVE.

Stage 3C **reads** frozen products of Stage 2, Stage 3A and Stage 3B and describes how their
vocabularies relate on the same experimental RT chains. It re-runs none of them, re-scores none of
them, and issues no combined verdict. Each upstream stage keeps its own verdict:

| upstream | frozen verdict | carried into 3C as |
|---|---|---|
| Stage 3A (`67c137ba`) | **CLOSED at FAIL** | read-only units, calls, validation, replicate and LOGO analyses |
| Stage 3B (`c0592f0`) | **CLOSED at PARTIAL**, K5 fired, Tier B never opened | Tier-A calibration evidence only (§4, §9) |
| Stage 2 (`94a1a788`, main) | **CLOSED** with residual limitations | RT0 UNRESOLVED · RT1 UNRESOLVED · RT2 PARTIAL · RT3 ESTABLISHED with qualification · RT4 ESTABLISHED with frame-instability qualification · RT5 ESTABLISHED · RT6 PARTIAL jointly with RT5 · RT7 ESTABLISHED with qualification |

Stage 3A central interpretation, carried verbatim in spirit: a label-free, externally validated
structural-domain decomposition does not reproducibly partition experimental RT structures into three
stable fingers-, palm- and thumb-like regions. **This is not a claim that those functional concepts are
biologically absent.**

---

## 1. Objective and success criterion

**Question.** How do independently defined RT sequence states, catalytic geometry, structural units and
historical retron-specific regions relate to each other, and which architectural representation is
actually reproducible across experimental retron/RT structures? **No winner is forced.** A valid
outcome is that different vocabularies describe different biological scales.

**Object.** The 62 experimental RT chains (31 biological groups) of the Stage-3A register, with their
frozen PDP units keyed by author `(chain, resnum, icode)`.

**Five comparisons**, each a separate gate (§7):

* **A** — Stage-3B catalytic Asp architecture vs Stage-3A units (Tier-A evidence scope only).
* **B** — frozen Stage-2 state system vs Stage-3A units, through the frozen production mapper.
* **C** — historical and literature fingers/palm/thumb annotations vs Stage-3A units, after a
  provenance audit of every boundary source.
* **D** — retron-specific Region X and Region Y: literature/provenance audit first, then a
  machine-readable operational annotation of the 62 chains joinable to the RT–ncRNA dataset.
* **E** — termini, insertions, fusions and additional structural units in the experimental register
  only; output is design requirements for a later fusion/accessory-domain task.

**Success criterion.** `analysis/stage3c_architecture_integration/` exists with every deliverable of
§7; `run.sh` regenerates every table and figure from the hashed frozen inputs byte-identically; every
rate carries its unit and a denominator counted twice by independent code paths (WA-D.3); every
comparison states its unmapped/unavailable cases as prominently as its mapped ones; the claim–evidence
matrix cites a frozen file and commit for every statement; and `STAGE3C_DECISION_REPORT.md` compares
the six vocabularies of §1a without declaring any of them correct.

### 1a. The six vocabularies the report compares

1. Stage-3A structural-domain units (PDP, BioJava 7.1.4, primary; BJ-p4 as sensitivity arm).
2. Stage-2 RT0–RT7 states — through frozen `state_id` blocks, never as structural-domain truth.
3. Stage-3B catalytic geometry — Tier-A truth-bearing chains only.
4. Historical/literature fingers/palm/thumb.
5. Retron-specific Region X / Region Y.
6. A conserved RT core plus variable terminal/insertion/fusion architecture.

---

## 2. Kill criteria

Written before any join. Each fires on a measurement, not on a disappointing result.

| # | condition | action |
|---|---|---|
| K1 | any Stage-3A frozen file named in §4 differs in sha256 from its blob at `67c137ba`, or `RT_PARTITION_FREEZE_sha256.txt` fails | stop; nothing downstream is computed |
| K2 | any file of `results/cat3b_g1_population_freeze` or `results/cat3b_g2_contract_and_thresholds` fails its own `OUTPUTS.tsv` hash | stop Comparison A |
| K3 | a Tier-B or Tier-C truth label, or any Tier-B detector output, enters a Comparison-A table other than as an explicitly excluded, count-only row | stop; Comparison A is void and is rebuilt, not patched |
| K4 | the frozen mapper's `check_instrument()` does not return `rtmap-1.0.0/53a1e738a19b3896` | stop Comparison B |
| K5 | **mapper positive control**: on `5G2X_C` (LtrA itself), fewer than 0.95 of the g7a-MAPPED LtrA states land on the same LtrA residue number as `g7a_state_to_residue.tsv` | stop Comparison B; report a join/numbering defect |
| K6 | **residue-key join**: for any comparison, fewer than 0.95 of the external residue positions that are modelled in the chain resolve to a key in the frozen PDP residue table | stop that comparison; report the join defect |
| K7 | a Stage-2 historical label is written onto a non-LtrA chain as if it were a measured domain, or RT0/RT1 is given any residue interval anywhere | stop; the table is withdrawn |
| K8 | Comparison C: zero literature sources yield verbatim, residue-numbered fingers/palm/thumb boundaries for any protein in the register | Comparison C reports `INSUFFICIENT_PRIMARY_EVIDENCE` and stops — no boundary is inferred |
| K9 | Comparison D: the operational X/Y rule is changed after any of the 62 chains has been scanned with it | stop; the scan is void and re-declared |
| K10 | any output would modify, re-threshold or re-interpret a Stage-2, 3A or 3B verdict | stop; that is a new task, not 3C |
| cost | CPU above 2× the §8 estimate, or any need for GPU/Ibex | stop and report the budget-halt as a budget-halt (WA-A.3) |

---

## 3. Non-goals — out of scope

* **Reopening Stage 3A**: no re-parse, re-threshold, re-classification, alternative decomposition, or
  any attempt to recover three domains. A 3A/3C disagreement is a 3C finding.
* **Recomputing Stage 2**: no re-derivation of states, anchors, profiles, crosswalks or statuses. The
  frozen mapper is **applied** to structure-chain sequences as an instrument (as g7a already did for its
  panel); nothing about it is refitted.
* **Modifying Stage 3B**: no re-estimation of catalytic pairs, no detector re-run, no threshold change,
  no Tier-B inference.
* **Inferring RT0/RT1 boundaries from structure** or from anything else.
* **Predicted-structure transfer** (the 8,765 ESMFold models are not touched).
* **Catalogue-wide fusion or domain scans**, and **catalogue-wide application of the X/Y rule**. The X/Y
  table covers the 62 chains and carries join keys plus the rule, so a later governed task can apply it.
* **ncRNA model training**, and any answer to the Region-Y pairing-specificity question beyond stating
  what evidence exists and designing the test.
* **Any combined structural-model verdict**; any inferential statistical test not declared in §7.
* **Promoting any 3C interpretation to a thesis or paper claim** (operator gate).

---

## 4. Inputs

All read-only. Paths relative to the worktree root unless absolute.

| path | what it is | trust grade |
|---|---|---|
| `analysis/stage3a_structural_core/g2r/results/rt_pdp_primary.residues.tsv` | per-residue PDP unit, 62 chains, 30,984 residues; `domain 0` = PDP-unassigned (552 residues, 15 chains), not a unit | `FROZEN:stage3a partition 76526444 / closure 67c137ba` |
| `analysis/stage3a_structural_core/g2r/results/rt_pdp_p4.residues.tsv` | BJ-p4 sensitivity-arm partition | `FROZEN:stage3a 76526444` |
| `analysis/stage3a_structural_core/g2r/results/rt_units.units.tsv`, `rt_units.calls.tsv`, `rt_units_p4.*`, `rt_units.report.txt` | unit features, palm/thumb/fingers-like roles, call status, LOGO | `FROZEN:stage3a results 891036e5` |
| `analysis/stage3a_structural_core/g2r/results/RT_PARTITION_FREEZE_sha256.txt`, `rt_pdp_implementation_sensitivity.tsv`, `rt_ss/`, `rt_ss_concordance.per_chain.tsv` | freeze hashes, implementation sensitivity, per-residue secondary structure | `FROZEN:stage3a 891036e5` |
| `analysis/stage3a_structural_core/STRUCTURE_REGISTER.tsv`, `BIOLOGICAL_GROUPS.tsv`, `closure/tables/T1_structure_register.tsv` | the 62 chains, groups, strata, fused flags, offsets, modified residues; lineage/family columns are metadata that enter 3C here for the first time (recorded transition) | `FROZEN:stage3a closure 67c137ba` |
| `analysis/stage3a_structural_core/closure/STAGE3A_CLOSURE.md`, `closure/STAGE3C_HANDOFF.md` | verdict, rules carried forward | `FROZEN:stage3a closure 67c137ba` |
| source mmCIF/PDB files named in `STRUCTURE_REGISTER.tsv` `source_file`, hashes in `file_sha256` | coordinates, for nucleic-acid contact geometry (Comparison D) and modelled sequence | `RAW` — hash re-verified before use |
| `results/cat3b_g1_population_freeze/`, `results/cat3b_g2_contract_and_thresholds/` incl. `tables/TRUTH_TABLE.tsv`, `tables/G2_TIERA_EVALUATION.tsv` | 3B population, truth, frozen detector's Tier-A output | `FROZEN:cat3b_g1, cat3b_g2` — **Tier A truth-bearing rows only** |
| same bundles, rows with `tier` = `B_heldout` or `C_no_truth_yet` | held-out/no-truth rows | `DO-NOT-USE` — 3B closure forbids Tier-B inference; counted, never placed |
| `analysis/stage3b_design/G2_DECOY_AUDIT_AND_K5_CLOSURE.md` | the permitted 3B statements and miss breakdown | `FROZEN:stage3b c0592f0` |
| `results/rt07_g4b_production_mapper/` (code, profile, params) | frozen production mapper `rtmap-1.0.0/53a1e738a19b3896` | `FROZEN:rt07_g4b_production_mapper` |
| git objects at `94a1a78868d6039297c78b3fdcc047d633d6645e`: `results/rt07_g7a_rt0_rt7_bridge/tables/g7a_state_to_residue.tsv`, `g7a_crosswalk_resolved.tsv`, `g7a_panel_results.tsv`; `docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv`; `docs/decisions/2026-09-19_stage2_closed.md`, `2026-09-19_stage2_g7a_review_errata.md` | Stage-2 closed state, read with `git show` (not an ancestor of this branch; no merge) | `FROZEN:rt07_g7a_rt0_rt7_bridge + erratum, main 94a1a788` — the erratum's `downstream_may_say` supersedes the bundle's |
| `results/rt07_pre_g4_scope_separation/tables/structure_reference_inventory.tsv` (if present) | anchor-set membership per structure (mapper independence) | `FROZEN:rt07_pre_g4_scope_separation` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/reference_boundaries.{tsv,json,py}`, `run_log.txt`, `boundary_extraction_report.txt` | historical F/P/T boundary product | `RE-DERIVE` — graded RED by `analysis/prior_asset_audit/REUSE_DECISIONS.md` §4.1; enters Comparison C **only** after the 3C provenance audit, as a separately labelled historical-product stratum, never pooled with literature and never as truth |
| primary literature retrieved in 3C (Europe PMC / PubMed / publisher full text) | verbatim statements with locator | `RAW` once quoted with locator; paraphrase without a verbatim quote is `DO-NOT-USE` |
| `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/origin_retron_data/notes/*.md`, `/home/borg/RETRON_STAGES/*.md` | prior reading notes naming Region X/Y sources | `DO-NOT-USE` as evidence — pointers to primary sources only |
| `docs/DATASET_REGISTRY.md` `rt_hash` convention (`results/dbchar_g2_canonical_units/scripts/g2lib.py`) | join-key definition for the RT–ncRNA dataset | `FROZEN:dbchar_g2_canonical_units` |

⛔ Read-only, always. Values are probed before use (WA-D.4): e.g. PDP label `0` is unassigned, not a unit.

---

## 5. What might already exist

* **The Stage-3C comparison plan** (`closure/STAGE3C_HANDOFF.md`) — adopted as the design basis for A–C;
  its rules 1–6 are binding here (read-only 3A; post hoc; strata kept; no verdict merging; join order).
* **g7a already applied the frozen mapper to structure-chain sequences** (`g7a_panel_results.tsv`:
  6AR1_A 141/150 MAPPED, 7V9U_A 63/150) and recorded that anchor-set members are NOT independent of the
  mapper. Reused as positive control and independence record; the numbers are re-measured, not inherited.
* **3B truth and detector output** exist per chain; the 19 Tier-A truth-bearing chains are the only
  valid 3B scope. Transferred truth (4 chains) is flagged in every row.
* **Historical boundaries** exist and are RED: `5HHJ` hardcoded anchor of unrecorded origin, thumb and
  fingers computed as residuals, 24/25 DSSP-vs-alignment disagreements logged, `5G2X` palm not
  containing its own catalytic dyad, same-protein 77-residue disagreements. The audit must re-verify
  these on the files, not inherit them.
* **Region X/Y**: prior notes attribute NAxxH (Region X, between RT2 and RT3) and VTG in RT7 (Region Y,
  msr recognition) to Toro & Nisa-Martínez 2014 and Mestre et al. 2020, which cite Inouye et al. 1999
  for Y. A prior claim (`D6`, Region X family-exclusivity) was withdrawn by its own authors; Region X was
  weak. ⚠ **Terminology hazard:** group-II/non-LTR "domain X" (the thumb, after RT7; Xiong & Eickbush
  1990; Blocker 2005) is a **different object** from retron "Region X" (between RT2 and RT3). Every row
  of every X/Y table names which object it means.
* **What would make these untrustworthy:** a residue-numbering offset (tag, fusion, construct) silently
  applied or not applied (`9WY8` +398, `9HDO` +522, `26CZ` +108 construct offsets are recorded in the
  register); a literature boundary quoted in a different numbering from the deposited chain; a prior
  note paraphrasing a source it never quoted.

---

## 6. Claims this task tests

| id | role in this task |
|---|---|
| `C4` | primary — descriptive, post hoc; no status change proposed without operator review |
| `C3` | supporting |
| `C9` | supporting |
| `C7` | supporting |
| `C6` | design only — Comparison D states the evidence and designs the Region-Y test; it tests nothing |

---

## 7. Gates

Deliverables land in `analysis/stage3c_architecture_integration/` (operator-named location), laid out
per `BUNDLE_SPEC` (`scripts/`, `tables/`, `figures/`, `MANIFEST.tsv`, `INPUTS.tsv`, `OUTPUTS.tsv`,
`env.lock`, `run.sh`, `README.md`, `PROVENANCE.md`) so it can be landed to `results/` unchanged later.
**Join order (handoff rule 6):** each comparison's join table is committed before its summary analysis.

| gate id | the ONE measurement | weight | settles | stop condition |
|---|---|---|---|---|
| `s3c_g0_inputs` | sha256 of every input vs its frozen record; `INPUT_PROVENANCE.tsv` | LIGHT | none — provenance | done when `INPUT_PROVENANCE.tsv` exists and `run.sh` reproduces it with K1/K2 passing |
| `s3c_gA_catalytic` | per Tier-A truth-bearing chain: fraction of catalytic truth Asp in the palm-like unit (or, if NO_CALL, the max-same-sheet-strand unit); `STRUCTURE_STAGE3B_CROSSWALK.tsv` | FULL | `C4`, `C9` | done when the crosswalk and its summary exist and `run.sh` reproduces them byte-identically |
| `s3c_gB_states` | per chain × frozen state block: mapping availability and unit membership; `STRUCTURE_STAGE2_CROSSWALK.tsv` | FULL | `C3`, `C4` | done when the crosswalk and per-block summary exist and `run.sh` reproduces them byte-identically |
| `s3c_gC_literature` | per literature region: best-matching PDP unit Jaccard; `LITERATURE_BOUNDARY_AUDIT.tsv` | FULL | `C4`, `C7` | done when the audit and overlap tables exist and `run.sh` reproduces the overlaps byte-identically |
| `s3c_gD_xy` | per chain: X/Y operational interval, motif state, nucleic-acid contact count; `XY_REGION_EVIDENCE.tsv`, `XY_REGION_ANNOTATIONS.tsv` | FULL | `C4`, `C6` | done when both tables exist and `run.sh` reproduces the annotation table byte-identically |
| `s3c_gE_termini` | per chain: N-/C-terminal extension, internal insertion and fused/extra-unit residues; `TERMINI_FUSION_SUMMARY.tsv` | LIGHT | `C4` | done when the summary and the design-requirements section exist and `run.sh` reproduces the summary |
| `s3c_g6_report` | `CONTRADICTIONS_AND_UNCERTAINTY.tsv`, claim–evidence matrix, figures from landed tables only, `STAGE3C_DECISION_REPORT.md` | FULL | `C4` | done when `run.sh` regenerates every figure TSV byte-identically from landed tables |

### 7a. Declared rules — fixed now, before any join

All thresholds below are **DECLARED** and are not moved after a join (EVIDENCE_STANDARDS §5). Each is
reported with a sensitivity sweep where one is cheap.

**Residue keys.** Author `(chain, resnum, icode)`. No offset is applied unless the register records it;
any offset used is written in the row. Residues are `IN_UNIT(k)`, `PDP_UNASSIGNED` (label 0) or
`PDP_ABSENT` (not in the PDP table) or `NOT_MODELLED`.

**Comparison A.**
* Population: Tier-A chains with `group_evidence_class` = `HARD_PAIR` and a truth set (19; 15 own-chain,
  4 transferred within replicate group, flagged). Tier-B/C rows are counted and excluded.
* Target unit = the palm-like unit when `C4` = CALL; otherwise the unit with the largest
  `max_strands_one_sheet` (tie → `TIED`, reported, not broken). This follows the handoff exactly.
* Site states: `ONE_UNIT` (all truth Asp in one unit), `SPLIT` (≥ 2 units), with discontinuity of the
  containing unit from `n_segments`.
* **Size-expected baseline** (price of the obvious alternative): the target unit's share of modelled
  residues — the fraction a residue placed at random would hit.
* Replicate stability: within replicate groups with ≥ 2 Tier-A truth-bearing chains, (i) identity of
  the truth Asp set, (ii) identity of the frozen detector prediction, (iii) residue-key Jaccard of the
  site-containing unit, (iv) unit-count agreement. Descriptive; same pairs for all four.
* The frozen detector's Tier-A predictions are joined as a separate column; HIT/MISS labels are
  3B's, unchanged. The permitted miss characterisation is the one in the 3B closure record.

**Comparison B.**
* Instrument: `rtmap-1.0.0/53a1e738a19b3896`, applied to each chain's **modelled** sequence (author
  numbering kept through an index map; chain breaks recorded, not bridged).
* State blocks = the erratum's supporting-state lists, named by the block, never by a label on a
  non-LtrA chain: `SB2p` 107–133 (17 states; historical RT2 PARTIAL), `SB3` 136–177 (22), `SB4`
  181–241 (42; frame-unstable), `SB56` 267–301 (34; joint RT5+RT6), `SB7` 310–315 (6), and
  `CAT_STATE 262` reported alone. RT0 and RT1 have **no states** and are reported as
  `NO_STATES_BY_CONSTRUCTION` on every chain.
* Block available in a chain: ≥ 0.50 of its states MAPPED. Block contained: ≥ 0.80 of its mapped
  residues in one unit; otherwise `SPLIT`, with the number of units holding ≥ 0.20. Merge: a unit that
  contains ≥ 2 blocks. Sensitivity: availability 0.30/0.70, containment 0.70/0.90.
* Independence: chains whose protein is an anchor-set member are flagged `NOT_INDEPENDENT_OF_MAPPER`.

**Comparison C.**
* A literature boundary is admitted only with a verbatim quote, a locator, the numbering system and
  the protein/construct it refers to. Statements in another numbering are converted only by a recorded
  offset; otherwise `NUMBERING_UNRESOLVED`, not used.
* Per region: best-matching unit by Jaccard; `COINCIDES` if Jaccard ≥ 0.70 (the 3A C7 bar); number of
  units holding ≥ 0.20 of the region (split); number of regions holding ≥ 0.20 of a unit (merge);
  discontinuity of region and of unit reported separately.
* Literature and the historical product are separate strata; references disagreeing on one protein are
  reported as disagreement, not averaged.

**Comparison D.**
* Order: (1) literature/provenance audit → `XY_REGION_EVIDENCE.tsv`, committed; (2) the operational
  interval and motif rule are written into `scripts/` and committed; (3) only then are chains scanned.
* Evidence classes kept apart: `EXPERIMENTAL_SEQUENCE`, `MOTIF`, `FUNCTIONAL`, `OPERATIONAL_INTERVAL`.
* Region X operational interval: residues strictly between the last mapped residue of `SB2p` and the
  first mapped residue of `SB3`; undefined if either side is unavailable. Motif states: strict
  `N-A-x-x-H`, relaxed `A-x-x-H`, else `NO_MOTIF_IN_INTERVAL` (not absence of Region X).
* Region Y operational interval and motif (VTG and I/L variants at position 1) are fixed from the audit
  in step (2); if no primary source states an experimental interval, Y is reported at motif and
  operational level only, with that status.
* Nucleic-acid contacts: protein heavy atom within 4.0 Å of a polynucleotide heavy atom in the same
  deposited entry. Positive control: reproduce 3B's `SUBSTRATE_NA` residue calls where they exist.
* Motif-scan positive control: the same scanning code recovers the 3B/literature YxDD on every
  Tier-A own-chain truth chain; negative control: 100 seeded shuffles of each interval (seed 20260919).
* Region-Y pairing-specificity is answered **only** as: what the structures show about Y–ncRNA
  contact, what the historical experiments showed, and the design of a later test.

**Comparison E.** Extensions measured from the Stage-2 mapped span (first/last mapped anchor residue)
and the register's construct/fusion records; an internal insertion is a gap between consecutive mapped
anchors exceeding the LtrA spacing by ≥ 20 residues. Expression tags/fusion partners (MBP etc.) are
separated from biological extensions using the register's recorded construct offsets.

**Statistics.** No inferential test is declared. All results are descriptive censuses over the 62
chains, stratified primary (46) / flagged (15) / design-exposed (1), with `IMPLEMENTATION_SENSITIVE`
(5) carried. Where a group-level summary is given it is counted over biological groups, and
chain-level and group-level denominators are both shown.

---

## 8. Compute

- Expected: borg CPU only, < 1 core-hour total (62 chains; mapper ~14 ms/sequence; contact geometry on
  ≤ 62 entries). No GPU, no Ibex.
- Network: literature retrieval only (Europe PMC, NCBI E-utilities, publisher full text). Nothing is
  uploaded.
- Hard stop at 2× the estimate — report, do not push through.

---

## 9. Autonomy envelope

**Auto-proceed:** `true`.

| | budget |
|---|---|
| CPU-hours | 2 |
| GPU-hours | 0 |
| max single job | 0.5 hr |
| review rounds per gate | 2 |

**Decide alone and continue** (log in `docs/BLOCKED.md`): code structure; table and figure layout;
literature search strategy; which retrieved sources qualify under §7a; declaring a source
`NOT_RETRIEVED` or `NUMBERING_UNRESOLVED`; reporting nulls, splits, unavailability and contradictions.

Three rules restated with their ids:
- **WA-A.4** — measure and report counts; do not conclude. Interpretation lands as `PROPOSED:`.
- **WA-G.5** — a null or refuting measurement is a result and lands like any other.
- **WA-S.1** — never guess silently and never stall; LOW-STAKES takes the default and continues.

**Human gate — stop and wait:**
- any change to a Stage-2, 3A or 3B frozen output, threshold or verdict;
- admitting 3B Tier-B/C truth labels into Comparison A (default: excluded);
- applying the mapper or the X/Y rule beyond the 62 chains; any predicted structure;
- any inferential test not declared in §7a;
- promoting any 3C interpretation to a thesis or paper claim;
- anything sent outside this machine.

**Stop condition for the track:** after the experimental-structure integration and report. Return for
operator review before any downstream Stage-3 task.
