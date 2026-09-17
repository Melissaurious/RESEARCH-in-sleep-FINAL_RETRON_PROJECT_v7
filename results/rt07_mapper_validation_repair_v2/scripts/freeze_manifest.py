#!/usr/bin/env python3
"""REPAIRS 2 + 3 - fail-closed freeze integrity.

v1 had three fail-open paths, all found by independent review or by these tests:

  1. a MISSING manifest let verify.sh still print VERIFY OK;
  2. a CORRUPTED root header verified clean - `ok` was computed from added/removed/changed and
     never compared the roots, so an all-zero expected root returned exit 0 "FREEZE INTACT".
     The headline integrity number was decorative;
  3. `lock()` chmodded files but not DIRECTORIES, so files could still be added, deleted or
     atomically replaced inside a "locked" bundle.

Everything now fails closed. Nothing prints INTACT unless every assertion passes.

The manifest protects the bundle; a detached sidecar (`<manifest>.sha256`) protects the
manifest. The sidecar lives beside the manifest, which lives OUTSIDE the bundle it validates.

Usage:
    freeze_manifest.py build   <bundle_dir> <manifest_path>
    freeze_manifest.py verify  <bundle_dir> <manifest_path> [expected_root_sha256]
    freeze_manifest.py lock    <bundle_dir>
    freeze_manifest.py unlock  <bundle_dir>
"""
import hashlib, os, stat, sys

# `.claude` and `.mcp.json` are SANDBOX-INJECTED when a shell cwd sits inside a bundle;
# `.mcp.json` arrives as a character device owned by nobody. They are not project files.
# `__pycache__` is NOT excluded any more - see REPAIR 3. Bytecode is suppressed at generation
# time instead, so an unmanifested cache cannot exist unnoticed.
EXCLUDE_DIRS = {".claude", ".git"}
EXCLUDE_NAMES = {".DS_Store", ".mcp.json"}


def walk(bundle):
    """Yield (relpath, abspath) for REGULAR files only, in sorted order."""
    for root, dirs, files in os.walk(bundle):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for fn in sorted(files):
            if fn in EXCLUDE_NAMES:
                continue
            p = os.path.join(root, fn)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            if not stat.S_ISREG(os.stat(p).st_mode):
                continue
            yield os.path.relpath(p, bundle), p


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _body(rows):
    return "".join(f"{h}  {n}  {rel}\n" for rel, h, n in rows)


def build(bundle, manifest):
    rows = sorted((rel, sha256_file(p), os.path.getsize(p)) for rel, p in walk(bundle))
    body = _body(rows)
    root = hashlib.sha256(body.encode()).hexdigest()
    with open(manifest, "w") as f:
        f.write("# bundle manifest - REPAIRS 2+3 fail-closed freeze integrity\n")
        f.write(f"# files: {len(rows)}\n")
        f.write(f"# ROOT_SHA256: {root}\n")
        f.write(body)
    # REPAIR 3: detached sidecar authenticating the manifest itself
    with open(manifest + ".sha256", "w") as f:
        f.write(sha256_file(manifest) + "\n")
    print(f"built {manifest}: {len(rows)} files")
    print(f"ROOT_SHA256 {root}")
    return root


def read_manifest(manifest):
    rows, root, n_declared = {}, None, None
    for ln in open(manifest):
        if ln.startswith("# ROOT_SHA256:"):
            root = ln.split(":", 1)[1].strip()
            continue
        if ln.startswith("# files:"):
            n_declared = int(ln.split(":", 1)[1].strip())
            continue
        if ln.startswith("#"):
            continue
        try:
            h, n, rel = ln.rstrip("\n").split("  ", 2)
            rows[rel] = (h, int(n))
        except ValueError:
            raise ValueError(f"malformed manifest row: {ln!r}")
    return rows, root, n_declared


