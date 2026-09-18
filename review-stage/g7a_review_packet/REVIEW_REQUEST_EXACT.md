# INDEPENDENT ADVERSARIAL REVIEW REQUEST — frozen Stage-2 RT0-RT7 historical bridge

You are the INDEPENDENT reviewer. You are a cross-provider fallback: the preferred reviewer
(Codex) is unavailable due to an external usage limit and produced ZERO scientific review
content. Nothing from that attempt may be cited in either direction.

The bundle under review AND an earlier self-audit of a DIFFERENT gate were produced by
Anthropic's Claude Opus. You are a different provider. Your independence is the point: do not
defer to the project's own conclusions.

## What you are reviewing

The frozen bundle `results/rt07_g7a_rt0_rt7_bridge/`. It attempts to establish an OPERATIONAL
HISTORICAL CORRESPONDENCE between a frozen conserved-state sequence representation and the
historical RT0-RT7 reverse-transcriptase subdomain terminology.

This is NOT a claim that RT0-RT7 are universal biological domains. Do not review it as if it
were. Equally, do not let that framing excuse a weak correspondence.

## The terminal interpretation you must CHALLENGE (do not assume it is correct)

  RT3 - ESTABLISHED OPERATIONAL CORRESPONDENCE
  RT4 - ESTABLISHED OPERATIONAL CORRESPONDENCE
  RT5 - ESTABLISHED OPERATIONAL CORRESPONDENCE
  RT7 - ESTABLISHED OPERATIONAL CORRESPONDENCE
  RT2 - PARTIAL / INTERPRETIVE
  RT6 - PARTIAL / INTERPRETIVE (especially jointly with RT5)
  RT0 - UNRESOLVED / NOT IDENTIFIABLE
  RT1 - UNRESOLVED / NOT IDENTIFIABLE

## Essential background on the frozen instrument (do not let the review violate these)

* The frozen mapper is `rtmap-1.0.0/53a1e738a19b3896`, profile `GII.deriv.hmm`, LENG 471,
  built under `hhmake -M 50`. It was NOT modified by this gate; it was executed read-only.
* It emits exactly **150 anchor states** per sequence, PLUS a separate `CAT_STATE` 262.
  `CAT_STATE` 262 is **NOT** one of the 150 anchors and must never be pooled with them.
* Per-state call vocabulary: `MAPPED` / `AMBIGUOUS` / `UNSUPPORTED` / `DELETED_STATE`.
  Only `MAPPED` is positive evidence.
* `DELETED_STATE` is an ALIGNMENT-PATH statement. It must NEVER be read as biological absence.
* `NO_SUPPORTED_MAPPING` / abstention is NOT failure and NOT biological absence.
* On the bridge substrate LtrA, the 150 anchors were MAPPED at 143/150, spanning
  profile states 107-317 and LtrA residues 97-363.
* The historical RT0/RT1 regions lie substantially UPSTREAM of residue 97.

## Hard constraints on your review

1. Absence of correspondence in the frozen instrument must NOT be converted into biological
   absence.
2. Agreement between an anchor and a historical region must NOT automatically be called a
   biological domain.
3. Numerical proximity alone (e.g. "363 is close to 364") must NOT be promoted into biological
   validation.
4. Do not claim universal RT architecture, external residue-level accuracy, or that historical
   correspondence validates the Stage-2 mapper.
5. Do not extrapolate beyond the instrument's observable span.
6. Distinguish rigorously between: (i) what the historical literature DIRECTLY STATES;
   (ii) what can be mapped operationally from historical figures/sequences/structures;
   (iii) what the PROJECT INFERRED; (iv) what the frozen instrument can ACTUALLY OBSERVE;
   (v) what remains UNOBSERVABLE or UNRESOLVED.
7. If a source is inaccessible to you, say so. NEVER treat an inaccessible source as
   supporting a claim.

## Specific propositions you must challenge

### RT0 and RT1
The project inherited, and then WITHDREW, the statement `RT0 = M1-R85; RT1/7 = R86-R364`.
Verify from the quoted primary passages below whether that statement is supported.
Determine specifically whether R85 lies in RT0, in RT1, or merely bounds a proteolytic
fragment that CONTAINS RT0.
Then decide whether RT0/RT1 are unresolved because:
  A. the historical definitions are insufficiently recoverable;
  B. the frozen instrument cannot observe the relevant region (anchors start at LtrA 97);
  C. both;
  D. another reason.
Do not infer biological absence from either failure mode.

### RT2
Is only PARTIAL/INTERPRETIVE supported, or something stronger or weaker? Identify precisely
which part is directly sourced and which part requires project interpretation.

### RT3, RT4, RT5
Independently test whether the evidence supports ESTABLISHED OPERATIONAL CORRESPONDENCE.
Check whether correspondence rests on MULTIPLE evidence types where claimed, and whether any
apparent agreement is CIRCULAR because the same sequence/profile information contributed to
both sides of the comparison.

### RT6
Challenge the decision NOT to identify RT6 independently. Does the historical evidence define
RT6 well enough to separate it from RT5 in the frozen representation? If the evidence supports
only a JOINT RT5/RT6 interpretation, say so explicitly.

### RT7
The project calls RT7 its strongest correspondence, citing historical evidence at R364/R365 and
the frozen anchor span ending near LtrA 363. Determine: what the source actually defines;
whether R364/R365 is a domain/subdomain boundary, a proteolytic/construct boundary, or another
kind of landmark; whether the ~363 endpoint agreement is genuinely informative or merely
coincidental; and whether the correspondence is independent enough to support the designation.

### Structural-source correction
The project records that an earlier plan wrongly treated PDB 6AR1 as LtrA, and corrects this:
6AR1 is a DIFFERENT group-II-intron RT (GsI-IIC, Geobacillus stearothermophilus), while
5G2X chain C is LtrA itself. Verify whether this correction is supported by the evidence below
and whether it changes any RT0-RT7 inference.

## REQUIRED OUTPUT FORMAT — return exactly these sections

### A. Evidence audit
For RT0, RT1, RT2, RT3, RT4, RT5, RT6, RT7 SEPARATELY:
  - historical definition/evidence
  - frozen-instrument observability
  - correspondence evidence
  - contradictory/limiting evidence
  - final evidential status

### B. Proposition audit
For every major g7a conclusion, one of: CONFIRMED / CONFIRMED WITH QUALIFICATION /
NOT ESTABLISHED / CONTRADICTED. Include reasoning and evidence location.

### C. Source audit
Claims verified against primary/direct sources; claims relying on secondary/project summaries;
inaccessible sources; source ambiguities. Do not silently treat an inaccessible source as
supporting a claim.

### D. Additional findings
Any error, circularity, source misreading, unsupported inference or missing limitation NOT
already recorded by the project.

### E. Strongest defensible statement
The strongest scientific statement about RT0-RT7 correspondence the evidence actually supports,
without claiming universal biological domains.

### F. Downstream-use assessment
Assess SEPARATELY: historical terminology in the thesis; figure annotation; descriptive
comparison with Stage-2 states; Stage-3 structural interpretation; classification reassessment;
treating RT0-RT7 as universal domains.
Do NOT produce a numerical score or ranking.

---

# THE EVIDENCE — verbatim from the frozen bundle

What follows is read directly from the landed, frozen artifacts. Where the project quotes a
primary source, the quote is the project's transcription; judge it as such and flag anything
you cannot verify.


===== BEGIN PREDECLARED ASSIGNMENT RULE + AMENDMENT 1 (contains the verbatim primary-source quotes from Blocker et al. 2005 and the withdrawal of the inherited boundary)  (file: results/rt07_g7a_rt0_rt7_bridge/control/ASSIGNMENT_RULE.md) =====
# Declared assignment and classification rule — written BEFORE the bridge was measured

This file is the gate's predeclaration. It fixes how a historical label may acquire an
operational correspondence, **before** `s03_bridge.py` ran and therefore before any
`state_id` → LtrA residue number existed. `run.sh` records the order.

Nothing in this file was chosen by looking at g5 or g6. Neither is an input to this gate
(`LAUNCHER_03` §4, hard input exclusion), and `INPUTS.tsv` is the check.

---

## A0 · The three routes, and what each may do

