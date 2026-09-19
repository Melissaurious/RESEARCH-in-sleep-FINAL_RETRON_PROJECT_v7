# Independent review result — Stage 3C architecture integration

**Reviewer:** Codex (GPT-5.x), read-only, model-disjoint from the author (Claude Opus 5) per BS-15 /
WA-A.5 · **Thread:** `01a0bb20-9e2c-7791-88f2-3f17509b17d1` · **Date:** 2026-09-19 ·
**Bundle reviewed at commit:** `34000ee` · **Request:** `INDEPENDENT_REVIEW_REQUEST_stage3c.md`

**Verdict: `FAIL_BLOCK`, 4.5/10. 5 blockers, 10 required repairs.**

The review is reproduced verbatim below. The author's independent verification of each blocker is a
separate document (`docs/errata/2026-09-19_stage3c_review_errata.md`); it does not alter one word of
what follows.

---

# 1. Verdict

**FAIL_BLOCK — 4.5/10.**

The bundle is unusually transparent and most arithmetic reproduces, but it is not promotable. Three primary results violate their declared analysis rules, and Comparison C omits literature evidence already present elsewhere in the same bundle.

| Headline | Review result |
|---|---|
| 19/19 catalytic sets in one unit | Reproduced |
| 5/9 in called palm unit | Reproduced |
| 9/10 in max-strand unit | Reproduced; 1RTD_A tied |
| 13/14 replicate Jaccard | Reproduced from landed table, but not valid as the declared primary analysis: 7 pairs are truth-based and 7 detector-based |
| 28/28 SB3+SB56 co-location | Reproduced |
| 35/36 SB56+SB7 co-location | Reproduced |
| CAT_STATE offset of 2 | Reproduced in 17/17 committed chains, but expected from CAT_STATE's `[YF].DD` construction—not independent validation |
| 0/11 literature fingers coincidence | Numerator reproduced, denominator invalid: three rows are a PMG motif, not a fingers boundary. Existing valid denominator is 0/8 |
| Region-Y RNA ratio 1.34× | Reproduced over 15 chains from 5 biological groups |
| 20/62 complete anchor series | Reproduced; full partition is 20 complete, 39 truncated, 3 without any mapped anchor |

I independently read all relevant TSVs with Python, traced their producing scripts, confirmed the seven copied Stage-2 files byte-for-byte against commit `94a1a788…`, and statically verified all 88 current output files against `OUTPUTS.tsv`.

# 2. Blockers

1. **The 13/14 replicate result violates the declared population and "same pairs" rule.**

   The launcher requires replicate analysis among "Tier-A truth-bearing chains" on the same pairs (launcher lines 203–205). Instead, `s03_catalytic_summary.py` lines 88–115 expands to Tier-A detector-scoreable chains and substitutes detector predictions whenever both chains lack own-chain truth.

   Consequently, the 14 Jaccards comprise 7 truth-based pairs and 7 detector-based pairs; four other numbering-consistent pairs are omitted because one chain's detector abstained. Unit-count agreement uses all 18 pairs. `CLAIM_EVIDENCE_MATRIX.tsv` S05 therefore incorrectly calls them "the same" pairs.

   Under the declared truth-bearing scope, the result is **7/7 Jaccard ≥0.70, median 0.882, versus 0/7 equal unit counts**, but those seven pairs come from only two biological groups. Regenerate the primary A replicate summary; any 13/14 hybrid result must be separately labelled exploratory.

2. **Comparison C contains a non-boundary in its fingers denominator and illegally pools the RED historical stratum.**

   `ECO8-JI26-PMG` explicitly says "Motif, not subdomain" in `C_literature_boundaries_retrieved.tsv` row 27, yet it is admitted as a "boundary statement" in `LITERATURE_BOUNDARY_AUDIT.tsv` row 48 and becomes three fingers rows in `C_overlap.tsv` rows 27–29.

   Removing those rows gives **0/8**, not 0/11, with median best Jaccard **0.488**, not 0.429.

   In addition, `s09_boundary_audit.py` lines 349–362 pools literature and `HISTORICAL_RED` into the `BOTH` 14/32 result, despite the launcher's never-pool rule. The PMG row also overwrites the real Ji fingers assignment in that merge dictionary. Correct, unpooled counts are:

   - Literature: **3/7** same best unit for fingers and palm.
   - `HISTORICAL_RED`: **9/25**.
   - The landed 14/32 is neither the correct pooled count nor a permitted analysis.

