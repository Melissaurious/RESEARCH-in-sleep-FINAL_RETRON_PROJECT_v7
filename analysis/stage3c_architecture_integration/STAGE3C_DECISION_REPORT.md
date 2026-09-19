# Stage 3C — post-hoc integration of independently frozen RT architecture analyses

**Status: COMPLETE for experimental structures. No verdict is issued, and none is merged.**
Stage 2 stays CLOSED, Stage 3A stays CLOSED at FAIL, Stage 3B stays CLOSED at PARTIAL. This stage
changed no threshold, no criterion and no output of any of them: all 236 hash-checked frozen inputs
matched their records (`INPUT_PROVENANCE.tsv`).

Governed by `launchers/LAUNCHER_03C_architecture_integration.md`. Every number below is a census over
named chains with its own denominator; no inferential test was declared and none was run. Interpretation
is marked `PROPOSED:` and is the operator's to accept (WA-A.4). Nulls and refutations are reported in
place (WA-G.5).

**The question.** How do independently defined RT sequence states, catalytic geometry, structural units
and historical retron-specific regions relate to each other, and which architectural representation is
actually reproducible across experimental retron/RT structures?

**The short answer.** `PROPOSED:` the five vocabularies are not competing descriptions of one object.
What is reproducible across these 62 chains is (i) a catalytic centre, locatable by three mutually
independent instruments that agree to within two residues, and (ii) a single large structural unit that
contains most of the numbered RT state series. What is *not* reproducible is any three-way
fingers/palm/thumb partition — not from contact density (Stage 3A's own FAIL), not from the literature
(which does not agree with itself), and not from the inherited boundary product (whose fingers and thumb
are arithmetic residuals). Different vocabularies describe different scales, and the failure of one is
not evidence against another.

---

## 1 · What was compared, and on what

62 experimentally determined RT chains, 31 biological groups, from the frozen Stage-3A register:
46 primary / 15 flagged / 1 design-exposed, with `IMPLEMENTATION_SENSITIVE` (5 chains) and the BJ-p4
partition carried as a sensitivity arm throughout. Family and lineage labels enter the analysis in this
stage for the first time; that transition is recorded here, and those labels are strata, never evidence.

| comparison | instrument being read | scope actually available |
|---|---|---|
| A | Stage-3B catalytic truth + frozen detector | **19** Tier-A truth-bearing chains; **none is a retron** |
| B | frozen mapper `rtmap-1.0.0/53a1e738a19b3896`, applied unmodified | 59 chains MAPPED, 1 ABSTAIN, 2 below the instrument's 250-aa minimum |
| C | literature + the inherited historical product | **17** usable boundary statements over **8** chains, plus 25 historical rows |
| D | Region X / Region Y literature, then an operational annotation | 62 chains scanned; 21 retron |
| E | the experimental register + the mapped anchor span | 62 chains; extensions interpretable in 20 |

---

## 2 · Comparison A — catalytic geometry against structural units

**Numbers.** → `STRUCTURE_STAGE3B_CROSSWALK.tsv`, `tables/A_summary.tsv`, `tables/A_replicate_*.tsv`,
`figures/F1_catalytic_site_vs_units.png`

* The catalytic aspartates lie **inside a single unit in 19/19** chains (14 biological groups).
* That unit is the **called palm-like unit in only 5/9** chains that received a palm-like CALL. In
  `9NL3_A` the site sits in the **fingers-like** unit; in `8GH6_A`, `8UW3_A`, `9YFD_A` in an unclassified
  unit.
* Where no palm-like unit was called, the site lies in the unit with the most same-sheet strands in
  **9/10** chains (one target TIED, not broken) — the post-hoc diagnosis Stage 3A recorded at closure.
* The site-containing unit is **discontinuous in 14/19** chains.
* The frozen detector's prediction lies in the **same unit as the truth in 19/19** chains, including all
  **6** residue-level misses 3B recorded. Localisation and residue membership separate cleanly.
* Chance baseline: the target unit holds a median **0.309** of modelled residues.
* **Replicate stability, on the same pairs:** the site-containing unit agrees at Jaccard ≥ 0.70 in
  **13/14** pairs (median **0.897**), while unit *count* agrees in **3/18** numbering-consistent pairs.
  Catalytic-pair carboxylate separation, by contrast, differs by more than 0.5 Å in **4/6** pairs
  (max **2.77 Å**) — consistent with the metal-bound/apo state effect 3B measured.

**`PROPOSED:` Means.** Catalytic *location* is the more reproducible architectural fact. It survives a
partition that is itself unstable, and it is recovered identically by the BJ-p4 arm. The palm-like label
is a β-sheet-content heuristic and does not track the catalytic site; the two must not be equated.
Catalytic *geometry* (the carboxylate distance) is not stable across replicates and should not be used
as a stability argument.

**Implication.** A catalytic-centre-anchored coordinate is a better hub for cross-family architecture
comparison than a domain partition. Stage 3A's FAIL is not contradicted: no three-way partition is
recovered here either.

**Would be wrong if.** A truth set were split across units, or the detector's misses landed in different
units. Neither occurs. It would also be weakened if the concordance were structural inevitability — the
0.309 size baseline prices that, and the site-in-target rate (9/10, 5/9) is not what a random residue
would give, but this remains a *description* of two instruments that both describe the same fold core
(`CONTRADICTIONS_AND_UNCERTAINTY.tsv` X22).

⚠️ **Scope, stated as prominently as the result:** every retron chain is Tier B or Tier C in Stage 3B,
which closed with Tier B never opened. **Comparison A says nothing about retron catalytic architecture.**
Admitting Tier-B truth labels descriptively is an operator decision (X12; `docs/BLOCKED.md`).

---

## 3 · Comparison B — RT0–RT7 state blocks against structural units

**Numbers.** → `STRUCTURE_STAGE2_CROSSWALK.tsv`, `tables/B_*.tsv`,
`figures/F2_state_blocks_vs_units.png`

| block (LtrA-local correspondence) | available | contained in one unit | split | modal unit is palm-like |
|---|---|---|---|---|
| RT0, RT1 | **0/62 — no states exist** | — | — | — |
| SB2p (RT2, PARTIAL) | 24/62 | 12 | 12 | 2 fingers-like, 10 unclassified |
| SB3 (RT3) | 33/62 | 31 | 2 | 15/31 |
| SB4 (RT4, frame-unstable) | 37/62 | 26 | 11 | 5/26 |
| SB56 (joint RT5+RT6) | 54/62 | 53 | 1 | 25/53 |
| SB7 (RT7) | 37/62 | 37 | 0 | 16/37 |
| CAT_STATE 262 (not an anchor) | 59/62 | 58 | 0 | 29/58 |

* **Blocks merge rather than separate.** Where two blocks are each contained in one unit, they are in the
  **same** unit: SB3+SB56 **28/28**, SB56+SB7 **35/36**, SB4+SB56 20/24. 50 of 219 units hold ≥ 2 blocks.
* **Splitting is concentrated exactly where Stage 2 said the evidence was weakest**: SB2p (RT2, PARTIAL)
  splits in 12/24 available chains and SB4 (frame-unstable) in 11/37, against 0/37 for SB7 and 1/54 for
  SB56.
* **Cross-instrument agreement:** CAT_STATE 262 lands **exactly 2 residues** before the nearest Stage-3B
  catalytic aspartate in **17/17** chains where both instruments commit, and in the same unit in 17/19.
  These are independent instruments — a sequence HMM state versus metal/substrate/author-derived truth.
* Between-protein variability: containment class is uniform within 28–31 of 31 groups per block.
* Availability is strongly family-dependent (retron median mapped fraction 0.427 vs non-LTR 0.813) — the
  known GII-centred frame gradient, a property of the instrument.
* Thresholds swept (availability 0.30/0.50/0.70 × containment 0.70/0.80/0.90): `tables/B_sensitivity.tsv`.

**`PROPOSED:` Means.** The numbered RT state series and contact-density units describe **different
scales**: most of the series collapses into one structural unit. That is why a three-way partition of the
RT core is not recoverable from contact density — there is, in these structures, mostly *one* core unit
plus accessory content.

**Implication.** RT0–RT7 remains a sequence-level vocabulary. It should not be redescribed as structural
domains, and a structural unit should not be given an RT-number name.

**Would be wrong if.** The blocks landed in distinct units in most chains. They do not. The claim is
limited by the instrument's reach: the 38 chains where SB2p is unavailable say nothing about RT2.

⚠️ **RT0 and RT1 receive no interval anywhere in this stage, on any structure.** They carry no frozen
states by construction. Non-observability is not absence, and nothing here resolves them (K7 enforced in
code).

---

## 4 · Comparison C — historical and literature fingers/palm/thumb

**Provenance audit first.** → `LITERATURE_BOUNDARY_AUDIT.tsv` (94 rows)

The inherited `reference_boundaries` product is **RED and re-verified as RED on the files themselves**:
fingers and thumb are arithmetic residuals of a palm-centred partition in **25/25** rows; the 5HHJ anchor
is hardcoded with no recorded source; the logs carry their own "DSSP vs alignment boundaries disagree"
warnings and gate nothing; the **5G2X palm excludes that chain's own catalytic aspartate**; the same Ec86
protein receives boundaries differing by 77 residues across entries; the anchor entry is misfamilied as a
retron when it is a group II intron maturase. It is reported only as its own stratum and never pooled.

Of the literature, **primary structure papers essentially never number fingers/palm/thumb** — for most
proteins the subdomains appear only as unnumbered figure schematics. 17 statements were usable after
per-chain numbering verification (13 chains verified by a source-stated motif position; 6 statements not
joined because numbering could not be verified).

**Numbers.** → `tables/C_summary.tsv`, `tables/C_overlap.tsv`, `figures/F3_literature_overlap.png`

| stratum | region | n (region × chain) | coincide (J ≥ 0.70) | median best J |
|---|---|---|---|---|
| LITERATURE | fingers | 11 | **0** | 0.429 |
| LITERATURE | palm | 7 | 2 | 0.596 |
| LITERATURE | thumb | 9 | 3 | 0.510 |
| LITERATURE | fingers+palm combined | 1 | **1** | 0.713 |
| HISTORICAL_RED | fingers | 25 | 3 | 0.500 |
| HISTORICAL_RED | palm | 25 | 2 | 0.497 |
| HISTORICAL_RED | thumb | 25 | **14** | 0.743 |

* Where one source numbers both fingers and palm, **a single unit is the best match for both in 14/32**
  source-chain cases.
* HIV-1 RT: the **thumb coincides** (J 0.959 / 0.866 for two reviews) while fingers and palm each map to
  the same unit 1 at J ≈ 0.5 — that unit is fingers+palm together. LtrA: the paper's combined
  "fingers-palm" region 82–360 coincides with unit 1 (J 0.713), while its thumb (391–474) is a *subset*
  of a larger unit (J 0.444, 100% of the region inside the unit).
* **Reference-specific disagreement** is itself a finding: the two 2026 Retron-Eco8 papers give
  incompatible partitions in the same numbering frame (X01); HIV-1 reviews differ by 1–5 residues (X02);
  one LtrA paper carries two thumb definitions (X03).

**`PROPOSED:` Means.** The classical fingers/palm/thumb vocabulary is real as a *description of the
right-hand fold*, but in these structures fingers and palm are not separable contact-density units — they
are one unit — while the thumb is the region most often recovered as a unit of its own. The
historical product's high thumb agreement is an artefact of its residual construction (everything after
the palm), not independent support.

