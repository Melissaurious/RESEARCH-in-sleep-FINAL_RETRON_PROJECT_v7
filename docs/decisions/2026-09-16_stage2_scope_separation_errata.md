# DECISION — Scope-separation review outcome: FAIL/BLOCK, verified errata, and three forks returned to the operator

Date: 2026-09-16 · Track: `rt07` · Status: **stopped; returned to the operator**

**Corrects** `docs/decisions/2026-09-16_stage2_scope_separation.md` and the tables in
`results/rt07_pre_g4_scope_separation/`. Those artifacts are left **byte-unchanged** — their
hashes are recorded in `review-stage/DESIGN_REVIEW_REQUEST_scope_separation.md` and they are the
reviewed object. Corrections land here, visibly, never by rewriting.

Supersede this record by a new record, never by rewriting it.

    REVIEW_SCORE: 4        REVIEW_VERDICT: FAIL/BLOCK
    review_gate.py -> {"decision": "continue", "reason": "positive threshold not met"}

**NO g4 DETECTOR EXECUTED; NO g5 CATALOGUE APPLICATION STARTED.**

---

## 1 · Why this session stopped

The operator's instruction: *"Do not start another design round beyond the independent review. If
the reviewer identifies another fundamental scientific fork, stop and return it to the operator."*

The reviewer named **three** fundamental forks (§4). This session stops.

This is the third consecutive design failure — 3/10, 4/10, 4/10 — and the pattern is now itself
evidence. Each round repaired what the previous reviewer named and was defeated by something
structurally deeper: first identifiability, then substrate, now reference composition and the
legitimacy of amending the rule that was blocking the work. A fourth round written under the same
standing assumptions would very likely fail the same way.

## 2 · Errors in the landed artifacts — refuted by the reviewer, re-verified here

Every one was re-measured from source in this session. **The reviewer was correct on all six.**
Both values are shown; the superseded value stays visible.

| # | as landed | verified correct | how it happened |
|---|---|---|---|
| E1 | ALIGN_000044 ungapped lengths **"599–687 aa (full length)"** | **375–1,064 aa**, median 610 | generalised from the handful of rows visible in a terminal, never measured |
| E2 | 11 myRT seeds contained in ALIGN_000044 **"from 10 of the 66"** | **11 distinct records**, and all 11 lie in the **bacterial** lineage group | the distinct-target count was never computed; the "10" was invented |
| E3 | ALIGN_000044 ∩ RTs-collection **"10 exact sequence overlap"** | **4 raw-exact**; 10 only after stripping a trailing `*` on the collection side | the normalisation was applied in code and never disclosed in the table |
| E4 | the 17 `all167` containments, **10 families summing to 16** | **17 across 11 families**; the omitted one is `RVT-UG11`: 1 | a `most_common(10)` truncation transcribed as if complete |
| E5 | `RTs-collection.faa` is **"full-length"** | **50–1,879 aa**, median 461; **26 below 250 aa, 103 below 300** | asserted from the per-family medians without checking the distribution |
| E6 | **"no myRT-derived substrate can address RT0, ever"** | true of the RVT_1 **seed fragments**; **false** for the unexcised collection proteins | an over-general quantifier on a claim that held only for the seeds |

**E6 matters most, and it cuts in the design's favour.** `RTs-collection.faa` holds unexcised
proteins that *can* inspect N-termini. The corrected statement: *no myRT **seed**-derived
substrate can address RT0, because the RVT_1 excision removed it; the full-length collection
retains the region, though RT0 still cannot be established without a non-LTR comparator — of
which there are **zero** local structures.*

### One claim withdrawn as unverifiable

That all 1,988 seeds are RVT_1 excisions. `buildRVT.sh` is a **commented recipe, not a build
manifest**, and only **1,835/1,988** are substrings of the shipped collection. The "version
drift" explanation for the remaining **153** was asserted without evidence and is withdrawn.

### A view name that must be carried

`RVT-CRISPR-like` is **3,168** exact RTs in the source-file view and **3,156** in the
single-family analytical view. Both are correct; neither may be quoted without its view.

## 3 · The design flaw this session did not catch

