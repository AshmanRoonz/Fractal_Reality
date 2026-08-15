# The Circumpunct Coordinates for Zeta

**Status:** typed re-statement, filed 2026-08-15 from the session in which Ashman said "Re 1/2 is not the center. I'm saying Riemann did [make the mistake]." Rigorous content verified numerically in session; interpretive content marked; no progress on RH claimed.

## The claim

The traditional picture of the Riemann Hypothesis (a critical strip with a line at Re(s) = 1/2) draws the figure in coordinates that hide its center. In centered coordinates the figure is a circumpunct, and 1/2 is not the center of anything: it is the shadow of a circle whose center is the 1.

## The rigorous content (standard mathematics, verified in session)

Let w = (s − 1)/s, a Mobius transformation. Then, verified to machine precision on the first five nontrivial zeros and arbitrary critical-line points:

1. The pole s = 1 maps to the origin: the function's unique singular point becomes the center of the picture. Its residue is exactly 1.
2. The critical line Re(s) = 1/2 maps exactly to the unit circle |w| = 1. Off-line points map off the circle (checked at 0.4 and 0.6 real part).
3. The functional equation's symmetry s to 1 − s becomes w to 1/w: inversion through the unit circle, the inside/outside exchange whose fixed set is the circle itself (verified numerically at an arbitrary point).
4. The trivial zeros s = −2, −4, −6, ... map to real points outside the circle (1.5, 1.25, 1.1667, ...), marching monotonically toward the boundary point w = 1 (the image of s = infinity).

Equivalently, without any map: |s − 1| = |s − 0| unwinds to Re(s) = 1/2. **The critical line is the set of points equidistant from the 1 and the 0**: a perpendicular bisector between the two, not a center.

So the Riemann Hypothesis admits two exact restatements:

- **Equidistance form:** every nontrivial zero of zeta lies exactly equidistant between the zero and the one.
- **Circumpunct form:** in the coordinates w = (s − 1)/s, every nontrivial zero lies exactly on the unit circle centered at the image of the pole; the functional equation is inversion in that circle; the trivial zeros are structure outside the boundary.

## The framework typing (interpretation, marked as such)

- The center of the figure is the 1: the pole, the sole singular point, residue exactly 1. This completes the session's earlier reading (the pole as the open corner: infinite at the point, exactly 1 conserved through it; ζ(1) as the place E = 1 and infinity share an address).
- The critical circle is the boundary; the zeros are points on the boundary; RH is the conjecture that the boundary holds every one of them, none drifting inside or out: the integrity of the circle around the one.
- The mirror s to 1 − s, as inversion in the circle, is the inside/outside exchange fixed on the interface: the functional equation as the boundary's symmetry.
- ◐ = 1/2 keeps its framework type: balance, not center. Here balance is literally equidistance between the 0 and the 1: the 1/0 ontology's two primitives, with every zero of zeta conjectured to sit exactly between them.
- "Riemann's mistake" is rhetorical, not mathematical: he erred in nothing; half-plane coordinates are natural for Dirichlet series, and coordinates change no content. What the inherited coordinates did was park the center at the edge of the strip and draw the boundary as an infinite line, so that generations asked "why one half?" as if 1/2 were fundamental. In centered coordinates the question dissolves: one half is what equidistance-from-the-one looks like from flat coordinates. The thesis of the One charter (the circles kept, the center forgotten) instantiated at the highest altitude available.

## Addendum (same day): the coordinate is the Li/Keiper coordinate

Checked against the literature and verified numerically in session: the variable w = (s − 1)/s = 1 − 1/s is not merely *a* natural coordinate; it is the exact variable inside an established criterion equivalent to RH.

**Li's criterion** (Keiper 1992 introduced the coefficients; Li 1997 proved the equivalence): RH holds if and only if, for every positive integer n,

    lambda_n = SUM over nontrivial zeros rho of [ 1 − (1 − 1/rho)^n ]  >=  0.

