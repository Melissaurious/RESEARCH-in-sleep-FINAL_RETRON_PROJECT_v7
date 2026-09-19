# Stage 3B — catalytic-site architecture · DESIGN DOSSIER

> **AMENDED 2026-09-18 by `EVIDENCE_REPAIR_2026-09-18.md`.** A bounded primary-literature repair
> added 9 structures and changed the retron evidence picture and the Tier B denominators. Sections
> 2.2, 5 and 11 below are superseded by that record where they disagree; everything else stands.

**Status:** design and input contract only. No catalogue-scale analysis was run. No detector was
built, tuned or frozen. No Stage 3A fingers/palm/thumb boundary was written or used. No launcher.

**Date:** 2026-09-18 · worktree `…_v7-asset-audit`, branch `prior-asset-audit`. No historical
directory was modified.

**Question this stage will ask**

> Can the catalytic site of bacterial reverse transcriptases be identified reproducibly from its
> three-dimensional catalytic-Asp architecture independently of a predefined YXDD-like sequence
> motif, and how conserved is that geometry across RT families despite variation in the local
> sequence motif?

**Files in this dossier**

| file | rows | what it is |
|---|---:|---|
| `STRUCTURE_REGISTER.tsv` | 51 | one row per RT protein chain, 30 fields |
| `REPLICATE_GROUPS.tsv` | 31 | one row per unique biological RT sequence |
| `TIER_ASSIGNMENT.tsv` | 20 | one row per 30 %-identity relatedness cluster, with tier |
| `CONTROLS.tsv` | 11 | the five required control classes plus four more that exist |
| `ANTICIRCULARITY_CONTRACT.tsv` | 25 | every input, allowed or forbidden, with the stage at which it becomes allowed |

Everything numeric below was **measured in this session** by parsing the coordinate files. Nothing
was inherited from the prior boundary table, from Gate S, or from any motif.

---

## 1 · Nonredundant experimental RT structure inventory

### 1.1 How the inventory was built, and why it is motif-free

72 distinct PDB accessions are on disk across the three caches identified in the prior asset audit.
Each file was parsed for: entity descriptions, `_struct_ref`/`_struct_ref_seq` (or `DBREF`) external
accessions and their construct↔parent spans, experimental method, resolution, every hetero ligand,
every nucleic-acid chain, author `_struct_site`/`SITE` records, and the primary `_citation`.

RT-bearing chains were identified from **entity description and external accession only** — metadata,
never sequence motif — and cross-checked against the landed v7 `structure_reference_inventory.tsv`.

**Catalytic-residue evidence was then derived from the structure itself, with no motif at any point**:

| evidence type | operational definition (declared here, before any detector exists) | strength |
|---|---|---|
| `METAL_CAT` | an Asp carboxylate O within **3.2 Å** of a Mg²⁺ or Mn²⁺ ion | hard |
| `SUBSTRATE_NT` | an Asp carboxylate O within **4.0 Å** of a bound dNTP/NTP or analogue | hard |
| `METAL_OTHER` | within 3.2 Å of K⁺/Na⁺/Zn²⁺/Ca²⁺ | supporting |
| `SUBSTRATE_NA` | within 4.0 Å of a nucleic-acid polymer chain | weak — tags any DNA/RNA-proximal Asp |
| `AUTHOR_SITE` | the residue appears in the deposition's own `_struct_site`/`SITE` record | a deposition claim, not a measurement |

Cryoprotectants, buffer components and modified residues (`MSE`, `GOL`, `PEG`, `1PE`, `SO4`, …) are
excluded from the substrate class by name. Without that filter, SeMet in `5HHK` and PEG in `8BGJ`
produce false substrate contacts — both were observed and removed.

### 1.2 Headline inventory

| quantity | value |
|---|---:|
| PDB accessions on disk | **72** |
| accessions carrying an RT protein chain | **50** |
| **RT protein chains registered** | **51** (`9Z6Z` contributes two distinct RTs, chains A and H) |
| **unique biological RT sequences** (≥ 90 % id, ≥ 70 % cov, single linkage) | **31** |
| relatedness clusters at 30 % id / 70 % cov | **20** |
| chains with an external accession (UniProt) | 39 / 51 |
| chains with **no** external accession — PDB self-reference only | **12** |
| chains where every Asp side chain is modelled | 44 / 51 |
| chains with a DOI for the primary paper | 38 / 51 |

