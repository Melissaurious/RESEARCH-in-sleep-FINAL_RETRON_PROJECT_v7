# Results — Characterization of a large-scale RT / retron mining corpus

> **Draft for the thesis / methods manuscript.** Every number below is traceable to a landed
> Stage-1 bundle (`results/dbchar_g1…g7`) or, where marked ⚙, to the exploratory workbench
> (`ARIS_OUTPUT/dbchar_workbench/`). The provenance manifest at the end maps every figure, table
> and claim to its source file. Figure and table numbers are placeholders — renumber on insertion.

---

## R.1 Corpus definition, identity and analytical populations

The corpus comprises **43 newline-delimited JSON files totalling 81,007,695,609 bytes and
3,358,182 records**, derived from genome and metagenome mining across eight source databases
(`ncbi_bacteria`, `gtdb_bacteria`, `ncbi_archaea`, `gtdb_archaea`, `mgnify_human_gut`,
`mgnify_soil`, `mgnify_marine`, `gem`). Each file was pinned by SHA-256 and the record set by a
single digest computed over every record's file, line number, byte offset and content hash
(`8e9b7999…41d00`), so every downstream number is attributable to an immutable input state.
**No record failed to parse** (0 unparsed lines, 0 records of unexpected anchor type).

The corpus resolves into three file-pure anchor populations:

| population | definition | n records | n files |
|---|---|---|---|
| `POP-RT-FAM` | RT-anchored records in single-RT-family files | 3,050,688 | 41 |
| `POP-RT-MULTI` | RT-anchored records carrying multiple family labels | 9,012 | 1 |
| `POP-NCRNA` | ncRNA-anchored records | 298,482 | 1 |

**The 298,482 ncRNA-anchor-only records were excluded from every RT denominator** by an explicit
analytical-population rule. They are retained with a population flag and may be analysed under
their own denominator, but they do not enter any RT rate, RT-family statistic, or RT–ncRNA
geometry reported here. `POP-RT-MULTI` is likewise held out as a separate ambiguity stratum
(§R.5) and is never folded into a single-family denominator.

⚙ For measurement — as distinct from corpus description — a single house analytical population
was used: distinct records (deduplicating byte-identical lines), MULTI and multi-label records
removed, and geometry-eligible only. This retains **3,026,000 records (98.90 % of raw)**, i.e.
2,822,547 loci, 2,451,078 physical loci, **477,956 exact RT proteins** and 1,535,827 genomes; its
cost is 8,462 duplicate lines, 9,022 MULTI/multi-label records and 16,216 geometry-ineligible
records. Contig-clipped windows were **stratified, not excluded** (§R.9), since ~41 % of records
carry a clipping flag while retaining verified RT coordinates.

> **[Table 1]** — corpus identity: per-file SHA-256, byte size, record count, anchor population.
> **[Table 2]** — analytical populations and the exclusions applied, with per-step denominator cost.

---

## R.2 The analytical unit ladder: counts do not convert by a constant

Because a single genomic locus may be deposited under several database accessions, and a single
RT protein may occur at many loci, the corpus supports several mutually non-interchangeable
counting units. Measured end to end:

| analytical unit | definition | n |
|---|---|---|
| raw record | one line of an RT-anchored file | 3,059,700 |
| distinct record | after byte-identical duplicate lines collapse | 3,051,238 |
| genomic locus | distinct (contig accession, RT start, end, strand) | 2,847,312 |
| physical locus | locus after `NZ_` contig-prefix normalisation | 2,475,684 |
| **exact RT protein** | distinct SHA-256 of the RT amino-acid sequence | **501,561** |
| genome | distinct normalised genome identifier | 1,542,433 |
| RT taxonomic occurrence | distinct (exact RT, genome) | 2,737,189 |

The corpus therefore collapses roughly **six-fold** from records to distinct proteins — but this
factor is an artefact of aggregation, not a conversion constant. Computed per source database, the number of **accession-defined loci per exact RT protein** ranges
from **1.11** (`mgnify_soil`) to **5.49** (`ncbi_bacteria`), a ~5× spread that tracks sequencing
depth rather than any property of the RTs [Figure 1]. ⚙ Within a single source database this
multiplier is numerically identical to *physical* loci per protein, because the `NZ_` twin collapse
merges RefSeq and GenBank spellings of one contig, which by construction sit in different
databases; the locus-definition choice changes corpus-wide totals but not the per-database
redundancy reported here. Consequently, any rate reported on records is weighted by isolate-genome sequencing
effort, whereas the same rate on exact proteins is not; every result below names the unit and
denominator it was computed on.