| route | evidence | may resolve a label alone? |
|---|---|---|
| **S** | a residue boundary **stated in a primary source** | yes, but only as a **LtrA-local** correspondence |
| **P** | an interval **reconstructed from primary evidence** (the six g2 blocks on ALIGN_000044 under Xiong & Eickbush's own stated criterion), with its landed uncertainty | yes, with uncertainty carried |
| **C** | a **comparator point** — the prior-frame RT1–RT7 single-point landmarks on LtrA from g3 | **no.** May corroborate; never resolves alone |

## A1 · The only source-stated residue coordinates in the held corpus

> **AMENDED — Amendment 1, below.** The original text of A1 read *"RT0 = M1–R85; RT1/7 =
> R86–R364"*. Tracing that statement to the Blocker PDF in `S1` showed it misreads a
> proteolytic **fragment** nomenclature as a **domain boundary**. The corrected reading is in
> Amendment 1 and is what the gate uses. The amendment was made **before `s03_bridge.py` ran**,
> from primary-source evidence alone, and it makes RT1 *less* well determined, not more.

Blocker et al. 2005, on LtrA, verified at the PDF in `rt07_g1` as assignment `B02`:

* a 10-kDa N-terminal proteolytic fragment **M1–R85**, whose Table 1 "domain composition" is
  given as `RT0`
* a 33-kDa fragment **R86–R364**, composition `RT1/7`
* the conserved **RT0 alanine at A39**

No other held primary source states a residue coordinate for any numbered subdomain. Xiong &
Eickbush 1990 states a construction criterion and no coordinates; Zimmerly 2001 numbers the
subdomains but its own alignment (`ALIGN_000044`) carries **zero** subdomain annotations;
Simon & Zimmerly 2008 supplies no construction procedure at all.

## A2 · The only source-stated landmark that fixes a numbered subdomain to a feature

Zimmerly, Hausner & Wu 2001, assignment `Z11`, recorded in `g1_evidence_quotes.tsv` and tested
in `g2_landmark_recovery.tsv` as statement `H05`:

> **the catalytic YxDD motif lies in subdomain 5.**

g2 independently recovered the catalytic Y/FxDD dyad inside reconstructed block 5.

## A3 · One anchored pair; everything else is ordinal

**`RT5 ↔ g2 block 5` is the single label↔interval pair anchored by a source-stated landmark.**

Every other label↔interval pair is obtained by **monotone ordinal propagation** outward from
that anchor, along both series simultaneously. Propagation is an **inference made by this
project**, recorded `project_inferred`, never `source_stated`. It is the same move g3 found
behind 24 of the prior frame's 29 blocks, and it is recorded as such rather than hidden.

## A4 · Propagation is admissible only if independently corroborated

A propagated label↔interval pair is admissible only when the Route C point landmark for that
label **falls inside** the propagated interval. Corroboration is **measured**, not assumed.

This is genuine convergence, not circularity: Route P intervals come from conservation on
`ALIGN_000044`, Route C points come from prior HMM frames built on different sequences by a
different method. Agreement between them is evidence; disagreement is recorded and the label
is `UNRESOLVED`.

Where Route C contradicts the propagation, the label is **`UNRESOLVED`**.

## A5 · Collapsed labels are never split

Where two historical labels propagate onto one interval, the pair is
**`SUPPORTED_MANY_TO_1`** and is reported jointly. A seven-way partition is not manufactured
by splitting an interval that the evidence did not split (g3 `no_seven_way_partition_to_inherit`).

## A6 · A source conflict, or an unstated junction, caps a label at `PARTIAL`

See Amendment 1 for the corrected Route S reading. Under it:

* a label whose propagated interval falls inside the **unstated RT0/RT1 junction zone
  (LtrA 39–85)** is at best `PARTIAL`. Blocker places RT0's conserved alanine at A39 *and* a
  cleavage site "in RT1" at R85, so both labels have a source-stated claim inside that window
  and the junction between them is **nowhere stated**;
* a label whose interval **straddles** a source-stated junction is at best `PARTIAL`;
* where two sources place the same label in mutually exclusive regions, the label is
  `UNRESOLVED`;
* a conflict is **reported, never resolved by preferring one source**. Blocker's coordinates are
  proteolytic cleavage sites on one protein, from a structural source that `LAUNCHER_02` §5d
  forbids from seeding the sequence partition; the numbered series is a sequence concept.
  Neither outranks the other here.

---

# Amendment 1 — corrected Route S reading, from primary-source tracing in `S1`

**Made 2026-09-18, before `s03_bridge.py` ran.** Source: the Blocker et al. 2005 PDF text,
pages 16–18 and Table 1, extracted with `pdftotext -layout` in `s01`.

## What the source actually says

> "These analyses allowed identification of the proteolysis products, pointing to two major
> cleavage sites, **one in RT1** and the other **between RT7 and domain X**. Cleavage at the
> first major site **in RT1** yielded a 10-kDa N-terminal fragment **containing RT0** (M1–R85)…"

and, in the discussion:

> "the Arg-C cleavage site **in RT1** (R85) is located in [a] β-strand"

and, on the N-terminal extension:

> "In all cases, the N-terminal portion of RT0 forms a predicted α-helix, which contains a
> **conserved alanine (LtrA A39)**…"

Table 1's right-hand column is headed **"Domain composition"** — it names what each fragment
*contains*, not where a domain begins or ends.

## The four corrected Route S facts

| id | source-stated fact | strength | what it fixes |
|---|---|---|---|
| **S-a** | the cleavage site at **R364/R365** is **"between RT7 and domain X"** | **a stated domain junction** | the **C-terminal end of the numbered series** — the single strongest coordinate in the held corpus |
| **S-b** | the cleavage site at **R85** is **"in RT1"** | a stated within-domain location | **RT1 spans residue 85** |
| **S-c** | RT0 is **contained within** M1–R85, and its N-terminal portion contains **A39** | an upper bound plus an interior point | **RT0 contains residue 39**; RT0's C-terminal edge is **not stated** |
| **S-d** | Blocker Fig. 3 draws RT0–RT7 as gray boxes on LtrA, *"as defined by Xiong and Eickbush (1990) and Zimmerly et al. (2001)"* | **inherited, figure-only** | nothing — it is a redrawing of the two earlier conventions, and extents exist only as boxes |

## What this changes

1. **There is no source-stated RT0|RT1 boundary at 85/86.** R85 is *inside* RT1. The statement
   "RT0 = M1–R85, RT1/7 = R86–R364", carried in
   `g2_reference_reconstruction/control/historical_statements.tsv` as `H09`, **overstates its
   own cited assignment `B02`**. g2 used it only as an external coordinate *test* and never to
   define anything, so no landed g2 number is affected — but the statement text is corrected here
   and the correction is reported.
2. **`S-a` is the strongest historical coordinate available**, and it bounds the *end* of the
   series rather than the beginning. The series is better determined at its C-terminus than at
   its N-terminus — the opposite of what the RT0-first framing suggests.
3. **RT0's C-terminal edge is unstated in every held source.** Combined with the unheld defining
   source (Malik, Burke & Eickbush 1999), RT0 has no stated boundary anywhere in this project's
   evidence — only an upper bound and an interior landmark.
4. `A6` is rewritten above: the 39–85 window is an **unstated junction zone**, not a conflict
   between two stated boundaries.

## Numbering control passed

Every residue identity Blocker states was checked against the LtrA record in the landed g2
reference set (`AAB06503`, 599 aa): **12 of 12 agree** — M1, R85, R86, R364, R365, K599, S372,
A39, R371, S462, K483, Y529 — as do 3 of 4 published Edman N-terminal sequences. The fourth,
`86-RMIYA`, reads `RMYIA` in the sequence: a two-residue transposition at 88/89 with position 86
agreeing, recorded as a discrepancy and **not** a numbering error. Blocker cites LtrA accession
`Q57005`; the project uses `AAB06503`/`P0A3U0` numbering. The 12/12 agreement is what licenses
treating them as one coordinate system, and it is a measurement, not an assumption.

## A7 · Frozen-state support is required on top

An interval resolves **only if at least one frozen anchor state is `MAPPED` to a LtrA residue
inside it**. The gate reports, per label: the number of supporting states, the state-id span,
and the residue span they cover.

**Zero supporting frozen states → `NO_SUPPORTED_CROSSWALK`**, whatever the literature says.
This is the step that makes the crosswalk *operational* rather than merely historical, and it
is the step that can return nothing.

Note the instrument emits **150 anchor states plus `CAT_STATE` 262**, not all 471 profile
states. Support is therefore measured against anchors only, and a region of LtrA containing no
anchor cannot be supported even if it is perfectly well defined historically. That is a
property of the frozen instrument and is reported as a limitation, not repaired.

## A8 · Point landmarks are assigned to the nearest anchor with the offset reported

A Route C point landmark is associated with the nearest `MAPPED` anchor state on LtrA. **The
residue offset between the landmark and that anchor is always reported.** An offset is never
rounded away, and a landmark is never described as "at" a state it is not at. Ties go to the
lower state id; a landmark whose nearest `MAPPED` anchor is more than **25 residues** away —
the median g2 block half-width — is recorded as having **no nearest anchor**.

## A9 · Correspondence vocabulary

Exactly one value per historical label, per `LAUNCHER_03` §7c:

`SUPPORTED_1_TO_1` · `SUPPORTED_1_TO_MANY` · `SUPPORTED_MANY_TO_1` · `PARTIAL` ·
`NO_SUPPORTED_CROSSWALK` · `UNRESOLVED`

## A10 · Terminal status vocabulary

Exactly one value per historical label, for the closure decision:

| terminal status | when |
|---|---|
| `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1`, `SUPPORTED_1_TO_MANY` or `SUPPORTED_MANY_TO_1`, with A4 corroboration and no A6 conflict |
| `PARTIAL / INTERPRETIVE CORRESPONDENCE` | `PARTIAL`, or supported but carrying an A6 source conflict |
| `UNRESOLVED / NOT IDENTIFIABLE` | `UNRESOLVED` or `NO_SUPPORTED_CROSSWALK` |

## A11 · What none of this licenses

* No RT0 occupancy, of any kind (g3 `OBJECT_MISMATCH`).
* No description of RT0–RT7 as a partition of the RT domain.
* No claim that any family lacks a historical region.
* No portable cross-family boundary from a LtrA-local correspondence. Everything measured here
  is measured **on LtrA**; transfer to other families is not tested by this gate and is not
  claimed by it.

===== END PREDECLARED ASSIGNMENT RULE + AMENDMENT 1 (contains the verbatim primary-source quotes from Blocker et al. 2005 and the withdrawal of the inherited boundary) =====


===== BEGIN HISTORICAL EVIDENCE REGISTER (one row per historical label x primary source)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_historical_evidence_register.tsv) =====
historical_label	primary_source	reference_system	reference_sequence	source_definition	source_boundary_or_landmark	evidence_class	source_stated_vs_inferred	caveat	unit	denominator
RT0	Blocker et al. 2005	LtrA proteolytic fragment map, Arg-C digestion	LtrA (cited as Q57005; project record AAB06503/P0A3U0, 599 aa)	'a 10-kDa N-terminal fragment CONTAINING RT0 (M1-R85)' (B02); 'the N-terminal portion of RT0 forms a predicted alpha-helix, which contains a conserved alanine (LtrA A39)' (PDF-VERIFIED s01).	UPPER BOUND M1-R85 plus an INTERIOR landmark A39. RT0's C-terminal edge is NOT stated.	EXPLICIT_STATED_BOUNDARY (upper bound + interior point)	source_stated	Table 1's column is headed 'Domain composition' - it names what a fragment CONTAINS. The same text places the R85 cleavage site 'in RT1', so R85 is NOT the RT0|RT1 boundary. The inherited statement 'RT0 = M1-R85' overstates this source.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT0	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT0	Malik, Burke & Eickbush 1999 (Mol Biol Evol 16(6):793)	NOT HELD - the defining source	NOT HELD	The source in which domain Z was renamed domain 0 (g1 genealogy edges G05, G06, G07, G09). Its content is not held by this project.	UNKNOWN - the source is unheld	NOT_IN_HELD_EVIDENCE	not_assessable	MISSING_PRIMARY_ASSET. Retrieval attempted 2026-09-18: Europe PMC HTTP 403, publisher page abstract-only, abstract does not mention domain 0, domain Z or numbered RT domains. Every held statement of RT0's scope CITES this source rather than deriving it.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT0	Simon & Zimmerly 2008	inherited frame; no alignment of its own	n/a	Restates the scope limit for domains 0 and 2a (g1 assignment set O11/G09).	NONE - restatement only	INHERITED_WITHOUT_DEFINITION	source_stated	g1 assessed this source as supplying NO construction procedure of its own for any numbered region.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT0	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	'Subdomain 0 can be considered an N-terminal extension of the RT domain and is conserved among non-LTR RTs' (Z02); 'subdomain 0 is conserved only between group II intron and non-LTR RTs' (Z06).	A SCOPE RULE, not a boundary: which classes the region exists in, not where it is.	EXPLICIT_STATED_BOUNDARY (scope rule only)	source_stated	Cites Malik et al. 1999 for the name (Z03) and does not derive it. ALIGN_000044 carries ZERO subdomain annotations, so the scope rule cannot be converted to coordinates on the source's own alignment.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT1	Blocker et al. 2005	LtrA proteolytic fragment map	LtrA, 599 aa	'two major cleavage sites, one IN RT1 ...'; 'the Arg-C cleavage site in RT1 (R85) is located in a beta-strand' (both PDF-VERIFIED s01).	R85 lies INSIDE RT1. This constrains RT1 to span residue 85; it is not an edge.	EXPLICIT_STATED_BOUNDARY (interior point)	source_stated	Because R85 is interior to RT1 and A39 is interior to RT0, the RT0|RT1 junction lies somewhere in LtrA 39-85 and is stated NOWHERE in the held corpus.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT1	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT1	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total. Domain 1 is explicitly flagged by the authors as the one domain NOT independently confirmed.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	The founding source's own weakest domain. g1 item U08 keeps this distinct from any modern RT1 measurement; that separation is preserved here and NOT interpreted.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT1	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT2	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT2	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	A restatable PROCEDURE, not coordinates. Any residue interval for this label is a reconstruction by this project, not a source statement.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT2	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT3	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT3	Poch et al. 1989 (via Xiong & Eickbush 1990 G02)	Poch motif series A-D over 82 RT sequences	consensus motifs	Consensus sequences with stated invariant residues (4 strictly, 18 conservatively maintained) in fixed linear order inside a 120-210 aa domain. Motif A is a predecessor of this numbered domain via genealogy edge G02.	Motif A consensus - a motif, not a block edge.	MOTIF_EVIDENCE	project_inferred	The motif-to-domain correspondence is a GENEALOGY edge recorded in g1, not a statement that the motif and the domain are the same object.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT3	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	A restatable PROCEDURE, not coordinates. Any residue interval for this label is a reconstruction by this project, not a source statement.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT3	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT4	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT4	Poch et al. 1989 (via Xiong & Eickbush 1990 G02)	Poch motif series A-D over 82 RT sequences	consensus motifs	Consensus sequences with stated invariant residues (4 strictly, 18 conservatively maintained) in fixed linear order inside a 120-210 aa domain. Motif B is a predecessor of this numbered domain via genealogy edge G02.	Motif B consensus - a motif, not a block edge.	MOTIF_EVIDENCE	project_inferred	The motif-to-domain correspondence is a GENEALOGY edge recorded in g1, not a statement that the motif and the domain are the same object.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT4	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	A restatable PROCEDURE, not coordinates. Any residue interval for this label is a reconstruction by this project, not a source statement.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT4	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT4	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	'These sites are between subdomains 4 and 5 of the RT domain (the 4/5 spacer)' (Z08); the 4/5 spacer varies from 1 to 179 aa.	A RELATIVE boundary: the 4|5 junction is where the widest inter-block gap sits.	EXPLICIT_STATED_BOUNDARY (relative position)	source_stated	Constrains the 4|5 junction ordinally, not by coordinate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT5	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT5	Poch et al. 1989 (via Xiong & Eickbush 1990 G02)	Poch motif series A-D over 82 RT sequences	consensus motifs	Consensus sequences with stated invariant residues (4 strictly, 18 conservatively maintained) in fixed linear order inside a 120-210 aa domain. Motif C is a predecessor of this numbered domain via genealogy edge G02.	Motif C consensus - a motif, not a block edge.	MOTIF_EVIDENCE	project_inferred	The motif-to-domain correspondence is a GENEALOGY edge recorded in g1, not a statement that the motif and the domain are the same object.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT5	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	A restatable PROCEDURE, not coordinates. Any residue interval for this label is a reconstruction by this project, not a source statement.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT5	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT5	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	'The catalytic YxDD motif lies in subdomain 5' (Z11).	AN ORDINAL ANCHOR: it ties subdomain 5 to a feature recoverable on any RT.	EXPLICIT_STATED_BOUNDARY (feature anchor)	source_stated	This is the ONLY source statement in the held corpus that fixes a numbered subdomain to a feature an instrument can find independently. Every other label's position is ordinal relative to it.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT6	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT6	Poch et al. 1989 (via Xiong & Eickbush 1990 G02)	Poch motif series A-D over 82 RT sequences	consensus motifs	Consensus sequences with stated invariant residues (4 strictly, 18 conservatively maintained) in fixed linear order inside a 120-210 aa domain. Motif D is a predecessor of this numbered domain via genealogy edge G02.	Motif D consensus - a motif, not a block edge.	MOTIF_EVIDENCE	project_inferred	The motif-to-domain correspondence is a GENEALOGY edge recorded in g1, not a statement that the motif and the domain are the same object.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT6	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	A restatable PROCEDURE, not coordinates. Any residue interval for this label is a reconstruction by this project, not a source statement.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT6	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT7	Blocker et al. 2005	LtrA proteolytic fragment map	LtrA, 599 aa	'two major cleavage sites, one in RT1 and the other BETWEEN RT7 AND DOMAIN X'; Table 1: 43-kDa fragment Met 1 - Arg 364 ('RT0/7'), 27-kDa fragment Arg 365 - Lys 599 ('X-D-E-1') (PDF-VERIFIED s01).	A STATED DOMAIN JUNCTION at R364/R365.	EXPLICIT_STATED_BOUNDARY (junction)	source_stated	The single strongest historical coordinate in the held corpus, and it bounds the END of the numbered series. It is a proteolytic site on ONE protein and may constrain or falsify a sequence-defined edge, never define one (LAUNCHER_02 section 5d).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT7	Blocker et al. 2005 Fig. 3	LtrA / HIV-1 RT sequence alignment figure	LtrA (Q57005) vs HIV-1 RT (P03366)	'Conserved sequence blocks RT0-RT7, AS DEFINED BY Xiong and Eickbush (1990) and Zimmerly et al. (2001), are indicated by gray boxes' (PDF-VERIFIED s01).	Extents exist only as gray boxes in a figure. No coordinates in text or table.	INHERITED_WITHOUT_DEFINITION|ALIGNMENT_BLOCK	source_stated	This is a REDRAWING of the two earlier conventions on LtrA, not an independent derivation - g1 classified Blocker's RT1-RT7 as SPELLING_ONLY_NO_INDEPENDENT_DERIVATION. Digitising the boxes is figure digitisation under LAUNCHER_02 section 5e and is NOT done in this gate.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT7	Xiong & Eickbush 1990	Xiong & Eickbush 1990 Fig. 1 alignment of 82 RT sequences in four groups; no accessioned alignment exists	Fig. 1 alignment, 82 sequences	Domains 1-7: seven peptide regions common to all elements, constructed by fixing conserved positions under the stated rule - a residue conserved in >50% of sequences in three of the four groups - and aligning between them. 42 conserved positions, 178 aa total.	NO residue coordinates. Per-block extents exist only as the printed columns of Figure 1.	MOTIF_EVIDENCE|ALIGNMENT_BLOCK	source_stated	A restatable PROCEDURE, not coordinates. Any residue interval for this label is a reconstruction by this project, not a source statement.	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT7	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	Subdomains 0-7 plus domain X, 'labeled according to previous studies (7,9,32) taking into account the boundaries of conservation seen in our alignment' (Z04, Z05). Per-group conserved-residue counts: 90 mitochondrial, 94 bacterial (Z10).	NO residue coordinates; ALIGN_000044 carries zero subdomain annotations.	ALIGNMENT_BLOCK	source_stated	Labels are inherited from earlier work and adjusted to conservation boundaries (Z04). The adjustment step included manual editing and is not reproducible (g1 U05).	(historical label, primary source) pair	8 historical labels x the primary sources that name them
RT7	Zimmerly, Hausner & Wu 2001	Zimmerly, Hausner & Wu 2001 alignment ALIGN_000044 (EMBL), 66 sequences x 1441 columns, RT domain at columns 261-886	ALIGN_000044 consensus	'... and between subdomain 7 and domain X (the 7/X spacer)' (Z08); the 7/X spacer ranges 0-235 aa.	A RELATIVE boundary for the C-terminal end of the numbered series.	EXPLICIT_STATED_BOUNDARY (relative position)	source_stated	Domain X was not reconstructed by g2, so the far side of this junction is not independently available.	(historical label, primary source) pair	8 historical labels x the primary sources that name them

