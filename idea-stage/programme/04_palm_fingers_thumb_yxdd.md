# Stage 4 · How to detect / delimit / identify palm, fingers and thumb domains and YXDD motifs

*(the YXDD motif should be present inside the palm)*

## 0 · The point of this task

The YXDD motif is supposed to sit inside the palm subdomain, and that expectation is used
everywhere in this field — but nothing here has verified it on real structures at scale,
and the character class we use to find the motif turns out to be our own invention rather
than the field's. So we currently cannot say, for an arbitrary RT, where the palm ends or
whether its catalytic motif is where the textbook says. Once this lands we have a
geometric definition of fingers/palm/thumb anchored on crystal ground truth, plus a direct
test of whether YXDD falls inside the palm — with any exceptions named rather than
averaged away. It also settles where our character class came from, which is unsourced
today and has already killed two of our own claims.

## 1 · ⭐ The ground truth is already computed

`RESEARCH-in-sleep-/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/` carries, **for all 25
crystals**, a per-structure validation table with:

- **fingers / palm / thumb boundaries**
- the **YXDD motif position** (e.g. `5HHJ` `YADD` at residues 236–239)
- **coordinating aspartates**, and site residues retained vs discarded as phantom/hetero
- **DSSP** assignment and SSE blocks
- LPQG presence or documented absence

Files: `boundary_extraction_report.txt` (human-readable) and `reference_boundaries.json`
(machine-readable, 1,025 lines). Producer: `extract_reference_boundaries_v5.py` with
`mkdssp` from the `retron_tradicional` env, 2026-06-22.

**This is exactly this stage's ground truth, and nobody has used it as such.**

## 2 · The instrument also exists — Gate S

The most-attacked claim in the project, and it survived:

| | |
|---|---|
| `A2` | reproduces its published calibration **96.9 / 8.1 to the decimal**; four attacks failed |
| `A4` | **threshold-independent** (plateau ≥ 7 Å); `SEQ_SEP` inert |
| `A5` | cluster 170's 0% is **biology, not folding failure** — pLDDT 94.8 at the tetrad |
| `A6` | **not a fusion detector** — verdicts identical span-sliced |
| `A7` | tracks global structural separation, **z = 16.69** |
| `A8` | an **independent sequence instrument recovers the verdict at 78%** vs a 26.6% base rate |
| `E5` | **predictor-robust** on 18/18 crystals |

Scripts: `s6d_gateS_f14_exact.py` (⚠️ **use this, never `s6b_gateS_LDD.py`** — buggy first
pass), `s6f_gateS_admit_557.py`, `s7z_gateS_crystals.py`.
Method docs: `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X09_gate_s_calibration.md`, `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X10_gate_s_admission.md`, `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X11_gate_s_controls.md`.

## 3 · ⛔ What is unresolved

**The character class has no source.**
- `A10` **KILLED** — *"`[YFWH].DD` is the criterion the field uses"* is false. It is
  **ours**. Published tools admit by **HMM bit score**.
- `A9` **KILLED** — `YIDD` is Y-initiated and **matches** `[YFWH].DD`, so **0 of 18
  crystals were of the excluded class**. The geometric validation survives; the admission
  validation does not.
- `PE15` — *where do `W` and `H` come from?* Never run.
- `A11` — Gate S is **RT-catalytic, not retron-specific**. This is a **bound**: any
  sentence saying "missed retrons" violates it.

## 4 · ⛔ TODO — crystal set re-verification (open)

1. **Re-verify name ↔ identity for all 25** accessions at the RCSB. Filenames are not
   evidence.
2. **Confirm every one is an RT.** The YXDD column covers all 25, but the report's
   `Family:` field literally says **`unknown`**, so nothing asserts the set is RT-only.
3. **Check `9YFD` first** — 1,125 residues / 83 SSE, far larger than the rest. Probably a
   complex or multi-domain assembly, not a bare RT.
4. **Resolve 18 vs 25.** `CLAIM_REGISTER` `A9` says *"18/18 crystals"*; the directory holds
   25. Which 18, and why 7 were dropped, is unrecorded.
5. **Recover or write the acquisition script.** ⛔ **Nothing on borg pulls these** — a grep
   for `rcsb`/`wwpdb`/fetch across `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_SCRIPTS/` and every `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/*/scripts/`
   returned nothing. `run_log.txt` shows the boundary step consuming files someone had
   already fetched, from an Ibex `rt_reference_search/structures` directory. Write a
   logged fetcher: accession list → RCSB → hash each file.
