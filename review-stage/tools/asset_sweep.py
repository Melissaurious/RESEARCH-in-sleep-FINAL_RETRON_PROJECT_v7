#!/usr/bin/env python3
"""Asset discovery sweep. Read-only.

Scans declared roots for scientific assets, groups them by holding directory, and emits one row
per asset collection with an identity pin. Answers the failure mode in which the declared project
was nine git worktrees while the real evidence base was much larger.

Identity pin = sha256 over the sorted "<name> <bytes>" listing of the collection. Fast, stable,
and sufficient to detect drift without hashing gigabytes.
"""
import hashlib, os, sys, csv
from collections import defaultdict

ROOTS = [
    "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7",
    "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4",
    "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3",
    "/home/borg/RESEARCH-in-sleep-RETRON-DB_V2",
    "/home/borg/RESEARCH-in-sleep-RETRON-DB",
    "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_WORK",
    "/home/borg/RETRONS_january_2026",
    "/home/borg/RESEARCH-retron-db",
    "/home/borg/RETRON_STAGES",
]
import glob
ROOTS += sorted(glob.glob("/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-*"))

KINDS = {
    "structure":  {".pdb", ".cif", ".mmcif", ".ent"},
    "tree":       {".treefile", ".contree", ".nwk", ".newick", ".nw", ".tre", ".suptree", ".ufboot"},
    "profile":    {".hmm", ".cm"},
    "matrix":     {".npy", ".npz"},
    "literature": {".pdf"},
}
EXT2KIND = {e: k for k, s in KINDS.items() for e in s}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "site-packages"}

def main():
    coll = defaultdict(lambda: defaultdict(list))   # dir -> kind -> [(name,size)]
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                ext = os.path.splitext(fn)[1].lower()
                if fn.endswith(".cf.tree"):
                    ext = ".tre"
                kind = EXT2KIND.get(ext)
                if not kind:
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    sz = os.path.getsize(p)
                except OSError:
                    continue
                coll[dirpath][kind].append((fn, sz))

    rows = []
    for d, kinds in coll.items():
        for kind, files in kinds.items():
            files.sort()
            h = hashlib.sha256("\n".join(f"{n} {s}" for n, s in files).encode()).hexdigest()
            rows.append({
                "collection_path": d,
                "kind": kind,
                "n_files": len(files),
                "total_bytes": sum(s for _, s in files),
                "manifest_sha256": h,
                "example_file": files[0][0],
                "root": next((r for r in sorted(ROOTS, key=len, reverse=True) if d.startswith(r)), ""),
            })
    rows.sort(key=lambda r: (-r["total_bytes"],))
    w = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()), delimiter="\t")
    w.writeheader()
    for r in rows:
        w.writerow(r)

if __name__ == "__main__":
    main()
