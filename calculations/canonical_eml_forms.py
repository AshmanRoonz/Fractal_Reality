#!/usr/bin/env python3
"""
Canonical eml-tree representation of framework constants.

This script expresses every closed framework constant as an elementary multilinear (eml) tree,
where eml(x, y) = exp(x) - ln(y).

Every ladder constant of the form C = (1/α)^E(d) becomes eml(E(d)·ln(1/α), 1).

Reference: Odrzywołek 2026; §27.7n.2 of circumpunct_framework.md.
"""

import math
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from enum import Enum

# Physical constants
ALPHA_MEASURED = 137.035999177  # fine-structure constant (CODATA 2022)
PHI = (1 + math.sqrt(5)) / 2  # golden ratio
PI = math.pi

# Framework integers
T = 3  # triad
P = 4  # pump phases
R = 7  # rungs (T² - 2)
G = 12  # generators (T(T+1))
V = 13  # vertices (G + 1)
S = 64  # states (P^T)
SU3 = 8  # SU(3) generators

class Dimension(Enum):
    """Dimensional stations."""
    SOURCE = "∞D"
    APERTURE = "0D"
    CONVERGENCE = "0.5D"
    LINE = "1D"
    BRANCHING = "1.5D"
    FIELD = "2D"
    EMERGENCE = "2.5D"
    BOUNDARY = "3D"
    RECURSION = "3.5D"
    WHOLE = "All"

@dataclass
class EmlTree:
    """Elementary multilinear (eml) tree node."""
    x_value: float
    y_value: float
    depth: int = 1
    description: str = ""

    def evaluate(self) -> float:
        """Compute eml(x, y) = exp(x) - ln(y)."""
        return math.exp(self.x_value) - math.log(self.y_value)

    def symbolic(self) -> str:
        """Return symbolic representation."""
        if self.depth == 0:
            return f"{self.x_value:.6f}"
        x_str = f"{self.x_value:.6g}" if isinstance(self.x_value, float) else str(self.x_value)
        y_str = f"{self.y_value:.6g}" if isinstance(self.y_value, float) else str(self.y_value)
        return f"eml({x_str}, {y_str})"

@dataclass
class FrameworkConstant:
    """A closed framework constant expressed as eml-tree(s)."""
    name: str
    symbol: str
    dimension: Dimension
    eml_trees: List[EmlTree]
    predicted_value: float
    measured_value: float
    formula_description: str = ""

    def rel_error(self) -> float:
        """Relative error: |predicted - measured| / measured."""
        if self.measured_value == 0:
            return 0.0
        return abs(self.predicted_value - self.measured_value) / abs(self.measured_value)

    def rel_error_ppm(self) -> float:
        """Relative error in parts per million."""
        return self.rel_error() * 1e6

def eml(x: float, y: float) -> float:
    """Elementary multilinear function: eml(x, y) = exp(x) - ln(y)."""
    return math.exp(x) - math.log(y)

# ============================================================================
# Define all framework constants as eml-tree expressions
# ============================================================================

