# Stage A · Delimitation as a measurable property
**Proposed addition. Not in the operator's original twelve.**

## 0 · The point of this task

Two completely independent instruments in this project find the right molecule and draw
the wrong boundary around it: CMfinder puts a motif *on* the true msr-msd at **12 of 17
loci (70.6%)** while covering only about **24%** of it, and the V5 ncRNA detector shows the
same split in a different apparatus. **Detection works; delimitation does not** — and this
was invisible until two separate stages were read side by side, so it is currently nobody's
problem. Once this lands we have a shared way to measure boundary accuracy *separately
from* detection accuracy, and an answer to whether the failure is one problem or three.
It is the project's actual open question, and it is cheaper than either instrument was.

## 1 · The evidence that it is one problem, not two

| stage | what it found |
|---|---|
| `denovo_family` | ⛔ positive control **6/17 = 35.3%** against a ≥50% bar, both configurations. ⭐ But: **localises at 12/17 (70.6%), covers ~24%** (`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/denovo_family/tables/d07_localisation_secondary.tsv`) |
| `extraction_first` | ⭐ *"given a locus the model localises; given a genome it does not rank"* (`FINDINGS.md` F11). ⛔ Cross-locus specificity **FAILS** — a call is a within-window statement only |

> **CMfinder finds the right molecule and draws the wrong boundary around it. The same
> split appears in `extraction_first` — both instruments localise and neither delimits.**

## 2 · It wears three hats inside the operator's own list

| stage | the boundary in question |
|---|---|
| **4** | where the **palm** ends, and whether YXDD is inside it |
| **7** | where the **operon** ends |
| **10** | where the **msr-msd** begins and ends |

Treating these as three unrelated stages hides the fact that the same evaluation applies
to all of them: *did the instrument find the object, and did it draw the right edge?*

## 3 · What must be delivered

- **A boundary metric reported separately from a detection metric.** Localisation rate and
  coverage fraction are two numbers, and the existing work already proves they dissociate.
- **A positive control for delimitation specifically** — a set where the true boundary is
  known, so that "wrong edge" can be measured rather than inferred.
- **A statement of whether the three delimitation problems share a cause.** If they do,
  one method serves all three; if not, that is also a result.
- The `-combine` / `try_merge` path in CMfinder is where the existing recommendation says
  to start.

## 4 · Prerequisites and gates

| gate | status |
|---|---|
| ⛔ **Do not run clade 4 de novo while the positive control fails** | `denovo_family` PREREG §7 branch 1 and its launcher §3 both forbid it — a null on clade 4 would measure the instrument, not the biology |
| ⭐ **The substrate is built and one command away** | 23 loci, 70 regions, 700 shuffles, 70 length-matched non-retron flanks |
| ⛔ **Stage C, a positive control** | this stage *is* largely a control-design problem |

## 5 · Why it is ranked so highly in the record

The handoff from 2026-09-01 lists the three things a successor could do, and ranks this
second of three:

> ⭐ **Delimitation, as its own stage with its own pre-registration.** Two independent
> instruments localise and neither delimits — that is the project's actual open problem,
> and neither stage could see it alone.

## 6 · Foreclosed nearby — do not confuse with this

⛔ **A better extractor.** `extraction_first` F9 caps the prize at **6 of 45** misses; the
detector loses 36. ⛔ **A new detector architecture** — foreclosed by V5's X164.
Delimitation is neither of those.
