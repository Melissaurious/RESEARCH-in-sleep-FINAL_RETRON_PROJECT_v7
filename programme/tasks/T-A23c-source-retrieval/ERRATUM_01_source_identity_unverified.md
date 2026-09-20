---
record: T-A23c-ERRATUM-01
task_id: T-A23c-source-retrieval
date: 2026-09-20
kind: ERRATUM — raised by the reconciliation session, not by the executing session
task_state_unchanged: PASS
scope: source identity only. The task's two substantive findings are NOT withdrawn
---

# T-A23c · ERRATUM 01 — four "secondhand primary" sources are not the cited references

**`T-A23c` is not VOID.** It was frozen before execution, its two declared controls passed, its
prohibitions held, and its two substantive findings stand. **What is wrong is the identity of four
of its eight sources**, and one verdict that rests on them.

---

## 1 · The defect

`tables/A23c_sources.tsv` resolves the four references `SIM2019` is counted through:

| source | resolved DOI | resolved title | year |
|---|---|---|---|
| `SIM2019` — the review | `10.1093/nar/gkz865` | Retrons and their applications in genome engineering | **2019** |
| `SIM2019_ref32` | `10.1002/mco2.70758` | msDNA: A "Wake-on Sensor" for Defense Effectors… | **2026** |
| `SIM2019_ref33` | `10.1038/s42003-026-10199-8` | Structural insights into the assembly… Retron Ec78 PtuAB | **2026** |
| `SIM2019_ref35` | `10.7554/elife.99554` | Intracellular expression of a fluorogenic DNA aptamer… | **2026** |
| `SIM2019_ref36` | `10.1093/nar/gkag111` | Structural basis of Retron-Eco8-mediated antiphage defense | **2026** |

**A 2019 review cannot cite four 2026 papers.** All four identifications are wrong.

## 2 · The cause, in the frozen code

`a23c_retrieve.py` L24–49 gives these four sources `"doi": None` and a **descriptive title string
composed for the search**, not a bibliographic title:

```python
{"source_id": "SIM2019_ref32", "role": "secondhand_primary", "doi": None,
 "title": "retron msDNA reverse transcriptase specificity", ...}
```

L148–152 queries `TITLE:"<that string>"`, falls back to unfielded free-text search, and L164 takes:

```python
r = res[0]
```

**The top keyword match, with no assertion that the retrieved record is the cited reference.** The
reference numbers 32/33/35/36 were never resolved against `SIM2019`'s own bibliography, which was
available — the review's full text was successfully retrieved.

## 3 · Why the controls could not catch it

| control | what it asserted | why it passed anyway |
|---|---|---|
| `A23c_POS_known_record` | *a* named, known-indexed article is retrieved with matching title/DOI | it used **`SIM2019` itself**, which carries a DOI. It proves the endpoint is alive; it says nothing about the four DOI-less lookups |
| `A23c_NEG_nonsense_query` | a nonsense query returns zero | it detects an endpoint that returns everything, not a wrong match |

**Neither control asserted identity.** The pair tests liveness in both directions and leaves a
plausible-but-wrong match invisible. This is the programme's standing control failure —
*a control that cannot tell "found the right thing" from "found something"* — in a bibliographic
substrate rather than a computational one.

## 4 · What is corrected

| table | field | correction |
|---|---|---|
| `A23c_sources.tsv` | the four `SIM2019_ref*` rows | `availability` reads `FULLTEXT_OA`; it must read **`MISIDENTIFIED_NOT_THE_CITED_REFERENCE`**. Their DOIs, titles, journals and years describe **different papers** |
| `A23c_uncertainties.tsv` | `U3_secondhand_primaries` | verdict reads `resolvable from retrieved text`; it must read **`NOT RESOLVED — the four references were never identified`** |
| `A23c_uncertainties.tsv` | `U6_direct_noncognate` | `n_candidate_passages = 19`. Only **6** come from `SIM2019`; 13 come from the misidentified papers (`ref36` 5, `ref33` 4, `ref35` 3, `ref32` 1). The defensible passage base for `U6` is **the 6 `SIM2019` passages** |
| `A23c_curation_consequences.tsv` | `uncertainties_resolvable = 3` | becomes **2** (`U5`, `U6`), with `U3` moving to unresolved: **3 unresolved → 4** |

**The tables are not rewritten.** `WORKING_RULES` §7: *no frozen bundle is modified, ever;
corrections are errata.* This file is the erratum.

## 5 · ⛔ What is NOT withdrawn

Both substantive findings rest on `SIM2019`'s **own** full text, retrieved correctly, and both are
quoted verbatim in `A23c_crosspair_passages.tsv`:

> **`U5`** — *"Swapping region Ys between RT-Eco1 (Ec86) and RT-Eco3 (Ec73) produced chimeric
> proteins with 'swapped' msr recognition (32)."*
>
> The region-Y rows describe **engineered chimeric constructs**, not native non-cognate RT–ncRNA
> pairings. This changes what the `T-A23` curation's rows mean.

> **`U6`** — *"These are the only two examples where an RT can function on a non-cognate msr-msd."*
>
> Referring to RT-Vch1 (Vc95) on msr-msd-Vpa3 (Vp96) and RT-Eco4 (Ec83) on msr-msd-Eco7 (Ec78).
> **Two** reported native non-cognate functional examples.

The honest negative also stands: **`BUF2025` is paywalled**, so `U1` and `U2` — which together
carry **42 of the 56** curated rows — cannot be adjudicated from anything retrievable. Recording
that as a finding rather than working around it is what the launcher required.

## 6 · Disposition

- `T-A23c` → `DONE_ERRATUM_REQUIRED`. Outputs are **not consumable**, which was already true (no
  §5 `TASK_REPORT.md`).
- **No row of the `T-A23` curation may be re-attributed on the strength of these four
  identifications.** The operator has independently stated the same constraint.
- Re-resolving refs 32/33/35/36 **from `SIM2019`'s own bibliography** is `T-A23d`'s scope as the
  operator redefined it on 2026-09-20: *explicit primary-reference resolution, not expansion by
  inference.*
- `T-A23d`'s launcher must carry an **identity control**: a retrieved record is accepted only when
  its identifiers match the reference as `SIM2019` lists it. A title match is not an identification.
