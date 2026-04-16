"""
Unified Expression T-Operator v4: The Glyph as Operator
=========================================================

⊙ = a circle (○) with a dot (•) at its center.
— = the diameter, connecting • to ○.
radius = —/2 = ◐ × —

◐ = 0.5 is NOT a parameter. It's the geometry of the glyph:
the radius is half the diameter. This constrains the operator:

  - Four beats = four quarter-turns of the circle (each π/2)
  - All beats have EQUAL rotation magnitude (the radius constraint)
  - The i-stroke determines the PLANE of rotation, not the magnitude
  - Beats 1-2 = inward half (π); beats 3-4 = outward half (π)
  - The midpoint (beat 2, i² = -1) is where direction reverses

The circle has circumference 2π. Four quarter-turns cover it.
The diameter — connects • to ○ through the center.
π × — = circumference (§27.7l: Φ is the glyph of π).

What's in the expression:
  1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]

What the glyph adds:
  ◐ = 0.5 (radius = diameter/2; inherent in ⊙)
  π (circumference/diameter; inherent in ○)
  All four beats are equal quarter-turns (four π/2 rotations)
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
R = T_triad**2 - 2
V = 4*T_triad + 1
SU3 = T_triad**2 - 1


def make_anti_hermitian(G):
    return (G - np.conj(G.T)) / 2


def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(4, dtype=complex) / 2.0
    return state / norm


# ============================================================
# THE FOUR BEATS: equal quarter-turns, different planes
# ============================================================
#
# Each beat is a rotation by π/2 in the plane defined by
# (station_d, station_{d+1 mod 4}).
#
# The i-stroke determines the PHASE of the rotation:
#   Beat 1 (•∘⊛): i¹ = +i  → rotation phase +π/2
#   Beat 2 (—∘⎇): i² = -1  → rotation phase π
#   Beat 3 (Φ∘✹): i³ = -i  → rotation phase -π/2 (= 3π/2)
#   Beat 4 (○∘⟳): i⁰ = +1  → rotation phase 0 (= 2π)
#
# All four rotations have the SAME magnitude: π/2.
# This IS the radius constraint: ◐ = 0.5 means
# each beat covers exactly one quarter of the circle.
#
# The generator for a rotation by angle θ in the (a,b) plane
# with complex phase ψ is:
#   G[a,b] = e^{iψ} × θ
#   G[b,a] = -conj(G[a,b])  (anti-Hermitian)

def build_beats_glyph():
    """
    Four equal quarter-turns. The glyph ⊙ as an operator.
    """
    beats = []

    # The rotation magnitude: π/2 (one quarter-turn)
    # This is the RADIUS of the unit circle in phase space.
    theta = np.pi / 2

    # The four i-strokes as complex phases
    i_phases = [
        1j,     # i¹ = +i  (convergence)
        -1+0j,  # i² = -1  (commitment, the i-turn)
        -1j,    # i³ = -i  (emergence)
        1+0j,   # i⁰ = +1  (recursion)
    ]

    beat_names = ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']

    for beat_idx in range(4):
        d = beat_idx
        d_next = (d + 1) % 4

        G = np.zeros((4, 4), dtype=complex)

        # The coupling in the (d, d+1) plane
        # Phase from i-stroke; magnitude = θ
        coupling = i_phases[beat_idx] * theta

        G[d, d_next] = coupling
        G[d_next, d] = -np.conj(coupling)

        # That's it. No self-rotation. The coupling IS the beat.
        # Anti-Hermitian is already enforced by the construction.
        G = make_anti_hermitian(G)

        beats.append((beat_names[beat_idx], expm(G)))

    return beats


def build_beats_glyph_with_self_rotation():
    """
    Variant: each beat also self-rotates the station by its i-stroke.
    The ∘ (pairing) means "structure AND process":
    the coupling (off-diagonal) and the phase advance (diagonal).
    """
    beats = []
    theta = np.pi / 2
    i_phases = [1j, -1+0j, -1j, 1+0j]
    beat_names = ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']

    for beat_idx in range(4):
        d = beat_idx
        d_next = (d + 1) % 4

        G = np.zeros((4, 4), dtype=complex)

        coupling = i_phases[beat_idx] * theta

        # Off-diagonal: coupling between stations
        G[d, d_next] = coupling
        G[d_next, d] = -np.conj(coupling)

        # Diagonal: self-rotation of station d by i-stroke
        # The ∘ means both happen together
        G[d, d] = i_phases[beat_idx] * theta

        G = make_anti_hermitian(G)
        beats.append((beat_names[beat_idx], expm(G)))

    return beats


def build_beats_diameter():
    """
    The diameter reading: — connects • to ○ directly.

    Instead of coupling ADJACENT stations (0↔1, 1↔2, 2↔3, 3↔0),
    each beat couples its STRUCTURAL station to the one across
    the diameter:
      Beat 1 (•): couples 0 ↔ 2 (soul ↔ field; the •-Φ axis)
      Beat 2 (—): couples 1 ↔ 3 (line ↔ boundary; the —-○ axis)
      Beat 3 (Φ): couples 2 ↔ 0 (field ↔ soul; same axis, reverse)
      Beat 4 (○): couples 3 ↔ 1 (boundary ↔ line; same axis, reverse)

    This makes the diameter explicit: each beat crosses the full
    width of the circle, and the radius is the midpoint.
    """
    beats = []
    theta = np.pi / 2
    i_phases = [1j, -1+0j, -1j, 1+0j]
    beat_names = ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']

    for beat_idx in range(4):
        d = beat_idx
        d_across = (d + 2) % 4  # the station across the diameter

        G = np.zeros((4, 4), dtype=complex)
        coupling = i_phases[beat_idx] * theta

        G[d, d_across] = coupling
        G[d_across, d] = -np.conj(coupling)

        G = make_anti_hermitian(G)
        beats.append((beat_names[beat_idx], expm(G)))

    return beats


# ============================================================
# NESTING: ⊂[α] as pure κ matrix
# ============================================================

def build_kappa():
    """κ with only the primary entry: κ_{0,2} = α"""
    kappa = np.eye(4, dtype=complex)
    kappa[0, 2] = alpha
    kappa[2, 0] = alpha
    return kappa


# ============================================================
# Analysis functions
# ============================================================

def analyze_construction(beats_func, label):
    """Full analysis of a beat construction."""

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")

    beats = beats_func()
    kappa = build_kappa()

    # Compose F
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F

    T_op = kappa @ F

    # --- F properties ---
    F_unitary = np.allclose(F @ np.conj(F.T), np.eye(4), atol=1e-10)
    F_ev = np.linalg.eigvals(F)
    F_phases = np.sort(np.angle(F_ev))
    phase_sum = np.sum(np.angle(F_ev))

    print(f"\n  F unitary: {F_unitary}")
    print(f"  |det(F)| = {abs(np.linalg.det(F)):.10f}")
    print(f"  F eigenvalue phases: {[f'{np.degrees(p):.3f}°' for p in F_phases]}")
    print(f"  Phase sum: {np.degrees(phase_sum):.4f}° = {phase_sum/np.pi:.6f}π")

    # Is F = identity? (four quarter-turns closing to identity)
    F_is_identity = np.allclose(F, np.eye(4), atol=1e-10)
    print(f"  F ≈ I (loop closes to identity): {F_is_identity}")

    if not F_is_identity:
        # How far from identity?
        dist_to_I = np.linalg.norm(F - np.eye(4))
        print(f"  ||F - I|| = {dist_to_I:.6f}")

    # --- Individual beats ---
    print(f"\n  Individual beat eigenvalues:")
    for name, B in beats:
        B_ev = np.linalg.eigvals(B)
        phases = np.sort(np.degrees(np.angle(B_ev)))
        mags = np.sort(np.abs(B_ev))
        print(f"    {name}: phases = [{', '.join([f'{p:.2f}°' for p in phases])}], "
              f"mags = [{', '.join([f'{m:.8f}' for m in mags])}]")

    # --- T eigenvalues ---
    T_ev, T_evec = np.linalg.eig(T_op)
    idx = np.argsort(-np.abs(T_ev))
    T_ev = T_ev[idx]
    T_evec = T_evec[:, idx]

    print(f"\n  T eigenvalues:")
    for i, ev in enumerate(T_ev):
        print(f"    λ_{i}: |λ| = {np.abs(ev):.10f}, phase = {np.degrees(np.angle(ev)):.4f}°")

    # --- Fixed point ---
    fp_idx = np.argmin(np.abs(np.abs(T_ev) - 1))
    fp = normalize(T_evec[:, fp_idx])
    fp_mags = np.abs(fp)**2

    print(f"\n  Fixed point (eigenvector closest to |λ|=1):")
    print(f"    |z|²: • = {fp_mags[0]:.6f}, — = {fp_mags[1]:.6f}, "
          f"Φ = {fp_mags[2]:.6f}, ○ = {fp_mags[3]:.6f}")

    # ◐ as weight ratio
    if fp_mags[0] + fp_mags[3] > 1e-10:
        balance_weight = fp_mags[0] / (fp_mags[0] + fp_mags[3])
    else:
        balance_weight = float('nan')

    # ◐ as inward/outward balance
    # Inward = beats 1,2 (convergence + commitment) = • + —
    # Outward = beats 3,4 (emergence + recursion) = Φ + ○
    inward = fp_mags[0] + fp_mags[1]
    outward = fp_mags[2] + fp_mags[3]
    if inward + outward > 1e-10:
        balance_inout = inward / (inward + outward)
    else:
        balance_inout = float('nan')

    # ◐ as structural/processual balance
    # This is a different reading: the state vector is structural;
    # the process is in the operators. But we can measure how
    # much of the state is in the "first half" vs "second half"
    # of the diameter.
    first_half = fp_mags[0] + fp_mags[1]  # • + — (center to midpoint)
    second_half = fp_mags[2] + fp_mags[3]  # Φ + ○ (midpoint to boundary)
    if first_half + second_half > 1e-10:
        balance_diameter = first_half / (first_half + second_half)
    else:
        balance_diameter = float('nan')

    print(f"\n  ◐ readings:")
    print(f"    •/(•+○) = {balance_weight:.6f}")
    print(f"    (•+—)/(•+—+Φ+○) = {balance_diameter:.6f}  (diameter midpoint)")
    print(f"    inward/total = {balance_inout:.6f}  (convergence+commitment / all)")

    # --- Cosmological check ---
    # Framework: vis ~5%, DM ~27%, DE ~69%
    # The i-cycle quadrant mapping:
    #   Right half (i⁰, i¹) = visible = • + ○? or • (genesis) + ○ (closure)?
    #   Left half (i², i³) = dark matter = — + Φ?
    #   Field itself = dark energy = Φ?
    #
    # Actually, from the framework §10.10a:
    #   ~5% visible: energy at the inter-scale interface (right half: i⁰+i¹)
    #   ~27% dark matter: energy mid-process (left half: i²+i³)
    #   ~68% dark energy: Φ itself, the complex plane

    print(f"\n  Cosmological readings:")
    print(f"    Reading 1 (station = dimension):")
    print(f"      • (0D) = {fp_mags[0]*100:.1f}%, — (1D) = {fp_mags[1]*100:.1f}%, "
          f"Φ (2D) = {fp_mags[2]*100:.1f}%, ○ (3D) = {fp_mags[3]*100:.1f}%")

    # i-cycle quadrant reading
    right_half = fp_mags[0] + fp_mags[3]   # i⁰ (recursion) + i¹ (convergence)
    left_half = fp_mags[1] + fp_mags[2]    # i² (commitment) + i³ (emergence)
    print(f"    Reading 2 (i-cycle quadrants):")
    print(f"      right half (•+○, visible): {right_half*100:.1f}%")
    print(f"      left half (—+Φ, dark matter): {left_half*100:.1f}%")

    # What if Φ station weight IS dark energy fraction?
    print(f"    Reading 3 (Φ as dark energy):")
    print(f"      Φ = {fp_mags[2]*100:.1f}% (target: 69%)")
    print(f"      ○ = {fp_mags[3]*100:.1f}% (boundary; might be DE from inside)")

    # --- Iteration ---
    print(f"\n  Iteration from η (equal superposition):")
    state = normalize(np.ones(4, dtype=complex))
    checkpoints = [0, 1, 5, 10, 50, 100, 137, 500, 1000, 2000]

    for target in checkpoints:
        if target == 0:
            pass
        else:
            prev = checkpoints[checkpoints.index(target) - 1]
            for _ in range(target - prev):
                state = T_op @ state
                state = normalize(state)

        mags = np.abs(state)**2
        inw = mags[0] + mags[1]
        outw = mags[2] + mags[3]
        bal = inw / (inw + outw) if (inw + outw) > 1e-10 else 0
        print(f"    n={target:4d}: • = {mags[0]:.4f}, — = {mags[1]:.4f}, "
              f"Φ = {mags[2]:.4f}, ○ = {mags[3]:.4f}  "
              f"◐(diam) = {bal:.4f}")

    # --- What does F² look like? F⁴? ---
    print(f"\n  Powers of F:")
    F_power = np.eye(4, dtype=complex)
    for n in [1, 2, 3, 4, 8, 12]:
        F_power = F_power @ F if n > 0 else np.eye(4)
        if n in [1, 2, 4]:
            dist = np.linalg.norm(F_power - np.eye(4))
            print(f"    F^{n}: ||F^n - I|| = {dist:.8f}")
            if dist < 0.01:
                print(f"           F^{n} ≈ I !")

    return T_op, F, T_ev, T_evec


def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v4: THE GLYPH AS OPERATOR")
    print("◐ = 0.5 is the radius/diameter ratio, inherent in ⊙")
    print("All four beats are EQUAL quarter-turns (π/2 each)")
    print("=" * 70)

    # Three constructions, all with equal quarter-turns
    r1 = analyze_construction(
        build_beats_glyph,
        "GLYPH (adjacent coupling, no self-rotation)"
    )

    r2 = analyze_construction(
        build_beats_glyph_with_self_rotation,
        "GLYPH + SELF-ROTATION (∘ means both coupling AND phase advance)"
    )

    r3 = analyze_construction(
        build_beats_diameter,
        "DIAMETER (each beat couples across the full diameter: d ↔ d+2)"
    )

    # ============================================================
    # COMPARISON
    # ============================================================
    print(f"\n{'='*70}")
    print("COMPARISON: WHICH CONSTRUCTION RESPECTS THE GLYPH?")
    print(f"{'='*70}")

    labels = ["Adjacent", "Adjacent+self", "Diameter"]
    for label, (T_op, F, T_ev, T_evec) in zip(labels, [r1, r2, r3]):
        F_phases = np.sort(np.angle(np.linalg.eigvals(F)))
        phase_sum = np.sum(F_phases)
        F_is_I = np.allclose(F, np.eye(4), atol=1e-6)

        fp_idx = np.argmin(np.abs(np.abs(T_ev) - 1))
        fp = normalize(T_evec[:, fp_idx])
        fp_mags = np.abs(fp)**2
        diam_bal = (fp_mags[0]+fp_mags[1]) / sum(fp_mags)

        print(f"\n  {label}:")
        print(f"    F phase sum = {phase_sum/np.pi:.6f}π")
        print(f"    F ≈ I: {F_is_I}")
        print(f"    ◐(diameter) = {diam_bal:.6f}")
        print(f"    weights: {[f'{m:.4f}' for m in fp_mags]}")


if __name__ == '__main__':
    main()
