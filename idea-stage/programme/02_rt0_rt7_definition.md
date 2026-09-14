# Stage 2 · RT0-RT7 definition (general RT, focused on retron RTs)

## 0 · The point of this task

The literature names RT0–RT7 blocks in reverse transcriptases, but the boundaries trace
back to a single derivation made by inspection in 1990 and have been inherited ever since
without a stated criterion — so "we used the RT core" is not an operation another lab can
repeat. **We have built a reproducible definition; the field has not published one**, and
ours has never been validated on a frame that is independent of the conventions it audits.
Once this lands we can cut any RT — retron or not — at declared boundaries with a stated
uncertainty, report **per-block occupancy** per family, and separate *absent* from
*undetected* from *uninspectable*. That definition is the prerequisite for the tree, the
fusion analysis and every domain-completeness claim.

⚠️ **Corrected 2026-09-12.** An earlier draft of this section attributed to Toro 2026 a
claim about retrons lacking RT0. **No such claim exists in that paper** — the attribution
was inherited from a summary and never checked against the source. The superseded sentence
is not reprinted here so it cannot be found by search and re-used. See §0a for what the
paper actually says.

## 0a · ⛔ What Toro 2026 actually says — verified at the PDF, 2026-09-12

Extracted with `pdftotext -layout` from
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Toro 2026 bioRxiv - Landscape of retron diversity across SPIRE metagenomes, candidate type XI-like lineages (COMPETITOR).pdf`:

| check | result |
|---|---|
| occurrences of **`RT0`** | ⛔ **0 — the string does not appear in the paper** |
| occurrences of `RT1` | **3**, all as a span, none with a citation |

The three, verbatim:

> l.141 — *"conservation of the canonical RT1–RT7 motif core"*
> l.143 — *"displayed near-complete RT1–RT7 architecture"*
> l.153 — *"the resulting alignment was trimmed to the **203 positions** corresponding to
> the conserved RT1–RT7 motif core **by removing columns containing more than 50% gaps**"*

**Toro makes no claim about RT0.** This is an **absence of mention**, not a claim of
absence, and attributing a positive claim to an author who did not make it is exactly the
inheritance failure this project exists to document. ⚠️ The error entered from an operator
summary and was propagated without opening the primary source.

⭐ **The real finding is stronger and does not depend on anyone asserting anything:**

> The lineage that carried RT0 into the retron literature **silently dropped it**, and the
> word **"canonical"** is doing the work a citation should do. The span is then replaced by
> **203 columns produced by a >50%-gap filter** — a criterion about *alignability*, not a
> criterion about *the partition*.

That is a provenance result, and it is measurable. The deliverable is **not** "test Toro's
claim"; it is **"measure what is actually there N-terminal to RT1 in retron RTs, because
nobody has."**

## 0b · ⭐ D9 verified at primary source — and it makes the RT0 question malformed as usually posed

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Zimmerly Hausner Wu 2001 NAR - Phylogenetic relationships among group II intron ORFs (defines RT subdomain 0).pdf`,
p.1241, verbatim:

> *"Subdomains 0 and 2A are named in accordance with non-LTR RTs (7); **subdomain 0 is
> conserved only between group II intron and non-LTR RTs**"*

**Retrons are neither.** So *"do retrons have RT0?"* asks whether an object has a property
defined over a set that excludes it — you cannot measure occupancy of something undefined
for your sequences. The answerable question, and the one this stage asks:

> **Is there conserved structure N-terminal to RT1 in retron RTs, and does it correspond to
> anything in the group II intron / non-LTR RT0?**

⭐ **Consequence for inputs:** group II intron and non-LTR RT structures are not *extras
beyond the 25 crystals* — they are **the reference frame for the only element in
question.** We already hold **6AR1** (group II intron RT), and **5HHJ / 5HHK / 5HHL /
9D5X / 5G2X** are in the same directory with boundaries already extracted.

## 0c · ⭐⭐ The subdomain ↔ block correspondence, at primary source

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/A diversity of uncharacterized reverse transcriptases in bacteria .pdf`
(Simon & Zimmerly 2008), Introduction, **verbatim**:

> *"**RT domains 1–7 constitute the palm and finger domains** of the polymerase protein,
> and their sequences are generally alignable across RTs (21). In contrast, **domains 0 and
> 2a are shared among only a subset of RT classes** (22,23). Downstream of the RT domain is
> **domain X, which corresponds to the thumb** of the polymerase…"*

**This is the published mapping, and it must be reported, not assumed:**

| structural subdomain | conserved blocks |
|---|---|
| **fingers + palm** | **RT1 – RT7** |
| **thumb** | **domain X** — *not* an RT-numbered block |
| — | **RT0 and 2a**: present in only a subset of RT classes |

⛔ **So fingers/palm/thumb and RT0–RT7 are different partitions of the same protein, and
neither defines the other.** Crystal geometry **constrains** the blocks — RT7 should fall at
the palm/thumb boundary, and the catalytic aspartates fix RT3 and RT5 — but it **cannot
produce** a seven-way split. Stage 4 supplies constraints and an uncertainty interval.

⭐ **Report this as a deliverable, because downstream tasks need it.** Once a palm boundary
is called, the question *"is it where theory says it should be?"* is answerable only against
this mapping. The concordance table (§1) must therefore carry, per protein: the called
fingers/palm/thumb boundaries, the called RT1–RT7 blocks, and **whether each block falls in
the subdomain this mapping predicts** — with disagreements named, not averaged.

⭐ It also **independently corroborates `D9`**: Zimmerly 2001 says subdomain 0 is conserved
only between group II intron and non-LTR RTs; Simon & Zimmerly 2008 says domains 0 and 2a
are *"shared among only a subset of RT classes."* Two papers, same conclusion, and neither
is the retron literature.

## 0d · ⭐ The published transferability measurement — our direct comparator

Same paper, Results and Table (verbatim figures):

> *"retrons have fewer alignable characters than group II introns (**157 versus 177**), DGRs
> have about the same number (**179 versus 177**) and five other groups have fewer alignable
> characters (**126–167** amino acids)"* — computed **across RT domains 1–7**.

And the cross-class core:

> *"only **59 amino acids alignable** across the entire set"*, footnoted as
> *"the **59 characters in RT domains 3–5** that could be aligned across all RTs in this
> study."*

⭐⭐ **This is the only published measurement of how far the RT1–RT7 frame transfers, and it
is the thing our occupancy matrix supersedes.** It is per-class, it is on the same blocks,
and it says **retrons are the hard case** — 157 against group II's 177. Any occupancy result
must be reported against these numbers, and a per-class occupancy table with *n* per block
is strictly more informative than a single alignable-character count.

⚠️ Our register held only this paper's *"20 groupings"* claim
(`/home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/simon-zimmerly-rt-groupings.md`).
**The transferability numbers were never extracted** — the paper was on disk the whole time.

## 0e · ⭐ The primary derivation IS on disk — correcting my own error

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Origin and evolution of retroelements based upon their reverse transcriptase sequences. .pdf`
— Xiong & Eickbush, 2.3 MB. **I reported this absent on 2026-09-12; that was wrong.** I
searched by author; the papers here are named by **title**.

It carries the derivation itself:

    Fig. 1  "Amino acid sequence alignment of RT-related and RNA-directed RNA
             polymerase sequences"
            "...shown at the top of the alignment. See text for a description of the
             criteria used in this assignment."
            "The 42 conserved positions identified in this report..."
            "Alignment of residues between these fixed sites..."