**The biological unit is the sequence, not the entry.** The 51 chains collapse to 31 proteins. The
largest redundancy blocks are:

| group | n entries | one protein |
|---|---:|---|
| `RG02` `8C8J 8SXT 8UW3 9HDO 9K6G` | 5 | human LINE-1 ORF2p (≥ 98.7 % identical) |
| `RG01` `5HHJ 5HHK 5HHL 7UIM 7UIN` | 5 | group II intron maturase RT — **`5HHL` is 100 % identical to `7UIM`/`7UIN`, and `5HHJ` is 94.5 % identical to `5HHL`** |
| `RG03` `7V9U 7V9X 7XJG 8QBM` | 4 | retron Ec86 RT (P23070) |
| `RG04` `6ME0 6MEC 8FLI` | 3 | *Thermosynechococcus* maturase (Q8DMK2) — **`8FLI` is the same protein as `6ME0`/`6MEC`** |
| `RG05` `9L7P 9NNB 9VHE` | 3 | retron Ec78 / St85 RT (94.5–100 %) |
| `RG06` `23OR 9X94`, `RG07` `8UB7 8UBD`, `RG08` `9C0I 9LJE`, `RG09` `9D4S 9D5X`, `RG10` `9DOU 9NL3` | 2 each | one protein each, 100 % identical |

Four of these collapses were not recorded anywhere in the project before this session:
`5HHL ≡ 7UIN ≡ 7UIM`, `8FLI ≡ 6ME0 ≡ 6MEC`, `9C0I ≡ 9LJE`, `23OR ≡ 9X94`.

### 1.3 Construct → parent numbering, measured per chain

Every offset below was read from `_struct_ref_seq`/`DBREF` **in the file**, not inherited.

| chain | construct feature | measured offset |
|---|---|---|
| `9WY8_A` | **MBP fusion** — `P0AEX9` occupies entity 18–383; the RT is entity 384–962 with author numbering −14…564 | entity → author **+398** (independently reproduces the prior `c6` figure) |
| `9HDO_A` | **triple fusion** — SUMO `Q12306` 426–522 + MBP `P0AEX9` 46–409 + ORF2p `O00370` entity 523–1797 ↔ parent 1–1275 | entity → parent **+522** — *not recorded anywhere in this project before* |
| `26CZ_A` | SUMO tag, entity 13–108; RT entity 109–775 ↔ 1–667 | **+108** |
| `8OZ7_A` | expression tag occupies author ≤ 0; entity 1–730 ↔ author −101…628 | **+102** |
| `8C8J_A` | N-terminally truncated ORF2p construct, entity 1–824 ↔ parent 238–1061 | **−237** |
| `5VBS_A` | MMLV RT catalytic fragment, entity 24–278 ↔ Pol 683–937 | **+659** |
| `1RTD_A` | HIV-1 p66, entity 1–554 ↔ Pol 168–721 | **+167** |
| `9Z6Z_A` | entity 1–426 ↔ author 1–420 | 6-residue internal insert (recorded internal His6) |

**12 chains carry no external accession at all** (`7KFT_C 7UIN_D 8OZ7_A 9D4S_A 9D5X_A 9DOU_A 9LJE_A
9NL2_A 9NL3_A 9YFD_A 9Z6Z_A 9Z6Z_H`). For these, `sequence_mapping_exact = NO`: the deposited
sequence is the only parent available, and a claim about "the biological RT protein" cannot be made
beyond it. `7UIN` has no protein `DBREF` because it is the legacy-PDB copy; its mmCIF twin `7UIM`
does (`A0A173ZME3`), and the two are 100 % identical — so the mapping is recoverable by fetching
`7UIN`'s mmCIF.

---

## 2 · Tier A / B / C populations and denominators

### 2.1 The declared assignment rule — fixed before any detector exists

1. The split unit is the **30 % identity / 70 % coverage relatedness cluster**. A cluster is never
   split across Tier A and Tier B.
2. **Tier A (calibration)** = clusters containing ≥ 1 chain with a `HARD_PAIR`: two or more Asp
   residues supported by `METAL_CAT` and/or `SUBSTRATE_NT`.
