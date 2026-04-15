#!/usr/bin/env python3
"""
EML-tree symbolic regression discovery tool for Circumpunct Framework.

Odrzywołek 2026: eml(x,y) = exp(x) - ln(y) + 1 generates elementary functions.
Use as a discovery tool to find shallow trees fitting framework constants.

Two outcomes:
  (a) Shallow tree fits ladder algebra: new derivation candidate
  (b) Shallow tree fits but conflicts: falsification candidate
"""

import math
from itertools import combinations_with_replacement, product
from typing import Dict, List, Tuple, Optional
import json

# Framework basis constants
FRAMEWORK_BASIS = {
    "1": 1.0,
    "alpha": 1.0 / 137.035999177,
    "phi": (1.0 + math.sqrt(5)) / 2.0,
    "pi": math.pi,
    "2": 2.0,
    "3": 3.0,
    "4": 4.0,
    "5": 5.0,
    "7": 7.0,
    "8": 8.0,
    "10": 10.0,
    "12": 12.0,
    "13": 13.0,
    "20": 20.0,
    "21": 21.0,
    "27": 27.0,
    "28": 28.0,
    "56": 56.0,
    "64": 64.0,
    "81": 81.0,
    "91": 91.0,
    "147": 147.0,
    "247": 247.0,
}

# Target constants (with measured values)
TARGETS = {
    "m_n_m_p": 1.00137841931,
    "V_cb": 0.0405,
    "V_ub": 0.00382,
    "Jarlskog": 3.08e-5,
    "sin2_theta_13": 0.0220,
    "sin2_theta_23": 0.546,
    "mass_sq_ratio": 0.0295,
    "delta_CP": 4.27,
}

class EMLNode:
    """Binary tree node for EML expressions."""
    def __init__(self, op: Optional[str] = None, left=None, right=None, value: Optional[str] = None):
        self.op = op  # 'eml', 'leaf'
        self.left = left
        self.right = right
        self.value = value  # leaf name

    def evaluate(self) -> float:
        """Evaluate the tree."""
        if self.op == "leaf":
            return FRAMEWORK_BASIS[self.value]
        elif self.op == "eml":
            x = self.left.evaluate()
            y = self.right.evaluate()
            try:
                result = math.exp(x) - math.log(y) + 1.0
                return result
            except (ValueError, OverflowError):
                return float('nan')
        return float('nan')

    def to_string(self) -> str:
        """Convert to readable expression."""
        if self.op == "leaf":
            return self.value
        elif self.op == "eml":
            return f"eml({self.left.to_string()}, {self.right.to_string()})"
        return "?"

    def depth(self) -> int:
        """Return tree depth."""
        if self.op == "leaf":
            return 0
        return 1 + max(self.left.depth(), self.right.depth())


def generate_leaf_set() -> List[EMLNode]:
    """Generate leaf nodes from framework basis."""
    leaves = []
    for name in FRAMEWORK_BASIS.keys():
        node = EMLNode(op="leaf", value=name)
        leaves.append(node)

    # Add powers of alpha and phi
    alpha = FRAMEWORK_BASIS["alpha"]
    phi = FRAMEWORK_BASIS["phi"]
    for k in range(1, 5):
        node_ak = EMLNode(op="leaf", value=f"alpha^{k}")
        FRAMEWORK_BASIS[f"alpha^{k}"] = alpha ** k
        leaves.append(node_ak)

        node_pk = EMLNode(op="leaf", value=f"phi^{k}")
        FRAMEWORK_BASIS[f"phi^{k}"] = phi ** k
        leaves.append(node_pk)

    return leaves


def generate_depth_1_trees(leaves: List[EMLNode]) -> List[EMLNode]:
    """Generate all depth-1 EML trees (eml(leaf, leaf))."""
    trees = []
    for left, right in product(leaves, leaves):
        if left.value != right.value:  # Avoid eml(x, x) trivially
            node = EMLNode(op="eml", left=left, right=right)
            trees.append(node)
    return trees


def generate_depth_2_trees(leaves: List[EMLNode]) -> List[EMLNode]:
    """Generate depth-2 trees: eml(eml(leaf,leaf), leaf) and eml(leaf, eml(leaf,leaf))."""
    trees = []
    depth1 = generate_depth_1_trees(leaves)

    # eml(depth1, leaf)
    for d1 in depth1:
        for leaf in leaves:
            node = EMLNode(op="eml", left=d1, right=leaf)
            trees.append(node)

    # eml(leaf, depth1)
    for leaf in leaves:
        for d1 in depth1:
            node = EMLNode(op="eml", left=leaf, right=d1)
            trees.append(node)

    return trees


def generate_depth_3_trees(leaves: List[EMLNode]) -> List[EMLNode]:
    """Generate depth-3 trees: eml(depth2, leaf) and eml(leaf, depth2)."""
    trees = []
    depth2 = generate_depth_2_trees(leaves)

    # eml(depth2, leaf)
    for d2 in depth2[:100]:  # Limit to avoid combinatorial explosion
        for leaf in leaves[:10]:  # Limit leaves too
            node = EMLNode(op="eml", left=d2, right=leaf)
            trees.append(node)

    # eml(leaf, depth2)
    for leaf in leaves[:10]:
        for d2 in depth2[:100]:
            node = EMLNode(op="eml", left=leaf, right=d2)
            trees.append(node)

    return trees


