#!/usr/bin/env python3
"""REPAIRS 2 + 3 tests - every fail-open path the reviewer found now has a negative control.

Each test asserts BOTH directions where that is meaningful: the good case must pass AND the
bad case must be detected. A freeze checker that cannot be made to report a violation is worth
nothing.

Runs entirely on a synthetic bundle in a temp directory. It never reads or writes a real
result bundle.

    freeze_tests.py <tmp_root> <tables_dir>
"""
import os, shutil, stat, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FM = os.path.join(HERE, "freeze_manifest.py")
TMP, TABLES = sys.argv[1], sys.argv[2]
ROOT = os.path.join(TMP, "freeze_synthetic")
MAN = os.path.join(TMP, "freeze_synthetic.MANIFEST")
rows = []


def fm(*a):
    r = subprocess.run([sys.executable, FM, *a], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def unlock_tree(path):
    for root, dirs, files in os.walk(path):
        os.chmod(root, 0o755)
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            try:
                os.chmod(os.path.join(root, f), 0o644)
            except FileNotFoundError:
                pass


def fresh():
    if os.path.isdir(ROOT):
        unlock_tree(ROOT)
        shutil.rmtree(ROOT)
    os.makedirs(os.path.join(ROOT, "control"))
    os.makedirs(os.path.join(ROOT, "tables"))
    open(os.path.join(ROOT, "control", "decl.md"), "w").write("frozen declaration\n")
    open(os.path.join(ROOT, "tables", "res.tsv"), "w").write("a\tb\n1\t2\n")
    fm("build", ROOT, MAN)


def rec(name, cls, ok, detail, passes_when, fails_when, pos, neg):
    rows.append([name, cls, "PASS" if ok else "FAIL", detail, passes_when, fails_when, pos, neg])


# ---- F1 positive: intact bundle verifies, exit 0 -----------------------------------------
fresh()
c, out = fm("verify", ROOT, MAN)
rec("F1_intact_bundle_verifies", "FALSIFIABLE_EMPIRICAL_TEST",
    c == 0 and "FREEZE INTACT" in out, f"exit={c}",
    "an untouched bundle verifies clean", "any violation is reported",
    "synthetic untouched bundle", "every F2-F10 mutation below (all EXECUTED)")

# ---- F1b root hash reproducible ----------------------------------------------------------
_, o1 = fm("build", ROOT, MAN + ".a")
_, o2 = fm("build", ROOT, MAN + ".b")
h1 = [l for l in o1.splitlines() if l.startswith("ROOT_SHA256")][0]
h2 = [l for l in o2.splitlines() if l.startswith("ROOT_SHA256")][0]
rec("F1b_root_hash_reproducible", "FALSIFIABLE_EMPIRICAL_TEST", h1 == h2,
    f"{h1[:24]} vs {h2[:24]}", "two builds of the same tree give the same root",
    "root construction is order-dependent or nondeterministic",
    "same bundle built twice", "n/a - determinism assertion")

# ---- F1c build and verify agree (caught a real v1 defect) --------------------------------
fresh()
c, out = fm("verify", ROOT, MAN)
exp = [l.split()[-1] for l in out.splitlines() if l.startswith("expected")][0]
obs = [l.split()[-1] for l in out.splitlines() if l.startswith("observed")][0]
rec("F1c_build_and_verify_agree", "FALSIFIABLE_EMPIRICAL_TEST", exp == obs,
    f"{exp[:16]}/{obs[:16]}", "build order and verify order produce the same root",
    "they disagree on an intact bundle",
    "intact bundle", "v1 hashed in walk order vs sorted order - this test pinned it")

# ---- F2 ADDED (the breach that actually happened) ----------------------------------------
fresh()
open(os.path.join(ROOT, "control", "sneaky_note.md"), "w").write("added mid-review\n")
c, out = fm("verify", ROOT, MAN)
rec("F2_added_file_detected", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "ADDED" in out and "sneaky_note.md" in out, f"exit={c}",
    "an added file is reported and exit is non-zero",
    "an addition passes - a content-only checksum list would miss it",
    "intact bundle", "one file added to control/ (EXECUTED)")

# ---- F3 CHANGED --------------------------------------------------------------------------
fresh()
open(os.path.join(ROOT, "control", "decl.md"), "a").write("x")
c, out = fm("verify", ROOT, MAN)
rec("F3_changed_file_detected", "FALSIFIABLE_EMPIRICAL_TEST", c != 0 and "CHANGED" in out,
    f"exit={c}", "a modified byte is reported", "a modification passes",
    "intact bundle", "one byte appended (EXECUTED)")

# ---- F4 REMOVED --------------------------------------------------------------------------
fresh()
os.remove(os.path.join(ROOT, "tables", "res.tsv"))
c, out = fm("verify", ROOT, MAN)
rec("F4_removed_file_detected", "FALSIFIABLE_EMPIRICAL_TEST", c != 0 and "REMOVED" in out,
    f"exit={c}", "a deleted file is reported", "a deletion passes",
    "intact bundle", "one file deleted (EXECUTED)")

# ---- F5 RENAMED --------------------------------------------------------------------------
fresh()
os.rename(os.path.join(ROOT, "tables", "res.tsv"), os.path.join(ROOT, "tables", "res2.tsv"))
c, out = fm("verify", ROOT, MAN)
rec("F5_rename_detected", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "ADDED" in out and "REMOVED" in out, f"exit={c}",
    "a rename is reported as both ADDED and REMOVED", "a rename passes",
    "intact bundle", "one file renamed, content unchanged (EXECUTED)")

# ---- F6 MISSING MANIFEST must fail (v1 fail-open #1) -------------------------------------
fresh()
c, out = fm("verify", ROOT, MAN + ".does_not_exist")
rec("F6_missing_manifest_fails_closed", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "MANIFEST ABSENT" in out, f"exit={c}",
    "a missing manifest is a failure",
    "absence of provenance reports success - v1 printed a note and exited 0",
    "present manifest in F1", "manifest path that does not exist (EXECUTED)")

# ---- F7 CORRUPTED ROOT HEADER must fail (v1 fail-open #2) --------------------------------
fresh()
bad = MAN + ".corruptroot"
src = open(MAN).read()
open(bad, "w").write(src.replace(
    [l.split(": ")[1].strip() for l in src.splitlines() if "ROOT_SHA256:" in l][0], "0" * 64))
open(bad + ".sha256", "w").write(__import__("hashlib").sha256(
    open(bad, "rb").read()).hexdigest() + "\n")
c, out = fm("verify", ROOT, bad)
rec("F7_corrupt_root_header_fails_closed", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "ROOT MISMATCH" in out, f"exit={c}",
    "a root header that disagrees with the observed root fails",
    "the root is decorative - v1 returned exit 0 and FREEZE INTACT on an all-zero root",
    "genuine manifest in F1", "all-zero expected root over genuine rows (EXECUTED)")

# ---- F8 TAMPERED MANIFEST must fail (sidecar) --------------------------------------------
fresh()
tam = MAN + ".tampered"
shutil.copy(MAN, tam)
shutil.copy(MAN + ".sha256", tam + ".sha256")       # stale sidecar
lines = open(tam).read().splitlines(True)
for i, l in enumerate(lines):
    if l.rstrip().endswith("control/decl.md"):
        lines[i] = "0" * 64 + l[64:]
        break
open(tam, "w").writelines(lines)
c, out = fm("verify", ROOT, tam)
rec("F8_tampered_manifest_detected", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "MANIFEST TAMPERED" in out, f"exit={c}",
    "editing the manifest is caught by its detached sidecar",
    "the manifest can be rewritten to match a mutated bundle",
    "untampered manifest + sidecar", "one manifest row hash rewritten (EXECUTED)")

# ---- F9 EXPECTED-ROOT argument must fail on mismatch --------------------------------------
fresh()
c, out = fm("verify", ROOT, MAN, "f" * 64)
rec("F9_caller_expected_root_enforced", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "EXPECTED ROOT MISMATCH" in out, f"exit={c}",
    "a caller-supplied expected root is enforced",
    "the caller's pinned root is ignored",
    "F1 verify with no expected root", "deliberately wrong expected root (EXECUTED)")

# ---- F10 DIRECTORY LOCK must prevent add AND delete (v1 fail-open #3) ---------------------
fresh()
fm("lock", ROOT)
d = os.path.join(ROOT, "control")
f_in = os.path.join(d, "decl.md")
dir_ro = not (os.stat(d).st_mode & 0o222)
try:
    open(os.path.join(d, "added_after_lock.md"), "w").write("x")
    could_add = True
except PermissionError:
    could_add = False
try:
    os.remove(f_in)
    could_delete = True
except PermissionError:
    could_delete = False
try:
    os.rename(f_in, f_in + ".renamed")
    could_rename = True
except (PermissionError, FileNotFoundError):
    could_rename = False
fm("unlock", ROOT)
unlocked = bool(os.stat(d).st_mode & 0o200)
rec("F10_directory_lock_blocks_add_delete_rename", "FALSIFIABLE_EMPIRICAL_TEST",
    dir_ro and not could_add and not could_delete and not could_rename and unlocked,
    f"dir_readonly={dir_ro} add_blocked={not could_add} delete_blocked={not could_delete} "
    f"rename_blocked={not could_rename} unlock_ok={unlocked}",
    "a locked bundle refuses file creation, deletion and rename",
    "chmod on files alone - v1 left directories 775, so add/delete/replace still worked",
    "unlocked bundle permits all three", "locked bundle, all three attempted (EXECUTED)")

# ---- F11 pycache is now manifested, not excluded ------------------------------------------
fresh()
os.makedirs(os.path.join(ROOT, "scripts", "__pycache__"), exist_ok=True)
open(os.path.join(ROOT, "scripts", "__pycache__", "x.cpython-312.pyc"), "wb").write(b"\x00\x01")
c, out = fm("verify", ROOT, MAN)
rec("F11_bytecode_not_invisible", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "ADDED" in out and "__pycache__" in out, f"exit={c}",
    "a stray .pyc is an ADDED file, not an invisible one",
    "__pycache__ is excluded from the manifest, so bytecode writes go unnoticed (v1)",
    "bundle with no __pycache__", "a .pyc created after freeze (EXECUTED)")

unlock_tree(ROOT)
shutil.rmtree(ROOT, ignore_errors=True)
with open(os.path.join(TABLES, "freeze_integrity_tests.tsv"), "w") as f:
    f.write("test\tclassification\tresult\tdetail\tpasses_when\tfails_when\t"
            "positive_control\tnegative_control\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[2]:4s} {r[0]:44s} {r[3]}")
bad_rows = [r for r in rows if r[2] != "PASS"]
print(f"\n{len(rows)-len(bad_rows)}/{len(rows)} passed")
sys.exit(1 if bad_rows else 0)
