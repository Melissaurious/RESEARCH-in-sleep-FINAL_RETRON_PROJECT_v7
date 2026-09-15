# DECISION — Stage-2 (`rt07`) operator decisions: four resolved, two deferred

Date: 2026-09-15 · Track: `rt07` · Status: **binding for `launchers/LAUNCHER_02_rt0_rt7_definition.md`**

**Decided by:** operator (Melissa Rios), 2026-09-15, at the Stage-2 planning checkpoint held
before `rt07_g1_history_and_definition` was started. No gate had run and no Stage-2 number
existed when these decisions were taken.

## What this record supersedes

`docs/decisions/2026-09-15_stage2_prior_dossier_audit.md` carried six items in its §G
("Unresolved, and who decides") and classified the non-LTR R2-type RT structure
`MOVE_TO_LATER_STAGE` in its §D. **That record is historical and is not rewritten.** Its
classifications of prior-dossier content remain binding; what changes here is only the
*decision status* of the items below.

| prior-dossier audit item | previous status | status after this record |
|---|---|---|
| §G.1 · acquire `ALIGN_000044`? | unresolved — operator authorises the fetch | **resolved — §A below** |
| §G.2 · inclusion rule for non-bacterial RT structures | unresolved — rule to be written before any are added | **resolved — §B below; the rule is written here and in launcher §9a** |
| §D · non-LTR R2-type RT structure, `MOVE_TO_LATER_STAGE`, "the launcher plans it and does not fetch it" | acquisition deferred to a later stage | **superseded — §B below.** Acquisition is permitted in `rt07` under the predeclared inclusion rule. The scientific classification behind it is unchanged: the structure is a comparator, and full structural segmentation remains Stage 04 |
| §G.5 · does Stage 04 come first or merge? | unresolved | **resolved — §C below: Stage 04 stays separate** |
| §G.6 · digitise Xiong & Eickbush Fig. 1? | unresolved — the effort is an operator call | **resolved — §D below: permitted as corroboration/fallback only** |
| §G.3 · is the operational definition its own methods paper? | unresolved | **still deferred — see "Deliberately deferred"** |
| §G.4 · how is RT1's concordance failure reported? | unresolved | **still deferred — see "Deliberately deferred"** |

Nothing here promotes a prior number to an acceptance criterion, changes a claim, changes the
scientific question, or alters the anti-circularity design. The evidence hierarchy of launcher
§5d is unchanged: comparators still may not seed the reconstructed frame.

## A · `ALIGN_000044` — approved for governed acquisition during `rt07_g1`

Zimmerly, Hausner & Wu 2001's own submitted alignment (EMBL accession `ALIGN_000044`) is
**approved for acquisition during `rt07_g1_history_and_definition`**, from an authoritative
archival source only.

Conditions, all of which hold before the asset is used as evidence:

- record **accession, source URL or archive, retrieval date, licence/access status, byte count
  and SHA256** in the `g1` acquisition and source-resolution register (launcher §7c);
- write the bytes to the governed acquisition cache `data/derived/rt07_external_assets/`
  (launcher §9c), never into the frozen `references/rt0_rt7/` package;
- if the accession is **unavailable, inaccessible or resolves ambiguously**, land
  `MISSING_PRIMARY_ASSET` in that register and continue **without inventing a substitute**;
- until acquired, registered and validated the asset is graded `DO-NOT-USE` (launcher §4).
  That grade is the evidence gate, not a revocation of this approval.

**Why:** it is the primary-source alignment behind the only Tier-1 paper that numbers RT
subdomains. Without it the sole subdomain-numbering source reaches this project as printed
figures and prose only, which is also the condition that makes §D's figure digitisation
necessary rather than optional. Registered status stays `MISSING_NOT_ACQUIRED` in
`references/rt0_rt7/RESOURCE_REGISTER.tsv` until a `g1` acquisition row says otherwise.

## B · External / non-bacterial RT structures — predeclared inclusion rule

A non-retron or non-bacterial RT structure may be acquired **only** when it satisfies at least
one of:

1. it represents a **historically relevant reference class** required to test a reconstructed
   concept; or
2. it provides an **independent structural comparator** for a sequence-defined block.

Binding limits on what such a structure may do:

