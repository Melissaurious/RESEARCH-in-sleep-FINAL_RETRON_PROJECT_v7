# Results — RT0–RT7 from historical labels to operational states

*Thesis chapter section. Every number is resolved from the landed Stage-2 record at
`94a1a78` (`tables/stage2_resolved_values.tsv`). Figures are in `../figures/`.*

## The historical labels are procedural, and RT0 has no recoverable coordinate

Of 32 region names in 6 held sources, 1 carries a
stated residue boundary; 18 can be derived only by procedure. The alignment from
which the numbered series was later drawn (ALIGN_000044, 66 sequences) carries
0 subdomain annotations. The defining source for RT0, Malik, Burke & Eickbush 1999, could
not be obtained. The held sources give RT0 only an upper bound (the LtrA fragment M1–R85, which
contains it) and an interior residue (A39). They place R85 inside RT1 and state
no RT0|RT1 boundary.

Reconstructing the landmarks independently on 66 reference proteins recovered their
**placement** but not their **number**. Conserved positions (p = 0.0050) and the widest
inter-block gap (p = 0.0050) exceeded column-permutation nulls. The block count did not
(p = 0.6965): 6 blocks in the published frame against 7 in an
independent realignment. A seven-way partition appeared in one frame and not the other. 5 of
6 blocks matched one-to-one across frames (median Jaccard 0.955). Block 4 split into
three (Jaccard 0.410). No block corresponded to RT0.

Earlier project frames were not independent evidence. Of 13 prior claims,
2 reproduced on the same object and frame and 3 were circular or
seed-dependent. The prior anchors lay 100.00% inside their own defining seed. The
prior RT0 was an object mismatch, and RT5 and RT6 collapsed onto one reconstructed region.

## A conserved-state mapper transfers to a fresh lineage

Three design reviews rejected designs that estimated RT0–RT7 architecture directly (Fig. F1). The
accepted instrument maps residues to 150 frozen conserved states. It did not reveal a
universal conserved core. Under `-M a2m`, DGRs and AbiA shared **0** and
**0** states with the other families (Fig. F3), so the instrument is valid under
`hhmake -M 50` only.

In construction, 217 of 219 sequences were committed. Family medians of per-sequence
MAPPED fraction ranged from 0.4733 to 0.9500 (Fig. F2a). The catalytic state
(CAT_STATE 262) agreed with the [YF].DD motif in 0.9857 of construction
occurrences. A first holdout design failed its predeclared monotonicity criterion
(monotone for 31 of 67 sequences (46.3%)), and a residue-transfer gate on G2L was rejected because it
had no frozen score rule and G2L was not a fresh lineage. On the predeclared fresh lineage UG25 (0 exact overlaps with
construction; 0 of 28 sequences meeting the full link rule), both qualifying components
cleared the floor T1 = 0.32 (medians 0.5133 and 0.5933; Fig. F2b). Catalytic
concordance was 26/27 = 0.9630. No synthetic control reached the commitment floor: the maximum was
17 MAPPED anchors against K_MIN = 30, while the weakest real UG25 sequence
had 54 (Fig. F2c). The confirmatory transfer was supported on independent
review (PASS_WITH_REQUIRED_REPAIRS, 7/10).

## The frozen instrument resolves most of the Stage-1 catalogue

Of 501,561 exact RT sequences, 369,381 were eligible (0.736463). Most
exclusions were short sequences (108,439); 23,741 had non-standard residues. All
eligible sequences were processed with 0 tool failures. 354,102 were
inspectable and 15,279 abstained (Fig. F4). Of 55,407,150 state calls,
40,217,506 were MAPPED and 9,944,424 were DELETED_STATE. Of 356,229 sequences with a
MAPPED catalytic state, 0.9653 carried [YF].DD there. Abstention, NO_SUPPORTED_MAPPING
and DELETED_STATE are outcomes of the instrument; they are not evidence of biological absence.

## The conserved-state descriptor is concordant across MyRT-defined strata

