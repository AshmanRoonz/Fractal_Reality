# Does Nesting Supply Locality?

**Status: session record, 2026-11-04. Claude drafted in answer to Ashman's "Yes, test nesting", pending Ashman's countersign.** Nothing in `circumpunct_framework.md` or `CLAUDE.md` is touched by this file. All data are synthetic and the mathematics is standard. No scoreboard entry is added. Successor to `plans/graph_from_self_limitation_2026_11_04.md`, which found that "one energy, self-limiting" produces the graph but not locality, and named nesting as the untried candidate.

Dimensions below are always about actual geometry (spectral dimension d_s, growth exponent, three dimensions of physical space). Everything else is named by role.

## The question

Does a nested rule, where a block that forms becomes a site of the next level with its own budget, supply the locality that closure did not? And does it select a growth exponent?

The rule, level by level from the bottom:

1. Blocks of this level are sites. The γ = 0 site-budget rule runs on them from the complete graph plus noise. What closes (pairs, odd cycles) is a group. No block size is planted.
2. Each group becomes a whole: its relation is laid over all member pairs, with noise, at outward share t, then the site budget.
3. The energy rule (γ, β) runs on the group's own submatrix, on existing support only, so nothing new is born. FREE: every entry is reinforced, so levels find their own shares. FROZEN: only the new level's entries, at fixed shares in a chosen ratio r.
4. The group is a block of the next level. Repeat until one block remains. Fresh noise each level, so no geometry is inherited.

## Verdict

**Locality: yes, in a thin form, up to 1024 sites. A dimension: no.**

The same rule (γ = 1, β = 2) goes small-world without nesting and stays stretched with it:

| | Non-nested | Nested (four configurations pooled) |
|---|---|---|
| Connected at n = 1024 | 100% | 100% |
| Hop diameter at n = 256, 512, 1024 | 13.7, 15.2, 17.0 | 32.8, 46.4, 62.1 |
| Diameter slope, 256 to 1024 | .16 | .46 |
| λ₂ at n = 256, 512, 1024 | 3.08e-2, 2.80e-2, 2.52e-2 | 1.49e-3, 6.14e-4, 2.23e-4 |
| λ₂ slope, 256 to 1024 | −.14 (nearly flat) | −1.37 (gap closes) |
| Spectral dimension (Weyl fit) across those n | 2.47, 2.81, 3.19 (still climbing) | 1.56, 1.51, 1.49 (settled) |
| Spectral dimension (return probability) | 2.08, 2.14, 2.16 | 1.44, 1.43, 1.43 |
| Interior fraction at n = 1024 | .665 | .91 to .94 |
| Midpoint index at n = 1024 | .522 | .51 (a length geometry) |

**The frozen main test failed, by one clause of four, and I had predicted it would pass.** N7 required connection, a power fit beating a log fit for diameter at both held-out sizes and within 15%, a stable growth exponent, and interior at least .75. At n = 1024 the main configuration's power fit gave 73.0 against an actual 56.0 (+30%), and the log fit (47.2) was closer. The other three clauses passed, and at n = 512 the power fit won clearly (+3% against −18%).

Two post hoc readings say that miss is seed scatter rather than a log law, but they are post hoc. Its four seeds at n = 1024 gave diameters 60, 61, 45, 58. Pooled over the four configurations with this rule, the power fit is +13% and the log fit −25%. Rerun with the same seeds to convergence (T = 600), the main configuration gives 31.8, 43.5, 58.5, slopes .45 and .43: a steady power law.

## What this does and does not establish

Tested on one family of rules, up to n = 1024 (block formation to 2048), with 4 seeds at n ≥ 512 and T = 150 unless stated. A larger size could still bend the diameter toward a log. This is not a no-go theorem for anything.

Correction, same day: the plane's c is blind to bridge strength (see the predecessor record), so every c = 1.0 in this record carries no information. Finding 5 uses only a, with extent read from r, so it stands. Its a is also a timescale separation under diffusion, so "holds" means metastable, not permanent: pure diffusion eventually erases any difference between blocks.

## Findings

**1. The mechanism is doors, and it is a law of this rule.** A whole of 400 sites touches the next level through about as many sites as a whole of 9. At γ = 1, β = 2, n = 1024:

| Block size | 2.1 | 4.3 | 8.7 | 18 | 40 | 87 | 196 | 427 |
|---|---|---|---|---|---|---|---|---|
| Doors per block | 2.0 | 2.9 | 3.7 | 4.2 | 4.1 | 3.8 | 3.4 | 3.3 |

