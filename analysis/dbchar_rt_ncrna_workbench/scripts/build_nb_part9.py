md(r"""
---

# N. Thesis figure set

The figures the thesis chapter uses, built to the agreed denominators. Each cell caches its table
and writes a PNG **and** a PDF so the panels go into LaTeX as vector art.
""")

code(r'''
import matplotlib.gridspec as gridspec
from matplotlib_venn import venn3

def savefig2(fig, name, sources=None, section="N", pop=None):
    """PNG for the notebook, PDF for LaTeX. `pop` stamps the Z0 population onto the figure."""
    savefig(fig, name, sources=sources, section=section, pop=pop)
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")
    return FIGURES / f"{name}.png"

BLUE, RED, GREEN, GREY, PURPLE = "#3b6ea5", "#b5533b", "#4a8a72", "#9aa7b1", "#7B4FA8"
print("N ready")
''')

md(r"""
## N1 — Tool agreement on distinct RT proteins, with ncRNA recovery

* **Unit.** Distinct Retron RT protein (primary); distinct record (supplementary panel).
* **Denominator.** Retron records / the distinct proteins they carry.
* **Point.** myRT alone contributes more distinct proteins than the three-tool intersection, while
  the intersection dominates on records. The axis changes the conclusion.
""")

code(r'''
# A protein may appear in several records detected by different tool sets. A protein-level Venn
# must therefore aggregate tools ACROSS all records of that protein (a protein is "detected by
# myRT" if ANY of its records was), otherwise the sets overlap and sum above the true total.
prot = cache("N1_tool_sets_protein", """
    WITH p AS (
      SELECT rt_seq_hash,
             bool_or(by_myRT)         AS by_myRT,
             bool_or(by_PADLOC)       AS by_PADLOC,
             bool_or(by_DefenseFinder)AS by_DefenseFinder,
             bool_or(n_ncrna > 0)     AS has_ncrna
      FROM rt_tool_calls WHERE file_label = 'Retron' GROUP BY 1)
    SELECT by_myRT, by_PADLOC, by_DefenseFinder,
           count(*) AS n_exact_rt,
           100.0 * count(*) FILTER (WHERE has_ncrna) / count(*) AS pct_exact_rt_with_ncrna
    FROM p GROUP BY 1,2,3 ORDER BY n_exact_rt DESC
""", pop="RT-BASE-1F")
prot["tool_set"] = ["|".join([n for n, v in
                    [("myRT", r.by_myRT), ("PADLOC", r.by_PADLOC),
                     ("DefenseFinder", r.by_DefenseFinder)] if v])
                    for r in prot.itertuples()]
save(prot, "N1_tool_sets_protein")
print(f"protein-level Venn total: {int(prot.n_exact_rt.sum()):,} distinct Retron RT proteins")
display(prot[["tool_set", "n_exact_rt", "pct_exact_rt_with_ncrna"]].round(2))

# RECORD level only. This table deliberately carries NO protein column: a protein detected by
# myRT in one record and by all three in another belongs to two rows here, so a per-row distinct
# protein count double-counts and sums to 84,032 against a true 78,287. The protein axis lives
# in N1_tool_sets_protein above and nowhere else.
tools = cache("N1_tool_sets", """
    SELECT detected_by_set, n_tools, by_myRT, by_PADLOC, by_DefenseFinder,
           count(*) AS n_records,
           100.0 * count(*) FILTER (WHERE n_ncrna > 0) / count(*) AS pct_records_with_ncrna
    FROM rt_tool_calls WHERE file_label = 'Retron'
    GROUP BY 1,2,3,4,5 ORDER BY n_records DESC
""", pop="REC-DIST")
save(tools, "N1_tool_sets")
display(tools[["detected_by_set", "n_records", "pct_records_with_ncrna"]].round(2))
print("  record axis only — for proteins use N1_tool_sets_protein (78,287, a true partition).")

cm_tool = cache("N1_cm_by_tool_set", """
    SELECT p.detection_model, t.detected_by_set, count(*) AS n_calls
    FROM rt_ncrna_pairs p JOIN rt_tool_calls t ON p.record_key = t.record_key
    WHERE p.canonical GROUP BY 1,2 ORDER BY n_calls DESC
""", pop="PL-CANON")
print(f"\ncovariance model x tool set: {len(cm_tool)} combinations")
display(cm_tool.head(8))
''')

code(r'''
T  = pd.read_csv(TABLES / "N1_tool_sets.tsv", sep="\t")          # record level
PR = pd.read_csv(TABLES / "N1_tool_sets_protein.tsv", sep="\t")  # protein level (true partition)
def subset(df, col, on):
    r = df[(df.by_myRT == on[0]) & (df.by_PADLOC == on[1]) & (df.by_DefenseFinder == on[2])]
    return int(r[col].iloc[0]) if len(r) else 0

fig = plt.figure(figsize=(13.2, 4.6))
gs  = gridspec.GridSpec(1, 3, width_ratios=[1.15, 1.15, 1.5], wspace=0.28)

for k, (df, col, ttl) in enumerate([(PR, "n_exact_rt", "distinct RT proteins"),
                                    (T,  "n_records",  "records")]):
    ax = fig.add_subplot(gs[0, k])
    sets = (subset(df, col, (1,0,0)), subset(df, col, (0,1,0)), subset(df, col, (1,1,0)),
            subset(df, col, (0,0,1)), subset(df, col, (1,0,1)), subset(df, col, (0,1,1)),
            subset(df, col, (1,1,1)))
    v = venn3(subsets=sets, set_labels=("myRT", "PADLOC", "DefenseFinder") if k == 0 else ("", "", ""),
              ax=ax)
    for patch, colr in zip(v.patches, [BLUE, RED, "#8a6fb0", GREEN, "#6f9bb0", "#b08a6f", GREY]):
        if patch: patch.set_color(colr); patch.set_alpha(0.62); patch.set_edgecolor("white")
    for t in (v.set_labels or []):
        if t: t.set_fontsize(9); t.set_fontweight("bold")
    for t in (v.subset_labels or []):
        if t: t.set_fontsize(7.6)
    ax.set_title(f"{ttl}\n(n = {sum(sets):,})", fontsize=9.5, loc="left")

ax = fig.add_subplot(gs[0, 2])
d = T.merge(PR[["tool_set", "pct_exact_rt_with_ncrna"]].rename(
        columns={"tool_set": "detected_by_set",
                 "pct_exact_rt_with_ncrna": "pct_protein_ncrna"}),
        on="detected_by_set", how="left").sort_values("pct_protein_ncrna")
y = np.arange(len(d)); h = 0.38
ax.barh(y + h/2, d.pct_protein_ncrna, height=h, color=BLUE, label="% of distinct proteins")
ax.barh(y - h/2, d.pct_records_with_ncrna,  height=h, color=GREY, label="% of records")
for i, r in enumerate(d.itertuples()):
    ax.text(r.pct_protein_ncrna + 1.2, i + h/2, f"{r.pct_protein_ncrna:.0f}%",
            va="center", fontsize=7.4)
ax.set_yticks(y)
ax.set_yticklabels([s.replace("|", "+") for s in d.detected_by_set], fontsize=7.8)
ax.set_xlim(0, 104); ax.set_xlabel("carrying at least one ncRNA call (%)")
ax.legend(fontsize=7.6, loc="lower right")
ax.set_title("ncRNA recovery by detecting-tool set", fontsize=9.5, loc="left")

fig.suptitle("Detection route determines both what is found and what appears associated "
             "— tools share model lineage, so agreement is not independent corroboration",
             fontsize=9, x=0.005, ha="left", y=1.04, color="#555555")
savefig2(fig, "N1_tool_venn", sources=["N1_tool_sets_protein", "N1_tool_sets"],
         pop=["RT-BASE-1F", "REC-DIST"]); plt.show()
''')

md(r"""
## N2 — RT family composition, all families, records versus distinct proteins

* **Unit.** Distinct record and distinct RT protein, side by side.
* **Denominator.** Each bar against its own population; the **gap between the bars is the
  redundancy**.
""")

code(r'''
famall = cache("N2_family_all", f"""
    WITH rt AS (SELECT family_label, count(*) AS n_exact_rt
                FROM rt_family_baseline WHERE view = 'V-RT-SINGLE' GROUP BY 1),
         rec AS (SELECT file_label AS family_label, count(*) AS n_records
                 FROM rt_records WHERE {POP_RT_SEQ} GROUP BY 1)
    SELECT rt.family_label, rt.n_exact_rt, rec.n_records
    FROM rt JOIN rec USING (family_label) ORDER BY rt.n_exact_rt DESC
""", pop=["RT-BASE-1F", "RT-SEQ"])
famall["pct_exact_rt"] = (100 * famall.n_exact_rt / famall.n_exact_rt.sum()).round(4)
famall["pct_records"]  = (100 * famall.n_records  / famall.n_records.sum()).round(4)
famall["records_per_protein"] = (famall.n_records / famall.n_exact_rt).round(2)
save(famall, "N2_family_all")
print(f"{len(famall)} single-family labels")
display(famall.head(10))
print("\nmost redundant families (records per distinct protein):")
display(famall.nlargest(5, "records_per_protein")[["family_label", "n_records",
                                                   "n_exact_rt", "records_per_protein"]])
''')

