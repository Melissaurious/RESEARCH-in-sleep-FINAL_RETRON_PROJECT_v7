# ============================== SECTION C ==============================
md(r"""
---

# C. ncRNA landscape

Two different things are counted in this section and must not be conflated: an **ncRNA call**
(a row of `rt_ncrna_calls_v1`, 346,722 of them) and an **exact ncRNA sequence**
(`nc_seq_hash`, 16,458 of them). A call is not a pair, and a pair is not a placement.

The single most important caveat for everything below: **the covariance models used are retron
models.** A zero-ncRNA rate outside the Retron family measures detector scope, not biology.
""")

md(r"""
## C1 — ncRNA call counts, and zero / one / multiple calls per RT locus

* **Question.** How many ncRNA calls exist, how do they distribute over loci, and what fraction of
  loci of each RT family carry no call at all?
* **Unit.** (i) ncRNA call (`V-NCRNA-CALL`); (ii) exact ncRNA sequence (`nc_seq_hash`);
  (iii) RT locus (`V-LOC`) for the zero/one/multiple split.
* **Denominator.** For the zero-class: **loci of that family label**, built from distinct raw
  records (`is_first_copy`) — the g3 denominator. MULTI is its own row.
* **Data.** `rt_ncrna_calls_v1`; `rt_ncrna_pairs_v1` → `locus_key`, `geometry_eligible`;
  `rt_records_v1` → `file_label`, `locus_key`, `n_ncrna`, `is_first_copy`.
""")

code(r'''
sizes = cache("C1_ncrna_view_sizes", """
    SELECT 'ncrna_calls (V-NCRNA-CALL)' AS view, count(*) AS n FROM rt_ncrna_calls
    UNION ALL SELECT 'placements, all',        count(*)                     FROM rt_ncrna_pairs
    UNION ALL SELECT 'placements, canonical',  count(*) FILTER (WHERE canonical) FROM rt_ncrna_pairs
    UNION ALL SELECT 'exact ncRNA sequences',  count(DISTINCT nc_seq_hash)  FROM rt_ncrna_calls
    UNION ALL SELECT 'exact RT-ncRNA pairs',   count(*)                     FROM rt_ncrna_exact_pairs
    UNION ALL SELECT 'loci carrying >=1 eligible call',
              count(DISTINCT locus_key) FILTER (WHERE geometry_eligible)    FROM rt_ncrna_pairs
""")
display(sizes)
print("against g3/g7:")
check("placements, all", int(sizes.loc[sizes.view == "placements, all", "n"].iloc[0]), "placements")
check("placements, canonical", int(sizes.loc[sizes.view == "placements, canonical", "n"].iloc[0]), "canonical")
check("exact RT-ncRNA pairs", int(sizes.loc[sizes.view == "exact RT-ncRNA pairs", "n"].iloc[0]), "pairs")

zero = cache("C1_zero_class_by_family", """
    SELECT file_label,
           count(DISTINCT locus_key)                                            AS n_loci,
           count(DISTINCT CASE WHEN n_ncrna > 0 THEN locus_key END)             AS n_loci_with_call,
           count(DISTINCT CASE WHEN n_ncrna = 0 THEN locus_key END)             AS n_loci_zero_ncrna
    FROM rt_records WHERE is_first_copy GROUP BY 1 ORDER BY n_loci DESC
""")
# A locus carries several records. If ANY record of a locus reported an ncRNA while another
# reported none, the locus would fall in both categories and the split would not be a partition.
# Verify rather than assume:
mixed = Q("""SELECT count(*) FILTER (WHERE mn = 0 AND mx > 0) AS mixed_loci, count(*) AS total_loci
             FROM (SELECT locus_key, min(n_ncrna) mn, max(n_ncrna) mx
                   FROM rt_records WHERE is_first_copy GROUP BY 1)""")
assert int(mixed.mixed_loci[0]) == 0, "zero/positive locus categories are NOT mutually exclusive"
print(f"  [OK] 0 of {int(mixed.total_loci[0]):,} loci have mixed records; "
      "the zero/positive split is a true partition.")
zero["pct_zero"] = (100 * zero.n_loci_zero_ncrna / zero.n_loci).round(4)
assert (zero.n_loci_with_call + zero.n_loci_zero_ncrna == zero.n_loci).all()
save(zero, "C1_zero_class_by_family")
display(zero.head(12))
print("\nagainst g3_zero_class_by_family:")
check("Retron  pct_zero", float(zero.loc[zero.file_label == "Retron", "pct_zero"].iloc[0]), "retron_zero", tol=1e-3)
check("RVT-GII pct_zero", float(zero.loc[zero.file_label == "RVT-GII", "pct_zero"].iloc[0]), "gii_zero", tol=1e-3)

perloc = cache("C1_calls_per_locus", """
    SELECT least(n_calls, 10) AS n_calls_capped, count(*) AS n_loci FROM (
      SELECT locus_key, count(*) AS n_calls FROM rt_ncrna_pairs
      WHERE geometry_eligible GROUP BY 1) GROUP BY 1 ORDER BY 1
""")
display(perloc)
''')

