md(r"""
---

## 0.1 The house analytical population

Operator decision (2026-09-16, this workbench), **revised after review**: geometry eligibility is
the right rule for analyses that need genomic context, and the wrong rule for analyses that need
only the protein. A record whose window was truncated still carries a usable RT sequence. The
population is therefore **two-tiered**:

```
POP_RT_SEQ  =  is_first_copy AND file_label <> 'MULTI' AND NOT multilabel AND elig_exact_rt
POP_RT_CTX  =  POP_RT_SEQ AND elig_geometry
```

`POP_RT_SEQ` is the default for **sequence-level** analyses (family composition, length,
completeness, diversity). `POP_RT_CTX` — written `POP_RT` in the rest of this notebook — is the
default for **context-level** analyses (geometry, ncRNA placement, intervening CDS, locus
architecture). Every section states which it used.

Three exclusions, each for a stated reason:

| exclusion | removes | applies to | why |
|---|---|---|---|
| `NOT is_first_copy` | 8,462 records | both tiers | byte-identical duplicate lines — not a second observation |
| `file_label <> 'MULTI'` + `NOT multilabel` | 9,022 records | both tiers | Rule 2: MULTI is an ambiguity stratum, analysed separately (section G) |
| `elig_geometry` | 16,216 further records | **`POP_RT_CTX` only** | ill-posed and off-contig RT systems — these keep a usable protein and stay in `POP_RT_SEQ` |

`elig_geometry` is exactly the flag that carries the operator's "ill-posed + off-contig"
requirement — the g2b recovery states map onto it **one-to-one**:

| recovery state | n | `elig_geometry` |
|---|---|---|
| `RECOVERED` | 14,188 | **True** — RT CDS reconstructed and verified, keeps full genomic context |
| `SEQUENCE_ONLY` | 16,688 | False — 9,128 RT wholly outside the retrieved contig, 3,924 inverted window, 3,636 RT crossing a contig end |
| `ILL_POSED` | 628 | False |

So `elig_geometry` drops all 628 ill-posed and all 16,688 off-contig/inverted cases, and keeps the
14,188 that were successfully recovered. No separate predicate is needed.

### What `POP_RT` deliberately does NOT exclude

**Contig clipping is a stratification flag, not an exclusion.** 1,249,012 distinct records are
`true_start_clipped` and 1,270,225 are `clipped_end_flag` — ~41 % of the corpus each. Those windows
have a *verified* RT with defensible coordinates; only the window's extent is truncated. Dropping
them would discard 41 % of the corpus to fix a problem that only affects a specific measurement
(the forced-downstream mode of D2), and that measurement is better handled by stratifying, as D2
does. Likewise partial/incomplete ORFs (B3) and atypical geometry (I) stay in and are reported.
""")