code(r'''
F = pd.read_csv(TABLES / "N2_family_all.tsv", sep="\t").iloc[::-1]
fig, axes = plt.subplots(1, 2, figsize=(12.6, 8.4), sharey=True,
                         gridspec_kw={"width_ratios": [2.1, 1]})
y = np.arange(len(F)); h = 0.38
ax = axes[0]
ax.barh(y + h/2, F.pct_exact_rt, height=h, color=BLUE, label="% of distinct RT proteins")
ax.barh(y - h/2, F.pct_records,  height=h, color=GREY, label="% of records")
ax.set_yticks(y); ax.set_yticklabels(F.family_label, fontsize=7.4)
ax.set_xscale("log"); ax.set_xlim(1e-3, 120)
ax.set_xlabel("percent of its own population (log)")
ax.legend(fontsize=8, loc="lower right")
ax.set_title("N2 — RT family composition, all 41 single-family labels", fontsize=9.5, loc="left")

ax = axes[1]
cols = [RED if v >= 10 else BLUE for v in F.records_per_protein]
ax.barh(y, F.records_per_protein, color=cols, height=0.66)
ax.axvline(F.n_records.sum() / F.n_exact_rt.sum(), color="#444", ls=":", lw=1,
           label="corpus mean")
ax.set_xscale("log"); ax.set_xlabel("records per distinct protein (log)")
ax.legend(fontsize=7.5)
ax.set_title("redundancy: how often the same protein was deposited", fontsize=9.5, loc="left")
fig.tight_layout()
savefig2(fig, "N2_family_composition_all", pop=["RT-BASE-1F", "RT-SEQ"], sources=["N2_family_all"]); plt.show()
''')

md(r"""
## N3 — RT length, stratified by completeness

* **Unit.** Distinct RT protein (`V-RT-SINGLE`). Exact-sequence identity, so an upper bound on
  distinctness pending clustering.
* **Denominator.** Proteins of that family, split by completeness — partial calls are short by
  construction, so pooling them understates every family's length.
""")

code(r'''
lenc = cache("N3_length_by_family_completeness", """
    SELECT family_label, completeness_class, count(*) AS n,
           min(rt_aa_len) AS min, quantile_cont(rt_aa_len, 0.25) AS q25,
           quantile_cont(rt_aa_len, 0.50) AS median, quantile_cont(rt_aa_len, 0.75) AS q75,
           max(rt_aa_len) AS max, avg(rt_aa_len) AS mean, stddev(rt_aa_len) AS sd
    FROM rt_family_baseline WHERE view = 'V-RT-SINGLE'
    GROUP BY 1, 2
""")
save(lenc, "N3_length_by_family_completeness")
comp_only = lenc[lenc.completeness_class == "all_complete"].nlargest(12, "n")
display(comp_only[["family_label", "n", "min", "q25", "median", "q75", "max", "mean", "sd"]].round(1))

shift = cache("N3_completeness_length_shift", """
    SELECT completeness_class, count(*) AS n_exact_rt,
           quantile_cont(rt_aa_len, 0.50) AS median_aa
    FROM rt_family_baseline WHERE view = 'V-RT-SINGLE' GROUP BY 1 ORDER BY n_exact_rt DESC
""")
display(shift)
print("  partial calls are shorter by construction — pooling them lowers every family's median.")
''')

code(r'''
L = pd.read_csv(TABLES / "N3_length_by_family_completeness.tsv", sep="\t")
fams = (L[L.completeness_class == "all_complete"].nlargest(12, "n").family_label.tolist())[::-1]

fig, axes = plt.subplots(1, 2, figsize=(12.4, 5.4), sharey=True,
                         gridspec_kw={"width_ratios": [2.3, 1]})
ax = axes[0]
for i, fam in enumerate(fams):
    for cls, colr, off in [("all_complete", BLUE, 0.17), ("all_partial", RED, -0.17)]:
        r = L[(L.family_label == fam) & (L.completeness_class == cls)]
        if r.empty: continue
        r = r.iloc[0]
        ax.plot([r.q25, r.q75], [i + off] * 2, color=colr, lw=5.5, solid_capstyle="butt",
                alpha=0.85, zorder=2)
        whislo = max(r["min"], r.q25 - 1.5 * (r.q75 - r.q25))
        whishi = min(r["max"], r.q75 + 1.5 * (r.q75 - r.q25))
        ax.plot([whislo, whishi], [i + off] * 2, color=colr, lw=0.9, zorder=1)
        ax.plot([r["median"]], [i + off], marker="|", color="#F2C14E", ms=9, mew=1.8, zorder=3)
ax.set_yticks(range(len(fams))); ax.set_yticklabels(fams, fontsize=8)
ax.set_xlabel("RT protein length (aa) — bar = IQR, whisker = Tukey, gold = median")
ax.set_xlim(0, 1250)
ax.plot([], [], color=BLUE, lw=5, label="complete calls"); ax.plot([], [], color=RED, lw=5,
        label="partial calls")
ax.legend(fontsize=8, loc="lower right")
ax.set_title("N3 — RT length by family, split by call completeness", fontsize=9.5, loc="left")

ax = axes[1]
tbl = L[(L.completeness_class == "all_complete") & (L.family_label.isin(fams))].set_index("family_label")
# `fams` is reversed so that matplotlib draws the largest family at the TOP of the y-axis.
# ax.table draws its rows top-DOWN, so it must be fed the un-reversed order, or every row of
# the table lines up against the wrong family. (It did, until 2026-09-17.)
rows = [[f, f"{int(tbl.loc[f,'n']):,}", f"{tbl.loc[f,'median']:.0f}",
         f"{tbl.loc[f,'q25']:.0f}–{tbl.loc[f,'q75']:.0f}", f"{tbl.loc[f,'sd']:.0f}"]
        for f in fams[::-1]]
ax.axis("off")
t = ax.table(cellText=rows, colLabels=["family", "n", "median", "IQR", "SD"],
             cellLoc="center", loc="center", bbox=[0, 0, 1, 1])
t.auto_set_font_size(False); t.set_fontsize(7.6)
for (r, cc), cell in t.get_celld().items():
    cell.set_linewidth(0.4); cell.set_edgecolor("#DDDDDD")
    if r == 0: cell.set_text_props(fontweight="bold"); cell.set_facecolor("#F2F2F2")
ax.set_title("complete calls only", fontsize=9.5, loc="left")
fig.tight_layout()
savefig2(fig, "N3_rt_length_by_completeness", sources=["N3_length_by_family_completeness"],
         pop="RT-BASE-1F"); plt.show()
''')

md(r"""
## N4 — RT family × covariance model

* **Unit.** Canonical placement.
* **Denominator.** All canonical placements.
* **Circularity caveat, on the figure.** The models are retron models. Near-absence outside Retron
  is partly expected; this shows *what the retron models find across families*, never *which
  families lack ncRNAs*.
""")

code(r'''
fxm = cache("N4_family_x_model", """
    SELECT file_label, detection_model, count(*) AS n_placements,
           count(DISTINCT nc_seq_hash) AS n_exact_ncrna
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1, 2
""")
save(fxm, "N4_family_x_model")
piv = fxm.pivot_table(index="file_label", columns="detection_model",
                      values="n_placements", fill_value=0)
piv = piv.loc[piv.sum(1).sort_values(ascending=False).index,
              piv.sum(0).sort_values(ascending=False).index]
display(piv.iloc[:8, :8])
nonret = fxm[~fxm.file_label.isin(["Retron", "MULTI"])]
print(f"\nnon-Retron families with any retron-CM call: {nonret.file_label.nunique()}")
print(f"non-Retron placements: {int(nonret.n_placements.sum()):,} of {int(fxm.n_placements.sum()):,}"
      f" ({100*nonret.n_placements.sum()/fxm.n_placements.sum():.3f}%)")
''')

code(r'''
from matplotlib.colors import LogNorm, LinearSegmentedColormap
SEQ = LinearSegmentedColormap.from_list("b", ["#f2f7fe", "#cde2fb", "#86b6ef",
                                              "#3987e5", "#1c5cab", "#0d366b"])
P4 = pd.read_csv(TABLES / "N4_family_x_model.tsv", sep="\t")
piv = P4.pivot_table(index="file_label", columns="detection_model",
                     values="n_placements", fill_value=0)
piv = piv.loc[piv.sum(1).sort_values(ascending=False).index[:14],
              piv.sum(0).sort_values(ascending=False).index[:18]]

fig, ax = plt.subplots(figsize=(11.2, 5.0))
data = piv.to_numpy().astype(float)
im = ax.imshow(np.where(data > 0, data, np.nan), cmap=SEQ, aspect="auto",
               norm=LogNorm(vmin=1, vmax=np.nanmax(data)))
ax.set_xticks(range(piv.shape[1])); ax.set_xticklabels(piv.columns, rotation=45, ha="right", fontsize=7)
ax.set_yticks(range(piv.shape[0])); ax.set_yticklabels(piv.index, fontsize=8)
ax.tick_params(length=0)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        if data[i, j] > 0:
            ax.text(j, i, f"{int(data[i,j]):,}", ha="center", va="center", fontsize=5.6,
                    color="white" if data[i, j] > np.nanmax(data) * 0.02 else "#333333")
cb = fig.colorbar(im, ax=ax, shrink=0.85); cb.set_label("canonical placements (log)", fontsize=8)
ax.set_title("N4 — retron covariance models across RT families (blank = no call)\n"
             "the models ARE retron models: near-absence elsewhere is detector scope, not biology",
             fontsize=9.5, loc="left")
fig.tight_layout(); savefig2(fig, "N4_family_x_model", pop="PL-CANON", sources=["N4_family_x_model"]); plt.show()
''')

md(r"""
## N5 — RT–ncRNA architecture: Retron against non-Retron

* **Unit.** Eligible, non-redundant placement (`PL-CANON`) — for **both** panels. This table
  used to run on `PL-ELIG` while the chapter's geometry table ran on `PL-CANON`; both gave
  94.51 % upstream, which agreed only to two decimals and read as one number measured twice.
* **Denominator.** Placements of that family group, stated on each panel.
* **Overlapping is shown as its own category**, not folded into a distance histogram where it would
  be a spike at zero that is a category rather than a measurement.
""")

