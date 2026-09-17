#!/usr/bin/env python3
"""Clean-room integrity: manifest, symlink detection, EXTERNAL pinned root.

Closes the infrastructure defects found across v1 and v2:

  v1  missing manifest failed OPEN
  v1  corrupted root header failed OPEN (root never entered the verdict)
  v1  lock() chmodded files, not directories
  v1  __pycache__ excluded from the manifest, so bytecode writes were invisible
  v2  walk() SKIPPED symlinks, so an added symlink verified INTACT
  v2  verify.sh accepted an omitted expected root, so a jointly rebuilt
      bundle+manifest+sidecar self-validated

Design rules here:
  * NOTHING is excluded from hashing except a small, explicitly declared set of
    sandbox-injected paths, and every exclusion is REPORTED in the verify output.
  * Symlinks are DETECTED and are a violation, never skipped.
  * The expected root MUST be supplied from outside the bundle. There is no
    "verify without a pinned root" mode.

Honest limit, stated rather than overclaimed: this is CRYPTOGRAPHIC DETECTION, not OS
immutability. A process running as this user can rewrite the bundle, the manifest, the
sidecar and the external root file together. What it cannot do is make those edits
invisible to a reviewer holding the root value out-of-band (in the review request, which
is what the reviewer is given). Filesystem permissions here are a speed bump; the root
value in the reviewer's hands is the trust anchor.
"""
import hashlib, os, stat, sys

# Sandbox-injected by the harness when a shell cwd sits inside the bundle. `.mcp.json`
# arrives as a character device owned by nobody and cannot be hashed. Every exclusion is
# printed by verify() so it is never a silent blind spot (the v1 __pycache__ lesson).
EXCLUDED_DIRS = {".claude", ".git"}
EXCLUDED_NAMES = {".mcp.json"}


class Finding(list):
    pass


def scan(bundle):
    """Return (regular_files, symlinks, irregular, excluded).

    Symlinks and non-regular entries are RETURNED, not skipped - the caller decides, and
    the decision is that they are violations.
    """
    regular, symlinks, irregular, excluded = [], [], [], []
    for root, dirs, files in os.walk(bundle, followlinks=False):
        for d in sorted(dirs):
            p = os.path.join(root, d)
            if d in EXCLUDED_DIRS:
                excluded.append(os.path.relpath(p, bundle))
            elif os.path.islink(p):
                symlinks.append(os.path.relpath(p, bundle))
        dirs[:] = sorted(d for d in dirs
                         if d not in EXCLUDED_DIRS and not os.path.islink(
                             os.path.join(root, d)))
        for fn in sorted(files):
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, bundle)
            if fn in EXCLUDED_NAMES:
                excluded.append(rel)
                continue
            if os.path.islink(p):
                symlinks.append(rel)
                continue
            try:
                m = os.lstat(p).st_mode
            except OSError:
                irregular.append(rel)
                continue
            if not stat.S_ISREG(m):
                irregular.append(rel)
                continue
            regular.append((rel, p))
    return sorted(regular), sorted(symlinks), sorted(irregular), sorted(excluded)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _body(rows):
    return "".join(f"{h}  {n}  {rel}\n" for rel, h, n in rows)


def build(bundle, manifest):
    regular, symlinks, irregular, excluded = scan(bundle)
    if symlinks:
        raise SystemExit(f"REFUSING TO BUILD: bundle contains symlink(s): {symlinks}")
    if irregular:
        raise SystemExit(f"REFUSING TO BUILD: non-regular file(s): {irregular}")
    # hard links: a file with st_nlink > 1 is aliased and its content can change via the
    # other name without any write to this path.
    aliased = [rel for rel, p in regular if os.lstat(p).st_nlink > 1]
    if aliased:
        raise SystemExit(f"REFUSING TO BUILD: hard-linked (aliased) file(s): {aliased}")
    rows = sorted((rel, sha256_file(p), os.path.getsize(p)) for rel, p in regular)
    body = _body(rows)
    root = hashlib.sha256(body.encode()).hexdigest()
    with open(manifest, "w") as f:
        f.write("# FINAL_PRE_UG25_VALIDATION_BUNDLE manifest\n")
        f.write(f"# files: {len(rows)}\n")
        f.write(f"# excluded (declared, sandbox-injected): {','.join(excluded) or 'none'}\n")
        f.write(f"# ROOT_SHA256: {root}\n")
        f.write(body)
    with open(manifest + ".sha256", "w") as f:
        f.write(sha256_file(manifest) + "\n")
    print(f"built {manifest}: {len(rows)} files, {len(excluded)} declared exclusion(s)")
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
        h, n, rel = ln.rstrip("\n").split("  ", 2)
        rows[rel] = (h, int(n))
    return rows, root, n_declared


