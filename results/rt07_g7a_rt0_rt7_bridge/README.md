# rt07_g7a_rt0_rt7_bridge — the historical RT0–RT7 bridge, closed

STATUS: VERIFIED — `run.sh` was run to completion from a cleared scratch directory on
2026-09-18 and reproduced every number below; all 12 `verify.sh` checks pass.

**Terminal. 8 of 8 historical labels carry a terminal evidence status: 4 `ESTABLISHED`,
2 `PARTIAL`, 2 `UNRESOLVED`. No control FAILED. No frozen object was modified.**

Launcher: `launchers/LAUNCHER_03_rt0_rt7_closure.md` · Reruns with
`bash results/rt07_g7a_rt0_rt7_bridge/run.sh`

## Counts, including the ones that look bad

```
n_attempted: 8      historical labels RT0-RT7 carried into the crosswalk
n_succeeded: 6      labels that received a supported or partial correspondence and are DRAWN
n_dropped:   0      nothing was dropped, filtered or excluded
```

**`n_dropped: 0` is exact and load-bearing.** The two labels that did not succeed — RT0 and
RT1 — were **not** dropped: they are carried through every table with a measured
`NO_SUPPORTED_CROSSWALK`, a terminal status, and a written statement of what may still be said
about them. A label that returns nothing is a result here (WA-G.5), and the figure draws those
two rows explicitly rather than interpolating them.

Panel-level counts, a different denominator: `n_attempted: 6` sequences, `n_succeeded: 5`
produced a scientific row, `n_dropped: 1` (`MMLV_5VBS_A`, rejected at 246 aa by the frozen
250 aa eligibility rule — see NC-3 below, which is recorded `INCONCLUSIVE`, not `PASS`).

---

## What this gate measured, in one sentence

**Production `state_id` → LtrA P0A3U0 residue** — the one link the RT0–RT7 crosswalk had never
had — obtained by applying the frozen instrument `rtmap-1.0.0/53a1e738a19b3896`, unmodified, to
LtrA, and then composing it with the literature-derived coordinates that are already landed.

Everything else in this bundle is either tracing (what the sources actually say) or derivation
from that one measurement.

## The bridge

| | |
|---|---|
| anchors MAPPED on LtrA | **143 of 150** (LtrA verdict `MAPPED`, mapped fraction 0.9533) |
| frozen state span | **107–317** |
| **LtrA residue span the anchors reach** | **97–363** |
| `CAT_STATE` 262 | LtrA residue **306**, window `YADD`, `CATALYTIC_CONFIRMED` |

**The residue span is the binding constraint of the whole gate.** The instrument's 150 anchors
begin at LtrA 97. Everything N-terminal to that — which is exactly where the literature places
RT0 and RT1 — **cannot receive frozen-state support however well defined it is historically**.
That is a property of the frozen instrument, and per `LAUNCHER_03` §2 and §3 it is reported,
not repaired.

## The closure decision