Redundancy collapse was evidence-supported rather than assumed. **371,628 RefSeq/GenBank twin
pairs** were identified, and every one was confirmed by identical window DNA, identical RT protein,
identical window coordinates and identical strand — **zero disagreements**. No locus carries
conflicting RT sequences (0 of 2,847,312), while **203,921 loci appear under more than one source
database**.

⚙ That cross-database overlap is structurally simple: essentially all of it is the single pair
`ncbi_bacteria + gtdb_bacteria` (200,914 loci), GTDB being a curated re-derivation of assemblies
NCBI publishes. Per-database counts are therefore reported as **coverage, not shares**. Where a
partition is required it is taken at the locus or genome rung under a declared primary-source rule;
it is not taken at the protein rung at all, because **~45 % of exact RT proteins occur in two or
more source databases** [Figure 2].

> **[Figure 1]** — the unit ladder (log-scaled funnel), with loci-per-exact-RT by source database.
> **[Figure 2]** — database attribution: coverage vs exclusive partition, and the exact-RT database span.
> **[Table 3]** — full unit ladder with definitions and denominators.

---

## R.3 Sequence integrity, and what each record can support

Every RT interval was independently re-derived by translating the stored window DNA and comparing
the product to the stored protein. **2,532,006 `POP-RT-FAM` records back-translate to an exact
match and only 618 mismatch**; overall **3,034,472 of 3,050,688 `POP-RT-FAM` records (99.47 %) are
geometry-eligible**, meaning their RT coordinates are verified against the window and the window is
internally self-consistent.

Records that cannot support a given measurement were classified and flagged, never deleted.
**31,504 RT-anchored records carry no annotated RT coding sequence.** These resolve into three
states:

| state | n | interpretation |
|---|---|---|
| `RECOVERED` | 14,188 | RT CDS reconstructed by back-translation; full genomic context retained |
| `SEQUENCE_ONLY` | 16,688 | usable RT sequence, no defensible genomic context |
| `ILL_POSED` | 628 | neither coordinates nor context recoverable |

Within `SEQUENCE_ONLY`, **9,128 records describe an RT lying wholly beyond the contig the extractor
retrieved**, 3,636 an RT crossing a contig end, and 3,924 an inverted window from which no sequence
was retrieved. Recovery was validated against an independent translation implementation, which
agreed on **1,999 of 2,000** sampled records, with zero cases resolved only by a frame shift.

These recovery states map exactly onto the geometry-eligibility flag: every `SEQUENCE_ONLY` and
`ILL_POSED` record is geometry-ineligible and every `RECOVERED` record is eligible, so a single
declared predicate suffices to exclude ill-posed and off-contig systems from any measurement
requiring genomic context ⚙.

> **[Table 4]** — RT-CDS recovery states and representation classes with counts.
> **[Figure 3]** *(optional)* — recovery-state composition and the independent-translation control.

**Caveat to state explicitly in the text.** "Verified" here means that two fields of a single
record agree. Where the upstream pipeline derived both from the same erroneous source, they would
agree and still be wrong; this check bounds internal inconsistency, not upstream correctness.

---

## R.4 RT-family landscape

Family composition was computed on exact RT proteins, since the record-level distribution
principally reports which organisms were sequenced most. The **501,561 exact RT proteins** resolve
into **493,956 single-family proteins across 41 family labels**, **7,593 MULTI-labelled proteins**,
and **12 proteins observed under more than one family label** in single-family files.

Three families dominate distinct-protein diversity: **RVT-GII (51.95 %)**, **Retron (15.85 %)** and
**RVT-DGRs (15.41 %)** — together ~83 % of single-family exact RTs. The record-level and
protein-level distributions differ for every family, and the direction of that difference
identifies the families concentrated in heavily redeposited isolate genomes [Figure 4].