**Implication.** This is where Stage 3A's narrow conclusion becomes interpretable: 3A did not fail to
find regions that the literature has pinned down; the literature has not pinned them down either.

**Would be wrong if.** A larger, retrievable literature set showed fingers and palm regularly coinciding
with separate units. 21 target papers could not be retrieved (paywall/403), so this is a sample of the
literature, not a census (X21).

---

## 5 · Comparison D — retron Region X and Region Y

**Provenance audit first.** → `XY_REGION_EVIDENCE.tsv` (41 rows, 30 sources), `tables/D_audit_notes.md`

* **No source states a general residue-numbered interval for either region.** X is "a ~16 aa segment
  between RT motifs 2 and 3"; Y is "a ~90 aa segment beginning at the VTG triplet within motif 7 and
  running to the C-terminus" (Simon et al. 2019, retrieved in full text).
* The **only** numbered Y intervals are experimental fragments of two proteins: RT-Ec86-(255–320), which
  binds its own msr stem-loop at K_D ≈ 5 × 10⁻⁸ M and not msr-Ec73, and RT-Ec73-(251–316), reciprocally
  (Inouye et al. 2004, abstract verbatim). The founding domain-exchange experiment (Inouye et al. 1999)
  is available here **in abstract only**: "the C-terminal 91-residue sequence of RT-Ec86 was found to be
  essential for the recognition of the unique stem-loop structure and the branching G residue".
