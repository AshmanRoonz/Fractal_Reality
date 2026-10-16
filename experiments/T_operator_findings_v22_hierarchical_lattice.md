# T-Operator Findings v22: The Bridged Lattice

Created: 2026-10-16
Last updated: 2026-10-16
Version: 1.0

Script: `experiments/unified_expression_T_v22_hierarchical_lattice.py` (default run about 12 minutes). Raw output: `experiments/v22_output.txt`. Builds on v20 (`T_operator_findings_v20_self_similarity.md`, v1.1) and v21 (`T_operator_findings_v21_seam_modulated.md`). No canon edits.

## Summary

The change of geometry that v21 §4 called for does not make the staggered octave dynamically self-similar, and the reason is now complete: geometry was never the binding constraint. The obstruction is the leak-or-freeze dilemma alone, and every geometry tested meets it.

v22 builds the hierarchical lattice v21 asked for. Every coupled pair of coarse stations gets a fine octave whose two tonics are those stations, recursively, which gives a family that is self-similar by construction. Four substitution rules were tested:
- the chain, which reproduces v20/v21 exactly;
- the beat lattice: the ten station pairs the octave's four beats couple;
- a parity lattice that carries the six same-parity couplings through two octaves (Ashman's 720 made geometric);
- the complete lattice: all 28 pairs.

All four were tested from level 1 to level 0. The chain, beat and parity lattices were also tested from level 2 to level 1 (lattice to lattice, up to 3482 nodes) and over two scale steps.

- **The corpus maps fail everywhere.** δ runs from 0.899 to 1.000 across 528 cells; none is small, so none passes.
- **Geometry does not move the best local coarse-graining.** It reaches 0.72 to 0.77 for every geometry, within 0.01 to 0.03 of random octave blocks on the same lattice and of random 10-pair geometries.
- **The coupled pairs were the wrong target.** The coarse cycle's generator is dense: the beat pairs carry 22 to 30% of its weight, and all within-octave pairs carry 80 to 84%.
- **Weak seams protect the tonics but freeze them.** The leak falls to 0.14 at ε = 0.05, but the best match at any number of cycles is the frozen channel's identity overlap. The induced generator lies in a four-dimensional span for any geometry (verified numerically). That span can align with the coarse generator to cos 0.12 to 0.28 at best; the canonical bridge reaches 0.02 to 0.06.

Three side results:
- **Conservation holds on lattices.** The departure stays between 0.41α and 0.83α with tonics shared by up to 14 octaves, which extends the Shared-Tonic Principle from chains and trees to lattices.
- **The parity facts.** The beat graph is bipartite, but its sides disagree with coordinate parity exactly at the two hubs. Making the lattice parity-consistent (the 720) changes nothing dynamically.
- **The Xorzo octave tree** under its own scale map (peeling its leaves) shadows its coarse part to δ = 0.28 to 0.35 for one cycle, or 0.21 to 0.26 with the best local map. That is the tree form of v20's adjacency result (peeling the open chain's bottom octave gave 0.290). Random octave blocks on the same tree do as well, and the relation does not propagate: the error grows to 0.64 to 0.74 by the eighth cycle. Each cycle the parts take 8 to 12% of the whole's squared amplitude through the shared tonic.

Taken with v20 and v21: within the operator family as defined (canon strokes, θ = π/2, octaves meeting only at shared tonics), the staggered octave is self-similar as a rule and not as a dynamics.

## 1. The question and the construction

v21 §4 (a grade C reading) named the one constructive step left after seam modulation. It said self-similarity would need "a fine dynamics with an octave-local protected channel whose induced dynamics is the coarse octave's, including the hub couplings that tie non-adjacent coarse stations together". It named the geometry for this: each coupled pair of coarse stations bridged by a fine octave whose two tonics are those stations, as in the hierarchical lattices of renormalization theory. v22 tests the geometry with canonical octaves (F1 to F4) and then the protected channel (F5).

**Substitution rules.** Under tonic decimation a fine octave spans two coarse stations (its tonics), so a fine geometry is a choice of which coarse pairs get a fine octave. A rule replaces every octave of level L by bridge octaves on a graph over its eight stations:
- the stations become the bridges' shared tonics (local 0 opens, local 7 closes);
- each bridge adds six new nodes;
- level L+1 is the same rule applied to every octave of level L.

Each family is therefore self-similar as a construction by definition. The only question is whether its dynamics renormalizes.

