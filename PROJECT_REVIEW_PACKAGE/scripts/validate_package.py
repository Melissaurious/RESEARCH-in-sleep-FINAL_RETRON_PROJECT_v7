#!/usr/bin/env python3
"""Validate PROJECT_REVIEW_PACKAGE.

Checks, all read-only:
  1. every lightweight file the package references exists;
  2. every registered path that is expected to exist does exist (heavy files are stat'd, never
     re-hashed - a frozen manifest already records their identity);
  3. every git commit referenced in the registries resolves in some known worktree;
  4. no frozen source bundle was modified (git status is clean for the directories the package
     only reads);
  5. duplicate or conflicting canonical claims are flagged (same claim_id twice; a claim marked
     both ESTABLISHED and FAILED; a withdrawn claim still asserted elsewhere).

Exit code 0 = PASS (no errors; warnings allowed), 1 = FAIL.
Usage:  python3 scripts/validate_package.py [--verbose]
"""
import csv
import os
import re
import subprocess
import sys

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V7 = "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7"
WORKTREES = [V7] + [V7 + s for s in
                    ("-synthesis", "-embeddings", "-embedding-report", "-stage3c",
                     "-asset-audit", "-mestre-audit", "-spire-ncrna", "-dbchar-workbench")]

REQUIRED_FILES = [
    "README_START_HERE.md", "CURRENT_SCIENTIFIC_STATE.md", "CLAIM_EVIDENCE_MATRIX.tsv",
    "DATASET_REGISTRY.tsv", "RESULT_BUNDLE_REGISTRY.tsv", "WORKTREE_REGISTRY.tsv",
    "EXPERIMENTAL_EVIDENCE_REGISTER.tsv", "NEGATIVE_RESULTS.md", "OPEN_QUESTIONS.md",
    "CIRCULARITY_AND_LEAKAGE.md", "METHODS_REGISTRY.tsv", "PUBLICATION_OPTIONS.md",
    "THESIS_ARCHITECTURE.md", "MINIMUM_REMAINING_WORK.md", "WHAT_IS_A_RETRON.md",
    "HANDOFF_PROMPT.md", "scripts/validate_package.py",
]

errors, warnings, notes = [], [], []
VERBOSE = "--verbose" in sys.argv


def ok(msg):
    if VERBOSE:
        print("  ok   " + msg)


def read_tsv(name):
    path = os.path.join(PKG, name)
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ---------------------------------------------------------------- 1 · package files
print("1 · package files")
for rel in REQUIRED_FILES:
    p = os.path.join(PKG, rel)
    if not os.path.exists(p):
        errors.append("missing package file: %s" % rel)
    elif os.path.getsize(p) == 0:
        errors.append("empty package file: %s" % rel)
    else:
        ok(rel)

# every TSV must be rectangular
for rel in [f for f in REQUIRED_FILES if f.endswith(".tsv")]:
    p = os.path.join(PKG, rel)
    if not os.path.exists(p):
        continue
    widths = set()
    with open(p, newline="") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            widths.add(len(row))
    if len(widths) != 1:
        errors.append("ragged TSV %s: field counts %s" % (rel, sorted(widths)))
    else:
        ok("%s rectangular (%d cols)" % (rel, widths.pop()))

# ---------------------------------------------------------------- 2 · registered paths
print("2 · registered paths")
path_re = re.compile(r"(/home/borg/[^\s,;()'\"]+)")
checked, missing = set(), []
for name, col in (("DATASET_REGISTRY.tsv", "canonical_path"),
                  ("RESULT_BUNDLE_REGISTRY.tsv", "path_relative_to_its_worktree"),
                  ("WORKTREE_REGISTRY.tsv", "worktree_path")):
    if not os.path.exists(os.path.join(PKG, name)):
        continue
    for row in read_tsv(name):
        raw = row.get(col, "")
        cands = path_re.findall(raw)
        if not cands and name == "RESULT_BUNDLE_REGISTRY.tsv":
            continue                       # relative bundle path, resolved via its worktree below
        for c in cands:
            c = c.rstrip(".,;")
            if c in checked:
                continue
            checked.add(c)
            if os.path.exists(c):
                ok(c)
            else:
                missing.append((name, c))
for name, c in missing:
    # a missing heavy asset is a WARNING (it may have been archived); state it explicitly
    warnings.append("registered path not present: %s (from %s)" % (c, name))
print("   %d registered paths checked, %d missing" % (len(checked), len(missing)))

# bundle paths, resolved against their worktree
bundles = read_tsv("RESULT_BUNDLE_REGISTRY.tsv") if os.path.exists(
    os.path.join(PKG, "RESULT_BUNDLE_REGISTRY.tsv")) else []
for row in bundles:
    rel = row["path_relative_to_its_worktree"]
    if rel.startswith("/"):
        continue
    if not any(os.path.exists(os.path.join(wt, rel)) for wt in WORKTREES):
        warnings.append("bundle path not found in any worktree: %s (%s)" % (rel, row["bundle_id"]))
    else:
        ok(rel)

# ---------------------------------------------------------------- 3 · git commits
print("3 · git commits")
sha_re = re.compile(r"\b([0-9a-f]{7,40})\b")
IGNORE = {"0" * 7}


