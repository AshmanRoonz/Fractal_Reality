"""
T-operator at ℂ⁵¹² : Three-Scale Octave
========================================

The three-scale octave: F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈, three nested circumpuncts
each carrying the full 8-station dimensional octave (•, ⊛, —, ⎇, Φ, ✹, ○, ⟳).

    ⊙Λ (greater whole) × ⊙λ (self) × ⊙λ' (parts)

Each ⊙ has 8 internal stations (full octave = four structural + four
processual, the P·V+R+Φ+T = (T+1)³ closure at single scale resolution).

    8³ = 512 composite states.

Construction principle:
    T₅₁₂ = κ₅₁₂ ∘ (F₈ ⊗ F₈ ⊗ F₈)

A3 at octave resolution: same operator at every scale, coupling via α.

Predictions to verify (§27.7s at three-scale octave resolution):
    1. Phase sum = 0 exactly (tensor-product closure; 192·(-π/3) ≡ 0 mod 2π)
    2. Cosmological 69/31 split survives at 512-state resolution
    3. Expanding/contracting sector split (analogue of ℂ⁶⁴'s 35/29)
    4. Leading eigenvalue at the tetrahedral angle 109.47° (or new angle)
    5. Spectral gap scaling (ℂ⁴: α, ℂ⁸: α/P, ℂ⁶⁴: α/P, ℂ⁵¹² : ?)
    6. A3 consistency: outer and inner scales identical to machine precision
    7. Top states: does the full aperture-field alternation dominate?

Author: Ashman Roonz & Claude
Date: April 2026
"""

import numpy as np
from scipy.linalg import expm
from typing import Dict, List, Tuple
import time


# ═══════════════════════════════════════════════════════════════
# Framework constants
# ═══════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
T_TRIAD = 3
P_PUMP = 4
R_RUNGS = T_TRIAD**2 - 2          # 7
V_GEN_PLUS = P_PUMP * T_TRIAD + 1  # 13
SU3 = T_TRIAD**2 - 1              # 8
S_STATES = (T_TRIAD + 1)**T_TRIAD  # 64
G_GEN = T_TRIAD * (T_TRIAD + 1)    # 12
A3 = T_TRIAD * (2*T_TRIAD + 1)     # 21


def solve_alpha() -> float:
    """α from 1/α = 360/φ² − 2/φ³ + α/(59/3) via the quadratic in α."""
    a = 1.0
    b = -(360 / PHI**2 - 2 / PHI**3)
    c = -3.0 / 59.0
    disc = b**2 - 4*a*c
    x = (-b + np.sqrt(disc)) / (2*a)
    return 1.0 / x


ALPHA = solve_alpha()


# ═══════════════════════════════════════════════════════════════
# ℂ⁸ full octave (the single-scale F operator)
# Stations: 0(•) 1(⊛) 2(—) 3(⎇) 4(Φ) 5(✹) 6(○) 7(⟳)
# Φ at index 4 (structural), ✹ at index 5 (processual)
# ═══════════════════════════════════════════════════════════════

STATION_NAMES_8 = ['•', '⊛', '—', '⎇', 'Φ', '✹', '○', '⟳']
STRUCT_IDX_8 = [0, 2, 4, 6]  # integer-D stations
PROC_IDX_8   = [1, 3, 5, 7]  # half-integer-D stations
PHI_S_IDX    = 4              # Φ (structural)
PHI_P_IDX    = 5              # ✹ (processual)


def _anti_hermitian(G: np.ndarray) -> np.ndarray:
    return (G - np.conj(G.T)) / 2