| label | terminal status | correspondence | states | LtrA |
|---|---|---|---|---|
| **RT0** | `UNRESOLVED / NOT IDENTIFIABLE` | `NO_SUPPORTED_CROSSWALK` | 0 | — |
| **RT1** | `UNRESOLVED / NOT IDENTIFIABLE` | `NO_SUPPORTED_CROSSWALK` | 0 | — |
| **RT2** | `PARTIAL / INTERPRETIVE` | `PARTIAL` | 17 | 97–123 |
| **RT3** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 22 | 126–166 |
| **RT4** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 42 | 170–230 |
| **RT5** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_MANY_TO_1` | 34 | 311–347 |
| **RT6** | `PARTIAL / INTERPRETIVE` | `SUPPORTED_MANY_TO_1`, downgraded by rule D1 | 34 | 311–347 |
| **RT7** | `ESTABLISHED OPERATIONAL CORRESPONDENCE` | `SUPPORTED_1_TO_1` | 6 | 356–361 |

`tables/g7a_closure_decision.tsv` carries, per label, the exact wording downstream work is
permitted to use. **That column is the operative output of this gate.**

## Three findings that were not expected

1. **The inherited statement "RT0 = M1–R85, RT1/7 = R86–R364" misreads its own source.** Blocker
   2005 says the R85 cleavage site is **in RT1**, and that the 10-kDa fragment *contains* RT0.
   Table 1's column is headed "Domain composition" — it names what a fragment holds, not where a
   domain ends. So **there is no source-stated RT0|RT1 boundary anywhere**, and the junction lies
   somewhere in the unstated window LtrA 39–85. Recorded in `control/ASSIGNMENT_RULE.md`
   Amendment 1, made from the PDF before the measurement ran. No landed g2 number is affected —
   g2 used the coordinate only as an external test — but the statement text is corrected.
2. **The strongest historical coordinate in the entire held corpus bounds the *end* of the
   series, not its beginning.** Blocker states a cleavage site "between RT7 and domain X" at
   R364/R365. The frozen anchor span independently ends at LtrA 363, and g2 block 6 ends at 361.
   Three routes — primary text, independent reconstruction, and the frozen instrument — agree
   that the numbered series ends at about 357–365. RT7 is the best-determined label, not RT0.
3. **`5G2X`, not `6AR1`, is the right structural comparator for this bridge.** The registered g7
   plan names `6AR1`; read from the file, `6AR1` is GsI-IIC RT from *Geobacillus
   stearothermophilus* (417 modelled residues, His8-tagged) — a different protein. `5G2X`
   entity 3 is **LtrA itself**, and its author numbering agrees with P0A3U0 at **487 of 487
   modelled residues, zero offset**. Corrected here and carried to `g7b`.

## Controls — every one reported

| control | result | what it showed |
|---|---|---|
| PC-1 catalytic | **PASS** | `CAT_STATE` 262 → LtrA 306, `YADD`, `CATALYTIC_CONFIRMED`, 1 dyad in the sequence |
| PC-3 structural numbering | **PASS** | 5G2X chain C agrees with P0A3U0 at 487/487 modelled residues |
| PC-4 the Zimmerly anchor | **PASS** | the catalytic residue 306 lies inside g2 block 5 — so "the catalytic YxDD lies in subdomain 5" is *measured*, not assumed |
| PC-5 substrate | **PASS** | LtrA verdict `MAPPED`, 143/150, bitscore 378.1, E 3.2e-117 |
| PC-2 anchor span | **MEASURED** | states 107–317 → LtrA 97–363. A limitation, not a pass/fail |
| NC-1 shuffled LtrA | **PASS** | `ABSTAIN`, 0/150, bitscore −2.7 |
| NC-2 reversed LtrA | **PASS** | `ABSTAIN`, 0/150, bitscore −3.8 |
| NC-3 MMLV RT (5VBS) | **INCONCLUSIVE** | never reached the mapper: 246 aa < the frozen 250 aa minimum. **Not counted as a pass** |
| NC-4 anti-circularity | **PASS** (`verify.sh`) | no `g5`/`g6` artefact is an input or is read by any script |
| 12/12 numbering | **PASS** | every residue identity Blocker states agrees with the project's LtrA record |

## The six adversarial questions (BS-14)

**1 · Where is each headline claim overstated — name the word.**
The word is **"correspondence"**. Four labels are reported as `ESTABLISHED OPERATIONAL
CORRESPONDENCE`, and a reader will hear "RT3 *is* states 136–177". It is not. What was measured
is that frozen anchor states fall inside a LtrA interval that the historical evidence places
that label in. The second word is **"supported"**: `SUPPORTED_1_TO_1` means *no competing
assignment survived the declared rule*, not that the assignment was independently confirmed.
The third is **"established"** itself — everything here was measured **on one protein**, LtrA.
Nothing in this bundle demonstrates that any correspondence transfers to another family, and
`tables/g7a_closure_decision.tsv` says so in every row.

**2 · What specific alternative explanation produces this exact number?**
That the ordinal propagation in rule A3 is simply **wrong by one block**. There are six
reconstructed blocks and seven numbered labels, so some pair must collapse; A3 anchors the frame
at RT5 via the catalytic motif and propagates outward, and Route C selects RT5+RT6 as the
collapsing pair. If instead RT6 owned block 6 and RT7 had no block, every label from RT6 upward
would shift and RT7's `ESTABLISHED` status would vanish. What argues against that is Blocker's
independent statement that the series ends at R364/R365, which block 6 (356–361) sits directly
against and block 5 (304–347) does not. That is one external constraint, not a proof, and it is
why RT6 is **downgraded** rather than reported as established.
A second alternative, for the two `NO_SUPPORTED_CROSSWALK` rows: they may reflect only that the
GII-derived profile has no anchors in its own N-terminal region, and nothing whatever about RT0
or RT1. **That reading is fully consistent with the data and is stated in the closure table** —
which is why those rows are `UNRESOLVED / NOT IDENTIFIABLE` rather than any claim of absence.

**3 · Could this test have returned a negative?**
Yes, and two of the eight rows *are* negatives. Four separate kills were declared in advance and
each could have fired: LtrA could have abstained (PC-5), `CAT_STATE` 262 could have missed the
catalytic dyad (PC-1), the decoys could have mapped (NC-1/NC-2), and the catalytic residue could
have fallen outside g2 block 5 (PC-4) — which would have destroyed the single anchor the whole
assignment rests on. The gate was also designed to survive returning **eight** unresolved rows.

**4 · The unit of every rate.**
`mapped_fraction` 0.9533 = MAPPED anchor states ÷ **150 frozen anchor states**, per sequence.
`n_supporting_states` = MAPPED anchor states whose LtrA residue lies inside that label's
reference interval; denominator **150**, and the intervals are **not** disjoint — RT5 and RT6
share all 34 of theirs, so the per-label counts must never be summed. The numbering control is
**12 of 12** stated residue identities and **3 of 4** published Edman sequences. `487/487` is
modelled residues of **5G2X chain C**, not of LtrA's 599. Every table carries `unit` and
`denominator` columns.

**5 · Which numbers have no producing script?**
The **quoted text** of the four Blocker passages and the Zimmerly `Z11` statement. They were read
by a directed `pdftotext -layout` extraction, and the register records the page context, but a
quote is not a computed number and no script asserts that the PDF says it. `run.sh` re-extracts
the text so the quotes can be re-checked, and the g1-verified assignment ids (`B02`, `Z08`,
`Z11`) are the independent second record. Everything else in `tables/` is produced by a named
script in `MANIFEST.tsv`.

**6 · What was withdrawn or weakened?**
- The **A1 clause of the declared rule was withdrawn and rewritten** before the measurement ran.
  Its original reading ("RT0 = M1–R85; RT1/7 = R86–R364") was traced to the PDF, found to
  misread fragment nomenclature as a domain boundary, and replaced by Amendment 1. The
  correction makes RT1 *worse* determined, not better.
- **NC-3 was downgraded from PASS to INCONCLUSIVE** after inspection: the sequence was rejected
  at 246 aa by the frozen eligibility rule and never reached the mapper, so it is not evidence
  that the mapper abstains on out-of-population proteins.
- **RT6 was downgraded** from `ESTABLISHED` to `PARTIAL` by declared rule D1, because its
  individual position rests only on comparator evidence.
- The prior proposal table's `1:1 candidate` for RT2 was **not** reproduced: RT2 measures
  `PARTIAL`. See `tables/g7a_prior_proposal_comparison.tsv`.
- **Attempted and did not survive:** acquisition of Malik, Burke & Eickbush 1999, the defining
  source for RT0. Two routes failed and the abstract does not mention domain 0, domain Z or any
  numbered RT domain. The absence is landed as `MISSING_PRIMARY_ASSET`, and it is the reason
  RT0's status is terminal rather than open.

## What this gate did NOT do

No HMM or mapper development. No revalidation of the frozen mapper — Stage-2 validation stays
CLOSED at Endpoint A. No motif discovery, no phylogeny, no retron reclassification, no `g6`
family architecture, no RT–ncRNA work, no fingers/palm/thumb segmentation. No `g5` or `g6`
output was read, for any purpose.
`results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv` is **unchanged and still
`UNRESOLVED` in every row**, and `crosswalk.assert_unresolved_until_g7()` still passes —
production emits no historical label, which remains true after this gate.

The remaining comparator campaign — Toro 2014, Mestre 2020, myRT, Toro 2026, DSSP
fingers/palm/thumb, `foldseek`, the non-LTR R2 structure — is **`g7b`** and is untouched.

## Claims

`C3` `primary`, `C9` `supporting`, `C7` `supporting`. **No claim is promoted by this bundle.**
Status lives only in `idea-stage/docs/research_contract.md`, where all three remain `UNPROVEN`.
