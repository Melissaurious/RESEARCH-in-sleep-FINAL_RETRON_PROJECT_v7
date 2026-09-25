#!/usr/bin/env python3
"""Cross-root content identity for Mestre-related files.

Collects every file (<= 300 MB, not under .git) whose name matches a Mestre/supplement/Toro/
benchmark pattern, or that sits in a directory whose name contains 'mestre', across the historical
roots and the current project copy. Groups by sha256 so that duplicate paths are never counted as
independent evidence. Output: one row per file with its identity group and group size.
"""
import hashlib, os, re, sys, csv, datetime
ROOTS = ["/home/borg/RESEARCH-retron-db", "/home/borg/RESEARCH-in-sleep-RETRON-DB_V2",
         "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3", "/home/borg/RESEARCH-in-sleep-RETRON-DB_V4",
         "/home/borg/RESEARCH-in-sleep-RETRON-DB_V5",
         "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/MELISSA_DATA/supplementary_material",
         "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/references",
         "/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7/results"]
NAME = re.compile(r"mestre|supp_material|supplementary_mestre|suppl_toro|toro_2014|support\.csv|"
                  r"stock_verdicts|ids_69|rescued_accessions|dead_accessions|still_manual|wp_fix|"
                  r"retron_(download|rescue|fix_wp)\.log|s2b_|s5b_|s5e_|s8b_|s7h_|s7i_|m1[0-3]_|m8_", re.I)
SKIP_DIR = re.compile(r"/\.git(/|$)|/fold/mestre(/|$)|/fm/mestre_span(/|$)|/ibex_mestre/terminal_")
MAX = 300 << 20

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

rows = []
for r in ROOTS:
    for root, dirs, files in os.walk(r):
        if SKIP_DIR.search(root):
            dirs[:] = []; continue
        dir_hit = "mestre" in root.lower()
        for f in files:
            p = os.path.join(root, f)
            if not (NAME.search(f) or dir_hit) or not os.path.isfile(p) or os.path.islink(p):
                continue
            st = os.stat(p)
            if st.st_size > MAX:
                continue
            rows.append([p, f, st.st_size, datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"), sha(p)])
groups = {}
for r in rows:
    groups.setdefault(r[4], []).append(r)
gid = {h: f"G{i:04d}" for i, h in enumerate(sorted(groups, key=lambda h: (-len(groups[h]), groups[h][0][1])), 1)}
def root_of(p):
    for r in ROOTS:
        if p.startswith(r + "/"):
            return r.replace("/home/borg/", "")
w = csv.writer(open(sys.argv[1], "w", newline=""), delimiter="\t", lineterminator="\n")
w.writerow(["identity_group", "group_size", "n_roots_in_group", "root", "path", "name", "bytes", "mtime", "sha256"])
for h in sorted(groups, key=lambda h: gid[h]):
    g = groups[h]; nroots = len({root_of(x[0]) for x in g})
    for p, f, b, m, s in sorted(g, key=lambda x: x[3]):
        w.writerow([gid[h], len(g), nroots, root_of(p), p, f, b, m, s])
print(len(rows), "files;", len(groups), "distinct contents;", sum(1 for g in groups.values() if len(g) > 1), "multi-copy groups", file=sys.stderr)
