#!/usr/bin/env python3
"""REPAIR 1 - freeze integrity. Build, verify and enforce a bundle manifest.

A freeze is only real if a mutation is DETECTABLE. The previous gate was declared frozen,
was mutated mid-review by the executor, and nothing in the bundle could have revealed it;
the independent reviewer caught it only by comparing directory listings across time.

Usage:
    freeze_manifest.py build  <bundle_dir> <manifest_path>
    freeze_manifest.py verify <bundle_dir> <manifest_path>
    freeze_manifest.py lock   <bundle_dir>
    freeze_manifest.py unlock <bundle_dir>

`verify` exits NON-ZERO on any difference: changed content, added file, removed file.
Addition is a violation too - the previous breach was an ADDED file, which a
content-only checksum list would have missed entirely.
"""
import hashlib, os, sys, stat

# scripts/__pycache__ is a build artefact. `.claude` and `.mcp.json` are SANDBOX-INJECTED:
# when the shell cwd is inside a bundle the harness bind-mounts them there, and `.mcp.json`
# arrives as a character device owned by nobody. They are not project files and must never
# enter a scientific manifest.
EXCLUDE_DIRS = {"__pycache__", ".claude", ".git"}
EXCLUDE_NAMES = {".DS_Store", ".mcp.json"}


def walk(bundle):
    """Yield (relpath, abspath) for REGULAR files only.

    Non-regular entries (devices, sockets, fifos) are skipped: they are never bundle
    content, and hashing one either fails or blocks.
    """
    for root, dirs, files in os.walk(bundle):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for fn in sorted(files):
            if fn in EXCLUDE_NAMES:
                continue
            p = os.path.join(root, fn)
            if not os.path.isfile(p) or os.path.islink(p):
                continue
            if not stat.S_ISREG(os.stat(p).st_mode):
                continue
            yield os.path.relpath(p, bundle), p


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(bundle, manifest):
    # sorted by relpath, IDENTICAL to the order verify() uses. If these two orders differ
    # the root hash disagrees on an intact bundle, which would make the headline integrity
    # number meaningless. (Observed and fixed during development.)
    rows = sorted((rel, sha256(p), os.path.getsize(p)) for rel, p in walk(bundle))
    body = "".join(f"{h}  {n}  {rel}\n" for rel, h, n in rows)
    root = hashlib.sha256(body.encode()).hexdigest()
    with open(manifest, "w") as f:
        f.write("# bundle manifest - REPAIR 1 freeze integrity\n")
        f.write(f"# files: {len(rows)}\n")
        f.write(f"# ROOT_SHA256: {root}\n")
        f.write(body)
    print(f"built {manifest}: {len(rows)} files")
    print(f"ROOT_SHA256 {root}")
    return root


def read_manifest(manifest):
    rows, root = {}, None
    for ln in open(manifest):
        if ln.startswith("# ROOT_SHA256:"):
            root = ln.split(":", 1)[1].strip()
        if ln.startswith("#"):
            continue
        h, n, rel = ln.rstrip("\n").split("  ", 2)
        rows[rel] = (h, int(n))
    return rows, root


def verify(bundle, manifest):
    want, want_root = read_manifest(manifest)
    have = {rel: (sha256(p), os.path.getsize(p)) for rel, p in walk(bundle)}
    added = sorted(set(have) - set(want))
    removed = sorted(set(want) - set(have))
    changed = sorted(r for r in set(want) & set(have) if have[r][0] != want[r][0])
    body = "".join(f"{have[r][0]}  {have[r][1]}  {r}\n" for r in sorted(have))
    root = hashlib.sha256(body.encode()).hexdigest()
    ok = not (added or removed or changed)
    for r in added:
        print(f"FREEZE VIOLATION  ADDED    {r}")
    for r in removed:
        print(f"FREEZE VIOLATION  REMOVED  {r}")
    for r in changed:
        print(f"FREEZE VIOLATION  CHANGED  {r}")
    print(f"expected ROOT_SHA256 {want_root}")
    print(f"observed ROOT_SHA256 {root}")
    if ok:
        print("FREEZE INTACT")
        return 0
    print(f"FREEZE BROKEN: {len(added)} added, {len(removed)} removed, {len(changed)} changed")
    return 1


def chmod_tree(bundle, lock):
    n = 0
    for _, p in walk(bundle):
        m = os.stat(p).st_mode
        new = (m & ~0o222) if lock else (m | stat.S_IWUSR)
        if new != m:
            os.chmod(p, new)
            n += 1
    print(("locked " if lock else "unlocked ") + f"{n} file(s) under {bundle}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    if cmd == "build":
        build(sys.argv[2], sys.argv[3])
    elif cmd == "verify":
        sys.exit(verify(sys.argv[2], sys.argv[3]))
    elif cmd == "lock":
        chmod_tree(sys.argv[2], True)
    elif cmd == "unlock":
        chmod_tree(sys.argv[2], False)
    else:
        raise SystemExit(__doc__)
