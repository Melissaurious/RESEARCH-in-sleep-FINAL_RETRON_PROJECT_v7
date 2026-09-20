#!/usr/bin/env python3
"""
T-A23c · Bounded retrieval of the primary sources behind the cross-pair curation.

FROZEN BEFORE EXECUTION (WORKING_RULES §6b).

Retrieves metadata, and open-access full text where the licence permits, for the
sources the A23 curation rests on.  Records availability and licence honestly: an
unavailable source is recorded as unavailable, which is itself a finding about the
evidence base.  No paywall circumvention.

⛔ It does not infer unmeasured negative pairs, and it opens no orthogonality
modelling.  It returns source-level evidence and curation consequences.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import argparse, json, os, re, time, urllib.parse, urllib.request

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UA = {"User-Agent": "retron-programme-A23c/1.0 (research; mailto:rioszemm@kaust.edu.sa)"}

# The named sources behind the curation, from A23_source_provenance.tsv
SOURCES = [
    {"source_id": "BUF2025", "role": "primary_research",
     "doi": "10.1038/s41587-025-02879-3",
     "title": "Discovery and engineering of retrons for precise genome editing",
     "why": "supplies the 7x7 panel; 42 of 56 curated rows rest on its caption"},
    {"source_id": "BOB2022", "role": "primary_research", "doi": None,
     "title": "Bacterial retrons encode phage-defending tripartite toxin-antitoxin systems",
     "why": "supplies assay contexts B1, B2a, B2b including the Sen2/Eco9 combinations"},
    {"source_id": "SIM2019", "role": "review", "doi": None,
     "title": "Retrons and their applications in genome engineering",
     "why": "the REVIEW through which refs 32, 33, 35, 36 are currently counted"},
    {"source_id": "SIM2019_ref32", "role": "secondhand_primary", "doi": None,
     "title": "retron msDNA reverse transcriptase specificity",
     "why": "counted as a primary study but read only through SIM2019"},
    {"source_id": "SIM2019_ref33", "role": "secondhand_primary", "doi": None,
     "title": "retron Ec86 msDNA synthesis in vivo",
     "why": "counted as a primary study but read only through SIM2019"},
    {"source_id": "SIM2019_ref35", "role": "secondhand_primary", "doi": None,
     "title": "retron msr msd RNA reverse transcriptase recognition",
     "why": "counted as a primary study but read only through SIM2019"},
    {"source_id": "SIM2019_ref36", "role": "secondhand_primary", "doi": None,
     "title": "multicopy single-stranded DNA retron chimera",
     "why": "counted as a primary study but read only through SIM2019"},
    {"source_id": "MVA1", "role": "primary_research", "doi": None,
     "title": "Myxococcus retron Mva1 cross-reactivity reverse transcriptase",
     "why": "the Mva1 cross-reactivity evidence"},
]

UNCERTAINTIES = [
    ("U1_7x7_every_cell_assayed",
     "Does the 7x7 heatmap caption mean every cell was assayed, or a panel from which "
     "only some cells were measured?", "BUF2025"),
    ("U2_six_nonfunctional_rows",
     "Are the six non-functional rows six measured cross-pairs, or one RT-level "
     "statement expanded six times?", "BUF2025"),
    ("U3_secondhand_primaries",
     "What do SIM2019 refs 32/33/35/36 actually report, read from the primary?",
     "SIM2019_ref32;SIM2019_ref33;SIM2019_ref35;SIM2019_ref36"),
    ("U4_mva1_crossreactivity", "What is the Mva1 cross-reactivity evidence?", "MVA1"),
    ("U5_sim2019_c2_chimera",
     "Is SIM2019-C2 a swapped pairing or a chimeric construct?", "SIM2019"),
    ("U6_direct_noncognate",
     "Which directly measured non-cognate RT-ncRNA pairings exist?", "ALL"),
]

CROSSPAIR_RX = re.compile(
    r"non-?cognate|cross-?react|chimer|swap|heterolog|cognate pair|mismatch(ed)? (RT|msr|msd)",
    re.I)


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def epmc_search(query, page_size=5):
    q = urllib.parse.quote(query)
    url = f"{EPMC}/search?query={q}&format=json&pageSize={page_size}&resultType=core"
    st, body = get(url)
    d = json.loads(body)
    return d.get("hitCount", 0), d.get("resultList", {}).get("result", [])


def epmc_fulltext(pmcid):
    try:
        st, body = get(f"{EPMC}/{pmcid}/fullTextXML", timeout=40)
        return body if st == 200 else None
    except Exception:
        return None


def tsv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else str(v).replace("\t", " ").replace("\n", " ")
                               for v in r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--prerun-commit", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.outdir)
    t0 = time.time()
    ctrl = []

    def add(c, t, b, e, o, s, d=""):
        ctrl.append([c, t, b, e, o, s, d])

    # ---- CONTROLS, opposite directions ---------------------------------
    try:
        n_pos, res = epmc_search('DOI:"10.1093/nar/gkz865"')
        ok_pos = n_pos > 0
        detail = res[0].get("title", "")[:80] if res else ""
    except Exception as ex:
        ok_pos, n_pos, detail = False, 0, f"{type(ex).__name__}: {ex}"
    add("A23c_POS_known_record", "positive", "YES",
        "a named known-indexed article is retrieved", f"{n_pos} hit(s)",
        "PASS" if ok_pos else "FAIL", detail)

    try:
        n_neg, _ = epmc_search('TITLE:"zzqxwv nonexistent retron qqzz 90210"')
        ok_neg = n_neg == 0
    except Exception as ex:
        n_neg, ok_neg = -1, False
    add("A23c_NEG_nonsense_query", "negative", "YES",
        "a constructed nonsense query returns zero results", f"{n_neg} hit(s)",
        "PASS" if ok_neg else "FAIL")

    if [c for c in ctrl if c[2] == "YES" and c[5] != "PASS"]:
        tsv(os.path.join(out, "tables/A23c_controls.tsv"),
            ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)
        print("BLOCKING CONTROL FAILURE — no primary table written")
        print("TASK_STATE: VOID")
        return 2

    # ---- retrieval ------------------------------------------------------
    srows, passages = [], []
    got = {}
    for s in SOURCES:
        q = f'DOI:"{s["doi"]}"' if s["doi"] else f'TITLE:"{s["title"]}"'
        try:
            hits, res = epmc_search(q, page_size=3)
            if hits == 0 and s["doi"] is None:
                hits, res = epmc_search(s["title"], page_size=3)
        except Exception as ex:
            srows.append([s["source_id"], s["role"], s["doi"], s["title"], "QUERY_ERROR",
                          f"{type(ex).__name__}", "", "", "", s["why"]])
            time.sleep(0.5)
            continue
        if not res:
            srows.append([s["source_id"], s["role"], s["doi"], s["title"],
                          "NOT_FOUND", "0 hits", "", "", "", s["why"]])
            time.sleep(0.5)
            continue
        r = res[0]
        pmcid = r.get("pmcid")
        oa = r.get("isOpenAccess", "N")
        lic = r.get("license", "")
        ft = None
        if pmcid and oa == "Y":
            ft = epmc_fulltext(pmcid)
        avail = ("FULLTEXT_OA" if ft else
                 "METADATA_ONLY_OA_NO_FULLTEXT" if oa == "Y" else
                 "METADATA_ONLY_NOT_OPEN_ACCESS")
        got[s["source_id"]] = ft
        srows.append([s["source_id"], s["role"], r.get("doi") or s["doi"],
                      (r.get("title") or "")[:160], avail,
                      f"pmid={r.get('pmid','')} pmcid={pmcid or ''}",
                      r.get("journalTitle", ""), r.get("pubYear", ""), lic, s["why"]])
        if ft:
            txt = re.sub(r"<[^>]+>", " ", ft)
            txt = re.sub(r"\s+", " ", txt)
            for m in CROSSPAIR_RX.finditer(txt):
                st_, en = max(0, m.start() - 260), min(len(txt), m.end() + 260)
                passages.append([s["source_id"], m.group(0), txt[st_:en]])
                if len([p for p in passages if p[0] == s["source_id"]]) >= 25:
                    break
        time.sleep(0.6)

    tsv(os.path.join(out, "tables/A23c_sources.tsv"),
        ["source_id", "role", "doi", "retrieved_title", "availability", "identifiers",
         "journal", "year", "license", "why_it_matters"], srows)
    tsv(os.path.join(out, "tables/A23c_crosspair_passages.tsv"),
        ["source_id", "matched_term", "passage"], passages)

    urows = []
    for uid, question, need in UNCERTAINTIES:
        ids = [x for x in need.split(";")] if need != "ALL" else list(got)
        have = [i for i in ids if got.get(i)]
        n_pass = sum(1 for p in passages if p[0] in ids)
        urows.append([uid, question, need,
                      "FULLTEXT_AVAILABLE" if have else "NO_FULLTEXT",
                      ";".join(have) or "none", n_pass,
                      "resolvable from retrieved text" if have and n_pass
                      else "NOT RESOLVABLE from what could be retrieved"])
    tsv(os.path.join(out, "tables/A23c_uncertainties.tsv"),
        ["uncertainty_id", "question", "sources_needed", "retrieval_state",
         "sources_with_fulltext", "n_candidate_passages", "verdict"], urows)

    n_ft = sum(1 for r in srows if r[4] == "FULLTEXT_OA")
    n_nf = sum(1 for r in srows if r[4] == "NOT_FOUND")
    tsv(os.path.join(out, "tables/A23c_curation_consequences.tsv"),
        ["consequence", "detail"],
        [["sources_named", len(SOURCES)],
         ["full_text_retrieved", n_ft],
         ["metadata_only", sum(1 for r in srows if r[4].startswith("METADATA_ONLY"))],
         ["not_found", n_nf],
         ["uncertainties_resolvable", sum(1 for r in urows if r[6].startswith("resolvable"))],
         ["uncertainties_unresolved", sum(1 for r in urows if r[6].startswith("NOT"))],
         ["standing_rule", "no unmeasured negative pair is inferred; absence from a panel is "
                           "not a measured non-functional outcome"],
         ["stage_12", "remains CLOSED; this task opens no orthogonality modelling"]])
    tsv(os.path.join(out, "tables/A23c_controls.tsv"),
        ["control_id", "type", "blocking", "expectation", "observed", "state", "detail"], ctrl)

    log = {"task_state": "PASS", "prerun_commit": a.prerun_commit,
           "sources_named": len(SOURCES), "fulltext_retrieved": n_ft, "not_found": n_nf,
           "candidate_passages": len(passages),
           "elapsed_s": round(time.time() - t0, 1), "blocking_failures": []}
    os.makedirs(os.path.join(out, "logs"), exist_ok=True)
    json.dump(log, open(os.path.join(out, "logs/run_log.json"), "w"), indent=2, sort_keys=True)
    print(json.dumps(log, indent=2, sort_keys=True))
    for c in ctrl:
        print(f"{c[5]:<7} {c[0]:<26} {c[4]}")
    print("TASK_STATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
