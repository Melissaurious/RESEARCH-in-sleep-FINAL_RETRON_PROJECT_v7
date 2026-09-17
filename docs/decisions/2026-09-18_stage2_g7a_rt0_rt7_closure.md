# DECISION — historical RT0–RT7 is CLOSED at `g7a`; the crosswalk of record is the g7a table

Date: 2026-09-18 · Track: `rt07` · Status: **binding for every downstream `rt07` gate,
the thesis and any paper**

Producing bundle: **`results/rt07_g7a_rt0_rt7_bridge/`** ·
Launcher: `launchers/LAUNCHER_03_rt0_rt7_closure.md` ·
Split recorded in `docs/decisions/2026-09-18_stage2_g7_split_amendment.md`

---

## A · The historical RT0–RT7 track is terminal

All eight labels now carry a terminal evidence status. **`UNRESOLVED` is a result here, not an
open task**, and no further method will be tried to convert one (`LAUNCHER_03` §1 stopping
condition).

| label | terminal status | correspondence | frozen states | LtrA residues |
|---|---|---|---|---|
| RT0 | `UNRESOLVED / NOT IDENTIFIABLE` | `NO_SUPPORTED_CROSSWALK` | — | — |
| RT1 | `UNRESOLVED / NOT IDENTIFIABLE` | `NO_SUPPORTED_CROSSWALK` | — | — |
| RT2 | `PARTIAL / INTERPRETIVE CORRESPONDENCE` | `PARTIAL` | 107–133 | 97–123 |
| RT3 | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 136–177 | 126–166 |
| RT4 | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 181–241 | 170–230 |
| RT5 | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_MANY_TO_1` | 267–301 | 311–347 |
| RT6 | `PARTIAL / INTERPRETIVE CORRESPONDENCE` | `SUPPORTED_MANY_TO_1` (downgraded, rule D1) | 267–301 | 311–347 |
| RT7 | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 310–315 | 356–361 |

**4 established · 2 partial · 2 unresolved.**

The summary statement the track lands on:

> RT2–RT7 carry varying degrees of defensible historical correspondence to the frozen
> conserved-state system **on LtrA**, while **RT0 and RT1 cannot be given an operational
> boundary from the available evidence at all** — the frozen instrument's 150 anchors do not
> reach the region of the protein where the literature places them.

## B · The crosswalk of record

**`results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv` is the interpretation
layer of record for historical RT0–RT7.** `tables/g7a_closure_decision.tsv` carries, per label,
the exact wording downstream work may use, and that column is binding.

**`results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv` is NOT edited and stays
`UNRESOLVED` in every row.** This is deliberate and is not an oversight:

* the frozen bundle is a **production instrument**, and production still emits no historical
  label — which is exactly what that table asserts;
* `crosswalk.assert_unresolved_until_g7()` therefore continues to pass, and remains a live guard
  against a plausible-looking label being typed into the frozen table;
* the interpretation layer lives in the gate that measured it, where its evidence, controls and
  uncertainty travel with it.

Any code wanting a historical label reads the **g7a** table explicitly, joined on `state_id`.

## C · Two corrections this gate establishes

### C.1 · "RT0 = M1–R85, RT1/7 = R86–R364" misreads its own source — **withdrawn**

`results/rt07_g2_reference_reconstruction/control/historical_statements.tsv` statement `H09`
attributes that span to Blocker 2005 assignment `B02`. Traced to the PDF, the source says:

> "…two major cleavage sites, **one in RT1** and the other **between RT7 and domain X**.
> Cleavage at the first major site **in RT1** yielded a 10-kDa N-terminal fragment
> **containing RT0** (M1–R85)…"

and, in discussion, "the Arg-C cleavage site **in RT1** (R85)". Table 1's column is headed
**"Domain composition"** — what a fragment *contains*, not where a domain ends.

**Therefore R85/R86 is not the RT0|RT1 boundary; it is a cleavage site inside RT1.** RT0 is
bounded *above* by 85 and contains the conserved alanine A39; the RT0|RT1 junction lies somewhere
in **LtrA 39–85** and is stated **nowhere** in the held corpus.

**No landed g2 number changes** — g2 used the coordinate only as an external `EXTERNAL_COORDINATE_TEST`
and never to define anything. What is withdrawn is the **statement text**, and `g1` item `U06`
("is Blocker's RT0 boundary transferable beyond LtrA?") is closed by correction: the premise was
wrong, so the question does not arise.

### C.2 · `5G2X`, not `6AR1`, is LtrA

`results/rt07_g4b_production_mapper/docs/G7_STRUCTURE_PLAN.md` calls `6AR1` *"the group II intron
RT structure and … the natural first crosswalk target"*. Read from the deposited files:

* **`6AR1`** entity 1 is `GsI-IIC RT`, *Geobacillus stearothermophilus*, 417 modelled residues,
  His8-tagged — a **different protein**;
* **`5G2X`** entity 3 is `GROUP II INTRON-ENCODED PROTEIN LTRA`, chain C, and its author
  numbering agrees with the project's LtrA record at **487 of 487 modelled residues, zero
  offset**, with Blocker's A39, R85 and R86 all present in the structure.

For work denominated in LtrA numbering, **`5G2X` is the primary structural comparator**. Carried
to `g7b`.

## D · What downstream work may and may not say

**May**, where the crosswalk supports it — this is the wording `LAUNCHER_03` was written to make
possible:

> "the `g6` signal localises to frozen states X–Y; these states overlap a
> **literature-supported portion of** historical RTn"

for **RT3, RT4, RT7** (individually), and for **RT5+RT6 jointly**. For **RT2** the same sentence
is available but the phrase *"a portion of"* is load-bearing and may not be dropped.

**May not**, ever:

1. **No RT0 or RT1 operational statement of any kind** — no occupancy, fraction, count, boundary
   or interval. Both are `UNRESOLVED / NOT IDENTIFIABLE`. RT0 additionally carries g3's
   `OBJECT_MISMATCH`, which is unchanged.
2. **No statement attributing a state to RT6 rather than RT5.** The two are not separable; the
   region is named **RT5+RT6** or not at all.
3. **No description of RT0–RT7 as a partition** of the RT domain. Six reconstructed blocks, seven
   labels, two of them unresolved.
4. **No transfer beyond LtrA.** Every correspondence here was measured on one protein. Applying a
   historical label to a retron, DGR or UG-family RT is a **new measurement** that has not been
   made.
5. **No reading of a low-occupancy or `DELETED_STATE` region as a missing historical region.**
   `DELETED_STATE` is an alignment-path state.
6. **No production column may carry a historical label.** Unchanged.

## E · Why RT0 and RT1 are terminal rather than open

Two independent reasons, and both are measurements:

1. **Evidence.** RT0's defining source — Malik, Burke & Eickbush 1999, where domain Z was renamed
   domain 0 — is a **`MISSING_PRIMARY_ASSET`**. Retrieval was attempted 2026-09-18 by two routes
   and failed; the accessible abstract does not mention domain 0, domain Z or numbered RT
   domains. Every held source that states RT0's scope **cites** it rather than deriving it. After
   the C.1 correction, RT0 has **no stated boundary anywhere in this project's evidence** — only
   an upper bound and an interior landmark.
2. **Instrument.** The frozen mapper's 150 anchors reach **LtrA 97–363**. The regions the
   literature assigns to RT0 (≤85) and RT1 (39–61) lie **entirely outside** that span, so zero
   frozen states can support them. Closing this would require rebuilding the instrument, which
   `LAUNCHER_03` §3 forbids and §2 makes a scope kill.

The second reason is a statement about **the instrument, not the biology**, and the closure table
says so. Neither reason is repairable inside the scope this project has set, which is what makes
the status terminal.

## F · Scope this decision does not touch

Stage-2 mapper validation stays **CLOSED at Endpoint A**. The instrument, profile, anchor set,
`CAT_STATE`, thresholds and all `g5` calls are unchanged and were executed, never modified.
`g6` is unaffected and unblocked: it operates in frozen `state_id` space and does not require
RT0–RT7 to be valid. `g7b` is untouched.

Two items remain **deferred to the operator** and are **not** settled here (`LAUNCHER_02` §9b):
whether the operational method becomes its own methods paper, and how any RT1 result is
interpreted relative to the 1990 caveat (`g1` item `U08`). `g7a` **measured** RT1 and did not
interpret it.

Supersede this record by a new record, never by rewriting it.
