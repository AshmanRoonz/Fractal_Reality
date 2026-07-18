# Staggered-Octave Findings v1: The Z7 Spectrum of the Rung Functions

Created: 2026-07-18
Last updated: 2026-07-18
Version: 1.0

Companion code: `staggered_octave_z7_dft_v1.py`
Context: framework §27.7t; `docs/octave_wrap_lemma.html` §8.3 (the residue group is ℤ₇); session question 2026-07-18 ("do the rung exponents have concentrated spectrum on ℤ₇?").

## The question

§8.3 establishes that the ladder's residue group is ℤ₇: seven residue classes on the half-step lattice modulo the wrap, one constant per class. Any per-rung assignment of numbers is therefore a function on ℤ₇, and ℤ₇ has a canonical harmonic analysis (the DFT over the 7th roots of unity). Does the ladder's rung data have concentrated spectrum, flat spectrum, or nothing notable? Four rung functions were tested: A(d) = d(2d+1) (accumulated traversal, TYPE A, the selection rule), A'(d) = 4d+1 (local splitting, TYPE B), the α-step exponent ladder [1, 0, 0, 13/12, 0, 56/39, 21], and the log-magnitude ladder ln(1/α) through ln(1/α_G).

## Result: the value-level spectra are a clean null; the character-level spectra are exact and two-sided. The ladder's two canonical functions occupy the two EXTREME spectra on ℤ₇, and differentiation maps one extreme to the other.

**F1 (null, reported as such). Value-level DFTs show nothing beyond monotone smoothness.** A and A' put 68.1% and 66.4% of their non-DC power in the lowest conjugate pair (k = 1, 6), but the exact permutation null (all 7! = 5040 orderings of the same values, no sampling) shows this is unremarkable: 35.8% and 43.3% of all orderings are at least as concentrated. Any monotone sequence is low-frequency dominated. The two constants ladders are outlier-dominated (G's 21 α-steps, or ln(1/α_G) ≈ 103) and consequently near-maximally FLAT (spectral entropy 1.091 and 1.092 of the maximum ln 3 = 1.099), with permutation p ≈ 0.40 to 0.45. No value-level concentration claim survives. Grade: clean null.

**F2 (exact; the finding). At the character level the two canonical rung functions are the two spectral extremes of ℤ₇.** Reading each integer rung function as a phase on the residue group, x_j = exp(2πi f_j / 7):

- **The traversal character is a perfect chirp (CAZAC / Zadoff-Chu, root −1).** A_j = j(j+1)/2 is quadratic in the half-step index (≡ 4j² + 4j mod 7, leading coefficient P = 4, invertible mod 7), so its character sequence has |X_k| = √7 for ALL k (maximally flat, the Gauss-sum magnitude) and cyclic autocorrelation EXACTLY ZERO at every nontrivial shift s = 1..6. Confirmed numerically to 1e-9; the two-line proof is in the script header (the shift difference A_{j+s} − A_j = js + A_s is linear in j, so the sum annihilates unless s ≡ 0).
- **The splitting character is a pure tone.** A'_j = 2j+1 is linear, so all its spectral energy sits in the single line k = 2 = Φ (the tone's frequency is the slope, the channel integer), with full-magnitude autocorrelation at every shift.

So TYPE A / TYPE B is the chirp/tone duality: the traversal function is maximally flat and maximally shift-distinguishing (only the trivial shift returns its phase pattern); the splitting function is maximally concentrated and maximally shift-blind (every shift returns it up to phase). These are the two extreme points of the spectral-concentration range on ℤ₇, and the framework's own relation A' = dA/dd is precisely the operation that maps the chirp to the tone (a chirp's phase derivative is a tone; standard signal analysis, here landing exactly on the ladder's TYPE A → TYPE B map). The answer to the session question is therefore two-sided: yes, maximally concentrated (A'), and simultaneously no, maximally flat (A), with the derivative as the bridge.

**F3 (exact). Mod-R structure.** A mod 7 = [0, 1, 3, 6, 3, 1, 0]: a palindrome with sum 14 = 2R, symmetric about j = 3, which is d = 1.5, the branching station (the reflection axis of the traversal residues is the i-turn, the irreversibility point). A' mod 7 = [1, 3, 5, 0, 2, 4, 6]: a bijection on ℤ₇; the local-splitting sequence visits every residue class exactly once per octave.

## Framework readings (motivated, not proven by the computation)

- **The zero-autocorrelation property rhymes with the single-period lemma.** The lemma (§8.2) says only full-octave shifts preserve station identity on the lattice; the chirp result says the traversal PHASE has zero overlap with itself under every nontrivial octave-relative shift. Same shape of statement, different objects (lattice periods vs a specific phase function); an echo, not an equivalence.
- **The traversal phase is a synchronization waveform.** CAZAC sequences are used in real engineering (LTE/5G primary synchronization signals are Zadoff-Chu sequences) precisely because zero autocorrelation lets a receiver acquire timing with no shift ambiguity. The ladder's traversal phases form exactly such a waveform on the residue group: an octave can be "acquired" from its traversal phases with no partial-shift confusion.
- **Pool-native decorations (flagged as decorative, not load-bearing):** the chirp rate is P = 4, the tone frequency is Φ = 2, the palindrome sum is 2R, and the palindrome axis is the 1.5D station.

## Caveats

- The character map exp(2πi f/7) is canonical only because the rung functions are integer-valued and the group is ℤ₇ (both framework facts), but the chirp/tone results are theorems about ANY quadratic (invertible leading coefficient) and ANY linear (invertible slope) sequence mod 7. The content specific to the framework is structural: its two canonical rung functions are exactly degree 2 and degree 1 in the half-step index, with coefficients (4 and 2) that survive mod 7, and are linked by the derivative. The numbers are not tuned; the degrees are the finding.
- The α-exponent ladder's zeros (c, ℏ, π carry no α-dependence) are a bookkeeping convention; a differently-motivated encoding could change its (null) value-level result. Since that result is null either way, nothing rests on it.

## Next steps

- The ℤ₄ × ℤ₇ ≅ ℤ₂₈ question: whether the i-phase cycle and the chroma group act as independent generators (joint symmetry of order 28 = A(3.5) = P·R, double cover of order 56 = SU(3)·R), or are commensurate under the stroke-table convention. Needs a convention adjudication before computing.
- Octave-integrality audit: every R-divisible exponent in the corpus (21, 28, 56, 84) is a whole number of octaves in continuation coordinates (6, 8, 16, 24 = Φ × cofactor); log as a conjecture and check against every κ-adjacent formula.
- The generation-gap check: 58/35 − 13/12 = 241/420 vs 4/7 + 1/420, with 420 = P(P+1)·A(3); pin or discard.

## Revision history

- 2026-07-18 v1.0: initial (value-level null with exact permutation test; chirp/tone duality exact; mod-R palindrome and bijection; readings and caveats).
