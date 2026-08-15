# The Shell Trident and the Balance Pole

**Status:** derived, proved, and numerically verified in session, 2026-08-15, in response to the challenge: derive one new exact theorem inside the circumpunct coordinates for zeta, connecting shell radius, Mellin norm, and Li angular modes, to test whether the framework produces mathematics rather than only reorganizing it. Novelty audit at the end; it is conceded in advance that every technique is classical and that parts may exist in the Keiper/Li literature, which could not be fully checked from this environment.

Coordinates throughout: w = (s - 1)/s, s = 1/(1 - w). Xi(w) = xi(1/(1 - w)); Li coefficients lambda_n = n [w^n] log 2Xi(w); RH iff lambda_n >= 0 for all n (Li). Shell C_sigma = image of the vertical line Re s = sigma; from Addendum 4 of the zeta note, C_sigma is the circle of radius R = 1/(2 sigma) centred at 1 - R, internally tangent to the unit circle at the tonic point w = 1. The arithmetic field is A(w) = log[(s - 1) zeta(s)], analytic at w = 0 with A(0) = 0, whose Taylor coefficients carry the prime part of the Li data: n [w^n] A = lambda_n^prime = sum_j eta_j C(n, j+1) (prime_boundary_field findings F3).

---

## Theorem 1 (the shell trident)

**(a) Radius/weight law.** For f measurable with the right-hand side finite, the Mellin transform (Mf)(s) = integral_0^infty f(x) x^(s-1) dx satisfies, on the shell of radius R = 1/(2 sigma):

    (1/2 pi) integral_R |(Mf)(sigma + it)|^2 dt  =  integral_0^infty |f(x)|^2 x^(1/R - 1) dx.

The Plancherel weight on a shell of radius R is x^(1/R - 1). It is flat, and the transform is unitary, precisely at R = 1: the critical circle is the unique shell of conservation, and the weight exponent 1/R - 1 vanishes exactly there.

**(b) Measure pullback.** Under s = 1/2 + it, w = e^(i theta): t = (1/2) cot(theta/2) and

    dt = d theta / |1 - w|^2.

Plancherel measure on the critical line is flat angular measure divided by the squared distance to the tonic.

**(c) Winding/visibility.** The shell C_sigma winds once around the centre w = 0 if 0 < sigma < 1 and zero times if sigma > 1 (proof: |centre| < radius iff |2 sigma - 1| < 1). Consequently, for every n >= 1:

  (i) for every sigma > 1, unconditionally:
      (1/2 pi i) contour-integral over C_sigma of A(w) w^(-n-1) dw = 0;
  (ii) for 1/2 < sigma < 1, the same integral equals lambda_n^prime / n, provided zeta has no zeros with Re s > sigma.

Both integrals converge absolutely even though every shell passes through the tonic, because A has only a logarithmic singularity at w = 1. So: **the Cauchy pairing on prime-convergent shells annihilates every Li mode; the modes become visible exactly when the shell crosses the Euler line sigma = 1 and captures the centre.** The Euler shell itself passes through the centre (0 lies on its boundary): the transition shell touches the 1's image.

## Theorem 2 (the balance pole)

The critical circle meets the real axis at exactly two points: the tonic w = 1 (image of infinity, where the zero angles accumulate) and its antipode w = -1, the image of the balance point s = 1/2. Let G(w) = sum_(n>=1) lambda_n w^n.

**(a) Generating identity.** G(w) = s(s - 1) xi'(s)/xi(s) with s = 1/(1 - w), valid for |w| < r_0 where r_0 = min(1, min over zeros of |w_rho|).

**(b) Unconditional limits along the segment.** As r goes to 1 from below:

    -log 2 Xi(-r)  ->  -log[ - zeta(1/2) Gamma(1/4) / (4 pi^(1/4)) ]   (call it C_1),
    G(-r)          ->  0,
    G'(-r)         ->  -(1/16) xi''(1/2) / xi(1/2)                      (call it C_3),

the middle limit because the mirror xi(s) = xi(1 - s) forces xi'(1/2) = 0.

**(c) RH equivalence.** The following are equivalent:

  (i)   the Riemann Hypothesis;
  (ii)  sum (-1)^(n-1) lambda_n is Abel summable;
  (iii) sum (-1)^(n-1) lambda_n / n is Abel summable.

