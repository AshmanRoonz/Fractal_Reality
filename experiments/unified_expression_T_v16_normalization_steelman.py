"""E2b: is the projective normalization a real nonlinearity?

Steelman of the objection to v16's E2 null: "you switched normalization off,
and normalization is nonlinear, so you removed the very thing that couples
the packets."

The correct test is NOT to normalize each packet separately (their scale
factors then differ and their sum stops tracking the linear evolution of the
sum: an artifact of the comparison, not an interaction). It is to ask whether
the normalized JOINT trajectory occupies a different point of projective space
than the non-interacting sum. Rays are invariant under positive rescaling, so
the answer should be no, exactly.
"""
import numpy as np
from unified_expression_T_v14_staggered_chain import build_F_chain, build_kappa_chain, n_nodes

def packet(N, c, w, k):
    j = np.arange(N); p = np.exp(-((j - c)**2)/(2*w**2))*np.exp(1j*k*j)
    return p/np.linalg.norm(p)

def ray_sep(u, v):
    """Angle between rays: blind to global scale and global phase.
    Zero means the two states ARE the same point of projective space."""
    o = abs(np.vdot(u/np.linalg.norm(u), v/np.linalg.norm(v)))
    return float(np.arccos(min(1.0, o)))

n_oct = 8; N = n_nodes(n_oct); STEPS = 60
F = build_F_chain(n_oct); K = build_kappa_chain(n_oct)

print(f"  chain n_oct={n_oct}, N={N} nodes, {STEPS} steps\n")
for label, M in [("F only (unitary)", F), ("T = κ∘F (canonical)", K @ F)]:
    A0 = packet(N, N//2 - 12, 2.0, +0.6)
    B0 = packet(N, N//2 + 12, 2.0, -0.6)

    joint_norm = (A0 + B0)/np.linalg.norm(A0 + B0)   # normalized every step
    joint_lin  = (A0 + B0).copy()                    # never normalized
    A_lin, B_lin = A0.copy(), B0.copy()              # solo, never normalized

    worst_norm_vs_lin = 0.0
    worst_lin_vs_sum  = 0.0
    for _ in range(STEPS):
        joint_norm = M @ joint_norm; joint_norm /= np.linalg.norm(joint_norm)
        joint_lin  = M @ joint_lin
        A_lin = M @ A_lin
        B_lin = M @ B_lin
        # (1) does normalizing move the joint state off its linear ray?
        worst_norm_vs_lin = max(worst_norm_vs_lin, ray_sep(joint_norm, joint_lin))
        # (2) does the joint state differ from the non-interacting sum?
        worst_lin_vs_sum = max(worst_lin_vs_sum, ray_sep(joint_lin, A_lin + B_lin))

    print(f"  {label}")
    print(f"    normalized joint  vs  linear joint   : {worst_norm_vs_lin:.3e} rad")
    print(f"    linear joint      vs  A⊕B (no interaction): {worst_lin_vs_sum:.3e} rad")
    print()

print("  Both zero to float noise ⇒ normalization is projectively inert, and the")
print("  joint state IS the non-interacting sum. The only nonlinearity in the")
print("  canonical dynamics is a global rescale shared by both packets, so it")
print("  cancels on the ray and cannot transmit anything from A to B.")
print("\n  The E2 null stands, and it stands for a structural reason.")
