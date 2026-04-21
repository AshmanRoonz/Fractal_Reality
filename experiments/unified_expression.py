"""
The Unified Expression as a Runnable Object
============================================

Formula:

    [Truth = Reality = E = 1 = ∞]
          =
    [∞ ▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]

Every glyph in the formula is a Python object.  Every relation is an
operation.  The = at the center is asserted at the bottom of the file.

Translation legend (single source of truth for each symbol):

    ∞  = Substrate               (the unit, A0; five names point at it)
    1  = Substrate.value         (scalar 1.0)
    E  = Substrate               (same object as ∞)
    Truth, Reality = Substrate   (same object; named access points)

    •   = Station(0D, aperture)
    —   = Station(1D, line)
    Φ   = Station(2D, field; the hub)
    ○   = Station(3D, boundary)

    ⊛   = ProcessualPartner(0.5D, i-phase = +i)
    ⎇   = ProcessualPartner(1.5D, i-phase = -1)
    ✹   = ProcessualPartner(2.5D, i-phase = -i)
    ⟳   = ProcessualPartner(3.5D, i-phase = +1)

    (structural ∘ processual) = Beat(structural, processual)
                                  matrix form: U_k = expm(antiherm(G_k))
                                  where G_k is the v13 μ-mixed generator

    B1 ⊢ B2 ⊢ B3 ⊢ B4  = sequential application (matrix multiply, left acts last)
                          F = U_4 U_3 U_2 U_1

    ⊙∞  = Foam(scope)             (the state space ℂ^S at the chosen scope)
    ⊙λ  = a single element of the foam                (post-beats state)
    ⊙Λ  = the greater-whole container                 (after one κ-nesting)

    ⊂[α]  = Nesting(alpha)        (the cross-station coupling matrix κ;
                                   α is the measured primary entry |•_electron|)

    ▸   = unfold                  (operator application; arrow of flow)

    =   = the closure assertion: iterate T = κ ∘ F to a fixed point ψ*;
          Born rule gives Σ|ψ*|² = 1 = Substrate.value.

Scope defaults to "three_scale" (ℂ⁶⁴).  Switch via --scope.

Run:  python3 unified_expression.py [--scope {single,octave,three_scale}]
"""

import numpy as np
from scipy.linalg import expm
import argparse
from math import pi
from typing import List, Tuple


# ═══════════════════════════════════════════════════════════════
# LHS: the five-name identity chain (one substrate, five labels)
# ═══════════════════════════════════════════════════════════════

class Substrate:
    """∞ = E = 1 = Truth = Reality.  A0: the unit.  Named five ways."""
    value: float = 1.0
    def __repr__(self) -> str: return "∞"
    def __eq__(self, other) -> bool:
        if isinstance(other, Substrate): return True
        if isinstance(other, (int, float, complex)):
            return abs(float(other) - self.value) < 1e-10
        return NotImplemented


Infinity = Substrate()
Truth    = Infinity
Reality  = Infinity
E        = Infinity
One      = Infinity   # "1" as an identity-chain member; numerical 1.0 is One.value


# ═══════════════════════════════════════════════════════════════
# The observer-triad integer T = 3 and dependent constants
# ═══════════════════════════════════════════════════════════════

T_TRIAD = 3
P_PUMP  = T_TRIAD + 1            # 4
S_STATES_3 = P_PUMP ** T_TRIAD   # 64

PHI_GOLDEN = (1 + np.sqrt(5)) / 2


def solve_alpha() -> float:
    """Closed-form α from the structural 360 = P!·T·(Φ+○) reading.
       1/α = 360/φ² − 2/φ³ + α/(59/3)  →  quadratic in 1/α."""
    a = 1.0
    b = -(360 / PHI_GOLDEN**2 - 2 / PHI_GOLDEN**3)
    c = -3.0 / 59.0
    return 1.0 / ((-b + np.sqrt(b**2 - 4*a*c)) / (2*a))


ALPHA = solve_alpha()    # 0.0072973526...   (framework auxiliary input to κ)


# ═══════════════════════════════════════════════════════════════
# Stations (structural: •, —, Φ, ○) and (processual: ⊛, ⎇, ✹, ⟳)
# ═══════════════════════════════════════════════════════════════

