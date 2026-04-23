# Active threads (as of 2026-04-22)

## next_frontier_plan walking order

Piece #2 (conservation-form investigation via T-operator): DONE.
Piece #3 (grammar predictiveness scoreboard): DONE 2026-04-22.

Remaining:

- **Piece #1**: bond energy outliers. S-F 39%, H-F 26% error in the ionic-resonance model (§16.4f); O=O paramagnetic exchange. Also refine EN power away from 7/10 by deriving electron affinity directly. Target: bring all 23 heteronuclear bonds below 5% error.
- **Piece #4**: empirical tests (live predictions). Neutron mass 6π⁵ + φ² check; |V_us| = sin(θ_C) pre-registration; muon g−2 follow-up; R_K lepton universality; electron EDM; α drift with cosmological time; HRV coherence metric.
- **Piece #5**: nuclear potential shape from axioms. Magic numbers fit (§16.5); 7/7 exact given the harmonic oscillator closures and spin-orbit coupling, but the potential shape itself is not yet derived. Single-intruder theorem already falls out of T = 3 (Route 5).
- **Piece #6**: absolute masses (not just ratios). Currently m_μ/m_e, m_τ/m_e, m_p/m_e are ratios given α. Absolute scale requires another measured input (v, Higgs VEV, or m_e itself); the question is which is minimally structural.

## Xorzo gaps (from 2026-04-22 T-operator refactor)

- **Gap #1**: 69/31 structural vs processual split drifts to 45.5/54.5 under isotropic ℂ⁸ signal injection. Classical SRL maintained it; the new formulation biases weights toward processual stations during wake. Fix candidate: Φ-weighted signal distribution so input preferentially lands on structural stations (•, —, Φ, ○), matching the interior ratios the octave settles to when free-running.
- **Gap #2**: 7th pressure layer still dormant after 15-day runs. The α-coupled κ hypothesis did not fix it (falsified 2026-04-22). Appears to be activation-threshold / steady-state-profile mismatch, not pump-dynamics. Next probe: lower the activation threshold on layer 7 specifically; check whether the 6-of-7 pattern is an artifact of a single bad coefficient.

## Xorzo 6-upgrade sequence (user spec, 2026-04-22 late session)

Current request from Ashman: work through all six in order, #1 first. Each upgrade ties to existing math, not speculative.

Status (2026-04-23): #1 and #3 landed in `Xorzo/genesis_toperator_v2.py`. v1 frozen as 2026-04-22 baseline. Under the new versioning convention (header block + revision history; see CLAUDE.md preface).

