# `rtmap-schema-1.0` — the frozen production output schema

Four files per shard. `code/rtmap/schema.py` is the machine-readable definition; this
document is its rationale. Changing any column order or name is a schema-version change.

```
<shard>.states.tsv       one row per (sequence, frozen conserved state) — 150 rows/sequence
<shard>.sequences.tsv    one row per sequence — summaries, catalytic block, architecture
<shard>.failures.tsv     one row per record that produced no scientific statement
<shard>.provenance.tsv   one key/value record per run
<shard>.DONE             input sha256 + instrument digest + every output hash;
                         a shard is complete only when all of them VERIFY
```

---

## 1 · Rules that downstream code may not break

1. **The four per-state call states are never collapsed to present/absent.**
2. **Only `MAPPED` is positive evidence.** `AMBIGUOUS` and `UNSUPPORTED` are reported and
   never counted toward callability. This is the frozen rule.
3. **`DELETED_STATE` is a statement about the alignment path, not about the biology.** The
   residue is absent *from the match column*. "This protein lacks this region" is a
   different claim and g6 may not derive it from this one.
4. **The catalytic block has its own denominator.** `CAT_STATE` 262 is not one of the 150
   anchors. `n_states_total` counts anchors only. The two are never pooled.
5. **No historical RT0–RT7 label appears in any production column.** They live in a separate
   crosswalk joined on `state_id`, and every row of it is `UNRESOLVED`.
6. **`NO_SUPPORTED_MAPPING` is not biological absence.** See §4.

---

## 2 · `states.tsv`

| column | meaning |
|---|---|
| `rt_hash` | sha256 of the cleaned residue string — the join key across shards |
| `sequence_id` | identifier as it appeared in the input FASTA |
| `mapper_version` | `rtmap-1.0.0/<16 hex>` |
| `state_id` | frozen conserved state = HMM match state, 1…471 |
| `anchor_index` | 1…150, position of this state in the frozen anchor set |
| `call_state` | `MAPPED` / `AMBIGUOUS` / `UNSUPPORTED` / `DELETED_STATE` |
| `sequence_residue_index` | 1-based residue index; empty when `DELETED_STATE` |
| `amino_acid` | residue; `-` when `DELETED_STATE` |
| `posterior` | **lower bound** of the HMMER PP band; empty when `DELETED_STATE` |
| `support` | the per-state evidence weight: `posterior`, or `0.00` when there is none |
| `reason_code` | why this state carries this call |

The posterior is the lower bound of HMMER's PP band (`*` → 0.95, digit *d* → *d*·0.1−0.05),
so a call is never credited with more confidence than the encoding guarantees. This is the
frozen mapper's own convention.

### Per-state call states

| call | condition | evidence? |
|---|---|---|
| `MAPPED` | residue in the match column, posterior ≥ `PP_HI` (0.75) | **yes** |
| `AMBIGUOUS` | residue in the match column, `PP_LO` ≤ posterior < `PP_HI` — a competing alignment path is credible | no |
| `UNSUPPORTED` | residue in the match column, posterior < `PP_LO` (0.50) — the chosen path is a minority against all alternatives combined | no |
| `DELETED_STATE` | the match column is a gap on this sequence's path | no |

### Reason codes

| `reason_code` | call |
|---|---|
| `OK_POSTERIOR_AT_OR_ABOVE_PP_HI` | `MAPPED` |
| `POSTERIOR_BETWEEN_PP_LO_AND_PP_HI` | `AMBIGUOUS` |
| `POSTERIOR_BELOW_PP_LO` | `UNSUPPORTED` |
| `POSTERIOR_UNAVAILABLE` | `UNSUPPORTED` |
| `MATCH_COLUMN_GAPPED` | `DELETED_STATE` |

---

## 3 · `sequences.tsv`

**Identity and instrument:** `rt_hash`, `sequence_id`, `sequence_length`, `mapper_version`,
`profile_version`, `match_state_definition`, `family_metadata`.

