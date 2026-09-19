# ERRATA — Stage 3C architecture integration, from the independent review

Date: 2026-09-19 · Track `s3c` · Bundle `analysis/stage3c_architecture_integration/` at `34000ee`

Review: `review-stage/INDEPENDENT_REVIEW_RESULT_stage3c.md` — Codex (GPT-5.x), model-disjoint,
read-only, thread `01a0bb20-9e2c-7791-88f2-3f17509b17d1`, **`FAIL_BLOCK`, 4.5/10, 5 blockers**.

> **This record is additive. The Stage-3C bundle is frozen and no file in it has been edited,
> regenerated or re-sealed.** Every statement below supersedes the bundle wording it quotes.
> **`STAGE3C_DECISION_REPORT.md` and `README.md` may not be read, cited or promoted without this
> erratum.** Where a corrected number is given, the author re-derived it independently from the
> landed tables; the verification command output is recorded in the session log and summarised in
> the `author_verification` column below.

**Nothing in Stage 2, Stage 3A or Stage 3B is altered by this erratum.** No threshold was retuned,
and no analysis was re-run: five of the ten items below require a **re-run that is not authorised
yet** (§3).

---

## 1 · The five blockers, each independently verified by the author

| # | blocker | author verification | verdict |
|---|---|---|---|
| B1 | The `13/14` replicate Jaccard is not the declared primary analysis: 7 pairs are truth-based and 7 detector-based, and it is not computed over "the same pairs" as the `3/18` unit-count figure | recomputed from `tables/A_replicate_stability.tsv`: basis counts are exactly `{truth: 7, detector_prediction: 7}`; pairs where **both** chains carry own-chain truth = **7**, drawn from only **2** biological groups (RG02, RG31) | **UPHELD** |
| B2 | `ECO8-JI26-PMG` is a motif, not a boundary, and contaminates the fingers denominator; the `14/32` fingers-and-palm figure pools LITERATURE with HISTORICAL_RED against the launcher's never-pool rule | the source row's own `notes` field reads "Motif, not subdomain"; excluding it gives literature fingers **0/8**, median best Jaccard **0.488**; unpooled fingers-and-palm co-location is **3/7** literature and **9/25** historical | **UPHELD** |
| B3 | Comparison C's source audit says Wang 2022 was `NOT_RETRIEVED` while Comparison D's audit holds the same paper as `FULL_TEXT` and quotes an Ec86 thumb interval | `tables/C_sources.tsv` `SRC-WANG22-EC86` = `NOT_RETRIEVED`, "NO Ec86 subdomain boundaries could be read"; `XY_REGION_EVIDENCE.tsv` `S-04` = `FULL_TEXT`, "thumb = 238-320"; `S-06` = `FULL_TEXT`, Eco7 "thumb deletion 235-313" | **UPHELD** |
| B4 | Every reported Region-X motif hit comes from the wide-window fallback, which the launcher's primary rule does not admit | declared two-block rule: X defined in **24/62** chains, of which **0** contain NAXXH or AXXH; all 4 strict and 2 relaxed hits lie in the **9** wide-window chains; retron chains with a declared-rule X interval = **3/21** | **UPHELD** |
| B5 | The synthesis does not bound the Stage-3B defects (PARTIAL mislabel, in-sample calibration, missing LOCO) or the selected-register provenance (C-5) | confirmed by inspection of the report; `g2_frozen_parameters.tsv` shows `SEP_MIN`/`SEP_MAX`/`D_MAX` each derived from the Tier-A truth pairs; LOCO rows in `G2_SENSITIVITY_TIERA.tsv` sum to **12 HIT / 5 MISS / 2 ABSTAIN** | **UPHELD** |

**All five blockers are upheld. Two of them (B1, B4) mean a primary Stage-3C number was computed
under a rule the governing launcher does not declare.** That is a process failure of this stage, not
of any upstream stage.

---

## 2 · Documentary repairs — superseded wording, corrected wording

Adopted verbatim from the review except where the author's verification refines a number; each
refinement is flagged.

### E-3C-1 · Stage-3B status

