# Pilot attempt: three defects, no valid endpoint, one usable effect-size estimate

```
Created: 2026-07-28
Last updated: 2026-07-28
Version: 1.0
```

*Code: `pole_gap_pilot_v1.py`. Two runs of the matched-pair pilot specified in the protocol. Neither produced a valid primary endpoint. This document records the defects and the one number worth keeping.*

---

## Verdict

**No result.** The pilot did not measure what it was built to measure, across two attempts. What follows is a defect list and an effect-size estimate salvaged from the checkpoints that did fire.

## The three defects

**1. The primary endpoint never fired, twice.** Observers begin scoring at index D = 16, and the substrate generator supplies only `PILOT_N + BURN + 2` rows, so the maximum reachable scored count is 49,985 against a declared endpoint of 50,000. Every primary-endpoint cell is NaN in both runs.

The second attempt is the instructive one. I "fixed" this by widening the `min()` bound that caps the stream, without checking that the endpoint actually fired. That is trusting the code change as an indicator of the thing it was supposed to produce, which is the exact failure mode this program is named after, committed by the author of the section describing it.

**2. Functional duplicates in the projection bank (fixed).** `maj{r}` and `den{r}>{r//2}` compute the identical projection. Three such collisions existed, so the first run's four "matched pairs" were three distinct pairs with the only informative one double-counted. That would have satisfied the protocol's "not carried by only one pair" criterion falsely. Fixed by deduplicating on the projected stream rather than the name: the bank drops from 40 to 35.

**3. Sentinel values consumed as measurements.** `stats()` returns `(0.0, 1.0, 0.0)` when no context clears MINCOUNT. At the calibration budget of 20,000 symbols with depth 12 and MINCOUNT 20, **zero** contexts clear the threshold for the XOR projections:

| projection | CAL_N | contexts occupied | clearing MINCOUNT | reported V, H |
|---|---|---|---|---|
| xor9 | 20,000 | 4,067 | **0** | 0.00, 1.0000 (sentinel) |
| xor7 | 20,000 | 4,066 | **0** | 0.00, 1.0000 (sentinel) |
| xor9 | 60,000 | 4,096 | 433 | 20.60, 0.1503 (real) |
| xor7 | 60,000 | 4,096 | 444 | 18.71, 0.1491 (real) |

The pair selector then matched two sentinels as a "pair" with ΔV = 0.00 and identical H = 1.0000, and it entered the primary statistic as one of four. A measurement failure was silently promoted to a measurement, and then to a data point.

This also means the calibration budget matters more than the precondition study made it look: at 20,000 the XOR family is entirely unmeasurable at depth 12, and its earlier V_π figures came from 60,000, where coverage is adequate.

**4 (design, not a bug).** The selector has no minimum-ΔV requirement. After deduplication only three pairs with meaningful ΔV exist under the non-overlap constraint, so the fourth slot falls to whatever remains, which was the sentinel pair.

## The one thing worth keeping

Across the three genuine pairs, at the checkpoints that did fire:

| pair | 10k | 20k | 35k |
|---|---|---|---|
| blk7off4 − blk7off2 | −0.0000 | −0.0000 | 0.0000 |
| den11>6 − den7>4 | −0.0000 | 0.0000 | 0.0002 |
| maj9 − maj7 | −0.0024 | −0.0020 | −0.0014 |

**The effect scale is at or below 0.002 bits per symbol, and two of three pairs are indistinguishable from zero at four decimal places.** That is the number the escalation rule needs, and it is discouraging: a powered confirmation of an effect this small needs either far more replication than the protocol's next tier supplies, or a substrate where the contrast is larger.

The sign is mixed and mean-negative, which is against the hypothesis, but with one pair carrying all the magnitude and no valid endpoint, the direction should not be read at all.

## What a valid rerun requires

- Generate `PILOT_N + BURN + D_CAP + margin` rows, and **assert** that every declared checkpoint fires rather than trusting the bound.
- Raise the calibration budget until context coverage is adequate for every family (60,000 sufficed at depth 12; 20,000 does not), and make `stats()` raise rather than return a sentinel.
- Require a minimum ΔV for pair admission, and report how many admissible pairs exist rather than padding to four.
- Only then interpret a direction.

## Note on stopping

Three consecutive attempts produced three distinct defects, the last being sentinel-as-data. That rate is itself a signal about the reliability of the operator at this point in a very long session, and the honest response is to stop and document rather than attempt a fourth patch. The harness is committed with its faults listed so the next attempt starts from a known state.

## Revision history

- 2026-07-28 v1.0: initial. Two pilot attempts, no valid primary endpoint; duplicates fixed, endpoint and sentinel defects documented and unfixed; effect scale estimated at ≤ 0.002 bits/symbol.