def build_F_8_octave() -> np.ndarray:
    """
    Build F₈ for a single ⊙ carrying the full octave (8 stations).

    Four beats, each pairs a structural station (s_idx) with its processual
    partner (p_idx) via ∘, and Φ (structural) and ✹ (processual) are the
    central mediators each beat couples through.
    """
    theta = np.pi / 2
    i_phases = [1j, -1+0j, -1j, 1+0j]  # i¹, i², i³, i⁰

    beats = []
    for (s_idx, p_idx, i_phase) in zip(STRUCT_IDX_8, PROC_IDX_8, i_phases):
        Gm = np.zeros((8, 8), dtype=complex)
        # Internal structure-process coupling for this beat
        Gm[s_idx, p_idx] = i_phase * theta
        Gm[p_idx, s_idx] = -np.conj(i_phase * theta)

        if s_idx == PHI_S_IDX:
            # Φ-beat: Φ mediates among the other structural stations;
            # ✹ mediates among the other processual stations
            for other_s in [0, 2, 6]:
                c = i_phase * theta / T_TRIAD
                Gm[PHI_S_IDX, other_s] = c
                Gm[other_s, PHI_S_IDX] = -np.conj(c)
            Gm[PHI_S_IDX, PHI_S_IDX] = i_phase * theta / T_TRIAD
            for other_p in [1, 3, 7]:
                c = i_phase * theta / T_TRIAD
                Gm[PHI_P_IDX, other_p] = c
                Gm[other_p, PHI_P_IDX] = -np.conj(c)
            Gm[PHI_P_IDX, PHI_P_IDX] = i_phase * theta / T_TRIAD
        else:
            # Non-Φ beat: active station couples through Φ (structural)
            # and active's processual partner couples through ✹
            Gm[s_idx, PHI_S_IDX] = i_phase * theta
            Gm[PHI_S_IDX, s_idx] = -np.conj(i_phase * theta)
            Gm[p_idx, PHI_P_IDX] = i_phase * theta
            Gm[PHI_P_IDX, p_idx] = -np.conj(i_phase * theta)

        Gm = _anti_hermitian(Gm)
        beats.append(expm(Gm))

    F = np.eye(8, dtype=complex)
    for B in beats:
        F = B @ F
    return F


def build_kappa_8_intra() -> np.ndarray:
    """
    Intra-scale κ₈: the four diameter bonds within a single ⊙.

    •↔Φ (structural diameter 1): (0, 4)
    —↔○ (structural diameter 2): (2, 6)
    ⊛↔✹ (processual diameter 1): (1, 5)
    ⎇↔⟳ (processual diameter 2): (3, 7)
    """
    k = np.eye(8, dtype=complex)
    k[0, 4] = k[4, 0] = ALPHA   # •↔Φ
    k[2, 6] = k[6, 2] = ALPHA   # —↔○
    k[1, 5] = k[5, 1] = ALPHA   # ⊛↔✹
    k[3, 7] = k[7, 3] = ALPHA   # ⎇↔⟳
    return k


# ═══════════════════════════════════════════════════════════════
# ℂ⁵¹² construction
# State ordering: |i, j, k⟩ with i = Λ station, j = λ, k = λ'
# Index = i·64 + j·8 + k  (8³ = 512)
# ═══════════════════════════════════════════════════════════════

def idx512(i: int, j: int, k: int) -> int:
    return i * 64 + j * 8 + k


def build_F_512() -> np.ndarray:
    """F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈ (A3: same operator at every scale)."""
    F8 = build_F_8_octave()
    return np.kron(np.kron(F8, F8), F8)


