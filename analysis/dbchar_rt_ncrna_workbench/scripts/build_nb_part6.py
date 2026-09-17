md(r"""
---

# K. Dataset inventory

One row per named dataset this characterization can hand downstream, each with its inclusion rule,
its counts under that exact rule, and — as important — what it may **not** be used to claim.

Rows marked **PROVISIONAL** cannot be populated yet because their selection rule is an operator
decision that has not been made (§K2). They are listed with their open parameters rather than
filled with a default, because a threshold invented here would silently become the project's
definition of a confident RT–ncRNA association.
""")

md(r"""
## K1 — Populated rows

* **Question.** Under each precise inclusion rule, how large is the resulting dataset in every unit
  a downstream task might need?
* **Unit.** Varies per row; every row reports records, loci, physical loci, exact RTs, exact ncRNAs
  and exact pairs where the concept applies.
* **Denominator.** Each row is its own population; the `overlap` column states its relation to the
  others rather than implying they partition anything.
* **Data.** All canonical tables.
""")

code(r'''
def counts(where_records=None, where_pairs=None):
    """Count one dataset in every unit that applies to it."""
    out = {}
    if where_records:
        r = Q(f"""SELECT count(*) AS n_records, count(DISTINCT locus_key) AS n_loci,
                         count(DISTINCT physical_locus_key) AS n_physical_loci,
                         count(DISTINCT rt_seq_hash) AS n_exact_rt,
                         count(DISTINCT genome_id_norm) AS n_genomes
                  FROM rt_records WHERE {where_records}""").iloc[0].to_dict()
        out.update(r)
    if where_pairs:
        p = Q(f"""SELECT count(*) AS n_placements,
                         count(DISTINCT physical_locus_key) AS n_physical_loci,
                         count(DISTINCT rt_seq_hash) AS n_exact_rt,
                         count(DISTINCT nc_seq_hash) AS n_exact_ncrna,
                         count(DISTINCT (rt_seq_hash, nc_seq_hash)) AS n_exact_pairs
                  FROM rt_ncrna_pairs WHERE {where_pairs}""").iloc[0].to_dict()
        out.update(p)
    return out

ROWS = [
    dict(dataset="D1 full RT corpus", purpose="provenance, corpus description",
         unit="raw record", rule="every RT-anchored record as mined",
         rec="TRUE", pair=None),
    dict(dataset="D2 distinct-record corpus", purpose="anything record-level",
         unit="distinct record", rule="is_first_copy",
         rec="is_first_copy", pair=None),
    dict(dataset="D3 sequence resource (POP_RT_SEQ)",
         purpose="family composition, length, completeness, diversity, clustering",
         unit="exact RT protein", rule="distinct, single-family, well-formed protein",
         rec=POP_RT_SEQ, pair=None),
    dict(dataset="D4 context resource (POP_RT_CTX)",
         purpose="geometry, locus architecture, genomic context",
         unit="record / locus", rule="POP_RT_SEQ + elig_geometry",
         rec=POP_RT_CTX, pair=None),
    dict(dataset="D5 MULTI stratum", purpose="family-ambiguity analysis only",
         unit="exact RT protein", rule="file_label = MULTI or multilabel",
         rec="is_first_copy AND (file_label = 'MULTI' OR multilabel)", pair=None),
    dict(dataset="D6 technically unresolved", purpose="QC, method development",
         unit="record", rule="distinct, single-family, NOT elig_geometry",
         rec="is_first_copy AND file_label <> 'MULTI' AND NOT multilabel AND NOT elig_geometry",
         pair=None),
    dict(dataset="D7 observed placements (canonical)",
         purpose="RT-ncRNA geometry as observed",
         unit="placement",
         rule="geometry-eligible and de-duplicated; pair counts here are canonical-derived (30,427)",
         rec=None, pair="canonical"),
    dict(dataset="D8 observed placements, Retron only",
         purpose="retron-specific geometric conclusions",
         unit="placement", rule="canonical AND file_label = Retron",
         rec=None, pair="canonical AND file_label = 'Retron'"),
    dict(dataset="D9 exact-pair resource (registered view)",
         purpose="pair-level association, co-evolution input",
         unit="exact (RT, ncRNA) pair",
         rule="rt_ncrna_exact_pairs_v1 — built on ELIGIBLE placements, not canonical (see F0)",
         rec=None, pair=None, registered_pairs=True),
    dict(dataset="D10 atypical placements",
         purpose="exception review; never a background set",
         unit="placement",
         rule="canonical AND (opposite strand OR >2 CDS between OR |distance| > 5 kb)",
         rec=None,
         pair="canonical AND (NOT same_strand OR n_cds_between > 2 OR abs(signed_distance_bp) > 5000)"),
    dict(dataset="D11 retron-CM / non-Retron-RT candidates",
         purpose="candidate cross-family associations",
         unit="placement", rule="eligible, retron CM, non-Retron single-family RT",
         rec=None,
         pair="geometry_eligible AND file_label NOT IN ('Retron','MULTI')"),
]

rows = []
for r in ROWS:
    if r.get("registered_pairs"):
        c = Q("""SELECT count(*) AS n_exact_pairs, count(DISTINCT rt_seq_hash) AS n_exact_rt,
                        count(DISTINCT nc_seq_hash) AS n_exact_ncrna
                 FROM rt_ncrna_exact_pairs""").iloc[0].to_dict()
    else:
        c = counts(r["rec"], r["pair"])
    rows.append({**{k: r[k] for k in ("dataset", "purpose", "unit", "rule")}, **c})
inv = pd.DataFrame(rows)
for col in ["n_records", "n_loci", "n_physical_loci", "n_exact_rt", "n_genomes",
            "n_placements", "n_exact_ncrna", "n_exact_pairs"]:
    if col in inv: inv[col] = inv[col].astype("Int64")
save(inv, "K1_dataset_inventory")
display(inv[["dataset", "unit", "n_records", "n_loci", "n_physical_loci", "n_exact_rt",
             "n_placements", "n_exact_ncrna", "n_exact_pairs"]])
''')

