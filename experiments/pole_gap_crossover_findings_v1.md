# The occupancy tax works, the interior optimum is real, and it converges far slower than the true order

```
Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
```

*Code: `pole_gap_crossover_v1.py`. Builds the testbed Ashman specified and tests the three predictions in his 2026-07-27 reply. Source: binary Markov of true order K = 12, P(Y=1 | y) = σ(b + Σ a_j (2y_j − 1)) with a_j = 1.15·0.72^j, b = 0.10, p ranging over [0.019, 0.984]. The stationary distribution over 4,096 states converges to L1 delta 1e-14, so every H_k is exact rather than estimated. 600,000 symbols, depths 1 to 16.*

---

## The exact structural entropies

| k | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 (true order) |
|---|---|---|---|---|---|---|---|---|
| H_k | 0.240013 | 0.184448 | 0.168353 | 0.163279 | 0.161386 | 0.160643 | 0.160226 | 0.160151 |

The declining coefficients make ΔH_k decay geometrically. Everything below follows from that.

## (A) The interior optimum is real and it migrates

| n | 1,000 | 3,000 | 10,000 | 30,000 | 100,000 | 300,000 | 590,000 |
|---|---|---|---|---|---|---|---|
| empirical k\* | 4 | 4 | 4 | 6 | 6 | 6 | 6 |
| predicted (occupancy) | 3 | 4 | 4 | 5 | 5 | 6 | 6 |
| predicted (crude) | 2 | 3 | 3 | 4 | 5 | 5 | 6 |

Confirmed: an interior optimum exists, sitting at depth 4 to 6 while the true order is 12 and the deepest observer tested is 16. It migrates upward with budget. The occupancy prediction tracks it within one step at every checkpoint and exactly at three; the crude prediction lags by one to two steps almost everywhere.

**Not confirmed: convergence to the true order.** k\* stalls at 6 and shows no sign of reaching 12 within 590,000 symbols. This is not noise, it is structural. ΔH_k decays geometrically (0.0556, 0.0161, 0.0051, 0.0019, 0.0007, 0.0003, ...) while the learning tax decays as roughly 1/n. So the crossover budget grows geometrically in k, and k\*(n) grows only like log n.

That is a sharper claim than "k\* eventually stabilizes around K": for a source whose dependence decays geometrically, the depth an observer should actually use is far below the true order at any realistic budget, and closing the last few orders costs exponentially more experience than the first few. The true order is a fact about the source that a bounded observer has no business trying to reach.

## (B) The occupancy tax is decisively better

Realized loss versus predicted (H_k + tax) at n = 100,000:

| k | realized | H_k + occupancy | error | H_k + crude | error |
|---|---|---|---|---|---|
| 4 | 0.1615 | 0.1640 | +0.0026 | 0.1646 | +0.0031 |
| 6 | 0.1594 | 0.1627 | +0.0033 | 0.1660 | +0.0066 |
| 8 | 0.1607 | 0.1646 | +0.0039 | 0.1811 | +0.0204 |
| 12 | 0.1666 | 0.1681 | +0.0016 | 0.2575 | +0.0909 |
| 16 | 0.1763 | 0.1715 | −0.0049 | 0.3488 | +0.1725 |

Mean absolute error: **0.0031 for the occupancy tax, 0.0546 for the crude one, a factor of 17.6.** The crude formula's error grows monotonically with depth, exactly as the ring-15 failure predicted: it charges for contexts the observer has never visited.

**The residual is located precisely.** The occupancy tax over-predicts slightly at shallow depths and *under*-predicts at deep ones (−0.0014, −0.0031, −0.0049 at k = 14, 15, 16). The cause is the term Ashman flagged as lower-order: a context seen once contributes log₂(1) = 0 to Σ log₂ N_c, but costs a full bit in realized loss, since a fresh context is priced at one half. At large k most contexts are singletons, so the missing per-context introduction cost is exactly where the error appears. Adding a constant times the visited-context count should close it.

## (C) The crossover budget predicts where it can

| k → k+1 | ΔH_k | observed n | predicted n |
|---|---|---|---|
| 1 → 2 | 0.05557 | 1,000 | 1,000 |
| 2 → 3 | 0.01609 | 1,000 | 1,000 |
| 3 → 4 | 0.00507 | 1,000 | 2,000 |
| 4 → 5 | 0.00189 | 20,000 | 20,000 |
| 5 → 6 | 0.00074 | 30,000 | 200,000 |
| 6 → 7 and deeper | ≤ 0.00030 | >590k | >590k |

Three exact hits, one within a single grid step, one clear miss at 5 → 6, and agreement on every "not within budget" case. The equation works wherever ΔH_k is large enough to be resolved above sampling noise and becomes meaningless at the 1e-5 level.

**One row is my error, not the equation's.** At k = 9 → 10 the run reports an observed crossover at n = 1,000 where ΔH is 0.00002. That is a finite-sample fluctuation, and it registered because my detection rule takes the *first* n where the deeper observer's loss dips below the shallower one, with no persistence requirement. That is the same class of mistake as the page's threshold light, made by me, hours after I caught it there. Any future version needs the crossing to hold for a sustained window.

## What this means for the program

The occupancy tax should replace the crude one everywhere. The interior optimum is a real phenomenon rather than an artifact of Xorzo2's byte alphabet, and it appears on a clean binary source with a known generator.

The candidate for genuinely new content has shifted. It is not "more memory can hurt," which is standard model selection, and it is not the crossover equation itself, which is MDL bookkeeping. It is the **scaling law**: for a source whose dependence decays at a given rate, how fast does the usable integration depth grow with experience? Geometric decay gives k\*(n) ~ log n and geometrically growing crossover budgets. A source with power-law decay should give a different law. That relation, between the decay profile of a process's dependence and the growth rate of an observer's usable depth, is the quantity worth chasing.

**A caution on the proposed CTW comparison.** The predicted outcome, that a hierarchical observer avoids the fixed-depth fragmentation cost, is the context-tree weighting theorem. CTW weights all bounded-memory tree sources at once, achieves Rissanen's redundancy lower bound, and handles unbounded depth in linear time. Running the comparison is a good calibration of the instrument, and it will confirm a result from 1995 rather than discover one.

## Revision history

- 2026-07-27 v1.0: initial. Interior k\* confirmed and migrating (4 to 6) but stalling far below the true order 12; occupancy tax beats the crude tax by 17.6x with the residual located at singleton contexts; crossover equation confirmed where ΔH_k is resolvable, with one false positive traced to my own detection rule.