⭐ **Note the phrase "See text for a description of the criteria used in this assignment."**
The usual story — *"delimited by eye, no criterion published"* — may be **false**. Read that
text before repeating it. Either way, **digitising Fig. 1 gives the columns actually cut**,
which converts the whole provenance chain from assertion into something measurable.

⚠️ **Also on disk and in the same chain:** `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Poch Sauvaget Delarue Tordo 1989 EMBO J - Identification of four conserved motifs among the RNA-dependent polymerase encoding elements.pdf`

⛔ **The wiki cannot find its own papers.**
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/papers/xiong1985_origin_evolution_retroelements.md`
records `doi: null`, `venue: "unknown"`, **year 1985 when the paper is 1990**, and **no local
path field at all**. A wiki node that cannot resolve to the PDF beside it is how a paper
gets declared missing. **Add a `local_path:` field to the paper schema.**

## 1 · What must be delivered

- An **operational definition** of each domain: the alignment columns or landmarks that
  define it, the rule that maps them onto a new sequence, and the failure mode when the
  rule cannot fire.
- **Per-domain occupancy** per RT family — the number the literature does not report.
  This is what turns "retrons lack RT0" into a measurement.
- **Boundaries with a stated uncertainty**, not a single coordinate.
- **What is N-terminal to RT1 in retron RTs** (§0b), reported with the trichotomy
  *absent* / *undetected (recoverable at low posterior)* / *uninspectable (contig-truncated,
  so it could not have been seen)*. The third class is what makes the first two real.
- ⭐ **A ruler figure** — every convention on one axis: Toro 2014's, Mestre's,
  Toro 2026's 203 gap-filtered columns, Simon & Zimmerly's per-class extents, and ours.
  `PE8` is **one row of this**, not a special case.
- Concordance against the **published span** and against the **crystal geometry** from
  stage 4.
- ⭐ **The subdomain ↔ block correspondence table** (§0c), per protein: called
  fingers/palm/thumb boundaries, called RT1–RT7 blocks, and whether each block falls where
  Simon & Zimmerly's mapping predicts. Downstream tasks need this to ask *"I found the palm
  — is it where it should be?"*
- **Alignable characters per class**, reported against Simon & Zimmerly's published
  **177 / 157 / 179 / 126–167** and their **59-character** cross-class core (§0d).

## 1a · ⭐ The inputs, in tiers — and the one rule that makes them non-circular

Four tiers, four **different roles**. The roles are the point: pooling them, or letting one
tier play two roles, is what produced every circularity in the previous attempt.

> ⛔ **The rule: the tier that DEFINES the frame must not be the tier you MEASURE on, and
> the tier that VALIDATES must not be inside the tier that defines.**

### Tier 0 — the frame. Structures. *Defines; never measured on.*

Because RT0 is defined *between* group II intron and non-LTR RTs (§0b), those are not
extras — they are the reference frame for the only element in question.

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/
      6AR1  group II intron RT (GsI-IIC)   <- ALREADY HELD, boundaries extracted
      5HHJ 5HHK 5HHL 9D5X 5G2X 7UIN 6ME0 ... 25 structures with
      fingers/palm/thumb + YXDD + DSSP already computed in
      /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/reference_boundaries.json

⛔ **Still to acquire:** a **non-LTR** RT (R2-type) — without it the RT0 question in §0b has
only one of its two reference classes. Optional but useful: telomerase TERT (the RT3a/IFD
correspondence) and a viral RT as outgroup.
⚠️ Structures **constrain** the partition; they do not produce it (§0c).

### Tier 1 — the anchors. Experimentally validated. *Validates; must be held out.*

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/anchors72.faa      72 — ⛔ NOT all structure-validated, see below
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/gold175_uniq.faa   171 unique of 175 (Khan panel)
    source of the Khan panel: /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/supporting_material/support.csv
      ⚠️ the protein is in `rt_protein_aa`, NOT `RT_sequence` (empty)

⛔⛔ **"72 structure-validated anchors" is wrong, and `D_instrument` says so itself.**
`FINDINGS.md` §5, verbatim: *"**Only 26 of the 72 anchors have a structure.** The other 46
cannot receive a structural transfer at all; their motif positions are **sequence-derived
only**. The '72 structure-validated anchors' are **26 structure-validated and 46
sequence-propagated**."* Its own self-adversarial check lists the phrase as one of three
inherited overstatements. **Say 26 + 46, never 72.**

⛔ **Unusable as validation in their current form.** `a1_seed_overlap.tsv`: `anchors72` is
**100% seed**, `gold175_uniq` is **25.7% seed**, and `a2` finds **42 of 63 "external"
producers in the seed**. **Split each into seed / held-out before anything is validated on
them**, and report the held-out n.
⚠️ The Khan panel also has **94.2% exact overlap with `mestre_1928`** — only 8 proteins lie
outside it — so it cannot externally validate anything in the Mestre/Toro lineage.

### Tier 2 — the comparators. Published conventions. *Compared against; never an input.*

    /home/borg/RETRON_CLAUDE_PART1/supplementary_material/toro_2014_Rt0-Rt7.FASTA   742 seqs
    Simon & Zimmerly 2008 per-class alignable characters: 177 / 157 / 179 / 126-167 (§0d)
    Toro 2026: 203 columns from a >50%-gap filter (§0a)
    Mestre 2020: the 1,928 reference set
    Xiong & Eickbush 1990 Fig. 1: the 42 conserved positions (§0e)

⭐ These are the rows of **the ruler figure** (§1). ⛔ **None of them may seed the frame** —
that is what makes the comparison mean something.

### Tier 3 — the population. The mining corpus. *Measured on; unconditional.*

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/retron.faa        78,287
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/nonretron.faa    423,274
    cut from the 501,561-sequence corpus chunks

⭐ **Why cut from the corpus chunks and not from `rt_proteins.faa` — the point that needed
explaining.** `rt_proteins.faa` holds **77,685** sequences and is **metagenome-depleted**:
recorded as trap T4, it is missing **602** sequences — **5.84% of metagenomic RTs and 0.00%
of isolate RTs**. Cutting from it would silently bias the population toward isolate genomes
(better-assembled, better-sampled, taxonomically skewed) and every occupancy number would
inherit that skew. Cutting from the corpus chunks gives the full **78,287** and removes the
trap entirely. **Two files differing by 602 sequences are not interchangeable**, and the
difference is not random.

⛔ **The residual circularity lives in this tier** (§2a): `family == 'Retron'` comes from the
corpus table, which came from PADLOC / DefenseFinder / myRT. One `hmmsearch` at
`full_RT ≥ 40 bits` closes it.

### Tier discipline — four rules

1. **Never pool tiers.** A number is on one tier, and the tier is named beside it.
2. **Membership is a hashed manifest**, enumerated and hashed — **never a glob**. Both known
   input failures (924,847; the ~12× `D6` discrepancy) came from implicit set construction.
3. **Tier 1 splits seed / held-out before it validates**, and the held-out n is reported.
4. ⚠️ **Measure the seed set's own bias.** The conservative seed (`partial == "00"` and not
   contig-adjacent) selects on *assembly quality*, which correlates with isolate-vs-MAG,
   which correlates with taxonomy and habitat. **Report the seed set's taxonomic composition
   against the full population** rather than assuming it is a random subset of RT diversity.

## 2 · Where this stands — 🟡 substantially **BUILT**, foundation unverified

⚠️ **Status downgraded 2026-09-12** from "substantially done". §3 says the step that makes
it publishable has never run; §5 says the load-bearing parameter's basis is `[CHOICE]`,
*"and not even ours"*; §8.6 says `D6`'s enrichments regenerate ~12× apart. Those cannot all
be true of something that is done.

### ⛔ The "72/72 concordance" figure does not mean what the summary says

Measured in `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/tables/a6_landmark_concordance.tsv`
(frame `RT17_CORE`, stratum `anchors72`, n = 72 anchor rows):

| motif | modal match state | concordance over truth-defined | n distinct states |
|---|---:|---:|---:|
| RT1 | 42 | **0.75** | 4 |
| RT2 | 87 | 0.9861 | 2 |
| **RT3** | **146** | **1.00** | **1** (modal residue `D`, 1.00) |
| RT4 | 193 | 0.9861 | 1 |

⛔ **"72/72" is the `n_anchor_rows` column — the sample size, not a concordance.** The
concordance column ranges **0.75 – 1.00 by motif**. Quoting "72/72 concordance" reports the
denominator as if it were the result.

### ⛔ And the 72 anchors are 100% seed-overlapping

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/tables/a1_seed_overlap.tsv`:

