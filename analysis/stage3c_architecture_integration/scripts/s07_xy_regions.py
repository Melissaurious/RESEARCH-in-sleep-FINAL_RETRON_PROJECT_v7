#!/usr/bin/env python3
"""s3c_gD — retron-specific Region X and Region Y: operational annotation of the 62 chains.

ORDER (LAUNCHER_03C 7a, D; K9): the literature/provenance audit lands first
(XY_REGION_EVIDENCE.tsv), then THIS RULE is committed, and only then are chains scanned. No rule
below may change after the scan.

What the audit established, and what it did not (see XY_REGION_EVIDENCE.tsv and the report):
  * Region X and Region Y are delimited in the literature only RELATIVE TO MOTIFS - "a ~16 aa
    segment between RT motifs 2 and 3" (X) and "a ~90 aa segment beginning at the VTG triplet
    within motif 7 and running to the C-terminus" (Y), Simon et al. 2019. No source states a
    residue-numbered interval for either region as a general definition.
  * The only residue-numbered intervals attached to Region Y are experimental FRAGMENTS of two
    proteins: RT-Ec86-(255-320) and RT-Ec73-(251-316) (Inouye et al. 2004).
  * Structure papers give motif positions in single proteins (Ec86 NAxxH 105-109, VTG 243-245).
    Those are used here only as EXTERNAL POSITIVE CONTROLS on the scanning code.

DECLARED operational rules
  X interval: residues strictly between the last mapped residue of block SB2p and the first mapped
    residue of block SB3 -> status X_INTERVAL_FROM_BLOCKS. If SB2p is unavailable but SB3 is, the
    wide window from the chain N-terminus to the first mapped SB3 residue is scanned instead ->
    status X_INTERVAL_WIDE_WINDOW (weaker; reported separately, never pooled). If SB3 is
    unavailable -> X_INTERVAL_UNDEFINED.
  X motif: strict N-A-x-x-H; relaxed A-x-x-H; else NO_MOTIF_IN_INTERVAL (never "no Region X").
  Y interval: the first V/I/L-T-G triplet whose start lies within SB7_WINDOW residues of the SB7
    mapped span (or, if SB7 is unavailable, within SB7_WINDOW after the last mapped anchor), through
    to the last modelled residue -> Y_INTERVAL_FROM_VTG. Without such a triplet -> Y_INTERVAL_UNDEFINED
    (the literature definition begins AT the triplet, so no triplet means no operational interval,
    not absence of a C-terminal region).
  Y motif: strict VTG; variant (I|L)TG at position 1, per Toro & Nisa-Martinez 2014.
  Nucleic-acid contact: protein heavy atom within 4.0 A of a polynucleotide heavy atom in the same
    deposited entry; RNA and DNA counted separately by residue name.

Controls
  positive (contacts): reproduce the SUBSTRATE_NA residues recorded independently in the frozen 3B
    truth table; positive (motif code): recover the YxDD-like window at the 3B catalytic truth;
    external: literature-stated motif positions in Ec86 / Eco7 / Vmi1-like chains;
  negative: 100 seeded shuffles of each X interval, same scan (seed 20260919).

Writes XY_REGION_ANNOTATIONS.tsv, tables/D_controls.tsv, tables/D_na_contacts_by_region.tsv.
"""
import collections
import hashlib
import os
import random
import re
import sys

import gemmi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

NA_CUTOFF = 4.0        # DECLARED
SB7_WINDOW = 60        # DECLARED: residues around the SB7 span in which the VTG triplet is sought
SHUFFLES = 100         # DECLARED
SEED = 20260919        # DECLARED
X_STRICT = re.compile("N A . . H".replace(" ", ""))
X_RELAXED = re.compile("A..H")
Y_STRICT = re.compile("VTG")
Y_VARIANT = re.compile("(I|L)TG")