===== END HISTORICAL EVIDENCE REGISTER (one row per historical label x primary source) =====


===== BEGIN COORDINATE CARRIAGE (every historical coordinate on LtrA, by evidence route)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_coordinate_carriage.tsv) =====
coordinate_id	route	historical_label	ltra_start	ltra_end	coordinate_kind	evidence_class	source_stated_vs_inferred	source	uncertainty	note	unit	frame	denominator
S-a	S	RT7	364	365	stated_domain_junction	EXPLICIT_STATED_BOUNDARY	source_stated	Blocker et al. 2005, PDF-verified in s01 (g1 assignment B02 plus Table 1 and text)	the junction is a proteolytic cleavage site between R364 and R365; the site is stated, the domain edge is inferred to coincide with it	'two major cleavage sites, one in RT1 and the other BETWEEN RT7 AND DOMAIN X'. The strongest historical coordinate in the held corpus. It bounds the END of the numbered series.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
S-b	S	RT1	85	85	stated_interior_point	EXPLICIT_STATED_BOUNDARY	source_stated	Blocker et al. 2005, PDF-verified in s01 (g1 assignment B02 plus Table 1 and text)	a point, not an edge	'the Arg-C cleavage site IN RT1 (R85)'. RT1 spans residue 85. This is NOT an RT0|RT1 boundary.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
S-c1	S	RT0	1	85	stated_upper_bound	EXPLICIT_STATED_BOUNDARY	source_stated	Blocker et al. 2005, PDF-verified in s01 (g1 assignment B02 plus Table 1 and text)	an UPPER BOUND on RT0's extent, not RT0's extent	'a 10-kDa N-terminal fragment CONTAINING RT0 (M1-R85)'. Table 1's column is headed 'Domain composition'.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
S-c2	S	RT0	39	39	stated_interior_point	EXPLICIT_STATED_BOUNDARY	source_stated	Blocker et al. 2005, PDF-verified in s01 (g1 assignment B02 plus Table 1 and text)	a point, not an edge	the conserved alanine in the N-terminal portion of RT0. RT0 contains residue 39.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
S-d	S	RT0|RT1	39	85	unstated_junction_zone	NO_STATED_BOUNDARY	project_inferred	derived from S-b and S-c2	the entire 47-residue window is unresolved	RT0 contains 39 and RT1 contains 85, so the junction between them lies in 39-85 and is stated NOWHERE in the held corpus.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
P-1	P	(unlabelled g2 block)	39	61	primary_derived_interval	ALIGNMENT_BLOCK	project_inferred	rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion	reported_start_column=264; reported_end_column=288; start_column_min=264; start_column_max=285; end_column_min=264; end_column_max=288; start_uncertainty_columns=21; end_uncertainty_columns=24; n_overlapping_blocks_across_sweep=150; n_conserved_positions_min=1; n_conserved_positions_max=5; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	g2 block 1. Cross-frame correspondence: ONE_TO_ONE (Jaccard 0.739 on LtrA residues). g2 recovered SIX blocks, not seven. Labels are attached in s04 by the declared rule, never here.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
P-2	P	(unlabelled g2 block)	79	123	primary_derived_interval	ALIGNMENT_BLOCK	project_inferred	rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion	reported_start_column=321; reported_end_column=375; start_column_min=321; start_column_max=375; end_column_min=323; end_column_max=375; start_uncertainty_columns=54; end_uncertainty_columns=52; n_overlapping_blocks_across_sweep=231; n_conserved_positions_min=1; n_conserved_positions_max=22; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	g2 block 2. Cross-frame correspondence: ONE_TO_ONE (Jaccard 1.000 on LtrA residues). g2 recovered SIX blocks, not seven. Labels are attached in s04 by the declared rule, never here.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
P-3	P	(unlabelled g2 block)	126	166	primary_derived_interval	ALIGNMENT_BLOCK	project_inferred	rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion	reported_start_column=432; reported_end_column=479; start_column_min=432; start_column_max=471; end_column_min=432; end_column_max=479; start_uncertainty_columns=39; end_uncertainty_columns=47; n_overlapping_blocks_across_sweep=246; n_conserved_positions_min=1; n_conserved_positions_max=16; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	g2 block 3. Cross-frame correspondence: ONE_TO_ONE (Jaccard 0.911 on LtrA residues). g2 recovered SIX blocks, not seven. Labels are attached in s04 by the declared rule, never here.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
P-4	P	(unlabelled g2 block)	170	230	primary_derived_interval	ALIGNMENT_BLOCK	project_inferred	rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion	reported_start_column=518; reported_end_column=590; start_column_min=518; start_column_max=576; end_column_min=518; end_column_max=590; start_uncertainty_columns=58; end_uncertainty_columns=72; n_overlapping_blocks_across_sweep=238; n_conserved_positions_min=1; n_conserved_positions_max=20; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	g2 block 4. Cross-frame correspondence: SPLIT_INTO_3 (Jaccard 0.410 on LtrA residues). g2 recovered SIX blocks, not seven. Labels are attached in s04 by the declared rule, never here.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
P-5	P	(unlabelled g2 block)	304	347	primary_derived_interval	ALIGNMENT_BLOCK	project_inferred	rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion	reported_start_column=781; reported_end_column=827; start_column_min=781; start_column_max=824; end_column_min=786; end_column_max=827; start_uncertainty_columns=43; end_uncertainty_columns=41; n_overlapping_blocks_across_sweep=238; n_conserved_positions_min=1; n_conserved_positions_max=14; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	g2 block 5. Cross-frame correspondence: ONE_TO_ONE (Jaccard 0.955 on LtrA residues). g2 recovered SIX blocks, not seven. Labels are attached in s04 by the declared rule, never here.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
P-6	P	(unlabelled g2 block)	356	361	primary_derived_interval	ALIGNMENT_BLOCK	project_inferred	rt07_g2_reference_reconstruction, reconstructed on ALIGN_000044 under Xiong & Eickbush's stated >50%-in-three-of-four-groups criterion	reported_start_column=880; reported_end_column=885; start_column_min=880; start_column_max=885; end_column_min=882; end_column_max=885; start_uncertainty_columns=5; end_uncertainty_columns=3; n_overlapping_blocks_across_sweep=120; n_conserved_positions_min=1; n_conserved_positions_max=4; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	g2 block 6. Cross-frame correspondence: ONE_TO_ONE (Jaccard 1.000 on LtrA residues). g2 recovered SIX blocks, not seven. Labels are attached in s04 by the declared rule, never here.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT1	C	RT1	49	49	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT2	C	RT2	102	102	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT3	C	RT3	160	160	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT4	C	RT4	213	213	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT5	C	RT5	308	308	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT6	C	RT6	344	344	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate
C-RT7	C	RT7	357	357	comparator_point_landmark	PRIOR_FRAME_POINT	project_inferred	rt07_g3_prior_method_replication, prior frame RT17_CORE	a single point; agreement across 4 prior frames: ALL AGREE	COMPARATOR ONLY (LAUNCHER_03 section 7b). 24 of the prior frame's 29 blocks were placed by interpolating order between only 4 motif-anchored blocks.	historical coordinate on LtrA	LtrA P0A3U0 / AAB06503 residue numbering, 1-based, 599 aa	historical coordinates carried onto LtrA by this gate