| stratum | n | exact seed members | % |
|---|---:|---:|---:|
| retron | 78,287 | 49 | 0.06% |
| nonretron | 423,274 | 97 | 0.02% |
| gold175_uniq | 171 | 44 | **25.7%** |
| **anchors72** | **72** | **72** | ⛔ **100.0%** |

**Every anchor is a seed.** So anchor concordance measures **internal consistency of the
frame**, not out-of-sample validity — and `a2_referee_externality.tsv` confirms the same
shape elsewhere: **42 of 63 "external" producers are in the `RT17_CORE` seed**, and 44 of
171 gold-panel members are too. ⚠️ **These belong beside the headline number, not in the
audit appendix.**

### What does hold

- `D1`: **a reproducible operational definition exists** — the landmark states above, with
  **99.91% held-out** and **214–441× above a positional null**, on frame `RT17_CORE`.
  ⚠️ Every one of those figures must carry **(frame, stratum, n)**; §8.3's own rule forbids
  quoting them bare, and this document did exactly that until 2026-09-12.
  ⭐ Still a **publishable methods contribution**, currently filed as infrastructure — but
  only once §2a is closed.
- `D4`: Toro's published span sits at ≈ **anchor −197 … +57**, with **80 verbatim
  matches**. Small, clean, unpublished, and buried in a fidelity check.
- `D2`: **RT1 fails its own declared ≥0.90 concordance bar (0.75, and 0.62 in the second
  frame)** — confirmed above at `a6`, where RT1 also scatters over **4 distinct match
  states** while RT3 sits on one. Xiong & Eickbush 1990 state that *"only domain 1 has not
  been independently confirmed."*
  ⚠️ **Wording corrected 2026-09-12:** our 0.75 is *concordance of our rule in 2026*; their
  caveat was about *evidence in 1990*. Different objects. Say **"independently recovers a
  weakness the founding authors flagged"** — **not** "replicates their caveat", which
  invites the question *which quantity was replicated?*
- `D9`: ⭐ **the RT0 void is EXPECTED.** Zimmerly, Hausner & Wu 2001 define RT0 as
  conserved *"only between group II intron and non-LTR RTs"* — **and retrons are
  neither.** This converts a derivation failure into a positioning statement.
- `D6`: ⛔ withdrawn — landmark enrichments are **224× / 445×**, not 2,657× / 4,936×, and
  Region X is **weak**, not `FAMILY_EXCLUSIVE`. Use the `*_REGEN*.tsv` outputs.

**Method documents:** `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X00_rt0_rt7_domain_derivation.md`,
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X12_landmark_register.md`. **Stages:** `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/` (+ its
audit `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/`), `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/`.

## 2a · ⭐ The circularity — half closed by the project itself, half open

**The profile-conditioning circularity was identified and fixed.** Verbatim from
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d1a_build_sets.py`:

> *"The circularity that voided the previous attempt: occupancy was measured on sequences
> **pre-selected for already matching the model**, so the profile reported the selection and
> not the population. This script therefore applies **EXACTLY ONE** selection criterion —
> `family == 'Retron'` / `family != 'Retron'` from the corpus table — and **no completeness,
> length, score or detection filter of any kind.**"*

Strata, unconditional: `retron` **78,287** (the population) · `nonretron` **423,274**
(outgroup, which separates retron-specific from RT-general occupancy) · `anchors72` and
`gold175` as **control strata explicitly not part of the population**.
⭐ It also avoids a known trap: the retron stratum is cut from the **501,561-sequence corpus
chunks**, not from `rt_proteins.faa`, which is metagenome-depleted (**602 missing, 5.84% of
metagenomic RTs, 0.00% of isolate**).

⛔ **What remains open, one level up.** The single criterion is `family == 'Retron'` **from
the corpus table** — and that label came from PADLOC / DefenseFinder / myRT, i.e. **the
detection conventions being audited**. So the *occupancy measurement* is unconditioned, but
the *stratification* is not. **The fix is already scoped and is one command:** validate the
`Retron` label corpus-wide at `full_RT ≥ 40 bits` (debate `D1b`, audit `B3`). It moves the
population under everything.

⛔ **And the frame itself is sequence-derived.** Match states come from an alignment, which
comes from a seed set. Structure is the only input not downstream of Xiong & Eickbush 1990.

⚠️⚠️ **But `D_instrument` already tested whether structure can carry that load, and the
answer constrains what stage 4 may promise.** `FINDINGS.md`, verbatim:

> *"The launcher names structure as **the adjudicator** of the A-vs-B boundary
> disagreement. **Structure cannot adjudicate a boundary, because it never set one.** That
> is not a shortfall in this session's work; it is what the provenance shows."*

**Read that precisely.** It is a statement about **provenance**, not about physics: the
published RT0–RT7 conventions were never derived from structure, so structure cannot
arbitrate *between* two conventions that both descend from sequence. It does **not** say
geometry is uninformative — §2b shows exactly how informative it is, and where it stops.

⛔ **The binding practical limit is the 26/72.** Only 26 anchors have a structure at all, so
a structure-first frame is built on 26 proteins and propagated to the rest by sequence —
which is the same transfer step, one layer down.

⚠️ **But do not over-promise what structure can do.** Fingers / palm / thumb are the three
subdomains of the RT fold; **RT0–RT7 are conserved blocks *within* fingers + palm.** Crystal
geometry can **constrain** the partition — RT7 should sit at the palm/thumb edge, and the
catalytic aspartates fix RT3 and RT5 — but it **cannot define** a seven-way split. Stage 4
supplies constraints and an uncertainty interval, not the answer.

