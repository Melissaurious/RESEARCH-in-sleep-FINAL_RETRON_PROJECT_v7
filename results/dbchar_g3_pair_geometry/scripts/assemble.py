#!/usr/bin/env python3
"""assemble - g3 rollup, derived registry and MANIFEST (tables AND figures). Computes nothing."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import pyarrow.parquet as pq

PLACEMENTS = "placements"
DERIVED = {"rt_ncrna_pairs_v1.parquet": "ncrna_id",
           "rt_ncrna_exact_pairs_v1.parquet": "rt_seq_hash",
           "rt_ncrna_exact_pair_recurrence_v1.parquet": "rt_seq_hash",
           "rt_ncrna_nonretron_candidates_v1.parquet": "ncrna_id"}
D = "denominator"
UNITS = {
    "g3_populations.tsv": ("a02_priors.py", PLACEMENTS, "all placements in rt_ncrna_pairs_v1"),
    "g3_ineligible_reasons.tsv": ("a02_priors.py", PLACEMENTS, "all placements"),
    "g3_zero_class_by_family.tsv": ("a02_priors.py", "loci", "loci of that family label"),
    "g3_zero_class_retron_by_database.tsv": ("a02_priors.py", "loci", "Retron loci of that source_database"),
    "g3_direction.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_distance_bins.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_distance_stats.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_distance_histogram.tsv": ("a02_priors.py", PLACEMENTS, "placements of that population with a defined signed distance"),
    "g3_cds_between_explicit.tsv": ("a02_priors.py", PLACEMENTS, "placements of that population/stratum"),
    "g3_same_strand.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_cds_between.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_overlap.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_multiplicity_class.tsv": ("a02_priors.py", PLACEMENTS, "n_in_population column"),
    "g3_calls_per_locus.tsv": ("a02_priors.py", "loci", "loci carrying >=1 geometry-eligible call"),
    "g3_pair_degree.tsv": ("a02_priors.py", "exact sequences", "the side named in the measure"),
    "g3_pair_view_sizes.tsv": ("a02_priors.py", "named per row", "named per row"),
    "g3_model_composition.tsv": ("a02_priors.py", PLACEMENTS, "CANONICAL placements of that model and family"),
    "g3_geometry_by_family.tsv": ("a02_priors.py", PLACEMENTS, "CANONICAL placements of that family label"),
    "g3_geometry_by_database.tsv": ("a02_priors.py", PLACEMENTS, "CANONICAL placements of that source_database"),
    "g3_shipped_field_qc.tsv": ("a02_priors.py", PLACEMENTS, "all placements, or the subset named in the measure"),
    "g3_atypical_catalogue.tsv": ("a02_priors.py", PLACEMENTS, "ELIGIBLE placements"),
    "g3_topology_degrees.tsv": ("a03_topology.py", "exact sequences", "the side named in the measure"),
    "g3_topology_components.tsv": ("a03_topology.py", "connected components", "components of the bipartite graph"),
    "g3_pair_recurrence.tsv": ("a03_topology.py", "exact pairs", "distinct exact pairs with a geometry-eligible placement"),
    "g3_same_rt_different_ncrna.tsv": ("a03_topology.py", "exact RTs", "exact RTs paired with >1 ncRNA sequence (top 500)"),
    "g3_same_ncrna_different_rt.tsv": ("a03_topology.py", "exact ncRNA sequences", "exact ncRNA sequences paired with >1 RT (top 500)"),
    "g3_ncrna_model_multiplicity.tsv": ("a03_topology.py", "exact ncRNA sequences", "exact ncRNA sequences with a geometry-eligible placement"),
    "g3_ncrna_boundary_variants.tsv": ("a03_topology.py", "pairs of distinct ncRNA sequences at one locus", "loci carrying >1 distinct exact ncRNA sequence"),
    "g3_shipped_field_semantics.tsv": ("a04_audits.py", PLACEMENTS, "geometry-eligible placements where the field is non-null"),
    "g3_shipped_field_structure.tsv": ("a04_audits.py", PLACEMENTS, "geometry-eligible placements where the field is non-null"),
    "g3_shipped_field_profile.tsv": ("a04_audits.py", PLACEMENTS, "all placements, or the non-null subset where stated"),
    "g3_shipped_field_presence_by_stratum.tsv": ("a04_audits.py", PLACEMENTS, "placements of that family and database"),
    "g3_nonretron_cm_placements.tsv": ("a04_audits.py", PLACEMENTS, "geometry-eligible placements at non-Retron-labelled RTs"),
    "g3_nonretron_vs_retron_geometry.tsv": ("a04_audits.py", PLACEMENTS, "the population named in the row"),
    "g3_downstream_mode_profile.tsv": ("a04_audits.py", PLACEMENTS, "CANONICAL downstream placements"),
    "g3_downstream_mode_window_signature.tsv": ("a04_audits.py", PLACEMENTS, "CANONICAL downstream placements"),
    "g3_downstream_mode_strata.tsv": ("a04_audits.py", PLACEMENTS, "CANONICAL downstream placements in that stratum"),
    "g3_downstream_mode_top_sequences.tsv": ("a04_audits.py", PLACEMENTS, "CANONICAL downstream placements within 150 bp of the median"),
    "g3_second_counts.tsv": ("c06_reconcile.py", "placements/records", "named per row; both routes count the same population"),
    "g3_prior_reconciliation.tsv": ("c06_reconcile.py", "named per row", "named per row"),
    "c04_positive_controls.tsv": ("c04_controls.py", "controls", "n/a - one pass/fail control per row on the synthetic fixture"),
    "fig01_distance_distribution.tsv": ("fig01_geometry.py", PLACEMENTS, "the population named in each row"),
    "fig02_cds_between.tsv": ("fig01_geometry.py", PLACEMENTS, "the population named in each row"),
    "fig03_direction_by_family.tsv": ("fig01_geometry.py", PLACEMENTS, "CANONICAL placements of that family label"),
    "g3_derived_registry.tsv": ("assemble.py", "datasets", "n/a - identity of the derived datasets; no rate"),
    "g3_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}
FIGS = {
    "fig01_distance_distribution": ("fig01_geometry.py", PLACEMENTS, "CANONICAL and ATYPICAL placements with a defined signed distance"),
    "fig02_cds_between": ("fig01_geometry.py", PLACEMENTS, "CANONICAL and ATYPICAL placements"),
    "fig03_direction_by_family": ("fig01_geometry.py", PLACEMENTS, "CANONICAL placements of that family label (n >= 30)"),
}


def rd(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T, DV, F = W / "tables", W / "derived", W / "figures"

    with (T / "g3_derived_registry.tsv").open("w") as fh:
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

    pops = {x["population"]: x["n_placements"] for x in rd(T / "g3_populations.tsv")}
    dirs = {(x["population"], x["direction"]): x["n_placements"] for x in rd(T / "g3_direction.tsv")}
    cds = {(x["population"], x["n_cds_between"]): x for x in rd(T / "g3_cds_between_explicit.tsv")
           if not x["stratum"]}
    deg = {x["measure"]: x["n"] for x in rd(T / "g3_topology_degrees.tsv")}
    comp = {x["shape"]: x["n_components"] for x in rd(T / "g3_topology_components.tsv")}
    dm = {x["measure"]: x["value"] for x in rd(T / "g3_downstream_mode_profile.tsv")}
    st = {x["measure"]: x for x in rd(T / "g3_shipped_field_structure.tsv")}
    sc = rd(T / "g3_second_counts.tsv")
    ctl = rd(T / "c04_positive_controls.tsv")
    nr = rd(T / "g3_nonretron_vs_retron_geometry.tsv")

    rows = [[f"population:{k}", v, "g3_populations.tsv"] for k, v in pops.items()]
    for d in ("upstream", "downstream", "overlapping"):
        rows.append([f"CANONICAL_direction:{d}", dirs.get(("CANONICAL", d), "0"), "g3_direction.tsv"])
    for k in ("0", "1", "2", "3", ">3"):
        rows.append([f"CANONICAL_cds_between:{k}", cds[("CANONICAL", k)]["n_placements"],
                     "g3_cds_between_explicit.tsv"])
    for k, v in deg.items():
        rows.append([f"topology:{k}", v, "g3_topology_degrees.tsv"])
    for k, v in comp.items():
        rows.append([f"components:{k}", v, "g3_topology_components.tsv"])
    for x in nr:
        rows.append([f"geometry:{x['population']}:pct_upstream", x["pct_upstream"],
                     "g3_nonretron_vs_retron_geometry.tsv"])
    rows.append(["downstream_mode_median_bp", dm["median_signed_distance_bp"],
                 "g3_downstream_mode_profile.tsv"])
    rows.append(["downstream_mode_distinct_exact_ncrna", dm["distinct_exact_ncrna_in_the_mode"],
                 "g3_downstream_mode_profile.tsv"])
    rows.append(["shipped_field_best_coordinate_frame_match",
                 st["field == (intergenic_region_index - 1) - (rt_start - win_start)"]["value"],
                 "g3_shipped_field_structure.tsv"])
    rows.append(["second_count_rows", len(sc), "g3_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for x in sc if x["agreement"] != "AGREE"),
                 "g3_second_counts.tsv"])
    rows.append(["positive_controls", len(ctl), "c04_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for x in ctl if x["result"] != "PASS"),
                 "c04_positive_controls.tsv"])
    with (T / "g3_summary.tsv").open("w") as fh:
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
