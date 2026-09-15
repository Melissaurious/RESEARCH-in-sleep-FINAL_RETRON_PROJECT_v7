# dbchar_g7_stage1_report

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced all 5 landed
tables, all 4 figure files, `REPORT.html`, `REPORT.md` and `MANIFEST.tsv` byte for byte
(BS-3, WA-B.2). Log in §7.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). This is the Stage-1 closeout report over the seven landed
measurement gates. **It computes no scientific result** (launcher: *"the report assembler must
compute no scientific result"*).

---

## 1 · What was measured

Nothing. That is the point of the gate, and it is enforced rather than promised.

### How a number gets into the report

`findings.py` declares 70 named values. Each one is a five-tuple —
**(bundle, landed table, exact row selector, column, format)** — and `assemble_report.py`
resolves it by reading that table out of that landed bundle:

- a selector matching **zero** rows fails the build;
- a selector matching **more than one** row fails the build;
- a `{placeholder}` in the prose with no declared lookup fails the build;
- a `{...}` surviving into the finished HTML fails the build.

Every resolved value is landed as `g7_resolved_values.tsv` — key, bundle, table, selector,
column, raw string and rendered string — so any number in the report can be traced back to the
row it came from without re-reading the prose.

| | |
|---|---:|
| declared values resolved | 70 |
| sections | 8 |
| figures embedded (base64; the HTML is self-contained) | 5 |
| landed bundles read as hashed inputs | 7 |
| files hashed in `INPUTS.tsv` | 62 |

### The two re-plotted figures

Two figures landed in earlier gates were numerically correct and **unreadable**:

| figure | defect |
|---|---|
| `dbchar_g3_pair_geometry/fig01_distance_distribution` | raw-float bin labels rotated into the denominator stamp; the two panels' stamps overlap each other |
| `dbchar_g4_family_baseline/fig01_rt_length_by_family` | the stamp sits at −0.22 axes fractions of a 25-row axis — a ~2-inch band of white between the plot and its denominator |

`REPORTING_STANDARDS` is explicit that a restyle *"re-runs the figure script against unchanged
tables … never a reason to touch a landed bundle (BS-6)"*, and that a figure over another gate's
tables *"is its own gate"*. So `f01_restyle_figures.py` reads **only** the landed TSV each figure
shipped beside itself, re-emits those rows verbatim (BS-13), and lands the new figure here. The
originals stay exactly as they landed; `g7_figure_map.tsv` records which bundle produced each
figure in the report.

The only transformation applied to any number is a label format (`-2000.0` → `−2k`). No value,
percentage, denominator or ordering changed — the re-emitted TSVs are byte-comparable to the
source rows.

### What the report says

Eight sections, each naming the view and bundle it was computed on, each with its own caveat
block: the pinned corpus; the analytical-unit ladder; RT integrity and eligibility; RT↔ncRNA
geometry (the priority output); the two geometry signals that are technical rather than
biological; family baselines and the MULTI tie; metadata/taxonomy and redundancy correction; and
annotation-route disagreement. The closing section counts the registered derived datasets and
states that **no Stage-1 measurement has been promoted to a project claim**.

## 2 · Counts, including the ones that look bad (BS-5)

n_attempted: 70 declared value lookups, 5 figures, 7 gate status reads
n_succeeded: 70 / 5 / 7
n_dropped: 0

| | n |
|---|---:|
| declared values that failed to resolve | 0 (a failure aborts the build) |
| placeholders with no declared lookup | 0 (aborts the build) |
| unresolved `{...}` surviving into the HTML | 0 (aborts the build) |
| figures with no landed TSV beside them | **0** |
| figures with no producing script | **0** |
| numbers in the report with no producing bundle | **0** |
| derived datasets registered but absent from `data/derived` | 0 |
| derived datasets on disk but in no bundle registry | 0 |
| controls / failed | 1 / 0; seeded-bad rejected |

## 3 · The denominator's second count (WA-D.3)

This gate has no rate of its own, so there is no rate to second-count. What it has instead is a
**consistency check on landed provenance**, and it runs on every build:

- every `*_derived_registry.tsv` row across the seven bundles is collected; a dataset registered
  twice aborts the build;
- the registry set is compared against `data/derived/` on disk — a file registered but missing,
  or present but unregistered, aborts the build;
- the count is compared against `findings.N_DERIVED`; a mismatch aborts the build, so the number
  in the closing prose cannot drift from the registries. It is **16**.

The disk comparison is skipped (with a printed note) when `data/derived` is absent, because that
directory is gitignored and a clone-safe rerun must not depend on 40 GB of regenerated parquet.
The registry-to-registry checks and the `N_DERIVED` assertion still run.

**Positive control** (1, in `run.sh` before anything else): the assembler is handed a section
whose prose contains `{placeholder_that_has_no_lookup}`. It must **refuse**. If it builds, `run.sh`
stops with *"the assembler ACCEPTED an unresolvable placeholder — it is untested"* and the gate
fails. This is the control that makes the resolver's guarantees worth anything: without it,
"every number is resolved from a landed table" is an assertion about code nobody tested.

## 4 · Claims

**No claim status proposed, and none may be.** The launcher's human gate covers *"promoting a
proposed interpretation to a thesis/paper claim"*, and `human_input_audit` is `PENDING` for all
seven measurement gates. The report states this on its own front matter and again in its closing
paragraph.

The report *carries* the supporting evidence the earlier gates proposed (`C7`, `C8` and the
unit-ladder evidence), attributed to the bundle that measured it. It promotes nothing.

## 5 · The self-adversarial pass (BS-14)

**1 · Overstated words.** *"Computes nothing"* is true of the scientific content and false in the
narrow literal sense: the assembler formats numbers (thousands separators, 2-dp percentages) and
counts registry rows. Both are landed — the raw string sits beside the rendered one in
`g7_resolved_values.tsv`, so a formatting error is visible rather than hidden. *"Self-contained"*
means no network fetch and no external asset: the figures are base64-embedded and the CSS is
inline. It does not mean the report is independent of the bundles — it is a **view** of them, and
a reader who wants to check a number must open the named table.

**2 · Alternative explanations.** A report that resolves every number correctly out of landed
tables is still only as good as the tables. This gate cannot detect a wrong measurement, only a
number that disagrees with what its gate landed. Every scientific caveat in the report is
inherited from the gate that measured it, and §5 and §4 of the report carry the two that most
change the reading — the retron-only detector scope, and the join-rate circularity.

**3 · Could this have returned a negative?** Yes, and the resolver's refusal path is exercised on
every run by the seeded-bad control in §3, which is the only reason to believe the guarantee. The
build's checks were not, however, what caught the defects this gate actually had: **reading the
rendered page** caught the two illegible figures and the double-escaped title, and **comparing the
closing prose against `ls data/derived`** caught that it claimed eleven registered datasets where
sixteen exist — which is how the four unregistered g4/g6 datasets were found and added to
`data/README.md`. Each of those three is now under a check that would fail the build, but none of
them was found by one. A validator finds what its author already thought of.

**4 · Unit of every rate.** No rate originates here. Every number carries the unit and denominator
of the bundle that produced it, named in that bundle's `MANIFEST.tsv` and repeated under each
table the report expands.

**5 · Numbers with no producing script.** None. That is the property the gate exists to enforce,
and `g7_resolved_values.tsv` is the evidence.

**6 · What was withdrawn or weakened.**
- **Withdrawn:** the first `REPORT.html`, which embedded the two illegible figures as landed. The
  visual inspection the launcher requires is what caught them; re-rendering a page and looking at
  it found what no validator did.
- **Withdrawn:** a section-4 title written as `RT&harr;ncRNA`, which the HTML escaper correctly
  double-escaped into visible markup. Titles now carry the literal character.
- **Weakened:** the closing sentence's dataset count, from prose I typed to a number asserted
  against the registries at build time.
- **Weakened:** the `data/derived` consistency check, from a hard requirement to one that is
  skipped-with-a-note when the gitignored directory is absent, so a fresh clone can still verify
  the bundle.

## 6 · What changed from the plan

Three things.

1. The gate was planned as an assembler only. It became an assembler **plus a restyle script**
   when visual inspection showed two landed figures were unreadable. Governance routes that into
   a new gate rather than an edit, which is what was done.
2. `g7_resolved_values.tsv`, `g7_figure_map.tsv` and `g7_gate_status.tsv` were added so the report
   has landed tables of its own and `run.sh` has something to byte-compare besides the HTML.
3. The SVG output needed a declared `svg.hashsalt` and suppressed `Date`/`Software` metadata
   before the figures were byte-reproducible; matplotlib salts element ids from a random seed.
   Without that, this gate could never have passed its own stop condition.

## 7 · Reproduction log (BS-3, WA-B.2)

```
$ bash results/dbchar_g7_stage1_report/run.sh
== guard: the assembler must REFUSE a number it cannot resolve from a landed table
   refused the unresolvable placeholder, as required
== f01 re-plot two landed figures legibly, from their landed TSVs only
  fig01_distance_distribution_restyled.png / .svg / .tsv  (40 rows carried through unchanged)
  fig01_rt_length_by_family_restyled.png / .svg / .tsv  (25 rows carried through unchanged)
== assemble the report: resolve every number out of the landed bundles
REPORT.html: 869,121 bytes, 8 sections, 5 figures, 70 resolved values
== BS-3 / WA-B.2: does this reproduce the landed artifacts byte for byte?
  OK × 5 tables, OK × 4 figure files, OK REPORT.html, OK REPORT.md, OK MANIFEST.tsv
REPRODUCED: every landed artifact is byte-identical on rerun.
wall 1.2 s, exit 0
```

## 8 · The visual inspection the launcher requires

The launcher requires that `REPORT.html` *"must be self-contained and visually inspected before
Stage 1 closes"*. It was rendered headless at 1200 px wide (full page: 1200 × 7307) and read
top to bottom. Findings, all fixed above: the two illegible figures, and the double-escaped
section-4 title. One cosmetic defect is **retained and not fixed**: in the landed
`fig03_direction_by_family`, the legend box covers the `n=` label of the third row. The number is
in `g3_direction.tsv` and the row itself is legible, and repairing it would mean re-plotting a
third figure for a label that the table already carries.

## 9 · Acceptance

Open `INPUTS.tsv` and recognise the 62 inputs: the landed tables and figures of the seven
measurement gates, their `README.md` status lines, and their derived-dataset registries. Then
open `REPORT.html` in a browser — it needs nothing else on disk — and check any number in it
against the row `tables/g7_resolved_values.tsv` names for it.