Across 36 family strata, the between-family occupancy distances of two
cluster-disjoint halves had a rank correlation of 0.9865. This exceeded the cluster-level
null (p99 0.9066) but not the sequence-level null (p99 0.9906) (Fig. F5). The two
nulls are sensitivity analyses with opposite biases, not bounds on the truth.
6 analyses restricted by MAPPED fraction or collapsed by relatedness
exceeded every sampled replicate of both nulls. With 60 permutations and 13
analyses, this is descriptive, not a calibrated 1% test. Within retrons, DefenseFinder and PADLOC
subtype strata gave 0.8917 and 0.9595 on their own denominators. The label-free arm
was UNDERPOWERED, and 26 of 50 subtype strata lacked the
power to enter.

Because the family labels are essentially MyRT-derived (369,370 of 369,381 records identical to the
raw MyRT label), this result shows **descriptive concordance of the mapper-derived descriptor
across largely MyRT-defined strata**. It does not show independent discovery of biological RT
family structure. The rank statistic uses ordinal tie-breaking; on the positive control, standard
Spearman would give 0.9307 rather than 0.9230.

## RT3, RT4, RT5+RT6 and RT7 correspond operationally on LtrA; RT0 and RT1 remain unresolved

On LtrA, 143 of 150 anchors were MAPPED, spanning residues
97-363. Controls gave 6 passes and 0 failures. Placing
each reconstructed interval on this map gave the final reviewed statuses (Fig. F6; Table T1):

- RT0 — UNRESOLVED / NOT IDENTIFIABLE. No stated extent; 0 anchors in LtrA 1-85.
- RT1 — UNRESOLVED / NOT IDENTIFIABLE. 0 anchors in the reconstructed LtrA 39-61; the nearest MAPPED anchor lies beyond the declared tolerance.
- RT2 — PARTIAL / INTERPRETIVE CORRESPONDENCE. 17 states support LtrA 97-123 of the reconstructed 79-123.
- RT3 — ESTABLISHED OPERATIONAL CORRESPONDENCE, with qualification. 22 states, LtrA 126-166; prior-frame agreement corroborates placement but is not independent replication.
- RT4 — ESTABLISHED OPERATIONAL CORRESPONDENCE, with frame-instability qualification. 42 states, LtrA 170-230; one-to-one in the primary frame, split into three in the independent frame (Jaccard 0.410).
- RT5 — ESTABLISHED OPERATIONAL CORRESPONDENCE, as the joint RT5+RT6 region. 34 states, LtrA 311-347; the catalytic state maps to LtrA 306 (YADD).
- RT6 — PARTIAL / INTERPRETIVE CORRESPONDENCE, jointly with RT5 only. No state can be attributed to RT6 rather than RT5.
- RT7 — ESTABLISHED OPERATIONAL CORRESPONDENCE, with narrowed wording. 6 states, LtrA 356-361, immediately N-terminal of the source-described proteolytic landmark R364/R365.

| label | reference interval on LtrA (g2 block; RT0: source upper bound) | frozen-state support | final reviewed status |
|---|---|---|---|
| RT0 | 1-85 | none - 0 frozen anchor states map inside the reference interval; anchor reach is LtrA 97-363 | UNRESOLVED |
| RT1 | 39-61 | none - 0 frozen anchor states map inside the reference interval; anchor reach is LtrA 97-363 | UNRESOLVED |
| RT2 | 79-123 | 17 states (107-133) -> LtrA 97-123 | PARTIAL |
| RT3 | 126-166 | 22 states (136-177) -> LtrA 126-166 | ESTABLISHED (with qualification) |
| RT4 | 170-230 | 42 states (181-241) -> LtrA 170-230 | ESTABLISHED (with frame-instability qualification) |
| RT5 | 304-347 | 34 states (267-301) -> LtrA 311-347 | ESTABLISHED (named jointly as RT5+RT6) |
| RT6 | 304-347 | 34 states (267-301) -> LtrA 311-347 | PARTIAL (jointly with RT5 only) |
| RT7 | 356-361 | 6 states (310-315) -> LtrA 356-361 | ESTABLISHED (with narrowed wording) |

These are LtrA-local interpretation-layer correspondences. The production instrument emits
`state_id` only. Both terminal analyses passed independent review with zero blockers (g6:
PASS_WITH_REQUIRED_REPAIRS, 6/10, 0 blockers; g7a: PASS_WITH_REQUIRED_REPAIRS, 7/10, 0 blockers). All eight statuses were preserved, and the 13 required
repairs changed wording only.
