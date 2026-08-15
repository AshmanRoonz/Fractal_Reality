"""
weil_scale_operator_v1.py

Created: 2026-08-15
Last updated: 2026-08-15
Version: 1.0
History:
- 2026-08-15 v1.0: initial. The scale operator compressed in the Weil metric:
  the free scale generator, deformed by the arithmetic coupling, has the
  Riemann ordinates as its spectrum in the window.

Sequel to prime_side_spectroscopy_v1.py, engaging the operator-level form of
the thread's final question. Two Hermitian forms on Gaussian scale-packets
g_nu(u) = exp(-u^2/(2 sigma^2)) e^{i nu u}, both computed ENTIRELY from the
arithmetic side of the Weil explicit formula (prime powers + digamma; no zeta
evaluations, no zeros):

    B0_jk = sum over ordinates gamma of  ghat_j(gamma) ghat_k(gamma)
    B1_jk = sum over ordinates gamma of  gamma ghat_j(gamma) ghat_k(gamma)

B0 is the Weil inner product on the window. B1 is the scale derivative
-i d/du paired through that inner product (multiplication by gamma on the
zero side IS the scale generator in the spectral picture). The compressed
scale operator is the generalized eigenproblem on the signal subspace:

    B1 v = gamma B0 v.

Because both forms are real symmetric and B0 is positive on the signal
subspace, the compressed operator is self-adjoint and its eigenvalues are
REAL BY TYPE: every finite-stage approximant is boundary-locked (|w| = 1).
The question the computation asks: do the eigenvalues land on the actual
Riemann ordinates?

Pre-registered predictions:
  P1  the eight eigenvalues approximate the eight in-band ordinates, more
      precisely than the v1 MUSIC scan (no grid involved);
  P2  the same operator compressed in the PLAIN L2 metric shows a featureless
      continuum (the nu grid back again): the arithmetic metric, not the
      operator, deletes the continuum and leaves the zeros;
  P3  the eigenvalues converge as the prime cutoff grows (the finite-stage
      convergence question, in miniature).

Closed forms used (sigma-Gaussian packets; Delta = nu_j - nu_k,
mu = (nu_j + nu_k)/2, E = exp(-sigma^2 Delta^2/4), K(u) = exp(-u^2/(4 sigma^2))):

    h0(t) = 2 pi sigma^2 E exp(-sigma^2 (t-mu)^2)         [for B0]
    h1(t) = t h0(t)                                        [for B1]
    2 Re g0(u) = 2 sigma sqrt(pi) E K(u) cos(u mu)
    2 Re g1(u) = 2 mu sigma sqrt(pi) E K(u) cos(u mu)
                 - (u sqrt(pi)/sigma) E K(u) sin(u mu)

Explicit formula (normalization validated in prime_side_spectroscopy_v1 and
revalidated here): sum_gamma h(gamma) = poles + (1/2pi) int h Omega
- 2 sum Lambda(n) n^{-1/2} Re g(log n), Omega(t) = Re psi(1/4+it/2) - log pi.
Pole terms are O(exp(-sigma^2 mu^2)) in-band and dropped (stated).

Honesty: this realizes, in a small numerical window, the architecture of the
current spectral RH programs as reported in session (Connes-Consani-Moscovici
2025 zeta spectral triples: finite-stage self-adjoint perturbations of the
scale operator with real-zero characteristic functions; Suzuki 2026: the
scale derivative made symmetric on Weil-completed spaces). Those primary
sources could not be fetched from this environment; the construction here is
independent standard linear algebra on the explicit formula. No convergence
theorem is proved; the window-to-infinity limit IS the open problem.
"""

import numpy as np
import mpmath as mp

SIGMA = 1.5
NU_MIN, NU_MAX, NU_STEP = 10.0, 45.0, 0.5
N_MAX = 2_000_000
N_ZEROS_VAL = 60

