# Thesis `\todo` resolutions — database characterization

Each item quotes your `\todo`, states the **answer**, gives **paste-ready thesis text** (LaTeX-safe
markdown), and names the figure/table and the reproducing notebook cell. Items that are **decisions
rather than measurements** are marked **[YOUR CALL]** and carry a recommendation, not a fait accompli.

---

## T1 — "clarify that the same genome appears in ncbi–gtdb with an added prefix but same genome"

**Answer.** Confirmed and quantified. **200,914 of 2,822,547** working-population loci appear under
both `ncbi_bacteria` and `gtdb_bacteria` (plus 2,534 under both archaeal databases); 111,394 genomes
appear under two databases. GTDB re-derives NCBI assemblies and prefixes RefSeq contigs with `NZ_`,
so the *same physical position* is deposited twice under two accession spellings.

> **Paste:** Genome and contig identifiers are not unique across source databases. GTDB re-publishes
> assemblies obtained from NCBI, and RefSeq contig accessions carry an `NZ\_` prefix absent from the
> corresponding GenBank record. A locus defined on the contig accession therefore counts one physical
> position twice when it has been deposited under both schemes. Normalising the contig prefix
> collapses 2,847,312 accession-defined loci to 2,475,684 physical loci. Every one of the 371,628
> RefSeq/GenBank twin pairs was confirmed by identical window DNA, identical RT protein sequence,
> identical window coordinates and identical strand, with no disagreements, so the collapse is
> evidence-supported rather than assumed.

*Do not write* "no accession overlap means no duplication" — the converse does not hold.
**Fig.** [Fig-DB-overlap] · **Table** [Tab-units] · **Cell** A4, `tables/A4_locus_database_sets.tsv`

---

## T2 — "I think we have sufficient evidence to say what happened: metagenomic assemblies, different gene call, or quality?"

**Answer: metagenomic assembly fragmentation. Unambiguously.** All **16,688** sequence-only records
come from metagenome-derived databases and **none** from isolate databases:

| database | sequence-only records | % of that database |
|---|---|---|
| `mgnify_human_gut` | 15,364 | 10.81 % |
| `mgnify_marine` | 766 | 9.63 % |
| `mgnify_soil` | 533 | 3.40 % |
| `gem` | 25 | 0.11 % |
| `ncbi_*`, `gtdb_*` (isolate) | **0** | 0 % |

Not a gene-calling disagreement, not a genome-quality filter.

> **Paste:** The sequence-only category is entirely attributable to metagenomic assembly
> fragmentation. All 16,688 such records originate from metagenome-derived databases
> (\texttt{mgnify\_human\_gut}, $n=15{,}364$; \texttt{mgnify\_marine}, $n=766$;
> \texttt{mgnify\_soil}, $n=533$; \texttt{gem}, $n=25$), and none from isolate-derived databases,
> where the corresponding rate is zero. Within the human-gut MAG collection they represent 10.81\% of
> records. The three underlying representation classes---an RT lying beyond the retrieved contig
> ($n=9{,}128$), an RT crossing a contig boundary ($n=3{,}636$), and an inverted window from which no
> sequence could be recovered ($n=3{,}924$)---are all expected consequences of short, fragmented
> metagenome-assembled contigs, on which a gene may extend past the available sequence. These records
> retain a usable protein sequence and are excluded only from analyses requiring genomic context.

**Fig.** [Fig-QC-recovery] · **Cell** L1, `tables/L1_sequence_only_by_database.tsv`

---

## T3 — "identify those 12"

**Answer.** All twelve carry the **same** label pair: `RVT-CRISPR | RVT-CRISPR-like`. Lengths
202–983 aa, 2–89 records each, each in 2–50 genomes. This is one profile boundary, not twelve
unrelated confusions.

> **Paste:** Twelve exact RT proteins were observed under more than one family label across
> single-family files. All twelve carry the same pair of labels, \texttt{RVT-CRISPR} and
> \texttt{RVT-CRISPR-like}, indicating a single region of overlap between two closely related
> profiles in the detection library rather than dispersed labelling inconsistency. They range from
> 202 to 983 amino acids and occur in 2--50 genomes each. They are reported as their own view
> (\texttt{V-RT-CROSS}) and are excluded from single-family denominators.

**Table** [Tab-crosslabel] (all 12 rows; supplementary) · **Cell** L2

---

## T4 — "add what is prodigal flag 00, 01, 10, 11 and what it means"

