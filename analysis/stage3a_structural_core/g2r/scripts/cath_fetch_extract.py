#!/usr/bin/env python3
"""Fetch benchmark mmCIF from RCSB (hashed, logged) and write single-chain extracts the same way the
RT chains were extracted in g2 (first model, author chain, ligands and waters removed).

Usage: cath_fetch_extract.py <selection.tsv> <cif_dir> <chain_dir> <fetch_log.tsv>
"""
import sys, csv, os, gzip, hashlib, urllib.request, gemmi

sel, cifd, chd, log = sys.argv[1:5]
os.makedirs(cifd, exist_ok=True); os.makedirs(chd, exist_ok=True)
rows = []
for r in csv.DictReader(open(sel), delimiter="\t"):
    pid, ch = r["pdb_id"], r["chain_id"]
    cif = f"{cifd}/{pid}.cif"
    status = "cached"
    if not os.path.exists(cif):
        try:
            with urllib.request.urlopen(f"https://files.rcsb.org/download/{pid}.cif.gz", timeout=60) as fh:
                open(cif, "wb").write(gzip.decompress(fh.read()))
            status = "200"
        except Exception as e:
            rows.append(dict(chain=r["chain"], pdb_id=pid, status=f"FETCH_FAIL {e}", cif_sha256="", extract="", n_ca=0))
            continue
    out = f"{chd}/{r['chain']}.pdb"
    n_ca = 0
    try:
        st = gemmi.read_structure(cif); st.setup_entities(); st.remove_alternative_conformations()
        sub = gemmi.Selection(f"/1/{ch}").copy_structure_selection(st)
        sub.remove_ligands_and_waters(); sub.setup_entities()
        n_ca = sum(1 for c in sub[0] for res in c if res.find_atom("CA", "*"))
        if n_ca == 0:
            raise ValueError("no CA atoms for chain")
        sub.write_pdb(out)
        ex = out
    except Exception as e:
        ex = f"EXTRACT_FAIL {e}"
    rows.append(dict(chain=r["chain"], pdb_id=pid, status=status,
                     cif_sha256=hashlib.sha256(open(cif, "rb").read()).hexdigest(),
                     extract=ex, n_ca=n_ca))
with open(log, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n")
    w.writeheader(); w.writerows(rows)
ok = sum(1 for r in rows if not str(r["extract"]).startswith(("EXTRACT_FAIL", "")) or r["n_ca"] > 0)
print("rows:", len(rows), " extracted:", sum(1 for r in rows if r["n_ca"] > 0),
      " failures:", [(r["chain"], r["status"], str(r["extract"])[:60]) for r in rows if r["n_ca"] == 0])
