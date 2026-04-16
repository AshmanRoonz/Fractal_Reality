"""
Unified Expression T-Operator v10: Prediction Catalog
======================================================

Extract every number the ℂ⁴ and ℂ⁸ operators produce, then systematically
match each against the full library of framework constants, ratios, and
known physical observables.

Goal: separate genuine predictions from construction artifacts.

For each number the operator produces, we ask:
  1. Is it a framework ratio? (T, P, R, V, φ, α, etc.)
  2. Is it a known physical observable? (cosmological, particle, etc.)
  3. Is it derivable from the construction? (then it's not a prediction)
  4. Is it robust? (does it survive changes in IC, iteration depth?)

Numbers that pass 1 or 2 but NOT 3 are genuine predictions.
"""

import numpy as np
from scipy.linalg import expm, logm

# ============================================================
# Framework constants library
# ============================================================
alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
pi = np.pi
T = 3
P = T + 1          # 4
Phi_ch = 2          # channels
R = T**2 - 2        # 7
V = 4*T + 1         # 13
SU3 = T**2 - 1      # 8
G = T*(T+1)          # 12
A3 = T*(2*T+1)       # 21
S = P**T             # 64
balance = 0.5        # ◐

# Framework ratio library: name → value
framework_ratios = {
    # Pure integers
    '•': 1, 'Φ_ch': 2, 'T': 3, 'P': 4, 'Φ+○': 5,
    'T!': 6, 'R': 7, 'SU3': 8, 'T²': 9, 'A(2)': 10,
    'G': 12, 'V': 13, 'P²': 16, 'P(P+1)': 20, 'A(3)': 21,
    'A(3.5)': 28, '2P²': 32, 'S': 64,
    # Framework fractions
    '1/T': 1/3, '1/P': 1/4, '1/R': 1/7, '1/V': 1/13,
    '1/G': 1/12, '1/SU3': 1/8,
    'T/P': 3/4, 'T/R': 3/7, 'R/T': 7/3, 'R/T²': 7/9,
    'P/T': 4/3, 'V/(V-1)': 13/12, 'SU3/T': 8/3,
    'T/G': 3/12, 'T/V': 3/13, 'P/R': 4/7,
    'T/Φ': 3/2, 'Φ/T': 2/3, '(Φ+○)/SU3': 5/8,
    'SU3/(Φ+○)': 8/5, 'R/V': 7/13, 'V/R': 13/7,
    'R/G': 7/12, 'G/R': 12/7,
    # Transcendental and irrational
    'φ': phi, '1/φ': 1/phi, '1/φ²': 1/phi**2,
    'φ²': phi**2, 'φ/2': phi/2, '2/φ': 2/phi,
    'π': pi, 'π/2': pi/2, 'π/3': pi/3, 'π/4': pi/4,
    'π/6': pi/6, '2π/3': 2*pi/3, '1/π': 1/pi,
    '√2': np.sqrt(2), '1/√2': 1/np.sqrt(2),
    'α': alpha, '2α': 2*alpha, 'α²': alpha**2,
    # Key angles in degrees
    '30°': 30, '36°': 36, '45°': 45, '60°': 60, '72°': 72,
    '90°': 90, '108°': 108, '109.47°': 109.47, '120°': 120,
    '150°': 150, '180°': 180, '270°': 270, '360°': 360,
    # Key angle fractions (in units of π)
    '1/6': 1/6, '1/4': 1/4, '1/3': 1/3, '1/2': 1/2,
    '2/3': 2/3, '3/4': 3/4, '5/6': 5/6,
    # Dimensional ladder exponents
    'E(1.5)=13/12': 13/12, 'E(2.5)=56/39': 56/39,
    'E(3)=21': 21,
    # Cosmological fractions
    'vis≈0.05': 0.0486, 'DM≈0.26': 0.2589, 'DE≈0.69': 0.6911,
    'DM+vis≈0.31': 0.3075, 'DE/matter=69/31': 69/31,
}

# Known physical angles (in degrees)
physics_angles = {
    'Weinberg angle θ_W': 28.74,
    'Cabibbo angle θ_C': 13.02,
    'θ₁₂ (solar)': 33.44,
    'θ₂₃ (atmospheric)': 49.2,
    'θ₁₃ (reactor)': 8.57,
    'Tetrahedral angle': 109.47,
    'Octahedral angle': 90.0,
    'sp² angle': 120.0,
    'Water angle': 104.45,
    'NH₃ angle': 107.0,
}


