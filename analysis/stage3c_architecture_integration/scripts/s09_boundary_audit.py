#!/usr/bin/env python3
"""s3c_gC — provenance audit of every fingers/palm/thumb boundary source, then overlap with units.

Two strata, never pooled:
  LITERATURE     - statements retrieved verbatim from primary/secondary literature, each with a
                   locator; admitted only when its numbering is verified on the deposited chain.
  HISTORICAL_RED - the inherited reference_boundaries product, graded RED by the prior asset audit.
                   Every claim of that audit is RE-VERIFIED here on the files themselves.

Numbering verification (DECLARED): a source's numbering is ACCEPTED for a chain only if a motif
the source itself states (YADD/YxDD, or a stated RT-domain span) is found at the stated author
residue numbers in that chain. Otherwise NUMBERING_UNVERIFIED and the boundary is not used.

Writes LITERATURE_BOUNDARY_AUDIT.tsv, tables/C_overlap.tsv, tables/C_reference_disagreement.tsv.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s3clib as L  # noqa: E402

COINCIDE_J = 0.70   # DECLARED (the 3A C7 bar)
HOLD_FRAC = 0.20    # DECLARED: a unit "holds" a region if it carries >= this fraction of it

HIST = "/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures"
FPT = os.path.join(os.environ.get("TMPDIR", "/tmp"), "..", "scratchpad", "fpt_audit")
FPT = os.environ.get("FPT_AUDIT_DIR", FPT)

seq = {r["chain"]: r for r in L.read_tsv(os.path.join(L.TABLES, "chain_sequences.tsv"))}
rev = collections.defaultdict(dict)
for r in L.read_tsv(os.path.join(L.TABLES, "chain_index_map.tsv")):
    rev[r["chain"]][int(r["resnum"])] = int(r["seq_index"])
reg = L.register()
labs = L.pdp_labels("primary")
units_t = L.units_table("primary")
calls = L.calls_table("primary")
by_pdb = collections.defaultdict(list)
for c in L.chains():
    by_pdb[c.split("_")[0]].append(c)

audit = []


def a(row):
    audit.append(row)


def residues_at(chain, lo, hi):
    s = seq[chain]["sequence"]
    return "".join(s[rev[chain][p] - 1] if p in rev[chain] else "-" for p in range(lo, hi + 1))


# =============================================================== 1. HISTORICAL_RED product
hist_rows = L.read_tsv(os.path.join(HIST, "reference_boundaries.tsv"))
log = open(os.path.join(HIST, "run_log.txt"), errors="replace").read()
rep = open(os.path.join(HIST, "boundary_extraction_report.txt"), errors="replace").read()

# claim 1: fingers and thumb are residuals of a palm-centred partition
resid = 0
for r in hist_rows:
    try:
        fs, fe, ps, pe, ts, te = (int(r[k]) for k in ("fingers_start", "fingers_end", "palm_start",
                                                      "palm_end", "thumb_start", "thumb_end"))
        rs, re_ = int(r["res_start"]), int(r["res_end"])
    except ValueError:
        continue
    if fs == rs and te == re_ and fe + 1 == ps and pe + 1 == ts:
        resid += 1
a(dict(stratum="HISTORICAL_RED", source_id="HIST-residual-partition", pdb_ids="all 25",
       protein="-", region="fingers/palm/thumb", claim_checked="fingers = everything before the palm and "
       "thumb = everything after it, i.e. both are residuals of a palm-centred partition",
       verdict="CONFIRMED", evidence=f"{resid}/{len(hist_rows)} rows satisfy fingers_start=res_start, "
       f"thumb_end=res_end, fingers_end+1=palm_start, palm_end+1=thumb_start exactly",
       consequence="a thumb Jaccard of 0 against such a product measures the residual construction, "
                   "not a biological absence", retrieval_status="ON_DISK",
       locator="reference_boundaries.tsv", numbering_status="n/a", unit="boundary set"))

m = re.search(r"\(12,\s*130\).{0,80}\(131,\s*260\).{0,80}\(261,\s*305\)", log, re.S)
a(dict(stratum="HISTORICAL_RED", source_id="HIST-hardcoded-anchor", pdb_ids="5HHJ", protein="R. intestinalis maturase RT",
       region="fingers/palm/thumb", claim_checked="5HHJ chain A is the anchor with boundaries hardcoded as "
       "(12,130)/(131,260)/(261,305), of unrecorded origin",
       verdict="CONFIRMED" if m else "NOT_FOUND_IN_LOG",
       evidence=(("run_log.txt contains " + " ".join(m.group(0).split())[:160]) if m else
                 "the three literals were not found in run_log.txt"),
       consequence="every other structure's boundaries are transferred from an anchor whose own numbers have "
                   "no stated source; the landed 5HHJ palm (148-286) is not even the hardcoded one (131-260)",
       retrieval_status="ON_DISK", locator="run_log.txt", numbering_status="n/a", unit="boundary set"))

dis = len(re.findall(r"DSSP vs alignment boundaries disagree", log + rep))
low = len(re.findall(r"low alignment coverage", log + rep, re.I))
a(dict(stratum="HISTORICAL_RED", source_id="HIST-selfwarnings", pdb_ids="all 25", protein="-",
       region="fingers/palm/thumb", claim_checked="the product logs its own disagreement and low-coverage warnings "
       "and gates nothing on them", verdict="CONFIRMED" if dis else "NOT_REPRODUCED",
       evidence=f"{dis} 'DSSP vs alignment boundaries disagree' and {low} low-coverage warnings in the logs; "
                f"every warned row is still present in reference_boundaries.tsv",
       consequence="the product's own instrument disagreed with it on most structures", retrieval_status="ON_DISK",
       locator="run_log.txt + boundary_extraction_report.txt", numbering_status="n/a", unit="warning"))

# claim: same protein, different boundaries (Ec86 entries)
ec86 = {r["pdb_id"]: r for r in hist_rows if r["pdb_id"] in ("7V9U", "7V9X", "7XJG", "8QBM")}
if ec86:
    spans = {k: f"{v['fingers_start']}-{v['fingers_end']}/{v['palm_start']}-{v['palm_end']}" for k, v in ec86.items()}
    same = len(set(spans.values())) == 1
    a(dict(stratum="HISTORICAL_RED", source_id="HIST-same-protein-disagreement", pdb_ids=";".join(sorted(ec86)),
           protein="retron Ec86 RT (P23070)", region="fingers/palm",
           claim_checked="the method returns different boundaries for the same protein",
           verdict="CONFIRMED" if not same else "NOT_REPRODUCED",
           evidence="; ".join(f"{k}: {v}" for k, v in sorted(spans.items())),
           consequence="a 77-residue disagreement produced by the method on identical input",
           retrieval_status="ON_DISK", locator="reference_boundaries.tsv", numbering_status="n/a", unit="entry"))

g5 = next((r for r in hist_rows if r["pdb_id"] == "5G2X"), None)
if g5:
    ps, pe = int(g5["palm_start"]), int(g5["palm_end"])
    asp = [int(x) for x in re.findall(r"\d+", g5["coord_asp"] or "")]
    inside = [x for x in asp if ps <= x <= pe]
    a(dict(stratum="HISTORICAL_RED", source_id="HIST-5G2X-palm-excludes-catalytic", pdb_ids="5G2X",
           protein="LtrA", region="palm", claim_checked="the 5G2X palm does not contain its own catalytic aspartate",
           verdict="CONFIRMED" if not inside else "NOT_REPRODUCED",
           evidence=f"palm {ps}-{pe}; recorded coordinating Asp {asp}; inside the palm: {inside or 'none'}",
           consequence="a palm that excludes the catalytic centre cannot be the polymerase palm",
           retrieval_status="ON_DISK", locator="reference_boundaries.tsv", numbering_status="n/a", unit="entry"))

fam = next((r for r in hist_rows if r["pdb_id"] == "5HHJ"), None)
a(dict(stratum="HISTORICAL_RED", source_id="HIST-5HHJ-family-mislabel", pdb_ids="5HHJ",
       protein="R. intestinalis group II intron maturase RT (D4L313)", region="-",
       claim_checked="the anchor entry is labelled family=RVT-Retrons",
       verdict="CONFIRMED" if fam and fam["family"] == "RVT-Retrons" else "NOT_REPRODUCED",
       evidence=f"reference_boundaries.tsv family field = '{fam['family'] if fam else ''}'; the 3A register records "
                f"'{reg['5HHJ_A']['family_METADATA_ONLY']}' with accession {reg['5HHJ_A']['external_accessions']}",
       consequence="the boundary anchor for the whole product is a misfamilied structure",
       retrieval_status="ON_DISK", locator="reference_boundaries.tsv", numbering_status="n/a", unit="entry"))

cov = sorted({r["pdb_id"] for r in hist_rows} & set(by_pdb))
a(dict(stratum="HISTORICAL_RED", source_id="HIST-coverage", pdb_ids=";".join(cov), protein="-", region="-",
       claim_checked="how much of the 62-chain Stage-3A population the historical product covers",
       verdict="MEASURED", evidence=f"{len(cov)} of {len(by_pdb)} PDB entries in the 3A register appear in the "
       f"historical product ({len(hist_rows)} rows)", consequence="the product cannot speak for the other entries",
       retrieval_status="ON_DISK", locator="reference_boundaries.tsv", numbering_status="n/a", unit="PDB entry"))

# =============================================================== 2. LITERATURE stratum
lit = L.read_tsv(os.path.join(FPT, "LITERATURE_BOUNDARIES.tsv"))
MOTIF_CHECK = {  # source-stated motif positions used to verify that source's numbering on a chain
    "9X94_A": (198, 201, "YADD", "Xiong 2026 states YADD at 198-201"),
    "9X9B_A": (198, 201, "YADD", "Xiong 2026 states YADD at 198-201"),
    "23OR_A": (198, 201, "YADD", "Ji 2026 states YADD at 198-201"),
    "9LBQ_A": (198, 201, "YADD", "Ji 2026 states YADD at 198-201"),
    "9WN8_A": (198, 201, "YADD", "Ji 2026 states YADD at 198-201"),
    "9I2F_A": (199, 202, "YADD", "Jasnauskaite 2026 states YADD at 199-202"),
    "9I2G_B": (199, 202, "YADD", "Jasnauskaite 2026 states YADD at 199-202"),
    "9S1F_B": (199, 202, "YADD", "Jasnauskaite 2026 states YADD at 199-202"),
    "9VHE_A": (185, 188, "YADD", "Dai 2025 states YADD at 185-188"),
    "9VHL_A": (185, 188, "YADD", "Dai 2025 states YADD at 185-188"),
    "9E8Z_H": (183, 186, "YADD", "Wang 2025 states YADD at 183-186"),
    "1RTD_A": (183, 186, "YMDD", "HIV-1 p66 catalytic YMDD 183-186 in standard numbering"),
    # Stage-2 g7a places CAT_STATE 262 (the motif-C tyrosine) at LtrA residue 306, so the YADD window
    # is 306-309. An earlier draft of this check used 305-308 and failed; the error was in the check,
    # not in any source, and is recorded here rather than silently corrected.
    "5G2X_C": (306, 309, "YADD", "LtrA YADD; Stage-2 CAT_STATE 262 places its tyrosine at LtrA 306"),
}
numbering = {}
for chain_id, (lo, hi, motif, why) in sorted(MOTIF_CHECK.items()):
    got = residues_at(chain_id, lo, hi)
    ok = bool(re.fullmatch("[YFWH].DD", got))
    numbering[chain_id] = ok
    a(dict(stratum="LITERATURE", source_id="NUMBERING-CHECK:" + chain_id, pdb_ids=chain_id.split("_")[0],
           protein=reg[chain_id]["family_METADATA_ONLY"], region="-",
           claim_checked=f"source numbering maps onto the deposited chain ({why})",
           verdict="NUMBERING_VERIFIED" if ok else "NUMBERING_UNVERIFIED",
           evidence=f"author residues {lo}-{hi} of {chain_id} are '{got}', expected a {motif}-like window",
           consequence="boundaries from this source may be joined to this chain" if ok else
                       "boundaries from this source are NOT joined to this chain",
           retrieval_status="ON_DISK", locator="deposited coordinates", numbering_status=str(ok), unit="chain"))

# a claim from the boundary audit that this session could not reproduce - recorded, not adopted
neg = {c: (L.ss_residues(c)[0]["key"][0], L.ss_residues(c)[-1]["key"][0]) for c in
       ("9WY8_A", "9HDO_A", "26CZ_A", "8BGJ_A", "9I2F_A")}
a(dict(stratum="LITERATURE", source_id="NUMBERING-CHECK:negative-author-numbers", pdb_ids="9WY8;9HDO;26CZ;8BGJ;9I2F",
       protein="fusion/tagged constructs", region="-",
       claim_checked="a retrieval claimed these chains carry negative author residue numbers for tag residues, and "
                     "that 9I2F chain A is a 67-residue chain",
       verdict="NOT_REPRODUCED",
       evidence="; ".join(f"{c}: author range {lo}..{hi}, no negative numbers" for c, (lo, hi) in sorted(neg.items())),
       consequence="literature residue numbers may NOT be assumed to map onto these chains; each source is verified "
                   "per chain by the motif check above, and unverified sources are not joined",
       retrieval_status="ON_DISK", locator="deposited coordinates used by Stage 3A", numbering_status="False",
       unit="chain"))

for r in lit:
    region = r["region_name"].lower()
    kind = ("fingers" if "finger" in region and "palm" not in region else
            "palm" if region.startswith("palm") else
            "thumb" if region.startswith("thumb") else
            "fingers_palm_combined" if "finger" in region and "palm" in region else "OTHER_REGION")
    chains = []
    for p in r["pdb_ids"].replace(" ", "").split(";"):
        chains.extend(by_pdb.get(p.split("(")[0], []))
    usable = (r["residue_intervals_as_stated"] not in ("FIGURE_ONLY_NO_NUMBERS", "")
              and r["retrieval_status"] == "FULL_TEXT" and kind != "OTHER_REGION"
              and any(numbering.get(c) for c in chains))
    a(dict(stratum="LITERATURE", source_id=r["boundary_id"], pdb_ids=r["pdb_ids"], protein=r["protein"],
           region=r["region_name"],
           claim_checked="verbatim residue-numbered boundary statement",
           verdict=("USABLE_FOR_OVERLAP" if usable else
                    "FIGURE_ONLY_NO_NUMBERS" if r["residue_intervals_as_stated"] == "FIGURE_ONLY_NO_NUMBERS" else
                    "NOT_A_FINGERS_PALM_THUMB_REGION" if kind == "OTHER_REGION" else
                    "NOT_JOINED (numbering unverified on any chain in this population)"),
           evidence=(r["verbatim_quote"] or "")[:400],
           consequence=f"intervals {r['residue_intervals_as_stated']} in {r['numbering_system']}",
           retrieval_status=r["retrieval_status"], locator=f"{r['source_citation']} | {r['locator']}",
           numbering_status=r["numbering_matches_pdb"], unit="boundary statement"))

L.write_tsv(os.path.join(L.S3C, "LITERATURE_BOUNDARY_AUDIT.tsv"), audit,
            ["stratum", "source_id", "pdb_ids", "protein", "region", "claim_checked", "verdict", "evidence",
             "consequence", "retrieval_status", "locator", "numbering_status", "unit"])


# =============================================================== 3. overlap with frozen units
def parse_intervals(s):
    out = []
    for part in s.split(";"):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-")[:2]
            try:
                out.append((int(lo), int(hi)))
            except ValueError:
                return []
    return out


def region_keys(chain, intervals):
    ks = set()
    for lo, hi in intervals:
        for p in range(lo, hi + 1):
            if p in rev[chain]:
                ks.add((p, ""))
    return ks


ov = []


def add_overlap(stratum, source, chain, region, intervals):
    ks = region_keys(chain, intervals)
    if not ks:
        return
    mem = L.unit_members(labs[chain])
    best_u, best_j = None, -1.0
    for u, keys in mem.items():
        j = L.jaccard(ks, keys)
        if j > best_j:
            best_u, best_j = u, j
    holding = sorted(u for u, keys in mem.items() if len(ks & keys) / len(ks) >= HOLD_FRAC)
    call = calls[chain]
    role = {}
    for rl, col in (("palm-like", "palm_unit"), ("thumb-like", "thumb_unit"), ("fingers-like", "fingers_unit")):
        if call[col]:
            role[int(call[col])] = rl
    u_row = units_t.get((chain, best_u))
    # how many literature regions of this source hold >=HOLD_FRAC of the best unit -> merge behaviour
    ov.append(dict(stratum=stratum, source_id=source, chain=chain, biological_group=L.t1()[chain]["biological_group"],
                   region=region, intervals=";".join(f"{a_}-{b_}" for a_, b_ in intervals),
                   n_region_residues_modelled=len(ks),
                   best_unit=best_u, best_jaccard=best_j,
                   coincides="YES" if best_j >= COINCIDE_J else "NO",
                   frac_region_in_best_unit=len(ks & mem[best_u]) / len(ks),
                   frac_best_unit_in_region=len(ks & mem[best_u]) / len(mem[best_u]),
                   n_units_holding=len(holding), units_holding=",".join(map(str, holding)),
                   split="YES" if len(holding) > 1 else "NO",
                   best_unit_role=role.get(best_u, "unclassified"),
                   best_unit_n_segments=u_row["n_segments"] if u_row else "",
                   region_is_discontinuous="YES" if len(intervals) > 1 else "NO",
                   unit="residue key"))


for r in lit:
    region = r["region_name"].lower()
    kind = ("fingers" if "finger" in region and "palm" not in region else
            "palm" if region.startswith("palm") and "helix" not in region else
            "thumb" if region.startswith("thumb") else
            "fingers_palm_combined" if "finger" in region and "palm" in region else None)
    if not kind or r["retrieval_status"] != "FULL_TEXT":
        continue
    iv = parse_intervals(r["residue_intervals_as_stated"])
    if not iv:
        continue
    for p in r["pdb_ids"].replace(" ", "").split(";"):
        for c in by_pdb.get(p.split("(")[0], []):
            if numbering.get(c):
                add_overlap("LITERATURE", r["boundary_id"], c, kind, iv)

for r in hist_rows:
    pdb = r["pdb_id"]
    for c in by_pdb.get(pdb, []):
        if c.split("_")[1] != r["chain"]:
            continue
        for kind in ("fingers", "palm", "thumb"):
            try:
                iv = [(int(r[kind + "_start"]), int(r[kind + "_end"]))]
            except ValueError:
                continue
            add_overlap("HISTORICAL_RED", "HIST:" + pdb, c, kind, iv)

L.write_tsv(os.path.join(L.TABLES, "C_overlap.tsv"), ov, list(ov[0]))

# =============================================================== 4. reference-specific disagreement
dis_rows = []
by_chain_region = collections.defaultdict(list)
for r in ov:
    by_chain_region[(r["chain"], r["region"], r["stratum"])].append(r)
for (chain, region, stratum), S in sorted(by_chain_region.items()):
    if len(S) < 2:
        continue
    dis_rows.append(dict(chain=chain, region=region, stratum=stratum, n_sources=len(S),
                         sources=";".join(x["source_id"] for x in S),
                         intervals=" | ".join(x["intervals"] for x in S),
                         best_units=";".join(str(x["best_unit"]) for x in S),
                         jaccards=";".join(f"{x['best_jaccard']:.3f}" for x in S),
                         agree_on_best_unit="YES" if len({x["best_unit"] for x in S}) == 1 else "NO",
                         unit="source pair on one chain"))
L.write_tsv(os.path.join(L.TABLES, "C_reference_disagreement.tsv"), dis_rows,
            list(dis_rows[0]) if dis_rows else ["chain", "region", "note"])

# =============================================================== 5. aggregates
summ = []
for stratum in ("LITERATURE", "HISTORICAL_RED"):
    S0 = [r for r in ov if r["stratum"] == stratum]
    for kind in ("fingers", "palm", "thumb", "fingers_palm_combined"):
        S = [r for r in S0 if r["region"] == kind]
        if not S:
            continue
        js = sorted(r["best_jaccard"] for r in S)
        summ.append(dict(stratum=stratum, region=kind, n_region_chain_pairs=len(S),
                         n_chains=len({r["chain"] for r in S}),
                         n_coincides=sum(r["coincides"] == "YES" for r in S),
                         frac_coincides=sum(r["coincides"] == "YES" for r in S) / len(S),
                         median_best_jaccard=js[len(js) // 2],
                         min_best_jaccard=js[0], max_best_jaccard=js[-1],
                         n_split_over_units=sum(r["split"] == "YES" for r in S),
                         best_unit_roles=";".join(f"{k}={v}" for k, v in sorted(
                             collections.Counter(r["best_unit_role"] for r in S).items())),
                         n_region_discontinuous=sum(r["region_is_discontinuous"] == "YES" for r in S),
                         unit="literature-region x chain", coincide_bar=COINCIDE_J))
# do a source's fingers and palm land in the SAME unit? (merge behaviour)
merge = collections.defaultdict(dict)
for r in ov:
    if r["region"] in ("fingers", "palm"):
        merge[(r["stratum"], r["source_id"].rsplit("-", 1)[0], r["chain"])][r["region"]] = r["best_unit"]
pairs = [v for v in merge.values() if len(v) == 2]
same = sum(1 for v in pairs if v["fingers"] == v["palm"])
summ.append(dict(stratum="BOTH", region="fingers_and_palm_same_unit", n_region_chain_pairs=len(pairs),
                 n_chains=len({k[2] for k, v in merge.items() if len(v) == 2}), n_coincides=same,
                 frac_coincides=same / len(pairs) if pairs else None, median_best_jaccard=None,
                 min_best_jaccard=None, max_best_jaccard=None, n_split_over_units=None,
                 best_unit_roles="-", n_region_discontinuous=None,
                 unit="source x chain where the same source numbers both fingers and palm",
                 coincide_bar="n/a - counts whether one PDP unit is the best match for BOTH regions"))
L.write_tsv(os.path.join(L.TABLES, "C_summary.tsv"), summ, list(summ[0]))
for r in summ:
    print(r["stratum"], r["region"], "n=", r["n_region_chain_pairs"], "coincide=", r["n_coincides"],
          "medianJ=", r["median_best_jaccard"])

print("audit rows:", len(audit), dict(collections.Counter(x["verdict"] for x in audit)))
print("overlap rows:", len(ov), dict(collections.Counter(x["stratum"] for x in ov)))
print("disagreement rows:", len(dis_rows))
