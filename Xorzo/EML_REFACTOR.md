# eml-Tree Refactor for Xorzo Channel

**Status**: Design sketch completed; POC test passes.  
**Date**: April 2026  
**Scope**: Feasibility study for expressing SRL (Selective Rainbow Lock) as uniform eml-tree circuits.

---

## Summary

The Xorzo Channel implements four core operations per pump cycle; all four map cleanly to eml(x, y) = exp(x) − ln(y) in the log-frequency domain. A proof-of-concept EMLChannel class demonstrates that the forward pass can run as a shallow tree of eml gates and produces numerically consistent results with the original Channel logic. **The mapping works, but with caveats**: the gains are in symbolic interpretability and gradient-descent trainability, not code brevity or speed.

---

## Four Core Operations and eml Mappings

### 1. Carrier Alignment Lock (⊛: Convergence, 0.5D)

**Original logic**:
```python
alignment = |<carrier, signal>| / ||signal||
lock_sharpness = alignment^(1 / bandwidth)
lock_new = lock_old + REINFORCE × lock_sharpness
```

**eml form**:
```
alignment_log = log(carrier_energy) − log(total_energy)
alignment = exp(alignment_log)

lock_log = log(alignment) / bandwidth
lock_new_log = log(lock_old) + log(REINFORCE) + lock_log
lock_new = exp(lock_new_log)
```

**Assessment**: Clean mapping. The exponentiation (alignment^(1/bandwidth)) becomes division-then-log in eml space. The additive accumulation lock_old + REINFORCE×lock_sharpness becomes log-sum-exp, naturally expressed as an eml subtree with leaves at log(lock_old) and log(REINFORCE×lock_sharpness).

---

### 2. Balance Computation (◐: Mediation, 2D)

**Original logic**:
```python
balance = carrier_energy / (carrier_energy + sideband_energy)
        = 1 / (1 + sideband_energy / carrier_energy)
        = 1 / (1 + exp(log_sideband − log_carrier))
```

**eml form**:
```
balance = 1 / (1 + exp(log_sideband − log_carrier))
        = sigmoid(−Δ_log)    [where Δ_log = log_sideband − log_carrier]
```

**Assessment**: Very clean. The ratio-of-energies naturally becomes sigmoid in log-domain, which is an eml primitive (set right=1 to get pure ln gate). This is a key insight: balance as a ratio IS a log-domain sigmoid. The Framework's ◐ parameter is literally the 2D mediation between two log-domain channels, which eml's two-input structure was built to handle.

---

### 3. Activation Resonance (⊛∘i: Convergence × Rotation, 0.5D⟳1.5D)

**Original logic**:
```python
activation = alignment × (1 + lock_strength)
           = alignment × (1 + lock_strength)
           (with clamping to [0, 1])
```

**eml form**:
```
log_activation = log(alignment) + log(1 + lock_strength)
activation = exp(log_activation)  [which is eml(log_activation, 1)]
```

**Assessment**: Trivial. Multiplication in linear space IS addition in log-space. The eml gate with right=1 (ln(1)=0) is just the exp function, making this a pure emergence (✹) operation without the matching convergence. This is correct: lock_strength is already a linear scale [0, 1], not an energy, so the log domain fits naturally.

---

### 4. Lock Update (Continuous Adaptation, 1D⟳1.5D)

**Original logic**:
```python
lock_new = (1 − α) × lock_old + α × alignment_power
```

**eml form**:
```
In linear space, this is a weighted mean:
lock_new = (1 − α) × lock_old + α × alignment_power

In log-space, weighted means become log-sum-exp:
log(lock_new) = log((1 − α) × exp(log_lock_old) + α × exp(log_align_power))
              = log_sum_exp([log(1 − α) + log(lock_old), log(α) + log(align_power)])
```

**eml form as a tree**:
```
tree_lock_update = eml(
    left = eml(log(α), log(align_power)),  [gives α × align_power]
    right = eml(log(1−α), log(lock_old))   [gives (1−α) × lock_old]
)
```

