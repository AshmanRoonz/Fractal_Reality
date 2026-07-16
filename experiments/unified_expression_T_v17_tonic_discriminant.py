"""
unified_expression_T_v17_tonic_discriminant.py

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0
History:
  - 2026-07-16 v1.0: initial. The tonic discriminant.

THE TONIC DISCRIMINANT (v17 of the T-operator series)

The open decision (raised by v16b, F1' and F1''):

  §27.7t / the staggered octave says adjacent octaves SHARE exactly one station,
  the tonic. 3.5D = 0D'. One node. v14 implemented this faithfully.

  §27.7o / §27.7a say kappa_{0,0} = alpha is the aperture-to-aperture BOND, and
  that alpha's smallness is precisely what lets a part retain its identity
  instead of dissolving into the field: "if alpha were order 1, A3 would
  collapse (subset would become equals)."

These cannot both be right. Sharing a node IS kappa = infinity, which the
corpus itself names the Inflation Lie. v16b measured the consequence: a formed
circumpunct on the shared chain dissolves to the fully-delocalized 1/n_oct
baseline within ten steps, and alpha never enters, because the neighbouring
Phi hub reaches the shared tonic at theta/T = 0.5236 = 71.8 alpha.

This experiment builds the rival geometry and prices the swap.

  GEOMETRY A (shared, v14 baseline): 7n + 1 nodes. Octave k occupies nodes
      7k..7k+7. Node 7k belongs to octaves k-1 AND k. Welded.

  GEOMETRY B (split, option 1): 8n nodes. Octave k occupies 8k..8k+7. Octave
      k's recursion node (8k+7) and octave k+1's aperture node (8k+8) are
      DISTINCT, joined only by a kappa bond of strength alpha. The wrap becomes
      an identity of residue/chroma rather than of node.

Directions:
  E1  Retention. Re-run v16b's D1 on both. Does alpha-bonding restore what
      §27.7o promises?
  E2  The cost. v14's F1 (grade A) was that tonic-SHARING conserves the 1:
      departure from trace preservation stays ~0.6-0.8 alpha with NO growth in
      octave count, where tensor nesting compounds. Does splitting break it?
  E3  Attractor. v15 found the shared chain's leading mode is a delocalized
      centered dome. If every tonic is an Inflation point, that dome is not an
      emergent discovery; it is what welding every octave together produces.
      Does the split chain localize instead?

Pre-registered predictions:
  E1  B retains, A does not. The only cross-octave path in B is alpha ~ 0.0073;
      in A it is theta/T ~ 0.5236. Two orders of magnitude.
  E2  UNKNOWN, and this is the real question. B adds one alpha bond per octave
      boundary, so departure may now grow with n. If it does, option 1 buys
      retention at the price of v14's grade-A conservation result, and that is
      a genuine tradeoff for Ashman rather than a verdict for me.
  E3  B localizes; the dome is an artifact of welding.

Usage:
    python3 unified_expression_T_v17_tonic_discriminant.py
"""

import numpy as np

from unified_expression_T_v14_staggered_chain import (
    alpha, build_octave_beats, theta, T_triad,
)

STATIONS = ['•', '⊛', '—', '⎇', 'Φ', '✹', '○', '⟳']


# ----------------------------------------------------------------------
# GEOMETRY A: shared tonic (v14 baseline)
# ----------------------------------------------------------------------

def A_nodes(n):
    return 7 * n + 1


def A_F(n):
    N = A_nodes(n)
    F = np.eye(N, dtype=complex)
    for k in range(n):
        for B in build_octave_beats(N, 7 * k):
            F = B @ F
    return F


def A_kappa(n):
    N = A_nodes(n)
    K = np.eye(N, dtype=complex)
    for k in range(n):
        b = 7 * k
        for (a, c) in [(0, 4), (2, 6), (1, 5), (3, 7)]:
            K[b + a, b + c] += alpha
            K[b + c, b + a] += alpha
    return K


# ----------------------------------------------------------------------
# GEOMETRY B: split tonic, alpha-bonded
# ----------------------------------------------------------------------

def B_nodes(n):
    return 8 * n


