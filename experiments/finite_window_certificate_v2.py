"""
finite_window_certificate_v2.py

Numerical certificate companion for the finite-window arithmetic-metric theorem.

Uses the exact packet parameters from:
  weil_scale_operator_v1.py
  prime_side_spectroscopy_v1.py

This script certifies the *mathematical truncated arithmetic form* relative to
the ideal eight-positive-zero target form, up to:
  - an unconditional prime-power tail majorant using Lambda(n) <= log n,
  - an unconditional off-window zero tail majorant using Bellotti-Wong's
    explicit N(T) bound and |beta-1/2| <= 1/2,
  - exact finite-dimensional conditioning.

It does NOT certify floating-point roundoff or the trapezoid implementation
with interval arithmetic. Those are reported separately as implementation
checks.

Bellotti-Wong v2:
|N(T) - T/(2*pi) log(T/(2*pi*e))|
 <= 0.10076 log T + 0.24460 log log T + 8.08344, T >= e.

The use of TAIL_START = 48 assumes the standard verified enumeration that the
eight listed positive zeros are all the positive nontrivial zeros below 48.
"""

import math
import numpy as np
import mpmath as mp

mp.mp.dps = 60

SIGMA = mp.mpf("1.5")
NU_MIN = mp.mpf("10")
NU_MAX = mp.mpf("45")
NU_STEP = mp.mpf("0.5")
N_PACKETS = 71
PRIME_CUTOFF = mp.mpf("2000000")
TAIL_START = mp.mpf("48")

TARGET = np.array([
    14.134725141734693,
    21.022039638771554,
    25.010857580145688,
    30.424876125859513,
    32.935061587739189,
    37.586178158825671,
    40.918719012147495,
    43.327073280914999,
], dtype=float)

# ----------------------------------------------------------------------
# Exact finite-support conditioning
# ----------------------------------------------------------------------

s = float(SIGMA)
nu = np.arange(float(NU_MIN), float(NU_MAX) + 1e-12, float(NU_STEP))
V = s * np.sqrt(2*np.pi) * np.exp(-0.5*s*s*(TARGET[None, :] - nu[:, None])**2)
sv = np.linalg.svd(V, compute_uv=False)
a = float(sv[-1]**2)
b = float(sv[0]**2)
M = float(np.max(np.abs(TARGET)))
min_gap = float(np.min(np.diff(TARGET)))

# ----------------------------------------------------------------------
# Prime tail
# ----------------------------------------------------------------------
# For the uploaded convention,
# K(log n) = exp(-(log n)^2/(4 sigma^2)).
#
# B0 tail entry <= 2 sigma sqrt(pi) *
#   sum_{n>P} log(n)/sqrt(n) K(log n)
#
# B1 tail entry <= sqrt(pi) *
#   [2 mu_max sigma S1 + sigma^{-1} S2]
#
# where we used Lambda(n) <= log n and enlarged from prime powers to all
# integers. Since the summands are decreasing at P=2e6,
# sum_{n>P} f(n) <= integral_P^infty f(x) dx.

P = PRIME_CUTOFF

def I_log_power(k):
    f = lambda x: (mp.log(x)**k) / mp.sqrt(x) * mp.e**(
        -(mp.log(x)**2)/(4*SIGMA**2)
    )
    return mp.quad(f, [P, mp.inf])

I1 = I_log_power(1)
I2 = I_log_power(2)

prime_entry_0 = 2*SIGMA*mp.sqrt(mp.pi)*I1
prime_entry_1 = mp.sqrt(mp.pi) * (
    2*NU_MAX*SIGMA*I1 + I2/SIGMA
)

eps0_prime = mp.mpf(N_PACKETS) * prime_entry_0
eps1_prime = mp.mpf(N_PACKETS) * prime_entry_1

# ----------------------------------------------------------------------
# Zero leakage
# ----------------------------------------------------------------------
# For rho = beta+i gamma and z=(rho-1/2)/i,
# |Im z| = |beta-1/2| <= 1/2.
#
# Hence for the spectral Gaussian:
# |exp[-sigma^2(z-mu)^2]|
# <= exp(sigma^2/4) exp[-sigma^2(gamma-mu)^2].
#
# Bellotti-Wong upper zero-counting function:
# U(T) = F(T)+R(T).

def F(T):
    return T/(2*mp.pi)*mp.log(T/(2*mp.pi*mp.e))

def R(T):
    return (
        mp.mpf("0.10076")*mp.log(T)
        + mp.mpf("0.24460")*mp.log(mp.log(T))
        + mp.mpf("8.08344")
    )

def U(T):
    return mp.max_fixed(mp.mpf("0"), F(T)+R(T))

# mpmath lacks a scalar max helper with this exact name on some versions.
def U(T):
    x = F(T)+R(T)
    return x if x > 0 else mp.mpf("0")

mu = NU_MAX
offaxis = mp.e**(SIGMA**2/4)

def phi(t):
    return mp.e**(-SIGMA**2*(t-mu)**2)