RT protein length differs between families but does not separate them: the overall median is
**385 aa** (range 20–10,449), with **Retron at 342 aa** and **RVT-GII at 407 aa**, while several
ungrouped families occupy markedly longer regimes (RVT-UG5 892 aa, RVT-UG8 606 aa) consistent with
domain fusion. The interquartile ranges of the three largest families overlap substantially, so
length alone is not a classifier [Figure 5]. Extreme lengths were retained rather than trimmed and
are catalogued individually.

Length is confounded by call completeness. Over single-family exact RTs, **25.2 % are `all_partial`**
and the partial fraction varies strongly between families, tracking the same families whose length
medians sit lowest. Family-level length comparisons intended as protein-architecture statements
should therefore be repeated on complete calls only. A missing Prodigal partial flag was classed as
`no_completeness_evidence`, never as "complete" [Figure 6].

**36 of 44 family length baselines from the prior production project were reproduced exactly**
(5 changed, 3 unresolved), providing an external consistency check on the family assignment.

> **[Figure 4]** — exact RTs by family, with protein-level vs record-level composition (all 41 families).
> **[Figure 5]** — RT length distribution by family (box/IQR, Tukey fences, n ≥ 30).
> **[Figure 6]** — completeness composition by family (stacked proportions).
> **[Table 5]** — per-family exact-RT counts, shares, length quantiles and completeness classes.

**Caveat.** `family_label` is the myRT-library assignment carried by the corpus file, not an
independent phylogenetic classification. A family's size is in part the sensitivity and breadth of
its HMM.

---

## R.5 The MULTI stratum is ambiguity, not mislabelling

The 7,593 MULTI-labelled exact RT proteins were re-scored against the myRT HMM library. For
**99.91 %** of them the best-scoring family is among the record's own labels, so the multiple
labels are not spurious. What distinguishes them is the margin: the **median best-versus-second
score gap is 5 bits for MULTI proteins against 81.7 bits in a seeded single-family control**, in
which the best-scoring profile matched the known label for 98.10 % of proteins [Figure 7].

MULTI is therefore an **ambiguity stratum**: these proteins sit where several family profiles score
near-equivalently, not where labelling failed. Stage 1 does not resolve them, and they are excluded
from single-family denominators throughout.

**Caveat to carry.** MULTI proteins are also shorter than single-family proteins (median 283 aa vs
385 aa) and HMM bit score scales with alignment length, so part of the reduced margin may be a
length effect rather than genuine profile ambiguity. Resolving the two requires a length-matched
control, which Stage 1 did not perform.

> **[Figure 7]** — MULTI best-vs-second margin distribution against the seeded control.
> **[Table 6]** — MULTI label-set combinations with HMM best/second family and margin.

---

## R.6 ncRNA detection landscape

Retron ncRNAs were detected by a library of **21 covariance models**, yielding **346,722 ncRNA
calls** that collapse to **16,458 distinct exact ncRNA sequences** in the paired view. Called
ncRNAs occupy a narrow length regime (median 151 nt, IQR 131–193 nt, range 34–395 nt), and most
individual models produce an interquartile range narrower than ~20 nt — largely a property of what
a covariance model can match rather than of msDNA architecture [Figure 8]. Structural annotation is
present for only **1.37 %** of calls.

Call-level and sequence-level model composition diverge sharply: the largest models
(`TypeIA_IIAI`, `Ec107_like`) produce many more calls per distinct sequence than others, i.e. their
hits are concentrated in hyper-deposited organisms and accumulate calls without accumulating
diversity [Figure 9].

**Carriage is overwhelmingly family-restricted.** Of 632,688 Retron loci, **333,838 (52.77 %) carry
at least one ncRNA call and 47.23 % carry none**. Every other family sits at or above 99.9 % zero
(RVT-GII 99.99 %, RVT-DGRs 99.98 %, RVT-UG11 100.00 %). Among loci that do carry a call, the large
majority carry exactly one.

> **This contrast must not be read as biology.** The covariance models are retron models. Outside
> the Retron family the zero-ncRNA rate measures **detector scope**, not the absence of an
> associated ncRNA. Absence claims in this corpus require a positive control demonstrating that the
> same instrument recovers a known-present case on an appropriate substrate.

