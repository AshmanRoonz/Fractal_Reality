"""
staggered_octave_z7_dft_v1.py

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0
History:
  - 2026-07-18 v1.0: initial. DFT of the rung functions on the residue group Z7;
    exact permutation nulls; character-level (Gauss-sum) analysis; mod-R structure.

THE Z7 SPECTRUM OF THE RUNG FUNCTIONS

The staggered octave (framework section 27.7t; docs/octave_wrap_lemma.html
section 8) establishes that the ladder's residue group is Z7: seven residue
classes on the half-step lattice modulo the wrap d + 3.5 = d', with one
constant per residue class. Any function assigning a number to each rung is
therefore a function on Z7, and Z7 carries a natural harmonic analysis: the
discrete Fourier transform over the 7th roots of unity.

Question (raised in session, 2026-07-18): do the rung functions have
CONCENTRATED spectrum on Z7, or flat, or unremarkable?

Rung functions tested (residue index j = 0..6, dimension d = j/2):

  f_A   A(d)  = d(2d+1)  = [0, 1, 3, 6, 10, 15, 21]   (accumulated traversal,
                            TYPE A, the selection rule; triangular numbers
                            T_j = j(j+1)/2 in half-step index)
  f_A'  A'(d) = 4d + 1   = [1, 3, 5, 7, 9, 11, 13]    (local splitting,
                            TYPE B; odd numbers 2j + 1)
  f_E   alpha-step exponent of the constant at each rung, 0 where the
        constant carries no alpha-dependence (c, hbar, pi):
        [1, 0, 0, 13/12, 0, 56/39, 21]
        (convention flagged: the zeros are a bookkeeping choice)
  f_ln  natural log of the dimensionless magnitude at each rung:
        [ln(1/alpha), ln c, ln hbar, ln(m_mu/m_e), ln pi,
         ln(v/Lambda_QCD), ln(1/alpha_G)]

Directions:
  E1  Value-level DFT of each function; conjugate-pair power fractions,
      spectral entropy, and an EXACT permutation null (all 7! = 5040
      orderings of the same seven values; no sampling).
  E2  Character-level DFT: x_j = exp(2*pi*i*f_j / 7) for the integer
      sequences A and A'. Analytic expectations:
        A  is quadratic in j (T_j = j(j+1)/2 = 4j^2 + 4j mod 7), so its
           character sequence is a Gauss-sum object: a Zadoff-Chu (CAZAC)
           chirp with |X_k| = sqrt(7) for ALL k (maximally FLAT spectrum)
           and cyclic autocorrelation exactly ZERO at every nontrivial shift.
        A' is linear in j (2j + 1), so its character sequence is a pure
           tone: all energy at a single frequency (maximally CONCENTRATED),
           autocorrelation of full magnitude at every shift.
      Since A' = dA/dd, the TYPE A / TYPE B pair is the chirp/tone pair.
  E3  Mod-R structure: A mod 7 is a palindrome [0,1,3,6,3,1,0] with sum
      2R = 14; A' mod 7 = [1,3,5,0,2,4,6] is a BIJECTION on Z7 (visits
      every residue class exactly once per octave).

Proof of the E2 chirp claims (two lines, verified numerically below):
  Autocorrelation at shift s:  sum_j exp(2*pi*i*(A_{j+s} - A_j)/7)
  and A_{j+s} - A_j = j*s + s(s+1)/2, so the sum factors as
  exp(2*pi*i*A_s/7) * sum_j exp(2*pi*i*j*s/7) = 0 for s != 0 mod 7.
  Flat spectrum |X_k| = sqrt(7) is the standard Gauss-sum magnitude for a
  quadratic phase with invertible leading coefficient (4 != 0 mod 7).

Interim glyph-integer rule respected: no pool integer is altered; the rung
functions are read off the canonical tables.
"""

import itertools
import math

import numpy as np

R = 7
LN3 = math.log(3.0)

# ---------------------------------------------------------------- rung data

j_idx = np.arange(R)
d = j_idx / 2.0