===== END COORDINATE CARRIAGE (every historical coordinate on LtrA, by evidence route) =====


===== BEGIN THE RESOLVED CROSSWALK (correspondence class per label)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv) =====
historical_label	correspondence	operational_states	n_supporting_states	state_span	ltra_residue_span_supported	reference_interval_ltra	reference_interval_source	mapping_route	route_c_point	route_c_offset_to_nearest_mapped_anchor	nearest_mapped_anchor_state	uncertainty	status_reason	unit	frame	denominator
RT0	NO_SUPPORTED_CROSSWALK		0			1-85	Blocker 2005 UPPER BOUND (S-c1) plus the interior landmark A39 (S-c2). No stated extent.	S (upper bound + interior point)				n/a	ZERO frozen anchor states map inside LtrA 1-85. The 150 anchors cover LtrA 97-363 only, so this region lies OUTSIDE the instrument's anchor span entirely (rule A7). This is a property of the frozen instrument, not a statement about the biology. | g3 ruled RT0 OBJECT_MISMATCH and no RT0 occupancy may be reported. Its defining source (Malik, Burke & Eickbush 1999) is a MISSING_PRIMARY_ASSET, so RT0 has no stated boundary anywhere in this project's evidence - only an upper bound and an interior point.	historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT1	NO_SUPPORTED_CROSSWALK		0			39-61	g2 reconstructed block 1 (Route P)	P interval, anchored via A3, corroborated by C	49	nearest MAPPED anchor is 48 residues away, beyond the declared 25	NONE	reported_start_column=264; reported_end_column=288; start_column_min=264; start_column_max=285; end_column_min=264; end_column_max=288; start_uncertainty_columns=21; end_uncertainty_columns=24; n_overlapping_blocks_across_sweep=150; n_conserved_positions_min=1; n_conserved_positions_max=5; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	ZERO frozen anchor states map inside LtrA 39-61. The 150 anchors cover LtrA 97-363 only, so this region lies OUTSIDE the instrument's anchor span entirely (rule A7). This is a property of the frozen instrument, not a statement about the biology. | RT1 is additionally the only landmark that MOVES between prior frames (g3), and Blocker places R85 INSIDE RT1, so RT1 spans the junction zone.	historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT2	PARTIAL	107,108,109,110,111,115,116,117,118,119,127,128,129,130,131,132,133	17	107-133	97-123	79-123	g2 reconstructed block 2 (Route P)	P interval, anchored via A3, corroborated by C	102	-1	111	reported_start_column=321; reported_end_column=375; start_column_min=321; start_column_max=375; end_column_min=323; end_column_max=375; start_uncertainty_columns=54; end_uncertainty_columns=52; n_overlapping_blocks_across_sweep=231; n_conserved_positions_min=1; n_conserved_positions_max=22; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	the reference interval 79-123 extends beyond the anchor span 97-363; only LtrA 97-123 carries frozen-state support | the interval overlaps the UNSTATED RT0/RT1 junction zone 39-85: Blocker places RT0's conserved alanine at A39 and a cleavage site 'in RT1' at R85, so both labels have a source-stated claim there and the junction is stated nowhere (rule A6)	historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT3	SUPPORTED_1_TO_1	136,137,138,139,140,145,146,157,158,159,160,162,163,169,170,171,172,173,174,175,176,177	22	136-177	126-166	126-166	g2 reconstructed block 3 (Route P)	P interval, anchored via A3, corroborated by C	160	0	171	reported_start_column=432; reported_end_column=479; start_column_min=432; start_column_max=471; end_column_min=432; end_column_max=479; start_uncertainty_columns=39; end_uncertainty_columns=47; n_overlapping_blocks_across_sweep=246; n_conserved_positions_min=1; n_conserved_positions_max=16; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed		historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT4	SUPPORTED_1_TO_1	181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,228,229,230,231,232,236,237,238,239,240,241	42	181-241	170-230	170-230	g2 reconstructed block 4 (Route P)	P interval, anchored via A3, corroborated by C	213	4	228	reported_start_column=518; reported_end_column=590; start_column_min=518; start_column_max=576; end_column_min=518; end_column_max=590; start_uncertainty_columns=58; end_uncertainty_columns=72; n_overlapping_blocks_across_sweep=238; n_conserved_positions_min=1; n_conserved_positions_max=20; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed		historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT5	SUPPORTED_MANY_TO_1	267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,299,300,301	34	267-301	311-347	304-347	g2 reconstructed block 5 (Route P)	P interval, ANCHORED by the source-stated catalytic landmark (Z11), measured by PC-4	308	3	267	reported_start_column=781; reported_end_column=827; start_column_min=781; start_column_max=824; end_column_min=786; end_column_max=827; start_uncertainty_columns=43; end_uncertainty_columns=41; n_overlapping_blocks_across_sweep=238; n_conserved_positions_min=1; n_conserved_positions_max=14; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	RT5 and RT6 both fall in g2 block 5 and are NOT separable within it (rule A5). Reported jointly.	historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT6	SUPPORTED_MANY_TO_1	267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,299,300,301	34	267-301	311-347	304-347	g2 reconstructed block 5 (Route P)	P interval, anchored via A3, corroborated by C	344	-1	297	reported_start_column=781; reported_end_column=827; start_column_min=781; start_column_max=824; end_column_min=786; end_column_max=827; start_uncertainty_columns=43; end_uncertainty_columns=41; n_overlapping_blocks_across_sweep=238; n_conserved_positions_min=1; n_conserved_positions_max=14; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	RT5 and RT6 both fall in g2 block 5 and are NOT separable within it (rule A5). Reported jointly. | RT6 carries no anchor of its own: only ordinal adjacency to the anchored RT5 and a Route C point, which is comparator evidence and may not resolve alone (rule A4, route kill). The JOINT RT5+RT6 statement is supported; RT6's own position inside block 5 is not.	historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels
RT7	SUPPORTED_1_TO_1	310,311,312,313,314,315	6	310-315	356-361	356-361	g2 reconstructed block 6 (Route P)	P interval, anchored via A3, corroborated by C	357	0	311	reported_start_column=880; reported_end_column=885; start_column_min=880; start_column_max=885; end_column_min=882; end_column_max=885; start_uncertainty_columns=5; end_uncertainty_columns=3; n_overlapping_blocks_across_sweep=120; n_conserved_positions_min=1; n_conserved_positions_max=4; edge_precision_claim=INTERVAL_ONLY - the sources state a procedure and no residue edges, so no single-column edge is claimed	Independently corroborated by the strongest historical coordinate in the corpus: Blocker's stated junction 'between RT7 and domain X' at R364/R365 (S-a). The anchor span ends at LtrA 363 and g2 block 6 ends at 361 - three routes agree the numbered series ends at about 357-365.	historical label	frozen GII.deriv.hmm state_id (LENG 471, hhmake -M 50) <-> LtrA P0A3U0 residue numbering	8 historical labels

