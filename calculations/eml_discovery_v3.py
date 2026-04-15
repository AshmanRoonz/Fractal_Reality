#!/usr/bin/env python3
"""
EML-tree symbolic regression v3: tightened basis, size <= 2, with null test.

Basis: framework primitives only.
  {1, alpha, phi, pi, T=3, P=4, R=7, SU3=8, G=12, V=13}

Goal: verify whether V_cb survives a tight search that null targets do not.
"""

import math
import random

ALPHA = 1.0 / 137.035999177
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PI = math.pi

LEAVES = {
    "1":     1.0,
    "alpha": ALPHA,
    "phi":   PHI,
    "pi":    PI,
    "T":     3.0,
    "P":     4.0,
    "R":     7.0,
    "SU3":   8.0,
    "G":     12.0,
    "V":     13.0,
}

TARGETS = {
    "m_n_over_m_p":  1.00137841931,
    "V_cb":          0.0405,
    "V_ub":          0.00382,
    "Jarlskog":      3.08e-5,
    "sin2_theta_13": 0.0220,
    "sin2_theta_23": 0.546,
    "mass_sq_ratio": 0.0295,
    "delta_CP":      4.27,
}

VAL_MIN, VAL_MAX = -50.0, 50.0


def eml(x, y):
    if y <= 0:
        return None
    if x > VAL_MAX or x < VAL_MIN:
        return None
    try:
        return math.exp(x) - math.log(y)
    except (ValueError, OverflowError):
        return None


def build_trees(max_size):
    trees = {0: [(n, v) for n, v in LEAVES.items()]}
    for size in range(1, max_size + 1):
        current = []
        for a in range(size):
            b = size - 1 - a
            for (el, vl) in trees[a]:
                if vl is None or vl < VAL_MIN or vl > VAL_MAX:
                    continue
                for (er, vr) in trees[b]:
                    if vr is None or vr <= 0:
                        continue
                    v = eml(vl, vr)
                    if v is None or not math.isfinite(v):
                        continue
                    current.append((f"eml({el}, {er})", v))
        trees[size] = current
        print(f"  size {size}: {len(current):,} trees")
    return trees


def find_best(trees, target, k=10):
    hits = []
    for size, lst in trees.items():
        for expr, v in lst:
            if target == 0:
                err = abs(v)
            else:
                err = abs(v - target) / abs(target)
            hits.append((err, size, expr, v))
    hits.sort(key=lambda t: (t[0], t[1]))
    return hits[:k]


def main():
    print("Tightened basis:", list(LEAVES.keys()))
    print("Building eml-trees up to size 2...\n")
    trees = build_trees(2)
    total = sum(len(v) for v in trees.values())
    print(f"\nTotal trees: {total:,}\n")

    # real targets
    real = {}
    for name, t in TARGETS.items():
        top = find_best(trees, t, k=5)
        real[name] = top

    # null distribution
    random.seed(42)
    ranges = [
        ("near-unity",    0.9, 1.1),
        ("percent",       0.01, 0.1),
        ("sub-percent",   1e-3, 1e-2),
        ("ppm",           1e-6, 1e-4),
        ("small-sin2",    0.01, 0.06),
        ("mid-sin2",      0.4, 0.7),
        ("mass-ratio",    0.02, 0.05),
        ("phase",         3.0, 5.0),
    ]
    null_by_range = {}
    n = 40
    for label, lo, hi in ranges:
        errs = []
        for _ in range(n):
            if hi < 0.1:
                t = math.exp(random.uniform(math.log(lo), math.log(hi)))
            else:
                t = random.uniform(lo, hi)
            top = find_best(trees, t, k=1)
            if top:
                errs.append(top[0][0])
        errs.sort()
        null_by_range[label] = errs

    print("Null-target distribution by range (40 draws each):")
    print(f"{'range':<15} {'min':<10} {'p10':<10} {'median':<10} {'p90':<10}")
    for label, errs in null_by_range.items():
        print(f"{label:<15} {errs[0]:<10.4%} {errs[max(0, n//10)]:<10.4%} {errs[n//2]:<10.4%} {errs[9*n//10]:<10.4%}")

    print("\nReal targets vs matched-range null:")
    print(f"{'target':<18} {'real err':<12} {'size':<5} {'formula':<35} {'null p10':<12} {'verdict'}")
    print("-" * 110)

    target_range = {
        "m_n_over_m_p":  "near-unity",
        "V_cb":          "percent",
        "V_ub":          "sub-percent",
        "Jarlskog":      "ppm",
        "sin2_theta_13": "small-sin2",
        "sin2_theta_23": "mid-sin2",
        "mass_sq_ratio": "mass-ratio",
        "delta_CP":      "phase",
    }

    for name, top in real.items():
        err, size, expr, v = top[0]
        rng = target_range[name]
        null_p10 = null_by_range[rng][max(0, n // 10)]
        null_min = null_by_range[rng][0]
        if err < null_min / 3:
            verdict = "CLEAR SIGNAL"
        elif err < null_p10 / 3:
            verdict = "signal"
        elif err < null_p10:
            verdict = "marginal"
        else:
            verdict = "noise"
        print(f"{name:<18} {err:<12.4%} {size:<5} {expr:<35} {null_p10:<12.4%} {verdict}")

    # write markdown
    out = "/sessions/focused-dreamy-edison/mnt/Fractal_Reality/calculations/eml_discovery_v3_results.md"
    with open(out, "w") as f:
        f.write("# EML Discovery v3: tight basis, size <= 2, with null test\n\n")
        f.write(f"Basis: {{{', '.join(LEAVES.keys())}}}  (10 leaves; framework primitives only)\n\n")
        f.write(f"Total trees: {total:,}\n\n")
        f.write("## Null distribution by range (40 random draws each)\n\n")
        f.write("| range | min | p10 | median | p90 |\n|---|---|---|---|---|\n")
        for label, errs in null_by_range.items():
            f.write(f"| {label} | {errs[0]:.4%} | {errs[max(0,n//10)]:.4%} | {errs[n//2]:.4%} | {errs[9*n//10]:.4%} |\n")
        f.write("\n## Real targets\n\n")
        f.write("| target | measured | best pred | rel err | size | formula | null p10 | verdict |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for name, top in real.items():
            err, size, expr, v = top[0]
            rng = target_range[name]
            null_p10 = null_by_range[rng][max(0, n // 10)]
            null_min = null_by_range[rng][0]
            if err < null_min / 3:
                verdict = "**CLEAR SIGNAL**"
            elif err < null_p10 / 3:
                verdict = "signal"
            elif err < null_p10:
                verdict = "marginal"
            else:
                verdict = "noise"
            f.write(f"| {name} | {TARGETS[name]:.6g} | {v:.6g} | {err:.4%} | {size} | `{expr}` | {null_p10:.4%} | {verdict} |\n")
        f.write("\n## Top-5 per target\n")
        for name, top in real.items():
            f.write(f"\n### {name} (measured {TARGETS[name]:.6g})\n\n")
            f.write("| rank | rel err | size | value | formula |\n|---|---|---|---|---|\n")
            for i, (err, size, expr, v) in enumerate(top, 1):
                f.write(f"| {i} | {err:.4%} | {size} | {v:.6g} | `{expr}` |\n")
    print(f"\nResults written to {out}")


if __name__ == "__main__":
    main()