Written as edges per site at level l falling as 2^(−κl), κ is close to 1 (constant doors) on 8 of 10 connected configurations: .97 to 1.17, against .74 at β = 1.2 and .69 at γ = 1.5. Nesting's contribution is an order: two sites can relate only once the wholes containing them merge, and the energy rule then strips each merge to a few doors. Connection comes from γ, not from nesting: at γ = 1 a bridge has energy exactly 1 (Foster), so bridges are never lost, and at γ = 0 the graph is all pairs, as predicted.

**2. It does not look like a manifold.** At γ = 1, β = 2 the dimension measures disagree: growth 1.74, metric 1.65, spectral 1.46 to 1.51, and 1 over the diameter slope about 2.3. The ring agrees across them (.97 to 1.02) and the 1024-site torus in two dimensions fairly well (1.77 to 2.18). The disagreement alone does not decide it, because the 512-site torus in three dimensions spreads about as widely (2.17 to 3.29). With mean degree 2.34 and clustering near zero, the likeliest picture is a thin, branching network with a length geometry rather than a sheet or a volume. This is a judgment from these measures, not a proof.

**3. No exponent is selected.** Every value moves with (γ, β). The start does not matter (d_s shifts by .04 across t0 in {.1, .3, .5} and β0 in {1.5, 2}), so the exponent comes from the rule, but the rule has a free dial. At n = 1024:

| Rule | d_s (Weyl, return) | Growth | Diameter slope | λ₂ slope | Mean degree | κ | Interior |
|---|---|---|---|---|---|---|---|
| FREE γ=1, β=3 | 1.17, 1.15 | 1.33 | .62 | −1.35 | 2.21 | 1.17 | .97 |
| FREE γ=1, β=2 | 1.51, 1.46 | 1.74 | .39 | −1.06 | 2.34 | .97 | .91 |
| FREE γ=1, β=1.5 | 1.67, 1.64 | 1.97 | .35 | −1.03 | 3.07 | 1.03 | .88 |
| FREE γ=1, β=1.2 | 2.73, 2.77 | 2.64 | .32 | −1.00 | 4.87 | .74 | .64 |
| FREE γ=1.5, β=2 | 2.58, 2.49 | 2.41 | .21 | −.49 | 3.10 | .69 | .76 |
| FROZEN r=.25 | .81, .83 | 1.65 | .38 | −1.79 | 2.91 | 1.04 | .94 |
| FROZEN r=.4 | 1.17, 1.15 | 1.61 | .45 | −1.32 | 2.94 | 1.09 | .94 |
| FREE γ=½, β=1.5 | .56, .57 | 2.11 | disconnected at n ≥ 512 | | 2.22 | | .75 |
| Non-nested γ=1, β=2 | 3.19, 2.16 | 2.41 | .16 | −.14 | 2.62 | | .67 |

Across the FREE rows the trend is one trade: more extent, weaker locality. The rows with higher d_s have flatter diameter and more doors.

**4. The biggest surprise: my ceiling broke at β = 1.2.** I predicted d_s ≤ 2γ + .2 in every FREE configuration, "so at γ = 1 there is no d_s near 3" (N9). At γ = 1, β = 1.2 and n = 1024 it reads 2.73 (Weyl) and 2.77 (return). When that missed I predicted it was a transient that would fall below 2.5 with mean degree below 4 at T = 600 (P4). It did not: d_s stayed at 2.73 and 2.79, degree only reached 4.59. This is also the one rule where the measures nearly agree: growth 2.64, metric 2.65, spectral 2.73 to 2.79, and 1 over the diameter slope about 3.1, though the λ₂ slope of −1.00 implies 2.

Do not read this as three dimensions. It has never converged, even at T = 600. Diameter is only 12.5, so finite size is close: the n = 512 torus in three dimensions reads Weyl 3.29, return 3.26, growth 2.33, metric 2.17. The Weyl fit is falling with n (5.40 to 2.73) and the return fit rising (1.12 to 2.77), and they cross only around n = 1024, so nothing shows a plateau. Doors rise with block size up to about 90 sites and then saturate near 23. β = 1.2 was one point on a grid, not a selected value. It is the obvious next thing to scan.

**5. Wholes that hold cost extent. This is the sharpest result.** My derivation (d) for when the plane accepts a level was wrong, which P3 exposed. A product of blocks has modes that span several levels at once, so the gap factor under a block with K levels above it is 1 − S_K, with S_K = r + r² + ... + r^K, not 1 − r. Corrected:

