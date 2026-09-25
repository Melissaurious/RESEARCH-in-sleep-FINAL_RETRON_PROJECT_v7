# DECISION — M1 Mestre forensic audit accepted; K0 recorded as `K0_FIRED_RESOLVED_COMPARATOR_ONLY`

Date: 2026-09-19 · Track `m1_mestre_audit` / proposed `m2` · Decided by: operator (Melissa Rios)

Supersede by a new record, never by rewriting.

## 1 · M1 accepted

The M1 forensic audit (`analysis/mestre_audit/REPORT.md`) is accepted as the provenance
record of the historical Mestre 2020 reproduction attempts. That includes the three Ibex
roots audited over SSH on 2026-09-19 (jobs 52089161–52089163, read-only).

## 2 · K0 disposition — `K0_FIRED_RESOLVED_COMPARATOR_ONLY`

K0 (proposed M2 launcher rev-2) fired as worded. The Ibex audit recovered the missing V4
material: pre-trim and trimmed alignments, IQ-TREE logs with exact command lines, model files,
bootstrap replicates, consensus trees and the SLURM producer scripts, all under
`/ibex/project/c2366/RETRONS/rt0_rt7_domain_test_v4_and_tree/mestre/`.

**Resolution:**

- These assets make the historical V4 analysis reproducible. They are to be **preserved,
  registered and reused as comparator assets**, not recomputed.
- They do **not** contain Mestre's original RT0–RT7 extracts, coordinates or MSA. They are
  motif-window alignments of the historical V4 population, which carries the known
  substitute-protein contamination (91 of the 112 rescued substitutes, 3 of them RNA-polymerase
  subunits).
- They therefore **do not supersede MCC-v2** and **must not become the primary Mestre
  reconstruction.**

## 3 · What this does not decide

M2 activation is a separate operator instruction, recorded when M2a–c is activated. **M2d
remains unapproved.**