3. **Tier B (held-out)** = clusters not in A containing ≥ 1 chain with `HARD_SINGLE` (one hard-evidence
   Asp) or `AUTHOR_PAIR` (two or more author-annotated Asp).
4. **Tier C** = everything else: comparators, plus RT clusters that currently have **no** independent
   catalytic truth.

The rule was written from evidence availability alone. It was not adjusted after seeing the result.

### 2.2 The result

| tier | clusters | unique sequences | chains | PDB entries | bacterial groups | non-LTR/viral groups |
|---|---:|---:|---:|---:|---:|---:|
| **A — calibration** | 10 | 18 | 31 | 31 | 12 | 6 |
| **B — held-out** | 2 → **3** | 3 → **4** | 7 → **17** | 7 → **17** | 3 → **4** | 0 |
| **C — no truth yet** | 8 → **7** | 10 → **9** | 13 → **12** | 13 → **12** | 10 → **9** | 0 |

*(arrows = after the 2026-09-18 evidence repair; see `EVIDENCE_REPAIR_2026-09-18.md` §5)*

Per-chain evidence classes across all 51: `HARD_PAIR` **16**, `HARD_SINGLE` 4, `AUTHOR_PAIR` 3,
`NONE` **28**.

**Tier A** (`C30_01 03 05 06 07 09 10 12 15 19`) covers group II intron / G2L / G2L4 / UG26 / UG8 /
UG15 / UG1 / DGR on the bacterial side and LINE-1 / R2Bm / R2Tg / R2Pm / HIV-1 on the outside.
Note that inside `C30_01` only `6AR1` carries a `HARD_PAIR`; `5HHJ`/`5HHK`/`5HHL` contribute
`AUTHOR_PAIR` and the remaining 7 chains have no independent truth and would receive it by
within-group transfer. That must be recorded as a dependency, not hidden.

**Tier B is two clusters and three unique sequences** — retron Ec86/Ec67 (`C30_02`, truth = a single
hard-evidence Asp, `7XJG` D198) and UG2/DRT2 (`C30_11`, two `HARD_SINGLE` chains). That is a real
held-out set, but a small one.

**Tier C (`C30_04 08 13 14 16 17 18 20`) is entirely bacterial and contains five of the six retron
clusters**, plus AbiK, AbiP2, AbiA, UG28, DRT6 and Drt3a.

### 2.3 Tier C comparators that already exist

* motif-positive non-RT proteins — see `CONTROLS.tsv` `C3` (4 unique proteins);
* RT chains with several YXDD-like candidates — `C4` (13 of 51 chains);
* distant RT classes — non-LTR (LINE-1, R2Bm, R2Tg, R2Pm) and viral (HIV-1, MMLV), 6 groups. These
  were believed absent locally until the prior asset audit found them;
* multiple structural states of one RT — `C5` (10 groups, 33 chains).

**Predicted structures appear nowhere in Tier A, B or C.** The 8,765 ESMFold models registered in the
prior audit are downstream application material only, after the detector has been validated on
experimental structures.

---

## 3 · Primary-literature catalytic evidence status

A **targeted** check only, as instructed. No broad review was performed.

**What is established, per structure, without leaving the deposition:** primary-paper title, journal,
year, DOI and PubMed ID for **38 of 51** chains (all mmCIF-sourced); author `_struct_site` catalytic
annotation for 4 chains (`5HHJ`, `5HHK`, `5HHL`, `1RTD`); bound metal identity and coordination
distance; bound substrate identity and contact distance; construct numbering and tag composition.

**What is NOT established and must not be claimed:** what the primary paper's *text* asserts about
catalytic residues, mutational support, or motif terminology. This session had no network access, and
only five literature PDFs are on disk (`Xiong & Eickbush 1990`, `Blocker 2005`, `Poch 1989`,
`Simon & Zimmerly 2008`, `Zimmerly 2001`) — none of them a structural paper for any entry here.

Consequently the register's `literature_supported_catalytic_residues` field is **deliberately empty**,
and every truth label currently in the dossier is one of: `METAL_CAT`, `SUBSTRATE_NT`, `AUTHOR_SITE`.
That is a defensible position — those are measurements or deposition claims, not inference — but it
is not the same as literature truth, and the difference is recorded rather than papered over.

