# Notebook build scripts

The notebook is **generated**, not hand-edited. To change a cell, edit the relevant
`build_nb_part*.py` here and regenerate — do not edit the `.ipynb` directly, or the next
regeneration will overwrite it.

## Regenerate and execute

```bash
cd ARIS_OUTPUT/dbchar_workbench
export JUPYTER_PATH=$PWD/.venv/share/jupyter \
       IPYTHONDIR=${TMPDIR:-/tmp}/ipython \
       MPLCONFIGDIR=${TMPDIR:-/tmp}/mplconfig_dbchar

.venv/bin/python scripts/build_nb.py database_characterization_workbench.ipynb
find tables figures -type f -delete          # optional: force a cold recompute
.venv/bin/python -m nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=1800 \
    --ExecutePreprocessor.kernel_name=dbchar-workbench \
    database_characterization_workbench.ipynb
```

Cold run takes ~40 s. With `tables/` warm it is much faster (plots read cached TSVs).

## Which file holds which section

| file | notebook sections |
|---|---|
| `build_nb_part1.py`  | title, setup, DuckDB layer, canonical-value helpers |
| `build_nb_part1b.py` | 0.1 house population (`POP_RT_SEQ` / `POP_RT_CTX`), A0 |
| `build_nb_part2.py`  | A1–A3 corpus and redundancy |
| `build_nb_part2b.py` | A4 database attribution |
| `build_nb_part3.py`  | B1–B3 family landscape |
| `build_nb_part4.py`  | C1–C3 ncRNA landscape, D1–D4 geometry |
| `build_nb_part4b.py` | D5 strand agreement |
| `build_nb_part4c.py` | D6 joint geometry |
| `build_nb_part5f.py` | F0–F3 pairing topology |
| `build_nb_part5.py`  | E, G, H, I scaffolds, J open slot, session inventory |
| `build_nb_part6.py`  | K1–K2 dataset inventory |
| `build_nb_part7.py`  | L1–L7 thesis `\todo` resolutions |
| `build_nb_part8.py`  | M0–M3 operon visualisation |

Build order is set in `build_nb.py`. Helpers available in every cell: `Q(sql)`,
`cache(name, sql)`, `save(df, name)`, `canon(key)`, `gate_table(bundle, name)`,
`check(label, got, key=...)`, `savefig(fig, name)`; population constants `POP_RT_SEQ`,
`POP_RT_CTX`, `POP_RT`.
