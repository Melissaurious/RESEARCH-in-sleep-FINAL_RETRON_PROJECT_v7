#!/usr/bin/env python3
"""s3c_gB — JOIN of frozen Stage-2 state blocks onto frozen Stage-3A units (LAUNCHER_03C 7a, B).

1. Applies the frozen production mapper rtmap-1.0.0/53a1e738a19b3896, unmodified, through its own
   production runner (inherited eligibility rule: >= 250 aa, standard residues), to the 62 chains'
   modelled sequences. Nothing about the instrument is refitted.
2. K5 positive control: on 5G2X_C (LtrA itself) the g7a-MAPPED LtrA states must land on the same
   LtrA residue number in >= 0.95 of cases.
3. Maps every state residue to author keys and PDP units; summarises each state block per chain.

State blocks are the Stage-2 erratum's supporting-state lists. They are NAMED BY BLOCK; the
historical label is given only as the LtrA-local correspondence it is (K7). RT0 and RT1 have no
states and are reported NO_STATES_BY_CONSTRUCTION on every chain.
"""
import collections
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

AVAIL_MIN = 0.50      # DECLARED: block available if >= this fraction of its states are MAPPED
CONTAIN_MIN = 0.80    # DECLARED: block contained if >= this fraction of its mapped residues sit in one unit
SPAN_UNIT_MIN = 0.20  # DECLARED: a unit "holds" a block if it carries >= this fraction of it
K5_MIN = 0.95         # DECLARED (K5)

MAPDIR = os.path.join(L.TABLES, "mapper")
WORK = os.path.join(os.environ.get("TMPDIR", "/tmp"), "s3c_mapper_work")

# ---- 1. frozen instrument, production runner --------------------------------------------------
for d in (MAPDIR, WORK):
    if os.path.isdir(d):
        shutil.rmtree(d)
os.makedirs(MAPDIR)
subprocess.run([sys.executable, os.path.join(L.MAPPER, "code", "rtmap", "run_mapper.py"),
                "--in", os.path.join(L.TABLES, "chains.faa"), "--out", MAPDIR, "--shard", "s3c",
                "--work", WORK], check=True)
# s3c.provenance.tsv carries host, paths and timestamps: landed, but declared NOT byte-reproducible
# (as g4b declares its own). The DONE sidecar is a resume marker, not a product.
os.remove(os.path.join(MAPDIR, "s3c.DONE"))
shutil.rmtree(WORK, ignore_errors=True)

states = collections.defaultdict(dict)
for r in L.read_tsv(os.path.join(MAPDIR, "s3c.states.tsv")):
    states[r["sequence_id"]][int(r["state_id"])] = r
seqsum = {r["sequence_id"]: r for r in L.read_tsv(os.path.join(MAPDIR, "s3c.sequences.tsv"))}
fails = {r["sequence_id"]: r for r in L.read_tsv(os.path.join(MAPDIR, "s3c.failures.tsv"))}

imap = collections.defaultdict(dict)
for r in L.read_tsv(os.path.join(L.TABLES, "chain_index_map.tsv")):
    imap[r["chain"]][int(r["seq_index"])] = (int(r["resnum"]), r["icode"])

# ---- 2. K5 positive control on LtrA itself ---------------------------------------------------
g7a = {int(r["state_id"]): r for r in L.read_tsv(os.path.join(L.STAGE2, "g7a_state_to_residue.tsv"))}
k5 = []
for sid, r in sorted(g7a.items()):
    if r["call_state"] != "MAPPED":
        continue
    s = states["5G2X_C"].get(sid)
    got = imap["5G2X_C"][int(s["sequence_residue_index"])][0] if s and s["call_state"] == "MAPPED" else None
    k5.append(dict(state_id=sid, ltra_residue_g7a=int(r["ltra_residue"]), call_state_5G2X=s["call_state"] if s else "",
                   resnum_5G2X=got if got is not None else "",
                   agrees="YES" if got == int(r["ltra_residue"]) else "NO"))
k5_rate = sum(x["agrees"] == "YES" for x in k5) / len(k5)
L.write_tsv(os.path.join(L.TABLES, "B_control_K5_ltra.tsv"), k5, list(k5[0]))
print(f"K5 LtrA control: {sum(x['agrees']=='YES' for x in k5)}/{len(k5)} = {k5_rate:.4f}")
if k5_rate < K5_MIN:
    sys.exit("KILL K5: mapper positive control failed on 5G2X_C")