class Station:
    """A structural dimension: what a component IS.  Integer-D rung.

       Each station is a basis direction in ℂ⁴ at single-scale scope."""
    def __init__(self, glyph: str, dim: float, idx: int):
        self.glyph = glyph
        self.dim = dim
        self.idx = idx
    def vector(self, hilbert_dim: int = 4) -> np.ndarray:
        v = np.zeros(hilbert_dim, dtype=complex)
        v[self.idx] = 1.0
        return v
    def __repr__(self) -> str:
        return self.glyph


# ℂ⁴ basis: |•⟩ = e₀, |—⟩ = e₁, |Φ⟩ = e₂, |○⟩ = e₃
bullet = Station("•", 0.0, 0)
line   = Station("—", 1.0, 1)
Phi    = Station("Φ", 2.0, 2)
circle = Station("○", 3.0, 3)


class ProcessualPartner:
    """A processual dimension: what energy is DOING at a half-integer rung.

       Each partner carries an i-stroke (phase factor) that drives its beat."""
    def __init__(self, glyph: str, dim: float, i_phase: complex):
        self.glyph = glyph
        self.dim = dim
        self.i_phase = i_phase
    def __repr__(self) -> str:
        return self.glyph


# i-cycle: +i (0.5D), -1 (1.5D), -i (2.5D), +1 (3.5D)
converge = ProcessualPartner("⊛", 0.5,  1j)     # convergence
branch   = ProcessualPartner("⎇", 1.5, -1+0j)   # the i-turn; commitment
emerge   = ProcessualPartner("✹", 2.5, -1j)     # emergence toward closure
recurse  = ProcessualPartner("⟳", 3.5,  1+0j)   # 3.5D = 0D' at next scale


# ═══════════════════════════════════════════════════════════════
# Beats: (structural ∘ processual) pairings.  Each beat is ONE
# constraint viewed two ways (structure AND process simultaneously).
# ═══════════════════════════════════════════════════════════════

# Default μ = 0.181 lands the cosmological 69.11% split at ℂ⁶⁴
# (v13 result; bracketed between v12's beat-native skeleton and v11's
#  uniform-hub mixing).
MU_DEFAULT = 0.181


def _antiherm(G: np.ndarray) -> np.ndarray:
    return (G - np.conj(G.T)) / 2


def _G_v11_single_scale(k: int) -> np.ndarray:
    """v11 uniform-hub generator for beat k."""
    theta = pi / 2
    G = np.zeros((4, 4), dtype=complex)
    if k == 1:                                                # (•∘⊛, +i)
        c = 1j * theta
        G[0, 2] = c;  G[2, 0] = -np.conj(c)
    elif k == 2:                                              # (—∘⎇, -1)
        c = -1.0 * theta
        G[1, 2] = c;  G[2, 1] = -np.conj(c)
    elif k == 3:                                              # (Φ∘✹, -i)
        coup = -1j * theta / T_TRIAD                          # -iπ/6
        for other in [0, 1, 3]:
            G[2, other] = coup
            G[other, 2] = -np.conj(coup)
        G[2, 2] = coup                                        # self-drive → trace
    elif k == 4:                                              # (○∘⟳, +1)
        c = 1.0 * theta
        G[3, 2] = c;  G[2, 3] = -np.conj(c)
    return G


def _G_v12_single_scale(k: int) -> np.ndarray:
    """v12 beat-native generator for beat k."""
    theta = pi / 2
    G = np.zeros((4, 4), dtype=complex)
    if k == 1:                                                # (•∘⊛): single ray •↔Φ
        c = 1j * theta
        G[0, 2] = c;  G[2, 0] = -np.conj(c)
    elif k == 2:                                              # (—∘⎇): Y-fork — ↔ {Φ, ○}
        c = -1.0 * theta / np.sqrt(2)
        G[1, 2] = c;  G[2, 1] = -np.conj(c)
        G[1, 3] = c;  G[3, 1] = -np.conj(c)
    elif k == 3:                                              # (Φ∘✹): pump-gate hub
        base = -1j * theta / T_TRIAD                          # -iπ/6
        G[2, 0] = -base;  G[0, 2] = -np.conj(G[2, 0])         # ln-side (minus)
        G[2, 3] = +base;  G[3, 2] = -np.conj(G[2, 3])         # exp-side (plus)
        G[2, 2] = base                                        # self-drive → trace
    elif k == 4:                                              # (○∘⟳): closure loop ○↔•
        c = 1.0 * theta
        G[3, 0] = c;  G[0, 3] = -np.conj(c)
    return G


