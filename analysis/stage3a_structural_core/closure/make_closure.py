#!/usr/bin/env python3
"""Stage-3A closure: final tables and figures, derived ONLY from frozen Stage-3A outputs.

Refuses to run unless (i) the frozen RT partition hashes match RT_PARTITION_FREEZE_sha256.txt and (ii) every
input under g2r/results and g2r/tables is unmodified relative to the git index. Computes nothing new beyond
counting/tabulating frozen outputs; no parser, SS route or C4–C7 rule is re-executed.

Usage (from analysis/stage3a_structural_core):  python closure/make_closure.py
"""
import csv, collections, hashlib, os, re, subprocess, statistics, sys
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.environ.get("TMPDIR", "/tmp"), "mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

R, T, O = "g2r/results", "g2r/tables", "closure"
os.makedirs(f"{O}/tables", exist_ok=True); os.makedirs(f"{O}/figures", exist_ok=True)

# ---- frozen-input guard ----
for l in open(f"{R}/RT_PARTITION_FREEZE_sha256.txt"):
    h, p = l.split()
    p = p.replace("analysis/stage3a_structural_core/", "")
    assert hashlib.sha256(open(p, "rb").read()).hexdigest() == h, f"frozen partition changed: {p}"
dirty = subprocess.run(["git", "status", "--porcelain", "--", R, T, "STRUCTURE_REGISTER.tsv"],
                       capture_output=True, text=True).stdout.strip()
assert not dirty, f"frozen inputs modified:\n{dirty}"
HEAD = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def rd(p):
    return list(csv.DictReader(open(p), delimiter="\t"))