code(r'''
geo2 = cache("N5_geometry_retron_vs_not", """
    SELECT CASE WHEN file_label = 'Retron' THEN 'Retron'
                WHEN file_label = 'MULTI'  THEN 'MULTI'
                ELSE 'non-Retron' END AS grp,
           count(*) AS n,
           100.0 * count(*) FILTER (WHERE direction = 'upstream')    / count(*) AS pct_upstream,
           100.0 * count(*) FILTER (WHERE direction = 'overlapping') / count(*) AS pct_overlapping,
           100.0 * count(*) FILTER (WHERE direction = 'downstream')  / count(*) AS pct_downstream,
           100.0 * count(*) FILTER (WHERE same_strand)               / count(*) AS pct_same_strand,
           100.0 * count(*) FILTER (WHERE n_cds_between = 0)         / count(*) AS pct_no_cds,
           quantile_cont(abs(signed_distance_bp), 0.50) FILTER (WHERE direction <> 'overlapping')
               AS median_abs_bp
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1 ORDER BY n DESC
""", pop="PL-CANON")
save(geo2, "N5_geometry_retron_vs_not")
display(geo2.round(2))
print(f"  denominator: PL-CANON, {int(geo2.n.sum()):,} placements — the same population as the")
print("  chapter's geometry table. The non-Retron n changes from the eligible-based 260.")

overlap = cache("N5_overlap_profile", """
    SELECT CASE WHEN overlap_bp / nullif(nc_seq_len, 0) <= 0.10 THEN 'a. <=10% of the ncRNA'
                WHEN overlap_bp / nullif(nc_seq_len, 0) <= 0.50 THEN 'b. 10-50%'
                WHEN overlap_bp / nullif(nc_seq_len, 0) <  0.99 THEN 'c. 50-99%'
                ELSE 'd. ncRNA fully enclosed by a CDS' END AS overlap_extent,
           count(*) AS n,
           count(*) FILTER (WHERE overlaps_rt_cds) AS n_overlapping_the_RT_gene,
           count(*) FILTER (WHERE overlaps_non_rt_cds) AS n_overlapping_another_gene
    FROM rt_ncrna_pairs WHERE canonical AND direction = 'overlapping'
    GROUP BY 1 ORDER BY 1
""", pop="PL-CANON")
overlap["pct"] = (100 * overlap.n / overlap.n.sum()).round(2)
save(overlap, "N5_overlap_profile")
display(overlap)
print("  overlap is mostly a short encroachment on the RT gene's own 5' end, not a gene collision.")
_enc = int(overlap.loc[overlap.overlap_extent.str.startswith('d.'), 'n'].iloc[0])
print(f"\n  NAMING. The {_enc} fully-enclosed placements here are NOT the 266 retron-CM calls at")
print("  non-Retron RT loci. Two unrelated populations happen to have the same size. Always")
print("  render this one as 'fully enclosed by a CDS (of 12,124 overlapping placements)'.")
''')

code(r'''
G = pd.read_csv(TABLES / "N5_geometry_retron_vs_not.tsv", sep="\t")
G = G[G.grp.isin(["Retron", "non-Retron"])].set_index("grp").loc[["Retron", "non-Retron"]]
O = pd.read_csv(TABLES / "N5_overlap_profile.tsv", sep="\t")

fig, axes = plt.subplots(1, 4, figsize=(14.2, 3.6))
ax = axes[0]
left = np.zeros(len(G))
for col, colr, lab in [("pct_upstream", BLUE, "upstream"),
                       ("pct_overlapping", PURPLE, "overlapping"),
                       ("pct_downstream", RED, "downstream")]:
    ax.barh(G.index, G[col], left=left, color=colr, label=lab, height=0.6); left += G[col].values
ax.set_xlim(0, 100); ax.set_xlabel("% of eligible, non-redundant placements"); ax.legend(fontsize=7.4)
ax.set_title("direction", fontsize=9.5, loc="left")
ax.set_yticklabels([f"{i}\n(n={int(G.loc[i,'n']):,})" for i in G.index], fontsize=8)

ax = axes[1]
xx = np.arange(len(G)); w = 0.36
ax.bar(xx - w/2, G.pct_same_strand, w, color=GREEN, label="same strand")
ax.bar(xx + w/2, G.pct_no_cds, w, color=GREY, label="no CDS between")
for i, (a, b) in enumerate(zip(G.pct_same_strand, G.pct_no_cds)):
    ax.text(i - w/2, a + 1.5, f"{a:.0f}", ha="center", fontsize=7.6)
    ax.text(i + w/2, b + 1.5, f"{b:.0f}", ha="center", fontsize=7.6)
ax.set_xticks(xx); ax.set_xticklabels(G.index, fontsize=8); ax.set_ylim(0, 132)
ax.set_ylabel("%")
# legend above the bars: at ylim 112 it sat on top of the Retron "no CDS between" value label
ax.legend(fontsize=7.4, loc="upper center", ncol=2, frameon=False,
          bbox_to_anchor=(0.5, 1.02))
ax.set_title("strand and adjacency", fontsize=9.5, loc="left")

ax = axes[2]
ax.bar(G.index, G.median_abs_bp, color=[BLUE, RED], width=0.5)
for i, v in enumerate(G.median_abs_bp):
    ax.text(i, v * 1.15, f"{v:,.0f} bp", ha="center", fontsize=8.5, fontweight="bold")
ax.set_yscale("log"); ax.set_ylim(10, 2e4); ax.set_ylabel("median |distance| (bp, log)")
ax.set_title("separation from the RT", fontsize=9.5, loc="left")

ax = axes[3]
ax.barh(O.overlap_extent.str.slice(3), O.n, color=PURPLE, height=0.62)
for i, (n, p) in enumerate(zip(O.n, O.pct)):
    ax.text(n + 90, i, f"{n:,} ({p:.0f}%)", va="center", fontsize=7.4)
ax.set_xlim(0, 9200); ax.set_xlabel("overlapping placements")
ax.tick_params(axis="y", labelsize=7.4)
ax.set_title("how much is overlapped\n(97.4% is the RT gene itself)", fontsize=9.5, loc="left")

fig.tight_layout()
savefig2(fig, "N5_architecture_retron_vs_not", pop="PL-CANON",
         sources=["N5_geometry_retron_vs_not", "N5_overlap_profile"]); plt.show()
''')

md(r"""
## N6 — Taxonomic representation, and covariance-model confidence

Two unrelated findings used to share one figure, which forced the thesis chapter to cite
`fig:taxa` from two subsections a hundred lines apart. They are now **N6a** (sampling redundancy,
belongs beside the unit ladder) and **N6b** (model confidence, belongs beside N4).

* **N6a — unit.** Distinct record and distinct RT protein, on `RT-SEQ`.
* **N6a — denominator.** Records carrying that species rank (~99.8 % of all). Phylum is **not**
  plotted — NCBI carries none, and the GTDB block mixes two release vintages.
* **N6b — unit.** Placement, on `PL-CANON`.
""")

code(r'''
tax = cache("N6_top_taxa", f"""
    SELECT taxonomy_system, tax_species, count(*) AS n_records,
           count(DISTINCT rt_seq_hash) AS n_exact_rt
    FROM rt_records
    WHERE {POP_RT_SEQ} AND nullif(tax_species, '') IS NOT NULL
    GROUP BY 1, 2 ORDER BY n_records DESC LIMIT 40
""", pop="RT-SEQ")
tax["proteins_per_100_records"] = (100 * tax.n_exact_rt / tax.n_records).round(1)
save(tax, "N6_top_taxa")
display(tax.head(12))
print("NOTE. This table is counted on RT-SEQ. The landed g5 bundle reports the same species on\n"
      "      ALL records (E. coli 450,012 / 28,018 there, vs 449,992 / 27,998 here). Both are\n"
      "      correct; quote one, and cite the figure that plots the same one.")

conf = cache("N6_cm_confidence", """
    SELECT CASE WHEN evalue <= 1e-20 THEN 'a. E <= 1e-20' WHEN evalue <= 1e-10 THEN 'b. 1e-20 - 1e-10'
                WHEN evalue <= 1e-5  THEN 'c. 1e-10 - 1e-5' WHEN evalue <= 1e-3 THEN 'd. 1e-5 - 1e-3'
                ELSE 'e. E > 1e-3' END AS evalue_band,
           count(*) AS n_placements, quantile_cont(score, 0.50) AS median_score
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1 ORDER BY 1
""", pop="PL-CANON")
conf["pct"] = (100 * conf.n_placements / conf.n_placements.sum()).round(2)
save(conf, "N6_cm_confidence")
display(conf)
hi = conf[conf.evalue_band < "d"].n_placements.sum()
print(f"\n  high-confidence calls (E <= 1e-5): {hi:,} of {conf.n_placements.sum():,} "
      f"({100*hi/conf.n_placements.sum():.2f}%)")
print("  an E-value filter therefore costs ~2% of the dataset.")

# A global threshold does NOT cost every model the same. The chapter claimed "one model returns
# 39.2% of its calls above 1e-5"; that is TypeIIIA2, and it is not the worst. Compute it, so the
# claim is traceable to a table instead of to a remembered print-out.
bym = cache("N6_cm_confidence_by_model", """
    SELECT detection_model, count(*) AS n_calls,
           sum(CASE WHEN evalue > 1e-5 THEN 1 ELSE 0 END) AS n_above_1e5,
           round(100.0 * sum(CASE WHEN evalue > 1e-5 THEN 1 ELSE 0 END) / count(*), 2) AS pct_above_1e5
    FROM rt_ncrna_pairs WHERE canonical GROUP BY 1 ORDER BY pct_above_1e5 DESC
""", pop="PL-CANON")
display(bym.head(6))
_w = bym.iloc[0]
print(f"\n  worst-affected model: {_w.detection_model} — {_w.pct_above_1e5:.1f}% of its "
      f"{int(_w.n_calls):,} calls fall above E = 1e-5.")
print("  Use this number, not the second-worst, when saying the threshold hits models unequally.")
''')