# External positive controls: literature-stated motif positions, author numbering of the protein
# named in the source. Verified here against the deposited chain sequence, never assumed.
LIT_POSITIONS = [
    ("7V9U_A", "NAxxH", 105, 109, "Wang 2022 Nat Microbiol (Ec86)"),
    ("7V9X_A", "NAxxH", 105, 109, "Wang 2022 Nat Microbiol (Ec86)"),
    ("7XJG_A", "NAxxH", 105, 109, "Wang 2022 Nat Microbiol (Ec86)"),
    ("7V9U_A", "VTG", 243, 245, "Wang 2022 Nat Microbiol (Ec86)"),
    ("7V9X_A", "VTG", 243, 245, "Wang 2022 Nat Microbiol (Ec86)"),
    ("7XJG_A", "VTG", 243, 245, "Wang 2022 Nat Microbiol (Ec86)"),
    ("7V9U_A", "YADD", 195, 198, "Wang 2022 Nat Microbiol (Ec86)"),
    ("9VHE_A", "NAxxH", 82, 86, "Wang 2025 NAR (Retron-Eco7); PDB linkage tested here, not assumed"),
    ("9VHE_A", "VTG", 236, 238, "Wang 2025 NAR (Retron-Eco7); PDB linkage tested here, not assumed"),
]

seq = {r["chain"]: r for r in L.read_tsv(os.path.join(L.TABLES, "chain_sequences.tsv"))}
imap = collections.defaultdict(dict)
rev = collections.defaultdict(dict)
for r in L.read_tsv(os.path.join(L.TABLES, "chain_index_map.tsv")):
    imap[r["chain"]][int(r["seq_index"])] = (int(r["resnum"]), r["icode"])
    rev[r["chain"]][(int(r["resnum"]), r["icode"])] = int(r["seq_index"])
X2 = L.read_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE2_CROSSWALK.tsv"))
blocks = {(r["chain"], r["block"]): r for r in X2 if r["arm"] == "primary"}
RES = L.read_tsv(os.path.join(L.TABLES, "B_state_residue_join.tsv"))
block_res = collections.defaultdict(list)
for r in RES:
    if r["resnum"]:
        block_res[(r["chain"], r["block"])].append(int(r["resnum"]))