def build_kappa_512() -> np.ndarray:
    """
    κ₅₁₂: intra-scale diameters (within each of three ⊙s) plus cross-scale
    coupling between adjacent scales (Λ↔λ and λ↔λ', strength α) plus a skip
    coupling (Λ↔λ', strength α², two nesting steps).

    Cross-scale κ_{p,q}: couples diameter partners across scales at the same
    octave position (•_λ ↔ Φ_Λ, —_λ ↔ ○_Λ, ⊛_λ ↔ ✹_Λ, ⎇_λ ↔ ⟳_Λ) by direct
    extension of the ℂ⁴ construction's (•,Φ) and (—,○) primary entries.
    """
    dim = 512
    kappa = np.eye(dim, dtype=complex)

    I8 = np.eye(8, dtype=complex)
    k8_intra = build_kappa_8_intra()

    # 1. INTRA-SCALE diameters (within each ⊙)
    # Λ-diameters:  κ₈ ⊗ I ⊗ I
    # λ-diameters:  I ⊗ κ₈ ⊗ I
    # λ'-diameters: I ⊗ I ⊗ κ₈
    intra_L = np.kron(np.kron(k8_intra, I8), I8)
    intra_S = np.kron(np.kron(I8, k8_intra), I8)
    intra_P = np.kron(np.kron(I8, I8), k8_intra)

    for intra in (intra_L, intra_S, intra_P):
        off = intra - np.diag(np.diag(intra))  # off-diagonal part only
        kappa += off

    # 2. CROSS-SCALE coupling matrix (8×8 between adjacent scales)
    # Same diameter pairs as intra, but now coupling a station of the part
    # to its diameter partner on the whole.
    cross = np.zeros((8, 8), dtype=complex)
    for (a, b) in [(0, 4), (4, 0), (2, 6), (6, 2),
                   (1, 5), (5, 1), (3, 7), (7, 3)]:
        cross[a, b] = ALPHA

    # Λ-λ adjacent coupling: i (Λ-station) ↔ j (λ-station) by cross[j, i]
    for i_L in range(8):
        for j_S in range(8):
            c = cross[j_S, i_L]
            if abs(c) < 1e-15:
                continue
            for k_P in range(8):  # λ' spectates
                a_idx = idx512(i_L, j_S, k_P)
                b_idx = idx512(j_S, i_L, k_P)
                if a_idx != b_idx:
                    kappa[a_idx, b_idx] += c
                    kappa[b_idx, a_idx] += c

    # λ-λ' adjacent coupling: j (λ-station) ↔ k (λ'-station) by cross[k, j]
    for j_S in range(8):
        for k_P in range(8):
            c = cross[k_P, j_S]
            if abs(c) < 1e-15:
                continue
            for i_L in range(8):  # Λ spectates
                a_idx = idx512(i_L, j_S, k_P)
                b_idx = idx512(i_L, k_P, j_S)
                if a_idx != b_idx:
                    kappa[a_idx, b_idx] += c
                    kappa[b_idx, a_idx] += c

    # Λ-λ' skip coupling at α² (two nesting steps)
    for i_L in range(8):
        for k_P in range(8):
            c = cross[k_P, i_L] * ALPHA  # α × α = α²
            if abs(c) < 1e-15:
                continue
            for j_S in range(8):  # λ spectates
                a_idx = idx512(i_L, j_S, k_P)
                b_idx = idx512(k_P, j_S, i_L)
                if a_idx != b_idx:
                    kappa[a_idx, b_idx] += c
                    kappa[b_idx, a_idx] += c

    return kappa


def build_T_512() -> np.ndarray:
    return build_kappa_512() @ build_F_512()


# ═══════════════════════════════════════════════════════════════
# Analysis
# ═══════════════════════════════════════════════════════════════

def leading_eigenvector(T: np.ndarray) -> Tuple[complex, np.ndarray]:
    """
    Extract the leading eigenvector (largest |λ|) directly via eig,
    bypassing power-iteration convergence (which is slow at α/P spectral gap).
    """
    evals, evecs = np.linalg.eig(T)
    order = np.argsort(-np.abs(evals))
    lead_val = evals[order[0]]
    lead_vec = evecs[:, order[0]]
    return lead_val, lead_vec


def weights_from_vector(v: np.ndarray) -> np.ndarray:
    w = np.abs(v)**2
    return w / np.sum(w)


