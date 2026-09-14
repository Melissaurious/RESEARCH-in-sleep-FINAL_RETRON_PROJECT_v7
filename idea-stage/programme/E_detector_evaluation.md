# Stage E · Detector evaluation protocol
**Proposed addition. Distinct from stages 11 and 12: about how you evaluate, not what you detect.**

## 0 · The point of this task

No published retron detection method has ever been evaluated on held-out families, so our
own detection numbers have nothing legitimate to be compared against. Worse, our
evaluation uses a **harder** negative set than any published method, which makes a bare
side-by-side comparison actively misleading in our favour. And the cheap leak check we run
tests only new *groups within families we have already seen*, while passing as though it
tested more. Once this lands we have an evaluation protocol that states exactly what it
holds out and why, plus a defensible published position on why our numbers cannot be
placed next to the field's.

## 1 · Where this stands

`lit_detector_audit` (2026-08-26) answered the framing question already:

> **Our 0/9 is unmeasurable against the detection literature, and *typical* against the
> adjacent literature that has actually run the test.** Not one of the six published
> detection-in-genomic-context methods in the table has **ever** been evaluated on
> held-out families, so there is no detection number our 0/9 can be anomalous or typical
> *relative to*.

⭐ **In RNA secondary structure prediction — where the identical protocol has been standard
since 2022 — the canonical result has our exact shape:** a model beats the thermodynamic
baseline under k-fold and falls **below** it on family-held-out data.

Evidence: `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/lit_detector_audit/VERDICT.md`, `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/lit_detector_audit/EVALUATION_TABLE.tsv`
(md5 `51b01e6208a5068245103657ca7c06dd`), `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/lit_detector_audit/tables/s2_L1_power_check.tsv`.

## 2 · ⛔ The traps this stage exists to close

| trap | detail |
|---|---|
| **Group-clean is not family-held-out** | a leak-free split still tests only new **groups within seen families**; the cheap check substitutes for the intended one **and passes** |
| **`fold_group` is the window** | in `V4/cache/v4inputs/TRAIN_IDS.tsv`, `fold_group` is literally `"WIN:" + window_sha1`, so the fatal leak assertion *"no `window_sha1` appears in more than one `fold_group`"* is **true by construction** and verifies nothing. The real leak runs the other way: a **window spanning more than one cluster**. Published baseline **4** is stale — it is **8** on the live table, and **18** with the excluded rows |
| **Harder negatives are not better numbers** | our 0.99 uses a harder negative than any published detector, so **never place the bare numbers side by side** |
| **Training-set contamination** | **77 of 172** published molecules **are** training positives (`extraction_first` `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/extraction_first/tables/e4a_leak.tsv`) |
| **No falsifiable metric** | CMfinder's own `Y/y/?/n/N` scoring has **no falsifiable metric** (`lit_detector_audit/FINDINGS.md`) |
| **Within-window ≠ genome-wide** | cross-locus specificity **FAILS**: a call is a within-window statement only. ⛔ **No fold-change between within-locus and pool-ranking may be computed** until a matched operating point exists |

## 3 · What must be delivered

- **A stated held-out design** — what is held out (family? clade? window? cluster?), why,
  and what the design does *not* control for.
- **A leak assertion that can actually fail**, replacing the vacuous one, measuring windows
  that span more than one cluster.
- **A matched operating point** before any two arms are compared — thresholding two arms
  separately confounds information with cut.
- **A comparability statement for publication**: why our numbers and the field's are not
  on the same axis, and what would have to change for them to be.
- **A positive control** (stage C) — and note `PE0`: report the null's sd, z, and a power
  curve.

## 4 · Prerequisites and gates

- **Stage C**, the positive control: an evaluation protocol with no control validates
  nothing.
- **Stage 1**, for a population whose families can be held out.

## 5 · What it serves

**Stage 11** (the novel-RT assessment's error profile is only meaningful under a stated
design), **stage 12** (the field's non-evaluation *is* the disagreement argument), and
**stage A** (delimitation needs its own metric, separate from detection).

## 6 · Foreclosed nearby

⛔ **A new detector architecture** — foreclosed by V5's X164. ⛔ **A better extractor** —
capped at **6 of 45**. This stage improves the *measurement*, not the detector.

---

# 7 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §6

## ⭐ The held-out ladder — this is exactly the missing design

The ideas document specifies the validation design this stage exists to supply, and it is
the right one:

    leave-one-family-out
    leave-one-clade-out
    leave-one-genus-out
    leave-one-phylum-out

with the explicit instruction: **"avoid relying only on random train/test splits."**

⭐ **This is precisely the trap already on record.** *"Group-clean is not
family-held-out"* — a leak-free split still tests only new **groups within seen
families**, and the cheap check substitutes for the intended one **and passes**. The ladder
turns the leak question into an axis: report performance at every rung and let the drop
show where generalisation ends.

⭐ And it aligns with the field precedent `lit_detector_audit` found: in RNA secondary
structure prediction, where family-held-out has been standard since 2022, the canonical
result is a model that **beats the thermodynamic baseline under k-fold and falls below it
on family-held-out data**. The ladder is what makes that shape visible instead of hidden.

⚠️ **The rungs are not independent here.** `full_lineage` is two schemas — gtdb 7-field,
ncbi 3-field with **no phylum**, ~61% of rows — so **leave-one-phylum-out is not
computable for the majority of the corpus** until the stage F metadata join is done.
Declare that limit rather than silently running the rung on a subset.

## What the ladder must be applied to

The ideas document's validation targets: **known retrons vs known non-retrons** (⛔ needs
**stage I**) · **unseen RT families** · **unseen retron clades** · **highly divergent
candidate sequences** (⭐ `s5_admission`'s rejected band is a ready-made set of these —
80.7% carry intact catalytic geometry).

## The open question this stage should answer

> *"Can a small number of interpretable features identify retron-like RTs without simply
> learning phylogeny?"*

⚠️ **`polythetic` already returned a pre-registered negative on the nearest version of
this**: coverage reached 60.26% but beat a shuffled axis in **0 of 24 cells**, and every
real axis fell **below** chance — the axes group what sequence already groups. So the
honest form of the question is not *can we find such features* but **how much of any
feature set's performance is phylogeny** — which is stage D's machinery applied to a
classifier. Design it that way from the start.
