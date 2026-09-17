# DECISION — g4a negative control added; independent review NOT obtained

Date: 2026-09-16 · Track: `rt07` · Status: **g4a executed and reproducible; UNREVIEWED**

Extends `docs/decisions/2026-09-16_stage2_g4a_frame_recovery.md`, which is not rewritten.

Supersede this record by a new record, never by rewriting it.

**NO FULL-CATALOGUE APPLICATION; g5 NOT STARTED. g4b NOT AUTHORISED.**

---

## 1 · The review could not be obtained

The independent reviewer (`codex` / `gpt-5.6-sol`) ran ~4 minutes and terminated on an external
account quota: *"You've hit your usage limit … try again at 4:38 PM."* **No score, no verdict, no
findings.**

`review_gate.py` requires a score and a verdict. Both are absent, and supplying placeholders would
fabricate a review, so **the gate was not called and this round has no transition.** `WA-A.5`
forbids routing around review or substituting a same-family reviewer; the executor is
`claude-opus-5`, so self-review is inadmissible and was not performed. No non-OpenAI-family
reviewer backend is configured in this session.

**Consequence: g4a's results stand as executed and reproducible, but unreviewed. They may not be
promoted and `g4b` is not authorised until a review is obtained.** The request record
(`review-stage/DESIGN_REVIEW_REQUEST_g4a.md`) is complete and can be re-submitted unchanged.

## 2 · A negative control was added, because the study lacked one

The executing session had flagged three weaknesses in its own work to the reviewer before the
attempt. With no review in flight, the most important was repaired rather than left open.

Decoys are built from the derivation sequences themselves, so no external data was needed:
**SHUF** (per-residue shuffle, composition and length preserved) and **REV** (reversed).

### Results — the control vindicates the main claims

| comparison | hhalign probability | versus the real result |
|---|---|---|
| real vs SHUF decoy, 42 pairs | **0.0 – 0.2**, median 0.0 | real: **74.2 – 100.0** |
| SHUF decoy vs SHUF decoy, 42 pairs | **0.0** | — |
| real vs REV decoy, 42 pairs | **0.1 – 4.3**, median 0.5 | — |

| transfer | median best bit score |
|---|---|
| real profile vs SHUF decoy sequences | **−2.3** |
| real profile vs REV decoy sequences | **−1.9** |
| real CROSS-family (landed) | **32.6** |
| real SELF (landed) | **424.1** |

Dyad: across the 84 real-vs-decoy pairs, **1** returned `DYAD_CORRESPONDS`; the rest had no dyad
in the query consensus or no aligned dyad.

**This answers all three self-criticisms:**

1. *Is hhalign 74.2–100.0 just what any profile pair gives?* **No.** Decoys give 0.0–4.3.
2. *Is 42/42 `DYAD_CORRESPONDS` near-inevitable?* **No.** 1 of 84 decoy pairs achieves it.
3. *Is CROSS 32.6 near-tautological?* **No.** The decoy floor is **−2.3**, so the cross-family
   signal is real, if weak, and sits well above noise.

### One control is invalid, and is reported as such

**`REV` decoy-vs-decoy gives probability 39.9–100.0, median 98.2** — indistinguishable from the
real result. This is **not** a failure of the study; it is a failure of that control. Reversing
*both* families preserves their mutual similarity exactly — reversed homologs remain homologous —
so `REV`-vs-`REV` is the original comparison run backwards, a positive control in disguise. Six
such pairs even return `DYAD_CORRESPONDS`, from reversed `DD` patterns.

The valid negative controls are the three rows above it. `REV`-vs-`REV` is retained in the landed
table with this explanation rather than deleted, because a discarded control is invisible and an
explained one is not.

## 3 · The harness was extended, and caught a real gap

Adding the control to `verify.sh` immediately exposed that three tables were **not** machine
generated — two authored design tables plus a retron split produced by an ad-hoc command.

Fixed: `scripts/g4a_retron_split.py` makes the split reproducible from the landed selection and
role tables, and `control/AUTHORED_TABLES.txt` declares the two genuinely authored tables, which
the harness now asserts exist but does not diff. The harness again reports **"OK: every landed
table reproduced byte-identically from registered inputs."**

## 4 · What is unchanged

The g4a outcome remains **`g4a PARTIAL`** — class/family frames supported, a universal frame not
justified; the shared core is 18.9–57.3% of covered positions. The negative control strengthens
the evidence for that outcome without changing it.

Still unestablished, across five reviews: biological absence, exact boundaries, family-assignment
accuracy, phylogenetic eligibility. Still untested by design: **whole-family transfer** — all
seven families contribute a derivation profile, so no family is held out.
