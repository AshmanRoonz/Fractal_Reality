# T-Operator Findings v14: The Staggered-Octave Chain

Created: 2026-07-16
Last updated: 2026-07-16
Version: 1.0

Companion code: `unified_expression_T_v14_staggered_chain.py` (raw output: `v14_output.txt`)
Framework context: §27.7t (staggered octave), §27.7s (T = κ ∘ F), docs/octave_wrap_lemma.html §8.

## What was built

Prior multi-scale operators (v11, ℂ⁶⁴) modeled scales as tensor factors: 24 stations, nothing shared. The staggered octave says adjacent scales share exactly one station, the tonic (3.5D = 0D′). v14 builds that geometry directly: n octaves as 8-station blocks (v9's ℂ⁸ construction per block) on the continuation lattice, sharing tonic nodes. Two topologies: the open chain (7n + 1 nodes; has edges) and the ring (7n nodes, tonic-closed; translation-invariant spectrum, the clean instrument).

## Findings, graded

**F1 (grade A): tonic-sharing conserves the 1; departure does not accumulate with scale count.** On both chain and ring, the departure from trace preservation stays at (|λ₁| − 1) ≈ 0.60-0.79 α for every octave count tested (n = 1-8 chain, n = 2-9 ring), with no growth trend. Contrast the tensor construction, where departure compounds: ℂ⁸ singular values (1±α)⁴, ℂ⁶⁴ spectral-radius departure 2α. Structural reading: sharing the tonic is what keeps the 1 near-conserved across unbounded nesting; the staggered geometry implements the framework's lateral-closure claim ("⊙λ ⊂ ⊙Λ ⊂ ∞ = 1 at every step") dynamically, where tensor nesting does not. This is the experiment's main positive result.

**F2 (grade B+): operator-level witness of the single-period lemma.** Adding a forbidden second-period coupling (bonds at the 4D offset, 8 half-steps) flattens station distinguishability (mean residue-profile variance across ALL eigenvectors) to 0.41-0.49 of baseline by g ≈ 0.5-1.0, while the commensurate control (bonds at 7 half-steps, tonic-to-tonic) holds at 0.72-0.82 over the same sweep. The forbidden period degrades the ladder roughly twice as fast as the commensurate one, in the direction the single-period lemma predicts. Caveat: the flattening saturates near 0.41 rather than reaching 0 (residual hub and α structure); the lemma's full collapse is a statement about exact periods, and the finite-coupling operator only approaches it.

**F3 (grade C): the 69/31 split brackets but does not converge.** Ring splits fluctuate with n: structural residues 43.5-64.4%, processual 28.3-38.3%, tonic class 7.3-19.0%. At n = 4, assigning the double-natured tonic class half-and-half gives 68.0/32.0 (0.7 points from ℂ⁸'s converged 68.7/31.3; 1.1 from the cosmological 69.11/30.89), but other n values land elsewhere. The fluctuation tracks eigenvalue crossings as n changes. No convergence claim is made; the split is bracketed, not reproduced.

**F4 (null result): no parity double-cover mode at α coupling.** The probe: period-2 octave components of the top 2n eigenvectors on rings of n = 2-9 octaves. Even rings (where pure alternation is possible) show components ≤ 0.066, decaying with n. Odd rings show larger values (0.37, 0.23, 0.16, 0.13 for n = 3, 5, 7, 9) but these track the trivial alternating-sum artifact of odd counts (≈ 1/n: 0.33, 0.20, 0.14, 0.11) and are not evidence. Conclusion: the parity double cover of §27.7t.5 does NOT manifest in this observable at α coupling. Sharper next instrument: momentum-resolved (Bloch-sector) analysis of the ring spectrum, comparing the q = π sector against q = 0; a genuine double-cover content would appear as a systematic spectral feature at antiperiodic momentum.

**F5 (attractor unique; the "ground floor" was finite-size, see v15).** 30 random initial conditions converge to the eig fixed point to 1.3e-6 (robust). The open-chain localization on the lowest octave (n = 4 shares: 0.569, 0.137, 0.080, 0.214) was originally flagged as a possible structural "foam floor." **v15 retires that reading:** at n >= 6 the profile becomes a centered dome (open-boundary standing wave, box scaling n x max-share -> 2.07), so the floor at n = 4 is a small-box edge artifact, not a privileged scale; A3 (no fundamental level) holds dynamically for the canonical operator. A genuine skin effect appears only under reversed (descending) beat order and is set by pump order, not i-chirality. See T_operator_findings_v15_ground_floor.md.

## Construction choices (conventions, not results)

Per-octave beats mirror v9's ℂ⁸ exactly (Φ/✹ hub, θ = π/2, hub coupling θ/T). Beat product is ascending (octave 0 first); on the ring, cyclic reordering preserves the spectrum, so this is inert there. κ carries the four per-octave diameter bonds at α (v9's κ₈ per block); the cross-scale tonic bond is realized by node sharing plus the two adjacent octaves' diameter bonds meeting at the shared node. A parameter-robustness sweep in the style of v13 is deferred to a follow-up.

## Revision history

- 2026-07-16 v1.0: initial; five findings graded A, B+, C, null, robust.