- it may **constrain or falsify** a sequence-defined boundary;
- it may **not define, seed or adjudicate the RT1–RT7 sequence partition**. The published
  RT0–RT7 conventions were never derived from structure, so structure cannot arbitrate between
  two conventions that both descend from sequence (prior-dossier audit §D, `KEEP_AS_DESIGN`);
- for the **RT0** question specifically, **group-II-intron and non-LTR RT structures are
  admissible historical comparison classes**, because the load-bearing prior reading (`D9`)
  defines subdomain 0 as conserved between exactly those two classes;
- acquisition follows the same governed route as §A: cache in
  `data/derived/rt07_external_assets/`, register row in `g1`, `DO-NOT-USE` until acquired,
  registered and validated;
- **broadening this rule** beyond the two criteria above remains a stop-and-wait operator
  decision (launcher §9b), as does any asset whose licence/access conditions are unclear, whose
  identity cannot be established unambiguously, or whose retrieval needs credentials the
  operator does not already hold.

This supersedes the prior-dossier audit's §D deferral of the non-LTR R2-type structure to a
later stage. It does **not** move any Stage 04 work into `rt07` — see §C.

## C · Stage 04 remains separate

**Stage 04 is not merged into Stage 2 and is not a prerequisite for it.** Stage 2 reconstructs
and operationalizes the historical **sequence** framework first; Stage 04 later supplies an
independent **structural** representation against which that framework may be tested.

**Why:** anchoring RT0–RT7 landmarks on fingers/palm/thumb geometry — the alternative the prior
dossier argued for — would import a structural partition into a sequence reconstruction whose
whole value is that it was built without one, and would dissolve the independence that makes
the later comparison informative. The two representations stay distinct and neither defines the
other (launcher §3, §5d). Full fingers/palm/thumb segmentation, ESMFold work and the structural
rescue pilot remain Stage 04 (prior-dossier audit §D, `MOVE_TO_LATER_STAGE`, unchanged).

## D · Xiong & Eickbush 1990 Fig. 1 — digitisation permitted as corroboration/fallback

When reconstructing a historical block or landmark, evidence is used in this order:

1. the **original digital or accessioned alignment**, if recoverable (this is why §A is
   resolved first, and ideally before `rt07_g2`);
2. **explicit textual criteria** in the primary paper;
3. **digitisation of the published alignment figure**, as corroboration or fallback.

Digitisation of Fig. 1 is permitted in `g1`/`g2` **only after routes 1 and 2 have been checked
and the check recorded**. Any coordinate inferred from a figure carries an **explicit extraction
uncertainty**, and a pixel-derived edge is **never reported as an exact residue boundary**
without independent support.

**Why:** the figure legend's "See text for a description of the criteria used in this
assignment", together with its 42 reported conserved positions, means the familiar story that
the 1990 boundaries were drawn by eye with no published criterion may be false. Digitisation
converts that provenance question from assertion into measurement — but a measurement whose
instrument is a scanned figure, and the uncertainty travels with every number it produces.

## Deliberately deferred — not decided here, and not to be decided by a gate

Both remain stop-and-wait operator decisions in launcher §9b. No gate, report or session may
settle either by default, and neither blocks `rt07_g1`.

1. **Whether the operational method becomes a separate methods paper.** A publication-strategy
   call that depends on what `g4` actually lands.
2. **How any future RT1 concordance failure is interpreted** — as a limitation of this method,
   or as an independent recovery of a weakness the founding authors flagged in 1990. The prior
   dossier is explicit that a 2026 concordance measurement and a 1990 evidence caveat are
   **different objects that must not be conflated**; deciding this before `g3` re-measures
   would be deciding it before the object exists. `g3` reports the measurement with its frame,
   stratum and n; the framing call comes after, from the operator.

## Consequences already encoded

- `launchers/LAUNCHER_02_rt0_rt7_definition.md` §4 (two `DO-NOT-USE` rows and the grade
  clarification), §7 `g1` stop condition, §7c (acquisition and source-resolution register),
  §9a (both acquisition bullets, figure-digitisation bullet), §9b (both deferred items,
  broadening as the guarded action), §9c (governed acquisition cache).
- `references/rt0_rt7/RESOURCE_REGISTER.tsv` — the `ALIGN_000044` note points at this record;
  its `provenance_status` stays `MISSING_NOT_ACQUIRED` until a `g1` acquisition row exists.

Supersede this record by a new record, never by rewriting it.