# -phi'(t)
def minus_phi_prime(t):
    return 2*SIGMA**2*(t-mu)*phi(t)

# q(t)=(t+1/2)phi(t), bounding |z| phi(t)
def minus_q_prime(t):
    return phi(t) * (
        2*SIGMA**2*(t+mp.mpf("0.5"))*(t-mu) - 1
    )

zero_scalar_0 = mp.quad(lambda t: U(t)*minus_phi_prime(t),
                       [TAIL_START, mp.inf])
zero_scalar_1 = mp.quad(lambda t: U(t)*minus_q_prime(t),
                       [TAIL_START, mp.inf])

C0 = 2*mp.pi*SIGMA**2
eps0_zero = N_PACKETS*C0*offaxis*zero_scalar_0
eps1_zero = N_PACKETS*C0*offaxis*zero_scalar_1

# Negative-ordinate partners are vastly smaller because all packet centers
# are positive. They are omitted from the displayed total; a Bellotti-Wong
# integral starting at 14 and mu=-10 is below 10^-550 after matrix factors,
# so adding 10^-500 is an absurdly safe placeholder.
eps0_negative = mp.mpf("1e-500")
eps1_negative = mp.mpf("1e-500")

# Pole terms omitted by weil_scale_operator_v1.py.
# h0(i/2)+h0(-i/2) entry magnitude <=
# 4 pi sigma^2 exp[-sigma^2(mu^2-1/4)], minimized at mu=10.
pole_entry_0 = (
    4*mp.pi*SIGMA**2
    * mp.e**(-SIGMA**2*(NU_MIN**2-mp.mpf("0.25")))
)
# For h1=t h0, the pair magnitude bound is half of h0's pair bound.
pole_entry_1 = pole_entry_0/2
eps0_pole = N_PACKETS*pole_entry_0
eps1_pole = N_PACKETS*pole_entry_1

eps0 = eps0_prime + eps0_zero + eps0_negative + eps0_pole
eps1 = eps1_prime + eps1_zero + eps1_negative + eps1_pole

# ----------------------------------------------------------------------
# Moving signal subspace
# ----------------------------------------------------------------------
# The top-8 eigenspace of the perturbed B0 moves. Davis-Kahan gives the
# conservative angle parameter eta = eps0/(a-eps0).
#
# A useful exact observation: restricting the *ideal pair*
# (V V*, V Gamma V*) to ANY 8-dimensional subspace transverse to ran(V)
# preserves the generalized eigenvalues Gamma, because both matrices undergo
# the same invertible congruence C* (.,.) C.
#
# Thus subspace movement only weakens the denominator through cos^2(theta).

a_mp = mp.mpf(str(a))
M_mp = mp.mpf(str(M))
eta = eps0/(a_mp-eps0)
a_moved = a_mp*(1-eta**2)

delta = (eps1 + M_mp*eps0)/(a_moved-eps0)

print("FINITE-WINDOW CERTIFICATE v2")
print(f"packets                  = {N_PACKETS}")
print(f"sigma                    = {float(SIGMA):.6f}")
print(f"packet band              = [{float(NU_MIN):.1f}, {float(NU_MAX):.1f}]")
print(f"prime cutoff             = {int(PRIME_CUTOFF)}")
print()
print(f"sigma_min(V)             = {sv[-1]:.12f}")
print(f"sigma_max(V)             = {sv[0]:.12f}")
print(f"cond(V)                  = {sv[0]/sv[-1]:.12f}")
print(f"a = lambda_min+(B0*)     = {a:.12f}")
print(f"b = lambda_max(B0*)      = {b:.12f}")
print(f"M = max target ordinate  = {M:.12f}")
print(f"minimum target gap       = {min_gap:.12f}")
print()
print("ANALYTIC ERROR MAJORANTS")
print(f"I1 prime integral        = {mp.nstr(I1, 15)}")
print(f"I2 prime integral        = {mp.nstr(I2, 15)}")
print(f"eps0_prime               = {mp.nstr(eps0_prime, 15)}")
print(f"eps1_prime               = {mp.nstr(eps1_prime, 15)}")
print(f"eps0_zero                = {mp.nstr(eps0_zero, 15)}")
print(f"eps1_zero                = {mp.nstr(eps1_zero, 15)}")
print(f"eps0_pole                = {mp.nstr(eps0_pole, 6)}")
print(f"eps1_pole                = {mp.nstr(eps1_pole, 6)}")
print()
print(f"eps0 total               = {mp.nstr(eps0, 15)}")
print(f"eps1 total               = {mp.nstr(eps1, 15)}")
print(f"subspace sin-theta eta   = {mp.nstr(eta, 15)}")
print(f"effective a after move   = {mp.nstr(a_moved, 15)}")
print()
print(f"CERTIFIED EIGENVALUE RADIUS delta = {mp.nstr(delta, 15)}")
print(f"2 delta                  = {mp.nstr(2*delta, 15)}")
print(f"minimum target gap       = {min_gap:.12f}")
print(f"unique matching certified= {2*float(delta) < min_gap}")