**The per-label cap in `candidate_reference_design.tsv` would have produced a UG-dominated
panel** — the opposite of its stated purpose. Measured on the 2,202 labelled collection records:
29 UG labels carry 872 sequences against **one** pooled `GII` (503), **one** `DGRs` (502),
**one** `CRISPR` (130), **one** `Retrons` (96).

| cap | panel n | UG | Retron |
|---|---|---|---|
| 20 | 616 | **77%** | 3% |
| 30 | 784 | **75%** | 4% |
| 40 | 918 | **73%** | 4% |

The rule would have reduced the project's primary biological target to 3–4% of its own reference
panel. Balancing must be **hierarchical** — major lineage first, family second — never per-label.
`RULE-2` of that table ("diversity is not abundance") was right in principle and its
implementation did the opposite.

## 4 · The three forks, returned

**Fork 1 — Is Stage 2 closed at 2A, or authorized as a new methods study?**
The reviewer: amending §5d is *"legitimate only as authorization for a new operational-reference
study, not as reinterpretation of the historical reconstruction ... currently self-serving because
it promotes the sole convenient blocked comparator into derivation, recommends that fork by
default, and then assigns g4b primary settlement of C3 and C9."* That criticism is accepted. If
2B proceeds it must be declared a **myRT/Pfam-conditioned coordinate methods study** with its own
question — not as reconstruction of RT0–RT7, and not settling `C3`/`C9` primary.
**Reviewer's recommendation: close at 2A until the repairs exist.**

**Fork 2 — What is 2B's reference universe?** Bacterial myRT/Pfam diversity, or the broader RT
superfamily including non-LTR and telomerase? These are different universes and cannot share an
unqualified "general RT" claim. Locally there are **zero** non-LTR and **zero** telomerase
structures, and the inventory missed at least two sequence resources (a UG/Abi 42-group /
9,141-RT reference set, and Silas 2017's 266 RT-Cas loci) that must be registered before any
breadth claim.

**Fork 3 — Is a callability-only coordinate projection worth the compute?** It cannot be promoted
to biological occupancy, absence, boundary accuracy, `C9` settlement or phylogenetic eligibility.
If the answer is no, Stage 2 closes at 2A.

## 5 · What survives all three reviews

- **`BOUNDARY_ACCURACY` and `BOUNDARY_CALIBRATION` are `UNESTABLISHED`**, endorsed each time.
- **Biological absence (`E08`) stays `UNESTABLISHED`** — the five-condition chain is insufficient,
  and `NOT_DETECTED_INSPECTABLE` should be renamed to something that does not imply demonstrated
  class-specific sensitivity, e.g. `NOT_CALLED_ON_COMPLETE_SEQUENCE`.
- **No RT0 occupancy**; no forced seven regions; no tuning to rescue RT1.
- **The historical/operational separation is real, not cosmetic** — confirmed by the reviewer.
  `ALIGN_000044` is the right substrate for 2A and the wrong one for 2B.
- **The confirmed measurements**: 66 records / 65 unique, all group II intron ORFs; 45 models with
  `NSEQ` 1,988 and zero model/FASTA mismatches; containment 17 / 13 / 11 with all GOLD hits retron
  and all ALIGN hits GII; zero cross-family duplicates; LtrA seed span 90–360; zero non-LTR and
  zero telomerase structures; 21 of 38 families without a structural anchor.
- **myRT's role assignment**: valid derivation material, invalid family-label validation.

## 6 · Repairs required before any 2B design is rewritten

Not attempted here. Recorded so they are not rediscovered: hierarchical lineage-then-family
balancing; reconcile the 45 / 38 / 42 label vocabularies and resolve `RVT-CRISPR-like`;
investigate the 153 unmatched seeds; per-sequence full-length eligibility instead of a blanket
label; register the missing UG/Abi and RT-Cas resources; restrict `g4b` estimands to projection,
callability, reproducibility, ordering-where-not-enforced and inter-anchor spacing; amend `g5`,
`g6`, §7a and §7c rather than `g4` alone; drop the `C9`-primary assignment; and make the artifact
reproducible with `run.sh`, scripts and a complete `INPUTS.tsv` — its absence is precisely what
let E1–E6 through.