**Superseded** (`STAGE3C_DECISION_REPORT.md` line 4): "Stage 3B stays CLOSED at PARTIAL."

**Corrected:** Stage 3B stopped on kill criterion K5 before Tier B was evaluated. Although its landed
materials use the label `CLOSED at PARTIAL`, the synthesis audit identifies that label as a
misclassification; Stage 3C treats the available Tier-A detector output only as in-sample
calibration material.

### E-3C-2 · Population provenance (synthesis audit C-5)

**Add to §1:** The 62-chain register is a selected experimental-structure panel assembled downstream
of Stage-3B catalytic-evidence collection; it is not an unbiased census of experimental RT
structures. Results describe this register only.

### E-3C-3 · Comparison-A detector and replicate statement

**Superseded:** "The frozen detector's prediction lies in the same unit as the truth in 19/19
chains … Replicate stability, on the same pairs … 13/14 … while unit count agrees in 3/18."

**Corrected:** The frozen detector, whose thresholds were calibrated on these same Tier-A truth
pairs, places its prediction in the truth-containing PDP unit in 19/19 chains. This is in-sample
co-location, not detector validation. Under the declared truth-bearing, numbering-consistent
replicate scope, the site-containing unit has Jaccard ≥ 0.70 in **7/7** pairs from **two** biological
groups (median **0.882**), while unit count agrees in **0/7**. The broader 13/14 result is an
exploratory hybrid of seven truth-based and seven detector-based pairs and is not the primary
replicate result. The out-of-sample LOCO result for the Stage-3B detector is **12 HIT / 5 MISS /
2 ABSTAIN**, not the in-sample 13/6/0.

### E-3C-4 · CAT_STATE 262 interpretation

**Superseded:** "These are independent instruments"; "Two instruments with no shared input agreeing
to a constant offset … was not expected."

**Corrected:** CAT_STATE 262 was constructed as the modal HMM state of `[YF].DD` motif starts, so its
position two residues before a motif aspartate is an expected motif-identity check, not independent
catalytic validation. Its co-location with Stage-3A units is still a cross-representation
observation.

### E-3C-5 · Comparison-C counts and pooling

**Superseded:** "17 usable boundary statements"; "literature fingers 0/11"; "a single unit is the
best match for both in 14/32"; "the historical product … is never pooled".

**Corrected:** After excluding the PMG motif, the currently landed C source set contains **16**
qualifying boundary statements over **seven** chains. Literature fingers coincide in **0/8**
region-chain cases (median best Jaccard **0.488**). For sources numbering both fingers and palm, the
same PDP unit is the best match in **3/7** literature cases and **9/25** `HISTORICAL_RED` cases; the
strata are **not** pooled. Final coverage and thumb counts require a re-run after incorporating or
explicitly excluding the full-text Ec86 and Eco7 thumb evidence already present in
`XY_REGION_EVIDENCE.tsv` (§3, R2).

### E-3C-6 · Region X

**Superseded:** "Region X could be scanned in 33/62 … undefined in 13/21 retron chains. Strict NAXXH
in 4, relaxed AXXH in 2."

**Corrected:** Under the launcher-declared two-block rule, Region X is defined in **24/62** chains and
in **3/21** retron chains; it is undefined in the remaining 38/62 and 18/21 respectively. **None of
the 24 declared intervals contains NAXXH or AXXH.** A separate, undeclared wide-window exploration
scanned nine further chains and found four strict and two relaxed matches; those rows are
exploratory and are **not** pooled with the primary X analysis.

### E-3C-7 · Region-Y RNA ratio

**Superseded:** "Three independent strands … 1.34× … against 1.06 in four non-retron chains."

**Corrected:** The retron-chain contact-concentration ratio is 1.34× its chain-length fraction
(median over 15 chains from **five** groups; range 0.59–1.86). This is a location ratio, not
enrichment evidence for specificity. The structural contact observations and the aggregate contact
ratio are **not** independent strands. The non-retron median 1.06 is defined over **three**
RNA-contacting chains; `26CZ_A` has DNA contacts but no RNA contacts and has no RNA ratio
(author-verified: non-retron Y rows = 4, of which 3 carry a ratio).

