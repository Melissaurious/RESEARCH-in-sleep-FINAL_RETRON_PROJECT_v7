# DECISION — Stage-2 g4 design amendment: from "per-block calls" to a portable region detector

Date: 2026-09-16 · Track: `rt07` · Status: **binding for `launchers/LAUNCHER_02_rt0_rt7_definition.md`**

**Decided by:** operator (Melissa Rios), 2026-09-16, after `rt07_g1`, `rt07_g2` and `rt07_g3`
landed and before `rt07_g4` was started. No g4 number existed when this was written.

Supersede this record by a new record, never by rewriting it.

---

## 1 · What g2 established

`results/rt07_g2_reference_reconstruction/` (REPRODUCIBLE):

- Applying the Xiong & Eickbush criterion verbatim to `ALIGN_000044` — the alignment Zimmerly
  2001 adjusted its inherited labels against — yields **81 conserved positions** and **six
  conserved regions** at the reporting point declared before any block was counted.
- The regions are **positionally reproducible**: 5 of 6 have one-to-one counterparts in an
  independent MAFFT re-alignment at **median Jaccard 0.955**.
- The **count is not**: seven blocks occur at isolated parameter values only, the independent
  frame returns seven where the primary returns six, and block count never separates from a
  column-permutation null at any gap tested (p = 0.6965 at the reporting point). Two spatial
  statistics do separate (largest gap, gap CV; both p = 0.0050).
- Landmarks recovered: the catalytic Y/FxDD in region 5, and the widest inter-region gap where
  the source describes the variable 4/5 spacer (5–185 residues against a published 1–179).
- **RT0 was not created.** The claim that defines subdomain 0 is cross-class and is
  `NOT_TESTABLE_ON_SUBSTRATE` on a group II intron alignment.

## 2 · What g3 established

`results/rt07_g3_prior_method_replication/` (REPRODUCIBLE):

- Prior landmarks are **real positions**: 27 of 28 landmark placements across four prior
  frames fall inside an independently reconstructed g2 region, and prior RT5 lands on the
  catalytic region g2 located without it.
- **The seven-way partition does not survive reconciliation**: prior RT5 (LtrA 308) and RT6
  (LtrA 344) fall inside the *same* g2 region, and only 4 of 28 prior frame blocks were fixed
  by a published motif — the other 24 were `order_interpolated`.
- **Frames are coordinate systems, not independent determinations**: 6 of 7 landmarks sit at
  the identical LtrA residue in every prior frame; `RT17_CORE.hmm` is byte-identical to
  `B_span17.hmm`.
- **RT0 was never measured on the RT0 region**: the prior frame spans LtrA 53–361 and begins
  14 residues downstream of the conserved RT0 alanine at LtrA 39, which g2's region 1 (39–61)
  covers. Verdict `OBJECT_MISMATCH`.
- **RT1 is the only landmark that moves between frames** (0.75 against a declared 0.90 bar),
  and it maps into the region Blocker assigns to RT0. Interpretation remains deferred.

## 3 · The corrected lineage of all167, anchors72, GOLD171, ph38 and CAND95

Landed in `results/rt07_pre_g4_seed_provenance/` and summarised here.

