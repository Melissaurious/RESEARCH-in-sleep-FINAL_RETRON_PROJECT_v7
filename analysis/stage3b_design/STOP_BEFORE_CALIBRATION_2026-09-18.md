# Stage 3B — three g2 truth rules applied; STOPPED before detector calibration

**Instruction honoured:** *"If applying these rules uncovers a fourth truth-definition ambiguity that
could affect labels, stop and report it before calibration rather than resolving it after seeing
detector performance."* Two such items were found. **No detector was built. No threshold was frozen.
Tier B was not opened.**

Truth schema **v2.0** (`stage3b-truth-2.0`) is implemented in `schema/truth_schema.py` +
`schema/scan.py` and applied uniformly to all **62 chains** → `TRUTH_TABLE.tsv`.

---

## 1 · The three rules, as implemented

**Rule 1 — reaction products.** New category `REACTION_PRODUCT = {POP}` (pyrophosphate 2−), cutoff
4.0 Å. It sets `catalytic_state_context` (e.g. `POST_CHEMISTRY`) and **can never create a `HARD_*`
class**. The hard-evidence rule is untouched: `METAL_CAT` (Mg/Mn ≤ 3.2 Å) or `SUBSTRATE_NT` (≤ 4.0 Å)
only. All 62 chains were re-scanned. **One hit:** `9Z6Y_H`, POP 3.90 Å from D192 and 3.52 Å from
D291 → `catalytic_metal+POST_CHEMISTRY+nucleic_acid`. Its `HARD_PAIR` comes from the two Mg, not from
POP.

**Rule 2 — modified polymer residues.** `MSE→M`, `PTR→Y`, `CSX→C` are routed to the polymer and are
never seen by the ligand rules. Both identities are kept: coordinate identity in
`modified_polymer_residues` (`650:PTR->Y`), canonical letter for sequence normalisation.
`PROTEIN_PRIMER` is annotated where supported: `9Z6Y_H` and `9Z6Z_H` (PTR650, covalent DNA attachment
per Science 2026). Applied uniformly: 5 chains carry modified residues (`5HHK_A` 13× MSE, `7R06_A`
PTR44, `8C8J_A` CSX661, `9Z6Y_H`/`9Z6Z_H` PTR650). **No modified residue in the population is an
aspartate, so rule 2 is label-neutral by construction** — but it is now explicit rather than
accidental.

**Rule 3 — channels stay independent.** Three columns, never merged: `S_evidence` (coordinate),
`L_author_assigned`, `F_mutational`. `S_class` is determined **only** by the coordinate rules.
For `9Z6Y` Drt3a the table records, separately and without reconciliation: coordinate set
`{D115, D197}`; mutational pair `{D197, D198}`; author motif `YVDD / Y195–D198`. Concordance at D197
and the D115-vs-D198 disagreement are both preserved.

---

## 2 · What rule 3 forced — a v1 implementation correction

In v1, deposition `AUTHOR_SITE` records were being counted toward the *coordinate-derived* catalytic
set, which could create a `HARD_PAIR`. That contradicted v1's own documented rule and its separate
`AUTHOR_PAIR` class, and **rule 3 forbids it outright**. v2 excludes `AUTHOR_SITE` from the structural
set.

| chain | v1 | v2 | cause |
|---|---|---|---|
| `5HHJ_A` `5HHK_A` | `HARD_PAIR`, set {151,239} | **`AUTHOR_PAIR`**, set {} | both residues were AUTHOR_SITE-only (K⁺, not Mg/Mn) |
| `5HHL_A` | `HARD_PAIR`, set {139,227} | **`AUTHOR_PAIR`**, set {} | same |
| `1RTD_A` | set {110,113,185,443,498,549} | set {110,185,443,498,549} | D113 was AUTHOR_SITE-only |

Group `RG01` (GII maturase): `HARD_PAIR` → `AUTHOR_PAIR`. **Cluster `C30_01` stays Tier A** via
`6AR1_A`, which has genuine Mg-based evidence.

The other 30 changes are presentational: chains with soft-only evidence moved `NONE` → `WEAK`, a class
v1 defined but never assigned. Both rank below the Tier B threshold, so nothing moved.

**Tier membership is unchanged by all of this: 11 / 3 / 6 clusters, 19 / 4 / 8 groups, 34 / 17 / 11
chains.**

---

## 3 · AMBIGUITY 4 — nucleoside monophosphates. Declared; measured label-neutral

