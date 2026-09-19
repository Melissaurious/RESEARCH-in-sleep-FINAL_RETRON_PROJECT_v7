# Stage 3A — positive structural criteria, as designed and as tested

Each criterion names an observable, an algorithm, a threshold, an expected failure mode, its
applicability, and what causes abstention. Nothing here uses a motif, a label, a prior boundary, or
a residual-flank rule.

## C1 — structural modularity of the element contact graph  · TESTED

| | |
|---|---|
| observable | contacts between secondary-structure elements |
| algorithm | elements from DSSP-KS (helix ≥ 4, strand ≥ 2); edge weight = number of CA–CA pairs ≤ 10 Å between two elements; normalised Laplacian; **k chosen by the largest eigengap over k = 2..8**; Ward linkage on the spectral embedding; modularity Q reported |
| threshold | none imposed on k — k is an output, not an input |
| expected failure mode | a densely packed single-domain fold has no spectral gap, so k is unstable; a dense graph can produce spatial slabs rather than domains |
| applicability | every chain with ≥ 6 elements and ≥ 60 residues — all 62 qualified |
| abstention | fewer than 6 elements, or no eigengap |

**Result: k = 3 is not what the fold says.** Natural k was 4 in 27 of 62 chains (44 %), 6–8 in 24
(39 %), and **3 in only 3 chains (5 %)**. Median modularity Q was **0.582** at natural k against
**0.495** when k was forced to 3 — the graph actively prefers a different number of modules.

## C2 — contiguity of the resulting modules · TESTED

| | |
|---|---|
| observable | sequence spans covered by each module |
| algorithm | for each module, the residue set, its maximal contiguous runs, and contiguity = largest run / module size |
| threshold | declared in advance: a module is "interval-representable" at contiguity ≥ 0.80 |
| expected failure mode | interleaved elements make every module discontinuous |

**Result: no module is interval-representable.** With k forced to 3, median contiguity was **0.255**,
median **8 spans per module**, and **0 of 186 modules was a single contiguous span**.

## C3 — contiguous-domain decomposition by normalised cut · **VOID, criterion defective**

| | |
|---|---|
| observable | residue contact graph, CA–CA ≤ 8 Å, \|i−j\| ≥ 3 |
| algorithm | exact dynamic programming over cut points minimising Σ cut(s, rest)/vol(s), k = 1..6, minimum segment 25 |
| intended threshold | natural k where relative improvement falls below 10 % |

**The objective is degenerate and the run is VOID.** Normalised cut is monotone increasing in k and
is identically 0 at k = 1, so "improvement" is undefined at the only point that matters and the
criterion trivially returns k = 1 for every chain. Output retained, marked `VOID_REASON`, in
`DOMAIN_ASSIGNMENTS_CONTIGUOUS.tsv`. **It is a recorded methodological failure, not a result.**

The correct form — not run in this session — normalises the interface against segment size in the
manner of PDP, `contacts(A,B) / (|A|^α · |B|^α)`, and accepts a split only when the interface is
sparser than expected, with α and the acceptance threshold declared before scoring.

## C4 — β-sheet membership as the positive palm criterion · NOT REACHED
## C5 — α-helical bundle as the positive thumb criterion · NOT REACHED
## C6 — recurrence of modules across proteins by structural superposition · NOT REACHED
## C7 — replicate-state stability of module assignment · NOT REACHED

C4–C7 were designed but not executed: C1 and C2 already falsified the premise they depend on, and
C3 — the criterion that would have supplied contiguous domains for them to describe — is void.
Running them on the C1 partition would describe modules that are neither three nor contiguous, which
answers a different question from the one this stage asks.