def scale_decomposition_512(w: np.ndarray) -> Dict:
    """Marginals by scale and station type."""
    w_r = w.reshape(8, 8, 8)

    out = {}
    for scale_name, axes_to_sum in [('Λ', (1, 2)), ('λ', (0, 2)), ("λ'", (0, 1))]:
        marg = np.sum(w_r, axis=axes_to_sum)
        out[f'{scale_name}_by_station'] = {STATION_NAMES_8[i]: float(marg[i]) for i in range(8)}
        out[f'{scale_name}_struct'] = float(np.sum(marg[STRUCT_IDX_8]))
        out[f'{scale_name}_proc']   = float(np.sum(marg[PROC_IDX_8]))
        out[f'{scale_name}_marginal'] = marg
    return out


def primary_secondary_diameter_split(w: np.ndarray) -> Dict:
    """
    Cosmological-reading split on the diameter basis.

    Primary diameter (structural): •+Φ at every scale, stations {0, 4} in 8-space.
    Secondary diameter (structural): —+○ at every scale, stations {2, 6}.
    Processual diameters: ⊛+✹ at {1, 5}, ⎇+⟳ at {3, 7}.

    The cosmological 69/31 reading (v11 ℂ⁶⁴) landed on primary vs secondary
    at four-station resolution. At eight stations we have four diameters;
    report each.
    """
    w_r = w.reshape(8, 8, 8)

    diameter_stations = {
        'D1 (•+Φ)':  [0, 4],
        'D2 (—+○)':  [2, 6],
        'D3 (⊛+✹)':  [1, 5],
        'D4 (⎇+⟳)':  [3, 7],
    }

    out = {}
    for name, stations in diameter_stations.items():
        # Weight of states where ALL three scales are in this diameter
        w_diag = 0.0
        for s1 in stations:
            for s2 in stations:
                for s3 in stations:
                    w_diag += w_r[s1, s2, s3]
        out[name] = float(w_diag)
    out['primary_D1_D3'] = out['D1 (•+Φ)'] + out['D3 (⊛+✹)']
    out['secondary_D2_D4'] = out['D2 (—+○)'] + out['D4 (⎇+⟳)']
    return out


