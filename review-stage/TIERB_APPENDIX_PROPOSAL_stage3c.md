# Proposed disposition — descriptive Tier-B retron appendix to Stage 3C

Date: 2026-09-19 · **PROPOSAL ONLY — NOT EXECUTED.** No Tier-B row has been placed, joined or
counted against the Stage-3A partition. This document states what such an appendix would contain,
what it could and could not say, and the author's recommendation.

Authorities: the operator's instruction (Tier B may be a *clearly separate, descriptive,
lower-confidence* appendix that cannot change the primary verdict, cannot be pooled with Tier A and
cannot re-tune any threshold); the independent review's ruling (§6 of
`review-stage/INDEPENDENT_REVIEW_RESULT_stage3c.md`); `LAUNCHER_03B` closure; synthesis audit C-6.

---

## 1 · What the Tier-B evidence actually is

Examined, not analysed: 17 Tier-B rows in the frozen `TRUTH_TABLE.tsv`, in three distinct grades.

| grade | n | rows | what the label rests on | admissible? |
|---|---|---|---|---|
| **own-chain, explicit residue, catalytic metal** | **5** | `7XJG_A` D198 (METAL_CAT 2.57 Å), `8QBL_A` D198 (3.00 Å), `9I2G_B` D202 (2.40 Å), `9C0I_A` D140 (2.09 Å), `9LJE_A` D140 (2.13 Å) | metal coordination in that chain's own coordinates — independent of the Stage-3B detector, of Stage 3A, and of any motif call | **yes**, as a location description |
| author/mutational, motif-named, no per-chain residue field | 6 | the six Retron-Eco8 chains; `truth_source = NONE`, label given as "D107; Y198; D200; D201 (YADD motif Y198-D201)" | literature author assignment plus mutational evidence, but named through the YADD **motif** and carrying no frozen per-chain residue field | **no** — the review rules that `FUNCTIONAL_PAIR` rows with `truth_source = NONE` must not be promoted into truth labels; the author concurs |
| transferred within replicate group | 6 | `7V9U_A`, `7V9X_A`, `8QBK_A`, `8QBM_A`, `9I2F_A`, `9S1F_B` | a partner chain's label, with a blank per-chain residue field | **no** — may be counted, not reconstructed. `9S1F_B` is additionally disqualified: its only cluster is the **TOPRIM nuclease** site, which the frozen table itself records as "contributes no polymerase structural truth" |

## 2 · The proposed appendix, in full

**Population.** The **5** own-chain, metal-evidenced Tier-B chains above — of which **3 are retron**
(`7XJG_A` and `8QBL_A`, both Ec86, biological group RG03; `9I2G_B`, Ec67, RG24) and 2 are UG2/DRT2
(`9C0I_A`, `9LJE_A`, RG08), reported separately and never merged into the retron count.

**Measurement.** For each chain, the single frozen labelled aspartate is located in the frozen
Stage-3A PDP partition: which unit contains it, that unit's palm-like/thumb-like/fingers-like call
status, its discontinuity, and the size-expected baseline. Both partition arms (primary and BJ-p4).
Nothing else.

**Forbidden in the appendix**, explicitly: running or scoring the Stage-3B detector; any HIT/MISS;
any hit rate, abstention rate or decoy count; any pooling with the 19 Tier-A chains; any threshold
change; any claim that a single labelled residue constitutes a catalytic *pair*; any statement that
this is held-out or blind validation.

**Required header wording** (adopted from the review verbatim):

> Exploratory Tier-B retron label-location appendix. This appendix places only frozen, per-chain
> Stage-3B Tier-B residue labels onto the frozen Stage-3A PDP partition. It does not run or score
> the Stage-3B detector, does not report HIT/MISS, is not held-out or blind validation, is not
> pooled with Tier A, changes no threshold or verdict, and makes no claim that a single labelled
> residue constitutes a catalytic pair. Tier B was inspected during detector design, and the
> detector's Tier-B PASS branch was unreachable; neither issue is cured by this descriptive
> placement.

**Why C-6 and the unreachable-PASS defect do not invalidate it.** Both are defects of Tier B *as a
held-out test set for the detector*. The appendix makes no detector-performance claim and no
blindness claim, so neither defect is load-bearing. The metal-coordination labels are structural
observations in each chain's own coordinates and were not produced by the detector.

## 3 · The honest objection to running it at all

**Three retron chains from two biological groups, two of them the same protein.** That is the entire
retron yield. It cannot support any statement about retron catalytic architecture in general; at
best it answers "in these three retron chains, does the frozen catalytic label fall in the same
structural unit as it does in the non-retron Tier-A chains?" — a consistency check on five data
points, not a result.

The appendix would also sit downstream of the same selection the synthesis audit flags (C-5): these
retron structures are in the register **because** they carry catalytic evidence.

## 4 · Recommendation

**Run it, but only after the Stage-3C blockers are repaired (R1–R5), and only under the wording
above** — with the yield stated in the first sentence, so no reader can mistake five chains for a
retron result. Its value is precisely that it closes an obvious question ("what about the retrons?")
with a number instead of a silence, and it removes the temptation to read Comparison A as if it had
said something about retrons.

**Do not run it if** the operator would rather Stage 3C say plainly "retron catalytic architecture
was out of scope and remains untested". That is an equally defensible position, and the appendix
adds no evidentiary weight — only an explicit, bounded null.

**Either way, the primary Stage-3C verdict is unchanged**, and Comparison A's population stays the
19 Tier-A own-chain-truth chains.

## 5 · Decision required

| option | consequence |
|---|---|
| **A (recommended)** | build the appendix as specified, after R1–R5, labelled exploratory/lower-confidence, 5 chains (3 retron / 2 non-retron), never pooled |
| **B** | do not build it; record in the report that retron catalytic architecture is untested in Stage 3C and name the 3B scope as the reason |
| **C** | build it with a wider population (Eco8 author/mutational rows and/or transferred rows) — **not recommended and not supported by the review**; it would require a fresh provenance ruling on motif-named labels |
