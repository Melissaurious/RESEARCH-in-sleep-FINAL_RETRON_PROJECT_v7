# PROJECT DEPENDENCY GRAPH — revision 2

**Revision 2** adds `embed_x2` (`4f8550b`) and the closed Stage 3C (`34000ee`), and corrects two
revision-1 rows: the "blocked" verdicts on partner specificity and on phylogeny.

What each result rests on, what it can carry, and where a defect would propagate. The point is to
show which downstream work is *actually* unblocked and which only looks unblocked.

---

## 1 · The spine

```
                    ONE JSON PARSE OF ONE MINING CORPUS
              (43 files, 3,358,182 lines, manifest 8e9b7999…41d00)
                                   │
              ┌────────────────────┴────────────────────┐
              │                                         │
      RT-anchored 3,059,700                    ncRNA-anchor-only 298,482
              │                                  (held OUTSIDE every RT denominator)
              ▼
   dbchar_g2 · canonical units  ──► exact RT 501,561 · locus 2,847,312
              │                     physical locus 2,475,684
              ├──► dbchar_g2b · RT CDS recovery (31,504 explained)
              ├──► dbchar_g3 · pair geometry  ──► 30,924 exact RT–ncRNA pairs
              ├──► dbchar_g4 · family baseline (Retron 78,287 exact RTs; 16,458 exact ncRNAs)
              ├──► dbchar_g5 · metadata / sampling
              └──► dbchar_g6 · tool calls  ──► THE EXTRACTION ASYMMETRY (6.6-fold)
                                   │
        ┌──────────────────────────┼───────────────────────────┐
        ▼                          ▼                           ▼
  STAGE 2 (rt07)            EMBEDDING TRACK              WORKBENCH / SPIRE
  g1→g2→g3→g4a→UG25         g0→g1→g2a→g2b→g2→g2c         Z6 → SPIRE R1 → R2 → post-mortem
        │                    │        └─► embed_x1        (branch CLOSED)
        ▼                    ▼
  g4b FROZEN INSTRUMENT   type-level signal only
  rtmap-1.0.0/53a1e738      (rung 3 FAILED)
        │
        ├─► g5a eligibility census  ──► G5_ELIGIBLE_N = 369,381   ◄── THE denominator
        ├─► g5 catalogue application ──► 354,102 inspectable
        ├─► g6 family architecture   ──► descriptive concordance ONLY
        └─► g7a RT0–RT7 bridge       ──► LtrA-local; RT0/RT1 UNRESOLVED
                                   │
                                   ▼   (descriptive use only, per the closure)
                          STAGE 3A structural ──► FAILED (0.565 < 0.70)
                                   ▲
                                   │ population supplied by
                          STAGE 3B catalytic ──► STOPPED on K5 (labelled "PARTIAL")
                                   │
                                   ▼
                          STAGE 3C ──► COMPLETE (34000ee): census over the SAME 62 chains
                                       A: catalytic site single-unit 19/19 (NO retron chains)
                                       B: state blocks MERGE; RT0/RT1 0/62
                                       C: literature fingers coincide 0/11; refs contradict
                                       D: Region Y not universal, not exclusive; 1.34x RNA contact
                                       E: termini interpretable in only 20/62

  embed_g2 (retrieval) ──► rung 3 FAILS (+0.0298 [-0.0048,+0.0633])
        │
        └─► embed_x1 (one held-out fold) ──► embed_x2 (4f8550b): 5-fold component-blocked
                                             cross-fit over ALL 1,075 components
                                             G-U -0.0426 · R-G -0.0055 · C3 52.5% of pairs
                                             ⇒ NO UNTOUCHED HOLDOUT REMAINS IN PAIR-ELIG
```

## 2 · Single points of failure

