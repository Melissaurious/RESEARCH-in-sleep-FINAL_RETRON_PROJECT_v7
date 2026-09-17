# DECISION — Full-length-first: complete RT proteins as the architecture substrate, RVT_1 fragments as anchors only

Date: 2026-09-16 · Track: `rt07` · Status: **proposed; pending independent review and operator acceptance**

Implements the operator's explicit scientific direction of 2026-09-16 and **supersedes** the
reference-design and launcher-amendment portions of
`docs/decisions/2026-09-16_stage2_scope_separation.md`, as corrected by
`docs/decisions/2026-09-16_stage2_scope_separation_errata.md`. Neither is rewritten.

Supersede this record by a new record, never by rewriting it.

Design artifacts: `results/rt07_pre_g4_full_length_design/`.

**NO FULL-CATALOGUE APPLICATION; g5 NOT STARTED.**

---

## 1 · The operator's direction, and why the measurements support it

> *Start from complete/full-length RT proteins rather than pre-excised RVT_1 fragments. Use the
> RVT_1 fragments/HMMs as homologous-core anchors and comparators, not as the sequence universe
> from which architecture is defined.*

**Measured, and it justifies the direction quantitatively.** Mapping all 1,988 myRT seed fragments
back onto their full-length parents (1,835 mapped by exact substring):

| what RVT_1 excision discards | measured |
|---|---|
| N-terminal sequence per protein | median **97 aa**, mean 112.3, max **631** |
| C-terminal sequence per protein | median ranges 14–1,120 aa by family |
| proteins with ≥80 aa N-terminal of the window | **1,138 of 1,835 — 62.0%** |

80 aa is the size of the LtrA RT0 zone (1–85). So for **62% of proteins the excision removes
enough sequence to contain an RT0-sized feature**, and a fragment-only design would render any
finding there impossible by construction rather than by evidence.

The direction is therefore justified not as a preference but as a **restoration of observability**.

## 2 · The measurement that makes RT0 a real question

Median N-terminal extension by family — the sequence space where an RT0-like feature would sit:

    UG10 468 · UG25 458 · CRISPR-G2 358 · UG1 205 · GII-I 110 · GII-II 88 · DGRs 72 · Retrons 51

**Group II intron RTs carry 88–110 aa there; retrons carry 51 aa.** Both GII medians exceed the
85 aa LtrA RT0 zone; the retron median does not.

This is a measured architectural difference in exactly the place that matters. It is **not**
evidence that retrons lack RT0 — it is measured against a Pfam-defined window, on 95 retrons, and
the defining cross-class claim still needs a non-LTR comparison class this project does not hold.
`rt0_test_design.md` states the five admissible outcomes and the blocking gap.

## 3 · The usable full-length population

| quantity | measured |
|---|---|
| records in `RTs-collection.faa` | 2,339 |
| unique amino-acid sequences | **2,339 — zero duplicates** |
| after excluding `NotUsed` (136), `UNC` (1), 10 non-standard-residue sequences and sub-250 aa fragments | **2,166 eligible** |
| non-redundant at 4-mer Jaccard 0.90 | **2,165 of 2,166** |

**The collection is already dereplicated.** Median within-family pairwise 4-mer Jaccard is
0.007–0.177. This changes the design: **redundancy control is not the binding constraint — family
imbalance is.** The previous round's emphasis on redundancy reduction was misplaced.

**Coverage gap, recorded:** 8 families have under 70% of their seeds mapping to any shipped
full-length protein — AbiP2 18.6%, UG24 18.2%, AbiK 41.7%, UG10 43.8%, G2L4 47.1%, UG23 50.0%,
UG2 59.1%, UG20 62.5%. For these, full-length parents are **not locally available**, so
full-length-first coverage is incomplete precisely where seed evidence exists. The previous
record's "version drift" explanation for the 153 unmapped seeds is now quantified and localised
rather than asserted.

## 4 · Roles of the three myRT objects

| object | N | role |
|---|---|---|
| `RTs-collection.faa` | 2,339 records / 2,166 eligible, **full length** | **PRIMARY derivation substrate** for broad architecture |
| 45 seed FASTAs | 1,988 / 1,986 unique, RT-domain fragments | **anchors and comparators only.** Never the sequence universe; no absence inferred outside the window |
| 45 HMMs (`RVT-All.hmm`, `NSEQ` 1,988) | 45 models | family-classification **context** and a core-localisation resource. **Never family ground truth** |

`RVT-ref.fst` (1,844, of which 1,828 are already seeds) adds no derivation value and stays a
comparator.

## 5 · Anchor-first, and what the anchors actually support

`[YF]xDD` occupancy measured across all 2,202 labelled collection proteins:

- **94.9% (2,090/2,202)** carry a literal dyad — against 84.8% (56/66) on the historical GII
  substrate, so the broad substrate is the *better* one for anchor work;
