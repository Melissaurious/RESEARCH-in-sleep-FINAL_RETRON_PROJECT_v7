# Stage 3A — decision report at the g0/g1/g2 stop point

**Status: PARTIAL, with one criterion VOID.** g0 complete; g1 complete (contract frozen, criteria
declared); g2 partially executed — two criteria tested and falsifying, one void, four not reached.
No catalogue transfer, no predicted structures, no boundary shipped as truth.

## 1 · Can fingers, palm and thumb be identified by positive structural criteria?

**Not yet, and not by the two criteria that were tested.** The element contact graph does not
partition RT chains into three modules: natural k was 4 in 44 % of chains, 6–8 in 39 %, and 3 in
**5 %**. Modularity is *worse* when three is imposed (0.495 vs 0.582). The criterion that would have
tested contiguous three-domain structure directly was degenerate and its run is void. **This is not
evidence that the three regions do not exist — it is evidence that they were not recovered by these
criteria, and one criterion never ran.**

## 2 · Are all three supported equally well?

Not answerable from this session. C4 (β-sheet palm) and C5 (helical-bundle thumb) were designed but
not executed. The prior audit's asymmetry — palm had positive logic, fingers and thumb were residual
flanks — is untouched and remains the standing position.

## 3 · Are they contiguous sequence regions?

**On the evidence obtained, no.** With k forced to 3, median contiguity 0.255, median 8 spans per
module, **0 of 186 modules a single contiguous span**. The classical interval representation is not
supported by contact-graph modularity. The caveat is real: this used one operationalisation, and the
contiguity-aware criterion that would have tested intervals properly is void.

## 4 · Which proteins violate a simple three-domain representation?

All of them, under C1/C2. Structurally the worst offenders carry large accessory content:
`9YFD_A` (1,125 res), `9Z6Z_H`/`9Z6Y_H` (626–628), `26CZ_A` (640), `9I2F_A`/`9I2G_B` (RT–TOPRIM
fusion), `7KFT_C` (Cas6-RT-Cas1), `24NC_A`, plus three constructs with vector-derived fusions
(`9WY8_A` MBP, `9HDO_A` SUMO+MBP, `26CZ_A` SUMO).

## 5 · How stable are assignments across replicate states?

**Not measured.** 13 of 31 groups have more than one deposition and are available for it, but
stability of a partition that is neither three-fold nor contiguous would not answer the stage question.

## 6 · Agreement with published structural annotation?

**Not measured.** The external layer was scoped but not populated. The historical
`reference_boundaries.tsv` remains RED and is retained only as a historical comparison layer.

## 7 · Which old transfer tools can safely be reused?

Unchanged from the asset audit, and nothing new refutes it. Foldseek is now **pinned and rerun**
(`10.941cd33`, sha256 `ce5f08d8…`) and is reusable. FoldMason `4.dd3c235` is installed with logged
historical commands and is reusable as a tool. HHblits/HHsearch capability exists, but the historical
profile database was built from **single-sequence A3Ms** and those depth-1 profiles are **not**
evolutionary profiles. `mkdssp` is **broken here** and was replaced by a validated implementation.
No transfer was attempted, because there is no frozen label to transfer.

## 8 · Ready for predicted-structure validation?

**No.** There is no validated experimental-structure definition to carry over.

## 9 · Ready for sequence or catalogue-scale transfer?

**No.** Emphatically not. Nothing was transferred and nothing should be.

## 10 · What is supported, and what is not

**Supported**

* A clean Stage-3A experimental register: **62 chains, 31 biological RT sequences**, 51 bacterial /
  9 non-LTR / 2 viral, with construct mapping, 1,300 unmodelled internal residues located across 37
  chains, and fusion constructs identified.
* A **validated** secondary-structure instrument: median 0.945 3-state agreement with mkdssp 4.5.5,
  helix recall 1.000, strand recall 0.701 — with the β conservatism stated.
* **1,785 secondary-structure elements** over 62 chains, median 25 per chain, with per-element
  agreement between two independent methods (median 1.000 inside elements).
* A complete, pinned, rerun **all-vs-all structural alignment** (3,844 rows, 62 × 62).
* The finding that **these 31 RT sequences are one structural fold**: group–group max TM median
  0.698, 93 % of pairs ≥ 0.50 — which is why the prospective diversity split collapsed and LOGO was
  adopted.
* The falsifying results in §1 and §3, under the two criteria actually tested.

**Not supported — and not claimed**

* Any fingers/palm/thumb boundary, for any protein.
* Any statement that the three regions are or are not recoverable *in principle*: C3 was void and
  C4–C7 never ran.
* Any comparison with Stage 3B, RT0–RT7, or published annotation.
* Any transfer, to sequence, to predicted structures, or to the catalogue.

## Recommendation

Do not proceed past the experimental-structure gate. The one substantive gap is a working
contiguity-aware domain criterion (C3 in PDP form, with α and the acceptance threshold declared
before scoring). That is a bounded piece of work, and until it exists the honest verdict on the stage
question is **PARTIAL — not demonstrated either way**, not FAIL.
