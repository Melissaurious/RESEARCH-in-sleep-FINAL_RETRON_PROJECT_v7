#!/usr/bin/env python3
"""Verify the landed population against a fresh rebuild. Non-destructive."""
import csv, hashlib, sys
rebuilt = sys.argv[1]
reb={(r["pdb_id"],r["chain"]):r for r in csv.DictReader(open(rebuilt),delimiter="\t")}
land=list(csv.DictReader(open("tables/g1_population.tsv"),delimiter="\t"))
for r in land:
    k=(r["pdb_id"],r["chain"])
    assert k in reb, f"chain vanished on rebuild: {k}"
    assert reb[k]["tier"]==r["tier"], f"tier changed for {k}"
    assert reb[k]["S_class"]==r["S_class"], f"class changed for {k}"
    h=hashlib.sha256(open(r["source_file"],"rb").read()).hexdigest()
    assert h==r["file_sha256"], f"input changed: {r['source_file']}"
d=hashlib.sha256("".join(sorted(r["file_sha256"] for r in land)).encode()).hexdigest()
assert d==open("tables/g1_population_digest.txt").read().strip(), "population digest changed"
print(f"g1 reproduces the frozen population digest: {d}")
print(f"  {len(land)} chains; tiers, classes and input hashes identical on rebuild")