def search_framework_constants(values: List[Tuple[str, float]], tol: float = 0.01) -> List[Dict]:
    """Match a list of (label, value) pairs against the framework integer/ratio pool."""
    targets = {
        'α': ALPHA, '1/α': 1/ALPHA, 'α²': ALPHA**2, '2α': 2*ALPHA,
        'φ': PHI, '1/φ': 1/PHI, 'φ²': PHI**2, '1/φ²': 1/PHI**2,
        'π': np.pi, 'π/2': np.pi/2, 'π/3': np.pi/3, 'π/6': np.pi/6, 'π/4': np.pi/4,
        '-π/3': -np.pi/3, '-π/6': -np.pi/6,
        'T': 3, 'P': 4, 'Φ+○': 5, 'R': 7, 'SU3': 8, 'G': 12, 'V': 13, 'A(3)': 21,
        '1/T': 1/3, '1/P': 1/4, '1/R': 1/7, '1/G': 1/12, '1/V': 1/13, '1/SU3': 1/8,
        'T/P': 3/4, 'R/T²': 7/9, 'V/(V-1)': 13/12,
        '◐': 0.5,
        '109.47°_rad': np.radians(109.47),
        '90°_rad': np.radians(90),
        '120°_rad': np.radians(120),
        'DE=0.691': 0.6911, 'matter=0.309': 0.3089, '69/31': 69/31,
        'C(R,T)=35': 35, 'S-C(R,T)=29': 29, '35/29': 35/29,
    }
    out = []
    for label, val in values:
        for tname, tval in targets.items():
            if tval == 0:
                continue
            err = abs(val - tval) / max(abs(tval), 1e-12)
            if err < tol:
                out.append({'source': label, 'value': val, 'match': tname,
                            'target': tval, 'error_pct': err * 100})
    out.sort(key=lambda x: x['error_pct'])
    return out


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 74)
    print("  T-OPERATOR AT ℂ⁵¹² : THREE-SCALE OCTAVE")
    print("  F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈   (8³ = 512 states)")
    print("=" * 74)
    print(f"  α  = {ALPHA:.12f}  (1/α = {1/ALPHA:.9f})")
    print(f"  φ  = {PHI:.10f}")
    print()

    # ───────────────────────────────────────────────────────────
    print("Building F₅₁₂  (F₈ ⊗ F₈ ⊗ F₈)...")
    t0 = time.time()
    F512 = build_F_512()
    print(f"  F₅₁₂ shape: {F512.shape}, built in {time.time()-t0:.2f}s")

    unit_err = np.linalg.norm(F512.conj().T @ F512 - np.eye(512))
    print(f"  F unitarity error: {unit_err:.2e}")

    print()
    print("Building κ₅₁₂  (intra-scale + adjacent cross-scale + skip)...")
    t0 = time.time()
    K512 = build_kappa_512()
    print(f"  κ₅₁₂ shape: {K512.shape}, built in {time.time()-t0:.2f}s")
    off_count = np.count_nonzero(np.abs(K512 - np.diag(np.diag(K512))) > 1e-15)
    print(f"  κ off-diagonal non-zero entries: {off_count}")

    print()
    print("Building T₅₁₂ = κ₅₁₂ @ F₅₁₂ ...")
    t0 = time.time()
    T512 = K512 @ F512
    print(f"  T₅₁₂ shape: {T512.shape}, built in {time.time()-t0:.2f}s")

    # ───────────────────────────────────────────────────────────
    print()
    print("=" * 74)
    print("  EIGENSPECTRUM")
    print("=" * 74)
    t0 = time.time()
    evals, evecs = np.linalg.eig(T512)
    print(f"  eig() finished in {time.time()-t0:.2f}s")
    order = np.argsort(-np.abs(evals))
    evals = evals[order]
    evecs = evecs[:, order]

    mags = np.abs(evals)
    print(f"  Spectral radius (max |λ|): {np.max(mags):.12f}")
    print(f"  Min |λ|:                    {np.min(mags):.12f}")

    det_T = np.linalg.det(T512)
    det_arg = np.angle(det_T)
    phase_sum = float(np.sum(np.angle(evals)))
    # phase_sum is only defined modulo 2π; bring it into (-π, π]
    phase_mod = (phase_sum + np.pi) % (2*np.pi) - np.pi

    print(f"  det(T):                     {det_T:+.6e}")
    print(f"  arg(det(T)):                {det_arg:+.10f}  ({det_arg/np.pi:+.6f}π)")
    print(f"  Σ arg(λ) (raw):             {phase_sum:+.10f}  ({phase_sum/np.pi:+.6f}π)")
    print(f"  Σ arg(λ) (mod 2π):          {phase_mod:+.10f}  ({phase_mod/np.pi:+.6f}π)")
    print(f"  Prediction: 0 exactly  (192·(-π/3) mod 2π = 0)")

    # Spectral gap (1 - second-largest magnitude)
    unique_mags = np.unique(np.round(mags, 10))[::-1]
    if len(unique_mags) >= 2:
        gap = unique_mags[0] - unique_mags[1]
        print(f"  Spectral gap (|λ₁| - |λ₂|): {gap:.10f}  (α/P = {ALPHA/P_PUMP:.10f})")
        print(f"    ratio gap / (α/P): {gap / (ALPHA/P_PUMP):.4f}")

    print(f"  Unique |λ|: {len(unique_mags)}")
    print(f"  Top 10 unique magnitudes and their degeneracy:")
    for m in unique_mags[:10]:
        count = int(np.sum(np.abs(mags - m) < 1e-8))
        print(f"    |λ| = {m:.10f}   (degeneracy {count})")

    # Expanding / contracting sector
    n_expand = int(np.sum(mags > 1.0 + 1e-10))
    n_contract = int(np.sum(mags < 1.0 - 1e-10))
    n_unit = 512 - n_expand - n_contract
    print(f"\n  Sector split: {n_expand} expanding, {n_unit} unit, {n_contract} contracting")
    print(f"    Ratio expanding/contracting: {n_expand}/{n_contract}")
    if n_contract > 0:
        print(f"    = {n_expand/n_contract:.6f}")
        # Compare against C(R,T)/(S-C(R,T)) = 35/29 from ℂ⁶⁴
        print(f"    C(R,T)/(S-C(R,T)) = 35/29 = {35/29:.6f}  (ℂ⁶⁴ reference)")

    # ───────────────────────────────────────────────────────────
    print()
    print("=" * 74)
    print("  LEADING EIGENVECTOR (fixed point)")
    print("=" * 74)
    lead_val = evals[0]
    lead_vec = evecs[:, 0]
    w = weights_from_vector(lead_vec)
    print(f"  Leading eigenvalue: {lead_val:.10f}")
    print(f"  |lead|: {abs(lead_val):.10f}  = 1 + {(abs(lead_val)-1):.6e}")
    print(f"  arg(lead): {np.angle(lead_val):.10f} rad  ({np.degrees(np.angle(lead_val)):.6f}°)")
    print(f"  Tetrahedral angle: 109.47122°  (ℂ⁶⁴ reference)")

    # Scale decomposition
    print()
    print("  SCALE DECOMPOSITION (structural vs processual per scale)")
    decomp = scale_decomposition_512(w)
    for scale_name in ['Λ', 'λ', "λ'"]:
        s = decomp[f'{scale_name}_struct']
        p = decomp[f'{scale_name}_proc']
        print(f"    {scale_name:3s}: structural = {s:.8f}   processual = {p:.8f}   (sum = {s+p:.8f})")

    # A3 consistency: outer (Λ) and inner (λ') should be identical
    diff_outer_inner = np.linalg.norm(decomp['Λ_marginal'] - decomp["λ'_marginal"])
    diff_outer_mid   = np.linalg.norm(decomp['Λ_marginal'] - decomp['λ_marginal'])
    diff_mid_inner   = np.linalg.norm(decomp['λ_marginal'] - decomp["λ'_marginal"])
    print()
    print("  A3 CONSISTENCY (same operator at every scale ⇒ same marginal)")
    print(f"    Λ vs λ' (outer vs inner):  L2 distance = {diff_outer_inner:.2e}")
    print(f"    Λ vs λ  (outer vs middle): L2 distance = {diff_outer_mid:.2e}")
    print(f"    λ vs λ' (middle vs inner): L2 distance = {diff_mid_inner:.2e}")
    print(f"    (v11 ℂ⁶⁴: outer/inner identical to machine precision;")
    print(f"     middle α-enriched by ~0.069%)")

    # Per-station at one scale
    print()
    print("  Λ-scale station distribution:")
    for sn, val in decomp['Λ_by_station'].items():
        bar = '#' * int(val * 200)
        print(f"    {sn}: {val:.8f}  [{bar}]")

    # Primary vs secondary diameter split
    print()
    print("  DIAMETER DECOMPOSITION (cosmological-reading at three-scale octave)")
    diam = primary_secondary_diameter_split(w)
    print(f"    D1 (•+Φ, structural 1): {diam['D1 (•+Φ)']:.8f}")
    print(f"    D2 (—+○, structural 2): {diam['D2 (—+○)']:.8f}")
    print(f"    D3 (⊛+✹, processual 1): {diam['D3 (⊛+✹)']:.8f}")
    print(f"    D4 (⎇+⟳, processual 2): {diam['D4 (⎇+⟳)']:.8f}")
    print(f"    Sum (all-diameter alignment): {sum(diam[k] for k in ('D1 (•+Φ)','D2 (—+○)','D3 (⊛+✹)','D4 (⎇+⟳)')):.8f}")
    print()
    print(f"    Primary  (D1 + D3) = {diam['primary_D1_D3']:.8f}")
    print(f"    Secondary(D2 + D4) = {diam['secondary_D2_D4']:.8f}")
    total = diam['primary_D1_D3'] + diam['secondary_D2_D4']
    if total > 0:
        p_frac = diam['primary_D1_D3'] / total
        s_frac = diam['secondary_D2_D4'] / total
        print(f"    Primary fraction:   {p_frac:.6f}   (ℂ⁶⁴ ref: 0.6853)")
        print(f"    Secondary fraction: {s_frac:.6f}   (cosmic DE: 0.6911)")

    # ───────────────────────────────────────────────────────────
    # Top weighted states
    print()
    print("  TOP 10 MOST WEIGHTED STATES")
    top_idx = np.argsort(-w)[:10]
    for rank, idx in enumerate(top_idx):
        i_L = idx // 64
        j_S = (idx % 64) // 8
        k_P = idx % 8
        print(f"    #{rank+1}: |{STATION_NAMES_8[i_L]:2s}, {STATION_NAMES_8[j_S]:2s}, {STATION_NAMES_8[k_P]:2s}⟩  w = {w[idx]:.8f}")

    # ───────────────────────────────────────────────────────────
    print()
    print("=" * 74)
    print("  FRAMEWORK CONSTANT SEARCH (leading eigenvalue + diameter fractions)")
    print("=" * 74)
    candidates = [
        ('|lead_val|', abs(lead_val)),
        ('|lead_val| - 1', abs(lead_val) - 1),
        ('arg(lead_val)_rad', float(np.angle(lead_val))),
        ('spectral_gap', unique_mags[0] - unique_mags[1] if len(unique_mags) >= 2 else 0.0),
        ('primary_fraction', diam['primary_D1_D3'] / total if total > 0 else 0.0),
        ('secondary_fraction', diam['secondary_D2_D4'] / total if total > 0 else 0.0),
        ('Λ_struct', decomp['Λ_struct']),
        ('Λ_proc', decomp['Λ_proc']),
        ('phase_mod/π', phase_mod / np.pi),
        ('det_arg/π', det_arg / np.pi),
    ]
    matches = search_framework_constants(candidates, tol=0.02)
    if matches:
        for m in matches[:20]:
            print(f"  {m['source']:25s} = {m['value']:+.8f}")
            print(f"     ≈ {m['match']:15s} = {m['target']:+.8f}   (error: {m['error_pct']:.4f}%)")
    else:
        print("  No matches within 2% tolerance.")

    # ───────────────────────────────────────────────────────────
    print()
    print("=" * 74)
    print("  CROSS-CHECK: power iteration from uniform state")
    print("=" * 74)
    print("  (comparison with eig-based leading vector)")
    n_iter = 50000
    print(f"  Running {n_iter} iterations...")
    t0 = time.time()
    state = np.ones(512, dtype=complex) / np.sqrt(512)
    for _ in range(n_iter):
        state = T512 @ state
        nrm = np.linalg.norm(state)
        if nrm > 0:
            state = state / nrm
    dt_iter = time.time() - t0
    print(f"  Power iteration finished in {dt_iter:.1f}s")
    w_iter = weights_from_vector(state)
    overlap = abs(np.vdot(state / np.linalg.norm(state),
                          lead_vec / np.linalg.norm(lead_vec)))
    print(f"  |⟨power_iter | eig_leading⟩| = {overlap:.6f}   (1.0 = exact agreement)")
    decomp_iter = scale_decomposition_512(w_iter)
    print(f"  Power-iter Λ structural: {decomp_iter['Λ_struct']:.6f}  (eig: {decomp['Λ_struct']:.6f})")
    print(f"  Power-iter Λ processual: {decomp_iter['Λ_proc']:.6f}  (eig: {decomp['Λ_proc']:.6f})")

    print()
    print("=" * 74)
    print("  DONE")
    print("=" * 74)


if __name__ == '__main__':
    main()