code(r'''
Z = pd.read_csv(TABLES / "C1_zero_class_by_family.tsv", sep="\t").head(14).iloc[::-1]
PL = pd.read_csv(TABLES / "C1_calls_per_locus.tsv", sep="\t")

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.2))
ax = axes[0]
cols = ["#b5533b" if f == "Retron" else "#9aa7b1" for f in Z.file_label]
ax.barh(Z.file_label, Z.pct_zero, color=cols, height=0.7)
ax.axvline(100, color="#444", lw=0.8, ls=":")
ax.set_xlim(0, 105); ax.set_xlabel("% of that family's loci with zero ncRNA call")
ax.set_title("C1 — zero-ncRNA rate by RT family\n(retron CMs: outside Retron this is detector scope)",
             fontsize=9.5, loc="left")

ax = axes[1]
ax.bar(PL.n_calls_capped, PL.n_loci, color="#3b6ea5", width=0.62)
ax.set_yscale("log"); ax.set_xlabel("ncRNA calls per locus (capped at 10)")
ax.set_ylabel("loci (log)")
ax.set_title("calls per locus, loci with ≥1 eligible call", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "C1_ncrna_call_landscape", pop=['PL-ALL']); plt.show()
''')

md(r"""
**Interpretation.** Retron loci carry a call **52.8 %** of the time (zero-rate 47.23 %); every
other family is at or above 99.9 % zero. That contrast is **not** evidence that non-Retron RTs lack
associated ncRNA — the models are retron models, so outside Retron this measures what the detector
can see. Among loci that do carry a call, the overwhelming majority carry exactly one; the
multi-call tail is small and is mostly the same call arriving from another record of the same
locus, not a second biological ncRNA (see the `multiplicity_class` breakdown in I).

**Caveat.** The denominator is *loci*, built from distinct raw records. A locus with no call and a
locus never examined by a CM look identical here. Any absence statement needs the positive control
in `results/dbchar_g3_pair_geometry/tables/c04_positive_controls.tsv`.
""")

md(r"""
## C2 — ncRNA length distribution

* **Question.** What length regime do the called ncRNAs occupy, and does it differ by covariance
  model?
* **Unit.** Exact ncRNA sequence (`nc_seq_hash`), 16,458.
* **Denominator.** Exact ncRNA sequences called by that model. **Every exact ncRNA sequence in
  this corpus is hit by exactly one model** (verified below: `n_models > 1` for 0 of 16,458), so
  the per-model counts **do** partition the 16,458 sequences and C2 (representative model) and C3
  (call-level model) cannot disagree about which model a sequence belongs to.
* **Data.** `ncrna_family_baseline_v1` → `nc_seq_hash`, `nc_seq_len`, `detection_model`,
  `n_models`, `n_placements`.
""")

code(r'''
nlen = cache("C2_ncrna_length_by_model", """
    SELECT detection_model, count(*) AS n_exact_ncrna,
           min(nc_seq_len) AS min,
           quantile_cont(nc_seq_len, 0.25) AS q25,
           quantile_cont(nc_seq_len, 0.50) AS median,
           quantile_cont(nc_seq_len, 0.75) AS q75,
           max(nc_seq_len) AS max
    FROM ncrna_family_baseline GROUP BY 1 ORDER BY n_exact_ncrna DESC
""")
display(nlen.head(16))

allb = Q("""SELECT count(*) AS n_exact_ncrna, min(nc_seq_len) AS min,
                   quantile_cont(nc_seq_len,0.25) AS q25, quantile_cont(nc_seq_len,0.50) AS median,
                   quantile_cont(nc_seq_len,0.75) AS q75, max(nc_seq_len) AS max,
                   count(*) FILTER (WHERE n_models > 1) AS n_multi_model,
                   count(*) FILTER (WHERE any_structure) AS n_with_structure
            FROM ncrna_family_baseline""")
print("\nall exact ncRNA sequences:"); display(allb)
assert int(allb.n_multi_model[0]) == 0, "an exact ncRNA is hit by >1 model; C2/C3 need reconciling"
assert int(nlen.n_exact_ncrna.sum()) == int(allb.n_exact_ncrna[0])
print(f"  [OK] per-model counts sum to {int(nlen.n_exact_ncrna.sum()):,} = every exact ncRNA "
      "sequence, each hit by exactly one model. C2 and C3 model labels are interchangeable.")

print("against g4_ncrna_length_by_model:")
g4n = gate_table("dbchar_g4_family_baseline", "g4_ncrna_length_by_model")
mm = nlen.merge(g4n[["detection_model", "n_exact_ncrna", "median"]], on="detection_model",
                suffixes=("", "_g4"))
print(f"  [{'MATCH' if (mm.n_exact_ncrna == mm.n_exact_ncrna_g4).all() and (mm['median'] == mm['median_g4']).all() else ' DIFF'}]"
      f" {len(mm)} models compared on (n, median)")
''')