- **251 (11.4%) carry more than one** — a multiplicity rule is mandatory;
- **7 families fall below 90%**: UG13 **52.0**, UG23 66.7, UG15 69.2, UG21 69.6, G2L 76.4,
  UG12 86.5, **Retrons 89.6**;
- where a mapped protein has a dyad, it lies inside the `RVT_1` window in **1,751 of 1,758 cases
  (99.6%)** — a reliable within-core anchor.

**Binding consequences.** No single anchor suffices: `F02` requires **at least two anchors in ≥90%
of panel proteins** or the common frame is abandoned. The seven anchor-poor families are
**predeclared**, so a low mapping rate there is a property of the reference material, not a
biological finding. And the focal class is not exempt — **retrons sit at 89.6%, just below the
line**, and that figure must travel with every retron result.

The Poch et al. 1989 four conserved motifs are the obvious second anchor and their occupancy is
**unmeasured**; measuring it is a precondition, not an assumption.

## 6 · The balanced panel, and the question this task could not settle

Hierarchical — **lineage first, family second**. Per-lineage target 90, Abi exhaustive:

    GII_like 90/555 · DGR 90/488 · CRISPR 90/129 · Retron 90/95 · UG 90/863 · Abi 36/36
    PANEL 486 of 2,166 eligible.  UG 18.5%, Retron 18.5%.

Contrast the previous round's per-label cap, which measured at **73–77% UG and 3–4% retron** — the
opposite of its stated purpose. That flaw is corrected here and §5f(f) forbids per-label capping.

**Unsettled, and returned:** whether **UG is one lineage or 29**. UG means *unknown group*;
whether its 29 labels are 29 lineages, a few clades, or a paraphyletic grade is established by
nothing in this project. `UG_OPTION_A` (one lineage, ~3 per label) and `UG_OPTION_B` (29 lineages,
≈66% UG) give materially different panels. `V09`/`F08` make the choice **auditable** — the frame
is rebuilt under both and the movement measured — but they do not settle it.

### A resource the previous review said was missed is half present

The previous reviewer asserted two locally held resources had been overlooked. Both were searched
for and the result is mixed, not a simple miss:

- **The Toro et al. 2019 9,141-RT reference tree IS here** —
  `references/rt0_rt7/myrt/Suppl_Toro_Tree.txt`, **measured at exactly 9,141 tips**, sha256
  `ea0ee646…`, with six byte-identical copies on this machine. It is the scaffold the 2022 UG/Abi
  paper used. It is **misfiled under `myrt/`** — it is Toro 2019, not myRT — and the project's own
  README had flagged its year as unestablished. It can now be dated.
- **What it does not carry is group annotation.** Tips are SEED/PATRIC `fig|` IDs plus organism,
  with no UG label, and the **2022 42-group assignment table and supplementary FASTAs are not on
  this machine**.
- **Silas et al. 2017's 266 RT-Cas loci are confirmed absent** — the paper is held in three copies
  and states the data are figshare-hosted.

**Consequence for the UG question.** The tree supplies *topology*, which is exactly what the UG
allocation needs. A bounded, local, catalogue-free join of myRT's UG labels onto the 9,141 tips
would turn `UG_OPTION_C` from a deferred preference into an evidence-based choice. **Whether that
join is possible is unverified** — it depends on matching myRT identifiers to SEED/PATRIC `fig|`
IDs, which has not been tested. `UG_OPTION_C_PATH` records this as the bounded next step rather
than assuming it works.

A separate caution: `hmms_per_domain_MyRT_round2/` (41 directories, 32 UG/Abi labels) is
**myRT-derived and rebuilt from an Ibex copy in June 2026**. It is not the 2022 paper's 42 groups
and must not be mistaken for an independent UG classification.

**Retron depth is the other binding limit:** only **95** eligible full-length retrons exist in
myRT. The retron-focal view cannot be built from this panel alone and needs a bounded declared
Stage-1 retron sample.

## 7 · What stays unestablished

Unchanged across three prior reviews and not reopened: **`BOUNDARY_ACCURACY` and
`BOUNDARY_CALIBRATION` `UNESTABLISHED`**; **biological presence/absence (`V12`) `UNESTABLISHED`**,
with `NOT_DETECTED_INSPECTABLE` renamed to `NOT_CALLED_ON_COMPLETE_SEQUENCE`; **family assignment
accuracy `UNESTABLISHED`** (Stage-1 labels are myRT's own output under a documented collapse —
38 one-to-one, 7 fine-to-coarse, 1 rename); **phylogenetic eligibility `UNESTABLISHED`**; **no RT0
occupancy**; **`C9` not assigned to any g4 gate**.

Three quantities are kept distinct and never substituted: **homology support**, **mapping
confidence**, **biological presence**.

## 8 · Reviewer verdict

Routed through ARIS's governed reviewer mechanism (backend `codex`, reviewer `gpt-5.6-sol`,
transition by `review_gate.py`). Verdict recorded in `review-stage/AUTO_REVIEW.md` and appended at
§8a. **No success criterion in this record may be weakened to obtain a pass** (`WA-A.5`).
