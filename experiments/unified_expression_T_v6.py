"""
Unified Expression T-Operator v6: Eigenvalue Splitting & Weight Structure
=========================================================================

Direction #8: What is the ±0.37α splitting factor in the sphere construction?
Direction #9: Is the {•,Φ}≈10%/{—,○}≈40% weight structure robust?

Strategy:
  #8: Compute (|λ_i| - 1)/α for all four T eigenvalues across all sphere
      constructions. Compare the factors against every framework ratio:
        T/SU3 = 3/8 = 0.375
        1/e ≈ 0.3679
        ◐(1-◐)·P/T = 0.25·4/3 = 0.3333
        R/(P·(P+1)) = 7/20 = 0.35
        1/φ² ≈ 0.3820
        2/R = 2/7 ≈ 0.2857
        T/(SU3+1) = 3/9 = 1/T = 0.3333
        (T-1)/Φ² = 2/4 = 0.5 (nope, too big)
        SU3/(A(3)) = 8/21 ≈ 0.3810
        α itself ≈ 0.0073 (nope, too small)
        V/S = 13/64 ≈ 0.2031
        φ-1 = 1/φ ≈ 0.6180 (too big)
        1/(T+1) = 1/P = 0.25
        R/A(3) = 7/21 = 1/T = 0.3333
        sin²(θ_W) ≈ 0.2312
        T/SU3 = 3/8 = 0.375 ← top candidate from plan

  #9: Sweep beat construction parameters (coupling angles, hub weights,
      Lenz sign, triad divisor) and record the fixed-point weight structure.
      Test which constructions (if any) produce the cosmological 5/27/68
      or the 10/40 pattern, and whether the pattern is robust.
"""

import numpy as np
from scipy.linalg import expm

# ============================================================
# Framework constants
# ============================================================
alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
T_triad = 3
P = T_triad + 1
R = T_triad**2 - 2  # 7
V = 4*T_triad + 1    # 13
SU3 = T_triad**2 - 1  # 8
G_gen = T_triad*(T_triad+1)  # 12
A3 = T_triad*(2*T_triad+1)   # 21

# Framework candidate ratios for the splitting factor
candidates = {
    'T/SU3 = 3/8':          T_triad / SU3,          # 0.375
    '1/e':                   1 / np.e,                # 0.3679
    '◐(1-◐)·P/T':           0.25 * P / T_triad,     # 0.3333
    'R/P(P+1) = 7/20':      R / (P*(P+1)),           # 0.35
    '1/φ²':                  1 / phi**2,              # 0.3820
    'SU3/A(3) = 8/21':      SU3 / A3,                # 0.3810
    'T²/(SU3·T) = 1/T':     1.0 / T_triad,           # 0.3333
    '2/R':                   2.0 / R,                  # 0.2857
    'SU3/(SU3+T) = 8/11':   SU3 / (SU3 + T_triad),  # 0.7273
    'T/(2R) = 3/14':        T_triad / (2*R),          # 0.2143
    'P/V = 4/13':           P / V,                     # 0.3077
    'R/A(3) = 1/3':         R / A3,                    # 0.3333
    '(R-1)/(2·SU3)':        (R-1) / (2*SU3),          # 0.375 = T/SU3
    'phi/(2·phi+1)':        phi / (2*phi + 1),         # 0.4472 (prob not)
    'sin(π/SU3)':           np.sin(np.pi / SU3),      # 0.3827
    'cos(π/T)':             np.cos(np.pi / T_triad),  # 0.5 (nope)
    'sin(π/R)':             np.sin(np.pi / R),         # 0.4339
    '(φ-1)/φ = 1/φ²':      (phi-1)/phi,               # same as 1/φ²
    'T/(SU3) (confirm)':    3.0/8.0,                   # 0.375
}


def make_anti_hermitian(G):
    return (G - np.conj(G.T)) / 2


def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(4, dtype=complex) / 2.0
    return state / norm


def build_kappa():
    kappa = np.eye(4, dtype=complex)
    kappa[0, 2] = alpha
    kappa[2, 0] = alpha
    return kappa