a_K = (1 − S_K) q / (q + S_K), which exceeds ½ if and only if S_K < q / (2q + 1), with q = b/(b−1) for complete blocks.

In a deep tower this is r < q/(3q+1). The corrected form matches the plane's gap and a to within .001 on every level compared, and its level count on 31 of 31 product rows (one is an exact tie at a = ½; one is at the plane's cap of six gaps). Post hoc, and close to exact arithmetic on a known spectrum, so this is a derivation checked rather than a prediction confirmed. The consequence, for all levels held in a deep tower:

| Block size b | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 16 |
|---|---|---|---|---|---|---|---|---|---|
| Largest d_s | 1.11 | 1.69 | 2.10 | 2.41 | 2.67 | 2.88 | 3.07 | 3.24 | 4.05 |

So in this family, with blocks of two, every level can hold as a whole only below d_s = 1.11, and three-dimensional diffusion with all levels held needs blocks of at least 8. The rule makes pairs (over 99% of blocks, Finding 8), and the runs agree: FROZEN r = .25 holds levels at d_s .81, while FREE reaches 1.5 and holds essentially none (0 to .2 accepted levels at n = 512). The threshold a > ½ is a chosen cut, so these numbers move with it; the shape of the trade does not. Measured d_s on the short b = 7 and 8 towers is only 2.1 (Weyl) and 2.6 (return), so the 3.07 is the formula's asymptote, not something observed.

**Correction, same day.** This table is for levels that stand out (a > ½). If levels only have to hold (A > ½), pairs allow d_s up to 3.42, and any block size allows three dimensions. So the statements above about pairs and three dimensions apply to sharply separated levels only. The fuller table is in the Theory of Wholeness draft, https://claude.ai/artifact/58ahYtFyKbQtDHEggdvEte.

This is one answer to the relayed question about simultaneous persistence of part autonomy and greater-whole integration: within this family, persistence at every level has a price in extent, and block size buys it back.

**6. FREE builds the levels and then erases them as wholes.** The nesting survives as wiring but not as wholes. In FREE, surviving edges carry nearly equal weight within each level's lower range (weight per edge about .45 through levels 0 to 2), and A stays near .4 at every scale. FROZEN keeps A at about .7 to .9 across the lower levels, but its d_s is then set by the chosen r (.81 at .25, 1.17 at .4, against formula values 1.00 and 1.51), so it is a free parameter there, as N5 predicted.

**7. The doors lemma (exact, N1).** Summing the site budget over a bipartition gives |A| − Σ_A s = |B| − Σ_B s. So a balanced bipartite whole cannot pass outward share through one door or through two doors on one side: the LP gives zero for pair, C4, C6, C8, Q3, Q4, K33, and about 2 through two opposite doors. An odd cycle's incidence matrix has full rank, so one door is allowed: C3, C5, C7, K4, K5, prism and Petersen all pass .996 to .998 through any single door. **The smallest whole with a single door is the triangle.** The pair, the rule's commonest block, always needs two doors, which is why level 0 shows doors 2.0 and level 1 climbs.

**8. Blocks form as predicted, with exceptions at large size (N2, P1).** Mean block size 2.06; 99.3% pairs. It shifts by .085 across n, .013 across β0, .011 across noise, .117 across level. Pairs plus odd cycles are 99.82% to 99.90% of blocks at every size. Long odd cycles do form, which fits the half-integral extreme points of the fractional perfect matching polytope. The rest are rare odd-sized blocks, up to 67 sites in this shape check (the block run saw sizes up to 71) with maximum degree up to 5, which are neither; at m = 1024 and 2048 they are 13 and 7 against 31 and 3 odd cycles, so they are a sizeable share of the non-pair blocks. I predicted these would be patterns unsettled at the 300-step limit, and did not test that.

**9. My stated guess was overturned by hand before any run.** I had said nesting would give "a growth exponent set by the block ratio." In the symmetric state with level weights w_l, the fixed point gives r = b^(−β/(1−β(1−γ))) and **d_s = 2(1/β − 1 + γ), with b cancelling.** The formula held within 10% on 28 of 42 cases and within 22% on all but one, the case that never separated, and two of the misses were flagged in advance. But the state it describes is not where the dynamics end (N6): from that fixed point plus 2% noise, mean degree falls by between a third and three quarters in all ten cases. At γ = 1, β ≥ 1.5 the end-state d_s is close to twice the formula (ratios 1.86 to 2.08), on n = 243 and 256 only, a post hoc pattern not tested further. The mean-field formula with measured κ does not predict the grown networks either (at β = 3 it gives about 3 against a measured 1.17), so the numbers in Finding 3 remain measured, not derived.

