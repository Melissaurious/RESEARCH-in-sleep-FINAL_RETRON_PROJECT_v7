#!/usr/bin/env python3
"""Canonical construction-family order — load-bearing, and NOT to be sorted.

A single shared RNG feeds negative-control generation, so the order in which families are
visited determines which di-shuffles fail. This was discovered empirically: visiting the
families in sorted order produced a DIFFERENT failed-replicate set (2 UG3 ids) from the
established one (2 CRISPR + 1 UG3). Both are legitimate draws; only one is the historical
population, and reproducing the landed controls requires the historical order.

This module is the single source of truth for that order. It is not derived, not sorted, and
not inferred from a dict's iteration order.
"""
import hashlib

# The order used by every previous bundle. DO NOT SORT.
CANONICAL_FAMILY_ORDER = ("Retrons", "GII", "DGRs", "CRISPR", "UG3", "AbiA")

# Seed for every RNG stream in the pipeline.
CANONICAL_SEED = 20260917


def order_hash(order=CANONICAL_FAMILY_ORDER, seed=CANONICAL_SEED):
    """Diagnostic hash over (seed, order). Any reorder changes it."""
    return hashlib.sha256(("|".join(order) + f"#{seed}").encode()).hexdigest()


CANONICAL_ORDER_HASH = order_hash()


def assert_canonical(order, seed=CANONICAL_SEED):
    """Fail closed if the order or seed drifts from the canonical pair."""
    got = order_hash(tuple(order), seed)
    if got != CANONICAL_ORDER_HASH:
        raise SystemExit(
            f"FAIL CLOSED: family order / seed is not canonical.\n"
            f"  expected {CANONICAL_FAMILY_ORDER} seed {CANONICAL_SEED} "
            f"-> {CANONICAL_ORDER_HASH[:16]}\n"
            f"  got      {tuple(order)} seed {seed} -> {got[:16]}\n"
            f"  A reorder changes which di-shuffles fail and therefore the landed controls.")
    return got


if __name__ == "__main__":
    print(f"order {CANONICAL_FAMILY_ORDER} seed {CANONICAL_SEED}")
    print(f"hash  {CANONICAL_ORDER_HASH}")
