# Stage 3A · g2r — AMENDMENT 2 (response to Codex review R2, B1–B8)

**Frozen before** any benchmark PDP output, any RT SS concordance, any RT C3r run and any C4–C7 score.
Amendment 1 governs where this document is silent; where the two differ, this one governs.
Review text: `review/CODEX_REVIEW_R2.md` (FIX_FIRST).

No PDP constant, no C4/C5/C4b threshold and no acceptance bar value was changed.

| # | defect | fix |
|---|---|---|
| B1 | one parser exception aborted the batch | `RunPDP.java`: each input runs in its own try/catch. A failure reports `PARSER_FAIL:<exception>` for that chain and the batch continues. In CATH scoring the chain gets count-incorrect and overlap 0; in C4 it is INSTRUMENT_LIMITED:pdp. Recompiled (`drv3`). On the 12 dry-run chains the per-residue output is byte-identical to the previous driver. |
| B2 | E1 required ≥ 2 domains for 1-domain discontinuous chains | E1 is now computed over discontinuous-stratum chains with **≥ 2 CATH domains**. Bar unchanged (0.60). All 33 discontinuous benchmark chains have ≥ 2 CATH domains, so n is unchanged. |
| B3 | endpoint fallback ignored insertion order | Missing endpoints resolve under the total order `(seqnum, icode)`, with `''` < `A` < `B` …. A segment whose resolved start follows its resolved end is dropped and logged (`seg_fail`). |
| B4 | pydssp not break-aware beyond donor mask | Route-B input is the canonical order. Incomplete-backbone residues become NaN rows. **Six NaN spacer rows** are inserted at every chain break; 6 exceeds pydssp's longest turn offset of 5. NaN geometry yields no H-bond, so no turn, bridge neighbourhood, local mask or amide-H placement spans a break. pydssp itself is unmodified. Dry run: route-B states identical on 12/12 chains, 0 changes. |
| B5 | cohort / coverage / degenerate-κ loopholes | `ss_concordance.py` asserts that the SS directory equals the frozen cohort `tables/g2r_rt_cohort.txt` (62 chains) with no duplicates. A chain with zero common residues fails the chain gate. κ is undefined exactly when both routes are constant and identical (all-S or no-S); that counts as concordant. **New population condition:** ≥ 0.90 of the cohort must pass the chain SS gate, otherwise C4/C5/C4b are INSTRUMENT_LIMITED. |
| B6 | verdict could not emit INSTRUMENT_LIMITED | `g2r_units.py` takes the primary instrument's CATH gate table as a required argument, and reads the population SS gate. If either failed, every verdict line is `INSTRUMENT_LIMITED`. The report header states both instrument statuses. Dry run confirmed that a CATH failure propagates. |
| B7 | pinned alignment only reported | `g2r_ava.py` aborts, writing nothing, unless row count, key set, starts/ends and aligned strings all equal the pinned g2 table. Output rows are sorted, because foldseek threads reorder them. Two consecutive runs are byte-identical. `tables/g2r_foldseek_ava.tsv` sha256 `ecf1ee4c…` has the same contents as the amendment-1 table, re-sorted. `g2r_units.py` also asserts that alignment walks end at qend/tend. |
| B8 | sheet-label ties; one-directional bridge test | A tie between sheet labels in a strand piece gives *no sheet*, which is conservative. The hairpin bridge test is now bidirectional: a bridge partner of either strand lies in the other. |

**Non-blocking items adopted:**
- `--exposed` is required and non-empty. The exact invocation is archived with the results.
- ShortSegmentRemover (drop a domain with total < 35 or all segments < 30) is part of the pinned method description.
- The "PDP output with a discontinuous domain" statistic is secondary. It can be inflated by PDP_ABSENT residues and is labelled as such.
- C6 is a *conditional* recurrence (both chains called). Prevalence is carried by the all-chain call rate.
- BJ-p4 classes and the `drv3` driver class are hashed in `tables/biojava_classpath_sha256.txt`.