**Eligibility, as recorded in the register.** 16 chains are `ELIGIBLE` (independent catalytic
evidence, resolution within the proposed 3.5 Å cut, external accession, carboxylate geometry
resolvable); 7 are `ELIGIBLE_WITH_CAVEAT` (one or more of: no external accession, or evidence from a
single residue); **28 are `NOT_SCOREABLE_AS_TRUTH`** — they carry no independent catalytic evidence of
their own and must either inherit truth from a replicate-group partner, with that inheritance flagged,
or wait for literature. Every caveat and exclusion reason is written out per chain in
`exclusion_or_caveat_reason`.

**13 entries have no DOI** in the local copy (`26CZ 5HHK 5VBS 6MEC 7UIN 7V9X 7XJG 8FLI 8QBM 8UBD 9LJE
9VHE 9X94`) because the local copy is legacy PDB format. Fetching their mmCIF closes this; it is
minutes of work, not a research task.

**The evidence that matters most is missing for exactly the lineage the secondary question is about.**
See §11.

---

## 4 · Candidate calibration / validation split

| quantity | value |
|---|---:|
| unique biological RT sequences | **31** |
| replicate PDB entries per sequence | median 1, max 5 (`RG01`, `RG02`) |
| sequences represented by ≥ 2 entries | 10 |
| relatedness clusters at 90 / 70 / 50 / 30 / 20 % identity | 31 / 31 / 29 / **20** / 7 |
| family–class coverage | ~19 distinct RT classes, metadata only |
| Tier A : Tier B unique sequences | **18 : 3** |

**Cluster structure under plausible thresholds.** Identity thresholds from 90 % down to 70 % give the
same 31 clusters — the redundancy in this set is near-duplicate, not graded. Structure only begins to
change at 50 % (29) and 30 % (20). At 20 % everything collapses into one component of 42, which is the
expected behaviour of a homologous superfamily and is why **20 % is not usable as a split threshold**.
30 % is the loosest threshold at which the set still has internal structure; it is proposed on that
ground, and **not** because it improves any result — no result exists yet.

**The cost of the 30 % threshold, stated plainly.** `C30_01` merges five replicate groups into one
cluster: the Roseburia/E. rectale maturase RTs, the *Thermosynechococcus* maturase, LtrA, GsI-IIC and
the CRISPR-associated Cas6-RT-Cas1. All 11 chains therefore sit on the same side of the split. That is
correct behaviour — they are genuinely related — but it removes the group II intron lineage from the
held-out set entirely.

**Is the set large and diverse enough for a genuine held-out validation?**

**Not for a general claim.** 3 unique held-out sequences in 2 clusters, with truth resting on single
hard-evidence residues, supports a *bounded* statement about transfer to two specific lineages. It
does not support "a transferable structural catalytic-site detector for bacterial RTs". This should be
stated in the launcher as a pre-registered expectation of **PARTIAL**, so that a PASS verdict requires
the held-out set to be enlarged first rather than the criterion to be relaxed.

**Two honest ways to enlarge Tier B**, both of which are new work, not reinterpretation:

1. establish literature truth for the Tier C clusters (retrons, AbiK/AbiP2/AbiA, UG28, DRT6, Drt3a) —
   8 clusters, 13 chains, targeted reading of ~10 primary papers;
2. acquire catalytic-state structures (metal + incoming nucleotide) for bacterial defence RTs, if any
   have been deposited since these caches were built.

---

## 5 · Available positive / negative / comparator controls

All five required controls exist. Four more were found. Full detail in `CONTROLS.tsv`.

| # | control | availability | adequacy |
|---|---|---|---|
| 1 | true experimental catalytic sites | 16 chains with a hard-evidence Asp pair, 23 with any | **adequate for calibration, thin for held-out** |
| 2 | within-RT alternative Asp-pair decoys | **113 decoy pairs** ≤ 6 Å across 51 chains (median 2/chain, max 5) | **adequate — the richest negative class** |
| 3 | motif-positive non-RT proteins | I-SceI `FMDD@142` (4 entries), I-HjeMI `YSDD@113`, AAA ATPase `YGDD@328`, TIGR02646 `YNDD@107` | **thin — 4 unique proteins** |
| 4 | RT chains with several YXDD-like candidates | **13 of 51**; measured first-match failures at `8BGJ` (true site is the *second* match, `FCDD@152` → D154) and `8OZ7` (true site is the *second* match, `YVDD@238` → D240/241) | adequate |
| 5 | replicate structural states of one RT | 10 groups, 33 chains, including `9D5X` apo vs `9D4S` substrate-bound — same protein, same answer | adequate |