def _valid_root(s):
    return (isinstance(s, str) and len(s) == 64
            and all(c in "0123456789abcdef" for c in s.lower())
            and set(s) != {"0"})


def verify(bundle, manifest, pinned_root):
    """Exit 0 ONLY if every assertion passes. A pinned external root is MANDATORY."""
    problems = Finding()

    # --- the externally supplied root is required, well-formed and not all-zero --------
    if not pinned_root:
        print("FREEZE VIOLATION  PINNED ROOT ABSENT - an external expected root is required; "
              "there is no unpinned verify mode")
        print("FREEZE BROKEN")
        return 1
    if not _valid_root(pinned_root):
        print(f"FREEZE VIOLATION  PINNED ROOT MALFORMED OR ALL-ZERO: {pinned_root!r}")
        print("FREEZE BROKEN")
        return 1

    if not os.path.isfile(manifest):
        print(f"FREEZE VIOLATION  MANIFEST ABSENT  {manifest}")
        print("FREEZE BROKEN: absence of provenance is a failure, not a note.")
        return 1

    side = manifest + ".sha256"
    if not os.path.isfile(side):
        problems.append(f"MANIFEST SIDECAR ABSENT  {side}")
    else:
        want_side, have_side = open(side).read().strip(), sha256_file(manifest)
        if want_side != have_side:
            problems.append(f"MANIFEST TAMPERED  sidecar {want_side[:16]} != "
                            f"actual {have_side[:16]}")

    try:
        want, want_root, n_declared = read_manifest(manifest)
    except Exception as e:
        print(f"FREEZE VIOLATION  MANIFEST MALFORMED  {e}")
        print("FREEZE BROKEN")
        return 1

    if not want_root:
        problems.append("MANIFEST HEADER MISSING ROOT_SHA256")
    if n_declared is not None and n_declared != len(want):
        problems.append(f"MANIFEST ROW COUNT  header {n_declared} != {len(want)} rows")

    regular, symlinks, irregular, excluded = scan(bundle)
    for s in symlinks:
        problems.append(f"SYMLINK PRESENT  {s}  (symlinks are never permitted)")
    for s in irregular:
        problems.append(f"NON-REGULAR FILE  {s}")
    for rel, p in regular:
        if os.lstat(p).st_nlink > 1:
            problems.append(f"HARD-LINKED FILE  {rel}  (content aliased outside this path)")

    have = {rel: (sha256_file(p), os.path.getsize(p)) for rel, p in regular}
    for r in sorted(set(have) - set(want)):
        problems.append(f"ADDED    {r}")
    for r in sorted(set(want) - set(have)):
        problems.append(f"REMOVED  {r}")
    for r in sorted(x for x in set(want) & set(have) if have[x][0] != want[x][0]):
        problems.append(f"CHANGED  {r}")

    rows = sorted((r, have[r][0], have[r][1]) for r in have)
    root = hashlib.sha256(_body(rows).encode()).hexdigest()

    if want_root and root != want_root:
        problems.append(f"MANIFEST ROOT MISMATCH  {want_root[:16]} != observed {root[:16]}")
    if root != pinned_root:
        problems.append(f"EXTERNAL PINNED ROOT MISMATCH  pinned {pinned_root[:16]} != "
                        f"observed {root[:16]}")

    print(f"declared exclusions: {','.join(excluded) or 'none'}")
    print(f"pinned   ROOT_SHA256 {pinned_root}")
    print(f"manifest ROOT_SHA256 {want_root}")
    print(f"observed ROOT_SHA256 {root}")
    for p in problems:
        print(f"FREEZE VIOLATION  {p}")
    if problems:
        print(f"FREEZE BROKEN: {len(problems)} violation(s)")
        return 1
    print("FREEZE INTACT")
    return 0


def chmod_tree(bundle, lock):
    """Filesystem permission hardening. NOT immutability - see the module docstring."""
    nf = nd = 0
    dirs = []
    for root, dnames, _ in os.walk(bundle, followlinks=False):
        dnames[:] = [d for d in dnames if d not in EXCLUDED_DIRS]
        dirs.append(root)
        dirs += [os.path.join(root, d) for d in dnames]
    for rel, p in scan(bundle)[0]:
        m = os.stat(p).st_mode
        new = (m & ~0o222) if lock else (m | stat.S_IWUSR)
        if new != m:
            os.chmod(p, new)
            nf += 1
    for d in sorted(set(dirs), key=len, reverse=not lock):
        m = os.stat(d).st_mode
        new = (m & ~0o222) if lock else (m | stat.S_IWUSR)
        if new != m:
            os.chmod(d, new)
            nd += 1
    print(("locked " if lock else "unlocked ") + f"{nf} file(s), {nd} dir(s)")


if __name__ == "__main__":
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