### `all167.faa` — the old seed

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign/step3_hmm/cache/all167.faa`
sha256 `48d48faadcc82434479459cfd492c92809a641a335764920cb16baa7a5d72c2d`,
**167 sequences, 167 unique** = 42 `RETRON_*` + 26 `PDB_*` + 4 `UNIPROT_*` + **95 `CAND_*`**.

### `anchors72` — built, not accidental

42 `RETRON_*` selected from `support.csv` on **measured RT-DNA activity**
(`RTDNA_DEMONSTRATED >= 0.10`), 26 `PDB_*` from RCSB, 4 `UNIPROT_*` from UniProtKB.
Tier A = 26 `A_experimental_structure`; Tier B = 46 `B_characterised_protein`.

> ⛔ **Correction to how g3 phrased it.** `anchors72 = 72/72 of the seed` is **true by
> construction** — the seed was assembled as anchors72 plus candidates — and must **not** be
> described as an accidental contamination discovery. g3's *measurements* stand; the framing
> is corrected here. What is genuinely circular is the **downstream reuse of seed components
> as purported independent validation material**, which is a different and real defect.

### GOLD171 — a retron literature challenge panel, not general RT ground truth

171 unique retron proteins from the Mestre-derived / `support.csv` literature lineage.
44 are exact-sequence seed members, 127 are not. **The overlap is not random**: it routes
through the activity-demonstrated `support.csv` members, so removing the 44 changes the
*evidence composition* of the panel, not just its size.

> ⛔ The 127 remainder may **not** be called a clean held-out gold set. GOLD171 is a
> **retron-specific literature challenge population**. Results are reported for all 171 and,
> separately, for the 44, the 127, and the activity strata.

### ph38 → the 26 PDB anchors — the lineage is a CONTRAST, not a feed

`anchors/tables/ph38_anchor_reassignment.tsv` (24 rows, 13 columns) re-derived each ph38
crystal's family from the *same chain* ph38 used and re-scanned it against the frozen Stage-2
model set (`a10_local_crystal_recheck.py`, then `a13_balance_report.py`).

⚠️ **Correction to the assumption that the 24 re-scanned entries "contributed to" the 26 PDB
anchors.** They did not feed it. Measured:

- **6 of 24 disagree** with ph38's own family labels (18 `agree`, 3 `AMBIGUOUS (margin<20)`,
  2 `MISASSIGNED`, 1 `NON-MEMBER`). `ANCHOR_SET.md`: *"UG3's only crystal anchor is in fact a
  retron, and UG17's is a DGR."*
- The 26 PDB anchors were recruited **independently** from RCSB sweeps
  (`a11_build_anchor_set.py` reading `a8_family_assignment.tsv`); `a11` never reads the ph38
  table. **Only 10 PDB IDs are shared** between the 24 and the 26.
- The single channel by which the old crystal set touches the new anchors is metadata
  (`structure_dyad_pos`/`structure_dyad_motif`) on 12 of 72 rows, which does not gate.
- **5G2X (LtrA) enters the 26 *because of* this audit** — it is the one crystal ph38 did not use.

So ph38's role was to **invalidate** the old panel's labels and justify rebuilding, not to
supply members.

### CAND95 — resolved, and structure-selected

`CAND_<family>_<cd-hit cluster>` ids are minted by
`columns_rt17/followup/scripts/f3a_recruit.py`; the mapping table is
`columns_rt17/followup/tables/f3a_candidates.tsv` (129 recruited, 95 survive).

- **Original identifier:** an `rt_hash` corpus sequence hash. **No NCBI or UniProt accession
  exists for these sequences** — the deepest identifier available is `rt_system_id` + assembly.
- **Source:** `stage2_rt/cache/ph4/dedup_501k.fasta` — the 501,561-sequence deduplicated
  corpus, **the same lineage as the Stage-1 catalogue**, which is why all 95 are exact
  Stage-1 members. Upstream databases: ncbi_bacteria 61, gtdb_bacteria 25, mgnify_human_gut 4,
  gem 3, mgnify_soil 2.
- **Selection:** `tier_variantB ∈ {COMPLETE, COMPLETE_MOSAIC}`, not clipped, 200–900 aa,
  cd-hit at 50%, the K largest clusters per coverage tier (6 `RT7_DISSENTER` / 4 `THIN` /
  3 `BY_CONSTRUCTION`). **No bit score and no e-value.** 34 families, lengths 250–896 aa.
- ⛔ **Annotation existed before inclusion.** Every CAND arrived carrying Stage-2 palm-HMM
  **domain boundary coordinates** (`palm_qs_frozen`/`palm_qe_frozen`/`palm_cov_frozen`), a
  catalytic `xxDD` motif string and a family call. The seed expansion was **not**
  annotation-free.
- ⛔ **The 95 were kept by a STRUCTURAL gate** (`f3c_validate.py` G1–G5: ≥3 crystal donors at
  TM ≥ 0.5, mean pLDDT ≥ 70, Asp/Asp/basic chemistry, motif order, ±2 probe agreement) over
  ESMFold models. **The old seed's expansion is structure-selected**, which is an additional
  reason it may not seed a sequence-defined instrument in g4.

Per-sequence detail: `results/rt07_pre_g4_seed_provenance/tables/preg4_cand_provenance.tsv`
(95 rows, code-level provenance established for 95/95).

### What the old seed was FOR, in its builders' own words

`step3_hmm/scripts/h1_seeds.py`: seed **A** = anchors only (72), *"the 95 structurally
validated representatives stay fully held out, so A is the BENCHMARK seed"*; seed **B** =
expanded (167), *"the 95 are training data here, so B is only ever scored leave-family-out"*.
**`RT17_CORE.hmm` is a byte-identical copy of `B_span17.hmm` — it is the 167-sequence model**,
so every number quoted on it is a number on a model that saw all 95 candidates. The
prior work knew this and said so; the defect is downstream, where seed members were reused as
validation.

### The balanced 25

`in_balanced_core` is a **column, not a file** (24 tier-A structures + `UNIPROT_F2K1V9`).
**No model anywhere was built from the 25.** Every prior model is seeded from 72, from 167,
from a family slice of 167, or from a leave-out of 167.

### Measured leakage of the old seed into every population g4 might use

| population | n | exact duplicates of seed members | ≥90% identity | ≥70% |
|---|---|---|---|---|
| `ALIGN_000044` (g2 substrate) | 66 | **1** | 1 | 2 |
| Toro 2014 | 742 | 0 | 1 | 9 |
| myRT reference | 1,844 | 0 | **29** | 63 |
| GOLD171 | 171 | 44 | 47 | 47 |
| `anchors72` | 72 | 72 | 72 | 73 |
| **Stage-1 exact-RT catalogue** | 501,561 | **146** | **162** | 163 |

Two of these change the design:

1. ⛔ **The one sequence shared between the old seed and `ALIGN_000044` is `PDB_5G2X_3`, which
   is exactly `L.l.` — LtrA.** LtrA is the protein g2 and g3 use as the shared coordinate
   carrier. **LtrA therefore cannot be both the coordinate system and an independent
   structural test**, and is excluded from the PDB held-out arm.
2. ⛔ **146 of 167 old-seed sequences — including all 95 CAND — are exactly present in the
   frozen Stage-1 catalogue, and 162 are ≥90% identical to something in it.** Any Stage-1
   sample drawn for g4 must be filtered against the old seed by identity, not only by hash.

### Prior models

488 profile HMMs were found under the audited trees: **38 built from all167**, 42 from
anchors72, 1 from RETRON_SEED's 1,500, 1 from Toro 742, 1 from the 24 re-scanned crystals.
**43 ship under a name they do not declare.** All are `PRIOR / AUDIT / COMPARATOR`.

## 4 · Statements superseded

| superseded statement | where it came from | replacement |
|---|---|---|
| "anchors72 is 100% seed-contaminated" as a *discovery* | g3 framing | true by construction; the real defect is downstream reuse as validation (§3) |
| "127 gold-panel members are a clean held-out population" | g3 handoff | GOLD171 is a retron literature challenge arm, reported in four strata (§3, §E) |
| "calibrated per-block call performance" as g4's object | launcher §7 | the portable region detector of §5 |
| "the anchor construction is unresolved" | `/home/borg/RETRON_STAGES/02_rt0_rt7_definition.md` | resolved and documented; that file is a non-authoritative archive and is corrected in place with a pointer here |
| RT0 occupancy values of any kind | prior project | no RT0 occupancy may be carried forward (g3 `OBJECT_MISMATCH`) |

### 4a · Archive correction that could NOT be applied in place

The operator asked for `/home/borg/RETRON_STAGES/02_rt0_rt7_definition.md` to be corrected as a
non-authoritative planning archive. **It could not be written: that path is mounted read-only
in this environment** (`OSError: [Errno 30] Read-only file system`), and its byte-identical
twin `general/RETRON_STAGES/02_rt0_rt7_definition.md` sits inside the governance submodule,
which a session may propose to change but never amend.

The intended correction is therefore recorded here and nowhere else, and the archive file still
carries its stale text. Anyone reading that file should apply this:

1. **The anchor construction is not unresolved.** `anchors72` = 42 `RETRON_*` on measured
   RT-DNA activity (`RTDNA_DEMONSTRATED >= 0.10`) + 26 `PDB_*` + 4 `UNIPROT_*`; `all167` =
   `anchors72 + 95 CAND_*`, so "72/72 of the seed" is true by construction.
2. **A stable seven-way partition is not established** — six positionally reproducible regions,
   block count indistinguishable from a permutation null, prior RT5 and RT6 inside one region.
3. **No RT0 occupancy may be carried forward** — `OBJECT_MISMATCH` in g3.
4. **`VOID_DO_NOT_CITE.md` does not exist on disk** though six documents reference it.

**Operator action required** if the archive is to be corrected in place: remount that path
writable, or apply the banner from a session that can write there.

## 5 · The revised scientific object of g4

> **A portable sequence-based operational detector of independently reconstructed conserved RT
> regions, returning region placement, call state, boundary uncertainty and calibrated
> evidence where calibration is supportable. Historical RT0–RT7 labels are mapped onto these
> operational regions and are not imposed as seven output segments.**

Binding consequences:

- **Do not manufacture seven regions.** g2 recovered six at its reporting point; the count is
  not established, and no region is split because inherited terminology has two labels there.
- Historical RT0–RT7 is a **separate mapping layer** with cardinalities `1:1`, `1:many`,
  `many:1`, `none`, `unresolved`.
- **RT0 stays analytically separate** and may be `OUT_OF_FRAME`.
- **RT1 remains explicitly uncertain and may not be rescued by threshold tuning.**
- The frame originates in the **g2 reconstruction and primary derivational evidence**, never
  by inheriting all167 or the interpolated prior boundaries.

## 6 · The revised validation architecture

Four arms, never pooled, each with its own denominator:

1. **Historical reconstruction arm** — `ALIGN_000044` and derivational primary material.
   Defines the regions. **Not a validation population.**
2. **PDB experimental-structure arm** — the 26 structural anchors, usable as an independent
   structural challenge **only if wholly excluded from derivation, fitting, threshold
   selection and calibration**. LtrA (`PDB_5G2X_3`) is excluded from this arm because it is
   the coordinate carrier. Construct tags and offsets are recorded and native coordinates
   mapped before any boundary comparison.
3. **GOLD171 retron literature challenge arm** — reported for all 171 and separately for the
   44 seed-overlapping, the 127 non-seed, and the activity strata. Measures transfer within a
   retron/Mestre-derived lineage, **not universal RT generalisation**.
4. **Stage-1 family/identity generalisation arm** — a bounded, family-stratified sample.
   **No full 501,561 pass in g4.** Leakage measured by identity and coverage, not exact
   duplicates alone; old-seed members and their near neighbours excluded by identity.
   Family-held-out results are reported as **transferability/stability**, never as accuracy,
   unless independent boundary truth exists for that population.

Confidence is **decomposed**, never one number: detection evidence · boundary uncertainty ·
out-of-distribution context (nearest derivation identity/coverage, family seen/unseen,
calibration scope). No probability is called calibrated outside the population it was
demonstrated on. The call-state vocabulary of launcher §7a is unchanged.

## 7 · Revised reusable deliverables

g4 lands at minimum: `operational_region_definitions.tsv`,
`historical_to_operational_mapping.tsv`, `validation_population.tsv`, `sequence_lineage.tsv`,
`leakage_audit.tsv`, `method_comparison.tsv`, `thresholds.tsv`, `calibration.tsv`,
`boundary_uncertainty.tsv`, `family_holdout_or_transferability.tsv`, and a **versioned
portable detector package** (`models/rt_regions_v1/`) containing the frozen model artifacts,
coordinate definitions, thresholds, calibration scope, usage code and `MODEL_CARD.md`.

The requirement is the **portable instrument**, not a preselected implementation: filenames
are not forced to any method. The detector must accept an unseen RT amino-acid sequence and
return, per region: call state, start, end, length, normalized position, detection
evidence/confidence, boundary uncertainty, method/model version, inspectability and OOD
fields.

Stage 2 must also eventually land a phylogeny-ready core substrate (`rt_core_coordinates`,
`rt_core_extracted`, `rt_core_alignment`, `rt_core_alignment_mask`, `phylogeny_eligibility`)
**after** the detector is frozen and the catalogue stage has run. **No phylogenetic inference
in Stage 2.** Occupancy and architecture products are g5/g6 and are inspectability-aware:
never use all sequences as a denominator when some could not physically show the region.

## 8 · Non-goals and stop conditions

- g4 does **not** run the full catalogue, build a tree, train a model from scratch, or settle
  the RT1 interpretation.
- g4 does **not** predeclare HMMER the winner: an interpretable primary candidate, a
  PSSM-class baseline and — only if a pinned local protein LM and its dependencies already
  exist and a pilot is affordable — a lightweight residue-level challenger are compared on
  predeclared criteria. Inability to run the challenger is recorded, not fatal.
- **Stop and report** if: seven regions can only be produced by forcing; the PDB arm cannot be
  kept out of model construction; no held-out population can be built without relabelling; or
  any claim would need a denominator that does not exist.

## 9 · Reviewer verdicts and repairs

Design review and the post-execution review are routed through ARIS's governed reviewer
mechanism (`/auto-review-loop`, backend `codex`, transition by
`/home/borg/ARIS_CODE/tools/review_gate.py`; positive requires **score ≥ 6 AND verdict ∈
{ready, almost}**). Verdicts, required repairs and the repairs actually applied are recorded
in `review-stage/` and appended here.

- **Design review (pre-g4):** see §9a below, appended after the review ran.
- **Landed-bundle review (post-g4):** see §9b below.

---

## 9a · Design review (pre-g4) — round 1 verdict: NOT READY, g4 NOT executed

    reviewer:  codex / gpt-5.6-sol, read-only, reading the repository itself
    date:      2026-09-16
    score:     3 / 10        verdict: not ready
    gate:      review_gate.py -> {"decision": "continue", "reason": "positive threshold not met"}

**g4 was not executed.** Nine blockers, of which the load-bearing one is identifiability:
g2 supplies an unstable derivational frame, and none of the challenge arms supplies
independent truth for the sequence-region boundaries a detector would be predicting. Full
verdict, per-check outcomes and the 16 required repairs are in `review-stage/AUTO_REVIEW.md`.

Two findings against this session's own conduct are accepted rather than argued:

1. **A full-catalogue pass was run during planning.** The pre-g4 leakage audit searched the
   167-sequence seed against the complete 501,561-sequence Stage-1 catalogue. Launcher §8
   forbids a full 501,561 pass during planning and in `g1`–`g4`. Logged in `docs/BLOCKED.md`
   as a HIGH-STAKES item for an operator ruling.
2. **This record was edited while the review was in flight**, which conflicts with its own
   "supersede, never rewrite" rule. The edits were the incoming CAND95/ph38 corrections.
   **From here, any design change lands as a NEW decision record.**

### What this means for the amendment above

§1–§4 (what g2 and g3 established; the corrected lineage) are **measurements and stand**.
§5–§8 (the revised object, validation architecture, deliverables, non-goals) are **not
approved** and must be re-issued in a successor record that resolves at minimum:

- whether the g4 target is an uncertainty-carrying region ensemble or only the stable
  landmarks (repair 2);
- how a detector is derived from g2 without importing prior models or boundaries (repair 5);
- whether any arm can supply boundary truth, or whether calibration, boundary accuracy and
  `C9` are declared **UNESTABLISHED** from the outset (repair 7) — the launcher's own g4 kill
  criterion already contemplates exactly this outcome;
- the PDB arm's real size (≤25) and whether it is a held-out arm or a structural comparator
  (repair 6);
- the bounded Stage-1 sampling frame, declared before any sample is drawn (repair 12);
- the compute-prohibition question (repair 13).

These are scope decisions with scientific consequences and they are the operator's, not this
session's.