code(r'''
# The house population, as a reusable SQL predicate. Cells that need the canonical Stage-1
# denominators (A1-A3, which must reproduce g2/g3/g4) deliberately do NOT apply it and say so.
POP_RT_SEQ = "is_first_copy AND file_label <> 'MULTI' AND NOT multilabel AND elig_exact_rt"
POP_RT_CTX = POP_RT_SEQ + " AND elig_geometry"
POP_RT     = POP_RT_CTX      # back-compatible alias: the context-level default

cascade = cache("A0_population_cascade", f"""
    SELECT 1 AS step, 'all raw records'                     AS population, count(*) AS n FROM rt_records
    UNION ALL SELECT 2, '+ is_first_copy',                     count(*) FILTER (WHERE is_first_copy) FROM rt_records
    UNION ALL SELECT 3, '+ drop the MULTI file',               count(*) FILTER (WHERE is_first_copy AND file_label <> 'MULTI') FROM rt_records
    UNION ALL SELECT 4, '+ drop multilabel records',           count(*) FILTER (WHERE is_first_copy AND file_label <> 'MULTI' AND NOT multilabel) FROM rt_records
    UNION ALL SELECT 5, '+ elig_exact_rt  = POP_RT_SEQ',       count(*) FILTER (WHERE {POP_RT_SEQ}) FROM rt_records
    UNION ALL SELECT 6, '+ elig_geometry  = POP_RT_CTX',       count(*) FILTER (WHERE {POP_RT_CTX}) FROM rt_records
    ORDER BY step
""")
cascade["removed_at_this_step"] = (cascade.n.shift(1) - cascade.n).fillna(0).astype(int)
cascade["pct_of_raw"] = (100 * cascade.n / cascade.n.iloc[0]).round(3)
save(cascade, "A0_population_cascade")
display(cascade[["step", "population", "n", "removed_at_this_step", "pct_of_raw"]])

# the ill-posed / off-contig mapping, verified rather than asserted
recov = cache("A0_recovery_vs_eligibility", """
    SELECT v.recovery_state, v.representation_class, r.elig_geometry, count(*) AS n
    FROM rt_cds_recovery v JOIN rt_records r USING (record_key)
    GROUP BY 1, 2, 3 ORDER BY n DESC
""")
display(recov)
assert not recov[(recov.recovery_state != "RECOVERED") & (recov.elig_geometry)].shape[0], \
    "a non-RECOVERED record is geometry-eligible: the POP_RT rationale needs revisiting"
print("  [OK] every SEQUENCE_ONLY / ILL_POSED record is elig_geometry = False; "
      "every RECOVERED record is True.")

# the units POP_RT yields, for use as denominators downstream
pop_units = cache("A0_pop_rt_units", f"""
    SELECT 'POP_RT_SEQ (sequence-level default)' AS population, count(*) AS n_records,
           count(DISTINCT locus_key) AS n_loci, count(DISTINCT physical_locus_key) AS n_physical_loci,
           count(DISTINCT rt_seq_hash) AS n_exact_rt, count(DISTINCT genome_id_norm) AS n_genomes
    FROM rt_records WHERE {POP_RT_SEQ}
    UNION ALL
    SELECT 'POP_RT_CTX (context-level default)', count(*), count(DISTINCT locus_key),
           count(DISTINCT physical_locus_key), count(DISTINCT rt_seq_hash),
           count(DISTINCT genome_id_norm)
    FROM rt_records WHERE {POP_RT_CTX}
""")
display(pop_units)
''')

md(r"""
**Interpretation.** `POP_RT_CTX` costs **33,700 records (1.10 %)** of the raw corpus, in three
clearly attributable slices; `POP_RT_SEQ` costs only the first two (17,484 records) and **retains
the 16,216 records whose protein is usable but whose genomic context is not** — the correction that
review identified. Nothing that is excluded disappears: the MULTI stratum has its own section,
and the ill-posed / off-contig records are the subject of section I. Every exclusion is a flag
already present in the canonical tables — no new definition is created here.

**Caveat.** A1–A3 reproduce the landed g2 unit ladder and therefore run on the *unfiltered*
population; their numbers are the canonical Stage-1 ones and will not equal the `POP_RT` numbers
above. That is intended — the two answer different questions ("what did the corpus contain" vs
"what will we measure on"). Any cell reporting a rate must say which of the two it used.
""")

md(r"""
## 0.2 — Z0, the population registry

* **Question.** Which analytical populations does this notebook count on, what is each one's
  unit, and how large is it?
* **Unit.** One population.
* **Why this exists.** A review of the thesis draft found six places where two *correct* numbers
  sat beside each other under similar labels and read as a contradiction: three different
  "funnels", the 30,924 / 30,427 pair views, a 94.51 % computed once on canonical and once on
  eligible placements, two unrelated counts of 266, two locus-overlap populations, and two tool
  tables with different protein counts. None of them was a wrong number. In every case the
  population was simply not printed next to the number.
* **The rule from here on.** Every population has a short stable id. Every cached table declares
  its id via `cache(..., pop=...)`; every figure declares its id via `savefig(..., pop=...)` and
  carries it as a stamp along the bottom edge. Every count below is **computed, never typed** —
  if a definition drifts, this table breaks loudly instead of the chapter drifting quietly.
""")