| node | what breaks if it is wrong | mitigation on record |
|---|---|---|
| **The corpus parse** | `C1`, `C2`, `C8` move together — every unit count, every rate, every denominator | record-manifest digest; independent second count per gate; contract prices it `LOW`, not `NONE` |
| **The Mestre CM lineage** | the retron *population itself*, every carriage rate, every subtype stratum, g6's grouping, the embedding "retron type" variable, SPIRE's truth | stated in several places; **not** consistently used to discount numbers (see OQ-01) |
| **`G5_ELIGIBLE_N` = 369,381** | every g5/g6 rate; using 501,561 instead inflates every denominator by 26.35 % | frozen census bundle; stated in `CURRENT_PROJECT_STATE.md` §3 |
| **The GII-centred frame** | every between-family architecture comparison (median MAPPED 0.94 GII → 0.49 Retron) | declared as constraint 1 of the Stage-2 closure |
| **`support.csv` (175-element panel)** | the only local experimental anchor | now **mapped**: `PANEL_LEAKAGE_MAP.tsv` — 58 train-exposed, 33 val/test-exposed, 56 catalogue-only, 12 near, **16 fully external** |
| **The absence of any untouched holdout** | every confirmatory test of the pairing model | created by X2's full cross-fit; the only external material is the 16 fully-external panel elements — **unresolved, OQ-16** |
| **The 62-chain structural population** | Stage 3A *and* Stage 3B share it, and 3B assembled it for catalytic truth | code allowlist blinds the inputs, not the selection |
| **`ARIS_OUTPUT/embed_x1_conditional/work/*.npy`** | gitignored scratch; the X1 pilot and its component table are **not re-derivable from git** if cleared | none |
| **`…-dbchar-workbench/ARIS_OUTPUT/dbchar_workbench/`** | the only copy of the Stage-1 thesis-writing material (88 MB, in no branch) | text-only snapshot tracked at `docs/dbchar_workbench_snapshot/` |

## 3 · What is genuinely unblocked, and by what

| downstream work | depends on | status of that dependency | verdict |
|---|---|---|---|
| Stage-1 descriptive chapter / resource paper | g1–g7b | landed, REPRODUCIBLE, `human_input_audit: PENDING` | **unblocked** after the audit clears |
| Stage-2 methods chapter / methods paper | g4b, g5a, g5, UG25 | landed and reviewed | **unblocked** |
| Any RT0–RT7 *label* statement | `docs/errata/g7a_…erratum_2026-09-19.tsv` | binding; RT0/RT1 closed as UNRESOLVED | **unblocked but tightly bounded** |
| Between-family architecture biology | the GII frame | confounded by construction | **blocked** — not by process, by evidence |
| Classification reassessment from g6 | g6 | review states BLOCKED on the evidence | **blocked** |
| Stage-3C Comparisons A/B/C/D/E | 3A + 3B + Stage 2 frozen outputs | **all ran**; 236 hash-checked inputs matched | **complete**; what remains is a promotion decision, not analysis |
| Stage-3C Comparison A speaking about **retrons** | Tier-B/C truth admission (X12) | Tier B never opened in 3B | **blocked by default** — Comparison A is retron-free |
| Partner-specificity claims from embeddings | arms G and P | **both ran (X2)**; lineage carries ~77 % of R−T; residual survives in sign | **unblocked at levels (i)–(ii); still blocked at (iii) pair discrimination and (iv) biochemistry** |
| A compatibility / contrastive model | a confirmatory population | **X2 trained on every fold — none remains inside PAIR-ELIG** | **blocked** until one is declared (OQ-16) |
| Any co-evolution test | a relatedness/phylogeny null | **does not exist anywhere in this project** | **blocked** — but the need is now stronger, since the measured effect lives largely in lineage structure |
| A modern label-independent phylogeny | a preregistered design | never attempted here; the failed routes targeted other questions | **open, not blocked** — rev-1 wrongly closed it |
| Region Y × exact-RT residual join | `XY_REGION_ANNOTATIONS.tsv` (rt_hash-keyed) + the modelling dataset | both exist; Stage 3C left the join out of scope deliberately | **unblocked, needs preregistration** |
| Supervised ncRNA boundary prediction | a non-circular boundary truth set | the 977 set does not exist; the panel gives 175 published extents, **58 train-exposed**, leaving ~95 not train-exposed | **blocked as prediction; unblocked as boundary-disagreement characterisation** |
| Neighbour / effector architecture | neighbour sequences | all 41.3 M have `has_sequence = False` | **blocked** until a parse exists |
| Fusion-domain analysis | a domain-annotation route | local Pfam is a stub; full Pfam-A is registered on Ibex | **blocked locally, feasible on Ibex** |
| Laboratory candidate prioritisation | a scored, non-circular pairing model | none exists; the framework is design-only (F7 is synthetic) | **blocked** |

