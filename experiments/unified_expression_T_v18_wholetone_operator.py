"""
unified_expression_T_v18_wholetone_operator.py

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0
History:
  - 2026-07-18 v1.0: initial. The whole-tone operator and the braiding hunt.

THE WHOLE-TONE OPERATOR (v18 of the T-operator series)

v16 established: the canon ring's bands are topologically trivial (identity
monodromy, zero windings), and the whole-tone stroke field is frustrated on
rings (flux walking the i-cycle, closing only at n = 0 mod 8). Open question
v16 left: does an operator BUILT on the whole-tone phase field show the band
braiding canon lacks?

CONSTRUCTION. Identical beat geometry to v16/v17 (v9 C8 beats, theta = pi/2,
hub theta/T, beat-synchronous composition). The only change is where each
beat's i-phase comes from. Both conventions read the phase off a stroke
field evaluated at the beat's processual node (global half-step index J_p):

  canon:      m(J) = 4*(J div 7) + ceil((J mod 7)/2)   (strokes at
              processual residues; 4 per octave; reproduces the stroke
              table i^1..i^0 identically in every octave)
  whole-tone: m(J) = ceil(J/2)                          (strokes at odd
              coordinates; 3.5 per octave on average)

phase(beat) = i^m(J_p). In octave 0 the two agree; from octave 1 on they
diverge, and the whole-tone pattern repeats only after 8 octaves (56 nodes),
per the v2/v16 flux arithmetic. So the whole-tone operator's true unit cell
is 56 nodes, and both operators are built here on that cell (canon serves as
the folded control: same cell, same geometry, canon phases).

Directions:
  E1  Builder validation: the canon 56-cell's Bloch spectrum at momentum q
      must equal the union of the canon 7-cell's bands at the eight
      unfolded momenta (q + 2 pi m)/8. Also: on a 112-node ring the
      whole-tone operator must break the 7-node shift symmetry but keep
      the 56-node one; canon keeps both.
  E2  The braiding hunt: track all 56 bands over the Brillouin circle by
      eigenvector-overlap assignment; monodromy cycle structure; det
      winding (tracking-free); minimum band separation. The canon-56
      control calibrates the folded description: a system whose true cell
      is 7 nodes must show seven 8-cycles (spectral flow by one sector per
      loop, order = folding multiplicity) with near-exact sector crossings;
      whole-tone deviations from that pattern are physical.
  E3  Conservation and chirality of the whole-tone operator: departure
      from |lambda| = 1 per alpha; leading-mode momentum; i-conjugation
      control.

Interim glyph-integer rule respected. The whole-tone reading is computed
here as the named alternative the adjudication retained; nothing in this
file promotes it to canon.
"""

import numpy as np
from scipy.linalg import expm
from scipy.optimize import linear_sum_assignment

alpha = 1.0 / 137.035999177
theta = np.pi / 2
T_triad = 3
STRUCT = [0, 2, 4, 6]
PROC = [1, 3, 5, 7]
PHI_s, PHI_p = 4, 5
KAPPA_BONDS = [(0, 4), (2, 6), (1, 5), (3, 7)]

N_OCT_CELL = 8
N_CELL = 7 * N_OCT_CELL  # 56


def m_canon(J):
    k, l = divmod(J, 7)
    return 4 * k + (l + 1) // 2


def m_wholetone(J):
    return (J + 1) // 2


def cell_beat_entries(m_field):
    """Entries [(a, b, h)] per beat index (4 lists), summed over the 8
    octaves of the 56-node cell. Node index 56 means next cell's node 0."""
    beats = [[] for _ in range(4)]
    for k in range(N_OCT_CELL):
        base = 7 * k
        for bi, (s, p) in enumerate(zip(STRUCT, PROC)):
            ph = 1j ** (m_field(base + p) % 4)
            c = ph * theta
            ent = [(s, p, c), (p, s, -np.conj(c))]
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
            beats[bi] += [(base + a, base + b, h) for (a, b, h) in ent]
    return beats


def compile_field(m_field):
    """Precompile: per beat, the intra-cell generator plus the (few) seam
    entries; likewise for kappa. Only the seam entries depend on q."""
    beats = []
    for ent in cell_beat_entries(m_field):
        G0 = np.zeros((N_CELL, N_CELL), dtype=complex)
        seam = []
        for (a, b, h) in ent:
            off = b // N_CELL - a // N_CELL
            if off == 0:
                G0[a % N_CELL, b % N_CELL] += h
            else:
                seam.append((a % N_CELL, b % N_CELL, h, off))
        beats.append((G0, seam))
    K0 = np.eye(N_CELL, dtype=complex)
    kseam = []
    for k in range(N_OCT_CELL):
        base = 7 * k
        for (a, b) in KAPPA_BONDS:
            aa, bb = base + a, base + b
            off = bb // N_CELL - aa // N_CELL
            if off == 0:
                K0[aa % N_CELL, bb % N_CELL] += alpha
                K0[bb % N_CELL, aa % N_CELL] += alpha
            else:
                kseam.append((aa % N_CELL, bb % N_CELL, off))
    return beats, K0, kseam