* **Region X's functional evidence is second-hand**: a deletion result reported only through a review.
* **Label attribution conflicts** (X06), and the phrase "the VTG triplet directs the RT to its cognate
  msr" **conflates two objects** (X07): VTG sits at the active site (Ec86 243–245, beside YADD 195–198),
  whereas the msr contacts reported in the same structure are thumb residues R238…Y302.
* ⚠️ **Terminology hazard, carried in every table:** group II intron "domain X" is the **thumb**, after
  RT7; retron "Region X" is between RT2 and RT3. Different objects, similar names. Positionally, retron
  Region Y — not Region X — is the one that corresponds to group II domain X.

**Operational annotation, rule committed before any chain was scanned.** → `XY_REGION_ANNOTATIONS.tsv`,
`tables/D_*.tsv`, `figures/F4_region_y_rna.png`

Controls all passed: literature-stated motif positions recovered **9/9** (this also confirms, by sequence,
the Eco7↔9VHE identity the retrieval only asserted); YxDD recovered at independently evidenced truth
**19/19**; the contact code reproduces Stage-3B's `SUBSTRATE_NA` residues **44/44**; shuffle null **4/3300**.

* Region X could be scanned in only **33/62** chains (24 from blocks, 9 in a wider window) and is
  undefined in **13/21 retron chains** — because the GII-centred mapper does not reach SB2p there. Strict
  NAxxH in 4 chains, relaxed AxxH in 2.
