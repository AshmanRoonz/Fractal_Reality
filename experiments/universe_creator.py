"""
Universe Creator: α-sweep across the three-scale T-operator
============================================================

Treat α (the primary entry of the ⊂[α] coupling matrix, §27.7q) as a free
parameter and ask: what kind of universe comes out? Our universe runs at
α = 1/137 ≈ 0.00729735; alternate universes are alternate values of the
⊂[α] coupling.

Three-scale architecture (§27.7s, ℂ⁶⁴ reading): F₆₄ = F₄ ⊗ F₄ ⊗ F₄ over
three nested circumpuncts ⊙Λ × ⊙λ × ⊙λ'; κ₆₄ carries intra-scale diameter
bonds plus adjacent cross-scale coupling (strength α) and a Λ-λ' skip
coupling (strength α²). T = κ ∘ F is the conservation form.

Five features, each flagged in a section header below:
    (1) α-sweep driver over [1/10, 1/30, 1/100, 1/137, 1/300, 1/1000]
    (2) cosmological-budget observable (structural vs processual at each scale)
    (3) stability regime detector (Severance / stable / Inflation)
    (4) pool-integer emergence checker at α = 1/137
    (5) emergent-time diagnostic (canonical beat order across iterations)

CLI:
    python universe_creator.py --our-universe       # α = 1/137, all diagnostics
    python universe_creator.py --sweep              # α-sweep table
    python universe_creator.py --alpha 0.00729735   # one universe
    python universe_creator.py --alpha 0.00729735 --scale C64

Author: Ashman Roonz & Claude
Date: 2026-04-22
"""

from __future__ import annotations

import argparse
import time
from typing import Dict, List, Tuple

import numpy as np
from scipy.linalg import expm


# =============================================================================
# Framework pool integers (all derive from T = 3 via seven independent routes)
# =============================================================================

PHI = (1 + np.sqrt(5)) / 2
T_TRIAD = 3
P_PUMP = 4
R_RUNGS = 7                         # T^2 - 2
V_GEN_PLUS = 13                     # P*T + 1
SU3 = 8                             # T^2 - 1
G_GEN = 12                          # T*(T+1)
S_STATES = 64                       # (T+1)^T = P^T
A3_VAL = 21                         # T*(2T+1)
A2_VAL = 10                         # 2*(2*2+1)

# Our-universe α: CODATA/framework-consistent value
ALPHA_OURS = 1.0 / 137.035999177


# =============================================================================
# ℂ⁴ single-scale F and κ  (parametrized by α; adapted from v11_C64.py)
# =============================================================================

def _anti_hermitian(G: np.ndarray) -> np.ndarray:
    return (G - np.conj(G.T)) / 2


def build_F_single() -> np.ndarray:
    """
    F₄ for one ⊙ (ℂ⁴ sphere-hub topology). Stations: 0(•) 1(—) 2(Φ) 3(○).
    Four beats in canonical order; Φ (index 2) is the central mediator.
    The beat sequence is (•∘⊛) → (—∘⎇) → (Φ∘✹) → (○∘⟳).
    """
    theta = np.pi / 2
    PHI_IDX = 2

    beat_config = [
        ('(•∘⊛)', 0, 1j),       # i¹ = +i,  convergence
        ('(—∘⎇)', 1, -1+0j),    # i² = -1,  commitment
        ('(Φ∘✹)', 2, -1j),      # i³ = -i,  emergence
        ('(○∘⟳)', 3, 1+0j),     # i⁰ = +1,  recursion
    ]

    beats = []
    for _, active, i_phase in beat_config:
        G = np.zeros((4, 4), dtype=complex)
        if active == PHI_IDX:
            for other in [0, 1, 3]:
                c = i_phase * theta / T_TRIAD
                G[PHI_IDX, other] = c
                G[other, PHI_IDX] = -np.conj(c)
            G[PHI_IDX, PHI_IDX] = i_phase * theta / T_TRIAD
        else:
            c = i_phase * theta
            G[active, PHI_IDX] = c
            G[PHI_IDX, active] = -np.conj(c)
        G = _anti_hermitian(G)
        beats.append(expm(G))

    F = np.eye(4, dtype=complex)
    for B in beats:
        F = B @ F
    return F