===== END THE RESOLVED CROSSWALK (correspondence class per label) =====


===== BEGIN CLOSURE DECISION (terminal status + permitted downstream wording per label)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_closure_decision.tsv) =====
historical_label	terminal_status	correspondence	supporting_states	ltra_residues_supported	evidence_basis	downstream_may_say	downstream_may_not_say	unit	denominator
RT0	UNRESOLVED / NOT IDENTIFIABLE	NO_SUPPORTED_CROSSWALK			Its defining source (Malik, Burke & Eickbush 1999) is a MISSING_PRIMARY_ASSET. The held sources give a scope rule, an upper bound (M1-R85, which CONTAINS RT0) and an interior landmark (A39) - no boundary. Zero frozen anchor states lie in LtrA 1-85.	Nothing operational. RT0 may be discussed as a HISTORICAL concept with its scope rule - conserved between group II intron and non-LTR RTs - and as a region of LtrA bounded above by residue 85 and containing the conserved alanine A39. No RT0 occupancy, fraction, count or boundary may be reported on any population.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT1	UNRESOLVED / NOT IDENTIFIABLE	NO_SUPPORTED_CROSSWALK			Zero frozen anchor states lie in LtrA 39-61, the interval the evidence places RT1 in: the instrument's 150 anchors begin at LtrA 97. RT1 is additionally the only landmark that moves between prior frames, and Blocker places the R85 cleavage site INSIDE RT1.	Nothing operational. RT1 may be discussed historically, including the founding authors' own statement that domain 1 was the one domain not independently confirmed, and Blocker's placement of R85 within it. No RT1 occupancy or boundary may be reported. Whether a modern RT1 result recovers the 1990 caveat remains a DEFERRED OPERATOR DECISION (g1 U08) and is not settled here.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT2	PARTIAL / INTERPRETIVE CORRESPONDENCE	PARTIAL	107,108,109,110,111,115,116,117,118,119,127,128,129,130,131,132,133	97-123	17 frozen anchor states map inside LtrA 79-123, but the interval extends below the anchor span, so only LtrA 97-123 carries support; the interval also overlaps the unstated RT0/RT1 junction zone.	'Frozen states 107-133 (LtrA 97-123) overlap a literature-supported portion of historical RT2.' The word 'portion' is load-bearing: the N-terminal part of the RT2 interval has no frozen-state support. Do not write 'RT2 is states 107-133'.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT3	ESTABLISHED OPERATIONAL CORRESPONDENCE	SUPPORTED_1_TO_1	136,137,138,139,140,145,146,157,158,159,160,162,163,169,170,171,172,173,174,175,176,177	126-166	22 frozen anchor states map inside LtrA 126-166, the interval is wholly within the anchor span, and the Route C comparator point falls inside it.	'The signal localises to frozen states 136-177; these states overlap a literature-supported portion of historical RT3.' A correspondence measured on LtrA, with 22 supporting states.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT4	ESTABLISHED OPERATIONAL CORRESPONDENCE	SUPPORTED_1_TO_1	181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,228,229,230,231,232,236,237,238,239,240,241	170-230	42 frozen anchor states map inside LtrA 170-230, the interval is wholly within the anchor span, and the Route C comparator point falls inside it.	'The signal localises to frozen states 181-241; these states overlap a literature-supported portion of historical RT4.' A correspondence measured on LtrA, with 42 supporting states.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT5	ESTABLISHED OPERATIONAL CORRESPONDENCE	SUPPORTED_MANY_TO_1	267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,299,300,301	311-347	RT5 and RT6 both fall in g2 block 5 and are NOT separable within it. RT5 carries the single source-stated anchor in the whole corpus - 'the catalytic YxDD motif lies in subdomain 5' - which the frozen instrument independently confirmed by placing CAT_STATE 262 at LtrA residue 306, inside block 5.	'The signal localises to frozen states 267-301; these states overlap a literature-supported portion of the joint historical RT5+RT6 region.' RT5 is the ONLY label with a source-stated feature anchor. The region must be named RT5+RT6 jointly, never RT5 alone.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT6	PARTIAL / INTERPRETIVE CORRESPONDENCE	SUPPORTED_MANY_TO_1	267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,299,300,301	311-347	DOWNGRADED by declared rule D1: this label's individual position rests only on comparator (Route C) evidence | RT5 and RT6 both fall in g2 block 5 and are NOT separable within it. RT5 carries the single source-stated anchor in the whole corpus - 'the catalytic YxDD motif lies in subdomain 5' - which the frozen instrument independently confirmed by placing CAT_STATE 262 at LtrA residue 306, inside block 5.	Only as part of the joint region: 'frozen states 267-301 overlap the joint historical RT5+RT6 region.' No statement may attribute a state to RT6 rather than RT5 - the two are not separable on this evidence.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels
RT7	ESTABLISHED OPERATIONAL CORRESPONDENCE	SUPPORTED_1_TO_1	310,311,312,313,314,315	356-361	6 frozen anchor states map inside LtrA 356-361, the interval is wholly within the anchor span, and the Route C comparator point falls inside it. | Independently corroborated by the strongest historical coordinate in the corpus: Blocker's stated junction 'between RT7 and domain X' at R364/R365. Three routes agree the numbered series ends at about 357-365.	'The signal localises to frozen states 310-315; these states overlap a literature-supported portion of historical RT7.' A correspondence measured on LtrA, with 6 supporting states.	May not be called a partition of the RT domain; may not be used to claim a family lacks this region (DELETED_STATE is an alignment-path state); may not be transferred to another protein without a new measurement - every correspondence here was measured ON LtrA.	historical label	8 historical labels

===== END CLOSURE DECISION (terminal status + permitted downstream wording per label) =====


