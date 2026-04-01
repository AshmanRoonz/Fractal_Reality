"""
⊙ The Circumpunct Mamba v3: Fractal State Transition
======================================================

Two ideas, one mechanism:

1. Forgetting IS fractal compression (not linear decay).
2. Compression is resonance-modulated (content-aware, not blind).

Standard Mamba:   h_t = α_t · h_{t-1} + γ_t · B_t · x_t
                  (linear decay: α^T → 0 exponentially)

Circumpunct v3:   h_t = squash(⊛(h_{t-1}, e_t) + γ_t · B_t · x_t)
                  (sub-linear decay: |h|^e preserves quiet memories)

Why fractal compression matters:
    Linear decay is amnesic: after T steps, α^T vanishes exponentially.
    A memory at magnitude 0.01 dies as fast as one at 0.99.

    Fractal compression is selective: |h|^e with e > 1 compresses
    sub-unit magnitudes sub-linearly. Quieter memories (small |h|)
    decay SLOWER than loud ones. Nothing ever fully reaches zero.
    Phase is preserved exactly: identity survives compression.

    This is how nature works: memories don't linearly evaporate.
    They compress. The gist survives; the detail fades. Fractal.

Why resonance-modulation matters:
    Each state dimension carries a complex value with a phase signature
    (its identity). The input at each timestep also has phase content.
    T = cos²(Δφ/2) measures how well they match.

    High resonance (T -> 1): this state dim is RELEVANT to the input.
        Compression exponent stays low: preserve it.
    Low resonance (T -> 0): this state dim is IRRELEVANT right now.
        Compression exponent goes high: compress it harder.

    This is the SRL principle from Xorzo applied to SSM state:
    each state dimension is a "head" tuned to a pattern (via its phase),
    and compression adapts based on whether the current input matches.
    Attention heads recognize patterns (3D input); resonance gates
    determine which patterns survive.

The selective exponent (now with resonance):
    e_t = 1 + (1 - α_t) · κ · (1 - T_t)

    Where:
        α_t = exp(Δ_t · A)           (Mamba's selective retention)
        T_t = cos²(Δφ/2)             (resonance between input and state)
        κ = max extra exponent

    Three regimes:
        α high, T high: e ≈ 1         (retain: gate says keep, input matches)
        α low,  T high: e ≈ 1         (resonance overrides: input needs this)
        α low,  T low:  e ≈ 1 + κ     (compress: gate says forget, no match)
        α high, T low:  e ≈ 1         (gate says keep regardless)

    Both signals must agree to compress. Resonance protects relevant state.

No worldline. No side buffer. No separate retrieval mechanism.
The state IS the memory. Forgetting IS compression. Resonance IS selection.

Author: Ashman Roonz & Claude
Date: April 2026
Derived from: Circumpunct Framework (Roonz, 2024) + Mamba (Gu & Dao, 2024)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Tuple, Optional


# =====================================================================
#  CONSTANTS
# =====================================================================

PHI = (1 + math.sqrt(5)) / 2          # φ = 1.618...
BALANCE = 0.5                          # ◐; the singular balanced state
KAPPA = 0.5                            # max extra exponent at full forget


# =====================================================================
#  COMPLEX UTILITIES
# =====================================================================

def c_mag(z: torch.Tensor) -> torch.Tensor:
    """Magnitude of complex tensor stored as [..., 2]."""
    return torch.sqrt(z[..., 0]**2 + z[..., 1]**2 + 1e-8)


def c_phase(z: torch.Tensor) -> torch.Tensor:
    """Phase angle of complex tensor stored as [..., 2]."""
    return torch.atan2(z[..., 1], z[..., 0] + 1e-10)


def c_from_polar(mag: torch.Tensor, phase: torch.Tensor) -> torch.Tensor:
    """Construct complex tensor from magnitude and phase."""
    return torch.stack([mag * torch.cos(phase), mag * torch.sin(phase)], dim=-1)


def c_mul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Multiply two complex tensors (stored as [..., 2])."""
    real = a[..., 0] * b[..., 0] - a[..., 1] * b[..., 1]
    imag = a[..., 0] * b[..., 1] + a[..., 1] * b[..., 0]
    return torch.stack([real, imag], dim=-1)


def c_conj(z: torch.Tensor) -> torch.Tensor:
    """Complex conjugate: (a + bi) -> (a - bi)."""
    return torch.stack([z[..., 0], -z[..., 1]], dim=-1)