## 2b · ⭐⭐ What structure CAN do here — measured, not asserted

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d2j_boundary_crossvalidation.py`
→ `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d2j_boundary_crossval.tsv`
cross-validates our derived match states against the crystals' **DSSP-derived
fingers / palm / thumb**, per structure, as a **Jaccard overlap**:

| structure | fingers | palm | thumb |
|---|---:|---:|---:|
| `5HHJ` | **0.7444** | 0.5182 | 0.2069 |
| `24NC` | **0.8390** | 0.5547 | **0.0000** |

⭐⭐ **This is the subdomain ↔ block correspondence, already measured** — the table §0c asks
for, sitting in `D_instrument`. And the gradient is exactly what Simon & Zimmerly predict:

> **RT1–RT7 = fingers + palm; the thumb is domain X, which is not an RT-numbered block.**

So fingers overlap strongly (**0.74–0.84**), palm moderately (**0.52–0.55**), and the thumb
**barely or not at all (0.00–0.21)** — because our RT-block frame is not supposed to reach
into the thumb. **Two independent lines agreeing: a 2008 statement about domain
architecture, and a 2026 Jaccard over crystals.** ⭐ This is the answer to *"I found the
palm — is it where it should be?"*, and it is quotable today.

### The structural gates `D_instrument` ran, and what they were for

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21a_extract_backbones.py
        extracts full-backbone chains  ⚠️ "the project's cached r4_chains are CA-ONLY;
        DSSP needs N, CA, C and O"
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21b_truncation_verdict.py
        ⭐ FALSIFICATION TEST 1, declared as a GATE: "is a structural negative at the
        N-terminus admissible?"  -> tables/d21b_per_chain_nterm.tsv
        ⭐⭐ This is the RT0 region. It is the closest thing on disk to an empirical test
           of whether N-terminal absence can be believed.
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d21c_sse_agreement.py
        ⭐ FALSIFICATION TEST 2: "do the two SSE algorithms agree well enough to set
        edges?" -- DSSP (H-bond energetics) vs P-SEA (CA geometry)
        -> tables/d21c_edge_disagreement.tsv, per-block start_delta / end_delta
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d2a_structural_core.py       the structural core in model-state coordinates
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d6a_retron_structural_core.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d2k_structural_rescue_pilot.py
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/run_esmfold.py               ⭐ ESMFold was run inside D_instrument
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d20a_capability_probe.py     what each method CAN define (§8.9)

⛔ **Read `d21b` and `d21c` before designing stage 4's contribution.** Both were declared as
gates *before* running, and both ask precisely the question stage 4 would otherwise ask
again from scratch.

⚠️ **Tool-version defect, recorded by the stage itself:** *"The foldseek build reports no
semantic version — only commit `d609cff8ca9250b9994a96207fb22a1585e7964e`, at
`/home/borg/foldseek/bin/foldseek` (2025-04-22). Tool identity is pinned; tool version is
`[UNVERIFIED]`."* ⛔ **And that is a THIRD foldseek install** — the others are
`/home/borg/miniconda3/envs/esmologs/bin/foldseek` and Ibex's
`foldseek/10-941cd33`. **Three builds, no agreed version. Pin one before any structural
comparison.**

## 3 · The one missing step

⛔ **Derive the boundaries from FULL-LENGTH proteins BEFORE building the HMM.** This is
recorded as the publishable route and has never been executed. The reason it matters:
a contig-edge-truncated CDS shifts the very boundary being defined, so the seed set must
be the conservative subset (`partial == "00"` **and** not contig-adjacent). Only after
boundaries exist can partial proteins be scored for domain presence — and many will turn
out domain-complete and rejoin on merit.

⛔ `PE8` — implement **Toro's convention exactly** (anchor −197 … +57) and ask whether the
published frame changes any surviving result. Never run.

## 4 · Prerequisites and gates

- **Stage 1**, for a full-length, completeness-flagged protein set.
- **Stage 4 should come first or merge.** The crystals already supply
  fingers/palm/thumb boundaries; RT0–RT7 landmarks should be anchored on that geometry
  rather than derived independently and reconciled afterwards.
- ⚠️ **Beyond bacterial RTs.** `D9` means that testing any RT0 claim **requires**
  structures outside the current 25 — group II intron, non-LTR, telomerase, viral RT. The
  25 crystals are a seed, not the population.

## 5 · Traps already paid for

- ⛔ **Never say "domain-based phylogeny."** The tree tips were a **341-aa tetrad window**,
  not the derived domain — Jaccard **0.736** against `B_coreflank`'s 0.912 (`D3`).
- ⛔ **The window cut is the load-bearing parameter**, and its basis is `[CHOICE]`, *"and
  not even ours"* (`X04`).
- ⚠️ **`E4`:** the tree session **built no HMM and re-derived no motif** — `B_coreflank`
  came from RETRON-DB_V3 and was used once as a comparator. The motif basis is a v3 result
  inherited unverified.

## 6 · Decisions for the operator

1. Whether the definition is published as its own methods paper (`D6` debate: *is
   `D_instrument` a paper of its own?*).
2. The inclusion rule for non-bacterial RT structures, written **before** any are added.
3. Whether RT1's failure is reported as a limitation or as the replication of Xiong &
   Eickbush's caveat. It is defensibly the latter, and that is the stronger paper.

---

## 7 · Refinements from `RETRON_RT_PROJECT_IDEAS.md` §3

## The per-family report table, made concrete

The ideas document specifies what to report per RT family, and it is more complete than the
existing record. Every column is computable once the boundaries exist:

    presence / absence of RT0-RT7      normalized position within the protein
    occupancy percentage               inter-motif distances
    start position                     sequence conservation
    end position                       consensus sequence
    length                             missing-block combinations
    insertions                         truncation frequency
    deletions                          core completeness

⭐ **"Missing-block combinations"** is the sharpest of these and appears nowhere in prior
work. It is what turns *"retrons lack RT0"* into a pattern: which blocks go missing
*together*, and does the co-absence follow lineage? `D9` predicts RT0's absence is
expected for retrons; this column tests whether other absences travel with it.

⚠️ **"Truncation frequency" must be read against the prodigal flag, not instead of it.**
`partial != "00"` is an assembly fact; a missing block is a biological one. Stage 1 carries
both, and conflating them is the error `decisions/0003` §4 exists to prevent.

## The comparison design

Compare **all bacterial RTs** vs **retron RTs** vs **major non-retron RT families**, and
ask whether retron RTs show a distinct conserved architecture.

⛔ **This requires stage I (the non-retron reference set), matched.** `x1_neighbourhood` is
the cautionary case: its fold only became interpretable once neighbour count was matched,
and the unmatched version would have supported the opposite conclusion.

## Open questions the record already partly answers

| ideas question | what is on record |
|---|---|
| *What is the accepted definition of RT0–RT7?* | ⚠️ **Unresolved, and softened 2026-09-12.** Xiong & Eickbush 1990 says *"See text for a description of the criteria used in this assignment"* (§0e) — so *"nobody ever stated a criterion"* may be false. **Read that text before repeating it.** What is certain: `D4` recovers Toro's span at ≈ anchor −197 … +57 from **80 verbatim matches**, so the convention is **unstated, not unreproducible** |
| *Which blocks are universally conserved?* | `s4_motifs`: **tetrad position 2 constrained in 40 of 40 families** |
| *Which are frequently absent?* | ⚠️ **Malformed as posed for RT0** (§0b): subdomain 0 is *defined* only between group II intron and non-LTR RTs, so it is undefined for retrons — not absent from them. ⛔ **Toro 2026 makes no RT0 claim** (§0a: 0 occurrences). Ask instead what is conserved N-terminal to RT1. For RT1–RT7 the question is well-posed and is what the occupancy table answers |
| *Are motif boundaries stable across families?* | `D1`: **99.91% held-out** on frame `RT17_CORE`. ⚠️ **"72/72" is the anchor sample size, not a concordance** (§2) — per-motif concordance on `anchors72` runs **0.75 (RT1) – 1.00 (RT3)**, and those anchors are **100% seed-overlapping**, so this is stability *within* the frame, not across families |
| *Which regions are most useful for phylogeny?* | ⛔ open, and it is stage 6's live question |

---

## 8 · EVERY PATH NEEDED TO VERIFY OR RE-DO THIS
**Verified by direct inspection 2026-09-11.** All paths absolute; counts measured.
⚠️ Every artifact below is `[UNVERIFIED]` under WA-I.3 — it enters a new row only as
`RE-DERIVED` or `BLIND-CONFIRMED`, at the point of use.

### 8.1 · The claims to be checked

From `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X00_rt0_rt7_domain_derivation.md`
(object `O5`) and `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/CLAIM_REGISTER.md`:

| claim | statement | where its number lives |
|---|---|---|
| `D1` | landmarks at match states **146 (RT3) / 229**, **99.91%** held-out, **214–441×** above a positional null — all on frame **`RT17_CORE`**. ⚠️ The **"72/72"** long quoted alongside these is the **`n_anchor_rows` sample size, not a concordance** (§2) | §8.4, and §2 for the correction |
| `D2` | **RT1 fails its own declared ≥0.90 bar (0.75 / 0.62)** — a *result*, replicating Xiong & Eickbush 1990's own caveat | §8.4 |
| `D4` | Toro's published span ≈ **anchor −197 … +57**, **80 verbatim matches** | §8.7 |
| `D6` | ⛔ **withdrawn** — enrichments are **224× / 445×**, not 2,657× / 4,936×; Region X is **weak** | §8.6 |
| `D9` | **the RT0 void is EXPECTED** — Zimmerly defines RT0 as conserved only between group II intron and non-LTR RTs, and retrons are neither | §8.10 |

### 8.2 · Input data — the published RT0–RT7 references

    /home/borg/RETRON_CLAUDE_PART1/supplementary_material/toro_2014_Rt0-Rt7.FASTA
        1.2 MB, 742 sequences  <- the published RT0-RT7 reference set. Root A only.

    /home/borg/RETRON_CLAUDE_PART1/supplementary_material/myRT-FastTree2.refpkg/
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/supporting_material/myRT-FastTree2.refpkg/
        CONTENTS.json  Mapping  phylo_modeldyadg_ia.json
        RVT-ref.hmm    RVT-ref.sto   RVT-ref.fst   RVT-ref.tre   RVT-ref.log
        ^ an HMM + its alignment + its tree + a mapping. The closest thing to a
          published, reusable RT profile available here. md5s are in CONTENTS.json.

    /home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/HMM/RVT-All.hmm
        myRT models, ~2,051 seeds / 47 families

⚠️ The two `myRT-FastTree2.refpkg` copies were **not** hash-compared. The four *other*
files shared between those two roots are byte-identical (verified in
`/home/borg/RETRON_STAGES/05_mestre_replication.md` §6.2) — do not assume this one is.

### 8.3 · Input data — our own protein sets, as actually used

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/aln/
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/d1c_per_seq_A_span17__retron.tsv.gz
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/d1c_per_seq_A_span17__nonretron.tsv.gz
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/d1c_per_seq_A_span17__anchors72.tsv.gz
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/d1c_per_seq_A_span17__gold175_uniq.tsv.gz
      ... and the same four for  _B_full__  and  _RT17_CORE__

⭐ **Three frames × four strata, and that grid IS the design.** `A_span17` (the 17-state
span), `B_full` (full-length) and `RT17_CORE` are **three different objects**; `retron`,
`nonretron`, `anchors72` and `gold175_uniq` are the four populations. ⛔ Any number quoted
without naming both the frame and the stratum is unattributable — this is exactly the
object confusion `crosscheck` found in §4.10.

### 8.4 · The main derivation arm — `D_instrument` (50 scripts, 92 tables)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/

| step | script | output table |
|---|---|---|
| build the strata | `scripts/d1a_build_sets.py` | `tables/d1a_strata.tsv` |
| align | `scripts/d1b_align.py` | `cache/aln/`, `cache/d1b_align.log` |
| **state occupancy** | `scripts/d1c_occupancy.py` | `tables/d1_state_occupancy.tsv`, `tables/d1c_stratum_summary.tsv` |
| A/B block mechanism | `scripts/d1d_ab_blocks.py`, `scripts/d1d2_block_mechanism.py` | `tables/d1d_block_disagreement.tsv`, `tables/d1d2_block_rebuild.tsv`, `tables/d1d_seed_geometry.tsv` |
| frame transfer provenance | `scripts/d1e_provenance.py` | `tables/d1e_domain_transfer_provenance.tsv` |
| dyad control | `scripts/d1f_dyad_control.py` | `tables/d1f_dyad_control.tsv`, `tables/d1f_dyad_per_anchor.tsv` |
| ⭐ **held-out + positional null** | `scripts/d1g_heldout_dyad.py` | `tables/d1g_heldout_dyad.tsv`, `tables/d1g_state_residue_null.tsv` ← **the 99.91% and the 214–441×** |
| ⭐ **subdomain verdict (`D2`)** | `scripts/d1h_subdomain_verdict.py` | `tables/d1h_subdomain_verdict.tsv`, `tables/d1h_motif_states.tsv` ← **RT1's 0.75 / 0.62** |
| frame criteria | `scripts/d1i_ab_recommendation.py` | `tables/d1i_frame_criteria.tsv` |
| dead states | `scripts/d1k_dead_states.py` | `tables/d1k_dead_runs.tsv`, `tables/d1k_differential_runs.tsv` |
| ⚠️ **conditioning bias** | `scripts/d1l_conditioning_bias.py` | `tables/d1l_conditioning_bias.tsv` ← read this before trusting any occupancy figure |
| **per-sequence boundaries** | (d1 chain) | `tables/d1_per_sequence_boundaries.tsv` ← **the deliverable: boundaries per protein** |
| structural core | `scripts/d2a_structural_core.py` | `tables/d2a_structural_core.tsv`, `tables/d2a_state_structure.tsv`, `tables/d2a_motif_vs_core.tsv` |
| completeness | `scripts/d2b_completeness.py` | `tables/d2_completeness.tsv` |
| referee + minimal unit | `scripts/d2c_referee_and_minimal_unit.py` | — |
| null + sensitivity | `scripts/d2d_null_and_sensitivity.py` | `tables/d2d_dyad_null.tsv`, `tables/d2d_threshold_sensitivity.tsv` |
| ⭐ **rule concordance** (n = 72 anchors; ⚠️ *not* a 72/72 score) | `scripts/d2f_rule_concordance.py` | `tables/d2f_rule_concordance.tsv` |
| input-set audit | `scripts/d2g_input_set_audit.py` | `tables/d2g_partial_semantics.tsv` |
| domain architecture | `scripts/d2i_domain_architecture.py` | `tables/d2i_domain_architecture.tsv`, `tables/d2i_domain_summary.tsv` |
| ⭐ **boundary cross-validation** | `scripts/d2j_boundary_crossvalidation.py` | `tables/d2j_boundary_crossval.tsv` |
| rescue | — | `tables/d2k_rescue_per_sequence.tsv` |
| ⭐ **method landscape** | `scripts/d20a_capability_probe.py`, `scripts/d20b_method_matrix.py`, `scripts/d20c_adversarial.py` | `tables/d20b_domain_methods.tsv` ← see §8.9 |
| crystal backbones | `scripts/d21a_extract_backbones.py` | `tables/d21a_residue_inventory.tsv` |
| truncation verdict | `scripts/d21b_truncation_verdict.py` | `tables/d21b_per_chain_nterm.tsv` |
| SSE agreement | `scripts/d21c_sse_agreement.py` | `tables/d21c_edge_disagreement.tsv` |
| retron core | — | `tables/d6a_retron_core.tsv`, `tables/d6a_core_by_function.tsv` |
| ESMFold metadata | — | `tables/d6_esmfold_metadata.tsv` (+ `_chunk0`, `_chunk1`) |
| clade purity / column provenance | — | `tables/d3d_clade_purity.tsv`, `tables/d3d_column_provenance.tsv` |
| depth / divergence sweeps | — | `tables/d7e_depth_sweep.tsv`, `tables/d7e_support_by_depth.tsv`, `tables/d7d_divergence_identity.tsv`, `tables/d7e_gradient.tsv`, `tables/d7e_rf_by_depth.tsv` |

**Method and rule documents in the same directory** — read before re-running anything:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/METHOD_RT_CORE_DETECTION.md   13.7 KB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/COMPLETENESS_RULES.md           9.3 KB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D_INHERIT.md                   27.9 KB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D2.0_METHOD_LANDSCAPE.md       13.0 KB
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/DECISION_REPORT.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/TRACK_D_REPORT.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/ADVERSARIAL_REVIEW.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D2_FINDINGS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D3_FINDINGS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D7_FINDINGS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D7_PREDICTIONS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/FINDINGS.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/STATUS.md

⭐ `D7_PREDICTIONS.md` is a **registered prediction file** — read it before scoring
anything, so predictions are not re-derived after seeing results.

### 8.5 · The audit arm — `d_instrument_audit` (7 scripts, 10 tables)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/

| audit | script | table | what it attacks |
|---|---|---|---|
| `a1` | `scripts/a1_seed_overlap.py` | `tables/a1_seed_overlap.tsv` | is the seed set independent of the test set? |
| ⭐ `a2` | `scripts/a2_referee_externality.py` | `tables/a2_referee_externality.tsv` | **is the "external" control actually external?** — one control's claim to externality **failed** |
| `a3` | `scripts/a3_raw_states.py` | `tables/a3_dyad_null.tsv`, `tables/a3_dyad_states.tsv`, `tables/a3_t5_conditioning.tsv` | the null, on raw states |
| `a4` | `scripts/a4_motif_order.py` | `tables/a4_motif_order.tsv`, `tables/a4_dyad_per_crystal.tsv` | motif order, per crystal |
| `a5` | `scripts/a5_frame_transfer.py` | `tables/a5_frame_transfer.tsv` | does the frame transfer survive? |
| ⭐ `a6` | `scripts/a6_landmark_concordance.py` | `tables/a6_landmark_concordance.tsv` | **the landmark concordance, independently** |
| `a7` | `scripts/a7_uncapped_tetrad.py` | `tables/a7_uncapped_tetrad.tsv` | the tetrad without its cap |

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/VERDICT.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/FINDINGS.md

⭐ The audit's own verdict is the strongest thing here: *"`D_instrument`'s instruments **can**
return another answer, and demonstrably did — RT1 scatters at 0.75 where RT3/RT5 hold at
1.00; the positional null returns a 0.23% background it could have returned at 100%."*
**That is a control that could have failed.** Reuse the design (stage C).

### 8.6 · The landmark register, and its ⛔ partial failure to regenerate

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X12_landmark_register.md
      object O3 span · findings G49-G52, and 🔴 G91

    Scripts (in /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/):
      s8d_regen_landmark_register.py
      s8e_regen_landmark_span.py

    Tables (in .../rt0_rt7_domain_test_v4_and_tree/tables/):
      s4v_landmark_register.tsv            <- ⛔ SUPERSEDED
      s4v_landmark_register_REGEN.tsv      <- ✅ USE THIS
      s4v_landmark_register_REGEN_span.tsv <- ✅ USE THIS (span frame)
      s4w_landmark_cooccurrence.tsv        <- ⛔ SUPERSEDED
      s4w_landmark_cooccurrence_REGEN.tsv  <- ✅ USE THIS

⛔ **`D6` is withdrawn** — but withdrawal is not diagnosis. The published enrichments
(2,657× / 4,936×) regenerate at **224× / 445×**: ratios of **11.9×** and **11.1×**.

> ⚠️ **A ~12× discrepancy between two runs of the same scripts on the same data is not a
> correction — it is a diagnosis nobody has done.** Until the cause is found, the `REGEN`
> numbers have **no more standing than the withdrawn ones**; "use the REGEN tables" is a
> convention, not a verdict.

⭐ **And it is the second input-set failure from implicit set construction** — the first was
the 924,847 denominator, from a directory glob that swept in the merged table. Two
independent failures of the same kind is **systemic**: fix it architecturally with a
**hashed set manifest** (enumerate and hash the members; never glob), not file by file.
Region X also drops from `FAMILY_EXCLUSIVE` to weak. ⚠️ `s8d`/`s8e` are also the scripts whose
directory-glob caused the 924,847 denominator error — **enumerate parts explicitly, never
glob a cache dir that also holds an aggregate file.**

### 8.7 · The Toro span fidelity arm (`D4`)

    Scripts:  /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/scripts/s5g_E3_fidelity.py   (✅ byte-identical)
    Tables:   .../tables/s5g_E3_fidelity.tsv          <- the 80 verbatim matches
              .../tables/s1c_toro_join.tsv
              .../tables/s1d_toro_arm_vs_dereplication.tsv
              .../tables/s7u_gateS_span_vs_full.tsv   <- span vs full-length, same instrument
              .../tables/s7v_concordance_span.tsv
    Method:   /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X07_toro_span_fidelity.md
              /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X03_anchor_selection.md
              /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X04_the_window_cut.md  ⭐🔴 the load-bearing parameter

⛔ `PE8` — *implement Toro's convention exactly (anchor −197 … +57) and ask whether the
published frame changes any surviving result* — **never run.** The inputs for it are all
above.

### 8.8 · The five `rt0_rt7_*` stages, and what is unique to each

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test/
        ASSESSMENT.md · D_INHERIT_RECONCILIATION.md · section3_bundle/
        scripts/s06_mestre_unit_reconciliation.py · scripts/s09_mestre_in_toro_frame.py
        tables/mestre_rt0_summary.tsv · tables/mestre_in_toro_frame_occupancy.tsv

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v2/
        instrument/ · MANIFEST.sha256 · README.md

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v3/
        ⭐ ASSET_REGISTRY.md · stratum3_hashes.txt · MANIFEST.sha256 · prereg/ · REPORT.md
        LAUNCHER_rt0_rt7_domain_test_v3.md   <- a prior launcher for this exact stage

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_paper/
        ⭐ PREREG_DIGEST.md · CLAIM_LEDGER_SCHEMA.md · INHERITANCE_LEDGER.md
        LITERATURE_INDEX.md · RERUN_LEDGER.md · EXPERIMENT_BASIS.md · AUDIT.md + audit/
        PAPER_STANDING.md · PREREG_PENDING.md · RECOMMENDATION_next_session.md

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/
        ⭐ METHOD_BASIS.md · LITERATURE_BASIS.md · SUPERSESSION.md · PROVENANCE.tsv
        MANIFEST.sha256 · INHERITANCE_LEDGER.md · prereg/ · OPEN_QUESTIONS.md
        RUNBOOK_esm_env.md · RUNBOOK_ibex_envs.md   <- how the envs were actually set up
        PAPER_SKELETON.md · MESTRE_EVIDENCE.md · TRACKER.md · SESSION_CLOSE.md

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_claim_ledger/
        ⭐ CLAIM_LEDGER.md · CLAIMS_WITHOUT_EVIDENCE.md · RETROSPECTIVE_PREREG.md
        FOR_A_STRANGER.md · EXPERIMENT_BRIEFS.md · PROPOSED_ANALYSES.md · MANIFEST.sha256

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_lit_and_narrative/
        LITERATURE_FOUNDATION.md · INSIGHTS_PER_PAPER.md · PAPER_TRAIL.md · PAPERS_READ.md
        PRIOR_ART.md · VERIFICATION_LOG.md · PROPOSED_METHOD_BASIS_RETAG.md · BACKGROUND.md

⭐ **Read `CLAIMS_WITHOUT_EVIDENCE.md` and `FOR_A_STRANGER.md` first** — the first names what
was asserted with nothing behind it, the second is written for exactly the reader this
section is for. ⭐ `SUPERSESSION.md` records which numbers replaced which.

⚠️ **`M_models` is NOT the RT0–RT7 arm**, despite `X00` naming it. Its scripts
(`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/scripts/m3b1_boundary_detection.py`, `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/scripts/m3b5_cmfinder_arms.py`,
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/scripts/m3b8_a1a2_boundary.py`, `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/M_models/scripts/m3g_archiveii_control.py`) are the
**ncRNA covariance-model / boundary** arm — `m3b1_boundary_detection.py`,
`m3b5_cmfinder_arms.py`, `m3b8_a1a2_boundary.py`, `m3g_archiveii_control.py`. They belong to
stages 10 and A. The only part relevant here is its **method landscape** thinking.