* **Region Y is defined in 15/21 retron chains. All six Retron-Eco8 chains carry no VTG-like triplet**
  in the window (X08), and a VTG triplet is also present in **four non-retron chains** (X09). In this
  population the motif is neither universal nor exclusive.
* Where the operational rule and the literature agree, they agree well: median Y length **74** in retrons
  against the literature's "~90 aa". Where a C-terminal fusion exists (Ec67), the rule swallows it
  (322–327 residues) — a limitation of the rule, recorded, not a finding about biology (X10).
* Region Y coincides with the structurally defined Ec86 **thumb** (238–320).

**The downstream question — could variation in Region Y plausibly contribute to RT–ncRNA pairing
specificity?**

> `PROPOSED:` **Plausible, and not established here.** Three independent strands point the same way:
> the classical reciprocal fragment-binding experiment (two retrons only); the structural observation
> that msr contacts are made by residues inside this region; and, measured in this stage, that Region Y
> carries **1.34×** its length-proportional share of RNA-contacting residues in retron chains (median;
> range **0.59–1.86**; n = 15) against 1.06 in four non-retron chains. None of that is specificity. The
> historical evidence tests exactly **one pair** of retrons, and the enrichment measured here is modest,
> variable, and computed on whatever nucleic acid each entry happens to contain.