f_A = d * (2 * d + 1)                       # [0, 1, 3, 6, 10, 15, 21]
f_Ap = 4 * d + 1                            # [1, 3, 5, 7, 9, 11, 13]
f_E = np.array([1.0, 0.0, 0.0, 13.0 / 12.0, 0.0, 56.0 / 39.0, 21.0])

alpha = 1.0 / 137.035999177
m_mu_over_m_e = 206.7682830
v_over_lambda_qcd = 1170.2
# alpha_G = G m_e^2 / (hbar c), CODATA-grade inputs
G_N = 6.67430e-11
m_e = 9.1093837015e-31
hbar = 1.054571817e-34
c_light = 2.99792458e8
alpha_G = G_N * m_e**2 / (hbar * c_light)
f_ln = np.array([
    math.log(1.0 / alpha),        # 0D    alpha
    0.0,                          # 0.5D  c = 1
    0.0,                          # 1D    hbar = 1
    math.log(m_mu_over_m_e),      # 1.5D  mass ratio
    math.log(math.pi),            # 2D    pi
    math.log(v_over_lambda_qcd),  # 2.5D  v / Lambda_QCD
    math.log(1.0 / alpha_G),      # 3D    gravity
])

FUNCS = [
    ("A(d) = d(2d+1)   [TYPE A, traversal]", f_A),
    ("A'(d) = 4d+1     [TYPE B, splitting]", f_Ap),
    ("E_alpha ladder   [alpha-step exponents]", f_E),
    ("ln ladder        [log magnitudes]", f_ln),
]

# ------------------------------------------------------------ spectral tools

def pair_stats(f):
    """Non-DC power grouped into conjugate pairs (1,6), (2,5), (3,4).

    Returns (pair power fractions p1..p3, max fraction, entropy over pairs).
    """
    F = np.fft.fft(f)
    pw = np.abs(F) ** 2
    pairs = np.array([pw[1] + pw[6], pw[2] + pw[5], pw[3] + pw[4]])
    tot = pairs.sum()
    if tot == 0:
        return np.full(3, 1.0 / 3), 1.0 / 3, LN3
    p = pairs / tot
    ent = -np.sum(np.where(p > 0, p * np.log(p), 0.0))
    return p, p.max(), ent


def exact_permutation_null(f):
    """Exact null over all 7! orderings of the same seven values.

    Returns p-values for (concentration >= observed) and (entropy <= observed),
    i.e. the fraction of orderings at least as concentrated as the actual
    rung ordering. Spectrum-magnitude symmetries (7 rotations x 2 reflections
    = 14 orderings per class) are included; the p-value floor is 14/5040.
    """
    _, c_obs, h_obs = pair_stats(f)
    n_c = n_h = 0
    vals = tuple(f)
    for perm in itertools.permutations(vals):
        _, c, h = pair_stats(np.array(perm))
        if c >= c_obs - 1e-12:
            n_c += 1
        if h <= h_obs + 1e-12:
            n_h += 1
    total = math.factorial(R)
    return n_c / total, n_h / total


# ----------------------------------------------------------------- E1: value

print("=" * 72)
print("E1  VALUE-LEVEL DFT ON Z7 (conjugate-pair power, exact permutation null)")
print("=" * 72)
print(f"    pair bins: k=(1,6), (2,5), (3,4); flat spectrum = 1/3 each; "
      f"max entropy = ln 3 = {LN3:.4f}")
for name, f in FUNCS:
    F = np.fft.fft(f)
    p, c_obs, h_obs = pair_stats(f)
    p_c, p_h = exact_permutation_null(f)
    print(f"\n  {name}")
    print(f"    values          : {np.round(f, 4)}")
    print(f"    |F_k| (k=0..6)  : {np.round(np.abs(F), 3)}")
    print(f"    pair fractions  : (1,6)={p[0]:.4f}  (2,5)={p[1]:.4f}  "
          f"(3,4)={p[2]:.4f}")
    print(f"    max pair conc.  : {c_obs:.4f}   entropy: {h_obs:.4f} "
          f"(of {LN3:.4f})")
    print(f"    exact null      : P(conc >= obs) = {p_c:.4f}   "
          f"P(entropy <= obs) = {p_h:.4f}   (floor 14/5040 = {14/5040:.4f})")

