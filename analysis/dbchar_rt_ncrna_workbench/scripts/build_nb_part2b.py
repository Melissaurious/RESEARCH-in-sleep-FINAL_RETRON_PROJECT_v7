md(r"""
## A4 — Source-database attribution: why per-database columns do not sum

* **Question.** A2's per-database counts exceed the corpus totals. What is the overlap made of,
  and what is the right way to report "share of corpus by database"?
* **Unit.** (i) genomic locus (`V-LOC`); (ii) genome; (iii) exact RT protein (`V-RT`).
* **Denominator.** `POP_RT` loci / genomes / exact RTs. Two framings are shown side by side:
  **coverage** (non-exclusive: "how many loci does this database contain") and an **exclusive
  partition** under a declared primary-source rule.
* **Data.** `rt_records_v1` → `source_database`, `locus_key`, `genome_id_norm`, `rt_seq_hash`;
  `rt_exact_v1` → `n_source_databases`.
""")

code(r'''
# 1. what the overlap is actually made of: the set of databases each locus appears under
dbsets = cache("A4_locus_database_sets", f"""
    WITH L AS (
      SELECT locus_key,
             string_agg(DISTINCT source_database, ' + ' ORDER BY source_database) AS database_set,
             count(DISTINCT source_database) AS n_databases
      FROM rt_records WHERE {POP_RT} GROUP BY 1)
    SELECT database_set, n_databases, count(*) AS n_loci
    FROM L GROUP BY 1, 2 ORDER BY n_loci DESC
""", pop="RT-CTX")
dbsets["pct_of_loci"] = (100 * dbsets.n_loci / dbsets.n_loci.sum()).round(3)
save(dbsets, "A4_locus_database_sets")
display(dbsets)

shared = dbsets[dbsets.n_databases > 1]
print(f"\nloci under >1 database: {int(shared.n_loci.sum()):,} "
      f"({100 * shared.n_loci.sum() / dbsets.n_loci.sum():.2f}% of POP_RT loci); "
      f"{100 * shared.n_loci.max() / shared.n_loci.sum():.1f}% of that overlap is a single pair.")

# The SAME quantity on the WHOLE corpus, because that is the number the thesis quotes and the
# number the landed g1 bundle registers. Two populations, two answers, both correct; printed
# together so that neither can be quoted while the other is cited.
both = cache("A4_multi_database_loci_by_population", """
    SELECT 'LOC (whole corpus)' AS population, count(*) AS n_loci_multi_database FROM (
      SELECT locus_key FROM rt_records GROUP BY 1 HAVING count(DISTINCT source_database) > 1)
""", pop="LOC")
_popn = int(shared.n_loci.sum())
if "RT-CTX (POP_RT loci)" not in set(both.population):
    both = pd.concat([both, pd.DataFrame([{"population": "RT-CTX (POP_RT loci)",
                                           "n_loci_multi_database": _popn}])], ignore_index=True)
    save(both, "A4_multi_database_loci_by_population")
display(both)
print(f"  difference: {int(both.n_loci_multi_database.iloc[0]) - _popn:,} loci are multi-database"
      " but fall outside POP_RT_CTX. Quote 203,921 only with the LOC denominator.")
''')

code(r'''
# 2. coverage (non-exclusive) vs an exclusive partition under a declared primary-source rule.
#    Rule: most-specific curated source wins. GTDB is a curated re-derivation of the same
#    assemblies NCBI publishes, so where a locus appears under both, GTDB is the primary.
PRIMARY_ORDER = ["gtdb_bacteria", "gtdb_archaea", "ncbi_bacteria", "ncbi_archaea",
                 "mgnify_human_gut", "mgnify_soil", "mgnify_marine", "gem"]
_rank = "CASE source_database " + " ".join(
    f"WHEN '{d}' THEN {i}" for i, d in enumerate(PRIMARY_ORDER)) + " ELSE 99 END"

attrib = cache("A4_database_attribution", f"""
    WITH cov AS (
      SELECT source_database, count(DISTINCT locus_key) AS n_loci_coverage
      FROM rt_records WHERE {POP_RT} GROUP BY 1),
    prim AS (
      SELECT locus_key, arg_min(source_database, {_rank}) AS primary_database
      FROM rt_records WHERE {POP_RT} GROUP BY 1),
    exc AS (
      SELECT primary_database AS source_database, count(*) AS n_loci_exclusive
      FROM prim GROUP BY 1)
    SELECT cov.source_database, cov.n_loci_coverage, coalesce(exc.n_loci_exclusive, 0) AS n_loci_exclusive
    FROM cov LEFT JOIN exc USING (source_database) ORDER BY n_loci_coverage DESC
""")
attrib["pct_of_partition"] = (100 * attrib.n_loci_exclusive / attrib.n_loci_exclusive.sum()).round(3)
attrib["coverage_minus_exclusive"] = attrib.n_loci_coverage - attrib.n_loci_exclusive
save(attrib, "A4_database_attribution")
display(attrib)

_pu = pd.read_csv(TABLES / "A0_pop_rt_units.tsv", sep="\t")
n_pop_loci = int(_pu.loc[_pu.population.str.startswith("POP_RT_CTX"), "n_loci"].iloc[0])
print(f"\ncoverage column sums to {int(attrib.n_loci_coverage.sum()):,} — "
      f"EXCEEDS the {n_pop_loci:,} POP_RT loci, so it is not a share.")
print(f"exclusive column sums to {int(attrib.n_loci_exclusive.sum()):,} — "
      f"{'partitions exactly' if int(attrib.n_loci_exclusive.sum()) == n_pop_loci else 'DOES NOT partition'}.")
''')

