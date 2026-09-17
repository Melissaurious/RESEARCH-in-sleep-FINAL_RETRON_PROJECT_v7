#!/usr/bin/env python3
"""Freeze negative-test matrix. Every declared corruption must exit non-zero.

Covers the fifteen cases the operator enumerated, plus hard-link aliasing. Runs entirely on
a synthetic bundle in a temp directory; no real bundle is read or written.

    tests_freeze.py <tmp_root> <tables_dir>
"""
import hashlib, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IG = os.path.join(HERE, "integrity.py")
TMP, TABLES = sys.argv[1], sys.argv[2]
ROOT = os.path.join(TMP, "frz")
MAN = os.path.join(TMP, "frz.MANIFEST")
rows = []
GOOD_ROOT = [None]


def ig(*a):
    r = subprocess.run([sys.executable, "-B", IG, *a], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def unlock(path):
    for root, dirs, files in os.walk(path):
        os.chmod(root, 0o755)
        for d in dirs:
            try:
                os.chmod(os.path.join(root, d), 0o755)
            except OSError:
                pass
        for f in files:
            try:
                os.chmod(os.path.join(root, f), 0o644)
            except OSError:
                pass


def fresh():
    if os.path.isdir(ROOT):
        unlock(ROOT)
        shutil.rmtree(ROOT)
    os.makedirs(os.path.join(ROOT, "code"))
    os.makedirs(os.path.join(ROOT, "tables"))
    open(os.path.join(ROOT, "code", "m.py"), "w").write("X = 1\n")
    open(os.path.join(ROOT, "tables", "r.tsv"), "w").write("a\tb\n1\t2\n")
    _, out = ig("build", ROOT, MAN)
    GOOD_ROOT[0] = [l.split()[-1] for l in out.splitlines()
                    if l.startswith("ROOT_SHA256")][0]


def sanitise(text):
    """Strip environment-specific paths from anything that will be LANDED.

    A landed product embedding an absolute temp path is not reproducible: the frozen row
    carried /tmp/... while a reviewer running under /dev/shm regenerated a different string,
    so verify.sh failed on a purely environmental difference. Canonical outputs carry logical
    labels; the real paths stay in the runtime log, which is not compared.
    """
    out = text.replace(MAN, "<MANIFEST>").replace(ROOT, "<BUNDLE>").replace(TMP, "<TMP>")
    return re.sub(r"(/|\\)[^\s\'\"]*?(frz[^\s\'\"]*)", r"<TMP>/\2", out)


def rec(name, ok, detail, expect):
    rows.append([name, "PASS" if ok else "FAIL", sanitise(detail), expect])


def must_fail(name, mutate, expect_token, expect_desc):
    fresh()
    mutate()
    c, out = ig("verify", ROOT, MAN, GOOD_ROOT[0])
    ok = c != 0 and (expect_token in out if expect_token else True)
    rec(name, ok, f"exit={c}; " + "; ".join(
        l for l in out.splitlines() if "VIOLATION" in l)[:150], expect_desc)


# ---- positive control: an untouched bundle with the right pinned root must PASS --------
fresh()
c, out = ig("verify", ROOT, MAN, GOOD_ROOT[0])
rec("P1_intact_with_correct_pinned_root", c == 0 and "FREEZE INTACT" in out, f"exit={c}",
    "an untouched bundle with the correct external root verifies clean")

# ---- the fifteen declared corruption cases -------------------------------------------
must_fail("N1_added_regular_file",
          lambda: open(os.path.join(ROOT, "tables", "extra.tsv"), "w").write("x"),
          "ADDED", "an added regular file fails")

must_fail("N2_deleted_file", lambda: os.remove(os.path.join(ROOT, "tables", "r.tsv")),
          "REMOVED", "a deleted file fails")

must_fail("N3_changed_file",
          lambda: open(os.path.join(ROOT, "code", "m.py"), "a").write("Y = 2\n"),
          "CHANGED", "a modified file fails")

must_fail("N4_renamed_file",
          lambda: os.rename(os.path.join(ROOT, "tables", "r.tsv"),
                            os.path.join(ROOT, "tables", "r2.tsv")),
          "ADDED", "a rename fails (as ADDED + REMOVED)")

must_fail("N5_added_file_symlink",
          lambda: os.symlink(os.path.join(ROOT, "code", "m.py"),
                             os.path.join(ROOT, "code", "injected.py")),
          "SYMLINK", "an added symlink fails - v2 SKIPPED symlinks and reported INTACT")

def _replace_with_symlink():
    p = os.path.join(ROOT, "code", "m.py")
    os.remove(p)
    os.symlink(os.path.join(ROOT, "tables", "r.tsv"), p)
must_fail("N6_symlink_replacing_registered_script", _replace_with_symlink,
          "SYMLINK", "a registered script replaced by a symlink fails")

must_fail("N7_symlink_escaping_bundle_root",
          lambda: os.symlink("/etc/hostname", os.path.join(ROOT, "code", "escape.py")),
          "SYMLINK", "a symlink pointing outside the bundle fails")

must_fail("N8_symlink_to_other_registered_artifact",
          lambda: os.symlink(os.path.join(ROOT, "tables", "r.tsv"),
                             os.path.join(ROOT, "tables", "alias.tsv")),
          "SYMLINK", "a symlink to another registered artifact fails")

must_fail("N9_missing_manifest",
          lambda: os.remove(MAN), "MANIFEST ABSENT", "a missing manifest fails")

def _malform():
    open(MAN, "w").write("not a manifest at all\n")
must_fail("N10_malformed_manifest", _malform, None, "a malformed manifest fails")

def _corrupt_root():
    s = open(MAN).read()
    cur = [l.split(": ")[1].strip() for l in s.splitlines() if "ROOT_SHA256:" in l][0]
    open(MAN, "w").write(s.replace(cur, "b" * 64))
    open(MAN + ".sha256", "w").write(
        hashlib.sha256(open(MAN, "rb").read()).hexdigest() + "\n")
must_fail("N11_corrupted_manifest_root", _corrupt_root, "MANIFEST ROOT MISMATCH",
          "a corrupted manifest root fails even with a recomputed sidecar")

# all-zero pinned root supplied by the caller
fresh()
c, out = ig("verify", ROOT, MAN, "0" * 64)
rec("N12_all_zero_pinned_root", c != 0 and "MALFORMED OR ALL-ZERO" in out, f"exit={c}",
    "an all-zero external pinned root is rejected outright")

# wrong external pinned root
fresh()
c, out = ig("verify", ROOT, MAN, "a" * 64)
rec("N13_wrong_external_pinned_root", c != 0 and "EXTERNAL PINNED ROOT MISMATCH" in out,
    f"exit={c}", "a wrong external pinned root fails")

# absent pinned root - there is no unpinned mode
fresh()
c, out = ig("verify", ROOT, MAN)
rec("N14_absent_pinned_root", c != 0 and "PINNED ROOT ABSENT" in out, f"exit={c}",
    "omitting the external root fails; v2 allowed an unpinned self-validating mode")

# the decisive one: bundle + manifest + sidecar all rebuilt together must STILL fail
# against the externally held root
fresh()
good = GOOD_ROOT[0]
open(os.path.join(ROOT, "code", "m.py"), "w").write("X = 999  # tampered\n")
ig("build", ROOT, MAN)                       # attacker regenerates manifest AND sidecar
c, out = ig("verify", ROOT, MAN, good)
rec("N15_self_consistent_rebuild_still_fails",
    c != 0 and "EXTERNAL PINNED ROOT MISMATCH" in out, f"exit={c}",
    "a jointly rebuilt bundle+manifest+sidecar cannot self-validate against the external root")

must_fail("N16_unexpected_bytecode",
          lambda: (os.makedirs(os.path.join(ROOT, "code", "__pycache__"), exist_ok=True),
                   open(os.path.join(ROOT, "code", "__pycache__", "m.cpython-312.pyc"),
                        "wb").write(b"\x00")),
          "ADDED", "a stray .pyc is an ADDED violation, not an invisible file")

def _hardlink():
    alias = os.path.join(TMP, "alias_outside.tsv")
    if os.path.exists(alias):          # a previous run's alias would make os.link raise
        os.remove(alias)
    os.link(os.path.join(ROOT, "tables", "r.tsv"), alias)
must_fail("N17_hard_link_aliasing", _hardlink, "HARD-LINKED",
          "a file aliased by a hard link outside the bundle fails")

unlock(ROOT)
shutil.rmtree(ROOT, ignore_errors=True)
with open(f"{TABLES}/freeze_negative_test_matrix.tsv", "w") as f:
    f.write("test\tresult\tdetail\texpectation\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[1]:4s} {r[0]:44s} {r[2][:95]}")
bad = [r for r in rows if r[1] != "PASS"]
print(f"\n{len(rows)-len(bad)}/{len(rows)} passed")
sys.exit(1 if bad else 0)