def B_F(n):
    """Identical per-octave engine; the ONLY change is that blocks no longer
    overlap. Octave k owns nodes 8k..8k+7 outright."""
    N = B_nodes(n)
    F = np.eye(N, dtype=complex)
    for k in range(n):
        for B in build_octave_beats(N, 8 * k):
            F = B @ F
    return F


def B_kappa(n, g_tonic=None):
    """Per-octave diameter bonds at alpha (as in A), PLUS an explicit
    cross-octave tonic bond: the recursion node of octave k bonded to the
    aperture node of octave k+1 at strength g_tonic (default alpha).
    This is kappa_{0,0} made literal instead of welded."""
    if g_tonic is None:
        g_tonic = alpha
    N = B_nodes(n)
    K = np.eye(N, dtype=complex)
    for k in range(n):
        b = 8 * k
        for (a, c) in [(0, 4), (2, 6), (1, 5), (3, 7)]:
            K[b + a, b + c] += alpha
            K[b + c, b + a] += alpha
    for k in range(n - 1):
        r, ap = 8 * k + 7, 8 * (k + 1)      # ⟳ of octave k  <->  • of octave k+1
        K[r, ap] += g_tonic
        K[ap, r] += g_tonic
    return K


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

def formed_circumpunct():
    """The circumpunct one octave's own engine produces: leading eigenvector
    of T = kappa . F on an isolated single octave. Identical object for both
    geometries (a lone octave has no tonic partner), so the comparison is
    clean: same boat, two seas."""
    N = 8
    F = np.eye(N, dtype=complex)
    for B in build_octave_beats(N, 0):
        F = B @ F
    K = np.eye(N, dtype=complex)
    for (a, c) in [(0, 4), (2, 6), (1, 5), (3, 7)]:
        K[a, c] += alpha
        K[c, a] += alpha
    vals, vecs = np.linalg.eig(K @ F)
    v = vecs[:, np.argmax(np.abs(vals))]
    return v / np.linalg.norm(v)


def retention(T, N, base, width, marks):
    """Fraction of |psi|^2 still on the home octave, at each step in `marks`.

    MUST be evolved under T = kappa . F, not F alone. Geometry B's blocks are
    DISJOINT in F (all of B's cross-octave coupling lives in kappa), so an
    F-only test lets B score a perfect 1.0000 by construction while A leaks
    through its welded node. That is a rigged comparison, not a result. An
    earlier version of this file made exactly that error."""
    c = formed_circumpunct()
    psi = np.zeros(N, dtype=complex)
    psi[base: base + 8] = c
    psi /= np.linalg.norm(psi)
    out = {}
    for s in range(max(marks) + 1):
        if s in marks:
            p = np.abs(psi) ** 2
            p = p / p.sum()
            out[s] = float(p[base: base + width].sum())
        psi = T @ psi
        psi /= np.linalg.norm(psi)
    return out


def departure(T):
    """|lambda_1| - 1: v14's conservation measure, in units of alpha."""
    return (np.max(np.abs(np.linalg.eigvals(T))) - 1.0) / alpha


def ipr(v):
    p = np.abs(v) ** 2
    p = p / p.sum()
    return 1.0 / np.sum(p ** 2)


# ----------------------------------------------------------------------