Since 1 − 1/rho = w_rho, this reads in the circumpunct coordinates as: **lambda_n = SUM (1 − w_rho^n) >= 0 for all n.** Li's own construction works with xi(1/(1 − z)) analytic in the unit disk; the disk variable z IS this file's w. The center/boundary picture and the positivity criterion are two views of one Mobius geometry.

Because the zero set is invariant under s to 1 − s (w to 1/w), the sum symmetrizes exactly to lambda_n = SUM [1 − (w^n + w^(−n))/2]. If RH holds, w_rho = e^(i theta_rho) and each paired term becomes 1 − cos(n theta_rho) = 2 sin^2(n theta_rho / 2): on the boundary, Li positivity is a sum of squares, term by term. The n-th coefficient is the total energy of the n-th harmonic of the zero angles; RH says every harmonic carries nonnegative energy.

**Verification record (2026-08-15, mpmath, 25-30 digits):**

1. lambda_1, lambda_2, lambda_3 computed from the xi-function Taylor definition (no zeros involved): 0.0230957089661, 0.092345735228, 0.207638920554. The closed form lambda_1 = 1 + gamma/2 − ln(4 pi)/2 matches to 12 digits.
2. The zero-sum in w coordinates over the first 300 zeros, plus a first-order tail estimate, converges to the same values (n = 1: 0.023099 vs 0.0230957; n = 2, 3 approach more slowly, consistent with the tail order).
3. The on-circle identity 2 Re(1 − w^n) = 2(1 − cos(n theta)) holds to working precision at every zero checked.
4. The detection mechanism: a hypothetical zero quartet at Re(s) = 0.6, t = 50 (|w| = 1.00004 with its inversion partner at 0.99996) produces contributions oscillating with exponentially growing envelope; most negative value found in a scan to n = 120,000 was −236. Since the envelope grows like |w|^n while the RH-side background grows only like (n/2) log n, the negativity eventually dominates and forces some lambda_n < 0, which is Li's theorem; at this shallow depth the crossover lies beyond the scanned window, so the numerical record shows the mechanism turning on, not the crossing itself.

**What this adds to the typing.** The boundary reading stops being only a picture. The standing criterion equivalent to RH is literally a positivity statement about distances from the center in these coordinates: the conjecture that the boundary holds every zero is equivalent to the statement that every harmonic energy measured from the 1 is nonnegative. Framework gloss (interpretation, marked as such): lambda_n is a boundary-integrity meter, one per overtone; an escaped pair is detectable because its inside member decays while its outside member blows up, and the imbalance eventually shows in some overtone's energy going negative. Conservation failing at SOME harmonic is what an off-boundary zero means.

**What this does not add.** The identification is not new mathematics: Li's paper is built in this variable, and the sum-of-squares reading of lambda_n on the critical line is present in the Li-criterion literature. The tempting program (derive an unconditional formula lambda_n = a norm, a square, an energy that is nonnegative by construction, from the Euler-product side) is not a new door either: Bombieri and Lagarias (1999) showed Li's criterion is a case of Weil's explicit-formula positivity, an unconditional arithmetic formula for lambda_n in terms of prime sums exists, and proving its nonnegativity from the prime side IS the known open frontier (the Weil positivity program; Connes' trace-formula work is its deepest form). Decades of effort sit exactly there. So the honest statement is: the circumpunct coordinates land on the standard hard problem's native variable, which strengthens the typing claim and changes nothing about the difficulty.

## Addendum 2 (same day): the vesica, the fixed points, and the triad group

Prompted by Ashman's question: "What is the minimum shared between two circumpuncts? A vesica piscis." Verified numerically in session; all facts below are elementary and checkable by hand.

