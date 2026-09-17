# Historical reconstruction substrate vs general RT operational reference set

Two objects have been conflated in Stage 2. This document separates them from the landed
evidence and states what each can and cannot do.

    HISTORICAL_RECONSTRUCTION_SUBSTRATE    ALIGN_000044, 66 records / 65 unique, ONE RT class
    GENERAL_RT_OPERATIONAL_REFERENCE_SET   does not yet exist in this project

---

## 1 · What the g2 substrate actually is

### Exact composition, measured

`results/rt07_g2_reference_reconstruction/reference/g2_reference_set.faa` and
`tables/g2_reference_sequence_set.tsv`:

| property | measured value |
|---|---|
| records | **66** |
| **unique amino-acid sequences** | **65** — see the duplicate below |
| RT classes represented | **one** |
| ungapped length range | 599–687 aa (full length) |
| lineage groups | mitochondrial 29 · bacterial 20 · algal/chloroplast 11 · euglenoid 6 |

### Every one of the 66 is a group II intron-encoded ORF

The shorthand does **not** overstate the composition. Reading the descriptions: `nad1 intron 4`,
`cox1 intron 1`, `psbC intron 4`, `LSU rRNA intron 1`, `petD intron 1`, `atp9 intron 1`,
`cob1 intron 3`, `ltrB intron`, `IS629-like orf intron`, `orf14 intron`. The two that do not
carry an intron number — `M.p.ORF732` and `A.l.orf456` — are intron-associated ORFs from the
same alignment.

**The four "lineage groups" are host compartments, not RT classes.** All 20 members of the
`bacterial` group are bacterial group II introns, LtrA (`L.l.`, *Lactococcus lactis* ltrB
intron, AAB06503) among them. Zimmerly's four subgroupings partition *where the intron lives*,
not *what kind of RT it is*.

Absent from the substrate: **retrons, DGRs, Abi (AbiA/AbiK/AbiP2), CRISPR-associated RTs, all
28 UG families, non-LTR RTs, telomerase, and viral RTs.** Of the 42 Stage-1 family labels,
exactly one — `RVT-GII` — is represented, by lineage rather than by any attached label.

### New finding: the substrate contains a duplicate

`O.s.petDI1` (*Oocystacea* sp. petD intron 1, S05341) and `S.o.petDI1` (*Scenedesmus obliquus*
petD intron 1, P19593) are **byte-identical over 610 aa** under two different names and
accessions. This appears in no landed table. It means:

- the substrate is **66 records / 65 unique sequences**;
- the `algal_chloroplast` group is 11 records / 10 unique;
- the g2 conservation criterion counts *"elements of a group"*, so the duplicate contributes
  twice to the algal group's denominator.

This does not invalidate g2 — the effect is one element in the smallest-but-one group — but any
re-derivation must flag it, and it belongs in the record.

### Why these sequences appear in ALIGN_000044

`ALIGN_000044` is the amino-acid alignment **Zimmerly, Hausner & Wu submitted to EMBL** alongside
*"Phylogenetic relationships among group II intron ORFs"*, NAR 29(5):1238–1250 (2001)
(`references/rt0_rt7/RESOURCE_REGISTER.tsv`, `asset_id = zimmerly2001_align_000044`). The paper is
a **group II intron ORF phylogeny**. Its sequence set is therefore exactly what its title says:
the group II intron ORFs available in 2001, sampled across the compartments where group II
introns were then known.

The RT0–RT7 labels were not invented there. Zimmerly's own statement (g1 assignment Z04) is that
the subdomain labels were **inherited from earlier work and adjusted to the boundaries of
conservation seen in this alignment**. The terminology comes from Xiong & Eickbush 1990; this
alignment is where it was *adjusted*.

## 2 · What g2 legitimately answers

> Applying the founding conservation criterion verbatim to the alignment against which the
> RT0–RT7 labels were adjusted, what conserved sequence structure is recovered, and do the
> historical landmarks reappear?

