#!/usr/bin/env python3
"""g1lib - the one record classifier for dbchar_g1_corpus_identity.

Shared by the census (s02) and the positive-control fixture (s04), so the controls
exercise exactly the code that produced the numbers. The independent second count
(s03) deliberately does NOT import this module.

Everything that decides a count is a named constant declared here before any data is
read (PLAN.md). Nothing in this module filters a record: every check is a flag.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# --- DECLARED before any data is read ------------------------------------------------
FILE_PREFIX = "master_"
RT_FILE_SUFFIX = "_merged_oriented.jsonl"
NCRNA_FILE = "master_ncRNA-anchored_merged.jsonl"
MULTI_FILE = "master_MULTI_merged_oriented.jsonl"
NCRNA_LABEL = "ncRNA-anchored"
ANCHOR_VALUES = ("RT", "ncRNA")
# The schema's own documented taxonomy_system values (input_format_schema_only.md, "Notes
# for ARIS"). Observed values outside this set are a schema discrepancy, not an error.
DOC_TAXONOMY_SYSTEMS = ("gtdb", "mmseqs2_inferred")
PARSE_CLASSES = ("ok", "blank", "bad_utf8", "bad_json", "not_object")

CHECKS = {
    "V01": "rt_system_id missing, non-string or empty",
    "V02": "anchor_type not in {RT, ncRNA}",
    "V03": "anchor_type inconsistent with the file's role (RT-family/MULTI file => RT; ncRNA file => ncRNA)",
    "V04": "source_database missing, non-string or empty",
    "V05": "system_types missing, not a list, or empty",
    "V06": "file label not among system_types tokens (family token; MULTI >=2 tokens; ncRNA-anchored)",
    "V07": "anchor_type RT without a dict rt_gene carrying a non-empty sequence",
    "V08": "anchor_type ncRNA with a non-null rt_gene",
    "V09a": "anchor_type RT with zero cds_annotations[] flagged is_rt_gene",
    "V09b": "anchor_type RT with more than one cds_annotations[] flagged is_rt_gene",
    "V10": "anchor_type ncRNA with any cds_annotations[] flagged is_rt_gene",
    "V11": "anchor_type ncRNA with an empty ncrnas[] array",
    "V12": "metadata.total_ncrnas != len(ncrnas)",
    "V13": "metadata.total_genes != len(cds_annotations)",
    "V14": "metadata.total_intergenic_regions != len(intergenic_regions)",
    "V15": "genomic_context.length != len(genomic_context.full_sequence)",
    "V16": "genomic_context.actual_window.start > actual_window.end",
    "V17": "some intergenic_regions[].has_ncrna is true while ncrnas[] is empty",
    "V18": "genome_id missing, non-string or empty",
    "V19": "contig missing, non-string or empty",
    "V20a": "taxonomy missing/not an object, or taxonomy.taxonomy_system missing",
    "V20b": "taxonomy.taxonomy_system present but outside the schema-documented set",
    "V21a": "record lacks at least one schema-documented top-level key",
    "V21b": "record carries at least one top-level key the schema does not document",
}

_DOC_LINE = re.compile(r"^- `([A-Za-z_][A-Za-z0-9_.\[\]]*)` ")


def documented_paths(schema_md: Path) -> set[str]:
    """Field paths the schema documents, in walk_paths spelling.

    The field list names leaves (`genomic_context.length`) and sometimes an array itself
    (`ncrnas[].overlapping_cds[]`). A documented leaf documents every container above it,
    so each prefix is added; a trailing `[]` names the array key itself.
    """
    out: set[str] = set()
    for line in schema_md.read_text(encoding="utf-8").splitlines():
        m = _DOC_LINE.match(line)
        if not m:
            continue
        p = m.group(1)
        p = p[:-2] if p.endswith("[]") else p
        parts = p.split(".")
        for i in range(1, len(parts) + 1):
            q = ".".join(parts[:i])
            out.add(q[:-2] if q.endswith("[]") else q)
    return out


def documented_top_level(paths: set[str]) -> set[str]:
    return {p.split(".")[0].replace("[]", "") for p in paths}


def file_role(name: str) -> tuple[str, str]:
    """(role, label) from the filename. role in {family, multi, ncrna, unknown}."""
    if name == NCRNA_FILE:
        return "ncrna", NCRNA_LABEL
    if name == MULTI_FILE:
        return "multi", "MULTI"
    if name.startswith(FILE_PREFIX) and name.endswith(RT_FILE_SUFFIX):
        return "family", name[len(FILE_PREFIX):-len(RT_FILE_SUFFIX)]
    return "unknown", name


def _nonempty_str(v: object) -> bool:
    return isinstance(v, str) and v != ""


def type_tokens(st: object) -> tuple[str, str, int, bool]:
    """system_types -> (raw JSON spelling, order-normalised token set, n tokens, multilabel).

    Multi-label = more than one list element OR any element containing '/'. The
    normalised set sits BESIDE the raw spelling; it never replaces it.
    """
    raw = json.dumps(st, separators=(",", ":"), ensure_ascii=False)
    if not isinstance(st, list):
        return raw, "", 0, False
    elems = [e if isinstance(e, str) else json.dumps(e) for e in st]
    toks = sorted({t for e in elems for t in e.split("/") if t})
    multi = len(elems) > 1 or any("/" in e for e in elems)
    return raw, "/".join(toks), len(toks), multi


def value_label(rec: dict, key: str) -> str:
    """A top-level scalar as a label that keeps absent, null and non-string distinct."""
    if key not in rec:
        return "<absent>"
    v = rec[key]
    if v is None:
        return "<null>"
    return v if isinstance(v, str) else f"<{type(v).__name__}:{v}>"


def anchor_class(rec: dict) -> str:
    return value_label(rec, "anchor_type")


def parse_line(line: bytes) -> tuple[str, object]:
    """One raw line (no trailing newline) -> (parse class, object or None). Strict decode."""
    if not line.strip():
        return "blank", None
    try:
        text = line.decode("utf-8")
    except UnicodeDecodeError:
        return "bad_utf8", None
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return "bad_json", None
    if not isinstance(obj, dict):
        return "not_object", None
    return "ok", obj


def validate(rec: dict, fname: str, doc_top: set[str]) -> list[str]:
    """Every declared check that fires on this record. Flags only; nothing is dropped."""
    role, label = file_role(fname)
    fired: list[str] = []
    anchor = rec.get("anchor_type")
    if not _nonempty_str(rec.get("rt_system_id")):
        fired.append("V01")
    if anchor not in ANCHOR_VALUES:
        fired.append("V02")
    if (role in ("family", "multi") and anchor != "RT") or (role == "ncrna" and anchor != "ncRNA"):
        fired.append("V03")
    if not _nonempty_str(rec.get("source_database")):
        fired.append("V04")
    st = rec.get("system_types")
    if not isinstance(st, list) or not st:
        fired.append("V05")
    _, norm, ntok, _ = type_tokens(st)
    toks = set(norm.split("/")) if norm else set()
    if (role == "family" and label not in toks) or (role == "multi" and ntok < 2) \
            or (role == "ncrna" and NCRNA_LABEL not in toks):
        fired.append("V06")
    rt = rec.get("rt_gene")
    cds = rec.get("cds_annotations")
    cds = cds if isinstance(cds, list) else []
    n_rt_cds = sum(1 for c in cds if isinstance(c, dict) and c.get("is_rt_gene") is True)
    ncr = rec.get("ncrnas")
    ncr = ncr if isinstance(ncr, list) else []
    igr = rec.get("intergenic_regions")
    igr = igr if isinstance(igr, list) else []
    if anchor == "RT":
        if not (isinstance(rt, dict) and _nonempty_str(rt.get("sequence"))):
            fired.append("V07")
        if n_rt_cds == 0:
            fired.append("V09a")
        elif n_rt_cds > 1:
            fired.append("V09b")
    if anchor == "ncRNA":
        if rt is not None:
            fired.append("V08")
        if n_rt_cds > 0:
            fired.append("V10")
        if not ncr:
            fired.append("V11")
    md = rec.get("metadata") if isinstance(rec.get("metadata"), dict) else {}
    if md.get("total_ncrnas") != len(ncr):
        fired.append("V12")
    if md.get("total_genes") != len(cds):
        fired.append("V13")
    if md.get("total_intergenic_regions") != len(igr):
        fired.append("V14")
    gc = rec.get("genomic_context") if isinstance(rec.get("genomic_context"), dict) else {}
    fs = gc.get("full_sequence")
    if gc.get("length") != (len(fs) if isinstance(fs, str) else None):
        fired.append("V15")
    aw = gc.get("actual_window") if isinstance(gc.get("actual_window"), dict) else {}
    s, e = aw.get("start"), aw.get("end")
    if isinstance(s, int) and isinstance(e, int) and s > e:
        fired.append("V16")
    if not ncr and any(isinstance(r, dict) and r.get("has_ncrna") is True for r in igr):
        fired.append("V17")
    if not _nonempty_str(rec.get("genome_id")):
        fired.append("V18")
    if not _nonempty_str(rec.get("contig")):
        fired.append("V19")
    tax = rec.get("taxonomy")
    if not isinstance(tax, dict) or "taxonomy_system" not in tax:
        fired.append("V20a")
    elif tax.get("taxonomy_system") not in DOC_TAXONOMY_SYSTEMS:
        fired.append("V20b")
    keys = set(rec.keys())
    if doc_top - keys:
        fired.append("V21a")
    if keys - doc_top:
        fired.append("V21b")
    return fired


def _tname(v: object) -> str:
    return "null" if v is None else type(v).__name__


def walk_paths(obj: dict, prefix: str, acc: dict) -> None:
    """Accumulate, per key path: [occurrences, null occurrences, {type: n}].

    Arrays of objects descend as `path[]`; scalars inside arrays are typed, not walked.
    """
    for k, v in obj.items():
        p = prefix + k
        slot = acc.get(p)
        if slot is None:
            slot = acc[p] = [0, 0, {}]
        slot[0] += 1
        t = _tname(v)
        if v is None:
            slot[1] += 1
        slot[2][t] = slot[2].get(t, 0) + 1
        if isinstance(v, dict):
            walk_paths(v, p + ".", acc)
        elif isinstance(v, list):
            for el in v:
                if isinstance(el, dict):
                    walk_paths(el, p + "[].", acc)


def record_sha256(line: bytes) -> str:
    return hashlib.sha256(line).hexdigest()


def write_tsv(path: Path, header: list[str], rows) -> None:
    with path.open("w", encoding="utf-8") as fh:
        fh.write("\t".join(header) + "\n")
        for r in rows:
            fh.write("\t".join("" if v is None else str(v) for v in r) + "\n")