### 8.9 · ⭐⭐ The table that already answers this stage's first open question

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/tables/d20b_domain_methods.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D2.0_METHOD_LANDSCAPE.md

Columns: `id · method · output_unit · what_it_measures · what_it_needs · feasibility_here ·
tools_probed · max_scale_here · can_define_RT0 · circularity · what_it_CANNOT_do`

Rows include `DM1` profile-HMM state occupancy, `DM2` MSA column conservation / block
trimming, and more — each graded `VERIFIED` for feasibility, with **`can_define_RT0`** and
**`circularity`** as explicit columns.

⭐ **This is a method survey with a `what_it_CANNOT_do` column, and it is exactly what
stage 2 §7's question *"what is the accepted definition of RT0–RT7?"* needs.** It is also a
ready-made row set for **stage B (the object register)**, which is why `PE14` is cheaper
than it looks — part of it already exists.

### 8.10 · Literature claims (`D9`, `D2`, `D10`)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/zimmerly2001-rt-subdomains.md          <- D9: RT0 defined only between group II and non-LTR
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/xiong-eickbush-rt-tree-82-retroelements.md  <- D2: "only domain 1 has not been independently confirmed"
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/poch-1989-four-conserved-motifs.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/blocker-lambowitz-rt-domain-structure.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/simon-zimmerly-rt-groupings.md          <- D10: the [LIV] trap, position 2 not position 1
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/toro2014-bacterial-rts-17-classes.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/toro2018-type-iii-crispr-rt-groups.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/toro2026-corpus-and-yield.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/toro2026-hmms-seeded-from-mestre.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/toro2026-positioning-inherited.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V5/research-wiki/claims/toro2026-thresholds-midpoint-of-overlapping-distributions.md

    Narrative + provenance: /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_lit_and_narrative/LITERATURE_FOUNDATION.md
                            /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_paper/LITERATURE_INDEX.md
    Papers on disk:         /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/

