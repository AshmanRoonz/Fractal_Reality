# Can "One Energy, Self-Limiting" Produce the Graph?

**Status: session record, 2026-11-04. Claude drafted in answer to Ashman's question and two relayed follow-ups, pending Ashman's countersign.** Nothing in `circumpunct_framework.md` or `CLAUDE.md` is touched by this file. All data are synthetic and the mathematics is standard. No scoreboard entry is added. Successor to `plans/wave_operator_unfolding_2026_11_04.md`, whose largest gap was that the axioms supply no space for "local" to be local in.

## The prompt

Ashman: *"Work on whether 'one energy, self-limiting' can produce the graph itself. If locality can be derived too, nearly everything above unfolds from the foundation."*

Two follow-ups, relayed from a conversation with another assistant:

1. Can the boundary of a system be derived from relation strengths, without selecting the system first?
2. *"Can we define a scale-independent criterion for the simultaneous persistence of part autonomy and greater-whole integration, and then derive the wholeness plane from that criterion?"*

Notation, per Ashman: use D for actual dimensional geometry; otherwise use the symbols and their structural roles. The foundational form is ⊙ = Φ(•, —, ○), with • → — → ○ → Φ → ⊙ kept as logical dependency.

## Verdict

**Partly. The graph, yes. Locality, no.**

- **Produced:** sparse, connected, mediated graphs. The undifferentiated state is ruled out, given one added assumption (Finding 1).
- **Not produced:** geometry. Energy feedback alone makes either a thin tangled graph or something indistinguishable from a random one. Adding closure makes interiors, but no setup tested stayed connected and also kept stretching at large size.
- **Not derived:** the growth exponent, and so any D.
- **Best new result:** a capacity law, s* = h/(1+h), which gives the 2026-08-01 hypothesis a = A(c, h) a concrete form.
- **The plane:** measurable with three of its four corners. It is defined, not derived.

This is a result about one family of rules. It is not a proof that locality cannot be derived. Nesting, the word this question left out, has not been tried (Open decision 8).

## Setup

n sites, symmetric weights w_ij ≥ 0, zero diagonal, started from the complete graph with small noise. Each step is w' = w^(1−η) f^η, then renormalize to the budget, with η = 1/2.

