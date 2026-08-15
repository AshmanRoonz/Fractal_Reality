"""
prime_boundary_field_v1.py

Created: 2026-08-15
Last updated: 2026-08-15
Version: 1.0
History:
- 2026-08-15 v1.0: initial. The prime boundary field and the Li energy bridge.

The experiment proposed in plans/zeta_circumpunct_coordinates_2026_08_15.md
Addendum 4: build the boundary field on the RH circle from the prime signal,
decompose it into circle harmonics, and pressure-test the claim that the n-th
Li coefficient is the energy of the n-th mode.

Coordinates: w = z = (s-1)/s, s = 1/(1-z). The critical line is |z| = 1, the
pole s = 1 is z = 0, infinity is z = 1. Li/Keiper: lambda_n = n [z^n] log
xi(1/(1-z)), and RH iff lambda_n >= 0 for all n >= 1.

Five sections:

1. THE BOUNDARY FIELD FROM XI. lambda_n for n = 1..40 by FFT extraction of
   the Taylor coefficients of log Xi(z) = log xi(1/(1-z)) on a circle
   |z| = r < 1. Unconditional, no zeros used. Validates against the three
   session-verified anchors lambda_1..lambda_3 and checks positivity and the
   Lagarias asymptotic lambda_n ~ (n/2)(log n - log(2 pi) + gamma - 1).

2. THE PRIME MOMENTS. The arithmetic field A(z) = log[(s-1) zeta(s)] obeys
   d/du log(u zeta(1+u)) = sum_j eta_j u^j (u = s-1), where the eta_j are the
   regularized prime moments: -zeta'/zeta(s) = 1/(s-1) - sum_j eta_j (s-1)^j,
   each eta_j an (unconditional, regularized) limit of von Mangoldt sums.
   Computed by FFT extraction of log(u zeta(1+u)); eta_0 = gamma is the check.

3. THE BRIDGE IS A BINOMIAL TRANSFORM. Because u = z/(1-z), coefficient
   composition gives EXACTLY: prime part of lambda_n = sum_j eta_j C(n, j+1).
   The conformal warping from prime frequencies to circle harmonics is, at
   coefficient level, the binomial transform of the regularized prime moments.
   Verified against a direct FFT of A(z), and the total
   lambda_n = lambda_n^prime + lambda_n^arch is verified against section 1.

4. THE PRIMES THEMSELVES. eta_0, eta_1, eta_2 recomputed from a sieve of the
   actual primes (von Mangoldt sums to X = 10^7 with the PNT regularization
   E(x) = psi(x) - x), demonstrating numerically that the prime signal alone
   assembles the Li data. Accuracy limited by truncation; reported honestly.

5. THE ENERGY DECOMPOSITION (the pressure test). Exact algebra, per zero:
       1 - Re(w^n) = (1/2)|1 - w^n|^2 - (1/2)(|w^n|^2 - 1).
   Summed over the zero multiset (symmetric ordering):
       lambda_n = E_n - D_n
   where E_n = (1/2) sum |1 - w^n|^2 >= 0 (boundary mode energy: the L2 norm
   of the function 1 - e_n against the zero measure) and
   D_n = (1/2) sum (|w^n|^2 - 1), which after pairing each zero with its
   functional-equation partner (w with 1/w) is a sum of AM-GM gaps
   (x + 1/x - 2)/2 >= 0, zero iff |w| = 1. So:
       - E_n >= 0 and D_n >= 0 always (unconditional);
       - RH iff D_n = 0 for all n iff lambda_n = E_n exactly;
       - Li positivity is the statement E_n >= D_n.
   The prime side (sections 2-4) computes only the package E_n - D_n; the
   split into energy and defect requires knowing where the zeros are. That
   localizes the RH gap: the transported-energy identity lambda_n = E_n is
   exactly equivalent to RH, as the pressure test predicted (consistent with
   the reported Suzuki-type norm equivalences).

Run: python3 prime_boundary_field_v1.py
"""

import mpmath as mp

try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False

N_LAMBDA = 40      # compute lambda_1..lambda_40
FFT_M = 128        # points per extraction circle
R_XI = mp.mpf('0.5')    # extraction radius for log Xi (singularity at z=1)
R_ETA = mp.mpf('1.0')   # extraction radius for log(u zeta(1+u)) (radius 3)
SIEVE_X = 10**7    # von Mangoldt truncation for section 4
N_ZEROS = 300      # zeros for section 5 checks