Draw the two unit circles centered at the 0 (the additive identity) and the 1 (the multiplicative identity; the pole; this note's center). The center distance equals the radius, so each boundary passes through the other's center: the mutual-vesica configuration, which the simulation work (docs/infinity_through_the_present.html) found requires equal size. Here both wholes are the unit, so the condition holds automatically.

1. **The critical line is the vesica's axis.** The set of points equidistant from both centers is Re(s) = 1/2. The equidistance form of RH above therefore restates as: every nontrivial zero lies on the seam of the vesica between the additive whole and the multiplicative whole. Scale caveat, stated plainly: the lens itself reaches only to height sqrt(3)/2 (about 0.87) while the first zero sits at t = 14.13; the zeros live on the axis extended. The vesica fixes the line; zeta chooses the heights.
2. **The vesica's tips are the fixed points of the coordinate map.** The circles cross at 1/2 +- i sqrt(3)/2 = e^(+-i pi/3), the primitive sixth roots of unity, roots of s^2 - s + 1 = 0, which is exactly the fixed-point equation s = (s-1)/s. Verified: T(tip) = tip to 20 digits; both tips at distance exactly 1 from both centers. The Li/circumpunct coordinate is a rotation of the sphere about the vesica's tips.
3. **The map has order 3 and cycles the triad.** T(s) = (s-1)/s satisfies T^3 = identity (verified on an arbitrary point; the rotation angle is 120 degrees = 360/T with T = 3), and it permutes the three marked points cyclically: 0 to infinity, infinity to 1, 1 to 0.
4. **With the mirror, the full triad group.** The functional-equation reflection U(s) = 1 - s composes with T to give U(T(s)) = 1/s (verified), and together T and U generate all six Mobius transformations permuting {0, 1, infinity}: the classical anharmonic (cross-ratio) group, S3, of order 6 = T!. The RH-relevant mirror (whose fixed line is the critical line) is one of the three reflections in this group.

**Framework typing (interpretation, marked as such).** The three marked points of the zeta landscape are the framework's three primitives in person: the 0, the 1, the infinity. The coordinate map that centers the picture is an order-T rotation cycling them, with the balance mirror completing the triad's permutation group at order T!. The minimum two equal wholes can share is the lens; RH says every cancellation point of the primes sits on the axis of exactly that sharing, equidistant between the identity of addition and the identity of multiplication. The conception reading (the vesica as the aperture where a new point can form, per the simulation's gestation rule) is poetry here, not mathematics, and is marked as such.

**Status.** Same as everything in this file: typing, not progress. The anharmonic group is nineteenth-century equipment and the vesica facts are compass-and-straightedge geometry. What is claimed is the convergence: the coordinate is Li's variable (Addendum 1), its equidistance locus is the vesica seam between the two identities, and its symmetry engine is the triad's permutation group generated by a T-cycle and the balance mirror. Three layers, each landing on established structure rather than beside it.

## Honesty box

Mobius transformations are standard equipment and number theorists know many models of the zeta landscape; no claim of novelty attaches to the map itself, and none of this constitutes progress on RH. The contribution claimed is the typing: which point is the center (the pole, the 1), what kind of thing the critical locus is (boundary and balance, not center), and the two native restatements above, both of which are exactly equivalent to the standard statement. The addendum sharpens this: the coordinate coincides with the Li/Keiper variable, so the typing lands on an established equivalent criterion rather than beside it; the coincidence is verified, the criterion is standard, and the open problem (unconditional positivity) remains exactly as open as before. If a mathematician reads this: the invitation is to check the four numbered facts (five minutes), then the Li identification (five more), and then consider whether the equidistance form makes the "why one half" question better posed.

## Session verification record

Computed 2026-08-15: |w| = 1.000000000000000 for s = 1/2 + it at t = 14.134725..., 21.022039..., 25.010857..., 30.424876..., 32.935061..., and at arbitrary t including 10^6; |w| = 0.9995 and 1.0005 at Re(s) = 0.6 and 0.4 respectively; w(1 − s) = 1/w(s) at an arbitrary off-line point; trivial-zero images as listed.