code(r'''
# 3. the same question one rung up the ladder: can exact RT proteins be attributed at all?
# NOTE: rt_exact is the FULL-CORPUS exact-RT table (501,561). This panel is therefore on the full
# corpus, unlike the two panels above which are POP_RT. Both are labelled on the figure.
spanning = cache("A4_exact_rt_database_span", """
    SELECT n_source_databases, count(*) AS n_exact_rt FROM rt_exact GROUP BY 1 ORDER BY 1
""")
spanning["pct_of_exact_rt"] = (100 * spanning.n_exact_rt / spanning.n_exact_rt.sum()).round(2)
save(spanning, "A4_exact_rt_database_span")
display(spanning)
multi_db = spanning[spanning.n_source_databases > 1].n_exact_rt.sum()
print(f"\n{multi_db:,} exact RT proteins ({100 * multi_db / spanning.n_exact_rt.sum():.1f}%) "
      f"occur in more than one source database.")
''')

code(r'''
A = pd.read_csv(TABLES / "A4_database_attribution.tsv", sep="\t").iloc[::-1]
S = pd.read_csv(TABLES / "A4_exact_rt_database_span.tsv", sep="\t")
DS = pd.read_csv(TABLES / "A4_locus_database_sets.tsv", sep="\t")
DS = DS[DS.n_databases > 1].sort_values("n_loci")

fig, axes = plt.subplots(1, 3, figsize=(13.2, 3.6))

ax = axes[0]
y = np.arange(len(A)); h = 0.38
ax.barh(y + h/2, A.n_loci_coverage, height=h, color="#9aa7b1", label="coverage (non-exclusive)")
ax.barh(y - h/2, A.n_loci_exclusive, height=h, color="#3b6ea5", label="exclusive (primary rule)")
ax.set_yticks(y); ax.set_yticklabels(A.source_database, fontsize=8)
ax.set_xscale("log"); ax.set_xlabel("POP_RT loci (log)"); ax.legend(fontsize=7.5, loc="lower right")
ax.set_title("A4 — coverage vs exclusive partition\n(population: POP_RT loci)", fontsize=9.5, loc="left")

ax = axes[1]
ax.barh(DS.database_set, DS.n_loci, color="#b5533b", height=0.62)
ax.set_xlabel("loci appearing under that database pair")
ax.set_title("what the overlap is made of\n(population: POP_RT loci)", fontsize=9.5, loc="left")
ax.tick_params(axis="y", labelsize=7.5)

ax = axes[2]
ax.bar(S.n_source_databases.astype(str), S.pct_of_exact_rt, color="#4a8a72", width=0.62)
for x, v in zip(range(len(S)), S.pct_of_exact_rt):
    ax.text(x, v + 1.2, f"{v:.1f}%", ha="center", fontsize=7.5)
ax.set_ylim(0, 65)
ax.set_xlabel("source databases containing that exact RT")
ax.set_ylabel("% of exact RT proteins")
ax.set_title("exact RTs are not attributable at all\n(population: FULL CORPUS exact RTs)", fontsize=9.5, loc="left")

fig.tight_layout(); savefig(fig, "A4_database_attribution", pop=['RT-CTX']); plt.show()
''')

md(r"""
**Interpretation — and the recommended rule.** The overlap is not diffuse: essentially all of it is
a single pair, `gtdb_bacteria + ncbi_bacteria` (plus the archaeal equivalent). GTDB is a curated
re-derivation of assemblies NCBI publishes, so those loci are **one organism seen twice**, not two
observations. Three consequences, in increasing severity up the unit ladder:

1. **Loci can be partitioned**, but only under a declared rule. The primary-source rule above
   (curated GTDB wins over NCBI; metagenomic databases never collide) sums exactly to the `POP_RT`
   locus total, so the `pct_of_partition` column is a legitimate share.
2. **Genomes overlap the same way** — 111,394 of 1,542,433 appear under two databases.
3. **Exact RT proteins cannot be attributed at all.** **45.23 %** occur in ≥2 databases — measured
   on the full-corpus exact-RT table (501,561), *not* on `POP_RT`, because database span is a
   property of all observations of a protein, and one protein
   in six databases is a meaningful biological statement, not a bookkeeping error. At the `V-RT`
   rung, "database" is a property of an *observation*, not of the object.

**So: how to address it.** Report per-database numbers as **coverage**, never as shares — that is
what A2 does, and it is correct for redundancy. When a share is genuinely needed (e.g. "what
fraction of the corpus is metagenomic"), do it **at the locus or genome rung under the declared
primary-source rule**, name the rule, and show the `coverage_minus_exclusive` column so the reader
sees what the rule moved. Never compute a database share on exact RTs.

**Caveat.** The primary-source rule is a *reporting* convention, not a claim that GTDB's copy is
the better one. Changing the priority order moves ~201 k loci between two rows and nothing else;
the metagenomic databases are unaffected because they never collide with anything.
""")
