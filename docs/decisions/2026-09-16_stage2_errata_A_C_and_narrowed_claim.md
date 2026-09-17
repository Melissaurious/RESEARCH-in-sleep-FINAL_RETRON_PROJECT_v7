# DECISION — Repair A (errata) and Repair C (narrowed architectural claim)

Date: 2026-09-16 · Track: `rt07` · Status: **applied**

Corrects values in `results/rt07_g4a_repaired/` and `results/rt07_ug5_holdout_gate/` and in the
decision records naming them. **No historical output is overwritten**; corrections live here.

Supersede this record by a new record, never by rewriting it.

---

## Repair A · Errata

Each entry: the superseded value, the verified value, and where the wrong value still appears.

| # | superseded | verified correct | appears in |
|---|---|---|---|
| A1 | "**8.0 is the smallest threshold** eliminating decoy placement" | **FALSE.** The candidate grid was {0, 5, 8, 10, 20, 30, 50} and **skipped 6 and 7**. The maximum *anchor-covering* decoy-domain score is **6.1 bits**, so any threshold above 6.1 — e.g. 7 — also zeroes the decoys. **8.0 was the first grid value that worked, not the smallest working value.** The rule itself is unchanged and still valid; only the minimality claim is withdrawn | `UG5_V3_PREDECLARATION.md` §2 · `ug5_v3_transfer_summary.md` §1 · `2026-09-16_stage2_ug5_v3_placement_rule_and_gate.md` §2 |
| A2 | `envelope_only_v2_rule` = the v2 rule, **21.7%** | **MISLABELLED.** That development row used the **exact aligned HMM span**; v2 used the aligned span **expanded by ±5**. Neither uses HMMER *envelope* coordinates, so the row name is wrong twice over. The true v2-style rate on the development decoys is **23.75%** | `placement_rule_development.tsv` row 1 · `UG5_V3_PREDECLARATION.md` §2 · `ug5_v3_transfer_summary.md` §1 |
| A3 | 2 abstentions, reason `QUALIFYING_DOMAIN_COVERS_NO_ANCHOR` | **WRONG REASON.** Both sequences have **zero qualifying domains** — best domain scores **6.2** (`WP_025510150.1_UG5`) and **5.0** (`ZP_02091461.1_UG5`). The code branched on the count of *all reported* domains rather than *qualifying* domains. Correct reason for both: **`NO_QUALIFYING_DOMAIN`** | `ug5_v3_abstention.tsv` · `ug5_v3_transfer_summary.md` §2 |
| A4 | "all five order metrics saturated at **1.0000**" | **inversion fraction is 0.0000.** The metrics are saturated at their *ideal extrema*, which is 1.0000 for tau, ordered-pair fraction, LMS fraction and monotonicity, and **0.0000** for inversion fraction | `UG5_V3_PREDECLARATION.md` §5 · `2026-09-16_stage2_ug5_v3_placement_rule_and_gate.md` §3 |
| A5 | "**UG5 was never opened** by the development scripts" | **Literally false.** Both call `eligible_by_family()`, which parses the entire mixed `RTs-collection.faa`, UG5 included, before selecting the five development families. **The threshold computation uses only non-UG5 sequences** — the reviewer verified this — but the wording overstates it. Correct statement: *"no UG5 sequence, profile, score or result entered the threshold computation; the mixed collection file is read before the development families are selected."* Separately, **human blinding is not established**: v2's UG5 results existed and motivated the rule class | `UG5_V3_PREDECLARATION.md` header · `placement_rule_development.py` docstring and final print · `order_metric_development.py` |
| A6 | dyad "within the placed span" | the code tests **proximity within 10 residues of any interpolated anchor position**, not containment in the min–max span. An independent span check happens to give the same **60/67**, so the number stands; the description did not match the computation | `ug5_gate_v3.py` · `ug5_v3_transfer_summary.md` §2 |
| A7 | shared core "**7.7 – 44.9%**" of full consensus | **7.5 – 27.5%** (the `LENG`-based value, already corrected in the tables) | `g4a_repaired_comparison_report.md` line 24 — **stale** |
| A8 | `-M 50` = `algorithmic_default`, "not sensitivity tested" | `-M 50` is an **`implementation_choice`** (HHmake's documented default is `-M a2m`) and it **was** sensitivity tested | `g4a_parameter_registry.tsv` — **stale**, contradicts `PREDECLARATION_ADDENDUM_2` §5 |
| A9 | Retrons components "**92 of 95**"; "no independent holdout **at any defensible separation level**" | **93/1/1**; and the supportable wording is "**at the declared 0.30 / 0.50 rule**" | `control/EXECUTION_AUDIT.md` A2 — **stale**, corrected in `PREDECLARATION_ADDENDUM_2` §1 and §6 |

**Nothing in A1–A9 changes a scientific result.** A3 changes a label, A7–A9 are stale copies of values already corrected elsewhere, and the rest are wording. The v3 placement rule, its 0/201 decoy result and the 65/67 placement result are unaffected.

---

## Repair C · The architectural claim is narrowed

The `-M` sensitivity (`g4a_hhmake_M_sensitivity.tsv`) measured, per family, `ALL_PARTNERS`
positions as a fraction of full consensus:

| family | `-M 50` | `-M 60` | `-M a2m` (HHmake's documented default) |
|---|---|---|---|
| Retrons | 21.5% | 18.0% | 3.3% |
| **GII** | **27.5%** | **25.8%** | **13.3%** (115 positions) |
| **DGRs** | 27.3% | 22.7% | **0.0% — zero positions** |
| CRISPR | 17.2% | 15.0% | 8.7% |
| UG3 | 27.3% | 23.6% | 15.1% |
| UG5 | 7.5% | 7.3% | 2.0% |
| **AbiA** | 10.6% | 10.6% | **0.0% — zero positions** |

**Withdrawn:** any family-symmetric or universal shared-core claim.

**Narrowed claim, which is what the evidence supports:**

> A compact **GII-centred** shared RT correspondence frame can be recovered under the tested
> profile match-state definitions (`-M 50`, `-M 60`), but a **family-symmetric** shared-core
> coordinate system is **not robust to the match-state definition**: under HHmake's documented
> default `-M a2m`, DGRs and AbiA retain **zero** `ALL_PARTNERS` positions while GII retains 115.

The `-M 50` frame is therefore **implementation-dependent** and is always reported with the
convention named. The sensitivity is **not hidden**: it is landed, tabulated above, and carried in
every summary of the shared-core result.