⚠️ `D10` is a registered trap: **do not cite Simon & Zimmerly 2008 as licensing `[LIV]`** —
their *"nearly always hydrophobic"* is **position 2**, our excluded class differs at
**position 1**.

### 8.11 · Structures (shared with stage 4)

    Crystals (25, with boundaries already extracted):
      /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/
        boundary_extraction_report.txt · reference_boundaries.json · run_log.txt
    Predicted, full-length (O2):
      /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/
    Predicted, span-sliced (O6) — Ibex only:
      /ibex/project/c2366/RETRONS/rt0_rt7_domain_test_v4_and_tree/struct/span_pdb/   5,256 .pdb
    id -> sequence map (sha1-verified):
      /home/borg/RETRON_STRUCTURE_ID_MAP_2026-09-09.tsv

Full detail: `/home/borg/RETRON_STRUCTURAL_DATA_AND_METHODS_2026-09-09.md`.

### 8.12 · Reports to read, in order

    1. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X00_rt0_rt7_domain_derivation.md   the method + the claim
    2. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/METHOD_RT_CORE_DETECTION.md                        how the instrument works
    3. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D2.0_METHOD_LANDSCAPE.md                           what the alternatives were
    4. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/D7_PREDICTIONS.md                                  what was predicted BEFORE scoring
    5. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/VERDICT.md                                   the adversarial read - ⭐ start here if short on time
    6. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_claim_ledger/CLAIMS_WITHOUT_EVIDENCE.md                  what has nothing behind it
    7. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/SUPERSESSION.md                  which numbers replaced which
    8. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/experiments/X12_landmark_register.md             the G91 regeneration failure
    9. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/25_august_paper_positioning/CLAIM_REGISTER.md                                rows D1-D10, incl. ⛔ withdrawn D6
   10. /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/s1_review/VERDICT.md                                            §1's coordinate audit

