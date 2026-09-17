# DECISION — repaired g4a + UG5 gate reviewed: FAIL/BLOCK (5/10); two verified bugs; eight bounded repairs

Date: 2026-09-16 · Track: `rt07` · Status: **stopped; returned to the operator**

Corrects `docs/decisions/2026-09-16_stage2_g4a_repair_and_ug5_gate.md`, which is **not rewritten**.

Supersede this record by a new record, never by rewriting it.

    REVIEW_SCORE: 5     REVIEW_VERDICT: FAIL/BLOCK
    review_gate.py -> {"decision": "continue", "reason": "positive threshold not met"}
    trend: 3 -> 4 -> 4 -> 5 -> 6 -> 5

**MAPPER NOT FROZEN. g4b NOT BEGUN. g5 BLOCKED. NO FULL-CATALOGUE APPLICATION.**

---

## 1 · Two bugs, verified here before acceptance

### B1 · The full-consensus denominator repair itself failed

`step2_analysis.py` counted HHM rows matching `^[A-Z]\s+\d+\s` instead of parsing the HHM `LENG`
field. Measured per family (my count vs `LENG`): Retrons 355/**475**, GII 513/**539**,
DGRs 331/**406**, CRISPR **305/796**, UG3 407/**421**, UG5 990/**1014**, AbiA 608/**708**.

**Corrected shared-core range: 7.5 – 27.5% of full consensus, not 7.7 – 44.9%.** CRISPR alone moves
from 44.9% to **17.2%**.

The error ran *against* the project's interest: corrected, the shared core is a **smaller** minority
than claimed, which strengthens the "minority core" conclusion. The repair still failed, and the
repaired tables carry wrong numbers.

### B2 · mmseqs identifier normalisation creates a phantom singleton

Input id `sp|P23070.1_Retrons` is returned by mmseqs as `P23070.1_Retrons` — the `sp|` prefix is
stripped. Its hits therefore never match back to the input id, and it becomes a spurious singleton
component. **Retrons is 93/1/1, not 92/1/1/1.**

The qualitative finding is unchanged (Retrons still does not usefully fragment: largest component
~98%), but the landed component structure is wrong and no assertion caught it.

## 2 · Overstatement to withdraw

**"no independent within-family held-out set exists at any defensible separation level" is too
strong.** At identity 0.50 the families *do* fragment substantially — largest components GII 98,
DGRs 104, CRISPR 15, UG3 5, Retrons 6.

The supportable claim is: **"no adequately sized independent within-family holdout exists at the
declared 0.30 / 0.50 rule."** The reviewer explicitly endorses retaining 0.30 and refusing a
post-outcome threshold change as *"conservative and valid"* — only the wording overreached.

## 3 · Further accepted findings

- **`hhmake -M 50` is not the HHmake default** (documented default `-M a2m`). Misclassified as
  `algorithmic_default`; it controls match states and therefore the frozen frame, so it is a
  deliberate choice needing sensitivity testing.
- **The 90%-dominant-component fragmentation criterion was never registered.**
- **"Pairs ≥50% identity" are directional mmseqs rows, not unique pairs** — 26/52/78/43/24 rows are
  roughly 13/26/39/22/12 unordered pairs.
- **UG5/AbiA maxima among coverage-satisfying pairs are 0.268 and 0.278**, not the unrestricted
  0.373 / 0.538 quoted.
- **12 of 24 UG5 construction hashes now differ** — the HMM/HHM files were regenerated after the
  gate ran. The scientific maps reproduce exactly, but the provenance record has drifted.
- **The verifier is still gameable**: `AUTHORED_TABLES.txt` and the parameter registry are
  unregistered mutable bypasses, and **there is no UG5 verifier at all**.
- **The UG5 gate is aggregate-profile-level, not per-sequence**; it omits the singleton component;
  and monotone order plus zero ambiguity are *"largely guaranteed by the one-to-one,
  order-preserving pairwise-alignment map"* — partly tautological, as suspected but not stated.

## 4 · What the review confirmed

The **g4a qualitative conclusion survives** (Q8: yes). Dyad 42/42; correspondence 42/42;
transitivity 87.0% with the sweep reproducing exactly (82.5 / 87.0 / 88.9 / 91.7 / 94.5%) and the
≥20-position filter excluding zero triples — *"no numerical evidence of outcome-driven tuning"*.
Cap repairs verified. Contradictory dyad outputs gone. The **150-anchor set was independently
reconstructed and matched exactly**, and UG5 real-vs-shuffled separation (135/150 at prob 97.3 vs
0/150 at 0.0) is *"decisive separation for that single deterministic aggregate shuffle"*.

The verifier does defeat ordinary drift: inputs authenticated, fresh temp dir, byte-identical
reproduction.

## 5 · Eight required repairs

1. Normalise or escape sequence identifiers before mmseqs; **assert exact input/output ID-set
   equality**; regenerate. Report Retrons as **93/1/1**.
2. Parse HHM **`LENG`** for the full-consensus denominator; correct every affected table and summary.
3. Deduplicate or explicitly label directional mmseqs hit counts; **register the 90%-dominance rule**.
4. Reclassify **`hhmake -M 50`** as a deliberate choice and sensitivity-test it.
5. **Land all 150 anchor coordinates**; add **per-sequence** UG5 mappings, every component including
   the singleton, dyad inclusion, transitivity, spacing/stability, explicit failure/abstention
   states, and non-tautological ambiguity and order checks.
6. Add a **UG5 verifier**; freeze or canonically hash its 24 construction inputs; fix the split-table
   total sort; verify all ten tables.
7. Register and externally anchor `AUTHORED_TABLES.txt`, the parameter registry, audit/report files
   and the frozen expected outputs.
8. Add audit entries for the denominator bug, identifier normalisation, post-gate g4a regeneration
   and hash drift, and incomplete component evaluation; **narrow the "any defensible level"
   wording**.

Optional: reciprocal UG3 withholding or a genuinely unseen lineage; multiple composition-matched
shuffles and unrelated real-protein controls; leave-one-construction-family sensitivity (the
all-partner anchor count ranges **150–181** when one partner is omitted); treat the 150 coordinates
as **11 correlated contiguous runs**, not 150 independent evidence units.

## 6 · Supportable claims, as narrowed by the review

A compact shared RT correspondence region is recoverable across the seven tested family profiles ·
the catalytic dyad corresponds in all 42 tested directed pairs · transitivity is high but imperfect ·
the shared region is a **minority (7.5–27.5% of full consensus)** · a six-family frame transfers at
**profile level** to UG5 better than the tested shuffle, with **sharply heterogeneous component
callability**.

**Not supported:** universality · transfer to unseen lineages or arbitrary RT families ·
**per-sequence coordinate accuracy** · biological boundaries · independent within-family transfer
for the five non-independent families.

## 7 · Why this session stops here

The task's stop condition requires returning to the operator after the independent review rather
than opening another repair cycle. The eight repairs are bounded and specific, but repairs 5 and 6
change what the UG5 gate *is* — from an aggregate-profile test to a per-sequence, verifier-protected
one — which is a scope decision.
