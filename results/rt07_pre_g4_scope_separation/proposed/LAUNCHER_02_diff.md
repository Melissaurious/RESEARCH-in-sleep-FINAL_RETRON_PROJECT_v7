# PROPOSED minimal launcher diff — `launchers/LAUNCHER_02_rt0_rt7_definition.md`

**NOT APPLIED.** The launcher is outside this track's write boundary (§9c), and §9b reserves
changing the scientific question to the operator. Four edits.

---

## EDIT 1 — §5d evidence hierarchy · **the blocking change**

**Current**

| tier | assets | permission |
|---|---|---|
| derivational primary | Poch 1989; Xiong & Eickbush 1990; Zimmerly 2001; Simon & Zimmerly 2008; `ALIGN_000044` | may inform reconstruction of the historical sequence framework |
| independent structural | Blocker 2005 and the registered RT structures | may **constrain or test**; may **not** manufacture the seven-way sequence partition |
| published comparators | Toro 2014; Mestre 2020; myRT reference assets; Toro 2026 and SPIRE | compared against only; **must never seed the reconstructed frame** |
| prior project work | `D_instrument`, `M_models`, prior HMMs, boundary tables | `PRIOR / UNVERIFIED`; no prior numerical result becomes an acceptance criterion |

**Problem.** "The reconstructed frame" is read as one object. There are two. Under the current
wording the only material that may seed *anything* is `ALIGN_000044` — 66 records, 65 unique, one
RT class — which is the substrate that failed two design reviews. **Stage 2B cannot be built at
all under §5d as written.**

**Proposed** — split the permission column in two; no asset changes tier:

| tier | assets | may seed **2A** historical reconstruction | may seed **2B** broad operational instrument |
|---|---|---|---|
| derivational primary | Poch 1989; Xiong & Eickbush 1990; Zimmerly 2001; Simon & Zimmerly 2008; `ALIGN_000044` | **YES — and only these** | YES, as one class among many, never as the panel |
| independent structural | Blocker 2005; the 39 registered RT structures | NO — may constrain or test only | **NO** — may constrain or test only, after freeze |
| broad RT reference material *(new row)* | myRT `RTs-collection.faa`, the 45 family seed FASTAs and `.sto` alignments, Pfam `RVT_1` | **NO — never** | **YES**, under §5f below |
| published comparators | Toro 2014; Mestre 2020; Toro 2026 and SPIRE; myRT `RVT-ref` package | NO | NO |
| prior project work | `D_instrument`, `M_models`, prior HMMs, boundary tables | NO | NO |

Note that myRT is **split across two rows**: its family seeds and full-length collection become
broad reference material, while `RVT-ref.fst` stays a comparator — 1,828 of its 1,844 sequences
are already family seeds, so it adds no derivation value and carries the checksum problems of
§5c.

**Proposed new §5f — conditions on broad RT reference material**

> Broad RT reference material may seed a **2B** operational instrument only under all of:
> (a) its genealogy against `all167`, `anchors72`, `GOLD171` and `ALIGN_000044` is measured and
> landed before use — currently 17, 12, 13 and 11 of 1,988 by containment;
> (b) its family labels are used as **strata only**, never as ground truth, because Stage-1's own
> labels are the same instrument's output;
> (c) it never seeds **2A**;
> (d) any question about RT0 or the N-terminus uses **full-length** substrates only — the myRT
> seeds are Pfam `RVT_1` excisions and the measured window on LtrA is residues **90–360**, while
> Blocker's RT0 zone is **1–85**, so the region is absent from the seeds by construction;
> (e) whole families are held out for class-transfer evaluation and named before derivation.

## EDIT 2 — §7 gate table

**Remove** the `rt07_g4_operational_boundary_model` row. **Insert two rows**, both `FULL`:

> **`rt07_g4a_reference_design`** — the measured composition of a broad RT reference panel:
> available diversity per family, redundancy structure, full-length eligibility, the declared
> caps and floors, and the named held-out classes. Settles `C3` supporting. Done when
> `results/rt07_g4a_reference_design/` reruns and reproduces the panel composition table, the
> genealogy table and the held-out class declaration.
>
> **`rt07_g4b_operational_core_coordinates`** — mapping reproducibility and class-transfer of a
> broad-RT homologous core coordinate mapper, reported per held-out RT class and per
> identity-distance bin, with the historical RT0–RT7 crosswalk as a mapping layer over the frozen
> output and cardinality including non-correspondence. `BOUNDARY_ACCURACY` and
> `BOUNDARY_CALIBRATION` are declared `UNESTABLISHED` at the outset. Settles `C3` primary, `C9`
> primary. Done when `results/rt07_g4b_operational_core_coordinates/` reruns and reproduces the
> coordinate definitions, the crosswalk, the per-class transfer tables, the stability ensemble,
> the genealogy audit and a frozen portable package.

Ordering line becomes: `g1`,`g2` → `g3` → `g4a` → `g4b`; `g4b` frozen before `g5`.

## EDIT 3 — §4 inputs and trust grades

The registered myRT row points at `references/rt0_rt7/myrt/`, which is the reference **package**
— 1,844 fragments. The objects Stage 2B would actually use are not registered. Add:

| path | what it is | trust grade |
|---|---|---|
| `…/src/myRT/Models/RTs-collection.faa` | 2,339 full-length family-labelled RT proteins, 38 real labels plus `NotUsed` 136 and `UNC` 1 | `RE-DERIVE` |
| `…/src/myRT/Models/HMM/*.fst` (45 canonical) | 1,988 records / 1,986 unique RT-domain fragments, 0 cross-family duplicates | `RE-DERIVE` |
| `…/src/myRT/Models/HMM/*.sto` (46) | per-family Stockholm alignments carrying `#=GC RF` match states | `RE-DERIVE` |
| `…/src/myRT/Models/HMM/RVT-All.hmm` | 45 models, summed `NSEQ` 1,988 | `RE-DERIVE` |
| `…/src/myRT/Models/HMM/buildRVT.sh` | the build script establishing the Pfam `RVT_1` excision provenance | `FROZEN` as a provenance document |
| `…/src/myRT/Models/cdd-pfamA/` | the local CDD/Pfam-A profile set containing `RVT_1` | `RE-DERIVE` |
| `MELISSA_DATA/crystal_structures/` (25 files) + 14 anchor-only entries | 39 distinct RT-bearing PDB entries; **0 non-LTR, 0 telomerase** | `RE-DERIVE` |

Add to §5b's known-wrong list: **the `RVT-CRISPR-like` label is absent from `RVT-All.hmm`** yet
Stage-1 carries it as a family with 3,168 exact RTs; and the seeds and `RTs-collection.faa` use
**different family vocabularies**.

## EDIT 4 — §1 success criterion 2

**Current:** *"an operational per-block detector exists that emits a call state and an uncertainty
interval per (exact RT, block), derived on a conservative full-length set and evaluated on a
held-out population whose independence from the seed is measured and reported"*

Two defects: "per-block" presumes the partition the evidence does not support, and "conservative
full-length set" was read as the historical substrate.

**Proposed:**

> an operational coordinate mapper exists that emits, per (exact RT, conserved anchor or region),
> a call state and a stability interval; it is derived on a **declared broad RT reference panel
> whose family composition is landed before derivation**, and is evaluated on **held-out RT
> classes** and by identity distance, with its genealogy against every prior seed and evaluation
> set measured and reported. Region count is never fixed in advance. Failure to transfer to a
> class is a result.
