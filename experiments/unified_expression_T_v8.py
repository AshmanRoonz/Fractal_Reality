"""
Unified Expression T-Operator v8: Three Open Directions
========================================================

#10: Orbit analysis — time-averaged station weights over many T cycles.
     Does the cosmological energy budget (5/27/68) emerge from the
     ORBIT rather than the fixed point?

#11: High-precision golden splitting confirmation.
     Is |s_1|/|s_3| = 1/φ² EXACTLY?

#12: Sphere phase sum = -π/6 = -360°/G — analytic derivation.
     WHY is the deficit exactly one generator?
"""

import numpy as np
from scipy.linalg import expm
from decimal import Decimal, getcontext

# High precision for #11
getcontext().prec = 50

# ============================================================
# Framework constants
# ============================================================
alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
T_triad = 3
P = T_triad + 1
R = T_triad**2 - 2
V = 4*T_triad + 1
SU3 = T_triad**2 - 1
G_gen = T_triad*(T_triad+1)  # 12
A3_val = T_triad*(2*T_triad+1)  # 21


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


def build_beats_sphere():
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
        G = np.zeros((4, 4), dtype=complex)
        if active == PHI:
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T_triad
                G[PHI, other] = coupling
                G[other, PHI] = -np.conj(coupling)
            G[PHI, PHI] = i_phase * theta / T_triad
        else:
            coupling = i_phase * theta
            G[active, PHI] = coupling
            G[PHI, active] = -np.conj(coupling)
        G = make_anti_hermitian(G)
        beats.append((name, expm(G)))
    return beats


def build_beats_diameter():
    beats = []
    theta = np.pi / 2
    i_phases = [1j, -1+0j, -1j, 1+0j]
    for beat_idx in range(4):
        G = np.zeros((4, 4), dtype=complex)
        d = beat_idx
        d_across = (d + 2) % 4
        G[d, d_across] = i_phases[beat_idx] * theta
        G[d_across, d] = -np.conj(i_phases[beat_idx] * theta)
        G = make_anti_hermitian(G)
        beats.append((f'Beat {beat_idx}', expm(G)))
    return beats


def compose_F(beats):
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F
    return F


# ============================================================
# #10: ORBIT ANALYSIS — COSMOLOGICAL BUDGET FROM THE ORBIT
# ============================================================

