#!/usr/bin/env python3
"""Family-scoped loader. The allowed-family list comes from RUNTIME, never from source.

History this closes:
  * `eligible_by_family()` parsed the whole mixed collection and materialised all 38
    families, so "UG5 was never opened" (errata A5) and later "UG25 was never read" were
    both literally false.
  * The v2 repair added a SEALED set plus an AUTHORISATION_TOKEN - but the token was a
    public constant in this very file, and the routine test `loader_equivalence.py` used it
    on every run, materialising UG25 and landing its count in an output table. A seal whose
    key is printed next to the lock is an accident guard, not authorisation.

Design now:
  * There is NO sealed-family list and NO token in this module. The module has no knowledge
    of UG25 whatsoever.
  * `load_families(allowed)` materialises exactly the labels it is given. Anything else is
    discarded at parse time - the residues are never retained, so there is no object to read.
  * The caller obtains `allowed` from `authorised_families()`, which reads an EXTERNAL
    runtime input (env var or file). A source-tree edit alone cannot widen the scope; the
    operator's runtime authorisation must change.

Precise claim this supports:
    UG25 SEALED FROM DEVELOPMENT EXECUTION
not:
    UG25 never existed in the source collection.
The sequences exist in the shared collection file. What is guaranteed is that no
development execution materialises them.
"""
import collections, hashlib, os, re, sys

COLLECTION = ("/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/"
              "RTs-collection.faa")
MIN_AA = 250
EXCLUDED_LABELS = {"NotUsed", "UNC"}
STANDARD_AA = re.compile(r"[^ACDEFGHIKLMNPQRSTVWY]")

ENV_VAR = "RT07_AUTHORISED_FAMILIES"

# Every label this process ever materialised. Written to the sealing-proof table.
_MATERIALISED = collections.Counter()
_REQUESTS = []


def label(h):
    """Text after the final underscore, else 'NONE'. Matches the historical predicate."""
    return h.rsplit("_", 1)[1] if "_" in h else "NONE"


def clean(x):
    return x.replace("-", "").replace(".", "").upper().rstrip("*").replace("*", "")


def authorised_families():
    """Read the authorised development families from the RUNTIME environment.

    Absent or empty -> hard error. There is no default list, precisely so that a scope can
    never be silently inherited from source.
    """
    raw = os.environ.get(ENV_VAR, "").strip()
    if not raw:
        raise SystemExit(
            f"FAIL CLOSED: {ENV_VAR} is not set. The authorised development family list is a "
            f"runtime input, not a source constant. Set it explicitly, e.g.\n"
            f"  export {ENV_VAR}=Retrons,GII,DGRs,CRISPR,UG3,AbiA")
    fams = [f.strip() for f in raw.split(",") if f.strip()]
    if not fams:
        raise SystemExit(f"FAIL CLOSED: {ENV_VAR} parsed to an empty family list")
    return fams


def load_families(allowed, collection=COLLECTION):
    """Materialise ONLY the requested labels; discard every other record at parse time."""
    allowed = set(allowed)
    _REQUESTS.append(sorted(allowed))
    out = collections.defaultdict(dict)
    hdr, buf = None, []
    kept = dropped = 0

    def flush():
        nonlocal kept, dropped
        if hdr is None:
            return
        fam = label(hdr)
        if fam in allowed and fam not in EXCLUDED_LABELS:
            s = clean("".join(buf))
            if len(s) >= MIN_AA and not STANDARD_AA.search(s):
                out[fam][hdr] = s
                _MATERIALISED[fam] += 1
                kept += 1
                return
        dropped += 1

    with open(collection, errors="replace") as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.startswith(">"):
                flush()
                hdr, buf = ln[1:].split()[0], []
            elif hdr is not None:
                buf.append(ln.strip())
    flush()
    return dict(out)


def materialisation_log():
    """{family: n_sequences_materialised} over the life of this process."""
    return dict(_MATERIALISED)


def request_log():
    return [list(r) for r in _REQUESTS]


def collection_sha256(collection=COLLECTION):
    h = hashlib.sha256()
    with open(collection, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


if __name__ == "__main__":
    fams = authorised_families()
    d = load_families(fams)
    for k in sorted(d):
        print(f"  {k}: {len(d[k])}")
    print("materialised:", materialisation_log())
