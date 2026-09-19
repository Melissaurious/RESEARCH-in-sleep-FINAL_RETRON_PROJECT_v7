# Discussion and limitations — Stage 2

*Thesis chapter section. Source of record `94a1a78`.*

## What Stage 2 changes

Before Stage 2, "RT0–RT7" was used as if it were a coordinate system. Stage 2 showed that it is
a set of historical, procedurally defined labels. Their placement can be reconstructed. Their
number depends on the alignment frame. RT0 has no coordinate in any held source. The project
therefore separated two things that had been conflated: the historical labels, and a frozen
operational coordinate system of 150 conserved profile-HMM states that is validated,
versioned (`rtmap-1.0.0/53a1e738a19b3896`) and applied to 369,381 catalogue RTs. The historical
labels connect to this system only through an explicit, reviewed bridge on one protein. They
never enter production output.

## Why UNRESOLVED and PARTIAL are informative

The two UNRESOLVED statuses are precise negative findings. RT0 and RT1 are unresolved for two
named, independent reasons. Historically, no held source states their boundary, and the
defining source for RT0 is not held. Instrumentally, the frozen anchors reach only LtrA
97-363, which starts C-terminal of both labels' reference intervals. Each reason names the evidence that could change the status: the primary
source, or an instrument with N-terminal anchors validated to the same standard. Assigning
coordinates instead — from inherited frames shown to be circular, or from a proteolytic fragment
that *contains* RT0 rather than delimiting it — would have attached an unsupported label to every
RT in the catalogue. The PARTIAL statuses are also specific. RT2 extends past the instrument's
reach. RT6 is inseparable from RT5 in the reconstruction. Neither says the region is doubtful.
Keeping these statuses is also what gives weight to the ESTABLISHED ones: the same predeclared
rules that refused RT0 and RT1 accepted RT3, RT4, the joint RT5+RT6 region and RT7.

## What the family-level analysis does and does not show

The mapper-derived descriptor is reproducible across cluster-disjoint halves of the catalogue
and concordant with the family structure given by MyRT and, within retrons, by DefenseFinder and
PADLOC. The strata are almost entirely MyRT-defined, and grouping and measurement share
sequence/profile modality. The result is therefore descriptive concordance, not independent
discovery of family structure. It supports using the frozen `state_id` system descriptively,
with its occupancy caveats, in later structural work. It does not support reassessing
classification.

## Limitations

- **One reference protein.** All RT0–RT7 correspondences are LtrA-local.
- **N-terminal blind spot** of the instrument (anchors cover LtrA 97-363).
- **Validation scope.** Transfer is shown to one fresh lineage under `hhmake -M 50`. Not shown:
  specificity against unrelated natural proteins, residue accuracy against external truth, or
  robustness to the match-state convention.
- **Frame dependence** of block number and of RT4's cardinality.
- **g6 statistics.** Ordinal tie-breaking; nulls too small for 1% tails; no multiplicity control;
  26 of 50 subtype strata excluded; post-hoc procedural
  additions disclosed.
- **Human input audit** is PENDING for the landed bundles.

## Outlook

Stage 2 is closed as workflow closure for the current instrument and evidence set, not as
complete historical recovery. The next step for RT0 and RT1 is primary evidence, not further
inference. Stage 3 proceeds independently with its own structural definitions. It may use the
bridge and the `state_id` system descriptively, but it may not present them as resolving any
historical label.