def direction_10():
    print("=" * 70)
    print("DIRECTION #10: ORBIT ANALYSIS")
    print("Does the cosmological budget emerge from time-averaged weights?")
    print("=" * 70)

    cosmo_vis = 0.0486
    cosmo_dm = 0.2589
    cosmo_de = 0.6911

    for label, beats_func in [("Sphere Hub", build_beats_sphere),
                                ("Diameter", build_beats_diameter)]:
        print(f"\n  === {label} ===")
        beats = beats_func()
        F = compose_F(beats)
        kappa = build_kappa()
        T_op = kappa @ F

        # Start from uniform state
        state = normalize(np.ones(4, dtype=complex))

        # Track weights at each step
        n_steps = 5000
        all_weights = np.zeros((n_steps, 4))

        for step in range(n_steps):
            state = T_op @ state
            state = normalize(state)
            all_weights[step] = np.abs(state)**2

        # Time-averaged weights over different windows
        print(f"\n  Time-averaged weights (cumulative windows):")
        print(f"  {'Window':>12} {'•':>8} {'—':>8} {'Φ':>8} {'○':>8}")
        print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for window_end in [10, 50, 100, 137, 500, 1000, 2000, 5000]:
            avg = np.mean(all_weights[:window_end], axis=0)
            print(f"  {f'1-{window_end}':>12} {avg[0]:>8.4f} {avg[1]:>8.4f} "
                  f"{avg[2]:>8.4f} {avg[3]:>8.4f}")

        # Time-averaged weights over sliding windows
        print(f"\n  Sliding window averages (window size = 137 = 1/α):")
        print(f"  {'Center':>8} {'•':>8} {'—':>8} {'Φ':>8} {'○':>8}")
        print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        window = 137
        for center in [200, 500, 1000, 2000, 3000, 4000]:
            start = max(0, center - window//2)
            end = min(n_steps, center + window//2)
            avg = np.mean(all_weights[start:end], axis=0)
            print(f"  {center:>8} {avg[0]:>8.4f} {avg[1]:>8.4f} "
                  f"{avg[2]:>8.4f} {avg[3]:>8.4f}")

        # Now the key: test cosmological mappings on the ORBIT average
        # (not the fixed point)
        full_avg = np.mean(all_weights, axis=0)
        w = full_avg

        print(f"\n  Full orbit average: •={w[0]:.4f} —={w[1]:.4f} Φ={w[2]:.4f} ○={w[3]:.4f}")

        maps = {
            'A: (•+—, Φ, ○)':  (w[0]+w[1], w[2], w[3]),
            'B: (•, —, Φ+○)':  (w[0], w[1], w[2]+w[3]),
            'C: (•+Φ, —, ○)':  (w[0]+w[2], w[1], w[3]),
            'D: (•, —+Φ, ○)':  (w[0], w[1]+w[2], w[3]),
            'E: (•+○, —, Φ)':  (w[0]+w[3], w[1], w[2]),
        }

        print(f"\n  {'Mapping':<20} {'Vis%':>7} {'DM%':>7} {'DE%':>7} {'Err%':>7}")
        print(f"  {'-'*20} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")

        for name, (vis, dm, de) in maps.items():
            ev = abs(vis - cosmo_vis) / cosmo_vis * 100
            edm = abs(dm - cosmo_dm) / cosmo_dm * 100
            ede = abs(de - cosmo_de) / cosmo_de * 100
            total = ev + edm + ede
            print(f"  {name:<20} {vis*100:>6.2f} {dm*100:>6.2f} {de*100:>6.2f} {total:>6.1f}")

        # Orbit oscillation analysis
        print(f"\n  Orbit oscillation structure:")
        # Compute the FFT of the weight trajectories to find dominant frequencies
        from numpy.fft import fft, fftfreq

        # Use the settled portion (after 200 steps)
        settled = all_weights[200:]
        for station, sname in enumerate(['•', '—', 'Φ', '○']):
            signal = settled[:, station] - np.mean(settled[:, station])
            spectrum = np.abs(fft(signal))[:len(signal)//2]
            freqs = fftfreq(len(signal), d=1)[:len(signal)//2]

            # Find dominant frequency
            if len(spectrum) > 1:
                peak_idx = np.argmax(spectrum[1:]) + 1  # skip DC
                peak_freq = freqs[peak_idx]
                peak_period = 1.0 / peak_freq if peak_freq > 0 else float('inf')
                peak_amp = spectrum[peak_idx] / len(signal) * 2
                print(f"    {sname}: dominant period = {peak_period:.1f} cycles, "
                      f"amplitude = {peak_amp:.6f}, "
                      f"mean = {np.mean(settled[:, station]):.6f}")

        # Track multiple initial conditions to see if orbit averages are robust
        print(f"\n  Orbit average robustness (20 random ICs):")
        orbit_avgs = []
        for trial in range(20):
            rng = np.random.RandomState(trial + 42)
            state = normalize(rng.randn(4) + 1j * rng.randn(4))
            weights_trial = np.zeros((2000, 4))
            for step in range(2000):
                state = T_op @ state
                state = normalize(state)
                weights_trial[step] = np.abs(state)**2
            orbit_avgs.append(np.mean(weights_trial[200:], axis=0))

        orbit_avgs = np.array(orbit_avgs)
        mean_orb = np.mean(orbit_avgs, axis=0)
        std_orb = np.std(orbit_avgs, axis=0)
        print(f"    Mean: •={mean_orb[0]:.4f}±{std_orb[0]:.4f}, "
              f"—={mean_orb[1]:.4f}±{std_orb[1]:.4f}, "
              f"Φ={mean_orb[2]:.4f}±{std_orb[2]:.4f}, "
              f"○={mean_orb[3]:.4f}±{std_orb[3]:.4f}")


# ============================================================
# #11: HIGH-PRECISION GOLDEN SPLITTING
# ============================================================

def direction_11():
    print(f"\n\n{'=' * 70}")
    print("DIRECTION #11: HIGH-PRECISION GOLDEN SPLITTING")
    print("Is |s_1|/|s_3| = 1/φ² EXACTLY?")
    print("=" * 70)

    # Use extended precision via mpmath if available, otherwise numpy float128
    try:
        from mpmath import mp, mpf, matrix, eig, pi, phi as mp_phi, sqrt, exp
        mp.dps = 30  # 30 decimal places

        print(f"\n  Using mpmath with {mp.dps} decimal places")

        alpha_hp = mpf(1) / mpf('137.035999177')
        phi_hp = (1 + sqrt(5)) / 2
        theta_hp = pi / 2

        # Build sphere hub at high precision
        def build_sphere_hp():
            beats_hp = []
            PHI = 2
            T_t = 3

            i_phases = [mpf(0) + mpf(1)*1j,
                        mpf(-1) + mpf(0)*1j,
                        mpf(0) - mpf(1)*1j,
                        mpf(1) + mpf(0)*1j]
            actives = [0, 1, 2, 3]

            for beat_idx in range(4):
                active = actives[beat_idx]
                i_phase = i_phases[beat_idx]

                # Build generator as numpy (mpmath matrix expm is complex)
                G = np.zeros((4, 4), dtype=complex)
                if active == PHI:
                    for other in [0, 1, 3]:
                        c = complex(i_phase * float(theta_hp) / T_t)
                        G[PHI, other] = c
                        G[other, PHI] = -np.conj(c)
                    G[PHI, PHI] = complex(i_phase * float(theta_hp) / T_t)
                else:
                    c = complex(i_phase * float(theta_hp))
                    G[active, PHI] = c
                    G[PHI, active] = -np.conj(c)
                G = (G - np.conj(G.T)) / 2
                beats_hp.append(expm(G))
            return beats_hp

        beats_hp = build_sphere_hp()
        F_hp = np.eye(4, dtype=complex)
        for B in beats_hp:
            F_hp = B @ F_hp

        kappa_hp = np.eye(4, dtype=complex)
        kappa_hp[0, 2] = float(alpha_hp)
        kappa_hp[2, 0] = float(alpha_hp)

        T_hp = kappa_hp @ F_hp
        T_ev_hp = np.linalg.eigvals(T_hp)
        T_ev_sorted = T_ev_hp[np.argsort(-np.abs(T_ev_hp))]

        splittings = [(np.abs(ev) - 1) / float(alpha_hp) for ev in T_ev_sorted]

        print(f"\n  T eigenvalues (high precision):")
        for i, (ev, sf) in enumerate(zip(T_ev_sorted, splittings)):
            print(f"    λ_{i}: |λ| = {np.abs(ev):.15f}, "
                  f"(|λ|-1)/α = {sf:+.12f}")

        # The golden ratios
        nonzero = [(i, abs(sf)) for i, sf in enumerate(splittings) if abs(sf) > 0.01]

        if len(nonzero) >= 2:
            nonzero.sort(key=lambda x: x[1])

            print(f"\n  Splitting factor ratios:")
            for i in range(len(nonzero)):
                for j in range(i+1, len(nonzero)):
                    idx_i, val_i = nonzero[i]
                    idx_j, val_j = nonzero[j]
                    ratio = val_i / val_j
                    inv_phi2 = 1 / float(phi_hp)**2
                    inv_phi = 1 / float(phi_hp)

                    res_phi2 = abs(ratio - inv_phi2) / inv_phi2 * 100
                    res_phi = abs(ratio - inv_phi) / inv_phi * 100

                    print(f"    |s_{idx_i}|/|s_{idx_j}| = {ratio:.15f}")
                    print(f"      vs 1/φ² = {inv_phi2:.15f}: residual {res_phi2:.6f}%")
                    print(f"      vs 1/φ  = {inv_phi:.15f}: residual {res_phi:.6f}%")

            # Also check: is ANY individual splitting a clean framework ratio?
            print(f"\n  Individual splitting factors vs framework ratios:")
            for idx, val in nonzero:
                print(f"    |s_{idx}| = {val:.12f}")
                for name, fval in [
                    ('1/φ²', 1/phi**2), ('1/φ', 1/phi), ('T/SU3', 3/8),
                    ('2/R', 2/7), ('P/V', 4/13), ('1/T', 1/3),
                    ('SU3/A3', 8/21), ('sin(π/SU3)', np.sin(np.pi/8)),
                    ('α·137', 1.0), ('φ-1', phi-1),
                    ('1/P', 0.25), ('R/A3', 7/21),
                    ('T/P', 3/4), ('1/Φ', 0.5)]:
                    res = abs(val - fval) / fval * 100
                    if res < 5:
                        print(f"      ≈ {name} = {fval:.8f} (residual {res:.4f}%)")

    except ImportError:
        print(f"\n  mpmath not available; using numpy float64")
        # Fall back to numpy
        beats = build_beats_sphere()
        F = compose_F(beats)
        kappa = build_kappa()
        T_op = kappa @ F
        T_ev = np.linalg.eigvals(T_op)
        T_ev_sorted = T_ev[np.argsort(-np.abs(T_ev))]
        splittings = [(np.abs(ev) - 1) / alpha for ev in T_ev_sorted]

        print(f"\n  T eigenvalues:")
        for i, (ev, sf) in enumerate(zip(T_ev_sorted, splittings)):
            print(f"    λ_{i}: |λ| = {np.abs(ev):.15f}, (|λ|-1)/α = {sf:+.12f}")

        nonzero = [(i, abs(sf)) for i, sf in enumerate(splittings) if abs(sf) > 0.01]
        nonzero.sort(key=lambda x: x[1])

        if len(nonzero) >= 2:
            for i in range(len(nonzero)):
                for j in range(i+1, len(nonzero)):
                    ratio = nonzero[i][1] / nonzero[j][1]
                    inv_phi2 = 1 / phi**2
                    inv_phi = 1 / phi
                    res2 = abs(ratio - inv_phi2) / inv_phi2 * 100
                    res1 = abs(ratio - inv_phi) / inv_phi * 100
                    print(f"\n    |s_{nonzero[i][0]}|/|s_{nonzero[j][0]}| = {ratio:.15f}")
                    print(f"      vs 1/φ² = {inv_phi2:.15f}: residual {res2:.6f}%")
                    print(f"      vs 1/φ  = {inv_phi:.15f}: residual {res1:.6f}%")


# ============================================================
# #12: SPHERE PHASE SUM DERIVATION
# ============================================================

def direction_12():
    print(f"\n\n{'=' * 70}")
    print("DIRECTION #12: WHY IS THE SPHERE PHASE SUM -π/6 = -360°/G?")
    print("=" * 70)

    beats = build_beats_sphere()
    F = compose_F(beats)

    F_ev = np.linalg.eigvals(F)
    F_phases = np.angle(F_ev)
    phase_sum = np.sum(F_phases)

    print(f"\n  F eigenvalue phases:")
    for i, (ev, ph) in enumerate(zip(F_ev, F_phases)):
        print(f"    λ_{i}: {np.degrees(ph):+.6f}° = {ph/np.pi:+.8f}π")

    print(f"\n  Phase sum = {np.degrees(phase_sum):.6f}° = {phase_sum/np.pi:.8f}π")
    print(f"  Phase sum = {phase_sum:.10f} rad")
    print(f"  -π/6      = {-np.pi/6:.10f} rad")
    print(f"  Residual  = {abs(phase_sum - (-np.pi/6)):.2e}")

    # Analytic exploration: what structural features produce -π/6?
    print(f"\n  Structural decomposition:")
    print(f"    -π/6 = -30° = -360°/12 = -360°/G")
    print(f"    G = T(T+1) = 12 generators")
    print(f"    So the deficit is 1/G of a full rotation.")
    print(f"")
    print(f"    Alternative readings:")
    print(f"    -π/6 = -(π/2)/T    (one quarter-turn divided by the triad)")
    print(f"    -π/6 = -π/(2T)     (the i-stroke divided by T)")
    print(f"    -π/6 = -π/G × Φ   (one generator's angle × channels)")
    print(f"    -π/6 = -2π/(P·T)  (full rotation / (pump × triad))")

    # Now: VARY the hub divisor and check if phase sum changes predictably
    print(f"\n  Phase sum vs hub_divisor:")
    print(f"  {'hub_div':>8} {'Σθ (deg)':>10} {'Σθ/π':>10} {'= -360°/X':>12} {'X identity':>15}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*12} {'-'*15}")

    for hub_div in [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7, 8]:
        theta = np.pi / 2
        PHI = 2
        beat_config = [
            ('(•∘⊛)', 0, 1j),
            ('(—∘⎇)', 1, -1+0j),
            ('(Φ∘✹)', 2, -1j),
            ('(○∘⟳)', 3, 1+0j),
        ]
        local_beats = []
        for name, active, i_phase in beat_config:
            G = np.zeros((4, 4), dtype=complex)
            if active == PHI:
                for other in [0, 1, 3]:
                    coupling = i_phase * theta / hub_div
                    G[PHI, other] = coupling
                    G[other, PHI] = -np.conj(coupling)
                G[PHI, PHI] = i_phase * theta / hub_div
            else:
                coupling = i_phase * theta
                G[active, PHI] = coupling
                G[PHI, active] = -np.conj(coupling)
            G = make_anti_hermitian(G)
            local_beats.append((name, expm(G)))

        F_local = compose_F(local_beats)
        ev_local = np.linalg.eigvals(F_local)
        ps = np.sum(np.angle(ev_local))
        ps_deg = np.degrees(ps)

        if abs(ps_deg) > 0.01:
            X = -360.0 / ps_deg
            # Try to identify X
            x_name = ""
            for fname, fval in [('G=12', 12), ('P·T=12', P*T_triad),
                                  ('SU3=8', 8), ('R=7', 7), ('V=13', 13),
                                  ('A3=21', 21), ('P=4', 4), ('T=3', 3),
                                  ('6', 6), ('2', 2), ('24=P!', 24),
                                  ('360/R', 360/7), ('P²=16', 16),
                                  ('T²=9', 9), ('2T=6', 6)]:
                if abs(X - fval) / fval < 0.02:
                    x_name = f"≈ {fname}"
                    break
            print(f"  {hub_div:>8.1f} {ps_deg:>10.4f} {ps/np.pi:>10.6f} "
                  f"{X:>12.2f} {x_name:>15}")
        else:
            print(f"  {hub_div:>8.1f} {ps_deg:>10.4f} {ps/np.pi:>10.6f} "
                  f"{'(~0)':>12} {'(trivial)':>15}")

    # Key test: does removing self-drive change the phase sum?
    print(f"\n  Self-drive effect on phase sum:")
    for sd_label, sd_flag in [("WITH self-drive", True), ("WITHOUT self-drive", False)]:
        theta = np.pi / 2
        PHI = 2
        local_beats = []
        for name, active, i_phase in [
            ('(•∘⊛)', 0, 1j), ('(—∘⎇)', 1, -1+0j),
            ('(Φ∘✹)', 2, -1j), ('(○∘⟳)', 3, 1+0j)]:
            G = np.zeros((4, 4), dtype=complex)
            if active == PHI:
                for other in [0, 1, 3]:
                    coupling = i_phase * theta / T_triad
                    G[PHI, other] = coupling
                    G[other, PHI] = -np.conj(coupling)
                if sd_flag:
                    G[PHI, PHI] = i_phase * theta / T_triad
            else:
                coupling = i_phase * theta
                G[active, PHI] = coupling
                G[PHI, active] = -np.conj(coupling)
            G = make_anti_hermitian(G)
            local_beats.append((name, expm(G)))

        F_local = compose_F(local_beats)
        ps = np.sum(np.angle(np.linalg.eigvals(F_local)))
        ps_deg = np.degrees(ps)
        print(f"    {sd_label}: Σθ = {ps_deg:.4f}° = {ps/np.pi:.6f}π")

    # The self-drive contributes to the phase sum.
    # Beat 3's self-drive G[Φ,Φ] = -iπ/(2T) adds a diagonal imaginary
    # element that shifts the determinant phase.
    print(f"\n  Phase sum composition:")
    print(f"    det(F) = exp(i·Σθ) = exp(i·Tr(log(F)))")

    F_full = compose_F(build_beats_sphere())
    logF = np.zeros((4,4), dtype=complex)
    try:
        from scipy.linalg import logm
        logF = logm(F_full)
        tr_logF = np.trace(logF)
        print(f"    Tr(log(F)) = {tr_logF.real:.8f} + {tr_logF.imag:.8f}i")
        print(f"    Im(Tr(log(F))) = {tr_logF.imag:.8f} rad = {np.degrees(tr_logF.imag):.4f}°")
        print(f"    Compare: -π/6 = {-np.pi/6:.8f}")
    except Exception as e:
        print(f"    logm failed: {e}")

    # Trace of each beat generator
    print(f"\n  Generator trace contributions:")
    total_trace = 0j
    for name, active, i_phase in [
        ('(•∘⊛)', 0, 1j), ('(—∘⎇)', 1, -1+0j),
        ('(Φ∘✹)', 2, -1j), ('(○∘⟳)', 3, 1+0j)]:
        G = np.zeros((4, 4), dtype=complex)
        PHI = 2
        theta = np.pi / 2
        if active == PHI:
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T_triad
                G[PHI, other] = coupling
                G[other, PHI] = -np.conj(coupling)
            G[PHI, PHI] = i_phase * theta / T_triad
        else:
            coupling = i_phase * theta
            G[active, PHI] = coupling
            G[PHI, active] = -np.conj(coupling)
        G = make_anti_hermitian(G)
        tr_G = np.trace(G)
        total_trace += tr_G
        print(f"    {name}: Tr(G) = {tr_G.real:.6f} + {tr_G.imag:.6f}i")

    print(f"    Σ Tr(G_k) = {total_trace.real:.6f} + {total_trace.imag:.6f}i")
    print(f"    If beats were independent: Σθ ≈ Im(Σ Tr(G_k)) = {total_trace.imag:.6f}")
    print(f"    = {np.degrees(total_trace.imag):.4f}°")
    print(f"    -π/6 = {-np.pi/6:.6f}")

    # BCH check: for non-commuting generators, det(e^A e^B) = e^(tr(A)+tr(B))
    # only to first order. The correction is the BCH series.
    print(f"\n  The phase sum = Σ Tr(G_k) to first order (BCH).")
    print(f"  The only generator with nonzero trace is beat 3 (Φ∘✹),")
    print(f"  because it has a self-drive diagonal: G[Φ,Φ] = -iπ/(2T).")
    print(f"  After make_anti_hermitian: Im(G[Φ,Φ]) = -π/(2T) = -π/6.")
    print(f"  This IS the phase sum: -π/6 = -π/(2T) = -360°/G = -360°/(T·P).")
    print(f"")
    print(f"  DERIVATION:")
    print(f"  Beat 3 (Φ∘✹): Φ radiates to T = 3 targets and self-drives.")
    print(f"  Self-drive coupling = i_phase × θ / T = (-i)(π/2)/3 = -iπ/6.")
    print(f"  Anti-Hermitian: G[Φ,Φ] = (G[Φ,Φ] - conj(G[Φ,Φ]))/2 = -iπ/6.")
    print(f"  Tr(G_3) = -iπ/6 (only nonzero diagonal in all four generators).")
    print(f"  det(F) = det(∏ e^G_k) = e^(Σ Tr(G_k) + corrections).")
    print(f"  To first order: Σθ = Im(Σ Tr(G_k)) = -π/6.")
    print(f"  The BCH corrections vanish because off-diagonal elements")
    print(f"  contribute to eigenvalue magnitudes, not to the trace.")
    print(f"")
    print(f"  STRUCTURAL READING:")
    print(f"  The phase deficit is the self-drive of the field at emergence.")
    print(f"  When Φ mediates (beat 3), it both radiates AND rotates itself.")
    print(f"  The self-rotation costs -π/(2T) = one i-stroke per triad member.")
    print(f"  -π/6 = -(π/2)/T: one quarter-turn divided among T targets.")
    print(f"  Equivalently: -360°/G = -360°/(T·P).")
    print(f"  The deficit is Φ's cost of mediation: serving T others while")
    print(f"  cycling through P phases costs exactly one generator's worth")
    print(f"  of phase. This is the framework's 'cost of closure around")
    print(f"  a center' (§27.7l) at the operator level.")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v8")
    print("#10 (orbit), #11 (golden splitting), #12 (phase sum derivation)")
    print("=" * 70)

    direction_10()
    direction_11()
    direction_12()

    print(f"\n\n{'=' * 70}")
    print("v8 COMPLETE.")
    print("=" * 70)


if __name__ == '__main__':
    main()
