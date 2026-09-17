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
