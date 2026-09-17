\section{Characterisation of the reverse-transcriptase mining corpus}

\label{sec:dbchar}



The discovery pipeline described in Section~\ref{sec:discovery-pipeline} produced \num{3,059,700} raw RT-system records. A record represents a reported
candidate system, not an experimentally established retron. The following
analyses distinguish repeated observations, sequence diversity and association
evidence to define resources for downstream work.


\subsection{What constitutes one observation}
\label{sec:dbchar:units}
The corpus cannot be counted in a single unit, because the same biological entity can appear repeatedly for several distinct reasons. Distinguishing these forms of repetition is therefore a prerequisite for interpreting every subsequent number. A \emph{locus} is the interval containing an RT on a specified contig and strand, represented by the contig accession together with the start and end coordinates and the strand. Two deposits of the same physical position under different contig accessions are consequently treated as two accession-defined loci. A \emph{physical locus} instead collapses supported alternative accession representations of the same contig, whereas a \emph{distinct RT protein} is defined by its exact amino-acid sequence.

\paragraph{Redundancy of deposition.} It arises because the same assembly can be represented in more than one collection. The corpus contains \num{111,394} normalised genome identifiers represented in two collections, while \num{203,921} accession-defined loci are represented in multiple collections. These are identifier- and locus-level overlaps, respectively, and should not be interpreted as counts of duplicate whole genomes. At the locus level, GTDB re-publishes assemblies obtained from NCBI, producing substantial overlap between the two bacterial collections. Consolidating supported alternative representations reduces the \num{2,847,312} accession-defined loci to \num{2,475,684} physical loci. This reduction comprises \num{371,628} matched RefSeq/GenBank locus pairs for which the local DNA sequence, RT protein sequence, coordinates and strand are identical. Matching RT-containing regions supports consolidation of the locus representations, but does not establish that the corresponding whole genomes are identical; such a claim would require assembly-level comparison.

\paragraph{Redundancy of sampling}. It has a much larger effect and is not removed by accession-level correction. Three species account for 47\% of all NCBI-assigned records: \emph{Escherichia coli} (\num{450,012} records), \emph{Salmonella enterica} (\num{374,314}) and \emph{Klebsiella pneumoniae} (\num{237,525}). The effect becomes apparent when organisms are compared using distinct protein sequences rather than records. For example, \emph{E.\ coli} contributes \num{28,018} distinct RT proteins from \num{450,012} records, corresponding to approximately six distinct proteins per hundred records, whereas \emph{uncultured Lachnospiraceae} contributes \num{7,539} distinct proteins from \num{16,408} records, or approximately forty-six per hundred (Figure~\ref{fig:taxa}). Thus, a family or taxon that is common at the record level may be much less common at the level of distinct proteins simply because the organisms carrying it have been sampled more extensively.

\paragraph{Consequence.} These distinctions determine what each summary statistic describes. Record counts primarily describe deposition and sampling intensity, whereas counts of distinct proteins describe sequence-level diversity; neither is intrinsically the more correct unit, and each result below specifies the unit it uses (Table~\ref{tab:units}). Exact amino-acid sequence deduplication yields \num{501,561} RT proteins. Here, exactness means equality of the stored amino-acid sequences: a single changed residue, an ambiguity character, or a length difference resulting from a truncated gene call is sufficient to produce a separate entry. Consequently, exact sequence counts should be regarded as upper bounds on biological distinctness. Similarity-based sequence clustering is therefore required before interpreting diversity estimates or partitioning the data for downstream modelling.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N6_taxa_and_confidence.png}
\caption[Sampling redundancy and model confidence]{Left: the most frequently deposited species carry
few distinct RT proteins; labels give distinct proteins per hundred records. Right: covariance-model
hit confidence, showing that a threshold at $E \le 10^{-5}$ retains \SI{97.75}{\percent} of calls.}
\label{fig:taxa}
\end{figure}


\begin{table}[htbp]

\centering\small

\caption{Units in the full RT corpus. Rows are counting units, not quality filters.}


\label{tab:units}

\begin{tabularx}{\linewidth}{@{}lXr@{}}

\toprule Unit & Definition & Count\\ \midrule

