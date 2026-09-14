# Stage G · Reproducibility packaging
**Proposed addition, smaller scope. `PE9` + debate `D7` in the existing record.**

## 0 · The point of this task

Several analyses in this project printed their results to a console and never wrote a
table — six of them for the central instrument. A reviewer checking data availability
would find that in minutes, and we cannot currently hand anyone the artefact behind some of
our own published numbers. Once this lands, every reported figure has a file behind it and
the project survives the data-availability check that journals now run as standard. It is
one `to_csv` per script, and it is the cheapest credibility this project can buy.

## 1 · Where this stands

- ⛔ `PE9` — *"the eight `to_csv` calls"*, marked **bookkeeping, and BLOCKING**. Six of the
  eight are **Gate S**, the project's most-attacked and most-defended instrument.
- 🔴 `B1` (audit) — one of the **four blocking items**, all cheap and all still open:
  *"artefacts for the ~8 print-only scripts (six are Gate S) — one `to_csv` each — if it
  fails, a data-availability reviewer finds it in minutes."*
- ⚠️ Debate `D7` — *"How much reproducibility debt ships with the paper?"* — still open.
- ⚠️ On record as a rule: **a superlative read off a console excerpt is unfalsifiable.** A
  display filter once hid **all seven counter-examples** and the producing script wrote no
  table at all.

## 2 · The other three blocking items, for context

| item | cost | if it fails |
|---|---|---|
| validate the `Retron` label corpus-wide (`full_RT ≥ 40 bits`) | **one `hmmsearch`** | the population under **everything** moves, `B1` included |
| re-run concordance with `REGIONX = NA..H` | **minutes** | nothing — it **strengthens** the result (0.511 → 0.588) |
| a **relatedness-preserving null** for the concordance | a day | 🔴 `B1` collapses and Part II is gone |
| artefacts for the print-only scripts | **one `to_csv` each** | a reviewer finds it in minutes |

Three of the four are hours or less. All four are still open.

## 3 · What must be delivered

- **A table behind every reported number.** Identify the print-only scripts, add the
  write, re-run, and hash the output.
- **A claim → artefact index.** Every claim in the paper points at a file. This is what
  `BUNDLE_SPEC` BS-7 requires: *nothing enters `paper/` without a bundle id.*
- **A data-availability statement** that is true: what is deposited, what is derivable, and
  what is too large to deposit with the command that regenerates it.
- **The reproducibility debt, stated** — `D7`'s question answered with a list rather than a
  feeling.

## 4 · How the new repo already solves this going forward

`research-wClaude-PART1_v2` makes this structural rather than remedial:

- **WA-B.1** — a number enters the repository **only** inside `results/<ROW>/`, with its
  script verbatim, inputs hashed, environment locked by content, seed declared, command
  recorded, and the agreements revision it ran under.
- **WA-R.5** — *a stage that produces no provenanced artifact has produced no result.*
- **BS-5** — counts are reported so defects are visible: n attempted, n succeeded, n
  dropped and why. **Never footnote a failure.**
- **WA-B.2** — a row is done when `run.sh` **reruns and reproduces** the number. A
  validator passing is not verification.

So this stage is **retrospective only**: it packages the V3/V4/V5 debt. Anything produced
in the new repo is packaged by construction.

## 5 · Prerequisites

None. It can run at any time, and it is the one stage that gets **harder** the longer it
waits — the scripts and their environments drift.
