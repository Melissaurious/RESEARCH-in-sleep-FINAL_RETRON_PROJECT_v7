# rt07_pre_g4_seed_provenance

STATUS: VERIFIED — `run.sh` reruns this audit from the bundle and reproduces every landed table.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **LIGHT** — this is a provenance and leakage audit that closes the last open item in the
old-seed genealogy before `rt07_g4`. It settles no claim. Its findings are binding on g4
through `docs/decisions/2026-09-16_stage2_g4_design_amendment.md`.

---

## 1 · What was measured

**The old seed, resolved.**
`all167.faa` (sha256 `48d48faa…`) = **42 `RETRON_*` + 26 `PDB_*` + 4 `UNIPROT_*` + 95 `CAND_*`**,
167 sequences, all unique. It is the byte-identical concatenation of `anchors72.faa` and
`validated95.faa`.

> `anchors72 = 72/72 of the seed` is **true by construction**, not a contamination discovery.
> The anchors were selected on documented criteria — 42 retrons at `RTDNA_DEMONSTRATED ≥ 0.10`
> measured RT-DNA production, 26 RCSB structures, 4 UniProt entries, membership gate
> `full_RT ≥ 40 bits` calibrated against known non-members. **The real defect is downstream
> reuse of seed components as purported independent validation.**

**CAND95, resolved (95/95).** Minted by `f3a_recruit.py` as `CAND_<family>_<cd-hit cluster>`;
original identifier is an `rt_hash` corpus hash with **no NCBI/UniProt accession**; source is
the 501,561-sequence deduplicated corpus — the same lineage as Stage-1; selection was
completeness tier + not-clipped + 200–900 aa + cd-hit 50% + K largest clusters per coverage
tier, with **no bit score or e-value**. 34 families.

Two properties of CAND95 that constrain g4:
- ⛔ **Annotation existed before inclusion** — palm-HMM domain boundaries, `xxDD` motif strings
  and family calls all arrived with the sequences.
- ⛔ **The 95 were kept by a structural gate** (ESMFold models, ≥3 crystal donors at TM ≥ 0.5,
  pLDDT ≥ 70, chemistry and order). The seed's expansion is **structure-selected**.

**ph38 is a contrast, not a feeder.** 24 crystals re-scanned; **6 disagree** with ph38's own
family labels; the 26 PDB anchors were recruited independently from RCSB and share only **10**
PDB IDs with the 24. 5G2X (LtrA) entered the anchor set *because of* that audit.

**The balanced 25 is a column, not a file**, and **no model was ever built from it**.

## 2 · Leakage, by identity and not only by hash

167 seed sequences searched (mmseqs, `-s 7.5`) against every population g4 might use:

| population | n | exact | ≥90% | ≥70% | ≥50% | ≥30% |
|---|---|---|---|---|---|---|
| `ALIGN_000044` (g2 substrate) | 66 | **1** | 1 | 2 | 18 | 45 |
| Toro 2014 | 742 | 0 | 1 | 9 | 17 | 46 |
| myRT reference | 1,844 | 0 | **29** | 63 | 117 | 166 |
| GOLD171 | 171 | 44 | 47 | 47 | 49 | 75 |
| `anchors72` | 72 | 72 | 72 | 73 | 79 | 132 |
| **Stage-1 catalogue** | 501,561 | **146** | **162** | 163 | 165 | 166 |

Two findings change g4's design:

1. ⛔ **The single seed sequence inside `ALIGN_000044` is `PDB_5G2X_3`, which is exactly
   `L.l.` — LtrA**, the shared coordinate carrier g2 and g3 use. **LtrA cannot be both the
   coordinate system and an independent structural test**, so it is excluded from the g4 PDB
   held-out arm.
2. ⛔ **146 of 167 seed sequences — all 95 CAND — are exact members of the frozen Stage-1
   catalogue, and 162 are ≥90% identical to something in it.** Any Stage-1 sample for g4 must
   be filtered against the old seed **by identity**, not by hash alone.

Also: **29 seed members are ≥90% identical to a myRT reference sequence**, so prior agreement
with myRT was partly built in.

## 3 · Prior models

488 profile HMMs found: **38 built from all167**, 42 from anchors72, 1 from RETRON_SEED (1,500),
1 from Toro 742, 1 from the 24 re-scanned crystals; **43 ship under a name they do not declare**
(`RT17_CORE.hmm` declares `B_span17`). All are `PRIOR / AUDIT / COMPARATOR`. None is training
truth for g4.

## 4 · Counts (BS-5)

    n_attempted:  167 seed sequences x 6 populations = 1,002 leakage comparisons;
                  129 CAND recruitment rows; 488 prior models; 72 anchor provenance rows
    n_succeeded:  95/95 CAND code-level provenance established; 1,002/1,002 comparisons
                  measured; 488/488 models headered and hashed
    n_dropped:    0 - nothing discarded. 1 seed sequence has no mmseqs hit in Stage-1 and is
                  landed as DISTANT_OR_NO_HIT rather than dropped.

## 5 · What this bundle does NOT do

- It does not re-open g3. g3's measurements stand; only the *framing* of `anchors72 = 72/72`
  is corrected, in the decision record.
- It reads Toro 2014 and myRT **only** to measure overlap. Neither defines, seeds, fits or
  thresholds anything, here or in g4.
- It makes no claim about whether any region exists. That is g2's result and g4's question.

## 6 · Reproduction

    $ bash results/rt07_pre_g4_seed_provenance/run.sh
    == 1. seed identity and per-member lineage      167 sequences, 167 unique
    == 2. leakage against every population          6 populations, mmseqs
    == 3. which prior model was built from which subset   488 models
    == 4. CAND_* provenance                         95/95 established
    REPRODUCED: every landed table and manifest is byte-identical on rerun.
