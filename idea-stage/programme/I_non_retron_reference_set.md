# Stage I · The non-retron RT reference set
**Proposed addition. From `RETRON_RT_PROJECT_IDEAS.md` §16, where it is flagged as an
"important missing piece". It is, and the project has improvised around it repeatedly.**

## 0 · The point of this task

Every claim that a feature is *retron-specific* needs a non-retron comparison group, and
this project has never built one deliberately — each stage improvised its own, which is
why some of our specificity claims have already died. Without a designed reference set we
cannot distinguish "this is what a retron looks like" from "this is what a reverse
transcriptase looks like". Once this lands we have one declared, frozen non-retron RT set
that every specificity claim in the project uses, so the claims become comparable to each
other. It costs almost nothing to build, because the corpus already contains all 41
non-retron RT families.

## 1 · ⭐ The set does not need acquiring — it needs selecting

The ideas document lists candidate groups (Group II intron, DGR, CRISPR-associated,
Abi-associated, G2L, UG families, other myRT families). **All of them are already in the
corpus**, as 41 of the 42 source JSONL files:

    RVT-GII · RVT-DGRs · RVT-CRISPR · RVT-CRISPR-like · RVT-AbiA · RVT-AbiK · RVT-AbiP2
    RVT-G2L · RVT-G2L4 · RVT-G2Lb · RVT-G2Lc · RVT-UG1 … RVT-UG28b

So this is a **selection and freezing** problem, not a data-gathering one. What is missing
is the *design*: how many per family, matched on what, and frozen where.

## 2 · Why the project needs it — four claims that already turned on it

| | evidence |
|---|---|
| `A11` | ⛔ **Gate S is RT-catalytic, not retron-specific** — admits carry ncRNA at 33.1% vs canonical 44.8%. Registered as a **bound**: any sentence saying "missed retrons" violates it. This bound exists *because* a non-retron comparison was run |
| `x1_neighbourhood` | ⛔ Retrons rank **27th of 41 RT families** on Tier-A defence carriage, with `RVT-UG6` at **96.19%**. The finding was only possible because all 41 families were available — and it **killed** the neighbourhood as an instrument |
| `s5_admission` | ⭐ What a published cutoff discards is **~90% catalytically intact reverse transcriptases of other families** — which a retron finder is *right* to decline. Without the non-retron set this reads as a 80.7% failure rather than as two opposite findings |
| `s4_motifs` | The general/family-specific split (**tetrad position 2 constrained in 40 of 40 families**) is only statable across families |

**The pattern:** every time a non-retron comparison was available, it changed the
conclusion — usually by demoting a "retron-specific" claim to "RT-general".

## 3 · What must be delivered

- **A declared selection rule**: which families, how many per family, and matched on what
  (length? completeness? taxonomy? all three?).
- **Matching, not just sampling.** ⚠️ `x1`'s fold only became interpretable **once
  neighbour count was matched**. An unmatched non-retron set produces a difference that is
  a composition artefact.
- **A frozen, hashed artefact** that every later specificity claim cites by id — so that
  "retron-specific" means the same thing in stages 3, 4, 8, 11 and J.
- **Per-family strata**, not one pooled non-retron blob. ⛔ **A pooled cross-group rate is
  the biggest group's rate** — `PQG[GA]` read 41.78% pooled vs **0.373% median-family**, a
  **112× gap**.
- **A documented negative control within the set** — non-retron families that should behave
  like retrons on a given axis, so the axis can be shown to discriminate.

## 4 · Prerequisites and gates

- **Stage 1**, for the population, completeness flags and the redundancy ladder.
- ⚠️ **`detected_by` is comparable within retrons only** — PADLOC and DefenseFinder were
  extracted **retron-only**, myRT **unfiltered**. So the non-retron set's *annotation* is
  not symmetric with the retron set's, and no cross-family detector comparison may use it.
- ⚠️ **The `Retron` label itself is unvalidated corpus-wide.** One `hmmsearch` at
  `full_RT ≥ 40 bits` settles it (debate `D1b`, audit `B3`) and **moves the population
  under everything** — including which sequences belong in this set. **Do that first.**

## 5 · What it serves

**Stage 3** (which motifs are retron-specific vs RT-general), **stage 4** (is the palm
architecture retron-distinct?), **stage 8** (are these fusions retron-specific or
RT-family-specific?), **stage 11** (the base rate for triage), **stage J** (novelty is
relative to a reference), and **stage E** (the negative set in any evaluation).

## 6 · The framing this unlocks

Half the project's strongest results are of the form *"the thing we thought was
retron-specific is RT-general"*. That is a real contribution, and it is only sayable with
a designed non-retron set. Building it deliberately converts an accidental pattern into a
stated method.
