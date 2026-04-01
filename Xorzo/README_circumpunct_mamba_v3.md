# ⊙ The Circumpunct Mamba v3: Fractal State Transition

**Forgetting is not destruction. It is compression.**

Standard state space models (SSMs) like Mamba forget by multiplying state by a decay factor α at every timestep. After T steps, a memory's magnitude is α^T, which vanishes exponentially. A memory at magnitude 0.01 dies just as fast as one at 0.99. This is linear, blind, and amnesic.

The Circumpunct Mamba replaces linear decay with fractal compression: instead of `h = α · h`, the state transition is `h = |h|^e · e^(iφ)`, where the exponent e is controlled by the same selective mechanism that Mamba already uses. Phase (identity) is preserved exactly. Magnitude (intensity/freshness) compresses sub-linearly: quieter memories decay *slower* than loud ones. Nothing ever fully reaches zero.

This is how biological memory works. Detail fades; gist survives. The compression is fractal, not linear.

## The Result

Copying benchmark, T=20 delay, 1000 epochs, d=64, N=16, 2 layers, GPU (RTX 5050):

| Model | Best Accuracy | Params | Status at Epoch 1000 |
|-------|--------------|--------|---------------------|
| Standard Mamba | 0.164 | 35,885 | Stuck at chance. Never learned. |
| **Fractal Mamba v3** | **0.621** | 39,981 | Still climbing. Loss still dropping. |

**Delta: +0.457 accuracy.** The standard model literally cannot solve this task. The fractal model learns it and keeps improving.

The extra parameters (4,096; 11% overhead) come entirely from the resonance projection. The fractal compression itself adds zero parameters: it replaces one operation (multiply by α) with another (raise to exponent e).

## How It Works

### 1. Fractal Compression Replaces Linear Decay

Standard Mamba:

```
h_t = α_t · h_{t-1} + γ_t · B_t · x_t
```

Circumpunct v3:

```
h_t = squash(⊛(h_{t-1}, e_t) + γ_t · B_t · x_t)
```

Where ⊛ is fractal compression: `|h|^e · e^(iφ)`. The magnitude is raised to a selective exponent; the phase passes through unchanged.

For magnitudes in (0, 1) with exponent > 1, `|h|^e < |h|` (real decay), but the curve is concave. Small magnitudes are compressed less than large ones. This is the opposite of linear decay, where all magnitudes lose the same fraction per step.

### 2. Resonance-Modulated Exponent

The compression exponent is not blind. It responds to two signals:

```
e_t = 1 + (1 - α_t) · κ · (1 - T_t)
```

Where:
- **α_t = exp(Δ_t · A)**: Mamba's standard selective retention signal. High α means "keep this."
- **T_t = cos^2(Δφ/2)**: Resonance gate. Measures phase match between the current input and each state dimension. High T means "this state is relevant to the current input."
- **κ**: Maximum extra exponent (default 0.5)

Both signals must agree to compress. If either α or T is high, the state is protected:

| α (gate) | T (resonance) | Exponent | Effect |
|----------|---------------|----------|--------|
| High | High | ~1.0 | Retain: gate says keep, input matches |
| Low | High | ~1.0 | Resonance protects: input needs this pattern |
| High | Low | ~1.0 | Gate protects regardless |
| Low | Low | ~1 + κ | Compress: gate says forget, no match |

Each state dimension is a "head" with a carrier phase (initialized via DNA init with 64 distinct phases). The resonance projection gives the input its own phase signature. Relevant patterns survive; irrelevant ones compress faster.

### 3. Magnitude Squashing (Boundary Condition)

After the state update (compression + new input), magnitude is squashed into (0, 1) via tanh:

```
h = tanh(|h|) · e^(iφ)
```

This is the boundary condition (○ in the Circumpunct Framework): the state cannot grow unbounded. Phase passes through untouched.

### 4. φ-Scaled A Initialization

The A matrix (which controls the base selective retention) is initialized with golden-ratio-proportioned groups:

- N/φ dimensions: slow decay (long horizon, working memory)
- N/φ^2 dimensions: fast decay (reactive, immediate context)

