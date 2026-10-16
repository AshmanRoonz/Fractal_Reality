# T-Operator Findings v21: The Seam-Modulated Chain, and the 720 Test

Created: 2026-10-16
Last updated: 2026-10-16
Version: 1.0

Companion code: `unified_expression_T_v21_seam_modulated.py` (raw output: `v21_output.txt`, about 3 minutes; the 35-parameter search: `--optimize`, logged in `v21_optimize_output.txt`, about 26 minutes)
Context: v20 (`T_operator_findings_v20_self_similarity.md`) found the homogeneous staggered chain not dynamically self-similar, R ∘ F^m ≠ F ∘ R under every corpus scale map, and its §4 turned the two obstructions into a specification: let the seams carry the coarse station pattern, recursively. This experiment builds that chain. During the run Ashman added a reading of his own (2026-10-16, in session): *"the point is a process at the next scale, in the staggered octave model, but then another scale again and it's a structure again... that's the 720."* §2 turns that sentence into tests, reported as F7. Operators reuse v14 (`Xorzo/t_operator.py`, StaggeredOperator), v16 (sync ring), v18 (whole-tone strokes) and v20 (metric, maps, nulls), each re-verified at startup. Station labels are continuation coordinates (v14+ convention). No canon file is touched.

## Summary

**Null again, and the obstruction is now located.** The seam-modulated chain removes both of v20's obstructions (it has no octave translation symmetry and no lattice momentum), yet it is still not self-similar. The corpus instances give defects of 0.89 to 1.00 (0 = exact, 1 = uncorrelated) at every m from 1 to 8, at depths L = 1 to 3, and do no better than random maps of the same shape. 0 of 48 cells pass v20's pre-stated rule. A 35-parameter search for the best possible seam modulation reaches a constrained family ceiling of 0.70 (0.67 for per-node maps), and the same search reaches 0.69 to 0.79 against unrelated random coarse targets, so its gain is fitting capacity.

An exact identity explains the pattern for any projection-type coarse-graining: δ² = 1 − |⟨F_c, R F^m R†⟩| / N_c. Self-similarity therefore needs R's row space to be nearly invariant and the compressed dynamics to equal the coarse one, and no map tested achieves both. The coarse octave's generator also couples non-adjacent stations (80 to 82% of its squared weight two or more stations apart). A chain of octaves meeting only at tonics cannot generate that at leading order, even with slow seams.

**The 720 test.** Read as the parity double cover (§27.7t.5: one scale step moves a point by 3.5D to process parity, two steps by 7D = R back to structure), Ashman's sentence predicts self-similarity at two scale steps rather than one. It does not appear. Two-step maps give the same defects as one-step maps and as random maps on the canon and seam-modulated chains. The canon attractor sits closer to the two-step fixed points (2.3° off, against 5.2° at one step) but not on one. The whole-tone reading, where the parity flip is dynamical, is less self-similar than canon. The reading closest to the sentence, each octave's closing point a coarse process and its body a coarse structure, gives the canon its best showing in any test (7th percentile of random octave blocks), short of the 1% rule and far from small.

**A correction to v20.** v20's station-dependent ceilings (F6) were reached by maps that shrink some coarse rows toward zero. Holding every coarse node at unit norm raises them (0.632 to 0.742 for 56 weights). v20 is updated to v1.1 with a dated correction; its conclusions stand.

## 1. The construction

**Roles.** On a ring of 7^L octaves, seam j (the tonic shared by octaves j−1 and j) carries a role: the coarse station it first becomes under repeated tonic decimation, which is the first nonzero base-7 digit of j (the top seam, j = 0, has role 0). On the 49-octave ring the roles read 0123456 1123456 2123456 3123456 4123456 5123456 6123456. Seams 1 to 6 become the coarse stations ⊛′ to ○′ of the first coarse octave, and seams 7, 14, …, 42 are coarse tonics whose own roles appear one level up. Under tonic decimation seam 7J goes to coarse seam J with the same role, so the coarse ring (7^(L−1) octaves) is the same construction one level up. This is the standard hierarchical labeling, and it is what "the seams carry the coarse station pattern, recursively" means.

**What the role modulates.** Octave k opens at seam k and completes into seam k+1. Two corpus instances, neither with a free parameter:

- **Role strokes.** An octave that completes into a processual coarse station (⊛′, ⎇′, ✹′; residues 1, 3, 5) carries that station's canon stroke (i¹, i², i³) on its completing beat, in place of the canon i⁰. Structural roles and the tonic keep i⁰. This follows the canon convention "one stroke per processual residue class": a completed octave takes the role of one station, and a processual station's identity is its stroke.
- **Role gates.** The same strokes, applied as a phase on the shared seam node once per cycle; the beats stay canon.

