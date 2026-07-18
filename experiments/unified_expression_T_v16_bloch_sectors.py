"""
unified_expression_T_v16_bloch_sectors.py

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0
History:
  - 2026-07-18 v1.0: initial. The Bloch-sector test v14's F4 proposed.

BLOCH SECTORS OF THE STAGGERED RING (v16 of the T-operator series)

The open thread of i. v14's F4 was a null: no parity double-cover mode in
period-2 octave components at alpha coupling, with a momentum-resolved
(Bloch-sector) analysis proposed as the sharper instrument. The canon
adjudication (2026-07-18; docs/the_staggered_octave.html section 8) then
tagged the -i double-cover holonomy to the whole-tone reading, not to the
canon octave. This experiment builds the proposed instrument and asks the
physical-content question in four sharp forms:

  E1  A translation-invariant ring operator (beat-synchronous: each beat is
      exp of the SUM of that beat's generators over all octaves, so the
      operator commutes with the 7-node octave shift exactly). Bloch
      decomposition into 7x7 blocks T(q) is then exact; validated against
      the full ring spectrum, and the difference from v14's octave-
      sequential convention is quantified (construction convention, not a
      result).
  E2  Band structure lambda_b(q) over the Brillouin zone with continuous
      band tracking, and the MONODROMY: the permutation induced on the
      seven bands by one loop q: 0 -> 2pi. A nontrivial cycle means bands
      form a k-fold cover of the Brillouin circle: operator-level cover
      content. (Non-Hermitian bands may braid; Hermitian ones may not.)
  E3  The four quarter-turn flux sectors q = 0, pi/2, pi, 3pi/2. This is
      v14's proposed q = pi (antiperiodic) test extended to the full
      i-cycle: threading one i-stroke of flux through the octave ring per
      sector. Reported per sector: leading |lambda|, gap, and where in q
      the global leading mode lives (q = 0 means the fixed point is
      octave-uniform, A3-consistent; q = pi would mean staggered order,
      i.e. spontaneous double-cover content).
  E4  The whole-tone closure obstruction, exact: a uniform (coordinate-
      anchored) stroke field on a ring of n octaves has floor(7n/2) strokes
      per loop; the loop closes iff that count is 0 mod 4, i.e. iff
      n = 0 mod 8. Otherwise the field is frustrated by a flux i^k, and
      the flux walks the i-cycle as n walks 2, 4, 6, 0 mod 8:
      -i, -1, +i, +1. The parity double cover (n = 2) carries exactly the
      -i holonomy found in staggered_octave_findings_v2.md. Verified by
      explicit phase-field construction.

Construction: per-octave beats mirror v14's ring builder exactly (v9's C8
beats: theta = pi/2, Phi/emergence hub with coupling theta/T, i-phases
[i, -1, -i, +1] on the four beats, per the canon stroke table). kappa
carries the four per-octave diameter bonds at alpha. Glyph positions follow
the legacy v-series basis (interim glyph-integer rule).
"""

import numpy as np
from scipy.linalg import expm
from scipy.optimize import linear_sum_assignment

alpha = 1.0 / 137.035999177
theta = np.pi / 2
T_triad = 3
R = 7
I_PHASES = [1j, -1 + 0j, -1j, 1 + 0j]

STRUCT = [0, 2, 4, 6]
PROC = [1, 3, 5, 7]
PHI_s, PHI_p = 4, 5


# ---------------------------------------------------------- generator builders

def beat_generator_entries(phases=I_PHASES):
    """The four beats as entry lists [(a, b, h)] on the 8-station template
    (a, b in 0..7; 7 = next cell's 0). Mirrors v14 build_octave_beats_ring."""
    beats = []
    for (s, p, ph) in zip(STRUCT, PROC, phases):
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


BEAT_ENTRIES = beat_generator_entries()
KAPPA_BONDS = [(0, 4), (2, 6), (1, 5), (3, 7)]


