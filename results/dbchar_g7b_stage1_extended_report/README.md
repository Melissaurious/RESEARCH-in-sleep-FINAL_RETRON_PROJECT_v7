# dbchar_g7b_stage1_extended_report

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 112 landed
tables, all 68 figure files, `REPORT.html` and `REPORT.md` byte for byte (BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** as a reporting product, but it is **not a measurement gate**: it is the extended
scientific synthesis over the seven landed Stage-1 gates and the registered canonical datasets,
requested as a second, richer reporting layer beside the closeout report.

`results/dbchar_g7_stage1_report/` remains the authoritative Stage-1 closeout and validation
report. **Nothing in g1–g7 was modified.** No claim status is proposed.

Plan, written before any analysis ran: `FIGURE_AND_ANALYSIS_PLAN.md` (landed here).

---

## 1 · What was measured

**No new measurement of record.** Every number in the report is a *view* over landed Stage-1
data:

- the 14 registered derived datasets in `data/derived/` (produced by g2/g2b/g3/g4/g6),
- 25 landed tables of g2, g2b, g3, g4, g5 and g6,
- two registered reference resources read as *context, not measurement*: PADLOC's 18 `retron_*`
  rule files and its CM metadata.

Raw JSONL was never opened. The one declared data gap is §11's prevalence denominator: no landed
table carries *sampled genomes per taxon*, so two columns of the GTDB bacterial catalogue that g5
already hashed and joined are read to supply it. That gap was declared in the plan before the
analysis ran.

### How a number gets into the report

The same resolver contract as g7: `findings.py` declares **153** named values, each a four-tuple
(landed table of **this** bundle, exact row selector, column, format). A selector matching zero or
several rows fails the build; a `{placeholder}` with no declared lookup fails the build; a stray
`{...}` surviving into the finished HTML fails the build. Every resolved value is landed in
`tables/g7b_resolved_values.tsv` with its raw and rendered form.

Analysis scripts write tables; figure scripts read `tables/` **and nothing else** (asserted by a
grep guard in `run.sh`); the assembler computes nothing.

| | |
|---|---:|
| sections | 13 |
| figures (PNG + SVG, each with its data TSV) | **34** |
| landed tables | **112** (77 analysis/check tables + 34 figure data tables + the resolver trace) |
| declared values resolved into the prose | 153 |
| landed Stage-1 tables read as hashed inputs | 25 |
| registered derived datasets read | 14 |
| files hashed in `INPUTS.tsv` | 58 |

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 34 figures, 112 tables, 153 value lookups, 294 reconciliation comparisons
n_succeeded: 34 / 112 / 153 / 294
n_dropped: 0

| | n |
|---|---:|
| re-derived quantities compared against a landed g1–g6 value | **294** |
| of those, DISAGREE | **0** |
| declared *definition differences* landed instead of forced agreement | 2 (`t42`) |
| independent intervening-CDS recount, placements compared / agreeing | 5,000 / **5,000 (100%)** |
| positive controls / failed | 20 / 0; the seeded-bad run is rejected, as required |
| figures with no landed TSV beside them | **0** |
| figures whose script reads anything outside `tables/` | **0** |
| unresolved placeholders in the HTML | **0** |
| rates landed without a unit and denominator | **0** (enforced by `write_table`) |
| Wilson intervals that do not contain their point estimate | **0** |
| **defects this bundle found in its own first draft** | **3** (§6) |

The ugly numbers are in the report, not hidden: 47.24% of Retron loci carry no ncRNA call;
the technical clipped mode contributes 5,234 placements that are excluded from every biological
reading; 16,752 records keep a sequence with no defensible genomic context; 669 are ill-posed;
and 34.4% of canonical placements fall in a configuration that turns out to be one *Salmonella*
protein re-deposited (§5 of the report).

## 3 · The denominator's second count (WA-D.3)

This bundle's job is to not change a Stage-1 number, so its "second count" is a **reconciliation
against the landed gates**, and it is a build-stopping check:

- `c01_reconcile.py` re-derives 294 quantities **from the derived parquet datasets** — never from
  the landed TSV it compares against — covering the unit ladder, the per-database and per-family
  ladders, CANONICAL placement counts by direction / CDS-between / strand, the zero-call class,
  the exact-pair view and its topology, the 266 candidates, the MULTI HMM margins, the per-family
  and per-model length baselines, the g2b recovery classes, the g6 tool matrix and carriage, and
  the per-database genome counts. **294 rows, 0 DISAGREE.** A single disagreement exits non-zero
  and the report is not built.
- `c02_independent_cds_between.py` recomputes `n_cds_between` and the CDS-overlap flags for a
  seeded sample of 5,000 CANONICAL placements straight from `rt_window_cds_v1`, with an
  interval-array implementation sharing no code with `g3lib.cds_between`: **100% agreement**.
- `c03_controls.py` checks 20 declared expectations (below), and `run.sh` first runs it with
  `--seed-bad` and aborts unless it **fails**.

**Positive controls (20).** The Wilson estimator against published interval values; the declared
mode-counting rule returning 2 on a constructed bimodal sample and 1 on a unimodal one; six
partition checks (configuration classes, database-membership classes, tool combinations at two
units, inspectability tiers, zero-call classes) each summing exactly to its population; the unit
funnel monotone with every step's removal reconciling; every landed Wilson interval containing
its point estimate inside [0,100]; the GTDB phylum rows summing to the catalogue and to the
corpus; and a rate that *can* move (the upstream-context gradient spans >20 points).

**An independent second implementation (Codex).** Four headline numbers were re-computed by a
separate coding agent (Codex, `gpt-5.2-codex`, read-only sandbox), told to write its own code from
scratch against the same parquet files and explicitly not to read this bundle's scripts. All four
agree exactly with the landed tables:

| quantity | landed here | Codex, independently |
|---|---:|---:|
| canonical upstream placements, 0 CDS, ≤500 bp / >500 bp | 193,375 / 118,275 | 193,375 / 118,275 |
| the same two classes as distinct exact pairs | 23,516 / 1,908 | 23,516 / 1,908 |
| 900–1,100 bp band: placements / distinct exact RTs / top RT's share | 127,078 / 1,938 / 102,853 | 127,078 / 1,938 / 102,853 |
| myRT+PADLOC physical loci, and % carrying a canonical ncRNA | 48,454 / 89.21% | 48,454 / 89.2145% |

This is an independent reproduction of the arithmetic, not of the biology: it shares the same
input datasets and the same definitions, so it tests the implementation, not the conventions.

**The control that fired.** The first Wilson control asserted the wrong published values
(0.3983/0.6017 for 50/100). The estimator was right and my expectation was wrong — Newcombe's
worked value is 0.4038/0.5962. The control caught it, the expectation was corrected, and the
episode is recorded here rather than silently fixed.

## 4 · Claims

**No claim status is proposed, and none may be.** The launcher reserves promotion of an
interpretation to a thesis/paper claim for the operator, and `human_input_audit` is PENDING for
all eight Stage-1 bundles. This bundle carries evidence attributed to the gate that measured it
and adds interpretation marked `PROPOSED:`.

Where the report contributes to the standing claim ledger it is as *supporting evidence already
landed by g2/g3/g5/g6*, re-expressed at explicit units: C1/C2 (the unit ladder and the family
share shift), C5 (the RT↔ncRNA geometry), C7 (tool-route disagreement), C8 (redundancy correction
of taxonomic representation).

## 5 · What the report found that Stage 1 had not stated

Five results are new as *statements*, all from landed Stage-1 data:

1. **The 94.5%-upstream prior has two modes, and the second is one protein.** 34.4% of canonical
   placements sit upstream across a long empty intergenic gap; the 900–1,100 bp band holds 127,078
   placements but only 1,938 distinct exact RTs, 102,853 of them from a single protein in
   *Salmonella enterica*. At the exact-pair unit the configuration collapses from 118,275 to 1,908.
   The adjacent-upstream architecture is the one that survives every change of unit.
2. **Most of the Retron zero-ncRNA class is missing upstream context.** Carriage runs from 0.78%
   at loci with no upstream window to 60.5% at loci with >9 kb of unclipped upstream context.
   The 47.24% zero rate is an upper bound on missingness, not an absence measurement.
3. **Part of the carriage gradient is written in PADLOC's rule files.** The ncRNA is a scoring
   element in 17 of 18 retron rules, is required in practice for `retron_Ec107-like` and
   `retron_outgroup`, and is **prohibited** for `retron_XII` — whose 0.006% carriage over 16,730
   loci the old report called a confirmed CM-model gap. Holding the subtype fixed, however,
   carriage still moves with the tool combination, so composition does not explain all of it.
4. **Recurrent proteins keep their ncRNA partner.** Among exact RTs at ≥100 physical loci, 87.8%
   carry the same dominant exact ncRNA partner at ≥90% of their loci and 100% use a single
   covariance model — while most pair recurrence is re-deposition, so the cross-species pairs are
   the ones worth a co-evolution question.
5. **Prevalence with a real denominator separates from burden.** On gtdb_bacteria against the GTDB
   catalogue: Pseudomonadota 51.8% of 267,130 sampled genomes, Chlamydiota 11.8%, Pelagibacter 0%
   of 1,374; Cyanobacteriota is mid-prevalence (47.9%) but carries the highest exact-RT burden per
   positive genome (2.63).

And one correction of the older reference report, re-derived here: **its headline "retron_V is
structurally distinct — 67% downstream, a fixed architectural inversion" is technical.** The
downstream rate reproduces (66.1%) and 96.9% of those downstream placements fall inside the
contig-start-clipped mode g3 identified, where the RT sits at the window's left edge and any call
is forced downstream. The full comparison is `tables/t27_old_report_reconciliation.tsv`.

## 6 · The self-adversarial pass (BS-14)

**1 · Where is a headline overstated? Name the word.**
- *"one protein re-deposited"* (§5) — **one exact amino-acid sequence**, in 1,276 species-labelled
  records dominated by one species. It is one sequence, not demonstrably one physical element.
- *"missing upstream context"* (§7) — the measured quantity is **bp of retrieved window upstream of
  the RT**, not the biological upstream region. A clipped window means the extractor stopped, not
  that the genome ends there.
- *"prevalence"* (§11) — against the **catalogue**, which is an upper bound on what the pipeline
  attempted. The corpus records no pipeline failures, so every prevalence is a floor.
- *"the gradient is partly definitional"* (§6) — **partly**. The rule files are quoted verbatim;
  how PADLOC weighted them at run time is not in this corpus.
- *"technical clipped mode"* — inherited from g3's audit, not re-established here.

**2 · What alternative explanation produces this exact number?**
- The upstream-context gradient (§7) could be reverse causation: loci whose ncRNA was found might
  be the ones the extractor chose to give more context to. `extended_for_cds` is set on 66.6% of
  records by the extractor's own rule, so this cannot be excluded from inside the corpus. What is
  measured is an association between available context and carriage, and it is monotone across
  eight bins in both the clipped and unclipped strata.
- The partner-consistency result (§8) would follow trivially if recurrent loci were mostly copies
  of one deposit — which they largely are. That is why it is reported by recurrence bin and with
  the cross-species class separated.
- The family-share shift (§2) would follow from any length- or database-correlated artefact in the
  exact-RT key. g2's key-set comparison against the prior project (identical key sets) is the only
  external check available, and it is not independent of the same extraction.

**3 · Could this have returned a negative?** Yes, and it did. The reconciliation was designed to
stop the build and one comparison initially failed; the seeded-bad control run must fail before
the real controls run; the Wilson control failed and corrected an error of mine; and the
composition test in §6 *refuted* the tidy version of its own hypothesis (subtype composition does
not fully explain the tool gradient).

**4 · Unit of every rate.** Every landed table carries `unit` and `denominator` columns, enforced
at write time — a table cannot land without them. Every figure stamps them on the axis. Every
report section opens with its unit/denominator line.

**5 · Numbers with no producing script.** None in `tables/` or in the report prose: 153 of 153
values in the prose resolve from a landed table by an exact selector, traced in
`g7b_resolved_values.tsv`. The counts in *this README* are sums over landed tables and the run log.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** a first `t23` multiplicity view that counted *placements* per locus. It made every
  RefSeq/GenBank twin look like a two-ncRNA locus (46,071 of them). The landed version counts
  distinct exact ncRNA sequences; the placement count is retained beside it as
  `n_loci_with_2plus_placements`.
- **Withdrawn:** hardcoded unit totals in fig10's axis labels, one of which was simply wrong
  (282,969 for a population of 297,793). Every total in a figure label now resolves from a table.
- **Withdrawn:** my own reconciliation rule for the zero-ncRNA class, which compared g3's
  record-level coverage against a placement-level recount and reported a DISAGREE. g3's rule is
  record-level; the check now uses g3's definition and the three coverage rules are landed side by
  side in `t42_definition_differences.tsv` as a declared difference, not a correction.
- **Weakened:** the §6 reading, from "the gradient is subtype composition" to "composition does
  not explain all of it, and the myRT-only and DefenseFinder-only columns cannot be tested this
  way at all".
- **Weakened:** §3's multimodality, from a family-architecture statement to a length observation
  with domain analysis named as out of scope.
- **Not claimed:** anything about the 266 non-Retron candidates beyond their geometry; anything
  causal in §13; any absence anywhere.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g7b_stage1_extended_report/run.sh
== guard: the assembler must REFUSE a number it cannot resolve from a landed table
   refused the unresolvable placeholder, as required
== a01 sections 1-3 ... == a05 sections 11-13
   GTDB catalogue genomes 715,230; RT-positive 299,306
== c01 reconcile every re-derived value against the landed g1-g6 value (STOPS on mismatch)
   294 comparisons, 0 DISAGREE
== c02 independent intervening-CDS recount from rt_window_cds_v1
   5,000 sampled placements; 93,438 window CDS rows pulled
   5 fields compared, 64 placement-level disagreements   <- all in the (context) row, see below
== c03 self-validation: rejected the seeded-bad case, as required
   20 controls, 0 failed
== figures (each reads tables/ and nothing else)
== guard: no figure script may open anything outside tables/
   figure scripts read only tables/
== assemble the report (computes nothing)
REPORT.html: 7,272,609 bytes, 13 sections, 34 figures, 153 resolved values
== BS-3 / WA-B.2: does this reproduce the landed artifacts byte for byte?
  compared 112 tables
  compared 68 figure files
REPRODUCED: every landed table, figure and document is byte-identical on rerun.
wall ~3 min, exit 0
```

The "64 placement-level disagreements" line is the recount's own **context row**, not a
disagreement: all four compared fields agree 100%, and the 64 are the placements whose ncRNA
overlaps the RT CDS *and* another CDS — the case where g3's `overlaps_non_rt_cds`
("overlaps some CDS and not the RT CDS") and a literal reading differ by definition. The row is
landed in `t43_independent_cds_recount.tsv` so the difference is visible rather than smoothed
away; `run.sh` exits non-zero only on a genuine field disagreement.

## 8 · The visual inspection

All 34 figures were rendered and **inspected individually as images** during development, and
eleven were re-plotted after that inspection: label collisions (fig02, fig18, fig21, fig24,
fig25, fig29, fig31, fig34), a legend crossing a title (fig31, fig34), overlapping translucent
bars replaced by step outlines (fig13), a hexbin distorted by setting the axis scale after
plotting (fig26), pooled overflow bins creating false spikes (fig07), and five symlog lines
replaced by a heatmap (fig31). The assembled `REPORT.html` was verified structurally: 34 embedded
figures, 46 expanded tables, 13 caveat blocks, 13 `PROPOSED:` blocks, 0 unresolved placeholders,
0 figures or tables missing a unit or denominator.

⚠️ **What I could NOT check:** a full-page browser rendering of `REPORT.html`. The only browser on
this machine is a snap-packaged Firefox that cannot start in this execution environment (it fails
in `snap-confine` with and without the command sandbox), and no headless renderer is installed.
Installing one was out of scope (`site/TOOLING.md`). The page is plain CSS with no script and no
external asset, and every figure inside it was inspected as an image — but the assembled page has
not been seen rendered, and that is the acceptance step the operator should perform first.

## 9 · Acceptance — the half that is not automatable

Open `INPUTS.tsv` and recognise the 58 inputs: 14 registered derived datasets, 25 landed Stage-1
tables, the GTDB bacterial catalogue, PADLOC's CM metadata and its 18 retron rule files.

Then open `REPORT.html` in a browser — it needs nothing else on disk — and check any number in it
against the row `tables/g7b_resolved_values.tsv` names for it.

If a number here ever disagrees with a landed g1–g7 value, that is a finding to report, not a
licence to edit either bundle: `c01_reconcile.py` is the check that would have caught it, and it
stops the build.
