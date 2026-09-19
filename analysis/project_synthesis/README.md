# PROJECT SYNTHESIS — independent review, evidence map and programme plan

## REVISION 2 (current)

Revision 1 is **stale and superseded**. It was written before two results landed:

- **`embed_x2`** — RT-specific conditioning, `…_v7-embeddings` @ **`4f8550b`** (results), formally
  **CLOSED** at **`fdf0872`** (closure / handoff / export — **the governing interpretive source**)
- **Stage 3C** — architecture integration, closed and packaged, `…_v7-stage3c` @ **`34000ee`**

Revision 1's thesis sentence, publication ranking and minimum-work recommendation were **withdrawn
and re-derived**, not patched. Four judgements were corrected:

| # | revision 1 said | revision 2 says | why |
|---|---|---|---|
| 1 | partner-specific pairing **failed** | four distinct levels, never collapsed to PASS/FAIL: lineage **ESTABLISHED**, exact-RT residual **SUPPORTED_WITH_LIMITATIONS** (sign replicated, magnitude undetermined), close-counterfactual pair discrimination **UNDERPOWERED**, biochemistry **NOT_YET_TESTED** | X2 cross-fits all 1,075 components with G/P controls; R − G −0.00551 [−0.00797, −0.00312], but C3 favours the observed RT in only 52.5 % of pairs and its raw pair-level mean is −0.000205. The conclusion of record is `X2_CLOSURE.md` §2, not the label `X2-A` |
| 2 | close sequence-tree routes permanently | **reopened**: reproduction of Mestre (FAILED), placement into the 11-clade system (FAILED on K3) and a **modern de novo phylogeny (NOT_YET_TESTED)** are three different questions | the failed instrument was a historical-placement one; the prior tree routes are unverified and targeted other questions |
| 3 | SPIRE post-mortem is circular and disposable | the discovery **failure stands**, and two **features** are inherited: a retron-enriched ~90-nt submotif and a type-conditioned positional prior (92.2 % IoU ≥ 0.5) — usable only against **non-CM** truth | the features are CM-derived, so they may be priors but never their own validation |
| 4 | thesis sentence asserted neighbourhood etc. carry no retron identity | untested things are now called untested; annotation lineage is described as how the **population** is defined, not as biology | neighbourhood was only ever tested as a *discriminator*, in unverified prior work |

**Read-only.** No frozen bundle was modified, no gate reopened, no compute started beyond an
exact-hash join for the leakage map. Not claim authority — `idea-stage/docs/research_contract.md` is.

## Files

| file | what it is | rev 2 |
|---|---|---|
| `PROJECT_EVIDENCE_MAP.md` | 16 evidence areas graded (incl. **§2.10a OpenCRISPR as methodological precedent**), contradictions (§3, now 10), the 977 verdict (§4), reviewer-acceptance table (§5) | **rewritten** |
| `CLAIM_EVIDENCE_MATRIX.tsv` | **48** claims × 16 cols, carrying a `rev1_grade` column so every change is visible; X2 rows pinned to `4f8550b`/`fdf0872` | **rewritten** |
| `PROJECT_DEPENDENCY_GRAPH.md` | what rests on what; single points of failure; what is genuinely unblocked | **updated** |
| `OPEN_QUESTIONS.tsv` | 17 questions; OQ-05 **CLOSED by X2**; OQ-08 **reopened**; OQ-16/OQ-17 **new** | **rewritten** |
| `NEGATIVE_RESULTS.md` | every recorded negative, with §2a (Stage 3C) new and the conclusion rewritten | **updated** |
| `EXPERIMENTAL_RT_NCRNA_REGISTER.tsv` | 185 rows; now carries exposure class per element | **updated** |
| **`PANEL_LEAKAGE_MAP.tsv`** | **new** — 175 panel elements joined by exact sequence hash to the catalogue, PAIR-ELIG, the X1/X2 folds, Mestre and the CM calls | **new** |
| **`TIER0_REPAIR_TABLE.md`** | **new** — the 8 zero-compute repairs itemised for sign-off, 4 flagged status-changing | **new** |
| `WHAT_IS_A_RETRON.md` | necessary / common / lineage-specific / conventional / experimentally defining | **updated** |
| `PUBLICATION_OPTIONS.md` | A–D re-evaluated, plus **C2** (RT architecture across experimental structures); X2 stated at four levels, never as PASS/FAIL | **rewritten** |
| `MINIMUM_REMAINING_WORK.md` | the programme re-adjudicated | **rewritten** |
| `scripts/` | `build_experimental_register.py`, `build_panel_leakage_map.py` | |

## Evidence sources, pinned

`…_v7` `46414f4` (Stage-2 final report; `human_input_audit` **PENDING**) and `94a1a78` ·
`…_v7-synthesis` `94a1a78` · **`…_v7-embeddings` `4f8550b` results + `fdf0872` closure (governing)** ·
`…_v7-embedding-report` `e3f96b1` ·
**`…_v7-stage3c` `34000ee`** · `…_v7-asset-audit` `67c137b` · `…_v7-dbchar-workbench` `12ea561` ·
`…_v7-mestre-audit` `b05934f` (MCC-v3.1 freeze `e047fdc`) ·
`…_v7-spire-ncrna` `ed4a663e19ca0d6625776bb92b1919b37e47e754`.

## The five things to read first

1. **`TIER0_REPAIR_TABLE.md`** — 8 repairs, none applied; **T0-1, T0-4, T0-5, T0-7 change what may be
   written** and need sign-off. T0-1 is now urgent: Stage 3C has inherited Stage 3B's "PARTIAL".
2. **`PANEL_LEAKAGE_MAP.tsv`** — only **16 of 175** panel elements are fully external. The panel is
   an assay layer, not independent validation, and those 16 are **not** a compatibility/orthogonality
   set: they carry functional measurements, not exchangeability labels. A separate prospective
   analysis could use them for **functional** validation of RT-DNA production or editing predictions
   — a different endpoint.
3. **`PROJECT_EVIDENCE_MAP.md` §2.10** — the four-level reading of X2 (governing source `fdf0872`),
   the substantive change in this revision; and **§2.10a**, which records OpenCRISPR as a
   **methodological precedent, not an experimental result of this project**.
4. **`PROJECT_EVIDENCE_MAP.md` §2.5** — Stage 3C, graded across six distinct vocabularies; no
   universal Region-Y motif and no universal three-domain architecture is claimed.
5. **`OPEN_QUESTIONS.tsv` OQ-16** — X2 trained on every fold, so **no untouched holdout remains
   inside PAIR-ELIG**. A confirmatory population must be declared before any compatibility model.

## Reviewer's bottom line

The project now has a defensible instrument layer, a strong negative layer, **one replicated and
controlled positive result** (RT-conditioned ncRNA likelihood, decomposed into lineage and a small
exact-RT residual) and **one reproducible architectural landmark** (a catalytic centre inside a
single core unit, independently located to within two residues). What failed remains failed:
reproduction of Mestre's classification, placement into the historical clade system, de novo ncRNA
discovery, and held-out catalytic-geometry validation. Recommended sequence: Tier-0 repairs → declare
a confirmatory population → write the resource/annotation-limits paper → the pairing paper at the
four-level claim → the architecture paper from Stage 3C.