**10. Capacity across levels needs the finite tower.** N4 missed outright: slow-mode crossings sat 20%, 38%, 37% and 37% above r* = q/(1+q). r* assumes infinitely many levels above, and the tested towers had 2 or 4. The finite form is q = r + ... + r^K. On A = ½ this is nearly arithmetic and fits to three digits (.742, .823, .758, .618 against .741, .823, .759, .618). The real test used the slow-mode crossing on towers not seen before (P2): 14 of 14 within 15% of the finite root, and closer than r* in every case. It is not exact: the crossing is always above the root, by 2.8% to 12.9%, and even at K = 8 it sits 10% above r*. That offset is unexplained.

## Prediction ledger

Frozen before running, except P1 to P4, frozen after seeing the N results and before running those checks.

| | Prediction | Result |
|---|---|---|
| N1 | Doors lemma LP | **Pass**, exact |
| N2 | Pairs and odd cycles, mean in [2.0, 2.6], pairs ≥ 60%, shift < .2 | **Pass** on all numbers; 99.8%+ of blocks fit the shapes, rare other blocks exist |
| N3 | Symmetric formula within 10%; independent of b; collapse outside the window | **Partial**: 28 of 42; collapse right; 2 of the 14 misses flagged in advance |
| N4 | Slow-mode crossing within 15% of r* | **Miss**, all four (20% to 38% high) |
| N5 | d_s within 10% for r ≤ .6 | **Partial**: 27 of 36 on Weyl |
| | Hop diameter ≤ L + 1 | **Pass**, 32 of 32 |
| | Levels accepted only below (d) thresholds, within .05 | **Mostly**: one family over (spread b=3, r=.40); the thresholds themselves were wrong, Finding 5 |
| | Midpoint ≥ .8 for r ≤ .5; ≤ .65 for ring, torus, gasket | **Miss** on the first: 14 of 30, product only 4 of 20; **pass** on the second |
| N6 | Symmetric state unstable: spread ×10, degree under L/2 | **Partial**: 5 of 10 and 6 of 10; the instability itself holds in all ten |
| N7 | Main test, four clauses | **Miss by one clause**, the power fit at n = 1024 |
| N8 | Diameter exponent in [.35, .8], ≥ .1 above baseline; d_s in [1, 2] at γ=1; shift < .15 | **Mostly**: β=1.2 misses both (.349, 2.73); the baseline gap is +.275; shift .04 |
| N9 | d_s ≤ 2γ + .2 in every FREE configuration | **Miss** at γ=1, β=1.2 (setting aside fit blow-ups at n = 32) |
| N10 | FREE ≤ 1 level, degree ≤ 3.2 and stable | **Mostly**: γ=½ has 3.2 levels; β=1.2 has degree 4.87 |
| | FROZEN r=.25 ≥ 3 levels with a, c > .7; doors grow slower than size | **Miss** on levels (2.0 at n = 512) and on a, c; **pass** on doors |
| N11 | γ=0 disconnected; γ=½ connected ≥ 80%, d_s ≤ 1.2 | **Partial**: γ=0 right; γ=½ fragments at n ≥ 256 (d_s clause holds). Its upper levels are very weak, so the support cutoff may be involved |
| N12 | Rings < 25%; FREE midpoint ≤ .65 | **Pass**, rings 0 everywhere; except γ=½ midpoint .73 to .83 |
| P1 | Pairs plus odd cycles ≥ 99% at every m | **Pass** |
| P2 | Finite-tower root within 15% on new towers | **Pass**, 14 of 14 |
| P3 | At r = b^(−2/3): none for b ≤ 4, at most one for b=5, all for b ≥ 6 | **Miss at b=6** (1 of 3); rest right. Exposed the wrong gap factor |
| P4 | At T=600: β=2 stable; β=1.2 falls below degree 4 and d_s 2.5 | **Pass** for β=2 (d_s moved .01, diameter 4.5%); **miss** for β=1.2 |

## What came from where

