#!/usr/bin/env python3
"""Apply truth schema v2.0 to every registered RT chain. Deterministic, no RNG."""
import gemmi, csv, os, sys, itertools, json, hashlib
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from truth_schema import *
from attribution import ATTRIBUTION
T=os.environ["TMPDIR"]; ROOT="/home/borg/RESEARCH-in-sleep-FINAL_RETRON_PROJECT_v7-asset-audit"
reg=list(csv.DictReader(open(ROOT+"/analysis/stage3b_design/STRUCTURE_REGISTER.tsv"),delimiter="\t"))
def source(r):
    return f"{T}/g1cif/{r['pdb_id']}.cif" if r["file"].endswith(".pdb") else r["file"]
cache={}
out=[]
for r in sorted(reg, key=lambda x:(x["pdb_id"],x["chain"])):
    f=source(r); chn=r["chain"]
    if f not in cache:
        st=gemmi.read_structure(f); st.setup_entities(); st.remove_alternative_conformations()
        cache[f]=st
    st=cache[f]; m=st[0]
    lig=defaultdict(list)
    for c in m:
        poly=c.get_polymer(); k=str(poly.check_polymer_type()) if len(poly) else ""
        isna = "Dna" in k or "Rna" in k
        for res in c:
            nm=res.name
            if nm in BUFFER_CRYO: continue
            if nm in MODIFIED_POLYMER: continue              # RULE 2: polymer, not ligand
            if res.het_flag=="H" and nm in CATALYTIC_METAL: lig["METAL_CAT"]+= [(c.name,nm,res.seqid.num,a) for a in res]
            elif res.het_flag=="H" and nm in OTHER_METAL:   lig["METAL_OTHER"]+=[(c.name,nm,res.seqid.num,a) for a in res]
            elif res.het_flag=="H" and nm in SUBSTRATE_NT:  lig["SUBSTRATE_NT"]+=[(c.name,nm,res.seqid.num,a) for a in res]
            elif res.het_flag=="H" and nm in REACTION_PRODUCT: lig["REACTION_PRODUCT"]+=[(c.name,nm,res.seqid.num,a) for a in res]
            elif res.het_flag=="H" and nm in EFFECTOR_LIGAND: lig["EFFECTOR_LIGAND"]+=[(c.name,nm,res.seqid.num,a) for a in res]
            elif res.het_flag=="H" and nm in NUC_MONOPHOS:  lig["NUC_MONOPHOS"]+=[(c.name,nm,res.seqid.num,a) for a in res]
            elif isna:                                       lig["SUBSTRATE_NA"]+=[(c.name,nm,res.seqid.num,a) for a in res]
    cc=[c for c in m if c.name==chn]
    if not cc: print("MISSING",r["pdb_id"],chn,file=sys.stderr); continue
    ch=cc[0]; poly=ch.get_polymer()
    # RULE 2: re-attach modified polymer residues to the chain, dual identity preserved
    modres=[(res.seqid.num,res.name,MODIFIED_POLYMER[res.name]) for res in ch if res.name in MODIFIED_POLYMER]
    asps={}
    for res in ch:
        if res.name!="ASP": continue
        ps=[a.pos for a in res if a.name in ("OD1","OD2")]
        if ps: asps[res.seqid.num]=ps
    def mind(ps, atoms): return min([p.dist(a.pos) for _,_,_,a in atoms for p in ps] or [1e9])
    ev={}; ctx={}
    for n,ps in asps.items():
        e=[]
        d=mind(ps,lig["METAL_CAT"]);      m1=d
        if d<=D_METAL: e.append(f"METAL_CAT@{d:.2f}")
        d=mind(ps,lig["SUBSTRATE_NT"])
        if d<=D_NT: e.append(f"SUBSTRATE_NT@{d:.2f}")
        d=mind(ps,lig["SUBSTRATE_NA"])
        if d<=D_NA: e.append(f"SUBSTRATE_NA@{d:.2f}")
        d=mind(ps,lig["METAL_OTHER"])
        if d<=D_METAL: e.append(f"METAL_OTHER@{d:.2f}")
        d=mind(ps,lig["REACTION_PRODUCT"])            # RULE 1: context only
        if d<=D_PROD: ctx[n]=f"REACTION_PRODUCT@{d:.2f}"
        if e: ev[n]=e
    # deposition author sites (structural channel)
    site=set()
    if f.endswith(".cif"):
        b=gemmi.cif.read(f).sole_block()
        for row in b.find("_struct_site_gen.",["site_id","auth_asym_id","auth_comp_id","auth_seq_id"]):
            if row.str(1)==chn and row.str(2)=="ASP":
                try: site.add(int(row.str(3)))
                except ValueError: pass
    for n in site:
        if n in asps: ev.setdefault(n,[]).append("AUTHOR_SITE")
    strong=sorted(n for n,e in ev.items() if any(x.startswith(("METAL_CAT","SUBSTRATE_NT")) for x in e))
    par={n:n for n in strong}
    def fnd(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for i,j in itertools.combinations(sorted(strong),2):
        if min(p.dist(q) for p in asps[i] for q in asps[j])<=SITE_MAX:
            a,b2=fnd(i),fnd(j)
            if a!=b2: par[a]=b2
    comp=defaultdict(list)
    for n in strong: comp[fnd(n)].append(n)
    cs=[sorted(v) for v in comp.values()]
    # ---- FROZEN multisite-attribution rule (schema v2.1) ----
    att = ATTRIBUTION.get((r["pdb_id"], chn))
    nonpoly = {}
    attribution_basis = ""
    if att and att["resolved"]:
        keep = set(att["polymerase"]); nonpoly = att["non_polymerase"]
        attribution_basis = att["basis"]
        cs = [c for c in cs if set(c) & keep] if keep else []
        strong = sorted(n for n in strong if n in keep)
    if len(cs) > 1 and not (att and att["resolved"]): cls="HARD_MULTISITE_UNRESOLVED"
    elif cs and max(len(c) for c in cs)>=2: cls="HARD_PAIR"
    elif cs: cls="HARD_SINGLE"
    elif len([n for n in ev if "AUTHOR_SITE" in ev[n]])>=2: cls="AUTHOR_PAIR"
    elif ev: cls="WEAK"
    else: cls="NONE"
    pairs=sorted((round(min(p.dist(q) for p in asps[i] for q in asps[j]),2),i,j)
                 for i,j in itertools.combinations(sorted(asps),2)
                 if abs(i-j)>=5 and min(p.dist(q) for p in asps[i] for q in asps[j])<=8.0)
    state=[]
    if lig["METAL_CAT"]: state.append("catalytic_metal")
    if lig["SUBSTRATE_NT"]: state.append("nucleotide")
    if lig["REACTION_PRODUCT"] and ctx: state.append("POST_CHEMISTRY")
    if lig["SUBSTRATE_NA"]: state.append("nucleic_acid")
    out.append(dict(pdb_id=r["pdb_id"], chain=chn, replicate_group=r["replicate_group"],
        relatedness_cluster_30pct=r["relatedness_cluster_30pct"],
        family_class_METADATA_ONLY=r["family_class_METADATA_ONLY"],
        source_file=f, resolution_A=r["resolution_A"],
        n_res_polymer=len(poly), n_modified_polymer_residues=len(modres),
        modified_polymer_residues=";".join(f"{n}:{c}->{a}" for n,c,a in modres),
        protein_primer_annotation=("PROTEIN_PRIMER" if r["pdb_id"] in ("9Z6Y","9Z6Z") and any(c=="PTR" for _,c,_ in modres) else ""),
        n_asp=len(asps),
        S_evidence=json.dumps({str(k):v for k,v in sorted(ev.items())}),
        S_context_reaction_product=json.dumps({str(k):v for k,v in sorted(ctx.items())}),
        S_catalytic_asp=",".join(map(str,strong)), S_clusters=str(cs),
        S_class=cls, non_polymerase_catalytic_sites=str(nonpoly), attribution_basis=attribution_basis,
        catalytic_state_context="+".join(state) or "apo",
        L_author_assigned=r["literature_supported_catalytic_residues"],
        F_mutational=("YES" if "MUTATIONAL" in (r["literature_evidence_type"] or "") and
                      r["literature_check_status"].startswith("VERIFIED") else "NO"),
        literature_check_status=r["literature_check_status"],
        n_asp_pairs_le8A=len(pairs), n_asp_pairs_le6A=sum(1 for d,_,_ in pairs if d<=6),
        tightest_asp_pairs=" ".join(f"{i}-{j}:{d}" for d,i,j in pairs[:3]),
        schema_version=SCHEMA_VERSION))
hdr=list(out[0].keys())
dest=sys.argv[1] if len(sys.argv)>1 else ROOT+"/analysis/stage3b_design/TRUTH_TABLE.tsv"
with open(dest,"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=hdr,delimiter="\t",lineterminator="\n"); w.writeheader(); w.writerows(out)
print("chains scanned:",len(out))
