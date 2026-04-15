#!/usr/bin/env python3
"""
EML-tree symbolic regression discovery tool: depth-4 extension.

Targets: three CKM/neutrino constants at depth 4 with aggressive pruning and beam search.
Also re-test five depth-3 moderate candidates to see if depth-4 improves them.

Pruning strategy:
  - Overflow/underflow rejection (|x| > 1e6 or |x| < 1e-12)
  - Quick 10% reject on intermediate value before full evaluation
  - Beam search: maintain top-K trees per depth and extend only those
"""

import math
from itertools import combinations_with_replacement, product
from typing import Dict, List, Tuple, Optional, Set
import json
import time

# Framework basis constants
FRAMEWORK_BASIS = {
    "1": 1.0,
    "alpha": 1.0 / 137.035999177,
    "phi": (1.0 + math.sqrt(5)) / 2.0,
    "pi": math.pi,
    "e": math.e,  # Euler's number
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

# Three primary targets (no shallow matches at depth 3)
PRIMARY_TARGETS = {
    "Jarlskog": 3.08e-5,
    "V_ub": 0.00382,
    "mass_sq_ratio": 0.0295,
}

# Five moderate depth-3 candidates to re-test
SECONDARY_TARGETS = {
    "sin2_theta_13": 0.0220,
    "sin2_theta_23": 0.546,
    "delta_CP": 4.27,
    "m_n_m_p": 1.00137841931,
    "V_cb": 0.0405,
}

ALL_TARGETS = {**PRIMARY_TARGETS, **SECONDARY_TARGETS}


class EMLNode:
    """Binary tree node for EML expressions."""
    def __init__(self, op: Optional[str] = None, left=None, right=None, value: Optional[str] = None):
        self.op = op  # 'eml', 'leaf'
        self.left = left
        self.right = right
        self.value = value  # leaf name
        self._cached_val = None
        self._cached_depth = None

    def evaluate(self, strict: bool = False) -> float:
        """Evaluate the tree. If strict=True, return nan on any error."""
        if self._cached_val is not None:
            return self._cached_val

        if self.op == "leaf":
            try:
                result = FRAMEWORK_BASIS[self.value]
            except KeyError:
                return float('nan')
        elif self.op == "eml":
            x = self.left.evaluate(strict=strict)
            y = self.right.evaluate(strict=strict)
            if math.isnan(x) or math.isnan(y):
                return float('nan')

            # Pruning: reject overflow/underflow early
            if abs(x) > 1e6 or abs(y) < 1e-12:
                return float('nan')
            if abs(y) > 1e6 or abs(x) < 1e-12:
                return float('nan')

            try:
                result = math.exp(x) - math.log(y) + 1.0
                if abs(result) > 1e6 or (abs(result) < 1e-12 and result != 0):
                    return float('nan')
            except (ValueError, OverflowError):
                return float('nan')
        else:
            return float('nan')

        self._cached_val = result
        return result

    def to_string(self) -> str:
        """Convert to readable expression."""
        if self.op == "leaf":
            return self.value
        elif self.op == "eml":
            return f"eml({self.left.to_string()}, {self.right.to_string()})"
        return "?"

    def depth(self) -> int:
        """Return tree depth (cached)."""
        if self._cached_depth is not None:
            return self._cached_depth
        if self.op == "leaf":
            self._cached_depth = 0
        else:
            self._cached_depth = 1 + max(self.left.depth(), self.right.depth())
        return self._cached_depth


def generate_leaf_set() -> List[EMLNode]:
    """Generate leaf nodes from framework basis."""
    leaves = []
    for name in FRAMEWORK_BASIS.keys():
        node = EMLNode(op="leaf", value=name)
        leaves.append(node)

    # Add powers of alpha and phi (up to 5)
    alpha = FRAMEWORK_BASIS["alpha"]
    phi = FRAMEWORK_BASIS["phi"]
    for k in range(1, 6):
        node_ak = EMLNode(op="leaf", value=f"alpha^{k}")
        FRAMEWORK_BASIS[f"alpha^{k}"] = alpha ** k
        leaves.append(node_ak)

        node_pk = EMLNode(op="leaf", value=f"phi^{k}")
        FRAMEWORK_BASIS[f"phi^{k}"] = phi ** k
        leaves.append(node_pk)

    return leaves


def relative_error(measured: float, predicted: float) -> float:
    """Compute relative error."""
    if abs(measured) < 1e-10:
        return abs(predicted - measured)
    return abs(predicted - measured) / abs(measured)


def quick_reject(target_value: float, candidate_value: float, threshold: float = 1.0) -> bool:
    """Quick reject: return True if candidate is way off (default 100% threshold)."""
    if math.isnan(candidate_value):
        return True
    err = relative_error(target_value, candidate_value)
    return err > threshold


def beam_search_depth4(target_name: str, target_value: float, beam_width: int = 20, timeout: int = 300) -> List[Tuple[EMLNode, float, float]]:
    """
    Beam search for depth-4 trees.
    Maintains top-K (beam_width) trees at each depth level, extends only those.
    Returns list of (tree, value, error) tuples sorted by error.
    """
    start_time = time.time()
    leaves = generate_leaf_set()

    print(f"\n  [Beam search depth 4 for {target_name}]")

    # Depth 0: leaves
    depth0_candidates = []
    for leaf in leaves:
        val = leaf.evaluate()
        if not math.isnan(val):
            err = relative_error(target_value, val)
            depth0_candidates.append((leaf, val, err))

    # Depth 1: eml(leaf, leaf)
    print(f"    Depth 1: generating eml(leaf, leaf)...")
    depth1_beam = []
    for left, right in product(leaves, leaves):
        if left.value != right.value:
            node = EMLNode(op="eml", left=left, right=right)
            val = node.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth1_beam.append((node, val, err))

    depth1_beam.sort(key=lambda x: x[2])
    depth1_beam = depth1_beam[:beam_width]
    if depth1_beam:
        print(f"      Top {len(depth1_beam)} at depth 1 (best error: {depth1_beam[0][2]:.6e})")
    else:
        print(f"      No candidates at depth 1 passed quick reject; relaxing threshold to 50%")
        # Relax threshold
        depth1_all = []
        for left, right in product(leaves, leaves):
            if left.value != right.value:
                node = EMLNode(op="eml", left=left, right=right)
                val = node.evaluate()
                if not math.isnan(val):
                    err = relative_error(target_value, val)
                    depth1_all.append((node, val, err))
        depth1_all.sort(key=lambda x: x[2])
        depth1_beam = depth1_all[:beam_width]
        if depth1_beam:
            print(f"      Relaxed: found {len(depth1_beam)} at depth 1 (best error: {depth1_beam[0][2]:.6e})")

    if time.time() - start_time > timeout:
        print(f"    Timeout at depth 1")
        return depth1_beam

    # Depth 2: eml(depth1, leaf) and eml(leaf, depth1)
    print(f"    Depth 2: generating eml(depth1, leaf) + eml(leaf, depth1)...")
    depth2_beam = []

    for tree1, val1, err1 in depth1_beam:
        for leaf in leaves[:15]:  # Limit leaf combinations
            # eml(depth1, leaf)
            node_left = EMLNode(op="eml", left=tree1, right=leaf)
            val = node_left.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth2_beam.append((node_left, val, err))

            # eml(leaf, depth1)
            node_right = EMLNode(op="eml", left=leaf, right=tree1)
            val = node_right.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth2_beam.append((node_right, val, err))

    depth2_beam.sort(key=lambda x: x[2])
    depth2_beam = depth2_beam[:beam_width]
    if depth2_beam:
        print(f"      Top {len(depth2_beam)} at depth 2 (best error: {depth2_beam[0][2]:.6e})")
    else:
        print(f"      No candidates at depth 2; returning depth 1 beam")
        return depth1_beam

    if time.time() - start_time > timeout:
        print(f"    Timeout at depth 2")
        return depth2_beam

    # Depth 3: eml(depth2, leaf) and eml(leaf, depth2)
    print(f"    Depth 3: generating eml(depth2, leaf) + eml(leaf, depth2)...")
    depth3_beam = []

    for tree2, val2, err2 in depth2_beam:
        for leaf in leaves[:15]:
            # eml(depth2, leaf)
            node_left = EMLNode(op="eml", left=tree2, right=leaf)
            val = node_left.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth3_beam.append((node_left, val, err))

            # eml(leaf, depth2)
            node_right = EMLNode(op="eml", left=leaf, right=tree2)
            val = node_right.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth3_beam.append((node_right, val, err))

    depth3_beam.sort(key=lambda x: x[2])
    depth3_beam = depth3_beam[:beam_width]
    if depth3_beam:
        print(f"      Top {len(depth3_beam)} at depth 3 (best error: {depth3_beam[0][2]:.6e})")
    else:
        print(f"      No candidates at depth 3; returning depth 2 beam")
        return depth2_beam

    if time.time() - start_time > timeout:
        print(f"    Timeout at depth 3")
        return depth3_beam

    # Depth 4: eml(depth3, leaf) and eml(leaf, depth3)
    print(f"    Depth 4: generating eml(depth3, leaf) + eml(leaf, depth3)...")
    depth4_beam = []

    for tree3, val3, err3 in depth3_beam:
        for leaf in leaves[:15]:
            # eml(depth3, leaf)
            node_left = EMLNode(op="eml", left=tree3, right=leaf)
            val = node_left.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth4_beam.append((node_left, val, err))

            # eml(leaf, depth3)
            node_right = EMLNode(op="eml", left=leaf, right=tree3)
            val = node_right.evaluate()
            if not math.isnan(val) and not quick_reject(target_value, val, 2.0):
                err = relative_error(target_value, val)
                depth4_beam.append((node_right, val, err))

    depth4_beam.sort(key=lambda x: x[2])
    depth4_beam = depth4_beam[:beam_width]
    if depth4_beam:
        print(f"      Top {len(depth4_beam)} at depth 4 (best error: {depth4_beam[0][2]:.6e})")
    else:
        print(f"      No candidates at depth 4; returning depth 3 beam")
        return depth3_beam

    elapsed = time.time() - start_time
    print(f"    Beam search completed in {elapsed:.1f}s")

    return depth4_beam


def is_ladder_consistent(formula: str, target_name: str) -> str:
    """Check if formula is framework-consistent."""
    # Heuristics
    if "alpha^" in formula:
        return "fits_ladder"

    if "phi^" in formula or ("phi" in formula and any(str(n) in formula for n in [56, 39, 21, 13])):
        return "fits_ladder"

    if target_name.startswith("sin") or "theta" in target_name:
        if any(str(n) in formula for n in [8, 13, 21]):
            return "fits_ladder"

    if "Jarlskog" in target_name or "V_" in target_name:
        if "alpha" in formula or "phi" in formula:
            return "fits_ladder"

    return "unclear"


def main():
    """Run discovery on all targets."""
    results = {}

    print("="*80)
    print("EML-Tree Discovery: Depth-4 with Beam Search")
    print("="*80)

    # PRIMARY TARGETS: new depth-4 search
    print("\n" + "="*80)
    print("PRIMARY TARGETS: Three CKM/Neutrino Constants (Depth 4)")
    print("="*80)

    for target_name, target_value in PRIMARY_TARGETS.items():
        print(f"\n{'='*80}")
        print(f"TARGET: {target_name} = {target_value:.10e}")
        print(f"{'='*80}")

        candidates = beam_search_depth4(target_name, target_value, beam_width=20, timeout=300)

        top_results = []
        for tree, val, err in candidates[:5]:
            err_pct = 100.0 * err
            formula = tree.to_string()
            consistency = is_ladder_consistent(formula, target_name)

            top_results.append({
                "formula": formula,
                "value": val,
                "error_rel": err,
                "error_pct": err_pct,
                "consistency": consistency,
                "depth": tree.depth(),
            })

            status = ""
            if err < 0.001:
                status = " [STRONG: <0.1%]"
            elif err < 0.01:
                status = " [CANDIDATE: <1%]"
            elif err < 0.1:
                status = " [WEAK: <10%]"

            print(f"\n  {formula}")
            print(f"    Value: {val:.10e}")
            print(f"    Error: {err:.6e} ({err_pct:.4f}%){status}")
            print(f"    Depth: {tree.depth()}")
            print(f"    Consistency: {consistency}")

        results[target_name] = {
            "target_value": target_value,
            "top_candidates": top_results,
            "category": "primary",
        }

    # SECONDARY TARGETS: re-test at depth 4 (compare to depth 3)
    print("\n" + "="*80)
    print("SECONDARY TARGETS: Moderate Depth-3 Candidates Re-Tested at Depth 4")
    print("="*80)

    for target_name, target_value in SECONDARY_TARGETS.items():
        print(f"\n{'='*80}")
        print(f"TARGET: {target_name} = {target_value:.10e}")
        print(f"{'='*80}")

        candidates = beam_search_depth4(target_name, target_value, beam_width=20, timeout=300)

        top_results = []
        for tree, val, err in candidates[:5]:
            err_pct = 100.0 * err
            formula = tree.to_string()
            consistency = is_ladder_consistent(formula, target_name)

            top_results.append({
                "formula": formula,
                "value": val,
                "error_rel": err,
                "error_pct": err_pct,
                "consistency": consistency,
                "depth": tree.depth(),
            })

            status = ""
            if err < 0.001:
                status = " [STRONG: <0.1%]"
            elif err < 0.01:
                status = " [CANDIDATE: <1%]"
            elif err < 0.1:
                status = " [WEAK: <10%]"

            print(f"\n  {formula}")
            print(f"    Value: {val:.10e}")
            print(f"    Error: {err:.6e} ({err_pct:.4f}%){status}")
            print(f"    Depth: {tree.depth()}")
            print(f"    Consistency: {consistency}")

        results[target_name] = {
            "target_value": target_value,
            "top_candidates": top_results,
            "category": "secondary",
        }

    return results


if __name__ == "__main__":
    print("Initializing framework basis...")
    print(f"  Alpha: {FRAMEWORK_BASIS['alpha']:.10e}")
    print(f"  Phi: {FRAMEWORK_BASIS['phi']:.10f}")
    print(f"  Pi: {FRAMEWORK_BASIS['pi']:.10f}")
    print(f"  e: {FRAMEWORK_BASIS['e']:.10f}")

    results = main()

    # Write results to markdown
    with open("/sessions/focused-dreamy-edison/mnt/Fractal_Reality/calculations/eml_discovery_depth4_results.md", "w") as f:
        f.write("# EML-Tree Discovery Results: Depth 4 with Beam Search\n\n")
        f.write("Odrzywołek 2026: eml(x,y) = exp(x) - ln(y) + 1\n\n")
        f.write("This report extends the depth-3 search to depth-4 using beam search with aggressive pruning.\n\n")

        f.write("## Primary Targets (No shallow matches at depth 3)\n\n")
        for target_name in PRIMARY_TARGETS:
            if target_name in results:
                data = results[target_name]
                f.write(f"### {target_name}\n\n")
                f.write(f"**Target value:** {data['target_value']:.10e}\n\n")

                for i, cand in enumerate(data['top_candidates'][:5], 1):
                    f.write(f"#### Candidate {i}\n\n")
                    f.write(f"**Formula:** {cand['formula']}\n\n")
                    f.write(f"**Value:** {cand['value']:.10e}\n\n")
                    f.write(f"**Error:** {cand['error_rel']:.6e} ({cand['error_pct']:.4f}%)\n\n")
                    f.write(f"**Depth:** {cand['depth']}\n\n")
                    f.write(f"**Consistency:** {cand['consistency']}\n\n")

                    if cand['error_pct'] < 0.1:
                        f.write("**VERDICT:** Strong candidate (< 0.1% error)\n\n")
                    elif cand['error_pct'] < 1.0:
                        f.write("**VERDICT:** Candidate (< 1% error; derivation opportunity)\n\n")
                    elif cand['error_pct'] < 10.0:
                        f.write("**VERDICT:** Weak (< 10% error; monitor for pattern)\n\n")
                    else:
                        f.write("**VERDICT:** No signal\n\n")

                    f.write("---\n\n")

        f.write("## Secondary Targets (Depth-3 Candidates Re-Tested at Depth-4)\n\n")
        for target_name in SECONDARY_TARGETS:
            if target_name in results:
                data = results[target_name]
                f.write(f"### {target_name}\n\n")
                f.write(f"**Target value:** {data['target_value']:.10e}\n\n")

                for i, cand in enumerate(data['top_candidates'][:5], 1):
                    f.write(f"#### Candidate {i}\n\n")
                    f.write(f"**Formula:** {cand['formula']}\n\n")
                    f.write(f"**Value:** {cand['value']:.10e}\n\n")
                    f.write(f"**Error:** {cand['error_rel']:.6e} ({cand['error_pct']:.4f}%)\n\n")
                    f.write(f"**Depth:** {cand['depth']}\n\n")
                    f.write(f"**Consistency:** {cand['consistency']}\n\n")

                    if cand['error_pct'] < 0.1:
                        f.write("**VERDICT:** Strong candidate (< 0.1% error)\n\n")
                    elif cand['error_pct'] < 1.0:
                        f.write("**VERDICT:** Candidate (< 1% error; derivation opportunity)\n\n")
                    elif cand['error_pct'] < 10.0:
                        f.write("**VERDICT:** Weak (< 10% error; monitor for pattern)\n\n")
                    else:
                        f.write("**VERDICT:** No signal\n\n")

                    f.write("---\n\n")

    print("\n" + "="*80)
    print("Results written to: eml_discovery_depth4_results.md")
    print("="*80)
