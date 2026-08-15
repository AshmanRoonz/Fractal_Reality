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

## Honesty box

Mobius transformations are standard equipment and number theorists know many models of the zeta landscape; no claim of novelty attaches to the map itself, and none of this constitutes progress on RH. The contribution claimed is the typing: which point is the center (the pole, the 1), what kind of thing the critical locus is (boundary and balance, not center), and the two native restatements above, both of which are exactly equivalent to the standard statement. If a mathematician reads this: the invitation is to check the four numbered facts (five minutes) and then consider whether the equidistance form makes the "why one half" question better posed.

## Session verification record

Computed 2026-08-15: |w| = 1.000000000000000 for s = 1/2 + it at t = 14.134725..., 21.022039..., 25.010857..., 30.424876..., 32.935061..., and at arbitrary t including 10^6; |w| = 0.9995 and 1.0005 at Re(s) = 0.6 and 0.4 respectively; w(1 − s) = 1/w(s) at an arbitrary off-line point; trivial-zero images as listed.