**Answer.** Two digits: left = 5′ end, right = 3′ end. `0` = boundary found, `1` = gene runs off the
contig. Observed over distinct records: `00` 88.19 %, `10` 4.79 %, `01` 4.31 %, `11` 1.68 %, empty
1.03 % (the no-RT-CDS population).

> **Paste:** Completeness is derived from the Prodigal \texttt{partial} attribute, a two-digit code
> in which the first digit describes the 5$'$ end of the called gene and the second the 3$'$ end;
> \texttt{0} indicates that the corresponding boundary was identified and \texttt{1} that the gene
> runs off the edge of the contig. Thus \texttt{00} denotes a complete open reading frame with both a
> start and a stop codon, \texttt{10} and \texttt{01} denote genes truncated at the 5$'$ and 3$'$ end
> respectively, and \texttt{11} denotes a gene whose contig is shorter than the gene itself. Across
> distinct records, 88.19\% are \texttt{00}, 4.79\% \texttt{10}, 4.31\% \texttt{01} and 1.68\%
> \texttt{11}. Partiality is a property of the assembly rather than of the protein, and a record
> lacking the attribute entirely is classified as having no completeness evidence rather than as
> complete.

**Cell** L3, `tables/L3_prodigal_partial_flags.tsv`

---

## T5 — "how shall I treat MULTI? include them back into the stats or downstream?" **[YOUR CALL]**

**Recommendation: keep them out of family statistics, put them into sequence-level resources, and
report them as their own result.** Three reasons from the data:

1. The evidence says *ambiguous*, not *mislabelled* — best-scoring family is among the record's own
   labels for 99.91 %.
2. But the discriminating evidence is weak: median best-vs-second margin **5 bits** against **81.7
   bits** in the seeded control. Assigning each to its top-scoring family would be a coin-flip
   dressed as a classification.
3. **The margin result is confounded with length** — MULTI proteins are shorter (median 283 aa vs
   385 aa) and HMM bit scores scale with alignment length. A length-matched control has not been run.

So: exclude from per-family composition, length and completeness statistics (they would
double-count into two families). Include in protein-level resources where family is not the unit —
diversity, clustering, RT–ncRNA pairing — with a `MULTI` flag carried through, since 7,593 proteins
is real sequence diversity that costs nothing to retain.

> **Paste:** Multi-labelled records were retained as a separate stratum throughout. Re-scoring
> against the family profile library showed that for 99.91\% of these proteins the highest-scoring
> family was among the labels already assigned, indicating that multiple labels reflect genuine
> profile ambiguity rather than erroneous assignment. The discriminating evidence is nonetheless
> weak: the median margin between the best- and second-best-scoring family is 5 bits, against 81.7
> bits in a seeded single-family control in which the best-scoring profile matched the known label
> for 98.10\% of proteins. Multi-labelled proteins are also shorter than single-family proteins
> (median 283 versus 385 amino acids), and profile bit scores scale with alignment length, so the
> reduced margin is not fully separable from a length effect. They are therefore excluded from
> family-level statistics, in which they would contribute to two denominators simultaneously, and
> retained in sequence-level analyses where family membership is not the unit of analysis.

**Fig.** [Fig-MULTI-margin] · **Before publishing**: run the length-matched control, or state the
confound as above.

---

## T6 — "same strand and exactly next to RT upstream should be the pool for the ncRNA–RT dataset" **[YOUR CALL — costed below]**

**Answer: your rule is sound and here is exactly what it yields.** Applied cumulatively to canonical
placements:

| rule | placements | exact pairs | exact RTs | exact ncRNAs | physical loci | pairs kept |
|---|---|---|---|---|---|---|
| canonical | 344,154 | 30,427 | 28,976 | 16,011 | 297,793 | 100 % |
| + Retron only | 343,892 | 30,287 | 28,838 | 15,906 | 297,608 | 99.5 % |
| + same strand | 340,961 | 29,837 | 28,465 | 15,666 | 296,061 | 98.1 % |
| + upstream | 322,223 | 26,293 | 25,043 | 13,793 | 280,986 | 86.4 % |
| + no CDS between | 311,279 | 25,295 | 24,134 | 13,252 | 271,714 | 83.1 % |
| **+ within 200 bp** | **190,028** | **22,526** | **21,610** | **11,514** | **156,741** | **74.0 %** |
| + not contig-start-clipped | 154,066 | 14,905 | 14,268 | 8,382 | 127,057 | 49.0 % |