3. **Comparison C's retrieval record contradicts evidence already inside Comparison D.**

   `C_sources.tsv` row SRC-WANG22-EC86 says Wang 2022 was not retrieved and no Ec86 boundary could be read. Yet `XY_REGION_EVIDENCE.tsv` S-04 marks that same paper `FULL_TEXT` and quotes the explicit Ec86 thumb interval **238–320**. At minimum it applies to 7V9U_A and 7XJG_A, where my direct join gives Jaccard 0.784 and 0.797, both coincidences.

   S-06 also supplies a full-text Eco7 "thumb domain deletion" interval 235–313 and needs an explicit admission/exclusion ruling. Comparison C, its source audit, X21, and all C counts must be reconciled and rerun.

4. **Every reported Region-X motif hit comes from a fallback forbidden by the launcher's primary rule.**

   The launcher says X is undefined if either SB2p or SB3 is unavailable (lines 236–238). The later script adds a chain-N-terminus-to-SB3 "wide window" (`s07` lines 19–23) and `s08` lines 35–46 pools it into the primary scanned denominator.

   Under the governing rule:

   - X is defined in **24/62**, not 33/62.
   - It is defined in **3/21 retron chains** and undefined in **18/21**, not 13/21.
   - All 24 declared intervals have **no NAXXH or AXXH hit**.
   - The declared-interval shuffle result is **0/2400**.

   All four strict and both relaxed hits occur only in the nine undeclared wide windows. Those rows can survive only as an explicitly post-hoc exploratory appendix, never pooled with the primary X analysis.

5. **The central synthesis does not adequately bound Stage-3B defects or retron scope.**

   `STAGE3C_DECISION_REPORT.md` line 4 repeats the mislabel "CLOSED at PARTIAL." The frozen detector result is presented without saying that `SEP_MIN`, `SEP_MAX`, and `D_MAX` were calibrated on the same 19 truth pairs. The report omits the out-of-sample LOCO result, **12 HIT / 5 MISS / 2 ABSTAIN**.

   The report also omits C-5: the 62-chain Stage-3A register was selected downstream of Stage-3B catalytic-evidence assembly (synthesis audit C-5). Thus "reproducible across these 62 chains" is not population-neutral.

# 3. Required documentary repairs

These wordings are acceptable after the computational blockers above are corrected.

1. **Stage-3B status**

   Superseded:

   > "Stage 3B stays CLOSED at PARTIAL."

   Corrected:

   > "Stage 3B stopped on kill criterion K5 before Tier B was evaluated. Although its landed materials use the label `CLOSED at PARTIAL`, the synthesis audit identifies that label as a misclassification; Stage 3C treats the available Tier-A detector output only as in-sample calibration material."

2. **Population provenance**

   Add to §1:

   > "The 62-chain register is a selected experimental-structure panel assembled downstream of Stage-3B catalytic-evidence collection; it is not an unbiased census of experimental RT structures. Results describe this register only."

3. **Comparison-A detector and replicate statement**

   Superseded:

   > "The frozen detector's prediction lies in the same unit as the truth in 19/19 chains … Replicate stability, on the same pairs … 13/14 … while unit count agrees in 3/18."

   Corrected:

   > "The frozen detector, whose thresholds were calibrated on these same Tier-A truth pairs, places its prediction in the truth-containing PDP unit in 19/19 chains. This is in-sample co-location, not detector validation. Under the declared truth-bearing, numbering-consistent replicate scope, the site-containing unit has Jaccard ≥0.70 in 7/7 pairs from two biological groups (median 0.882), while unit count agrees in 0/7. The broader 13/14 result is an exploratory hybrid of seven truth-based and seven detector-based pairs and is not the primary replicate result."

4. **CAT_STATE interpretation**

   Superseded:

   > "These are independent instruments"
   > "Two instruments with no shared input agreeing to a constant offset … was not expected."

   Corrected:

   > "CAT_STATE 262 was constructed as the modal HMM state of `[YF].DD` motif starts, so its position two residues before a motif aspartate is an expected motif-identity check, not independent catalytic validation. Its co-location with Stage-3A units is still a cross-representation observation."

