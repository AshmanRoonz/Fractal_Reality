"""
Unified Expression T-Operator v3: Pure κ nesting, no smuggled ◐
================================================================

v2 diagnosis: the nesting operator was projecting toward "balanced
state" (equal superposition). But ◐ does NOT appear in the unified
expression. The only parameter is α (inside ⊂[α]).

v3 principle: put in ONLY what the expression contains.
  - Four beats: •, ⊛, —, ⎇, Φ, ✹, ○, ⟳ (the eight stations)
  - Nesting: ⊂[α] (the κ coupling matrix with primary entry α)
  - Closure: the loop ∞ → ... → ∞ (T(1) = 1)

If ◐ = 0.5 is real, it emerges from the fixed point of T.
If it doesn't emerge, either the beat construction or the κ
construction is wrong, and that's diagnostic.

What IS in the expression:
  - Four i-strokes: +i, -1, -i, +1 (the processual phases)
  - Four structural dimensions: 0, 1, 2, 3
  - Entailment (⊢): each beat feeds the next
  - Pairing (∘): structure and process within each beat
  - α: the coupling constant in the nesting
  - Scale labels λ, Λ: the nesting hierarchy
"""

import numpy as np
from scipy.linalg import expm

# ============================================================
# Framework constants (from the expression via T = 3)
# ============================================================
alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
T_triad = 3
P = T_triad + 1          # 4
R = T_triad**2 - 2       # 7
V = 4*T_triad + 1        # 13
SU3 = T_triad**2 - 1     # 8


def make_anti_hermitian(G):
    return (G - np.conj(G.T)) / 2


# ============================================================
# BEATS: built from the i-strokes and dimensional positions
# ============================================================
#
# What the expression gives us for each beat:
#   Beat 1: (•∘⊛) — 0D paired with 0.5D — i-stroke i¹ = +i
#   Beat 2: (—∘⎇) — 1D paired with 1.5D — i-stroke i² = -1
#   Beat 3: (Φ∘✹) — 2D paired with 2.5D — i-stroke i³ = -i
#   Beat 4: (○∘⟳) — 3D paired with 3.5D — i-stroke i⁰ = +1
#
# The ∘ within each beat means the integer and half-integer
# are two views of the same constraint. So each beat IS one
# rotation, and its character is determined by its i-stroke.
#
# The ⊢ between beats means the output of one feeds the input
# of the next. Composition.
#
# What determines the MAGNITUDE of each rotation?
# The expression doesn't give explicit angles. But conservation
# of traversal (0+1+2 = 3) IS in the expression (it's what
# makes ○ close). And v2 showed that the sum of F phases = 0.
#
# Natural choice: each beat rotates by its i-stroke phase,
# scaled by its dimensional position relative to the total
# traversal. The dimensional positions are 0, 1, 2, 3;
# they sum to 6 = T! = 2·T.
#
# Actually, let's be even more minimal. The i-strokes ARE
# the rotations. i¹ = rotation by π/2, i² = rotation by π,
# i³ = rotation by 3π/2, i⁰ = rotation by 0 (or 2π).
# These are the ONLY angles the expression gives us.