Raw system record & Candidate-system observation & 3,059,700\\

Distinct record & Identical repeated records consolidated & 3,051,238\\

Accession-defined locus & RT interval on a named contig and strand & 2,847,312\\

Physical locus & Supported duplicate representations consolidated & 2,475,684\\

Exact RT protein & Distinct stored amino-acid sequence & 501,561\\

Genome identifier & Normalised identifier in the corpus & 1,542,433\\

\bottomrule
\end{tabularx}
\end{table}


\subsection{Annotation artefacts and what survives them}
\label{sec:dbchar:qc}

\num{31,504} records carry no annotated coding sequence for the RT they are anchored on. Resolving
them separates a recoverable annotation failure from an irrecoverable one
(Table~\ref{tab:recovery}). For \num{14,188} records the coding sequence was reconstructed by
translating the genomic window and matching the stored protein, and these retain full genomic
context. For \num{16,688} the protein is usable but the genomic context is not: the RT lies wholly
beyond the retrieved contig (\num{9,128}), crosses a contig boundary (\num{3,636}), or sits in an
inverted window from which no sequence could be recovered (\num{3,924}). A further 628 are
irrecoverable. \todo{clarify then what will move on onto the datasets}


\begin{table}[htbp]
\centering
\caption[Records lacking an annotated RT coding sequence]{Resolution of the \num{31504} records
lacking an annotated RT coding sequence. The context-less classes derive entirely from
metagenome-assembled genomes.}
\label{tab:recovery}
\begin{tabular}{llr}
\toprule
Outcome & Basis & Records \\
\midrule
Coding sequence recovered   & reconstructed and verified against the window & \num{14188} \\
Protein only, no context    & RT beyond the retrieved contig                & \num{9128}  \\
                            & RT crossing a contig boundary                 & \num{3636}  \\
                            & inverted window, no sequence retrieved        & \num{3924}  \\
Irrecoverable               &                                               & 628 \\
\bottomrule
\end{tabular}
\end{table}

All \num{16,688} context-less records originate from metagenome-derived
collections and none from isolate-derived collections, where the rate is zero; within the human-gut
MAG collection they are 10.81\% of records. Short, fragmented assemblies simply do not
extend far enough for a gene near a contig edge to be fully represented. This is an assembly
property rather than a detection failure, and it is the reason the two analytical populations of
Section~\ref{sec:dbchar:scope} exist: these records contribute their protein to sequence-level
analyses and are excluded from anything requiring genomic neighbourhood.

Windows truncated at a contig edge were retained rather than excluded, because they are numerous
(approximately 41\% of records carry a truncation flag) and their RT coordinates are
verified; where truncation affects a measurement it is handled by stratification, as in
Section~\ref{sec:dbchar:architecture}.

\subsection{Composition of the RT family landscape}
\label{sec:dbchar:families}

\todo{add the 500K, explain clearly here why from 500--> 493?}
The \num{493,964} distinct RT proteins of the sequence population resolve into \num{486,371}
single-family proteins across 41 family labels and \num{7,593} multi-labelled proteins and 12 cross-labelled proteins. \todo{present them and mention what i did with them, under which family group they stayed?} Three
families dominate protein-level diversity: RVT-GII (51.95\%), Retron (15.85\%) and RVT-DGRs (15.41\%), together approximately
83\% of single-family proteins.

The full-corpus exact-sequence baseline contains \num{501561} RT proteins:
\num{493956} assigned to one family, \num{7593} in the MULTI stratum and 12
with conflicting labels across single-family records. This baseline is not the
record-filtered sequence population introduced above. RVT-GII, Retron and RVT-DGRs
account for \SI{51.95}{\percent}, \SI{15.85}{\percent} and
\SI{15.41}{\percent} of the single-family baseline, respectively.
The Retron subset contains \num{78287} exact proteins.

Reporting each family on records and on distinct proteins side by side makes the redundancy of
Section~\ref{sec:dbchar:units} concrete and family-specific (Figure~\ref{fig:families}). Families
whose record share greatly exceeds their protein share are those concentrated in repeatedly
deposited isolate genomes; the ratio of records to distinct proteins, shown alongside, is a direct
measure of how often the same protein was deposited.