## 4 · Dependency inversions worth noticing

1. **Stage 3B supplied Stage 3A's population, then Stage 3A was declared blind to Stage 3B.** The
   blinding is real at the level of *inputs* (an executable allowlist) and unavoidable-by-design at
   the level of *sample selection*. Any Stage-3 write-up must state the direction of this
   dependency.
2. **The embedding track's "independent" variable comes from the ncRNA side.** `retron_type` is the
   ncRNA's own covariance model, so arm T of the conditional pilot and rung 3 of the retrieval
   ladder both condition on an ncRNA-derived label. The protein→label direction (ESM-C, 0.4978) is
   the only non-circular half.
3. **SPIRE's benchmark truth is the thing SPIRE was meant to discover independently.** The 21 CMs
   were themselves built by CMfinder on clade-grouped upstream windows, so a CMfinder motif
   overlapping a CM call 97.9 % of the time is partly a same-paradigm rediscovery. This is why G7
   (the positional prior) is the informative gate, and why it is the one that failed worst.
4. **Stage 3C inherits Stage 3B's mislabel.** Its report repeats "3B stays CLOSED at PARTIAL", so a
   documentation defect in a stopped track has now propagated into a freshly packaged bundle. Repair
   T0-1 before either is cited.
5. **X2's strength created a new dependency.** By cross-fitting every fold it removed the last
   untouched holdout inside PAIR-ELIG. Statistical power was bought with confirmability.
6. **The historical bridge depends on a single protein.** Everything in g7a was measured on LtrA. A
   second reference protein is not a nicety; it is the only way the correspondences become more than
   LtrA-local.

## 5 · Propagation map — if one thing turned out wrong

| defect | what falls | what survives |
|---|---|---|
| A coordinate/extraction defect in the corpus parse | every Stage-1 unit count, all geometry, the g5 denominator, the embedding pair set | nothing quantitative; the *methods* survive |
| One CMfinder-era covariance model is wrong | retron carriage rates, subtype strata, g6's grouping, embedding type labels, SPIRE truth | Stage 2's mapper (it never uses ncRNA), Stage 3A (contract forbids it) |
| The mapper's GII frame is unfit for retrons | every between-family architecture comparison, parts of g6 | the mapper as a GII-family instrument; the RT0/RT1 negatives (they are *about* the frame) |
| `1RTD_A`-style threshold effects dominate Stage 3A | the interpretation "no compact palm unit" | the narrower, still-publishable "PDP + these thresholds do not recover it" |
| The Khan panel attribution is wrong | the experimental register's provenance column | the sequences and assay values themselves, which are internally consistent |

## 6 · Reading order for a fresh reviewer

1. `docs/CURRENT_PROJECT_STATE.md` — stage, instrument, denominators, constraints
2. `docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv` — what may be said per historical label
3. `docs/decisions/2026-09-19_stage2_g6_review_errata.md` — how every g6 sentence must be read
4. this file, then `PROJECT_EVIDENCE_MAP.md` §3 (contradictions) and `NEGATIVE_RESULTS.md`
5. `EXPERIMENTAL_RT_NCRNA_REGISTER.tsv` + `PANEL_LEAKAGE_MAP.tsv` — the experimental layer and what
   it can actually support (16 of 175 elements fully external)
6. `results/embed_x2_rt_specificity_confirmation/DECISION.md` and
   `analysis/stage3c_architecture_integration/STAGE3C_DECISION_REPORT.md` — the two new closures,
   both of which state their own limits well