> **[Figure 8]** — ncRNA length distribution by covariance model.
> **[Figure 9]** — CM composition: calls vs distinct sequences (redundancy per model).
> **[Figure 10]** — zero-ncRNA rate by RT family, with the detector-scope caveat on the figure.
> **[Table 7]** — per-model call counts, distinct sequences, score/E-value medians, length quantiles.

---

## R.7 RT–ncRNA genomic architecture

This is the priority biological output of the characterization. **346,722 placements reduce to
344,154 canonical placements** after de-duplication and geometry eligibility. All geometry was
computed from coordinates and strand; the shipped positional field was not used (§R.9).

The canonical architecture is tight and highly consistent:

| property | value | denominator |
|---|---|---|
| ncRNA upstream of the RT | **325,269 (94.51 %)** | 344,154 canonical placements |
| overlapping | 12,124 (3.52 %) | " |
| downstream | 6,761 (1.96 %) | " |
| median upstream gap | **−55 bp** | upstream placements |
| no intervening CDS | **94.41 %** | 344,154 canonical placements |
| one intervening CDS | 3.61 % | " |
| more than three | 1.55 % | " |
| same strand as the RT | **99.12 %** | " |

Taken together, the dominant arrangement is a close, same-strand, 5′ adjacency: the ncRNA lies
immediately upstream of the RT with no annotated coding sequence between them [Figure 11]. **These
are coordinates. They are compatible with a shared transcriptional unit and do not demonstrate
one**, and they say nothing about cognate RT–ncRNA recognition.

⚙ These four axes are strongly coupled rather than independently distributed. A single joint
combination — **upstream, same strand, no CDS between, within 200 bp** — accounts for **55.22 % of
canonical placements**. Re-weighting to distinct physical loci barely changes the marginals
(upstream 94.51 % → 94.91 %, same strand 99.12 % → 99.45 %), so the arrangement is not produced by
one genomic position being deposited repeatedly. Re-weighting to distinct exact sequence pairs is
more discriminating: the ≤ 200 bp band **strengthens** from 55.22 % of placements to **73.86 % of
exact pairs**, while the 1–5 kb upstream band **collapses** from 32.83 % to 2.95 % — that band is
carried by a few sequence pairs observed very many times. Overall `upstream` falls from 94.51 % of
placements to 88.10 % of exact pairs. **The defensible summary is that close (≤ 200 bp),
same-strand, 5′ adjacency with no intervening CDS is the dominant arrangement under every
weighting, and the only band that strengthens when redundancy is removed** [Figure 11b].

Atypical arrangements were retained and quantified rather than filtered. On the **eligible**
placement population (n = 345,313 — the denominator the atypical catalogue uses, one rung wider
than the canonical 344,154): 12,259 placements overlap the RT, 5,903 have more than two intervening
CDS, 3,095 are on the opposite strand and 557 exceed 5 kb.

⚙ **Note on the same-strand figure.** An earlier internal report stated 99.8 % same-strand. That
value is not reproducible: the gate table and independent recomputation both give **99.12 %**
(341,113 same-strand of 344,154 canonical placements), and the figure is stable across every
population tested. **Use 99.12 %.**

⚙ The 3,041 opposite-strand placements are not a random error tail but a structured population:
**84.5 % derive from a single covariance model (`TypeXIIIA_firmi`)**, 96 % sit at Retron loci, their
median RT–ncRNA distance is **−4,750 bp** against −44 bp for same-strand placements, only 12.5 %
have no intervening CDS against 95.1 %, and they collapse onto just 288 distinct ncRNA sequences
over 439 exact RT proteins [Figure 12]. Architecturally they are a distant, CDS-separated,
single-model population rather than an inverted retron; the leading hypothesis is covariance-model
cross-matching at distance, and this has not yet been excluded.

Non-Retron RTs whose loci carry a retron covariance-model call show a markedly weaker positional
preference: **57.69 % upstream across 260 eligible single-family non-Retron placements**, against
94.51 % for Retron. These are retained as a **candidate population and are explicitly not called
novel retrons** (§R.11).

> **[Figure 11]** — signed RT→ncRNA distance distribution, stratified by contig-start clipping;
> intervening-CDS and strand panels.
> **[Figure 11b]** — joint geometry (direction × strand × adjacency × distance) and the
> placement / physical-locus / exact-pair weighting comparison.
> **[Figure 12]** — same-strand rate across populations, and the structure of the opposite-strand stratum.
> **[Table 8]** — direction, distance quantiles, CDS-between and strand by RT family.