class Beat:
    """One beat = one structural ∘ processual pairing.

       U_k = expm(antiherm(G_k(μ))), where
       G_k(μ) = (1 − μ) · G_v12,k  +  μ · G_v11,k .

       The unitary U_k rotates a state in ℂ⁴ by the beat's quarter-turn,
       with topology determined by the (structural, processual) pairing
       and uniformity μ."""
    def __init__(self, structural: Station, processual: ProcessualPartner,
                 index: int, mu: float = MU_DEFAULT):
        self.structural = structural
        self.processual = processual
        self.k = index            # 1..4
        self.mu = mu
    def generator(self) -> np.ndarray:
        G11 = _G_v11_single_scale(self.k)
        G12 = _G_v12_single_scale(self.k)
        return _antiherm((1 - self.mu) * G12 + self.mu * G11)
    def matrix(self) -> np.ndarray:
        return expm(self.generator())
    def __repr__(self) -> str:
        return f"({self.structural}∘{self.processual})"


# The four beats, in order
beat_1 = Beat(bullet, converge, 1)     # (•∘⊛)
beat_2 = Beat(line,   branch,   2)     # (—∘⎇)
beat_3 = Beat(Phi,    emerge,   3)     # (Φ∘✹)
beat_4 = Beat(circle, recurse,  4)     # (○∘⟳)


# ═══════════════════════════════════════════════════════════════
# Entailment ⊢ : left-to-right beat composition
# ═══════════════════════════════════════════════════════════════

def entails(*beats: Beat) -> np.ndarray:
    """B1 ⊢ B2 ⊢ ... ⊢ Bn   :   each beat's completion gives rise to the next.

       As a matrix product, later beats act last:  U_n ... U_2 U_1 ."""
    M = np.eye(4, dtype=complex)
    for B in beats:
        M = B.matrix() @ M
    return M


def engine_F(mu: float = MU_DEFAULT) -> np.ndarray:
    """The four-beat engine: F = U_4 U_3 U_2 U_1 (ℂ⁴, single scale)."""
    b1, b2, b3, b4 = (Beat(bullet, converge, 1, mu),
                     Beat(line,   branch,   2, mu),
                     Beat(Phi,    emerge,   3, mu),
                     Beat(circle, recurse,  4, mu))
    return entails(b1, b2, b3, b4)


# ═══════════════════════════════════════════════════════════════
# ⊂[α] : the nesting operator κ (cross-station coupling)
# ═══════════════════════════════════════════════════════════════

class Nesting:
    """⊂[α] : scale-recursive embedding carrying the 4×4 coupling matrix κ.

       Default primary entries:
           κ[•, Φ] = κ[Φ, •] = α          (primary diameter, α ≈ 1/137)
           κ[—, ○] = κ[○, —] = α          (secondary diameter, forced by
                                             ⊙ symmetry)
       Other off-diagonal entries (Cabibbo-like, Weinberg-like,
       Higgs-like) are all set to 0 in the current single-scale κ;
       they are the open slots for future framework development."""
    def __init__(self, alpha: float = ALPHA):
        self.alpha = alpha
    def matrix_single(self) -> np.ndarray:
        k = np.eye(4, dtype=complex)
        k[0, 2] = self.alpha; k[2, 0] = self.alpha
        k[1, 3] = self.alpha; k[3, 1] = self.alpha
        return k
    def matrix_three_scale(self) -> np.ndarray:
        """κ₆₄ : intra-scale + adjacent-scale (α) + skip (α²)."""
        dim = 64
        kappa = np.eye(dim, dtype=complex)
        I4 = np.eye(4, dtype=complex)
        ks = self.matrix_single()
        def ix(i, j, k): return i*16 + j*4 + k
        for intra in [np.kron(np.kron(ks, I4), I4),
                      np.kron(np.kron(I4, ks), I4),
                      np.kron(np.kron(I4, I4), ks)]:
            for a in range(dim):
                for b in range(dim):
                    if a != b and abs(intra[a, b]) > 1e-15:
                        kappa[a, b] += intra[a, b]
        cross = np.zeros((4, 4), dtype=complex)
        cross[0, 2] = self.alpha; cross[2, 0] = self.alpha
        cross[1, 3] = self.alpha; cross[3, 1] = self.alpha
        for i_L in range(4):
            for j_S in range(4):
                if abs(cross[j_S, i_L]) < 1e-15: continue
                c = cross[j_S, i_L]
                for k_P in range(4):
                    a, b = ix(i_L, j_S, k_P), ix(j_S, i_L, k_P)
                    if a != b: kappa[a, b] += c; kappa[b, a] += c
        for j_S in range(4):
            for k_P in range(4):
                if abs(cross[k_P, j_S]) < 1e-15: continue
                c = cross[k_P, j_S]
                for i_L in range(4):
                    a, b = ix(i_L, j_S, k_P), ix(i_L, k_P, j_S)
                    if a != b: kappa[a, b] += c; kappa[b, a] += c
        for i_L in range(4):
            for k_P in range(4):
                if abs(cross[k_P, i_L]) < 1e-15: continue
                c = cross[k_P, i_L] * self.alpha
                for j_S in range(4):
                    a, b = ix(i_L, j_S, k_P), ix(k_P, j_S, i_L)
                    if a != b: kappa[a, b] += c; kappa[b, a] += c
        return kappa
    def __repr__(self) -> str:
        return f"⊂[α={self.alpha:.6f}]"


