# g4a — method, and the failure modes that remain

## Method, as executed

Only sequence input: `RTs-collection.faa`. No `.fst`, no `.hmm`, no `.sto`, no Pfam was opened by
any derivation step. Seven families predeclared in `control/PREDECLARATION.md` before any
alignment ran.

    eligible full-length-source proteins
      -> cd-hit -c 0.50 clusters
      -> WHOLE clusters dealt to derivation / development / challenge
      -> MAFFT L-INS-i (--thread 1) on derivation only        [primary]
      -> MUSCLE v5 on the same set                            [sensitivity]
      -> per-column gap fraction, entropy, modal fraction, context entropy  [ranked, no cut-off]
      -> hmmbuild + hhmake on the derivation alignment ONLY   [de novo profiles]
      -> hhalign, all 42 ordered pairs                        [between-family]
      -> dyad correspondence read from the alignment text     [anchor test]
      -> transitivity + supported intersection                [Phase C]
      -> hmmsearch against held-out challenge sequences       [transfer, as a score]

## What was established

| result | value |
|---|---|
| between-family profile correspondence | **42 of 42** ordered pairs, hhalign probability **74.2–100.0**, best E-value **4.8e-42** |
| catalytic dyad correspondence | **42 of 42** `DYAD_CORRESPONDS` at offset 0, one dyad per consensus |
| transitive consistency | **210** triples, mean **88.2%** within ±2, **174/210 (83%)** at ≥80% |
| supported intersection, global | **68–160** positions per family; **18.9%** (UG5) to **57.3%** (CRISPR) of covered positions |
| global-or-class | **69.1%** (UG3) to **99.6%** (CRISPR) |
| global core extent | spans of **94–201** consensus positions, **64.2–87.3%** of each span global |
| transfer, as a score | SELF median bit score **424.1** vs CROSS **32.6** — a **13.0×** separation |
| reproducibility | `verify.sh` → byte-identical from registered inputs |

## Failure modes that remain — none of these is fixed by g4a

**1 · No family was held out.** All seven families contribute a derivation profile, so `G13`
whole-family transfer is untested **by design**. Sequence-level holdout is genuine — whole cd-hit
clusters at 0.50 were assigned to roles, so no challenge sequence has a ≥50% relative in
derivation — but *family* generalisation is not evidence here. An eighth family withheld entirely
would be needed.

**2 · The detection-rate transfer test cannot fail.** At `hmmsearch --max -E 10`, 46 of 49 cells
sit at 100%. This is flagged `NON_DISCRIMINATING` in the table itself and must not be quoted. The
bit-score distribution (`G08`) is the quantity that carries information.

**3 · hhalign probability is profile similarity, not positional homology.** A pair at probability
100.0 tells us the profiles correspond overall; it does not certify any single column. The
transitivity check (`G05`) is the partial guard, and 17% of triples fall below 80%.

**4 · The supported intersection depends on the seven families chosen.** A different seven would
give a different intersection. The families were predeclared on lineage coverage, N and length —
never on how they align — but the dependence is real and unquantified. Rebuilding under a
different admissible family set is the obvious sensitivity analysis and was **not** run.

**5 · MUSCLE is used as a sensitivity method, not an independent instrument.** Both aligners are
progressive/consistency-based and share assumptions; their agreement is weaker evidence than two
genuinely different methods would be. `G01` reports it as method sensitivity for that reason.

**6 · UG5 and GII are the weak corners.** Lowest global fractions (18.9%, 19.0%), the worst
transitive triples, and the weakest transfers (GII profile on UG5 challenge: median bit score
0.3). Any claim about the shared core is weakest exactly there.

**7 · Retrons are analysed but not independently evaluated.** 90 of 95 available eligible retrons
were drawn; the challenge sequences share the source pool with the derivation profile. See
`stage1_retron_augmentation_design.md`.

**8 · Three coding errors were made and corrected during execution**, two of which produced
plausible *negative* results — an empty correspondence table and a spurious "the catalytic dyad
does not correspond across families". Both are documented in `control/ERRATA.md`. The general
lesson adopted: **do not reimplement a tool's internal coordinate system to interrogate its
output; read the output.**

**9 · A fourth error was found only because the harness was repaired.** MAFFT `--thread 4` is
non-deterministic; conclusions were stable across runs but tables were not byte-reproducible until
MAFFT was pinned to `--thread 1`. The previous bundle's harness could not have detected this,
because it wrote the reproduction over the expected output.

## What g4a does not claim

No biological boundary accuracy. No complete RT architecture truth. No biological absence from
non-detection. No universal RT0–RT7 partition. No RT0 label on any N-terminal sequence. No family
assignment accuracy. No claim that similar normalised position implies correspondence — every
correspondence reported here came from profile-profile alignment, never from position matching.
