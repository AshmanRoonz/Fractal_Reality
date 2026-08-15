# Prime Boundary Field v1: Findings

**Created:** 2026-08-15
**Version:** 1.0
**Code:** `experiments/prime_boundary_field_v1.py`
**Parent note:** `plans/zeta_circumpunct_coordinates_2026_08_15.md` (Addendum 4 proposed this experiment and pre-registered its pressure test)

The experiment: build the boundary field on the RH circle (|w| = 1, w = (s-1)/s) from the prime signal, decompose it into circle harmonics, and test whether the n-th Li coefficient is the energy of the n-th mode. Li's criterion: RH iff lambda_n >= 0 for all n.

## F1 (grade A): the boundary field computed from xi, no zeros used

FFT extraction of the Taylor coefficients of log Xi(z) = log xi(1/(1-z)) on the ring |z| = 1/2 (128 points, 32 digits; branch unwrapped, winding 0 to 1e-34). lambda_1, lambda_2, lambda_3 match the session anchors to 1e-13; c_0 = log(1/2) exactly. All forty lambda_n positive. The Lagarias asymptotic (n/2)(log n - log 2pi + gamma - 1) is approached from above (ratio 1.19 at n = 20, 1.07 at n = 40); the wild ratio at n = 10 (10.9) is the asymptotic's bracket nearly vanishing there, not a failure.

## F2 (grade A): the prime moments

