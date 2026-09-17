#!/usr/bin/env python3
"""C6 negative-control policy with MANDATORY, TYPED replicate-identity binding.

Scientific criterion UNCHANGED (control/C6_CONTROL_POLICY.md):
  * C6 is evaluated PER CONTROL CLASS. One class violating fails C6 even when the pooled
    statistic is clean - pooling 654 near-zero values hides a class whose own p95 is 10.
  * p95 is REPORTED, never a pass condition. Requiring per-class p95 == 0 would be
    unpassable: the reverse class reaches 10 on construction data where the mapper works.
  * Empty, missing or depleted classes fail closed.
  * Failed replicate generations are counted, their IDs LANDED, and never substituted.

Identity repair (final authorised bounded repair). Counting alone could not detect a replicate
that silently disappeared, because counts have no names attached. Independently demonstrated
holes in the count-only version, all of which returned PASS or crashed:

    set-valued or dict-valued ID collections   -> PASS  (list(set) / list(dict) looked fine)
    None / int / generator ID inputs           -> uncaught TypeError, not a controlled FAIL
    83 values + 1 failed id, no valid-id list  -> PASS  (disjointness unverifiable)

C6 now reconciles IDENTITIES, not just totals:

    set(valid_ids) | set(failed_ids) == set(attempted_ids)
    set(valid_ids) & set(failed_ids) == empty
    len(valid_ids) == n_valid,  len(failed_ids) == n_failed,  n_valid + n_failed == n_attempted

Identity lists are MANDATORY. There is no count-only mode.

TYPE CONTRACT: every replicate-ID collection must be exactly `list[str]` - `type(x) is list`
with every element `type(e) is str`, non-empty after stripping. Anything else is REJECTED with
a reason code, never coerced: set, dict, tuple, generator, iterator, None, int, float, str,
bytes, nested containers, non-string elements. A malformed container is a FAIL, not a crash.
"""
import math

CLASSES = ("MONO", "DI", "REV")
MIN_REPLICATE_FRACTION = 0.90
ABSOLUTE_MIN_REPLICATES = 20
REPLICATES_PER_SEQUENCE = 3


class _Missing:
    """Private sentinel. A required identity map that was never supplied at all."""
    def __repr__(self):
        return "<not supplied>"


_MISSING = _Missing()


def _safe_repr(obj):
    """repr() that cannot itself raise.

    An element whose __repr__ raises would otherwise escape as an uncaught exception from the
    very code path meant to reject it - a validator that crashes on hostile input is not a
    validator. (Found in review.)
    """
    try:
        r = repr(obj)
    except Exception as e:
        return f"<unreprable {type(obj).__name__}: {type(e).__name__}>"
    return r if len(r) <= 80 else r[:77] + "..."


def _safe_type_name(obj):
    try:
        return type(obj).__name__
    except Exception:
        return "<untypable>"


def pctl(vals, q):
    v = sorted(vals)
    return v[min(int(q * len(v)), len(v) - 1)] if v else None


def _finite_nonneg_ints(name, vals):
    bad = []
    for i, v in enumerate(vals):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            bad.append(f"{name}[{i}]={_safe_repr(v)} not numeric")
        elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            bad.append(f"{name}[{i}]={_safe_repr(v)} not finite")
        elif v < 0:
            bad.append(f"{name}[{i}]={_safe_repr(v)} negative")
        elif float(v) != int(v):
            bad.append(f"{name}[{i}]={_safe_repr(v)} not an integer count")
    return bad


def strict_id_list(name, value):
    """Validate an ID collection against the type contract. Returns (problems, ids).

    `type(value) is list` - not `isinstance` - so list subclasses and every other container
    are rejected rather than silently accepted. Nothing is coerced.
    """
    if value is _MISSING:
        return ([f"{name}: the whole identity map was not supplied; it is mandatory"], [])
    if value is None:
        return ([f"{name} is None; an explicit list[str] is required"], [])
    if type(value) is not list:
        return ([f"{name} must be exactly list[str], got {_safe_type_name(value)}"], [])
    problems, ids = [], []
    for i, e in enumerate(value):
        if type(e) is not str:
            problems.append(f"{name}[{i}]={_safe_repr(e)} is {_safe_type_name(e)}, "
                            f"not str")
            continue
        if not e.strip():
            problems.append(f"{name}[{i}] is blank")
            continue
        ids.append(e)
    if len(set(ids)) != len(ids):
        dupes = sorted({x for x in ids if ids.count(x) > 1})
        problems.append(f"{name} contains duplicate id(s): {dupes[:5]}")
    return (problems, ids)