def verify(bundle, manifest, expected_root=None):
    """Exit code 0 ONLY when every assertion passes."""
    problems = []

    if not os.path.isfile(manifest):
        print(f"FREEZE VIOLATION  MANIFEST ABSENT  {manifest}")
        print("FREEZE BROKEN: no provenance. Absence of a manifest is a failure, not a note.")
        return 1

    # --- the manifest itself must be authentic -------------------------------------------
    side = manifest + ".sha256"
    if not os.path.isfile(side):
        problems.append(f"MANIFEST SIDECAR ABSENT  {side}")
    else:
        want_side = open(side).read().strip()
        have_side = sha256_file(manifest)
        if want_side != have_side:
            problems.append(f"MANIFEST TAMPERED  sidecar {want_side[:16]} != actual "
                            f"{have_side[:16]}")

    try:
        want, want_root, n_declared = read_manifest(manifest)
    except ValueError as e:
        print(f"FREEZE VIOLATION  MANIFEST MALFORMED  {e}")
        print("FREEZE BROKEN")
        return 1

    if not want_root:
        problems.append("MANIFEST HEADER MISSING ROOT_SHA256")
    if n_declared is not None and n_declared != len(want):
        problems.append(f"MANIFEST ROW COUNT  header says {n_declared}, {len(want)} rows present")

    # --- the bundle must match the manifest ------------------------------------------------
    have = {rel: (sha256_file(p), os.path.getsize(p)) for rel, p in walk(bundle)}
    added = sorted(set(have) - set(want))
    removed = sorted(set(want) - set(have))
    changed = sorted(r for r in set(want) & set(have) if have[r][0] != want[r][0])
    for r in added:
        problems.append(f"ADDED    {r}")
    for r in removed:
        problems.append(f"REMOVED  {r}")
    for r in changed:
        problems.append(f"CHANGED  {r}")

    rows = sorted((r, have[r][0], have[r][1]) for r in have)
    root = hashlib.sha256(_body(rows).encode()).hexdigest()

    # --- REPAIR 2: the root comparison is part of the verdict, not decoration --------------
    if want_root and root != want_root:
        problems.append(f"ROOT MISMATCH  manifest {want_root[:16]} != observed {root[:16]}")
    if expected_root and root != expected_root:
        problems.append(f"EXPECTED ROOT MISMATCH  caller expected {expected_root[:16]} != "
                        f"observed {root[:16]}")

    print(f"expected ROOT_SHA256 {want_root}")
    print(f"observed ROOT_SHA256 {root}")
    for p in problems:
        print(f"FREEZE VIOLATION  {p}")
    if problems:
        print(f"FREEZE BROKEN: {len(problems)} violation(s)")
        return 1
    print("FREEZE INTACT")
    return 0


def chmod_tree(bundle, lock):
    """REPAIR 3: lock DIRECTORIES as well as files.

    A read-only file inside a writable directory can still be deleted, renamed or atomically
    replaced - `chmod 444` on the file does not prevent unlink. Clearing write on the
    directory is what actually freezes the namespace.
    """
    nf = nd = 0
    dirs = []
    # EXCLUDE_DIRS must be applied here too. A raw os.walk descends into `.claude`, which the
    # sandbox bind-mounts read-only; chmod there raises EROFS, so locking aborted partway and
    # left the bundle HALF-LOCKED. (Observed and fixed during development - a half-locked
    # bundle is worse than an unlocked one, because it looks locked.)
    for root, dnames, _ in os.walk(bundle):
        dnames[:] = [d for d in dnames if d not in EXCLUDE_DIRS]
        dirs.append(root)
        for d in dnames:
            dirs.append(os.path.join(root, d))
    for _, p in walk(bundle):
        m = os.stat(p).st_mode
        new = (m & ~0o222) if lock else (m | stat.S_IWUSR)
        if new != m:
            os.chmod(p, new)
            nf += 1
    # deepest-first when locking so we never lock a parent before its children
    for d in sorted(set(dirs), key=len, reverse=not lock):
        m = os.stat(d).st_mode
        new = (m & ~0o222) if lock else (m | stat.S_IWUSR)
        if new != m:
            os.chmod(d, new)
            nd += 1
    print(("locked " if lock else "unlocked ") + f"{nf} file(s) and {nd} director(ies) "
          f"under {bundle}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    if cmd == "build":
        build(sys.argv[2], sys.argv[3])
    elif cmd == "verify":
        sys.exit(verify(sys.argv[2], sys.argv[3],
                        sys.argv[4] if len(sys.argv) > 4 else None))
    elif cmd == "lock":
        chmod_tree(sys.argv[2], True)
    elif cmd == "unlock":
        chmod_tree(sys.argv[2], False)
    else:
        raise SystemExit(__doc__)