def wr(name, rows, cols=None):
    cols = cols or list(rows[0].keys())
    with open(f"{O}/tables/{name}.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    md += ["| " + " | ".join(str(r.get(c, "")).replace("|", "\\|") for c in cols) + " |" for r in rows]
    return "\n".join(md)


MD = {}
reg = rd("STRUCTURE_REGISTER.tsv")
calls = {r["chain"]: r for r in rd(f"{R}/rt_units.calls.tsv")}
units = rd(f"{R}/rt_units.units.tsv")
sens = {r["chain"]: r for r in rd(f"{R}/rt_pdp_implementation_sensitivity.tsv")}
ssc = {r["chain"]: r for r in rd(f"{R}/rt_ss_concordance.per_chain.tsv")}

# ---- T1 structure register (no lineage/family metadata: those enter only in Stage 3C) ----
t1 = []
for r in reg:
    c = f"{r['pdb_id']}_{r['chain']}"
    t1.append(dict(chain=c, biological_group=r["biological_group"], method=r["method"], resolution_A=r["resolution_A"],
                   n_modelled=r["n_modelled_residues"], n_missing_internal=r["n_missing_internal"],
                   fused_or_accessory=r["fused_or_accessory"], modified_residues=r["modified_polymer_residues"] or "-",
                   stratum=calls[c]["stratum"], n_units=calls[c]["n_units"],
                   implementation_sensitive=sens[c]["IMPLEMENTATION_SENSITIVE"], ss_chain_gate=ssc[c]["chain_ss_gate"]))
t1.sort(key=lambda r: (r["biological_group"], r["chain"]))
MD["T1"] = wr("T1_structure_register", t1)

# ---- T2 parser validation ----
gp, g4 = rd(f"{R}/cath_score_primary.gates.tsv"), rd(f"{R}/cath_score_p4.gates.tsv")
t2 = [dict(gate=a["gate"], measure=a["metric"], n=a["n"], bar=a["bar"], primary=f"{float(a['value']):.3f}",
           primary_pass="PASS" if a["pass"] == "1" else "FAIL", bj_p4=f"{float(b['value']):.3f}",
           bj_p4_pass="PASS" if b["pass"] == "1" else "FAIL") for a, b in zip(gp, g4)]
MD["T2"] = wr("T2_parser_validation", t2)
pc = rd(f"{R}/cath_score_primary.per_chain.tsv")
conf = collections.Counter((int(r["n_cath"]), int(r["n_pdp"])) for r in pc)
maxp = max(k[1] for k in conf)
t2b = [dict(CATH_domains=n, **{f"PDP_{m}": conf.get((n, m), 0) for m in range(1, maxp + 1)}) for n in (1, 2, 3, 4)]
MD["T2b"] = wr("T2b_parser_confusion_primary", t2b)
dv = [float(r["overlap"]) for r in pc if r["count_ok"] == "1"]
parser_extra = dict(boundary_correct=f"{sum(o >= 0.85 for o in dv)}/{len(dv)}",
                    median_overlap_all=f"{statistics.median(float(r['overlap']) for r in pc):.3f}",
                    one_domain_oversplit=f"{sum(1 for r in pc if r['n_cath'] == '1' and r['n_pdp'] != '1')}/30")

# ---- T3 SS validation ----
sg = rd(f"{R}/rt_ss_concordance.gate.tsv")
t3 = [dict(state=r["state"], metric=r["metric"], value=f"{float(r['median']):.3f}", n=r["n_defined"], bar=r["bar"],
           result="PASS" if r["pass"] == "1" else "FAIL") for r in sg]
for s in ("E", "H"):
    k = [float(r[f"{s}_kappa"]) for r in ssc.values() if r[f"{s}_kappa"] != "NA"]
    t3.append(dict(state=s, metric="min per-chain kappa", value=f"{min(k):.3f}", n=len(k), bar="0.70 (chain gate)",
                   result="PASS" if min(k) >= 0.70 else "SOME FAIL"))
MD["T3"] = wr("T3_secondary_structure_validation", t3)

# ---- T4 unit counts / discontinuity ----
strata = {"primary": [c for c in calls if calls[c]["stratum"] == "primary"],
          "flagged": [c for c in calls if calls[c]["stratum"] == "flagged"],
          "design_exposed": [c for c in calls if calls[c]["stratum"] == "design_exposed"],
          "all_62": list(calls)}
t4 = []
for s, cs in strata.items():
    cs_ = set(cs)
    u = [x for x in units if x["chain"] in cs_]
    nu = [int(calls[c]["n_units"]) for c in cs]
    palm = [x for x in u if x["role"] == "palm-like"]
    t4.append(dict(stratum=s, chains=len(cs), units=len(u),
                   units_per_chain_dist=" ".join(f"{k}:{v}" for k, v in sorted(collections.Counter(nu).items())),
                   median_units_per_chain=statistics.median(nu),
                   discontinuous_units=f"{sum(int(x['n_segments']) > 1 for x in u)}/{len(u)}",
                   median_unit_size=statistics.median(int(x["n_res"]) for x in u) if u else "",
                   palm_like_discontinuous=f"{sum(int(x['n_segments']) > 1 for x in palm)}/{len(palm)}",
                   EXTRA_DOMAIN_units=f"{sum(x['EXTRA_DOMAIN'] == '1' for x in u)}/{len(u)}"))
MD["T4"] = wr("T4_unit_counts_discontinuity", t4)

# ---- parse frozen report (primary / flagged / pooled; LOGO) ----
rep = open(f"{R}/rt_units.report.txt").read()
rep4 = open(f"{R}/rt_units_p4.report.txt").read()


def parse(txt):
    out, cur = {}, None
    for l in txt.splitlines():
        m = re.match(r"## (\w+) \(n=(\d+)\)\s+verdict-rule outcome: (\w+)", l)
        if m: cur = m.group(1); out[cur] = dict(n=int(m.group(2)), verdict=m.group(3)); continue
        m = re.match(r"(C4b?|C5)\tcall_rate=([\d.]+)\tC6=(\w+)\(median=([\w.]+),group_pairs=(\d+),absent_in_Y=(\d+)\)"
                     r"\tC7=(\w+)\(median=([\w.]+),groups=(\d+),numbering_excluded=(\d+)\)\tmeets=(\w+)", l)
        if m and cur:
            out[cur][m.group(1)] = m.groups()[1:]
        m = re.match(r"replicate PDP domain-count agreement: ([\w.]+) over (\d+) pairs", l)
        if m and cur: out[cur]["dca"] = (m.group(1), m.group(2))
        m = re.match(r"call-status counts: (.*)", l)
        if m and cur: out[cur]["status"] = m.group(1)
    logo = {k: v for k, v in re.findall(r"^(C4b?|C5)\tcall_rate ([^\n]+)$", txt, re.M)}
    folds = re.search(r"LOGO folds by verdict: (.*?); folds flipping.*?: (.*)", txt)
    return out, logo, folds.groups()


P, LOGO, FOLDS = parse(rep)
P4, _, FOLDS4 = parse(rep4)
REG = {"C4": "palm-like", "C5": "thumb-like", "C4b": "fingers-like"}

# ---- T5 call rates ----
t5 = []
for s in ("primary", "flagged", "all_nonexposed"):
    for k, name in REG.items():
        v = P[s][k]
        cnt = re.search(rf"{k}: (\{{[^}}]*\}})", P[s]["status"]).group(1)
        t5.append(dict(stratum=s, n=P[s]["n"], region=name, criterion=k, call_rate=v[0], bar="0.70",
                       meets_rate="yes" if float(v[0]) >= 0.70 else "no", status_counts=cnt))
MD["T5"] = wr("T5_call_rates", t5)

# ---- T6 recurrence / stability ----
t6 = []
for s in ("primary", "flagged", "all_nonexposed"):
    for k, name in REG.items():
        v = P[s][k]
        t6.append(dict(stratum=s, region=name, C6_status=v[1], C6_median=v[2], C6_group_pairs=v[3],
                       C6_absent_in_Y=v[4], C7_status=v[5], C7_median=v[6], C7_groups=v[7],
                       C7_numbering_excluded=v[8], region_meets_all_bars=v[9]))
MD["T6"] = wr("T6_recurrence_stability", t6)

# ---- T7 replicate instability ----
byg = collections.defaultdict(list)
for c in calls:
    byg[calls[c]["group"]].append(c)
t7 = []
for g, cs in sorted(byg.items()):
    if len(cs) < 2: continue
    nu = [int(calls[c]["n_units"]) for c in sorted(cs)]
    prs = [(a, b) for i, a in enumerate(nu) for b in nu[i + 1:]]
    t7.append(dict(biological_group=g, chains=len(cs), strata=",".join(sorted({calls[c]["stratum"] for c in cs})),
                   unit_counts=",".join(str(x) for x in nu), distinct_counts=len(set(nu)),
                   pair_agreement=f"{sum(a == b for a, b in prs)}/{len(prs)}",
                   palm_calls=f"{sum(calls[c]['C4'] == 'CALL' for c in cs)}/{len(cs)}"))
MD["T7"] = wr("T7_replicate_instability", t7)
rep_summary = {s: P[s]["dca"] for s in ("primary", "flagged", "all_nonexposed")}

# ---- T8 fusion / large-chain and code sensitivity ----
t8 = []
for s in ("primary", "flagged", "all_nonexposed"):
    t8.append(dict(analysis=f"stratum:{s}", n=P[s]["n"], verdict=P[s]["verdict"],
                   palm_call_rate=P[s]["C4"][0], thumb_call_rate=P[s]["C5"][0], fingers_call_rate=P[s]["C4b"][0],
                   replicate_count_agreement=f"{P[s]['dca'][0]} ({P[s]['dca'][1]} pairs)"))
t8.append(dict(analysis="BJ-p4 parser (primary)", n=P4["primary"]["n"], verdict=P4["primary"]["verdict"],
               palm_call_rate=P4["primary"]["C4"][0], thumb_call_rate=P4["primary"]["C5"][0],
               fingers_call_rate=P4["primary"]["C4b"][0],
               replicate_count_agreement=f"{P4['primary']['dca'][0]} ({P4['primary']['dca'][1]} pairs)"))
t8.append(dict(analysis="LOGO (22 folds, primary)", n="45-46 minus group", verdict=FOLDS[0],
               palm_call_rate=LOGO["C4"].split("\t")[0], thumb_call_rate=LOGO["C5"].split("\t")[0],
               fingers_call_rate=LOGO["C4b"].split("\t")[0], replicate_count_agreement=f"flips: {FOLDS[1]}"))
MD["T8"] = wr("T8_fusion_and_sensitivity", t8)
t8b = [dict(chain=c, stratum=calls[c]["stratum"], n_primary=sens[c]["n_primary"], n_p4=sens[c]["n_p4"],
            overlap=sens[c]["overlap"], C4_primary=calls[c]["C4"]) for c in sorted(sens) if sens[c]["IMPLEMENTATION_SENSITIVE"] == "1"]
MD["T8b"] = wr("T8b_implementation_sensitive_chains", t8b)

# ---- figures ----
plt.rcParams.update({"font.size": 9, "savefig.dpi": 200, "savefig.bbox": "tight"})
# F1 parser validation
fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
M = np.array([[conf.get((n, m), 0) for m in range(1, maxp + 1)] for n in (1, 2, 3, 4)])
ax[0].imshow(M, cmap="Greys"); ax[0].set_xticks(range(maxp)); ax[0].set_xticklabels(range(1, maxp + 1))
ax[0].set_yticks(range(4)); ax[0].set_yticklabels([1, 2, 3, 4]); ax[0].set_xlabel("PDP domains"); ax[0].set_ylabel("CATH domains")
for i in range(4):
    for j in range(maxp):
        if M[i, j]: ax[0].text(j, i, M[i, j], ha="center", va="center", color="red" if i + 1 == j + 1 else "tab:blue")
ax[0].set_title("A  CATH benchmark: domain count (n=100)")
gv = [(r["gate"], float(r["primary"]), float(r["bar"])) for r in t2]
ax[1].bar([g for g, _, _ in gv], [v for _, v, _ in gv], color="0.6")
ax[1].scatter([g for g, _, _ in gv], [b for _, _, b in gv], marker="_", s=400, color="red", label="frozen bar")
ax[1].set_ylim(0, 1.05); ax[1].set_title("B  Acceptance gates (primary parser)"); ax[1].legend(frameon=False)
fig.savefig(f"{O}/figures/F1_parser_validation.png"); plt.close(fig)
# F2 SS concordance
fig, ax = plt.subplots(figsize=(4.5, 3.2))
for i, s in enumerate(("E", "H")):
    k = [float(r[f"{s}_kappa"]) for r in ssc.values() if r[f"{s}_kappa"] != "NA"]
    ax.scatter(np.full(len(k), i) + np.random.default_rng(0).uniform(-.15, .15, len(k)), k, s=8, color="0.3")
ax.axhline(0.70, color="red", lw=.8, ls="--", label="chain gate 0.70"); ax.axhline(0.75, color="orange", lw=.8, label="population median bar 0.75")
ax.set_xticks([0, 1]); ax.set_xticklabels(["strand (E)", "helix (H)"]); ax.set_ylim(0.6, 1.01); ax.set_ylabel("Cohen's κ, mkdssp vs pydssp")
ax.legend(frameon=False, fontsize=7); ax.set_title("Secondary-structure instrument (62 chains)")
fig.savefig(f"{O}/figures/F2_ss_concordance.png"); plt.close(fig)
# F3 unit counts and discontinuity
fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
for s, col in (("primary", "0.3"), ("flagged", "tab:orange")):
    nu = collections.Counter(int(calls[c]["n_units"]) for c in strata[s])
    xs = np.arange(1, 9)
    ax[0].bar(xs + (-.2 if s == "primary" else .2), [nu.get(x, 0) for x in xs], width=.4, color=col, label=s)
ax[0].set_xlabel("PDP units per chain"); ax[0].set_ylabel("chains"); ax[0].legend(frameon=False); ax[0].set_title("A  Units per chain")
cats = ["all units", "palm-like units"]
for i, s in enumerate(("primary",)):
    u = [x for x in units if x["chain"] in set(strata[s])]
    pl = [x for x in u if x["role"] == "palm-like"]
    fr = [sum(int(x["n_segments"]) > 1 for x in u) / len(u), sum(int(x["n_segments"]) > 1 for x in pl) / len(pl)]
    ax[1].bar(cats, fr, color="0.5")
    for j, (a, b) in enumerate(((sum(int(x["n_segments"]) > 1 for x in u), len(u)), (sum(int(x["n_segments"]) > 1 for x in pl), len(pl)))):
        ax[1].text(j, fr[j] + .02, f"{a}/{b}", ha="center")
ax[1].set_ylim(0, 1); ax[1].set_ylabel("fraction discontinuous"); ax[1].set_title("B  Discontinuous units (primary)")
fig.savefig(f"{O}/figures/F3_units_discontinuity.png"); plt.close(fig)
# F4 call rates + LOGO range
fig, ax = plt.subplots(figsize=(5, 3.2))
names = list(REG.values()); rates = [float(P["primary"][k][0]) for k in REG]
lo = [float(LOGO[k].split("\t")[0].split()[0].split("-")[0]) for k in REG]
hi = [float(LOGO[k].split("\t")[0].split()[0].split("-")[1]) for k in REG]
ax.bar(names, rates, color="0.6")
ax.errorbar(names, rates, yerr=[np.array(rates) - lo, np.array(hi) - rates], fmt="none", ecolor="k", capsize=4, label="LOGO range")
ax.axhline(0.70, color="red", ls="--", lw=.8, label="frozen call-rate bar")
ax.set_ylim(0, 1); ax.set_ylabel("call rate (primary, n=46)"); ax.legend(frameon=False, fontsize=7)
ax.set_title("Region call rates")
fig.savefig(f"{O}/figures/F4_call_rates_logo.png"); plt.close(fig)
# F5 per-chain unit maps
order = sorted(calls, key=lambda c: (calls[c]["stratum"] != "primary", calls[c]["group"], c))
ROLEC = {"palm-like": "tab:red", "thumb-like": "tab:blue", "fingers-like": "tab:green"}
fig, ax = plt.subplots(figsize=(8, 11))
pdpres = collections.defaultdict(list)
for r in rd(f"{R}/rt_pdp_primary.residues.tsv"):
    pdpres[r["chain"]].append(int(r["domain"]))
for y, c in enumerate(order):
    lab = pdpres[c]; roles = {int(x["unit"]): x["role"] for x in units if x["chain"] == c}
    for i, d in enumerate(lab):
        col = ROLEC.get(roles.get(d, ""), None) if d else "white"
        if col is None: col = plt.cm.Greys(0.25 + 0.12 * (d % 5))
        ax.add_patch(plt.Rectangle((i, y - .4), 1, .8, color=col, lw=0))
    ax.text(-8, y, f"{c} ({calls[c]['stratum'][0]})", ha="right", va="center", fontsize=6)
ax.set_xlim(-2, max(len(v) for v in pdpres.values()) + 2); ax.set_ylim(len(order), -1); ax.set_yticks([])
ax.set_xlabel("ordered residue index (PDP representative atoms)")
for n, col in ROLEC.items(): ax.plot([], [], color=col, lw=6, label=n)
ax.plot([], [], color="0.6", lw=6, label="other PDP unit (grey shades)"); ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=7)
ax.set_title("C3r units per chain (p = primary, f = flagged, d = design-exposed)")
fig.savefig(f"{O}/figures/F5_unit_maps.png"); plt.close(fig)
# F6 replicate unit counts
fig, ax = plt.subplots(figsize=(7, 3))
gs = [r for r in t7]
for i, r in enumerate(gs):
    v = [int(x) for x in r["unit_counts"].split(",")]
    ax.scatter(np.full(len(v), i) + np.linspace(-.15, .15, len(v)), v, s=14, color="tab:orange" if "flagged" in r["strata"] else "0.2")