That is a well-posed historical question, and the substrate is the **correct and only** substrate
for it. Using the 2001 group II intron ORF set to reconstruct a 2001 group II intron ORF
alignment's conserved structure is not a sampling error — it is the experiment.

g2's landed answers stand (§4 below).

## 3 · Why the same substrate cannot carry a general RT instrument

Three independent reasons, each measured:

1. **One RT class.** A coordinate system derived on group II intron ORFs and applied to retrons,
   DGRs, Abi and 28 UG families is a single-class extrapolation to 41 unseen classes. The
   previous design called every Stage-1 family "out-of-family by construction" and drew the
   consequence that no held-out split existed. The premise was wrong — `RVT-GII` *is*
   in-family — but the deeper problem is the one it obscured: a single-class derivation panel
   cannot hold out a class, so **class-level transfer was untestable in principle**.
2. **Retrons, the project's primary biological target, are entirely unrepresented.** Stage-1
   carries 78,292 retron exact RTs. The derivation set has none.
3. **The historical substrate is not designed for diversity.** It is designed for one clade's
   phylogeny, sampled by what had been sequenced by 2001.

**A single-class historical substrate is the right instrument for Stage 2A and the wrong
instrument for Stage 2B.** That is the whole conflation.

## 4 · What is preserved from g1–g3

Changing the next instrument does not retract the historical arm. These stand:

- the provenance and genealogy of the RT0–RT7 terminology (`g1`);
- the historical landmarks substantially recover on their own source material — 2 `RECOVERED`,
  5 `PARTIALLY_RECOVERED` of 9 testable statements, and the `g2` kill criterion was
  `NOT TRIGGERED`;
- **the conserved positions carry real, non-random signal**: 81 strict columns against a
  residue-shuffle null whose mean, minimum and maximum are all 0 across 200 replicates,
  empirical p = 0.0050;
- ordering substantially survives — 27 of 28 prior landmark placements fall inside an
  independently reconstructed region, and order is monotone in LtrA coordinates;
- historical RT5 (LtrA 308) and RT6 (LtrA 344) map **within one** reconstructed region;
- a forced seven-region partition is **not** independently supported — block count never
  separates from a column-permutation null at any gap tested;
- exact boundaries are not externally established;
- RT0 has a distinct historical status and no RT0 occupancy may be carried forward;
- RT1 remains the unstable landmark and its interpretation is deferred (`U08`).

> **The distinction that must survive:** *"six blocks is not established as a biological
> constant"* is a statement about the **partition count**. It is **not** a statement about the
> conserved positions, which are strongly non-random, nor about their localization, which
> reproduces across independent alignment frames. The count is a free parameter; the positions
> are a measurement.

## 5 · What a general reference set would have to be — and what exists

The resource inventory (`tables/reference_source_inventory.tsv`) finds that broad, family-labelled
RT reference material **already exists locally**, in the myRT distribution. Its structure matters
more than its size.

### myRT is three different objects, and they are not interchangeable

| object | N | sequence kind | consequence |
|---|---|---|---|
| family seed FASTAs, 45 canonical | 1,988 records / 1,986 unique | **RT-domain fragments**, median 201 aa | broad and clean, but windowed |
| `RTs-collection.faa` | 2,339, all unique | **full-length**, median 365–663 aa | the only broad full-length local collection |
| `RVT-ref.fst` | 1,844 | fragments | 1,828 of 1,844 are also family seeds — not independent |

### The seeds are Pfam RVT_1 excisions, and this is decisive

`Models/HMM/buildRVT.sh` documents the procedure verbatim: search `RTs-collection.faa` against
`cdd-PfamA.hmm`, take the `RVT_1` hits, and **`cut -c $start-$stop`** — then filter short
sequences and Muscle-align.

So every myRT seed is an RT domain cut to the Pfam RVT_1 window, and **myRT's implicit coordinate
system is Pfam RVT_1's match states**.