\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N2_family_composition_all.png}
\caption[RT family composition]{All 41 single-family labels, shown as a share of records and of
distinct proteins. The gap between the two bars is the redundancy of deposition; the right panel
gives it directly as records per distinct protein.}
\label{fig:families}
\end{figure}


\paragraph{Lenght distribution.} RT protein length differs between families but does not separate them, and the comparison is only
meaningful once call completeness is accounted for. Completeness is derived from the gene caller's
partial-gene attribute, which records separately whether the 5$'$ and 3$'$ ends of the called gene
were found or ran off the contig. Across distinct records, 88.19\% of RT genes are
complete at both ends, 4.79\% are truncated at the 5$'$ end, 4.31\% at
the 3$'$ end and 1.68\% at both. Since 25.2\% of distinct proteins are
partial at every occurrence, and partial calls are short by construction, a length distribution
pooling both classes understates every family. Figure~\ref{fig:lengths} therefore reports complete
and partial calls separately. On complete calls the overall median is 385 amino acids, with Retron
at 342 and RVT-GII at 407, while several ungrouped families occupy longer regimes consistent with
domain fusion. Extreme values were retained rather than trimmed.


\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N3_rt_length_by_completeness.png}
\caption[RT protein length by family and completeness]{RT protein length by family, separated by
call completeness. Partial calls are short by construction, so pooling the two classes understates
every family.}
\label{fig:lengths}
\end{figure}

\paragraph{Multi-labelled proteins.} Re-scoring the \num{7,593} multi-labelled proteins against the
family profile library places the highest-scoring family among the labels already assigned in
99.91\% of cases, so the multiple labels are not erroneous. They are nonetheless not
resolvable: the median margin between the best- and second-best-scoring family is 5~bits, and 99.8\% of these proteins have a margin below 20~bits, against a median of 81.7~bits in
a seeded single-family control in which the best-scoring profile matched the known label for 98.10\% of proteins. Assigning each protein to its highest-scoring family would
therefore distribute \num{7,593} proteins among families on evidence that does not distinguish those
families. They are excluded from family-level statistics, in which they would enter two denominators
at once, and retained in sequence-level analyses with their label set preserved.


\subsection{Detection of the associated non-coding RNA}
\label{sec:dbchar:ncrna}

Non-coding RNAs were detected with a library of 21 retron covariance models, yielding \num{346,722}
calls that reduce to \num{16,458} distinct RNA sequences. Each distinct sequence is matched by
exactly one model, so per-model counts partition the sequence set cleanly
(Figure~\ref{fig:ncrna}). Detected RNAs occupy a narrow length regime (median 151~nt, interquartile
range 131--193), and most individual models return hits of nearly constant length: these are
model-defined hit boundaries rather than independently determined transcript boundaries, and the
distinction matters for any downstream use of the sequences.


\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures_db_thesis_section/C2_ncrna_length_by_model.png}
\caption[Detected RNA length by covariance model]{Length of detected RNAs by covariance model, on
distinct sequences. Each distinct sequence is matched by exactly one model. These are model-defined
hit boundaries, not transcript boundaries.}
\label{fig:ncrna}
\end{figure}

Hit confidence is high and uniform enough to be used as a filter rather than merely reported:
\SI{97.75}{\percent} of calls have an expectation value at or below $10^{-5}$ and
\SI{55.81}{\percent} at or below $10^{-20}$ (Figure~\ref{fig:taxa}). Confidence is not evenly
distributed across models, however; one model returns \SI{39.2}{\percent} of its calls above
$10^{-5}$, so a global threshold affects models unequally.

Detection is strongly family-restricted: \SI{52.77}{\percent} of Retron loci carry at least one
call, against at or below \SI{0.1}{\percent} for every other family. This asymmetry is expected and
is not evidence about the biology of other families. The models are retron models, so their failure
to match elsewhere measures the scope of the instrument. Figure~\ref{fig:famxmodel} accordingly
reports what the retron models find across families, and should not be read as a statement of which
families lack associated RNAs. Establishing absence would require a positive control demonstrating
that the same instrument recovers a known-present case on an appropriate substrate.