5. **Comparison-C counts and pooling**

   Superseded:

   > "17 usable boundary statements"
   > "literature fingers 0/11"
   > "a single unit is the best match for both in 14/32"
   > "the historical product … is never pooled."

   Corrected, pending reconciliation with D's sources:

   > "After excluding the PMG motif, the currently landed C source set contains 16 qualifying boundary statements over seven chains. Literature fingers coincide in 0/8 region-chain cases (median best Jaccard 0.488). For sources numbering both fingers and palm, the same PDP unit is the best match in 3/7 literature cases and 9/25 `HISTORICAL_RED` cases; the strata are not pooled. Final coverage and thumb counts require a rerun after incorporating or explicitly excluding the full-text Ec86 and Eco7 thumb evidence already present in `XY_REGION_EVIDENCE.tsv`."

6. **Region X**

   Superseded:

   > "Region X could be scanned in 33/62 … undefined in 13/21 retron chains. Strict NAXXH in 4, relaxed AXXH in 2."

   Corrected:

   > "Under the launcher-declared two-block rule, Region X is defined in 24/62 chains and in 3/21 retron chains; it is undefined in the remaining 38/62 and 18/21, respectively. None of the 24 declared intervals contains NAXXH or AXXH. A separate, undeclared wide-window exploration scanned nine additional chains and found four strict and two relaxed matches; those rows are not pooled with the primary analysis."

7. **Region-Y RNA ratio**

   Superseded:

   > "Three independent strands … 1.34× … against 1.06 in four non-retron chains."

   Corrected:

   > "The retron-chain contact-concentration ratio is 1.34× its chain-length fraction (median 15 chains from five groups; range 0.59–1.86). This is a location ratio, not enrichment evidence for specificity. The structural contact observations and the aggregate contact ratio are not independent strands. The non-retron median 1.06 is defined over three RNA-contacting chains; 26CZ_A contains DNA contacts but no RNA contacts and has no RNA ratio."

8. **Termini denominator**

   Superseded:

   > "20/62 complete; in 39 the anchor series is truncated."

   Corrected:

   > "Of 62 chains, 20 meet the operational complete-anchor criterion, 39 have a truncated anchor series, and three have no mapped anchor: 1RTD_A, 5VBS_A and 8BGJ_A."

9. **Overall synthesis**

   Superseded:

   > "What is reproducible across these 62 chains is a catalytic centre, locatable by three mutually independent instruments …"
   > "Vocabulary 6, anchored on vocabulary 3, is the representation this evidence actually supports."

   Corrected:

   > "Across nonuniform subsets of this selected register, mapped sequence-state blocks and Tier-A non-retron catalytic labels often occupy a large PDP unit. The instruments are not mutually independent, and no retron catalytic-architecture conclusion follows. 'Conserved core plus variable accessory architecture' remains a hypothesis for later testing, not a winning representation established here."

10. **Stale coverage row**

   `CONTRADICTIONS_AND_UNCERTAINTY.tsv` X21 still says "17 … over 8 chains," contradicting the report's current seven. Replace the fixed count with the reconciled post-rerun total.

# 4. Advisory notes

- The residue-key foundation is sound for the landed data. `chain_index_map.tsv` has 30,988 modelled residues; PDP has 30,984, with exactly four `PDP_ABSENT` modified residues and 552 label-0 residues across 15 chains. All actual insertion codes are blank, so the places where C and D discard `icode` do not alter current results. They should nevertheless retain `(resnum, icode)` to satisfy the frozen contract.

- Comparison B includes 46 mapped residues with PDP label 0 in its denominators; it does not silently turn label 0 into a unit. CAT_STATE has 59 available rows: 58 contained and one `AVAILABLE_BUT_NO_RESIDUE_IN_A_UNIT` (`7KFT_C`). The report table should show that fourth category.

- The 0.309 target-unit size baseline uses **18**, not 19, chains because 1RTD_A has a tied target. State that denominator.

- The 1.34× Region-Y value is chain-weighted. Fifteen chains represent only five biological groups, with six Ec86 and four Ec78-family depositions. A group-weighted descriptive summary would be useful.

- The complete-anchor thresholds, first state ≤115 and last state ≥310, are declared only in `s06_termini.py` lines 28–31, not in the governing launcher, and were not sensitivity-tested.

- The strict Tier-A decoy count is 19; adding the four eligible external controls gives 23. Neither reaches K5's required 60. Stage 3C does not otherwise depend on the stale "36" count or the stale "all six adjacent" description.

- "9/9 confirms Eco7↔9VHE identity" is too strong. Two recovered motif positions support the mapping; they do not establish full sequence identity.

# 5. Per-focus-area findings