def evaluate_c6(neg_by_class, real_mapped_non_abstaining, n_eligible,
                attempted_ids_by_class=_MISSING, valid_ids_by_class=_MISSING,
                failed_ids_by_class=_MISSING,
                replicates_per_sequence=REPLICATES_PER_SEQUENCE):
    """Return (verdict, reasons, report_rows). Any invalid state => FAIL with a reason code.

    The three identity arguments are REQUIRED. Confirmatory C6 has no count-only mode.
    """
    reasons, rows = [], []

    if (not isinstance(replicates_per_sequence, int)
            or isinstance(replicates_per_sequence, bool) or replicates_per_sequence <= 0):
        reasons.append(f"INVALID_DESIGN: replicates_per_sequence="
                       f"{replicates_per_sequence!r} must be a positive int")
        replicates_per_sequence = 1
    if not isinstance(n_eligible, int) or isinstance(n_eligible, bool) or n_eligible <= 0:
        reasons.append(f"INVALID_DENOMINATOR: n_eligible={n_eligible!r} must be a positive int")
        n_eligible_safe = 1
    else:
        n_eligible_safe = n_eligible

    for label, container in (("neg_by_class", neg_by_class),
                             ("attempted_ids_by_class", attempted_ids_by_class),
                             ("valid_ids_by_class", valid_ids_by_class),
                             ("failed_ids_by_class", failed_ids_by_class)):
        if container is _MISSING:
            reasons.append(f"IDENTITY_MAP_NOT_SUPPLIED: {label} is mandatory and was omitted "
                           f"entirely")
        elif type(container) is not dict:
            reasons.append(f"INVALID_CONTAINER: {label} must be a dict, got "
                           f"{_safe_type_name(container)}")

    for label, container in (("neg_by_class", neg_by_class),
                             ("attempted_ids_by_class", attempted_ids_by_class),
                             ("valid_ids_by_class", valid_ids_by_class),
                             ("failed_ids_by_class", failed_ids_by_class)):
        if type(container) is dict:
            for k in container:
                if k not in CLASSES:
                    reasons.append(f"UNDECLARED_CONTROL_CLASS:{k!r} in {label}")

    try:
        real = list(real_mapped_non_abstaining)
    except TypeError:
        reasons.append("INVALID_INPUT: real observation set is not iterable")
        real = []
    reasons += [f"INVALID_INPUT: {b}" for b in _finite_nonneg_ints("real", real)]
    if real and len(real) > n_eligible_safe:
        reasons.append(f"IMPOSSIBLE_REAL_CARDINALITY: {len(real)} real observations > "
                       f"n_eligible {n_eligible_safe}")
    if not real:
        reasons.append("NO_NON_ABSTAINING_REAL_SEQUENCES: C6 undefined -> FAIL CLOSED")

    expected = replicates_per_sequence * n_eligible_safe
    required = max(ABSOLUTE_MIN_REPLICATES, int(MIN_REPLICATE_FRACTION * expected + 0.5))
    invalid_so_far = bool(reasons)

    def _get(container, key):
        """Return the per-class list, or the sentinel when the whole map was omitted."""
        if container is _MISSING:
            return _MISSING
        return container.get(key) if type(container) is dict else None

    pooled = []
    for cls in CLASSES:
        vals_raw = _get(neg_by_class, cls)
        if vals_raw is None:
            reasons.append(f"MISSING_CONTROL_CLASS:{cls} -> FAIL CLOSED")
            vals = []
        else:
            try:
                vals = list(vals_raw)
            except TypeError:
                reasons.append(f"INVALID_INPUT:{cls} control values are not iterable")
                vals = []
            reasons += [f"INVALID_INPUT: {b}" for b in _finite_nonneg_ints(cls, vals)]

        # ---- MANDATORY typed identity lists ------------------------------------------
        a_problems, a_ids = strict_id_list(f"{cls}.attempted", _get(attempted_ids_by_class, cls))
        v_problems, v_ids = strict_id_list(f"{cls}.valid", _get(valid_ids_by_class, cls))
        f_problems, f_ids = strict_id_list(f"{cls}.failed", _get(failed_ids_by_class, cls))
        reasons += [f"INVALID_ATTEMPTED_IDS:{cls} {b}" for b in a_problems]
        reasons += [f"INVALID_VALID_IDS:{cls} {b}" for b in v_problems]
        reasons += [f"INVALID_FAILED_IDS:{cls} {b}" for b in f_problems]
        ids_ok = not (a_problems or v_problems or f_problems)

        n_failed = len(f_ids)
        nums_ok = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                      and math.isfinite(v) for v in vals)
        healthy = nums_ok and not invalid_so_far and vals_raw is not None

        rows.append(dict(control_class=cls, n_attempted=expected, n_valid=len(vals),
                         n_failed=n_failed,
                         max=max(vals) if (vals and healthy) else None,
                         mean=(sum(vals) / len(vals)) if (vals and healthy) else None,
                         p95=pctl(vals, 0.95) if healthy else None,
                         n_with_any_mapped=sum(1 for v in vals if healthy and v > 0)))
        pooled += vals if nums_ok else []

        if ids_ok:
            A, V, F = set(a_ids), set(v_ids), set(f_ids)
            overlap = sorted(V & F)
            if overlap:
                reasons.append(f"REPLICATE_IN_BOTH_SETS:{cls} {overlap[:5]}")
            unknown_v = sorted(V - A)
            unknown_f = sorted(F - A)
            if unknown_v:
                reasons.append(f"UNKNOWN_VALID_ID:{cls} not in attempted universe: "
                               f"{unknown_v[:5]}")
            if unknown_f:
                reasons.append(f"UNKNOWN_FAILED_ID:{cls} not in attempted universe: "
                               f"{unknown_f[:5]}")
            missing = sorted(A - (V | F))
            if missing:
                reasons.append(f"UNACCOUNTED_ATTEMPTED_ID:{cls} in neither valid nor failed: "
                               f"{missing[:5]} ({len(missing)} total)")
            if len(a_ids) != expected:
                reasons.append(f"ATTEMPTED_ID_COUNT_MISMATCH:{cls} {len(a_ids)} ids vs "
                               f"{expected} attempted by design")
            if len(v_ids) != len(vals):
                reasons.append(f"VALID_ID_COUNT_MISMATCH:{cls} {len(v_ids)} ids vs "
                               f"{len(vals)} values")
            if len(v_ids) + len(f_ids) != len(a_ids):
                reasons.append(f"IDENTITY_NOT_RECONCILED:{cls} valid {len(v_ids)} + failed "
                               f"{len(f_ids)} != attempted {len(a_ids)}")

        if vals_raw is None:
            continue
        if not vals:
            reasons.append(f"EMPTY_CONTROL_CLASS:{cls} (0 valid replicates) -> FAIL CLOSED")
            continue
        if len(vals) + n_failed != expected:
            reasons.append(f"ACCOUNTING_NOT_RECONCILED:{cls} valid {len(vals)} + failed "
                           f"{n_failed} != attempted {expected} "
                           f"({expected - len(vals) - n_failed:+d} unaccounted)")
        if len(vals) < required:
            reasons.append(f"INSUFFICIENT_REPLICATES:{cls} {len(vals)} < {required} "
                           f"(expected {expected}, {n_failed} generation failure(s))")
        if real and not invalid_so_far and nums_ok and max(vals) >= min(real):
            reasons.append(f"SEPARATION_VIOLATED:{cls} max {max(vals)} >= "
                           f"min real {min(real)}")

    pooled_ok = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                    and math.isfinite(v) for v in pooled) and not invalid_so_far
    rows.append(dict(control_class="POOLED", n_attempted=expected * len(CLASSES),
                     n_valid=len(pooled),
                     n_failed=sum(len(r["n_failed"]) if isinstance(r["n_failed"], list)
                                  else r["n_failed"] for r in rows[:len(CLASSES)]),
                     max=max(pooled) if (pooled and pooled_ok) else None,
                     mean=(sum(pooled) / len(pooled)) if (pooled and pooled_ok) else None,
                     p95=pctl(pooled, 0.95) if pooled_ok else None,
                     n_with_any_mapped=sum(1 for v in pooled if pooled_ok and v > 0)))

    return ("PASS" if not reasons else "FAIL"), reasons, rows