\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N4_family_x_model.png}
\caption[Retron covariance models across RT families]{What the retron covariance models find across
RT families. Near-absence outside the Retron family reflects the scope of the model library and is
not evidence that other families lack associated RNAs.}
\label{fig:famxmodel}
\end{figure}

\subsection{Genomic architecture of the RT--RNA association}
\label{sec:dbchar:architecture}

Geometry was computed from coordinates and strand throughout. The \num{346,722} placements reduce to
\num{344,154} after removing placements on duplicated records and repeated observations of the same
call at one locus; these are referred to below as \emph{eligible, non-redundant placements}, a
technical description that carries no implication of biological validity.

The dominant arrangement is close, same-strand and 5$'$ (Table~\ref{tab:geometry}): the RNA lies
upstream of the RT in 94.51\% of placements, overlaps it in 3.52\% and
lies downstream in 1.96\%; the median upstream separation is 55~bp; 99.12\%
are on the same strand as the RT; and 94.41\% have no annotated coding sequence between
the two features.

These properties are strongly coupled rather than independently distributed. The single combination
of upstream, same strand, no intervening coding sequence and separation within 200~bp accounts for
55.22\% of placements, and the remaining combinations fall away by orders of magnitude.
Re-weighting from placements to distinct physical loci leaves the marginals almost unchanged, so the
arrangement is not produced by one position being deposited repeatedly. Re-weighting to distinct
sequence pairs is more discriminating: the band within 200~bp strengthens to 73.86\% of
distinct pairs, while the 1--5~kb band collapses from 32.83\% of placements to
2.95\% of pairs, showing the latter to be carried by few sequence pairs observed many
times. Close 5$'$ adjacency is therefore the dominant arrangement under every weighting and the only
band that strengthens when redundancy is removed.

These are coordinates. They are compatible with a shared transcriptional unit and do not demonstrate
one, and they carry no information about recognition between a particular RT and a particular RNA.

\paragraph{Overlapping placements.} The \num{12,124} overlapping placements are a benign class rather
than a failure. In 97.36\% of them the RNA overlaps the RT gene itself and not some
other feature; only 45 overlap a different coding sequence. The extent is small: a median of 22~bp,
with 58.5\% overlapping a tenth or less of the RNA and only 266 lying entirely within a
coding sequence. This is the short encroachment expected where an RNA abuts the 5$'$ end of a gene
in a compact locus. Overlapping placements are accordingly retained in the association resource as a
flagged class, and only the two small pathological subsets are set aside.

\paragraph{A technical mode among downstream placements.} Where the extraction window begins at the
start of a contig there is no sequence upstream of the RT to search, so any RNA found is necessarily
reported downstream. These forced placements accumulate at one separation: \num{5,234} placements,
77.4\% of all downstream placements, lie within 150~bp of a median of \num{2,682}~bp,
and involve only 18 distinct RNA sequences across 15 species, with 99.96\% of the
dominant stratum truncated at the contig start. Once they are set aside, the \num{1,041} remaining
downstream placements lie at a median of 64~bp and involve 149 distinct sequences, that is, close to
the RT in the same way upstream placements are.

\paragraph{Placements on the opposite strand.} The \num{3,041} placements on the strand opposite the
RT are concentrated rather than scattered: 84.5\% come from one covariance model and
96\% occur at Retron loci. They differ from same-strand placements in every respect
that matters. Their median separation is \num{4,750}~bp against 44~bp, and only 12.5\% 
have no intervening coding sequence against 95.1\% . They are not an artefact of
repeated deposition, spanning \num{1,324} physical loci across 67 species, and they are not weak
matches, since \num{2,921} of \num{3,041} have an expectation value at or below $10^{-5}$. The same
model additionally produces \num{1,576} same-strand placements at a median of 64~bp across 292
species. A hit several kilobases away, with genes in between, is a match elsewhere in the retained
genomic window rather than a component of the RT's own locus, and these placements are excluded
from the association resource on that basis.