Two controls found that were not asked for, and are the sharpest in the set:

* **`1RTD` chain B — HIV-1 RT p51.** The same polypeptide as p66, carrying `YMDD@183`, in a
  conformation with no functional polymerase site. Sequence held exactly constant, geometry changed,
  expected verdict changed. This is the single cleanest test of the stage's own question.
* **`1RTD` chain A — the RNase H site as a within-protein comparator.** D443/D498/D549 form a genuine
  second carboxylate-metal catalytic centre, and `443–498 = 3.02 Å` **outranks** the polymerase pair
  `110–186 = 2.97 Å`… by a margin of 0.05 Å. Per the stage instruction, this is an **evolutionary
  comparator of homologous chemistry, not a negative**: a detector that fires on it has found a real
  active site of the wrong kind, which is a different outcome from a false positive and must be
  reported separately.

**Apo requirement.** 9 chains are apo with no nucleic acid (`5HHJ 5HHK 5HHL 7KFT 7R08 9D5X 9WY8 24NC
9YFD`). `9D5X` (apo) and `9D4S` (substrate-bound) are the same protein and yield the **same** tightest
Asp pair, 145–240 at 2.70 Å and 2.71 Å. That is the existence proof that metal-free detection is
possible, and it is why metal presence is validation evidence and never a detector input.

---

## 6 · The anti-circularity contract

The machine-checkable form is `ANTICIRCULARITY_CONTRACT.tsv` (25 rows). In summary:

**Forbidden as candidate-selection input, at every point before the detector is frozen:** YXDD/YADD/
YIDD/YMDD motif coordinates; `[YFWH].DD`, `[LIV].DD` or any successor regex; RT5 / RT0–RT7 / HMM state
coordinates; `CAT_STATE` 262 or any `rtmap` state; palm / fingers / thumb boundaries from any source;
family or class labels; previous Gate S verdicts or the Gate S criterion; expected normalised position
of the site; the prior `reference_boundaries.*` files; `s6b_gateS_LDD.py`; any Tier B structure or its
label; any threshold refit after Tier B has been scored.

**Forbidden as input but allowed as validation evidence or truth label:** bound Mg/Mn positions; bound
dNTP/template/primer positions; author `_struct_site` annotation. These *define* truth; they cannot
also *select* candidates, or the detector becomes undefined on the 9 apo structures.

**Allowed as detector input:** carboxylate coordinates; all-atom coordinates of the chain; pairwise and
n-body geometry (distances, angles, dispersion, coplanarity); solvent accessibility; secondary
structure **computed de novo from the candidate structure**, never read from a prior DSSP table; local
packing context within a declared radius; chain length and Asp/Glu census.

**One input needs an explicit rule because it sits on the boundary.** Sequence separation between the
two candidate residues, `|i − j|`, is an intrinsic property of the candidate, not an external prior —
so it is allowed. But the admissible range must be **calibrated on Tier A only and frozen before Tier B
is opened**. The measured Tier A separations are tightly clustered (Ec86 78, Eco8 93, `5HHJ` 88,
`6AR1` 85, LINE-1 102, `24NC` 91, `9D4S` 94, `9YFD` 112), and that consistency is precisely why
refitting it on the validation set would be circular.

**Comparison against the motif happens once, after the freeze**, and is reported as agreement and
disagreement, both — never used to repair the detector.

---

## 7 · Proposed detector inputs — and what the data says about them

Per the instruction, **no algorithm is imposed here**. What follows is a feature-availability report.

### 7.1 The candidate space is small and tractable

| quantity | value |
|---|---:|
| Asp residues per RT chain | median 23, range 8–76 |
| Asp–Asp carboxylate pairs ≤ 8 Å with \|i−j\| ≥ 5 | median 3, range 1–18 |
| **Asp–Asp carboxylate pairs ≤ 6 Å** | **median 2, range 0–6; 131 total across 51 chains** |
| Asp–Asp pairs ≤ 4 Å | median 1, range 0–5 |
| Asp **triplets** all-pairs ≤ 8 Å | **0 in 44 of 51 chains** |

