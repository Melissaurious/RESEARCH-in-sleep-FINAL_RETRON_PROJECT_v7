#!/usr/bin/env python3
"""g5a — deterministic eligibility census over the Stage-1 exact-RT catalogue.

    census.py <tables_dir> <derived_dir>

This is step 1 of `results/rt07_g4b_production_mapper/docs/G5_EXECUTION_PLAN.md` §2, run
before the catalogue application so that every later g5/g6 denominator is a censused number
rather than the catalogue count.

WHAT IT DOES NOT DO
  * It does not map anything. No `hmmalign`, no `hmmsearch`, no state call, no mapper output.
  * It does not change the eligibility rule. The rule is imported from the frozen production
    package and applied verbatim; `MIN_AA` and the alphabet are not restated here.
  * It draws no biological conclusion. A short sequence is not called incomplete, a family is
    not called architecture-less, and no metadata label is treated as truth.

THE ELIGIBILITY RULE IS NOT REDEFINED HERE. `rtmap.run_mapper.validate` is the frozen
function the production runner itself calls, and the census calls it on the whole catalogue.
Reason priority is therefore the frozen priority: length is tested before the alphabet, so a
`NON_STANDARD_RESIDUE` record is always >= MIN_AA. The secondary flag
`also_has_nonstandard_residue` is reported separately so that the overlap is visible rather
than hidden by that priority.
"""
import collections
import gzip
import hashlib
import os
import statistics
import sys

ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
G4B = f"{ROOT}/results/rt07_g4b_production_mapper"
sys.path.insert(0, f"{G4B}/code")

from rtmap import run_mapper as R          # noqa: E402  the frozen eligibility rule
from rtmap import params as P              # noqa: E402
from rtmap import version as V             # noqa: E402

import pandas as pd                        # noqa: E402

FAA = f"{ROOT}/data/derived/rt_exact_v1.faa"
EXACT = f"{ROOT}/data/derived/rt_exact_v1.parquet"
FAMBASE = f"{ROOT}/data/derived/rt_family_baseline_v1.parquet"
TOOLS = f"{ROOT}/data/derived/rt_tool_calls_v1.parquet"
RECORDS = f"{ROOT}/data/derived/rt_records_v1.parquet"

TABLES, DERIVED = sys.argv[1], sys.argv[2]

# Length bins. Declared here as a REPORTING convenience only - no bin edge is a threshold,
# and none of them is used to include or exclude anything. The only operative cutoff is the
# frozen MIN_AA, which the 200-249 / 250-299 boundary happens to sit on.
BINS = [(0, 99, "<100"), (100, 149, "100-149"), (150, 199, "150-199"),
        (200, 249, "200-249"), (250, 299, "250-299"), (300, 399, "300-399"),
        (400, 499, "400-499"), (500, 10 ** 9, ">=500")]

PCTLS = [("min", 0.0), ("p1", 0.01), ("p5", 0.05), ("p25", 0.25), ("median", 0.50),
         ("p75", 0.75), ("p95", 0.95), ("p99", 0.99), ("max", 1.0)]


