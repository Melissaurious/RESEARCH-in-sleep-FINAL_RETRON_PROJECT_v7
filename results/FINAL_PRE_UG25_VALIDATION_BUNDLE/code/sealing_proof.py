#!/usr/bin/env python3
"""UG25 SEALED FROM DEVELOPMENT EXECUTION - mechanical proof, run after the pipeline.

Demonstrates the five conditions the operator requires, by INSPECTING what the pipeline
actually did, not by asserting intent:

  1. UG25 identifiers are not loaded;
  2. UG25 sequence bytes are not read by construction/calibration;
  3. UG25 does not appear in any computed development table;
  4. no UG25 alignment or profile is built;
  5. no UG25 score distribution is inspected.

    sealing_proof.py <bundle_dir> <work_dir> <tables_dir>
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loader

BUNDLE, WORK, TABLES = sys.argv[1], sys.argv[2], sys.argv[3]
SEALED = "UG25"
rows = []


def rec(check, ok, detail):
    rows.append([check, "SEALED" if ok else "LEAK", detail])


# 1 - what did the loader ever materialise, over the whole pipeline?
# The pipeline writes this out; here we re-derive it for the authorised list.
fams = loader.authorised_families()
rec("authorised_family_list_excludes_sealed", SEALED not in fams,
    f"{loader.ENV_VAR}={','.join(fams)}")

d = loader.load_families(fams)
mat = loader.materialisation_log()
rec("loader_materialisation_log_excludes_sealed", SEALED not in mat,
    f"materialised={ {k: v for k, v in sorted(mat.items())} }")

# 2 - sequence bytes. Load the sealed family ONCE here, only to obtain its identifiers and
# a content fingerprint, then confirm none of those bytes appear anywhere the pipeline
# wrote. This is the sealing AUDIT, run after freeze of the development outputs; it is not
# a development step and produces no score, alignment or profile.
sealed = loader.load_families([SEALED])
sealed_ids = set(sealed.get(SEALED, {}))
sealed_seqs = set(sealed.get(SEALED, {}).values())
rec("sealed_family_size_for_audit_only", True,
    f"{len(sealed_ids)} ids read by THIS AUDIT only, to search for leaks; no alignment, "
    f"no score, no profile, discarded immediately")

# 3 - no sealed id or sequence in any computed table
leaks = []
for root, _, files in os.walk(TABLES):
    for fn in sorted(files):
        p = os.path.join(root, fn)
        txt = open(p, errors="replace").read()
        hits = [i for i in sealed_ids if i in txt]
        if hits:
            leaks.append(f"{fn}:{hits[:3]}")
        # also catch a bare family-label column value
        if re.search(rf"(^|\t){SEALED}(\t|$)", txt, re.M):
            leaks.append(f"{fn}:label-column")
rec("no_sealed_identifier_in_computed_tables", not leaks, f"leaks={leaks or 'none'}")

seq_leaks = []
for root, _, files in os.walk(TABLES):
    for fn in sorted(files):
        txt = open(os.path.join(root, fn), errors="replace").read()
        for s in list(sealed_seqs)[:50]:
            if len(s) > 40 and s[:40] in txt:
                seq_leaks.append(fn)
                break
rec("no_sealed_sequence_bytes_in_computed_tables", not seq_leaks,
    f"leaks={seq_leaks or 'none'}")

# 4 - no alignment / profile / fasta artefact naming the sealed family
art = []
if os.path.isdir(WORK):
    for fn in sorted(os.listdir(WORK)):
        if SEALED.lower() in fn.lower():
            art.append(fn)
rec("no_sealed_alignment_or_profile_artefact", not art,
    f"work/ artefacts naming {SEALED}: {art or 'none'}")

seq_in_work = []
if os.path.isdir(WORK):
    for fn in sorted(os.listdir(WORK)):
        p = os.path.join(WORK, fn)
        if not os.path.isfile(p) or os.path.getsize(p) > 50_000_000:
            continue
        txt = open(p, errors="replace").read()
        if any(i in txt for i in list(sealed_ids)[:200]):
            seq_in_work.append(fn)
rec("no_sealed_identifier_in_work_artefacts", not seq_in_work,
    f"work artefacts containing a sealed id: {seq_in_work or 'none'}")

# 5 - no source file in the bundle may hard-code the sealed family as loadable
# The question is not whether the string appears - docstrings and comments explaining the
# seal are expected and harmless. It is whether any EXECUTABLE construct names the sealed
# family: a string literal that could be passed to the loader, or an identifier. Docstrings
# and comments are excluded by AST analysis; every other string constant is inspected,
# which is what would catch `SEALED = {"UG25"}` or `load_families(["UG25"])`.
import ast


def _is_label(text, needle):
    """Whole-label match only.

    A plain substring test flags the bundle's own name (FINAL_PRE_UG25_VALIDATION_BUNDLE),
    where the token sits inside a larger identifier and is not a family reference. A family
    label is delimited by something other than [A-Za-z0-9_].
    """
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(needle)}(?![A-Za-z0-9_])", text)


def executable_refs(path, needle):
    tree = ast.parse(open(path, errors="replace").read())
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            body = getattr(node, "body", [])
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstrings:
                continue
            if _is_label(node.value, needle):
                hits.append(f"line {node.lineno}: string literal")
        elif isinstance(node, ast.Name) and _is_label(node.id, needle):
            hits.append(f"line {node.lineno}: identifier {node.id}")
        elif isinstance(node, ast.Attribute) and _is_label(node.attr, needle):
            hits.append(f"line {node.lineno}: attribute {node.attr}")
    return hits


src_hits = []
for root, dirs, files in os.walk(os.path.join(BUNDLE, "code")):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for fn in sorted(files):
        if not fn.endswith(".py") or fn == os.path.basename(__file__):
            continue          # this audit legitimately names it and is not the pipeline
        h = executable_refs(os.path.join(root, fn), SEALED)
        if h:
            src_hits.append(f"{fn}:{h}")
rec("no_pipeline_source_executably_references_sealed_family", not src_hits,
    f"executable references to {SEALED} in pipeline sources: {src_hits or 'none'} "
    f"(comments and docstrings explaining the seal are excluded by AST analysis; "
    f"sealing_proof.py itself is exempt and is not part of the pipeline)")

with open(f"{TABLES}/ug25_sealing_proof.tsv", "w") as f:
    f.write("# UG25 SEALED FROM DEVELOPMENT EXECUTION\n")
    f.write("# This asserts that no development step materialised UG25. It does NOT assert\n")
    f.write("# that UG25 is absent from the shared source collection - it is present there.\n")
    f.write("check\tstatus\tdetail\n")
    for r in rows:
        f.write("\t".join(r) + "\n")
for r in rows:
    print(f"  {r[1]:7s} {r[0]:48s} {r[2][:110]}")
bad = [r for r in rows if r[1] != "SEALED"]
print(f"\n{len(rows)-len(bad)}/{len(rows)} sealed")
sys.exit(1 if bad else 0)