code(r'''
N = pd.read_csv(TABLES / "C2_ncrna_length_by_model.tsv", sep="\t")
N = N[N.n_exact_ncrna >= 30].head(16).iloc[::-1]
stats = [dict(label=f"{r.detection_model}  (n={int(r.n_exact_ncrna):,})", med=r["median"],
              q1=r.q25, q3=r.q75, whislo=r["min"], whishi=r["max"], fliers=[])
         for _, r in N.iterrows()]

fig, ax = plt.subplots(figsize=(7.6, 5.2))
bp = ax.bxp(stats, vert=False, showfliers=False, patch_artist=True, widths=0.62)
for p in bp["boxes"]: p.set_facecolor("#4a8a72"); p.set_alpha(0.8); p.set_edgecolor("#2d5747")
for k in ("whiskers", "caps"):
    for p in bp[k]: p.set_color("#2d5747")
for p in bp["medians"]: p.set_color("#f2c14e"); p.set_linewidth(1.8)
ax.set_xlabel("ncRNA sequence length (nt) — box = IQR, whiskers = observed min/max")
ax.set_title("C2 — ncRNA length by detection model, exact sequences", fontsize=9.5, loc="left")
savefig(fig, "C2_ncrna_length_by_model", pop=['NC-ELIG']); plt.show()
''')

md(r"""
**Interpretation.** Called ncRNAs are tightly constrained: most models have an IQR narrower than
20 nt around a median of 120–170 nt, which is what a covariance-model hit *should* look like — the
model largely dictates the length of what it can match. Differences between models are therefore
first a statement about the model library and only second about msDNA/msr-msd architecture.

**Caveat.** Whiskers here are observed min/max, not Tukey fences, so single long hits stretch them.
These are **CM-hit lengths**, not independently established transcript boundaries: the model
largely dictates the extent of what it can match, so a per-model length is a statement about the
model as much as about the RNA. The two `Outgroup` models (`OutgroupA` 10,910 calls / 3,319
sequences, `OutgroupB` 2,018 / 338) are part of the shipped CM library; **their intended role is
not determinable from the corpus** and must be read from the myRT/PADLOC model documentation
before their hits are interpreted.
""")

md(r"""
## C3 — Model / CM-family composition

* **Question.** Which covariance models produce the corpus's ncRNA calls, and how different is the
  composition at call level versus exact-sequence level?
* **Unit.** (i) ncRNA call; (ii) exact ncRNA sequence.
* **Denominator.** All 346,722 calls / all 16,458 exact ncRNA sequences.
* **Data.** `rt_ncrna_calls_v1` → `detection_model`, `nc_seq_hash`, `score`, `evalue`,
  `nc_source`, `has_structure_annotation`.
""")

code(r'''
models = cache("C3_model_composition", """
    SELECT detection_model,
           count(*)                        AS n_calls,
           count(DISTINCT nc_seq_hash)     AS n_exact_ncrna,
           quantile_cont(score, 0.50)      AS median_score,
           quantile_cont(nc_seq_len, 0.50) AS median_len,
           count(*) FILTER (WHERE has_structure_annotation) AS n_with_structure
    FROM rt_ncrna_calls GROUP BY 1 ORDER BY n_calls DESC
""")
models["pct_of_calls"]     = (100 * models.n_calls / models.n_calls.sum()).round(2)
models["pct_of_exact_seq"] = (100 * models.n_exact_ncrna / models.n_exact_ncrna.sum()).round(2)
models["calls_per_exact_seq"] = (models.n_calls / models.n_exact_ncrna).round(1)
save(models, "C3_model_composition")
display(models)

src = Q("SELECT nc_source, count(*) AS n_calls FROM rt_ncrna_calls GROUP BY 1 ORDER BY 2 DESC")
print("\ncall source:"); display(src)
''')