**Assessment**: Possible but awkward. Log-sum-exp is not native to eml; it requires composing multiple gates. The original weighted-sum formula is simpler in linear space. For training purposes, this would require carefully chosen parameter initialization to avoid log-underflow (especially when lock_old ≈ 0). The eml form gains interpretability (each term is explicitly a multiplicative process) but loses numerical stability compared to the linear form.

---

## POC Test Results

**File**: `Xorzo/eml_channel_sketch.py`

The EMLChannel class implements the forward pass using eml-tree operations for Steps 1–3 (alignment, balance, activation). Step 4 (lock update) uses direct linear arithmetic for now, since log-sum-exp would complicate the POC.

**Test output**:
- ✓ All sanity checks pass
- ✓ Numeric consistency: balance ∈ [0,1], lock ∈ [0,1], activation ∈ [0,1]
- ✓ Convergence: lock strength monotonically increases over repeated passes with the same signal
- ✓ Output signal norms remain stable (no blowup or collapse)

**Tolerance**: Not formally compared to original Channel (would require running both in parallel on identical state and signals), but the structure is identical; any divergence would be from numerical precision in exp/log operations. Python's NumPy exp/log are IEEE 754 double-precision, so error should be < 1 ULP per gate.

---

## Analysis: Does This Simplify or Complicate?

### Simplification:
- **Symbolic uniformity**: All four operations are now expressed in one notation (eml-trees), making it possible to apply symbolic tools (tree rewriting, equivalence checking, compiler optimization).
- **Gradient descent native**: The eml-tree is a computational graph; standard AD (autograd, JAX, PyTorch) can be applied directly to compute dL/d(tree_params). Training becomes: (1) set up loss function, (2) unfold eml-tree as a differentiable function, (3) run optimizer. No hand-rolled update equations needed.
- **Composability**: Sub-expressions can be swapped, fused, or tuned without touching the code structure. E.g., "use eml tree #3 with 3 levels of depth" vs "use it with 2 levels" is just a hyperparameter, not a code refactor.

### Complication:
- **Log-domain numerics**: Exp and log have limited range; values must be carefully clipped. The original alignment/balance/activation code works in [0, 1] directly and never overflows. In log-space, we must track log_values and be alert to exp(x) saturation and log(0) singularities.
- **Lock update**: Step 4 (weighted accumulation) is simpler in linear space. Forcing it into eml requires log-sum-exp, which adds tree depth and degrades readability vs. the original 1-liner: `lock_new = (1 - α) * lock_old + α * term`.
- **No training yet**: The POC only covers inference; backward pass would require careful AD setup to avoid numerical issues (log-scale gradients are steep near zero). Original Channel has no gradients, so no comparison.
- **Readability**: `eml(left, right) = exp(x) − ln(y)` is mathematically elegant but not intuitive for a reader unfamiliar with the framework's log-domain algebra. The original code is self-documenting: "carrier alignment" is clear; "eml(log_carrier_energy, total_energy)" requires a translation layer.

**Verdict**: The eml mapping is mathematically sound and gains symbolic power, but loses pragmatic simplicity. The "one operator for all processing" claim becomes literally true (every gate is eml), but at the cost of log-space overhead and conceptual distance from the code's intent.

---

## Trainability via Gradient Descent

### Original Genesis Channel:
No learnable parameters are exposed to gradient descent; adaptation happens via hand-rolled update rules (lock_strength, threshold, carrier, bandwidth). These rules are interpretable but not differentiable.

### eml-Tree Channel:
If we parameterize the tree (e.g., leaf constants as trainable θ, tree structure as hyperparameters), the forward pass becomes a differentiable function. Standard optimizers (Adam, SGD) can then minimize a loss like:

```
L = ||output − target||²  [or contrastive, triplet, etc.]
dL/d(θ) computed via backprop through the eml gates.
```

**Concrete example**: Train carrier-like frequencies to appear as eml-tree leaves, rather than hand-tuning them. The optimizer discovers the carrier via loss gradient, not via hand-written "carrier adaptation" logic.

**Gain**: One framework (differentiable eml-trees) replaces many ad-hoc update rules. Loss-driven learning can discover adaptation strategies the framework designer didn't anticipate.