| rule | pairs per octave | bridges per octave | nodes at levels 0, 1, 2, 3 |
|---|---|---|---|
| chain | 7 (the path 0-1-...-7) | 7 | 14, 98, 686, 4802 |
| beat | 10 (the pairs the four beats couple) | 10 | 14, 134, 1334, 13334 |
| parity720 | 10 (the six same-parity pairs through two octaves) | 16 | 14, 218, 3482, 55706 |
| complete | 28 (all pairs) | 28 | 14, 350, 9758, 273182 |

The rules:
- **Chain.** Reproduces the v20/v21 ring to 1e-16 (E0).
- **Beat.** The ten pairs, in order of first appearance in the beats (which happens to be lexicographic), are (0,1), (0,4), (1,5), (2,3), (2,4), (3,5), (4,5), (4,6), (5,7), (6,7). Four are the structure-process partner pairs and the hub pair (4,5); six are hub pairs (4 with 0, 2, 6; 5 with 1, 3, 7). This is the geometry v21 §4 asked for.
- **Complete.** Carries every within-octave coupling.

Settings:
- **Root (level 0).** The canonical two-octave staggered ring, as in v20 E2.
- **Composition.** Bridges fire octave by octave in the order the rule lists (seq, the StaggeredOperator convention), or beat-synchronously (sync, v16).
- **Operator.** Canon strokes, θ = π/2, κ diameter bonds at the measured α, legacy coordinates.
- **Symmetry.** Only the chain's pair set is invariant under a one-station shift: 14 of 14 pairs map onto pairs, against 10 of 20 for the beat and parity lattices and 44 of 55 for the complete lattice. So the lattices carry no fine translation, and v20's Theorem 1 floor has no analog on them.