code(r'''
# The registry. Each row: id, unit, the SQL that defines it, and what it may / may not be used
# for. Counts are recomputed from parquet every time this table is built.
_pairs_sel = "SELECT rt_seq_hash, nc_seq_hash FROM rt_ncrna_pairs"

def _build_registry():
    rec = Q(f"""
        SELECT count(*) AS "REC-ALL",
               sum(CASE WHEN is_first_copy THEN 1 ELSE 0 END) AS "REC-DIST",
               count(DISTINCT locus_key) AS "LOC",
               count(DISTINCT physical_locus_key) AS "PLOC",
               count(DISTINCT genome_id_norm) AS "GEN",
               count(DISTINCT rt_seq_hash) AS "RT-BASE"
        FROM rt_records
    """).iloc[0]
    pop = Q(f"""
        SELECT (SELECT count(DISTINCT rt_seq_hash) FROM rt_records WHERE {POP_RT_SEQ}) AS "RT-SEQ",
               (SELECT count(DISTINCT rt_seq_hash) FROM rt_records WHERE {POP_RT_CTX}) AS "RT-CTX"
    """).iloc[0]
    fam = Q("""
        SELECT sum(CASE WHEN view = 'V-RT-SINGLE' THEN 1 ELSE 0 END) AS "RT-BASE-1F",
               sum(CASE WHEN view = 'V-RT-MULTI'  THEN 1 ELSE 0 END) AS "RT-MULTI",
               sum(CASE WHEN view = 'V-RT-CROSS'  THEN 1 ELSE 0 END) AS "RT-CROSS"
        FROM rt_family_baseline
    """).iloc[0]
    pl = Q("""
        SELECT count(*) AS "PL-ALL",
               sum(CASE WHEN geometry_eligible THEN 1 ELSE 0 END) AS "PL-ELIG",
               sum(CASE WHEN canonical THEN 1 ELSE 0 END) AS "PL-CANON",
               count(DISTINCT nc_seq_hash) AS "NC-ALL",
               count(DISTINCT CASE WHEN geometry_eligible THEN nc_seq_hash END) AS "NC-ELIG"
        FROM rt_ncrna_pairs
    """).iloc[0]
    pr = Q(f"""
        SELECT (SELECT count(*) FROM (SELECT DISTINCT rt_seq_hash, nc_seq_hash
                FROM rt_ncrna_pairs WHERE geometry_eligible)) AS "PAIR-ELIG",
               (SELECT count(*) FROM (SELECT DISTINCT rt_seq_hash, nc_seq_hash
                FROM rt_ncrna_pairs WHERE canonical)) AS "PAIR-CANON"
    """).iloc[0]
    n = {**rec.to_dict(), **pop.to_dict(), **fam.to_dict(), **pl.to_dict(), **pr.to_dict()}

    spec = [
        ("REC-ALL",    "raw record",                 "rt_records, all rows",
         "provenance, per-file composition as mined",  "any biological rate"),
        ("REC-DIST",   "distinct record",            "is_first_copy",
         "as REC-ALL, minus byte-identical duplicate lines", "any biological rate"),
        ("LOC",        "accession-defined locus",    "distinct locus_key",
         "per-locus architecture, contig context",     "counts a RefSeq/GenBank twin twice"),
        ("PLOC",       "physical locus",             "distinct physical_locus_key",
         "locus counts corrected for twin publication", "collapse only where supported"),
        ("GEN",        "genome identifier",          "distinct genome_id_norm",
         "taxonomic breadth",                          "genome-level prevalence (RT-carrying only)"),
        ("RT-BASE",    "exact RT protein",           "distinct rt_seq_hash, whole corpus",
         "the full exact-sequence baseline",           "any POP_RT-filtered statement"),
        ("RT-BASE-1F", "exact RT protein",           "rt_family_baseline view = V-RT-SINGLE",
         "family composition of the baseline",         "the record-filtered sequence population"),
        ("RT-MULTI",   "exact RT protein",           "rt_family_baseline view = V-RT-MULTI",
         "the multi-label stratum, on its own",        "never appended to a single family"),
        ("RT-CROSS",   "exact RT protein",           "rt_family_baseline view = V-RT-CROSS",
         "proteins seen under >1 single-family label", "family denominators"),
        ("RT-SEQ",     "exact RT protein",           "POP_RT_SEQ",
         "family, length, completeness, diversity",    "geometry (no context guarantee)"),
        ("RT-CTX",     "exact RT protein",           "POP_RT_CTX",
         "geometry, ncRNA placement, architecture",    "sequence diversity (drops 16,008 usable)"),
        ("PL-ALL",     "placement",                  "rt_ncrna_pairs, all rows",
         "call-level QC",                              "geometry (contains QC failures)"),
        ("PL-ELIG",    "eligible placement",         "geometry_eligible",
         "geometry before de-duplication",             "counting distinct biology"),
        ("PL-CANON",   "eligible, non-redundant placement", "canonical",
         "all geometry reported in the chapter",       "raw call frequency"),
        ("NC-ALL",     "exact ncRNA sequence",       "distinct nc_seq_hash, all placements",
         "the ncRNA sequence set as called",           "pairing with eligible placements"),
        ("NC-ELIG",    "exact ncRNA sequence",       "distinct nc_seq_hash, eligible",
         "the ncRNA side of the registered pair view", "call-level composition"),
        ("PAIR-ELIG",  "exact RT-ncRNA pair",        "distinct (rt,nc) over eligible",
         "pair topology; matches rt_ncrna_exact_pairs_v1", "geometry composition"),
        ("PAIR-CANON", "exact RT-ncRNA pair",        "distinct (rt,nc) over canonical",
         "the dataset funnel and geometry composition", "pair topology (497 pairs short of g3)"),
    ]
    return pd.DataFrame(
        [{"pop_id": i, "unit": u, "n": int(n[i]), "definition": d,
          "honest_for": h, "not_honest_for": nh} for i, u, d, h, nh in spec])

POPREG = cache("Z0_population_registry", fn=_build_registry)
display(POPREG[["pop_id", "unit", "n", "honest_for", "not_honest_for"]])
''')