6. ⭐ **Decide the scope beyond bacterial RTs.** `D9` implies an RT0 test **requires**
   group II intron, non-LTR, telomerase and viral RT (HIV-1, HBV) structures. Record the
   inclusion rule before adding any.

## 5 · Prerequisites and ordering

**This stage should run before stage 2, or merge with it** — RT0–RT7 landmarks should be
anchored on crystal geometry rather than derived separately and reconciled later.
Needs the structure id → sequence map (`/home/borg/RETRON_STRUCTURE_ID_MAP_2026-09-09.tsv`,
9,965 rows, sha1-verified) re-derived inside a row before any figure uses it.

## 6 · Traps already paid for

- ⛔ **Full-length and span-sliced structures are different objects.** borg
  `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/pdb/` is full-length (5,109); **Ibex `struct/span_pdb/` is span-sliced
  (5,256)** and does not exist on borg. `crosscheck` caught §4.10 with its table on one
  and its prose on the other.
- ⚠️ **borg and Ibex structure counts differ on every shared set** (Mestre 1,928/1,919;
  ldd557 563/1,060). They are not verified mirrors — hash before assuming.
- ⚠️ **Coordinate-correct is not semantically correct.** Every audit here has been an
  arithmetic audit; ask what object the cut returns, and read every external tool's flags.

---

# 7 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §4 and §5

## ⭐ The ideas document splits this into two stages, and the split is right

§4 is **palm/fingers/thumb detection**; §5 is **YXDD motif analysis**. Keeping them
separate is better than the merge in this document, because they fail differently: a
boundary can be wrong while the motif is right, and vice versa. The claim *"YXDD sits
inside the palm"* is then a **join between two independently-derived results**, not an
assumption baked into one.

Recommended split if this stage is broken up: **4a · core domain boundaries** ·
**4b · catalytic motif** · **4c · the join** (is the motif inside the palm, and where is it
not?).

## Evidence sources to combine

The ideas document lists structural references, sequence alignment, profile HMMs,
HHpred/HHblits, Foldseek, AlphaFold/predicted structures, and conserved catalytic motifs.
What is available here:

| source | status |
|---|---|
| structural references | ⭐ **25 crystals with boundaries already extracted** (§1) |
| predicted structures | ⭐ **9,965 mapped and sha1-verified**; Ibex adds 5,256 span-sliced |
| Foldseek | module `foldseek/10-941cd33` on Ibex; local in the `esmologs` env; all-vs-all TM matrix over 1,919 proteins already computed |
| profile HMMs | ⚠️ **InterProScan here ships a stub** — Pfam-A holds 3–4 profiles locally; 21,979 models are on Ibex |
| AlphaFold / AF3 | databases at `/ibex/reference/KSL/alphafold/{2.1.1,2.3.1,3.0.0}`; ⚠️ no `params/` seen |
| HHpred / HHblits | ⛔ not established here — availability unchecked |

## §5's diagnostic question, which prior work can already answer in part

> *Are apparently missing motifs caused by sequence truncation, annotation error, or
> genuine biological divergence?*

Three causes, three different flags, all available: **truncation** → prodigal `partial` +
contig-edge distance (stage 1); **annotation error** → the three-tool disagreement (stage
12); **genuine divergence** → `A5`, where **cluster 170's 0% is biology, not folding
failure** (pLDDT 94.8 at the tetrad). ⭐ That is a worked precedent for separating the
third cause from the first two.

> *Can catalytic geometry rescue cases where the canonical sequence motif is weak?*

⭐ **This is Gate S's exact purpose, and the answer on record is yes** — `A8`: an
independent sequence instrument recovers the geometric verdict at **78%** against a 26.6%
base rate. And `s5_admission`: **80.7%** of what a published *sequence* cutoff rejects
carries intact catalytic geometry. ⚠️ But `A11` bounds it — geometry recovers **RTs**, not
retrons specifically.

## From the parking lot (§21), belonging here

> *"Analyze whether catalytic-site geometry is more conserved than motif sequence."*

⭐ **Directly testable with what exists** — 25 crystals with per-structure geometry, Gate S,
and 9,965 predicted structures. And it reframes `A9`'s death usefully: the admission
validation died, **the geometric validation survived**. That asymmetry is the hypothesis.

---

