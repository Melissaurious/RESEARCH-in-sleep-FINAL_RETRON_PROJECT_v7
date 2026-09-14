# Stage 11 · Fast but robust assessment of a novel RT

## 0 · The point of this task

Given a new protein, we want to say quickly and defensibly whether it is a reverse
transcriptase, and whether it is a retron. We already have an instrument that does the
first part — it reproduces a published calibration to the decimal and an independent
sequence method recovers its verdict at 78% — but it is **RT-catalytic, not
retron-specific**, and it has never been checked against a genuinely lineage-disjoint
instrument. So today we can assess a novel protein but cannot state the bound on what the
assessment means. Once this lands we have a declared operating point, a known error
profile, and an explicit statement of what the assessment can and cannot claim. That is
also what makes our striking result about published cutoffs reportable rather than merely
provocative.

## 1 · Where this stands — 🟡 the instrument exists and survived attack

**Gate S**, the most-attacked claim in the project:

| | finding |
|---|---|
| `A2` | reproduces its published calibration **96.9 / 8.1 to the decimal**. Four attacks failed |
| `A4` | **threshold-independent** — plateau ≥ 7 Å; `SEQ_SEP` inert |
| `A5` | cluster 170's 0% is **biology, not folding failure** (pLDDT 94.8 at the tetrad) |
| `A7` | tracks global structural separation, **z = 16.69** |
| `A8` | ⭐ **an independent SEQUENCE instrument recovers the verdict at 78%** against a 26.6% base rate |
| `E5` | **predictor-robust** — 18/18 crystals; the structural *tree* numbers are predictor-sensitive and reported at their lower bound |

**And the headline application** — `s5_admission`, which was `PE2`, *"the highest-value
unrun experiment in the project"*:

> **80.7%** of c50 representatives of the rejected 40–160-bit band carry an **intact
> catalytic site** (431 / 534 carrying a tetrad; 71.8% of all 600 drawn) against a matched
> null of **12.2%** — 🔴 **the registered 10–20% prediction is REFUTED, four times over,
> in the optimistic direction.**

It decomposes into two opposite findings: what the criterion discards is **~90%
catalytically intact reverse transcriptases of other families** (which a retron finder is
right to decline), and a **`Retron`-labelled stratum that is only 53.3% intact** — where
the real cost lives.

## 2 · ⚠️ The bound that must travel with every claim

`A11` — **Gate S is RT-catalytic, not retron-specific.** Admitted proteins carry ncRNA at
**33.1%** against canonical **44.8%**. This is registered as a **bound, not a claim**:
**any sentence saying "missed retrons" violates it.**

## 3 · What is left to do

- ⛔ `PE6` — **Pfam PF00078 (RVT_1)**: is the population reverse transcriptase by a
  **lineage-disjoint** instrument? The script is written and will run unchanged
  (`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/reruns/scripts/r3_pf00078_membership.py`); it is **blocked on acquiring
  the profile**. ⚠️ Note the local **InterProScan stub database** (Pfam-A holds 3–4
  profiles) — Pfam-A 37.0 with 21,979 models is on Ibex.
- ⛔ **One `hmmsearch`, still open:** validate the `Retron` label corpus-wide at
  `full_RT ≥ 40 bits`. Debate `D1b` records that this **single run settles two open
  items**, audit `B3` requires it, and it moves **the population under everything**, `B1`
  included.
- ⛔ `A10`'s consequence: since `[YFWH].DD` is **ours** and published tools admit by **HMM
  bit score**, the assessment must be stated in the field's currency, not only in ours.
- **A declared operating point.** Two arms thresholded separately confound information with
  cut — re-score at matched recall before reading any gap.

## 4 · Prerequisites and gates

- **Stage 1** for the population; **stage 4** for the geometry; **stage 2** if the
  assessment reports domain architecture.
- **Stage E (detector evaluation protocol)** — the assessment's error profile is only
  meaningful under a stated held-out design.

## 5 · Traps already paid for

- ⛔ **Match the operating point** before comparing two arms.
- ⛔ **Group-clean is not family-held-out.** A leak-free split still tests only new *groups
  within seen families*, and the cheap check substitutes for the intended one **and
  passes**.
- ⚠️ **Never pick candidates by top-N score** — stratify against the positive
  distribution.
- ⚠️ **Confirm a control could have failed** before trusting it.

---

# 6 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §13

## ⭐⭐ The output classes — adopt these, they solve a real problem

The ideas document rejects a binary filter and proposes graded classes:

    canonical RT          canonical retron RT        divergent / interesting candidate
    probable RT           probable retron RT         fragmentary
                                                     inconsistent
                                                     likely false positive

⭐ **This is the never-delete-always-flag rule applied to triage**, and it fixes something
the project has already been burned by. `A11` bounds Gate S as **RT-catalytic, not
retron-specific** — a binary "is it a retron?" output *cannot* respect that bound, whereas
`canonical RT` / `probable retron RT` can. The class set encodes the instrument's actual
resolution.

⭐ And **`divergent / interesting candidate` is the class the project most needs.**
`s5_admission` found **80.7%** of what a published cutoff rejects carries intact catalytic
geometry — those proteins are exactly this class, and today there is no label for them.
The ideas document's own principle says it: *avoid a strict binary filter that discards
unusual biology.*

⚠️ **`inconsistent` deserves its own home** — it is stage 12's population (tools disagree)
and stage H's (placement moves under perturbation). Route it there rather than discarding
it.

## The check ladder, with what exists

| tier | checks | status here |
|---|---|---|
| **sequence integrity** | ambiguous residues · length · low complexity · internal stops · truncation · contig-edge | ⭐ all from stage 1's carried flags; **contig-edge and prodigal `partial` are already required deliverables** |
| **RT evidence** | family profile match · RT0–RT7 architecture · fingers/palm/thumb completeness · YXDD · catalytic geometry | ⭐ Gate S covers geometry and YXDD; stages 2 and 4 supply the rest; ⛔ profile match blocked by the **InterProScan stub** |
| **family-specific expectations** | expected length range · motif occupancy · domain architecture · indels | ⛔ needs stage 2's per-family occupancy table and **stage I's non-retron reference** for the base rates |
| **retron-specific evidence** | retron-enriched motifs · structural features · phylogenetic placement · embedding similarity | ⚠️ placement needs a tree (a confirmed negative); embeddings exist (`s4l_embed_esm2.py`, `s4n_embed_esmc.py`) |
| **genomic context** | nearby ncRNA · strand consistency · plausible RT–ncRNA distance · accessory proteins · operon structure | ⭐ stage 1's geometry gives the distributions that define "plausible"; ⛔ operon needs stage 7 |

⭐ **The context tier is where this stage becomes cheap:** "plausible RT–ncRNA distance"
is just a quantile of stage 1's geometry distribution. No new instrument needed.

## What must still be built

- **A declared operating point per class**, with the base rate stated. Two arms thresholded
  separately confound information with cut — re-score at matched recall.
- **The base rates**, which require **stage I**. "Probable retron RT" is meaningless without
  knowing how often a non-retron RT scores the same.
- ⚠️ **Do not let the class labels become a filter.** The classes are columns on the frozen
  dataset, not a subset of it.
