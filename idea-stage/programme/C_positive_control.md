# Stage C · Apparatus and positive control
**Proposed addition. Not in the operator's original twelve.**

## 0 · The point of this task

This project currently has **no positive control on its own apparatus** — the one it had
was retired deliberately when the work restarted from raw data. That matters because
several planned stages produce negative results, and a negative from an instrument that
could not have returned anything else is worthless. Right now we cannot demonstrate that
our own pipeline detects a signal we know is present. Once this lands, every negative
claim has something to lean on, and we can show a control that **could have failed**
rather than one that merely passed.

## 1 · Where this stands — 🔴 none exists

`R0` — *"apparatus positive control — 46 records, three instruments agree"* — was
committed at `db3cbee` and **deliberately retired** on 2026-09-05
(`/home/borg/research-wClaude-PART1_v2/docs/decisions/0002-retire-r0.md`). It is recoverable from history but is not carried
forward. The decision record states the consequence plainly:

> ⚠️ **The project currently has no positive control on its apparatus.** R0 was that
> control. Retiring it is a real loss, not a neutral cleanup.
> The first row to make a negative or absence claim must supply its own positive control
> (EVIDENCE_STANDARDS §6). It may not lean on R0.

`ROADMAP.md` rule **RM-5** encodes it: *a row that will produce any count of zero declares
its positive control in its "Declared before the run" block.*

## 2 · Why this is a stage and not a footnote

Three planned stages produce negatives as their primary output:

| stage | the negative |
|---|---|
| **6** | five tree routes fail; the structural route may too |
| **9** | diversity/saturation, currently blocked and likely to return nulls |
| **10** | co-evolution, where the existing null cannot move |

And the project has already been burned by a control that could not fail:

> The tree stage's audit produced **5 refutations in 45 rows because its instruments could
> not have returned another answer.** `D_instrument`'s instruments **can**, and
> demonstrably did — RT1 scatters at 0.75 where RT3/RT5 hold at 1.00; the positional null
> returns a 0.23% background it could have returned at 100%.

## 3 · What must be delivered

- **An apparatus control**: a signal known to be present, recovered end-to-end through the
  current pipeline, on the current substrate.
- **Evidence the control could have failed** — the null's own **sd** (sd = 0 means the row
  carries no information), and an **injected-signal power curve** showing the instrument
  detects a known effect. This is `PE0`, the standing rule.
- **A reusable pattern** so each later row can instantiate its own control cheaply rather
  than inventing one.
- **A statement of what the control does NOT cover**, so it is not over-claimed the way
  `R0` risked being.

## 4 · The standing rule this stage owns (`PE0`)

> No permutation result may be reported without:
> 1. the null's own **standard deviation** — `sd = 0` ⇒ the row carries no information;
> 2. **z**, not the ratio — one case measured the ratio's entire dynamic range as
>    1.00 → 1.28;
> 3. an **injected-association power curve** on the same data and the same blocks, showing
>    the null detects a known non-descent signal.

⭐ This is EVIDENCE_STANDARDS §6 (*"a null for your own criterion"*) applied to the null
itself, and it generalises past this project.

## 5 · Design rules already learned

- **Confirm a control could have failed before trusting it.**
- **Never pick candidates by top-N score** — stratify against the positive distribution.
- **A check is validated only by watching it FAIL on a case it must reject AND accept a
  case it must accept.** Passing on a good case alone proves nothing.
- **Verify foreign artifacts with an instrument sharing no derivation** with the artifact,
  and run an **exonerating** control before writing any defect report about another
  stage's work.

## 6 · Prerequisites

Stage 1, for a substrate whose population can be named. Nothing else.

---

## 7 · ⭐ Two worked examples on disk — declared as gates BEFORE they ran

Found 2026-09-12. These are the best templates in the project for a control that could
fail, and both are structural falsification tests:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21b_truncation_verdict.py
      "FALSIFICATION TEST 1 ... D2.0 declared this test as a GATE: is a structural negative
       at the N-terminus admissible?"
      -> /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d21b_per_chain_nterm.tsv

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21c_sse_agreement.py
      "FALSIFICATION TEST 2: do the two SSE algorithms agree well enough to set edges?"
       DSSP (H-bond energetics) vs P-SEA (CA geometry) -- two independent instruments
      -> /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d21c_edge_disagreement.tsv

**Why they are the right shape:**

1. **Declared as gates in `D2.0_METHOD_LANDSCAPE.md` before running** — not scored after.
2. **Each names what would refute it.** `d21b` asks whether an absence can be believed *at
   all* before any absence is reported; `d21c` requires **two independent algorithms** to
   agree before an edge is set.
3. **Each could have failed, and the project reports where controls did.** `D_instrument`'s
   audit: *"RT1 scatters at 0.75 where RT3/RT5 hold at 1.00; the positional null returns a
   0.23% background it could have returned at 100%."*
4. ⭐ **`d21b` is the template for any absence claim.** Before reporting *"X is absent"*,
   show that the instrument could have seen X had it been there — which is exactly what
   stages 2 (RT0), 6 (tree resolution) and 9 (diversity) each need.

⚠️ **And one counter-example to learn from, in the same tree:** `a2_referee_externality.py`
found that a control's claim to being **external** failed — **42 of 63 "external" producers
were inside the seed** (`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/tables/a2_referee_externality.tsv`).
**A control is not external because it is called external.** Check membership.
