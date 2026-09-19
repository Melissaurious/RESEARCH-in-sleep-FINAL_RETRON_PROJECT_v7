#!/usr/bin/env python3
"""g2r amendment 1 (F5) — structural independence screen of the CATH benchmark candidates.

Every candidate chain is searched against the 62 Stage-3A RT chain extracts with the pinned foldseek
(10.941cd33; default 3Di+AA alignment, exhaustive, e-value cutoff 10 so weak hits are still seen).
A candidate is EXCLUDED if any RT hit has e-value <= 1e-3 OR max(qtmscore, ttmscore) >= 0.50.
Then, per stratum, candidates are taken in rank order and the first QUOTA survivors form the benchmark.
A stratum with fewer survivors than its quota keeps all survivors; the shortfall is reported.
No PDP output is read here.

Usage: cath_screen.py <candidates.tsv> <cand_chain_dir> <rt_chain_dir> <hits_out.tsv> <final_out.tsv>
"""
import sys, os, csv, subprocess, tempfile, shutil, collections

FOLDSEEK = "/home/borg/miniconda3/envs/esmologs/bin/foldseek"
cand, cdir, rdir, hits_out, final_out = sys.argv[1:6]
rows = list(csv.DictReader(open(cand), delimiter="\t"))
with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
    q = os.path.join(tmp, "q"); os.makedirs(q)
    for r in rows:
        shutil.copy(os.path.join(cdir, r["chain"] + ".pdb"), q)
    out = os.path.join(tmp, "hits.tsv")
    subprocess.run([FOLDSEEK, "easy-search", q, rdir, out, os.path.join(tmp, "t"), "--exhaustive-search", "1",
                    "-e", "10", "--format-output", "query,target,evalue,prob,qtmscore,ttmscore,alntmscore,alnlen",
                    "-v", "1"], check=True, capture_output=True, text=True)
    hits = [l.rstrip("\n").split("\t") for l in open(out)]
with open(hits_out, "w") as fh:
    fh.write("query\ttarget\tevalue\tprob\tqtmscore\tttmscore\talntmscore\talnlen\n")
    for h in hits:
        fh.write("\t".join(h) + "\n")
bad = collections.defaultdict(list)
for h in hits:
    qn = h[0].replace(".pdb", "")
    ev, qt, tt = float(h[2]), float(h[4]), float(h[5])
    if ev <= 1e-3 or max(qt, tt) >= 0.50:
        bad[qn].append(f"{h[1].replace('.pdb', '')}:e={ev:.1e},qTM={qt:.2f},tTM={tt:.2f}")
final = []
for k in sorted({int(r["n_domains"]) for r in rows}):
    pool = sorted([r for r in rows if int(r["n_domains"]) == k], key=lambda r: int(r["rank"]))
    quota = int(pool[0]["quota"])
    keep = [r for r in pool if r["chain"] not in bad][:quota]
    print(f"{k}-domain: candidates {len(pool)}  excluded {sum(r['chain'] in bad for r in pool)}  "
          f"kept {len(keep)} / quota {quota}" + ("  SHORTFALL" if len(keep) < quota else ""))
    final += keep
with open(final_out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) + ["screen"], delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in final:
        w.writerow(dict(r, screen="PASS"))
print("benchmark chains:", len(final), " discontinuous:", sum(int(r["discontinuous"]) for r in final))
print("excluded among first-quota v1 set:",
      sorted(c for c in bad if any(r["chain"] == c and int(r["rank"]) < int(r["quota"]) for r in rows)))