The arithmetic half of the field is A(z) = log[(s-1) zeta(s)], and d/du log(u zeta(1+u)) = sum_j eta_j u^j where the eta_j are the regularized prime moments (the coefficients of -zeta'/zeta about s = 1, each an unconditional limit of von Mangoldt sums). Computed by ring extraction: **eta_0 = gamma to 1.5e-33** (the Mertens constant appearing as the zeroth prime moment), eta_1 = -0.1875462328, eta_2 = +0.0516886320, decaying like 3^-j (the radius set by the first trivial zero at s = -2, i.e. u = -3: the nearest obstruction to the prime expansion is the trivial structure outside the strip).

## F3 (grade A): the bridge is a binomial transform

The question Addendum 4 asked ("what operation turns the logarithmic prime spectrum into the Li angular spectrum?") has an exact answer. Because u = s - 1 and z are related by u = z/(1-z), coefficient composition gives, with no approximation:

    lambda_n^prime = sum_{j>=0} eta_j C(n, j+1)

**The conformal warping from prime frequencies to circle harmonics is, at coefficient level, the binomial transform of the regularized prime moments.** Verified against an independent direct FFT of A(z): max deviation 2.5e-20 over n <= 40. Adding the archimedean modes (FFT of log[(1/2) s pi^(-s/2) Gamma(s/2)]) reproduces the full lambda_n to 2.7e-20. Observation, no claim attached: the prime part is positive for all n <= 40 while the archimedean part changes sign near n = 9; the small early lambda_n are a near-cancellation of the two (at n = 1: +0.5772 - 0.5541 = 0.0231).

This is not new mathematics: expressions for lambda_n via these eta constants are in the Bombieri-Lagarias and Coffey line of work. What is established here is the verified computation and the geometric reading: the binomial transform IS the Mobius map u = z/(1-z) acting on coefficients, the same map that draws the shell family.

## F4 (grade C): the primes themselves assemble the field

Sieve of the actual primes to X = 10^7 (psi(X)/X = 0.999854), with the PNT regularization E(x) = psi(x) - x: eta_0 = 0.5538 (exact 0.5772, err 2.4e-2), eta_1 = -0.2514 (exact -0.1875, err 6.4e-2), eta_2 = +0.0170 (exact +0.0517, err 3.5e-2). Truncation-limited (the oscillating tail of E(x)/x^2 converges slowly); two-digit accuracy at 10^7 is what honest truncation buys. The demonstration stands: **von Mangoldt data alone, regularized against x, assembles the Li coefficients**; lambda_1 from sieved primes plus the archimedean mode lands at 0.0231-ish with the expected error. Grade C for precision, A for mechanism.

## F5 (the headline; exact algebra, verified): lambda_n = E_n - D_n

Per zero, with W = w_rho^n, two lines of algebra give

    1 - Re(W) = (1/2)|1 - W|^2 - (1/2)(|W|^2 - 1)

(verified 1e-20 at an arbitrary complex point). Summing over the zero multiset in the standard symmetric order:

    lambda_n = E_n - D_n

- **E_n = (1/2) sum |1 - w_rho^n|^2 >= 0 always**: the energy of the function 1 - e^(in theta) against the zero measure; the boundary mode energy.
- **D_n = (1/2) sum (|w_rho^n|^2 - 1) >= 0 always**: after pairing each zero with its functional-equation partner (w with 1/w), each pair contributes (x + 1/x - 2)/2 with x = |w^n|^2, which is **the AM-GM gap of the inversion pair**: nonnegative, and zero iff |w| = 1. Verified: the AM-GM form equals the direct sum to 1e-13 even at n = 119,699.

Consequences, all exact:

1. **RH iff D_n = 0 for all n iff lambda_n = E_n**: the Li coefficient IS the boundary mode energy precisely when every zero sits on the boundary.
2. **Li positivity is E_n >= D_n**: energy beats defect at every harmonic.
3. Numerical exhibits: the hypothetical off-line quartet at Re(s) = 0.6, t = 50 gives, at n = 119,699: E = 14161.1, D = 14397.1, E - D = -236.008, exactly matching the direct computation from Addendum 1's scan. Both E and D are individually enormous and nonnegative; the lambda-contribution goes negative because the defect outruns the energy. On the real (on-line) zeros: D_n = 0 to 1e-20 and E_n (300 zeros + tail) reproduces lambda_1, lambda_2, lambda_3.

## The pressure test verdict (as pre-registered)

The transported-energy identity "lambda_n = energy of mode n" is **exactly equivalent to RH**, not a route to it. The prime side (F2-F4) computes lambda_n unconditionally, but only as the package E_n - D_n: the explicit-formula machinery delivers the difference and cannot separate energy from defect without knowing where the zeros are. The split IS the Riemann Hypothesis. This is consistent with the reported Suzuki-type results (norm identities equivalent to RH) and with Bombieri-Lagarias (Li positivity as a case of Weil positivity). No unconditional positivity was obtained, and none was expected; the experiment's contribution is making the gap's exact location computable and visible: **what the primes cannot see is the radial coordinate of their own zeros.**

## Framework typing (interpretation, marked as such)

E_n is the shared/boundary content (the angle channel of Addendum 3: pure i-rotation energy); D_n is the radial defect, and its AM-GM form makes it literally the cost of the inflation/severance pair: each off-boundary zero is one partner inflated (|w| > 1) and one severed (|w| < 1), and D_n prices the pair's departure from balance, zero exactly at kappa-health. RH in this vocabulary: **every overtone of the boundary carries zero defect; all the energy lives in rotation, none in radial escape.** The two Lies appear as the two halves of one AM-GM gap, and the conjectured truth of RH is that the gap never opens.

## Honesty box

The E - D identity is two lines of algebra and is surely implicit in the Li-criterion literature; no novelty is claimed for it, for the binomial form (Bombieri-Lagarias/Coffey territory), or for the eta moments. Zero sums converge conditionally and were taken in symmetric order; the 300-zero checks use a first-order tail estimate; the sieve section is truncation-limited to two digits. The claims made: the computations verify as reported, the pressure test resolved exactly as pre-registered (energy identity equivalent to RH, not unconditional), and the typing (energy/defect as rotation/radial-escape, AM-GM as the two Lies' shared price) is interpretation over verified structure. Nothing in this file constitutes progress on RH.

## Revision history

- 2026-08-15 v1.0: initial run. Section 4 executed standalone after a numpy install (same code path); all other sections from the main script, exit 0.