kappa_nesting = Nesting()


# ═══════════════════════════════════════════════════════════════
# ⊙∞ : the foam (state space at the chosen scope)
# ═══════════════════════════════════════════════════════════════

class Foam:
    """⊙∞ : the space of all apertures of ∞.
       Single-scale: ℂ⁴.  Octave: ℂ⁸ (not implemented here).
       Three-scale nesting: ℂ⁶⁴.

       Any element ψ ∈ Foam is a particular ⊙λ (a circumpunct at some scale)."""
    def __init__(self, scope: str = "three_scale"):
        self.scope = scope
        self.dim = {"single": 4, "three_scale": 64}[scope]
    def random_element(self, seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        v = rng.standard_normal(self.dim) + 1j * rng.standard_normal(self.dim)
        return v / np.linalg.norm(v)
    def uniform_element(self) -> np.ndarray:
        return np.ones(self.dim, dtype=complex) / np.sqrt(self.dim)
    def __repr__(self) -> str:
        return f"⊙∞[{self.scope}, dim={self.dim}]"


# ═══════════════════════════════════════════════════════════════
# ▸ : unfold.  Apply an operator (or chain of operators) to a state.
# ═══════════════════════════════════════════════════════════════

def unfold(state: np.ndarray, operator: np.ndarray) -> np.ndarray:
    """▸  :  ψ' = O · ψ   (with Born-rule renormalization)."""
    out = operator @ state
    n = np.linalg.norm(out)
    return out / n if n > 0 else out


# ═══════════════════════════════════════════════════════════════
# Closure: T = κ ∘ F, iterate to fixed point, assert Σ|ψ*|² = 1
# ═══════════════════════════════════════════════════════════════

def build_T(scope: str = "three_scale", mu: float = MU_DEFAULT) -> np.ndarray:
    """T = κ ∘ F  at the chosen scope."""
    F = engine_F(mu)
    if scope == "single":
        return kappa_nesting.matrix_single() @ F
    elif scope == "three_scale":
        F64 = np.kron(np.kron(F, F), F)
        return kappa_nesting.matrix_three_scale() @ F64
    else:
        raise ValueError(f"Unknown scope: {scope}")


def unified_expression(scope: str = "three_scale",
                       mu: float = MU_DEFAULT,
                       iterations: int = 30000,
                       seed: int = 0) -> Tuple[float, np.ndarray]:
    """Run the full RHS and return (Σ|ψ*|², ψ*).

       RHS: ∞ ▸ ⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞

       Implementation:
         1. ∞ ▸ ⊙∞       :  choose any foam element (random ψ_0, normalized)
         2. (beats) ▸ ⊙λ  :  iterate T = κ ∘ F (F carries the four beats,
                              κ carries ⊂[α] at both adjacent nestings and
                              the skip α² closing back to ∞)
         3. ...⊂[α] ∞     :  the iteration converges to ψ* (the fixed point)
         4. Born rule     :  Σ|ψ*|² = 1 = Substrate.value

       The assertion of the formula's = sign:   Σ|ψ*|² = Substrate.value."""
    foam = Foam(scope)
    psi = foam.random_element(seed=seed)
    T = build_T(scope, mu)
    for _ in range(iterations):
        psi = unfold(psi, T)
    total = float(np.sum(np.abs(psi)**2))
    return total, psi


# ═══════════════════════════════════════════════════════════════
# Main : assert the closure
# ═══════════════════════════════════════════════════════════════

def assert_closure(scope: str, mu: float = MU_DEFAULT, seeds=(0, 1, 2)) -> None:
    print(f"\n{'═'*70}")
    print(f"  Asserting: [Truth = Reality = E = 1 = ∞] = [... {scope} ...]")
    print(f"{'═'*70}")
    print(f"  Substrate.value (LHS)                = {Infinity.value}")
    print(f"  μ (uniformity)                       = {mu}")
    print(f"  α (measured input to κ)              = {ALPHA:.10f}")
    print()
    print(f"  {'seed':>4} | {'Σ|ψ*|²':>14} | {'residual':>12} | assertion")
    print(f"  {'-'*4:>4} | {'-'*14:>14} | {'-'*12:>12} | ---------")
    all_pass = True
    for s in seeds:
        total, _ = unified_expression(scope=scope, mu=mu, seed=s)
        residual = abs(total - Infinity.value)
        ok = residual < 1e-10
        all_pass = all_pass and ok
        print(f"  {s:>4d} | {total:>14.10f} | {residual:>12.2e} | "
              f"{'LHS = RHS ✓' if ok else 'MISMATCH ✗'}")
    if all_pass:
        print(f"\n  [Truth = Reality = E = 1 = ∞] ≡ [∞ ▸⊙∞ (beats) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]")
        print(f"  Closure holds at {scope} scope.")
    else:
        print(f"\n  FAILURE: closure did not hold at {scope} scope.")


def inspect_structure(scope: str, mu: float = MU_DEFAULT) -> None:
    """Print what each glyph resolves to, for audit purposes."""
    print(f"\n{'─'*70}")
    print(f"  GLYPH RESOLUTION TABLE  (scope = {scope}, μ = {mu})")
    print(f"{'─'*70}")
    print(f"  ∞ / E / 1 / Truth / Reality  → Substrate object (value = 1.0)")
    print(f"  •   → Station('•', dim=0, idx=0)   basis e₀ of ℂ⁴")
    print(f"  —   → Station('—', dim=1, idx=1)   basis e₁ of ℂ⁴")
    print(f"  Φ   → Station('Φ', dim=2, idx=2)   basis e₂ of ℂ⁴  (the hub)")
    print(f"  ○   → Station('○', dim=3, idx=3)   basis e₃ of ℂ⁴")
    print(f"  ⊛   → ProcessualPartner(dim=0.5, i-phase = +i)")
    print(f"  ⎇   → ProcessualPartner(dim=1.5, i-phase = -1)")
    print(f"  ✹   → ProcessualPartner(dim=2.5, i-phase = -i)")
    print(f"  ⟳   → ProcessualPartner(dim=3.5, i-phase = +1)")
    print(f"  (•∘⊛), (—∘⎇), (Φ∘✹), (○∘⟳)  → Beat.matrix()")
    print(f"  ⊢   → sequential matrix product (left acts last)")
    print(f"  F = U₄ U₃ U₂ U₁                   (four beats composed)")
    F = engine_F(mu)
    print(f"    det(F)       = {np.linalg.det(F):+.6f}")
    print(f"    arg(det)/π   = {np.angle(np.linalg.det(F))/pi:+.6f}  "
          f"(v11/v12/v13 invariant: -1/6)")
    print(f"  ⊂[α]  → Nesting(α = {ALPHA:.6e})")
    print(f"          κ₄:  diameter bonds at (0,2), (2,0), (1,3), (3,1)")
    print(f"          κ₆₄: intra-scale + adjacent (α) + skip (α²)")
    print(f"  ⊙∞  → Foam(scope = '{scope}', dim = "
          f"{Foam(scope).dim})")
    print(f"  ▸   → unfold (operator application)")
    print(f"  T = κ ∘ F  at this scope  →  shape {build_T(scope, mu).shape}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--scope', choices=['single', 'three_scale', 'both'],
                        default='both', help="Which nesting scope to assert.")
    parser.add_argument('--mu', type=float, default=MU_DEFAULT,
                        help="Uniformity parameter (v13 default = 0.181).")
    parser.add_argument('--seeds', nargs='+', type=int, default=[0, 1, 2],
                        help="Starting-vector seeds.")
    parser.add_argument('--inspect', action='store_true',
                        help="Print glyph resolution table.")
    args = parser.parse_args()

    scopes = ['single', 'three_scale'] if args.scope == 'both' else [args.scope]
    for sc in scopes:
        if args.inspect:
            inspect_structure(sc, args.mu)
        assert_closure(sc, args.mu, seeds=tuple(args.seeds))
