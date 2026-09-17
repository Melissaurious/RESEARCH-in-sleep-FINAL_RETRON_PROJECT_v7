# G2L holdout scope classification

## Classification: `FRESH_FAMILY_WITHIN_RELATED_LINEAGE`

**Not `FRESH_LINEAGE`, and not `NOT_INDEPENDENT`.**

### Why not `NOT_INDEPENDENT`

Every contamination measure is zero: **0** exact sequence overlap with any construction derivation
set, **0** exact overlap with the GII construction set specifically, **0** G2L identifiers in any
construction object, and **0** hits from a content scan of construction sequence and alignment
files. No G2L object entered anchor selection, threshold setting, placement-rule development,
mapper development or sensitivity analysis. The holdout is genuinely un-consulted.

### Why not `FRESH_LINEAGE`

G2L is measurably **adjacent** to GII, which is in construction:

- median best identity of a G2L sequence to a GII construction sequence is **0.326**;
- **48 of 51** G2L sequences sit at or above **0.30** identity — the identity leg of the link rule
  the whole design uses to define "related";
- **2 of 51** reach **≥0.50**, with a maximum of **0.636**;
- the family name itself denotes **group-II-like**.

A frame built on GII being able to map G2L residues is therefore a weaker test than mapping a
genuinely distant lineage. Calling it "unseen lineage transfer" would overstate it.

### The claim this holdout can support

> Transfer of the frozen state→residue mapping to a **held-out RT family within a related
> GII-like lineage**, with no family-specific tuning.

**It may not be described as transfer to an unseen RT lineage**, nor generalised to distant RT
families.

### Why no better candidate exists

The mechanical audit over all 38 family labels found **three** families passing the independence
rule — `G2L` (40/9/1/1), `UG14` (10/6) and `UG25` (19/5/4). G2L was selected by the tie-break
declared *before* the audit ran: criterion 1 (number of components ≥5) ties at 2 for all three;
criterion 2 (size of the second qualifying component) selects G2L at **9**, against UG14's 6 and
UG25's 5.

**UG14 and UG25 are not genealogically closer to construction than G2L in any measured sense** —
they are simply smaller, and their second components (6 and 5 sequences) give a thinner challenge
set. Neither would upgrade the claim to `FRESH_LINEAGE`; both are UG families whose relationship to
construction was not separately audited because the tie-break did not select them. If the operator
prefers a lineage further from GII, **UG25 is the natural alternative** and would need its own
genealogy audit.