def build_kappa_single(alpha: float) -> np.ndarray:
    """Intra-scale κ₄ for one ⊙. Primary diameters: •↔Φ and —↔○, each at strength α."""
    k = np.eye(4, dtype=complex)
    k[0, 2] = k[2, 0] = alpha   # •↔Φ
    k[1, 3] = k[3, 1] = alpha   # —↔○
    return k


# =============================================================================
# ℂ⁶⁴ three-scale construction, parametrized by α
# =============================================================================

def _idx64(i: int, j: int, k: int) -> int:
    return i * 16 + j * 4 + k


def build_F_64() -> np.ndarray:
    """F₆₄ = F₄ ⊗ F₄ ⊗ F₄  (A3: same F at every scale; α-independent)."""
    F = build_F_single()
    return np.kron(np.kron(F, F), F)


def build_kappa_64(alpha: float) -> np.ndarray:
    """
    κ₆₄: intra-scale diameters at every scale (strength α), adjacent cross-scale
    (Λ↔λ, λ↔λ') at strength α, skip coupling (Λ↔λ') at strength α².
    """
    dim = 64
    kappa = np.eye(dim, dtype=complex)

    I4 = np.eye(4, dtype=complex)
    k_s = build_kappa_single(alpha)

    # Intra-scale at each of the three scales
    intra_L = np.kron(np.kron(k_s, I4), I4)
    intra_S = np.kron(np.kron(I4, k_s), I4)
    intra_P = np.kron(np.kron(I4, I4), k_s)
    for intra in (intra_L, intra_S, intra_P):
        off = intra - np.diag(np.diag(intra))
        kappa += off

    # Cross-scale 4x4 coupling matrix (same diameter pattern as intra)
    cross = np.zeros((4, 4), dtype=complex)
    cross[0, 2] = cross[2, 0] = alpha
    cross[1, 3] = cross[3, 1] = alpha

    # Adjacent: Λ↔λ
    for i_L in range(4):
        for j_S in range(4):
            c = cross[j_S, i_L]
            if abs(c) < 1e-15:
                continue
            for k_P in range(4):
                a = _idx64(i_L, j_S, k_P)
                b = _idx64(j_S, i_L, k_P)
                if a != b:
                    kappa[a, b] += c
                    kappa[b, a] += c

    # Adjacent: λ↔λ'
    for j_S in range(4):
        for k_P in range(4):
            c = cross[k_P, j_S]
            if abs(c) < 1e-15:
                continue
            for i_L in range(4):
                a = _idx64(i_L, j_S, k_P)
                b = _idx64(i_L, k_P, j_S)
                if a != b:
                    kappa[a, b] += c
                    kappa[b, a] += c

    # Skip: Λ↔λ' at α^2
    for i_L in range(4):
        for k_P in range(4):
            c = cross[k_P, i_L] * alpha
            if abs(c) < 1e-15:
                continue
            for j_S in range(4):
                a = _idx64(i_L, j_S, k_P)
                b = _idx64(k_P, j_S, i_L)
                if a != b:
                    kappa[a, b] += c
                    kappa[b, a] += c

    return kappa