### 8.13 · Recipe to re-do the cross-check

1. **Declare the frame and the stratum first.** §8.3 shows three frames × four strata.
   Pick one of each, name them in every table header, and do not mix.
2. **Re-derive occupancy** with
   `/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d1c_occupancy.py`
   → compare to `tables/d1_state_occupancy.tsv`. ⚠️ Read `tables/d1l_conditioning_bias.tsv`
   **before** trusting either.
3. **Re-derive the held-out figure and the positional null** (`d1g_heldout_dyad.py`).
   The claim to beat, **on frame `RT17_CORE`**: **99.91% held-out, 214–441× above the
   null** — and report the held-out **n** after the tier-1 seed/held-out split (§1a), because
   the anchors are currently 100% seed. ⭐ Confirm the null
   *could* have returned a different answer — it returns 0.23% where it could have
   returned 100%.
4. **Re-derive the subdomain verdict** (`d1h_subdomain_verdict.py`). Expect **RT1 to fail
   its own ≥0.90 bar**. Then read `xiong-eickbush-rt-tree-82-retroelements.md` and decide
   whether to report it as a limitation or as a **replication of the founding authors' own
   caveat**. It is defensibly the latter.
5. **Use only the `*_REGEN*` landmark tables** (§8.6). `D6` is withdrawn; the non-REGEN
   files reproduce withdrawn numbers.
6. ⛔ **Do the missing step: derive boundaries from FULL-LENGTH proteins, then build the
   HMM.** Seed from the conservative subset (`partial == "00"` **and** not contig-adjacent,
   from stage 1). Only then score partial proteins for domain presence.
7. **Run `PE8`** — Toro's convention exactly (§8.7). All inputs exist.
8. **Harvest `d20b_domain_methods.tsv` for stage B**, not for stage 2. It is a method/object
   survey with a `what_it_CANNOT_do` column and it is filed under the wrong stage.

---

## 9 · CONSOLIDATED INPUT PATH REGISTER
**Every input this stage needs, resolved to an absolute path and `test -e` verified
2026-09-12.** Variables in the source (`CORPUS`, `ANCHORS72`, `DEDUP`, `S2B`) are resolved
here to what they actually point at — several resolve into **V3, not V4**.

### 9.1 · Tier 3 — the population (measured on)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign/step4_scoring/cache/corpus/
        ^ CORPUS. 21 chunks, 501,561 sequences. ⚠️ lives in V3.
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/retron.faa       30 MB  · 78,287
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/nonretron.faa   173 MB  · 423,274
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage1_db_analysis/cache/systems_dedup.parquet
        ^ DEDUP