code(r'''
M = pd.read_csv(TABLES / "C3_model_composition.tsv", sep="\t").head(16).iloc[::-1]

fig, ax = plt.subplots(figsize=(8.0, 4.8))
y = np.arange(len(M)); h = 0.38
ax.barh(y + h/2, M.pct_of_calls, height=h, color="#3b6ea5", label="% of ncRNA calls")
ax.barh(y - h/2, M.pct_of_exact_seq, height=h, color="#4a8a72", label="% of exact ncRNA sequences")
ax.set_yticks(y); ax.set_yticklabels(M.detection_model)
ax.set_xlabel("percent of its own denominator"); ax.legend(fontsize=8)
ax.set_title("C3 — CM composition: calls vs distinct sequences\n"
             "a gap means that model's hits are highly redundant", fontsize=9.5, loc="left")
savefig(fig, "C3_model_composition", pop=['PL-ALL', 'NC-ALL']); plt.show()
''')

md(r"""
**Interpretation.** Call-level and sequence-level composition disagree sharply for the largest
models: `TypeIA_IIAI` and `Ec107_like` produce far more calls per distinct sequence than
`OutgroupA` does. `calls_per_exact_seq` is the redundancy of that model's hits, and it is the same
sequencing-effort effect seen in A2 reappearing on the ncRNA side — a model matching an ncRNA that
sits in a hyper-deposited organism accumulates calls without accumulating diversity.

**Caveat.** Model names are retron subtype labels from the CM library; they are the detector's
vocabulary, not an independent taxonomy of msDNA. Score and E-value medians are comparable
*within* a model only.
""")

# ============================== SECTION D ==============================
md(r"""
---

# D. RT–ncRNA geometry

This is the priority biological output of Stage 1. Everything here is computed on the
**coordinate-derived** geometry (`direction`, `signed_distance_bp`, `same_strand`,
`n_cds_between`). The shipped `position_relative_to_rt` field is **not** used: it is null on
331,897 placements and matches no coordinate frame (artefact 2 in `CONTEXT.md`).
""")

md(r"""
## D1 — Direction: upstream / downstream / overlapping

* **Question.** Where does the ncRNA sit relative to its RT?
* **Unit.** Placement (`V-PAIR-PLACEMENT`).
* **Denominator.** `CANONICAL` placements = 344,154 (geometry-eligible and de-duplicated). The
  `ALL` population (346,722) is shown beside it so the denominator effect is visible.
* **Data.** `rt_ncrna_pairs_v1` → `direction`, `canonical`, `geometry_eligible`, `file_label`.
""")

code(r'''
direc = cache("D1_direction", """
    SELECT 'ALL' AS population, direction, count(*) AS n_placements FROM rt_ncrna_pairs GROUP BY 1,2
    UNION ALL
    SELECT 'ELIGIBLE', direction, count(*) FROM rt_ncrna_pairs WHERE geometry_eligible GROUP BY 1,2
    UNION ALL
    SELECT 'CANONICAL', direction, count(*) FROM rt_ncrna_pairs WHERE canonical GROUP BY 1,2
""")
piv = direc.pivot_table(index="direction", columns="population", values="n_placements", fill_value=0)
piv = piv[["ALL", "ELIGIBLE", "CANONICAL"]]
piv.loc["TOTAL"] = piv.sum()
piv["pct_of_CANONICAL"] = (100 * piv.CANONICAL / piv.loc["TOTAL", "CANONICAL"]).round(3)
display(piv)

print("against g3 / g7:")
for d, k in [("upstream", "up"), ("downstream", "down"), ("overlapping", "overlap")]:
    check(f"canonical {d}", int(piv.loc[d, "CANONICAL"]), k)

strand = cache("D1_same_strand", """
    SELECT canonical, same_strand, count(*) AS n FROM rt_ncrna_pairs GROUP BY 1,2
""")
s = strand[strand.canonical == True]
pct_same = 100 * s.loc[s.same_strand == True, "n"].sum() / s.n.sum()
print(f"\nsame strand, canonical placements: {pct_same:.3f}%  "
      f"(opposite: {int(s.loc[s.same_strand == False, 'n'].sum()):,})")

# g3_same_strand.tsv is the canonical source. NOTE: the g7 REPORT.md prose says "99.8%" for this
# quantity; that string is a hard-coded literal in g7_stage1_report/scripts/findings.py (every
# other number in that sentence is a resolved placeholder) and is NOT in g7_resolved_values.tsv.
# Check against the gate table, which is the authority. See notes/2026-09-16_same_strand_discrepancy.md
g3s = gate_table("dbchar_g3_pair_geometry", "g3_same_strand")
g3c = g3s[g3s.population == "CANONICAL"]
g3_pct = 100 * g3c.loc[g3c.same_strand == True, "n_placements"].sum() / g3c.n_placements.sum()
check("canonical same-strand % (vs g3_same_strand.tsv)", round(pct_same, 3),
      expected=round(g3_pct, 3), tol=1e-3)
print('  [ NOTE] g7 REPORT.md prose states "99.8%" for this quantity — an unregistered literal;'
      f' the gate table gives {g3_pct:.3f}%.')
''')