---

## R.8 Exact RT–ncRNA pairing topology

Reducing placements to distinct sequence pairs gives **30,924 exact (RT, ncRNA) pairs**, spanning
**29,192 exact RT proteins and 16,458 exact ncRNA sequences**. ⚙ The registered pair view is built
on the **eligible** placement population (345,313), not the canonical one: 30,427 pairs are
derivable from canonical placements, and the remaining **497 pairs are represented only by
placements removed during de-duplication**. Geometry compositions are therefore reported on the
canonical-derived 30,427, and pair-level topology on the registered 30,924; the two must not be
quoted interchangeably. The relationship is strongly, but not
exclusively, one-to-one:

- **28,271 exact RTs (96.85 %) pair with exactly one ncRNA sequence**; 921 pair with more than one
  (maximum 176).
- **13,542 exact ncRNAs (82.28 %) pair with exactly one RT**; 2,916 pair with more than one
  (maximum 705).
- Decomposing the bipartite graph into 14,918 connected components: **12,079 are strictly 1:1**,
  2,293 many:1, 179 1:many and 367 many:many.

Pair recurrence was classified by the kind of repetition it represents, so that database
redundancy is not mistaken for evolutionary recurrence: 12,005 pairs occur once,
**9,362 recur only as multiple database copies of one physical locus**, 4,452 across multiple
genomes of one species, and **5,056 across multiple species**. Only the last class supports a
co-evolutionary reading.

> **[Figure 13]** — degree distributions on both sides of the pair graph; component-shape composition.
> **[Table 9]** — pair recurrence classes with counts and denominators.

---

## R.9 Two positional signals that are technical, not biological

Two features of the data would produce confident but meaningless results if taken at face value,
and both are reported here so that downstream analyses exclude them.

**(i) The downstream distance mode — and what it is not.** All canonical downstream placements
number **6,761 over 230 distinct exact ncRNA sequences**. *The technical mode* is a defined subset:
the placements within ±150 bp of the 2,682 bp downstream median, i.e. **5,234 placements (77.4 % of
downstream) over just 18 distinct ncRNA sequences, 126 exact RTs and 15 species**, dominated by one
`ncbi_bacteria` / Retron / `TypeV` stratum that is **99.96 % contig-start-clipped** — the extraction
window begins at the contig start, so any call it contains is forced to appear downstream. The
"18 sequences" figure belongs to the mode, **not to downstream placements generally**; the two must
not be conflated.

⚙ Stratifying by the clipping flag also surfaces a population the artefact was masking: the
**1,041 downstream placements that are not contig-start-clipped sit at a median of only 64 bp over
149 distinct ncRNA sequences** — a genuine near-range downstream group that the technical mode does
not explain and that warrants separate examination [Figure 11].

**(ii) The shipped `position_relative_to_rt` field.** This field is null on **331,897 of 346,722
placements** and matches no coordinate frame: of twelve candidate reference frames tested, the best
reproduces only **146 values**. Its variation decomposes as the negative RT offset into the window
plus the ncRNA's intergenic-region index — an index added to a coordinate, which is not a distance.
The field is retained as provenance only; **all geometry reported here is coordinate-derived**.

> **[Figure 14]** — the shipped field: null fraction and the non-null value distribution,
> as a QC exhibit.
> **[Table 10]** — candidate coordinate frames tested against the shipped field, with match counts.

---

## R.10 Taxonomic representation, and what redundancy correction changes

Genome identifiers resolved into their source catalogues essentially completely (99.9999 % for
`ncbi_bacteria`, 100 % for all others). **A resolved join is not a resolved value**, however: the
NCBI assembly summaries carry no genome-completeness column at all, so a quality filter based on
completeness can speak for roughly three-quarters of the corpus and is silent on the rest.

Taxonomic rank coverage is a property of the schema, not of the data quality: **phylum is present
for 100 % of GTDB-assigned records and 0 % of NCBI-assigned records, by construction**. Taxonomy is
therefore reported per system and never pooled — a point of practical importance, since the two
schemas use different names for the same phyla (`Pseudomonadota`/`Proteobacteria`,
`Bacillota`/`Firmicutes`), and pooling them silently splits single taxa into multiple rows.