Strand and adjacency are nearly free — the population already satisfies them. **The distance cut and
the clipping cut are the only consequential decisions**, and clipping alone removes a further 34 %.

Within the 22,526-pair rule, recurrence splits: 8,660 single-placement · 6,686 database copies of one
physical locus · **7,180 independently recurrent** (3,761 across species).

**Recommendation: ship three tiers, not one threshold.**
- **Permissive** (22,526 pairs) — Retron, same strand, upstream, no CDS between, ≤ 200 bp
- **Strict** (14,905) — additionally not contig-start-clipped
- **Independent** (~7,180 before re-intersection) — additionally recurring across genomes or species

Then the paper reports all three and a model picks its operating point, instead of you defending one
number. **Covariance-model hit quality (`score`, `evalue`) is in none of these tiers** — it is
present on all 346,722 calls and used nowhere. Add it before calling any tier "high-confidence".

**Fig.** [Fig-dataset-cascade] · **Cell** L7, `tables/L7_dataset_rule_cascade.tsv`

---

## T7 — "these may be annotation artefacts... and if a non-retron system is consistent with retrons, are they divergent retrons or chance?"

**Answer: chance, on the current evidence — and the distances settle it.**

| population | upstream median | downstream median |
|---|---|---|
| Retron | **−55 bp** | — |
| non-Retron, retron-CM hit | **−1,802 bp** (n=150) | **+4,281 bp** (n=108) |

The non-Retron candidates sit roughly **33× further** from their RT than retron ncRNAs do. They are
not a weaker version of retron architecture; they are a different thing at a different scale.

> **Paste:** Non-Retron RT loci carrying a retron covariance-model hit showed a weaker positional
> association: 57.69\% of 260 eligible single-family non-Retron placements were upstream of the RT,
> compared with 94.51\% among Retron placements. The separation is also an order of magnitude larger.
> Upstream non-Retron placements lie at a median of 1,802 bp from the RT and downstream placements at
> 4,281 bp, against a median of 55 bp for Retron placements. These hits are therefore not
> architecturally consistent with retron loci, and proximity alone does not support their
> interpretation as divergent retrons. They are retained as candidate associations for annotation
> follow-up, and would require covariance-model hit quality, RT phylogenetic placement and inspection
> of the intervening region before any stronger claim could be made.

On the atypical placements generally: say they are **heterogeneous in cause** — window clipping,
annotation gaps in the intervening region, and possible biology — and that Stage 1 flags them rather
than adjudicating them. Do not assert "annotation artefact" wholesale; you have not shown it for all
of them, and for the opposite-strand group (T8) it is demonstrably not the whole story.

**Fig.** [Fig-nonretron-geometry] · **Cell** L5

---

## T8 — "is this biology? or a consistent annotation artefact, e.g. same genome measured many times?"

**Answer: not database redundancy. The simplest artefact is excluded.** The 2,571 opposite-strand
`TypeXIIIA_firmi` placements span **1,324 physical loci, 1,322 genomes, 67 species, 2 databases**.

The sharpest result is that **one model produces two disjoint populations**:

| `TypeXIIIA_firmi` | placements | median distance | genomes | species |
|---|---|---|---|---|
| same strand | 1,576 | **+64 bp** | 1,359 | **292** |
| opposite strand | 2,571 | **−4,750 bp** | 1,322 | **67** |

Same covariance model, two geometries, disjoint in distance *and* in taxonomic range.

> **Paste:** The opposite-strand placements are not an artefact of repeated deposition. The 2,571
> placements attributed to the \texttt{TypeXIIIA\_firmi} model span 1,324 distinct physical loci,
> 1,322 genomes and 67 species across two source databases, so the arrangement recurs across
> independent assemblies. The same model additionally produces 1,576 same-strand placements at a
> median separation of 64 bp across 292 species, disjoint from the opposite-strand set in both
> separation and taxonomic range. A single covariance model therefore recovers two distinct
> populations. Whether the opposite-strand population reflects a genuine distant antisense
> arrangement restricted to a narrow clade, or the model matching a second, unrelated element, cannot
> be resolved from placement geometry alone and requires characterisation of the 142 ncRNA sequences
> involved.

**This is one of the more interesting findings in the characterization** — it is a concrete,
bounded follow-up, not a caveat. **Fig.** [Fig-strand-strata] · **Cell** L4

---

## T9 — "cross-check if the 176 comes from storing all ncRNA matches in the same metadata and we should keep only the highest-confidence one"