md(r"""
## D2 — Signed genomic distance, and the technical downstream mode

* **Question.** What is the gap distribution between RT and ncRNA, and what happens to it when the
  contig-start-clipped windows are separated out?
* **Unit.** Placement (`V-PAIR-PLACEMENT`), `CANONICAL`.
* **Denominator.** 344,154 canonical placements; the stratified panel uses the same placements
  split by `true_start_clipped`.
* **Data.** `rt_ncrna_pairs_v1` → `signed_distance_bp`, `direction`, `canonical`,
  `true_start_clipped`, `clipped_end_flag`.
* **Convention.** Negative = ncRNA upstream of the RT; 0 = overlapping; positive = downstream.
""")

code(r'''
dstats = cache("D2_distance_stats", """
    SELECT 'CANONICAL' AS population, direction, count(*) AS n,
           quantile_cont(signed_distance_bp, 0.25) AS q25,
           quantile_cont(signed_distance_bp, 0.50) AS median,
           quantile_cont(signed_distance_bp, 0.75) AS q75,
           min(signed_distance_bp) AS min, max(signed_distance_bp) AS max
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1,2
    UNION ALL
    SELECT 'CANONICAL_by_clip: ' || CASE WHEN true_start_clipped THEN 'true_start_clipped'
                                         ELSE 'not_clipped' END,
           direction, count(*), quantile_cont(signed_distance_bp, 0.25),
           quantile_cont(signed_distance_bp, 0.50), quantile_cont(signed_distance_bp, 0.75),
           min(signed_distance_bp), max(signed_distance_bp)
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1,2
    ORDER BY population, direction
""")
display(dstats)
check("canonical upstream median bp",
      float(dstats[(dstats.population == "CANONICAL") & (dstats.direction == "upstream")]["median"].iloc[0]),
      "up_median")

# THE DOWNSTREAM POPULATION IS NOT THE TECHNICAL MODE. g3 defines "the mode" as the placements
# within +/-150 bp of the downstream median (2,682 bp); that is a SUBSET of all downstream
# placements. Reporting "18 distinct ncRNAs" against the whole downstream population overstates
# how narrow it is. Both are computed here with their own denominators.
g3p = gate_table("dbchar_g3_pair_geometry", "g3_downstream_mode_profile").set_index("measure")["value"]
MODE_MEDIAN, MODE_HALFWIDTH = float(g3p["median_signed_distance_bp"]), 150.0

dmode = cache("D2_downstream_strata", f"""
    SELECT 'all canonical downstream' AS stratum, count(*) AS n_placements,
           count(DISTINCT nc_seq_hash) AS n_exact_ncrna, count(DISTINCT rt_seq_hash) AS n_exact_rt,
           count(DISTINCT detection_model) AS n_models,
           quantile_cont(signed_distance_bp, 0.50) AS median_bp,
           100.0 * count(*) FILTER (WHERE true_start_clipped) / count(*) AS pct_true_start_clipped
    FROM rt_ncrna_pairs WHERE canonical AND direction = 'downstream'
    UNION ALL SELECT 'THE MODE: within +/-{MODE_HALFWIDTH:.0f} bp of {MODE_MEDIAN:.0f} bp',
           count(*), count(DISTINCT nc_seq_hash), count(DISTINCT rt_seq_hash),
           count(DISTINCT detection_model), quantile_cont(signed_distance_bp, 0.50),
           100.0 * count(*) FILTER (WHERE true_start_clipped) / count(*)
    FROM rt_ncrna_pairs WHERE canonical AND direction = 'downstream'
      AND abs(signed_distance_bp - {MODE_MEDIAN}) <= {MODE_HALFWIDTH}
    UNION ALL SELECT 'downstream, contig-start-clipped', count(*), count(DISTINCT nc_seq_hash),
           count(DISTINCT rt_seq_hash), count(DISTINCT detection_model),
           quantile_cont(signed_distance_bp, 0.50),
           100.0 * count(*) FILTER (WHERE true_start_clipped) / count(*)
    FROM rt_ncrna_pairs WHERE canonical AND direction = 'downstream' AND true_start_clipped
    UNION ALL SELECT 'downstream, NOT clipped (near-range)', count(*), count(DISTINCT nc_seq_hash),
           count(DISTINCT rt_seq_hash), count(DISTINCT detection_model),
           quantile_cont(signed_distance_bp, 0.50),
           100.0 * count(*) FILTER (WHERE true_start_clipped) / count(*)
    FROM rt_ncrna_pairs WHERE canonical AND direction = 'downstream' AND NOT true_start_clipped
""")
display(dmode.round(2))
check("distinct exact ncRNA in THE MODE",
      int(dmode.loc[dmode.stratum.str.startswith("THE MODE"), "n_exact_ncrna"].iloc[0]),
      "dmode_seqs")
print(f"\n  all canonical downstream carries "
      f"{int(dmode.n_exact_ncrna.iloc[0])} distinct exact ncRNAs, NOT the 18 of the mode.")
print("  the unclipped downstream remainder sits at a median "
      f"{dmode.loc[dmode.stratum.str.contains('NOT clipped'), 'median_bp'].iloc[0]:.0f} bp — "
      "near-range, and NOT explained by the clipping artefact.")
''')

