#!/usr/bin/env python3
"""assemble - g4 rollup, derived registry and MANIFEST. Computes nothing."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import pyarrow.parquet as pq

EX = "exact RT sequences"
NC = "exact ncRNA sequences"
DERIVED = {"rt_family_baseline_v1.parquet": "rt_seq_hash",
           "ncrna_family_baseline_v1.parquet": "nc_seq_hash",
           "multi_hmm_evidence_v1.parquet": "rt_seq_hash"}
UNITS = {
    "g4_views.tsv": ("b01_baseline.py", EX, "exact RT sequences in the corpus (501,561)"),
    "g4_exact_rt_per_family_label.tsv": ("b01_baseline.py", EX, "distinct RT sequences in that source file, over all records"),
    "g4_rt_length_by_family.tsv": ("b01_baseline.py", EX, "V-RT-SINGLE exact RTs of that family label"),
    "g4_rt_length_outlier_rates.tsv": ("b01_baseline.py", EX, "V-RT-SINGLE exact RTs of that family label"),
    "g4_rt_length_named_outliers.tsv": ("b01_baseline.py", EX, "the 20 smallest outliers per family"),
    "g4_completeness_by_family.tsv": ("b01_baseline.py", EX, "V-RT-SINGLE exact RTs of that family label"),
    "g4_completeness_states_raw.tsv": ("b01_baseline.py", EX, "V-RT-SINGLE exact RTs"),
    "g4_family_composition.tsv": ("b01_baseline.py", EX, "V-RT-SINGLE exact RTs of that family label"),
    "g4_ncrna_length_by_model.tsv": ("b01_baseline.py", NC, "exact ncRNA sequences called by that model"),
    "g4_ncrna_model_by_family.tsv": ("b01_baseline.py", NC, "exact ncRNA sequences of that family label and model"),
    "g4_ncrna_structure_coverage.tsv": ("b01_baseline.py", NC, "exact ncRNA sequences with an eligible placement"),
    "g4_multi_hmm_positive_control.tsv": ("h02_multi_hmm.py", EX, "a seeded random sample of 2,000 V-RT-SINGLE exact RTs"),
    "g4_multi_hmm_control_by_family.tsv": ("h02_multi_hmm.py", EX, "sampled control exact RTs of that family"),
    "g4_multi_hmm_profile.tsv": ("h02_multi_hmm.py", EX, "V-RT-MULTI exact RTs (7,593)"),
    "g4_multi_hmm_margin_comparison.tsv": ("h02_multi_hmm.py", EX, "the population named in the row"),
    "g4_multi_label_sets_vs_hmm.tsv": ("h02_multi_hmm.py", EX, "V-RT-MULTI exact RTs with that label set"),
    "g4_second_counts.tsv": (" c05_reconcile.py".strip(), EX, "named per row; both routes count the same population"),
    "g4_prior_reconciliation.tsv": ("c05_reconcile.py", EX, "that family's exact RTs in each project"),
    "c04_positive_controls.tsv": ("c04_controls.py", "controls", "n/a - one pass/fail control per row on the synthetic fixture"),
    "fig01_rt_length_by_family.tsv": ("fig01_family.py", EX, "V-RT-SINGLE exact RTs of that family (top 25)"),
    "fig02_multi_label_margins.tsv": ("fig01_family.py", EX, "the population named in the row"),
    "g4_derived_registry.tsv": ("assemble.py", "datasets", "n/a - identity of the derived datasets; no rate"),
    "g4_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}
FIGS = {"fig01_rt_length_by_family": ("fig01_family.py", EX, "V-RT-SINGLE exact RTs of that family (top 25 by n)"),
        "fig02_multi_label_margins": ("fig01_family.py", EX, "the population named on the axis")}


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T, DV, F = W / "tables", W / "derived", W / "figures"

    with (T / "g4_derived_registry.tsv").open("w") as fh:
        fh.write("dataset\tbytes\tsha256\trows\tcontent_key\tcontent_digest_sha256\n")
        for name, key in DERIVED.items():
            p = DV / name
            if not p.exists():
                continue
            h = hashlib.sha256()
            with p.open("rb") as f2:
                for b in iter(lambda: f2.read(16 << 20), b""):
                    h.update(b)
            t = pq.read_table(p, columns=[key])
            cd = hashlib.sha256()
            for v in t[key].to_pylist():
                cd.update((v or "").encode() + b"\n")
            fh.write(f"{name}\t{p.stat().st_size}\t{h.hexdigest()}\t{t.num_rows}\t{key}\t{cd.hexdigest()}\n")

    views = {x["view"]: x["n_exact_rt"] for x in rd(T / "g4_views.tsv")}
    ctrl = {x["measure"]: x for x in rd(T / "g4_multi_hmm_positive_control.tsv")}
    prof = {x["measure"]: x for x in rd(T / "g4_multi_hmm_profile.tsv")}
    marg = rd(T / "g4_multi_hmm_margin_comparison.tsv")
    pr = rd(T / "g4_prior_reconciliation.tsv")
    sc = rd(T / "g4_second_counts.tsv")
    cc = rd(T / "c04_positive_controls.tsv")
    ln = rd(T / "g4_rt_length_by_family.tsv")
    comp = rd(T / "g4_completeness_by_family.tsv")

    rows = [[f"view:{k}", v, "g4_views.tsv"] for k, v in views.items()]
    for r in ln[:6]:
        rows.append([f"rt_length_median:{r['family_label']}", r["median"], "g4_rt_length_by_family.tsv"])
    for r in marg:
        rows.append([f"multi_hmm_median_margin_bits:{r['population']}", r["median_margin_bits"],
                     "g4_multi_hmm_margin_comparison.tsv"])
    rows.append(["multi_hmm_control_best_equals_label_pct",
                 ctrl["best-scoring profile family equals the file label"]["pct"],
                 "g4_multi_hmm_positive_control.tsv"])
    rows.append(["multi_best_family_in_labels_pct",
                 prof["best-scoring family is among the record's labels"]["pct"],
                 "g4_multi_hmm_profile.tsv"])
    retron_complete = [x for x in comp if x["family_label"] == "Retron"
                       and x["completeness_class"] == "all_complete"]
    if retron_complete:
        rows.append(["Retron_all_complete_exact_rt", retron_complete[0]["n_exact_rt"],
                     "g4_completeness_by_family.tsv"])
    rows.append(["prior_families_CONFIRMED", sum(1 for x in pr if x["verdict"] == "CONFIRMED"),
                 "g4_prior_reconciliation.tsv"])
    rows.append(["prior_families_CHANGED", sum(1 for x in pr if x["verdict"] == "CHANGED"),
                 "g4_prior_reconciliation.tsv"])
    rows.append(["prior_families_UNRESOLVED", sum(1 for x in pr if x["verdict"] == "UNRESOLVED"),
                 "g4_prior_reconciliation.tsv"])
    rows.append(["second_count_rows", len(sc), "g4_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for x in sc if x["agreement"] != "AGREE"),
                 "g4_second_counts.tsv"])
    rows.append(["positive_controls", len(cc), "c04_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for x in cc if x["result"] != "PASS"),
                 "c04_positive_controls.tsv"])
    with (T / "g4_summary.tsv").open("w") as fh:
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
        for n in sorted(FIGS):
            s, u, d = FIGS[n]
            for ext in ("png", "svg"):
                if (F / f"{n}.{ext}").exists():
                    fh.write(f"figures/{n}.{ext}\tscripts/{s}\tsee run.sh: {s}\t{u}\t{d}\n")
    print(f"assemble: {len(rows)} summary rows, {len(present)} tables, {len(FIGS)} figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