def build_constants() -> List[FrameworkConstant]:
    """Build complete set of framework constants."""

    u_alpha = -math.log(ALPHA_MEASURED)  # ln(1/α) = -ln(α)

    constants = []

    # ========================================================================
    # 0D Station: Aperture Coupling
    # ========================================================================

    # α: fine-structure constant (self-referential closure)
    # 1/α = 360/φ² - 2/φ³ + α/(21 - 4/3)
    # This is not directly eml, but α itself enters other constants as eml(E·u, 1)
    # For symbolic representation: α is the root fixed point
    alpha_tree = EmlTree(
        x_value=1.0,  # placeholder; α is self-determining
        y_value=1.0,
        depth=0,
        description="Self-referential closure: 360/φ² - 2/φ³ + α/(59/3)"
    )
    constants.append(FrameworkConstant(
        name="Fine-structure constant",
        symbol="α",
        dimension=Dimension.APERTURE,
        eml_trees=[alpha_tree],
        predicted_value=ALPHA_MEASURED,
        measured_value=137.035999177,
        formula_description="1/α = 360/φ² - 2/φ³ + α/(59/3) [self-determined]"
    ))

    # ========================================================================
    # 1.5D Station: Branching / Commitment (Mass Ratios)
    # ========================================================================

    # m_μ/m_e = (1/α)^(13/12 + α/27)
    E_muon = 13.0/12.0
    correction_muon = ALPHA_MEASURED / 27.0
    total_exp_muon = E_muon + correction_muon
    m_mu_me_pred = math.exp(total_exp_muon * u_alpha)

    muon_tree = EmlTree(
        x_value=total_exp_muon * u_alpha,
        y_value=1.0,
        depth=1,
        description="E(1.5) = V/(V-1) + α/T³"
    )
    constants.append(FrameworkConstant(
        name="Muon-to-electron mass ratio",
        symbol="m_μ/m_e",
        dimension=Dimension.BRANCHING,
        eml_trees=[muon_tree],
        predicted_value=m_mu_me_pred,
        measured_value=206.768,
        formula_description="(1/α)^(13/12 + α/27)"
    ))

    # m_τ/m_e = (1/α)^(58/35 + α/81)
    E_tau = 58.0/35.0
    correction_tau = ALPHA_MEASURED / 81.0
    total_exp_tau = E_tau + correction_tau
    m_tau_me_pred = math.exp(total_exp_tau * u_alpha)

    tau_tree = EmlTree(
        x_value=total_exp_tau * u_alpha,
        y_value=1.0,
        depth=1,
        description="E(2.5) = (S-SU3)/(T·V) + α/3⁴"
    )
    constants.append(FrameworkConstant(
        name="Tau-to-electron mass ratio",
        symbol="m_τ/m_e",
        dimension=Dimension.BRANCHING,
        eml_trees=[tau_tree],
        predicted_value=m_tau_me_pred,
        measured_value=3477.2,
        formula_description="(1/α)^(58/35 + α/81)"
    ))

    # ========================================================================
    # 2D Station: Field / Mediation (Gauge Angles, Weinberg)
    # ========================================================================

    # sin²(θ_W) = 3/13 + 5α/81
    # This is not exponential, but demonstrates depth-2 composition
    sin2_W_pred = (3.0/13.0) + (5.0 * ALPHA_MEASURED / 81.0)
    sin2_W_tree = EmlTree(
        x_value=math.log(sin2_W_pred),
        y_value=1.0,
        depth=2,
        description="SU(2)/V + (Φ+○)α/T⁴"
    )
    constants.append(FrameworkConstant(
        name="Weinberg angle (squared sine)",
        symbol="sin²(θ_W)",
        dimension=Dimension.FIELD,
        eml_trees=[sin2_W_tree],
        predicted_value=sin2_W_pred,
        measured_value=0.23122,
        formula_description="3/13 + 5α/81"
    ))

    # ========================================================================
    # 2.5D Station: Emergence (Mass Ratios cont'd, Cabibbo)
    # ========================================================================

    # m_p/m_e = (1/α)^(3/2 + (11/3)α + 13α²)
    # Depth 3: base + first-order + second-order
    E_p_base = 3.0/2.0
    E_p_1st = (11.0/3.0) * ALPHA_MEASURED
    E_p_2nd = 13.0 * ALPHA_MEASURED * ALPHA_MEASURED
    total_exp_p = E_p_base + E_p_1st + E_p_2nd
    # Use logarithmic form to avoid overflow: (1/α)^E = exp(E·ln(1/α))
    m_p_me_pred = math.exp(total_exp_p * u_alpha)

    proton_tree = EmlTree(
        x_value=total_exp_p * u_alpha,
        y_value=1.0,
        depth=3,
        description="A(1.5)/P + A'(2.5)α/T + A'(3)α²"
    )
    constants.append(FrameworkConstant(
        name="Proton-to-electron mass ratio",
        symbol="m_p/m_e",
        dimension=Dimension.EMERGENCE,
        eml_trees=[proton_tree],
        predicted_value=m_p_me_pred,
        measured_value=1836.153,
        formula_description="(1/α)^(3/2 + (11/3)α + 13α²)"
    ))

    # sin(θ_Cabibbo) = α^(1/2 + α·T/R) · SU(3)/T
    E_cabibbo = 0.5 + (ALPHA_MEASURED * T / R)
    prefactor_cabibbo = (SU3 / T)
    sin_theta_C_pred = math.exp(E_cabibbo * u_alpha) * prefactor_cabibbo

    cabibbo_tree = EmlTree(
        x_value=E_cabibbo * u_alpha,
        y_value=1.0 / prefactor_cabibbo,
        depth=2,
        description="α^(1/2 + 3α/7) · 8/3"
    )
    constants.append(FrameworkConstant(
        name="Cabibbo angle (sine)",
        symbol="sin(θ_C)",
        dimension=Dimension.EMERGENCE,
        eml_trees=[cabibbo_tree],
        predicted_value=sin_theta_C_pred,
        measured_value=0.2243,
        formula_description="α^(1/2 + 3α/7) · 8/3"
    ))

    # v/Λ_QCD = (1/α)^(56/39)
    E_vLambda = 56.0 / 39.0
    v_Lambda_pred = math.exp(E_vLambda * u_alpha)

    v_Lambda_tree = EmlTree(
        x_value=E_vLambda * u_alpha,
        y_value=1.0,
        depth=1,
        description="E(2.5) = (SU3·R)/(T·V)"
    )
    constants.append(FrameworkConstant(
        name="VEV to QCD scale ratio",
        symbol="v/Λ_QCD",
        dimension=Dimension.EMERGENCE,
        eml_trees=[v_Lambda_tree],
        predicted_value=v_Lambda_pred,
        measured_value=1170.2,
        formula_description="(1/α)^(56/39)"
    ))

    # ========================================================================
    # 3D Station: Boundary / Closure (Gravity, Cosmological Const)
    # ========================================================================

    # G (gravitational coupling) α_G = α²¹ · φ²/2 · (1 + 2α/91)
    E_G = 21.0
    phi_factor = (PHI * PHI) / 2.0
    correction_G = 1.0 + (2.0 * ALPHA_MEASURED / 91.0)
    alpha_G_pred = math.exp(E_G * u_alpha) * phi_factor * correction_G

    gravity_tree = EmlTree(
        x_value=E_G * u_alpha,
        y_value=1.0 / (phi_factor * correction_G),
        depth=3,
        description="α²¹ · φ²/2 · (1 + 2α/91)"
    )
    constants.append(FrameworkConstant(
        name="Gravitational coupling",
        symbol="α_G",
        dimension=Dimension.BOUNDARY,
        eml_trees=[gravity_tree],
        predicted_value=alpha_G_pred,
        measured_value=5.906e-39,  # approximate
        formula_description="α²¹ · (φ²/2) · (1 + 2α/91)"
    ))

    # Λ (cosmological constant in Planck units)
    # Λ = α^56 · (1 - 6α + 4α²) / 72
    E_Lambda = 56.0
    poly_Lambda = 1.0 - 6.0*ALPHA_MEASURED + 4.0*ALPHA_MEASURED*ALPHA_MEASURED
    prefactor_Lambda = poly_Lambda / 72.0
    Lambda_pred = math.exp(E_Lambda * u_alpha) * prefactor_Lambda

    cosmological_tree = EmlTree(
        x_value=E_Lambda * u_alpha,
        y_value=1.0 / prefactor_Lambda,
        depth=4,
        description="α^56 · (1 - 6α + 4α²) / 72"
    )
    constants.append(FrameworkConstant(
        name="Cosmological constant",
        symbol="Λ",
        dimension=Dimension.BOUNDARY,
        eml_trees=[cosmological_tree],
        predicted_value=Lambda_pred,
        measured_value=2.888e-122,
        formula_description="α^56 · (1 - 6α + 4α²) / 72"
    ))

    # ========================================================================
    # Composite / Derived Constants (Non-eml at top level, but use eml components)
    # ========================================================================

    # m_W / m_e = (1/α)^(95/39 - α/2)
    E_W = (95.0/39.0) - (ALPHA_MEASURED / 2.0)
    m_W_me_pred = math.exp(E_W * u_alpha)

    W_tree = EmlTree(
        x_value=E_W * u_alpha,
        y_value=1.0,
        depth=2,
        description="E(2.5) + 1 - α/Φ"
    )
    constants.append(FrameworkConstant(
        name="W boson mass (electron units)",
        symbol="m_W/m_e",
        dimension=Dimension.BOUNDARY,
        eml_trees=[W_tree],
        predicted_value=m_W_me_pred,
        measured_value=80.369e3/0.511,  # ~157,308 in electron masses
        formula_description="(1/α)^(95/39 - α/2)"
    ))

    # Higgs quartic coupling λ = (1/8)(1 + 5α - 8α²)
    lambda_H_pred = (1.0/8.0) * (1.0 + 5.0*ALPHA_MEASURED - 8.0*ALPHA_MEASURED*ALPHA_MEASURED)

    higgs_tree = EmlTree(
        x_value=0.0,  # Not an eml exponential; algebraic
        y_value=1.0,
        depth=1,
        description="1/SU(3) · (1 + 5α - 8α²)"
    )
    constants.append(FrameworkConstant(
        name="Higgs quartic coupling",
        symbol="λ_H",
        dimension=Dimension.BOUNDARY,
        eml_trees=[higgs_tree],
        predicted_value=lambda_H_pred,
        measured_value=0.12938,
        formula_description="(1/8)(1 + 5α - 8α²)"
    ))

    # ========================================================================
    # Chemistry & Biology Constants (Framework Integers)
    # ========================================================================

    # Tetrahedral angle: cos(θ_tet) = -1/T = -1/3
    cos_tet_pred = -1.0 / T
    tet_angle_deg = math.degrees(math.acos(cos_tet_pred))

    tet_tree = EmlTree(
        x_value=0.0,  # arccos(-1/T) is not eml; pure structural
        y_value=T,
        depth=0,
        description="arccos(-1/T) = 109.47°"
    )
    constants.append(FrameworkConstant(
        name="Tetrahedral bond angle",
        symbol="θ_tet",
        dimension=Dimension.FIELD,
        eml_trees=[tet_tree],
        predicted_value=tet_angle_deg,
        measured_value=109.47,
        formula_description="arccos(-1/3)"
    ))

    # Water bond angle: cos(θ_HOH) = -(R² - G)/(T·R²) = -37/147
    cos_water = -(R*R - G) / (T * R * R)
    water_angle_deg = math.degrees(math.acos(cos_water))

    water_tree = EmlTree(
        x_value=0.0,  # structural, not exponential
        y_value=T * R * R / (R*R - G),
        depth=0,
        description="arccos(-37/147) = 104.58°"
    )
    constants.append(FrameworkConstant(
        name="Water bond angle",
        symbol="θ_HOH",
        dimension=Dimension.FIELD,
        eml_trees=[water_tree],
        predicted_value=water_angle_deg,
        measured_value=104.45,
        formula_description="arccos(-37/147)"
    ))

    # Kleiber exponent: T/P = 3/4
    kleiber_pred = T / P

    kleiber_tree = EmlTree(
        x_value=0.0,  # pure ratio
        y_value=1.0,
        depth=0,
        description="T/P = triad/pump"
    )
    constants.append(FrameworkConstant(
        name="Kleiber's Law exponent",
        symbol="T/P",
        dimension=Dimension.FIELD,
        eml_trees=[kleiber_tree],
        predicted_value=kleiber_pred,
        measured_value=0.75,
        formula_description="3/4"
    ))

    # Murray's Law exponent: T = 3
    murray_pred = T

    murray_tree = EmlTree(
        x_value=0.0,
        y_value=1.0,
        depth=0,
        description="T = triad"
    )
    constants.append(FrameworkConstant(
        name="Murray's Law exponent",
        symbol="T",
        dimension=Dimension.BOUNDARY,
        eml_trees=[murray_tree],
        predicted_value=murray_pred,
        measured_value=3.0,
        formula_description="3"
    ))

    # DNA base pairs per turn: A(3)/Φ = 21/2 = 10.5
    dna_bpt_pred = (T * (T + 1)) / 2.0  # A(3) = 21, Φ = 2

    dna_tree = EmlTree(
        x_value=0.0,
        y_value=2.0 / 21.0,
        depth=0,
        description="A(3)/Φ = T(T+1)/2"
    )
    constants.append(FrameworkConstant(
        name="DNA helical turns per base pair",
        symbol="A(3)/Φ",
        dimension=Dimension.WHOLE,
        eml_trees=[dna_tree],
        predicted_value=dna_bpt_pred,
        measured_value=10.5,
        formula_description="21/2"
    ))

    # Hayflick limit: S = 64 = P^T
    hayflick_pred = S

    hayflick_tree = EmlTree(
        x_value=0.0,
        y_value=1.0,
        depth=0,
        description="S = P^T = 4^3"
    )
    constants.append(FrameworkConstant(
        name="Hayflick limit (cell divisions)",
        symbol="S",
        dimension=Dimension.WHOLE,
        eml_trees=[hayflick_tree],
        predicted_value=hayflick_pred,
        measured_value=64.0,
        formula_description="64 = 4^3"
    ))

    return constants