The corpus is overwhelmingly bacterial; archaeal records are a small minority
(⚙ 10,401 of 3,026,000 house-population records). Under GTDB the leading phyla by distinct RT
protein are Pseudomonadota, Bacillota and Bacteroidota.

**Redundancy correction moves the distribution substantially.** Changing the unit from records to
exact RT proteins:

| measure | on records | on exact RTs |
|---|---|---|
| top species, NCBI (*Escherichia coli*) | **19.97 %** | **6.09 %** |
| top ten species, NCBI | **66.21 %** | **18.95 %** |
| top species, GTDB | 8.57 % | 2.21 % |
| top ten species, GTDB | 26.86 % | 9.85 % |

The two-thirds of NCBI records accounted for by ten species is a statement about deposition
practice; the corresponding 18.95 % of distinct proteins is the diversity statement.

> **[Figure 15]** — taxonomic composition by domain and phylum, split by taxonomy system, on both
> record and exact-RT axes.
> **[Figure 16]** — redundancy correction: top-species share on records vs exact RTs.
> **[Table 11]** — join coverage, quality-field availability and rank coverage per source database
> and taxonomy system.

**Caveats to state.** (i) The join rate is descriptive, not a test: a corpus whose genome
identifiers were harvested from these catalogues resolves into them by construction. (ii) Record
counts measure sequencing effort. Any over- or under-representation claim requires a denominator of
genomes *surveyed*, which a corpus assembled by RT presence does not contain — "representation" is
reported here, never "enrichment".

---

## R.11 Annotation routes disagree, and the disagreement is structured

Across **663,308 distinct Retron records**, detection tools recovered markedly different subsets:
**myRT 92.77 %, PADLOC 68.37 %, DefenseFinder 67.71 %**, with **all three agreeing on 53.17 %** and
at least one tool present by construction.

Where both subtype-writing tools produced a label (**365,708 records**), the labels agree after
case and punctuation normalisation on **160,381 records (43.86 %)** and disagree on 205,327.

Most consequentially for downstream analysis, **ncRNA carriage depends strongly on which tools
called the locus**: 89.23 % for myRT + PADLOC, 70.39 % for all three tools, 44.23 % for
PADLOC + DefenseFinder, but only **13.50 % for myRT alone** [Figure 17]. A tool-defined subset of
this corpus is therefore **not a random subset of it**, and any rate computed on one is conditioned
on the detector combination that produced it.

> **[Figure 17]** — three-set Venn of tool agreement on Retron records, with ncRNA carriage
> annotated per intersection.
> **[Table 12]** — tool presence, subtype agreement and ncRNA carriage per `detected_by` set.

**Caveats.** Agreement between these tools is **not independent corroboration** — they share model
lineage. And a tool absent from a record cannot be distinguished from a tool that was never run on
that genome, so the detection percentages bound tool coverage from below.

---

## R.12 Exceptional populations retained

Consistent with a flag-before-filter policy, atypical observations were retained, quantified and
made addressable rather than removed. The principal retained populations are:

| population | n | why retained |
|---|---|---|
*Denominators differ by row and are named explicitly; rows drawn from the atypical catalogue use
the eligible placement population (345,313), not the canonical one (344,154).*

| retron-CM calls beside non-Retron RTs | 266 (260 single-family, 6 MULTI) | candidate cross-family association; **not** called novel retrons |
| geometry-ineligible placements | 2,568 | 1,303 duplicate lines, 41 RT partially outside window, 37 outside, 28 back-translation mismatch |
| RT wholly beyond the retrieved contig | 9,128 | sequence usable, context not |
| inverted windows, no sequence retrieved | 3,924 | extraction pathology, reported not repaired |
| opposite-strand placements *(canonical)* | 3,041 ⚙ | structured single-CM population (§R.7) |
| placements overlapping the RT *(eligible)* | 12,259 | alternative architecture |
| loci carrying >1 distinct ncRNA sequence *(eligible)* | 398 | multiplicity candidates |
| MULTI stratum | 9,012 records / 7,593 proteins | unresolved family ambiguity (§R.5) |

