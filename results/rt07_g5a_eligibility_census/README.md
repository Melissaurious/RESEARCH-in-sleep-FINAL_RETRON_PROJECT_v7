# rt07_g5a_eligibility_census

STATUS: VERIFIED — `verify.sh` regenerates every landed table and every derived file into a
temp tree and compares them; the census is a pure function of its inputs and the frozen
eligibility rule, so the comparison is byte-for-byte (gzip outputs are written with the
timestamp pinned so their sha256 is a content hash).

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

    n_attempted:  501561   exact RT records read from the Stage-1 catalogue
    n_succeeded:  369381   eligible under the frozen rule — THE g5 DENOMINATOR
    n_dropped:    132180   ineligible, every one retained with an exact reason

Weight **ENGINEERING / CENSUS**. This gate maps nothing and concludes nothing biological.
It fixes a denominator.

---

## 1 · The one number

**`G5_ELIGIBLE_N = 369,381`**

This, not 501,561, is the population the frozen mapper is applied to in `g5`, and it is the
denominator every g5 and g6 rate is taken over. 26.35 % of the exact-RT catalogue is outside
the population the instrument has ever been exercised on.

| | |
|---|---|
| total exact RT sequences | 501,561 |
| unique `rt_hash` | 501,561 (the catalogue is one row per exact sequence) |
| duplicate identifiers | **0** |
| eligible | **369,381** (0.7365) |
| ineligible | 132,180 |
| — `BELOW_MIN_LENGTH` (< 250 aa) | 108,439 |
| — `NON_STANDARD_RESIDUE` | 23,741 |
| — short records *also* carrying a non-standard residue | 4,000 (secondary flag) |

This census is where the eligibility rule **selects the population**. It runs once here; g5
reads the resulting partition and never re-applies it. (The production runner separately
re-validates its own input on every shard, as its own fail-closed contract; on this partition
it rejected 0 records.)

The rule is imported from the frozen production package, not restated:
`MIN_AA=250; ALPHABET=ACDEFGHIKLMNPQRSTVWY; CLEAN=strip[-.]upper,rstrip*`, applied by
`rtmap.run_mapper.validate` — the same function the production runner calls. Reason priority
is the frozen priority: length is tested before the alphabet, so every `NON_STANDARD_RESIDUE`
record is ≥ 250 aa, and the 4,000 overlapping records are reported as a secondary flag so the
priority does not hide them.

## 2 · Reconciliation

    369,381 + 132,180 = 501,561

asserted in code, not just reported: no identifier appears on both sides, no identifier is
missing from both, and the catalogue FASTA's hash set is identical to the canonical parquet's.
`rt_aa_len` in the canonical parquet agrees with the cleaned length this census computed on
**all 501,561** records — 0 disagreements.

## 3 · Length distribution

| population | n | min | p1 | p5 | p25 | median | p75 | p95 | p99 | max | mean |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all exact RT | 501,561 | 20 | 72 | 124 | 272 | 384 | 468 | 638 | 1057 | 10449 | 386.5 |
| eligible | 369,381 | 250 | 255 | 276 | 347 | 423 | 494 | 643 | 1061 | 4299 | 441.0 |
| ineligible | 132,180 | 20 | 49 | 77 | 139 | 191 | 237 | 594 | 1044 | 10449 | 234.1 |
| — below min length | 108,439 | 20 | 46 | 74 | 128 | 174 | 212 | 242 | 248 | 249 | 167.6 |
| — non-standard residue | 23,741 | 250 | 254 | 276 | 358 | 458 | 622 | 1063 | 1466 | 10449 | 538.2 |

The non-standard-residue population is **long**, not short (median 458 aa). It is excluded on
alphabet, not on length, and the two exclusions are different populations.

| length bin | total | eligible | ineligible | eligible fraction |
|---|---|---|---|---|
| < 100 | 14,780 | 0 | 14,780 | 0.0000 |
| 100–149 | 24,099 | 0 | 24,099 | 0.0000 |
| 150–199 | 33,384 | 0 | 33,384 | 0.0000 |
| 200–249 | 36,176 | 0 | 36,176 | 0.0000 |
| 250–299 | 39,214 | 36,725 | 2,489 | 0.9365 |
| 300–399 | 120,456 | 114,550 | 5,906 | 0.9510 |
| 400–499 | 136,883 | 131,242 | 5,641 | 0.9588 |
| ≥ 500 | 96,569 | 86,864 | 9,705 | 0.8995 |

## 4 · Denominator warning — eligibility is NOT uniform across strata

This is the reason the census exists. Flagged where the eligible fraction is more than 0.05
below the catalogue-wide 0.7365:

| stratum | total | eligible | fraction | vs catalogue |
|---|---|---|---|---|
| **`mixed_or_codon_evidence`** completeness | 31,832 | 3,591 | **0.1128** | −0.6237 |
| **`MULTI`** | 7,598 | 2,825 | **0.3718** | −0.3647 |
| `all_partial` completeness | 127,473 | 73,136 | 0.5737 | −0.1627 |
| RVT-UG18 | 299 | 168 | 0.5619 | −0.1746 |
| RVT-UG11 | 1,292 | 740 | 0.5728 | −0.1637 |
| RVT-CRISPR-like | 3,168 | 1,837 | 0.5799 | −0.1566 |
| RVT-UG4 | 4,705 | 2,972 | 0.6317 | −0.1048 |
| RVT-AbiA | 11 | 7 | 0.6364 | −0.1001 |
| RVT-G2L | 1,988 | 1,292 | 0.6499 | −0.0866 |
| **RVT-GII** | 256,624 | 176,126 | 0.6863 | −0.0501 |

**This is a downstream interpretation warning and nothing else.** It says which strata lose
the most records to the eligibility rule before the mapper ever runs. It does **not** say the
mapper is biased, inaccurate, or that these families lack anything. Any g6 comparison across
these strata must use each stratum's own censused eligible denominator, and must state that
the excluded fraction differs between them.

## 5 · What is landed where

Small, in this bundle (`tables/`): the census summary, length distribution and bins, the
ineligibility-reason table, the global duplicate-identifier census (0 rows), eligibility by
Stage-1 collapsed family, raw MyRT family, MULTI status, completeness class, view, source
database, system type, taxonomic domain and tool-support pattern, and the `< 250 aa`
breakdowns by family, raw family, source database, system type and MULTI status.

Large, under `data/derived/rt07_g5a/` (gitignored by project convention; hashes recorded in
`tables/g5a_census_summary.tsv` and `PROVENANCE.md`):

| file | rows | bytes |
|---|---|---|
| `g5a_eligibility_partition.tsv.gz` | 501,561 | 20,084,071 |
| `g5a_eligible_ids.txt.gz` | 369,381 | 13,514,830 |
| `g5a_ineligible_records.tsv.gz` | 132,180 | 6,937,603 |

The ineligible table is a **full record**, not a count: `rt_hash`, sequence id, cleaned
length, exact reason, the non-standard secondary flag, the reason detail, raw MyRT family
label set, Stage-1 collapsed family, MULTI status, completeness class, view, source databases,
system types, taxonomic domains and phyla, `n_species`, PADLOC / DefenseFinder / MyRT support,
and record/locus/genome counts. Nothing was silently dropped.

## 6 · What this bundle does not say

* Not that short sequences are biologically incomplete or truncated.
* Not that any family genuinely lacks RT architecture.
* Not that a metadata label is correct, or that tool support is truth.
* Not that the 250 aa floor is the right biological cutoff — it is the floor the instrument
  was calibrated and validated under, and it is **unchanged** by this census.
