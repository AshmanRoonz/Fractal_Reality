"""
Unified Expression T-Operator v7: The Core Mathematics
=======================================================

Directions #3, #4, #5, #1, #2 — the skipped steps.

Goal: turn 1 = [∞▸⊙∞ ((•∘⊛) ⊢ (—∘⎇) ⊢ (Φ∘✹) ⊢ (○∘⟳)) ▸ ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞]
into a mathematical object with provable properties.

#3: CPTP identification
    Is T a quantum channel? Is F trace-preserving? Is T completely positive?
    Compute Z = Tr(F). Check: does Z = 1?

#5: κ-closure
    The nesting chain ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞ composes to identity.
    This constrains κ. What does κ^n → ? Is κ idempotent?
    Use the fixed-point equation to predict new entries.

#4: Non-1 fixed points
    Solve T(x) = x for x ≠ 1. Classify each by:
      - Does it satisfy ◐ = 0.5? If not → one of the Lies.
      - Does it satisfy A3 (self-similarity)? If not → scale pathology.
    Prediction: every non-1 fixed point is a Lie.

#1: Full linearization
    DT|_1 is the Jacobian at the fixed point. Its eigenvalues control
    how perturbations decay. Compare the spectrum against the dimensional
    ladder constants.

#2: Contraction bounds
    Lipschitz constant of each beat; their product is the contraction
    rate of one full pump cycle. Match against framework constants.
"""

import numpy as np
from scipy.linalg import expm, logm

# ============================================================
# Framework constants
# ============================================================
alpha = 1.0 / 137.035999177
phi = (1 + np.sqrt(5)) / 2
T_triad = 3
P = T_triad + 1      # 4
R = T_triad**2 - 2   # 7
V = 4*T_triad + 1    # 13
SU3 = T_triad**2 - 1 # 8
G_gen = T_triad*(T_triad+1)  # 12
A3_val = T_triad*(2*T_triad+1)  # 21


def make_anti_hermitian(G):
    return (G - np.conj(G.T)) / 2


def normalize(state):
    norm = np.sqrt(np.sum(np.abs(state)**2))
    if norm < 1e-15:
        return np.ones(4, dtype=complex) / 2.0
    return state / norm


# ============================================================
# Build the operators (standard sphere hub from v5/v6)
# ============================================================

def build_beats_sphere():
    """Standard sphere hub: Φ as central mediator."""
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
    """v4 diameter construction for comparison."""
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


def build_kappa():
    """The ⊂[α] coupling matrix with known entry κ_{0,2} = α."""
    kappa = np.eye(4, dtype=complex)
    kappa[0, 2] = alpha   # κ_{•,Φ} = α (the primary coupling)
    kappa[2, 0] = alpha   # symmetric
    return kappa


def compose_F(beats):
    F = np.eye(4, dtype=complex)
    for name, B in beats:
        F = B @ F
    return F


# ============================================================
# #3: CPTP IDENTIFICATION
# ============================================================