1. **Frozen joins:** Mostly correct at the residue level. Stage-2 copies match their git blobs; all 62 chains remain represented; label 0 and PDP absence are distinguished. The significant denominator failures are analytical rather than low-level join loss: hybrid A replicates, PMG contamination/pooling in C, and wide-window pooling in D.

2. **Stage-3B limitations:** C-2 is inherited directly through the `PARTIAL` language. In-sample calibration materially affects the detector-based 19/19 and half of the 13/14 replicate result. LOCO is absent. The obsolete decoy and adjacent-miss statements are not reused. C-5 is unreported. C-6 does not affect current primary rows because Tier B is excluded, but it constrains any appendix. OQ-11's concern is not adequately bounded for A.

3. **Catalytic location versus unit stability:** The 19/19, 5/9 and 9/10 measurements are correct. A same-pair truth-only contrast does support greater site-unit than unit-count stability—7/7 versus 0/7—but only in two non-retron groups. The report's broad "architectural fact" claim exceeds that evidence.

4. **RT0–RT7:** Scope is generally handled well. RT0/RT1 receive no intervals, and block names retain their LtrA-local meaning. The 28/28 and 35/36 co-location counts are correct. CAT_STATE's +2 offset is construction-driven, not independent confirmation.

5. **Literature boundaries:** Unverified statements are excluded, and most quotes have good provenance fields. However, the admitted denominator is wrong, historical and literature strata are pooled once, and the C/D retrieval contradiction omits at least one strong primary thumb boundary. The phrase "13 chains verified by a source-stated motif" is also inaccurate for 1RTD and 5G2X; those checks are not from the same boundary source.

6. **Region X/Y:** The Y counts and retron 1.34× arithmetic reproduce. The Eco8 VTG null is strong—none of the six sequences contains VTG/ITG/LTG anywhere, not merely in the chosen window. Region X's primary result is invalid because of the undeclared fallback. Nothing here establishes RT–ncRNA pairing specificity.

7. **Termini/fusions:** The truncation caveat is appropriate and important. Both insertion measures are correctly retained: zero ≥20-residue anchor-gap calls, maximum excess 19, versus a mapper insertion run of 774. The complete/truncated/no-anchor partition and unswept completeness thresholds need explicit reporting.

8. **Retron-specific support:** The report exceeds retron evidence in its short answer, vocabulary table, and preferred "vocabulary 6" synthesis. Comparison A has no retron; B is GII-framed; C is small and currently miscomputed; D supports thumb/RNA contact location but not pairing specificity. No retron-wide architecture winner is established.

# 6. Tier-B appendix ruling

**Defensible, but only as a separately titled, lower-confidence location-description appendix using frozen labels—not detector output.**

Acceptable wording:

> "Exploratory Tier-B retron label-location appendix. This appendix places only frozen, per-chain Stage-3B Tier-B residue labels onto the frozen Stage-3A PDP partition. It does not run or score the Stage-3B detector, does not report HIT/MISS, is not held-out or blind validation, is not pooled with Tier A, changes no threshold or verdict, and makes no claim that a single labelled residue constitutes a catalytic pair. Tier B was inspected during detector design, and the detector's Tier-B PASS branch was unreachable; neither issue is cured by this descriptive placement."

Only rows carrying an explicit frozen per-chain label should be placed. In the current `TRUTH_TABLE.tsv`, that means the five `OWN_CHAIN` Tier-B rows. Transferred rows with blank residue fields and `truth_source=TRANSFERRED_WITHIN_REPLICATE_GROUP` may be counted but should not be reconstructed unless an already-frozen per-chain transfer mapping is cited. `FUNCTIONAL_PAIR` rows with `truth_source=NONE` must not be promoted into truth labels.

Under those limits, C-6 and the unreachable-PASS defect do not invalidate the appendix because it makes no detector-performance or blindness claim.

# 7. What I could not check

- I did not run `run.sh`, as instructed. I verified only that all 88 currently landed files match their current `OUTPUTS.tsv` seals.
- The cached literature full texts are not included in the bundle, and network access was unavailable. I could audit quotes, locators, retrieval statuses and hashes, but not compare every quote with the original source text.
- I could not resolve whether every deposited RNA is the cognate msr; the bundle itself records this as unknown.
- I did not test alternate X/Y windows, alternate contact cutoffs, or alternate complete-anchor thresholds.
- I did not validate the modelled-sequence `rt_hash` values against the external RT–ncRNA catalogue.
- The required human-input audit remains pending.
