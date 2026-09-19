#!/usr/bin/env python3
"""build - assemble the Stage-2 final reporting package from the frozen, reviewed record.

This script COMPUTES NO SCIENCE. It:
  1. resolves every value in findings.py from a landed table (exactly one row per selector),
     a declared display derivation over landed rows, or a literal verified in a reviewed record;
  2. checks the eight RT0-RT7 statuses against the governing erratum table and that the
     production crosswalk is still UNRESOLVED in all eight rows;
  3. writes the report tables, renders templates/*.md into report/ and DELIVERABLES_INDEX.md;
  4. fails on any unresolved placeholder and on any superseded or withdrawn wording.

Landing commits are read from git history at the pinned source-of-record commit, so a rerun
gives the same answer however many commits land later.
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import findings as F  # noqa: E402
import ledger as L  # noqa: E402

PH = re.compile(r"\{\{([A-Za-z0-9_:]+)\}\}")


def rows(p: Path) -> list[dict]:
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t"))


def write_tsv(p: Path, cols: list[str], rs: list[dict]) -> None:
    with p.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rs:
            fh.write("\t".join(str(r[c]).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")


def fmt(v: str, kind: str) -> str:
    if kind == "int":
        return f"{int(float(v)):,d}"
    return str(v)


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout


def die(msg: str) -> None:
    raise SystemExit(f"FATAL: {msg}")


# ---------------------------------------------------------------------------------------------
def resolve(root: Path) -> tuple[dict, dict, list]:
    vals, raw, trace = {}, {}, []
    for k, (path, sel, col, kind) in F.TABLE.items():
        p = root / path
        if not p.exists():
            die(f"{k}: no such table {path}")
        m = [r for r in rows(p) if all(r.get(a, "") == b for a, b in sel.items())]
        if len(m) != 1:
            die(f"{k}: selector {sel} matched {len(m)} rows in {path}")
        if col not in m[0]:
            die(f"{k}: no column {col} in {path}")
        raw[k], vals[k] = m[0][col], fmt(m[0][col], kind)
        trace.append(dict(key=k, kind="TABLE", source=path,
                          selector=";".join(f"{a}={b}" for a, b in sel.items()), column=col,
                          raw_value=raw[k], rendered=vals[k]))

    # DERIVED - declared display derivations over landed rows, formula carried into the trace.
    st = rows(root / F.G6T)
    dfy = sum(1 for r in st if r["tool"] == "DefenseFinder" and r["powered"] == "YES")
    ply = sum(1 for r in st if r["tool"] == "PADLOC" and r["powered"] == "YES")
    under = sum(1 for r in st if r["powered"] == "UNDERPOWERED")
    seqs = rows(root / F.UGS)
    ctl = {r["control_class"]: r for r in rows(root / F.UGN)}
    b = rows(root / F.G6B)
    der = {
        "g6_strata_total": len(st),
        "g6_strata_underpowered": under,
        "g6_strata_excluded": under + (dfy - int(raw["g6_df_groups"])) + (ply - int(raw["g6_pl_groups"])),
        "ug25_min_real_mapped": min(int(r["n_mapped"]) for r in seqs),
        "ug25_n_seq": len(seqs),
        "ug25_ctrl_max": max(int(ctl[c]["max_mapped"]) for c in ("MONO", "DI", "REV")),
        "g6_ctrl_exceed_both": sum(1 for r in b if r["analysis_id"].startswith(("CTRL-VIS", "CTRL-REL"))
                                   and r["exceeds_null1"] == "YES" and r["exceeds_null2"] == "YES"),
    }
    if set(der) != set(F.DERIVED):
        die("DERIVED keys and their implementations disagree")
    for k, v in der.items():
        raw[k], vals[k] = str(v), f"{v:,d}"
        trace.append(dict(key=k, kind="DERIVED", source="(see formula)", selector=F.DERIVED[k],
                          column="", raw_value=raw[k], rendered=vals[k]))
    # The erratum verified 26 by hand from the same rows; the build must agree with it.
    if der["g6_strata_excluded"] != 26 or der["g6_strata_total"] != 50:
        die("the g6 strata derivation no longer reproduces E-g6-4 (26 of 50)")

    for k, (src, lit, rendered) in F.DOC.items():
        text = git(root, "show", "-s", "--format=%B", src[4:]) if src.startswith("git:") \
            else (root / src).read_text(encoding="utf-8")
        if lit not in text:
            die(f"{k}: the literal is not present in {src}: {lit!r}")
        raw[k], vals[k] = lit, rendered
        trace.append(dict(key=k, kind="DOC", source=src, selector="literal present verbatim",
                          column="", raw_value=lit.replace("\n", " "), rendered=rendered))
    return vals, raw, trace


def commits(root: Path) -> tuple[dict, dict]:
    pin = F.PINNED_COMMIT
    if git(root, "rev-parse", pin).strip() != pin:
        die(f"pinned commit {pin} is not in this repository")
    landed, last = {}, {}
    for bnd, _, _ in F.BUNDLES:
        adds = git(root, "log", "--diff-filter=A", "--format=%H", pin, "--", f"results/{bnd}").split()
        if not adds:
            die(f"bundle {bnd} was never landed at {pin}")
        landed[bnd] = adds[-1]
        last[bnd] = git(root, "log", "-1", "--format=%H", pin, "--", f"results/{bnd}").strip()
    return landed, last


def path_commit(root: Path, path: str) -> str:
    if path.startswith("git:"):
        return git(root, "rev-parse", path[4:]).strip()
    return git(root, "log", "-1", "--format=%H", F.PINNED_COMMIT, "--", path).strip()


def bundle_of(path: str) -> str:
    return path.split("/")[1] if path.startswith("results/") else "(governing record)"


def fill(text: str, vals: dict, where: str, tables: dict | None = None) -> str:
    def sub(m):
        k = m.group(1)
        if k.startswith("TABLE:"):
            if tables is None or k[6:] not in tables:
                die(f"{where}: no table block {k}")
            return tables[k[6:]]
        if k not in vals:
            die(f"{where}: placeholder {{{{{k}}}}} has no declared lookup")
        return vals[k]
    out = PH.sub(sub, text)
    if PH.search(out):
        die(f"{where}: an unresolved placeholder survived")
    return out


def md_table(cols: list[str], rs: list[dict], heads: list[str] | None = None) -> str:
    heads = heads or cols
    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
    out = ["| " + " | ".join(heads) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(esc(r[c]) for c in cols) + " |" for r in rs]
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------
# Historical evidence per label, transcribed from the g7a evidence register as CORRECTED by
# E-g7a-2 (X05/X06 are source-stated) and E-g7a-4 (R364/R365 is a source-described proteolytic
# landmark). Every clause names its source; nothing here is a new reading.
HIST = {
    "RT0": "Named by Zimmerly et al. 2001 (as a scope rule: which classes carry it) and Blocker et al. "
           "2005; defining source {{malik_missing}}, not held. Blocker: the N-terminal fragment M1-R85 CONTAINS RT0; "
           "interior conserved alanine A{{g3_rt0_alanine}}. No C-terminal edge stated anywhere.",
    "RT1": "Xiong & Eickbush 1990 domain 1 (alignment block, no residue coordinates); Blocker places R85 "
           "INSIDE RT1 (interior point, not an edge). The only prior-frame landmark that moves between frames (g3).",
    "RT2": "Xiong & Eickbush 1990 domain 2 (alignment block, no coordinates); X06 {{x06}} (source-stated, "
           "no coordinates).",
    "RT3": "Xiong & Eickbush 1990 domain 3; X05 {{x05}} and X06 {{x06}} (source-stated motif-set "
           "correspondences, no coordinates).",
    "RT4": "Xiong & Eickbush 1990 domain 4; X05 and X06 (no coordinates); Zimmerly 2001 relative position: "
           "the 4|5 junction sits at the widest inter-block gap.",
    "RT5": "Xiong & Eickbush 1990 domain 5; X05 (no coordinates); Zimmerly 2001 feature anchor: the "
           "catalytic YxDD lies in subdomain 5 - the only residue-level feature tied to a label.",
    "RT6": "Xiong & Eickbush 1990 domain 6; X05 (no coordinates). No feature anchor of its own.",
    "RT7": "Xiong & Eickbush 1990 domain 7; X05 (no coordinates); Blocker 2005: R364/R365 is a "
           "source-described between-domain proteolytic landmark ('between RT7 and domain X'); Zimmerly "
           "2001 relative C-terminal position.",
}


def build_final_table(root: Path, vals: dict) -> list[dict]:
    err = {r["historical_label"]: r for r in rows(root / F.ERR)}
    xw = {r["historical_label"]: r for r in rows(root / F.G7X)}
    prod = {r["historical_label"]: r for r in rows(root / "results/rt07_g4b_production_mapper/control/CROSSWALK_RT0_RT7.tsv")}
    if sorted(err) != sorted(F.STATUS) or sorted(xw) != sorted(F.STATUS):
        die("erratum or crosswalk does not carry exactly RT0-RT7")
    for lab, (full, _, _) in F.STATUS.items():
        if err[lab]["terminal_status"] != full:
            die(f"{lab}: erratum status {err[lab]['terminal_status']!r} differs from the reviewed {full!r}")
        if err[lab]["terminal_status_changed"] != "NO":
            die(f"{lab}: erratum records a status change")
        if prod[lab]["historical_RT0_RT7_correspondence_if_supported"] != "UNRESOLVED":
            die(f"{lab}: the production crosswalk is no longer UNRESOLVED")
    out = []
    for lab in sorted(F.STATUS):
        full, short, qual = F.STATUS[lab]
        x, e = xw[lab], err[lab]
        if x["n_supporting_states"] == "0":
            reach = (f"none - 0 frozen anchor states map inside the reference interval; anchor reach is "
                     f"LtrA {vals['g7_anchor_span']}")
        else:
            reach = (f"{x['n_supporting_states']} states ({x['state_span']}) -> LtrA "
                     f"{x['ltra_residue_span_supported']}")
        out.append(dict(
            label=lab,
            historical_evidence=fill(HIST[lab], vals, f"HIST {lab}"),
            reconstructed_interval_ltra=x["reference_interval_ltra"],
            interval_source=x["reference_interval_source"],
            mapper_reach_on_ltra=reach,
            correspondence=e["correspondence_qualified"],
            final_status=full,
            status_short=short + (f" ({qual})" if qual else ""),
            may_say=e["downstream_may_say_corrected"],
            errata=e["errata_applied"],
            governing_record="docs/errata/g7a_closure_decision_erratum_2026-09-19.tsv",
        ))
    return out


# ---------------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, help="repository root")
    ap.add_argument("--out", required=True, help="bundle directory to write into")
    a = ap.parse_args()
    root, out, bundle = Path(a.root).resolve(), Path(a.out), HERE.parent
    for d in ("tables", "report"):
        (out / d).mkdir(parents=True, exist_ok=True)

    vals, raw, trace = resolve(root)
    landed, last = commits(root)
    vals["pinned"] = F.PINNED_COMMIT
    vals["pinned_short"] = F.PINNED_COMMIT[:7]
    for bnd in landed:
        vals[f"landed_{bnd}"] = landed[bnd][:7]
    T = out / "tables"

    # T1 - the RT0-RT7 final table
    final = build_final_table(root, vals)
    fcols = ["label", "historical_evidence", "reconstructed_interval_ltra", "interval_source",
             "mapper_reach_on_ltra", "correspondence", "final_status", "status_short", "may_say",
             "errata", "governing_record"]
    write_tsv(T / "stage2_rt0_rt7_final.tsv", fcols, final)

    # T3 - review ledger (every row's verdict and score verified against its record)
    rev = []
    for seq, layer, obj, verdict, score, disp, rec, lit in L.REVIEWS:
        text = git(root, "show", "-s", "--format=%B", rec[4:]) if rec.startswith("git:") \
            else (root / rec).read_text(encoding="utf-8")
        if lit not in text:
            die(f"review ledger row {seq}: literal not in {rec}: {lit!r}")
        rev.append(dict(seq=seq, layer=layer, object=obj, verdict=verdict,
                        score_of_10=score or "n/a - not completed", disposition=disp, record=rec,
                        verified_literal=lit.replace("\n", " ")))
    write_tsv(T / "stage2_review_ledger.tsv", list(rev[0]), rev)

    # T4 - negative and null results
    neg = [dict(id=i, layer=ly, result=fill(r, vals, i), rules_out=ro, why_informative=fill(w, vals, i),
                source=s) for i, ly, r, ro, w, s in L.NEGATIVES]
    write_tsv(T / "stage2_negative_results.tsv", list(neg[0]), neg)

    # T2 - claim-evidence matrix: one row per (claim, evidence value)
    src = {t["key"]: t for t in trace}
    cem = []
    for cid, layer, claim, keys, note in L.CLAIMS:
        ctext = fill(claim, vals, cid)
        for k in keys:
            if k not in src:
                die(f"{cid}: evidence key {k} is not a declared lookup")
            t = src[k]
            path = t["source"] if t["kind"] != "DERIVED" else {
                "g6_strata_total": F.G6T, "g6_strata_underpowered": F.G6T, "g6_strata_excluded": F.G6T,
                "ug25_min_real_mapped": F.UGS, "ug25_n_seq": F.UGS, "ug25_ctrl_max": F.UGN,
                "g6_ctrl_exceed_both": F.G6B}[k]
            bnd = bundle_of(path)
            cem.append(dict(claim_id=cid, layer=layer, claim=ctext, permitted_scope=note, evidence_key=k,
                            value=vals[k], lookup_kind=t["kind"], source=path, selector=t["selector"],
                            column=t["column"], bundle=bnd,
                            bundle_landing_commit=landed.get(bnd, "n/a - governing record"),
                            source_commit_at_pin=path_commit(root, path)))
    write_tsv(T / "stage2_claim_evidence_matrix.tsv", list(cem[0]), cem)

    # T5 - frozen parameters, read from the instrument's own control tables
    par = [dict(parameter=p, value=vals[k], source=F.TABLE[k][0] if k in F.TABLE else F.DOC[k][0])
           for p, k in [("mapper_version", "mapper_version"), ("instrument_sha256", "instrument_sha"),
                        ("profile", "profile_leng"), ("match_state_convention", "profile_m"),
                        ("N_ANCHORS", "n_anchors"), ("PP_HI", "pp_hi"), ("PP_LO", "pp_lo"),
                        ("S_MIN", "s_min"), ("K_MIN", "k_min"), ("T1", "t1"), ("D_MAX", "d_max"),
                        ("D_RANDOM", "d_random"), ("CAT_STATE", "cat_state"),
                        ("CAT_STATE construction agreement", "cat_agree"), ("MIN_AA", "min_aa")]]
    par[2]["parameter"], par[2]["value"] = "profile LENG (GII.deriv.hmm)", vals["profile_leng"]
    write_tsv(T / "stage2_frozen_parameters.tsv", ["parameter", "value", "source"], par)

    # T6 - resolved values (the audit trail)
    write_tsv(T / "stage2_resolved_values.tsv",
              ["key", "kind", "source", "selector", "column", "raw_value", "rendered"],
              sorted(trace, key=lambda r: r["key"]))

    # T7 - figure plan
    fp = [dict(id=i, figure=f"figures/{s}.png", plotted_numbers=f"tables/{s}.tsv", question=qn,
               source_tables=st, may_show=ms, may_not_show=mn) for i, s, qn, st, ms, mn in L.FIGURES]
    write_tsv(T / "stage2_figure_plan.tsv", list(fp[0]), fp)

    # bundle index
    bix = []
    for bnd, layer, role in F.BUNDLES:
        rp = root / "results" / bnd / "README.md"
        rd = rp.read_text(encoding="utf-8").splitlines() if rp.exists() else []
        status = next((ln for ln in rd if ln.startswith("STATUS:")),
                      "STATUS: (none stated)" if rd else "(no README.md; see the bundle's PROVENANCE or governing decision record)")
        bix.append(dict(bundle=f"results/{bnd}", layer=layer, role=role, landing_commit=landed[bnd],
                        last_commit_at_pin=last[bnd], readme_status=status.split("—")[0].strip()))
    write_tsv(T / "stage2_bundle_index.tsv", list(bix[0]), bix)

    # markdown blocks for the templates
    blocks = {
        "rt0_rt7_final": md_table(
            ["label", "historical_evidence", "reconstructed_interval_ltra", "mapper_reach_on_ltra",
             "status_short", "may_say"], final,
            ["label", "historical evidence (held sources)", "reference interval on LtrA (g2 block; RT0: source upper bound)",
             "mapper reach on LtrA", "final reviewed status", "caveat / what may be said"]),
        "rt0_rt7_compact": md_table(
            ["label", "reconstructed_interval_ltra", "mapper_reach_on_ltra", "status_short"], final,
            ["label", "reference interval on LtrA (g2 block; RT0: source upper bound)", "frozen-state support", "final reviewed status"]),
        "review_ledger": md_table(["seq", "layer", "object", "verdict", "score_of_10", "disposition"], rev,
                                  ["#", "layer", "object", "verdict", "score /10", "disposition"]),
        "negatives": md_table(["id", "layer", "result", "rules_out", "why_informative"], neg,
                              ["id", "layer", "result", "rules out", "why it is informative"]),
        "bundles": md_table(["bundle", "layer", "role", "landing_commit"],
                            [dict(r, landing_commit=r["landing_commit"][:7]) for r in bix]),
        "claims": md_table(["claim_id", "layer", "claim", "permitted_scope"],
                           [dict(claim_id=c, layer=ly, claim=fill(t, vals, c), permitted_scope=n)
                            for c, ly, t, _, n in L.CLAIMS],
                           ["id", "layer", "claim", "permitted scope"]),
        "parameters": md_table(["parameter", "value"], par),
        "figures": md_table(["id", "figure", "question", "may_not_show"], fp,
                            ["id", "file", "question", "must not be read as"]),
    }

    tmpl = bundle / "templates"
    targets = {"STAGE2_TECHNICAL_REPORT.md": out / "report" / "STAGE2_TECHNICAL_REPORT.md",
               "THESIS_METHODS.md": out / "report" / "THESIS_METHODS.md",
               "THESIS_RESULTS.md": out / "report" / "THESIS_RESULTS.md",
               "THESIS_DISCUSSION.md": out / "report" / "THESIS_DISCUSSION.md",
               "DELIVERABLES_INDEX.md": out / "DELIVERABLES_INDEX.md"}
    for name, dst in targets.items():
        dst.write_text(fill((tmpl / name).read_text(encoding="utf-8"), vals, name, blocks), encoding="utf-8")

    # guard: superseded or withdrawn wording may not appear in anything this package writes
    written = list(targets.values()) + sorted(T.glob("stage2_*.tsv"))
    for p in written:
        text = p.read_text(encoding="utf-8")
        for pat, why in F.FORBIDDEN:
            if re.search(pat, text, flags=re.I):
                die(f"{p.name}: superseded wording /{pat}/ present - {why}")
    # guard: every final status appears verbatim in the technical report and the results
    for name in ("STAGE2_TECHNICAL_REPORT.md", "THESIS_RESULTS.md"):
        text = targets[name].read_text(encoding="utf-8")
        for lab, (full, _, _) in F.STATUS.items():
            if not re.search(rf"{lab}\b.*{re.escape(full)}", text):
                die(f"{name}: no line gives {lab} its reviewed status {full!r}")

    print(f"resolved {len(trace)} values; {len(rev)} reviews; {len(neg)} negative results; "
          f"{len(L.CLAIMS)} claims / {len(cem)} evidence links; {len(targets)} documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
