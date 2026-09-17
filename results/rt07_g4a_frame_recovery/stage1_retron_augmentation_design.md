# Stage-1 retron augmentation — DESIGN ONLY, no sample drawn

**No Stage-1 sequence was read, clustered or scored in g4a.** This is the frame under which
Stage-1 could later supply retron diversity, written now so it exists before it is needed.

## Why augmentation is needed

myRT holds **95 eligible full-length-source retron proteins**. g4a drew **90** of them
(derivation 50, development 14, challenge 26), leaving **5 unused**. That is enough to analyse
retrons under the same rules as every other family — which g4a did — but **not enough for an
independent retron evaluation set**, because the challenge sequences come from the same 95 as the
derivation profile.

Stage-1 carries **78,292 retron exact RTs**, of which **54,679** are `all_complete`. The depth
exists; the question is how to draw from it without circularity.

## The circularity that must be avoided

Stage-1's `Retron` label is the myRT `RVT-Retrons` model's own output under a documented collapse.
Drawing a retron sample *by that label* and then using it to evaluate a retron mapper tests the
mapper against the labelling instrument, not against biology.

**Consequence:** the label may select the sampling frame; it may never serve as the truth against
which anything is scored. Tool labels are strata (`§14`), not ground truth.

## Sampling frame

| field | specification |
|---|---|
| unit | exact RT, sha256 over residues |
| frame source | landed Stage-1 metadata only — `rt_family_baseline_v1`, `rt_cds_recovery_v1` — joined on the `Retron` file label |
| inclusion | `V-RT-SINGLE`; `completeness_class = all_complete`; not clipped; no contig edge |
| length | within the retron family's own landed median ± a declared factor, NOT an inherited absolute window |
| **primary stratifier** | **sequence-diversity cluster**, not tool agreement — cluster the eligible retron keys and sample across clusters so the draw spans diversity rather than abundance |
| exclusion, derivation leakage | drop any sequence at or above a declared identity **with declared bidirectional coverage** to any of the 90 myRT retrons used in g4a |
| exclusion, near-neighbour | drop any sequence at or above the same identity to an already-drawn sample member, so the sample is internally diverse |
| retained strata | `myrt_raw_label`, `stage1_collapsed_label`, `padloc_support`, `defensefinder_support`, `tool_agreement_class`, `source_database`, `taxonomy`, `system_context` |
| max N | a declared ceiling in the low thousands at most; the realised n is reported, never back-filled toward the ceiling |
| seed | declared before the draw |
| compute boundary | keys drawn from metadata; sequences extracted for drawn keys only; **no index built over the full catalogue and no search against it as target** |

## How the strata are used

As **reporting strata and robustness checks**, never as truth. The permitted claim shape is:

> Among sequences that tool X classified as family F, feature A was mapped in Y% of inspectable
> sequences.

and never:

> Agreement with tool X validates feature A.

`padloc_support` / `defensefinder_support` / `tool_agreement_class` are especially useful as
**disagreement** strata: whether mapping behaves differently where the tools disagree is an
interesting measurement about instrument scope, and it is not a validation.

## What this would and would not buy

**Would:** a retron challenge set genuinely independent of the 90 myRT retrons that built the
profile; enough depth for retron subtype structure; taxonomic and source-database breadth that 95
curated references cannot have.

**Would not:** independent boundary truth, independent family truth, or a licence to call
non-detection absence. Those remain unestablished regardless of sample size.

## Trigger

Draw this sample only when a gate needs an independent retron evaluation population — i.e. when a
retron-focal mapper is being evaluated, not before. g4a did not need it and did not draw it.