> **[Table 13]** — full atypical-geometry catalogue with counts and denominators.

---

## R.13 Reproducibility controls

Each analysis gate carried an independent recount of its own headline quantities and a set of
positive controls asserting that the instrument recovers known-present cases. Across the six
measurement gates, **236 independently recounted quantities produced 0 disagreements**, and
**224 positive controls produced 0 failures**. RT reconstruction was additionally validated against
a second translation implementation (1,999/2,000 agreement).

> **[Table 14]** — per-gate recount and positive-control summary.

---

## R.14 Dataset inventory

The characterization delivers a set of named datasets, each with an explicit inclusion rule and an
explicit statement of what it may not be used to claim [Table 15]. Eleven rows are populated: the
full corpus; the distinct-record corpus; the **sequence resource** (distinct, single-family,
well-formed proteins — 3,042,216 records / 493,964 exact RTs) and the **context resource** (the same
plus geometry eligibility — 3,026,000 records / 477,956 exact RTs); the MULTI stratum; the
technically unresolved population; canonical placements overall and Retron-only; the exact-pair
resource; atypical placements; and the retron-CM / non-Retron-RT candidates.

The separation of the sequence and context resources matters: geometry eligibility is the right
rule for analyses needing genomic context and the wrong rule for analyses needing only the protein.
**16,008 exact RT proteins are usable as sequences but have no defensible genomic context**, and
they are retained in the sequence resource and excluded from the context resource.

Three further datasets — **confident RT–ncRNA associations**, a **modeling dataset** and an
**experimental-prioritization dataset** — are specified but **not populated**, because each requires
a selection rule that is a decision rather than a computation [Table 16]. In particular, "canonical
placement" means *technically eligible and de-duplicated*; it is **not** a synonym for a
biologically validated pair, and must not be renamed as one. The open parameters are the distance
cut, whether overlapping placements are included, whether covariance-model hit quality (`score` /
`evalue`, present on every call and **currently unused anywhere in this characterization**) enters
the rule, whether 1:1 partner topology is required or merely flagged, and whether independent
recurrence across genomes or species is required. Applied individually, each criterion retains
between 31 % and 98 % of pairs; their intersection depends entirely on the rule chosen.

> **[Table 15]** — dataset inventory: purpose, unit, inclusion rule, counts, suitable uses,
> unsupported claims, retained uncertainty.
> **[Table 16]** — open parameters for the confident-association rule, with per-criterion
> sensitivity.

---

## Provenance manifest