code(r'''
hist = cache("D2_distance_histogram", """
    SELECT CASE WHEN true_start_clipped THEN 'true_start_clipped' ELSE 'not_clipped' END AS stratum,
           50 * floor(signed_distance_bp / 50.0) AS bin_start,
           count(*) AS n
    FROM rt_ncrna_pairs
    WHERE canonical AND signed_distance_bp BETWEEN -3000 AND 4000
    GROUP BY 1, 2 ORDER BY 1, 2
""")
H = pd.read_csv(TABLES / "D2_distance_histogram.tsv", sep="\t")

fig, axes = plt.subplots(2, 1, figsize=(8.4, 5.4), sharex=True)
for ax, (stratum, color) in zip(axes, [("not_clipped", "#3b6ea5"), ("true_start_clipped", "#b5533b")]):
    h = H[H.stratum == stratum]
    ax.bar(h.bin_start, h.n, width=48, color=color, align="edge")
    ax.set_yscale("log"); ax.set_ylabel("placements (log)")
    ax.axvline(0, color="#444", lw=0.9, ls=":")
    ax.set_title(f"{stratum}  (n={int(h.n.sum()):,} in −3,000…4,000 bp)", fontsize=9, loc="left")
axes[1].set_xlabel("signed distance RT→ncRNA (bp, 50-bp bins) · negative = ncRNA upstream")
axes[0].annotate("canonical upstream mode\n(median −55 bp)", xy=(-55, 1), xytext=(-2700, 3e3),
                 fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
axes[1].annotate("technical downstream mode\n≈2,682 bp — window starts at the contig start,\n"
                 "so any call is forced downstream", xy=(2682, 1), xytext=(900, 2e3),
                 fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
fig.suptitle("D2 — signed RT→ncRNA distance, canonical placements, split by contig-start clipping",
             fontsize=10, x=0.01, ha="left")
fig.tight_layout(); savefig(fig, "D2_distance_distribution", pop=['PL-CANON']); plt.show()
''')

md(r"""
**Interpretation.** The biological signal is a tight upstream mode at a median **−55 bp**: the
ncRNA sits immediately 5′ of the RT, typically with no intervening CDS (D3). The apparently
bimodal distance distribution resolves once the strata are separated — the second mode at
~2,682 bp lives almost entirely in the `true_start_clipped` stratum, contains only 18 distinct
ncRNA sequences, and is an artefact of windows that begin at the contig start, where any call is
*forced* to appear downstream.

**Two populations must not be conflated here.** *All* canonical downstream placements number
**6,761 over 230 distinct exact ncRNA sequences**. *The technical mode* — defined by g3 as the
placements within ±150 bp of the 2,682 bp downstream median — is **5,234 placements (77.4 % of
downstream) over just 18 distinct ncRNA sequences, 126 exact RTs and 15 species, dominated by a
single `ncbi_bacteria` / Retron / `TypeV` stratum that is 99.96 % contig-start-clipped**. The
"18 sequences" figure belongs to the mode, not to downstream placements generally.

Separating the strata also surfaces something the artefact was hiding: the **1,041 downstream
placements that are *not* contig-start-clipped sit at a median of only 64 bp over 149 distinct
ncRNA sequences** — a genuine near-range downstream population that the technical mode does not
explain and that deserves its own examination.

**Caveat.** Do not use the technical mode as a prior for anything. Overlapping placements are
reported as distance 0 by construction, so the zero bin is a category, not a measurement. The
near-range unclipped downstream group above is a *description*; whether those are inverted
arrangements, mis-assigned RT boundaries or a distinct architecture is not established here.
""")