# ---- 3. blocks --------------------------------------------------------------------------------
err = {r["historical_label"]: r for r in L.read_tsv(os.path.join(L.STAGE2, "g7a_closure_decision_erratum_2026-09-19.tsv"))}


def states_of(label):
    return [int(x) for x in err[label]["supporting_states"].split(",") if x]


BLOCKS = [
    ("RT0_none", [], "RT0", "UNRESOLVED / NOT IDENTIFIABLE"),
    ("RT1_none", [], "RT1", "UNRESOLVED / NOT IDENTIFIABLE"),
    ("SB2p", states_of("RT2"), "RT2", "PARTIAL - only LtrA 97-123 of 79-123 observed"),
    ("SB3", states_of("RT3"), "RT3", "ESTABLISHED with qualification (Route C not independent)"),
    ("SB4", states_of("RT4"), "RT4", "ESTABLISHED with frame-instability qualification (SPLIT_INTO_3, Jaccard 0.410)"),
    ("SB56", states_of("RT5"), "RT5+RT6", "RT5 ESTABLISHED / RT6 PARTIAL - joint region only"),
    ("SB7", states_of("RT7"), "RT7", "ESTABLISHED with narrowed wording"),
    ("CAT262", [262], "catalytic state (not an anchor)", "CAT_STATE 262; separate measurement"),
]
assert states_of("RT5") == states_of("RT6")
inv = {r["pdb"]: r for r in L.read_tsv(os.path.join(L.ROOT, "results/rt07_pre_g4_scope_separation/tables/structure_reference_inventory.tsv"))}
t1 = L.t1()

