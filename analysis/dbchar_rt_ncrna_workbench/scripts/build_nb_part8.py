md(r"""
---

# M. Operon visualisation

Draws candidate RT–ncRNA operons directly from the canonical datasets. It does **not** depend on
the external `PipelineData`/`utils_FOR_ALL_FILES.py` helper or on any batch JSON: the coding
sequences come from `rt_window_cds_v1` and the ncRNA placement from `rt_ncrna_pairs_v1`, so the
figures inherit this project's populations and eligibility rules.

Two conventions are fixed:

* **Every operon is drawn on the canonical (`+`) strand.** Loci found on the minus strand are
  reflected about the window midpoint, so that transcription always runs left to right and operons
  are visually comparable. Coordinates, gap sizes and distances are unaffected — reflection is an
  isometry.
* **The strand a locus was actually found on is always shown**, as a badge beside the identifier.
  It cannot be switched off, because a normalised figure without it would be misleading.

Everything else is optional (`OperonStyle`), so a figure can be stripped down for a thesis panel.
""")

code(r'''
# ── M0. operon assembly from the canonical tables ────────────────────────────────────────────
from dataclasses import dataclass, replace, asdict, field
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

COLOR_RT      = "#E84B3A"
COLOR_OTHER   = ["#3AABCF", "#5DC46A", "#A855C8", "#F5A623", "#2BBFA4", "#E8617A",
                 "#4A90D9", "#8CBF3F", "#D4629A", "#F07C3E", "#5B8FF9", "#3EC9A7"]
COLOR_NCRNA   = "#7B4FA8"
COLOR_INK     = "#222222"
COLOR_MUTED   = "#888888"
COLOR_WARN    = "#CC4444"


@dataclass
class OperonStyle:
    """What to draw. `show_strand` is intentionally not configurable — see section M."""
    show_id: bool            = True     # locus / record identifier in the title
    show_gaps: bool          = True     # intergenic distances in bp
    show_ncrna_distance: bool= True     # RT<->ncRNA separation in bp
    show_gene_labels: bool   = False    # gene ids on non-RT genes (off, as in the original)
    show_rt_label: bool      = True     # the letters "RT" inside the RT gene
    show_ncrna_label: bool   = False    # the word "ncRNA" beside the glyph (off: the
                                        # artwork is self-evident, as in the original)
    show_scale_bar: bool     = True
    show_taxon: bool         = True     # species in the title line
    show_model: bool         = False    # covariance model that made the call
    show_coords: bool        = False    # absolute genomic start/end under the baseline
    show_context_genes: bool = True     # flanking non-operon genes, muted, for context
    show_operon_span: bool   = True     # bracket marking the delimited operon
    normalise_strand: bool   = True     # draw minus-strand loci reflected onto +
    ncrna_glyph: str         = "svg"    # "svg" (your artwork) | "cartoon" (fallback) | "none"
    gene_height: float       = 0.45
    fig_width: float         = 12.0
    row_height: float        = 2.8

    def only(self, *names):
        """Return a copy with ONLY the named show_* flags on. Strand is always drawn."""
        off = {f: False for f in asdict(self) if f.startswith("show_")}
        return replace(self, **{**off, **{n: True for n in names}})

STYLE = OperonStyle()          # module-level default; pass your own to plot_operons()


def delimit_operon(cds_rows, rt_idx, max_gap_bp=150):
    """Maximal run of co-directional CDS around the RT, broken by a gap > max_gap_bp.

    A transparent re-implementation of the anchor-run / operon-delimitation heuristic:
    extend from the RT gene in both directions while the next CDS is on the same strand and the
    intergenic distance does not exceed `max_gap_bp`. Overlapping genes (negative gap) never break
    a run. This is a heuristic, not a transcription-unit call.
    """
    strand = cds_rows[rt_idx]["cds_strand"]
    lo = hi = rt_idx
    while lo > 0:
        a, b = cds_rows[lo - 1], cds_rows[lo]
        if a["cds_strand"] != strand or (b["cds_start"] - a["cds_end"]) > max_gap_bp:
            break
        lo -= 1
    while hi < len(cds_rows) - 1:
        a, b = cds_rows[hi], cds_rows[hi + 1]
        if b["cds_strand"] != strand or (b["cds_start"] - a["cds_end"]) > max_gap_bp:
            break
        hi += 1
    return cds_rows[lo:hi + 1]


def fetch_operons(where="canonical AND file_label = 'Retron' AND n_cds_between = 0 "
                        "AND abs(signed_distance_bp) <= 200 AND same_strand "
                        "AND direction = 'upstream'",
                  limit=6, max_gap_bp=150, order_by="record_key",
                  min_genes=1, context_flank=1, scan=None):
    """Build operon datasets from rt_ncrna_pairs_v1 + rt_window_cds_v1.

    `where` is any predicate over rt_ncrna_pairs_v1. The default is the candidate
    RT-ncRNA association rule of section L7.
    """
    sel = Q(f"""
        SELECT source_file, line_no, record_key, locus_key, physical_locus_key,
               rt_start, rt_end, rt_strand, nc_start, nc_end, nc_strand,
               signed_distance_bp, direction, n_cds_between, same_strand,
               tax_species, taxonomy_system, detection_model, file_label, source_database,
               true_start_clipped, clipped_end_flag
        FROM rt_ncrna_pairs
        WHERE {where}
        ORDER BY {order_by}
        LIMIT {int(scan or limit * 8)}
    """)
    if sel.empty:
        return []

    keys = ", ".join(f"('{r.source_file}', {int(r.line_no)})" for r in sel.itertuples())
    cds_all = Q(f"""
        SELECT source_file, line_no, cds_idx, gene_id, cds_start, cds_end, cds_strand,
               is_rt_gene, partial
        FROM rt_window_cds
        WHERE (source_file, line_no) IN ({keys})
        ORDER BY source_file, line_no, cds_start
    """)

    out = []
    for r in sel.itertuples():
        rows = cds_all[(cds_all.source_file == r.source_file) &
                       (cds_all.line_no == r.line_no)].to_dict("records")
        if not rows:
            continue
        rt_i = next((i for i, c in enumerate(rows) if c["is_rt_gene"]), None)
        if rt_i is None:                      # RT CDS absent: fall back to the RT interval itself
            rows.append(dict(gene_id="RT (reconstructed)", cds_start=r.rt_start, cds_end=r.rt_end,
                             cds_strand=r.rt_strand, is_rt_gene=True, partial=""))
            rows.sort(key=lambda c: c["cds_start"])
            rt_i = next(i for i, c in enumerate(rows) if c["is_rt_gene"])
        run = delimit_operon(rows, rt_i, max_gap_bp=max_gap_bp)
        if len(run) < min_genes:
            continue
        run_ids = {c["gene_id"] for c in run}
        lo = max(0, rows.index(run[0]) - context_flank)
        hi = min(len(rows), rows.index(run[-1]) + 1 + context_flank)
        out.append(dict(
            cds=run,
            context=[c for c in rows[lo:hi] if c["gene_id"] not in run_ids],
            n_cds_in_window=len(rows), max_gap_bp=max_gap_bp,
            rt_gene_id=rows[rt_i]["gene_id"], strand=r.rt_strand,
            ncrna=(int(r.nc_start), int(r.nc_end), r.nc_strand),
            label=r.locus_key, record_key=r.record_key,
            taxon=r.tax_species, taxonomy_system=r.taxonomy_system,
            model=r.detection_model, family=r.file_label, database=r.source_database,
            distance_bp=r.signed_distance_bp, direction=r.direction,
            clipped=bool(r.true_start_clipped or r.clipped_end_flag),
        ))
        if len(out) >= limit:
            break
    return out

print("M0 ready — fetch_operons(), delimit_operon(), OperonStyle")
''')