code(r'''
TX = pd.read_csv(TABLES / "N6_top_taxa.tsv", sep="\t")
TX = TX[TX.taxonomy_system == "ncbi"].head(12).iloc[::-1]

fig, ax = plt.subplots(figsize=(7.6, 4.4))
y = np.arange(len(TX)); h = 0.38
ax.barh(y + h/2, TX.n_records, height=h, color=GREY, label="records")
ax.barh(y - h/2, TX.n_exact_rt, height=h, color=BLUE, label="distinct RT proteins")
for i, r in enumerate(TX.itertuples()):
    ax.text(r.n_records * 1.06, i + h/2, f"{r.proteins_per_100_records:.0f} per 100",
            va="center", fontsize=7, color="#555")
ax.set_yticks(y); ax.set_yticklabels([s.replace("_", " ") for s in TX.tax_species], fontsize=8)
ax.set_xscale("log"); ax.set_xlim(500, 2.2e6); ax.set_xlabel("count (log)")
ax.legend(fontsize=8, loc="lower right")
ax.set_title("N6a — the most deposited species carry few distinct proteins\n"
             "(NCBI-assigned records; labels give distinct proteins per 100 records)",
             fontsize=9.5, loc="left")
fig.tight_layout()
savefig2(fig, "N6a_taxa_redundancy", sources=["N6_top_taxa"], pop="RT-SEQ"); plt.show()
''')

code(r'''
CF = pd.read_csv(TABLES / "N6_cm_confidence.tsv", sep="\t")
BM = pd.read_csv(TABLES / "N6_cm_confidence_by_model.tsv", sep="\t").head(8).iloc[::-1]

fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.0), gridspec_kw={"width_ratios": [1, 1.15]})
ax = axes[0]
ax.bar(CF.evalue_band.str.slice(3), CF.pct, color=[GREEN, GREEN, GREEN, "#d9a441", RED], width=0.62)
for i, (p, n) in enumerate(zip(CF.pct, CF.n_placements)):
    ax.text(i, p + 1.4, f"{p:.1f}%\n({n:,})", ha="center", fontsize=7.2)
ax.set_ylim(0, 68); ax.set_ylabel("% of placements")
ax.tick_params(axis="x", labelsize=7.2, rotation=30)
# from counts, not from the sum of ROUNDED band percentages (which gives 97.75, not 97.74)
_hi = 100.0 * CF[CF.evalue_band < "d"].n_placements.sum() / CF.n_placements.sum()
ax.set_title(f"N6b — covariance-model hit confidence\n{_hi:.2f}% at E ≤ 1e-5",
             fontsize=9.5, loc="left")

# The marginal is reassuring; the per-model view is the one that carries the caveat.
ax = axes[1]
yy = np.arange(len(BM))
ax.barh(yy, BM.pct_above_1e5, color=[RED if v >= 20 else "#d9a441" for v in BM.pct_above_1e5],
        height=0.62)
for i, r in enumerate(BM.itertuples()):
    ax.text(r.pct_above_1e5 + 0.9, i, f"{r.pct_above_1e5:.1f}%  (n={int(r.n_calls):,})",
            va="center", fontsize=7)
ax.set_yticks(yy); ax.set_yticklabels(BM.detection_model, fontsize=7.6)
ax.set_xlim(0, max(BM.pct_above_1e5) * 1.42); ax.set_xlabel("% of that model's calls above E = 1e-5")
ax.set_title("a global threshold does not cost every model the same\n"
             "(the eight most affected models)", fontsize=9.5, loc="left")
fig.tight_layout()
savefig2(fig, "N6b_cm_confidence",
         sources=["N6_cm_confidence", "N6_cm_confidence_by_model"], pop="PL-CANON"); plt.show()
''')

md(r"""
## N7 — RT burden per genome and family co-occurrence

* **Unit.** Genome (deduplicated), so a twin-published assembly counts once.
* **Denominator.** Genomes carrying at least one RT — so this cannot say whether RTs co-occur more
  than chance, only what co-occurs among RT-carrying genomes.
""")

code(r'''
burden = cache("N7_rt_per_genome", f"""
    WITH g AS (SELECT genome_id_norm, count(DISTINCT rt_seq_hash) AS k
               FROM rt_records WHERE {POP_RT_SEQ} GROUP BY 1)
    SELECT CASE WHEN k = 1 THEN '1' WHEN k = 2 THEN '2' WHEN k <= 5 THEN '3-5'
                WHEN k <= 10 THEN '6-10' ELSE '>10' END AS distinct_rts,
           CASE WHEN k = 1 THEN 1 WHEN k = 2 THEN 2 WHEN k <= 5 THEN 3
                WHEN k <= 10 THEN 4 ELSE 5 END AS ord,
           count(*) AS n_genomes FROM g GROUP BY 1, 2 ORDER BY ord
""")
burden["pct"] = (100 * burden.n_genomes / burden.n_genomes.sum()).round(2)
save(burden, "N7_rt_per_genome")
display(burden)

retron_burden = cache("N7_retron_loci_per_genome", f"""
    WITH g AS (SELECT genome_id_norm, count(DISTINCT locus_key) AS k
               FROM rt_records WHERE {POP_RT_SEQ} AND file_label = 'Retron' GROUP BY 1)
    SELECT CASE WHEN k = 1 THEN '1' WHEN k = 2 THEN '2' WHEN k <= 5 THEN '3-5' ELSE '>5' END
               AS retron_loci,
           count(*) AS n_genomes FROM g GROUP BY 1 ORDER BY n_genomes DESC
""")
display(retron_burden)

cooc = cache("N7_family_cooccurrence", f"""
    WITH g AS (SELECT genome_id_norm, file_label FROM rt_records
               WHERE {POP_RT_SEQ} GROUP BY 1, 2)
    SELECT a.file_label AS family_a, b.file_label AS family_b, count(*) AS n_genomes
    FROM g a JOIN g b ON a.genome_id_norm = b.genome_id_norm AND a.file_label < b.file_label
    GROUP BY 1, 2 ORDER BY n_genomes DESC LIMIT 20
""")
save(cooc, "N7_family_cooccurrence")
display(cooc.head(10))
''')

code(r'''
B  = pd.read_csv(TABLES / "N7_rt_per_genome.tsv", sep="\t").sort_values("ord")
RB = pd.read_csv(TABLES / "N7_retron_loci_per_genome.tsv", sep="\t")
CO = pd.read_csv(TABLES / "N7_family_cooccurrence.tsv", sep="\t").head(10).iloc[::-1]

fig, axes = plt.subplots(1, 3, figsize=(13.4, 3.8), gridspec_kw={"width_ratios": [1, 1, 1.5]})
ax = axes[0]
ax.bar(B.distinct_rts, B.n_genomes, color=BLUE, width=0.62)
for i, (n, p) in enumerate(zip(B.n_genomes, B.pct)):
    ax.text(i, n * 1.06, f"{p:.0f}%", ha="center", fontsize=8)
ax.set_yscale("log"); ax.set_xlabel("distinct RT proteins in one genome")
ax.set_ylabel("genomes (log)")
ax.set_title("N7 — RT burden per genome", fontsize=9.5, loc="left")

ax = axes[1]
order = ["1", "2", "3-5", ">5"]
RB = RB.set_index("retron_loci").reindex(order).reset_index()
ax.bar(RB.retron_loci, RB.n_genomes, color=RED, width=0.62)
for i, n in enumerate(RB.n_genomes):
    if pd.notna(n): ax.text(i, n * 1.08, f"{int(n):,}", ha="center", fontsize=8)
ax.set_yscale("log"); ax.set_xlabel("Retron loci in one genome")
ax.set_title("multi-retron genomes", fontsize=9.5, loc="left")

ax = axes[2]
lab = [f"{a} + {b}" for a, b in zip(CO.family_a, CO.family_b)]
ax.barh(lab, CO.n_genomes, color=GREEN, height=0.66)
for i, n in enumerate(CO.n_genomes):
    ax.text(n * 1.03, i, f"{n:,}", va="center", fontsize=7.4)
ax.set_xscale("log"); ax.set_xlim(8e3, 4e5)
ax.set_xlabel("genomes carrying both (log)"); ax.tick_params(axis="y", labelsize=7.4)
ax.set_title("which RT families share a genome", fontsize=9.5, loc="left")
fig.tight_layout()
savefig2(fig, "N7_burden_and_cooccurrence", pop="GEN",
         sources=["N7_rt_per_genome", "N7_retron_loci_per_genome", "N7_family_cooccurrence"])
plt.show()
''')

md(r"""
## N8 — The dataset funnel

* **Unit.** Distinct exact RT–ncRNA pair at every step.
* **Denominator.** Each step against the previous; **each reduction is attributed to a finding**
  from the preceding sections. This is the spine of the chapter.
""")

code(r'''
funnel_ds = cache("N8_dataset_funnel", """
    WITH p AS (SELECT * FROM rt_ncrna_pairs WHERE canonical)
    SELECT 1 AS step, 'eligible, non-redundant placements' AS stage,
           count(DISTINCT (rt_seq_hash, nc_seq_hash)) AS n_pairs,
           'de-duplication + coordinate verification' AS reason FROM p
    UNION ALL SELECT 2, 'Retron family only', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           'detection is retron-model-scoped' FROM p WHERE file_label = 'Retron'
    UNION ALL SELECT 3, 'same strand', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           'opposite strand is a distant single-model group' FROM p
      WHERE file_label = 'Retron' AND same_strand
    UNION ALL SELECT 4, 'upstream or overlapping', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           'downstream is largely window-truncation artefact' FROM p
      WHERE file_label = 'Retron' AND same_strand AND direction <> 'downstream'
    UNION ALL SELECT 5, 'no intervening CDS', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           'operonic architecture' FROM p
      WHERE file_label = 'Retron' AND same_strand AND direction <> 'downstream' AND n_cds_between = 0
    UNION ALL SELECT 6, 'within 200 bp', count(DISTINCT (rt_seq_hash, nc_seq_hash)),
           'the joint-geometry mode' FROM p
      WHERE file_label = 'Retron' AND same_strand AND direction <> 'downstream'
        AND n_cds_between = 0 AND abs(signed_distance_bp) <= 200
    UNION ALL SELECT 7, 'high-confidence CM hit (E <= 1e-5)',
           count(DISTINCT (rt_seq_hash, nc_seq_hash)), 'detection confidence' FROM p
      WHERE file_label = 'Retron' AND same_strand AND direction <> 'downstream'
        AND n_cds_between = 0 AND abs(signed_distance_bp) <= 200 AND evalue <= 1e-5
    ORDER BY step
""")
funnel_ds["pct_retained"] = (100 * funnel_ds.n_pairs / funnel_ds.n_pairs.iloc[0]).round(2)
funnel_ds["removed"] = (funnel_ds.n_pairs.shift(1) - funnel_ds.n_pairs).fillna(0).astype(int)
save(funnel_ds, "N8_dataset_funnel")
display(funnel_ds[["step", "stage", "n_pairs", "removed", "pct_retained", "reason"]])
print("\n  NOTE: overlapping placements are RETAINED (97.4% overlap only the RT gene itself,")
print("  median 22 bp). Sequence clustering is NOT yet applied — see the caveat in section F.")
''')

