# Producer record for the artefacts no script in this bundle computes

`MANIFEST.tsv` names this file in the `script` column for every artefact that was **not** produced by
running code here. Each is listed with how it actually came to exist, so "no producing script" is a
stated decision rather than a silence (the same convention as `n/a - <why>` for `seed` and
`denominator`).

## Retrieved once, over the network, then landed

The literature retrieval was a one-time audited acquisition (Europe PMC REST, NCBI E-utilities, and
publisher full text where it was reachable). It is **not** re-run by `run.sh`: re-fetching would make
the stage depend on a live network and on publisher availability, and the retrieved text is the
evidence. Every quoted statement carries its source, locator and retrieval status; nothing that could
not be read verbatim was recorded as evidence.

| artefact | how it was produced |
|---|---|
| `XY_REGION_EVIDENCE.tsv` | Region X/Y literature audit — 41 statements over 30 sources, quotes extracted programmatically from cached full texts |
| `tables/C_literature_boundaries_retrieved.tsv` | fingers/palm/thumb boundary audit — 73 statements, 49 sources |
| `tables/C_sources.tsv`, `tables/D_sources.tsv` | per-source retrieval status (FULL_TEXT / ABSTRACT_ONLY / NOT_RETRIEVED / NOT_SEARCHED) |
| `tables/C_audit_notes.md`, `tables/D_audit_notes.md` | the retrieval passes' own coverage and hazard notes |
| `tables/D_source_cache_hashes.tsv` | sha256 of each retrieved text; the texts themselves stay in disposable scratch and are not redistributed here |

Both retrievals were performed by subagents. **Their output is data, not authority:** every statement
used downstream was re-verified in this bundle — literature residue numbers against the deposited
sequences (`LITERATURE_BOUNDARY_AUDIT.tsv`, NUMBERING-CHECK rows, 13 verified, 6 statements not
joined), and one retrieval claim was **not reproduced and not adopted**
(`CONTRADICTIONS_AND_UNCERTAINTY.tsv` X05).

## Authored

| artefact | how it was produced |
|---|---|
| `STAGE3C_DECISION_REPORT.md` | written from the landed tables; every number in it is traceable to a table and a script |
| `CONTRADICTIONS_AND_UNCERTAINTY.tsv` | authored register; each row cites the file that evidences it |
| `CLAIM_EVIDENCE_MATRIX.tsv` | authored; each row names evidence file, producing script, commit and falsifier |
| `README.md`, `PROVENANCE.md`, `run.sh` | packaging |
| `env.lock` | `conda env export -p /home/borg/miniconda3/envs/retron_tradicional`, verbatim |

## Copied from git, hash-verified

`inputs/stage2_94a1a788/*` are the Stage-2 closed-state tables and decision records, copied with
`git show 94a1a78868d6039297c78b3fdcc047d633d6645e:<path>` because that commit is on `main` and is not
an ancestor of this branch. Each copy's sha256 is checked against the git blob in
`INPUT_PROVENANCE.tsv` on every run; a mismatch fires K1.