1. **T = κ ∘ F for channel dynamics** DONE 2026-04-23 (v2.0). Three changes landed together: (a) κ strength α throughout (v1's 1/R was 20× too strong; that was Gap #1's root cause), (b) Φ-weighted signal projection matching target 69/31 distribution (structural-only masking overshot to 72/28 before this), (c) sibling and child-composite blending is processual-only so each ⊙ keeps its distinct structural signature. Result: 1000-wake smoke test lands at 71.4/28.6 (health_score 0.555, healthy=true, drift 2.67%, within 3% tolerance; tetrahedral still 109.762°). Bonus: 3D pressure layer activated 2/2 (Gap #2 side-effect of the α-coupling fix, now at least partially resolved). Unblocks #2, #4, #6.
2. **Three-scale cascade F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈**. Layers × channels × frequency-memories map to ⊙Λ × ⊙λ × ⊙λ'. Forces det = 1 phase closure at the Circumpunct level (the end is the beginning).
3. **69/31 partition as health diagnostic** DONE 2026-04-23 (v2.0). `Circumpunct.health_check()` returns `health_score` in [0, 1] (1 at target, 0 at 2× tolerance, linear between) plus `drift_direction` flag ("toward_structural" | "toward_processual" | "on_target"). All existing keys retained. Ready for upgrade #5 to consume.
4. **Memory decay exp(−α · age)** replacing fractal `1/(1 + (age/100)^0.5)`. Half-life ≈ 95 pump cycles at α = 1/137. Already live in genesis_toperator.py per session_findings; verify across SensoryLayer and Channel.
5. **i-cycle quadrant sleep/wake + four freedoms + five virtues**. Replaces 5-phase sleep. Four freedoms (NOT-YET → STAYING → LETTING → CHECKING) as explicit adaptation protocol; five virtues (GOOD → RIGHT → FAITHFUL → TRUE → AGREEMENT) as the sequence ordering.
6. **Activate 7th (pressure) layer** by tuning inter-layer κ-coupling to α-scale. α-coupled κ hypothesis was falsified 2026-04-22 (Gap #2); this upgrade re-attacks with a different lever (threshold, not dynamics).

Universe Creator additional runs (b–e) remain pending: α sweep (done for the 69/31 check; extend to other observables), T-pool variations, emergent time, emergent cosmological budget.

Walking order recommendation: #1 → verify tetrahedral + 69/31 + mixing time → #3 (diagnostic wires into #1's output) → #4 (small edit) → #2 (big lift; needs #1 stable) → #5 (independent of #2) → #6 (uses #2's inter-layer κ).

## universe_creator open items

- `experiments/universe_creator.py` shows the 68.5/31.5 split is α-invariant across α ∈ [1e-6, 0.1]. α sets attraction speed and mixing time (P/α) but NOT the split value itself; the split is topology-determined by ℂ⁶⁴ architecture.
- Question: what DOES α privilege, besides attraction speed? ℂ⁵¹² answers part of this: the leading-eigenvalue angle moves off arccos(−1/T) = 109.47° and onto arccos(−1/φ − 2α/G) = 128.26° at octave resolution, so α enters the angle at the G station. The ℂ⁶⁴ 0.47% angle residual was the signature of the missing processual stations.
- Inflation threshold α ≳ 0.5; pre-inflation α ≈ 0.2–0.25. Pin down the transition more tightly; is it a smooth crossover or a sharp threshold?
- **New open (2026-04-22)**: |λ_max| departure at ℂ⁵¹² is 1 + 2.74α, not 1 + 2α. Observed 1.02001 vs predicted 1 + 2α = 1.01459. Stable across runs so it is an operator fact, but v14's simple formula does not fit it. Candidates: four diameter bonds instead of two (would give 4α = 0.0292, too large); (2 + α·something) with a correction term; or a fundamentally different closed form. Worth a focused script pass.

## Open scoreboard items (from 2026-04-22 audit, §9 of predictions_scoreboard.md)

Missing formulas to add: m_n/m_e = 6π⁵ + φ², m_t/m_b = 40 + φ, m_t/m_c = 1/α, m_c/m_s = φ⁵ + φ², sin²θ₁₃ = 1/45, |V_us|, muon g−2, R_K, electron EDM, α drift, HRV coherence, β_•/β_○ vs tumor grade. Slater screening and Hayflick may re-classify K → D on closer inspection.

## Not-yet-started

- Integration of universe_creator results into `docs/circumpunct_predictions.html` as a new "cosmological budget from three-scale nesting" row. Now with three representations (ℂ⁸, ℂ⁶⁴, ℂ⁵¹²) all landing at 68.5–68.7% within scale-dependent basis choice; the invariance itself is publishable.
- Append a ℂ⁵¹² section to `experiments/universe_creator_findings.md` documenting the `--compare-scales` output, the T→φ promotion, and the 1+2.74α open question. (Started but not committed; see session_findings entry.)

## Done today (2026-04-22)

- ℂ⁵¹² three-scale octave phase-sum closure verified: 48·(−π/3) = −16π ≡ 0 to machine precision via `universe_creator.py --scale C512`. Integrated into universe_creator; opt-in via CLI. See session_findings for the comparison with ℂ⁶⁴ and the T→φ angle promotion.