The last row is the most important structural fact in this dossier. **The canonical catalytic Asp
network is not an equilateral triplet.** The motif-C Asp–Asp pair is ~2.9–3.5 Å apart and the motif-A
Asp sits 2.5–5.0 Å from one of them, so a 3-clique under a uniform 8 Å carboxylate criterion usually
does not form. A detector built on "compact Asp triplet" would abstain almost everywhere. The object
is an **asymmetric network**, and it must be modelled as one.

### 7.2 Measured geometry of true sites

Where two or three catalytic Asp are independently supported, their carboxylate separations are:

`24NC` 149–240 **3.05**, 149–241 **2.96**, 240–241 **3.49** · `9D4S` 145–239 **2.75**, 145–240 **2.71**,
239–240 **3.01** · `9YFD` 212–324 **2.89**, 212–325 **2.88**, 324–325 **2.90** · `6AR1` 138–223 **2.71**
· `8C8J` 600–702 **2.88** · `9HDO` 600–702 **2.98** · `9NL2` 506–606 **2.51** · `9DOU` 777–878 **3.15**
· `8GH6` 529–628 **3.56** · `8UB7` 138–215 **3.03** · `1RTD` 110–185 **3.24** · `8BGJ` 73–154 **4.23**
· `26CZ` 182–278 **4.44** · `5HHJ`/`5HHK` 151–239 **4.60** (apo) · `5HHL` 139–227 **4.95** (apo).

**Metal-bound sites: 2.5–3.6 Å. Apo sites: 4.2–5.0 Å.** The conformational-state effect is real,
measurable, and about 1.5 Å. A single fixed distance cut-off cannot serve both states.

### 7.3 Is the true site the *tightest* pair? Often, but not reliably

Among the 18 chains where a catalytic pair is independently supported and resolvable at ≤ 6 Å, the true
pair ranks **1st in 12, 2nd in 5, 3rd in 1**.

Failures are systematic and informative:

* `9NL3` (R2Tg), `9DOU` (R2Tg), `9NL2` (R2Pm), `8GH6` (R2Bm), `8SXT`/`9K6G` (LINE-1) — large
  multi-domain retroelement ORFs where an accessory-domain Asp pair (e.g. `1275–1288`, `1054–1067`,
  `996–1009`) is tighter than the polymerase site;
* `1RTD` — the RNase H site, by 0.05 Å;
* `6MEC`/`8FLI` versus `6ME0` — the **same protein** in different states, where the rank changes.

Per-replicate-group agreement of a naive top-1 rule: perfect in `RG03` (Ec86, 4 entries), `RG05`
(Ec78/St85, 3), `RG06` (Eco8, 2), `RG07` (DGR, 2), `RG08` (UG2, 2), `RG09` (G2L4, apo + bound); broken
in `RG01` (1 of 5), `RG02` (3 of 5), `RG04` (2 of 3), `RG10` (2 of 2).

**Read plainly: geometry alone reduces the candidate space to 1–6 pairs per chain but does not
uniquely identify the catalytic site by any single distance criterion, and it fails preferentially on
large multi-domain RTs.** That is the honest prior going into Stage 3B, and it is what makes the
FAIL branch of the gate a live possibility rather than a formality.

### 7.4 Features available and worth testing, with no commitment to any

Carboxylate coordinates and pairwise distances · the asymmetric three-residue geometry (two tight +
one at 2.5–5 Å) · `|i−j|` sequence separation, calibrated on Tier A only · burial and solvent
accessibility · de-novo secondary structure at the candidate · local packing composition · number and
identity of nearby basic residues · conformational state, treated as a stratum rather than a covariate
· resolution, treated as an eligibility criterion, not a weight.

**Resolution floor.** `5G2X` at 3.80 Å yields **zero** Asp carboxylate pairs ≤ 6 Å — side chains are
not placed. `6ME0`/`6MEC` (3.60 Å) and `8FLI` (3.80 Å) yield pairs but disagree with one another on the
same protein. An eligibility cut on resolution must be **declared before scoring** and must not be
moved afterwards.

