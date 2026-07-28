# The exact regret closes the accounting; the slope law is not yet tested

```
Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
```

*Code: `pole_gap_frontier_v1.py`. Tests Ashman's exact KT regret tax and his usable-integration-frontier slope prediction. Three binary Markov sources of true order K = 10 with coefficient decay 0.55, 0.70, 0.85; stationary distributions solved exactly, so every H_k is exact; 250,000 symbols each, depths 1 to 10, nine budgets from 1,000 to 249,000.*

---

## 1. The exact regret makes the accounting an identity (confirmed)

Using r_KT(n₀,n₁) = −log₂ Q_KT(n₀,n₁) − N·h₂(n₁/N) summed over visited contexts:

| source | \|L − (Ĥ_k + R_KT)\| |
|---|---|
| decay 0.55 | 9.10e-15 |
| decay 0.70 | 1.53e-15 |
| decay 0.85 | 1.63e-15 |

Machine precision. This is not an improved approximation, it is an identity: KT's sequential-to-block property forces realized loss per symbol to equal the empirical plug-in conditional entropy plus the exact regret. The singleton cost appears automatically at exactly 1 bit, with no fitted constant, as predicted.

**Consequence:** predicting H_k + R_KT leaves a residual of exactly H_k − Ĥ_k, the gap between the true and empirical conditional entropy. The tax model is now perfect and the entire remaining error is an entropy-estimation problem.

**My prediction about that residual was wrong.** I expected it to be the plug-in bias, recoverable by Miller-Madow. Measured residuals are −0.000673, +0.002727, −0.003508 against Miller-Madow estimates of +0.001443, +0.001330, +0.000073. Wrong sign twice. At these sample sizes ordinary sampling fluctuation of Ĥ_k dominates its bias, so Miller-Madow does not capture it. The residual is exactly characterised; it is just not the term I named.

## 2. The slope law: NULL RESULT, underpowered rather than falsified

Prediction: dk\*/d(ln n) = 1/(α+β) with β = ln 2.

| source | fitted α | predicted slope | measured slope | ratio |
|---|---|---|---|---|
| 0.55 | 1.363 | 0.486 | 0.555 | 1.14 |
| 0.70 | 1.063 | 0.570 | 0.386 | 0.68 |
| 0.85 | 1.077 | 0.565 | 0.674 | 1.19 |

Ratios scatter from 0.68 to 1.19 with no trend. More damningly, the predicted slopes barely vary across the three sources (0.486, 0.570, 0.565) while the measured ones vary widely and in a different order, so **this design has no discriminating power**. It neither confirms nor refutes the law.

Four reasons, all fixable:

1. **k\* is integer-valued** and moves over only 3 to 5 units across the whole budget range. Regressing a 4-valued step function on 9 points estimates where the steps landed, not a slope.
2. **The α fits are poor.** Source 0.85 gives ΔH_k ratios of 0.26, 0.12, 0.34, 0.33: not exponential, so the fitted α is not measuring what the law assumes.
3. **Source 0.85 is outside the regime.** H₁ = 0.041 means one bit nearly determines the next; k\* sits at 1 until n = 128,000 and then jumps to 5. The asymptotic argument does not apply to a near-deterministic source.
4. **One seed per source, no error bars.**

A real test needs an interpolated (non-integer) k\* from the fitted loss curves, budgets spanning many more decades, several seeds per source, and sources chosen so that α varies over a wide range while ΔH_k stays cleanly exponential. Until then the law is a conjecture with an untested constant.

## 3. A third body of prior art: AR order selection

The classification (exponential decay of predictive gain giving log n growth, power-law decay giving a power of n) is the known shape of results in **model-order selection for infinite-order autoregressive processes**, where the order is allowed to grow with the sample size. Shibata (1980) is the standard reference for the asymptotically efficient version, and the subsequent literature on same-realization prediction and infinite-order AR selection treats exactly the question of how fast the optimal order should grow.

I have not read Shibata closely enough to state the correspondence precisely, and that check should be made before the classification is presented as new. What may survive as distinctive is the joint framing in terms of observer *architecture* (the β exponent as a property of how the observer organises contexts, testable by fixed-order against CTW) rather than of the estimator alone.

## Revision history

- 2026-07-27 v1.0: initial. Exact-regret identity confirmed to 1e-15; residual characterised exactly but not by Miller-Madow, contra my prediction; slope law untested by an underpowered design; AR order selection flagged as a third prior-art literature.