_COMPILED = {}


def expm_ah(G):
    """exp of an anti-Hermitian matrix via eigh (G = -i H, H Hermitian)."""
    w, V = np.linalg.eigh(1j * G)
    return (V * np.exp(-1j * w)) @ np.conj(V.T)


def bloch_T56(q, m_field):
    key = m_field.__name__
    if key not in _COMPILED:
        _COMPILED[key] = compile_field(m_field)
    beats, K0, kseam = _COMPILED[key]
    F = np.eye(N_CELL, dtype=complex)
    for (G0, seam) in beats:
        G = G0.copy()
        for (a, b, h, off) in seam:
            G[a, b] += h * np.exp(1j * q * off)
        G = (G - np.conj(G.T)) / 2
        F = expm_ah(G) @ F
    K = K0.copy()
    for (a, b, off) in kseam:
        K[a, b] += alpha * np.exp(1j * q * off)
        K[b, a] += alpha * np.exp(-1j * q * off)
    return K @ F


def bloch_T7(q):
    """v16's canon 7-node Bloch block (for the folding check)."""
    F = np.eye(7, dtype=complex)
    for bi, (s, p) in enumerate(zip(STRUCT, PROC)):
        ph = 1j ** (m_canon(p) % 4)
        c = ph * theta
        ent = [(s, p, c), (p, s, -np.conj(c))]
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
        G = np.zeros((7, 7), dtype=complex)
        for (a, b, h) in ent:
            G[a % 7, b % 7] += h * np.exp(1j * q * (b // 7 - a // 7))
        G = (G - np.conj(G.T)) / 2
        F = expm(G) @ F
    K = np.eye(7, dtype=complex)
    for (a, b) in KAPPA_BONDS:
        ph = np.exp(1j * q * (b // 7 - a // 7))
        K[a % 7, b % 7] += alpha * ph
        K[b % 7, a % 7] += alpha * np.conj(ph)
    return K @ F


def ring_T(n_oct, m_field):
    """Full ring, beat-synchronous, phases from m_field."""
    N = 7 * n_oct
    F = np.eye(N, dtype=complex)
    for bi in range(4):
        G = np.zeros((N, N), dtype=complex)
        for k in range(n_oct):
            base = 7 * k
            s, p = STRUCT[bi], PROC[bi]
            ph = 1j ** (m_field(base + p) % 4)
            c = ph * theta
            ent = [(s, p, c), (p, s, -np.conj(c))]
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
            for (a, b, h) in ent:
                G[(base + a) % N, (base + b) % N] += h
        G = (G - np.conj(G.T)) / 2
        F = expm(G) @ F
    K = np.eye(N, dtype=complex)
    for k in range(n_oct):
        base = 7 * k
        for (a, b) in KAPPA_BONDS:
            K[(base + a) % N, (base + b) % N] += alpha
            K[(base + b) % N, (base + a) % N] += alpha
    return K @ F


def shift_op(N, s):
    U = np.zeros((N, N))
    for j in range(N):
        U[(j + s) % N, j] = 1.0
    return U


def match_multisets(x, y):
    C = np.abs(x[:, None] - y[None, :])
    r, c = linear_sum_assignment(C)
    return C[r, c].max()


# ------------------------------------------------------------------------- E1

def E1():
    print("=" * 72)
    print("E1  BUILDER VALIDATION: FOLDING AND SYMMETRY")
    print("=" * 72)
    for q in [0.3, 2.0]:
        ev56 = np.linalg.eigvals(bloch_T56(q, m_canon))
        ev7 = np.concatenate([np.linalg.eigvals(
            bloch_T7((q + 2 * np.pi * m) / 8)) for m in range(8)])
        print(f"  canon 56-cell vs folded 7-cell at q = {q}: max matched "
              f"distance = {match_multisets(ev56, ev7):.3e}")
    n = 16
    N = 7 * n
    Twt = ring_T(n, m_wholetone)
    Tc = ring_T(n, m_canon)
    U7, U56 = shift_op(N, 7), shift_op(N, 56)
    print(f"\n  112-node ring commutators (Frobenius):")
    print(f"    canon:      ||[T, U7]|| = {np.linalg.norm(Tc @ U7 - U7 @ Tc):.3e}"
          f"   ||[T, U56]|| = {np.linalg.norm(Tc @ U56 - U56 @ Tc):.3e}")
    print(f"    whole-tone: ||[T, U7]|| = {np.linalg.norm(Twt @ U7 - U7 @ Twt):.3e}"
          f"   ||[T, U56]|| = {np.linalg.norm(Twt @ U56 - U56 @ Twt):.3e}")
    print("  expected: whole-tone breaks the octave shift, keeps the 8-octave "
          "shift.")


# ------------------------------------------------------------------------- E2

def band_run(m_field, nq):
    qs = np.linspace(0, 2 * np.pi, nq, endpoint=False)
    ev, U = np.linalg.eig(bloch_T56(qs[0], m_field))
    U = U / np.linalg.norm(U, axis=0, keepdims=True)
    ev0, U0 = ev.copy(), U.copy()
    bands = np.zeros((nq, N_CELL), dtype=complex)
    bands[0] = ev
    min_sep = np.inf
    U_prev, ev_prev = U, ev
    for i in range(1, nq):
        ev, U = np.linalg.eig(bloch_T56(qs[i], m_field))
        U = U / np.linalg.norm(U, axis=0, keepdims=True)
        O = -np.abs(np.conj(U_prev.T) @ U)
        r, c = linear_sum_assignment(O)
        perm = c[np.argsort(r)]
        ev, U = ev[perm], U[:, perm]
        bands[i] = ev
        d = np.abs(ev[:, None] - ev[None, :]) + np.eye(N_CELL) * 1e9
        min_sep = min(min_sep, d.min())
        U_prev, ev_prev = U, ev
    # close the loop: match final tracked frame to the initial one
    O = -np.abs(np.conj(U_prev.T) @ U0)
    r, c = linear_sum_assignment(O)
    perm = c[np.argsort(r)]
    resid = np.abs(bands[-1] - ev0[perm]).max()  # rough closure sanity
    return qs, bands, perm, min_sep, resid


def cycles_of(perm):
    seen, cyc = set(), []
    for b in range(len(perm)):
        if b in seen:
            continue
        cur, x = [], b
        while x not in seen:
            seen.add(x)
            cur.append(x)
            x = int(perm[x])
        cyc.append(cur)
    return cyc


def det_winding_from_bands(bands):
    """Winding of det T(q) around one loop, from the tracked eigenvalues
    (det = product of all bands; tracking-independent)."""
    d = np.prod(bands, axis=1)
    d = np.append(d, d[0])
    return float(np.sum(np.angle(d[1:] / d[:-1])) / (2 * np.pi))


def E2(nq=2048):
    print()
    print("=" * 72)
    print("E2  THE BRAIDING HUNT: MONODROMY OF 56 BANDS")
    print("=" * 72)
    out = {}
    for label, mf in [("canon-56 (control)", m_canon),
                      ("whole-tone", m_wholetone)]:
        qs, bands, perm, min_sep, resid = band_run(mf, nq)
        cyc = cycles_of(perm)
        sizes = sorted((len(c) for c in cyc), reverse=True)
        n_nontriv = sum(1 for s in sizes if s > 1)
        w = det_winding_from_bands(bands)
        out[label] = (sizes, min_sep)
        print(f"\n  {label}:")
        print(f"    monodromy cycle sizes: {sizes[:12]}{'...' if len(sizes) > 12 else ''}")
        print(f"    nontrivial cycles: {n_nontriv}   largest: {sizes[0]}")
        print(f"    min band separation over zone: {min_sep:.4e}")
        print(f"    det winding: {w:+.4f}")
    print("\n  folding calibration: canon's TRUE cell is 7 nodes, so its 56-cell")
    print("  bands must flow by one momentum sector per zone loop: seven 8-cycles")
    print("  (cycle order = folding multiplicity), with near-exact crossings at")
    print("  the sector intersections. Whole-tone deviations from that pattern")
    print("  are physical, not artifacts.")
    return out


def E2_robust(nq_list=(512, 1024, 2048)):
    print("\n  grid-robustness of the whole-tone monodromy:")
    for nq in nq_list:
        _, _, perm, min_sep, _ = band_run(m_wholetone, nq)
        sizes = sorted((len(c) for c in cycles_of(perm)), reverse=True)
        n_nontriv = sum(1 for s in sizes if s > 1)
        print(f"    nq = {nq}: nontrivial cycles = {n_nontriv}, "
              f"largest = {sizes[0]}, min sep = {min_sep:.3e}")


# ------------------------------------------------------------------------- E3

def E3():
    print()
    print("=" * 72)
    print("E3  CONSERVATION AND CHIRALITY OF THE WHOLE-TONE OPERATOR")
    print("=" * 72)
    qs = np.linspace(0, 2 * np.pi, 257, endpoint=False)
    lead = []
    for q in qs:
        lead.append(np.abs(np.linalg.eigvals(bloch_T56(q, m_wholetone))).max())
    lead = np.array(lead)
    i0 = int(np.argmax(lead))
    print(f"  whole-tone departure (max over zone): "
          f"(|l|-1)/alpha = {(lead.max()-1)/alpha:.4f}   "
          f"(canon, v16: 0.68)")
    print(f"  leading momentum (56-node cell): q* = {qs[i0]/np.pi:.4f} pi "
          f"(cell = 8 octaves, so per-octave phase = q*/8 + m*pi/4 branch)")
    # i-conjugation: build with conjugated field phases
    def m_wt_conj(J):
        return -m_wholetone(J) % 4
    lead_c = []
    for q in qs:
        lead_c.append(np.abs(np.linalg.eigvals(
            bloch_T56(q, m_wt_conj))).max())
    i0c = int(np.argmax(np.array(lead_c)))
    print(f"  conjugated-field leading momentum: q* = {qs[i0c]/np.pi:.4f} pi "
          f"(mirror of {2 - qs[i0]/np.pi:.4f} pi expected under chirality flip)")


if __name__ == '__main__':
    E1()
    E2(2048)
    E2_robust()
    E3()
