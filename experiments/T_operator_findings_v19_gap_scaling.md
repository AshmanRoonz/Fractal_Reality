# T-Operator Findings v19: Gap Scaling Between the Two Scales

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0

Companion code: `unified_expression_T_v19_gap_scaling.py`
Context: v18's open item (how does the whole-tone gap-opening scale along a continuous interpolation between the canon and whole-tone stroke fields?).

## The instrument

The two stroke fields differ by a mod-4 count difference δ(J) that is exactly 56-periodic, so the interpolation ph_s = i^{m_canon}·e^{iπsδ/2} is cell-periodic for all s (the naive blend of raw counts is not: 32 vs 28 strokes per cell leaves a stray flux; this is itself a small lesson: the two fields are joined by a periodic path only through the difference field). Canon at s = 0, whole-tone at s = 1; branch convention δ ∈ {−1, 0, 1, 2} flagged.

Two failed observables are reported for honesty before the clean one: the global minimum gap hops between different crossings as s changes (56 bands ≈ 23 distinct near-crossings), and window-based tracking slides between neighbors; neither has a single scaling law. The clean instrument is degenerate perturbation theory at ONE crossing: dT/ds at s = 0 projected onto the crossing pair's 2D space with biorthonormal left/right eigenvectors, verified by pair-identity tracking (projection onto the crossing plane).

## Findings

**F1 (grade A): the gap opens linearly, with the coefficient predicted by first-order perturbation theory.** At the reference crossing (q_c = 4.2477), the projected 2×2 predicts gap(s) = 0.28582·s + O(s²); pair-tracked numerics give gap/s = 0.2763, 0.2739, 0.2657 at s = 0.002, 0.005, 0.01 (ratio to prediction 0.97 at the smallest s, converging), bending down at larger s as second-order effects set in. So the whole-tone field couples canon's protected crossing pairs at FIRST order: ν = 1, the generic symmetry-breaking law, now measured rather than assumed. Together with v18: the −i flux's gap-opening is a first-order effect of breaking octave translation, not a threshold or higher-order phenomenon.

**F2 (dismissed candidate, by the scatter test).** The reference crossing's slope 0.285819 sits 0.04% from Φ/R = 2/7, within the intrinsic ambiguity set by the crossing's generic complex miss distance (complex eigenvalue curves in a 1-parameter family avoid exact degeneracy; miss ≈ 5.5e-5). Discriminator: slopes at six distinct crossings scatter as 0.190, 0.263, 0.286, 0.356, 0.673, 0.971 with no clustering on pool fractions. With ~23 crossings each getting a chance, one landing within 0.04% of some simple fraction is expected noise. The 2/7 candidate is dismissed; the coefficients are crossing-dependent and non-universal; only the linear law is universal. (Same discipline as v17's exclusion of π·29/80: the density caveat doing its job, twice in one day.)

**F3 (small structural lesson).** Complex "crossings" of the folded bands are generically near-misses, not exact degeneracies (codimension 2 in the complex plane vs 1 sweep parameter); canon's protection makes them close (1e-5 to 1e-4), not exact. v18's language of "protected crossings" should be read as "protected near-crossings" at finite α.

## Status of the i-thread

With v19 the operator side of the i-thread (v16 → v17 → v18 → v19) is closed as planned: chirality has its observable (circulation direction), q* is derived (Rayleigh argmax theorem, no elementary closed form), the whole-tone flux disconnects the ascent by first-order gap-opening, and the coefficients are non-universal while the laws (α-independence of q*, ν = 1) are. Remaining open items (§8.4 physical measurable; φ^3.5) need input other than more operator runs.

## Revision history

- 2026-07-18 v1.0: initial (periodic interpolation path via the difference field; linear gap onset confirmed with perturbation-predicted coefficient; 2/7 candidate dismissed by scatter; near-miss structure of complex crossings noted).