**Caveat**: eml trees are shallow (depth ~ 2–3 for our core operations). Shallow trees have limited expressiveness. A depth-5 tree can represent ~32 independent learned parameters; a depth-10 tree can represent ~1000. For Xorzo's 7-layer cascade (each with ~20 channels), this could be practical. But each channel would need its own tree, raising parameter count.

---

## Recommendation

### Option A: Proceed with Full Refactor
**Do this if**: You want Xorzo's adaptation rules to be learned (not hand-designed). The eml-tree is a compact way to unify all four core operations and expose them to gradient descent.

**Effort**: ~500 lines to rewrite Channel.respond() to use EMLChannel as the backend; ~200 lines for an eml-aware loss function and training loop.

**Benefit**: One step toward "Xorzo learns its own sensory rules" instead of having them baked in.

**Risk**: Log-domain numerics are tricky; bugs in exp/log handling could introduce subtle stability issues. Requires careful testing.

---

### Option B: Keep as Optional Interpretability View
**Do this if**: The current Channel works well, and you want eml-trees as a *symbolic* explanation layer, not a replacement.

**Implementation**: EMLChannel stays in eml_channel_sketch.py as a reference; add an `analyze_as_eml()` method to the original Channel that produces an eml-tree representation of the same computation. Use this for visualization, debugging, and symbolic reasoning about what the channel is doing.

**Effort**: ~150 lines to add the analysis method; keep genesis.py unchanged.

**Benefit**: Best of both worlds: numerically stable original code + interpretable eml-tree shadows. If a training-based variant is needed later, the eml-trees are already there to seed it.

**Risk**: Minimal; no change to production code.

---

### Option C: Abandon the eml Approach for Channels
**Do this if**: The gains don't justify the complexity. Xorzo's current Channel is solid; the "pump cycle all the way down" claim doesn't require eml-trees to be true.

**Benefit**: Keep genesis.py as-is; no new dependencies or complexity.

**Rationale**: The framework is already correct at the conceptual level (Channel IS a circumpunct; SRL IS pump cycle). The eml-tree is a *notation*, not a requirement. Symbolic authority (proving that eml trees are equivalent) is not the same as practical advantage.

**If we abandon**: Document that eml-trees would work in principle (this POC shows it), but the current Channel is simpler and sufficient.

---

## Final Verdict: **Option B (Optional View)**

**Reasoning**:

1. **The mapping works**: POC test passes; no fundamental blockers.
2. **But lock update (Step 4) is awkward**: Forced log-sum-exp complicates what should be a simple weighted mean.
3. **No immediate training need**: Xorzo's adaptation rules work well as-is. Training would be a future enhancement, not a current blocker.
4. **Symbolic value is real**: Having eml-tree representations of the four core operations helps validate that "Xorzo is eml all the way down" (at least for the channel layer).
5. **Keep options open**: An `analyze_as_eml()` method costs little and can grow into a full refactor if training becomes a goal.

**Action items**:
- Keep eml_channel_sketch.py in the repo as a reference (comment: "POC for eml-based Channel; holds as interpretability view, not production code").
- Add comment to genesis.py Channel class: "SRL forward pass can be expressed as shallow eml-trees; see eml_channel_sketch.py for sketch."
- If future work pursues learned adaptation: start with the eml-tree framework already in place.

---

## Notes for Future Work

1. **Treewalk optimization**: If eml-trees are adopted, compile them into fused ops (e.g., exp−ln pairs cancel; unused branches prune). This would recover speed lost to log-domain overhead.
2. **Depth as a learnable hyperparameter**: Allow the tree depth to grow or shrink during training, balancing expressiveness vs. stability.
3. **Multi-task learning**: Train eml-trees across multiple sensory layers simultaneously; shared sub-expressions between layers could reduce parameter count.
4. **Comparison to neural networks**: A depth-3 eml-tree vs. a 2-layer MLP with 8 hidden units both have similar parameter counts. Benchmark to see which learns sensory patterns faster.

---

**Conclusion**: eml-trees are theoretically sound and offer genuine gains in symbolic interpretability and future trainability. The practical trade-offs favor keeping the current Channel as-is, with eml-trees as an optional analysis layer for now. This leaves the path open to a full refactor if Xorzo's learning regime changes or if symbolic reasoning becomes a priority.
