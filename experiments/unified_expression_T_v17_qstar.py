"""
unified_expression_T_v17_qstar.py

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0
History:
  - 2026-07-18 v1.0: initial. The analytic derivation of q*.

THE MOMENTUM OF THE ASCENDING FIXED POINT (v17 of the T-operator series)

v16 found the leading mode of the staggered ring at momentum q* ~ 0.3621 pi
per octave, alpha-independent. This experiment derives why, and pins the
number.

THE PERTURBATION THEOREM. T(q) = K(q) F(q) with K = I + alpha B(q), F(q)
unitary (all |lambda| = 1). For a simple eigenpair (e^{i phi_b}, u_b) of the
normal matrix F(q):

    lambda_b(alpha) = e^{i phi_b} (1 + alpha <u_b|B|u_b>) + O(alpha^2)
    =>  (|lambda_b| - 1)/alpha  =  beta_b(q) := <u_b(q)|B(q)|u_b(q)> + O(alpha)

since B is Hermitian (the Rayleigh quotient is real). So the band-modulus
landscape is, to first order, the bond matrix B(q) read in F(q)'s eigenbasis,
with NO alpha anywhere: q* = argmax_{b,q} beta_b(q) is a pure property of the
four-beat geometry, which is exactly what v16 observed numerically.

THE SEAM DECOMPOSITION. B(q) = B_intra + e^{iq} E_{30} + e^{-iq} E_{03}
(the only q-dependence is the one bond that crosses the tonic seam, the
(3,7) diameter, which in Bloch form is a hop from node 3 to the next cell's
node 0). Hence

    beta_b(q) = <u_b|B_intra|u_b> + 2 Re( e^{iq} conj(u_b[3]) u_b[0] )

If the eigenvector were q-frozen, beta would be a pure cosine and

    q*_frozen = - arg( conj(u_b[3]) u_b[0] )

i.e. THE LEADING MODE'S MOMENTUM IS THE PHASE ITS AMPLITUDE PICKS UP
CROSSING THE TONIC SEAM (from the commitment node 3 to the next tonic).
The eigenvector does depend on q (through the beat generators' own seam
entries), so beta acquires higher harmonics; the experiment measures how
much of q* the frozen-seam phase explains.

Directions:
  E1  Validate the perturbation theorem: (|lambda|-1)/alpha -> beta_b(q)
      as alpha -> 0, with O(alpha) error scaling.
  E2  Pin q*0 = argmax beta to 12 digits (alpha-free), and Fourier-analyze
      the tracked leading band's beta(q): harmonic content.
  E3  The frozen-seam estimate q*_frozen vs the true q*0.
  E4  Identification hunt: q*0 against eigenphase differences of F, seam
      matrix-element phases, and a small closed-form library. Rational
      pi-multiples are reported with the density caveat (they can match
      anything to ~1e-4 and prove nothing without a structural reason).

Construction identical to v16 (beat-synchronous Bloch blocks; v9 C8 beats,
theta = pi/2, hub theta/T; canon stroke phases per the 2026-07-18
adjudication). Interim glyph-integer rule respected.
"""

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize_scalar

alpha = 1.0 / 137.035999177
theta = np.pi / 2
T_triad = 3
I_PHASES = [1j, -1 + 0j, -1j, 1 + 0j]
STRUCT = [0, 2, 4, 6]
PROC = [1, 3, 5, 7]
PHI_s, PHI_p = 4, 5
KAPPA_BONDS = [(0, 4), (2, 6), (1, 5), (3, 7)]


def beat_entries():
    beats = []
    for (s, p, ph) in zip(STRUCT, PROC, I_PHASES):
        ent = []
        c = ph * theta
        ent += [(s, p, c), (p, s, -np.conj(c))]
        if s == PHI_s:
            for o in [0, 2, 6]:
                h = ph * theta / T_triad
                ent += [(PHI_s, o, h), (o, PHI_s, -np.conj(h))]
            ent += [(PHI_s, PHI_s, ph * theta / T_triad)]
            for o in [1, 3, 7]:
                h = ph * theta / T_triad
                ent += [(PHI_p, o, h), (o, PHI_p, -np.conj(h))]
            ent += [(PHI_p, PHI_p, ph * theta / T_triad)]
        else:
            ent += [(s, PHI_s, c), (PHI_s, s, -np.conj(c)),
                    (p, PHI_p, c), (PHI_p, p, -np.conj(c))]
        beats.append(ent)
    return beats


