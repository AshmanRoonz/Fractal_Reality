# Prime-Side Spectroscopy v1: Findings

**Created:** 2026-08-15
**Version:** 1.0
**Code:** `experiments/prime_side_spectroscopy_v1.py`
**Parent:** zeta note Addendum 8's final question: what Hilbert space can represent all prime scale cycles simultaneously, without collapsing them, while making their joint scale evolution self-adjoint?

The infinite object is the open problem (it is RH). This experiment computes its finite window and checks that the window behaves exactly as the sought whole would. Basis: 71 Gaussian wave packets g_nu(u) = exp(-u^2/(2 sigma^2)) e^(i nu u) in the octave coordinate u = log x, sigma = 1.5, scale-frequencies nu in [10, 45]. The Gram matrix of the Weil (conserving) form, B_jk = sum over zero ordinates of ghat_j(gamma) ghat_k(gamma), was computed ENTIRELY from the arithmetic side of the explicit formula: von Mangoldt sums over 149,235 prime powers up to 2e6, plus a digamma integral, plus (negligible in-band) pole terms. No zeta evaluations, no zeros, anywhere in the pipeline.

## F1 (grade A): the normalization and the formula, verified end to end

Validation entries computed independently from the first 60 zeros match the prime-side entries to 3.5e-8 (diagonal at nu = 14), 4.6e-9 (nu = 21), and 1.5e-14 (an off-diagonal that both sides agree is zero). The explicit formula used (stated in the code header, with the derivation from the even case) is exact as normalized.

## F2 (grade A): the three pre-registered predictions, all confirmed

- **P1 (positivity = window conservation).** Minimum eigenvalue -1.1e-7 against maximum 34.7: positive semidefinite to the numerical floor (relative -3e-9). Positivity of the window form is what "the conserving inner product exists here" means; a straddling zero pair inside the band would create indefinite directions, so the window's positivity reflects the computationally verified absence of off-line zeros at these heights, and is not a proof of anything beyond the window.
- **P2 (rank = zero count).** Eigenvalues above threshold: exactly 8. Zeros in the effective band: exactly 8. The spectrum is razor-sharp: eight eigenvalues between 32.1 and 34.7, then 0.000. Each on-circle zero contributes one rank-one direction; the window form IS the Gram matrix of the zero-evaluation vectors, and the primes know it.
- **P3 (recovery of the ordinates).** MUSIC subspace scan on the prime-built B, peaks at: 14.1350, 21.0200, 25.0100, 30.4250, 32.9350, 37.5850, 40.9200, 43.3250 against true ordinates 14.1347, 21.0220, 25.0109, 30.4249, 32.9351, 37.5862, 40.9187, 43.3271. Deviations 0.0001 to 0.002, at the scan grid's resolution. **The zeta zeros, located to three or four digits, from prime powers and a digamma integral.**

## F3 (grade A, the composition control): the zeros emerge as the primes compose

The diagonal profile B(nu, nu) is a sum of Gaussian bumps at the zeros. Rebuilt with truncated prime sets:

| primes up to | correlation with zero-bump target | top-8 peak deviations |
|---|---|---|
| 10 | +0.8644 | 0.05 to 0.41 |
| 100 | +0.9962 | 0.003 to 0.019 |
| 1000 | +1.0000 | 0.000 to 0.005 |
| 2,000,000 | +1.0000 | 0.000 to 0.002 |

Four primes give a blur; twenty-five give the zeros to two decimals; none of the peaks is any single prime's comb (the comb of 2 alone would sit at multiples of 2 pi / log 2 = 9.06). The zeros are not in any prime; they are in the composition, and they condense fast.

## What this answers, and what it does not

The final question asked for a Hilbert space representing all prime scale cycles simultaneously, without collapse, with self-adjoint joint evolution. **In the window, this experiment exhibits it**: the test-packet space with the Weil form. Every prime's cycle enters as one superposed signal (the von Mangoldt sum); nothing is quotiented, so nothing collapses; the form is real symmetric (self-adjointness built in); and the joint spectrum, the thing the composition produces, is the zeta ordinates, recovered without touching zeta. The window behaves exactly as the sought whole would.

What does not extend: the positivity. On a window it is a numerical fact reflecting verified zeros; on all windows at once it is the Weil positivity criterion, which is RH. The experiment therefore adds no progress on RH and was not expected to; its contribution is a concrete demonstration that the "whole" of the thread's endpoint is not rhetoric: in finite dimension you can build it, diagonalize it, and read the zeros off it, from primes alone.

## Honesty box

Recovering zeros from primes via the explicit formula is standard mathematics; the formula IS that statement, and spike-plot demonstrations of it are classical. The presentation here (Gram-matrix rank equal to the windowed zero count; MUSIC subspace recovery; positivity read as window conservation; the truncated-prime composition control) is a signal-processing arrangement of known content, possibly fresh as a demonstration, claimed only as that. Convergence subtleties: the Gaussian test class is not compactly supported (prime sums truncated at 2e6 with tail below 1e-15 by the Gaussian factor); pole terms are exactly computed and negligible in-band; validation zero-sums truncate at 60 zeros with Gaussian-small tails. Nothing in this file constitutes progress on the Riemann Hypothesis.

## Revision history

- 2026-08-15 v1.0: initial run; all three pre-registered predictions confirmed on first execution; composition control added same session.