# 8 · ⭐⭐ THE CORE MEASUREMENT ALREADY EXISTS — and it constrains what this stage may claim
**Found 2026-09-12 while auditing which stages actually used structure.**

## 8.1 · The subdomain ↔ block overlap, measured

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d2j_boundary_crossvalidation.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d2j_boundary_crossval.tsv

Our derived match states against each crystal's **DSSP fingers / palm / thumb**, as Jaccard:

| structure | fingers | palm | thumb |
|---|---:|---:|---:|
| `5HHJ` | **0.7444** | 0.5182 | 0.2069 |
| `24NC` | **0.8390** | 0.5547 | **0.0000** |

Columns include `their_method`, `their_n_sse_blocks`, `is_retron_rt`,
`their_{fingers,palm,thumb}_res`, `*_state`, `*_overlap_states`, `*_jaccard` — i.e. **it
already reports, per structure, where each subdomain sits and how well our blocks cover
it.** That is the *"I found the palm — is it where it should be?"* table.

⭐⭐ **And the gradient corroborates Simon & Zimmerly 2008 independently.** They state
*"RT domains 1–7 constitute the palm and finger domains… domain X corresponds to the
thumb."* So an RT1–RT7 frame **should** cover fingers well, palm partly, and the thumb
**not at all** — and the measured Jaccards fall **0.74–0.84 / 0.52–0.55 / 0.00–0.21**,
in that order. A 2008 architectural statement and a 2026 Jaccard over crystals agreeing is
worth reporting as such.

## 8.2 · ⛔ The two falsification gates were already declared and run

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21b_truncation_verdict.py
        "FALSIFICATION TEST 1 ... D2.0 declared this test as a GATE: is a structural
         negative at the N-terminus admissible?"
        -> /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d21b_per_chain_nterm.tsv
           (per chain: construct_len, modelled_n_residues, modelled_first_res, ...)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21c_sse_agreement.py
        "FALSIFICATION TEST 2: do the two SSE algorithms agree well enough to set edges?"
         DSSP (H-bond energetics) vs P-SEA (CA geometry)
        -> /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d21c_edge_disagreement.tsv
           (per block: dssp_start/end, psea_start/end, start_delta, end_delta)

⭐⭐ **`d21b` is the RT0 question in structural form** — whether an N-terminal structural
negative can be believed, or whether crystal constructs are systematically truncated there.
**Read it before proposing any N-terminal absence result.**
⭐ **`d21c` is the honest uncertainty model for boundaries**: two independent SSE algorithms,
per-block start/end deltas. That is where stage 4's *"boundaries with stated uncertainty"*
comes from — no uncertainty model needs inventing.

## 8.3 · ⛔ Two corrections this stage must carry

**1 · The anchors are not 72 structure-validated.** `D_instrument/FINDINGS.md` §5, verbatim:
*"**Only 26 of the 72 anchors have a structure.** The other 46 cannot receive a structural
transfer at all; their motif positions are **sequence-derived only**."* Its own
self-adversarial check flags *"the 72 structure-validated anchors"* as an inherited
overstatement. **Say 26 + 46.** A structure-first frame therefore rests on **26 proteins**,
propagated to the rest by sequence — the same transfer step, one layer down.

**2 · Structure cannot adjudicate between published conventions.** Verbatim:
*"The launcher names structure as the adjudicator of the A-vs-B boundary disagreement.
**Structure cannot adjudicate a boundary, because it never set one.**"*
⚠️ That is a **provenance** statement, not a claim that geometry is uninformative — §8.1
shows how informative it is. It means: the published conventions descend from sequence, so
geometry cannot arbitrate between two of them. Geometry **constrains and validates**; it
does not **define** the seven-way split (§7 of this file).

## 8.4 · ⚠️ Three foldseek installs, no agreed version

    /home/borg/foldseek/bin/foldseek                          commit d609cff8ca9250b9994a96207fb22a1585e7964e, 2025-04-22
                                                              ⛔ "reports no semantic version" — D_instrument/FINDINGS.md
    /home/borg/miniconda3/envs/esmologs/bin/foldseek
    Ibex: module load foldseek/10-941cd33

**Pin one before any structural comparison**, and record which. Also on disk:
`/home/borg/miniconda3/envs/foldmason/bin/foldmason`, and `mkdssp` in
`/home/borg/miniconda3/envs/retron_tradicional/bin/mkdssp`.
