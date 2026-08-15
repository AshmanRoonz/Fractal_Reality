"""
balance_pole_theorem_v1.py

Created: 2026-08-15
Last updated: 2026-08-15
Version: 1.0
History:
- 2026-08-15 v1.0: initial. Numerical verification of every clause of the
  shell trident and balance pole theorems (plans/balance_pole_theorem_2026_08_15.md).

Coordinates: w = (s-1)/s, s = 1/(1-w). Xi(w) = xi(1/(1-w)).
G(w) = sum_n lambda_n w^n = s(s-1) xi'(s)/xi(s).

Verifies:
V1  lambda_n for n <= 120 by ring FFT (anchors lambda_1..3).
V2  the generating identity G(w) = s(s-1) xi'/xi at two interior points.
V3  clause (a): Mellin weight law x^(1/R - 1) at R = 1 (flat, unitary) and
    R = 1/2 (weight x), both sides in closed agreement.
V4  clause (b): |dt/dtheta| |1-w|^2 = 1 on the critical circle.
V5  clause (c): winding obstruction. Shell contour integral of the
    arithmetic field A(w) w^(-4): sigma = 1.3 gives 0; sigma = 0.8 gives
    lambda_3^prime / 3.
V6  clauses (d): balance pole values. -log 2 Xi(-r), G(-r), G'(-r) as
    r -> 1 against the closed forms -log[-zeta(1/2) Gamma(1/4) / (4 pi^(1/4))],
    0, and -(1/16) xi''(1/2)/xi(1/2); plus series-side check at r = 0.9.
"""

import mpmath as mp


def xi(s):
    return mp.mpf('0.5') * s * (s - 1) * mp.pi ** (-s / 2) * mp.gamma(s / 2) * mp.zeta(s)


def G_direct(w):
    s = 1 / (1 - w)
    return s * (s - 1) * mp.diff(xi, s) / xi(s)


def unwrapped_ring(F, centre, radius, M, offset=mp.mpf('0.5')):
    """F evaluated on the circle centre + radius e^{i phi} at M offset points,
    log taken with a continuously unwrapped branch. Returns (points, logs)."""
    pts, logs, prev = [], [], None
    for k in range(M):
        phi = 2 * mp.pi * (k + offset) / M
        w = centre + radius * mp.e ** (1j * phi)
        L = mp.log(F(w))
        if prev is not None:
            n2pi = mp.floor(((L - prev).imag / (2 * mp.pi)) + mp.mpf('0.5'))
            L -= 2j * mp.pi * n2pi
        pts.append(w)
        logs.append(L)
        prev = L
    return pts, logs


