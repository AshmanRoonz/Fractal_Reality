# The Weil-Compressed Scale Operator v1: Findings

**Created:** 2026-08-15
**Version:** 1.0
**Code:** `experiments/weil_scale_operator_v1.py`
**Parent:** `experiments/prime_side_spectroscopy_v1.py` (the Gram matrix and its validation); zeta note Addenda 8-9 (the confinement question).

The operator-level engagement of the thread's final question. Two Hermitian forms on 71 Gaussian scale-packets, both computed entirely from the arithmetic side of the Weil explicit formula (prime powers to 2e6 plus a digamma integral; no zeta evaluations, no zeros):

    B0 = the Weil inner product on the window (sum over ordinates of ghat_j ghat_k)
    B1 = the scale derivative -i d/du paired through that inner product
         (sum over ordinates of gamma ghat_j ghat_k)

The compressed scale operator is the generalized eigenproblem B1 v = gamma B0 v on the signal subspace of B0. Both forms real symmetric, B0 positive there: **the operator is self-adjoint by construction, so its eigenvalues are real by type. Every finite stage is boundary-locked: |w| = 1 before anyone checks anything.** The computation asks whether the eigenvalues land on the actual Riemann ordinates.

## F1 (grade A): validation

Both forms validated against the zero side (60 zeros): B0 entries to 3.5e-8, B1 entries to 4.6e-7; off-diagonal zero entries agree to 1e-13.

## F2 (the headline): the spectrum IS the zeros, to twelve digits

Eigenvalues of the Weil-compressed scale operator versus the true ordinates:

| eigenvalue | true ordinate | deviation |
|---|---|---|
| 14.134725 | 14.134725141 | 1.4e-12 |
| 21.022040 | 21.022039639 | 1.8e-12 |
| 25.010858 | 25.010857580 | 3.5e-13 |
| 30.424876 | 30.424876126 | 1.0e-12 |
| 32.935062 | 32.935061588 | 5.5e-13 |
| 37.586178 | 37.586178159 | 7.8e-13 |
| 40.918719 | 40.918719012 | 6.4e-13 |
| 43.327073 | 43.327073281 | 3.7e-12 |

**Why the precision is structural, not mysterious** (stated so nobody over-reads it): within the window, B0 and B1 are exactly the moment-0 and moment-1 Gram matrices of the zero-evaluation vectors, so on the signal subspace the pencil's eigenvalues are exactly the windowed ordinates as a linear-algebra identity; the deviations measure only out-of-band leakage (the nearest excluded zero at 48.005 enters at Gaussian-squared suppression ~1e-9 and is further cut by the projection) plus quadrature and truncation error. The content of the result is not the twelve digits; it is that **the matrices were assembled from primes**, and the identity held.

## F3 (grade A): the metric, not the operator, carries the arithmetic

The same scale generator compressed in the plain L2 metric on the same packets: 71 eigenvalues spread uniformly across the band at the packet-grid spacing (~0.5). The featureless continuum, no zeros anywhere. One operator, two inner products: the plain metric keeps the continuum; the arithmetic metric deletes it and leaves the zeros. This is the thread's "keep every loop and every relation between loops" made operational: the prime periods enter as coupling structure inside the inner product, not as boundary identifications on the space.

## F4 (grade A): finite-stage convergence in the window

Eigenvalue accuracy versus prime cutoff:

| primes up to | max deviation | mean deviation |
|---|---|---|
| 100 | 0.0041 | 0.0022 |
| 1,000 | 0.0001 | 0.00003 |
| 10,000 | < 1e-4 | < 1e-5 |
| 2,000,000 | ~1e-12 | ~1e-12 |

Twenty-five primes know the first eight zeros to three digits through this operator; a thousand primes to four. The composition converges fast in the window. (This is the window analogue of the finite-stage convergence that the current spectral programs need at infinity; nothing here bears on the infinite limit.)

## What this establishes, and what it does not

Established, as computation: the architecture the current research frontier proposes (finite-stage self-adjoint deformations of the scale generator by arithmetic coupling, with reality of zeros automatic at every stage) can be realized in a window by elementary means, from primes alone, and its spectrum lands exactly where it should. The prime periods log p never appear as identifications (which Addendum 8 showed would annihilate); they appear as coupling distances inside the inner product, and the incommensurability that destroyed the naive quotient is exactly what lets the couplings interfere into the zeta spectrum.

Not established: anything about the window-to-infinity limit. At every finite stage reality of the spectrum is free (self-adjointness); the entire difficulty of RH lives in the convergence of the family to the completed xi, which is where the reported Connes-Consani-Moscovici determinant strategy and Suzuki's limiting-operator conjecture sit. Those primary sources were not fetchable from this environment and are cited as reported. This experiment is independent standard linear algebra on the explicit formula; no novelty is claimed for the architecture, and no progress on RH is claimed at all.

## Honesty box

The twelve-digit agreement is a structural identity holding within the window (see F2), not an approximation converging to truth; presenting it otherwise would be resolution abuse. The Gaussian test class is not compactly supported (tails below 1e-15 at the cutoff); pole terms are dropped at magnitude exp(-sigma^2 mu^2), stated in the code; the P3 cutoff study varies only the prime sums, holding the archimedean part exact. The plain-metric contrast (F3) uses closed-form Gaussian Gram matrices. The framework typing (metric as the whole's interior, loops as couplings) is interpretation over verified structure, marked as such in the zeta note.

## Revision history

- 2026-08-15 v1.0: initial run; all three pre-registered predictions confirmed on first execution.