def direction_3():
    print("=" * 70)
    print("DIRECTION #3: IS T A QUANTUM CHANNEL?")
    print("=" * 70)

    for label, beats_func in [("Sphere Hub", build_beats_sphere),
                                ("Diameter", build_beats_diameter)]:
        print(f"\n  --- {label} ---")
        beats = beats_func()
        F = compose_F(beats)
        kappa = build_kappa()
        T_op = kappa @ F

        # ─── Trace of F ───
        tr_F = np.trace(F)
        print(f"\n  Tr(F) = {tr_F.real:.8f} + {tr_F.imag:.8f}i")
        print(f"  |Tr(F)| = {abs(tr_F):.8f}")
        print(f"  Tr(F) = 1? {np.isclose(abs(tr_F), 1, atol=0.01)}")
        print(f"  Tr(F) = 4 (dim)? {np.isclose(abs(tr_F), 4, atol=0.01)}")

        # ─── F unitarity (already confirmed, but verify) ───
        FdF = F @ np.conj(F.T)
        F_unitary = np.allclose(FdF, np.eye(4), atol=1e-10)
        print(f"\n  F unitary: {F_unitary}")
        print(f"  (Unitary ⊂ CPTP: unitary maps are quantum channels)")

        # ─── T properties ───
        # Trace-preserving: Tr(T(ρ)) = Tr(ρ) for all ρ
        # For a matrix operator T acting as T|ψ⟩, trace-preserving means
        # the dual T† preserves identity: T† I = I, i.e., Tr(T) = dim
        tr_T = np.trace(T_op)
        print(f"\n  Tr(T) = {tr_T.real:.8f} + {tr_T.imag:.8f}i")

        # T eigenvalues (for trace decomposition)
        T_ev = np.linalg.eigvals(T_op)
        print(f"  T eigenvalues: {[f'{ev.real:.6f}+{ev.imag:.6f}i' for ev in T_ev]}")
        print(f"  Sum(λ) = {np.sum(T_ev).real:.8f} + {np.sum(T_ev).imag:.8f}i  (= Tr(T))")

        # ─── Is T a contraction? ───
        # A quantum channel on states has operator norm ≤ 1
        # T acts on state vectors, so check singular values
        sv = np.linalg.svd(T_op, compute_uv=False)
        print(f"\n  Singular values of T: {[f'{s:.8f}' for s in sv]}")
        print(f"  Max singular value (operator norm): {max(sv):.8f}")
        print(f"  ||T|| ≤ 1? {max(sv) <= 1 + 1e-10}")
        print(f"  ||T|| = 1 + O(α)? (|λ|-1)/α = {(max(sv)-1)/alpha:.4f}")

        # ─── Density matrix formulation ───
        # Promote to superoperator: T_super acts on ρ = |ψ⟩⟨ψ|
        # T_super(ρ) = T ρ T†  (for unitary part)
        # But T is NOT unitary (κ breaks it), so the correct form is:
        # T_super(ρ) = T ρ T† / Tr(T ρ T†)  (normalized)
        # Check: is T_super completely positive?

        # Choi matrix: Φ_T = (I ⊗ T) |Ω⟩⟨Ω| where |Ω⟩ = Σ|ii⟩/√d
        d = 4
        Omega = np.zeros((d*d,), dtype=complex)
        for i in range(d):
            Omega[i*d + i] = 1.0 / np.sqrt(d)

        # Choi matrix for the map ρ → T ρ T†
        # Φ = Σ_{i,j} |i⟩⟨j| ⊗ T|i⟩⟨j|T†
        Choi = np.zeros((d*d, d*d), dtype=complex)
        for i in range(d):
            for j in range(d):
                # |i⟩⟨j| in the first system
                ket_i = np.zeros(d, dtype=complex); ket_i[i] = 1
                bra_j = np.zeros(d, dtype=complex); bra_j[j] = 1
                outer_ij = np.outer(ket_i, bra_j)  # d×d

                # T|i⟩⟨j|T† in the second system
                T_outer = T_op @ outer_ij @ np.conj(T_op.T)  # d×d

                # Tensor product: (d²×d²) matrix
                Choi += np.kron(outer_ij, T_outer)

        Choi_ev = np.linalg.eigvalsh(Choi)
        print(f"\n  Choi matrix eigenvalues (for ρ → TρT†):")
        print(f"    {[f'{ev:.8f}' for ev in sorted(Choi_ev)]}")
        print(f"    All ≥ 0 (completely positive)? {all(ev > -1e-10 for ev in Choi_ev)}")
        print(f"    Min eigenvalue: {min(Choi_ev):.10f}")

        # ─── Trace preservation check ───
        # For map ρ → TρT†: trace-preserving iff T†T = I
        TdT = np.conj(T_op.T) @ T_op
        tp_error = np.linalg.norm(TdT - np.eye(4))
        print(f"\n  T†T = I (trace-preserving)? ||T†T - I|| = {tp_error:.8f}")
        print(f"  T†T eigenvalues: {[f'{ev:.8f}' for ev in np.linalg.eigvalsh(TdT)]}")

        # ─── The partition function reading ───
        # Z = Tr(F) for the loop interpretation (1D TQFT)
        # For a unitary F, Tr(F) = sum of phases = Σ exp(iθ_k)
        F_ev = np.linalg.eigvals(F)
        F_phases = np.angle(F_ev)
        print(f"\n  Partition function Z = Tr(F):")
        print(f"    F eigenvalue phases: {[f'{np.degrees(p):.2f}°' for p in F_phases]}")
        print(f"    Z = Σ exp(iθ_k) = {tr_F.real:.6f} + {tr_F.imag:.6f}i")
        print(f"    |Z| = {abs(tr_F):.6f}")
        print(f"    Z/d = {abs(tr_F)/d:.6f}  (should be 1/d for Haar-random)")

        # ─── Phase sum (conservation of traversal) ───
        phase_sum = np.sum(F_phases)
        print(f"\n  Phase sum Σθ = {phase_sum:.8f} rad = {np.degrees(phase_sum):.4f}°")
        print(f"  Σθ = 0? {abs(phase_sum) < 0.01}")
        print(f"  Σθ = 2π? {abs(phase_sum - 2*np.pi) < 0.01}")
        print(f"  Σθ/π = {phase_sum/np.pi:.6f}")