code(r'''
FN = pd.read_csv(TABLES / "N8_dataset_funnel.tsv", sep="\t").sort_values("step")
fig, ax = plt.subplots(figsize=(10.4, 4.6))
y = np.arange(len(FN))[::-1]
ax.barh(y, FN.n_pairs, color=[BLUE if i < len(FN) - 1 else GREEN for i in range(len(FN))],
        height=0.6)
for yi, r in zip(y, FN.itertuples()):
    ax.text(r.n_pairs + 350, yi, f"{r.n_pairs:,}  ({r.pct_retained:.0f}%)", va="center", fontsize=8.4)
    if r.removed > 0:
        ax.text(r.n_pairs + 5200, yi, f"− {r.removed:,}   {r.reason}", va="center",
                fontsize=7.2, color="#777777", style="italic")
ax.set_yticks(y); ax.set_yticklabels(FN.stage, fontsize=8.4)
ax.set_xlim(0, 52000); ax.set_xlabel("distinct exact RT–ncRNA sequence pairs")
ax.set_title("N8 — from observation to dataset: every reduction and its reason\n"
             "overlapping placements retained; sequence clustering still to apply",
             fontsize=9.5, loc="left")
fig.tight_layout(); savefig2(fig, "N8_dataset_funnel", pop="PAIR-CANON", sources=["N8_dataset_funnel"]); plt.show()
''')

md(r"""
---

# Z1 — The resulting association datasets

* **Question.** What does the funnel actually deliver, how much of the apparent many-to-many
  structure survives it, and what must a user account for before using it?
* **Unit.** Exact RT–ncRNA pair (`PAIR-CANON` lineage), reported beside the RT-level association
  it collapses to.
* **Denominator.** Each tier against itself; the tiers are nested.
* **Why the collapse column matters.** A pair is a distinct `(rt_seq_hash, nc_seq_hash)`
  combination. Both hashes are exact, so one trimmed nucleotide makes a second pair out of one
  association. Counting distinct `(rt_seq_hash, detection_model)` instead gives the number of
  RT-to-RNA-type associations, which is invariant to that trimming. The gap between the two
  columns is the boundary-jitter inflation, measured rather than assumed.
""")

code(r'''
BASE = "canonical AND file_label = 'Retron'"
ARCH = BASE + (" AND same_strand AND direction <> 'downstream' AND n_cds_between = 0"
               " AND abs(signed_distance_bp) <= 200")
T3   = ARCH + " AND evalue <= 1e-5"

def _tiers():
    rows = []
    for name, where in [("T1 observed", BASE),
                        ("T2 architecture-filtered", ARCH),
                        ("T3 high-confidence", T3)]:
        r = Q(f"""SELECT count(*) n_placements,
                    count(DISTINCT (rt_seq_hash, nc_seq_hash)) n_exact_pairs,
                    count(DISTINCT (rt_seq_hash, detection_model)) n_rt_associations,
                    count(DISTINCT rt_seq_hash) n_exact_rt,
                    count(DISTINCT nc_seq_hash) n_exact_ncrna,
                    count(DISTINCT physical_locus_key) n_physical_loci,
                    count(DISTINCT tax_species) n_species
                  FROM rt_ncrna_pairs WHERE {where}""").iloc[0]
        rows.append({"tier": name, **r.to_dict()})
    # T4: the subset of T3 that recurs in distinct genomic backgrounds. Uses the REGISTERED
    # recurrence view, not a recomputation: distinct genome_id_norm overstates independence,
    # because one physical locus is republished under several genome accessions. (Recomputing
    # it naively from tax_species is worse still - 2,760 T3 pairs sit in ONE genome that is
    # named differently by NCBI and GTDB, and a species-based rule scores them as cross-species.)
    r = Q(f"""WITH pr AS (SELECT DISTINCT rt_seq_hash, nc_seq_hash
                          FROM rt_ncrna_pairs WHERE {T3}),
                   sel AS (SELECT pr.* FROM pr
                           JOIN rt_ncrna_exact_pair_recurrence r USING (rt_seq_hash, nc_seq_hash)
                           WHERE r.recurrence_class IN
                                 ('multiple_species', 'one_species_multiple_genomes'))
              SELECT NULL n_placements, count(*) n_exact_pairs,
                     NULL n_rt_associations, count(DISTINCT rt_seq_hash) n_exact_rt,
                     count(DISTINCT nc_seq_hash) n_exact_ncrna,
                     NULL n_physical_loci, NULL n_species FROM sel""").iloc[0]
    rows.append({"tier": "T4 independently recurrent", **r.to_dict()})
    return pd.DataFrame(rows)

tiers = cache("Z1_association_resource_tiers", fn=_tiers, pop="PAIR-CANON")
display(tiers)
''')

code(r'''
# Is the many-to-many structure resolved? Measure it, per direction, inside T3.
topo = cache("Z1_t3_topology", f"""
    WITH pr AS (SELECT DISTINCT rt_seq_hash, nc_seq_hash FROM rt_ncrna_pairs WHERE {T3})
    SELECT 'RT -> ncRNA' AS side,
           count(DISTINCT rt_seq_hash) AS n_nodes,
           (SELECT count(*) FROM (SELECT rt_seq_hash FROM pr GROUP BY 1 HAVING count(*) = 1))
               AS n_with_one_partner,
           (SELECT max(k) FROM (SELECT count(*) k FROM pr GROUP BY rt_seq_hash)) AS max_partners
    FROM pr
    UNION ALL
    SELECT 'ncRNA -> RT', count(DISTINCT nc_seq_hash),
           (SELECT count(*) FROM (SELECT nc_seq_hash FROM pr GROUP BY 1 HAVING count(*) = 1)),
           (SELECT max(k) FROM (SELECT count(*) k FROM pr GROUP BY nc_seq_hash))
    FROM pr
""", pop="PAIR-CANON")
topo["pct_with_one_partner"] = (100 * topo.n_with_one_partner / topo.n_nodes).round(2)
save(topo, "Z1_t3_topology")
display(topo)

# Of the RTs that DO have several partners, how many are boundary variants of one RNA type?
jit = cache("Z1_t3_partner_jitter", f"""
    WITH pr AS (SELECT DISTINCT rt_seq_hash, nc_seq_hash, nc_seq_len, detection_model
                FROM rt_ncrna_pairs WHERE {T3}),
         g AS (SELECT rt_seq_hash, count(*) n_partners,
                      count(DISTINCT detection_model) n_models,
                      max(nc_seq_len) - min(nc_seq_len) len_spread
               FROM pr GROUP BY 1 HAVING count(*) > 1)
    SELECT count(*) AS rts_with_several_partners,
           sum(CASE WHEN n_models = 1 THEN 1 ELSE 0 END) AS all_partners_one_model,
           sum(CASE WHEN n_models = 1 AND len_spread <= 5  THEN 1 ELSE 0 END) AS spread_le_5nt,
           sum(CASE WHEN n_models = 1 AND len_spread <= 20 THEN 1 ELSE 0 END) AS spread_le_20nt,
           sum(CASE WHEN n_models > 1 THEN 1 ELSE 0 END)  AS partners_from_several_models
    FROM g
""", pop="PAIR-CANON")
display(jit)

_t = tiers[tiers.tier == "T3 high-confidence"].iloc[0]
_p, _a = int(_t.n_exact_pairs), int(_t.n_rt_associations)
print(f"\n  T3: {_p:,} exact pairs collapse to {_a:,} RT-to-RNA-type associations")
print(f"       ({_p - _a:,} pairs, {100*(_p-_a)/_p:.1f}%, are boundary variants of another pair).")
print("  Every RT in T3 with several partners draws them from ONE covariance model, so the")
print("  RT -> ncRNA direction is resolved by collapsing to model level. The ncRNA -> RT")
print("  direction is NOT resolved: it needs RT clustering, for which rt_exact_v1.faa is ready.")
print("  ncRNA clustering has no input yet - no derived dataset carries the ncRNA SEQUENCE,")
print("  only nc_seq_hash and nc_seq_len. Exporting that FASTA is the prerequisite.")
''')

md(r"""
---

# Z2 — The tool-agreement table, and redundancy by taxonomic domain

## Z2.1 — Tool agreement, both axes, as a regenerating table

* **Question.** How do the three detection routes partition the Retron corpus, on records and on
  distinct proteins, and how does RNA co-occurrence vary across the regions?
* **Unit.** Distinct record (`REC-DIST`) and distinct RT protein (`RT-BASE-1F`), side by side.
* **Denominator.** Retron records (663,308) and the distinct proteins they carry (78,287).
* **Why it is here.** This table was hand-written LaTeX in the draft, the only object in the
  chapter not backed by a cached table. Three of its columns were wrong: the record column was
  counted on ALL Retron records *including byte-identical duplicate lines* (665,321 rather than
  663,308), and the RNA column did not match any computable definition — "PADLOC only" read
  49.26 % against a true 25.09 %.
* **On attribution.** Every RNA call in this corpus has `nc_source = 'infernal'`. Not one came
  from a detection tool. The association between tool region and RNA carriage is a selection
  effect, not detection by that tool. The cell below asserts this rather than assuming it.
""")

