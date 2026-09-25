#!/usr/bin/env python
"""embed-g0/a08 - assemble results/embed_g0_input_contract/ from this task's scratch.

The gate is LIGHT: it settles the INPUT CONTRACT, not a scientific claim. It lands because it
produces a registered canonical dataset (rt_ncrna_oriented_v1) and a frozen batching rule, and
neither may live only in gitignored scratch.

INPUTS.tsv hashes the derived-layer inputs directly. The 18 raw corpus files are NOT re-hashed
here - their identity is pinned by dbchar_g1 (record-manifest sha256
8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00) and re-hashing 21 GB to
restate a pin that already exists would be duplication, not verification.
"""
from __future__ import annotations
import hashlib, shutil, sys
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[1]
BUNDLE = ROOT / "results" / "embed_g0_input_contract"
CANON = Path("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/data/derived")

DERIVED_INPUTS = ["rt_ncrna_exact_pairs_v1.parquet", "rt_ncrna_pairs_v1.parquet",
                  "rt_ncrna_exact_pair_recurrence_v1.parquet", "rt_exact_v1.parquet",
                  "rt_family_baseline_v1.parquet", "ncrna_family_baseline_v1.parquet"]

# artifact -> (producing script, unit, denominator)
UNITS = {
    "g0_views.tsv": ("a01_universe.py", "exact RT-ncRNA pair", "the view named in each row"),
    "g0_length_distributions.tsv": ("a01_universe.py", "unique exact sequence", "29,192 RT / 16,458 ncRNA"),
    "g0_length_strata.tsv": ("a01_universe.py", "unique exact sequence", "the denominator column"),
    "g0_multiplicity.tsv": ("a01_universe.py", "pair / sequence", "30,924 pairs; 29,192 RT; 16,458 ncRNA"),
    "g0_recurrence_class.tsv": ("a01_universe.py", "exact RT-ncRNA pair", "30,924 PAIR-ELIG pairs"),
    "g0_detection_model.tsv": ("a01_universe.py", "exact RT-ncRNA pair", "30,924 PAIR-ELIG pairs"),
    "g0_rt_family.tsv": ("a01_universe.py", "exact RT-ncRNA pair", "30,924 PAIR-ELIG pairs"),
    "g0_completeness.tsv": ("a01_universe.py", "exact RT-ncRNA pair", "30,924 PAIR-ELIG pairs"),
    "g0_split_keys.tsv": ("a01_universe.py", "grouping key", "n/a - cardinalities, no rate"),
    "g0_storage.tsv": ("a01_universe.py", "array row", "n/a - storage, no rate"),
    "g0_ncrna_source_files.tsv": ("a01_universe.py", "unique ncRNA hash", "16,458 ncRNA hashes"),
    "g0_ncrna_fasta_manifest.tsv": ("a02_ncrna_fasta.py", "file", "n/a - identity, no rate"),
    "g0_component_structure.tsv": ("a05_components.py", "connected component", "30,924 pairs per row"),
    "g0_component_top_sizes.tsv": ("a05_components.py", "connected component", "30,924 pairs"),
    "g0_esmc_context.tsv": ("a06_pilot_esmc.py", "exact RT", "n/a - the 3 longest, one row each"),
    "g0_esmc_pilot.json": ("a06_pilot_esmc.py", "pilot run", "n/a - harness measurement"),
    "g0_rinalmo_pilot.json": ("a07_pilot_rinalmo.py", "pilot run", "n/a - harness measurement"),
}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    for d in ("scripts", "tables"):
        (BUNDLE / d).mkdir(parents=True, exist_ok=True)
    for s in sorted((TASK / "scripts").iterdir()):
        if s.name != "a08_assemble.py":
            shutil.copy2(s, BUNDLE / "scripts" / s.name)
    shutil.copy2(TASK / "scripts" / "a08_assemble.py", BUNDLE / "scripts" / "a08_assemble.py")
    # g0_ncrna_fetch_plan.tsv (1.9 MB) is NOT landed: every column in it is already carried
    # per-hash by data/derived/rt_ncrna_oriented_v1.parquet, and a01 regenerates it in ~15 s.
    # Landing it would put a duplicate of a registered dataset into git (CLAUDE.md, results/).
    skip = {"g0_ncrna_fetch_plan.tsv"}
    for t in sorted((TASK / "tables").iterdir()):
        if t.name in skip:
            continue
        shutil.copy2(t, BUNDLE / "tables" / t.name)
    for t in skip:
        (BUNDLE / "tables" / t).unlink(missing_ok=True)

    rows = ["path\tsha256\tbytes\trole"]
    for n in DERIVED_INPUTS:
        p = CANON / n
        rows.append(f"{p}\t{sha(p)}\t{p.stat().st_size}\tFROZEN canonical derived input")
    for n in ("rt_ncrna_oriented_v1.fna", "rt_ncrna_oriented_v1.parquet"):
        p = ROOT / "data" / "derived" / n
        rows.append(f"data/derived/{n}\t{sha(p)}\t{p.stat().st_size}\tproduced by this gate")
    rows.append("/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/json_files_input_june/"
                "\t8e9b7999954b460d2bdfc558c605d26610d58e6901788f61720e11eafdc41d00\t81007695609"
                "\tRAW corpus - identity pinned by dbchar_g1 record manifest, not re-hashed here")
    (BUNDLE / "INPUTS.tsv").write_text("\n".join(rows) + "\n")

    man = ["artifact\tscript\tunit\tdenominator\tsha256"]
    out = ["path\tsha256\tbytes"]
    for t in sorted((BUNDLE / "tables").iterdir()):
        s, u, d = UNITS.get(t.name, ("?", "?", "?"))
        man.append(f"tables/{t.name}\tscripts/{s}\t{u}\t{d}\t{sha(t)}")
    for s in sorted((BUNDLE / "scripts").iterdir()):
        out.append(f"scripts/{s.name}\t{sha(s)}\t{s.stat().st_size}")
    for t in sorted((BUNDLE / "tables").iterdir()):
        out.append(f"tables/{t.name}\t{sha(t)}\t{t.stat().st_size}")
    (BUNDLE / "MANIFEST.tsv").write_text("\n".join(man) + "\n")
    (BUNDLE / "OUTPUTS.tsv").write_text("\n".join(out) + "\n")

    unknown = [r for r in man[1:] if "\t?\t" in r]
    if unknown:
        raise AssertionError(f"{len(unknown)} artifacts have no declared unit/denominator")
    print(f"assembled {BUNDLE}")
    print(f"  {len(list((BUNDLE/'scripts').iterdir()))} scripts, "
          f"{len(list((BUNDLE/'tables').iterdir()))} tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
