#!/usr/bin/env python3
"""assemble - g2b rollup, derived registry and MANIFEST. Computes no measurement."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import pyarrow.parquet as pq

UNITS = {
    "g2b_recovery_classes.tsv": ("r01_recovery.py", "records", "n_records_without_rt_cds column: the 31,504 RT-anchored records with no marked RT CDS"),
    "g2b_recovered_evidence.tsv": ("r01_recovery.py", "records", "n_recovered column: RECOVERED records"),
    "g2b_recovered_overlap_partial_states.tsv": ("r01_recovery.py", "records", "n_recovered column: RECOVERED records"),
    "g2b_representation_classes.tsv": ("r01_recovery.py", "records", "n_sequence_only column: SEQUENCE_ONLY records"),
    "g2b_sequence_only_by_database.tsv": ("r01_recovery.py", "records", "SEQUENCE_ONLY records of that source_database"),
    "g2b_by_family.tsv": ("r01_recovery.py", "records", "records with no marked RT CDS in that family file"),
    "g2b_independent_translation_check.tsv": ("r01_recovery.py", "records", "the seeded sample named in n_sampled"),
    "g2b_second_counts.tsv": ("c04_reconcile.py", "records", "named per row; the routes count the same population"),
    "c03_positive_controls.tsv": ("c03_controls.py", "controls", "n/a - one pass/fail control per row on the synthetic fixture"),
    "g2b_derived_registry.tsv": ("assemble.py", "datasets", "n/a - identity of the derived dataset; no rate"),
    "g2b_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T, D = W / "tables", W / "derived"

    p = D / "rt_cds_recovery_v1.parquet"
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(16 << 20), b""):
            h.update(b)
    t = pq.read_table(p, columns=["record_key"])
    cd = hashlib.sha256()
    for v in t["record_key"].to_pylist():
        cd.update((v or "").encode() + b"\n")
    with (T / "g2b_derived_registry.tsv").open("w") as fh:
        fh.write("dataset\tbytes\tsha256\trows\tcontent_key\tcontent_digest_sha256\n")
        fh.write(f"rt_cds_recovery_v1.parquet\t{p.stat().st_size}\t{h.hexdigest()}\t{t.num_rows}\t"
                 f"record_key\t{cd.hexdigest()}\n")

    cls = rd(T / "g2b_recovery_classes.tsv")
    rep = rd(T / "g2b_representation_classes.tsv")
    ind = rd(T / "g2b_independent_translation_check.tsv")
    sec = rd(T / "g2b_second_counts.tsv")
    ctl = rd(T / "c03_positive_controls.tsv")
    rows = []
    for st in ("RECOVERED", "SEQUENCE_ONLY", "ILL_POSED"):
        rows.append([f"recovery_state:{st}", sum(int(x["n_records"]) for x in cls
                                                 if x["recovery_state"] == st), "g2b_recovery_classes.tsv"])
    for x in cls:
        rows.append([f"class:{x['no_rt_cds_class']}", x["n_records"], "g2b_recovery_classes.tsv"])
    for x in rep:
        rows.append([f"representation:{x['representation_class']}", x["n_records"],
                     "g2b_representation_classes.tsv"])
    for x in ind:
        rows.append([f"independent_translation:{x['population']}",
                     f"{x['n_agree_with_stored_protein']}/{x['n_sampled']} agree, "
                     f"{x['n_agree_after_a_one_base_frame_shift(NEGATIVE CONTROL, must be ~0)']} after a frame shift",
                     "g2b_independent_translation_check.tsv"])
    rows.append(["records_keeping_a_usable_RT_sequence",
                 sum(int(x["n_elig_exact_rt"]) for x in cls), "g2b_recovery_classes.tsv"])
    rows.append(["records_with_verified_coordinates",
                 sum(int(x["n_elig_rt_coords"]) for x in cls), "g2b_recovery_classes.tsv"])
    rows.append(["second_count_rows", len(sec), "g2b_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for x in sec if x["agreement"] != "AGREE"),
                 "g2b_second_counts.tsv"])
    rows.append(["positive_controls", len(ctl), "c03_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for x in ctl if x["result"] != "PASS"),
                 "c03_positive_controls.tsv"])
    with (T / "g2b_summary.tsv").open("w") as fh:
        fh.write("quantity\tvalue\tsource_table\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    present = sorted(x.name for x in T.glob("*.tsv"))
    missing = [n for n in present if n not in UNITS]
    if missing:
        print(f"assemble: tables with no MANIFEST row: {missing}", file=sys.stderr)
        return 1
    with (W / "MANIFEST.tsv").open("w") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for n in present:
            s, u, d = UNITS[n]
            fh.write(f"tables/{n}\tscripts/{s}\tsee run.sh: {s}\t{u}\t{d}\n")
    print(f"assemble: {len(rows)} summary rows, {len(present)} tables")
    return 0


if __name__ == "__main__":
    sys.exit(main())