code(r'''
_srcs = Q("SELECT nc_source, count(*) n FROM rt_ncrna_pairs GROUP BY 1 ORDER BY n DESC")
print("ncRNA call provenance:")
display(_srcs)
assert len(_srcs) == 1 and _srcs.nc_source.iloc[0] == "infernal", \
    "ncRNA calls are NOT all from infernal - the caption claim must be re-checked"
print("  -> all calls come from one source; no detection tool produced any of them.\n")

agree = cache("N1_tool_agreement_table", """
    WITH rec AS (
      SELECT detected_by_set,
             count(*) AS n_records,
             100.0 * count(*) FILTER (WHERE n_ncrna > 0) / count(*) AS pct_records_with_rna
      FROM rt_tool_calls WHERE file_label = 'Retron' GROUP BY 1),
    prot AS (
      SELECT tool_set AS detected_by_set,
             count(*) AS n_exact_rt,
             100.0 * count(*) FILTER (WHERE has_rna) / count(*) AS pct_exact_rt_with_rna
      FROM (SELECT rt_seq_hash,
              concat_ws('|', CASE WHEN bool_or(by_myRT) THEN 'myRT' END,
                             CASE WHEN bool_or(by_PADLOC) THEN 'PADLOC' END,
                             CASE WHEN bool_or(by_DefenseFinder) THEN 'DefenseFinder' END)
                  AS tool_set,
              bool_or(n_ncrna > 0) AS has_rna
            FROM rt_tool_calls WHERE file_label = 'Retron' GROUP BY 1) GROUP BY 1)
    SELECT rec.detected_by_set, rec.n_records,
           100.0 * rec.n_records / sum(rec.n_records) OVER () AS pct_records,
           rec.pct_records_with_rna,
           prot.n_exact_rt,
           100.0 * prot.n_exact_rt / sum(prot.n_exact_rt) OVER () AS pct_exact_rt,
           prot.pct_exact_rt_with_rna
    FROM rec JOIN prot USING (detected_by_set) ORDER BY rec.n_records DESC
""", pop=["REC-DIST", "RT-BASE-1F"])
display(agree.round(2))

_tot = Q("""SELECT count(*) AS n_records,
              100.0 * count(*) FILTER (WHERE n_ncrna > 0) / count(*) AS pct_records_with_rna,
              (SELECT count(*) FROM (SELECT rt_seq_hash FROM rt_tool_calls
                                     WHERE file_label='Retron' GROUP BY 1)) AS n_exact_rt,
              (SELECT 100.0 * avg(CASE WHEN has_rna THEN 1.0 ELSE 0.0 END) FROM
                 (SELECT rt_seq_hash, bool_or(n_ncrna>0) has_rna FROM rt_tool_calls
                  WHERE file_label='Retron' GROUP BY 1)) AS pct_exact_rt_with_rna
            FROM rt_tool_calls WHERE file_label = 'Retron'""").iloc[0]
print(f"\n  totals: {int(_tot.n_records):,} distinct records ({_tot.pct_records_with_rna:.2f}% with RNA)"
      f" | {int(_tot.n_exact_rt):,} distinct proteins ({_tot.pct_exact_rt_with_rna:.2f}% with RNA)")
print(f"  RNA carriage spread on the protein axis: "
      f"{agree.pct_exact_rt_with_rna.max()/agree.pct_exact_rt_with_rna.min():.1f}x")

# The regions must partition each axis exactly - that is what makes the table readable.
check("tool regions sum to the Retron records",   int(agree.n_records.sum()),  expected=663308)
check("tool regions sum to the Retron proteins",  int(agree.n_exact_rt.sum()), expected=78287)
''')

code(r'''
# Emit the LaTeX so the chapter table is generated, never retyped.
_LBL = {"myRT|PADLOC|DefenseFinder": r"myRT $+$ PADLOC $+$ DefenseFinder",
        "myRT": "myRT only", "myRT|DefenseFinder": r"myRT $+$ DefenseFinder",
        "myRT|PADLOC": r"myRT $+$ PADLOC", "PADLOC": "PADLOC only",
        "PADLOC|DefenseFinder": r"PADLOC $+$ DefenseFinder",
        "DefenseFinder": "DefenseFinder only"}

def _emit_agreement_tex(df, tot, path):
    body = []
    for r in df.itertuples():
        bold = (lambda v: rf"\textbf{{{v:.2f}}}") if r.pct_exact_rt_with_rna > 80 else (lambda v: f"{v:.2f}")
        body.append(
            f"{_LBL[r.detected_by_set]} & \\num{{{int(r.n_records)}}} & {r.pct_records:.2f} & "
            f"{bold(r.pct_records_with_rna)} & \\num{{{int(r.n_exact_rt)}}} & {r.pct_exact_rt:.2f} & "
            f"{bold(r.pct_exact_rt_with_rna)} \\\\")
    tex = (r"""% GENERATED by notebook section Z2.1 - do not edit by hand.
\begin{table}[htbp]
\centering\footnotesize
\setlength{\tabcolsep}{5pt}
\caption[Detection-tool agreement on retron reverse transcriptases]{%
\textbf{Agreement between the three detection tools, and its relationship to non-coding RNA
co-occurrence.} Regions are exclusive and partition each axis. A protein is assigned to a region
by aggregating the tools across all of its records, so the two axes have different shapes: myRT
alone is the largest region by protein and the second smallest by record. RNA co-occurrence varies
""" + f"{df.pct_exact_rt_with_rna.max()/df.pct_exact_rt_with_rna.min():.1f}" + r"""-fold across regions on the protein axis. Every RNA call in this
corpus was made by Infernal against the covariance-model library, for each record alike; none
originated from a detection tool, so the association is a property of what each tool's retron
model requires in order to fire, not evidence that the tool found the RNA.}
\label{tab:venn_agreement}
\begin{tabular}{@{}lrrrrrr@{}}
\toprule
& \multicolumn{3}{c}{\textbf{Per distinct record}} & \multicolumn{3}{c}{\textbf{Per distinct RT protein}} \\
\cmidrule(lr){2-4}\cmidrule(l){5-7}
\textbf{Detected by} & \textbf{n} & \textbf{\%} & \textbf{\% RNA} & \textbf{n} & \textbf{\%} & \textbf{\% RNA} \\
\midrule
""" + "\n".join(body) + r"""
\midrule
\textbf{Total} & \textbf{\num{""" + str(int(tot.n_records)) + r"""}} & \textbf{100} & """
    + f"{tot.pct_records_with_rna:.2f}" + r""" & \textbf{\num{""" + str(int(tot.n_exact_rt))
    + r"""}} & \textbf{100} & """ + f"{tot.pct_exact_rt_with_rna:.2f}" + r""" \\
\bottomrule
\end{tabular}
\end{table}
""")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tex)
    return tex

_out = WB / "exports_v2" / "tables_tex" / "tab_venn_agreement.tex"
_tex = _emit_agreement_tex(agree, _tot, _out)
print(f"wrote {_out.relative_to(WB)}  ({len(_tex.splitlines())} lines)")
print("\n".join(_tex.splitlines()[:6]) + "\n  ...")
''')

md(r"""
## Z2.2 — Redundancy by taxonomic domain

* **Question.** Is the redundancy of deposition a property of RTs, or of how much each organism
  has been sequenced?
* **Unit.** Distinct record and distinct RT protein, on `RT-SEQ`.
* **Denominator.** Records of that domain, and the distinct proteins they carry.
* **Point.** Archaea are barely re-deposited. If redundancy were a property of RT biology the
  ratio would travel with the family; instead it travels largely with the domain, and most
  families show a bacterial ratio several times their archaeal one. The exception is
  `RVT-CRISPR`, where the archaeal ratio is the higher of the two on 73 archaeal proteins --- a
  reminder that these archaeal cells are small, and that the panel is a contrast rather than a
  law. Archaeal n is printed under each family for exactly that reason.
* **Caveat.** Archaea are \SI{0.34}{\percent} of the corpus. This is a contrast, not an archaeal
  survey, and the unassigned block is shown rather than dropped.
""")

code(r'''
dom = cache("Z2_redundancy_by_domain", f"""
    SELECT CASE WHEN tax_domain ILIKE '%archae%' THEN 'Archaea'
                WHEN tax_domain ILIKE '%bacter%' THEN 'Bacteria'
                ELSE 'unassigned' END AS domain,
           count(*) AS n_records,
           count(DISTINCT rt_seq_hash) AS n_exact_rt,
           count(DISTINCT genome_id_norm) AS n_genomes
    FROM rt_records WHERE {POP_RT_SEQ} GROUP BY 1 ORDER BY n_records DESC
""", pop="RT-SEQ")
dom["records_per_protein"] = (dom.n_records / dom.n_exact_rt).round(2)
save(dom, "Z2_redundancy_by_domain")
display(dom)

domfam = cache("Z2_redundancy_by_domain_family", f"""
    SELECT CASE WHEN tax_domain ILIKE '%archae%' THEN 'Archaea'
                WHEN tax_domain ILIKE '%bacter%' THEN 'Bacteria'
                ELSE 'unassigned' END AS domain,
           file_label AS family_label,
           count(*) AS n_records, count(DISTINCT rt_seq_hash) AS n_exact_rt
    FROM rt_records WHERE {POP_RT_SEQ} GROUP BY 1, 2
""", pop="RT-SEQ")
domfam["records_per_protein"] = (domfam.n_records / domfam.n_exact_rt).round(2)
save(domfam, "Z2_redundancy_by_domain_family")
_top = (domfam[(domfam.domain == "Archaea") & (domfam.n_exact_rt >= 50)]
        .nlargest(6, "n_exact_rt").family_label.tolist())
display(domfam[domfam.family_label.isin(_top) & domfam.domain.isin(["Bacteria", "Archaea"])]
        .pivot(index="family_label", columns="domain", values="records_per_protein"))
''')