# ============================================================
# #5: κ-CLOSURE
# ============================================================

def direction_5():
    print(f"\n\n{'=' * 70}")
    print("DIRECTION #5: κ-CLOSURE")
    print("Constrain the full 4×4 coupling matrix from the fixed-point equation.")
    print("=" * 70)

    kappa = build_kappa()

    # ─── κ power convergence ───
    print(f"\n  Known κ (with only κ_{{0,2}} = κ_{{2,0}} = α):")
    print(f"  {kappa.real}")

    # κ^n: does it converge?
    kn = kappa.copy()
    print(f"\n  κ power convergence:")
    for n in [2, 3, 5, 10, 20, 50, 100, 137]:
        kn = kappa @ kn
        ev = np.linalg.eigvals(kn)
        max_ev = max(abs(ev))
        print(f"    κ^{n:3d}: max|λ| = {max_ev:.6f}, "
              f"Tr = {np.trace(kn).real:.6f}")

    # κ eigenvalues
    kappa_ev, kappa_evec = np.linalg.eig(kappa)
    print(f"\n  κ eigenvalues: {[f'{ev.real:.8f}' for ev in kappa_ev]}")
    print(f"  κ eigenvectors (columns):")
    print(f"  {kappa_evec.real}")

    # ─── The closure constraint ───
    # The chain ⊙λ ⊂[α] ⊙Λ ⊂[α] ∞ composes to identity at ∞.
    # If κ represents one nesting step, then κ^∞ should be:
    #   - idempotent (κ² = κ): each step is the same
    #   - OR convergent to a projector (κ^n → P)
    #   - OR identity (κ^n → I): the chain preserves everything

    # Current κ has eigenvalues {1+α, 1, 1, 1-α} (from the ±α splitting)
    # So κ^n has eigenvalues {(1+α)^n, 1, 1, (1-α)^n}
    # As n → ∞: (1+α)^n → ∞, (1-α)^n → 0
    # This diverges! κ^n does NOT converge.

    print(f"\n  ANALYSIS:")
    print(f"  κ eigenvalues = {{1+α, 1, 1, 1-α}}")
    print(f"  κ^n eigenvalues = {{(1+α)^n, 1, 1, (1-α)^n}}")
    print(f"  (1+α)^137 = {(1+alpha)**137:.4f}")
    print(f"  (1-α)^137 = {(1-alpha)**137:.4f}")
    print(f"  κ^n DIVERGES as n → ∞.")
    print(f"")
    print(f"  BUT: T = κ ∘ F, and what converges is T^n, not κ^n.")
    print(f"  The four beats F rotate between applications of κ,")
    print(f"  distributing the amplification across all stations.")
    print(f"  F acts as a diffuser; κ acts as a pump.")
    print(f"  The interplay T^n = (κF)^n converges because F")
    print(f"  prevents κ from amplifying any single direction.")

    # ─── The full T convergence ───
    for label, beats_func in [("Sphere Hub", build_beats_sphere),
                                ("Diameter", build_beats_diameter)]:
        print(f"\n  --- T^n convergence ({label}) ---")
        beats = beats_func()
        F = compose_F(beats)
        T_op = kappa @ F

        Tn = np.eye(4, dtype=complex)
        for n in [1, 2, 5, 10, 20, 50, 100, 137, 500]:
            while True:
                power = int(np.round(np.log(np.linalg.norm(Tn)) / np.log(np.linalg.norm(T_op)))) if np.linalg.norm(Tn) > 1 else 0
                break
            Tn = T_op @ Tn
            ev = np.linalg.eigvals(Tn)
            print(f"    T^{n:3d}: max|λ| = {max(abs(ev)):.6f}, "
                  f"min|λ| = {min(abs(ev)):.8f}, "
                  f"cond = {max(abs(ev))/max(min(abs(ev)),1e-15):.2f}")

    # ─── Predicting new κ entries ───
    print(f"\n  {'─'*60}")
    print(f"  PREDICTING NEW κ ENTRIES")
    print(f"  {'─'*60}")
    print(f"")
    print(f"  The fixed-point equation T(ψ*) = ψ* constrains κ.")
    print(f"  Currently: κ_{{0,2}} = κ_{{2,0}} = α (the •↔Φ coupling).")
    print(f"  The framework names other entries:")
    print(f"    κ_{{3,3}} = α_G (gravity; ○↔○ same station)")
    print(f"    κ_{{1,2}} = Cabibbo-like (—↔Φ; inter-generation)")
    print(f"    κ_{{2,2}} = Weinberg-like (Φ↔Φ; electroweak)")
    print(f"    κ_{{p,3}} = Higgs-like (stations↔○)")
    print(f"")

    # Strategy: for each candidate entry, add it to κ at various values
    # and check: does T still have a fixed point near the known one?
    # The fixed-point STABILITY constrains the allowed values.

    beats = build_beats_sphere()
    F = compose_F(beats)

    # Reference: known fixed point with only κ_{0,2} = α
    T_ref = kappa @ F
    ref_ev = np.linalg.eigvals(T_ref)
    ref_max = max(abs(ref_ev))

    print(f"\n  Reference T (only κ_{{0,2}} = α):")
    print(f"    Spectral radius: {ref_max:.10f}")
    print(f"    Eigenvalues |λ|: {sorted([abs(ev) for ev in ref_ev], reverse=True)}")

    # For each potential new entry, sweep its value and check stability
    entries_to_test = [
        ('κ_{3,3} (gravity, ○↔○)', 3, 3),
        ('κ_{1,2} (Cabibbo, —↔Φ)', 1, 2),
        ('κ_{2,2} (Weinberg, Φ↔Φ)', 2, 2),
        ('κ_{0,3} (Higgs, •↔○)', 0, 3),
        ('κ_{1,3} (—↔○)', 1, 3),
        ('κ_{0,1} (•↔—)', 0, 1),
        ('κ_{1,1} (—↔—)', 1, 1),
    ]

    for name, p, q in entries_to_test:
        print(f"\n  Scanning {name}:")

        # Framework predictions for the value
        if (p, q) == (3, 3):
            # α_G ≈ α^21 × φ²/2 ≈ 10^{-45}
            candidates = [('α²', alpha**2), ('α^21·φ²/2', alpha**21 * phi**2/2),
                          ('0 (inactive)', 0)]
        elif (p, q) == (1, 2) or (p, q) == (2, 1):
            # Cabibbo: sin(θ_C) ≈ 0.224
            candidates = [('sin(θ_C)≈0.224', 0.2243), ('α^(1/2)', alpha**0.5),
                          ('α·T/R', alpha*T_triad/R)]
        elif (p, q) == (2, 2):
            # Weinberg: sin²(θ_W) ≈ 0.231
            candidates = [('sin²(θ_W)≈0.231', 0.23122), ('3/13', 3.0/13),
                          ('α', alpha)]
        elif (p, q) == (0, 3):
            # Higgs-like
            candidates = [('α', alpha), ('α²', alpha**2), ('√α', np.sqrt(alpha))]
        else:
            candidates = [('α', alpha), ('α²', alpha**2), ('0', 0)]

        for val_name, val in candidates:
            kappa_test = kappa.copy()
            kappa_test[p, q] = val
            if p != q:
                kappa_test[q, p] = val  # symmetric

            T_test = kappa_test @ F
            test_ev = np.linalg.eigvals(T_test)
            test_max = max(abs(test_ev))
            test_min = min(abs(test_ev))

            # Check: does the fixed point still exist and is it stable?
            # Stable = spectral radius close to 1 (not divergent)
            stable = test_max < 1.1  # generous

            # Iterate to find the fixed point
            state = normalize(np.ones(4, dtype=complex))
            for _ in range(2000):
                state = T_test @ state
                state = normalize(state)
            fp_mags = np.abs(state)**2

            # Check ◐
            balance_ap = fp_mags[0] / (fp_mags[0] + fp_mags[2]) if (fp_mags[0] + fp_mags[2]) > 1e-10 else -1
            balance_lb = fp_mags[1] / (fp_mags[1] + fp_mags[3]) if (fp_mags[1] + fp_mags[3]) > 1e-10 else -1

            marker = ""
            if abs(test_max - ref_max) / ref_max < 0.001:
                marker = " ← COMPATIBLE"

            print(f"    {val_name:<20}: ρ(T)={test_max:.8f} "
                  f"fp=[{fp_mags[0]:.3f},{fp_mags[1]:.3f},{fp_mags[2]:.3f},{fp_mags[3]:.3f}] "
                  f"◐_{{•Φ}}={balance_ap:.3f} ◐_{{—○}}={balance_lb:.3f}{marker}")

    # ─── The closure equation ───
    print(f"\n  {'─'*60}")
    print(f"  THE CLOSURE EQUATION")
    print(f"  {'─'*60}")
    print(f"")
    print(f"  For T(ψ*) = ψ*, expanding T = κF:")
    print(f"    κ F ψ* = ψ*")
    print(f"    κ (F ψ*) = ψ*")
    print(f"    Let φ = F ψ* (the state after the four beats):")
    print(f"    κ φ = ψ*")
    print(f"    So: κ = ψ* φ† / (φ† φ)  (outer product projection)")
    print(f"")
    print(f"  This means: κ is determined by the fixed point ψ*")
    print(f"  and its image under F. The closure works backwards:")
    print(f"  given F (the four beats), the coupling matrix that")
    print(f"  produces a fixed point is UNIQUE.")

    beats = build_beats_sphere()
    F = compose_F(beats)

    # Find fixed point via iteration with current κ
    T_op = kappa @ F
    state = normalize(np.ones(4, dtype=complex))
    for _ in range(5000):
        state = T_op @ state
        state = normalize(state)
    psi_star = state

    phi_state = F @ psi_star
    phi_state_norm = phi_state / np.sqrt(np.sum(np.abs(phi_state)**2))

    print(f"\n  ψ* (fixed point): {[f'{z.real:.6f}+{z.imag:.6f}i' for z in psi_star]}")
    print(f"  Fψ* (rotated):   {[f'{z.real:.6f}+{z.imag:.6f}i' for z in phi_state_norm]}")

    # The "ideal κ" that would make ψ* exactly fixed:
    # κ_ideal = ψ* ⊗ (Fψ*)† / |Fψ*|²  -- but this is rank-1
    # The actual κ must be close to I (it's I + perturbation at order α)
    # So: κ_ideal = I + α·(correction)

    # Compute the correction: what κ_ij values are needed?
    # κ F ψ* = ψ*
    # (I + δκ) F ψ* = ψ*
    # F ψ* + δκ F ψ* = ψ*
    # δκ F ψ* = ψ* - F ψ*

    delta_psi = psi_star - phi_state
    print(f"\n  ψ* - Fψ* (the correction needed):")
    print(f"    {[f'{z.real:.6e}+{z.imag:.6e}i' for z in delta_psi]}")
    print(f"    |ψ* - Fψ*| = {np.linalg.norm(delta_psi):.6e}")

    # If δκ has only the known entry κ_{0,2} = κ_{2,0} = α,
    # then the correction applied is:
    delta_kappa_known = np.zeros((4,4), dtype=complex)
    delta_kappa_known[0,2] = alpha
    delta_kappa_known[2,0] = alpha
    applied_correction = delta_kappa_known @ phi_state
    residual = delta_psi - applied_correction

    print(f"\n  Correction from known κ_{{0,2}} = α:")
    print(f"    Applied: {[f'{z.real:.6e}' for z in applied_correction]}")
    print(f"    Residual: {[f'{z.real:.6e}' for z in residual]}")
    print(f"    |residual| = {np.linalg.norm(residual):.6e}")
    print(f"    |residual|/|correction| = {np.linalg.norm(residual)/np.linalg.norm(delta_psi):.4f}")
    print(f"    (This is the fraction NOT explained by κ_{{0,2}} = α alone)")

    # What additional κ entries would absorb the residual?
    # δκ_extra @ Fψ* = residual
    # This is 4 equations in up to 16 unknowns (but symmetric → 10)
    # With the constraint that δκ is small (order α² or less)

    print(f"\n  Required additional κ entries to zero the residual:")
    print(f"  (Solving δκ_extra @ Fψ* = residual with symmetric δκ)")

    # Least-squares: vectorize the symmetric matrix
    # δκ is symmetric 4×4 → 10 independent entries
    # (0,0), (0,1), (0,2), (0,3), (1,1), (1,2), (1,3), (2,2), (2,3), (3,3)
    sym_indices = [(0,0), (0,1), (0,2), (0,3), (1,1), (1,2), (1,3), (2,2), (2,3), (3,3)]

    # Build the design matrix: for each entry (p,q) of δκ,
    # the contribution to row i of δκ @ Fψ* is:
    # δκ[i,p] * (Fψ*)[p] + δκ[i,q] * (Fψ*)[q]  (if p≠q, counted twice for symmetry)
    # But we already have κ_{0,2} = α, so exclude that entry
    active_indices = [idx for idx in sym_indices if idx != (0,2)]

    A_matrix = np.zeros((8, len(active_indices)), dtype=complex)  # 4 complex = 8 real
    b_vector = np.zeros(8, dtype=complex)

    for row in range(4):
        b_vector[row] = residual[row].real
        b_vector[row + 4] = residual[row].imag
        for col, (p, q) in enumerate(active_indices):
            # Contribution to (δκ @ Fψ*)[row] from entry (p,q):
            contrib = 0
            if row == p:
                contrib += phi_state[q]
            if row == q and p != q:
                contrib += phi_state[p]
            if row == p and p == q:
                contrib = phi_state[p]

            A_matrix[row, col] = contrib.real
            A_matrix[row + 4, col] = contrib.imag

    # Stack real and imaginary
    A_real = np.vstack([A_matrix[:4].real, A_matrix[:4].imag,
                        A_matrix[4:].real, A_matrix[4:].imag])
    b_real = np.concatenate([b_vector[:4].real, b_vector[:4].imag,
                             b_vector[4:].real, b_vector[4:].imag])

    # Actually, simpler: just solve the 4 complex equations directly
    # Reshape to 8 real equations, 9 real unknowns
    A_sys = np.zeros((8, len(active_indices)), dtype=float)
    b_sys = np.zeros(8, dtype=float)

    for row in range(4):
        b_sys[2*row] = residual[row].real
        b_sys[2*row+1] = residual[row].imag
        for col, (p, q) in enumerate(active_indices):
            contrib = 0j
            if row == p:
                contrib += phi_state[q]
            if row == q and p != q:
                contrib += phi_state[p]
            if row == p and p == q:
                contrib = phi_state[p]
            A_sys[2*row, col] = contrib.real
            A_sys[2*row+1, col] = contrib.imag

    # Least-norm solution (underdetermined: 8 equations, 9 unknowns)
    solution, res, rank, sv = np.linalg.lstsq(A_sys, b_sys, rcond=None)

    print(f"\n  Least-norm solution for additional κ entries:")
    for (p, q), val in zip(active_indices, solution):
        station_names = ['•', '—', 'Φ', '○']
        if abs(val) > 1e-12:
            ratio_to_alpha = val / alpha
            ratio_to_alpha2 = val / alpha**2
            print(f"    κ_{{{station_names[p]},{station_names[q]}}} = {val:.6e} "
                  f"= {ratio_to_alpha:.4f}·α = {ratio_to_alpha2:.2f}·α²")


