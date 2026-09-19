#!/usr/bin/env python3
"""s3c_g0_inputs — hash every Stage-3C input against its frozen record (LAUNCHER_03C K1, K2, K4).

Writes INPUT_PROVENANCE.tsv. Exits non-zero if any FROZEN input mismatches (kill criteria fire
before any join is computed).
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

rows = []


def rel(p):
    return os.path.relpath(p, L.ROOT) if p.startswith(L.ROOT) else p


def add(input_id, path, role, grade, ref, expected, expected_source):
    obs = L.sha256_file(path) if os.path.isfile(path) else None
    if obs is None and "__pycache__" in path:
        # BS-16: a compiled artefact is not a result and must never be sealed. The 3B bundles
        # sealed three .pyc files that git never tracked; recorded as a packaging defect of
        # that bundle, not as a content mismatch of any result it carries.
        verdict = "PYCACHE_SEALED_NOT_PRESENT"
    elif obs is None:
        verdict = "MISSING"
    elif expected is None:
        verdict = "NO_EXPECTED_RECORD"
    else:
        verdict = "MATCH" if obs == expected else "MISMATCH"
    rows.append(dict(input_id=input_id, path=rel(path), role=role, trust_grade=grade, frozen_ref=ref,
                     sha256_observed=obs or "", sha256_expected=expected or "",
                     expected_source=expected_source, verdict=verdict,
                     bytes=os.path.getsize(path) if obs else ""))


def blob_sha(commit, path):
    b = L.git_blob(commit, rel(path))
    return L.sha256_bytes(b) if b is not None else None


# ---- Stage 3A: working copy must equal the blob at the closure commit (K1) -------------------
C3A = L.STAGE3A_CLOSURE_COMMIT
s3a_files = [
    ("3A_pdp_primary_residues", L.PDP_PRIMARY, "per-residue PDP unit (primary)"),
    ("3A_pdp_primary_summary", os.path.join(L.S3A_RES, "rt_pdp_primary.summary.tsv"), "PDP summary (primary)"),
    ("3A_pdp_p4_residues", L.PDP_P4, "per-residue PDP unit (BJ-p4 sensitivity arm)"),
    ("3A_pdp_p4_summary", os.path.join(L.S3A_RES, "rt_pdp_p4.summary.tsv"), "PDP summary (BJ-p4)"),
    ("3A_units_primary", L.UNITS["primary"], "unit features and roles"),
    ("3A_calls_primary", L.CALLS["primary"], "palm/thumb/fingers-like call status"),
    ("3A_units_p4", L.UNITS["p4"], "unit features (BJ-p4)"),
    ("3A_calls_p4", L.CALLS["p4"], "call status (BJ-p4)"),
    ("3A_units_report", os.path.join(L.S3A_RES, "rt_units.report.txt"), "verdict, LOGO, PDP_ABSENT"),
    ("3A_impl_sensitivity", os.path.join(L.S3A_RES, "rt_pdp_implementation_sensitivity.tsv"), "primary vs BJ-p4"),
    ("3A_partition_freeze", os.path.join(L.S3A_RES, "RT_PARTITION_FREEZE_sha256.txt"), "partition freeze hashes"),
    ("3A_register", L.REGISTER, "62-chain register"),
    ("3A_groups", os.path.join(L.S3A, "BIOLOGICAL_GROUPS.tsv"), "biological groups"),
    ("3A_T1", L.T1, "closure table S3A-1 (strata)"),
    ("3A_closure", os.path.join(L.S3A, "closure", "STAGE3A_CLOSURE.md"), "closure package"),
    ("3A_handoff", os.path.join(L.S3A, "closure", "STAGE3C_HANDOFF.md"), "3C handoff rules"),
]
for iid, p, role in s3a_files:
    add(iid, p, role, "FROZEN", f"stage3a {C3A}", blob_sha(C3A, p), f"git blob {C3A}")
for p in sorted(glob.glob(os.path.join(L.SS_DIR, "*.ss.tsv"))):
    add("3A_ss_" + os.path.basename(p).split(".")[0], p, "per-residue secondary structure (route A/B)",
        "FROZEN", f"stage3a {C3A}", blob_sha(C3A, p), f"git blob {C3A}")

# partition freeze file: second, independent record for the four partition files
freeze = {}
for ln in open(os.path.join(L.S3A_RES, "RT_PARTITION_FREEZE_sha256.txt")):
    h, p = ln.split()
    freeze[p] = h
for p, h in sorted(freeze.items()):
    add("3A_freeze_" + os.path.basename(p), os.path.join(L.ROOT, p), "partition file vs freeze record",
        "FROZEN", "RT_PARTITION_FREEZE_sha256.txt (76526444)", h, "RT_PARTITION_FREEZE_sha256.txt")


# ---- Stage 3B and the mapper: every bundle file vs the bundle's own OUTPUTS.tsv (K2) --------
def bundle(tag, bdir, ref, used):
    outs = L.read_tsv(os.path.join(bdir, "OUTPUTS.tsv"))
    for r in outs:
        p = os.path.join(bdir, r["path"])
        role = "USED: " + used[r["path"]] if r["path"] in used else "bundle member (integrity only)"
        add(f"{tag}:{r['path']}", p, role, "FROZEN", ref, r["sha256"], f"{rel(bdir)}/OUTPUTS.tsv")


bundle("cat3b_g1", L.CAT3B_G1, "cat3b_g1_population_freeze",
       {"tables/g1_population.tsv": "3B population", "tables/g1_declared_criteria.tsv": "resolution cut"})
bundle("cat3b_g2", L.CAT3B_G2, "cat3b_g2_contract_and_thresholds",
       {"tables/TRUTH_TABLE.tsv": "3B truth (Tier-A rows only)",
        "tables/G2_TIERA_EVALUATION.tsv": "frozen detector Tier-A output",
        "tables/g2_frozen_parameters.tsv": "frozen detector parameters and PARTIAL scope"})
bundle("rt07_g4b", L.MAPPER, "rt07_g4b_production_mapper (rtmap-1.0.0/53a1e738a19b3896)",
       {"code/rtmap/mapper.py": "frozen mapper", "code/rtmap/run_mapper.py": "production runner",
        "code/rtmap/params.py": "frozen parameters"})

for iid, p, ref, role in [
    ("3B_K5_closure", os.path.join(L.ROOT, "analysis/stage3b_design/G2_DECOY_AUDIT_AND_K5_CLOSURE.md"),
     "c0592f0", "permitted 3B statements and miss breakdown"),
    ("3B_launcher", os.path.join(L.ROOT, "launchers/LAUNCHER_03B_catalytic_site_architecture.md"),
     "c0592f0", "3B closure banner"),
    ("stage2_structure_inventory",
     os.path.join(L.ROOT, "results/rt07_pre_g4_scope_separation/tables/structure_reference_inventory.tsv"),
     C3A, "anchor-set membership per structure (mapper independence)"),
    ("dbchar_rt_hash_convention", os.path.join(L.ROOT, "results/dbchar_g2_canonical_units/scripts/g2lib.py"),
     C3A, "rt_hash join-key definition"),
]:
    add(iid, p, role, "FROZEN", ref, blob_sha(ref, p), f"git blob {ref}")

# ---- Stage 2 closed state: vendored copies vs git objects at 94a1a788 ------------------------
S2 = {"g7a_state_to_residue.tsv": "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_state_to_residue.tsv",
      "g7a_crosswalk_resolved.tsv": "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_crosswalk_resolved.tsv",
      "g7a_panel_results.tsv": "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_panel_results.tsv",
      "g7a_closure_decision.tsv": "results/rt07_g7a_rt0_rt7_bridge/tables/g7a_closure_decision.tsv",
      "g7a_closure_decision_erratum_2026-09-19.tsv": "docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv",
      "2026-09-19_stage2_closed.md": "docs/decisions/2026-09-19_stage2_closed.md",
      "2026-09-19_stage2_g7a_review_errata.md": "docs/decisions/2026-09-19_stage2_g7a_review_errata.md"}
for name, src in S2.items():
    b = L.git_blob(L.STAGE2_COMMIT, src)
    add(f"stage2:{name}", os.path.join(L.STAGE2, name), f"Stage-2 closed state ({src})", "FROZEN",
        f"main {L.STAGE2_COMMIT[:10]}", L.sha256_bytes(b) if b is not None else None,
        f"git blob {L.STAGE2_COMMIT[:10]}:{src}")

# ---- RAW coordinate files: vs the register's file_sha256 -------------------------------------
seen = set()
for c, r in sorted(L.register().items()):
    if r["source_file"] in seen:
        continue
    seen.add(r["source_file"])
    add(f"coords:{r['pdb_id']}", r["source_file"], "deposited coordinates (NA contacts, sequence check)",
        "RAW", "STRUCTURE_REGISTER.tsv file_sha256", r["file_sha256"], "STRUCTURE_REGISTER.tsv")

# ---- historical boundary product: hashed, audited in Comparison C, never truth --------------
HB = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures"
for f in ("reference_boundaries.tsv", "reference_boundaries.json", "reference_boundaries.py",
          "run_log.txt", "boundary_extraction_report.txt"):
    add(f"historical:{f}", os.path.join(HB, f), "historical F/P/T boundary product (graded RED; audited in C)",
        "RE-DERIVE", "prior_asset_audit REUSE_DECISIONS.md 4.1", None, "none - hash recorded here first")

# ---- mapper instrument identity (K4) ----------------------------------------------------------
sys.path.insert(0, os.path.join(L.MAPPER, "code"))
from rtmap import version as V  # noqa: E402

ver = V.mapper_version(V.check_instrument())
rows.append(dict(input_id="rt07_g4b:instrument", path="results/rt07_g4b_production_mapper/code/rtmap",
                 role="frozen instrument identity (check_instrument)", trust_grade="FROZEN",
                 frozen_ref="rtmap-1.0.0/53a1e738a19b3896", sha256_observed=ver,
                 sha256_expected="rtmap-1.0.0/53a1e738a19b3896", expected_source="LAUNCHER_03C K4",
                 verdict="MATCH" if ver == "rtmap-1.0.0/53a1e738a19b3896" else "MISMATCH", bytes=""))

cols = ["input_id", "path", "role", "trust_grade", "frozen_ref", "sha256_observed", "sha256_expected",
        "expected_source", "verdict", "bytes"]
L.write_tsv(os.path.join(L.S3C, "INPUT_PROVENANCE.tsv"), rows, cols)

bad = [r for r in rows if r["verdict"] in ("MISMATCH", "MISSING")]
frozen_bad = [r for r in bad if r["trust_grade"] == "FROZEN"]
from collections import Counter  # noqa: E402
print("INPUT_PROVENANCE:", len(rows), "rows", dict(Counter(r["verdict"] for r in rows)))
for r in bad:
    print("  ", r["verdict"], r["trust_grade"], r["input_id"])
if frozen_bad:
    sys.exit("KILL K1/K2/K4: a FROZEN input does not match its record")