`XY_REGION_ANNOTATIONS.tsv` is machine-readable and carries `rt_hash` (the dbchar `g2lib.rt_hash`
convention, computed on the modelled sequence), UniProt accessions and the construct hash, so a later
governed task can join it to the RT–ncRNA modelling dataset. **The join itself, and any catalogue-wide
application of the X/Y rule, are out of scope here.**

---

## 6 · Comparison E — termini, insertions, fusions, extra units

**Numbers.** → `TERMINI_FUSION_SUMMARY.tsv`, `tables/E_*.tsv`, `figures/F5_architecture_vs_calls.png`

* Residues outside the mapped anchor span are interpretable as **terminal extensions in only 20/62**
  chains; in 39 the anchor series is truncated (mostly N-terminally, in retrons) and those residues are
  **unseen RT sequence, not measured extension** (X17). Among complete-series chains the median fraction
  outside the core is 0.529 (primary stratum) and 0.712 (flagged).
* **Insertions: two measures, deliberately reported together.** The declared gap rule detects **no**
  insertion ≥ 20 residues (max excess 19), but it is blind wherever anchors are deleted; the instrument's
  own insertion runs reach **774 residues** in one chain (median maximum run 108). A "no insertions"
  statement would have been false (X16).
* Units wholly outside the RT core: median **3** in flagged chains vs **1** in primary; `EXTRA_DOMAIN`
  units concentrate in flagged chains, as Stage 3A found.
* Does unusual architecture explain the decomposition failures? **Only weakly.** Chains without a
  palm-like call have a median of **1** unit outside the core against **2** for chains with a call, and
  identical median unit counts (3). The palm-like call is not simply lost in the most fused chains.
* Fusion partners are classified only where independently known (MBP in 9WY8); the rest are
  `MULTIPLE_ACCESSIONS_UNCLASSIFIED` pending literature.

**Design requirements for a later fusion/accessory-domain task** (this stage produces requirements, not
the scan):

1. **Do not define the RT core by the GII-centred mapper.** It truncates N-terminally on exactly the
   families of interest. The core needs a family-aware or structure-based boundary.
2. **An insertion measure must not require anchors to be mapped.** Use profile-relative insertion runs, or
   a structural measure, and report both.
3. **Separate expression constructs from biology before counting**, using per-accession identity, not
   construct length alone; the register's `SUSPECTED` flag is length-based and is not evidence of fusion.
4. **Carry the numbering hazard**: author numbering in these files is native (no negative tag numbering
   was found, X05), but construct offsets exist and are recorded per chain.
5. **Predicted structures remain out of scope** until a governed task authorises transfer; nothing here
   licenses it.
6. Keep the strata (primary/flagged/design-exposed) and the BJ-p4 sensitivity arm.

---

## 7 · The six vocabularies, side by side

| vocabulary | what it reproducibly delivers on these 62 chains | what it does not |
|---|---|---|
| **1. Structural-domain units** (PDP, 3A) | a large core unit; recurrent palm-like β-sheet unit (call rate 0.565) | a stable unit count (replicates agree 38.5%); a three-way partition |
| **2. RT0–RT7 states** (Stage 2) | a sequence coordinate that lands in one structural unit; SB7/SB56 highly containable | separation into distinct structural domains; anything for RT0/RT1; retron N-terminal reach |
| **3. Catalytic geometry** (3B) | site *location*, single-unit, replicate-stable, cross-checked by a second instrument to 2 residues | exact residue membership (13/19); anything about retrons (Tier B never opened); stable carboxylate distance |
| **4. Historical fingers/palm/thumb** | a thumb that is often a unit; a fingers+palm block that is one unit | self-consistency between references; numbers for most proteins |
| **5. Retron Region X / Y** | Y as an operational, motif-anchored C-terminal region coinciding with the thumb, RNA-contact-enriched | universality (no VTG in Eco8), exclusivity (VTG in non-retrons), any general residue interval, X in most retrons |
| **6. Conserved core + variable terminal/fusion architecture** | the description most of the data supports: one core unit plus accessory content that varies by family | a boundary between core and accessory that is instrument-independent |

