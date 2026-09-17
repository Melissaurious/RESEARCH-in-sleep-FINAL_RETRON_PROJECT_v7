#!/usr/bin/env python3
"""REPAIR 5 tests - the scoped loader must be EXACTLY equivalent on construction families,
and must refuse to materialise a sealed family.

If the scoped loader kept even one sequence more or fewer than the old loader, every
calibrated threshold would shift and the repair would silently change the science. During
development it did exactly that: it kept GII 497 vs 496 and DGRs 492 vs 488 because it had not
replicated the old loader's rejection of non-standard amino acids. L1 pins that.

    loader_equivalence.py <tables_dir>
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scoped_loader import load_families, access_log, SEALED, AUTHORISATION_TOKEN
sys.path.insert(0, "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results/"
                   "rt07_g4a_repaired/scripts")
from repaired_lib import eligible_by_family

TABLES = sys.argv[1]
CONSTRUCTION = ["Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA"]
rows = []


def rec(name, cls, ok, detail, passes_when, fails_when):
    rows.append([name, cls, "PASS" if ok else "FAIL", detail, passes_when, fails_when])


old = eligible_by_family()
new = load_families(CONSTRUCTION)

# L1 - exact equivalence, sequence by sequence, on every construction family
diffs = []
for fam in CONSTRUCTION:
    if new.get(fam) != old.get(fam):
        diffs.append(f"{fam}: scoped={len(new.get(fam, {}))} old={len(old.get(fam, {}))}")
rec("L1_scoped_loader_equivalent_on_construction", "FALSIFIABLE_EMPIRICAL_TEST", not diffs,
    f"differences: {diffs or 'none'}; counts=" +
    str({f: len(new[f]) for f in CONSTRUCTION}),
    "every construction family is identical (ids AND residues) to the old loader",
    "any family differs by even one sequence - which would shift every calibrated threshold")

# L2 - sealed family is not materialised, and is not even present as a key
sealed_present = [f for f in SEALED if f in new]
rec("L2_sealed_family_not_materialised", "FALSIFIABLE_EMPIRICAL_TEST", not sealed_present,
    f"sealed families present in scoped output: {sealed_present or 'none'}; "
    f"old loader materialised {sorted(SEALED & set(old))}",
    "no sealed family appears in the scoped loader's output",
    "a sealed family is materialised - the defect this repair exists to remove")

# L3 - requesting a sealed family WITHOUT the token must raise (negative control, executed)
raised = False
try:
    load_families(["GII", "UG25"])
except SystemExit as e:
    raised = "sealed" in str(e).lower()
rec("L3_sealed_request_fails_closed", "FALSIFIABLE_EMPIRICAL_TEST", raised,
    f"unauthorised request for a sealed family raised: {raised}",
    "requesting UG25 without the operator token raises SystemExit",
    "the request silently succeeds")

# L4 - the token DOES permit it (otherwise the confirmatory run could never happen).
# This proves the guard is a gate, not a wall, and that L3 is not passing for a trivial reason.
ok4 = False
try:
    d = load_families(["UG25"], authorisation=AUTHORISATION_TOKEN)
    ok4 = "UG25" in d and len(d["UG25"]) > 0
    n_ug25 = len(d.get("UG25", {}))
except SystemExit:
    n_ug25 = -1
rec("L4_authorised_request_succeeds", "FALSIFIABLE_EMPIRICAL_TEST", ok4,
    f"authorised load returned n={n_ug25} (feasibility count only; NOT evaluated, NOT aligned, "
    f"NOT scored - this test discards the object immediately)",
    "the explicit operator token permits loading the sealed family",
    "the token is ignored and the confirmatory run could never execute")

# L5 - the old loader is the thing being replaced: confirm it DOES leak, so the repair is real
leak = sorted(SEALED & set(old))
rec("L5_old_loader_demonstrably_leaked", "FALSIFIABLE_EMPIRICAL_TEST", bool(leak),
    f"old eligible_by_family() materialises {len(old)} families including {leak} "
    f"(n={len(old.get('UG25', {}))}) - this is the falsified claim",
    "the old loader is shown to materialise the sealed family",
    "the old loader did not leak - which would mean the reviewer's finding was wrong")

with open(f"{TABLES}/loader_scope_tests.tsv", "w") as f:
    f.write("test\tclassification\tresult\tdetail\tpasses_when\tfails_when\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[2]:4s} {r[0]:44s} {r[3]}")
bad = [r for r in rows if r[2] != "PASS"]
print(f"\n{len(rows)-len(bad)}/{len(rows)} passed")
sys.exit(1 if bad else 0)