- **From "nested" itself:** the order (sites relate only once their wholes merge), and through it the stretched geometry and the constant doors.
- **Added, not derived:** β > 1 and energy shared by mode (γ > 0), both carried over from the earlier record; bottom-up order with one merge at a time; the block-forming rule (γ = 0) being different from the energy rule; existing support only; the plane's a > ½.
- **Chosen by me as test settings:** β = 2, t0, T, the 1e-5 support cutoff, noise.
- **Not inherited:** geometry. Fresh noise at every level.

## Retained readings, not canon

- **Doors and the boundary.** In a space of D physical dimensions, the surface of a region grows as size^((D−1)/D), so a whole's doors would grow as size^(2/3) in three dimensions, which is κ = 1/3. This rule gives κ near 1. So "doors per whole against size" is a sharp, cheap test for any rule claiming physical space, and it connects to ○ as an area in the physical-space expression. In the mean-field formula, κ = 1/3 with d_s = 3 would need γ = 2 − 1/(2β), so γ between 1.5 and 2 for β ≥ 1. Arithmetic only, not tested.
- **FREE in the plane.** FREE blocks read as high c, low a, which is the absorption corner. Nesting that lets levels renegotiate their shares dissolves its parts into the whole; holding them needs a constraint the energy rule does not supply. A reading only, and the earlier record found a and c are not independent.
- **Concordances noticed and not claimed.** (a) d_s near 1.5 at γ=1, β=2 against D = 1.5 at balance: it moves to 1.17 at β=3 and 1.67 at β=1.5, and β=2 was my setting. (b) 8 as the smallest block for three dimensions with all levels held, against 2³ and SU(3): it depends on the a > ½ cut. (c) r = 1/φ for the ring of 4 with two levels above: it comes from q = 1 and K = 2, which my test set chose, and it goes to ½ in a deep tower. (d) The triangle as smallest single-door whole, against T = 3: a real theorem about the site budget, with no shown link to T. (e) Nested pairs with matching contact form a hypercube, against the corpus's Q₆: the rule does not produce matching contact.

## Practical note

The first full run of the block part was stopped at 93 minutes. It was not stuck: it ran dense matrix sweeps on matrices already about 99.9% zeros, reported nothing and saved nothing, and my estimate of under an hour was wrong. Sparse sweeps gave identical blocks on 12 test cases (maximum difference 2e-13). The full run then took about 50 minutes. The first attempt's work was lost; no prediction changed.

## Open decisions (Ashman to adjudicate)

1. **The verdict.** "Locality yes, thin, up to n = 1024; a dimension no." Countersign, or tell me what would count differently, given that the frozen N7 strictly failed.
2. **Which nesting is the circumpunct's?** FREE lets levels dissolve into wiring and reaches d_s 1.5. FROZEN keeps wholes and stays below about 1.1 with pairs. If a whole must persist as a whole at every scale, FROZEN is closer, and it needs a constraint the energy rule does not give.
3. **Is the block rule right?** Pairs come from the γ = 0 rule. Finding 5 says larger blocks are what buy extent and held levels together, and nothing here makes blocks of 8. Is a block size something to derive, or is a pair the honest smallest whole?
4. **The doors law as a target.** Adopt doors against size as the test for any rule claiming physical space?
5. **Next test.** Scan β from 1.05 to 1.5 at n up to 2048, to see whether the β = 1.2 behaviour plateaus or moves smoothly. This is the one place the rule came near three dimensions.
6. **The two errors in my hand work.** The wrong gap factor in (d) and the infinite tower in (c) are corrected only here. The frozen docstring keeps them as written.

## Files

- `plans/graph_from_self_limitation_2026_11_04.md`: predecessor; its open decision 8 now points here.
- `experiments/graph_from_nesting_v1.py`: the rule, hand derivations, frozen predictions N1 to N12. Run: `python graph_from_nesting_v1.py OUTDIR [doors blocks formula capacity static dense grow]`, about 50 minutes on 16 cores.
- `experiments/graph_from_nesting_posthoc_v1.py`: P1 to P4, the corrected gap check, and the tally behind this ledger. Run after the above: `python graph_from_nesting_posthoc_v1.py OUTDIR [shapes finite holds longT gaps tally]`, about 15 minutes.
- `experiments/graph_from_self_limitation_v1.py`, `experiments/wholeness_plane_criterion_v1.py`: imported.

## Sources

Standard mathematics, from memory and not re-checked in this session: Foster's theorem on effective resistance; half-integrality of the fractional perfect matching polytope (Balinski); Weyl counting and return probability as definitions of spectral dimension; the hierarchical contact pattern called "spread" here resembles Dyson's hierarchical model. No outside source is relied on for a result.