\paragraph{Retron models at non-Retron RT loci.} Non-Retron RT loci carrying a retron covariance
model hit show both a weaker positional preference (57.69\% of 260 eligible placements
upstream, against 94.51\% for Retron) and a far greater separation: a median of
\num{1,802}~bp for upstream placements and \num{4,281}~bp for downstream ones, against 55~bp for
Retron (Figure~\ref{fig:architecture}). They are not architecturally consistent with retron loci and
are retained as candidates for annotation follow-up rather than described as divergent retrons.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N5_architecture_retron_vs_not.png}
\caption[RT--RNA architecture]{Architecture of the RT--RNA association, comparing Retron loci with
non-Retron loci carrying a retron model hit. Overlapping placements are shown as their own category;
the rightmost panel gives the extent of overlap, which is predominantly a short encroachment on the
RT gene itself.}
\label{fig:architecture}
\end{figure}

\subsection{Structure of the association at sequence level}
\label{sec:dbchar:pairs}

Reducing placements to distinct pairs of sequences gives \num{30,924} RT--RNA pairs over \num{29,192}
distinct RT proteins and \num{16,458} distinct RNAs. As observed, the association is close to
one-to-one: 96.85\% of the RT proteins occur with exactly one RNA sequence and
82.28\% of RNAs with exactly one RT protein.

The exceptions are, on inspection, consequences of exact-sequence identity rather than of biology,
and they illustrate why the caveat of Section~\ref{sec:dbchar:units} is load-bearing. Where an RT
protein has several RNA partners, those partners are almost always length variants of one RNA: for
659 of the 921 such proteins the partner sequences differ in length by 5~nt or less, and the most
extreme case, 176 partners, is a near-continuous length series from 68 to 223~nt with 57 sequences
at exactly 158~nt, produced by the model trimming its hit slightly differently at each locus.
Correspondingly, the RNA with the greatest number of RT partners occurs across \num{25,748} genomes
but only 17 species, and its partners range from 58 to \num{1,254} amino acids within one family,
that is, length and truncation variants of related proteins in heavily sequenced taxa. \todo{i dont understand this, so what makes a unique pair?}

Apparent many-to-many structure is therefore largely redundancy. Establishing the true topology
requires clustering both sequence sets at a stated identity threshold, or trimming RNAs to a common
model-defined boundary, before partners are counted.

Recurrence was classified by the kind of repetition it represents. Of the \num{30,924} pairs,
\num{12,005} occur once, \num{9,362} recur only as multiple database copies of a single physical
locus, \num{4,452} recur across genomes of one species and \num{5,056} across species. Approximately
one third of the apparent recurrence in this resource is therefore deposition rather than
independent observation, and only the last two classes support an evolutionary reading. \todo{what does this mean?}


\begin{table}[htbp]
\centering
\caption[Geometry of eligible non-redundant placements]{Geometry of the \num{344154} eligible,
non-redundant RT--RNA placements.}
\label{tab:geometry}
\begin{tabular}{lrr}
\toprule
Property & Placements & Percentage \\
\midrule
RNA upstream of the RT   & \num{325269} & 94.51 \\
Overlapping the RT       & \num{12124}  & 3.52 \\
RNA downstream of the RT & \num{6761}   & 1.96 \\
\midrule
Same strand as the RT    & \num{341113} & 99.12 \\
No intervening CDS       & \num{324904} & 94.41 \\
One intervening CDS      & \num{12427}  & 3.61 \\
\midrule
\multicolumn{3}{l}{Median upstream separation: 55~bp} \\
\bottomrule
\end{tabular}
\end{table}


\begin{table}[htbp]
\centering\small
\caption{Existing cumulative rule exercise (L7), not a final confidence filter.
A pair needs at least one placement passing every condition. The final flag
concerns contig-start clipping only.}
\label{tab:dbchar:cascade}
\begin{tabular}{@{}lrrr@{}}
\toprule Condition & Placements & Pairs & RTs\\ \midrule
Retained placements & 344,154 & 30,427 & 28,976\\
+ Retron label & 343,892 & 30,287 & 28,838\\
+ Same strand & 340,961 & 29,837 & 28,465\\
+ Upstream & 322,223 & 26,293 & 25,043\\
+ No intervening CDS & 311,279 & 25,295 & 24,134\\
+ Gap at most 200 bp & 190,028 & 22,526 & 21,610\\
+ Not contig-start-clipped & 154,066 & 14,905 & 14,268\\
\bottomrule
\end{tabular}
\end{table}