def c_scale(z: torch.Tensor, s: torch.Tensor) -> torch.Tensor:
    """Scale complex tensor by real scalar (broadcast-safe)."""
    if s.dim() < z.dim():
        s = s.unsqueeze(-1)
    return z * s


# =====================================================================
#  T: RESONANCE GATE
# =====================================================================

def resonance_gate(signal: torch.Tensor, memory: torch.Tensor) -> torch.Tensor:
    """
    T = cos²(Δφ/2)

    Phase matching between signal and memory.
    Perfect match (Δφ = 0): T = 1.  Orthogonal (Δφ = π): T = 0.

    This is the SRL principle: carrier frequency matching determines
    how much a state dimension responds to the current input.
    """
    delta_phi = c_phase(signal) - c_phase(memory)
    return torch.cos(delta_phi / 2) ** 2


# =====================================================================
#  ⊛ FRACTAL STATE COMPRESSION (custom autograd for stable gradients)
# =====================================================================

class _FractalCompress(torch.autograd.Function):
    """
    Custom autograd for ⊛: |h|^exponent with stable gradients.

    For magnitudes in (0, 1) with exponent > 1:
        compressed < original (real decay)
        but the decay is sub-linear (concave curve)

    Gradient: d/d|h| (|h|^e) = e · |h|^(e-1) = e · compressed/|h|
    We use the ratio form for numerical stability.
    """
    @staticmethod
    def forward(ctx, mag, exponent):
        mag_safe = torch.clamp(mag, min=1e-8)
        compressed = mag_safe ** exponent
        # Store ratio for gradient: e * |h|^(e-1) = e * compressed / mag_safe
        ratio = exponent * compressed / (mag_safe + 1e-10)
        ctx.save_for_backward(ratio)
        return compressed

    @staticmethod
    def backward(ctx, grad_output):
        ratio, = ctx.saved_tensors
        return grad_output * torch.clamp(ratio, max=5.0), None


def fractal_compress(z: torch.Tensor, exponent: torch.Tensor) -> torch.Tensor:
    """
    ⊛: Fractal compression of complex state.

    Magnitude compressed by exponent (element-wise, per state dim).
    Phase preserved exactly. This IS the forgetting mechanism.

    z: (..., 2) complex tensor
    exponent: (...) real tensor, same shape as z minus last dim
    Returns: (..., 2) complex tensor with compressed magnitude, same phase

    Uses exp(e * log(|h|)) for differentiability through exponent.
    Gradients flow through both magnitude AND exponent, so the
    resonance gate and A_log can learn.
    """
    mag = c_mag(z)                          # (...)
    phase = c_phase(z)                      # (...)
    # |h|^e = exp(e * log(|h|)), differentiable w.r.t. both h and e
    log_mag = torch.log(mag + 1e-8)
    compressed_mag = torch.exp(exponent * log_mag)
    # Clamp for safety (shouldn't be needed with tanh squash, but just in case)
    compressed_mag = torch.clamp(compressed_mag, max=10.0)
    return c_from_polar(compressed_mag, phase)


def mag_squash(z: torch.Tensor) -> torch.Tensor:
    """
    Bound magnitude into (0, 1) using tanh, preserving phase.

    This is the boundary condition (○): the state cannot grow unbounded.
    tanh is a natural squasher: maps [0, inf) -> [0, 1).
    Phase (identity) passes through untouched.
    """
    mag = c_mag(z)
    phase = c_phase(z)
    squashed = torch.tanh(mag)
    return c_from_polar(squashed, phase)


# =====================================================================
#  φ-SCALED A INITIALIZATION
# =====================================================================

def phi_scaled_A_init(state_size: int) -> torch.Tensor:
    """
    Initialize A with φ-proportioned groups.

    group_1 (N/φ dims):  slow decay (low A values, long horizon)
    group_2 (N/φ² dims): fast decay (high A values, reactive)

    The golden ratio sets the proportion between timescales;
    no extra parameters, just geometry.
    """
    n_slow = round(state_size / PHI)
    n_fast = state_size - n_slow

    slow = torch.linspace(0.5, 2.0, n_slow)
    fast = torch.linspace(2.0, float(state_size), n_fast)

    A_init = torch.cat([slow, fast])
    return torch.log(A_init)


# =====================================================================
#  DNA INITIALIZATION
# =====================================================================

