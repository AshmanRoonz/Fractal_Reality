# Finite-Window Arithmetic-Metric Certificate v2

**Date:** 2026-08-15  
**Inputs:** `weil_scale_operator_v1.py`, `prime_side_spectroscopy_v1.py`  
**Scope:** the eight positive Riemann ordinates below 48 sampled by the 71 Gaussian packets centered from 10 to 45, with `sigma = 1.5`.

## Result

The finite-support matrix-pencil recovery is exact:

\[
B_0^\star = V V^*,\qquad
B_1^\star = V\Gamma V^*,
\]

and any 8-dimensional subspace transverse to `ran(V)` gives the same ideal generalized eigenvalues `diag(Gamma)` after restriction, because both forms undergo the same invertible congruence.

For the actual packet family,

- `sigma_min(V) = 5.66823878`
- `sigma_max(V) = 5.88987779`
- `cond(V) = 1.03910192`
- `a = lambda_min^+(B0*) = 32.12893087`
- `b = lambda_max(B0*) = 34.69066044`

The target spectral representation is therefore extremely well-conditioned.

## Rigorous-form truncation bounds

The uploaded code uses

\[
\widehat g_\nu(t)=\sigma\sqrt{2\pi}\,
e^{-\sigma^2(t-\nu)^2/2}
\]

and prime coupling envelope

\[
K(\log n)=e^{-(\log n)^2/(4\sigma^2)}.
\]

At prime-power cutoff \(P=2,000,000\), using only
\(\Lambda(n)\le \log n\) and enlarging the prime-power tail to all integers gives

\[
\varepsilon^{\rm prime}_0
\le 1.9691703813\times 10^{-4},
\]

\[
\varepsilon^{\rm prime}_1
\le 9.5117157726\times 10^{-3}.
\]

These are deliberately crude absolute operator-norm bounds; they do not use cancellation of the oscillatory prime phases.

For the off-window zero contribution, Bellotti-Wong's explicit bound

\[
\left|N(T)-\frac{T}{2\pi}
\log\frac{T}{2\pi e}\right|
\le
0.10076\log T+0.24460\log\log T+8.08344
\]

for \(T\ge e\) gives, starting at \(T=48\), and allowing arbitrary
\(0<\beta<1\) through the Gaussian factor
\(e^{\sigma^2(\beta-1/2)^2}\le e^{\sigma^2/4}\),

\[
\varepsilon^{\rm zero}_0
\le 4.7287201707\times10^{-5},
\]

\[
\varepsilon^{\rm zero}_1
\le 2.2934340274\times10^{-3}.
\]

The negative-ordinate partners contribute below \(10^{-500}\) at this positive-frequency window. The pole terms omitted by the operator script are below \(10^{-94}\) in operator norm.

Thus, for the exact archimedean integral and exact arithmetic,

\[
\varepsilon_0
\le 2.4420423984\times10^{-4},
\]

\[
\varepsilon_1
\le 1.1805149800\times10^{-2}.
\]

## Signal-subspace movement does not break the algebra

Let \(\widetilde S\) be the top-8 eigenspace extracted from the perturbed arithmetic \(B_0\). Davis-Kahan gives

\[
\sin\Theta
\le
\eta=
\frac{\varepsilon_0}{a-\varepsilon_0}
\approx 7.6008\times10^{-6}.
\]

More importantly, the *ideal* pair restricted to any transverse 8-dimensional subspace still has the exact ordinates as generalized eigenvalues. If \(W\) spans that subspace and \(C=V^*W\), then

\[
W^*B_0^\star W=C^*C,\qquad
W^*B_1^\star W=C^*\Gamma C,
\]

so invertibility of \(C\) preserves the pencil spectrum exactly.

Subspace movement therefore enters only through the lower metric bound, not as a separate first-order spectral error.

## Certified finite-window eigenvalue enclosure

With

\[
M=\max_r\gamma_r=43.3270732809
\]

and the perturbed metric lower bound, generalized Rayleigh-quotient perturbation gives

\[
\boxed{
|\widetilde\gamma_r-\gamma_r|
\le
6.9676\times10^{-4}
}
\]

for all eight recovered modes of the exact truncated arithmetic form.

The minimum gap among the eight target ordinates is

\[
2.4083542688,
\]

whereas

\[
2\delta\approx1.3935\times10^{-3}.
\]

So the theorem also certifies **unique mode matching by an enormous margin**.

This bound is intentionally conservative. The observed implementation errors are around \(10^{-12}\) because the prime tail is highly oscillatory and cancels; the theorem above refuses to use that cancellation.

## Implementation audit

The uploaded script reports arithmetic-vs-zero-side entry checks at roughly

- \(3.5\times10^{-8}\) for \(B_0\)
- \(4.6\times10^{-7}\) for \(B_1\)

and recovers the eight ordinates to roughly \(10^{-12}\).

An independent high-accuracy quadrature comparison of the uploaded trapezoid grid against adaptive quadrature found maximum discrepancies around

- \(2.2\times10^{-15}\) in the archimedean \(I_0\) integrals
- \(8.5\times10^{-14}\) in the archimedean \(I_1\) integrals

for the 141 `mu` values. This is an implementation check, not interval arithmetic, so it is not used in the rigorous-form bound above.

## Rank correction

The phrase "rank exactly 8" should be replaced by:

> **effective numerical rank 8 at the stated window and threshold.**

With Gaussian packets, every zero has a nonzero analytic tail, so the full exact matrix is not literally rank 8. The **ideal target-only matrix** has exact rank 8. The complete matrix has a sharply separated eight-dimensional signal subspace because the leakage is tiny relative to

\[
a=32.12893087.
\]

## What is proved here

This is a genuine finite-dimensional theorem/certificate:

1. finite target support is recovered exactly by the moment pencil;
2. the target packet family is well-conditioned;
3. prime truncation and off-window zero leakage admit explicit unconditional norm majorants;
4. the prime-only signal subspace remains transverse and stable;
5. every recovered finite-window eigenvalue lies within about `0.000697` of its unique target ordinate.

It does **not** prove RH. Nothing here controls the window-to-infinity limit or global positivity. The infinite limit remains the RH-grade step.