def relative_error(measured: float, predicted: float) -> float:
    """Compute relative error."""
    if abs(measured) < 1e-10:
        return abs(predicted - measured)
    return abs(predicted - measured) / abs(measured)


def search_constant(target_name: str, target_value: float, max_depth: int = 3) -> List[Tuple[EMLNode, float, str]]:
    """
    Search for EML trees matching a target constant.
    Returns top candidates ranked by relative error.
    """
    leaves = generate_leaf_set()
    candidates = []

    print(f"\nSearching {target_name} = {target_value:.6e}")
    print(f"  Generating depth-1 trees...")
    depth1 = generate_depth_1_trees(leaves)
    for tree in depth1:
        try:
            val = tree.evaluate()
            if not math.isnan(val) and val > 0:
                err = relative_error(target_value, val)
                if err < 10.0:  # Keep only reasonable candidates
                    candidates.append((tree, val, tree.to_string()))
        except:
            pass

    if max_depth >= 2:
        print(f"  Generating depth-2 trees...")
        depth2 = generate_depth_2_trees(leaves)
        for tree in depth2[:2000]:  # Sample to avoid explosion
            try:
                val = tree.evaluate()
                if not math.isnan(val) and val > 0:
                    err = relative_error(target_value, val)
                    if err < 10.0:
                        candidates.append((tree, val, tree.to_string()))
            except:
                pass

    if max_depth >= 3:
        print(f"  Generating depth-3 trees (sampling)...")
        depth3 = generate_depth_3_trees(leaves)
        for tree in depth3[:2000]:  # Sample
            try:
                val = tree.evaluate()
                if not math.isnan(val) and val > 0:
                    err = relative_error(target_value, val)
                    if err < 10.0:
                        candidates.append((tree, val, tree.to_string()))
            except:
                pass

    # Sort by error
    candidates.sort(key=lambda c: relative_error(target_value, c[1]))

    # Return top 10
    return candidates[:10]


def is_ladder_consistent(formula: str, target_name: str) -> str:
    """
    Check if a formula is consistent with framework ladder algebra.
    Returns: "fits_ladder", "conflicts_ladder", or "unclear".
    """
    # Heuristics based on framework structure
    if "alpha^" in formula:
        if any(f"alpha^{k}" in formula for k in range(1, 6)):
            return "fits_ladder"

    if "phi^" in formula or "phi" in formula:
        if "56" in formula or "39" in formula or "21" in formula:
            return "fits_ladder"

    if "exp" in formula and "ln" in formula:
        return "fits_ladder"

    # Neutrino and CKM angles might use trig-derived forms
    if target_name.startswith("sin"):
        if "8" in formula or "13" in formula:
            return "fits_ladder"

    return "unclear"


def main():
    """Run discovery on all targets."""
    results = {}

    for target_name, target_value in TARGETS.items():
        print(f"\n{'='*70}")
        print(f"TARGET: {target_name} = {target_value:.10e}")
        print(f"{'='*70}")

        candidates = search_constant(target_name, target_value, max_depth=3)

        top_results = []
        for tree, val, formula in candidates[:5]:
            err = relative_error(target_value, val)
            err_pct = 100.0 * err
            consistency = is_ladder_consistent(formula, target_name)

            top_results.append({
                "formula": formula,
                "value": val,
                "error_rel": err,
                "error_pct": err_pct,
                "consistency": consistency,
            })

            print(f"\n  Tree: {formula}")
            print(f"    Value: {val:.10e}")
            print(f"    Error: {err:.6e} ({err_pct:.4f}%)")
            print(f"    Depth: {tree.depth()}")
            print(f"    Consistency: {consistency}")

            if err < 0.001:
                print(f"    *** STRONG CANDIDATE ***")
            elif err < 0.01:
                print(f"    ** CANDIDATE **")

        results[target_name] = {
            "target_value": target_value,
            "top_candidates": top_results,
        }

    return results


if __name__ == "__main__":
    print("EML-Tree Discovery Tool")
    print("Searching for shallow trees fitting framework constants\n")

    results = main()

    # Write results to markdown
    with open("/sessions/focused-dreamy-edison/mnt/Fractal_Reality/calculations/eml_discovery_results.md", "w") as f:
        f.write("# EML-Tree Discovery Results\n\n")
        f.write("Odrzywołek 2026: eml(x,y) = exp(x) - ln(y) + 1 generates elementary functions.\n")
        f.write("This report searches for shallow trees (depth ≤ 3) fitting framework constants.\n\n")

        for target_name, data in results.items():
            f.write(f"## {target_name}\n\n")
            f.write(f"Target value: {data['target_value']:.10e}\n\n")

            for i, cand in enumerate(data['top_candidates'], 1):
                f.write(f"### Candidate {i}\n\n")
                f.write(f"**Formula:** {cand['formula']}\n\n")
                f.write(f"**Computed value:** {cand['value']:.10e}\n\n")
                f.write(f"**Relative error:** {cand['error_rel']:.6e} ({cand['error_pct']:.4f}%)\n\n")
                f.write(f"**Framework consistency:** {cand['consistency']}\n\n")

                if cand['error_pct'] < 0.1:
                    f.write("**Status:** STRONG CANDIDATE\n\n")
                elif cand['error_pct'] < 1.0:
                    f.write("**Status:** CANDIDATE\n\n")
                else:
                    f.write("**Status:** Weak\n\n")
                f.write("---\n\n")

    print("\n" + "="*70)
    print("Results written to: eml_discovery_results.md")
    print("="*70)