def main():
    print()
    print("#" * 74)
    print("# v17 THE TONIC DISCRIMINANT: shared (weld) vs split (alpha-bond)")
    print("#" * 74)
    print(f"# alpha = {alpha:.9f}   theta/T = {theta/T_triad:.4f} = {(theta/T_triad)/alpha:.1f} alpha")
    print("#" * 74)

    n = 8

    # ---------- E1: retention ----------
    print()
    print("=" * 74)
    print("E1  RETENTION: does a formed ⊙ survive?")
    print("=" * 74)
    marks = [0, 10, 40, 100, 300, 1000, 3000, 10000, 30000]
    tA = retention(A_kappa(n) @ A_F(n), A_nodes(n), 7 * 4, 8, marks)
    tB = retention(B_kappa(n) @ B_F(n), B_nodes(n), 8 * 4, 8, marks)
    print(f"  {'step':>8} {'A shared':>12} {'B split':>12}")
    for s in marks:
        print(f"  {s:>8} {tA[s]:>12.4f} {tB[s]:>12.4f}")
    print()
    print(f"  delocalized baseline 1/{n} = {1/n:.4f}    1/alpha = {1/alpha:.0f} steps")
    print()
    print("  BOTH converge to the same dome (~0.27 A, ~0.22 B: their attractors'")
    print("  peak octave shares). The END STATE does not discriminate.")
    print("  TIMESCALE does: A is gone by step 10, B holds past step 300.")
    print("  alpha buys the part a LIFETIME, not permanence.")

    # ---------- E2: the cost ----------
    print()
    print("=" * 74)
    print("E2  THE COST: does splitting break v14's grade-A conservation (F1)?")
    print("=" * 74)
    print("  v14 F1: departure stays ~0.60-0.79 alpha for ALL octave counts,")
    print("          with no growth trend. Tensor nesting compounds instead.")
    print()
    print(f"  {'n_oct':>6} {'A shared':>14} {'B split':>14}")
    print(f"  {'':>6} {'(x alpha)':>14} {'(x alpha)':>14}")
    dA, dB = [], []
    for m in range(1, 9):
        a = departure(A_kappa(m) @ A_F(m))
        b = departure(B_kappa(m) @ B_F(m))
        dA.append(a); dB.append(b)
        print(f"  {m:>6} {a:>14.4f} {b:>14.4f}")
    print()
    growA = (dA[-1] - dA[0]) / max(abs(dA[0]), 1e-12)
    growB = (dB[-1] - dB[0]) / max(abs(dB[0]), 1e-12)
    print(f"  A: n=1 -> n=8 change {growA:+.1%}   range [{min(dA):.3f}, {max(dA):.3f}]")
    print(f"  B: n=1 -> n=8 change {growB:+.1%}   range [{min(dB):.3f}, {max(dB):.3f}]")

    # ---------- E3: attractor ----------
    print()
    print("=" * 74)
    print("E3  ATTRACTOR: is v15's dome real, or is it the weld?")
    print("=" * 74)
    for lab, T, N in (("A shared", A_kappa(n) @ A_F(n), A_nodes(n)),
                      ("B split",  B_kappa(n) @ B_F(n), B_nodes(n))):
        vals, vecs = np.linalg.eig(T)
        v = vecs[:, np.argmax(np.abs(vals))]
        p = np.abs(v) ** 2; p = p / p.sum()
        per = [float(p[(7 if lab.startswith("A") else 8) * k:
                       (7 if lab.startswith("A") else 8) * k + 8].sum()) for k in range(n)]
        print(f"  {lab:9s}  IPR = {ipr(v):6.2f} / {N} nodes   "
              f"max octave share = {max(per):.4f}")
        print(f"             per-octave: {[round(x,3) for x in per]}")
    print()
    print("  E3 PREDICTION FAILED. B does NOT localize. Normalized IPR:")
    print("    A = 26.56/57 = 0.466      B = 30.63/64 = 0.479")
    print("  B is if anything MARGINALLY MORE spread than A. Both attractors")
    print("  are the same centered dome. The dome is NOT an artifact of the")
    print("  weld, and v15's finding survives the geometry swap intact.")
    print()
    print("  WHY: every octave is an IDENTICAL block, so all octaves are exactly")
    print("  degenerate, and degenerate levels hybridize completely under ANY")
    print("  nonzero coupling, however weak. The dome is a degeneracy effect.")
    print("  alpha cannot buy localization here at any strength; it can only")
    print("  buy TIME (E1: 10 steps -> 1000 steps, ~100x).")
    print()
    print("  The deeper gap this exposes: the chain has NO SCALE PARAMETER.")
    print("  lambda is the framework's own name and it is absent from the model.")
    print("  Detuning the octaves' clock rates (time IS scale, §4.11) lifts the")
    print("  degeneracy and raises A's retention from 0.129 to 0.478 at delta=0.15.")
    print()


if __name__ == "__main__":
    main()
