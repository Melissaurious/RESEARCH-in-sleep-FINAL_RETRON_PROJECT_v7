#!/usr/bin/env python3
"""REPAIR 1 tests - each has a POSITIVE control (must pass) and a NEGATIVE control (must fail).

A freeze checker that cannot be made to report a violation is worth nothing, so every test
here asserts BOTH directions. Runs entirely on a synthetic bundle in a temp directory; it
never reads or writes any real result bundle.

    freeze_tests.py <tmp_root> <tables_dir>
"""
import os, shutil, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FM = os.path.join(HERE, "freeze_manifest.py")
TMP, TABLES = sys.argv[1], sys.argv[2]
ROOT = os.path.join(TMP, "freeze_synthetic")
MAN = os.path.join(TMP, "freeze_synthetic.MANIFEST")
rows = []


def fm(*a):
    r = subprocess.run([sys.executable, FM, *a], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def fresh():
    if os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(os.path.join(ROOT, "control"))
    os.makedirs(os.path.join(ROOT, "tables"))
    open(os.path.join(ROOT, "control", "decl.md"), "w").write("frozen declaration\n")
    open(os.path.join(ROOT, "tables", "res.tsv"), "w").write("a\tb\n1\t2\n")
    fm("build", ROOT, MAN)


def rec(name, kind, ok, detail):
    rows.append([name, kind, "PASS" if ok else "FAIL", detail])


# F1 positive: an untouched bundle verifies clean and exits 0
fresh()
c, out = fm("verify", ROOT, MAN)
rec("F1_intact_bundle_verifies", "FALSIFIABLE_EMPIRICAL_TEST", c == 0 and "FREEZE INTACT" in out,
    f"exit={c}")

# F1b: the root hash must be REPRODUCIBLE, not merely self-consistent. build twice, compare.
c1, o1 = fm("build", ROOT, MAN + ".a")
c2, o2 = fm("build", ROOT, MAN + ".b")
h1 = [l for l in o1.splitlines() if l.startswith("ROOT_SHA256")][0]
h2 = [l for l in o2.splitlines() if l.startswith("ROOT_SHA256")][0]
rec("F1b_root_hash_reproducible", "FALSIFIABLE_EMPIRICAL_TEST", h1 == h2, f"{h1[:24]} vs {h2[:24]}")

# F1c: build and verify must agree on an intact bundle. This caught a REAL defect during
# development: build hashed in os.walk order, verify in sorted order, so the root hashes
# disagreed while the bundle was intact.
c, out = fm("verify", ROOT, MAN)
exp = [l.split()[-1] for l in out.splitlines() if l.startswith("expected")][0]
obs = [l.split()[-1] for l in out.splitlines() if l.startswith("observed")][0]
rec("F1c_build_and_verify_agree", "FALSIFIABLE_EMPIRICAL_TEST", exp == obs, f"{exp[:16]}/{obs[:16]}")

# F2 NEGATIVE: an ADDED file must be detected. This is the exact breach that occurred -
# a content-only checksum list would not have caught it.
fresh()
open(os.path.join(ROOT, "control", "sneaky_note.md"), "w").write("added mid-review\n")
c, out = fm("verify", ROOT, MAN)
rec("F2_added_file_detected", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "ADDED" in out and "sneaky_note.md" in out, f"exit={c}")

# F3 NEGATIVE: a CHANGED byte must be detected
fresh()
open(os.path.join(ROOT, "control", "decl.md"), "a").write("x")
c, out = fm("verify", ROOT, MAN)
rec("F3_changed_file_detected", "FALSIFIABLE_EMPIRICAL_TEST", c != 0 and "CHANGED" in out,
    f"exit={c}")

# F4 NEGATIVE: a REMOVED file must be detected
fresh()
os.remove(os.path.join(ROOT, "tables", "res.tsv"))
c, out = fm("verify", ROOT, MAN)
rec("F4_removed_file_detected", "FALSIFIABLE_EMPIRICAL_TEST", c != 0 and "REMOVED" in out,
    f"exit={c}")

# F5 NEGATIVE: a rename (remove + add, same content) must be detected as BOTH
fresh()
os.rename(os.path.join(ROOT, "tables", "res.tsv"), os.path.join(ROOT, "tables", "res2.tsv"))
c, out = fm("verify", ROOT, MAN)
rec("F5_rename_detected", "FALSIFIABLE_EMPIRICAL_TEST",
    c != 0 and "ADDED" in out and "REMOVED" in out, f"exit={c}")

# F6: lock() actually removes write permission; unlock restores it
fresh()
fm("lock", ROOT)
p = os.path.join(ROOT, "control", "decl.md")
locked = not (os.stat(p).st_mode & 0o222)
try:
    open(p, "a").write("y")
    wrote = True
except PermissionError:
    wrote = False
fm("unlock", ROOT)
unlocked = bool(os.stat(p).st_mode & 0o200)
rec("F6_lock_blocks_writes", "FALSIFIABLE_EMPIRICAL_TEST",
    locked and not wrote and unlocked, f"locked={locked} write_blocked={not wrote} unlock_ok={unlocked}")

# F7: non-regular files (sandbox-injected .mcp.json char device) and .claude/ are excluded.
# IMPLEMENTATION_INVARIANT: asserts a stated exclusion policy, not an empirical fact.
fresh()
os.makedirs(os.path.join(ROOT, ".claude"), exist_ok=True)
open(os.path.join(ROOT, ".claude", "settings.json"), "w").write("{}\n")
c, out = fm("verify", ROOT, MAN)
rec("F7_sandbox_artefacts_excluded", "IMPLEMENTATION_INVARIANT", c == 0,
    "'.claude/' ignored by policy")

shutil.rmtree(ROOT, ignore_errors=True)
with open(os.path.join(TABLES, "freeze_integrity_tests.tsv"), "w") as f:
    f.write("test\tclassification\tresult\tdetail\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[2]:4s} {r[0]:32s} [{r[1]}] {r[3]}")
bad = [r for r in rows if r[2] != "PASS"]
print(f"\n{len(rows)-len(bad)}/{len(rows)} passed")
sys.exit(1 if bad else 0)
