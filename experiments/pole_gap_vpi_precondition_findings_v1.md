# The two-family design is unidentifiable, and the replacement is in the same data

```
Created: 2026-07-27
Last updated: 2026-07-28
Version: 1.1
```

> ## RETRACTION NOTICE (2026-07-28)
>
> **The central claim of this document is withdrawn.** Sections 2 and 3 below are wrong, and section 1 is unreliable. Ashman's audit of the harness found that the entropy figure this study used is a partial-mass sum: `stats()` weights each qualifying context by `m / tot` where `tot` includes contexts excluded by MINCOUNT, so the reported quantity is ρ · H_qualified, with ρ the fraction of sample mass in qualifying contexts.
>
> The two families differ enormously in ρ, and barely at all in entropy:
>
> | family | ρ | H reported | H renormalised | H over all occupied |
> |---|---|---|---|---|
> | aggregating | 0.68 - 0.82 | 0.665 - 0.805 | 0.939 - 0.986 | 0.914 - 0.976 |
> | algebraic | 0.14 - 0.16 | 0.138 - 0.157 | 0.901 - 0.971 | 0.890 - 0.957 |
>
> **The difficulty gap was a coverage gap.** XOR projections spread mass evenly so few contexts clear MINCOUNT; aggregating projections concentrate mass so many do. A fivefold ρ difference produced the fivefold H difference.
>
> **Amendment (2026-07-28, second pass).** The corrected values in the row above were themselves computed on the misaligned contexts of defect 4: they condition on O_{t−1} onward and never include O_t. They destroy the claimed empty separation, but they do not characterise the intended task. A separate aligned audit gives, at n = 60,000 and D = 12:
>
> | family | H_qualified (aligned) | H over all occupied (aligned) |
> |---|---|---|
> | aggregating | 0.759 - 0.973 | 0.722 - 0.969 |
> | algebraic | 0.331 - 0.969 | 0.341 - 0.956 |
>
> So **the ranges overlap and matching is not impossible**, which is the load-bearing retraction and it survives alignment. But this sentence does not survive and is withdrawn: *"Every projection in both families is nearly maximally unpredictable at depth 12."* Aligned xor3 sits at 0.331 bits and maj3 at 0.759, while others remain near 0.96. The spread within the algebraic family alone is 0.638 bits. The intended task contains far more difficulty variation than the shifted task revealed.
>
> Consequences: the "empty overlap" result is false; matching is not impossible; the pooled corr(V_π, H) = +0.797 measures coverage rather than a genuine confound; and the recommendation to abandon the two-family contrast rested on a false premise.
>
> **V_π is retracted and has two faults, not one.** First, coverage: it is computed over the same MINCOUNT-qualified subset, so at 15% coverage it describes a biased, high-count minority of contexts, and the z = +7.26 separation may be measuring coverage structure. Second, and surviving any coverage repair: the estimator fits the depth-D conditional probability and then searches for the shortest suffix resembling *that same estimate*, on the same observations. Selection and target share their noise, so ℓ(c) is optimistic and unstable wherever the deep context is sparse, and a noisy deep estimate can make some shorter suffix look adequate by chance.
>
> The repair is sample separation: fit the deep and suffix models on calibration-train, and declare adequacy by held-out predictive loss on calibration-validation. Difficulty and heterogeneity then become separate instruments with separate failure states, and coverage is reported alongside both rather than multiplied into either. No context should silently vanish from a difficulty estimate; sparse ones get KT or shrinkage, not omission.
>
> **Status after this notice:** empty family separation, retracted. Matching impossible, retracted. Families nearly equally difficult, unsupported. V_π separation, retracted pending aligned held-out estimation. The projection-by-architecture hypothesis, still untested.
>
> The next run should not be another CTW pilot. It should be a measurement-validation study showing that aligned, held-out estimates of difficulty and V_π are stable across seeds and calibration budgets.
>
> Verification: `pole_gap_defect_audit_v1.py` (defects 4 and 5) and `pole_gap_aligned_audit_v1.py` (the aligned ranges, with an alignment oracle applied to the entropy function itself). Nothing below this notice has been edited; it is left as written so the error is legible.

