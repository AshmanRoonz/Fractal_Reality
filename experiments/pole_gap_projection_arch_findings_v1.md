# Projection x architecture, attempt 1: an apparent flip the design cannot support

```
Created: 2026-07-27
Last updated: 2026-07-27
Version: 1.0
```

*Code: `pole_gap_projection_arch_v1.py`. Ashman's §6 question: hold the substrate fixed, sweep the projection, and ask whether the ranking of observer architectures changes. Rule 30 ring 15, five projections of the same state, fixed-order KT against CTW (implemented here; sanity-checked at 0.738 bits on an iid p = 0.8 stream against a true entropy of 0.722, so its redundancy is behaving).*

---

## What came out

At n = 79,000, CTW loss minus best-fixed loss:

| projection | CTW − fixed | apparent winner |
|---|---|---|
| majority of 3 | −0.0037 | CTW |
| block density > 3 | −0.0024 | CTW |
| parity of 3 | +0.0046 | fixed |
| center cell | +0.0047 | fixed |
| two separated cells | +0.0062 | fixed |

The sign flips across projections, which is the result the question was looking for. **I do not believe it,** for three reasons, all mine.

## Why the design cannot support it

**1. The fixed-order arm is oracle-selected.** F_fixed is min over k of the realized loss, so the fixed observer is handed the best depth for free while CTW pays for not knowing it. That is precisely the quantity CTW's theorem is about: its model redundancy is the price of not being told k. Finding CTW slightly behind an oracle is the theorem working, not evidence about projections. A fair comparison charges the fixed arm for selecting k, or compares CTW against a realistic selection rule.

**2. The fixed optimum is pinned at the tested maximum.** Best k came out at 19 or 20 in every single row, with D = 20 the deepest tested. The centre column needs k_min = 21, so the fixed observer is still improving where I truncated it. F_fixed is a truncation artifact rather than an optimum, and the gap being measured is partly the gap to a depth I did not run.

**3. One seed, no error bars, differences of 0.005 bits.** The flips are 5 to 7 percent of losses near 0.07, from a single substrate initial condition. Nothing here separates them from noise.

There is a fourth, softer problem: the five projections produce nearly identical difficulty (F_fixed of 0.070, 0.083, 0.069, 0.070, 0.080). They are not probing different regimes, so there is little contrast for an interaction to show up in.

## The hypothesis it did generate

The two projections where CTW led are the two that *aggregate* cells (majority of three, block density). The three where it trailed are all sharp or algebraic reads of specific cells (centre cell, parity of three, XOR of two separated cells). If that survives a proper design, the mechanism would be that aggregating projections induce sparse, variable-depth dependence, which is exactly the structure CTW's mixture exploits and a fixed depth cannot, while algebraic projections induce uniform-depth dependence where a single well-chosen k is adequate.

That is a real, testable prediction about projection-architecture interaction, and it is the kind of claim none of the three prior-art literatures obviously supplies. It is a hypothesis from a broken experiment, not a finding.

## What a valid version needs

- D beyond k_min for the hardest projection (28 or more on ring 15), so the fixed optimum is interior.
- The fixed arm charged for model selection, or compared against a switching rule rather than an oracle.
- Many seeds, with paired differences and confidence intervals, and a crossing declared only when the interval stays on one side across successive budgets (the same uncertainty-aware rule the crossover work needs).
- Projections chosen for contrast in difficulty, not five reads of similar hardness.

## Revision history

- 2026-07-27 v1.0: initial. Apparent architecture-ranking flip across projections, withdrawn on three design defects (oracle-selected fixed arm, optimum pinned at the truncation depth, single seed). Kept for the harness, the CTW implementation, and the aggregating-versus-algebraic hypothesis.