def xi(s):
    return mp.mpf('0.5') * s * (s - 1) * mp.pi ** (-s / 2) * mp.gamma(s / 2) * mp.zeta(s)


def unwrapped_log_ring(G, r, M):
    """Values of log G on the circle |z| = r at M roots of unity, with the
    imaginary part unwrapped to a continuous branch. Returns (logs, winding):
    winding is the net change of arg/2pi around the loop (0 means log G is
    single-valued on the circle, i.e. no zeros of G enclosed... beyond those
    at 0 which G must not have)."""
    logs = []
    prev = None
    for m in range(M + 1):  # extra point to close the loop and read winding
        z = r * mp.e ** (2j * mp.pi * m / M)
        L = mp.log(G(z))
        if prev is not None:
            k = mp.floor(((L - prev).imag / (2 * mp.pi)) + mp.mpf('0.5'))
            L -= 2j * mp.pi * k
        if m < M:
            logs.append(L)
        prev = L
    winding = (prev - logs[0]).imag / (2 * mp.pi)
    return logs, winding


def coeffs_from_ring(logs, r, M, kmax):
    """Taylor coefficients c_0..c_kmax from ring samples of the (unwrapped)
    logarithm, by discrete Fourier sum."""
    out = []
    for k in range(kmax + 1):
        acc = mp.mpc(0)
        for m in range(M):
            acc += logs[m] * mp.e ** (-2j * mp.pi * k * m / M)
        out.append(acc / (M * r ** k))
    return out


