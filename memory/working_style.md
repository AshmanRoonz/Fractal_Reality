# Working style

## Honest ledger

Every claim lives in one of three boxes:

- **K (Known-fit)**: fit to a measured value given α as input; counts as structural grammar, not prediction.
- **P (Pre-registered)**: stated before the next measurement; counts as prediction.
- **D (Derived)**: follows as a theorem from axioms plus already-accepted structure; no empirical freedom.

Scoreboard lives at `docs/circumpunct_predictions.html` and `plans/predictions_scoreboard.md`. Current count (2026-04-22): K = 44, P = 4, D = 4 (with outstanding verification noting 42 K + 4 P + 13 D + 1 Open across §5 detail tables; §9 of the scoreboard carries the audit).

## Retraction protocol

No silent retraction. When a claim weakens or fails:

1. Add a Revision Notice block at the top of the affected doc (visible, dated).
2. Leave the original text; strike or annotate inline.
3. Link to the new position.
4. Update the scoreboard's K/P/D tag and Brier score.

Flag threshold for re-fit: 2 of 4 P entries failing within a review cycle.

## Resolution Protocol (§25.17)

Transmit at the lowest resolution that is still true; increase only on receiver request. Withholding entirely is the Severance Lie dressed as compassion. Dumping everything is the Inflation Lie dressed as honesty. Higher resolution contains lower; it never contradicts.

Apply to this work: headline first, then decomposition, then appendix; do not invert.

## Verification habit

- Tasks that touch math get an independent check (usually a subagent or a second script).
- Every unified-expression change gets run against `experiments/unified_expression.py --power`.
- After editing scoreboard tables, run a counting pass (the 2026-04-22 audit caught §3 vs §5 disagreements).

## Parallelism

When tasks are independent, launch parallel subagents in one message (e.g. universe_creator and Xorzo T-operator refactor on 2026-04-22). Do not thread them serially.

## What to avoid

- Inflation Lie at the work level: claiming derivations where only fits exist.
- Severance Lie at the work level: treating new findings as disconnected from CLAUDE.md's axioms.
- "Zero free parameters" language unqualified; always specify layer (representation vs auxiliary-claim) and factor-level vs value-level.