===== BEGIN CONTROLS (positive and negative, all reported)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_controls.tsv) =====
control_id	kind	expectation	observed	result	note
NC-1	negative control	does not produce a confident mapping comparable to real LtrA	verdict=ABSTAIN, mapped 0/150 (0.0000), bitscore -2.7, E-value 0.097	PASS	seeded shuffle. Compared against LtrA's 0.9533. LAUNCHER_03 section 2 negative-control kill.
NC-2	negative control	does not produce a confident mapping comparable to real LtrA	verdict=ABSTAIN, mapped 0/150 (0.0000), bitscore -3.8, E-value 0.21	PASS	reversed. Compared against LtrA's 0.9533. LAUNCHER_03 section 2 negative-control kill.
NC-3	negative control	does not produce a confident mapping comparable to real LtrA	NOT TESTED - produced no scientific row: INPUT_INVALID / BELOW_MIN_LENGTH (246 aa < registered minimum 250)	INCONCLUSIVE	out-of-population real protein. The sequence was rejected by the FROZEN eligibility rule BEFORE it reached the mapper, so this is not evidence that the mapper abstains on it - it is evidence that the sequence is outside the population the instrument is ever applied to. Recorded as inconclusive rather than counted as a pass. The valid negatives for this gate are NC-1 and NC-2, which both reached the mapper and both ABSTAINED at 0/150.
NC-4	anti-circularity	no g5 or g6 path is read by this gate	checked in verify.sh against INPUTS.tsv and the scripts	SEE_VERIFY	LAUNCHER_03 section 4 hard input exclusion.
PC-1	positive control - catalytic	CAT_STATE 262 lands on the LtrA Y/FxDD catalytic dyad	cat_call_state=MAPPED, residue 306 (Y), window YADD, class CATALYTIC_CONFIRMED, 1 dyad motif(s) in the sequence	PASS	The sharpest independent check on the state->residue bridge: the one operational coordinate the frozen instrument commits to, on the one protein the history is denominated in. LAUNCHER_03 section 2 positive-control kill.
PC-2	anchor span - a LIMITATION, measured	the 150 anchors do not cover the whole protein; the covered span is reported	MAPPED anchors span state_id 107-317 and LtrA residues 97-363; 143 of 150 anchors MAPPED	MEASURED	This is the binding constraint on the crosswalk: a historical region outside LtrA 97-363 CANNOT receive frozen-state support however well defined it is historically (declared rule A7). It is a property of the frozen instrument, not of the biology, and it is not repaired.
PC-3	structural numbering control	5G2X chain C author numbering agrees with P0A3U0 at every modelled residue, and Blocker's landmarks A39/R85/R86 are present in the structure	487/487 modelled residues agree; residue 39=A, 85=R, 86=R, 364=not modelled	PASS	Zero offset. This is what makes 5G2X usable as a coordinate comparator at all, and it is measured here rather than inherited from the prior reference_boundaries extraction, which is DO-NOT-USE.
PC-4	positive control - the Zimmerly anchor is MEASURED	the catalytic residue lies inside g2 block 5 (LtrA 304-347), which is what makes 'the catalytic YxDD lies in subdomain 5' (Z11) an anchor rather than an assumption	catalytic residue 306; g2 block 5 = LtrA 304-347	PASS	Declared rule A2/A3. If this fails, the single anchored label<->interval pair is lost and every label becomes ordinal with no anchor.
PC-5	positive control - LtrA is inspectable	the frozen instrument commits on LtrA (verdict MAPPED)	verdict=MAPPED, mapped 143/150 (0.9533), domain bitscore 378.1, E-value 3.2e-117	PASS	LAUNCHER_03 section 2 substrate kill.

===== END CONTROLS (positive and negative, all reported) =====


===== BEGIN LtrA NUMBERING CONTROL (Blocker-stated residue identities checked against the project's LtrA record)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_ltra_numbering_control.tsv) =====
check_id	kind	expected	observed	result	note
NUM-1	stated_residue_identity	M1	M1	AGREE	Table 1, 10-kDa fragment start
NUM-85	stated_residue_identity	R85	R85	AGREE	Table 1, 10-kDa fragment end; text: cleavage site IN RT1
NUM-86	stated_residue_identity	R86	R86	AGREE	Table 1, 33-kDa and 60-kDa fragment start
NUM-364	stated_residue_identity	R364	R364	AGREE	Table 1, 33-kDa and 43-kDa fragment end
NUM-365	stated_residue_identity	R365	R365	AGREE	Table 1, 27-kDa fragment start; junction RT7/domain X
NUM-599	stated_residue_identity	K599	K599	AGREE	Table 1, 60-kDa and 27-kDa fragment end
NUM-372	stated_residue_identity	S372	S372	AGREE	Table 1, X-D-E-2 fragment start
NUM-39	stated_residue_identity	A39	A39	AGREE	text: conserved alanine in the N-terminal portion of RT0
NUM-371	stated_residue_identity	R371	R371	AGREE	discussion, R371
NUM-462	stated_residue_identity	S462	S462	AGREE	Fig. 3 legend, key residue
NUM-483	stated_residue_identity	K483	K483	AGREE	Fig. 3 legend, key residue
NUM-529	stated_residue_identity	Y529	Y529	AGREE	Fig. 3 legend, key residue
EDMAN-1	published_N_terminal_sequence	1-MKPTM	1-MKPTM	AGREE	Edman degradation N-term, Blocker Table 1
EDMAN-86	published_N_terminal_sequence	86-RMIYA	86-RMYIA	DISAGREE	Edman degradation N-term, Blocker Table 1
EDMAN-365	published_N_terminal_sequence	365-RSGTI	365-RSGTI	AGREE	Edman degradation N-term, Blocker Table 1
EDMAN-372	published_N_terminal_sequence	372-SGKVK	372-SGKVK	AGREE	Edman degradation N-term, Blocker Table 1
NUM-SUMMARY	summary	12 stated residue identities agree	12/12 agree; 3/4 Edman sequences agree	PASS	This is what licenses treating Blocker's LtrA coordinates and the project's AAB06503/P0A3U0 record as ONE coordinate system. A measurement, not an assumption.

===== END LtrA NUMBERING CONTROL (Blocker-stated residue identities checked against the project's LtrA record) =====


===== BEGIN STRUCTURAL COMPARATORS (5G2X / 6AR1 / 7V9U, with independence verdicts)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_structural_comparators.tsv) =====
comparator	chain	protein	relation_to_ltra_frame	independence_verdict	independence_basis	expression_tag	numbering_agreement	what_it_says_about_the_crosswalk	agreement_class	caveat	unit	frame	denominator
5G2X	C	Lactococcus lactis LtrA P0A3U0	THE SAME PROTEIN - the structure of LtrA itself	NOT_INDEPENDENT	5G2X is an anchor-set member (in_26_anchor_set=YES) and g3 measured anchors72 at 100% seed membership. It is therefore a crosswalk ILLUSTRATION, not an independent test.	none - no tag offset to remove	487/487 modelled residues agree with the project's LtrA record (AAB06503/P0A3U0); modelled range 4-592	RT0: no supported span; RT1: no supported span; RT2: 27/27 supported residues modelled; RT3: 41/41 supported residues modelled; RT4: 61/61 supported residues modelled; RT5: 37/37 supported residues modelled; RT6: 37/37 supported residues modelled; RT7: 6/6 supported residues modelled	AGREES_ON_COORDINATES	Agreement here is agreement about RESIDUE NUMBERING, which is what the crosswalk needs from this structure. It is NOT independent evidence that a historical label is correctly placed, and it cannot be: structure may not manufacture the seven-way partition.	structural comparator	PDB author residue numbering vs LtrA P0A3U0	3 declared structural comparators
6AR1	A	Geobacillus stearothermophilus GsI-IIC RT E2GM63	A DIFFERENT PROTEIN - no held source states an RT0-RT7 coordinate on it	NOT_INDEPENDENT	anchor-set member (in_26_anchor_set=YES); g3 measured anchors72 at 100% seed membership	His8 C-terminal - residue numbering from a tagged construct is offset by the tag length and was NOT used to place any boundary	not applicable - a different protein, not compared residue by residue to LtrA	the frozen instrument commits on this protein (141/150 anchors, mapped fraction 0.9400), so the SAME state_ids are locatable in it. It therefore shows the frozen state axis is not LtrA-specific. It says NOTHING about where a historical label sits, because no held source states an RT0-RT7 coordinate on this protein.	NON_COMPARABLE_FOR_THE_HISTORICAL_LABELS	Included to test whether the frozen state axis transfers as a COORDINATE SYSTEM, not to place a historical label. Panel sequences are built from MODELLED residues only and carry internal chain breaks.	structural comparator	PDB author residue numbering	3 declared structural comparators
7V9U	A	E. coli retron Ec86 P23070	A DIFFERENT PROTEIN - no held source states an RT0-RT7 coordinate on it	NOT_INDEPENDENT	anchor-set member (in_26_anchor_set=YES); g3 measured anchors72 at 100% seed membership	none	not applicable - a different protein, not compared residue by residue to LtrA	the frozen instrument commits on this protein (63/150 anchors, mapped fraction 0.4200), so the SAME state_ids are locatable in it. It therefore shows the frozen state axis is not LtrA-specific. It says NOTHING about where a historical label sits, because no held source states an RT0-RT7 coordinate on this protein.	NON_COMPARABLE_FOR_THE_HISTORICAL_LABELS	Included to test whether the frozen state axis transfers as a COORDINATE SYSTEM, not to place a historical label. Panel sequences are built from MODELLED residues only and carry internal chain breaks.	structural comparator	PDB author residue numbering	3 declared structural comparators

===== END STRUCTURAL COMPARATORS (5G2X / 6AR1 / 7V9U, with independence verdicts) =====


===== BEGIN ACQUISITION REGISTER (the missing primary asset for RT0)  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_acquisition_register.tsv) =====
asset_id	asset	why_needed	attempt_date	route_1	route_1_result	route_2	route_2_result	resolution_state	usable_as_evidence	consequence	governed_acquisition_note
malik1999_domain0_definition	Malik, Burke & Eickbush 1999, Mol Biol Evol 16(6):793-805	The source in which domain Z was renamed domain 0. It is the defining source for RT0 and is cited, not derived, by every held source that states RT0's scope.	2026-09-18	Europe PMC article page	FAILED_HTTP_403	Publisher page (academic.oup.com/mbe/article/16/6/793/2925486)	ABSTRACT_ONLY - full text not accessible; the abstract does not mention domain 0, domain Z or numbered RT domains	MISSING_PRIMARY_ASSET	NO	RT0 has no stated boundary anywhere in this project's evidence. This is recorded as a terminal evidence state, not as an open task.	Any route requiring credentials, payment or a paywall bypass is a stop-and-wait operator decision (LAUNCHER_03 section 9b). None was attempted.