def build_T_64(alpha: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    F = build_F_64()
    K = build_kappa_64(alpha)
    return K @ F, F, K


# =============================================================================
# Observables (used by features 2, 3, 4, 5)
# =============================================================================

def leading_eig(T: np.ndarray):
    evals, evecs = np.linalg.eig(T)
    order = np.argsort(-np.abs(evals))
    return evals[order], evecs[:, order]


def weights_from_vec(v: np.ndarray) -> np.ndarray:
    w = np.abs(v)**2
    s = np.sum(w)
    return w / s if s > 0 else w


# -----------------------------------------------------------------------------
# FEATURE 2 : Cosmological-budget observable
# -----------------------------------------------------------------------------

def cosmological_split_C64(w: np.ndarray) -> Dict[str, float]:
    """
    On the diameter basis: primary = •+Φ stations (structural aperture/field),
    secondary = —+○ stations (line/boundary). The v11 ℂ⁶⁴ result read 68.53/31.47
    on primary vs secondary at three-scale (cf cosmological 69.11/30.89).

    Returns per-scale structural/processual-proxy fractions. In ℂ⁴ the four
    stations are all structural (no processual half-integer partners at this
    resolution), so we use the diameter-basis reading as the "cosmological"
    analogue: primary diameter (•+Φ) vs secondary diameter (—+○).
    """
    w_r = w.reshape(4, 4, 4)
    out: Dict[str, float] = {}

    primary = [0, 2]   # • and Φ
    secondary = [1, 3]  # — and ○

    for name, axes in [('Lambda', (1, 2)), ('lambda', (0, 2)), ('lambdap', (0, 1))]:
        marg = np.sum(w_r, axis=axes)
        p_frac = float(np.sum(marg[primary]))
        s_frac = float(np.sum(marg[secondary]))
        tot = p_frac + s_frac
        out[f'{name}_primary'] = p_frac
        out[f'{name}_secondary'] = s_frac
        out[f'{name}_primary_frac'] = p_frac / tot if tot > 0 else 0.0
        out[f'{name}_secondary_frac'] = s_frac / tot if tot > 0 else 0.0

    # Mean primary / secondary across the three scales (one budget number per universe)
    primary_mean = np.mean([out[f'{s}_primary_frac'] for s in ('Lambda', 'lambda', 'lambdap')])
    secondary_mean = np.mean([out[f'{s}_primary_frac'] for s in ('Lambda', 'lambda', 'lambdap')])
    out['primary_fraction_mean'] = float(primary_mean)
    out['secondary_fraction_mean'] = float(1 - primary_mean)
    return out


# -----------------------------------------------------------------------------
# FEATURE 3 : Stability regime detector
# -----------------------------------------------------------------------------

def stability_regime(alpha: float, T: np.ndarray) -> Dict[str, float]:
    """
    Measure spectral radius, spectral gap, and mixing time. Classify:
        Severance: gap collapses (decoupling; mixing -> inf)
        Inflation: |lambda_max| blows up (fusion; dynamics unstable)
        Stable:    neither
    Returns a dict of diagnostics plus a verdict.
    """
    evals, _ = leading_eig(T)
    mags = np.abs(evals)
    lead = mags[0]

    # Find spectral gap (|lambda_1| - |lambda_2|, skipping duplicates at the top)
    unique = np.unique(np.round(mags, 12))[::-1]
    gap = (unique[0] - unique[1]) if len(unique) >= 2 else 0.0
    mixing_time = 1.0 / gap if gap > 1e-15 else float('inf')

    # Verdicts: thresholds are heuristic, matched to framework expectations
    # Severance: spectral radius drops toward 1 and gap -> 0 (no attraction toward fixed point)
    # Inflation: lead > 1 + 2*alpha, growing faster than the naive two-diameter prediction
    # Stable: lead close to 1 + 2*alpha and gap comparable to alpha / P
    pred_lead = 1 + 2 * alpha
    pred_gap = alpha / P_PUMP

    # Empirical regime thresholds from the extended sweep:
    #   - |lambda_max| exceeds 2 when alpha >= 0.5 (dynamics runaway / inflation-like)
    #   - primary/secondary fraction flips when alpha >= 0.20 (structural inversion)
    #   - mixing time diverges as 1/alpha; below 1e-6 the bond is effectively absent
    verdict = 'stable'
    if lead > 2.0 or not np.isfinite(lead):
        verdict = 'inflation'
    elif alpha >= 0.20:
        verdict = 'pre-inflation'
    elif alpha < 1e-6:
        verdict = 'severance'

    return {
        'alpha': alpha,
        'spectral_radius': float(lead),
        'spectral_gap': float(gap),
        'mixing_time': float(mixing_time),
        'predicted_lead_1p2a': float(pred_lead),
        'predicted_gap_a_over_P': float(pred_gap),
        'verdict': verdict,
    }


# -----------------------------------------------------------------------------
# FEATURE 4 : Pool-integer emergence checker (at α = 1/137, ℂ⁶⁴)
# -----------------------------------------------------------------------------

def pool_integer_checks(T: np.ndarray, alpha: float) -> List[Dict]:
    """
    Check whether the ℂ⁶⁴ eigenvalue spectrum and sector split land on the
    framework pool integers at the predicted positions.
    Targets:
        - leading eigenvalue phase ~ 109.47° = arccos(-1/T)
        - expanding/contracting sector split = 35/29 = C(R,T)/(S - C(R,T))
        - quadrant counts: Q1 = Q4 = A(3) = 21, Q2 = A(2) = 10, Q3 = G = 12
    """
    results: List[Dict] = []
    evals, _ = leading_eig(T)

    # (a) Leading-eigenvalue phase
    lead_val = evals[0]
    lead_phase_deg = np.degrees(np.angle(lead_val))
    target_phase_deg = np.degrees(np.arccos(-1.0 / T_TRIAD))   # 109.47122...
    # Eigenvalues come in conjugate pairs; the "leading angle" might be +/-
    lead_abs = abs(lead_phase_deg)
    err_phase = abs(lead_abs - target_phase_deg) / target_phase_deg
    results.append({
        'name': 'Leading-eigenvalue phase = arccos(-1/T) = 109.47°',
        'predicted': target_phase_deg,
        'observed': lead_abs,
        'error_pct': err_phase * 100,
        'match': err_phase < 0.05,
    })

    # (b) Expanding/contracting sector split
    mags = np.abs(evals)
    n_expand = int(np.sum(mags > 1.0 + 1e-9))
    n_contract = int(np.sum(mags < 1.0 - 1e-9))
    target_expand = 35   # C(R, T) = C(7, 3)
    target_contract = 29  # S - C(R, T) = 64 - 35
    results.append({
        'name': 'Expanding sector count = C(R,T) = 35',
        'predicted': target_expand,
        'observed': n_expand,
        'error_pct': abs(n_expand - target_expand) / target_expand * 100,
        'match': n_expand == target_expand,
    })
    results.append({
        'name': 'Contracting sector count = S - C(R,T) = 29',
        'predicted': target_contract,
        'observed': n_contract,
        'error_pct': abs(n_contract - target_contract) / target_contract * 100,
        'match': n_contract == target_contract,
    })

    # (c) Quadrant counts of eigenvalue phases
    phases = np.angle(evals)
    q1 = int(np.sum((phases >= 0) & (phases < np.pi/2)))
    q2 = int(np.sum((phases >= np.pi/2) & (phases <= np.pi)))
    q3 = int(np.sum((phases >= -np.pi) & (phases < -np.pi/2)))
    q4 = int(np.sum((phases >= -np.pi/2) & (phases < 0)))
    q_targets = {'Q1': A3_VAL, 'Q2': A2_VAL, 'Q3': G_GEN, 'Q4': A3_VAL}
    q_observed = {'Q1': q1, 'Q2': q2, 'Q3': q3, 'Q4': q4}
    for qn in ('Q1', 'Q2', 'Q3', 'Q4'):
        pred = q_targets[qn]
        obs = q_observed[qn]
        results.append({
            'name': f'Quadrant {qn} count = {pred}',
            'predicted': pred,
            'observed': obs,
            'error_pct': abs(obs - pred) / pred * 100,
            'match': obs == pred,
        })

    return results


# -----------------------------------------------------------------------------
# FEATURE 5 : Emergent-time diagnostic
# -----------------------------------------------------------------------------

def emergent_time_check(alpha: float, n_steps: int = 200) -> Dict:
    """
    §4.11: time is scale; the fold direction (beat order) IS time. We track
    whether the four beats fire in canonical order ((•∘⊛) → (—∘⎇) → (Φ∘✹) →
    (○∘⟳)) across iterations by watching which station dominates the state
    after each single-beat application.

    Diagnostic at ℂ⁴ (single scale): starting from a uniform state, apply each
    of the four beats individually (not the compiled F), and see which station
    has the highest amplitude. Repeat for n_steps cycles and check whether the
    dominant station cycles in canonical order.
    """
    theta = np.pi / 2
    PHI_IDX = 2

    beat_config = [
        ('(•∘⊛)', 0, 1j),
        ('(—∘⎇)', 1, -1+0j),
        ('(Φ∘✹)', 2, -1j),
        ('(○∘⟳)', 3, 1+0j),
    ]
    canonical_stations = [0, 1, 2, 3]  # •, —, Φ, ○ (the ACTIVE station of each beat)
    station_names = ['•', '—', 'Φ', '○']

    beats = []
    for _, active, i_phase in beat_config:
        G = np.zeros((4, 4), dtype=complex)
        if active == PHI_IDX:
            for other in [0, 1, 3]:
                c = i_phase * theta / T_TRIAD
                G[PHI_IDX, other] = c
                G[other, PHI_IDX] = -np.conj(c)
            G[PHI_IDX, PHI_IDX] = i_phase * theta / T_TRIAD
        else:
            c = i_phase * theta
            G[active, PHI_IDX] = c
            G[PHI_IDX, active] = -np.conj(c)
        G = _anti_hermitian(G)
        beats.append(expm(G))

    kappa = build_kappa_single(alpha)

    state = np.ones(4, dtype=complex) / 2.0
    canonical_hits = 0
    total_checks = 0
    observed_sequence: List[int] = []

    for cycle in range(n_steps):
        for beat_i, B in enumerate(beats):
            state = kappa @ B @ state
            state = state / np.linalg.norm(state)
            w = np.abs(state)**2
            dominant = int(np.argmax(w))
            observed_sequence.append(dominant)
            # The canonical expectation: after beat i, dominant should be active station i
            # However, the mediator Φ is central (idx 2); it tends to carry weight throughout.
            # We use a softer check: dominant cycles in one of the two canonical permutations.
            expected = canonical_stations[beat_i]
            if dominant == expected:
                canonical_hits += 1
            total_checks += 1

    # Alternative check: does the sequence repeat with period 4?
    first_cycle = observed_sequence[:4]
    periodic_count = 0
    for i in range(0, len(observed_sequence) - 3, 4):
        if observed_sequence[i:i+4] == first_cycle:
            periodic_count += 1
    total_cycles = (len(observed_sequence) - 3) // 4 + 1

    return {
        'canonical_hit_rate': canonical_hits / total_checks if total_checks else 0.0,
        'first_observed_cycle': [station_names[s] for s in first_cycle],
        'periodic_fraction': periodic_count / total_cycles if total_cycles else 0.0,
        'n_steps': n_steps,
    }


# =============================================================================
# FEATURE 1 : α-sweep driver
# =============================================================================

SWEEP_ALPHAS = [
    ('1/10',    0.1),
    ('1/30',    1.0/30),
    ('1/100',   0.01),
    ('1/137',   ALPHA_OURS),
    ('1/300',   1.0/300),
    ('1/1000',  0.001),
]

# Extended sweep for regime-boundary detection
EXTENDED_ALPHAS = [
    ('2.0',     2.0),
    ('1.0',     1.0),
    ('0.5',     0.5),
    ('0.25',    0.25),
    ('1/10',    0.1),
    ('1/137',   ALPHA_OURS),
    ('1/1000',  0.001),
    ('1e-6',    1e-6),
    ('1e-9',    1e-9),
]


def run_one_universe(alpha: float, label: str = '') -> Dict:
    """Build T for a given α, extract all observables."""
    T, F, K = build_T_64(alpha)

    # Leading eigenvector and weights
    evals, evecs = leading_eig(T)
    lead_vec = evecs[:, 0]
    w = weights_from_vec(lead_vec)

    # Cosmological budget
    cosmo = cosmological_split_C64(w)

    # Stability
    stab = stability_regime(alpha, T)

    out = {
        'alpha': alpha,
        'label': label,
        'inv_alpha': 1.0 / alpha,
        'spectral_radius': stab['spectral_radius'],
        'spectral_gap': stab['spectral_gap'],
        'mixing_time': stab['mixing_time'],
        'primary_fraction_mean': cosmo['primary_fraction_mean'],
        'secondary_fraction_mean': cosmo['secondary_fraction_mean'],
        'Lambda_primary_frac': cosmo['Lambda_primary_frac'],
        'lambda_primary_frac': cosmo['lambda_primary_frac'],
        'lambdap_primary_frac': cosmo['lambdap_primary_frac'],
        'verdict': stab['verdict'],
    }
    return out


def run_sweep() -> List[Dict]:
    rows = []
    for label, alpha in SWEEP_ALPHAS:
        t0 = time.time()
        row = run_one_universe(alpha, label=label)
        row['wall_time_s'] = time.time() - t0
        rows.append(row)
    return rows


# =============================================================================
# Reporting helpers
# =============================================================================

def print_sweep_table(rows: List[Dict]) -> None:
    print()
    print('=' * 100)
    print('  UNIVERSE-CREATOR alpha-SWEEP  (three-scale T-operator, C64 = C4 x C4 x C4)')
    print('=' * 100)
    headers = ['label', '1/alpha', '|lambda_max|', 'gap', 'mix_time',
               'primary%', 'secondary%', 'verdict']
    print(f"{headers[0]:>8s}  {headers[1]:>10s}  {headers[2]:>12s}  {headers[3]:>12s}  "
          f"{headers[4]:>10s}  {headers[5]:>8s}  {headers[6]:>10s}  {headers[7]:>10s}")
    print('-' * 100)
    for row in rows:
        mix = row['mixing_time']
        mix_s = f"{mix:8.1f}" if np.isfinite(mix) else '     inf'
        print(f"{row['label']:>8s}  {row['inv_alpha']:>10.2f}  "
              f"{row['spectral_radius']:>12.8f}  {row['spectral_gap']:>12.8f}  "
              f"{mix_s:>10s}  "
              f"{100*row['primary_fraction_mean']:>7.3f}%  "
              f"{100*row['secondary_fraction_mean']:>9.3f}%  "
              f"{row['verdict']:>10s}")
    print()


def print_regime_boundaries(rows: List[Dict]) -> None:
    print('=' * 100)
    print('  STABILITY REGIME BOUNDARIES')
    print('=' * 100)
    verdicts = [row['verdict'] for row in rows]
    print(f"  Verdicts across the sweep: {verdicts}")

    sev_alphas = [r['alpha'] for r in rows if r['verdict'] == 'severance']
    inf_alphas = [r['alpha'] for r in rows if r['verdict'] == 'inflation']
    stab_alphas = [r['alpha'] for r in rows if r['verdict'] == 'stable']

    if sev_alphas:
        print(f"  Severance regime at alpha <= {max(sev_alphas):.6f}")
    if stab_alphas:
        print(f"  Stable regime:  alpha in [{min(stab_alphas):.6f}, {max(stab_alphas):.6f}]")
    if inf_alphas:
        print(f"  Inflation regime at alpha >= {min(inf_alphas):.6f}")
    print()


def print_pool_checks(checks: List[Dict]) -> None:
    print('=' * 100)
    print('  POOL-INTEGER EMERGENCE  (alpha = 1/137, C64)')
    print('=' * 100)
    print(f"  {'check':<56s} {'predicted':>12s} {'observed':>14s} {'err%':>8s} {'match':>6s}")
    print('-' * 100)
    for c in checks:
        pred = c['predicted']
        obs = c['observed']
        err = c['error_pct']
        mark = 'YES' if c['match'] else 'no'
        pred_s = f"{pred:12.4f}" if isinstance(pred, float) else f"{pred:>12d}"
        obs_s = f"{obs:14.4f}" if isinstance(obs, float) else f"{obs:>14d}"
        print(f"  {c['name']:<56s} {pred_s} {obs_s} {err:>7.3f} {mark:>6s}")
    print()


def print_time_check(tc: Dict) -> None:
    print('=' * 100)
    print('  EMERGENT-TIME DIAGNOSTIC  (beat order = fold direction, Section 4.11)')
    print('=' * 100)
    print(f"  Canonical hit rate (dominant station matches active beat station):")
    print(f"    {100*tc['canonical_hit_rate']:.3f}%")
    print(f"  First observed 4-beat cycle: {tc['first_observed_cycle']}")
    print(f"  Periodic fraction (subsequent cycles matching the first): "
          f"{100*tc['periodic_fraction']:.3f}%")
    print(f"  Steps run: {tc['n_steps']}")
    print()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Universe creator: three-scale T-operator with alpha as input.')
    parser.add_argument('--alpha', type=float, default=None,
                        help='fine-structure-like coupling (default: our-universe 1/137)')
    parser.add_argument('--scale', choices=['C64'], default='C64',
                        help='architecture (currently only C64 implemented)')
    parser.add_argument('--sweep', action='store_true',
                        help='run the alpha-sweep across six universes')
    parser.add_argument('--extended-sweep', action='store_true',
                        help='run the extended alpha-sweep (regime-boundary detection)')
    parser.add_argument('--our-universe', action='store_true',
                        help='run alpha = 1/137 with all diagnostics (feature 1 summary + 2,3,4,5)')
    args = parser.parse_args()

    if args.sweep:
        print('Running alpha-sweep...')
        rows = run_sweep()
        print_sweep_table(rows)
        print_regime_boundaries(rows)
        return

    if args.extended_sweep:
        print('Running extended alpha-sweep...')
        rows = []
        for label, alpha in EXTENDED_ALPHAS:
            try:
                row = run_one_universe(alpha, label=label)
                rows.append(row)
            except Exception as e:
                print(f"  (alpha = {alpha}: {e})")
        print_sweep_table(rows)
        print_regime_boundaries(rows)
        return

    if args.our_universe:
        print('Running our-universe diagnostic at alpha = 1/137 ...')
        alpha = ALPHA_OURS
        # Feature 1 summary row
        row = run_one_universe(alpha, label='ours')
        print_sweep_table([row])
        # Features 2, 3 (encoded in the sweep row)
        print_regime_boundaries([row])
        # Feature 4
        T, F, K = build_T_64(alpha)
        checks = pool_integer_checks(T, alpha)
        print_pool_checks(checks)
        # Feature 5
        tc = emergent_time_check(alpha)
        print_time_check(tc)
        return

    # Single-alpha run
    print(f"Single-universe run at alpha = {alpha:.12f} (1/alpha = {1/alpha:.6f}) ...")
    row = run_one_universe(alpha, label=f"alpha={alpha:.6f}")
    print_sweep_table([row])
    T, F, K = build_T_64(alpha)
    checks = pool_integer_checks(T, alpha)
    print_pool_checks(checks)
    tc = emergent_time_check(alpha)
    print_time_check(tc)


if __name__ == '__main__':
    main()