code(r'''
# ── M1. drawing ──────────────────────────────────────────────────────────────────────────────
def _arrow(ax, x0, x1, y, h, color, edge=COLOR_INK):
    """A gene arrow always pointing right (strand normalisation happens before this)."""
    tip = min((x1 - x0) * 0.30, 0.18)
    yb, yt = y - h / 2, y + h / 2
    body = x1 - tip
    ax.add_patch(mpatches.Polygon([(x0, yb), (body, yb), (x1, y), (body, yt), (x0, yt)],
                                  closed=True, facecolor=color, edgecolor=edge,
                                  linewidth=0.8, zorder=3))


def _ncrna_cartoon(ax, xc, y_base, h):
    """A small stem-loop glyph: no external asset, always available."""
    stem_w, stem_h, loop_r = h * 0.16, h * 0.78, h * 0.34
    ax.add_patch(mpatches.FancyBboxPatch((xc - stem_w / 2, y_base), stem_w, stem_h,
                                         boxstyle="round,pad=0.002", facecolor=COLOR_NCRNA,
                                         edgecolor=COLOR_NCRNA, zorder=4))
    ax.add_patch(mpatches.Circle((xc, y_base + stem_h + loop_r * 0.72), loop_r,
                                 facecolor="none", edgecolor=COLOR_NCRNA, linewidth=1.9, zorder=4))
    for dy in (0.30, 0.52, 0.74):
        ax.add_artist(Line2D([xc - stem_w * 1.5, xc + stem_w * 1.5],
                             [y_base + stem_h * dy] * 2, color="white",
                             linewidth=0.7, zorder=5))


def _ncrna_auto_zoom(img, gene_h, row_height):
    """The original sizing rule: scale the artwork to ~2.2 gene-heights in axes units."""
    target_axes_h = gene_h * 2.2
    pt_per_unit   = (row_height / (gene_h * 7)) * 72
    return (target_axes_h * pt_per_unit) / img.shape[0]


def _ncrna_svg(ax, xc, y_base, h, zoom=None, row_height=2.8):
    """The project's ncRNA artwork, sized by the original auto-zoom rule."""
    img = _load_ncrna_svg()
    if img is None:
        return _ncrna_cartoon(ax, xc, y_base, h)
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    ax.add_artist(AnnotationBbox(OffsetImage(img, zoom=zoom or _ncrna_auto_zoom(img, h, row_height)),
                                 (xc, y_base), frameon=False, xycoords="data",
                                 box_alignment=(0.5, 0.0), zorder=4))


_NCRNA_SVG_CACHE = {}
NCRNA_SVG_PATH = Path("/home/borg/RETRONS_january_2026/the-retron-project/FINAL_REPORT/"
                      "retron_ncrna4.svg")

def _load_ncrna_svg():
    """Load the SVG glyph once, white->transparent. Returns None if unavailable."""
    if "img" in _NCRNA_SVG_CACHE:
        return _NCRNA_SVG_CACHE["img"]
    img = None
    try:
        if NCRNA_SVG_PATH.exists():
            import io as _io, cairosvg
            from PIL import Image
            arr = np.array(Image.open(_io.BytesIO(
                cairosvg.svg2png(url=str(NCRNA_SVG_PATH), scale=8.0))).convert("RGBA"))
            white = (arr[:, :, 0] > 230) & (arr[:, :, 1] > 230) & (arr[:, :, 2] > 230)
            arr[white, 3] = 0
            img = arr
    except Exception as exc:                       # missing cairosvg, bad asset, anything
        print(f"  [note] ncRNA SVG unavailable ({exc.__class__.__name__}); using the cartoon glyph")
    _NCRNA_SVG_CACHE["img"] = img
    return img


def _stack_label(ax, x, text, taken, y0, fontsize=6.5, color=COLOR_MUTED):
    """Place a label under the baseline, stepping down to avoid a near neighbour."""
    y = y0
    for lx, ly in taken:
        if abs(lx - x) < 0.6:
            y = min(ly - 0.26, y)
    taken.append((x, y))
    ax.text(x, y, text, ha="center", va="top", fontsize=fontsize, color=color)


def draw_operon(ax, d, style: OperonStyle = None):
    """Draw one operon onto `ax`, normalised to the + strand."""
    st = style or STYLE
    cds, strand = d["cds"], d["strand"]
    nc_s, nc_e, nc_strand = d["ncrna"]

    ctx = d.get("context", []) if st.show_context_genes else []
    coords = ([c["cds_start"] for c in cds + ctx] + [c["cds_end"] for c in cds + ctx]
              + [nc_s, nc_e])
    gmin, gmax = min(coords), max(coords)
    flip = st.normalise_strand and strand == "-"
    ref  = (lambda bp: gmin + gmax - bp) if flip else (lambda bp: bp)

    pad   = (gmax - gmin) * 0.08
    scale = st.fig_width / max(gmax - gmin + 2 * pad, 1)
    x     = lambda bp: (ref(bp) - (gmin - pad)) * scale

    h, yc = st.gene_height, 0.0
    yb    = yc - h / 2
    ax.axis("off")

    # ---- title: identifier, taxon, model -- and ALWAYS the strand badge ----
    bits = []
    if st.show_id:    bits.append(str(d["label"]))
    if st.show_taxon and d.get("taxon"): bits.append(str(d["taxon"]).replace("_", " "))
    if st.show_model and d.get("model"): bits.append(str(d["model"]))
    if bits:
        ax.set_title("   ·   ".join(bits), loc="left", fontsize=9, fontweight="bold",
                     color="#444444", pad=6)
    badge = f"found on {strand} strand" + ("  → drawn 5′→3′ on +" if flip else "")
    ax.text(0.999, 1.0, badge, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.4, color="white", zorder=6,
            bbox=dict(boxstyle="round,pad=0.30",
                      facecolor="#444444" if strand == "+" else "#8A5A2B",
                      edgecolor="none"))

    # ---- baseline ----
    ax.add_artist(Line2D([x(gmin - pad * 0.4) if not flip else x(gmax + pad * 0.4),
                          x(gmax + pad * 0.4) if not flip else x(gmin - pad * 0.4)],
                         [yb, yb], color=COLOR_INK, linewidth=1.2, zorder=0))

    # ---- flanking context genes, muted and behind ----
    for c in ctx:
        x0, x1 = sorted((x(c["cds_start"]), x(c["cds_end"])))
        tipc = min((x1 - x0) * 0.30, 0.18)
        pts = ([(x0, yc - h*0.30), (x1 - tipc, yc - h*0.30), (x1, yc),
                (x1 - tipc, yc + h*0.30), (x0, yc + h*0.30)]
               if (c["cds_strand"] == strand) != flip else
               [(x1, yc - h*0.30), (x0 + tipc, yc - h*0.30), (x0, yc),
                (x0 + tipc, yc + h*0.30), (x1, yc + h*0.30)])
        ax.add_patch(mpatches.Polygon(pts, closed=True, facecolor="#DDDDDD",
                                      edgecolor="#AAAAAA", linewidth=0.6, zorder=1))

    # ---- genes, ordered 5'->3' after normalisation ----
    ordered = sorted(cds, key=lambda c: ref(c["cds_start"]))
    k = 0
    for c in ordered:
        x0, x1 = sorted((x(c["cds_start"]), x(c["cds_end"])))
        is_rt  = bool(c["is_rt_gene"])
        _arrow(ax, x0, x1, yc, h, COLOR_RT if is_rt else COLOR_OTHER[k % len(COLOR_OTHER)])
        if not is_rt: k += 1
        if is_rt and st.show_rt_label:
            ax.text((x0 + x1) / 2, yc, "RT", ha="center", va="center", fontsize=10,
                    color=COLOR_INK, zorder=5)
        elif not is_rt and st.show_gene_labels:
            ax.text((x0 + x1) / 2, yc + h / 2 + 0.09, str(c["gene_id"]).split("_")[-1],
                    ha="center", va="bottom", fontsize=8, fontweight="bold", color=COLOR_INK)

    # ---- bracket marking the delimited operon ----
    if st.show_operon_span and ctx:
        xs = [x(c["cds_start"]) for c in cds] + [x(c["cds_end"]) for c in cds]
        bx0, bx1 = min(xs), max(xs)
        yv = yc + h * 1.32
        ax.add_artist(Line2D([bx0, bx1], [yv, yv], color="#666666", linewidth=1.0))
        for xe in (bx0, bx1):
            ax.add_artist(Line2D([xe, xe], [yv - 0.06, yv], color="#666666", linewidth=1.0))
        ax.text((bx0 + bx1) / 2, yv + 0.03,
                f"operon run (gap \u2264 {d.get('max_gap_bp', '?')} bp)",
                ha="center", va="bottom", fontsize=6.4, color="#666666")

    taken = []

    # ---- intergenic distances ----
    if st.show_gaps:
        for a, b in zip(ordered, ordered[1:]):
            # `ordered` is in DISPLAY order, which is reverse-genomic for a mirrored locus.
            # Intergenic distance must be computed in genomic coordinates, so sort the pair.
            lo, hi = (a, b) if a["cds_start"] <= b["cds_start"] else (b, a)
            gap = hi["cds_start"] - lo["cds_end"]
            mid = x((lo["cds_end"] + hi["cds_start"]) / 2)
            _stack_label(ax, mid, f"{gap} bp" if gap >= 0 else f"{gap} bp (overlap)",
                         taken, yb - 0.18, color=COLOR_WARN if gap < 0 else COLOR_MUTED)

    # ---- ncRNA ----
    nc_x = None
    if st.ncrna_glyph != "none":
        xc = nc_x = x((nc_s + nc_e) / 2)
        if st.ncrna_glyph == "svg":
            _ncrna_svg(ax, xc, yb, h, row_height=st.row_height)
        else:
            _ncrna_cartoon(ax, xc, yb, h)
        if st.show_ncrna_label:
            lift = h * 2.55 if st.ncrna_glyph == "svg" else h * 2.05
            ax.text(xc, yb + lift, "ncRNA", ha="center", va="bottom", fontsize=7.5,
                    color=COLOR_NCRNA, fontweight="bold")
        if st.show_ncrna_distance and d.get("distance_bp") is not None:
            nearest = min(ordered, key=lambda c: min(abs(c["cds_start"] - nc_e),
                                                     abs(nc_s - c["cds_end"])))
            edge = nearest["cds_start"] if ref(nearest["cds_start"]) > ref(nc_e) else nearest["cds_end"]
            _stack_label(ax, (xc + x(edge)) / 2, f"{int(abs(d['distance_bp']))} bp",
                         taken, yb - 0.18, color=COLOR_NCRNA)

    # ---- absolute coordinates ----
    if st.show_coords:
        ax.text(x(gmin if not flip else gmax), yb - 0.62, f"{gmin:,}", ha="center", va="top",
                fontsize=6, color=COLOR_MUTED)
        ax.text(x(gmax if not flip else gmin), yb - 0.62, f"{gmax:,}", ha="center", va="top",
                fontsize=6, color=COLOR_MUTED)

    # ---- scale bar ----
    if st.show_scale_bar:
        span = gmax - gmin
        unit = 10 ** int(np.floor(np.log10(max(span / 4, 10))))
        bar  = unit * max(1, int((span / 4) / unit))
        # keep clear of the ncRNA artwork, which is tall and anchored on the baseline
        on_left = nc_x is None or nc_x > st.fig_width * 0.5
        x0 = st.fig_width * 0.02 if on_left else st.fig_width * 0.98 - bar * scale
        ax.add_artist(Line2D([x0, x0 + bar * scale], [yc + h * 2.4] * 2,
                             color=COLOR_INK, linewidth=1.6))
        ax.text(x0 + bar * scale / 2, yc + h * 2.5,
                f"{bar:,} bp", ha="center", va="bottom", fontsize=6.6, color=COLOR_INK)

    ax.set_xlim(-st.fig_width * 0.01, st.fig_width * 1.01)
    ax.set_ylim(yc - h * 3.6, yc + h * (4.9 if st.ncrna_glyph == "svg" else 3.6))


def plot_operons(datasets, style: OperonStyle = None, filename=None, title=None):
    """Draw a stack of operons, one per row."""
    st = style or STYLE
    if not datasets:
        print("no operons to draw"); return None
    fig, axes = plt.subplots(len(datasets), 1,
                             figsize=(st.fig_width, st.row_height * len(datasets)), squeeze=False)
    for ax, d in zip(axes[:, 0], datasets):
        draw_operon(ax, d, st)
    if title:
        fig.suptitle(title, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(h_pad=2.2, rect=(0, 0, 1, 0.99 if title else 1))
    if filename:
        savefig(fig, filename, sources=["rt_window_cds_v1", "rt_ncrna_pairs_v1"], section="M")
        fig.savefig(FIGURES / f"{filename}.pdf", bbox_inches="tight")
        print(f"saved → {FIGURES / filename}.png + .pdf")
    plt.show()
    return fig

print("M1 ready — draw_operon(), plot_operons()")
''')