*Code: `pole_gap_vpi_precondition_v1.py`. Pilot for the projection x architecture protocol (`plans/pole_gap_boundary.md` §6). Calibration only: rings 101 and 151, n = 60,000, D = 12, forty prospective projections per family built by rule before any results were seen. No CTW, no architecture comparison.*

---

## 0. A compute constraint, stated first

The smallest credible confirmatory version specified in the protocol (40 projections x 4 ring widths x 25 initial rows x 200,000 symbols x 2 observers) is on the order of 8x10⁸ symbol-steps per observer. In pure Python, with CTW costing roughly 40 node operations per symbol, that is not runnable in this environment. Any confirmatory run needs either vectorised observers or a scale reduction of two orders of magnitude. This does not affect the pilot below, which requires only context counting.

## 1. Precondition 1 passes: the families do generate different V_π

| family | V_π mean | median | range | n |
|---|---|---|---|---|
| aggregating | 23.098 | 23.195 | [17.879, 26.581] | 40 |
| algebraic | 18.051 | 18.048 | [14.961, 20.621] | 40 |

Mann-Whitney U = 1554, **z = +7.26**. The separation is not marginal.

## 2. Precondition 2 fails: difficulty matching is impossible

| family | entropy-rate range |
|---|---|
| aggregating | [0.2370, 0.9925] |
| algebraic | [0.1288, 0.1770] |

The overlapping band is **empty**: the easiest aggregating projection (0.2370) is harder than the hardest algebraic one (0.1770). Every algebraic projection is systematically more predictable than every aggregating one.

Pooled across all 80 projections, **corr(V_π, H) = +0.797**. The family contrast therefore cannot identify γ₁ from γ₂: a between-family effect could be depth heterogeneity or could be difficulty, and no matching procedure can separate them because the supports do not intersect. The protocol's §3 requirement is unsatisfiable with these families on this substrate.

**Likely mechanism, offered as conjecture.** Rule 30's update is l ⊕ (c ∨ r). XOR combinations of cells partially preserve the linear component of that update while majority and density projections destroy it, which would make algebraic reads systematically more predictable on this substrate specifically. If that is right, the confound is structural rather than an artifact of how the bank was drawn, and it would recur on any XOR-based rule. Untested.

## 3. The replacement design is visible in the same numbers

| family | corr(V_π, H) within | V_π range within | H range within |
|---|---|---|---|
| aggregating | +0.303 | [17.88, 26.58] | [0.2370, 0.9925] |
| algebraic | **+0.073** | [14.96, 20.62] | [0.1288, 0.1770] |

Within families the confound largely disappears. The algebraic family alone spans 5.7 units of V_π while its entropy rate varies by only 0.05 and the two are essentially uncorrelated (r = 0.07). That is close to the ideal identifying design: vary the mechanism, hold difficulty fixed.

**Recommended revision to §6.** Drop the between-family contrast, which was always post-hoc scaffolding from the withdrawn result. Use within-family V_π variation as the identifying variation, with family as a fixed effect and H retained as a control. Run the algebraic family first, since it offers near-orthogonal V_π variation and needs the weakest assumptions. The regression in §7 is unchanged; only the source of identifying variation moves.

This also reduces the compute problem: the primary arm becomes 40 projections rather than 80, on one family.

## 4. What the pilot cost and what it saved

Four minutes of context counting, against a confirmatory run that would have produced a between-family difference guaranteed to be uninterpretable. The failure mode it caught was listed in the protocol as "the relationship disappears after difficulty matching"; what it actually found is worse and cheaper to know, that the matching step is impossible.

## Revision history

- 2026-07-27 v1.0: initial. V_π separation confirmed (z = +7.26); difficulty overlap empty; pooled corr(V_π, H) = +0.797 kills the two-family design; within-family correlations of +0.303 and +0.073 identify the replacement.
