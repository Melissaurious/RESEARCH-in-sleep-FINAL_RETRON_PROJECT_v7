# rt07_g1_history_and_definition

STATUS: VERIFIED — `run.sh` was rerun from this assembled bundle and reproduced every landed table, both reports and `MANIFEST.tsv` byte-for-byte.

    bundle_status:     REPRODUCIBLE
    human_input_audit: PENDING

Weight **FULL** (launcher §7). Settles `C3` supporting, `C9` supporting. No claim is promoted here.

---

## 1 · What was measured

**One measurement:** the evidence class of every region name in scope, in every derivational
primary source — motif evidence, alignment block, explicit stated boundary, terminology only,
or inherited-without-definition — counted, with the unresolved-definition register and the
acquisition and source-resolution register for `ALIGN_000044`.

6 sources × 32 region names = **192 cells**. 53 carry evidence; 129 are cells where the source
never names the region. Every classification rests on a **verbatim quote verified against the
extracted text by the code that builds the table** — 36 quotes declared, 0 unverifiable. Page
locators are derived from the text, never asserted.

The evidence set is the four Tier-1 derivational papers, the Tier-1 structural paper (which may
constrain but not seed), and `ALIGN_000044`. **No Tier-2 comparator was read.** Toro 2014,
Mestre 2020, myRT and Toro 2026 all carry the RT0–RT7 convention under audit; reading them here
would have reproduced the convention by construction.

### `ALIGN_000044` — acquired, and it does not contain the blocks

Governed acquisition succeeded on the fifth attempt. Dbfetch returned an error string under
HTTP 200; the ENA browser API rejects the legacy accession format twice; the retired **EMBL
Alignment Database archive at EMBL-EBI** holds it. Recorded: source URL, authority, retrieval
date 2026-09-15T15:46:41Z, archive Last-Modified 2009-02-11, access conditions (anonymous
HTTPS, no credentials), byte counts and SHA256 — before use, per launcher §9a.

The record is a **1,441-column alignment of 66 proteins**, submitted 13-NOV-2000, built by
*PILEUP, CLUSTALX and manual adjustment*. It annotates **three** domains — RT at columns
261–886, maturase 1123–1235, nuclease 1319–1441 — and **zero** numbered subdomains.

> `PROPOSED:` the authors' own alignment is the right substrate for `g2` and the wrong source
> for the labels. Blocks must be **re-derived** on it from the stated conservation criteria and
> the recovery reported as a measurement. The stated manual adjustment step also means this is a
> fixed primary artefact, not a reproducible procedure.
>
> Would be wrong if: the numbered subdomains are annotated in the `.aln` companion or in
> supplementary material this gate did not parse. The `.aln` was acquired and hashed; only the
> `.dat` was read for annotation.
> → `scripts/s04_acquisition_register.py` · `tables/g1_align000044_record_summary.tsv`

### Terminology genealogy — 12 edges, 6 leaving the held set

The seven-way partition originates with **Xiong & Eickbush 1990**: *"Seven peptide regions
(domains 1-7) containing 178 amino acids were found to be common to all elements."*
**Zimmerly 2001** numbers subdomains 0–7 but states the labels are *"labeled according to
previous studies (7,9,32) taking into account the boundaries of conservation seen in our
alignment"* — refs 7/9/32 are Malik, Burke & Eickbush 1999, Gorbalenya 1994 and Xiong &
Eickbush 1990, of which only the last is held. **Blocker 2005** supplies the modern `RT0–RT7`
spelling as a respelling with citations to all three. **Poch 1989** is a different partition
(motifs A–D of five RT-motifs), cross-walked by Xiong to domains 3–7.

> `PROPOSED:` RT0 is the weakest link and it is the link RT0 hangs from — *"Domain 0 was
> formerly called domain Z but was more recently renamed domain 0 in non-LTR RTs (7)"*. Both
> held statements of RT0's scope **cite** Malik et al. 1999 rather than deriving the region, and
> that paper is not held by this project.
>
> Would be wrong if: Gorbalenya 1994 or Malik et al. 1999 contains a derivation that changes the
> direction of inheritance. Neither is held, so this is a statement about the held set.
> → `scripts/s03_evidence_matrix.py` · `tables/g1_terminology_genealogy.tsv`

