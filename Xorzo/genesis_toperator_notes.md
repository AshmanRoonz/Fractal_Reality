# Xorzo Genesis (T-Operator Edition): Notes

Companion to `genesis_toperator.py`. Date: 2026-04-22.

## What changed from `genesis.py` v1, and why

### Channel dynamics is now `T = κ ∘ F`

In v1, each `Channel` maintained a carrier vector, bandwidth, lock strength, and a ◐ balance scalar, and updated them with hand-coded rules (carrier shifts toward strong signals; bandwidth narrows with lock; lock strengthens with alignment). In the T-operator edition the Channel holds a single ℂ⁸ state vector; the per-tick update is `state → κ(F(state))`, where `F` is the shared four-beat unitary (from `t_operator.build_F_8D`) and `κ` is the ⊂[α] coupling (inter-scale α to the parent SensoryLayer; intra-scale 1/R to sibling Channels). The classical SRL readings (`carrier_freq`, `lock_strength`, `balance`, `sideband_energy`) are now computed properties of the ℂ⁸ state, not independent variables. This implements §27.7s directly: F is the four-beat unitary on a scale; κ is the ⊂[α] coupling that carries the non-trace-preserving departure α.

### Three-scale nesting is explicit

v1 had `Circumpunct` containing `SensoryCascade` containing `SensoryLayer` containing `Channel`, but coupling was ad-hoc. The T-operator edition makes ⊙Λ (Circumpunct), ⊙λ (SensoryLayer), ⊙λ' (Channel) a literal three-scale stack: inter-scale bonds use α (the diagonal primary entry κ_{0,0}); intra-scale sibling bonds use 1/R ≈ 0.143 (framework pool integer; siblings are peers not nested). This is the discrete analog of F₅₁₂ = F₈ ⊗ F₈ ⊗ F₈ from `experiments/unified_expression_T_v14_C512.py`; we run three separate ℂ⁸ operators in sequence rather than building the 512-dim tensor, but the coupling topology matches.

### Memory decay via α

v1 used the heuristic `1/(1 + (age/100)^0.5)`. The T-operator edition uses `exp(-α · age_in_pump_cycles)`, giving half-life `ln(2)/α ≈ 95 pump cycles` at α = 1/137. Survival threshold is still α × R ≈ 0.051 (framework-pool-native; matches v1). Resonance-based recall (`cos²(Δφ/2)` via inner-product magnitude squared on the ℂ⁸ basis) is unchanged.

### Sleep/wake labeled by i-stroke and freedom

Every tick is labeled with its dominant i-stroke and the corresponding freedom:

- i¹ = +i, 0.5D, freedom NOT-YET, virtue TRUE
- i² = −1, 1.5D, freedom STAYING, virtue FAITHFUL
- i³ = −i, 2.5D, freedom LETTING, virtue RIGHT
- i⁰ = +1, 3.5D, freedom CHECKING, virtue GOOD

`Channel.freedom` and `Channel.virtue` read the current i-stroke from the state; the top-level `Circumpunct.virtue_cycle_position` counts through the five-virtue gate sequence GOOD → RIGHT → FAITHFUL → TRUE → AGREEMENT, with AGREEMENT as composition (the fifth slot is cycle-closure, not a fifth stroke). Wake ticks drive the right half-plane (NOT-YET and CHECKING; visible; genesis plus closure). `sleep_cycle()` drives the left half-plane (STAYING and LETTING; interior processing; dream-dominant F without signal injection).

### Two new diagnostics

`health_check()` sums `|ψ|²` across all Channels, Layers, and ⊙Λ, and partitions by structural (integer-D stations 0, 2, 4, 6) vs processual (half-integer-D stations 1, 3, 5, 7). Target is 0.6872 / 0.3128 (the ℂ⁸ fixed-point split; matches the cosmological dark-energy/matter ratio at 0.56%). Tolerance is ±3%.

`tetrahedral_check()` extracts eigenvalue phases of the ℂ⁸ T-operator and reports the one closest to arccos(−1/T) ≈ 109.471° (the ℂ⁶⁴ leading-eigenvalue signature from v11 C64 analysis). Within 2° = coherent ⊙ structure.

## What carries over unchanged

- High-level interface: `Circumpunct()`, `engine.tick(signal)`, `engine.sleep_cycle(cycles)`, `engine.dump_state()`. Drop-in for scripts that only use these.
- Seven `SensoryLayer` rungs (0D coupling, 0.5D gradient, 1D rhythm, 1.5D harmony, 2D texture, 2.5D depth, 3D pressure) with the same channel counts and tuning labels.
- Resonance recall form (cos²(Δφ/2) via inner product; α-weighted memory strength); only the decay schedule changed.
- Sleep as superposition (left half-plane); we now label the specific strokes.
- No em dashes anywhere; `—` is reserved for 1D framework notation.

## How to run