===== END ACQUISITION REGISTER (the missing primary asset for RT0) =====


===== BEGIN COMPARISON AGAINST THE PRIOR PROPOSED MAPPING  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_prior_proposal_comparison.tsv) =====
historical_label	prior_proposal_cardinality	prior_proposal_object	g7a_measured_correspondence	agreement	note
RT0	NO_VALID_CORRESPONDENCE	none	NO_SUPPORTED_CROSSWALK	AGREES	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT1	UNRESOLVED	g2 region 1	NO_SUPPORTED_CROSSWALK	AGREES	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT2	1:1 candidate	g2 region 2	PARTIAL	DIFFERS	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT3	1:1 candidate	g2 region 3	SUPPORTED_1_TO_1	AGREES	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT4	1:many	g2 region 4	SUPPORTED_1_TO_1	DIFFERS	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT5	many:1 - jointly with RT6	g2 region 5	SUPPORTED_MANY_TO_1	AGREES	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT6	many:1 - jointly with RT5	g2 region 5	SUPPORTED_MANY_TO_1	AGREES	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.
RT7	1:1 candidate	g2 region 6	SUPPORTED_1_TO_1	AGREES	The prior table is a PROPOSAL made before the mapper was frozen and before any state->residue measurement existed. It is a hypothesis this gate tested, never a result inherited.

===== END COMPARISON AGAINST THE PRIOR PROPOSED MAPPING =====


===== BEGIN UNRESOLVED ITEMS CARRIED FORWARD  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_unresolved_carried_forward.tsv) =====
item_id	question	status_after_g7a	what_g7a_changed
U01	Where is the primary definition of domain 0 / RT0?	CLOSED_AS_MISSING_PRIMARY_ASSET	Retrieval of Malik, Burke & Eickbush 1999 was attempted and failed (Europe PMC 403; publisher abstract-only, and the abstract does not mention domain 0, domain Z or numbered RT domains). Combined with the measured absence of any frozen anchor state in LtrA 1-85, RT0's status is now TERMINAL rather than open: UNRESOLVED / NOT IDENTIFIABLE.
U02	Which blocks do Simon & Zimmerly's 59 alignable characters fall in?	STILL_OPEN - belongs to g7b	Not addressed. It is a published-comparator question.
U06	Is Blocker's RT0 (M1-R85) boundary transferable beyond LtrA?	CLOSED_BY_CORRECTION	The premise was wrong. M1-R85 is not an RT0 boundary even ON LtrA: Blocker states the R85 cleavage site is IN RT1 and that the fragment CONTAINS RT0. The question of transferring it does not arise. See control/ASSIGNMENT_RULE.md Amendment 1.
U08	Is domain 1's weaker support in 1990 the same object as a later RT1 concordance failure?	STILL_DEFERRED_TO_OPERATOR	g7a measured RT1 (NO_SUPPORTED_CROSSWALK: zero anchors in LtrA 39-61) and did NOT interpret it. The two objects remain distinct. LAUNCHER_02 section 9b reserves this to the operator.
U09	Is the block COUNT recoverable at all?	STILL_OPEN	g7a adds one fact: the frozen instrument's 150 anchors resolve the region of LtrA carrying blocks 2-6 but none of block 1, so no instrument in this project can currently count seven.
U11	What is the tag offset in the tagged anchors?	NOT_NEEDED_FOR_THIS_GATE	The primary structural comparator 5G2X is UNTAGGED and its numbering agrees with P0A3U0 at 487/487 modelled residues. No residue coordinate in this gate was read off a tagged construct.
G7A-1	Does the frozen anchor span limit the crosswalk, and can that be repaired?	NEW - ANSWERED, AND NOT REPAIRED	Measured: the 150 anchors span LtrA 97-363 on the bridge substrate. Everything N-terminal to 97 is unreachable by the frozen instrument. Repairing it would mean rebuilding the instrument, which LAUNCHER_03 section 3 forbids and section 2 makes a scope kill. It is recorded as a property of the instrument.

===== END UNRESOLVED ITEMS CARRIED FORWARD =====


===== BEGIN RESOLVED-VALUE SUMMARY  (file: results/rt07_g7a_rt0_rt7_bridge/tables/g7a_summary.tsv) =====
quantity	value	source_table	unit	denominator
historical_labels_in_scope	8	g7a_closure_decision.tsv	historical label	8 historical labels
terminal_ESTABLISHED	4	g7a_closure_decision.tsv	historical label	8 historical labels
terminal_PARTIAL	2	g7a_closure_decision.tsv	historical label	8 historical labels
terminal_UNRESOLVED	2	g7a_closure_decision.tsv	historical label	8 historical labels
evidence_register_rows	35	g7a_historical_evidence_register.tsv	(label, source) pair	labels x the sources that name them
evidence_rows_source_stated	30	g7a_historical_evidence_register.tsv	(label, source) pair	all evidence register rows
anchors_mapped_on_ltra	143	g7a_state_to_residue.tsv	frozen anchor state	150 frozen anchor states
anchor_state_span	107-317	g7a_state_to_residue.tsv	state_id	n/a - a span
anchor_ltra_residue_span	97-363	g7a_state_to_residue.tsv	LtrA residue	n/a - a span
controls_pass	6	g7a_controls.tsv	control	9 declared controls
controls_fail	0	g7a_controls.tsv	control	9 declared controls
controls_inconclusive	1	g7a_controls.tsv	control	9 declared controls
ltra_numbering_checks_agree	12/12 residues, 3/4 Edman sequences	g7a_ltra_numbering_control.tsv	stated residue identity	12 Blocker-stated residues
structural_comparators_independent	0	g7a_structural_comparators.tsv	structure	3 declared structural comparators
missing_primary_assets	1	g7a_acquisition_register.tsv	asset	assets this gate needed

===== END RESOLVED-VALUE SUMMARY =====


===== BEGIN THE BUNDLE'S OWN README, INCLUDING ITS SELF-STATED ADVERSARIAL ANSWERS  (file: results/rt07_g7a_rt0_rt7_bridge/README.md) =====
# rt07_g7a_rt0_rt7_bridge — the historical RT0–RT7 bridge, closed

STATUS: VERIFIED — `run.sh` was run to completion from a cleared scratch directory on
2026-09-18 and reproduced every number below; all 12 `verify.sh` checks pass.

**Terminal. 8 of 8 historical labels carry a terminal evidence status: 4 `ESTABLISHED`,
2 `PARTIAL`, 2 `UNRESOLVED`. No control FAILED. No frozen object was modified.**

Launcher: `launchers/LAUNCHER_03_rt0_rt7_closure.md` · Reruns with
`bash results/rt07_g7a_rt0_rt7_bridge/run.sh`

## Counts, including the ones that look bad

```
n_attempted: 8      historical labels RT0-RT7 carried into the crosswalk
n_succeeded: 6      labels that received a supported or partial correspondence and are DRAWN
n_dropped:   0      nothing was dropped, filtered or excluded
```

**`n_dropped: 0` is exact and load-bearing.** The two labels that did not succeed — RT0 and
RT1 — were **not** dropped: they are carried through every table with a measured
`NO_SUPPORTED_CROSSWALK`, a terminal status, and a written statement of what may still be said
about them. A label that returns nothing is a result here (WA-G.5), and the figure draws those
two rows explicitly rather than interpolating them.

Panel-level counts, a different denominator: `n_attempted: 6` sequences, `n_succeeded: 5`
produced a scientific row, `n_dropped: 1` (`MMLV_5VBS_A`, rejected at 246 aa by the frozen
250 aa eligibility rule — see NC-3 below, which is recorded `INCONCLUSIVE`, not `PASS`).

---

## What this gate measured, in one sentence

**Production `state_id` → LtrA P0A3U0 residue** — the one link the RT0–RT7 crosswalk had never
had — obtained by applying the frozen instrument `rtmap-1.0.0/53a1e738a19b3896`, unmodified, to
LtrA, and then composing it with the literature-derived coordinates that are already landed.

Everything else in this bundle is either tracing (what the sources actually say) or derivation
from that one measurement.

## The bridge

| | |
|---|---|
| anchors MAPPED on LtrA | **143 of 150** (LtrA verdict `MAPPED`, mapped fraction 0.9533) |
| frozen state span | **107–317** |
| **LtrA residue span the anchors reach** | **97–363** |
| `CAT_STATE` 262 | LtrA residue **306**, window `YADD`, `CATALYTIC_CONFIRMED` |

**The residue span is the binding constraint of the whole gate.** The instrument's 150 anchors
begin at LtrA 97. Everything N-terminal to that — which is exactly where the literature places
RT0 and RT1 — **cannot receive frozen-state support however well defined it is historically**.
That is a property of the frozen instrument, and per `LAUNCHER_03` §2 and §3 it is reported,
not repaired.

## The closure decision

