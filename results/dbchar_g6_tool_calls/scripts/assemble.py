#!/usr/bin/env python3
"""assemble - g6 rollup, derived registry and MANIFEST. Computes nothing."""
from __future__ import annotations
import argparse, csv, hashlib, sys
from pathlib import Path
import pyarrow.parquet as pq
R = "records"
UNITS = {
 "g6_tool_matrix_by_family.tsv": ("t01_tool_calls.py", "records / loci / exact RTs", "distinct raw records of that family label"),
 "g6_tool_matrix_retron.tsv": ("t01_tool_calls.py", "records / loci / exact RTs", "distinct raw records of the Retron family label"),
 "g6_tool_matrix_retron_all_records.tsv": ("t01_tool_calls.py", R, "ALL records of master_Retron (including duplicate lines)"),
 "g6_tool_presence_retron.tsv": ("t01_tool_calls.py", "records / loci", "distinct raw records of the Retron family label"),
 "g6_subtype_presence.tsv": ("t01_tool_calls.py", R, "Retron records, or the tool-detected subset named in the measure"),
 "g6_subtype_vocabulary_DefenseFinder.tsv": ("t01_tool_calls.py", R, "Retron records carrying a DefenseFinder-style subtype"),
 "g6_subtype_vocabulary_PADLOC.tsv": ("t01_tool_calls.py", R, "Retron records carrying a PADLOC-style subtype"),
 "g6_subtype_agreement.tsv": ("t01_tool_calls.py", R, "Retron records where both tools wrote a subtype"),
 "g6_subtype_disagreement_pairs.tsv": ("t01_tool_calls.py", R, "Retron records where the two tools disagree (top 60)"),
 "g6_extraction_asymmetry.tsv": ("t01_tool_calls.py", R, "Retron records of that detected_by combination"),
 "g6_tool_by_database.tsv": ("t01_tool_calls.py", R, "Retron records of that source_database"),
 "g6_second_counts.tsv": ("c04_reconcile.py", R, "named per row; both routes count ALL records of master_Retron"),
 "g6_prior_reconciliation.tsv": ("c04_reconcile.py", "named per row", "named per row"),
 "c03_positive_controls.tsv": ("c03_controls.py", "controls", "n/a - one pass/fail control per row"),
 "g6_derived_registry.tsv": ("assemble.py", "datasets", "n/a - identity of the derived dataset; no rate"),
 "g6_summary.tsv": ("assemble.py", "named per row", "named per row in the source_table column"),
}
def rd(p):
    with p.open(encoding="utf-8") as fh: return list(csv.DictReader(fh, delimiter="\t"))
def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--work", required=True)
    W = Path(ap.parse_args().work); T, D = W / "tables", W / "derived"
    p = D / "rt_tool_calls_v1.parquet"
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for b in iter(lambda: fh.read(16 << 20), b""): h.update(b)
    t = pq.read_table(p, columns=["record_key"]); cd = hashlib.sha256()
    for v in t["record_key"].to_pylist(): cd.update((v or "").encode() + b"\n")
    with (T / "g6_derived_registry.tsv").open("w") as fh:
        fh.write("dataset\tbytes\tsha256\trows\tcontent_key\tcontent_digest_sha256\n")
        fh.write(f"rt_tool_calls_v1.parquet\t{p.stat().st_size}\t{h.hexdigest()}\t{t.num_rows}\trecord_key\t{cd.hexdigest()}\n")
    pres = rd(T / "g6_tool_presence_retron.tsv"); sub = rd(T / "g6_subtype_presence.tsv")
    ag = rd(T / "g6_subtype_agreement.tsv"); asym = rd(T / "g6_extraction_asymmetry.tsv")
    sc = rd(T / "g6_second_counts.tsv"); ctl = rd(T / "c03_positive_controls.tsv")
    pr = rd(T / "g6_prior_reconciliation.tsv")
    rows = [[f"tool_presence_pct:{x['tool']}", x["pct_of_retron_records"], "g6_tool_presence_retron.tsv"] for x in pres]
    rows += [[f"subtype:{x['measure']}", x["n"], "g6_subtype_presence.tsv"] for x in sub]
    rows += [[f"agreement:{x['measure']}", x["n"], "g6_subtype_agreement.tsv"] for x in ag]
    for x in asym:
        rows.append([f"ncrna_carriage_pct:{x['detected_by_set']}", x["pct_with_ncrna"], "g6_extraction_asymmetry.tsv"])
    rows.append(["second_count_rows", len(sc), "g6_second_counts.tsv"])
    rows.append(["second_count_disagreements", sum(1 for x in sc if x["agreement"] != "AGREE"), "g6_second_counts.tsv"])
    rows.append(["prior_rows_CONFIRMED", sum(1 for x in pr if x["verdict"] == "CONFIRMED"), "g6_prior_reconciliation.tsv"])
    rows.append(["positive_controls", len(ctl), "c03_positive_controls.tsv"])
    rows.append(["positive_controls_failed", sum(1 for x in ctl if x["result"] != "PASS"), "c03_positive_controls.tsv"])
    with (T / "g6_summary.tsv").open("w") as fh:
        fh.write("quantity\tvalue\tsource_table\n")
        for r in rows: fh.write("\t".join(str(x) for x in r) + "\n")
    present = sorted(x.name for x in T.glob("*.tsv"))
    missing = [n for n in present if n not in UNITS]
    if missing:
        print(f"assemble: tables with no MANIFEST row: {missing}", file=sys.stderr); return 1
    with (W / "MANIFEST.tsv").open("w") as fh:
        fh.write("artifact\tscript\tcommand\tunit\tdenominator\n")
        for n in present:
            s, u, d = UNITS[n]
            fh.write(f"tables/{n}\tscripts/{s}\tsee run.sh: {s}\t{u}\t{d}\n")
    print(f"assemble: {len(rows)} summary rows, {len(present)} tables")
    return 0
if __name__ == "__main__":
    sys.exit(main())