rows, rrows, merges = [], [], []
for c in L.chains():
    pdb = c.split("_")[0]
    indep = ("NOT_INDEPENDENT_OF_MAPPER (anchor-set member)" if inv.get(pdb, {}).get("in_26_anchor_set") == "YES"
             else "not an anchor-set member" if pdb in inv else "NOT_IN_INVENTORY (membership unknown)")
    if c in fails:
        verdict, mf = "INPUT_INVALID:" + fails[c]["reason_code"], ""
    else:
        verdict, mf = seqsum[c]["verdict"], seqsum[c]["mapped_fraction"]
    modelled = {x["key"]: x for x in L.ss_residues(c)}
    for arm in ("primary", "p4"):
        lab = L.pdp_labels(arm)[c]
        members = L.unit_members(lab)
        units = L.units_table(arm)
        call = L.calls_table(arm)[c]
        role_of = {}
        for role, col in (("palm-like", "palm_unit"), ("thumb-like", "thumb_unit"), ("fingers-like", "fingers_unit")):
            if call[col]:
                role_of[int(call[col])] = role
        contained_in = collections.defaultdict(list)
        for block, sids, label, status in BLOCKS:
            base = dict(chain=c, arm=arm, biological_group=t1[c]["biological_group"], stratum=t1[c]["stratum"],
                        implementation_sensitive=t1[c]["implementation_sensitive"], mapper_verdict=verdict,
                        mapped_fraction=mf, mapper_independence=indep, block=block, block_states=len(sids),
                        historical_label_LtrA_local=label, stage2_status=status)
            if not sids:
                rows.append(dict(base, n_mapped=0, frac_mapped=None, available="NO", resnum_span="",
                                 n_in_units=0, n_outside_units=0, modal_unit="", modal_unit_frac=None,
                                 n_units_holding=0, units_holding="", containment="NO_STATES_BY_CONSTRUCTION",
                                 modal_unit_role="", modal_unit_discontinuous="", modal_unit_frac_E="",
                                 modal_unit_frac_H=""))
                continue
            placed = []
            for sid in sids:
                if block == "CAT262":
                    # CAT_STATE 262 is NOT one of the 150 anchors: the frozen instrument reports it
                    # in the sequence summary, never in the state table. Separate measurement,
                    # separate denominator (CURRENT_PROJECT_STATE section 2).
                    q = seqsum.get(c)
                    s = (dict(call_state=q["cat_call_state"], sequence_residue_index=q["cat_residue_index"],
                              amino_acid=q["cat_residue"]) if q and q["cat_residue_index"] else None)
                else:
                    s = states.get(c, {}).get(sid)
                cs = s["call_state"] if s else ("INPUT_INVALID" if c in fails else "")
                key = imap[c][int(s["sequence_residue_index"])] if s and s["call_state"] == "MAPPED" else None
                st, u = L.residue_state(lab, key, modelled) if key else ("", None)
                if arm == "primary":
                    rrows.append(dict(chain=c, block=block, state_id=sid, call_state=cs,
                                      seq_index=s["sequence_residue_index"] if s else "",
                                      resnum=key[0] if key else "", icode=key[1] if key else "",
                                      amino_acid=s["amino_acid"] if s and key else "",
                                      residue_state=st, unit_primary=u if u is not None else "",
                                      unit_p4=(L.residue_state(L.pdp_labels("p4")[c], key, modelled)[1] or "") if key else ""))
                if key:
                    placed.append((sid, key, st, u))
            n_map = len(placed)
            frac = n_map / len(sids)
            avail = frac >= AVAIL_MIN
            in_u = [p for p in placed if p[3] is not None]
            cnt = collections.Counter(p[3] for p in in_u)
            modal, mc = (cnt.most_common(1)[0] if cnt else (None, 0))
            mfrac = mc / n_map if n_map else None
            holding = sorted(u for u, k in cnt.items() if k / n_map >= SPAN_UNIT_MIN) if n_map else []
            if not avail:
                cont = "NOT_AVAILABLE"
            elif not in_u:
                # mapped, but every residue is PDP_UNASSIGNED or PDP_ABSENT - not a split
                cont = "AVAILABLE_BUT_NO_RESIDUE_IN_A_UNIT"
            elif mfrac is not None and mfrac >= CONTAIN_MIN:
                cont = "CONTAINED"
                contained_in[modal].append(block)
            else:
                cont = "SPLIT"
            ur = units.get((c, modal)) if modal is not None else None
            keys = sorted(p[1] for p in placed)
            rows.append(dict(base, n_mapped=n_map, frac_mapped=frac, available="YES" if avail else "NO",
                             resnum_span=f"{keys[0][0]}-{keys[-1][0]}" if keys else "",
                             n_in_units=len(in_u), n_outside_units=n_map - len(in_u),
                             modal_unit=modal if modal is not None else "", modal_unit_frac=mfrac,
                             n_units_holding=len(holding), units_holding=",".join(map(str, holding)),
                             containment=cont, modal_unit_role=role_of.get(modal, "unclassified") if modal is not None else "",
                             modal_unit_discontinuous=("YES" if ur and int(ur["n_segments"]) > 1 else "NO") if ur else "",
                             modal_unit_frac_E=ur["frac_E"] if ur else "", modal_unit_frac_H=ur["frac_H"] if ur else ""))
        for u in sorted(members):
            bl = [b for b in contained_in.get(u, []) if b != "CAT262"]
            merges.append(dict(chain=c, arm=arm, unit=u, unit_n_res=len(members[u]),
                               unit_role=role_of.get(u, "unclassified"), blocks_contained=",".join(bl),
                               n_blocks_contained=len(bl), CAT262_in_unit="YES" if "CAT262" in contained_in.get(u, []) else "NO",
                               merge="MERGE" if len(bl) >= 2 else ("ONE_BLOCK" if bl else "NO_BLOCK")))

L.write_tsv(os.path.join(L.S3C, "STRUCTURE_STAGE2_CROSSWALK.tsv"), rows, list(rows[0]))
L.write_tsv(os.path.join(L.TABLES, "B_state_residue_join.tsv"), rrows, list(rrows[0]))
L.write_tsv(os.path.join(L.TABLES, "B_unit_block_membership.tsv"), merges, list(merges[0]))

# K7 guard: no RT0/RT1 interval anywhere, and no block row names a label as a measured domain
bad = [r for r in rows if r["block"] in ("RT0_none", "RT1_none") and (r["resnum_span"] or r["n_mapped"])]
if bad:
    sys.exit("KILL K7: RT0/RT1 received an interval")
prim = [r for r in rows if r["arm"] == "primary"]
print("verdicts:", collections.Counter(r["mapper_verdict"] for r in prim if r["block"] == "SB3"))
print("containment:", collections.Counter((r["block"], r["containment"]) for r in prim))