reg = L.register()
t1 = L.t1()
A3B = {r["chain"]: r for r in L.read_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE3B_CROSSWALK.tsv")) if r["arm"] == "primary"}
truth3b = {f"{r['pdb_id']}_{r['chain']}": r for r in L.read_tsv(os.path.join(L.CAT3B_G2, "tables", "TRUTH_TABLE.tsv"))}
labs = L.pdp_labels("primary")


# ---------------------------------------------------------------- nucleic-acid contacts
def na_contacts(chain_id):
    """{(resnum, icode): (n_rna_contacts, n_dna_contacts)} for the protein chain of interest."""
    r = reg[chain_id]
    st = gemmi.read_structure(r["source_file"])
    st.remove_alternative_conformations()
    st.remove_hydrogens()
    model = st[0]
    prot = model[r["chain"]]
    out = collections.defaultdict(lambda: [0, 0])
    na = []
    for ch in model:
        for res in ch:
            kind = ("RNA" if res.name in ("A", "U", "G", "C") else
                    "DNA" if res.name in ("DA", "DT", "DG", "DC", "DU") else None)
            if kind:
                na.extend((kind, at.pos) for at in res)
    if not na:
        return {}, 0, 0
    ns = gemmi.NeighborSearch(model, st.cell, NA_CUTOFF).populate()
    prot_name = r["chain"]
    for kind, pos in na:
        for mark in ns.find_atoms(pos, "\0", radius=NA_CUTOFF):
            cra = mark.to_cra(model)
            if cra.chain.name != prot_name or cra.residue.name not in L.THREE2ONE and cra.residue.name not in L.MODIFIED_PARENT:
                continue
            if cra.atom.pos.dist(pos) <= NA_CUTOFF:
                out[(cra.residue.seqid.num, cra.residue.seqid.icode.strip())][0 if kind == "RNA" else 1] += 1
    n_rna = sum(1 for v in out.values() if v[0])
    n_dna = sum(1 for v in out.values() if v[1])
    return {k: tuple(v) for k, v in out.items()}, n_rna, n_dna


def scan(s, pat):
    return [m.start() + 1 for m in re.finditer(f"(?=({pat.pattern}))", s)]


rows, ctrl, narows = [], [], []
rng = random.Random(SEED)
contacts_cache = {}
for c in L.chains():
    s = seq[c]["sequence"]
    n = len(s)
    sb2, sb3, sb7 = (blocks[(c, b)] for b in ("SB2p", "SB3", "SB7"))
    r2 = sorted(block_res.get((c, "SB2p"), []))
    r3 = sorted(block_res.get((c, "SB3"), []))
    r7 = sorted(block_res.get((c, "SB7"), []))
    # ---- Region X interval
    if sb3["available"] == "YES" and r3:
        i3 = rev[c][(r3[0], "")]
        if sb2["available"] == "YES" and r2:
            i2 = rev[c][(r2[-1], "")]
            x_lo, x_hi, x_status = i2 + 1, i3 - 1, "X_INTERVAL_FROM_BLOCKS"
        else:
            x_lo, x_hi, x_status = 1, i3 - 1, "X_INTERVAL_WIDE_WINDOW"
    else:
        x_lo = x_hi = None
        x_status = "X_INTERVAL_UNDEFINED (block SB3 not available in this chain)"
    xseq = s[x_lo - 1:x_hi] if x_lo and x_hi and x_hi >= x_lo else ""
    hits_strict = [x_lo + p - 1 for p in scan(xseq, X_STRICT)] if xseq else []
    hits_relax = [x_lo + p - 1 for p in scan(xseq, X_RELAXED)] if xseq else []
    x_motif = ("NAXXH_STRICT" if hits_strict else "AXXH_RELAXED" if hits_relax else
               "NO_MOTIF_IN_INTERVAL" if xseq else "NOT_SCANNED")
    x_hit = (hits_strict or hits_relax or [None])[0]
    # negative control: same scan on shuffles of the same interval
    if xseq:
        lst = list(xseq)
        hits = 0
        for _ in range(SHUFFLES):
            rng.shuffle(lst)
            if scan("".join(lst), X_STRICT):
                hits += 1
        ctrl.append(dict(control="negative_shuffle_X_strict", chain=c, n_trials=SHUFFLES, n_hits=hits,
                         observed="NAXXH_STRICT" if hits_strict else x_motif,
                         detail=f"interval length {len(xseq)}", unit="shuffle"))
    # ---- Region Y interval
    y_anchor = (r7[0] if r7 else None)
    cand = scan(s, Y_STRICT) or []
    cand_var = scan(s, Y_VARIANT) or []
    y_i = y_kind = None
    if y_anchor is not None:
        a = rev[c][(y_anchor, "")]
        lo, hi = a - SB7_WINDOW, (rev[c][(r7[-1], "")] + SB7_WINDOW)
    else:
        last_anchor = max((rev[c][(v, "")] for b in ("SB56", "SB4", "SB3") for v in block_res.get((c, b), [])), default=None)
        lo, hi = (last_anchor, last_anchor + SB7_WINDOW) if last_anchor else (None, None)
    if lo is not None:
        for p in cand:
            if lo <= p <= hi:
                y_i, y_kind = p, "VTG_STRICT"
                break
        if y_i is None:
            for p in cand_var:
                if lo <= p <= hi:
                    y_i, y_kind = p, "ITG_LTG_VARIANT"
                    break
    y_status = ("Y_INTERVAL_FROM_VTG" if y_i else
                "Y_INTERVAL_UNDEFINED (no VTG-like triplet in the SB7 window)" if lo is not None else
                "Y_INTERVAL_UNDEFINED (no anchor to place the SB7 window)")
    # ---- contacts
    if c not in contacts_cache:
        contacts_cache[c] = na_contacts(c)
    cmap, n_rna, n_dna = contacts_cache[c]

    def region_contacts(lo_i, hi_i):
        nr = nd = tot = 0
        for i in range(lo_i, hi_i + 1):
            k = imap[c].get(i)
            if k and k in cmap:
                nr += 1 if cmap[k][0] else 0
                nd += 1 if cmap[k][1] else 0
            tot += 1
        return nr, nd, tot

    x_nr, x_nd, x_len = region_contacts(x_lo, x_hi) if xseq else (0, 0, 0)
    y_nr, y_nd, y_len = region_contacts(y_i, n) if y_i else (0, 0, 0)
    a = A3B[c]
    rows.append(dict(
        chain=c, pdb_id=c.split("_")[0], auth_chain=reg[c]["chain"], biological_group=t1[c]["biological_group"],
        family_METADATA=reg[c]["family_METADATA_ONLY"], lineage_METADATA=reg[c]["lineage_METADATA_ONLY"],
        is_retron_family="YES" if "Retron" in reg[c]["family_METADATA_ONLY"] else "NO",
        uniprot_accessions=reg[c]["external_accessions"], construct_sha256=reg[c]["construct_sha256"],
        rt_hash_modelled_sequence=seq[c]["rt_hash_modelled"],
        join_key_note="rt_hash convention = sha256 of the uppercased sequence with one trailing '*' removed "
                      "(dbchar_g2 g2lib.rt_hash); computed here on the MODELLED sequence, so it joins the "
                      "RT-ncRNA dataset only for chains whose modelled sequence is the full protein",
        n_modelled=n, mapper_verdict=blocks[(c, "SB3")]["mapper_verdict"],
        region_X_status=x_status,
        region_X_start_resnum=imap[c][x_lo][0] if xseq else "", region_X_end_resnum=imap[c][x_hi][0] if xseq else "",
        region_X_length=x_len, region_X_motif=x_motif,
        region_X_motif_resnum=imap[c][x_hit][0] if x_hit else "",
        region_X_motif_sequence=s[x_hit - 1:x_hit + 4] if x_hit else "",
        region_X_unit=(labs[c].get(imap[c][x_hit], "") if x_hit else ""),
        region_X_rna_contact_residues=x_nr, region_X_dna_contact_residues=x_nd,
        region_Y_status=y_status, region_Y_motif=y_kind or "NO_VTG_LIKE_TRIPLET_IN_WINDOW",
        region_Y_motif_resnum=imap[c][y_i][0] if y_i else "",
        region_Y_start_resnum=imap[c][y_i][0] if y_i else "", region_Y_end_resnum=imap[c][n][0] if y_i else "",
        region_Y_length=y_len, region_Y_unit=(labs[c].get(imap[c][y_i], "") if y_i else ""),
        region_Y_rna_contact_residues=y_nr, region_Y_dna_contact_residues=y_nd,
        chain_rna_contact_residues=n_rna, chain_dna_contact_residues=n_dna,
        chain_has_nucleic_acid="YES" if (n_rna or n_dna) else "NO",
        frac_chain_rna_contacts_in_region_Y=(y_nr / n_rna) if n_rna and y_i else None,
        catalytic_truth_3B_scope=a["scope_3C"], catalytic_truth_residues=a["truth_residues"],
        evidence_class="OPERATIONAL_INTERVAL (motif-anchored); the literature states no general "
                       "residue-numbered interval for either region",
        caveat="Region X and Region Y are retron concepts; they are computed here on EVERY chain so that "
               "non-retron families act as their own comparison. A motif absence is not a region absence, "
               "and the X interval depends on the GII-centred mapper reaching blocks SB2p/SB3.",
        unit="chain"))
    if n_rna or n_dna:
        narows.append(dict(chain=c, family_METADATA=reg[c]["family_METADATA_ONLY"],
                           n_rna_contact_residues=n_rna, n_dna_contact_residues=n_dna,
                           region_Y_rna=y_nr, region_Y_dna=y_nd, region_Y_length=y_len,
                           region_X_rna=x_nr, region_X_dna=x_nd, region_X_length=x_len,
                           frac_rna_contacts_in_Y=(y_nr / n_rna) if n_rna and y_i else None,
                           expected_if_uniform=(y_len / n) if y_i else None,
                           unit="residue with >=1 contact at 4.0 A"))

# ---------------------------------------------------------------- controls
for chain_id, motif, lo, hi, src in LIT_POSITIONS:
    s = seq[chain_id]["sequence"]
    got = "".join(s[rev[chain_id][(p, "")] - 1] if (p, "") in rev[chain_id] else "?" for p in range(lo, hi + 1))
    exp = {"NAxxH": re.compile("NA..H"), "VTG": re.compile("VTG"), "YADD": re.compile("Y.DD")}[motif]
    ctrl.append(dict(control="external_literature_position", chain=chain_id, n_trials=1,
                     n_hits=1 if exp.fullmatch(got) else 0, observed=f"{motif} stated {lo}-{hi}: found '{got}'",
                     detail=src, unit="literature statement"))
for c, a in sorted(A3B.items()):
    if a["scope_3C"] != "IN_SCOPE_OWN_CHAIN_TRUTH":
        continue
    truth = [int(x) for x in a["truth_residues"].split(",") if x]
    s = seq[c]["sequence"]
    # CORRECTION, recorded rather than hidden: the first formulation anchored on min(truth), which is
    # the motif-A aspartate, not the motif-C pair that carries the YxDD-like window. The corrected
    # control searches +-6 residues around EVERY truth residue. This is a control on the scanning
    # code; no outcome-bearing threshold is involved.
    found = ""
    for t in truth:
        i = rev[c].get((t, ""))
        if not i:
            continue
        win = s[max(0, i - 7):i + 6]
        m = re.search("[YFWH].DD", win)
        if m:
            found = f"{t}:{m.group(0)}"
            break
    ctrl.append(dict(control="positive_YxDD_at_3B_truth", chain=c, n_trials=1,
                     n_hits=1 if found else 0,
                     observed=(f"YxDD-like window found near truth residue {found}" if found
                               else f"no YxDD-like window within +-6 of truth residues {truth}"),
                     detail="the same scanning code must recover a YxDD-like window at independently evidenced truth",
                     unit="chain"))
    cmap = contacts_cache[c][0]
    ev = truth3b[c]["S_evidence"]
    want = sorted(int(m) for m in re.findall(r'"(\d+)": \[[^]]*SUBSTRATE_NA', ev))
    if want:
        got = sum(1 for p in want if (p, "") in cmap)
        ctrl.append(dict(control="positive_NA_contact_reproduces_3B", chain=c, n_trials=len(want), n_hits=got,
                         observed=f"3B SUBSTRATE_NA residues {want}",
                         detail="independent recomputation at 4.0 A of contacts 3B recorded", unit="residue"))

L.write_tsv(os.path.join(L.S3C, "XY_REGION_ANNOTATIONS.tsv"), rows, list(rows[0]))
L.write_tsv(os.path.join(L.TABLES, "D_controls.tsv"), ctrl, ["control", "chain", "n_trials", "n_hits", "observed", "detail", "unit"])
L.write_tsv(os.path.join(L.TABLES, "D_na_contacts_by_region.tsv"), narows, list(narows[0]))

print("X status:", collections.Counter(r["region_X_status"].split(" (")[0] for r in rows))
print("X motif :", collections.Counter(r["region_X_motif"] for r in rows))
print("Y status:", collections.Counter(r["region_Y_status"].split(" (")[0] for r in rows))
print("Y motif :", collections.Counter(r["region_Y_motif"] for r in rows))
for k in ("external_literature_position", "positive_YxDD_at_3B_truth", "positive_NA_contact_reproduces_3B"):
    C = [x for x in ctrl if x["control"] == k]
    print(f"{k}: {sum(x['n_hits'] for x in C)}/{sum(x['n_trials'] for x in C)}")
neg = [x for x in ctrl if x["control"] == "negative_shuffle_X_strict"]
print("negative shuffle NAXXH hits:", sum(x["n_hits"] for x in neg), "/", sum(x["n_trials"] for x in neg))