def write_control_report(path, rows, verdict, reasons, failed_ids_by_class=None,
                         intended_null=None):
    failed_ids_by_class = failed_ids_by_class or {}
    intended_null = intended_null or {}
    with open(path, "w") as f:
        f.write(f"# C6 verdict: {verdict}\n")
        for r in reasons:
            f.write(f"# reason: {r}\n")
        for cls in CLASSES:
            ids = sorted(failed_ids_by_class.get(cls, []))
            f.write(f"# {cls} intended null: {intended_null.get(cls, 'n/a')}\n")
            f.write(f"# {cls} generation failures ({len(ids)}), NOT replaced: "
                    f"{','.join(ids) if ids else 'none'}\n")
        f.write("# p95 is REPORTED, never a pass condition (C6_CONTROL_POLICY.md s3)\n")
        f.write("# C6 is PER CLASS: one class violating fails C6 even if pooled is clean\n")
        f.write("# identities reconciled: attempted == valid U failed, valid & failed empty\n")
        f.write("control_class\tn_attempted\tn_valid\tn_failed\tmax\tmean\tp95\t"
                "n_with_any_mapped\n")
        for r in rows:
            f.write(f"{r['control_class']}\t{r['n_attempted']}\t{r['n_valid']}\t"
                    f"{r['n_failed']}\t{r['max']}\t"
                    f"{'' if r['mean'] is None else format(r['mean'], '.3f')}\t"
                    f"{r['p95']}\t{r['n_with_any_mapped']}\n")