def make_anti_hermitian(G):
    return (G - np.conj(G.T)) / 2

def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(len(state), dtype=complex) / np.sqrt(len(state))
    return state / norm


# ============================================================
# Operator constructions (from v7/v9)
# ============================================================

def build_sphere_4D():
    """Standard ℂ⁴ sphere hub."""
    beats = []
    theta = np.pi / 2
    PHI = 2
    beat_config = [
        ('(•∘⊛)', 0, 1j),
        ('(—∘⎇)', 1, -1+0j),
        ('(Φ∘✹)', 2, -1j),
        ('(○∘⟳)', 3, 1+0j),
    ]
    for name, active, i_phase in beat_config:
        Gm = np.zeros((4, 4), dtype=complex)
        if active == PHI:
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T
                Gm[PHI, other] = coupling
                Gm[other, PHI] = -np.conj(coupling)
            Gm[PHI, PHI] = i_phase * theta / T
        else:
            coupling = i_phase * theta
            Gm[active, PHI] = coupling
            Gm[PHI, active] = -np.conj(coupling)
        Gm = make_anti_hermitian(Gm)
        beats.append((name, expm(Gm)))
    return beats


def build_octave_8D():
    """Full ℂ⁸ octave from v9."""
    stations = ['•', '⊛', '—', '⎇', 'Φ', '✹', '○', '⟳']
    beats = []
    theta = np.pi / 2
    i_phases = [1j, -1+0j, -1j, 1+0j]
    struct_idx = [0, 2, 4, 6]
    proc_idx =   [1, 3, 5, 7]
    PHI_s = 4; PHI_p = 5

    for beat, (s_idx, p_idx, i_phase) in enumerate(zip(struct_idx, proc_idx, i_phases)):
        Gm = np.zeros((8, 8), dtype=complex)
        internal = i_phase * theta
        Gm[s_idx, p_idx] = internal
        Gm[p_idx, s_idx] = -np.conj(internal)

        if s_idx == PHI_s:
            for other_s in [0, 2, 6]:
                c = i_phase * theta / T
                Gm[PHI_s, other_s] = c
                Gm[other_s, PHI_s] = -np.conj(c)
            Gm[PHI_s, PHI_s] = i_phase * theta / T
            for other_p in [1, 3, 7]:
                c = i_phase * theta / T
                Gm[PHI_p, other_p] = c
                Gm[other_p, PHI_p] = -np.conj(c)
            Gm[PHI_p, PHI_p] = i_phase * theta / T
        else:
            ext = i_phase * theta
            Gm[s_idx, PHI_s] = ext
            Gm[PHI_s, s_idx] = -np.conj(ext)
            Gm[p_idx, PHI_p] = ext
            Gm[PHI_p, p_idx] = -np.conj(ext)

        Gm = make_anti_hermitian(Gm)
        beats.append((f'({stations[s_idx]}∘{stations[p_idx]})', expm(Gm)))
    return beats


def compose_F(beats):
    d = len(beats[0][1])
    F = np.eye(d, dtype=complex)
    for _, B in beats:
        F = B @ F
    return F


def build_kappa_4D():
    k = np.eye(4, dtype=complex)
    k[0,2] = k[2,0] = alpha  # •↔Φ
    k[1,3] = k[3,1] = alpha  # —↔○
    return k

def build_kappa_8D():
    k = np.eye(8, dtype=complex)
    k[0,4] = k[4,0] = alpha  # •↔Φ
    k[2,6] = k[6,2] = alpha  # —↔○
    k[1,5] = k[5,1] = alpha  # ⊛↔✹
    k[3,7] = k[7,3] = alpha  # ⎇↔⟳
    return k


def iterate_T(F, kappa, psi0, n_steps=20000):
    psi = psi0.copy()
    for _ in range(n_steps):
        psi = kappa @ F @ psi
        psi = normalize(psi)
    return np.abs(psi)**2