`24NC` contains `DGT` (dGTP), **`DGP` (dGMP) and `GMP`** together. A nucleoside monophosphate is
neither a triphosphate substrate nor a pyrophosphate product; the frozen schema has no category for
it. Declared as `NUC_MONOPHOS`, **unclassified by design**.

**Measured, before any detector existed:** in `24NC` chain A, `DGP` and `GMP` have **no aspartate
within 4.0 Å** (`DGP` → none; `GMP` → none), while `MG` reaches D149/D240/D241 and `DGT` reaches
D149/D240. **Whichever way they are classified, no label and no catalytic set changes.** The
classification is a single line in `truth_schema.py` and is reversible at zero cost.

Also declared, for completeness: `PO4`/`SO4` are treated as buffer, not as reaction products, because
they cannot be distinguished from crystallisation additives without per-entry author annotation.
`NAD`/`AR6` are `EFFECTOR_LIGAND` — they belong to the effector's NADase chemistry, not the
polymerase.

---

## 4 · AMBIGUITY 5 — the stop. Site attribution is under-determined for `1RTD`, and it moves a threshold

`1RTD_A` (HIV-1 RT p66) carries **two** separate structural clusters:

```
[[110, 185],            <- DNA polymerase active site
 [443, 498, 549]]       <- RNase H active site
```

The frozen attribution rule says a multi-cluster chain is `HARD_MULTISITE_UNRESOLVED` *"unless an
AUTHOR_SITE record or a VERIFIED literature label attributes one cluster to the RT polymerase site."*
**The deposition's `_struct_site` records annotate BOTH sites** — AUTHOR_SITE aspartates are
`{110, 113, 185, 443, 498, 549}`. The rule therefore fires as "attributed" without selecting a
cluster, and the implementation falls back to taking the largest cluster, which is the **RNase H
triad**.

**This is not cosmetic. It moves a threshold that was about to be frozen:**

| Tier A truth pairs used for calibration | n | \|i−j\| range | median |
|---|---:|---|---:|
| polymerase pairs only (22 pairs, 17 chains) | 22 | **77 – 113** | 100 |
| with the RNase H triad included (current behaviour) | 23 | **51 – 113** | 99 |

The RNase H pairs have separations of **51, 55 and 106**; two of them sit far below every polymerase
pair in the population. Including them **widens the calibrated sequence-separation window by 26
residues at the lower bound** — on the basis of an active site that is not the target of this stage.

`1RTD_A` is the only Tier A chain with more than one cluster. (`9I2G_B`, Ec67, is the only other
multi-cluster chain in the whole population and it sits in Tier B.)

**I did not resolve this.** Three options, for the operator:

1. **Exclude multi-cluster chains from calibration**, keeping them as comparators. `1RTD_A` is the
   only Tier A case; the window becomes 77–113.
2. **Require the attribution source to name exactly one cluster.** Multi-cluster author annotation
   then does not attribute, `1RTD_A` becomes `HARD_MULTISITE_UNRESOLVED`, and — since `5VBS_A` is
   `WEAK` — **cluster `C30_07` would drop from Tier A to Tier C**, losing the viral stratum.
3. **Run the targeted-literature step for `1RTD`** (its `literature_check_status` is still `PENDING`)
   and let the functional channel attribute the polymerase cluster, per rule 3's use of literature for
   attribution rather than redefinition.

Option 3 is most consistent with the project's own discipline, but each option changes either the
frozen window or the Tier A composition, so it is the operator's call.

---

## 5 · State at the stop

**Done:** mmCIF fetched for the 11 legacy-PDB entries and verified **content-identical** to the legacy
files (same residue counts, same aspartate sets, same hetero inventory — no format-driven data loss);
complete hetero inventory over the population (37 distinct components, every one categorised);
schema v2.0 implemented and applied to all 62 chains; truth table landed with a `truth_source` column
(`OWN_CHAIN` 25, `TRANSFERRED_WITHIN_REPLICATE_GROUP` 9, `NONE` 28).

**Not done, deliberately:** foldseek pin; resolution eligibility cut; the g1 bundle; the
anti-circularity checker; any threshold; any detector; any calibration; Tier B.

**Kill criteria:** none fired. K1 not applicable (no detector). K2 not applicable (Tier B untouched).
K3 not applicable (no threshold set). K4 Tier A has 34 chains, well above the floor of 12. K5 the
decoy pool is unchanged. K6 not applicable (no detector).