def build_beats_v3():
    """
    Build four unitary beat operators.

    Each beat rotates in the plane of (station_d, station_{d+1})
    by the angle given by its i-stroke phase.

    The i-strokes give rotation angles:
      i¹ = +i  →  arg(+i) = +π/2
      i² = -1  →  arg(-1) = π
      i³ = -i  →  arg(-i) = -π/2 (or equivalently 3π/2)
      i⁰ = +1  →  arg(+1) = 0 (or 2π; identity)

    But arg(+1) = 0 would make beat 4 trivial.
    The framework says i⁰ = +1 IS the recursion station:
    the loop has already closed. So beat 4 is MEANT to be
    near-identity: the recursion is the gentlest move.

    However, i⁰ = i⁴ and the full cycle is 2π. So beat 4's
    contribution is that the CUMULATIVE rotation after four
    beats is 2π (= identity). This means:
      π/2 + π + (-π/2) + θ₄ = 2π  →  θ₄ = 2π - π = π

    Wait. Let's just use the actual i-stroke values as
    complex multipliers on the coupling between stations.
    """
    beats = []

    # The four i-strokes as complex phases
    i_phases = [
        1j,        # i¹ = +i  (beat 1)
        -1+0j,     # i² = -1  (beat 2)
        -1j,       # i³ = -i  (beat 3)
        1+0j,      # i⁰ = +1  (beat 4)
    ]

    # Each beat couples station d to station (d+1) mod 4
    # The coupling strength within a single ⊙ is NOT α
    # (α is cross-scale). Within-scale coupling should be
    # determined by the expression's structure alone.
    #
    # What determines within-scale coupling?
    # The ∘ (pairing) means structure and process are
    # "two views of one constraint". The constraint IS
    # the beat. So the coupling is the beat itself.
    #
    # Generator: G[d, d+1] = i_phase × coupling_strength
    # For anti-Hermitian: G[d+1, d] = -conj(G[d, d+1])
    #
    # The coupling strength between adjacent stations:
    # the expression doesn't specify it. But the four
    # beats are the four constraints, and the constraints
    # are the ONLY thing that exists (A0: all else is
    # constraints on the 1). So the coupling IS the
    # constraint, and the constraint's strength is...
    # the dimension at that station.
    #
    # Try: coupling at beat d = (d+0.5)/T_total
    # where T_total = 0+1+2+3 = 6
    # Beat 1: 0.5/6, Beat 2: 1.5/6 = 1/4, Beat 3: 2.5/6, Beat 4: 3.5/6
    #
    # Actually, simplest possible: all four beats have the
    # SAME coupling strength, and only differ in i-stroke phase.
    # The expression treats the four beats symmetrically in form:
    # (X ∘ Y) ⊢ (X ∘ Y) ⊢ (X ∘ Y) ⊢ (X ∘ Y)
    # Same shape, different content. The content is the i-stroke.

    # Let's try coupling = π/(2P) for all beats
    # (one i-stroke divided by pump phases; the quantum of rotation)
    theta = np.pi / (2 * P)  # π/8

    for beat_idx in range(4):
        d = beat_idx      # station index: 0, 1, 2, 3
        d_next = (d + 1) % 4
        i_phase = i_phases[beat_idx]

        G = np.zeros((4, 4), dtype=complex)

        # Self-rotation: the i-stroke rotates station d
        G[d, d] = i_phase * theta

        # Coupling: station d ↔ station (d+1)
        # The i-stroke determines the PHASE of the coupling
        G[d, d_next] = i_phase * theta
        G[d_next, d] = -np.conj(i_phase * theta)

        G = make_anti_hermitian(G)
        B = expm(G)

        beat_names = ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']
        beats.append((beat_names[beat_idx], B))

    return beats


def build_beats_v3b():
    """
    Alternative: dimension-weighted coupling.

    The four structural dimensions are 0, 1, 2, 3.
    Conservation of traversal: 0 + 1 + 2 = 3.

    Each beat's rotation angle = (d + 0.5) × π / A(3)
    where A(3) = 21 (accumulated traversal at boundary).

    This makes the beats proportional to their dimensional
    position, with the half-integer (processual) shift.
    """
    beats = []
    A3 = 21  # A(3) = 3(2·3+1) = 21

    i_phases = [1j, -1+0j, -1j, 1+0j]
    beat_names = ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']

    for beat_idx in range(4):
        d = beat_idx
        d_next = (d + 1) % 4
        i_phase = i_phases[beat_idx]

        # Dimension-weighted angle
        theta = (d + 0.5) * np.pi / A3

        G = np.zeros((4, 4), dtype=complex)
        G[d, d] = i_phase * theta
        G[d, d_next] = i_phase * theta
        G[d_next, d] = -np.conj(i_phase * theta)
        G = make_anti_hermitian(G)

        beats.append((beat_names[beat_idx], expm(G)))

    return beats