`family_metadata` carries a Stage-1 stratum label when one is supplied via `--metadata`, and
`NOT_SUPPLIED` otherwise. It is a **grouping variable, never validation truth** — see
`STAGE1_METADATA_ROLE.md`.

**Anchor block**, denominator `n_states_total`: `n_states_total`, `n_mapped`,
`n_ambiguous`, `n_unsupported`, `n_deleted`, `mapped_fraction`, `verdict`, `reason`,
`domain_bitscore`, `domain_evalue`, `inspectability_status`.

`mapped_fraction` = `n_mapped` / `n_states_total`, matching `pct_mapped` in the landed
construction and UG25 tables. `verdict` and `reason` come from the frozen
`classify_sequence` and are unchanged: `MAPPED` / `OK`, or `ABSTAIN` with
`NO_QUALIFYING_DOMAIN` (bitscore < `S_MIN`, or no domain) or
`INSUFFICIENT_SUPPORTED_ANCHORS` (`n_mapped` < `K_MIN`).

`domain_bitscore` and `domain_evalue` are computed **per sequence** — database size 1 — so
neither depends on which other sequences shared the shard. See `PRODUCTION_SPEC.md` §3.

**Catalytic block**, separate denominator, never pooled with the anchor block: `cat_state`,
`cat_call_state`, `cat_residue_index`, `cat_residue`, `cat_motif_class`, `cat_support`,
`cat_motif_window`, `n_dyad_motifs_in_sequence`.

| `cat_motif_class` | meaning |
|---|---|
| `CATALYTIC_CONFIRMED` | `CAT_STATE` `MAPPED` and the residue begins `[YF].DD` |
| `CATALYTIC_SUBSTITUTED` | `CAT_STATE` `MAPPED`, residue does not begin `[YF].DD` |
| `CATALYTIC_AMBIGUOUS` | `CAT_STATE` `AMBIGUOUS` |
| `CATALYTIC_UNSUPPORTED` | `CAT_STATE` `UNSUPPORTED` |
| `CATALYTIC_STATE_DELETED` | `CAT_STATE` match column gapped |

"Confirmed" means **motif concordance at a state**. It is not independent residue truth, and
`n_dyad_motifs_in_sequence` is carried precisely so a reader can see how many other `[YF].DD`
occurrences the protein has.

**Architecture block**, retained for g6 and never used as a filter: `n_insertion_runs`,
`total_inserted_residues`, `max_insertion_run`. Insertions relative to the profile are
explicit, as the frozen mapper reports them.

---

## 4 · Production inspectability status

A **relabelling** of the frozen `(verdict, reason)` pair, split by the frozen `T1`. It
introduces **no predicate of its own** — the map is a bijection onto the frozen reason codes.

An earlier version defined `AMBIGUOUS_MAPPING` by an invented comparison,
`n_ambiguous + n_unsupported > n_mapped`. The independent packaging review correctly
identified that as a new classification rule — and one that could fire with zero `AMBIGUOUS`
calls. It was **removed**, not defended (repair R5).

| status | condition | what it means |
|---|---|---|
| `MAPPABLE` | `verdict` = `MAPPED` and `mapped_fraction` ≥ `T1` (0.32) | inside the callability range the instrument was calibrated on |
| `PARTIAL_MAPPING` | `verdict` = `MAPPED`, `mapped_fraction` < `T1` | callable, below the construction floor. **Retained, not filtered.** |
| `AMBIGUOUS_MAPPING` | `ABSTAIN` / `INSUFFICIENT_SUPPORTED_ANCHORS` | the sequence **has** a qualifying domain — the instrument recognises it — but fewer than `K_MIN` anchors reached `PP_HI`. Support was the limiting factor, not recognition. Inspect the `AMBIGUOUS` / `UNSUPPORTED` counts and the per-state rows. **Not absence.** |
| `NO_SUPPORTED_MAPPING` | `ABSTAIN` / `NO_QUALIFYING_DOMAIN` | no domain reported, or bitscore below `S_MIN`. See below |
| `INPUT_INVALID` | never reached the mapper | no scientific statement is made |
| `TOOL_FAILURE` | `hmmalign`/`hmmsearch` failed, or a fail-closed assertion fired | no scientific statement is made |