# ============================================================
# Parameterized sphere hub construction
# ============================================================

def build_beats_sphere_param(hub_divisor=T_triad, theta=np.pi/2,
                              lenz_sign=1.0, self_drive=True):
    """
    Parameterized sphere hub beats for sensitivity analysis.

    hub_divisor: what to divide by when Φ distributes to multiple targets
    theta: rotation angle per beat (π/2 = quarter-turn)
    lenz_sign: +1 or -1 on beat 3 coupling (Lenz minus)
    self_drive: whether Φ has self-rotation in beat 3
    """
    beats = []
    PHI = 2

    beat_config = [
        ('(•∘⊛)', 0, 1j),
        ('(—∘⎇)', 1, -1+0j),
        ('(Φ∘✹)', 2, -1j * lenz_sign),
        ('(○∘⟳)', 3, 1+0j),
    ]

    for name, active, i_phase in beat_config:
        G = np.zeros((4, 4), dtype=complex)

        if active == PHI:
            for other in [0, 1, 3]:
                coupling = i_phase * theta / hub_divisor
                G[PHI, other] = coupling
                G[other, PHI] = -np.conj(coupling)
            if self_drive:
                G[PHI, PHI] = i_phase * theta / hub_divisor
        else:
            coupling = i_phase * theta
            G[active, PHI] = coupling
            G[PHI, active] = -np.conj(coupling)

        G = make_anti_hermitian(G)
        beats.append((name, expm(G)))

    return beats


def compute_T_properties(beats):
    """Compute F, T, eigenvalues, and fixed-point weights."""
    kappa = build_kappa()

    # Compose F
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F

    T_op = kappa @ F

    # T eigenvalues
    T_ev = np.linalg.eigvals(T_op)
    T_ev_sorted = T_ev[np.argsort(-np.abs(T_ev))]

    # Splitting factors: (|λ| - 1) / α
    splittings = [(np.abs(ev) - 1) / alpha for ev in T_ev_sorted]

    # Fixed point via iteration (more robust than eigenvector for
    # near-degenerate cases)
    state = normalize(np.ones(4, dtype=complex))
    for _ in range(5000):
        state = T_op @ state
        state = normalize(state)

    fp_mags = np.abs(state)**2

    # F properties
    F2_I = np.allclose(F @ F, np.eye(4), atol=1e-6)
    phase_sum = np.sum(np.angle(np.linalg.eigvals(F))) / np.pi

    return {
        'F': F,
        'T_op': T_op,
        'T_ev': T_ev_sorted,
        'splittings': splittings,
        'fp_mags': fp_mags,
        'F2_I': F2_I,
        'phase_sum': phase_sum,
    }


# ============================================================
# DIRECTION #8: Eigenvalue splitting factor identification
# ============================================================