When they hold, the Abel sums are, respectively, **0** and **C_1 = -log[-zeta(1/2) Gamma(1/4)/(4 pi^(1/4))] = 0.0057750873854...**, and Abel-sum (-1)^(n-1) n lambda_n = C_3 = -0.0028881241394... In words: **RH holds if and only if the alternating Li series can be summed at all, and if it can, the mirror forces its value to be exactly zero.** The even ladder is pinned by Gamma(1/4), zeta(1/2), pi; the odd ladder vanishes by parity.

---

## Proofs

**1(a).** Substitute x = e^u: (Mf)(sigma + it) = integral f(e^u) e^(sigma u) e^(itu) du, the Fourier transform of g(u) = f(e^u) e^(sigma u). Fourier-Plancherel gives (1/2 pi) integral |Mf|^2 dt = integral |g|^2 du = integral |f(x)|^2 x^(2 sigma - 1) dx. By the shell radius law R = 1/(2 sigma) (Addendum 4, proved there), 2 sigma - 1 = 1/R - 1. Flat iff R = 1. QED.

**1(b).** From w = e^(i theta), s = 1/(1 - w) = 1/2 + (i/2) cot(theta/2), so t = (1/2) cot(theta/2); dt/d theta = -(1/4) csc^2(theta/2); |1 - e^(i theta)|^2 = 4 sin^2(theta/2); the product of |dt/d theta| and |1 - w|^2 is 1. QED.

**1(c).** Centre 1 - R = (2 sigma - 1)/(2 sigma), radius R = 1/(2 sigma); 0 enclosed iff |2 sigma - 1| < 1 iff 0 < sigma < 1. For sigma > 1 the closed disk bounded by C_sigma is the image of {Re s >= sigma} plus infinity; there (s - 1) zeta(s) is analytic and zero-free (zeta(s) is nonzero for Re s >= 1, classical; the factor s - 1 compensates the pole and is nonzero), so A is analytic in the open disk and continuous up to the boundary except at w = 1, where A = log(s - 1) + log zeta(s) ~ log(1/(1 - w)): logarithmic, hence integrable along the contour. Since 0 lies outside, w^(-n-1) is also analytic on and inside C_sigma; Cauchy's theorem on the contour with a shrinking notch at w = 1 gives 0 (the notch contribution vanishes by the log estimate). For 1/2 < sigma < 1 with the zero-free hypothesis the same argument applies except that 0 is now inside; the residue of A(w) w^(-n-1) at 0 is the Taylor coefficient [w^n] A = lambda_n^prime / n. QED.

**2(a).** ds/dw = s^2, so d/dw log Xi = s^2 xi'/xi and G = w s^2 xi'/xi = s(s - 1) xi'/xi since w s^2 = s(s - 1). Radius: the singularities of log 2Xi in the closed unit disk are the images of the zeta zeros (log branch points; poles of G) and the essential singularity at the tonic; hence r_0 = min(1, min |w_rho|). QED.

**2(b).** w = -r maps to s = 1/(1 + r), which runs down (1/2, 1] to 1/2 as r -> 1. xi is analytic, real, and strictly positive on this interval (on (0, 1): zeta(sigma) < 0, s(s-1)/2 < 0, Gamma and pi factors positive, so xi > 0; and xi(1/2) != 0 because zeta(1/2) = -1.4603... != 0), so log 2Xi(-r) -> log 2 xi(1/2), and from the definition, xi(1/2) = -(1/8) pi^(-1/4) Gamma(1/4) zeta(1/2), giving C_1. Differentiating the mirror xi(s) = xi(1 - s) gives xi'(s) = -xi'(1 - s); at s = 1/2, xi'(1/2) = 0; hence G(-r) = s(s-1) xi'/xi -> (1/2)(-1/2) * 0 / xi(1/2) = 0. For the derivative: dG/dw = s^2 [(2s - 1) F + s(s - 1) F'] with F = xi'/xi; at s = 1/2 the first term dies twice over ((2s - 1) = 0 and F(1/2) = 0) and F'(1/2) = xi''(1/2)/xi(1/2) (the (xi'/xi)^2 term vanishes), so the limit is (1/4)(1/2)(-1/2) xi''(1/2)/xi(1/2) = -(1/16) xi''(1/2)/xi(1/2). QED.

**2(c).** If RH holds, every |w_rho| = 1, so r_0 = 1: both series converge for each r < 1 and the Abel limits exist and equal the limits of 2(b) by continuity of G and log 2Xi at w = -1 (Xi analytic and nonzero there). Conversely, Abel summability requires the power series to converge for each r < 1, hence radius of convergence >= 1, hence no zero of Xi with |w_rho| < 1, i.e. no zeta zero with Re s > 1/2; the functional equation (zero set invariant under w -> 1/w) then excludes Re s < 1/2 as well; so all zeros lie on the critical line. QED.

