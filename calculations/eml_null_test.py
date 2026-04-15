#!/usr/bin/env python3
"""
Null-test for eml-tree symbolic regression.

Question: are the sub-0.1% fits on physics constants meaningful, or does the
size-3 eml-tree space over this basis fit ANY target in the same range just
as well?

Method: draw 200 random targets uniformly from the same order-of-magnitude
ranges as the real physics targets; run the same search; compare best-fit
error distributions.
"""

import math
import random
import sys
sys.path.insert(0, "/sessions/focused-dreamy-edison/mnt/Fractal_Reality/calculations")
from eml_discovery_v2 import build_trees_by_size, find_best, TARGETS


def main():
    random.seed(42)
    print("Building trees (size <= 3)...")
    trees = build_trees_by_size(3)
    print()

    # real targets: record best-fit errors
    real_errs = {}
    for name, t in TARGETS.items():
        top = find_best(trees, t, top_k=1)
        real_errs[name] = top[0][0] if top else float('inf')

    # null targets: same order-of-magnitude ranges
    ranges = [
        (0.9, 1.1),       # near-unity (like m_n/m_p)
        (0.01, 0.1),      # ~1% (CKM-ish)
        (1e-3, 1e-2),     # ~0.1%
        (1e-5, 1e-4),     # Jarlskog-ish
        (0.01, 0.06),     # sin^2 theta small angles
        (0.4, 0.7),       # sin^2 theta_23
        (0.02, 0.05),     # mass-sq ratio
        (3.0, 5.0),       # phase-like
    ]

    null_errs = []
    n_per_range = 25
    for lo, hi in ranges:
        for _ in range(n_per_range):
            # uniform in log-space for small values, linear for order-unity
            if hi < 0.1:
                t = math.exp(random.uniform(math.log(lo), math.log(hi)))
            else:
                t = random.uniform(lo, hi)
            top = find_best(trees, t, top_k=1)
            if top:
                null_errs.append((t, top[0][0]))

    # summary
    print(f"{'Target':<22} {'Real err':<15} {'Null median':<15} {'Null p10':<15} {'Signal?'}")
    print("-" * 90)

    # group nulls by which range they fall in, compare to each real
    # (simpler: just report overall null distribution)
    null_vals = sorted(e for _, e in null_errs)
    null_median = null_vals[len(null_vals) // 2]
    null_p10 = null_vals[len(null_vals) // 10]
    null_p01 = null_vals[max(1, len(null_vals) // 100)]

    print(f"\nNull distribution ({len(null_errs)} random targets):")
    print(f"  10th percentile best-err: {null_p10:.4%}")
    print(f"  50th percentile best-err: {null_median:.4%}")
    print(f"  1st percentile best-err:  {null_p01:.4%}")
    print()

    for name, t in TARGETS.items():
        re = real_errs[name]
        # find the nulls in the same order-of-magnitude range
        same_mag_nulls = [e for (tv, e) in null_errs
                          if 0.3 < tv / t < 3.0 or 0.3 < t / tv < 3.0]
        if same_mag_nulls:
            same_mag_nulls.sort()
            nm = same_mag_nulls[len(same_mag_nulls) // 2]
            np10 = same_mag_nulls[max(0, len(same_mag_nulls) // 10)]
        else:
            nm = null_median
            np10 = null_p10
        signal = "REAL" if re < np10 / 3 else ("marginal" if re < nm / 3 else "NULL (noise)")
        print(f"{name:<22} {re:<15.4%} {nm:<15.4%} {np10:<15.4%} {signal}")


if __name__ == "__main__":
    main()
