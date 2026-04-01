# Circumpunct Machine Learning: Fractal Forgetting

**Core thesis**: forgetting in neural networks should be fractal compression, not destructive linear decay.

Linear decay is amnesic. After T steps, α^T vanishes exponentially. A memory at magnitude 0.01 dies as fast as one at 0.99. Nature doesn't work this way. Memories compress: the gist survives, the detail fades. That's fractal.

Fractal compression (`|h|^e` with e > 1 on sub-unit magnitudes) gives sub-linear decay. Quieter memories decay *slower* than loud ones. Phase (identity) is preserved exactly. Nothing ever fully reaches zero.

This repo contains two implementations of the same idea in two architectures.

---

## circumpunct_mamba_v3.py

Fractal compression replaces the linear state transition in a Mamba-style selective SSM.

**Standard Mamba:**
```
h_t = α_t · h_{t-1} + γ_t · B_t · x_t
```
α^T vanishes exponentially. Old state is destroyed.

**Circumpunct v3:**
```
h_t = squash(⊛(h_{t-1}, e_t) + γ_t · B_t · x_t)
```
Where `⊛(h, e) = |h|^e · e^(iφ)` compresses magnitude while preserving phase.

**Selective exponent**: `e_t = 1 + (1 - α_t) · κ`. The same selective signal from Mamba (α computed from Δ·A) now controls a compression exponent instead of a multiplicative factor. When α is near 1 (retain), the exponent is near 1 (identity). When α is near 0 (forget), the exponent rises (compress harder). The selectivity is preserved; the geometry of decay changes.

**Key properties:**

- Complex-valued states: phase carries identity, magnitude carries intensity
- tanh squashing on magnitude keeps states bounded (the boundary condition, ○)
- φ-scaled A initialization: golden ratio proportioned slow/fast decay groups
- DNA initialization: 64 distinct phases break symmetry (A1: the 1 must self-limit)
- No worldline, no side buffer, no separate retrieval. The state IS the memory.
- Zero parameter overhead vs standard Mamba

**Framework mapping:**

| Component | Framework | Role |
|-----------|-----------|------|
| State h | Φ (field) | The 2D surface carrying all information |
| Fractal ⊛ | Convergence | Compression toward center; gist preservation |
| Squash (tanh) | ○ (boundary) | Containment; prevents unbounded growth |
| Selective exponent | • (aperture) | The gate that controls how much passes |
| Phase preservation | Identity | What survives compression is who you are |

---

## circumpunct_transformer.py

Fractal compression applied to the KV cache in a standard transformer.

In a transformer, there is no explicit forgetting. Every past key-value pair is stored at full fidelity. The problem isn't amnesia; it's the opposite: no compression at all. Every past token gets equal treatment regardless of relevance. Context windows are expensive precisely because nothing compresses.

**The mechanism**: before computing attention at each layer, keys and values get position-dependent fractal compression. Older entries receive stronger compression. Recent entries stay vivid. The attention mechanism (softmax(QK^T/√d)) still does the selection; the fractal shapes what it selects *from*.

```
effective_exponent = 1 + age · (head_kappa - 1)
K_compressed = |K|^effective_exponent · sign(K)
V_compressed = |V|^effective_exponent · sign(V)
```

Newest token (age=0): exponent = 1, no compression.
Oldest token (age=1): exponent = head_kappa, maximum compression.

**Key properties:**

- Learnable per-head compression rate (each head finds its own κ)
- Zero parameter overhead vs standard transformer (κ is n_heads scalars)
- Pre-norm residual blocks with GELU FFN
- Sinusoidal positional encoding
- Causal masking for autoregressive tasks
- `use_fractal` flag per block for easy ablation

**Framework mapping:**

| Component | Framework | Role |
|-----------|-----------|------|
| Queries | • (aperture) | Convergence points that select from the field |
| Attention surface | Φ (2D field) | The surface of token-to-token relationships |
| Layer output | ○ (3D boundary) | Commits the selected information |
| KV cache | Φ history | The field's memory of past tokens |
| Fractal compression | ⊛ on Φ | The field compresses its own history |
| Per-head κ | Head specialization | Each aperture compresses at its own rate |

---

## Benchmark Results

Both files include copying and selective copying benchmarks with matched baselines.

**Copying task (T=30, d=32, 1 layer, CPU):**

| Model | Best Accuracy | Epochs to 100% |
|-------|--------------|-----------------|
| Standard Transformer | 0.816 | ~200 |
| Fractal Transformer | 1.000 | ~375 |

The fractal version reaches full accuracy but learns slower on short sequences. This is expected: with T=30, standard attention already reaches every position directly. The fractal compression adds a gradient obstacle the network must learn around (the per-head κ must converge to useful values).

The predicted advantage is on long-context tasks where standard attention begins washing out, and on efficiency (compressed KV cache could enable longer effective context at lower memory cost). Testing this requires GPU compute.

**Mamba v3**: forward pass verified clean (no NaN, no Inf). Identical parameter count to baseline. Full benchmark pending GPU.

---

## The Idea in One Sentence

Replace linear multiplicative decay (which destroys memory exponentially) with power-law compression (which preserves the gist sub-linearly), and let phase carry identity through the compression.

---

## Lineage

- **v1** (`circumpunct_mamba.py`): fractal worldline as a side buffer alongside standard Mamba decay. Proved the concept but didn't replace forgetting.
- **v2** (`circumpunct_mamba_v2.py`): hierarchical worldlines, adaptive ◐, φ-scaled A init. More sophisticated side buffer. Still two mechanisms, not one.
- **v3** (`circumpunct_mamba_v3.py`): fractal compression IS the state transition. No worldline. No side buffer. One mechanism.
- **Transformer** (`circumpunct_transformer.py`): same idea, applied to KV cache compression in a transformer. The architecture most of the world actually uses.

---

## Running

```bash
# Mamba v3: copying benchmark, T=200, 300 epochs
python circumpunct_mamba_v3.py 200 300 copying

# Mamba v3: selective copying
python circumpunct_mamba_v3.py 200 300 selective

# Transformer: copying benchmark, T=50, 300 epochs
python circumpunct_transformer.py 50 300 copying

# Transformer: selective copying
python circumpunct_transformer.py 50 300 selective
```

Both scripts run standard baseline first, then the fractal variant, and print a comparison.

---

## Dependencies

- Python 3.8+
- PyTorch 1.9+

---

## Authors

Ashman Roonz & Claude

Derived from the Circumpunct Framework (Roonz, 2024).