---

## 8 · Proposed PASS / PARTIAL / FAIL logic — designed, not optimised

No thresholds are proposed here, deliberately. What is proposed is the **shape** of the verdict, so
that the launcher declares its numbers before it runs.

**Three outcomes are reported separately and never merged.**

| outcome | meaning |
|---|---|
| **hit** | the detector's top-ranked site matches the truth label |
| **miss** | the detector returns a site, and it is the wrong one |
| **abstain** | the detector declines to return a site (no candidate clears its own criterion) |

**Abstention is reported as its own quantity with its own denominator, never folded into failure.**
An abstention on a 3.8 Å apo structure is an honest statement about the instrument; a miss is a claim
that was wrong. They are different results.

| verdict | shape of the condition |
|---|---|
| **PASS** — transferable | on **held-out clusters not used in calibration**, the hit rate among non-abstaining chains meets a pre-declared bar, the abstention rate is below a pre-declared bar, **and** the detector does not fire on the motif-positive non-RT controls above a pre-declared rate. Requires the held-out set to be larger than it is today. |
| **PARTIAL** — bounded scope | the above holds **within a named, pre-declared RT scope** (for example, single-domain bacterial RTs) and demonstrably fails or abstains outside it. The scope must be named **before** scoring, not carved out afterwards. |
| **FAIL** | geometry alone cannot separate the true site from within-protein decoys at the pre-declared bar on held-out clusters. The reportable conclusion is then that **a combined sequence + structure instrument is required** — which is a result, not a shortfall. |

**Conditions that must be fixed in the launcher before any scoring:** the hit and abstention bars; the
resolution eligibility cut; the `|i−j|` range calibrated on Tier A; the rule for scoring a chain whose
truth comes by within-group transfer rather than from its own evidence; and the rule that the RNase H
site in `1RTD` counts as a **third outcome** (`homologous-chemistry hit`), not a false positive.

**Reporting discipline inherited from Stage 2 and carried forward:** every rate carries its own
denominator; retron, group II intron, non-LTR and viral strata are reported separately and never
pooled; no accuracy, sensitivity, precision or F1 is computed against a tool label or a motif call.

---

## 9 · Existing compute and assets that are reusable

| asset | reuse | condition |
|---|---|---|
| **72 experimental structures across three caches** | **GREEN — reuse, no re-download** | hash the 25-file stage2b cache (open from the prior audit) |
| **`a1_fetch_log.tsv`** — 325 logged RCSB fetches with sha256 | **GREEN** | adopt as the acquisition pattern for anything new |
| **`c2_resmap.tsv`** — struct↔entity residue map for 26 anchor chains, frame-validated at ≥ 90 % | **GREEN** | — |
| **`d21b_per_chain_nterm.tsv`** — construct/modelled/offset per chain | **GREEN** | independently reproduced for `9WY8` (+398) this session |
| **`c2_dyad_env.tsv`** — 99 measured Asp-carboxylate contacts in entity coordinates | **GREEN as a cross-check** | its dyad calls flagged `column_resolved` are alignment-derived and must not enter truth |
| **`c1_answer_key.tsv`** — the multi-occurrence ambiguity policy | **GREEN as method** | its residue calls are motif-derived and are forbidden as truth |
| `c2_foldseek_aln` / `c2_struct_pairs` / `c2_pair_summary` | **AMBER** | pin foldseek `10.941cd33`; only needed if structural superposition is used |
| DSSP cache for 26 chains | **RECOMPUTE** | seconds of work, and the contract requires de-novo computation anyway |
| Gate S (`s6d_gateS_f14_exact.py`) | **comparator only, after the freeze** | never truth, never an input |
| `reference_boundaries.*`, `s6b_gateS_LDD.py`, palm/fingers/thumb tables | **FORBIDDEN** | graded RED in the prior asset audit |
| 8,765 ESMFold models | **downstream application only** | after experimental validation; 42 over-length models excluded |

**What this session already computed and does not need repeating:** the 51-chain register with
offsets and hashes; the per-Asp metal/substrate/author evidence for every chain; the 131-pair
candidate space; the 31-sequence replicate grouping and the 20-cluster relatedness structure; the
control inventory. All of it is in the five files listed at the top and all of it is re-derivable in
under a minute of CPU.

