"""Which steps from 'one energy, self-limiting, nested' to a wave operator can fail? Stdlib only.

Created: 2026-11-04
Last updated: 2026-11-04
Version: 1.0
History: 2026-11-04 v1.0: initial. Record: plans/wave_operator_unfolding_2026_11_04.md
"""
import math, random

# --- Tridiagonal eigenvalues by Sturm bisection (Dirichlet chain) ---
def count_below(d, e2, x):
    c, q = 0, 1.0
    for i in range(len(d)):
        q = d[i] - x - (e2[i - 1] / q if i else 0.0)
        if q == 0:
            q = 1e-300
        if q < 0:
            c += 1
    return c

def eig(d, e2, k, hi):
    lo_, hi_ = 0.0, hi
    for _ in range(70):
        m = (lo_ + hi_) / 2
        if count_below(d, e2, m) >= k:
            hi_ = m
        else:
            lo_ = m
    return (lo_ + hi_) / 2

def chain(w):
    n = len(w) - 1
    d = [w[i] + w[i + 1] for i in range(n)]
    e2 = [w[i + 1] ** 2 for i in range(n - 1)]
    return d, e2

# STEP: nesting. Random local bonds at the small scale. Does the coarse scale forget them?
print("1. Random local bonds: lowest modes against a plain wave with one effective stiffness")
rng = random.Random(11)
N = 4000
for name, draw in [("uniform 0.5-1.5", lambda: rng.uniform(.5, 1.5)), ("lognormal, wide", lambda: math.exp(rng.gauss(0, 1.0)))]:
    w = [draw() for _ in range(N + 1)]
    harm = (N + 1) / sum(1 / x for x in w)
    d, e2 = chain(w)
    top = 4 * max(w) + 1
    for k in (1, 2, 5, 20, 100, 400):
        lam = eig(d, e2, k, top)
        wave = harm * (k * math.pi / (N + 1)) ** 2
        print(f"   {name:18} mode {k:4}: exact/wave = {lam / wave:.4f}")
    print(f"   arithmetic mean/harmonic mean of bonds = {sum(w) / len(w) / harm:.3f}")

# STEP: locality. Long-range coupling should change the operator.
print("2. Dispersion exponent p in omega^2 ~ k^p, coupling J(r) = r^-(1+a)")
def disp(k, a, R=200000):
    return sum(r ** (-(1 + a)) * (2 - 2 * math.cos(k * r)) for r in range(1, R))
for a in (0.5, 1.0, 1.5, 3.0, 5.0):
    k1, k2 = 0.004, 0.008
    print(f"   a={a}: p = {math.log(disp(k2, a) / disp(k1, a)) / math.log(k2 / k1):.3f}")
print("   exponential range 3:", end=" ")
ex = lambda k: sum(math.exp(-r / 3) * (2 - 2 * math.cos(k * r)) for r in range(1, 400))
print(f"p = {math.log(ex(.008) / ex(.004)) / math.log(2):.3f}")

# STEP: relational. Add one absolute (on-site) term: gap and speed.
print("3. Closure: wave in a transverse box of width L gives omega^2 = k^2 + (pi/L)^2")
L = 1.0
m = math.pi / L
for k in (0.0, 0.5, 1.0, 5.0, 50.0):
    om = math.sqrt(k * k + m * m)
    vg = k / om
    print(f"   k={k:5}: omega={om:9.4f} group speed={vg:.4f}  m + k^2/2m={m + k * k / (2 * m):9.4f}")

# STEP: generator. Change with no growth or decay. A random real matrix, split into symmetric and skew parts.
print("4. Generator split: norm drift of each part over t=20, 6 dimensions")
n = 6
A = [[rng.gauss(0, 1) for _ in range(n)] for _ in range(n)]
S = [[(A[i][j] + A[j][i]) / 2 for j in range(n)] for i in range(n)]
K = [[(A[i][j] - A[j][i]) / 2 for j in range(n)] for i in range(n)]
def run(G, t=20.0, dt=1e-3):
    z = [rng.gauss(0, 1) for _ in range(n)]
    n0 = math.sqrt(sum(x * x for x in z))
    f = lambda v: [sum(G[i][j] * v[j] for j in range(n)) for i in range(n)]
    for _ in range(int(t / dt)):
        k1 = f(z)
        k2 = f([z[i] + dt / 2 * k1[i] for i in range(n)])
        k3 = f([z[i] + dt / 2 * k2[i] for i in range(n)])
        k4 = f([z[i] + dt * k3[i] for i in range(n)])
        z = [z[i] + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(n)]
    return math.sqrt(sum(x * x for x in z)) / n0
print(f"   symmetric part: final/initial norm {run(S):.4g}")
print(f"   skew part:      final/initial norm {run(K):.10f}")

# STEP: is the second-order form forced? Spreading of a local pulse: wave vs first-order complex form on a lattice.
print("5. Earliest arrival on a lattice: size at distance r after time 10, per-site unit coupling")
def bessel(n_, x, m=4000):
    # J_n(x) by integral
    h = math.pi / m
    return sum(math.cos(n_ * (i + .5) * h - x * math.sin((i + .5) * h)) for i in range(m)) * h / math.pi
for r in (5, 10, 15, 20, 30, 40):
    print(f"   r={r:3}: first-order |psi| = {abs(bessel(r, 2 * 10)):.3e}")
print("   continuum first-order kernel magnitude is uniform in r at any t>0: 1/sqrt(4 pi t), no light cone")
print("   continuum wave: exactly zero beyond r = c t")