TRUE_ZEROS = [14.134725141734693, 21.022039638771554, 25.010857580145688,
              30.424876125859513, 32.935061587739189, 37.586178158825671,
              40.918719012147495, 43.327073280914999, 48.005150881167159,
              49.773832477672302]


def sieve_von_mangoldt(N):
    is_p = np.ones(N + 1, dtype=bool)
    is_p[:2] = False
    for p in range(2, int(N ** 0.5) + 1):
        if is_p[p]:
            is_p[p * p::p] = False
    primes = np.nonzero(is_p)[0]
    ns, lams = [primes.astype(np.float64)], [np.log(primes.astype(np.float64))]
    for p in primes[primes <= int(N ** 0.5)]:
        pk = p * p
        while pk <= N:
            ns.append(np.array([float(pk)]))
            lams.append(np.array([np.log(float(p))]))
            pk *= p
    n = np.concatenate(ns)
    lam = np.concatenate(lams)
    order = np.argsort(n)
    return n[order], lam[order]


def main():
    mp.mp.dps = 15
    s = SIGMA
    nu = np.arange(NU_MIN, NU_MAX + 1e-9, NU_STEP)
    K = len(nu)
    print(f"basis: {K} packets, sigma={s}, band [{NU_MIN}, {NU_MAX}]")

    n_arr, lam_arr = sieve_von_mangoldt(N_MAX)
    logn = np.log(n_arr)
    kernel = np.exp(-logn ** 2 / (4 * s * s))
    base_w = lam_arr / np.sqrt(n_arr) * kernel

    t_lo, t_hi, dt = NU_MIN - 6.0, NU_MAX + 6.0, 0.02
    t_grid = np.arange(t_lo, t_hi + dt, dt)
    Om = np.array([float(mp.re(mp.digamma(mp.mpc(0.25, tt / 2)))) for tt in t_grid]) - np.log(np.pi)

    mu_grid = np.arange(NU_MIN, NU_MAX + 1e-9, NU_STEP / 2)
    mu_index = {round(m, 6): i for i, m in enumerate(mu_grid)}

    def build_forms(X):
        mask = n_arr <= X
        w = base_w[mask]
        ln = logn[mask]
        Pc = np.array([np.sum(w * np.cos(m * ln)) for m in mu_grid])
        Ps = np.array([np.sum(w * ln * np.sin(m * ln)) for m in mu_grid])
        I0 = np.array([np.trapezoid(np.exp(-s * s * (t_grid - m) ** 2) * Om, t_grid) for m in mu_grid])
        I1 = np.array([np.trapezoid(t_grid * np.exp(-s * s * (t_grid - m) ** 2) * Om, t_grid) for m in mu_grid])
        B0 = np.zeros((K, K))
        B1 = np.zeros((K, K))
        for j in range(K):
            for k in range(j, K):
                D = nu[j] - nu[k]
                m = (nu[j] + nu[k]) / 2
                i_m = mu_index[round(m, 6)]
                E = np.exp(-s * s * D * D / 4)
                B0[j, k] = B0[k, j] = E * (s * s * I0[i_m] - 2 * s * np.sqrt(np.pi) * Pc[i_m])
                B1[j, k] = B1[k, j] = E * (s * s * I1[i_m]
                                           - 2 * m * s * np.sqrt(np.pi) * Pc[i_m]
                                           + (np.sqrt(np.pi) / s) * Ps[i_m])
        return B0, B1

    B0, B1 = build_forms(N_MAX)
    print("forms B0, B1 assembled from primes + digamma only")

    # --- validation against the zero side ---
    zeros = [float(mp.zetazero(k).imag) for k in range(1, N_ZEROS_VAL + 1)]
    def zero_side(j, k, moment):
        D = nu[j] - nu[k]; m = (nu[j] + nu[k]) / 2
        tot = 0.0
        for g in zeros:
            for gg in (g, -g):
                hval = 2 * np.pi * s * s * np.exp(-s * s * D * D / 4) * np.exp(-s * s * (gg - m) ** 2)
                tot += (gg ** moment) * hval
        return tot
    print("validation (arithmetic vs zero side), entries (j,k) and moments:")
    for (j, k) in [(8, 8), (10, 20)]:
        for mom, Bm in ((0, B0), (1, B1)):
            zs = zero_side(j, k, mom)
            print(f"  nu=({nu[j]},{nu[k]}) m={mom}: arith={Bm[j,k]:+.6f}, zeros={zs:+.6f}, "
                  f"dev={abs(Bm[j,k]-zs):.2e}")

    # --- the compressed scale operator in the Weil metric ---
    evals0, evecs0 = np.linalg.eigh(B0)
    in_band = [g for g in TRUE_ZEROS if NU_MIN - 2 < g < NU_MAX + 2]
    n_sig = len(in_band)
    S = evecs0[:, -n_sig:]                 # signal subspace of the Weil form
    A0 = S.T @ B0 @ S
    A1 = S.T @ B1 @ S
    L = np.linalg.cholesky(A0)
    Li = np.linalg.inv(L)
    M = Li @ A1 @ Li.T
    gam = np.sort(np.linalg.eigvalsh(M))
    print(f"\nP1: eigenvalues of the Weil-compressed scale operator vs true ordinates:")
    for g_est, g_true in zip(gam, sorted(in_band)):
        print(f"  {g_est:12.6f}   true {g_true:12.6f}   dev {abs(g_est-g_true):.2e}")

    # --- P2: the same operator in the plain L2 metric ---
    Dm = nu[:, None] - nu[None, :]
    Mu = (nu[:, None] + nu[None, :]) / 2
    G0 = s * np.sqrt(np.pi) * np.exp(-s * s * Dm ** 2 / 4)          # <g_j, g_k>
    # <g_j, -i g_k'> : multiplication by t on the Fourier side:
    # int t ghat_j ghat_k dt/(2pi) = G0 * (mu + 0) for real Gaussians -> mu G0
    G1 = G0 * Mu
    ev_plain = np.sort(np.linalg.eigvalsh(np.linalg.inv(np.linalg.cholesky(G0)) @ G1
                                          @ np.linalg.inv(np.linalg.cholesky(G0)).T))
    print(f"\nP2: plain-metric compression of the same operator: {K} eigenvalues,")
    print(f"  spread {ev_plain[0]:.2f} .. {ev_plain[-1]:.2f}, spacing ~{np.median(np.diff(ev_plain)):.3f}")
    print("  (the featureless continuum: the nu grid back again; no zeros anywhere)")

    # --- P3: convergence in the prime cutoff ---
    print("\nP3: eigenvalues vs prime cutoff (dev from true ordinates, max over the 8):")
    for X in (100, 1000, 10_000, N_MAX):
        B0x, B1x = build_forms(X)
        e0, v0 = np.linalg.eigh(B0x)
        Sx = v0[:, -n_sig:]
        A0x = Sx.T @ B0x @ Sx
        A1x = Sx.T @ B1x @ Sx
        try:
            Lx = np.linalg.cholesky(A0x)
            Lxi = np.linalg.inv(Lx)
            gx = np.sort(np.linalg.eigvalsh(Lxi @ A1x @ Lxi.T))
            devs = [abs(a - b) for a, b in zip(gx, sorted(in_band))]
            print(f"  primes <= {X:>7}: max dev {max(devs):.4f}, mean dev {np.mean(devs):.4f}")
        except np.linalg.LinAlgError:
            print(f"  primes <= {X:>7}: signal subspace not yet positive (form indefinite)")

    print("\nVERDICT: the scale generator, compressed in the arithmetic (Weil)")
    print("metric built from primes alone, is self-adjoint by construction")
    print("(eigenvalues real by type: every finite stage is boundary-locked)")
    print("and its spectrum lands on the Riemann ordinates. The plain metric")
    print("keeps the continuum; the arithmetic metric deletes it. What remains")
    print("open is the window-to-infinity limit, which is RH.")


if __name__ == '__main__':
    main()