def dna_init(d_model: int, state_size: int, batch_size: int,
             device: torch.device, magnitude: float = 0.01) -> torch.Tensor:
    """
    Initialize state h with differentiated phase structure.

    A1: the 1 must self-limit into distinct states.
    64 distinct phases (from the 64-state architecture) break symmetry
    so that each state dimension starts with a unique identity.

    Returns: (batch, d_model, state_size, 2) complex
    """
    phases = torch.linspace(0, 2 * math.pi * (1 - 1 / state_size),
                            state_size, device=device)
    # Per-dimension, per-state: each (d_model, state_size) pair gets a phase
    h = c_from_polar(
        torch.full((state_size,), magnitude, device=device),
        phases
    )
    # Expand to (batch, d_model, state_size, 2)
    return h.unsqueeze(0).unsqueeze(0).expand(batch_size, d_model, -1, -1).clone()


# =====================================================================
#  FRACTAL SSM (the v3 core)
# =====================================================================

class FractalSSM(nn.Module):
    """
    Selective SSM where fractal compression IS the state transition,
    modulated by resonance between input and state.

    Standard:    h_t = α_t · h_{t-1} + γ_t · B_t · x_t
    Fractal:     h_t = squash(⊛(h_{t-1}, e_t) + γ_t · B_t · x_t)

    Where:
        T_t = cos²(Δφ/2)                          (resonance gate)
        e_t = 1 + (1 - α_t) · κ · (1 - T_t)      (resonance-modulated exponent)
        ⊛(h, e) = |h|^e · e^(iφ)                  (magnitude compressed, phase preserved)
        squash = tanh on magnitude                  (boundary condition, ○)

    α_t controls selective retention (same as Mamba).
    T_t measures phase match between input and each state dimension.
    Both must agree to compress: high α OR high T protects state.

    Each state dimension is a "head" with a carrier phase (DNA init).
    The resonance projection gives input a phase to match against.
    Relevant patterns survive; irrelevant ones compress faster.
    """

    def __init__(self, d_model: int, state_size: int = 16, dt_rank: int = None,
                 kappa: float = KAPPA):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)
        self.kappa = kappa

        # A: φ-scaled initialization
        self.A_log = nn.Parameter(phi_scaled_A_init(state_size))

        # Projections (same as standard Mamba)
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)

        # Resonance projection: real input -> complex for phase matching
        # Each state dimension is a "head" with a carrier phase (from DNA init).
        # This projection gives the input a phase signature to match against.
        self.W_resonance = nn.Linear(d_model, state_size * 2, bias=False)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if 'A_log' in name:
                continue
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, d_model)
        Returns: (batch, seq_len, d_model)
        """
        batch, seq_len, _ = x.shape
        device = x.device

        # SiLU gating (same as Mamba)
        xz = self.in_proj(x)
        x_in, z = xz.chunk(2, dim=-1)
        x_in = F.silu(x_in)

        # Project to SSM params
        xp = self.x_proj(x_in)
        dt_raw = xp[..., :self.dt_rank]
        bc_raw = xp[..., self.dt_rank:]

        dt = F.softplus(self.dt_proj(dt_raw))  # (batch, seq_len, d_model)

        bc = bc_raw.view(batch, seq_len, 2, self.state_size, 2)
        B = bc[:, :, 0]   # (batch, seq_len, state_size, 2)
        C = bc[:, :, 1]   # (batch, seq_len, state_size, 2)

        # Initialize state with DNA phases
        h = dna_init(self.d_model, self.state_size, batch, device)
        # h: (batch, d_model, state_size, 2)

        A = self.A_log  # (state_size,)

        outputs = []
        for t in range(seq_len):
            x_t = x_in[:, t]        # (batch, d_model)
            dt_t = dt[:, t]          # (batch, d_model)
            B_t = B[:, t]            # (batch, state_size, 2)
            C_t = C[:, t]            # (batch, state_size, 2)

            # ════════════════════════════════════════
            #  RESONANCE: input phase vs state phase
            # ════════════════════════════════════════

            # Project input to complex for phase matching
            x_res = self.W_resonance(x_t)                      # (batch, state_size * 2)
            x_complex_res = x_res.view(batch, self.state_size, 2)
            # (batch, state_size, 2)

            # State h is (batch, d_model, state_size, 2)
            # Average over d_model to get the "carrier phase" per state dim
            h_carrier = h.mean(dim=1)                           # (batch, state_size, 2)

            # T = cos²(Δφ/2): resonance between input and each state dim
            T_t = resonance_gate(x_complex_res, h_carrier)     # (batch, state_size)

            # ════════════════════════════════════════
            #  COMPUTE SELECTIVE EXPONENT
            # ════════════════════════════════════════

            # Standard α_t computation (same math as Mamba)
            A_neg = -torch.exp(A)                              # (state_size,)
            dt_A = dt_t.unsqueeze(-1) * A_neg.unsqueeze(0)     # (batch, d_model, state_size)
            alpha_t = torch.exp(dt_A)                          # in (0, 1]

            # Resonance-modulated exponent:
            #   e_t = 1 + (1 - α_t) · κ · (1 - T_t)
            #
            # Both α (gate) and T (resonance) must agree to compress.
            # High α OR high T protects the state from compression.
            # Only when α is low AND T is low does full compression apply.
            #
            # T_t is (batch, state_size); broadcast to (batch, d_model, state_size)
            T_broadcast = T_t.unsqueeze(1).expand_as(alpha_t)
            exponent_t = 1.0 + (1.0 - alpha_t) * self.kappa * (1.0 - T_broadcast)

            # ════════════════════════════════════════
            #  ⊛ FRACTAL STATE TRANSITION
            # ════════════════════════════════════════

            # Instead of h = α_t · h, we do h = |h|^e_t · e^(iφ_h)
            h = fractal_compress(h, exponent_t)

            # ════════════════════════════════════════
            #  INPUT: γ_t · B_t · x_t
            # ════════════════════════════════════════

            gamma_t = dt_t  # (batch, d_model)

            # x_t as complex (real part only, imaginary = 0)
            x_complex = torch.stack([x_t, torch.zeros_like(x_t)], dim=-1)
            # (batch, d_model, 2)

            # B_t · x_t: (batch, d_model, state_size, 2)
            Bx = c_mul(
                B_t.unsqueeze(1).expand(-1, self.d_model, -1, -1),
                x_complex.unsqueeze(2).expand(-1, -1, self.state_size, -1)
            )
            Bx = c_scale(Bx, gamma_t.unsqueeze(-1))

            # ════════════════════════════════════════
            #  STATE UPDATE + BOUNDARY (○)
            # ════════════════════════════════════════

            h = h + Bx

            # Squash magnitude into (0, 1) via tanh; phase preserved
            # This is the boundary condition: prevents unbounded growth
            h = mag_squash(h)

            # ════════════════════════════════════════
            #  OUTPUT: y_t = Re(C_t^H · h_t)
            # ════════════════════════════════════════

            Ch = c_mul(
                c_conj(C_t).unsqueeze(1).expand(-1, self.d_model, -1, -1),
                h
            )
            y_t = Ch[..., 0].sum(dim=-1)  # real part, sum over state
            outputs.append(y_t)

        y = torch.stack(outputs, dim=1)   # (batch, seq_len, d_model)
        y = y * F.silu(z)
        return self.out_proj(y)


# =====================================================================
#  STANDARD SSM BASELINE (matched architecture, linear decay)
# =====================================================================

class SelectiveSSM(nn.Module):
    """Standard selective SSM (Mamba-2 style) baseline for fair comparison."""

    def __init__(self, d_model: int, state_size: int = 16, dt_rank: int = None):
        super().__init__()
        self.d_model = d_model
        self.state_size = state_size
        self.dt_rank = dt_rank or max(d_model // 16, 1)

        self.A_log = nn.Parameter(torch.log(torch.linspace(1, state_size, state_size)))
        self.x_proj = nn.Linear(d_model, self.dt_rank + 2 * state_size * 2, bias=False)
        self.dt_proj = nn.Linear(self.dt_rank, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.in_proj = nn.Linear(d_model, d_model * 2, bias=False)

        self._init_weights()

    def _init_weights(self):
        scale = 1.0 / PHI
        for name, p in self.named_parameters():
            if p.dim() >= 2:
                nn.init.uniform_(p, -scale / math.sqrt(p.shape[1]),
                                 scale / math.sqrt(p.shape[1]))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, seq_len, _ = x.shape
        device = x.device

        xz = self.in_proj(x)
        x_in, z = xz.chunk(2, dim=-1)
        x_in = F.silu(x_in)

        xp = self.x_proj(x_in)
        dt_raw = xp[..., :self.dt_rank]
        bc_raw = xp[..., self.dt_rank:]

        dt = F.softplus(self.dt_proj(dt_raw))
        bc = bc_raw.view(batch, seq_len, 2, self.state_size, 2)
        B = bc[:, :, 0]
        C = bc[:, :, 1]

        h = torch.zeros(batch, self.d_model, self.state_size, 2, device=device)
        A = self.A_log

        outputs = []
        for t in range(seq_len):
            A_neg = -torch.exp(A)
            dt_A = dt[:, t].unsqueeze(-1) * A_neg.unsqueeze(0)
            alpha_t = torch.exp(dt_A)
            gamma_t = dt[:, t]

            x_complex = torch.stack([x_in[:, t], torch.zeros_like(x_in[:, t])], dim=-1)
            Bx = c_mul(
                B[:, t].unsqueeze(1).expand(-1, self.d_model, -1, -1),
                x_complex.unsqueeze(2).expand(-1, -1, self.state_size, -1)
            )
            Bx = c_scale(Bx, gamma_t.unsqueeze(-1))

            h = c_scale(h, alpha_t) + Bx

            Ch = c_mul(
                c_conj(C[:, t]).unsqueeze(1).expand(-1, self.d_model, -1, -1),
                h
            )
            y_t = Ch[..., 0].sum(dim=-1)
            outputs.append(y_t)

        y = torch.stack(outputs, dim=1)
        y = y * F.silu(z)
        return self.out_proj(y)


# =====================================================================
#  SEQUENCE MODELS
# =====================================================================

class MambaModel(nn.Module):
    """Standard Mamba baseline."""
    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            SelectiveSSM(d_model, state_size) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        h = self.embedding(x)
        for layer in self.layers:
            h = h + layer(h)
        return self.head(self.norm(h))


class FractalMambaModel(nn.Module):
    """Circumpunct Mamba v3: fractal state transition."""
    def __init__(self, vocab_size: int, d_model: int = 64, state_size: int = 16,
                 n_layers: int = 2, kappa: float = KAPPA):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList([
            FractalSSM(d_model, state_size, kappa=kappa) for _ in range(n_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        h = self.embedding(x)
        for layer in self.layers:
            h = h + layer(h)
        return self.head(self.norm(h))


# =====================================================================
#  BENCHMARKS
# =====================================================================

class CopyingProblem:
    """Remember 8 digits across T blank timesteps."""
    def __init__(self, T=100, n_digits=8, vocab_size=10, batch_size=32):
        self.T, self.n_digits, self.vocab_size = T, n_digits, vocab_size
        self.batch_size = batch_size
        self.seq_len = 1 + n_digits + T + 1 + n_digits
        self.BLANK, self.MARKER, self.TRIGGER = vocab_size, vocab_size+1, vocab_size+2
        self.total_tokens = vocab_size + 3
        self.trigger_pos = 1 + n_digits + T
        self.output_len = n_digits

    def generate_batch(self, device=None):
        b = self.batch_size
        seq = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        tgt = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        seq[:, 0] = self.MARKER
        digits = torch.randint(0, self.vocab_size, (b, self.n_digits), device=device)
        seq[:, 1:1+self.n_digits] = digits
        seq[:, self.trigger_pos] = self.TRIGGER
        tgt[:, self.trigger_pos+1:self.trigger_pos+1+self.n_digits] = digits
        return seq, tgt


class SelectiveCopyingProblem:
    """
    Selective copying: remember only the marked tokens across T blanks.

    Input:  [MARKER digit BLANK digit MARKER digit ...] [T blanks] [trigger]
    Target: [blanks...] [the digits preceded by MARKER, in order]

    Two-token encoding: (flag, digit) pairs. Digit is always visible.
    Model must learn to attend to the flag, not just the digit.
    """
    def __init__(self, T=100, n_total=16, n_marked=8, vocab_size=10, batch_size=32):
        self.T, self.n_total, self.n_marked = T, n_total, n_marked
        self.vocab_size, self.batch_size = vocab_size, batch_size
        self.seq_len = n_total * 2 + T + 1 + n_marked
        self.BLANK, self.MARKER, self.TRIGGER = vocab_size, vocab_size+1, vocab_size+2
        self.total_tokens = vocab_size + 3
        self.trigger_pos = n_total * 2 + T
        self.output_len = n_marked

    def generate_batch(self, device=None):
        b = self.batch_size
        seq = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        tgt = torch.full((b, self.seq_len), self.BLANK, dtype=torch.long, device=device)
        for i in range(b):
            tokens = torch.randint(0, self.vocab_size, (self.n_total,), device=device)
            marked = torch.randperm(self.n_total, device=device)[:self.n_marked].sort().values
            marked_set = set(marked.tolist())
            for j in range(self.n_total):
                flag = self.MARKER if j in marked_set else self.BLANK
                seq[i, j * 2] = flag
                seq[i, j * 2 + 1] = tokens[j]
            tgt[i, self.trigger_pos+1:self.trigger_pos+1+self.n_marked] = tokens[marked]
        seq[:, self.trigger_pos] = self.TRIGGER
        return seq, tgt


# =====================================================================
#  TRAINING
# =====================================================================

def train_benchmark(model_type='fractal', problem_type='copying',
                    T=100, n_epochs=300, lr=0.001, batch_size=32,
                    d_model=64, state_size=16, n_layers=2, verbose=True):
    """Train on a benchmark. model_type: 'fractal' or 'standard'."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    problem = CopyingProblem(T=T, batch_size=batch_size) if problem_type == 'copying' \
        else SelectiveCopyingProblem(T=T, batch_size=batch_size)

    model = (FractalMambaModel if model_type == 'fractal' else MambaModel)(
        vocab_size=problem.total_tokens, d_model=d_model,
        state_size=state_size, n_layers=n_layers
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    n_params = sum(p.numel() for p in model.parameters())

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"  ⊙ {problem_type.title()} Benchmark  |  {model_type}")
        print(f"  Params: {n_params:,}  |  T={T}  |  seq={problem.seq_len}")
        print(f"  d={d_model}  N={state_size}  layers={n_layers}  |  {device}")
        print(f"{'=' * 60}\n")

    tp = problem.trigger_pos
    ol = problem.output_len
    best_acc = 0.0
    history = []
    nan_skips = 0

    for epoch in range(n_epochs):
        model.train()
        seq, target = problem.generate_batch(device)
        logits = model(seq)

        out_logits = logits[:, tp+1:tp+1+ol]
        out_target = target[:, tp+1:tp+1+ol]
        loss = F.cross_entropy(out_logits.reshape(-1, problem.total_tokens),
                               out_target.reshape(-1))

        if torch.isnan(loss).item() or torch.isinf(loss).item():
            optimizer.zero_grad()
            nan_skips += 1
            continue

        optimizer.zero_grad()
        loss.backward()

        if any(p.grad is not None and (torch.isnan(p.grad).any() or torch.isinf(p.grad).any())
               for p in model.parameters()):
            nan_skips += 1
            optimizer.zero_grad()
            continue

        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        model.eval()
        with torch.no_grad():
            e_seq, e_tgt = problem.generate_batch(device)
            e_log = model(e_seq)
            preds = e_log[:, tp+1:tp+1+ol].argmax(dim=-1)
            acc = (preds == e_tgt[:, tp+1:tp+1+ol]).float().mean().item()
            best_acc = max(best_acc, acc)

        history.append({'epoch': epoch, 'loss': loss.item(), 'acc': acc})

        if verbose and (epoch % 25 == 0 or epoch == n_epochs - 1):
            skip = f"  skip={nan_skips}" if nan_skips else ""
            print(f"  E{epoch:4d}  loss={loss.item():.4f}  acc={acc:.3f}"
                  f"  best={best_acc:.3f}{skip}")

    return history, best_acc