**The general family (35 parameters).** Per role: a phase and a gain on the completing beat, a phase and a gain on the opening beat, and a seam gate phase. The `--optimize` mode searches it (Powell from three corpus starts and three random starts on the unconstrained ceiling, then a constrained refinement from the best point; seed and procedure in the script).

**New instruments.** A fast exact family optimizer built from entry-level Gram identities (it reproduces v20's family optima to 1e-6), and a constrained optimizer that keeps every coarse row at unit norm (block-wise majorize-maximize ascent). The unconstrained optimum may shrink hard-to-match coarse rows toward zero. A coarse-graining has to keep every coarse node, so the constrained ceiling is the honest one. It is always bracketed by the unconstrained and the row-normalized values, as E0 checks.

## 2. Ashman's 720, made testable

The sentence fits §27.7t.5 and wrap lemma §8.4 exactly. The tonic is ⟳ of the octave below and • of the octave above. A point at coordinate 0 has structure parity, the next scale's point sits at 3.5 (process parity), and two scales up it sits at 7D = R (structure again): a double cover in which 360° flips and 720° restores, the spin-½ shape the corpus already flags. v20 and E2 to E8 compare scale n with scale n+1 only, so the 720 version is a test they did not run. Four forms (E9):

- **(a) Attractor arithmetic.** One step sends the attractor's phase advance per octave q to 7q, two steps to 49q. Self-similar attractors need 6q ≡ 0 (one step) or 48q ≡ 0 (two steps); a one-step flip with a two-step return needs 7q ≡ q + π.
- **(b, c) Two-step maps** on the canon ring and on the seam-modulated chain: scale n straight to scale n+2 (one level-2 station per seven fine octaves).
- **(d) The whole-tone reading**, the one construction in the corpus where the parity flip is dynamical (strokes anchored to odd coordinates, v18). Canon's strokes are anchored to residues, so its dynamics cannot see coordinate parity.
- **(e) The reading closest to the sentence.** Each fine octave becomes two coarse stations, its body a structure and its closing point a process (ratio 3.5). Fine closures then land on coarse processes in one coarse octave and on coarse structures in the next, returning after two coarse octaves: the double cover inside the coarse-graining itself.

In canon, any sign twist, half-step frame shift or relabeling at one step is absorbed into R, and the per-node families already cover it. That is why the new content is the two-step map and the ratio-3.5 map.

## 3. Findings, graded

**F1 (null result, robust): the seam-modulated chain is not self-similar.** Corpus instances at L = 2 (sequential composition, the StaggeredOperator convention), m = 4 and m = 8 (full rows in `v21_output.txt`, E2):

| modulation | R_dec, m = 4 | R_dec, m = 8 | R_whole, m = 4 | R_whole, m = 8 | R_unif, m = 4 | R_unif, m = 8 |
|---|---|---|---|---|---|---|
| homogeneous (v20 chain) | 0.980 | 0.952 | 0.960 | 0.957 | 0.966 | 0.936 |
| role strokes | 0.996 | 0.983 | 0.990 | 0.997 | 0.955 | 0.970 |
| role gates | 0.974 | 0.976 | 0.960 | 0.993 | 0.940 | 0.990 |

Over m = 1..8 the corpus instances lie in [0.893, 0.998] on both compositions and at L = 1. At L = 3 (343 fine octaves, 2401 nodes) they give 0.959 to 0.998. T tracks F to within 0.002. Against the nulls (200 Haar co-isometries, 200 random decimations, 200 random block weights, six wrong-residue decimations), 0 of 48 cells pass. The only two cells below every null are R_whole at m = 1 (0.921 and 0.893): v20's frozen-image effect, not structure. Thirty random 35-parameter modulations give a constrained ceiling of 0.843 ± 0.013 (minimum 0.814, on a slightly coarser phase grid); role strokes (0.812) is level with the best of them and role gates (0.748) is better. Neither corpus modulation beats the unmodulated chain (0.738).

**F2 (grade A, exact): v20's obstructions no longer apply, and conservation holds.** The modulation breaks octave translation invariance by a relative 0.59 to 0.98 for a one-octave shift and 0.22 to 0.41 for a seven-octave shift. The unmodulated sync ring is invariant to 5e-16. So v20's Theorem 1 (which needs exact octave invariance) and Theorem 2 (which needs a lattice momentum) have no purchase here, and whatever fails, fails for another reason. The modulation keeps v14's conservation: the departure (|λ₁| − 1)/α is 0.58 to 0.83 at both scales.

**F3 (grade A for the identity, B for the measured trade-off): every local coarse-graining leaks or freezes.** For a co-isometric R with row space V and compressed dynamics M = R F^m R†, the defect obeys exactly δ² = 1 − |⟨F_c, M⟩| / N_c, verified here to 3e-16. Since |⟨F_c, M⟩| ≤ N_c √(1 − ℓ²), where ℓ² is the share of V's squared amplitude that leaks out of V in m steps, δ² ≥ 1 − √(1 − ℓ²). Self-similarity therefore needs V nearly invariant AND M close to a phase times F_c. At m = 4 the fixed corpus maps leak heavily (ℓ = 0.85 to 0.92) and their compressed dynamics hardly align with F_c (cosine 0.02 to 0.22). The best maps found trade one against the other and stop well short of both: the constrained per-node optimum for the searched modulation leaks ℓ = 0.63 and aligns at cosine 0.70, giving δ = 0.68. The near-eigenmode readout (R_whole) is the low-leakage end at small m, and there M is close to a pure phase: the frozen image.

**F4 (grade B): honest family ceilings, and the octave still does no work.** With every coarse row at unit norm (L = 2, m = 4), the best local coarse-grainings reach 0.738 (station-dependent, 56 weights) and 0.732 (per-node, 392 weights) on the unmodulated chain, and 0.737 to 0.812 with the corpus modulations. Translation-covariant windows stay at 0.86 to 0.93. The canonical octave is not special: random 8×8 octave blocks with the same geometry give 0.744 ± 0.020 (canonical at the 40th percentile), 0.762 ± 0.018 at v20's size (canonical at the 30th), and 0.759 ± 0.017 with role gates (canonical at the 33rd).

**F5 (grade B): the best seam modulation is fitting capacity.** The search lowers the unconstrained ceiling from 0.642 to 0.574 (0.578 to 0.639 from the other starts). The constrained refinement reaches 0.700 (per-node 0.670, from 0.732 unmodulated). The same search aimed at coarse rings built from unrelated random octave blocks gains as much (0.544 to 0.507, 0.717 to 0.632, 0.731 to 0.617) and ends at constrained values of 0.693, 0.786 and 0.753. The true target's constrained value at the same stage (0.727) sits inside that range. The optimum is stable across depth (L = 1, 2, 3: 0.615, 0.700, 0.694) and composition (sync 0.707), and its parameters show no role pattern: completing-beat phases all negative (−0.13 to −0.53 π), gains above canon (1.03 to 1.54), seam-gate phases scattered. Fixed maps on the best modulation stay at 0.88 to 1.00.

**F6 (grade B−): the coarse octave is non-local along the chain.** Octaves that meet only at shared tonics generate, at leading order in a weak seam coupling, a coarse dynamics whose generator couples neighbouring stations only. With slow seams (coupling ε), interiors couple through a tonic at O(ε²) to adjacent octaves and only at O(ε⁴) beyond. The coarse operator's own generator (principal logarithm) is the opposite: 66% of the squared weight of log F₈ couples stations two or more apart (the hub couplings), and on the 7-octave coarse ring 0.82 sits at distance two or more and 0.49 at distance four or more (0.80 and 0.47 with role strokes). So time-scale separation, the one regime the m = 4 search could not reach, cannot produce F_c either. The profile is exact; the leading-order argument is standard perturbation theory, with the caveat that another branch of the logarithm could in principle redistribute weight.

**F7 (null result; grade A for the arithmetic): the 720 test.**

- *(a) Attractor arithmetic.* At the measured α, q* = 0.362110π is 5.18° from the nearest one-step fixed point (π/3) and 2.32° from the nearest two-step fixed point (9π/24); in the α → 0 limit (v17) the offsets are 5.25° and 2.25°. The two-step grid is finer and q* sits closer to it, but not on it. The one-step-flip condition (7q ≡ q + π) misses by 24.8°.
- *(b) Canon, two steps.* Composing two tonic decimations gives 0.940 to 0.993 for m = 1 to 64 (m = 16 and 64 included for squared time dilation). Composing two whole-mode maps gives 0.908 to 0.970. Haar maps of the same shape give 0.936 to 0.993. The symmetry floor for any translation-covariant two-step projection is 0.500, as at one step. On the finite rings used, the discretized momenta happen to coincide (49 q_f = Q_c = 0), and the attractor overlap there (0.434) is at the within-sector chance level (0.340 ± 0.164).
- *(c) Seam-modulated chain, two levels* (343 fine octaves to 7), two-step decimation and composed whole-mode maps together: 0.901 to 0.994 (unmodulated), 0.929 to 0.996 (role strokes), 0.905 to 0.998 (searched modulation).
- *(d) Whole-tone reading.* Less self-similar than canon on the same builder and sizes: constrained ceilings 0.865 (m = 1) and 0.895 (m = 4), against canon's 0.760 and 0.741. Its own return takes eight octaves (the −i holonomy, v16), not two.
- *(e) Body plus closing point (ratio 3.5).* Fixed map 0.934 to 0.992. Per-node constrained ceiling 0.592 to 0.632, the lowest in this study, but random octave blocks with the same geometry reach 0.632 ± 0.020 (minimum 0.580), and the canonical octave sits at the 7th percentile. That is the canon's best showing in any test here: suggestive, short of the 1% rule, and far from small. The map's symmetry floor is 0.505, and its attractor condition (7q = 2q) misses by 6.8°.

The geometry in the sentence is real: points do alternate parity from scale to scale. But the canon dynamics, with strokes anchored to residue, does not see coordinate parity. The construction that does see it is less self-similar, and the two causes in F3 and F6 do not depend on the number of steps.

**F8 (null): the attractor does not map to the attractor.** With no momentum on the modulated chain, the test is direct. Overlaps |⟨ψ_c, R ψ_f⟩| at L = 2 are 0.006 to 0.214 against a random-vector chance of 0.12 to 0.13 (± 0.07). The fine attractor's phase advance across seven fine octaves differs from the coarse attractor's advance per coarse octave in every case (for example −0.771π against +0.362π unmodulated, and +0.157π against +0.405π for the searched modulation).

**F9 (grade A, recap): the tensor-nesting null is unchanged.** δ(m) = √(1 − |tr F₈^{m−1}/8|^{depth−1}): exact at m = 1 (separable), compounding toward 1 with depth for m ≥ 2 (v20 F7).

## 4. What this says (readings, flagged)

*Reading, grade C: the obstruction is not symmetry.* v20's two theorems were sufficient reasons for its null, and they are gone here, yet the null remains. What remains is the leak-or-freeze dilemma of F3 together with the locality mismatch of F6, and neither depends on the number of scale steps. Both apply to any chain whose octaves mix every station at full strength each cycle (θ = π/2) and talk to each other only through shared tonics. A local coarse-grained subspace either loses most of its amplitude within a few cycles, or is nearly invariant because it sits on a near-eigenmode (and then its dynamics is close to a pure phase), or trades the two and stops short of both: the best maps found still leak about 40% of their squared amplitude in four cycles and align with F_c only at cosine 0.6 to 0.7.

*Reading, grade C: what could work, if anything.* Self-similarity would need a fine dynamics with an octave-local protected channel whose induced dynamics is the coarse octave's, including the hub couplings that tie non-adjacent coarse stations together (F6). On a chain those couplings would have to be carried by long-range seams: each coupled pair of coarse stations bridged by a fine octave whose two tonics are those stations, as in the hierarchical lattices of renormalization theory. That is a change of geometry (a graph, not a chain), beyond seam modulation. The corpus already uses a non-chain topology in the Xorzo octave tree. Not built or claimed here.

*Reading, grade C: on the 720.* The parity double cover is a real feature of the staggered geometry, and the sentence states it well. In this operator it stays bookkeeping, as §27.7t.5 already says of canon ("residue fixes identity; parity is octave-relative"). Making it dynamical (the whole-tone reading) costs self-similarity rather than buying it. If the 720 is to carry dynamical weight, it has to enter through a construction that is not yet in the corpus. The ratio-3.5 map, the canon's best showing, is the place to look first.

*Bearing on the framework (unchanged from v20 §4).* The staggered octave as built is scale-homogeneous. Seam modulation, the natural way to make the parts carry the whole's pattern, does not make it dynamically self-similar at one scale step or at two. CLAUDE.md open decision 2 is unaffected beyond v20's note.

## 5. Scope and open items

- The family modulates whole opening and completing beats and adds a seam gate. It does not add new couplings at the tonic (for example a tonic coupled to stations other than its beat partners and hubs), which belong to the geometry change in §4.
- The search ran at L = 2, m = 4 on the station-dependent family. Its optimum was then checked at other m, depths, compositions and on per-node maps (F5), but a search aimed at m = 8, at two-step maps or at the ratio-3.5 map was not run.
- The 720 tests use the canon, seam-modulated and whole-tone constructions. A construction that makes the parity flip dynamical while keeping canon's stroke table at every scale was not found or built.
- The ratio-3.5 map's 7th-percentile showing is the one result worth repeating with more random blocks (15 here) and at larger sizes.

## Revision history

- 2026-10-16 v1.0: initial. Seam-modulated hierarchical chain built (roles = first nonzero base-7 digit; corpus instances role strokes and role gates; 35-parameter family and committed search); null under every corpus map and the searched modulation (0 of 48 cells pass; best constrained ceiling 0.67 to 0.70, inside the capacity null); exact leakage identity; locality profile of the coarse generator; the 720 test (two-step maps, attractor arithmetic, whole-tone reading, ratio-3.5 body-plus-closure map) at Ashman's prompt: null in every form; constrained-ceiling correction to v20 F6.