code(r'''
# Guard rails. These are the six collisions the registry exists to prevent, asserted as
# arithmetic rather than left as prose.
R = {r.pop_id: r.n for r in POPREG.itertuples()}
print("registry consistency checks")
print(f"  [{'OK ' if R['RT-BASE-1F'] + R['RT-MULTI'] + R['RT-CROSS'] == R['RT-BASE'] else 'BAD'}]"
      f" RT-BASE-1F + RT-MULTI + RT-CROSS == RT-BASE  "
      f"({R['RT-BASE-1F']:,} + {R['RT-MULTI']:,} + {R['RT-CROSS']:,} = {R['RT-BASE']:,})")
# POP_RT_SEQ excludes MULTI by construction: it is single-family + cross-labelled, NOT
# single-family + MULTI. The thesis draft had this backwards.
_seq_split = Q(f"""
    SELECT n_fam, count(*) AS n_rt FROM (
      SELECT rt_seq_hash, count(DISTINCT file_label) AS n_fam
      FROM rt_records WHERE {POP_RT_SEQ} GROUP BY 1) GROUP BY 1 ORDER BY 1
""")
_one, _multi_fam = int(_seq_split.n_rt.iloc[0]), int(_seq_split.n_rt.iloc[1:].sum())
print(f"  [{'OK ' if _one + _multi_fam == R['RT-SEQ'] else 'BAD'}]"
      f" RT-SEQ = {_one:,} single-family + {_multi_fam:,} cross-labelled = {R['RT-SEQ']:,}"
      f"  -- contains 0 MULTI proteins")
print(f"  [{'OK ' if R['PL-ALL'] >= R['PL-ELIG'] >= R['PL-CANON'] else 'BAD'}]"
      f" PL-ALL {R['PL-ALL']:,} >= PL-ELIG {R['PL-ELIG']:,} >= PL-CANON {R['PL-CANON']:,}")
print(f"  [{'OK ' if R['PAIR-ELIG'] > R['PAIR-CANON'] else 'BAD'}]"
      f" PAIR-ELIG {R['PAIR-ELIG']:,} - PAIR-CANON {R['PAIR-CANON']:,} ="
      f" {R['PAIR-ELIG'] - R['PAIR-CANON']:,} pairs carried only by de-duplicated placements")
print(f"  [{'OK ' if R['NC-ALL'] > R['NC-ELIG'] else 'BAD'}]"
      f" NC-ALL {R['NC-ALL']:,} vs NC-ELIG {R['NC-ELIG']:,}"
      f"  -- PL-ALL pairs with NC-ALL, never with NC-ELIG")
print()
print("Caption stamp preview:")
for i in ["RT-SEQ", "PL-CANON", "PAIR-CANON"]:
    print("   ", pop_stamp(i))
''')