def direction_8():
    print("=" * 70)
    print("DIRECTION #8: EIGENVALUE SPLITTING FACTOR")
    print("What is the ±0.37α factor in the sphere construction?")
    print("=" * 70)

    # Run the standard sphere hub (the one from v5)
    beats = build_beats_sphere_param(hub_divisor=T_triad, theta=np.pi/2)
    props = compute_T_properties(beats)

    print("\n  T eigenvalues and splitting factors:")
    for i, (ev, sf) in enumerate(zip(props['T_ev'], props['splittings'])):
        print(f"    λ_{i}: |λ| = {np.abs(ev):.10f}, "
              f"phase = {np.degrees(np.angle(ev)):+.4f}°, "
              f"(|λ|-1)/α = {sf:+.6f}")

    # Get the splitting magnitudes (non-zero ones)
    nonzero_splits = [abs(sf) for sf in props['splittings'] if abs(sf) > 0.01]

    if nonzero_splits:
        avg_split = np.mean(nonzero_splits)
        print(f"\n  Average |splitting factor| = {avg_split:.6f}")

        # Compare to framework candidates
        print(f"\n  {'Candidate ratio':<30} {'Value':>10} {'Residual':>10} {'Match?':>8}")
        print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*8}")

        scored = []
        for name, val in candidates.items():
            residual = abs(avg_split - val) / avg_split * 100
            match = "✓" if residual < 2 else ""
            scored.append((residual, name, val, match))

        scored.sort()
        for residual, name, val, match in scored[:15]:
            print(f"  {name:<30} {val:>10.6f} {residual:>9.2f}% {match:>8}")

    # Now vary the hub_divisor to see how the splitting factor depends on it
    print(f"\n  {'─'*60}")
    print(f"  Splitting factor vs hub divisor (sensitivity check):")
    print(f"  {'hub_div':>8} {'avg |split|':>12} {'closest ratio':>25} {'residual':>10}")
    print(f"  {'-'*8} {'-'*12} {'-'*25} {'-'*10}")

    for hub_div in [1, 2, T_triad, P, R/2, R, SU3, phi, phi**2]:
        beats = build_beats_sphere_param(hub_divisor=hub_div)
        props = compute_T_properties(beats)
        ns = [abs(sf) for sf in props['splittings'] if abs(sf) > 0.01]
        if ns:
            avg = np.mean(ns)
            # Find best match
            best_name, best_val, best_res = "", 0, 1e10
            for name, val in candidates.items():
                res = abs(avg - val) / avg * 100
                if res < best_res:
                    best_name, best_val, best_res = name, val, res
            print(f"  {hub_div:>8.3f} {avg:>12.6f} {best_name:>25} {best_res:>9.2f}%")

    # Check specifically: does hub_divisor = SU3 give splitting = T/SU3?
    # The sphere divides beat 3 by T_triad (3 targets). What if the
    # division encodes a different structural constant?
    print(f"\n  {'─'*60}")
    print(f"  Splitting factor breakdown by eigenvalue:")

    beats = build_beats_sphere_param(hub_divisor=T_triad)
    props = compute_T_properties(beats)

    # Detailed eigenvalue analysis
    T_ev = props['T_ev']
    for i, ev in enumerate(T_ev):
        mag = np.abs(ev)
        phase = np.angle(ev)
        delta = mag - 1

        if abs(delta) > 1e-8:
            # Test each candidate as (|λ|-1) = candidate × α
            print(f"\n    λ_{i}: |λ| = {mag:.10f}, Δ = {delta:+.4e}")
            for name, val in sorted(candidates.items(),
                                     key=lambda x: abs(abs(delta) - x[1]*alpha)):
                predicted = val * alpha
                res = abs(abs(delta) - predicted) / abs(delta) * 100
                if res < 5:
                    print(f"      {name:<30}: predicted Δ = {predicted:.4e}, "
                          f"residual = {res:.3f}%")

    # Also check: are the FOUR splitting factors related to each other
    # in a framework way?
    print(f"\n  Splitting factor ratios (pairwise):")
    abs_splits = [abs(sf) for sf in props['splittings']]
    for i in range(4):
        for j in range(i+1, 4):
            if abs_splits[j] > 0.01 and abs_splits[i] > 0.01:
                ratio = abs_splits[i] / abs_splits[j]
                print(f"    |s_{i}|/|s_{j}| = {ratio:.6f}")


# ============================================================
# DIRECTION #9: Weight structure robustness
# ============================================================

