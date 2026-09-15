#!/usr/bin/env python3
"""assemble - g2 rollup, derived-dataset registry and MANIFEST. Computes no measurement:
every value is a lookup or a sum over a named column of a landed table, and the registry
records identity (bytes + a deterministic content digest) of the derived datasets."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import pyarrow.parquet as pq

DERIVED_KEY = {                     # dataset -> the column its content digest is taken over
    "rt_records_v1.parquet": "record_key",
    "rt_loci_v1.parquet": "locus_key",
    "rt_physical_loci_v1.parquet": "physical_locus_key",
    "rt_exact_v1.parquet": "rt_seq_hash",
    "rt_ncrna_calls_v1.parquet": "ncrna_id",
    "rt_window_cds_v1.parquet": "gene_id",
    "rt_exact_v1.faa": "",
}
UNITS = {
    "g2_unit_ladder.tsv": ("a02_units.py", "named per row", "named per row in the denominator column"),
    "g2_ladder_by_source_database.tsv": ("a02_units.py", "records/loci/exact RTs", "distinct raw records of that source_database"),
    "g2_ladder_by_family_label.tsv": ("a02_units.py", "records/loci/exact RTs", "distinct raw records of that source file's family label"),
    "g2_ladder_by_population.tsv": ("a02_units.py", "records/loci/exact RTs", "distinct raw records of that population"),
    "g2_multiplicity.tsv": ("a02_units.py", "named per row", "named per row in the denominator column"),
    "g2_bt_status.tsv": ("a02_units.py", "records", "n_in_population column (and its frame-disambiguating half)"),
    "g2_bt_status_by_family.tsv": ("a02_units.py", "records", "RT-anchored records of that family label"),
    "g2_rt_cds_classes.tsv": ("a02_units.py", "records", "n_in_population column"),
    "g2_rt_cds_concordance.tsv": ("a02_units.py", "records", "RT-anchored records (3,059,700)"),
    "g2_cds_sequence_carrier.tsv": ("a02_units.py", "records", "RT-anchored records (3,059,700)"),
    "g2_eligibility.tsv": ("a02_units.py", "records", "n_records_in_population column"),
    "g2_eligible_unit_counts.tsv": ("a02_units.py", "records/loci/exact RTs/genomes", "the eligible subset named in the row"),
    "g2_window_qc.tsv": ("a02_units.py", "records", "n_records_total column: RT-anchored records"),
    "g2_inverted_window_profile.tsv": ("a02_units.py", "records/loci", "records with an inverted window"),
    "g2_rt_outside_window_profile.tsv": ("a02_units.py", "records/loci", "records whose RT is not inside its window"),
    "g2_ncrna_count_source.tsv": ("a02_units.py", "records", "RT-anchored records of that population"),
    "g2_ncrna_flag_reconciliation.tsv": ("a02_units.py", "records", "RT-anchored records (3,059,700)"),
    "g2_multi_stratum.tsv": ("a02_units.py", "records/loci/exact RTs", "POP-RT-MULTI records (9,012)"),
    "g2_multilabel_in_family_files.tsv": ("a02_units.py", "records/loci", "multi-label records inside single-family files"),
    "g2_cross_family_loci.tsv": ("a02_units.py", "loci", "loci whose records span more than one family label"),
    "g2_twin_evidence.tsv": ("a02_units.py", "physical loci/loci/records", "physical loci (2,475,684)"),
    "g2_duplicate_lines.tsv": ("a02_units.py", "records/groups/loci", "RT-anchored records (3,059,700)"),
    "g2_locus_conflicts.tsv": ("a02_units.py", "loci", "n_loci_total column: loci (2,847,312)"),
    "g2_second_counts.tsv": ("c05_reconcile.py", "records/loci/exact RTs", "named per row in scope; the routes count the same population"),
    "g2_prior_reconciliation.tsv": ("c05_reconcile.py", "named per row", "named per row in the scope columns"),
    "c04_positive_controls.tsv": ("c04_controls.py", "controls", "n/a - one pass/fail control per row on the synthetic fixture"),
    "g2_derived_registry.tsv": ("assemble.py", "datasets", "n/a - identity of the derived datasets; no rate"),
    "g2_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(16 << 20), b""):
            h.update(b)
    return h.hexdigest()


def content_digest(p: Path, key: str) -> tuple[str, int]:
    """Deterministic across parquet writer versions: sha256 over the key column in row order."""
    if not key:
        return "", 0
    t = pq.read_table(p, columns=[key])
    h = hashlib.sha256()
    for v in t[key].to_pylist():
        h.update((v if v is not None else "").encode())
        h.update(b"\n")
    return h.hexdigest(), t.num_rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T, D = W / "tables", W / "derived"

    reg = []
    for name, key in DERIVED_KEY.items():
        p = D / name
        if not p.exists():
            continue
        cd, rows = content_digest(p, key) if name.endswith(".parquet") else ("", 0)
        reg.append([name, p.stat().st_size, sha_file(p), rows, key, cd])
    with (T / "g2_derived_registry.tsv").open("w") as fh:
        fh.write("dataset\tbytes\tsha256\trows\tcontent_key\tcontent_digest_sha256\n")
        for r in reg:
            fh.write("\t".join(str(x) for x in r) + "\n")

    ladder = {x["unit"]: x["n"] for x in rd(T / "g2_unit_ladder.tsv")}
    elig = {(x["population"], x["eligibility_flag"], x["state"]): x["n_records"]
            for x in rd(T / "g2_eligibility.tsv") if x["state"] == "ELIGIBLE"}
    bt = rd(T / "g2_bt_status.tsv")
    cls = rd(T / "g2_rt_cds_classes.tsv")
    sc = rd(T / "g2_second_counts.tsv")
    pr = rd(T / "g2_prior_reconciliation.tsv")
    ctl = rd(T / "c04_positive_controls.tsv")
    tw = rd(T / "g2_twin_evidence.tsv")

    rows = [[k, v, "g2_unit_ladder.tsv"] for k, v in ladder.items()]
    for p in ("POP-RT-FAM", "POP-RT-MULTI"):
        ver = sum(int(x["n_records"]) for x in bt if x["population"] == p and x["verified"] == "True")
        tot = next(int(x["n_in_population"]) for x in bt if x["population"] == p)
        rows.append([f"bt_verified_records:{p}", f"{ver}/{tot}", "g2_bt_status.tsv"])
        verd = sum(int(x["n_records_frame_disambiguating"].split(".")[0]) for x in bt
                   if x["population"] == p and x["verified"] == "True")
        totd = next(int(x["n_in_population_frame_disambiguating"]) for x in bt if x["population"] == p)
        rows.append([f"bt_verified_records_frame_disambiguating:{p}", f"{verd}/{totd}", "g2_bt_status.tsv"])
        for f in ("elig_exact_rt", "elig_rt_coords", "elig_geometry"):
            rows.append([f"{f}:{p}", elig[(p, f, "ELIGIBLE")], "g2_eligibility.tsv"])
    rows.append(["records_without_rt_cds", sum(int(x["n_records"]) for x in cls
                                               if x["no_rt_cds_class"] != "has_rt_cds"), "g2_rt_cds_classes.tsv"])
    rows.append(["records_without_rt_cds_recoverable",
                 sum(int(x["n_records"]) for x in cls if x["no_rt_cds_class"].startswith("no_prodigal_call_bt_verified")),
                 "g2_rt_cds_classes.tsv"])
    for x in tw:
        rows.append([f"twin:{x['twin_evidence_class']}", x["n_physical_loci"], "g2_twin_evidence.tsv"])
    rows.append(["second_count_rows", len(sc), "g2_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for x in sc if x["agreement"] != "AGREE"),
                 "g2_second_counts.tsv"])
    for x in pr:
        rows.append([f"prior:{x['quantity']}:{x['prior_scope'][:40]}", x["verdict"], "g2_prior_reconciliation.tsv"])
    rows.append(["positive_controls", len(ctl), "c04_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for x in ctl if x["result"] != "PASS"),
                 "c04_positive_controls.tsv"])
    with (T / "g2_summary.tsv").open("w") as fh:
        fh.write("quantity\tvalue\tsource_table\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    present = sorted(p.name for p in T.glob("*.tsv"))
    missing = [n for n in present if n not in UNITS]
    if missing:
        print(f"assemble: tables with no MANIFEST row: {missing}", file=sys.stderr)
        return 1
    with (W / "MANIFEST.tsv").open("w") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for n in present:
            s, u, d = UNITS[n]
            fh.write(f"tables/{n}\tscripts/{s}\tsee run.sh: {s}\t{u}\t{d}\n")
    print(f"assemble: {len(rows)} summary rows, {len(present)} tables, {len(reg)} derived datasets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