def gzip_text(path):
    """Deterministic gzip writer: no timestamp, no stored filename, so a rerun on the same
    data produces a byte-identical file and its sha256 is a content hash."""
    import io
    raw = open(path, "wb")
    gz = gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=raw, mtime=0)
    return io.TextIOWrapper(gz, encoding="utf-8", newline="\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def pct(vals_sorted, q):
    """Nearest-rank percentile on a pre-sorted list. Deterministic, no interpolation."""
    if not vals_sorted:
        return ""
    if q <= 0:
        return vals_sorted[0]
    if q >= 1:
        return vals_sorted[-1]
    i = int(q * (len(vals_sorted) - 1) + 0.5)
    return vals_sorted[i]


def write_tsv(path, header, rows):
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    print(f"  wrote {os.path.basename(path)}  ({len(rows)} rows)")


def main():
    comps = V.check_instrument()
    mv = V.mapper_version(comps)
    print(f"frozen instrument: {mv}")
    print(f"eligibility rule:  {comps['eligibility_rule']}")

    # ---- 1. the frozen rule, applied to the whole catalogue --------------------------
    records = list(R.read_fasta(FAA))
    n_total = len(records)
    good, invalid = R.validate(records)
    # Clean once. `R.clean` is the frozen cleaning function; calling it per lookup later,
    # or rebuilding dict(records) inside a comprehension, turns this into an O(n^2) pass
    # over a 501k-record catalogue.
    cleaned = {sid: R.clean(raw) for sid, raw in records}
    lengths = {sid: len(s) for sid, s in cleaned.items()}

    # Reason per ineligible id. `validate` emits one row per rejected occurrence; identifiers
    # here are sequence hashes and are unique, which is asserted below rather than assumed.
    reason = {sid: code for sid, _, code, _ in invalid}
    detail = {sid: det for sid, _, code, det in invalid}

    ids = [sid for sid, _ in records]
    assert len(set(ids)) == n_total, "FAIL CLOSED: duplicate identifier in the exact-RT FASTA"
    assert not (set(good) & set(reason)), "FAIL CLOSED: an id is both eligible and ineligible"
    assert len(good) + len(reason) == n_total, "FAIL CLOSED: partition does not reconcile"
    n_elig, n_inel = len(good), len(reason)
    print(f"total {n_total}  eligible {n_elig}  ineligible {n_inel}")

    # secondary flag: a <MIN_AA record may ALSO carry a non-standard residue. The frozen
    # priority assigns it BELOW_MIN_LENGTH, so the overlap would otherwise be invisible.
    nonstd_secondary = {sid for sid in reason
                        if reason[sid] == "BELOW_MIN_LENGTH"
                        and R.NON_STANDARD.search(cleaned[sid])}

    # ---- 2. cross-check the FASTA against the canonical parquet ----------------------
    ex = pd.read_parquet(EXACT, columns=["rt_seq_hash", "rt_aa_len", "any_multilabel",
                                         "family_label_set", "wellformed",
                                         "n_source_databases", "n_records", "n_loci",
                                         "n_genomes"])
    hash_match = set(ex.rt_seq_hash) == set(ids)
    len_mismatch = int((ex.set_index("rt_seq_hash").rt_aa_len
                        .reindex(ids).values != [lengths[i] for i in ids]).sum())
    print(f"parquet hash-set identical to FASTA: {hash_match}; "
          f"rt_aa_len != cleaned length on {len_mismatch} record(s)")

    # ---- 3. metadata, per exact RT --------------------------------------------------
    fam = pd.read_parquet(FAMBASE, columns=["rt_seq_hash", "family_label",
                                            "completeness_class", "view", "n_species"])
    tl = pd.read_parquet(TOOLS, columns=["rt_seq_hash", "by_myRT", "by_PADLOC",
                                         "by_DefenseFinder"])
    tl = tl.groupby("rt_seq_hash", sort=True).agg(
        by_myRT=("by_myRT", "max"), by_PADLOC=("by_PADLOC", "max"),
        by_DefenseFinder=("by_DefenseFinder", "max")).reset_index()

    rec = pd.read_parquet(RECORDS, columns=["rt_seq_hash", "source_database",
                                           "type_set_norm", "tax_domain", "tax_phylum"])

    def joined_per_hash(df, col, out):
        """Deterministic ';'-joined distinct values per exact RT.

        Deduplicate FIRST, then join. A single groupby with a per-group Python lambda over
        3.06M records and 501,561 groups is pathological (it did not finish); deduplicating
        to the distinct (hash, value) pairs first takes this to seconds per column. The
        result is identical: sorted distinct values, joined.
        """
        sub = (df[["rt_seq_hash", col]].dropna().drop_duplicates()
               .sort_values(["rt_seq_hash", col], kind="mergesort"))
        s = sub.groupby("rt_seq_hash", sort=True)[col].agg(";".join)
        n = sub.groupby("rt_seq_hash", sort=True)[col].size()
        return (s.rename(out).to_frame()
                .join(n.rename(f"n_distinct_{col}")).reset_index())

    agg = None
    for col, out in (("source_database", "source_databases"),
                     ("type_set_norm", "system_types"),
                     ("tax_domain", "tax_domains"),
                     ("tax_phylum", "tax_phyla")):
        part = joined_per_hash(rec, col, out)
        agg = part if agg is None else agg.merge(part, on="rt_seq_hash", how="outer")
        print(f"  aggregated {col}")
    agg = agg.rename(columns={"n_distinct_tax_phylum": "n_tax_phylum"})
    del rec

    meta = (ex.merge(fam, on="rt_seq_hash", how="left")
              .merge(tl, on="rt_seq_hash", how="left")
              .merge(agg, on="rt_seq_hash", how="left"))
    meta["cleaned_len"] = meta.rt_seq_hash.map(lengths)
    meta["eligible"] = meta.rt_seq_hash.map(lambda h: h in good)
    meta["ineligibility_reason"] = meta.rt_seq_hash.map(
        lambda h: reason.get(h, "ELIGIBLE"))
    meta["also_has_nonstandard_residue"] = meta.rt_seq_hash.map(
        lambda h: h in nonstd_secondary)
    meta["multi_status"] = meta.any_multilabel.map({True: "MULTI", False: "NON_MULTI"})
    meta = meta.sort_values("rt_seq_hash", kind="mergesort").reset_index(drop=True)

    # ---- 4. the per-record partition, landed under data/derived/ --------------------
    os.makedirs(DERIVED, exist_ok=True)
    part_cols = ["rt_seq_hash", "cleaned_len", "eligible", "ineligibility_reason",
                 "also_has_nonstandard_residue"]
    part = f"{DERIVED}/g5a_eligibility_partition.tsv.gz"
    with gzip_text(part) as f:
        f.write("\t".join(part_cols) + "\n")
        for t in meta[part_cols].itertuples(index=False):
            f.write("\t".join(str(x) for x in t) + "\n")

    inel_cols = ["rt_seq_hash", "sequence_id", "cleaned_len", "ineligibility_reason",
                 "also_has_nonstandard_residue", "ineligibility_detail",
                 "raw_myrt_family_label_set", "stage1_collapsed_family", "multi_status",
                 "completeness_class", "view", "source_databases", "n_source_databases",
                 "system_types", "tax_domains", "tax_phyla", "n_tax_phylum", "n_species",
                 "by_myRT", "by_PADLOC", "by_DefenseFinder", "n_records", "n_loci",
                 "n_genomes", "wellformed"]
    inel = meta[~meta.eligible].copy()
    inel["sequence_id"] = inel.rt_seq_hash          # the FASTA identifier IS the hash
    inel["ineligibility_detail"] = inel.rt_seq_hash.map(detail)
    inel = inel.rename(columns={"family_label_set": "raw_myrt_family_label_set",
                                "family_label": "stage1_collapsed_family"})
    inel_path = f"{DERIVED}/g5a_ineligible_records.tsv.gz"
    with gzip_text(inel_path) as f:
        f.write("\t".join(inel_cols) + "\n")
        for t in inel[inel_cols].itertuples(index=False):
            f.write("\t".join(str(x) for x in t) + "\n")

    elig_path = f"{DERIVED}/g5a_eligible_ids.txt.gz"
    with gzip_text(elig_path) as f:
        for h in meta.loc[meta.eligible, "rt_seq_hash"]:
            f.write(h + "\n")

    # ---- 5. global duplicate-identifier census (G5 plan §2/§4) ----------------------
    dup = collections.Counter(ids)
    conflicts = sorted(k for k, v in dup.items() if v > 1)
    write_tsv(f"{TABLES}/g5a_id_conflicts.tsv", ["sequence_id", "n_occurrences"],
              [[k, dup[k]] for k in conflicts])

    # ---- 6. length distributions ----------------------------------------------------
    def dist_rows(label, hashes):
        v = sorted(lengths[h] for h in hashes)
        row = [label, len(v)]
        for _, q in PCTLS:
            row.append(pct(v, q))
        row.append(f"{statistics.mean(v):.1f}" if v else "")
        return row

    write_tsv(f"{TABLES}/g5a_length_distribution.tsv",
              ["population", "n"] + [n for n, _ in PCTLS] + ["mean"],
              [dist_rows("all_exact_rt", ids),
               dist_rows("eligible", list(good)),
               dist_rows("ineligible", list(reason)),
               dist_rows("ineligible_BELOW_MIN_LENGTH",
                         [h for h in reason if reason[h] == "BELOW_MIN_LENGTH"]),
               dist_rows("ineligible_NON_STANDARD_RESIDUE",
                         [h for h in reason if reason[h] == "NON_STANDARD_RESIDUE"])])

    def bin_of(n):
        for lo, hi, name in BINS:
            if lo <= n <= hi:
                return name
        return "UNBINNED"

    bin_tab = collections.Counter()
    for h in ids:
        bin_tab[(bin_of(lengths[h]), "eligible" if h in good else "ineligible")] += 1
    rows = []
    for _, _, name in BINS:
        e, i = bin_tab[(name, "eligible")], bin_tab[(name, "ineligible")]
        rows.append([name, e + i, e, i,
                     f"{e / (e + i):.4f}" if (e + i) else ""])
    write_tsv(f"{TABLES}/g5a_length_bins.tsv",
              ["length_bin_aa", "n_total", "n_eligible", "n_ineligible",
               "eligible_fraction"], rows)

    # ---- 7. ineligibility reasons ---------------------------------------------------
    rc = collections.Counter(reason.values())
    rows = [[code, rc[code], f"{rc[code] / n_total:.4f}", f"{rc[code] / n_inel:.4f}"]
            for code in sorted(rc)]
    rows.append(["ELIGIBLE", n_elig, f"{n_elig / n_total:.4f}", ""])
    write_tsv(f"{TABLES}/g5a_ineligibility_reasons.tsv",
              ["reason", "n", "fraction_of_catalogue", "fraction_of_ineligible"], rows)

    # ---- 8. eligibility by stratum --------------------------------------------------
    overall = n_elig / n_total

    def strat(col, path, min_n=1, note=""):
        g = meta.groupby(col, dropna=False, sort=True)
        rows = []
        for key, sub in g:
            tot = len(sub)
            if tot < min_n:
                continue
            e = int(sub.eligible.sum())
            frac = e / tot
            rows.append([str(key), tot, e, tot - e, f"{frac:.4f}",
                         f"{frac - overall:+.4f}",
                         "LOWER_THAN_CATALOGUE" if frac < overall - 0.05 else
                         ("HIGHER_THAN_CATALOGUE" if frac > overall + 0.05 else "COMPARABLE")])
        rows.sort(key=lambda r: -r[1])
        rows.append(["ALL_EXACT_RT", n_total, n_elig, n_inel, f"{overall:.4f}",
                     "+0.0000", "reference"])
        write_tsv(path, [col, "n_total", "n_eligible", "n_ineligible",
                         "eligible_fraction", "delta_vs_catalogue", "flag"], rows)
        return rows

    strat("family_label", f"{TABLES}/g5a_eligibility_by_family.tsv")
    strat("family_label_set", f"{TABLES}/g5a_eligibility_by_raw_myrt_family.tsv", min_n=100)
    strat("multi_status", f"{TABLES}/g5a_eligibility_by_multi_status.tsv")
    strat("completeness_class", f"{TABLES}/g5a_eligibility_by_completeness.tsv")
    strat("view", f"{TABLES}/g5a_eligibility_by_view.tsv")
    strat("source_databases", f"{TABLES}/g5a_eligibility_by_source_database.tsv", min_n=100)
    strat("system_types", f"{TABLES}/g5a_eligibility_by_system_type.tsv", min_n=100)
    strat("tax_domains", f"{TABLES}/g5a_eligibility_by_tax_domain.tsv", min_n=100)

    meta["tool_support"] = (
        meta.by_myRT.fillna(False).astype(int).astype(str) + "/"
        + meta.by_PADLOC.fillna(False).astype(int).astype(str) + "/"
        + meta.by_DefenseFinder.fillna(False).astype(int).astype(str))
    strat("tool_support", f"{TABLES}/g5a_eligibility_by_tool_support.tsv")

    # ---- 9. the <MIN_AA population, described only -----------------------------------
    short = meta[meta.ineligibility_reason == "BELOW_MIN_LENGTH"]
    for col, path in (("family_label", "g5a_short_by_family.tsv"),
                      ("family_label_set", "g5a_short_by_raw_myrt_family.tsv"),
                      ("source_databases", "g5a_short_by_source_database.tsv"),
                      ("system_types", "g5a_short_by_system_type.tsv"),
                      ("multi_status", "g5a_short_by_multi_status.tsv")):
        c = collections.Counter(short[col].astype(str))
        tot_by = collections.Counter(meta[col].astype(str))
        rows = sorted(([k, c[k], tot_by[k], f"{c[k] / tot_by[k]:.4f}"] for k in c),
                      key=lambda r: -r[1])
        rows = [r for r in rows if r[1] >= 1][:200]
        write_tsv(f"{TABLES}/{path}",
                  [col, "n_below_min_length", "n_total_in_stratum",
                   "fraction_of_stratum_below_min_length"], rows)

    # ---- 10. summary ----------------------------------------------------------------
    inputs = [("exact_rt_faa", FAA), ("exact_rt_parquet", EXACT),
              ("family_baseline_parquet", FAMBASE), ("tool_calls_parquet", TOOLS),
              ("records_parquet", RECORDS)]
    srows = [
        ["mapper_version", mv, "identifier",
         "the frozen production instrument whose eligibility rule this census applies"],
        ["instrument_sha256", V.instrument_digest(comps), "sha256", ""],
        ["eligibility_rule", comps["eligibility_rule"], "rule",
         "imported from the frozen package, not restated by this census"],
        ["MIN_AA", R.MIN_AA, "aa", "the only operative length cutoff; unchanged"],
        ["n_total_exact_rt", n_total, "exact RT sequences",
         "every record in rt_exact_v1.faa"],
        ["n_unique_rt_hash", len(set(ids)), "exact RT sequences",
         "the catalogue is one row per exact sequence, so this equals the total"],
        ["n_duplicate_identifiers", len(conflicts), "identifiers",
         "global duplicate-identifier census (G5 plan section 4)"],
        ["G5_ELIGIBLE_N", n_elig, "exact RT sequences",
         "THE FROZEN g5 DENOMINATOR"],
        ["n_ineligible", n_inel, "exact RT sequences", ""],
        ["eligible_fraction", f"{overall:.6f}", "fraction of the catalogue", ""],
        ["n_below_min_length", rc["BELOW_MIN_LENGTH"], "exact RT sequences",
         f"cleaned length < {R.MIN_AA} aa"],
        ["n_non_standard_residue", rc["NON_STANDARD_RESIDUE"], "exact RT sequences",
         "at least one residue outside the 20 standard amino acids; all are >= MIN_AA "
         "because the frozen rule tests length first"],
        ["n_below_min_length_also_nonstandard", len(nonstd_secondary),
         "exact RT sequences",
         "secondary flag, reported so the frozen reason priority does not hide the overlap"],
        ["partition_reconciles", "YES", "verdict",
         f"{n_elig} + {n_inel} = {n_total}, and no identifier appears on both sides"],
        ["parquet_hash_set_identical", "YES" if hash_match else "NO", "verdict",
         "rt_exact_v1.faa and rt_exact_v1.parquet describe the same sequence set"],
        ["n_rt_aa_len_disagreements", len_mismatch, "exact RT sequences",
         "rt_aa_len in the canonical parquet vs the cleaned length this census computed"],
    ] + [[f"input.{n}.sha256", sha256_file(p), "sha256", p] for n, p in inputs] \
      + [["output.g5a_eligibility_partition.tsv.gz", sha256_file(part), "sha256", part],
         ["output.g5a_ineligible_records.tsv.gz", sha256_file(inel_path), "sha256",
          inel_path],
         ["output.g5a_eligible_ids.txt.gz", sha256_file(elig_path), "sha256", elig_path]]
    write_tsv(f"{TABLES}/g5a_census_summary.tsv",
              ["quantity", "value", "unit", "note"], srows)

    print(f"\nG5_ELIGIBLE_N = {n_elig}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