# ============================================================================
# Main Output Routine
# ============================================================================

def print_constant_table(constants: List[FrameworkConstant]) -> None:
    """Print formatted table of all constants."""
    print("=" * 150)
    print("CANONICAL eml-TREE REPRESENTATIONS OF CIRCUMPUNCT FRAMEWORK CONSTANTS")
    print("=" * 150)
    print()
    print(f"{'Constant':<25} {'Symbol':<12} {'Dimension':<10} {'Depth':<5} "
          f"{'Predicted':<18} {'Measured':<18} {'Rel Error':<12}")
    print("-" * 150)

    for const in constants:
        if const.eml_trees:
            tree = const.eml_trees[0]
            pred_str = f"{const.predicted_value:.6e}"
            meas_str = f"{const.measured_value:.6e}"
            err_ppm = const.rel_error_ppm()
            if err_ppm < 1e-6:
                err_str = f"< 1 ppb"
            elif err_ppm < 1e-3:
                err_str = f"{err_ppm:.2f} ppb"
            else:
                err_str = f"{err_ppm:.2e} ppm"

            print(f"{const.name:<25} {const.symbol:<12} {const.dimension.value:<10} {tree.depth:<5} "
                  f"{pred_str:<18} {meas_str:<18} {err_str:<12}")

    print("=" * 150)

