# Stage 3B — bounded primary-literature evidence repair

**Scope:** retron catalytic truth only. No geometry detector was run. No catalogue-scale analysis.
The anti-circularity contract (`ANTICIRCULARITY_CONTRACT.tsv`) is **unchanged**; everything added
here is a *truth label*, which that contract already forbids as a detector input.

**Network was available in this session**, so the provisional statement in the dossier ("no network
access") no longer applies to the items repaired below. Nine mmCIF files were retrieved from RCSB
and landed with sha256 in
`data/stage3b_external_structures/` + `FETCH_LOG.tsv` (gitignored, absolute paths registered).

---

## 1 · What the primary paper actually says — verified verbatim

**Ji CG, Li Z, Wei XY, Li Y, Zhang JT, Liu X, Jia N.** *Mechanistic insights into activation of
bacterial Retron-Eco8 immunity by phage protein SSB.* **Nat Commun 2026 Jun 10;17(1):7374.**
DOI `10.1038/s41467-026-74106-9` · PMID `42270618` · PMC `PMC13402713`. Full text read this session.

| claim | verbatim source | evidence class assigned |
|---|---|---|
| catalytic motif | *"the YADD (Y198–D201) and ING (I247–G249) motifs in the palm domain, and the PMG (P163–G165) motif in the fingers domain"* | `AUTHOR_ASSIGNED` |
| upstream Asp + metal | *"A coordinated Mg²⁺ ion, positioned by the aspartate residue D107 and the YADD motif, **likely** facilitates catalysis"* | `AUTHOR_ASSIGNED` + **`METAL_ASSERTED_NOT_DEPOSITED`** — see §2 |
| mutational support | *"Mutations in conserved motifs … including the YADD motif (Y198–D201) of RT (YADD to YAAA) … abolished defense activity"* and *"Alanine substitution of residues in the YADD, ING, and PMG motifs, **as well as D107** and F112, abolished anti-phage defense activity"* | **`MUTATIONAL`** |
| independent confirmation | *"catalytically inactive variants of the reverse transcriptase (YADD to YAAA)"* retain normal DNA staining | `MUTATIONAL` |
| construct numbering | UniProt `P0DV59`, entity 1–374 ↔ parent 1–374 in all six Eco8 depositions — **no offset** | mapping exact |

**Individuation.** `D107A` is a single-residue substitution, so **D107 is individuated**.
`198YADD201 → 198AAAA201` mutates four residues at once, so **D200 and D201 are implicated jointly,
not individually**. The truth label records the site as `{D107} + {D200, D201}`, not three
independent residues.

---

## 2 · Which deposited Eco8 structure actually contains the Mg²⁺ — **none of them**

The operator brief attributed the Mg²⁺ to this paper. **It is in the paper's text and figure, and it
is in none of the paper's deposited coordinates.**

| entry | title | res. | paper | hetero atoms in file |
|---|---|---:|---|---|
| `9LBQ` | Retron-Eco8 complex | 2.94 Å | this paper | **HETATM = 0** |
| `9WN8` | Retron-Eco8 complex **in the presence of ATP** | 2.81 Å | this paper | **HETATM = 0** |
| `23OR` | Retron-Eco8–SSB complex | 3.11 Å | this paper | **HETATM = 0** |
| `9X94` | Apo Retron-Eco8 complex | 2.57 Å | Xiong *et al.*, NAR 2026 | 0 |
| `9LPA` | retron Eco8, active state | 3.30 Å | Li *et al.*, Mol Cell 2025 | ATP ×4 — **on the OLD nuclease**, 32.6 Å from the RT Asps |
| **`9X9B`** | **Retron-Eco8 complex with ATP-Mg²⁺** | 2.80 Å | Xiong *et al.*, NAR 2026 (`10.1093/nar/gkag111`, PMID 41665008) | **ATP ×4 + MG ×4 — on chain B, the OLD nuclease. Nearest Mg to RT D107/D200/D201 = 44.9 Å** |

The paper itself is consistent with this: *"Despite the inclusion of ATP in the sample, densities
corresponding to the ATP are unobserved."* Structural interpretation in that paper focused on the
2.81 Å dataset — `9WN8` — which contains no ligand.

**Conclusion.** There is **no structural metal evidence at the Eco8 RT active site in any deposited
model**, from any of the four papers. The Mg²⁺ claim is an author interpretation, recorded as
`METAL_ASSERTED_NOT_DEPOSITED`, and it is **not** counted as `METAL_CAT`.

**Chain completeness for scoring.** In all six Eco8 entries, residues **107, 200 and 201 are ASP with
modelled side chains**. `Y198` is present but its side chain is unmodelled in every entry. The RT
chain is complete enough to score. Measured carboxylate geometry, six independent depositions:

| entry | D107–D200 | D107–D201 | D200–D201 |
|---|---:|---:|---:|
| `9X9B` 2.80 Å | **2.54** | 3.29 | 3.44 |
| `9X94` 2.57 Å | **2.62** | 2.76 | — |
| `9LBQ` 2.94 Å | 2.98 | **2.72** | 3.51 |
| `9WN8` 2.81 Å | 4.10 | **2.92** | 4.91 |
| `9LPA` 3.30 Å | 4.01 | **3.16** | 5.08 |
| `23OR` 3.11 Å | 4.79 | **4.48** | — |

The same three-residue network, in six independent reconstructions from three laboratories.

---

## 3 · The other retron RTs — what the repair found (task 5)

RCSB was searched for every deposition of each retron RT, and every entry carrying Mg/Mn was fetched
and measured. **Metal presence in a file was never assumed to mean metal at the RT site.**

| retron | entries searched | new hard evidence | verdict |
|---|---|---|---|
| **Ec86 / Eco1** (`P23070`) | 7 (`7V9U 7V9X 7XJG 8QBK 8QBL 8QBM 9JM0`) | **`8QBL` Mg²⁺ 3.00 Å from D198** in RT chain A (2.66 Å map). `8QBK` gives Mg 3.22 Å from **D119** — *just outside* the declared 3.2 Å cut, recorded, **not counted** | **HARD_SINGLE**, now from two independent depositions (`7XJG` D198 @2.57 Å + `8QBL` D198 @3.00 Å); D119 near-threshold |
| **Ec67 / Eco2** (`P21325`) | 4 (`9I2F 9I2G 9S1F 9LM3`) | **`9I2G` Mg²⁺ 2.40 Å from D202** (the YADD D) **and** Mg²⁺ 1.97 Å from **D460** — two separate metal sites in one chain. `9S1F` metal-supports only D460/D462 | **HARD_MULTISITE_UNRESOLVED** — see §4 |
| **Ec78 / St85 / Eco7** (`Q46666`, `A0AB38GW94`, `A0AAW7FAU3`) | 18 | `9VHL` carries ATP+Mg — **51.1 Å from the nearest RT Asp**; it is the PtuA ATPase site. Other entries carry Zn only (structural / effector) | **NONE — unchanged** |
| **Ec83** (`Q47526`) | 4 | Zn only, on the effector | **NONE — unchanged** |
| **retron I-A `9N69`** | in the Ec78 search | no RT-site metal | **NONE — unchanged** |

---

## 4 · A rule defect found and fixed during the repair

Applying the dossier's `HARD_PAIR` rule to `9I2G` produced a false pair: the rule counted **D202
(polymerase) and D460 (the fused nuclease)** as one catalytic pair because both coordinate a
magnesium. They are in different domains and different active sites — the same failure mode the
dossier had already flagged for HIV-1 RT's RNase H centre.

**Two rules were added, declared before re-tiering and applied uniformly to all 60 chains:**

1. **Site locality.** Two hard-evidence Asp count as one site only if their carboxylates are within
   **8.0 Å** of each other.
2. **Site attribution.** A chain whose hard evidence falls in **more than one** separate acidic
   cluster is **`HARD_MULTISITE_UNRESOLVED`** unless an `AUTHOR_SITE` record or a VERIFIED literature
   label attributes one cluster to the RT polymerase site. **The motif is never used to attribute.**

Chains affected: `9I2G_B` (`[[202],[460]]` → unresolved) and `1RTD_A` (`[[110,185],[113],[443,498,549]]`
→ resolved by its own author `_struct_site` records, which name the polymerase cluster). Ec67 is
therefore held out of Tier A until its site attribution is settled by a targeted literature check —
the conservative call, taken deliberately rather than inflating the evidence.

---

## 5 · Revised evidence counts

### Retron biological RT sequences (6 replicate groups)

| class | before | **after** | which |
|---|---:|---:|---|
| `HARD_PAIR` | 0 | **0** | — |
| `HARD_SINGLE` | 1 | **1** | `RG03` Ec86 — now doubly supported (`7XJG`, `8QBL`) |
| `FUNCTIONAL_PAIR` *(new class)* | — | **1** | `RG06` Eco8 — `D107A` + `YADD→AAAA`, both abolish defence |
| `HARD_MULTISITE_UNRESOLVED` *(new class)* | — | **1** | `RG24` Ec67 — metal at D202 **and** at D460 |
| `AUTHOR_PAIR` | 0 | **0** | — |
| `NONE` | 5 | **3** | `RG05` Ec78/St85, `RG23` Ec83, `RG26` retron I-A |

**Retron groups with some independent catalytic truth: 1 → 3 of 6.**

### Whole register

| | before | after |
|---|---:|---:|
| RT chains | 51 | **60** |
| unique biological RT sequences | 31 | **31** (all nine new chains fall in existing groups, by UniProt and by sequence) |
| PDB entries | 50 | **59** |
| Tier A — clusters / groups / chains | 10 / 18 / 31 | **10 / 18 / 31** (unchanged) |
| Tier B — clusters / groups / chains | 2 / 3 / 7 | **3 / 4 / 17** |
| Tier C — clusters / groups / chains | 8 / 10 / 13 | **7 / 9 / 12** |

Tier B is now `C30_02` (Ec86 + Ec67), `C30_08` (Eco8) and `C30_11` (UG2/DRT2) — **three of the four
held-out groups are retrons.**

---

## 6 · Does the secondary question unblock?

> *How do retron RTs compare with other bacterial RT families in catalytic-site sequence and geometry?*

**It moves from BLOCKED to EXPLORATORY. It does not reach confirmatory.**

Supporting the move: three retron sequences now carry independent truth, one of them (Eco8) with
**functional** evidence that is stronger than any structural proxy for anti-circularity purposes,
because it uses no structural observable at all. Eco8's D107/D200/D201 geometry reproduces across six
independent depositions from three laboratories.

Blocking the confirmatory step, and to be written into the launcher as a declared limit:

1. **No retron RT has a catalytic-state structure.** Zero of the six groups has a ternary complex with
   an incoming nucleotide at the RT site. Every retron geometry available is a product or apo state.
2. **The evidence classes are not comparable across the comparison.** Tier A bacterial comparators are
   anchored by Mg/Mn + dNTP at the site; the retron side is anchored by mutation (Eco8), by a single
   metal contact (Ec86), or not at all. Comparing geometry across groups whose truth rests on
   different evidence types confounds the biology with the evidence.
3. **The state effect is larger than the expected signal.** The dossier measured ~1.5 Å between
   metal-bound (2.5–3.6 Å) and apo (4.2–5.0 Å) catalytic carboxylate separations. Eco8 alone spans
   2.54–4.79 Å across its own six depositions. A retron-vs-other comparison conducted across states
   would measure state, not lineage.
4. **n = 3 retron sequences with truth, 0 with a resolved structural pair.**

**Consequence for the launcher:** the secondary question is admitted as an **exploratory, state-matched,
descriptive** comparison with its own denominator, and is explicitly barred from producing a
confirmatory claim about retron-specific catalytic architecture. It becomes confirmatory only if a
catalytic-state retron RT structure appears, or if Ec78/Ec83/I-A gain primary-source functional truth.

---

## 7 · Exact evidence used

| item | source | identity |
|---|---|---|
| Eco8 author + mutational truth | Nat Commun 2026;17:7374 | DOI `10.1038/s41467-026-74106-9`, PMID `42270618`, PMC `PMC13402713`, full text read |
| `9LBQ_A`, `9WN8_A`, `23OR_A` | that paper's depositions | `P0DV59` 1–374, no offset; HETATM = 0 |
| `9X9B_A`, `9X94_A` | Xiong *et al.*, Nucleic Acids Res 2026;54(4):gkag111, DOI `10.1093/nar/gkag111`, PMID `41665008` | `9X9B` Mg/ATP on chain B (OLD nuclease), 44.9 Å from the RT site |
| `9LPA_A` | Li *et al.*, Mol Cell 2025, DOI `10.1016/j.molcel.2025.09.029`, PMID `41172990` | ATP on the effector, 32.6 Å from the RT site |
| `8QBK_A`, `8QBL_A` | Retron-Eco1 NAD⁺-hydrolysing filament paper | `P23070` 1–320; `8QBL` Mg–D198 3.00 Å; `8QBK` Mg–D119 3.22 Å (near-threshold, not counted) |
| `9I2G_B`, `9S1F_B` | *Structure and mechanism of antiphage retron Eco2* | `P21325` 1–586; `9I2G` Mg–D202 2.40 Å and Mg–D460 1.97 Å |
| `9VHL_A` | *Phage nuclease-mediated defense activation* | `Q46666` 1–311; nearest Mg 51.1 Å from any RT Asp |

All nine files landed with sha256 in `data/stage3b_external_structures/FETCH_LOG.tsv`.

---

## 8 · Still open after this bounded repair

* **Ec67 site attribution** — one targeted read of the Eco2 paper would move `RG24` from
  `HARD_MULTISITE_UNRESOLVED` to `HARD_PAIR` or `HARD_SINGLE`.
* **Ec86 mutational evidence** — not checked; the Retron-Eco1 papers may individuate D119/D197/D198.
* **Ec78, Ec83, retron I-A** — no functional truth checked; these are the three remaining `NONE` groups.
* **Non-retron Tier C groups** (AbiK, AbiP2, AbiA, UG28, DRT6, Drt3a) — untouched by this repair.
