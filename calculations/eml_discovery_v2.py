#!/usr/bin/env python3
"""
EML-tree symbolic regression v2: CORRECT eml(x, y) = exp(x) - ln(y).

Fixes the +1 bug from v1. Enumerates by tree size (count of eml nodes)
and prunes by numerical bounds. Reports top-k per target.
"""

import math
from functools import lru_cache

ALPHA = 1.0 / 137.035999177
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PI = math.pi

LEAVES = {
    "1": 1.0,
    "alpha": ALPHA,
    "phi": PHI,
    "pi": PI,
    "e": math.e,
    "2": 2.0, "3": 3.0, "4": 4.0, "5": 5.0, "7": 7.0, "8": 8.0,
    "10": 10.0, "12": 12.0, "13": 13.0, "20": 20.0, "21": 21.0,
    "27": 27.0, "28": 28.0, "56": 56.0, "64": 64.0, "81": 81.0,
    "91": 91.0, "147": 147.0, "247": 247.0,
}

TARGETS = {
    "m_n_over_m_p":        1.00137841931,
    "V_cb":                0.0405,
    "V_ub":                0.00382,
    "Jarlskog":            3.08e-5,
    "sin2_theta_13":       0.0220,
    "sin2_theta_23":       0.546,
    "mass_sq_ratio":       0.0295,
    "delta_CP":            4.27,
}

# Numerical bounds: reject subtrees whose value cannot lead to useful output.
VAL_MIN = -50.0    # exp(-50) is negligible
VAL_MAX = 50.0     # exp(50) is enormous; anything beyond blows up


def eml(x, y):
    """Correct eml: exp(x) - ln(y). Requires y > 0; returns None otherwise."""
    if y <= 0:
        return None
    try:
        if x > VAL_MAX or x < VAL_MIN:
            return None
        return math.exp(x) - math.log(y)
    except (ValueError, OverflowError):
        return None


def build_trees_by_size(max_size):
    """
    Generate all eml-trees up to given size (internal node count).
    Size 0 = leaf. Size N = eml(size-a, size-b) with a+b+1 = N.
    Returns dict: size -> list of (expr_string, value).
    """
    trees = {0: [(name, val) for name, val in LEAVES.items()]}
    for size in range(1, max_size + 1):
        current = []
        for a in range(size):
            b = size - 1 - a
            for (expr_l, val_l) in trees[a]:
                if val_l is None:
                    continue
                if val_l < VAL_MIN or val_l > VAL_MAX:
                    continue
                for (expr_r, val_r) in trees[b]:
                    if val_r is None or val_r <= 0:
                        continue
                    v = eml(val_l, val_r)
                    if v is None:
                        continue
                    if not math.isfinite(v):
                        continue
                    expr = f"eml({expr_l}, {expr_r})"
                    current.append((expr, v))
        trees[size] = current
        print(f"  size {size}: {len(current):,} trees")
    return trees


def find_best(trees, target_value, top_k=10):
    """Scan all trees across all sizes for closest match to target."""
    hits = []
    for size, lst in trees.items():
        for expr, v in lst:
            if v == 0 and target_value != 0:
                continue
            rel_err = abs(v - target_value) / abs(target_value) if target_value != 0 else abs(v)
            hits.append((rel_err, size, expr, v))
    hits.sort(key=lambda t: (t[0], t[1]))
    return hits[:top_k]


def main():
    MAX_SIZE = 3  # internal nodes; corresponds to depth <= 3 with the usual depth metric
    print(f"Building eml-trees up to size {MAX_SIZE}...")
    trees = build_trees_by_size(MAX_SIZE)
    total = sum(len(v) for v in trees.values())
    print(f"Total trees enumerated: {total:,}\n")

    results_md = ["# EML Discovery v2 Results (CORRECTED eml = exp(x) - ln(y))\n"]
    results_md.append(f"Max tree size: {MAX_SIZE} internal nodes")
    results_md.append(f"Total trees enumerated: {total:,}")
    results_md.append(f"Leaf basis: {', '.join(LEAVES.keys())}\n")

    print(f"{'Target':<20} {'Measured':<15} {'Best Pred':<15} {'Rel Err':<12} {'Size':<5} {'Formula'}")
    print("-" * 130)

    for name, target in TARGETS.items():
        top = find_best(trees, target, top_k=5)
        if not top:
            print(f"{name:<20} {target:<15.6g} NO MATCH")
            continue
        err, size, expr, v = top[0]
        verdict = ""
        if err < 1e-3:
            verdict = "STRONG"
        elif err < 1e-2:
            verdict = "moderate"
        elif err < 1e-1:
            verdict = "weak"
        else:
            verdict = "no-signal"
        print(f"{name:<20} {target:<15.6g} {v:<15.6g} {err:<12.4%} {size:<5} {expr}  [{verdict}]")

        results_md.append(f"\n## {name}")
        results_md.append(f"Measured: {target}\n")
        results_md.append(f"Top 5 candidates:")
        results_md.append("")
        results_md.append("| Rank | Rel Err | Size | Value | Formula |")
        results_md.append("|------|---------|------|-------|---------|")
        for i, (err, size, expr, v) in enumerate(top, 1):
            results_md.append(f"| {i} | {err:.4%} | {size} | {v:.6g} | `{expr}` |")
        results_md.append(f"\nVerdict: **{verdict}** (best error {top[0][0]:.4%})")

    out = "/sessions/focused-dreamy-edison/mnt/Fractal_Reality/calculations/eml_discovery_v2_results.md"
    with open(out, "w") as f:
        f.write("\n".join(results_md))
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