| label | terminal status | correspondence | states | LtrA |
|---|---|---|---|---|
| **RT0** | `UNRESOLVED / NOT IDENTIFIABLE` | `NO_SUPPORTED_CROSSWALK` | 0 | — |
| **RT1** | `UNRESOLVED / NOT IDENTIFIABLE` | `NO_SUPPORTED_CROSSWALK` | 0 | — |
| **RT2** | `PARTIAL / INTERPRETIVE` | `PARTIAL` | 17 | 97–123 |
| **RT3** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 22 | 126–166 |
| **RT4** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 42 | 170–230 |
| **RT5** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_MANY_TO_1` | 34 | 311–347 |
| **RT6** | `PARTIAL / INTERPRETIVE` | `SUPPORTED_MANY_TO_1`, downgraded by rule D1 | 34 | 311–347 |
| **RT7** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 6 | 356–361 |

`tables/g7a_closure_decision.tsv` carries, per label, the exact wording downstream work is
permitted to use. **That column is the operative output of this gate.**

## Three findings that were not expected

1. **The inherited statement "RT0 = M1–R85, RT1/7 = R86–R364" misreads its own source.** Blocker
   2005 says the R85 cleavage site is **in RT1**, and that the 10-kDa fragment *contains* RT0.
   Table 1's column is headed "Domain composition" — it names what a fragment holds, not where a
   domain ends. So **there is no source-stated RT0|RT1 boundary anywhere**, and the junction lies
   somewhere in the unstated window LtrA 39–85. Recorded in `control/ASSIGNMENT_RULE.md`
   Amendment 1, made from the PDF before the measurement ran. No landed g2 number is affected —
   g2 used the coordinate only as an external test — but the statement text is corrected.
2. **The strongest historical coordinate in the entire held corpus bounds the *end* of the
   series, not its beginning.** Blocker states a cleavage site "between RT7 and domain X" at
   R364/R365. The frozen anchor span independently ends at LtrA 363, and g2 block 6 ends at 361.
   Three routes — primary text, independent reconstruction, and the frozen instrument — agree
   that the numbered series ends at about 357–365. RT7 is the best-determined label, not RT0.
3. **`5G2X`, not `6AR1`, is the right structural comparator for this bridge.** The registered g7
   plan names `6AR1`; read from the file, `6AR1` is GsI-IIC RT from *Geobacillus
   stearothermophilus* (417 modelled residues, His8-tagged) — a different protein. `5G2X`
   entity 3 is **LtrA itself**, and its author numbering agrees with P0A3U0 at **487 of 487
   modelled residues, zero offset**. Corrected here and carried to `g7b`.

## Controls — every one reported

| control | result | what it showed |
|---|---|---|
| PC-1 catalytic | **PASS** | `CAT_STATE` 262 → LtrA 306, `YADD`, `CATALYTIC_CONFIRMED`, 1 dyad in the sequence |
| PC-3 structural numbering | **PASS** | 5G2X chain C agrees with P0A3U0 at 487/487 modelled residues |
| PC-4 the Zimmerly anchor | **PASS** | the catalytic residue 306 lies inside g2 block 5 — so "the catalytic YxDD lies in subdomain 5" is *measured*, not assumed |
| PC-5 substrate | **PASS** | LtrA verdict `MAPPED`, 143/150, bitscore 378.1, E 3.2e-117 |
| PC-2 anchor span | **MEASURED** | states 107–317 → LtrA 97–363. A limitation, not a pass/fail |
| NC-1 shuffled LtrA | **PASS** | `ABSTAIN`, 0/150, bitscore −2.7 |
| NC-2 reversed LtrA | **PASS** | `ABSTAIN`, 0/150, bitscore −3.8 |
| NC-3 MMLV RT (5VBS) | **INCONCLUSIVE** | never reached the mapper: 246 aa < the frozen 250 aa minimum. **Not counted as a pass** |
| NC-4 anti-circularity | **PASS** (`verify.sh`) | no `g5`/`g6` artefact is an input or is read by any script |
| 12/12 numbering | **PASS** | every residue identity Blocker states agrees with the project's LtrA record |

## The six adversarial questions (BS-14)

**1 · Where is each headline claim overstated — name the word.**
The word is **"correspondence"**. Four labels are reported as `ESTABLISHED OPERATIONAL
CORRESPONDENCE`, and a reader will hear "RT3 *is* states 136–177". It is not. What was measured
is that frozen anchor states fall inside a LtrA interval that the historical evidence places
that label in. The second word is **"supported"**: `SUPPORTED_1_TO_1` means *no competing
assignment survived the declared rule*, not that the assignment was independently confirmed.
The third is **"established"** itself — everything here was measured **on one protein**, LtrA.
Nothing in this bundle demonstrates that any correspondence transfers to another family, and
`tables/g7a_closure_decision.tsv` says so in every row.

**2 · What specific alternative explanation produces this exact number?**
That the ordinal propagation in rule A3 is simply **wrong by one block**. There are six
reconstructed blocks and seven numbered labels, so some pair must collapse; A3 anchors the frame
at RT5 via the catalytic motif and propagates outward, and Route C selects RT5+RT6 as the
collapsing pair. If instead RT6 owned block 6 and RT7 had no block, every label from RT6 upward
would shift and RT7's `ESTABLISHED` status would vanish. What argues against that is Blocker's
independent statement that the series ends at R364/R365, which block 6 (356–361) sits directly
against and block 5 (304–347) does not. That is one external constraint, not a proof, and it is
why RT6 is **downgraded** rather than reported as established.
A second alternative, for the two `NO_SUPPORTED_CROSSWALK` rows: they may reflect only that the
GII-derived profile has no anchors in its own N-terminal region, and nothing whatever about RT0
or RT1. **That reading is fully consistent with the data and is stated in the closure table** —
which is why those rows are `UNRESOLVED / NOT IDENTIFIABLE` rather than any claim of absence.

**3 · Could this test have returned a negative?**
Yes, and two of the eight rows *are* negatives. Four separate kills were declared in advance and
each could have fired: LtrA could have abstained (PC-5), `CAT_STATE` 262 could have missed the
catalytic dyad (PC-1), the decoys could have mapped (NC-1/NC-2), and the catalytic residue could
have fallen outside g2 block 5 (PC-4) — which would have destroyed the single anchor the whole
assignment rests on. The gate was also designed to survive returning **eight** unresolved rows.

**4 · The unit of every rate.**
`mapped_fraction` 0.9533 = MAPPED anchor states ÷ **150 frozen anchor states**, per sequence.
`n_supporting_states` = MAPPED anchor states whose LtrA residue lies inside that label's
reference interval; denominator **150**, and the intervals are **not** disjoint — RT5 and RT6
share all 34 of theirs, so the per-label counts must never be summed. The numbering control is
**12 of 12** stated residue identities and **3 of 4** published Edman sequences. `487/487` is
modelled residues of **5G2X chain C**, not of LtrA's 599. Every table carries `unit` and
`denominator` columns.

**5 · Which numbers have no producing script?**
The **quoted text** of the four Blocker passages and the Zimmerly `Z11` statement. They were read
by a directed `pdftotext -layout` extraction, and the register records the page context, but a
quote is not a computed number and no script asserts that the PDF says it. `run.sh` re-extracts
the text so the quotes can be re-checked, and the g1-verified assignment ids (`B02`, `Z08`,
`Z11`) are the independent second record. Everything else in `tables/` is produced by a named
script in `MANIFEST.tsv`.

**6 · What was withdrawn or weakened?**
- The **A1 clause of the declared rule was withdrawn and rewritten** before the measurement ran.
  Its original reading ("RT0 = M1–R85; RT1/7 = R86–R364") was traced to the PDF, found to
  misread fragment nomenclature as a domain boundary, and replaced by Amendment 1. The
  correction makes RT1 *worse* determined, not better.
- **NC-3 was downgraded from PASS to INCONCLUSIVE** after inspection: the sequence was rejected
  at 246 aa by the frozen eligibility rule and never reached the mapper, so it is not evidence
  that the mapper abstains on out-of-population proteins.
- **RT6 was downgraded** from `ESTABLISHED` to `PARTIAL` by declared rule D1, because its
  individual position rests only on comparator evidence.
- The prior proposal table's `1:1 candidate` for RT2 was **not** reproduced: RT2 measures
  `PARTIAL`. See `tables/g7a_prior_proposal_comparison.tsv`.
- **Attempted and did not survive:** acquisition of Malik, Burke & Eickbush 1999, the defining
  source for RT0. Two routes failed and the abstract does not mention domain 0, domain Z or any
  numbered RT domain. The absence is landed as `MISSING_PRIMARY_ASSET`, and it is the reason
  RT0's status is terminal rather than open.

## What this gate did NOT do

No HMM or mapper development. No revalidation of the frozen mapper — Stage-2 validation stays
CLOSED at Endpoint A. No motif discovery, no phylogeny, no retron reclassification, no `g6`
family architecture, no RT–ncRNA work, no fingers/palm/thumb segmentation. No `g5` or `g6`
output was read, for any purpose.
`results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv` is **unchanged and still
`UNRESOLVED` in every row**, and `crosswalk.assert_unresolved_until_g7()` still passes —
production emits no historical label, which remains true after this gate.

The remaining comparator campaign — Toro 2014, Mestre 2020, myRT, Toro 2026, DSSP
fingers/palm/thumb, `foldseek`, the non-LTR R2 structure — is **`g7b`** and is untouched.

## Claims

`C3` `primary`, `C9` `supporting`, `C7` `supporting`. **No claim is promoted by this bundle.**
Status lives only in `idea-stage/docs/research_contract.md`, where all three remain `UNPROVEN`.

===== END THE BUNDLE'S OWN README, INCLUDING ITS SELF-STATED ADVERSARIAL ANSWERS =====


---

# FINAL INSTRUCTION

Review adversarially. The project's own README already argues against itself in places; do not
simply agree with its self-criticism either — verify it. Where the project claims a primary
source says something, treat the quote as a transcription you cannot independently open, and
say so in section C rather than assuming it is faithful.

Return ONLY sections A through F.
