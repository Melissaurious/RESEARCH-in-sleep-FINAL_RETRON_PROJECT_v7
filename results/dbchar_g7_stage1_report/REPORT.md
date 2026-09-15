# Stage 1 — RT/retron corpus characterisation


## 1. The corpus, identity-pinned

Stage 1 rests on 43 files, 81,007,695,609 bytes, 3,358,182 newline-delimited records, each file pinned by sha256 and the record set pinned by one digest over every record's file, line, byte offset and content hash: 8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00. There were no parse failures of any kind. The corpus splits into three anchor populations that are file-pure: 3,050,688 RT-anchored records in the single-family files, 9,012 in the MULTI file, and 298,482 ncRNA-anchor-only records.

> The ncRNA-anchor-only records are outside the RT analytical population by operator decision and enter no RT denominator anywhere in Stage 1.


## 2. The analytical units do not convert by a constant

3,059,700 raw records collapse to 3,051,238 distinct records, 2,847,312 loci, 2,475,684 physical loci and 501,561 exact RT proteins across 1,542,433 genomes (2,737,189 RT taxonomic occurrences). The conversion factor between units is itself database-dependent - loci per exact RT runs from 1.11 to 5.49 - so a raw-record count and a locus count describe different populations. 371,628 RefSeq/ GenBank twin pairs were found and every one is supported by identical window DNA, RT protein, window coordinates and strand (371,628 collapse-supported, zero disagreements). 0 loci carry conflicting RT sequences; 203,921 loci appear under more than one source database.

> The locus key is a coordinate interval on a contig accession: two assembly versions of one contig are two loci here.


## 3. RT integrity, and what each record can support

The RT interval was translated from the window DNA and compared with the stored protein: 2,532,006 records match exactly, only 618 mismatch, and 99.47% of RT-family records are geometry-eligible. Records that cannot support a measurement are flagged, never deleted. Of the 14,188 RT records with no marked RT CDS that are fully recoverable, recovery is by back-translation and confirmed by an independent implementation; 16,688 keep a usable sequence but no defensible genomic context - 9,128 of them lie wholly beyond the contig the extractor retrieved - and 628 remain ill-posed.

> &quot;Verified&quot; means two fields of one record agree. Where the pipeline wrote both from the same wrong place, they would agree and still be wrong.


## 4. RT↔ncRNA geometry: the priority biological output

346,722 placements reduce to 344,154 canonical ones. On those, the ncRNA sits upstream of the RT in 325,269 placements against 6,761 downstream and 12,124 overlapping, at a median gap of -55 bp, on the same strand in 99.8% of cases, with no intervening CDS in 94.41% (one CDS 3.61%, more than three 1.55%). The exact-pair view holds 30,924 distinct (RT, ncRNA) sequence pairs, of which 12,079 components are strictly one-to-one.

> The covariance models are retron models. The zero-ncRNA rate is 47.23% for Retron loci and 99.99% for RVT-GII: outside Retron this measures detector scope, never biological absence. The 260 retron-CM placements beside non-Retron RTs (57.69% upstream) are retained as a candidate population and are not called novel retrons.


## 5. Two geometry signals that are technical, not biological

The downstream placements cluster at a median 2,682 bp, but the cluster contains only 18 distinct ncRNA sequences and 99.96% of its dominant stratum is contig-start-clipped - the window begins at the contig start, so any call is forced downstream. It is labelled a technical mode. Separately, the shipped position_relative_to_rt is null on 331,897 placements and matches no coordinate frame: the best of twelve candidates reproduces 146 values. Its variation is -(RT offset into the window) plus the ncRNA's intergenic-region index - an index minus a coordinate.

> Neither signal is used as a prior. The coordinate-derived geometry is canonical; the shipped field is retained as provenance only.


## 6. Family baselines, and why MULTI carries several labels

On exact-sequence views - 493,956 single-family proteins, 7,593 MULTI, 12 spanning labels - RVT-GII has a median length of 407 aa and Retron 342 aa. 36 of the prior project's 44 family length baselines are reproduced exactly. The MULTI labels were investigated with the myRT HMM library: the best-scoring family is among the record's own labels for 99.91% of MULTI proteins, and the best-vs-second margin is 5 bits against 81.7 bits in a control whose best hit matches the known label 98.10% of the time. MULTI is an ambiguity stratum, not mislabelling.

> MULTI proteins are also shorter, and score scales with length, so part of the tie may be a length effect. Stage 1 does not resolve MULTI.


## 7. Metadata, taxonomy and what redundancy correction changes

Every catalogue join resolves (100.00% for the largest, ncbi_bacteria), but a join that resolves a row is not one that resolves a value: the NCBI summaries carry no completeness column at all, so a quality filter can speak for roughly a quarter of the corpus's genome entries. Taxonomy is reported per schema - phylum coverage is 100.00% under GTDB and 0.00% under the NCBI block, which has no phylum by construction. Correcting for redundancy moves the distribution: Escherichia coli is 19.97% of NCBI records but 6.09% of exact RTs, and the top ten species fall from 66.21% of records to 18.95% of exact RTs.

> The join rate is a description, not a test: a corpus whose genome ids were harvested from these catalogues resolves into them by construction.


## 8. Annotation routes disagree, and the disagreement is structured

myRT detected 92.77% of Retron records, PADLOC 68.37%, DefenseFinder 67.71%, and all three together 53.17%. Where both tools wrote a subtype (365,708 records) they agree on 160,381. Most consequentially, ncRNA carriage depends on which tools called the locus: 89.23% for myRT+PADLOC against 13.50% for myRT alone. A tool-defined subset of this corpus is not a random subset.

> Agreement between these tools is not independent corroboration - they share model lineage - and a tool missing from a record cannot be distinguished from a tool that was never run on that genome.
