# RECORD — M2a outcome: STOP (K3 failed); independent review FAIL 4.5/10; budget overrun

Date: 2026-09-19 · Track `m2` · Recorded by the executing session. **Every open item below is
the operator's.** Supersede by a new record, never by rewriting.

Bundle: `results/m2a_reference_reconstruction/` (README `STATUS: UNVERIFIED`; the static checks
in `bundle_valid.sh` pass BS-1..BS-10; `verify.sh` re-derives 12/12 tables byte-identically).

## 1 · Gate outcome

| criterion | outcome |
|---|---|
| K1: reference reconstructable | **INCOMPLETE.** The pruning/mapping check passes (10/10), but it is near-tautological. The **AU sub-criterion was not evaluated**: the clean tree and the AU jobs were cancelled for budget. |
| K2: held-out clade recovery | Numerically met **under the implemented design only**: MCC-v3.1 88.2 % correct / 0.0 % wrong (n = 705); MCC-v2 90.0 % / 0.0 % (n = 778). The design deviates from the launcher (§3). |
| K3: controls | **FAILED.** Residue-shuffled queries were confidently placed at 7.9 % (v3.1) and 19.8 % (v2), against a ≤ 1 % limit. The negative panels passed: 0 / 1,083. No RNAP substitute was placed. |

**→ STOP.** M2c was not run; the smoke script exists but was never executed. M2d is not approved.
No threshold or rule was changed after evaluation replicates were read.

## 2 · Budget — exceeded without prior approval

The total is **64.5 CPU-h against 60 approved (+4.5, 7.5 %)**:
- fixed-topology `LG+F+R10` fits: 13.0 + 8.4;
- replicates: 35.2;
- Ibex tree (cancelled, allocated): 5.7;
- M2b: 1.3;
- raxml-ng full fit: 0.8.

The session estimated the fits and replicates too low, and noticed the overrun only once the
fits completed. The Ibex tree job (52098505) and AU job (52098506) were then cancelled to stop
further spending. This is an accounting failure of the executing session, recorded here rather
than footnoted.

## 3 · Independent review — Codex (read-only), thread `01a0ba36-56f2-7be3-838f-b4b7743ae11c`

The prompt listed only the material and neutral questions; no conclusion was stated to the
reviewer. **Verdict: FAIL. Score: 4.5 / 10.** Findings, condensed. Each was checked against the
code by the executing session, and each is accurate.

| # | label | finding |
|---|---|---|
| 1 | ADVISORY | Historical cleaning is sound and the denominators reconcile. In the v2 ledger, "not extractable" should read "not admitted" (it includes 1 MULTI_CORE). |
| 2 | **REQUIRED** | The 76 source-stated proteins are **not independent validation**: they were used to choose MCC-v3 over MCC-v2. The v3.0 → v3.1 correction is technically right but post-application, and it changed the counts (1,446 → 1,490; 58 → 62/76). "Provenance-driven" must be qualified. |
| 3 | **REQUIRED** | MCC-v3.1 core-QC is **conditional on MCC-v2 extractability**. **75 clean proteins entered without it.** Either amend the contract prospectively, or rebuild under the stated rule. |
| 4 | **REQUIRED** | The leave-out design is **not as declared**: it is not clade-stratified; **calibration and evaluation reuse queries** (v3.1 249/618 unique evaluation taxa; v2 303/702); and the reduced MSAs are row-deletions from an alignment that included the withheld sequences. |
| 5 | **REQUIRED** | The confidence rule is **not calibrated or validated**: τ_LWR defaulted to 0.99 with the calibration shuffled rate at 64 %. **Category 2 is unreachable**, because the implemented rule sends high-pendant placements to `OUTSIDE`. The README's shuffled-failure diagnosis is accurate. |
| 6 | ADVISORY | Controls are correctly reported. "Column-shuffled" (launcher) differs from the implemented residue shuffle. |
| 7 | **REQUIRED** | **K1 cannot be reported PASS**, since the AU test was not evaluated. K2 needs the design qualifier. The STOP remains correct because K3 fired independently. |
| 8 | ADVISORY | The V4 comparator interpretation and the denominator reconciliation (10/11, 9/10, ≤ 3/11, 2–3/11, 4–6/11, 7–9/11) are sound. |
| 9 | **REQUIRED** | Reproducibility is only partial. `verify.sh` covers `a04`/`a05` only, and `run.sh` has not been run end to end; `STATUS: UNVERIFIED` must stay. The reviewer independently regenerated the 12 tables and verified all 235 output hashes. |
| 10 | ADVISORY | The compute arithmetic is correct, but it mixes user+sys time with allocated core-hours. The attribution to host load lacks landed timing evidence. |

## 4 · Changes made in response to the review (before the bundle landed)

These are README wording changes only. No number, table, script or threshold changed.

- The gate headline now reads **STOP**, with K1 **INCOMPLETE** and K2 qualified.
- New README §1a lists the seven implementation-versus-contract departures (findings 2–6).
- The v2 denominator reads "not admitted to the reference (85 not extractable + 1 MULTI_CORE)".
- The compute line states mixed measured/allocated accounting.

No REQUIRED repair was *executed*. Repairs change the design or the extractor, which is an
operator decision.

## 5 · The M2b freeze (independent of the K3 outcome)

`data/derived/m2_mestre/M2B_QUERY_FREEZE.tsv.gz`: 501,561 rows, sha256
`63603e3e692b8ec23a8f9d9455bbcc5ad1c506bcd30f5b8ebd7ae0e6e931dd92`. Extracts:
`M2B_extracts.faa`, sha256 `0734f7b2a7ca8782793eb10df5785fb312301dbe40045e472fb703c2b59e3110`
(both LOCAL ONLY).

Included (MCC-v3.1, modern mode): A 25,454 / 33,670; B1 10,456 / 20,451; B0 9,514 / 24,166;
MULTI 0 / 7,593. Finding 3 (conditional core-QC) applies here too. The freeze inherits it.

## 6 · Open for the operator

1. **Budget.** Retrospectively accept the 4.5 CPU-h overrun, or not.
2. **Whether to repair and re-run M2a, and how.** Minimum repairs implied by the review:
   - clade-stratified, **query-disjoint** calibration and evaluation holdouts;
   - reduced reference alignments rebuilt without the withheld sequences;
   - an explicit prospective decision on MCC-v3.1 core-QC for MCC-v2-non-extractable proteins
     (amend the contract, or rebuild);
   - a confidence rule redesigned before any new evaluation, e.g. with an alignment-quality
     and minimum-pendant component, and evaluated on **fresh** replicates;
   - reconcile category 2 with the status rule;
   - the AU test and the clean tree (checkpoint preserved on Ibex).
   The executing session estimates these at roughly 40–60 CPU-h, to be measured before
   approval.
3. **M2c** stays blocked until M2a passes. **M2d** stays unapproved.