### What can be operationalised

| verdict | n | regions |
|---|---|---|
| `DERIVABLE_PROCEDURE` | 18 | domains 0–7, 2a, X, motifs A–D, Y/FxDD, regions a–e, both spacers |
| `STRUCTURAL_DEFINED_ELSEWHERE` | 3 | palm, fingers, thumb |
| `SPELLING_ONLY_NO_INDEPENDENT_DERIVATION` | 7 | RT1–RT7 as modern spellings |
| `SPELLING_WITH_STRUCTURAL_COORDINATE_ONLY` | 1 | RT0 as a modern spelling |
| `STATED_RESIDUE_BOUNDARY` | 1 | the RT domain as a whole |
| `NO_OPERATIONAL_BASIS` | 1 | motif E |
| `NOT_IN_HELD_EVIDENCE` | 1 | motif F |

**Exactly one region has a stated residue boundary, and it is the container, not a block.**
No source in the held set gives a per-block residue extent for any of domains 0–7.

> `PROPOSED:` the RT1–RT7 framework is operationally recoverable but not readable: Xiong &
> Eickbush state a restatable criterion — conserved positions present in *"over 50% of the RT
> elements from three of the four most abundant groups"* — so `g2` can attempt recovery on the
> acquired alignment. What no one published is where each block starts and ends.
>
> Would be wrong if: a per-block coordinate table exists in supplementary material for any of
> the four papers. The reference package records that **no Tier-1 supplementary file exists
> anywhere locally**, so this gate could not check that.
> → `tables/g1_region_verdicts.tsv` · `tables/g1_operational_evidence_matrix.tsv`

### Spelling and concept are different objects

`RT1` as a literal token appears **0 times** in Xiong & Eickbush 1990 and **once** in Zimmerly
2001 — and that single hit is the gene name `C.e.RT1`, not a subdomain label, which is why the
cell lands `NAMED_UNCLASSIFIED` rather than carrying an evidence class. The concept is present
in both papers; the spelling is not. Modern-spelling rows therefore carry their own verdict vocabulary so
that "RT1 has no operational basis" can never be read off this table as a statement about
domain 1 — which lands `DERIVABLE_PROCEDURE`.

### RT0 stays analytically distinct, and now on verified grounds