\subsection{From observations to an association resource}
\label{sec:dbchar:dataset}

The preceding sections each identify a population that should not enter a resource intended to
represent RT--RNA association, and applying them in sequence gives the reduction shown in
Figure~\ref{fig:funnel} and Table~\ref{tab:funnel}. Beginning from \num{30,427} distinct sequence
pairs supported by eligible, non-redundant placements, restriction to the Retron family
(\num{30,287}), to same-strand placements (\num{29,837}), to placements that are not downstream
(\num{29,440}), to those with no intervening coding sequence (\num{28,442}), to a separation within
200~bp (\num{25,673}) and to high-confidence model hits (\num{23,680}) retains 77.8\% of
the starting set.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N8_dataset_funnel.png}
\caption[Construction of the association resource]{Reduction from eligible placements to the
association resource, with the count removed at each step and the finding that motivates it.}
\label{fig:funnel}
\end{figure}

Each reduction is attributable. Restriction to Retron follows from detection being
retron-model-scoped (Section~\ref{sec:dbchar:ncrna}); the exclusion of opposite-strand and
downstream placements follows from their being, respectively, distant single-model matches elsewhere
in the window and a window-truncation artefact (Section~\ref{sec:dbchar:architecture}); the
adjacency and separation criteria follow from the joint geometry; and the confidence threshold costs
little because 97.75\% of calls already satisfy it. Overlapping placements are retained,
for the reasons given above.

Two limitations remain, and both are deliberate. Sequence clustering has not been applied, so the
pair counts are upper bounds and the resource is not yet partitioned for modelling: variants of a
single RNA, and truncated variants of a single protein, would otherwise fall on both sides of any
split. And the resource is conditioned on the detection route, as Section~\ref{sec:dbchar:tools}
shows. It is offered in tiers rather than as a single thresholded set, so that a downstream
application may select its own operating point, and the numbers above define the most restrictive
tier.

\begin{table}[htbp]
\centering
\caption[Construction of the association resource]{Construction of the RT--RNA association resource,
with the finding motivating each reduction.}
\label{tab:funnel}
\begin{tabular}{llrr}
\toprule
Criterion & Motivating finding & Pairs & Retained (\%) \\
\midrule
Eligible, non-redundant   & de-duplication, coordinate verification & \num{30427} & 100.0 \\
Retron family             & detection is retron-model-scoped        & \num{30287} & 99.5 \\
Same strand               & opposite strand matches elsewhere       & \num{29837} & 98.1 \\
Not downstream            & window-truncation artefact              & \num{29440} & 96.8 \\
No intervening CDS        & operonic architecture                   & \num{28442} & 93.5 \\
Within 200~bp             & the joint-geometry mode                 & \num{25673} & 84.4 \\
Model hit $E \le 10^{-5}$ & detection confidence                    & \num{23680} & 77.8 \\
\bottomrule
\end{tabular}
\end{table}
\todo{200 basepairs is correct? does it contain all matches?}

\subsection{Dependence on the annotation route}
\label{sec:dbchar:tools}

Every result above is conditioned on which tools annotated a locus, and the size of that effect is
only visible on the protein axis. Across the \num{78,287} distinct Retron RT proteins, the three
detection routes partition as shown in Figure~\ref{fig:venn}. myRT alone accounts for \num{29,436}
distinct proteins, more than the \num{20,203} recovered by all three tools together; on records the
ordering reverses, because the three-tool intersection is dominated by repeatedly deposited
organisms. A tool-defined subset of this corpus is not a random subset of it.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N1_tool_venn.png}
\caption[Detection route]{Agreement between detection routes on distinct Retron RT proteins (left)
and on records (centre), and the RNA carriage rate of each combination (right). The protein and
record axes give opposite orderings.}
\label{fig:venn}
\end{figure}

The apparent rate of RNA association depends on the same choice. Among proteins detected by myRT and
PADLOC the RNA carriage rate is 87.58\%, and among those detected by myRT alone it is
18.64\%. The covariance models are not evenly distributed across tool combinations
either, with individual models occurring almost entirely within particular combinations, so which
model matched and which tools called the locus are not independent.