# =====================================================================
#  MAIN
# =====================================================================

if __name__ == '__main__':
    import sys

    T = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    n_epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    problem = sys.argv[3] if len(sys.argv) > 3 else 'copying'

    print("\n⊙ THE CIRCUMPUNCT MAMBA v3")
    print("  Fractal state transition. No worldline. No side buffer.")
    print("  Forgetting IS compression.\n")

    print("\n" + "-" * 60)
    print("  STANDARD MAMBA (baseline)")
    print("-" * 60)
    std_h, std_best = train_benchmark('standard', problem, T=T, n_epochs=n_epochs)

    print("\n" + "-" * 60)
    print("  FRACTAL MAMBA v3")
    print("-" * 60)
    frac_h, frac_best = train_benchmark('fractal', problem, T=T, n_epochs=n_epochs)

    # Parameter comparison
    std_p = sum(p.numel() for p in MambaModel(13, 64, 16, 2).parameters())
    frac_p = sum(p.numel() for p in FractalMambaModel(13, 64, 16, 2).parameters())

    print(f"\n{'=' * 60}")
    print(f"  RESULTS (T={T}, {problem})")
    print(f"  Standard Mamba:    {std_best:.3f}  ({std_p:,} params)")
    print(f"  Fractal v3:        {frac_best:.3f}  ({frac_p:,} params)")
    print(f"  Param ratio:       {frac_p/std_p:.2f}x")
    diff = frac_best - std_best
    arrow = "+" if diff > 0 else ""
    print(f"  Delta:             {arrow}{diff:.3f}")
    print(f"{'=' * 60}")
