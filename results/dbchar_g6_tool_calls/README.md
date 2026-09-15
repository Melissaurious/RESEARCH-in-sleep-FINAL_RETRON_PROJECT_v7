# dbchar_g6_tool_calls

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 16 landed
tables and `MANIFEST.tsv` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Population: the **Retron locus population** (the `Retron` family
label), with other families reported beside it and never merged in.

---

## 1 · What was measured

### The detection matrix — `g6_tool_matrix_retron.tsv`, `g6_tool_presence_retron.tsv`

663,308 distinct Retron records (632,688 loci):

| tool | records | % of Retron records | loci |
|---|---:|---:|---:|
| myRT | 615,349 | 92.77 | 586,818 |
| PADLOC | 453,476 | 68.37 | 441,061 |
| DefenseFinder | 449,134 | 67.71 | 434,289 |
| **all three** | 352,705 | **53.17** | 345,779 |

Every Retron record carries at least one tool. The seven combinations run from 352,705 records
(all three) down to 8,729 (DefenseFinder alone).

### `system_subtypes` is two tools in one field — and is never pooled

The declared rule (the project's standing known-wrong note): **capital-initial = DefenseFinder,
lowercase = PADLOC**. Applied to the Retron records:

| | records |
|---|---:|
| a DefenseFinder-style subtype | 449,134 |
| a PADLOC-style subtype | 453,476 |
| **both** | 365,708 |
| neither | 126,406 |
| an unclassifiable subtype string | **0** |
| detected by a tool but missing that tool's subtype | **0** for both tools |

The case rule **partitions the field exactly** — zero strings fall outside it, and every record
a tool detected carries that tool's label. Each vocabulary is landed separately
(`g6_subtype_vocabulary_DefenseFinder.tsv`: 15 labels; `..._PADLOC.tsv`: 37 labels).

**Agreement, where both tools wrote a label** (365,708 records): the two strings agree for
**160,381 (43.85%)** after case and punctuation normalisation, and disagree for 205,327. The top
60 disagreeing pairs are landed.

⛔ This agreement is **not** independent corroboration: the two tools share model lineage. The
gate reports the matrix and the disagreement classes and claims neither corroboration nor error.

### The extraction asymmetry — `g6_extraction_asymmetry.tsv`

This is the finding that constrains every other gate:

| detected by | records | **% carrying an ncRNA** | median RT aa |
|---|---:|---:|---:|
| myRT + PADLOC | 61,541 | **89.23** | 319 |
| myRT + PADLOC + DefenseFinder | 352,705 | **70.39** | 315 |
| PADLOC + DefenseFinder | 13,003 | 44.23 | 338 |
| PADLOC alone | 26,227 | 18.63 | 325 |
| myRT + DefenseFinder | 74,697 | 16.97 | 338 |
| DefenseFinder alone | 8,729 | 14.66 | 338 |
| **myRT alone** | 126,406 | **13.50** | 317 |

ncRNA carriage varies **6.6-fold** with the tool combination. A tool-defined subset of this
corpus is therefore **not a random subset**, and any ncRNA rate computed on one inherits that
selection. This is the confounder the prior project named; here it is measured.

**PROPOSED:** the gradient tracks PADLOC's presence, and PADLOC's retron rule is itself
ncRNA-model-driven — so "PADLOC called it" and "an ncRNA was found" are close to the same event.
That reading is the operator's to accept; the measurement stands either way.

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 663,308 distinct Retron records (3,051,238 records tabulated overall)
n_succeeded: all classified into a tool combination and a subtype state
n_dropped: 0

| | n |
|---|---:|
| Retron records with no subtype from either tool | 126,406 |
| records where the two tools disagree on the subtype | 205,327 |
| unclassifiable subtype strings | 0 |
| second-count comparisons / disagreements | 11 / **0** |
| positive controls / failed | 9 / 0; seeded-bad rejected |

## 3 · The denominator's second count (WA-D.3)

`c02_second_count.sh` recounts the seven `detected_by` combinations and the subtype case classes
with awk over the raw `master_Retron` bytes. All 11 comparisons agree exactly — against
`g6_tool_matrix_retron_all_records.tsv`, which is computed over **all** records (including
byte-identical duplicate lines) precisely because that is what awk sees; the deduplicated
figures in §1 are the first-copy counts.

**Positive controls** (9): the case rule must send `Retron_I_A` to DefenseFinder and
`retron_i_a` to PADLOC, must keep both when they co-occur (pooling would lose one), must call a
non-alphabetic first character unclassifiable rather than assigning it to a tool, must not drop
malformed JSON, and the asymmetry measure must move on constructed data.

## 4 · Claims

No claim status proposed. `C7` (supporting): disagreement between annotation routes is
measurable and structured — 43.85% subtype agreement where both tools speak, and a 6.6-fold
spread in ncRNA carriage across tool combinations — while agreement between tools that share
model lineage is not evidence of independent detection.

Prior work (`g6_prior_reconciliation.tsv`): the prior figure of ~44.6% subtype agreement is
**CONFIRMED** at 43.85% (the prior's grain and normalisation are not stated precisely, so the
comparison is a band, not an identity); the "two tools in one field, split by case, never
`groupby`" rule is **CONFIRMED** — zero strings fall outside it; and the caution that tool
agreement is a confounder rather than corroboration is carried forward unchanged.

## 5 · The self-adversarial pass (BS-14)

**1 · Overstated words.** *"detected by"* is what `metadata.detected_by` records, not evidence
that the tool was run and failed elsewhere — a tool missing from a record may mean it was not
run on that genome at all, which this corpus cannot distinguish from a negative call. *"agree"*
means two strings match after normalisation, not that two methods reached the same biological
conclusion. *"asymmetry"* is an association across tool combinations, not a causal claim.

**2 · Alternative explanations.** The ncRNA gradient could be entirely definitional: if PADLOC's
retron rule requires an ncRNA, then "PADLOC called it" and "ncRNA present" are the same event,
and the 89% vs 13% contrast measures a rule, not biology. The corpus carries no per-tool
provenance detail that would separate these, so the gate reports both readings. The 43.85%
agreement could be inflated or deflated by my normalisation choice (case and punctuation
stripped); the raw disagreeing pairs are landed so the choice can be re-examined.

**3 · Could this have returned a negative?** Yes — the case rule could have left unclassifiable
strings (0 did), tools could have been detected without their subtype (0 were), and carriage
could have been flat across combinations (it spans 13.5%–89.2%).

**4 · Unit of every rate.** Records or loci, named per table in `MANIFEST.tsv`.

**5 · Numbers with no producing script.** None in `tables/`. The 6.6-fold figure is the ratio of
two named cells of `g6_extraction_asymmetry.tsv`.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** a first second-count comparison that put first-copy counts against awk's
  all-records counts and disagreed by the duplicate lines. The comparable all-records table is
  now landed beside the deduplicated one.
- **Weakened:** the PADLOC/ncRNA reading, from an explanation to a `PROPOSED:` one.

## 6 · What changed from the plan

Nothing material; the extraction-asymmetry table was extended with RT length and geometry
eligibility so the asymmetry can be checked on more than ncRNA carriage.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g6_tool_calls/run.sh
== c03 self-validation: rejected the seeded-bad case, as required
== c03 positive controls ...  c03: 9 controls, 0 failed
== t01 the per-tool call matrix, subtype vocabularies and the extraction asymmetry
== c02 independent second count (awk over master_Retron)
== c04 reconcile ...          11 rows, 0 DISAGREE; prior 3 rows; agreement 43.8549%
== assemble ...               27 summary rows, 16 tables
  OK × 16 tables, OK MANIFEST.tsv
REPRODUCED: every landed table is byte-identical on rerun.
wall 78.3 s, exit 0
```

## 8 · Derived dataset

`rt_tool_calls_v1.parquet` — 3,051,238 rows, one per distinct raw record, carrying the tool
flags, the tool combination, and each tool's subtype label **kept separate**. Registered with
hashes in `g6_derived_registry.tsv` and `data/README.md`.

## 9 · Acceptance

Open `INPUTS.tsv` and recognise the 2 inputs: `master_Retron_merged_oriented.jsonl` and the g2
record table.