def resolves(sha):
    for wt in WORKTREES:
        if not os.path.isdir(wt):
            continue
        r = subprocess.run(["git", "-C", wt, "cat-file", "-e", sha + "^{commit}"],
                           capture_output=True)
        if r.returncode == 0:
            return True
    return False


seen = set()
for name in ("RESULT_BUNDLE_REGISTRY.tsv", "DATASET_REGISTRY.tsv", "WORKTREE_REGISTRY.tsv",
             "CLAIM_EVIDENCE_MATRIX.tsv", "METHODS_REGISTRY.tsv"):
    if not os.path.exists(os.path.join(PKG, name)):
        continue
    for row in read_tsv(name):
        for key in ("commit", "tip_commit", "source_commit"):
            for sha in sha_re.findall(row.get(key, "") or ""):
                if sha in seen or sha in IGNORE or not sha.islower():
                    continue
                seen.add(sha)
                if not resolves(sha):
                    errors.append("commit does not resolve in any worktree: %s (%s)" % (sha, name))
                else:
                    ok("commit %s" % sha)
print("   %d distinct commits checked" % len(seen))

# ---------------------------------------------------------------- 4 · frozen bundles unmodified
print("4 · frozen bundles unmodified")
READ_ONLY = {
    V7: ["results"],
    V7 + "-stage3c": ["analysis/stage3a_structural_core", "analysis/stage3b_design",
                      "analysis/stage3c_architecture_integration", "results"],
    V7 + "-embeddings": ["results"],
    V7 + "-mestre-audit": ["analysis/mestre_audit", "results"],
    V7 + "-spire-ncrna": ["analysis/spire_ncrna_audit"],
    V7 + "-embedding-report": ["analysis/embedding_report"],
}
for wt, dirs in READ_ONLY.items():
    if not os.path.isdir(wt):
        warnings.append("worktree absent: %s" % wt)
        continue
    r = subprocess.run(["git", "-C", wt, "status", "--porcelain", "--"] + dirs,
                       capture_output=True, text=True)
    dirty = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("??")]
    if dirty:
        errors.append("frozen area modified in %s:\n      %s" % (wt, "\n      ".join(dirty[:10])))
    else:
        ok("%s clean" % os.path.basename(wt))

# ---------------------------------------------------------------- 5 · claim consistency
print("5 · claim consistency")
claims = read_tsv("CLAIM_EVIDENCE_MATRIX.tsv") if os.path.exists(
    os.path.join(PKG, "CLAIM_EVIDENCE_MATRIX.tsv")) else []
ids = [c["claim_id"] for c in claims]
dupes = {i for i in ids if ids.count(i) > 1}
if dupes:
    errors.append("duplicate claim_id(s): %s" % ", ".join(sorted(dupes)))
for c in claims:
    st = c["status"].upper()
    if "ESTABLISHED" in st and "FAILED" in st:
        errors.append("%s is marked both ESTABLISHED and FAILED" % c["claim_id"])
    if not c.get("safe_thesis_wording"):
        warnings.append("%s has no safe_thesis_wording" % c["claim_id"])
    if not c.get("prohibited_overclaim"):
        warnings.append("%s has no prohibited_overclaim" % c["claim_id"])
    if not c.get("denominator"):
        warnings.append("%s has no denominator" % c["claim_id"])

# withdrawn claims must not be asserted as support elsewhere in the prose
withdrawn = [c["claim_id"] for c in claims if "WITHDRAWN" in c["status"].upper()]
notes.append("withdrawn claims: %s" % (", ".join(withdrawn) or "none"))
BANNED = [
    (r"13/14", "Stage-3C replicate figure withdrawn by blocker B1 (declared scope: 7/7 from 2 groups)"),
    (r"33/62", "Stage-3C Region-X coverage withdrawn by blocker B4 (declared rule: 24/62)"),
    (r"\bX2 (?:PASSED|FAILED)\b", "X2 must never be reported as PASS/FAIL"),
    (r"X2-A", "X2-A is a GATE LABEL, not a biological conclusion - it may appear only with its "
              "qualifier (gate/label/outcome/not a conclusion/conclusion of record)"),
]
# context words that make a mention of a banned token legitimate
ALLOW_CTX = (r"withdraw|corrected|erratum|blocker|exploratory|never|originally|not the declared"
             r"|\(not |rather than|hybrid|weaker|superseded|gate|label|outcome|qualified"
             r"|conclusion of record|headline|must not|may not|not a biological")
for md in [f for f in REQUIRED_FILES if f.endswith(".md")]:
    p = os.path.join(PKG, md)
    if not os.path.exists(p):
        continue
    text = open(p).read()
    for pat, why in BANNED:
        for m in re.finditer(pat, text):
            line = text[:m.start()].count("\n") + 1
            ctx = text[max(0, m.start() - 120):m.start() + 120].replace("\n", " ")
            if re.search(ALLOW_CTX, ctx, re.I):
                continue                    # quoted with its correction - that is the point
            errors.append("%s:%d asserts a withdrawn/prohibited figure (%s)" % (md, line, why))

# ---------------------------------------------------------------- report
print("\n" + "=" * 72)
for n in notes:
    print("NOTE    " + n)
for w in warnings:
    print("WARN    " + w)
for e in errors:
    print("ERROR   " + e)
print("=" * 72)
print("%d errors, %d warnings" % (len(errors), len(warnings)))
print("VALIDATION: " + ("FAIL" if errors else "PASS"))
sys.exit(1 if errors else 0)