md(r"""
## D3 — Intervening CDS and strand

* **Question.** How often is the RT–ncRNA arrangement a clean operon-like adjacency, with nothing
  transcribed between them?
* **Unit.** Placement (`V-PAIR-PLACEMENT`), `CANONICAL`.
* **Denominator.** 344,154 canonical placements.
* **Data.** `rt_ncrna_pairs_v1` → `n_cds_between`, `cds_between_bin`, `same_strand`,
  `overlaps_rt_cds`, `overlaps_non_rt_cds`.
""")

code(r'''
cds = cache("D3_cds_between", """
    SELECT CASE WHEN n_cds_between >= 4 THEN '>3' ELSE CAST(n_cds_between AS VARCHAR) END AS n_cds_between,
           least(n_cds_between, 4) AS ord, count(*) AS n_placements
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1, 2 ORDER BY ord
""")
tot = cds.n_placements.sum()
cds["pct_of_canonical"] = (100 * cds.n_placements / tot).round(4)
save(cds, "D3_cds_between")
display(cds[["n_cds_between", "n_placements", "pct_of_canonical"]])
print("against g3_cds_between_explicit:")
for lab, key in [("0", "cds0"), ("1", "cds1"), (">3", "cds_gt3")]:
    check(f"{lab} CDS between", float(cds.loc[cds.n_cds_between == lab, "pct_of_canonical"].iloc[0]),
          key, tol=1e-3)

ov = cache("D3_overlap_profile", """
    SELECT overlaps_rt_cds, overlaps_non_rt_cds, same_strand, count(*) AS n
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1,2,3 ORDER BY n DESC
""")
display(ov.head(10))
''')

code(r'''
Cd = pd.read_csv(TABLES / "D3_cds_between.tsv", sep="\t").sort_values("ord")
St = pd.read_csv(TABLES / "D1_same_strand.tsv", sep="\t")
St = St[St.canonical == True]

fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.4))
ax = axes[0]
ax.bar(Cd.n_cds_between.astype(str), Cd.pct_of_canonical, color="#3b6ea5", width=0.62)
for x, v in zip(range(len(Cd)), Cd.pct_of_canonical):
    ax.text(x, v * 1.35, f"{v:.2f}%", ha="center", fontsize=8)
ax.set_yscale("log"); ax.set_ylim(0.05, 400)
ax.set_xlabel("CDS between RT and ncRNA"); ax.set_ylabel("% of canonical placements (log)")
ax.set_title("D3 — intervening CDS", fontsize=9.5, loc="left")

ax = axes[1]
lab = ["same strand" if b else "opposite strand" for b in St.same_strand]
ax.bar(lab, 100 * St.n / St.n.sum(), color=["#3b6ea5", "#b5533b"], width=0.5)
for x, v in enumerate(100 * St.n.values / St.n.sum()):
    ax.text(x, v + 2, f"{v:.2f}%", ha="center", fontsize=8.5)
ax.set_ylim(0, 112); ax.set_ylabel("% of canonical placements")
ax.set_title("strand agreement", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "D3_cds_and_strand", pop=['PL-CANON']); plt.show()
''')

md(r"""
**Interpretation.** **94.41 %** of canonical placements have *no* CDS between the RT and its ncRNA,
and **99.12 %** are on the same strand (`g3_same_strand.tsv`; the g7 report prose says 99.8 %, an
unregistered literal — see D1 and `notes/`). Combined with the −55 bp median gap of D2, the dominant
genomic arrangement is a close, same-strand, 5′ adjacency with no annotated CDS between the two
features. **This is an arrangement, not a demonstrated transcriptional relationship** — these
coordinates are compatible with cotranscription but do not establish it, and nothing here speaks
to cognate RT–ncRNA recognition. The ~5.6 % with intervening CDS and the ~0.88 % opposite-strand cases (3,041 placements) are retained as
atypical biology, not filtered (project convention).

**Caveat.** `n_cds_between` depends on the annotation present in the extracted window. A window
with sparse Prodigal calls will show "0 CDS between" for a reason that is annotational, not
genomic. Overlapping placements are their own category and by definition have no gap to populate.
""")