**Answer: no — that is not the mechanism.** For multi-partner RTs, **237,965 placements sit at loci
carrying exactly one distinct ncRNA sequence**, against only 376 at loci carrying 2–3. The
multiplicity is **the same exact RT protein occurring at many loci whose ncRNA calls differ
slightly**, not several matches stored against one locus.

And the differences are boundary jitter: for **659 of 921 multi-partner RTs (71.6 %)** the partners'
lengths span **≤ 5 nt**. The 176-partner extreme is a near-continuous length ladder from 68 to 223 nt
with 57 sequences at exactly 158 nt.

So the fix is **not** "keep the highest-scoring call". It is **cluster the ncRNAs** (or trim to a
common model-defined boundary) before counting partners.

**Fig.** [Fig-multiplicity] · **Cell** L6

---

## T10 — "how can we explain the 705? different taxa? a single amino-acid change? how to treat this in a data split?"

**Answer: both of your hypotheses, and they compound.** The 705-partner ncRNA spans **25,748 genomes
but only 17 species** (hyper-sequenced isolates), and its RT partners range from **58 to 1,254 aa**
(median 585) within one family — i.e. largely length and truncation variants.

Exact-sequence identity is a very fine equivalence: one residue, or a partial call, creates a new
`rt_seq_hash`.

> **Paste:** Conversely, 2,916 ncRNA sequences were associated with more than one RT protein, with a
> maximum of 705. This reflects the resolution of exact-sequence identity rather than promiscuous
> association. The most connected ncRNA occurs across 25,748 genomes but only 17 species, and its RT
> partners range from 58 to 1,254 amino acids within a single family, indicating that they are
> largely length and truncation variants of related proteins deposited under a small number of
> heavily sequenced taxa. A single residue difference, or a partial gene call, produces a distinct
> sequence hash and therefore a distinct node.

**On the data split — this matters and is easy to get wrong.** Splitting on un-clustered exact
hashes **leaks**: boundary variants of one ncRNA and truncation variants of one RT would land in both
train and test, and a model would score well by memorising. Do all three:
1. Cluster **both** sides at a stated identity (e.g. MMseqs2/CD-HIT) and split on **clusters**;
2. Never split within a physical locus — the 30.32 % of pairs that recur only as database copies of
   one locus must stay on one side;
3. Consider a **taxonomy-aware** held-out split (hold out species or genera), since 17 species carry
   a large share of the pairs.

**Cell** L6, `tables/L6_partner_length_spread.tsv`

---

## T11 — "so what would be the ultimate RT–ncRNA dataset?" **[YOUR CALL]**

There isn't one — and saying so is the stronger position. What the data supports is the **tiered**
release in T6, plus the clustering and split rules in T10, plus one addition: **bring covariance-model
hit quality in**. Four open parameters remain yours: the distance cut (200 bp is defensible and
evidence-based), whether clipped windows are excluded, whether CM score/E-value enters, and whether
independent recurrence is required.

Also, hold the line on vocabulary: **"canonical placement" means technically eligible and
de-duplicated.** It is not a synonym for a validated pair, and renaming it would be the single
easiest way to lose a reviewer.

---

## T12 — "Venn diagram: shall we report on loci or unique RT sequence?" **[YOUR CALL]**

**Recommendation: unique RT protein as the primary, locus as a supplementary panel.** The question
the Venn answers is "which tools recognise this RT", which is a property of the protein; on records
or loci the diagram is dominated by how often organisms were sequenced. Note this changes the
headline numbers materially — the prior project measured 88.3 % vs 20.8 % ncRNA carriage on exact
RTs where the record-level figures are 89.23 % vs 13.50 % — so the axis must be stated on the figure.

Caveat to print **on** the figure: the three tools share model lineage, so agreement is not
independent corroboration, and a tool absent from a record cannot be distinguished from a tool never
run on that genome.

**Status: not yet built** — notebook section E is still a scaffold, and it currently specifies
record-level analysis that should be re-specified to protein level before it is implemented.

---

## Still genuinely open

| # | item | why it is open |
|---|---|---|
| 1 | CM `score` / `evalue` unused | present on all 346,722 calls, in no analysis |
| 2 | MULTI length-matched control | the 5-bit margin is confounded with length |
| 3 | The 142 opposite-strand ncRNA sequences | what they actually are (T8) |
| 4 | Sections E, G, H | tool agreement, MULTI detail, taxonomy |
| 5 | Sequence clustering | needed for T10's split, not yet run |