def build_beats_v3c():
    """
    Third option: the i-stroke IS the full rotation.

    Beat 1 rotates by arg(i) = π/2
    Beat 2 rotates by arg(-1) = π
    Beat 3 rotates by arg(-i) = -π/2
    Beat 4 rotates by arg(1) = 0 (near-identity)

    Total phase: π/2 + π - π/2 + 0 = π

    Or using the MAGNITUDE of the i-stroke angle:
    π/2 + π + 3π/2 + 2π = 5π
    Mod 2π: π

    The coupling between stations is just the arg itself.
    """
    beats = []
    i_phases = [1j, -1+0j, -1j, 1+0j]
    i_angles = [np.pi/2, np.pi, -np.pi/2, 0.0]
    beat_names = ['(•∘⊛)', '(—∘⎇)', '(Φ∘✹)', '(○∘⟳)']

    for beat_idx in range(4):
        d = beat_idx
        d_next = (d + 1) % 4
        theta = i_angles[beat_idx]

        if abs(theta) < 1e-10:
            # Beat 4: i⁰ = +1, near-identity
            # Use a small angle: α (the only parameter we have)
            theta = alpha * np.pi

        G = np.zeros((4, 4), dtype=complex)

        # Scale the generator so it doesn't blow up for large θ
        scale = theta / P

        G[d, d] = 1j * scale  # always rotate in complex plane
        G[d, d_next] = scale
        G[d_next, d] = -scale
        G = make_anti_hermitian(G)

        beats.append((beat_names[beat_idx], expm(G)))

    return beats


# ============================================================
# NESTING: ⊂[α] as the κ coupling matrix, nothing else
# ============================================================

def build_kappa_nesting():
    """
    The nesting ⊂[α] implemented as the κ matrix.

    Known entries from the framework:
      κ_{0,2} = α  (aperture-to-field; the primary coupling)
      κ_{d,d} = 1  (each station maps to itself at next scale)

    The nesting couples ⊙λ into ⊙Λ. The diagonal is identity
    (each station persists across scale). The off-diagonal
    κ_{0,2} = α couples the aperture into the field of the
    greater whole.

    This is NOT unitary (it has an off-diagonal perturbation
    of the identity). It IS a contraction on some subspace.

    No projection. No balance target. Just κ.
    """
    kappa = np.eye(4, dtype=complex)

    # Primary coupling: κ_{0,2} = α
    # Aperture (0D) couples to field (2D) of the greater whole
    kappa[0, 2] = alpha
    kappa[2, 0] = alpha  # symmetric: field also couples back to aperture

    # That's it. That's all ⊂[α] gives us at this resolution.
    # Other entries (Cabibbo, Weinberg, Higgs, gravity) can be
    # added later as we derive them.

    return kappa


def build_kappa_nesting_full():
    """
    Fuller κ matrix with all known couplings.

    κ_{0,2} = α         (aperture-to-field; electromagnetic)
    κ_{3,3} = 1 - α_G   (gravity correction at boundary)
    κ_{1,2} = sin(θ_C)·α  (Cabibbo-like; line-to-field)
    κ_{2,2} = 1 - sin²(θ_W)·α  (Weinberg-like; field self-coupling)

    Still no ◐. Every entry comes from the framework's
    derived constants.
    """
    alpha_G = alpha**21 * phi**2 / 2
    sin_theta_C = 0.2243  # from framework: α^(1/2 + 3α/7) × 8/3
    sin2_theta_W = 0.23122  # from framework: 3/13 + 5α/81

    kappa = np.eye(4, dtype=complex)

    # Primary: aperture ↔ field
    kappa[0, 2] = alpha
    kappa[2, 0] = alpha

    # Gravity: boundary self-coupling correction
    kappa[3, 3] = 1 - alpha_G

    # Cabibbo: line ↔ field (inter-generation mixing)
    kappa[1, 2] = sin_theta_C * alpha
    kappa[2, 1] = sin_theta_C * alpha

    # Weinberg: field self-coupling correction
    kappa[2, 2] = 1 - sin2_theta_W * alpha

    return kappa


# ============================================================
# Build T and iterate
# ============================================================

def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(4, dtype=complex) / 2.0
    return state / norm