*"subdomain 0 is conserved only between group II intron and non-LTR RTs"* — verified verbatim in
Zimmerly 2001, and independently restated by Simon & Zimmerly 2008 (*"domains 0 and 2a are
shared among only a subset of RT classes"*). The launcher's separation of RT0 from RT1–RT7 now
rests on the sources rather than on the prior dossier. `domain_2a` carries the companion
statement, and it is the **only** held Tier-1 sentence naming retron RTs together with a
numbered region: *"subdomain 2A is weakly conserved among non-LTR, group II intron and retron
RTs."*

## 2 · Counts, including the ones that look bad (BS-5)

    n_attempted:  192 cells (6 sources x 32 region names) + 36 quote assignments
                  + 12 genealogy edges + 7 acquisition attempts
    n_succeeded:  53 cells classified from verified evidence; 36/36 quotes verified;
                  12/12 genealogy quotes verified; 2 files acquired and hash-verified
    n_dropped:    0 — nothing was discarded. 129 NOT_NAMED cells and 10 NAMED_UNCLASSIFIED
                  cells are retained and reported as their own states, and 5 failed
                  acquisition attempts are landed as rows rather than deleted.

Ugly counts kept in view: **1 region has no operational basis** (motif E), **1 name does not
exist in the held derivational sources at all** (motif F), **6 of 12 genealogy edges point at
sources this project does not hold**, and **18 of 25 assessed (source, region) pairs cannot
define an operational boundary**.

## 3 · The second count (WA-D.3) and positive controls

**Second count.** 9 spot-checks, route A = compiled Python regexes over NFKC-normalised text,
route B = `tr`/`grep`/`wc` sharing no code with route A. **0 disagreements.** Separately, every
PDF was rendered twice (`raw` and `-layout`) and all 192 cells counted in both: 14 cells
disagree between renderings and are landed in `tables/g1_census_route_agreement.tsv` rather than
reconciled.

**Positive controls, 9/9 PASS**, declared before any zero was reported:

| control | expected | observed |
|---|---|---|
| modern-spelling detector, RT0–RT7 | non-zero in a source known to use the spelling (Blocker 2005) | 5–21 per token |
| alignment-annotation detector | non-zero: the record names the domain it annotates | 4 |

**Seeded-bad guard.** `run.sh` runs the census first with deliberately broken patterns and
**aborts if the controls still pass**. They fail, as required.

> **The alignment control earned its place on the first run: it FAILED.** EMBL line-type codes
> (`CC`) split every wrapped sentence, so the record read as naming no domain at all. The zero it
> was guarding was an artefact of extraction, not a property of the record. Without that control
> this bundle would have reported "the authors' alignment does not name the RT domain" — and
> been wrong. → `scripts/rt07g1lib.py::embl_prose`

## 4 · Claims

| id | role | what this gate contributes | status |
|---|---|---|---|
| `C3` | supporting | The evidence basis for reproducible operational definitions is now classified per source and region, with 18 regions holding a derivable procedure and exactly 1 stated residue boundary. | `UNPROVEN` |
| `C9` | supporting | Detection and boundary delimitation are shown to be separable *in the literature itself*: every source names and localises regions it never delimits. | `UNPROVEN` |

No claim is promoted. No prior number became an acceptance criterion.

## 5 · The self-adversarial pass (BS-14)

1. **Could the evidence classes be my reading rather than the sources'?** Partly — the class is a
   judgement. It is constrained by requiring a verbatim quote that the build verifies, so a class
   can be wrong but cannot be unsupported. All 36 quotes verify; the curated layer is hashed in
   `INPUTS.tsv` so a later edit invalidates the bundle.
2. **Could a zero mean the detector is broken?** That is exactly what happened once, and the
   control caught it. Every remaining zero is licensed by a control that returns non-zero on a
   known-present case; cells without such a licence are marked in the matrix.
3. **Could a comparator have leaked in?** No Tier-2 asset is in `INPUTS.tsv`, in the source list,
   or in any script path. The evidence set is enumerated in `control/sources.tsv`.
4. **Is "no per-block boundary exists" too strong?** It is scoped to the held set and to what was
   read: running text and the alignment record. Figures were not digitised and no Tier-1
   supplementary material exists locally. Stated as `U03` in the register, not as a finding.
5. **Does acquiring `ALIGN_000044` make the frame circular?** No — it predates every convention
   under audit and was fetched by accession from the paper's own front page, without consulting a
   comparator. It is Tier-1 derivational by the launcher's own tier table.
6. **Would the gate have reported failure honestly?** The failure paths are exercised, not
   asserted: 5 failed acquisition attempts are landed as rows, `MISSING_PRIMARY_ASSET` is
   implemented and reachable, and the seeded-bad guard proves the controls can fail.

## 6 · What changed from the plan

- The launcher scoped figure digitisation as an authorised fallback for `g1`/`g2`. **It was not
  needed in `g1`**: route 1 (original alignment) succeeded for Zimmerly 2001, and route 2
  (textual criteria) succeeded for Xiong & Eickbush. Digitisation stays available for `g2`
  extents, with extraction uncertainty attached.
- The non-LTR R2 structure was **not** acquired. It is approved, but `g1` measures literature
  evidence classes and cannot use a structure; landed as `NOT_ATTEMPTED_NOT_NEEDED_IN_G1`.
- The verdict vocabulary gained `SPELLING_*` and `STRUCTURAL_DEFINED_ELSEWHERE` after the first
  run showed that a single `NO_OPERATIONAL_BASIS` label would have made "RT1" read as a claim
  about domain 1.

## 7 · What surprised me

- **The founding paper is more rigorous than its reputation.** The story that Xiong & Eickbush's
  1990 boundaries were drawn by eye with no published criterion is **refuted by the paper**: it
  states a quantitative inclusion rule and a construction procedure, and reports that Poch's
  motifs and Webster's blocks independently confirm domains 2–7, with **domain 1 alone
  unconfirmed** — by the authors' own admission.
- **The authors' own alignment does not contain the blocks.** The single highest-value asset in
  the whole register was acquired successfully and turns out not to answer the question it was
  wanted for. It is still the right substrate; it is not the answer.
- **Block absence was described in 1990.** *"Most of the RNA viruses did not have a complete
  domain 6"* — whole classes lacking a block is original to the founding literature, not an
  artefact this project's detectors will introduce.
- **Motif F does not exist** in any held derivational source, and motif E exists only to be
  excluded from Poch's four.

## 8 · What I could NOT check

- **Malik, Burke & Eickbush 1999 and Gorbalenya 1994** — the two unheld sources that the RT0 and
  2a labels come from. RT0's definition is one citation outside this project's evidence set.
- **Figure 1 of Xiong & Eickbush and Figures 2–3 of Zimmerly 2001** — not digitised in this gate.
  Per-block extents may exist there as printed columns.
- **Figure 4 of Simon & Zimmerly 2008** — so the claim that the 59 across-the-set alignable
  characters lie in domains 3–5 is neither confirmed nor refuted (`U02`).
- **All Tier-1 supplementary material** — the reference package records that none exists locally.
- **The `.aln` companion file** — acquired and hashed, but only the `.dat` was parsed.

## 9 · Reproduction log (BS-3, WA-B.2)

    $ bash results/rt07_g1_history_and_definition/run.sh
    == 0. extract the evidence text (sha256-verified inputs)
    extracted 6 sources (59 pages), routes verified by sha256
    == 1. seeded-bad guard: a broken detector MUST fail its own controls
    SEEDED-BAD GUARD PASSED (the broken detector failed its controls, as required)
    == 2. naming census + positive controls
    census rows      : 192 (6 sources x 32 regions)
    positive controls: 9/9 PASS
    == 3. evidence matrix, genealogy, operational matrix, unresolved register
    quotes verified  : 36/36
    == 4. acquisition and source-resolution register (verify, never re-fetch)
    acquired and verified: 2
    == 5. independent second count (coreutils route, no shared code)
    second count: 9 check(s), 0 disagreement(s)
    == 6. summary and prior reconciliation
    == 7. report (computes nothing; every value resolves to a landed table)
    report assembled: 39 values resolved, 7 sections
    == 8. manifest and inputs
    == 9. byte comparison against the landed bundle
    REPRODUCED: every landed table, report and manifest is byte-identical on rerun.

`REPORT.html` was checked to be **self-contained** — no external stylesheet, script, font or
image reference — and structurally complete: every section present, every placeholder resolved
(an unresolved one fails the build). Launcher §9d also asks for a **visual** inspection before
the gate closes; that one is the operator's, and it is the only part of §9d this session cannot
perform itself.

## 10 · Acceptance — the half that is not automatable

- The gate's one measurement is landed, reproducible and quote-verified, and its zeros are
  licensed by controls that are demonstrated to be able to fail.
- Nothing here promotes a claim, adopts a prior number, or reads a comparator.
- `g2` inherits: the acquired alignment as substrate, the Xiong criteria as the recovery
  procedure, 6 open register items, and the standing instruction that **no region marked
  `NO_OPERATIONAL_BASIS` may be given a boundary later** (launcher §2).
- Two decisions remain the operator's and were not touched: whether this method becomes its own
  methods paper, and how any future RT1 concordance failure is interpreted.