md(r"""
## M2 — Candidate operons under the section-L7 association rule

* **Question.** What do the loci selected by the candidate RT–ncRNA rule actually look like?
* **Unit.** Genomic locus, one panel each.
* **Denominator.** None — these are illustrative examples drawn from the 190,028 placements
  satisfying the L7 rule, not a sample supporting a rate.
* **Data.** `rt_ncrna_pairs_v1` (placement, taxonomy, model) and `rt_window_cds_v1` (coding
  sequences in the extraction window).
""")

code(r'''
ops = fetch_operons(limit=6, min_genes=2)   # min_genes=2 -> illustrative multi-gene operons
print(f"{len(ops)} operons assembled\n")
for d in ops:
    print(f"  {d['label']:<40s} strand={d['strand']}  genes={len(d['cds']):2d}  "
          f"ncRNA {d['distance_bp']:+.0f} bp  {d['taxon']}")

plot_operons(ops, title="Candidate RT–ncRNA operons (all normalised to the + strand)",
             filename="M2_operons_default")
''')

code(r'''
# Both strands side by side, to show that normalisation makes them comparable.
plus  = fetch_operons(where="canonical AND file_label = 'Retron' AND rt_strand = '+' "
                            "AND n_cds_between = 0 AND abs(signed_distance_bp) <= 200 "
                            "AND same_strand AND direction = 'upstream'", limit=2)
minus = fetch_operons(where="canonical AND file_label = 'Retron' AND rt_strand = '-' "
                            "AND n_cds_between = 0 AND abs(signed_distance_bp) <= 200 "
                            "AND same_strand AND direction = 'upstream'", limit=2)
plot_operons(plus + minus, title="Two plus-strand and two minus-strand loci, drawn identically",
             filename="M2_operons_strand_normalised")
''')