ax.set_xticks(range(len(gs))); ax.set_xticklabels([r["biological_group"] for r in gs], rotation=90, fontsize=7)
ax.set_ylabel("PDP units"); ax.set_title(f"Replicate PDP unit counts per biological group (agreement {rep_summary['primary'][0]} over {rep_summary['primary'][1]} primary pairs; orange = flagged)")
fig.savefig(f"{O}/figures/F6_replicate_unit_counts.png"); plt.close(fig)

# ---- dump markdown table bundle + provenance ----
with open(f"{O}/tables/ALL_TABLES.md", "w") as fh:
    fh.write(f"<!-- generated by closure/make_closure.py at HEAD {HEAD} from frozen outputs only -->\n\n")
    titles = {"T1": "Table S3A-1. Experimental structure register (62 chains, 31 biological groups)",
              "T2": "Table S3A-2. External CATH validation of the C3r parser",
              "T2b": "Table S3A-2b. CATH→PDP domain-count confusion (primary parser)",
              "T3": "Table S3A-3. Secondary-structure instrument validation (mkdssp vs pydssp)",
              "T4": "Table S3A-4. Structural-unit counts and discontinuity",
              "T5": "Table S3A-5. Palm-, thumb- and fingers-like call rates",
              "T6": "Table S3A-6. Recurrence (C6) and replicate stability (C7)",
              "T7": "Table S3A-7. Replicate instability of the PDP partition",
              "T8": "Table S3A-8. Fusion/large-chain, parser-code and LOGO sensitivity",
              "T8b": "Table S3A-8b. Implementation-sensitive chains (primary vs BJ-p4)"}
    for k, t in titles.items():
        fh.write(f"### {t}\n\n{MD[k]}\n\n")
    fh.write(f"Parser secondary statistics: boundary-correct {parser_extra['boundary_correct']}; median overlap (all) "
             f"{parser_extra['median_overlap_all']}; single-domain over-split {parser_extra['one_domain_oversplit']}.\n")
print("HEAD", HEAD)
print("primary discontinuous:", t4[0]["discontinuous_units"], "| replicate agreement:", rep_summary, "| LOGO:", FOLDS, "| p4:", P4["primary"]["verdict"])
print("parser:", parser_extra)
