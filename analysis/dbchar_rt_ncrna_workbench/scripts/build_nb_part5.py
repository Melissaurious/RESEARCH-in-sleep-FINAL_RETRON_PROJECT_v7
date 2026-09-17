# ====================== SECTIONS E-J : SCAFFOLD ONLY ======================
md(r"""
---

# E. Detection / tool relationships  *(scaffold — not yet implemented)*

* **Question.** How do myRT, PADLOC and DefenseFinder partition the corpus, and how much of the
  apparent biology of a tool-defined subset is a detector-definition effect?
* **Unit.** Distinct record (`V-REC-DISTINCT`, `record_key`). `rt_tool_calls_v1` **is** that
  population — 3,051,238 rows, i.e. `is_first_copy`.
* **Denominator.** Retron records for the headline tool percentages (to match g6); state clearly
  whenever the denominator is all RT records instead.
* **Data.** `rt_tool_calls_v1` → `by_myRT`, `by_PADLOC`, `by_DefenseFinder`, `detected_by_set`,
  `n_tools`, `n_ncrna`, `file_label`, `subtypes_padloc`, `subtypes_defensefinder`.

Planned:
1. 3-set Venn over the seven `detected_by_set` classes (`matplotlib_venn.venn3`).
2. ncRNA carriage per tool intersection — the 89.23 % (myRT+PADLOC) vs 13.50 % (myRT alone) contrast.
3. Subtype agreement where both tools wrote one (365,708 records; 160,381 agree).
4. An explicit **detector-definition vs biology** panel.

**Hard caveat to carry into every cell here:** the three tools share model lineage, so agreement is
not independent corroboration; and *"tool absent from a record"* cannot be distinguished from
*"tool never run on that genome"*. A tool-defined subset of this corpus is **not** a random subset.
""")

md(r"""
# G. The MULTI population  *(scaffold — not yet implemented)*

* **Question.** What is the basis of the multiple family labels — mislabelling, or genuine
  profile ambiguity?
* **Unit.** Exact RT protein in `V-RT-MULTI` (7,593); the record-level stratum is 9,012.
* **Denominator.** MULTI exact RTs. **MULTI is never appended to a single family** (Rule 2).
* **Data.** `multi_hmm_evidence_v1` → `labels`, `best_family`, `best_score`, `second_family`,
  `second_score`, `margin_bits`, `best_in_labels`, `rt_aa_len`; `rt_family_baseline_v1`.

Planned: margin distribution vs the seeded single-family control (5 bits vs 81.7 bits);
label-set combinations; length and completeness of MULTI vs `V-RT-SINGLE`; margin-vs-length to
test the length confound.

**Caveat.** Stage 1 does **not** resolve MULTI, and neither should this section. MULTI proteins are
shorter than single-family ones and HMM score scales with length, so part of the small margin may
be a length effect rather than biological ambiguity. Treat it as an ambiguity population.
""")

md(r"""
# H. Taxonomic representation  *(scaffold — not yet implemented)*

* **Question.** How is the corpus distributed over taxa, and what changes when redundancy is
  corrected?
* **Unit.** Report **both** distinct record (`V-REC-DISTINCT`) and exact RT (`V-RT`) /
  RT taxonomic occurrence (`V-RT-TAXOCC`); the difference *is* the result.
* **Denominator.** Per taxonomy system, never pooled: `ncbi` 2,267,726 records ·
  `gtdb` 769,698 · `unknown` 22,276.
* **Data.** `rt_records_v1` → `taxonomy_system`, `tax_domain`, `tax_phylum`, `tax_class`,
  `tax_species`, `genome_id_norm`, `rt_seq_hash`, `is_first_copy`.

Planned: representation by domain/phylum/class per schema; the record→exact-RT shift
(*E. coli* 19.97 % → 6.09 %; top-10 species 66.21 % → 18.95 %); an explicit
raw-representation vs normalised-enrichment pair.

**Caveats.** (i) NCBI rows carry **no phylum by construction** — 0.00 % coverage is a schema fact,
not missing data; report GTDB and NCBI separately and never pool ranks. (ii) Record counts measure
sequencing effort. Any enrichment claim needs a stated normalisation and a denominator of genomes
*surveyed*, which this corpus — harvested by RT presence — does not contain. Prefer
"representation" over "enrichment" unless that denominator is supplied.
""")

md(r"""
# I. QC and exceptional populations  *(scaffold — not yet implemented)*

* **Question.** What does the corpus look like at its edges, and what does each eligibility rule
  cost its denominator?
* **Unit.** Varies per sub-analysis — declared per cell.
* **Denominator.** Declared per cell; every eligibility filter reports (n eligible, n ineligible,
  by reason).
* **Data.** `rt_cds_recovery_v1` (31,504), `rt_ncrna_pairs_v1` (`geometry_ineligible_reason`,
  `multiplicity_class`), `rt_records_v1` (`window_inverted`, `true_start_clipped`,
  `clipped_end_flag`, `rt_at_window_edge`, `bt_status`),
  `rt_ncrna_nonretron_candidates_v1` (266), `g3_atypical_catalogue.tsv`.

Planned:
1. RT-CDS recovery classes — `RECOVERED` 14,188 / `SEQUENCE_ONLY` 16,688 / `ILL_POSED` 628, and
   `representation_class` (9,128 wholly beyond the retrieved contig).
2. Geometry-ineligible placements by reason (2,568 non-canonical: 1,303 byte-identical duplicate
   lines, 41 + 37 + 28 QC).
3. Atypical / inverted windows (3,924 inverted-no-sequence) and the atypical catalogue.
4. The **266** retron-CM / non-Retron-RT candidates (260 single-family + 6 MULTI).
5. Back-translation status: 2,532,006 exact vs 618 mismatch.

**Caveat.** Atypical biology is **flagged before it is filtered** (project convention). Nothing in
this section is a cleanup step; it is the measurement of what each rule removes. And "verified"
only means two fields of one record agree.
""")

md(r"""
# J. Open exploratory analyses

Space for analyses added on request. Each new block follows the same shape:

1. Markdown declaration — **question · unit · denominator · datasets/columns**.
2. Computation cell using `Q(...)` / `cache("<Jn_name>", "<sql>")`.
3. Compact table.
4. One plot, drawn from the cached table.
5. Markdown interpretation **and caveat**.

Before adding one, check whether the value already exists in `g7_resolved_values.tsv` — if it does,
load it rather than creating a second definition.
""")

code(r'''
# Scratch cell — free exploration. Anything worth keeping becomes a J-section block above.
# Q("SELECT ... FROM rt_records WHERE ... LIMIT 20")
''')

md(r"""
---

## Session inventory

Run this last to list what this session produced.
""")

code(r'''
rows = []
for d, kind in [(TABLES, "table"), (FIGURES, "figure"), (EXPORTS, "export")]:
    for p in sorted(d.iterdir()):
        if p.is_file():
            rows.append({"kind": kind, "name": p.name, "kB": round(p.stat().st_size / 1024, 1)})
inv = pd.DataFrame(rows)
print(f"{len(inv)} artefacts under {WB}")
display(inv)
''')