def main():
    mp.mp.dps = 32
    print("=" * 72)
    print("SECTION 1: the boundary field from xi (no zeros used)")
    print("=" * 72)

    logXi, wind = unwrapped_log_ring(lambda z: xi(1 / (1 - z)), R_XI, FFT_M)
    print(f"branch winding of log Xi on |z|={float(R_XI)}: {mp.nstr(wind, 3)} (want 0)")
    cs = coeffs_from_ring(logXi, R_XI, FFT_M, N_LAMBDA)
    lam = [None] + [n * cs[n].real for n in range(1, N_LAMBDA + 1)]
    imag_leak = max(abs(cs[n].imag) for n in range(1, N_LAMBDA + 1))
    print(f"c_0 = {mp.nstr(cs[0].real, 12)}  (want log(1/2) = {mp.nstr(mp.log(0.5), 12)})")
    print(f"max |Im c_n| (should be ~0): {mp.nstr(imag_leak, 3)}")
    anchors = [mp.mpf('0.0230957089661'), mp.mpf('0.0923457352280'), mp.mpf('0.2076389205540')]
    for n in (1, 2, 3):
        print(f"lambda_{n} = {mp.nstr(lam[n], 12)}   anchor {mp.nstr(anchors[n-1], 12)}"
              f"   dev {mp.nstr(abs(lam[n] - anchors[n-1]), 3)}")
    neg = [n for n in range(1, N_LAMBDA + 1) if lam[n] <= 0]
    print(f"positivity for n = 1..{N_LAMBDA}: {'ALL POSITIVE' if not neg else 'FAILURES: ' + str(neg)}")
    print("Lagarias asymptotic check lambda_n vs (n/2)(log n - log 2pi + gamma - 1):")
    for n in (10, 20, 40):
        asym = n / 2 * (mp.log(n) - mp.log(2 * mp.pi) + mp.euler - 1)
        print(f"  n={n}: lambda={mp.nstr(lam[n], 8)}, asymptotic={mp.nstr(asym, 8)}, "
              f"ratio={mp.nstr(lam[n] / asym, 6)}")

    print()
    print("=" * 72)
    print("SECTION 2: the prime moments eta_j (regularized von Mangoldt data)")
    print("=" * 72)

    # g(u) = log(u zeta(1+u)) is analytic in |u| < 3 with g(0) = 0 and
    # g'(u) = sum_j eta_j u^j, so eta_j = (j+1) [u^{j+1}] g.
    logg, windg = unwrapped_log_ring(lambda u: u * mp.zeta(1 + u) if u != 0 else mp.mpf(1),
                                     R_ETA, FFT_M)
    print(f"branch winding of log(u zeta(1+u)) on |u|={float(R_ETA)}: {mp.nstr(windg, 3)} (want 0)")
    ds = coeffs_from_ring(logg, R_ETA, FFT_M, N_LAMBDA + 1)
    eta = [( (j + 1) * ds[j + 1]).real for j in range(N_LAMBDA)]
    print(f"eta_0 = {mp.nstr(eta[0], 15)}   (gamma = {mp.nstr(+mp.euler, 15)}; "
          f"dev {mp.nstr(abs(eta[0] - mp.euler), 3)})")
    for j in (1, 2, 3, 4):
        print(f"eta_{j} = {mp.nstr(eta[j], 15)}")
    print(f"decay check: eta_10 = {mp.nstr(eta[10], 6)}, eta_20 = {mp.nstr(eta[20], 6)} "
          f"(radius-3 decay ~ 3^-j)")

    print()
    print("=" * 72)
    print("SECTION 3: the bridge is a binomial transform")
    print("=" * 72)

    # Prime part of lambda_n: exact coefficient composition through u = z/(1-z):
    #   lambda_n^prime = sum_{j=0}^{n-1} eta_j C(n, j+1).
    lam_prime = [None] + [sum(eta[j] * mp.binomial(n, j + 1) for j in range(n))
                          for n in range(1, N_LAMBDA + 1)]
    # Cross-check with a direct FFT of A(z) = log[(s-1) zeta(s)], s = 1/(1-z):
    logA, windA = unwrapped_log_ring(
        lambda z: (z / (1 - z)) * mp.zeta(1 / (1 - z)) if z != 0 else mp.mpf(1),
        R_XI, FFT_M)
    As = coeffs_from_ring(logA, R_XI, FFT_M, N_LAMBDA)
    lam_prime_direct = [None] + [n * As[n].real for n in range(1, N_LAMBDA + 1)]
    dev_bridge = max(abs(lam_prime[n] - lam_prime_direct[n]) for n in range(1, N_LAMBDA + 1))
    print(f"binomial-transform vs direct-FFT prime part, max |dev| over n<=40: "
          f"{mp.nstr(dev_bridge, 3)}")
    # Archimedean part and total:
    logB, windB = unwrapped_log_ring(
        lambda z: (lambda s: mp.mpf('0.5') * s * mp.pi ** (-s / 2) * mp.gamma(s / 2))(1 / (1 - z)),
        R_XI, FFT_M)
    Bs = coeffs_from_ring(logB, R_XI, FFT_M, N_LAMBDA)
    lam_arch = [None] + [n * Bs[n].real for n in range(1, N_LAMBDA + 1)]
    dev_total = max(abs(lam_prime[n] + lam_arch[n] - lam[n]) for n in range(1, N_LAMBDA + 1))
    print(f"lambda_n^prime + lambda_n^arch vs lambda_n, max |dev| over n<=40: "
          f"{mp.nstr(dev_total, 3)}")
    print("decomposition at low n (prime part, arch part, total):")
    for n in (1, 2, 3, 5, 10):
        print(f"  n={n}: prime={mp.nstr(lam_prime[n], 8)}, arch={mp.nstr(lam_arch[n], 8)}, "
              f"total={mp.nstr(lam_prime[n] + lam_arch[n], 8)}")
    # Sign structure: is the prime part manifestly positive? (It is not.)
    signs = ''.join('+' if lam_prime[n] > 0 else '-' for n in range(1, N_LAMBDA + 1))
    print(f"sign of prime part, n = 1..{N_LAMBDA}: {signs}")

    print()
    print("=" * 72)
    print(f"SECTION 4: eta from the primes themselves (sieve to X = {SIEVE_X:.0e})")
    print("=" * 72)

    if HAVE_NUMPY:
        X = SIEVE_X
        # sieve primes to X
        is_p = np.ones(X + 1, dtype=bool)
        is_p[:2] = False
        for p in range(2, int(X ** 0.5) + 1):
            if is_p[p]:
                is_p[p * p::p] = False
        primes = np.nonzero(is_p)[0]
        # von Mangoldt
        Lam = np.zeros(X + 1)
        Lam[primes] = np.log(primes)
        for p in primes[primes <= int(X ** 0.5)]:
            pk = p * p
            while pk <= X:
                Lam[pk] = np.log(p)
                pk *= p
        psi = np.cumsum(Lam)           # psi(m) for integer m
        m = np.arange(1, X)            # intervals [m, m+1)
        xm = m + 0.5
        E = psi[m] - xm                # psi(x) - x at midpoint (psi constant on interval)
        lx = np.log(xm)
        base = E / xm ** 2
        c = [float(np.sum(base * lx ** k)) for k in range(3)]
        eta_sieve = [-1.0 - c[0], c[1] - c[0], c[1] - c[2] / 2.0]
        for j in range(3):
            exact = float(eta[j])
            print(f"eta_{j}: sieve={eta_sieve[j]:+.6f}, exact={exact:+.6f}, "
                  f"abs err={abs(eta_sieve[j] - exact):.2e}")
        lam1_sieve = eta_sieve[0] * 1.0  # C(1,1) = 1
        lam1_from_primes = lam1_sieve + float(lam_arch[1])
        print(f"lambda_1 assembled from sieved primes + archimedean: "
              f"{lam1_from_primes:+.6f} (exact {mp.nstr(lam[1], 6)})")
        n2 = 2 * eta_sieve[0] + 1 * eta_sieve[1]
        print(f"lambda_2 assembled from sieved primes + archimedean: "
              f"{n2 + float(lam_arch[2]):+.6f} (exact {mp.nstr(lam[2], 6)})")
    else:
        print("numpy unavailable; section skipped")

    print()
    print("=" * 72)
    print("SECTION 5: the energy decomposition lambda_n = E_n - D_n (pressure test)")
    print("=" * 72)

    mp.mp.dps = 20
    # per-zero identity check at an arbitrary complex point
    Wt = mp.mpc('1.03', '0.4') ** 7
    lhs = 1 - Wt.real
    rhs = mp.mpf('0.5') * abs(1 - Wt) ** 2 - mp.mpf('0.5') * (abs(Wt) ** 2 - 1)
    print(f"per-zero identity 1 - Re W = |1-W|^2/2 - (|W|^2-1)/2: dev = "
          f"{mp.nstr(abs(lhs - rhs), 3)}")

    # off-line quartet: E and D separately, and the AM-GM gap form of D
    rho = mp.mpc('0.6', '50')
    quartet = [rho, mp.conj(rho), 1 - rho, 1 - mp.conj(rho)]
    ws = [(r - 1) / r for r in quartet]
    for n in (100, 119699):
        En = sum(mp.mpf('0.5') * abs(1 - w ** n) ** 2 for w in ws)
        Dn = sum(mp.mpf('0.5') * (abs(w ** n) ** 2 - 1) for w in ws)
        direct = sum((1 - w ** n).real for w in ws)
        # AM-GM gap form: pair w with 1/w
        x1 = abs(ws[0] ** n) ** 2
        x2 = abs(ws[1] ** n) ** 2
        Dn_amgm = (x1 + 1 / x1 - 2) / 2 + (x2 + 1 / x2 - 2) / 2
        print(f"off-line quartet, n={n}: E={mp.nstr(En, 6)}, D={mp.nstr(Dn, 6)}, "
              f"E-D={mp.nstr(En - Dn, 6)}, direct={mp.nstr(direct, 6)}, "
              f"D_amgm dev={mp.nstr(abs(Dn - Dn_amgm), 3)}")
        print(f"    E >= 0: {En >= 0};  D >= 0: {Dn >= 0};  "
              f"lambda-contribution negative: {En - Dn < 0}")

    # on the real zeros (RH data): D = 0 and E_n reproduces lambda_n
    print(f"computing first {N_ZEROS} zeros for the on-circle energy check...")
    zeros = [mp.zetazero(k) for k in range(1, N_ZEROS + 1)]
    T = zeros[-1].imag
    for n in (1, 2, 3):
        En = mp.mpf(0)
        Dn = mp.mpf(0)
        for r in zeros:
            w = (r - 1) / r
            # zero, its conjugate, and their functional-equation partners:
            # on-line data makes the four collapse to the conjugate pair
            En += 2 * mp.mpf('0.5') * abs(1 - w ** n) ** 2
            Dn += 2 * mp.mpf('0.5') * (abs(w ** n) ** 2 - 1)
        tail = n * (mp.log(T / (2 * mp.pi)) + 1) / (2 * mp.pi * T)
        print(f"  n={n}: E_n(partial)+tail = {mp.nstr(En + tail, 8)}, "
              f"D_n = {mp.nstr(Dn, 3)}, lambda_{n} = {mp.nstr(lam[n], 8)}")

    print()
    print("VERDICT: lambda_n = E_n - D_n exactly and unconditionally; E_n and D_n")
    print("are separately nonnegative; RH iff D_n = 0 for all n iff lambda_n is")
    print("the boundary mode energy E_n. The prime side (sections 2-4) assembles")
    print("only the package E_n - D_n; the energy/defect split requires the zero")
    print("positions. The transported-energy identity is equivalent to RH, as")
    print("pre-registered in Addendum 4. No unconditional positivity obtained.")


if __name__ == '__main__':
    main()