code(r'''
K = pd.read_csv(TABLES / "K1_dataset_inventory.tsv", sep="\t")

USES = {
 "D1 full RT corpus": ("corpus provenance; per-file composition",
                       "ANY biological rate — it double-counts loci mined more than once"),
 "D2 distinct-record corpus": ("record-level QC, tool-call analysis",
                       "diversity statements — one protein appears at many records"),
 "D3 sequence resource (POP_RT_SEQ)": ("family composition, length, completeness, clustering",
                       "anything needing genomic context — 16,008 of these proteins have none"),
 "D4 context resource (POP_RT_CTX)": ("geometry, neighbourhood, locus architecture",
                       "protein diversity — it discards usable proteins with broken context"),
 "D5 MULTI stratum": ("family-ambiguity analysis",
                       "any single-family statistic; do not merge into a family"),
 "D6 technically unresolved": ("QC and extraction-method development",
                       "biology of any kind"),
 "D7 observed placements (canonical)": ("observed geometry, distance, strand, adjacency",
                       "cotranscription, cognate recognition, or 'validated pairs'"),
 "D8 observed placements, Retron only": ("retron-specific geometric conclusions",
                       "cross-family generalisation"),
 "D9 exact-pair resource (registered view)": ("pair-level association; recurrence-class-filtered co-evolution input",
                       "orthogonality — 1:1 as observed is not exclusive pairing"),
 "D10 atypical placements": ("exception review, hypothesis generation",
                       "a background or null distribution"),
 "D11 retron-CM / non-Retron-RT candidates": ("candidate list for annotation follow-up",
                       "novel retrons — CM cross-matching is not excluded"),
}
K["suitable_for"] = K.dataset.map(lambda d: USES[d][0])
K["NOT_usable_for"] = K.dataset.map(lambda d: USES[d][1])
K["retained_uncertainty"] = K.dataset.map({
 "D1 full RT corpus": "duplicate lines; ncRNA-anchored records excluded by rule",
 "D2 distinct-record corpus": "cross-database locus overlap (200,914 loci)",
 "D3 sequence resource (POP_RT_SEQ)": "partiality (~25% all_partial); family label is HMM-assigned",
 "D4 context resource (POP_RT_CTX)": "~41% contig-clipped windows retained and stratified, not excluded",
 "D5 MULTI stratum": "unresolved; margin result confounded with protein length",
 "D6 technically unresolved": "628 ill-posed; 16,688 sequence-only",
 "D7 observed placements (canonical)": "detector scope (retron CMs only); technical downstream mode",
 "D8 observed placements, Retron only": "zero-ncRNA rate 47.23% is not measured absence",
 "D9 exact-pair resource (registered view)": "30.3% of recurrence is database copies of one physical locus; ELIGIBLE-based, 497 pairs have no canonical placement",
 "D10 atypical placements": "mixed causes: artefact, annotation gap, and possible biology",
 "D11 retron-CM / non-Retron-RT candidates": "partner ambiguity and CM-hit quality not yet assessed",
})
save(K, "K1_dataset_inventory")
pd.set_option("display.max_colwidth", 58)
display(K[["dataset", "suitable_for", "NOT_usable_for", "retained_uncertainty"]])
pd.set_option("display.max_colwidth", 50)
print(f"\nwritten: {TABLES / 'K1_dataset_inventory.tsv'}")
''')