`PROPOSED:` vocabulary 6, anchored on vocabulary 3, is the representation this evidence actually supports.
Vocabulary 4 remains legitimate at the fold level and should be used with a named reference and its
numbering. Vocabulary 2 stays a sequence-level frame. **No winner is declared, and no combined verdict is
issued.**

---

## 8 · What surprised me

* **CAT_STATE 262 sits exactly 2 residues before the nearest catalytic aspartate in 17/17 chains.** Two
  instruments with no shared input agreeing to a constant offset across families was not expected.
* **The catalytic site is outside the called palm-like unit in 4/9 palm-CALL chains, and in one case
  inside the *fingers*-like unit.** The palm-like label is weaker than its name suggests.
* **The site-containing unit is replicate-stable (13/14) although the unit count almost never is (3/18).**
  Instability of a partition and instability of a landmark are different things.
* **Two 2026 papers on the same retron protein publish incompatible fingers/palm/thumb boundaries** in the
  same numbering frame. The disagreement the project was testing for exists inside the current literature.
* **All six Retron-Eco8 chains lack the "characteristic" VTG triplet**, and VTG appears in non-retron
  chains — a motif treated as diagnostic is neither universal nor exclusive here.
* **The historical product's thumb agrees with units more often than the literature's thumb does** — for
  the wrong reason: it is defined as everything after the palm.

## 9 · What I could NOT check

* **Retron catalytic architecture** — excluded by Stage 3B's own closure (X12). This is the single largest
  gap, and it is a scope decision, not a measurement.
* **21 literature sources** (Ec86, 9LPA, 24NC, 26CZ, 9IOA, 9WY8, 9K6G, 9LJE and others) returned 403 or
  paywall; MMLV RT has no obtainable numbered boundary. Supplementary files were not fetched.
* **Inouye et al. 1999 and Lampson et al. 2005 in full text** — the founding Region X/Y sources. The X/Y
  label attribution is therefore unresolved (X06), and Region X's functional evidence is second-hand.
* **Whether the RNA in each entry is the cognate msr** — contacts were counted against whatever
  polynucleotide the entry contains.
* **Sensitivity of the X/Y window rules** (the 60-residue SB7 window, the wide-window fallback). Declared
  before scanning, not swept; a different window could change the Eco8 and non-retron VTG counts (X16 note
  in S16).
* **Any catalogue-scale statement.** 62 chains, 31 groups, one fold; cryo-EM dominates (50/62).
* **`human_input_audit` is PENDING** on every number here, as on the bundles it reads.

## 10 · Stop condition and what is returned

Stopped after experimental-structure integration, as the launcher requires. **No predicted-structure
transfer, no catalogue-wide fusion scan, no ncRNA model training, and no redefinition of Stage 2, 3A or
3B.** Returned for operator review, with two decisions named:

1. **X12** — admit Stage-3B Tier-B/C truth labels descriptively (which would let Comparison A speak about
   retrons), or leave Comparison A retron-free. Default taken: leave excluded.
2. **Promotion** — whether any `PROPOSED:` statement in §2–§7 may become a thesis claim. Nothing here has
   been promoted; `CLAIM_EVIDENCE_MATRIX.tsv` marks each statement "after operator review".

Deliverables: `INPUT_PROVENANCE.tsv` · `STRUCTURE_STAGE2_CROSSWALK.tsv` · `STRUCTURE_STAGE3B_CROSSWALK.tsv` ·
`LITERATURE_BOUNDARY_AUDIT.tsv` · `XY_REGION_EVIDENCE.tsv` · `XY_REGION_ANNOTATIONS.tsv` ·
`TERMINI_FUSION_SUMMARY.tsv` · `CONTRADICTIONS_AND_UNCERTAINTY.tsv` · `CLAIM_EVIDENCE_MATRIX.tsv` ·
`STAGE3C_DECISION_REPORT.md` · 5 figures (PNG+SVG, each with its data TSV) · 40 supporting tables ·
`run.sh` reproducing all of it from the hashed frozen inputs.
