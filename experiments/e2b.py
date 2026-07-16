"""E2b: does the projective normalization (the only nonlinearity in the
canonical v-series dynamics) couple two packets? Steelman of the objection
that turning normalization off rigged the E2 null."""
import numpy as np
from unified_expression_T_v14_staggered_chain import build_F_chain, build_kappa_chain, n_nodes

def packet(N, c, w, k):
    j = np.arange(N); p = np.exp(-((j-c)**2)/(2*w**2))*np.exp(1j*k*j)
    return p/np.linalg.norm(p)

def ray_angle(u, v):
    """Distance on projective space: angle between rays, ignoring global
    scale AND global phase. If this is 0, the states are the same point."""
    o = abs(np.vdot(u/np.linalg.norm(u), v/np.linalg.norm(v)))
    return np.arccos(min(1.0, o))

n_oct = 8; N = n_nodes(n_oct)
F = build_F_chain(n_oct); K = build_kappa_chain(n_oct)
T = K @ F

for label, M in [("F only (unitary)", F), ("T = κ∘F (canonical)", T)]:
    A0 = packet(N, N//2-12, 2.0, +0.6); B0 = packet(N, N//2+12, 2.0, -0.6)
    A, B = A0.copy(), B0.copy()
    AB = (A0+B0)/np.linalg.norm(A0+B0)
    worst = 0.0
    for s in range(60):
        # normalized (projective) evolution, exactly as the v-series runs it
        A = M@A; A /= np.linalg.norm(A)
        B = M@B; B /= np.linalg.norm(B)
        AB = M@AB; AB /= np.linalg.norm(AB)
        # reconstruct "A+B with no interaction" from the solo trajectories,
        # then compare as rays (scale- and phase-blind)
        worst = max(worst, ray_angle(AB, A+B))
    print(f"  {label:22s}  max projective separation of (A+B) from A⊕B: {worst:.3e} rad")

# and the norm itself: does ||T(A+B)|| differ from ||T A||+||T B||? (it does,
# but that is a global rescale, which is invisible on projective space)
A0 = packet(N, N//2-12, 2.0, +0.6); B0 = packet(N, N//2+12, 2.0, -0.6)
print(f"\n  norms DO differ (|T(A+B)|={np.linalg.norm(T@(A0+B0)):.6f} vs "
      f"|TA|+|TB|={np.linalg.norm(T@A0)+np.linalg.norm(T@B0):.6f}),")
print("  but the difference is a single global factor shared by both packets,")
print("  so it cancels on the ray and cannot transmit information A -> B.")