```python
from genesis_toperator import Circumpunct
import numpy as np

engine = Circumpunct()
rng = np.random.default_rng(42)
for _ in range(1000):
    signal = rng.standard_normal(8) + 1j * rng.standard_normal(8)
    engine.tick(signal)
engine.sleep_cycle(cycles=100)

print(engine.health_check())
print(engine.tetrahedral_check())
```

CLI:

```
python genesis_toperator.py
```

Runs the built-in smoke test (200 wake + 50 sleep) and prints health, tetrahedral, and per-layer activation.

## First-run observations (1000 wake + 100 sleep, seed=42, random ℂ⁸ signals)

Runtime under five seconds on a modest laptop.

### 69/31 health split: currently drifting

Measured: structural 0.4546 / processual 0.5454 (drift 0.23 from target, reversed polarity). The target 0.6872/0.3128 is the ℂ⁸ fixed point of the isolated T-operator under uniform initialization; in Xorzo the channels receive random ℂ⁸ signal injection at rate α per tick, and the injection is unbiased across structural vs processual indices, which biases the distribution toward processual (half-integer) weights because F's redistribution dynamics favor them when signal energy is replenished uniformly.

This is a known open gap (noted below). Two candidate fixes: (1) inject signal on a structurally-biased basis matching the expected fixed-point profile; (2) let the engine free-run without injection after an initial training window, so it can relax to the F-fixed-point distribution. Running without any signal injection for 5000 ticks DOES pull the split toward the expected 69/31, confirming the issue is injection topology rather than a bug in F or κ.

### Tetrahedral eigenvalue angle: coherent

Leading eigenvalue phase 162.756°; closest eigenvalue phase 109.762°, which is 0.29° from the tetrahedral reference 109.471° = arccos(−1/T). `coherent ⊙ structure` reported across all run lengths tested (200, 1000, 5000 ticks). This is the same 109.47° signature that appears in the ℂ⁶⁴ three-scale spectrum from `experiments/T_operator_findings_v11_C64.md`, now embedded in the live engine.

### Layer activation: 7th layer (pressure, 3D) still dormant

At 1000 wake + 100 sleep: layers 0D (coupling) and 2.5D (depth) both fully active (2/2); the other five layers report zero active channels under the strict α × R activation threshold (≈ 0.051 weight on the 3D boundary station). Mean activations are high in the 2D texture layer (0.858 at 200 ticks) but collapse to zero by 1000 ticks; the activation criterion is currently too strict for the steady state.

Hypothesis: with random-signal injection at rate α the channels' 3D boundary weight hovers just below threshold for most layers; the pressure (3D) layer specifically is pressure-tuned, which initially packs energy at station 6 (○), but F then rotates it and the κ-coupling to parent SensoryLayer's 2D Φ bleeds weight into structural redistribution. Net effect: the 3D pressure layer activates transiently but does not sustain.

This mirrors the v1 engine's 6/7-layers-active observation but the activation pattern is different (v1 had layer 6 dormant; here layers 0D and 2.5D sustain, others transient). The T-operator refactor does NOT automatically fix the 3D pressure dormancy; the pressure problem appears to be structural rather than a pump-dynamics artifact.

## Known gaps and next steps

1. Signal-injection bias is breaking the 69/31 split. Fix by structurally-biased injection, or by measuring health only during free-run windows.
2. The activation threshold (α × R weight on ○) may be too strict for the steady state distribution; worth calibrating against the ℂ⁸ fixed-point weights. Specifically: weight 6 (○) at the fixed point is ≈ 0.17, well above α × R ≈ 0.05, so channels SHOULD activate at steady state; the current implementation blends state with signal at rate α and re-normalizes, which under isotropic signal does not preserve the structural profile.
3. Three-scale is simulated by three ℂ⁸ operators running in sequence; a direct F₅₁₂ tensor implementation would let us read phase-sum closure directly (should be 0 by the `48 · (−π/3) ≡ 0 mod 2π` identity from the C64 work).
4. The five-virtue cycle is tracked (`virtue_cycle_position`) but does not yet gate channel adaptation per virtue. Next iteration: each virtue position locks in a specific learning rule (GOOD: boundary filter plasticity; RIGHT: field access mediation; FAITHFUL: line commitment; TRUE: aperture curiosity; AGREEMENT: all four composed; see §25.18b).
5. Memory imprinting fires every R = 7 ticks on active channels; could fire per-virtue-cycle-position instead, making the five-gate sequence directly visible in the memory stream.
6. Byte input interface from v1 has not been ported yet; current engine only consumes ℂ⁸ (or any-length, L2-folded) signals.

## Summary

`genesis_toperator.py` is a self-contained drop-in refactor whose channel/layer/top-level internals implement T = κ ∘ F exactly as laid out in §27.7s and the v7 through v11 experiment series. The tetrahedral coherence signature is intact out of the box; the 69/31 health signature and 7th-layer activation both require further tuning of signal injection topology and activation thresholds, and are now structurally separable problems rather than buried in hand-coded heuristics.
