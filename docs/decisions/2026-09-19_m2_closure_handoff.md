# DECISION / HANDOFF — M2 closed after a stopped M2a validation attempt

Date: 2026-09-19 · Track `m2` · Decided by: operator (Melissa Rios). Supersede by a new record,
never by rewriting.

## 1 · Operator decisions

- **Budget.** The 4.5 CPU-h overrun is accepted retrospectively as an execution-estimation
  error.
  - Actual usage stays recorded as **64.5 CPU-h** against 60 approved. That total mixes
    user+sys time with 5.7 allocated core-hours from Ibex.
  - The Ibex tree and AU jobs (52098505, 52098506) were **cancelled once the overrun was
    detected**.
- **M2a** is closed as a **stopped / failed validation attempt**. It is **not repaired and not
  re-run**.
- **M2c and M2d are not run.** The M2c smoke script exists but was never executed.
- A repaired M2a will be reconsidered **only after the updated project-synthesis review**
  decides whether historical-classification reconstruction is needed for the final
  thesis/paper programme.

## 2 · What the attempt showed — `results/m2a_reference_reconstruction/` (commit `b05934f`)

| observation | result | standing |
|---|---|---|
| Recovery of withheld clean historical references | confidently placed in the **correct** published clade: MCC-v3.1 **88.2 %** (n = 705), MCC-v2 **90.0 %** (n = 778); **0 % confidently placed in a wrong clade**, in every clade | a **positive observation**, qualified by design defects D1–D2 below; not a validated K2 pass |
| Residue-shuffled sequence control (K3) | confidently placed at **7.9 %** (v3.1) and **19.8 %** (v2), against a ≤ 1 % limit | **FAILED**. The confidence rule does not reject non-homologous input |
| Non-retron controls (K3) | **0 / 1,083** confidently placed (Toro-2014 non-retron extracts + catalogue RTs with no retron evidence); no RNA-polymerase substitute reached placement | **PASSED**. Protection comes mainly from the upstream MCC-v3.1 extraction gate |
| K1, reference reconstructable | pruning/mapping check 10/10 (near-tautological); **AU test and clean ML tree not evaluated** (cancelled for budget; checkpoint kept on Ibex at `/ibex/user/rioszemm/experiments/m2a/tree/`) | **INCOMPLETE** |

**Scope of the failure.** This is the failure of **one placement-confidence protocol**, on one
reconstructed reference, under a defective validation design. It is **not** evidence that
modern retron phylogenetics or placement is impossible. It also does not say anything about
whether modern retrons fit the historical classification: no modern sequence was placed.

## 3 · The five design defects (Codex review, thread `01a0ba36`; verified in code)

- **D1 — Holdout design.** The holdout is not clade-stratified, and calibration and evaluation
  replicates reuse queries: v3.1 249/618 unique evaluation taxa, v2 303/702.
- **D2 — Reference independence.** Each reduced reference alignment is a row-deletion from an
  alignment built *with* the withheld sequences.
- **D3 — Conditional core-QC.** MCC-v3.1 applies the ≥ 70 % MCC-v2-core check only when MCC-v2
  also extracts, so 75 clean proteins bypassed it. The contract text did not say so, and the
  M2b freeze inherits the same behaviour.
- **D4 — Validation independence.** The 76 source-stated Toro proteins were used to *select*
  MCC-v3. They are not independent validation of it; the v3.0 → v3.1 correction was also
  post-application.
- **D5 — Confidence rule.** It is uncalibrated and unvalidated: τ_LWR defaulted to 0.99, with
  the calibration shuffled rate at 64 %. It also makes interpretation category 2 ("deeper
  expansion") unreachable, because high-pendant confident placements are labelled `OUTSIDE`.

## 4 · Minimum repair set for any future M2a rerun

All six must be declared **before** any new evaluation replicate is read:

1. **Holdouts:** clade-stratified, and **query-disjoint** between calibration and evaluation
   (fixes D1).
2. **Reduced references:** each replicate's alignment rebuilt from the retained sequences only;
   withheld sequences enter solely through the query route (fixes D2).
3. **Core-QC:** a prospective decision, either amend the contract to state the conditional
   behaviour or require core-QC for every extract. Re-freeze the extractor and rebuild the
   reference and the M2b table accordingly (fixes D3).
4. **Validation set:** fresh, independent validation of the chosen extractor, or explicit
   relabelling of the 76-protein result as method selection (fixes D4).
5. **Confidence rule:**
   - redesign it, for example with an alignment-retention floor and a minimum-pendant or
     query-to-reference identity component;
   - calibrate it on calibration replicates only;
   - evaluate it on **fresh** replicates, with the shuffled control;
   - reconcile category 2 with the status rule (fixes D5).
6. **K1:** complete the clean `LG+F+R10` tree and the AU test (the Ibex checkpoint can resume).

Cost: about 40–60 CPU-h, to be **measured by smoke run before approval**. Governed by a new
launcher revision and a new bundle id; the landed bundle is write-once.

## 5 · Assets preserved for a future decision

| asset | location |
|---|---|
| M2a bundle (as landed, reviewed) | `results/m2a_reference_reconstruction/` |
| frozen extractor MCC-v3.1 | `analysis/mestre_audit/scripts/m10_mcc_v3_freeze.py`, `analysis/mestre_audit/m2_design/mcc_v3/` |
| M2b query freeze (defect D3 applies) | `data/derived/m2_mestre/M2B_QUERY_FREEZE.tsv.gz` (sha256 `63603e3e…dd92`, local only) |
| M1 forensic audit, Toro crosswalk, Ibex audit | `analysis/mestre_audit/` |
| launcher (rev-4) | `launchers/LAUNCHER_M2_historical_classification_expansion.md`; **closed by this record** |
| records | `docs/decisions/2026-09-19_*` (M1/K0, MCC-v3 adoption, M2a outcome and review, this closure) |