def build_and_analyze(beats_func, kappa_func, label):
    """Build T from given beats and kappa, analyze everything."""

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")

    # Build components
    beats = beats_func()
    kappa = kappa_func()

    # Compose F = B4 ∘ B3 ∘ B2 ∘ B1
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F

    # T = κ ∘ F
    T_op = kappa @ F

    # --- Check F ---
    F_unitary = np.allclose(F @ np.conj(F.T), np.eye(4), atol=1e-10)
    F_ev = np.linalg.eigvals(F)
    F_phases = np.sort(np.angle(F_ev))
    phase_sum = np.sum(F_phases)

    print(f"\n  F unitary: {F_unitary}")
    print(f"  F phases: {[f'{np.degrees(p):.3f}°' for p in F_phases]}")
    print(f"  Phase sum: {np.degrees(phase_sum):.4f}° = {phase_sum/np.pi:.6f}π")

    # --- Check κ ---
    kappa_ev = np.linalg.eigvals(kappa)
    print(f"\n  κ eigenvalues: {[f'{ev:.8f}' for ev in np.sort(kappa_ev)[::-1]]}")
    print(f"  κ is identity + O(α): {np.allclose(kappa, np.eye(4), atol=0.01)}")

    # --- T eigenvalues ---
    T_ev, T_evec = np.linalg.eig(T_op)
    idx = np.argsort(-np.abs(T_ev))
    T_ev = T_ev[idx]
    T_evec = T_evec[:, idx]

    print(f"\n  T eigenvalues:")
    for i, ev in enumerate(T_ev):
        mag = np.abs(ev)
        phase = np.degrees(np.angle(ev))
        print(f"    λ_{i}: |λ| = {mag:.10f}, phase = {phase:.4f}°, value = {ev:.8f}")

    # --- Fixed point analysis ---
    # The dominant eigenvector of T (closest |λ| to 1)
    fp_idx = np.argmin(np.abs(np.abs(T_ev) - 1))
    fp = normalize(T_evec[:, fp_idx])
    fp_mags = np.abs(fp)**2

    print(f"\n  Fixed point (dominant eigenvector):")
    print(f"    |z|²: • = {fp_mags[0]:.6f}, — = {fp_mags[1]:.6f}, Φ = {fp_mags[2]:.6f}, ○ = {fp_mags[3]:.6f}")

    # ◐ = •/(•+○) — does it emerge as 0.5?
    if fp_mags[0] + fp_mags[3] > 1e-10:
        balance = fp_mags[0] / (fp_mags[0] + fp_mags[3])
    else:
        balance = None
    print(f"    ◐ = •/(•+○) = {balance:.6f}" if balance else "    ◐ undefined")

    # Alternative balance: is the fixed point equidistant from
    # all-• and all-○? (Geometric balance, not weight balance)
    dist_to_soul = np.linalg.norm(fp - normalize(np.array([1,0,0,0], dtype=complex)))
    dist_to_body = np.linalg.norm(fp - normalize(np.array([0,0,0,1], dtype=complex)))
    geo_balance = dist_to_soul / (dist_to_soul + dist_to_body)
    print(f"    geometric ◐ (distance ratio): {geo_balance:.6f}")

    # What about the energy budget? Compare to cosmological 5/27/68
    total = sum(fp_mags)
    pct = fp_mags / total * 100
    print(f"    as percentages: • = {pct[0]:.1f}%, — = {pct[1]:.1f}%, Φ = {pct[2]:.1f}%, ○ = {pct[3]:.1f}%")

    # --- Iteration ---
    print(f"\n  Iteration (3000 steps from equal superposition):")
    state = normalize(np.ones(4, dtype=complex))
    for step in [0, 10, 50, 100, 137, 500, 1000, 3000]:
        if step == 0:
            mags = np.abs(state)**2
        else:
            for _ in range(step - (0 if step == 10 else [10,50,100,137,500,1000][
                [10,50,100,137,500,1000,3000].index(step)-1] if step > 10 else 0)):
                state = T_op @ state
                state = normalize(state)
            mags = np.abs(state)**2

        bal = mags[0]/(mags[0]+mags[3]) if (mags[0]+mags[3]) > 1e-10 else 0
        print(f"    n={step:4d}: • = {mags[0]:.4f}, — = {mags[1]:.4f}, Φ = {mags[2]:.4f}, ○ = {mags[3]:.4f}  ◐ = {bal:.4f}")

    return T_op, F, kappa, T_ev, T_evec


