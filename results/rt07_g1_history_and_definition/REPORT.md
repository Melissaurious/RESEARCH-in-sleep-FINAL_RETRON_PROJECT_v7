# rt07_g1_history_and_definition

_What the derivational primary sources actually define, and what they only name_

Every number below resolves to a landed table via `tables/g1_resolved_values.tsv`. This document computes nothing.

## 1 · The measurement

This gate classified the evidence for every region name in scope across the derivational primary literature. **6** sources x **32** region names = **192** cells; **53** carry evidence, **129** are cells where the source never names the region at all. Every classification rests on a verbatim quote checked against the extracted text by the code that builds this table: **36** quotes declared, **0** unverifiable. A quote that cannot be found is a build failure, not a warning.

> Naming is not defining, and not naming is not absence. A cell reading NOT_NAMED_IN_SOURCE says the source does not use that name - nothing about biology, and nothing about whether the source describes the region under another name.

Tables: `tables/g1_literature_evidence_matrix.tsv`, `tables/g1_evidence_quotes.tsv`

## 2 · ALIGN_000044 was acquired, and it does not contain the blocks

The primary-source alignment behind the only held paper that numbers RT subdomains was approved for governed acquisition and is now in hand: **2** file(s), state **ACQUIRED_VERIFIED**, **132,904** bytes, from the EMBL-EBI public archive; **0** asset(s) landed MISSING_PRIMARY_ASSET. It is a **1,441**-column alignment of **66** protein sequences, submitted **13-NOV-2000**, built by **PILEUP, CLUSTALX and manual adjustment**. It annotates **3** domains - the RT domain at columns **261-886**, plus maturase and nuclease - and **0** numbered subdomains.

> PROPOSED: the alignment is the right substrate for g2 and the wrong source for the labels. The blocks must be re-derived on it from the stated conservation criteria and the recovery reported as a measurement; they cannot be read off it. The record also states a manual adjustment step, so the alignment is a fixed primary artefact, not a reproducible procedure.

Tables: `tables/g1_acquisition_source_resolution.tsv`, `tables/g1_align000044_record_summary.tsv`

## 3 · The numbering is inherited, and one link leaves the held set

**12** genealogy edges were traced, each carrying a verified quote. **6** of them point at a source this project does not hold. The seven-way partition originates with Xiong & Eickbush 1990 (domains 1-7, 178 aa); Zimmerly 2001 numbers subdomains 0-7 but states plainly that the labels are inherited from three earlier papers and only adjusted against its own alignment; Blocker 2005 supplies the modern RT0-RT7 spelling as a respelling with citations. RT0 itself was renamed from domain Z in Malik, Burke & Eickbush 1999 - which is not held here.

> PROPOSED: RT0's definitional source being unheld is the weakest link in the chain, and it is the link RT0 hangs from. Both held statements of RT0's scope cite that paper rather than deriving the region.

Tables: `tables/g1_terminology_genealogy.tsv`

## 4 · What can and cannot be operationalised

Of **32** region names: **1** has a stated residue boundary, **18** have a derivable procedure but no coordinates, **1** is NO_OPERATIONAL_BASIS and **1** is not in the held evidence at all. Across (source, region) pairs, **7** could define an operational boundary and **18** could not. Xiong & Eickbush give a restatable criterion for the blocks - conserved positions present in over 50% of RT elements from three of the four most abundant groups - so the textual-criteria route of launcher 5e succeeds and figure digitisation is not needed to recover the criteria. What no source gives is a per-block residue extent.

> RT0 lands **DERIVABLE_PROCEDURE** and domain 1 lands **DERIVABLE_PROCEDURE**; domain X lands {domainX_verdict}. Motif E lands {motifE_verdict} and motif F {motifF_verdict} - the F label does not exist in the held derivational sources.

Tables: `tables/g1_region_verdicts.tsv`, `tables/g1_operational_evidence_matrix.tsv`

## 5 · Spelling and concept are different objects

The modern spelling RT1 appears **0** times in Xiong & Eickbush 1990 and **1** times in Zimmerly 2001. The concept is present in both; the spelling is not. Every modern-spelling row therefore lands SPELLING_ONLY_NO_INDEPENDENT_DERIVATION rather than a verdict about the block, so that 'RT1 has no operational basis' can never be read off this table as a statement about domain 1.

> Zimmerly 2001's evidence class for subdomain 0 is **EXPLICIT_STATED_BOUNDARY** and Xiong's for domain 5 is **ALIGNMENT_BLOCK**. Different classes, different objects, different papers.

Tables: `tables/g1_token_census.tsv`, `tables/g1_region_verdicts.tsv`

## 6 · Controls and the second count

**9** positive controls pass: the modern-spelling detector is demonstrated on a source known to use that spelling, and the alignment-annotation detector is demonstrated on the alignment record itself before its zero is reported. **9** independent second-count checks were run through a route sharing no code with the census, with **0** disagreements.

> The alignment-annotation control earned its place: on the first run it FAILED, because EMBL line-type codes split every wrapped sentence. The zero it was guarding was an artefact, and the control is what found it.

Tables: `tables/g1_detector_positive_control.tsv`, `tables/g1_second_counts.tsv`, `tables/g1_census_route_agreement.tsv`

## 7 · What stays open

**6** items are open in the unresolved-definition register, including where RT0 is actually defined, which blocks Simon & Zimmerly's 59 across-the-set alignable characters fall in, and whether Figure 1's printed columns yield per-block extents.

> Two questions are deliberately NOT answered here and may not be settled by a gate: whether this operational method becomes its own methods paper, and how any future RT1 concordance failure is interpreted.

Tables: `tables/g1_unresolved_definition_register.tsv`, `tables/g1_prior_reconciliation.tsv`