# ------------------------------------------------------------- E2: character

print()
print("=" * 72)
print("E2  CHARACTER-LEVEL DFT: x_j = exp(2*pi*i*f_j/7)  (integer sequences)")
print("=" * 72)

for name, f in [("A (traversal, quadratic phase)", f_A),
                ("A' (splitting, linear phase)", f_Ap)]:
    x = np.exp(2j * np.pi * f / R)
    X = np.fft.fft(x)
    mags = np.abs(X)
    ac = np.array([np.abs(np.vdot(x, np.roll(x, -s))) for s in range(R)])
    print(f"\n  {name}")
    print(f"    f mod 7         : {np.mod(f.astype(int), R)}")
    print(f"    |X_k| (k=0..6)  : {np.round(mags, 6)}")
    print(f"    |autocorr(s)|   : {np.round(ac, 6)}   (s = 0..6)")

# exact assertions for the analytic claims
x_A = np.exp(2j * np.pi * f_A / R)
X_A = np.abs(np.fft.fft(x_A))
assert np.allclose(X_A, math.sqrt(R), atol=1e-9), "A: spectrum not flat"
ac_A = [abs(np.vdot(x_A, np.roll(x_A, -s))) for s in range(1, R)]
assert np.allclose(ac_A, 0.0, atol=1e-9), "A: autocorrelation not zero"

x_Ap = np.exp(2j * np.pi * f_Ap / R)
X_Ap = np.abs(np.fft.fft(x_Ap))
assert np.isclose(X_Ap[2], R, atol=1e-9), "A': tone not at k=2"
assert np.isclose(np.sort(X_Ap)[-2], 0.0, atol=1e-9), "A': not a pure tone"
ac_Ap = [abs(np.vdot(x_Ap, np.roll(x_Ap, -s))) for s in range(R)]
assert np.allclose(ac_Ap, R, atol=1e-9), "A': autocorrelation not full"

print("\n  CONFIRMED (1e-9): A-character is CAZAC (Zadoff-Chu root -1): "
      "|X_k| = sqrt(7) for all k,")
print("  zero cyclic autocorrelation at every nontrivial shift. "
      "A'-character is a pure tone at k = 2:")
print("  all energy in one line, full-magnitude autocorrelation at every "
      "shift. A' = dA/dd links them.")

# ----------------------------------------------------------------- E3: mod R

print()
print("=" * 72)
print("E3  MOD-R STRUCTURE OF THE INTEGER RUNG FUNCTIONS")
print("=" * 72)

A_mod = np.mod(f_A.astype(int), R)
Ap_mod = np.mod(f_Ap.astype(int), R)
palindrome = bool((A_mod == A_mod[::-1]).all())
bijection = len(set(Ap_mod.tolist())) == R
print(f"\n  A  mod 7 = {A_mod}   palindrome about j <-> 6-j: {palindrome}   "
      f"sum = {A_mod.sum()} = 2R")
print(f"  A' mod 7 = {Ap_mod}   bijection on Z7 (every residue once per "
      f"octave): {bijection}")
assert palindrome and A_mod.sum() == 2 * R and bijection

print()
print("=" * 72)
print("SUMMARY")
print("=" * 72)
print("""
  Value level: no significant concentration beyond monotone smoothness
  (see printed p-values). Character level, EXACT: the traversal function A
  is maximally FLAT (a Zadoff-Chu chirp on Z7; zero autocorrelation at all
  nontrivial octave-relative shifts) and the splitting function A' is
  maximally CONCENTRATED (a pure tone at k = 2). TYPE A / TYPE B is the
  chirp/tone duality; differentiation maps one to the other. Only the
  trivial shift returns A's phase pattern, rhyming with (not proving) the
  single-period lemma. Mod R: A is palindromic with sum 2R; A' visits
  every residue class exactly once per octave.
""")