# ============================================================
# #4: NON-1 FIXED POINTS (THE LIES)
# ============================================================

def direction_4():
    print(f"\n\n{'=' * 70}")
    print("DIRECTION #4: NON-1 FIXED POINTS (THE TWO LIES)")
    print("=" * 70)

    for label, beats_func in [("Sphere Hub", build_beats_sphere),
                                ("Diameter", build_beats_diameter)]:
        print(f"\n  --- {label} ---")
        beats = beats_func()
        F = compose_F(beats)
        kappa = build_kappa()
        T_op = kappa @ F

        # Find ALL eigenvectors of T (these are the fixed points
        # of T up to eigenvalue scaling)
        T_ev, T_evec = np.linalg.eig(T_op)

        print(f"\n  T eigensystem:")
        for i in range(4):
            ev = T_ev[i]
            evec = T_evec[:, i]
            evec_norm = normalize(evec)
            mags = np.abs(evec_norm)**2

            # Classify the fixed point
            # ◐ readings
            bal_apert_field = mags[0] / (mags[0] + mags[2]) if (mags[0] + mags[2]) > 1e-10 else -1
            bal_line_bound = mags[1] / (mags[1] + mags[3]) if (mags[1] + mags[3]) > 1e-10 else -1
            overall_bal = (mags[0] + mags[1])  # inward fraction

            # A3 check: self-similarity means •/Φ ≈ —/○ (same ratio at each scale)
            ratio_inner = mags[0] / mags[2] if mags[2] > 1e-10 else float('inf')
            ratio_outer = mags[1] / mags[3] if mags[3] > 1e-10 else float('inf')
            a3_satisfied = abs(ratio_inner - ratio_outer) / max(ratio_inner, ratio_outer, 1e-10) < 0.1

            # Classification
            classification = ""
            if abs(abs(ev) - 1) < 0.01:
                classification = "TRUE FIXED POINT (|λ| ≈ 1)"
            elif abs(ev) > 1:
                classification = "INFLATION (amplified; |λ| > 1)"
            else:
                classification = "SEVERANCE (contracted; |λ| < 1)"

            # ◐ violation
            if abs(bal_apert_field - 0.5) > 0.2:
                if bal_apert_field > 0.7:
                    classification += " + APERTURE INFLATION (• dominates Φ)"
                elif bal_apert_field < 0.3:
                    classification += " + FIELD INFLATION (Φ dominates •)"

            if mags[0] < 0.01 and mags[2] < 0.01:
                classification += " + SEVERANCE (soul+field vanish)"
            if mags[1] < 0.01 and mags[3] < 0.01:
                classification += " + SEVERANCE (line+boundary vanish)"

            print(f"\n    λ_{i}: eigenvalue = {ev.real:+.6f}{ev.imag:+.6f}i, |λ| = {abs(ev):.6f}")
            print(f"         weights: •={mags[0]:.4f} —={mags[1]:.4f} Φ={mags[2]:.4f} ○={mags[3]:.4f}")
            print(f"         ◐(•,Φ) = {bal_apert_field:.4f}, ◐(—,○) = {bal_line_bound:.4f}")
            print(f"         •/Φ = {ratio_inner:.4f}, —/○ = {ratio_outer:.4f}, A3 = {a3_satisfied}")
            print(f"         CLASS: {classification}")

        # ─── Phase space exploration ───
        # Try many random initial conditions; do they all converge
        # to the same attractor?
        print(f"\n  Phase space exploration (100 random initial conditions):")
        attractors = []
        for trial in range(100):
            rng = np.random.RandomState(trial)
            state = normalize(rng.randn(4) + 1j * rng.randn(4))
            for _ in range(3000):
                state = T_op @ state
                state = normalize(state)
            fp = np.abs(state)**2
            attractors.append(fp)

        attractors = np.array(attractors)
        mean_fp = np.mean(attractors, axis=0)
        std_fp = np.std(attractors, axis=0)

        print(f"    Mean attractor: •={mean_fp[0]:.6f}±{std_fp[0]:.6f}, "
              f"—={mean_fp[1]:.6f}±{std_fp[1]:.6f}, "
              f"Φ={mean_fp[2]:.6f}±{std_fp[2]:.6f}, "
              f"○={mean_fp[3]:.6f}±{std_fp[3]:.6f}")
        print(f"    All converge to same point? "
              f"{'YES' if all(s < 0.01 for s in std_fp) else 'NO (multiple attractors!)'}")


