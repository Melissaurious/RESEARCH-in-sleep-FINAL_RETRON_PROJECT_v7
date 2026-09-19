#!/usr/bin/env python3
"""Stage 3A g0 — experimental structure register. Structural metadata ONLY.

No catalytic column, no motif, no Stage-2 state, no historical boundary is read or emitted here.
The Stage-3B table is used solely as the audited POPULATION and provenance index.
"""
import gemmi, csv, os, sys, hashlib, collections
ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
S3B=ROOT+"/analysis/stage3b_design/TRUTH_TABLE.tsv"
OUT=ROOT+"/analysis/stage3a_structural_core"
T=os.environ.get("TMPDIR","/tmp")
pop=list(csv.DictReader(open(S3B),delimiter="\t"))
ALLOWED={"pdb_id","chain","replicate_group","relatedness_cluster_30pct","source_file",
         "resolution_A","family_class_METADATA_ONLY","modified_polymer_residues"}
rows=[]; cache={}
for r in sorted(pop,key=lambda x:(x["pdb_id"],x["chain"])):
    f=r["source_file"]
    if f.endswith(".pdb"):
        alt=f"{T}/g1cif/{r['pdb_id']}.cif"
        if os.path.exists(alt): f=alt
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations(); cache[f]=st
    st=cache[f]; m=st[0]
    ch=[c for c in m if c.name==r["chain"]][0]
    poly=ch.get_polymer()
    modelled=[x for x in ch if x.name in gemmi.tabulate_residues.__doc__] if False else list(poly)
    nums=[x.seqid.num for x in poly]
    seq_mod=gemmi.one_letter_code([x.name for x in poly]).upper()
    # construct sequence + external accessions
    con=""; accs=[]
    if f.endswith(".cif"):
        b=gemmi.cif.read(f).sole_block()
        for row in b.find("_entity_poly.",["entity_id","pdbx_seq_one_letter_code_can","pdbx_strand_id"]):
            if r["chain"] in [x.strip() for x in row.str(2).split(",")]: con="".join(row.str(1).split())
        refs={row.str(0):(row.str(1),row.str(2)) for row in b.find("_struct_ref.",["id","db_name","pdbx_db_accession"])}
        for row in b.find("_struct_ref_seq.",["ref_id","pdbx_strand_id","seq_align_beg","seq_align_end","db_align_beg","db_align_end"]):
            if row.str(1)==r["chain"]:
                db,acc=refs.get(row.str(0),("",""))
                accs.append((db,acc,row.str(2),row.str(3),row.str(4),row.str(5)))
    accs=sorted(set(accs))
    unp=sorted({a[1] for a in accs if a[0].upper() in ("UNP","UNIPROT")})
    # internal gaps
    gaps=[]
    for a,b2 in zip(nums,nums[1:]):
        if b2-a>1: gaps.append((a,b2,b2-a-1))
    n_missing_internal=sum(g[2] for g in gaps)
    nterm_missing = (nums[0]-1) if nums else 0
    cterm_missing = (len(con)-nums[-1]) if con and nums and nums[-1]<=len(con) else ""
    # fused / accessory domain signal: >1 distinct UniProt accession mapped to this chain
    fused = "YES" if len(unp)>1 else ("SUSPECTED" if (con and len(con)>1.6*len(poly)) else "no")
    fused_detail = "; ".join(f"{a[0]}:{a[1]} entity {a[2]}-{a[3]} -> db {a[4]}-{a[5]}" for a in accs) if len(accs)>1 else ""
    rows.append(dict(
        pdb_id=r["pdb_id"], chain=r["chain"],
        biological_group=r["replicate_group"], relatedness_cluster_30pct=r["relatedness_cluster_30pct"],
        lineage_METADATA_ONLY=("viral" if "retroviral" in r["family_class_METADATA_ONLY"] else
                               "non-LTR" if "non-LTR" in r["family_class_METADATA_ONLY"] else "bacterial"),
        family_METADATA_ONLY=r["family_class_METADATA_ONLY"],
        method=dict(st.info).get("_exptl.method",""), resolution_A=r["resolution_A"],
        source_file=f, file_sha256=hashlib.sha256(open(f,'rb').read()).hexdigest(),
        n_modelled_residues=len(poly), modelled_range=f"{nums[0]}-{nums[-1]}" if nums else "",
        construct_len=len(con), construct_sha256=hashlib.sha256(con.encode()).hexdigest() if con else "",
        modelled_seq_sha256=hashlib.sha256(seq_mod.encode()).hexdigest(),
        external_accessions=";".join(unp) or "NONE",
        n_internal_gaps=len(gaps), n_missing_internal=n_missing_internal,
        gap_spans=";".join(f"{a+1}-{b2-1}" for a,b2,_ in gaps),
        n_missing_nterm=nterm_missing, n_missing_cterm=cterm_missing,
        fused_or_accessory=fused, fused_detail=fused_detail,
        modified_polymer_residues=r["modified_polymer_residues"]))
hdr=list(rows[0].keys())
with open(OUT+"/STRUCTURE_REGISTER.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=hdr,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(rows)
# biological groups
g=collections.defaultdict(list)
for r in rows: g[r["biological_group"]].append(r)
brows=[]
for bg,ms in sorted(g.items()):
    brows.append(dict(biological_group=bg,
        n_pdb_entries=len({m["pdb_id"] for m in ms}), n_chains=len(ms),
        pdb_entries=",".join(sorted({m["pdb_id"] for m in ms})),
        relatedness_cluster_30pct=ms[0]["relatedness_cluster_30pct"],
        lineage_METADATA_ONLY=ms[0]["lineage_METADATA_ONLY"],
        family_METADATA_ONLY=";".join(sorted({m["family_METADATA_ONLY"] for m in ms})),
        best_resolution_A=min(float(m["resolution_A"]) for m in ms),
        median_modelled_len=sorted(m["n_modelled_residues"] for m in ms)[len(ms)//2],
        n_states=len({m["pdb_id"] for m in ms}),
        any_fused=("YES" if any(m["fused_or_accessory"]=="YES" for m in ms) else "no"),
        external_accessions=";".join(sorted({a for m in ms for a in m["external_accessions"].split(";") if a!="NONE"})) or "NONE"))
with open(OUT+"/BIOLOGICAL_GROUPS.tsv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=list(brows[0].keys()),delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(brows)
print(f"chains: {len(rows)}   biological groups: {len(brows)}")
print("lineage:",dict(collections.Counter(r["lineage_METADATA_ONLY"] for r in rows)))
print("fused/accessory:",dict(collections.Counter(r["fused_or_accessory"] for r in rows)))
print("groups with >1 deposition (state replicates):",sum(1 for b in brows if b["n_states"]>1))
print("chains with internal gaps:",sum(1 for r in rows if r["n_internal_gaps"]>0),
      " total missing internal residues:",sum(r["n_missing_internal"] for r in rows))
