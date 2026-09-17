#!/usr/bin/env python3
"""Freeze tests for the production package. Run before every g5 shard batch.

These are NEGATIVE tests in the sense that matters: each one asserts that a specific way of
silently changing the science would be caught. They do not re-validate the mapper - that
question is closed - they prove the packaging cannot drift away from it.

    test_production_freeze.py
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
G4B = os.path.dirname(HERE)
sys.path.insert(0, f"{G4B}/code")

from rtmap import params as P          # noqa: E402
from rtmap import schema as S          # noqa: E402
from rtmap import version as V         # noqa: E402
from rtmap import crosswalk as X       # noqa: E402
from rtmap import run_mapper as R      # noqa: E402

PY = "/home/borg/miniconda3/envs/retron_tradicional/bin/python3"
ROOT = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
BUNDLE = f"{ROOT}/results/FINAL_PRE_UG25_VALIDATION_BUNDLE"

FAILS = []


def check(ok, label, detail=""):
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(label)


def t1_mapper_is_byte_identical():
    print("\n== T1  the production mapper is the frozen mapper, byte for byte ==")
    got = P.sha256_file(f"{G4B}/code/rtmap/mapper.py")
    check(got == V.FROZEN_MAPPER_SHA256, "T1 mapper.py sha256 equals the frozen hash", got)
    check(got == P.sha256_file(f"{BUNDLE}/code/mapper.py"),
          "T1 identical to FINAL_PRE_UG25_VALIDATION_BUNDLE/code/mapper.py")
    src = open(f"{G4B}/code/rtmap/mapper.py").read()
    check("hmmalign" in src and "--outformat" in src and "Stockholm" in src,
          "T1 the alignment call is unchanged")
    # The only occurrence of "interpolat" in the frozen mapper is the docstring guarantee
    # that the correspondence "comes from the ACTUAL hmmalign path, never from interpolation
    # between endpoints". A second occurrence would mean interpolation code came back.
    n_interp = len(re.findall(r"interpolat", src, re.I))
    check(n_interp == 1 and "never from" in src,
          "T1 endpoint interpolation was not reintroduced", f"{n_interp} mention(s)")


def t2_parameters_match_the_closure_decision():
    print("\n== T2  frozen scientific parameters ==")
    for k, want in sorted(P.EXPECTED_VALUES.items()):
        check(P.PARAMS[k] == want, f"T2 {k} == {want}", P.PARAMS[k])
    check(P.MATCH_STATE_DEFINITION == "hhmake -M 50",
          "T2 match-state definition is -M 50", P.MATCH_STATE_DEFINITION)
    check(len(P.ANCHORS) == 150 and P.ANCHORS == sorted(P.ANCHORS),
          "T2 150 frozen anchors, ascending")
    check(P.CAT_STATE not in P.ANCHORS,
          "T2 CAT_STATE is NOT an anchor - the two denominators stay separate")
    check(P.PROFILE_SHA256 == P.sha256_file(P.PROFILE_HMM),
          "T2 profile HMM identity")


def t3_control_tamper_is_caught():
    print("\n== T3  a tampered control table fails closed ==")
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["cp", "-r", "--no-preserve=mode", f"{G4B}/code",
                        f"{G4B}/control", td], check=True)
        p = f"{td}/control/SUPPORT_RULE_FROZEN.tsv"
        txt = open(p).read().replace("PP_HI\t0.75", "PP_HI\t0.65")
        open(p, "w").write(txt)
        r = subprocess.run([PY, "-B", "-c",
                            "import sys; sys.path.insert(0,'code'); import rtmap.params"],
                           capture_output=True, text=True, cwd=td,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        check(r.returncode != 0 and "FAIL CLOSED" in (r.stderr + r.stdout),
              "T3 a retuned PP_HI is rejected at import",
              (r.stderr + r.stdout).strip().splitlines()[0] if (r.stderr or r.stdout) else "")


def t4_mapper_tamper_is_caught():
    print("\n== T4  a tampered mapper fails closed ==")
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["cp", "-r", "--no-preserve=mode", f"{G4B}/code",
                        f"{G4B}/control", td], check=True)
        p = f"{td}/code/rtmap/mapper.py"
        open(p, "a").write("\n# drift\n")
        r = subprocess.run([PY, "-B", "-c",
                            "import sys; sys.path.insert(0,'code');"
                            " from rtmap import version; version.check_instrument()"],
                           capture_output=True, text=True, cwd=td,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        check(r.returncode != 0 and "NOT the frozen mapper" in (r.stderr + r.stdout),
              "T4 an edited mapper.py is rejected before any record is emitted")


def t5_schema_completeness():
    print("\n== T5  the schema keeps every required field and state ==")
    required_state = {"state_id", "call_state", "sequence_residue_index", "amino_acid",
                      "posterior", "support", "reason_code"}
    check(required_state <= set(S.STATES_COLUMNS), "T5 per-state fields present",
          str(sorted(required_state - set(S.STATES_COLUMNS))))
    required_seq = {"rt_hash", "sequence_id", "sequence_length", "mapper_version",
                    "profile_version", "match_state_definition", "family_metadata",
                    "n_states_total", "n_mapped", "n_ambiguous", "n_unsupported",
                    "n_deleted", "mapped_fraction", "inspectability_status", "cat_state",
                    "cat_call_state", "cat_residue_index", "cat_residue", "cat_motif_class",
                    "cat_support"}
    check(required_seq <= set(S.SEQUENCES_COLUMNS), "T5 per-sequence fields present",
          str(sorted(required_seq - set(S.SEQUENCES_COLUMNS))))
    check(set(S.CALL_STATES) == {"MAPPED", "AMBIGUOUS", "UNSUPPORTED", "DELETED_STATE"},
          "T5 exactly the four frozen call states")
    check(set(S.INSPECTABILITY_STATUS) ==
          {"MAPPABLE", "PARTIAL_MAPPING", "NO_SUPPORTED_MAPPING", "AMBIGUOUS_MAPPING",
           "INPUT_INVALID", "TOOL_FAILURE"},
          "T5 the six production statuses")
    blob = " ".join(S.STATES_COLUMNS + S.SEQUENCES_COLUMNS + S.FAILURES_COLUMNS)
    check(not re.search(r"\bRT[0-7]\b", blob),
          "T5 no historical RT0-RT7 label appears in any production column")


def t6_crosswalk_is_separate_and_unresolved():
    print("\n== T6  historical RT0-RT7 stays a separate, unresolved crosswalk ==")
    check(X.assert_unresolved_until_g7(), "T6 every crosswalk row is UNRESOLVED")
    rows = X.crosswalk_rows()
    check(len(rows) == 8, "T6 RT0..RT7 all present", str(len(rows)))
    check(all(r["operational_state"] == "UNRESOLVED" for r in rows),
          "T6 no production state is claimed to correspond to a historical label")
    check(X.annotate(P.CAT_STATE)[0]["historical_RT0_RT7_correspondence_if_supported"]
          == "UNRESOLVED",
          "T6 even CAT_STATE 262 carries no historical label")


def t7_no_biological_absence_language():
    print("\n== T7  absence language is not attached to abstention ==")
    doc = S.INSPECTABILITY_STATUS["NO_SUPPORTED_MAPPING"]
    check("NOT a biological absence" in doc,
          "T7 NO_SUPPORTED_MAPPING is documented as not biological absence")
    doc2 = S.INSPECTABILITY_STATUS["AMBIGUOUS_MAPPING"]
    check("not absence" in doc2.lower(), "T7 AMBIGUOUS_MAPPING is not absence")
    check("statement about the alignment path" in S.__doc__,
          "T7 DELETED_STATE is documented as an alignment-path statement")


def _executable_source(path):
    """Source with comments and string literals removed, so a docstring that MENTIONS a
    thing is not mistaken for code that REACHES for it."""
    import io
    import tokenize
    out = []
    with open(path, "rb") as f:
        for tok in tokenize.tokenize(f.readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            out.append(tok.string)
    return " ".join(out)


def t8_ug25_is_not_reachable():
    print("\n== T8  the production package cannot reach for UG25 or a holdout ==")
    mods = [f"{G4B}/code/rtmap/{fn}" for fn in sorted(os.listdir(f"{G4B}/code/rtmap"))
            if fn.endswith(".py")]
    code = " ".join(_executable_source(m) for m in mods)
    check("UG25" not in code,
          "T8 no production module has executable code referencing UG25")
    check("load_families" not in code and "authorised_families" not in code
          and "RT07_AUTHORISED_FAMILIES" not in code,
          "T8 production does not use the family loader at all - it reads a FASTA shard")
    check("Random" not in code and "shuffle" not in code,
          "T8 no RNG and no shuffling in the production path")
    check("make_negatives" not in code,
          "T8 production does not generate synthetic controls")


def t9_runner_contracts():
    print("\n== T9  runner input contracts ==")
    good, invalid = R.validate([("a", "M" * 300), ("a", "M" * 300), ("b", "M" * 10),
                                ("c", "M" * 299 + "X"), ("d", ""), (None, "AAA")])
    codes = sorted(c for _, _, c, _ in invalid)
    check(list(good) == ["a"], "T9 only the valid record survives", str(list(good)))
    check(codes == ["BELOW_MIN_LENGTH", "DUPLICATE_SEQUENCE_ID", "EMPTY_SEQUENCE",
                    "NON_STANDARD_RESIDUE", "UNPARSEABLE_RECORD"],
          "T9 every INPUT_INVALID reason is reachable", str(codes))
    conflict, cinv = R.validate([("k", "M" * 300), ("k", "W" * 300)])
    check(conflict == {} and sorted(c for _, _, c, _ in cinv)
          == ["DUPLICATE_SEQUENCE_ID_CONFLICT"] * 2,
          "T9 an identifier with different sequences rejects EVERY occurrence")
    check(R.MIN_AA == 250, "T9 eligibility minimum inherited from the registered loader")
    check(R.inspectability("MAPPED", "OK", 0.67) == "MAPPABLE", "T9 MAPPABLE")
    check(R.inspectability("MAPPED", "OK", 0.30) == "PARTIAL_MAPPING",
          "T9 PARTIAL_MAPPING below T1")
    check(R.inspectability("ABSTAIN", "INSUFFICIENT_SUPPORTED_ANCHORS", 0.03)
          == "AMBIGUOUS_MAPPING", "T9 AMBIGUOUS_MAPPING")
    check(R.inspectability("ABSTAIN", "NO_QUALIFYING_DOMAIN", 0.0)
          == "NO_SUPPORTED_MAPPING", "T9 NO_SUPPORTED_MAPPING")


def t10_version_identifier():
    print("\n== T10  the compact instrument identifier ==")
    c = V.check_instrument()
    mv = V.mapper_version(c)
    check(re.fullmatch(r"rtmap-1\.0\.0/[0-9a-f]{16}", mv), "T10 identifier shape", mv)
    c2 = dict(c, PP_HI="0.65")
    check(V.mapper_version(c2) != mv, "T10 a changed threshold changes the identifier")
    c3 = dict(c, mapper_sha256="0" * 64)
    check(V.mapper_version(c3) != mv, "T10 a changed mapper changes the identifier")
    c4 = dict(c, profile_sha256="0" * 64)
    check(V.mapper_version(c4) != mv, "T10 a changed profile changes the identifier")
    c5 = dict(c, anchor_set_sha256="0" * 64)
    check(V.mapper_version(c5) != mv, "T10 a changed anchor set changes the identifier")
    for f in ("instrument_tree_sha256", "eligibility_rule", "domain_scoring_protocol"):
        check(V.mapper_version(dict(c, **{f: "CHANGED"})) != mv,
              f"T10 a changed {f} changes the identifier")
    check(V.mapper_version(c) == mv, "T10 identical components give an identical identifier")


def t11_repairs_required_by_review():
    """The five repairs the independent packaging review required, asserted structurally.
    smoke/check_repairs.py exercises them end to end; these are the static guarantees."""
    print("\n== T11  the five review repairs are in place ==")
    c = V.check_instrument()
    check({"instrument_tree_sha256", "eligibility_rule", "domain_scoring_protocol"}
          <= set(c), "T11 R1 the wrapper, eligibility and protocol are instrument components")
    check("tables" not in V.INSTRUMENT_TREES,
          "T11 R1 tables/ is outside the instrument tree")
    check(c["domain_scoring_protocol"] == "PER_SEQUENCE_DB_SIZE_1",
          "T11 R1 the domain-scoring protocol is recorded as per-sequence")
    check("DUPLICATE_SEQUENCE_ID_CONFLICT" in S.INPUT_INVALID_REASONS,
          "T11 R2 the conflict reason code exists")
    src = open(f"{G4B}/code/rtmap/run_mapper.py").read()
    check("does not reconcile" in src,
          "T11 R3 the reconciliation assertion is present")
    check("def done_is_valid" in src and "output changed since it was written" in src,
          "T11 R4 the DONE sidecar is validated, not merely present")
    check("def verify_bundle_root" in src and "--pinned-root" in src,
          "T11 R1 external pinned-root verification is available")
    import inspect
    body = inspect.getsource(R.inspectability)
    body = body.split('"""')[2] if body.count('"""') >= 2 else body
    check(not any(t in body for t in ("n_amb", "n_uns", "n_map")),
          "T11 R5 no invented anchor-count predicate remains")
    check(set(S.STATUS_FROM_FROZEN_REASON) ==
          {("ABSTAIN", "INSUFFICIENT_SUPPORTED_ANCHORS"),
           ("ABSTAIN", "NO_QUALIFYING_DOMAIN")},
          "T11 R5 the status map is a bijection onto the frozen abstention reasons")


def main():
    for t in (t1_mapper_is_byte_identical, t2_parameters_match_the_closure_decision,
              t3_control_tamper_is_caught, t4_mapper_tamper_is_caught,
              t5_schema_completeness, t6_crosswalk_is_separate_and_unresolved,
              t7_no_biological_absence_language, t8_ug25_is_not_reachable,
              t9_runner_contracts, t10_version_identifier,
              t11_repairs_required_by_review):
        t()
    print()
    if FAILS:
        print(f"FREEZE TESTS FAILED: {len(FAILS)}")
        for f in FAILS:
            print(f"  {f}")
        return 1
    print("FREEZE TESTS OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