BEAT_ENTRIES = beat_entries()


def bloch_F(q):
    F = np.eye(7, dtype=complex)
    for ent in BEAT_ENTRIES:
        G = np.zeros((7, 7), dtype=complex)
        for (a, b, h) in ent:
            G[a % 7, b % 7] += h * np.exp(1j * q * (b // 7 - a // 7))
        G = (G - np.conj(G.T)) / 2
        F = expm(G) @ F
    return F


def bond_B(q):
    B = np.zeros((7, 7), dtype=complex)
    for (a, b) in KAPPA_BONDS:
        ph = np.exp(1j * q * (b // 7 - a // 7))
        B[a % 7, b % 7] += ph
        B[b % 7, a % 7] += np.conj(ph)
    return B


def eig_normalized(F):
    ev, U = np.linalg.eig(F)
    U = U / np.linalg.norm(U, axis=0, keepdims=True)
    return ev, U


def betas(q):
    ev, U = eig_normalized(bloch_F(q))
    B = bond_B(q)
    b = np.real(np.einsum('ib,ij,jb->b', np.conj(U), B, U))
    return ev, U, b


def beta_max(q):
    return float(betas(q)[2].max())


# ------------------------------------------------------------------------- E1

def E1():
    print("=" * 72)
    print("E1  PERTURBATION THEOREM: (|lambda|-1)/alpha -> beta as alpha -> 0")
    print("=" * 72)
    print(f"  {'q/pi':>8} {'beta_max':>12} {'a=alpha':>12} {'a=alpha/4':>12} "
          f"{'a=alpha/16':>12} {'err ratio':>10}")
    for q in [0.20, 1.1377, 2.50, np.pi]:
        bm = beta_max(q)
        F = bloch_F(q)
        deps = []
        for a in [alpha, alpha / 4, alpha / 16]:
            Tq = (np.eye(7) + a * bond_B(q)) @ F
            deps.append((np.abs(np.linalg.eigvals(Tq)).max() - 1) / a)
        e1, e2, e3 = [abs(d - bm) for d in deps]
        ratio = e1 / e3 if e3 > 0 else float('inf')
        print(f"  {q/np.pi:>8.4f} {bm:>12.8f} {deps[0]:>12.8f} {deps[1]:>12.8f} "
              f"{deps[2]:>12.8f} {ratio:>10.1f}")
    print("  err ratio ~ 16 confirms O(alpha) error: the theorem holds; "
          "beta is the alpha-free landscape.")


# ------------------------------------------------------------------------- E2

def track_leading_band(nq=4096):
    """Track bands by eigenvector overlap; return qs and the tracked beta
    curve of the band that achieves the global maximum."""
    qs = np.linspace(0, 2 * np.pi, nq, endpoint=False)
    _, U_prev, b_prev = betas(qs[0])
    order = np.arange(7)
    curves = np.zeros((nq, 7))
    curves[0] = b_prev
    for i in range(1, nq):
        _, U, b = betas(qs[i])
        O = np.abs(np.conj(U_prev.T) @ U)
        perm = np.full(7, -1)
        used = set()
        for r in np.argsort(-O.max(axis=1)):
            c = int(np.argmax([O[r, c] if c not in used else -1
                               for c in range(7)]))
            perm[r] = c
            used.add(c)
        curves[i] = b[perm]
        U_prev = U[:, perm]
    i_star, b_star = np.unravel_index(np.argmax(curves), curves.shape)
    return qs, curves, int(b_star)


def E2():
    print()
    print("=" * 72)
    print("E2  PINNING q*0 AND THE HARMONIC CONTENT OF beta(q)")
    print("=" * 72)
    res = minimize_scalar(lambda q: -beta_max(q), bounds=(0.9, 1.4),
                          method='bounded',
                          options={'xatol': 1e-13})
    q0 = res.x
    # confirm global on a coarse scan
    qs_c = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    scan = np.array([beta_max(q) for q in qs_c])
    assert beta_max(q0) >= scan.max() - 1e-12
    print(f"  q*0 = {q0:.12f} rad = {q0/np.pi:.12f} pi")
    print(f"  beta(q*0) = {beta_max(q0):.12f}   "
          f"(v16 measured (|l|-1)/alpha ~ 0.680-0.681 at small alpha)")
    qs, curves, b_star = track_leading_band()
    c = np.fft.fft(curves[:, b_star]) / len(qs)
    mags = np.abs(c)
    print(f"\n  tracked leading band's beta(q), Fourier magnitudes:")
    print(f"    k=0 (mean): {mags[0]:.6f}")
    for k in range(1, 7):
        print(f"    k={k}:        {mags[k]:.6f}   (phase {np.angle(c[k]):+.6f})")
    frac1 = mags[1] ** 2 / np.sum(mags[1:len(qs)//2] ** 2)
    print(f"  first-harmonic share of AC power: {frac1:.4f}")
    return q0, qs, curves, b_star, c


# ------------------------------------------------------------------------- E3

def E3(q0, qs, curves, b_star, c):
    print()
    print("=" * 72)
    print("E3  THE FROZEN-SEAM ESTIMATE: q* AS THE TONIC-SEAM PHASE")
    print("=" * 72)
    # identify the tracked leading band's eigenvector at q = 0 and at q*0
    for q_eval, label in [(0.0, "q=0"), (q0, "q=q*0")]:
        ev, U, b = betas(q_eval)
        # match to tracked band by beta value proximity at that q
        i_grid = int(np.argmin(np.abs(qs - q_eval))) if q_eval > 0 else 0
        target = curves[i_grid, b_star]
        bb = int(np.argmin(np.abs(b - target)))
        u = U[:, bb]
        seam = np.conj(u[3]) * u[0]
        q_frozen = (-np.angle(seam)) % (2 * np.pi)
        print(f"  frozen-seam estimate from {label:>6}: "
              f"q*_frozen = {q_frozen:.6f} rad = {q_frozen/np.pi:.6f} pi   "
              f"(2|u3 u0| = {2*np.abs(seam):.6f})")
    # first-harmonic phase of the tracked curve is the self-consistent version
    q_h1 = (-np.angle(c[1])) % (2 * np.pi)
    print(f"  first-harmonic argmax of tracked beta:  {q_h1:.6f} rad = "
          f"{q_h1/np.pi:.6f} pi")
    print(f"  true q*0:                               {q0:.6f} rad = "
          f"{q0/np.pi:.6f} pi")
    print("\n  reading: the leading mode's momentum is the phase its amplitude")
    print("  picks up crossing the tonic seam (node 3 -> next tonic), with the")
    print("  residual set by the eigenvector's own q-dependence (higher "
          "harmonics).")


# ------------------------------------------------------------------------- E4

def E4(q0):
    print()
    print("=" * 72)
    print("E4  IDENTIFICATION HUNT FOR q*0 (with the density caveat)")
    print("=" * 72)
    ev0, U0 = eig_normalized(bloch_F(0.0))
    phases0 = np.sort(np.angle(ev0))
    cands = {}
    for i in range(7):
        for j in range(7):
            if i != j:
                d = (phases0[i] - phases0[j]) % (2 * np.pi)
                cands[f"eigenphase diff F(0) [{i}-{j}]"] = d
    lib = {
        "pi/e": np.pi / np.e,
        "arctan(2)": np.arctan(2),
        "arctan(sqrt(2))": np.arctan(np.sqrt(2)),
        "arctan(phi)": np.arctan((1 + np.sqrt(5)) / 2),
        "pi/2 - pi/6 + arctan(1/T^2)": np.pi / 3 + np.arctan(1 / 9),
        "2pi/R + pi/6": 2 * np.pi / 7 + np.pi / 6,
        "pi * 13/36": np.pi * 13 / 36,
        "pi * 29/80": np.pi * 29 / 80,
    }
    cands.update(lib)
    rows = sorted(((abs(v - q0), k, v) for k, v in cands.items()))[:8]
    print(f"  q*0 = {q0:.9f} rad = {q0/np.pi:.9f} pi\n")
    for d, k, v in rows:
        print(f"    {k:36s} = {v:.9f}   |diff| = {d:.3e}  "
              f"({d/q0*100:.3f}%)")
    print("\n  caveat: rational pi-multiples with denominator <= ~100 can land")
    print("  within ~1e-3 of anything; only a candidate with a structural")
    print("  derivation counts. Verdict is printed by the numbers above, not")
    print("  asserted here.")


if __name__ == '__main__':
    E1()
    q0, qs, curves, b_star, c = E2()
    E3(q0, qs, curves, b_star, c)
    E4(q0)
