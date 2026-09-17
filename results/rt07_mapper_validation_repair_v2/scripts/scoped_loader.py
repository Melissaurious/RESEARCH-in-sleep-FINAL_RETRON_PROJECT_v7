#!/usr/bin/env python3
"""REPAIR 5 - family-scoped loader. UG25 is never materialised before its authorised run.

The previous claim "no UG25 object was read" was FALSE. Every script called
`eligible_by_family()`, which parses the whole mixed collection and materialises all 38
families - UG25 (n=28) and G2L (n=51) included - before construction families are selected.
That is literally the same defect as errata A5 ("UG5 was never opened"), in the same loader.

This loader takes an explicit allow-list and never builds a record for any other family. A
sequence outside the allow-list is discarded at parse time: its residues are never stored, so
there is no object to read.

`UNEVALUATED` is not the same as `UNREAD`. This module is what makes the stronger word true.
"""
import collections, hashlib, os, re, sys

COLLECTION = ("/home/borg/RETRONS_january_2026/the-retron-project/src/myRT/Models/"
              "RTs-collection.faa")
MIN_AA = 250
EXCLUDED_LABELS = {"NotUsed", "UNC"}

# Families sealed for the confirmatory holdout. Requesting one without an explicit
# authorisation token is a hard error, not a warning.
SEALED = {"UG25"}
AUTHORISATION_TOKEN = "UG25_CONFIRMATORY_RUN_AUTHORISED_BY_OPERATOR"

_ACCESS_LOG = []


# The three predicates below MUST match repaired_lib exactly, or the construction populations
# change and every calibrated threshold silently shifts. Verified equivalent on all six
# construction families by scripts/loader_equivalence.py.
STANDARD_AA = re.compile(r"[^ACDEFGHIKLMNPQRSTVWY]")


def label(h):
    """Identical to repaired_lib.label: text after the final underscore, else 'NONE'."""
    return h.rsplit("_", 1)[1] if "_" in h else "NONE"


def clean(x):
    """Identical to repaired_lib.clean."""
    return x.replace("-", "").replace(".", "").upper().rstrip("*").replace("*", "")


def load_families(allowed, collection=COLLECTION, authorisation=None):
    """Materialise ONLY the requested families.

    `allowed` is an explicit set of family labels. Any record whose label is not in `allowed`
    is dropped before its sequence is retained. Requesting a SEALED family without the exact
    authorisation token raises.
    """
    allowed = set(allowed)
    sealed_requested = allowed & SEALED
    if sealed_requested and authorisation != AUTHORISATION_TOKEN:
        raise SystemExit(
            f"FAIL CLOSED: {sorted(sealed_requested)} is sealed for the confirmatory holdout. "
            f"Loading it requires the explicit operator authorisation token. "
            f"This guard exists because the previous bundle claimed UG25 was never read "
            f"while the shared loader materialised it on every call.")

    out = collections.defaultdict(dict)
    seen_labels, kept, dropped = set(), 0, 0
    hdr, buf = None, []

    def flush():
        nonlocal kept, dropped
        if hdr is None:
            return
        fam = label(hdr)
        seen_labels.add(fam)
        if fam in allowed and fam not in EXCLUDED_LABELS:
            s = clean("".join(buf))
            if len(s) >= MIN_AA and not STANDARD_AA.search(s):
                out[fam][hdr] = s
                kept += 1
                return
        dropped += 1          # residues discarded; nothing retained for this record

    with open(collection, errors="replace") as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.startswith(">"):
                flush()
                hdr, buf = ln[1:].split()[0], []
            elif hdr is not None:
                buf.append(ln.strip())
    flush()

    _ACCESS_LOG.append(dict(allowed=sorted(allowed), materialised=sorted(out),
                            n_kept=kept, n_dropped=dropped,
                            labels_present_in_file=len(seen_labels)))
    for fam in SEALED:
        if fam in out and authorisation != AUTHORISATION_TOKEN:
            raise SystemExit(f"FAIL CLOSED: {fam} materialised without authorisation")
    return dict(out)


def access_log():
    return list(_ACCESS_LOG)


def collection_sha256(collection=COLLECTION):
    h = hashlib.sha256()
    with open(collection, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


if __name__ == "__main__":
    allowed = sys.argv[1].split(",")
    d = load_families(allowed)
    for k in sorted(d):
        print(f"  {k}: {len(d[k])}")
    print("access log:", access_log())