### E-3C-8 · Termini denominator

**Superseded:** "20/62 complete; in 39 the anchor series is truncated."

**Corrected:** Of 62 chains, **20** meet the operational complete-anchor criterion, **39** have a
truncated anchor series, and **three** have no mapped anchor at all: `1RTD_A`, `5VBS_A`, `8BGJ_A`.
The completeness thresholds (first state ≤ 115, last state ≥ 310) are declared in
`scripts/s06_termini.py` only, not in the governing launcher, and were not sensitivity-swept.

### E-3C-9 · Overall synthesis

**Superseded:** "What is reproducible across these 62 chains is a catalytic centre, locatable by
three mutually independent instruments …"; "Vocabulary 6, anchored on vocabulary 3, is the
representation this evidence actually supports."

**Corrected:** Across nonuniform subsets of this selected register, mapped sequence-state blocks and
Tier-A **non-retron** catalytic labels often occupy a large PDP unit. The instruments are **not**
mutually independent, and **no retron catalytic-architecture conclusion follows**. "Conserved core
plus variable accessory architecture" remains a hypothesis for later testing, not a winning
representation established here.

### E-3C-10 · Stale coverage row and small denominators

* `CONTRADICTIONS_AND_UNCERTAINTY.tsv` X21 still says "17 … over 8 chains"; the report already says
  seven. Both are superseded by E-3C-5 pending the re-run.
* The 0.309 size-expected baseline is over **18** chains, not 19 (`1RTD_A` has a tied target). The
  landed table states this; the report does not.
* Comparison B has a fourth containment category that the report's table omits:
  `AVAILABLE_BUT_NO_RESIDUE_IN_A_UNIT`, which occurs once (`7KFT_C`, CAT_STATE).
* "9/9 confirms the Eco7↔9VHE identity" is too strong: two recovered motif positions **support** the
  mapping; they do not establish sequence identity.

---

## 3 · Required re-runs — NOT AUTHORISED, NOT PERFORMED

The operator's instruction is that Stage 3C remains frozen, so none of the following has been run.
Each would change a landed primary table and therefore needs explicit authorisation.

| id | re-run | what it fixes | scope |
|---|---|---|---|
| R1 | regenerate the Comparison-A replicate summary under the truth-bearing scope, with the hybrid result relabelled exploratory | B1 | `scripts/s03_catalytic_summary.py`, tables `A_replicate_*` |
| R2 | admit or explicitly exclude the full-text Ec86 (thumb 238–320) and Eco7 (235–313) boundaries, reconcile `C_sources.tsv` with `XY_REGION_EVIDENCE.tsv`, and re-run all C counts | B3 | `scripts/s09_boundary_audit.py`, tables `C_*` |
| R3 | drop the PMG motif row from the boundary denominator and stop pooling the two strata in the fingers-and-palm statistic | B2 | `scripts/s09_boundary_audit.py` |
| R4 | report Region X under the declared two-block rule as primary, with the wide window as a separate exploratory appendix | B4 | `scripts/s07_xy_regions.py`, `scripts/s08_xy_summary.py` |
| R5 | regenerate the report and README against R1–R4, incorporating E-3C-1…E-3C-10 | B5 and all | prose only, after R1–R4 |

**Until R1–R5 are authorised and executed, no Stage-3C number may be promoted to a thesis or paper
claim, and `CLAIM_EVIDENCE_MATRIX.tsv` rows S05, S11, S12 and the Region-X portion of S16 are
WITHDRAWN.** Rows S01–S04, S07–S10 and S19–S22 are unaffected by the blockers; S17 stands as
corrected by E-3C-7.

## 4 · Not affected

Stage 3C does **not** reuse the two superseded Stage-3B statements the synthesis audit flags (the
"decoy pool 36" count and the "all six misses are adjacent-aspartate confusions" description); the
author re-checked the whole bundle for both strings and found neither. The residue-key join
foundation, the Stage-2 copies (byte-identical to their git blobs), the RT0/RT1 no-interval rule and
the 88-file `OUTPUTS.tsv` seal were all independently confirmed by the reviewer.