Measured on LtrA, from the seed header `L.l.I1|ML|IIA1|Lactococcus_90_360_GII-II`:

    myRT RVT_1 window on LtrA          90 – 360
    Blocker RT0 zone                    1 –  85     ENTIRELY OUTSIDE
    g2 region 1  (RT0-zone region)     39 –  61     ENTIRELY OUTSIDE
    g2 region 2                        79 – 123     PARTIAL - 90-123 inside
    g2 regions 3-6                    126 – 361     fully inside, catalytic dyad at 306 included

**Consequence, binding: no myRT-derived substrate can address RT0, ever.** The region was excised
before the seeds existed. Any RT0 question requires full-length sequences.

### An unforced convergence worth recording

Three instruments derived independently of one another place the RT core in nearly the same place
on LtrA, and **all three exclude the RT0 landmark at residue 39**:

    Pfam RVT_1 window (myRT)        LtrA  90 – 360
    Blocker 2005 RT1-RT7 span       LtrA  86 – 364
    prior project RT0-RT7 frame     LtrA  53 – 361

This is reported as an observation, not as validation — the three are not fully independent — but
it is the strongest available prior on where a general RT core coordinate system would sit.

### myRT's genealogy: usable for derivation, unusable for validation

| relation | measured |
|---|---|
| myRT seeds ∩ `all167` (containment) | **17 of 1,988** — 0.86% |
| myRT seeds ∩ `anchors72` | 12 of 1,988 |
| myRT seeds ∩ `GOLD171` | 13 of 1,988 — 0.65%, **all** `RVT-Retrons` |
| myRT seeds ∩ `ALIGN_000044` | 11 of 1,988 — **all** `RVT-GII-I`/`RVT-GII-II`, from 10 of the 66 |
| cross-family duplicate sequences among the 45 | **0** — the family partition is clean |
| Stage-1 family labels | produced by **this same** classification system |

**Role assignment:** myRT is *valid* as broad diversity and derivation material — its
contamination by the old project seed is under 1% — and *invalid* as independent validation of
family assignment, because Stage-1's labels are its own output. It is also *incapable* of
addressing RT0. Rejecting it for lack of independence would be the wrong call; using it to
validate family labels would be circular.

### Package discrepancies, measured and reconciled

- **45** models in `RVT-All.hmm`; summed `NSEQ` = **1,988**; every family's `NSEQ` equals its
  FASTA record count exactly.
- **47** `.hmm` files = 45 canonical + `RVT-All.hmm` + `RVT-CRISPR-like.hmm`.
- **47** `.fst` files = 45 canonical + `RVT-CRISPR-like` (10) + `RVT-test` (21).
- **46** `.sto` alignments, each carrying a `#=GC RF` match-state line.
- `List` holds **43**: the 45 minus `RVT-G2L`, `RVT-G2Lb`, `RVT-G2Lc`, plus `RVT-CRISPR-like`.
- `RVT-CRISPR-like` has an HMM and a FASTA but is **absent from `RVT-All.hmm`** — and Stage-1
  nevertheless carries `RVT-CRISPR-like` as a family label with 3,168 exact RTs.
- The seeds and `RTs-collection.faa` use **different family vocabularies** (`GII-I`/`GII-II` vs
  `GII`; the collection adds `NotUsed` 136 and `UNC` 1).

**The operator's expected ~2,051 seeds / ~47 families is not reproduced by any object measured.**
The closest values are 1,988 canonical records, 2,019 across all 47 `.fst` files, and 2,339 in the
full-length collection; and 45 canonical families, 46 with `RVT-CRISPR-like`, 47 `.fst` files
including `RVT-test`. The launcher's own correction — 45 models, 1,988 sequences — is confirmed
exactly.

## 6 · The fork this creates, which is the operator's

Launcher §5d places Toro 2014, Mestre, myRT and Toro 2026 in the **published comparators** tier:
*"compared against only; must never seed the reconstructed frame."*

That rule is correct for Stage 2A and it makes Stage 2B impossible. If no published comparator may
seed, the only derivation material is `ALIGN_000044` — 66 sequences of one RT class — which is
precisely the substrate that failed two design reviews.

**Stage 2B cannot be built without amending the tier rules, or it cannot be built at all.** The
three exits are set out in the decision record; none of them is this session's to choose.
