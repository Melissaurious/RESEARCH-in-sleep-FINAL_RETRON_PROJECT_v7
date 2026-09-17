# DECISION — Stage 2 conflates two scientific objects; separating them, and what that costs

Date: 2026-09-16 · Track: `rt07` · Status: **proposed; pending independent review and operator acceptance**

**Supersedes** the *scope* statements of
`docs/decisions/2026-09-16_stage2_g4_identifiability_redesign.md` and of
`docs/decisions/2026-09-16_stage2_g4_review_round2_and_repairs.md` listed in §6. Neither is
rewritten. Both stay on disk with their hashes recorded in `review-stage/`.

Supersede this record by a new record, never by rewriting it.

Design artifacts: `results/rt07_pre_g4_scope_separation/`.

**NO g4 DETECTOR EXECUTED; NO g5 CATALOGUE APPLICATION STARTED.**

---

## 1 · The finding

Stage 2 has been asking one gate to be two instruments.

    HISTORICAL_RECONSTRUCTION_SUBSTRATE   ALIGN_000044 — 66 records, 65 unique, ONE RT class
    GENERAL_RT_OPERATIONAL_REFERENCE_SET  does not exist in this project

`g4` failed two independent design reviews (3/10, then 4/10). Both verdicts are correct, and this
record identifies why they were inevitable: **`g4` was specified to build a general RT instrument
from a single-class historical artefact.** No amount of estimand discipline repairs that, because
the defect is in the substrate, not in the statistics.

## 2 · What the g2 substrate is, measured

All 66 sequences are **group II intron-encoded ORFs** — `nad1 intron 4`, `cox1 intron 1`,
`psbC intron 4`, `LSU rRNA intron 1`, `ltrB intron`, and so on. The four "lineage groups" are
**host compartments** (mitochondrial 29, bacterial 20, algal/chloroplast 11, euglenoid 6), not RT
classes; all 20 `bacterial` members are bacterial group II introns, LtrA among them.

Of 42 Stage-1 family labels, exactly one — `RVT-GII` — is represented, and by lineage rather than
by an attached label. Retrons, DGRs, Abi, CRISPR-associated RTs and all 28 UG families are absent.

**New finding, in no landed table:** `O.s.petDI1` and `S.o.petDI1` are **byte-identical over 610
aa** under two names and accessions. The substrate is **66 records / 65 unique**; the
`algal_chloroplast` group is 11 records / 10 unique. Since the g2 criterion counts *elements of a
group*, the duplicate contributes twice to that group's denominator. This does not invalidate g2
— one element in the second-smallest group — but any re-derivation must flag it.

**g2's substrate choice was correct.** `ALIGN_000044` is the alignment Zimmerly, Hausner & Wu
submitted with their **group II intron ORF phylogeny** (NAR 29:1238–1250), and it is where the
inherited RT0–RT7 labels were *adjusted*. Reconstructing that alignment's conserved structure on
that alignment is the experiment, not a sampling error.

## 3 · Preserved from g1–g3 — not retracted

Changing the next instrument does not retract the historical arm. Terminology provenance;
landmarks substantially recovering (2 `RECOVERED`, 5 `PARTIALLY_RECOVERED` of 9 testable);
ordering surviving (27 of 28 prior placements inside a reconstructed region); RT5 and RT6 inside
one region; exact boundaries not externally established; RT0's distinct historical status; RT1
unresolved.

And the distinction that must not be lost:

> **"Six blocks is not established as a biological constant" is a statement about the partition
> count.** It is not a statement about the conserved positions, which are strongly non-random —
> 81 strict columns against a residue-shuffle null whose mean, min and max are all 0 over 200
> replicates, p = 0.0050 — nor about their localization, which reproduces across independent
> alignment frames. The count is a free parameter; the positions are a measurement.

## 4 · myRT, measured and reconciled

Three distinct objects, not interchangeable:

| object | N | kind |
|---|---|---|
| family seed FASTAs, 45 canonical | 1,988 records / **1,986 unique** | RT-domain **fragments**, median 201 aa |
| `RTs-collection.faa` | **2,339**, all unique | **full-length**, median 365–663 aa |
| `RVT-ref.fst` | 1,844 | fragments; **1,828 are already family seeds** |

Counts: **45 models** in `RVT-All.hmm`, summed `NSEQ` **1,988**, and **every family's `NSEQ`
equals its FASTA record count exactly**. The 47 `.hmm` files are 45 + `RVT-All.hmm` +
`RVT-CRISPR-like`; the 47 `.fst` are 45 + `RVT-CRISPR-like` (10) + `RVT-test` (21); `List` holds
43. **The operator's expected ~2,051 seeds / ~47 families is not reproduced by any object
measured**; the launcher's own correction (45 models, 1,988 sequences) is confirmed exactly.

Two package discrepancies that touch Stage 1: `RVT-CRISPR-like` has an HMM and FASTA but is
**absent from `RVT-All.hmm`**, while Stage-1 carries it as a family with 3,168 exact RTs; and the
seeds and the collection use **different family vocabularies**.

### The decisive provenance fact

`buildRVT.sh` documents the build verbatim: hmmscan `RTs-collection.faa` against `cdd-PfamA`,
take the `RVT_1` hits, **`cut -c $start-$stop`**, filter, Muscle-align. Every seed is a Pfam
`RVT_1` excision, so **myRT's implicit coordinate system is Pfam RVT_1's match states**.