**Scale maps** (level L+1 to level L; the coarse nodes keep their ids):
- **R_dec.** Restriction to the bridges' tonics, the literal 3.5D = 0D′ reading of v20/v21.
- **R_cell.** Block spin over Voronoi cells: bridge locals 1 to 3 go to the opening tonic, 4 to 6 to the closing one, and a parity720 midpoint tonic goes with its opening end.
- **R_whole.** The cell, weighted by each bridge's octave whole-mode.
- **Per-node cell family.** Any weights on the cells; it contains all three maps above. Its constrained optimum keeps every coarse row at unit norm (v21's honest ceiling). Because the cells are disjoint, every constrained member is co-isometric, so v21's leakage identity applies exactly.

**Nulls.** A small defect counts only if it beats all of these clearly:
- Haar co-isometries of the same shape;
- random decimations (same sparsity as R_dec);
- random weights on the same cells (same sparsity as R_cell and R_whole);
- random connected 10-pair geometries with canonical octaves;
- random octave blocks on the same lattice (one Haar 8×8 block everywhere, the coarse ring included);
- tensor nesting (closed form).

No parameter search was run, so no capacity null is needed.

**Verdict rule** (v20's, unchanged): supported at m only if δ ≤ 0.10 AND below the 1st percentile of every null family.

## 2. The 720 made geometric

A fine octave spans 3.5D, a half-integer, so it flips coordinate parity: integer (structure) against half-integer (process), which is the local index mod 2. On the chain every bridge joins stations of opposite parity, so under tonic decimation each fine tonic lands on a coarse station of its own parity.

The beat pairs are not all like that:
- four pairs flip parity: (0,1), (2,3), (4,5), (6,7);
- six pairs keep it: the hub pairs.

The beat graph is still bipartite (E1), with sides {1, 3, 4, 7} and {0, 2, 5, 6}. Those sides agree with coordinate parity everywhere except at the two hubs: local 4 (the structural hub) sits with the processual stations, and local 5 (the processual hub) with the structural ones. This is a fact about the beat template (grade A).

The parity720 rule repairs this the way Ashman's sentence says:
- a same-parity coupling is carried by two octaves in series through a new fine tonic (7D: a structure again, the 720);
- a parity-flipping coupling is carried by one octave (3.5D: a process at the next scale, the 360).

Along every coupling path of this lattice, a point is a process one octave away and a structure two octaves away. v21's ratio-3.5 body-plus-closure map has no lattice analog. It needs a continuation axis: each fine octave sends its body to one coarse station and its closing tonic to the next, so there are twice as many coarse stations as fine octaves along a line. A lattice level has no such axis, since its octaves meet in stars at the hubs. The parity lattice and the two-step map (F7) are the lattice forms of the 720.

## 3. Findings

### F1. Corpus maps: null at every level (null)

There are 528 cells: three corpus maps, four geometries, m = 1..8, F and T. They cover level 1 to 0 (seq and sync) and level 2 to 1 (seq, for the chain, beat and parity lattices, up to 3482 fine nodes). δ runs from 0.899 to 1.000; no cell is small, so no cell is supported. T matches F to within 0.002 in every cell.

At m = 4 and m = 8 (F):

| geometry | map | L1 to L0, seq | L1 to L0, sync | L2 to L1, seq |
|---|---|---|---|---|
| chain | R_dec | 0.984, 0.947 | 0.981, 0.974 | 0.979, 0.952 |
| chain | R_cell | 0.991, 0.944 | 0.971, 0.950 | 0.992, 0.950 |
| chain | R_whole | 0.984, 0.963 | 0.950, 0.972 | 0.992, 0.969 |
| beat | R_dec | 0.985, 0.960 | 0.965, 0.971 | 0.983, 0.955 |
| beat | R_cell | 0.962, 0.951 | 0.982, 0.944 | 0.958, 0.954 |
| beat | R_whole | 0.976, 0.980 | 0.963, 0.960 | 0.972, 0.977 |
| parity720 | R_dec | 0.973, 0.968 | 0.974, 0.997 | 0.967, 0.966 |
| parity720 | R_cell | 0.977, 0.952 | 0.978, 0.968 | 0.976, 0.954 |
| parity720 | R_whole | 0.947, 0.964 | 0.951, 0.961 | 0.946, 0.967 |
| complete | R_dec | 0.993, 0.990 | 0.962, 0.963 | not run |
| complete | R_cell | 0.989, 0.974 | 0.987, 0.986 | not run |
| complete | R_whole | 0.988, 0.982 | 0.968, 0.972 | not run |

145 cells lie below the 1st percentile of every null family that applies to them. Their δ runs from 0.899 to 0.982. Most are the whole-mode cell map at m = 1 to 4 and the plain cell map at m = 1 and 8. These local maps follow a cycle or two of the local dynamics better than random weights on the same cells do. That is structure beyond chance, not self-similarity; the smallest of them is 0.899.

### F2. The ceiling does not depend on the geometry or on the octave block (grade B)

The per-node cell family contains every local coarse-graining onto the cells. Values are unconstrained / constrained, level 1 to 0, seq, F:

| geometry | m = 1 | m = 2 | m = 4 | m = 8 |
|---|---|---|---|---|
| chain | 0.652 / 0.769 | 0.657 / 0.764 | 0.706 / 0.754 | 0.676 / 0.748 |
| beat | 0.658 / 0.765 | 0.671 / 0.735 | 0.701 / 0.735 | 0.690 / 0.733 |
| parity720 | 0.638 / 0.774 | 0.643 / 0.768 | 0.652 / 0.742 | 0.663 / 0.751 |
| complete | 0.647 / 0.736 | 0.660 / 0.722 | 0.672 / 0.720 | 0.688 / 0.724 |

Two checks:
- **Lattice to lattice** (level 2 to 1, m = 4): chain 0.707 / 0.758, beat 0.701 / 0.745, the same as one level down.
- **Cross-check with v21.** v21's per-node window family (eight nodes, the closing octave) on the same chain gives 0.731 constrained.

Nulls at m = 4 (constrained):

| geometry | canonical | random octave blocks, same geometry | z | percentile |
|---|---|---|---|---|
| chain | 0.754 | 0.767 ± 0.016 (20 draws) | −0.8 | 15th |
| beat | 0.735 | 0.761 ± 0.018 (20) | −1.4 | below all 20 |
| parity720 | 0.742 | 0.768 ± 0.023 (20) | −1.1 | 15th |
| complete | 0.720 | 0.746 ± 0.012 (10) | −2.2 | below all 10 |

Random connected 10-pair geometries with canonical octaves give 0.756 ± 0.012 (20 draws), with the beat lattice's 0.735 at z −1.6, below all 20.

Across the four geometries and m = 1 to 8 the constrained ceiling moves within 0.720 to 0.774. In every geometry the canonical octave sits 0.01 to 0.03 below the mean of its random-block null, and the beat pairs sit 0.02 below random pairs. That edge is consistent across geometries and so is probably real, but it is 0.02 on a ceiling of 0.73, nowhere near the 0.10 bar.

**Reference: locality is what the test measures.** Without locality, an unrestricted co-isometry reaches δ = 0.013 on the beat lattice at m = 4 just by matching eigenvalues. The fine spectrum contains the coarse one; no local map finds it.

### F3. At full seams the leak dominates; geometry only moves the trade-off (grade A for the identity, B for the reading)

v21's exact identity (δ² = 1 − |⟨F_c, M⟩|/N_c, with M = R F^m R† and leak² = 1 − ‖M‖²/N_c) holds here to 1e-15 (E0).

Every fixed-map cell, level 1 to 0, seq, F, ranges over m = 1..8:

| geometry | map | leak | cos(M, F_c) |
|---|---|---|---|
| chain | R_dec | 0.77 to 0.99 | 0.08 to 0.22 |
| chain | R_cell | 0.78 to 0.96 | 0.06 to 0.25 |
| chain | R_whole | 0.83 to 0.97 | 0.05 to 0.29 |
| beat | R_dec | 0.90 to 0.99 | 0.03 to 0.28 |
| beat | R_cell | 0.89 to 0.95 | 0.06 to 0.34 |
| beat | R_whole | 0.86 to 0.94 | 0.04 to 0.34 |
| parity720 | R_dec | 0.91 to 0.99 | 0.07 to 0.32 |
| parity720 | R_cell | 0.86 to 0.97 | 0.03 to 0.34 |
| parity720 | R_whole | 0.83 to 0.96 | 0.09 to 0.33 |
| complete | R_dec | 0.97 to 1.00 | 0.03 to 0.15 |
| complete | R_cell | 0.93 to 0.97 | 0.06 to 0.30 |
| complete | R_whole | 0.96 to 0.98 | 0.10 to 0.28 |

Across every fixed-map cell the leak is 0.77 to 1.00 and the alignment 0.03 to 0.34. The corpus maps both lose the channel and point the wrong way.

At m = 4, with the constrained optima:

| geometry | map | leak | cos(M, F_c) | δ |
|---|---|---|---|---|
| chain | R_dec | 0.902 | 0.075 | 0.984 |
| chain | constrained cells | 0.761 | 0.664 | 0.754 |
| beat | R_dec | 0.930 | 0.080 | 0.985 |
| beat | constrained cells | 0.785 | 0.741 | 0.735 |
| parity720 | R_dec | 0.956 | 0.183 | 0.973 |
| parity720 | constrained cells | 0.692 | 0.623 | 0.742 |
| complete | R_dec | 0.990 | 0.102 | 0.993 |
| complete | constrained cells | 0.815 | 0.832 | 0.720 |

The tonics are 4 to 14% of the fine nodes, and every bridge drains them at full strength each cycle. So the fixed maps keep only 2 to 19% of their squared amplitude after four cycles, and what stays barely points at F_c.

The constrained optima trade leak for alignment:
- the complete lattice gets the best alignment (0.83) at the highest leak (0.82);
- the parity lattice gets the lowest leak (0.69) at the lowest alignment (0.62);
- δ lands between 0.72 and 0.75 for all of them.

This is v21's dilemma (its F3) with the geometry as a dial: changing the geometry moves along the trade-off, not off it.

### F4. The coarse generator is dense: the coupled pairs were the wrong target (grade A for the shares, B for the reading)

The table gives the share of the squared weight of G_c = log F_c (root ring) that lies on the diagonal plus each geometry's pairs. In parentheses is the best cosine a generator with that support can reach with G_c (the square root of the share).

| support | pairs on the root ring | seq | sync |
|---|---|---|---|
| diagonal only | 0 | 0.032 (0.18) | 0.029 (0.17) |
| chain | 14 | 0.235 (0.48) | 0.263 (0.51) |
| beat and parity720 | 20 | 0.295 (0.54) | 0.216 (0.46) |
| complete | 55 | 0.797 (0.89) | 0.837 (0.91) |

The beat pairs carry barely more of the generator than the chain's path does, and under sync they carry less. The coarse cycle is the composite of four non-commuting beats at θ = π/2. Its generator is not the sum of the beat generators: at that angle the composition is far from perturbative, and it spreads the generator's weight over essentially all pairs. 16 to 20% of it sits on pairs in different coarse octaves, which no within-octave lattice can reach.

v21 F6 measured this as 80 to 82% of the weight at ring distance two or more, and read it as non-locality. The sharper word is density: no sparse set of pairs, adjacent or not, carries most of the generator. Bridging the coupled pairs therefore does not carry it. Only the complete lattice comes close in support (cos 0.89 to 0.91), and F2 and F3 show that support does not help while the seams leak.

### F5. Weak seams: protection without alignment (grade A for the span and its check, B for the conclusion)

Scaling the six tonic-touching couplings of every bridge by ε protects the tonics: at ε = 0.05, R_dec's leak after one cycle falls to 0.14 (chain) and 0.17 (beat, parity720). The table gives the minimum over m of δ for R_dec against the canonical root ring, scanned exactly through the Schur form for every m up to 200 at ε = 1 and up to 20000 at ε = 0.05, with the m where it occurs:

| ε | chain | beat | parity720 | complete |
|---|---|---|---|---|
| 1 (canon) | 0.908 (m = 78) | 0.939 (5) | 0.929 (7) | 0.963 (129) |
| 0.3 | 0.909 (1) | 0.907 (1) | 0.906 (1) | 0.943 (5) |
| 0.1 | 0.866 (1) | 0.865 (1) | 0.865 (1) | 0.880 (1) |
| 0.05 | 0.861 (1) | 0.861 (1) | 0.860 (1) | 0.862 (5093) |

As the seams weaken, the best δ moves to m = 1 and approaches 0.859. That is the score of a channel that does nothing: M = phase × identity scores sqrt(1 − |tr F_c|/N_c). The protected channel's best match to the coarse octave is standing still. Against random-block coarse targets, whose frozen score averages 0.948, the same scan finds 0.89 to 0.91, below their frozen score, by selection over 20000 values of m. The canonical target is never matched beyond its identity component.

**Why.** At second order in ε, each bridge contributes the same two-by-two effective generator on its pair of tonics: a self-energy at the opening tonic, one at the closing tonic, and a complex transfer between them. Each bridge contributes independently of the others. So the effective coarse generator of identical bridges lies in the real four-dimensional span of i·D_open, i·D_close, A − Aᵀ and i(A + Aᵀ), with A the directed bridge adjacency.

The extracted generator confirms this. Its distance from that span falls as ε goes from 0.05 to 0.02, as a second-order effect should:
- chain: 0.056 to 0.022;
- beat: 0.098 to 0.043;
- complete: 0.132 to 0.077.

How far the uniform span can point along G_c:

| | chain | beat | complete |
|---|---|---|---|
| best possible cos, seq | 0.12 | 0.21 | 0.28 |
| best possible cos, sync | 0.16 | 0.21 | 0.20 |
| canonical bridge's actual cos (seq) | 0.015 | 0.060 | 0.029 |

The canonical bridge's effective generator is essentially orthogonal to G_c. A protected channel built from identical canonical octaves cannot run the coarse octave in any geometry. Bridges with pair-specific couplings could do better, bounded by the per-pair capacities of F4: cos 0.46 to 0.54 on the beat pairs, 0.89 to 0.91 on all within-octave pairs. But that would mean writing the coarse octave into the bridges pair by pair (§4).

### F6. Conservation on lattices (grade A)

Departure (|λ₁| − 1)/α of T = κF:

| | chain | beat | parity720 | complete |
|---|---|---|---|---|
| level 1, seq | 0.811 | 0.733 | 0.699 | 0.640 |
| level 1, sync | 0.672 | 0.406 | 0.591 | 0.763 |
| level 2, seq | 0.833 | 0.705 | not run | not run |

For reference: the root ring 0.655, the Xorzo v3 tree 0.666 (reproducing the v3 notes' 0.6659), regular trees 0.645 and 0.641.

The departure stays between 0.41α and 0.83α, with no growth in degree or size, across:
- tonics shared by up to 14 octaves (the complete lattice);
- cycles in the octave graph;
- lattices of 1334 nodes.

v14 showed saturation on chains (0.61 to 0.65 for one to three octaves) and the v3 engine on its tree. The bridged lattices extend the Shared-Tonic Principle (CLAUDE.md, Wholeness Plane notice, item 3) to graphs with cycles and high-degree seams. Reading the departure as participation remains the interpretation that notice flags.

### F7. The 720 in the lattice (null; grade A for the parity facts)

- **The parity lattice behaves like the beat lattice everywhere.** Corpus maps 0.907 to 0.998 (beat: 0.899 to 0.994); constrained ceiling 0.742 against 0.735 at m = 4; weak seams agree to the third decimal. Carrying the same-parity couplings through two octaves instead of one is invisible to the dynamics.
- **Two scale steps** (level 2 to 0, R_dec composed twice, m from 1 to 64): chain 0.946 to 0.994, beat 0.975 to 0.999, parity720 0.976 to 0.999. Haar co-isometries on the beat lattice give 0.962 to 0.996.
- **The structural facts of §2** (the beat graph is bipartite, with the hubs on the opposite side from their coordinate parity) are exact. Their dynamical consequence is nil, consistent with v21 F7 and §27.7t.5: in this operator, parity is bookkeeping.

### F8. The Xorzo octave tree (null; grade C for the reading)

The corpus's existing non-chain geometry is the Xorzo octave tree. Each child's closing tonic is the parent's opening tonic, and parts fire before wholes. Its natural scale map is peeling: the coarse tree is the fine tree minus its leaves, with each leaf's private nodes in the cell of the tonic it attaches to.

This is the tree form of v20's adjacency reading (its F4). There, the octave shift was exact on the sync ring at m = 1, and peeling the open chain's bottom octave into its closure tonic gave 0.290 at m = 1, with the residue at the bottom seam.

Two things follow because the coarse octaves are present unchanged in the fine tree:
- the time scale is one cycle (m = 1);
- the relation must then propagate: R Fⁿ = F_cⁿ R.

Comparing R F^m with a single coarse step for m ≥ 2, as for the decimation maps, gives 0.85 to 0.98, but that is the wrong time scale for a peel map.

| tree | nodes | R_peel, m = 1 | best local map, m = 1 | random blocks, m = 1 | iterated, n = 2, 4, 8 | Haar, m = 1 |
|---|---|---|---|---|---|---|
| Xorzo v3 | 169 to 57 | 0.348 | 0.214 / 0.255 | 0.344 ± 0.015; 0.249 ± 0.021 | 0.479, 0.628, 0.744 | 0.956 |
| binary, depth 4 to 3 | 106 to 50 | 0.282 | 0.165 / 0.206 | 0.280 ± 0.016; 0.201 ± 0.021 | 0.386, 0.507, 0.635 | 0.956 |
| ternary, depth 3 to 2 | 92 to 29 | 0.317 | 0.201 / 0.235 | 0.318 ± 0.011; 0.225 ± 0.019 | 0.439, 0.589, 0.693 | 0.955 |

(The best local map is unconstrained / constrained. Random blocks: R_peel; constrained ceiling, 20 draws.)

These defects are of the same order as v20's chain peel, and far below their Haar null. They are still not small, and three facts place them:
- **They belong to the geometry, not the canonical octave.** Random octave blocks on the same tree score the same.
- **The leak at one cycle is 0.28 to 0.35.** Each cycle the leaves take 8 to 12% of the coarse part's squared amplitude through the shared tonic, and what stays is well aligned (cos 0.94 to 0.96).
- **The error accumulates over cycles.** The iterated defect reaches 0.64 to 0.74 after eight cycles. It grows roughly additively in δ² at first (0.12 per cycle for the v3 tree) and then slows. v20 did not run this test, which is the right propagation check for a same-time-scale map. Unlike the octave shift on the ring, peeling is not even an approximate symmetry of the tree's dynamics beyond a cycle or two.

### F9. Robustness and the tensor recap

Beat lattice variants, level 1 to 0, seq, m = 4:

| variant | nodes | R_dec | cell ceiling (unconstrained / constrained) |
|---|---|---|---|
| as built | 134 | 0.985 | 0.701 / 0.736 |
| orientation flipped | 134 | 0.979 | 0.682 / 0.753 |
| order reversed | 134 | 0.993 | 0.689 / 0.751 |
| root: one open octave | 68 | 0.981 | 0.695 / 0.703 |

(The ascending order coincides with the built order, since the first-appearance order of the ten pairs is lexicographic.)

Tensor nesting (v20 E8 closed form): depth 2 gives 0.000, 0.836, 0.838, 0.847, 0.982, 0.737, 0.863, 0.883 for m = 1..8, exact at m = 1 and compounding with depth.

## 4. What this says (readings, flagged)

*Reading, grade C: the obstruction, completed.* v21 named two causes: leak-or-freeze, and locality. v22 removes locality, since the complete lattice carries every within-octave pair, and nothing changes:
- at full seams every geometry leaks (F3);
- at weak seams every geometry freezes (F5);
- the generator of the coarse cycle is dense (F4), so the coupled pairs were the wrong target anyway.

What remains is one statement. In this operator family, the coarse octave is not the effective dynamics of any arrangement of canonical fine octaves joined at shared tonics, for two reasons:
- full-strength octaves drain any local channel;
- weak-seamed octaves induce a generator confined to a four-dimensional span that is set by the octave itself, not by the coarse octave.

*Reading, grade C: what would work, and why it would not be self-similarity.* Two ingredients together could in principle reproduce the coarse octave: a protected channel whose bridges are tuned pair by pair (each bridge's effective coupling set to the matching entry of log F_c), and a lattice that also bridges the cross-octave pairs. Two-mode couplers are universal: a general N-mode unitary needs N(N−1)/2 of them (the beam-splitter decompositions of linear optics, Reck et al. 1994). The complete lattice already has exactly one coupler per pair, 28 per octave, which is the count an eight-mode unitary needs. That is precisely why tuning it would prove nothing. The coarse octave would be written into the fine one, coupling by coupling, rather than produced by the rule.

*Reading, grade C: the arc v20 to v22.*
- v20: the homogeneous chain fails for two exact reasons (the symmetry floor and attractor selection).
- v21: seam modulation removes both and still fails, for a third reason (leak-or-freeze), with locality as a suspected fourth.
- v22: the change of geometry removes locality and fails for the third alone.

Within canon strokes, θ = π/2, and octaves meeting only at shared tonics, the staggered octave is self-similar as a rule and not as a dynamics. Every level is built by the same substitution and every scale runs the same engine, but the coarse-grained dynamics of the engine is not the engine. v20 F4 drew this line on the chain ("translation invariance in scale, the same rule at every octave, is satisfied; dynamical self-similarity with any time dilation is not"); v22 carries it to lattices and trees.

*Reading, grade C: bearing on open decision 2 (the home of A3).* CLAUDE.md lists the option of promoting self-similarity to a theorem of the wrap: "the circuit exits ⟳ and re-enters • unchanged in form, so every scale runs the same engine." v20 to v22 support that theorem as it is stated, at the level of form. They caution against a dynamical reading, that the engine's coarse-grained dynamics is the engine again, because the operator does not satisfy it for any scale map tested in three experiments. This is for Ashman to adjudicate; there is no canon edit here.

*Reading, grade C: the tree.* Like v20's chain peel, the tree's peel holds only without time dilation, and here only for a cycle or two. Under peeling, the coarse tree shadows the fine one for a cycle because the parts touch the whole at one node per child. The defect is the share of the whole that passes through its parts each cycle. Here the dilemma takes its plainest form: the whole would shadow itself exactly only if its parts stopped touching it (weak seams at the attachment tonics make the leaves irrelevant). The v3 engine's design chooses the coupling and pays for it in exactly this defect: AGREEMENT lives at the seam, and parts complete before wholes.

*Reading, grade C: the 720.* Honoring the parity double cover in the geometry is dynamically invisible (F7). The one new structural fact is that the octave's own coupling graph has a consistent two-coloring, with the two hubs on the opposite side from their coordinate parity. The hub beat is therefore where structure and process trade places in the coupling graph. That is a description of the template, not a claim beyond it.

## 5. Scope and open items

- **Not run.** Sync at level 2 (dense exponentials of 1334 or more nodes); the complete lattice at level 2 (9758 nodes) beyond node counts; ceilings at level 2 for the parity and complete lattices; level 3 (node counts only).
- **Not built, deliberately: tuned (modulated) lattices.** A tuned complete lattice is universal (§4), so a fit would need a capacity null and would prove nothing about the rule.
- **Other θ or stroke conventions.** v22 keeps canon (θ = π/2) throughout. The two mechanisms (strong mixing draining the tonics at full seams, and the uniform span at weak seams) do not depend on θ in kind. A different θ would change the numbers. This is a reading, not tested.
- **The parity lattice's effective generator** was not extracted: its two-octave paths act at fourth order in ε.
- **Trees.** Peel is the tree's only natural scale map. An octave-to-station map would need children attached at every station of the parent, which is a different tree, not built.
- **For Ashman:** whether the theorem proposed for open decision 2 should say "in form" explicitly.

## Revision history

- 2026-10-16 v1.0: initial.
