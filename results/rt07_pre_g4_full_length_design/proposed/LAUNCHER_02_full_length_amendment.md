# PROPOSED launcher amendment — full-length-first

**NOT APPLIED.** The launcher is outside this track's write boundary (§9c) and §9b reserves
changing the scientific question to the operator. This supersedes the amendment proposed in
`results/rt07_pre_g4_scope_separation/proposed/LAUNCHER_02_diff.md`, which the independent
reviewer judged **self-serving as written** — it promoted the one convenient blocked comparator
into derivation and then assigned that gate primary settlement of `C3` and `C9`. Both defects are
corrected below.

---

## EDIT 1 — §5d tier table, narrowed from the previous proposal

The previous version created a broad "may seed 2B" permission. The reviewer was right that this
reads as loosening the rule that was blocking the work. **Narrowed:** the permission is granted to
a *substrate class* defined by a property, not to myRT by name, and it carries an explicit
prohibition on the use that made the earlier version self-serving.

Add one row and one condition; no existing asset changes tier.

| tier | assets | may seed the historical reconstruction (2A) | may seed a broad operational instrument (2B) |
|---|---|---|---|
| **full-length RT reference sequence** *(new)* | any family-labelled collection of **complete, untrimmed** RT proteins — currently only myRT `RTs-collection.faa` qualifies | **NO — never** | **YES**, under §5f |
| published comparators | Toro 2014; Mestre 2020; Toro 2026; myRT `RVT-ref` package; **the myRT `RVT_1` seed fragments** | NO | **NO** |

Note the change of side: the **seed fragments stay comparator-only**. Only the *untrimmed*
collection is admissible, which is the whole point of this amendment and is what the previous
proposal got wrong by treating the two myRT objects alike.

**New §5f — conditions on full-length reference material**

> (a) genealogy against `all167`, `anchors72`, `GOLD171` and `ALIGN_000044` measured and landed
> before use;
> (b) family labels used as **strata only**, never as ground truth — Stage-1's 42 labels are this
> same system's output under a documented collapse (38 one-to-one, 7 fine-to-coarse, 1 rename);
> (c) it never seeds 2A;
> (d) **no reference protein is trimmed to an inherited core window before homologous
> relationships have been inferred**; every coordinate transform stays reversible and both
> `full_sequence_coordinates` and `operational_core_coordinates` are retained;
> (e) whole families **and whole lineages** are withheld for transfer evaluation, named before
> derivation;
> (f) the panel is balanced **hierarchically — lineage first, family second**. A per-label cap is
> forbidden: measured on this collection it yields **73–77% UG and 3–4% retron**.

## EDIT 2 — §7 gate table

Replace `rt07_g4_operational_boundary_model` with two `FULL` gates.

> **`rt07_g4a_reference_design`** — the measured composition of a broad full-length RT reference
> panel: per-family eligible depth, redundancy, length and extension distributions, per-family
> anchor occupancy, and the named withheld families and lineages. Settles `C3` supporting.
>
> **`rt07_g4b_core_coordinate_mapping`** — anchor recovery, ordering, correspondence stability and
> transfer to withheld families and lineages for a broad-RT homologous core coordinate mapper
> derived from complete proteins, with inter-anchor spacing and terminal extensions retained as
> architecture and the historical RT0–RT7 crosswalk applied over frozen output. Settles `C3`
> supporting.

**`C9` is not assigned to either gate.** The RT-subdomain leg of `C9` is `UNESTABLISHED`
(`docs/decisions/2026-09-16_stage2_scope_separation_errata.md` §2), and renaming outputs as
coordinates does not make boundary delimitation measurable. This corrects the previous proposal's
`C9`-primary assignment, which the reviewer flagged.

## EDIT 3 — §4 inputs and trust grades

Register, with grades, the objects actually used: `RTs-collection.faa` (2,339 records, 2,166
eligible) `RE-DERIVE`; the 45 seed FASTAs (1,988 / 1,986 unique) `RE-DERIVE`, **comparator only**;
the 46 `.sto` alignments carrying `#=GC RF` `RE-DERIVE`; `RVT-All.hmm` (45 models, `NSEQ` 1,988)
`RE-DERIVE`; `buildRVT.sh` `FROZEN` as a provenance document; `cdd-pfamA` (contains `RVT_1`)
`RE-DERIVE`; the 39 local RT structures `RE-DERIVE`.

Add to §5b known-wrong: `RVT-CRISPR-like` is absent from `RVT-All.hmm` while Stage-1 carries it
(**3,168** in the source-file view, **3,156** in the single-family analytical view — the view must
be named); and **153 of 1,988 seeds have no full-length parent in the shipped collection**,
concentrated in AbiP2 (35 of 43), UG24 (9 of 11) and AbiK (7 of 12).

## EDIT 4 — §1 success criterion 2

> an operational **coordinate mapper** exists that emits, per (exact RT, anchor), a located
> position and support, and per interval a call state and a stability interval; it is derived on a
> **declared broad panel of complete untrimmed RT proteins whose lineage composition is landed
> before derivation**, and is evaluated on **withheld families and withheld lineages** and by
> identity distance. Region count is never fixed in advance. `BOUNDARY_ACCURACY` and
> `BOUNDARY_CALIBRATION` are `UNESTABLISHED`. Failure to transfer to a family or lineage is a
> result.

## EDIT 5 — §7c deliverables, and §5/§6 downstream — the gap the reviewer named

The previous proposal amended `g4` only and left `g5`/`g6`/§7a/§7c carrying "phylogeny-ready",
missing-block and exact-edge language intact. Also required:

- §7c: "phylogeny-ready core substrate" → "**candidate** core substrate";
  `boundary_uncertainty.tsv` → `coordinate_stability_intervals.tsv`;
  `family_holdout_or_transferability.tsv` → `family_and_lineage_transfer.tsv`.
- §7a: rename `NOT_DETECTED_INSPECTABLE` → **`NOT_CALLED_ON_COMPLETE_SEQUENCE`**, which does not
  imply demonstrated class-specific sensitivity.
- `g6`: replace "missing-block combination" and per-region start/end/length with **inter-anchor
  spacing, terminal extension length and call-state combination**. `g6`'s current deliverables
  presume the region edges `V13` declares unestablished.
- `g5`: retain, but its per-region start/end columns become anchor positions plus interval
  stability.