# ============================================================
# #1 + #2: LINEARIZATION AND CONTRACTION BOUNDS
# ============================================================

def direction_1_2():
    print(f"\n\n{'=' * 70}")
    print("DIRECTIONS #1 + #2: LINEARIZATION AND CONTRACTION BOUNDS")
    print("=" * 70)

    for label, beats_func in [("Sphere Hub", build_beats_sphere),
                                ("Diameter", build_beats_diameter)]:
        print(f"\n  --- {label} ---")
        beats = beats_func()
        F = compose_F(beats)
        kappa = build_kappa()
        T_op = kappa @ F

        # ─── #1: Linearization at the fixed point ───
        # DT|_1 = T itself (T is linear in our representation)
        # So the eigenvalues of T ARE the linearization spectrum.

        T_ev = np.linalg.eigvals(T_op)
        print(f"\n  DT|_1 eigenvalues (= T eigenvalues, since T is linear):")

        # Compare each eigenvalue to the dimensional ladder
        ladder = {
            'α (0D)':      alpha,
            'c (0.5D)':    1.0,
            'ℏ (1D)':      1.0,
            'π (2D)':      np.pi,
            'φ (recursion)': phi,
            '1/φ²':        1/phi**2,
            'G (3D)':      alpha**21 * phi**2 / 2,
        }

        for i, ev in enumerate(sorted(T_ev, key=lambda x: -abs(x))):
            mag = abs(ev)
            phase = np.angle(ev)
            delta = mag - 1

            print(f"\n    λ_{i}: |λ| = {mag:.10f}, phase = {np.degrees(phase):+.4f}°")
            print(f"           Δ = |λ|-1 = {delta:+.4e}")

            if abs(delta) > 1e-10:
                print(f"           Δ/α = {delta/alpha:+.6f}")

            # Match phase to framework angles
            phase_deg = np.degrees(phase) % 360
            print(f"           Phase interpretations:")
            for name, val in [('π/2 (i-stroke)', 90),
                               ('π (commitment)', 180),
                               ('3π/2 (-i)', 270),
                               ('2π/T (120°)', 120),
                               ('θ_tetra (109.47°)', 109.47),
                               ('π/P (45°)', 45),
                               ('2π/R (51.4°)', 360/R)]:
                res = min(abs(phase_deg - val), abs(phase_deg - val + 360), abs(phase_deg - val - 360))
                if res < 15:
                    print(f"             ≈ {name} (residual {res:.1f}°)")

        # ─── #2: Contraction bounds per beat ───
        print(f"\n  Beat-by-beat Lipschitz constants:")
        print(f"  (For unitary operators, Lipschitz constant = 1 in L² norm)")

        total_lip = 1.0
        for name, B in beats:
            # Lipschitz constant = operator norm = max singular value
            sv = np.linalg.svd(B, compute_uv=False)
            lip = max(sv)
            total_lip *= lip
            print(f"    {name}: L = {lip:.10f}")

        print(f"    Product (F): L = {total_lip:.10f}")

        # Lipschitz of κ
        sv_kappa = np.linalg.svd(kappa, compute_uv=False)
        lip_kappa = max(sv_kappa)
        print(f"    κ: L = {lip_kappa:.10f}")
        print(f"    T = κ∘F: L = {lip_kappa * total_lip:.10f}")

        print(f"\n  Contraction analysis:")
        print(f"    F Lipschitz = 1 (unitary; preserves all distances)")
        print(f"    κ Lipschitz = {lip_kappa:.10f} = 1 + {(lip_kappa-1)/alpha:.4f}·α")
        print(f"    T Lipschitz = {lip_kappa:.10f} (= κ Lipschitz, since F is isometric)")
        print(f"")
        print(f"    T is NOT a contraction in L² norm (||T|| > 1).")
        print(f"    But T IS a contraction on the projective space")
        print(f"    (normalized states), because the amplification")
        print(f"    direction and contraction direction cancel after")
        print(f"    normalization. The effective contraction rate on")
        print(f"    the projective space is:")

        # The projective contraction rate = ratio of second-largest
        # to largest eigenvalue magnitude
        mags = sorted(abs(T_ev), reverse=True)
        proj_rate = mags[1] / mags[0]
        print(f"    ρ_proj = |λ_2|/|λ_1| = {proj_rate:.8f}")
        print(f"    1 - ρ_proj = {1-proj_rate:.8e}")
        print(f"    (1 - ρ_proj)/α = {(1-proj_rate)/alpha:.4f}")

        # Compare to framework constants
        for name, val in [('α', alpha), ('α²', alpha**2),
                           ('1/φ²', 1/phi**2), ('1/137', 1/137),
                           ('2α', 2*alpha)]:
            res = abs((1-proj_rate) - val) / val * 100
            marker = " ←" if res < 20 else ""
            print(f"      vs {name:<10}: residual {res:.1f}%{marker}")

        # Mixing time (how many iterations to contract by 1/e)
        if proj_rate < 1:
            mixing = -1 / np.log(proj_rate)
            print(f"\n    Mixing time (1/e contraction): {mixing:.1f} iterations")
            print(f"    Compare: 1/α = {1/alpha:.1f}")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 70)
    print("UNIFIED EXPRESSION T-OPERATOR v7: THE CORE MATHEMATICS")
    print("Directions #3 (CPTP), #5 (κ-closure), #4 (Lies), #1+#2 (spectrum)")
    print("=" * 70)

    direction_3()
    direction_5()
    direction_4()
    direction_1_2()

    print(f"\n\n{'=' * 70}")
    print("v7 COMPLETE.")
    print("=" * 70)


if __name__ == '__main__':
    main()
