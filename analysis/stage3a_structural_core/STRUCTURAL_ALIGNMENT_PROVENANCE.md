# Stage 3A — structural-alignment and secondary-structure provenance

## Foldseek — pinned, recorded, rerun for this stage

No historical foldseek product was reused as evidence.

| | |
|---|---|
| binary | `/home/borg/miniconda3/envs/esmologs/bin/foldseek` |
| version | **`10.941cd33`** (matches the Ibex module `foldseek/10-941cd33`) |
| sha256 | `ce5f08d8f1e15598f618ac6155a756608fe0939b9534e773b5b5472a74acb842` |
| command | `foldseek easy-search <chains> <chains> <out> <tmp> --alignment-type 1 -e inf --exhaustive-search 1 --tmscore-threshold 0.0 --max-seqs 200 --format-output query,target,qstart,qend,tstart,tend,qaln,taln,alntmscore,lddt,alnlen -v 1` |
| input | 62 single-chain coordinate extracts, **author residue numbering preserved**, ligands and waters removed |
| output | 3,844 alignment rows = 62 × 62, complete all-vs-all |

The unversioned `/home/borg/foldseek/bin/foldseek` (commit `d609cff8`) remains `DO-NOT-USE`.

## FoldMason — not used in this gate

`foldmason 4.dd3c235` is installed and the historical MSAs exist, but Stage 3A g2 needed pairwise
superposition only. Nothing from the historical FoldMason products entered this stage.

## Secondary structure — mkdssp is BROKEN in this environment

`mkdssp 4.5.5` from `retron_tradicional` **fails on every input tried**: on valid mmCIF it reports
`basic_filebuf::underflow error reading the file: Is a directory` for a plain file, and on a
gemmi-written PDB it reports `parse error at line 1: This file does not seem to be an mmCIF file`.
Setting `LIBCIFPP_DATA_DIR` and copying inputs locally did not help. It was not used.

Two independent assignments were implemented directly instead (`scripts/sse.py`), both label-blind
and sequence-blind:

* **DSSP-KS** — Kabsch & Sander backbone hydrogen-bond energy, 3-/4-/5-turns, parallel and
  antiparallel bridges, collapsed to H/E/C.
* **P-SEA** — Labesse CA-only geometry: d(i,i+2), d(i,i+3), d(i,i+4), pseudo-angle and
  pseudo-dihedral, with run-length gating.

### DSSP-KS validated against the historical mkdssp 4.5.5 output

The 26 historical `.dssp` files in `D_instrument/cache/d21_sse/` were used **as an instrument check
only** — they carry no boundary, motif or label.

| | |
|---|---|
| chains compared | 26 |
| **median 3-state agreement** | **0.9449** |
| median helix recall | **1.000** |
| median strand recall | **0.701** |
| chains ≥ 0.92 agreement | 25 of 26 (`PDB_7R06_1` at 0.742 is the exception) |

**Stated limitation:** this implementation is conservative on β — it recovers about 70 % of the
strand residues mkdssp calls, while never missing helix. Any β-dependent criterion inherits that
conservatism and must carry it.

Two join defects were found and fixed during validation, and both would have produced a false
failure of the instrument: the historical `.dssp` files are numbered differently from the backbone
extracts (fixed by positional alignment), and they were computed on the **full deposition**, so the
chain column must be honoured or residues from other chains collide on residue number.
