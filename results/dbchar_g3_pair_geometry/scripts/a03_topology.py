#!/usr/bin/env python3
"""a03 - the bipartite topology of exact RT <-> exact ncRNA pairing.

The pair view is a bipartite graph: exact RT protein sequences on one side, exact ncRNA
sequences on the other, an edge where a geometry-eligible placement puts them at one locus.
This gate measures the SHAPE of that graph and what explains a repeated edge.

⚠️ Declared caution, before any number is read: two exact ncRNA sequences that differ only in
where the covariance model cut the boundary are two nodes here and one molecule in biology.
Boundary-variant edges are therefore measured and reported separately, and no count in this
gate may be read as "distinct ncRNA families".
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd


def w(path: Path, df: pd.DataFrame) -> None:
    df.to_csv(path, sep="\t", index=False)
    print(f"  {path.name}: {len(df)} rows")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    W = Path(a.work)
    T = W / "tables"
    p = pd.read_parquet(W / "derived" / "rt_ncrna_pairs_v1.parquet")
    ex = pd.read_parquet(W / "derived" / "rt_ncrna_exact_pairs_v1.parquet")
    e = p[p.geometry_eligible]

    # ---- 1 · degrees on each side ----------------------------------------------------
    deg_rt = ex.groupby("rt_seq_hash").nc_seq_hash.nunique()
    deg_nc = ex.groupby("nc_seq_hash").rt_seq_hash.nunique()
    w(T / "g3_topology_degrees.tsv", pd.DataFrame([
        ["exact_RTs_in_the_pair_view", len(deg_rt), ""],
        ["exact_RTs_paired_with_exactly_one_ncRNA_sequence", int((deg_rt == 1).sum()),
         round(100 * (deg_rt == 1).mean(), 4)],
        ["exact_RTs_paired_with_more_than_one_ncRNA_sequence", int((deg_rt > 1).sum()),
         round(100 * (deg_rt > 1).mean(), 4)],
        ["max_ncRNA_sequences_on_one_exact_RT", int(deg_rt.max()), ""],
        ["exact_ncRNA_sequences_in_the_pair_view", len(deg_nc), ""],
        ["exact_ncRNA_sequences_paired_with_exactly_one_RT", int((deg_nc == 1).sum()),
         round(100 * (deg_nc == 1).mean(), 4)],
        ["exact_ncRNA_sequences_paired_with_more_than_one_RT", int((deg_nc > 1).sum()),
         round(100 * (deg_nc > 1).mean(), 4)],
        ["max_exact_RTs_on_one_ncRNA_sequence", int(deg_nc.max()), ""],
    ], columns=["measure", "n", "pct_of_that_side"]).assign(
        unit="exact sequences", denominator="the side named in the measure, in the exact-pair view"))

    # ---- 2 · connected components, classified ----------------------------------------
    g = nx.Graph()
    g.add_edges_from(zip("R" + ex.rt_seq_hash, "N" + ex.nc_seq_hash))
    rows = []
    comp_of = {}
    for i, comp in enumerate(nx.connected_components(g)):
        nr = sum(1 for x in comp if x[0] == "R")
        nn = len(comp) - nr
        shape = ("1:1" if nr == 1 and nn == 1 else
                 "1:many" if nr == 1 else "many:1" if nn == 1 else "many:many")
        rows.append([i, shape, nr, nn])
        for x in comp:
            comp_of[x] = i
    comps = pd.DataFrame(rows, columns=["component", "shape", "n_exact_rt", "n_exact_ncrna"])
    w(T / "g3_topology_components.tsv", comps.groupby("shape").agg(
        n_components=("component", "size"), n_exact_rt=("n_exact_rt", "sum"),
        n_exact_ncrna=("n_exact_ncrna", "sum"),
        max_rt_in_a_component=("n_exact_rt", "max"),
        max_ncrna_in_a_component=("n_exact_ncrna", "max")).reset_index().assign(
            n_components_total=len(comps), unit="connected components",
            denominator="components of the exact RT-ncRNA bipartite graph"))
    ex["component"] = ("R" + ex.rt_seq_hash).map(comp_of)
    ex["component_shape"] = ex.component.map(comps.set_index("component").shape.to_dict()
                                             if False else dict(zip(comps.component, comps.shape)))

    # ---- 3 · what explains a REPEATED pair? ------------------------------------------
    # For each exact pair seen at more than one placement, is the recurrence explained by the
    # same locus mined twice, the same genome, the same species, or by broader taxa?
    k = e.groupby(["rt_seq_hash", "nc_seq_hash"]).agg(
        n_placements=("ncrna_id", "size"), n_loci=("locus_key", "nunique"),
        n_physical_loci=("physical_locus_key", "nunique"), n_genomes=("genome_id_norm", "nunique"),
        n_species=("tax_species", "nunique"), n_databases=("source_database", "nunique"),
        n_families=("file_label", "nunique"), n_models=("detection_model", "nunique")).reset_index()

    def explain(r) -> str:
        if r.n_placements == 1:
            return "single_placement"
        if r.n_physical_loci == 1:
            return ("one_physical_locus_multiple_database_copies" if r.n_databases > 1
                    else "one_physical_locus_multiple_records")
        if r.n_genomes == 1:
            return "one_genome_multiple_loci"
        if r.n_species == 1:
            return "one_species_multiple_genomes"
        return "multiple_species"
    k["recurrence_class"] = [explain(r) for r in k.itertuples()]
    w(T / "g3_pair_recurrence.tsv", k.groupby("recurrence_class").agg(
        n_exact_pairs=("n_placements", "size"), n_placements=("n_placements", "sum"),
        median_placements_per_pair=("n_placements", "median"),
        max_placements_per_pair=("n_placements", "max"),
        median_species_per_pair=("n_species", "median")).reset_index().assign(
            n_exact_pairs_total=len(k), unit="exact pairs",
            denominator="distinct (exact RT, exact ncRNA) pairs with a geometry-eligible placement"))
    k.to_parquet(W / "derived" / "rt_ncrna_exact_pair_recurrence_v1.parquet", index=False,
                 compression="zstd")

    # ---- 4 · the two asymmetric cases, kept with their evidence -----------------------
    multi_nc = set(deg_rt.index[deg_rt > 1])
    multi_rt = set(deg_nc.index[deg_nc > 1])
    same_rt = e[e.rt_seq_hash.isin(multi_nc)]
    same_nc = e[e.nc_seq_hash.isin(multi_rt)]
    w(T / "g3_same_rt_different_ncrna.tsv", same_rt.groupby("rt_seq_hash").agg(
        n_distinct_ncrna=("nc_seq_hash", "nunique"), n_placements=("ncrna_id", "size"),
        n_loci=("locus_key", "nunique"), n_genomes=("genome_id_norm", "nunique"),
        n_species=("tax_species", "nunique"), n_models=("detection_model", "nunique"),
        n_databases=("source_database", "nunique"),
        median_abs_distance_bp=("signed_distance_bp", lambda s: s.abs().median())).reset_index()
      .sort_values("n_distinct_ncrna", ascending=False).head(500).assign(
          n_such_rts=len(multi_nc), unit="exact RTs",
          denominator="exact RTs paired with >1 ncRNA sequence (top 500 by degree)"))
    w(T / "g3_same_ncrna_different_rt.tsv", same_nc.groupby("nc_seq_hash").agg(
        n_distinct_rt=("rt_seq_hash", "nunique"), n_placements=("ncrna_id", "size"),
        n_loci=("locus_key", "nunique"), n_genomes=("genome_id_norm", "nunique"),
        n_species=("tax_species", "nunique"), n_families=("file_label", "nunique"),
        n_databases=("source_database", "nunique"), detection_model=("detection_model", "first"),
        median_abs_distance_bp=("signed_distance_bp", lambda s: s.abs().median())).reset_index()
      .sort_values("n_distinct_rt", ascending=False).head(500).assign(
          n_such_ncrnas=len(multi_rt), unit="exact ncRNA sequences",
          denominator="exact ncRNA sequences paired with >1 exact RT (top 500 by degree)"))

    # ---- 4b · is any ncRNA sequence called by more than one covariance model? ---------
    # The prior project reported this as zero and warned the zero is produced by the
    # pipeline's winner-take-all model selection, not by CM specificity. Measured here first.
    mm = e.groupby("nc_seq_hash").detection_model.nunique()
    w(T / "g3_ncrna_model_multiplicity.tsv", pd.DataFrame([
        ["exact_ncRNA_sequences", len(mm), ""],
        ["called_by_exactly_one_model", int((mm == 1).sum()), round(100 * (mm == 1).mean(), 4)],
        ["called_by_more_than_one_model", int((mm > 1).sum()), round(100 * (mm > 1).mean(), 4)],
        ["max_models_on_one_sequence", int(mm.max()), ""],
    ], columns=["measure", "n", "pct"]).assign(
        unit="exact ncRNA sequences", denominator="exact ncRNA sequences with a geometry-eligible placement",
        caveat="one model per call is imposed by the pipeline's selection step; this is not CM specificity"))

    # ---- 5 · boundary variants: the caution, measured --------------------------------
    # Two ncRNA calls at ONE locus whose intervals overlap are boundary variants of one call,
    # not two molecules. This is the rate at which "distinct exact ncRNA sequence" can mean
    # "same molecule, different cut".
    m = e[e.n_distinct_ncrna_seq_at_locus > 1][
        ["locus_key", "nc_seq_hash", "nc_start", "nc_end", "detection_model"]].copy()
    pairs = m.merge(m, on="locus_key", suffixes=("_a", "_b"))
    pairs = pairs[pairs.nc_seq_hash_a < pairs.nc_seq_hash_b]
    if len(pairs):
        ov = (np.minimum(pairs.nc_end_a, pairs.nc_end_b)
              - np.maximum(pairs.nc_start_a, pairs.nc_start_b) + 1)
        pairs["overlap_bp"] = np.maximum(0, ov)
        pairs["same_model"] = pairs.detection_model_a == pairs.detection_model_b
        pairs["class"] = np.where(pairs.overlap_bp > 0, "overlapping_intervals_boundary_variant",
                                  "disjoint_intervals_two_distinct_calls")
        w(T / "g3_ncrna_boundary_variants.tsv", pairs.groupby(["class", "same_model"]).agg(
            n_sequence_pairs=("locus_key", "size"), n_loci=("locus_key", "nunique"),
            median_overlap_bp=("overlap_bp", "median")).reset_index().assign(
                n_sequence_pairs_total=len(pairs), unit="pairs of distinct ncRNA sequences at one locus",
                denominator="loci carrying >1 distinct exact ncRNA sequence"))
    else:
        w(T / "g3_ncrna_boundary_variants.tsv", pd.DataFrame(
            columns=["class", "same_model", "n_sequence_pairs", "n_loci", "median_overlap_bp"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