def main():
    # ---------- V1: lambda_n by ring FFT ----------
    mp.mp.dps = 40
    N = 120
    M = 256
    r_ex = mp.mpf('0.6')
    pts, logs = unwrapped_ring(lambda w: 2 * xi(1 / (1 - w)), mp.mpf(0), r_ex, M, offset=0)
    lam = [None] * (N + 1)
    for n in range(1, N + 1):
        acc = mp.mpc(0)
        for k in range(M):
            acc += logs[k] * mp.e ** (-2j * mp.pi * n * k / M)
        lam[n] = (n * acc / (M * r_ex ** n)).real
    anchors = [mp.mpf('0.0230957089661'), mp.mpf('0.0923457352280'), mp.mpf('0.2076389205540')]
    print("V1: lambda anchors:",
          [mp.nstr(abs(lam[n] - anchors[n - 1]), 3) for n in (1, 2, 3)],
          "| lambda_120 =", mp.nstr(lam[120], 8))

    # ---------- V2: generating identity ----------
    mp.mp.dps = 30
    for w0 in (mp.mpc('-0.5', '0'), mp.mpc('0.3', '0.4')):
        series = sum(lam[n] * w0 ** n for n in range(1, N + 1))
        direct = G_direct(w0)
        print(f"V2: G({mp.nstr(w0, 3)}): series={mp.nstr(series, 12)}, "
              f"direct={mp.nstr(direct, 12)}, dev={mp.nstr(abs(series - direct), 3)}")

    # ---------- V3: Mellin weight law ----------
    mp.mp.dps = 15
    # R = 1 (sigma = 1/2): flat weight; f = e^-x
    lhs1 = mp.quad(lambda x: mp.e ** (-2 * x), [0, 40])
    rhs1 = mp.quad(lambda t: abs(mp.gamma(mp.mpc(0.5, t))) ** 2, [-30, -2, 0, 2, 30]) / (2 * mp.pi)
    # R = 1/2 (sigma = 1): weight x^(1/R - 1) = x
    lhs2 = mp.quad(lambda x: x * mp.e ** (-2 * x), [0, 40])
    rhs2 = mp.quad(lambda t: abs(mp.gamma(mp.mpc(1, t))) ** 2, [-30, -2, 0, 2, 30]) / (2 * mp.pi)
    print(f"V3: R=1 (flat): {mp.nstr(lhs1, 10)} = {mp.nstr(rhs1, 10)};  "
          f"R=1/2 (weight x): {mp.nstr(lhs2, 10)} = {mp.nstr(rhs2, 10)}")

    # ---------- V4: pullback measure ----------
    devs = []
    for th in (mp.mpf('0.3'), mp.mpf('1.7'), mp.mpf('3.0')):
        dtdth = abs(mp.diff(lambda x: mp.cot(x / 2) / 2, th))
        w = mp.e ** (1j * th)
        devs.append(abs(dtdth * abs(1 - w) ** 2 - 1))
    print(f"V4: |dt/dtheta| |1-w|^2 - 1 at three angles: max {mp.nstr(max(devs), 3)}")

    # ---------- V5: winding obstruction on shells ----------
    mp.mp.dps = 15
    n_mode = 3
    lam3_prime_target = mp.mpf('0.4068990')  # (3 eta_0 + 3 eta_1 + eta_2)/3, prior session
    for sigma, label in ((mp.mpf('1.3'), "sigma=1.3 (prime side, no winding)"),
                         (mp.mpf('0.8'), "sigma=0.8 (centre captured)")):
        c = (2 * sigma - 1) / (2 * sigma)
        R = 1 / (2 * sigma)
        Msh = 4096

        def Afield(w):
            s = 1 / (1 - w)
            return (s - 1) * mp.zeta(s)

        pts, logs = unwrapped_ring(Afield, c, R, Msh)
        acc = mp.mpc(0)
        for k in range(Msh):
            phi = 2 * mp.pi * (k + mp.mpf('0.5')) / Msh
            acc += logs[k] * pts[k] ** (-(n_mode + 1)) * R * mp.e ** (1j * phi)
        integral = acc * (2 * mp.pi / Msh) / (2 * mp.pi)
        print(f"V5: {label}: contour integral = {mp.nstr(integral.real, 6)} "
              f"(+{mp.nstr(integral.imag, 2)}i)"
              + (f"  [target lambda_3^prime/3 = {mp.nstr(lam3_prime_target, 6)}]"
                 if sigma < 1 else "  [target 0]"))

    # ---------- V6: balance pole ----------
    mp.mp.dps = 30
    C1_closed = -mp.log(-(mp.zeta(mp.mpf('0.5')) * mp.gamma(mp.mpf('0.25'))) / (4 * mp.pi ** mp.mpf('0.25')))
    C1_xi = -mp.log(2 * xi(mp.mpf('0.5')))
    print(f"V6: C1 closed form = {mp.nstr(C1_closed, 15)}; via xi(1/2) = {mp.nstr(C1_xi, 15)}; "
          f"dev {mp.nstr(abs(C1_closed - C1_xi), 3)}")
    xip = mp.diff(xi, mp.mpf('0.5'))
    xipp = mp.diff(xi, mp.mpf('0.5'), 2)
    C3_closed = -(xipp / xi(mp.mpf('0.5'))) / 16
    print(f"V6: xi'(1/2) = {mp.nstr(xip, 3)} (mirror: exactly 0); "
          f"C3 = -(1/16) xi''(1/2)/xi(1/2) = {mp.nstr(C3_closed, 12)}")
    print("V6: approach along the segment (function side, unconditional):")
    for rr in ('0.9', '0.99', '0.999'):
        r = mp.mpf(rr)
        v1 = -mp.log(2 * xi(1 / (1 + r)))
        v2 = G_direct(-r)
        v3 = mp.diff(G_direct, -r)
        print(f"   r={rr}: -log 2Xi(-r) = {mp.nstr(v1, 9)} (-> {mp.nstr(C1_closed, 9)}); "
              f"G(-r) = {mp.nstr(v2, 6)} (-> 0); G'(-r) = {mp.nstr(v3, 8)} "
              f"(-> {mp.nstr(C3_closed, 8)})")
    # series side at r = 0.9 with the 120 computed lambdas
    r = mp.mpf('0.9')
    s1 = sum((-1) ** (n - 1) * lam[n] * r ** n / n for n in range(1, N + 1))
    s2 = sum(lam[n] * (-r) ** n for n in range(1, N + 1))
    print(f"V6: series side at r=0.9 (N=120): sum (-1)^(n-1) lam_n r^n/n = {mp.nstr(s1, 9)} "
          f"vs -log 2Xi(-0.9) = {mp.nstr(-mp.log(2 * xi(1 / (1 + r))), 9)}")
    print(f"    sum lam_n (-r)^n = {mp.nstr(s2, 9)} vs G(-0.9) = {mp.nstr(G_direct(-r), 9)}")


if __name__ == '__main__':
    main()