code(r'''
DM = pd.read_csv(TABLES / "Z2_redundancy_by_domain.tsv", sep="\t")
DF_ = pd.read_csv(TABLES / "Z2_redundancy_by_domain_family.tsv", sep="\t")
order = ["Bacteria", "Archaea", "unassigned"]
DM = DM.set_index("domain").loc[[d for d in order if d in set(DM.domain)]].reset_index()

fig, axes = plt.subplots(1, 2, figsize=(12.6, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})

ax = axes[0]
y = np.arange(len(DM))[::-1]; h = 0.36
ax.barh(y + h/2, DM.n_records, height=h, color=GREY, label="records")
ax.barh(y - h/2, DM.n_exact_rt, height=h, color=BLUE, label="distinct RT proteins")
for i, r in zip(y, DM.itertuples()):
    ax.text(r.n_records * 1.35, i, f"×{r.records_per_protein:.2f}", va="center",
            fontsize=8.5, fontweight="bold", color="#333")
ax.set_yticks(y); ax.set_yticklabels(DM.domain, fontsize=9)
ax.set_xscale("log"); ax.set_xlim(1e3, 3e7); ax.set_xlabel("count (log)")
ax.legend(fontsize=8, loc="lower right")
ax.set_title("Z2a — redundancy of deposition by domain\n"
             "(label = records per distinct protein)", fontsize=9.5, loc="left")

# Same families, both domains: the ratio travels with the domain, not the family.
ax = axes[1]
fams = (DF_[(DF_.domain == "Archaea") & (DF_.n_exact_rt >= 50)]
        .nlargest(6, "n_exact_rt").family_label.tolist())
P = DF_[DF_.family_label.isin(fams) & DF_.domain.isin(["Bacteria", "Archaea"])] \
      .pivot(index="family_label", columns="domain", values="records_per_protein") \
      .loc[fams]
xx = np.arange(len(P)); w = 0.36
ax.bar(xx - w/2, P["Bacteria"], w, color=BLUE, label="Bacteria")
ax.bar(xx + w/2, P["Archaea"],  w, color=GREEN, label="Archaea")
for i, (b, a) in enumerate(zip(P["Bacteria"], P["Archaea"])):
    ax.text(i - w/2, b + 0.12, f"{b:.1f}", ha="center", fontsize=7.6)
    ax.text(i + w/2, a + 0.12, f"{a:.1f}", ha="center", fontsize=7.6)
# the reference line goes in the legend, not as floating text where bars can cover it
ax.axhline(1.0, color="#999", ls=":", lw=1,
           label="1.0 = every record a distinct protein")
NA = (DF_[(DF_.domain == "Archaea")].set_index("family_label")
        .reindex(P.index).n_exact_rt.fillna(0).astype(int))
ax.set_xticks(xx)
ax.set_xticklabels([f"{f}\n(archaeal n={n:,})" for f, n in zip(P.index, NA)],
                   fontsize=7.6, rotation=18, ha="right")
ax.set_ylabel("records per distinct protein")
ax.set_ylim(0, max(P["Bacteria"].max(), P["Archaea"].max()) * 1.30)
ax.legend(fontsize=7.6, loc="upper right", framealpha=0.95)
_n_lower = int((P["Archaea"] < P["Bacteria"]).sum())
ax.set_title(f"Z2b — the same families in both domains\n"
             f"archaeal redundancy is the lower of the two in {_n_lower} of {len(P)}",
             fontsize=9.5, loc="left")
fig.tight_layout()
savefig2(fig, "Z2_redundancy_by_domain", sources=["Z2_redundancy_by_domain",
         "Z2_redundancy_by_domain_family"], pop="RT-SEQ"); plt.show()
''')

md(r"""
---

# Z3 — What the exact-sequence grain actually measures

* **Question.** \num{46887} of the \num{78287} Retron proteins (\SI{59.9}{\percent}) occur in
  exactly one genome. Is that an artefact, is it diversity, or is it neither?
* **Unit.** Exact RT protein, Retron family, sequence-level population.
* **Denominator.** The \num{78287} distinct Retron proteins.
* **Why it matters.** The chapter says exact-sequence counts are upper bounds on distinctness.
  This section measures *how loose* that bound is, which decides whether a diversity or
  saturation claim can be made at all.

The test has two halves. First, strip the two obvious technical explanations --- truncated gene
calls and metagenome-assembly variation --- and see whether the singletons survive. Then ask
where the survivors live: a sequence seen once among two hundred thousand sequenced genomes *of
one species* is a strain-level variant, whatever its exact-sequence status.
""")

code(r'''
_SEQ = ("is_first_copy AND file_label = 'Retron' AND NOT multilabel AND elig_exact_rt")

occ = cache("Z3_singleton_diagnosis", f"""
    WITH g AS (
      SELECT rt_seq_hash,
             count(DISTINCT genome_id_norm) AS k_genomes,
             max(CASE WHEN source_database IN ('mgnify_human_gut','mgnify_soil',
                                               'mgnify_marine','gem') THEN 1 ELSE 0 END) AS any_mag,
             min(CASE WHEN source_database IN ('ncbi_bacteria','gtdb_bacteria',
                                               'ncbi_archaea','gtdb_archaea') THEN 0 ELSE 1 END)
                 AS all_mag
      FROM rt_records WHERE {_SEQ} GROUP BY 1)
    SELECT 'a. all Retron proteins' AS stratum, count(*) AS n_proteins,
           sum(CASE WHEN k_genomes = 1 THEN 1 ELSE 0 END) AS n_seen_once,
           sum(CASE WHEN k_genomes = 2 THEN 1 ELSE 0 END) AS n_seen_twice,
           100.0 * sum(CASE WHEN k_genomes = 1 THEN 1 ELSE 0 END) / count(*) AS pct_seen_once
    FROM g
    UNION ALL
    SELECT 'b. drop metagenome-only', count(*), sum(CASE WHEN k_genomes = 1 THEN 1 ELSE 0 END),
           sum(CASE WHEN k_genomes = 2 THEN 1 ELSE 0 END),
           100.0 * sum(CASE WHEN k_genomes = 1 THEN 1 ELSE 0 END) / count(*)
    FROM g WHERE all_mag = 0
    UNION ALL
    SELECT 'c. drop metagenome-only AND partial calls', count(*),
           sum(CASE WHEN k_genomes = 1 THEN 1 ELSE 0 END),
           sum(CASE WHEN k_genomes = 2 THEN 1 ELSE 0 END),
           100.0 * sum(CASE WHEN k_genomes = 1 THEN 1 ELSE 0 END) / count(*)
    FROM g JOIN rt_family_baseline f USING (rt_seq_hash)
    WHERE g.all_mag = 0 AND g.any_mag = 0 AND f.completeness_class = 'all_complete'
    ORDER BY 1
""", pop="RT-BASE-1F")
display(occ.round(1))
print("  The singletons survive both technical explanations. They are not an artefact.\n")

# Make the Chao1 illustration traceable rather than quoted. f1/f2 are the singleton and
# doubleton counts; the estimator is reported ONLY to show that it is uninterpretable at this
# grain, never as a richness claim.
_a = occ[occ.stratum == "a. all Retron proteins"].iloc[0]
_f1, _f2, _S = int(_a.n_seen_once), int(_a.n_seen_twice), int(_a.n_proteins)
_chao1 = _S + _f1**2 / (2 * _f2)
print(f"  frequency spectrum: f1 (seen in one genome) = {_f1:,}, f2 (two genomes) = {_f2:,}")
print(f"  Chao1 = S + f1^2/(2*f2) = {_S:,} + {_f1:,}^2/(2*{_f2:,}) = {_chao1:,.0f}")
print(f"  i.e. {_chao1/_S:.1f}x the observed count. At exact-sequence grain this measures")
print("  single-residue variation between strains, NOT unsampled biology. Do not publish it")
print("  as a richness estimate; it is here to show why the estimate must wait for clustering.")
save(pd.DataFrame([{"S_observed": _S, "f1_singletons": _f1, "f2_doubletons": _f2,
                    "chao1": round(_chao1), "ratio_to_observed": round(_chao1/_S, 2)}]),
     "Z3_chao1_illustration")

# Then: where do the survivors live? A sequence seen once among many thousand sequenced
# genomes OF ONE SPECIES is a strain variant, not a distinct entity.
home = cache("Z3_singleton_sampling_context", f"""
    WITH g AS (SELECT rt_seq_hash, count(DISTINCT genome_id_norm) AS k
               FROM rt_records WHERE {_SEQ} GROUP BY 1),
         s AS (SELECT DISTINCT rt_seq_hash, tax_species FROM rt_records
               WHERE {_SEQ} AND taxonomy_system = 'ncbi' AND nullif(tax_species,'') IS NOT NULL),
         sp AS (SELECT tax_species, count(DISTINCT genome_id_norm) AS n_gen FROM rt_records
                WHERE {_SEQ} AND taxonomy_system = 'ncbi' AND nullif(tax_species,'') IS NOT NULL
                GROUP BY 1)
    SELECT CASE WHEN sp.n_gen >= 1000 THEN 'a. >=1000 genomes of that species sequenced'
                WHEN sp.n_gen >=  100 THEN 'b. 100-999'
                WHEN sp.n_gen >=   10 THEN 'c. 10-99'
                ELSE                       'd. <10' END AS sampling_depth_of_its_species,
           count(*) AS n_proteins_seen_once
    FROM g JOIN s USING (rt_seq_hash) JOIN sp USING (tax_species)
    WHERE g.k = 1 GROUP BY 1 ORDER BY 1
""", pop="RT-BASE-1F")
display(home)

# The clinching case: one heavily sequenced species, counted at exact-sequence grain.
within = cache("Z3_distinct_rt_within_species", f"""
    SELECT tax_species, count(DISTINCT genome_id_norm) AS n_genomes,
           count(DISTINCT rt_seq_hash) AS n_distinct_exact_rt
    FROM rt_records WHERE {_SEQ} AND taxonomy_system = 'ncbi'
      AND nullif(tax_species,'') IS NOT NULL
    GROUP BY 1 ORDER BY n_genomes DESC LIMIT 8
""", pop="RT-BASE-1F")
display(within)
_ec = within[within.tax_species == "Escherichia_coli"].iloc[0]
print(f"\n  {int(_ec.n_distinct_exact_rt):,} distinct EXACT Retron RT sequences inside "
      f"E. coli alone, across {int(_ec.n_genomes):,} genomes.")
print("  The literature describes E. coli retrons in the order of ten types. The exact-sequence")
print("  grain is therefore two to three orders of magnitude finer than biological type.")
print("  CONCLUSION: the singletons are real sequences and are not a diversity measure.")
print("  No saturation, rarefaction or Chao1 estimate may be computed at this grain.")
''')

