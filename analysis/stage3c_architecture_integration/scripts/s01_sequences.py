#!/usr/bin/env python3
"""s01 — modelled sequence of each of the 62 chains, in 3A's canonical residue index space.

Source: 3A's frozen per-residue secondary-structure files (residues carrying CA, author keys).
Second, independent path: the register's `modelled_seq_sha256`, computed in 3A g0 from the
deposited file. Both must agree or the chain is flagged.

Outputs
  tables/chain_sequences.tsv   chain, length, sequence, modified residues, chain breaks, hashes
  tables/chain_index_map.tsv   chain, seq_index (1-based), resnum, icode, resname
  tables/chains.faa            FASTA for the frozen mapper (id = chain)
"""
import hashlib
import os
import sys

import gemmi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

reg = L.register()
t1 = L.t1()
rows, imap, fa = [], [], []
for c in L.chains():
    res = L.ss_residues(c)
    seq, mods = [], []
    for i, r in enumerate(res, 1):
        aa, modified = L.one_letter(r["resname"])
        seq.append(aa)
        if modified:
            mods.append(f"{r['key'][0]}{r['key'][1]}:{r['resname']}->{aa}")
        imap.append(dict(chain=c, seq_index=i, resnum=r["key"][0], icode=r["key"][1], resname=r["resname"]))
    s = "".join(seq)
    n_breaks = sum(r["brk"] for r in res[1:])
    # register hash was computed on the modelled one-letter sequence; test both conventions
    reg_hash = reg[c]["modelled_seq_sha256"]
    h = hashlib.sha256(s.encode()).hexdigest()
    # second path: re-read the deposited polymer exactly as 3A g0 did and explain any difference
    reason = "-"
    if h != reg_hash:
        st = gemmi.read_structure(reg[c]["source_file"])
        st.setup_entities()
        poly = st[0][reg[c]["chain"]].get_polymer()
        dep = gemmi.one_letter_code([x.name for x in poly]).upper()
        no_ca = [f"{x.seqid.num}:{x.name}" for x in poly if not x.find_atom("CA", "*")]
        mine_x = "".join("X" if L.one_letter(r["resname"])[1] else a for r, a in zip(res, s))
        dep_ca = "".join(a for x, a in zip(poly, dep) if x.find_atom("CA", "*"))
        if hashlib.sha256(dep.encode()).hexdigest() != reg_hash:
            reason = "UNEXPLAINED: deposited polymer no longer hashes to the register value"
        elif mine_x == dep_ca:
            parts = []
            if mods:
                parts.append("register writes modified residues as X; 3C maps them to the parent")
            if no_ca:
                parts.append("polymer residues without CA are outside 3A's CA index space: " + ",".join(no_ca))
            reason = "EXPLAINED: " + "; ".join(parts)
        else:
            reason = "UNEXPLAINED: sequence differs beyond modified residues and CA-less residues"
    rows.append(dict(chain=c, biological_group=t1[c]["biological_group"], stratum=t1[c]["stratum"],
                     n_modelled=len(s), sequence=s, modified_residues=";".join(mods) or "-",
                     n_chain_breaks=n_breaks, seq_sha256=h, register_modelled_seq_sha256=reg_hash,
                     register_hash_agrees="YES" if h == reg_hash else "NO", disagreement_reason=reason,
                     rt_hash_modelled=hashlib.sha256(s.upper().rstrip("*").encode()).hexdigest(),
                     register_n_modelled=reg[c]["n_modelled_residues"],
                     n_modelled_agrees="YES" if str(len(s)) == reg[c]["n_modelled_residues"] else "NO"))
    fa.append(f">{c}\n{s}\n")

L.write_tsv(os.path.join(L.TABLES, "chain_sequences.tsv"), rows, list(rows[0]))
L.write_tsv(os.path.join(L.TABLES, "chain_index_map.tsv"), imap, list(imap[0]))
with open(os.path.join(L.TABLES, "chains.faa"), "w") as f:
    f.write("".join(fa))
na = [r["chain"] for r in rows if r["n_modelled_agrees"] != "YES"]
nh = [r["chain"] for r in rows if r["register_hash_agrees"] != "YES"]
un = [r["chain"] for r in rows if r["disagreement_reason"].startswith("UNEXPLAINED")]
print(f"chains={len(rows)} length-disagree={na} hash-disagree={len(nh)} {nh} unexplained={un}")
if un:
    sys.exit("sequence identity not established for " + ",".join(un))