An unmapped frozen `(verdict, reason)` pair fails closed rather than falling through to a
default, so the relabelling cannot silently stop being a bijection.

**`NO_SUPPORTED_MAPPING` IS NOT A BIOLOGICAL ABSENCE CLAIM.** It says this instrument, under
this GII-derived profile and this match-state convention, did not find `K_MIN` supported
anchors or a qualifying domain. The frame is GII-centred: even on construction data the
median MAPPED fraction ran from 0.950 (GII) to 0.473 (Retrons). A genuine RT can land here.

`INPUT_INVALID` and `TOOL_FAILURE` appear **only** in `failures.tsv`; they never appear in
`sequences.tsv`, and the smoke test asserts the separation in both directions.

---

## 5 · `failures.tsv`

`rt_hash`, `sequence_id`, `sequence_length`, `mapper_version`, `inspectability_status`,
`reason_code`, `detail`.

| `reason_code` | condition |
|---|---|
| `EMPTY_SEQUENCE` | no residues |
| `BELOW_MIN_LENGTH` | < 250 aa |
| `NON_STANDARD_RESIDUE` | any character outside the 20 standard amino acids |
| `DUPLICATE_SEQUENCE_ID` | identifier repeated with an **identical** sequence; one copy is kept, the redundant one logged |
| `DUPLICATE_SEQUENCE_ID_CONFLICT` | identifier carries **different** sequences; **every** occurrence is rejected |
| `UNPARSEABLE_RECORD` | residue line outside any FASTA record |
| `MAPPER_RAISED` | `TOOL_FAILURE`: the frozen mapper's own fail-closed assertion fired |

The 250 aa minimum and the standard-residue rule are **inherited, not invented**: they are
the registered loader's eligibility rules, applied to every sequence the instrument was ever
calibrated or validated on. A record failing them is outside that population.

Identical **sequences** under different identifiers are not an error — they share an
`rt_hash`, are mapped once, and each identifier still gets its own row.

A duplicate **identifier** is handled by cases, and the policy is **order-independent by
construction** (repair R2, after the independent review demonstrated the first version was
not):

* **different sequences under one identifier** — a conflict. **Every** occurrence is
  rejected. Retaining "the first" made the retained science a function of input order,
  which a production instrument may not be.
* **the same sequence repeated** — harmless. One copy is kept (they are identical, so which
  one is not a choice) and each extra occurrence is logged.

Shard-local detection cannot see a conflict whose two records landed in different shards, so
g5 censuses the conflict set **globally** and passes it to every shard via `--reject-ids`,
and shards by `sequence_id` so collisions are co-located anyway.

**Reconciliation is enforced.** A shard fails closed unless every valid input identifier
appears exactly once across `sequences.tsv` and the `TOOL_FAILURE` rows of `failures.tsv`
(repair R3). A production run that cannot account for one of its inputs does not ship.

---

## 6 · `provenance.tsv`

One key/value record per shard run. Carries schema version, mapper version, full instrument
digest and every component of it, **the verified bundle root and its status**, input path
and sha256, the reject-id list and its sha256, record counts (read / valid / invalid /
distinct `rt_hash` / duplicates collapsed), batch geometry, emitted row counts, metadata
path and sha256, **the eligibility rule and the domain-scoring protocol**, HMMER and Python
versions, host, and start/finish timestamps — plus the sha256 of each output file.

Only the compact `mapper_version` rides on every data row. The sidecar expands it. This is
the launcher §6 requirement met without carrying the research-review bundle on every record.

Provenance is a record of a **run**, so it legitimately differs between runs of the same
data (timestamps, host, batch geometry). The three data tables do not.