md(r"""
---

# Z4 — Are the outgroup-model calls different from the rest?

* **Question.** Two of the 21 covariance models are named `OutgroupA` and `OutgroupB`. They
  contribute \SI{22}{\percent} of distinct RNA sequences but only \SI{3.7}{\percent} of calls.
  Does the model name identify a different kind of hit, or only a different model?
* **Unit.** Eligible, non-redundant placement at a Retron locus (`PL-CANON`).
* **Denominator.** Each model group against itself.
* **Why it is here.** An earlier draft of this chapter asserted that the outgroup models
  contaminate the association resource and should be excluded from it. That assertion was made
  from the model's **name**, never from its placements. This section tests it. The test is
  geometric: if outgroup calls were spurious background they would sit further away, more often
  on the opposite strand, and more often with a gene in between.
""")

code(r'''
og = cache("Z4_outgroup_vs_rest", """
    SELECT CASE WHEN detection_model LIKE 'Outgroup%' THEN 'outgroup models (2)'
                ELSE 'other models (19)' END AS model_group,
           count(*) AS n_placements,
           count(DISTINCT nc_seq_hash) AS n_exact_ncrna,
           100.0 * avg(CASE WHEN direction = 'upstream' THEN 1 ELSE 0 END) AS pct_upstream,
           100.0 * avg(CASE WHEN same_strand THEN 1 ELSE 0 END) AS pct_same_strand,
           100.0 * avg(CASE WHEN n_cds_between = 0 THEN 1 ELSE 0 END) AS pct_no_cds_between,
           quantile_cont(abs(signed_distance_bp), 0.5) AS median_abs_bp,
           quantile_cont(nc_seq_len, 0.5) AS median_nc_len,
           quantile_cont(score, 0.5) AS median_score,
           100.0 * avg(CASE WHEN evalue <= 1e-5 THEN 1 ELSE 0 END) AS pct_evalue_le_1e5
    FROM rt_ncrna_pairs
    WHERE canonical AND file_label = 'Retron'
    GROUP BY 1 ORDER BY n_placements DESC
""", pop="PL-CANON")
display(og.round(2))

per = cache("Z4_outgroup_per_model", """
    SELECT detection_model, count(*) AS n_placements,
           count(DISTINCT nc_seq_hash) AS n_exact_ncrna,
           100.0 * avg(CASE WHEN direction = 'upstream' THEN 1 ELSE 0 END) AS pct_upstream,
           100.0 * avg(CASE WHEN same_strand THEN 1 ELSE 0 END) AS pct_same_strand,
           quantile_cont(abs(signed_distance_bp), 0.5) AS median_abs_bp,
           quantile_cont(score, 0.5) AS median_score,
           100.0 * avg(CASE WHEN evalue <= 1e-5 THEN 1 ELSE 0 END) AS pct_evalue_le_1e5
    FROM rt_ncrna_pairs
    WHERE canonical AND file_label = 'Retron' AND detection_model LIKE 'Outgroup%'
    GROUP BY 1 ORDER BY n_placements DESC
""", pop="PL-CANON")
display(per.round(2))

_o = og[og.model_group.str.startswith("outgroup")].iloc[0]
_r = og[og.model_group.str.startswith("other")].iloc[0]
print("\nVERDICT")
print(f"  upstream        outgroup {_o.pct_upstream:5.2f}%   other {_r.pct_upstream:5.2f}%")
print(f"  same strand     outgroup {_o.pct_same_strand:5.2f}%   other {_r.pct_same_strand:5.2f}%")
print(f"  no CDS between  outgroup {_o.pct_no_cds_between:5.2f}%   other {_r.pct_no_cds_between:5.2f}%")
print(f"  median |gap|    outgroup {_o.median_abs_bp:5.0f} bp  other {_r.median_abs_bp:5.0f} bp")
print()
print("  Outgroup-model placements sit in canonical retron architecture: as often upstream, as")
print("  often same-strand, MORE often with no intervening gene, and CLOSER to the RT than the")
print("  other nineteen models. The name records which model matched, not a verdict on the hit.")
print("  They are RETAINED. Excluding them would discard 4,156 pairs from tier T3 on a label.")
''')

md(r"""
---

# Z5 — The filter catalogue

* **Question.** Which flags can a downstream user apply to the association resource, what does
  each one cost, and which ones are traps?
* **Unit.** Exact RT-ncRNA pair over canonical Retron placements.
* **Denominator.** 30,287 pairs (tier T1).
* **Why it is here.** So that "how do I filter this further" is answered by a table a machine can
  read, not by prose a human has to re-derive. Every cost below is measured on this build.

`category` is the load-bearing column:

| category | meaning |
|---|---|
| `USE` | a real confidence flag; applying it is defensible |
| `IN_T3` | already applied in the default tier |
| `STRATIFY` | keep as a column, do **not** filter on it |
| `TRAP` | looks like quality, is not — see `note` |
| `NOOP` | already guaranteed upstream; costs nothing, gains nothing |
""")

code(r'''
_BASE = "canonical AND file_label = 'Retron'"

# (label, sql_predicate, category, note)
_FILTERS = [
    ("same_strand",              "same_strand",                                   "IN_T3",
     "RNA on the same strand as the RT"),
    ("not_downstream",           "direction <> 'downstream'",                     "IN_T3",
     "downstream is largely a window-truncation artefact"),
    ("no_intervening_cds",       "n_cds_between = 0",                             "IN_T3",
     "no annotated CDS between RT and RNA"),
    ("within_200bp",             "abs(signed_distance_bp) <= 200",                "IN_T3",
     "the joint-geometry mode; not a completeness bound"),
    ("evalue_le_1e5",            "evalue <= 1e-5",                                "IN_T3",
     "global CM threshold; hits models unevenly, see N6_cm_confidence_by_model"),
    ("evalue_le_1e10",           "evalue <= 1e-10",                               "USE",
     "stricter CM threshold"),
    ("score_ge_50",              "score >= 50",                                   "USE",
     "bit-score alternative to the E-value cut"),
    ("rt_fully_in_window",       "rt_in_window AND NOT rt_at_window_edge",        "USE",
     "RT not abutting the extracted window edge"),
    ("backtranslation_exact",    "bt_status = 'exact'",                           "USE",
     "RT protein reproduces from window DNA; alt_start is the main other class"),
    ("single_call_at_locus",     "n_calls_at_locus = 1",                          "USE",
     "one RNA call at that locus"),
    ("not_start_clipped",        "NOT true_start_clipped",                        "STRATIFY",
     "contig clipping is a stratification flag by project convention, not an exclusion"),
    ("not_end_clipped",          "NOT clipped_end_flag",                          "STRATIFY",
     "as above"),
    ("single_multiplicity",      "multiplicity_class = 'single_call'",            "STRATIFY",
     "placement multiplicity; use for weighting, not filtering"),
    ("drop_outgroup_models",     "detection_model NOT LIKE 'Outgroup%'",          "TRAP",
     "REJECTED: outgroup-model calls sit in canonical retron architecture - see Z4"),
    ("has_structure_annotation", "has_structure_annotation",                      "TRAP",
     "populated on 1.37% of placements; records annotation coverage, not quality"),
    ("nc_fully_in_window",       "nc_in_window AND NOT nc_at_window_edge",        "NOOP",
     "guaranteed by the canonical definition"),
    ("window_self_consistent",   "window_len_consistent AND NOT window_inverted", "NOOP",
     "guaranteed by the canonical definition"),
    ("one_ncrna_seq_at_locus",   "n_distinct_ncrna_seq_at_locus = 1",             "NOOP",
     "effectively guaranteed; costs 118 pairs"),
]

def _catalogue():
    base = Q(f"""SELECT count(DISTINCT (rt_seq_hash, nc_seq_hash)) n
                 FROM rt_ncrna_pairs WHERE {_BASE}""").n.iloc[0]
    rows = []
    for label, pred, cat, note in _FILTERS:
        r = Q(f"""SELECT count(DISTINCT (rt_seq_hash, nc_seq_hash)) n_pairs,
                    count(DISTINCT rt_seq_hash) n_rt, count(DISTINCT nc_seq_hash) n_ncrna
                  FROM rt_ncrna_pairs WHERE {_BASE} AND {pred}""").iloc[0]
        rows.append({"filter": label, "category": cat, "sql_predicate": pred,
                     "pairs_kept": int(r.n_pairs),
                     "pct_kept": round(100.0 * r.n_pairs / base, 2),
                     "pairs_lost": int(base - r.n_pairs),
                     "rts_kept": int(r.n_rt), "ncrnas_kept": int(r.n_ncrna),
                     "note": note})
    df = pd.DataFrame(rows)
    df.attrs["baseline"] = int(base)
    return df.sort_values(["category", "pairs_lost"]).reset_index(drop=True)

filters = cache("Z5_filter_catalogue", fn=_catalogue, pop="PAIR-CANON")
for cat in ["IN_T3", "USE", "STRATIFY", "TRAP", "NOOP"]:
    sub = filters[filters.category == cat]
    if len(sub):
        print(f"\n--- {cat} ---")
        display(sub[["filter", "pairs_kept", "pct_kept", "pairs_lost", "note"]])

print("\nbaseline (tier T1, canonical Retron pairs): "
      f"{Q(f'SELECT count(DISTINCT (rt_seq_hash, nc_seq_hash)) n FROM rt_ncrna_pairs WHERE {_BASE}').n.iloc[0]:,}")
print("Costs are MARGINAL - each filter applied alone to the baseline, never cumulatively.")
print("For the cumulative tiers see Z1_association_resource_tiers.")
''')