Two limitations follow. The tools share model lineage, so their agreement is not independent
corroboration; and the absence of a tool from a record cannot be distinguished from that tool never
having been run on the corresponding genome, so these figures bound tool coverage from below.



\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/N7_burden_and_cooccurrence.png}
\caption[RT burden and family co-occurrence]{Distinct RT proteins per genome, genomes carrying
several Retron loci, and the RT family pairs most often sharing a genome. Measured on RT-carrying
genomes only, so it describes co-occurrence among them rather than enrichment.}
\label{fig:burden}
\end{figure}


\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures_db_thesis_section/M2_operons_strand_normalised.png}
\caption[Representative loci]{Representative RT--RNA loci selected by the criteria of
Section~\ref{sec:dbchar:dataset}. All are drawn on the plus strand so that transcription runs left
to right; the strand each locus was found on is marked. Grey arrows are flanking genes outside the
delimited run.}
\label{fig:operons}
\end{figure}



\dbcharproposal{F1: redundancy and taxonomy; T1: units}{
Use A1--A4 for a count schematic and source-overlap panels. Add top genera
before/after deduplication, with unassigned entries; show GTDB phyla separately.
Define how proteins occurring in multiple taxa contribute. Show source coverage
as non-exclusive. Do not label matching loci as identical whole genomes.}

\dbcharproposal{F2: family composition; F3: length; S1: ambiguous labels}{
F2: all 41 IDs with exact-protein counts, percentages and a defined redundancy
multiplier. F3: violin/box distributions with median, interquartile range and n;
mean optional. Add completeness strata and an extreme-value supplement.
B1--B3 provide baselines. S1: the 12 cross-labelled proteins and MULTI
score-margin, coverage and length summaries. Preserve original labels.}


\dbcharproposal{T2: recovery and permitted uses}{
Three rows: reconstructed context, sequence only and unresolved, with counts
and appropriate uses. Keep detailed translation mismatches in supplementary QC
unless their severity affects inclusion. Source-stratified rates need denominators.}


\dbcharproposal{F4: CM composition and RNA lengths}{
Use C2--C3 for all CM IDs, counts on separate call/exact-RNA panels, and exact-RNA
length distributions. Distinguish outgroup models and multi-model handling.
An RT-family-by-CM heatmap is supplementary; give counts and locus-normalised
recovery, not only composition among hits. GC is optional; free-energy
comparison needs a structural question and length/composition controls.}


\dbcharproposal{F5: geometry and locus examples}{
Schematic: RT-relative direction, strand, gap and overlap.
Panels: Retron-only direction/strand, near/full distance ranges, intervening CDS
and joint combinations; extend D1--D6. Specify non-exclusive pair denominators.
Add adjacent, overlapping, near-downstream, distant, opposite-strand and
non-Retron locus examples. Measure overlap extent and relevant-flank availability.
Compare before/after assignment before treating assignment-dependent geometry
as an independent prior.}


\dbcharproposal{F6: pairing and recurrence}{
Extend F1--F3 and L6: many loci with one RNA each versus several candidates at
one locus; partner degrees; recurrence classes; illustrative partner alignments.
Add clustering sensitivity after clustering. Resolve the 497-pair difference
without assuming those pairs are invalid.}


\dbcharproposal{F7: tool Venn; T3: RNA recovery}{
Build E on exact Retron proteins with a declared union of recorded calls.
T3: each tool overall and seven exclusive combinations; RT counts; RNA-detection
and proposed-association counts/rates; unresolved context. Overall rows overlap;
combination rows partition. Add CM-ID composition by combination with a declared
association unit. Do not transfer record-level percentages to a protein Venn.}


\dbcharproposal{F8: dataset selection}{
Use L7 for the cumulative comparison. Add distance-threshold alternatives,
an overlap branch and relevant-flank availability. Expand the inventory with
RNA counts and quality coverage. Priorities: pairing quality, taxonomy and
matched reference-diversity analysis. RT/retron counts per genome and co-occurrence
are exploratory extensions after assembly deduplication; coexistence does not
establish orthogonality.}