# Pre-repair smoke snapshot — the "BEFORE" half of `../g4b_repair_no_science_change.tsv`

These are the smoke products as produced by the g4b packaging **before** the five repairs
required by the independent packaging review (R1–R5). They carry the superseded instrument
identifier `rtmap-1.0.0/46aa95cb0e197b40`.

They are landed for one reason: the round-2 reviewer could not independently recompute the
before/after column diff, because only the executor's summary of it existed. With these files
present, anyone can:

```bash
python3 - <<'PY'
def load(p):
    f = open(p); cols = f.readline().rstrip("\n").split("\t")
    return cols, [l.rstrip("\n").split("\t") for l in f]
for name in ("states", "sequences", "failures"):
    ca, a = load(f"tables/pre_repair_snapshot/smoke.{name}.tsv")
    cb, b = load(f"tables/smoke_{name}.tsv")
    assert ca == cb, name
    diff = {ca[i] for x, y in zip(a, b) for i in range(len(x)) if x[i] != y[i]}
    print(f"{name}: {len(a)} rows, columns that differ: {sorted(diff)}")
PY
```

Expected output: `mapper_version` only, for `states` and `sequences`; `mapper_version` and the
free-text `detail` for `failures`.

**These files are superseded and are not production outputs.** They are audit history. The
current products are `../smoke_states.tsv`, `../smoke_sequences.tsv`, `../smoke_failures.tsv`.