| § | claim / figure | source |
|---|---|---|
| R.1 | corpus identity, populations, parse failures | `dbchar_g1_corpus_identity/tables/s01_corpus_root.tsv`, `s02_populations.tsv`, `s02_record_manifest_digest.tsv` |
| R.1 ⚙ | house analytical population | `ARIS_OUTPUT/dbchar_workbench/tables/A0_population_cascade.tsv`, `A0_pop_rt_units.tsv`; draft decision in `notes/2026-09-16_house_population_DRAFT_DECISION.md` |
| R.2 | unit ladder, twins, locus conflicts | `dbchar_g2_canonical_units/tables/g2_unit_ladder.tsv`, `g2_twin_evidence.tsv`, `g2_locus_conflicts.tsv` |
| R.2 ⚙ | database attribution, coverage vs partition | `tables/A2_redundancy_by_database.tsv`, `A4_locus_database_sets.tsv`, `A4_database_attribution.tsv`, `A4_exact_rt_database_span.tsv` |
| R.3 | back-translation, eligibility, recovery | `dbchar_g2_canonical_units/tables/g2_bt_status.tsv`, `g2_eligibility.tsv`; `dbchar_g2b_rt_cds_recovery/tables/g2b_summary.tsv`, `g2b_representation_classes.tsv`, `g2b_independent_translation_check.tsv` |
| R.4 | family composition, length, completeness | `dbchar_g4_family_baseline/tables/g4_views.tsv`, `g4_rt_length_by_family.tsv`, `g4_completeness_by_family.tsv`, `g4_prior_reconciliation.tsv` |
| R.5 | MULTI HMM evidence | `dbchar_g4_family_baseline/tables/g4_multi_hmm_profile.tsv`, `g4_multi_hmm_margin_comparison.tsv`, `g4_multi_hmm_positive_control.tsv` |
| R.6 | ncRNA models, lengths, zero-class | `dbchar_g4_family_baseline/tables/g4_ncrna_length_by_model.tsv`; `dbchar_g3_pair_geometry/tables/g3_model_composition.tsv`, `g3_zero_class_by_family.tsv` |
| R.7 | geometry, direction, distance, CDS, strand | `dbchar_g3_pair_geometry/tables/g3_direction.tsv`, `g3_distance_stats.tsv`, `g3_cds_between_explicit.tsv`, `g3_same_strand.tsv`, `g3_atypical_catalogue.tsv`, `g3_nonretron_vs_retron_geometry.tsv` |
| R.7 ⚙ | same-strand correction; opposite-strand structure | `tables/D5_same_strand_by_population.tsv`, `D5_opposite_strand_profile.tsv`, `D5_opposite_strand_composition.tsv`; `notes/2026-09-16_same_strand_discrepancy.md` |
| R.8 | pairing topology and recurrence | `dbchar_g3_pair_geometry/tables/g3_topology_degrees.tsv`, `g3_topology_components.tsv`, `g3_pair_recurrence.tsv` |
| R.9 | technical modes | `dbchar_g3_pair_geometry/tables/g3_downstream_mode_profile.tsv`, `g3_downstream_mode_strata.tsv`, `g3_shipped_field_qc.tsv`, `g3_shipped_field_semantics.tsv` |
| R.10 | metadata, taxonomy, redundancy correction | `dbchar_g5_metadata_sampling/tables/g5_join_coverage.tsv`, `g5_quality_availability.tsv`, `g5_rank_coverage_by_system.tsv`, `g5_redundancy_correction.tsv` |
| R.11 | tool presence, subtypes, carriage | `dbchar_g6_tool_calls/tables/g6_tool_presence_retron.tsv`, `g6_subtype_agreement.tsv`, `g6_extraction_asymmetry.tsv` |
| R.13 | recounts and positive controls | `*/tables/*_second_counts.tsv`, `*/tables/c0*_positive_controls.tsv` |
| R.14 ⚙ | dataset inventory and open rules | `tables/K1_dataset_inventory.tsv`, `K2_criterion_sensitivity.tsv` |
| R.7 ⚙ | joint geometry and weighting comparison | `tables/D6_joint_geometry.tsv`, `D6_marginals_by_weighting.tsv` |
| R.8 ⚙ | pair-view basis; topology; recurrence | `tables/F0_pair_view_basis.tsv`, `F1_partner_degrees.tsv`, `F2_component_shapes.tsv`, `F3_recurrence_classes.tsv` |
| R.9 ⚙ | downstream strata | `tables/D2_downstream_strata.tsv` |

**⚙ = exploratory workbench, not a landed gate.** Three items carry this mark: the house analytical
population (R.1), the database-attribution rule (R.2) and the same-strand correction plus
opposite-strand characterization (R.7). Each should be landed as a governed bundle, or the claim
softened, before submission. In particular, **the same-strand correction is a change to a number
that appears in a landed report**, and should be resolved by a new decision record rather than
carried silently into the manuscript.

## Items to resolve before this section is final

1. **Same-strand**: land the 99.12 % correction and register the quantity in the resolved-value
   table (it currently has no registry key).
2. **Opposite-strand stratum**: test the CM-cross-matching hypothesis before the paragraph in R.7
   claims structure that is causally interpreted.
3. **MULTI length confound**: run a length-matched HMM control, or state in R.5 that the margin
   result is not disentangled from length.
4. **Non-Retron candidates (266)**: decide whether they are described in R.11/R.12 only, or promoted
   to their own subsection with a positive-control-backed absence framework.
5. **Figures 4, 8, 15, 17 do not yet exist** in the current workbench and must be produced.
6. **The confident-association rule (Table 16) is unset.** Until it is, no "high-confidence RT–RNA
   dataset" figure may appear anywhere in the thesis or manuscript.
7. **CM hit quality is unused.** `score` and `evalue` exist on all 346,722 calls and enter no
   analysis in this characterization. Either bring them in or state that detection confidence was
   not filtered.