def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v3")
    print("NO SMUGGLED ◐. ONLY WHAT THE EXPRESSION CONTAINS.")
    print("1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]")
    print("=" * 70)

    # Test all three beat constructions with minimal κ
    print("\n" + "#" * 70)
    print("# MINIMAL κ (only κ_{0,2} = α)")
    print("#" * 70)

    results = {}

    results['3a_min'] = build_and_analyze(
        build_beats_v3, build_kappa_nesting,
        "v3a: uniform coupling (π/8) + minimal κ"
    )

    results['3b_min'] = build_and_analyze(
        build_beats_v3b, build_kappa_nesting,
        "v3b: dimension-weighted coupling + minimal κ"
    )

    results['3c_min'] = build_and_analyze(
        build_beats_v3c, build_kappa_nesting,
        "v3c: i-stroke angles + minimal κ"
    )

    # Test with full κ
    print("\n" + "#" * 70)
    print("# FULL κ (all known coupling entries)")
    print("#" * 70)

    results['3a_full'] = build_and_analyze(
        build_beats_v3, build_kappa_nesting_full,
        "v3a: uniform coupling + full κ"
    )

    results['3c_full'] = build_and_analyze(
        build_beats_v3c, build_kappa_nesting_full,
        "v3c: i-stroke angles + full κ"
    )

    # ============================================================
    # SUMMARY: which construction produces ◐ closest to 0.5?
    # ============================================================
    print("\n" + "=" * 70)
    print("SUMMARY: DOES ◐ = 0.5 EMERGE?")
    print("=" * 70)

    for name, (T_op, F, kappa, T_ev, T_evec) in results.items():
        fp_idx = np.argmin(np.abs(np.abs(T_ev) - 1))
        fp = normalize(T_evec[:, fp_idx])
        fp_mags = np.abs(fp)**2
        bal = fp_mags[0]/(fp_mags[0]+fp_mags[3]) if (fp_mags[0]+fp_mags[3]) > 1e-10 else None

        F_phases = np.sort(np.angle(np.linalg.eigvals(F)))
        phase_sum = np.sum(F_phases)

        print(f"\n  {name}:")
        print(f"    ◐ = {bal:.6f}" if bal else f"    ◐ undefined")
        print(f"    station weights: {[f'{m:.4f}' for m in fp_mags]}")
        print(f"    F phase sum: {phase_sum/np.pi:.6f}π")

        # Check for cosmological ratios
        # Framework predicts: vis ~5%, DM ~26%, DE ~69%
        # These map to right half-plane, left half-plane, field
        # In our basis: (•+○) ~ vis, (—) ~ DM?, (Φ) ~ DE?
        vis = (fp_mags[0] + fp_mags[3]) * 100
        dm_candidate = fp_mags[1] * 100
        de_candidate = fp_mags[2] * 100
        print(f"    cosmological? (•+○)={vis:.1f}%, —={dm_candidate:.1f}%, Φ={de_candidate:.1f}%")

    # ============================================================
    # What if we DON'T normalize? Let the norm evolve.
    # The expression says 1 = [...], meaning the WHOLE thing
    # equals 1. Maybe the norm IS the observable.
    # ============================================================
    print("\n" + "=" * 70)
    print("BONUS: ITERATION WITHOUT NORMALIZATION")
    print("(Does |⊙|² naturally approach 1?)")
    print("=" * 70)

    # Use v3a with minimal κ
    beats = build_beats_v3()
    kappa = build_kappa_nesting()
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F
    T_op = kappa @ F

    state = np.ones(4, dtype=complex) / 2.0  # start with |⊙|² = 1

    print(f"\n  Starting |⊙|² = {np.sum(np.abs(state)**2):.6f}")

    for step in range(1, 201):
        state = T_op @ state
        norm_sq = np.sum(np.abs(state)**2)
        if step in [1, 5, 10, 20, 50, 100, 137, 200]:
            mags = np.abs(state)**2
            print(f"    n={step:3d}: |⊙|² = {norm_sq:.8f}, weights = [{', '.join([f'{m:.6f}' for m in mags])}]")


if __name__ == '__main__':
    main()