md(r"""
## K2 — PROVISIONAL rows: what is still undecided

Three datasets named in the review cannot be populated from the current evidence, because each
needs a selection rule that is an **operator decision**, not a computation. They are specified here
with their open parameters so the decision can be made explicitly.

### K2.1 — "Confident RT–ncRNA associations"

The term *canonical placement* means **technically eligible and de-duplicated under the existing
geometry rules**. It must not be renamed "biologically validated pair". A confidence rule needs
values for, at minimum:

| parameter | candidate basis in the data | currently undecided |
|---|---|---|
| maximum RT–ncRNA distance | the ≤ 200 bp band holds 73.9 % of exact pairs (D6) | is the cut 200 bp, 500 bp, or distribution-derived? |
| strand requirement | 99.12 % same-strand; opposite-strand is a single-CM population (D5) | require same strand, or retain opposite as flagged? |
| intervening CDS | 94.41 % have none | require 0, or allow 1? |
| direction | upstream 94.5 %; overlapping 3.5 % | are overlapping placements included? |
| CM hit quality | `score` / `evalue` exist per call and are **not yet used anywhere** | no threshold set; per-model or global? |
| partner ambiguity | 96.85 % of RTs have one partner (F1) | require 1:1, or allow ambiguous with a flag? |
| recurrence independence | only 30.86 % recur across genomes/species (F3) | require independent recurrence, or allow singletons? |
| context completeness | `POP_RT_CTX` only, or also clipped windows? | |

**Until these are set, the confident-association dataset does not exist and should not be quoted.**
The counts under any candidate rule are one query away once the rule is chosen.

### K2.2 — Modeling dataset
Needs K2.1 plus a train/test split rule that does not leak: exact pairs recurring only as database
copies of one physical locus (30.32 %) must not be split across folds, or performance will be
inflated by memorisation.

### K2.3 — Experimental-prioritization dataset
Needs K2.1 plus task-specific criteria (host tractability, subtype coverage, sequence novelty
against known retrons) that this characterization does not measure.
""")

code(r'''
# The confidence rule is not set, so no dataset is produced. What CAN be shown is how many exact
# pairs survive each candidate criterion INDEPENDENTLY — the input to choosing the rule.
sens = cache("K2_criterion_sensitivity", """
    WITH p AS (SELECT * FROM rt_ncrna_pairs WHERE canonical),
         d AS (SELECT rt_seq_hash, nc_seq_hash,
                      count(*) OVER (PARTITION BY rt_seq_hash) AS rt_partners,
                      count(*) OVER (PARTITION BY nc_seq_hash) AS nc_partners
               FROM rt_ncrna_exact_pairs)
    SELECT 'all exact pairs derivable from CANONICAL placements' AS criterion,
           count(DISTINCT (rt_seq_hash, nc_seq_hash)) AS n_exact_pairs FROM p
    UNION ALL SELECT 'same strand', count(DISTINCT (rt_seq_hash, nc_seq_hash)) FROM p WHERE same_strand
    UNION ALL SELECT 'upstream only', count(DISTINCT (rt_seq_hash, nc_seq_hash)) FROM p WHERE direction = 'upstream'
    UNION ALL SELECT 'no CDS between', count(DISTINCT (rt_seq_hash, nc_seq_hash)) FROM p WHERE n_cds_between = 0
    UNION ALL SELECT 'distance <= 200 bp', count(DISTINCT (rt_seq_hash, nc_seq_hash)) FROM p WHERE abs(signed_distance_bp) <= 200
    UNION ALL SELECT 'distance <= 500 bp', count(DISTINCT (rt_seq_hash, nc_seq_hash)) FROM p WHERE abs(signed_distance_bp) <= 500
    UNION ALL SELECT 'not contig-start-clipped', count(DISTINCT (rt_seq_hash, nc_seq_hash)) FROM p WHERE NOT true_start_clipped
    UNION ALL SELECT '1:1 partner topology', count(*) FROM d WHERE rt_partners = 1 AND nc_partners = 1
    UNION ALL SELECT 'recurs across genomes/species',
           count(*) FROM rt_ncrna_exact_pair_recurrence
           WHERE recurrence_class IN ('multiple_species','one_species_multiple_genomes','one_genome_multiple_loci')
""", pop="PAIR-CANON")
base = int(sens.n_exact_pairs.iloc[0])   # canonical-derived baseline, 30,427 (see F0)
sens["pct_of_all_pairs"] = (100 * sens.n_exact_pairs / base).round(2)
save(sens, "K2_criterion_sensitivity")
display(sens)
print("\nEach row is that criterion applied ALONE, not cumulatively. The intersection depends on the")
print("rule chosen in K2.1 and is deliberately not computed here.")
print("Do not read this table beside the L7 or N8 cascades: those are cumulative, this one is")
print("marginal, so the same criterion name carries a different number in each.")
''')

md(r"""
**Interpretation.** Baseline here is the **canonical-derived 30,427 pairs** (F0), not the registered
30,924. Every individual criterion retains a large share of them, so
the confident-association dataset is not obviously small under any single rule — but the criteria
are correlated, and their **intersection** is the number that matters. That intersection is not
computed here on purpose: producing one would make an arbitrary threshold into the project's
operating definition of a confident association.

**What to decide next, in order:** (1) distance cut and whether overlapping placements are in;
(2) whether CM hit quality enters at all — `score` and `evalue` are present on every call and are
currently unused anywhere in this characterization; (3) whether 1:1 topology is required or flagged;
(4) whether independent recurrence is required. Once those four are set, K2.1, K2.2 and K2.3
populate in a single pass.
""")