def direction_9():
    print(f"\n\n{'=' * 70}")
    print("DIRECTION #9: WEIGHT STRUCTURE ROBUSTNESS")
    print("{•,Φ}≈10%/{—,○}≈40%: is it robust? cosmological connection?")
    print("=" * 70)

    # Cosmological targets
    cosmo_vis = 0.0486    # visible matter
    cosmo_dm = 0.2589     # dark matter
    cosmo_de = 0.6911     # dark energy

    results = []

    # Sweep: hub_divisor
    print(f"\n  Sweep: hub_divisor (theta=π/2, standard i-phases)")
    print(f"  {'hub_div':>8} {'•':>8} {'—':>8} {'Φ':>8} {'○':>8} "
          f"{'•+Φ':>8} {'—+○':>8} {'ratio':>8}")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for hub_div in [1, 1.5, 2, 2.5, T_triad, 3.5, P, 5, R/2, R, SU3]:
        beats = build_beats_sphere_param(hub_divisor=hub_div)
        props = compute_T_properties(beats)
        w = props['fp_mags']
        soul_field = w[0] + w[2]
        line_bound = w[1] + w[3]
        ratio = line_bound / soul_field if soul_field > 1e-10 else float('inf')
        results.append(('hub_div', hub_div, w, ratio))
        print(f"  {hub_div:>8.2f} {w[0]:>8.4f} {w[1]:>8.4f} {w[2]:>8.4f} {w[3]:>8.4f} "
              f"{soul_field:>8.4f} {line_bound:>8.4f} {ratio:>8.2f}")

    # Sweep: theta (rotation angle)
    print(f"\n  Sweep: theta (hub_div=T=3, standard i-phases)")
    print(f"  {'theta/π':>8} {'•':>8} {'—':>8} {'Φ':>8} {'○':>8} "
          f"{'•+Φ':>8} {'—+○':>8} {'ratio':>8}")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for theta_frac in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        theta = theta_frac * np.pi
        beats = build_beats_sphere_param(hub_divisor=T_triad, theta=theta)
        props = compute_T_properties(beats)
        w = props['fp_mags']
        soul_field = w[0] + w[2]
        line_bound = w[1] + w[3]
        ratio = line_bound / soul_field if soul_field > 1e-10 else float('inf')
        results.append(('theta', theta_frac, w, ratio))
        print(f"  {theta_frac:>8.2f} {w[0]:>8.4f} {w[1]:>8.4f} {w[2]:>8.4f} {w[3]:>8.4f} "
              f"{soul_field:>8.4f} {line_bound:>8.4f} {ratio:>8.2f}")

    # Sweep: Lenz sign on beat 3
    print(f"\n  Sweep: Lenz sign (hub_div=T=3, theta=π/2)")
    for lenz in [1.0, -1.0]:
        beats = build_beats_sphere_param(hub_divisor=T_triad, lenz_sign=lenz)
        props = compute_T_properties(beats)
        w = props['fp_mags']
        soul_field = w[0] + w[2]
        line_bound = w[1] + w[3]
        ratio = line_bound / soul_field if soul_field > 1e-10 else float('inf')
        print(f"  Lenz={lenz:+.0f}: •={w[0]:.4f} —={w[1]:.4f} Φ={w[2]:.4f} ○={w[3]:.4f}"
              f"  •+Φ={soul_field:.4f}  —+○={line_bound:.4f}  ratio={ratio:.2f}")

    # Sweep: self-drive on/off
    print(f"\n  Sweep: self-drive (hub_div=T=3, theta=π/2)")
    for sd in [True, False]:
        beats = build_beats_sphere_param(hub_divisor=T_triad, self_drive=sd)
        props = compute_T_properties(beats)
        w = props['fp_mags']
        soul_field = w[0] + w[2]
        line_bound = w[1] + w[3]
        ratio = line_bound / soul_field if soul_field > 1e-10 else float('inf')
        print(f"  self_drive={str(sd):<5}: •={w[0]:.4f} —={w[1]:.4f} Φ={w[2]:.4f} ○={w[3]:.4f}"
              f"  •+Φ={soul_field:.4f}  —+○={line_bound:.4f}  ratio={ratio:.2f}")

    # ============================================================
    # Cosmological budget analysis
    # ============================================================
    print(f"\n  {'─'*60}")
    print(f"  COSMOLOGICAL BUDGET SEARCH")
    print(f"  Target: vis=4.86%, DM=25.89%, DE=69.11%")
    print(f"  {'─'*60}")

    # Interpretation mappings to test:
    #   Map A: ○ = DE (boundary = dark energy field of scale above)
    #          •+— = visible (aperture + line = right half of i-cycle)
    #          Φ = DM (field = internal processing)
    #   Map B: Φ+○ = DE (field + boundary = the "exterior")
    #          • = visible (aperture = observer)
    #          — = DM (commitment = hidden structure)
    #   Map C: ○ = DE, — = DM, •+Φ = visible

    print(f"\n  Mapping interpretations for standard sphere hub:")
    beats = build_beats_sphere_param(hub_divisor=T_triad)
    props = compute_T_properties(beats)
    w = props['fp_mags']

    maps = {
        'A: (•+—, Φ, ○)':  (w[0]+w[1], w[2], w[3]),
        'B: (•, —, Φ+○)':  (w[0], w[1], w[2]+w[3]),
        'C: (•+Φ, —, ○)':  (w[0]+w[2], w[1], w[3]),
        'D: (•, —+Φ, ○)':  (w[0], w[1]+w[2], w[3]),
        'E: (•+○, —, Φ)':  (w[0]+w[3], w[1], w[2]),
    }

    print(f"  Weights: •={w[0]:.4f}, —={w[1]:.4f}, Φ={w[2]:.4f}, ○={w[3]:.4f}")
    print(f"\n  {'Mapping':<20} {'Vis':>8} {'DM':>8} {'DE':>8} {'err_V':>8} {'err_DM':>8} {'err_DE':>8} {'total_err':>10}")
    print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

    for name, (vis, dm, de) in maps.items():
        ev = abs(vis - cosmo_vis) / cosmo_vis * 100
        edm = abs(dm - cosmo_dm) / cosmo_dm * 100
        ede = abs(de - cosmo_de) / cosmo_de * 100
        total = ev + edm + ede
        print(f"  {name:<20} {vis*100:>7.2f}% {dm*100:>7.2f}% {de*100:>7.2f}% "
              f"{ev:>7.1f}% {edm:>7.1f}% {ede:>7.1f}% {total:>9.1f}%")

    # ============================================================
    # Big sweep: find any construction that matches cosmology
    # ============================================================
    print(f"\n  {'─'*60}")
    print(f"  EXHAUSTIVE SWEEP: looking for cosmological match")
    print(f"  Sweeping hub_div × theta × lenz × self_drive")
    print(f"  {'─'*60}")

    best_matches = []  # (total_error, params, mapping_name, vis, dm, de)

    hub_divs = [1, 1.5, 2, 2.5, T_triad, 3.5, P, 5, R/2, R, SU3, phi, phi**2, V, A3]
    thetas = [np.pi * f for f in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
    lenz_signs = [1.0, -1.0]
    self_drives = [True, False]

    for hd in hub_divs:
        for th in thetas:
            for lenz in lenz_signs:
                for sd in self_drives:
                    try:
                        beats = build_beats_sphere_param(
                            hub_divisor=hd, theta=th, lenz_sign=lenz, self_drive=sd)
                        props = compute_T_properties(beats)
                        w = props['fp_mags']

                        # Test all mappings
                        for mname, (vis, dm, de) in [
                            ('A', (w[0]+w[1], w[2], w[3])),
                            ('B', (w[0], w[1], w[2]+w[3])),
                            ('C', (w[0]+w[2], w[1], w[3])),
                            ('D', (w[0], w[1]+w[2], w[3])),
                            ('E', (w[0]+w[3], w[1], w[2])),
                        ]:
                            ev = abs(vis - cosmo_vis) / cosmo_vis * 100
                            edm = abs(dm - cosmo_dm) / cosmo_dm * 100
                            ede = abs(de - cosmo_de) / cosmo_de * 100
                            total = ev + edm + ede

                            if total < 50:  # generous threshold
                                best_matches.append((
                                    total,
                                    f"hd={hd:.2f},θ={th/np.pi:.1f}π,L={lenz:+.0f},sd={sd}",
                                    mname, vis*100, dm*100, de*100
                                ))
                    except Exception:
                        pass

    best_matches.sort()

    if best_matches:
        print(f"\n  Top 15 cosmological matches (total err < 50%):")
        print(f"  {'Params':<45} {'Map':>4} {'Vis%':>7} {'DM%':>7} {'DE%':>7} {'Err%':>7}")
        print(f"  {'-'*45} {'-'*4} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
        for total, params, mname, vis, dm, de in best_matches[:15]:
            print(f"  {params:<45} {mname:>4} {vis:>6.2f} {dm:>6.2f} {de:>6.2f} {total:>6.1f}")
    else:
        print(f"\n  No matches found within 50% total error.")
        print(f"  This suggests the cosmological budget does NOT emerge from")
        print(f"  the fixed point of T directly; it may require orbit analysis")
        print(f"  or a richer representation (ℂ⁸, density matrix).")

    # ============================================================
    # The ratio (—+○)/(•+Φ) across constructions
    # ============================================================
    print(f"\n  {'─'*60}")
    print(f"  WEIGHT RATIO ANALYSIS")
    print(f"  Is (—+○)/(•+Φ) = P (the pump) = 4?")
    print(f"  {'─'*60}")

    print(f"\n  Standard sphere hub (hub_div=T=3):")
    beats = build_beats_sphere_param(hub_divisor=T_triad)
    props = compute_T_properties(beats)
    w = props['fp_mags']
    ratio = (w[1] + w[3]) / (w[0] + w[2]) if (w[0] + w[2]) > 1e-10 else float('inf')
    print(f"    Weights: •={w[0]:.6f}, —={w[1]:.6f}, Φ={w[2]:.6f}, ○={w[3]:.6f}")
    print(f"    (—+○)/(•+Φ) = {ratio:.6f}")
    print(f"    Compare to framework values:")
    for name, val in [('P = 4', 4), ('T = 3', 3), ('Φ = 2', 2),
                       ('P-1 = 3', 3), ('R/Φ = 3.5', 3.5),
                       ('(SU3-1)/Φ = 3.5', 3.5), ('φ²', phi**2),
                       ('P/• = 4', 4), ('R-T = 4', R-T_triad),
                       ('SU3/Φ = 4', SU3/2)]:
        res = abs(ratio - val) / val * 100
        marker = " ←←←" if res < 2 else (" ←" if res < 5 else "")
        print(f"      {name:<20}: residual {res:.2f}%{marker}")

    # Check if •/Φ ratio is meaningful
    if w[0] > 1e-10 and w[2] > 1e-10:
        ratio_ap = w[0] / w[2]
        print(f"\n    •/Φ = {ratio_ap:.6f}")
        for name, val in [('1', 1), ('α', alpha), ('1/T', 1/T_triad),
                           ('◐', 0.5), ('Φ/P = 0.5', 0.5)]:
            res = abs(ratio_ap - val) / val * 100 if val > 0 else 999
            marker = " ←←←" if res < 2 else (" ←" if res < 5 else "")
            print(f"      {name:<20}: residual {res:.2f}%{marker}")

    # Check if —/○ ratio is meaningful
    if w[1] > 1e-10 and w[3] > 1e-10:
        ratio_lb = w[1] / w[3]
        print(f"\n    —/○ = {ratio_lb:.6f}")
        for name, val in [('1', 1), ('T/R', T_triad/R),
                           ('◐', 0.5), ('Φ/P = 0.5', 0.5),
                           ('R/V', R/V), ('T/(P+1)', T_triad/(P+1))]:
            res = abs(ratio_lb - val) / val * 100 if val > 0 else 999
            marker = " ←←←" if res < 2 else (" ←" if res < 5 else "")
            print(f"      {name:<20}: residual {res:.2f}%{marker}")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v6")
    print("Directions #8 (splitting factor) and #9 (weight structure)")
    print("=" * 70)

    direction_8()
    direction_9()

    print(f"\n\n{'=' * 70}")
    print("DONE. Check results above for:")
    print("  #8: Which framework ratio matches the splitting factor?")
    print("  #9: Is the weight structure robust? Does any construction")
    print("       match the cosmological energy budget?")
    print("=" * 70)


if __name__ == '__main__':
    main()