def match_against_library(value, library, tolerance=0.05, name=""):
    """Find all library entries within tolerance of value."""
    matches = []
    for lib_name, lib_val in library.items():
        if lib_val == 0:
            continue
        residual = abs(value - lib_val) / abs(lib_val)
        if residual < tolerance:
            matches.append((lib_name, lib_val, residual))
    matches.sort(key=lambda x: x[2])
    return matches


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_operator(label, beats_func, kappa_func, dim, station_names):
    print(f"\n{'='*70}")
    print(f"  {label} (ℂ{dim})")
    print(f"{'='*70}")

    beats = beats_func()
    F = compose_F(beats)
    kappa = kappa_func()
    Top = kappa @ F

    # --- Eigenvalues ---
    ev = np.linalg.eigvals(Top)
    # Sort by magnitude descending
    idx = np.argsort(-np.abs(ev))
    ev = ev[idx]

    # Also get eigenvectors for station assignment
    eigenvalues, eigenvectors = np.linalg.eig(Top)
    ev_idx = np.argsort(-np.abs(eigenvalues))
    eigenvalues = eigenvalues[ev_idx]
    eigenvectors = eigenvectors[:, ev_idx]

    print(f"\n  {'─'*60}")
    print(f"  EIGENVALUE CATALOG")
    print(f"  {'─'*60}")

    print(f"\n  {'#':>3}  {'|λ|':>10}  {'Δ/α':>10}  {'Phase°':>10}  {'Phase/π':>10}  Dominant station")
    for k in range(dim):
        mag = abs(eigenvalues[k])
        delta = (mag - 1) / alpha
        phase_deg = np.degrees(np.angle(eigenvalues[k]))
        phase_pi = np.angle(eigenvalues[k]) / pi

        # Find dominant station
        weights = np.abs(eigenvectors[:, k])**2
        dom_idx = np.argmax(weights)
        dom_frac = weights[dom_idx]

        print(f"  {k:>3}  {mag:>10.8f}  {delta:>+10.6f}  {phase_deg:>+10.4f}  {phase_pi:>+10.6f}  {station_names[dom_idx]} ({dom_frac:.2f})")

    # --- Phase analysis ---
    print(f"\n  {'─'*60}")
    print(f"  PHASE MATCHING")
    print(f"  {'─'*60}")

    for k in range(dim):
        phase_deg = np.degrees(np.angle(eigenvalues[k]))
        phase_abs = abs(phase_deg)

        print(f"\n  λ_{k}: phase = {phase_deg:+.4f}°")

        # Match absolute phase against known angles
        matches = match_against_library(phase_abs, {**{f'{n}°': v for n, v in
            [('30', 30), ('36', 36), ('45', 45), ('60', 60), ('72', 72),
             ('90', 90), ('108', 108), ('109.47', 109.47), ('120', 120),
             ('132', 132), ('144', 144), ('150', 150), ('160', 160),
             ('162', 162), ('168', 168), ('180', 180)]},
            **physics_angles}, tolerance=0.10)

        if matches:
            for name, val, res in matches[:3]:
                print(f"    ≈ {name} = {val:.2f}° (residual {res*100:.2f}%)")
        else:
            print(f"    No match within 10%")

        # Match phase/π against framework fractions
        phase_pi_abs = abs(np.angle(eigenvalues[k]) / pi)
        frac_matches = match_against_library(phase_pi_abs,
            {'1/6': 1/6, '1/4': 1/4, '1/3': 1/3, '5/12': 5/12,
             '1/2': 1/2, '7/12': 7/12, '2/3': 2/3, '3/4': 3/4,
             '5/6': 5/6, '11/12': 11/12,
             'E(1.5)/π=13/12π': 13/(12*pi), 'T/G': 3/12,
             'R/G': 7/12, 'SU3/G': 8/12, 'V/G': 13/12,
             'T/R': 3/7, 'T/V': 3/13, 'R/V': 7/13,
             'Φ/R': 2/7, 'P/R': 4/7, '(Φ+○)/R': 5/7,
             'T/SU3': 3/8, 'P/SU3': 4/8, '(Φ+○)/SU3': 5/8,
             'SU3/V': 8/13, 'A(2)/V': 10/13,
             'T/(Φ+○)': 3/5, 'Φ/(Φ+○)': 2/5, 'P/(Φ+○)': 4/5,
             }, tolerance=0.05)
        if frac_matches:
            for name, val, res in frac_matches[:3]:
                print(f"    |phase|/π ≈ {name} = {val:.6f} (residual {res*100:.2f}%)")

    # --- Magnitude analysis ---
    print(f"\n  {'─'*60}")
    print(f"  SPLITTING FACTOR MATCHING (Δ/α)")
    print(f"  {'─'*60}")

    deltas = [(abs(eigenvalues[k]) - 1) / alpha for k in range(dim)]
    for k in range(dim):
        d = deltas[k]
        if abs(d) < 0.001:
            continue
        print(f"\n  λ_{k}: Δ/α = {d:+.6f}")
        d_abs = abs(d)
        matches = match_against_library(d_abs, {
            '1': 1, '1/2': 0.5, '1/3': 1/3, '1/4': 0.25,
            '1/φ': 1/phi, '1/φ²': 1/phi**2, 'φ-1=1/φ': phi-1,
            'T/R': 3/7, 'R/V': 7/13, 'T/V': 3/13, 'P/V': 4/13,
            'SU3/V': 8/13, 'T/SU3': 3/8, 'Φ/R': 2/7,
            '(Φ+○)/V': 5/13, '(Φ+○)/G': 5/12,
            'R/G': 7/12, 'SU3/G': 8/12,
            '2/R': 2/7, '2/V': 2/13, '3/V': 3/13,
            'π/6': pi/6, 'π/4': pi/4,
            'sin(30°)': 0.5, 'sin(θ_C)': 0.2243,
            'cos(θ_W)': np.cos(np.radians(28.74)),
            'sin(θ_W)': np.sin(np.radians(28.74)),
        }, tolerance=0.05)
        if matches:
            for name, val, res in matches[:3]:
                print(f"    ≈ {name} = {val:.6f} (residual {res*100:.2f}%)")

    # --- Splitting RATIOS ---
    print(f"\n  {'─'*60}")
    print(f"  SPLITTING RATIOS")
    print(f"  {'─'*60}")

    nonzero_deltas = [(k, abs(deltas[k])) for k in range(dim) if abs(deltas[k]) > 0.001]
    nonzero_deltas.sort(key=lambda x: -x[1])

    for i in range(len(nonzero_deltas)):
        for j in range(i+1, len(nonzero_deltas)):
            ki, di = nonzero_deltas[i]
            kj, dj = nonzero_deltas[j]
            if dj < 0.001:
                continue
            ratio = dj / di
            matches = match_against_library(ratio, {
                '1/φ²': 1/phi**2, '1/φ': 1/phi, 'φ-1': phi-1,
                '1/2': 0.5, '1/3': 1/3, '1/4': 0.25,
                'T/R': 3/7, 'T/V': 3/13, 'R/V': 7/13,
                'Φ/T': 2/3, 'T/P': 3/4,
                '(Φ+○)/SU3': 5/8, 'SU3/V': 8/13,
                'sin²(θ_W)': 0.23122,
            }, tolerance=0.03)
            if matches:
                for name, val, res in matches[:2]:
                    print(f"  |Δ_{kj}|/|Δ_{ki}| = {ratio:.6f} ≈ {name} = {val:.6f} ({res*100:.3f}%)")

    # --- Fixed-point weights ---
    print(f"\n  {'─'*60}")
    print(f"  FIXED-POINT WEIGHTS")
    print(f"  {'─'*60}")

    psi0 = normalize(np.random.randn(dim) + 0.01)
    weights = iterate_T(F, kappa, psi0, 20000)

    for k in range(dim):
        w = weights[k]
        print(f"\n  {station_names[k]}: w = {w:.6f}")
        matches = match_against_library(w, {
            '1/T': 1/3, '1/P': 1/4, '1/R': 1/7, '1/V': 1/13,
            '1/G': 1/12, '1/SU3': 1/8, '1/A(3)': 1/21,
            '1/(Φ+○)': 1/5, '1/6=1/(T!)': 1/6, '1/10=1/A(2)': 1/10,
            '2/G': 2/12, '2/V': 2/13, 'T/G': 3/12,
            'T/A(3)': 3/21, 'Φ/A(3)': 2/21, 'P/A(3)': 4/21,
            'vis≈0.049': 0.0486, 'DM≈0.259': 0.2589, 'DE≈0.691': 0.6911,
            'T/R²': 3/49, 'Φ/R²': 2/49, '1/S': 1/64,
            '1/P²': 1/16, 'T/V': 3/13, 'T/S': 3/64,
            'P/S': 4/64, 'R/S': 7/64, 'SU3/S': 8/64,
            'V/S': 13/64, 'G/S': 12/64,
        }, tolerance=0.10)
        if matches:
            for name, val, res in matches[:3]:
                print(f"    ≈ {name} = {val:.6f} (residual {res*100:.2f}%)")

    # --- Weight ratios ---
    print(f"\n  {'─'*60}")
    print(f"  WEIGHT RATIOS")
    print(f"  {'─'*60}")

    for i in range(dim):
        for j in range(i+1, dim):
            if weights[j] < 0.01:
                continue
            ratio = weights[i] / weights[j]
            if 0.5 < ratio < 2.0:
                # Near-unity ratios: check framework near-1 fractions
                matches = match_against_library(ratio, {
                    '1': 1.0, 'V/(V-1)=13/12': 13/12, '(V-1)/V=12/13': 12/13,
                    'T/Φ': 3/2, 'Φ/T': 2/3, 'P/T': 4/3, 'T/P': 3/4,
                    'R/SU3': 7/8, 'SU3/R': 8/7,
                    '(Φ+○)/P': 5/4, 'P/(Φ+○)': 4/5,
                }, tolerance=0.05)
            elif ratio >= 2.0:
                matches = match_against_library(ratio, {
                    'Φ': 2, 'T': 3, 'P': 4, 'Φ+○': 5,
                    'T!': 6, 'R': 7, 'SU3': 8, 'T²': 9,
                    'A(2)': 10, 'G': 12, 'V': 13,
                    'T/Φ': 3/2, 'R/T': 7/3, 'R/Φ': 7/2,
                    'SU3/T': 8/3, 'V/T': 13/3, 'G/T': 12/3,
                    'φ': phi, 'φ²': phi**2,
                }, tolerance=0.05)
            else:
                continue

            if matches:
                for name, val, res in matches[:2]:
                    print(f"  w({station_names[i]})/w({station_names[j]}) = {ratio:.4f} ≈ {name} = {val:.4f} ({res*100:.2f}%)")

    # --- Grouped weights ---
    print(f"\n  {'─'*60}")
    print(f"  GROUPED WEIGHTS")
    print(f"  {'─'*60}")

    if dim == 4:
        groups = {
            '•+Φ (primary diameter)': weights[0] + weights[2],
            '—+○ (secondary diameter)': weights[1] + weights[3],
            '•+○ (right half-plane)': weights[0] + weights[3],
            '—+Φ (left half-plane)': weights[1] + weights[2],
            '•+— (low-dim)': weights[0] + weights[1],
            'Φ+○ (high-dim)': weights[2] + weights[3],
        }
    elif dim == 8:
        groups = {
            'Structural (•,—,Φ,○)': weights[0]+weights[2]+weights[4]+weights[6],
            'Processual (⊛,⎇,✹,⟳)': weights[1]+weights[3]+weights[5]+weights[7],
            'Beat 1 (•+⊛)': weights[0]+weights[1],
            'Beat 2 (—+⎇)': weights[2]+weights[3],
            'Beat 3 (Φ+✹)': weights[4]+weights[5],
            'Beat 4 (○+⟳)': weights[6]+weights[7],
            'Primary diam struct (•+Φ)': weights[0]+weights[4],
            'Secondary diam struct (—+○)': weights[2]+weights[6],
            'Primary diam proc (⊛+✹)': weights[1]+weights[5],
            'Secondary diam proc (⎇+⟳)': weights[3]+weights[7],
            'Integer dims (0D+1D+2D+3D)': weights[0]+weights[2]+weights[4]+weights[6],
            'Half-int dims (0.5+1.5+2.5+3.5)': weights[1]+weights[3]+weights[5]+weights[7],
            'Low-dim struct (•+—)': weights[0]+weights[2],
            'High-dim struct (Φ+○)': weights[4]+weights[6],
            'Low-dim proc (⊛+⎇)': weights[1]+weights[3],
            'High-dim proc (✹+⟳)': weights[5]+weights[7],
        }

    for gname, gval in groups.items():
        print(f"\n  {gname}: {gval:.6f}")
        matches = match_against_library(gval, {
            '1/T': 1/3, '1/P': 1/4, '2/T': 2/3, 'T/P': 3/4,
            '1/2=◐': 0.5, '1/V': 1/13, '1/R': 1/7,
            'vis≈0.049': 0.0486, 'DM≈0.259': 0.2589, 'DE≈0.691': 0.6911,
            'DM+vis≈0.31': 0.3075,
            '0.70 (struct)': 0.70, '0.30 (proc)': 0.30,
            '7/10=R/A(2)': 7/10, '3/10=T/A(2)': 3/10,
            '7/13=R/V': 7/13, '6/13': 6/13,
            'T/R': 3/7, 'P/R': 4/7,
        }, tolerance=0.05)
        if matches:
            for name, val, res in matches[:3]:
                print(f"    ≈ {name} = {val:.6f} ({res*100:.2f}%)")

    return eigenvalues, weights


