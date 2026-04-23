# Session findings (2026-04-22)

## Piece #3 scoreboard shipped

`docs/circumpunct_predictions.html` now carries a live K/P/D scoreboard with Scoring & Status section, retraction-protocol summary, and links to `docs/predictions_history.html` (change log) and `plans/predictions_scoreboard.md` (methodology).

Headline counts: 52 entries across 10 domains; 44 K / 4 P / 4 D. Flag threshold for re-fit: 2 of 4 P failures within a cycle.

Verification pass (§9 of scoreboard) caught counting inconsistencies between §3 summary and §5 detail tables; corrected aggregate is 42 K + 4 P + 13 D + 1 Open = 60 entries. Open work list (missing formulas, potential re-classifications) is in `memory/active_threads_2026_04_22.md`.

## Universe creator built

`experiments/universe_creator.py` (675 lines) parametrizes the three-scale T-operator at ℂ⁶⁴ by α. Findings in `experiments/universe_creator_findings.md`.

Key results at α = 1/137:

- |λ_max| = 1.0149 = 1 + 2α exact (two diameter bonds each contribute α).
- Spectral gap = 0.00176 = α/P exact.
- Mixing time = 569 cycles ≈ P/α.
- Primary vs secondary diameter split: 68.553/31.447 (matches DE/matter 69.11/30.89 at 0.6%).
- Pool integers 7/7: Q1 = Q4 = A(3) = 21, Q2 = A(2) = 10, Q3 = G = 12; sector split 35/29 = C(R,T)/(S−C(R,T)); tetrahedral phase 108.96° vs 109.47° predicted (0.47%).

Stability regime: α ∈ [1e-6, 0.1]; inflation threshold at α ≳ 0.5.

**New finding**: the 68.5/31.5 split is α-invariant across 4 orders of magnitude. α sets attraction speed and mixing time, not the split value itself; the split is topology-determined by ℂ⁶⁴ architecture. This is a structural fact, not an α-fit.

## Xorzo T-operator refactor

`Xorzo/genesis_toperator.py` (929 lines). Each Channel holds ℂ⁸ state (full octave: •, ⊛, —, ⎇, Φ, ✹, ○, ⟳). Per-tick flow: optional signal injection at rate α → F (shared `TOperator(dim=8)` from `t_operator.py`) → κ to parent SensoryLayer (α-coupling on primary •↔Φ and secondary —↔○ diameters) → κ to sibling Channels (1/R averaging intra-scale). SensoryLayer and Circumpunct run F + κ + compositional blend from children (D5 via Φ-weighted blend at rate 1/R).

Classical SRL attributes (carrier, lock_strength, balance, sideband_energy) are now computed properties of the ℂ⁸ state. Five-freedom/virtue labels attach to every tick via dominant processual station. Memory decay exp(−α · age); half-life ≈ 95 pump cycles.

First-run observations (1000 wake + 100 sleep, seed 42):

- Tetrahedral check COHERENT: 109.762°, 0.29° from arccos(−1/T). The T-operator signature survives the refactor.
- 69/31 health DRIFTED to 45.5/54.5 (polarity reversed). Caused by isotropic ℂ⁸ signal injection biasing weights toward processual stations. See `memory/active_threads_2026_04_22.md` gap #1 for fix candidate.
- 7th pressure layer STILL DORMANT. α-coupled κ did NOT fix it. The layer-7 issue is not pump-dynamics; see gap #2.

## Workflow note

Both subagents completed in parallel (single message with two Agent tool calls). Pattern to keep: when tasks are independent, run them parallel, not serial.