md(r"""
## M3 — Controlling what appears on the figure

`OperonStyle` turns each element on or off. `style.only(...)` gives a minimal figure with just the
named elements. The strand badge is drawn in every case.
""")

code(r'''
# The operon boundary is a threshold choice, so show what it costs.
def _gap_sens():
    rows = []
    for g in (50, 100, 150, 300, 500):
        runs = [len(o["cds"]) for o in fetch_operons(limit=60, max_gap_bp=g, scan=240)]
        rows.append({"max_gap_bp": g, "n_loci": len(runs),
                     "median_genes_in_run": float(np.median(runs)),
                     "pct_single_gene": round(100 * np.mean([r == 1 for r in runs]), 1)})
    return pd.DataFrame(rows)

sens = cache("M_operon_gap_sensitivity", fn=_gap_sens, force=True)
display(sens)
print("  the operon boundary is a heuristic; this is its sensitivity on 60 example loci.")

# 1. everything on
plot_operons(ops[:2], style=OperonStyle(show_coords=True, show_model=True),
             title="Maximal: every annotation enabled")

# 2. thesis panel — no bp labels, no gene ids, no identifier
plot_operons(ops[:2], style=STYLE.only("show_rt_label", "show_scale_bar"),
             title="Minimal: architecture only (no distances, no identifiers)",
             filename="M3_operons_minimal")

# 3. distances kept, identifiers dropped
plot_operons(ops[:2],
             style=OperonStyle(show_id=False, show_taxon=False, show_gene_labels=False),
             title="Distances retained, identifiers removed")
''')

md(r"""
**Interpretation.** Under the candidate rule the architecture is visually consistent: the ncRNA sits
immediately 5′ of the RT with no coding sequence between them, and the RT is typically the first or
second gene of a short co-directional run. Normalising minus-strand loci onto the plus strand makes
that comparison possible at a glance; without normalisation half the panels would read right to
left.

**Caveats.** (i) The operon boundary is a **heuristic**: a maximal run of co-directional coding
sequences around the RT, broken by an intergenic gap exceeding `max_gap_bp` (default 150 bp). It is
not a transcription-unit call, and no terminator prediction is used. Changing `max_gap_bp` changes
the number of genes drawn. (ii) Genes shown are those annotated **within the extraction window**; a
window truncated at a contig end will show a shortened operon, and `d["clipped"]` flags those loci.
(iii) These panels are illustrative examples chosen by a query, not a random sample, and support no
rate. (iv) Reflection preserves distances and gene order exactly; it changes only the direction of
the axis, so every number printed on a normalised figure is the true genomic value.
""")