⛔ **Do NOT substitute `rt_proteins.faa`** (77,685, metagenome-depleted — trap T4: 602
missing, 5.84% of metagenomic RTs, 0.00% of isolate).
✅ **Located 2026-09-13:** `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/cache/neighborhood_annotation/rt_proteins.faa`
— **77,685 sequences exactly**. ⚠️ The data register names the **V5** tree; the file is in
**V3**. Fix the register. (A different object of the same name lives at
`/home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/x1_neighbourhood/cache/neighborhood_nonretron/rt_proteins.faa`
— the non-retron arm's RTs. Do not confuse them.)

### 9.2 · Tier 1 — the anchors (validate; must be split seed/held-out first)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage2b_assessor_redesign/anchors/anchor_set_v1.faa
        ^ ANCHORS72, the canonical source
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/anchors72.faa      34 KB · 72
        ⛔ 26 structure-validated + 46 sequence-propagated, NOT "72 structure-validated" (§1a)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/gold175.faa        74 KB · 175 rows
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/cache/sets/gold175_uniq.faa   73 KB · 171
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/supporting_material/support.csv
        ^ the Khan panel source. protein in `rt_protein_aa`, NOT `RT_sequence`

    Overlap evidence — read before using either as validation:
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/tables/a1_seed_overlap.tsv
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/d_instrument_audit/tables/a2_referee_externality.tsv

### 9.3 · Tier 0 — structures (define the frame; never measured on)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/
        25 structures incl. 6AR1 (group II intron RT), 5HHJ 5HHK 5HHL 9D5X 5G2X 7UIN 6ME0
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/reference_boundaries.json
        fingers/palm/thumb + YXDD + DSSP, per structure, already computed
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/boundary_extraction_report.txt
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/run_log.txt

    Predicted structures, if needed:
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/cache/fold/
    /home/borg/RETRON_STRUCTURE_ID_MAP_2026-09-09.tsv        9,965 structures -> sequence, sha1-verified

⭐ **Structure papers on disk that bear on the frame** — these were not previously listed:

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Domain structure and three-dimensional model of a group II intron-encoded reverse transcriptase.pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Structural basis for the evolution of a domesticated group II intron–like reverse transcriptase to function in host cell DNA repair .pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Compilation and analysis of group II intron insertions in bacterial genomes- evidence for retroelement behavior .pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Gapinska et al 2024 NAR - Structure-functional characterization of Lactococcus AbiA phage defense system.pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Garcia-Rodriguez Martinez-Abarca et al 2025 NAR - Phage helicases trigger type III-A3 retron-mediated anti-phage defense.pdf

⛔ **STILL TO ACQUIRE — a non-LTR RT (R2-type) structure.** Without it §0b has only one of
its two reference classes, and the RT0 question cannot be closed. `NEEDS_NETWORK`.

### 9.4 · Tier 2 — published comparators (never seed the frame)

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Origin and evolution of retroelements based upon their reverse transcriptase sequences. .pdf
        ^ Xiong & Eickbush. THE primary derivation. Fig. 1 alignment, 42 conserved positions,
          and "See text for a description of the criteria used in this assignment."
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Poch Sauvaget Delarue Tordo 1989 EMBO J - Identification of four conserved motifs among the RNA-dependent polymerase encoding elements.pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Zimmerly Hausner Wu 2001 NAR - Phylogenetic relationships among group II intron ORFs (defines RT subdomain 0).pdf
        ^ D9 at primary source, p.1241
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/A diversity of uncharacterized reverse transcriptases in bacteria .pdf
        ^ Simon & Zimmerly 2008. The subdomain<->block mapping (§0c) AND the
          transferability numbers 177/157/179/126-167 + the 59-character core (§0d)
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Systematic_predicion_2020.pdf
        ^ Mestre 2020
    /home/borg/RETRON_CLAUDE_PART1/supplementary_material/toro_2014_Rt0-Rt7.FASTA        742 sequences
    /home/borg/RETRON_CLAUDE_PART1/supplementary_material/Supplementary_mestre_Tree.nwk
    /home/borg/RETRON_CLAUDE_PART1/supplementary_material/myRT-FastTree2.refpkg/RVT-ref.hmm

    Toro 2026, and its supplementary:
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Toro 2026 bioRxiv - Landscape of retron diversity across SPIRE metagenomes, candidate type XI-like lineages (COMPETITOR).pdf
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/MELISSA_DATA/papers_Phylogeny/Landscape of retron diversity across the SPIRE prokaryotic metagenome resource reveals candidate novel type XI like lineages.pdf
    /home/borg/RETRON_CLAUDE_PART1/Toro_2026/SPIRE_retron_type_specific_HMMs.tar.gz
    /home/borg/RETRON_CLAUDE_PART1/Toro_2026/retron_reference_phylogeny_EPAng.newick
    /home/borg/RETRON_CLAUDE_PART1/Toro_2026/typeXI_local_tree.contree
    /home/borg/RETRON_CLAUDE_PART1/Toro_2026/spire_pipeline_scripts/

⚠️ **Two Toro 2026 PDFs, different md5** (`af0a0cca…` vs `9f8bceb2…`) — **identical extracted
text** (2,163 lines each, same line numbers, 3 × `RT1`, **0 × `RT0`** in both). Same bioRxiv
version (doi `10.64898/2026.05.14.725207`, posted 2026-05-14), re-downloaded. A **duplicate,
not two versions** — but hash before assuming that of any other pair.

### 9.5 · Environment

    /home/borg/miniconda3/envs/retron_tradicional/bin        ^ BIN in d1_common.py
    Ibex: module load esm/1.0.3 ; module load foldseek/10-941cd33
          export PATH=/ibex/user/rioszemm/conda-environments/<env>/bin:$PATH
    Runbooks recording how the envs were actually built:
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/RUNBOOK_esm_env.md
    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/rt0_rt7_domain_test_v4_and_tree/RUNBOOK_ibex_envs.md

### 9.6 · The source of truth for the constants

    /home/borg/RESEARCH-in-sleep-RETRON-DB_V4/ARIS_OUTPUT/D_instrument/scripts/d1_common.py
        V3, V4, S2B, CORPUS, DEDUP, ANCHORS72, BIN, MOTIFS, FROZEN

⭐ `FROZEN = {"corpus": 501_561, "retron": 78_287, "nonretron": 423_274, …}` is asserted in
code, so the strata are self-checking. `MOTIFS = ["RT1"…"RT7"]` — ⚠️ **RT0 is not in the
list**, which is itself consistent with §0b: the instrument never claimed to measure it.

### 9.7 · Gaps — what is NOT resolved

| gap | status |
|---|---|
| **non-LTR (R2-type) RT structure** | ⛔ absent; `NEEDS_NETWORK`; blocks §0b |
| `rt_proteins.faa` at the registered V5 path | ✅ **RESOLVED 2026-09-13 — the register named the wrong tree.** The file is in **V3**, not V5: `/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/ARIS_OUTPUT/stage3_phylogenetic_paper/cache/neighborhood_annotation/rt_proteins.faa`, **77,685 sequences exactly**. Fix the register entry |
| the wiki → PDF link | ⛔ **no `local_path:` field in the paper schema**; this is how Xiong & Eickbush was wrongly declared missing |
| `myRT-FastTree2.refpkg` in the two roots | ⚠️ never hash-compared |
| Toro 2026 S1–S3 tables as files | ⚠️ only the HMMs, newick and scripts are on disk |
| Xiong & Eickbush Fig. 1 digitised | ⛔ not done — the PDF is there, the columns are not extracted |