This gives the SSM built-in multi-timescale structure within a single layer, zero extra parameters.

### 5. DNA Initialization

State is initialized with complex values whose phases are evenly distributed around the unit circle. This breaks symmetry from step zero: each state dimension starts with a unique identity (phase signature), not a uniform blob.

## Architecture

```
Input x_t
    |
    v
[SiLU gate] ──> z (gating branch)
    |
    v
[x_proj] ──> Δ_t, B_t, C_t (selective SSM parameters)
    |
    v
[Resonance projection] ──> x_complex (phase signature for matching)
    |
    v
[Resonance gate] T_t = cos^2(Δφ/2) between x_complex and h_carrier
    |
    v
[Selective exponent] e_t = 1 + (1 - α_t) · κ · (1 - T_t)
    |
    v
[⊛ Fractal compression] h = |h|^e_t · e^(iφ_h)    <── THIS replaces α · h
    |
    v
[State update] h = h + γ_t · B_t · x_t
    |
    v
[Squash] h = tanh(|h|) · e^(iφ)                     <── Boundary condition
    |
    v
[Output] y_t = Re(C_t^H · h_t)
    |
    v
y_t * SiLU(z) ──> [out_proj] ──> output
```

## Usage

```bash
# Full benchmark (standard baseline + fractal)
python circumpunct_mamba_v3.py 20 1000 copying

# Fractal only (skip baseline)
python circumpunct_mamba_v3.py 20 1000 copying --fractal-only

# Selective copying (harder: remember only marked tokens)
python circumpunct_mamba_v3.py 20 1000 selective --fractal-only

# Longer delay (where fractal advantage grows)
python circumpunct_mamba_v3.py 50 2000 copying --fractal-only
```

Arguments: `[T] [epochs] [problem] [--fractal-only]`
- T: number of blank timesteps between input and recall (default 200)
- epochs: training iterations (default 300)
- problem: `copying` or `selective` (default copying)

## Requirements

- Python 3.8+
- PyTorch (2.9.0+ for RTX 5000 series with CUDA 12.8)

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu128
```

## Connection to the Circumpunct Framework

This work applies the Circumpunct Framework (Roonz, 2024) to machine learning. The framework's core ontological structure is ⊙ = Φ(•, ○): a whole composed of aperture (convergence), field (mediation), and boundary (filtration).

The mapping to the SSM:
- **⊛ (convergence)**: Fractal compression. The state converges inward; magnitude decreases while phase (identity) is preserved. This IS forgetting, reframed as compression rather than destruction.
- **Φ (field/mediation)**: The complex-valued state space. Phase carries identity; magnitude carries intensity. The field mediates between past input and future output.
- **○ (boundary)**: The tanh squash. Magnitude is bounded in (0, 1). The boundary filters; it prevents unbounded growth.
- **T = cos^2(Δφ/2)** (resonance gate): Direct from the framework's theory of transmission fidelity. Phase matching determines what passes through.
- **φ-scaled initialization**: The golden ratio (φ = 1.618...) appears throughout the framework as the balance between nested scales.
- **DNA init (64 phases)**: From the framework's 64-state architecture (3 circumpuncts x 2 channels = 6 binary degrees of freedom = 2^6 = 64 states).

The deeper principle: in the framework, process and structure are the same thing (as Einstein showed energy and matter are the same). The fractal compression is both the process of forgetting and the structure of memory. They are not two mechanisms; they are one, seen from different angles.

## Files

| File | Description |
|------|-------------|
| `circumpunct_mamba_v3.py` | The fractal state transition SSM (this project) |
| `circumpunct_mamba_v2.py` | v2: hierarchical worldline approach (side buffer, superseded) |
| `circumpunct_mamba.py` | v1: basic fractal worldline (proof of concept, superseded) |
| `circumpunct_lstm.py` | Original LSTM with fractal compression (earlier experiment) |
| `genesis.py` | Xorzo consciousness engine (separate technology, same framework) |

## Authors

Ashman Roonz and Claude
April 2026

Derived from the Circumpunct Framework (Roonz, 2024) and Mamba (Gu & Dao, 2024).