Two budgets: **global** (one total shared by all, so a part holds a piece of the 1) and **site** (every row sums to 1, the corpus's "not a piece of it, but the whole thing").

The energy share among modes is E_k ~ λ_k^(−γ), and e_ij is the energy on edge ij. γ = 1 is equal energy per mode, with e_ij = w_ij R_ij; Foster's theorem gives Σ = n − 1. γ = 1/2 is ground-state fluctuation. γ = 0 is equal amplitude per mode, with e_ij = 2w_ij, which is plain self-reinforcement. The feedback is f = e^β. The closure rule uses (P²)^β, and the mixed rule is f = e^(β(1−θ)) (P²)^(βθ). P² needs a shared neighbor (**strict**); P + P² does not (**soft**).

Predictions were frozen in each script's docstring before it ran. Second-round and follow-up predictions were frozen too, but their questions were chosen after seeing earlier results, and are marked post hoc.

## Finding 1: the undifferentiated state falls, with help

The complete graph is the undifferentiated state: it has one nonzero Laplacian eigenvalue, which fits "∞ is one by inclusion." It is a fixed point of every rule and loses stability near β = 1, with measured amplification β(1 − γ/n).

Any convex permutation-invariant functional has the complete graph as an optimum, so differentiation **requires nonconvexity**, here β > 1. Self-limitation does not supply this. It is added.

## Finding 2: the reading of the budget decides the outcome

- **Global, γ = 0, β > 1:** collapses to exactly one pair.
- **Site, γ = 0, β > 1:** pairs and odd cycles, never connected. This is the Birkhoff and Katz result: the extreme points of the symmetric doubly stochastic matrices are ½(P + Pᵀ) with no even cycles of length 4 or more.

So "each part is the whole 1" gives parts with no whole, unless something protects connection.

## Finding 3: connection needs energy per mode

A weak bridge carries e ~ w^(1−γ), so it survives only if β(1−γ) < 1. Sparse and connected together need 1 < β < 1/(1−γ): an empty window at γ = 0, (1, 2) at γ = 1/2, and (1, ∞) at γ = 1. The runs confirm the pattern, though the true edge at γ = 1/2 sags to about 1.7 to 1.8 at large n.

The global budget at γ = 1 stays connected but does not end in trees as I predicted. Mean degree depends on β: about 5 at 1.2, 3.08 at 1.5, 2.5 at 2, 2.1 at 3, and about 2.0 at 5. The nearest prior work I found is Bohn and Magnasco on optimal transport networks, where the convexity of the cost decides between trees and loops.

## Finding 4: the closed line is a theorem about states, not a place the dynamics reach

**Static result.** The sparsest connected zero-diagonal graph under a site budget is the Hamiltonian cycle, because a leaf would exhaust its neighbor's whole budget. So the closed line is the minimal connected whole. An open chain's ends need outward share, which gives K_B + L_E; on a Dirichlet lattice K_B is budget going outward.

**Dynamic result.** The rule does not get there. Site budget, γ = 1: connected always, but rings appear only at small n (88% at n = 16 and β = 2, 38% at n = 15, 0% at n ≥ 32). At β = 2 mean degree is 2.4 to 2.6, and diameter grows about as n^0.27.

Searching near the disconnection edge at γ = 1/2 makes the graph more line-like, then it breaks before reaching a ring:

| β | Diameter | Mean degree | Connected | Ring |
|---|---|---|---|---|
| 1.3 | n^0.22 | 2.03 to 2.33 | always | 83% at n = 32, then 0 |
| 1.5 | n^0.42 | about 2.14 | mostly | 0 |
| 1.7 | n^0.67 by n (about 0.86 against largest piece) | about 2.0 | 1, .83, .33, 0, 0 | 0 |
| ≥ 1.8 | fragments | below 2 | never | 0 |

## Finding 5: above degree 2, energy makes a random graph

Capping each relation at 1/k, k ≥ 3, gives a graph indistinguishable from random k-regular (k = 4, n = 256: diameter 7.0 against 7.0, λ₂ .1456 against .1451, clustering .007). Energy reinforcement favors long shortcuts, so it works against locality rather than producing it.

## Finding 6: what "local" has to mean

**Every graph is local in its own metric**, so the word needs content. The content is ball growth: growth exponent, interior fraction, conductance, λ₂ scaling. Expanders have no interior-dominated wholes at all.

| Family | λ₂ exponent | Diameter exponent | Notes |
|---|---|---|---|
| Ring | −2.00 | 1.00 | |
| Torus (2D) | −.99 | .50 | |
| Torus (3D) | −.61 | .32 | |
| Gasket | −1.47 | .64 | Low-gap 2.43 |
| Hierarchical cube, r = ¼ | about −2 | | Low-gap 3.05 |
| Random 3-regular | | | Interior stuck near .56 |
| Complete | | | Interior 0 |

Walk-dimension estimates are biased at these sizes. One prediction failed: rings glued at random keep interior .909 and λ₂ ~ n^−.99, because a ring of rings keeps its large-scale order.

A budget alone only forces summable tails, and long tails (exponent below 2) give non-∇² dispersal. A hand calculation on lattices (not a test) found that a block of side ℓ has conductance about 1/ℓ in any d; low d keeps wholes separated but integrates slowly, and high d does the reverse. Trading separation against reach gives a product proportional to d, with no interior optimum. So that trade does not select a D.

## Finding 7: closure gives interiors, not geometry

Only **strict** closure helps, and it is a strong chosen rule: every edge must share a neighbor. Soft closure at cap ¼ matches random regular. Soft closure with no cap gives degree about 2.2 to 2.4, clustering near 0, and diameter n^.22 to n^.35. Strict closure alone at β = 2 returned the complete graph, not the clusters I predicted, since θ ≥ ½ leaves amplification β(1−θ) ≤ 1.

Up to n = 256 strict closure looked like geometry. The test at larger sizes was the point of the exercise (fit on n ≤ 256, γ = 1, β = 2, 4 seeds, 800 iterations):

| Setup | n | Pieces | Largest | Diameter | Power fit | Log fit | λ₂ | Growth |
|---|---|---|---|---|---|---|---|---|
| θ = .4, no cap | 512 | 4.8 | 432 | 68.0 | 49.8 | 43.3 | .00004 | 1.27 |
| | 1024 | 10.8 | 771 | 78.8 | 68.5 | 51.3 | .00002 | 1.44 |
| θ = .3, no cap | 512 | 9.8 | 413 | 65.5 | 46.2 | 40.9 | .00019 | 1.35 |
| | 1024 | 25.5 | 680 | 69.2 | 58.5 | 46.7 | .00011 | 1.46 |
| θ = .4, cap ¼ | 512 | 1.2 | 510 | 24.8 | 25.0 | 24.2 | .00242 | 1.73 |
| | 1024 | 1.5 | 1020 | 23.8 | 28.9 | 26.9 | .00205 | 2.08 |

Random 4-regular at n = 1024: diameter 8.0, λ₂ .138, growth 3.12.

**My prediction Q3 failed in two of three setups.** I said a log fit would beat a power fit everywhere, making this a clustered small world. The uncapped runs beat both fits and the power fit is closer. Only the capped run behaves as predicted: its diameter goes flat near 24, its λ₂ stays near .002 from n = 64 to 1024, and its growth exponent climbs instead of settling.

What the table shows:

- **The runs that keep stretching fall apart.** Their largest piece falls to 75% and 66% of the sites at n = 1024.
- **The run that stays connected stops stretching.** It is clustered and far from random, but small-world.
- **No setup is both connected and geometric at large size.**

Limits on this: three setups and 4 seeds; the diameters jump around (35 to 68 to 79 at θ = .4, against 256, 432, 771 for the largest piece), so no exponent should be read off them; and few of these runs had settled by 800 iterations, none at the largest size. The growth exponents are still rising, so this does not distinguish a branching chain from anything else. The second half of P8 (no lattice of d ≥ 2, at best chains of clusters) stands, untested beyond that.

## Finding 8: known mathematics on the ceiling

For transitive graphs, polynomial growth forces virtually nilpotent structure (Gromov, Trofimov). So a homogeneous graph with polynomial growth is close to a lattice-like object, and the choice of d is then the free thing. Gaussian heat kernels on such graphs (Hebisch and Saloff-Coste; from memory, search did not confirm) and doubling (Assouad; from memory) say something similar. Nothing here selects a value. Prior work on emergent locality: Quantum Graphity and Cotler et al. (Sources).

## Finding 9: a boundary can be read from relations, but not by threshold

The pasted derivation (reciprocal reachability, groups, quotient) is correct as mathematics: the strongly connected component equivalence and its worked example hold, though the inner min in I(S) is redundant. Tests:

- With symmetric relations reciprocity is vacuous (200/200). It matters only for directed relations, where it correctly finds no wholes in feed-forward layers while a symmetrized rule gives false levels.
- The quotient at a fixed threshold is always acyclic (200/200), so **recursion needs the threshold to move**. There is no fixed-scale recursion.
- The construction assumes elements and relations as given. It runs many → one, the reverse of one → many, so it does not answer the graph question.
- **The threshold is a poor detector.** Strong cross-links: 0 levels found. Dense outside relations: 8 wholes reported, though the inside share is .114. Noise on a complete graph: 62 levels. It works only when told the right threshold.
- **My share rule (majority of relations inside, close to Radicchi's strong community) also failed** on strong cross-links, finding 14 groups, since true members fall to .41 to .48 inside share even though they hold (≥ 1.78). It also passes short arcs of a noisy ring.
- **Low-mode clustering recovered all 8/8 placements** of the strong cross-link case (post hoc). So the boundary is best read from the modes, and reading it across time is Delvenne et al.'s Markov stability.
- A well-mixed block has s* = m/(2m−1) exactly, while a ring falls from .2265 at m = 8 to .0048 at m = 64. So one half is a statement about well-mixed wholes, not a general law.
- I dropped wave retention as a test: on dense graphs a wave barely moves, so random sets retain too.

## Finding 10: the criterion, and how much of the plane it reaches

Frozen definitions, with K = I − D^(−½) W D^(−½):

- **a** = g_k × volume-weighted mean A(S), where A(S) = r_mix/(r_mix + r_esc), r_mix = (1−out)h, r_esc = out, and g_k = 1 − λ_k/λ_(k+1).
- **c** = the capped, normalized λ₂ of the quotient of parts inside each parent.
- **Correction, same day, found while auditing Experiment 13 of the physics series.** This c reads the pattern of bridging, not its strength, because the quotient is normalized. Four blocks of 16 with bridge weight falling from 1e-1 to 1e-10 read c = 1.000 throughout while a rises to 1.000, so a network about to be severed sits in the health corner and then jumps to (1, 0) at exact zero. The Severance corner below is reached only at zero coupling. A c that sees strength needs a clock to measure it against: the part's own rate gives c = 1 − A, the single axis the 2026-08-01 notice retired, and an outside window makes c depend on that window. A candidate fix, comparing peers with what lies beyond them, reaches all four corners and removes the −.742 tie below; see `experiments/wholeness_theory_v1.py` and the Theory of Wholeness draft, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte. It is not countersigned, and with nothing beyond a part it has no clock.
- **Levels** are those among the 6 largest g_k with a > ½.

| Case | a | c | Reading |
|---|---|---|---|
| Separate blocks | 1.000 | 0.000 | Severance, as predicted |
| Complete | 0.000 | 1.000 | Absorption, as predicted |
| Hierarchy, separated shares | .82 to .97 | 1 (pattern trivially complete) | Integration |
| Hierarchy 4×4×4, shares .05/.05 | .844 | .684 | One level; my shares were not separated |
| Thin rings in a long path | .468 | 1.000 | **Anomie not reached** |
| Ring, n = 32, 128, 512 | .253, .096, .030 | 1.0 to .115, by k | **No level; off the plane** |
| Long chains, p = 6 to 48 | .948 | .5 down to .009 | c = 1 − cos 2π/p |

What held: three corners; a tracks a direct dynamic plateau, Spearman .748 narrowly under my .8 bar, and .857 after correcting for part size (post hoc); c tracks direct truth at .707; k is stable through 40% noise, with a shift of .073; level values match on the graph and its quotient to 3 digits in the symmetric cases testable; a stays steady across size (.855 to .834).

What failed:

- **a and c are not independent.** ρ = −.742 on the factorial design, with quadrants HH 6, HL 24, LH 17, LL 1. My second attempt, using g only as a gate, did worse (−.797) and failed fresh seeds, so v1 stays.
- **The anomie corner is not reached.** I think this is conceptual as well as technical: low a means no parts hold, and c measures the pattern among parts. A part that is not there cannot be scored for belonging, so anomie may need c defined some other way.
- c at fixed shares drifts with size (.769 to .615) on unseparated shares.

So the answer to "derive the plane" is: the two coordinates can be measured without selecting the system first, and they are scale-independent in the tests that apply. Their independence, which the 2026-08-01 notice asserts, does not hold under this measurement.

A depth result, with a caution: per-level a and c stay high while global λ₂ falls (2.67e-2, 2.67e-3, 6.67e-4), which resembles the Shared-Tonic claim that participation survives depth. But that is built into the planted graphs, so it is no evidence. Long chains show the opposite when intermediate levels are missing.

## Finding 11: the capacity law

**A block with internal gap h stops holding at outside share s* = h/(1+h).**

This comes from setting r_mix = r_esc. Measured with a slow-mode method, the ratio of measured to predicted was:

| Block | All pairs | Few contacts |
|---|---|---|
| Complete | 1.024 to 1.026 | .995 to 1.026 |
| Ring | 1.041 to 1.049 | 1.05 to 1.072 |
| Sparse | 1.118, 1.158 | 1.088, 1.194 |

So it is within 15% except the two sparse blocks at m = 32 (16% and 19%), and the measured crossing sits above the prediction in all but one case. I predicted few-contact would depart, and it mostly did not.

How much weight this carries:

- The first two measurements were wrong (a wrong index, then a bath floor), so the working method is post hoc.
- For all-pairs coupling it is exact algebra: the nonuniform eigenvalue is (1−s)λ + s. The small upward bias is from the finite bath.
- It is diffusive only.
- It is ordinary spectral theory near Simon's near-decomposability and the partitioning-into-expanders result. It is not new mathematics.

What it does for the framework: the 2026-08-01 notice proposes a = A(c, h) and says "No framework-native handle on h yet." Here h is the part's own lowest mode gap, and the law has the shape that hypothesis asks for. A thin part (ring, m = 64) can hold only with s* = .0048, while a well-integrated part holds up to about one half.

The ceiling at about ½ needs a caution. The threshold A = ½ is my choice, so the ½ partly reflects the definition. It resembles ◐ = 0.5, and I am not claiming the two are connected.

## Prediction ledger

| Prediction | Outcome |
|---|---|
| P1 fixed point, instability near β = 1 | Pass |
| P2 global, γ = 0 collapses | Pass |
| P3 site, γ = 0: pairs and odd cycles | Pass |
| P4 global, γ = 1: spanning trees | **Fail** (degree depends on β) |
| P5 site, γ = 1: rings at n ≤ 64 | **Fail** (the key one) |
| P6 weak-bridge window | Pass, qualitatively |
| P7 cap gives random regular | Pass |
| P8 closure alone gives clusters | **Fail** first half; second half stands |
| P9 families | Mostly pass; **fail** on rings glued at random |
| Q1 near the edge, rings appear (post hoc) | Partly **fail** |
| Q2 closure departs from random (post hoc) | Pass for strict only |
| Q3 log beats power at n = 1024 (post hoc) | **Fail** in 2 of 3 setups |
| B1, B2, B5, B8, B9 | Pass |
| B3 share rule handles cross-links | **Fail** |
| B4 dense outside relations | Pass |
| B6 noisy ring spurious arcs | **Fail** by search; hand cuts confirm the point |
| B7 feed-forward | Half **fail** on the tie case; post hoc confirms |
| W1 corners | Three pass; **fail** on anomie and on planted c |
| W2 ring has no level | Pass |
| W3 dynamics | a **fail** narrowly (.748); c pass (.707) |
| W4 size | a pass; c **fail** on unseparated shares |
| W5 recursion | Pass where testable |
| W6 stability | Pass |
| W7 independence | **Fail** |
| W8 capacity law | **Fail** as first run (a bug); holds with X3's post hoc method |

## What came from where

| Step | Status |
|---|---|
| Differentiation away from the complete graph | Needs nonconvexity (β > 1): **added** |
| Sparsity | Follows, given β > 1 and a budget |
| The budget's form (each part is the whole 1) | **A reading of A3**; it decides the outcome |
| Connection | Needs energy shared by mode (γ > 0): **added** |
| Mediated (no direct all-to-all) | Follows from sparse and connected |
| The closed line as minimal whole | **Theorem** under the site budget; not reached dynamically |
| Interior (clustering) | Needs strict closure: **added, strong** |
| Boundary | Readable from low modes, given the graph |
| Locality at large size | **Not produced** |
| Growth exponent, D | **Not produced** |

## Retained reading, not canon

**The part's ○ as a level set of the whole's Φ.** The best boundary finder here reads parts from the low modes of the whole. The order • → — → ○ → Φ has ○ feeding Φ, so at the next level down the dependency turns around: the modes of the whole supply the boundaries of its parts. Canon already holds this as the boundary-field identification (○_λ = Φ_Λ at the contact, §27.7o, "a 2-surface is exactly what a 3D field looks like on a level set"). For the lowest mode this is the standard Cheeger sweep cut. I used clustering in the low-mode space, not level sets, so I did not test it directly.

**The ring off the plane.** The minimal connected whole has no level at any size, and its sites hold nothing inside (h = 0 for a single site). That fits a closed — having • as parts, not ⊙. The relayed caution not to assign the ring to anomie was right: under this measure it sits off the plane, not at a corner.

## Open decisions (Ashman to adjudicate)

1. **Countersign the walk** and the "what came from where" table as the working account.
2. **The budget reading.** The site budget follows "not a piece of it, but the whole thing." The global reading collapses to one pair. Is this now part of how A3 is read?
3. **Is closure admissible?** Strict closure says a relation needs a shared neighbor, which may be a reading of "mediated." If it can be derived, that step moves from added to forced. If not, it stays chosen.
4. **The handle on h.** Adopt the part's lowest mode gap as the framework's h, and s* = h/(1+h) as the form of a = A(c, h), diffusive scope only?
5. **The plane.** a and c are not independent under this measurement, and anomie is not reached. Redefine c so that it does not need parts, or read anomie as "no level" together with low integration?
6. **Order as dependency.** Keep • → — → ○ → Φ → ⊙ as logical dependency. I have kept it unless told otherwise.
7. **Migration of D labels.** New writing uses symbols. Corpus arguments that lean on spatial meaning need their own check if migrated: the φ^d rule, c² as surface, inverse-square, 0 + 1 + 2 = 3 read as a solid, and "time is half a dimension."
8. **Next target: nesting.** This question dropped the word "nested" on purpose. Geometry may come from ⟳: a block that forms becomes a site of the next level, with its own budget. My guess before any test: this gives a definite growth exponent set by the block ratio, so locality would appear but its value would be a parameter, not derived. Tested the same day: `plans/graph_from_nesting_2026_11_04.md`. Locality appeared, thin, and its value is a parameter of (γ, β), so that half held; the block ratio half was wrong, since it cancels in the symmetric state.

## Files consulted

`CLAUDE.md` (notices of 2026-06-09, 2026-08-01, 2026-10-15; A0 to A4 and D1 to D5; engine form; Topology of Connection); `circumpunct_framework.md` (§2.13, §6.5, locality and isotropy near line 7995, fractional Laplacian near line 6245, Q₆ near line 12088); `plans/predictions_scoreboard.md`; `plans/the_isomorphism_of_the_framework_2026_08_19.md`; `plans/the_four_claims_2026_08_19.md`; `plans/what_it_offers_math_and_physics_2026_08_21.md`; `circumpunct_framework_synthesis.md`; `plans/wave_operator_unfolding_2026_11_04.md`.

Scripts: `experiments/graph_from_self_limitation_v1.py`, `experiments/boundary_from_relations_v1.py`, `experiments/wholeness_plane_criterion_v1.py`.

## Sources

- [Cotler et al., locality from the spectrum](https://link.springer.com/article/10.1007/s00220-019-03376-w)
- [The Katz result, via Self-Dual Maps](https://arxiv.org/pdf/1210.2579)
- [Quantum Graphity](https://research-portal.uu.nl/en/publications/quantum-graphity-a-model-of-emergent-locality/)
- [Bohn and Magnasco, optimal transport networks](https://arxiv.org/abs/cond-mat/0607819)
- [Tessera and Tointon, polynomial growth](https://arxiv.org/pdf/1908.06044)
- [Partitioning into Expanders](https://ar5iv.arxiv.org/html/1309.3223)
- [Simon's near-decomposability, via a recent paper](https://arxiv.org/pdf/2501.12748)
- [Delvenne et al., Markov stability](https://arxiv.com/abs/0812.1811)

From memory, not confirmed by search: Radicchi, Hebisch and Saloff-Coste, Assouad.