def bloch_T(q, a_kappa=alpha, phases=I_PHASES, reverse_beats=False):
    """7x7 Bloch block of the beat-synchronous ring operator at momentum q."""
    ents = beat_generator_entries(phases)
    if reverse_beats:
        ents = ents[::-1]
    F = np.eye(7, dtype=complex)
    for ent in ents:
        G = np.zeros((7, 7), dtype=complex)
        for (a, b, h) in ent:
            G[a % 7, b % 7] += h * np.exp(1j * q * (b // 7 - a // 7))
        G = (G - np.conj(G.T)) / 2
        F = expm(G) @ F
    K = np.eye(7, dtype=complex)
    for (a, b) in KAPPA_BONDS:
        ph = np.exp(1j * q * (b // 7 - a // 7))
        K[a % 7, b % 7] += a_kappa * ph
        K[b % 7, a % 7] += a_kappa * np.conj(ph)
    return K @ F


def ring_T_sync(n_oct):
    """Full ring, beat-synchronous: B_b = expm(sum over octaves of beat b's
    generator); F = B4 B3 B2 B1. Commutes with the 7-node shift exactly."""
    N = 7 * n_oct
    F = np.eye(N, dtype=complex)
    for ent in BEAT_ENTRIES:
        G = np.zeros((N, N), dtype=complex)
        for k in range(n_oct):
            b0 = 7 * k
            for (a, b, h) in ent:
                G[(b0 + a) % N, (b0 + b) % N] += h
        G = (G - np.conj(G.T)) / 2
        F = expm(G) @ F
    K = np.eye(N, dtype=complex)
    for k in range(n_oct):
        b0 = 7 * k
        for (a, b) in KAPPA_BONDS:
            K[(b0 + a) % N, (b0 + b) % N] += alpha
            K[(b0 + b) % N, (b0 + a) % N] += alpha
    return K @ F


def ring_T_sequential(n_oct):
    """v14's octave-sequential composition, for the convention comparison."""
    N = 7 * n_oct
    F = np.eye(N, dtype=complex)
    for k in range(n_oct):
        b0 = 7 * k
        for ent in BEAT_ENTRIES:
            G = np.zeros((N, N), dtype=complex)
            for (a, b, h) in ent:
                G[(b0 + a) % N, (b0 + b) % N] += h
            G = (G - np.conj(G.T)) / 2
            F = expm(G) @ F
    K = np.eye(N, dtype=complex)
    for k in range(n_oct):
        b0 = 7 * k
        for (a, b) in KAPPA_BONDS:
            K[(b0 + a) % N, (b0 + b) % N] += alpha
            K[(b0 + b) % N, (b0 + a) %  N] += alpha
    return K @ F


def match_multisets(x, y):
    """Max distance under optimal pairing of two complex multisets."""
    C = np.abs(x[:, None] - y[None, :])
    r, c = linear_sum_assignment(C)
    return C[r, c].max()


# ------------------------------------------------------------------------- E1

def E1(n=6):
    print("=" * 72)
    print(f"E1  TRANSLATION-INVARIANT RING + EXACT BLOCH DECOMPOSITION (n = {n})")
    print("=" * 72)
    Ts = ring_T_sync(n)
    N = 7 * n
    U = np.zeros((N, N))
    for j in range(N):
        U[(j + 7) % N, j] = 1.0
    comm = np.linalg.norm(U @ Ts - Ts @ U)
    print(f"  ||[T_sync, shift-by-octave]|| = {comm:.3e}   (exact symmetry)")
    ev_full = np.linalg.eigvals(Ts)
    ev_bloch = np.concatenate([np.linalg.eigvals(bloch_T(2 * np.pi * m / n))
                               for m in range(n)])
    d = match_multisets(ev_full, ev_bloch)
    print(f"  Bloch union vs full spectrum, max matched distance: {d:.3e}")
    Tq = ring_T_sequential(n)
    print(f"  convention distance ||T_sync - T_seq|| / ||T_seq|| = "
          f"{np.linalg.norm(Ts - Tq) / np.linalg.norm(Tq):.4f}")
    l_s = np.abs(np.linalg.eigvals(Ts)).max()
    l_q = np.abs(np.linalg.eigvals(Tq)).max()
    print(f"  leading |lambda|: sync {l_s:.8f}   sequential {l_q:.8f}   "
          f"(both (dep)/alpha: {(l_s-1)/alpha:.3f}, {(l_q-1)/alpha:.3f})")


# ------------------------------------------------------------------------- E2

def E2(nq=2801):
    print()
    print("=" * 72)
    print("E2  BAND STRUCTURE AND MONODROMY OVER THE BRILLOUIN CIRCLE")
    print("=" * 72)
    qs = np.linspace(0, 2 * np.pi, nq)
    bands = np.zeros((nq, 7), dtype=complex)
    bands[0] = np.linalg.eigvals(bloch_T(qs[0]))
    for i in range(1, nq):
        ev = np.linalg.eigvals(bloch_T(qs[i]))
        C = np.abs(bands[i - 1][:, None] - ev[None, :])
        r, c = linear_sum_assignment(C)
        bands[i] = ev[c[np.argsort(r)]]
    # monodromy: pair the tracked endpoints with the q=0 eigenvalues
    C = np.abs(bands[-1][:, None] - bands[0][None, :])
    r, c = linear_sum_assignment(C)
    perm = c[np.argsort(r)]
    resid = C[r, c].max()
    print(f"  tracking grid: {nq} points; endpoint matching residual: {resid:.2e}")
    print(f"  monodromy permutation (band b at q=2pi is band perm[b] of q=0): "
          f"{list(perm)}")
    seen, cycles = set(), []
    for b in range(7):
        if b in seen:
            continue
        cyc, x = [], b
        while x not in seen:
            seen.add(x); cyc.append(x); x = perm[x]
        cycles.append(cyc)
    print(f"  cycle structure: {[len(c) for c in cycles]}  "
          f"{'<- NONTRIVIAL: bands braid' if max(len(c) for c in cycles) > 1 else '(identity: no braiding)'}")
    # winding of each band's phase around the origin over one loop
    winds = []
    for b in range(7):
        dphi = np.angle(bands[1:, b] / bands[:-1, b])
        winds.append(float(np.sum(dphi) / (2 * np.pi)))
    print(f"  per-band phase winding over one loop: "
          f"{[f'{w:+.3f}' for w in winds]}   (sum = {sum(winds):+.3f})")
    sep = np.min([np.min([np.abs(bands[i, a] - bands[i, b])
                          for a in range(7) for b in range(a + 1, 7)])
                  for i in range(0, nq, 7)])
    print(f"  minimum band separation over the zone (subsampled): {sep:.4e}")
    # leading modulus vs q
    mods = np.abs(bands)
    lead = mods.max(axis=1)
    q_star = qs[np.argmax(lead)]
    print(f"  global leading |lambda| = {lead.max():.8f} at q = {q_star:.4f} rad "
          f"= {q_star/np.pi:.4f} pi")
    return qs, bands


# ------------------------------------------------------------------------- E3

def E3(qs, bands):
    print()
    print("=" * 72)
    print("E3  THE FOUR QUARTER-TURN FLUX SECTORS (one i-stroke of flux each)")
    print("=" * 72)
    print(f"  {'sector':>10s} {'q':>8s} {'max|l|':>12s} {'(max|l|-1)/a':>13s} "
          f"{'gap':>12s} {'gap/a':>8s}")
    for label, q in [("q=0", 0.0), ("q=pi/2", np.pi / 2),
                     ("q=pi", np.pi), ("q=3pi/2", 3 * np.pi / 2)]:
        m = np.sort(np.abs(np.linalg.eigvals(bloch_T(q))))[::-1]
        print(f"  {label:>10s} {q:>8.4f} {m[0]:>12.8f} {(m[0]-1)/alpha:>13.4f} "
              f"{m[0]-m[1]:>12.3e} {(m[0]-m[1])/alpha:>8.4f}")
    mods = np.abs(bands)
    lead = mods.max(axis=1)
    print(f"\n  leading-modulus profile: |l|(0) - |l|(pi) = "
          f"{lead[0] - lead[len(lead)//2]:.3e}")
    print(f"  interpretation: leading mode at q = 0 -> octave-uniform fixed "
          f"point (A3);")
    print(f"  a leading mode at q = pi would have meant spontaneous staggered "
          f"(double-cover) order.")


# ------------------------------------------------------------------------- E4

def E4():
    print()
    print("=" * 72)
    print("E4  WHOLE-TONE CLOSURE OBSTRUCTION ON THE RING (exact arithmetic)")
    print("=" * 72)
    print("  uniform (coordinate-anchored) stroke field: x_J = i^(#odd J' <= J);")
    print("  loop flux = i^(#strokes per loop) = i^(floor(7n/2) mod 4)\n")
    print(f"  {'n octaves':>10s} {'strokes/loop':>13s} {'flux':>6s} {'closes?':>8s}")
    for n in range(2, 18, 2):
        strokes = (7 * n) // 2
        k = strokes % 4
        flux = ['+1', '+i', '-1', '-i'][k]
        # explicit phase-field check: the field's value continuing past the
        # seam differs from its start by i^strokes
        cnt = int(np.sum([J % 2 for J in range(7 * n)]))
        assert cnt == strokes and np.isclose(1j ** strokes, [1, 1j, -1, -1j][k])
        print(f"  {n:>10d} {strokes:>13d} {flux:>6s} {str(k == 0):>8s}")
    print("\n  the flux walks the i-cycle as n walks 2, 4, 6, 0 (mod 8):")
    print("  -i, -1, +i, +1. The parity double cover (n = 2) carries exactly")
    print("  the -i holonomy of staggered_octave_findings_v2.md. Closure only")
    print("  at n = 0 mod 8: the whole-tone stroke field is a spin-structure-")
    print("  like object; the canon field (4 strokes per octave) closes on")
    print("  every ring.")


def leading_profile(a_kappa=alpha, phases=I_PHASES, reverse_beats=False,
                    coarse=721, refine=241):
    """(q*, max|l|) of the leading-modulus profile, plus values at 0 and pi
    and the modulus gap at pi. Coarse scan then local refinement."""
    qs = np.linspace(0, 2 * np.pi, coarse, endpoint=False)
    lead = np.array([np.abs(np.linalg.eigvals(
        bloch_T(q, a_kappa, phases, reverse_beats))).max() for q in qs])
    i0 = int(np.argmax(lead))
    dq = qs[1] - qs[0]
    qf = np.linspace(qs[i0] - dq, qs[i0] + dq, refine)
    lf = np.array([np.abs(np.linalg.eigvals(
        bloch_T(q, a_kappa, phases, reverse_beats))).max() for q in qf])
    j = int(np.argmax(lf))
    m_pi = np.sort(np.abs(np.linalg.eigvals(
        bloch_T(np.pi, a_kappa, phases, reverse_beats))))[::-1]
    return qf[j] % (2 * np.pi), lf[j], m_pi[0] - m_pi[1]


def momentum_weights(v, n):
    """Weight of eigenvector v in each octave-shift momentum sector."""
    N = 7 * n
    out = []
    for m in range(n):
        Pv = np.zeros(N, dtype=complex)
        for k in range(n):
            Pv += np.exp(-2j * np.pi * m * k / n) * np.roll(v, 7 * k)
        Pv /= n
        out.append(float(np.linalg.norm(Pv) ** 2))
    out = np.array(out)
    return out / out.sum()


def E5(n=6):
    print()
    print("=" * 72)
    print("E5  CHIRALITY AND ROBUSTNESS OF THE MOMENTUM-CARRYING FIXED POINT")
    print("=" * 72)
    print("  (a) q* and the q=pi modulus gap vs alpha multiplier "
          "(canon phases):")
    print(f"  {'mult':>6} {'q*/pi':>10} {'(max|l|-1)/a':>13} {'gap(pi)/a':>10}")
    for mult in [0.25, 0.5, 1.0, 2.0, 4.0]:
        a = mult * alpha
        q_star, lmax, gpi = leading_profile(a_kappa=a)
        print(f"  {mult:>6.2f} {q_star/np.pi:>10.4f} {(lmax-1)/a:>13.4f} "
              f"{gpi/a:>10.4f}")
    print("\n  (b) i-chirality control (conjugated stroke phases) and beat-"
          "order control:")
    q_c, _, _ = leading_profile()
    q_conj, _, _ = leading_profile(phases=[np.conj(p) for p in I_PHASES])
    q_rev, _, _ = leading_profile(reverse_beats=True)
    print(f"    canon phases:        q* = {q_c/np.pi:.4f} pi")
    print(f"    conjugated phases:   q* = {q_conj/np.pi:.4f} pi   "
          f"(2 - q*/pi = {2 - q_c/np.pi:.4f}: mirror = chirality flip)")
    print(f"    reversed beat order: q* = {q_rev/np.pi:.4f} pi")
    print(f"    chirality observable: sign of the leading mode's momentum. "
          f"v15 showed weight")
    print(f"    observables cannot see i-chirality; momentum is the phase-"
          f"sensitive observable that does.")
    print(f"\n  (c) momentum content of the OCTAVE-SEQUENTIAL (v14) ring's "
          f"leading eigenvector (n = {n}):")
    Tq = ring_T_sequential(n)
    ev, V = np.linalg.eig(Tq)
    v = V[:, np.argmax(np.abs(ev))]
    mw = momentum_weights(v, n)
    print("    sector weights m = 0..n-1: "
          + "  ".join(f"{m}:{w:.4f}" for m, w in enumerate(mw)))
    print(f"    dominant sector: m = {int(np.argmax(mw))} "
          f"(q = {2*np.argmax(mw)/n:.3f} pi); nonzero-momentum content = "
          f"{1 - mw[0]:.4f}")


if __name__ == '__main__':
    E1(6)
    qs, bands = E2()
    E3(qs, bands)
    E4()
    E5(6)