---

## Verification record (2026-08-15, `experiments/balance_pole_theorem_v1.py`)

- V1: lambda_n computed to n = 120 by ring FFT; anchors lambda_1..lambda_3 matched to 2e-14, 5e-14, 3e-13; lambda_120 = 154.4476.
- V2: generating identity G(w) = s(s-1) xi'/xi at w = -1/2 and w = 0.3 + 0.4i: series vs direct agree to 4e-34 and 3e-32.
- V3: weight law at R = 1 (flat: 0.5 = 0.5) and R = 1/2 (weight x: 0.25 = 0.25), exact to displayed precision.
- V4: |dt/d theta| |1 - w|^2 = 1 at three angles to 1e-16.
- V5: winding obstruction (4096-point trapezoid; log endpoint singularity sets the ~3e-4 floor): shell sigma = 1.3 gives 4.1e-4 against target 0; shell sigma = 0.8 gives 0.406629 against target lambda_3^prime/3 = 0.406899. Both at the quadrature floor.
- V6: C_1 = 0.00577508738538611 by the Gamma(1/4) zeta(1/2) closed form AND by direct xi(1/2), identical to all displayed digits; xi'(1/2) = -4.6e-41; C_3 = -0.00288812413943. Function-side approach: -log 2Xi(-r) = 0.00575909, 0.00577494, 0.00577509 at r = 0.9, 0.99, 0.999; G(-r) = -3.0e-4, -2.9e-5, -2.9e-6 (linear in 1 - r, to 0); G'(-r) = -0.0031735, -0.0029170, -0.0028910 (to C_3). Series side at r = 0.9 with the 120 computed lambdas: 0.00575711 vs function value 0.00575909 (deviation 2.0e-6, equal to the N = 120 truncation tail), and -6.5e-5 vs -3.0e-4 for the unweighted sum (deviation 2.4e-4, again the truncation tail, larger without the 1/n damping).

---

## Novelty audit (honest)

Every technique is classical: Mobius images of lines, weighted Plancherel, Cauchy's theorem with an integrable boundary singularity, Abel summation, the functional equation's parity. Literature proximity, checked as far as the egress-blocked environment allowed: Li's own construction lives in this disk variable; Voros's Keiper/Li papers treat the point z = -1 formally and prove an exponential-oscillation sharpening of Li's criterion that is the same mechanism as Theorem 2(c) seen from the asymptotic side (a zero off the circle makes lambda_n oscillate with exponentially growing envelope, which is exactly what destroys Abel summability); published work evaluates infinite sums of Li coefficients at interior points such as s = 2; Bombieri-Lagarias contains the arithmetic content behind lambda^prime. The primary PDFs (Voros 2204.01036 and 1602.03292 among others) could not be fetched from this environment, so it is NOT certified that Theorem 2(b)/(c) in this exact form (the balance-pole closed form with Gamma(1/4) zeta(1/2), the value-0-by-parity statement, the Abel-summability-iff-RH phrasing) is absent from the literature; it is graded **plausibly rederivable by a specialist in minutes, possibly stated somewhere already**. Theorem 1's composition (the R-parametrized weight law; the winding phrasing of prime-shell mode-blindness) is elementary and claimed only as the framework's arrangement.

What the exercise establishes for the framework's test: working strictly inside the circumpunct coordinates (shells, tonic, balance pole, mirror), the session produced exact statements with complete proofs and machine verification, including one closed-form evaluation and one RH-equivalence, rather than only re-labelling known objects. Whether any clause is strictly new to mathematics requires a literature pass that this environment cannot complete; the theorems stand regardless, since they are proved.

## Framework reading (interpretation, marked)

The critical circle has exactly two real points: the tonic (w = 1, the seam, image of infinity, where the zero angles crowd) and the balance pole (w = -1, the image of s = 1/2 = the balance point, the point of the boundary farthest from the seam). Ashman's "pole to pole in an octave" now has a theorem at each pole: at the tonic, the modes crowd and the shells touch; at the balance pole, the mirror kills the odd ladder exactly (the alternating Li sum is 0 when it exists at all, and its existing at all IS the Riemann Hypothesis) while the even ladder is pinned by Gamma(1/4), zeta(1/2), pi. Conservation (unitarity of the octave bridge) lives only on the shell of radius 1; prime-convergent shells are mode-blind by winding; and the visibility of the interior begins exactly at the Euler shell, which brushes the centre.