md(r"""
## D4 — Geometry by RT family

* **Question.** Do the non-Retron families whose loci *do* carry a retron-CM call show the same
  geometry as Retron loci?
* **Unit.** Placement (`V-PAIR-PLACEMENT`), geometry-eligible.
* **Denominator.** Eligible placements **of that family label**. Note how small the non-Retron
  denominators are — this is the detector-scope effect of C1, not a family-size effect.
* **Data.** `rt_ncrna_pairs_v1` → `file_label`, `direction`, `same_strand`,
  `signed_distance_bp`, `n_cds_between`, `geometry_eligible`.
""")

code(r'''
geo = cache("D4_geometry_by_family", """
    SELECT file_label, count(*) AS n_placements,
           100.0 * count(*) FILTER (WHERE direction = 'upstream')    / count(*) AS pct_upstream,
           100.0 * count(*) FILTER (WHERE direction = 'downstream')  / count(*) AS pct_downstream,
           100.0 * count(*) FILTER (WHERE direction = 'overlapping') / count(*) AS pct_overlapping,
           100.0 * count(*) FILTER (WHERE same_strand)               / count(*) AS pct_same_strand,
           100.0 * count(*) FILTER (WHERE n_cds_between = 0)         / count(*) AS pct_no_cds_between,
           quantile_cont(signed_distance_bp, 0.50)                              AS median_signed_bp,
           count(DISTINCT nc_seq_hash)                                          AS n_exact_ncrna
    FROM rt_ncrna_pairs WHERE geometry_eligible
    GROUP BY 1 ORDER BY n_placements DESC
""")
display(geo.round(2))
print("\nnon-Retron single-family eligible placements (the g3 candidate population):")
nr = geo[(geo.file_label != "Retron") & (geo.file_label != "MULTI")]
print(f"  n_placements = {int(nr.n_placements.sum()):,}   "
      f"pct_upstream = {100 * (nr.pct_upstream * nr.n_placements / 100).sum() / nr.n_placements.sum():.3f}%")
check("non-Retron eligible placements", int(nr.n_placements.sum()), "nonretron")
''')

code(r'''
G = pd.read_csv(TABLES / "D4_geometry_by_family.tsv", sep="\t")
G = G[G.n_placements >= 5].sort_values("n_placements", ascending=False).head(12).iloc[::-1]

fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.0), sharey=True)
y = np.arange(len(G))
ax = axes[0]
left = np.zeros(len(G))
for col, c, lab in [("pct_upstream", "#3b6ea5", "upstream"),
                    ("pct_overlapping", "#7fa8cc", "overlapping"),
                    ("pct_downstream", "#b5533b", "downstream")]:
    ax.barh(y, G[col], left=left, color=c, label=lab, height=0.68); left += G[col].values
ax.set_yticks(y)
ax.set_yticklabels([f"{f}  (n={int(n):,})" for f, n in zip(G.file_label, G.n_placements)])
ax.set_xlim(0, 100); ax.set_xlabel("% of that family's eligible placements")
ax.legend(fontsize=8, loc="lower left", framealpha=0.9)
ax.set_title("D4 — direction by RT family", fontsize=9.5, loc="left")

ax = axes[1]
h = 0.38
ax.barh(y + h/2, G.pct_same_strand, height=h, color="#4a8a72", label="same strand")
ax.barh(y - h/2, G.pct_no_cds_between, height=h, color="#9aa7b1", label="no CDS between")
ax.set_xlim(0, 100); ax.set_xlabel("% of that family's eligible placements"); ax.legend(fontsize=8)
ax.set_title("strand agreement and adjacency", fontsize=9.5, loc="left")
fig.tight_layout(); savefig(fig, "D4_geometry_by_family", pop=['PL-CANON']); plt.show()
''')

md(r"""
**Interpretation.** Retron placements dominate the eligible population and set the canonical
geometry. The non-Retron families that carry a retron-CM call amount to only a few hundred
placements in total, with a markedly weaker upstream preference (~57.7 % vs Retron's ~95 %). Stage 1
retains these as a **candidate** population and explicitly does **not** call them novel retrons.

**Caveat.** The per-family denominators here differ by four orders of magnitude, so a percentage on
a family with n < 50 is not comparable to Retron's. These placements exist because a retron CM
matched next to a non-Retron RT; the first hypotheses to exclude are CM cross-matching and
RT-family mislabelling, not novel biology. The 266-row candidate table
(`rt_ncrna_nonretron_candidates_v1`) is examined in section I — note that the report's **260** is
its single-family subset, with 6 MULTI rows held out.
""")