---

## 10 · Minimum new computation actually required

Nothing here is catalogue-scale and nothing needs a GPU.

1. **Fetch mmCIF for the 11 legacy-PDB entries** (`5HHK 5VBS 6MEC 7UIN 7V9X 7XJG 8FLI 8QBM 8UBD 9VHE
   9X94`) — recovers DOIs, `_struct_ref` accessions for `7UIN`, and author `_struct_site` records.
   Minutes, using the logged fetch pattern.
2. **Hash the stage2b cif cache** and re-verify each accession against its in-file identity, as was
   done for the 25 in the prior audit.
3. **Targeted primary-literature read for the Tier C clusters** — ~10 papers, to establish whether
   catalytic residues for the retron, Abi, UG28, DRT6 and Drt3a RTs are explicitly supported. This is
   the only step that can move Tier C into Tier B.
4. **Freeze the truth table** as a landed artifact, one row per chain, with the evidence type on every
   residue and an explicit `TRANSFERRED_WITHIN_REPLICATE_GROUP` flag where truth is inherited.
5. **Declare the thresholds** — resolution cut, `|i−j|` range from Tier A, hit and abstention bars —
   and land them **before** any detector is run.
6. Only then: build and freeze the detector on Tier A, and open Tier B once.

---

## 11 · Blocking evidence gap

**One gap is blocking, and it is specific.**

> **PARTLY REPAIRED 2026-09-18.** Three of the six retron groups now carry independent truth
"
> (Ec86 `HARD_SINGLE`, Eco8 `FUNCTIONAL_PAIR`, Ec67 `HARD_MULTISITE_UNRESOLVED`), and the secondary
"
> question moves from BLOCKED to EXPLORATORY. The statement below still holds as written:
>
> **No retron RT structure on disk is in a catalytic state.** Of the 6 retron replicate groups
> (`RG03` Ec86, `RG05` Ec78/St85, `RG06` Eco8, `RG23` Ec83, `RG24` Ec67, `RG26` 9N69), **zero** have an
> RT chain with a catalytic Mg²⁺/Mn²⁺ ion **and** a bound incoming nucleotide at the active site.
> Exactly one chain in the whole retron set carries any hard structural evidence at all — `7XJG`
> D198, a single residue.

The deposited retron structures are effector complexes, msDNA/msr product complexes and apo forms.
That is a property of the field's deposition history, not of these caches.

**Consequences, stated before any work begins:**

* the **primary** question — can the catalytic site be found from geometry alone — is answerable, on
  Tier A, with 16 hard-evidence chains spanning group II intron, G2L, G2L4, DGR, UG1, UG8, UG15, UG26,
  non-LTR and viral RTs;
* the **secondary** question — how retron RTs compare with other bacterial RT families in catalytic
  sequence and geometry — **cannot currently be answered against independent truth**. Retron catalytic
  residues would have to come from literature or by homology transfer, and homology transfer is
  precisely what the stage is trying to avoid depending on;
* the geometry is nonetheless *present* and internally consistent in retron RTs — `RG03` gives
  119–198 at 2.68 / 2.71 / 2.90 Å across four independent entries, `RG05` gives 96–188 at 3.05 / 3.11 Å,
  `RG06` gives 107–200/201 at 2.62 / 2.76 Å. **What is missing is the independent evidence, not the
  signal.**

**Three secondary gaps**, none blocking: the motif-positive non-RT control pool is 4 unique proteins,
which supports a qualitative specificity statement but not a specificity *rate*; 12 chains have no
external accession, so "the biological RT protein" for them is the deposited construct and nothing
more; and Tier B is 3 unique sequences, which supports a bounded transfer claim and not a general one.

---

## 12 · Recommendation

Proceed to a Stage 3B launcher, with three things written into it before anything runs:

1. **the expectation of PARTIAL**, on the evidence above — PASS should require enlarging Tier B first,
   not relaxing a bar;
2. **the retron gap named as a scope limit**, so the secondary question is either deferred or
   explicitly answered on transferred truth with that dependency stated in the result;
3. **abstention reported as its own quantity**, because 9 apo chains and a 3.8 Å resolution floor
   guarantee that abstention will happen and it must not read as failure.
