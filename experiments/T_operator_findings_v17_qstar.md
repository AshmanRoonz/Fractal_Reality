# T-Operator Findings v17: The Momentum of the Ascending Fixed Point

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0

Companion code: `unified_expression_T_v17_qstar.py`
Context: v16's F2 (leading mode at q* ≈ 0.3621π, α-independent, open item "identify q* analytically").

## Result: q* is now DERIVED as the argmax of an explicit α-free landscape; it is NOT elementary in closed form, and the high-precision value excludes every near-match tested.

**F1 (grade A): the perturbation theorem.** T(q) = (I + αB(q))F(q) with F(q) unitary, so for each simple eigenpair of F, (|λ_b| − 1)/α = ⟨u_b(q)|B(q)|u_b(q)⟩ + O(α): the band-modulus landscape is the Hermitian bond matrix B read in the four-beat eigenbasis, with no α anywhere. Validated numerically: error shrinks ×15.5-16.0 as α → α/16 at four test momenta (clean O(α) scaling). v16's observed α-independence of q* is therefore a theorem: q* = argmax over bands and momenta of the Rayleigh quotient β_b(q), a pure property of the beat geometry.

**F2: the pinned value.** q*₀ = 1.138788503361 rad = **0.362487638892 π**, with β(q*₀) = 0.681741 (matching v16's measured (|λ|−1)/α → 0.6812 at small α).

**F3 (negative, honest): the frozen-seam story fails quantitatively.** The only q-dependence in B is the one bond crossing the tonic seam, so β_b(q) = intra + 2Re(e^{iq}·conj(u_b[3])·u_b[0]); if the eigenvector were q-frozen, q* would equal the phase the leading amplitude picks up crossing the seam. It does not: frozen estimates give 0.700π (from q = 0) and 0.815π (from q = q*), and even the self-consistent first harmonic of the tracked band's β curve peaks at 0.230π, all far from 0.3625π, despite the first harmonic carrying 91.6% of the AC power. The eigenvector's own q-dependence (the beat generators also carry seam entries) dominates the argmax. The seam reading survives qualitatively (all momentum dependence enters through the tonic seam, in κ and in F), not as a formula.

**F4 (identification hunt: negative at precision).** Best candidate π·29/80 sits 3.9e-5 rad away (0.003%) but is EXCLUDED: q*₀ is computed to ~1e-12 and the discrepancy is real. Everything else tested (π/e, arctan(2), arctan(√2), hub-angle combinations, all eigenphase differences of F(0)) is ≥ 0.4% off. Verdict: q* has no elementary closed form in the tested library; it is a genuinely computed geometric angle of the beat product, now derived (F1) but not named. The density caveat was applied throughout: rational π-multiples prove nothing without a structural derivation, and the one that came close failed at precision, which is exactly what the caveat predicts for numerology.

## Status

The v16 open item "identify q* analytically" is half-closed: derived as an argmax (theorem), not identified as a closed form (and the obvious candidates are excluded rather than merely unconfirmed). Further closed-form hunting is low priority; the theorem is the usable result.

## Revision history

- 2026-07-18 v1.0: initial (perturbation theorem validated; q*₀ pinned to 12 digits; frozen-seam approximation quantitatively rejected; closed-form candidates excluded at precision).