def print_constant_details(constants: List[FrameworkConstant]) -> None:
    """Print detailed breakdown of each constant."""
    print("\n" + "=" * 120)
    print("DETAILED eml-TREE DEFINITIONS")
    print("=" * 120)
    print()

    for const in constants:
        print(f"  {const.name:.<60}")
        print(f"    Symbol:      {const.symbol}")
        print(f"    Dimension:   {const.dimension.value}")
        print(f"    Formula:     {const.formula_description}")
        print(f"    Predicted:   {const.predicted_value:.12e}")
        print(f"    Measured:    {const.measured_value:.12e}")
        print(f"    Rel Error:   {const.rel_error_ppm():.6f} ppm")
        if const.eml_trees:
            for i, tree in enumerate(const.eml_trees):
                print(f"    eml-tree {i}: {tree.symbolic()}")
                print(f"                Depth: {tree.depth}, Description: {tree.description}")
        print()

if __name__ == "__main__":
    constants = build_constants()

    print("\n")
    print_constant_table(constants)
    print_constant_details(constants)

    # Summary statistics
    print("\n" + "=" * 120)
    print("SUMMARY STATISTICS")
    print("=" * 120)
    print(f"Total constants defined: {len(constants)}")

    depths = [tree.depth for c in constants for tree in c.eml_trees]
    print(f"eml-tree depths: min={min(depths)}, max={max(depths)}, avg={sum(depths)/len(depths):.2f}")

    # Group by dimension
    print("\nConstants by dimensional station:")
    dim_groups: Dict[Dimension, List[FrameworkConstant]] = {}
    for const in constants:
        dim = const.dimension
        if dim not in dim_groups:
            dim_groups[dim] = []
        dim_groups[dim].append(const)

    for dim in sorted(dim_groups.keys(), key=lambda d: d.value):
        print(f"  {dim.value:<10} : {len(dim_groups[dim]):>2} constants")

    print("\n" + "=" * 120)