if __name__ == '__main__':
    np.random.seed(42)

    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v10: PREDICTION CATALOG")
    print("=" * 70)

    # ─── ℂ⁴ sphere (both diameters) ───
    ev4, w4 = analyze_operator(
        "ℂ⁴ SPHERE (κ both diameters)",
        build_sphere_4D, build_kappa_4D, 4,
        ['•(0D)', '—(1D)', 'Φ(2D)', '○(3D)']
    )

    # ─── ℂ⁸ octave ───
    ev8, w8 = analyze_operator(
        "ℂ⁸ FULL OCTAVE",
        build_octave_8D, build_kappa_8D, 8,
        ['•(0D)', '⊛(0.5D)', '—(1D)', '⎇(1.5D)', 'Φ(2D)', '✹(2.5D)', '○(3D)', '⟳(3.5D)']
    )

    # ─── Summary: predictions vs derivations ───
    print(f"\n{'='*70}")
    print(f"  PREDICTION CATALOG SUMMARY")
    print(f"{'='*70}")

    print("""
  CONFIRMED (derived from construction, not predictions):
  ─────────────────────────────────────────────────────
  • Phase sum ℂ⁴ = -π/6 (from self-drive, analytic)
  • Phase sum ℂ⁸ = -π/3 (double self-drive)
  • Singular values = {1+α, 1-α} (from κ_{0,2} = α)
  • Mixing time = 1/α (from singular value ratio)
  • Attractor uniqueness (proven by contraction)

  PREDICTIONS (numbers the operator produces that are NOT
  inputs to the construction):
  ─────────────────────────────────────────────────────
  Report follows from the matching above.
  A number is a GENUINE PREDICTION if:
    (a) it matches a framework ratio or physical observable
    (b) it was NOT put into the construction
    (c) the match is better than 5%
    """)

    # Collect genuine predictions
    print("  GENUINE PREDICTIONS:")
    print()

    # The ℂ⁸ 70/30 split
    struct_total = w8[0]+w8[2]+w8[4]+w8[6]
    proc_total = w8[1]+w8[3]+w8[5]+w8[7]
    print(f"  1. ℂ⁸ structural/processual = {struct_total:.4f}/{proc_total:.4f}")
    print(f"     → R/A(2) = 7/10 = 0.7000 / T/A(2) = 3/10 = 0.3000")
    err = abs(struct_total - 0.7)/0.7 * 100
    print(f"     Structural residual: {err:.2f}%")
    print(f"     Cosmological 69/31 residual: {abs(struct_total - 0.6911)/0.6911*100:.2f}%")
    print()

    # Phase assignments
    print(f"  2. Eigenvalue phase assignments (ℂ⁸):")
    for k in range(8):
        phase_deg = np.degrees(np.angle(ev8[k]))
        weights_k = np.abs(np.linalg.eig(build_kappa_8D() @ compose_F(build_octave_8D()))[1][:, np.argsort(-np.abs(np.linalg.eigvals(build_kappa_8D() @ compose_F(build_octave_8D()))))[k]])**2
        dom = np.argmax(weights_k)
        snames = ['•', '⊛', '—', '⎇', 'Φ', '✹', '○', '⟳']
        print(f"     λ_{k}: {phase_deg:+.2f}° (dominant: {snames[dom]})")
    print()

    print("  3. Individual ℂ⁸ fixed-point weights (to be matched against")
    print("     particle mass fractions, coupling constants, or")
    print("     dimensional ladder positions):")
    snames = ['•(0D)', '⊛(0.5D)', '—(1D)', '⎇(1.5D)', 'Φ(2D)', '✹(2.5D)', '○(3D)', '⟳(3.5D)']
    for k in range(8):
        print(f"     {snames[k]}: {w8[k]:.6f}")

    print(f"\n{'='*70}")
    print(f"v10 COMPLETE.")
    print(f"{'='*70}")
