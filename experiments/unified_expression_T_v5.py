"""
Unified Expression T-Operator v5: The Sphere and Faraday
==========================================================

v4 insight: ◐ = 0.5 is the radius/diameter ratio, built into ⊙.
v4 result: diameter construction gives ◐ = 0.5 exactly, F² = I,
           eigenvalue splitting ±α.

v5 insight: ○ is 3D, not 2D. ⊙ is a sphere, not a circle.
In a sphere:
  - • is the center (0D point)
  - — is the radius (1D line from center to surface)
  - Φ is the surface/field (2D, wraps the interior, mediates everything)
  - ○ is the boundary (3D, the full volumetric closure)

Faraday connection (§27.7r):
  i IS d/dt on an oscillating 2D field.
  EMF = -dΦ/dt: the rate of change of the 2D field through
  a closed surface induces a response at the boundary.
  Lenz's minus sign = ○ filtering the pump to conserve ⊙.

This changes the operator topology:
  v4 (circle):  two independent diameters: {•,Φ} and {—,○}
  v5 (sphere):  Φ as hub; all stations coupled THROUGH the field

In a sphere, Φ mediates EVERYTHING. The field is not one of four
equal stations; it's the medium through which the other three
communicate. Star topology, not ring or diameter.

The beats become Faraday inductions:
  Each beat: d/dt applied to Φ at a specific phase (i-stroke)
  → induces response at ○ (boundary, Lenz's law)
  → connects through • (aperture, source of flux)
  → along — (radial path)
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
# SPHERE TOPOLOGY: Φ as hub
# ============================================================
#
# In the sphere, Φ (station 2) mediates all couplings:
#   • ↔ Φ  (aperture to field; flux from center)
#   — ↔ Φ  (line to field; radial path through the field)
#   ○ ↔ Φ  (boundary to field; Faraday induction, EMF = -dΦ/dt)
#
# Each beat applies d/dt to Φ at a different i-stroke phase.
# The response at each station depends on its relationship
# to the field:
#   • contributes flux (source)
#   — carries the flux (radial conductor)
#   ○ receives the induction (boundary response)
#   Φ mediates (the 2D surface itself)
#
# The Faraday structure: when Φ changes, ○ responds with
# a MINUS sign (Lenz's law). This is the ○ filtering the
# pump to conserve the whole.

def build_beats_sphere():
    """
    Four beats as Faraday inductions through a spherical ⊙.

    Each beat:
    1. Active station applies its i-stroke
    2. This change propagates through Φ (the mediator)
    3. Other stations respond via their coupling to Φ

    Generator structure:
      G[active, Φ] = i-stroke × θ  (active station drives Φ)
      G[Φ, active] = -conj(...)     (anti-Hermitian)
      All four beats have equal magnitude (quarter-turns: θ = π/2)
      The i-stroke determines the PHASE of the drive.
    """
    beats = []
    theta = np.pi / 2  # quarter-turn (the radius in phase space)

    # Station indices: 0=•, 1=—, 2=Φ, 3=○
    PHI = 2  # Φ is the hub

    # The four beats and their i-strokes
    beat_config = [
        ('(•∘⊛)', 0, 1j),      # Beat 1: • drives Φ with phase +i
        ('(—∘⎇)', 1, -1+0j),   # Beat 2: — drives Φ with phase -1
        ('(Φ∘✹)', 2, -1j),     # Beat 3: Φ self-drives with phase -i (emergence)
        ('(○∘⟳)', 3, 1+0j),    # Beat 4: ○ drives Φ with phase +1 (recursion)
    ]

    for name, active, i_phase in beat_config:
        G = np.zeros((4, 4), dtype=complex)

        if active == PHI:
            # Beat 3 (Φ∘✹): Φ is both source and hub.
            # Emergence: Φ radiates outward to all other stations.
            # This is the Faraday moment: changing field induces
            # responses at •, —, and ○ simultaneously.
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T_triad  # divided by T (three targets)
                G[PHI, other] = coupling
                G[other, PHI] = -np.conj(coupling)
            # Self-rotation of Φ
            G[PHI, PHI] = i_phase * theta / T_triad
        else:
            # Beats 1, 2, 4: a station drives Φ
            coupling = i_phase * theta
            G[active, PHI] = coupling
            G[PHI, active] = -np.conj(coupling)

        G = make_anti_hermitian(G)
        beats.append((name, expm(G)))

    return beats


def build_beats_sphere_v2():
    """
    Alternative: ALL beats couple through Φ to ALL stations.

    In a sphere, every change at any station propagates through
    the entire field. The i-stroke determines the phase; the
    active station determines the direction; but ALL stations
    feel the change.

    Generator: star topology centered on Φ.
      For each beat:
        G[active, PHI] = i_phase × θ         (active → Φ)
        G[PHI, other]  = i_phase × θ × (α)   (Φ → other, weaker)

    The coupling from Φ to non-active stations is weaker by α
    because cross-station propagation goes through the nesting
    (and α IS the cross-station coupling).
    """
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
            # Φ drives all others equally
            for other in [0, 1, 3]:
                coupling = i_phase * theta / T_triad
                G[PHI, other] = coupling
                G[other, PHI] = -np.conj(coupling)
        else:
            # Active drives Φ (primary)
            G[active, PHI] = i_phase * theta
            G[PHI, active] = -np.conj(i_phase * theta)

            # Φ redistributes to other stations (secondary, via α)
            for other in [0, 1, 3]:
                if other != active:
                    secondary = i_phase * theta * alpha
                    G[PHI, other] = secondary
                    G[other, PHI] = -np.conj(secondary)

        G = make_anti_hermitian(G)
        beats.append((name, expm(G)))

    return beats


def build_beats_faraday():
    """
    The purest Faraday reading.

    Faraday's law: EMF = -dΦ/dt
    In the framework: the time derivative of the 2D field
    induces a response at the boundary.

    i IS d/dt (§27.7r). So each beat's i-stroke IS a
    time derivative of Φ. The response at ○ has a minus
    sign (Lenz's law = conservation).

    Structure:
      - • is the source of flux (drives Φ)
      - — is the radial path (carries flux from • to ○)
      - Φ is the field (the thing being differentiated)
      - ○ is the boundary (receives the induction with minus sign)

    Beat 1 (•∘⊛): • generates flux → Φ grows → i¹ = +i
    Beat 2 (—∘⎇): — commits the flux path → Φ branches → i² = -1
    Beat 3 (Φ∘✹): Φ emerges outward → ○ responds (Lenz) → i³ = -i
    Beat 4 (○∘⟳): ○ closes → flux returns to • → i⁰ = +1

    The Lenz minus sign appears in beat 3: when Φ drives ○,
    the coupling has a minus sign (○ opposes the change to
    conserve the total flux = conserve the 1).
    """
    beats = []
    theta = np.pi / 2
    # indices: 0=•, 1=—, 2=Φ, 3=○

    # Beat 1: • → Φ (source generates flux in field)
    G1 = np.zeros((4, 4), dtype=complex)
    G1[0, 2] = 1j * theta       # • drives Φ with +i
    G1[2, 0] = -(-1j * theta)   # anti-Hermitian
    G1 = make_anti_hermitian(G1)

    # Beat 2: — → Φ (radial path commits flux through field)
    # i² = -1: the i-turn, irreversible
    G2 = np.zeros((4, 4), dtype=complex)
    G2[1, 2] = (-1+0j) * theta   # — drives Φ with -1
    G2[2, 1] = -(1+0j) * theta   # anti-Hermitian
    G2 = make_anti_hermitian(G2)

    # Beat 3: Φ → ○ (field induces at boundary; FARADAY)
    # i³ = -i: emergence
    # Lenz's law: ○ responds with MINUS sign
    G3 = np.zeros((4, 4), dtype=complex)
    G3[2, 3] = (-1j) * theta     # Φ drives ○ with -i
    G3[3, 2] = -(1j) * theta     # anti-Hermitian (Lenz's minus)
    G3 = make_anti_hermitian(G3)

    # Beat 4: ○ → • (boundary closes; recursion returns to center)
    # i⁰ = +1: identity; the loop closes
    G4 = np.zeros((4, 4), dtype=complex)
    G4[3, 0] = (1+0j) * theta    # ○ drives • with +1
    G4[0, 3] = -(1+0j) * theta   # anti-Hermitian
    G4 = make_anti_hermitian(G4)

    beats = [
        ('(•∘⊛)', expm(G1)),
        ('(—∘⎇)', expm(G2)),
        ('(Φ∘✹)', expm(G3)),
        ('(○∘⟳)', expm(G4)),
    ]

    return beats


def build_beats_faraday_sphere():
    """
    Combined: Faraday induction through a sphere.

    The sequential Faraday path (•→Φ→○→•) from build_beats_faraday,
    BUT with Φ as hub: every beat also has secondary coupling
    through Φ to all other stations.

    Primary: the Faraday circuit (•→Φ, —→Φ, Φ→○, ○→•)
    Secondary: Φ redistributes to all (sphere mediation)

    The secondary coupling is weaker by α (cross-station
    coupling through the nesting).
    """
    beats = []
    theta = np.pi / 2

    # Primary couplings (the Faraday circuit)
    primaries = [
        ('(•∘⊛)', 0, 2, 1j),      # • → Φ
        ('(—∘⎇)', 1, 2, -1+0j),   # — → Φ
        ('(Φ∘✹)', 2, 3, -1j),     # Φ → ○ (Faraday induction)
        ('(○∘⟳)', 3, 0, 1+0j),    # ○ → • (recursion)
    ]

    for name, src, dst, i_phase in primaries:
        G = np.zeros((4, 4), dtype=complex)

        # Primary coupling
        G[src, dst] = i_phase * theta
        G[dst, src] = -np.conj(i_phase * theta)

        # Secondary: Φ (station 2) redistributes to all other stations
        # This is the sphere mediation: the field connects everything
        PHI = 2
        for other in [0, 1, 3]:
            if other != src and other != dst:
                # Φ couples to other stations with strength α
                secondary = i_phase * theta * alpha
                if src == PHI or dst == PHI:
                    G[PHI, other] += secondary
                    G[other, PHI] += -np.conj(secondary)

        G = make_anti_hermitian(G)
        beats.append((name, expm(G)))

    return beats


# ============================================================
# NESTING: ⊂[α] as pure κ
# ============================================================

def build_kappa():
    kappa = np.eye(4, dtype=complex)
    kappa[0, 2] = alpha
    kappa[2, 0] = alpha
    return kappa


# ============================================================
# Analysis
# ============================================================

def analyze(beats_func, label):
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

    # F properties
    F_unitary = np.allclose(F @ np.conj(F.T), np.eye(4), atol=1e-10)
    F_ev = np.linalg.eigvals(F)
    F_phases = np.sort(np.angle(F_ev))
    phase_sum = np.sum(np.angle(F_ev))

    print(f"\n  F unitary: {F_unitary}")
    print(f"  F phases: {[f'{np.degrees(p):.3f}°' for p in F_phases]}")
    print(f"  Phase sum: {np.degrees(phase_sum):.4f}° = {phase_sum/np.pi:.6f}π")

    F2 = F @ F
    F2_is_I = np.allclose(F2, np.eye(4), atol=1e-6)
    print(f"  F² ≈ I: {F2_is_I}")
    print(f"  ||F² - I|| = {np.linalg.norm(F2 - np.eye(4)):.8f}")

    # F⁴
    F4 = F2 @ F2
    F4_is_I = np.allclose(F4, np.eye(4), atol=1e-6)
    print(f"  F⁴ ≈ I: {F4_is_I}")
    print(f"  ||F⁴ - I|| = {np.linalg.norm(F4 - np.eye(4)):.8f}")

    # T eigenvalues
    T_ev, T_evec = np.linalg.eig(T_op)
    idx = np.argsort(-np.abs(T_ev))
    T_ev = T_ev[idx]
    T_evec = T_evec[:, idx]

    print(f"\n  T eigenvalues:")
    for i, ev in enumerate(T_ev):
        mag = np.abs(ev)
        phase = np.degrees(np.angle(ev))
        # Check if magnitude matches 1±α or 1±kα
        delta = mag - 1
        if abs(delta) > 1e-10:
            ratio = delta / alpha
            print(f"    λ_{i}: |λ| = {mag:.10f}, phase = {phase:.4f}°, "
                  f"(|λ|-1)/α = {ratio:.4f}")
        else:
            print(f"    λ_{i}: |λ| = {mag:.10f}, phase = {phase:.4f}°")

    # Fixed point
    fp_idx = np.argmin(np.abs(np.abs(T_ev) - 1))
    fp = normalize(T_evec[:, fp_idx])
    fp_mags = np.abs(fp)**2

    print(f"\n  Fixed point:")
    print(f"    |z|²: • = {fp_mags[0]:.6f}, — = {fp_mags[1]:.6f}, "
          f"Φ = {fp_mags[2]:.6f}, ○ = {fp_mags[3]:.6f}")

    # Multiple ◐ readings
    readings = {}

    # ◐ as •/(•+○)
    if fp_mags[0] + fp_mags[3] > 1e-10:
        readings['•/(•+○)'] = fp_mags[0] / (fp_mags[0] + fp_mags[3])

    # ◐ as diameter midpoint (•+—)/(total)
    readings['(•+—)/total'] = (fp_mags[0] + fp_mags[1])

    # ◐ as inward/total
    readings['inward/total'] = (fp_mags[0] + fp_mags[1])

    # Right half / total (i⁰+i¹ quadrants = •+○)
    readings['right_half'] = fp_mags[0] + fp_mags[3]

    # Left half / total (i²+i³ quadrants = —+Φ)
    readings['left_half'] = fp_mags[1] + fp_mags[2]

    print(f"\n  ◐ readings:")
    for name, val in readings.items():
        marker = " ← ◐!" if abs(val - 0.5) < 0.02 else ""
        print(f"    {name} = {val:.6f}{marker}")

    # Cosmological readings
    print(f"\n  Cosmological budget (target: 5/27/68):")

    # Reading 1: right half = visible, left half = dark matter, Φ = dark energy
    vis1 = (fp_mags[0] + fp_mags[3]) * 100
    dm1 = fp_mags[1] * 100
    de1 = fp_mags[2] * 100
    print(f"    R1 (•+○ / — / Φ):     vis={vis1:.1f}%, DM={dm1:.1f}%, DE={de1:.1f}%")

    # Reading 2: from §10.10a i-cycle quadrants
    vis2 = (fp_mags[0] + fp_mags[3]) * 100
    dm2 = (fp_mags[1] + fp_mags[2]) * 100
    de_implicit = "field itself"
    print(f"    R2 (right/left half):  right={vis2:.1f}%, left={dm2:.1f}%")

    # Reading 3: Φ is DE from the scale above (○_λ = Φ_Λ)
    print(f"    R3 (○ as Φ_Λ):        ○={fp_mags[3]*100:.1f}% (target 69%)")

    # Iteration
    print(f"\n  Iteration from η:")
    state = normalize(np.ones(4, dtype=complex))
    checkpoints = [0, 1, 10, 50, 100, 137, 500, 1000, 2000]
    prev = 0

    for target in checkpoints:
        for _ in range(target - prev):
            state = T_op @ state
            state = normalize(state)
        prev = target

        mags = np.abs(state)**2
        inw = mags[0] + mags[1]
        outw = mags[2] + mags[3]
        diam_bal = inw / (inw + outw) if (inw + outw) > 1e-10 else 0
        right = mags[0] + mags[3]
        left = mags[1] + mags[2]

        print(f"    n={target:4d}: •={mags[0]:.4f} —={mags[1]:.4f} "
              f"Φ={mags[2]:.4f} ○={mags[3]:.4f}  "
              f"◐(d)={diam_bal:.4f}  R/L={right:.3f}/{left:.3f}")

    return T_op, F, T_ev, T_evec, fp_mags


def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v5: SPHERE + FARADAY")
    print("○ is 3D (sphere). Φ mediates everything. i = d/dt on Φ.")
    print("=" * 70)

    results = {}

    results['sphere_hub'] = analyze(
        build_beats_sphere,
        "SPHERE HUB: Φ as central mediator, all stations couple through Φ"
    )

    results['sphere_v2'] = analyze(
        build_beats_sphere_v2,
        "SPHERE v2: Φ hub + secondary α-redistribution"
    )

    results['faraday'] = analyze(
        build_beats_faraday,
        "FARADAY CIRCUIT: •→Φ→○→• (sequential induction, no hub)"
    )

    results['faraday_sphere'] = analyze(
        build_beats_faraday_sphere,
        "FARADAY + SPHERE: sequential circuit + Φ hub redistribution"
    )

    # ============================================================
    # COMPARISON
    # ============================================================
    print(f"\n{'='*70}")
    print("COMPARISON ACROSS ALL CONSTRUCTIONS")
    print(f"{'='*70}")

    # Include v4 diameter for reference
    from unified_expression_T_v4 import build_beats_diameter
    results['v4_diameter'] = analyze(
        build_beats_diameter,
        "v4 DIAMETER (reference): d ↔ d+2, ◐=0.5 conserved"
    )

    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"  {'Construction':<25} {'F²=I?':>6} {'Σphase':>10} {'•':>7} {'—':>7} {'Φ':>7} {'○':>7} {'◐(d)':>7}")
    print(f"  {'-'*25} {'-'*6} {'-'*10} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")

    for name, (T_op, F, T_ev, T_evec, fp_mags) in results.items():
        F2_I = np.allclose(F @ F, np.eye(4), atol=1e-6)
        psum = np.sum(np.angle(np.linalg.eigvals(F))) / np.pi
        dbal = (fp_mags[0]+fp_mags[1])

        print(f"  {name:<25} {'Y' if F2_I else 'N':>6} {psum:>9.4f}π "
              f"{fp_mags[0]:>7.4f} {fp_mags[1]:>7.4f} "
              f"{fp_mags[2]:>7.4f} {fp_mags[3]:>7.4f} {dbal:>7.4f}")


if __name__ == '__main__':
    main()