Measured on LtrA, from the seed header `L.l.I1|ML|IIA1|Lactococcus_90_360_GII-II`:

    myRT RVT_1 window          LtrA  90 – 360
    Blocker RT0 zone           LtrA   1 –  85     ENTIRELY OUTSIDE
    g2 region 1                LtrA  39 –  61     ENTIRELY OUTSIDE
    g2 regions 3-6             LtrA 126 – 361     fully inside, dyad at 306 included

**Binding: no myRT-derived substrate can address RT0, ever.** The region was excised before the
seeds existed.

An unforced convergence, reported as observation not validation: Pfam `RVT_1` (90–360), Blocker's
RT1–RT7 span (86–364) and the prior project frame (53–361) place the core in nearly the same
place, and **all three exclude the RT0 landmark at LtrA 39**.

### Role assignment for myRT

**Valid** as broad diversity and derivation material — containment in `all167` is **17 of 1,988**
(0.86%), in `GOLD171` **13** (all `RVT-Retrons`), in `ALIGN_000044` **11** (all GII) — and its
45-family partition has **zero cross-family duplicate sequences**.

**Invalid** as independent validation of family assignment, because Stage-1's labels are this same
system's output. **Incapable** of addressing RT0.

Rejecting myRT for lack of independence would be the wrong call; using it to validate family
labels would be circular. It is derivation material with family labels as strata.

## 5 · Structures, measured

**39 distinct RT-bearing PDB entries** locally (40 with the HIV-1 outgroup): Retron 12, `RVT-GII`
7, G2L/G2L4 4, UG 9, Abi 3, DGR 2, CRISPR-associated 1, viral 2.

**Zero non-LTR/R2-type. Zero telomerase.** RT0's defining claim is cross-class between group II
intron and non-LTR RTs, so **the comparison class required to test it has no local structural
representative** — an independent confirmation that `E09` is `UNESTABLISHED`.

**21 of 38 RVT families have no structural anchor at all**, the largest being `RVT-UG5` (6,439),
`RVT-UG4` (4,705) and `RVT-UG17` (4,702).

Two cautions carried forward: the prior sequence-to-structure cross-validation
(`d2j_boundary_crossval.tsv`) covers only **11 of 25** structures and agreement is **poor at the
thumb** (Jaccard 0.0 for five, including 5G2X) and moderate at the fingers (0.48–0.86); and **no
expression-tag column exists in any table** — every tag recorded in
`tables/structure_reference_inventory.tsv` except 26CZ's SUMO was measured by regex in this
session, so `U11` is still open and is larger than g3's count over `anchors72` alone.

## 6 · What is superseded

| statement | where | replacement |
|---|---|---|
| "every Stage-1 family is out-of-family by construction" | redesign §4; already withdrawn in the round-2 repairs record | `RVT-GII` is the in-family class; the deeper point is that a **single-class panel cannot hold out a class at all**, so class transfer was untestable in principle |
| g4 derives from `ALIGN_000044` alone | redesign §3, §5 | `ALIGN_000044` seeds **2A only**; 2B needs a broad panel and a §5d tier amendment |
| "the derivation substrate contains zero retrons, therefore poor retron transfer is the likely outcome" | round-2 repairs record §4 | still true of `ALIGN_000044`, but no longer the design: 2B's panel contains 91 retron seeds and 96 full-length retrons, and retron transfer becomes a **measurement with a held-out denominator** |
| g4 is one gate | launcher §7 | `g4a` reference design, then `g4b` coordinate mapper |
| the crosswalk is a separate stage (2C) | operator's proposed decomposition | historical crosswalk lands **inside 2B** over frozen output; structural/published crosswalk stays as the existing `g7` |

Unchanged and still binding: `BOUNDARY_ACCURACY` and `BOUNDARY_CALIBRATION` `UNESTABLISHED`; no
RT0 occupancy; no forced seven regions; no threshold tuning to rescue RT1; the §7a call-state
vocabulary; the bounded-sampling discipline.

## 7 · The fork, which is the operator's

**Launcher §5d places myRT, Toro 2014, Mestre and Toro 2026 in the published-comparator tier:
*"compared against only; must never seed the reconstructed frame."*** That rule is right for 2A
and it makes 2B impossible — if no comparator may seed, the only derivation material is the
66-sequence single-class substrate that already failed twice.

Three exits, none of them this session's:

1. **Amend §5d** to distinguish *seeds 2A* from *seeds 2B*, with the §5f conditions in
   `proposed/LAUNCHER_02_diff.md`. Stage 2B becomes buildable on ~2,339 full-length
   family-labelled proteins across 38 labels. **Recommended default.**
2. **Keep §5d** and accept that Stage 2 ends at 2A — a historical reconstruction plus a
   documented impossibility result, which the launcher's whole-track kill criterion already
   contemplates. Honest, and much smaller.
3. **Build a new reference panel from Stage-1 itself**, independent of myRT. But Stage-1's family
   labels *are* myRT's output, so this buys less independence than it appears to, and it costs a
   catalogue-scale operation the compute rules currently forbid.

## 8 · Reviewer verdict

Routed through ARIS's governed reviewer mechanism (backend `codex`, reviewer `gpt-5.6-sol`,
transition by `review_gate.py`; positive requires **score ≥ 6 AND verdict ∈ {ready, almost}**).
Verdict recorded in `review-stage/AUTO_REVIEW.md` and appended at §8a. **No success criterion in
this record may be weakened to obtain a pass** (`WA-A.5`).
